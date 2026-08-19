# Priority 7 — Phase 1 Summary

**Phase:** Pedagogical and Data Specification only  
**Outcome:** the architecture and editorial contract are locked; no production verb-pattern content or application behavior was created.  
**Next-step status:** **NO-GO pending owner approval.** Phase 2A tooling may be authorized without populated reviewer names; named human authorities are mandatory before real Phase 2B candidates advance through review.

## 1. Safety baseline

Before work, all required checks passed:

| Check | Verified value |
|---|---|
| Branch | `priority-7-phase-1-specification` |
| HEAD | `ba58c7f2b2b4479ba8d3be1156981521ea5e8491` |
| Tree | `02896b9dc08c923778301495a3514d9b7505af2e` |
| Git remotes | none |
| `push.default` | `nothing` |
| Initial worktree | clean |

Phase 0 was treated as authoritative: 181 primary lemmas, 98 direct Mędak matches, the approved 30-candidate working set and tiered 100-verb research pool remain unchanged. No Phase 0 audit was rerun and no candidate was promoted to approved content.

## 2. What is locked

### Entity hierarchy

The full editorial canonical record is independent and one-way-linked to existing content:

```text
dataset → lemma → meaning → pattern → ordered complements[]
                                  └→ reviewed examples[]
```

Existing cards do not become the canonical store. The full record is private editorial/audit data; a separately validated public runtime projection contains only learner-consumer fields. A lemma is one lexical form including `się`; aspect partners and reflexive/non-reflexive forms are distinct entities. A meaning is split when semantic roles, truth conditions, register/CEFR, or safe activity interpretation differ. Different syntax creates a separate pattern; it creates a separate meaning only when the learner sense also differs.

### Syntactic relationship model

One pattern-level enum is locked:

- `lexical-frame` — direct, prepositional, infinitive, clause, or multi-complement frame selected by the meaning;
- `constructional-frame` — a lemma-headed broader construction such as predication determines the case;
- `means-method` — means/method or adjunct-like phrase, preventing an “always takes” claim;
- `subject-experiencer` — non-English-like subject/stimulus and experiencer mapping.

Complement type separately distinguishes direct from prepositional shape. This is the smallest model that handles `płacić`, `być`, and `podobać się` without academic overengineering.

Fixed `to jest` + Nominative is explicitly an **out-of-corpus constructional contrast**. The model has no structured fixed-`to` constituent, so it must not produce a misleading generic `być + Nominative`. A future `być` record may link through a typed content reference to a grammar explanation. Canonical support for fixed constructions would require a broader model, not a one-off display field.

### Complement and case model

Complement types remain closed to `case`, `preposition-case`, `infinitive`, and `clause`. `case-or-clause` and every other union type are prohibited. Multiple complements are ordered objects with explicit `required` and closed `role` metadata; order is pedagogical, not fixed Polish word order.

Full case IDs are `nominative`, `genitive`, `dative`, `accusative`, `instrumental`, `locative`, and `vocative`. Static English/Polish names and base questions are central metadata. Questions derive for direct and prepositional complements; `questionOverridePl` is a native-reviewed exception. Abbreviations are never IDs or sole learner labels. Direct Locative/Vocative complements are invalid; Nominative direct slots are restricted to constructional/subject-experiencer patterns.

One exact structured preposition belongs to each `preposition-case` complement. Alternative prepositions use separate patterns. Clause kinds are `ze`, `czy`, `zeby`, and `interrogative`.

### Stable IDs

IDs use lowercase ASCII repository-compatible namespaces:

- lemma: `vp-l-<slug>-<digest12>`;
- meaning: `vp-m-<slug>-<meaning-key>-<digest12>`;
- pattern: `vp-p-<slug>-<meaning-key>-<pattern-key>-<digest12>`;
- example: `vp-e-…`;
- future exercise: `vp-x-<pattern-stem>-<activity-type>-<item-key>-<digest12>`.

