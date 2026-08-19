# Priority 7 — Current Verb and Case Inventory

**Phase:** 0, reports only  
**Baseline:** branch `priority-7-phase-0-audit`; HEAD `f6bdc73a86f8b114582d52d0380e7289b8f2fe5d`; tree `92e9cdc905ec7ed8f21e784505e501880071704b`  
**Status:** reproducible current-state audit. No content, code, tests, audio, progress, or generated pages were changed.

## Evidence conventions

| Label | Meaning |
|---|---|
| Repository finding | Directly observable in the checked-out source |
| Source finding | Directly observable in the supplied research PDF |
| Supported inference | Reasoned from repository/source evidence but not an approved linguistic rule |
| Requires verification | Needs contemporary reference and competent native/editorial review |
| Recommendation | Proposed future product decision; not implemented |

## 1. Repository corpus

| Corpus | Topics | Vocabulary cards | Teach items | Drills / scene material |
|---|---:|---:|---:|---:|
| A1 | 15 | 340 | — | — |
| A2 | 22 | 514 | — | — |
| B1 | 17 | 312 | — | — |
| Grammar Cases | 7 | — | 49 | 99 drills |
| People & Numbers | 7 | — | 47 | 86 drills |
| Politeness | 5 | — | 23 | 52 drills |
| Building Sentences | 4 | — | 19 | 44 drills |
| Verbs | 9 | — | 44 | 72 drills |
| Scenarios | 8 | — | — | 102 nodes / 194 learner options |
| Podcasts | 3 | 49 | — | — |
| **Validated total** | **97** | **1,215** | — | **353 drills** |

The 1,215-card total is exactly 1,166 A1/A2/B1 cards plus 49 podcast cards. The validator reports 10 levels, 97 topics, 1,215 cards, 353 drills and 1,675 stable IDs. Sources: [`validate_content.py`](../validate_content.py), [`data-a1.js`](../data-a1.js), [`data-a2.js`](../data-a2.js), [`data-b1.js`](../data-b1.js), [`data-grammar.js`](../data-grammar.js), [`data-verbs.js`](../data-verbs.js), [`data-scenarios.js`](../data-scenarios.js), and [`data-podcasts.js`](../data-podcasts.js).

## 2. Defensible verb-inventory rule

The repository has no `lemma` or part-of-speech field. For overlap work, an “existing Po polsku verb” therefore means a lexical card satisfying all of these mechanical conditions:

1. the Polish `pl` label is infinitive-headed;
2. its first token ends in `-ć` or `-c` (covering forms such as `móc` and `piec`);
3. the English gloss begins with `to …` or contains `/ to …`;
4. immediate `się` remains part of the lemma;
5. any following words remain on the card as a phrase/collocation, while the leading infinitive is the primary lemma candidate.

Normalization is NFC Unicode, case-folding, surrounding/duplicate whitespace removal only. Polish diacritics, `się`, aspect, and multiword wording are not erased. Grammar examples, drill sentences, scenario utterances, and finite-form cards are evidence but are not primary headwords.

This rule is intentionally narrow. It excludes four obvious pair-backed finite/sentence forms—`zepsuł się`, `robiłem`, `mówiłem`, and `Zgadzam się z tobą`—which belong in a manual mapping queue, not an exact headword match.

## 3. Headline verb inventory

| Scope | Strict cards | Distinct primary lemmas | Standalone cards | Phrase cards | `się` cards / lemmas |
|---|---:|---:|---:|---:|---:|
| A1–B1 core | 204 | 163 | 140 | 64 | 29 / 27 |
| Core plus podcasts | 228 | 181 | 140 | 88 | 35 / 33 |

Core distribution is A1 50, A2 61, B1 93. Podcasts add 24 infinitive-headed phrase cards but no standalone lemma cards. The repository-wide lexical set contains 218 distinct normalized card surfaces and 181 primary lemma candidates.

