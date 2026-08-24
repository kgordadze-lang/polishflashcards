# Priority 8 Phase 4B6 — Batch 6 schema matrix

## 1. Starting state

This is a **control-plane authoring plan** produced before any Batch 6
`candidateContent` is written. It is not candidate content, not a staging
schema, not runtime data, not a guard, and it allocates no stable ID. It adds
no field to the locked Phase 4B candidate-content schema.

Starting endpoint, verified before any file was created:

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `248c740b3ee52363d2e878e570877734ee0f6a0b`
- tree `04df0291a1d436fcb5e61e9c4ec6dfe3cb6d140b`
- parent `f69132cc757bdf2b5033c0b5824ceb1dbc716fbc`
- subject `Correct Priority 8 Phase 4B5 example quality`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook (`-rwxr-xr-x .git/hooks/pre-push`)

Recorded content invariants (must remain byte-identical through this task):

- `editorial/priority-8-phase4-staging.json` SHA-256
  `fbc25a832c7bd50d775117c877d1876eaa213545785f881585ef5819169c4442`
- `tests/fixtures/priority8_phase4b_authoring_rules.json` SHA-256
  `4cd62f335c8af96f655de49d6f1ed58acd8dba8a3f4eddb461c1c3b7dc6c8f2f`

Final Batch 5 digest currently pinned, located and confirmed at three
independent sites — `tests/test_priority8_phase4b5_batch05.py:38`,
`reports/priority-8-phase-4b5-batch-05-authoring.md:241`, and
`reports/priority-8-phase-4b5-batch-05-risk-review.md:330`:

`d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951`

This matches the expected value in the task brief exactly.

Recomputed staging logical state (recomputed from the file, not taken on
trust):

| Quantity | Value |
|---|---:|
| `phaseStep` | `4B5` |
| `stagingRevision` | 6 |
| authored full-pattern lemmas | 49 |
| meanings | 66 |
| patterns | 164 |
| examples | 164 |
| future-empty full-pattern lemmas | 19 |
| total staging lemma records | 68 |

Scoped Phase 4B test baseline recomputed: **219 tests** across the nine suites
(31 + 65 + 9 + 11 + 17 + 23 + 29 + 8 + 26 = 219). Every expected starting-state
value in the brief was reproduced; there is **no state mismatch**.

All ten Batch 6 records carry `bindingConstraints: []` in staging — none of the
ten is a `KEEP WITH NARROWING` record and none is one of the five additional
`compatible with narrowing` representation records. The per-lemma authoring
constraints that do bind them come from the Phase 3B freeze CSV
(`authoring_constraint` column) and are quoted per lemma in §5.

## 2. Exact Batch 6 scope

Exactly these ten full-pattern lemmas, all `full_pattern_in_phase4 = yes` and
`human_freeze_status = FROZEN FULL-PATTERN LEMMA` in the Phase 3B freeze:

| Order | Lemma | Aspect | Aspect partner | Phase 3 disposition | Fit | Evidence |
|---|---|---|---|---|---|---|
| 52 | `gotować` | imperfective | — | KEEP VERIFIED | compatible | A |
| 53 | `rezerwować` | imperfective | `zarezerwować` | KEEP VERIFIED | compatible | A |
| 54 | `cieszyć się` | imperfective | — | KEEP VERIFIED | compatible | A |
| 55 | `martwić się` | imperfective | — | KEEP VERIFIED | compatible | A |
| 56 | `zgadzać się` | imperfective | — | KEEP VERIFIED | compatible | A |
| 57 | `zapraszać` | imperfective | — | KEEP VERIFIED | compatible | A |
| 58 | `polecać` | imperfective | — | KEEP VERIFIED | compatible | A |
| 59 | `radzić` | imperfective | — | KEEP VERIFIED | compatible | A |
| 60 | `pasować` | imperfective | — | KEEP VERIFIED | compatible | A |
| 61 | `móc` | imperfective | — | KEEP VERIFIED | compatible | A |

This is exactly the frozen Batch 6 slice `52-61` of the seven-batch map in
`reports/priority-8-phase-4b1a-authoring-schema-lock.md` (`10 / 10 / 10 / 9 /
10 / 10 / 9`).

**Evidence boundary observed.** Orders 52–60 are Phase 3 Batch 06 rows; order
61 `móc` is a Phase 3 Batch 07 row. Batch 07 material was consulted **only**
for order 61.

Explicitly excluded and not given a Batch 6 row:

- order 51 `powiedzieć` — a Batch 06 *verification* row, but already authored
  in **Batch 5** (staging shows one meaning, eleven patterns);
- order 62 `musieć` and every later order — **Batch 7** authoring scope;
- orders 17 `zaczynać` and 37 `przeczytać` — metadata-only identities, both
  outside this range;
- `radzić sobie` (order 29) — a separate, already-authored lexical identity.

`zarezerwować` is recorded in the freeze as `rezerwować`'s aspect partner but
is **not** among the 68 and receives nothing here; no syntax is transferred
through the aspect relation.

## 3. Source hierarchy

Binding source hierarchy, in order of authority:

1. `reports/priority-8-phase-3-batch-06.md` (+ risk review, verification CSV)
   — orders 52–60.
2. `reports/priority-8-phase-3-batch-07.md` (+ risk review, verification CSV)
   — order 61 `móc`.
3. `reports/priority-8-phase-3-final-synthesis.md`.
4. `reports/priority-8-phase-3b-final-lemma-freeze.{csv,md}`,
   `reports/priority-8-phase-3b-phase4-handoff.md`,
   `reports/priority-8-phase-3b-risk-review.md`.
5. Phase 4B control documents:
   `reports/priority-8-phase-4b1a-authoring-schema-lock.md`,
   `reports/priority-8-phase-4b4-schema-matrix.md`,
   `reports/priority-8-phase-4b5-schema-matrix.md`,
   `reports/priority-8-phase-4b-authoring-guard-hardening.md`,
   `reports/priority-8-phase-4b-test-lifecycle.md`.
6. Read-only structural authority for what the locked model can express:
   `validate_priority8_staging.py`,
   `tests/fixtures/priority8_phase4b_authoring_rules.json`,
   `tests/test_priority8_phase4b_authoring_guards.py`, and — for role and
   relation-type convention only — `editorial/verb-pattern-candidates.json`.
   None of these was modified.

**No fresh web research was performed.** No construction was broadened from
general Polish intuition.

### 3.1 How the two evidence layers were read

The verification-CSV field `supported_constructions_structured` is a **flat
complement inventory**, not a per-schema grouping. Batch 6 demonstrates the
limitation directly:

- `radzić`'s flat list contains `case:Dative(advisee,required,...)` **and**
  `case:Dative(advisee,optional,infinitive schema)` as two entries with a
  prose qualifier inside the parentheses. The flat list cannot say which
  content complement each Dative belongs to.
- `pasować`'s flat list repeats `preposition-case:do+Genitive` three times
  with three different roles and two different optionality states, tagged only
  by a trailing `senseN` marker.
- `zgadzać się`'s flat list marks every entry with `sense1`/`sense2` but
  never expresses that the sense-2 `z + Instrumental` is **required** in one
  source row and **optional** in another.
- `gotować`'s flat list gives two independently optional entries but not the
  fact that they belong to **one** source schema.

