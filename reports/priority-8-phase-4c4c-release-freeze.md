# Priority 8 Phase 4C4C — approved release-governance freeze

Phase 4C4C persists the product owner's approval of the exact 224-pattern
Priority 8 review set, refreshes the nonhuman editorial tier over the authorized
audio-enabled scope, and derives release authority through the repository's
existing freeze machinery. It does not project, deploy, or integrate production
content.

## 1. Starting endpoint

The work began on `priority-8-phase-4c-architecture` at
`292a963c5f6f67b08392edb97b395ce05cb74297`, tree
`36d4711ef441486c8eaa7250414a1259df32bff4`, parent
`e4dba274be989093b25a9367aea9ab6a9c29cbdb`, subject `Priority 8 Phase
4C4C2 scope historical tooling locks`. The worktree was clean, remotes were
absent, `push.default` was `nothing`, and the fail-closed pre-push hook was
executable.

The staging validator passed. The sixteen governed Priority 8 suites passed
483/483 and the Phase 4C4C1 parity suite passed 5/5 before persistence.

## 2. Human approval authority

The explicit product-owner decision was: approve all 224 Priority 8 verb-pattern
patterns bound by the Phase 4C4A review manifest. The existing human reviewer
`product-owner-001` has `human: true`, the `product-approval` role, and the
required acknowledgement of `solo-maintainer-reference-backed`.

The approval records only the product-release decision. It does not claim
row-by-row inspection, human source verification, human editorial or linguistic
review, listening QA, audio-quality approval, activity approval, or production
projection.

## 3. Immutable review receipt

`editorial/priority-8-phase4c4a-review-manifest.json` remains the immutable
pre-approval review receipt. Its SHA-256 remains
`f9776493385c06aa8eef212f6168072d931bc82c72cf086d872c977090127eee`.
No receipt state or review row was rewritten.

## 4. Exact review set

The following sets are exactly equal at 224 pattern IDs:

- review-manifest pattern IDs;
- review-preview pattern IDs;
- live editorial Priority 8 pattern IDs;
- stable-map `vp-p` IDs.

There are no missing or extra rows.

## 5. Five-event transition

Every Priority 8 pattern now has exactly five append-only review events:

1. existing nonhuman `reference-verification / accept`;
2. existing nonhuman `editorial-review / accept`;
3. nonhuman `editorial-review / changes-requested`;
4. fresh corroborated nonhuman `editorial-review / accept`;
5. human `product-approval / accept`.

The first two events are byte-identical to the Phase 4C4A input history.

## 6. Event 3 rationale

Event 3 records only the governed scope transition caused by changing
`audioEligible` from false to true. Its note states that no learner-facing
semantic content changed. It does not allege a linguistic defect or correction.

## 7. Audio eligibility transition

Exactly 224 Priority 8 examples changed `audioEligible: false` to `true`.
Example IDs and Polish and English sentences are unchanged. This is
pronunciation-playback eligibility only; it creates no Listening eligibility and
generates no audio.

## 8. Refreshed editorial acceptance

Event 4 is a new `editorial-review / accept` recorded after the audio flag is
present. Each event carries the freshly recomputed tier-2 scope digest for its
final audio-enabled pattern. Replaying the first four events derives
`editorial-reviewed` before product approval.

## 9. Independent corroboration

Event 4 uses `priority8-editorial-review` and the distinct corroborator
`priority8-editorial-corroboration`. Both are registered nonhuman editorial
actors. Self-corroboration and cross-tier actor reuse remain rejected.

## 10. Human product approvals

Exactly 224 Event 5 records use `reviewerRef: product-owner-001`, no `actorRef`,
and grounded date `2026-08-26`. Every acceptance binds to the exact final
product-approval scope digest.

## 11. Derived approved state

Repository review-state replay derives `approved` for 224/224 Priority 8
patterns. `reviewState` is never accepted independently of the current history.

## 12. Semantic immutability

Comparison with the Phase 4C3 canonical candidates found zero semantic drift in
the 68 lemmas, 95 meanings, 224 patterns, and 224 examples. The only authorized
content-level change is the 224 audio flags. Stable IDs, candidate keys,
structure, wording, policy, examples, teaching data, seven source complements,
six genuine family targets, eleven direct-speech patterns, and both
`requiredLexicalItems: ["udział"]` patterns are preserved.

## 13. Editorial validation

The real unmodified `validate_editorial` reports zero issues both for the
in-memory rehearsal and the persisted state.

## 14. Activity boundary

All 224 Priority 8 `activityEligibility` arrays remain empty. There is zero
Listening, Type It, mixed-quiz, or other activity authorization.

## 15. Freeze result

The existing `freeze_editorial` machinery reconstructs the released revision-2
baseline, derives the approved Priority 8 transition in memory, and validates the
complete frozen document with zero issues. No parallel allocator, freeze
algorithm, or persisted production projection was created.

## 16. Frozen digests

Canonical SHA-256 digests are:

- complete frozen document:
  `86b48556b9bb81fc5beb327d356015bb7a7359e01a651db54a9448a9da71f589`;
