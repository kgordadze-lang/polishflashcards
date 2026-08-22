# Priority 8 Phase 4B2 — Batch 02 authoring

## Scope and authority

This is private, ID-less staging authoring for exactly these ten frozen
full-pattern lemmas, in preserved order:

`przyjechać`, `wyjść`, `wyjechać`, `przynosić`, `odpowiadać`, `zamawiać`,
`zacząć`, `kończyć`, `pamiętać`, and `zapominać`.

Verification order 17 (`zaczynać`) is not a full-pattern record. It remains
metadata-only under the existing private aspect relationship `zacząć ->
zaczynać`; no `candidateContent` was authored for it, and its identity is
absent from the 68 `canonicalLemma` names.

Authoritative linguistic evidence used:

- `reports/priority-8-phase-3-batch-02.md`
- `reports/priority-8-phase-3-batch-02-risk-review.md`
- `reports/priority-8-phase-3-batch-02-verification.csv`
- `reports/priority-8-phase-3-batch-03.md` (for `zapominać`, verification
  order 21)
- `reports/priority-8-phase-3-batch-03-risk-review.md`
- `reports/priority-8-phase-3-batch-03-verification.csv`
- `reports/priority-8-phase-3-final-synthesis.md`
- `reports/priority-8-phase-3-final-synthesis-risk-review.md`
- `reports/priority-8-phase-3b-final-lemma-freeze.csv`
- `reports/priority-8-phase-3b-final-lemma-freeze.md`
- `reports/priority-8-phase-3b-phase4-handoff.md`
- `reports/priority-8-phase-3b-risk-review.md`

The Phase 4 policy, staging contract, B0/B1A schema-lock reports, the test
lifecycle report, Batch 1's authoring/risk-review reports as style precedent
only, the live staging validator, and the read-only canonical editorial
corpus were also consulted. No source was used to broaden the frozen
construction inventory, and no Batch 1 linguistic structure was copied
across lemmas.

## Authored records

### `przyjechać`

- Meanings: 1 — `transport-destination-arrival`.
- Patterns: 2 — `do-genitive-destination` (`do + Genitive`), `na-accusative-destination`
  (`na + Accusative`); both A2/A2, active-production, core.
- Examples: `Przyjadę do Warszawy.` — "I will arrive in Warsaw."; `Przyjadę
  na dworzec.` — "I will arrive at the station." Both editorial-generated.
- Handling: only the destination realizations of selected `DOKĄD` are
  authored; no source, vehicle, route, time, or manner; no syntax borrowed
  from imperfective `przyjeżdżać`.

### `wyjść`

- Meanings: 1 — `literal-exit-from-place`.
- Patterns: 3 — `z-genitive-source` (`z + Genitive`, A1/A1, core),
  `do-genitive-destination` (`do + Genitive`, A2/A2, common),
  `na-accusative-destination` (`na + Accusative`, A2/A2, common); all
  active-production.
- Examples: `Wyszedłem z domu.` — "I left the house."; `Wyjdę do ogrodu.` —
  "I will go out to the garden."; `Wyjdę na balkon.` — "I will go out onto
  the balcony." All editorial-generated.
- Handling: source and destination are both labelled non-exclusive
  realizations of `SKĄD`/`DOKĄD`. The separately evidenced ranking/result
  sense (`na CO`, e.g. "wyjść na prowadzenie") is intentionally **not**
  authored here — see "Omitted verified constructions" below. No syntax
  borrowed from imperfective `wychodzić`.

### `wyjechać`

- Meanings: 1 — `transport-departure`.
- Patterns: 1 — `z-genitive-source` (`z + Genitive`); A2/A2,
  active-production, core.
- Example: `Wyjadę z miasta.` — "I will leave the city." Editorial-generated.
- Handling: only the source realization is authored; no destination,
  vehicle, route, time, or manner; no syntax borrowed from imperfective
  `wyjeżdżać`.

### `przynosić`

- Meanings: 1 — `physical-carrying`.
- Patterns: 1 — `accusative-object`; A1/A1, active-production, core.
- Example: `Przynoszę kawę.` — "I am bringing coffee." Editorial-generated.
- Handling: only direct Accusative is authored. No Dative recipient (that
  Phase 2 hypothesis was explicitly rejected); no concrete source/goal
  preposition, since Phase 3 did not authorize one for product use; no
  syntax inherited from perfective `przynieść`.

