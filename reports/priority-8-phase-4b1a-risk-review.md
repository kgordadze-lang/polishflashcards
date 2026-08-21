# Priority 8 Phase 4B1A - Risk Review

## Overall assessment

Phase 4B1A is safe for independent review as an ID-less private-schema lock.
It changes validator/test/report machinery only. Batch 1 has not begun, and the
live Phase 4B0 staging artifact remains byte-identical.

## 1. False global key uniqueness

Risk: A validator could reject a legitimate textual key merely because an
unrelated owner already uses it, contradicting the parent-scoped stable-ID
model.

Control: Meaning keys are scoped to a lemma, pattern keys to a meaning within a
lemma, and example keys to a pattern owner within a lemma. Positive tests reuse
the same meaning key across lemmas, pattern key across meanings, and example key
across patterns.

## 2. Dangling ownership

Risk: A normalized pattern or example could refer to no candidate parent and
later be canonicalized under an invented owner.

Control: `meaningKeyRef` and `patternKeyRef` resolve fail-closed within the
containing lemma. Dedicated dangling-reference mutations fail.

## 3. Ambiguous and cross-lemma references

Risk: A flat example `patternKeyRef` is ambiguous when the same pattern key is
legitimately reused under two meanings, or a reference could accidentally bind
to a similarly named parent in another lemma.

Control: Examples carry the minimum transitive `meaningKeyRef` alongside
`patternKeyRef`; the pair resolves one pattern. All indexes are rebuilt per
lemma, so no other lemma can satisfy a reference. Tests cover repeated pattern
keys with resolved examples and an attempted cross-lemma bind.

## 4. Staging drifts from canonical semantics

Risk: A private format could invent complement concepts or silently accept
values the canonical authoring model cannot represent.

Control: Candidate validators copy the canonical relation, complement, case,
role, CEFR, teaching-status, priority, register, and conditional-field rules
from the inspected Priority 7 tooling. Candidate shapes retain canonical field
names when semantics match and document every omission. No fifth complement
type or generalized-role pseudo-type is accepted.

## 5. Direct-speech staging/canonical mismatch before Phase 4C

Risk: `direct-speech` is approved for private authoring but is not yet legal in
the canonical Python or JavaScript clause-kind sets.

Control: It remains a `clause` subtype only, is accepted only by this private
staging validator, and is not projected or promoted. Phase 4C must add and test
canonical Python/JavaScript parity before promotion.

## 6. Accidental governance leakage

Risk: Canonical `reviewState`, events, reviewer/actor identities, release mode,
registries, or provenance actors could falsely claim review in a draft record.

Control: Candidate shapes are closed and a recursive candidate-only check
rejects governance and identity fields even if nested. The existing private
lemma-level `stagingReviewStatus` is separate; authored fixtures remain
`draft`. No independent-review event is invented.

## 7. Premature production IDs

Risk: Candidate keys could be mistaken for allocated stable identities, or an
ID field/value could leak into staging.

Control: Candidate fields contain no `id`. Recursive checks reject production
ID field names and all five `vp-*` families. Tests cover each family and an ID
field mutation. The validator calls neither `freeze_editorial` nor
`verified_runtime_from_frozen` and generates nothing.

## 8. Batch membership drift

Risk: Future authoring could skip, repeat, reorder, or prematurely populate a
lemma, or restore orders 17/37 as full records.

Control: One frozen constant contains the exact seven batches. Its size vector
is `10/10/10/9/10/10/9`; its flattened sequence must equal the frozen ordered
68 exactly; orders 17 and 37 are forbidden. Phase/revision mapping determines
which batches must be populated and which must remain empty. Both boundary
failures have tests.

## 9. False independent-review status

Risk: A coding-model authoring commit could claim independent review before it
occurs.

Control: The validator accepts truthful private `draft` status for authored
records and never requires `independently-reviewed` merely because a batch is
complete. Independent review remains a post-commit human workflow gate.

## 10. Example cardinality strengthened without authority

Risk: Treating the current corpus's one-example-per-pattern observation as a
schema law could reject otherwise canonical authoring.

Control: The canonical validator was inspected directly. Examples are optional
unless certain activities are enabled. Phase 4B fixtures therefore require all
present references to resolve but permit zero examples; a positive test proves
that behavior.

## Residual risk and gate

The remaining risk is substantive Batch 1 authoring and review quality. This
commit must receive independent review before any live candidate content is
added. Canonical direct-speech support, governance construction, key freeze,
ID allocation, promotion, runtime projection, audio, and activities remain
outside Phase 4B1A.
