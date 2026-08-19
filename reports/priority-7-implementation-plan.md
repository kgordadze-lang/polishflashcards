# Priority 7 — Phased Implementation Plan

**Phase 0 status:** audit complete; no implementation.  
**Baseline:** app `8.10`; shell `popolsku-v65`; audio cache `popolsku-audio`; progress schema/revision `2/2`.

Each future phase should be independently reviewable and shippable. Later phase numbers describe sequencing, not current authorization.

## Phase 1 — lock the pedagogical and data specification

**Objective:** approve what a verb-pattern fact means and how it is governed before any 30-verb content production.

### Decisions that must be explicit

| Decision | Approval required |
|---|---|
| Canonical entity boundary | lemma→meaning→pattern, with multiple complements |
| Exact field/schema names | closed fields, types, required/optional rules |
| Meaning model | when a gloss/frame becomes a separate meaning |
| Case representation | full seven-value identifiers; no opaque abbreviations |
| Question representation | attached to the complement/role; multiple questions allowed |
| Preposition model | normalized form and case coupling |
| Complement types | direct case, preposition-case, infinitive, clause; any directional subtype only if needed |
| Syntactic relationship distinction | approve the smallest useful distinction among lexical government, preposition-governed, predicative/constructional, means/method or adjunct-like, and subject/experiencer; do not require a large taxonomy |
| Aspect links | distinct entities, relationship semantics, reciprocity and review |
| Reflexive handling | `się` identity and separation from non-reflexive meanings |
| Stable IDs | syntax, hierarchy, immutability, retirement and non-reuse |
| Provenance | source ID/locator/fact type; no passages; authored examples separate |
| Review states | transition authority and fail-closed learner eligibility |
| CEFR | pattern/meaning-level rules, not lemma-only |
| Production/recognition | definitions and gating |
| Activity eligibility | explicit allowlist/default false per activity |
| Learner terminology | simple approved phrases and full case labels |
| Polish example convention | independent, natural, contextual, review/length rules |
| English gloss convention | meaning-specific, not automatically a production prompt |
| Error-feedback convention | role/question/case explanation; common errors only when reviewed |
| File/loader strategy | distinct filename/format, no accidental `data-*.js` parser coupling |
| Progress decision | session-only pilot; no new storage key |

### Adversarial examples the spec must represent

- one lemma with two frames (`rozmawiać z/o`);
- two simultaneous complements (`prosić kogoś o coś`);
- experiencer/stimulus reversal (`podobać się`);
- predicative/constructional contrast (`być` + Instrumental versus `to jest` + Nominative);
- a means/method relationship that must not be assumed to be ordinary lexical government (`płacić` + Instrumental);
- reflexive/non-reflexive meaning split (`interesować się` versus non-reflexive use);
- reviewed linked forms that are not interchangeable answers (`szukać/znaleźć`);
- direct-object negation without mislabeling Genitive as the lemma's sole government;
- an infinitive or clause complement;
- a valid pattern approved only for recognition.

### Deliverables/exit gate

- owner-approved schema and editorial style guide;
- owner-approved minimal syntactic-relationship distinction, demonstrated on `płacić`, `być`, `to jest` and `podobać się`;
- explicit resolution plan for `nie lubię` and `chcieć` inconsistencies;
- stable-ID and review-state policy;
- 5–8 non-production fixtures covering positive/adversarial shapes;
- documented decision that schema and migration revision remain 2;
- native-review workflow and named approval authority.

**No production pattern data, UI, activity, audio, page or persistence belongs in Phase 1.**

## Phase 2 — audit tooling and frozen safeguards

**Objective:** make invalid/unreviewed data impossible to ship before adding learner content.

Expected work:

- dedicated parser and closed-schema validator;
- complement/case/preposition conditional validation;
- global IDs, typed cross-refs and aspect/reflexive relationship checks;
- provenance/review transition validation;
- approved-only collectors for search/activity/audio fixtures;
- independent ID/wording/policy/structure frozen snapshot;
- positive and negative candidate fixtures;
- CI integration that leaves all current totals/baselines unchanged.

