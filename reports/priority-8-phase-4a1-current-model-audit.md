# Priority 8 Phase 4A-1 — Current Verb-Pattern Model Audit

**Phase:** 4A-1 (repository audit only; no editorial authoring, no ID allocation)
**Scope:** factual reconstruction of the current released Verb Patterns model, mechanically reproduced from the repository.

Evidence in this report is tagged with its source:

- **OBSERVED FROM RUNTIME** — read directly from `content/verb-patterns.json`.
- **OBSERVED FROM PRIVATE GOVERNANCE** — read directly from `editorial/verb-pattern-candidates.json` and `editorial/priority-7-authoring-context.json`.
- **OBSERVED FROM SCRIPT/VALIDATOR** — read from `priority7_tooling.py`, `pp-verb-patterns.js`, `priority8_phase1_transition.py`, or observed by running a read-only command.
- **HISTORICAL REPORT CLAIM** — a prior report's stated number, not independently re-derived in this section.

## 1. Mechanically observed counts (OBSERVED FROM RUNTIME)

Computed directly from `content/verb-patterns.json` by walking every lemma → meaning → pattern → example:

| Metric | Value |
|---|---|
| Lemmas | 30 |
| Meanings | 34 |
| Patterns | 45 |
| Examples | 45 |
| contentRefs | 101 |
| errorNotes | 24 |
| teachingStatus = active-production | 41 |
| teachingStatus = recognition-only | 4 |
| audioEligible = true | 45 |
| audioEligible = false | 0 |
| activityEligibility non-empty | 0 (all 45 patterns carry `activityEligibility: []`) |
| patternDataRevision | 2 |
| formatVersion | 1 |
| aspect = imperfective | 29 |
| aspect = perfective | 1 (`znaleźć`) |
| reflexive = true | 6 |
| reflexive = false | 24 |
| `aspectPartnerIds` occurrences | 0 |
| `aspectEquivalentPatternIds` occurrences | 0 |
| `displayLemma` occurrences | 0 |
| `vp-x-` (exercise) IDs | 0 |

**Result: every core count matches the historical reference exactly** (30 lemmas / 34 meanings / 45 patterns / 45 examples / 101 contentRefs / 24 errorNotes / 41 active-production / 4 recognition-only). No discrepancy was found. This audit did not need to stop under Section 9's discrepancy clause.

ID uniqueness was checked mechanically over the whole file: lemma IDs, meaning IDs, pattern IDs, and example IDs are each 100% unique (30/30, 34/34, 45/45, 45/45 — no duplicates).

Cross-check (OBSERVED FROM SCRIPT/VALIDATOR): `python3 verify_audio.py` reports `content/verb-patterns.json   45 phrases  OK` and `3402 required phrase(s) checked against 3402 manifest entries and 3402 MP3(s) on disk` — the 45-example/45-audioEligible figure is independently corroborated by the audio inventory, not just the JSON walk.

`reports/priority-8-current-verb-pattern-inventory.md` (HISTORICAL REPORT CLAIM) separately states "There are 29 imperfective lemmas and one perfective lemma (`znaleźć`)" — this matches the runtime walk exactly.

## 2. Actual object hierarchy (OBSERVED FROM RUNTIME + SCRIPT/VALIDATOR)

The conceptual `lemma → meaning → pattern → complements/examples` model is confirmed as implemented, with `contentRefs` and `errorNotes` as additional pattern-level children:

```
lemma
├─ id, canonicalLemma, reflexive, aspect
└─ meanings[]
   ├─ id, glossesEn[]
   └─ patterns[]
      ├─ id, relationType, cefr{recognition, production?}, teachingStatus
      ├─ usage{priority, register, note?}, learnerExplanationEn
      ├─ activityEligibility[]
      ├─ complements[]  (type: case | preposition-case | infinitive | clause)
      ├─ examples[]  (id, pl, en, audioEligible)
      ├─ contentRefs[]  (kind, id, purpose)
      └─ errorNotes[]  (kind, incorrectForm, guidanceEn)
```

Optional runtime fields not currently exercised by any released record but structurally supported by both the JS loader (`pp-verb-patterns.js`) and the projector: lemma-level `displayLemma`, lemma-level `aspectPartnerIds[]`, pattern-level `aspectEquivalentPatternIds[]`.

