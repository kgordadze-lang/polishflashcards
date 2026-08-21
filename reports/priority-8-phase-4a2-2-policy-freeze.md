# Priority 8 Phase 4A2-2 - Human Architecture and Authoring Policy Freeze

## Status

APPROVED.

The product owner explicitly approved the Phase 4A2-2 decisions on 2026-08-21.

This document converts the Phase 4A2-1 option analysis into the binding policy for subsequent Priority 8 work.

Starting approved integration baseline:

- HEAD: `48da24652fe1d02ad2b158a4e572179ce4059433`
- tree: `8115b839164740041dd108106cef728857882b9b`

This phase is reports-only. It creates no schema, runtime, editorial corpus, stable ID, audio, activity, or learner-facing change.

## 1. Metadata-only aspect identities

The two Phase 3B collapsed identities remain:

- `zaczynać` -> full-pattern anchor `zacząć`
- `przeczytać` -> full-pattern anchor `czytać`

Binding policy:

1. They remain verified lexical identities.
2. They do not count among the 68 Phase 4 full-pattern additions.
3. They must not receive separate full-pattern editorial records.
4. They receive no production `vp-*` IDs in Priority 8.
5. They must not be inserted into current `aspectPartnerIds`.
6. Their relationship is preserved only in private Phase 4 staging/governance metadata.
7. No syntax may transfer through the relationship.
8. No Priority 8 public-runtime or learner-UI field is added solely for these two collapsed identities.
9. If learner-facing aspect navigation or aspect-partner display is desired later, that requires a separate holistic architecture decision rather than a special-case Priority 8 mechanism.

The approved private staging representation may use a structure conceptually equivalent to:

```json
{
  "metadataAspectPartner": {
    "canonicalLemma": "zaczynać",
    "aspect": "imperfective"
  }
}
```

and:

```json
{
  "metadataAspectPartner": {
    "canonicalLemma": "przeczytać",
    "aspect": "perfective"
  }
}
```

These are staging/governance values, not public runtime fields.

## 2. Direct speech

Direct speech remains inside the existing locked complement type:

`clause`

The approved new clause subtype is:

`direct-speech`

The eventual canonical representation is therefore:

```text
type: clause
clauseKind: direct-speech
```

The learner-facing token should be:

`„…”`

The learner-facing label should be:

`Direct speech`

Direct speech must not be represented as a fifth complement type and must not be collapsed into `że`, `żeby`, `czy`, or generic interrogative-dependent clauses.

The eventual implementation must keep Python and JavaScript clause-kind enums/token tables mechanically synchronized and must add a parity test.

No schema or runtime implementation occurs in Phase 4A2-2 or Phase 4B.

## 3. Stable-ID lifecycle

The strict post-approval allocation policy is approved.

During Phase 4B:

- no production lemma IDs;
- no production meaning IDs;
- no production pattern IDs;
- no production example IDs;
- no provisional `vp-*` IDs stored or committed.

Candidate semantic keys may exist in the private staging artifact.

Before production ID allocation:

1. the complete lemma editorial record must be drafted;
2. it must pass independent editorial review;
3. it must receive explicit human staging approval;
4. its semantic keys then freeze;
5. deterministic production IDs are allocated exactly once;
6. only then may the record be promoted into the canonical editorial/governance system.

Formal canonical governance occurs after IDs exist.

Verification order must never become part of a key or stable-ID seed.

Existing tombstone and non-recycling rules remain unchanged.

## 4. Key policy

Meaning, pattern, example and future item keys remain durable semantic/structural identity inputs.

During staging they are candidate keys and may be corrected before human staging approval.

At human staging approval:

- candidate keys freeze;
- subsequent production ID allocation uses those frozen keys;
- no key is renamed merely for readability after allocation.

Verification order is traceability metadata only.

If a meaning or pattern boundary changes before human staging approval, its candidate key may be replaced without retirement because no production identity exists yet.

After production allocation/release, existing replacement/tombstone rules apply.

## 5. Required lexical material

The Phase 3B requirement to preserve lexical `udział` in:

- `brać udział w + Locative`
- `wziąć udział w + Locative`

is binding.

Priority 8 will NOT add a new canonical/runtime `requiredLexicalItems` field solely for this need.

Instead the private Phase 4 staging/checklist representation must explicitly record:

```json
"requiredLexicalItems": ["udział"]
```

for the relevant draft construction(s).

Phase 4B review must fail the draft if `udział` disappears or the construction is reduced to generic object syntax.

## 6. Twenty-one narrowing/representation constraints

All 16 KEEP WITH NARROWING constraints and the 5 additional compatible-with-narrowing constraints remain binding.

They must be carried into the private Phase 4 staging artifact as structured authoring/checklist metadata.

The exact Phase 3B constraint wording and source must remain traceable.

Priority 8 does not attempt to encode general linguistic judgments such as generalized-role discipline, sense boundaries, or maximal-frame prevention as universal runtime schema rules.

These remain editorial/governance constraints checked during batch review.

## 7. Phase 4B authoring source

Phase 4B will use a private staging artifact:

`editorial/priority-8-phase4-staging.json`

This file is not the canonical Priority 7 editorial corpus.

During Phase 4B it must:

- contain no production stable IDs;
- not be consumed by `freeze_editorial`;
- not be consumed by `verified_runtime_from_frozen`;
- not be projected into `content/verb-patterns.json`;
- not change released runtime;
- preserve exact frozen 68-lemma membership;
- preserve Phase 3 verification order for traceability only;
- carry Phase 3B constraints;
- carry private metadata-only aspect relationships;
- carry required lexical-item checks where applicable.

No approved Phase 4B lemma is promoted into `editorial/verb-pattern-candidates.json` during Phase 4B.

## 8. Phase sequencing

The approved sequence is:

Phase 4A2-2
-> policy freeze

Phase 4B
-> staging-only editorial authoring of the frozen 68
-> controlled batches
-> independent review
-> human staging approval
-> no production IDs
-> no canonical promotion
-> no runtime/schema change

Phase 4C
-> full 68-lemma reconciliation
-> implement required canonical architecture changes, including direct-speech support
-> freeze approved semantic keys
-> allocate deterministic production IDs
-> promote approved records into canonical editorial/governance data
-> run canonical governance and validation

Phase 4D
-> official runtime projection
-> release integration and validation
-> no activity activation unless separately authorized

## 9. Version/revision policy

Current values remain unchanged during Phase 4A2-2 and Phase 4B:

- `formatVersion = 1`
- `patternDataRevision = 2`

The approved future release policy is:

- direct-speech legal-shape support moves the Verb Patterns contract to `formatVersion = 2`;
- the completed expansion runtime moves `patternDataRevision` from 2 to 3.

The actual increments occur only when the corresponding implementation/runtime projection is performed.

No APP_VERSION, service-worker generation, shell-cache, schema, or migration value changes are authorized by this freeze alone.

## 10. Binding boundary

This policy supersedes conflicting recommendations in the Phase 4A2-1 option reports.

The Phase 4A2-1 reports remain preserved as analysis history.

No Phase 4B authoring may override these decisions without explicitly reopening Phase 4A2 governance.
