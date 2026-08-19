# Priority 7 — Phase 3E Summary

## 1. Safety baseline

- Working directory: `/Users/Kaj/Downloads/Repository for Codex - Priority 7 Phase 3E`
- Branch: `priority-7-phase-3e-hardening`
- Baseline HEAD: `539f712090a7102996796748b0739310369868d5`
- Baseline tree: `2a4da600deb32fbf6f1562f2c493c54bd0e24aab`
- Remotes: zero
- `push.default`: `nothing`
- Starting tree: clean
- No commit, push or remote addition was performed.

The required pre-edit baseline was green: **337 Python tests** and **34 JXA suites / 10,409 assertions / 0 failures**. `validate_content.py`, `verify_audio.py` and `build_pages.py --check` also passed before editing.

The targeted correction pass began from the same HEAD/tree with only the existing
uncommitted Phase 3E candidate present. Independent review returned `NO-GO` on two
MEDIUM hardening gaps; sections 3.5 and 3.6 record those findings and their corrections.

## 2. Scope and authoritative material

The Phase 3A current-surface audit, implementation plan, runtime prototype contract, summary and UX integration architecture were reviewed together with the Phase 3B, 3C and 3D-1 summaries, `pp-verb-patterns.js`, all current Priority 7 tests, the shared accessibility/focus/mobile suites and the existing Grammar navigation/activity code.

This remained a hardening phase. The canonical Grammar placement, lemma-first ownership, case-filter semantics, two-gate card rule, activity/retry/scoring architecture and release boundary were not changed.

## 3. Confirmed defects and corrections

### 3.1 Supported zero-result case filter silently became All

**Reproduction:** accept a valid synthetic runtime whose patterns contain no Nominative complement, then follow the existing Nominative lesson continuation. `pFilterExists()` considered only filters present in the runtime, so `startPatterns()` silently replaced the known Nominative filter with `all`.

**Expected:** a known, structurally filterable case remains selected, reports zero results truthfully and leaves All/other filters usable. Truly unsupported values and Vocative must still fail closed to All.

**Correction:** a missing selected case is admitted only when it is a known filterable case and runtime data is available. It is inserted as a contextual selected chip in canonical case order. The count becomes `0 verbs · 0 patterns with Mianownik (Nominative)` and the empty copy becomes `No verb patterns with Mianownik (Nominative).` All clears it. Unknown values and Vocative still fall back without masquerading as active.

### 3.2 Filter wording overstated government

**Reproduction:** every filtered count used `verbs/patterns take …`, including Nominative and constructional frames.

**Correction:** filtered counts now use neutral `patterns with …` wording. The approved Grammar continuation wording remains `Verb patterns with the …`; Vocative still has no continuation.

### 3.3 Passive language-of-parts was flattened

**Reproduction:** filter names, Grammar continuations, reverse case links and direct card pointers used flat `aria-label` strings containing both Polish and English. The multi-meaning lead-in also put a Polish lemma inside an unmarked English sentence. A prior filter announcement remained in `#pStatus` after entering a lemma.

**Correction:** the passive surface now uses the same safe `{text, lang}` fragment shape as the synthetic choose path. Native button content supplies the name; Polish names/questions remain in `lang="pl"` descendants; English remains in the document language. Flat overriding labels were removed where they destroyed segmentation. Filter status is cleared on index/lemma transitions before a new state is announced.

### 3.4 Unbroken hostile runtime tokens could overflow

**Reproduction:** the layouts wrapped at spaces, but a deliberately long lemma, gloss, preposition, option, prompt or feedback token had no emergency break opportunity. A single token could therefore exceed a 320 px content column.

**Correction:** `overflow-wrap:anywhere` was added only to fields that paint runtime data: passive lemma/gloss/headline/chip/role/explanation/example fields and synthetic choose prompt/option/feedback fields. The independent-review correction completed that contract on the detail-only `.vp-lemma-head` and `.vp-meaning-head` selectors. No `overflow-x:hidden`, clipping, ellipsis, fixed width, `word-break`, new breakpoint or global selector was added. Essential grammar text remains complete.

### 3.5 Independent review: detail lemma/gloss still lacked emergency wrapping

**Reproduction:** accept a valid synthetic runtime with a 366-character single-token
`displayLemma` and a 367-character single-token English gloss, open the real index row,
then enter the lemma detail. The index copies were protected, but the detail `h2` and
meaning `h3` had no emergency break opportunity.

