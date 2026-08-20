# Priority 8 Phase 0 — service-worker implications

## Existing contract

The shell cache is `popolsku-v66`; audio uses the versionless `popolsku-audio`. The manifest and public Verb Patterns runtime are required precache assets and network-first at runtime, with cached offline fallback. Content-hashed MP3s are cache-first and are not precached.

The worker validates status, response type, redirect state and media type before every write and again on reads. It canonicalizes same-origin keys, ignores unknown/cross-origin/non-GET requests, and does not call `skipWaiting()` or `clients.claim()`.

## Future Phase 1 dependencies

A playback release would change:

- private editorial/frozen data and projected `content/verb-patterns.json`;
- `pp-verb-patterns.js` derived example view;
- `index.html` example control wiring/CSS only as needed;
- `pp_audio_rule.py`, generator/verifier/validators through the one shared discovery rule;
- `audio-manifest.json`;
- 25 new content-hashed MP3s;
- relevant tests/specifications.

Audio additions alone need only manifest publication and lazy `popolsku-audio` population; they do not require a shell-cache bump. However, the Phase 1 UI/helper code change is a shell asset change, so its release should bump the numbered shell cache (and the learner-visible app version under the project’s release policy) to stage a coherent control implementation. The public runtime remains network-first.

## Offline guarantee

- Shell/runtime/manifest: available offline after a successful worker install.
- MP3: available offline only after that exact clip has been warmed.
- Unwarmed or evicted clip offline: the network request fails; the shared device-voice fallback is attempted; if unavailable/failing, the existing visible retry status appears.
- No proposal should claim that all pronunciation is predownloaded.

## Range behavior

Warm validated clips support one byte range with a true 206, correct `Content-Range`, `Content-Length` and `Accept-Ranges`. Unsatisfiable valid ranges return 416. Multiple/malformed/If-Range requests pass through unchanged. Partial responses are never cached. New hashed clips inherit this path without worker logic changes.

## Capacity and quota

Current cache-policy ceiling is 4,200 and the library is 3,377, leaving 823 entries. Adding 25 current-example clips yields at most 3,402. The central expansion estimate adds about 65 net-new clips, yielding about 3,467; the high planning scenario of 80 yields about 3,482. Both retain substantial headroom.

Retention is FIFO, trims to 4,000 only after crossing 4,200, protects the just-written exact key and only deletes approved MP3 entries. A write failure triggers deletion of at most 64 approved entries and one retry. Do not misdescribe this as LRU or an exact byte quota.

## Staleness and release order

The content hash prevents a file at the same URL from changing text. The remaining stale risk is cross-asset skew: a runtime flag/control can arrive before its manifest entry, or an offline client can have the new runtime with an old manifest. The player safely falls back, but release verification should stage code/runtime/manifest/audio atomically at the deployment boundary and test old/new cached combinations.

No worker change, forced activation or cache-clearing feature is needed merely for additional pronunciation files.
