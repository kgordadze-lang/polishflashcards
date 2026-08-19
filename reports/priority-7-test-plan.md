# Priority 7 — Future Test and Verification Plan

**Phase:** 0 planning only. No production tests were added or modified.

## Baseline that later phases must preserve

- 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 current IDs.
- Flashcards/search 1,215; Type It 1,089; Listening 1,113; Mixed 1,183.
- Progress `schemaVersion` 2 and `CONTENT_MIGRATION_REVISION` 2.
- 3,377 required/manifest/file audio entries with no orphans.
- 23 generated grammar pages, six vocabulary pages, guide hub and 32 sitemap URLs.
- Shell cache `popolsku-v65`; audio cache `popolsku-audio`.

Counts may change only in a phase that explicitly owns that change and updates its pinned expectations.

## 1. Dataset schema

### Positive cases

- one lemma with one meaning and one direct-case pattern;
- one meaning with two patterns;
- one pattern with two complements and separate roles/questions;
- `preposition-case`, `infinitive` and `clause` complement types;
- distinct reflexive and non-reflexive lemma entities;
- distinct aspect entities with reviewed links;
- CEFR, production status, eligibility, provenance and review metadata.
- fixtures covering lexical government, preposition-governed, predicative/constructional, means/method or adjunct-like, and subject/experiencer relationships under the minimal Phase 1 representation.

### Rejections

- unknown fields or complement types;
- empty lemma/meaning/pattern/complement arrays;
- abbreviated/unknown case IDs;
- preposition missing from `preposition-case` or present on direct `case`;
- question attached ambiguously to a multi-complement pattern;
- invalid CEFR/status/review transition;
- learner-facing eligibility on an unapproved record;
- production eligibility on `recognition-only` content;
- copied excerpt/example fields prohibited by the rights policy.
- flattening `płacić` + Instrumental method, `być` + Instrumental role, `to jest` + Nominative or `podobać się` experiencer structure into ordinary lexical government when the approved Phase 1 distinction says otherwise.

The parser must be closed-schema and fail closed.

## 2. IDs and referential integrity

- global uniqueness across lemma, meaning and pattern IDs;
- lowercase kebab-case syntax and stable placement;
- no reuse/repurposing after retirement;
- exactly typed `{kind,id}` content references;
- reject dangling, wrong-kind and self references;
- validate aspect partner resolution, reciprocity policy and cycles;
- ensure card/topic/drill/scenario refs point to the expected existing entity;
- ensure no authored backlinks are required on PP_LEVELS objects.

Add fixture-based positive/negative tests before the first learner-facing record.

## 3. Frozen baselines

- establish independent ID, wording, policy and structure snapshots for the pattern corpus;
- reject unapproved additions, removals, moves, wording changes, eligibility changes and ID reuse;
- require an explicit meaningful approval message for baseline updates;
- update snapshots atomically;
- assert all existing PP_LEVELS frozen totals/digests remain unchanged during the pilot.

## 4. Provenance and review workflow

- every research-derived fact has a source ID, locator and fact type;
- no source passage, screenshot or example is stored;
- authored examples are marked separately;
- review transitions are monotonic/fail closed;
- reviewer/ref and date are required for native-reviewed/approved;
- `rejected`/`deferred` records cannot enter production;
- search, activity and audio collectors include approved records only.

Use audit fixtures for headword-only evidence versus detailed evidence so the UI/editorial tooling cannot overstate source confidence.

## 5. Linguistic/editorial verification

For every pilot meaning/pattern, require a checklist covering:

- modern reputable reference confirmation;
- contemporary frequency/register evidence where needed;
- native review of lemma, `się`, aspect, meaning, complement roles, questions, preposition/case and required/optional status;
- relationship classification sufficient to distinguish lexical/preposition-governed patterns from predicative, means/method and subject/experiencer constructions, using `płacić`, `być`, `to jest` and `podobać się` as required review fixtures;
- independent natural Polish example and accurate English gloss;
- CEFR and recognition/production suitability;
- explicit resolution of `nie lubię` and `chcieć` consistency issues before affected material ships;
- product-owner approval.

Automated schema tests cannot replace this gate.

## 6. Activity tests

### Choose/build

- deterministic prompt and exactly one intended answer;
- options have no semantic collisions;
- canonical build answer and every accepted order are valid and immutable;
- wrong answers requeue once and feedback names the expected role/case without exposing unapproved alternatives;
- unknown drill types are rejected, not treated as build;
- keyboard, focus, live-region and retry behavior match current grammar accessibility.

### Type It

