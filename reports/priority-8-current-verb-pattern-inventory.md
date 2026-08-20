# Priority 8 Phase 0 — released Verb Patterns inventory

## Auditable inventory

[priority-8-current-patterns.csv](priority-8-current-patterns.csv) is the canonical row-level audit table. It has one row for every released pattern (45 rows) and carries the lemma/meaning/pattern/example IDs, exact Polish and English example, reflexivity, aspect, complements, cases, prepositions, CEFR, status, origin, content references, error notes, review state/event chain, `activityEligibility` and `audioEligible`. It is generated from the public runtime joined by stable pattern/example IDs to the private editorial artifact; summaries below are derived from that table.

| Lemma | ID | Rflx | Aspect | Meanings | Patterns | Status mix |
|---|---|---:|---|---:|---:|---|
| bać się | `vp-l-bac-sie-0fcafe1aef9f` | yes | imperfective | 2 | 2 | active-production 1, recognition-only 1 |
| być | `vp-l-byc-8deae1e7376a` | no | imperfective | 1 | 1 | active-production 1 |
| czekać | `vp-l-czekac-c6c3d0da2caa` | no | imperfective | 1 | 1 | active-production 1 |
| dbać | `vp-l-dbac-15ed83f8434d` | no | imperfective | 1 | 1 | active-production 1 |
| dziękować | `vp-l-dziekowac-8e4ca359cb86` | no | imperfective | 1 | 2 | active-production 2 |
| interesować się | `vp-l-interesowac-sie-594d3cf1b5a6` | yes | imperfective | 1 | 1 | active-production 1 |
| lubić | `vp-l-lubic-a9766b487203` | no | imperfective | 1 | 2 | active-production 2 |
| mieć | `vp-l-miec-3d78141ba164` | no | imperfective | 1 | 1 | active-production 1 |
| mówić | `vp-l-mowic-5f4740bd3f57` | no | imperfective | 1 | 2 | active-production 2 |
| myśleć | `vp-l-myslec-8be636ebca9e` | no | imperfective | 1 | 1 | active-production 1 |
| opiekować się | `vp-l-opiekowac-sie-3a290ee21577` | yes | imperfective | 1 | 1 | active-production 1 |
| płacić | `vp-l-placic-d709669437d2` | no | imperfective | 1 | 2 | active-production 2 |
| podobać się | `vp-l-podobac-sie-26084690c7ca` | yes | imperfective | 1 | 1 | active-production 1 |
| pomagać | `vp-l-pomagac-54633912de9a` | no | imperfective | 1 | 2 | active-production 2 |
| potrzebować | `vp-l-potrzebowac-8b78ee8b092d` | no | imperfective | 1 | 1 | active-production 1 |
| prosić | `vp-l-prosic-82f143d28483` | no | imperfective | 1 | 2 | active-production 2 |
| pytać | `vp-l-pytac-0410b0f88718` | no | imperfective | 1 | 2 | active-production 2 |
| rozmawiać | `vp-l-rozmawiac-dd7ecc80c231` | no | imperfective | 1 | 3 | active-production 3 |
| słuchać | `vp-l-sluchac-301b09233922` | no | imperfective | 2 | 2 | active-production 1, recognition-only 1 |
| szukać | `vp-l-szukac-0daf5e6b5693` | no | imperfective | 1 | 1 | active-production 1 |
| tęsknić | `vp-l-tesknic-3c9b07c066c3` | no | imperfective | 1 | 1 | active-production 1 |
| uczyć się | `vp-l-uczyc-sie-a01d00cb7f2f` | yes | imperfective | 1 | 2 | active-production 2 |
| ufać | `vp-l-ufac-6a061471e40a` | no | imperfective | 1 | 1 | active-production 1 |
| używać | `vp-l-uzywac-a617dcf0b2fc` | no | imperfective | 1 | 1 | active-production 1 |
| widzieć | `vp-l-widziec-59dbe12f8b3d` | no | imperfective | 1 | 1 | active-production 1 |
| wierzyć | `vp-l-wierzyc-171eb7790262` | no | imperfective | 1 | 2 | active-production 2 |
| zajmować się | `vp-l-zajmowac-sie-176f8a1300f8` | yes | imperfective | 2 | 2 | recognition-only 1, active-production 1 |
| zależeć | `vp-l-zalezec-679daa27f9be` | no | imperfective | 2 | 2 | active-production 1, recognition-only 1 |
| znać | `vp-l-znac-a4c921e7688c` | no | imperfective | 1 | 1 | active-production 1 |
| znaleźć | `vp-l-znalezc-eec53e19f1a0` | no | perfective | 1 | 1 | active-production 1 |

No released lemma has `aspectPartnerIds`; therefore the released corpus has zero governed reciprocal aspect pairs. This is not evidence that the verbs lack lexical partners. It means no partner relationship passed the Priority 7 release gate. There are 29 imperfective lemmas and one perfective lemma (`znaleźć`).

## Structural distribution

- Reflexive lemmas: 6 — `bać się`, `interesować się`, `opiekować się`, `podobać się`, `uczyć się`, `zajmować się`.
- Patterns owned by lexical-`się` lemmas: 9.
- Single-pattern lemmas: 16.
- Multi-pattern lemmas: 14; `rozmawiać` has 3, the other 13 have 2.
- Meaning-sensitive lemmas with more than one released meaning: 4 — `bać się`, `słuchać`, `zajmować się`, `zależeć`.
- Multi-complement patterns: 9.
- Relation types: 42 `lexical-frame`, one `constructional-frame`, one `means-method`, one `subject-experiencer`.

## Complement and case coverage

The 45 patterns contain 54 complement slots:

| Complement form | Count |
|---|---:|
| direct case | 31 |
| preposition + case | 20 |
| infinitive | 2 |
| clause | 1 |

Direct-case slots: Genitive 7, Dative 9, Accusative 8, Instrumental 6 and Nominative 1. Preposition-case slots: Accusative 11, Locative 5, Instrumental 3 and Genitive 1.

Prepositions are `o + Acc` 6, `na + Acc` 1, `za + Acc` 3, `o + Loc` 3, `w + Loc` 1, `na + Loc` 1, `z + Instr` 2, `za + Instr` 1, `w + Acc` 1 and `od + Gen` 1. No preposition + Dative pattern ships, which is consistent with the locked allowed model and standard inventory, not a gap to fill mechanically.

## CEFR and teaching disposition

Recognition levels are A1 16, A2 18 and B1 11. Production levels among active-production patterns are A1 11, A2 13 and B1 17; recognition-only patterns omit production. The four recognition-only patterns are learner-labeled “Understand for now” by the existing UI derivation.

## Provenance and governance

Examples split exactly into 20 `repository-reuse` and 25 `editorial-generated`. Content references split into 35 cards, 17 drills and 49 topics. All 45 records are currently approved, but approval grants no activity: every allowlist is empty and every audio flag is false.

## Current gaps, interpreted selectively

The clearest learner-coverage gaps are preposition + Genitive (only one slot), clauses (one), infinitives (two), preposition + Instrumental (three), and meaning-sensitive coverage (four lemmas). Dative is comparatively healthy. Accusative will naturally grow through everyday verbs, but simple transitives should not crowd out the more error-prone frames.

These are coverage signals, not claims of exhaustive valency. The released 30 describe selected learner-facing constructions for selected meanings only.
