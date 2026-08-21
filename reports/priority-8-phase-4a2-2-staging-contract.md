# Priority 8 Phase 4A2-2 - Phase 4B Staging Contract

## Purpose

Phase 4B authoring occurs outside the canonical released editorial corpus.

The staging artifact is:

`editorial/priority-8-phase4-staging.json`

It is a private authoring/review artifact and must never be treated as public runtime input.

## 1. Envelope requirements

The staging artifact must mechanically identify:

- Priority: 8
- phase: 4B
- frozen full-pattern count: 68
- source Phase 3B freeze
- source Phase 4A2-2 policy freeze
- starting integration baseline
- staging schema/revision owned only by Priority 8 authoring

The staging schema/revision is private authoring metadata and is not `formatVersion`.

## 2. Per-lemma traceability

Each full-pattern draft must carry:

- preserved Phase 3 verification order;
- `canonicalLemma`;
- aspect;
- Phase 3 disposition;
- Phase 3 evidence/source references needed for editorial review;
- exact applicable Phase 3B constraint text;
- candidate editorial meanings;
- candidate patterns;
- candidate examples;
- candidate semantic keys;
- staging review status.

No production `vp-*` ID is permitted.

## 3. Candidate keys

Candidate keys are allowed because later production IDs depend on them.

They are editable while the record is a draft.

They freeze only after explicit human staging approval.

Verification-order numbers must not appear in the key merely to preserve ordering.

## 4. Metadata-only aspect relationship

Only the full-pattern anchors carry the private collapsed-partner metadata:

- `zacząć` may record `zaczynać`;
- `czytać` may record `przeczytać`.

The metadata records lexical identity/aspect only.

They contain:

- no stable ID;
- no patterns;
- no meanings;
- no examples;
- no inherited syntax.

They must not increase the full-pattern count above 68.

## 5. Required lexical material

Where Phase 3B requires fixed lexical material, staging may carry:

```json
"requiredLexicalItems": ["udział"]
```

This is authoring/checklist metadata only.

It must not automatically become a canonical or runtime field.

## 6. Constraint carryover

The 21 compatible-with-narrowing records must carry their applicable constraint text into staging.

Global constraints also remain binding, including:

- generalized selected role versus concrete realization;
- sense-specific schemas;
- no unsupported maximal frames;
- lexical `się` / `sobie`;
- required lexical `udział`;
- independent aspect evidence;
- no syntax inheritance;
- grammar-owned Genitive under ordinary negation;
- exact clause distinctions;
- related lexical identities kept separate;
- rejected Phase 2 hypotheses remain rejected.

## 7. Review statuses

The staging workflow may use private statuses equivalent to:

- `draft`
- `independently-reviewed`
- `human-approved`

These statuses are NOT the canonical governance `reviewState`.

`human-approved` means the exact ID-less staging record is frozen for later canonicalization.

It does not claim product release approval.

## 8. Phase 4B validation expectations

Before any Phase 4B batch is accepted, private staging validation should check at minimum:

- exact allowed 68-lemma set;
- no extra lemma;
- no missing lemma from the authorized portion of the batch;
- no metadata-only identity counted as full-pattern;
- no production `vp-*` ID anywhere in staging;
- candidate-key syntax and sibling uniqueness;
- preserved verification-order traceability;
- required Phase 3B constraints present;
- `udział` protection where applicable;
- metadata-only aspect values exactly limited to the two frozen relationships;
- no canonical editorial/runtime/schema/audio path modified by authoring.

A private staging validator may be created for these checks.

It must not become an alternate public-runtime generator.

## 9. Promotion boundary

No promotion to:

`editorial/verb-pattern-candidates.json`

occurs during Phase 4B.

Promotion occurs only after the complete 68-lemma staging set passes Phase 4C reconciliation and the required canonical architecture is ready.
