# Priority 8 Phase 4B1A - Candidate Authoring Schema Lock

## Status and boundary

Phase 4B1A locks and tests the private, ID-less candidate hierarchy that the
seven Phase 4B authoring batches will use. It authors no Polish linguistic
content and does not begin Batch 1.

The live `editorial/priority-8-phase4-staging.json` remains the approved Phase
4B0 artifact: `phaseStep: 4B0`, `stagingRevision: 1`, 68 draft lemmas, and zero
candidate meanings, patterns, examples, keys, or production IDs. Its SHA-256 at
the starting HEAD and after this work is
`bb98e88767a390892bf2ddc68a097b0dbea714e3b81d93674f7d477a297f32f7`.

## Canonical sources inspected

The field selection was derived read-only from:

- `editorial/verb-pattern-candidates.json`, the actual canonical editorial
  corpus;
- `priority7_tooling.py`, especially `_validate_hierarchy`,
  `_validate_pattern`, `_validate_example`, `_validate_complement`,
  `_validate_cefr`, and `_validate_usage`;
- `editorial/priority-7-authoring-context.json`, for the separation between
  content and registries/governance identities;
- `pp-verb-patterns.js`, for the projected public shape and the matching
  complement/value contract;
- `reports/priority-7-stable-id-specification.md`, for parent-scoped key and ID
  seeds.

The canonical meaning shape requires exactly `id`, `key`, `glossesEn`,
`internalScope`, and nested `patterns`.

The canonical pattern shape requires `id`, `key`, `relationType`,
`complements`, `cefr`, `teachingStatus`, `usage`, `learnerExplanationEn`,
`activityEligibility`, `evidence`, `reviewState`, and `reviewEvents`. It may
also carry `aspectEquivalentPatternIds`, nested `examples`, `contentRefs`,
`errorNotes`, and `releaseMode`.

The canonical example shape requires exactly `id`, `key`, `pl`, `en`, `origin`,
and `audioEligible`.

## Locked ID-less candidate shapes

The per-lemma container remains normalized:

```json
{
  "candidateContent": {
    "meanings": [],
    "patterns": [],
    "examples": []
  }
}
```

Candidate meaning fields are exactly:

```text
candidateMeaningKey
glossesEn
internalScope
```

The containing staging lemma is the meaning owner, so no lemma ID or lemma-key
reference is stored.

Candidate pattern fields are exactly:

```text
candidatePatternKey
meaningKeyRef
relationType
complements
cefr
teachingStatus
usage
learnerExplanationEn
```

`meaningKeyRef` must resolve to one `candidateMeaningKey` in the same staging
lemma. Every candidate meaning must own at least one pattern, matching the
canonical mechanically enforced non-empty pattern cardinality.

Candidate example fields are exactly:

```text
candidateExampleKey
meaningKeyRef
patternKeyRef
pl
en
candidateOrigin
```

`patternKeyRef` resolves together with the transitive `meaningKeyRef` to one
candidate pattern in the same staging lemma. The additional meaning reference
is the minimum disambiguator required by the locked rule that the same
`candidatePatternKey` may occur under different meanings. Without it, a flat
example record could not identify its owner when such reuse occurs.

Every candidate example also preserves its provenance claim at authoring time.
`candidateOrigin` is required and has exactly one of these private shapes:

```json
{"kind": "editorial-generated"}
```

or:

```json
{
  "kind": "repository-reuse",
  "repositorySource": {
    "kind": "card",
    "id": "repository-content-id",
    "field": "pl"
  }
}
```

For `card`, the source field is `pl` or `ex`; for `drill`, it is `prompt` or
`answer`. The source object contains exactly `kind`, `id`, and `field`, and its
ID is a non-empty trimmed repository content ID. `editorial-generated` carries
no repository source and makes no human-authorship claim. `original` is not an
authorized candidate origin.

This private claim is deliberately not canonical example `origin`. No
`generatorRef`, `adoptedAt`, `authorRef`, reviewer, or actor identity exists in
Phase 4B candidate provenance. Batch review must independently check every
repository-reuse claim against the named repository source. Phase 4C remains
responsible for constructing canonical `origin` and satisfying the existing
byte-exact repository-reuse rules. Provenance must never be reconstructed later
from sentence wording.

## Canonical fields deliberately excluded

- Production `id` fields are prohibited; no `vp-l-`, `vp-m-`, `vp-p-`,
  `vp-e-`, or `vp-x-` value is legal anywhere in staging.
- Canonical `key` is replaced by the three explicit candidate-key names.
- Nested canonical `patterns` and `examples` are replaced by the normalized
  per-lemma arrays and explicit ownership references.
- `reviewState`, `reviewEvents`, `releaseMode`, reviewer/actor references, and
  registries are canonical governance fields and are excluded. Canonical
  example `origin` is also excluded, but its truthful source classification is
  preserved immediately in required private `candidateOrigin`. Private
  lemma-level `stagingReviewStatus` remains a separate vocabulary and may
  truthfully remain `draft` before independent review.
