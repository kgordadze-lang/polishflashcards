# Priority 8 Phase 4B — final reconciliation correction implementation

## A. Starting state

The stop-on-mismatch gate passed before editing.

| Check | Observed |
|---|---|
| Folder | `/Users/Kaj/Downloads/Repository for Codex - Priority 8 Phase 4B SAFE` |
| Branch | `priority-8-phase-4b-editorial-authoring` |
| Starting HEAD | `70ae638d4c5eb85888d756d1522130b03085e8ae` |
| Starting subject | `Priority 8 Phase 4B final semantic reconciliation` |
| Worktree | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |
| Envelope | `phaseStep = 4B7`, `stagingRevision = 8` |
| Content | 68 authored / 95 meanings / 224 patterns / 224 examples / 0 future-empty |
| Status | 220 active-production / 4 recognition-only |
| Guards | 72 rules, registry version 2 |
| Baseline | validator PASS; exact eleven suites 270 tests, OK |

## B. Human decisions applied

**HD-1.** Both corrected interrogative-dependent rows now use recognition A2,
production A2, and `active-production`. The current global split is 222 active /
2 recognition-only.

**HD-2.** The seven source-semantic rows retain the locked coarse Phase 4B
`role: target`. No `source` role was invented and no source-oriented key was
renamed. Binding Phase 4C constraint: before runtime projection, these seven rows
must either map to a faithful source representation or be specially projected so
they can never receive the target phrase "what it is aimed at":

1. `wracać/return-to-earlier-place/z-genitive-return-source`
2. `wrócić/completed-return-to-earlier-place/z-genitive-return-source`
3. `wyjść/literal-exit-from-place/z-genitive-source`
4. `wyjechać/transport-departure/z-genitive-source`
5. `kupować/process-purchase/seller-price-schema` (`od` + Genitive seller)
6. `kupić/completed-purchase/seller-price-schema` (`od` + Genitive seller)
7. `zamawiać/commissioning-ordering/u-genitive-provider`

## C. Changed paths

The actual set equals the pre-edit planned set exactly.

| Path | Reason |
|---|---|
| `editorial/priority-8-phase4-staging.json` | approved structural, key, CEFR/status, example and editorial corrections |
| `tests/fixtures/priority8_phase4b_authoring_rules.json` | two exact-shape guards; corrected `móc` signature |
| `tests/test_priority8_phase4b2_batch02.py` | B2 digest and `zapominać` reconciliation invariant |
| `tests/test_priority8_phase4b3_batch03.py` | B3 digest and `kłócić się` reconciliation invariant |
| `tests/test_priority8_phase4b6_batch06.py` | B6 digest and exact `móc` negative signature invariant |
| `tests/test_priority8_phase4b7_batch07.py` | B7 digest |
| `tests/test_priority8_phase4b_progress.py` | 222/2 recognition-only control and current reconciliation-rule presence |
| `reports/priority-8-phase-4b2-batch-02-authoring.md` | labelled historical correction note |
| `reports/priority-8-phase-4b2-batch-02-risk-review.md` | labelled historical correction note |
| `reports/priority-8-phase-4b3-batch-03-authoring.md` | labelled historical correction note |
| `reports/priority-8-phase-4b3-batch-03-risk-review.md` | labelled historical correction note |
| `reports/priority-8-phase-4b6-batch-06-authoring.md` | labelled historical correction note |
| `reports/priority-8-phase-4b7-batch-07-authoring.md` | labelled historical correction note |
| `reports/priority-8-phase-4b-final-correction-implementation.md` | this implementation/audit record and binding Phase 4C debt |

No SHA-locked B4–B7 matrix was edited.

## D. Clause-kind corrections

| Lemma | Clause kind | Pattern key | Example reference | Editorial surface |
|---|---|---|---|---|
| `zapominać` | `czy` → `interrogative` | `czy-dependent-clause` → `interrogative-forgotten-content` | renamed in lockstep | exact accepted learner explanation and `internalScope`; Polish/English example unchanged |
| `kłócić się` | `czy` → `interrogative` | `czy-dependent-clause` → `interrogative-disputed-content` | renamed in lockstep | exact accepted learner explanation; `internalScope` unchanged because already correct; Polish/English example unchanged |

The surface `czy` in both Polish examples remains a valid realization of an
interrogative-dependent clause.

## E. Status and CEFR

