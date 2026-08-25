# Priority 8 Phase 4B7 — Batch 07 authoring

## 1. Starting endpoint and scope

This is the **final** Phase 4B authoring batch. The frozen, independently
reviewed Batch 7 schema matrix was **implemented, not linguistically
reinterpreted**: every meaning key, pattern key, `relationType`, role,
complement, requiredness value, clause kind, meaning ownership,
generalized-role treatment and guard proposal is taken verbatim from
`reports/priority-8-phase-4b7-schema-matrix.md`. No fresh linguistic research
was performed and no frozen row was re-derived, re-scoped or re-worded.

Starting endpoint, verified before any file was written:

- branch `priority-8-phase-4b-editorial-authoring`
- HEAD `e2f00190095cec74721fd766d944cf30ecfdce40`
- tree `ab727d30729e58fbcfa6ec671b61c1eebb4f4eca`
- parent `9a7973a03314b98f935df2b6265447c0373cb7da`
- subject `Clarify Priority 8 Phase 4B7 matrix precedents`
- clean working tree, zero remotes, `push.default=nothing`, executable
  blocking pre-push hook

Recorded SHA-256 before editing:

| Path | SHA-256 |
|---|---|
| `reports/priority-8-phase-4b7-schema-matrix.md` | `8b152b204485001f921d54c1b8941f9e2c2173fbc910cd52c57b9e240240212a` |
| `editorial/priority-8-phase4-staging.json` | `9bd26dff88943a507b5ead9ce9e72ee8a3da2704193531296f74f4937a6462b3` |
| `tests/fixtures/priority8_phase4b_authoring_rules.json` | `a6d696414b35f68a0b69251841e145f000d8c5dd46efc07b3fc61bb69158815d` |

Recomputed starting staging state: `phaseStep 4B6`, `stagingRevision 7`, 59
authored, 82 meanings, 201 patterns, 201 examples, 9 future-empty; guard
registry 57 rules at `registryVersion 2`; scoped baseline 243 tests
(31 + 65 + 9 + 11 + 17 + 23 + 29 + 24 + 8 + 26). All six historical digests
recomputed and matched. **No state mismatch.**

The matrix SHA-256 is **unchanged** by this task and is pinned inside the new
historical Batch 7 lock.

## 2. Exact scope and 9 / 13 / 23 reconciliation

Exactly the nine remaining full-pattern lemmas, orders 62–70, were authored.
`móc` (order 61, Batch 6), the metadata-only identities `zaczynać` and
`przeczytać`, and the separate lexical identities `uczyć się` and
`życzyć sobie` received nothing.

| Order | Lemma | Meanings | Patterns | Examples |
|---|---|---:|---:|---:|
| 62 | `musieć` | 1 | 1 | 1 |
| 63 | `wiedzieć` | 1 | 4 | 4 |
| 64 | `jeść` | 1 | 1 | 1 |
| 65 | `pić` | 1 | 1 | 1 |
| 66 | `kochać` | 3 | 4 | 4 |
| 67 | `przepraszać` | 1 | 2 | 2 |
| 68 | `życzyć` | 1 | 2 | 2 |
| 69 | `korzystać` | 2 | 2 | 2 |
| 70 | `uczyć` | 2 | 6 | 6 |
| — | **total** | **13** | **23** | **23** |

Cross-checks: 1+1+1+1+3+1+1+2+2 = 13 ✓; 1+4+1+1+4+2+2+2+6 = 23 ✓; one primary
example per pattern, so 23 examples ✓. Every meaning owns at least one pattern.

**Matrix conformance was machine-checked before writing.** All 23 rows were
compared against a contract transcribed from the matrix §4 tables: 23/23 exact
on complement type, preposition, case, clause kind, role and requiredness;
0 missing rows; 0 extra rows; complement ordering also matches the matrix
listing order.

## 3. Full authored inventory

