# Priority 8 Phase 4F1 — Verb Patterns global-search correction

## 1. Starting endpoint

- Branch: `priority-8-phase-4c-architecture`
- HEAD: `61108de211934d50d44f89d3fc1876c5752f0f06`
- Tree: `aa96d672023add340df535c921ef9806bf1ebf26`
- Parent: `2146dc960b0beadeb39d7f0ea3d7094b46afe70f`
- Subject: `Priority 8 Phase 4E2 record human audio QA disposition`
- Worktree clean, zero remotes, `push.default=nothing`, and the executable
  pre-push hook failed closed with exit 1.

No tag contains the starting endpoint, the repository has no remote, and the
recent history describes an unreleased Priority 8 release-candidate sequence.
There was no contrary evidence that v8.13/v68 had been deployed.

## 2. Acceptance defect and exact reproduction

The app was served locally and exercised in the in-app browser after normal
runtime settlement. Grammar → Verb Patterns showed `98 verbs · 269 patterns`,
contained all six requested lemmas, and the Genitive filter returned its frozen
`40 verbs · 70 patterns` baseline. Before the correction, global search gave:

| Query | Total topics | Verb Patterns result |
|---|---:|---|
| `brać` | 12 | absent |
| `gotować` | 2 | absent |
| `dojechać` | 3 | absent |
| `odpowiadać` | 0 | absent |
| `uczyć się` | 7 | absent |
| `radzić sobie` | 1 | absent |

This reproduced the acceptance failure without changing application state.

## 3. Proven root cause and loader/search lifecycle

`patternIndexTopics()` executes synchronously while `LEVELS` is constructed.
At that time `PP_VERB_PATTERNS` has no accepted runtime, so
`PP_VERB_PATTERNS.searchText()` returns the empty string. That value is copied
into the single Verb Patterns topic object stored in `LEVELS`.

On the first matching global search, `topicHaystack()` flattens that same topic
object and stores the lower-cased string in the `HAY` `WeakMap`. The result
contains the static topic labels but no released lemma corpus. Later,
`loadRuntimeDocument()` accepts the production document and populates the
loader's private runtime state. The previous settlement callback only called
`renderTopics()`/`pRenderIndex()`; it did not reconstruct `LEVELS`, replace or
update the topic object, or invalidate `HAY`. The visual count still became
98/269 because its renderer reads the live runtime, while lemma search continued
to use the stale topic snapshot/cache.

## 4. Chosen correction

Successful runtime settlement now finds the existing single Verb Patterns
topic, replaces only its `searchText` with the current authoritative
`PP_VERB_PATTERNS.searchText()` projection, deletes that topic's cached `HAY`
entry, and then performs the existing visible rerender. Failure still returns
without mutation or rendering.

This is a deterministic lifecycle refresh: no polling, timeout, new listener,
reload, duplicate topic, deep link, or secondary corpus was introduced. A query
already present during settlement is reevaluated by the existing rerender.

## 5. Search-content contract and 98/98 coverage

The loader's existing `searchText()` remains authoritative. It contributes
display lemmas plus its existing case names, prepositions, diagnostic questions,
infinitive token, and clause tokens. Polish diacritics and lexical forms are
unchanged. The focused behavioral probe derives expected display lemmas from
`content/verb-patterns.json`; all 98 of 98 produced exactly one Verb Patterns
match after settlement. Explicit lexical checks passed for `uczyć się`,
`radzić sobie`, and `spotykać się`.

The implementation contains none of the six acceptance strings and no authored
lemma list. It calls the runtime projection once after successful acceptance.

## 6. Six acceptance queries and result behavior

Post-fix browser results were:

| Query | Total topics | Verb Patterns | Opened 98/269 surface |
|---|---:|---:|---:|
| `brać` | 13 | exactly 1 | yes |
| `gotować` | 3 | exactly 1 | yes |
| `dojechać` | 4 | exactly 1 | yes |
| `odpowiadać` | 1 | exactly 1 | yes |
| `uczyć się` | 8 | exactly 1 | yes |
| `radzić sobie` | 2 | exactly 1 | yes |

The result is the established normal topic card. Opening it lands on the normal
Verb Patterns index; no lemma deep-link behavior was added.

Additional browser searches also surfaced and opened Verb Patterns for the
motion verb `chodzić` (8 total topics), lexical form `spotykać się` (4), ordinary
transitive verb `czytać` (5), and late-corpus lemma `życzyć` (3).

## 7. Async/race and unrelated-search regression

