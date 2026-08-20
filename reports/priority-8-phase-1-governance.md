# Priority 8 Phase 1A — governance

The owner authorized the playback-only policy for the already-approved 45 examples. The policy is now explicit: `audioEligible` permits learner-initiated pronunciation of the exact approved example; it does not infer or authorize Listening, Type It, grammar practice, or any activity.

The Priority 7 specification files remain historical records of the revision-1 policy. Priority 8 revision 2 prospectively supersedes the former audio-implies-Listening policy: `audioEligible` now authorizes learner-initiated pronunciation only, while `activityEligibility` remains separately and explicitly governed. This is a Priority 8 policy amendment, not a rewrite of Priority 7 history.

Changing `audioEligible` moved the tier-2/product digests. The established event model requires a changes-requested event before a new editorial acceptance can follow the completed prior round, so each pattern received exactly three append-only events dated 2026-08-20:

1. nonhuman `editorial-review: changes-requested`, recording that the prior higher-tier acceptances became stale;
2. digest-bound nonhuman `editorial-review: accept`, narrowly accepting the eligibility policy without claiming human listening/native/linguistic review;
3. digest-bound human `product-approval: accept`, recording the owner's playback-only authorization and explicitly leaving the 25 clips pending human audio QA.

The private authoring context records the same limitations and sets `pronunciationPlaybackAuthorized: true`. The default validation context remains false, so revision-1/synthetic candidates do not silently inherit the exception; public/frozen validation permits pronunciation independent from Listening only at `patternDataRevision >= 2`. No reference-verification event was changed or fabricated because tier-1 content did not move. The official frozen transition verifies the append-only history, exact revision progression, public projection, and private/public boundary.

The generated clips have no governance field that can honestly be marked passed, and none was invented. The pending QA report/CSV is the handoff artifact. The local candidate is not authorized for integration or deployment until that external human action is complete.
