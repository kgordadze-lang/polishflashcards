# Priority 7 — Data-Model Options

**Phase:** 0 architecture analysis only. No schema or production dataset was created.

## Recommendation

Adopt a **one-way hybrid**:

1. a canonical independent `lemma → meaning → pattern` dataset owns linguistic facts;
2. pattern records may contain typed references to existing card, topic, drill or scenario IDs;
3. existing cards remain byte-for-byte unchanged in the pilot;
4. any reverse “show patterns for this card” index is computed at runtime or build time, not authored as backlinks.

This preserves the additive/migration safety of an independent dataset while allowing deliberate integration with current content.

## 1. Option comparison

| Criterion | A. Independent dataset | B. Extend existing cards | C. One-way hybrid |
|---|---|---|---|
| Multiple meanings/patterns | strong | awkward; card is translation/display grain | strong |
| Existing-card edits | none | many | none required for pilot |
| Frozen-content risk | new baseline needed | high: existing wording/policy/structure | new baseline only |
| Progress migration | unnecessary if session-only | easy to couple accidentally | unnecessary if one-way/session-only |
| Search/activity integration | explicit adapters | automatic exposure can be unsafe | explicit and controlled |
| Provenance/review | clean ownership | pollutes card schema | clean ownership |
| Reuse of stable content IDs | optional references | intrinsic but semantically weak | typed optional references |
| Recommended | safe but isolated | reject as canonical store | **yes** |

### Why not Option B

Cards model an utterance or translation unit. Many `pl` values are phrases or inflected forms, while one linguistic lemma may need several meanings and several complement frames. The card field allowlist rejects new pattern fields, and existing card changes are covered by frozen wording/policy/structure checks. Current card eligibility also feeds Type It, Listening and Mixed pools. Extending cards would create bulk historical edits, ambiguous ownership and accidental activity/progress consequences.

### Why not a fully isolated Option A

It is structurally safe, but a dataset without typed links and explicit consumers would be invisible to learners, search, activities, audio, offline loading and existing content. The one-way hybrid adds discoverability without making current cards own the new facts.

## 2. Smallest safe conceptual shape

This is a Phase 1 discussion shape, not a mandated schema:

```text
dataset
  formatVersion
  lemmas[]
    id
    form
    surfaceSieForm
    aspect
    aspectPartnerIds[]?
    meanings[]
      id
      glossEn
      cefr
      patterns[]
        id
        complements[]
          type: case | preposition-case | infinitive | clause
          case?
          preposition?
          questions[]?
          role?
          optional?
        example { pl, en }?
        productionStatus
        activityEligibility?
        contentRefs[]?
        evidence[]
        review
```

The smallest safe model still needs arrays at meaning, pattern and complement levels. A loose `secondaryCase` field would not explain which question/role belongs to which complement and would fail for three-part frames.

## 3. Required invariants

### Lemma and meaning

- Reflexive and non-reflexive forms are distinct stable entities; `się` is not a display decoration.
- Aspect partners are explicit links between distinct entities, never automatically collapsed into one progress identity.
- A lemma may have more than one meaning; a meaning may have more than one pattern.
- English glosses identify the intended meaning and do not act as production prompts by default.

### Complement representation

- Use full internal case IDs: `nominative`, `genitive`, `dative`, `accusative`, `instrumental`, `locative`, `vocative`.
- `preposition-case` requires both a preposition and case.
- A direct `case` complement must not carry a preposition.
- Questions and semantic roles belong to the complement they explain.
- Multiple complements are multiple typed objects, in a deliberate presentation order.
- Infinitive and clause complements are explicit types, not encoded as case strings.
- Required/optional status must be explicit only where the distinction is editorially meaningful.

### Syntactic relationship is a Phase 1 decision

The complement `type` describes the surface shape needed for validation and teaching; it must not silently assert that every case-connected phrase is ordinary lexical government. Phase 1 must decide the smallest useful internal distinction among:

- lexical government;
- preposition-governed relationships;
- predicative/constructional relationships;
- means/method or adjunct-like relationships;
- subject/experiencer relationships.

This does not mandate a large taxonomy or even a particular field. The approved representation only needs enough precision to keep materially different relationships from being flattened while learner wording stays simple. The decision must be tested against `płacić` + Instrumental method, `być` + Instrumental role/profession, `to jest` + Nominative, and `podobać się` with a Nominative stimulus and Dative experiencer.

### IDs

