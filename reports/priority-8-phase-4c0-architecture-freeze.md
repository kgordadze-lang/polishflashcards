# Priority 8 Phase 4C0 — canonical architecture and stable-ID policy freeze

This document is **architecture and policy only**. It allocates no stable ID, implements
no stable ID, writes no canonical or runtime content, modifies no staging, generates no
audio, changes no `APP_VERSION` or service worker, and deploys and pushes nothing. Its
only repository effect is its own creation.

Every decision below is binding on Phase 4C1 and later unless a listed human decision
(§26) is answered differently.

---

## 1. Executive architecture verdict

**The Phase 4B frozen semantic identity layer can be promoted to production without
reopening Phase 4B governance.** No frozen candidate key must be renamed, removed,
reparented or reused. `PHASE 4B GOVERNANCE REOPEN REQUIRED` is **not** raised by any
item in this report.

Four findings determine the whole architecture, and all four were established by direct
recomputation against the repository rather than by reading its reports.

1. **The stable-ID architecture already exists, is already deterministic, and already
   keys on exactly the identity layer Phase 4B froze.** `priority7_tooling.py`
   allocates every ID from `(normalized canonical lemma, meaning key, pattern key,
   example key)` and nothing else. This audit re-derived all **154** released production
   IDs from the released corpus and reproduced **154/154 byte-identically, zero
   mismatches**. Phase 4C therefore does not design an allocator; it *uses* the locked
   one. §13, §14, §15.
2. **A full-corpus allocation rehearsal is collision-free.** Running the locked
   allocator in memory over the frozen manifest yields **611** prospective identities
   (68 lemma + 543 key-derived), **internally unique**, **byte-identical across repeated
   runs**, and with **zero collisions against the 154 released IDs** (union 765). No ID
   was written, printed, or persisted; only these counts were retained. §13, §27.
3. **The promotion pipeline already exists end to end** — `validate_editorial` →
   `freeze_editorial` (allocations, identity/structure/wording/policy snapshots,
   tombstones, release authorization) → `verified_runtime_from_frozen` → committed
   runtime — and it has already been exercised once on real data by
   `priority8_phase1_transition.py`. Phase 4C builds a second transition through the same
   path, not a parallel one. §5, §18.
4. **Exactly three canonical/runtime contract extensions are required**, all of which
   ride one already-approved `formatVersion` increment: the `direct-speech` clause kind
   (already approved at Phase 4A2-2 §2), a `source` role (§8, HD-4C-01), and a
   `requiredLexicalItems` pattern field (§12, HD-4C-02). Everything else the 68 lemmas
   need is already expressible in the released schema.

**Gate result: `HUMAN ARCHITECTURE DECISION REQUIRED BEFORE PHASE 4C1`.** Two decisions
are genuinely open (§26). Both are narrow, both have a firm recommendation, and neither
touches a frozen key. Phase 4C1 tooling design may begin the moment they are answered.

---

## 2. Starting state

Every value below was recomputed, not quoted.

