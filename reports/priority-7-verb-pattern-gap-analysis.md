# Priority 7 — Verb-Pattern Gap Analysis

**Phase:** 0, reports only  
**Conclusion:** the repository has enough authored evidence for a carefully reviewed pilot, but no reusable verb-pattern entity and no safe automatic path from existing prose into production activities.

## 1. What is missing structurally

Current cards model a display/translation unit. Priority 7 needs a different identity:

`lemma → meaning → one or more complement patterns`

The current closed schema cannot explicitly represent:

- distinct meanings of one lemma;
- reflexive versus non-reflexive entities;
- direct case versus preposition+case;
- two or more complements with separate roles/questions;
- infinitive or clause complements;
- required versus optional complements;
- aspect links whose semantics have been reviewed;
- CEFR and recognition/production status per pattern;
- activity eligibility per pattern;
- provenance and review state.

Adding one `case` field to existing cards would not solve this. It would overload lexical cards, flatten polysemy, and force historical edits into frozen content.

## 2. Existing representation cannot be promoted automatically

| Current field/source | Useful evidence | Why it is unsafe as canonical pattern data |
|---|---|---|
| `pair` | possible aspect/contrast candidates | free text, incomplete and sometimes semantically wrong as an aspect relation |
| `relationType` | 17 strict core aspect-pair cards and six contrasts | sparse; still card-level rather than meaning-level |
| `relatedIds` | stable reciprocal contrast links on six core verb cards | not aspect or government metadata |
| `senseGroups` | eight core verb cards grouped for answers/distractors | not lexical equivalence |
| `hint`, `pattern`, `ex` | many case/preposition facts | prose is not typed or consistently scoped |
| grammar drills | deterministic examples and case choices | drill identity is not a reusable linguistic claim |
| scenarios | natural context and explanatory notes | branching reinforcement, not scored government data |

Known `pair` anomalies include `szukać / znaleźć`, conflicting partners for duplicate `oszczędzać`, and finite forms such as `robiłem / zrobiłem`. No automated migration from `pair` to aspect entities should be attempted.

## 3. Activity fit and gaps

### Type It

Type It is card translation, not complement selection. It uses `en`, optional `typeItCue`, optional `exEn`, and a closed answer set of canonical `pl` plus `acceptedAnswers`. Exact normalization lowercases, removes limited punctuation and collapses whitespace; diacritic folding and some hyphen variants are only “almost.” It does not infer word order, aspect, gender/person, slash alternatives, or valid paraphrases.

The existing prompt tests identify five ambiguous duplicate-English groups, but cannot discover broader semantic ambiguity. Bare prompts such as “ask,” “talk,” “believe,” “care,” “know,” “like,” or “find” are unsafe for pattern production. Future use should be limited to contextual cloze/build prompts whose intended meaning, roles and closed answer set are explicit.

### Listening

Listening plays the complete Polish card text and asks for an English meaning. It can reuse approved natural example sentences for recognition, including endings and preposition+noun phrase recognition. Abstract labels (`szukać + Genitive`), case names, and diagnostic questions should not become audio prompts.

### Grammar choose/build

The grammar engine is the closest existing primitive:

- choose uses exact authored option equality;
- build uses shuffled authored tokens and ordered equality;
- alternative word orders require explicit `acceptedOrders`;
- misses requeue once;
- score is session-only and grammar functions do not write progress.

The whole repository contains 285 choose and 68 build drills; only six build drills currently allow one alternate order. A pilot can reuse these primitives if it authors deterministic context, forms, distractors and accepted orders. An unknown drill type currently falls through to build behavior, so any future type must be explicitly validated and handled rather than silently accepted.

### Mixed activities

Case Mix samples the 99 case drills; it has no pattern or lemma stratification. Per-topic Mixed samples vocabulary cards and writes current card/topic progress. Injecting pattern entities as fake cards would conflate progress semantics. Pattern mastery should remain session-only in the pilot.

### Conversations

Scenarios have no correct/wrong state or learner progress. They are well suited to contextual reinforcement and optional explanatory notes. They should not be forced into assessment or rewritten merely to place pilot verbs.

## 4. Scenario evidence for pilot design

