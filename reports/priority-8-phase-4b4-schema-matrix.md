# Priority 8 Phase 4B4 — Batch 4 schema matrix

## 1. Scope and source hierarchy

This is a **control-plane authoring plan** produced before any Batch 4
`candidateContent` is written. It is not candidate content, not a staging
schema, not runtime data, and it allocates no stable IDs. It adds no field to
the locked Phase 4B candidate-content schema.

It covers exactly these nine full-pattern lemmas:

| Order | Lemma | Aspect |
|---|---|---|
| 32 | `dawać` | imperfective |
| 33 | `dać` | perfective |
| 34 | `brać` | imperfective |
| 35 | `wziąć` | perfective |
| 36 | `czytać` | imperfective |
| 38 | `pisać` | imperfective |
| 39 | `napisać` | perfective |
| 40 | `spotykać się` | imperfective |
| 41 | `spotkać się` | perfective |

**Order 37 `przeczytać` is metadata-only.** It receives no full-pattern schema
matrix and no `candidateContent`. Its own verified Phase 3 evidence may inform
aspect-partner metadata only and never donates syntax to `czytać`. Orders 42+
are out of scope.

Binding source hierarchy, in order of authority:

1. `reports/priority-8-phase-3-batch-04.md` (+ risk review, verification CSV)
   — orders 32–40.
2. `reports/priority-8-phase-3-batch-05.md` (+ risk review, verification CSV)
   — order 41 `spotkać się`.
3. `reports/priority-8-phase-3-final-synthesis.md` (+ risk review).
4. `reports/priority-8-phase-3b-final-lemma-freeze.{csv,md}`,
   `reports/priority-8-phase-3b-phase4-handoff.md`,
   `reports/priority-8-phase-3b-risk-review.md`.
5. Phase 4B control documents:
   `reports/priority-8-phase-4b1a-authoring-schema-lock.md`,
   `reports/priority-8-phase-4b-authoring-guard-hardening.md`,
   `reports/priority-8-phase-4b-test-lifecycle.md`.

No fresh web research was performed. No construction was broadened from
intuition. None of orders 32–41 appears in the sixteen `KEEP WITH NARROWING`
constraints; all nine are `KEEP VERIFIED`.

**Core translation principle applied throughout:** translate the *source
schema itself*. One source schema with an optional participant becomes **one**
alternative carrying that optional complement — never a required core pattern
plus a standalone optional-participant pattern. Distinct source schemas remain
distinct alternatives and are never merged into a maximal frame. This is the
discipline established by the `wymagać` correction.

## 2. Full schema matrix

Complement notation: `type:value role=... required|optional`.

### Order 32 — `dawać` (imperfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `transfer-to-recipient` |
| meaningScope | Imperfective transfer causing a recipient to own or use a thing; process, repeated, and habitual transfer. |
| schemaKeyProposal | `accusative-thing-dative-recipient` |
| requiredComplements | `case:accusative role=object required`; `case:dative role=recipient required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | gift occasion; purpose; manner; time; `w prezencie` and comparable contextual gift language |
| evidenceSource | Batch 04 §32; WSJP `dawać` sense 1 — exact `CO + KOMU` |
| proposedLiveGuard | `require-exact-pattern-shapes` (A) |

### Order 33 — `dać` (perfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `completed-transfer-to-recipient` |
| meaningScope | Completed/bounded transfer causing a recipient to own or use a thing. |
| schemaKeyProposal | `accusative-thing-dative-recipient` |
| requiredComplements | `case:accusative role=object required`; `case:dative role=recipient required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | gift occasion; purpose; manner; time; `w prezencie` |
| evidenceSource | Batch 04 §33; WSJP `dać` sense 1 — independently exact `CO + KOMU` |
| proposedLiveGuard | `require-exact-pattern-shapes` (B) |

### Order 34 — `brać` (imperfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `literal-taking` |
| meaningScope | Literal grasping/taking of an entity. Two distinct source schemas, kept as alternatives. |
| schemaKeyProposal | **A1** `accusative-entity-optional-instrumental-means` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | `case:instrumental role=means optional` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | animate subject |
| explicitExclusions | destination; manner; time; circumstance |
| evidenceSource | Batch 04 §34; WSJP `brać I` sense 1 — `CO + (CZYM)` |
| proposedLiveGuard | `require-exact-pattern-shapes` (C) |

| Field | Value |
|---|---|
| schemaKeyProposal | **A2** `accusative-entity-za-accusative-gripped-part` |
| requiredComplements | `case:accusative role=object required`; `preposition-case:za+accusative role=target required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | personal subject |
| explicitExclusions | as A1 |
| evidenceSource | Batch 04 §34; WSJP `brać I` sense 1 — `KOGO/CO + za CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (C) |

