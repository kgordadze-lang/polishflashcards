# Priority 8 Phase 4D0 — historical release-lock scoping

## 1. Starting state

This correction started on branch `priority-8-phase-4c-architecture` at
`3d60bc61a85066007a659be4837aafc16131f0e4`, tree
`b373d5f0c6fbbf60b85c0f075ecab79ba27f7f48`. The only initial worktree
changes were the three verified Phase 4D candidate paths:
`content/verb-patterns.json`, `index.html`, and `sw.js`.

The candidate was copied without regeneration to
`/tmp/priority8-phase4d-release-candidate/`. Its recorded bytes are:

| Path | SHA-256 / marker |
|---|---|
| `content/verb-patterns.json` | `66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1` |
| `index.html` | `1a5cf7c18bf227f478883d439b13abfd93c5d822010b100a547df3c9c14fd925`; `APP_VERSION = "8.13"` |
| `sw.js` | `86baf01e4049adabc08c92a36c410dd0b46577a729f8b460744c75eb7059f14d`; `CACHE = "popolsku-v68"`; `AUDIO_CACHE = "popolsku-audio"` |
| saved three-path diff | `f58e577aa0b5c7652bfc8bdeda433e2ba73186e45aaf566bbcbb296ebe7800ef` |

The candidate corpus contains 98 lemmas, 129 meanings, 269 patterns, and 269
examples at format version 2 and pattern-data revision 3.

## 2. Exact initial failure and error inventory

With those three candidate files present, the sixteen governed Priority 8
suites ran 410 tests before class-level setup failures masked the remaining
methods: 11 failures, 4 errors, zero skips. Every item below is a
`HISTORICAL_PHASE_SNAPSHOT`; no `CURRENT_GLOBAL_INVARIANT` was violated.

| Kind | Test / setup | Original assertion or setup location | Pre-release expectation invalidated by Phase 4D | Owner |
|---|---|---|---|---|
| Error | `tests.test_priority8_phase4c1_stable_ids.Priority8Phase4C1StableIdTests.setUpClass` | test setup calling `priority8_phase4c1_stable_ids.py:332` | released identity rows must total 30/34/45/45 rather than the live 98/129/269/269 | Phase 4C1 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_01_released_contract_moves_only_format_version` | `tests/test_priority8_phase4c2_schema_extensions.py:181` | the Phase 4C2 runtime differs from its predecessor only by format version and remains revision 2 | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_02_released_counts_and_all_154_ids_are_unchanged` | line 188 | exact 30/34/45/45 and 154 released IDs | Phase 4C2 |
| Error | `Priority8Phase4C2SchemaExtensionTests.test_03_all_released_ids_reproduce_through_locked_allocator` | method call reaching `priority8_phase4c1_stable_ids.py:332` | allocator reproduction over the Phase 4C2 released 154-ID snapshot | Phase 4C2 |
| Error | `Priority8Phase4C2SchemaExtensionTests.test_04_private_611_id_map_is_byte_and_semantically_unchanged` | method call reaching `priority8_phase4c1_stable_ids.py:332` | private map union uses the Phase 4C2 154-ID release base | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_05_no_new_map_id_is_promoted_to_released_content` | line 218 | none of the 611 prospective IDs was released at Phase 4C2 | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_06_staging_freeze_map_audio_shell_and_service_worker_are_unchanged` | line 222 | exact Phase 4C2 production hashes, including pre-release `sw.js` | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_09_upgraded_editorial_projects_the_released_runtime_exactly` | line 254 | Phase 4C2's approved editorial projection equals its 30-lemma runtime | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_10_all_45_released_render_and_search_projections_are_exact` | line 272 | exact 45-pattern Phase 4C2 render/search projection | Phase 4C2 |
| Failure | `Priority8Phase4C2SchemaExtensionTests.test_22_migration_activity_and_audio_boundaries_remain_exact` | line 442 | Phase 4C2 shell remains APP 8.12 and cache v67 while migration stays revision 2 | Phase 4C2 |
| Error | `tests.test_priority8_phase4c3_canonical_projection.Priority8Phase4C3CanonicalProjectionTests.setUpClass` | test setup reaching `priority8_phase4c3_canonical_projection.py:174` | Phase 4C3 frozen runtime input has its pre-release SHA | Phase 4C3 |
| Failure | `HumanReviewPackage.test_the_preview_claims_no_release_revision_advance` | `tests/test_priority8_phase4c4a_governance_preparation.py:823` | preview revision equals the then-current production revision 2 | Phase 4C4A |
| Failure | `RuntimeAndProductionIsolation.test_production_runtime_is_untouched` | line 831 | production remains 30 lemmas and revision 2 during Phase 4C4A | Phase 4C4A |
| Failure | `RuntimeAndProductionIsolation.test_the_packaged_corpus_still_projects_only_the_released_forty_five` | line 847 | Phase 4C4A packaging still projects exactly its 45-pattern released runtime | Phase 4C4A |
| Failure | `RuntimeAndProductionIsolation.test_no_schema_or_runtime_source_changed` | line 882 | Phase 4C4A does not change its production/runtime-source interval, including `index.html` and `sw.js` | Phase 4C4A |

