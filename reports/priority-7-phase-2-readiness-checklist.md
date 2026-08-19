# Priority 7 — Phase 2A/2B Readiness Checklist

**Phase 1 outcome:** corrected specification decisions are complete; no next phase is automatically authorized.  
**Current gate:** **NO-GO pending product-owner approval of Phase 1 and explicit Phase 2A authorization.**

## 1. Proposed controlled roadmap subdivision

- **Phase 2A — three schemas plus approval/projector, ID, review-digest, and frozen tooling:** fictional fixtures only. No real candidates, learner consumers, production data, UI, search, audio, progress, or loader integration.
- **Phase 2B — 30-verb pilot authoring:** real full records stay in an isolated private/local editorial workflow. They never enter the public static-site repository. Native review remains a separate gate before learner implementation.

Owner approval is required separately for 2A and 2B. Generic 2A tooling does not require populated reviewer names. Named external, native, and product authorities are mandatory before real 2B records advance through the corresponding stages.

## 2. Three explicit data contracts

### A. Phase 1 fictional specification fixture

The existing report JSON/Schema validates invented Phase 1 examples only. Its `artifactStatus` is `specification-example-not-production`. It is neither an editorial-authoring schema nor a runtime schema.

### B. Full private editorial schema

Envelope:

```json
{
  "artifactStatus": "priority-7-editorial-nonproduction",
  "formatVersion": 1,
  "lemmas": []
}
```

It owns the full authoritative record: internal scope/keys, evidence, review state/events/digests, registries/references, complete example origin, and all learner/product fields. `patternDataRevision` is forbidden. The working file name `editorial/verb-pattern-candidates.json` is allowed only inside the isolated local Priority 7 workflow. It MUST be absent from the production/public repository transfer set and final tree. Directory naming, not loading, and not precaching are not privacy controls.

If a durable private home is needed after the local workflow, Phase 2B must approve its operational/security design before real authoring.

### C. Public runtime schema

`content/verb-patterns.json` is a generated runtime projection with envelope `formatVersion`, released `patternDataRevision`, and projected `lemmas`. It contains only fields required by learner consumers and rejects every private/editorial field. Runtime consumers do not receive or interpret approval/audit data.

The release-authoritative frozen transition must validate full editorial records and current digests, prior frozen state, allocations, active identities, tombstones/no resurrection, replacements, retained review history, exact runtime projection, and the runtime revision transition before a deployable asset can be sourced from its `runtimeProjection`. A pure standalone projector is nonrelease tooling only.

## 3. Corrected specification completeness

- [x] Entity hierarchy, four relations, four complements, `to jest` boundary, aspect/reflexive identity, IDs, CEFR, and no persistence remain locked.
- [x] `relationType` is released structural identity.
- [x] Full external/native/product review fingerprints and evidence pinning are deterministic.
- [x] Editorial and runtime layers/envelopes are separately specified.
- [x] Runtime projection’s exact included/excluded field sets are locked.
- [x] `patternDataRevision` is runtime-release-only, never editorial WIP state.
- [x] Editorial file absence from the public repository/transfer/tree is a release invariant.
- [x] Per-example `repositorySource` structurally identifies exact card/drill ID and field.
- [x] `recognition-only` forbids `grammar-build` and `type-it`.
- [x] `limited` forbids `active-production` for the A1–B1 pilot.
- [x] `supportingEvidenceDigests` is accepted-external-only.
- [x] Audio requires approved `listening`; `reference` alone is insufficient.
- [x] Editing/removing a pinned evidence record, including its note, invalidates acceptance.
- [x] Native/product error-note fingerprints resolve numeric evidence indexes to ordered complete evidence digests.
- [x] `reflexive` is a redundant assertion; lexical `się` addition/removal replaces released identity.
- [x] Runtime shape/allocation validation is distinct from complete frozen release validation; retained tombstoned allocations never prove active membership.

## 4. Phase 2A authorization gate

- [ ] Product owner approves all corrected Phase 1 reports.
- [ ] Product owner explicitly authorizes **Phase 2A only**.
- [ ] Phase 2A plan maps every change to the three schemas, projector, ID/review/frozen tooling, tests, or fictional fixtures.
- [ ] Fresh branch/HEAD/tree/remote/push/worktree checks pass.
- [ ] Existing content baselines, progress, audio, generated pages, versions, and service worker remain unchanged.
- [ ] No automation or AI can fabricate a human acceptance or project a record with stale digests.

Reviewer names are not a Phase 2A prerequisite.

## 5. Additional Phase 2B gate

