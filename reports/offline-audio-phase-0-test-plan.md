# Offline Pronunciation Download — deterministic and iPhone test plan

## Existing coverage inventory

The repository already contains executable coverage relevant to the integration boundary:

| Area | Principal tests | Current evidence |
|---|---|---|
| Service-worker classification, canonical keys, cache writes, named reads, MIME validation, invalid eviction | `tests/test_phase4b1_service_worker_cache.js` | detailed fake worker/cache/network harness; some historical release-lock assertions require scoped execution/update in implementation phase |
| Offline navigation/installability | `tests/test_phase4b2_offline_navigation_installability.js` | explicit route inventory, install state, cache boundaries |
| Range, retention, quota, arbitrary eviction, persistence API, offline audio | `tests/test_phase4b3_audio_resilience_range_storage.js` | 558 behavior assertions passed in this audit; 5 historical version/count locks failed |
| Manifest load and playback fallback | `tests/test_audio_fallback.js` | 585/585 passed |
| Inline audio failure, Retry, focus, stale callbacks | `tests/test_audio_failure_inline_feedback.js` | 38/38 passed |
| Audio discovery/manifest/file integrity | `tests/test_priority8_phase1.py`, `tests/test_priority8_phase4e1_audio_generation.py`, `verify_audio.py` | current 3,621 reconciliation passes; one historical `APP_VERSION 8.13` lock fails |
| Verb Patterns pronunciation integration | `tests/test_priority8_phase1_playback.js` | control/fallback/cache/Range boundaries |
| Accessibility and navigation | `tests/test_phase1a_accessibility.js`, `test_phase1b_keyboard_focus.js`, `test_phase2c_navigation.js`, `test_phase3b_*`, `test_listening_accessibility.js`, `test_conversation_accessibility.js`, `test_mixed_accessibility.js` | existing native controls, screen routing/focus, live regions, reduced motion, mobile layout |

There is no current deterministic suite for a whole-library downloader, cache reconciliation against a changing manifest, pause/resume, worker messaging, or Remove. Phase 1 should add a focused fake Cache Storage/worker/message harness rather than drive 3,621 real network requests.

## Harness design

Run shipping/extracted Phase 1 worker and engine code against deterministic fakes:

- manifest factory with small unique content-hashed URL sets plus one exact 3,621 fixture derived from the committed manifest;
- insertion-ordered named Cache Storage with exact Requests/Responses;
- full response, 206, redirect, bad MIME, error status, unreadable/throwing, delayed, network rejection, and quota-reject routes;
- hand-drained or explicitly controlled promises so pause and stale ordering are exact;
- message-event `waitUntil` and `MessageChannel` acknowledgement recorder;
- fake page lifecycle/visibility/navigation and fresh engine instances over the same persistent fake cache;
- fake DOM for native buttons, progress semantics, live announcements, focus, and reduced motion.

Do not make assertions depend on wall-clock network timing. Test concurrency by counting unresolved operations.

## Required deterministic cases

### 1. Full download of all manifest entries

Start with empty audio cache and a unique manifest. Download all. Assert every request is same-origin canonical full GET with no Range/If-Range, all responses pass shared validation, exact cache keys equal the manifest set, final reconciliation equals total, and Complete appears only after reconciliation.

Run once with the committed 3,621-file manifest using synthetic response bodies to prove exact scale without reading/writing 52 MB.

### 2. Existing entries skipped

Seed valid canonical entries. Reconcile, start, and assert no network/store command is issued for them. Counts include them immediately.

### 3. Partial cache resumes

Seed an arbitrary subset, instantiate a fresh page engine, and assert only set difference is queued. Final cache is the exact union with no reset.

### 4. Exact completion count

Use duplicates, unrelated audio keys, non-audio entries, query variants, invalid MIME, and 206 responses. Assert only exact canonical valid current-manifest 200 audio entries count. `total` is the unique approved manifest size.

### 5. Future manifest with new clips

Complete manifest A (3,621 synthetic identities), reopen with A+59. Assert 3,621/3,680, “59 new”, and only the 59 are fetched. Existing content-hashed keys remain byte/identity untouched.

### 6. Pause/resume

Hold exactly three requests unresolved. Activate Pause. Assert no fourth schedules; resolve the three; counts update; status becomes partial. Continue queues remaining only. Repeated rapid Pause/Continue never exceeds concurrency 3 or duplicates an in-flight key.

### 7. Network interruption

Resolve successes then reject one bounded wave. Assert new scheduling stops, in-flight successes settle, reconciliation preserves them, UI shows partial/network state, and a new engine can Continue after route recovery.

### 8. Quota failure

Make first `put` fail, allow existing 64-entry recovery and one retry; assert shared behavior and acknowledged success. Then make retry fail; assert scheduling stops, post-drain reconciliation is authoritative, no false Complete, no shell/unrelated-cache deletion, and no retry loop.

