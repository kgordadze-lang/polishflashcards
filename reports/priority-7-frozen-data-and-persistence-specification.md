# Priority 7 — Frozen Data and Persistence Specification

**Phase:** 1 specification only  
**Decision:** independent frozen corpus; no persistent pattern mastery in the 30-verb pilot

## 1. Frozen surface

Before the first learner-facing pattern ships, a future dedicated validator establishes four private editorial audit dimensions and a separately generated public runtime projection snapshot:

| Snapshot | Frozen material |
|---|---|
| Identity | editorial format, every lemma/meaning/pattern/example ID, parent ownership, immutable key, structural `relationType`, and tombstones; released `patternDataRevision` exists only in the separate runtime snapshot |
| Structure | lemma form/reflexivity/aspect links; meaning ownership; ordered complements, type/case/preposition/clause kind/role/requiredness; aspect-equivalent links; typed content refs |
| Wording | display lemma, learner glosses/explanations, examples/translations, question overrides, usage/error/feedback learner copy |
| Policy | CEFR, teaching status, usage priority/register, activity and audio eligibility, review state, scope version, and current external/native/product scope digests |

Current PP_LEVELS baselines remain untouched. Full editorial snapshots, evidence, review history, and registries remain private to the isolated Priority 7 workflow; they MUST NOT be transferred to the public site repository. The runtime snapshot covers only the generated field projection and its released `patternDataRevision`.

## 2. Change classes

| Change | Required workflow |
|---|---|
| Add a new approved entity | new `patternDataRevision`, validation, native/owner approval, atomic snapshot update |
| Wording correction with same meaning | preserve ID; correction review; wording snapshot update |
| CEFR/eligibility/register/review policy | preserve ID; evidence and owner approval; policy snapshot update |
| Case, preposition, role, `relationType`, complement count, or meaning boundary changes a released construction identity | create replacement key/ID, retire old ID, record reason/replacement, update revision/snapshots |
| Remove from teaching | retire/tombstone; never delete/reuse ID |
| Add corroborating provenance only | no identity change; audit update; revision bump only if production artifact bytes change |
| Reorder arrays | no semantic change; canonical serializer should prevent noisy diffs |

Learner wording is frozen for review integrity and regression visibility, not because copy can never improve. Every change remains possible through its explicit class.

Before first production release, an unshipped candidate with a wrong structural field may be replaced and its ID recomputed without a tombstone. Once present in an approved frozen baseline, `relationType` is always identity-bearing and cannot be edited in place.

## 3. Pattern data revision

Use independent positive integer `patternDataRevision`, starting at `1` when the first runtime projection is released. It increments for each released runtime change and is not an editorial work-in-progress counter, application version, shell cache, progress `schemaVersion`, or `CONTENT_MIGRATION_REVISION`. The nonproduction editorial envelope has no revision field. `formatVersion` changes only for incompatible data-contract semantics.

The revision supports audit, cache compatibility, and deterministic frozen comparisons. It carries no learner progress meaning.

## 4. Pilot persistence decision

The 30-verb pilot has no durable pattern mastery or progress. Consequences:

- pattern practice is session-only;
- no pattern ID enters existing `known`, `still`, topic, or card progress;
- no new localStorage/sessionStorage/IndexedDB pattern-progress key is created (ordinary in-memory session state only);
- `popolsku-progress-v2` remains byte-for-byte unchanged through loading, answering, completion, restart, and backup/restore;
- current Flashcard, Type It, Listening, Mixed, and case-topic totals/semantics do not change merely because pattern data exists;
- card mastery never implies pattern mastery, and pattern performance never changes card mastery;
- analytics/tracking are out of scope.

Session-only does not mean unvalidated: future activities still need stable item IDs for frozen content and diagnostics, but those IDs are not persisted as mastery.

## 5. Migration and version decision

For the specified independent, one-way, session-only pilot:

- `schemaVersion` remains `2`;
- `CONTENT_MIGRATION_REVISION` remains `2`;
- `APP_VERSION` remains `8.10` in Phase 1;
- shell cache remains `popolsku-v65` in Phase 1;
- `AUDIO_CACHE` remains `popolsku-audio`.

An implementation release may later bump APP_VERSION/shell cache for its own deployment, but that is not a progress migration and is outside this phase. `popolsku-audio` remains versionless unless separately redesigned.

## 6. Triggers for a future persistence/migration discussion

Stop and open a separate design before any of these:

- persistent pattern mastery, spacing, streaks, or attempt history;
- a new durable `popolsku-*` store;
- transfer or inference between card and pattern mastery;
- changing existing persisted card/topic IDs or semantics;
- changing backup counts, preflight, restore, export, or compatibility semantics;
- merging/splitting a released identity that has durable references;
- syncing pattern state across devices.

That design must decide separate namespaced store versus progress v3, semantic validation, migration idempotence, corrupt/newer-version behavior, atomic backup/restore, retention/privacy, and transfer rules before code or data ships.

## 7. Editorial record, projector, runtime file, and deployment ownership

The full authoritative record may use the working name `editorial/verb-pattern-candidates.json` only inside the isolated local Priority 7 workflow. It contains private/internal scope, evidence, review events/digests, registries, and example provenance. It MUST NOT be transferred to the production/public static-site repository, Pages source, build/deployment inputs, or final public tree. Not loading or precaching it is insufficient. Release inventory tests prove absence. A durable private home beyond this workflow is an explicit Phase 2B operational decision before real authoring.

Future public `content/verb-patterns.json` is a generated runtime projection, deliberately outside `data-*.js`, containing no audit/private fields. A pure current-editorial-to-runtime transform may exist for tests and as an internal step, but it has no release authority: a caller-supplied revision and an allocation registry cannot prove that retained historical IDs are still active. The sole Phase 2A release source of truth is `freeze_editorial(...).runtimeProjection`, produced only after the complete prior frozen state (when present), allocations, active identity, tombstones/no resurrection, replacements, retained review history, current approval, runtime parity, and revision transition have all validated.

Runtime validation without frozen state proves only the closed runtime shape/privacy contract. Runtime validation with repository/allocation context may additionally prove referential shape, kind, and parent ownership, but not active release membership because tombstoned allocations are intentionally retained. Complete release verification must validate the whole frozen envelope and its exactly derived `runtimeProjection`; Phase 2A exposes no deployment command.

A dedicated `pp-verb-patterns.js` loader reads only the public runtime projection. The projector/validators, runtime snapshot, consumer adapters, service-worker required-asset/network-first classification, and shell cache update deploy atomically. Audio inventory reads only projected examples with `audioEligible: true` under a pattern eligible for `listening`.

The file is not added in Phase 1. The report-only JSON artifacts under `reports/` are specifications and MUST be excluded from runtime discovery.

## 8. Verification requirements for later phases

Future tooling must prove:

1. three distinct contracts: Phase 1 specification fixture, full private editorial schema, and public runtime schema;
2. closed schema/canonical serialization for the editorial record and exact projector output;
3. identity/structure/wording/policy snapshot parity;
4. no retired/reused/moved IDs;
5. only approved records with matching scope digests can be projected;
6. runtime projection rejects editorial/private fields and editorial files are absent from production transfer/tree inventories;
7. unchanged PP_LEVELS frozen totals/digests;
8. unchanged progress bytes and absence of a new durable key;
9. explicit loader failure behavior and atomic offline install;
10. exact audio reuse/new delta before synthesis;
11. a runtime-shaped standalone projection containing a tombstoned historical allocation is never treated as release-authoritative, while complete frozen validation rejects resurrection;
12. any remaining projection CLI is named and wrapped explicitly as a nonrelease fixture.

## 9. Decision log

| Decision | Alternatives | Why selected | Reopen trigger |
|---|---|---|---|
| Four independent frozen dimensions | one whole-file checksum only | distinguishes identity, structure, copy, and policy intent | tooling complexity proves excessive after audit prototype |
| Full review-scope digests in policy baseline | narrative approval or revision number only | proves exact parent/meaning/pattern/example coverage and invalidation | only an equivalently deterministic signed manifest |
| Independent pattern revision | reuse progress migration/app version | avoids conflating content audit with learner state | only if a later unified release protocol provides equal clarity |
| `patternDataRevision` belongs only to released runtime projection | use it as an editorial WIP counter | keeps private authoring history separate from deployable corpus revisions | a concrete runtime release protocol requires a replacement counter |
| Complete frozen transition owns release projection | standalone projector plus caller revision/allocation lookup | retained tombstoned allocations cannot masquerade as active release membership | only a future authenticated release wrapper that validates the same complete frozen state |
| No pilot persistence | new store; reuse card progress | lowest migration/backup risk and honest skill semantics | explicit product value case for durable mastery |
| Tombstone retirement | delete records | protects references and reuse | not reversible after release |
| Private editorial source; generated `content/verb-patterns.json` runtime projection | commit the audit record; use `data-verb-patterns.js` | prevents publication of private audit fields and avoids existing validator/audio globs | repository discovery and a secure authoring boundary are deliberately redesigned |
