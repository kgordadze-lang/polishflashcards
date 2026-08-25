# Priority 8 Phase 4B3 — Batch 03 authoring

## Scope and authority

This is private, ID-less staging authoring for exactly these ten frozen
full-pattern lemmas, in preserved order:

`próbować`, `pozwalać`, `unikać`, `wymagać`, `należeć`, `kłócić się`,
`pokazywać`, `radzić sobie`, `kupować`, and `kupić`.

Authoritative linguistic evidence used:

- `reports/priority-8-phase-3-batch-03.md` (orders 22–30)
- `reports/priority-8-phase-3-batch-03-risk-review.md`
- `reports/priority-8-phase-3-batch-03-verification.csv`
- `reports/priority-8-phase-3-batch-04.md` (order 31 `kupić`)
- `reports/priority-8-phase-3-batch-04-risk-review.md`
- `reports/priority-8-phase-3-batch-04-verification.csv`
- `reports/priority-8-phase-3-final-synthesis.md`
- `reports/priority-8-phase-3-final-synthesis-risk-review.md`
- `reports/priority-8-phase-3b-final-lemma-freeze.csv`
- `reports/priority-8-phase-3b-final-lemma-freeze.md`
- `reports/priority-8-phase-3b-phase4-handoff.md`
- `reports/priority-8-phase-3b-risk-review.md`

The Phase 4 policy, staging contract, B1A schema-lock report, test lifecycle
report, Batch 1/2 reports and tests as style precedent only, the live
staging validator, and the read-only canonical editorial corpus were also
consulted. No source was used to broaden the frozen construction inventory,
and no Batch 1/2 linguistic structure was copied onto a Batch 3 lemma merely
because a JSON shape resembled it.

## Authored records

### `próbować`

- Meanings: 2 — `attempt-action-result`, `taste-sample-food-drink`.
- Patterns: 3 — `infinitive` and `genitive-action-noun` (attempt, both
  active-production); `genitive-sampled-object` (taste, active-production).
- Examples: `Próbuję rozwiązać problem.` — "I'm trying to solve the
  problem."; `Próbuję szczęścia.` — "I'm trying my luck."; `Próbuję zupy.`
  — "I'm tasting the soup." All editorial-generated.
- Handling: the attempt-sense Genitive is a noun in Genitive
  (`genitive-action-noun`), never modeled as an infinitive. The two Genitive
  patterns share surface case but are attached to different meanings and
  are not merged.

### `pozwalać`

- Meanings: 2 — `human-permission`, `inanimate-enabling`.
- Patterns: 6 — `dative-na-accusative-permission` and
  `dative-zeby-permission` (optional Dative + required na/żeby), standalone
  `infinitive` (no Dative) under permission; `na-accusative-enabling`,
  standalone `infinitive`, and `zeby-enabling` (**recognition-only**) under
  enabling.
- Examples: `Mama pozwala mi na wyjście.`; `Mama pozwala, żeby dzieci
  oglądały bajki.`; `Pozwalam pracować z domu.`; `Internet pozwala na
  szybką komunikację.`; `Internet pozwala pracować zdalnie.`; `Prawo
  pozwala, żeby firmy stosowały ulgi.` All editorial-generated.
- Handling: Dative is structurally present only inside the `na`/`żeby`
  permission patterns' own complement lists; the standalone `infinitive`
  pattern (both meanings) has exactly one complement (the infinitive
  itself) and never a Dative. No Dative exists anywhere in the
  `inanimate-enabling` meaning. No syntax is borrowed from perfective
  `pozwolić`.

### `unikać`

- Meanings: 1 — `avoidance`.
- Patterns: 1 — `genitive-object`; active-production.
- Example: `Unikam słodyczy.` — "I avoid sweets." Editorial-generated.
- Handling: only direct Genitive is authored. No infinitive pattern exists
  anywhere in the record; the rejected Phase 2 infinitive hypothesis is not
  restored.

### `wymagać`

