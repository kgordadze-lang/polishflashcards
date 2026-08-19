# Priority 7 — Phase 3C Summary

**Phase:** 3C — Grammar ↔ Verb Patterns cross-links and the safe vocabulary-card pointer.
**This is a non-release engineering slice: nothing here is authorized for production release, and
nothing here makes any claim about Polish.** No real Priority 7 runtime content, no activity, no
release machinery. All 45 real patterns remain `research`.

---

## 1. Baseline

Verified before any file was opened for writing, all matching the expected values:

| Check | Expected | Verified |
|---|---|---|
| Branch | `priority-7-phase-3c-crosslinks` | ✅ |
| HEAD | `82dd0e8e7bff1f5d11a755bd15f70ec9afa20ac4` | ✅ |
| Tree | `8ec37df794e383615260d3e66ac02bad2eb00a20` | ✅ |
| Git remotes | none | ✅ zero |
| `push.default` | `nothing` | ✅ |
| Starting worktree | clean | ✅ |

Baseline test state was recorded before editing, so every later result is attributable to this phase:
**271 Python tests OK**; **33 JXA suites, 9,945 assertions, 0 failed** — identical to the totals
Phase 3B recorded.

## 2. Authoritative design read first

All five Phase 3A reports in full, `reports/priority-7-phase-3b-summary.md`, `pp-verb-patterns.js`,
the Phase 3B synthetic fixture and both its suites, the Grammar and card renderers in `index.html`,
the locked `contentRef` model (`priority7_tooling.py` `CONTENT_KINDS` / `CONTENT_PURPOSES`, pattern
data specification §11), and the Phase 1/2A material the eligibility rule depends on.

The corrected Phase 3A architecture is what was built. **`Verb Patterns → lemma → meaning → pattern`
remains the one canonical ownership hierarchy; case remains a filter / browse view / deep-linkable
state that never owns anything.** Nothing in this phase creates a case-owned container, and the
one-lemma-one-entry invariant is unchanged.

## 3. Files changed

**Modified (4):**

| File | Change |
|---|---|
| `pp-verb-patterns.js` | the static `CASE_LESSON_TOPICS` map and its two pure lookups (`caseFilterFor`, `caseLessonFor`); `caseLinksFor` and the `caseLinks` field on the lemma view; the three card-back wording constants; the `scope` field and the distinct-owner rule on `cardSupport`; two `hasOwnProperty` hardenings on the card index (§7) |
| `index.html` | `#patternLine` card-back markup; `#gPatternLine` lesson-completion markup; `ppRenderCardPattern` / `ppCardPatternClaim` / `ppOpenCardPattern`; `gRenderPatternLink` / `gPatternContinuation`; `ppPatternsLocation` / `ppCaseLessonLocation` / `ppOpenPatternsFiltered` / `ppOpenPatternsLemma` / `ppOpenPatternsIndex` / `ppOpenCaseLesson`; the `caseLinks` block in `pRenderLemma`; a fourth optional argument on `startPatterns`; two call sites (`render`, `gShowDone`); the `.vp-*` cross-link CSS |
| `tests/test_priority7_patterns_ui.js` | new section **M** (133 new assertions); two Phase-boundary assertions inverted and one element-type set widened, each documented in place (§11) |
| `tests/test_grammar_interaction.js` | `GNAMES` gained the two helpers `gShowDone` now calls, so the extracted function still runs (§13) |

**Added (1):** `tests/test_priority7_phase3c.py` — 22 file- and corpus-level isolation tests.

**Correction pass (§20).** An independent review found two semantic blockers after the first
candidate; both are fixed here, in the same four files plus this report. Every claim below describes
the corrected state.

**Not touched:** `editorial/*` (byte-identical, `verb-pattern-candidates.json` sha256
`b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`,
`priority-7-authoring-context.json` sha256 `d04dabf8…`), `priority7_tooling.py`, all seven
`data-*.js`, `sw.js`, `validate_content.py`, `build_pages.py`, `generate_audio.py`,
`verify_audio.py`, `pp_audio_rule.py`, `audio-manifest.json`, `sitemap.xml`, `robots.txt`,
`manifest.json`, `grammar/`, `vocabulary/`, `guide/`, `audio/`,
`tests/fixtures/priority7/runtime-fixture.json`, `tests/test_priority7_phase3b.py`,
`tests/test_priority7_phase2a.py`, and every pre-existing report.

Diff size: 1,463 insertions / 20 deletions across the four modified files, plus 349 lines of new
Python tests.

## 4. Grammar → Verb Patterns

**One continuation per case topic, at the end of the lesson, rendered by the app around the lesson
rather than into it.**

- Host: `gShowDone()`, i.e. the lesson-completion screen (Phase 3A journey J3), immediately after the
  three existing done-actions. It is rendered before `gPhaseView("done")` and does not touch the
  existing focus order — focus still lands on `#gDoneTitle`.
