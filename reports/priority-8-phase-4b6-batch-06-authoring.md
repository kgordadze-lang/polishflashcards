# Priority 8 Phase 4B6 — Batch 06 authoring

## Scope and starting endpoint

This is an **implementation** task against an already independently-reviewed
and frozen schema matrix. No Phase 3 evidence was reinterpreted, no fresh
linguistic research was performed, and the schema matrix itself was not
modified. **The frozen matrix was implemented, not linguistically
reinterpreted.**

Starting endpoint (verified before any edit):

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `b3aae02ece5ce57ffb74420f95cb030c9baa8040`
- tree `28d746c180d52e432015ed3f6f668400d562632d`
- parent `3e5a7db2fbeaf7bbfb17b54bbe5d2ef9a8feb6ab`
- subject `Clarify Priority 8 Phase 4B6 guard limitations`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook
- staging SHA-256 before authoring:
  `fbc25a832c7bd50d775117c877d1876eaa213545785f881585ef5819169c4442`
- guard registry SHA-256 before authoring:
  `4cd62f335c8af96f655de49d6f1ed58acd8dba8a3f4eddb461c1c3b7dc6c8f2f`

Binding authoring plan: `reports/priority-8-phase-4b6-schema-matrix.md`,
independently reviewed (`APPROVE WITH CORRECTIONS`) and corrected to
`APPROVE`. SHA-256 before this task and after:
`72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c` —
**unchanged**.

Recomputed pre-authoring staging state: `phaseStep 4B5`, `stagingRevision 6`,
49 authored / 66 meanings / 164 patterns / 164 examples / 19 future-empty.
Guard registry: `registryVersion 2`, 36 rules. Scoped test baseline: 219
tests. Approved Batch 5 digest confirmed:
`d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951`.

## 10/16/37 reconciliation

Every count was independently re-derived from the frozen matrix's §17 before
any content was written, then re-verified against the authored staging file
after writing:

| Lemma | Meanings | Patterns | Examples |
|---|---:|---:|---:|
| `gotować` | 1 | 1 | 1 |
| `rezerwować` | 1 | 2 | 2 |
| `cieszyć się` | 1 | 4 | 4 |
| `martwić się` | 1 | 4 | 4 |
| `zgadzać się` | 2 | 7 | 7 |
| `zapraszać` | 1 | 2 | 2 |
| `polecać` | 2 | 5 | 5 |
| `radzić` | 1 | 5 | 5 |
| `pasować` | 4 | 5 | 5 |
| `móc` | 2 | 2 | 2 |
| **Total** | **16** | **37** | **37** |

37/37 frozen schema alternatives implemented exactly as declared:
`meaningKeyProposal`, `schemaKeyProposal`, `relationType`, complement
requiredness/optionality, roles, and `clauseKind` were all taken **verbatim**
from the matrix's §4. Zero extra rows, zero missing rows, zero renamed keys.

## Per-lemma counts

See table above; identical to the frozen matrix's §17 table
(`gotować` 1/1, `rezerwować` 1/2, `cieszyć się` 1/4, `martwić się` 1/4,
`zgadzać się` 2/7, `zapraszać` 1/2, `polecać` 2/5, `radzić` 1/5,
`pasować` 4/5, `móc` 2/2 — sums to 16/37).

## Candidate keys

16/16 meaning keys and 37/37 pattern keys are the exact `meaningKeyProposal`
and `schemaKeyProposal` strings from the frozen matrix, copied verbatim — none
renamed or "improved". All 37 `candidateExampleKey` values are `"primary"`,
following the locked B1A convention (uniqueness is scoped to
`(lemma, meaningKeyRef, patternKeyRef)`, and every pattern has exactly one
example, so `"primary"` is unambiguous throughout). No key contains a
batch/order/source ID or a production `vp-*` ID; verified mechanically
(`tests/test_priority8_phase4b6_batch06.py::test_no_production_ids_or_id_fields_exist`
and `::test_candidate_keys_match_the_frozen_matrix_proposals`).

## CEFR / teaching-status decisions

All 37 patterns were independently adjudicated against the Batch 1-5
precedent corpus (no quota, no automatic downgrade, no automatic
active-production default taken without checking):

- **Simple case/prepositional alternatives** (the "anchor" realization of a
  meaning): `A1-A2` recognition, `A1-A2` production, `active-production`,
  `core` priority — matching the `dawać`/`zapraszać`/`umówić się` precedent.
- **`ze`/`zeby`/direct-speech clause alternatives**: `A2` recognition, `B1`
  production, `active-production`, `common` priority — matching the
  `dzwonić`/`pisać`/`powiedzieć`/`umówić się` precedent exactly.
