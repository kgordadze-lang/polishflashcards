# Priority 8 Phase 0 — current test inventory and results

## Executed results

| Command | Result |
|---|---|
| `python3 validate_content.py` | pass; 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 IDs, frozen forward digest unchanged |
| `python3 pp_audio_rule.py` | pass; 3,377 phrases, 25 incomplete templates correctly have no main audio |
| `python3 verify_audio.py` | pass; 3,377 required/manifest/MP3, 0 missing, 0 orphaned |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | pass; **1,999 tests**, 0 failures/errors; existing unclosed-file `ResourceWarning` messages only |
| every `tests/test_*.js` via `osascript -l JavaScript` | pass; **36 files, 10,557 assertions**, 0 failures |

There are 28 Python test modules, including 26 `test_priority7_*.py` modules, and 36 JXA modules. Direct Node execution is not a valid runner because the suites depend on JXA’s `ObjC` bridge; the attempted Node invocation failed before tests with `ObjC is not defined` and is not a product failure.

## Classification

| Class | Current coverage |
|---|---|
| Generic regression | `validate_content.py`; `test_priority5_content.py`; data/audio normalization parity; activities, answers, distractors, migration, navigation, focus, mobile, mixed, Type It, Listening and accessibility JXA suites |
| Audio rule/manifest | `pp_audio_rule.py`, `verify_audio.py`, `test_priority5_content.py`, `test_activities.js`, `test_audio_fallback.js`, `test_mixed_audio.js`, `test_listening_accessibility.js` |
| Service worker/offline | `test_phase4b1_service_worker_cache.js`, `test_phase4b2_offline_navigation_installability.js`, `test_phase4b3_audio_resilience_range_storage.js` |
| Editorial governance/stable IDs | Priority 7 Python phases 2A through 5A; schema, allocation, review digests, private/public boundary, freeze, tombstones, revision and projection |
| Runtime validation/UI | `test_priority7_phase4fi1.py`, `test_priority7_release_loader.js`, `test_priority7_patterns_ui.js`, `test_priority7_phase5a_bridge.js` |
| Phase provenance | many historical Priority 7 phase tests pin what one phase changed relative to its baseline |
| Release-only | freeze/projection/release-manifest/atomic-activation assertions, especially Phase 4FG1/FI1 and Phase 5A bridge |

## Priority 7 caveat

`tests/test_priority7_phase4fi1.py` is partly a phase-provenance and atomic-activation test. It passes in the current repository, but it should not be rewritten merely to look like a generic production regression. Future Priority 8 tests should add new generic invariants beside historical phase evidence, not alter history.

## Gaps relevant to Priority 8

No current test expects a Verb Patterns example control or includes eligible runtime examples in the audio required set. Current governance tests intentionally reject `audioEligible:true` without Listening. No test pins the exact 20/25 reuse split, detects duplicate eligible Verb Patterns utterances, or checks rapid switching among multiple controls on one lemma page. These are future Phase 1 obligations.
