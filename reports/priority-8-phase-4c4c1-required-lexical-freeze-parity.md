# Priority 8 Phase 4C4C1 — frozen runtime `requiredLexicalItems` parity correction

## 1. Starting endpoint and scope

Starting endpoint: `priority-8-phase-4c-architecture` at
`ebc17083502d7d1432b7a426c048e9baf18dfadc`, tree
`31fd756dc4d49310a8c6fc745a1b39de52613270`, with a clean worktree, zero
remotes, `push.default=nothing`, and the executable fail-closed pre-push hook.

This narrow prerequisite corrects one shared frozen-runtime reconstruction
omission. It does not alter editorial governance, production data, IDs,
allocation state, audio, activity eligibility, or release authorization.

## 2. Exact defect and root cause

The normal runtime projector copied an optional pattern-level
`requiredLexicalItems` array, and frozen structure retained the same array. The
independent frozen-runtime reconstruction omitted it. The existing strict
`FROZEN_RUNTIME_PARITY` gate correctly rejected the resulting incomplete
reconstruction.

An unmodified in-memory five-event Phase 4C4C rehearsal reproduced exactly one
freeze issue, `FROZEN_RUNTIME_PARITY`. Comparing normal projection to frozen
reconstruction found exactly two differences: absent
`requiredLexicalItems: ["udział"]` fields on the Priority 8 `brać` and `wziąć`
participation patterns. No other structural field differed.

## 3. Minimal correction and generic contract

The frozen reconstruction now copies `requiredLexicalItems` exactly when it is
present in frozen pattern structure, matching the normal projector's optional
field semantics. It creates no default array when the field is absent.

The change is three lines in `_derive_runtime_from_frozen`; it copies the
existing ordered array with `copy.deepcopy` only when frozen pattern structure
holds the field. No validator, scope/digest calculation, allocation, review,
policy, normal projection, or runtime schema logic changed.

## 4. Regression and adversarial coverage

The dedicated regression suite uses the real `freeze_editorial`, normal
projector, frozen reconstructor, and frozen validator. It proves one-item and
ordered multiple-item round trips, absence preservation, runtime-only parity
rejection, frozen-structure rejection, ordered-array changes, and unknown
frozen structure fields.

The validator remains fail-closed. Runtime-only lexical-item changes produce
`FROZEN_RUNTIME_PARITY`. Frozen-structure changes and removals are rejected
earlier by `FROZEN_SCOPE_PARITY`, because current frozen scope intentionally
includes this structural field; the independently reconstructed runtime also
differs from the retained runtime. Reordering is not normalized away. Unknown
frozen structure fields remain rejected by the closed schema.

## 5. Real Priority 8 verification and five-event rehearsal

The fully valid five-event transition was run wholly in memory after the
correction. The real freeze completed and its separately reconstructed runtime
was byte-equal to the normal frozen projection. Results:

- 224/224 Priority 8 patterns derived `approved`;
- 224/224 examples were audio-enabled in memory only;
- 224/224 activity allowlists remained empty;
- 224/224 new histories held five events;
- 224 Priority 8 patterns were admitted by frozen policy;
- 765 total allocations were derived and tombstones remained zero.

The canonical JSON SHA-256 of the in-memory frozen document was
`64a4637d6d509af161466037f3acf3a63b61c2c28d1f79276f29c0878d60c173`.

The real participation patterns preserved `requiredLexicalItems: ["udział"]`
through editorial data, frozen structure, and reconstructed runtime:

- `vp-p-brac-fixed-participation-w-locative-participation-target-e33132012e5e`
- `vp-p-wziac-fixed-participation-w-locative-participation-target-45b686043181`

No governance data or frozen output was persisted by the rehearsal.

## 6. Test and immutability results

Before the correction, `python3 validate_priority8_staging.py` and the sixteen
governed Priority 8 suites passed at 483 tests. The dedicated regression suite
runs five tests and passes.

The broader historical `tests.test_priority7_phase2a` fixture suite remains
pre-existing red (83 run, 25 failures, 30 errors): its format-1 synthetic
records fail the established format-2 contract and its deployment guard reports
an incomplete historical release bundle. It is outside this correction and was
not changed.

The editorial corpus, authoring context, review manifest/preview, canonical
candidates, stable-ID map, candidate-key freeze, staging artifact, production
runtime, loader, validator, application shell, service worker, audio manifest,
migration tooling, and activity code remain untouched.

## 7. Phase 4C4C retry gate

The parity defect is fixed, the strict parity gate remains intact, and the
five-event in-memory freeze no longer encounters the former blocker. Subject to
the post-commit governed-suite rerun, Phase 4C4C is ready to retry.

## 8. Independent next blocker

The post-fix sixteen-suite run reached 483 tests with three expected failures
from historical Phase 4C3/4C4A locks rather than from the parity correction:

- Phase 4C3's protected-input SHA lock still requires the old
  `priority7_tooling.py` SHA-256.
- Phase 4C3's dirty-worktree path guard rejects this phase's three authorized
  paths until they are committed.
- Phase 4C4A's runtime-isolation test still forbids any tooling source change.

The dirty-worktree assertion clears after committing. The two tooling hash/path
locks require their own deliberately scoped historical-test correction, which
would exceed this task's exact three-path authorization. The parity correction
is independently correct, complete, and useful, so it is committed without
altering those historical locks. Phase 4C4C remains blocked until the separate
lock-scope decision is completed and the governed suite is green again.
