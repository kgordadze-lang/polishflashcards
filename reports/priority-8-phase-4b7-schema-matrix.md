# Priority 8 Phase 4B7 — Batch 7 schema matrix

## 1. Starting state

This is a **control-plane authoring plan** produced before any Batch 7
`candidateContent` is written. It is not candidate content, not a staging
schema, not runtime data, not a guard, and it allocates no stable ID. It adds
no field to the locked Phase 4B candidate-content schema.

Starting endpoint, verified before any file was created:

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `b517f68ea3791266d5162c117caf6192a085ebce`
- tree `0404582b46c39eacb8be427f0f3524c75e9a0d76`
- parent `cad4c494a1996d9d394a0a49aa304ebeb9dc5dc7`
- subject `Correct Priority 8 Phase 4B6 aspect examples`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook (`-rwxr-xr-x .git/hooks/pre-push`)

Recorded content invariants (must remain byte-identical through this task):

- `editorial/priority-8-phase4-staging.json` SHA-256
  `9bd26dff88943a507b5ead9ce9e72ee8a3da2704193531296f74f4937a6462b3`
- `tests/fixtures/priority8_phase4b_authoring_rules.json` SHA-256
  `a6d696414b35f68a0b69251841e145f000d8c5dd46efc07b3fc61bb69158815d`
- `reports/priority-8-phase-4b6-schema-matrix.md` SHA-256
  `72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c`

Final Batch 6 digest, **recomputed** from the live staging file using the
digest projection pinned in `tests/test_priority8_phase4b6_batch06.py`, and
independently located at three sites
(`tests/test_priority8_phase4b6_batch06.py:38`,
`reports/priority-8-phase-4b6-batch-06-authoring.md:330`,
`reports/priority-8-phase-4b6-batch-06-risk-review.md:35`):

`cff207b6e728fb203ba05a9ba94915432957be76101b3bd6a0f65137cdda98d5`

This matches the expected value in the task brief exactly.

Recomputed staging logical state (recomputed from the file, not taken on
trust):

| Quantity | Value |
|---|---:|
| `phaseStep` | `4B6` |
| `stagingRevision` | 7 |
| authored full-pattern lemmas | 59 |
| meanings | 82 |
| patterns | 201 |
| examples | 201 |
| future-empty full-pattern lemmas | 9 |
| total staging lemma records | 68 |
| `frozenFullPatternCount` | 68 |

The nine future-empty records are exactly orders 62–70 (`musieć`, `wiedzieć`,
`jeść`, `pić`, `kochać`, `przepraszać`, `życzyć`, `korzystać`, `uczyć`) — the
exact Batch 7 scope, and nothing else.

Guard registry recomputed: **57 rules**, `registryVersion = 2`
(`forbid-complement-cooccurrence` 1, `forbid-complement-match` 3,
`require-exact-pattern-shapes` 30, `require-lexical-identity` 8,
`allow-only-preposition-case-signatures` 11,
`require-empty-candidate-content` 2,
`require-lexical-material-in-explanation` 2).

Scoped Phase 4B test baseline recomputed: **243 tests** across the ten suites
(31 + 65 + 9 + 11 + 17 + 23 + 29 + 24 + 8 + 26 = 243).

Every expected starting-state value in the brief was reproduced. There is
**no state mismatch**, so no STOP condition arose.

All nine Batch 7 records carry `bindingConstraints: []` in staging — all nine
are `KEEP VERIFIED` with representation fit `compatible`, and none is one of
the 21 `compatible with narrowing` records. The per-lemma authoring constraints
that do bind them come from the Phase 3B freeze CSV (`authoring_constraint`
column) and are quoted per lemma in §5.

## 2. Exact final Batch 7 scope

Exactly these **nine** full-pattern lemmas, all `full_pattern_in_phase4 = yes`
and `human_freeze_status = FROZEN FULL-PATTERN LEMMA` in the Phase 3B freeze:

| Order | Lemma | Aspect | Aspect partner | Phase 3 disposition | Fit | Evidence |
|---|---|---|---|---|---|---|
| 62 | `musieć` | imperfective | — | KEEP VERIFIED | compatible | A |
| 63 | `wiedzieć` | imperfective | — | KEEP VERIFIED | compatible | A |
| 64 | `jeść` | imperfective | — | KEEP VERIFIED | compatible | A |
| 65 | `pić` | imperfective | — | KEEP VERIFIED | compatible | A |
| 66 | `kochać` | imperfective | — | KEEP VERIFIED | compatible | A |
| 67 | `przepraszać` | imperfective | — | KEEP VERIFIED | compatible | A |
| 68 | `życzyć` | imperfective | — | KEEP VERIFIED | compatible | A |
| 69 | `korzystać` | imperfective | — | KEEP VERIFIED | compatible | A |
| 70 | `uczyć` | imperfective | — | KEEP VERIFIED | compatible | A |

This is exactly the frozen Batch 7 slice `62-70` of the seven-batch map in
`reports/priority-8-phase-4b1a-authoring-schema-lock.md` (`10 / 10 / 10 / 9 /
10 / 10 / 9`), and it is exactly `validator.AUTHORING_BATCHES[6]`.

Explicitly excluded and given **no** Batch 7 row:

- order 61 `móc` — a Phase 3 Batch 07 *verification* row, but **already
  authored in Phase 4B6** (staging shows two meanings, two patterns). It is
  not re-planned, not re-scoped, and not touched here.
- orders 17 `zaczynać` and 37 `przeczytać` — metadata-only identities, both
  outside this range and already protected by
  `p8-4b-zaczynac-metadata-only` / `p8-4b-przeczytac-metadata-only`.
- `uczyć się` — a **separate lexical identity**, already released in the
  canonical corpus (`editorial/verb-pattern-candidates.json`). It receives
  nothing here and donates nothing here.
- `życzyć sobie` — a **separate lexical identity**. It is not among the frozen
  68, receives no record, and donates no syntax or semantics.

No metadata-only identity is included. No aspect partner is recorded for any
of the nine, so no syntax can travel an aspect relation into this batch.

After Batch 7 authoring, all 68 frozen full-pattern additions will have
`candidateContent`.

## 3. Source hierarchy

Binding source hierarchy, in order of authority:

1. `reports/priority-8-phase-3-batch-07.md` (narrative, per-lemma `Składnia`
   quotation) — orders 62–70.
2. `reports/priority-8-phase-3-batch-07-risk-review.md` — representation
   boundaries and the ten independent-review items.
3. `reports/priority-8-phase-3-batch-07-verification.csv` — orders 62–70
   (flat complement inventory; see §3.1).
4. `reports/priority-8-phase-3-final-synthesis.md`.
5. `reports/priority-8-phase-3b-final-lemma-freeze.{csv,md}`,
   `reports/priority-8-phase-3b-phase4-handoff.md`,
   `reports/priority-8-phase-3b-risk-review.md`.
6. Phase 4B control documents:
   `reports/priority-8-phase-4b1a-authoring-schema-lock.md`,
   `reports/priority-8-phase-4b4-schema-matrix.md`,
   `reports/priority-8-phase-4b5-schema-matrix.md`,
   `reports/priority-8-phase-4b6-schema-matrix.md`,
   `reports/priority-8-phase-4b-authoring-guard-hardening.md`,
   `reports/priority-8-phase-4b-test-lifecycle.md`.
7. Read-only structural authority for what the locked model can express:
   `validate_priority8_staging.py`, `priority7_tooling.py`,
   `tests/fixtures/priority8_phase4b_authoring_rules.json`,
   `tests/test_priority8_phase4b_authoring_guards.py`, and — for role and
   relation-type convention only — `editorial/verb-pattern-candidates.json`.
   None of these was modified.

**No fresh web research was performed.** No WSJP page was fetched. No
construction was broadened from general Polish intuition. Every requiredness,
grouping, meaning-ownership, clause-pairing, and role decision below traces to
a quoted frozen statement.

### 3.1 How the two evidence layers were read

The verification-CSV field `supported_constructions_structured` is a **flat
complement inventory**, not a per-schema grouping. Batch 7 demonstrates the
limitation directly:

- `wiedzieć`'s flat list gives four positions
  (`case:Accusative`, `preposition-case:o+Locative`, `clause:że`,
  `clause:interrogative-dependent`) but **drops the optional generalized
  `SKĄD`** that the narrative attaches to every one of the source rows.
- `jeść`'s flat list tags both positions `optional` but cannot say that they
  belong to **one** source schema `(CO) + (CZYM)` rather than two.
- `przepraszać`'s flat list contains `case:Accusative(...,required,za schema)`
  **and** `case:Accusative(...,optional,że schema)` as two entries whose
  grouping survives only inside a prose qualifier.
- `uczyć`'s flat list flattens five sense-1 alternatives and one sense-2
  schema into eight comma-separated entries tagged only `sense1`/`sense2`, and
  encodes the `że | ZDANIE PYTAJNOZALEŻNE` alternation bar as two separate
  entries with no marker that they came from one source row.
- `kochać`'s flat list carries `sense1`/`sense2`/`sense3` markers but no
  statement that the sense-3 infinitive and the sense-3 Accusative are two
  alternatives of one meaning.

