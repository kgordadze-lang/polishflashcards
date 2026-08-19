# Priority 7 — Phase 0 Summary

**Scope:** repository-wide current-state, research-source, content-coverage and architecture audit  
**Outcome:** Priority 7 appears safely additive if it uses an independently validated lemma→meaning→pattern corpus, one-way references and session-only pilot activities. Phase 1 should lock the specification; it should not build the feature.

## 1. Verified safety baseline

All required preconditions passed before audit work:

| Check | Verified value |
|---|---|
| Branch | `priority-7-phase-0-audit` |
| HEAD | `f6bdc73a86f8b114582d52d0380e7289b8f2fe5d` |
| Tree | `92e9cdc905ec7ed8f21e784505e501880071704b` |
| Git remotes | none |
| `push.default` | `nothing` |
| Initial worktree | clean |
| App version | `8.10` |
| Shell cache | `popolsku-v65` |
| Audio cache | `popolsku-audio` |
| Progress schema / migration revision | `2 / 2` |

No remote was added, no commit or push was made, and no production repository was accessed.

## 2. Headline repository inventory

- Validated corpus: 10 levels, 97 topics, 1,215 cards, 353 drills and 1,675 stable IDs.
- A1/A2/B1: 1,166 cards (340/514/312); podcasts: 49 cards.
- Cases: seven dedicated topics, 49 teaching items and 99 drills.
- Verbs curriculum: nine topics, 44 teaching items and 72 drills.
- Scenarios: eight topics, 102 scene nodes and 194 learner options.

Because there is no lemma/POS field, overlap uses a strict mechanical definition: an infinitive-headed Polish label (`-ć`/`-c`, preserving immediate `się`) whose English gloss is verbal. It excludes finite forms, examples, drills and scenario utterances.

| Scope | Strict verb cards | Distinct primary lemmas | Standalone / phrase cards | `się` cards / lemmas |
|---|---:|---:|---:|---:|
| A1–B1 core | 204 | 163 | 140 / 64 | 29 / 27 |
| Core + podcasts | 228 | 181 | 140 / 88 | 35 / 33 |

Four obvious finite/sentence verb cards sit outside the strict primary inventory and require manual lemmatization. Ten exact core Polish surfaces are duplicated; 25 core primary lemmas occur on multiple cards. Duplicate surface does not automatically mean duplicate sense.

Current aspect/reflexive representation is weak: 151/204 core verb cards have free-text `pair`, but only 17 have `relationType: "aspect-pair"`. `pair` contains contrasts, inconsistencies and inflected forms, so it cannot be promoted automatically into linguistic entities.

## 3. 1,001-headword overlap

The supplied demo PDF was inspected page by page. It contains methodology, a complete numbered 1,001-entry index and detailed sample entries only for source entries 1–50. The full extracted list was used internally and is not reproduced or delivered.

Matching preserves diacritics, `się`, aspect and multiword forms. It uses NFC, case-folding and whitespace normalization only, plus the source's five explicitly printed alternative-form groups. No fuzzy, diacritic-stripped, reflexive-collapsed or aspect-collapsed match is counted.

| Result | Exact audit count |
|---|---:|
| Direct listed-form match | 98 / 181 app primary lemmas |
| Of those | 97 entry-string matches + 1 explicitly listed alternative |
| No direct match | 83 / 181 |
| Repository-pair-linked only | 26 |
| Opposite-`się` base collision only | 3 |
| No relation detected by heuristic | 54 |
| Source entries without direct primary-lemma match | 903 / 1,001 |

The 903 figure means “not directly matched by this app primary-lemma inventory,” not “absent from all Po polsku content.” Repository pair fields reference 28 source entries; direct+linked union covers 125 source entries, but link semantics are unreviewed and incomplete. The book index is a comparison source, not a backlog.

Rights-safe row evidence is in [`priority-7-book-headword-overlap.csv`](priority-7-book-headword-overlap.csv); it contains app lemmas and source entry numbers, not source-only headwords or passages.

## 4. Strongest current verb/case coverage

All seven cases have explanations and drills. Strong existing anchors include:

- Genitive: scoped direct-object negation and `szukać`; cards for `słuchać`, `uczyć się`, `używać`, `bać się`; repeated `potrzebować` contexts.
- Dative: explicit list/drills for `dawać`, `pomagać`, `mówić`, `dziękować`, `ufać`, `wierzyć`.
- Accusative: direct-object foundation plus `pytać o` and `prosić o`.
- Instrumental: lexical/prepositional anchors `interesować się`, `zajmować się`, `rozmawiać z`; method-of-payment contexts whose internal relationship still needs Phase 1 classification.
- Locative: `rozmawiać o` and `myśleć o`.
- Scenarios: especially strong reuse for `potrzebować`, `pomagać`, `używać`, `prosić o` and `płacić`.

