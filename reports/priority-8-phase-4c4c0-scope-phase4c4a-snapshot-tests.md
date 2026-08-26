# Priority 8 Phase 4C4C0 — scope Phase 4C4A tests to their historical snapshot

## 1. Starting endpoint

Phase 4C4C0 started on `priority-8-phase-4c-architecture` at
`2e3e42df34c0899f7dbb93d0bbea4c24823e2e58`, tree
`949ebe2b3618bcf3604d510d8f05d4fd86c1b8d1`, subject `Priority 8 Phase
4C4A scope historical Priority 7 locks`. The worktree was clean, remotes were
absent, `push.default` was `nothing`, and the fail-closed pre-push hook was
executable.

`python3 validate_priority8_staging.py` passed. The sixteen governed Priority
8 suites passed at 483 tests before this test-only change.

## 2. Blocking conflict

The Phase 4C4A suite had correctly asserted its own pre-product-approval
checkpoint against live files. That made its snapshot facts incompatible with a
later legitimate Phase 4C4C advancement: zero P8 product approvals, exactly
two nonhuman events, `editorial-reviewed`, disabled P8 audio, and an empty
allocation registry.

The authoritative snapshot is commit
`4e81202591cf2c8609983346e3c24fe2c185a8b8` (`Priority 8 Phase 4C4A prepare
release governance`). It is read locally through `git show`; no network or
remote access is required.

## 3. Assertion inventory and classification

Twenty-one Phase 4C4A state-snapshot checks now read the immutable endpoint:
the awaiting-human-review manifest state, zero P8 product approvals and
approved states, the 45 approved released patterns, two-event/nonhuman P8
histories, disabled P8 audio, empty P8 allocation registry, absence of a
freeze/release artifact, pre-approval audio rejection, deterministic packaging,
review-package binding, and the pre-approval nonrelease projection.

The remaining 70 test methods retain current/global inputs. They continue to
validate schema and editorial validity, reviewer/actor separation and roles,
source/evidence validity, current scope digests, stable IDs and candidate
freeze, metadata/deferral integrity, activity restrictions, runtime leakage
prohibition, production immutability, and adversarial validator failures. The
one mixed actor-registry check keeps its source and policy fields live while
reading only the historical allocation-registry assertion from the snapshot.

## 4. Exact modification

`tests/test_priority8_phase4c4a_governance_preparation.py` now declares the
Phase 4C4A commit and loads its corpus, authoring context, review manifest and
preview independently from live files. A single strict helper asserts the
historical state; it does not accept either state, ranges, skips, or current
state branching. Live manifest bytes are additionally required to equal the
historical review-input manifest, consistent with the existing bridge's
immutable pre-approval review-package design.

No editorial, governance, runtime, production, tooling, audio, manifest,
preview, stable-map, candidate, or freeze-input bytes changed.

## 5. Historical test-strength proof

The strict historical helper passes against the exact `4e812025` snapshot and
is explicitly required to fail when a copied snapshot contains any one of:

- a product-approval event;
- an approved P8 pattern;
- one allocation-registry entry;
- a third P8 review event; or
- an audio-enabled P8 example.

The helper's data source is the immutable historical commit, so a legitimate
future live advancement cannot weaken or invalidate any of those assertions.

## 6. Future-state rehearsal

No repository file was modified during either rehearsal. The requested direct
two-to-three-event rehearsal set all 224 P8 examples to `audioEligible: true`,
then appended one valid human product approval per pattern with current
product-scope digests dated `2026-08-26`. It correctly failed validation with
`AUDIO_NOT_AUTHORIZED` for all 224 rows.

This is a separate Phase 4C4C design gate, not a defect in the test scoping:
`review_scope` includes examples (and therefore `audioEligible`) at the
editorial tier. Changing audio invalidates the standing editorial-review
digest. The smallest valid in-memory transition is therefore five events per
P8 pattern: the existing reference/editorial events, then editorial
`changes-requested`, fresh corroborated editorial acceptance, and human product
approval. That rehearsal validated with zero issues, produced 224 approved
patterns, 224 audio-enabled examples, empty activity eligibility, and 611
schema-valid P8 allocation records.

It does not satisfy the requested Phase 4C4C `2 → 3` event transition. Phase
4C4C must therefore reconcile its event-count instruction with the locked
scope-digest rules before it is retried.

## 7. Current/global adversarial preservation

The unchanged adversarial suite continues to reject an invalid reviewer role,
a nonhuman product approver, broken source identity, stale scope digest,
stable-ID or key corruption, metadata-only promotion, structural drift, and
pre-approval audio authorization. Runtime-isolation and activity-authorization
checks remain live and unscoped.

## 8. Test result and gate

The directly affected Phase 4C4A suite passed all 91 tests after the change.
The Phase 4C4C0 snapshot scoping is complete, but the mandated exact
future-state rehearsal failed its 2-to-3-event requirement for the grounded
scope reason above.

**NO — PHASE 4C4C STILL BLOCKED.** A revised, internally consistent Phase
4C4C instruction must authorize the required fresh editorial tier before human
product approval, or explicitly change the locked review-scope architecture in
a separately governed task.
