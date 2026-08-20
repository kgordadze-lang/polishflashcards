# Priority 8 Phase 1A — service worker and offline behavior

No service-worker strategy or cache implementation changed. The shell marker advances to `popolsku-v67` because the learner-visible shell and helper changed; `popolsku-audio` remains versionless and persistent.

The runtime and audio manifest remain required precache assets and network-first at runtime. Content-hashed MP3s remain lazy/cache-first in `popolsku-audio` and are not added to the shell precache. A warmed clip remains available offline; an unwarmed offline clip reaches the existing device-voice fallback or visible retry state.

Range handling, response/MIME validation, canonical keys, partial-body refusal, FIFO ceiling 4,200/trim target 4,000, 64-entry one-shot quota recovery, and stale-entry eviction are unchanged. The final library of 3,402 remains below the retention ceiling. There is still no `skipWaiting()` or `clients.claim()`.

The existing worker suites plus the Phase 1A playback suite own the executable verification of network-first runtime/manifest, cache-first MP3s, warm Range 206, malformed/multiple/If-Range passthrough, 416 behavior, offline fallback, retention, quota recovery, and cache preservation.