### `odpowiadać`

- Meanings: 1 — `answering-by-speech`.
- Patterns: 3 — `na-accusative-question` (`na + Accusative`, A1/A1, core),
  `ze-content-clause` (`że` clause, A2/B1, common), `direct-speech`
  (`clauseKind: direct-speech`, A2/B1, common); all active-production.
- Examples: `Odpowiadam na pytanie.` — "I am answering the question.";
  `Odpowiadam, że nie wiem.` — "I answer that I don't know."; `Odpowiadam:
  „Nie wiem”.` — "I answer: \"I don't know.\"" All editorial-generated.
- Handling: the three constructions are kept as alternatives, not a combined
  maximal frame. No Dative addressee is authored; the person spoken to is
  not a schema position. Direct speech is authored under the Phase 4B
  private-staging direct-speech policy; canonical support remains deferred
  to Phase 4C, and no canonical/runtime file was touched.

### `zamawiać`

- Meanings: 1 — `commissioning-ordering`.
- Patterns: 4 — `accusative-item` (A1/A1, core), `dative-beneficiary`
  (A2/A2, common), `dla-genitive-beneficiary` (A2/A2, common),
  `u-genitive-provider` (A2/A2, common); all active-production.
- Examples: `Zamawiam pizzę.` — "I am ordering a pizza."; `Zamawiam mężowi
  prezent.` — "I am ordering a present for my husband."; `Zamawiam prezent
  dla żony.` — "I am ordering a present for my wife."; `Zamawiam meble u
  stolarza.` — "I am ordering furniture from a carpenter." All
  editorial-generated.
- Handling: Dative and `dla + Genitive` beneficiary are authored as
  independent alternative patterns, never combined into one frame. `u +
  Genitive` provider is labelled a documented realization of a selected
  provider/location role, not exclusive provider government. No syntax
  borrowed from perfective `zamówić`.

### `zacząć`

- Meanings: 1 — `bounded-onset`.
- Patterns: 2 — `accusative-activity` (A1/A1, core), `infinitive` (A1/A1,
  core); both active-production.
- Examples: `Zacząłem lekcję.` — "I started the lesson."; `Zacząłem czytać
  książkę.` — "I started reading a book." Both editorial-generated.
- Handling: the pre-existing private `metadataAspectPartner` relationship to
  `zaczynać` is preserved byte-for-byte; no candidateContent was given to
  `zaczynać`; no syntax inherited from it.

### `kończyć`

- Meanings: 1 — `activity-completion`.
- Patterns: 2 — `accusative-task` (A1/A1, core), `infinitive` (A1/A1, core);
  both active-production.
- Examples: `Kończę pracę.` — "I am finishing the work."; `Kończę czytać
  książkę.` — "I am finishing reading the book." Both editorial-generated.
- Handling: no syntax borrowed from perfective `skończyć`; this record does
  not pre-decide the later `kończyć`/`skończyć` pair policy.

### `pamiętać`

- Meanings: 2 — `recall-retain`, `obligation-reminder`.
- Patterns: 4 — `accusative-recollection` (recall, A1/A1, core),
  `o-locative-topic` (recall, A2/A2, common), `infinitive-obligation`
  (obligation, A2/A2, core), `zeby-clause-obligation` (obligation, A2/B1,
  common); all active-production.
- Examples: `Pamiętam ten dzień.` — "I remember that day."; `Pamiętam o
  twoich urodzinach.` — "I remember your birthday."; `Pamiętaj zamknąć
  drzwi.` — "Remember to close the door."; `Pamiętaj, żeby dzieci umyły
  ręce.` — "Remember that the children should wash their hands." All
  editorial-generated.
- Handling: recall and obligation/reminder are kept as separate meanings.
  `żeby` is authored only in the obligation meaning; recall never uses
  `żeby`. The że-content-clause and interrogative-dependent-clause
  constructions independently verified for the recall sense are
  intentionally **not** authored here — see "Omitted verified
  constructions" below.

### `zapominać`