- Meanings: 2 — `person-requires-behavior`, `situation-requires-content`.
- Patterns: 4 — `genitive-required-content` and `zeby-clause` under each
  meaning (2 + 2). Each pattern carries the required Phase 3 core
  complement (Genitive content, or the `żeby` clause) plus an **optional**
  `od + Genitive` complement, matching the exact source schemas
  `(od KOGO) + CZEGO`, `(od KOGO) + żeby ZDANIE` (person-requires) and
  `(od KOGO/CZEGO) + CZEGO`, `(od KOGO/CZEGO) + żeby ZDANIE`
  (situation-requires). There is no standalone `od + Genitive` pattern:
  `od` never appears without its required Genitive or `żeby` co-complement,
  because no source schema licenses `od` alone. The situation-meaning's
  `zeby-clause` is **recognition-only**; the other three are
  active-production, unchanged from the original authoring pass.
- Examples: `Wymaga lojalności od pracowników.` (realizes the required
  Genitive together with the optional `od` participant); `Szef wymaga,
  żeby pracownicy przychodzili punktualnie.`; `Wyjście z nałogu wymaga
  silnej woli.` (repository-reuse, realizes the required Genitive alone,
  `od` unrealized since it is optional); `Sytuacja wymaga, żeby wszyscy
  zachowali spokój.`
- Handling: `od + Genitive` is optional inside each exact schema, never a
  required sole complement. The person-only restriction on `od + Genitive`
  under person-requires versus the broader person-or-thing restriction
  under situation-requires is recorded in each meaning's `internalScope`,
  since the architecture has no formal noun-class restriction mechanism.
  The two meanings are never merged despite sharing pattern keys and
  surface forms.

  **Correction note.** The original Batch 3 authoring pass incorrectly
  modeled `od + Genitive` as a third, standalone, required-sole-complement
  pattern (`od-genitive-required-from`) in each meaning, and omitted the
  optional `od` participant from both `zeby-clause` patterns. An
  independent review identified this as a schema-decomposition defect: no
  Phase 3 source schema licenses `wymagać` with only an `od + Genitive`
  phrase and no required core. This has been corrected as described above;
  the two invalid standalone patterns and their two now-superseded
  editorial-generated examples (`Szef wymaga lojalności.` and `Wymaga
  elastyczności od zespołu.`) were removed. `Wymaga lojalności od
  pracowników.`, which already correctly realized the required Genitive
  together with the optional `od` participant, was re-targeted onto the
  corrected `genitive-required-content` pattern for `person-requires-
  behavior` with its wording preserved exactly. The repository-reuse
  example for the situation meaning's Genitive pattern was kept unchanged
  to preserve its provenance.

### `należeć`

- Meanings: 2 — `ownership`, `organization-membership`.
- Patterns: 2 — `do-genitive-owner` (ownership), `do-genitive-organization`
  (organization-membership); both active-production.
- Examples: `Ten dom należy do sąsiadki.` — "This house belongs to my
  neighbor."; `Należę do klubu sportowego.` — "I belong to a sports club."
  Both editorial-generated.
- Handling: identical `do + Genitive` surface form is kept under two
  separately labelled meanings rather than one flattened "belong to"
  record. Category, relationship, obligation, `należeć się`, location,
  time, and manner are not imported. Example wording deliberately avoids
  the WSJP citation anchors ("samochód należy do ojca", "do partii") to
  avoid reproducing dictionary illustrations.

### `kłócić się`

- Meanings: 1 — `interpersonal-quarrelling`.
- Patterns: 4 — `z-instrumental-interlocutor`, `o-accusative-topic`,
  `ze-content-clause` (all active-production), `czy-dependent-clause`
  (**recognition-only**).
- Examples: `Kłócę się z bratem.`; `Kłócimy się o drobiazgi.`; `Kłócimy
  się, że nikt nie sprząta.`; `Kłócimy się, czy powinniśmy wyjechać.` All
  editorial-generated.