The current facts are distributed through hints, templates, examples, drill explanations, scenario notes and recap bullets. They are pedagogically useful but not typed or queryable.

## 5. Largest gaps

1. No verb-first view or canonical lemma→meaning→pattern record.
2. No way to join two correct patterns currently taught in different case silos (`rozmawiać z/o`).
3. No structured multiple-complement model (`prosić kogoś o coś`, `dziękować komuś za coś`).
4. Reflexive/aspect/meaning identity is inferred from prose and sparse relations.
5. Search is raw topic substring matching: it cannot answer “which case after szukać?” and misses inflected/diacritic variants.
6. Type It tests translation, not government; bare English prompts are often ambiguous.
7. Existing Mixed progress is card/topic mastery and must not be reused for pattern mastery.
8. A separate dataset would not automatically reach loaders, search, activities, audio, generated pages or offline caching.
9. New independent data would bypass the current frozen snapshot unless dedicated safeguards are built.
10. Current content contains a high-priority inconsistency: `nie lubię + accusative` conflicts with its example and the Genitive-negation lesson. `chcieć` treatment also needs scoped contemporary review.
11. Case-shaped connections are not all ordinary lexical government: predicative, means/method and subject/experiencer constructions need a minimal internal distinction.

## 6. Proposed 30-verb pilot

Ranked research shortlist:

1. `pomagać`
2. `szukać`
3. `słuchać`
4. `czekać`
5. `potrzebować`
6. `dziękować`
7. `płacić`
8. `uczyć się`
9. `używać`
10. `interesować się`
11. `dbać`
12. `prosić`
13. `tęsknić`
14. `lubić`
15. `znać`
16. `rozmawiać`
17. `bać się`
18. `być`
19. `mówić`
20. `mieć`
21. `widzieć`
22. `pytać`
23. `myśleć`
24. `znaleźć`
25. `podobać się`
26. `ufać`
27. `wierzyć`
28. `opiekować się`
29. `zajmować się`
30. `zależeć`

This set balances direct cases, preposition+case frames, reference contrasts and meaning-sensitive/multi-pattern verbs. Scores and required fields are in [`priority-7-pilot-ranking.csv`](priority-7-pilot-ranking.csv). The CSV now includes all nine integer component scores, the exact weighted formula and deterministic tie-break inputs. Independent review changed 17 positions solely by replacing editorial tie order; no candidate or calculated score changed. [`priority-7-pattern-candidates.json`](priority-7-pattern-candidates.json) includes all 30 detailed research candidates plus a tiered 100-verb future pool. No candidate is approved; most source support is headword-index-only.

## 7. Recommended architecture

Use a **one-way hybrid**:

- canonical independent `lemma → meaning → patterns[] → complements[]` data;
- optional typed pattern-side references to existing cards/topics/drills/scenarios;
- no authored backlinks or new fields on existing cards in the pilot;
- runtime/build reverse indexes where needed;
- explicit consumers for search, activity and audio;
- dedicated closed-schema validation and frozen snapshot.

Complements need typed direct case, preposition+case, infinitive and clause forms. Use full case IDs. Questions/roles attach to the complement they explain. Aspect partners and reflexive/non-reflexive forms remain distinct stable entities.

Complement shape alone must not imply ordinary lexical government. Phase 1 must choose the smallest useful internal distinction among lexical government, preposition-governed, predicative/constructional, means/method or adjunct-like, and subject/experiencer relationships. This is a precision safeguard, not a mandate for learner-facing jargon or a large taxonomy.

Do not call the file `data-*.js` without deliberately changing current parsers; validation/audio tooling globs those files and expects PP_LEVELS. A distinct name such as `verb-patterns.js` is safer, subject to Phase 1 approval.

## 8. Migration and frozen-content decision

No progress migration appears necessary for an independent dataset, one-way refs and session-only activities:

- `schemaVersion` stays 2;
- `CONTENT_MIGRATION_REVISION` stays 2;
- current `known`/`still` arrays do not receive pattern IDs;
- `popolsku-progress-v2` must remain byte-for-byte unchanged during pilot sessions.

A migration becomes necessary if existing persisted IDs or progress semantics change, or if card mastery is transferred into pattern mastery. A future durable pattern key also needs an explicit storage/backup decision because current backup copying does not provide semantic validation automatically.

The current forward baseline pins 1,675 IDs, 13,387 wording entries, 1,312 policy entries and 1,777 structure entries. Existing cards should remain unchanged. The new corpus needs its own closed validator and immutable ID/wording/policy/structure baseline before learner-facing data lands.