| Order | Lemma | Meaning key | Pattern key | Complements | CEFR rec/prod | Status | Priority | Example (pl) | Example (en) |
|---|---|---|---|---|---|---|---|---|---|
| 62 | `musieć` | `necessity-obligation` | `infinitive-required-action` | `infinitive` content req | A1/A1 | active | core | Muszę dziś iść do lekarza. | I have to go to the doctor today. |
| 63 | `wiedzieć` | `factual-knowledge` | `accusative-known-content` | `case:accusative` content req | A1/A2 | active | core | Wiem to od dawna. | I have known that for a long time. |
| 63 | `wiedzieć` | `factual-knowledge` | `o-locative-known-topic` | `o+locative` topic req | A2/A2 | active | core | Wiem o twoich problemach. | I know about your problems. |
| 63 | `wiedzieć` | `factual-knowledge` | `ze-known-proposition` | `clause:ze` content req | A2/B1 | active | common | Wiem, że masz teraz dużo pracy. | I know that you have a lot of work right now. |
| 63 | `wiedzieć` | `factual-knowledge` | `interrogative-queried-content` | `clause:interrogative` content req | A2/A2 | active | common | Nie wiem, czy zdążymy na pociąg. | I don't know whether we'll make the train. |
| 64 | `jeść` | `food-consumption` | `accusative-food-instrumental-implement` | `case:accusative` object opt; `case:instrumental` means opt | A1/A1 | active | core | Dziecko je zupę łyżką. | The child is eating the soup with a spoon. |
| 65 | `pić` | `liquid-consumption` | `accusative-drink-object` | `case:accusative` object req | A1/A1 | active | core | Codziennie rano piję kawę. | I drink coffee every morning. |
| 66 | `kochać` | `person-love` | `accusative-loved-person` | `case:accusative` object req | A1/A1 | active | core | Bardzo kocham swoją babcię. | I love my grandmother very much. |
| 66 | `kochać` | `idea-or-place-attachment` | `accusative-cherished-idea-or-place` | `case:accusative` object req | A2/A2 | active | common | Kocham swoje rodzinne miasto. | I love my home town. |
| 66 | `kochać` | `strong-liking` | `accusative-strongly-liked-thing` | `case:accusative` object req | A2/A2 | active | common | Moja siostra kocha czekoladę. | My sister loves chocolate. |
| 66 | `kochać` | `strong-liking` | `infinitive-strongly-liked-activity` | `infinitive` content req | A2/A2 | active | common | Dzieci kochają biegać po plaży. | The children love running on the beach. |
| 67 | `przepraszać` | `apology` | `accusative-person-za-accusative-offence` | `case:accusative` interlocutor req; `za+accusative` topic req | A2/A2 | active | core | Marek przeprasza nauczyciela za spóźnienie. | Marek apologises to the teacher for being late. |
| 67 | `przepraszać` | `apology` | `accusative-person-ze-explanation` | `clause:ze` content req; `case:accusative` interlocutor opt | A2/B1 | active | common | Przepraszam cię, że nie zadzwoniłem wczoraj. | I'm sorry I didn't call you yesterday. |
| 68 | `życzyć` | `good-wishes` | `dative-recipient-genitive-wished-thing` | `case:dative` recipient req; `case:genitive` content req | A2/A2 | active | core | Życzę ci zdrowia i szczęścia. | I wish you health and happiness. |
| 68 | `życzyć` | `good-wishes` | `dative-recipient-zeby-wished-event` | `case:dative` recipient req; `clause:zeby` content req | A2/B1 | active | common | Życzę ci, żebyś zdał ten egzamin. | I hope you pass this exam. |
| 69 | `korzystać` | `resource-use` | `z-genitive-used-resource` | `z+genitive` object req | A2/A2 | active | core | Codziennie korzystam z komunikacji miejskiej. | I use public transport every day. |
| 69 | `korzystać` | `benefit-from-advantage` | `z-genitive-source-of-benefit` | `z+genitive` object req | A2/A2 | active | common | Studenci chętnie korzystają ze zniżek studenckich. | Students readily take advantage of student discounts. |
| 70 | `uczyć` | `teaching-instruction` | `accusative-learner-genitive-taught-content` | `case:accusative` object req; `case:genitive` content req | A2/A2 | active | common | Babcia uczy wnuczkę cierpliwości. | Grandma teaches her granddaughter patience. |
| 70 | `uczyć` | `teaching-instruction` | `accusative-learner-infinitive-taught-skill` | `case:accusative` object req; `infinitive` content req | A2/A2 | active | common | Ojciec uczy syna pływać. | The father is teaching his son to swim. |
| 70 | `uczyć` | `teaching-instruction` | `accusative-learner-ze-taught-proposition` | `case:accusative` object req; `clause:ze` content req | A2/B1 | active | common | Rodzice uczą dzieci, że warto mówić prawdę. | Parents teach their children that it is worth telling the truth. |
| 70 | `uczyć` | `teaching-instruction` | `accusative-learner-interrogative-taught-content` | `case:accusative` object req; `clause:interrogative` content req | A2/A2 | active | common | Instruktor uczy kursantów, jak reagować w niebezpiecznej sytuacji. | The instructor teaches the trainees how to react in a dangerous situation. |
| 70 | `uczyć` | `teaching-instruction` | `accusative-person-o-locative-taught-topic` | `case:accusative` object req; `o+locative` topic req | A2/A2 | active | common | Nauczycielka uczy dzieci o zwyczajach w innych krajach. | The teacher teaches the children about customs in other countries. |
| 70 | `uczyć` | `school-subject-teaching` | `accusative-learner-genitive-school-subject` | `case:genitive` content req; `case:accusative` object opt | A2/A2 | active | core | Pani Nowak uczy dzieci matematyki. | Mrs Nowak teaches the children maths. |

