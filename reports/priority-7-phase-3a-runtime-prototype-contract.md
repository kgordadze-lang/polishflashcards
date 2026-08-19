# Priority 7 — Phase 3A Runtime and Non-Release Prototype Contract

**Phase:** 3A design only. **No runtime file was created.** `content/verb-patterns.json` does not
exist at this tree and must not exist until a release gate authorizes it.

This report defines the boundary a future browser consumer must respect, and the safest way for
Phase 3B to build and test UI **before** any linguistic release approval exists.

---

## 1. Three artifacts that are not equivalent

The single most important thing this report establishes is that the following are **three different
things**, with three different authorities, and that satisfying one proves nothing about the others.

| # | Artifact | What it proves | What it does **not** prove | Produced by |
|---|---|---|---|---|
| **1** | **Test / non-release fixture** | that the UI code runs against *a* document of the right shape | nothing about linguistics, nothing about approval, nothing about release | Phase 3B, from synthetic data |
| **2** | **Validated runtime shape** | the document is closed-schema, contains no private key, and (with context) resolves its refs and allocations | **not** active release membership — tombstoned allocations are deliberately retained | `validate_runtime(...)` |
| **3** | **Authorized frozen release** | the complete frozen transition validated: prior frozen state, allocations, active identity, tombstones, replacement rules, retained history, current approval, runtime parity, revision transition | — | `freeze_editorial(...).runtimeProjection` only |

The Phase 2A summary states this in the tooling's own terms: *"an allocation-only projection may
mechanically contain a historical tombstoned ID and remains explicitly nonrelease"*, and
*"Only complete frozen-envelope validation authorizes its exactly derived `runtimeProjection`."*

**`validate_runtime` passing is not release authorization.** Neither is
`project-fixture` succeeding. Neither is the file existing. Neither is the UI rendering it.

### 1.1 Two responsibilities, deliberately separated

The distinction that governs this whole report is a **separation of responsibility between two
different systems at two different times**, not a matter of how carefully either one is written.

#### Browser / runtime loader responsibility — *shape and safety, at load time*

The loader **may**, and must:

- accept **only** the expected public runtime shape (`{formatVersion, patternDataRevision, lemmas}`);
- **reject** private editorial and non-release envelope fields, at any depth
  (`artifactStatus`, `releaseAuthorized`, and every member of `PRIVATE_RUNTIME_KEYS`);
- **fail safely** when the data is unavailable, unreachable, malformed or partially invalid — the
  surface simply does not exist (§5.3);
- **expose no private provenance or review field** to the DOM, to any derived view, or to any
  future consumer.

The loader **must never be described, documented, commented, named or reasoned about as evidence
that a runtime artifact came from an authorized frozen release.** It cannot establish that, and no
amount of validation in the browser can. A well-formed, private-key-free, shape-valid document is
exactly what a *hand-edited file* also looks like. The loader's rejection of a bad document is
meaningful; its acceptance of a good-looking one proves only that the document looked right.

#### Release / build responsibility — *authority, before shipping*

Only the frozen/release validation machinery can establish:

- **active membership** — that an entity is currently live rather than a retained historical
  allocation;
- **tombstone validity** — that nothing was resurrected, reused, or silently disappeared;
- **review and release state** — that every included pattern is `approved` with current external,
  native and product scope digests;
- **an authorized frozen projection** — bytes exactly derivable from the frozen dimensions, with a
  valid `patternDataRevision` transition.

`freeze_editorial(...).runtimeProjection`, or `verified_runtime_from_frozen(...)` over an already
constructed frozen artifact, is **the authoritative release gate**. It runs in the build/release
workflow, on private inputs the browser never sees, and it is the only place any of the four
properties above can be decided.

#### The one-sentence form

> The loader decides whether a document is **safe to render**.
> The frozen release machinery decides whether a document is **allowed to exist in public**.
> Neither can answer the other's question, and neither substitutes for the other.

---

## 2. The boundary