- Handling: the exact lexical identity `kłócić się` is preserved; nothing
  is transferred from non-reflexive `kłócić`. `że` and `czy` are modeled as
  alternatives to the nominal `o + Accusative` topic, not to the
  interlocutor. The plural-subject topic example (`Kłócimy się o
  drobiazgi.`) illustrates the evidence's noted plural/z-omission
  asymmetry without inventing a new complement type.

### `pokazywać`

- Meanings: 1 — `directing-attention-to-content`.
- Patterns: 3 — `dative-recipient-accusative-thing` (optional Dative +
  required Accusative, one combined pattern), `na-accusative-pointing`
  (exact, distinct construction), `interrogative-dependent-clause`; all
  active-production.
- Examples: `Pokazuję dzieciom zdjęcia.`; `Pokazuję na mapę.`; `Pokazuję,
  jak to zrobić.` All editorial-generated.
- Handling: optional selected `GDZIE` from the evidence is recorded in
  `internalScope` as selected semantic-role evidence only and is **not**
  concretized into any `w`/`na` + Locative or other location pattern. Exact
  `na + Accusative` (pointing) is kept distinct from the Dative+Accusative
  showing frame. No syntax is borrowed from `pokazać`.

### `radzić sobie`

- Meanings: 1 — `coping-with-difficulty`.
- Patterns: 1 — `z-instrumental-topic`; active-production.
- Example: `Radzę sobie z trudnościami.` — "I cope with difficulties."
  Editorial-generated.
- Handling: the complete lexical phrase `radzić sobie` is preserved as the
  `canonicalLemma`; `sobie` also appears explicitly in the example text. No
  syntax is borrowed from non-reflexive advice-sense `radzić`, which
  remains a separate full lemma elsewhere in the frozen 68.

### `kupować`

- Meanings: 1 — `process-purchase`.
- Patterns: 3 — `seller-price-schema` (Accusative + optional `od +
  Genitive` seller + optional `za + Accusative` price, combined),
  `dative-beneficiary-schema` (Accusative + optional Dative), and
  `dla-beneficiary-schema` (Accusative + optional `dla + Genitive`); all
  active-production.
- Examples: `Kupuję warzywa od rolnika za dziesięć złotych.`; `Kupuję
  dzieciom zabawki.`; `Kupuję zabawki dla dzieci.` All editorial-generated.
- Handling: the three schemas are kept as independent alternatives; no
  pattern requires or freely combines seller, price, Dative beneficiary,
  and `dla` beneficiary all together. Purchase location, channel,
  occasion, frequency, and manner remain outside the pattern inventory. No
  syntax is inherited from perfective `kupić`.

### `kupić`

- Meanings: 1 — `completed-purchase`.
- Patterns: 3 — the identical three schema shapes as `kupować`
  (`seller-price-schema`, `dative-beneficiary-schema`,
  `dla-beneficiary-schema`), independently authored from `kupić`'s own
  Phase 3 Batch 4 evidence; all active-production.
- Examples: `Kupię chleb od piekarza za pięć złotych.` (editorial-generated);
  `Kupiłem jej kwiaty.` (repository-reuse); `Kupiłem prezenty dla całej
  rodziny.` (repository-reuse).
- Handling: `kupić` and `kupować` are both retained as independent
  full-pattern records per the deliberate Phase 3B purchase-pair decision.
  Neither construction was copied from the other — each pattern was built
  from `kupić`'s own Batch 4 verification entry — and the two records use
  different example vocabulary throughout (bread/coat/daughter vs.
  vegetables/ticket/children) so the pair reads as independently authored
  rather than mechanically mirrored. The aspectual contrast (imperfective
  process/habitual buying vs. perfective bounded acquisition) is made
  visible through tense choice (`kupuję` present vs. `kupię`/`kupiłem`
  future/past) without inventing any syntactic difference between the two
  lemmas.

## Omitted verified constructions and rationale

