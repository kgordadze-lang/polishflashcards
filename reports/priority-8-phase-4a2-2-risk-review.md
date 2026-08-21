# Priority 8 Phase 4A2-2 - Risk Review

## 1. Public/private aspect split

Risk:
A private metadata-only partner may later be mistaken for syntax-bearing or public runtime data.

Control:
The two relationships are staging/governance metadata only, carry no IDs or syntax, and do not enter current `aspectPartnerIds`.

## 2. Direct speech authored before canonical enum implementation

Risk:
Phase 4B can author direct-speech candidates even though the current canonical schema cannot yet accept them.

Control:
Phase 4B is staging-only. Canonical promotion is blocked until Phase 4C implements and validates `clauseKind: direct-speech`.

## 3. Premature stable IDs

Risk:
Draft keys or imperfect editorial boundaries could become frozen production identities.

Control:
No `vp-*` ID is permitted anywhere in Phase 4B staging. Keys freeze only after explicit human staging approval.

## 4. Circular approval language

Risk:
Calling an ID-less staging record canonically "approved" could falsely imply it passed the existing ID-based product-governance chain.

Control:
Use private staging statuses. Human staging approval freezes editorial content for canonicalization but does not equal release/product approval.

## 5. Constraint loss

Risk:
The 21 narrowing constraints could disappear when Phase 3 evidence is converted into learner-facing content.

Control:
Carry exact constraint text/source in staging and require explicit batch/final review.

## 6. Fixed-expression loss

Risk:
`brać/wziąć udział w + Locative` could become generic object syntax.

Control:
Private staging `requiredLexicalItems: ["udział"]` plus explicit QA.

## 7. Over-engineering schema

Risk:
Priority 8 could add canonical fields merely to encode one-off editorial controls.

Control:
Keep metadata-only aspect relationships, required lexical items and authoring constraints private unless a future product requirement independently justifies canonical/runtime representation.

## 8. Staging file becomes an alternate runtime source

Risk:
A convenient staging format could bypass the official approval-gated generator.

Control:
The staging file must never be consumed by `freeze_editorial` or `verified_runtime_from_frozen`. Canonical promotion remains mandatory before runtime projection.

## 9. Version bumps happen too early

Risk:
`formatVersion` or `patternDataRevision` changes could leak into unfinished authoring work.

Control:
Both remain unchanged through Phase 4B. Schema/version implementation occurs later.

## 10. Batch drift

Risk:
Seven batches could gradually expand beyond the frozen 68 or restore rejected Phase 2 hypotheses.

Control:
The staging validator and every independent batch review compare against the frozen Phase 3B intake and constraints.

## 11. Canonical promotion too early

Risk:
Promoting individual batches would mix incomplete Priority 8 content with the released canonical corpus and complicate cross-batch corrections.

Control:
No canonical promotion until all 68 pass Phase 4C reconciliation.

## Final assessment

With these controls, Phase 4B may begin after Phase 4A2-2 is independently verified and integrated.

The principal remaining implementation risk is Phase 4C, where direct-speech schema support, stable-ID allocation and canonical promotion converge. That work must receive its own gated implementation and review plan.
