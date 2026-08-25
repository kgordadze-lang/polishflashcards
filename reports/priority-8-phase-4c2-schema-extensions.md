# Priority 8 Phase 4C2 — canonical schema extensions and formatVersion 2

## 1. Starting endpoint

Phase 4C2 began from the exact independently verified Phase 4C1 endpoint:

| Check | Observed |
|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4C SAFE` |
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `604df149045fb91bbcf35eb54499b0ef490e1e99` |
| Tree | `4c669cd7b8ad61d984f27d925a7d08ca53687026` |
| Subject | `Priority 8 Phase 4C1 allocate stable IDs` |
| Worktree | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |

The live staging/freeze hierarchy remained 68 lemmas, 95 meanings, 224 patterns,
224 examples and 543 frozen candidate keys. The private ID map remained 68 `vp-l`,
95 `vp-m`, 224 `vp-p`, 224 `vp-e`, zero `vp-x`, 611 total. Released production
remained 30/34/45/45 with 154 IDs. The staging validator passed and all thirteen
existing suites passed at 324 tests before implementation.

## 2. Exact approved contract

This phase implements exactly four contract changes:

1. role `source`;
2. clause kind `direct-speech`;
3. optional structural pattern field `requiredLexicalItems`;
4. Verb Patterns `formatVersion` 1 → 2.

No existing enum value or field was removed or renamed. In particular, `czy` remains
legal. No Priority 8 candidate content was promoted.

## 3. Changed production and schema paths

| Path | Reason |
|---|---|
| `content/verb-patterns.json` | `formatVersion` only, 1 → 2 |
| `priority7_tooling.py` | Python schema enums, exact format contract, lexical-item validation, runtime projection, review scope and frozen-structure support |
| `validate_priority8_staging.py` | role-vocabulary parity only; direct speech was already legal |
| `pp-verb-patterns.js` | matching runtime enums/version, source phrase, direct-speech token, closed-field validation and generic headline rendering |
| `tests/test_priority8_phase4c2_schema_extensions.py` | dedicated 22-test Phase 4C2 contract suite |
| `tests/test_priority8_phase4c1_stable_ids.py` | replace a phase-local whole-file hash lock with frozen-input hashes plus a hash over the unchanged allocator functions; all 27 Phase 4C1 tests remain present |
| this report | implementation and handoff evidence |

The Phase 4C1 test correction is necessary because its former whole-file hashes pinned
the two files this approved phase was explicitly required to change. The replacement is
stricter about the invariant Phase 4C1 actually owns: frozen identity inputs remain
byte-pinned and the locked allocator function source remains byte-pinned.

## 4. Source role implementation

Python canonical/runtime and staging role vocabularies gain exactly `source`.
JavaScript gains the same value and the approved phrase **“where it comes from”**.
`source` is not added to `ANIMATE_ROLES`; generic Genitive rendering therefore remains
inanimate by default. A synthetic `od` + Genitive fixture proves the generic question is
`od czego?`, while the existing `questionOverridePl: ["kogo?"]` mechanism produces
`od kogo?` without any lemma-specific branch. No released `target` row changes.

## 5. Direct-speech implementation

Python and JavaScript clause vocabularies gain the exact token `direct-speech`.
`CLAUSE_TOKENS` maps it to `„…”`. The existing generic clause paths produce headline
token `„…”`, chip `+ „…” · Clause`, the no-case bucket and searchable `„…”` text. Tests
prove it stays distinct from `ze`, `zeby`, `interrogative` and retained `czy`.

## 6. requiredLexicalItems implementation

`requiredLexicalItems` is optional at pattern level in both the private canonical and
public runtime closed schemas. When present it must be an ordered array of 1–4 unique,
exact lowercase NFC Polish words. Non-arrays, empty arrays, non-string/nested items,
blank or padded strings, uppercase values, duplicates and overlength arrays fail closed
in both languages. Unknown pattern fields remain rejected.

The field is copied by canonical → runtime projection, included conditionally in review
scope, stored conditionally in frozen pattern structure, validated in the frozen
structure schema and reconstructed for frozen review-digest checks. Conditional presence
means all released patterns that omit it preserve their historical scope and structure
bytes.

The generic headline mechanism inserts authored lexical items immediately after the
lemma and before its fillable slots. Synthetic fixtures render:

- `brać udział + w czym?`;
- `wziąć udział + w czym?`.

No fake Accusative complement and no `udział` special case exists. With the field absent,
the same synthetic shape retains the exact historical `brać w czym?` behavior.

## 7. formatVersion change

The released runtime and both language constants now require exact `formatVersion = 2`.
Version 2 is accepted; versions 1 and 3 are rejected by both Python and JavaScript.
Arbitrary future versions are not accepted.

Other boundaries remain exact:

| Value | Result |
|---|---|
| `patternDataRevision` | 2, unchanged |
| `PP_MIGRATE.SCHEMA_VERSION` | 2, unchanged |
| `PP_MIGRATE.CONTENT_MIGRATION_REVISION` | 2, unchanged |
| `APP_VERSION` | 8.12, unchanged |
| service-worker shell cache | `popolsku-v67`, unchanged |

## 8. Python/JavaScript parity

The JavaScript contract exposes defensive copies of its role, clause-kind, complement-
type and relation-type tables. The dedicated suite evaluates the shipping JavaScript and
compares those live tables with the Python constants and the staging validator tables.
This is a table-driven behavioral comparison, not a duplicated expected-value list or a
fragile source-text match.

## 9. Released-30 immutability

The pre-change production document was read directly from the starting commit. Replacing
only its `formatVersion` with 2 makes it exactly equal to the post-change JSON object.
The canonical JSON semantic projection excluding `formatVersion` has identical SHA-256
before and after:

`df01674f00bdc3bdced9acbf137a73cc9d3ab8d994ddd7af2de5677145c2fb03`

Counts remain exactly 30 lemmas, 34 meanings, 45 patterns and 45 examples. All lemma,
meaning, pattern and example data is unchanged.

## 10. Existing-ID reproduction

The released corpus still contains exactly 154 unique IDs: 30 lemma, 34 meaning,
45 pattern and 45 example IDs. The locked Phase 4C1 reproduction walk accepts all
154/154 with zero mismatch. The stable allocator functions are source-hashed at the
same value as the Phase 4C1 starting endpoint:

`ef9236f5b4841627631aebb45122e5d0a943ec642b3bcd26671f2f0c41769f03`

Schema fields, roles, clauses and lexical items remain absent from all ID seeds.

## 11. Phase 4C1 map immutability

The private map remains byte-identical at SHA-256:

`20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d`

Independent regeneration equals the persisted object. Validation reports 611 new IDs,
154 released IDs, union 765, zero collisions, zero `vp-x` and zero tombstones. None of
the 611 mapped new IDs occurs in released content.

## 12. Rendering and search regression

The dedicated suite executes the starting JavaScript against the starting runtime and
the Phase 4C2 JavaScript against the upgraded runtime. It compares the complete derived
lemma projection for all 45 released patterns: headlines, badges, recognition state,
chips, roles, examples, case links and eligibility. The projections are exactly equal.
The full released search text is also exactly equal, so the search regression is covered
by the same behavioral projection test rather than a second copied fixture.

## 13. Malformed-input tests

Both languages reject unknown roles, unknown clause kinds, unknown pattern fields and
every malformed lexical-item shape listed in §6. Valid direct speech, source and lexical
fixtures pass both validators. Exact-version rejection remains whole-document and
fail-closed.

## 14. Migration and version boundary

Only the Verb Patterns public-contract version moved. Progress storage and migrations,
the human-facing app version, service-worker generation/cache identity and data revision
did not move. Repository hashes prove `index.html` and `sw.js` are byte-identical to the
starting endpoint.

## 15. No-promotion and no-structure-freeze proof

Canonical production remains 30/34/45/45. The 68 candidate lemmas and all 611 private-map
IDs remain absent. The staging JSON, candidate-key freeze manifest and private map are
byte-identical to the start. No `freeze_editorial` or equivalent structure-freezing
operation was invoked, no structure snapshot for the 68 was created, and no allocation,
tombstone or candidate key changed.

## 16. Activities and audio proof

No activity path or logic changed. All 45 released `activityEligibility` arrays remain
empty. No audio file, audio rule, generator, verifier, manifest entry or cache changed;
`audio-manifest.json` remains byte-identical and the existing 45 released examples retain
their existing `audioEligible: true` values. No Priority 8 audio was generated.

## 17. Tests and audits

| Gate | Result |
|---|---|
| `python3 validate_priority8_staging.py` | PASS |
| Existing twelve Phase 4B suites | 297 tests, OK |
| Existing Phase 4C1 suite | 27 tests, OK |
| Existing thirteen suites | 324 tests, OK |
| Dedicated Phase 4C2 suite | 22 tests, OK |
| All fourteen suites together | 346 tests, OK |
| Phase 4C1 map checker | 154 released / 611 new / 765 union; zero collisions |
| `git diff --check` | PASS |

## 18. Phase 4C3 handoff

The contract now has the generic structural/runtime capacity required by Phase 4C3.
Phase 4C3 may author/promote `source`, `direct-speech` and pattern-level
`requiredLexicalItems` only after independent Phase 4C2 verification. This phase has not
authored, frozen or promoted any of those candidate structures.

**READY FOR INDEPENDENT PHASE 4C2 VERIFICATION BEFORE PHASE 4C3**
