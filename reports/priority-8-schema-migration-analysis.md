# Priority 8 Phase 0 — schema and migration analysis

## Recommendation

Keep:

- `SCHEMA_VERSION = 2`;
- `CONTENT_MIGRATION_REVISION = 2`;
- Verb Patterns public `formatVersion = 1`.

No proposed Priority 8 work requires learner-progress migration.

## Why the changes are additive

- `audioEligible` already exists as a required Boolean on every public/private example.
- `activityEligibility` already exists as an explicit pattern allowlist.
- New lemmas, meanings, patterns, examples and stable IDs expand the independent Verb Patterns corpus without changing the object shape.
- `patternDataRevision` already exists for content/projection transitions.
- Verb Patterns create no durable learner mastery state. Current progress remains keyed to existing cards/topics, not `vp-*` entities.
- Playback speed already uses its own preference and needs no new persistent record.
- Stable-ID additions and tombstones live in the private frozen release history, not the learner schema.

The proposed policy change is semantic: pronunciation eligibility no longer implies Listening. It requires validator/spec/test updates but not a new JSON field or shape. Unknown activity values continue to fail closed.

## Conditions that would require separate approval

Escalate rather than silently bump if a later phase proposes:

- durable pattern mastery, listening scores or per-example progress;
- a new persisted preference with migration requirements;
- changing existing storage keys/record shapes;
- removing/renaming required runtime fields;
- a second runtime envelope/parser;
- recycling or translating stable IDs;
- converting eligibility into inferred state.

A schema/migration bump would require a separate design, backup/restore analysis, idempotent migration, recovery path, cross-version tests and explicit owner approval. None is justified for Priority 8 as scoped.
