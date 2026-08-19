# Priority 7 — Phase 3B Summary

**Phase:** 3B — Synthetic non-release fixture + passive Verb Patterns reference UI + the required
`routeTopic` default-deny remediation. **This is a non-release engineering prototype: nothing here is
authorized for production release.**

**Revision:** integration-gate correction pass applied. The `Grammar → Verb Patterns` entry is now
part of the ordinary information architecture and is created unconditionally, so the shipping-path
no-data behaviour is a real, reachable, validated state rather than an absent one. No runtime file,
no fetch, no service-worker, cache or version change was added — those remain one atomic release
concern. See §17 for the correction record.

---

## 1. Baseline

Verified before any file was opened for writing, all matching the expected values:

| Check | Verified value |
|---|---|
| Branch | `priority-7-phase-3b-passive-ui` |
| HEAD | `e4fd568eeb22be2ed6f43946ab27a6452cfc6fdf` |
| Tree | `863af56c5c2d5758fa6c95336fe43d211e26dcd2` |
| Git remotes | **none** |
| `push.default` | `nothing` |
| Starting worktree | clean |

Baseline test state was also recorded before editing: **251** Python tests and **33** JXA suites
green, so every later failure could be attributed to this phase rather than inherited.

## 2. Authoritative design read first

All five approved Phase 3A reports were read in full, plus the locked Phase 1/2A material needed to
implement the runtime contract: `priority7_tooling.py` (envelope, projector, `PRIVATE_RUNTIME_KEYS`,
the `project-fixture` CLI), `tests/test_priority7_phase2a.py` (`DeploymentIsolationTests` and the
fictional-fixture idiom), and both `editorial/*.json` files **read-only**.

The corrected Phase 3A architecture is what was built: **`Verb Patterns → lemma → meaning → pattern`
is the one canonical ownership hierarchy, the A–Z index is the default entry, and case is a filter /
browse view / deep-linkable state that never owns anything.** The superseded case-owned draft was not
reintroduced anywhere.

## 3. Exact implementation scope

In: the pure loader; the wrapped synthetic fixture and the test-only injection path; the `#patterns`
screen with the A–Z index, the case-filter chip row and the lemma entry; the unconditional
`Grammar → Verb Patterns` entry and its no-data state; `patternIndexTopics()`; the `tCount` branch;
**the complete §A4a routing work**; the `<script src>` entry; the `.vp-*` CSS; two new test files;
three narrowly amended existing assertions.

Out, and confirmed absent: card-back pointer, Grammar cross-links, any activity, any audio,
`content/`, any service-worker change, any version bump.

## 4. Files added / modified

**Added (4):**

| File | What it is |
|---|---|
| `pp-verb-patterns.js` | the fifth pure helper: envelope validation, case metadata, question/chip/role/headline derivation, the A–Z index and case-filter views, the card-support index, the activity allowlist, and `__acceptForTest` |
| `tests/fixtures/priority7/runtime-fixture.json` | the wrapped, explicitly non-release synthetic fixture |
| `tests/test_priority7_phase3b.py` | fixture provenance, wrapper, runtime validity, anti-leak, isolation, no-request entry, version markers (19 tests) |
| `tests/test_priority7_patterns_ui.js` | loader boundary, harness contract, IA invariants, rendering, the no-runtime shipping path, routing default-deny, no-persistence (274 assertions) |

**Modified (4):**

| File | Change |
|---|---|
| `index.html` | script entry; `patternIndexTopics()`; unconditional `LEVELS.push`; `tCount` branch; `routeTopic` default-deny + both call sites; `pPatternSurfaceReady` / `pPatternDataReady`; `#patterns` screen markup; `P` state, `startPatterns`, `pRenderIndex`, `pRenderLemma` and their helpers; `.vp-*` CSS block |
| `tests/test_priority7_phase2a.py` | three deliberate amendments (§10) |
| `tests/test_phase3b_overlays.js` | `D5` narrowed to the propagating call site, plus a new assertion for the mature-gate deny focus path |
| `tests/test_phase3b_mobile_layout.js` | `D5` header inventory 10 → 11 (count only) |