- Meanings: 2 — `recall-failure`, `failure-to-act`.
- Patterns: 6 — `genitive-object` (recall, A2/A2, core), `accusative-object`
  (recall, A2/A2, core), `o-locative-topic` (recall, A2/A2, common),
  `ze-content-clause` (recall, A2/B1, common), `czy-dependent-clause`
  (recall, **B1 recognition-only**, common), `infinitive-failure`
  (failure-to-act, A2/A2, core).
- Examples: `Zapominam numeru telefonu.` — "I forget the phone number.";
  `Zapominam tę twarz.` — "I forget that face."; `Zapominam o spotkaniu.` —
  "I forget about the meeting."; `Zapominam, że mam spotkanie.` — "I forget
  that I have a meeting."; `Zapominam, czy zamknąłem drzwi.` — "I forget
  whether I locked the door."; `Zapominam zadzwonić.` — "I forget to call."
  All editorial-generated.
- Handling: the recall sense authors all five directly verified
  constructions (Genitive, Accusative, `o + Locative`, `że`-clause,
  `czy`-clause) per the completeness rule explicitly retained for this
  lemma in the Phase 3 batch reconciliation. The failure-to-act meaning
  authors only the infinitive; the proposed `żeby` clause was explicitly
  rejected by Phase 3 and is not authored. No syntax is inherited from
  another aspect identity.

## Omitted verified constructions and rationale