| Check | Required | Observed |
|---|---|---|
| Working folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4C SAFE` | exact |
| Branch | `priority-8-phase-4c-architecture` | exact |
| HEAD | `65cd97739bfe762a6f1fb383c27384c8454eb968` | exact |
| Tree | `f7867b456099324c9bc3203245b98b0a5bf857c4` | exact |
| Subject | `Priority 8 Phase 4B freeze candidate keys` | exact |
| Worktree at start | clean | clean |
| Remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Pre-push hook | executable, fail-closed | executable; prints the repository block message, exits 1 |
| Staging envelope | `phaseStep = 4B7`, `stagingRevision = 8` | exact |
| Full-pattern lemmas / meanings / patterns / examples | 68 / 95 / 224 / 224 | exact |
| Frozen candidate keys | 543 | exact (95 + 224 + 224) |
| Teaching-status split | 222 active-production / 2 recognition-only | exact |
| Guard registry | 74 rules, `registryVersion = 2` | exact |
| `candidateKeyFreezeDigest` | `0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27` | recomputed from **live staging** and from the **manifest hierarchy**; both exact |
| Manifest `status` | `frozen` | exact |
| Released Verb Patterns baseline | separate and unchanged | `formatVersion 1`, `patternDataRevision 2`, 30 lemmas / 34 meanings / 45 patterns / 45 examples |
| Pre-existing stable production IDs for the 68 | none | none found in staging or manifest |

No mismatch. Proceeding was authorized.

### 2.1 Authoritative inputs read in full

- `editorial/priority-8-phase4-candidate-key-freeze.json`
- `reports/priority-8-phase-4b-candidate-key-freeze.md`
- `reports/priority-8-phase-4b-to-4c-handoff.md`
- `reports/priority-8-phase-4b-final-semantic-reconciliation.md`
- `reports/priority-8-phase-4b-final-reconciliation-mechanical-audit.md`

### 2.2 Additional artifacts inspected directly

`editorial/priority-8-phase4-staging.json`; `editorial/verb-pattern-candidates.json`;
`editorial/priority-7-authoring-context.json`; `content/verb-patterns.json`;
`priority7_tooling.py`; `pp-verb-patterns.js`; `validate_priority8_staging.py`;
`priority8_phase1_transition.py`; `pp_audio_rule.py`; `generate_audio.py`;
`verify_audio.py`; `audio-manifest.json`; `pp-migrate.js`; `validate_content.py`;
`sw.js`; `index.html`; `tests/fixtures/priority8_phase4b_authoring_rules.json`; the
twelve Phase 4B/freeze suites; and the Phase 4A1/4A2 architecture reports, including
`priority-8-phase-4a1-stable-id-audit.md`, `priority-8-phase-4a2-2-policy-freeze.md`,
`priority-8-phase-4a2-1-direct-speech-options.md`,
`priority-7-stable-id-specification.md`, `priority-8-schema-migration-analysis.md` and
`priority-8-audio-architecture-audit.md`.

---

## 3. Phase 4B frozen invariants

These are inputs to Phase 4C, not decisions of Phase 4C. None may be altered without an
explicit Phase 4B governance reopening.

1. **543 candidate keys**: 95 `candidateMeaningKey`, 224 `candidatePatternKey`, 224
   `candidateExampleKey`. All 224 example keys are `primary`.
2. **68 full-pattern lemma identities**, in frozen `verificationOrder`; membership exact.
3. **Ownership**: meaning within lemma, pattern within `(lemma, meaning)`, example within
   `(lemma, meaning, pattern)`; exactly one example per pattern; zero orphans.
4. **Two metadata-only identities**: `zaczynać` under `zacząć`, `przeczytać` under
   `czytać`. Neither is one of the 68 and neither receives production content.
5. **Two lemmas carry `requiredLexicalItems: ["udział"]`**: `brać`, `wziąć`.
6. **`candidateKeyFreezeDigest` is exactly the recorded value** under the manifest's
   canonical projection (UTF-8, direct Unicode, `sort_keys=True`, separators `,`/`:`).
7. **Teaching split 222/2**; register `neutral` on all 224; priority 116 core / 108
   common; origin 220 editorial-generated / 4 repository-reuse.
8. **Zero `czy` clause kinds remain.** Live clause distribution is `ze` 19, `zeby` 19,
   `interrogative` 16, `direct-speech` 11.
9. **No production `vp-*` ID exists** in staging or manifest.

**Phase 4C adapts to these facts. They do not adapt to Phase 4C.**

---

## 4. D01–D13 adjudication

### 4.1 Classification scheme

- **A** — must resolve before stable-ID allocation
- **B** — must resolve before canonical projection
- **C** — must resolve before runtime exposure
- **D** — non-blocking follow-up
- **E** — no implementation required; preservation rule only

### 4.2 The adjudication principle this report applies

The handoff classifies twelve of the thirteen items as "resolve before runtime
projection: yes". That is a single bucket and it is not the most useful one, because the
repository's own release machinery has **three** distinct irreversibility points, not one:

1. **Allocation** — `freeze_editorial` writes the allocation record and the *structure*
   snapshot at the same instant. Any field inside `_structure_for_entity` (for a pattern:
   `relationType`, and every complement key except `questionOverridePl`) becomes immutable
   at that moment: changing it later raises `FROZEN_COMPLEMENT_REPLACEMENT_REQUIRED` /
   `FROZEN_RELATION_REPLACEMENT_REQUIRED` and costs a **new ID plus a tombstone**.
2. **Projection** — what is or is not present in the first frozen baseline. Absence is
   *cheap and reversible*: because seeds depend only on `meaning_id` + `pattern_key`, a
   pattern added in a later revision receives **exactly the ID it would have received
   now**, with no tombstone and no drift.
3. **Runtime exposure** — what a learner sees.

Items are therefore graded by which of those three points they actually touch. This is a
deliberate refinement of the handoff, not a disagreement with it: nothing is downgraded
below "resolve during Phase 4C", and two items are *upgraded* to the stricter allocation
gate.

### 4.3 Adjudication table

| Debt ID | Topic | Handoff position | **Phase 4C0 class** | Verdict | Why this class |
|---|---|---|---|---|---|
| D01 | source/provider role on 7 rows | before runtime projection | **A** | Add role `source` (§8) | `role` is inside the frozen structure snapshot. Allocating with `target` and adding `source` later would force 7 replacement IDs and 7 tombstones on already-released patterns. **Upgraded.** |
| D02 | 11 direct-speech patterns | before runtime projection | **B** | Implement `clauseKind: direct-speech` exactly as approved at 4A2-2 §2 (§9) | Deferral costs no identity: the same 11 IDs would be produced in any later revision. But omitting them is silent loss under §24, so it gates projection. |
| D03 | unrepresented generalized roles | before runtime projection | **E** | Permanent structural boundary; retained as governance metadata only (§10) | The decision is *to omit*. It requires no schema, no runtime and no data. Its only artifact is a deferral register consumed by the loss audit. **Downgraded, deliberately.** |
| D04 | `umówić się` appointment `KIEDY` | before runtime projection | **E** | Permanent non-structural boundary (§10.3) | Same reasoning as D03. |
| D05 | `co do` + Genitive | before runtime projection | **D** | Neither build compound-preposition capability nor admit the pattern (§10.4) | Nothing in the frozen 68 uses it. A future admission needs Phase 4B reopening regardless of when capability is built. **Downgraded.** |
| D06 | role-vocabulary granularity | before runtime projection | **A** | Keep every existing assignment; add exactly one value (`source`) (§8) | Same structure-snapshot argument as D01. The role vocabulary must be final before the first allocation. **Upgraded.** |
| D07 | `pasować` subject/experiencer | before runtime projection | **E** | No action; keep the frozen `lexical-frame` (§4.4) | Mechanically settled — see below. |
| D08 | `kochać` + infinitive register | non-blocking | **D** | Preserve `neutral`; revisit only on governed evidence | `usage.register` lives in the *policy* dimension, which is correctable in place without a new ID. Genuinely non-blocking. Handoff agreed. |
| D09 | B1/residual-B2 guard coverage | before runtime projection | **B** | Replace hand-written backfill with generated canonical-projection invariants (§23) | The projection cannot be trusted before its contract tests exist. |
| D10 | canonical/provenance/IDs/promotion | before runtime projection | **A** | Full pipeline specified in §5, §7, §13–§18 | This *is* the allocation gate. |
| D11 | metadata-only + lexical identity | before runtime projection | **A** | Hard exclusion plus positive identity tests (§11) | A mistaken promotion of `zaczynać`/`przeczytać` would allocate two lemma IDs that could then only be retired by tombstone. |
| D12 | required `udział` | before runtime projection | **A** | Add `requiredLexicalItems` to the pattern *structure* dimension (§12, HD-4C-02) | If it is structural it must exist before allocation; if it is added afterwards the two patterns need replacement IDs. |
| D13 | `Czy mogę…?` packaging | before runtime projection | **E** | Preservation invariant only; no schema feature (§11.4) | The frozen representation is already correct. Only a test is needed. |

**Bucket C is empty, and that is a finding rather than an omission.** In this repository
`priority7_tooling.py` shares one set of enum constants between editorial validation and
runtime validation, and `pp-verb-patterns.js` mirrors them. Consequently every
runtime-exposure obligation in this inventory is *upstream-gated*: a value that the
runtime cannot render is a value the canonical validator will not accept. There is no
class of item that can pass canonical projection and then surprise the runtime.

### 4.4 D07 — decided mechanically, not by preference

`pasować/expectation-suitability/dative-expectation-holder` carries one *optional* Dative
`experiencer` and no subject complement. The released `podobać się` precedent uses
`relationType: subject-experiencer` with **two required complements** — a Nominative
`subject` and a Dative `experiencer`.

`_validate_relation_roles` in `priority7_tooling.py` raises `EXPERIENCER_ROLES_REQUIRED`
unless **both** `subject` and `experiencer` roles are present. Adopting
`subject-experiencer` for `pasować` would therefore require inventing a Nominative
complement that its Składnia does not list — precisely the fabrication Phase 4B refused.
Adopting the relation type *without* the subject complement is not merely undesirable, it
**fails validation**. And the only runtime effect of `subject-experiencer`
(`SUBJECT_EXPERIENCER_SUBJECT`, "the thing that appeals") applies solely to a `subject`
role, so it would be inert even if it validated.

**Verdict: NO ACTION. Not "optional future enhancement" — the current frozen
representation is the only legal one.** Class E.

---

## 5. Current production schema audit

Recomputed from `content/verb-patterns.json`, `editorial/verb-pattern-candidates.json`
and their actual consumers. **Schema facts** are separated from **implementation
assumptions** as required.

### 5.1 Layers

| Layer | Path | Status |
|---|---|---|
| Private editorial/governance corpus | `editorial/verb-pattern-candidates.json` | source of truth; `artifactStatus: priority-7-editorial-nonproduction` |
| Private authoring context | `editorial/priority-7-authoring-context.json` | registries; `allocationRegistry` currently **empty** |
| Frozen release artifact | *not committed* | produced transiently by `freeze_editorial`; previous state reconstructed from a named git commit |
| Public runtime | `content/verb-patterns.json` | `formatVersion 1`, `patternDataRevision 2` |
| Runtime consumer | `pp-verb-patterns.js` | closed-envelope loader, validator, derivation and view builder |

### 5.2 Released envelope and inventory — schema facts

| Item | Value |
|---|---|
| `formatVersion` | `1` (runtime requires **exact equality**, not `>=`) |
| `patternDataRevision` | `2` (runtime requires only a positive integer) |
| Envelope keys | exactly `formatVersion`, `patternDataRevision`, `lemmas` — closed |
| Lemmas / meanings / patterns / examples | 30 / 34 / 45 / 45 |
| Total released IDs | **154** |

### 5.3 Entity shapes — schema facts

**Lemma.** Runtime required `id`, `canonicalLemma`, `reflexive`, `aspect`, `meanings`;
optional `displayLemma`, `aspectPartnerIds`. `canonicalLemma` must be NFC, trimmed,
single-spaced and lowercase; `reflexive` must equal "ends in lexical ` się`". Editorial
adds nothing further at lemma level.

**Meaning.** Runtime `id`, `glossesEn` (1–3, unique), `patterns`. Editorial additionally
requires `key` and `internalScope`, both of which are **private** and pruned before
runtime.

**Pattern.** Runtime required `id`, `relationType`, `complements`, `cefr`,
`teachingStatus`, `usage`, `learnerExplanationEn`, `activityEligibility`; optional
`aspectEquivalentPatternIds`, `examples`, `contentRefs`, `errorNotes`. Editorial
additionally requires `key`, `evidence`, `reviewState`, `reviewEvents`, and optionally
`releaseMode` — all private.

**Example.** Runtime `id`, `pl`, `en`, `audioEligible` — closed, exactly four keys.
Editorial additionally requires `key` and `origin`, both private.

**Complement.** Required `type`, `required`, `role`; optional `case`, `preposition`,
`clauseKind`, `questionOverridePl`. Type-conditional rules: `case` forbids `preposition`
and `clauseKind` and its case must be direct-capable (Locative and Vocative are refused);
`preposition-case` requires a **single lowercase Polish word** preposition
(`^[a-ząćęłńóśźż]+$`) with a prepositional-capable case and forbids `clauseKind`;
`infinitive` forbids all three; `clause` requires `clauseKind` and forbids `case` and
`preposition`.

### 5.4 Closed vocabularies — schema facts

| Vocabulary | Released values | Runtime location |
|---|---|---|
| `COMPLEMENT_TYPES` | `case`, `preposition-case`, `infinitive`, `clause` | both languages |
| `RELATION_TYPES` | `lexical-frame`, `constructional-frame`, `means-method`, `subject-experiencer` | both |
| `ROLES` | `subject`, `object`, `recipient`, `experiencer`, `predicate`, `content`, `topic`, `interlocutor`, `means`, `target` | both |
| `CLAUSE_KINDS` | `ze`, `czy`, `zeby`, `interrogative` | both |
| `TEACHING_STATUSES` | runtime `active-production`, `recognition-only`; editorial also `deferred` | both |
| `CEFR_LEVELS` | `A1`, `A2`, `B1`, `above-b1` | both |
| `USAGE_PRIORITIES` | `core`, `common`, `limited` | both |
| `REGISTERS` | `neutral`, `formal`, `informal` | both |
| `ACTIVITY_KEYS` | `reference`, `search`, `grammar-choose`, `grammar-build`, `type-it`, `listening`, `mixed-quiz`, `case-mix`, `conversation` | both |
| `CONTENT_KINDS` / `CONTENT_PURPOSES` | `card`/`topic`/`drill`/`scenario`; `support`/`practice`/`context`/`contrast` | both |

### 5.5 Released distributions — schema facts

Complement types: `case` 31, `preposition-case` 20, `infinitive` 2, `clause` 1.
Roles: `topic` 13, `object` 12, `target` 10, `recipient` 5, `content` 5, `interlocutor`
4, `experiencer` 2, `subject` 1, `predicate` 1, `means` 1.
Relation types: `lexical-frame` 42, plus one each of `constructional-frame`
(`być/predicate-role`), `means-method` and `subject-experiencer` (`podobać
się/appeal-to`).
Clause kinds in use: `ze` ×1 only. Teaching status: 41 active-production, 4
recognition-only. `activityEligibility`: **empty on all 45**. `audioEligible`: **true on
all 45**.

### 5.6 ID syntax and ordering — schema facts

```
vp-l-<lemma-slug>-<digest12>
vp-m-<lemma-slug>-<meaning-key>-<digest12>
vp-p-<lemma-slug>-<meaning-key>-<pattern-key>-<digest12>
vp-e-<pattern-readable-stem>-<example-key>-<digest12>
vp-x-<pattern-readable-stem>-<activity-type>-<item-key>-<digest12>   (defined, unused)
```

Projection order is by `id` at every level. Runtime re-sorts lemmas by a folded display
key. Neither order participates in identity; the specification states explicitly that
reordering has no effect and IDs are never renumbered.

### 5.7 Implementation assumptions — **not** schema facts

These are properties of the current code that the schema does not state, and each is a
real Phase 4C constraint.

1. **`formatVersion` is checked for exact equality.** A document declaring `2` is
   rejected whole by today's shipped loader. This is what makes the approved bump a
   deployment-ordering constraint rather than a data migration.
2. **Rejection is whole-document and fail-closed.** One unknown enum value anywhere sets
   `available = false` and the surface renders its neutral unavailable state. A stale
   cached bundle meeting a new corpus degrades safely — it never renders partially.
3. **The pattern headline is generated purely from `displayLemma` + `complements`.** No
   pattern authors its own headline. This is the mechanism behind both D01 and D12.
4. **Roles become words in exactly one place**, `ROLE_PHRASES`, with one context override
   for `subject-experiencer`. There is no per-row phrase escape hatch.
5. **Clause kinds become words in exactly one place**, `CLAUSE_TOKENS`. Adding a kind is
   one enum member plus one table row; `chipFor`, `headlineFor` and `searchText` all key
   off the table generically and need no new branch.
6. **The runtime lemma `key` is an array index** into the sorted index. Adding 68 lemmas
   shifts it for existing lemmas. Verified safe: it is derived per session in
   `build()`, is never written to `localStorage`, and never appears in the URL hash.
7. **`allocationRegistry` is empty**, so every released ID is currently re-verified by
   *live recomputation* through `ID_RECOMPUTATION` rather than against a frozen record.
   This audit confirmed all 154 recompute exactly. It is the strongest available evidence
   that the generator is the operative mechanism, not merely a historical one.
8. **The previous frozen state is reconstructed from git**, not read from a committed
   manifest (`priority8_phase1_transition.py` uses `git show <commit>:…`).
9. **`patternDataRevision` increments by exactly one** when, and only when, the runtime
   payload changes; `FROZEN_REVISION_TRANSITION` enforces it.
10. **From revision ≥ 2, `audioEligible` no longer implies Listening.** Editorial
    validation additionally requires `pronunciation_playback_authorized` in the context,
    which is already `true`.

---

## 6. Target canonical schema

**Design principle: minimal extension.** The 68 lemmas are 3.7× the released corpus but
introduce only three shapes the released schema cannot express. Everything else — five
new prepositions, `direct-speech`, three new clause-bearing lemma families, two-complement
patterns, optional complements, aspect-partner families — is already legal today.

### 6.1 New field/value states

| # | Name | Type | Allowed values | Req. | Purpose | Editorial source | Runtime consumer | Migration consequence |
|---|---|---|---|---|---|---|---|---|
| 1 | `clauseKind: "direct-speech"` | enum member on the existing complement field | one new member of `CLAUSE_KINDS` | required when `type: clause` | Preserve the fourth frozen clause distinction on 11 patterns | staging `complements[].clauseKind` | `CLAUSE_KINDS`, `CLAUSE_TOKENS`, `chipFor`, `headlineFor`, `searchText` | contract change → `formatVersion 2`; already approved at 4A2-2 §2 |
| 2 | `role: "source"` | enum member on the existing complement field | one new member of `ROLES` | required (roles always are) | Faithful origin/provider semantics for 7 patterns | staging `complements[].role` | `ROLES`, `ROLE_PHRASES`, `validComplement` | contract change; rides the same `formatVersion 2`. **Zero released rows migrate** — proven in §8.3. HD-4C-01 |
| 3 | `requiredLexicalItems` | array of strings, pattern level | 1–4 lowercase Polish words; unique; ordered as authored | **optional**; absent on 267 of 269 patterns | Fixed lexical material that is part of the construction and not a fillable slot | staging lemma-level `requiredLexicalItems`, re-anchored to the owning pattern | `validPattern` allowed keys; `headlineFor`; `chipFor` unaffected | new optional field; rides the same `formatVersion 2`. HD-4C-02 |

No other field is added. No field is removed, renamed, or made required. No existing
enum member is removed — including `clauseKind: "czy"`, which is now unused by both
corpora but is retained because removing a legal value is a contract *narrowing* with no
benefit.

### 6.2 Placement of `requiredLexicalItems` in the four release dimensions

It belongs in **structure**, not wording, and this is the whole point of the field.

- `_structural_complements` deliberately strips `questionOverridePl` because question copy
  is *wording* — correctable in place through the correction workflow.
- `requiredLexicalItems` must behave like `relationType` and `complements`: changing it
  after release must require a replacement ID and a tombstone.

Placing it in structure gives D12 the "equally strong governed constraint" the handoff
demands, mechanically rather than by review discipline.

### 6.3 What is deliberately *not* extended

- No fifth `COMPLEMENT_TYPE` (4A2-2 §2 and the 4A2-1 B3 analysis both refuse it).
- No new `relationType`.
- No compound-preposition support (§10.4).
- No generalized-role or semantic-role metadata field (§10).
- No lemma-level metadata-aspect field (4A2-2 §1 point 8 forbids it).
- No progress-schema or migration-revision change (§20).
- No activity vocabulary change (§22).

---

## 7. Editorial → canonical mapping

Every staging field maps to exactly one destination. Nothing is dropped silently.

| Staging field | Destination | Rule |
|---|---|---|
| `canonicalLemma` | canonical `lemma.canonicalLemma` | verbatim; already NFC/trimmed/lowercase |
| `aspect` | canonical `lemma.aspect` | verbatim |
| — | canonical `lemma.reflexive` | **derived**: `normalize_canonical_lemma(...).endswith(" się")`; never authored |
| — | canonical `lemma.id` | **allocated** (§14) |
| `verificationOrder` | *not promoted* | traceability only; 4A2-2 §3 forbids it in any key or seed |
| `phase3Disposition`, `phase3Evidence`, `bindingConstraints` | canonical `pattern.evidence` + the 4C provenance ledger | §7.1 |
| `stagingReviewStatus` | *not promoted* | superseded by canonical `reviewState` + `reviewEvents` |
| `candidateMeaningKey` | canonical `meaning.key` | **verbatim, byte-for-byte** |
| `glossesEn` | canonical `meaning.glossesEn` | verbatim |
| `internalScope` | canonical `meaning.internalScope` | verbatim; private, pruned from runtime |
| `candidatePatternKey` | canonical `pattern.key` | **verbatim, byte-for-byte** |
| `meaningKeyRef` | structural parenthood | becomes the meaning→pattern nesting |
| `relationType`, `complements`, `cefr`, `teachingStatus`, `usage`, `learnerExplanationEn` | same-named canonical fields | verbatim, except `role: target → source` on the 7 D01 rows (HD-4C-01) |
| `candidateExampleKey` | canonical `example.key` | **verbatim** (always `primary`) |
| `patternKeyRef` | structural parenthood | becomes the pattern→example nesting |
| `pl`, `en` | canonical `example.pl` / `example.en` | verbatim |
| `candidateOrigin` | canonical `example.origin` | `editorial-generated` rows name the registered generator actor; the 4 `repository-reuse` rows must re-resolve byte-identically through the repository index |
| lemma-level `requiredLexicalItems` | canonical **pattern-level** `requiredLexicalItems` | re-anchored to the participation pattern only (§12) |
| `metadataAspectPartner` | *not promoted* | 4A2-2 §1: stays governance-only (§11) |
| — | canonical `activityEligibility` | **`[]` for all 224** (§22) |
| — | canonical `example.audioEligible` | **`true` for all 224** (§19) |
| — | canonical `contentRefs` | authored in 4C2; may be `[]` |
| — | canonical `errorNotes` | optional; authored only where evidenced |
| — | canonical `aspectPartnerIds` / `aspectEquivalentPatternIds` | **omitted for all** (§11.3) |
| — | canonical `reviewState`, `reviewEvents`, `releaseMode` | authored in 4C2 under the existing governance model |

### 7.1 Provenance

Staging carries `phase3Evidence` as `{verificationCsv, verificationOrder, primarySourceKey,
primarySourceLocator}`. Canonical `evidence` records require
`{sourceId, sourceKind, locator, factType, checkedAt}` with unique complete-record digests.
The mapping is mechanical for `locator`/`factType`, but `sourceId` must resolve in the
context `sourceRegistry` and `checkedAt` must be a real inspection date. Phase 4C2 must
therefore either register the Phase 3 sources or re-inspect; it must not synthesize a
`checkedAt`. `bindingConstraints` and `phase3Disposition` are **governance provenance**,
not `evidence` records: they belong in the 4C provenance ledger (§16), not in a field
whose digest is pinned by review events.

---

## 8. Role architecture (D01, D06)

### 8.1 The three role models

| Model | Vocabulary | Where it lives |
|---|---|---|
| **Editorial** | the canonical vocabulary plus `internalScope` prose, which may name any semantic role including ones with no structural realization (`GDZIE`, `SKĄD`, `KTÓRĘDY`, `KIEDY`) | staging / canonical `internalScope` (private) |
| **Canonical** | the closed enum: 10 released values **+ `source`** = 11 | canonical `complements[].role` |
| **Runtime** | identical to canonical; each value maps to exactly one English phrase | `ROLES` + `ROLE_PHRASES` |

**Editorial → canonical is lossy by design and the loss is registered, not hidden.** A
generalized role with no structural realization produces no complement and no pattern; it
survives in `internalScope` and in the §24 deferral register. Canonical → runtime is
**1:1 and total**: there is no mapping layer, and there must not be one.

### 8.2 D06 — granularity verdict

**Keep the coarse vocabulary. Change no existing assignment. Add exactly one value.**

The reconciliation examined the two live granularity questions and closed both:
`wiedzieć/accusative-known-content` using `content` where 19 peers use `object`, and one
`z` + Genitive form spanning `target`/`topic`/`object`. In each case both learner phrases
are accurate for their rows, no mechanical contradiction exists, and normalizing would
churn a guard, a digest and a test for no learner benefit. Proliferating roles to encode
distinctions the learner phrase already carries is exactly the failure mode §10 of the
task warns against.

`source` is different in kind. It is not a finer shade of `target`; it is its **opposite
direction**, and the runtime renders `target` as "what it is aimed at" — a phrase that is
not merely coarse but *inverted* for `Wracam z kina`.

### 8.3 D01 — recommended architecture: **OPTION A, add canonical/runtime role `source`**

**The seven affected rows** (all frozen keys already say *source*):

| Lemma | Meaning key | Pattern key | Complement |
|---|---|---|---|
| `wracać` | `return-to-earlier-place` | `z-genitive-return-source` | `z` + Genitive |
| `wrócić` | `completed-return-to-earlier-place` | `z-genitive-return-source` | `z` + Genitive |
| `wyjść` | `literal-exit-from-place` | `z-genitive-source` | `z` + Genitive |
| `wyjechać` | `transport-departure` | `z-genitive-source` | `z` + Genitive |
| `kupować` | `process-purchase` | `seller-price-schema` | `od` + Genitive (seller) |
| `kupić` | `completed-purchase` | `seller-price-schema` | `od` + Genitive (seller) |
| `zamawiać` | `commissioning-ordering` | `u-genitive-provider` | `u` + Genitive (provider) |

**Decisive evidence — the released corpus needs no migration.** Every released `target`
row was inspected individually: `szukać` Genitive, `słuchać` Genitive, `czekać na`,
`płacić za`, `prosić o` (×2), `dbać o`, `tęsknić za`, `wierzyć w`, `bać się` Genitive.
All ten are genuine targets. The one released origin-shaped complement,
`zależeć/depend-on/od-genitive-source`, already uses `topic`, not `target`, and "what it
is about" remains accurate for it. **Adding `source` changes zero released rows.** This
removes the single largest objection the 4B reconciliation raised against Option A.

**Exact change set.**

- `ROLES` gains `source` in `priority7_tooling.py`, `pp-verb-patterns.js`, and
  `validate_priority8_staging.py` (kept in sync by the §23 parity test).
- `ROLE_PHRASES.source` — recommended wording **"where it comes from"**, which reads
  correctly for a place (`Wracam z kina`), a seller (`kupuję od sąsiada`) and a provider
  (`zamawiam u stolarza`) alike.
- `ANIMATE_ROLES` is **not** changed. `source` stays on the inanimate diagnostic
  question, which is correct for the four motion rows.
- The three person-origin rows (`kupować`, `kupić`, `zamawiać`) use the **existing**
  optional `questionOverridePl: ["kogo?"]`, which `questionsFor` renders as `od kogo?` /
  `u kogo?`. This is a *wording*-dimension field, so it is correctable later without a new
  ID — exactly the right dimension for an animacy nicety. Note this also **repairs a
  pre-existing defect**: those rows currently render `od czego?` / `u czego?` for a human
  seller.

**Why not Option B (coarse role plus a projection/mapping layer).** It requires a
by-name exception list of seven patterns living somewhere between the corpus and the
renderer. That list is unauditable from the data, silently wrong for the eighth such row
whenever one is added, and directly contradicts the runtime's stated design that a role
is the *only* thing distinguishing two chips carrying the same case name. It also does
not remove the wrong value — it merely hides it, so search, chips and any future consumer
must each remember the exception.

**Why not Option C.** No third architecture was found that keeps the closed-enum model,
avoids an exception list, and does not invent a complement.

**Requirements check.** Learner/runtime never exposes these as "target" ✓ (the value is
gone, not masked). Frozen source/provider keys unchanged ✓. No fake syntactic distinction
✓ (`z`/`od`/`u` + Genitive is unchanged; only the role label moves). Existing 30 released
patterns backwards compatible ✓ (proven above). Deterministic ✓ (a fixed seven-row list
fixed at allocation).

**Status: HD-4C-01.** Recommended firmly; routed to the human because the identical
question was raised as HD-2 in Phase 4B and was never answered.

---

## 9. Clause / direct-speech architecture (D02)

### 9.1 Standing approval

Phase 4A2-2 §2 is **APPROVED, binding policy**, and Phase 4C0 confirms it without
amendment: direct speech stays inside the locked `clause` complement type as
`clauseKind: direct-speech`, with learner token `„…”` and label `Direct speech`. It must
not become a fifth complement type and must not collapse into `że`, `żeby`, `czy` or
generic interrogative-dependent.

The 11 frozen patterns are on `odpowiadać`, `czytać`, `pisać` (×2), `napisać` (×2),
`powiedzieć`, `zgadzać się` (×2), `polecać`, `radzić`. **None is removed for lack of
runtime support** — the runtime changes instead.

### 9.2 Exact canonical/runtime change set

| Location | Change |
|---|---|
| `priority7_tooling.py` `CLAUSE_KINDS` | `+ "direct-speech"` |
| `pp-verb-patterns.js` `CLAUSE_KINDS` | `+ "direct-speech"` |
| `pp-verb-patterns.js` `CLAUSE_TOKENS` | `+ "direct-speech": "„…”"` |
| `validate_priority8_staging.py` | already contains it; no change |
| `chipFor` / `headlineFor` / `searchText` | **no change** — all three key off `CLAUSE_TOKENS` generically |
| Parity test | new; asserts the Python set and the JS list are equal (§23) |

### 9.3 How direct speech differs, and why the schema still fits

Direct speech is a quoted independent utterance with no subordinator, so `clauseKind`
becomes "the discriminator for a clause-shaped complement" rather than strictly "the
subordinating conjunction". This is a real if narrow fidelity compromise, and it is
accepted because for every property the schema actually constrains — fills the clause
slot, forbids `case` and `preposition`, is a closed discriminated alternative, renders in
the same chip shape — direct speech behaves exactly like the other four.

### 9.4 Consumer tolerance, UI, IDs, validation, compatibility

- **Existing consumers do not tolerate the new value**, by design: `validComplement`
  rejects an unknown `clauseKind`, and rejection is whole-document. This is precisely why
  the contract moves to `formatVersion = 2` and why the loader and the corpus must ship in
  the same release.
- **UI**: the chip reads `+ „…” · Clause`; the headline appends `„…”` after the lemma. The
  token is Polish-tagged like every other clause token. Nothing new is authored per row.
- **Stable-ID consequences: none.** `clauseKind` appears in no seed. The eleven patterns
  would receive the same IDs whether allocated now or in a later revision — which is what
  makes D02 a class-B rather than class-A item.
- **Validation**: the parity test plus a positive canonical invariant asserting exactly
  11 `direct-speech` complements on exactly the frozen 11 pattern identities.
- **Backwards compatibility**: a stale cached `pp-verb-patterns.js` meeting a
  `formatVersion 2` corpus rejects it whole and shows the neutral unavailable state. That
  is a safe degradation, not a broken one, but it makes shell-cache/`APP_VERSION`
  ordering a mandatory Phase 4D (not 4C) responsibility.

### 9.5 `odpowiadać/direct-speech` — explicit adjudication as required

This row is a **documented private-staging policy addition**: its frozen Phase 3 evidence
lists only `clause:że`, and both the authoring and risk reports classify it as a policy
addition with canonical support deferred, not as a transcription of a source label.

**Verdict: PROMOTE.** Three independent grounds. (i) Phase 3B global constraint 9 binds
Phase 4 to preserve direct speech as one of exactly four clause distinctions, corpus-wide
and not per-lemma. (ii) The construction is uncontroversially grammatical for a verb of
answering, and the corpus teaches the identical alternative on seven other speech and
writing verbs. (iii) Rejecting it would delete a frozen candidate key, which is exactly
the act §2 forbids without reopening Phase 4B. Its `evidence` record must state the
policy-addition basis honestly rather than cite a Składnia row that does not license it.

---

## 10. Generalized-role policy (D03, D04, D05)

### 10.1 Uniform policy

> A verified generalized role that has **no** concrete realization in its own frozen
> source evidence receives **no** canonical complement, **no** canonical pattern, and
> **no** canonical semantic-role metadata field. It is preserved verbatim in the private
> `internalScope` it already occupies, and it is additionally listed in the Phase 4C
> deferral register, where the loss audit reconciles it.
>
> A verified generalized role that **does** have a documented concrete realization is
> already authored as that realization, hedged as non-exclusive, and needs nothing
> further.

**The critical rule holds absolutely: no generalized role is ever turned into an
unsupported concrete preposition pattern.** The Phase 4B mechanical audit found zero
unauthorized concretizations across all 18 families and the semantic pass confirmed the
hedging discipline is real rather than nominal. Phase 4C changes nothing here.

**Why no canonical semantic-role metadata field is introduced.** Such a field would be
private (pruned from runtime), so it would buy no learner value; it would be unvalidatable
against anything except the prose it was copied from; and it would create a second,
drifting home for information `internalScope` already holds. The task's option "expose
selected abstract participant information" is rejected for the same reason: exposing
"this verb also has a place role we cannot express" teaches a learner nothing actionable
and invites exactly the concretization the constraint forbids.

### 10.2 The deferred inventory — 9 generalized-role facts

| Lemma / scope | Position | Disposition |
|---|---|---|
| `pracować` | workplace `GDZIE` | omitted structurally; `internalScope` only |
| `przynosić` | optional generalized source/goal | omitted structurally |
| `pokazywać` | optional `GDZIE` | omitted structurally |
| `czytać` | generalized `GDZIE` | omitted structurally |
| `zapraszać` | separate `KOGO + GDZIE` schema | omitted structurally; the exact `na`/`do` constructions are authored and correctly **unhedged** |
| `wiedzieć` | `SKĄD` source-of-knowledge | omitted structurally; no `od`/`z` inferred |
| `uczyć` (school sense) | `GDZIE` | omitted structurally |
| `umówić się` | appointment `KIEDY` | omitted structurally — see §10.3 |
| corpus-wide | `KTÓRĘDY` | produces no authored row anywhere |

### 10.3 D04 — `umówić się` + `KIEDY`: one binding decision

**Decision: `KIEDY` receives no canonical representation. The omission is permanent and
is recorded as an architecture boundary, not as debt.**

Three grounds. (i) Its own frozen evidence gives it **no documented concrete
realization**; representing it would require inventing one, which the uniform policy and
the lemma's own binding constraint both forbid. (ii) It is an **adjunct boundary, not
valency**: a time expression attaches to almost any Polish predicate and is owned by
sentence grammar, not by this verb's Składnia — the same reasoning by which the corpus
keeps Genitive-of-negation grammar-owned (global constraint 8). (iii) It is **not
product-useful here**: the meaning's authored `na` + Accusative event slot already carries
the appointment content a learner needs, and the task explicitly forbids inventing a
complement to preserve source richness that is not learner-useful.

It must **never** be folded into the `do` + Genitive venue complement.

### 10.4 D05 — `co do` + Genitive

The Phase 4B preposition validator and the canonical validator share the same rule:
`PREPOSITION_RE = ^[a-ząćęłńóśźż]+$` — one lowercase Polish word. `co do` cannot be
expressed, and encoding it as `co` or `do` alone would be false.

Separating the two decisions exactly as the task requires:

- **Content admission — NO.** The `umówić się/mutual-agreement` meaning already teaches
  five representable alternatives (`na`, `o`, `że`, `żeby`, interrogative). A sixth,
  register-marked compound preposition adds negligible learner value to an already
  seven-pattern lemma. Admitting it would create a new pattern key and a new example key
  and therefore **require reopening Phase 4B**. Not recommended.
- **Architecture capability — NO, not now.** Building compound-preposition support with
  no admitted content would add an unexercised code path across two validators, the
  headline builder, the chip builder, `searchText` and the case-filter bucket logic, and
  would ship in a `formatVersion` bump whose other members are all in active use. The
  repository's own precedent (`vp-x-` exercise IDs: defined years before use, still
  unused) shows what that costs.

**Binding: `co do + Genitive` remains verified linguistic evidence with no canonical
representation.** It stays in `internalScope` and in the deferral register. Any future
admission requires a Phase 4B reopening *and* a preposition-model change, in that order.
It is **never** silently added.

---

## 11. Lexical / aspect identity policy (D11, D13)

### 11.1 Metadata-only identities — hard exclusion

`zaczynać` (under `zacząć`) and `przeczytać` (under `czytać`) are **verified lexical
identities that receive nothing**: no canonical lemma record, no meaning, no pattern, no
example, **no production ID of any family**, and no entry in any `aspectPartnerIds`
array. Their relationship survives only in the private staging `metadataAspectPartner`
objects and in governance prose, exactly as 4A2-2 §1 binds.

Leakage cannot occur accidentally because three independent mechanisms would each catch
it, and §23 makes all three explicit: a canonical lemma-set equality test pinning exactly
68 names; a name-absence test for both partners; and the arithmetic of the loss audit,
which reconciles 68 lemma IDs against 68 frozen lemma identities and would fail at 69 or
70.

### 11.2 Lexical `się` / `sobie` identities

`się` and `sobie` are part of `canonicalLemma`, so they are part of the normalized seed
and therefore part of the lemma ID by construction. Separation is structural, not
conventional:

- `radzić` vs `radzić sobie` — separate lemmas, separate IDs, no syntax exchange.
- `uczyć` (non-reflexive, new) vs `uczyć się` (**released**) — separate lemmas.
- `życzyć` vs `życzyć sobie` — an embedded `sobie` elsewhere never creates this identity.
- Identity-bearing across the corpus: `kłócić się`, `radzić sobie`, `spotykać się`,
  `spotkać się`, `umówić się`, `cieszyć się`, `martwić się`, `zgadzać się`.

**Verified for the released-overlap question (D11): the released 30 and the new 68 share
zero canonical lemma names.** `uczyć` ≠ `uczyć się` and `kochać` ≠ `lubić` at the identity
layer, so `LEMMA_IDENTITY_COLLAPSE` cannot fire and no merge is mechanically possible.
The remaining `uczyć się` and `lubić` overlaps are **product/curriculum integration
questions for Phase 4D**, not semantic or identity questions, and this report does not
resolve them.

### 11.3 Aspect independence

Eight full-record aspect families exist among the 68 (`wracać`/`wrócić`,
`kończyć`/`skończyć`, `kupować`/`kupić`, `pisać`/`napisać`, `spotykać się`/`spotkać się`,
`oglądać`/`obejrzeć`, `dawać`/`dać`, `brać`/`wziąć`). Each partner keeps independent
evidence and independent IDs.

**Policy: `aspectPartnerIds` and `aspectEquivalentPatternIds` are omitted for all 68.**
Three reasons: zero of the 30 released lemmas populate either field, so omission is the
established corpus convention; the validator requires links to be reciprocal, non-self,
and backed by an already-reviewed pattern on **both** ends, which is machinery no Phase 4C
requirement needs; and 4A2-2 §1 point 9 rules that learner-facing aspect navigation is a
separate holistic decision, not a Priority 8 side effect.

**No syntax inherits through any aspect relationship.** The specification is explicit that
links "never imply pattern inheritance", and the deliberate `pisać`/`napisać` requiredness
asymmetry — Dative required on `napisać`'s Dative+clause rows, optional on `pisać`'s — is
frozen, guarded, and must survive promotion byte-for-byte precisely because it proves the
two are authored independently.

### 11.4 D13 — `Czy mogę…?` packaging

The frozen representation is already correct and needs **no schema feature**:
`móc/permission/infinitive-permitted-action` has exactly one complement, `type:
infinitive`. `Czy mogę otworzyć okno?` lives in the example `pl` and in the learner
explanation, which states in terms that a permission request is this same construction
asked as a question.

**Protection is a preservation invariant, in three parts** (§23): the existing
`p8-4b-moc-no-question-clause` guard, whose signature was corrected from `czy` to
`interrogative` and is therefore now non-vacuous; a canonical invariant asserting that
neither `móc` pattern carries any complement of `type: clause`; and a standing constraint
on any future `vp-x-` activity authoring that a `móc` item may never present `czy` as a
governed complement.

---

## 12. `requiredLexicalItems` policy (D12)

### 12.1 The problem is demonstrable, not theoretical

`headlineFor` builds the pattern headline from `displayLemma` plus `complements` and
nothing else. `brać/fixed-participation/w-locative-participation-target` has exactly one
complement, `w` + Locative. The headline therefore renders as `brać + w czym?` — which
models `*biorę w konferencji`, an ungrammatical sentence, for a learner. The same applies
to `wziąć`.

This is the same class of harm as D01: not coarseness, but a generated learner-facing
string that is wrong.

### 12.2 Mechanisms examined and rejected

| Candidate | Why it fails |
|---|---|
| `displayLemma` | lemma-level; `brać` also owns `literal-taking`, which must **not** show `udział` |
| `questionOverridePl` | cannot position a word *before* the preposition — `questionsFor` prefixes the preposition to every override — and it lives in the **wording** dimension, so it is correctable in place and therefore not the immutable mechanism D12 requires |
| separate lemmas `brać udział` / `wziąć udział` | changes lemma identity, contradicts the Phase 3B frozen 68-lemma membership, and **requires reopening Phase 4B** |
| governance-only invariant with no schema change | mechanically strong for *preservation* — nothing can silently drop `udział` — but leaves the wrong headline shipping |

### 12.3 Recommendation

**Add `requiredLexicalItems` as an optional pattern-level array in the structure
dimension, and render it in the headline immediately after the lemma.** Applied to exactly
two patterns, producing `brać udział + w czym?` and `wziąć udział + w czym?`.

The cost argument is what makes this decisive. `formatVersion` is **already** moving 1 → 2
for direct speech (4A2-2 §9). Adding this field in the same increment costs one contract
change, not two, and it converts a review-discipline constraint into a mechanical one:
once the field is structural, removing `udział` after release raises
`FROZEN_COMPLEMENT_REPLACEMENT_REQUIRED`-class enforcement and demands a replacement ID
plus a tombstone.

**These patterns are never reduced to generic `verb + Accusative + w Locative`.** Note
that the frozen structure already contains **no** Accusative complement — `udział` was
never modelled as a fillable object — so the field records what the structure already
implies rather than adding a new claim.

**Status: HD-4C-02**, because Phase 4A2-2 §5 states that Priority 8 will not add this
field "solely for this need". That clause must be **narrowly reopened**. Its stated
reason — avoid a one-off field on a one-off need — is materially weakened now that the
contract is bumping anyway and the runtime harm is demonstrated. If the human declines,
the fallback is the governance-only invariant in §12.2, and the two headlines ship
knowingly imperfect; that fallback must then be recorded as accepted product debt, not
left implicit.

---

## 13. Stable-ID policy

**No stable ID is allocated, implemented, or persisted by this report.**

### 13.1 Recommended policy — one sentence

> Phase 4C uses the existing locked deterministic allocator in `priority7_tooling.py`
> **exactly as it stands**, seeded from the frozen candidate-key hierarchy, with no new
> generator, no new seed version, and no change to any released ID.

### 13.2 The two evaluated mechanisms

**Mechanism 1 — derive directly by hashing a canonical identity path.**
Deterministic; requires no persisted state; reruns are identical by construction; already
implemented; already validated live for every released entity, because
`allocationRegistry` is empty and `validate_editorial` therefore *recomputes* each of the
154 released IDs on every run. Its weakness is that a released ID would drift if its
identity inputs were ever corrected.

**Mechanism 2 — generate through a persistent mapping manifest.**
Immune to input drift; makes retirement and tombstones first-class. Its weakness is that it
introduces a second source of truth that can disagree with the corpus, and that nothing in
the repository currently maintains one — `allocationRegistry` is `{}` and no frozen
document is committed.

**Recommendation: Mechanism 1 as the generator, with Mechanism 2's guarantees already
supplied by the existing frozen-release machinery.** This is not a compromise; it is what
the repository already does. `freeze_editorial` records, for every entity, an allocation
row `{id, kind, parentId, key, seed, readableStem, canonicalLemmaAtAllocation,
meaningKeyAtAllocation}` and re-verifies that the retained seed reproduces the complete
original ID including its readable stem. The specification's own drift exception is
already written: a released ID is an identifier validated against its frozen allocation
record, **not** a live hash of mutable wording.

### 13.3 Requirements check

| Requirement | How it is met |
|---|---|
| Deterministic | SHA-256 over a fixed seed string; no counter, timestamp, array index, or ordering input |
| Based on frozen semantic identity, not mutable wording | seeds contain only the normalized lemma and the frozen keys; a changed gloss, explanation, example, CEFR or teaching status cannot move an ID |
| Collision checked | `ID_GLOBAL_DUPLICATE` at editorial and frozen level; `FROZEN_ALLOCATION_DUPLICATE`; family-letter prefixes make cross-namespace collision structurally impossible |
| Immutable after release | frozen `identity` snapshot; `FROZEN_IDENTITY_DRIFT` on any in-place `kind`/`parentId`/`key` change |
| Never recycled | `TOMBSTONE_RESURRECTION`; allocations are append-only |
| Tombstones reserved for retired identities | schema, validator and revision-window checks all exist (§17) |
| Existing production IDs unchanged | §15 |
| Reruns produce identical mapping | rehearsed twice in memory; byte-identical both times |
| Metadata-only identities handled explicitly | zero IDs; §11.1 |
| No syntax inherited through aspect relationships | seeds contain no partner reference; links omitted entirely (§11.3) |

### 13.4 Rehearsal result — architecture proof, no allocation

The locked allocator was run in memory over the frozen manifest. **No ID was written to
disk, printed, committed, or recorded anywhere, including in this report.** Only the
following aggregate facts were retained:

| Measure | Result |
|---|---|
| Prospective identities | **611** (68 lemma + 95 meaning + 224 pattern + 224 example) |
| Run-to-run identical | **yes**, byte-for-byte |
| Internally unique | **yes**, 611/611 |
| Collisions against the 154 released IDs | **0** |
| Union size | **765** |
| Malformed under the locked ID regexes | **0** |
| Lemma slugs reaching the 32-character truncation | **0** |
| Longest prospective identifier | 101 characters (no length cap exists; readability observation only) |

---

## 14. Identity-path definition

Repository archaeology **confirms** the conceptual path given in the task, with one
correction the task invited: **the lemma level has no key.** Lemma identity is the
normalized canonical lemma itself, so the frozen 543 keys map to 543 of the 611 IDs and
the remaining 68 come from lemma identity directly.

| Level | Identity input | Seed |
|---|---|---|
| Lemma | normalized canonical lemma | `v1\|lemma\|<normalized-canonical-lemma>` |
| Meaning | lemma ID + frozen `candidateMeaningKey` | `v1\|meaning\|<lemma-id>\|<meaning-key>` |
| Pattern | meaning ID + frozen `candidatePatternKey` | `v1\|pattern\|<meaning-id>\|<pattern-key>` |
| Example | pattern ID + frozen `candidateExampleKey` | `v1\|example\|<pattern-id>\|<example-key>` |
| Activity item (unused) | pattern ID + activity type + item key | `v1\|exercise\|<pattern-id>\|<activity-type>\|<item-key>` |

Each level's seed contains its **parent ID**, so ownership is inside the hash: moving a
pattern to another meaning necessarily produces a different ID. This is exactly why the
frozen ownership hierarchy — not merely the frozen key strings — is the identity input.

### 14.1 Normalization, serialization and truncation

1. **Unicode NFC** on all input text.
2. **Canonical lemma**: NFC, trim, collapse internal whitespace runs to one ASCII space,
   Unicode lowercase. The full normalized form — never the possibly truncated slug —
   enters the seed.
3. **Slug** (readability only): transliterate `ą ć ę ł ń ó ś ź ż → a c e l n o s z z`;
   replace each run outside ASCII `[a-z0-9]` with one hyphen; collapse repeats; trim; if
   longer than 32 characters take exactly the first 32 and drop a trailing hyphen. Must be
   non-empty. **Verified: no lemma among the 68 reaches truncation.**
4. **Keys** are already lowercase ASCII kebab-case and enter the seed verbatim.
5. **Seed serialization**: the `v1|…` string above, UTF-8 encoded, **no trailing
   newline**, fields joined by `|`.
6. **Digest**: SHA-256, **first 12 lowercase hex characters** (48 bits).
7. **Readable stem for children**: derived from the *owning pattern ID* by stripping
   `vp-p-` and the final hyphen-plus-12-hex — never reconstructed from current lemma text
   or keys. This is what keeps descendants stable across a permitted same-identity parent
   correction.

**No actual ID is produced in this task.**

---

## 15. Existing-ID compatibility

### 15.1 Recommended answer: **OPTION A — use the current deterministic generator exactly**

Not by analogy, but by proof. This audit re-derived every released ID from
`(canonicalLemma, meaningKey, patternKey, exampleKey)` — the meaning/pattern/example keys
recovered from each released ID's own readable stem — and compared against
`content/verb-patterns.json`:

| Family | Released | Reproduced exactly | Mismatched |
|---|---:|---:|---:|
| Lemma | 30 | 30 | 0 |
| Meaning | 34 | 34 | 0 |
| Pattern | 45 | 45 | 0 |
| Example | 45 | 45 | 0 |
| **Total** | **154** | **154** | **0** |

The generator is not a historical artifact; it is the live contract every existing ID
still satisfies.

**Option B (mapping manifest while leaving old IDs untouched)** is rejected as the
*primary* mechanism: it would create a registry that must agree with a corpus that already
carries its own IDs inline, and disagreement would be silent. Its useful half — a
persisted allocation record with seeds and tombstones — already exists inside
`freeze_editorial` and is retained (§16).

**Option C**: no other repository-supported mechanism exists.

### 15.2 The four compatibility guarantees

| Guarantee | Mechanism |
|---|---|
| Preserve all existing IDs byte-for-byte | the 68 are **added** to `editorial/verb-pattern-candidates.json`; no existing entity's `canonicalLemma`, `key`, or parenthood is touched, so no existing seed changes |
| Never recompute them into different values | released entities validate against their frozen allocation records; the specification's identifier-not-live-hash rule governs |
| Prevent collision with newly allocated IDs | `ID_GLOBAL_DUPLICATE` over the merged corpus; independently rehearsed at zero collisions across 765 identities (§13.4) |
| Keep existing references valid | zero lemma-name overlap between the corpora (§11.2); `contentRefs` point outward to cards and topics, never between verb-pattern entities; the runtime lemma index key is positional but session-only and never persisted (§5.7 item 6) |

---

## 16. Mapping-manifest design

**Recommendation: yes — create one private, derived, non-authoritative manifest in Phase
4C1.**

Its justification is narrow and specific: the frozen candidate-key layer lives in
`editorial/`, the allocated IDs will live in the canonical corpus, and **nothing would
otherwise record the join between them**. The loss audit (§24), the no-recycle policy
(§17) and any future question of the form "which frozen key produced this identity" all
need that join to be durable rather than re-derived.

| Property | Design |
|---|---|
| Path | `editorial/priority-8-phase4c-stable-id-map.json` |
| Status field | `artifactStatus: "priority-8-phase-4c-id-map-nonproduction"` |
| Key hierarchy | one row per identity: `{kind, canonicalLemma, meaningKey, patternKey, exampleKey, id, seedVersion, status}`, with unused key levels `null` |
| ID values | the allocated production IDs — **written in Phase 4C1, not here** |
| `status` | `active` \| `tombstoned` |
| Source freeze digest | `sourceCandidateKeyFreezeDigest` pinned to `0d636b3c…be27`; a mismatch is a hard stop |
| Allocation revision | `allocationRevision`, starting at 1, incremented only when rows are added or tombstoned |
| Collision metadata | not stored. Collisions are prevented structurally and detected by validation; a persisted "collision note" would be a record of something that must never exist |

**Four rules keep it from becoming an accidental source of truth.**

1. It is **derived**: a test recomputes every row from
   `editorial/priority-8-phase4-candidate-key-freeze.json` through the locked allocator
   and fails on any drift.
2. It is **never read** by `pp-verb-patterns.js`, `sw.js`, `index.html`,
   `freeze_editorial`, `verified_runtime_from_frozen`, or the audio pipeline. A test
   asserts the path appears in no runtime or service-worker file.
3. It is **never precached** and never copied to the public site.
4. On disagreement between the manifest and the canonical corpus, **the canonical corpus
   wins** and the run stops. The manifest is a witness, not an authority.

---

## 17. Tombstone / no-recycle policy

### 17.1 The rule

**An allocated ID is never deleted and never reused, for any reason, forever** — including
when no learner progress references it. A retired entity keeps its allocation row and gains
a tombstone row `{id, kind, formerParentId, retirementRevision, reason, replacementIds}`.
Enforcement already exists: a tombstone must have an allocation record, must agree with it
on `kind` and former parent, must carry a `retirementRevision` inside the frozen revision
window, must have unique non-self replacements resolving to *currently active* entities of
the same kind, and may never coexist with an active identity of the same ID
(`TOMBSTONE_RESURRECTION`). Every allocation must be exactly one of active or tombstoned.

### 17.2 Behaviour by retirement kind

| Event | Behaviour |
|---|---|
| **Retired** | tombstone with reason; `replacementIds: []`; ID never reissued |
| **Merged** | each absorbed identity tombstoned with `replacementIds` naming the survivor; the survivor keeps its own ID |
| **Replaced** | new identity allocated from its new key; old tombstoned with `replacementIds` naming the new one. Triggered by any structural change: `relationType`, complement identity, `requiredLexicalItems`, meaning boundary, or reparenting |
| **Removed from runtime only** | **not** a tombstone. Set `teachingStatus: deferred` or empty the eligibility allowlist; the identity stays active and allocated |

That last row is the distinction most easily got wrong: **runtime removal is a projection
decision, tombstoning is an identity decision.** A pattern absent from the public
projection is not retired.

### 17.3 Relationship between candidate-key retirement and tombstones

Candidate keys are frozen, so the three states are ordered and non-overlapping:

1. **Before allocation** — a candidate key may be replaced only by reopening Phase 4B.
   No tombstone exists or is possible, because no production identity exists.
2. **At allocation** — the key becomes the permanent seed input for exactly one ID. From
   this instant the key can no longer be "corrected": correcting it means retiring an ID.
3. **After release** — retiring a semantic identity means (a) tombstoning its ID, (b)
   marking the map row `tombstoned`, and (c) removing it from the public projection. The
   frozen candidate key itself is **never deleted** from the freeze manifest; the manifest
   is a historical record of what was frozen, not a live inventory of what ships.

A retired key is therefore never reused for a different semantic identity — doing so would
recycle its ID by construction, since the ID is a pure function of the key path.

---

## 18. Promotion policy

### 18.1 The pipeline

```
frozen staging (editorial/priority-8-phase4-staging.json, read-only from here on)
  → frozen candidate-key hierarchy (…-candidate-key-freeze.json, digest-verified)
    → stable-ID mapping (locked allocator; private ID map written)
      → canonical candidate projection (records appended to editorial/verb-pattern-candidates.json)
        → validation (validate_editorial → freeze_editorial → verified_runtime_from_frozen)
          → production runtime content (content/verb-patterns.json, revision 3)   [Phase 4D]
