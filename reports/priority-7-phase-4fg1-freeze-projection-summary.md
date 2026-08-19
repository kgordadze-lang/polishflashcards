# Priority 7 — Phase 4F-G1: Approval-Gated Freeze and Public Runtime Projection

**Status: NO-GO on materialising the public runtime artifact.**
The freeze itself succeeded, cleanly and with zero tooling change. What could
not be done in this phase is putting the resulting document in the tree.

| | |
|---|---|
| Baseline commit | `3fd3355c263f91abc4b9bc0e5aa9050a1f3a4f4a` |
| Baseline tree | `3cb8ec017a7df54890ecda7128801731d3cc1176` |
| Canonical corpus SHA-256 | `cbd416a4f81757a39cf9418ba954e4947e333b96700d2ff52f5246e5460299d3` |
| Authoring-context SHA-256 | `807eaa7aa9917b4786495ebf959fdf1bd365f4fcf41f81a1832c7e71ebfcf6ce` |
| Approved patterns frozen | 45 / 45 |
| Freeze function | `priority7_tooling.freeze_editorial(document, 1, context)` |
| Projection function | `priority7_tooling.verified_runtime_from_frozen(frozen)` |
| `formatVersion` | 1 |
| `patternDataRevision` | 1 (mechanically determined) |
| Runtime SHA-256 | `4a42cd6a15b5a52246484aa82bbbf214b3525b88ea11756b0fac937793606671` |
| Pattern-ID-set digest | `be25c5cc78a9a42e0868aef0829c270bb0f42806f1397ae1f08f5639b4372d7d` |
| Private-key leakage | 0 |
| Sensitive-value leakage | 0 |
| Canonical SHA after freeze | unchanged |
| Authoring-context SHA after freeze | unchanged |
| Public artifact `content/verb-patterns.json` | **not created — see §3** |

---

## 1. Architecture found

Reconstructed from `priority7_tooling.py`, the Priority 7 suites,
`pp-verb-patterns.js`, and the two locking specifications.

### 1.1 Three artifacts, three authorities

| Artifact | Produced by | Authority |
|---|---|---|
| Non-release preview fixture | `project_runtime_nonrelease` / `project-fixture` | none — carries `artifactStatus` and `releaseAuthorized: false` |
| Validated runtime shape | `validate_runtime(...)` | closed schema + privacy only; **not** release membership |
| Authorised frozen release | `freeze_editorial(...)` → `.runtimeProjection` | the only release authority |

### 1.2 Answers to the fourteen inspection questions

1. **Preconditions.** Every pattern's `reviewState` must equal the state its
   own append-only event history and current scope digests still support
   (`_derive_review_currency`); the editorial record must validate whole;
   allocations must hash back to their seeds; and, for a first release, no
   prior frozen baseline may be asserted.
2. **Responsible function.** `freeze_editorial()` (`priority7_tooling.py:4532`).
   There is **no CLI subcommand for freeze** — the CLI exposes only
   `validate-specification`, `validate-editorial`, `validate-runtime` and
   `project-fixture`. Freeze is a library call, by design: the module states it
   "never writes a production asset."
3. **Mutation.** Freeze mutates nothing. It is a pure function returning a new
   frozen envelope. The editorial canonical file is untouched.
4. **Official runtime artifact path.** `content/verb-patterns.json` — locked by
   `priority-7-frozen-data-and-persistence-specification.md` §7 and restated by
   `priority-7-phase-3a-runtime-prototype-contract.md` §2. It does not exist at
   baseline and every phase so far has asserted its absence.
5. **Runtime schema.** A closed public envelope of exactly three keys:
   `formatVersion`, `patternDataRevision`, `lemmas`. The shipping loader
   declares the identical `ENVELOPE_KEYS` and refuses anything else whole.
6. **`patternDataRevision` meaning.** The public payload's generation counter.
   It is explicitly *not* `APP_VERSION`, not the shell cache, not
   `schemaVersion`, not `CONTENT_MIGRATION_REVISION`.
7. **Revision selection.** Fully mechanical. With `previous is None`,
   `freeze_editorial` admits **only** revision 1 (`FROZEN_INITIAL_REVISION`).
   On a later advance it computes `previous + 1` if and only if the public
   payload bytes changed, else it requires the same revision
   (`FROZEN_REVISION_TRANSITION`).
8. **Where the revision is stored.** Only inside the runtime document and its
   parent frozen envelope. Nothing in `index.html` or `sw.js` names it.