### Per-object-type field table

| Object | Public runtime fields | Required? | Private-only editorial fields (never reach runtime) |
|---|---|---|---|
| Lemma | `id`, `canonicalLemma`, `reflexive`, `aspect`, `meanings` | all required; `displayLemma`, `aspectPartnerIds` optional | *(none beyond the public set — lemma has no private-only fields today)* |
| Meaning | `id`, `glossesEn[]`, `patterns` | all required | `key` (immutable authoring key), `internalScope` (sense-boundary note for authors) |
| Pattern | `id`, `relationType`, `complements[]`, `cefr`, `teachingStatus`, `usage`, `learnerExplanationEn`, `activityEligibility[]`; optional `examples[]`, `contentRefs[]`, `errorNotes[]`, `aspectEquivalentPatternIds[]` | `id`/`relationType`/`complements`/`cefr`/`teachingStatus`/`usage`/`learnerExplanationEn`/`activityEligibility` required | `key`, `evidence[]` (sourceId/sourceKind/locator/factType/checkedAt/note), `reviewState`, `reviewEvents[]`, `releaseMode` |
| Complement | `type`, `required`, `role`, plus type-specific `case` and/or `preposition` and/or `clauseKind`; optional `questionOverridePl[]` | varies by `type` (see §3) | none |
| Example | `id`, `pl`, `en`, `audioEligible` | all required | `key`, `origin` (original / repository-reuse / editorial-generated + provenance) |
| contentRef | `kind`, `id`, `purpose` | all required | none |
| errorNote | `kind`, `incorrectForm`, `guidanceEn` | all required | `evidenceRefs[]` (indices into the pattern's private `evidence[]`) |

`reflexive` is a redundant, mechanically-checked Boolean mirror of whether `canonicalLemma` contains lexical `się`/`sobie` — it is not an independent notion of reflexivity (confirmed in `reports/priority-7-stable-id-specification.md` §6 and enforced by the runtime/editorial validators).

### Complement types (locked, OBSERVED FROM SCRIPT/VALIDATOR: `priority7_tooling.py` `COMPLEMENT_TYPES`)

Exactly four, matching the frozen authoring rule in the task brief §6.1:

- `case` — requires `case`; forbids `preposition`, `clauseKind`. Direct Locative and Vocative are mechanically forbidden (`DIRECT_CASE_FORBIDDEN`).
- `preposition-case` — requires `preposition` + `case`; forbids `clauseKind`.
- `infinitive` — forbids `case`, `preposition`, `clauseKind`.
- `clause` — requires `clauseKind`; forbids `case`, `preposition`.

`clauseKind` is itself an enum, not free text: **`{"ze", "czy", "zeby", "interrogative"}`** (`priority7_tooling.py` `CLAUSE_KINDS`). This is a load-bearing fact for the Phase 3B compatibility assessment (§21.9 in the task, and see `priority-8-phase-4a1-phase3b-compatibility.md`): **there is no `direct-speech` value in this enum**, even though Phase 3 evidence explicitly lists "direct speech" as a verified alternative construction for 9 researched identities: **8 of the frozen 68 full-pattern lemmas** (`odpowiadać`, `czytać`, `pisać`, `napisać`, `powiedzieć`, `zgadzać się`, `polecać`, `radzić`) **plus 1 metadata-only verified aspect identity** (`przeczytać`, anchored by `czytać`, per the Phase 3B freeze — not itself one of the 68) (see `reports/priority-8-phase-3-batch-02.md`, `reports/priority-8-phase-3-batch-04.md`, `reports/priority-8-phase-3-batch-06.md`, `reports/priority-8-phase-3-batch-04-risk-review.md`, `reports/priority-8-phase-3-batch-06-risk-review.md`). No occurrence of `direct-speech` or `direct speech` exists anywhere in `priority7_tooling.py`, `pp-verb-patterns.js`, or any schema/spec JSON in the repository.

`ROLES` (OBSERVED FROM SCRIPT/VALIDATOR) is likewise a closed enum: `{subject, object, recipient, experiencer, predicate, content, topic, interlocutor, means, target}`.

### teachingStatus / CEFR / usage (OBSERVED FROM SCRIPT/VALIDATOR)

- `TEACHING_STATUSES = {"active-production", "recognition-only", "deferred"}`. Only the first two appear in the released runtime (41 / 4); `deferred` is a valid editorial state that never reaches runtime.
- `CEFR_LEVELS = ("A1", "A2", "B1", "above-b1")`; `cefr.recognition` required, `cefr.production` optional.
- `usage = {priority: core|common|limited, register: neutral|formal|informal, note?}`.

### contentRefs / errorNotes (OBSERVED FROM SCRIPT/VALIDATOR)

- `contentRefs[].kind ∈ {card, topic, drill, scenario}`; `purpose ∈ {support, practice, context, contrast}`; `id` is validated against a repository index and must resolve to an entity of the matching `kind` (`CONTENT_REF_DANGLING`, `CONTENT_REF_KIND`). contentRefs have no dedicated stable-ID namespace of their own — they point at IDs that belong to other systems (cards/topics/drills/scenarios), validated for resolution, not allocated here.
- `errorNotes[].kind ∈ {documented-common-error, predicted-distractor}`. errorNotes are anonymous nested objects with no ID of their own; in the private editorial record, `documented-common-error` entries require non-empty `evidenceRefs[]` (integer indices into the pattern's `evidence[]`), which are stripped before runtime projection.

## 3. Governance / policy fields

- **activityEligibility**: pattern-level array, allow-listed against `ACTIVITY_KEYS = {reference, search, grammar-choose, grammar-build, type-it, listening, mixed-quiz, case-mix, conversation}`. Mechanically gated: `recognition-only` forbids `grammar-build`/`type-it`; `deferred` forbids any eligibility; non-empty eligibility requires `reviewState == "approved"`. Currently **empty for all 45 released patterns** — no activity has ever been turned on for Verb Patterns, consistent with Priority 8 policy that no new activity is enabled in this phase.
- **audioEligible**: example-level Boolean. All 45 released examples are `true` as of `patternDataRevision` 2 (see §4). `pp_audio_rule.py`/`verify_audio.py` treat "every projected example with `audioEligible: true`" as the audio-inventory source of truth (`verb_pattern_audio_examples` in `pp_audio_rule.py`), independent of `activityEligibility` — this is the documented separation between pronunciation permission and activity/exercise permission, and it is what actually runs (`python3 verify_audio.py` reports `content/verb-patterns.json 45 phrases OK` with no reference to activity state).
- **patternDataRevision** = 2, **formatVersion** = 1. Documented meaning (`reports/priority-8-runtime-revision-options.md`, `reports/priority-7-frozen-data-and-persistence-specification.md` §3): revision 1 was the original 30/34/45/45 corpus; revision 2 is the same corpus with pronunciation-only audio eligibility authorized (Priority 8 Phase 1A, confirmed by `priority8_phase1_transition.py`, which asserts `runtime["patternDataRevision"] != 2` would be an error and requires exactly 45 audio-eligible examples with all `activityEligibility` empty). `formatVersion` changes only for incompatible data-contract semantics and has never moved from 1.

## 4. Source-of-truth summary

`content/verb-patterns.json` is **generated, not hand-authored**. See `priority-8-phase-4a1-runtime-pipeline-map.md` for the full traced pipeline. In summary: `editorial/verb-pattern-candidates.json` (private, 30 lemmas, identical IDs to runtime, richer fields per §2 above) is validated and passed through `priority7_tooling.freeze_editorial()` then `priority7_tooling.verified_runtime_from_frozen()` to produce the exact bytes committed at `content/verb-patterns.json`. This was confirmed both by static reading of `priority8_phase1_transition.py` (which performs and checks exactly this transform) and by running the actual validators read-only:

```
python3 priority7_tooling.py validate-editorial editorial/verb-pattern-candidates.json --context editorial/priority-7-authoring-context.json --repository-root .
→ Priority 7 private editorial record: valid   (exit 0)

python3 priority7_tooling.py validate-runtime content/verb-patterns.json --context editorial/priority-7-authoring-context.json --repository-root .
→ Priority 7 runtime projection: valid   (exit 0)
```

Both commands are read-only (no `--write`/output flag used); `git status --short` was empty before and after every command run in this audit.