- Markup: one `.vp-continue-line` wrapper holding one native `<button type="button">`. Populated with
  `textContent`; the `→` is a separate `aria-hidden` span.
- Wording: **`Verb patterns with the Genitive →`**, with the accessible name adding the Polish case
  name around the visible one — `Verb patterns with the Genitive (Dopełniacz)` — so the visible label
  is contained in the accessible name and speech input still matches. Phase 3A's J3 sketch reads
  *"Verbs that take the Genitive"*, and that wording was corrected: **a case complement is not always
  a governed object.** A Nominative subject and a constructional frame are neither, and what the link
  opens is a filtered view of *patterns*, not a list of verbs that govern the case. The label now
  promises exactly what the destination shows. `Verbs that take the` appears in **zero** shipping
  files, comments included. The reverse label `Learn the <Case>` is unchanged — a lesson does take a
  name — and the learner-facing case chip format is untouched.
- Which topics: the **six** `grammar-cases-*` topics whose case can actually occur as a complement.
  **Vocative offers no continuation** — see below. The Mix topic (no `id`) gets nothing; so does every
  vocabulary, podcast, Type It, Listening, conversation and pattern topic.

- **No pattern content was copied into Grammar.** `data-grammar.js` is byte-identical and contains no
  `vp-`, no `verb-patterns`, no link wording. The Grammar code block contains **zero** references to
  `PP_VERB_PATTERNS`, `chipFor`, `cardSupport`, `.vp-chip`, `lemma(` or `rows(`; the two helpers it
  calls live in the Verb Patterns block. No `teach.push` / `teach.concat` / `drills.push` exists
  anywhere in the shell, so the authored, frozen, pinned arrays are untouched.
- **The link is created unconditionally**, not gated on accepted data — see §10 and the deviation
  record in §13.

**Vocative — no continuation.** Under the current runtime contract Vocative can be neither a direct
nor a prepositional complement (the editorial validator refuses one), so no pattern the contract
admits can carry it and there is no filtered view for a Vocative deep link to open. Offering one
would be a promise the corpus can never keep. The exclusion is **derived** from the central case
metadata (`!meta.direct && !meta.prepositional`), not hard-coded against the case id, so a future
schema admitting a genuine Vocative complement would answer differently with no edit here.
**Nothing was removed from the app:** the Wołacz lesson and its drills, the `CASE_ORDER` entry, the
case-table row and the reverse `caseLessonFor('vocative')` mapping are all intact, and the runtime
schema was not modified to support the link.

## 5. The case-filter deep link

`ppOpenPatternsFiltered(caseId, invoker)` locates the Verb Patterns topic by walking `LEVELS` for the
one topic whose surface key the renderer recognises, hands the invoking control to
`ppUseInvokerForNextScreen`, and calls `startPatterns(li, ti, caseId)`.

- The filter is **state on the screen**, not a navigation step: `startPatterns` sets `P.filter`
  before `show("patterns", true)` and adds no history entry of its own.
- The learner arrives in the **one canonical index**, filtered, with the matching chip
  `aria-pressed="true"`, the sub-title naming the case in both languages, the count line reading e.g.
  `2 verbs · 2 patterns take Biernik (Accusative)`, and the filter **clearable** back to `All verbs`.
- **Filtered rows stay pointers**: no explanation, no example, no back-link, no practice affordance.
- **A multi-complement frame is never truncated.** Arriving from the Locative lesson, the
  Dative + `w`+Locative pattern renders **both** chips with only the Locative one marked — verified in
  the suite and measured in the browser.
- **Every offered continuation lands in the case it names.** Because a continuation exists only for a
  case that can occur, no offered link falls back. Measured across all six with the synthetic corpus:
  `nominative, genitive, dative, accusative, instrumental, locative`.
- **Routing is not gated on data.** An unknown filter — which is every filter while no runtime exists
  — falls back to the canonical index, and the screen renders the neutral unavailable state. The
  route succeeds; nothing throws; no request is made.
- **A fallback can never masquerade as a filtered view.** Where the fallback is still reachable (a
  case the accepted corpus happens not to use, or a hand-built call), `P.filter` is `all`, the
  sub-title is **empty**, the pressed chip is `All verbs`, and the count line reports the whole corpus
  with no `take <Case>` clause. Asserted explicitly.
- Back from the deep-linked index returns to the case lesson (its own history entry), with focus
  restored to the continuation button through the existing `ppScreenReturnTargets` path.

## 6. Verb Patterns → Grammar

Each pattern in the lemma entry renders **one route back per distinct nominal case in its frame**, in
authored complement order, as native buttons labelled `Learn the Genitive →` with the accessible name
`Learn the Genitive (Dopełniacz)`. Activating one opens the **existing** case topic via
`startGrammar`, located by topic id and `kind`, never by position.

- A single-case pattern therefore gets **exactly one** link — the shape Phase 3A §4.1 specifies.
- **Infinitive-only and clause complements contribute nothing.** `bezokolicznikować` + infinitive
  renders no case link at all; its `Dative + że …` sibling renders the Dative link only. No case
  lesson is ever fabricated for a structure that has no case.
