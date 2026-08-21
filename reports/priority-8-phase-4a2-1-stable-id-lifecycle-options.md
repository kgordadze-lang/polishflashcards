# Priority 8 Phase 4A2-1 — Decision C: Stable-ID / Key Authoring Lifecycle

**Status:** OPTIONS AND RECOMMENDATION ONLY. No stable ID is allocated by this report. HUMAN DECISION REQUIRED before Phase 4B.

## 1. Current architecture (recap, with exact mechanics)

IDs are deterministic SHA-256 digests over already-known text, never a counter (`priority7_tooling.py` lines 396–448, `priority-7-stable-id-specification.md` §1–2):

```
allocate_lemma_id(canonical_lemma)                         → v1|lemma|<normalized-lemma>
allocate_meaning_id(lemma_id, canonical_lemma, meaning_key) → v1|meaning|<lemma_id>|<meaning_key>
allocate_pattern_id(meaning_id, canonical_lemma,
                     meaning_key, pattern_key)              → v1|pattern|<meaning_id>|<pattern_key>
allocate_example_id(pattern_id, example_key)                → v1|example|<pattern_id>|<example_key>
allocate_exercise_id(pattern_id, activity_type, item_key)   → v1|exercise|<pattern_id>|<activity_type>|<item_key>
```

Critically, **the lemma ID depends only on the normalized `canonicalLemma` text** — not on any `key`. Meaning/pattern/example/exercise IDs depend on the owning parent ID **and** an author-chosen `key` (`meaning_key`, `pattern_key`, `example_key`, `item_key`). This asymmetry is load-bearing for every question below.

A tombstone registry exists and is mechanically validated (`_validate_tombstone`, lines 4450–4507): retired entities are never deleted, never reused, and a retirement record must reference a real prior entity of the same kind/parent and only non-dangling, same-kind, already-allocated replacement IDs.

## 2. Why the current contract is ambiguous for Phase 4

Handoff global constraint #12 is a single, unqualified sentence: **"Allocate no stable ID until the exact Phase 4 editorial record is approved under the later ID policy."** Because the four ID kinds have different dependency structures (lemma IDs need only lemma text; meaning/pattern/example IDs additionally need author-chosen keys that don't exist until drafting happens), "the exact Phase 4 editorial record is approved" is open to at least two readings: does it mean *each entity, individually, once its own record is approved* (allowing early lemma-ID allocation, since lemma identity is already frozen text), or does it mean *the complete lemma+meaning+pattern+example record, as one unit, once fully approved*? The Phase 3B freeze itself never allocates an ID for any of the 68 — it freezes lemma *text*, not lemma *IDs* — so nothing in the freeze already answers this.

## 3. Options

### Option C1 — Allocate all IDs only after the complete record passes editorial approval (RECOMMENDED)
For a given lemma, no `allocate_*_id()` call is made for any of its lemma/meaning/pattern/example IDs until that lemma's full record (all its meanings, all their patterns, all their examples) has passed the same review-state gate the released 30 use (`reviewState` reaching an `approved`/reviewed state per `REVIEWED_STATES`).

