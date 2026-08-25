# Priority 8 Phase 4B — final 68-lemma mechanical reconciliation audit

This document is an audit and adjudication queue. It makes no semantic correction, renames no candidate key, allocates no stable ID, and changes no staging, guard, test, validator, schema, canonical, runtime, production, analytics, audio, or telemetry artifact.

## 1. Starting state

The stop-on-mismatch gate passed before this report was created.

| Check | Required | Recomputed result |
|---|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4B SAFE` | exact |
| Branch | `priority-8-phase-4b-editorial-authoring` | exact |
| HEAD | `d3ac83903f2f48c1394f074a3c11e25783fb84fb` | exact |
| Tree | `d0b25cbc11dc2fa7cab28ce769e4aa192b22349d` | exact |
| Parent | `12a922fac870dd0d4ec3aa37cb53d6a78b53e9c3` | exact |
| Subject | `Correct Priority 8 Phase 4B7 priority count` | exact |
| Initial worktree | clean | clean |
| Remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Pre-push hook | executable and blocking | executable; emits the repository-specific block message and exits 1 |
| Staging envelope | `phaseStep=4B7`, `stagingRevision=8` | exact |
| Review status | 68 `draft` | exact |
| Guard registry | version 2, 72 rules | exact |

## 2. Global inventory

### Aggregate totals

| Unit | Total |
|---|---:|
| Full-pattern lemmas | 68 |
| Meanings | 95 |
| Patterns | 224 |
| Examples | 224 |
| Future-empty full-pattern records | 0 |
| Active-production patterns | 220 |
| Recognition-only patterns | 4 |
| Other teaching statuses | 0 |

Aggregate distributions:

- CEFR recognition/production: `A1/A1` 60; `A1/A2` 7; `A2/A2` 96; `A2/B1` 57; `B1/—` 4.
- Priority: `core` 116; `common` 108.
- Register: `neutral` 224; every other value 0.
- Candidate origin: `editorial-generated` 220; `repository-reuse` 4.
- Relation type: `lexical-frame` 218; `means-method` 6.
- Complement type occurrences: `case` 121; `preposition-case` 117; `clause` 65; `infinitive` 21.
- Role occurrences: `content` 90; `object` 67; `recipient` 64; `target` 55; `topic` 22; `interlocutor` 15; `means` 9; `experiencer` 2.

### Per-lemma inventory

`CEFR` is recognition/production. `A/R` is active-production/recognition-only. Distributions are counts within the lemma.

|Order|Batch|Lemma|Aspect|M|P|E|A/R|CEFR|Priority|Register|Origin|
|---:|---:|---|---|---:|---:|---:|---:|---|---|---|---|
|1|1|`pracować`|imperfective|1|1|1|1/0|A1/A2:1|core:1|neutral:1|editorial-generated:1|
|2|1|`iść`|imperfective|1|3|3|3/0|A1/A1:3|core:3|neutral:3|editorial-generated:2, repository-reuse:1|
|3|1|`chodzić`|imperfective|2|3|3|3/0|A1/A1:3|core:3|neutral:3|editorial-generated:3|
|4|1|`jechać`|imperfective|1|3|3|3/0|A1/A1:2, A1/A2:1|core:2, common:1|neutral:3|editorial-generated:3|
|5|1|`jeździć`|imperfective|1|3|3|3/0|A2/A2:3|core:2, common:1|neutral:3|editorial-generated:3|
|6|1|`dojść`|perfective|1|1|1|1/0|A2/A2:1|common:1|neutral:1|editorial-generated:1|
|7|1|`dojechać`|perfective|1|4|4|4/0|A2/A2:4|core:3, common:1|neutral:4|editorial-generated:4|
|8|1|`wracać`|imperfective|1|2|2|2/0|A1/A1:2|core:1, common:1|neutral:2|editorial-generated:2|
|9|1|`wrócić`|perfective|1|2|2|2/0|A2/A2:2|core:1, common:1|neutral:2|editorial-generated:2|
|10|1|`przyjść`|perfective|2|3|3|3/0|A2/A2:3|core:3|neutral:3|editorial-generated:3|
|11|2|`przyjechać`|perfective|1|2|2|2/0|A2/A2:2|core:2|neutral:2|editorial-generated:2|
|12|2|`wyjść`|perfective|1|3|3|3/0|A1/A1:1, A2/A2:2|core:1, common:2|neutral:3|editorial-generated:3|
|13|2|`wyjechać`|perfective|1|1|1|1/0|A2/A2:1|core:1|neutral:1|editorial-generated:1|
|14|2|`przynosić`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|15|2|`odpowiadać`|imperfective|1|3|3|3/0|A1/A1:1, A2/B1:2|core:1, common:2|neutral:3|editorial-generated:3|
|16|2|`zamawiać`|imperfective|1|4|4|4/0|A1/A1:1, A2/A2:3|core:1, common:3|neutral:4|editorial-generated:4|
|18|2|`zacząć`|perfective|1|2|2|2/0|A1/A1:2|core:2|neutral:2|editorial-generated:2|
|19|2|`kończyć`|imperfective|1|2|2|2/0|A1/A1:2|core:2|neutral:2|editorial-generated:2|
|20|2|`pamiętać`|imperfective|2|4|4|4/0|A1/A1:1, A2/A2:2, A2/B1:1|core:2, common:2|neutral:4|editorial-generated:4|
|21|2|`zapominać`|imperfective|2|6|6|5/1|A2/A2:4, A2/B1:1, B1/—:1|core:3, common:3|neutral:6|editorial-generated:6|
|22|3|`próbować`|imperfective|2|3|3|3/0|A1/A1:1, A2/A2:2|core:2, common:1|neutral:3|editorial-generated:3|
|23|3|`pozwalać`|imperfective|2|6|6|5/1|A2/B1:5, B1/—:1|core:2, common:4|neutral:6|editorial-generated:6|
|24|3|`unikać`|imperfective|1|1|1|1/0|A2/A2:1|core:1|neutral:1|editorial-generated:1|
|25|3|`wymagać`|imperfective|2|4|4|3/1|A2/A2:2, A2/B1:1, B1/—:1|core:2, common:2|neutral:4|editorial-generated:3, repository-reuse:1|
|26|3|`należeć`|imperfective|2|2|2|2/0|A2/A2:2|core:2|neutral:2|editorial-generated:2|
|27|3|`kłócić się`|imperfective|1|4|4|3/1|A1/A1:2, A2/B1:1, B1/—:1|core:2, common:2|neutral:4|editorial-generated:4|
|28|3|`pokazywać`|imperfective|1|3|3|3/0|A1/A1:1, A2/A2:2|core:2, common:1|neutral:3|editorial-generated:3|
|29|3|`radzić sobie`|imperfective|1|1|1|1/0|A2/A2:1|core:1|neutral:1|editorial-generated:1|
|30|3|`kupować`|imperfective|1|3|3|3/0|A1/A2:1, A2/A2:2|core:1, common:2|neutral:3|editorial-generated:3|
|31|3|`kupić`|perfective|1|3|3|3/0|A1/A2:1, A2/A2:2|core:1, common:2|neutral:3|editorial-generated:1, repository-reuse:2|
|32|4|`dawać`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|33|4|`dać`|perfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|34|4|`brać`|imperfective|2|3|3|3/0|A1/A1:2, A2/A2:1|core:2, common:1|neutral:3|editorial-generated:3|
|35|4|`wziąć`|perfective|2|3|3|3/0|A1/A1:2, A2/A2:1|core:2, common:1|neutral:3|editorial-generated:3|
|36|4|`czytać`|imperfective|1|5|5|5/0|A1/A1:1, A2/A2:2, A2/B1:2|core:2, common:3|neutral:5|editorial-generated:5|
|38|4|`pisać`|imperfective|2|13|13|13/0|A1/A1:3, A2/A2:4, A2/B1:6|core:3, common:10|neutral:13|editorial-generated:13|
|39|4|`napisać`|perfective|2|13|13|13/0|A1/A1:3, A2/A2:4, A2/B1:6|core:3, common:10|neutral:13|editorial-generated:13|
|40|4|`spotykać się`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|41|4|`spotkać się`|perfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|42|5|`oglądać`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|43|5|`obejrzeć`|perfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|44|5|`skończyć`|perfective|2|3|3|3/0|A1/A1:1, A1/A2:1, A2/B1:1|core:2, common:1|neutral:3|editorial-generated:3|
|45|5|`chcieć`|imperfective|2|6|6|6/0|A1/A1:3, A1/A2:1, A2/B1:2|core:4, common:2|neutral:6|editorial-generated:6|
|46|5|`robić`|imperfective|2|2|2|2/0|A1/A1:2|core:2|neutral:2|editorial-generated:2|
|47|5|`rozumieć`|imperfective|2|4|4|4/0|A1/A1:2, A2/A2:1, A2/B1:1|core:2, common:2|neutral:4|editorial-generated:4|
|48|5|`mieszkać`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|49|5|`umówić się`|perfective|2|7|7|7/0|A2/A2:5, A2/B1:2|core:2, common:5|neutral:7|editorial-generated:7|
|50|5|`dzwonić`|imperfective|1|4|4|4/0|A1/A1:2, A2/B1:2|core:2, common:2|neutral:4|editorial-generated:4|
|51|5|`powiedzieć`|perfective|1|11|11|11/0|A1/A1:2, A2/A2:4, A2/B1:5|core:4, common:7|neutral:11|editorial-generated:11|
|52|6|`gotować`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|53|6|`rezerwować`|imperfective|1|2|2|2/0|A2/A2:2|core:1, common:1|neutral:2|editorial-generated:2|
|54|6|`cieszyć się`|imperfective|1|4|4|4/0|A2/A2:2, A2/B1:2|core:2, common:2|neutral:4|editorial-generated:4|
|55|6|`martwić się`|imperfective|1|4|4|4/0|A2/A2:2, A2/B1:2|core:1, common:3|neutral:4|editorial-generated:4|
|56|6|`zgadzać się`|imperfective|2|7|7|7/0|A2/A2:3, A2/B1:4|core:3, common:4|neutral:7|editorial-generated:7|
|57|6|`zapraszać`|imperfective|1|2|2|2/0|A2/A2:2|core:2|neutral:2|editorial-generated:2|
|58|6|`polecać`|imperfective|2|5|5|5/0|A2/A2:2, A2/B1:3|core:1, common:4|neutral:5|editorial-generated:5|
|59|6|`radzić`|imperfective|1|5|5|5/0|A2/A2:2, A2/B1:3|core:1, common:4|neutral:5|editorial-generated:5|
|60|6|`pasować`|imperfective|4|5|5|5/0|A2/A2:4, A2/B1:1|core:4, common:1|neutral:5|editorial-generated:5|
|61|6|`móc`|imperfective|2|2|2|2/0|A1/A1:2|core:2|neutral:2|editorial-generated:2|
|62|7|`musieć`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|63|7|`wiedzieć`|imperfective|1|4|4|4/0|A1/A2:1, A2/A2:2, A2/B1:1|core:2, common:2|neutral:4|editorial-generated:4|
|64|7|`jeść`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|65|7|`pić`|imperfective|1|1|1|1/0|A1/A1:1|core:1|neutral:1|editorial-generated:1|
|66|7|`kochać`|imperfective|3|4|4|4/0|A1/A1:1, A2/A2:3|core:1, common:3|neutral:4|editorial-generated:4|
|67|7|`przepraszać`|imperfective|1|2|2|2/0|A2/A2:1, A2/B1:1|core:1, common:1|neutral:2|editorial-generated:2|
|68|7|`życzyć`|imperfective|1|2|2|2/0|A2/A2:1, A2/B1:1|core:1, common:1|neutral:2|editorial-generated:2|
|69|7|`korzystać`|imperfective|2|2|2|2/0|A2/A2:2|core:1, common:1|neutral:2|editorial-generated:2|
|70|7|`uczyć`|imperfective|2|6|6|6/0|A2/A2:5, A2/B1:1|core:1, common:5|neutral:6|editorial-generated:6|

## 3. Batch digest/lock audit

Each digest was independently recomputed by importing the corresponding historical test module and applying that batch's own projection fields, canonical JSON serialization, and staging-order membership.

| Batch | Lemmas | Meanings | Patterns/examples | Recomputed digest | Result |
|---:|---:|---:|---:|---|---|
| B1 | 10 | 12 | 25/25 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` | exact |
| B2 | 10 | 12 | 28/28 | `dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8` | exact |
| B3 | 10 | 14 | 30/30 | `8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb` | exact |
| B4 | 9 | 13 | 41/41 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` | exact |
| B5 | 10 | 15 | 40/40 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` | exact |
| B6 | 10 | 16 | 37/37 | `cff207b6e728fb203ba05a9ba94915432957be76101b3bd6a0f65137cdda98d5` | exact |
| B7 | 9 | 13 | 23/23 | `88aed6dc4b972ddc3ce7ea18b5e987d95ae1f38d5eb5a742a45be7332c372672` | exact |