```

### 18.2 What is generated, hand-authored, frozen, recomputed, persisted

| Class | Items |
|---|---|
| **Generated** (never hand-typed) | all 611 IDs; `lemma.reflexive`; the readable stems; the private ID map; the frozen `allocations`/`identity`/`structure`/`wording`/`policy` snapshots; `releaseAuthorization`; the entire runtime projection |
| **Hand-authored in Phase 4C2** | `evidence` records; `reviewState` / `reviewEvents` / `releaseMode`; `contentRefs`; `errorNotes`; the seven `role: source` values (HD-4C-01); the three `questionOverridePl` animacy overrides; the two `requiredLexicalItems` values (HD-4C-02) |
| **Frozen** (copied verbatim, never re-decided) | 68 lemma identities; 543 candidate keys; ownership; `relationType`; `complements` (except the D01 role change); `cefr`; `teachingStatus`; `usage`; `learnerExplanationEn`; `glossesEn`; `internalScope`; example `pl`/`en` |
| **Recomputed every run** | the freeze digest; every new ID; every scope digest; the runtime projection bytes |
| **Persisted** | canonical corpus; private ID map; runtime file; authoring context. The frozen release document remains **transient**, with its predecessor reconstructed from a named commit, exactly as `priority8_phase1_transition.py` already does |

### 18.3 Promotion criteria

A frozen record is promoted when **all** of the following hold.

1. It is one of the 68 frozen full-pattern lemma identities. (Metadata-only identities are
   excluded permanently, §11.1.)
2. Its candidate keys are unchanged and the freeze digest recomputes exactly.
3. Its canonical record passes `validate_editorial` with zero issues.
4. It carries evidence, an approved `reviewState`, and the review events its
   `releaseMode` requires.
5. Its structure is expressible in the target canonical schema — which, after the three
   §6.1 extensions, is true of all 224 patterns.

### 18.4 Field-by-field promotion behaviour

- **active-production (222)** — promoted; recognition and production CEFR both present.
- **recognition-only (2)** — **promoted, not dropped.** `recognition-only` is a released,
  first-class `teachingStatus`; four released patterns already carry it and the runtime
  renders a dedicated recognition chip. The two rows are `pozwalać/zeby-enabling` and
  `wymagać/situation-requires-content/zeby-clause`, both `B1` recognition with no
  production level, both justified by an inanimate/abstract subject. Nothing in the
  product architecture demands their removal, so **no record disappears for being
  recognition-only.**
- **Examples** — all 224 promoted; exactly one per pattern; the 4 `repository-reuse` rows
  must re-resolve byte-identically through the repository index or promotion stops.
- **CEFR** — verbatim. Distribution `A1/A1` 60, `A1/A2` 7, `A2/A2` 98, `A2/B1` 57,
  `B1/—` 2. The validator's own rule (production must not precede recognition;
  active-production requires an A1–B1 production level) is satisfied by all 224.
- **Priority** — verbatim (116 core, 108 common).
- **Register** — verbatim `neutral` on all 224, including `kochać` + infinitive (D08).
- **Provenance** — §7.1.
- **Aspect metadata** — §11.3: aspect recorded per lemma; no partner links.
- **`requiredLexicalItems`** — §12.
- **Generalized-role metadata** — not promoted as data; registered as deferrals (§10).
- **Architecture-deferred information** — 10 items (§24.2), each with a written reason.

---

## 19. Audio boundary

**No audio is generated, and no audio file, manifest entry, or `audioEligible` value is
written by Phase 4C.** The existing architecture is kept unchanged; nothing here requires
a new audio component, a second manifest, or a change to the naming scheme.

| Question | Answer |
|---|---|
| Which canonical Polish strings become pronunciation-audio candidates? | Exactly the `example.pl` of every example whose `audioEligible` is `true` in the **released public runtime**. `pp_audio_rule.py::verb_pattern_audio_examples` already reads `content/verb-patterns.json` for precisely this. Prospective addition: **224** strings. Learner explanations, glosses, headlines, chips and internal scopes are **not** audio candidates. |
| How is exact reuse detected? | By the existing content hash. Normalize (strip `<[^>]+>`, collapse whitespace runs to one space, trim — no lowercasing, no punctuation or Unicode folding), then `sha256(normalized UTF-8)[:12]`. A hit in `audio-manifest.json` **is** reuse; no new clip is synthesized. |
| Examples, labels, or both? | **Examples only.** |
| When does `audioEligible` become true? | At canonical authoring in Phase 4C2, as `true` for all 224 — matching all 45 released examples. It is authorized because `patternDataRevision` is already ≥ 2 and the authoring context already sets `pronunciationPlaybackAuthorized: true`; the frozen-policy rule permits pronunciation independently of Listening from revision 2 onward. It authorizes **playback only** and never Listening. |
| How do audio filenames relate to stable semantic IDs? | **They do not, deliberately.** Audio identity is content-derived, so identical Polish across two patterns reuses one clip and a corrected sentence naturally moves to a new clip. Coupling audio names to `vp-e-` IDs would break both properties. |
| Does audio identity stay content-hash based? | **Yes.** No change. |

**Boundary conditions carried to the audio phase.** The 12-hex name is 48 bits, so the
generator must continue refusing a key that resolves to different text rather than
overwriting it. The service-worker audio cache has a 4,200-entry ceiling with a 4,000 trim
target and roughly 823 entries of headroom against 3,402 current manifest entries — adding
up to 224 clips fits, but the margin must be re-measured before generation, not assumed.
Reuse against 3,402 existing entries is expected to be low, because all 224 Polish
sentences are unique within the corpus and 220 of 224 are editorially generated.

---

## 20. Migration / versioning policy

Four version-like values exist and must not be confused.

| Value | Current | Phase 4C0 decision | Trigger |
|---|---|---|---|
| Verb Patterns `formatVersion` | `1` | **→ 2**, once, in Phase 4C2 | Any change to the closed public data contract. Three changes trigger it and all three land together: `clauseKind: direct-speech` (approved, 4A2-2 §9), `role: source` (HD-4C-01), `requiredLexicalItems` (HD-4C-02). |
| `patternDataRevision` | `2` | **→ 3**, in Phase 4D | `FROZEN_REVISION_TRANSITION` requires exactly `previous + 1` when the runtime payload changes. It is arithmetic, not a choice. |
| `PP_MIGRATE.SCHEMA_VERSION` | `2` | **unchanged** | Learner-progress storage shape. Untouched. |
| `PP_MIGRATE.CONTENT_MIGRATION_REVISION` | `2` | **unchanged** | Learner-progress migration. Untouched. |

**Why no progress migration is required — verified, not assumed.** Verb Patterns create no
durable learner mastery state; progress is keyed to cards and topics, never to `vp-*`
entities; `audioEligible` and `activityEligibility` already exist with their current
shapes; no storage key or record shape changes; no runtime field is removed or renamed;
there is no second envelope or parser; and no stable ID is recycled or translated. Every
one of the escalation conditions in `priority-8-schema-migration-analysis.md` is absent.

**Legacy mappings: none.** There is one envelope, one parser, and one contract.

**Implementation responsibility.** `formatVersion` moves in **4C2** (schema extensions),
because the canonical validator is the first thing that must accept the new values.
`patternDataRevision` moves in **4D**, computed by the transition script rather than typed.
`APP_VERSION`, the service-worker generation and the shell cache are **Phase 4D
responsibilities and are explicitly out of scope for every 4C subphase** — but they are
*mandatory* in 4D, because the loader and the corpus must ship together (§9.4).

---

## 21. Runtime consumer impact

| # | File | Current assumption | Required Phase 4C change | Risk | Test requirement |
|---|---|---|---|---|---|
| 1 | `pp-verb-patterns.js` — `FORMAT_VERSION` | exact equality with `1` | → `2` | **High**: a stale bundle rejects the whole new corpus | acceptance test at 2; rejection test at 1 and 3 |
| 2 | `pp-verb-patterns.js` — `CLAUSE_KINDS` / `CLAUSE_TOKENS` | four kinds, no `direct-speech` | add member + `„…”` token | Med | Python/JS parity test; token render test |
| 3 | `pp-verb-patterns.js` — `ROLES` / `ROLE_PHRASES` | ten roles, no `source` | add member + phrase | Med | every role has exactly one phrase; no row renders "what it is aimed at" for the 7 source rows |
| 4 | `pp-verb-patterns.js` — `validPattern` closed keys | no `requiredLexicalItems` | add to the optional list | **High**: an unknown key rejects the document whole | positive and negative shape tests |
| 5 | `pp-verb-patterns.js` — `headlineFor` | headline = lemma + complements | insert `requiredLexicalItems` after the lemma | Med | golden headline test for both participation patterns |
| 6 | `pp-verb-patterns.js` — `chipFor` / `questionsFor` | table-driven | **none** | Low | regression only |
| 7 | `pp-verb-patterns.js` — `searchText` | concatenates case names, prepositions, questions, clause tokens | **none** — new tokens flow through automatically | Low | search finds a direct-speech pattern |
| 8 | `pp-verb-patterns.js` — index/rows/filters | 30 lemmas; positional `lemma.key` | **none** | Low — verified session-only, never persisted, never in the URL hash | 98-lemma index build; no-persistence assertion |
| 9 | `pp-verb-patterns.js` — `isRecognitionOnly` / `eligibleFor` | closed-by-default allowlist | **none** | Low | 2 recognition chips; zero eligible patterns |
| 10 | `pp-verb-patterns.js` — `cardSupport` | card + `support` refs only | **none** | Low | contrast refs stay invisible |
| 11 | `pp-verb-patterns.js` — `grammarChooseDrill` | adapter over supplied `vp-x-` items | **none** — no exercise items exist | Low | unchanged |
| 12 | `priority7_tooling.py` — enums | four clause kinds, ten roles | mirror all three additions | **High**: must not drift from JS | parity test |
| 13 | `priority7_tooling.py` — `_structural_complements` / `_structure_for_entity` | strips `questionOverridePl` | include `requiredLexicalItems` in **structure** | Med | replacement-required test on mutation |
| 14 | `priority7_tooling.py` — `_runtime_pattern` | fixed projected field list | carry `requiredLexicalItems` when present | Med | projection round-trip |
| 15 | `validate_priority8_staging.py` | already accepts `direct-speech` | add `source` to `ROLES` for parity only | Low | staging still validates |
| 16 | `index.html` — `pRenderLemma` | renders headline, badge, chips, explanation, example, case links | **none** | Low | DOM test at 98 lemmas |
| 17 | `index.html` — audio button | keyed on `example.audioEligible` | **none** | Low | button appears for a new example |
| 18 | `pp_audio_rule.py` / `generate_audio.py` / `verify_audio.py` | read the released runtime | **none in 4C** | Low | required-set count moves 45 → 269 only after 4D |
| 19 | `sw.js` | precaches the loader and the runtime | **none in 4C**; `APP_VERSION`/cache generation is a 4D duty | **High if forgotten in 4D** | offline test after the 4D bump |
| 20 | `pp-migrate.js` / `validate_content.py` | learner-progress migration | **none** | Low | unchanged |

---

## 22. Activity-eligibility policy

**Verb Pattern activities remain absent. This is stated explicitly, as required.**

All 45 released patterns carry `activityEligibility: []`. Zero `vp-x-` activity items
exist anywhere in the repository. The only activity adapter, `grammarChooseDrill`, consumes
externally supplied items and never derives them from the runtime document.

**Decision: all 224 promoted patterns receive `activityEligibility: []`.** Phase 4A2-2 §8
binds Phase 4D to "no activity activation unless separately authorized", and the runtime
allowlist is closed by default, so an empty array is both the compliant value and the
fail-safe one.

**Main-surface visibility and production-activity eligibility are not the same thing, and
must not be conflated.**

- **Visibility** on the Verb Patterns reference surface follows from being projected at
  all. All 224 patterns — including both recognition-only rows — are visible.
- **Production-activity eligibility** follows from the allowlist alone. It is empty for
  all 224, so no pattern is practisable regardless of teaching status.

**Existing recognition-only semantics are preserved exactly**: the row renders with its
recognition chip, its badge shows only the recognition level, and the validator
independently forbids `grammar-build` and `type-it` for a recognition-only pattern — a
guarantee that stays live even though the allowlist is empty, so that a future activation
phase cannot accidentally make a recognition-only row productive.

---

## 23. Validation / test architecture (D09)

### 23.1 Strategy

**Prefer generated, property-style invariants derived from the freeze manifest and the
canonical projection schema over hand-written per-lemma guards.** The Phase 4B guard
registry is 74 hand-written rules covering 66 of 68 lemmas — Batch 1 has no declarative
semantic guards at all and Batch 2's are selective. Backfilling that unevenness by hand
would add dozens of rules that restate what a generated invariant proves once, uniformly,
for all 68.

**D09 verdict: the candidate-freeze test alone is *not* sufficient**, because it protects
the editorial identity layer and says nothing about the projection. The correct answer is
not "backfill semantic guards" either. It is **canonical-projection contract tests plus
generated invariants**, which give Batch 1 the same coverage as Batch 7 without writing a
single new lemma-specific rule. The existing 74 guards are retained unchanged; they are
not the mechanism being extended.

### 23.2 Required validators and tests

| # | Validation | Kind | Gate |
|---|---|---|---|
| 1 | Candidate-key freeze: digest, counts, hierarchy, ownership, manifest ≡ live | existing (retained unchanged) | every subphase |
| 2 | Stable-ID mapping: every map row recomputes through the locked allocator from its frozen key path | **generated** | 4C1 |
| 3 | ID collision: 765 identities globally unique; family prefixes correct; all match the locked regexes | **generated** | 4C1 |
| 4 | No-recycle: allocations append-only; no ID both active and tombstoned; tombstones resolve | existing + map assertion | 4C1 |
| 5 | Canonical schema: `validate_editorial` clean on the merged corpus | existing | 4C2 |
| 6 | Editorial → canonical loss audit: exact reconciliation (§24) | **generated** | 4C3 |
| 7 | Source-role projection: the 7 rows carry `role: source`; **no** projected complement anywhere renders "what it is aimed at" for a `z`/`od`/`u` origin | **generated** | 4C2 |
| 8 | Direct speech: exactly 11 `direct-speech` complements, on exactly the frozen 11 identities; token renders `„…”` | **generated** | 4C2 |
| 9 | Python/JS enum parity: `CLAUSE_KINDS`, `ROLES`, `COMPLEMENT_TYPES`, `RELATION_TYPES`, `TEACHING_STATUSES`, `CEFR_LEVELS`, `USAGE_PRIORITIES`, `REGISTERS`, `ACTIVITY_KEYS` | **generated**, parses the JS source | 4C2 |
| 10 | Lexical identity: `radzić`/`radzić sobie`, `uczyć`/`uczyć się`, `życzyć`/`życzyć sobie` are distinct lemma IDs; all 8 `się`/`sobie` lemmas keep their particle; every example's main predicate keeps it | **generated** | 4C3 |
| 11 | Aspect independence: 8 families keep independent IDs and evidence; **zero** `aspectPartnerIds` and `aspectEquivalentPatternIds` corpus-wide; the `pisać`/`napisać` requiredness asymmetry survives byte-for-byte | **generated** | 4C3 |
| 12 | Required `udział`: both participation patterns carry `requiredLexicalItems: ["udział"]`; both examples and both explanations contain `udział`; neither pattern has an Accusative complement | **generated** | 4C3 |
| 13 | Metadata-only exclusion: canonical lemma set equals exactly the 68 frozen names; `zaczynać` and `przeczytać` absent as lemma names and from every partner array | **generated** | 4C3 |
| 14 | Recognition-status preservation: exactly 222 active-production and 2 recognition-only, on exactly the frozen identities | **generated** | 4C3 |
| 15 | Existing-ID immutability: all 154 released IDs present, byte-identical, with unchanged parenthood and keys | **generated** | every subphase from 4C2 |
| 16 | Round-trip determinism: two full projection runs are byte-identical; the runtime file is reproducible from the canonical corpus | existing pattern (`priority8_phase1_transition.py`) | 4C3 |
| 17 | `Czy mogę` preservation: no `móc` pattern has any `clause` complement; the guard signature is `interrogative`, not `czy` | **generated** | 4C3 |
| 18 | Generalized-role boundary: no canonical complement exists for any of the 9 registered deferrals; no new preposition appears that is absent from staging | **generated** | 4C3 |
| 19 | Activity closure: `activityEligibility == []` on all 269 patterns; zero `vp-x-` identities | **generated** | 4C3 |
| 20 | Audio boundary: `audioEligible == true` on all 269; no audio file or manifest entry is written by any 4C subphase | **generated** | 4C3 |

Existing coverage is **retained in full**: `validate_priority8_staging.py`, the twelve
Phase 4B suites (**297 tests**), the seven batch digests and the four SHA-locked matrices.
No historical lock is edited by any Phase 4C subphase.

---

## 24. Loss-audit design

### 24.1 Principle

> Every frozen semantic identity is either **promoted** to exactly one production
> identity, or **explicitly architecture-deferred with a written reason**. There is no
> third outcome, and silence is a failure.

### 24.2 The accounting model

**Ledger A — identity promotion. Must reconcile exactly.**

| Frozen input | Count | Production output | Count | Rule |
|---|---:|---|---:|---|
| Full-pattern lemma identities | 68 | `vp-l-` identities | 68 | 1:1 |
| `candidateMeaningKey` | 95 | `vp-m-` identities | 95 | 1:1 |
| `candidatePatternKey` | 224 | `vp-p-` identities | 224 | 1:1 |
| `candidateExampleKey` | 224 | `vp-e-` identities | 224 | 1:1 |
| **Frozen keys** | **543** | **key-derived identities** | **543** | **1:1** |
| — | — | **total new identities** | **611** | 543 + 68 |
| Metadata-only identities | 2 | production identities | **0** | by policy (§11.1) |

**Ledger B — the deferral register. Every row needs a written reason.**

| # | Item | Class | Reason |
|---|---|---|---|
| 1–7 | `GDZIE`/`SKĄD`/source-goal on `pracować`, `przynosić`, `pokazywać`, `czytać`, `zapraszać`, `wiedzieć`, `uczyć` | generalized role | no concrete realization in the frozen evidence; inventing one is forbidden (§10.1) |
| 8 | `umówić się` `KIEDY` | generalized role | adjunct boundary, not valency; not product-useful (§10.3) |
| 9 | `KTÓRĘDY` corpus-wide | generalized role | produces no authored realization anywhere |
| 10 | `umówić się` `co do` + Genitive | compound preposition | not expressible; not admitted; admission needs a Phase 4B reopening (§10.4) |

**Ledger C — post-promotion corpus totals.**

| Level | Released | Promoted | Total |
|---|---:|---:|---:|
| Lemmas | 30 | 68 | **98** |
| Meanings | 34 | 95 | **129** |
| Patterns | 45 | 224 | **269** |
| Examples | 45 | 224 | **269** |
| **IDs** | **154** | **611** | **765** |

### 24.3 Mechanism

The audit is a **deterministic set comparison**, not a review. It walks the freeze manifest
and the canonical corpus in parallel, keyed by identity path, and emits one of exactly
three verdicts per frozen key: `PROMOTED` (with its ID), `DEFERRED` (with a register
reference), or `MISSING`. **Any `MISSING`, any deferral without a register row, any
unmatched production identity, and any count disagreement is a hard stop.** Ledger C is
asserted independently so that an equal-but-wrong pairing cannot pass.

---

## 25. Phase 4C subphase plan

Narrow, independently reviewable gates. No giant implementation.

### 4C1 — stable-ID allocator verification and mapping tooling

- **Goal**: prove the locked allocator against the frozen manifest; write the private ID
  map; add the mapping, collision, no-recycle and existing-ID-immutability tests.
- **Allowed files**: `editorial/priority-8-phase4c-stable-id-map.json` (new);
  `tests/test_priority8_phase4c1_stable_ids.py` (new);
  `reports/priority-8-phase-4c1-*.md` (new).
- **Expected artifacts**: the ID map; the test suite; an allocation report.
- **Best model**: **CODEX** — pure deterministic tooling against a locked algorithm.
- **Review gate**: 154 released IDs unchanged; 611 new identities unique; zero collisions;
  two runs byte-identical; canonical corpus and runtime untouched.

### 4C2 — canonical schema extensions

- **Goal**: land exactly the three §6.1 extensions plus `formatVersion` 1 → 2, with parity
  tests. **No content is promoted in this subphase.**
- **Allowed files**: `priority7_tooling.py`; `pp-verb-patterns.js`;
  `validate_priority8_staging.py` (role parity only);
  `tests/test_priority8_phase4c2_schema.py` (new); existing Priority 7 suites as required
  by the version change; `reports/priority-8-phase-4c2-*.md` (new).
- **Expected artifacts**: the extended contract; the enum parity test; the direct-speech
  and source-role render tests; a schema-change report.
- **Best model**: **CODEX** for the mechanical, cross-language change; **SONNET** for the
  report.
- **Review gate**: all existing Priority 7 and Priority 8 suites pass; `formatVersion 2`
  accepted and 1 and 3 rejected; Python/JS enums equal; the released 30-lemma corpus still
  validates and projects **byte-identically** at revision 2 under the new contract.

### 4C3 — deterministic canonical projection

- **Goal**: author the 68 canonical records, allocate the 611 IDs through the locked
  allocator, run the loss audit, and land the §23 invariants.
- **Allowed files**: `editorial/verb-pattern-candidates.json` (append only);
  `editorial/priority-7-authoring-context.json` (registries only);
  `editorial/priority-8-phase4c-stable-id-map.json` (ID values);
  `priority8_phase4c_promotion.py` (new);
  `tests/test_priority8_phase4c3_projection.py` (new);
  `reports/priority-8-phase-4c3-*.md` (new).
  **`content/verb-patterns.json` is NOT touched.**
- **Expected artifacts**: the promoted canonical corpus; the completed ID map; the loss
  audit; a promotion report.
- **Best model**: **CODEX** for projection and validation; **OPUS** for the evidence and
  provenance mapping (§7.1), which requires judgement about what a source actually
  licenses; **SONNET** for the reports.
- **Review gate**: loss audit reconciles exactly (611 / 0 missing / 10 registered
  deferrals); all 154 released IDs byte-identical; 98/129/269/269; 222/2 preserved; zero
  `vp-x-`; all §23 invariants pass.

### 4C4 — canonical governance and release readiness

- **Goal**: complete review events and release authorization for the 68 under the existing
  governance model. Still no runtime projection.
- **Allowed files**: `editorial/verb-pattern-candidates.json` (review events only);
  `editorial/priority-7-authoring-context.json`; `reports/priority-8-phase-4c4-*.md`.
- **Best model**: **OPUS** for adjudicating review scope and authority; **CODEX** for
  digest-bound event mechanics.
- **Review gate**: `freeze_editorial` succeeds; `releaseAuthorization` is complete; no
  authority is invented; `activityEligibility` empty; no runtime file changed.

### 4C5 — projection rehearsal and release validation

- **Goal**: rehearse `verified_runtime_from_frozen` at revision 3 **without writing** the
  runtime file; measure and report the consequences for 4D.
- **Allowed files**: `tests/test_priority8_phase4c5_release.py` (new);
  `reports/priority-8-phase-4c5-*.md` (new).
- **Expected artifacts**: rehearsal report covering projected counts, the exact
  `patternDataRevision` transition, the 224 prospective audio strings with measured reuse,
  the service-worker cache-headroom measurement, and the `APP_VERSION`/deployment ordering
  handoff.
- **Best model**: **CODEX** for the rehearsal; **OPUS** for the 4D risk assessment.
- **Review gate**: rehearsal projects cleanly; revision computes to exactly 3; **zero**
  bytes written to `content/`, `audio/`, `audio-manifest.json`, `sw.js` or `index.html`.

**Phase 4D** (out of Phase 4C scope entirely) then performs the runtime projection,
`APP_VERSION` and service-worker generation, audio generation and QA, and release
integration.

---

## 26. Human decision table

Only genuine unresolved choices appear. Every other decision in this report is settled by
repository evidence and is not routed to a human.

| Decision ID | Topic | Recommended option | Alternative | Reason | Implementation consequence | Runtime consequence | Key impact | Requires Phase 4B reopening? |
|---|---|---|---|---|---|---|---|---|
| **HD-4C-01** | D01/D06 — origin/provider role on 7 rows | **Add `source` to the role enum**; phrase "where it comes from"; keep it out of `ANIMATE_ROLES`; use the existing `questionOverridePl` for the 3 person-origin rows | Keep `target` and add a projection-mapping rule that suppresses the `target` phrase for these 7 rows | The 7 frozen keys already say *source*; the runtime renders `target` as "what it is aimed at", which is directionally inverted. **Verified: zero released rows migrate** — the only released origin complement (`zależeć/od-genitive-source`) already uses `topic`. The alternative needs an unauditable by-name exception list that the next such row would silently miss. | `ROLES` + `ROLE_PHRASES` in 3 files; 7 canonical role values; 3 `questionOverridePl` values; rides the already-approved `formatVersion 2` | 7 patterns render "where it comes from" instead of "what it is aimed at"; 3 gain the animate diagnostic question | **None** — keys already encode *source* and are durable either way | **No** |
| **HD-4C-02** | D12 — required `udział` | **Add optional pattern-level `requiredLexicalItems` in the structure dimension**, rendered in the headline after the lemma | Governance-only invariant with no schema change; accept `brać + w czym?` as shipped product debt | The headline is generated purely from lemma + complements, so today it models the ungrammatical `*biorę w konferencji`. Structure placement makes the constraint mechanical (post-release change ⇒ replacement ID + tombstone) rather than review-dependent. `formatVersion` is bumping anyway, so the marginal contract cost is one field, not one version. | One optional field in `priority7_tooling.py`, `pp-verb-patterns.js` and the structure snapshot; 2 canonical values | 2 headlines read `brać udział + w czym?` / `wziąć udział + w czym?` | **None** | **No** — but it **narrowly reopens Phase 4A2-2 §5**, which must be recorded explicitly |

**Deliberately not escalated**, because the evidence makes one answer clearly superior:
the direct-speech representation and its token (approved at 4A2-2 §2); using the existing
allocator rather than a new one (154/154 reproduction); the identity path (repository
archaeology); `formatVersion 2` and `patternDataRevision 3` (approved policy plus
`FROZEN_REVISION_TRANSITION` arithmetic); no aspect links (zero released precedent plus
validator requirements); `activityEligibility: []` (approved policy plus closed-by-default
runtime); `audioEligible: true` (revision ≥ 2 policy already in force); promoting both
recognition-only rows (released precedent); D03/D04/D05 boundaries (frozen evidence);
D07 (`EXPERIENCER_ROLES_REQUIRED` makes the alternative invalid); D08 (no governed
register evidence); D13 (already correct); retaining `clauseKind: "czy"` in the enum
(removal is a narrowing with no benefit).

---

## 27. No-ID proof

| Check | Result |
|---|---|
| New stable production IDs allocated | **ZERO** |
| Files added by this task | **one** — `reports/priority-8-phase-4c0-architecture-freeze.md` |
| Existing files modified | **none** |
| `editorial/` changed | **no** |
| `content/` changed | **no** |
| `audio/`, `audio-manifest.json` changed | **no** |
| `sw.js`, `index.html`, `APP_VERSION` changed | **no** |
| Strings in this report matching an allocated-ID shape (`vp-[lmpex]-…-[0-9a-f]{12}`) | **zero** |
| Concrete placeholder IDs written | **none** — the report deliberately writes no example ID at all, synthetic or otherwise |

Where an ID family must be named, only its **prefix** appears (`vp-l-`, `vp-m-`, `vp-p-`,
`vp-e-`, `vp-x-`) or its **format template** with no digest. No string in this document can
be mistaken for an allocated identifier.

The §13.4 rehearsal ran the allocator **in memory only**. Its 611 outputs were counted and
compared and were never written to disk, printed into any artifact, or recorded here. The
repository contains no new production ID.

---

## 28. Phase 4C1 entry gate

Phase 4C1 may begin only when **all** of the following hold.

1. `HD-4C-01` and `HD-4C-02` are answered by the human.
2. The freeze manifest exists with `status = frozen` and the digest recomputes from live
   staging to `0d636b3c81c15f51e36558ef5d9c18e35b189b5f5a143003c283b4732f33be27`.
3. The hierarchy is exactly 68 / 95 / 224 / 224 / 543, split 222 active-production and 2
   recognition-only.
4. `python3 validate_priority8_staging.py` passes.
5. The twelve Phase 4B/freeze suites pass at 297 tests.
6. No unexpected stable production ID exists.
7. Work begins from the commit containing this architecture freeze.
8. Every 4C1 change is confined to the three allowed paths in §25.

**Phase 4C1 must stop** if the key projection differs, if any released ID fails to
reproduce, or if any human decision above is answered in a way that changes the identity
path. A candidate-key rename, removal, reassignment, reparenting, reuse or addition still
requires an explicit Phase 4B governance reopening. Nothing in this report requests one.

---

## Appendix A — test and safety results

| Check | Result |
|---|---|
| `python3 validate_priority8_staging.py` | **PASS** — "Priority 8 4B7 staging revision 8 is read-only valid (68 lemmas, 21 constrained records, 12 global constraints)" |
| Twelve Phase 4B/freeze suites together via `python3 -m unittest` | **297 tests, OK** |
| Candidate-key freeze digest, recomputed from live staging | exact |
| Candidate-key freeze digest, recomputed from the manifest hierarchy | exact |
| Released ID reproduction through the locked allocator | **154/154 exact, 0 mismatches** |
| Prospective identity rehearsal (in memory, nothing written) | 611 unique, deterministic, 0 collisions with the released 154 |
| `git status --short` | single added path: this report |
| `git remote -v` | zero remotes |
| `git config --get push.default` | `nothing` |
| Pre-push hook | executable, fail-closed (exit 1) |
| Existing artifacts changed | **none** |

Candidate semantic keys remain frozen. Stable production IDs are **not** yet allocated.
