# Priority 8 Phase 4C3 — private canonical candidate projection and loss audit

## 1. Starting endpoint

Phase 4C3 began from the exact independently verified Phase 4C2 endpoint.

| Check | Observed |
|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4C SAFE` |
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `a858cf83a7f9d979feecfecef32c42937b5e9eec` |
| Tree | `8ee029862166befb0e57fe1bd8b2550700687eb4` |
| Parent | `604df149045fb91bbcf35eb54499b0ef490e1e99` |
| Subject | `Priority 8 Phase 4C2 implement schema extensions` |
| Worktree | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |

The staging validator passed. All fourteen existing suites passed twice at **346 tests**:
once before the initial stop and once after the authoritative prompt correction.

## 2. Authoritative inputs

The projection consumes, read-only, the frozen Phase 4C0 architecture and human
adjudication, the Phase 4C1 and Phase 4C2 implementation reports, the final Phase 4B
handoff/reconciliation, staging, candidate-key freeze, private stable-ID map, released
runtime corpus, locked allocator/tooling, runtime consumer, and all relevant Phase 4C1/4C2
tests. Repository evidence, not completion summaries, controls every transformation.

## 3. Pre-write governance correction

The initial Phase 4C3 task prompt incorrectly stated that 11 target complements in the
seven source/provider families required conversion. The mandatory pre-write gate caught
the contradiction and stopped with no write and no commit. Authoritative correction then
confirmed the already-frozen Phase 4C0 governance:

- exactly **7** source/provider complements become `role: source`;
- exactly **6** other `target` complements in those families remain `target`;
- the separate **11 direct-speech patterns** count is unchanged.

This is a prompt correction, not a Phase 4B or Phase 4C0 semantic reopening.

## 4. Frozen candidate and map verification

| Gate | Result |
|---|---|
| Candidate freeze digest | `0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27` |
| Manifest/live hierarchy | exact equality |
| Candidate hierarchy | 68 lemmas / 95 meanings / 224 patterns / 224 examples / 543 keys |
| Stable-map SHA-256 | `20fc8a566cb34825306f9198f4977fb0dacef3c33696cad45ff7ecbab6487a9d` |
| Stable-map allocation | 68 `vp-l` / 95 `vp-m` / 224 `vp-p` / 224 `vp-e` / 0 `vp-x` |
| Stable-map IDs | 611 unique; zero collisions |
| Released reproduction | 154/154 exact |
| Released + new union | 765 unique IDs |

The map equals independent regeneration through the locked allocator. No allocator logic
is duplicated in Phase 4C3.

## 5. Projection architecture and private artifact

The Phase 4C0 report freezes the canonical entity contract but does not define a distinct
standalone Phase 4C3-only artifact path. The task-specified fallback is therefore used:

`editorial/priority-8-phase4c-canonical-candidates.json`

| Property | Value |
|---|---|
| Schema | `canonicalCandidateSchemaVersion: 1` |
| Status | `priority-8-phase-4c3-canonical-candidates-private-nonproduction` |
| Release authority | `false` |
| Contract snapshot | `formatVersion: 2`, existing `patternDataRevision: 2` |
| SHA-256 | `c54e611da32ad61c4c020545594ec1f33c0bcea6937f31c9e7a31d29bc5fa7e9` |

The canonical candidate core uses the production entity shapes and is validated by
`priority7_tooling.validate_runtime` through an in-memory envelope. Private traceability,
provenance, meaning scopes, metadata-only relationships and loss ledgers live outside
that closed canonical core. The artifact is not loaded or precached by runtime, service
worker, index, or audio code.

`priority8_phase4c3_canonical_projection.py` is verify-only by default and writes only
with `--write`. It performs two independent builds and requires byte-identical output;
persisted bytes must equal regeneration.

## 6. Promotion counts and stable IDs

| Entity | Promoted | Namespace |
|---|---:|---|
| Lemmas | 68 | `vp-l` |
| Meanings | 95 | `vp-m` |
| Patterns | 224 | `vp-p` |
| Examples | 224 | `vp-e` |
| **Total** | **611** | zero `vp-x` |

Every mapped ID equals both the private map and independent locked-allocator
recomputation. No replacement ID, collision, reparenting, duplicate promotion, or map
mutation occurred.

## 7. Source-role conversion

The exact conversions are:

| Lemma | Meaning key | Pattern key | Converted complement |
|---|---|---|---|
| `wracać` | `return-to-earlier-place` | `z-genitive-return-source` | `z` + Genitive |
| `wrócić` | `completed-return-to-earlier-place` | `z-genitive-return-source` | `z` + Genitive |
| `wyjść` | `literal-exit-from-place` | `z-genitive-source` | `z` + Genitive |
| `wyjechać` | `transport-departure` | `z-genitive-source` | `z` + Genitive |
| `kupować` | `process-purchase` | `seller-price-schema` | seller `od` + Genitive only |
| `kupić` | `completed-purchase` | `seller-price-schema` | seller `od` + Genitive only |
| `zamawiać` | `commissioning-ordering` | `u-genitive-provider` | `u` + Genitive |

The seller/provider rows on `kupować`, `kupić`, and `zamawiać` receive the approved
`questionOverridePl: ["kogo?"]`. `source` remains globally inanimate by default.

Six genuine targets remain unchanged: the `wracać` and `wrócić` return goals, the two
`wyjść` destinations, and the two `za` purchase-price complements. Tests reject blanket
conversion, a missed source row, or conversion of any genuine target.

## 8. Direct speech and interrogative boundary

Exactly **11** patterns retain canonical `clauseKind: direct-speech`, on the frozen
identities for `odpowiadać`, `czytać`, `pisać` (2), `napisać` (2), `powiedzieć`,
`zgadzać się` (2), `polecać`, and `radzić`.

`zapominać/interrogative-forgotten-content` and
`kłócić się/interrogative-disputed-content` remain `interrogative`. No frozen or promoted
`czy-dependent-clause` key exists. `Czy mogę…?` remains example sentence packaging around
`móc + infinitive`; no `móc` clause complement is created.

## 9. Required lexical material

`requiredLexicalItems: ["udział"]` is projected onto exactly:

- `brać/fixed-participation/w-locative-participation-target`;
- `wziąć/fixed-participation/w-locative-participation-target`.

No other pattern receives the field and neither participation pattern gains a fake
Accusative complement. The shipping generic headline helper renders structured tokens
equivalent to `brać udział + w czym?` and `wziąć udział + w czym?`.

## 10. Metadata, lexical identity and aspect boundaries

`zaczynać` and `przeczytać` remain metadata-only governance relationships. They receive
no lemma, meaning, pattern, example, or ID. No `aspectPartnerIds` or
`aspectEquivalentPatternIds` are emitted.

Lexical `się`/`sobie` remains identity-bearing. In particular `radzić` and `radzić sobie`
remain distinct, `uczyć` remains distinct from released `uczyć się`, and the seven
lexical-`się` lemmas retain their particles and independently allocated IDs.

No syntax is inherited across the eight aspect families. The frozen `pisać`/`napisać`
Dative requiredness asymmetry on the `że`, `żeby`, and interrogative clause patterns is
preserved.

## 11. Other semantic boundaries

- Generalized roles are not manufactured into concrete complements.
- `umówić się` appointment `KIEDY` remains non-structural and separate from venue.
- `co do + Genitive` capability/content is not introduced.
- `pasować/dative-expectation-holder` remains a `lexical-frame` without a synthetic
  subject.
- All `kochać` patterns retain the frozen neutral register.
- Frozen glosses, explanations, examples, CEFR, status, priority and register are copied
  exactly except for the three architecture-approved transformations: source role,
  animate question override, and pattern-level `requiredLexicalItems`.

## 12. Provenance

The private governance layer retains 95 meaning scopes, 224 pattern provenance rows and
224 example-origin rows. Pattern provenance preserves the lemma's Phase 3 disposition,
source locator and binding constraints without misrepresenting them as a completed
canonical review event.

The `odpowiadać/direct-speech` row is explicitly marked
`policy-authorized-direct-speech`; it does not falsely claim direct-speech licensing from
the narrower evidence row. Example origins remain exactly 220 `editorial-generated` and
4 `repository-reuse`. All four reused Polish strings re-resolve byte-identically through
their registered repository sources.

No source citation or human review authority is invented. No review event, release
authorization, or structure freeze is performed.

## 13. Status, activity and audio eligibility

The exact teaching split is **222 active-production / 2 recognition-only**. Every one of
the 224 patterns has `activityEligibility: []`.

Under the frozen Phase 4C0 policy, all 224 promoted examples have `audioEligible: true`,
making 224 future pronunciation-audio candidates. This does not authorize Listening.
No audio file or audio-manifest entry is generated or changed.

## 14. Loss ledger A — identities

| Input | Promoted | Missing | Duplicate |
|---|---:|---:|---:|
| 68 frozen lemma identities | 68 | 0 | 0 |
| 95 meaning keys | 95 | 0 | 0 |
| 224 pattern keys | 224 | 0 | 0 |
| 224 example keys | 224 | 0 | 0 |
| **Total identities** | **611** | **0** | **0** |

Every row records frozen identity path → stable ID → `PROMOTED`. The 543 frozen keys map
to 543 keyed canonical entities; the remaining 68 are lemma identities.

## 15. Deferral ledger B — 10 registered facts

| # | Lemma/scope | Fact |
|---:|---|---|
| 1 | `pracować` | workplace `GDZIE` |
| 2 | `przynosić` | optional generalized source/goal |
| 3 | `pokazywać` | optional `GDZIE` |
| 4 | `czytać` | generalized `GDZIE` |
| 5 | `zapraszać` | separate `KOGO + GDZIE` schema |
| 6 | `wiedzieć` | `SKĄD` source of knowledge |
| 7 | `uczyć` | school-sense `GDZIE` |
| 8 | `umówić się` | appointment `KIEDY` |
| 9 | corpus-wide | `KTÓRĘDY` |
| 10 | `umówić się` | `co do + Genitive` |

Each artifact row records its reason, architecture decision, why no canonical pattern is
created, and that candidate-key/stable-ID impact is zero because the deferred fact is not
a frozen keyed identity.

## 16. Combined ledger C

| Level | Released | Promoted private | Combined future |
|---|---:|---:|---:|
| Lemmas | 30 | 68 | 98 |
| Meanings | 34 | 95 | 129 |
| Patterns | 45 | 224 | 269 |
| Examples | 45 | 224 | 269 |
| Stable IDs | 154 | 611 | 765 |

This is accounting only. No combined corpus is written to production.

## 17. Immutability and runtime isolation

The following remain byte-identical to the Phase 4C3 start: staging, candidate freeze,
private ID map, released runtime corpus, `priority7_tooling.py`, Phase 4C1 helper,
`validate_priority8_staging.py`, `pp-verb-patterns.js`, `index.html`, `sw.js`, and
`audio-manifest.json`. The released corpus remains `formatVersion: 2`,
`patternDataRevision: 2`, and 30/34/45/45 with all 154 IDs unchanged.

The private artifact has zero runtime imports, service-worker references, HTML references,
or audio-manifest references. No `APP_VERSION`, migration, activity, audio, runtime,
release-authorization, deployment, push, or integration operation occurs.

## 18. Determinism and tests

- Staging validator: PASS.
- Existing fourteen suites: **346 tests, OK**.
- Dedicated Phase 4C3 suite: **46 tests, OK**.
- All fifteen suites together: **392 tests, OK**.
- Persisted artifact equals repeated regeneration byte-for-byte.
- Default checker mode leaves artifact bytes unchanged.
- Malformed/unknown fields and every required semantic mutation are rejected.

The dedicated suite covers the generated invariants, real production schema validation,
runtime headline rendering, exact seven/six source accounting, all loss ledgers, protected
hashes, runtime isolation, and adversarial omission, duplication, reparenting, ID drift,
role drift, clause drift, lexical-item drift, aspect inheritance, metadata promotion and
unregistered deferral mutations.

## 19. Phase 4C4 handoff

Phase 4C4 may independently verify Phase 4C3 semantics and loss accounting before any
canonical governance/release-readiness work. It must treat this artifact as private and
pre-release, preserve the 611 mapped IDs and all frozen identities, and must not project
runtime content until the separately governed later phase.

**READY FOR INDEPENDENT PHASE 4C3 SEMANTIC/LOSS VERIFICATION BEFORE PHASE 4C4**