## 9. Activity implications

- Reuse existing choose/build as the safest pilot primitive; author context, distractors and accepted orders explicitly.
- Keep grammar/pattern score session-only initially.
- Type It only when a prompt has a closed, deterministic answer set; default false.
- Use Listening only for approved complete natural sentences, not labels/questions/notation.
- Keep current Flashcard/Type It/Listening/Mixed totals unchanged by default.
- Use scenarios as contextual reinforcement, not artificial scored tests.
- Reject unknown drill types rather than allowing fallback-to-build behavior.

## 10. Audio and offline implications

Current audio passes exact parity at 3,377 required/manifest/file entries. A planning estimate of 30–90 net-new utterances assumes one to three non-reused approved examples per pilot verb; the actual inventory must be computed after review. Do not synthesize lemma labels, case names, questions or pattern notation.

At 3,377 clips, the versionless audio cache has 823 files of nominal headroom before its maximum and 623 before the trim target. Keep `popolsku-audio` unchanged.

A future pattern file must be an explicit required/network-first service-worker asset. Loader, dataset, manifest/SW changes, shell cache bump and tests must deploy atomically. Generated pages currently have no automatic pattern impact and should be deferred.

## 11. Source/copyright constraints

- The supplied PDF remains untracked in `_research/` and was not changed or copied.
- No full index, detailed entry, example collection, definition set or synonym set is reproduced.
- Product provenance should store source ID + locator + fact type, not passages.
- App examples must be independently authored and separately marked.
- The source's age and demo scope make modern reference/native review mandatory.
- No external web/corpus research was authorized or performed.
- No endorsement by the author/publisher may be implied.

## 12. Unresolved questions

1. Exact production schema/field names and stable ID convention.
2. When two frames are separate meanings versus patterns under one meaning.
3. The smallest useful internal distinction among lexical, preposition-governed, predicative/constructional, means/method or adjunct-like, and subject/experiencer relationships.
4. Approved aspect relationship semantics and whether links must be reciprocal.
5. Treatment of reflexive variants and rare/lexicalized `się` constructions.
6. Contemporary resolution of `nie lubię`, `chcieć`, and every provisional multi-pattern claim.
7. Final CEFR and recognition/production status per pattern.
8. Which 6–10 candidates form the first small data slice before all 30.
9. Native reviewer identity/process and owner approval authority.
10. Exact example/gloss/common-error conventions.
11. Whether pattern search supports only fields or also natural-language intents.
12. JavaScript versus JSON file format and offline media-type/load failure behavior.
13. Whether any future durable mastery is worth a new store/migration.
14. Whether static pages are ever justified; they are not required for the pilot.

## 13. Recommended Phase 1

Phase 1 should approve only the pedagogical and data specification:

- entity/meaning/complement schema;
- full case/question/preposition rules;
- the smallest sufficient syntactic-relationship distinction, tested on `płacić`, `być`, `to jest` and `podobać się` without imposing learner jargon;
- aspect/reflexive identity;
- stable IDs and retirement;
- provenance and fail-closed review states;
- CEFR and production/recognition policy;
- per-activity default-false eligibility;
- learner terminology;
- Polish example, English gloss and error-feedback conventions;
- distinct filename/loader/validator/frozen/offline strategy;
- explicit session-only/no-migration pilot decision;
- adversarial fixtures proving multi-pattern, multi-complement, reflexive and negation cases.

Then Phase 2 can build audit tooling and a frozen snapshot with no learner feature. Production data should begin only after those gates and native review exist.

## 14. Artifacts created

1. `priority-7-current-verb-case-inventory.md`
2. `priority-7-source-and-rights-audit.md`
3. `priority-7-case-coverage-gap-analysis.md`
4. `priority-7-verb-pattern-gap-analysis.md`
5. `priority-7-pilot-verb-ranking.md`
6. `priority-7-data-model-options.md`
7. `priority-7-pedagogical-model.md`
8. `priority-7-existing-content-integration-map.md`
9. `priority-7-audio-impact-analysis.md`
10. `priority-7-test-plan.md`
11. `priority-7-risk-register.md`
12. `priority-7-implementation-plan.md`
13. `priority-7-existing-verbs.csv`
14. `priority-7-pilot-ranking.csv`
15. `priority-7-pattern-candidates.json`
16. `priority-7-book-headword-overlap.csv`
17. `priority-7-phase-0-summary.md`

## 15. Explicitly not implemented

No learner-facing content, existing card, application code, HTML/CSS/JavaScript/Python application file, test, migration, schema version, content migration revision, app version, service-worker cache, audio file/manifest, generated page, search behavior, activity, UI, progress record or production data structure was changed or created. Nothing was committed or pushed.