- A case repeated inside one frame (`kogoś` + `o coś`, both Accusative) is offered once, not twice.
- **No case teaching was duplicated into Verb Patterns.** The link carries a label and a topic id and
  nothing else: no ending table, no declension prose, no drill. Grammar remains the owner.

**Multi-case ownership — the one point the reports leave open.** Phase 3A §7.1 says "one link each
way" and §4.1 sketches a single `Learn the …` row, but neither §3.2's resolution table nor the
wireframes rank the complements of a two-case pattern, and §4.1a explicitly refuses to let a
multi-case pattern be split or ordered by case. Rather than invent a primacy rule, this phase offers
**both** cases, in authored order, with neither marked primary — which ranks nothing, matches the
chip row the learner is already reading, and keeps the §7.1 intent ("a route to the case that would
fix the actual gap") available when the gap could be either case. The alternative — showing no link
at all for the 9 multi-complement patterns — would be conservative about surface but would remove the
escape hatch exactly where a learner is most likely to need it. Recorded here as a decision, not
absorbed silently.

## 7. Card-pointer derivation

Built once when a runtime document is accepted, in `pp-verb-patterns.js`, entirely separate from
rendering and navigation. Deterministic and fail-closed.

**Eligibility — `kind === "card" && purpose === "support"`, and nothing else.** The test is applied
where the index is *built*, so no other relation can reach the resolver to be re-judged. In
particular: `card`+`contrast` is not a claim; `card`+`practice` and `card`+`context` are not claims;
`topic`+`support`, `topic`+`contrast`, `drill`+`practice` and every `scenario` reference never reach
the card surface. No new relation type was invented; the loader contains no `contrast` branch in
either direction, so a contrast reference can neither add a claim nor remove one.

**The algorithm.**

```
cardSupport(cardId):
  no accepted document                       -> { state: "none" }
  cardId is not a non-empty string           -> { state: "none" }
  cardId is not an OWN property of the index -> { state: "none" }
  claims = index[cardId]                     (only card+support refs are in it)
  claims.length > 1:                                                   <- Gate 1
      distinct owning lemmas > 1             -> { doorway, scope:"index", lemmaKey:null }
      otherwise                              -> { doorway, scope:"lemma", lemmaKey:<that lemma> }
  owner = lemma of the single claim
  owner.meanings > 1 or owner.patterns > 1   -> { doorway, scope:"lemma", lemmaKey:owner }
  otherwise                                  -> { chip, scope:"lemma", lemmaKey:owner,
                                                   chips:<complete frame> }
```

**Gate 1 — reference ambiguity.** Zero eligible claims → no pointer at all. Exactly one → Gate 2.
More than one → **no pattern is selected**, and *where the doorway may lead* is then a second
question with two different answers:

- **every claim owned by the same lemma** — the claims disagree about which meaning or pattern
  applies, but they agree about the verb. The doorway names that verb and opens its entry, asserting
  nothing the references do not already agree on. **This case is unchanged.**
- **claims owned by different lemmas** — nothing about "this verb" is established at all. **No lemma
  is selected.** The doorway opens the canonical index instead. Any tie-break here — claim order,
  lemma order, the card's own visible text — would be a claim invented by the sort, because the
  runtime order of two references carries no meaning. Order is proven irrelevant: reversing the two
  claims, and adding a third owner, produce the identical result.

**Gate 2 — owning-lemma ambiguity.** Even with exactly one eligible claim, a chip is printed only when
the owning runtime lemma has exactly one meaning **and** exactly one pattern. Otherwise the doorway.
This is the `bać się` failure mode: a card claimed by one pattern of a verb that has a second,
card-less meaning would otherwise teach half the verb confidently, and the omitted half would be
invisible *precisely because* it has no card. **Absence of a reference is never read as absence of a
meaning.**

**Two hardenings added this phase.** The index is now written and read through
`Object.prototype.hasOwnProperty`. Previously a card id spelling an inherited member — `constructor`,
`toString` — resolved to an `Object.prototype` value whose `.length` is a number, which would have
been treated as an existing claim list. Phase 3B derived this index but rendered nothing from it, so
the defect was unreachable; Phase 3C renders it, so it is closed here and covered by a test.

**No lemma guessing.** The pointer is derived from the explicit `contentRef` id and nothing else.
The card's Polish, its English, its hint, its topic membership, any normalisation and any similarity
between its visible word and a lemma are all ignored — asserted at source (`ppCardPatternClaim` reads
`card.id` and no other field, and contains no `card.pl`, `card.en`, `toLowerCase`, `normalize` or
`PP_ANSWER`) and behaviourally: a synthetic card whose visible word **is** a runtime lemma, with no
eligible reference, gets nothing.

## 8. Card back

- Markup: one `.pair-line` — the card's existing compact labelled-row idiom — placed after
  `#variantLine` and before `#exampleBox`, `hidden` in the markup, holding the key `PATTERN` and one
  native `<button type="button">`.
- **Direct pointer:** the claimed pattern's **complete** chip set (a two-slot frame renders both
  chips; truncating one would teach half a frame), plus an `aria-hidden` arrow. Accessible name
  `See this verb's pattern: kogo? co? · Accusative`, which contains the visible text.