The production-function lifecycle probe covered:

- search before settlement: zero fabricated Verb Patterns match;
- rejected settlement: no exception, mutation, or rerender;
- successful settlement while `odpowiadać` was already present: the cached
  pre-load miss became one result without retyping;
- searches after settlement: 98/98 runtime lemmas matched;
- clear: the normal current-level list returned with no stale result;
- navigation-equivalent re-entry and repeated settlement: one result, no duplicate;
- reset/reload: pre-load miss followed by automatic post-settlement match.

A synthetic existing-topic ordering probe preserved `[Travel basics, Food
basics]` for their shared term and returned only Travel basics for its exclusive
term. In the browser, unrelated query `weather` continued to return nine
pre-existing topics, no Verb Patterns result, and cleared back to the normal A1
home list.

## 8. Filter and narrow product regression

| Filter | Browser result |
|---|---:|
| Nominative | 1 verb / 1 pattern |
| Accusative | 63 / 95 |
| Genitive | 40 / 70 |
| Dative | 24 / 53 |
| Instrumental | 24 / 33 |
| Locative | 19 / 25 |
| No case | 37 / 89 |
| Reset | 98 / 269 |

The browser also verified ordinary multi-pattern rendering; source/target roles
on `kupować`; direct speech on `czytać`; required lexical item `udział` on
`brać`; recognition-only presentation on `bać się`; the normal speaker control;
back/home navigation; a new clip (`Boję się pająków i latania samolotem.`); and
a reused clip (`Idę do sklepu.`). Both audio requests returned HTTP 200 and both
controls entered their playing state.

## 9. Console and network

There were zero unexplained product console errors in the acceptance session.
The local server log showed successful shell/data/runtime requests (HTTP 200 or
304), both tested MP3 requests returned 200, and there were zero product 404s,
failed content requests, or failed audio requests.

## 10. Automated results

| Gate | Result |
|---|---|
| `python3 verify_audio.py` | PASS — 3621/3621 |
| Priority 8 Phase 1 | PASS — 17/17 |
| Phase 1 playback JXA | PASS — 25/25 |
| Priority 8 Phase 1B | PASS — 1/1 |
| Phase 1B keyboard/focus JXA (additional) | PASS — 214/214 |
| Phase 4C4C | PASS — 78/78 |
| Phase 4D1 | PASS — 5/5 |
| Phase 4E1 | PASS — 5/5 |
| Phase 4F1 focused suite | PASS — 12/12 |
| migration JXA | PASS — 121/121 |
| audio fallback JXA | PASS — 585/585 |
| `validate_priority8_staging.py` | PASS |

The pre-commit full Priority 8 discovery ran 606 tests: 605 functional tests
passed and the only failure was the historical Phase 4C3 test that requires a
clean `git status` and therefore rejects every authorized later-phase working
path while the three Phase 4F1 paths are uncommitted. The complete suite is to
be rerun at the clean post-commit endpoint; its new total is 606 (the prior 594
plus 12 focused Phase 4F1 tests).

## 11. Production, audio, activity, and release immutability

- `content/verb-patterns.json`: unchanged; SHA-256
  `66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`;
  98 lemmas / 269 patterns.
- `audio-manifest.json`: unchanged; SHA-256
  `09f038097c118c6c55c00f15185a5e4207d02f103480675ad0b3a499ab3ad0a7`;
  3621 entries.
- `audio/*.mp3`: unchanged; 3621 files; 269/269 Verb Patterns coverage.
- Human QA CSV: unchanged; SHA-256
  `89d3c5de44b6a8a028c3c5e5ff6f178f68934d0c99d0d14d81c088c46ae2f58f`.
- `pp-migrate.js`: unchanged; SHA-256
  `cd729b0827687d42edba2239e104e667c387725d87fd52135e9139ba90ce6712`.
- Activity eligibility functions and all governance inputs: unchanged.
- `APP_VERSION`: `8.13`; shell cache: `popolsku-v68`; audio cache:
  `popolsku-audio`; no version/cache marker changed.

## 12. Changed paths and acceptance-retest handoff

Exactly three paths are in scope:

- `M index.html`
- `A tests/test_priority8_phase4f1_verb_patterns_search.py`
- `A reports/priority-8-phase-4f1-verb-patterns-search.md`

The local correction is ready for an independent, read-only targeted Phase 4F1
acceptance re-test after the clean committed endpoint is recorded. It is not an
integration, deployment, or release authorization.