All 36 candidate keys (13 meaning + 23 pattern) are the frozen matrix
proposals **verbatim**; none was renamed or "improved". Every key is
lowercase kebab-case, carries no verification order, batch number, source key,
sentence wording or production `vp-*` identifier, and is sibling-unique in its
locked scope. Every `candidateExampleKey` is the locked B1A convention value
`primary`.

## 4. CEFR, teaching status and usage decisions

Assignments follow the Batch 1–6 conventions observed in the live corpus rather
than the Phase 2 lemma-level CEFR signal, which is a starting hint only:
plain case-object rows sit at A1/A1–A2/A2, `o + Locative` topic rows at A2/A2,
`że`/`żeby` clause rows at A2/B1, and interrogative-dependent clause rows at
A2/A2.

| Decision | Rows | Rationale |
|---|---|---|
| A1/A1 core | `musieć` infinitive; `jeść`; `pić`; `kochać` person-love | Everyday, high-frequency, structurally transparent. `musieć` matches the frozen `móc` infinitive rows exactly. |
| A1/A2 core | `wiedzieć` Accusative content | Recognition is trivial, but production is constrained: the Accusative here is in practice a pronoun or quantifier (`to`, `wszystko`, `coś`), which is a real production hurdle recorded in the explanation. |
| A2/A2 core | `wiedzieć` `o + Locative`; `przepraszać` `za`; `życzyć` Genitive; `korzystać` resource-use; `uczyć` school subject | Core A2 government, matching the established `o + Locative` and case-pair conventions. |
| A2/A2 common | `kochać` idea/place and strong-liking rows; `wiedzieć` interrogative; `korzystać` benefit-from; `uczyć` A1, A2, A4, A5 | Structurally simple but semantically later, or lower-frequency than the core row of the same lemma. Interrogative rows follow the frozen A2/A2 convention. |
| A2/B1 common | `wiedzieć` `że`; `przepraszać` `że`; `życzyć` `żeby`; `uczyć` `że` | The established Batch 1–6 value for `że`/`żeby` content clauses. |

**Recognition-only decisions: none.** No Batch 7 row is marginal enough to
withhold production, and `recognition-only` must never be used to park an
authoring concern. All 23 rows are `active-production`. Every row is
`register: neutral`; 10 rows are `priority: core` and 13 are `priority: common`.

## 5. Examples, lexical identity and provenance

