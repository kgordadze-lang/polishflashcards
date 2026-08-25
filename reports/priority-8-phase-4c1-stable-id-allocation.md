# Priority 8 Phase 4C1 — stable-ID allocation and private ID map

## 1. Starting endpoint

Phase 4C1 began only after every required repository and safety gate matched.

| Check | Required and observed |
|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4C SAFE` |
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `95a6ddcb1a283533f706b7fb7f01fa2f10aa0167` |
| Tree | `a493a141880ca7da869e12869106246cb92d780b` |
| Parent | `e30cd0cff83937f9b8c76386a7ff984b9c719844` |
| Subject | `Priority 8 Phase 4C0 record human architecture decisions` |
| Worktree | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |

HD-4C-01 and HD-4C-02 were both human-approved at this endpoint. This phase does not
implement either schema consequence.

## 2. Frozen identity source

Allocation consumes
`editorial/priority-8-phase4-candidate-key-freeze.json` and independently projects the
same hierarchy from `editorial/priority-8-phase4-staging.json`. The two projections are
exactly equal.

The manifest is `freezeSchemaVersion = 1`, `status = frozen`, and its canonical hierarchy
recomputes to:

`candidateKeyFreezeDigest = 0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27`

The hierarchy remains 68 lemmas, 95 meanings, 224 patterns, 224 examples and 543 frozen
candidate keys. The manifest and staging files remain byte-identical to their starting
versions.

## 3. Allocator archaeology and reuse

`priority8_phase4c1_stable_ids.py` delegates every allocation to the existing locked
functions in `priority7_tooling.py`:

- `normalize_canonical_lemma`
- `allocate_lemma_id`
- `allocate_meaning_id`
- `allocate_pattern_id`
- `allocate_example_id`
- `pattern_readable_stem`
- the existing `ID_RES` namespace syntax contracts

No second stable-ID hash implementation was added. The Phase 4C1 wrapper computes the
candidate-freeze SHA-256 digest, but all stable-ID hashing remains owned by the existing
allocator.

The existing frozen allocation machinery was also inspected: `_allocation_for_entity`,
`_expected_allocation_id`, allocation-registry validation, `freeze_editorial`, and the
append-only tombstone checks. The private map follows those lifecycle rules without
modifying or invoking canonical release projection.

## 4. Exact identity and seed contract

The locked contract is unchanged:

| Kind | Frozen identity | Exact seed |
|---|---|---|
| Lemma | normalized canonical lemma | `v1\|lemma\|<normalized-canonical-lemma>` |
| Meaning | owning lemma ID + `candidateMeaningKey` | `v1\|meaning\|<lemma-id>\|<meaning-key>` |
| Pattern | owning meaning ID + `candidatePatternKey` | `v1\|pattern\|<meaning-id>\|<pattern-key>` |
| Example | owning pattern ID + `candidateExampleKey` | `v1\|example\|<pattern-id>\|<example-key>` |

Inputs use Unicode NFC. Canonical lemmas are trimmed, whitespace-collapsed and lowercased.
Keys remain lowercase ASCII kebab-case. Seeds are UTF-8 without a trailing newline. The
allocator uses SHA-256 truncated to the first 12 lowercase hexadecimal characters. Lemma
readable stems use the existing Polish transliteration and 32-character rule; descendant
readable stems use the stable parent identity exactly as the locked allocator specifies.

Mutable learner-facing wording, complements, roles, CEFR, teaching status, usage,
verification order and later schema fields do not enter any seed. Parent IDs do enter
child seeds, so reparenting changes identity.

## 5. Released-ID reproduction

Before any new ID was persisted, the current released corpus was independently walked and
every identity was reproduced through the locked allocator.

| Namespace | Released | Reproduced | Mismatch |
|---|---:|---:|---:|
| `vp-l` | 30 | 30 | 0 |
| `vp-m` | 34 | 34 | 0 |
| `vp-p` | 45 | 45 | 0 |
| `vp-e` | 45 | 45 | 0 |
| **Total** | **154** | **154** | **0** |

`content/verb-patterns.json` was not modified. Its starting SHA-256 remains
`889b44aa7f87f25325364188a9283a36b22aa6d5d491fc347bb7be73072ba14d`.

## 6. New allocation and namespace counts

| Namespace | Kind | New allocations |
|---|---|---:|
| `vp-l` | lemma | 68 |
| `vp-m` | meaning | 95 |
| `vp-p` | pattern | 224 |
| `vp-e` | example | 224 |
| `vp-x` | exercise | 0 |
| **Total** |  | **611** |

All 68 lemma identities map once. All 543 frozen keyed identities map once. No candidate
key is used as a production ID.

## 7. Determinism

The complete allocation was run twice from independently loaded source documents. The
serialized results were byte-identical. The persisted private map was then read again,
validated and compared with a third regeneration; it was also byte-identical.

The persisted map SHA-256 at this endpoint is
`20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d`.
There is no timestamp, randomness, counter, array-index identity input or environment
dependency in the ID-bearing projection.

## 8. Collision audit

| Audit | Result |
|---|---:|
| Duplicate identity paths | 0 |
| Duplicate seeds | 0 |
| New ↔ new ID collisions | 0 |
| New ↔ released ID collisions | 0 |
| Namespace mismatches | 0 |
| Same identity receiving two IDs | 0 |
| One ID belonging to two identities | 0 |
| Released + prospective union | **765** |

The released set has 154 unique IDs and the prospective set has 611 unique IDs. Their
intersection is empty.

## 9. Private stable-ID map

Path: `editorial/priority-8-phase4c-stable-id-map.json`.

| Field | Value |
|---|---|
| `stableIdMapSchemaVersion` | `1` |
| `artifactStatus` | `priority-8-phase-4c-id-map-nonproduction` |
| `sourceCandidateKeyFreezeDigest` | exact frozen digest above |
| `allocationRevision` | `1` |
| `allocations` | 611 deterministic rows |
| `tombstones` | empty; none warranted |

Each allocation row retains `kind`, the complete hierarchical identity
(`canonicalLemma`, `meaningKey`, `patternKey`, `exampleKey` with unused levels null), the
stable `id`, `seedVersion`, and lifecycle `status`. Parent IDs are mechanically resolved
from the retained hierarchy and validated before any child ID is accepted.

This artifact is private governance/editorial data. Runtime, service-worker and canonical
consumers do not reference it, it is not precached, and it is not a canonical or runtime
source of truth.

Before canonical promotion, this map is the durable join between the frozen candidate
identity and its prospective production ID. After promotion, the released canonical
corpus is authoritative. The checker compares any overlapping released identity and
stops if its canonical ID disagrees with the map; it never rewrites canonical IDs.

## 10. Tombstone and no-recycle result

No identity is retired in Phase 4C1, so no tombstone was invented. All 611 rows are
`active` and the tombstone registry is empty.

The schema and checker nevertheless preserve the frozen lifecycle contract: a tombstoned
allocation row must remain present; it must have exactly one same-ID tombstone carrying
the original kind and derived former parent; retirement revision and reason are required;
replacement IDs must be unique, non-self, active and same-kind; and an active allocation
cannot coexist with a tombstone. Mutation tests prove valid retirement representation and
reject resurrection, reuse, duplicate ownership and dangling/invalid lifecycle states.

## 11. Metadata-only exclusions and source semantics

`zaczynać` and `przeczytać` remain metadata-only. Both still exist in private staging
metadata, neither appears as an allocated top-level lemma, and both receive zero meaning,
pattern or example IDs.

The seven source/provider identities are seeded only from their already-frozen semantic
keys and ownership. An in-memory mutation from the temporary Phase 4B `target` role to the
approved future `source` role produces the identical map. Therefore the temporary role
does not contaminate stable identity. `source` itself is not implemented in this phase.

## 12. Loss and allocation accounting

| Ledger item | Input | Allocation result |
|---|---:|---:|
| Full-pattern lemma identities | 68 | 68 |
| Meaning keys | 95 | 95 |
| Pattern keys | 224 | 224 |
| Example keys | 224 | 224 |
| **Frozen keyed identities** | **543** | **543** |
| **Total prospective identities** | **611** | **611** |
| Metadata-only identities | 2 | 0 |
| Existing released IDs | 154 | 154 preserved |
| Future promoted identity universe | — | **765** |

No frozen identity is missing, duplicated, silently merged or promoted as content.

## 13. Canonical, runtime, schema and audio immutability

Phase 4C1 makes zero change to the released corpus, runtime JavaScript, `pp-*.js`, audio,
audio manifest, service worker, `index.html`, `APP_VERSION`, `formatVersion`,
`patternDataRevision`, runtime loader, renderer, activities or production schema fields.

It does not implement role `source`, `clauseKind: direct-speech`, or
`requiredLexicalItems`. It does not insert the 68 lemmas into canonical data and does not
generate audio.

## 14. Tests

The pre-implementation gate passed:

- `python3 validate_priority8_staging.py`: PASS;
- the twelve existing Phase 4B/freeze suites: 297 tests, OK;
- independent released-ID reproduction: 154/154, zero mismatch.

The dedicated suite `tests/test_priority8_phase4c1_stable_ids.py` contains 27 tests. It
covers the exact freeze digest and hierarchy, released reproduction, allocation and
namespace counts, union/collisions, independent determinism, persisted regeneration,
ownership, metadata-only and `vp-x` exclusions, source-role independence, wording
stability, key rename and reparent rejection, released-ID mutation, tombstone/no-recycle,
identity/ID bijection, complete 68 + 543 accounting, private-map isolation, and locked
allocator reuse.

Post-implementation results are: staging validator PASS; existing suites 297 tests, OK;
dedicated suite 27 tests, OK; combined run 324 tests, OK.

## 15. Changed-path boundary

The implementation is confined to:

- `editorial/priority-8-phase4c-stable-id-map.json`;
- `priority8_phase4c1_stable_ids.py`;
- `tests/test_priority8_phase4c1_stable_ids.py`;
- this report.

No existing production, runtime, canonical, staging, freeze-manifest, schema, version or
audio path changed.

## 16. Phase 4C2 handoff

Phase 4C2 may begin only from this Phase 4C1 mapping after independent verification.
Under the frozen architecture its scope is limited to implementing role `source`,
`clauseKind: direct-speech`, optional structural `requiredLexicalItems`, and
`formatVersion` 1 → 2 with Python/JavaScript schema parity and table-driven runtime
support. The released 30-lemma corpus must still project byte-identically at revision 2.
The new 68 lemmas remain unpromoted in Phase 4C2.

**READY FOR INDEPENDENT PHASE 4C1 VERIFICATION BEFORE PHASE 4C2**
