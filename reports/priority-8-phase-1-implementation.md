# Priority 8 Phase 1A — implementation

## Outcome

The local candidate extends the existing pronunciation architecture to Verb Patterns. The public derived view retains `audioEligible`; the existing lemma renderer conditionally adds one native `.mini-audio` button; and every activation routes through the existing `data-say` delegate and single `speakText()` owner.

The control uses the exact Polish example in its contextual accessible name, remains a native keyboard-operable button, has a 44 × 44 px target, exposes the shared playing state, and uses the existing MP3 → device voice → visible retry failure chain. Manifest loading disables only these eligible controls. Starting a new clip cancels the prior owner, and returning to the index or leaving Verb Patterns clears stale playback.

No second player, manifest, cache, normalizer, runtime parser, renderer, fallback, storage key, progress state, analytics, activity, learner-facing review UI, or expansion content was added.

## Content and runtime

`priority8_phase1_transition.py` reconstructs the authorized starting revision-1 frozen state from Git and advances it through `freeze_editorial(..., 2, previous=...)` and `verified_runtime_from_frozen(...)`. It is idempotent in check mode. The private context explicitly authorizes independent pronunciation, while the default/revision-1 policy stays fail-closed. The resulting runtime has `formatVersion: 1`, `patternDataRevision: 2`, and 45 `audioEligible: true` examples. Every `activityEligibility` array remains empty.

All example text, translation, provenance, stable IDs, lemma/meaning/pattern content, CEFR, teaching status, relations, content references, and error notes remain byte-equivalent to the baseline after the three Phase 1A review events and the eligibility Boolean are normalized out.

## Release markers

The learner-visible UI/helper change advances `APP_VERSION` from 8.11 to 8.12 and the numbered shell cache from `popolsku-v66` to `popolsku-v67`. `build_pages.py` regenerates the version-stamped pages and sitemap. `AUDIO_CACHE` remains `popolsku-audio`.
