# Priority 8 Phase 4B5 — Batch 5 schema matrix

## 1. Starting state

This is a **control-plane authoring plan** produced before any Batch 5
`candidateContent` is written. It is not candidate content, not a staging
schema, not runtime data, and it allocates no stable ID. It adds no field to
the locked Phase 4B candidate-content schema.

Starting endpoint, verified before any file was created:

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `98d068d4c596031e2525991c2918d49c4236f8c3`
- tree `15abd72ede844c69287cc06f3b0c4ba3fafd6a47`
- parent `878511063d61710908901c4ddcf90b5feb834262`
- subject `Clarify Priority 8 Phase 4B4 report arithmetic`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook

Recorded content invariants (must remain byte-identical through this task):

- `editorial/priority-8-phase4-staging.json` SHA-256
  `0f26b17238ec1abe984145fd7a6c232419465a5baec1f59a3a14e23d93295f8c`
- `tests/fixtures/priority8_phase4b_authoring_rules.json` SHA-256
  `3caab1419f14718ed7c82b5fea4eb5fac3326160864c88decd88ca13b6277db0`

Recomputed staging logical state (not taken on trust):

| Quantity | Value |
|---|---:|
| `phaseStep` | `4B4` |
| `stagingRevision` | 5 |
| authored full-pattern lemmas | 39 |
| meanings | 51 |
| patterns | 124 |
| examples | 124 |
| future-empty full-pattern lemmas | 29 |

Scoped Phase 4B test baseline recomputed: **190 tests** across the eight
suites (31 + 65 + 9 + 11 + 17 + 23 + 8 + 26).

## 2. Exact Batch 5 scope

Exactly these ten full-pattern lemmas, all `full_pattern_in_phase4 = yes` in
the Phase 3B freeze:

| Order | Lemma | Aspect | Phase 3 disposition |
|---|---|---|---|
| 42 | `oglądać` | imperfective | KEEP VERIFIED |
| 43 | `obejrzeć` | perfective | KEEP VERIFIED |
| 44 | `skończyć` | perfective | KEEP VERIFIED |
| 45 | `chcieć` | imperfective | KEEP VERIFIED |
| 46 | `robić` | imperfective | KEEP VERIFIED |
| 47 | `rozumieć` | imperfective | KEEP VERIFIED |
| 48 | `mieszkać` | imperfective | **KEEP WITH NARROWING** |
| 49 | `umówić się` | perfective | **KEEP WITH NARROWING** |
| 50 | `dzwonić` | imperfective | **KEEP WITH NARROWING** |
| 51 | `powiedzieć` | perfective | KEEP VERIFIED |

No metadata-only identity falls inside Batch 5. Orders 17 (`zaczynać`) and 37
(`przeczytać`) are the only metadata-only identities and both lie outside this
range. None of the ten carries `metadataAspectPartner` or
`requiredLexicalItems` in the frozen skeleton.

Batch 6 material was consulted **only** for order 51 `powiedzieć`, which the
frozen seven-batch map places in Batch 5 while its Phase 3 verification row
lives in the Batch 06 files. No other Batch 6 lemma was planned or authored.

## 3. Source hierarchy

Binding source hierarchy, in order of authority:

1. `reports/priority-8-phase-3-batch-05.md` (+ risk review, verification CSV)
   — orders 42–50.
2. `reports/priority-8-phase-3-batch-06.md` (+ risk review, verification CSV)
   — order 51 `powiedzieć`.
3. `reports/priority-8-phase-3-final-synthesis.md`.
4. `reports/priority-8-phase-3b-final-lemma-freeze.{csv,md}`,
   `reports/priority-8-phase-3b-phase4-handoff.md`,
   `reports/priority-8-phase-3b-risk-review.md`.
5. Phase 4B control documents:
   `reports/priority-8-phase-4b1a-authoring-schema-lock.md`,
   `reports/priority-8-phase-4b4-schema-matrix.md`,
   `reports/priority-8-phase-4b-authoring-guard-hardening.md`,
   `reports/priority-8-phase-4b-test-lifecycle.md`.

**No fresh web research was performed.** No construction was broadened from
intuition.

### 3.1 How the two evidence layers were read (methodological note)

The verification CSV field `supported_constructions_structured` is a **flat
complement inventory**, not a per-schema grouping. It was calibrated against
Batch 4, whose product answers are already frozen and approved:

- Order 32 `dawać` — flat `case:Accusative;case:Dative` became **one** product
  schema with **both required**.
- Order 36 `czytać` — six flat entries became **five** product alternatives
  whose requiredness the flat list cannot express (`o+Locative` is required in
  alternative 2 but optional in alternatives 3–4, yet appears unmarked once).
- Order 38 `pisać` — nine flat entries were placed on **HOLD** in Batch 4
  precisely because the repository text was a *compressed characterization*,
  not a per-schema enumeration.

The flat CSV field therefore **cannot** by itself settle schema cardinality,
per-alternative requiredness, or optional-participant attachment. The
authoritative per-schema layer is the narrative report's per-lemma section,
which quotes the WSJP `Składnia` notation with explicit parenthesised
optionality (`GDZIE + (z KIM)`, `CZEGO + (od KOGO) + (dla KOGO)`), grouped
alternatives (`że ZDANIE|ZDANIE PYTAJNOZALEŻNE`), and explicit schema counts.
Every row below is derived from that narrative layer, cross-checked against
the CSV; where the narrative layer is itself compressed, the row is **HOLD**.

## 4. Full schema matrix

Complement notation: `type:value role=... required|optional`.

### Order 42 — `oglądać` (imperfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `processual-viewing` |
| meaningScope | Processual or habitual viewing of a film, programme, performance, or other visual content (WSJP sense 2). |
| schemaKeyProposal | `accusative-content-optional-presentation-context` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | `preposition-case:w+locative role=target optional` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable — the optional `w + Locative` is an **exact** listed position (`phase3_representation_fit = compatible`, no narrowing), not a realization of a generalized role |
| subjectOrParticipantRestriction | — |
| explicitExclusions | viewing place, time, frequency, manner, device, medium; generalizing the `w` position to every cinema/television/screen/medium phrase; inheriting anything from `obejrzeć` |
| evidenceSource | Batch 05 §42; `WSJP-OGLAD-02`, sense 2 — exact `KOGO/CO + (w CZYM)` |
| proposedLiveGuard | `require-exact-pattern-shapes` (A) |

### Order 43 — `obejrzeć` (perfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `completed-viewing` |
| meaningScope | Completed viewing resulting in acquaintance with a film, programme, performance, or other visual content (WSJP sense 2). |
| schemaKeyProposal | `accusative-content` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | **no `w + Locative` imported from `oglądać`**; cinema, television, screen, time, manner, purpose, recommendation expressions |
| evidenceSource | Batch 05 §43; `WSJP-OBEJRZ-02`, sense 2 — independently exact `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (B) |

### Order 44 — `skończyć` (perfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `activity-completion` |
| meaningScope | Bringing a noun- or infinitive-denoted activity to completion (WSJP sense 1). |
| schemaKeyProposal | **A1** `accusative-task` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | completion time, deadline, place, manner, result circumstances; `z + Instrumental`; inheritance from `kończyć` |
| evidenceSource | Batch 05 §44; `WSJP-SKONCZ-01`, sense 1 — `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (C) |

| Field | Value |
|---|---|
| schemaKeyProposal | **A2** `infinitive` |
| requiredComplements | `infinitive: role=content required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | as A1 |
| evidenceSource | Batch 05 §44; `WSJP-SKONCZ-01`, sense 1 — `BEZOKOLICZNIK` |
| proposedLiveGuard | `require-exact-pattern-shapes` (C) |

### Order 44 — `skończyć` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `definitive-cessation` |
| meaningScope | Colloquial definitive ceasing of an activity or habit (WSJP sense 4). A separate sense, not a variant of task completion. |
| schemaKeyProposal | `z-instrumental-ceased-activity` |
| requiredComplements | `preposition-case:z+instrumental role=topic required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | adding `z + Instrumental` to any completion-sense pattern; treating cessation as a completion variant |
| evidenceSource | Batch 05 §44; `WSJP-SKONCZ-01`, sense 4 “z nałogiem” — separately `z CZYM` |
| proposedLiveGuard | `require-exact-pattern-shapes` (C) |