**Correction:** `.vp-lemma-head` and `.vp-meaning-head` now receive the same local
`overflow-wrap:anywhere` rule as the corresponding index fields. No max width was needed:
both are block/flex-column children already bounded by the content column, and `anywhere`
lowers their min-content contribution. The harness opens the detail and proves both long
strings remain complete; the exact CSS allowlists now include both selectors.

### 3.6 Independent review: duplicate filtered rows lost exact Back focus

**Reproduction:** the synthetic Locative view contains two rows for `metodować`, from
meaning 0 / sorted patterns 1 and 2. Both previously carried only lemma key `3`, so Back
from the second row rebuilt the list and `querySelector()` focused the first.

**Correction:** a filtered row now carries a JavaScript-only rendered-origin descriptor
`{lemmaKey, meaningIndex, patternIndex}`. Existing safety tests deliberately require the
loader's renderer API to strip raw runtime IDs, so the descriptor uses the narrow equivalent:
positions in the deterministic sorted public lemma view. It is copied into state, never
stored as a DOM node or serialized into DOM attributes. New row nodes are matched after
rerender. Exact first and second origins restore to themselves. If an exact descriptor
disappears, a single unambiguous lemma row is the only row fallback; duplicate candidates
fall back to the index heading rather than the wrong row.

## 4. Audit matrix

| Surface / condition | Automated or DOM/harness proof | Real-browser observation | Result |
|---|---|---|---|
| Grammar → Verb Patterns | Native button, static case map, six supported continuations, Vocative exclusion, invoker hand-off | Grammar case lesson opened at 320 px; entry layout did not overflow | Pass |
| No-runtime entry | Shipping startup, no request, no rows/filters/card links, neutral status, focus contract | 320 and 375 px plus desktop: heading focus, neutral copy, no horizontal overflow; Back restored the tile | Pass |
| General index and filters | Full synthetic runtime, native buttons, `aria-pressed`, focus retention, counts and language parts | Populated runtime is intentionally unavailable to ordinary startup | Pass (harness) |
| Zero-result filter | Valid synthetic runtime with no Nominative match; selected contextual chip; truthful zero; clear to All | Not exposed by ordinary no-runtime startup | Pass (harness) |
| Lemma / patterns | Heading hierarchy, focus/reveal, meanings, complete frames, examples, reverse links, and long-token detail rendering | Not exposed by ordinary no-runtime startup | Pass (harness) |
| Multi-complement frame | Dative + Locative remains complete under either filter; preposition and case remain bonded | Not exposed by ordinary no-runtime startup | Pass (harness) |
| Card pointer / doorway | Complete zero/direct/same-lemma/cross-lemma/multi-meaning/multi-pattern/contrast matrix and focus hand-off | No card link on ordinary no-runtime startup | Pass |
| Synthetic choose activity | Correct-first, wrong→correct, repeated misses, retries, completion truth, language fragments, hostile/long text, focus and no persistence | Test-only entry remains unreachable in ordinary startup | Pass (harness only) |
| 320 / 360 / 375 / 400 / 768 / desktop reflow | Exact CSS allowlists; wrapping and no-hidden-overflow assertions | Document `scrollWidth === clientWidth` at all six widths; pattern unavailable screen also measured at 320, 375 and 1280 | Pass for observable surfaces |
| Keyboard / focus | Native buttons; shared screen/invoker helpers; exact first/second duplicate-row restoration; safe missing-origin fallback | Heading entry and Back restoration observed on the shipping no-runtime surface | Pass by DOM/source contracts; stated browser limitation |
| Reduced motion | No Priority 7 animation added; existing reduced-motion rules unchanged | No motion-dependent state found | Pass |

## 5. Accessibility and semantics