### Order 34 — `brać` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `fixed-participation` |
| meaningScope | Fixed lexical construction `brać udział w czymś` = participation. A separate lexical entry, **not** derived from ordinary object syntax. |
| schemaKeyProposal | `w-locative-participation-target` |
| requiredComplements | `preposition-case:w+locative role=target required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | **`udział`** — required lexical material of the fixed construction |
| generalizedRoleStatus | not a generalized role; exact governed complement of the fixed entry |
| subjectOrParticipantRestriction | personal subject |
| explicitExclusions | participation modifiers (`aktywny`, `czynny`); event circumstances; time; manner; treating `udział` as a replaceable Accusative object; modelling this as generic `brać + w + Locative` |
| evidenceSource | Batch 04 §34; WSJP fixed entry `ktoś bierze udział w czymś` |
| proposedLiveGuard | `require-exact-pattern-shapes` (D) + `require-lexical-material-in-explanation` (E) |

**Schema-representation note.** The locked candidate-pattern schema has **no
field that structurally attaches required lexical material to a pattern**.
This matrix therefore records `requiredLexicalMaterial = udział` as a
control-plane fact and invents no new `candidateContent` field and no
fixed-expression complement type. The authored pattern will structurally encode
only `w + Locative`; the fixed-expression identity is additionally controlled
by lemma-level `requiredLexicalItems` governance (already present on `brać`),
this approved matrix, the learner explanation, the authored example, the Batch 4
historical content lock, and independent linguistic review. A genuine
pattern-level representation remains an open later schema question.

### Order 35 — `wziąć` (perfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `bounded-literal-taking` |
| meaningScope | Bounded literal grasping/taking. Independently evidenced; nothing obtained because `brać` has it. |
| schemaKeyProposal | **A1** `accusative-entity-optional-instrumental-means` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | `case:instrumental role=means optional` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | animate subject |
| explicitExclusions | destination; time; manner; circumstance |
| evidenceSource | Batch 04 §35; WSJP `wziąć` sense 1 — independently `CO + (CZYM)` |
| proposedLiveGuard | `require-exact-pattern-shapes` (F) |

| Field | Value |
|---|---|
| schemaKeyProposal | **A2** `accusative-entity-za-accusative-gripped-part` |
| requiredComplements | `case:accusative role=object required`; `preposition-case:za+accusative role=target required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | personal subject |
| explicitExclusions | as A1 |
| evidenceSource | Batch 04 §35; WSJP `wziąć` sense 1 — independently `KOGO/CO + za CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (F) |

### Order 35 — `wziąć` — meaning B of B

| Field | Value |
|---|---|
| meaningKeyProposal | `fixed-participation` |
| meaningScope | Fixed lexical construction `wziąć udział w czymś` = entry into participation. Separate WSJP fixed entry, independently evidenced from `brać`'s. |
| schemaKeyProposal | `w-locative-participation-target` |
| requiredComplements | `preposition-case:w+locative role=target required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | **`udział`** |
| generalizedRoleStatus | not a generalized role; exact governed complement of the fixed entry |
| subjectOrParticipantRestriction | personal subject |
| explicitExclusions | as `brać` participation |
| evidenceSource | Batch 04 §35; WSJP fixed entry `ktoś wziął udział w czymś` |
| proposedLiveGuard | `require-exact-pattern-shapes` (F) + `require-lexical-material-in-explanation` (F) |

### Order 36 — `czytać` (imperfective) — one meaning, five alternatives

Source enumerates each variant with explicit parenthesized optionality:
`CO + (KOMU) + (GDZIE)`; topic variant `(CO) + (KOMU) + o KIM/CZYM`;
content-clause variants with optional `o KIM/CZYM` and `GDZIE`;
`(KOMU) + MOWA WPROST`.

| Field | Value |
|---|---|
| meaningKeyProposal | `reading-written-content` |
| meaningScope | Reading written symbols/text, including process/habitual reading, content reporting, and reading aloud. |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | reading frequency, speed, manner, language, medium, incidental place; **any concrete location frame** |
| evidenceSource | Batch 04 §36; WSJP `czytać` sense 1 |

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind | generalizedRoleStatus |
|---|---|---|---|---|---|
| 1 | `accusative-content-optional-listener` | `case:accusative role=object required` | `case:dative role=recipient optional` | — | source schema also carries optional generalized `GDZIE`; **recorded as role evidence only, not authored** |
| 2 | `o-locative-topic` | `preposition-case:o+locative role=topic required` | `case:accusative role=object optional`; `case:dative role=recipient optional` | — | not applicable |
| 3 | `ze-content-clause` | `clause:ze role=content required` | `preposition-case:o+locative role=topic optional` | `ze` | optional generalized `GDZIE`; **not authored** |
| 4 | `interrogative-content-clause` | `clause:interrogative role=content required` | `preposition-case:o+locative role=topic optional` | `interrogative` | optional generalized `GDZIE`; **not authored** |
| 5 | `direct-speech-content` | `clause:direct-speech role=content required` | `case:dative role=recipient optional` | `direct-speech` | not applicable |