Exit gate: tooling rejects unknown fields, dangling refs, invalid state/eligibility and baseline drift. There is still no learner feature.

## Phase 3 — small approved data/reference pilot

**Objective:** prove the model with a small subset before all 30 candidates.

Recommended first slice: 6–10 high-support patterns spanning direct Genitive, Dative, preposition+Accusative, Instrumental and one reviewed multi-pattern lemma. Good research candidates include `szukać`, `pomagać`, `słuchać`, `czekać`, `potrzebować`, `używać`, `interesować się` and `rozmawiać`; final selection depends on Phase 1/native approval.

Expected capabilities:

- read-only verb-first reference and optional pattern blocks resolved from one-way refs;
- field-aware search adapter;
- optional session-only existing choose/build practice;
- no current-card edits, current activity-pool changes or progress writes;
- explicit loader/SW required-asset/network-first integration and cache bump;
- accessibility/mobile/offline tests.

Exit gate: all records approved, deterministic prompts, pattern session leaves `popolsku-progress-v2` byte-for-byte unchanged, existing totals remain pinned and offline deployment is atomic.

## Phase 4 — complete the 30-verb data pilot and approved audio

**Objective:** expand only after the small slice validates the model.

Sequence:

1. externally verify and native-review each remaining candidate;
2. resolve meaning/aspect/reflexive/CEFR/activity decisions;
3. independently author and review examples;
4. inventory exact existing-audio reuse and net-new phrases;
5. approve the delta;
6. generate/verify clips and perform native listening QA;
7. update manifest/pinned counts/offline retention tests atomically.

Exit gate: all learner-facing records are approved, no research-only fields leak publicly, audio parity is exact and current content/progress baselines remain stable.

## Phase 5 — optional advanced activities or durable mastery

This is a separate product decision, not a presumed continuation.

Possible scope:

- richer pattern mix/spacing;
- new drill types;
- durable pattern mastery;
- backup/export support;
- transfer rules between card and pattern mastery.

Before any durable state, decide whether to use a rigorously validated separate namespaced store or a real progress v3. Update semantic backup preflight/restore, corrupt/newer-version behavior and migration tests. Any change to existing persisted IDs, progress shape or mastery semantics requires explicit owner approval and migration design.

## Phase 6 — optional generated pages/discovery expansion

Only if separately justified:

- choose a curated public subset, not 1,001 or automatically all 100;
- dedicated renderer with stable slugs/canonicals;
- unique meaning/frame content rather than duplicated case prose;
- sitemap, service-worker generated inventory and build checks;
- approved records only;
- SEO/rights/editorial review.

Static pages are not required for the learning pilot.

## Cross-phase safeguards

| Safeguard | Rule |
|---|---|
| Existing content | no bulk card edits; current frozen baselines move only under explicit separate approval |
| Progress | schema/revision stay 2 until a persisted-semantics decision genuinely requires otherwise |
| Audio cache | never rename `popolsku-audio` as ordinary release plumbing |
| Shell cache | bump when shell/precache assets change |
| Source rights | locators/facts only; no entries/examples/index reproduction |
| Linguistic quality | no AI/source-only candidate becomes learner-facing without human gates |
| Activity safety | default false; deterministic accepted set required |
| Scope | 100-verb pool is research backlog, not implementation authorization |

## Migration trigger matrix

| Change | Migration? |
|---|---|
| Independent approved data + session-only reference/practice | no |
| One-way refs to unchanged existing IDs | no |
| New shell/data asset and cache bump | no progress migration |
| New nonpersistent search/activity adapter | no |
| New durable pattern store | explicit storage/backup decision; possibly migration |
| Existing card/topic ID split, merge, retirement or reassignment | yes |
| Transfer of card mastery to pattern mastery | yes |
| Change to v2 progress shape/meaning | yes |

## Immediate recommendation

Approve Phase 1 only. Do not authorize production content, UI or storage in the same review. The central outcome should be a specification that a native reviewer, content author and engineer interpret identically.