- Matches handoff constraint #12 under its **strictest, most literal reading** — no stable ID exists anywhere (not even a lemma ID) before approval.
- Process cost: since allocation is a pure, cheap, deterministic function call, computing all IDs for one fully-drafted lemma at approval time is a single batch operation with no meaningful performance cost.
- Batch granularity: naturally per-lemma (matches Option D2's promotion unit in the authoring-source decision).
- Risk of hand-computed mismatch (4A-1 risk review §2): eliminated if IDs are only ever produced by calling the allocator functions at the single approval-time step, never earlier and never by inspection/copy-paste.

### Option C2 — Allocate lemma IDs at lemma-identity freeze; defer meaning/pattern/example IDs until their own approval
Since lemma IDs depend only on `canonicalLemma` text (already frozen by Phase 3B for all 68), lemma IDs could in principle be computed now, immediately, with zero risk of ever changing (barring the very rare post-release-correction path in `priority-7-stable-id-specification.md` §4, which does not apply pre-release).

- Textually **riskier** against constraint #12: the handoff's wording does not carve out lemma IDs as a special case, and reading it that way is a plausible-but-not-certain interpretation, not a stated exception. Per this task's recommendation standard (§13 — "do not recommend a workaround that falsifies the Phase 3B freeze"), this audit treats the literal, unqualified reading of #12 as authoritative and does **not** recommend C2 unless the human reviewer explicitly rules that "lemma identity freeze" satisfies "the exact Phase 4 editorial record is approved" for the lemma family specifically.
- Would reduce churn only marginally: lemma-ID computation is already nearly free under C1 (it happens at the same approval step as the other three ID kinds), so C2's main advantage — being able to name a lemma by its future ID before its content is drafted — has limited practical value and a real governance-reading risk.
- **Not recommended**, given the stricter reading is safer and no meaningful practical benefit is given up.

### Option C3 — Allocate deterministic IDs during drafting as provisional; never publish/freeze until approval
Compute IDs early (during drafting) purely as scratch/internal values in a non-canonical, non-frozen staging location, explicitly marked non-final, and only "promote" them (i.e., commit them into `editorial/verb-pattern-candidates.json`) once approved.

- Because allocation is a pure deterministic hash, a "provisional" ID and a "final" ID for the same (lemma, key) pair are **bit-for-bit identical values** — "provisional vs. final" is a **process/location** distinction (is it in the frozen, validated canonical file yet?), not a different ID variant. This means C3 is not actually a different *technical* mechanism from C1/C2; it is a *staging discipline* question, which this report treats as part of the Phase 4B authoring-source decision (see `priority-8-phase-4a2-1-authoring-source-options.md`, Option D2) rather than a genuinely distinct ID-lifecycle option.
- Risk: if "provisional" IDs are computed by hand or cached anywhere outside the staging artifact, they can leak into commits, reviews, or reports before approval, creating exactly the false impression of an approved allocation the freeze is trying to prevent. This is a discipline/tooling risk, not a hash-collision risk.
- **Recommended only as an implementation detail of C1**, not as an alternative to it: a staging file may contain deterministically-precomputed candidate IDs for internal consistency-checking during drafting (e.g., to catch a duplicate `pattern_key` early), provided those values are never written into `editorial/verb-pattern-candidates.json`, never referenced by a tombstone, and never treated as final until the same approval gate C1 requires is passed.

## 4. Key-naming / identity-significance questions (task §6)

- **Are keys identity inputs?** **Yes**, for meaning/pattern/example/exercise. `meaning_key`, `pattern_key`, `example_key`, and `item_key` are concatenated directly into the SHA-256 seed string (`v1|meaning|<lemma_id>|<meaning_key>`, etc.) — a changed key produces a different digest and therefore a different ID. Lemma `key`-equivalent input is only the canonical lemma text itself; there is no separate lemma-level `key` field in the schema (`current-model-audit` §2 field table: lemma has no private-only fields at all, hence no `key`).
- **Are keys merely readable editorial handles?** No — this is a common misreading the stable-ID spec explicitly corrects (`priority-7-stable-id-specification.md` §2: "the digest, not the readable stem, provides collision resistance"). The *readable stem* built from the key is for debugging only; the *key's presence in the seed* is load-bearing for uniqueness and stability. Both things are true at once: keys are human-readable **and** identity-significant.
- **Can changing a key after ID allocation change the deterministic ID?** Yes, trivially, if recomputed — which is exactly why keys are "unique among siblings and frozen after ID allocation" (`priority-7-stable-id-specification.md` §3) and why a released ID is validated against its frozen allocation record post-release, not recomputed live (§4). Changing a key after release does not change the *already-frozen* ID (frozen IDs aren't live hashes), but it does mean any *new* computation from the changed key would silently produce a different digest — which is precisely the failure mode `key`-immutability-after-allocation exists to prevent.
- **Which key components participate in allocation?** `meaning_key` (meaning seed and pattern seed indirectly via `meaning_id`), `pattern_key` (pattern seed), `example_key` (example seed), `activity_type`+`item_key` (exercise seed, unused today). `canonicalLemma` text participates in the lemma seed and in every readable-stem slug, but is not itself called a "key" in the schema.
- **Can the 68 keep their Phase 3 verification order separately from key names?** **Yes, and they must.** The stable-ID spec is explicit that "IDs never depend on array position" (§1) and keys "describe durable semantic/structural identity, not mutable display copy" (§3) — verification order (1–16, 18–70 per the handoff) is a *provenance/traceability* fact belonging in governance documents (this freeze, the handoff, the batch reports), never in a `key` string or an array position. `key` values should be chosen for durable semantic meaning (e.g. `seek`, `genitive-target`, matching the existing 30's convention observed in `editorial/verb-pattern-candidates.json`), independent of any ordinal.
- **Should verification order ever become part of an ID or key?** **No.** Embedding order in a key would violate the explicit "never depend on array position" principle in spirit (an order number is exactly the kind of extrinsic, reorderable fact IDs are designed to be independent of), and would create a spurious identity change if a future audit ever re-sequences or renumbers the verification record without any actual linguistic change.
- **What should happen if a meaning is split before approval?** Per the ID-change matrix (`priority-7-stable-id-specification.md` §4: "New meaning boundary, repurposed meaning, different participant structure → no; create and retire"), this only applies **post-release**. Pre-approval (which, per Option C1, means pre-allocation entirely), a split meaning simply becomes two draft `meaning_key` candidates with no ID yet allocated for either — there is nothing to retire, because nothing was ever frozen. This is exactly why C1 (defer all allocation until full-record approval) avoids an entire class of pre-release churn that C2/C3-as-independent-options would risk.
- **What should happen if a pattern is rejected before ID allocation?** Nothing to tombstone — under C1 it never had an ID. It is simply dropped from the staging artifact (or marked `rejected` per `REVIEW_STATES`, which already includes `"rejected"` as a legal editorial-only state) and never promoted into the canonical file.
- **What happens if an already allocated/released record is later retired?** The existing, fully-specified tombstone mechanism applies unchanged (`_validate_tombstone`; §5 above) — this is unaffected by any of the C1/C2/C3 choice, since it only ever governs *post-release* retirement of *already-allocated* IDs. Phase 4 as currently scoped only adds lemmas and retires none of the released 30 or any of the frozen 68, so this mechanism is expected to remain unexercised through Phase 4B, consistent with the 4A-1 risk review's finding (§4–5) that it is "sound but untested against real data."

## 5. Recommendation

**Recommend Option C1**: allocate no ID of any kind (lemma, meaning, pattern, example) for any of the 68 until that lemma's complete record has passed the same approval gate the released 30 use. Treat C3's "provisional ID" idea as a permitted *internal staging convenience* under C1, never as an independent lifecycle. Do not adopt C2 without an explicit human ruling that lemma-identity freeze satisfies handoff constraint #12 for the lemma-ID family specifically — this audit does not make that ruling itself, per the instruction not to recommend a workaround that falsifies the Phase 3B freeze.

## HUMAN DECISION REQUIRED

1. Approve Option C1 as the ID-allocation lifecycle for the 68 (and the 2 metadata-only identities receive **no** lemma ID at all under the Decision A recommendation).
2. Rule on whether lemma IDs may be allocated earlier than meaning/pattern/example IDs (Option C2) — default is no, absent this ruling.
3. Approve the key-naming convention for the 68's `meaning_key`/`pattern_key`/`example_key` values (durable semantic identity, independent of verification order — see §4 above).
4. Confirm whether Phase 4B tooling should compute-and-discard provisional IDs during drafting for early duplicate-key detection (Option C3-as-staging-convenience) or defer all computation to the single approval-time step.