Proposed live guard: `require-exact-pattern-shapes` (G) +
`allow-only-preposition-case-signatures` (H) restricted to the single
authorized `o+locative` topic signature, which structurally blocks any
concretization of `GDZIE` into `w`/`na` + Locative, `do` + Genitive, or any
other location preposition.

**Conservative-reading note.** The source lists optional `KOMU` explicitly on
variants 1, 2 and 5 but **not** on the content-clause variants. This matrix
therefore does not attach a Dative listener to alternatives 3 and 4. Adding an
unlisted participant would breach the "do not add what the schema does not
license" discipline.

### Order 38 — `pisać` (imperfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `text-creation` |
| meaningScope | Creating and recording a text or music (WSJP sense 2). |
| schemaKeyProposal | `accusative-created-text` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | correspondence addressees of any form; writing medium, place, time, language, frequency, manner; creative-sense `do gazet / do tygodników` connections (explicitly **not** an addressee schema) |
| evidenceSource | Batch 04 §38; WSJP `pisać` sense 2 — exact `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (I), creation meaning only |

### Order 38 — `pisać` — meaning B of B — **RESOLVED** (see §11 for HOLD/resolution history)

| Field | Value |
|---|---|
| meaningKeyProposal | `written-correspondence` |
| meaningScope | Communicating information in writing (WSJP sense 4). |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | `do + Genitive` never generalized beyond correspondence; writing medium, place, time, language, frequency, manner; creative-sense newspaper connections; merging Dative and `do + Genitive` into one frame; Dative/`do` co-occurrence in one pattern |
| evidenceSource | Batch 04 §38 (sense identification only) + externally supplied primary-source adjudication (exact schema structure; see §11) |

Two parallel, mutually exclusive recipient modes, six content families each,
**all recipients optional in every `pisać` correspondence schema**:

**Mode A — Dative recipient (optional throughout)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| A1 | `dative-topic` | `preposition-case:o+locative role=topic required` | `case:dative role=recipient optional` | — |
| A2 | `dative-ze-clause` | `clause:ze role=content required` | `case:dative role=recipient optional` | `ze` |
| A3 | `dative-zeby-clause` | `clause:zeby role=content required` | `case:dative role=recipient optional` | `zeby` |
| A4 | `dative-interrogative-clause` | `clause:interrogative role=content required` | `case:dative role=recipient optional` | `interrogative` |
| A5 | `dative-direct-speech` | `clause:direct-speech role=content required` | `case:dative role=recipient optional` | `direct-speech` |
| A6 | `dative-accusative-content` | `case:accusative role=object required` | `case:dative role=recipient optional` | — |

**Mode B — `do` + Genitive recipient (optional throughout)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| B1 | `do-genitive-topic` | `preposition-case:o+locative role=topic required` | `preposition-case:do+genitive role=recipient optional` | — |
| B2 | `do-genitive-ze-clause` | `clause:ze role=content required` | `preposition-case:do+genitive role=recipient optional` | `ze` |
| B3 | `do-genitive-zeby-clause` | `clause:zeby role=content required` | `preposition-case:do+genitive role=recipient optional` | `zeby` |
| B4 | `do-genitive-interrogative-clause` | `clause:interrogative role=content required` | `preposition-case:do+genitive role=recipient optional` | `interrogative` |
| B5 | `do-genitive-direct-speech` | `clause:direct-speech role=content required` | `preposition-case:do+genitive role=recipient optional` | `direct-speech` |
| B6 | `do-genitive-accusative-content` | `case:accusative role=object required` | `preposition-case:do+genitive role=recipient optional` | — |

Mode A and Mode B are alternatives and must never co-occur in one pattern; no
pattern requires a recipient. Total: **12 alternatives**.

**Source-row vs. product-row note.** The adjudicated primary source expresses
this as 8 schema rows (2 recipient modes × 4 content families, where "clause
content" is one family covering three alternative clause kinds). The Phase 4B
product architecture represents each concrete `clauseKind` (`ze`, `zeby`,
`interrogative`) as its own alternative, so the clause family expands from 1
source row to 3 product rows per recipient mode (+2 rows each), yielding 12
product alternatives from 8 source rows. This is normalization of an
explicitly-alternative source clause-kind list into the locked
`clauseKind`-typed representation — not four invented schemas.

### Order 39 — `napisać` (perfective) — meaning A of B

| Field | Value |
|---|---|
| meaningKeyProposal | `completed-text-creation` |
| meaningScope | Completed creation and recording of a text or music (WSJP sense 2). |
| schemaKeyProposal | `accusative-created-text` |
| requiredComplements | `case:accusative role=object required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | correspondence addressees; medium, place, time, language, repetition, manner; creative-sense `do gazety / do tygodnika` connections |
| evidenceSource | Batch 04 §39; WSJP `napisać` sense 2 — **independently** exact `CO` |
| proposedLiveGuard | `require-exact-pattern-shapes` (J), creation meaning only |

