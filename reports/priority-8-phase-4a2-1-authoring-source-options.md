# Priority 8 Phase 4A2-1 — Phase 4B Authoring Source

**Status:** OPTIONS AND RECOMMENDATION ONLY. No authoring artifact is created, and the editorial corpus is not touched, by this report. HUMAN DECISION REQUIRED before Phase 4B.

## 1. Current architecture

`editorial/verb-pattern-candidates.json` is the sole, canonical editorial source (current-model-audit §4, pipeline map §"What feeds the runtime"). It is:
- tracked, committed production Git history (not excluded, not staging);
- validated as a whole by `validate_editorial` on every check;
- the only input `freeze_editorial` / `verified_runtime_from_frozen` ever reads to produce `content/verb-patterns.json`.

Every object in it (lemma, meaning, pattern, example) has a **required** `id` field — there is no schema-legal way to represent a partially-drafted, not-yet-approved, not-yet-ID'd record inside this file today.

## 2. Why this matters for the 68

Combined with the Decision C recommendation (allocate no ID until a lemma's complete record is approved), the canonical editorial file **cannot** hold an in-progress draft of any of the 68, because `id` is mandatory on every object it contains. Authoring 68 lemmas' worth of meanings/patterns/examples is a multi-step drafting process (research → draft complements → draft examples → review → approval) that necessarily passes through incomplete, ID-less intermediate states. Something has to hold those intermediate states somewhere other than the canonical, freeze-path-validated file.

## 3. Options

### Option D1 — Direct append to `editorial/verb-pattern-candidates.json` in controlled batches
Add each lemma's record directly to the canonical file once fully drafted, in small batches, relying on `validate_editorial` to gate each commit.

- Reviewability: each batch is a diff against the single, large (currently 8772-line) canonical JSON file — reviewable, but batch diffs sit inside a file that also contains the live, released 30, raising the chance a reviewer's eye slips past an unrelated released record while reviewing new content.
- Risk of accidental governance advancement: **moderate** — because `id` is mandatory, this option forces IDs to exist for a lemma **before** its record is fully approved (an incomplete record cannot be represented in this file without one), which directly conflicts with the Decision C recommendation (no ID before full approval). Working around this by allocating IDs early for drafts effectively adopts something like Option C3 informally and by necessity, not by design — undermining the ID-lifecycle decision rather than implementing it cleanly.
- Stable-ID timing: forced early, as above — the weakest fit of the three options against the recommended C1 lifecycle.
- Batch review: possible, but batches are commits directly against the file the freeze pipeline reads, so a half-reviewed or partially-approved batch sitting in the canonical file for any length of time is one accidental `freeze_editorial`/projection run away from reaching runtime prematurely (nothing structurally prevents this beyond process discipline).
- Rollback: reverting a batch means reverting a change to the one file every validator and the freeze pipeline reads — safe if done immediately, but any interleaving with other legitimate edits to the same file (e.g. an unrelated correction to the released 30) makes a clean revert harder.
- Diff size: grows the single canonical file monotonically; per-batch diffs are moderate, but the file's total size and review surface grows continuously across all of Phase 4B with no natural checkpoint smaller than "everything committed so far."
- Compatibility with existing validators: fully compatible (this is exactly what the validators already expect) — but only for **complete, ID-bearing** records, which is the source of the ID-timing conflict above.

### Option D2 — Private Phase 4 staging file → reviewed → promoted into canonical corpus (RECOMMENDED)
Draft each lemma's record in a separate, non-canonical, non-frozen-path staging artifact (e.g. `editorial/phase4-staging-candidates.json` or similar, structurally similar to but explicitly not gated by `validate_editorial`/`freeze_editorial`). Once a lemma's full record (all meanings/patterns/examples) is complete and approved, IDs are allocated (Decision C, Option C1) and the complete, ID-bearing record is moved — promoted — into `editorial/verb-pattern-candidates.json` in one clean, small, self-contained commit.

- Reviewability: **best of the three** — a promotion commit is a small, self-contained addition of one complete lemma (or small batch of lemmas) to the canonical file, with nothing partial or unresolved inside it. The staging file's own diffs (draft edits, in-progress research notes) never need the same scrutiny as a promotion, since they cannot reach runtime by construction (staging is not read by any validator or freeze step).
- Risk of accidental governance advancement: **lowest** — the staging file is explicitly outside the pipeline the pipeline map traces (`editorial/verb-pattern-candidates.json` → `validate_editorial` → `freeze_editorial` → `verified_runtime_from_frozen` → `content/verb-patterns.json`); nothing in a staging file can reach the runtime file without the deliberate, human-reviewed promotion step.
- Stable-ID timing: **matches the Decision C recommendation exactly** — IDs are computed only at promotion time, once the record is fully approved, never before.
- Batch review: natural, per-lemma (or small-batch) promotion boundary; this is the cleanest match to "the exact Phase 4 editorial record is approved" (handoff constraint #12) as a discrete, reviewable event.
- Rollback: reverting a promotion commit is a clean, isolated revert of exactly one lemma's addition to the canonical file; the staging file is unaffected either way.
- Diff size: each promotion is small and self-contained; staging-file churn (drafts, revisions, abandoned attempts) never appears in the canonical file's history at all.
- Compatibility with existing validators: **full** — the canonical file is only ever touched with complete, valid, ID-bearing records, exactly as `validate_editorial`/`freeze_editorial` already expect; no validator behavior needs to change to support this workflow.
- Footprint: one new (private, non-runtime, non-validated-by-the-freeze-path) file; no code change to `priority7_tooling.py` or `pp-verb-patterns.js` is required to support the staging/promotion workflow itself (though the private-lexical-material checklist idea in the decision summary, if adopted, would live in this same staging file).

### Option D3 — Another mechanism (per-lemma fragment files + merge tooling)
Author each lemma as its own small JSON fragment file (e.g. `editorial/phase4-drafts/<lemma-slug>.json`), merged by new tooling into the canonical file at promotion time.

- Reviewability: potentially even more isolated per-lemma than D2 (one file per lemma rather than one shared staging file), but this benefit is marginal at 68 lemmas and comes at the cost of needing genuinely new merge tooling that does not exist today (no such merge script was found in this repository).
- Risk of accidental governance advancement: comparable to D2, provided the fragment directory is likewise outside the freeze pipeline's read path.
- Batch review / rollback / diff size: comparable to D2 for the promotion step, worse during drafting (68 separate files to keep track of vs. one staging file with 68 lemma entries).
- Compatibility with existing tooling: **requires new tooling to be built** (a merge/promotion script) that does not exist; D2 requires no new code at all, only a new data file and a manual (or lightly scripted) copy-in-whole-record promotion step.
- **Not recommended over D2** — D2 achieves the same isolation and safety properties without requiring new merge machinery to be designed, built, and itself reviewed before Phase 4B can even start.

## 4. Recommendation

**Recommend Option D2** — a private Phase 4 staging file, reviewed per-lemma, promoted into `editorial/verb-pattern-candidates.json` only once a lemma's complete record is approved and its IDs are allocated (per the Decision C recommendation). This is the option that most cleanly satisfies "smallest maintainable architecture" (no new tooling required, unlike D3) while giving the strongest isolation between in-progress drafting and the canonical, freeze-path-validated corpus (stronger than D1, which forces incomplete records — or premature IDs — into the same file every validator and the release pipeline reads).

## HUMAN DECISION REQUIRED

1. Approve Option D2 and name the staging artifact's exact path/filename.
2. Decide the promotion granularity: strictly one lemma per promotion commit, or small controlled batches (e.g. by Phase 3 verification-order grouping) — either is compatible with D2.
3. Decide whether the staging file should also carry the private, non-runtime lexical-material and narrowing-constraint checklist fields discussed in the decision summary, or whether those belong in a separate private artifact.