Ten exact Polish surfaces are duplicated in the core inventory: `biegać`, `brać prysznic`, `gotować`, `inwestować`, `kochać`, `kupować`, `lubić`, `nosić`, `odpoczywać`, and `oszczędzać`. Different cards can encode different senses or contexts, so duplicate surface is not automatically duplicate content. Twenty-five core lemmas, and 28 including podcasts, occur on multiple cards.

The row-level evidence is in [`priority-7-existing-verbs.csv`](priority-7-existing-verbs.csv). It preserves card IDs, surfaces, glosses, phrase/lemma classification, current activity eligibility, free-text pair data, case-name evidence, and overlap audit status.

## 4. How verbs are represented now

| Concern | Current representation | Consequence |
|---|---|---|
| Lemma | Inferred from `pl` text | Finite forms and phrases require manual classification |
| Meaning | English `en`, sometimes `hint`/examples | One card is not a stable meaning entity |
| Reflexivity | Textual `się` | No explicit Boolean or semantic subtype |
| Aspect | Free-text `pair`; sometimes `relationType` | Cannot be parsed into approved aspect semantics safely |
| Government | Free-text `hint`, `pattern`, examples, notes, drills | Not queryable or reusable as structured data |
| Relationships | `relatedIds`, `relationType`, `senseGroups` | Card-level relations, not lemma→meaning→pattern relations |
| CEFR | Level/topic location | No accepted per-card CEFR field |
| Stable identity | Card/topic IDs | IDs describe content placement, not linguistic identity |

Of the 204 core verb cards, 151 have a `pair`: 133 slash-separated strings and 18 one-sided annotations. Only 17 also carry `relationType: "aspect-pair"`; six carry contrast relations. The free text includes unsafe cases for automatic interpretation, including `szukać / znaleźć`, inflected pairs such as `robiłem / zrobiłem`, and inconsistent `oszczędzać` partners across duplicate cards. `pair` must therefore remain research evidence until reviewed row by row.

