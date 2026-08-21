# Priority 8 Phase 4B0 - Private Staging Setup

## Status and boundary

Phase 4B0 establishes private authoring infrastructure only. No linguistic
authoring, production ID allocation, canonical promotion, runtime projection,
schema work, audio work, or activity activation is included.

The verified starting integration baseline is:

- HEAD: `2e90510f2a91bca2297781208bce3c94648e4427`
- tree: `f86d876fce59f4042fa3bf9a306720914ed79b9d`

The private artifact is `editorial/priority-8-phase4-staging.json`. It is not an
input to `freeze_editorial`, `verified_runtime_from_frozen`, the canonical
editorial corpus, or public runtime generation.

## Frozen sources

The exact full-pattern intake comes from rows with
`full_pattern_in_phase4=yes` in
`reports/priority-8-phase-3b-final-lemma-freeze.csv`, cross-checked against the
ordered list in `reports/priority-8-phase-3b-phase4-handoff.md`.

The staging envelope stores path plus SHA-256 identity for:

| Source | SHA-256 |
|---|---|
| `reports/priority-8-phase-3b-final-lemma-freeze.csv` | `c54da66e854f0d1b4014b783e2493c150ad1e3c94941cb481b3a341d8b3f6375` |
| `reports/priority-8-phase-3b-phase4-handoff.md` | `5fd32f1f8fd11028c62d5ed68c91ee3b5670cc9b6f87ec14295e8f3266a4a9eb` |
| `reports/priority-8-phase-4a2-2-policy-freeze.md` | `149c684feba063742b73a5a3be2ec7379b6d7be83640e2114acc3c81c3c83119` |
| `reports/priority-8-phase-4a2-2-staging-contract.md` | `5a041f504446490c7f782278c2853c17b01bbedaefcab55420c372909f61191c` |

Aspect and evidence traceability are recovered from the exact matching row in
the seven `reports/priority-8-phase-3-batch-*-verification.csv` files. Every
staging record stores that CSV path, verification order, primary source key,
and primary source locator. No aspect value was inferred from general Polish
knowledge.

## Exact intake and order

The Phase 3B freeze contains 70 researched identities. Exactly 68 rows are
marked for full-pattern work. Orders 17 (`zaczynać`) and 37 (`przeczytać`) are
the only metadata-only rows and are excluded from the `lemmas` array.

The validator derives the expected sequence from the authoritative freeze CSV,
joins it to all 70 Phase 3 verification rows by verification order, and demands
exact sequence equality. The resulting staging sequence has:

- count: 68;
- first record: order 1, `pracować`;
- last record: order 70, `uczyć`;
- unique `canonicalLemma` values: 68;
- review status: 68 `draft`, zero other statuses.

The preserved orders are traceability metadata only and are not candidate-key
or stable-ID inputs.

## Staging schema

The deterministic private envelope has:

- `stagingSchemaVersion: 1`;
- `stagingRevision: 1`;
- `priority: 8`;
- `phase: "4B"`;
- `phaseStep: "4B0"`;
- `frozenFullPatternCount: 68`;
- frozen source identities and starting HEAD/tree;
- the private status vocabulary;
- 12 exact global constraints;
- the 68 ordered lemma records.

Each lemma record contains verification order, canonical lemma, exact Phase 3
aspect, Phase 3 disposition, evidence-row pointer, applicable binding
constraints, private staging status, and an explicit `candidateContent` object.
The latter contains empty `meanings`, `patterns`, and `examples` arrays.

Future candidate key field names are `candidateMeaningKey`,
`candidatePatternKey`, and `candidateExampleKey`. The validator applies the
current stable-key lowercase-kebab syntax and per-kind uniqueness checks if a
future fixture introduces them. Phase 4B0 itself rejects all candidate keys and
all non-empty candidate-content collections.

This private schema does not alter `formatVersion`, `SCHEMA_VERSION`,
`CONTENT_MIGRATION_REVISION`, or `patternDataRevision`.

## Constraint mapping

All 21 `compatible with narrowing` rows are attached to their exact lemma with
the exact CSV/handoff text and a pointer to the relevant handoff section.

The 16 `KEEP WITH NARROWING` mappings are:

| Order | Lemma | Frozen handoff section |
|---:|---|---|
| 1 | `pracować` | Sixteen KEEP WITH NARROWING constraints |
| 8 | `wracać` | Sixteen KEEP WITH NARROWING constraints |
| 9 | `wrócić` | Sixteen KEEP WITH NARROWING constraints |
| 10 | `przyjść` | Sixteen KEEP WITH NARROWING constraints |
| 11 | `przyjechać` | Sixteen KEEP WITH NARROWING constraints |
| 12 | `wyjść` | Sixteen KEEP WITH NARROWING constraints |
| 13 | `wyjechać` | Sixteen KEEP WITH NARROWING constraints |
| 14 | `przynosić` | Sixteen KEEP WITH NARROWING constraints |
| 15 | `odpowiadać` | Sixteen KEEP WITH NARROWING constraints |
| 16 | `zamawiać` | Sixteen KEEP WITH NARROWING constraints |
| 21 | `zapominać` | Sixteen KEEP WITH NARROWING constraints |
| 23 | `pozwalać` | Sixteen KEEP WITH NARROWING constraints |
| 24 | `unikać` | Sixteen KEEP WITH NARROWING constraints |
| 48 | `mieszkać` | Sixteen KEEP WITH NARROWING constraints |
| 49 | `umówić się` | Sixteen KEEP WITH NARROWING constraints |
| 50 | `dzwonić` | Sixteen KEEP WITH NARROWING constraints |

The five additional `KEEP VERIFIED` representation mappings are orders 2
`iść`, 3 `chodzić`, 4 `jechać`, 5 `jeździć`, and 7 `dojechać`. Their source
section is `Additional KEEP VERIFIED representation constraints`.

The 12 global constraints are copied exactly and retain item-level pointers to
`Global Phase 4 constraints` in the Phase 3B handoff. They cover generalized
roles versus realizations, sense-specific schemas, alternative schemas,
lexical `się`/`sobie`, required `udział`, independent aspect evidence, no
syntax inheritance, grammar-owned negation Genitive, clause distinctions,
separate lexical identities, rejected Phase 2 hypotheses, and post-approval ID
allocation.

## Metadata-only aspect representation

Exactly two anchor records carry a private `metadataAspectPartner` object:

- `zacząć` -> `zaczynać` (`imperfective`);
- `czytać` -> `przeczytać` (`perfective`).

The partner objects contain only `canonicalLemma` and `aspect`. Neither partner
is a full-pattern record. They carry no ID, meaning, pattern, example, or
syntax. There are zero `aspectPartnerIds` fields.

## Required lexical material

`requiredLexicalItems: ["udział"]` occurs exactly on `brać` and `wziąć`. It is
absent from the other 66 records. The field is a private lemma-level Phase 4B0
checklist guard and does not create a canonical/runtime field.

## Validator behavior

`validate_priority8_staging.py` is read-only and deterministic. It reads the
private JSON and frozen reports, derives the exact intake from CSV sources, and
validates:

- envelope, source identities, and starting baseline;
- exact count, membership, order, uniqueness, aspect, disposition, and evidence
  pointers;
- allowed private statuses and the all-draft Phase 4B0 state;
- exact 21 per-lemma and 12 global constraints;
- exact metadata-only and required-lexical placement;
- empty candidate content;
- future candidate-key syntax and uniqueness;
- recursive production-ID prefixes and production-ID field names.

It imports no canonical generator, allocates no identity, writes no file, and
produces no canonical or runtime JSON.

## Negative-test inventory

`tests/test_priority8_phase4b0_staging.py` proves rejection of:

1. 67 lemma records;
2. 69 records with an unauthorized reserve;
3. wrong order;
4. duplicate lemma;
5. `zaczynać` as a full record;
6. `przeczytać` as a full record;
7. missing metadata partner;
8. wrong metadata partner;
9. metadata partner on the wrong anchor;
10. `vp-l-` recursively;
11. `vp-m-` recursively;
12. `vp-p-` recursively;
13. `vp-e-` recursively;
14. `vp-x-` recursively;
15. production-ID field names;
16. a missing narrowing constraint;
17. a constraint moved to the wrong lemma;
18. missing `udział` on `brać`;
19. missing `udział` on `wziąć`;
20. `udział` on an unrelated lemma;
21. authored candidate meaning;
22. authored candidate pattern;
23. authored candidate example;
24. non-draft Phase 4B0 status;
25. bad starting baseline;
26. malformed future candidate-key syntax;
27. a duplicate future candidate key.

Positive tests validate the real staging file and prove validator non-mutation,
determinism, and unchanged canonical/runtime boundary snapshots.

## Empty-content and ID proof

Mechanical inspection of all 68 records reports:

- candidate meanings: 0;
- candidate patterns: 0;
- candidate examples: 0;
- candidate keys: 0;
- recursively matched production `vp-*` IDs: 0.

Thus Phase 4B0 contains no meaning, pattern, example, learner explanation,
complement decision, CEFR decision, teaching-status decision, candidate key, or
production ID.

## Canonical/runtime boundary proof

The implementation changes only the five Phase 4B0-authorized paths. The test
suite hashes the protected canonical/runtime files before and after invoking
the validator and confirms identical content. It also confirms that the
`content` directory file inventory does not change.

No existing editorial corpus, Priority 7 tooling, runtime data, UI, service
worker, audio manifest, audio generator, audio file, existing test, or frozen
report is modified. Validation completes with `git diff --check` clean and the
authorized changed-path scope exact.
