# Priority 7 Phase 4F-F2 — Formal Human Product Approval

Baseline `cd0a3bf8a0003e81d405428dc039ec3f348cb8b5`
(tree `28ee6de0226ad48839212fca2ec1cd167e4fbfe7`).

This phase performed **no content review, no linguistic review and no release
action**. The substantive decision is the product owner's own: after visually
inspecting all 45 patterns in the real Priority 7 learner interface, the owner
returned a single explicit **`APPROVE ALL`** on 2026-08-17. Phase 4F-F2 records
that one human decision as the governance events the tooling requires, and
nothing else.

All 45 patterns move from `editorial-reviewed` to `approved`. Nothing was
frozen, released or projected to runtime.

## 1. The governance contract, as found

The stage was already defined in full. It was read out of `priority7_tooling.py`
before anything was written, and **the tooling was not changed**.

| Question | What the repository actually says |
|---|---|
| Chain for `solo-maintainer-reference-backed` | `SOLO_STAGE_KINDS` — `reference-verification` → `editorial-review` → **`product-approval`** |
| Who performs `product-approval` | A **human**. The stage appears in neither mode's `MODE_NONHUMAN_STAGE_KINDS`, so the event requires `reviewerRef` and is structurally incapable of naming a nonhuman `actorRef` |
| Where the approver lives | `reviewerRegistry` in the authoring context, resolved by `_validate_review_event`, which requires `human: true` |
| Required reviewer role | The stage name itself: `product-approval` |
| Extra requirement under the solo mode | The approver's record must list the mode in `acknowledgedReleaseModes`, or `OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED` |
| Corroboration | **Forbidden.** `corroboratingActorRefs` is tier-2-only (`EDITORIAL_CORROBORATION_FORBIDDEN`, plus `SCHEMA_UNKNOWN_FIELD`) |
| `supportingEvidenceDigests` | **Forbidden** — allowed only on an accepted tier-1 verification |
| `findings` | **Forbidden** — an editorial-tier field |
| Digest scope | `STAGE_SCOPE_TIER["product-approval"] == "product-approval"` — tier 3: the tier-2 projection **plus** `pattern.contentRefs`, sorted by `(kind, id, purpose)`. `scopeVersion` stays `1` |
| Required preceding state | `editorial-reviewed`, with tier 2 standing on the current digest (`REVIEW_STAGE_ORDER`) |
| Transition rule | `_derive_review_currency`: tier 3 becomes current only if tier 2 is current **and** the acceptance pins the current tier-3 digest. `_replay_review_order` additionally rejects a repeated acceptance of the same scope |
| One human for all 45? | Permitted. `ownerAllowsMultipleRoles` guards one reviewer performing **two stages**, not one stage across 45 rows. The owner performs exactly one stage, so it is deliberately absent |
| Approval date | `reviewedAt`, required, nondecreasing against prior events and not in the future |
| Fields the transition touches | `pattern.reviewEvents` (append) and `pattern.reviewState`. Both, or `REVIEW_STATE_MISMATCH` |

The architecture supported this phase without modification.
`priority7_tooling.py` is byte-identical to the baseline.

## 2. The blocker, and how it was cleared

At baseline the repository named **no product-approval authority at all**.
`reviewerRegistry` held exactly one human — AB (`native-reviewer-001`),
`native-linguistic` only — and `authorRegistry` was empty. Every candidate
attribution failed against the real validator:

| Attempt | Validator result |
|---|---|
| An unregistered `reviewerRef` | `REVIEWER_REGISTRY_DANGLING` |
| AB as the approver | `REVIEWER_ROLE` + `OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED` |
| A nonhuman actor via `reviewerRef` | `REVIEWER_REGISTRY_DANGLING` |
| A nonhuman actor via `actorRef` | `SCHEMA_REQUIRED` + `SCHEMA_UNKNOWN_FIELD` |
| A human record without `acknowledgedReleaseModes` | `OWNER_RELEASE_MODE_NOT_ACKNOWLEDGED` |

**No identity was invented.** The phase stopped before editing and asked for the
four things only the owner could supply: the registry key, the `human: true`
authorisation, the role grant, and the release-mode acknowledgement. The owner
then supplied all four explicitly, including the statement that they understand
the formal reference-verification and editorial-review tiers were nonhuman
workflows with no human external verification and no formal native-speaker
review advancing them, and the instruction that **no `correction` or `reopen`
authority be granted at this stage**.

## 3. The reviewer registered

