# Priority 7 — Phase 3A Implementation Plan

**Phase:** 3A design only. Nothing below is implemented, authorized or scheduled. Every slice
requires its own explicit authorization, its own fresh safety baseline, and its own review.

Two parts:
**Part A** — the exact file/function touch map, derived from the repository at tree
`f6e9b3ae49bd7e0f35bc2ba6f7bfd092ed017fc3`.
**Part B** — the recommended slice sequence after Phase 3A.

---

# PART A — Touch map

Every row names a real file, a real function or a real selector. Nothing invented. "Required" means
the recommended architecture cannot exist without it; "optional" means it improves the result but
the slice ships without it.

## A1 — New files

| File | What it is | Required? | Regression risk | Tests |
|---|---|---|---|---|
| `pp-verb-patterns.js` | Fifth pure helper: envelope validation, the A–Z index and case-filter derivation, case metadata, question derivation, chip/role/headline derivation, the eligible-`contentRef` reverse index, `eligibleFor` allowlist, and the **test-only injection entry point** (`__acceptForTest`) described in the runtime contract §4.5a | **required** | **Low in isolation** — pure, no DOM, no storage. The risk is entirely in its call sites. | new `tests/test_priority7_patterns_ui.js` (JXA), driving it exactly as `tests/test_activities.js` drives `PP_USAGE`; plus a source-level assertion that the injection entry point is never referenced from `index.html` |
| `tests/fixtures/priority7/runtime-fixture.json` | Wrapped non-release synthetic fixture | **required** (3B) | **Low** — path is already asserted absent from every public surface; the assertion inverts to "present and only this" | new `tests/test_priority7_phase3b.py` |
| `tests/test_priority7_phase3b.py` | Fixture provenance, wrapper, `validate_runtime`, anti-leak, absence of `content/verb-patterns.json` | **required** (3B) | none | itself |
| `tests/test_priority7_patterns_ui.js` | Loader + rendering behaviour, fail-closed cases, question derivation, reverse index, progress non-writing | **required** (3B) | none | itself |
| `content/verb-patterns.json` | The public runtime projection | **prohibited until a release gate** | — | — |

## A2 — `index.html` — script loading