All 23 Polish sentences are **unique**; all 23 English translations happen to
be unique as well, though translation uniqueness is not a requirement —
naturalness outranks it (Phase 4B4 precedent).

**Every required complement is realized in its example.** The three special
realization requirements are met:

- `jeść` — the single all-optional row realizes **both** optional complements:
  *Dziecko je zupę łyżką* (Accusative `zupę` + Instrumental `łyżką`).
- `przepraszać` `że` row — realizes the **optional** person (`cię`), while the
  explanation states the optionality.
- `uczyć` school-subject row — realizes the **optional** learner (`dzieci`).

**Aspect / lexical-identity audit.** The finite verb token of all 23 sentences
was inspected individually against the exact authored lemma:

`muszę` · `wiem` ×4 · `je` · `piję` · `kocham` ×2, `kocha`, `kochają` ·
`przeprasza`, `przepraszam` · `życzę` ×2 · `korzystam`, `korzystają` ·
`uczy` ×5, `uczą`

All are imperfective forms of the authored lemma. No perfective partner
(`przeprosić`, `skorzystać`, `nauczyć`, `wypić`, `zjeść`) appears as the main
verb — the tokens `nauczyciela` and `Nauczycielka` in two `uczyć`/`przepraszać`
examples are the **nouns** "teacher", explicitly checked and excluded, not the
perfective verb. **No `uczyć` example contains `się`** and **no `życzyć`
example contains `sobie`**, so neither lexical identity drifts to `uczyć się`
or `życzyć sobie`.

**Quiet-reuse / provenance (two layers, honestly scoped).**

- **Layer A — indexed product corpus.** All 23 sentences were compared against
  every indexed entity via `priority7_tooling.repository_index_from_root`
  (1665 entities, zero index issues), on the addressable fields `card.pl`,
  `card.ex`, `drill.prompt`, `drill.answer`. **Zero exact matches.**
- **Layer B — broad supplemental raw-text scan.** Substring scan of all 23
  sentences across 380 repository text/data files (17,425,266 bytes;
  `.json/.js/.md/.csv/.txt/.html/.ts/.jsx/.py/.yml/.yaml`, excluding `.git`,
  `node_modules`, `__pycache__`). **Zero hits.**

Both layers are clean, so **all 23 examples are `editorial-generated`** and
zero `repository-reuse` claims are made. No sentence was rewritten to dodge a
collision, because no collision was found.

## 6. Frozen semantic treatments carried into staging

- **`musieć`** — one meaning, one infinitive pattern. Personal and zero-subject
  realization is recorded in `internalScope` and the learner explanation as a
  sentence-level fact; no second pattern, no second meaning, no subject,
  impersonal or question complement.
- **`wiedzieć`** — four alternatives under one meaning. The optional
  generalized `SKĄD` is recorded in `internalScope` as **verified but
  unrepresented**, never as unsupported or rejected; no `od`/`z` or other
  source preposition exists anywhere in the record. The interrogative row uses
  `clauseKind: interrogative`; its example realizes it with `czy`, and the
  explanation teaches `czy` as one realization alongside `gdzie`/`kiedy`.
- **`jeść`** — the one all-optional row, `role: means` on the Instrumental per
  the frozen matrix. The learner explanation states the boundary explicitly and
  correctly: the Genitive after a negated verb is **the general Polish rule for
  negated objects, correct Polish**, and is simply not authored here as a
  lemma-specific pattern. Nothing implies it is ungrammatical.
- **`pić`** — one required Accusative; the animate-subject restriction is
  carried in `internalScope` only.
- **`kochać`** — three meanings with distinct `internalScope`, distinct
  `glossesEn`, distinct explanations and deliberately contrasting examples: a
  person (`babcię`), a place bond (`swoje rodzinne miasto`), and an everyday
  preference (`czekoladę`). The infinitive belongs to `strong-liking` alone.
- **`przepraszać`** — `role: interlocutor` on the person in both rows, with the
  requiredness asymmetry preserved exactly (`true` with `za`, `false` with
  `że`) and no combined row.
