# Priority 8 Phase 4C4C2 — scope historical tooling locks

## 1. Starting endpoint

This correction started on `priority-8-phase-4c-architecture` at
`e4dba274be989093b25a9367aea9ab6a9c29cbdb`, tree
`63a7d1f4b060802b3ead03bd410ce10df049f80b`, parent
`ebc17083502d7d1432b7a426c048e9baf18dfadc`, subject `Priority 8 Phase
4C4C1 fix frozen lexical-item parity`.

The worktree was clean, remotes were absent, `push.default` was `nothing`, and
the executable pre-push hook failed closed. `python3
validate_priority8_staging.py` passed before editing. The sixteen governed
Priority 8 suites ran 483 tests: 481 passed and exactly the two failures below
remained. The unchanged Phase 4C4C1 regression passed 5/5.

## 2. Exact two failures

1. `tests/test_priority8_phase4c3_canonical_projection.py` —
   `Priority8Phase4C3CanonicalProjectionTests.test_30_all_protected_inputs_and_production_paths_are_unchanged`.
   The loop over `PROTECTED_HASHES` compared the Phase 4C3 frozen SHA-256
   `9e8080f35a73680ab3d7f7f6e3f9435f83b2db56a26ebc6f48f3a4a7afa98988`
   to the live Phase 4C4C1 file SHA-256
   `c08b607ef4b6b13d89a774d86d25d54b341a65310aa49adbf7b174df61cca85c`.
2. `tests/test_priority8_phase4c4a_governance_preparation.py` —
   `RuntimeAndProductionIsolation.test_no_schema_or_runtime_source_changed`.
   `git diff --quiet 816176f... -- priority7_tooling.py` compared the Phase
   4C4A baseline to current `HEAD`, so it returned 1 after the later Phase
   4C4C1 tooling correction.

There was no third baseline failure.

## 3. Historical ownership of each lock

The Phase 4C3 SHA lock owns the exact protected-input identity at commit
`816176f591909d505549e2818d6b8d6d75c67f25`, `Priority 8 Phase 4C3 project
canonical candidates`. At that endpoint `priority7_tooling.py` has exactly the
frozen expected digest already recorded in `PROTECTED_HASHES`.

The Phase 4C4A isolation lock owns the interval beginning at the Phase 4C3
endpoint `816176f...`, passing through the governance-preparation commit
`4e81202591cf2c8609983346e3c24fe2c185a8b8`, and ending at the final Phase
4C4A endpoint `2e3e42df34c0899f7dbb93d0bbea4c24823e2e58`. Local Git proves the tooling
bytes are identical at all three checkpoints. Thus Phase 4C4A did not mutate
the tooling source it treated as an input.

## 4. Why the live failures are legitimate evolution

Phase 4C4C1 is a later, separately reviewed tooling evolution. It corrected
the independent frozen-runtime reconstruction so optional structural
`requiredLexicalItems` survives reconstruction. Neither historical phase owned
a permanent ban on future tooling corrections. Comparing a historical
invariant to live `HEAD` therefore conflated temporal identity with current
functional correctness.

The old expected digest was not changed to the current digest. No skip, xfail,
alternative hash, range, current-HEAD branch, or acceptance of arbitrary later
bytes was introduced.

## 5. Corrected historical mechanism

Both suites now use local `git show <commit>:priority7_tooling.py` byte reads,
following the repository-safe historical snapshot precedent already used by
the Phase 4C4A suite. A nonzero Git result raises `AssertionError`, so a missing
commit, tree, blob, or path fails closed. The mechanism uses no network,
checkout, worktree mutation, array-order assumption, or historical rewrite.

The Phase 4C3 test keeps the original SHA-256 value and applies it to tooling
bytes read from `816176f...`. Its other protected hashes remain live exactly as
before. The Phase 4C4A test keeps its other schema/runtime-source checks live,
while comparing exact tooling bytes across `816176f...`, `4e81202...`, and
`2e3e42d...`.