One human record was added to `reviewerRegistry`.

```json
"product-owner-001": {
  "human": true,
  "roles": ["product-approval"],
  "acknowledgedReleaseModes": ["solo-maintainer-reference-backed"],
  "namedInPhase": "Priority 7 Phase 4F-F2"
}
```

- **`product-approval` and nothing else.** No `external-verification`, no
  `native-linguistic`, no `reference-verification`, and — as instructed — no
  `correction` and no `reopen`.
- **`ownerAllowsMultipleRoles` is deliberately absent**, because the owner
  performs exactly one release stage.
- **No personal identity was recorded.** No display name, no email, no contact
  detail, no organisation, no title. The registry blob contains none of `@`,
  `phone` or `address`, and the record claims no linguistic credential of any
  kind.
- **AB is unchanged**, has no new event and no new authority. AB is not the
  approver, and `native-reviewer-001` still appears nowhere in the corpus.
- **`authorRegistry` stays empty.** Product approval created no author, which
  is what still blocks the five accepted replacement sentences.
- **The four nonhuman actors are byte-identical** and none of them holds, or
  could hold, the `product-approval` role.

## 4. Events created

Exactly one `product-approval` acceptance per pattern — 45 in total.

```json
{
  "kind": "product-approval",
  "decision": "accept",
  "scopeVersion": 1,
  "scopeDigest": "<current tier-3 digest of this pattern>",
  "reviewerRef": "product-owner-001",
  "reviewedAt": "2026-08-17",
  "note": "Product owner approval after visual inspection of all 45 patterns in the Priority 7 learner interface: APPROVE ALL. Inclusion and usefulness decision on the recorded treatment; no new language review was performed."
}
```

Every row carries the same note because there was one decision, not 45. The
matrix records the same source for all 45 rows, and the owner is nowhere
described as having performed a new review of the Polish.

## 5. Counts

| | Before | After |
|---|---|---|
| Patterns | 45 | 45 |
| Examples | 29 | 29 |
| `reference-verification` acceptances | 47 | **47** |
| `editorial-review` acceptances | 45 | **45** |
| `product-approval` acceptances | 0 | **45** |
| `editorial-reviewed` states | 45 | 0 |
| `approved` states | 0 | **45** |
| Total review events | 92 | 137 |
| `activityEligibility` entries | 0 | **0** |
| Audio-eligible examples | 0 | **0** |

## 6. Digests

Every digest was recomputed with `review_scope_digest("product-approval", …)`
against the live row it sits on. None was copied or guessed.

- **45 / 45** recompute exactly.
- **45 distinct** digests — no two rows share one.
- The tier-3 digest **differs from the tier-2 digest on all 45 rows**, because
  every row carries `contentRefs` and those enter scope only at tier 3. The
  distinction is load-bearing, not cosmetic.
- **No tier-1 or tier-2 event was created, altered or invalidated.** The 47
  reference acceptances and 45 editorial acceptances stand byte-identical,
  including the two superseded `mówić` reference events.

The post-D3.1 / E1 content is therefore exactly what was approved.

## 7. Content immutability

Against the baseline, proven field by field:

- `lemma`, `meaning`, pattern text, IDs, `relationType`, `complements`, roles,
  `cefr`, `teachingStatus`, `activityEligibility`, `learnerExplanationEn`,
  `errorNotes`, `examples` and their IDs, keys and provenance, `evidence`,
  `contentRefs`, `repositorySource`, allocation and tombstones — **all
  identical**.
- The lemma envelope, the meaning envelope and the document envelope are
  identical.
- The Phase 4F-F2 normaliser reconstructs both files **byte for byte** back to
  the baseline blobs.
- The canonical file changed only in `reviewEvents` and `reviewState`.
- The authoring context changed only in `reviewerRegistry` and by an appended
  `contextNotice` paragraph, which supersedes exactly the three statements
  Phase 4F-F2 performed — that no product-approval authority is named, that no
  product-approval event exists, and that no pattern is approved — and leaves
  every other statement standing.

## 8. What `approved` does and does not mean

`approved` means: **the human product owner accepted the recorded treatment for
product inclusion**, under a release mode whose two lower tiers were performed
by nonhuman project workflows.

It does **not** mean human external verification, professional linguistic
review, or native-speaker review. The owner's decision is a usefulness and
inclusion judgement about learner-facing product content; it is **not a
language judgement** and claims none. No new source check and no new review of
the Polish was performed in this phase. AB's Phase 4C acceptance remains
supplementary evidence and advanced nothing on this chain.