The authoritative per-schema layer is therefore the **narrative report's
per-lemma section**, which quotes the WSJP `Składnia` notation with explicit
parenthesised optionality (`(CO) + (CZYM)`, `(KOGO) + że ZDANIE`,
`(KOGO) + CZEGO + GDZIE`, `CO + (SKĄD)`), explicit alternation bars
(`że ZDANIE | ZDANIE PYTAJNOZALEŻNE`), and explicit schema enumeration ("gives
X; Y; and separately Z"). Every row below is derived from that narrative layer
and cross-checked against the CSV and the risk review. Where the two agree, the
row is resolved. **No row in Batch 7 required the flat list to settle
cardinality or requiredness**, and no row contradicts it.

**Notation used below:** `type:value role=… required|optional`. Alternation in
a source row (`A | B`) yields **separate** product alternatives, per global
rule B and the frozen `powiedzieć` / `zapraszać` / `cieszyć się` precedent.
Parenthesised source positions yield `required: false`. Unparenthesised
positions yield `required: true`.

## 4. Full schema matrix

### Order 62 — `musieć` (imperfective)

Source (Batch 07 §62, `WSJP-MUSIEC-01` sense 1): "gives an unrestricted-subject
schema plus `BEZOKOLICZNIK` and a zero-subject schema plus `BEZOKOLICZNIK`."
Freeze constraint: "distinguish personal and impersonal sentence realization
only when pedagogically useful, **without multiplying verb patterns**."

| Field | Value |
|---|---|
| verificationOrder | 62 |
| lemma | `musieć` |
| aspect | imperfective |
| meaningKeyProposal | `necessity-obligation` |
| meaningScope | Core necessity or obligation to do something (WSJP sense 1), covering both personal/unrestricted-subject and zero-subject sentence realization. Excludes the separate discourse uses for advice, expectation, criticism, and elliptical modal talk. |
| schemaKeyProposal | **A1** `infinitive-required-action` |
| relationType | `lexical-frame` |
| requiredComplements | `infinitive role=content required=true` |
| optionalComplements | none |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable — no generalized position in the source |
| subjectOrParticipantRestriction | The subject is **unrestricted** in one source schema and **absent** in the other. Neither is a complement. Recorded in `internalScope`/usage planning only. |
| explicitExclusions | no subject complement; no impersonal complement; no question complement; **no second infinitive pattern created merely because the subject can be absent**; no advice/expectation/criticism/elliptical discourse meaning; obligation source, deadline, reason, time, place, circumstances remain contextual |
| evidenceSource | Batch 07 §62; risk review "Modal verbs and sentence packaging"; CSV order 62; freeze constraint order 62 |
| proposedLiveGuard | **A** `require-exact-pattern-shapes` |

**One meaning, one pattern — determined, not assumed.** See §5.1. No governance
document requires a second meaning record; the HOLD contingency in the brief
therefore does not trigger.

### Order 63 — `wiedzieć` (imperfective)

Source (Batch 07 §63, `WSJP-WIEDZ-01` sense 1): `CO + (SKĄD)`; `o CZYM +
(SKĄD)`; and `(SKĄD) + że ZDANIE | ZDANIE PYTAJNOZALEŻNE`. Three source rows;
the third carries an alternation bar. `SKĄD` is parenthesised in all three.

Meaning: **`factual-knowledge`** — knowing content that can be stated as true
(WSJP sense 1), with nominal, topical, propositional, and
interrogative-dependent content as alternatives.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind | Content shape |
|---|---|---|---|---|---|
| A1 | `accusative-known-content` | `case:accusative role=content required=true` | — | — | **nominal** known content |
| A2 | `o-locative-known-topic` | `preposition-case:o+locative role=topic required=true` | — | — | **topical** known area |
| A3 | `ze-known-proposition` | `clause:ze role=content required=true` | — | `ze` | **propositional** known content |
| A4 | `interrogative-queried-content` | `clause:interrogative role=content required=true` | — | `interrogative` | **queried / unknown-value** content, including any `czy` realization |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
none; `subjectOrParticipantRestriction` — none recorded; `evidenceSource` —
Batch 07 §63, `WSJP-WIEDZ-01`, freeze constraint order 63; `proposedLiveGuard`
— **B**, **C**.

`generalizedRoleStatus`: **optional generalized `SKĄD` is verified-but-
unrepresented.** It is a selected source-role position in all three source
rows, it has **no** concrete product form under the locked four-type
architecture, and it receives **no** product row and **no** complement. See
§12.

`explicitExclusions` (all four rows): **no `od + Genitive`, no `z + Genitive`,
no other source preposition, no `SKĄD` type** — under any circumstances; no
separate `czy` type or `czy` pattern (a `czy` sentence is one realization of
A4); the four alternatives are not cumulative and must not be glossed as
freely interchangeable; no syntax from released `znać` (acquaintance
knowledge); time, place, degree, manner and ordinary circumstances remain
adjuncts.

### Order 64 — `jeść` (imperfective)

Source (Batch 07 §64, `WSJP-JESC-01` sense 1, `jeść I`): exact
`(CO) + (CZYM)` — **one** schema, **both** positions parenthesised. The same
section states the schema "lists **no** lexical Genitive alternative."

| Field | Value |
|---|---|
| verificationOrder | 64 |
| lemma | `jeść` |
| aspect | imperfective |
| meaningKeyProposal | `food-consumption` |
| meaningScope | Ordinary consumption of food (WSJP `jeść I` sense 1). Excludes meal, diet, figurative, and every other `jeść` sense. |
| schemaKeyProposal | **A1** `accusative-food-instrumental-implement` |
| relationType | `lexical-frame` |
| requiredComplements | **none** |
| optionalComplements | `case:accusative role=object required=false`; `case:instrumental role=means required=false` |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable — both positions are exact concrete `Składnia` labels |
| subjectOrParticipantRestriction | — |
| explicitExclusions | **no `jeść` + Genitive pattern of any kind**; no partitive Genitive; no negation-driven Genitive; no promotion of either complement to required; no split into two patterns; no standalone implement row; meal/diet/figurative and all other senses; place, time, meal occasion, frequency, quantity, manner, companions, food source remain adjuncts |
| evidenceSource | Batch 07 §64; risk review "Grammar-owned negation"; CSV order 64; freeze constraint order 64 |
| proposedLiveGuard | **D** `require-exact-pattern-shapes`, **E** `forbid-complement-match` |

**All-optional row.** See §7. **Grammar-owned negation.** See §9.

### Order 65 — `pić` (imperfective)

Source (Batch 07 §65, `WSJP-PIC-01` sense 1): exact `CO`, with an animate
subject, unparenthesised. "No other case or prepositional complement is present
in that schema."

| Field | Value |
|---|---|
| verificationOrder | 65 |
| lemma | `pić` |
| aspect | imperfective |
| meaningKeyProposal | `liquid-consumption` |
| meaningScope | Ordinary consumption of a liquid by an animate subject (WSJP sense 1). Excludes alcohol-use, plant absorption, footwear, and figurative senses. |
| schemaKeyProposal | **A1** `accusative-drink-object` |
| relationType | `lexical-frame` |
| requiredComplements | `case:accusative role=object required=true` |
| optionalComplements | none |
| clauseKind | — |
| requiredLexicalMaterial | — |
| generalizedRoleStatus | not applicable |
| subjectOrParticipantRestriction | The source schema specifies an **animate subject**. This is a selectional restriction on the subject, not a complement, and is carried in `internalScope` only. |
| explicitExclusions | **no Genitive, no partitive Genitive, no quantity-derived Genitive**; no container, source, quantity, temperature, or occasion complement; alcohol-use meaning; plant-absorption meaning; footwear and figurative senses; place, time, frequency, manner, company remain adjuncts |
| evidenceSource | Batch 07 §65; risk review "Grammar-owned negation" (second paragraph); CSV order 65; freeze constraint order 65 |
| proposedLiveGuard | **F** `require-exact-pattern-shapes`, **G** `forbid-complement-match` |

### Order 66 — `kochać` (imperfective) — HIGHEST SEMANTIC-FLATTENING RISK

**Three** meanings. The repeated Accusative surface does **not** merge them.
Freeze constraint order 66: "must label person-love, attachment to
ideas/places, and strong liking separately; **the surface Accusative does not
erase the meaning split**."

#### Meaning A — `person-love`

Source (`WSJP-KOCH-01` sense 1 "matkę"): `KOGO`, unparenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| A1 | `accusative-loved-person` | `case:accusative role=object required=true` | — | emotional **love of a person** |

meaningScope: emotional love of a person (WSJP sense 1).
`explicitExclusions`: **no infinitive** — the sense-3 infinitive may never be
imported here; no idea/place reading; no `za`, `z`, `do` or other collocation
promoted to a frame; reason, duration, degree, reciprocity, manner, time,
place, comparison remain adjuncts.

#### Meaning B — `idea-or-place-attachment`

Source (`WSJP-KOCH-02` sense 2 "wolność"): `CO`, unparenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| B1 | `accusative-cherished-idea-or-place` | `case:accusative role=object required=true` | — | emotional **attachment to an idea or place** |

meaningScope: emotional attachment to an idea, value, or place (WSJP sense 2).
`explicitExclusions`: **no infinitive**; no person-love reading; no
strong-liking reading; same adjunct exclusions as A.

#### Meaning C — `strong-liking`

Source (`WSJP-KOCH-03` sense 3 "czytać"): `CO` **and** `BEZOKOLICZNIK` — two
listed alternatives, neither parenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| C1 | `accusative-strongly-liked-thing` | `case:accusative role=object required=true` | — | strong liking of a **thing** |
| C2 | `infinitive-strongly-liked-activity` | `infinitive role=content required=true` | — | strong liking of an **activity** |

meaningScope: strong liking of a thing or of doing something (WSJP sense 3).
`explicitExclusions`: the two rows are **alternatives, not cumulative**; no
emotional person-love or idea/place reading; the infinitive belongs **only**
here.

Shared `kochać` fields: `relationType: lexical-frame`;
`requiredLexicalMaterial` — none; `clauseKind` — none, deliberately;
`generalizedRoleStatus` — not applicable; `subjectOrParticipantRestriction` —
none recorded as a complement; `evidenceSource` — Batch 07 §66,
`WSJP-KOCH-01`/`-02`/`-03`, risk review "Love versus strong liking", freeze
constraint order 66; `proposedLiveGuard` — **H**.

**Structural-guard limitation, recorded here as required.** A1, B1 and C1 are
**structurally identical** (`case:accusative role=object required=true`). A
structural guard can pin *shape ownership* — which declared shapes exist under
which meaning key — but it **cannot prove the correct semantic interpretation
of identical Accusative shapes**. A swap of the three rows between the three
meaning keys would be structurally invisible. See §8 and §17.

### Order 67 — `przepraszać` (imperfective)

Source (Batch 07 §67, `WSJP-PRZEPRASZ-01`): `KOGO + za CO` and **separately**
`(KOGO) + że ZDANIE`. Two schemas. The person is parenthesised in the clause
schema **only**. Freeze constraint order 67: "preserve required coexistence in
`KOGO + za CO` and **not attach the optionality from the clause schema to the
nominal one**."

Meaning: **`apology`** — asking forgiveness for wrongdoing or inappropriate
behaviour, with a nominal offence/reason schema and an alternative
explanation-clause schema.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `accusative-person-za-accusative-offence` | `case:accusative role=interlocutor required=true`; `preposition-case:za+accusative role=topic required=true` | **none** | — |
| A2 | `accusative-person-ze-explanation` | `clause:ze role=content required=true` | `case:accusative role=interlocutor required=false` | `ze` |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
none; `generalizedRoleStatus` — not applicable; `subjectOrParticipantRestriction`
— the apologised-to position is a person (`KOGO`) in both schemas, carried in
`internalScope`; `evidenceSource` — Batch 07 §67, `WSJP-PRZEPRASZ-01`, risk
review "Apology schema optionality", freeze constraint order 67;
`proposedLiveGuard` — **I**, **J**.

**The requiredness asymmetry is the defining structural fact of this lemma**
and is preserved exactly: the person is `required: true` in A1 and
`required: false` in A2. It is **not** normalized in either direction.

`explicitExclusions`: **no combined `za`-reason + `że`-clause pattern**; no
optional person in A1; no required person in A2; **no reason adjunct pattern
built from ordinary context** — the reason receives frame credit only as exact
`za + Accusative` (A1) or exact `że` content (A2); no standalone person row; no
`żeby`, interrogative, or direct-speech clause; the separate frozen form
`przepraszam` and polite discourse-marker uses supply nothing; manner,
intensity, time, place, channel, subsequent repair remain adjuncts.

### Order 68 — `życzyć` (imperfective, NON-reflexive)

Source (Batch 07 §68, `WSJP-ZYCZ-01` sense 1 "pomyślności"): `KOMU + CZEGO`
and **separately** `KOMU + żeby ZDANIE`. Nothing is parenthesised in either
schema. "No infinitive is listed."

Meaning: **`good-wishes`** — expressing a good wish to a recipient, with
nominal wished content and an alternative wished-event clause.

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `dative-recipient-genitive-wished-thing` | `case:dative role=recipient required=true`; `case:genitive role=content required=true` | — | — |
| A2 | `dative-recipient-zeby-wished-event` | `case:dative role=recipient required=true`; `clause:zeby role=content required=true` | — | `zeby` |

Shared row fields: `relationType: lexical-frame`; `requiredLexicalMaterial` —
**none**; canonical identity is bare `życzyć`; `generalizedRoleStatus` — not
applicable; `subjectOrParticipantRestriction` — none recorded;
`evidenceSource` — Batch 07 §68, `WSJP-ZYCZ-01`, risk review "Wishing identity
and content alternatives", freeze constraint order 68; `proposedLiveGuard` —
**K**.

`explicitExclusions`: **no combined Genitive + `żeby` pattern** — the two
content shapes are alternatives, never cumulative; **no infinitive** — none is
listed in the exact sense; no standalone recipient row; no optionalization of
either the Dative or the content; **no syntax, meaning, or example material
from `życzyć sobie`**; no request/formal-demand meaning; occasion, time,
manner, intensity, medium, ceremony, contextual reasons remain adjuncts.

**Lexical-identity boundary.** A Dative recipient realized as ordinary `komuś`
is part of the verified `życzyć` pattern. The lexical phrase `życzyć sobie` is
a **separate identity** and must not be smuggled into scope or examples merely
because `sobie` is morphologically Dative. What structural guards can and
cannot enforce here is stated in §10 and §17.

### Order 69 — `korzystać` (imperfective) — HIGH SEMANTIC-SAME-SHAPE RISK

**Two** meanings. Identical surface government does **not** merge them.
Freeze constraint order 69: "label resource use versus benefit **while
preserving the same exact `z + Genitive` form**."

#### Meaning A — `resource-use`

Source (`WSJP-KORZ-02` sense 2 "z kuchni"): exact `z CZEGO`, unparenthesised.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| A1 | `z-genitive-used-resource` | `preposition-case:z+genitive role=object required=true` | — | the **resource, tool, or service used** |

meaningScope: using a resource, tool, facility, or service (WSJP sense 2).

#### Meaning B — `benefit-from-advantage`

Source (`WSJP-KORZ-01` sense 1 "z ulg"): exact `z CZEGO`, unparenthesised,
**independently** listed.

| Ref | schemaKeyProposal | requiredComplements | optional | Relation |
|---|---|---|---|---|
| B1 | `z-genitive-source-of-benefit` | `preposition-case:z+genitive role=object required=true` | — | the **advantage or circumstance benefited from** |

meaningScope: benefiting from an advantage, concession, or favourable
circumstance (WSJP sense 1).

Shared `korzystać` fields: `relationType: lexical-frame`;
`requiredLexicalMaterial` — none; `clauseKind` — none; `generalizedRoleStatus`
— not applicable; `subjectOrParticipantRestriction` — none recorded;
`evidenceSource` — Batch 07 §69, `WSJP-KORZ-01`/`-02`, risk review "Same form
across use and benefit senses", freeze constraint order 69;
`proposedLiveGuard` — **L**, **M**.

`explicitExclusions` (both rows): **the two meanings are never merged into one
generic "use" meaning**; no place, provider, availability, purpose, frequency,
duration, manner, or result complement; no collocation-only frame; no syntax
from released `używać` (which independently selects a **direct** Genitive, not
`z + Genitive`).

**Structural-guard limitation.** A1 and B1 carry an **identical structural
signature**. Structural guards cannot prove whether resource-use semantics
versus benefit-from semantics is attached to the correct meaning key. See §8
and §17.

### Order 70 — `uczyć` (imperfective, NON-reflexive) — HIGHEST STRUCTURAL DENSITY

Source (Batch 07 §70). Sense 1 (`WSJP-UCZ-01` "mówić") gives, as **separate**
alternatives: `KOGO/CO + CZEGO`; `KOGO/CO + BEZOKOLICZNIK`;
`KOGO/CO + że ZDANIE | ZDANIE PYTAJNOZALEŻNE`; and `KOGO + o CZYM`. Nothing in
sense 1 is parenthesised. Sense 2 (`WSJP-UCZ-02` "w szkole") gives
`(KOGO) + CZEGO + GDZIE` — the learner **is** parenthesised, the subject
Genitive is not, and `GDZIE` is a generalized position.

#### Meaning A — `teaching-instruction`

meaningScope: teaching or instructing a learner or entity — imparting content,
a skill, a proposition, procedural information, or a topic (WSJP non-reflexive
sense 1).

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| A1 | `accusative-learner-genitive-taught-content` | `case:accusative role=object required=true`; `case:genitive role=content required=true` | — | — |
| A2 | `accusative-learner-infinitive-taught-skill` | `case:accusative role=object required=true`; `infinitive role=content required=true` | — | — |
| A3 | `accusative-learner-ze-taught-proposition` | `case:accusative role=object required=true`; `clause:ze role=content required=true` | — | `ze` |
| A4 | `accusative-learner-interrogative-taught-content` | `case:accusative role=object required=true`; `clause:interrogative role=content required=true` | — | `interrogative` |
| A5 | `accusative-person-o-locative-taught-topic` | `case:accusative role=object required=true`; `preposition-case:o+locative role=topic required=true` | — | — |

Requiredness verified from the source, not assumed: **no** sense-1 position is
parenthesised in the quoted `Składnia`, so every sense-1 complement is
`required: true`. A5's Accusative is restricted to `KOGO` (a person) in the
source; that restriction is carried in `internalScope`, not in the role (§13).

#### Meaning B — `school-subject-teaching`

meaningScope: teaching a school subject (WSJP non-reflexive sense 2).

| Ref | schemaKeyProposal | requiredComplements | optional | clauseKind |
|---|---|---|---|---|
| B1 | `accusative-learner-genitive-school-subject` | `case:genitive role=content required=true` | `case:accusative role=object required=false` | — |

Shared `uczyć` fields: `relationType: lexical-frame`; `requiredLexicalMaterial`
— **none**; canonical identity is bare non-reflexive `uczyć`, with **no `się`
in any form**; `subjectOrParticipantRestriction` — none recorded as a
complement; `evidenceSource` — Batch 07 §70, `WSJP-UCZ-01`/`-02`, risk review
"Non-reflexive `uczyć`", freeze constraint order 70; `proposedLiveGuard` —
**N**, **O**.

`generalizedRoleStatus`: **sense-2 `GDZIE` is verified-but-unrepresented.** It
is a selected generalized place position in the exact sense-2 schema; it
receives **no** complement, **no** preposition, and **no** product row, while
the representable lexical core (optional learner + required subject Genitive)
is retained as B1. See §12 for the precedent check.

`explicitExclusions`: **no maximal frame** merging Genitive, infinitive,
clause, and `o + Locative` — the five sense-1 rows are strict alternatives;
**no concrete `w`, `na`, `u`, or other place government derived from `GDZIE`**;
no place complement type; no standalone learner row; no standalone content row;
no optionalization of any sense-1 complement; no promotion of the sense-2
learner to required; **no evidence, complement, role, key, or example material
from `uczyć się`** in either direction; time, duration, manner, institution,
frequency, method, purpose, and ordinary location remain adjuncts.

## 4.1 Source-row → product-row reconciliation (high-risk lemmas)

### `wiedzieć` (order 63)

| Source row (exact) | Product rows | Note |
|---|---|---|
| `CO + (SKĄD)` | A1 | `SKĄD` dropped as unrepresentable; recorded, not silently lost (§12) |
| `o CZYM + (SKĄD)` | A2 | as above |
| `(SKĄD) + że ZDANIE \| ZDANIE PYTAJNOZALEŻNE` | A3 **and** A4 | the alternation bar **splits** into two product rows; `SKĄD` dropped as above |

3 source rows → **4** product rows. A `czy` sentence is a realization of A4 and
creates **no** fifth row.

### `kochać` (order 66)

| Source row (exact) | Meaning | Product row |
|---|---|---|
| sense 1 `KOGO` | `person-love` | A1 |
| sense 2 `CO` | `idea-or-place-attachment` | B1 |
| sense 3 `CO` | `strong-liking` | C1 |
| sense 3 `BEZOKOLICZNIK` | `strong-liking` | C2 |

4 source rows → **4** product rows across **3** meanings. The three Accusative
rows stay **meaning-owned**; they are not merged, and the sense-3 infinitive is
not lifted into senses 1 or 2.

### `przepraszać` (order 67)

| Source row (exact) | Product row | Person requiredness |
|---|---|---|
| `KOGO + za CO` | A1 | **required** (unparenthesised) |
| `(KOGO) + że ZDANIE` | A2 | **optional** (parenthesised) |

2 source rows → **2** product rows. The optionality stays inside the clause
schema.

### `życzyć` (order 68)

| Source row (exact) | Product row |
|---|---|
| `KOMU + CZEGO` | A1 |
| `KOMU + żeby ZDANIE` | A2 |

2 source rows → **2** product rows. The Dative is required in both; the two
content shapes never combine; no infinitive row is created because none is
listed.

### `uczyć` (order 70)

| Source row (exact) | Meaning | Product rows |
|---|---|---|
| `KOGO/CO + CZEGO` | `teaching-instruction` | A1 |
| `KOGO/CO + BEZOKOLICZNIK` | `teaching-instruction` | A2 |
| `KOGO/CO + że ZDANIE \| ZDANIE PYTAJNOZALEŻNE` | `teaching-instruction` | A3 **and** A4 (bar splits) |
| `KOGO + o CZYM` | `teaching-instruction` | A5 |
| `(KOGO) + CZEGO + GDZIE` | `school-subject-teaching` | B1, with `GDZIE` unrepresented |

5 source rows → **6** product rows across **2** meanings. No row is merged into
a maximal frame; the generalized `GDZIE` does not disappear silently — it is
governed in §12.

## 5. Per-lemma rationale

### 5.1 `musieć` — why one meaning and one pattern

Three independent frozen statements make the personal/zero-subject contrast a
**sentence-realization** fact, not a lexical one:

- Batch 07 §62: "Personal versus impersonal sentence realization **does not
  create two complement types**."
- CSV order 62 `verified_meaning_summary`: "core obligation or necessity sense
  1, **covering personal and zero-subject schemas without inventing a separate
  impersonal complement type**"; `adjunct_boundary_summary`: "**Subject
  realization is not a complement slot.**"
- Freeze constraint order 62: "…**without multiplying verb patterns**."

The two source schemas differ **only** in whether a subject is realized, and
the subject is not a complement in the locked model. Producing two patterns
would therefore create two byte-identical complement multisets under one
meaning — a duplicate that misrepresents the source as offering two lexical
alternatives. Producing two meanings would contradict the single scoped
necessity sense. **One meaning, one pattern**; the personal/zero-subject
contrast is carried in `internalScope` and usage planning. No repository
governance document requires two meaning records, so the brief's HOLD
contingency does not trigger.

### 5.2 `wiedzieć` — four content alternatives, one meaning

The evidence scopes exactly one sense ("knowledge of content that can be stated
as true") and lists four architecture-compatible positions inside it. The
freeze constraint requires preserving "nominal/topic versus
propositional/interrogative content" — a distinction between *patterns*, not
between *meanings*. Four alternatives under one meaning is therefore the exact
representation; splitting into four meanings would invent sense boundaries the
source does not draw, and merging any two would erase a distinction the freeze
constraint names.

The Accusative takes `role: content` rather than `object` because the source
labels it "known **content**" and because the same slot alternates with `że`
and interrogative clause content; canonical `mówić`
(`dative-recipient-accusative-content`) already uses `case:accusative
role=content` for exactly such a nominal/clausal content alternation.

### 5.3 `jeść` — an all-optional row is the faithful reading

`(CO) + (CZYM)` is **one** parenthesised pair in **one** schema. Splitting it
into two patterns would assert two source alternatives that do not exist;
promoting either position would contradict the parentheses; dropping the
Instrumental would discard an explicit completeness addition the risk review
names ("exact optional Instrumental completeness addition"). The only faithful
product row therefore has a non-empty complement array in which every
complement is optional. That representation is already proven live (§7).

The Instrumental role is `means` on direct precedent, not invention — see
§13.1.

### 5.4 `pić` — one required Accusative

The exact schema gives `CO` and nothing else. The animate-subject specification
is a selectional restriction on the subject; the locked model has no subject
complement outside `constructional-frame`/`subject-experiencer` Nominative, and
inventing one here would contradict `relationType: lexical-frame` and the
source. Quantity contexts are explicitly excluded from creating Genitive: "No
generic Genitive or partitive pattern is inferred."

### 5.5 `kochać` — three meanings survive identical shapes

The source lists three separately numbered senses; the freeze constraint
requires all three to be labelled separately. The infinitive is attached to
sense 3 alone ("a completeness addition rather than evidence for the
emotional-person sense"). The released canonical corpus independently shows the
same *shape pair* under one meaning for `lubić`
(`accusative-object` + `infinitive-activity`); that is convergent evidence for
how a thing/activity liking sense is represented, **not** a donation — `kochać`
sense 3 is derived from `WSJP-KOCH-03` alone.

### 5.6 `przepraszać` — the asymmetry is the lemma

Both the narrative, the CSV, the risk review, and the freeze constraint state
the same fact four times: person + `za`-reason **coexist and are required**
in the nominal schema; the person is optional **only** in the clause schema.
The risk review names the failure mode explicitly: "Applying this optionality
to the nominal person-plus-reason schema would be an **alignment error**."

### 5.7 `życzyć` — alternatives, never cumulative

`KOMU + CZEGO` and `KOMU + żeby ZDANIE` are two listed schemas sharing a
required Dative. The Genitive and the `żeby` clause are the **same content
slot** realized two ways, which is why the Genitive carries `role: content` —
matching the clause it alternates with, and matching canonical `uczyć się`'s
`genitive-subject-matter` (`role: content`) for a comparable nominal content
position. No infinitive is listed, so none is authored.

### 5.8 `korzystać` — two meanings, one form

Both senses are independently listed with `z CZEGO`; the CSV states their
"semantic roles differ, but each is an exact preposition-case construction",
and the freeze constraint requires labelling the two while "preserving the same
exact `z + Genitive` form". Merging them because the government is identical is
precisely the prohibited move; giving them different `role` values to force a
structural difference would be inventing a distinction the locked role enum
does not encode (§13.2). Two meanings, one identical shape each, with the
semantic split carried editorially.

### 5.9 `uczyć` — density without merger

The source enumerates alternatives with explicit separateness ("gives
`KOGO/CO + CZEGO`; `KOGO/CO + BEZOKOLICZNIK`; …; and `KOGO + o CZYM`") and the
Phase 2 answer states the conclusion directly: "it does **not** license one
Accusative-plus-Genitive-plus-infinitive frame." Sense 2 is independently
listed and independently scoped (school subject), and its learner is
parenthesised while sense 1's is not — so B1's optional Accusative is a source
fact, not a normalization.

## 6. Requiredness / optionality audit

Every multi-complement product row, with each complement's requiredness and its
exact source warrant:

| Row | Complements | Source warrant |
|---|---|---|
| `jeść` A1 | accusative **optional**, instrumental **optional** | `(CO) + (CZYM)` — both parenthesised, one schema |
| `przepraszać` A1 | accusative **required**, `za`+accusative **required** | `KOGO + za CO` — neither parenthesised |
| `przepraszać` A2 | `ze` clause **required**, accusative **optional** | `(KOGO) + że ZDANIE` — person parenthesised |
| `życzyć` A1 | dative **required**, genitive **required** | `KOMU + CZEGO` — neither parenthesised |
| `życzyć` A2 | dative **required**, `zeby` clause **required** | `KOMU + żeby ZDANIE` — neither parenthesised |
| `uczyć` A1 | accusative **required**, genitive **required** | `KOGO/CO + CZEGO` |
| `uczyć` A2 | accusative **required**, infinitive **required** | `KOGO/CO + BEZOKOLICZNIK` |
| `uczyć` A3 | accusative **required**, `ze` clause **required** | `KOGO/CO + że ZDANIE` |
| `uczyć` A4 | accusative **required**, `interrogative` clause **required** | `KOGO/CO + ZDANIE PYTAJNOZALEŻNE` |
| `uczyć` A5 | accusative **required**, `o`+locative **required** | `KOGO + o CZYM` |
| `uczyć` B1 | genitive **required**, accusative **optional** | `(KOGO) + CZEGO + GDZIE` — learner parenthesised, subject not |

**11 multi-complement rows.** The remaining **12** rows are single-complement:
`musieć` 1, `wiedzieć` 4, `pić` 1, `kochać` 4, `korzystać` 2. 11 + 12 = **23**.

No complement anywhere was promoted from optional to required, and none was
demoted. Every requiredness value traces to an explicit parenthesisation (or
its absence) in the quoted `Składnia` notation. The two requiredness
asymmetries in this batch — `przepraszać`'s person (A1 required, A2 optional)
and `uczyć`'s learner (A1–A5 required, B1 optional) — are preserved exactly and
normalized in **neither** direction.

## 7. All-optional pattern audit

**Exactly one** proposed row has zero required complements. The number was
discovered by inspecting every row, not prescribed: `uczyć` B1 has a required
Genitive, `przepraszać` A2 has a required clause, and no other row parenthesises
all of its positions.

Per the binding Phase 4B5 precedent (HOLD-1A adjudication) and the Phase 4B6
extension, a product pattern **may** have a non-empty complement array in which
every complement is `required: false`; five such patterns are already live in
staging (`umówić się` ×1, `gotować` ×1, `pasować` ×3 of the current 201). This
row is **not** placed on HOLD.

| # | Row | Complements (all optional) | Array non-empty? | Source optionality | Promotion? | Standalone-participant error? |
|---:|---|---|---|---|---|---|
| 1 | `jeść` A1 | `case:accusative role=object`; `case:instrumental role=means` | **yes**, 2 | `(CO) + (CZYM)` — both parenthesised in **one** schema | none — promoting either would contradict the parentheses and the brief | no — both participants stay **inside** their single source-owned schema; neither receives a standalone row |

**Structural validation.** A read-only, in-memory probe against the current
locked `validate_priority8_staging.py` (no repository file written; staging
SHA-256 identical before and after — see §21.1) confirmed that this exact
two-complement all-optional shape validates: it returned only the unrelated
`future-batch lemma must remain empty` boundary issue, byte-identical to the
required-complement control.

**Guard consequence.** `require-exact-pattern-shapes` compares exact complement
objects including `required`, so guard D pins this row's optionality
structurally: promoting either complement to required, or splitting the pair
into two rows, breaks multiset equality and fails.

## 8. Same-shape semantic audit

Every case in which two or more **different meanings of the same lemma** carry
structurally identical shapes. Two families exist in Batch 7.

### Family 1 — `kochać`: three identical Accusative rows

Shape: `[{type: case, case: accusative, required: true, role: object}]`, under
`person-love` (A1), `idea-or-place-attachment` (B1), and `strong-liking` (C1).

- **A. What a structural guard can enforce.** Guard H
  (`require-exact-pattern-shapes`, `exactMeaningSet: true`) pins the exact
  meaning-key inventory (three keys, no more, no fewer) and the exact shape
  multiset under each key: one Accusative row under A and under B; one
  Accusative row **and** one infinitive row under C. It therefore blocks
  merging the three meanings, adding a fourth, importing the infinitive into A
  or B, adding any complement to any row, and changing any requiredness.
- **B. What it cannot enforce.** It cannot prove that person-love semantics
  sits under `person-love` rather than under `strong-liking`. Three identical
  complement multisets are structurally interchangeable; a three-way swap would
  be invisible to every available primitive, and no additional structural rule
  could separate them without inventing a schema field that does not exist.
- **C. Editorial fields that must carry semantic identity.**
  `candidateMeaningKey`, `internalScope`, `glossesEn`,
  `learnerExplanationEn`, and the authored examples.
- **D. What independent authoring review must inspect.** That each Accusative
  example names the right kind of object (a person; an idea/value/place; a
  thing), that no gloss reads "love + Accusative" generically, and that the
  infinitive row appears only under `strong-liking`.

### Family 2 — `korzystać`: two identical `z + Genitive` rows

Shape: `[{type: preposition-case, preposition: z, case: genitive, required:
true, role: object}]`, under `resource-use` (A1) and `benefit-from-advantage`
(B1).

- **A. Enforceable.** Guard L pins two meaning keys with exactly one shape
  each; guard M pins the single authorized preposition-case signature so no
  other preposition can appear under either meaning.
- **B. Not enforceable.** Which of the two semantics belongs under which key.
  The shapes are byte-identical, deliberately so, because the frozen evidence
  says the form is the same.
- **C. Editorial fields.** `candidateMeaningKey`, `internalScope`,
  `glossesEn`, `learnerExplanationEn`, examples.
- **D. Review must inspect.** That the `resource-use` example uses a resource,
  tool, facility, or service, and the `benefit-from-advantage` example uses an
  advantage/concession/circumstance — and that neither gloss collapses into a
  generic "use `z` + Genitive".

### `uczyć` — checked and **no** family found

`uczyć` was independently checked for structural convergence because it is the
densest lemma. Its six rows are pairwise distinct: A1 (`acc required` +
`gen`) versus B1 (`acc **optional**` + `gen`) differ in the Accusative
`required` flag, which is part of the exact complement object the guard
compares. Guard N can therefore place both rows structurally, and `uczyć`
contributes **no** same-shape family.

### Cross-lemma shape coincidence — not a family

`pić` A1, `kochać` A1/B1/C1 and (with different roles) other Batch 1–6 rows
share the shape `[case:accusative required=true role=object]`. This is
**cross-lemma** convergence between separate lemma records, each independently
sourced; guards are lemma-scoped and meaning ownership is never in question
across lemma boundaries. It is recorded here for completeness and is **not**
counted as a same-shape semantic family.

### Batch 6 lesson carried forward

The `polecać` A4/B1 and `móc` ability/permission findings (Batch 6 §14.2 items
1 and 5) established that `exactMeaningSet: true` pins the *inventory* but
never the *semantics* of identical multisets. Batch 7 reproduces that finding
twice and resolves it the same way — by documenting the limitation and routing
the invariant to editorial fields and independent review, not by inventing a
guard that cannot exist.

## 9. Grammar-owned negation audit — `jeść`

This section exists because the `jeść` boundary is the single most
misrepresentable fact in Batch 7.

| Claim | Status |
|---|---|
| Positive lexical object of `jeść` is **Accusative** | **Product lexical pattern** — A1, `case:accusative role=object required=false` |
| Surface **Genitive under ordinary negation** (`nie jem chleba`) | **Grammar-owned**: a general Polish sentence-grammar transformation, generated by the negation rule, not selected by this lemma |
| A candidate pattern for `jeść` + Genitive | **None. Not authored.** |
| Partitive Genitive | Not established by the exact inspected schema, and explicitly not conflated with negation |

Exact frozen warrants: Batch 07 §64 — "Ordinary Genitive under negation is a
general Polish grammar transformation, not a separate lemma-specific pattern.
The exact schema **lists no lexical Genitive alternative**." Risk review —
"Creating a lemma-specific `jeść + Genitive` pattern from negative sentences
would **falsely attribute a general Polish transformation to lexical
valency**." Phase 3B global constraint 8 — "Keep ordinary Genitive under
negation grammar-owned rather than creating a lemma-specific lexical pattern."
Freeze constraint order 64 — "teach positive Accusative as the lexical frame
and handle negation separately; examples should not make negation obscure the
selected object case."

**Scope of the claim, stated precisely.** Nothing here says or implies that
Genitive under negation is unsupported, marginal, or incorrect Polish. It is
ordinary, fully grammatical Polish. The narrow claim is: **it is not authored
in this record as lemma-specific lexical valency for `jeść`**, because the
exact sense-1 schema does not list it and because the alternation is produced
by sentence grammar that applies to Accusative objects generally. Any future
guard message, report line, or learner explanation must preserve that narrow
framing. The same narrow framing applies to `pić` (§10 of the Batch 07
narrative; risk review second paragraph of "Grammar-owned negation").

**Proposed live-guard strategy (not implemented).** Two layers:

1. Guard D (`require-exact-pattern-shapes`) already makes the meaning's shape
   multiset exact — a Genitive complement added anywhere under
   `food-consumption` breaks multiset equality and fails.
2. Guard E (`forbid-complement-match`, signature `{type: case, case:
   genitive}`) is proposed **in addition**, for the same reason the frozen
   `p8-4b-moc-no-question-clause` rule was accepted alongside
   `p8-4b-moc-exact-pattern-shapes`: it states the invariant *legibly and
   independently*, so the "no lexical Genitive" boundary survives any future
   legitimate revision of the shape set, and it names the boundary in the
   registry where a later author will actually look. It carries no risk of
   redundancy harm because `jeść` legitimately has **no** Genitive complement
   of any kind. Guard G is the identical proposal for `pić`.

Both are absence/prohibition rules and may therefore be introduced before or
with the authoring commit, per
`reports/priority-8-phase-4b-authoring-guard-hardening.md`. No guard is
implemented in this task.

## 10. Lexical-identity audit

| Lemma | Canonical identity | Lexical material | Treatment |
|---|---|---|---|
| `życzyć` (68) | `życzyć` | **none** | Bare non-reflexive identity. `sobie` is **not** part of it and must never be attached. A Dative recipient realized as ordinary `komuś` is in scope; the lexical phrase `życzyć sobie` is a **separate identity** and is out of scope for meaning, patterns, and examples. |
| `życzyć sobie` | — | `sobie` | Not among the frozen 68, receives no record, donates nothing. |
| `uczyć` (70) | `uczyć` | **none** | Bare non-reflexive identity. **No `się` in any form.** No complement, role, key, gloss, explanation, or example may rely on `uczyć się`. |
| `uczyć się` | `uczyć się` | `się` | A **separate, already-released canonical lemma** (`editorial/verb-pattern-candidates.json`, meaning `study`, patterns `genitive-subject-matter` and `infinitive-skill`). Its own `internalScope` already states: "uczyć (teach someone) is a different lemma." It donates nothing to order 70 and receives nothing from it. |

Phase 3B global constraint 4 ("Preserve lexical `się` and `sobie` as part of
the verified identity") and constraint 10 ("Keep related identities separate,
including … `uczyć / uczyć się`") are both satisfied by exclusion: neither
Batch 7 lemma **has** such material, and neither may acquire it.

### 10.1 What structural guards CAN enforce here

This was determined by reading the guard engine, not assumed:

- Every rule targets its record by `verificationOrder`, and
  `guard_issues` then rejects the record outright unless
  `canonicalLemma == rule.lemma`
  (`tests/test_priority8_phase4b_authoring_guards.py:356–364`), with the same
  check repeated at registry-validation time via `_target_issues`. Any rule
  carrying `verificationOrder: 68, lemma: "życzyć"` therefore **structurally
  prevents record 68 from being renamed to `życzyć sobie`**, and guard N does
  the same for record 70 versus `uczyć się`. This is real enforcement, and it
  comes free with the shape guards.
- `validate_priority8_staging.py` permits `requiredLexicalItems` **only** on
  `brać` and `wziąć`, and only with the value `["udział"]`
  (`validate_priority8_staging.py:919, 979–985`). Neither `sobie` nor `się`
  can be attached to any Batch 7 record as structural lexical material.
- Guard N's exact shape sets make the released `uczyć się` inventory
  unauthorable on `uczyć`: a bare single-complement `genitive content` row (the
  `uczyć się` study shape) or a bare `infinitive content` row (the `uczyć się`
  skill shape) breaks multiset equality, because every authorized `uczyć` row
  also carries the Accusative learner.

### 10.2 What structural guards CANNOT enforce here

- **No primitive inspects example tokens.** `candidateExample.pl` is never read
  by any guard kind. Nothing structural prevents a future example sentence for
  `życzyć` from containing `sobie`, or an example for `uczyć` from containing
  `się`.
- **`require-lexical-identity` is an inclusion test, not an exclusion test.**
  It checks that the canonical lemma *contains* the listed material
  (`_token_present`); it cannot express "must **not** contain `sobie`".
  Proposing `require-lexical-identity` with `lexicalItems: ["życzyć"]` would be
  a tautology against the identity string and would add no invariant beyond the
  target-equality check above, so it is **not** proposed (§16, and §22 of the
  brief on guard proliferation).
- **`require-lexical-material-in-explanation` also only asserts presence**, in
  `learnerExplanationEn` prose, and its own governing report states it "cannot
  … interpret a negated/unrelated mention". It cannot forbid a word.

These two facts are therefore recorded as **semantic/editorial limitations for
later authoring and independent review**: the `życzyć` / `życzyć sobie` and
`uczyć` / `uczyć się` boundaries must be protected by `internalScope`,
`glossesEn`, `learnerExplanationEn`, example wording, and an explicit reviewer
check — not by a guard that cannot exist. See §17 items 3 and 4.

## 11. Clause normalization audit

Clause kinds are kept exactly as the source distinguishes them. The locked
private clause-kind vocabulary is `ze`, `czy`, `zeby`, `interrogative`,
`direct-speech`.

| Lemma | `ze` | `zeby` | `interrogative` | `direct-speech` | `czy` |
|---|---|---|---|---|---|
| `wiedzieć` | A3 | — | A4 | — | **not used** |
| `przepraszać` | A2 | — | — | — | — |
| `życzyć` | — | A2 | — | — | — |
| `uczyć` | A3 | — | A4 | — | **not used** |
| `musieć`, `jeść`, `pić`, `kochać`, `korzystać` | — | — | — | — | — |

- `ze` and `zeby` are never merged. `wiedzieć`, `przepraszać` and `uczyć` have
  `że`; `życzyć` has `żeby`; no lemma has both.
- `interrogative` (interrogative-dependent content, `ZDANIE PYTAJNOZALEŻNE`) is
  never merged into `ze` or into `czy`.
- **`czy` is a realization, not a fifth clauseKind.** For `wiedzieć` and
  `uczyć` the exact source label is `ZDANIE PYTAJNOZALEŻNE`; the narrative
  states "a `czy` clause is **one realization** of the interrogative-dependent
  construction" and "`Czy` is **not a fifth locked type**". The product
  therefore uses `clauseKind: interrogative`, and a primary example that
  happens to use `czy` creates **no** separate type, pattern, or key. Live
  staging does carry `clauseKind: czy` on the already-frozen Batch 2/3 records
  `zapominać` and `kłócić się`, but their frozen Phase 3 evidence is
  **interrogative-dependent** (`że ZDANIE | ZDANIE PYTAJNOZALEŻNE` and
  `ZDANIE PYTAJNOZALEŻNE` / `ŻE` respectively), not a direct literal-`czy`
  source. Those prior-batch authoring decisions are **outside Batch 7 scope**;
  this matrix takes no position on them and does **not** cite them as
  source-level precedent for a literal `czy` mapping. Batch 7 maps
  `ZDANIE PYTAJNOZALEŻNE` to `interrogative` on its own frozen evidence alone.
- **No direct-speech pattern anywhere in Batch 7.** No Batch 7 source lists
  direct speech, so none is authored — including for `przepraszać` and
  `uczyć`, where an apology or an instruction could plausibly be quoted.
  Plausibility is not evidence.
- The `że | ZDANIE PYTAJNOZALEŻNE` alternation bar in `wiedzieć` row 3 and
  `uczyć` sense-1 row 3 **splits** into two product rows each (§4.1).

## 12. Generalized-role audit

`DOKĄD`, `SKĄD`, `GDZIE`, and `KTÓRĘDY` are not complement types, are not
proof of one concrete preposition, and are not concretized anywhere in
Batch 7.

| Lemma | Generalized role in evidence | Status | Product treatment |
|---|---|---|---|
| `wiedzieć` (63) | **optional `SKĄD`**, attached to all three source rows | **verified-but-unrepresented** | No complement, no row, no preposition. The selected source role is retained in this matrix and must be retained in `internalScope` planning. Guard C pins the single authorized preposition-case signature (`o + Locative`), so no `od`, `z`, `spod`, or other source preposition can ever be introduced as a `SKĄD` concretization. |
| `uczyć` (70) sense 2 | **`GDZIE`** in `(KOGO) + CZEGO + GDZIE` | **verified-but-unrepresented** | No complement, no row, no preposition. The representable lexical core of the schema (optional learner + required subject Genitive) **is** retained as B1. Guard O pins the single authorized preposition-case signature (`o + Locative`), so no `w`, `na`, `u`, or other place preposition can be introduced. |
| all other Batch 7 lemmas | none listed | not applicable | — |

**Distinguishing verified-but-unrepresented from rejected.** These two
positions are **selected, verified source evidence** that the locked four-type
model cannot express. They are neither rejected hypotheses nor unsupported
inferences. Rejected material in Batch 7 (e.g. `jeść` + Genitive as lexical
valency, a `czy` type, a `SKĄD` type, a place complement type) is listed in
§15 under exclusions and is categorically different: it is evidence the source
does **not** support, or a representation the architecture forbids.

**Precedent independently verified, as the brief requires.** Retaining a
representable lexical core while dropping an unrepresentable generalized
position is the established frozen treatment, not a new move invented for
`uczyć`:

- `zapraszać` (Batch 6, §11 of the Batch 6 matrix): the separate
  `KOGO + GDZIE` schema receives **no product row at all**, while the exact
  `na`/`do` schemas are authored — "a selected source position that the locked
  model cannot represent is documented, not silently dropped and not
  invented."
- `czytać` (Batch 4): deliberately unauthored `GDZIE`.
- `umówić się` (Batch 5): deliberately unauthored `KIEDY`.
- `pracować` (Batch 1, live binding constraint): "Do not encode … ordinary
  workplace `GDZIE` as a verb pattern," while the `nad + Instrumental`
  production sense **is** authored.

`uczyć` sense 2 differs from `zapraszać` only in that its unrepresentable
position sits **inside** a schema that also has representable positions, rather
than in a schema of its own. The `pracować` and `czytać` precedents cover
exactly that case: the representable core is authored, the generalized position
is documented and left unrepresented. **No HOLD arises.**

## 13. RelationType / role representability audit

Locked vocabularies (read-only, from `priority7_tooling.py:45–64`):
`relationType` ∈ {`lexical-frame`, `constructional-frame`, `means-method`,
`subject-experiencer`}; `role` ∈ {`subject`, `object`, `recipient`,
`experiencer`, `predicate`, `content`, `topic`, `interlocutor`, `means`,
`target`}.

Every Batch 7 row uses `relationType: lexical-frame`. No row is a
`constructional-frame` (no Nominative predicate), no row is
`subject-experiencer` (no row has both `subject` and `experiencer`), and no row
is `means-method` — see §13.1.

| Lemma / position | Proposed role | Warrant / precedent | Alternatives considered and rejected |
|---|---|---|---|
| `musieć` infinitive | `content` | Live `móc` A1/B1 infinitive `role=content`; canonical `lubić` `infinitive-activity`, `uczyć się` `infinitive-skill` | — |
| `wiedzieć` Accusative known content | `content` | Canonical `mówić` `dative-recipient-accusative-content` uses `case:accusative role=content` for nominal content alternating with a `że` clause | `object` — rejected: the source labels it "known **content**", and it alternates with clause content |
| `wiedzieć` `o + Locative` topic | `topic` | Canonical `o-locative-topic`; live staging `o+locative role=topic` ×11 | — |
| `wiedzieć` / `uczyć` clause content | `content` | Every live `ze`/`interrogative` clause complement in staging uses `role=content` (16 + 12 occurrences) | — |
| `jeść` Accusative food | `object` | Live `case:accusative role=object` ×45 | — |
| `jeść` Instrumental implement/means | `means` | **See §13.1** | `object`, `target` — rejected as less faithful to "eating implement/means" |
| `pić` Accusative drink | `object` | as above | — |
| `kochać` Accusative (all three meanings) | `object` | Canonical `lubić` `accusative-object`, `znać` `accusative-object` | `experiencer`/`topic` — rejected: the loved entity is the object of the emotion verb, and `subject-experiencer` is not licensed |
| `kochać` infinitive activity | `content` | Canonical `lubić` `infinitive-activity` `role=content` | — |
| `przepraszać` Accusative person | `interlocutor` | **See §13.3** | `object`, `recipient` |
| `przepraszać` `za + Accusative` offence | `topic` | Canonical `dziękować` `za-accusative-reason` and `dative-recipient-za-accusative` both use `za+accusative role=topic` for the reason of a thanking speech act — the closest released twin of an apology reason | `target` — rejected: live `za+accusative role=target` (×4, `kupować`/`kupić`/`brać`) is the **price/exchange** relation, semantically wrong here |
| `życzyć` Dative recipient | `recipient` | Live `case:dative role=recipient` ×40 | — |
| `życzyć` Genitive wished content | `content` | Alternates with the `żeby` content clause in the same slot; canonical `uczyć się` `genitive-subject-matter` uses `case:genitive role=content` | `object` — rejected: live `case:genitive role=object` (`wymagać`, `unikać`, `próbować`) is a demanded/avoided **entity**, not content alternating with a clause |
| `korzystać` `z + Genitive` (both meanings) | `object` | **See §13.2** | `means`, `topic`, `target` |
| `uczyć` Accusative learner/entity | `object` | **See §13.3** | `interlocutor`, `recipient` |
| `uczyć` Genitive taught content / school subject | `content` | Released canonical `uczyć się`'s `genitive-subject-matter` uses `role=content` for the same semantic position (subject matter) | `object` — rejected as above |
| `uczyć` infinitive taught skill | `content` | Canonical `uczyć się` `infinitive-skill` `role=content` | — |
| `uczyć` `o + Locative` taught topic | `topic` | Canonical `o-locative-topic`; live ×11 | — |

**No role was invented.** Every value above is a member of the locked enum and
every choice is anchored to released canonical or live staging precedent.

### 13.1 `jeść` Instrumental — role `means` under `lexical-frame`

This was the brief's first named HOLD candidate. It resolves **without** a
HOLD, on exact precedent:

- Live staging `brać` / `wziąć` pattern
  `accusative-entity-optional-instrumental-means` is
  `relationType: lexical-frame` with complements
  `[case:accusative required=true role=object,
  case:instrumental required=false role=means]` — a required/optional
  object-plus-implement frame with the implement as `means` under
  `lexical-frame`. `jeść` A1 is the same construction with the object also
  optional.
- The role-vocabulary fit is exact: the source position is `CZYM`, glossed by
  the frozen evidence as "eating **implement/means**".
- `relationType: means-method` is **not** used. The engine requires a `means`
  role for `means-method` (`priority7_tooling.py:1428–1433`), but the converse
  does not hold: a `means` role does **not** require `means-method`, as
  `brać`/`wziąć` prove live. `means-method` in both corpora marks frames whose
  *defining* complement is the means (canonical `płacić` `instrumental-method`;
  live `jechać`/`jeździć`/`dojechać` vehicle frames). Consumption is not a
  method relation, and the Accusative food object is the frame's primary
  position. `lexical-frame` is therefore the faithful relation.

No governed fallback is needed and no invention occurs. **Resolved.**

### 13.2 `korzystać` — role `object` for both meanings

This was the brief's second named HOLD candidate. It resolves **without** a
HOLD:

- The closest released analogue is canonical `używać` (`use`), whose
  `internalScope` reads "Employing a thing as a tool or means to do something"
  and whose complement is nevertheless `case:genitive required=true
  **role=object**`. The released corpus therefore already decides that the
  *thing used* is an `object`, **not** a `means`, even when the gloss says
  "tool or means".
- `means` is additionally rejected because it would invite the `means-method`
  relation reading and because, per §13.1, `means` marks the instrument of a
  distinct action, not the verb's own complement.
- `topic` is rejected: in both corpora `topic` marks "about"-relations and
  emotion causes (`pytać o`, `myśleć o`, `dziękować za`, `cieszyć się z`), not
  a resource one draws on.
- `target` is rejected: it marks goals, destinations, and endpoints.

**Both meanings take the same role.** Assigning different roles to A1 and B1
purely to make them structurally distinguishable would encode a distinction the
locked enum does not have and would misrepresent the benefit sense as a
"topic". The frozen evidence states the two senses share "the same exact
`z + Genitive` form"; the product mirrors that, and the semantic split is
carried by the meaning keys and editorial fields (§8 Family 2, §17 item 2).
**Resolved.**

### 13.3 Accusative persons — why `uczyć` uses `object` and `przepraszać` uses `interlocutor`

The role enum has no `learner` or `addressee` value, so both choices are
approximations; each is anchored to precedent rather than taste.

- **`uczyć` → `object`.** The source position is `KOGO/**CO**` in four of the
  five sense-1 rows and in sense 2: it may be a **non-person entity**, which
  `interlocutor` (a party in a verbal exchange, in both corpora) cannot
  describe. `object` covers person and entity alike, and live `zapraszać`
  already uses `case:accusative role=object` for an Accusative person. One role
  is used across all six `uczyć` rows, including A5's `KOGO`-only row, so the
  learner participant is represented consistently; A5's person restriction is
  carried in `internalScope`, not in the role.
- **`przepraszać` → `interlocutor`.** The position is `KOGO` only — always a
  person — and the schema is *Accusative person + prepositional content of a
  speech act*, which is structurally and semantically the released
  `prosić` (`accusative-person-o-accusative-thing`) and `pytać`
  (`accusative-person-o-accusative-topic`) construction; both use
  `case:accusative role=**interlocutor**`. An apology is that same
  person-addressed speech act.
- **Recorded for review.** A reviewer may reasonably prefer `object` for
  `przepraszać` on the live `zapraszać` precedent instead. The alternative is
  recorded here explicitly so the choice is adjudicated rather than inherited;
  it changes no requiredness, no meaning, and no pattern count, and either
  value is inside the locked enum. This is a **review item, not a HOLD**,
  because neither value misrepresents the frozen evidence.

### 13.4 Structural probe

All eight distinct Batch 7 complement shapes were probed read-only against the
live locked validator (§21.1). Each returned only the unrelated future-batch
boundary issue, identical to the control — including the two shapes with no
prior precedent in the exact type/role combination
(`preposition-case z+genitive role=object`, `case:accusative role=content` on a
Batch 7 record). No role/type/relation combination proposed here is rejected by
the locked model.

## 14. Cross-lemma independence audit

| Risk | Decision | Enforcement |
|---|---|---|
| **A. `musieć` / `móc` (Batch 6) modal normalization** | **NO TRANSFER.** `móc` has two meanings (ability, permission), `musieć` one. `móc` folds its question-use sense into `permission` as pragmatic packaging; `musieć` folds nothing — its zero-subject schema is realization, not sense. The two lemmas are not harmonized into a shared "modal + infinitive" template. | Guard A; frozen guards T/U on `móc`. |
| **B. `jeść` / `pić` consumption normalization** | **NOT normalized.** `jeść` has an all-optional object plus an optional Instrumental implement; `pić` has a single required Accusative and **no** Instrumental. The asymmetry is exactly what the two sources say and is preserved. | Guards D, F. Guard D pins two optional complements; guard F pins one required complement, so neither can drift toward the other. |
| **C. `jeść` / `brać`,`wziąć` (Batch 4) instrumental means** | **Convergent, not donated.** Both use `case:instrumental role=means` under `lexical-frame`, each from its own exact `CZYM`/means evidence. `brać`/`wziąć` additionally carry `requiredLexicalItems: ["udział"]` and a participation meaning that `jeść` must never acquire. | Validator `requiredLexicalItems` allowlist; guard D. |
| **D. `kochać` / released `lubić`** | **NO TRANSFER.** `lubić` is already released with `accusative-object` + `infinitive-activity` under one meaning. `kochać` sense 3 has the same shape pair from `WSJP-KOCH-03` alone. Product overlap is not linguistic donation, and `kochać`'s three-meaning split must not be flattened toward `lubić`'s single meaning. | Guard H (`exactMeaningSet: true`, three keys). |
| **E. `wiedzieć` / released `znać`; `wiedzieć` / `rozumieć`,`pamiętać`,`zapominać`** | **NO TRANSFER.** `znać` (acquaintance) is a different released lemma with a different scope; `rozumieć`/`pamiętać`/`zapominać` are separately authored Batch 2/5 records. Shared clause kinds are independently sourced convergence. `wiedzieć` gets **no `czy` complement**: its own frozen source is interrogative-dependent, so `interrogative` is the only mapping. Live staging's `clauseKind: czy` on already-frozen `zapominać` is a prior-batch authoring state outside Batch 7 scope (§11) and is not precedent here. | Guards B, C. |
| **F. `przepraszać` / `dziękować` (released) and `zapraszać` (Batch 6)** | **NO TRANSFER.** `dziękować` supplies role convention only (§13); its **Dative** person is not imported into `przepraszać`, which has an Accusative person. `zapraszać`'s `na`/`do` positions are not imported. | Guards I, J. Guard J's allowlist contains only `za+accusative`. |
| **G. `życzyć` / `życzyć sobie`** | **STRICT SEPARATION.** See §10. | Rule-target identity check; guard K; editorial fields; review. |
| **H. `uczyć` / `uczyć się` (released canonical)** | **STRICT SEPARATION.** See §10. Nothing is inherited in either direction; the released `uczyć się` record's own scope note already asserts the boundary. | Rule-target identity check; guard N (every authorized `uczyć` row carries the Accusative learner, which `uczyć się` never has); validator `requiredLexicalItems` allowlist; editorial fields; review. |
| **I. `uczyć` / `radzić`,`polecać` (Batch 6) instruction semantics** | **NO TRANSFER.** Similar didactic/directive semantics do not license schema transfer. `radzić`/`polecać` take a **Dative** advisee/recipient; `uczyć` takes an **Accusative** learner. `uczyć` has **no** `żeby` and **no** direct speech; `radzić`/`polecać` do. | Guard N. |
| **J. `korzystać` / released `używać`** | **NO TRANSFER.** `używać` selects a **direct** Genitive; `korzystać` selects `z + Genitive`. Role convention is shared (§13.2); government is not. | Guards L, M. |
| **K. Aspect partners** | **None exist.** All nine Batch 7 records have an empty `aspect_partner` in the freeze, so no syntax can travel an aspect relation into or out of this batch. | Frozen 68 intake boundary. |

## 15. Explicit exclusions (consolidated)

| Lemma | Excluded |
|---|---|
| `musieć` | second infinitive pattern for the zero-subject schema; subject complement; impersonal complement; question complement; second meaning; advice/expectation/criticism/elliptical discourse meanings; obligation source, deadline, reason, time, place, circumstances as complements |
| `wiedzieć` | `od + Genitive`; `z + Genitive`; any other source preposition; any `SKĄD` type or complement; separate `czy` type/pattern; cumulative merger of the four alternatives; "interchangeable" glossing; `znać` acquaintance syntax; time, place, degree, manner, circumstances |
| `jeść` | **`jeść` + Genitive in any form** (negation-driven or partitive); promotion of Accusative to required; promotion of Instrumental to required; splitting the pair into two patterns; standalone implement row; meal/diet/figurative and all other senses; place, time, meal occasion, frequency, quantity, manner, companions, food source |
| `pić` | Genitive; partitive Genitive; quantity-derived Genitive; container, source, quantity, temperature, occasion complements; alcohol-use meaning; plant-absorption, footwear and figurative senses; place, time, frequency, manner, company |
| `kochać` | flattening the three meanings to one generic "love + Accusative"; infinitive under `person-love` or `idea-or-place-attachment`; a fourth meaning; `za`, `z`, `do` collocations as frames; reason, duration, degree, reciprocity, manner, time, place, comparison |
| `przepraszać` | combined `za`-reason + `że`-clause pattern; optional person in A1; required person in A2; reason adjunct pattern built from ordinary context; standalone person row; `żeby`/interrogative/direct-speech clauses; the separate frozen form `przepraszam` and discourse-marker uses; manner, intensity, time, place, channel, subsequent repair |
| `życzyć` | combined Genitive + `żeby` pattern; infinitive; standalone recipient row; optionalization of Dative or content; **any syntax, semantics, or example material from `życzyć sobie`**; request/formal-demand uses; occasion, time, manner, intensity, medium, ceremony |
| `korzystać` | merging the two meanings into one generic "use" meaning; any preposition other than `z`; direct Genitive imported from `używać`; place, provider, availability, purpose, frequency, duration, manner, result |
| `uczyć` | maximal frame merging Genitive/infinitive/clause/`o + Locative`; **any concrete place form derived from `GDZIE`** (`w`, `na`, `u`, …); place complement type; standalone learner row; standalone content row; optionalization of any sense-1 complement; promotion of the sense-2 learner to required; **any evidence, complement, role, key, or example material from `uczyć się`**; `żeby` and direct-speech clauses; time, duration, manner, institution, frequency, method, purpose, ordinary location |

## 16. Proposed live guards (NOT implemented in this task)

`tests/fixtures/priority8_phase4b_authoring_rules.json` is **unchanged** by
this task and remains byte-identical at
`a6d696414b35f68a0b69251841e145f000d8c5dd46efc07b3fc61bb69158815d` (57 rules,
`registryVersion: 2`). Presence-asserting rules
(`require-exact-pattern-shapes`) must land in the same commit as the
`candidateContent` they protect, per the test-lifecycle rule; the
absence/prohibition rules (E, G) may land earlier. All proposals below use
**existing** primitives; **no new primitive is required** and the guard
interpreter is not modified.

| Ref | Proposed rule ID | Target | Primitive | Purpose |
|---|---|---|---|---|
| A | `p8-4b-musiec-exact-pattern-shapes` | `musieć` (62) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; one meaning `necessity-obligation`, exactly one infinitive shape. Because multiset equality is exact, this blocks a second (impersonal) meaning, a duplicate zero-subject pattern, and **any** added complement — subject, impersonal, or question. |
| B | `p8-4b-wiedziec-exact-pattern-shapes` | `wiedzieć` (63) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; one meaning, exactly four single-complement shapes. Blocks cumulative mergers, a fifth alternative, a separate `czy` pattern, and any `SKĄD` complement. |
| C | `p8-4b-wiedziec-authorized-preposition-cases` | `wiedzieć` (63) | `allow-only-preposition-case-signatures` | Allowlist exactly `o+locative role=topic required=true`. **This is the anti-concretization control for generalized `SKĄD`**: no `od`, `z`, `spod`, or other source preposition can ever be introduced. |
| D | `p8-4b-jesc-exact-pattern-shapes` | `jeść` (64) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; one meaning, one shape with **both complements `required: false`**. Structurally blocks promoting either to required, splitting the pair, adding a standalone implement row, adding a Genitive, and adding a second meaning. |
| E | `p8-4b-jesc-no-lexical-genitive` | `jeść` (64) | `forbid-complement-match` | Signature `{type: case, case: genitive}`. Explicit, legible protection of the grammar-owned-negation boundary, independent of D, so the rule survives any future legitimate revision of the shape set. See §9. |
| F | `p8-4b-pic-exact-pattern-shapes` | `pić` (65) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; one meaning, one required-Accusative shape. Blocks alcohol-use/figurative meanings and any added complement. |
| G | `p8-4b-pic-no-lexical-genitive` | `pić` (65) | `forbid-complement-match` | Signature `{type: case, case: genitive}`. Blocks partitive/quantity-derived Genitive inference. Same rationale as E; **not** a quantity guard — no quantity rule is proposed, per §22 of the brief. |
| H | `p8-4b-kochac-exact-pattern-shapes` | `kochać` (66) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; **three** meanings with 1 / 1 / 2 shapes. **This is the meaning-ownership control**: it pins the three-key inventory and confines the infinitive to `strong-liking`. It cannot separate the three identical Accusative rows semantically — see §17 item 1. |
| I | `p8-4b-przepraszac-exact-pattern-shapes` | `przepraszać` (67) | `require-exact-pattern-shapes` | One meaning, exactly two shapes, **pinning the person requiredness asymmetry structurally**: `required: true` in the `za` shape, `required: false` in the `że` shape. Any normalization in either direction breaks multiset equality. Also blocks a combined `za` + `że` frame and a standalone person row. |
| J | `p8-4b-przepraszac-authorized-preposition-cases` | `przepraszać` (67) | `allow-only-preposition-case-signatures` | Allowlist exactly `za+accusative role=topic required=true`. Blocks importing `o + Accusative`, `do + Genitive`, or any other preposition, and blocks the price/exchange `za+accusative role=target` signature. |
| K | `p8-4b-zyczyc-exact-pattern-shapes` | `życzyć` (68) | `require-exact-pattern-shapes` | One meaning, exactly two two-complement shapes. Blocks a cumulative Genitive + `żeby` frame, an infinitive shape, a standalone recipient row, and optionalization of either position. Its `verificationOrder: 68` + `lemma: "życzyć"` targeting also structurally pins the canonical identity against a rename to `życzyć sobie` (§10.1). |
| L | `p8-4b-korzystac-exact-pattern-shapes` | `korzystać` (69) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; **two** meanings, one shape each. Pins the two-key inventory against merger into one generic "use" meaning. It cannot verify which semantics sits under which key — see §17 item 2. |
| M | `p8-4b-korzystac-authorized-preposition-cases` | `korzystać` (69) | `allow-only-preposition-case-signatures` | Allowlist exactly `z+genitive role=object required=true`. Signature exclusion: blocks any other preposition and any direct-Genitive drift toward `używać`. |
| N | `p8-4b-uczyc-exact-pattern-shapes` | `uczyć` (70) | `require-exact-pattern-shapes` | `exactMeaningSet: true`; two meanings with **5** and **1** shapes. Blocks every maximal frame (a merged Genitive+infinitive+clause row is not in the multiset), a standalone learner or content row, optionalization of any sense-1 complement, promotion of the sense-2 learner, a `GDZIE`-derived place row, and — because every authorized row carries the Accusative learner — the bare `uczyć się` shapes. |
| O | `p8-4b-uczyc-authorized-preposition-cases` | `uczyć` (70) | `allow-only-preposition-case-signatures` | Allowlist exactly `o+locative role=topic required=true`. **This is the anti-concretization control for generalized `GDZIE`**: no `w`, `na`, `u`, or other place preposition can ever be introduced. |

**Fifteen proposed rules**, all existing primitives, all lemma-scoped.
Combined with the live 57 this would give 72 rules at Batch 7 authoring time.

### 16.1 Guard-engine notes

- **Every `allow-only-…` allowlist must list every distinct signature with its
  exact `required` and `role`**, because the interpreter tests
  `complement == signature` — exact object equality. Each of C, J, M and O
  needs exactly **one** entry here, because each lemma has exactly one distinct
  preposition-case signature. (`korzystać` A1 and B1 are the *same* signature,
  so one entry covers both meanings.)
- **A lemma-wide preposition allowlist is NOT meaning-placement protection.**
  Carried forward from the Batch 5 M/N lesson and Batch 6 §14.1:
  `require-exact-pattern-shapes` supplies **meaning ownership**;
  `allow-only-preposition-case-signatures` supplies **signature exclusion**
  only. C, J, M and O are proposed as companions to B, I, L and N, never as
  substitutes.
- **Where a lemma has no preposition-case complement at all**, an allowlist is
  not legal (`allowedSignatures` requires ≥1 entry). `musieć`, `jeść`, `pić`,
  `kochać` and `życzyć` therefore receive none; where a specific prohibited
  signature exists (`jeść`/`pić` Genitive), a `forbid-complement-match` rule is
  proposed instead. This mirrors the frozen `p8-4b-radzic-no-z-instrumental-coping`
  reasoning.
- **No `require-lexical-identity` rule is proposed for Batch 7.** The primitive
  asserts that the canonical lemma *contains* given material; every Batch 7
  lemma is bare, so such a rule would be a tautology adding no invariant beyond
  the target-equality check that any rule already performs (§10.1). Proposing
  one would be guard proliferation without an additional invariant.
- **No `require-lexical-material-in-explanation` rule is proposed.** No Batch 7
  pattern has required lexical material.
- **Configuration validity checked.** All 15 proposed rules were validated
  read-only in memory against the live
  `validate_rule_registry` implementation, alone (15 rules) and merged with the
  live registry (72 rules, unique IDs): both **VALID**. The fixture file was
  not written and its SHA-256 is unchanged (§21.1).

## 17. Guard non-enforceable semantic facts

Stated explicitly rather than papered over. Each of these is a real invariant
with **no** structural expression in the locked model; each must be carried by
`internalScope`, `glossesEn`, `learnerExplanationEn`, examples, and independent
authoring review.

1. **`kochać`'s three-way sense split is not structurally enforceable.** A1,
   B1 and C1 are the identical multiset
   `[case:accusative required=true role=object]`. Guard H pins the three-key
   inventory and each key's shape count but cannot verify that person-love
   semantics sits under `person-love`. A three-way swap would be structurally
   invisible. This is not a guard defect: the complement structures genuinely
   are identical, so no additional structural rule could separate them without
   inventing a schema field that does not exist.
2. **`korzystać`'s resource-use versus benefit-from split is not structurally
   enforceable.** A1 and B1 are the identical multiset
   `[preposition-case z+genitive required=true role=object]`, deliberately so,
   because the frozen evidence says the form is the same. Guard L pins the
   two-key inventory; nothing structural proves the attachment.
3. **The `życzyć` / `życzyć sobie` boundary is only partly enforceable.**
   Enforceable: record 68's canonical identity cannot be renamed while any rule
   targets it (§10.1), and `sobie` cannot become structural
   `requiredLexicalItems`. **Not** enforceable: no primitive reads example
   text, so nothing structural prevents a future `życzyć` example sentence from
   containing `sobie`, and `require-lexical-identity` cannot express a
   prohibition. Editorial and review control only.
4. **The `uczyć` / `uczyć się` boundary is only partly enforceable.**
   Enforceable: the canonical identity (§10.1) and the fact that every
   authorized `uczyć` shape carries an Accusative learner, which makes the bare
   released `uczyć się` shapes unauthorable (§10.1). **Not** enforceable:
   future example-token lexical identity — no guard can inspect whether an
   example sentence contains `się`. Editorial and review control only.
5. **`musieć`'s personal versus zero-subject realization is not
   representable.** The locked model has no subject field for a
   `lexical-frame`, and the contrast is deliberately unencoded. Guard A can
   forbid a subject complement; it cannot assert that the contrast *exists* and
   is intentionally carried in prose.
6. **`wiedzieć`'s optional `SKĄD` and `uczyć`'s sense-2 `GDZIE` cannot be
   asserted-as-omitted.** Guards C and O can forbid every *wrong*
   concretization; no primitive can record that a verified generalized position
   was deliberately left unrepresented. That fact lives in §12, in
   `internalScope` planning, and in this matrix.
7. **`wiedzieć`'s and `uczyć`'s `czy`-as-realization status is documentation,
   not structure.** Guards B and N forbid a `czy` complement by multiset
   exactness, but nothing structural records *why* — that `czy` is one
   realization of the interrogative-dependent clause rather than a missing
   type.
8. **`pić`'s animate-subject restriction is not expressible.** There is no
   selectional-restriction field; it lives in `internalScope`.
9. **`uczyć` A5's `KOGO`-only (person) restriction is not expressible.** A1–A4
   and B1 allow `KOGO/CO`; A5 allows `KOGO` alone. `role: object` is used
   throughout and the restriction lives in `internalScope`.
10. **`jeść`'s grammar-owned-negation boundary is enforceable only
    negatively.** Guards D and E can prevent a Genitive complement from being
    authored; no structure can assert the positive fact that Genitive under
    negation *is* correct Polish and is owned by sentence grammar. That framing
    must be preserved in prose (§9) so no report or guard message is ever read
    as claiming the Genitive is bad Polish.
11. **"This is exact source syntax, not a narrowed realization" is
    documentation, not structure.** Guards pin which signatures may appear; the
    epistemic label lives in this matrix, `internalScope`, and review.

## 18. Candidate-key audit

Every proposed key is lowercase kebab-case matching
`^[a-z0-9]+(?:-[a-z0-9]+)*$`, semantic, durable, and sibling-unique in its
locked scope. **No key** is derived from verification order, batch number,
array position, a source key (`WSJP-*`), example wording, or a production
`vp-*` ID. No numbered `sense-1` / `sense-2` / `sense-3` key is used anywhere.

| Lemma | Meaning keys | Pattern keys (per meaning) |
|---|---|---|
| `musieć` | `necessity-obligation` | `infinitive-required-action` |
| `wiedzieć` | `factual-knowledge` | `accusative-known-content`; `o-locative-known-topic`; `ze-known-proposition`; `interrogative-queried-content` |
| `jeść` | `food-consumption` | `accusative-food-instrumental-implement` |
| `pić` | `liquid-consumption` | `accusative-drink-object` |
| `kochać` | `person-love`; `idea-or-place-attachment`; `strong-liking` | `accusative-loved-person` / `accusative-cherished-idea-or-place` / (`accusative-strongly-liked-thing`, `infinitive-strongly-liked-activity`) |
| `przepraszać` | `apology` | `accusative-person-za-accusative-offence`; `accusative-person-ze-explanation` |
| `życzyć` | `good-wishes` | `dative-recipient-genitive-wished-thing`; `dative-recipient-zeby-wished-event` |
| `korzystać` | `resource-use`; `benefit-from-advantage` | `z-genitive-used-resource` / `z-genitive-source-of-benefit` |
| `uczyć` | `teaching-instruction`; `school-subject-teaching` | `accusative-learner-genitive-taught-content`; `accusative-learner-infinitive-taught-skill`; `accusative-learner-ze-taught-proposition`; `accusative-learner-interrogative-taught-content`; `accusative-person-o-locative-taught-topic` / `accusative-learner-genitive-school-subject` |

**Semantic meaning keys where the brief requires them.** `kochać` →
`person-love`, `idea-or-place-attachment`, `strong-liking`; `korzystać` →
`resource-use`, `benefit-from-advantage`; `uczyć` → `teaching-instruction`,
`school-subject-teaching`. Each names the semantics, not an ordinal.

**Uniqueness.** Meaning keys are unique within their lemma (13 keys across 9
lemmas, no intra-lemma repeat). Pattern keys are unique within
`(lemma, meaningKeyRef)`: the only lemma with two patterns under one meaning
besides `wiedzieć`, `przepraszać`, `życzyć` and `uczyć` is `kochać`'s
`strong-liking`, whose two keys differ. No cross-lemma collision matters, and
none of the 23 keys duplicates a live staging key in a way that could confuse
ownership resolution, which is performed inside one lemma only.

**Durability check.** Each pattern key names the complement inventory and its
semantic relation, so it survives re-ordering, re-batching, and example
rewrites. Each meaning key names the sense, so it survives CEFR, teaching
status, and usage decisions — none of which is made here.

## 19. HOLD history and status

**HOLD count: 0.**

Four HOLD candidates were named in the brief and each was investigated rather
than assumed away. All four **resolved** on repository evidence:

| # | Candidate | Investigation | Outcome |
|---:|---|---|---|
| 1 | `jeść` Instrumental role mapping | Locked enum contains `means`; live `brać`/`wziąć` `accusative-entity-optional-instrumental-means` proves `role: means` under `relationType: lexical-frame`; `means-method` correctly rejected because it marks means-defined frames only, and the engine's constraint is one-directional | **RESOLVED** — §13.1. No invention, no governed fallback needed. |
| 2 | `korzystać` semantic-role mapping | Released canonical `używać` ("Employing a thing as a tool or means") uses `role: object`; `means`, `topic`, `target` each rejected on precedent | **RESOLVED** — §13.2. Both meanings take `object`; the semantic split is editorial by design, exactly as the frozen evidence describes. |
| 3 | `uczyć` sense-2 `GDZIE` omission with retained core | Precedent independently verified against `zapraszać` (Batch 6), `czytać` (Batch 4), `umówić się` (Batch 5) and the live `pracować` binding constraint — all retain a representable core and leave a generalized position unrepresented | **RESOLVED** — §12. |
| 4 | Lexical-identity enforcement limits for `życzyć`/`życzyć sobie` and `uczyć`/`uczyć się` | Guard engine read directly: rule-target identity equality **is** enforced; example tokens are **not** inspectable; `require-lexical-identity` is inclusion-only | **RESOLVED** — §10. A guard limitation that is faithfully documented is not a HOLD; the candidate structure misrepresents nothing. |

No proposed candidate structure misrepresents frozen evidence, so no HOLD is
created. Per §25 of the brief, a semantically rich fact that can be carried
faithfully in `internalScope` is **not** a HOLD; every unrepresentable fact in
this batch is recorded in §12 or §17 rather than encoded.

One item is recorded as a **review item, not a HOLD**: the `przepraszać`
Accusative-person role (`interlocutor` proposed, `object` recorded as the
alternative) — §13.3. Both values are inside the locked enum, neither changes
requiredness, meaning count, or pattern count, and neither misrepresents the
source.

## 20. Final reconciliation counts

Counted independently from the matrix rows above, not prescribed in advance.

| Quantity | Count |
|---|---:|
| Lemmas | **9** |
| Meanings | **13** |
| Product schemas (patterns) | **23** |
| All-optional schemas | **1** |
| HOLDs | **0** |
| Same-shape cross-meaning families | **2** |
| Verified-but-unrepresented generalized roles | **2** |
| Multi-complement rows | 11 |
| Single-complement rows | 12 |
| Clause-bearing rows | 6 |
| Proposed live guards | 15 |
| Candidate meaning keys | 13 |
| Candidate pattern keys | 23 |

Per-lemma:

| Order | Lemma | Meanings | Schemas | All-optional | Clause rows |
|---|---|---:|---:|---:|---:|
| 62 | `musieć` | 1 | 1 | 0 | 0 |
| 63 | `wiedzieć` | 1 | 4 | 0 | 2 |
| 64 | `jeść` | 1 | 1 | **1** | 0 |
| 65 | `pić` | 1 | 1 | 0 | 0 |
| 66 | `kochać` | 3 | 4 | 0 | 0 |
| 67 | `przepraszać` | 1 | 2 | 0 | 1 |
| 68 | `życzyć` | 1 | 2 | 0 | 1 |
| 69 | `korzystać` | 2 | 2 | 0 | 0 |
| 70 | `uczyć` | 2 | 6 | 0 | 2 |
| — | **total** | **13** | **23** | **1** | **6** |

Cross-checks: 1+1+1+1+3+1+1+2+2 = 13 meanings ✓. 1+4+1+1+4+2+2+2+6 = 23
schemas ✓. Every meaning owns at least one pattern ✓ (locked cardinality rule).
11 multi-complement + 12 single-complement = 23 ✓. Clause rows: `wiedzieć` A3,
A4; `przepraszać` A2; `życzyć` A2; `uczyć` A3, A4 = 6 ✓.

Projected staging state **after** a future Batch 7 authoring commit (for
planning only; nothing is authored here): 68 authored lemmas, 82 + 13 = **95**
meanings, 201 + 23 = **224** patterns, 0 future-empty, `phaseStep: 4B7`,
`stagingRevision: 8`.

### 20.1 Matrix self-audit

For every one of the 23 product rows:

| Check | Result |
|---|---|
| exact meaning owner declared | **pass** — every row names its `meaningKeyRef` owner |
| semantic durable keys | **pass** — §18; no ordinal, source, batch, or production key |
| requiredness exact | **pass** — §6; every value traced to parenthesisation |
| optionality exact | **pass** — §6, §7 |
| `relationType` valid | **pass** — all `lexical-frame`, a locked enum member; no row triggers the `means-method` or `subject-experiencer` obligations |
| `role` valid | **pass** — §13; all **six** role values used (`content`, `object`, `topic`, `interlocutor`, `recipient`, `means`) are among the **ten** locked enum members; none invented |
| `clauseKind` exact | **pass** — §11; `ze`/`zeby`/`interrogative` kept distinct, `czy` used nowhere, no direct speech |
| no maximal merger | **pass** — §4.1; `uczyć` and `wiedzieć` alternatives split, never combined |
| no generalized-role concretization | **pass** — §12; `SKĄD` and `GDZIE` receive no preposition and no row |
| no syntax inheritance | **pass** — §14; `uczyć się`, `życzyć sobie`, `lubić`, `używać`, `znać`, `radzić`, `polecać`, `móc` all excluded as donors |
| no grammar-owned negation leakage | **pass** — §9; no Genitive row for `jeść` or `pić` |
| explicit exclusions recorded | **pass** — §15, plus per-row exclusions in §4 |
| no production IDs | **pass** — no `vp-l-`, `vp-m-`, `vp-p-`, `vp-e-`, `vp-x-` value appears anywhere in this report |
| structurally valid under the locked validator | **pass** — §21.1 probe |

## 21. Content invariants

Exactly **one** repository path is added by this task:

- `reports/priority-8-phase-4b7-schema-matrix.md`

Proven unchanged (byte-identical to the starting HEAD):

- `editorial/priority-8-phase4-staging.json` —
  `9bd26dff88943a507b5ead9ce9e72ee8a3da2704193531296f74f4937a6462b3`
- `tests/fixtures/priority8_phase4b_authoring_rules.json` —
  `a6d696414b35f68a0b69251841e145f000d8c5dd46efc07b3fc61bb69158815d`
- `tests/test_priority8_phase4b_progress.py`,
  `tests/test_priority8_phase4b_authoring_guards.py`
- all historical Batch 1–6 tests
  (`tests/test_priority8_phase4b0_staging.py`,
  `…4b1a_authoring_schema.py`, `…4b1_batch01.py` … `…4b6_batch06.py`)
- all previous Phase 4B matrices and reports, including
  `reports/priority-8-phase-4b6-schema-matrix.md` —
  `72ab74094d67e4a6c944eaa5b421c2a8b7509ae4bd3b59e102a448fee364fe8c`
- all Phase 3 / Phase 3B files
- `validate_priority8_staging.py`, `priority7_tooling.py`, and every
  runtime / canonical / audio / product file

Staging remains `phaseStep: 4B6`, `stagingRevision: 7`, 59 authored, 82
meanings, 201 patterns, 201 examples, 9 future-empty. No `candidateContent` was
written, no example was created or searched for, no CEFR or `teachingStatus`
was assigned, no ID was allocated, and no guard, test, schema, or validator was
modified.

### 21.1 Read-only probes (no file written)

Two in-memory probes were run against the live locked code. Neither wrote any
repository file; both target SHA-256 values were identical before and after.

**Probe 1 — structural acceptability of the proposed shapes.** Eight distinct
Batch 7 complement shapes were installed on an in-memory copy of a future-batch
record and passed to `validate_priority8_staging.validate_data`:

| Probe shape | Result |
|---|---|
| `jeść` all-optional (accusative object + instrumental means, both optional) | 1 issue — the unrelated `future-batch lemma must remain empty` boundary |
| `korzystać` `z+genitive role=object required=true` | same 1 issue |
| `przepraszać` accusative `interlocutor` + `za`+accusative `topic` | same 1 issue |
| `życzyć` dative `recipient` + genitive `content` | same 1 issue |
| `uczyć` accusative `object` + genitive `content` | same 1 issue |
| `uczyć` accusative `object` + `o`+locative `topic` | same 1 issue |
| `wiedzieć` accusative `content` | same 1 issue |
| control: `pić` accusative `object` required | same 1 issue |

Every probe returned exactly the same single boundary issue as the control, so
**no proposed shape, role, case, preposition, clause kind, or requiredness
combination is rejected by the locked validator**. The boundary issue is
expected and correct: Batch 7 records must stay empty until authoring.

**Probe 2 — configuration validity of the 15 proposed guards.** The proposed
rules were built in memory and passed to the live
`validate_rule_registry`: **VALID** as a standalone 15-rule registry, and
**VALID** merged with the live 57 rules as a 72-rule registry with unique IDs.
The fixture file was neither read-modified nor written.

## 22. Test results

Run before and after writing this report; the report is the only changed path,
and it is not an input to any suite.

| Suite | Tests | Result |
|---|---:|---|
| `tests/test_priority8_phase4b0_staging.py` | 31 | OK |
| `tests/test_priority8_phase4b1a_authoring_schema.py` | 65 | OK |
| `tests/test_priority8_phase4b1_batch01.py` | 9 | OK |
| `tests/test_priority8_phase4b2_batch02.py` | 11 | OK |
| `tests/test_priority8_phase4b3_batch03.py` | 17 | OK |
| `tests/test_priority8_phase4b4_batch04.py` | 23 | OK |
| `tests/test_priority8_phase4b5_batch05.py` | 29 | OK |
| `tests/test_priority8_phase4b6_batch06.py` | 24 | OK |
| `tests/test_priority8_phase4b_progress.py` | 8 | OK |
| `tests/test_priority8_phase4b_authoring_guards.py` | 26 | OK |
| **combined single run** | **243** | **OK** |

`python3 validate_priority8_staging.py` →
`PASS: Priority 8 4B6 staging revision 7 is read-only valid (68 lemmas, 21
constrained records, 12 global constraints).`

The recomputed baseline equals the expected 243.

### 22.1 Phase 4C reconciliation items carried forward

1. Canonical example `origin`, pattern `evidence`, `activityEligibility`,
   `contentRefs`, and `audioEligible` remain Phase 4C responsibilities for all
   23 planned patterns.
2. The `uczyć` / `uczyć się` and `kochać` / `lubić` **product overlaps** with
   the released canonical corpus need a Phase 4C integration decision; they are
   not linguistic donations and do not affect this plan.
3. The absence of any pattern-level lexical-material field remains the open
   later schema question recorded in
   `reports/priority-8-phase-4b-authoring-guard-hardening.md`; Batch 7 needs no
   such field, since no Batch 7 pattern has required lexical material.
4. A structural representation for verified-but-unrepresented generalized
   positions (`SKĄD`, `GDZIE`, `KIEDY`, `DOKĄD`) remains unavailable by design;
   the two Batch 7 instances are documented in §12 and join the frozen
   `zapraszać` / `czytać` / `umówić się` set.