- **`interrogative` clause alternatives**: `A2` recognition, `A2` production,
  `active-production`, `common` priority — matching the
  `rozumieć`/`umówić się` precedent (embedded wh-questions are treated as no
  more marked than the case alternatives, unlike `ze`/`zeby`).
- **Infinitive-only modal patterns** (`móc`): `A1`/`A1`, `active-production`,
  `core`, matching the Phase 2 `A1` hypothesis and the `chcieć`/`zacząć`
  precedent for bare-infinitive constructions.
- **Optional-Dative + infinitive patterns** (`polecać`, `radzić`): `A2`/`B1`,
  `active-production`, `common`, matching the `pozwalać` Dative+infinitive
  precedent exactly.

**36 active-production, 0 recognition-only.** Recognition-only was
independently considered and rejected for every high-attention row named in
the brief:

- `cieszyć się` Instrumental (`cieszę się zaufaniem zespołu`) — real,
  WSJP-evidenced, and has natural everyday realizations
  (`cieszyć się Twoim towarzystwem`) alongside more formal ones
  (`cieszyć się popularnością`); no genuine register-based case for
  suppression, so kept `active-production` at `B1` production reflecting
  its somewhat higher register rather than downgraded to recognition-only.
- `martwić się` Instrumental/interrogative — both are everyday, high-frequency
  worry constructions (`martwię się twoim zdrowiem`, `martwię się, jak sobie
  poradzimy`); no case for suppression.
- `zgadzać się` direct-speech rows (both meanings) — short spoken-reply
  constructions are extremely common; both kept `active-production`.
- `polecać` instruction gerund/action-noun row — this is a CEFR/status
  question logically independent of the identical-shape/meaning-ownership
  issue documented in §G below; on its own communicative merits it is a
  common, useful construction and was kept `active-production`.
- `radzić` direct-speech/interrogative — both are natural, frequent advice
  constructions.
- `pasować` typicality and expectation-suitability — expectation-suitability
  (`ten termin mi nie pasuje`) is extremely frequent in everyday scheduling
  talk and was set `A2`/`A2` `core`; typicality (`ten kolor mi do ciebie nie
  pasuje`) is somewhat more evaluative but still a natural, commonly produced
  construction, kept `active-production` at `B1` production.
- `móc`'s duplicate-shape pair — both rows are basic, high-frequency modal
  constructions; there is no precedent anywhere in the corpus for downgrading
  a lemma's most central infinitive pattern, and doing so here would not
  address the identical-shape issue (that is a `relationType`/meaning-key
  question, not a CEFR question) — kept `active-production` `A1`/`A1` for
  both, matching the Phase 2 `A1` hypothesis for `móc`.

No pattern was marked `recognition-only` to hide a schema concern. Usage
`priority` follows the established convention: the single/anchor realization
of each meaning is `core`; alternative realizations are `common`. `register`
is `neutral` throughout, matching every currently authored pattern in the
corpus (no `formal`/`informal` register has ever been used in Batches 1-5).

## Example provenance

37 examples, all classified `editorial-generated`, 0 `repository-reuse`.

**Quiet-reuse coverage — both layers, both complete, zero collisions:**

- **Layer A (indexed product corpus).** `priority7_tooling.repository_index_from_root`
  loaded through `validate_content.load_source_corpus` — 1665 entities,
  `index.issues == []`. Every one of the 37 generated Polish sentences was
  checked against every `card.pl`, `card.ex`, `drill.prompt`, and
  `drill.answer` field in that index. Zero exact matches.
- **Layer B (broader supplemental raw-text scan).** A substring scan of all
  37 Polish sentences against 190 raw repository files: every `data-*.js`
  and `pp-*.js` source file, every top-level `*.json` file, every
  `editorial/*.json` file, and every `reports/*.md` file. Zero exact
  substring matches anywhere.

This coverage is reported honestly as complete for both layers as scoped
(indexed product corpus + a broad raw-text sweep across every JS/JSON/MD
file in the repository root and its `editorial/`/`reports/` subdirectories);
it does not claim to have scanned binary or unlisted file types, none of
which exist in this repository for prose content.

## 21 guards

All 21 Batch 6 guard rules from the frozen matrix's §14 (refs A-U) were
implemented **verbatim** — exact `ruleId`, exact `kind`, exact
`allowedSignatures`/`meaningShapes`/`signature`/`lexicalItems` content, no
renaming, no 22nd rule added:

`p8-4b-gotowac-exact-pattern-shapes`,
`p8-4b-rezerwowac-exact-pattern-shapes`,
`p8-4b-rezerwowac-authorized-preposition-cases`,
`p8-4b-cieszyc-sie-lexical-identity`,
`p8-4b-cieszyc-sie-exact-pattern-shapes`,
`p8-4b-cieszyc-sie-authorized-preposition-cases`,
`p8-4b-martwic-sie-lexical-identity`,
`p8-4b-martwic-sie-exact-pattern-shapes`,
`p8-4b-martwic-sie-authorized-preposition-cases`,
`p8-4b-zgadzac-sie-lexical-identity`,
`p8-4b-zgadzac-sie-exact-pattern-shapes`,
`p8-4b-zgadzac-sie-authorized-preposition-cases`,
`p8-4b-zapraszac-exact-pattern-shapes`,
`p8-4b-zapraszac-authorized-preposition-cases`,
`p8-4b-polecac-exact-pattern-shapes`,
`p8-4b-radzic-exact-pattern-shapes`,
`p8-4b-radzic-no-z-instrumental-coping`,
`p8-4b-pasowac-exact-pattern-shapes`,
`p8-4b-pasowac-authorized-preposition-cases`,
`p8-4b-moc-exact-pattern-shapes`,
`p8-4b-moc-no-question-clause`.

`tests/test_priority8_phase4b_authoring_guards.py` (the interpreter) was
**not** modified. `registryVersion` remains `2`. Registry rule count:
36 existing + 21 Batch 6 = **57 total**, confirmed both by direct count and
by `validate_rule_registry` accepting the merged registry with zero
configuration errors.

## Mutation results

Using in-memory deep copies only (staging and guard-registry files verified
byte-identical before and after every probe), 25 structural mutations were
attempted against the clean, guard-passing content:

**24 caught**, each by the correct rule (`require-exact-pattern-shapes` for
every shape/cardinality/meaning-merger mutation, `allow-only-preposition-case-signatures`
for every unauthorized-preposition mutation, `require-lexical-identity` for
every `się`-stripping mutation, `forbid-complement-match` for the `radzić`
z+Instrumental injection and the `móc` `czy`-complement injection). Full
per-mutation results are in the risk review, §17.

**1 expected non-enforceable semantic limitation** (not a failed guard):
swapping `polecać`'s A4 (`dative-accusative-action-noun`,
`directive-instruction`) and B1 (`dative-accusative-recommended-item`,
`recommendation`) meaning ownership produces **zero** guard issues, because
the two rows are structurally identical — exactly as the frozen matrix's
§14.2 item 5 documents. Reported as `EXPECTED NON-ENFORCEABLE SEMANTIC
LIMITATION`, per the frozen matrix's own classification, not as a defect.

Two additional non-guard structural controls were independently exercised
and confirmed:

- `radzić` + injected `requiredLexicalItems: ["sobie"]` is rejected by the
  **validator** (`requiredLexicalItems is allowed only on brać and wziąć`),
  not by a guard rule — the schema itself forecloses this path.
- `pasować` sense-5 with `relationType` forced to `subject-experiencer` is
  rejected by the **validator**
  (`subject-experiencer requires subject and experiencer roles`), confirming
  the frozen §5.9 architecture decision is enforced at the schema layer, not
  merely by convention.

## Batch 6 digest

```
4315720bc2ca58424f668d0aec4448c0eb7716bc8db682b7b439c2dd22f64a96
```

B1-B5 independently recomputed and confirmed **unchanged**:

- B1 `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e`
- B2 `dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8`
- B3 `8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb`
- B4 `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2`
- B5 `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951`

## Cumulative state

`phaseStep = 4B6`, `stagingRevision = 7`. Cumulative content:

| Quantity | Before | Batch 6 | After |
|---|---:|---:|---:|
| authored lemmas | 49 | +10 | **59** |
| meanings | 66 | +16 | **82** |
| patterns | 164 | +37 | **201** |
| examples | 164 | +37 | **201** |
| future-empty lemmas | 19 | -10 | **9** |

All 68 records remain `stagingReviewStatus = draft`.

## Tests

`python3 validate_priority8_staging.py`:
`PASS: Priority 8 4B6 staging revision 7 is read-only valid (68 lemmas, 21
constrained records, 12 global constraints).`

Ten scoped suites, individually and together (see full counts in the risk
review, §19): **243 tests total (219 pre-Batch-6 baseline + 24 new
`test_priority8_phase4b6_batch06.py`), all passing.**

`git diff --check` clean. Exactly six changed paths (see completion report).
