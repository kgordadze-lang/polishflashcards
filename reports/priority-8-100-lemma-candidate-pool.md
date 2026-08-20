# Priority 8 Phase 0 — candidate pool for an approximately 100-lemma corpus

## Result

The auditable pool contains **101 new candidates**, excluding all 30 released lemmas. Recommendations are 70 `include`, 24 `reserve` and 7 `defer`. The pool is intentionally broader than the next-70 so a reviewer can replace weak or uncorroborated entries without restarting discovery.

[priority-8-candidate-verbs.csv](priority-8-candidate-verbs.csv) contains every component score, total, repository evidence, uncertainty, provisional CEFR/construction/case value, likely meaning/pattern range, aspect/reflexive note, reuse opportunity and recommendation. No construction in the file is approved. Every construction is a discovery hypothesis for Phase 3, and architecture compatibility is a hard gate that may override its numeric score.

## Repository discovery model

Discovery parsed the committed `data-*.js` structures and inspected vocabulary cards, example sentences, grammar teaching/drills, conversations, podcasts, released content references, the existing audio manifest and generated topic surfaces. Generated pages are derived from the same data and were used as discoverability/context evidence, not double-counted as independent frequency evidence.

`exact_infinitive_mentions` is a conservative literal headword/infinitive floor. It deliberately undercounts inflected forms and must not be described as Polish corpus frequency. Conversation-reuse and repository-frequency scores also consider cited scenario/grammar/card contexts. This avoids pretending a regex is a lemmatizer.

National relevance and contemporary-standard scores are editorial planning judgments about neutral practical use. They are not external corroboration. No public reference lookup was performed in Phase 0; every row says that WSJP PAN or another contemporary source is still required in Phase 3.

## Scoring model

Positive components use small visible scales:

| Component | Scale | Interpretation |
|---|---:|---|
| Everyday usefulness | 0–5 | practical frequency and learner utility |
| A1–B1 relevance | 0–5 | A1 highest, then A2, then B1 |
| Repository frequency floor | 0–5 | exact mentions plus cited structured evidence |
| Conversation reuse | 0–4 | direct pragmatic reuse |
| Case/preposition value | 0–5 | construction-learning value |
| Learner-error risk | 0–4 | benefit of explicit teaching |
| Clear construction | 0–4 | selective, explainable frame |
| Deterministic exercise fit | 0–4 | likely closure under controlled prompts |
| National relevance | 0–3 | useful across Poland, not local novelty |
| Contemporary usage | 0–3 | expected modern standard usage, pending verification |
| Source corroboration quality | 0–2 in this audit | repository support only; external verification absent |
| Example/audio reuse | 0–3 each | likelihood of exact committed-source reuse |

Risk/cost components are subtracted: overlap/duplication (0–3), editorial complexity (0–4), meaning complexity (0–3), pattern complexity (0–3), aspect/reflexive complexity (0–3) and audio complexity (0–2). The total is decision support, not approval and not the final sort key.

## Selection logic

The provisional include set emphasizes:

- high-utility modals and infinitives;
- motion verbs already heavily taught in the repository;
- everyday transitive verbs without letting Accusative dominate;
- Dative recipient/experiencer frames;
- the large preposition + Genitive gap;
- `o/w + Locative`, `z + Instrumental`, clauses and multi-complement patterns;
- selected meaning-sensitive and lexical-`się` verbs;
- explicit aspect pairs as separate lemmas only where both provisionally have independent repository evidence and learner value.

The reserve pool holds useful replacements, especially additional aspect partners and motion verbs. Deferrals are not linguistic rejections: they have weak direct repository evidence, disproportionate complexity or lower A1–B1 priority.

## Locked-model fit

The only complement types available are `case`, `preposition-case`, `infinitive` and `clause`; this correction does not propose a schema expansion. `czuć się` moves to reserve because its core adverb/adjective predicate is not representable, and `kosztować` moves to reserve because an ordinary price/amount expression must not be forced into a direct case-object label. `pracować` remains provisionally included for compatible `nad + Instrumental` and carefully verified `w + Locative` value, while `jako + Nominative` is explicitly outside the locked model. Neither incompatible construction contributes to coverage estimates.

`przynosić` replaces `czuć się` because its provisional Dative recipient + Accusative thing frame is compatible, independently useful and supported by a cited healthcare context. `kłócić się` replaces `kosztować` because `z + Instrumental` and `o + Accusative` are compatible, error-prone relationship constructions with direct repository context. These replacements were selected for learner value, coverage and evidence—not by taking the next numeric totals.

## Aspect-pair slot policy

Both members of a pair may consume separate slots only when **each** has independent everyday usefulness, independent repository evidence, a learner need for both aspect choices, and teaching value beyond duplicating one frame. The reviewer must also find that the pair fits the approximately 70-lemma budget after comparing domain/coverage opportunity cost; otherwise one partner remains reserve. Each lemma is researched separately, patterns are never inherited, and both must independently pass Phase 3 before a final Phase 3B freeze.

The ten provisionally double-slotted pairs are `kupować/kupić`, `dawać/dać`, `brać/wziąć`, `czytać/przeczytać`, `pisać/napisać`, `spotykać się/spotkać się`, `oglądać/obejrzeć`, `zaczynać/zacząć`, `kończyć/skończyć` and `wracać/wrócić`. The begin pair is retained provisionally for the independently useful process versus bounded-onset contrast, but must collapse to one slot if Phase 3 cannot substantiate both. `zamawiać` is the single provisional ordering-family slot and `zamówić` remains reserve; `rezerwować` is the single booking-family slot and `zarezerwować` remains reserve. Phase 3 evidence may justify a partner swap without implying inheritance or automatic expansion to two slots.

## Motion concentration

Twelve of the 70 provisional inclusions are primarily motion lemmas: `iść`, `chodzić`, `jechać`, `jeździć`, `dojść`, `dojechać`, `wracać`, `wrócić`, `przyjść`, `przyjechać`, `wyjść` and `wyjechać`—**17.1%**. The share is provisionally justified by unusually strong repository teaching, everyday navigation value and learner need to distinguish determinate/indeterminate and bounded/unbounded motion. It is also the ceiling for this shortlist: additional motion partners stay reserve unless Phase 3B replaces a weaker motion slot.

Motion occurrence does not itself create Verb Patterns coverage. Destination, source and vehicle phrases are broadly reusable adjunct candidates and receive no governed case/preposition credit unless Phase 3 proves a selected lexical/constructional frame for the exact meaning.

## Limits and ownership

A headword hit never licenses a syntactic frame. Repository evidence proves Po polsku relevance or reuse opportunity, not Polish valency. Scores and ranking position do not substitute for contemporary reference evidence, editorial analysis or human product approval. Phase 2 locks only a provisional shortlist and balance target; Phase 3 verifies or replaces hypotheses, and the human product owner freezes the final lemma set in Phase 3B. No ranked frame is approved before that sequence.