- [ ] Product owner separately authorizes nonproduction Phase 2B authoring.
- [ ] External-verification authority/source policy, native reviewer pool, and product authority are named.
- [ ] Locator-only Mędak and original/repository-reuse rights policies are confirmed.
- [ ] Initial candidate slice and authoring ownership are approved.
- [ ] Private location/transfer controls prove editorial data cannot enter the production/public repository or deployment.
- [ ] If durable retention beyond the local workflow is needed, its private operational home is explicitly approved first.

Phase 2B never authorizes learner implementation or runtime release.

## 6. Phase 2A tooling acceptance matrix

| Boundary / test | Required result |
|---|---|
| Phase 1 fictional example against fixture Schema | accept |
| Editorial envelope against editorial Schema | accept; runtime Schema rejects it |
| Runtime projection against runtime Schema | accept |
| Runtime record containing `internalScope` | reject |
| Runtime record containing `evidence`, source locator/note/ID, or registry data | reject |
| Runtime record containing `reviewState`, `reviewEvents`, `reviewerRef`, or any scope/evidence digest | reject |
| Runtime example containing `origin`, `authorRef`, `authoredAt`, or `repositorySource` | reject |
| Editorial artifact in public transfer inventory or final production tree | fail release |
| Candidate without current external/native/product acceptance | projector rejects |
| Approved teaching-deferred or review-deferred/rejected record | projector rejects |
| `recognition-only` + `type-it` | Schema rejects |
| `recognition-only` + `grammar-build` | Schema rejects |
| `limited` + `active-production` | Schema rejects |
| `repository-reuse` without exact `repositorySource` | Schema rejects |
| `original` carrying `repositorySource` | Schema rejects |
| repository source with wrong kind/field/dangling ID/nonmatching sentence | dedicated validator rejects |
| accepted external event without evidence digests | Schema rejects |
| native/product acceptance carrying `supportingEvidenceDigests` | Schema rejects |
| non-accept/reopen/correction carrying evidence/scope digests | Schema rejects |
| edited/removed pinned evidence record | current external acceptance invalid |
| `audioEligible: true` without approved `listening` | Schema rejects |
| direct Nominative with wrong relation/role | Schema rejects |
| parent/covered-field mutation | recomputed review state/digest invalid |
| two current externally pinned evidence records reordered under an unchanged numeric error reference | native/product scope becomes stale; approval and projection fail |
| evidence inserted before an error claim and numeric index updated to the same complete evidence digest | native/product fingerprint unchanged solely for that positional move |
| duplicate/moved/reused IDs or nonreciprocal links | dedicated validator rejects |
| allocation-only standalone projection contains a tombstoned historical ID | may validate shape, but is explicitly nonrelease and cannot authorize a release |
| complete frozen release transition attempts to resurrect a tombstoned ID | reject |
| standalone projection CLI | absent, or explicitly fixture/nonrelease name and wrapper; never deployable output |

## 7. Schema versus dedicated-validator responsibility

| Invariant | Owner |
|---|---|
| Same-record field/enum/conditional combinations | fixture/editorial/runtime JSON Schemas as appropriate |
| Exact editorial-to-runtime field projection | approval/projector plus runtime Schema |
| Global ID uniqueness/recomputation, parent ownership, sibling keys | dedicated validator |
| Reciprocal aspect links and typed existing-content refs | dedicated validator |
| Review transition order and current scope/evidence-digest resolution | dedicated validator |
| Source/reviewer registry resolution and human-role authority | dedicated validator/private workflow |
| Repository-reuse entity/field existence and exact sentence equality | dedicated validator |
| Editorial absence from public transfer/final tree | release inventory validator |
| Tombstones and private editorial/runtime frozen baselines | dedicated validator |
| Mixed/choose/case-mix item recognition-vs-production semantics | future activity-item validator |

## 8. Linguistic questions that do not block 2A

- [ ] `płacić` method optionality/wording.
- [ ] Exact `być` + Instrumental scope.
- [x] `to jest`: out-of-corpus grammar contrast.
- [ ] `podobać się`, `zależeć`, `mówić`, and `bać się` boundaries.
- [ ] Every aspect/reflexive relationship.
- [ ] Existing `nie lubię` and `chcieć` inconsistencies.
- [ ] Final CEFR/status/usage/examples/glosses/eligibility per real candidate.

These block affected real content, not fictional 2A tooling.

## Phase 2A / Phase 2B GO / NO-GO

- **Phase 2A:** **NO-GO** pending owner approval, explicit authorization, and fresh safety checks.
- **Phase 2B:** **NO-GO** pending separate authorization, named authorities/source policy, and private operational boundary.
- **Learner/runtime implementation:** not authorized by either subdivision.