9. **Validation rules.** `validate_runtime()` for shape and privacy;
   `validate_frozen_release()` for the whole envelope, including
   `FROZEN_RUNTIME_PARITY` — the projection must be *exactly derivable* from
   the four closed frozen dimensions.
10. **Atomicity.** Freeze and projection are one operation:
    `freeze_editorial` computes the projection internally and embeds it;
    `verified_runtime_from_frozen` re-validates the whole envelope before
    returning a copy. There is no way to obtain the release projection without
    the full frozen validation passing.
11. **Review state after freeze.** Unchanged — `approved` stays `approved`.
12. **Freeze metadata in the private record.** None. This contract records
    freeze state nowhere but the frozen envelope.
13. **Boundary tests.** `test_priority7_phase2a.py::DeploymentIsolationTests`,
    `test_priority7_phase3fa.py` (release-bundle atomicity),
    `test_priority7_phase5a.py` (working-tree ownership + freeze semantics),
    `test_priority7_phase5a_bridge.js` E1–E3.
14. **Does the projector handle all 45 unmodified?** **Yes.** Zero changes to
    `priority7_tooling.py`.

---

## 2. Freeze preconditions — all proved independently

| Precondition | Result |
|---|---|
| Patterns | 45 |
| `reviewState = approved` | 45 / 45 |
| Reference-verification acceptances | 47 |
| Editorial-review acceptances | 45 |
| Product-approval acceptances | 45 |
| Exactly one current product approval per pattern | yes (min 1, max 1) |
| Approver | `product-owner-001` on all 45; `reviewerRef` borne, `actorRef` refused |
| Owner valid under contract | human, `roles = ["product-approval"]`, acknowledges `solo-maintainer-reference-backed` |
| Tier-1/2/3 digest currency | all 45 derive to `approved` via `_frozen_expected_review_state` |
| Correction / reopen activity | none — event kinds are exactly the three stages, all `accept` |
| Rows blocking freeze | 0; `_admitted_frozen_pattern_ids` returns 45 |
| `validate_editorial` | 0 issues |

Derived release authorisation, computed not asserted:

```
releaseModes                : ["solo-maintainer-reference-backed"]
humanVerifiedPatternIds     : []
humanNativeReviewedPatternIds : []
```

Both human-coverage lists are empty, and that emptiness is the honest
statement: no human external verification and no human native review is being
claimed for this release.

---

## 3. Revision decision — none required

`patternDataRevision = 1`, and it was **not chosen**. No prior frozen baseline
exists anywhere in the repository, so `previous is None`, and
`freeze_editorial` rejects every other value:

| Attempt | Result |
|---|---|
| revision 1 | accepted |
| revision 2 | `FROZEN_INITIAL_REVISION` |
| revision 0 / −1 | `FROZEN_REVISION` |

No human release decision is outstanding on the revision.

---

## 4. Official freeze and projection

```python
frozen  = priority7_tooling.freeze_editorial(corpus, 1, context)
runtime = priority7_tooling.verified_runtime_from_frozen(frozen)
```

`context` is `_load_context("editorial/priority-7-authoring-context.json",
repository_root=".")`. No lower-level helper was called; the F1 preview path
(`project_runtime_nonrelease` / `project-fixture`) was **not** used, and its
wrapper is refused by the release gate (`SCHEMA_UNKNOWN_FIELD`). Nothing was
hand-assembled.

`validate_frozen_release(frozen)` → 0 issues.
`validate_runtime(runtime, ...)` → 0 issues, with and without the frozen
allocation registry.

---

## 5. Public runtime contract

Top level is exactly `{formatVersion, patternDataRevision, lemmas}` — no
wrapper, no status field, no governance metadata. The complete key vocabulary
at every depth is 37 public names:

```
activityEligibility, aspect, audioEligible, canonicalLemma, case, cefr,
clauseKind, complements, contentRefs, en, errorNotes, examples, formatVersion,
glossesEn, guidanceEn, id, incorrectForm, kind, learnerExplanationEn, lemmas,
meanings, patternDataRevision, patterns, pl, preposition, priority, production,
purpose, recognition, reflexive, register, relationType, required, role,
teachingStatus, type, usage
```

The Python `PRIVATE_RUNTIME_KEYS` set and the loader's `PRIVATE_KEYS` rejection
list were re-checked against each other and still agree exactly.

---

## 6. Private → public leakage audit