- Screen entry remains on the Verb Patterns `h1`; a lemma entry focuses its Polish `h2` and reveals it without making it a tab stop.
- Back from a lemma returns to its exact originating filtered row with the filter intact, including either of two rows for the same lemma. A missing exact descriptor focuses a sole matching lemma row only when unambiguous; otherwise it falls back to the index heading. Screen exits use the shared remembered-invoker contract. Grammar continuation, card pointer and reverse case-link invokers are handed to that same contract.
- Filters, rows, continuations, case links, card links, options and Next are native buttons. No custom key handler was added.
- Existing `:focus-visible` rules remain for all Priority 7 controls. Existing 40 px Back/Home controls follow the app-wide convention; Phase 7-specific chips/rows/links remain at least 44 px high.
- Filter state remains `aria-pressed`; selected state is also visible in border/weight, not colour alone.
- Heading order remains `h1` screen → `h2` lemma/letter grouping → `h3` meanings. Pattern sections keep `aria-labelledby` without inventing extra headings.
- The unavailable state has one polite atomic status. Filter changes announce one count; index/lemma transitions retire stale text.
- No native semantics were replaced with ARIA roles. Structured child content now supplies mixed-language names instead of flat `aria-label` text.

No screen reader was available, so this report does **not** claim VoiceOver, TalkBack or NVDA output verification. The automated proof covers DOM semantics and language nodes, not voice switching.

## 6. Focus and navigation findings

All required routes remained intact: Grammar tile → unavailable/index, case lesson → filtered index, index row → lemma, card direct pointer → lemma, cross-lemma doorway → index, pattern → case lesson, and harness-only activity entry. Invalid routes remain default-deny and do not move focus.

The real browser confirmed entry focus on `#pTitle` and Back restoration to the Verb Patterns topic tile at 320 px. The populated-only flows are proved by the shipping functions running in the JXA fake DOM: first duplicate → first, second duplicate → second, a unique filtered row → itself, and an unavailable exact duplicate → index heading. A real populated browser was not manufactured because doing so would require a non-shipping injection path.

## 7. Language findings

Synthetic choose language fragments remain intact for the initial option, selected correct/incorrect option, revealed answer, live status and structural feedback. The correction extends the same safe fragment shape to passive mixed-language strings: filter subtitles/counts, filter control names, Grammar continuation case names, reverse case-link case names, multi-meaning lead-ins and direct card pattern chips.

All hostile fragment strings continue to be text nodes/textContent. No runtime value is parsed as HTML.

## 8. Mobile, reflow, zoom and touch

The in-app browser was measured at 320, 360, 375, 400, 768 and 1280 px. No tested page state had horizontal document overflow. After the correction, the no-runtime Verb Patterns screen was directly rechecked at 320, 375 and 1280 px: `scrollWidth === clientWidth`, both detail selectors resolved to `overflow-wrap:anywhere`, and no hidden-overflow workaround existed. The populated long-token detail is intentionally unavailable to ordinary startup; the JXA shipping-code harness opens it, preserves the complete strings, and pairs that behavior proof with the exact CSS contract.

Actual browser zoom or OS text scaling to 200% could not be controlled reliably in the available browser interface. Viewport narrowing was not misreported as zoom. Structural zoom constraints were audited instead: flex wrapping, `min-width:0`, bounded controls, complete text, emergency wrapping only on runtime-data fields, and no hidden-overflow workaround.

## 9. Empty, partial and invalid state findings

- **No runtime:** tile visible; screen opens; neutral unavailable copy; no error; no filters/rows/card links; case continuations may safely reach it.
- **Empty valid runtime:** not applicable. The public-shape validator rejects `lemmas: []`, so no valid zero-lemma document exists under the current contract.
- **Zero-match supported filter:** now retained, named, selected, truthful and clearable.
- **Unsupported filter / invalid route:** still defaults to All or denies routing as appropriate; it never masquerades as active.

## 10. Card-pointer regression

The full matrix passes unchanged: zero support → nothing; one unambiguous support → direct complete pattern; multiple supports under one lemma → lemma doorway; supports across lemmas → general index; one support on a multi-meaning or multi-pattern lemma → doorway; contrast only → nothing; support + contrast → support only; visible lemma resemblance without support → nothing. Direct pointer language parts are now preserved without changing the derivation or destination.

## 11. Synthetic activity regression

The activity remains test-only and uses the existing Grammar choose engine. Correct-first, wrong→correct retry, wrong→wrong retry, multiple retries, truthful completion copy, settled language fragments, hostile text, long prompt/options/feedback, Next focus and no-persistence assertions pass. No learner-visible entry, activity type, progress write or eligibility was added.

## 12. Files changed