The current closed card schema has no `lemma`, `meaningId`, `case`, `preposition`, `question`, provenance, or review-state fields ([`validate_content.py:813`](../validate_content.py#L813), [`validate_content.py:1955`](../validate_content.py#L1955)). `relatedIds` is reciprocal card-to-card metadata; `senseGroups` governs answer/distractor grouping rather than lexical equivalence.

## 5. Existing case teaching

All seven Polish cases have a dedicated seven-item explanation sequence and drills in [`data-grammar.js`](../data-grammar.js):

| Case | Topic starts | Drills | Choose / build | Existing verb-trigger emphasis |
|---|---:|---:|---:|---|
| Nominative | line 13 | 14 | 10 / 4 | subject and `to jest` contrast |
| Genitive | line 145 | 14 | 10 / 4 | negated direct objects; `szukać` |
| Dative | line 280 | 14 | 9 / 5 | `dawać`, `pomagać`, `mówić`, `dziękować`, `ufać`, `wierzyć` |
| Accusative | line 418 | 15 | 10 / 5 | direct objects; `pytać o`, `prosić o` |
| Instrumental | line 555 | 14 | 10 / 4 | `interesować się`, `zajmować się`, `rozmawiać z` |
| Locative | line 688 | 14 | 10 / 4 | `rozmawiać o`, `myśleć o` |
| Vocative | line 825 | 14 | 10 / 4 | direct address; no artificial case question |

Across 1,166 core vocabulary cards, 72 distinct cards contain 73 literal English/Polish case-name mentions: Nominative 1, Genitive 37, Dative 4, Accusative 11, Instrumental 12, Locative 8, Vocative 0. Podcast cards add nine mentions. This count measures explicit labels, not every case-bearing example. Only 27 of the 204 strict core verb cards explicitly name a case; nine podcast verb-phrase cards do so.

Nine of 25 template cards encode a case name inside human-readable `pattern` text (six Genitive, two Accusative, one Locative). Templates are excluded from normal practice and remain unstructured.

## 6. Strong implicit government already present

| Construction | Current evidence | Classification |
|---|---|---|
| `szukać + Gen` | A1 card plus Genitive build drill | explicit card and exercise |
| `pomagać + Dat` | A1 card, Dative explanation and drills | explicit multi-surface |
| `czekać na + Acc` | A1 card and later relative-clause drill | explicit, weak scenario reuse |
| `słuchać + Gen` | A1 card | explicit card-only |
| `uczyć się + Gen` | A1 example, reflexive lesson, A2 lemma card | repeated, distributed |
| `potrzebować + Gen` | A2 template, examples, comparisons, pharmacy/doctor scenarios | strong implicit/contextual; no strict lemma card |
| `prosić o + Acc` | A2 template, Accusative teaching, shops scenario note/recap | strong but meaning-sensitive |
| `interesować się + Instr` | A2 card, explanation and drills | explicit multi-surface |
| `używać + Gen` | A2 card and gym scenario note | explicit/contextual |
| `płacić + Instr`; `za + Acc` | cards and pharmacy/shops/city scenarios | means/method relationship plus prepositional frame; internal relation classification unresolved |
| `bać się + Gen` | B1 card | explicit; `bać się o` not currently taught |
| `rozmawiać z + Instr`; `o + Loc` | separate case explanations/drills | correct but split across case silos |
| `tęsknić za + Instr`, `wybaczyć + Dat`, `dbać o + Acc` | B1 cards/examples | authored B1 expansion evidence |

These are repository findings, not a blanket linguistic approval. Every proposed production pattern still needs contemporary reference review, competent native review, and owner approval.

## 7. Activity exposure of the strict core set

| Activity | Eligible strict core verb cards | What it currently tests |
|---|---:|---|
| Flashcards | 204 | card surface and translation |
| Search | 204 | topic substring discoverability, not direct card results |
| Type It | 190 | translation to canonical Polish card text |
| Listening | 191 | heard Polish card text to English meaning |
| Per-topic Mixed | 204 | existing card-level modes/progress |

Only two strict core verb cards have `typeItCue`. The answer engine accepts canonical `pl` plus explicit `acceptedAnswers`; it does not split slash pairs ([`pp-answer.js:147`](../pp-answer.js#L147)). Current exposure therefore must not be mistaken for verb-government practice.

## 8. Known consistency and uncertainty flags

- `a1-food-basics-023` labels `nie lubię` as “+ accusative,” while its own example is Genitive and the Genitive lesson explicitly teaches Accusative→Genitive under negation ([`data-a1.js:308`](../data-a1.js#L308), [`data-grammar.js:160`](../data-grammar.js#L160)). This needs correction review in a later approved phase; Phase 0 did not edit it.
- `chcieć` is named among Accusative triggers, while the modal lesson discusses a Genitive noun complement and colloquial Accusative. The scope/register distinction needs contemporary native review ([`data-grammar.js:433`](../data-grammar.js#L433), [`data-verbs.js:477`](../data-verbs.js#L477)).
- “Certain verbs always take a Dative object” is pedagogically useful but may be too absolute once meaning-specific frames are modeled.
- Case-connected material is not uniformly lexical government: Phase 1 must distinguish `płacić` method, `być`/`to jest` predication and `podobać się` subject/experiencer structure as far as the product model requires.
- Literal case-name counts understate implicit `kogoś/coś/komuś` guidance and examples; they are an explicit-label metric only.
- The strict inventory is reproducible, not exhaustive. It intentionally excludes finite forms, sentence cards, examples, and scenario occurrences.

## 9. Audit conclusion

Po polsku already contains substantial verb/case teaching, but its linguistic facts are distributed across case lessons, lexical cards, templates, free-text hints, drills, and scenarios. The repository can support a high-value pilot without rewriting current cards, but it does not currently have a stable lemma→meaning→pattern layer. The safe next step is specification and validation tooling, not automatic extraction of `pair` or government prose.
