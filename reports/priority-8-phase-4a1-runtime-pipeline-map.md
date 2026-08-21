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

### Correction: production repository vs. static-host exposure vs. runtime payload

This audit's original text stated the two editorial files are "not transferred to the production/public static-site repository" and that "release inventory tests prove absence." That statement was too broad and conflicts with this repository's own tracked history. Three separate concepts must be distinguished:

1. **Production Git repository.** This repository is (or is a checkout of) the actual `popolsku.app` production source: `CNAME` contains `popolsku.app` and `sitemap.xml` lists live `https://popolsku.app/...` URLs. Both editorial files are **tracked, committed paths in this repository's own git history** — `git ls-files editorial/` lists both, `.gitignore` contains no rule excluding `editorial/`, and `git log --diff-filter=A -- editorial/verb-pattern-candidates.json` shows both files were added in commit `2bf4d09505866c9a47ecfa0f6634d6f05352f679`, whose message is literally `release: activate Priority 7 verb patterns`. **The two editorial files are part of the tracked production Git history, not excluded from it.**
2. **Deployed/static-host file exposure.** Whether a live deployed host actually serves the raw `/editorial/*.json` paths to a browser depends on hosting/deployment configuration (e.g. whether GitHub Pages serves the full repository tree or only a filtered build output) — this audit performed no deployment or network research and **does not know, and does not claim, either way** whether these paths are reachable on the deployed site.
3. **Public Verb-Pattern runtime payload.** This remains as originally established and is unaffected by (1)/(2): the Verb Patterns browser/runtime path (`pp-verb-patterns.js`) only ever fetches `content/verb-patterns.json`; it never loads either editorial file; and every private/governance field (`evidence`, `reviewEvents`, `internalScope`, `key`, `origin`, `releaseMode`, etc.) is stripped by the projector and mechanically rejected if present by `validate_runtime`'s `_recursive_private_key_check`.

The "MUST NOT be transferred... release inventory tests prove absence" line is a **historical specification statement** from `reports/priority-7-frozen-data-and-persistence-specification.md` §7 (a Phase-1 planning document), not an observation of current repository state — the repository's actual history shows the opposite happened for the git tree specifically (the files were transferred/committed as part of the Phase 7 release-activation commit). The "release inventory" tests this audit found (`tests/test_priority7_phase4fi1.py::PhaseFootprintTests::test_no_editorial_path_is_in_the_footprint`) check something narrower than "absence from the repository": they check that a specific *release commit's own diff* ("footprint") does not itself add or touch an `editorial/`-prefixed path — not that `editorial/` is absent from the tree, and not anything about what a deployed host serves.

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

## Note on the wider test suite (corrected)

Command actually run, verbatim, and re-run again during the Phase 4A-1 correction pass with an identical result:

```
python3 -m pytest tests/test_priority8_phase1.py tests/test_priority8_phase1b.py tests/test_priority7_phase3b.py tests/test_priority7_phase5a.py -q
```

**Totals: 136 passed, 19 failed, 155 total.** `git status --short` was empty before and after both runs — no file was modified before, during, or by this command.

The original wording ("19 pre-existing failures... all in files unrelated to the four run") was self-contradictory, since the failures occur inside three of the four files that were actually run, and is corrected below.

**Failures occurred within the selected historical phase-pinned suites**, by file:

| File | Failed | Passed |
|---|---|---|
| `tests/test_priority8_phase1.py` | 1 | (remainder) |
| `tests/test_priority8_phase1b.py` | 0 | all |
| `tests/test_priority7_phase3b.py` | 5 | (remainder) |
| `tests/test_priority7_phase5a.py` | 13 | (remainder) |

Reason categories, by exact assertion/error text observed in the run:

1. **Pinned Phase 4F-I1 activation-layer bundle state (8 of 19 failures).** `tests/priority7_phase4fi1_normalizer.py:397` raises `AssertionError: the Phase 4F-I1 activation layer is present on some but not all of the runtime document, index.html and sw.js, or the runtime bytes are not the pinned I1 release; the bundle is incomplete and must not be normalised away`. These tests require index.html/sw.js/runtime bytes to jointly match one specific pinned historical release combination; this checkout does not currently match that exact combination.
2. **A pinned historical commit SHA does not contain the expected path in this checkout's history (7 of 19 failures).** `git show 7beb50d7b3463d7745352f1608f1e30019529fdf:editorial/verb-pattern-candidates.json` (invoked by the test helpers) fails with `fatal: path 'editorial/verb-pattern-candidates.json' exists on disk, but not in '7beb50d7b3463d7745352f1608f1e30019529fdf'` — the referenced commit exists in this repository, but the test's assumption about what that specific historical commit contains does not hold in this checkout.
3. **Cascading count/set-membership assertions stemming from the same two root causes (3 of 19 failures)** — `AssertionError: Items in the second set but not the first` (×2) and `AssertionError: 0 != 45` (×1), each occurring in tests downstream of the pinned-baseline comparisons in categories 1–2.
4. **The Phase-1A transition script rejects the current, later authoring-context state (1 of 19 failures)** — `tests/test_priority8_phase1.py::Priority8Phase1GovernanceTests::test_official_transition_is_current_and_revision_two` invokes `priority8_phase1_transition.py` as a subprocess and asserts its exit code is 0; it returns 1 with `RuntimeError: authoring context contains a non-Phase-1A change`, matching this audit's own direct run of that script (see above).

The defensible statement is: **these failures exist on the untouched Phase 4A-1 starting baseline and were not caused by this reports-only audit** — not that they are "pre-existing" merely because the working tree was clean (clean-tree is necessary evidence that nothing here caused them, but the failures' actual cause, established above, is that several tests pin exact historical commit SHAs and an exact release-bundle state that this checkout does not currently match). No test file was read for the purpose of editing, and none was modified.
