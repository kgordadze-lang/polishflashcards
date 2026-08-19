# Priority 7 — Case Coverage and Gap Analysis

**Phase:** 0, reports only  
**Finding:** all seven cases are explicitly taught and drilled; the principal Priority 7 gap is the missing verb-centered connection across those case silos.

## 1. Dedicated case curriculum

Every case topic in [`data-grammar.js`](../data-grammar.js) contains seven teaching items. The 99 case drills comprise 69 choose and 30 build drills, as itemized below.

| Case | Start | Core teaching | Questions/learner cue | Drills (choose/build) |
|---|---:|---|---|---:|
| Nominative | 13 | subjects, naming, `to jest` | `kto? co?` | 14 (10/4) |
| Genitive | 145 | possession/absence, quantities, prepositions, negated direct objects | `kogo? czego?` | 14 (10/4) |
| Dative | 280 | recipient/beneficiary and selected verbs | `komu? czemu?` | 14 (9/5) |
| Accusative | 418 | affirmative direct object and selected prepositional frames | `kogo? co?` | 15 (10/5) |
| Instrumental | 555 | means/role, `z`, selected reflexive verbs | `kim? czym?` | 14 (10/4) |
| Locative | 688 | location/topic after prepositions | `o kim? o czym?`, `gdzie?` | 14 (10/4) |
| Vocative | 825 | direct address | functional cue; no artificial question | 14 (10/4) |

