# Priority 8 final Phase 4B to Phase 4C handoff

## A. Binding baseline

Phase 4C begins from the frozen Phase 4B semantic identity layer represented by `editorial/priority-8-phase4-candidate-key-freeze.json`.

| Measure | Baseline |
|---|---:|
| Full-pattern lemmas | 68 |
| Meanings | 95 |
| Patterns | 224 |
| Examples | 224 |
| Frozen candidate keys | 543 |
| Active-production patterns | 222 |
| Recognition-only patterns | 2 |

The staging envelope remains `phaseStep = 4B7`, `stagingRevision = 8`. The guard registry baseline is 74 rules at `registryVersion = 2`.

## B. Freeze manifest and digest

- Manifest: `editorial/priority-8-phase4-candidate-key-freeze.json`
- Freeze report: `reports/priority-8-phase-4b-candidate-key-freeze.md`
- Regression test: `tests/test_priority8_phase4b_candidate_key_freeze.py`
- `candidateKeyFreezeDigest`: `0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27`

The live staging hierarchy and manifest hierarchy are exactly equal under the canonical freeze projection.

## C. Final B1–B7 digests

| Batch | Final digest |
|---|---|
| B1 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` |
| B2 | `87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82` |
| B3 | `6f69b92ac24cda947aee18b06fe8090f36a70c64fec8db6650abcc8d024a8601` |
| B4 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` |
| B5 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` |
| B6 | `ec9148072c58879334e1eeeae1b20f62259ceecf56ea18500f0d0fb4666e610a` |
| B7 | `910b83b8c63f3bac49648623e52f861ea31d20e427daef6d200977486be35f93` |

## D. Stable-ID and promotion boundary

**NO stable production IDs currently exist.** Phase 4C may allocate or map IDs only after consuming and verifying the frozen candidate semantic identities. Every production meaning, pattern, and example ID must trace to exactly one frozen composite owner in the manifest.

Private staging must never be consumed directly by runtime/product code. Phase 4C must perform canonical reconciliation and promotion into approved canonical editorial/governance data before any runtime projection. Stable-ID allocation does not authorize runtime projection, deployment, audio generation, or activity activation.

The approved future version boundary remains: direct-speech canonical legal-shape support moves the contract to `formatVersion = 2`; the completed expansion runtime later moves `patternDataRevision` from 2 to 3. Those increments occur only in their separately governed implementation/projection phases.

## E. Metadata-only and lexical identity boundaries

- Full `zacząć` owns metadata-only `zaczynać`; `zaczynać` must not become a separate full record merely because IDs are allocated.
- Full `czytać` owns metadata-only `przeczytać`; `przeczytać` must not become a separate full record merely because IDs are allocated.
- `radzić` and `radzić sobie` are separate lexical identities and must not inherit, merge, or exchange syntax.
- `uczyć` remains non-reflexive and distinct from released `uczyć się`; Phase 4C must reconcile the product overlap without donating or merging syntax.
- `życzyć` remains distinct from `życzyć sobie`; the optional/embedded occurrence of `sobie` elsewhere does not create that lexical identity.
- Lexical `się`/`sobie` is identity-bearing for `kłócić się`, `radzić sobie`, `spotykać się`, `spotkać się`, `umówić się`, `cieszyć się`, `martwić się`, and `zgadzać się`.
- `kochać` remains distinct from released `lubić`; product overlap requires integration review, not semantic merger.
- `brać` and `wziąć` participation meanings require lexical `udział`; Phase 4C must preserve this requirement in canonical validation/projection.

## F. Deduplicated binding Phase 4C debt inventory

Closed Phase 4B editorial defects and completed reconciliation corrections are deliberately excluded. The list below contains only still-live architecture, promotion, or projection obligations supported by committed governance.

| Debt ID | Affected lemma(s) | Current Phase 4B representation and why acceptable | Required Phase 4C action | Resolve before runtime projection? | Expected key impact |
|---|---|---|---|---|---|
| P8-4C-D01 | `wracać`, `wrócić`, `wyjść`, `wyjechać`, `kupować`, `kupić`, `zamawiać` | Seven source/provider participants use legal coarse `role: target`; durable keys, scopes, and explanations preserve source semantics, so Phase 4B identity is faithful. | Add a faithful canonical/runtime source representation or a special projection rule that never renders target's “what it is aimed at” phrase for these rows; re-audit released canonical role use if the enum expands. | yes | expected none; source/provider keys are already durable |
| P8-4C-D02 | 11 direct-speech patterns on `odpowiadać`, `czytać`, `pisać`, `napisać`, `powiedzieć`, `zgadzać się`, `polecać`, `radzić` | Private staging legally carries `clauseKind: direct-speech`; runtime/canonical support was intentionally deferred. `odpowiadać/direct-speech` is additionally a documented policy addition rather than a frozen source label. | Implement and validate canonical/tooling/runtime legal-shape support, including the approved format-version boundary, before canonical promotion; explicitly adjudicate the `odpowiadać` policy row during reconciliation. | yes | expected none if all 11 frozen identities survive; rejection/removal would require reopening Phase 4B |
| P8-4C-D03 | `pracować`, `przynosić`, `pokazywać`, `czytać`, `zapraszać`, `wiedzieć`, `uczyć`; corpus-wide `KTÓRĘDY` | Verified `GDZIE`, `SKĄD`, optional source/goal, and `KTÓRĘDY` positions are deliberately unrepresented because Phase 4B could not invent concrete realizations or types. Representable cores remain valid. | Decide and document which generalized positions receive canonical structural representation and which remain an explicit permanent boundary; do not infer arbitrary prepositions. | yes | expected none if the boundary remains; adding frozen semantic rows/keys requires reopening Phase 4B |
| P8-4C-D04 | `umówić się` appointment sense | Required source-selected `KIEDY` is documented but intentionally non-structural; the `GDZIE` venue has only the narrowed `do + Genitive` realization. | Decide explicitly whether `KIEDY` remains a permanent non-structural boundary or gains governed canonical representation; never fold it into the venue complement. | yes | expected none if boundary remains; a new keyed row requires reopening Phase 4B |
| P8-4C-D05 | `umówić się` agreement sense; future compound-preposition rows | Verified `co do + Genitive` is not represented because the locked preposition validator accepts one word; five other agreement alternatives remain valid. | Decide compound-preposition support. If supported, return to Phase 4B governance before adding the sixth semantic pattern/example identity; never encode it as `co` or `do` alone. | yes | not none if added: at least one new pattern and example key, requiring Phase 4B reopening |
| P8-4C-D06 | `wiedzieć`, `rozumieć`, `zapraszać`, `pasować`, motion/source families and comparable peers | Coarse roles such as `content`/`object`, `target`, and `experiencer` are defensible and meaning keys preserve distinctions; no Phase 4B defect remains. | Review canonical role-vocabulary granularity and either retain the governed coarse mapping with accurate learner phrases or extend it with migration and released-corpus re-audit. | yes | expected none |
| P8-4C-D07 | `pasować` expectation-suitability meaning | `lexical-frame` with optional Dative `experiencer` exactly reflects the source positions; Phase 4B could not use `subject-experiencer` without inventing a Nominative complement. | Decide whether canonical promotion keeps this legal lexical frame or supports a constructionally supplied subject under `subject-experiencer`, following the `podobać się` precedent. | yes | expected none |
| P8-4C-D08 | `kochać` infinitive strongly-liked activity | Register remains `neutral` because frozen evidence provides no informal/register caveat; this is faithful and not a Phase 4B defect. | Revisit only if Phase 4C obtains governed register evidence; otherwise preserve `neutral`. | no | expected none |
| P8-4C-D09 | Batch 1 and residual early Batch 2 semantic protection | Historical digests and validator rules protect the frozen projection; Batch 1 still has no declarative semantic guards, while Batch 2 coverage is selective. | Confirm during canonical reconciliation that digest/validator coverage is sufficient or add future-safe semantic guards without changing frozen keys. | yes | expected none |
| P8-4C-D10 | All 68 lemmas / 224 patterns and examples | Private staging intentionally omits canonical production IDs and canonical fields such as normalized evidence/origin, activity eligibility, content references, and audio eligibility. | Construct, review, and validate canonical records; map provenance; allocate deterministic IDs from frozen owners; preserve the no-activity-without-authorization and no-audio-generation boundaries. | yes | expected none; IDs map to frozen keys rather than replace them |
| P8-4C-D11 | Metadata-only partners and lexical identities listed in section E; released `uczyć się` and `lubić` overlaps | Phase 4B keeps identities separate and metadata-only partners empty; product overlap is unresolved integration work, not semantic uncertainty. | Reconcile against released canonical data without accidental merge, syntax donation, duplicate full records, or aspect-partner promotion. | yes | expected none |
| P8-4C-D12 | `brać`, `wziąć` | `requiredLexicalItems: ["udział"]` and guards preserve fixed participation constructions in private staging. | Preserve required `udział` through canonical schema/validation or an equally strong governed constraint before promotion. | yes | expected none |
| P8-4C-D13 | `móc` permission meaning and future activities | `Czy mogę…?` is usage-level sentence packaging over the infinitive, not a question complement; the current key hierarchy is correct. | Ensure canonical projection and any later exercise/activity generation do not reintroduce `czy` as a complement of `móc`. | yes | expected none |

## G. Phase 4C entry conditions

Phase 4C may begin only if all of the following remain true:

1. The candidate-key freeze manifest exists with `status = frozen`.
2. The dedicated freeze regression test passes.
3. Live staging and manifest recompute the exact recorded `candidateKeyFreezeDigest`.
4. The hierarchy remains 68 lemmas, 95 meanings, 224 patterns, 224 examples, and 543 candidate keys.
5. `python3 validate_priority8_staging.py` passes.
6. All existing Phase 4B suites pass.
7. No stable production IDs pre-exist unexpectedly.
8. Work begins from the commit containing this exact freeze checkpoint.

Phase 4C must stop if the key projection differs. Any proposed candidate-key rename, removal, reassignment, reparenting, reuse, or addition after this checkpoint requires explicitly reopening Priority 8 Phase 4B governance.

## H. Phase 4B completion boundary

Candidate semantic keys are now frozen. Stable production IDs are NOT yet allocated. No canonical promotion, runtime projection, Phase 4C implementation, audio generation, activity activation, deployment, or integration is performed by this handoff.