None. Every clearly learner-relevant, directly verified, architecture-
compatible construction identified in the Phase 3 Batch 3/4 evidence for
these ten lemmas is authored somewhere in the record above (subject to the
completeness-rule exclusions Phase 3 itself already applied — e.g. the
rejected Dative-person for `pozwalać`'s infinitive, the rejected infinitive
for `unikać`, and the rejected żeby for none of these ten lemmas since no
żeby proposal was rejected for any Batch 3 lemma).

## Generalized-role note

Unlike Batches 1–2, no Batch 3 construction is a narrowed realization of
`DOKĄD`, `SKĄD`, `GDZIE`, or `KTÓRĘDY` — this matches the Phase 3 Batch 3
reconciliation statement exactly. Every authored complement is either an
exact schema-listed case/preposition-case position (e.g. `należeć`'s
`do + Genitive`, `kłócić się`'s `z + Instrumental`/`o + Accusative`,
`wymagać`'s `od + Genitive`) or a genuinely optional/alternative
elaboration (the `kupować`/`kupić` seller/price/beneficiary additions).
None of these needed the Batch 1/2-style "one common way, not the only
form" non-exclusivity hedge, because none of them narrow a generalized
motion/location role; learner wording instead uses "one way… another way"
phrasing only where Phase 3 itself frames the options as genuine
alternatives (e.g. Dative vs. `dla` beneficiary).

## Coverage, provenance, and totals

- Batch 3 totals: 14 meanings, 30 patterns, 30 examples.
- Cumulative Batch 1 + 2 + 3 totals: 38 meanings, 83 patterns, 83 examples,
  across 30 authored lemmas.
- Every authored pattern has exactly one candidate example.
- Teaching status: 27 active-production; 3 recognition-only
  (`pozwalać`/`zeby-enabling`, `wymagać`/`zeby-clause` under
  situation-requires, `kłócić się`/`czy-dependent-clause`).
  - **Recognition-only rationale.** All three exceptions share a genuine,
    independently-motivated pattern: an abstract/impersonal grammatical
    subject (a law, a policy, "the situation") combined with a `żeby`
    clause, or an embedded yes/no (`czy`) clause expressing uncertainty
    about a past fact. Both are directly verified constructions but are
    more realistically encountered in comprehension than produced by an
    A1–B1 learner; each is authored (not omitted) with CEFR recognition at
    B1 and no production CEFR value, per the validator's `recognition-only`
    rule.
  - **Active-production justification for the remaining 27.** Each
    represents a concrete, high-frequency valency construction (direct
    case objects, exact schema-listed prepositional positions, plain
    infinitives, human-subject `żeby`/`że` clauses, and the wh-word
    `interrogative` clause under `pokazywać`, which is common and practical
    at A2 — e.g. "Pokaż, jak to zrobić" is a textbook-level request).
    Productive use is realistic at each pattern's assigned CEFR.
- Provenance: 3 repository-reuse; 27 editorial-generated.
  - `wymagać` / `genitive-required-content` (situation-requires): reused
    `card:b1-healthy-lifestyle-018.ex` — "Wyjście z nałogu wymaga silnej
    woli."
  - `kupić` / `dative-beneficiary-schema`: reused
    `card:a2-nature-animals-016.ex` — "Kupiłem jej kwiaty."
  - `kupić` / `dla-beneficiary-schema`: reused
    `card:a2-holidays-traditions-007.ex` — "Kupiłem prezenty dla całej
    rodziny."
  - A repository search was conducted across `data-a1.js`, `data-a2.js`,
    `data-b1.js`, `data-grammar.js`, `data-scenarios.js`, and
    `data-podcasts.js` for each Batch 3 lemma's inflected forms. Notable
    rejected near-misses: `spróbuj`/`spróbuję` (perfective `spróbować`,
    wrong aspect for imperfective `próbować`); `pokłócić się`/
    `pokłóciliśmy się` (perfective aspect partner of `kłócić się`, wrong
    lemma); `radzić sobie ze stresem` embedded under "Muszę nauczyć się..."
    (not a standalone realization of `radzić sobie`'s own valency); `Nie
    będę kupować nowych ubrań` (negation-Genitive artifact, not the plain
    Accusative pattern); `kupować kota w worku` (idiomatic sense, not the
    literal purchase sense); several `kupić`/`kupować` card examples with
    unauthorized time/location/channel/occasion adjuncts (e.g. "w
    aplikacji", "na targu", "na wesele", "Latem…").

## Candidate keys

All meaning and pattern keys are durable semantic/construction identities
(e.g. `attempt-action-result`, `dative-na-accusative-permission`,
`seller-price-schema`), independent of batch number, verification order, or
example wording. Pattern-key reuse across meanings of the same lemma
(`infinitive` under both `pozwalać` meanings; `genitive-required-content`
and `zeby-clause` under both `wymagać` meanings; `seller-price-schema` etc.
shared between `kupować` and `kupić`) is sibling-scoped per the locked
architecture, matching Batch 1/2 precedent. All 30 `candidateExampleKey`
values use the durable slot name `primary`.

## Batch 3 digest

`8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb`

(Superseded corrected value. The original authoring-pass digest,
`160c25b9c9311eb97dd50faa2c5e8582243bb850b5b9afc14dee671c1363720d`, was
recomputed after the `wymagać` schema correction described above; see
`tests/test_priority8_phase4b3_batch03.py`.)

The digest projects verification orders 22–31 in staging order over
`verificationOrder`, `canonicalLemma`, `aspect`, `phase3Disposition`,
`phase3Evidence`, `bindingConstraints`, `candidateContent`, and
`metadataAspectPartner` (present on none of these ten lemmas), serialized as
UTF-8 JSON with sorted keys and compact separators before SHA-256 hashing,
following the same canonical-projection philosophy as the Batch 1/2
digests.

## Test results

```
python3 -m unittest tests.test_priority8_phase4b0_staging         # 31 tests, OK
python3 -m unittest tests.test_priority8_phase4b1a_authoring_schema   # 65 tests, OK
python3 -m unittest tests.test_priority8_phase4b1_batch01          # 9 tests, OK
python3 -m unittest tests.test_priority8_phase4b2_batch02          # 11 tests, OK
python3 -m unittest tests.test_priority8_phase4b3_batch03          # 17 tests, OK
python3 -m unittest tests.test_priority8_phase4b_progress          # 8 tests, OK
```

Combined: 141 tests, OK. (One additional dedicated test,
`test_wymagac_od_genitive_is_optional_not_standalone`, was added by the
`wymagać` correction; see `tests/test_priority8_phase4b3_batch03.py`.)

## Validator result

```
PASS: Priority 8 4B3 staging revision 4 is read-only valid (68 lemmas, 21 constrained records, 12 global constraints).
```

## Final reconciliation correction note (2026-08-25)

This labelled note preserves the historical Batch 3 account while recording
the later human-adjudicated Phase 4B reconciliation.

- `kłócić się/czy-dependent-clause` is superseded by
  `interrogative-disputed-content`; its clause kind is now `interrogative`
  and the dependent example reference was renamed in lockstep. HD-1 changes
  the row from B1/none recognition-only to A2/A2 active-production. The
  existing Polish `czy` sentence remains unchanged.
- `p8-4b-klocic-sie-exact-pattern-shapes` now protects the complete corrected
  family while the pre-existing lexical-identity guard continues to protect
  `się`.
- P8-SR-001 corrects the person-subject example to `Szef wymaga lojalności od
  pracowników.` / `The boss requires loyalty from employees.` The replacement
  remains `editorial-generated`: Layer A found zero matches in 1,665 indexed
  entities and Layer B found zero broad raw-text hits.
- Current Batch 3 status is 28 active-production / 2 recognition-only; the two
  retained rows are `pozwalać/inanimate-enabling/zeby-enabling` and
  `wymagać/situation-requires-content/zeby-clause`.
- Pre-reconciliation digest
  `8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb`
  is superseded by current digest
  `313b50ec3fe5a2764c4f477c0f47ceef7733cadade7c7b183350f335bcff7197`.

No source-oriented candidate key or coarse Phase 4B `target` role was changed.