```
   PRIVATE (never a browser resource, never in the public tree)
   ┌────────────────────────────────────────────────────────────────┐
   │  editorial/verb-pattern-candidates.json                        │
   │  editorial/priority-7-authoring-context.json                   │
   │    · internalScope, evidence, sourceId/locator/checkedAt       │
   │    · reviewState, reviewEvents, reviewerRef, scopeDigest       │
   │    · example origin, authorRef, repositorySource               │
   │    · source / reviewer / author / allocation registries        │
   └────────────────────────────┬───────────────────────────────────┘
                                │  freeze_editorial(...)      ← the ONLY release authority
                                ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  frozen artifact (private, non-production)                     │
   │    identity · structure · wording · policy · tombstones        │
   │    → .runtimeProjection  (exactly derivable, parity-checked)   │
   └────────────────────────────┬───────────────────────────────────┘
                                │  release gate (human, owner-approved)
                                ▼
   PUBLIC
   ┌────────────────────────────────────────────────────────────────┐
   │  content/verb-patterns.json   { formatVersion,                 │
   │                                 patternDataRevision, lemmas }  │
   └────────────────────────────┬───────────────────────────────────┘
                                │  fetch, network-first, fail-closed
                                ▼
   ┌────────────────────────────────────────────────────────────────┐
   │  pp-verb-patterns.js   →   UI (case metadata added here)       │
   └────────────────────────────────────────────────────────────────┘
```

The two names — `content/verb-patterns.json` and `pp-verb-patterns.js` — are **already locked** by
[`priority-7-frozen-data-and-persistence-specification.md`](priority-7-frozen-data-and-persistence-specification.md) §7.
Phase 3A does not rename them.

---

## 3. Forbidden in the browser, absolutely

### 3.1 Forbidden files

`editorial/verb-pattern-candidates.json` and `editorial/priority-7-authoring-context.json` must
never be:

- referenced by any `<script src>`, `fetch`, `import`, or link in `index.html`;
- listed in `REQUIRED_ASSETS`, `OPTIONAL_ASSETS`, `GENERATED_PAGE_ASSETS` or any derived path list
  in [`sw.js`](../sw.js);
- reachable by the `data-*.js` glob, the audio discovery walk, or `build_pages.py`;
- present in `sitemap.xml` or any generated page;
- copied, renamed, symlinked or inlined into any public artifact.

Directory naming is not a privacy control, and "the app doesn't load it" is not a privacy control.
The control is the test suite (§7).

### 3.2 Forbidden fields