- **Same-verb doorway:** the neutral line `See how this verb is used` — naming no case, no question
  and no pattern. Verified: the rendered doorway contains none of *Genitive / Dative / Locative /
  kogo? / komu? / czym?*.
- **Cross-verb doorway:** `See verb patterns`. A doorway that cannot name a verb must not sound as
  though it has, so this one promises only the reference — which is all it opens. Verified: it names
  no verb, no case and no pattern, and carries no chip. Which of the two applies is decided by the
  derivation's `scope`, never by the renderer.
- **Nothing:** the row stays `hidden` with no children, and moving between cards clears it completely
  — no stale text, no stale accessible name, never a second line. A podcast introduction hides it too.
- **The card data schema was not reopened.** `CARD_FIELDS` is unchanged (25 members, no
  reference-shaped addition), `validate_content.py` is byte-identical, no card authors a backlink, and
  card totals are unmoved at 1,215. (`pattern` and `relationType` are pre-existing card fields with
  their own long-standing meaning; this feature reads neither.)
- **Nothing internal is exposed:** no review state, no evidence, no identifier, no `contentRef`, no
  relation vocabulary, no CEFR badge, no editorial term. The card remains a vocabulary card.
- **Text as data.** Built with `createElement` + `textContent` only; the renderer contains no
  `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` or `eval`. A hostile preposition
  fed through a synthetic document renders verbatim as text: `0` `img`/`script` nodes,
  `window.__vpPwned` still `undefined`, confirmed both in the suite and in the browser.

## 9. Card-pointer interaction

Three destinations, all on the one existing screen. `ppOpenCardPattern(claim, invoker)` reads the
destination off the claim and never re-derives it, so the renderer cannot widen it.

- **Chip → the owning lemma entry**, in one step: one `show("patterns", true)`, one render, one focus
  move to the lemma `h2` (focused then revealed). No visible stop at the index.
- **Same-verb doorway → the same entry**, with every meaning and every pattern rendered side by side
  and none pre-selected. The card never picks a meaning on the learner's behalf.
- **Cross-verb doorway → the canonical all-verbs index**: `P.view === "index"`, `P.filter === "all"`,
  `P.lastLemmaKey === null`, no lemma entry rendered, focus on the screen heading. It does not fail
  silently, and it does not open an arbitrary verb.
- All three go through the existing `startPatterns` / `pRenderLemma`. **No second Verb Patterns
  renderer and no new screen exists.** A claim whose shape does not match one of the three outcomes
  exactly renders nothing rather than a dead control.
- The invoking control is handed to `ppUseInvokerForNextScreen` explicitly rather than being read off
  `document.activeElement`, because a click does not focus a button on every engine. Back therefore
  returns to the control that was pressed, through the shipping `ppScreenReturnTargets` /
  `ppRouteScreenFocus` helpers — proven in the suite and measured in the browser for both the card
  pointer and the Grammar continuation.
- In-app Back from the entry returns to the index (the existing two-step model, unchanged); the
  system Back returns to the card in one step, since the surface holds one history entry.
- An unresolvable lemma key navigates nowhere and mutates nothing.

## 10. No-runtime shipping behaviour

Ordinary startup at this tree — no injection, nothing fetched, nothing read from `tests/`:

| Requirement | Result |
|---|---|
| `Verb Patterns` tile present in Grammar | ✅ six grammar levels, the sixth is `Verb patterns`, tile reads `Reference · Not ready yet` |
| Case cross-links present on all seven case lessons | ✅ all seven resolve; the Mix topic resolves to `null` |
| Activating one is a successful route | ✅ opens `#patterns`, focus on `#pTitle`, neutral unavailable copy rendered and announced |
| The unavailable state exposes nothing internal | ✅ none of *research / review / approv / corpus / editorial / error / failed / fixture / JSON / loader* |
| No card pattern pointer anywhere | ✅ all 28 card backs of a real topic rendered through the shipping `render()`; `#patternLine` hidden on every one |
| No runtime fetch | ✅ `fetch(` count in the shell is still **2** (audio manifest + freshness HEAD); zero requests matching `content` / `verb-patterns` / `fixture` / `tests` |
| No fixture loaded | ✅ the Verb Patterns block contains no `fixture`, `editorial`, `__acceptForTest` or `JSON.parse` |
| No error | ✅ the only console errors are the pre-existing `file://` service-worker registration and directory-`HEAD` failures Phase 3B recorded |

Cross-link **existence** is not conditional on data, per brief §16 and the Phase 3B §17.1 correction:
a surface that appears only once data exists cannot have its empty state validated and cannot be
found by a learner. A card **pointer** is the opposite case and is impossible without accepted data,
by construction — `ppCardPatternClaim` returns `null` before consulting anything else.