The authoritative per-schema layer is therefore the **narrative report's
per-lemma section**, which quotes the WSJP `Składnia` notation with explicit
parenthesised optionality (`(CO) + (KOMU)`, `CO + (dla KOGO)`, `optional KOMU
plus do KOGO/CZEGO`), explicit alternation bars (`z KOGO/CZEGO | na CO`,
`KOGO + na CO | do CZEGO`), and explicit schema enumeration ("gives X, a
separate Y, and Z"). Every row below is derived from that narrative layer and
cross-checked against the CSV. Where the two agree, the row is resolved. No
row in Batch 6 required the flat list to settle cardinality or requiredness.

**Notation used below:** `type:value role=… required|optional`. Alternation in
a source row (`A | B`) yields **separate** product alternatives, per global
rule B and the frozen `powiedzieć`/`zapraszać` precedent. Parenthesised source
positions yield `required: false`. Unparenthesised positions yield
`required: true`.

## 4. Full schema matrix

### Order 52 — `gotować` (imperfective)

Source (Batch 06 §52, `WSJP-GOTOW-03` sense 3): exact `(CO) + (KOMU)` — **one**
schema, **both** positions parenthesised.

| Field | Value |
|---|---|
| verificationOrder | 52 |
| lemma | `gotować` |
| aspect | imperfective |
| meaningKeyProposal | `meal-preparation` |
| meaningScope | Preparing hot meals or dishes (WSJP sense 3). Excludes food itself boiling/cooking (inchoative), and every other `gotować` sense. |
| schemaKeyProposal | **A1** `accusative-dish-dative-beneficiary` |
| requiredComplements | **none** |
| optionalComplements | `case:accusative role=object required=false`; `case:dative role=recipient required=false` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable — both positions are exact concrete `Składnia` labels, no generalized role involved |
| subjectOrParticipantRestriction | — |
| explicitExclusions | `dla + Genitive` (appears only outside the exact schema and receives no frame credit); kitchen/home location, time, frequency, manner, tools, ingredients, purpose; inchoative food-cooking/boiling and all other `gotować` senses |
| relationType | `lexical-frame` |
| evidenceSource | Batch 06 §52; risk review "Beneficiaries"; CSV order 52 |
| proposedLiveGuard | **A** `require-exact-pattern-shapes` |

**All-optional row.** See §7 row 1.

### Order 53 — `rezerwować` (imperfective)

Source (Batch 06 §53, `WSJP-REZERW-01` sense 1): `CO + (KOMU)` and
`CO + (dla KOGO)` — **two** schemas, object unparenthesised in both,
beneficiary parenthesised in both.

| Field | Value |
|---|---|
| verificationOrder | 53 |
| lemma | `rezerwować` |
| aspect | imperfective |
| meaningKeyProposal | `booking-reservation` |
| meaningScope | Booking a table, room, seat, ticket, service, or comparable reservable item for a customer/beneficiary (WSJP sense 1). Excludes setting time or resources aside (sense 2). |
| schemaKeyProposal | **A1** `accusative-item-dative-beneficiary` |
| requiredComplements | `case:accusative role=object required=true` |
| optionalComplements | `case:dative role=recipient required=false` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | `dla + Genitive` in this row (it is the *alternative* A2, never cumulative with the Dative); sense-2 `na + Accusative`; sense-2 `dla` allocation semantics; booking time, duration, venue, channel, price, occasion, travel context |
| relationType | `lexical-frame` |
| evidenceSource | Batch 06 §53; `WSJP-REZERW-01` |
| proposedLiveGuard | **B** `require-exact-pattern-shapes`, **C** `allow-only-preposition-case-signatures` |

| Field | Value |
|---|---|
| schemaKeyProposal | **A2** `accusative-item-dla-genitive-beneficiary` |
| requiredComplements | `case:accusative role=object required=true` |
| optionalComplements | `preposition-case:dla+genitive role=recipient required=false` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | — |
| explicitExclusions | Dative in this row; sense-2 `na + Accusative`; standalone beneficiary pattern |
| relationType | `lexical-frame` |
| evidenceSource | Batch 06 §53; `WSJP-REZERW-01` |
| proposedLiveGuard | **B**, **C** |

**Sense 2 disposition.** Setting-aside / resource-allocation receives **no
Phase 4 product meaning**. This is determined, not assumed — see §8.1.

### Order 54 — `cieszyć się` (imperfective, lexical `się`)

Source (Batch 06 §54, `WSJP-CIESZ-SIE-01` sense 1): `z KOGO/CZEGO | na CO`, a
**separate** `że ZDANIE`, and `KIM/CZYM`. The alternation bar splits row 1
into two product alternatives; three source rows therefore yield four product
alternatives. Nothing is parenthesised.

Meaning: **`experiencing-joy`** — experiencing joy, with nominal,
prepositional, and propositional cause/content alternatives (WSJP
lexical-reflexive sense 1).

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind | Semantic distinction |
|---|---|---|---|---|---|
| A1 | `z-genitive-realized-cause` | `preposition-case:z+genitive role=topic required=true` | — | — | **existing / completed** source or cause of the joy |
| A2 | `na-accusative-anticipated-occasion` | `preposition-case:na+accusative role=target required=true` | — | — | **anticipated** occasion or object (looking forward to) |
| A3 | `instrumental-nominal-cause` | `case:instrumental role=object required=true` | — | — | **nominal** cause/object of satisfaction |
| A4 | `ze-propositional-cause` | `clause:ze role=content required=true` | — | `ze` | **propositional** cause/content |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial`
— canonical lemma identity `cieszyć się`, lexical `się` is **part of the
lemma, never a complement**; `generalizedRoleStatus` — not applicable, all
four are exact concrete labels; `subjectOrParticipantRestriction` — none
recorded; `evidenceSource` — Batch 06 §54, `WSJP-CIESZ-SIE-01`;
`proposedLiveGuard` — **D**, **E**, **F**.

`explicitExclusions` (all four rows): the four alternatives are **not
cumulative** and must not be glossed as freely interchangeable; no syntax from
non-reflexive `cieszyć`; no `o + Accusative` imported from `martwić się`; no
`się`-stripped record; degree, duration, manner, time, place, and ordinary
contextual reasons remain adjuncts.

### Order 55 — `martwić się` (imperfective, lexical `się`)

Source (Batch 06 §55, `WSJP-MARTW-SIE-01`): directly gives `CZYM`,
`o KOGO/CO`, `że ZDANIE`, and `ZDANIE PYTAJNOZALEŻNE` — four listed positions,
none parenthesised, none grouped.

Meaning: **`worry-concern`** — worrying or being sustainedly concerned.
Semantically distinct from fear.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `instrumental-worry-cause` | `case:instrumental role=object required=true` | — | — |
| A2 | `o-accusative-concern-object` | `preposition-case:o+accusative role=topic required=true` | — | — |
| A3 | `ze-worry-proposition` | `clause:ze role=content required=true` | — | `ze` |
| A4 | `interrogative-worry-content` | `clause:interrogative role=content required=true` | — | `interrogative` |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
canonical identity `martwić się`, lexical `się` never a complement;
`generalizedRoleStatus` — not applicable; `subjectOrParticipantRestriction` —
none recorded; `evidenceSource` — Batch 06 §55, `WSJP-MARTW-SIE-01`;
`proposedLiveGuard` — **G**, **H**, **I**.

`explicitExclusions`: no construction borrowed from non-reflexive `martwić`;
**no construction borrowed from released `bać się`** (the `o + Accusative`
overlap is product overlap, not linguistic donation, and does not erase this
record — the human freeze retained the lemma precisely because worry semantics
plus Instrumental and clause coverage are independently verified); no
`z + Genitive` imported from `cieszyć się`; time, duration, intensity, manner,
place, contextual reasons remain adjuncts.

### Order 56 — `zgadzać się` (imperfective, lexical `się`) — HIGH RISK

Two meanings, kept completely separate. Matching/correspondence and
conflict-free-coexistence meanings are **excluded entirely**.

#### Meaning A — `consent`

Source (`WSJP-ZGADZ-SIE-01` sense 1): gives `na KOGO/CO`, `żeby ZDANIE`,
infinitive, and direct speech — four listed alternatives, none parenthesised,
**no partner position in any of them**.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `na-accusative-consented-proposal` | `preposition-case:na+accusative role=target required=true` | — | — |
| A2 | `zeby-consented-event` | `clause:zeby role=content required=true` | — | `zeby` |
| A3 | `infinitive-consented-action` | `infinitive role=content required=true` | — | — |
| A4 | `direct-speech-consent` | `clause:direct-speech role=content required=true` | — | `direct-speech` |

meaningScope: consenting to a proposal or action (WSJP sense 1).

`explicitExclusions` for meaning A: **no `z + Instrumental`** — the partner
relation belongs exclusively to meaning B and must not be invented here; no
`że` clause; conditions, degree, manner, time, place, reasons remain adjuncts.

#### Meaning B — `opinion-agreement`

Source (`WSJP-ZGADZ-SIE-02` sense 2): gives `z KIM/CZYM`, **optional**
`z KIM/CZYM` with a `że` clause, and direct speech — three listed source rows.
The optionality marker appears on exactly one of them.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| B1 | `z-instrumental-agreement-partner` | `preposition-case:z+instrumental role=interlocutor required=true` | — | — |
| B2 | `ze-agreed-proposition` | `clause:ze role=content required=true` | `preposition-case:z+instrumental role=interlocutor required=false` | `ze` |
| B3 | `direct-speech-agreement` | `clause:direct-speech role=content required=true` | **none** | `direct-speech` |

meaningScope: agreeing with a person or with an opinion/view (WSJP sense 2).

**B3 carries no partner.** The source attaches the optional `z + Instrumental`
to the `że` row only; direct speech is listed on its own. This follows the
frozen `powiedzieć` precedent exactly (its direct-speech schema is
recipientless because the exact source lists it without a recipient). No
partner is assumed. See §22 for why this is resolved rather than held.

Shared row fields (A and B): `relationType: lexical-frame`;
`requiredLexicalMaterial` — canonical identity `zgadzać się`, lexical `się`
never a complement; `generalizedRoleStatus` — not applicable;
`subjectOrParticipantRestriction` — none recorded (reciprocal readings are
sentence-level, not a complement); `evidenceSource` — Batch 06 §56,
`WSJP-ZGADZ-SIE-01`/`-02`; `proposedLiveGuard` — **J**, **K**, **L**.

`explicitExclusions` for meaning B: **no `na + Accusative`, no infinitive, no
`żeby`** imported from consent; no matching/correspondence sense;
no partner on B3.

### Order 57 — `zapraszać` (imperfective)

Source (Batch 06 §57, `WSJP-ZAPRASZ-01` sense 1): `KOGO + na CO | do CZEGO`
and **separately** `KOGO + GDZIE`. The alternation bar splits row 1 into two
product alternatives. Nothing is parenthesised.

Meaning: **`invitation`** — inviting a person to an event/activity, a
destination/institution, or another selected place (WSJP sense 1).

| Ref | schemaKeyProposal | requiredComplements | optional | Semantic role of the second position |
|---|---|---|---|---|
| A1 | `accusative-invitee-na-accusative-event` | `case:accusative role=object required=true`; `preposition-case:na+accusative role=target required=true` | — | **event / activity** |
| A2 | `accusative-invitee-do-genitive-destination` | `case:accusative role=object required=true`; `preposition-case:do+genitive role=target required=true` | — | **destination / institution** |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
none; `subjectOrParticipantRestriction` — none recorded; `evidenceSource` —
Batch 06 §57, `WSJP-ZAPRASZ-01`; `proposedLiveGuard` — **M**, **N**.

**generalizedRoleStatus.** `na + Accusative` and `do + Genitive` are **exact
concrete `Składnia` positions**, not narrowed realizations of a generalized
role: "no narrowed concrete realization label is needed for `na` or `do`"
(Batch 06 §57 and risk review). They are therefore **not** to be described as
realizations, and equally **not** as exclusive government beyond their exact
scoped roles. The separate `KOGO + GDZIE` schema is selected source evidence
that receives **no product row at all**; it stays fully unconcretized. See
§11.

`explicitExclusions`: `na` and `do` are alternatives, never simultaneous slots;
**no `w`, `u`, `na + Locative`, or any other place form may be derived from
`GDZIE`**; no standalone invitee-only pattern; time, occasion details, manner,
reason, transport, incidental location remain adjuncts.

### Order 58 — `polecać` (imperfective) — HIGH RISK

Two meanings. The instruction sense must never be glossed as ordinary
recommendation.

#### Meaning A — `directive-instruction`

Source (`WSJP-POLEC-01` sense 1, incl. `Informacja normatywna`): **optional
Dative** with infinitive, `żeby`, direct speech, **or** `CO`. The optional
Dative attaches to **all four** content alternatives. The normative note states
the Accusative position is usually a gerund/action noun.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `dative-infinitive-instruction` | `infinitive role=content required=true` | `case:dative role=recipient required=false` | — |
| A2 | `dative-zeby-instruction` | `clause:zeby role=content required=true` | `case:dative role=recipient required=false` | `zeby` |
| A3 | `dative-direct-speech-instruction` | `clause:direct-speech role=content required=true` | `case:dative role=recipient required=false` | `direct-speech` |
| A4 | `dative-accusative-action-noun` | `case:accusative role=object required=true` | `case:dative role=recipient required=false` | — |

meaningScope: directing or instructing someone to act (WSJP sense 1). The A4
Accusative is characteristically a **gerund / action noun**, per the source's
normative note — a lexical-semantic fact carried in `internalScope` and
`learnerExplanationEn`, since the locked schema has no noun-class field.

#### Meaning B — `recommendation`

Source (`WSJP-POLEC-02` sense 2): **optional** Dative recipient plus Accusative
person/item — one schema.

| Ref | schemaKeyProposal | requiredComplements | optional |
|---|---|---|---|
| B1 | `dative-accusative-recommended-item` | `case:accusative role=object required=true` | `case:dative role=recipient required=false` |

meaningScope: recommending a person or item to a potential user/customer
(WSJP sense 2).

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
none; `generalizedRoleStatus` — not applicable;
`subjectOrParticipantRestriction` — none recorded; `evidenceSource` — Batch 06
§58, `WSJP-POLEC-01`/`-02`; `proposedLiveGuard` — **O**.

`explicitExclusions`: **no infinitive, `żeby`, or direct speech in meaning B**;
the meaning-A Dative and the meaning-B Dative are separate positions and must
not be assumed to combine across senses; the A1 infinitive is **not** an
ordinary recommendation construction; reason, authority context, manner, time,
place, channel, evaluative detail remain adjuncts.

### Order 59 — `radzić` (imperfective, NON-reflexive) — HIGH RISK

Source (Batch 06 §59, `WSJP-RADZ-02` sense 2): required `KOMU + CO`; required
`KOMU` with `żeby` **or** an interrogative-dependent clause; direct speech plus
required `KOMU`; and **optional** `KOMU` with an infinitive.

Meaning: **`giving-advice`** — advising someone about how they should act
(WSJP non-reflexive sense 2).

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `dative-accusative-advice-item` | `case:dative role=recipient required=true`; `case:accusative role=object required=true` | — | — |
| A2 | `dative-zeby-advice` | `case:dative role=recipient required=true`; `clause:zeby role=content required=true` | — | `zeby` |
| A3 | `dative-interrogative-advice` | `case:dative role=recipient required=true`; `clause:interrogative role=content required=true` | — | `interrogative` |
| A4 | `dative-direct-speech-advice` | `case:dative role=recipient required=true`; `clause:direct-speech role=content required=true` | — | `direct-speech` |
| A5 | `dative-infinitive-advice` | `infinitive role=content required=true` | `case:dative role=recipient required=false` | — |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
canonical identity `radzić`, **no `sobie`**; `generalizedRoleStatus` — not
applicable; `subjectOrParticipantRestriction` — none recorded;
`evidenceSource` — Batch 06 §59, `WSJP-RADZ-02`; `proposedLiveGuard` — **P**,
**Q**.

**The requiredness asymmetry is the defining structural fact of this lemma**
and is preserved exactly: Dative `required: true` in A1–A4, `required: false`
in A5 alone. It is **not** normalized in either direction. See §10.

`explicitExclusions`: **no `z + Instrumental` coping construction** and no
other evidence from lexical `radzić sobie`; `sobie` is not attached to this
lemma in any form; the five alternatives are not a maximal template; topic,
reason, circumstances, manner, time, place, source of expertise remain
adjuncts.

### Order 60 — `pasować` (imperfective) — HIGHEST FLATTENING RISK

**Four** meanings. The repeated `do + Genitive` surface does **not** merge
them.

#### Meaning A — `appearance-harmony` (WSJP sense 1)

Source (`WSJP-PASOW-01`): exact `do KOGO/CZEGO`, **unparenthesised**.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| A1 | `do-genitive-harmony-target` | `preposition-case:do+genitive role=target required=true` | — | appearance/character **harmony or match** with the target |

meaningScope: one thing harmonizing or matching in appearance/character with
another (WSJP sense 1). `relationType: lexical-frame`.
`explicitExclusions`: **no Dative** (Dative belongs to senses 4 and 5 only);
no `na + Accusative`; no subject-experiencer wording.

#### Meaning B — `physical-fit` (WSJP sense 2)

Source (`WSJP-PASOW-02`): **optional** `do KOGO/CZEGO` **or**
`na KOGO/CO` — two alternatives, each parenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| B1 | `do-genitive-fit-target` | **none** | `preposition-case:do+genitive role=target required=false` | physical **fit by size/shape** to the target |
| B2 | `na-accusative-fitted-object` | **none** | `preposition-case:na+accusative role=target required=false` | physical fit **on** the wearer/object fitted |

meaningScope: physically fitting by size or shape (WSJP sense 2).
`relationType: lexical-frame`. Both rows are **all-optional** — see §7 rows 2
and 3. The two target forms are **alternatives, not cumulative**.
`explicitExclusions`: **no Dative**; neither complement may be promoted to
required; the two forms may not be combined into one row; harmony and
reference-target relations excluded.

#### Meaning C — `typical-appropriateness` (WSJP sense 4)

Source (`WSJP-PASOW-04`): **optional** `KOMU` plus `do KOGO/CZEGO`; only
`KOMU` is parenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| C1 | `dative-evaluator-do-genitive-reference` | `preposition-case:do+genitive role=target required=true` | `case:dative role=experiencer required=false` | being **typical of / appropriate to** a person or thing, as judged by the optional evaluator |

meaningScope: being typical of or appropriate for a person/thing (WSJP sense
4). `relationType: lexical-frame` — precedent: canonical `zależeć`
(`dative-experiencer-na-locative`) also carries a Dative `experiencer` under
`lexical-frame`, so role `experiencer` does **not** imply the
`subject-experiencer` relation type.
`explicitExclusions`: this Dative is **not** the sense-5 experiencer and
carries no subject-experiencer wording; `na + Accusative` excluded; the
`do + Genitive` here is a **reference target**, not the sense-1 harmony target
and not the sense-2 fit target.

#### Meaning D — `expectation-suitability` (WSJP sense 5)

Source (`WSJP-PASOW-05`): **optional** `KOMU/CZEMU` — the only listed position.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| D1 | `dative-expectation-holder` | **none** | `case:dative role=experiencer required=false` | **satisfying the expectations / suiting** the expectation holder |

meaningScope: being suitable for, or satisfying the expectations of, someone
(WSJP sense 5). **All-optional** — see §7 row 4.
`relationType: lexical-frame` — **flagged representation decision, see §5.9
and §19.**
`explicitExclusions`: no `do + Genitive`, no `na + Accusative`; no harmony,
fit, or reference-target relation.

Shared `pasować` fields: `requiredLexicalMaterial` — none;
`generalizedRoleStatus` — not applicable, every position is an exact concrete
label; `subjectOrParticipantRestriction` — the subject–experiencer
characterization belongs to **meaning D only** and is carried in D's
`internalScope`/`learnerExplanationEn`; `evidenceSource` — Batch 06 §60,
`WSJP-PASOW-01/-02/-04/-05`; `proposedLiveGuard` — **R**, **S**.

### Order 61 — `móc` (imperfective)

Source (Batch 07 §61): `WSJP-MOC-01` sense 1, `WSJP-MOC-02` sense 2, and
`WSJP-MOC-04` sense 4 each list an exact infinitive in `Składnia`.

| Ref | Meaning | meaningScope | schemaKeyProposal | requiredComplements |
|---|---|---|---|---|
| A1 | `ability-possibility` | Objective possibility or ability to do something (WSJP sense 1). | `infinitive-possible-action` | `infinitive role=content required=true` |
| B1 | `permission` | Absence of prohibition / having permission to do something (WSJP sense 2). Also owns the request/help question use (`Czy mogę…?`) as **sentence-level interrogative and pragmatic packaging** over this same infinitive frame — carried as usage guidance, never as a complement. | `infinitive-permitted-action` | `infinitive role=content required=true` |

Shared fields: `relationType: lexical-frame`; `optionalComplements` — none;
`clauseKind` — **none, deliberately**; `requiredLexicalMaterial` — none;
`generalizedRoleStatus` — not applicable;
`subjectOrParticipantRestriction` — none as a complement (person choice and
politeness are pragmatics); `evidenceSource` — Batch 07 §61, `WSJP-MOC-01`,
`WSJP-MOC-02`, `WSJP-MOC-04`; `proposedLiveGuard` — **T**, **U**.

`explicitExclusions`: **no `czy` clause complement, no question complement, no
new architecture type** — under any circumstances; probability sense 3, idioms,
and unrelated uses are not imported; time, reason, means, conditions,
circumstances remain contextual.

Sense-4 disposition is determined from frozen evidence, not chosen for count
convenience — see §8.5.

## 4.1 Source-row → product-row reconciliation (high-risk lemmas)

### `zgadzać się` (order 56)

| # | Exact source row | Product rows | Why |
|---:|---|---|---|
| 1 | sense 1 `na KOGO/CO` | A1 | one position, required |
| 2 | sense 1 `żeby ZDANIE` | A2 | separate listed alternative |
| 3 | sense 1 infinitive | A3 | separate listed alternative |
| 4 | sense 1 direct speech | A4 | separate listed alternative |
| 5 | sense 2 `z KIM/CZYM` | B1 | standalone partner row; `z` required (unparenthesised) |
| 6 | sense 2 optional `z KIM/CZYM` + `że ZDANIE` | B2 | one row: required content clause + **optional** partner |
| 7 | sense 2 direct speech | B3 | listed alone; **no partner attached** |

**7 source rows → 7 product rows.** No compression, no expansion. `z +
Instrumental` appears with **two different requiredness values** (B1 required,
B2 optional); these are two distinct complement signatures and both must be
listed in guard L.

### `polecać` (order 58)

| # | Exact source row | Product rows | Why |
|---:|---|---|---|
| 1 | sense 1 optional `KOMU` + infinitive | A1 | optional Dative distributes over each content alternative |
| 2 | sense 1 optional `KOMU` + `żeby` | A2 | " |
| 3 | sense 1 optional `KOMU` + direct speech | A3 | " — note this **differs from `powiedzieć`**, whose direct speech is recipientless; the difference is preserved, not smoothed |
| 4 | sense 1 optional `KOMU` + `CO` (usually gerund) | A4 | " |
| 5 | sense 2 optional `KOMU` + Accusative person/item | B1 | separate meaning, one row |

**Source lists a single sense-1 group with four content alternatives → 4
product rows; plus 1 sense-2 row = 5.** The optional Dative is *not* given a
standalone row (global rule C).

### `radzić` (order 59)

| # | Exact source row | Product rows | Dative |
|---:|---|---|---|
| 1 | required `KOMU + CO` | A1 | **required** |
| 2 | required `KOMU` + (`żeby` \| interrogative-dependent) | A2, A3 | **required** (alternation bar → two rows) |
| 3 | direct speech + required `KOMU` | A4 | **required** |
| 4 | optional `KOMU` + infinitive | A5 | **optional** |

**4 source rows → 5 product rows**, the expansion coming solely from the
explicit `żeby | interrogative` alternation. This is the one place in Batch 6
where source-row count and product-row count legitimately differ, and the
reason is an explicit alternation, not a reconstruction.

### `pasować` (order 60)

| # | Exact source row | Product row | Requiredness |
|---:|---|---|---|
| 1 | sense 1 `do KOGO/CZEGO` | A1 | `do` **required** |
| 2 | sense 2 optional `do KOGO/CZEGO` \| `na KOGO/CO` | B1, B2 | both **optional** (alternation bar → two rows) |
| 3 | sense 4 optional `KOMU` + `do KOGO/CZEGO` | C1 | `do` **required**, Dative **optional** |
| 4 | sense 5 optional `KOMU/CZEMU` | D1 | Dative **optional** |

**4 source rows → 5 product rows**, again solely from an explicit alternation.
`do + Genitive` occurs in three meanings with two distinct requiredness values
and three distinct semantic relations; a lemma-wide preposition allowlist
cannot place them — guard S (meaning-scoped exact shapes) supplies ownership.

### `móc` (order 61)

| # | Exact source row | Product row | Note |
|---:|---|---|---|
| 1 | sense 1 `BEZOKOLICZNIK` | A1 | ability / objective possibility |
| 2 | sense 2 `BEZOKOLICZNIK` | B1 | permission / absence of prohibition |
| 3 | sense 4 `BEZOKOLICZNIK` (question use) | **none — folded into B1 as usage** | The frozen evidence states `Czy mogę…?` is "interrogative and pragmatic packaging **over the permission infinitive**" and "establishes no new locked-model construction". Ownership is stated explicitly, so no separate row and no separate meaning is created. |

**3 source rows → 2 product rows**, the compression being an explicit frozen
finding rather than an editorial judgment. See §8.5.

## 5. Per-lemma rationale

**5.1 `gotować`.** Freeze constraint: "Later authoring should keep optionality
explicit and avoid extending the schema to every food-process sense." Both
source positions are parenthesised in a single schema, so the faithful product
shape is one pattern with two optional complements and **no required anchor**.
Neither is promoted. The Dative is credited because `KOMU` is in the exact
`Składnia`, not because meals are typically cooked for people; `dla + Genitive`
appears only outside the exact schema and is excluded.

**5.2 `rezerwować`.** Freeze constraint: "Later authoring must distinguish
Dative from `dla + Genitive` alternatives and keep booking separate from
resource/time allocation." Two source schemas → two product alternatives, each
anchored by the required Accusative. Dative and `dla` are never cumulative and
never standalone.

**5.3 `cieszyć się`.** Freeze constraint: "Later authoring must distinguish the
semantic contribution of `z`, `na`, Instrumental, and the proposition rather
than presenting interchangeable labels." The four alternatives are therefore
given four distinct semantic descriptions (realized cause / anticipated
occasion / nominal cause / propositional cause) reflected in the four
candidate pattern keys, so that the distinction survives into the product
without relying on prose alone.

**5.4 `martwić się`.** Freeze rationale: "distinct worry semantics and
independently verified Instrumental/clause coverage justify retention
alongside released `bać się`." The `o + Accusative` overlap is a *product*
overlap already adjudicated by the human freeze; it neither removes the row
nor licenses importing anything from `bać się`.

**5.5 `zgadzać się`.** Freeze constraint: "Later authoring must label consent
versus opinion agreement and keep matching/correspondence outside these
records." Two meanings, seven alternatives, zero cross-sense transfer. The
consent inventory (`na`, `żeby`, infinitive, direct speech) and the agreement
inventory (`z`, `że`+optional `z`, direct speech) are disjoint apart from both
having a direct-speech row, and even there the two rows differ in nothing
structurally — which is why meaning ownership must come from guard K, not from
signature exclusion.

**5.6 `zapraszać`.** Freeze constraint: "Later authoring must keep
event/activity and destination/institution readings distinct and avoid
concretizing the `GDZIE` alternative." Both are honored: two rows with
distinct semantic descriptions, and the `GDZIE` schema left entirely
unauthored.

**5.7 `polecać`.** Freeze constraint: "Later authoring must not gloss the
sense-1 infinitive as ordinary recommendation; it is directive/instructional
in the exact source." The two meanings are given non-overlapping content
inventories; only the optional Dative shape recurs, and it belongs
independently to each sense.

**5.8 `radzić`.** Freeze constraint: "Later authoring must encode the Dative
required/optional distinction across schemas and keep advice separate from
coping." Both are the load-bearing facts of this lemma and are encoded
structurally (per-row `required` flags) rather than in prose.

**5.9 `pasować`.** Freeze constraint: "Later product authoring must choose
sense-specific role wording; the locked model can encode the forms but generic
'fits' wording would obscure the relations." Four meanings are preserved with
four distinct relation descriptions.

**Flagged representation decision (meaning D, `relationType`).** Phase 3
states sense 5 "is suitable for a subject–experiencer treatment". The locked
validator (`validate_priority8_staging.py:631`) requires **both** a `subject`
and an `experiencer` role before `relationType: subject-experiencer` is legal,
and (`:465`) permits a direct Nominative only under that or
`constructional-frame`. A read-only in-memory probe against the live validator
confirmed this: `subject-experiencer` with only an optional Dative experiencer
produces
`complements: subject-experiencer requires subject and experiencer roles`,
while the same shape under `lexical-frame` produces no shape issue at all
(§18.1). Encoding meaning D as `subject-experiencer` would therefore require
inventing a required Nominative `subject` complement that the exact
`WSJP-PASOW-05` `Składnia` does not list — prohibited by the Phase 4B rule that
only exact source positions become complements — and would also destroy the
all-optional shape the source actually gives.

The resolution is therefore determined, not guessed: meaning D is authored as
`lexical-frame` with the single optional Dative `experiencer`, and the
subject–experiencer *characterization* is carried in `internalScope` and
`learnerExplanationEn`, exactly where the freeze constraint puts the
"sense-specific role wording". The canonical corpus supplies the decisive
precedent that this is a legitimate pairing: `zależeć` carries
`case:dative role=experiencer` under `lexical-frame`, while `podobać się` uses
`subject-experiencer` **only because** its own source frame contains a
Nominative subject. Whether canonical promotion should later restore
`relationType: subject-experiencer` (with a Nominative subject supplied
constructionally, `podobać się`-style) is recorded as a Phase 4C
reconciliation item in §19 — it is not silently dropped, and it is not a
Phase 4B evidence gap.

**5.10 `móc`.** Freeze constraint: "Later authoring must label modal meaning
where useful and keep the permission question as sentence-level packaging over
the infinitive frame." Two meanings with one identical infinitive shape each.
The identical shape is not a reason to merge them — ability and permission are
semantically distinct in the frozen evidence — and is also not structurally
enforceable, exactly as for `robić` in Batch 5 (§14, limitation 1).

## 6. Requiredness / optionality audit

Every multi-complement product row, with each complement's requiredness and
its exact source warrant:

| Row | Complements | Source warrant |
|---|---|---|
| `gotować` A1 | accusative **optional**, dative **optional** | `(CO) + (KOMU)` — both parenthesised |
| `rezerwować` A1 | accusative **required**, dative **optional** | `CO + (KOMU)` |
| `rezerwować` A2 | accusative **required**, `dla`+genitive **optional** | `CO + (dla KOGO)` |
| `zgadzać się` B2 | `ze` clause **required**, `z`+instrumental **optional** | "optional `z KIM/CZYM` with a `że` clause" |
| `zapraszać` A1 | accusative **required**, `na`+accusative **required** | `KOGO + na CO` — neither parenthesised |
| `zapraszać` A2 | accusative **required**, `do`+genitive **required** | `KOGO + do CZEGO` |
| `polecać` A1 | infinitive **required**, dative **optional** | "optional Dative with infinitive" |
| `polecać` A2 | `zeby` clause **required**, dative **optional** | "…with … `żeby`" |
| `polecać` A3 | `direct-speech` clause **required**, dative **optional** | "…with … direct speech" |
| `polecać` A4 | accusative **required**, dative **optional** | "…with … `CO`" |
| `polecać` B1 | accusative **required**, dative **optional** | "optional Dative plus Accusative person/item" |
| `radzić` A1 | dative **required**, accusative **required** | "required `KOMU + CO`" |
| `radzić` A2 | dative **required**, `zeby` clause **required** | "required `KOMU` with `żeby`" |
| `radzić` A3 | dative **required**, `interrogative` clause **required** | "required `KOMU` with … an interrogative-dependent clause" |
| `radzić` A4 | dative **required**, `direct-speech` clause **required** | "direct speech plus required `KOMU`" |
| `radzić` A5 | infinitive **required**, dative **optional** | "optional `KOMU` with an infinitive" |
| `pasować` C1 | `do`+genitive **required**, dative **optional** | "optional `KOMU` plus `do KOGO/CZEGO`" |

**17 multi-complement rows.** The remaining **20** rows are single-complement:
`cieszyć się` 4, `martwić się` 4, `zgadzać się` A1–A4 + B1 + B3 = 6,
`pasować` A1 + B1 + B2 + D1 = 4, `móc` 2. 17 + 20 = **37**.

No complement anywhere was promoted from optional to required, and none was
demoted. Every requiredness value traces to an explicit parenthesisation (or
its absence) in the quoted `Składnia` notation.

## 7. All-optional pattern audit

Four proposed rows have **zero required complements**. Per the binding Phase
4B5 precedent (§15 of the Batch 5 matrix, HOLD-1A adjudication), a product
pattern **may** have a non-empty complement array in which every complement is
`required: false`; this is already live in staging
(`umówić się` / `z-instrumental-partner-na-accusative-event`, the only such
pattern among the current 164). None of these rows is placed on HOLD for being
all-optional.

| # | Row | Complements (all optional) | Array non-empty? | Source optionality | Promotion? | Standalone-participant error? |
|---:|---|---|---|---|---|---|
| 1 | `gotować` A1 | accusative object; dative recipient | **yes**, 2 | `(CO) + (KOMU)` — both parenthesised in **one** schema | none — forcing either to required would contradict the source | no — both participants stay **inside** their single source-owned schema; neither is given a standalone row |
| 2 | `pasować` B1 | `do`+genitive target | **yes**, 1 | sense 2 "optional `do KOGO/CZEGO`" | none | no — this *is* the source alternative, not an extracted participant |
| 3 | `pasować` B2 | `na`+accusative target | **yes**, 1 | sense 2 "…or `na KOGO/CO`" (same parenthesised group) | none | no — B1/B2 are the two members of an explicit alternation, not one row split |
| 4 | `pasować` D1 | dative experiencer | **yes**, 1 | sense 5 "optional `KOMU/CZEMU`" — the **only** listed position | none — the brief and the source both forbid forcing it | no — it is the sense's entire complement inventory |

**Structural validation.** A read-only, in-memory probe against the current
locked `validate_priority8_staging.py` (no repository file written; staging
SHA-256 identical before and after) confirmed that a **single**-complement
all-optional pattern validates: shapes 1 and 2 in §18.1 returned only the
unrelated `future-batch lemma must remain empty` boundary issue, byte-identical
to the required-complement control (shape 5). The Batch 5 adjudication proved
the two-complement case; this extends the same proof to the one-complement
case, which Batch 5 did not exercise.

**Guard consequence.** `require-exact-pattern-shapes` compares exact complement
objects including `required`, so guards A and R pin these rows' optionality
structurally: promoting `gotować`'s Accusative or `pasować` D1's Dative to
required would break multiset equality and fail.

## 8. Sense-separation audit

**8.1 `rezerwować` — one meaning, sense 2 excluded.** Determined, not assumed.
Batch 06 §53: "Sense researched. WSJP sense 1 … Separate sense 2 was inspected
**only as a contrast boundary**." CSV `verified_meaning_summary` names sense 1
alone; `secondary_source_locator` reads "sense 2; … **contrast boundary**";
`research_notes`: "The separate setting-aside source is used **only to enforce
the meaning boundary**." The Phase 3 scoped meaning is therefore sense 1 only,
and sense 2 receives **no Phase 4 product meaning**. Its `dla` and `na`
relations are excluded from the booking meaning; the freeze constraint "keep
booking separate from resource/time allocation" is satisfied by exclusion, not
by authoring a second meaning. No repository text contradicts this reading, so
no HOLD arises.

**8.2 `zgadzać się` — two meanings.** `consent` (sense 1) and
`opinion-agreement` (sense 2) never share a complement inventory. `na`,
infinitive, and `żeby` are consent-only; `z + Instrumental` is
agreement-only. Matching/correspondence and conflict-free coexistence receive
no meaning at all.

**8.3 `polecać` — two meanings.** `directive-instruction` (sense 1) and
`recommendation` (sense 2). The infinitive, `żeby`, and direct-speech
alternatives are instruction-only. Both senses independently carry an optional
Dative; that recurrence is independently sourced convergence, not a shared
slot, and the two Datives are never assumed to combine.

**8.4 `pasować` — four meanings.** `appearance-harmony`, `physical-fit`,
`typical-appropriateness`, `expectation-suitability`. `do + Genitive` recurs in
three of them with three different relations and two different requiredness
values; the Dative recurs in two of them with two different roles (evaluator
vs. expectation holder). No merger. A single generic "fit" meaning is
explicitly rejected.

**8.5 `móc` — two meanings, sense 4 folded into permission.** Determined from
frozen evidence, not chosen to inflate or reduce a count. Three independent
frozen statements assign ownership:

- Batch 07 §61: "`Czy mogę…?` is interrogative and pragmatic packaging **over
  the permission infinitive**; it is not a distinct lexical question
  complement."
- Batch 07 CSV order 61: "question-use sense 4 kept as **pragmatic packaging
  rather than a new complement**"; research notes: sense 4 "again lists an
  infinitive and **establishes no new locked-model construction**."
- Phase 3B freeze `authoring_constraint` for order 61: "keep the permission
  question as **sentence-level packaging over the infinitive frame**."

The evidence names the *permission* frame as the owner, so sense 4 becomes
usage/pragmatic guidance under meaning `permission` and receives no separate
product meaning and no product row. Ability and permission remain two distinct
meanings because the frozen evidence treats them as semantically distinct
senses with independent exact infinitive selection. Under no circumstances is
a question-complement pattern created; see guard U.

## 9. Lexical-identity audit

| Lemma | Canonical identity | Lexical material | Treatment |
|---|---|---|---|
| `cieszyć się` | `cieszyć się` | `się` | Part of the canonical lemma identity. **Never** a complement, never a `requiredLexicalItems` entry. No syntax from non-reflexive `cieszyć`. Guard D. |
| `martwić się` | `martwić się` | `się` | Same. No syntax from non-reflexive `martwić`, and none from `bać się`. Guard G. |
| `zgadzać się` | `zgadzać się` | `się` | Same. Guard J. |
| `radzić` | `radzić` | **none** | Strictly independent from `radzić sobie` (order 29, already authored). No `sobie`; no `z + Instrumental` coping frame; no evidence, role, or complement transferred in either direction. Guards P, Q. |
| `radzić sobie` | `radzić sobie` | `sobie` | Untouched by Batch 6; already protected by the live rule `p8-4b-radzic-sobie-lexical-identity`. |

**Structural note.** The locked validator already makes `sobie` unattachable to
`radzić`: `requiredLexicalItems` is permitted **only** on `brać` and `wziąć`
and must equal `["udział"]` (`validate_priority8_staging.py:919,979–985`). The
`radzić`/`radzić sobie` separation therefore rests on (a) that hard validator
rule, (b) two distinct canonical lemma identities in the frozen 68, (c)
proposed guard Q forbidding `z + Instrumental` on `radzić`, and (d) proposed
guard P pinning `radzić`'s exact five shapes.

## 10. Clause normalization audit

Clause kinds are kept exactly as the source distinguishes them. The locked
private clause-kind vocabulary is `ze`, `czy`, `zeby`, `interrogative`,
`direct-speech`.

| Lemma | `ze` | `zeby` | `interrogative` | `direct-speech` | `czy` |
|---|---|---|---|---|---|
| `cieszyć się` | A4 | — | — | — | — |
| `martwić się` | A3 | — | A4 | — | — |
| `zgadzać się` consent | — | A2 | — | A4 | — |
| `zgadzać się` agreement | B2 | — | — | B3 | — |
| `polecać` instruction | — | A2 | — | A3 | — |
| `radzić` | — | A2 | A3 | A4 | — |
| `móc` | — | — | — | — | **forbidden** |

`ze` and `zeby` are never merged. `interrogative` (interrogative-dependent
content) is never merged into `ze` or `czy`. Direct speech is represented
**only** as `{"type": "clause", "clauseKind": "direct-speech"}`, per the B1A
lock, and is never given a participant the exact source does not list
(`zgadzać się` B3 is partnerless; `polecać` A3 and `radzić` A4 carry the
Dative because their own source rows do). `czy` appears nowhere in Batch 6 and
is affirmatively forbidden on `móc`.

## 11. Generalized-role audit

`DOKĄD`, `SKĄD`, `GDZIE`, and `KTÓRĘDY` are not complement types and are not
concretized anywhere in Batch 6.

**Batch 6 requires no narrowed concrete realization at all.** The Phase 3 risk
review states this explicitly: "Batch 6 needs no narrowed concrete
realization."

| Lemma | Generalized role in evidence | Product treatment |
|---|---|---|
| `zapraszać` | separate schema `KOGO + GDZIE` | **No product row.** The schema is recorded as selected source evidence that the locked four-type model does not concretize. `na + Accusative` and `do + Genitive` come from the *other* source schema, where they are **exact** — they are not realizations of `GDZIE` and must not be labelled as such, nor as exclusive government beyond their exact scoped roles. Guard N pins the two authorized preposition-case signatures so no `w`, `u`, `na + Locative`, or other place form can later be introduced as a `GDZIE` concretization. |
| all others | none listed | not applicable |

This mirrors the frozen treatment of `czytać`'s deliberately unauthored
`GDZIE` and `umówić się`'s deliberately unauthored `KIEDY`: a selected source
position that the locked model cannot represent is documented, not silently
dropped and not invented.

## 12. Cross-lemma independence audit

| Risk | Decision | Enforcement |
|---|---|---|
| **A. `gotować` / `rezerwować` beneficiaries** | **NOT normalized.** `gotować` has an optional Dative **only** (one schema, no `dla`). `rezerwować` has an optional Dative **or** an alternative optional `dla + Genitive` (two schemas). The systems are deliberately asymmetric. | Guards A, B, C. Guard C's allowlist contains `dla+genitive` for `rezerwować`; `gotować` has **no** preposition-case complement at all, so guard A's exact shapes reject any `dla` addition. |
| **B. `cieszyć się` / `martwić się` emotional reflexives** | **NOT normalized.** Lexical `się` preserved independently on each. Their cause inventories are disjoint: `z + Genitive`, `na + Accusative`, Instrumental, `że` versus Instrumental, `o + Accusative`, `że`, interrogative. Only the Instrumental and `że` shapes coincide, and each is independently sourced. No generic "emotion frame" is created. | Guards D, E, F, G, H, I. Guards F and I are disjoint allowlists (`z`/`na` vs. `o`), so neither lemma can acquire the other's preposition. |
| **C. `zgadzać się` / `polecać` / `radzić` communicative semantics** | **NO TRANSFER.** Similar communicative semantics do not license schema transfer. Each inventory is derived solely from its own `Składnia`. Notably `radzić` requires its Dative in four of five rows while `polecać` never requires its Dative — the asymmetry is preserved, not smoothed; and `zgadzać się` has no Dative at all. | Guards K, O, P. |
| **D. `radzić` / `radzić sobie`** | **STRICT SEPARATION.** See §9. | Validator `requiredLexicalItems` rule; guards P, Q; existing `p8-4b-radzic-sobie-lexical-identity`. |
| **E. `pasować` internal flattening** | **NOT flattened.** Four meanings retained despite `do + Genitive` recurring in three of them. | Guard R (meaning-scoped exact shapes) supplies **meaning ownership**; guard S (lemma-wide allowlist) supplies **signature exclusion** only. |
| **F. `móc` question packaging** | **Sentence grammar / pragmatics.** No question complement, no `czy` clause, no new type. | Guards T, U. |
| **G. `powiedzieć` (Batch 5) / `polecać` direct speech** | **Difference preserved.** `powiedzieć`'s direct speech is recipientless; `polecać`'s carries an optional Dative. Each follows its own source row. No harmonization. | Guards O and the frozen Batch 5 guard K. |
| **H. `zapraszać` / motion lemmas (`iść`, `chodzić`, `przyjść`, …)** | **NO TRANSFER.** `zapraszać`'s `na`/`do` are exact invitation positions, not destination realizations borrowed from the motion family. | Guard N. |
| **I. `rezerwować` / `zarezerwować`** | **No transfer.** The perfective partner is not among the 68 and receives nothing; aspect metadata never transfers syntax. | Frozen 68 intake boundary. |

## 13. Explicit exclusions (consolidated)

| Lemma | Excluded |
|---|---|
| `gotować` | `dla + Genitive`; required Accusative; required Dative; split beneficiary row; inchoative food-cooking and all other senses; kitchen/home place, time, frequency, manner, tools, ingredients, purpose |
| `rezerwować` | Dative + `dla` in one pattern; standalone beneficiary row; sense-2 `na + Accusative`; sense-2 `dla` allocation semantics; any setting-aside meaning; booking time, duration, venue, channel, price, occasion, travel context |
| `cieszyć się` | cumulative merger of the four alternatives; "interchangeable" glossing; non-reflexive `cieszyć` syntax; `o + Accusative`; `się`-stripped identity; degree, duration, manner, time, place, contextual reason |
| `martwić się` | `martwić` syntax; `bać się` syntax; `z + Genitive`; `się`-stripped identity; time, duration, intensity, manner, place, contextual reasons |
| `zgadzać się` | consent↔agreement transfer in either direction (`na`/infinitive/`żeby` into agreement; `z + Instrumental` into consent); partner on the agreement direct-speech row; matching/correspondence and conflict-free-coexistence meanings; `się`-stripped identity; conditions, degree, manner, time, place, reasons |
| `zapraszać` | `na` + `do` in one cumulative pattern; standalone invitee row; **any concrete place form derived from `GDZIE`** (`w`, `u`, `na + Locative`, …); "exclusive government" labelling; "narrowed realization" labelling of `na`/`do`; time, occasion detail, manner, reason, transport, incidental location |
| `polecać` | infinitive/`żeby`/direct speech in the recommendation meaning; cross-sense Dative combination; required Dative anywhere; standalone Dative row; "ordinary recommendation" glossing of the sense-1 infinitive; reason, authority context, manner, time, place, channel, evaluative detail |
| `radzić` | `z + Instrumental` coping frame; `sobie` in any form; any evidence from `radzić sobie`; normalization of the Dative requiredness asymmetry; maximal template merging the five alternatives; topic, reason, circumstances, manner, time, place, expertise source |
| `pasować` | one generic "fit" meaning; Dative in meanings A or B; `do`/`na` in meaning D; subject-experiencer wording on meanings A, B, C; promotion of any optional complement; combining B1 and B2; degree, style, occasion, time, place, manner, contextual comparison |
| `móc` | **`czy` clause complement**; any question complement; any new architecture type; merging ability and permission; a third meaning for sense 4; probability sense 3; idioms; time, reason, means, conditions, circumstances, person choice, politeness as complements |

## 14. Proposed live guards (NOT implemented in this task)

`tests/fixtures/priority8_phase4b_authoring_rules.json` is **unchanged** by
this task and remains byte-identical at
`4cd62f335c8af96f655de49d6f1ed58acd8dba8a3f4eddb461c1c3b7dc6c8f2f`.
Presence-asserting rules must land in the same commit as the
`candidateContent` they protect, per the test-lifecycle rule. All proposals
below use **existing** primitives; no new primitive is required and the guard
interpreter is not modified.

| Ref | Proposed rule ID | Target | Primitive | Purpose |
|---|---|---|---|---|
| A | `p8-4b-gotowac-exact-pattern-shapes` | `gotować` | `require-exact-pattern-shapes` | One meaning, one shape, **both complements `required: false`**. Structurally blocks promoting either to required, splitting the beneficiary into a standalone row, adding `dla + Genitive`, and adding a second meaning. |
| B | `p8-4b-rezerwowac-exact-pattern-shapes` | `rezerwować` | `require-exact-pattern-shapes` | One meaning, exactly two shapes. Blocks Dative + `dla` co-occurrence, a standalone beneficiary row, a required beneficiary, and a second (allocation) meaning. |
| C | `p8-4b-rezerwowac-authorized-preposition-cases` | `rezerwować` | `allow-only-preposition-case-signatures` | Allowlist exactly `dla+genitive role=recipient required=false`. Blocks importing sense-2 `na + Accusative` or any other preposition. |
| D | `p8-4b-cieszyc-sie-lexical-identity` | `cieszyć się` (order 54) | `require-lexical-identity` | `lexicalItems: ["się"]` against the canonical identity. |
| E | `p8-4b-cieszyc-sie-exact-pattern-shapes` | `cieszyć się` | `require-exact-pattern-shapes` | One meaning, exactly four single-complement shapes. Blocks any cumulative merger and any fifth alternative. |
| F | `p8-4b-cieszyc-sie-authorized-preposition-cases` | `cieszyć się` | `allow-only-preposition-case-signatures` | Allowlist exactly `z+genitive role=topic required=true` and `na+accusative role=target required=true`. Blocks acquiring `o + Accusative` from `martwić się` or any other preposition. |
| G | `p8-4b-martwic-sie-lexical-identity` | `martwić się` (order 55) | `require-lexical-identity` | `lexicalItems: ["się"]`. |
| H | `p8-4b-martwic-sie-exact-pattern-shapes` | `martwić się` | `require-exact-pattern-shapes` | One meaning, exactly four single-complement shapes. |
| I | `p8-4b-martwic-sie-authorized-preposition-cases` | `martwić się` | `allow-only-preposition-case-signatures` | Allowlist exactly `o+accusative role=topic required=true`. Blocks acquiring `z + Genitive` from `cieszyć się` and any `bać się`-shaped addition. |
| J | `p8-4b-zgadzac-sie-lexical-identity` | `zgadzać się` (order 56) | `require-lexical-identity` | `lexicalItems: ["się"]`. |
| K | `p8-4b-zgadzac-sie-exact-pattern-shapes` | `zgadzać się` | `require-exact-pattern-shapes` | `exactMeaningSet: true`; consent = 4 declared shapes, opinion-agreement = 3. **This is the meaning-ownership control**: it blocks `na`/infinitive/`żeby` appearing under agreement, `z + Instrumental` appearing under consent, and a partner being attached to the agreement direct-speech row. |
| L | `p8-4b-zgadzac-sie-authorized-preposition-cases` | `zgadzać się` | `allow-only-preposition-case-signatures` | Allowlist exactly **three** signatures: `na+accusative role=target required=true`; `z+instrumental role=interlocutor required=true` (B1); `z+instrumental role=interlocutor required=false` (B2). Signature exclusion only — it cannot place a signature in the right meaning. |
| M | `p8-4b-zapraszac-exact-pattern-shapes` | `zapraszać` | `require-exact-pattern-shapes` | One meaning, exactly two two-complement shapes. Blocks a cumulative `na` + `do` pattern, a standalone invitee row, a standalone place row, and any optionalization of the invitee. |
| N | `p8-4b-zapraszac-authorized-preposition-cases` | `zapraszać` | `allow-only-preposition-case-signatures` | Allowlist exactly `na+accusative role=target required=true` and `do+genitive role=target required=true`. **This is the anti-concretization control for the separate `GDZIE` schema**: no `w`, `u`, `na + Locative`, or other place preposition can ever be introduced. |
| O | `p8-4b-polecac-exact-pattern-shapes` | `polecać` | `require-exact-pattern-shapes` | `exactMeaningSet: true`; instruction = 4 shapes each with the optional Dative, recommendation = 1. Blocks importing infinitive/clause content into recommendation, promoting any Dative to required, creating a standalone Dative row, and merging the two meanings. |
| P | `p8-4b-radzic-exact-pattern-shapes` | `radzić` | `require-exact-pattern-shapes` | One meaning, exactly five shapes, **pinning the Dative requiredness asymmetry structurally**: `required: true` in the nominal, `żeby`, interrogative, and direct-speech shapes; `required: false` in the infinitive shape. Any normalization in either direction breaks multiset equality. |
| Q | `p8-4b-radzic-no-z-instrumental-coping` | `radzić` | `forbid-complement-match` | Signature `{type: preposition-case, preposition: z, case: instrumental}`. Directly blocks the `radzić sobie` coping construction from ever appearing on non-reflexive `radzić`. (An empty preposition allowlist is not legal — `allowedSignatures` requires at least one entry — so a forbid rule is the correct primitive for a lemma that legitimately has **no** preposition-case complement.) |
| R | `p8-4b-pasowac-exact-pattern-shapes` | `pasować` | `require-exact-pattern-shapes` | `exactMeaningSet: true`; four meanings with 1 / 2 / 1 / 1 shapes. **Meaning-scoped by construction**, which is the only way to place `do+genitive role=target required=true` (harmony) versus `do+genitive role=target required=false` (fit) versus `do+genitive role=target required=true` + optional Dative (reference) into their correct owners. Also pins the three all-optional shapes against promotion. |
| S | `p8-4b-pasowac-authorized-preposition-cases` | `pasować` | `allow-only-preposition-case-signatures` | Allowlist exactly three signatures: `do+genitive role=target required=true`; `do+genitive role=target required=false`; `na+accusative role=target required=false`. **Signature exclusion only.** |
| T | `p8-4b-moc-exact-pattern-shapes` | `móc` | `require-exact-pattern-shapes` | `exactMeaningSet: true`; two meanings, one infinitive shape each. Because multiset equality is exact, this also structurally prevents **any** additional complement — including a `czy` clause — from being added to either meaning. |
| U | `p8-4b-moc-no-question-clause` | `móc` | `forbid-complement-match` | Signature `{type: clause, clauseKind: czy}`. Explicit, legible protection of the packaging boundary, independent of T, so the "no question complement" rule survives even if the shape set is later legitimately revised. |

### 14.1 Guard-engine notes and the carried-forward Batch 5 M/N lesson

**Every `allow-only-…` allowlist must list every distinct signature with its
exact `required` flag**, because the interpreter tests
`complement == signature` — exact object equality — so `required` and `role`
are part of signature identity. This is why guard L needs **three** entries
(the same `z + Instrumental` appears once required and once optional) and
guard S needs **three** (the same `do + Genitive` appears once required and
once optional). This is the correction adjudicated for `czytać` in Phase 4B4-A
and re-applied for `umówić się` in Phase 4B5; it applies identically here.

**A lemma-wide preposition allowlist is NOT sufficient meaning-placement
protection.** Carried forward from the Batch 5 M/N lesson:

- `require-exact-pattern-shapes` supplies **meaning ownership** — it is the
  only primitive that knows which meaning a shape belongs to;
- `allow-only-preposition-case-signatures` supplies **signature exclusion** —
  it knows only what may appear *somewhere* in the lemma.

For `pasować` this is decisive: guard R alone would happily accept
`do+genitive role=target required=false` sitting under the *harmony* meaning,
because that signature is on the lemma-wide allowlist. Only guard R rejects it.
Guard S is therefore proposed as a companion to R, never as a substitute.

### 14.2 Semantic facts guards cannot enforce

Stated explicitly rather than papered over:

1. **`móc`'s ability/permission split is not structurally enforceable.** Both
   meanings have the identical shape `{infinitive role=content required=true}`.
   `exactMeaningSet: true` pins the meaning-key inventory and cardinality but
   cannot verify that the right semantics sits under each key. This is exactly
   the frozen `robić` limitation from Batch 5. Control falls to
   `internalScope`, `glossesEn`, `learnerExplanationEn`, the example, and
   independent review.
2. **`móc`'s request/help question packaging is not structurally
   representable.** That `Czy mogę…?` belongs to the permission meaning as
   pragmatic packaging is a usage fact with no schema field. Guard U can forbid
   a `czy` complement; it cannot assert that the packaging *exists* and is
   deliberately unencoded.
3. **`zgadzać się`'s two direct-speech rows are structurally identical.**
   Consent A4 and agreement B3 have the same single complement. Guard K places
   each under the correct meaning key, but nothing structural verifies that the
   consent semantics sits under `consent` rather than under
   `opinion-agreement`.
4. **`polecać`'s A4 gerund/action-noun preference is not expressible.** The
   locked schema has no noun-class field; the normative note lives in
   `internalScope` and `learnerExplanationEn` only.
5. **`polecać`'s A4 and B1 rows are structurally identical across two
   different meanings.** A4 `dative-accusative-action-noun`
   (`directive-instruction`) and B1 `dative-accusative-recommended-item`
   (`recommendation`) share the exact shape
   `{case:accusative role=object required=true, case:dative role=recipient
   required=false}`. Guard O's `exactMeaningSet: true` pins the declared shape
   set under each meaning key, but — exactly as for `móc` (item 1) and
   `zgadzać się` (item 3) above — a structural comparison of two identical
   complement multisets cannot itself distinguish which semantics belongs
   under which key; a swap between the two rows would be structurally
   invisible to guard O. This is not a guard defect and not a missing
   invariant: the complement structures genuinely are identical, so no
   additional structural rule could separate them without inventing a field
   the locked schema does not have. The directive/instruction-versus-
   recommendation split — like the A4 gerund/action-noun preference in item 4
   — is therefore preserved only through `internalScope`, `glossesEn`,
   `learnerExplanationEn`, the example, and independent review, not through
   any guard.
6. **`pasować`'s four relation types are not structurally distinguishable
   beyond shape.** Meanings A and C both contain
   `do+genitive role=target required=true`; only C's optional Dative
   distinguishes them structurally. That harmony ≠ reference-target is a
   semantic fact carried by the meaning keys, `internalScope`, and the learner
   explanations. Meanings C and D both use `case:dative role=experiencer`; only
   the presence of `do + Genitive` distinguishes them.
7. **`cieszyć się`'s four cause distinctions (realized / anticipated / nominal
   / propositional) are semantic**, not structural; the four distinct shapes
   are enforceable, the four distinct *meanings of those shapes* are not.
8. **`zapraszać`'s event-vs-destination role distinction is not expressible in
   the `role` enum.** Both positions must take `role: target` (the enum has no
   finer value); guard N pins the preposition/case pair, and the semantic
   distinction lives in the pattern keys, `internalScope`, and the learner
   explanations.
9. **`pasować` meaning D's subject–experiencer characterization is not
   expressible as `relationType` under Phase 4B** — see §5.9 and §19.
10. **"This is exact source syntax, not a narrowed realization" is documentation,
    not structure.** Guards pin *which* signatures may appear; the epistemic
    label lives in this matrix, `internalScope`, and review.

## 15. Candidate-key audit

Every proposed key is lowercase kebab-case matching
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, semantic, durable, and sibling-unique within its
owner scope. **No key contains a digit, a verification order, a batch number,
an array position, a source ID (`WSJP-…`), example wording, or a production
`vp-*` ID.**

**Meaning keys** (unique within their lemma; cross-lemma repetition is legal
per the B1A lock):

`meal-preparation`, `booking-reservation`, `experiencing-joy`,
`worry-concern`, `consent`, `opinion-agreement`, `invitation`,
`directive-instruction`, `recommendation`, `giving-advice`,
`appearance-harmony`, `physical-fit`, `typical-appropriateness`,
`expectation-suitability`, `ability-possibility`, `permission` — **16**, all
distinct here, each unique within its own lemma.

**Pattern keys** (unique within `(lemma, meaningKeyRef)`) — 37 total, listed in
§4. Conventions followed:

- Multi-complement keys name their participants in source order
  (`accusative-dish-dative-beneficiary`,
  `dative-evaluator-do-genitive-reference`), following the frozen
  `kupować`/`powiedzieć` convention.
- Mode-prefixed keys distinguish alternative realizations of the same role
  (`accusative-item-dative-beneficiary` vs.
  `accusative-item-dla-genitive-beneficiary`), following the frozen `pisać` /
  `powiedzieć` `dative-…` / `do-genitive-…` convention.
- **Keys do not encode requiredness.** `radzić`'s infinitive row is
  `dative-infinitive-advice`, not `infinitive-advice-optional-dative` — the
  asymmetry lives in the complement `required` flags and guard P, consistent
  with the frozen `umówić się` key-naming rule that keys name
  participants/realization rather than the requiredness pattern.
- Where the same complement shape recurs under different meanings of one
  lemma, the keys are deliberately made distinct for readability rather than
  reused (`do-genitive-harmony-target` / `do-genitive-fit-target` /
  `dative-evaluator-do-genitive-reference`; `infinitive-possible-action` /
  `infinitive-permitted-action`), following the frozen `rozumieć` precedent.
- `ze`/`zeby`/`interrogative`/`direct-speech` key fragments use the locked
  ASCII clause-kind vocabulary, not Polish orthography.

Example keys are **not** proposed here; example authoring is out of scope.

## 16. HOLD history and status

**HOLD count: 0.**

No Batch 6 row required a HOLD. Every candidate HOLD anticipated by the brief
was checked and resolved from repository evidence:

| Anticipated HOLD | Status | Resolution |
|---|---|---|
| `zgadzać się` direct-speech participant pairing unclear | **Resolved** | The sense-2 narrative enumerates three source rows and places the optionality marker on exactly one of them ("`z KIM/CZYM`, optional `z KIM/CZYM` with a `że` clause, and direct speech"). Direct speech is listed alone, so B3 takes no partner. This is an explicit enumeration, not an inference, and it matches the frozen `powiedzieć` treatment of a recipientless direct-speech schema. |
| `pasować` optionality cannot be reconstructed exactly | **Resolved** | The narrative marks optionality position-by-position and the CSV structured field agrees on every one: sense 1 `do` unmarked → required; sense 2 both marked optional; sense 4 `KOMU` marked optional, `do` unmarked → required; sense 5 `KOMU/CZEMU` marked optional. Two independent layers agree; nothing was inferred. |
| `móc` sense-4 meaning ownership cannot be resolved | **Resolved** | Three independent frozen statements assign the question use to the **permission** frame (§8.5). Ownership is stated, not inferred. |
| `rezerwować` sense-2 disposition | **Resolved** | Three independent frozen statements scope Phase 3 to sense 1 and label sense 2 a contrast boundary only (§8.1). |
| `gotować` / `pasować` all-optional rows | **Not a HOLD by policy** | The Phase 4B5 adjudication (HOLD-1A) is binding precedent, independently re-confirmed here by validator probe (§18.1). |
| `pasować` meaning D `relationType` | **Resolved, flagged** | Determined by the locked validator plus the canonical `zależeć` precedent (§5.9). Recorded as a Phase 4C reconciliation item (§19), not as an evidence gap. |

Because HOLD count is 0, the commit gate in §26 of the authoring brief is
open.

## 17. Final reconciliation counts

Counts are **discovered from the evidence**, not prescribed in advance.

- **Full-pattern lemmas covered:** exactly **10** — orders 52, 53, 54, 55, 56,
  57, 58, 59, 60, 61.
- **Metadata-only identities in scope:** none.
- **Meanings proposed: 16** — `gotować` 1, `rezerwować` 1, `cieszyć się` 1,
  `martwić się` 1, `zgadzać się` 2, `zapraszać` 1, `polecać` 2, `radzić` 1,
  `pasować` 4, `móc` 2. Independently recomputed:
  1+1+1+1+2+1+2+1+4+2 = **16**.
- **Product schema alternatives resolved: 37** — `gotować` 1, `rezerwować` 2,
  `cieszyć się` 4, `martwić się` 4, `zgadzać się` 7, `zapraszać` 2,
  `polecać` 5, `radzić` 5, `pasować` 5, `móc` 2. Independently recomputed:
  1+2+4+4+7+2+5+5+5+2 = **37**.
- **All-optional product rows: 4** — `gotować` A1, `pasować` B1, `pasować` B2,
  `pasować` D1 (§7).
- **Multi-complement rows: 17**; single-complement rows: **20**;
  17 + 20 = **37** ✓ (§6).
- **HOLD rows: 0.**
- **Source rows → product rows: 35 → 37.** Per lemma: `gotować` 1→1,
  `rezerwować` 2→2, `cieszyć się` 3→4, `martwić się` 4→4,
  `zgadzać się` 7→7, `zapraszać` 2→2, `polecać` 5→5, `radzić` 4→5,
  `pasować` 4→5, `móc` 3→2. Source-row total independently recomputed:
  1+2+3+4+7+2+5+4+4+3 = **35**. The net +2 decomposes exactly into **four**
  alternation-bar expansions (`cieszyć się` `z … | na …`; `zapraszać`
  `na CO | do CZEGO`; `radzić` `żeby | interrogative`; `pasować` sense 2
  `do … | na …`, each +1), **one** deliberately unauthored generalized-role
  row (`zapraszać`'s `KOGO + GDZIE`, −1, §11), and **one** frozen ownership
  compression (`móc` sense 4 folded into `permission`, −1):
  35 + 4 − 1 − 1 = **37**. Every mapping is reconciled row by row in §4.1.
- **Proposed live guards: 21** (A–U, contiguous).
- **Guards proposed for implementation in this task: 0.**

Projected staging state **after** a future Batch 6 authoring task (for
reference only — nothing is changed here): `phaseStep` `4B6`,
`stagingRevision` 7, 59 authored lemmas, 82 meanings, 201 patterns, 9
future-empty lemmas. These are arithmetic projections from the current 49 / 66
/ 164 / 19 plus this matrix's 10 / 16 / 37, not commitments; example counts are
out of scope because example authoring is not planned here.

## 18. Content invariants

Verified unchanged at the end of this task:

| Path | SHA-256 | Status |
|---|---|---|
| `editorial/priority-8-phase4-staging.json` | `fbc25a832c7bd50d775117c877d1876eaa213545785f881585ef5819169c4442` | unchanged |
| `tests/fixtures/priority8_phase4b_authoring_rules.json` | `4cd62f335c8af96f655de49d6f1ed58acd8dba8a3f4eddb461c1c3b7dc6c8f2f` | unchanged |

Staging remains `phaseStep: 4B5`, `stagingRevision: 6`, 49 authored
full-pattern lemmas, 66 meanings, 164 patterns, 164 examples, 19 future-empty
full-pattern lemmas. All ten Batch 6 records retain
`candidateContent: {"meanings": [], "patterns": [], "examples": []}` and
`stagingReviewStatus: "draft"`.

No test file, validator, schema, guard registry, guard interpreter, prior
Phase 4B report, Phase 3 / Phase 3B file, or runtime / canonical / audio /
product file was modified. No production ID was allocated. No
`candidateContent`, meaning, pattern, example, CEFR value, or teaching status
was authored.

### 18.1 Read-only validator probe (no file written)

To avoid relying on assumption for two structurally novel shapes, an in-memory
probe deep-copied live staging, injected synthetic patterns under `pasować`,
and called `validate_data`. The staging file's SHA-256 was identical before and
after (`fbc25a…4442`), confirming nothing was written.

| Probe | Shape | Result |
|---|---|---|
| 1 | single all-optional `do+genitive`, `lexical-frame` | only `future-batch lemma must remain empty` |
| 2 | single all-optional `dative role=experiencer`, `lexical-frame` | only `future-batch lemma must remain empty` |
| 3 | `subject-experiencer` with **only** the optional Dative experiencer | **`complements: subject-experiencer requires subject and experiencer roles`** + the boundary issue |
| 4 | `subject-experiencer` with an added required Nominative subject | only `future-batch lemma must remain empty` |
| 5 | **control**: required `do+genitive`, `lexical-frame` | only `future-batch lemma must remain empty` |

Probes 1, 2, and 5 return the identical single issue, proving the batch-boundary
check fires regardless of requiredness and that **no rule in the locked
validator rejects an all-optional complement array**, including the
single-complement case. Probe 3 versus 4 establishes that
`relationType: subject-experiencer` is impossible for `pasować` meaning D
without inventing a Nominative subject the exact source does not list — the
basis for the §5.9 decision.

## 19. Test results and Phase 4C reconciliation items

### Test results

`python3 validate_priority8_staging.py`:

```
PASS: Priority 8 4B5 staging revision 6 is read-only valid
(68 lemmas, 21 constrained records, 12 global constraints).
```

Nine scoped suites, run individually and then together:

| Suite | Tests | Result |
|---|---:|---|
| `tests/test_priority8_phase4b0_staging.py` | 31 | OK |
| `tests/test_priority8_phase4b1a_authoring_schema.py` | 65 | OK |
| `tests/test_priority8_phase4b1_batch01.py` | 9 | OK |
| `tests/test_priority8_phase4b2_batch02.py` | 11 | OK |
| `tests/test_priority8_phase4b3_batch03.py` | 17 | OK |
| `tests/test_priority8_phase4b4_batch04.py` | 23 | OK |
| `tests/test_priority8_phase4b5_batch05.py` | 29 | OK |
| `tests/test_priority8_phase4b_progress.py` | 8 | OK |
| `tests/test_priority8_phase4b_authoring_guards.py` | 26 | OK |
| **all nine together** | **219** | **OK** |

`git diff --check` clean; `git status --short` and `git diff --name-status`
show exactly one path.

### Phase 4C reconciliation items carried forward

1. **`pasować` meaning D `relationType`.** Phase 4B authors it as
   `lexical-frame` with an optional Dative `experiencer` because the locked
   validator requires a `subject` role for `subject-experiencer` and the exact
   source lists no subject position (§5.9, §18.1). Canonical promotion should
   decide whether to restore `relationType: subject-experiencer` with a
   constructionally supplied Nominative subject, following the canonical
   `podobać się` template. The subject–experiencer characterization is
   **verified evidence**, not rejected — it is architecture-constrained in
   Phase 4B only.
2. **`zapraszać`'s `KOGO + GDZIE` schema.** A selected source position with no
   representable concretization under the locked four-type model. Recorded,
   deliberately unauthored, never converted into a place preposition —
   the same disposition as `czytać`'s `GDZIE` and `umówić się`'s `KIEDY`.
3. **`role` enum granularity.** `zapraszać`'s event/activity versus
   destination/institution roles, and `pasować`'s harmony versus fit versus
   reference targets, all collapse to `role: target`; `pasować`'s evaluator and
   expectation holder both collapse to `role: experiencer`. The distinctions
   are carried in meaning keys, pattern keys, `internalScope`, and learner
   explanations. Whether the canonical role vocabulary should be extended is a
   Phase 4C question.
4. **`móc`'s question packaging.** That `Czy mogę…?` is sentence-level
   pragmatic packaging over the permission infinitive has no schema field and
   is carried as usage guidance. Any later activity or exercise generation must
   not reintroduce it as a complement.
