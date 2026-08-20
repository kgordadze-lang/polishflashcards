# Priority 8 Phase 0 — pronunciation and Listening product options

## Options

| Option | User value | Complexity/governance | Risk |
|---|---|---|---|
| A — pronunciation playback only | Immediate, contextual pronunciation for every approved example | Smallest UI/audio extension; audio suitability and product reapproval only | Low; no exercise semantics |
| B — playback plus Listening | Adds receptive practice | Requires activity eligibility, item design, distractors, sampler/feedback policy and broader tests | High scope coupling; approved sentence alone is not a deterministic Listening item |
| C — staged mixed policy | Broad approved playback first; later selective Listening | Two explicit gates and rollback boundaries | Lowest long-term coupling; requires the policy distinction to be documented and tested |

## Recommendation

Choose **Option C**, staged so Priority 8 Phase 1 implements pronunciation playback only for the already-approved 45 examples. Keep every `activityEligibility` array empty. Consider Listening later, pattern by pattern, after a separate product decision and deterministic item design.

The recommended invariant is:

- `audioEligible: true` = the exact approved example may use the shared pronunciation player and enter the audio build set;
- `activityEligibility:["listening"]` = the pattern may supply separately governed Listening items;
- the first does not imply the second;
- Listening requires both suitable eligible audio and a valid exercise item.

This refines the historical Priority 7 rule, which coupled audio to Listening because no reference-playback consumer existed. The new consumer must be explicitly approved; silent reinterpretation is not acceptable.

## Why playback first

Playback adds clear value without turning the reference into an activity, writing mastery, creating accepted-answer policy or exposing recognition-only content to production. The current player already handles switching, fallback, offline cache, Range, retry, speed and accessibility. The exact current audio workload is bounded at 20 reuses plus 25 new clips.

Listening adds semantic questions the sentence itself does not answer: target meaning, distractors, role/case focus, repeat policy, pool balance and whether recognition-only patterns yield fair questions. It also raises rollback and QA cost. Bundling it with 70 new lemmas would make failures difficult to isolate.

## Recognition and production

Pronunciation playback is permitted for active-production and recognition-only patterns after approval because it asks the learner to listen, not produce. Recognition-only remains labeled “Understand for now” and must not silently enter grammar-build, Type It or any productive pool. Do not automatically enable Type It at any stage.

## UI policy

Place one native button in the example block, adjacent to the Polish sentence but outside the text paragraph. Use the existing speaker icon plus a contextual accessible name (“Play example sentence: …”). One player owns all buttons; activating another cancels the first. Preserve focus, language tags, wrapping, 44px target, reduced motion and visible failure/retry. Loading should disable only eligible playback controls until manifest settlement; an unavailable manifest may use the existing device-voice fallback.

## Rollback

The Phase 1 rollback unit is the runtime eligibility projection, UI control path, manifest additions and 25 new hashed files. Existing 20 audio files are shared assets and must not be removed. Listening has a later, independent rollback unit because its allowlist/items do not need to ship with playback.