## 11. Accessibility

Reused wholesale, never re-implemented: `ppScreenEntryTarget` + `ppRouteScreenFocus` for screen entry,
`ppScreenReturnTargets` + `ppUseInvokerForNextScreen` for return, `ppFocusAndRevealActivityTarget` for
in-screen moves, `ppSetActivityStatus` for the one announcement region. No parallel focus system.

- Every new control is a native `<button type="button">` with an `onclick` handler, so Enter and Space
  activate it and nothing needs a key handler of its own.
- Every accessible name **contains** its visible label (`Verbs that take the Genitive` ⊂
  `Verbs that take the Genitive (Dopełniacz)`; the chip text ⊂ `See this verb's pattern: …`), so
  label-in-name holds for speech input.
- Every decorative arrow is `aria-hidden="true"`; no meaning is carried by an arrow, a colour or a
  weight alone. The filter state remains `aria-pressed` plus border and weight.
- Screen-entry focus: from a case lesson → `#pTitle`; from a card → the lemma `h2`. Return focus lands
  on the invoking control in both directions, measured live.
- Touch targets: all three new controls measure **44px** high at 320px, 375px, 768px and 1280px.
- The case-filtered arrival is understandable without an announcement: the sub-title names the case,
  the pressed chip states it, and the count line reads `N verbs · N patterns take Biernik
  (Accusative)`. Applying a filter in-screen still announces once without moving focus (Phase 3B
  behaviour, unchanged).

**Not proven here:** real key synthesis. The preview harness does not deliver synthetic `Enter` to the
page — verified by pressing `Enter` on a **pre-existing** Phase 3B filter button, which also did not
activate. This is a harness limitation, not an app behaviour, and real screen readers, real key
presses and real device text scaling remain human checks, exactly as the repository's own suites
state. The structural contract (native button, type, name, handler) is asserted in tests.

## 12. Mobile

No new breakpoint (`@media` widths are still exactly `[360, 400, 400]`), nothing added to the 360px
block, no `overflow-x:hidden|clip`, no `overflow-wrap` or `word-break` on any new selector, no
animation or transition (so reduced motion needs no new rule), no new top-level category. Every new
rule is width-agnostic flex-wrap in relative units with `max-width:100%` and no intrinsic width.

Measured in the browser, not asserted:

| Width | Result |
|---|---|
| 320 × 780 | `scrollWidth === clientWidth === 320` on the case-filtered index, the lemma entry with four case links, and the card back. Filter row wraps to **four** lines, every filter 44px. Case links 44px, longest 166px wide, right edge 201px. |
| 320, densest card back | aspect pair + a two-chip pointer + example box + feedback buttons: the `PATTERN` row wraps to 95px over three visual lines, nothing clipped, nothing past the card, no horizontal scroll |
| 375 × 812 | no horizontal overflow on the filtered index, the lemma entry or the card back |
| 768 × 1024 | no horizontal overflow; four case links render; hostile text still text |
| 1280 × 800 | no horizontal overflow; the surface stays in the centred column; the continuation button is centred at 243 × 44 |

## 13. Deviations from the approved Phase 3A touch map

Four, all recorded rather than absorbed.

1. **The case continuation is created unconditionally.** Slice 3C's test list says "the link is absent
   when the loader is unavailable", written under the superseded §3.2 assumption that the
   `Verb patterns` level does not exist without data. Phase 3B's integration-gate correction (§17.1)
   reversed that: the level, the tile and the screen are ordinary information architecture and exist
   with no data. Brief §16 requires the same for cross-links. The link is therefore always present and
   may reach the neutral unavailable state — the identical behaviour the tile already has.
2. **A multi-case pattern renders one link per case** rather than a single link of unstated ownership.
   Rationale and the alternative considered are in §6. No linguistic hierarchy is invented.
3. **`tests/test_grammar_interaction.js` was amended** (`GNAMES` + 2 entries). Not in the 3C touch
   map. It is required, not optional: that suite extracts and *executes* `gShowDone`, which now calls
   one helper, so without the two names in scope the extracted function throws. The change adds names
   to an extraction list; no assertion was altered, and all 612 of its assertions still pass unchanged.
4. **`tests/test_priority7_phase3c.py` was added.** The 3C touch map names no new Python file, but
   brief §22 requires deployment isolation to be *proven* for this phase's new code paths, and those
   proofs are file- and corpus-level rather than DOM-level. It only adds assertions; no existing
   Python test was modified. `tests/test_priority7_phase2a.py` needed **no** amendment — the one
   `startPatterns` line this phase rewrote was itself added by Phase 3B, so it lies outside the
   production baseline and the `ALLOWED_INDEX_REMOVALS` list is still exact.