Product approval is also **not release**. It unlocks the next decisions; it
makes none of them. Nothing was frozen, no runtime was projected, no release
data was created, `patternDataRevision` was not incremented, and `index.html`,
`sw.js`, `manifest.json`, `pp-verb-patterns.js`, the shipping data files and
the audio are byte-identical.

## 9. Historical suites

Recording tier 3 legitimately falsifies claims that earlier phases made about
the state of the corpus *at their own time*. The repository's established
mechanism for this is a phase-owned normaliser, and Phase 4F-F2 follows it
exactly.

`tests/priority7_phase4ff2_normalizer.py` reverts the 45 approvals and the one
reviewer record, keyed on a literal 45-identity allowlist and the complete
pinned event object. A duplicate acceptance, a repinned digest, a reworded
note, a later state or an edited owner record is **not** recognised, stays
visible, and still breaks the guard it was hidden behind.

It composes **outside** the Phase 4F-E1 normaliser, which is pinned to
`editorial-reviewed` and sees nothing until this layer is removed first:

```python
E1.without_phase_4fe1_editorial_review(
    F2.without_phase_4ff2_product_approval(live_corpus))
```

Fourteen historical suites were updated at that seam. A further **13 tests
across 8 suites** (3B is seam-only; 3C, 3F-A, 3D-1, 4E, 4F-A, 4F-C2, 4C and
5-A carry substantive edits) were phase-scoped rather than weakened: each made
a claim about which tiers had run, and each now stands over the normalised
view with a docstring recording that Phase 4F-F2 superseded it. What those
suites guard about **release** — zero eligibility, zero audio, no public
runtime, no human external verification, no native review, no `correction` or
`reopen` authority — stays asserted against the **live** files, because Phase
4F-F2 moved none of it.

Two are worth naming explicitly:

- Phase 4E's `test_the_later_stages_of_the_solo_chain_are_still_unperformed`
  was renamed to `test_the_solo_chain_never_borrows_human_chain_authority`. Its
  old name became false; what it permanently guards did not. It now also proves
  that where tier 3 has been performed it names a registered human and never a
  nonhuman actor.
- Phase 4C's `test_no_row_ever_claims_human_review_or_approval` was narrowed to
  the two states that claim a human checked the **Polish** —
  `externally-verified` and `native-reviewed`. Those have no authority to this
  day and stay refused live. The third, `approved`, was legitimately supplied.

No suite was weakened to make Phase 4F-F2 pass, and no assertion was deleted
without its guard being restated somewhere it still bites.

## 10. Validation

| Gate | Result |
|---|---|
| Phase 4F-F2 focused suite | **99 tests, OK** |
| Full Python suite | **1572 tests, OK** (1473 at baseline + 99 new) |
| JXA suites | **36 / 36** |
| `validate_content.py` | OK |
| `verify_audio.py` | OK — 3377 phrases verified |
| `build_pages.py --check` | committed output current |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | clean |

## 11. Limitations — read this before releasing

Everything in §9 of the Phase 4F-E1 summary still applies and is not softened
by this approval. The two lower tiers remain nonhuman. Reference-backed model
review can be wrong in ways a native speaker would catch immediately, and the
product owner's approval does not and cannot correct that: it is a decision
about whether to ship this material, made in explicit knowledge of what
assurance stands behind it.

Specifically still open:

- No `correction` and no `reopen` authority exists, by the owner's instruction.
  Nothing in the approved corpus can currently be changed through an authorised
  governance path; granting one of those roles is a separate owner decision.
- `authorRegistry` is still empty, so `origin.kind = "original"` remains
  unavailable and the five accepted replacement sentences still cannot enter
  the canonical corpus.
- No `external-verification` authority exists, so nothing here is
  human-verified against sources.
- The four subframe rows and the sense-selection questions on rows 1 and 36,
  flagged by Phase 4F-A, were not revisited here.

## 12. Verdict

**GO.**

The explicit human `APPROVE ALL` decision is truthfully recorded for exactly
all 45 editorial-reviewed patterns, under the governance contract the
repository already had and without changing it. All 45 are approved. The
approver is a real, registered, acknowledged human holding product authority
only; no nonhuman actor and no other person was represented as making this
decision. Historical evidence is intact — 47 reference acceptances and 45
editorial acceptances byte-identical — and zero learner-facing content changed.
Nothing was frozen, projected, released or pushed.
