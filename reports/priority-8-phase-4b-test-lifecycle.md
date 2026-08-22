# Priority 8 Phase 4B test lifecycle

## Historical and live responsibilities

Completed-batch regression tests must permanently protect approved batch
content without requiring the live staging artifact to remain at that batch's
authoring step. The separate live-progress test owns the intentionally moving
phase, revision, authored-boundary, future-empty, and draft-state assertions.
This separation prevents later Batch 2-7 authoring from invalidating Batch 1's
historical regression test while still detecting any change to its approved
content.

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

Each future authoring commit updates only the moving live-progress test's
phase, revision, authored-boundary, future-empty, draft-state, and cumulative
total expectations. Historical completed-batch regression tests remain fixed
unless the corresponding approved batch content itself is deliberately
re-adjudicated under a separately authorized change.
