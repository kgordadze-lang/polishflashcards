# Priority 7 — 30-Verb Pilot Ranking

**Phase:** 0 research shortlist  
**Release status:** none of these patterns is linguistically approved or implemented. Every row requires contemporary verification, competent native review and product-owner approval.

The machine-readable detail is in [`priority-7-pilot-ranking.csv`](priority-7-pilot-ranking.csv). Candidate complements, current repository references, source scope and the full 100-verb expansion pool are in [`priority-7-pattern-candidates.json`](priority-7-pattern-candidates.json).

## 1. Ranking method

Candidates were judged on nine integer component scales. The component values, formula inputs and calculated result are stored in the CSV, so every score can be reproduced without editorial inference.

| Component | 1 | 3 | 5 | Weight |
|---|---|---|---|---:|
| Everyday utility | rare/specialized | useful in recurring situations | core everyday communication | +4 |
| Current repository support | absent or incidental | one useful teaching/context anchor | rich, reusable teaching and context support | +3 |
| Beginner value | mainly later-level value | useful around A2 | foundational A1–A2 need | +3 |
| Learning payoff | little new case-pattern learning | useful reinforcement | highly non-obvious or transfer-prone relationship | +4 |
| Exercise determinism | difficult to close safely | deterministic with substantial context | naturally supports one closed answer | +2 |
| Context reuse | no useful current context | one reusable context | several strong cards/drills/scenarios | +2 |
| Contrast value | little useful contrast | one useful comparison | central cross-case/meaning contrast | +2 |
| Ambiguity | low | meaning or prompt needs care | strongly polysemous/role-ambiguous | −2 |
| Review burden | low | meaningful expert review needed | unusually high or weakly evidenced | −1 |

For all scales, 2 and 4 are the intermediate points between the stated anchors. Higher ambiguity and review-burden values are penalties. The score is:

`4×utility + 3×current support + 3×beginner value + 4×learning payoff + 2×determinism + 2×context + 2×contrast − 2×ambiguity − review burden`

This is a transparent prioritization heuristic, not corpus frequency or linguistic confidence. No external web/corpus research was authorized. Ties are resolved mechanically by: lower ambiguity; lower review burden; higher current support; then the NFC lemma in ascending Unicode code-point order. The ranking favors patterns where English translation does not reveal the Polish complement and balances direct cases, preposition+case frames, reference contrasts and multi-pattern verbs.

## 2. Recommended pilot