### Order 45 — `chcieć` (imperfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `desire` |
| meaningScope | Desire for an object, one's own action, or an event/state (WSJP sense 1). |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | flattening object-wanting, action-wanting, event-wanting and polite request into one maximal template; purpose, reason, degree, contextual beneficiary outside the exact schemas; **directly listed adverbial `JAK`, which lies outside the locked four complement types and creates no new type** |
| evidenceSource | Batch 05 §45; `WSJP-CHCIEC-01`, sense 1 — `CZEGO + (od KOGO) + (dla KOGO)`, `BEZOKOLICZNIK`, `żeby ZDANIE`, `JAK` |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| A1 | `genitive-desired-object` | `case:genitive role=object required` | `preposition-case:od+genitive role=target optional`; `preposition-case:dla+genitive role=recipient optional` | — |
| A2 | `infinitive-own-action` | `infinitive: role=content required` | — | — |
| A3 | `zeby-desired-event` | `clause:zeby role=content required` | — | `zeby` |

Proposed live guard: `require-exact-pattern-shapes` (D).

### Order 45 — `chcieć` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `polite-request-or-intention` |
| meaningScope | First-person polite request or stated intention (WSJP sense 3). |
| subjectOrParticipantRestriction | **First-person past/conditional usage restriction** (`chciałem/chciałabym…`). No field in the locked schema expresses this; it must be carried in `internalScope` and `usage.note`. |
| requiredLexicalMaterial | — |
| explicitExclusions | conflation with ordinary desire; importing `od`/`dla` participants from the desire sense; one maximal object + infinitive + `żeby` frame |
| evidenceSource | Batch 05 §45; `WSJP-CHCIEC-01`, sense 3 — separately `CO`, `BEZOKOLICZNIK`, `żeby ZDANIE` |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| B1 | `accusative-requested-object` | `case:accusative role=object required` | — | — |
| B2 | `infinitive-intended-action` | `infinitive: role=content required` | — | — |
| B3 | `zeby-requested-event` | `clause:zeby role=content required` | — | `zeby` |

Proposed live guard: `require-exact-pattern-shapes` (D).

**Case contrast is load-bearing.** Desire sense takes **Genitive**; polite
request sense takes **Accusative**. That contrast, plus the optional
`od`/`dla` positions occurring only in the desire sense, is what keeps the two
meanings structurally distinguishable under `require-exact-pattern-shapes`.

### Order 46 — `robić` (imperfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `entity-creation` |
| meaningScope | Making or creating an entity (WSJP sense 1). |
| schemaKeyProposal | `accusative-created-entity` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | materials, tools, place, purpose, beneficiary, time, manner; merging with the activity sense on shared Accusative morphology |
| evidenceSource | Batch 05 §46; `WSJP-ROBIC-01`, sense 1 “kotlety” — exact `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (E) |

### Order 46 — `robić` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `activity-performance` |
| meaningScope | Performing the activity named by an adjacent noun (WSJP sense 2). |
| schemaKeyProposal | `accusative-activity-noun` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | **promoting individual `robić + noun` collocations into separate governed frames**; merging with the creation sense |
| evidenceSource | Batch 05 §46; `WSJP-ROBIC-01`, sense 2 “pranie” — separately exact `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (E) |

**Representation note.** The two meanings are structurally *identical*
(`case:accusative role=object required`). `require-exact-pattern-shapes` with
`exactMeaningSet: true` still pins the meaning inventory and one shape per
meaning, but **no guard can distinguish creation from activity-performance
structurally**. The sense split is carried by `candidateMeaningKey`,
`internalScope`, `glossesEn`, the learner explanation, the example, the
historical lock, and independent review. This is a documented limitation, not
a defect introduced here.

### Order 47 — `rozumieć` (imperfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `content-comprehension` |
| meaningScope | Comprehending communicated or represented content (WSJP sense 1). |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | degree, manner, language of presentation, information source, circumstances; merging with the person sense; treating `how`/`why`/`what` as separate frames rather than instances of one interrogative-dependent clause type |
| evidenceSource | Batch 05 §47; `WSJP-ROZUM-01`, sense 1 “dowcip” — `CO` and an alternative `że ZDANIE\|ZDANIE PYTAJNOZALEŻNE` |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| A1 | `accusative-content` | `case:accusative role=object required` | — | — |
| A2 | `ze-content-clause` | `clause:ze role=content required` | — | `ze` |
| A3 | `interrogative-content-clause` | `clause:interrogative role=content required` | — | `interrogative` |

Proposed live guard: `require-exact-pattern-shapes` (F).