| Lemma family | Authored scenario entries / topics | Guidance entries | Implication |
|---|---:|---:|---|
| `potrzebować` | 8 / 5 | 3 | strongest contextual reuse across pharmacy, doctor, shops, city and gym |
| `pomagać/pomóc` | 5 / 3 | 1 | practical Dative; work context also shows `z + Instr` |
| `używać/użyć` | 3 / 1 | 1 | gym note explicitly supports Genitive |
| `szukać` | 1 / 1 | 0 | formal support stronger than scenario support |
| `prosić o` | learner line/note/recap in shops | 2 | distinguish a request from generic `proszę` |
| `pytać/zapytać` | 5 / 3 | 1 | current meaningful scenario example differs from `pytać o`; separate pattern records needed |
| `płacić/zapłacić` | 8 / 3 | 2 | method and paid-for object need separate frames; method relationship classification remains open |
| `dzwonić w sprawie` | 1 / 1 | contextual recap | useful future pattern linked to A2 card |

There are no scenario hits for `rozmawiać`, `interesować się`, `słuchać`, or `bać się`. This is not a reason to insert them artificially; card/grammar evidence can justify recognition-first teaching.

## 5. Discovery gaps

Search recursively concatenates almost every string in a topic, lowercases it and performs raw substring matching ([`index.html:2486`](../index.html#L2486)). Results are topics, without matched-card snippets or field-aware ranking.

Examples produced by an exact emulation of the current walker:

| Query | Topic results | Why it succeeds/fails |
|---|---:|---|
| `szukać` | 5 | literal occurrences, including unrelated contexts |
| `szukac` | 0 | no diacritic folding |
| `czekać na` | 1 | misses the A1 card, which uses inflected `Czekam na` in prose |
| `rozmawiać o` | 0 | content uses inflected forms |
| `genitive` | 33 | high recall, noisy topic-level results |
| `which case after szukać?` | 0 | no natural-language or lemma-aware index |

An independent pattern dataset would be invisible until a dedicated lemma/preposition/case/gloss index and results adapter are intentionally added. Copying pattern prose into existing topics to exploit the current search would create duplication rather than solve discovery.

## 6. Generated pages and offline gaps

`build_pages.py` reads `data-grammar.js` and `data-b1.js`, renders teach material (not drills), and owns the generated grammar/vocabulary/guide directories. It does not consume `data-verbs.js`, scenarios, podcasts, or any future pattern dataset. New pattern pages would require an explicit generator, curated stable slugs, canonical/duplicate rules, sitemap integration and service-worker inventory updates.

The service worker has exact required asset and generated-page inventories. A future distinct pattern file must be loaded explicitly, classified network-first, included in required assets, deployed atomically with its consumer, and covered by offline tests. Naming it `data-verb-patterns.js` is unsafe unless current parser tooling is deliberately expanded, because both validation and audio rules glob every `data-*.js` and expect `PP_LEVELS.push(...)`.

## 7. High-value content gaps

1. No verb-first reference that brings together patterns split across cases.
2. No meaning boundary for English collisions such as `pytać`/`prosić`, `znać`/`wiedzieć`, `lubić`/`podobać się`, or `szukać`/`znaleźć`.
3. No typed secondary complements for `prosić kogoś o coś`, `dziękować komuś za coś`, or `mówić komuś coś/że…`.
4. No safe distinction between a lemma's ordinary frame and negated direct-object case behavior.
5. No provenance/review workflow for research-derived claims.
6. No pattern-specific eligibility controlling reference, recognition, listening and active production.
7. No frozen baseline for a new independent dataset.
8. No internal distinction yet prevents predicative, means/method or subject/experiencer relationships from being presented as ordinary lexical government.

## 8. Recommended response

Use an independent canonical pattern dataset with optional one-way references to existing cards, drills/topics and scenarios. Keep existing content byte-for-byte unchanged during the pilot; compute reverse links at runtime. Permit learner-facing use only for `approved` records and require explicit per-activity eligibility with default `false`.

Phase 1 must lock the schema and editorial rules, including the smallest useful relationship distinction tested on `płacić`, `być`, `to jest` and `podobać się`. This need not become a large taxonomy or learner-facing jargon. Phase 2 should build validation/frozen-audit tooling with candidate fixtures. Only then should a small native-reviewed pilot enter a reference view or session-only choose/build practice.