| Rank | Score | Lemma | Approx. CEFR | Provisional learner-relevant pattern(s) | Current support | Main reason / risk |
|---:|---:|---|---|---|---|---|
| 1 | 92 | `pomagać` | A1 | direct Dative | A1 card; Dative drills; scenarios | practical and contrastive; addressee/frame context required |
| 2 | 92 | `szukać` | A1 | direct Genitive | A1/A2/B1 cards; Genitive drill | high payoff; `szukać/znaleźć` is not a safe automatic aspect pair |
| 3 | 92 | `słuchać` | A1 | direct Genitive | A1 card | strong English mismatch; contrast with `słyszeć` |
| 4 | 91 | `czekać` | A1 | `na` + Accusative | A1 card; grammar reuse | common and deterministic; source sample entry available |
| 5 | 89 | `potrzebować` | A1 | direct Genitive | templates, examples, drills, 5 scenario topics | excellent reuse; lacks strict lemma card |
| 6 | 88 | `dziękować` | A1 | Dative addressee + `za` + Accusative reason | Dative teaching; formulas/scenarios | two complements; bare “thank” prompt is underspecified |
| 7 | 88 | `płacić` | A1–A2 | Instrumental method; `za` + Accusative item | 3 primary cards; pharmacy/shops/city | method may be means/adjunct-like rather than ordinary lexical government; classify in Phase 1 |
| 8 | 88 | `uczyć się` | A1 | direct Genitive | A1/A2 and verb lesson | app-relevant and reflexive; distinguish senses of “study/teach” |
| 9 | 87 | `używać` | A2 | direct Genitive | A2 card; gym note | high payoff and exercise-friendly; contrast with `korzystać z` later |
| 10 | 85 | `interesować się` | A2 | direct Instrumental | A2 card; explanation/drills | strong existing support; keep reflexive/non-reflexive meanings separate |
| 11 | 85 | `dbać` | A2 | `o` + Accusative | B1 card | practical and non-obvious; distinguish “care” senses |
| 12 | 85 | `prosić` | A1 | Accusative addressee + `o` + Accusative request | template, Accusative lesson, shops scenario | core request language; must separate from `pytać` |
| 13 | 83 | `tęsknić` | A2 | `za` + Instrumental | B1 card/drill reuse | emotionally useful; English “miss” is ambiguous |
| 14 | 82 | `lubić` | A1 | direct Accusative | A1/B1 cards | useful reference for `podobać się`; negation inconsistency must be resolved |
| 15 | 82 | `znać` | A1 | direct Accusative | A1 card; Accusative teaching | useful reference; contrast with factual `wiedzieć` and change-of-state `poznać` |
| 16 | 82 | `rozmawiać` | A1–A2 | `z` + Instrumental interlocutor; `o` + Locative topic | both patterns in separate case lessons | ideal cross-case bridge; bare “talk” is unsafe |
| 17 | 82 | `bać się` | A2 | direct Genitive; provisional `o` + Accusative concern | B1 card; source sample entry | meaning-sensitive flagship; second frame requires independent modern review |
| 18 | 82 | `być` | A1 | Instrumental role/profession; `to jest` + Nominative contrast | multiple cards and case teaching; source sample | predicative/constructional contrast, not ordinary direct government; classify in Phase 1 |
| 19 | 81 | `mówić` | A1 | Dative recipient + Accusative content; Dative recipient + `że` clause | A1 card; Dative list | separate case and clause patterns; “say/speak/tell” meanings still need review |
| 20 | 79 | `mieć` | A1 | direct Accusative | many cards and phrases | foundational reference; idiomatic `mieć` meanings must remain separate |
| 21 | 79 | `widzieć` | A1 | direct Accusative | Accusative teaching/examples | reference perception verb; useful contrast with `słyszeć/słuchać` |
| 22 | 79 | `pytać` | A1–A2 | Accusative addressee + `o` + Accusative topic | Accusative lesson; scenario family | contrast with `prosić`; scenario evidence includes another frame |
| 23 | 76 | `myśleć` | A2 | `o` + Locative | Locative teaching | useful but meaning/clause ambiguity makes production context essential |
| 24 | 75 | `znaleźć` | A2 | affirmative direct Accusative | current linked/contrast evidence and drills | useful `szukać` contrast; absent from source index and aspect handling needs review |
| 25 | 74 | `podobać się` | A2 | Nominative stimulus + Dative experiencer | B1 phrase evidence; Dative teaching | high English-to-Polish role reversal; unsafe bare “like” prompt |
| 26 | 72 | `ufać` | A2 | direct Dative | Dative trigger list | practical contrast; no strict lexical card |
| 27 | 70 | `wierzyć` | A2 | direct Dative; provisional `w` + Accusative belief object | Dative teaching | good meaning-dependent pair; requires frame-specific review |
| 28 | 69 | `opiekować się` | A2 | direct Instrumental | weak repository surface evidence | family/health value; higher source/current-support review burden |
| 29 | 69 | `zajmować się` | A2 | direct Instrumental | Instrumental teaching | work utility and architecture stress test; keep non-reflexive meaning separate |
| 30 | 58 | `zależeć` | A2–B1 | `od` + Genitive; provisional Dative experiencer + `na` + Locative | limited repository evidence | valuable multi-construction stress test; recognition-first and highest review risk |

## 3. Balance check

Categories overlap because a meaning can teach more than one relationship.

- Accusative/reference comparisons: `znać`, `lubić`, `widzieć`, `mieć`, `znaleźć`.
- Direct Genitive: `szukać`, `słuchać`, `potrzebować`, `używać`, `uczyć się`, `bać się`.
- Direct Dative/experiencer: `pomagać`, `dziękować`, `mówić`, `ufać`, `wierzyć`, `podobać się`.
- Instrumental-connected: lexical candidates `interesować się`, `zajmować się`, `opiekować się`; the predicative `być` construction and `płacić` means/method use remain Phase 1 relation-classification questions.
- Preposition+case: `czekać`, `prosić`, `pytać`, `rozmawiać`, `myśleć`, `dbać`, `tęsknić`, `zależeć`, `płacić`.
- Meaning-sensitive or multi-pattern: `bać się`, `być`, `mówić`, `pytać`, `prosić`, `płacić`, `podobać się`, `wierzyć`, `zależeć`.