- identity:
  `78cd20154b6dd43dd9f54602ecf4f17ba9b94815c8b7f132757e7c964105fbab`;
- structure:
  `21e948bdf02cf5f72280e74eef23f87d6772c586b20d7fc38bdf93a61476a2e6`;
- wording:
  `3f25d13d0885d0fd3b543cd7e0b08849bb8e5bd86fb69d9229b5c53fe313b37f`;
- policy:
  `3a32a08ca9dc8b7d1a4f97f5d197685e37af788733075a083d111bfd6b4491f5`.

Repeated independent builds are byte-identical.

## 17. Required lexical-item parity

Both participation patterns retain `requiredLexicalItems: ["udział"]` through
editorial data, frozen structure, primary runtime projection, and independent
frozen-runtime reconstruction. The primary and reconstructed runtime documents
are exactly equal.

## 18. Allocation registry

Existing freeze machinery derives and the private context persists:

- 154 existing released allocations;
- 611 new Priority 8 allocations: 68 lemma, 95 meaning, 224 pattern, and 224
  example IDs;
- 765 total allocation/identity records.

There are zero collisions, duplicate IDs, replacement IDs, metadata-only
allocations, or `vp-x` allocations.

## 19. Tombstones

No identity was retired. Tombstones remain empty.

## 20. Release authorization

`freeze_editorial` derives release authorization rather than reading a
hand-authored record. It reports release mode
`solo-maintainer-reference-backed`, empty human-verification and
human-native-review coverage arrays, and admits exactly 224 Priority 8 patterns.
Recognition-only patterns remain admissible without an invented activity gate.

## 21. Authority truthfulness

The retained chain truthfully distinguishes nonhuman reference verification,
nonhuman editorial review, and human product approval. It claims no human
reference verification, human editorial review, human linguistic review,
listening QA, audio-quality approval, Listening approval, or activity approval.

## 22. Metadata-only boundary

`zaczynać` and `przeczytać` remain metadata-only. They receive no canonical
entities, stable IDs, allocations, product approvals, or release admission.

## 23. Deferrals

All ten Phase 4C3 architecture deferrals remain registered and none was promoted
during freeze.

## 24. Private-input immutability

The review receipt, review preview, canonical candidates, stable-ID map,
candidate-key freeze, and staging artifact remain byte-identical. In particular:

- canonical candidates SHA-256:
  `c54e611da32ad61c4c020545594ec1f33c0bcea6937f31c9e7a31d29bc5fa7e9`;
- stable map SHA-256:
  `20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d`.

## 25. Production isolation

Production remains 30 lemmas, 34 meanings, 45 patterns, and 45 examples at
`formatVersion: 2` and `patternDataRevision: 2`. `priority7_tooling.py`, the
runtime corpus and loader, staging validator, application shell, service worker,
audio, audio manifest, migrations, and activity code are unchanged. No runtime
projection, push, deployment, or integration occurred.

## 26. Historical-test compatibility corrections

The first persisted run exposed four historical assertions that treated earlier
snapshots as permanent live requirements. Finalization scopes exactly those four:

1. the Phase 4C2 released-runtime projection now reads the exact Phase 4C2-owned
   local Git snapshot rather than the later live editorial population;
2. the Phase 4C4A scope-digest assertion checks its exact two-event,
   audio-disabled snapshot, allowing the original acceptance to remain valid
   history after a legitimate changes-requested transition;
3. the Phase 4C4A renamed-key adversarial check uses its historical empty
   allocation registry;
4. the Phase 4C4A metadata-only-promotion adversarial check uses the same
   historical pre-freeze corpus and context.

Each historical assertion remains exact and includes or retains mutation proof.
Current Event 4/Event 5 scope currency and current allocation corruption remain
covered by the unchanged Phase 4C4C suite. The Phase 4C3 dirty-worktree guard was
not edited; it is expected to fail before commit and pass after the worktree is
clean.

## 27. Tests

Pre-write gates passed at 483/483 governed tests and 5/5 Phase 4C4C1 parity
tests. The new Phase 4C4C suite passes 78/78, including its adversarial cases.

After historical scoping, the pre-commit governed run is exactly 482/483: the
sole failure is the untouched Phase 4C3 dirty-worktree guard. The staging
validator passes, Phase 4C4C1 passes 5/5, Phase 4C4C passes 78/78,
`validate_editorial` reports zero issues, and deterministic verify-only mode
reports that persisted state is current with no writes.

The clean post-commit gate must return the governed suites to 483/483 before
Phase 4C5 begins.

## 28. Phase 4C5 handoff

Phase 4C4C grants and freezes release governance only. Phase 4C5 may begin only
after independent verification of the clean committed endpoint, including
483/483 governed tests, 5/5 parity tests, 78/78 Phase 4C4C tests, immutable
private and production inputs, the 765-allocation universe, zero tombstones,
224 release-admitted patterns, and exact frozen-runtime parity.

**READY FOR INDEPENDENT PHASE 4C4C VERIFICATION BEFORE PHASE 4C5**
