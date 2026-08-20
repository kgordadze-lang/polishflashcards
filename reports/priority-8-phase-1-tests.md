# Priority 8 Phase 1A — tests

## Added deterministic coverage

- `tests/test_priority8_phase1.py`: official frozen transition; digest-bound governance; public/private boundary; exact stable content; schema/migration/revision; recognition-only and empty activity allowlists; exact 20/25 split; 3,402-set parity; file/manifest reconciliation; reused-byte identity; prospective-hash absence; collision/duplicate/missing/orphan negative controls; pending-QA artifacts.
- `tests/test_priority8_phase1_playback.js`: derived audio permission; no inferred activity; conditional native control; accessible naming/language/target; manifest readiness; shared replay/switching/stale/fallback path; reduced motion; offline/cache/Range routing; release markers; no analytics/storage.

The existing shared-player behavioral suites continue to exercise dual MP3 failure signals, one fallback, rapid replacement, late/stale callbacks, retry focus, visible live-region failure, and activity exit cleanup against the actual `index.html` functions. Existing service-worker suites execute the real worker.

## Revised current-head gate result

- Current-state Python: **190 passed**. This is 173 existing current-state tests plus 17 Phase 1 tests. The runner selected every test in `test_build_pages`, `test_priority5_content`, and `test_priority8_phase1` except the two exact release-state test IDs documented below.
- Existing current-state JXA: **9,406 assertions passed** across 35 files. Phase 1 JXA: **25 assertions passed**. These totals include the passing current-behavior assertions in mixed-purpose files and exclude only the exact release assertions listed below.
- `python3 validate_content.py`: pass; 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 IDs, forward digest `2a71401d8966ccbda59ec696f2c41cc3b48801d5c6059a881183b44ea3a1ce50`.
- `priority7_tooling.py validate-specification`: pass.
- `priority7_tooling.py validate-editorial`: pass against the private context and repository index.
- `priority7_tooling.py validate-runtime`: pass against the public runtime and private context.
- `priority8_phase1_transition.py` check mode: pass; source unchanged by the check, revision 2, 45 eligible examples, 135 appended governance events, zero non-empty activity allowlists.
- `python3 build_pages.py --check`: pass; 23 grammar pages, six vocabulary pages, the guide hub, 32 sitemap URLs, and 380 generated-page pronunciation controls are current.
- `python3 pp_audio_rule.py`: pass; 3,402 required phrases and 45 eligible Verb Patterns examples.
- `python3 verify_audio.py`: pass; 3,402 required phrases, 3,402 manifest entries, 3,402 MP3 files, no missing or orphaned audio.

The service-worker implementation after removing the exact `v67 -> v66`, `3,402 -> 3,377`, and `~23% -> ~24%` release/inventory metadata is byte-identical to the starting `sw.js`. The Phase 1 Python suite pins this, while 558 applicable assertions in `test_phase4b3_audio_resilience_range_storage.js` execute Range, cache, retention, quota, offline, invalid-response, and stale-entry behavior against the current worker.

## Python historical provenance and release classification

All 26 files below are tracked, unchanged Priority 7 phase suites. Their source identifies a particular phase in the module docstring/name and, except for the final I1 suite itself, layers exact phase normalizers over live data. The shared I1 block calls itself “normalisation, shared by every historical Priority 7 suite” and says its claims are restated over the prior release bundle. They are not classified from failure alone.

### NOT APPLICABLE TO MODIFIED PHASE 1 HEAD

| Module | Declared tests | Source evidence |
|---|---:|---|
| `tests.test_priority7_phase2a` | 78 | imports the explicit historical I1 normalizer; current failures are its deployment-isolation and exact I1-transition assertions |
| `tests.test_priority7_phase3b` | 19 | docstring defines a synthetic non-release fixture and asserts that no real runtime exists; historical I1 normalizer present |
| `tests.test_priority7_phase3c` | 22 | Phase 3C cross-link checkpoint; `ReleaseBoundaryTests` asserts no runtime/request and unmoved release markers; historical I1 normalizer present |
| `tests.test_priority7_phase3d1` | 44 | synthetic Phase 3D-1 prototype; explicitly asserts the real corpus is untouched research, no runtime exists, and versions are unmoved |
| `tests.test_priority7_phase3fa` | 17 | release-readiness rehearsal whose source says it keeps the real loader dormant and corpus unreleased; historical I1 normalizer present |
| `tests.test_priority7_phase4c` | 58 | pins the truthful lower governance state before later examples, reviews, approvals, freeze, and runtime existed |
| `tests.test_priority7_phase4e` | 105 | synthetic solo-maintainer amendment; source says the real 45-pattern corpus advanced by exactly nothing |
| `tests.test_priority7_phase4e1` | 99 | Phase 4E.1 governance checkpoint; source re-proves the real corpus advanced by exactly nothing and its committed-state guard is phase-pinned |
| `tests.test_priority7_phase5a` | 118 | synthetic freeze/authorization rehearsal; source checks the real corpus against the prior HEAD and includes the superseded audio-implies-Listening policy |

### NOT REPRODUCIBLE - REQUIRED HISTORICAL OBJECT ABSENT

Each module below declares the listed immutable `BASELINE_COMMIT` in source and reads/diffs it with Git. `git cat-file -e <id>^{commit}` fails for every listed object in this disposable repository.

