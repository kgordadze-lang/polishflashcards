# Priority 8 Phase 0 — candidate pool for an approximately 100-lemma corpus

## Result

The auditable pool contains **101 new candidates**, excluding all 30 released lemmas. Recommendations are 70 `include`, 24 `reserve` and 7 `defer`. The pool is intentionally broader than the next-70 so a reviewer can replace weak or uncorroborated entries without restarting discovery.

[priority-8-candidate-verbs.csv](priority-8-candidate-verbs.csv) contains every component score, total, repository evidence, uncertainty, provisional CEFR/construction/case value, likely meaning/pattern range, aspect/reflexive note, reuse opportunity and recommendation. No construction in the file is approved.

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

The include set emphasizes:

- high-utility modals and infinitives;
- motion verbs already heavily taught in the repository;
- everyday transitive verbs without letting Accusative dominate;
- Dative recipient/experiencer frames;
- the large preposition + Genitive gap;
- `o/w + Locative`, `z + Instrumental`, clauses and multi-complement patterns;
- selected meaning-sensitive and lexical-`się` verbs;
- explicit aspect pairs as separate lemmas where both have repository value.

The reserve pool holds useful replacements, especially additional aspect partners and motion verbs. Deferrals are not linguistic rejections: they have weak direct repository evidence, disproportionate complexity or lower A1–B1 priority.

## Limits

A headword hit never licenses a syntactic frame. Scores do not substitute for contemporary reference evidence, editorial analysis or human product approval. If a proposed frame lacks adequate support in Phase 3, defer it or replace the lemma from the reserve pool.