Two assertions in `tests/test_priority7_patterns_ui.js` pinned the 3B/3C phase boundary and were
**inverted rather than deleted**, each keeping the half of its meaning that is still a safety
property: `A7` now asserts that no case-topic id or link wording is hard-coded into the shell (they
live once in the pure helper) and that the card pointer is derived through `cardSupport` and nothing
else. `I10`'s element-type set gained `button`, because the lemma entry now carries the route back;
the property — nothing arrived that the renderer did not create — is unchanged.

## 14. Tests run and results

| Suite | Result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **293 tests, OK** (271 at baseline + 22 new) |
| `python3 -m unittest tests.test_priority7_phase3c` (new) | **22 tests, OK** |
| `python3 -m unittest tests.test_priority7_phase3b` | **19 tests, OK** (unmodified, re-run against the edited shell) |
| `python3 -m unittest tests.test_priority7_phase2a` | **77 tests, OK** (unmodified) |
| All 33 `tests/*.js` under JXA | **10,078 assertions, 0 failed** (9,945 at baseline + 133 new) |
| `tests/test_priority7_patterns_ui.js` | **407 assertions, 0 failed** (274 + 133) |
| `tests/test_grammar_interaction.js` | **612 assertions, 0 failed** (unchanged count) |
| `tests/test_phase3_closeout.js` | 510 passed |
| `tests/test_phase3b_mobile_layout.js` | 169 passed |
| `tests/test_phase3b_overlays.js` | 108 passed |
| `tests/test_phase1a_accessibility.js` | 82 passed |
| `python3 validate_content.py` | OK — levels 10, topics 97, cards 1,215, drills 353, 1,675 ids, forward baseline sha256 `2a71401d…` unchanged |
| `python3 verify_audio.py` | OK — 3,377 phrases / 3,377 manifest entries / 3,377 MP3s, nothing orphaned |
| `python3 build_pages.py --check` | OK — no drift; 23 grammar + 6 vocabulary pages, guide hub, 32 sitemap URLs |

**No pinned total moved:** 10 levels of vocabulary content, 97 topics, 1,215 cards, 353 drills, 1,675
ids, Type It 1,089 / Listening 1,113 pools, 3,377 audio files, 32 sitemap URLs.

### What the new assertions prove

**Case cross-links (M1–M3).** Both directions of the static map, before and after data is accepted,
byte-identical in both states; every non-case topic id, the empty string, `null`, a number and
inherited property names resolve to `null`. **Vocative resolves to `null` in the outbound direction**
while its lesson, its case-table row, its `CASE_ORDER` position and its reverse mapping stay intact.
The wording claims no government, no continuation anywhere says a verb *takes* the case, and the
overstated phrase is absent from every shipping file. Exactly six case topics receive the affordance;
the Vocative topic, the Mix topic and every other kind receive nothing. The rendered link's wording
and accessible name; no chip, explanation, example or identifier on it; moving to a non-case topic
clears it. The deep link opens filtered with the chip pressed and clearable; the multi-complement
frame survives the filter that brought the learner in; a filtered row still carries no explanation,
example or back-link; **all six offered continuations land in the case they name — none falls back**,
and where a fallback is still reachable it presents itself as unfiltered (empty sub-title, `All
verbs` pressed, no `take <Case>` in the count line). Grammar gained no pattern content: the grammar
code block, the three lesson renderers and `data-grammar.js` are all clean.

**Pattern → Grammar (M4).** One link for a single-case pattern; both, in authored order, for a
two-case frame; the case and not the preposition for `w`+Locative; **none** for an infinitive-only
pattern; the cased slot only for a `Dative + że …` frame; a repeated case offered once. Native buttons
with names containing their labels, `aria-hidden` arrows, no case explanation copied in. Activating
one starts the located case topic and hands over the invoker; an unresolvable topic starts nothing.

**Card derivation (M5) — the eight required cases.** (1) one support on a single-meaning
single-pattern lemma → chip, with the complete frame, including a two-slot frame rendered whole;
(2) two eligible claims → doorway, no pattern selected — **and, when the claims belong to different
verbs, no lemma selected either**: `scope: "index"`, `lemmaKey: null`, stable under reversed claim
order and under a third owner, while two claims on the *same* verb still resolve to that verb
(`scope: "lemma"`), also stable under order and with three claims; (3) one support on a multi-meaning lemma →
doorway, and the card-less second meaning is still reachable from the entry; (4) one support on a
multi-pattern lemma → doorway; (5) contrast-only → nothing, and several contrast refs still nothing;
(6) support + contrast on the same card → the support is evaluated alone, and a contrast ref from a
*different* pattern cannot make the card ambiguous; (7) no references → nothing; (8) a card whose
visible word **is** a runtime lemma, with no eligible ref → nothing. Plus: every other
kind/purpose combination produces nothing; malformed and inherited card ids fail closed; an
unavailable loader claims nothing.