**Not touched:** `editorial/*` (byte-identical, sha256 `b6fb8139…`), `priority7_tooling.py`, all seven
`data-*.js`, `sw.js`, `validate_content.py`, `build_pages.py`, `generate_audio.py`, `verify_audio.py`,
`pp_audio_rule.py`, `audio-manifest.json`, `sitemap.xml`, `robots.txt`, `manifest.json`, `grammar/`,
`vocabulary/`, `guide/`, `audio/`, and every pre-existing report.

## 5. Synthetic fixture design

**Generated, never hand-written.** `tests/test_priority7_phase3b.py` holds an invented editorial
document, writes it and its registries to a temporary directory, runs the existing non-release CLI
(`python3 priority7_tooling.py project-fixture … --test-pattern-data-revision 1 --context …`) and
asserts the committed fixture is **byte-identical** to its stdout. It therefore cannot be edited into
a different document, and no new CLI, command or release path was created.

Six invented lemmas / 7 meanings / 10 patterns, every gloss carrying a `SYNTHETIC-NONRELEASE` marker:

| Shape required by the brief | Where it lives |
|---|---|
| one lemma / one meaning / one pattern | `fikcjonować` (Accusative object) |
| one lemma, several meanings | `zetafikcjonować się` (2 meanings, different government) |
| one meaning, several patterns | `metodować` (3 sibling patterns) |
| several case complements in one frame | `metodować` Dative + `w`+Locative; `podobnikować się` Nominative + Dative |
| preposition + case | `o`+Locative, `w`+Locative, `o`+Accusative |
| lexical `się` | `zetafikcjonować się`, `podobnikować się` |
| infinitive complement | `bezokolicznikować` |
| clause complement | `bezokolicznikować` (Dative + `że` clause) |
| recognition ≠ production | 4 patterns; 2 have no production level at all |
| recognition-only status | `zetafikcjonować się` (second meaning), `podobnikować się` |
| example present / absent | 4 patterns have one, 6 have none |
| long learner-facing strings | two ~300-character explanations, one long example, one long `displayLemma` |
| mobile wrapping | exercised by the above at 320px (§12) |
| case filtering | six cases occur (all but Vocative, which the validator forbids as a complement) plus the no-case bucket |
| hostile text | `<img src=x onerror=…></span><script>…</script>` inside one explanation and one example |

The fixture is compact (16 KB, one file) and is not a second corpus. `patternDataRevision` is `1`
inside the fixture only and carries no release meaning.

**Not real content.** A mechanical anti-leak test asserts no real canonical lemma and no real gloss
appears in the fixture bytes, and that the fixture's own glosses are disjoint from the corpus.

## 6. Shipping-loader behaviour

`pp-verb-patterns.js` is pure: no DOM, no storage, no network, no `innerHTML`, no `eval`. It performs
the seven-step check in the contract's order — plain object; **closed** envelope of exactly
`{formatVersion, patternDataRevision, lemmas}`; `formatVersion === 1`; positive-integer revision;
non-empty `lemmas`; per-entity closed-enum validation; and a recursive private-key check mirroring all
**26** members of `PRIVATE_RUNTIME_KEYS`. Steps 1–5 and 7 fail the whole value; step 6 drops the
offending pattern and prunes empty ancestors, so one bad record cannot remove the feature.

Because the envelope is closed, **the wrapped fixture is refused by construction** — no branch names
`releaseAuthorized`, and none needs to. The loader:

- never fetches, never reads or writes storage, never touches the DOM;
- never unwraps a `runtimeProjection` — that string does not occur in it or in `index.html`;
- never reads a private field (asserted for every private key in every access form);
- treats `activityEligibility` as an allowlist that fails closed on an unknown or misspelled activity,
  a missing array or a non-array, and additionally refuses production activities for a
  recognition-only pattern;
- exposes **no** vocabulary for release authorization: a test asserts no exported name matches
  `/releas|authoriz|verified|frozen|approv/i`, and the file's header states plainly that accepting a
  value proves only that the value looked right.