`PRIVATE_RUNTIME_KEYS` ([`priority7_tooling.py:99`](../priority7_tooling.py#L99)) is the
authoritative list, and `_recursive_private_key_check` rejects any of them at any depth:

```
artifactStatus, specificationNotice, internalScope, key,
evidence, sourceId, sourceKind, locator, factType, checkedAt,
reviewState, reviewEvents, reviewerRef, reviewedAt,
scopeVersion, scopeDigest, supportingEvidenceDigests,
origin, authorRef, authoredAt, repositorySource, evidenceRefs,
sourceRegistry, reviewerRegistry, authorRegistry, editorialNotes
```

Note `key` in that list: the immutable authoring keys (`genitive-target`, `seek`, `assist`) are
**private**. They are readable, tempting, and forbidden as learner-facing labels. The UI derives its
labels from `complements` + central case metadata, never from `key`.

Also excluded from the projection by construction, not just by key-name: all `deferred`, `rejected`,
`research` and stale-digest candidates; example `origin` and `repositorySource`; every registry.

### 3.3 What the runtime document *does* contain

Per `_runtime_pattern` ([`priority7_tooling.py:2332`](../priority7_tooling.py#L2332)):

```
lemma    : id, canonicalLemma, reflexive, aspect,
           displayLemma?, aspectPartnerIds?, meanings[]
meaning  : id, glossesEn[], patterns[]
pattern  : id, relationType, complements[], cefr, teachingStatus, usage,
           learnerExplanationEn, activityEligibility[],
           aspectEquivalentPatternIds?, examples?, contentRefs?, errorNotes?
example  : id, pl, en, audioEligible
```

**It contains no case name, no Polish case name, and no diagnostic question.** Those are central
consumer metadata, derived in `pp-verb-patterns.js` from the table in
[`priority-7-phase-3a-ux-integration-architecture.md`](priority-7-phase-3a-ux-integration-architecture.md) §5.3.
This is by Phase 1 design and it is also a useful privacy property: the runtime file carries
structure, not prose about structure.

`relationType` **is** in the runtime document. It is a display *input* (it selects a wording
template) and never a display *output*.

---

## 4. Non-release prototype strategy for Phase 3B

### 4.1 Recommendation

> **Phase 3B builds and tests exclusively against an explicitly synthetic fixture that contains
> invented verbs, is generated by the existing `project-fixture` non-release path, lives only under
> `tests/`, and is never written to `content/`.**

Ranked against the alternatives:

| Option | Verdict |
|---|---|
| **Synthetic fixture, invented lemmas, `project-fixture` wrapper, under `tests/`** | **selected** |
| A small subset copied mechanically from the research corpus | **rejected** — see §4.3 |
| Serving the real research corpus behind a flag | **rejected outright** — this is the failure mode the whole boundary exists to prevent |
| Hand-writing a JSON literal in the test file | acceptable *in addition*, not instead: a hand-written literal can drift from the real shape, so it must be validated by `validate_runtime` in the same test |

### 4.2 Why synthetic, specifically

1. **The real corpus cannot produce a runtime document anyway.** Verified at this tree:
   `validate_editorial(corpus, committed_context)` returns **0 issues**, and
   `project_runtime_nonrelease(corpus, 1, context)` then raises
   `PROJECTION_EMPTY $.lemmas: No current approved active/recognition pattern can be projected.`
   All 45 patterns are `research`; the projector admits only `approved`. **There is no "just for
   testing" path through the real data — the tooling already refuses.**
2. **Phase 1 and Phase 2A already established the pattern.** The fictional `fikcjonować` family is
   the committed specification example, and Phase 2A's entire 76-test suite runs on in-memory
   fictional fixtures. Phase 3B continues an existing, reviewed practice rather than inventing one.
3. **A synthetic fixture can be adversarial in ways real data cannot.** It can carry a
   three-complement pattern, a clause complement, a Vocative, an aspect pair, a lemma with three
   meanings, a pattern with no example, a recognition-only pattern and a pattern with an empty
   `activityEligibility` — all in twelve records. The real corpus has none of some of these.
4. **It cannot be mistaken for content.** Invented verbs are self-evidently not Polish teaching
   material to anyone who opens the file, including a future reviewer who has lost this context.

### 4.3 Why not "a small subset copied mechanically from research"

Because it would require **flipping `reviewState` to `approved`** on real linguistic claims in order
to get them through the projector — which is exactly the act the entire review architecture exists
to prevent, and which zero humans have authorized. Even in a disposable workspace, a file on disk
containing real Polish government claims marked approved is a document that can be copied, quoted,
screenshotted or shipped by mistake. The synthetic route has no such artifact.

A secondary reason: a real subset would make the UI look finished. Reviewers seeing `szukać +
Genitive` rendering beautifully will read that as progress on the *linguistic* track. Seeing
`fikcjonować + Genitive` renders the same UI while making the phase status unmistakable.

### 4.4 Where fixture data lives

```
tests/fixtures/priority7/runtime-fixture.json        ← the non-release wrapper, committed
```

Notes:

- `tests/fixtures/priority7` is **already** a `PRIVATE_PATH_MARKER` in
  [`tests/test_priority7_phase2a.py:2980`](../tests/test_priority7_phase2a.py#L2980), asserted absent
  from `index.html`, `sw.js`, `sitemap.xml` and every generated page. Choosing this exact path means
  the guard that keeps it out of the browser **already exists and already passes**.
- It must live under `tests/`, never under `content/`, never at the repo root, never inside
  `grammar/`, `vocabulary/` or `guide/` (which `build_pages.py` owns and prunes).
- The generator command is the existing non-release CLI, run against a synthetic editorial document:
  `python3 priority7_tooling.py project-fixture …`. No new CLI is added, and specifically **no
  deployment or release command is created**.

### 4.5 The fixture's visible guard

`project_nonrelease_fixture` ([`priority7_tooling.py:2459`](../priority7_tooling.py#L2459)) already
wraps every projection:

```json
{
  "artifactStatus": "priority-7-runtime-projection-nonrelease-fixture",
  "releaseAuthorized": false,
  "runtimeProjection": { "formatVersion": 1, "patternDataRevision": 1, "lemmas": [ … ] }
}
```

**This wrapper is the guard, and it must remain unwrapped-by-the-loader.** Two contracts follow:

1. **The loader accepts only the bare runtime envelope** — an object whose keys are exactly
   `formatVersion`, `patternDataRevision`, `lemmas`. It must **reject** any document carrying
   `artifactStatus` or `releaseAuthorized`. Consequence: **the fixture file cannot be served to the
   browser at all**, because the shipping loader would refuse it.
2. Conversely, a document without the wrapper cannot be produced by `project-fixture`, so a bare
   runtime envelope in the tree is *itself* evidence that something bypassed the non-release path.

This is a deliberately awkward asymmetry, and the awkwardness is the point: the artifact the tests
use is structurally not the artifact the browser can load.

### 4.5a How the UI tests consume a fixture the shipping loader refuses

This is the mechanism that makes the asymmetry workable without weakening it.

**The unwrapping happens in the test harness, never in production code, and never in the file.**

```
tests/fixtures/priority7/runtime-fixture.json      ← wrapped; unloadable by design
        │
        │  read by the TEST HARNESS only
        ▼
  harness asserts:  artifactStatus === "priority-7-runtime-projection-nonrelease-fixture"
                    releaseAuthorized === false
        │
        │  harness reads .runtimeProjection  ← an explicit, deliberate, test-only step
        ▼
  PP_VERB_PATTERNS.__acceptForTest(projection)   ← test-only injection entry point
        │
        ▼
  the SAME derivation and rendering code the shipping loader feeds
```

Four properties make this safe:

1. **Production code never opens the fixture.** The shipping fetch path targets exactly
   `content/verb-patterns.json`. It has no branch, flag, query parameter, environment check or
   fallback that can reach a `tests/` path. There is no "test mode" in the shipping app.
2. **The unwrap is an assertion, not a convenience.** The harness must *verify* the wrapper's two
   fields before reading `runtimeProjection`. If the wrapper is absent or `releaseAuthorized` is
   anything other than `false`, the test **fails** rather than proceeding — so the harness cannot
   silently start consuming a bare or authorized-looking document.
3. **The injection entry point takes an already-unwrapped projection**, so it exercises exactly the
   code path the fetch path feeds. The tests therefore test the shipping derivation logic, not a
   parallel one. The entry point is named to be unmistakable (`__acceptForTest` or equivalent), is
   never called from `index.html`, and its absence from `index.html` is itself asserted by a
   source-level test.
4. **The refusal is tested from both sides.** One test feeds the *whole wrapped fixture* to the
   normal loader and asserts it is **rejected**; another feeds `fixture.runtimeProjection` through
   the injection point and asserts it renders. The two together prove the wrapper is load-bearing
   rather than decorative.

**Production code must never:**

- strip, delete, ignore, or default `releaseAuthorized: false`;
- read `runtimeProjection` out of a wrapper — that unwrap exists only in test code;
- convert, normalise, migrate or "adapt" a `project-fixture` envelope into a loadable document;
- accept a document because it *contains* a valid projection somewhere inside it;
- treat a passing fixture validation, a passing `validate_runtime`, or a rendering UI as evidence of
  release authorization.

**Preserved, and restated because this section is where it is most likely to erode:**
**test fixture ≠ validated runtime shape ≠ authorized frozen release.** The harness above touches
only the first two. The third is unreachable from any test, by construction, and that is the correct
design — a test suite that could produce a releasable artifact would be a test suite that could
release.

### 4.6 Non-visible guards

- The fixture's lemmas are invented (`fikcjonować` family or equivalent) and every gloss is
  obviously non-teaching.
- `patternDataRevision` in the fixture is `1` and carries no release meaning; the real revision
  begins only with the first released runtime projection.
- The fixture is regenerable: a test asserts it is byte-identical to a fresh `project-fixture` run
  over the committed synthetic editorial document, so it cannot be hand-edited into something else.

---

## 5. Loader contract (`pp-verb-patterns.js`, Phase 3B)

### 5.1 Shape

A fifth `pp-*.js` helper, matching the existing four: an IIFE exposing one global
(`PP_VERB_PATTERNS`), **pure with respect to the DOM and app state** so a JXA suite can drive it
directly, exactly as `tests/test_activities.js` drives `PP_USAGE`.

Responsibilities, and only these:

1. accept a parsed document and validate its envelope (fail closed);
2. build the derived views: sets by case, A–Z lemma list, `cardId → pattern[]` reverse index;
3. own the central case metadata (Polish name, English name, question derivation);
4. derive headline tokens, chip content and role phrases;
5. expose `eligibleFor(pattern, activity)` implementing the allowlist with a default-deny fallthrough.

It does **not** fetch, does **not** touch the DOM, does **not** read or write storage.

### 5.2 Validation the loader performs, in order

```
1. document is a non-null plain object                          → else unavailable
2. it has exactly {formatVersion, patternDataRevision, lemmas}   → else unavailable
   (presence of artifactStatus or releaseAuthorized → unavailable)
3. formatVersion === 1                                          → else unavailable
4. patternDataRevision is a positive integer                    → else unavailable
5. lemmas is a non-empty array                                  → else unavailable
6. every lemma/meaning/pattern has the required keys and closed
   enum values (case ids, complement types, relationType,
   teachingStatus, roles, activity keys)                        → else DROP that entity
7. no key from PRIVATE_RUNTIME_KEYS appears at any depth        → else unavailable
```

Steps 1–5 and 7 are **whole-document** failures: the surface does not exist. Step 6 is
**per-entity**: a malformed pattern is dropped and its siblings survive, an empty meaning is pruned,
an empty lemma is pruned. This mirrors the projector's own ancestor-pruning behaviour and prevents
one bad record from removing the whole feature.

Step 7 is a defence in depth. The projector already guarantees it; the loader re-checks because the
loader is the last thing before the DOM, and a private key reaching the browser is the one failure
that cannot be undone after shipping.

**What this sequence does and does not establish.** Passing all seven steps establishes that the
document is *shape-valid, private-key-free and safe to render* — nothing more. It does **not**
establish that the document was produced by `freeze_editorial`, that its entities are active rather
than tombstoned, that any pattern in it is `approved`, or that its `patternDataRevision` is a valid
transition from the previously released one. Those four are structurally invisible to the browser,
because the evidence for them lives in the private frozen artifact the browser never receives. Any
code comment, variable name, log message or future report that implies otherwise is a defect in its
own right and should be corrected on sight.

### 5.3 Fallback and failure behaviour

| Condition | Behaviour |
|---|---|
| File 404 / network failure / offline with no cache | `PP_VERB_PATTERNS.available === false`. The `Verb patterns` level is **never pushed** onto `LEVELS`. Home shows five grammar levels. Card backs show no pattern row. No error UI. |
| Malformed JSON | Same as above. The `JSON.parse` throw is caught and swallowed to a single `console.info`, matching the migration code's non-critical style ([`index.html:2005`](../index.html#L2005)). |
| Envelope rejected (steps 1–5, 7) | Same as above. |
| Some patterns dropped (step 6) | Surface exists with the survivors. A set that ends up empty is not created. |
| Loaded after `renderTopics()` has already run | Not permitted. The level must be pushed **before** the first `renderLevels()`/`renderTopics()`, so the fetch is awaited during startup or the file is loaded as a classic script. |

**On that last point:** the app has no async startup today; `LEVELS` is final before any render. Two
implementable options exist, and the choice belongs to Phase 3B:

- **(a) `fetch` + await before first render** — keeps `content/verb-patterns.json` as JSON (the
  locked name), matches the service worker's network-first data classification, but introduces the
  app's first asynchronous startup dependency and therefore a new failure mode on a cold offline
  start;
- **(b) load the projection as a classic script** that assigns a global, like the `data-*.js` files —
  no async startup, no new failure mode, but it changes the locked artifact from JSON to JS and
  would land inside the `data-*.js` glob unless carefully named.

**Recommendation: (a)**, because the locked specification says JSON and says *"A future loader reads
only `content/verb-patterns.json`"*, and because option (b) risks the audio/data discovery globs
that Phase 1 explicitly chose JSON to avoid. The cold-offline failure mode is acceptable precisely
because the fallback is "the feature is absent", not "the app is broken".

### 5.4 What the loader must never do

- Never accept a document with `releaseAuthorized` present at any value, or with `artifactStatus`
  present at any value.
- Never unwrap a `runtimeProjection` out of an envelope. That step exists in the test harness only
  (§4.5a).
- Never read `key`, `internalScope`, `reviewState` or any private field even if one appears —
  the presence of one is a whole-document rejection, not a field to skip.
- Never synthesize a pattern, an example, a question override, or an accepted answer.
- Never write to `localStorage`, `sessionStorage` or IndexedDB.
- Never treat `activityEligibility` as anything but an allowlist: unknown activity → `false`,
  missing array → `false`, non-array → `false`. This mirrors
  [`pp-usage.js:136`](../pp-usage.js#L136)'s existing fail-closed idiom.
- Never emit, log, expose or infer a claim about release authorization — including a
  "verified"/"released"/"authorized" flag, property or class name derived from a successful load.
  The loader has no vocabulary for that concept and must not acquire one.

---

## 6. Offline and cache implications (design only — nothing bumped in 3A)

Phase 3A bumps nothing. `APP_VERSION` stays `8.10`, `CACHE` stays `popolsku-v65`, `AUDIO_CACHE`
stays `popolsku-audio`, `schemaVersion` stays `2`, `CONTENT_MIGRATION_REVISION` stays `2`.

When a runtime file eventually ships, **all of the following must land in one atomic release**, per
[`priority-7-existing-content-integration-map.md`](priority-7-existing-content-integration-map.md) §7:

1. `content/verb-patterns.json` present;
2. `./pp-verb-patterns.js` and `./content/verb-patterns.json` added to `REQUIRED_ASSETS` in
   [`sw.js:81`](../sw.js#L81) — *required*, not optional, because a half-installed shell that
   renders the level and cannot load its data is worse than no level;
3. an explicit **network-first** branch for the JSON, alongside the existing `DATA_FILE` and
   `AUDIO_MANIFEST_PATH` branches, so a corpus update reaches learners without a shell bump;
4. `mediaGroupForPath` must classify `content/verb-patterns.json` as `json` — it already does, by
   extension ([`sw.js:304`](../sw.js#L304)) — so a `200 text/html` soft-404 cannot be stored under
   that key;
5. `STATIC_ASSET_PATHS` is *derived* from the precache list minus the data/manifest branches
   ([`sw.js:168`](../sw.js#L168)), so the new JSON must be excluded there too — a one-line filter
   change beside the existing `DATA_FILE` exclusion;
6. **shell cache bump** `popolsku-v65 → v66`, because the precache list changed;
7. `APP_VERSION` bump, because a deploy happened;
8. `tests/test_phase4b1_service_worker_cache.js` `A1 the app-shell cache is popolsku-v65` and
   `tests/test_phase4b2_offline_navigation_installability.js` updated in the same slice;
9. install-failure tests: the install must **fail atomically** when the pattern JSON cannot be
   stored, and the previous shell must survive.

`AUDIO_CACHE` is **not** renamed and **not** versioned — content-hashed clips are intentionally
retained across releases. No audio is added: zero examples carry `audioEligible: true` and none can
until a pattern gains `listening` eligibility.

`GENERATED_PAGE_ASSETS` and `sitemap.xml` are **untouched** — no static pattern pages exist in this
plan, so the 32-URL sitemap assertion stays valid.

---

## 7. Release guards and test expectations

### 7.1 Guards that already exist and already pass

`DeploymentIsolationTests` in [`tests/test_priority7_phase2a.py:2976`](../tests/test_priority7_phase2a.py#L2976):

| Test | Guarantees |
|---|---|
| `test_private_editorial_workspace_is_local_only_and_never_published` | `editorial/` holds exactly the two authorized files; `content/verb-patterns.json` absent; `tests/fixtures/priority7` absent |
| `test_fixture_cannot_enter_data_or_audio_discovery_globs` | the `data-*.js` glob is exactly the seven current files |
| `test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths` | no marker path and no `editorial/` prefix in `index.html`/`sw.js`/`sitemap.xml`/generated pages; the `<script src>` list is exactly eleven entries; sitemap has 32 URLs |
| `test_generator_outputs_remain_current_and_owned_directories_contain_no_fixture` | generated output has no drift and no fixture inside the owned directories |
| `test_protected_application_surface_matches_untouched_production_baseline` | `git diff` over 30 protected paths against `f6bdc73a…` is empty |

### 7.2 Guards that must be *deliberately amended* — and how

Phase 3B **will** break two of these, on purpose:

1. `test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths` asserts the script
   list is exactly eleven entries. Adding `pp-verb-patterns.js` makes it twelve.
2. `test_protected_application_surface_matches_untouched_production_baseline` diffs `index.html`
   against a fixed commit. Any app change fails it.

**The required discipline:** these amendments are the *approval gate itself*. In the slice that adds
the loader, each amendment must be a separate, reviewable edit whose diff shows exactly what was
allowed in and why. The two assertions must be **narrowed, not deleted** — the script list stays an
exact list (twelve named entries), and the protected-surface baseline moves to the new reviewed
commit rather than dropping `index.html` from the protected set.

`test_private_editorial_workspace_is_local_only_and_never_published` must be **strengthened**, not
weakened, when the fixture lands: `tests/fixtures/priority7` stops being asserted absent and starts
being asserted (a) present, (b) containing only the wrapped non-release fixture, and (c) still
absent from every public surface.

### 7.3 New tests Phase 3B must add

Python, in a new `tests/test_priority7_phase3b.py` (never by editing the 2A suite's own contracts):

1. the committed fixture is byte-identical to a fresh `project-fixture` run over the committed
   synthetic editorial document;
2. the fixture's outer object has `artifactStatus == "priority-7-runtime-projection-nonrelease-fixture"`
   and `releaseAuthorized == false`;
3. `validate_runtime(fixture["runtimeProjection"], ValidationContext())` returns **zero issues**;
4. the fixture contains no string matching any lemma in the real editorial corpus (a mechanical
   anti-leak assertion);
5. `content/verb-patterns.json` still does not exist;
6. the fixture path appears in no public surface — reuse the existing marker sweep.

JXA, in a new `tests/test_priority7_patterns_ui.js`, driving `pp-verb-patterns.js` directly:

7. **the harness contract, both directions (§4.5a):** feeding the *whole wrapped fixture* to the
   normal loader is **rejected**; feeding `fixture.runtimeProjection` through the test-only
   injection entry point renders; the harness itself fails if the wrapper's `artifactStatus` or
   `releaseAuthorized: false` is missing; and a source-level assertion proves the injection entry
   point is **not referenced anywhere in `index.html`**;
8. a document containing any `PRIVATE_RUNTIME_KEYS` member at any depth is rejected whole;
9. `formatVersion !== 1`, a non-positive revision, or an empty `lemmas` array → unavailable;
10. an unknown case id / complement type / relationType / role drops that pattern and keeps siblings;
11. `eligibleFor(pattern, "type-it")` is `false` for an empty allowlist, `false` for an unknown
    activity name, `false` for a non-array, and `false` for a `recognition-only` pattern requesting
    `grammar-build` or `type-it`;
12. question derivation is exact for all seven cases and for every preposition+case combination in
    the fixture;
13. the reverse card index yields the chip only for a card claimed by exactly one pattern, and the
    neutral doorway for a card claimed by two.

Progress negative-regression, in the same JXA suite or beside `tests/test_migration.js`:

14. snapshot `popolsku-progress-v2`; load the surface, open a set, open a lemma, expand, collapse,
    leave; assert the stored bytes are **byte-for-byte unchanged**;
15. assert no new `localStorage`/`sessionStorage` key beginning `pp-` or `popolsku-` exists;
16. assert `schemaVersion` is 2 and `CONTENT_MIGRATION_REVISION` is 2.

---

## 8. Public runtime expectations, once a release exists

These are the properties a released `content/verb-patterns.json` must have. They are stated now so
the release gate has a checklist and cannot be argued into existence later.

1. Produced **only** by `freeze_editorial(...).runtimeProjection`, or re-verified from a frozen
   artifact via `verified_runtime_from_frozen(...)`. Never by `project_runtime_nonrelease`, never by
   `project-fixture`, never by hand.
2. Envelope exactly `{formatVersion, patternDataRevision, lemmas}` — no wrapper, no status field.
3. `patternDataRevision` starts at 1 with the first release and increments only when the public
   payload bytes change. It is not `APP_VERSION`, not the shell cache, not `schemaVersion`, not
   `CONTENT_MIGRATION_REVISION`.
4. Contains only `approved` patterns whose `teachingStatus` is `active-production` or
   `recognition-only`, with current scope digests.
5. Contains no `PRIVATE_RUNTIME_KEYS` member at any depth.
6. Every `contentRef` resolves against the shipped repository content at the same release.
7. Every `audioEligible: true` example sits under a pattern with `listening` eligibility **and** has
   a corresponding manifest entry and MP3 — or `audioEligible` is false everywhere, which is the
   pilot's expected state.
8. Deploys atomically with its loader, its service-worker entries, its shell bump and its tests.

---

## 9. Explicit non-equivalences, restated

Because these are the errors most likely to be made under time pressure:

- *"`validate_runtime` passes"* ⇏ the data may ship.
- *"`project-fixture` produced a file"* ⇏ the data may ship.
- *"The file is in `content/`"* ⇏ it was released; it may simply have been written there wrongly.
- *"The UI renders it"* ⇏ anything about linguistic correctness.
- *"All 45 patterns validate cleanly"* ⇏ any of them is approved. Verified at this tree: the corpus
  validates with **0 issues** and is simultaneously **unprojectable**. Structural validity and
  release authorization are orthogonal, and this corpus is the proof.
- *"`project-fixture` is called `nonrelease`"* ⇏ the fixture is safe to serve; the loader must
  refuse the wrapper, and that refusal is the actual control.
- *"The loader rejected every private key and accepted the document"* ⇏ the document came from an
  authorized frozen release. The loader is a shape-and-safety gate at load time; release authority
  lives in `freeze_editorial` at build time, on inputs the browser never receives (§1.1).
- *"The UI tests pass against the fixture"* ⇏ the loader would accept that fixture. It would not —
  the tests reach the projection through an explicit test-only injection path, and one of the tests
  exists precisely to prove the loader refuses the wrapped file (§4.5a).