The set deliberately includes several low-complexity reference verbs. They make contrasts teachable and prevent the feature from looking like a list of exceptional cases only.

### Independent-review ranking correction

The review added reproducible components and the deterministic tie-break above. Candidate membership and every calculated score stayed unchanged; 17 positions moved only because the former editorial tie order was removed.

| Lemma | Previous rank | Corrected rank |
|---|---:|---:|
| `pomagać` | 2 | 1 |
| `szukać` | 1 | 2 |
| `dziękować` | 7 | 6 |
| `płacić` | 8 | 7 |
| `uczyć się` | 6 | 8 |
| `interesować się` | 11 | 10 |
| `dbać` | 12 | 11 |
| `prosić` | 10 | 12 |
| `lubić` | 18 | 14 |
| `znać` | 17 | 15 |
| `rozmawiać` | 14 | 16 |
| `bać się` | 15 | 17 |
| `być` | 16 | 18 |
| `mieć` | 22 | 20 |
| `pytać` | 20 | 22 |
| `opiekować się` | 29 | 28 |
| `zajmować się` | 28 | 29 |

## 4. Activity suitability

| Candidate family | Reference/recognition | Choose/build | Type It | Listening |
|---|---|---|---|---|
| Single direct case with concrete noun | strong | strong | contextual cloze only | natural sentence |
| Preposition+case | strong | strong | full context and closed answer set | natural sentence |
| Two complements | progressive disclosure | strong when roles are supplied | usually unsafe from bare English | sentence recognition after teaching |
| Meaning-sensitive multi-pattern | meaning split first | strong contrast choice | unsafe until meaning is explicit | recognition by full sentence |
| Reference contrast (`lubić`/`podobać się`, etc.) | strong | strong | separate prompts, never shared bare gloss | separate contextual examples |

No pilot pattern should enter an activity merely because it exists. Eligibility must default to false and be approved separately for reference, recognition, choose/build, listening and production.

## 5. Source-confidence interpretation

- `sample-detailed-entry` means the demo contains a detailed source entry, but the proposed product treatment is still unapproved.
- `headword-index-only` means the source establishes only that a listed form exists; the detailed pattern must be independently verified.
- `not-in-headword-index` means repository evidence may still justify investigation; the source provides no direct entry support.
- Repository examples and lessons are evidence of current teaching, not proof that every wording or rule is correct.

## 6. Future 100-verb pool

The JSON artifact contains exactly 100 distinct research candidates in three tiers:

- Tier 1: the 30 pilot candidates above.
- Tier 2, next essential (35): `spotykać się`, `cieszyć się`, `zakochiwać się`, `zgadzać się`, `wybaczać`, `pasować`, `brakować`, `przeszkadzać`, `szkodzić`, `sprzyjać`, `radzić`, `doradzać`, `odpowiadać`, `pokazywać`, `dawać`, `kupować`, `jeść`, `pić`, `oglądać`, `słyszeć`, `rozumieć`, `pamiętać`, `zapominać`, `marzyć`, `rezygnować`, `korzystać`, `próbować`, `przestawać`, `zaczynać`, `planować`, `decydować się`, `umawiać się`, `zapraszać`, `informować`, `przepraszać`.
- Tier 3, useful B1 expansion (35): `oskarżać`, `wymagać`, `unikać`, `przestrzegać`, `żądać`, `oczekiwać`, `spodziewać się`, `obawiać się`, `wstydzić się`, `żałować`, `zazdrościć`, `gratulować`, `życzyć`, `zabraniać`, `pozwalać`, `polecać`, `proponować`, `przekonywać`, `namawiać`, `zmuszać`, `zachęcać`, `ostrzegać`, `przypominać`, `przypatrywać się`, `przyglądać się`, `przyzwyczajać się`, `specjalizować się`, `skupiać się`, `zastanawiać się`, `walczyć`, `dążyć`, `należeć`, `wspierać`, `uczestniczyć`, `polegać`.

Tier placement is backlog research priority only. It is not implementation scope or a claim that every listed verb should ship.