Frozen matrix SHA-256 values also match their historical locks: B4 `6e63c9d2628d9237e7b5851c29e55975734440878dac7491873f9368291f3781`; B5 `9f2de2eda2cb051d47ec13f4eaadc45ba617f55b5c8871588db61e8b79641ad7`; B6 `72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c`; B7 `8b152b204485001f921d54c1b8941f9e2c2173fbc910cd52c57b9e240240212a`.

Historical-lock safety is correct. B1-B7 batch locks pin content projections rather than moving `phaseStep`, `stagingRevision`, corpus-wide draft counts, or future-empty boundaries. The Batch 6 repair is present: `len(registry["rules"]) >= 57`, while all 21 Batch 6 guard IDs remain individually required. B7 analogously uses `>= 72` and pins its 15 rule IDs. The only moving lifecycle assertions are intentionally centralized in `test_priority8_phase4b_progress.py`; no historical batch lock still pins moving lifecycle state.

## 4. Candidate-key audit

All 95 meaning keys, 224 pattern keys, and 224 example keys were scanned.

| Check | Meaning | Pattern | Example |
|---|---:|---:|---:|
| Values scanned | 95 | 224 | 224 |
| Invalid format/kebab-case | 0 | 0 | 0 |
| Sibling-scope duplicates | 0 | 0 | 0 |
| Raw globally unique values | 93 | 159 | 1 |
| Raw reused values | 2 values | 41 values | `primary` × 224 |
| Verification-order/batch number leakage | 0 | 0 | 0 |
| Source-ID leakage | 0 | 0 | 0 |
| Production `vp-*` leakage | 0 | 0 | 0 |