Both corrected rows changed from B1/none recognition-only to A2/A2
active-production. The two live recognition-only controls are unchanged:

- `pozwalać/inanimate-enabling/zeby-enabling`: B1/none, common.
- `wymagać/situation-requires-content/zeby-clause`: B1/none, common.

Global result: 222 active-production / 2 recognition-only.

## F. Guards and mutation proof

Registry version remains 2. Rule count is 72 → 74.

- Added `p8-4b-zapominac-exact-pattern-shapes`.
- Added `p8-4b-klocic-sie-exact-pattern-shapes`.
- Corrected `p8-4b-moc-no-question-clause` signature from
  `{type: clause, clauseKind: czy}` to
  `{type: clause, clauseKind: interrogative}`.

All mutations used deep in-memory copies; no mutation wrote a repository file.

| Proof | Result |
|---|---|
| Clean corrected staging | zero guard issues |
| Corrected `zapominać` shape | passes |
| Corrected `kłócić się` shape | passes |
| Either corrected row changed back to `czy` | rejected by its new exact-shape rule |
| Either corrected row changed to unauthorized `direct-speech` | rejected by its new exact-shape rule |
| `móc` injected with an interrogative clause | rejected by `p8-4b-moc-no-question-clause` (and independently by its exact-shape rule) |

## G. Adopted editorial corrections

| Lemma / item | Field | Old | New | Reason |
|---|---|---|---|---|
| `wymagać` P8-SR-001 | example PL | `Wymaga lojalności od pracowników.` | `Szef wymaga lojalności od pracowników.` | make person-subject meaning visible |
| `wymagać` P8-SR-001 | example EN | `It requires loyalty from employees.` | `The boss requires loyalty from employees.` | remove contradiction with person-subject meaning |
| `polecać` P8-FR-006 | example EN | `The coach orders the players to warm up.` | `The coach instructs the players to warm up.` | preserve directive force without overstatement |
| `polecać` P8-FR-006 | explanation inline gloss | `orders` | `instructs` | keep explanation consistent with example |
| `musieć` P8-FR-008 | explanation | `Musieć always takes a bare infinitive: muszę iść do lekarza (I have to go to the doctor). Polish uses this one construction whether or not the sentence names who has to act, so impersonal sentences add nothing new to learn.` | `Musieć always takes a bare infinitive: muszę iść do lekarza (I have to go to the doctor). This is the only construction it uses.` | remove curriculum meta-commentary |
| `jeść` P8-FR-009 | explanation | `Both parts are optional: put the food in the Accusative and the implement in the Instrumental — dziecko je zupę łyżką (the child eats the soup with a spoon) — or just say je (is eating). After a negated verb the object switches to the Genitive (nie je zupy); that is the general Polish rule for negated objects, not a separate pattern of jeść.` | `Both parts are optional: the food takes the Accusative and the implement the Instrumental — dziecko je zupę łyżką (the child eats the soup with a spoon) — or just je (is eating). Jeść has no Genitive object of its own.` | return negation to grammar ownership |
| `kochać` P8-FR-010 | `strong-liking.glossesEn` | `love (doing something)`; `really like` | `really like`; `love (a thing or an activity)` | lead with weaker sense and cover both owned patterns |
| `przepraszać` item E | example EN | `I'm sorry I didn't call you yesterday.` | `I apologise to you for not calling yesterday.` | preserve attachment of the apologised-to participant |
| `życzyć` item F | explanation | `To wish for something to happen, keep the Dative person and use a żeby clause instead of the Genitive: życzę ci, żebyś zdał egzamin (I hope you pass the exam). Use one or the other, not both.` | `To wish for something to happen, keep the Dative person and use a żeby clause instead of the Genitive: życzę ci, żebyś zdał egzamin (literally 'I wish for you that you pass the exam'; English usually says I hope you pass). Use one or the other, not both.` | make required Dative visible without unnatural English |
| `uczyć` P8-FR-011 | example PL | `Nauczycielka uczy dzieci o zwyczajach w innych krajach.` | `Nauczycielka uczy uczniów o polskich zwyczajach.` | remove second Locative and make learner case clearer |
| `uczyć` P8-FR-011 | example EN | `The teacher teaches the children about customs in other countries.` | `The teacher teaches the pupils about Polish customs.` | translate accepted Polish replacement |
| `uczyć` P8-FR-012 | example PL | `Pani Nowak uczy dzieci matematyki.` | `Pani Nowak uczy moją córkę matematyki.` | visibly separate Accusative from Genitive |
| `uczyć` P8-FR-012 | example EN | `Mrs Nowak teaches the children maths.` | `Mrs Nowak teaches my daughter maths.` | translate accepted Polish replacement |
| `uczyć` P8-FR-012 | explanation inline Polish | `pani Nowak uczy dzieci matematyki` | `pani Nowak uczy moją córkę matematyki` | keep accepted example visible in instruction |