### Order 47 — `rozumieć` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `empathic-person-understanding` |
| meaningScope | Empathically understanding a person (WSJP sense 4). |
| schemaKeyProposal | `accusative-person` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | personal object |
| explicitExclusions | **no content clause is transferred to the person sense**; no person frame is derived from a content schema |
| evidenceSource | Batch 05 §47; `WSJP-ROZUM-01`, sense 4 “kogoś” — separately exact `KOGO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (F) |

### Order 48 — `mieszkać` (imperfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `long-term-residence` |
| meaningScope | Residing somewhere permanently or for a long period, optionally with a co-resident (WSJP sense 1). |
| schemaKeyProposal | `w-locative-residence-optional-co-resident` |
| requiredComplements | `preposition-case:w+locative role=target required` |
| optionalComplements | `preposition-case:z+instrumental role=interlocutor optional` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | **`w + Locative` is a NARROWED REALIZATION of the selected generalized `GDZIE` residence-place role — never exclusive government.** `z + Instrumental` is an exact selected co-resident participant, not a realization. |
| subjectOrParticipantRestriction | `z + Instrumental` is restricted to the **co-resident** role; incidental accompaniment does not qualify |
| explicitExclusions | describing `w + Locative` as exclusive government; promoting same-sense `na` or `u` place forms into additional product frames; residence duration, reason, manner, incidental companions |
| evidenceSource | Batch 05 §48; `WSJP-MIESZK-01`, sense 1 “w domu” — `Składnia` `GDZIE + (z KIM)`; same-sense `Połączenia` document `w + Locative` alongside `na`/`u` |
| proposedLiveGuard | `require-exact-pattern-shapes` (G) + `allow-only-preposition-case-signatures` (H) |

**Requiredness derivation.** `GDZIE` is unparenthesised in `Składnia` →
required; `(z KIM)` is parenthesised → optional. The authorised realization
`w + Locative` inherits `GDZIE`'s required status inside the single source
schema. Per the Batch 4 core translation principle, one source schema with an
optional participant becomes **one** product alternative carrying that
optional complement — never a required core plus a standalone
optional-participant pattern.

**Binding constraint honoured** (order 48): "Label `w + Locative` as a
residence-place realization rather than exclusive government; restrict
`z + Instrumental` to the selected co-resident role."

### Order 49 — `umówić się` (perfective) — meaning A of B — **ADJUDICATED (was HOLD-1)**

| Field | Value |
|---|---|
| meaningKeyProposal | `meeting-arrangement` |
| meaningScope | Arranging a meeting with another person (WSJP sense 1). Lexical `się` is part of the identity. |
| subjectOrParticipantRestriction | reciprocal plural personal subject may occur without a separate partner phrase; recorded in `internalScope`, **not** as a second complementless pattern |
| requiredLexicalMaterial | lexical `się` is part of `canonicalLemma`, not a complement |
| generalizedRoleStatus | `GDZIE` and `KIEDY` are selected generalized roles in source schema 2. `do + Genitive` is authorised as a **narrowed representable projection** of `GDZIE` (§8). `KIEDY` is source-selected but has **no** documented concrete realization and is **not** converted into a complement, a new type, or any other structural field — see the representation-boundary note below and the Phase 4C backlog (§19). |
| explicitExclusions | merging appointment with agreement; treating `do + Genitive` as exclusive government or as epistemically identical to the generalized `GDZIE` slot; a maximal appointment+agreement frame; stripping `się`; inventing a `KIEDY` complement or adverbial type |
| evidenceSource | Batch 05 §49; `WSJP-UMOW-SIE-01`, sense 1 “na spotkanie” |
| proposedLiveGuard | `require-exact-pattern-shapes` (L) |

Two source schemas, translated as two product patterns — never merged, never
split into standalone optional-participant patterns:

| # | schemaKeyProposal | requiredComplements | optionalComplements | generalizedRoleStatus |
|---|---|---|---|---|
| A1 | `z-instrumental-partner-na-accusative-event` | — (none) | `preposition-case:z+instrumental role=interlocutor optional`; `preposition-case:na+accusative role=topic optional` | not applicable — both positions are exact and source-parenthesised, not realizations |
| A2 | `do-genitive-appointment-venue` | `preposition-case:do+genitive role=target required` | `preposition-case:z+instrumental role=interlocutor optional` | **`do + Genitive` is a narrowed representable projection of the selected `GDZIE` venue/service position, required in THIS product row because the row exists specifically to represent that position — not exclusive government, not the only possible appointment-location form, and not epistemically identical to the source `GDZIE` slot itself. `KIEDY` remains an unrepresented source-selected time position (§8).** |

**A1 is a genuine all-optional pattern**, mirroring source schema 1
`(z KIM) + (na CO)` — both complements source-parenthesised, neither promoted
to required to manufacture an anchor. A read-only in-memory validator probe
(§15) confirmed the locked candidate-pattern validator imposes no rule
against an all-optional, non-empty complement array; this is the first Batch 5
(or corpus-wide) pattern of this shape, authorised by explicit policy
adjudication rather than invented.

### Order 49 — `umówić się` — meaning B of B — **ADJUDICATED (was partially HOLD-2)**

| Field | Value |
|---|---|
| meaningKeyProposal | `mutual-agreement` |
| meaningScope | Reaching an agreement with another person about a term, action, or proposition (WSJP sense 2). Lexical `się` is part of the identity. |
| subjectOrParticipantRestriction | reciprocal plural personal subject may occur without a separate partner phrase; recorded in `internalScope`, **not** as a second complementless pattern |
| requiredLexicalMaterial | lexical `się` in `canonicalLemma` |
| generalizedRoleStatus | not applicable to the five representable alternatives below — each content position is exact and source-listed, not a realization |
| explicitExclusions | combining `na`, `o`, `że`, `żeby`, interrogative into one maximal pattern; importing appointment-sense `do + Genitive`; communication channel, manner, advance notice, purpose; **encoding `co do + Genitive` as `co` or `do` alone** |
| evidenceSource | Batch 05 §49; `WSJP-UMOW-SIE-01`, sense 2 “co do ceny” — optional `z KIM` with `co do CZEGO`, `na CO`, or `o CO`, and optional `z KIM` with `że`, `żeby`, or an interrogative-dependent clause |
| proposedLiveGuard | `require-exact-pattern-shapes` (M) |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind | status |
|---|---|---|---|---|---|
| B1 | `na-accusative-agreed-term` | `preposition-case:na+accusative role=topic required` | `preposition-case:z+instrumental role=interlocutor optional` | — | resolved |
| B2 | `o-accusative-agreed-subject` | `preposition-case:o+accusative role=topic required` | `preposition-case:z+instrumental role=interlocutor optional` | — | resolved |
| B3 | `ze-agreement-clause` | `clause:ze role=content required` | `preposition-case:z+instrumental role=interlocutor optional` | `ze` | resolved |
| B4 | `zeby-agreed-action-clause` | `clause:zeby role=content required` | `preposition-case:z+instrumental role=interlocutor optional` | `zeby` | resolved |
| B5 | `interrogative-agreement-clause` | `clause:interrogative role=content required` | `preposition-case:z+instrumental role=interlocutor optional` | `interrogative` | resolved |

`co do + Genitive` receives **no Phase 4B product row**. It is verified
linguistic evidence, not rejected evidence, but the frozen Phase 4B complement
schema cannot encode a two-word preposition (§15). It is classified
**VERIFIED — ARCHITECTURE-DEFERRED FROM PHASE 4B** and carried forward as a
Phase 4C backlog item (§19), never silently dropped and never faked as `co`
or `do` alone. Five of six source-listed agreement alternatives become five
Phase 4B product rows; the sixth is deferred, not lost.

### Order 50 — `dzwonić` (imperfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `telephone-contact` |
| meaningScope | Making telephone contact with a person or institution and optionally reporting or requesting content (WSJP sense 3). |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | **`w sprawie + Genitive` is NOT governed** — it appears only in `Połączenia`, never in `Składnia`; call source/device, time, frequency, manner, topic; ringing/sounding senses; describing `do`/`na` as exclusive government; combining a target with a content clause absent an exact source schema |
| evidenceSource | Batch 05 §50; `WSJP-DZWON-03`, sense 3 “telefonować” — `Składnia` gives `DOKĄD` **and an alternative** `że ZDANIE\|żeby ZDANIE`; same-sense connections document `do + Genitive` and `na + Accusative` targets |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind | generalizedRoleStatus |
|---|---|---|---|---|---|
| 1 | `do-genitive-call-target` | `preposition-case:do+genitive role=target required` | — | — | **narrowed realization of `DOKĄD`** |
| 2 | `na-accusative-call-target` | `preposition-case:na+accusative role=target required` | — | — | **narrowed realization of `DOKĄD`** |
| 3 | `ze-reported-content-clause` | `clause:ze role=content required` | — | `ze` | exact listed alternative |
| 4 | `zeby-requested-content-clause` | `clause:zeby role=content required` | — | `zeby` | exact listed alternative |

Proposed live guard: `require-exact-pattern-shapes` (I) +
`allow-only-preposition-case-signatures` (J).

**Binding constraint honoured** (order 50): "Label `do`/`na` targets as
realizations, retain direct content clauses, and do not encode
`w sprawie + Genitive` as a governed construction."

### Order 51 — `powiedzieć` (perfective) — one meaning, eleven alternatives

| Field | Value |
|---|---|
| meaningKeyProposal | `spoken-communication` |
| meaningScope | Spoken communication that conveys interpretable content (WSJP sense 1), with recipient and content realized through separate object, topic, clause, or direct-speech schemas. |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | one maximal `KOMU + CO + o + że + żeby` template; **assigning a recipient to direct speech**; voice, manner, channel, location, time, communicative circumstances; **directly listed `JAK`, which lies outside the locked four complement types**; nonverbal senses |
| evidenceSource | Batch 06 §51; `WSJP-POWIEDZ-01`, sense 1 “o miłości” — **"lists seven separate schemas"** |

**Mode A — Dative addressee (optional throughout)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| A1 | `dative-accusative-content` | `case:accusative role=object required` | `case:dative role=recipient optional` | — |
| A2 | `dative-o-locative-topic` | `preposition-case:o+locative role=topic required` | `case:dative role=recipient optional` | — |
| A3 | `dative-ze-clause` | `clause:ze role=content required` | `case:dative role=recipient optional` | `ze` |
| A4 | `dative-zeby-clause` | `clause:zeby role=content required` | `case:dative role=recipient optional` | `zeby` |
| A5 | `dative-interrogative-clause` | `clause:interrogative role=content required` | `case:dative role=recipient optional` | `interrogative` |

**Mode B — `do` + Genitive addressee (optional throughout)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| B1 | `do-genitive-accusative-content` | `case:accusative role=object required` | `preposition-case:do+genitive role=recipient optional` | — |
| B2 | `do-genitive-o-locative-topic` | `preposition-case:o+locative role=topic required` | `preposition-case:do+genitive role=recipient optional` | — |
| B3 | `do-genitive-ze-clause` | `clause:ze role=content required` | `preposition-case:do+genitive role=recipient optional` | `ze` |
| B4 | `do-genitive-zeby-clause` | `clause:zeby role=content required` | `preposition-case:do+genitive role=recipient optional` | `zeby` |
| B5 | `do-genitive-interrogative-clause` | `clause:interrogative role=content required` | `preposition-case:do+genitive role=recipient optional` | `interrogative` |

**Recipientless direct speech**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| C1 | `direct-speech-content` | `clause:direct-speech role=content required` | — | `direct-speech` |

Mode A and Mode B are alternatives and must never co-occur in one pattern; no
pattern requires a recipient; **C1 carries no recipient at all**. Total:
**11 alternatives**.

Proposed live guard: `require-exact-pattern-shapes` (K).

## 4.1 `powiedzieć` source-row → product-row reconciliation

The Batch 06 narrative states the primary source **"lists seven separate
schemas"** and then enumerates four descriptive clauses. Only one
decomposition yields exactly seven:

| Source schema | Addressee | Content |
|---:|---|---|
| S1 | optional Dative | Accusative content |
| S2 | optional `do` + Genitive | Accusative content |
| S3 | optional Dative | `o` + Locative topic |
| S4 | optional `do` + Genitive | `o` + Locative topic |
| S5 | optional Dative | clause family (`że` \| `żeby` \| interrogative) |
| S6 | optional `do` + Genitive | clause family (`że` \| `żeby` \| interrogative) |
| S7 | — (none) | direct speech alone |

2 addressee modes × 3 content families + 1 recipientless direct-speech schema
= **7**. No other reading of the four clauses reaches seven: treating the
addressee as a single either/or slot gives 6; treating the clause family as
three separate rows per mode gives 13. The stated count is therefore what
fixes the decomposition — this is arithmetic reconciliation against an
explicit source-supplied cardinality, **not** an inferred cross-product.

Product normalization, following the Batch 4 `pisać`/`napisać` precedent
exactly: the Phase 4B architecture represents each concrete `clauseKind` as
its own alternative, so each grouped clause-family source row (S5, S6)
expands from 1 source row into 3 product rows.

| | Source rows | Product rows |
|---|---:|---:|
| Accusative content (S1, S2) | 2 | 2 |
| `o` + Locative topic (S3, S4) | 2 | 2 |
| clause family (S5, S6) | 2 | **6** |
| direct speech (S7) | 1 | 1 |
| **Total** | **7** | **11** |

7 source schemas → 11 product alternatives (+4, entirely from clause-kind
normalization). Requiredness is preserved exactly through the expansion:
every addressee stays optional, every content complement stays required, and
direct speech stays recipientless.

## 5. Per-lemma rationale

- **`oglądać` / `obejrzeć`** — `oglądać` has one exact source schema with a
  parenthesised optional `w + Locative` presentation context; `obejrzeć` is
  independently sourced with a bare `CO` and no optional position. The
  asymmetry is the whole point of retaining both: nothing is imported in
  either direction.
- **`skończyć`** — sense 1 lists `CO` and `BEZOKOLICZNIK` as two parallel
  `Składnia` entries, neither parenthesised. They cannot be one schema (that
  would require both simultaneously). The already-approved Batch 2 authoring
  of `kończyć` (order 19) for the identical notation produced exactly two
  alternatives, `accusative-task` and `infinitive` — this matrix follows that
  frozen precedent. Sense 4's `z CZYM` is a separate WSJP sense and becomes
  its own meaning.
- **`chcieć`** — sense 1's `CZEGO + (od KOGO) + (dla KOGO)` is one schema with
  two parenthesised optional participants (the `czytać` alternative-2
  precedent from Batch 4); `BEZOKOLICZNIK` and `żeby ZDANIE` are separate
  entries and therefore separate alternatives. Sense 3 independently lists
  `CO`, `BEZOKOLICZNIK`, `żeby ZDANIE`. `JAK` is directly listed but
  unrepresentable and is excluded.
- **`robić`** — WSJP separates making/creating from performing a noun-named
  activity; the shared Accusative surface does not license one generic object
  record. One exact schema each.
- **`rozumieć`** — sense 1 gives `CO` **and an alternative**
  `że ZDANIE|ZDANIE PYTAJNOZALEŻNE`; the `|`-grouped clause family normalizes
  into two product clauseKind rows. Sense 4's `KOGO` is a separate meaning.
- **`mieszkać`** — one source schema `GDZIE + (z KIM)`; `w + Locative` is the
  authorised narrowed realization of `GDZIE`, `z + Instrumental` an exact
  optional co-resident. One meaning, one alternative.
- **`umówić się`** — two clearly separate WSJP senses. The appointment sense's
  two source schemas both parenthesise every participant; schema 1 becomes a
  genuine all-optional product pattern (policy-authorised, §15), and schema 2
  becomes a `do + Genitive` realization row required only because that row
  exists to represent the selected `GDZIE` position, with `KIEDY` left
  structurally unrepresented. The agreement sense's five case/clause
  alternatives are mechanically recoverable; its sixth, `co do + Genitive`, is
  verified but architecture-deferred to Phase 4C because the locked schema
  cannot encode a two-word preposition (§15, §19).
- **`dzwonić`** — `Składnia` gives generalized `DOKĄD` **and an alternative**
  `że ZDANIE|żeby ZDANIE`. The `DOKĄD` row has two documented concrete
  realizations, both explicitly authorised as realizations by the binding
  constraint; the grouped clause row normalizes into two clause rows.
- **`powiedzieć`** — one broad sense, seven source schemas, eleven product
  alternatives (§4.1).

## 6. Requiredness / optionality audit

Every row states requiredness explicitly per complement. No source schema was
decomposed into a required core pattern plus a standalone optional-participant
pattern, and no alternatives were merged.

| Lemma | Optional participants carried inside their own schema |
|---|---|
| `oglądać` | optional `w + Locative` presentation context inside the Accusative schema (never standalone) |
| `obejrzeć` | none — the single complement is required |
| `skończyć` | none in either meaning |
| `chcieć` | desire A1: optional `od + Genitive` **and** optional `dla + Genitive` inside the Genitive-object schema; A2/A3 and all of sense 3: none |
| `robić` | none |
| `rozumieć` | none |
| `mieszkać` | optional `z + Instrumental` co-resident inside the `w + Locative` schema (never standalone) |
| `umówić się` | appointment A1: optional `z + Instrumental` **and** optional `na + Accusative`, both inside one all-optional schema (never split); appointment A2: optional `z + Instrumental` inside the `do + Genitive` realization row; agreement B1–B5: optional `z + Instrumental` partner inside each content alternative |
| `dzwonić` | none — each of the four alternatives has exactly one required complement |
| `powiedzieć` | optional Dative on all five Mode-A alternatives; optional `do + Genitive` on all five Mode-B alternatives; **none on C1 direct speech** |

Explicitly checked and rejected: no standalone `w + Locative` pattern for
`oglądać`; no standalone `z + Instrumental` co-resident pattern for
`mieszkać`; no standalone `od`/`dla` pattern for `chcieć`; no standalone
partner or event pattern for `umówić się` appointment or agreement; no
`powiedzieć` pattern requires a recipient, and Dative/`do` + Genitive never
co-occur in one pattern.

**Multi-complement schemas** (all others are single-complement):

| Lemma / schema | Required | Optional |
|---|---|---|
| `oglądać` `accusative-content-optional-presentation-context` | Accusative object | `w`+Locative target |
| `chcieć` A1 `genitive-desired-object` | Genitive object | `od`+Genitive target; `dla`+Genitive recipient |
| `mieszkać` `w-locative-residence-optional-co-resident` | `w`+Locative target | `z`+Instrumental interlocutor |
| `umówić się` A1 `z-instrumental-partner-na-accusative-event` | **none** | `z`+Instrumental interlocutor; `na`+Accusative topic |
| `umówić się` A2 `do-genitive-appointment-venue` | `do`+Genitive target | `z`+Instrumental interlocutor |
| `umówić się` B1–B5 (5 schemas) | one content complement each | `z`+Instrumental interlocutor |
| `powiedzieć` A1–A5 (5 schemas) | one content complement each | Dative recipient |
| `powiedzieć` B1–B5 (5 schemas) | one content complement each | `do`+Genitive recipient |

`umówić się` A1 is the sole **all-optional** schema in the entire matrix —
non-empty complement array, both complements `required: false` — authorised
by explicit policy adjudication and confirmed compatible with the locked
validator (§15).

## 7. Sense-separation audit

| Lemma | Senses | Kept separate because |
|---|---:|---|
| `skończyć` | 2 | WSJP sense 1 vs. colloquial sense 4; `z + Instrumental` belongs only to cessation |
| `chcieć` | 2 | WSJP sense 1 vs. sense 3; **Genitive vs. Accusative** object case, plus sense 3's first-person restriction |
| `robić` | 2 | WSJP sense 1 vs. sense 2; structurally identical — sense split carried non-structurally (see §4 note) |
| `rozumieć` | 2 | WSJP sense 1 vs. sense 4; content clauses belong only to the content sense |
| `umówić się` | 2 | WSJP sense 1 vs. sense 2; entirely separate complement inventories |

`oglądać`, `obejrzeć`, `mieszkać`, `dzwonić`, `powiedzieć` each carry exactly
one scoped meaning.

## 8. Generalized-role / realization audit

Three Batch 5 lemmas carry `KEEP WITH NARROWING`. Each is handled as a
**realization**, never as exclusive government:

| Lemma | Generalized role | Authorised concrete realization(s) | Status |
|---|---|---|---|
| `mieszkać` | `GDZIE` residence place | `w + Locative` | narrowed realization; `na`/`u` documented but **not** authored as frames |
| `umówić się` (appointment, schema 2) | `GDZIE` venue/service position | `do + Genitive` | **narrowed representable projection** into the product row `do-genitive-appointment-venue` (§4, order 49) — required only because the row's purpose is to represent that selected position, never exclusive government, never the only possible appointment-location form, never epistemically identical to the source `GDZIE` slot |
| `dzwonić` | `DOKĄD` call target | `do + Genitive`, `na + Accusative` | both narrowed realizations |

`umówić się` appointment schema 2's **`KIEDY`** position is a distinct case:
it is source-selected and required in the WSJP `Składnia` entry, but has **no
documented concrete realization anywhere in the Batch 5 evidence** and is not
a locked complement type. It is therefore **not represented at all** — not as
a complement, not as a new type, not folded silently into `do + Genitive`.
This is a deliberate, bounded projection of the source schema into the locked
four-type model, analogous to how `czytać`'s optional `GDZIE` was left
unauthored as role-evidence-only in Phase 4B4-A — it is **not** evidence that
`KIEDY` was optional or absent in the source, and it is carried forward as a
Phase 4C backlog item (§19) rather than silently dropped.

`umówić się` appointment schema 1 (`z + Instrumental`, `na + Accusative`, both
optional) carries **no** generalized role at all — both positions are
directly parenthesised in `Składnia`, not realizations of anything.

Constructions that are **exact selected positions, not realizations**, and
must not be mislabelled: `oglądać`'s optional `w + Locative` (fit is
`compatible`, not `compatible with narrowing`), `mieszkać`'s
`z + Instrumental`, all `chcieć` positions, `umówić się` appointment schema 1
in full, all `umówić się` agreement positions, `dzwonić`'s `że`/`żeby`, all
`powiedzieć` positions.

No generalized role becomes a product complement type. `GDZIE`, `KIEDY`,
`DOKĄD`, and `JAK` remain outside the locked four types.

## 9. Lexical-identity audit

- **`się`** (`umówić się`) — part of `canonicalLemma`, never a complement.
  The lemma is indivisible; no non-reflexive `umówić` record exists or may be
  derived. Enforceable by `require-lexical-identity`.
- No Batch 5 lemma requires fixed lexical material of the `udział` kind; no
  Batch 5 lemma carries `requiredLexicalItems` in the frozen skeleton.
- No Batch 5 lemma is metadata-only, and none carries a
  `metadataAspectPartner`.

## 10. Clause normalization audit

Grouped source clause families expand into separate product `clauseKind`
rows, exactly as adjudicated for Batch 4:

| Lemma | Source clause row | Product rows | Expansion |
|---|---|---:|---:|
| `rozumieć` | `że ZDANIE\|ZDANIE PYTAJNOZALEŻNE` (1 row) | `ze`, `interrogative` | 1 → 2 |
| `dzwonić` | `że ZDANIE\|żeby ZDANIE` (1 row) | `ze`, `zeby` | 1 → 2 |
| `powiedzieć` | clause family × 2 addressee modes (2 rows) | `ze`, `zeby`, `interrogative` × 2 | 2 → 6 |
| `umówić się` (agreement) | `że`, `żeby`, interrogative (1 row) | `ze`, `zeby`, `interrogative` | 1 → 3 |
| `chcieć` | `żeby ZDANIE` per sense (2 separate rows) | `zeby` × 2 | 2 → 2 |

The four locked clause kinds `ze`, `czy`, `zeby`, `interrogative` plus the
Phase 4B-only `direct-speech` are never flattened into one another. No Batch 5
row uses `czy`.

## 11. Explicit exclusions

| Lemma | Excluded |
|---|---|
| `oglądać` | generalizing the `w` position to any cinema/TV/device/medium/viewing-place phrase; time, frequency, manner; inheritance from `obejrzeć` |
| `obejrzeć` | any `w + Locative` imported from `oglądać`; cinema, television, screen, time, manner, purpose, recommendation |
| `skończyć` | `z + Instrumental` inside completion; completion time, deadline, place, manner, result; inheritance from `kończyć` |
| `chcieć` | one maximal object + infinitive + `żeby` template; purpose, reason, degree, contextual beneficiary; **adverbial `JAK`** |
| `robić` | promoting `robić + noun` collocations into frames; materials, tools, place, purpose, beneficiary, time, manner; merging the two senses |
| `rozumieć` | merging person and content senses; treating `how`/`why` as separate frames; degree, manner, language, information source |
| `mieszkać` | exclusive-government claim for `w`; `na`/`u` as extra frames; duration, reason, manner, incidental companions |
| `umówić się` | merging appointment and agreement; `do + Genitive` as exclusive government; forcing either appointment schema-1 participant to required to manufacture an anchor; a synthesised `KIEDY` complement or adverbial type; a fake `co`/`do` encoding of `co do + Genitive`; maximal frames; stripping `się`; channel, manner, advance notice, purpose |
| `dzwonić` | **governed `w sprawie + Genitive`**; exclusive-government claim for `do`/`na`; source, device, time, frequency, manner, topic; ringing/sounding senses |
| `powiedzieć` | maximal `KOMU + CO + o + że + żeby` template; **recipient on direct speech**; voice, manner, channel, location, time; **adverbial `JAK`**; nonverbal senses |

## 12. Proposed live-guard plan (NOT implemented in this task)

`tests/fixtures/priority8_phase4b_authoring_rules.json` is **unchanged** by
this task and remains byte-identical at
`3caab1419f14718ed7c82b5fea4eb5fac3326160864c88decd88ca13b6277db0`.
Presence-asserting rules must land in the same commit as the
`candidateContent` they protect, per the test-lifecycle rule.

| Ref | Target | Proposed primitive | Purpose |
|---|---|---|---|
| A | `oglądać` | `require-exact-pattern-shapes` | One meaning, one alternative; optional `w + Locative` stays inside it |
| B | `obejrzeć` | `require-exact-pattern-shapes` | One meaning, one bare-Accusative alternative; structurally blocks importing `oglądać`'s optional `w` |
| C | `skończyć` | `require-exact-pattern-shapes` | Exact two-meaning set; completion = 2 alternatives, cessation = 1; blocks adding `z + Instrumental` to completion |
| D | `chcieć` | `require-exact-pattern-shapes` | Exact two-meaning set; 3 + 3 alternatives with the Genitive/Accusative contrast and the two optional desire-sense participants pinned |
| E | `robić` | `require-exact-pattern-shapes` | Exact two-meaning set, one shape each (see limitation below) |
| F | `rozumieć` | `require-exact-pattern-shapes` | Exact two-meaning set; 3 content alternatives + 1 person alternative; blocks transferring clauses to the person sense |
| G | `mieszkać` | `require-exact-pattern-shapes` | One alternative; optional `z + Instrumental` never standalone |
| H | `mieszkać` | `allow-only-preposition-case-signatures` | Allowlist exactly `w+locative role=target required=true` and `z+instrumental role=interlocutor required=false`; structurally blocks concretizing `GDZIE` into `na`/`u`/`do` or any other place preposition |
| I | `dzwonić` | `require-exact-pattern-shapes` | Exactly four alternatives; blocks combining a target with a content clause |
| J | `dzwonić` | `allow-only-preposition-case-signatures` | Allowlist exactly `do+genitive role=target required=true` and `na+accusative role=target required=true`; **structurally blocks `w sprawie`-style topic concretization and any other `DOKĄD` realization** |
| K | `powiedzieć` | `require-exact-pattern-shapes` | Eleven declared shapes; inherently prevents addressee-mode merger, Dative/`do` co-occurrence, clause-kind merger, a maximal frame, and **assigning a recipient to direct speech** |
| L | `umówić się` | `require-lexical-identity` (`się`) | Lexical identity preserved |
| M | `umówić się` | `require-exact-pattern-shapes` | Exact two-meaning set; appointment = 2 alternatives (A1 fully optional `z`/`na`; A2 required `do`+Genitive realization + optional `z`), agreement = 5 alternatives (`na`, `o`, `ze`, `zeby`, interrogative, each with optional `z`); structurally blocks merging appointment/agreement, forcing A1's participants to required, and adding a sixth agreement row for `co do` |
| N | `umówić się` | `allow-only-preposition-case-signatures` | Allowlist exactly the five legitimate preposition-case signatures actually used across both meanings — `z+instrumental role=interlocutor required=false`; `na+accusative role=topic required=false` (A1); `na+accusative role=topic required=true` (B1); `do+genitive role=target required=true` (A2); `o+accusative role=topic required=true` (B2) — and nothing else; **structurally blocks concretizing the appointment `GDZIE`/`KIEDY` positions into any additional preposition beyond the single approved `do + Genitive` realization row**, and blocks a fake `co`/`do`-only encoding of `co do + Genitive` from later slipping in as an ordinary single-word preposition |

Note that guards H, J, and N must each list **every** distinct signature with
its exact `required` flag, because the guard engine matches complements by
exact signature equality and `required` is part of signature identity — the
correction adjudicated for `czytać` in Phase 4B4-A applies identically here.
Guard J's two signatures are both `required=true`. Guard N is the first
`allow-only-preposition-case-signatures` rule that must track signatures
across **two** meanings of one lemma and **two** distinct roles (`interlocutor`
and `topic`) rather than a single generalized-role position — later authoring
must build its allowlist from the full complement inventory in §4, not from
the appointment rows alone.

**Guard-engine coverage assessment.** Every invariant above is expressible
with existing primitives; no new primitive is required and the interpreter is
not modified. Limitations flagged rather than papered over:

1. **`robić`'s sense split is not structurally enforceable.** Both meanings
   have the identical shape `case:accusative role=object required`.
   `require-exact-pattern-shapes` with `exactMeaningSet: true` pins the
   meaning inventory and cardinality but cannot verify that the *right*
   semantics sits under each key. Control falls to `internalScope`,
   `glossesEn`, `learnerExplanationEn`, the example, the historical lock, and
   independent review.
2. **`chcieć`'s first-person past/conditional restriction is not
   structurally expressible.** No field in the locked schema encodes it. It
   must be carried in `internalScope` and `usage.note`; no guard can enforce
   it.
3. **`mieszkać`'s co-resident-vs-accompaniment distinction and `umówić się`'s
   reciprocal-plural behaviour are not structurally expressible.** Both are
   participant/usage facts with no schema field; they are recorded in
   `internalScope` per the frozen matrix discipline.
4. **Realization-vs-government labelling is documentation, not structure.**
   Guards H, J, and N pin *which* signatures may appear, which is the
   enforceable half; the "this is a realization of `GDZIE`/`DOKĄD`" claim
   itself lives in `internalScope`, this matrix, and review.
5. **`umówić się`'s `KIEDY` source-selection and `co do + Genitive`
   architecture-deferral are not structurally represented at all — by
   design.** No guard can assert "a required source position named `KIEDY`
   exists and is intentionally unauthored" or "`co do + Genitive` was
   verified but deferred rather than rejected"; both facts live only in this
   matrix, `internalScope`, the learner-explanation guidance, the historical
   lock, independent review, and the Phase 4C backlog (§19).

## 13. Aspect / cross-lemma independence audit

| Family | Decision | Enforcement in this matrix |
|---|---|---|
| `oglądać` / `obejrzeć` | **RETAIN BOTH** | Separately sourced; `obejrzeć` has **no** optional `w + Locative`, and guard B pins its bare-Accusative shape so the asymmetry cannot be normalized away |
| `kończyć` (order 19, Batch 2) / `skończyć` (order 44) | **RETAIN BOTH** | `skończyć` is sourced from its own WSJP entry. Its completion meaning legitimately has the same two-alternative shape as the already-authored `kończyć`; this is independently evidenced convergence, not inheritance — and `skończyć` additionally carries a second cessation meaning `kończyć` does not |
| `chcieć` | no partner in scope | — |
| `umówić się` | no partner in scope | Lexical `się` preserved; no non-reflexive `umówić` exists |
| `dzwonić` / `powiedzieć` vs. `pisać`/`napisać`/`odpowiadać` | **NO TRANSFER** | Communication semantics do not license schema transfer. `dzwonić`'s four alternatives and `powiedzieć`'s eleven are derived solely from their own `Składnia` rows. Notably `dzwonić` has **no** recipient-bearing clause pattern (unlike `pisać`), and `powiedzieć` has a **recipientless** direct-speech schema (unlike `pisać`'s `dative-direct-speech`) — the differences are preserved, not smoothed |

No aspect partner donates syntax. No family is reconsidered here.

## 14. Candidate-key quality audit

Every proposed key is lowercase kebab-case matching
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, semantic, durable, and sibling-unique within its
owner scope. None encodes a verification order, batch number, sentence
wording, source ID, or production ID.

- Meaning keys are unique within their lemma. Cross-lemma repetition is legal
  and occurs deliberately: `activity-completion` matches the already-authored
  `kończyć` key, and `accusative-content` / `direct-speech-content` recur
  across lemmas — permitted by the B1A lock ("the same value is allowed in
  another lemma").
- Pattern keys are unique within `(lemma, meaningKeyRef)`. `rozumieć`'s
  `accusative-content` (content sense) and `accusative-person` (person sense)
  are deliberately distinct rather than reusing one key under two meanings, so
  that ownership reads unambiguously.
- `powiedzieć`'s mode-prefixed keys (`dative-…`, `do-genitive-…`) follow the
  frozen Batch 4 `pisać`/`napisać` convention exactly.
- `umówić się` appointment keys (`z-instrumental-partner-na-accusative-event`,
  `do-genitive-appointment-venue`) name participants/realization, not the
  requiredness pattern itself — consistent with existing keys like
  `z-instrumental-meeting-partner` (`spotykać się`/`spotkać się`), which also
  do not encode optionality in the name. The agreement keys were renumbered
  B1–B5 after `co do + Genitive` was removed from the product row sequence;
  no gap or skipped number remains in the committed matrix.
- No key contains a digit.

## 15. HOLD history and adjudication

**Original HOLD count: 2, both on order 49 `umówić się`.** The initial matrix
pass placed two `umówić się` representation questions on HOLD rather than
inventing precision, per §20 of the authoring brief, and left the matrix
uncommitted. Human/policy adjudication has since resolved both. This section
preserves the original HOLD statements in full as a historical record — the
HOLDs were correctly raised given the evidence and architecture questions
available at the time — followed by the adjudication actually applied.
**Current HOLD count: 0.**

### HOLD-1 — `umówić się` (order 49), meaning `meeting-arrangement`

**Repository evidence, quoted exactly** (Batch 05 §49):

> gives optional `z KIM` with optional `na CO`, or optional `z KIM` with
> generalized `GDZIE` and `KIEDY`, plus reciprocal plural variants. Its
> same-sense connections document `do` venue/service forms.

**What is settled.** Appointment is a separate sense from agreement. There are
two source schemas. `z + Instrumental` is optional in both. `na + Accusative`
is optional. `GDZIE`/`KIEDY` are selected but generalized. `do + Genitive` is
a documented venue/service realization of `GDZIE` and — per the CSV's rejected
hypotheses — "is **not** an exact exclusive appointment frame in `Składnia`".

**What is unresolved.** Two independent facts, neither recoverable from the
repository:

1. **Source schema 1 has no required complement.** `(z KIM)` and `(na CO)` are
   both parenthesised. Rendering it faithfully produces a product pattern
   whose complements are *all optional*. **Zero of the 124 currently authored
   patterns has all-optional complements**, so this would be an architectural
   first. The repository does not state whether the locked model permits a
   zero-required pattern, nor — if it does not — what the faithful alternative
   shape is. Making `na + Accusative` required to avoid the problem would
   directly contradict the source's parenthesisation.

2. **Source schema 2 contains a required position with no representable
   realization.** `GDZIE` and `KIEDY` are both unparenthesised, hence
   required. `GDZIE` has a documented realization (`do + Genitive`); **`KIEDY`
   has none** — no concrete time realization is documented anywhere in the
   Batch 5 evidence, and `KIEDY` is not a locked complement type. Authoring
   schema 2 as "optional `z` + `do + Genitive`" would silently drop a required
   source position *and* promote a realization the CSV explicitly says is not
   an exact frame to required status. Omitting schema 2 entirely would instead
   under-represent the source and leave the binding constraint's instruction
   to "label `do` as a realization" with nothing to label.

**Exact fact needed for adjudication.** For appointment sense 1, an
authoritative statement of (a) whether the locked candidate-pattern model
permits a pattern with zero required complements, and if so whether source
schema 1 is to be authored as a single all-optional
`z + Instrumental` / `na + Accusative` pattern; and (b) the authorised product
representation of source schema 2 — specifically whether `do + Genitive` is
authored at all, with what requiredness, and how the co-required `KIEDY`
position is to be treated (represented, deliberately unauthored as
role-evidence-only in the manner of `czytać`'s `GDZIE`, or something else).

**Why this must not be guessed.** Both gaps are exactly the failure mode the
`wymagać` correction and the Batch 4 `pisać` HOLD were raised to prevent:
producing plausible-looking rows would manufacture precision the repository
does not contain.

### HOLD-2 — `umówić się` (order 49), meaning `mutual-agreement`, alternative B1

**Repository evidence, quoted exactly** (Batch 05 §49):

> separately gives optional `z KIM` with `co do CZEGO`, `na CO`, or `o CO`,
> and optional `z KIM` with `że`, `żeby`, or an interrogative-dependent
> clause.

**What is settled.** The agreement sense has six content alternatives, each
with an optional `z + Instrumental` partner. Five of them (`na + Accusative`,
`o + Accusative`, `że`, `żeby`, interrogative) are fully resolved in §4 above.

**What is unresolved — an encoding limitation, not an evidence gap.**
`co do + Genitive` **cannot be represented in the locked candidate schema.**
The validator constrains a `preposition-case` complement's preposition to
`PREPOSITION_RE = ^[a-ząćęłńóśźż]+$` — a single lowercase Polish word with no
space. `co do` is a two-word compound preposition and fails this check;
correspondingly, **no complement anywhere in the 124 authored patterns uses a
multi-word preposition** (the full attested set is `dla, do, na, nad, o, od,
u, w, z, za`).

The three unsafe workarounds, all rejected here:

- encode the preposition as `co` or `do` alone → falsifies the construction
  and, for `do`, collides with the appointment-sense venue realization;
- silently omit the alternative → under-represents a source-listed agreement
  alternative and would make guard M's declared shape set wrong;
- widen `PREPOSITION_RE` → prohibited; this task must not modify the schema,
  the validator, or the guard interpreter.

**Exact fact needed for adjudication.** An authorised decision on how
multi-word prepositions are to be handled in Phase 4B: either (a) `co do` is
formally out of scope for Phase 4B and the agreement sense is authored with
five alternatives, with the omission recorded as a known architectural
limitation; or (b) a schema/validator change is authorised under a separate
task to admit multi-word prepositions, after which agreement has six
alternatives. Note this is a **general architectural question** — it will
recur for any later batch whose evidence lists a compound preposition.

### Not a HOLD

`dzwonić`'s `w sprawie + Genitive` raises the same multi-word-preposition
issue but is **not** a HOLD: Phase 3 independently rejected it as ungoverned
because it appears only in `Połączenia` and never in `Składnia`. It is
excluded on evidence grounds, so the encoding limitation never arises.

### Adjudication of HOLD-1

Human/policy adjudication authorised the following, applied exactly:

**HOLD-1A (source schema 1 — the all-optional question).** A Phase 4B
product pattern **may** have a non-empty complement array in which every
complement is `required: false`. Neither `z + Instrumental` nor
`na + Accusative` was forced to `required: true` to manufacture an anchor.

Before relying on this, a read-only, in-memory synthetic probe was run
against the current locked `validate_priority8_staging.py` validator (no
repository file was written): a synthetic pattern
`{"z+instrumental role=interlocutor required=false",
"na+accusative role=topic required=false"}` was injected into an in-memory
deep copy of live staging under `umówić się` and validated with
`validate_data`. **Result: the shape itself produced zero validation issues.**
The only issue returned (`"future-batch lemma must remain empty"`) is the
unrelated batch-boundary check, confirmed by an isolating control: an
otherwise-identical synthetic pattern with the complement forced to
`required: true` produced the **identical single issue**, proving the
boundary check fires regardless of requiredness and that no rule in the
current validator rejects an all-optional complement array. The probe
modified nothing on disk (verified by comparing the staging file's bytes
before and after). Source schema 1 is therefore authored as product row
**A1** `z-instrumental-partner-na-accusative-event`, with **both**
complements optional, in **one** pattern (§4, order 49).

**HOLD-1B (source schema 2 — `GDZIE` + `KIEDY`).** `do + Genitive` is
authored as a **narrowed representable projection** of the selected `GDZIE`
venue/service position: product row **A2**
`do-genitive-appointment-venue`, with `do + Genitive` `required: true` in
that row only (because the row's entire purpose is to represent that
position — not because `do + Genitive` is exclusive government, the only
possible appointment-location form, or epistemically identical to the
generalized source slot), and `z + Instrumental` optional. `KIEDY` is
**not** converted into a complement, a new type, or any other structural
field; it remains an explicitly documented, source-selected, required
position that Phase 4B's locked four-type model cannot represent. This
boundary is stated in the row's `generalizedRoleStatus` (§4, order 49), the
generalized-role/realization audit (§8), the live-guard plan (§12), and the
Phase 4C backlog (§19) — it is not silently dropped and not evidence that
`KIEDY` was optional or absent in the source.

Reciprocal plural-subject behaviour for the appointment sense is recorded as
a `subjectOrParticipantRestriction`/`internalScope` fact on the meaning, not
as a third, complementless product pattern.

### Adjudication of HOLD-2

`co do + Genitive` remains **verified linguistic evidence** — the agreement
sense's sixth source-listed alternative is real and was never in doubt. It
is classified **VERIFIED — ARCHITECTURE-DEFERRED FROM PHASE 4B**: the locked
Phase 4B complement schema cannot encode a two-word preposition
(`PREPOSITION_RE` accepts one lowercase Polish word only), and per this
task's explicit instruction the schema/validator is **not** modified to
accommodate it, and it is **not** encoded as `co` or `do` alone. It receives
**no Phase 4B product schema row** and contributes zero alternatives to the
agreement count. It is carried forward as a named Phase 4C reconciliation
item (§19) rather than being called rejected, unsupported, or unverified —
those words describe a different situation (evidence insufficiency) that
does not apply here. The other five agreement alternatives (`na`, `o`, `że`,
`żeby`, interrogative-dependent) are authored exactly as resolved in the
original pass, renumbered B1–B5.

## 16. Final reconciliation counts

Counts are **discovered from the evidence and the adjudication**, not
prescribed in advance.

- **Full-pattern lemmas covered:** exactly 10 — orders 42, 43, 44, 45, 46, 47,
  48, 49, 50, 51.
- **Metadata-only identities in scope:** none.
- **Meanings proposed:** **15** — `oglądać` 1, `obejrzeć` 1, `skończyć` 2,
  `chcieć` 2, `robić` 2, `rozumieć` 2, `mieszkać` 1, `umówić się` 2,
  `dzwonić` 1, `powiedzieć` 1. Independently recomputed:
  1+1+2+2+2+2+1+2+1+1 = 15.
- **Product schema alternatives resolved:** **40** — `oglądać` 1,
  `obejrzeć` 1, `skończyć` 3, `chcieć` 6, `robić` 2, `rozumieć` 4,
  `mieszkać` 1, `umówić się` 7 (2 appointment + 5 agreement), `dzwonić` 4,
  `powiedzieć` 11. Independently recomputed:
  1+1+3+6+2+4+1+7+4+11 = 40.
- **HOLD rows: 0.** Both original HOLDs (`umówić się` appointment meaning,
  `umówić się` agreement alternative `co do + Genitive`) are now **resolved**
  — see §15 for the full adjudication history, including why the original
  HOLDs were correct given the evidence and questions available at the time
  and exactly what adjudication closed each one.
- `co do + Genitive` is **verified — architecture-deferred**, not authored as
  a Phase 4B row and not counted in the 40; it is tracked as a Phase 4C
  backlog item (§19) rather than dropped.

Per-lemma resolution status:

| Order | Lemma | Meanings | Schemas | Status |
|---|---|---:|---:|---|
| 42 | `oglądać` | 1 | 1 | resolved |
| 43 | `obejrzeć` | 1 | 1 | resolved |
| 44 | `skończyć` | 2 | 3 | resolved |
| 45 | `chcieć` | 2 | 6 | resolved |
| 46 | `robić` | 2 | 2 | resolved |
| 47 | `rozumieć` | 2 | 4 | resolved |
| 48 | `mieszkać` | 1 | 1 | resolved |
| 49 | `umówić się` | 2 | 7 | resolved (adjudicated; `co do` deferred to Phase 4C) |
| 50 | `dzwonić` | 1 | 4 | resolved |
| 51 | `powiedzieć` | 1 | 11 | resolved |

**All ten lemmas are fully resolved.** This matrix is ready for independent
review.

## 17. Content invariants

- `editorial/priority-8-phase4-staging.json` — unchanged, SHA-256
  `0f26b17238ec1abe984145fd7a6c232419465a5baec1f59a3a14e23d93295f8c`
- `tests/fixtures/priority8_phase4b_authoring_rules.json` — unchanged, SHA-256
  `3caab1419f14718ed7c82b5fea4eb5fac3326160864c88decd88ca13b6277db0`
- `phaseStep` `4B4`, `stagingRevision` 5, 39 authored / 51 meanings /
  124 patterns / 124 examples / 29 future-empty — all unchanged
- No `candidateContent` authored, no example created, no CEFR or
  `teachingStatus` assigned, no reuse search performed, no ID allocated
- Guard registry, guard interpreter, progress test, all Batch 0–4 tests, all
  Batch 1–4 reports, all Phase 3 / Phase 3B artifacts, and all
  runtime/canonical/audio/product files unchanged

## 18. Test results

- `python3 validate_priority8_staging.py` → `PASS: Priority 8 4B4 staging
  revision 5 is read-only valid (68 lemmas, 21 constrained records, 12 global
  constraints).`
- Eight scoped Phase 4B suites individually: 31, 65, 9, 11, 17, 23, 8, 26 —
  all OK.
- Eight suites together: **190 tests, all passing** — identical to the
  pre-task baseline, as required for a report-only task.
- `git diff --check` — clean.

## 19. Phase 4C architecture reconciliation items

This backlog records architecture questions the HOLD adjudication surfaced.
Neither item is a schema change performed now; both require a future,
separately-governed decision before Phase 4C canonical promotion.

### 1. Compound-preposition support — verified `co do + Genitive`

**Current status.** Linguistically verified: `umówić się` agreement sense 2
(WSJP `Składnia`) directly lists `co do CZEGO` alongside `na CO` and `o CO` as
a co-equal alternative. Intentionally **not represented** in any Phase 4B
`candidateContent` — no product schema row exists for it, and it is not
counted in this matrix's totals. It is not encoded as `co` or `do` alone, and
it is not described as rejected or unverified.

**Required 4C decision.** Whether the canonical `preposition-case` complement
architecture should be extended to permit multi-word (compound) prepositions
— currently `PREPOSITION_RE` accepts exactly one lowercase Polish word. If
authorised, `umówić się`'s agreement sense gains a sixth alternative,
`co-do-genitive-agreement-scope` or equivalent, with the same optional
`z + Instrumental` partner as its five siblings. This is a general
architectural question, not specific to `umówić się`: any later batch whose
verified evidence lists a compound preposition will hit the identical
encoding limitation.

### 2. `KIEDY` in the `umówić się` appointment source schema

**Current status.** `KIEDY` is a source-selected, required adverbial/time
position in WSJP's appointment `Składnia` entry (alongside `GDZIE`, whose
venue/service realization `do + Genitive` **is** represented). `KIEDY` is
intentionally left **outside** the locked Phase 4B complement model — not
converted into a complement, not given a new architecture type, not folded
into `do + Genitive` or any other position. The fact of its source-selected
existence is documented only in this matrix, in the meaning's
`generalizedRoleStatus`/`internalScope` (once authored), and in learner
guidance — never structurally.

**Required 4C decision.** No new complement type is automatically requested
by this item. The 4C decision needed is narrower: confirm that canonical
projection and documentation for `umówić się`'s appointment sense
deliberately remains non-structural for `KIEDY` (i.e., that this is an
accepted, permanent representational boundary of the four-type model, not an
oversight to be quietly patched later without review).