- **`wyjść` ranking/result sense** (`na + Accusative`, e.g. "wyjść na
  prowadzenie"). Phase 3 separately evidenced this as a distinct sense from
  literal exit. It is intentionally not authored in this selective product
  at this stage: authoring it now, immediately alongside literal exit's own
  `na + Accusative` destination pattern on the same lemma, would place two
  same-preposition, same-case, different-sense `na + Accusative` patterns on
  one lemma in the same batch, which meaningfully raises the risk that
  learners (and future authors) blur the destination and result readings
  together. Deferring the result sense to a later, separately reviewed
  authoring pass keeps the literal-exit boundary unambiguous now. No
  result-sense content or syntax was merged into `literal-exit-from-place`.
- **`pamiętać` recall że-content-clause and interrogative-dependent-clause.**
  Phase 3 evidence directly supports both for the recall sense. They are
  intentionally deferred here because `pamiętać`'s distinct obligation
  meaning already authors a `żeby`-clause in this same batch; adding a
  `że`-clause to the sibling recall meaning in the same pass risks exactly
  the reminder/recall conflation the task explicitly warns against (`że`
  and `żeby` differ by two letters and are easy for A1–B1 learners to
  conflate across two freshly introduced sibling meanings). The
  interrogative-dependent clause is, independently, a more advanced
  embedded-question construction not flagged as a completeness addition for
  this lemma the way it was for `zapominać`. Both remain valid, directly
  verified constructions for later authoring once the recall/obligation
  boundary is independently reviewed and confirmed stable.

## Coverage, provenance, and totals

- Batch 2 totals: 12 meanings, 28 patterns, 28 examples.
- Cumulative Batch 1 + Batch 2 totals: 24 meanings, 53 patterns, 53
  examples, across 20 authored lemmas.
- Every authored pattern has exactly one candidate example.
- Teaching status: 27 active-production; 1 recognition-only
  (`zapominać` / `czy-dependent-clause`).
  - **Recognition-only rationale.** The `czy`-embedded dependent clause
    ("zapominam, czy zamknąłem drzwi") combines aspect marking on the
    embedded verb with an embedded yes/no question — a construction
    directly verified by Phase 3 but more realistically taught for
    comprehension than for early productive use at A1–B1. It is authored
    (not omitted) because it is clearly learner-relevant for recognition,
    with CEFR recognition at B1 and no production CEFR value.
  - **Active-production justification for the remaining 27.** Each of the
    other 27 patterns represents a core-to-common valency construction for
    a common A1–B1 verb (direct case objects, single-preposition
    destination/source realizations, plain infinitives, and the `że`/direct
    speech/`żeby` clauses that are staples of everyday spoken narration and
    instruction at this level). None requires more than one clause boundary
    or embedded question, so productive use is realistic at the assigned
    CEFR; this is not a mechanical default but an independent judgment for
    each pattern.
- Provenance: 0 repository-reuse; 28 editorial-generated.
  - A repository search was conducted across `data-a1.js`, `data-a2.js`,
    `data-b1.js`, `data-grammar.js`, `data-scenarios.js`, `data-podcasts.js`,
    and `content/verb-patterns.json` for each Batch 2 lemma's inflected
    forms. Matches found and rejected as ineligible:
    - `data-verbs.js` verb-grid rows (e.g. "Wyszedłem z domu.", "Przyjdę o
      piątej.") are teaching-table entries without an `id` field inside a
      `cards`/`drills` collection, so they cannot be resolved through the
      established repository index and are not eligible for
      `repository-reuse` origin.
    - `a1-morning-routine-017` ("Wychodzę z domu o ósmej piętnaście.") uses
      imperfective `wychodzić`, not Batch 2's perfective `wyjść` — wrong
      lemma/aspect.
    - `a1-weather-today-013`, `a2-describing-past-024`,
      `b1-everyday-slang-019`, `b1-swearing-002` ("zapomniałem parasola",
      "zapomniałem o spotkaniu", "zapomniał hasła", "zapomniałem portfela")
      all use perfective `zapomnieć`, not Batch 2's imperfective
      `zapominać` — wrong lemma/aspect, despite thematic overlap.
    - `b1-urban-party-slang-001` ("słoiki wyjechały do domu") uses the
      correct lemma `wyjechać` but the wrong pattern (a `do + Genitive`
      destination, which is explicitly not authored for `wyjechać`).
    - `b1-urban-party-slang-004` ("nic nie pamiętam") is negation-entangled
      and embedded in an informal slang card; it does not cleanly
      demonstrate the plain Accusative recall pattern.
    - `a1-months-seasons-006` ("kończy się szkoła") uses reflexive `kończyć
      się`, a distinct lexical identity from plain `kończyć`.
    - No eligible card/drill match exists for `przynosić`, `odpowiadać`,
      `zamawiać`'s Batch 2 patterns, or for `zacząć`/`pamiętać`'s bare
      Accusative/infinitive patterns.
  - All 28 Polish/English example pairs are unique within the batch and were
    independently checked against the local card/drill index for quiet
    reuse (see `tests/test_priority8_phase4b2_batch02.py`); none matched.

## Candidate keys

All `candidateMeaningKey`/`candidatePatternKey` values are durable semantic
or construction identities (e.g. `transport-destination-arrival`,
`z-genitive-source`, `zeby-clause-obligation`), independent of batch number,
verification order, or example wording. Pattern-key reuse across lemmas
(`z-genitive-source`, `do-genitive-destination`, `infinitive`,
`accusative-object`, `o-locative-topic`) is sibling-scoped per the locked
architecture, matching the precedent already exercised in Batch 1. All 28
`candidateExampleKey` values use the durable slot name `primary`.

## Batch 2 digest

`5fef7ce7dddb9f06dd56e25cef7591ac4c94e0aa2f71fe208227431b0a649664`

The digest projects verification orders 11, 12, 13, 14, 15, 16, 18, 19, 20,
21 in staging order over `verificationOrder`, `canonicalLemma`, `aspect`,
`phase3Disposition`, `phase3Evidence`, `bindingConstraints`,
`candidateContent`, and `metadataAspectPartner` (present only on `zacząć`),
serialized as UTF-8 JSON with sorted keys and compact separators before
SHA-256 hashing, following the same canonical-projection philosophy as the
Batch 1 digest in `reports/priority-8-phase-4b-test-lifecycle.md`.

## Test results

```
python3 -m unittest tests.test_priority8_phase4b0_staging        # 31 tests, OK
python3 -m unittest tests.test_priority8_phase4b1a_authoring_schema  # 65 tests, OK
python3 -m unittest tests.test_priority8_phase4b1_batch01         # 9 tests, OK
python3 -m unittest tests.test_priority8_phase4b2_batch02         # 11 tests, OK
python3 -m unittest tests.test_priority8_phase4b_progress         # 8 tests, OK
```

Combined: 124 tests, OK.

## Validator result

```
PASS: Priority 8 4B2 staging revision 3 is read-only valid (68 lemmas, 21 constrained records, 12 global constraints).
```