The raw reuse is authorized by the locked parent scopes: meaning within lemma, pattern within `(lemma, meaning)`, example within `(lemma, meaning, pattern)`. The repeated meaning keys are `activity-completion` (two aspect-related lemmas) and `fixed-participation` (two aspect-related lemmas). The 41 repeated pattern values are ordinary structural keys under distinct parents. All 224 example keys are deliberately `primary`; therefore none incorporates example wording. Composite ownership remains collision-free.

Mechanically invalid keys: none.

Technically valid but semantically freeze-sensitive keys:

- `zapominać/czy-dependent-clause` and `kłócić się/czy-dependent-clause` embed the unadjudicated literal-`czy` representation that conflicts with the frozen interrogative-dependent source classification.
- The meaning and pattern keys in the 14 same-lemma cross-meaning signature collisions listed in section 7 depend on semantic ownership that structure alone cannot prove. `polecać`, `kochać`, and `korzystać` are the highest explicitly documented examples.

## 5. Ownership audit

All references were checked in their locked scopes. Every `meaningKeyRef` resolves within its lemma. Every `(meaningKeyRef, candidatePatternKey)` is unique within the owning lemma. The multiset of 224 pattern owners equals the multiset of 224 example `(meaningKeyRef, patternKeyRef)` owners exactly. Every example's `candidateExampleKey` is unique in its parent pattern. Results: 0 orphan meanings, 0 orphan patterns, 0 orphan examples, 0 duplicate owners, 0 ownership mismatches, and exactly one example for every pattern.

## 6. Guard audit

Registry version is 2 and the registry contains 72 unique rule IDs. Primitive distribution: 39 `require-exact-pattern-shapes`; 15 `allow-only-preposition-case-signatures`; 8 `require-lexical-identity`; 5 `forbid-complement-match`; 2 `require-empty-candidate-content`; 2 `require-lexical-material-in-explanation`; 1 `forbid-complement-cooccurrence`.

Inferred provenance is B3 6 rules, B4 14, B5 14, B6 21, B7 15, and 2 metadata-only partner rules; B1/B2 predate the live declarative guard layer and are protected by validator/schema rules and historical digests rather than batch-specific semantic rules. Every rule ID expected by its historical suite is present. No duplicate ID, byte-equivalent configuration (ignoring only `ruleId`), unresolved target, violation, or contradictory rule pair exists.

Overlaps are intentional redundant defense: exact-shape plus authorized-preposition controls; exact-shape plus lexical-identity controls; exact-shape plus explicit negative controls; and exact participation shapes plus learner-explanation lexical-material controls. There is no suspicious duplicate configuration. The material architecture limitation is that pre-B3 source/staging semantic alignment is not independently guarded; consequently both `czy` discrepancies pass all current structural tests and are also pinned by their historical digests. After adjudication, CODEX must ensure the chosen state and its regression protection agree before Phase 4C.

Rule-ID inventory by provenance:

- **B3 (6):** `p8-4b-pozwalac-no-dative-infinitive`, `p8-4b-unikac-no-infinitive`, `p8-4b-wymagac-exact-alternative-shapes`, `p8-4b-klocic-sie-lexical-identity`, `p8-4b-pokazywac-authorized-preposition-cases`, `p8-4b-radzic-sobie-lexical-identity`.
- **B4 (14):** `p8-4b-dawac-exact-pattern-shapes`, `p8-4b-dac-exact-pattern-shapes`, `p8-4b-brac-exact-pattern-shapes`, `p8-4b-brac-participation-explanation-material`, `p8-4b-wziac-exact-pattern-shapes`, `p8-4b-wziac-participation-explanation-material`, `p8-4b-czytac-exact-pattern-shapes`, `p8-4b-czytac-authorized-o-locative-topic-signatures`, `p8-4b-pisac-exact-pattern-shapes`, `p8-4b-napisac-exact-pattern-shapes`, `p8-4b-spotykac-sie-lexical-identity`, `p8-4b-spotykac-sie-exact-pattern-shapes`, `p8-4b-spotkac-sie-lexical-identity`, `p8-4b-spotkac-sie-exact-pattern-shapes`.
- **B5 (14):** `p8-4b-ogladac-exact-pattern-shapes`, `p8-4b-obejrzec-exact-pattern-shapes`, `p8-4b-skonczyc-exact-pattern-shapes`, `p8-4b-chciec-exact-pattern-shapes`, `p8-4b-robic-exact-pattern-shapes`, `p8-4b-rozumiec-exact-pattern-shapes`, `p8-4b-mieszkac-exact-pattern-shapes`, `p8-4b-mieszkac-authorized-preposition-cases`, `p8-4b-dzwonic-exact-pattern-shapes`, `p8-4b-dzwonic-authorized-preposition-cases`, `p8-4b-powiedziec-exact-pattern-shapes`, `p8-4b-umowic-sie-lexical-identity`, `p8-4b-umowic-sie-exact-pattern-shapes`, `p8-4b-umowic-sie-authorized-preposition-cases`.
- **B6 (21):** `p8-4b-gotowac-exact-pattern-shapes`, `p8-4b-rezerwowac-exact-pattern-shapes`, `p8-4b-rezerwowac-authorized-preposition-cases`, `p8-4b-cieszyc-sie-lexical-identity`, `p8-4b-cieszyc-sie-exact-pattern-shapes`, `p8-4b-cieszyc-sie-authorized-preposition-cases`, `p8-4b-martwic-sie-lexical-identity`, `p8-4b-martwic-sie-exact-pattern-shapes`, `p8-4b-martwic-sie-authorized-preposition-cases`, `p8-4b-zgadzac-sie-lexical-identity`, `p8-4b-zgadzac-sie-exact-pattern-shapes`, `p8-4b-zgadzac-sie-authorized-preposition-cases`, `p8-4b-zapraszac-exact-pattern-shapes`, `p8-4b-zapraszac-authorized-preposition-cases`, `p8-4b-polecac-exact-pattern-shapes`, `p8-4b-radzic-exact-pattern-shapes`, `p8-4b-radzic-no-z-instrumental-coping`, `p8-4b-pasowac-exact-pattern-shapes`, `p8-4b-pasowac-authorized-preposition-cases`, `p8-4b-moc-exact-pattern-shapes`, `p8-4b-moc-no-question-clause`.
- **B7 (15):** `p8-4b-musiec-exact-pattern-shapes`, `p8-4b-wiedziec-exact-pattern-shapes`, `p8-4b-wiedziec-authorized-preposition-cases`, `p8-4b-jesc-exact-pattern-shapes`, `p8-4b-jesc-no-lexical-genitive`, `p8-4b-pic-exact-pattern-shapes`, `p8-4b-pic-no-lexical-genitive`, `p8-4b-kochac-exact-pattern-shapes`, `p8-4b-przepraszac-exact-pattern-shapes`, `p8-4b-przepraszac-authorized-preposition-cases`, `p8-4b-zyczyc-exact-pattern-shapes`, `p8-4b-korzystac-exact-pattern-shapes`, `p8-4b-korzystac-authorized-preposition-cases`, `p8-4b-uczyc-exact-pattern-shapes`, `p8-4b-uczyc-authorized-preposition-cases`.
- **Metadata-only (2):** `p8-4b-zaczynac-metadata-only`, `p8-4b-przeczytac-metadata-only`.

Classification: the overlapping guards are intentional redundant defense; suspicious duplication 0; actual contradiction 0.

## 7. Signature inventory

Canonical signature fields were exactly `relationType` plus, in source order for every complement, `type`, `case`, `preposition`, `role`, `required`, and `clauseKind`.

- Duplicate signatures within the same meaning: **0 groups / 0 rows**. The potentially blocking A class is empty.
- Identical signatures across meanings of the same lemma: **14 groups / 29 rows**, across 12 lemmas. These are a semantic limitation, not a mechanically provable defect.
- Identical signatures across different lemmas: **39 groups / 174 rows**. These are informational convention precedents.

The complete B-class inventory is:

| Lemma | Shared shape | Meanings/patterns |
|---|---|---|
| `próbować` | Genitive object | `attempt-action-result/genitive-action-noun`; `taste-sample-food-drink/genitive-sampled-object` |
| `pozwalać` | infinitive content | `human-permission/infinitive`; `inanimate-enabling/infinitive` |
| `wymagać` | Genitive object + optional `od` target | both meanings' `genitive-required-content` |
| `wymagać` | `żeby` content + optional `od` target | both meanings' `zeby-clause` |
| `należeć` | `do` + Genitive target | ownership and organization-membership rows |
| `chcieć` | infinitive content | both meanings' infinitive rows |
| `chcieć` | `żeby` content | both meanings' `żeby` rows |
| `robić` | Accusative object | creation and activity-performance rows |
| `rozumieć` | Accusative object | content and empathic-person rows |
| `zgadzać się` | direct-speech content | consent and opinion-agreement rows |
| `polecać` | Accusative object + optional Dative recipient | directive action-noun and recommended-item rows |
| `móc` | infinitive content | ability/possibility and permission rows |
| `kochać` | Accusative object | person, idea/place, and strong-liking rows |
| `korzystać` | `z` + Genitive object | resource-use and benefit-from rows |

The largest C-class precedents are: required `do` + Genitive target (15 rows), required Accusative object (19), required infinitive content (18), required `na` + Accusative target (12), required `że` content (8), Accusative object plus optional Dative recipient (9), and the correspondence clause families across `pisać`, `napisać`, and `powiedzieć`. No cross-lemma identity creates ownership ambiguity because all keys and references are parent-scoped.

## 8. RelationType/role consistency

The two relation types and eight roles are schema-valid. Comparable-shape differences needing interpretation rather than mechanical normalization are:

| Construction | Current labels | Comparable precedent / assessment |
|---|---|---|
| required Instrumental | B1 motion rows: `means-method/means`; B6 `cieszyć się`, `martwić się`: `lexical-frame/object` | Semantically motivated; informational. |
| required `z` + Genitive | B1/B2 motion sources: `target`; B6 `cieszyć się`: `topic`; B7 `korzystać`: `object` | Same form, different semantic roles. Motion use exposes closed-enum source-role debt. |
| required Accusative | 19 rows `object`; B7 `wiedzieć/accusative-known-content`: `content` | Plausible meaning distinction, but a cross-batch role convention review is warranted before freeze. |
| required `z` + Instrumental | meeting/agreement/quarrel partner: `interlocutor`; coping/cessation: `topic` | Semantically motivated; informational. |
| Accusative + `za` + Accusative | B4 taking: `object,target`; B7 apology: `interlocutor,topic` | Semantically motivated; informational. |

No mechanically provable wrong label or contradictory relation type was found. The `source` role does not exist in the locked enum: `wracać`, `wrócić`, `wyjść`, and `wyjechać` therefore encode a semantically source-like `z` + Genitive complement as legal `role: target`. The source semantics survive in keys, scopes, and explanations, but this is architecture debt requiring an explicit pre-4C policy decision.

## 9. ClauseKind audit

Counts across 65 clause complements: `ze` 19; `zeby` 19; `interrogative` 14; `direct-speech` 11; `czy` 2; other 0.

Complete clause inventory:

|Batch|Lemma|Meaning|Pattern|clauseKind|
|---:|---|---|---|---|
|B2|`odpowiadać`|`answering-by-speech`|`ze-content-clause`|`ze`|
|B2|`odpowiadać`|`answering-by-speech`|`direct-speech`|`direct-speech`|
|B2|`pamiętać`|`obligation-reminder`|`zeby-clause-obligation`|`zeby`|
|B2|`zapominać`|`recall-failure`|`ze-content-clause`|`ze`|
|B2|`zapominać`|`recall-failure`|`czy-dependent-clause`|`czy`|
|B3|`pozwalać`|`human-permission`|`dative-zeby-permission`|`zeby`|
|B3|`pozwalać`|`inanimate-enabling`|`zeby-enabling`|`zeby`|
|B3|`wymagać`|`person-requires-behavior`|`zeby-clause`|`zeby`|
|B3|`wymagać`|`situation-requires-content`|`zeby-clause`|`zeby`|
|B3|`kłócić się`|`interpersonal-quarrelling`|`ze-content-clause`|`ze`|
|B3|`kłócić się`|`interpersonal-quarrelling`|`czy-dependent-clause`|`czy`|
|B3|`pokazywać`|`directing-attention-to-content`|`interrogative-dependent-clause`|`interrogative`|
|B4|`czytać`|`reading-written-content`|`ze-content-clause`|`ze`|
|B4|`czytać`|`reading-written-content`|`interrogative-content-clause`|`interrogative`|
|B4|`czytać`|`reading-written-content`|`direct-speech-content`|`direct-speech`|
|B4|`pisać`|`written-correspondence`|`dative-ze-clause`|`ze`|
|B4|`pisać`|`written-correspondence`|`dative-zeby-clause`|`zeby`|
|B4|`pisać`|`written-correspondence`|`dative-interrogative-clause`|`interrogative`|
|B4|`pisać`|`written-correspondence`|`dative-direct-speech`|`direct-speech`|
|B4|`pisać`|`written-correspondence`|`do-genitive-ze-clause`|`ze`|
|B4|`pisać`|`written-correspondence`|`do-genitive-zeby-clause`|`zeby`|
|B4|`pisać`|`written-correspondence`|`do-genitive-interrogative-clause`|`interrogative`|
|B4|`pisać`|`written-correspondence`|`do-genitive-direct-speech`|`direct-speech`|
|B4|`napisać`|`completed-written-correspondence`|`dative-ze-clause`|`ze`|
|B4|`napisać`|`completed-written-correspondence`|`dative-zeby-clause`|`zeby`|
|B4|`napisać`|`completed-written-correspondence`|`dative-interrogative-clause`|`interrogative`|
|B4|`napisać`|`completed-written-correspondence`|`dative-direct-speech`|`direct-speech`|
|B4|`napisać`|`completed-written-correspondence`|`do-genitive-ze-clause`|`ze`|
|B4|`napisać`|`completed-written-correspondence`|`do-genitive-zeby-clause`|`zeby`|
|B4|`napisać`|`completed-written-correspondence`|`do-genitive-interrogative-clause`|`interrogative`|
|B4|`napisać`|`completed-written-correspondence`|`do-genitive-direct-speech`|`direct-speech`|
|B5|`chcieć`|`desire`|`zeby-desired-event`|`zeby`|
|B5|`chcieć`|`polite-request-or-intention`|`zeby-requested-event`|`zeby`|
|B5|`rozumieć`|`content-comprehension`|`ze-content-clause`|`ze`|
|B5|`rozumieć`|`content-comprehension`|`interrogative-content-clause`|`interrogative`|
|B5|`umówić się`|`mutual-agreement`|`ze-agreement-clause`|`ze`|
|B5|`umówić się`|`mutual-agreement`|`zeby-agreed-action-clause`|`zeby`|
|B5|`umówić się`|`mutual-agreement`|`interrogative-agreement-clause`|`interrogative`|
|B5|`dzwonić`|`telephone-contact`|`ze-reported-content-clause`|`ze`|
|B5|`dzwonić`|`telephone-contact`|`zeby-requested-content-clause`|`zeby`|
|B5|`powiedzieć`|`spoken-communication`|`dative-ze-clause`|`ze`|
|B5|`powiedzieć`|`spoken-communication`|`dative-zeby-clause`|`zeby`|
|B5|`powiedzieć`|`spoken-communication`|`dative-interrogative-clause`|`interrogative`|
|B5|`powiedzieć`|`spoken-communication`|`do-genitive-ze-clause`|`ze`|
|B5|`powiedzieć`|`spoken-communication`|`do-genitive-zeby-clause`|`zeby`|
|B5|`powiedzieć`|`spoken-communication`|`do-genitive-interrogative-clause`|`interrogative`|
|B5|`powiedzieć`|`spoken-communication`|`direct-speech-content`|`direct-speech`|
|B6|`cieszyć się`|`experiencing-joy`|`ze-propositional-cause`|`ze`|
|B6|`martwić się`|`worry-concern`|`ze-worry-proposition`|`ze`|
|B6|`martwić się`|`worry-concern`|`interrogative-worry-content`|`interrogative`|
|B6|`zgadzać się`|`consent`|`zeby-consented-event`|`zeby`|
|B6|`zgadzać się`|`consent`|`direct-speech-consent`|`direct-speech`|
|B6|`zgadzać się`|`opinion-agreement`|`ze-agreed-proposition`|`ze`|
|B6|`zgadzać się`|`opinion-agreement`|`direct-speech-agreement`|`direct-speech`|
|B6|`polecać`|`directive-instruction`|`dative-zeby-instruction`|`zeby`|
|B6|`polecać`|`directive-instruction`|`dative-direct-speech-instruction`|`direct-speech`|
|B6|`radzić`|`giving-advice`|`dative-zeby-advice`|`zeby`|
|B6|`radzić`|`giving-advice`|`dative-interrogative-advice`|`interrogative`|
|B6|`radzić`|`giving-advice`|`dative-direct-speech-advice`|`direct-speech`|
|B7|`wiedzieć`|`factual-knowledge`|`ze-known-proposition`|`ze`|
|B7|`wiedzieć`|`factual-knowledge`|`interrogative-queried-content`|`interrogative`|
|B7|`przepraszać`|`apology`|`accusative-person-ze-explanation`|`ze`|
|B7|`życzyć`|`good-wishes`|`dative-recipient-zeby-wished-event`|`zeby`|
|B7|`uczyć`|`teaching-instruction`|`accusative-learner-ze-taught-proposition`|`ze`|
|B7|`uczyć`|`teaching-instruction`|`accusative-learner-interrogative-taught-content`|`interrogative`|