**Card rendering (M6–M7).** Direct pointer / same-verb doorway / cross-verb doorway / nothing; neither
doorway names a case or question, and the cross-verb one names no verb either; no duplicate line on
re-render; the row clears completely when moving cards; an intro card shows nothing; nothing internal
in text or attributes; hostile runtime text rendered verbatim with zero injected nodes; safe DOM APIs
only; the card schema untouched. The chip and the same-verb doorway open the owning entry in one step
with focus on the lemma heading; **the cross-verb doorway opens the canonical all-verbs index with no
lemma preselected, identically under reversed claim order**; the invoker is handed over in every
case; Back returns to the index; a malformed claim shape renders nothing rather than a dead control.

**Layout (M8) and the shipping path (M9).** Every new selector present once; widths still
`[360, 400, 400]`; nothing in the 360px block; no word-breaking; 44px targets; wrap not scroll; a
focus style each; no animation. With no data: the continuation still exists and opens the unavailable
state safely, no card pointer appears for any id, no request was added, opening a lemma fails closed,
and the version and cache markers are intact.

## 15. Manual review

Performed read-only in a browser: the page was loaded from disk and, for the populated states, a
synthetic projection was injected through the console. **No repository file, tool or framework was
added, and the working tree was not touched by this.** Findings are in §10 (no-runtime), §11
(accessibility) and §12 (mobile). Flows exercised at 320 / 375 / 768 / 1280: Genitive lesson →
completion → continuation → filtered index → Back to the lesson with focus restored; card back with a
direct pointer, with a two-chip pointer, with the doorway, and with nothing; card → lemma entry;
lemma entry → case lesson → Back with focus restored to the case link. After the correction pass,
re-verified live: the Vocative lesson reaches its done screen with the continuation **hidden** and no
label; the Nominative lesson shows `Verb patterns with the Nominative →`; a cross-verb card renders
`See verb patterns →`, names neither verb, and opens the index with both verbs listed and no lemma
opened; a same-verb card renders `See how this verb is used →` and opens that verb's entry with both
its patterns. `Verbs that take the` occurs nowhere in the served document.

## 16. Deployment isolation

- **Synthetic card objects are test-only.** `p7-fixture-card…` and `SYNTHETIC-NONRELEASE` appear in
  **zero** public surfaces — `index.html`, `pp-verb-patterns.js`, `sw.js`, `sitemap.xml`, all three
  card data files and all 33 generated pages.
- **No real vocabulary card was given an invented support relationship.** The committed fixture
  carries **zero** `contentRefs` of any kind; every reference in every test is created inside the
  suite by mutating a clone. A test sweeps every real card id in `data-a1/a2/b1.js` and asserts that
  where one appears in the suite it never appears on a line that creates a support reference.
- **The fixture was not modified.** `tests/fixtures/priority7/runtime-fixture.json` is byte-identical,
  so `test_priority7_phase3b.py`'s byte-for-byte regeneration test still passes untouched, and the
  fixture-envelope / shipping-loader boundary is unchanged.
- **No guard was weakened.** All three Phase 3B `DeploymentIsolationTests` amendments stand as
  written; `tests/test_priority7_phase2a.py` was not edited and its 77 tests pass against the edited
  shell.
- **Shipping code still cannot unwrap the envelope.** `runtimeProjection`, `releaseAuthorized`,
  `artifactStatus` and `__acceptForTest` appear **zero** times in `index.html`.
- **Card derivation reads no editorial JSON.** Neither `index.html` nor `pp-verb-patterns.js`
  references `editorial/`, `verb-pattern-candidates`, `priority-7-authoring-context`, `readFileSync`,
  `require(` or `XMLHttpRequest`. The loader names private editorial keys only to reject them, and
  Phase 3B's per-access-form assertions still prove none is read.
- **No public research corpus and no real runtime file.** `content/` does not exist.

## 17. Real corpus and review state

- `editorial/verb-pattern-candidates.json` byte-identical to baseline (sha256 `b6fb8139…`), as is
  `editorial/priority-7-authoring-context.json` (sha256 `d04dabf8…`). Both were read only.
- Verified mechanically: **30 lemmas, 34 meanings, 45 patterns; `reviewState` set = `{research}`;
  0 review events; 0 `activityEligibility` entries; 0 `audioEligible: true` examples; reviewer
  registry empty; author registry empty.**
- **Zero review-state change, zero new review events, zero reviewer or author identities.** No
  linguistic claim is approved, native-reviewed or release-ready by this work.
- **Zero activity integration.** No pattern drill, no Type It feedback, no Mixed Quiz, no Listening,
  no build-the-pattern, no exercise id, no queue, no score, no progress, no mastery.
- **No progress, analytics or telemetry change.** No storage key, no schema migration, no cookie, no
  identifier. `schemaVersion` 2, `CONTENT_MIGRATION_REVISION` 2.

## 18. Version and cache state

`APP_VERSION` `8.10` — unchanged. Shell cache `popolsku-v65`, audio cache `popolsku-audio`, `sw.js`
byte-identical — no service-worker, cache or version work was done, and none is authorized outside a
release. No `patternDataRevision` anywhere in the shipping app.

## 19. Git