No runtime identifier crosses the boundary: view objects are keyed by opaque integers, and a test
asserts no `vp-l-` / `vp-m-` / `vp-p-` / `vp-e-` string appears in any returned view, in the search
string, or anywhere in the rendered DOM including attributes.

**Why no fetch was wired, and what happens instead.** `content/verb-patterns.json` is prohibited
until a release gate, and the runtime contract §6 with plan §A8 require the public file, its
`REQUIRED_ASSETS` entries, its network-first branch and the shell-cache bump to land in **one atomic
release**. Wiring half of that now would be a partial release. So the loader's shipping entry point
(`acceptRuntimeDocument`) exists and is tested, and `index.html` opens no data channel at all.

**The surface exists anyway.** Creating and opening `Grammar → Verb Patterns` depends on no request
and no data: the level is pushed unconditionally at startup, the tile is always present, activating it
is a **successful route**, and the screen renders the neutral unavailable state. An entry that
appeared only once data existed could not have its empty state validated and could not be found by a
learner, so the empty state is the shipping state here — and it is exercised by tests and by direct
inspection rather than asserted. The surface being visible in this candidate does not authorize it for
production release; nothing in §14 changed.

## 7. Test-only injection behaviour

The harness lives in `tests/test_priority7_patterns_ui.js` and is the **only** place a wrapper is
opened. `unwrapNonReleaseFixtureForTest()` asserts before it reads: the object shape, then
`artifactStatus === "priority-7-runtime-projection-nonrelease-fixture"`, then
`releaseAuthorized === false`, then the presence of `runtimeProjection`. Four tests prove it throws
when any of those is missing or tampered with, so it cannot silently start consuming a bare or
authorized-looking value. The unwrapped projection then goes to
`PP_VERB_PATTERNS.__acceptForTest(...)`, which runs the same validation and builds the same views the
fetch path would feed.

Proven from both directions:

- **shipping side** — `acceptRuntimeDocument(wrappedFixture)` is `false`; the surface stays
  unavailable; a projection with `artifactStatus` or `releaseAuthorized` bolted on is rejected; a
  document that merely *contains* a valid projection is rejected; `__acceptForTest` is not a
  wrapper-stripper either;
- **test side** — the injected projection renders, and every later UI assertion runs on it.

Source-level: `__acceptForTest` appears **zero** times in `index.html`, which contains no `"tests/`
or `'tests/` literal, no fixture path, no `runtimeProjection`, no `releaseAuthorized`, no
`URLSearchParams`/query-parameter switch and no "load fixture" mode.

## 8. Passive UX implemented

- **Entry.** A `Verb patterns` level with `group:"grammar"` — the Grammar tab, no fourth top-level
  category, the three-tab row untouched. It contributes **one** topic (the index), carrying no
  identifier and a curated flat `searchText` (display lemmas, case names in both languages,
  prepositions, diagnostic questions). Tile: `Reference · 6 verbs · 10 patterns`, no Quiz pill.
- **Lemma-first index** — one canonical row per lemma, A–Z by a diacritic-folded sort key with
  `się` intact, letter headings, meanings joined, a pattern count, and **no chip** (a chip would
  assert one answer for a lemma that may have several).
- **Case filter** — eight native `<button aria-pressed>` controls derived from the cases actually
  present, in canonical case order, plus the explicit `No case (verb / clause)` bucket. Full case
  names, never abbreviations; the accessible name adds the Polish name around the visible English one
  (`Genitive (Dopełniacz)`), so speech input still matches. Applying a filter replaces the list **in
  place**: the pressed control keeps focus and the new count is announced once.
- **Filtered rows are pointers with summaries** — lemma, the matching meaning, and the pattern's
  **complete** chip set with the matching chip marked in weight, border *and* a screen-reader
  "(matches this filter)" phrase. No explanation, no example, no affordance. Filtering a
  Dative+Locative frame under either case shows both chips.
- **Lemma entry is the one owner** — `h2` lemma, a lead-in when there are several meanings, `h3` per
  meaning, and one labelled `<section>` per pattern: generated headline, recognition-level badge,
  `Understand this one` chip where applicable, a `<ul>` of chips each with its role phrase, the
  explanation, and the example when there is one. Nothing is hidden behind a toggle, so no
  `aria-expanded` is used — there is no genuine disclosure to describe.