- `index.html` — zero-filter UI, neutral count/empty copy, passive language fragments, stale-status retirement, targeted runtime-token wrapping, and exact rendered-row focus restoration.
- `pp-verb-patterns.js` — exposes Polish case names and a fragment-safe multi-meaning lead-in, and exposes the sorted pattern position needed by the rendered-row navigation descriptor while keeping runtime IDs behind the existing boundary.
- `tests/test_priority7_patterns_ui.js` — twenty additive hardening assertions, including the long-token detail and duplicate-row focus corrections, plus narrow expectation updates for corrected semantics.
- `tests/test_priority7_choose_ui.js` — preserves the completion harness host and pins the targeted emergency wrapping.
- `tests/test_priority7_phase2a.py` — narrowly enumerates the six pre-existing activity CSS declarations replaced by Phase 3E.
- `tests/test_phase3_closeout.js` — extends the exact audited emergency-wrap allowlist; global/container wrapping remains forbidden.
- `reports/priority-7-phase-3e-summary.md` — this report.

No `data-*.js`, editorial data, `priority7_tooling.py`, service worker, generated page, audio, version or cache file changed.

## 13. Tests and validators

Final authoritative totals:

| Command / suite | Result |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **337 tests, OK** |
| All `tests/*.js` under JXA | **34 suites, 10,429 assertions, 0 failed** |
| `tests/test_priority7_patterns_ui.js` | **427 passed, 0 failed** (407 baseline + 20 hardening assertions) |
| `tests/test_priority7_choose_ui.js` | **327 passed, 0 failed** |
| `tests/test_grammar_interaction.js` | **616 passed, 0 failed** |
| `tests/test_phase3_closeout.js` | **510 passed, 0 failed** |
| `tests/test_phase3b_mobile_layout.js` | **169 passed, 0 failed** |
| `tests/test_phase1b_keyboard_focus.js` | **214 passed, 0 failed** |
| `tests/test_phase2a_core_activity_accessibility.js` | **127 passed, 0 failed** |
| `tests/test_activities.js` / `test_round_scoring.js` / `test_typeit_eligibility.js` | **146 / 168 / 120 passed** |
| `python3 validate_content.py` | **OK** — 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 ids; baseline SHA-256 `2a71401d…` |
| `python3 verify_audio.py` | **OK** — 3,377 phrases / 3,377 manifest entries / 3,377 MP3s; no orphan |
| `python3 build_pages.py --check` | **OK** — 23 grammar + 6 vocabulary pages, guide hub, 32 sitemap URLs |
| `git diff --check` | **OK** |

## 14. Release boundary

Mechanical recheck of the private candidate file reports **45 patterns**, review-state set `{research}`, **0 review events**, **0 activity-eligibility entries**, **0 audio-eligible examples** and **0 exercise keys/IDs**. There is no production `content/verb-patterns.json`, real exercise runtime or runtime fetch. Ordinary startup has no synthetic activity, no pattern activity entry and no card pointer without accepted runtime data.

Progress/mastery, analytics, service worker and production were untouched. `APP_VERSION` remains **8.10**; service-worker cache remains **popolsku-v65**. No cache/version bump was made.

## 15. Deviations and limitations

Two existing protection tests required narrow amendments because a legitimate hardening correction changed their exact source allowlists:

1. `tests/test_priority7_phase2a.py` now enumerates the six replaced shared activity CSS declarations. It does not relax private-path, runtime, version or release checks.
2. `tests/test_phase3_closeout.js` now enumerates the runtime-data selectors allowed to use `overflow-wrap:anywhere`. Document-level/global wrapping, clipping, hidden horizontal overflow, truncation and `word-break` remain forbidden.

No dedicated new test module was necessary; the shipping-code harness in `test_priority7_patterns_ui.js` already owns the relevant DOM and routing behavior, so Phase 3E coverage was added there rather than creating a parallel harness.

Real screen-reader output, real OS text scaling/200% browser zoom, real touch hardware and a populated production browser remain manual checks outside this environment. These are not claimed as verified. The browser result for the correction is the real shipping no-runtime surface plus computed shipping CSS at 320/375/1280; populated long-detail layout and duplicate-row focus are JXA shipping-code/harness proofs, not misreported as production-browser observations.

## 16. Git and delivery state

The final worktree contains only the seven files listed in section 12. Remotes remain zero; `push.default` remains `nothing`. No commit and no push were performed. Phase 3D-2 and release work were not started.