The wording is mostly consistent. A small Dative presentation mismatch lists `komu? czemu?` but translates only “to whom?” ([`data-grammar.js:284`](../data-grammar.js#L284)). Vocative correctly avoids inventing a question.

## 2. Verb triggers already taught by case

| Case silo | Existing verb-centered material | Coverage quality |
|---|---|---|
| Nominative | `to jest` versus role/profession with `być` | useful construction contrast, not a general verb index |
| Genitive | scoped Accusative→Genitive rule under direct-object negation; `szukać` drill | strong rule teaching; selected lexical triggers scattered elsewhere |
| Dative | `dawać/dać`, `pomagać`, `mówić/powiedzieć`, `dziękować`, `ufać`, `wierzyć` | strongest trigger list, but wording can sound absolute |
| Accusative | direct-object verbs plus `pytać o` and `prosić o` | strong foundation; meaning distinctions are not centralized |
| Instrumental | `interesować się`, `zajmować się`, `rozmawiać z` | strong examples and two interest drills |
| Locative | `rozmawiać o`, `myśleć o` | strong case-side teaching |
| Vocative | address forms | not a verb-government priority |

The clearest architectural gap is `rozmawiać`: `z + Instrumental` and `o + Locative` are taught correctly in different topics, but nothing presents one lemma with two meaning/role-aware patterns.

## 3. Explicit labeling outside grammar

The 1,166 A1/A2/B1 cards contain 72 distinct cards with 73 literal case-name mentions:

| Case name | Mentions |
|---|---:|
| Nominative | 1 |
| Genitive | 37 |
| Dative | 4 |
| Accusative | 11 |
| Instrumental | 12 |
| Locative | 8 |
| Vocative | 0 |

Podcast cards add nine more: one Dative, four Accusative, two Instrumental and two Locative. Scenario guidance—127 option notes, 15 tips and 32 recap bullets—contains 21 Genitive, four Dative, 14 Accusative and 10 Instrumental name mentions.

These are literal-label counts, not total grammatical coverage. Many useful examples use case questions or correct endings without spelling out the English/Polish case name. Conversely, a named case does not mean the underlying claim has been reviewed for Priority 7.

## 4. Government is rich but fragmented

| Candidate | Card/template | Case lesson/drill | Scenario/context | Gap |
|---|---|---|---|---|
| `potrzebować + Gen` | template and repeated examples | comparison material | 8 authored entries across 5 scenarios; 3 guidance entries | no strict lemma card or reusable pattern entity |
| `pomagać + Dat` | A1 card | explanation/drills | 5 entries across 3 scenarios; 1 guidance entry | English “help” hides Dative; frames with `z + Instr` need modeling |
| `używać + Gen` | A2 card | — | 3 gym entries; 1 explicit note | strong content, weak cross-navigation |
| `szukać + Gen` | A1 card | dedicated build | one city narrative hit | contextual gap; unsafe `pair` semantics with `znaleźć` |
| `prosić o + Acc` | A2 template | Accusative explanation | shops learner line, note and recap | must distinguish addressee and requested thing; contrast `pytać` |
| `płacić + Instr` / `za + Acc` | several cards | Instrumental foundation | 8 entries across pharmacy/shops/city; 2 guidance entries | separate the means/method relationship from the prepositional frame; classify the former in Phase 1 |
| `czekać na + Acc` | A1 card | relative-clause drill | only one non-government scenario note | common pattern lacks contextual reinforcement |
| `interesować się + Instr` | A2 card | explanation/drills | no scenario occurrence | strong formal coverage, no scenario reuse |
| `rozmawiać z/o` | no strict lemma card | split across Instrumental/Locative | no scenario occurrence | no shared lemma view |
| `bać się + Gen` | B1 card | — | no scenario occurrence | meaning-sensitive `bać się o` absent |

Scenario counts are authored-entry counts, not learner exposure counts; branching means each learner sees a subset. Scenarios currently provide context and explanatory notes, not scored assessment.

## 5. Principal gaps

### 5.1 Case-first only

A learner can open “Dative” and discover several triggers, but cannot reliably open `pomagać` and see what follows. There is no bidirectional lemma/case index, no meaning layer, and no structured way to connect one lemma to several complements.

### 5.2 Free-text facts cannot be reused safely

Government lives in `hint`, `pattern`, `ex`, scenario notes, recap bullets, and drill explanations. Search, activities, audio collection, and generated pages cannot distinguish a rule from display prose or an example.

### 5.3 English often erases the trigger

Translations such as “need,” “help,” “listen to,” “wait for,” and “ask” communicate meaning but do not reveal Polish case or role assignment. Bare translation practice therefore does not test the missing skill.

### 5.4 Multi-pattern verbs do not fit one-case summaries

`rozmawiać`, `płacić`, `wierzyć`, `bać się`, `pytać`, `prosić`, `mówić`, `być`, and `zależeć` require meaning/role-aware frames. Encoding `lemma → one case` would introduce errors immediately.

The same case-shaped representation can also conceal different syntactic relationships. `być` + Instrumental and `to jest` + Nominative are predicative/constructional, `płacić` + Instrumental method may be means/method or adjunct-like, and `podobać się` distributes subject and experiencer roles. Phase 1 must approve the smallest distinction needed to keep these from being mislabeled as ordinary lexical government.

### 5.5 Cross-case practice is not coverage-guaranteed

Case Mix uniformly samples 15 of the 99 case drills. Because the source pool has 14 drills per case except 15 Accusative, a round has an approximately 48.9% chance of omitting at least one case. It is valid mixed practice, but it cannot prove seven-case coverage and has no verb-pattern stratification.

## 6. Consistency questions requiring review

1. `a1-food-basics-023` says `nie lubię + accusative`; its example and the scoped Genitive-negation lesson use Genitive. This is a high-priority content-consistency review, not a Phase 0 edit.
2. The treatment of `chcieć` differs between the Accusative trigger list and the modal lesson's Genitive/colloquial-Accusative note. The intended standard, register and teaching level need native review.
3. “Certain verbs always take a Dative object” should be reviewed against meaning-specific frames; “this meaning takes…” is safer for Priority 7.
4. Case questions should be attached to the complement they explain. A single loose question field is inadequate for patterns with two complements.
5. The internal relationship distinction must be tested on lexical, preposition-governed, predicative, means/method and subject/experiencer examples without forcing that taxonomy into learner copy.

## 7. Recommended gap-closing principle

Keep the current case lessons as case-first foundations. Add a separate, reviewed lemma→meaning→pattern layer that can point back to selected cards, drills and scenarios without changing them. The learner-facing bridge should answer: “For this meaning, what comes next?” Phase 1 should specify that bridge; it should not rewrite the seven-case curriculum.