The digest is the first 12 hex characters of SHA-256 over exact versioned UTF-8 seeds. Exercise seeds include both explicit `activityType` and immutable authored `itemKey`, so one pattern can own multiple items of one type. Immutable internal keys, not learner wording or positions, determine allocation. IDs are never reused; structural repurposing creates a new ID and tombstones the old one.

`relationType` is structural pattern identity. Before release, a wrong unshipped candidate may be replaced. After release, any relation-type change creates a new key/ID and tombstones the old pattern.

### Aspect and reflexivity

Aspect partners remain separate lemma/pattern identities. Links are explicit, reciprocal, native-confirmed, and never cause inheritance. Equivalent aspect patterns are duplicated explicitly and linked only after review. `się` is part of canonical lemma, identity seed, display, search identity, audio expectations, and typed answers. The `reflexive` Boolean is a redundant mechanical assertion, not a second analysis: fixing only the Boolean may keep ID; adding/removing lexical `się` creates a new released lemma identity. No repository `pair` string is promoted automatically.

### CEFR and production/recognition

CEFR is stored on patterns only; lemma and meaning floors derive from their children. `recognition` is earliest introduction and optional `production` is earliest active production. Values are A1/A2/B1/above-B1. Teaching status is the smallest actionable set:

- `active-production`;
- `recognition-only`;
- `deferred`.

Valid advanced or restricted dictionary constructions are omitted or deferred; the corpus is not exhaustive. Approval never implies activity eligibility.

### Usage/register

Structured usage is limited to priority `core`/`common`/`limited` and register `neutral`/`formal`/`informal`. `limited` requires an approved learner-facing note and MUST NOT be `active-production` in the A1–B1 pilot. The model does not invent fine-grained frequency claims.

### Provenance and review

Evidence records store `sourceId`, source kind, locator, fact type, check date, and optional short note—never source passages. A cited evidence digest covers the complete evidence record including note; editing/removing it invalidates acceptance, while adding a separate corroborating record does not. Examples record original human authorship or approved repository reuse with an exact per-example `repositorySource` pointing to a stable card/drill ID and utterance field.

Fail-closed review states are:

`research → externally-verified → native-reviewed → approved`, with terminal/paused `deferred` and `rejected`.

Append-only human events identify external verification, native linguistic review, and product approval. Every accepted stage carries `scopeVersion: 1` and a full SHA-256 digest of an RFC 8785 canonical projection. Every projection includes the owning lemma and meaning. External scope covers linguistic structure/usage; native scope adds CEFR, teaching status, explanation, examples, errors, activity/audio eligibility; product scope additionally covers content references. Raw evidence/review audit logs are excluded, with external events pinning supporting evidence-record digests; native/product error claims replace numeric authoring indexes in their fingerprints with ordered complete digests of the evidence records those indexes currently resolve. Parent, covered-field, or referenced-evidence-target changes therefore invalidate stale approvals mechanically. AI agreement is never sufficient.

The full editorial record—including `internalScope`, evidence, review events/digests, registries, and origins—may use `editorial/verb-pattern-candidates.json` only inside the isolated local Priority 7 workflow. It MUST NOT enter the production/public repository or transfer/tree inventory; directory naming and “not loaded” are not privacy controls. A durable private home is a Phase 2B operational decision before real authoring.

Public `content/verb-patterns.json` is a generated runtime projection, not the editorial source. After validating all three current approvals and the complete prior frozen/tombstone/revision transition, the release authority admits only approved active/recognition patterns and emits IDs, lemma/display/aspect data, learner glosses, structured patterns/complements, CEFR/status/usage/explanations, eligibility, learner examples/translations/audio flags, runtime content refs, and learner error guidance. It excludes internal scope/keys, evidence/source data, review state/events/digests, registries/reviewer refs, example origin/author data, evidence refs, editorial notes, and all unapproved/deferred/rejected candidates. A standalone runtime-shape transform is nonrelease tooling and cannot establish active membership from retained allocations.

