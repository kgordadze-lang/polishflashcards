# Priority 8 Phase 0 — audio governance impact

## Current contract

The released private record places both `audioEligible` and `activityEligibility` inside the editorial/native scope and, transitively, product-approval scope. The reference-verification scope does not contain either field. Current tooling also raises `AUDIO_NOT_AUTHORIZED` when `audioEligible:true` is not owned by an approved pattern with `listening` eligibility. That rule reflected Priority 7’s lack of a reference-pronunciation consumer; it must not be bypassed.

## Required product-policy decision

Before editing any flag, the owner must approve a revised one-way invariant:

- `audioEligible` authorizes pronunciation of the exact approved example;
- Listening eligibility remains an independent explicit pattern allowlist;
- a Listening item requires approved audio, but approved audio does not create a Listening item.

This keeps one runtime field and the one audio architecture. Adding a second ambiguous audio flag would increase schema and consumer drift. The semantics change must be written into the governance specification, Python editorial/frozen validators, runtime tests and release checklist before any corpus mutation.

## Change impact by field

| Change | Reference verification | Editorial re-review | Product approval | New stable ID | Runtime revision | Frozen baseline |
|---|---:|---:|---:|---:|---:|---:|
| `audioEligible: false → true`, exact text unchanged | retain existing current event | required (audio suitability/current scope digest changes) | required | no | yes | yes |
| add `listening` to `activityEligibility` | retain if structural/evidence claims unchanged | required (eligibility/current scope digest changes) | required | no | yes | yes |
| change example Polish/English | existing reference evidence may remain only if its pinned claim still resolves; otherwise rerun | required | required | normally no if identity key/ownership unchanged | yes | yes |
| change relation/complements/meaning ownership | rerun from research/reference | required | required | often yes; released relation type requires replacement/tombstone | yes | yes |

A flag is policy/wording scope, not structural identity. It never justifies changing `vp-e` or `vp-p` IDs. Stable IDs remain frozen; retired IDs are tombstoned and never recycled.

## Minimum valid chain for the current 45

1. **Research (retained):** the existing approved sentence, origin and pattern analysis remain unchanged.
2. **Reference verification (retained):** existing current reference-verification events/digests remain valid because audio/activity flags are not tier-1 fields.
3. **Policy authorization:** human owner approves the new pronunciation-without-Listening invariant and the exact Phase 1 set.
4. **Audio/editorial preparation:** set `audioEligible:true` only on the approved 45, calculate 20 exact reuses/25 new, generate only after the text/flag freeze, and perform human pronunciation/audio QA.
5. **Editorial re-review:** append current-digest `editorial-review:accept` events covering exact text, translation, origin, audio eligibility and QA disposition. AI agreement is not linguistic or audio approval.
6. **Product approval:** the human owner visually/audibly reviews the control and corpus treatment and appends `product-approval:accept` against the current product digest.
7. **Approval-gated freeze/projection:** advance the frozen baseline and `patternDataRevision`, project the public runtime through the official path, verify exact parity and publish only in a later authorized phase.

If the tooling requires an explicit reopen/correction event before changed tier-2 scope, use its existing event vocabulary; do not manufacture a fresh reference-verification event when the tier-1 digest did not move.

## Listening chain

Adding Listening repeats editorial and product approval with activity suitability, item context, distractors, answer closure, CEFR/status, sampler and feedback all in scope. An example and a clip are necessary but not sufficient. Recognition-only may participate only in genuinely receptive, deterministic items; it remains barred from productive activities.

## Revision and migration

Any public flag change changes runtime bytes and therefore should advance the pattern data revision. It does not alter learner persistence and requires neither `SCHEMA_VERSION` nor `CONTENT_MIGRATION_REVISION`. It does move the independent frozen Verb Patterns policy baseline.
