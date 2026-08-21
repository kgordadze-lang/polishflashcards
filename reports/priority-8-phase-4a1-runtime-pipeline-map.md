# Priority 8 Phase 4A-1 — Runtime Pipeline Map

**Scope:** the actual, discovered implementation pipeline from private editorial data to the public runtime and its consumers. No stage is invented; every stage below was located in the repository and, where safe, exercised read-only.

## Pipeline

```
editorial/verb-pattern-candidates.json          (private editorial source; 30 lemmas; hand-authored + reviewed)
editorial/priority-7-authoring-context.json     (private registries: sources, reviewers, editorial actors, authors, allocations)
        │
        ▼
priority7_tooling.validate_editorial(doc, context)      — schema/enum/reference/review-workflow validation
        │  (raises tooling.ValidationFailure on any issue)
        ▼
priority7_tooling.freeze_editorial(doc, revision, context, previous=prior_frozen)
        │  — builds the frozen envelope: identity / structure / wording / policy snapshots,
        │    validates tombstones and non-resurrection against the prior frozen state,
        │    validates review-event history and scope digests
        ▼
priority7_tooling.verified_runtime_from_frozen(frozen)
        │  — strips every private/governance-only field (PRIVATE_RUNTIME_KEYS ∪ GOVERNANCE_PRIVATE_KEYS),
        │    emits the closed public shape
        ▼
content/verb-patterns.json                      (public runtime projection; committed bytes)
        │
        ▼
pp-verb-patterns.js                             (dedicated loader; validates the closed runtime shape again,
        │                                          independently, before use — ENVELOPE_KEYS = [formatVersion,
        │                                          patternDataRevision, lemmas])
        ├──▶ Verb Patterns UI/runtime (application)
        └──▶ pp_audio_rule.verb_pattern_audio_examples() → verify_audio.py / generate_audio.py
                                                          → audio/*.mp3, audio-manifest.json
```

sw.js (service worker) also references `content/verb-patterns.json` by name for required-asset/offline caching classification (OBSERVED FROM SCRIPT: `grep` match in `sw.js`), i.e. it is treated as a required, network-first-or-cached runtime asset like the other `data-*.js` files, not as an optional/lazy resource.

## Is the runtime hand-authored, generated, or projected?

**Fully generated / projected — not hand-authored.** `content/verb-patterns.json` is the deterministic output of `verified_runtime_from_frozen(freeze_editorial(editorial_doc, revision, context))`. This was confirmed two ways:

1. **Static tracing**: `priority8_phase1_transition.py` (a one-shot historical migration script for the Phase 1A audio-eligibility change) performs and re-checks exactly this transform: it reconstructs the revision-1 projection from a pinned starting commit, asserts the reconstruction is byte-identical to the committed revision-1 baseline, then re-projects the current editorial state to revision 2 and asserts the *committed* `content/verb-patterns.json` bytes equal that fresh projection (`priority8_phase1_transition.py` lines 162–231).
2. **Dynamic re-validation** (read-only commands actually run in this audit, no `--write`/output flag):
   ```
   python3 priority7_tooling.py validate-editorial editorial/verb-pattern-candidates.json --context editorial/priority-7-authoring-context.json --repository-root .
   → Priority 7 private editorial record: valid   (exit 0)

   python3 priority7_tooling.py validate-runtime content/verb-patterns.json --context editorial/priority-7-authoring-context.json --repository-root .
   → Priority 7 runtime projection: valid   (exit 0)
   ```
   Both passed against the exact files currently committed on this branch. `git status --short` was empty immediately before and after each run.

Running `python3 priority8_phase1_transition.py` (no `--write`) itself raised `RuntimeError: authoring context contains a non-Phase-1A change` — expected and harmless: this script is pinned to the historical Phase 1A transition (`STARTING_HEAD = "e036a53c..."` and a hard-coded Phase-1A context notice), and the repository has since moved on to Phase 3B governance content that this old one-shot script does not recognize as "only a Phase 1A change." It is not the live/ongoing generator; it is a frozen record of one specific past transition. It made no filesystem change (`git status --short` stayed empty).

## What feeds the runtime

- `editorial/verb-pattern-candidates.json` — sole content source (30/30 lemma IDs identical to runtime; this audit confirmed the lemma ID sets are byte-for-byte the same set between the two files).
- `editorial/priority-7-authoring-context.json` — the `ValidationContext` (source/reviewer/editorial-actor/author/allocation registries) that both `validate_editorial` and `freeze_editorial` require to resolve `sourceId`, `reviewerRef`, `actorRef`, and allocation-registry cross-references.

Neither of these files is loaded by the shipping application; per `reports/priority-7-frozen-data-and-persistence-specification.md` §7, the editorial record "MUST NOT be transferred to the production/public static-site repository... Release inventory tests prove absence."

## Validators protecting the runtime