Blocking source/staging discrepancies:

1. `zapominać/czy-dependent-clause` is live as `clauseKind: czy`, while Phase 3 order 21 records `clause:interrogative-dependent(recall sense)` and WSJP `ZDANIE PYTAJNOZALEŻNE`; no later human adjudication authorizing literal `czy` was found.
2. `kłócić się/czy-dependent-clause` is live as `clauseKind: czy`, while Phase 3 order 27 records `clause:interrogative-dependent` and parallel `ZDANIE PYTAJNOZALEŻNE`/`ŻE`; no later human adjudication authorizing literal `czy` was found.

The full 68-lemma source/staging comparison found no other discrepancy of this classification. `odpowiadać/direct-speech` is not a source-label substitution: its authoring/risk reports explicitly classify it as a private-staging policy addition with canonical support deferred to Phase 4C.

## 10. Generalized-role audit

| Lemma(s) | Frozen generalized role / boundary | Authored state | Classification |
|---|---|---|---|
| `pracować` | workplace `GDZIE` excluded | only exact `nad` + Instrumental | unrepresented by policy |
| `iść` | `DOKĄD` | `do`/`na` destination rows labelled non-exclusive | authorized narrowed realization |
| `wracać`, `wrócić` | `DOKĄD + (SKĄD)` | `do`/`z` rows labelled realizations | authorized narrowed realization; `source→target` role debt |
| `przyjść` | destination role | event `na` exact; place `do` labelled realization | authorized mixed exact/narrowed policy |
| `przyjechać` | `DOKĄD` | `do`/`na` labelled non-exclusive | authorized narrowed realization |
| `wyjść` | `SKĄD/DOKĄD` | `z/do/na` labelled realizations | authorized narrowed realization; `source→target` role debt |
| `wyjechać` | `SKĄD` | only `z` labelled source realization | authorized narrowed realization; `source→target` role debt |
| `przynosić` | optional generalized source/goal | no concrete source/goal row | unrepresented by policy |
| `zamawiać` | provider/location `GDZIE` | `u` + Genitive labelled non-exclusive provider realization | authorized narrowed realization |
| `pokazywać` | optional `GDZIE` | no Locative/product location row | unrepresented by policy |
| `czytać` | generalized `GDZIE` evidence | no location row | unrepresented by policy |
| `mieszkać` | residence `GDZIE` | `w` + Locative labelled one realization; `na/u` omitted | authorized narrowed realization |
| `umówić się` | appointment `GDZIE` and time boundary | `do` + Genitive venue is labelled realization; time remains unencoded | authorized narrowed realization |
| `dzwonić` | target `DOKĄD` | `do`/`na` target rows labelled narrowed | authorized narrowed realization |
| `zapraszać` | exact `KOGO + na/do`; separate `KOGO + GDZIE` | exact `na/do`; generalized `GDZIE` unconcretized | exact source constructions plus unrepresented policy role |
| `wiedzieć` | source-of-knowledge `SKĄD` | no source complement; no `od/z` inference | unrepresented by policy |
| `uczyć` school sense | `(KOGO) + CZEGO + GDZIE` | learner/subject authored; `GDZIE` omitted | unrepresented by policy |

No unauthorized concretization was found. `KTÓRĘDY` produces no authored concrete row in this corpus. The source-role enum debt is the only structural convention item that must be explicitly accepted or resolved before Phase 4C.

## 11. Lexical/aspect identity audit

The lexical multiword/reflexive inventory is `kłócić się`, `radzić sobie`, `spotykać się`, `spotkać się`, `umówić się`, `cieszyć się`, `martwić się`, and `zgadzać się`. Main predicates in their examples retain the required particle. `radzić` examples do not become `radzić sobie`; `uczyć` examples remain non-reflexive and do not become `uczyć się`; `życzyć` examples do not become `życzyć sobie`. The occurrence of embedded `sobie` in `martwić się`'s “jak sobie poradzimy” clause belongs to the embedded coping predicate, not the main lemma.

All 68 `aspect` values match the frozen identities. A conservative lexical/morphological read found no confidently detectable analogous aspect substitution. In particular, the Batch 6 corrections remain live: four `polecać` directive examples use present `poleca`, and `radzić/dative-direct-speech-advice` uses present `radzę`; no `polecił` or `poradziła` remains in those candidate examples.

Independent full-record aspect families are `wracać/wrócić`, `kończyć/skończyć`, `kupować/kupić`, `pisać/napisać`, `spotykać się/spotkać się`, `oglądać/obejrzeć`, `dawać/dać`, and `brać/wziąć`. Their records keep independent evidence pointers and no syntax inheritance was mechanically detected.

## 12. Metadata-only boundary audit

Exactly two collapsed identities exist:

- Full `zacząć` with metadata-only `zaczynać`.
- Full `czytać` with metadata-only `przeczytać`.