### Learner terminology and authoring

Prefer “For this meaning…”, “This verb takes…” only for accurately scoped lexical frames, “Ask `kogo? czego?`”, “Use `na` + Accusative”, and role-based prompts. Constructional/method/experiencer wording names the actual function. Internal taxonomy is hidden.

Future examples are genuinely original or exact validator-resolved approved repository reuses; all are short, natural, CEFR-controlled complete sentences in practical contexts. They normally isolate one target and avoid unintentional negation. English glosses translate meaning naturally without implying syntactic equivalence. Common errors are optional and must be documented; a predicted distractor is labeled separately.

### Activity eligibility

Eligibility is an explicit allowlist, default false, with keys for reference, search, grammar choose/build, Type It, listening, Mixed Quiz, Case Mix, and conversation. `recognition-only` forbids `grammar-build` and `type-it`; mixed/choose item semantics remain future item-level validation. Type It requires a fully closed answer set and complete context. Listening uses only approved natural sentences. Mixed practice remains pattern-aware and session-only; conversations are contextual reinforcement only.

### Audio

Only exact approved Polish example sentences under patterns eligible for `listening` may set `audioEligible: true`, followed by later audio/native QA. `reference` alone never authorizes audio. Existing normalized utterances are reused where exact. Lemma labels, pattern notation, case labels, questions, and feedback remain silent. No audio was generated.

### Persistence and frozen data

The pilot has no persistent pattern mastery. It creates no durable key, never writes pattern IDs into existing card/topic progress, and never transfers mastery. Pattern sessions must leave `popolsku-progress-v2` byte-for-byte unchanged.

Before learner data ships, private editorial audit dimensions and the separate runtime projection are frozen independently. `patternDataRevision` begins with the first released runtime projection; it is neither an editorial WIP counter nor a progress migration. Tombstones prevent ID reuse.

### Future filename/loader

The editorial envelope is exactly `artifactStatus: priority-7-editorial-nonproduction`, `formatVersion: 1`, and full `lemmas`; it has no `patternDataRevision`. The public runtime envelope is `formatVersion`, released `patternDataRevision`, and projected `lemmas`. A future loader reads only `content/verb-patterns.json`. Phase 2A owns separate fictional-fixture, full-editorial, and runtime schemas plus the complete frozen release boundary. Runtime/offline integration is atomic later; report JSON files are never runtime data.

## 3. What remains provisional

No individual 30-verb government fact, meaning boundary, pattern, example, aspect pair, CEFR, register, or activity decision is linguistically approved. The illustrative JSON uses invented verbs and is explicitly nonproduction. The Phase 0 pilot candidates remain research candidates.

Open native/contemporary questions include:

1. exact optionality/classification and wording for `płacić` method;
2. predicative boundaries and learner presentation for `być`; `to jest` remains a linked grammar contrast unless a broader construction model is separately approved;
3. subject/stimulus/experiencer wording for `podobać się`;
4. meaning/construction priority for `zależeć`;
5. nominal versus clause frames and meaning scope for `mówić`;
6. second-frame meaning/register for `bać się`;
7. every aspect link and reflexive/non-reflexive relationship;
8. the existing `nie lubię` negation inconsistency;
9. the existing `chcieć` case/register inconsistency;
10. final CEFR/status/usage/examples/glosses/eligibility for every authored record.

These do not block generic audit-tool design, but they block affected learner content.

## 4. Version and migration decision

Phase 1 requires no changes:

| Item | Remains |
|---|---|
| APP_VERSION | `8.10` |
| shell cache | `popolsku-v65` |
| AUDIO_CACHE | `popolsku-audio` |
| progress `schemaVersion` | `2` |
| `CONTENT_MIGRATION_REVISION` | `2` |

Persistent pattern mastery, a new durable store, card↔pattern transfer, existing stored-ID changes, or backup semantic changes would reopen a separate migration design.

## 5. Deliverables