- **`życzyć`** — required Dative in both rows, Genitive and `żeby` as strict
  alternatives, no infinitive, no `sobie` anywhere.
- **`korzystać`** — two meanings over one identical `z + Genitive` shape with
  `role: object` on both, per the frozen matrix. The split is carried entirely
  by editorial fields and by sharply contrasting examples (public transport as
  a service versus student discounts as an advantage).
- **`uczyć`** — six strict alternatives, non-reflexive throughout. Sense-2
  `GDZIE` is recorded in `internalScope` as **verified but unrepresented**; no
  `w`, `na`, `u` or any other place government exists in the record, and the
  school-subject example deliberately contains no place phrase at all.

## 7. Clause inventory

Exactly **6** clause rows, matching the frozen matrix: `ze` ×3
(`wiedzieć`, `przepraszać`, `uczyć`), `interrogative` ×2 (`wiedzieć`,
`uczyć`), `zeby` ×1 (`życzyć`). **Zero `direct-speech`** and **zero
`clauseKind: czy`** in Batch 7. A surface `czy` appears only inside one example
sentence, as a realization of `clauseKind: interrogative`.

## 8. Live guards — 57 → 72

`tests/fixtures/priority8_phase4b_authoring_rules.json` now contains
**72 rules** at `registryVersion 2`: the 57 existing rules unchanged plus
exactly the **15** approved Batch 7 proposals, with the matrix rule IDs and
configurations verbatim. No rule was renamed, no sixteenth Batch 7 rule was
added, and the guard interpreter
`tests/test_priority8_phase4b_authoring_guards.py` is **unchanged**.

| Ref | Rule ID | Primitive |
|---|---|---|
| A | `p8-4b-musiec-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| B | `p8-4b-wiedziec-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| C | `p8-4b-wiedziec-authorized-preposition-cases` | `allow-only-preposition-case-signatures` |
| D | `p8-4b-jesc-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| E | `p8-4b-jesc-no-lexical-genitive` | `forbid-complement-match` |
| F | `p8-4b-pic-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| G | `p8-4b-pic-no-lexical-genitive` | `forbid-complement-match` |
| H | `p8-4b-kochac-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| I | `p8-4b-przepraszac-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| J | `p8-4b-przepraszac-authorized-preposition-cases` | `allow-only-preposition-case-signatures` |
| K | `p8-4b-zyczyc-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| L | `p8-4b-korzystac-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| M | `p8-4b-korzystac-authorized-preposition-cases` | `allow-only-preposition-case-signatures` |
| N | `p8-4b-uczyc-exact-pattern-shapes` | `require-exact-pattern-shapes` |
| O | `p8-4b-uczyc-authorized-preposition-cases` | `allow-only-preposition-case-signatures` |

The registry validates as configuration and against live staging targets, and
`guard_issues` reports **no issues** on the authored corpus.

### 8.1 One authorized additional path

Adding any rule breaks `tests/test_priority8_phase4b6_batch06.py`, which pinned
`assertEqual(57, len(registry["rules"]))` — a **moving-state** assertion of
exactly the kind that file's own docstring says it avoids, and the only such
assertion in Batches 1–6 (Batches 1–5 assert rule *presence* only). With
explicit authorization, that single assertion was replaced by
`assertGreaterEqual(len(registry["rules"]), 57)` plus a comment. Batch 6's
digest, matrix SHA-256, all 21 guard-presence assertions and every other
assertion are untouched, and its 24 tests still pass. The new Batch 7 lock
deliberately uses the same presence-plus-lower-bound form so it can never
block Phase 4C.

## 9. Mutation proof

29 structural mutations were applied to **in-memory deep copies only** (both
target files verified byte-identical before and after). Every one is caught:

| Lemma | Mutation | Caught by |
|---|---|---|
| `musieć` | duplicate the infinitive pattern | A |
| `musieć` | invent a separate impersonal/subject pattern | A |
| `wiedzieć` | add `od + Genitive` source concretization | B, C |
| `wiedzieć` | add `z + Genitive` source concretization | B, C |
| `wiedzieć` | replace `interrogative` with `czy` | B |
| `wiedzieć` | merge `że` + interrogative into one row | B |
| `jeść` | promote optional Accusative to required | D |
| `jeść` | promote optional Instrumental to required | D |
| `jeść` | add lexical Genitive pattern | D, E |
| `jeść` | split optional participants into standalone rows | D |
| `pić` | add Genitive/partitive row | F, G |
| `kochać` | move infinitive into `person-love` | H |
| `kochać` | merge the three meanings | H |
| `kochać` | add `za + Accusative` collocation frame | H |
| `przepraszać` | make `za`-schema person optional | I |
| `przepraszać` | make `że`-schema person required | I |
| `przepraszać` | combine `za` + `że` | I |
| `życzyć` | combine Genitive + `żeby` | K |
| `życzyć` | add infinitive row | K |
| `życzyć` | remove the required Dative | K |
| `korzystać` | merge the two meanings | L |
| `korzystać` | add unauthorized preposition (`do + Genitive`) | L, M |
| `uczyć` | build maximal Acc+Gen+Infinitive frame | N |
| `uczyć` | add `w + Locative` school place | N, O |
| `uczyć` | add `na + Locative` GDZIE concretization | N, O |
| `uczyć` | promote school-sense learner to required | N |
| `uczyć` | import bare `uczyć się` Genitive shape | N |
| `uczyć` | import bare `uczyć się` infinitive shape | N |
| `uczyć` | merge `że` + interrogative alternatives | N |

### 9.1 Expected non-enforceable semantic limitations

These are **not guard failures**; they are the frozen matrix's documented
limits, reproduced here empirically:

| Probe | Result |
|---|---|
| `kochać` — swap the three structurally identical Accusative rows between `person-love`, `idea-or-place-attachment` and `strong-liking` | **EXPECTED NON-ENFORCEABLE SEMANTIC LIMITATION** — not caught |
| `korzystać` — swap the two identical `z + Genitive` rows between `resource-use` and `benefit-from-advantage` | **EXPECTED NON-ENFORCEABLE SEMANTIC LIMITATION** — not caught |

Two further limitations are structural-by-nature and are not overclaimed: no
guard primitive reads example text, so nothing structural prevents a future
`życzyć` example from drifting to `życzyć sobie` or a future `uczyć` example
from using `uczyć się`. Guard N does make the *bare* released `uczyć się`
complement shapes unauthorable on `uczyć`, and the rule-target identity check
pins both canonical lemma strings, but example wording remains an editorial and
review responsibility.

## 10. Digests

New Batch 7 digest, over the standard historical projection
(`verificationOrder`, `canonicalLemma`, `aspect`, `phase3Disposition`,
`phase3Evidence`, `bindingConstraints`, `candidateContent`,
`metadataAspectPartner`, `requiredLexicalItems`):

`88aed6dc4b972ddc3ce7ea18b5e987d95ae1f38d5eb5a742a45be7332c372672`

Batches 1–6 recomputed after authoring and **unchanged**:

| Batch | Digest |
|---|---|
| B1 | `3849e0082e59e0984e7082c35e5b492eb3a228706aab2a7323575a5a9f9e619e` |
| B2 | `dd55047bbd7db3d28224d6366015c7353479206e4ffba64cf8b6397efb8d8db8` |
| B3 | `8276864944181e47b573767151e98b556b52037b7920335d32fb510aeee58edb` |
| B4 | `7f8fd8840d7aadeffbd23a5047cf8ce200b07c84c41520835a11f575c698b4f2` |
| B5 | `d84939a803de1e7513bec822e2e707e93b0090e3bff2251658d058b99e7ed951` |
| B6 | `cff207b6e728fb203ba05a9ba94915432957be76101b3bd6a0f65137cdda98d5` |

## 11. Final cumulative content state

| Quantity | Before | Batch 7 | After |
|---|---:|---:|---:|
| authored lemmas | 59 | +9 | **68** |
| meanings | 82 | +13 | **95** |
| patterns | 201 | +23 | **224** |
| examples | 201 | +23 | **224** |
| future-empty | 9 | −9 | **0** |