`zaczynać` and `przeczytać` are absent from the 68 canonical lemma names, have no candidate content, and are represented only inside their owners' private `metadataAspectPartner` objects. The two `require-empty-candidate-content` rules resolve and pass. No production ID or inherited partner syntax is present. The 68 full-pattern records exactly match the intended frozen set.

## 13. requiredLexicalItems audit

Only `brać` and `wziąć` possess `requiredLexicalItems`, exactly `['udział']` in each case. Their participation patterns and examples use `udział` (`Biorę udział…`, `Wziąłem udział…`), and the two explanation-material guards pass. No other lemma has `requiredLexicalItems`; the validator rejects unauthorized use.

## 14. Requiredness/all-optional audit

Required-complement count by pattern: 0 required = 6; 1 required = 197; 2 required = 21. Every pattern has a non-empty complement array.

The six all-optional patterns are:

| Lemma/pattern | Optional shape | Example realizes |
|---|---|---|
| `umówić się/z-instrumental-partner-na-accusative-event` | optional partner + optional event | both |
| `gotować/accusative-dish-dative-beneficiary` | optional dish + optional beneficiary | both |
| `pasować/do-genitive-fit-target` | optional fit target | target |
| `pasować/na-accusative-fitted-object` | optional fitted object | object |
| `pasować/dative-expectation-holder` | optional experiencer | experiencer |
| `jeść/accusative-food-instrumental-implement` | optional food + optional implement | both |

All six examples realize the optional structure as their batch policy required. Mechanically comparable requiredness differences were inspected. The material cross-batch asymmetry is B4 `napisać`: Dative is required in its Dative+clause rows while B4 `pisać` and B5 `powiedzieć` use optional Dative there; this is explicitly frozen and guarded rather than accidental normalization. Other differences (`pasować` fit, `gotować`, `jeść`, transfer/beneficiary rows, and `pozwalać`/`radzić`/`życzyć`) track distinct source schemas or meanings. No requiredness contradiction is mechanically provable.

## 15. CEFR/status/priority/register outlier audit

The four recognition-only rows are:

| Lemma/pattern | CEFR | Priority | Committed rationale |
|---|---|---|---|
| `zapominać/czy-dependent-clause` | B1/— | common | embedded yes/no question considered comprehension-first |
| `pozwalać/zeby-enabling` | B1/— | common | abstract/inanimate subject plus `żeby` clause |
| `wymagać/situation-requires-content/zeby-clause` | B1/— | common | abstract situation subject plus `żeby` clause |
| `kłócić się/czy-dependent-clause` | B1/— | common | embedded yes/no uncertainty clause |

The two `czy` rows' status may need reevaluation after clauseKind adjudication; no status is changed here. Reports and staging otherwise agree on 220/4.

All registers are `neutral`, so there is no register outlier. Documented CEFR/priority edges still present include `wiedzieć` Accusative at A1/A2; `kochać` idea/place and strong-liking at A2/A2 common; `korzystać` identical structures split core/common; and `uczyć` `o` + Locative at A2/A2 common. A purely mechanical sibling inversion scan also finds easier/common rows against harder/core rows in `pisać` and `napisać` (`do-genitive-accusative-content` versus `dative-topic`) and `pasować` (`na-accusative-fitted-object` versus the B1-production evaluator/reference row). Priority is a usage measure, not a difficulty order, so these are review prompts rather than defects.

## 16. Example/provenance audit

There are 224 unique Polish examples and 219 unique English examples. Exact Polish duplicates: 0; normalized Polish duplicates: 0; cross-batch Polish duplicates: 0. Five English strings each occur twice because distinct Polish Dative and `do` + Genitive recipient variants collapse in translation: two `pisać`, two `napisać`, and one `powiedzieć` pair. This is informational.

The four reuse records are `iść/do-genitive-destination` from card `a1-first-verbs-006.ex`; `wymagać/genitive-required-content` from `b1-healthy-lifestyle-018.ex`; and `kupić` Dative/`dla` beneficiary rows from `a2-nature-animals-016.ex` and `a2-holidays-traditions-007.ex`. Each has complete `kind`, `id`, and `field` source metadata and resolves byte-identically under the historical tests. Counts are 4 repository reuse and 220 editorial generated.

All 224 `candidateExampleKey` values are `primary`, which is exact repetition by authorized parent scope rather than near-identical wording leakage. No example key incorporates its sentence wording.

## 17. Report consistency audit

Batch authoring/risk report counts match the live historical projections: B1 12/25/25, B2 12/28/28, B3 14/30/30, B4 13/41/41, B5 15/40/40, B6 16/37/37, B7 13/23/23. Their cumulative counts reconcile to 95/224/224. Batch active/recognition counts, priority correction, provenance counts, guard increments, final 72-rule total, all seven digest locks, and all four matrix SHA locks agree with staging/tests.

Superseded values are explicitly labelled in their reports and were not treated as current claims. Historical start-of-batch future-empty/rule/test totals are temporally scoped and reconcile to their batch boundaries. No unlabelled current false count, digest, matrix SHA, or guard-total statement was found.

The committed B7 risk report says independent B7 review was outstanding at that commit boundary. No later B7 independent linguistic review artifact exists in the repository; therefore this audit relies on the committed B7 authoring/risk reports plus live staging for the equivalent carry-forward checks in section 19.

## 18. Architecture-boundary audit

The Phase 4B diff from the recorded starting integration baseline contains only private staging, Phase 4B reports, validator/tests, and test fixtures. Production/canonical/runtime/audio files have no Phase 4B diff. Recursive scans find no production stable ID field or `vp-*` value in candidate content; the four `id` fields that do occur are explicitly allowed provenance source IDs.

No stable-ID allocation, runtime projection, new runtime clause kind, runtime schema revision, analytics/telemetry, audio generation, production canonical mutation, or Phase 4C artifact is present. The private staging enum includes the already-authorized private `direct-speech` form; it did not modify the runtime enum or schema.

## 19. Known carry-forward items

All requested B7 non-blocking checks remain present and unadjudicated:

- `musieć` explanation is 40 words and still uses absolutist/meta wording: “always takes” and “add nothing new to learn”. **EDITORIAL REVIEW ITEM**.
- `jeść` explanation is 62 words and combines optionality, case instruction, an example, ellipsis, negation grammar, and a boundary disclaimer. **EDITORIAL REVIEW ITEM**.
- `kochać/strong-liking` gloss order remains `love (doing something)` before `really like`. **EDITORIAL REVIEW ITEM**.
- `uczyć/accusative-person-o-locative-taught-topic` still uses `w innych krajach` as a nominal modifier inside the example for the governed `o zwyczajach` topic. **EDITORIAL REVIEW ITEM**.
- `uczyć/accusative-learner-genitive-school-subject` still uses `dzieci`, whose Nominative/Accusative surface syncretism weakens visible case teaching. **EDITORIAL REVIEW ITEM**.
- `polecać/dative-accusative-action-noun` still has `Trener poleca zawodnikom rozgrzewkę.` / “The coach orders the players to warm up.” Its stronger English directive force and its structural identity with the recommendation row remain unadjudicated. **REVIEW ITEM — LINGUISTIC / EDITORIAL**.

The Batch 6 aspect repairs remain correct, as documented in section 11.

## 20. Consolidated reconciliation queue

| ID | Lemma(s) | Category | Finding | Mechanical evidence | Current state | Severity | Reviewer |
|---|---|---|---|---|---|---|---|
| P8-FR-001 | `zapominać` | clauseKind/source alignment; key freeze | `czy` is narrower than frozen interrogative-dependent evidence; pattern key also embeds `czy` | live `clauseKind: czy`; Phase 3 order 21 `clause:interrogative-dependent`; no later authorization | unadjudicated, digest-pinned | BLOCKING | OPUS |
| P8-FR-002 | `kłócić się` | clauseKind/source alignment; key freeze | `czy` is narrower than frozen interrogative-dependent evidence; pattern key also embeds `czy` | live `clauseKind: czy`; Phase 3 order 27 `clause:interrogative-dependent`; no later authorization | unadjudicated, digest-pinned | BLOCKING | OPUS |
| P8-FR-003 | `wracać`, `wrócić`, `wyjść`, `wyjechać` | role architecture debt | source realizations use `role: target` because locked enum has no `source` | four required `z` + Genitive source rows; risk report calls this closed-model debt | semantics textually preserved; structural role unresolved | BLOCKING | HUMAN |
| P8-FR-004 | early-batch lock layer | regression architecture | current guards/validator cannot detect the two frozen-evidence clauseKind mismatches | validator and all 270 tests pass with both mismatches; B2/B3 digests pin them | regression policy must follow adjudication | BLOCKING | CODEX |
| P8-FR-005 | 12 lemmas in section 7 | semantic ownership | 14 same-lemma cross-meaning signature collisions cannot be mechanically distinguished | 29 rows canonicalize to identical shapes across sibling meanings | keys valid; semantic ownership still review-dependent | REVIEW | OPUS |
| P8-FR-006 | `polecać` | editorial/semantic boundary | A4 English overstates directive force; A4 and recommendation are structurally identical | exact current PL/EN plus identical Accusative + optional Dative signature | unadjudicated | REVIEW | OPUS |
| P8-FR-007 | `wiedzieć` and `z` + Genitive families | cross-batch role convention | `wiedzieć` Accusative uses `content` while comparable direct objects use `object`; same `z` form spans `target/topic/object` | role inventory in section 8 | no mechanical contradiction | REVIEW | OPUS |
| P8-FR-008 | `musieć` | editorial wording | explanation is absolutist/meta | 40 words; “always takes”; “add nothing new to learn” | present | REVIEW | OPUS |
| P8-FR-009 | `jeść` | editorial concision | explanation is unusually long and multi-purpose | 62-word live explanation | present | REVIEW | OPUS |
| P8-FR-010 | `kochać` | gloss ordering | strong-liking gloss order may foreground stronger English “love” | live gloss order | present | REVIEW | OPUS |
| P8-FR-011 | `uczyć` | example transparency | `o` + Locative example also contains surface `w` + Locative nominal modifier | `o zwyczajach w innych krajach` | present | REVIEW | OPUS |
| P8-FR-012 | `uczyć` | example case transparency | school example's `dzieci` is Nom/Acc syncretic | `Pani Nowak uczy dzieci matematyki.` | present | REVIEW | OPUS |
| P8-FR-013 | `pisać`, `napisać`, `pasować` | CEFR/priority outlier | three easier/common versus harder/core sibling comparisons | mechanical scan in section 15 | usage priority may justify | REVIEW | OPUS |
| P8-FR-014 | `pisać`, `napisać`, `powiedzieć` | English duplication | five pairs of exact duplicate English examples obscure distinct Polish recipient forms | 224 PL unique versus 219 EN unique | structurally valid | INFORMATIONAL | NONE |
| P8-FR-015 | all 68 | candidate-key scoping | raw global reuse is extensive but parent composites are unique | 93/159/1 globally unique raw M/P/E values; zero sibling collision | authorized by schema lock | INFORMATIONAL | NONE |

No item is duplicated: key-freeze impact is attached to its underlying semantic/architecture finding.

## 21. Candidate-key freeze readiness

Conclusion **C: mechanically valid but semantic review still required**. The set has no exact format, ownership, or collision defect under its frozen parent scopes. It is not ready for human freeze because P8-FR-001 and P8-FR-002 directly affect two pattern keys, and P8-FR-005 covers structurally indistinguishable semantic ownership. Keys are not frozen by this audit.

## 22. Test results

| Check | Result |
|---|---|
| `python3 validate_priority8_staging.py` | PASS: 4B7 revision 8; 68 lemmas; 21 constrained records; 12 global constraints |
| Exact 11 Phase 4B suites together via `python3 -m unittest` | 270 tests in 71.325s; OK |
| Batch digests B1-B7 | all exact |
| Matrix SHA locks B4-B7 | all exact |
| `git diff --check` | to be rerun at commit gate |
| `git status --short` | to be rerun at commit gate; intended sole path is this report |
| `git remote -v` | zero remotes |
| `git config --get push.default` | `nothing` |
| Blocking pre-push hook | executable and fail-closed |

This report intentionally records blockers rather than silently fixing them. If final diff checks retain exactly this one added path, the validator and 270-test result remain valid, and the report itself passes review, the requested local commit gate is satisfied.