| Location | Change | Required? | Risk | Existing tests | New tests |
|---|---|---|---|---|---|
| [`index.html:1830`](../index.html#L1830)–[`1840`](../index.html#L1840) (`<script src>` block) | add `<script src="pp-verb-patterns.js"></script>` after `pp-migrate.js` | **required** | **Medium.** `test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths` asserts the list is **exactly** eleven entries in order; this fails until deliberately amended | `tests/test_priority7_phase2a.py::DeploymentIsolationTests` | the same test, narrowed to twelve named entries |

## A3 — `index.html` — bootstrap and level synthesis

| Function / line | Change | Required? | Risk | Existing tests | New tests |
|---|---|---|---|---|---|
| `LEVELS.push(…)` at [`index.html:1919`](../index.html#L1919) | push a `{ level:"Verb patterns", group:"grammar", blurb, topics: patternIndexTopics() }` level **only when** `PP_VERB_PATTERNS.available` | **required** | **Medium.** `LEVELS` length changes 12 → 13. Anything asserting a level count or index is affected. `S.levelIdx` is an index into this array, so ordering matters for the Grammar pill order | `tests/test_activities.js` (walks `LEVELS` via `PP_USAGE.typedPracticeCards`), `tests/test_typeit_eligibility.js` | assert the new level is absent when the loader is unavailable; assert pool totals for Type It (1,089) and Listening (1,113) are unchanged |
| new `patternIndexTopics()` beside `practiceTopics()` at [`index.html:1910`](../index.html#L1910) | build **one** topic — the verb index — carrying `kind:"patterns"`, `name`, `desc`, `chip`, `emoji`, an opaque surface key and a curated `searchText`, and **no `vp-*` identifier**. **Not** seven case topics: case is in-screen filter state, not a topic (UX architecture §1.0, §3.1) | **required** | **Medium.** `topicHaystack` recurses over every string and does not skip `id` — anything id-shaped on this object becomes searchable, and with one topic instead of eight this single string carries all the discipline | none directly | assert `topicHaystack(indexTopic)` contains no `vp-` substring; assert exactly one topic is produced |
| `VOCAB_SRC` at [`index.html:1877`](../index.html#L1877) | **no change** | — | must stay unchanged: it is `every(t => !t.kind)`, so the new topics (which carry a `kind`) are excluded automatically | `tests/test_typeit_eligibility.js` | assert `VOCAB_SRC.length === 3` after the push |
| `poolFor()` at [`index.html:1900`](../index.html#L1900) | **no change** | — | it walks `VOCAB_SRC` only, so pattern topics can never enter a Type It or Listening pool | `tests/test_activities.js` | — |
| `PP_TYPED_INDEX` at [`index.html:4144`](../index.html#L4144) region / `PP_USAGE.typedPracticeCards` at [`pp-usage.js:198`](../pp-usage.js#L198) | **no change** | — | it skips any topic with a `kind`, so pattern topics contribute no typed answers and cannot create collisions | `tests/test_answer_collisions.js` | assert index size is unchanged |

## A4 — `index.html` — navigation and home rendering

| Function / line | Change | Required? | Risk | Existing tests | New tests |
|---|---|---|---|---|---|
| `categoryOf()` [`index.html:2397`](../index.html#L2397) | **no change** | — | `group:"grammar"` routes automatically; this is the documented extension contract | `tests/test_phase2c_navigation.js` | assert the new level's category is `"grammar"` |
| `CATEGORIES` [`index.html:2402`](../index.html#L2402) | **no change** | — | a fourth tab is explicitly rejected | `tests/test_phase3_closeout.js` (`C1` tab contracts) | — |
| `renderLevels()` [`index.html:2413`](../index.html#L2413) | **no change** | — | grammar pills go 5 → 6; the existing `n<=3 / ===4 / else` rule keeps `repeat(3,1fr)` | none | assert the grid template is unchanged at 6 |
| `tCount()` [`index.html:2593`](../index.html#L2593) | add a `t.kind==="patterns"` branch returning e.g. `"30 verbs · 45 patterns"` | **required** | **Low, but a real bug if omitted** — an unknown `kind` currently falls through to `t.cards.length` and would render `undefined cards` | none | assert the count string, and that it reports verbs *and* patterns (they differ) |
| `topicIcon()` [`index.html:2591`](../index.html#L2591) / `ICONS` [`index.html:2592`](../index.html#L2592) region | reuse an existing icon key (e.g. `🔗` or `🎯`, both already in `ICONS`) rather than adding one | optional | **Low.** An unmapped emoji falls back to the literal glyph, which renders inconsistently with every other tile | none | assert the set topics resolve to an SVG, not a glyph |
| `renderTopics()` [`index.html:2605`](../index.html#L2605) | **no change** | — | `showPill` is `(!t.kind || t.kind==="podcast")`, so no Quiz pill appears on a pattern set — correct by default | none | assert no `.pill-practice` on a pattern set row |
| `routeTopic()` [`index.html:3389`](../index.html#L3389) | add the explicit `patterns` branch **and** convert the trailing `else` into an explicit vocab/podcast test with a fail-closed default | **REQUIRED — both halves.** See §A4a | **Medium→High.** Phase 3B introduces the first new `kind` since `typeit`/`listen`, which makes the latent default-fallthrough defect reachable | `tests/test_audio_fallback.js` (extracts `routeTopic`), `tests/test_phase3b_overlays.js` (extracts `openTopic`) | see §A4a |
| `topicHaystack()` / `HAY_SKIP` [`index.html:2489`](../index.html#L2489) | **no change preferred** | — | relies on the discipline in A3: no identifier on the topic object. Extending `HAY_SKIP` is the fallback if that discipline cannot be held | none | the `vp-` assertion above |

## A4a — Topic routing: default-deny is a REQUIRED Phase 3B safety task

**Status: required, not optional, and a Phase 3B acceptance-gate item.**

Phase 3A's audit found that `routeTopic()` has no default-deny branch and that an unknown `kind`
falls through to `startTopic()`, which immediately calls `S.cards.map(...)` on an undefined `cards`
array (audit §2.3). The defect is latent today because every existing topic carries a known `kind`.
**Phase 3B introduces the first new `kind` since `typeit`/`listen`**, so it is the phase that makes
the defect reachable, and it is therefore the phase that must close it. Shipping a new routing kind
on top of an open fallthrough is not acceptable even if the new kind itself is handled correctly:
the next kind, or a typo in this one, lands in the flashcard renderer.

### A4a.1 Required behaviour

**(a) Explicit handling for the new pattern kind.** One named branch, matching the existing idiom
exactly:

```js
if(t.kind === "grammar")       startGrammar(li, ti);
else if(t.kind === "convo")    startConvo(li, ti);
else if(t.kind === "typeit")   startTypeit(li, ti);
else if(t.kind === "listen")   startListen(li, ti);
else if(t.kind === "patterns") startPatterns(li, ti);
else if(!t.kind || t.kind === "podcast") startTopic(li, ti);   /* vocab + podcast, now EXPLICIT */
else return false;                                             /* default deny */
```

The change to the existing final branch is the substance: `startTopic` stops being the fallthrough
and becomes a named destination for the two kinds it can actually render. Every branch is a positive
match.

**(b) Safe / default-deny handling for unknown kinds.** An unrecognised `kind`:

- performs **no navigation** — `show()` is not called, no history entry is pushed;
- **mutates no state** — in particular `S.levelIdx` / `S.topicIdx` must not be reassigned, which
  means the deny check happens in `routeTopic` *before* any `start*` function is entered;
- renders **no error UI, no toast, no alert** — consistent with the app's existing quiet-failure
  posture for non-critical paths (`ppCheckFresh`, the migration `catch`);
- emits at most **one `console.info`**, matching [`index.html:2005`](../index.html#L2005)'s style;
- returns a falsy value so `openTopic()` and the mature-gate continuation can both observe that
  nothing happened.

`routeTopic` should return a boolean for this reason. Both current call sites — `openTopic()` and
the `#matureContinue` handler ([`index.html:3411`](../index.html#L3411)) — must propagate it rather
than ignoring it.

**(c) Expected focus behaviour.** This is the part most likely to be got wrong. On a denied route:

- **focus does not move.** It stays on the invoking `.topic-main` button, which is still present,
  still visible and still interactive, so the learner (and any screen-reader user) is left exactly
  where they were rather than on `<body>`;
- **no `ppFocusActivityTarget` / `ppFocusElement` call is made at all** — a deny is not a transition,
  and the app's focus contract is that focus moves only on a real screen change;
- `ppRememberScreenInvoker` / `ppUseInvokerForNextScreen` must **not** be primed, since there is no
  next screen to return from;
- **via the mature gate:** `#matureContinue` closes the dialog and then routes. If the route denies,
  the existing `ppCloseSharedOverlay(gate, false)` has already suppressed the dialog's own focus
  restoration in anticipation of an activity taking focus — so a deny must **restore focus to the
  remembered invoker itself**, using the invoker already captured by
  `ppTakeSharedOverlayInvoker()`. Otherwise the one path that can strand focus on `<body>` is
  precisely the adult-language gate. This is the single most important detail in A4a.

**(d) Regression tests.** In `tests/test_priority7_patterns_ui.js` (or beside the existing
`routeTopic` coverage in `tests/test_audio_fallback.js`, which already extracts the function):

1. `kind:"patterns"` reaches `startPatterns` and nothing else;
2. each of `undefined`, `"podcast"`, `"grammar"`, `"convo"`, `"typeit"`, `"listen"` still reaches its
   existing destination — an unchanged-behaviour proof for all five shipping kinds;
3. an unknown `kind` (`"pattern"`, `"Patterns"`, `"typeIt"`, `""`, `null`, `0`, `{}`) reaches **no**
   `start*` function;
4. a denied route calls no navigation function and pushes no history entry;
5. a denied route leaves `S.levelIdx` / `S.topicIdx` unchanged;
6. a denied route leaves `document.activeElement` on the invoking button;
7. a denied route **through the mature gate** leaves focus on the remembered invoker, never on
   `<body>`;
8. a topic with `kind:"patterns"` but a missing/invalid surface payload is denied rather than
   rendered — the deny is on the *routing* decision, and the renderer additionally refuses bad input;
9. `routeTopic` returns falsy on deny and truthy on every successful route.

**(e) Stop condition.** *If any unknown or malformed `kind` can still reach an incompatible renderer
— `startTopic`, `startGrammar`, `startConvo`, `startTypeit`, `startListen` or `startPatterns` — Phase
3B does not ship.* This is a hard stop, not a defect to log. The same stop applies if a denied route
is observed to move focus, mutate `S`, push history, or leave the mature gate closed with focus on
`<body>`.

### A4a.2 Why this is in 3B and not deferred

It is small, it is entirely independent of linguistic approval, and it is a **precondition** for the
new kind rather than a cleanup after it. Deferring it would mean shipping a routing table whose
correctness depends on no one ever making a typo — and the first new `kind` in the codebase's
history is exactly the moment that assumption stops being safe.

## A5 — `index.html` — the new screen

| Item | Change | Required? | Risk | Existing tests | New tests |
|---|---|---|---|---|---|
| new `<section class="screen" id="patterns">` in the body, after `#round` and before `#privacy` | `.sbar` with `#pBack`, `<h1 id="pTitle">`, `.back.home-btn`; a scrollable content region `#pBody`. **No** speed toggle (nothing plays), **no** progress bar (nothing is scored) | **required** | **Medium.** A tenth screen id enters `show()`/`showScreen()`, `ppRouteScreenFocus`, the scroll contract and the `popstate` handler | `tests/test_phase1b_keyboard_focus.js` and `tests/test_phase3b_focus_scroll.js` both extract `show`/`showScreen` | assert screen entry focuses `#pTitle`, back restores the invoking `.topic-main`, and the remembered scroll offset is reapplied |
| new `startPatterns(li, ti)` | set state, render the **verb index**, `show("patterns", true)`, then focus via the renderer — the same two-step every activity uses (`startTypeit`, `startListen`, `startRound` all pass `deferFocus=true`). Accepts an optional case-filter argument so a case lesson can deep-link into the filtered state (slice 3C) | **required** | Low if the existing idiom is followed exactly | `tests/test_phase1b_keyboard_focus.js` (extracts `startTypeit`/`startListen`/`startRound`) | assert the same focus contract; assert the filter argument sets state without adding a history entry |
| new `pRenderIndex()` / `pRenderLemma()` | `pRenderIndex` renders the A–Z list plus the filter chip row and applies the case filter **in place**; `pRenderLemma` renders one lemma entry. Build DOM with `createElement` + `textContent` **only** | **required** | **High if violated.** `gRenderTeach`/`gRenderChoose`/`gChooseFeedback` are `innerHTML`-based and must not be reused for generated strings | — | assert no `innerHTML` assignment in the new functions (a source-level assertion, matching the style of existing JXA suites) |
| **one-lemma-one-entry invariant** | `pRenderLemma` is the only function that renders a pattern's explanation, example or links; `pRenderIndex` renders row summaries only | **required** | **Medium.** This invariant is what makes case a view rather than an owner; violating it silently reintroduces duplication | — | for every lemma id in the fixture, assert exactly one rendered entry across every filter state; assert a filtered row contains no explanation/example/link node |
| filter chip row | eight `<button aria-pressed>` controls reusing the `.seg-btn`/`.cat-btn` idiom; `flex-wrap`, never horizontal scroll | **required** | Medium at 320px (three wrapped lines) | `tests/test_phase3_closeout.js` (`A5` no `overflow-x`) | assert wrap not scroll; assert 44px targets; assert `aria-pressed` reflects the active filter |
| `show()` [`index.html:2357`](../index.html#L2357) / `showScreen()` [`index.html:2342`](../index.html#L2342) | **no change** | — | the screen id is data to them | both focus suites | — |
| hash deep-link allowlist [`index.html:2376`](../index.html#L2376) | **no change** | — | `#patterns` stays non-deep-linkable, like every other activity screen | `tests/test_phase2c_navigation.js` | — |

## A6 — `index.html` — the card back pointer (slice 3C)

| Item | Change | Required? | Risk | Existing tests | New tests |
|---|---|---|---|---|---|
| body markup after `#variantLine` ([`index.html:1185`](../index.html#L1185) region) | add `<div class="pair-line" id="patternLine" hidden>` with a key span and a button | optional (tier 3) | **Medium.** The back face is already dense; this is the item that risks the 320px vertical budget | `tests/test_phase1a_accessibility.js` (extracts `render`) | assert hidden by default and shown only for a single-claim card |
| `render()` [`index.html:2801`](../index.html#L2801) | populate/hide `#patternLine` via the **two-gate** rule (UX architecture §8.3); reuse `ppSetSharedCardText` for the Polish half | optional | **Medium.** `render()` is the most-driven function in the suite | `tests/test_phase1a_accessibility.js`, `tests/test_phase3_closeout.js` (`B4` card contracts) | see the eligibility tests below |
| reverse index in `pp-verb-patterns.js` | index **only** refs where `kind === "card" && purpose === "support"`; then apply Gate 2 (owning lemma has exactly one meaning and one pattern) | optional (tier 3) | **Medium.** Indexing every `contentRef` would attach patterns to `contrast` cards, which assert the opposite | — | assert `contrast`, `practice`, `context` card refs are never indexed; assert `topic`/`drill`/`scenario` refs never reach the card feature; assert the four outcomes (nothing / chip / doorway-by-count / doorway-by-meaning); assert `bać się`'s card yields a doorway and `szukać`'s a chip |
| `.pair-line` CSS [`index.html:449`](../index.html#L449) | reuse; add no new selector if possible | optional | Low | `tests/test_phase3b_mobile_layout.js`, `tests/test_phase3_closeout.js` | — |
| `data-a1.js` / `data-a2.js` / `data-b1.js` | **no change** | — | `CARD_FIELDS` is closed; the link is derived, never authored | `tests/test_priority5_content.py`, `validate_content.py` | assert card totals unchanged (1,215) |
| `validate_content.py` | **no change** | — | any change here reopens the content schema and its frozen baselines | `tests/test_priority5_content.py` | — |

## A7 — CSS

| Item | Change | Required? | Risk | Existing tests |
|---|---|---|---|---|
| new `.vp-*` block in the second `<style>` ([`index.html:74`](../index.html#L74)) | chip, chip list, role line, headline, meaning/lemma section, links | **required** | **High.** Four pinned constraints (below) | `tests/test_phase3b_mobile_layout.js`, `tests/test_phase3_closeout.js` |
| new media-query width | **prohibited** | — | `A1 no extra widths were scattered across the sheet` asserts exactly `[360,400,400]` | same |
| adding a selector to the 360px block | **prohibited** | — | `A4` asserts that block's selectors are exactly `['.pill-practice','.t-arrow','.topic','.topic-main']` | same |
| `overflow-x:hidden|clip` | **prohibited anywhere** | — | `A5 no rule anywhere sets overflow-x to hidden or clip` | `tests/test_phase3_closeout.js` |
| `overflow-wrap:anywhere` / `word-break` on new selectors | **prohibited** | — | `B5 only the audited selectors may break inside a word` | same |
| `@media (prefers-reduced-motion:reduce)` [`index.html:986`](../index.html#L986) | if any expand/collapse animates, add its selector **to the existing block** | conditional | Low | `tests/test_phase3_closeout.js` (`A4`) |

Consequence: the pattern layout is **width-agnostic flex-wrap**, sized in relative units, with no
intrinsic minimum wider than one token. Any width-specific tweak that is genuinely unavoidable must
go inside one of the two existing 400px blocks and be justified in the slice's own record.

## A8 — Service worker (slice 3F only, with a release)

| Item | Change | Required? | Risk | Existing tests |
|---|---|---|---|---|
| `REQUIRED_ASSETS` [`sw.js:81`](../sw.js#L81) | add `"./pp-verb-patterns.js"` and `"./content/verb-patterns.json"` | required at release | **High.** A required asset that cannot be stored fails the whole install | `tests/test_phase4b1_service_worker_cache.js`, `tests/test_phase4b2_offline_navigation_installability.js` |
| network-first branch beside `DATA_FILE` / `AUDIO_MANIFEST_PATH` [`sw.js:118`](../sw.js#L118) | add a `PATTERN_DATA_PATH` constant and its fetch branch | required at release | Medium | same |
| `STATIC_ASSET_PATHS` [`sw.js:168`](../sw.js#L168) | exclude the new JSON, beside the existing `DATA_FILE`/manifest exclusions | required at release | Medium — otherwise the file is both cache-first and network-first | same |
| `CACHE` [`sw.js:26`](../sw.js#L26) | `popolsku-v65` → `v66` | required at release | Medium | `A1 the app-shell cache is popolsku-v65` fails until amended |
| `AUDIO_CACHE` | **no change ever** | — | content-hashed clips are retained deliberately | `A1 the audio cache is unchanged` |
| `GENERATED_PAGE_ASSETS` [`sw.js:127`](../sw.js#L127) | **no change** | — | no static pattern pages in this plan | `tests/test_phase4b2_…` |

## A9 — Version and revision markers

| Marker | Location | 3A | 3B | 3C–3E | Release |
|---|---|---|---|---|---|
| `APP_VERSION` | [`index.html:1849`](../index.html#L1849) | `8.10` | `8.10` (no deploy) | `8.10` | **bump** |
| `CACHE` | [`sw.js:26`](../sw.js#L26) | `popolsku-v65` | unchanged | unchanged | **bump** |
| `AUDIO_CACHE` | [`sw.js:27`](../sw.js#L27) | `popolsku-audio` | unchanged | unchanged | unchanged |
| progress `schemaVersion` | `pp-migrate.js` | `2` | `2` | `2` | `2` |
| `CONTENT_MIGRATION_REVISION` | `pp-migrate.js` | `2` | `2` | `2` | `2` |
| `patternDataRevision` | runtime file only | absent | `1` **in the fixture only, non-release** | fixture only | `1` on first release |

## A10 — Files that must not change, in any Phase 3 slice

`editorial/verb-pattern-candidates.json`, `editorial/priority-7-authoring-context.json`,
`priority7_tooling.py` (except by a slice that explicitly owns a tooling change),
`data-a1.js`, `data-a2.js`, `data-b1.js`, `data-grammar.js`, `data-verbs.js`, `data-scenarios.js`,
`data-podcasts.js`, `validate_content.py`, `build_pages.py`, `generate_audio.py`, `verify_audio.py`,
`pp_audio_rule.py`, `audio-manifest.json`, `audio/`, `sitemap.xml`, `robots.txt`, `manifest.json`,
`grammar/`, `vocabulary/`, `guide/`, and every existing report under `reports/`.

---

# PART B — Slice sequence

Each slice is small enough for one independent review, ends in a verifiable state, and states what
remains prohibited when it lands.

---

## Slice 3B — Non-release fixture + passive reference surface

**Objective.** Prove the whole presentation architecture end to end against synthetic data, with no
learner-facing linguistic content and no release.

**Scope — in.** `pp-verb-patterns.js`; the wrapped synthetic fixture and its test-only injection
path; the `#patterns` screen with the A–Z verb index, the case-filter chip row and the lemma entry;
`patternIndexTopics()`; the `tCount` branch; **the complete §A4a routing work — the `patterns`
branch *and* the default-deny remediation**; the `<script src>` entry; the `.vp-*` CSS; the two new
test files; the two deliberate amendments to `DeploymentIsolationTests`.

**Scope — out.** Card back pointer. Grammar cross-links. Any activity. Any audio. `content/`.
Any service-worker change. Any version bump.

**Files likely touched.** `index.html` (script list, `patternIndexTopics`, `tCount`, `routeTopic`
+ its two call sites, `startPatterns`, `pRenderIndex`, `pRenderLemma`, new screen markup,
`.vp-*` CSS); new `pp-verb-patterns.js`; new `tests/fixtures/priority7/runtime-fixture.json`;
new `tests/test_priority7_phase3b.py`; new `tests/test_priority7_patterns_ui.js`;
amended `tests/test_priority7_phase2a.py` (two assertions, narrowed).

**Tests.** All of §7.3 of the runtime contract report, plus the full existing suites green:
`python3 validate_content.py`, `python3 verify_audio.py`, `python3 build_pages.py --check`,
`python3 -m unittest discover -s tests -p 'test_*.py'`, and every `tests/*.js` under JXA.

**Manual checks.** 320px / 375px / 768px / 1280px; 200% text; VoiceOver and TalkBack on one real
device each; keyboard-only traversal of set → lemma → back; reduced-motion on; the loader-unavailable
path (rename the fixture and confirm the level simply does not appear).

**Stop conditions.** Any existing pinned total moves (10 levels of vocabulary content, 97 topics,
1,215 cards, 353 drills, 1,675 IDs, Type It 1,089, Listening 1,113, 3,377 audio, 32 sitemap URLs).
`popolsku-progress-v2` bytes change. A new storage key appears. Any CSS constraint in A7 is
violated. `content/verb-patterns.json` appears. Any real Polish lemma from the editorial corpus
appears in the fixture. **Any unknown or malformed topic `kind` can still reach an incompatible
renderer (§A4a.1(e)).** The shipping loader accepts a wrapped `project-fixture` envelope. A lemma
renders more than one entry across any filter state.

**Integration gate — all four required.**

1. Owner approval that the presentation architecture is correct, specifically including the
   **lemma-first canonical hierarchy** and case-as-filter.
2. **§A4a routing default-deny is complete and its nine regression tests pass**, including the
   mature-gate focus case. This is a gate item in its own right, not a line in the diff.
3. The harness contract of runtime contract §4.5a is proven from both sides: the loader **rejects**
   the wrapped fixture, and the injection path renders the unwrapped projection.
4. Explicit acknowledgement that the two amended `DeploymentIsolationTests` assertions were reviewed
   line by line.

No linguistic claim is approved by this slice.

---

## Slice 3C — Cross-links: Grammar out, patterns back, card pointer

**Objective.** Connect the new surface to the content the learner already has, in both directions,
with exactly one link each way.

**Scope — in.** One outbound **deep link per case topic into the case-filtered state of the verb
index** (rendered by the app at the end of the Grammar lesson, **not** authored into
`data-grammar.js`); one back-link per pattern to its case topic; the card-back `#patternLine` and its
**two-gate, `card`+`support`-only** rule.

**Scope — out.** Any change to `data-grammar.js` or the vocabulary data files. Any new drill. Any
change to `validate_content.py`. Generated pages.

**Files likely touched.** `index.html` — `gShowDone()` or `gRenderTeach()` (the outbound link's
host, to be chosen in the slice), `render()` (card back), body markup for `#patternLine`, `.vp-*`
CSS; `pp-verb-patterns.js` (reverse index, case-topic mapping).

**Design constraint that must be respected.** The case→patterns link must not be injected into the
`teach` array, because that array is authored, frozen-wording content counted in the pinned
baseline. It is rendered by the app *around* the lesson, from a static case-id → set-key map in
`pp-verb-patterns.js`.

**Tests.** Link present on exactly the seven case topics and nowhere else; the link is absent when
the loader is unavailable; the deep link opens the index **already filtered**, with the filter chip
showing `aria-pressed="true"` and clearable; card back shows chip / doorway / nothing per the two
gates, including the `bać się` doorway and the four contrast-only cards showing nothing;
`contrast`/`practice`/`context`/`topic`/`drill` refs never produce a card pointer;
`render()`'s existing accessibility assertions still pass; card totals and drill totals unchanged.

**Manual checks.** Card back at 320px with a long chip and a long aspect pair present simultaneously
(`szukać / poszukać` + `kogo? czego? · Genitive`); Grammar lesson completion focus order unchanged;
Back from a deep-linked filtered index returns to the case lesson, not to an unfiltered index.

**Stop conditions.** Any `data-*.js` byte changes. Card or drill totals move. The card back overflows
horizontally or clips at 320px / 200% text. A `contrast` reference produces any card-back affordance.
A card with an ambiguous lemma shows a chip.

**Integration gate.** Owner approval that the linking direction is right, that the deep link lands in
a filtered *view* rather than a case-owned container, and that no duplication was introduced into the
case lessons.

---

## Slice 3D — Activity work, split into two independently gated halves

**Do not design or implement either half now.** The split below exists so the two are not confused
with each other, because they have completely different prerequisites.

The earlier draft treated 3D as a single slice blocked on linguistic approval. That conflated two
different things: **exercising the activity machinery**, which is an engineering question, and
**putting real Polish in front of a learner**, which is a linguistic and product question. Only the
second is blocked on approvals.

### 3D-1 — Synthetic activity-mechanics prototype *(possible without approved Polish)*

**Objective.** Prove that a session-only pattern-practice round works — queueing, requeue-once,
option rendering, focus, announcements, and above all **that it writes nothing** — using the same
explicitly synthetic non-release fixture and test-only injection path as 3B.

**Why this does not need linguistic approval.** Nothing here asserts anything about Polish. The
fixture's items are invented, the "correct" answer is correct only within the fixture, and the whole
slice never reaches a learner. Requiring native review to test a queue is a category error, and
would also create pressure to obtain approvals prematurely just to unblock engineering.

**Prerequisites.** 3B complete. Synthetic `vp-x-…-grammar-choose-…` item records added to the
synthetic editorial fixture document, regenerated through `project-fixture` exactly as in 3B.

**Scope — in.** A `pStartPractice()` reusing the `.opts` / `.opt` markup and the
`gFocusNextOption` / `ppSetActivityOptionState` / `ppSetActivityStatus` idioms with its own queue;
item resolution and eligibility enforcement in `pp-verb-patterns.js`.

**Scope — out, and prohibited.** Any real Priority 7 pattern or item. `grammar-build`. Type It as a
cue. Mixed Quiz. Listening. Any persistence. Any learner-visible entry point — **the practice
affordance must not render for a corpus with no eligible items, which is every real corpus at this
point**, so on real data the slice is invisible by construction.

**Files likely touched.** `index.html` (`pStartPractice` + its renderers);
`pp-verb-patterns.js`; the synthetic fixture; `tests/test_priority7_patterns_ui.js`.

**Tests.** Exactly one intended answer per item; distractors come from the item record and are never
generated; requeue-once; unknown item type is **rejected**, not treated as build; a pattern whose
allowlist omits `grammar-choose` **cannot** enter the round; the progress byte-equality regression
from 3B repeated across a full practice round; `popolsku-progress-v2` byte-identical; no new storage
key.

**Stop conditions.** Any write to card progress. Any generated distractor. Any real editorial lemma
or item in the fixture. Any practice affordance rendered for a pattern with an empty allowlist.

**Integration gate.** Owner approval of the mechanics and of the negative progress evidence. **No
linguistic sign-off is required, and none may be claimed.** Completing 3D-1 says nothing whatsoever
about whether any Polish content is ready.

### 3D-2 — Integration of real Priority 7 activity items *(blocked)*

**Objective.** Allow genuinely approved patterns and their authored items to appear in the round.

**Prerequisites, all of them, before this half may begin:**

1. named native Polish linguistic reviewer(s) exist in the reviewer registry;
2. named external-verification role and accepted-source policy exist;
3. named product-approval authority exists;
4. at least one pattern has reached `reviewState: approved` through real, recorded review events;
5. that pattern's `activityEligibility` contains `grammar-choose`;
6. authored `vp-x-…-grammar-choose-…` item records exist for it, with context, authored distractors,
   one intended answer and frozen feedback, each reviewed as content in its own right;
7. a release exists or is being prepared under slice 3F — real items cannot reach a learner through
   a non-release fixture.

**Today none of these hold.** All 45 patterns are `research`, all `activityEligibility` arrays are
empty, and the reviewer and author registries are empty by design. **This half is currently
unstartable, and that is the correct state.** 3D-1 completing does not change that, and must never be
presented as progress toward it.

**Integration gate.** Native review sign-off on the items themselves, plus product approval, plus the
3F release gate. The UI being ready is not a reason to start.

---

## Slice 3E — Accessibility and mobile hardening

**Objective.** Close what 3B–3D deferred, on real devices, before anything is proposed for release.

**Scope — in.** VoiceOver / TalkBack passes on the full traversal (index → filter → filtered index →
lemma entry → back); 200% and 320px audits with measured screenshots, including the wrapped
eight-chip filter row; reduced-motion; focus-order verification for every expandable region and for
the filter's in-place list replacement (the filter must announce the new result count without
stealing focus); touch targets measured, not asserted; the JXA layout-contract assertions extended
to the `.vp-*` selectors.

**Scope — out.** New features. New content. Copy changes beyond accessibility fixes.

**Files likely touched.** `index.html` (`.vp-*` CSS, ARIA corrections); `tests/test_phase3b_mobile_layout.js`
extended (**not** rewritten — its existing assertions stay exactly as they are);
`tests/test_priority7_patterns_ui.js` extended.

**Tests.** All four A7 CSS constraints re-asserted after the additions; every new interactive element
keyboard-reachable and named; every announcement single and atomic.

**Stop conditions.** Any pinned CSS assertion in `test_phase3b_mobile_layout.js` or
`test_phase3_closeout.js` requiring modification rather than extension.

**Integration gate.** Owner approval of the accessibility evidence record.

---

## Slice 3F — Release gate *(not an engineering slice)*

**This is a decision, not a change.** It cannot be reached from the current state.

**Entry requirements.**

1. Every pattern intended for release has real external verification, real native linguistic review
   and real product approval, with recorded events and current scope digests.
2. `freeze_editorial(...)` validates the complete transition and returns a `runtimeProjection`.
3. That projection — and only that projection — becomes `content/verb-patterns.json`.
4. The unresolved Phase 2C.2 items are closed: the 12 human/teacher-priority rows, the 5 editorial
   example fixes, the `013` `required`-semantics wording gap, and the open `029` question about the
   productivity of `mówić komuś coś`.
5. The two long-standing content inconsistencies flagged in Phase 0 — `nie lubię` labelled
   "+ accusative" in `a1-food-basics-023`, and the `chcieć` case/register inconsistency — are
   resolved, because shipping a verb-pattern surface beside a card that contradicts it is worse than
   shipping neither.
6. 22 patterns currently have no example; each released pattern either has an approved example or
   ships without one by explicit decision.

**Scope when it proceeds.** `content/verb-patterns.json`; the `sw.js` changes in A8; the
`APP_VERSION` and shell-cache bumps; the offline install-failure tests; the amended cache
assertions.

**Stop conditions.** Any pattern in the file that is not `approved`. Any private key at any depth.
Any non-atomic deploy. `AUDIO_CACHE` renamed. `schemaVersion` or `CONTENT_MIGRATION_REVISION` moved.

---

## Sequencing rationale

The order is derived from the repository audit, not from a template:

- **3B first**, because the presentation risk (CSS constraints, a tenth screen, `routeTopic`'s
  missing default, `topicHaystack`'s recursion) is entirely independent of linguistic approval and
  can be fully resolved against synthetic data. Discovering the `test_phase3b_mobile_layout.js`
  width constraint *after* designing a breakpoint-based layout would be expensive.
- **3C second**, because cross-links only make sense once there is something to link to, and because
  the card back is the highest-risk surface in the whole design (density at 320px) and deserves its
  own review rather than being buried in a larger slice.
- **3D third, and split**, because its two halves have unrelated blockers. **3D-1** is ordinary
  engineering against synthetic data and can proceed on the same footing as 3B; **3D-2** is gated on
  humans who do not yet exist in the registries. Merging them, as the first draft did, would have
  either blocked mechanics work behind linguistic approval or created pressure to fabricate
  approvals to unblock engineering. Neither is acceptable, and separating them removes both.
- **3E fourth**, because device hardening is only meaningful once the final surfaces exist.
- **3F last and separate**, because release is a linguistic decision wearing an engineering costume,
  and every prior slice was explicitly designed so that reaching it changes nothing about whether
  the content is ready.

## What remains prohibited across the entire sequence

- Publishing `editorial/*` in any form, under any name.
- Any private field in any browser-reachable artifact.
- Any persistent pattern mastery, any new storage key, any migration.
- Any analytics, telemetry, cookie or identifier.
- Any change to `popolsku-progress-v2` semantics or bytes.
- Any claim, in code, copy, commit message or report, that a pattern is approved when it is
  `research`.
- Any automated promotion of a candidate's `reviewState`. AI agreement is never sufficient.