- explicit contextual cue makes meaning/person/number/gender/aspect deterministic;
- canonical answer plus every intentionally accepted alternative is enumerated;
- normalization parity with `pp-answer.js`;
- tests for diacritics, punctuation, whitespace, hyphen and word-order behavior;
- reject bare ambiguous prompts (`ask`, `talk`, `like`, `believe`, etc.);
- collision tests include semantic paraphrases, not just identical normalized English strings.

### Listening

- only complete approved natural sentences are used;
- no labels/questions/notation enter the phrase pool;
- safe distractor ownership and `senseGroups` where needed;
- first-try scoring and replay behavior remain clear;
- native listening QA.

### Mixed/conversations

- pattern entities do not enter current card Mixed pools/progress;
- any future pattern mix is stratified by family/CEFR as specified;
- scenarios remain contextual and do not acquire accidental right/wrong state;
- existing scenario order/branching remains unchanged.

## 7. Progress, migration and backup

Required negative regression tests for the session-only pilot:

1. snapshot `popolsku-progress-v2` bytes;
2. load, start, answer, complete and restart a pattern session;
3. assert the key is byte-for-byte unchanged;
4. assert no new local/session storage pattern key exists;
5. assert schema and revision remain 2;
6. run v1, v2, recovery, current-backup and old-backup round trips unchanged.

If persistence is later proposed, test semantic validation, backup counts, preflight, atomic restore, corrupt/newer-version rejection and migration idempotence before shipping. A new key being copied by backup is not sufficient.

## 8. Search and navigation

- lemma queries with/without `się`;
- Polish diacritics and intentional no-diacritic behavior;
- inflected or normalized query rules as specified;
- preposition+case and diagnostic-question queries;
- case names in Polish and English;
- expected exact target counts for `szukać`, `czekać na`, `rozmawiać o`, etc.;
- natural-language intent such as “which case after szukać?” if approved;
- IDs, source locators and reviewer notes never exposed/indexed;
- no unrelated PP_LEVELS result inflation;
- keyboard navigation, focus return, live-region announcements, `lang="pl"` on Polish text and mobile layout.

## 9. Audio

- explicit approved utterance inventory with reuse/new counts;
- Python/JavaScript normalization parity;
- phrase→manifest→file and file→manifest coverage;
- nonempty files and filename hash identity;
- no unapproved, label, question or notation synthesis;
- orphan reporting without silent deletion;
- current and old clips retained across shell updates;
- Range request, offline cache hit, storage-pressure and retry tests;
- exact pinned manifest count updated only in the audio phase.

## 10. Offline/service worker

- pattern file is a required asset and explicitly network-first;
- correct media type and parse failure behavior;
- install remains atomic when pattern asset fetch fails;
- stale shell/data combinations fail safely rather than render mismatched schema;
- online update, refresh activation and old→new shell transition;
- cold/offline and warm/offline behavior;
- existing audio cache name and contents retained;
- exact service-worker asset inventories updated intentionally.

## 11. Generated pages (only if separately approved)

- curated exact URL/slug set and collision rejection;
- stable canonical URLs independent of display-title changes;
- no duplicate case explanations/examples across pages;
- deterministic `build_pages.py --check` output;
- sitemap and service-worker generated-page inventory parity;
- approved records only; no research candidates indexed;
- structured data, breadcrumbs, internal links, audio controls and noindex/canonical behavior;
- no hand-authored file survives inside generator-owned directories accidentally.

## 12. Accessibility and device verification

Automated checks:

- semantic headings/landmarks and control names;
- keyboard-only operation;
- visible focus and focus restoration;
- status/error live regions;
- Polish/English language boundaries;
- reduced motion, high contrast and text scaling;
- 320px layout and touch target checks.

Manual/physical-device checks:

- VoiceOver on iPhone/iPad and TalkBack on Android;
- installed PWA and browser modes;
- portrait/landscape, safe areas and 200% text;
- weak network, offline transition, refresh and storage pressure;
- audio speed/replay with real device speakers/headphones.

## 13. Phase gates

| Gate | Minimum proof |
|---|---|
| Phase 1 spec | approved schema/editorial decisions and adversarial examples |
| Phase 2 tooling | closed validator, frozen snapshot, candidate fixtures, no learner consumer |
| Phase 3 data pilot | native-approved records, deterministic activities, zero progress/card-total change |
| Phase 4 audio | exact approved delta, manifest/file parity and listening QA |
| Later persistence/pages | separate owner approval, migration/storage or SEO/offline test plan completed |

Any unexplained movement in existing totals, progress bytes, frozen baselines, audio inventory or generated pages is a stop condition.