### Order 39 — `napisać` — meaning B of B — **RESOLVED** (see §11 for HOLD/resolution history)

| Field | Value |
|---|---|
| meaningKeyProposal | `completed-written-correspondence` |
| meaningScope | Completed written communication (WSJP sense 4). |
| subjectOrParticipantRestriction | — |
| requiredLexicalMaterial | — |
| explicitExclusions | `do + Genitive` never generalized beyond correspondence; Dative/`do` alternatives never merged; medium, place, time, language, repetition, manner; creative-sense newspaper connections; flattening every variant into one optional maximal frame; **normalizing `napisać`'s schema-specific Dative requiredness to `pisać`'s uniformly-optional Dative** |
| evidenceSource | Batch 04 §39 (sense identification and Dative-asymmetry statement only) + externally supplied primary-source adjudication (exact schema structure; see §11) |

Same two parallel recipient modes as `pisać`, independently sourced. **Critical
asymmetry: Dative is required on the three clause alternatives (A2–A4) and
optional everywhere else.** `do` + Genitive remains optional throughout, in
both lemmas.

**Mode A — Dative recipient (requiredness varies by alternative — do not normalize)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| A1 | `dative-topic` | `preposition-case:o+locative role=topic required` | `case:dative role=recipient optional` | — |
| A2 | `dative-ze-clause` | `clause:ze role=content required`; **`case:dative role=recipient required`** | — | `ze` |
| A3 | `dative-zeby-clause` | `clause:zeby role=content required`; **`case:dative role=recipient required`** | — | `zeby` |
| A4 | `dative-interrogative-clause` | `clause:interrogative role=content required`; **`case:dative role=recipient required`** | — | `interrogative` |
| A5 | `dative-direct-speech` | `clause:direct-speech role=content required` | `case:dative role=recipient optional` | `direct-speech` |
| A6 | `dative-accusative-content` | `case:accusative role=object required` | `case:dative role=recipient optional` | — |

**Mode B — `do` + Genitive recipient (optional throughout, uniform with `pisać`)**

| # | schemaKeyProposal | requiredComplements | optionalComplements | clauseKind |
|---|---|---|---|---|
| B1 | `do-genitive-topic` | `preposition-case:o+locative role=topic required` | `preposition-case:do+genitive role=recipient optional` | — |
| B2 | `do-genitive-ze-clause` | `clause:ze role=content required` | `preposition-case:do+genitive role=recipient optional` | `ze` |
| B3 | `do-genitive-zeby-clause` | `clause:zeby role=content required` | `preposition-case:do+genitive role=recipient optional` | `zeby` |
| B4 | `do-genitive-interrogative-clause` | `clause:interrogative role=content required` | `preposition-case:do+genitive role=recipient optional` | `interrogative` |
| B5 | `do-genitive-direct-speech` | `clause:direct-speech role=content required` | `preposition-case:do+genitive role=recipient optional` | `direct-speech` |
| B6 | `do-genitive-accusative-content` | `case:accusative role=object required` | `preposition-case:do+genitive role=recipient optional` | — |

Mode A and Mode B are alternatives and must never co-occur in one pattern.
Total: **12 alternatives**.

**Source-row vs. product-row note.** As with `pisać`, the adjudicated primary
source expresses this as 8 schema rows; the mandatory-Dative "clause" family
(A2–A4) is one source row that itself already states the required-Dative fact
for all three clause kinds, expanded here into 3 product rows each carrying
that same required Dative — the requiredness is preserved exactly through the
expansion, not reallocated. 8 source rows → 12 product alternatives.