- Canonical pattern `evidence` is not duplicated into each ID-less candidate.
  The staging lemma already pins the frozen Phase 3 evidence row and exact
  source locator. Phase 4C must construct and review canonical evidence records
  when promotion becomes authorized.
- `activityEligibility`, `contentRefs`, and example `audioEligible` are
  integration, activity, and audio-policy decisions, not Phase 4B linguistic
  authoring fields.
- `aspectEquivalentPatternIds` requires production pattern IDs and is therefore
  impossible in Phase 4B.
- Optional `errorNotes` are not required to construct the minimum authored
  record and are outside this locked candidate shape.

No parallel linguistic concepts were added.

## Legal structural values

Candidate validation preserves the canonical relation types, roles, direct and
prepositional case sets, CEFR values, teaching statuses, usage priorities, and
registers from `priority7_tooling.py`.

The complement types remain exactly:

```text
case
preposition-case
infinitive
clause
```

`DOKĄD`, `SKĄD`, and `GDZIE` are not complement types. The private staging
clause kinds are the four current canonical values (`ze`, `czy`, `zeby`, and
`interrogative`) plus the Phase 4B-only value `direct-speech`.

Direct speech is represented only as:

```json
{
  "type": "clause",
  "clauseKind": "direct-speech"
}
```

The test suite accepts this shape in private staging. Canonical Python and
JavaScript support remains deferred to Phase 4C.

## Ownership and sibling-key scope

- `candidateMeaningKey` is unique within one lemma. The same value is allowed
  in another lemma.
- `candidatePatternKey` is unique within `(lemma, meaningKeyRef)`. The same
  value is allowed under another meaning or in another lemma.
- `candidateExampleKey` is unique within
  `(lemma, meaningKeyRef, patternKeyRef)`. The same value is allowed under a
  different pattern or in another lemma.
- Every candidate key matches `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Ownership resolution is performed inside one lemma only. A key present only
  in another lemma cannot satisfy a reference.
- Verification order, batch number, and array position are not key or identity
  inputs. No numeric sequential key is generated or required.

The fixture suite proves that cross-lemma duplicate meaning keys validate,
while same-owner duplicates and cross-lemma ownership attempts fail.

## Canonical cardinality found

The current canonical corpus contains 30 lemmas, 34 meanings, 45 patterns, and
45 examples. Each of its 45 patterns currently has one example. That observed
corpus regularity is not a schema invariant: `_validate_pattern` makes
`examples` optional and requires a non-empty example set only when a pattern is
eligible for Listening or active grammar activities.

Phase 4B therefore requires at least one meaning per completed-batch lemma, at
least one pattern per meaning, and resolved ownership for every present
example. It does not require exactly one example per pattern. A focused fixture
with zero examples validates.

## Frozen seven-batch map

| Batch | Orders | Count | First lemma | Last lemma |
|---:|---|---:|---|---|
| 1 | 1-10 | 10 | `pracować` | `przyjść` |
| 2 | 11-16, 18-21 | 10 | `przyjechać` | `zapominać` |
| 3 | 22-31 | 10 | `próbować` | `kupić` |
| 4 | 32-36, 38-41 | 9 | `dawać` | `spotkać się` |
| 5 | 42-51 | 10 | `oglądać` | `powiedzieć` |
| 6 | 52-61 | 10 | `gotować` | `móc` |
| 7 | 62-70 | 9 | `musieć` | `uczyć` |

The frozen sizes are `10 / 10 / 10 / 9 / 10 / 10 / 9`. Flattening the constant
equals the live staging file's ordered 68 `(verificationOrder,
canonicalLemma)` pairs exactly once. Orders 17 (`zaczynać`) and 37
(`przeczytać`) occur in no batch and remain metadata-only identities.

## Phase progression

The private progression is exact:

| phaseStep | stagingRevision | Completed batches |
|---|---:|---:|
| `4B0` | 1 | 0 |
| `4B1` | 2 | 1 |
| `4B2` | 3 | 2 |
| `4B3` | 4 | 3 |
| `4B4` | 5 | 4 |
| `4B5` | 6 | 5 |
| `4B6` | 7 | 6 |
| `4B7` | 8 | 7 |

For an authored step, every lemma in a completed batch must have at least one
candidate meaning and pattern; every future-batch lemma must keep all three
candidate arrays empty. The exact 68 membership/order, 21 per-lemma
constraints, 12 global constraints, two metadata-only relationships,
`udział` guards, private review vocabulary, source identities, recursive ID
prohibition, and read-only behavior remain enforced.

## Confirmation

Only in-memory fixtures contain candidate records in Phase 4B1A. The live
staging artifact remains byte-identical to the starting HEAD. No Polish
linguistic content was authored, no production ID was allocated, and no
canonical/runtime generator is imported or called.

The validator CLI success label is derived from the validated document's
actual `phaseStep` and `stagingRevision`; the unchanged live artifact therefore
reports `4B0` and revision 1, while a valid future `4B1` fixture reports revision
2.