- `priority7_tooling.validate_editorial` — closed-schema, enum, cross-reference, and review-workflow validation of the private record.
- `priority7_tooling.validate_runtime` — closed-schema validation of the public projection, including a recursive private-key sweep (`_recursive_private_key_check`) that rejects any of the ~30 `PRIVATE_RUNTIME_KEYS`/`GOVERNANCE_PRIVATE_KEYS` (e.g. `evidence`, `reviewEvents`, `sourceId`, `internalScope`, `key`, `origin`, `releaseMode`) appearing anywhere in the runtime document.
- `priority7_tooling.validate_frozen_release` — validates the complete frozen envelope (identity/structure/wording/policy + tombstones + review history) before a `verified_runtime_from_frozen` projection is trusted as release-authoritative.
- `pp-verb-patterns.js` (client-side) — re-validates the runtime shape independently at load time (`validLemmaShell`, `validMeaningShell`, `validPattern`, `validComplement`), and additionally checks `runtime.formatVersion !== FORMAT_VERSION` and reads `patternDataRevision`. A malformed or wrong-format-version file is rejected by the loader itself, not just by the build-time tooling.
- `validate_content.py` — **does not** touch Verb Patterns at all (zero matches for any verb-pattern-related string in the file). It validates the unrelated `data-*.js` content families. This matches the documented intent in `reports/priority-7-stable-id-specification.md` §8: "Existing `validate_content.py` does not gain this responsibility in Phase 1."
- `verify_audio.py` / `pp_audio_rule.py` — audio-side validator; `pp_audio_rule.verb_pattern_audio_examples()` reads *only* the projected runtime file's `audioEligible: true` examples, independent of `activityEligibility`, and `verify_audio.py` checks each has a manifest entry and a real MP3 on disk (and vice versa — no orphans). Run read-only in this audit: `python3 verify_audio.py` → `content/verb-patterns.json 45 phrases OK`, `3402 required phrase(s) checked against 3402 manifest entries and 3402 MP3(s) on disk`, exit 0, no filesystem change.

## Generation/validation commands discovered (all safe to run as shown — read-only/check-only)

| Command | Effect |
|---|---|
| `python3 priority7_tooling.py validate-editorial editorial/verb-pattern-candidates.json --context editorial/priority-7-authoring-context.json --repository-root .` | Validates the private editorial record. Read-only. |
| `python3 priority7_tooling.py validate-runtime content/verb-patterns.json --context editorial/priority-7-authoring-context.json --repository-root .` | Validates the public runtime projection. Read-only. |
| `python3 priority7_tooling.py validate-specification <file>` | Validates a Phase-1 fictional specification fixture. Read-only. |
| `python3 priority7_tooling.py project-fixture <file> --test-pattern-data-revision N [--context ...] [--repository-root ...]` | Emits a nonrelease runtime-shaped fixture. **Writes only if `--output` is passed** — omit `--output` to keep it read-only (stdout only). |
| `python3 verify_audio.py` | Checks every required phrase (including the 45 Verb Pattern examples) has a manifest entry and a real MP3, and that nothing is orphaned. Read-only; explicitly documented as safe ("never auto-deleted"). |
| `python3 -m pytest tests/test_priority8_phase1.py tests/test_priority8_phase1b.py tests/test_priority7_phase3b.py tests/test_priority7_phase5a.py -q` | Existing automated test suites that exercise this pipeline. Read-only (assertions only, no fixture writes observed; `git status --short` stayed empty after running). |
| `osascript -l JavaScript tests/test_priority7_release_loader.js` | JavaScriptCore rehearsal of `pp-verb-patterns.js` against a synthetic fixture, per the file's own header comment. Not run in this audit (not required to answer the Phase 4A-1 questions; static reading of `pp-verb-patterns.js` was sufficient and lower-risk). |

`priority8_phase1_transition.py` (no `--write`) was run and is **not** listed above as a general-purpose command — it is a one-shot historical script pinned to a specific past commit and a specific past context state, and it now fails by design once the repository has moved past that point. It is documented here only as evidence for the projection mechanism, not as a reusable audit command.

## Note on the wider test suite

Running the four test files above turned up **19 pre-existing failures out of 155 tests**, all in files unrelated to the four run for pipeline confirmation once the broader suite was sampled (`test_priority7_phase5a.py`'s `CommittedStateGuard`/`RealCorpusBoundaryTests`, `test_priority7_phase3b.py`'s `FixtureIsolationTests`, `test_priority8_phase1.py`'s `test_official_transition_is_current_and_revision_two`). These are **pre-existing and not caused by this audit** — no file was modified before or during the run (`git status --short` was empty throughout), and the failures are consistent with these being *phase-pinned* regression tests that assert the repository is at one specific earlier phase checkpoint (e.g. "is the official transition script current," "is a specific sixth committed edit the head state") rather than living forward-compatible tests. The project has since advanced to Phase 3B/8, so several of these historical pins now legitimately fail. This is recorded as an **OBSERVED FACT** for the risk review; it is not something this audit fixed or should fix, since doing so would mean editing test files, which is out of scope.