### Order 40 — `spotykać się` (imperfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `recurring-social-meeting` |
| meaningScope | Recurring or processual social meetings and contact. Lexical `się` is part of the identity. |
| schemaKeyProposal | `z-instrumental-meeting-partner` |
| requiredComplements | `preposition-case:z+instrumental role=interlocutor required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | lexical `się` is part of `canonicalLemma`, not a complement |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | `z + Instrumental` is the exact schema for a **singular personal subject**. A **reciprocal plural personal subject** may occur without a separate partner phrase; this is recorded as a participant/usage constraint in `internalScope`, **not** as a second complementless product pattern. |
| explicitExclusions | frequency; time; place; manner; purpose; accompanying activities; stripping `się` |
| evidenceSource | Batch 04 §40; WSJP `spotykać się` sense 1 |
| proposedLiveGuard | `require-lexical-identity` (`się`) + `require-exact-pattern-shapes` (K) |

**Reciprocal-representation decision.** The evidence states the reciprocal
plural construction "adds no new complement type". Authoring a second,
complementless pattern would assert a product construction the locked model
does not need and the evidence does not require. The architecture-compatible
representation is therefore one complement schema plus a documented participant
restriction. This decision is recorded here so independent review can accept or
reject it before authoring.

### Order 41 — `spotkać się` (perfective)

| Field | Value |
|---|---|
| meaningKeyProposal | `completed-social-meeting` |
| meaningScope | A completed/bounded social meeting or contact. Lexical `się` is part of the identity. |
| schemaKeyProposal | `z-instrumental-meeting-partner` |
| requiredComplements | `preposition-case:z+instrumental role=interlocutor required` |
| optionalComplements | — |
| clauseKind | — |
| requiredLexicalMaterial | lexical `się` in `canonicalLemma` |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | same singular/reciprocal-plural treatment as order 40, **independently evidenced** from Batch 05 §41 |
| explicitExclusions | time; place; manner; purpose; accompanying activities; stripping `się` |
| evidenceSource | **Batch 05 §41**; WSJP `spotkać się` sense 1 |
| proposedLiveGuard | `require-lexical-identity` (`się`) + `require-exact-pattern-shapes` (L) |

## 3. Per-lemma rationale

- **`dawać` / `dać`** — Each source gives one exact schema, `CO + KOMU`, with
  both participants bare (required). One meaning, one alternative each. The
  identical inventory is expected and correct: Phase 3 verified each form
  independently and explicitly states nothing is borrowed either way.
- **`brać` / `wziąć`** — Two clearly separate meanings each. The literal sense
  has two distinct source schemas differing in subject restriction and in
  whether the second participant is an optional Instrumental means or a
  required `za + Accusative` gripped part; these stay alternatives. The fixed
  participation entry is a separate WSJP lexical entry, so it is a separate
  meaning, never a literal-sense variant.
- **`czytać`** — One meaning, five alternatives, each enumerated in the source
  with its own optionality. Optional `GDZIE` appears in three of them and is
  deliberately left unauthored.
- **`pisać` / `napisać`** — Creation senses are exact and settled: bare
  Accusative, no addressee. Correspondence senses are now **resolved** (§11):
  two mutually exclusive recipient modes (Dative, `do` + Genitive) × six
  content families (topic, `że`, `żeby`, interrogative-dependent, direct
  speech, Accusative) = 12 alternatives each, never merged into one frame.
  `napisać`'s Dative is required on exactly the three clause alternatives and
  optional elsewhere — this asymmetry versus `pisać`'s uniformly-optional
  Dative is preserved exactly, not normalized in either direction.
- **`spotykać się` / `spotkać się`** — One meaning and one complement schema
  each, plus a documented reciprocal participant restriction.

## 4. Required/optional participant audit

Every row above states requiredness explicitly per complement. No source
schema was decomposed into a required core pattern plus a standalone
optional-participant pattern, and no alternatives were merged.

| Lemma | Optional participants carried inside their own schema |
|---|---|
| `dawać` / `dać` | none — both complements required |
| `brać` / `wziąć` | literal A1: optional `case:instrumental role=means` inside the Accusative schema (never standalone) |
| `czytać` | alt 1: optional Dative; alt 2: optional Accusative **and** optional Dative (only `o+locative` required); alts 3–4: optional `o+locative`; alt 5: optional Dative |
| `pisać` | creation: none. Correspondence: optional Dative on all 6 Mode-A alternatives; optional `do`+Genitive on all 6 Mode-B alternatives |
| `napisać` | creation: none. Correspondence: optional Dative on A1/A5/A6 only — **required** Dative on A2/A3/A4 (not optional, not normalized); optional `do`+Genitive on all 6 Mode-B alternatives |
| `spotykać się` / `spotkać się` | none — the single complement is required |

Explicitly checked and rejected: no standalone `instrumental-means` pattern for
`brać`/`wziąć`; no standalone `dative-listener` or standalone `o-locative`
pattern for `czytać`; no standalone addressee pattern anywhere; no
`pisać`/`napisać` pattern requires a recipient by default (only `napisać`
A2–A4 do, and only because the adjudicated source requires it there
specifically); no Dative/`do`+Genitive co-occurrence in any single pattern.

## 5. Aspect independence audit

| Family | Decision | Enforcement in this matrix |
|---|---|---|
| `dawać` / `dać` | **RETAIN BOTH** | Separate rows citing each lemma's own WSJP sense; identical shape is independently evidenced, not copied |
| `brać` / `wziąć` | **RETAIN BOTH** | Separate literal schemas and separate fixed `udział` entries per lemma |
| `czytać` / `przeczytać` | `czytać` = full-pattern anchor; **`przeczytać` = metadata-only** | No `przeczytać` row exists in this matrix |
| `pisać` / `napisać` | **RETAIN BOTH** | Creation rows separately sourced; correspondence resolved separately per lemma with `napisać`'s schema-specific required-Dative alternatives (A2–A4) kept exactly as adjudicated and **not** normalized to `pisać`'s uniformly-optional Dative in either direction |
| `spotykać się` / `spotkać się` | **RETAIN BOTH** | `spotkać się` sourced from **Batch 05**, not from order 40 |

No aspect partner donates syntax. No family is reconsidered here.

## 6. Lexical identity / fixed-material audit

- **`udział`** (`brać`, `wziąć`) — recorded as `requiredLexicalMaterial` in the
  participation rows. Not modelled as a complement, not modelled as a
  replaceable Accusative object, and no fixed-expression complement type is
  introduced. Both lemmas already carry lemma-level
  `requiredLexicalItems: ["udział"]` in the frozen skeleton.
- **`się`** (`spotykać się`, `spotkać się`) — part of `canonicalLemma`, never a
  complement. Neither lemma inherits from a non-reflexive form.
- **`przeczytać`** — remains metadata-only; no schema row; contributes no
  syntax to `czytać`.

## 7. Generalized-role audit

Only one generalized role appears in Batch 4: optional `GDZIE` in three
`czytać` source schemas (alternatives 1, 3, 4).

It is recorded **as role evidence only**. This matrix authorizes **no**
concrete reading-location realization — no `w + Locative`, no `na + Locative`,
no `do + Genitive`, no other location preposition. Reading place, medium,
language, speed and frequency remain outside product complement syntax. The
proposed `allow-only-preposition-case-signatures` guard (H) makes this
structurally enforceable by allowlisting only the authorized `o+locative` topic
signature for `czytać`.

No other Batch 4 construction is a narrowed realization of a generalized role;
`za + Accusative`, `w + Locative` (participation), `z + Instrumental`,
`o + Locative`, and `do + Genitive` (correspondence) are all exact
schema-listed positions.

## 8. Explicit exclusion audit

| Lemma | Excluded |
|---|---|
| `dawać`, `dać` | gift occasion, purpose, manner, time, `w prezencie` |
| `brać`, `wziąć` | literal destination, manner, time, circumstance; participation modifiers (`aktywny`, `czynny`); event circumstances; generic `brać/wziąć + w + Locative` reading of participation |
| `czytać` | frequency, speed, manner, language, medium, incidental place; **all concrete location frames** |
| `pisać`, `napisać` | creation/correspondence merger; `do + Genitive` outside correspondence; creative-sense newspaper connections as an addressee schema; medium, place, time, language, frequency/repetition, manner; Dative+`do` merger; maximal-frame flattening; normalizing `napisać`'s required-Dative alternatives to optional or vice versa |
| `spotykać się`, `spotkać się` | frequency, time, place, manner, purpose, accompanying activities; stripping `się` |

## 9. Proposed live-guard plan (NOT implemented in this task)

`tests/fixtures/priority8_phase4b_authoring_rules.json` is **unchanged** by
this task. Presence-asserting rules must land in the same commit as the
`candidateContent` they protect, per the test-lifecycle rule.

| Ref | Target | Proposed primitive | Purpose |
|---|---|---|---|
| A | `dawać` | `require-exact-pattern-shapes` | One meaning, one alternative, both complements required |
| B | `dać` | `require-exact-pattern-shapes` | Same, independently pinned |
| C | `brać` literal | `require-exact-pattern-shapes` | Two alternatives; optional Instrumental stays inside A1; no standalone means pattern |
| D | `brać` participation | `require-exact-pattern-shapes` | Exactly one `w+locative` alternative in the participation meaning |
| E | `brać` participation | `require-lexical-material-in-explanation` | Learner explanation must contain whole token `udział` |
| F | `wziąć` | same three as C/D/E | Independently pinned |
| G | `czytać` | `require-exact-pattern-shapes` | Five alternatives with exact optionality |
| H | `czytać` | `allow-only-preposition-case-signatures` | Allowlist `o+locative` topic only → blocks any `GDZIE` concretization |
| I | `pisać` | `require-exact-pattern-shapes` | Creation meaning (1 alternative) plus correspondence meaning (12 alternatives: 6 optional-Dative Mode A + 6 optional-`do` Mode B); the exact-shape check inherently prevents recipient-mode merger, Dative/`do` co-occurrence, clause-kind merger, and any maximal correspondence frame, since only the 13 declared shapes are accepted |
| J | `napisać` | `require-exact-pattern-shapes` | Creation meaning (1 alternative) plus correspondence meaning (12 alternatives), with the rule's declared shapes encoding **required** Dative on exactly A2–A4 and optional Dative/`do` everywhere else — this is what structurally prevents future authoring from normalizing `napisać`'s requiredness to `pisać`'s |
| K | `spotykać się` | `require-lexical-identity` + `require-exact-pattern-shapes` | `się` preserved; single required `z+instrumental` |
| L | `spotkać się` | `require-lexical-identity` + `require-exact-pattern-shapes` | Same, independently pinned |

**Guard-engine coverage assessment.** Every invariant above is expressible with
existing primitives; no new primitive is required. Two limitations are flagged
rather than papered over:

1. **`udział` is not structurally guaranteed.** `require-lexical-material-in-explanation`
   checks learner-explanation prose only. It cannot prove the pattern
   structurally contains the lexical item, and it does not interpret negation.
   This is a known, documented limitation, not a defect introduced here.
2. **Subject/participant restrictions are not structurally expressible.** The
   animate-vs-personal subject split (`brać`/`wziąć` literal) and the
   singular-vs-reciprocal-plural split (`spotykać się`/`spotkać się`) have no
   field in the locked schema. They are recorded in this matrix and must be
   carried in `internalScope`; no guard can enforce them.

## 10. Matrix reconciliation summary

- **Full-pattern lemmas covered:** exactly 9 — orders 32, 33, 34, 35, 36, 38,
  39, 40, 41.
- **Order 37 `przeczytać`:** remains **metadata-only**; no schema row; no
  syntax donated to `czytać`. ✔
- **Meanings proposed:** **13** — `dawać` 1, `dać` 1, `brać` 2, `wziąć` 2,
  `czytać` 1, `pisać` 2, `napisać` 2, `spotykać się` 1, `spotkać się` 1.
- **Schema alternatives fully resolved:** **41** — `dawać` 1, `dać` 1, `brać` 3,
  `wziąć` 3, `czytać` 5, `pisać` **13** (1 creation + 12 correspondence),
  `napisać` **13** (1 creation + 12 correspondence), `spotykać się` 1,
  `spotkać się` 1. Independently recomputed: 1+1+3+3+5+13+13+1+1 = 41.
- **HOLD rows:** **0.** Both original HOLDs (`pisać` `written-correspondence`,
  `napisać` `completed-written-correspondence`) are now **resolved** — see §11
  for the full HOLD/resolution history, including why the original HOLD was
  correct and exactly what new evidence closed it.
- **Required lexical / identity constraints preserved:** ✔ `udział` recorded
  for both participation meanings without inventing a field; lexical `się`
  preserved in both meeting lemmas; `przeczytać` metadata-only.
- **Aspect independence:** ✔ all five families handled per §5; no partner
  donates syntax; `napisać`'s schema-specific required-Dative alternatives are
  preserved exactly, not normalized to `pisać`'s in either direction.
- **Generalized-role discipline:** ✔ `czytać` `GDZIE` left unconcretized.
- **Recipient-mode discipline (`pisać`/`napisać`):** ✔ Dative and `do` +
  Genitive never co-occur in one pattern; no pattern requires a recipient
  except `napisać` A2–A4, exactly as adjudicated.

**This matrix is ready for authoring**, pending independent matrix review.

## 11. HOLD / resolution history

**Summary.** The initial Phase 4B4-A pass placed correspondence authoring for
`pisać` and `napisać` on HOLD because the frozen repository summary did not
preserve source-row cardinality and schema-specific recipient requiredness at
the granularity the product matrix needs. That HOLD was correct given the
evidence available at the time: the repository text was a *compressed
characterization*, not a per-schema enumeration, and guessing a plausible
structure would have manufactured precision the repository did not contain —
the same failure mode the `wymagać` correction was raised to prevent.

A separate primary-source adjudication has since supplied the missing exact
schema structure directly from the authoritative WSJP entries. This
adjudication was performed **outside this matrix task** and its results were
supplied to this task as adjudicated fact; this task did not itself perform
fresh web research to obtain it, and the original repository Phase 3 report
(`reports/priority-8-phase-3-batch-04.md`) has **not** been edited or
represented as having contained this granularity originally. The two HOLDs are
resolved below using that supplied structure; the two correspondence tables in
§2 (order 38 and order 39) already reflect the resolution.

### HOLD-1 (original) — `pisać` (order 38), meaning `written-correspondence`

**Repository evidence, quoted exactly** (Batch 04 §38; the verification CSV
`secondary_source_evidence_summary` says the same in different words):

> gives parallel optional `KOMU` and `do KOGO` addressee schemas with `CO`,
> `o KIM/CZYM`, `że`, `żeby`, an interrogative-dependent clause, or direct
> speech.

**What is settled.** Correspondence is a separate sense from creation. The
content inventory is six shapes: Accusative content, `o + Locative` topic, `że`,
`żeby`, interrogative-dependent, direct speech. There are two addressee forms,
Dative and `do + Genitive`, both marked optional, and they are **parallel**
(alternatives), so they must never co-occur in one pattern.

**What is unresolved.** The evidence gives a *compressed characterization*, not
a per-schema enumeration. Three questions cannot be answered from the
repository:

1. **Cardinality.** Does WSJP list a full cross-product — two addressee forms ×
   six content shapes = 12 alternatives — or six content alternatives each of
   which may realize its addressee in either form, or some smaller set? "Parallel
   … schemas with A, B, C, D, E, or F" is compatible with more than one reading.
2. **Addressee/content pairing.** Is *every* content shape licensed with *both*
   addressee forms? The prompt's own rule — "Do not assume that every recipient
   form combines with every content form unless the source explicitly gives that
   schema" — cannot be satisfied, because the source does not spell the pairings
   out.
3. **Degenerate overlap.** If both addressee forms are optional, the
   addressee-omitted realization of a Dative variant and of a `do + Genitive`
   variant are structurally identical, producing duplicate patterns under
   `require-exact-pattern-shapes`. Whether the intended representation collapses
   these is a representation decision, not something the evidence settles.

**Contrast that makes this a genuine HOLD.** `czytać`'s evidence in the same
report enumerates each variant with its own parenthesized optionality
(`CO + (KOMU) + (GDZIE)`, `(CO) + (KOMU) + o KIM/CZYM`, …), which is why
`czytać` is fully resolved above. `pisać`'s correspondence evidence is written
at a strictly lower level of structural detail.

### HOLD-2 (original) — `napisać` (order 39), meaning `completed-written-correspondence`

**Repository evidence, quoted exactly** (Batch 04 §39):

> independently gives `KOMU` and `do KOGO` addressee alternatives with `CO`,
> `o KIM/CZYM`, clauses, or direct speech; Dative is required in the dedicated
> clause schema and optional in the other listed Dative variants.

Reinforced by the Batch 04 risk review:

> `napisać` has schema-specific Dative optionality, including a required Dative
> in its dedicated clause variant; later authoring must not flatten every
> variant into one optional maximal frame.

**What is settled.** Correspondence is separate from creation. Dative
optionality is **schema-specific** and must not be normalized. At least one
schema has a **required** Dative. `napisać`'s matrix must not be copied from
`pisać`'s.

**What is unresolved.** All three `pisać` questions apply, plus two more that
are specific and consequential:

4. **Which schema is "the dedicated clause schema"?** The phrase is singular,
   but the content list says "clauses" (plural) and the structured CSV field
   lists three clause kinds for this lemma (`że`, `żeby`,
   interrogative-dependent) plus direct speech. Is the required-Dative schema
   one collective clause schema covering all three, or one specific clause kind?
   Authoring the wrong one would assert a required Dative where the source does
   not license it, or drop it where it does.
5. **Is direct speech inside or outside the required-Dative schema?** For
   `czytać`/`przeczytać` the direct-speech schema is `(KOMU) + MOWA WPROST` —
   Dative optional. For `napisać`, direct speech is listed separately from
   "clauses", and its Dative status is not stated. It cannot be inferred from
   the reading family without transferring evidence across lemmas.

**Why this must not be guessed.** Section 12 of the authoring brief names this
the "major independent-review target" and requires deriving requiredness *per
alternative* from the exact source. Producing plausible-looking rows here would
manufacture precision the repository does not contain — exactly the failure mode
that the `wymagać` correction was raised to prevent.

### Resolution actually adopted

The original HOLD statement offered two options: (a) re-inspect and re-record
the source at `czytać`-level granularity, or (b) author a defensible subset
now and defer the rest. **Option (a) was effectively taken**, via an external
primary-source adjudication rather than fresh research performed inside this
task. The adjudicated structure supplied and now recorded in §2:

- confirms the content-family inventory this matrix already expected (topic,
  three clause kinds, direct speech, Accusative content) — six families, not
  a smaller or larger set;
- confirms both recipient forms (Dative, `do` + Genitive) are optional in
  every `pisać` schema, resolving HOLD-1 question 1 (cardinality: 2 modes × 6
  families = 12, not a smaller cross-product) and question 2 (addressee/content
  pairing: every content family pairs with both recipient modes; the
  adjudication did not report any family excluded from either mode) and
  question 3 (degenerate overlap: the two modes remain listed as genuinely
  separate alternatives in the primary source despite both being optional, so
  they are kept as 12 distinct declared alternatives rather than collapsed —
  this is a fact taken from the adjudication, not a representation choice made
  here);
- resolves HOLD-2 question 4 (which schema is "the dedicated clause schema"):
  it is not one collective schema but specifically the three clause-kind
  alternatives A2–A4, each independently carrying the required Dative;
- resolves HOLD-2 question 5 (direct speech's Dative status for `napisać`):
  direct speech is **outside** the required-Dative set — its Dative is
  optional, patterning with topic and Accusative content rather than with the
  three clause kinds.

No question raised in HOLD-1 or HOLD-2 was left unaddressed by the supplied
adjudication.