`phaseStep` is now `4B7` and `stagingRevision` is `8`;
`stagingSchemaVersion` remains `1`. All 68 records remain
`stagingReviewStatus: draft`.

Every frozen full-pattern record now carries `candidateContent`. **This does
not mean Phase 4B is approved**: independent Batch 7 review and the final
68-lemma reconciliation still follow.

## 12. Tests

| Suite | Tests | Result |
|---|---:|---|
| `test_priority8_phase4b0_staging.py` | 31 | OK |
| `test_priority8_phase4b1a_authoring_schema.py` | 65 | OK |
| `test_priority8_phase4b1_batch01.py` | 9 | OK |
| `test_priority8_phase4b2_batch02.py` | 11 | OK |
| `test_priority8_phase4b3_batch03.py` | 17 | OK |
| `test_priority8_phase4b4_batch04.py` | 23 | OK |
| `test_priority8_phase4b5_batch05.py` | 29 | OK |
| `test_priority8_phase4b6_batch06.py` | 24 | OK |
| `test_priority8_phase4b7_batch07.py` | 27 | OK |
| `test_priority8_phase4b_progress.py` | 8 | OK |
| `test_priority8_phase4b_authoring_guards.py` | 26 | OK |
| **combined** | **270** | **OK** |

`python3 validate_priority8_staging.py` reports
`PASS: Priority 8 4B7 staging revision 8 is read-only valid (68 lemmas, 21
constrained records, 12 global constraints).`

The new historical Batch 7 lock protects the exact lemma set and order, the
9/13/23/23 counts, one example per pattern, ownership scopes, key validity and
key-shape hygiene, `lexical-frame` on all 23 rows, provenance truthfulness,
quiet-reuse absence, the matrix SHA-256, the Batch 7 guard IDs, the
deterministic Batch 7 digest, and every targeted per-lemma invariant listed in
§6–§7. Following the Batch 1–6 future-safe architecture, it pins **no** moving
lifecycle state: not `phaseStep`, not `stagingRevision`, not the future-empty
count, not review status beyond the allowed lifecycle vocabulary, and not the
registry total.

## Final reconciliation correction note (2026-08-25)

The final Phase 4B reconciliation preserves the historical Batch 7 account
above and supersedes only the following live editorial fields:

- `musieć`: learner explanation shortened to the accepted construction-focused
  wording.
- `jeść`: learner explanation returns negation to sentence-grammar ownership
  and retains the no-lexical-Genitive boundary.
- `kochać/strong-liking`: glosses are now `really like` and
  `love (a thing or an activity)`.
- `przepraszać/accusative-person-ze-explanation`: English is now `I apologise
  to you for not calling yesterday.`; Polish is unchanged.
- `życzyć/dative-recipient-zeby-wished-event`: the accepted literal-gloss
  explanation now makes the required Dative visible; the example pair is
  unchanged.
- `uczyć/accusative-person-o-locative-taught-topic`: example is now
  `Nauczycielka uczy uczniów o polskich zwyczajach.` / `The teacher teaches
  the pupils about Polish customs.`
- `uczyć/accusative-learner-genitive-school-subject`: example is now
  `Pani Nowak uczy moją córkę matematyki.` / `Mrs Nowak teaches my daughter
  maths.`, with the inline learner gloss updated in lockstep.

The two new Polish `uczyć` sentences remain `editorial-generated`: Layer A
found zero matches in 1,665 indexed entities and Layer B found zero broad
raw-text hits. Pre-reconciliation Batch 7 digest
`88aed6dc4b972ddc3ce7ea18b5e987d95ae1f38d5eb5a742a45be7332c372672`
is superseded by current digest
`a2d34c616d416f6a36f2346a2c4190522f1102087b3745ab0605be29c5430d9e`.
The B7 matrix SHA remains unchanged. The global guard registry is now 74
rules solely because the reconciliation adds two early-batch shape guards;
the 15 Batch 7 rule IDs remain unchanged.