**Zero remotes. `push.default=nothing`. No commit. No push. No remote added.** HEAD is still
`82dd0e8e7bff1f5d11a755bd15f70ec9afa20ac4`.

Final `git status --short --untracked-files=all`:

```
 M index.html
 M pp-verb-patterns.js
 M tests/test_grammar_interaction.js
 M tests/test_priority7_patterns_ui.js
?? reports/priority-7-phase-3c-summary.md
?? tests/test_priority7_phase3c.py
```

## 20. Correction pass — the two semantic blockers

An independent review of the first candidate found two defects. Both were real, both are fixed, and
neither required redesigning Phase 3C. Recorded here rather than folded silently into the sections
above.

### 21.1 A cross-lemma card ambiguity selected a lemma

**Before.** Gate 1 correctly refused to select a *pattern* when more than one eligible
`card`+`support` claim existed, but it always returned `claims[0].lemmaKey` as the destination. When
the claims belonged to **different verbs**, that was a lemma chosen by array order — a tie-break
presented to the learner as an answer. The doorway said `See how this verb is used` and opened a verb
the references did not agree on. Same-lemma ambiguity was unaffected and was always correct.

**After.** `cardSupport` counts **distinct owning lemmas** among the claims:

| Claims | Owners | Result |
|---|---|---|
| > 1 | all one lemma | `{ doorway, scope: "lemma", lemmaKey: <that lemma> }` — opens that verb's entry |
| > 1 | more than one | `{ doorway, scope: "index", lemmaKey: null }` — opens the canonical index |

No ordering, no first claim, no first lemma, no visible card text, no other tie-break. The
cross-verb doorway reads `See verb patterns` — it promises only the reference, because that is all it
opens — and `ppOpenCardPattern` reads the destination off the claim rather than re-deriving it.
No new screen; no silent failure on click.

**Proven (M5-2a / M5-2b / M7):** state is `doorway`; no chip is returned; `lemmaKey` is `null` for a
cross-lemma ambiguity; the rendered doorway opens the all-verbs index with no lemma preselected;
reversing the claim order and adding a third owner change nothing; and two claims on the **same**
lemma still open that lemma's entry, also stable under order and at three claims. Source-level, the
old `state: "doorway", lemmaKey: claims[0].lemmaKey` shape is asserted absent.

### 21.2 The Grammar continuation overstated verb government, and offered an impossible Vocative link

**Before.** `Verbs that take the <Case>` on all seven case topics — including Nominative, where the
complement is a subject rather than a governed object, and including constructional frames that
govern nothing. Vocative was offered a deep link to a filter that **cannot exist**, since the runtime
contract forbids Vocative as a complement; it silently fell back to the unfiltered index.

**After.** `Verb patterns with the <Case>`, accessible name `Verb patterns with the <Case> (<Polish>)`
— it names what the destination actually shows and asserts no government. Applied to all supported
continuations. The reverse label `Learn the <Case>` and the learner-facing case chip format are
deliberately unchanged. `Verbs that take the` is absent from every shipping file, comments included.

Vocative now offers **no continuation at all**, derived from `!meta.direct && !meta.prepositional`
rather than hard-coded, so the rule follows the contract instead of restating it. The Wołacz lesson,
the case metadata, `CASE_ORDER` and the reverse mapping are untouched, and the runtime schema was not
modified. Supported: Nominative, Genitive, Dative, Accusative, Instrumental, Locative.

Because a continuation now exists only for a case that can occur, **no offered link falls back**. The
fallback that remains reachable by other routes is asserted never to present itself as case-filtered:
empty sub-title, `All verbs` pressed, no `take <Case>` clause in the count line.

### 21.3 What the correction did not change

`card`+`support` as the only eligible relation; contrast-only → nothing; support + contrast evaluates
the support alone; Gate 2 whole-lemma ambiguity; no lemma guessing; safe DOM rendering; no-runtime
card backs; Grammar owning case teaching; Verb Patterns owning pattern content; complete
multi-complement frames; every routing and focus behaviour; and every Phase 3B safety boundary. No
fixture, editorial file, `data-*.js`, service worker, version or cache was touched. Files changed by
the correction: `pp-verb-patterns.js`, `index.html`, `tests/test_priority7_patterns_ui.js`,
`tests/test_priority7_phase3c.py`, and this report. `tests/test_grammar_interaction.js` needed **no**
further change — its 612 assertions carry no wording or count that the correction moves.

## 21. What this phase does not claim

Phase 3C proves that the two navigation relationships work against synthetic data, that the card
pointer cannot be produced by anything except an explicit `card`+`support` reference, and that both
ambiguity gates fail closed. It claims nothing about Polish. **Test fixture ≠ validated runtime shape
≠ authorized release.** There is still no real Priority 7 runtime, no `content/verb-patterns.json`,
no runtime fetch, no public research corpus, no native-review or product-approval claim, no activity
eligibility, no audio change, no pattern mastery and no analytics. **Phase 3D was not started.**
