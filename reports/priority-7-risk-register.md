# Priority 7 — Risk Register

**Phase:** 0, reports only. Priority reflects combined likelihood, impact and reversibility if Priority 7 proceeds without the named control.

## Priority 1 — block content production until resolved

| ID | Category | Risk | Evidence/trigger | Required control |
|---|---|---|---|---|
| R-01 | Linguistic | Wrong meaning→pattern mapping | many pilot verbs have several meanings/frames | meaning-first records; modern reference + native + owner approval |
| R-02 | Linguistic | Free-text `pair` is mistaken for aspect truth | `szukać/znaleźć`, inflected pairs, inconsistent `oszczędzać` | never auto-import; distinct stable entities and manual review |
| R-03 | Linguistic | Reflexive/non-reflexive entities are collapsed | `się` exists only in text; opposite-base collisions in overlap | separate IDs, meanings and progress identity |
| R-04 | Linguistic | Existing inconsistency is propagated | `nie lubię + accusative` conflicts with example/Genitive lesson | resolve under native/editorial review before affected pilot content |
| R-05 | Governance | Copyrighted dictionary content is reconstructed or copied | full index was extractable; demo examples are protected | locators/fact types only; independent examples; no full index in reports/product |
| R-06 | Governance | AI research candidate is presented as approved | detailed source unavailable for most pilot verbs | fail-closed review states and explicit learner eligibility |
| R-07 | Technical | Independent data bypasses frozen protections | current baseline watches PP_LEVELS, not a new file | closed validator and dedicated frozen snapshot before learner data |
| R-08 | Pedagogical | Bare translation prompts accept several natural answers | `ask`, `talk`, `like`, `believe`, `know`, aspect/word order | contextual deterministic prompts; explicit accepted set; default Type It false |

## Priority 2 — resolve before pilot implementation

| ID | Category | Risk | Evidence/trigger | Required control |
|---|---|---|---|---|
| R-09 | Linguistic | Valid but uncommon/outdated structure is actively taught | source published 2011 with older introductory basis | contemporary reference/corpus evidence and CEFR/register review |
| R-10 | Linguistic | Aspect or negation is encoded as the lemma's ordinary case | direct-object negation and `znaleźć` comparison | model construction/context separately; do not flatten to `lemma→case` |
| R-11 | Linguistic | English gloss distorts Polish roles | `podobać się`, `mówić`, `prosić/pytać` | role-aware glosses/examples reviewed together |
| R-11A | Linguistic | Every case-connected phrase is mislabeled as ordinary lexical government | `płacić` method, `być`/`to jest` predication, `podobać się` subject/experiencer | Phase 1 approves the smallest useful relationship distinction; learner wording remains plain |
| R-12 | Pedagogical | A1/A2 learners face dictionary-like complexity | multiple questions/cases/register details | progressive disclosure and recognition-first CEFR gating |
| R-13 | Pedagogical | Static reference has no retrieval practice | existing case facts already sit in prose silos | approved choose/build and contextual reinforcement in pilot |
| R-14 | Pedagogical | Learners memorize endings without transfer | case-only drills do not provide verb-first retrieval | meaning→role→question→case sequence and mixed contextual tasks |
| R-15 | Technical | Existing card pools/progress are polluted | card eligibility feeds Type It/Listening/Mixed | one-way refs; separate adapters; session-only pattern practice |
| R-16 | Technical | New pattern IDs are unstable/reused | no current convention/baseline | lock ID/retirement policy; uniqueness and frozen-placement tests |
| R-17 | Technical | A new `data-*.js` breaks parsing or expands audio | validators/audio glob all `data-*.js` as PP_LEVELS | distinct filename and explicit parser/audio contract |
| R-18 | Technical | Generic `pl`/`ex` fields create audio explosion | recursive phrase collector | explicit approved-utterance collector; labels/questions silent |
| R-19 | Technical | Offline deploy produces UI/data mismatch | exact required assets/classifiers; atomic SW install | deploy loader/data/SW/cache/tests together; fail safely |
| R-20 | Technical | Search becomes noisy or leaks internal fields | current recursive topic string walker | field whitelist, target counts, no IDs/provenance indexing |
| R-21 | Technical | Generated pages duplicate case content/URLs | current generator not pattern-aware and owns output dirs | defer; dedicated curated renderer/stable slugs/canonical rules |
| R-22 | Governance | Implementation begins before review workflow exists | 30 candidates include headword-only/provisional claims | Phase 1 spec, Phase 2 tooling, then small approved pilot |

## Priority 3 — monitor or defer to separately approved scope

| ID | Category | Risk | Trigger | Control |
|---|---|---|---|---|
| R-23 | Technical | Durable pattern state is copied but not semantically validated by backup | new `popolsku-*` key | no pilot persistence; separate storage/migration design later |
| R-24 | Technical | Existing progress IDs are split/merged/transferred | pattern mastery mapped from card mastery | explicit migration revision and compatibility plan |
| R-25 | Technical | Current grammar silently treats unknown type as build | new drill type | reject unknown type in validator/runtime before extension |
| R-26 | Pedagogical | Case Mix implies seven-case coverage it does not guarantee | 15 random drills omit ≥1 case about 48.9% of rounds | label correctly; stratify a future pattern mix if coverage matters |
| R-27 | Technical | Valid Polish word orders are marked wrong | only six of 68 builds have an alternate order | explicit accepted orders and native prompt review |
| R-28 | Technical | Audio cache reaches trim/storage pressure | 3,377 current; pilot adds examples | exact delta and storage/retention tests; reuse existing utterances |
| R-29 | Governance | Future 100-verb pool becomes an assumed roadmap | source index mistaken for backlog | maintain tier as research pool; separate approval per expansion |
| R-30 | Governance | Source citation is read as endorsement | named author/publisher in research record | neutral internal attribution; no promotional endorsement claim |

## Risk notes by required category

### Linguistic

Highest uncertainty clusters around polysemy, aspect, `się`, optional/secondary complements, register and English glosses. Source headword presence is not detailed pattern evidence. Even repository rules require review because current content contains at least one clear internal contradiction.

### Pedagogical

The feature fails if it becomes an academic valency dictionary, a static table, or ambiguous translation drill. Progressive disclosure, contextual retrieval and recognition→production gating are required design controls.

### Technical

The safest architecture is additive only if the new corpus receives validation/frozen controls and remains outside existing progress. “Separate file” alone is not a safeguard. Search, audio, SW, activity and page consumers must be explicit.

### Governance

Research facts, authored examples and approval decisions need separate provenance. No external research was performed; every contemporary claim is still outstanding.

## Stop conditions

Stop a later phase and return to design if any of these occurs:

- the selected structure cannot represent one meaning with multiple complement frames;
- a pilot requires editing existing cards merely to hold canonical pattern data;
- progress writes or a migration become necessary without separate owner approval;
- frozen PP_LEVELS baselines move unexpectedly;
- a source claim cannot be supported without copying protected content;
- native review cannot make an activity prompt deterministic;
- unapproved candidates reach search, activity or audio collectors;
- new data cannot be deployed offline atomically;
- scope expands into durable mastery, generated pages or the 100-verb pool without a new decision.