The separately invoked Phase 4C4C suite stopped in `setUpClass` before its 78
methods: `priority8_phase4c4c_release_freeze.py:170` compared the candidate
corpus SHA to the Phase 4C4C pre-release production SHA. That is also a
`HISTORICAL_PHASE_SNAPSHOT`, owned by Phase 4C4C.

Once these setup blockers were removed, rehearsal exposed four additional
calls inside the same five directly implicated files: the Phase 4C1
verify-only wrapper, Phase 4C3 map validation and persisted-artifact source
comparison, and Phase 4C4C's second deterministic-freeze call. They were
historical call paths masked by the initial setup errors, not additional
current/global defects, and were scoped to the same owning endpoints.

## 3. Historical endpoint mapping

| Historical claim | Immutable local-Git endpoint |
|---|---|
| Phase 4C1 released identity base | `604df149045fb91bbcf35eb54499b0ef490e1e99` |
| Phase 4C2 schema-extension result | `a858cf83a7f9d979feecfecef32c42937b5e9eec` (with `604df149...` retained as the transition's before-state) |
| Phase 4C3 canonical-projection input set | `816176f591909d505549e2818d6b8d6d75c67f25` |
| Phase 4C4A package endpoint | `4e81202591cf2c8609983346e3c24fe2c185a8b8`; unchanged-source span also checks corrected endpoint `2e3e42df34c0899f7dbb93d0bbea4c24823e2e58` against baseline `816176f...` |
| Phase 4C4C production-isolation endpoint | `3d60bc61a85066007a659be4837aafc16131f0e4` |

These endpoints come from the phase reports, constants already present in the
tests, and local commit history. Historical reads use only `git show
<commit>:<path>`, fail on any missing object/path, perform no checkout, and
never mutate the worktree.

## 4. Exact corrections

Only the five directly implicated governed test files were changed.

- Phase 4C1's released runtime and its verify-only wrapper now receive the
  Phase 4C1 runtime snapshot explicitly; the private map and candidate inputs
  remain live.
- Phase 4C2's post-transition runtime, production hashes, APP 8.12, and cache
  v67 assertions read the Phase 4C2 endpoint. The pre-transition runtime and
  loader remain pinned to the existing Phase 4C1 starting endpoint. Schema,
  projection, loader, migration, activity, and audio checks remain exact.
- Phase 4C3 regeneration, persisted-artifact comparison, and released map
  validation receive the Phase 4C3 runtime snapshot. Its protected-input
  hashes are checked against exact Phase 4C3 Git bytes.
- Phase 4C4A's preview/runtime/projection isolation checks read the owning
  package endpoint. Its no-source-change proof compares exact bytes across
  baseline, package endpoint, and corrected final endpoint instead of
  comparing a historical baseline to the current worktree.
- Phase 4C4C's immutable production gate, deterministic builds, production
  digest checks, 30/34/45/45 revision-2 check, and verify-only execution read
  exact production bytes from `3d60bc61...`. Private governance inputs remain
  live and exact.
- The Phase 4C3 path guard recognizes only the five authorized test files and
  this report as the current correction. It deliberately does not allow the
  three Phase 4D production paths, preserving the single expected future-state
  rehearsal failure.

No expected value was changed to 98, 129, 269, revision 3, APP 8.13, or cache
v68. There is no skip, xfail, expected failure, range, old-or-new alternative,
or branch on current release state.

## 5. Historical strictness

Existing test methods retain their count while adding in-memory negative
controls. The corrected locks prove that each of these mutations breaks the
same exact historical assertion:

- removal of one historical production lemma;
- historical revision 2 changed to 3;
- historical APP 8.12 changed to 8.13;
- historical shell cache v67 changed to v68;
- an appended byte on every historical production/protected blob.

The helpers fail closed when `git show` cannot resolve the requested immutable
object. Test count was not reduced.

## 6. Current/global coverage preservation

Historical byte identity is separated from current validator behavior. The
governed and Phase 4C4C adversarial suites remain live for schema closure,
stable-ID uniqueness and recomputation, release/frozen parity, review-set
admission, revision policy, source-role semantics, direct speech,
`requiredLexicalItems`, recognition-only status, activity eligibility, and
private-field exclusion. In particular, the unchanged/current mutation tests
still reject:

- malformed runtime envelopes, roles, clause kinds, and lexical-item shapes;
- duplicate/replaced stable IDs and missing allocation identities;
- incomplete or unauthorized release admission;
- source/target and purchase-price regressions;
- direct-speech downgrades;
- lexical-item removal, reorder, or tamper;
- recognition-only promotion and activity/listening leakage;
- private editorial/governance fields in public runtime validation.

The exact Phase 4D candidate also completed its prior current release-parity
checks: zero drift among the old 154 identities, 611/611 frozen-runtime parity,
and the 121-test migration suite. This correction does not replace or weaken
those present-day gates.

## 7. Clean pre-release baseline

With production restored to `3d60bc61...`:

| Gate | Result |
|---|---|
| `python3 validate_priority8_staging.py` | PASS |
| sixteen governed Priority 8 suites | 483/483 PASS |
| Phase 4C4C1 parity | 5/5 PASS |
| Phase 4C4C release-freeze | 78/78 PASS |
| `osascript -l JavaScript tests/test_migration.js` | 121/121 PASS |

The JXA migration suite must be run with `osascript`; invoking it as a Node
CommonJS test is not its execution contract.

## 8. Temporary future-release rehearsal

The exact saved candidate bytes—not regenerated output—were temporarily copied
back into only the three production paths. All three hashes matched the saved
values before testing.

| Gate | Result with Phase 4D candidate present |
|---|---|
| staging validator | PASS |
| sixteen governed Priority 8 suites | 482/483 PASS plus exactly one known dirty-worktree-guard failure |
| Phase 4C4C1 parity | 5/5 PASS |
| Phase 4C4C release-freeze | 78/78 PASS; no setup errors |
| migration | 121/121 PASS |

The sole governed failure was
`Priority8Phase4C3CanonicalProjectionTests.test_46_no_unexpected_changed_paths_exist`.
Its diagnostic contained exactly `content/verb-patterns.json`, `index.html`,
and `sw.js` in addition to the authorized Phase 4D0 test/report edits. No
production-count, revision, APP-version, cache, historical-hash, schema,
parity, semantic, or migration failure remained.

## 9. Production restoration and diff audit

After rehearsal, only the three production paths were restored from the exact
`3d60bc61...` Git tree. Their restored hashes are:

- `content/verb-patterns.json`:
  `c5e934a80e33b261a58a5dc7087e4c82e3ec9b9c684863465241173790c6a961`;
- `index.html`:
  `2257d3c9916a4cbf2420ffbf63b25e51dfd01e87e0eb153cb37386b0af1f6eab`;
- `sw.js`:
  `5f5e3d41762f14fca51f5d5984071c09ec6349c8ea2f87b36c16b8238a6a6b3e`.

The repository diff contains no production, source/tooling, loader,
migration, audio, editorial, or governance change. It contains only:

- `tests/test_priority8_phase4c1_stable_ids.py`;
- `tests/test_priority8_phase4c2_schema_extensions.py`;
- `tests/test_priority8_phase4c3_canonical_projection.py`;
- `tests/test_priority8_phase4c4a_governance_preparation.py`;
- `tests/test_priority8_phase4c4c_release_freeze.py`;
- `reports/priority-8-phase-4d0-historical-release-locks.md`.

There are many other legitimate historical phase tests in the repository;
this report's five-file set is only the set directly implicated by the named
post-release baselines and their masked call paths.

## 10. Phase 4D retry gate

Phase 4D may be retried only from a clean endpoint containing this historical
lock correction, using the unchanged three saved candidate files and rerunning
the current release validation. Phase 4D must remain its own later three-path
production commit. This Phase 4D0 change neither publishes nor integrates it.

**READY TO RETRY PHASE 4D after the clean post-commit gate.**