Items classified KEEP AS IS, CLOSED—NO ACTION, unselected optional editorial,
or DEFER TO PHASE 4C were not implemented.

## H. Polish example provenance and lexical identity

Exactly three Polish sentences changed:

| Sentence | Layer A | Layer B | Origin | Lexical identity |
|---|---|---|---|---|
| `Szef wymaga lojalności od pracowników.` | 0 collisions / 1,665 entities / 0 index issues | 0 broad raw-text hits | `editorial-generated` | finite `wymaga` belongs to `wymagać` |
| `Nauczycielka uczy uczniów o polskich zwyczajach.` | 0 collisions / 1,665 entities / 0 index issues | 0 broad raw-text hits | `editorial-generated` | finite `uczy` belongs to non-reflexive `uczyć` |
| `Pani Nowak uczy moją córkę matematyki.` | 0 collisions / 1,665 entities / 0 index issues | 0 broad raw-text hits | `editorial-generated` | finite `uczy` belongs to non-reflexive `uczyć` |

## I. Complete candidateContent field-level diff

The machine-generated recursive comparison against starting HEAD found exactly 30
changed leaf fields. `<missing>` means the approved field was added. No other
`candidateContent` field changed.

| Order | Lemma | Meaning | Pattern | Field | Old | New | Reason |
|---:|---|---|---|---|---|---|---|
| 21 | `zapominać` | `recall-failure` | — | `meanings[0].internalScope` | `Losing recall of people, things, events, or information. Direct Genitive and direct Accusative both realize the remembered/forgotten object; o+Locative names a remembered topic; że and czy content clauses realize forgotten propositional/question content. All are directly verified for this exact sense. Excludes the distinct failure-to-act meaning below and does not use żeby; that schema was explicitly rejected by Phase 3.` | `Losing recall of people, things, events, or information. Direct Genitive and direct Accusative both realize the remembered/forgotten object; o+Locative names a remembered topic; że clauses realize forgotten propositional content and interrogative-dependent clauses realize forgotten question content (a czy sentence is one realization of that clause type, never a separate clause kind). All are directly verified for this exact sense. Excludes the distinct failure-to-act meaning below and does not use żeby; that schema was explicitly rejected by Phase 3.` | P8-FR-001 |
| 21 | `zapominać` | `recall-failure` | corrected row | `candidatePatternKey` | `czy-dependent-clause` | `interrogative-forgotten-content` | P8-FR-001 key durability |
| 21 | `zapominać` | `recall-failure` | corrected row | `cefr.production` | `<missing>` | `A2` | HD-1 |
| 21 | `zapominać` | `recall-failure` | corrected row | `cefr.recognition` | `B1` | `A2` | HD-1 |
| 21 | `zapominać` | `recall-failure` | corrected row | `complements[0].clauseKind` | `czy` | `interrogative` | P8-FR-001 |
| 21 | `zapominać` | `recall-failure` | corrected row | `learnerExplanationEn` | `Use czy to introduce a forgotten yes/no question: zapominam, czy zamknąłem drzwi (I forget whether I locked the door).` | `Use a dependent question clause for a forgotten question. For a yes/no question that word is czy: zapominam, czy zamknąłem drzwi (I forget whether I locked the door); question words such as gdzie or kiedy work the same way.` | P8-FR-001 |
| 21 | `zapominać` | `recall-failure` | corrected row | `teachingStatus` | `recognition-only` | `active-production` | HD-1 |
| 21 | `zapominać` | `recall-failure` | corrected row | `examples[4].patternKeyRef` | `czy-dependent-clause` | `interrogative-forgotten-content` | ownership integrity |
| 25 | `wymagać` | `person-requires-behavior` | `genitive-required-content` | `examples[0].en` | `It requires loyalty from employees.` | `The boss requires loyalty from employees.` | P8-SR-001 |
| 25 | `wymagać` | `person-requires-behavior` | `genitive-required-content` | `examples[0].pl` | `Wymaga lojalności od pracowników.` | `Szef wymaga lojalności od pracowników.` | P8-SR-001 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `candidatePatternKey` | `czy-dependent-clause` | `interrogative-disputed-content` | P8-FR-002 key durability |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `cefr.production` | `<missing>` | `A2` | HD-1 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `cefr.recognition` | `B1` | `A2` | HD-1 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `complements[0].clauseKind` | `czy` | `interrogative` | P8-FR-002 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `learnerExplanationEn` | `Use czy to introduce an undecided yes/no topic: kłócimy się, czy powinniśmy wyjechać (we're arguing about whether we should leave).` | `Use a dependent question clause when the disputed point is an open question. For a yes/no question that word is czy: kłócimy się, czy powinniśmy wyjechać (we're arguing about whether we should leave); question words such as gdzie or kiedy work the same way.` | P8-FR-002 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `teachingStatus` | `recognition-only` | `active-production` | HD-1 |
| 27 | `kłócić się` | `interpersonal-quarrelling` | corrected row | `examples[3].patternKeyRef` | `czy-dependent-clause` | `interrogative-disputed-content` | ownership integrity |
| 58 | `polecać` | `directive-instruction` | `dative-accusative-action-noun` | `learnerExplanationEn` | `The Accusative names the ordered action as a noun (usually a gerund/action noun), not a recommended item: trener poleca zawodnikom rozgrzewkę (the coach orders the players to warm up).` | `The Accusative names the ordered action as a noun (usually a gerund/action noun), not a recommended item: trener poleca zawodnikom rozgrzewkę (the coach instructs the players to warm up).` | P8-FR-006 |
| 58 | `polecać` | `directive-instruction` | `dative-accusative-action-noun` | `examples[3].en` | `The coach orders the players to warm up.` | `The coach instructs the players to warm up.` | P8-FR-006 |
| 62 | `musieć` | `necessity-obligation` | `infinitive-required-action` | `learnerExplanationEn` | exact old text in §G | exact new text in §G | P8-FR-008 |
| 64 | `jeść` | `food-consumption` | `accusative-food-instrumental-implement` | `learnerExplanationEn` | exact old text in §G | exact new text in §G | P8-FR-009 |
| 66 | `kochać` | `strong-liking` | — | `glossesEn[0]` | `love (doing something)` | `really like` | P8-FR-010 |
| 66 | `kochać` | `strong-liking` | — | `glossesEn[1]` | `really like` | `love (a thing or an activity)` | P8-FR-010 |
| 67 | `przepraszać` | `apology` | `accusative-person-ze-explanation` | `examples[1].en` | `I'm sorry I didn't call you yesterday.` | `I apologise to you for not calling yesterday.` | item E |
| 68 | `życzyć` | `good-wishes` | `dative-recipient-zeby-wished-event` | `learnerExplanationEn` | exact old text in §G | exact new text in §G | item F |
| 70 | `uczyć` | `school-subject-teaching` | `accusative-learner-genitive-school-subject` | `learnerExplanationEn` | `For teaching a school subject, the subject takes the Genitive and naming the pupils is optional: pani Nowak uczy dzieci matematyki, or simply uczy matematyki.` | `For teaching a school subject, the subject takes the Genitive and naming the pupils is optional: pani Nowak uczy moją córkę matematyki, or simply uczy matematyki.` | P8-FR-012 |
| 70 | `uczyć` | `teaching-instruction` | `accusative-person-o-locative-taught-topic` | `examples[4].en` | `The teacher teaches the children about customs in other countries.` | `The teacher teaches the pupils about Polish customs.` | P8-FR-011 |
| 70 | `uczyć` | `teaching-instruction` | `accusative-person-o-locative-taught-topic` | `examples[4].pl` | `Nauczycielka uczy dzieci o zwyczajach w innych krajach.` | `Nauczycielka uczy uczniów o polskich zwyczajach.` | P8-FR-011 |
| 70 | `uczyć` | `school-subject-teaching` | `accusative-learner-genitive-school-subject` | `examples[5].en` | `Mrs Nowak teaches the children maths.` | `Mrs Nowak teaches my daughter maths.` | P8-FR-012 |
| 70 | `uczyć` | `school-subject-teaching` | `accusative-learner-genitive-school-subject` | `examples[5].pl` | `Pani Nowak uczy dzieci matematyki.` | `Pani Nowak uczy moją córkę matematyki.` | P8-FR-012 |