1. `priority-7-phase-1-summary.md`
2. `priority-7-pattern-data-specification.md`
3. `priority-7-pedagogical-specification.md`
4. `priority-7-stable-id-specification.md`
5. `priority-7-provenance-and-review-specification.md`
6. `priority-7-activity-eligibility-specification.md`
7. `priority-7-content-authoring-specification.md`
8. `priority-7-frozen-data-and-persistence-specification.md`
9. `priority-7-phase-2-readiness-checklist.md`
10. `priority-7-pattern-schema.example.json` — fictional, explicit specification example only
11. `priority-7-pattern-schema.spec.json` — nonproduction JSON Schema precision aid

## 6. Proposed Phase 2A/2B subdivision and prerequisites

This is a proposed controlled refinement of the original roadmap, not automatic authorization:

- **Phase 2A — three schemas plus approval/projector/ID/frozen tooling:** fictional nonproduction fixtures only; no real candidate records or learner consumers.
- **Phase 2B — 30-verb pilot authoring:** real records remain in nonproduction editorial data while research/external/native/product review proceeds. Native review remains a separate gate before learner implementation.

Phase 2A requires owner approval of Phase 1 and explicit Phase 2A authorization. It does not require reviewer names merely to validate fictional shapes. Before Phase 2B records can advance beyond research, the appropriate named human authorities and source policy must exist.

1. independent product-owner approval of all Phase 1 reports;
2. explicit Phase 2A authorization limited to validator/ID/frozen tooling, tests, and fictional fixtures;
3. confirmation that the editorial artifact is outside the public repository/transfer/tree and only the runtime projection can be loaded or shipped;
4. before Phase 2B review advancement: named human product-approval authority;
5. before Phase 2B review advancement: named competent native Polish linguistic reviewer/pool;
6. before Phase 2B review advancement: named contemporary external-verification role and accepted-source policy;
7. confirmation of locator-only rights and original-example policy;
8. fresh branch/HEAD/tree/remote/push/worktree safety checks;
9. implementation plan proving separate editorial/runtime schemas and projector plus unchanged existing content, totals, progress, audio, pages, versions, and caches;
10. adversarial tooling fixtures for all four relation types and four complement types, plus the out-of-corpus `to jest` boundary;
11. confirmation that automation/AI cannot promote a candidate to `approved`, and runtime consumers never receive audit/private fields.

## Phase 2A / Phase 2B GO / NO-GO checklist

- [x] Entity, relation, complement, case, preposition, aspect, reflexive, ID, CEFR, status, usage, provenance, review, terminology, activity, audio, frozen, persistence, and file/loader decisions are specified.
- [x] Eleven verb-pattern stress fixtures fit structurally; `to jest` is correctly rejected as an out-of-corpus fixed-construction contrast.
- [x] Example and JSON Schema artifacts are explicitly nonproduction.
- [ ] Product owner has approved the specification.
- [ ] Phase 2A fictional-tooling-only scope is explicitly authorized.
- [ ] Phase 2 baseline safety checks have been rerun.

**Current decision: NO-GO.** Move to **GO for Phase 2A only** after owner approval, explicit authorization, and fresh safety checks. Named reviewers/source policy are a separate mandatory gate before Phase 2B candidates advance; Phase 2B itself remains nonproduction authoring, not learner implementation.

## 7. Decision-log index

Each normative report records decision, alternatives, rationale/consequence, reversibility, and reopen trigger. The principal locked choices are: independent one-way corpus; fixed-`to` boundary; four relation types; structural relation identity; four complement types; central question derivation; deterministic digest IDs including exercise item keys; exact review-scope and complete evidence-record digests; typed per-example repository reuse; explicit/non-inheriting aspect links; distinct reflexive identity; pattern-only CEFR; private full editorial authority projected to approved-only public runtime; default-false and fail-closed activity/audio eligibility; runtime-only frozen revision; no pilot persistence; and owner-approved Phase 2A/2B subdivision.
