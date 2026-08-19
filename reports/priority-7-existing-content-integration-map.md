# Priority 7 — Existing-Content Integration Map

**Phase:** 0 analysis only. No integration was implemented.

## Recommended one-way flow

```text
reviewed verb-pattern corpus
  ├─ typed contentRefs ──> existing cards/topics/drills/scenarios
  ├─ field-aware index ──> verb/case/preposition search results
  ├─ eligibility adapter ─> session-only choose/build/listening activities
  └─ approved utterances ─> explicit audio inventory

existing PP_LEVELS/content ── does not author backlinks or own pattern facts
```

This keeps current stable IDs useful while preserving existing content and progress semantics.

## 1. Current loaders and consumers

| Surface | Current source | Current behavior | Priority 7 requirement |
|---|---|---|---|
| App data load | seven `data-*.js` files before helpers ([`index.html:1830`](../index.html#L1830)) | populates `window.PP_LEVELS` | explicit load for a distinct pattern file and fail-closed availability check |
| Home/topics | `PP_LEVELS` | routes/counts by hard-coded topic `kind` | do not inject patterns into an existing topic shape |
| Search | recursively collected topic strings | raw lowercase substring, returns topics | field-aware lemma/case/preposition/gloss adapter; do not index IDs |
| Flashcards | card objects | card display/translation | optional read-only pattern block resolved from pattern-side refs |
| Type It | eligible A1/A2/B1 cards | translation to canonical `pl` | separate contextual pattern prompt adapter only |
| Listening | eligible A1/A2/B1 cards | hear `pl`, choose `en` | approved complete sentence inventory only |
| Grammar | `teach` + `drills` topics | choose/build; session-only score | safest pilot activity primitive, without persistent mastery |
| Per-topic Mixed | vocabulary cards | listen/type/mc and card progress | do not insert pattern entities as fake cards |
| Scenarios | scene nodes/options/notes | authored branching, no right/wrong/progress | contextual links/notes only |
| Generated pages | grammar teach + six mapped B1 topics | 23 grammar, six vocabulary pages, guide hub | no automatic impact; future dedicated renderer only |
| Audio | recursive phrase inventory + manifest | exact normalized phrase lookup | explicit approved-example collector |
| Offline | exact service-worker inventories | data network-first; shell versioned | new required asset/classifier and atomic deployment |
| Progress | stable card/topic IDs, schema v2 | card/topic mastery | keep pattern pilot session-only |

## 2. Existing content anchors for the pilot

| Pattern family | Existing anchor IDs/topics | Recommended future use |
|---|---|---|
| `szukać + Genitive` | `a1-first-verbs-020`; `grammar-cases-genitive-014`; A2/B1 cards | reference link, controlled Genitive build, `znaleźć` contrast after review |
| `pomagać + Dative` | `a1-first-verbs-022`; Dative drills; work scenario | reference and choose/build; scenario reinforcement |
| `czekać na + Accusative` | `a1-first-verbs-021`; relative-clause drill | reference/choose; add no artificial scenario |
| `potrzebować + Genitive` | A2 official-matters template; comparison; pharmacy/doctor scenarios | consolidate distributed evidence without creating a duplicate vocab card |
| `prosić … o …` | A2 restaurant template; Accusative lesson; shops scenario | meaning/role-aware two-complement practice |
| `interesować się + Instrumental` | `a2-leisure-culture-002`; Instrumental drills | compact card block and controlled case practice |
| `używać + Genitive` | `a2-ecology-024`; gym note | reference plus contextual cloze |
| `płacić` frames | A2/B1 money cards; pharmacy/shops/city scenarios | separate paid-for and payment-method records; classify the method relationship in Phase 1 rather than assuming lexical government |
| `rozmawiać z/o` | Instrumental and Locative case topics/drills | first cross-case lemma view |
| `bać się` meanings | `b1-character-emotions-010` | keep current Genitive evidence; second meaning stays research-only until verified |
| `tęsknić za`, `dbać o`, `wybaczyć` | B1 relationship/health cards | recognition-first B1 expansion |

`contentRefs` should point to stable content locations, not copy their prose. A conceptual ref is `{kind, id, purpose}` where `purpose` could be `current-card`, `supporting-drill`, `context-example` or `contrast`. Exact values must be locked in Phase 1.

## 3. Activities and answer ownership

### Type It

The global Type It pool is synthesized from plain A1/A2/B1 topics. Its current total is 1,089 cards. `typeItCue` is Type-It-only, while per-topic Mixed intentionally ignores it. A future pattern adapter must not mutate this pool or current totals. Pattern prompts need their own stable IDs, explicit meanings, contextual cues, accepted forms and no card-progress writes.

### Listening

Current Listening contains 1,113 cards. It tests Polish utterance→English meaning, not government. Approved full pattern examples could use a dedicated recognition activity, but abstract labels/questions must not enter current phrase discovery.

### Grammar

Choose/build can represent a safe pilot:

- choose: supplied context, one correct case/preposition/form;
- build: supplied meaning and tokens, explicit alternate orders;
- misses requeue once;
- no durable grammar progress.

Unknown types must be rejected by data validation and runtime routing. Current “anything other than choose behaves as build” is not a safe extension contract.

### Mixed/progress

Per-topic Mixed writes first-try right/miss to existing card progress. Pattern entities must remain outside it until pattern-progress semantics receive a separate approved design. A runtime adapter may include pattern practice in a session-only “case mix” without touching `popolsku-progress-v2`.

## 4. Search integration

The current index recursively captures nearly every string, including internal-looking fields, and searches one literal substring. Priority 7 needs a deliberate index with fields such as:

- display lemma and reviewed linked forms;
- meaning gloss and curated synonyms, if approved;
- full case names and Polish case names;
- preposition;
- diagnostic question;
- learner-facing pattern label.

IDs, provenance locators, review notes and source identifiers must not be searchable. Results should target a meaning/pattern, show why it matched and optionally link to supporting case lessons/cards. Natural-language support such as “which case after szukać?” would require a small intent adapter or normalized query parser; current substring search cannot answer it.

## 5. Generated-page integration

[`build_pages.py`](../build_pages.py) hardcodes `data-grammar.js` and `data-b1.js`, renders teaching content rather than drills, and owns generated directories. Adding a pattern file has zero automatic SEO effect.

If static pattern pages are later approved:

1. use a dedicated renderer and curated set, not one page per source headword;
2. derive stable URLs from approved pattern slugs/IDs, not mutable display titles;
3. avoid duplicating case explanations and examples across lemma pages;
4. add canonical, sitemap and exact service-worker generated inventories;
5. validate deterministic output and collisions;
6. keep unapproved/research candidates out of public pages.

Static pages are explicitly out of the pilot unless separately scoped.

## 6. Audio integration

Current audio discovery recursively treats certain `pl`, `ex`, `full` and `npc` strings as phrases. A new generic object using those keys could create unintended synthesis. Pattern audio must use an explicit collector that selects only approved, complete natural utterances. Reuse is by exact normalized phrase; labels, case names, questions and notation remain silent.

## 7. Offline and release integration

A new pattern asset requires all of these in the same future release:

- loader and consumer;
- service-worker `REQUIRED_ASSETS` entry;
- explicit network-first data classification;
- exact inventory tests;
- correct JavaScript/JSON media type;
- shell cache bump when the shell or precache list changes;
- stale/offline and failed-install tests.

Do not leave the file as an unclassified static asset. Do not rename `AUDIO_CACHE`; content-hash audio entries are intentionally retained across releases.

## 8. Frozen and migration integration

Pattern records need a dedicated closed-schema validator, referential-integrity checks and their own frozen snapshot. Current PP_LEVELS baselines must remain unchanged.

For the pilot:

- `schemaVersion` remains 2;
- `CONTENT_MIGRATION_REVISION` remains 2;
- pattern sessions do not write local storage;
- existing v1/v2/recovery/backup round trips remain byte-for-byte unchanged;
- loading/completing pattern practice must leave `popolsku-progress-v2` unchanged.

If durable pattern mastery is later approved, backup preflight/restore and progress semantics must be designed before any storage key ships.

## 9. Integration gates

| Gate | Required evidence |
|---|---|
| Linguistic | external verification, native review, owner approval |
| Data | closed schema, stable IDs, valid refs, frozen snapshot |
| Activities | deterministic prompts, explicit eligibility/answers, negative progress tests |
| Audio | exact approved utterance delta and manifest/file parity |
| Offline | atomic install/update and stale-data tests |
| Search | field whitelist, expected target counts, no ID/provenance leakage |
| Generated pages | separate scope, stable URLs, canonical/duplicate/sitemap checks |

No integration should proceed merely because a record can be linked to an existing card.