## 6. Proof the old locks remain strict

Each corrected test appends scratch bytes to an in-memory copy of its owned
historical tooling blob and requires the same equality assertion to raise.
Both tamper checks pass. Separate unavailable-object probes also raised for
both historical readers: 2/2 failed closed.

Current `HEAD` contains the authorized Phase 4C4C1 correction and both
historical methods pass directly, proving a later authorized change no longer
invalidates the checkpoints.

## 7. Current Phase 4C4C1 tooling remains live-tested

`tests/test_priority8_phase4c4c1_required_lexical_freeze_parity.py` is
unchanged. Its five tests still exercise the real normal projector, freezer,
independent frozen reconstructor, and frozen validator. They cover ordered
single/multiple `requiredLexicalItems`, absence preservation, strict
`FROZEN_RUNTIME_PARITY`, frozen structural tampering/removal/reordering, and
unknown structural-field rejection.

An additional read-only mutation probe removed the three Phase 4C4C1
reconstruction lines from an in-memory module copy. The reconstructed runtime
then omitted `requiredLexicalItems` and differed from the retained primary
runtime, so strict parity detected the former defect. No live source file was
edited for this probe.

## 8. Adversarial results

| Probe | Result |
|---|---|
| Tamper Phase 4C3 historical tooling bytes in memory | historical SHA assertion fails |
| Tamper final Phase 4C4A historical tooling bytes in memory | historical span assertion fails |
| Remove either required historical object/path | both readers fail closed |
| Keep the authorized Phase 4C4C1 change at current `HEAD` | both historical assertions pass |
| Remove the live 4C4C1 reconstruction fix in memory | current frozen-runtime parity detects the omission |
| Frozen lexical items changed, removed, reordered, or supplemented by an unknown field | current regression rejects the mutation |

Historical byte identity and current functional validation remain separate.

## 9. Test results

| Gate | Result |
|---|---|
| `python3 validate_priority8_staging.py` | PASS before and after |
| Two corrected methods directly | 2/2 PASS |
| Complete affected Phase 4C4A suite | 91/91 PASS |
| Phase 4C3 suite excluding only its pre-commit clean-worktree status method | 45/45 PASS |
| All governed tests excluding only that pre-commit status method | 482/482 PASS |
| Final clean-worktree sixteen-suite run | 483/483 PASS |
| Unchanged Phase 4C4C1 regression | 5/5 PASS |
| Governed plus Phase 4C4C1 regression | 488/488 PASS |

The clean-worktree status method necessarily receives its final result only
after the one authorized commit; the final sixteen-suite run includes it.

## 10. Five-event rehearsal and Phase 4C4C retry gate

The complete Phase 4C4C transition was rerun in memory only. Historical
revision inputs received only the already-established in-memory format-2
envelope upgrade needed by the current schema; no historical file was
rewritten. The prospective Priority 8 records received the five-event path
already established by Phase 4C4C0: the two existing events, editorial
`changes-requested`, fresh corroborated editorial acceptance, and human product
approval. Nothing was persisted.

Results: 224 approved Priority 8 patterns; 224 audio-enabled examples; 224
empty activity-eligibility arrays; 224 five-event histories; zero real
`validate_editorial` issues; zero real freeze issues; 224 admitted Priority 8
patterns; 611 new Priority 8 allocations within 765 total allocations; zero
tombstones; and byte-exact equality between the independently reconstructed
frozen runtime and the primary frozen runtime.

`priority7_tooling.py`, all editorial/governance data, canonical candidates,
stable map, candidate freeze, staging, manifest, preview, production, runtime
loader, service worker, audio, and activity code remain unchanged from the
starting `HEAD`.

**READY TO RETRY PHASE 4C4C.** The historical locks retain their exact
checkpoint claims, current tooling remains strictly regression-tested, and the
five-event freeze rehearsal remains green.
