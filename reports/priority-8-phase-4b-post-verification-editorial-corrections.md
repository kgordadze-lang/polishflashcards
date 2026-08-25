# Priority 8 Phase 4B post-verification editorial corrections

## Purpose and freeze timing

The candidate-key freeze was intentionally delayed because the final independent Opus verification approved the candidate keys but identified three residual stale inline example/gloss strings in `learnerExplanationEn`. The corrections below were applied before the freeze checkpoint so the approved semantic inventory can be frozen together with internally consistent learner-facing prose.

These corrections do not change semantic identity and therefore do not reopen candidate-key adjudication.

## Opus findings and exact corrections

### S-1 — `uczyć`

- Verification order: 70
- Meaning key: `teaching-instruction`
- Pattern key: `accusative-person-o-locative-taught-topic`
- Old snippet: `nauczycielka uczy dzieci o zwyczajach w innych krajach (the teacher teaches the children about customs in other countries)`
- New snippet: `nauczycielka uczy uczniów o polskich zwyczajach (the teacher teaches the pupils about Polish customs)`
- Old field: `To name a topic you teach about rather than a subject to be mastered, use o + Locative with an Accusative person: nauczycielka uczy dzieci o zwyczajach w innych krajach (the teacher teaches the children about customs in other countries).`
- New field: `To name a topic you teach about rather than a subject to be mastered, use o + Locative with an Accusative person: nauczycielka uczy uczniów o polskich zwyczajach (the teacher teaches the pupils about Polish customs).`

### S-2 — `wymagać`

- Verification order: 25
- Meaning key: `person-requires-behavior`
- Pattern key: `genitive-required-content`
- Old snippet: `wymaga lojalności od pracowników (it requires loyalty from employees)`
- New snippet: `szef wymaga lojalności od pracowników (the boss requires loyalty from employees)`
- Old field: `The required thing takes the Genitive; you can optionally add od + Genitive for the person it's required from: wymaga lojalności od pracowników (it requires loyalty from employees).`
- New field: `The required thing takes the Genitive; you can optionally add od + Genitive for the person it's required from: szef wymaga lojalności od pracowników (the boss requires loyalty from employees).`

### S-3 — `przepraszać`

- Verification order: 67
- Meaning key: `apology`
- Pattern key: `accusative-person-ze-explanation`
- Old snippet: `przepraszam cię, że nie zadzwoniłem (I'm sorry I didn't call you)`
- New snippet: `przepraszam cię, że nie zadzwoniłem (I apologise to you for not calling)`
- Old field: `You can also explain yourself with a że clause, and here the person is optional: przepraszam cię, że nie zadzwoniłem (I'm sorry I didn't call you), or simply przepraszam, że nie zadzwoniłem.`
- New field: `You can also explain yourself with a że clause, and here the person is optional: przepraszam cię, że nie zadzwoniłem (I apologise to you for not calling), or simply przepraszam, że nie zadzwoniłem.`

## Mechanical scope proof

A recursive comparison of the committed `HEAD` staging JSON with the corrected working result found exactly three changed leaves under `candidateContent`. All three leaves are `learnerExplanationEn`, at verification orders 25, 67, and 70. There are zero unauthorized `candidateContent` changes and zero changes to Polish or English primary examples.

The complete candidate-key inventory is byte-semantically identical before and after correction:

| Key kind | Count |
|---|---:|
| Meaning | 95 |
| Pattern | 224 |
| Example | 224 |
| Total | 543 |

All `candidateOrigin` fields are byte-identical. All 224 pattern structures, including `relationType`, complements, roles, requiredness, and `clauseKind`, are byte-identical. The guard registry is byte-identical at `registryVersion = 2` with 74 rules.

## Final counts and lifecycle

| Measure | Final value |
|---|---:|
| Authored lemmas | 68 |
| Meanings | 95 |
| Patterns | 224 |
| Examples | 224 |
| Future-empty | 0 |
| Active-production | 222 |
| Recognition-only | 2 |

The recognition-only pair remains `pozwalać / zeby-enabling` and `wymagać / zeby-clause`. The envelope remains `phaseStep = 4B7` and `stagingRevision = 8`.

## Historical digest recomputation

All B1–B7 digests were recomputed with their existing historical projections.

| Batch | Before | After | Result |
|---|---|---|---|
| B1 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` | same | unchanged |
| B2 | `87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82` | same | unchanged |
| B3 | `313b50ec3fe5a2764c4f477c0f47ceef7733cadade7c7b183350f335bcff7197` | `6f69b92ac24cda947aee18b06fe8090f36a70c64fec8db6650abcc8d024a8601` | changed as predicted |
| B4 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` | same | unchanged |
| B5 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` | same | unchanged |
| B6 | `ec9148072c58879334e1eeeae1b20f62259ceecf56ea18500f0d0fb4666e610a` | same | unchanged |
| B7 | `a2d34c616d416f6a36f2346a2c4190522f1102087b3745ab0605be29c5430d9e` | `910b83b8c63f3bac49648623e52f861ea31d20e427daef6d200977486be35f93` | changed as predicted |

Only the B3 and B7 historical digest constants were updated. No invariant was weakened; the B1, B2, B4, B5, and B6 locks were not modified.

## Verification and freeze readiness

- `python3 validate_priority8_staging.py`: PASS
- Targeted B3 and B7 suites: 45 tests, PASS
- Exact eleven Phase 4B suites together: 274 tests, PASS
- Candidate keys: unchanged and ready to freeze
- Stable IDs: not allocated
- Phase 4C/runtime/canonical/audio/product work: not started or modified

The staging artifact is ready for the candidate-key freeze checkpoint.