## J. Keys and ownership

All 543 candidate keys validate mechanically: 95 meaning keys, 224 pattern keys,
224 example keys; zero format errors, sibling collisions, orphan references,
duplicate owners, or ownership mismatches. Exactly the two approved pattern keys
changed, with exactly one dependent `patternKeyRef` each. No meaning key or example
key changed. Result: **READY TO FREEZE** from the correction perspective; no key is
frozen by this implementation.

## K. Batch digests

All values were recomputed from the existing batch projections.

| Batch | Before | After | Result |
|---|---|---|---|
| B1 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` | same | unchanged as predicted |
| B2 | `dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8` | `87c07469634cc039e68e2f52a5f306a05ca7753e1e4d328d58542c4b549e2f82` | changed as predicted |
| B3 | `8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb` | `313b50ec3fe5a2764c4f477c0f47ceef7733cadade7c7b183350f335bcff7197` | changed as predicted |
| B4 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` | same | unchanged as predicted |
| B5 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` | same | unchanged as predicted |
| B6 | `cff207b6e728fb203ba05a9ba94915432957be76101b3bd6a0f65137cdda98d5` | `ec9148072c58879334e1eeeae1b20f62259ceecf56ea18500f0d0fb4666e610a` | changed as predicted |
| B7 | `88aed6dc4b972ddc3ce7ea18b5e987d95ae1f38d5eb5a742a45be7332c372672` | `a2d34c616d416f6a36f2346a2c4190522f1102087b3745ab0605be29c5430d9e` | changed as predicted |

## L. Historical tests and reports

B2, B3, B6 and B7 historical digest constants were recomputed. B2 and B3 gain
targeted exact corrected-row invariants; B6 pins the corrected `móc` negative
signature. The moving progress test pins the current 222/2 split, exact two
recognition-only rows, both reconciliation guard IDs, version 2, and a future-safe
minimum of 74 rules. No fixed registry-total assertion was added to a historical
batch lock.

Six historical reports received appended, labelled correction notes. Original
claims remain as historical context; stale keys, statuses and digests are marked
superseded in the notes. No historical matrix or unrelated report was rewritten.

## M. Counts and same-shape control

- 68 authored lemmas
- 95 meanings
- 224 patterns
- 224 examples
- 0 future-empty records
- 222 active-production
- 2 recognition-only

Only `zapominać` and `kłócić się` changed complement structure, exactly at
the approved `clauseKind` leaf. Every editorially changed same-shape family
(`wymagać`, `polecać`, `musieć`, `jeść`, `kochać`, `przepraszać`,
`życzyć`, `uczyć`) retained byte-equivalent complement arrays. The
`polecać` A4/B1 structural boundary remains frozen and semantically clearer after
the English correction.

## N. Architecture immutability and safety

Unchanged: `validate_priority8_staging.py`,
`tests/test_priority8_phase4b_authoring_guards.py`, `priority7_tooling.py`, all
runtime/canonical/audio files, `APP_VERSION`, service-worker files, stable-ID
tooling/output, and the B4–B7 frozen matrices. No production/stable ID was added.
`phaseStep = 4B7`, `stagingRevision = 8`, and all 68 review statuses remain
`draft`.

No runtime projection, Phase 4C implementation, push, deploy, or integration was
performed.

## O. Verification results

| Gate | Result |
|---|---|
| Validator | PASS: 4B7 revision 8; 68 lemmas; 21 constrained records; 12 global constraints |
| Exact eleven Phase 4B suites | 274 tests in 70.820s; OK |
| Corrected-path targeted suites | 117 tests in 39.840s; OK |
| Guard mutations | all required proofs PASS; clean staging zero issues |
| Candidate keys / ownership | 543 valid; zero issues |
| Quiet-reuse provenance | three sentences, Layer A zero, Layer B zero |
| Digest prediction | B1/B4/B5 unchanged; B2/B3/B6/B7 changed, exact |
| `git diff --check` | clean |

## P. Candidate-key freeze readiness

**READY FOR FINAL INDEPENDENT VERIFICATION BEFORE CANDIDATE-KEY FREEZE**

No candidate key was frozen and no stable ID was allocated.