| Module | Declared tests | Required absent commit(s) |
|---|---:|---|
| `tests.test_priority7_phase4fa` | 74 | `681ff69a191ccc6d61f73eccb21248703e1ac9d5` |
| `tests.test_priority7_phase4fb3b` | 128 | `7beb50d7b3463d7745352f1608f1e30019529fdf` |
| `tests.test_priority7_phase4fc1c` | 73 | `080d92ad49a514332f21ecd90b4a11de070a243f` |
| `tests.test_priority7_phase4fc2` | 106 | `080d92ad49a514332f21ecd90b4a11de070a243f` |
| `tests.test_priority7_phase4fc2b` | 17 | `080d92ad49a514332f21ecd90b4a11de070a243f` |
| `tests.test_priority7_phase4fc2c` | 78 | `080d92ad49a514332f21ecd90b4a11de070a243f` |
| `tests.test_priority7_phase4fc2d` | 28 | `080d92ad49a514332f21ecd90b4a11de070a243f`; also `7beb50d7b3463d7745352f1608f1e30019529fdf` |
| `tests.test_priority7_phase4fd1` | 61 | `3d613def18e9edf8bcabd331d40b5b90df30a9da`; audit baseline `ea60d346dac2de519f487c16165e1f523dd00350` |
| `tests.test_priority7_phase4fd2` | 23 | `3d613def18e9edf8bcabd331d40b5b90df30a9da`; audit baseline `ea60d346dac2de519f487c16165e1f523dd00350` |
| `tests.test_priority7_phase4fd31` | 50 | `3d613def18e9edf8bcabd331d40b5b90df30a9da` |
| `tests.test_priority7_phase4fe1` | 101 | `5aef7e4a447b57f862dabf098b575a431f5f8484` |
| `tests.test_priority7_phase4ff2` | 99 | `cd0a3bf8a0003e81d405428dc039ec3f348cb8b5` |
| `tests.test_priority7_phase4fg1` | 75 | `3fd3355c263f91abc4b9bc0e5aa9050a1f3a4f4a` |
| `tests.test_priority7_phase4fh2` | 92 | `4141872721d097e53c40f05e83b3ea730c38eff0` |
| `tests.test_priority7_phase4fh21` | 106 | `98cd258016564a381856d7b86cccf9e6402b458d` |
| `tests.test_priority7_phase4fh3` | 57 | `fa524f68bada3f0b893c8ed94835bfaa274a9b35` |
| `tests.test_priority7_phase4fi1` | 96 | `fe07bd32e0379e6b96c06659063ce30cba8514b3` |

The declared method counts total 1,824 across these 26 historical modules. No file was edited, skipped, marked expected-failure, relaxed, or parameterized.

## Exact prior-release assertions excluded from current-state counts

Two Python test IDs are release snapshots rather than current behavior:

- `tests.test_build_pages.LearningEndingTests.test_app_version_is_extracted_from_the_single_shipping_source` pins `APP_VERSION = "8.11"` in a module constant.
- `tests.test_priority5_content.Priority5HealthcareShippingTests.test_candidate_audio_occurrences_unique_counts_and_manifest_reuse` pins the global manifest and MP3 counts to 3,377 inside a Priority 5 shipping snapshot. Current 3,402 reconciliation and the unchanged Priority 5 candidate audio assertions are covered by the Phase 1 audio suite and verifier.

The following 18 JXA assertions are exact prior-release identities; all other assertions in their files passed and are included in the 9,406 current-state total:

| File | Exact release-only assertions |
|---|---|
| `test_phase2c_navigation.js` | two F1 assertions: app 8.11 and shell v66 |
| `test_phase3_closeout.js` | two G1 assertions: app 8.11 and shell v66 |
| `test_phase3b_focus_scroll.js` | H1 app 8.11 |
| `test_phase3b_mobile_layout.js` | J3 app 8.11 |
| `test_phase4b2_offline_navigation_installability.js` | A1 shell v66; two D1 app/shell assertions |
| `test_phase4b3_audio_resilience_range_storage.js` | R0 shell v66; S1 3,377 clips; two W5 app/shell assertions; W8 3,377 manifest identity |
| `test_priority7_choose_ui.js` | J3 app 8.11 release identity |
| `test_priority7_patterns_ui.js` | L2 app 8.11; M9 I1 app/cache atomic identity |
| `test_priority7_phase5a_bridge.js` | E1 exact revision-1 runtime SHA-256 |

`test_phase4b1_service_worker_cache.js` is classified as a whole release-state module: its current source contains 49 literal `popolsku-v66` references, including the cache identity under test and the cache names used to seed operational harness cases. It cannot execute coherently against v67 without altering historical source. Unchanged, it passes **1,133 assertions** against a temporary export of starting commit `e036a53c...`; the temporary export was removed afterward. Status at the modified Phase 1 head: **NOT APPLICABLE TO MODIFIED PHASE 1 HEAD**.

## Phase 0 documentation/reproducibility discrepancy

Phase 0 reports a complete 1,999-test Python pass. This workspace cannot reproduce the historical portion: at minimum the explicitly cited I1 object `fe07bd32e0379e6b96c06659063ce30cba8514b3`, and in fact every phase baseline commit listed above, is absent. This is recorded as a documentation/reproducibility discrepancy for later adjudication. It does not invalidate the Phase 0 product conclusions or the independently verified 20-reuse/25-new audio result. No approved Phase 0 report was rewritten, no object was fetched or reconstructed, and no remote, sibling, production, or integration repository was accessed.