- **Case/complement visual language** — one chip type everywhere: `kogo? czego? · Genitive`, with the
  preposition bonded inside (`z kim? z czym? · Instrumental`), the Polish half carrying `lang="pl"`
  and the case name not. Non-case complements use the same shape (`+ bezokolicznik · Infinitive`,
  `+ że … · Clause`). One tint for every case; no per-case colour, no notation system.
- **CEFR / recognition** — only the recognition level is badged, with an accessible name
  ("Recognise from A2"); a production gap is never collapsed into it and shows up as the absence of a
  production activity. Editorial vocabulary (`recognition-only`, `active-production`, `research`,
  `deferred`, `relationType` and its values, `teachingStatus`, `activityEligibility`, `contentRef`,
  `patternDataRevision`) appears nowhere in learner-facing code; asserted term by term.
- **Examples** — rendered when present; when absent the pattern is simply complete, with no
  placeholder, no "TODO", no promise. No audio anywhere.
- **Unavailable state — the shipping path at this tree.** The tile reads `Reference · Not ready yet`;
  opening it routes successfully, focuses the screen heading, and renders neutral learner copy ("This
  reference isn't ready to open yet. Everything else in the app works as usual."), announced once. A
  test asserts the copy contains none of *research / review / approv / corpus / editorial / error /
  failed / fixture / JSON / loader*, and Back restores focus to the invoking tile through the ordinary
  `ppScreenReturnTargets` path.
- **Card support index** — derived (`kind:"card"` + `purpose:"support"` only, then the meaning-
  ambiguity gate) and **rendered nowhere**: no `#patternLine`, no `render()` change, no call to
  `cardSupport` from `index.html`. Phase 3C owns that surface.

## 9. Routing default-deny fix (the hard gate)

`routeTopic()` now has a positive branch per kind and denies by default. `startTopic` stopped being
the fallthrough and became a named destination for the two kinds it can render — a topic with **no**
`kind` (vocabulary) and `"podcast"`. `patterns` has its own branch guarded by
`pPatternSurfaceReady(t)`, which is checked *before* dispatch and asks about the **surface** — is this
topic the verb index? — never about the data. Having nothing to list is therefore not a routing
failure: `pPatternDataReady()` is a separate renderer-side question, so the screen opens and says so.
A denied route: calls no `start*`
function, navigates nowhere, pushes no history entry, mutates no state, renders no error UI, emits one
`console.info`, moves no focus, and returns falsy. Both call sites propagate it: `openTopic` returns
the answer, and `#matureContinue` observes it and — because `ppCloseSharedOverlay(gate, false)` has
already suppressed the dialog's own restoration — hands focus back to the invoker captured by
`ppTakeSharedOverlayInvoker()` and retires the unused invoker via `ppUseInvokerForNextScreen(null)`.

All nine required regression assertions pass, plus extras, executed against the shipping dispatch:

1. `patterns` reaches `startPatterns` and nothing else; 2. `undefined`, `podcast`, `grammar`,
`convo`, `typeit`, `listen` all still reach their existing destinations; 3. twelve unknown kinds
(`"pattern"`, `"Patterns"`, `"PATTERNS"`, `"typeIt"`, `""`, `null`, `0`, `false`, `{}`, `[]`,
`"flashcard"`, `"grammar-choose"`) reach **no** `start*` function, and never flashcards or Grammar;
4. a denied route calls no navigation and pushes no history entry; 5. `S.levelIdx`/`S.topicIdx`
unchanged — and `routeTopic` provably contains no state assignment at all; 6. `document.activeElement`
stays on the invoking button and no focus helper is called; 7. a deny **through the mature gate**
leaves focus on the remembered invoker, never on `<body>`, with the gate closed; 8. a `patterns`
topic whose `surface` is missing or unrecognised is denied rather than rendered, while a valid
`kind:"patterns"` + `surface:"verb-index"` topic with **no accepted runtime data routes successfully**
to `startPatterns` — the renderer then detects that there is no data and shows the neutral unavailable
state, because having nothing to list is not a routing failure (§17.1);
9. falsy on deny, truthy on every successful route, propagated by both call sites.

**Stop condition satisfied:** no unknown or malformed `kind` can reach `startTopic`, `startGrammar`,
`startConvo`, `startTypeit`, `startListen` or `startPatterns`.

## 10. Deployment-isolation changes

Three amendments to `DeploymentIsolationTests`, each narrowing or strengthening, none deleted or
disabled, and each reviewed line by line:

1. **Script list eleven → twelve** (`test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths`).
   Still an exact ordered list of named files, so a thirteenth entry, a reordering or an unexpected
   path still fails.
2. **Fixture path: absent → present and only this** (`test_private_editorial_workspace_is_local_only_and_never_published`).
   **Strengthened:** `tests/fixtures/priority7` must exist, contain exactly `runtime-fixture.json`,
   and that file must carry the non-release `artifactStatus` and `releaseAuthorized: false`. The
   public-surface marker sweep that keeps the path out of the browser is unchanged and still passes.
3. **Protected surface split.** The 29 non-shell protected paths keep the original assertion — a
   `git diff --exit-code` against `f6bdc73a…` that must be empty. `index.html` moves to a new,
   narrower assertion, because this phase edits it deliberately and does not commit, so there is no
   newer reviewed commit for the baseline to move to: every line **removed** from the shell must be
   one of the five enumerated routing lines this phase replaced, and no **added** line may contain
   `editorial/`, `tests/fixtures`, `runtime-fixture`, `runtimeProjection`, `releaseAuthorized`,
   `artifactStatus`, `content/verb-patterns.json`, `__acceptForTest` or `APP_VERSION`. Nothing was
   dropped from the protected set.

New explicit isolation assertions (in `tests/test_priority7_phase3b.py`): the fixture stays under the
approved test path and nowhere else; its content, marker, wrapper fields and every synthetic lemma are
absent from `index.html`, `sw.js`, `pp-verb-patterns.js`, `sitemap.xml` and all 33 generated pages
(sitemap still exactly 32 URLs); editorial data stays private; `content/verb-patterns.json` and the
`content/` directory do not exist; shipping code cannot unwrap the envelope; the loader mirrors the
private-key list exactly while reading none of it; and every version/cache marker is unmoved.

## 11. Accessibility and mobile

Reused wholesale, never re-implemented: `ppScreenEntryTarget` + `ppRouteScreenFocus` for screen
entry, the existing `ppScreenReturnTargets` path in `show()` for exit, `ppFocusActivityTarget` /
`ppFocusAndRevealActivityTarget` for every in-screen move, and `ppSetActivityStatus` (text nodes only)
for the one announcement region. No parallel accessibility system was created.

- Keyboard: the index, the eight filters and every lemma row are native `<button>`s; the lemma entry's
  only tab stops are Back and Home, because a reference surface has no other controls. No chip is
  interactive.
- Focus: screen entry → `#pTitle`; opening a lemma → the lemma `h2` (focused then revealed); Back from
  a lemma → the row that was opened; Back from the index → home, where the existing invoker
  restoration returns focus to the topic tile; applying a filter → focus is *not* moved.
- Reading order equals visual order: headline → level → recognition chip → chip (question, case, role)
  → next chip → explanation → example. Heading hierarchy is `h1` screen → `h2` lemma → `h3` meaning,
  with patterns as labelled sections rather than headings.
- Non-colour: every case distinction is text; the filter's selected state is weight + border +
  `aria-pressed`; a filter match adds a screen-reader phrase as well as weight.
- One `sr-only role="status" aria-live="polite" aria-atomic="true"` region, written only on real state
  changes (filter result count, unavailable state), so it never announces silence.
- Mobile: no new media query (widths stay exactly `[360, 400, 400]`), nothing added to the 360px
  block, no `overflow-x:hidden|clip`, no `overflow-wrap`/`word-break` on any new selector, no
  `position:fixed`, no `visibility:hidden`, no animation or transition (so nothing for reduced motion
  to switch off). The layout is width-agnostic flex-wrap; the filter row wraps and never scrolls.

## 12. Manual checks

Automated suites aside, the surface was inspected live in a browser (read-only: the page was loaded
from disk and the fixture projection injected through the console; **no repository file, tool or
framework was added, and the working tree was not touched by this**). Measured, not assumed:

| Check | Result |
|---|---|
| 320 × 780 | `scrollWidth === clientWidth === 320`; nothing extends past x=300; filter row wraps to **four** lines; every filter button exactly **44px** tall |
| 375 × 812 | no horizontal overflow; filter row three lines |
| 1280 × 800 | no horizontal overflow; the surface stays in the centred 520px column; filter row two lines |
| Long compound pattern | `metodować komu? w czym?` renders both chips stacked with their own role lines; the ~300-character explanation and the long example wrap between tokens, no clipping |
| Multi-meaning lemma | one `h2`, lead-in sentence, two `h3` meanings, one `Understand this one` chip, one example present and one absent |
| No-example state | pattern renders complete, with no placeholder |
| Hostile text | rendered as visible text; `document.querySelectorAll('#pBody img, #pBody script').length === 0`; `window.__vpPwned` stayed `undefined` |
| Keyboard traversal | index → filter → filtered index → lemma → Back → row, with focus landing where §11 says |
| Filter in place | focus stayed on the pressed control; `aria-pressed` moved; status read `1 verb · 2 patterns take Miejscownik (Locative)` |
| Unavailable shipping path | with the loader unavailable, Grammar shows **six** levels and `Verb patterns` is the sixth; its tile reads `Reference · Not ready yet`; activating it is a **successful route** to the patterns screen with no routing-deny `console.info`; the neutral learner copy renders and is announced; Back returns focus to the tile |
| Network | `pp-verb-patterns.js` loads; **no request for `content/verb-patterns.json`** and none to any `tests/` path |
| Console | no error from this phase (the only file:// errors are the pre-existing service-worker/`HEAD` limitations) |

Real device text scaling, VoiceOver and TalkBack remain human checks, as the repository's own suites
state; slice 3E owns them.

## 13. Tests run and results

| Suite | Result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **271 tests, OK** (251 at baseline + 20 new) |
| `python3 -m unittest tests.test_priority7_phase3b` | **19 tests, OK** |
| `python3 -m unittest tests.test_priority7_phase2a` | **77 tests, OK** (76 + 1 new) |
| `python3 validate_content.py` | OK — levels 10, topics 97, cards 1,215, drills 353, 1,675 ids, forward baseline sha256 `2a71401d…` unchanged |
| `python3 verify_audio.py` | OK — 3,377 phrases / 3,377 manifest entries / 3,377 MP3s, nothing orphaned |
| `python3 build_pages.py --check` | OK — no drift; 23 grammar + 6 vocabulary pages, guide hub, 32 sitemap URLs |
| All 33 `tests/*.js` under JXA | **9,945 assertions, 0 failed** — the single authoritative total, from the final run after the correction pass |
| `tests/test_priority7_patterns_ui.js` (new) | **274 assertions, 0 failed** |
| `tests/test_phase3b_overlays.js` | 108 passed (106 + the amended and the added assertion) |
| `tests/test_phase3b_mobile_layout.js` | 169 passed |

No pinned total moved: 10 levels of vocabulary content, 97 topics, 1,215 cards, 353 drills, 1,675
ids, Type It 1,089 / Listening 1,113 pools (`test_typeit_eligibility.js`, `test_activities.js` green),
3,377 audio files, 32 sitemap URLs.

## 14. Confirmations

- **The real Priority 7 corpus was not projected, exposed, transformed or copied.**
  `editorial/verb-pattern-candidates.json` is byte-identical to the baseline (sha256
  `b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`), as is
  `editorial/priority-7-authoring-context.json`; both were read only. No real lemma, gloss or example
  appears in the fixture, in `index.html`, in `pp-verb-patterns.js` or in any generated output.
- **All 45 real patterns remain `research`.** Verified mechanically: 45 patterns, `reviewState`
  set = `{research}`, **0** review events, **0** `activityEligibility` entries, **0**
  `audioEligible: true` examples, 30 lemmas / 34 meanings unchanged.
- **Zero review-state change, zero new review events, zero reviewer or author identities.** No
  linguistic claim is approved, native-reviewed or release-ready by this work, and none is implied by
  the fixture: its "approved" records are invented verbs and exist only because the projector admits
  nothing else — which is the guard, not a loophole.
- **Zero activity integration.** No `grammar-choose`, `grammar-build`, Type It, Mixed Quiz, Listening,
  build-the-pattern, queue, score or practice affordance. `PP_TYPED_INDEX`, `poolFor`, `VOCAB_SRC` and
  `PP_USAGE` are untouched.
- **No progress, analytics or telemetry change.** No storage key, no schema migration, no cookie, no
  identifier; the whole traversal provably runs in an environment with no storage object at all.
  `schemaVersion` 2, `CONTENT_MIGRATION_REVISION` 2.
- **Version / cache state unchanged.** `APP_VERSION` `8.10`; shell cache `popolsku-v65`; audio cache
  `popolsku-audio`; no `patternDataRevision` anywhere in the shipping app; `sw.js` byte-identical.
- **Git.** Zero remotes. `push.default=nothing`. **No commit. No push. No remote added.** HEAD is
  still `e4fd568e…`.

Final `git status --short --untracked-files=all`:

```
 M index.html
 M tests/test_phase3b_mobile_layout.js
 M tests/test_phase3b_overlays.js
 M tests/test_priority7_phase2a.py
?? pp-verb-patterns.js
?? tests/fixtures/priority7/runtime-fixture.json
?? tests/test_priority7_patterns_ui.js
?? tests/test_priority7_phase3b.py
```

## 15. Deviations from the approved Phase 3A touch map

Three, all recorded rather than absorbed:

1. **`tests/test_phase3b_mobile_layout.js` was amended** (`D5`, header inventory 10 → 11). Not in the
   3B touch map — the plan lists that suite under slice 3E — but a tenth screen with the `.sbar`
   Back/Home header the plan itself specifies necessarily changes a header count. The change is
   count-only; the invariant (every header has Back and Home, and the two counts stay equal) is
   unchanged, and the D4 speed-control count stays at six because this header deliberately has none.
2. **`tests/test_phase3b_overlays.js` was amended** (`D5`). The plan's §A4 row names this suite as an
   existing test affected by the routing work, so it is in scope; the amendment replaces a literal
   assertion of the discarded call (`if(p) routeTopic(...)`) with the propagating form §A4a requires,
   keeps the other two clauses verbatim, and **adds** an assertion for the mature-gate deny focus path
   that was previously impossible to state.
3. **The fetch of `content/verb-patterns.json` was not wired**, so the shipping loader is never fed
   with real data. The runtime contract §5.3 leaves the mechanism to this phase; §6 and plan §A8
   require the file, the service-worker entries and the cache bump to land atomically at release.
   Wiring the request now would half-land that release and would also request a file that must not
   exist. Everything downstream of a successful parse is fully implemented and fully tested through
   the injection path. **The surface itself is not fetch-gated** — see §17.

One design reading worth stating: the Phase 3A wireframe sketches the filter row with abbreviations
(`Gen Dat Acc…`), while the summary's Case-UX rule and §5.1/§5.2 forbid abbreviations and the
architecture requires full case names. Full names were implemented, with the Polish name in the
accessible label, because an abbreviated visible label with a full accessible name would also break
the label-in-name expectation for speech input.

## 17. Integration-gate correction record

Phase 3B was provisionally accepted with one material scope correction and one reporting
reconciliation. Both are applied here.

### 17.1 The passive surface is reachable in the candidate

The earlier candidate created the level only when the loader already held accepted data, so with no
runtime the entry did not exist. That did not satisfy the requirement to implement and validate the
**shipping-path** unavailable state. Corrected in three edits, all inside the existing Phase 3B touch
map (`index.html`):

| Edit | Before | After |
|---|---|---|
| level synthesis | `if(PP_VERB_PATTERNS && PP_VERB_PATTERNS.available){ LEVELS.push(…) }` | unconditional `LEVELS.push(…)` — one level, one topic, no request |
| `tCount` | `PP_VERB_PATTERNS.countLabel()` | `available ? countLabel() : "Not ready yet"` — no size claimed that cannot be backed up |
| routing / render split | one `pPatternSurfaceReady(t)` that also required data, so a no-data route was **denied** | `pPatternSurfaceReady(t)` (surface only, routing) + `pPatternDataReady()` (data, renderer) |

Resulting no-runtime behaviour, verified by test **and** by direct inspection of the running app with
ordinary startup and no injection:

| Requirement | Result |
|---|---|
| `Verb Patterns` discoverable inside Grammar | yes — 6 grammar levels, the sixth is `Verb patterns`; tile `Reference · Not ready yet`, no Quiz pill |
| activating it routes to the patterns screen | `routeTopic` returns **true**, `startPatterns` runs, `#patterns` becomes the active screen |
| not treated as an unknown-kind failure | no deny, no `console.info` emitted on that path |
| screen-entry focus | `#pTitle` (the screen `h1`), focus deferred by `show("patterns", true)` |
| no runtime JSON request | zero network requests matching `content` / `verb-patterns` / `tests` / `fixture`; `fetch(` count in the shell is still 2 (audio manifest + freshness HEAD) |
| no editorial or fixture read | no `"tests/`, `editorial/`, `fixtures`, `runtime-fixture` or `JSON.parse` reference in the surface or the loader |
| no console exception | none; the only file:// console errors are the pre-existing service-worker registration failures |
| neutral unavailable copy | rendered and announced once |
| no internal terms exposed | asserted absent: research, review, approval, corpus, editorial, error, failed, fixture, JSON, loader |
| return focus | Back leaves for home and the invoking `.topic-main` tile is refocused through `ppScreenReturnTargets` |
| default-deny unchanged | all twelve unknown-kind variants still reach no `start*` function |

### 17.2 Same surface for the synthetic populated state

Injection still happens only through the harness, and it populates **the same screen with the same
renderers**: no second screen, no second level, no second topic, and no branch in the renderers that
exists only for tests. Verified in the suite (index, filters, multi-meaning lemma, multi-pattern
meaning, multi-complement frame, infinitive/clause, example present and absent, recognition treatment)
and again by direct inspection: section count and level count unchanged after injection, tile switches
from `Not ready yet` to a real count, and the loader still refuses the wrapper it was fed from.

### 17.3 New and amended tests

`tests/test_priority7_patterns_ui.js` — new section **J** covering the shipping path end to end
(entry built with no data and no request, honest tile, successful route, screen-entry focus,
unavailable copy, nothing internal, no fixture read, return focus through the real remembered-invoker
helpers, then injection populating the same surface with no duplicate). `H8` was rewritten: a no-data
pattern topic now **routes successfully**, while an unrecognised surface key is still denied, and the
two preconditions are asserted to ask different questions. `A6` now asserts the push is unconditional,
that exactly one level and one push site exist, that nothing else can add a second entry, and that no
fetch was added. `tests/test_priority7_phase3b.py` gained
`test_the_surface_exists_without_any_runtime_request` and
`test_ordinary_startup_reads_no_fixture_and_no_editorial_file`. Every pre-existing Phase 3B safety
test was preserved unchanged.

### 17.4 Assertion-total reconciliation

The earlier work log contained both 9,926 and 9,927 because two runs straddled the addition of a
storage-scope assertion. That ambiguity is retired: the totals in §13 come from **one** full run after
this correction pass — **271 Python tests** and **9,945 JXA assertions across 33 suites, 0 failed**.
This is the authoritative final total for Phase 3B.

## 16. What this phase does not claim

Phase 3B proves that the presentation architecture works against synthetic data, that the loader
boundary holds from both sides, and that no unknown topic kind can reach an incompatible renderer. It
claims nothing about Polish. **Test fixture ≠ validated runtime shape ≠ authorized release**: this
phase touched the first two and cannot reach the third. There is still no authorized real Priority 7
runtime, no real `content/verb-patterns.json`, no public research corpus, no native-review or
product-approval claim, no activity eligibility, no audio change, no pattern mastery and no analytics.
Phase 3C was not started.
