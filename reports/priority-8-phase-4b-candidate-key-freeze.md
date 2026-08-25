# Priority 8 Phase 4B candidate-key freeze

## 1. Starting endpoint

The checkpoint began from the exact approved post-verification endpoint:

| Item | Value |
|---|---|
| Branch | `priority-8-phase-4b-editorial-authoring` |
| HEAD | `4b76312a2425969fedcf2a161a2128c79afc0095` |
| Tree | `905368929f1ea69dc7b26e39aa867db9a6069905` |
| Parent | `49dcd8a3d8ac567e462c7dace76a1ba46f1d48c0` |
| Subject | `Priority 8 Phase 4B correct final inline glosses` |
| Worktree | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and blocking |

The live staging envelope was `phaseStep = 4B7`, `stagingRevision = 8`. The validator passed and the exact existing eleven Phase 4B suites passed all 274 tests before the freeze artifacts were authored.

## 2. Human freeze decision

**THE CURRENT 543 CANDIDATE KEYS ARE HUMAN-APPROVED AND FROZEN.**

This decision freezes the semantic candidate-key identity layer only. It does not freeze learner-facing wording, teaching metadata, lifecycle state, guards, runtime state, or production IDs.

Candidate semantic keys are now frozen.

Stable production IDs are NOT yet allocated.

## 3. Rationale and inventory

The 68-lemma corpus has completed semantic reconciliation, final corrections, independent candidate-key approval, and the post-verification inline-gloss cleanup. Freezing now gives Phase 4C one stable semantic identity layer from which deterministic production IDs may later be allocated or mapped.

| Identity unit | Count |
|---|---:|
| Full-pattern lemmas | 68 |
| `candidateMeaningKey` | 95 |
| `candidatePatternKey` | 224 |
| `candidateExampleKey` | 224 |
| Total candidate keys | 543 |

## 4. Manifest and deterministic projection

Manifest: `editorial/priority-8-phase4-candidate-key-freeze.json`

Schema version: `freezeSchemaVersion = 1`; `priority = 8`; `phase = 4B`; `status = frozen`.

The canonical projection is the manifest's `lemmas` array. Lemmas are sorted by `verificationOrder`. Each lemma contains only `verificationOrder`, `canonicalLemma`, and ordered meanings. Each meaning contains only `candidateMeaningKey` and its ordered patterns. Each pattern contains only `candidatePatternKey` and its owned example object containing only `candidateExampleKey`.

The projection is serialized with UTF-8 JSON using Unicode characters directly, object keys sorted lexicographically, and separators `,` and `:` with no insignificant whitespace. SHA-256 of those canonical bytes is:

`candidateKeyFreezeDigest = 0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27`

The digest was independently recomputed from live staging and from the manifest hierarchy. Both equal the recorded digest exactly.

The manifest contains no learner-facing text, complement structure, evidence material, production ID, runtime ID, audio ID, or batch-specific synthetic identity. It freezes identity and ownership, not editorial wording.

## 5. Key validation

Mechanical validation established:

- all 543 keys match kebab-case key syntax;
- sibling uniqueness holds at lemma, meaning, pattern, and example ownership scopes;
- every pattern resolves to one meaning in its lemma;
- every example resolves to one pattern under the same meaning;
- exactly one example is owned by every pattern;
- zero orphan references, duplicate owners, or ownership mismatches exist;
- zero `czy-dependent-clause` keys remain;
- `zapominać/interrogative-forgotten-content` is present;
- `kłócić się/interrogative-disputed-content` is present;
- no key contains `vp-` production-ID material;
- no key depends on verification order, batch number, or evidence-source ID;
- no example key depends on current Polish or English wording.

## 6. HD-2 source-role durability

The seven approved source/provider semantic identities remain:

| Lemma | Meaning key | Pattern key | Coarse Phase 4B role |
|---|---|---|---|
| `wracać` | `return-to-earlier-place` | `z-genitive-return-source` | `target` |
| `wrócić` | `completed-return-to-earlier-place` | `z-genitive-return-source` | `target` |
| `wyjść` | `literal-exit-from-place` | `z-genitive-source` | `target` |
| `wyjechać` | `transport-departure` | `z-genitive-source` | `target` |
| `kupować` | `process-purchase` | `seller-price-schema` | `target` on the `od + Genitive` seller |
| `kupić` | `completed-purchase` | `seller-price-schema` | `target` on the `od + Genitive` seller |
| `zamawiać` | `commissioning-ordering` | `u-genitive-provider` | `target` |

The key freeze does NOT approve `target` as the final runtime semantic representation for these rows.

Phase 4C remains bound to produce a faithful source representation before runtime projection.

## 7. Final historical batch digests

All existing historical projections were independently recomputed and matched their final locks:

| Batch | Final digest |
|---|---|
| B1 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` |
| B2 | `87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82` |
| B3 | `6f69b92ac24cda947aee18b06fe8090f36a70c64fec8db6650abcc8d024a8601` |
| B4 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` |
| B5 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` |
| B6 | `ec9148072c58879334e1eeeae1b20f62259ceecf56ea18500f0d0fb4666e610a` |
| B7 | `910b83b8c63f3bac49648623e52f861ea31d20e427daef6d200977486be35f93` |

No existing historical lock was modified for this checkpoint.

## 8. Regression test and mutation proof

Regression test: `tests/test_priority8_phase4b_candidate_key_freeze.py`

The test protects the exact 68 lemma/order hierarchy, counts, complete hierarchical key projection, freeze digest, manifest/live equality, ownership integrity, corrected interrogative identities, the seven HD-2 source/provider identities, absence of old `czy` keys and stable production IDs, and manifest `status = frozen`.

The following in-memory mutations are all detected by an integrity failure or digest mismatch:

| Mutation | Result |
|---|---|
| Rename one meaning key | caught |
| Rename one pattern key | caught |
| Rename one example key | caught |
| Move one pattern to a different meaning | caught |
| Reassign one example to another pattern | caught |
| Swap two pattern keys | caught |
| Restore `czy-dependent-clause` | caught |
| Rename a source key to a target-oriented key | caught |
| Remove one key | caught |
| Add one key | caught |
| Change only `learnerExplanationEn` | digest unchanged, as required |

The test deliberately does not pin `learnerExplanationEn`, Polish or English examples, CEFR, teaching status, priority, register, candidate origin, review status, guard count, runtime state, or fixed future staging lifecycle values. It compares the manifest's source-staging metadata to live staging without freezing those fields into the identity digest.

## 9. Governance rule after freeze

After this checkpoint, no frozen candidate key may be renamed, removed, reassigned, reparented, or reused for a different semantic identity without explicitly reopening Priority 8 Phase 4B governance.

Phase 4C stable IDs must be derived from or mapped to this frozen hierarchy. Phase 4C must stop if the live projection differs from the manifest or its digest.

A newly approved semantic row that would require a new candidate key is also key-set expansion and therefore requires an explicit Phase 4B governance reopening; it cannot be introduced silently during Phase 4C.

## 10. Phase 4B completion and Phase 4C entry

Phase 4B semantic authoring and candidate-key governance are complete. No stable production ID, canonical promotion, runtime projection, audio work, deployment, or integration is performed by this freeze.

Phase 4C may begin only from this exact checkpoint after independent freeze verification confirms the manifest, digest, 543-key inventory, validator, existing Phase 4B suites, dedicated freeze test, and absence of unexpected stable IDs.

Candidate semantic keys are now frozen.

Stable production IDs are NOT yet allocated.