### 9. Individual bad response

Return 404, 206, redirect, opaque, HTML, missing MIME, and unreadable response cases. Assert none is cached or counted; isolated failures do not erase other successes; final state identifies incomplete count and Try again.

### 10. No duplicate cache entries

Include duplicate manifest file values, repeated messages, rapid Continue, query-bearing inputs, and already-present exact keys. Assert input validation/deduplication and a single exact cache entry per canonical manifest URL.

### 11. Retention-policy compatibility

Download 3,621 into clean cache: no threshold trim. Seed enough approved legacy/future entries to cross 4,200: assert FIFO trim to 4,000, protected write, possible current-set eviction, and mandatory final reconciliation rather than success-counter completion.

### 12. Remove offline audio

Seed intentional, naturally warmed, valid legacy/query, and invalid entries in `popolsku-audio`; seed shell/unrelated caches and localStorage progress. Confirm Remove. Assert only the whole audio cache is deleted, worker estimate resets, other state is untouched, acknowledgement/reconciliation yields zero, and later ordinary playback recreates one audio entry. Cancel path changes nothing.

### 13. Existing lazy cache still works

Never open Offline audio. Drive a normal non-Range clip miss/hit through the shipping fetch handler. Assert online response is returned, shared write stores it, and failure to store never breaks online playback.

### 14. Range playback still works

Retain current matrix: warm exact 206 slices and headers; 416; malformed/multiple/If-Range pass-through; cold Range to unchanged network request; no Range cache writes; body-read invalid eviction. Assert downloader itself never produces a Range request.

### 15. Offline warm playback

After downloader acknowledgement and final reconciliation, reject all network. Play representative early/middle/late manifest clips and exercise Range. Assert MP3 route succeeds without speech fallback.

### 16. Offline cold playback

Use a current-manifest clip absent from cache with network rejected. Assert existing one-time device voice fallback; if speech unavailable/fails, visible polite Retry state. If the later specific offline message is adopted, assert it does not suppress a successful device voice and does not rely solely on `navigator.onLine`.

### 17. Accessibility/progress

Assert native named buttons, exact progress min/max/now/value text, non-color status, stable DOM order, 44px target rules, no focus stealing, same-control Pause→Continue behavior, polite/atomic announcements only at configured milestones, reduced-motion rules, and accessible Remove confirmation/focus return.

### 18. App reload during partial download

Resolve arbitrary subset, discard all page/worker in-memory counters, retain only fake Cache Storage, construct fresh instances, and reconcile. Assert exact retained count and missing-only Continue. Deliver stale old-session replies after reload and assert they are ignored.

## Additional boundary cases

- No `window.caches`, no service worker, install failure, no active worker, and worker replaced mid-session.
- Manifest loading, malformed container, invalid paths, duplicates, empty set, and manifest change during download.
- `navigator.storage`/estimate/persist absent, getter throws, sync return, rejection, denial, grant; none blocks core flow.
- Estimate indicates insufficient space but writes succeed; estimate indicates adequate space but write fails.
- Navigate away while three requests run; no new scheduling and no global UI mutation.
- Remove races with in-flight completion; generation/serialization prevents resurrection.
- Reconciliation invalid-entry eviction failure; invalid entry still not counted.
- Percentage for 0, partial, and exact total; no 100% before final reconciliation.
- Ordinary shell activation preserves audio cache; `AUDIO_CACHE` remains `popolsku-audio`.
- No new analytics, telemetry, cookie, identifier, endpoint, or backup payload inclusion.

## Static/repository gates

Each implementation phase should also run:

- `python3 verify_audio.py` → exact required/manifest/file equality and zero orphaned;
- `python3 build_pages.py --check`;
- content/runtime validation suites;
- current relevant JXA suites with historical release locks updated only as part of the authorized implementation release;
- `git diff --name-only` allowlist for the phase;
- checks that 98/129/269/269 and 269 eligible examples remain unchanged;
- exact manifest and `audio/` hashes unchanged unless a future content phase explicitly authorizes them.

## Physical iPhone acceptance

Repository tests cannot close real Cache Storage quota, service-worker termination, audio decoder, Range, installed-PWA, or VoiceOver risk. The release gate therefore includes the 14-step matrix in `offline-audio-phase-0-ios-storage-analysis.md`, on Safari and Home Screen app, plus:

- download over stable Wi-Fi and a throttled/weak connection;
- pause/continue at multiple counts;
- force-quit/relaunch partial and complete states;
- flight-mode sample spanning app-shell study, Listening, Verb Patterns, and generated-page pronunciation;
- storage pressure/eviction where safely reproducible;
- Remove then ordinary lazy rewarming;
- VoiceOver with display text enlarged, portrait and landscape;
- evidence record of manifest count, reconciled count, device/OS/browser, and observed failures.

No release may claim background completion or permanent retention based on this plan.