- IDs should be lowercase kebab-case and globally unique within the pattern corpus.
- IDs must be stable, semantic and independent of array position or CEFR placement.
- Lemma, meaning and pattern IDs must not be reused after retirement.
- Card/topic/drill/scenario references must include a `kind` and resolve to exactly that kind.
- Aspect-partner links must be reciprocal or have a documented one-way rule; cycles/self-links should fail validation.

Exact ID syntax and whether meaning IDs embed lemma IDs are Phase 1 decisions. The existing repository permits `[a-z0-9-]+`, but adopting a convention is not the same as implementing it.

## 4. Review and provenance

Recommended fail-closed states:

`research-candidate → externally-verified → native-reviewed → approved`

Alternative terminal/eligibility states are `recognition-only`, `rejected`, and `deferred`. Only `approved` records may enter learner-facing activities/audio; `recognition-only` additionally blocks production.

Evidence should store source ID, locator and fact type, not copied passages. Authored examples must be separately identified. Review metadata should identify the reviewer/ref, date, disposition and any restricted activity/register decision.

## 5. Activity eligibility

Eligibility should be an allowlist with a default of false, conceptually separating:

- reference/display;
- search discovery;
- recognition choice;
- grammar choose;
- grammar build/cloze;
- listening;
- active typing;
- conversational reinforcement.

A status such as `approved` does not imply that every activity is safe. A multi-meaning pattern may be approved for reference and choose practice but not bare English Type It.

## 6. File and loader strategy

Do not name the independent file `data-*.js` unless the current global parser contract is intentionally changed. Both [`validate_content.py`](../validate_content.py) and [`pp_audio_rule.py`](../pp_audio_rule.py) glob every `data-*.js` and expect `PP_LEVELS.push(...)`; generic `pl`/`ex` fields can also leak into audio discovery.

A distinct filename such as `verb-patterns.js` is safer, with:

- a dedicated closed-schema parser/validator;
- an explicit loader before any consuming adapter;
- an explicit field-aware search adapter;
- an explicit approved-example audio collector;
- explicit service-worker required-asset and network-first classification;
- a separate immutable ID/wording/policy/structure snapshot.

The exact file format—JavaScript assignment versus JSON—and CSP/media-type implications remain Phase 1 decisions.

## 7. Frozen-content implications

The current forward baseline pins 1,675 IDs, 13,387 wording entries, 1,312 policy entries and 1,777 structure entries, with snapshot digest `2a71401d8966ccbda59ec696f2c41cc3b48801d5c6059a881183b44ea3a1ce50`. A dataset outside `PP_LEVELS` would bypass those checks unless it receives its own closed validator and frozen snapshot.

Therefore:

- do not treat “outside the existing validator” as flexibility;
- establish the pattern baseline before learner-facing records ship;
- require deliberate approval for additions/wording/policy/structure changes;
- reject removed, moved, reused or repurposed IDs;
- keep existing PP_LEVELS content untouched during the pilot.

## 8. Progress and migration

Current progress schema and migration revision are both 2. Existing progress is card/topic oriented (`known`/`still` arrays keyed by stable content IDs). Grammar sessions have no durable progress.

An additive dataset plus session-only pattern activities requires:

- no `schemaVersion` change;
- no `CONTENT_MIGRATION_REVISION` change;
- no existing progress transformation;
- no pattern IDs in current `known`/`still` arrays.

A migration decision becomes mandatory if a later phase:

- splits, merges, retires or reassigns existing persisted IDs;
- changes progress shape or semantics;
- transfers card mastery into pattern mastery;
- introduces a durable pattern-progress store that backup/restore must validate semantically.

The backup currently copies every `popolsku-*` key but only understands existing migration state. A new durable key would be copied without adequate semantic validation unless backup preflight, counts, restore and compatibility tests were extended. The pilot should avoid that risk.

## 9. Decisions Phase 1 must lock

1. entity boundaries and exact field names;
2. meaning and multiple-pattern rules;
3. complement type/case/preposition/question constraints;
4. the smallest useful syntactic-relationship distinction, including the five cases above;
5. aspect/reflexive identity rules;
6. stable ID and retirement policy;
7. CEFR, recognition and production semantics;
8. activity allowlist/default behavior;
9. provenance/review states and transition authority;
10. example/gloss/common-error conventions;
11. file, loader, validator, frozen snapshot and offline strategy;
12. explicit decision to keep pilot progress session-only.

No learner content should be authored until these decisions are approved.
