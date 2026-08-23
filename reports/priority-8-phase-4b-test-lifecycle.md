# Priority 8 Phase 4B test lifecycle

## Three separate control layers

### Historical content locks

Completed-batch regression tests permanently protect approved batch content
without requiring the live staging artifact to remain at that batch's
authoring step. A historical digest answers “Did approved Batch N content
change?” It does not answer “Was the original interpretation linguistically
correct?” The immutable/future-safe files are:

- `tests/test_priority8_phase4b1_batch01.py`
- `tests/test_priority8_phase4b2_batch02.py`
- `tests/test_priority8_phase4b3_batch03.py`

### Moving progress gate

`tests/test_priority8_phase4b_progress.py` alone owns the intentionally moving
phase step, staging revision, authored boundary, cumulative counts,
future-empty boundary, and draft-state assertions. This separation prevents
later Batch 2-7 authoring from invalidating a historical regression test while
still detecting unauthorized movement in the current authoring envelope.

### Live declarative authoring guards

`tests/test_priority8_phase4b_authoring_guards.py` reads the current live
staging file and interprets the declarative registry at
`tests/fixtures/priority8_phase4b_authoring_rules.json`. It answers “Does the
current staging violate a known semantic-structure or explanation-consistency
invariant?” Rules remain active across later batches and contain no current
phase/revision/count, future-empty boundary, or historical digest assertions.
Structural matchers are independent of a candidate pattern key unless a future
semantic identity genuinely requires such a key.

Independent linguistic review answers a third question: “Did the schema
faithfully represent the evidence and learner need?” Historical locks, live
guards, and independent review are complementary controls; none substitutes
for another.

## Batch 1 regression digest

The approved Batch 1 SHA-256 digest is
`3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e`.

The digest projects orders 1-10 in staging order and includes:

- `verificationOrder`
- `canonicalLemma`
- `aspect`
- `phase3Disposition`
- `phase3Evidence`, including its representation/evidence source fields
- `bindingConstraints`
- `candidateContent`, including every meaning, pattern, complement, learner
  explanation, CEFR value, teaching status, usage value, example, translation,
  candidate key, and provenance field

The projection is serialized as UTF-8 JSON with sorted object keys and compact
stable separators before SHA-256 hashing. `stagingReviewStatus` is excluded
because review status may legitimately advance from `draft` to
`independently-reviewed` or `human-approved` without changing approved
authoring material.

## Assertions moved to the live-progress gate

The Batch 1 historical test no longer pins `phaseStep` to `4B1`,
`stagingRevision` to 2, orders 11-70 to 58 empty full-pattern records, or all
68 review statuses to `draft`. The moving
`tests/test_priority8_phase4b_progress.py` test now owns those assertions, as
well as the current authored totals and the corpus-wide metadata, constraint,
and production-ID boundaries.

No linguistic or editorial content changed. The live staging JSON remains
byte-for-byte unchanged.

## Batch 2-7 maintenance rule

For moving-state assertions, each future authoring commit updates only the
live-progress test's phase, revision, authored-boundary, future-empty,
draft-state, and cumulative-total expectations. Historical completed-batch
regression tests remain fixed unless the corresponding approved batch content
itself is deliberately re-adjudicated under a separately authorized change.
The live rule registry is extended when a new batch activates an
evidence-driven invariant; reusable guard logic changes only when no existing
primitive expresses that invariant.

Presence-asserting rules for a new batch—such as exact required pattern shapes
or required lexical tokens in a selected pattern's learner explanation—are
introduced in the same authoring commit as the candidate content they protect,
after the schema matrix has been derived. They fail by design while the target
meaning/pattern is absent. Absence/prohibition rules may be activated earlier
only when that is semantically appropriate.

## Schema-first authoring rule for Batches 4-7

Before `candidateContent` is edited, the author must derive and verify a compact
pre-authoring matrix from the binding Phase 3/3B evidence. It has one row per
meaning and alternative schema and records:

| lemma | meaning | alternative/schema identity | required complements | optional complements | clause kind | lexical required material | generalized-role realization status | explicit exclusions |
|---|---|---|---|---|---|---|---|---|
| `wymagać` | person requires behavior | A | Genitive content | `od` + Genitive person | — | — | not applicable | no standalone `od` |
| `wymagać` | person requires behavior | B | clause content | `od` + Genitive person | `żeby` | — | not applicable | no standalone `od` |
| `brać` (Batch 4 plan only) | participation | fixed participation | `w` + Locative | — | — | `udział` | exact governed realization | no generic `brać + w` frame |

The matrix is checked against evidence before pattern keys, examples, learner
explanations, or staging content are written. Future batch prompts must require
the model to output and verify it internally or place it in the batch authoring
report before staging authoring. It is a workflow/control-plane artifact, not
a new staging field, and does not alter the locked candidate-content schema.

For Batch 4 participation, the current controls are deliberately split:
lemma-level private `requiredLexicalItems: ["udział"]`; the matrix row above;
an independently authored `w` + Locative complement; an explanation-token
guard; an example preserved by the future historical Batch 4 lock; and
independent linguistic review of the fixed construction. The explanation
guard checks only that `learnerExplanationEn` mentions the token. It cannot
prove that a pattern structurally contains lexical material, interpret a
negated/unrelated mention, or turn `w` + Locative into a lexical-material
field. A genuine pattern-level representation is an open later schema question
for schema implementation/reconciliation, not a Phase 4B change.

After authoring, the historical lock, moving progress gate, applicable live
semantic guards, and independent linguistic review all run. The fuller engine
design and current registry are documented in
`reports/priority-8-phase-4b-authoring-guard-hardening.md`.