| Check | Result |
|---|---|
| `FORBIDDEN_RUNTIME_KEYS` members at any depth | **0** |
| `product-owner-001` | absent |
| `priority7-reference-analysis` | absent |
| `priority7-editorial-review` | absent |
| `priority7-editorial-corroboration` | absent |
| `priority7-example-generation` | absent |
| `native-reviewer-001` | absent |
| Any identifier from any of the five registries | absent (10 checked) |
| `sha256:` digest tokens | 0 |
| ISO date tokens | 0 |
| `evidence`, `reviewEvents`, `origin`, `findings`, `actorRef`, `scopeDigest`, `editorialNotes` | absent |
| Example provenance | absent — example keys are exactly `id`, `pl`, `en`, `audioEligible` |

**Value-level audit.** Every string of ≥8 characters living under a
private-keyed subtree of the editorial record was collected and intersected
with every string in the projection. 14 pairs overlap. All 14 are repository
**content identifiers** — card, topic and drill IDs that appear privately in
`origin.repositorySource` and publicly in the runtime's `contentRefs`, which
the contract explicitly carries. Every one of them already ships publicly in
`data-*.js`. **Genuine value-level leakage: 0.**

Negative control: a private value hidden under a public key
(`learnerExplanationEn`) is caught by the same sweep, so the sweep has teeth.

---

## 7. Content correspondence

| Measure | Canonical | Runtime |
|---|---|---|
| Lemmas | 30 | **30** |
| Meanings | 34 | **34** |
| Patterns | 45 | **45** |
| Examples | 29 | **29** |
| contentRefs | 101 | **101** |
| errorNotes | 24 | **24** |

- Missing pattern IDs: **0**. Extra pattern IDs: **0**.
- Pattern-ID-set digest: `be25c5cc78a9a42e0868aef0829c270bb0f42806f1397ae1f08f5639b4372d7d`
- Lemma-ID-set digest: `323b26bfd579c48c4c2a6cca00d664468ec64defba71146ffff93c73bbea0ca2`
- A field-by-field learner view (lemma/meaning/pattern hierarchy, canonical
  lemma, reflexive, aspect, glosses, relationType, complements, CEFR,
  teachingStatus, usage, learner explanation, activity eligibility, error
  notes, example IDs and example text) is **identical** on both sides.
- `teachingStatus`: 41 `active-production`, 4 `recognition-only` — carried, not
  promoted.
- No synthetic fixture row reached the projection (`quuxify`, `zorbulate`,
  `TEST-ONLY`, `vp-x-` all absent).

---

## 8. Approval did not change eligibility

- `activityEligibility` is `[]` on all 45. No `grammar-build`, `type-it`,
  `listening`, audio or production practice was invented.
- `audioEligible: true` examples: **0**. The string does not occur in the
  artifact.
- Controls: an eligibility expansion in the source is refused
  (`REVIEW_STATE_MISMATCH`), newly enabled audio is refused
  (`AUDIO_NOT_AUTHORIZED`), and an expansion smuggled directly into the
  projection breaks `FROZEN_RUNTIME_PARITY`.

---

## 9. Source immutability

Freeze mutated nothing.

- `editorial/verb-pattern-candidates.json` — byte-identical to the baseline
  commit, SHA-256 unchanged.
- `editorial/priority-7-authoring-context.json` — byte-identical, SHA-256
  unchanged.
- All 45 rows remain `approved` after freeze.
- Retained governance history in the frozen envelope equals the corpus event
  arrays verbatim, all 47 + 45 + 45 events.
- No freeze/release vocabulary entered the private record.
- 20 shipping files byte-identical to the baseline commit, including
  `index.html`, `sw.js`, `manifest.json`, `pp-verb-patterns.js` and
  `priority7_tooling.py`.

---

## 10. Why the public artifact was not materialised

This is the one part of the phase that could not be delivered, and the reason
is the repository's own contract rather than caution.

`content/verb-patterns.json` is the locked path. Its **existence in the tree is
defined as release intent**, and release intent triggers a bundle requirement
that this phase was explicitly scoped to exclude. Writing the real projection
to that path and running the existing suites produces:

```
tests/test_priority7_phase3fa.py
  test_future_activation_is_guarded_as_one_atomic_dependency_bundle
    loader activation missing
    runtime path missing from application
    helper missing from required precache
    runtime missing from required precache
    APP_VERSION did not advance
    shell cache generation did not advance
  test_real_corpus_remains_unreleased_below_editorial_review        FAIL

tests/test_priority7_phase2a.py::DeploymentIsolationTests           FAIL
tests/test_priority7_phase5a.py                                     4 failures
  ("no shipping file may be modified: ['content/']")
tests/test_priority7_phase5a_bridge.js                              E1, E2 FAIL
```

Four independent guards, in four suites, agree. The Phase 3F-A guard is not a
historical leftover — its name states a forward-looking rule: *the dormant path
may not be activated one file at a time*. The frozen-data specification §7 says
the same in prose: the runtime snapshot, consumer adapters, service-worker
classification and shell cache update **deploy atomically**. Phase 5-A
independently restricts the working tree to `tests/` and `reports/`.

Making the artifact land would therefore require either bumping `APP_VERSION`
and the shell cache and wiring the loader — all four forbidden by this phase's
scope — or normalising away a guard whose entire purpose is to prevent
undeclared release mutations. The brief forbids that too: a G1 normaliser must
be "unable to hide arbitrary future release/runtime mutations", and this one
would hide precisely those.

So the projection was produced, verified, audited and **pinned by digest**, and
the file was not written. Because no shipping file was created, **no historical
suite needed repair and no normaliser was written.**

The future release slice must reproduce exactly:

```
sha256  4a42cd6a15b5a52246484aa82bbbf214b3525b88ea11756b0fac937793606671
bytes   86619
serialisation  json.dumps(runtime, ensure_ascii=False, indent=2,
                          sort_keys=False) + "\n"
```

---

## 11. Determinism

Three independent freezes from the same committed source at revision 1 produced
one SHA-256 and one pattern-ID set. No timestamp, ISO datetime, `generatedAt`,
`frozenAt` or random identifier appears in the artifact. Lemma, meaning and
pattern arrays are sorted by ID at every level, so ordering cannot drift.

---

## 12. File footprint

| File | Change |
|---|---|
| `tests/test_priority7_phase4fg1.py` | created (75 tests) |
| `reports/priority-7-phase-4fg1-freeze-projection-summary.md` | created |
| `reports/priority-7-phase-4fg1-freeze-manifest.json` | created |

Nothing else. No shipping file, no tooling file, no editorial file, no
`content/` directory. `priority7_tooling.py` is byte-identical.

---

## 13. Validation

| Gate | Result |
|---|---|
| Phase 4F-G1 focused suite | **75 tests, OK** |
| Full Python discovery | **1647 tests, OK** (1572 at baseline + 75 new) |
| JXA suites | **36 / 36** |
| `validate_content.py` | OK |
| `verify_audio.py` | OK — 3377 phrases verified |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `priority7_tooling.py validate-editorial` | valid |
| `priority7_tooling.py validate-runtime` (official CLI, with and without repository context) | **valid** |
| `git diff --check` | clean |

Focused suites re-run individually, all OK: F2, E1, D1, D2, D3.1, C2D, C2C,
C2B, C2, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 3B, 3C, 2A.

`tests/test_priority7_phase4fc1c.py` reports 5 errors when invoked
directly as a standalone module (`ModuleNotFoundError:
test_priority7_phase4fb3b`). This is the known pre-existing direct-import
defect, it predates this phase, and full discovery — which is the gate — is
green. It was not opportunistically fixed.

**Reproducibility.** The projection was regenerated in an isolated temporary
clone of the baseline, in the committed state, and produced byte-identical
output: same SHA-256, same byte length, same pattern-ID-set digest. Three
in-process regenerations agree with both.

**Committed-state proof.** A fresh zero-remote scratch was created from
`3fd3355c…`, the candidate applied and committed as its direct first
descendant (parent verified, tree clean, zero remotes, exactly three files
changed, no shipping file touched). Full Python (1647 OK), all 36 JXA suites,
every validator and `git diff --check` were re-run green in that committed
state, and the runtime projection stayed byte-identical. The scratch was then
deleted; the real workspace remains uncommitted at the baseline.

---

## 14. What is still not done

- The public artifact `content/verb-patterns.json` does not exist.
- No app loader wiring; `loadRuntimeDocument` stays dormant.
- No service-worker `REQUIRED_ASSETS` or network-first branch.
- `APP_VERSION` stays `8.10`; shell cache stays `popolsku-v65`.
- No real-device or product QA of the runtime path.
- No release candidate, no transfer to production, no push.

The next phase is the atomic release slice, and it owns all six at once.
