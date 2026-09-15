# Offline Pronunciation Download — Phase 1 engine

## Scope and starting repository proof

Phase 1 implements only the shared downloader/cache engine and deterministic tests. It adds no learner-facing Offline audio screen, menu item, progress control, copy, or route.

| Item | Verified starting value |
|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Codex - Offline Audio Phase 1` |
| Branch | `offline-audio-phase-1-engine` |
| Starting commit (`HEAD`) | `9931aed6585012a0a407e0cd50d141de5f58639a` |
| Starting tree (`HEAD^{tree}`) | `0717d2ab7a04f02c5e9d378f4df5e59c25f44f52` |
| Starting worktree | clean |
| Git remotes | none |
| `push.default` | `nothing` |

The supplied expected value was the starting tree object, and it matched exactly. All eight approved Phase 0 reports were read before product-code editing.

No production site, remote repository, deployment target, or other local repository was accessed. Nothing was pushed or deployed.

## Shared validated audio store

`sw.js` now has one promise-returning `storeValidatedAudio(key, response)` primitive for audio writes. It:

1. requires an approved canonical content-hashed audio key;
2. applies the existing `isCacheableResponse()` contract (`ok`, status 200, non-redirected basic/default response, exact `audio/mpeg` MIME);
3. takes the two clones needed for an initial put and at most one retry;
4. writes only to `popolsku-audio`;
5. awaits existing FIFO retention maintenance;
6. on first put failure, awaits the coalesced recovery barrier and retries its own response once;
7. returns `stored`, `bad-response`, or `storage-failed` with no rejection escaping expected storage failures.

The ordinary non-Range playback `cacheWrite()` branch wraps this exact primitive under `FetchEvent.waitUntil()` and continues to return the successful online response immediately. Storage failure therefore remains non-blocking to the learner. Non-audio shell writes retain their existing path. The Phase 1 harness executes an ordinary audio fetch and an explicit downloader message and proves that both increment the same `storeValidatedAudio` instrumentation.

Status 206 cannot reach this primitive through normal dispatch: Range requests are still classified before the ordinary audio branch, and the primitive itself independently rejects any non-200 response. The downloader constructs its own complete `Request` and copies no caller headers.

## Quota single-flight design

Quota recovery uses an in-memory epoch plus one shared barrier:

- each write records the recovery epoch before its initial `cache.put`;
- the first failed write for that epoch starts one bounded eviction wave;
- overlapping failures await the active barrier;
- a failure handler that runs after the same wave completed observes the advanced epoch and reuses its result instead of starting another wave;
- after the barrier, each affected write retries its own spare clone at most once;
- a later write begun in a later epoch may start a later recovery wave;
- there is no retry or recovery loop.

The eviction policy remains exactly 64 oldest approved clips, excluding the key being stored. Deterministic controlled-promise coverage proves three concurrent initial failures perform one recovery wave and 64 deletions, while all three retain their one-retry ceiling.

## Worker message protocol

The active worker handles three local commands over the first transferred `MessagePort`. Every acknowledgement echoes only the short ephemeral request token and command. Tokens are never persisted or sent over the network.

### `offline-audio-reconcile`

Input is `files` plus `token`. The worker accepts at most 5,000 values, allowing reviewed growth above the current 3,621 while retaining a strict bound. It accepts only exact committed-manifest spelling (`audio/<lowercase-hex>.mp3`) or the exact canonical absolute URL. It rejects duplicates, whitespace variants, dot segments, leading-slash alternatives, query/fragment values, cross-origin URLs, paths outside worker scope, malformed paths, and non-hashed filenames.

Reconciliation opens only `popolsku-audio`, calls `cache.keys()` once, intersects exact stored URLs with the validated current set, then validates candidate responses sequentially. Its maximum simultaneous Cache operation is therefore **1**. It applies `isCacheableResponse()` without reading bodies, evicts invalid exact hits, and returns counts plus bounded present/missing URL arrays—never Responses or bodies.

Worker diagnostics record reconciliation count and observed active/maximum Cache operations. The exact 3,621-identity scale test confirms one scan, bounded validation, and zero reconciliation body reads.

### `offline-audio-store-one`

Input is one `file`, the worker mutation generation obtained from reconciliation, and `token`. The worker revalidates the URL and generation, returns `already-present` for an exact valid hit, otherwise constructs a full same-origin GET with no Range or If-Range header. It distinguishes:

- `already-present`;
- `stored`;
- `bad-response`;
- `network-failed`;
- `storage-failed`;
- `stale` for an invalidated downloader mutation;
- `invalid-request` / `worker-failed` for protocol boundaries.

One message handles one clip. It never invokes a learner playback function.

### `offline-audio-remove`

Remove increments the worker mutation generation immediately and joins the explicit audio-mutation queue. It deletes exactly `popolsku-audio`, resets `audioEntryEstimate` to `null`, and returns `removed` (including the already-absent case) or `remove-failed`. It cannot delete the numbered shell cache, unrelated caches, progress, localStorage, or learning data.

## Store/remove ordering

Reconciliation returns the current in-memory worker mutation generation. Every explicit store message must present that exact generation. Network fetches can overlap, but validated downloader writes enter a small worker-side mutation queue before `storeValidatedAudio()`.

Remove increments the generation synchronously before its queued deletion. Therefore an older downloader operation has only two possible orderings:

- its queued store completes before Remove, after which Remove deletes it; or
- it reaches the queue after invalidation and returns `stale` without writing.

A late old-generation fetch cannot recreate audio after acknowledged removal. No persistent transaction metadata is used. An ordinary learner playback remains free to warm a clip again after Remove.

## Dormant page download engine

`index.html` contains a marked, non-visible `window.PPOfflineAudioEngine` block. Keeping it inline avoids introducing a new shell asset or changing the frozen shell cache revision.

The factory validates and deduplicates a manifest set, then exposes `reconcile`, `start`, `continueDownload`, `pause`, `remove`, and immutable state/manifest snapshots. It never opens Cache Storage, never programs media playback, never uses localStorage, and does not depend on `navigator.storage` APIs or `navigator.onLine`.

The default transport waits for `navigator.serviceWorker.ready.active`, creates one `MessageChannel` per request, validates the echoed command/token, and has a bounded channel timeout. Missing, replaced, throwing, malformed, or timed-out worker/channel behavior becomes `interrupted`; a later Continue begins with a fresh worker reconciliation.

### Scheduler and Pause

The scheduler creates exactly three fixed lanes. `Promise.all` covers those three lane promises only—never the manifest. Each lane owns at most one `offline-audio-store-one` request, so at most three downloads are active. A session guard prevents rapid Continue from creating a second set of lanes while Pause is draining.

Pause changes scheduling state immediately, schedules no next item, and lets up to three active operations return durable acknowledgements. It uses no `AbortController`. Continue always starts a new generation and fresh reconciliation, then queues only current missing URLs.

### Failure policy

The selected network policy is **stop on the first failed concurrency wave**: the first `network-failed` acknowledgement stops new scheduling, while the other at-most-two active operations settle. This is deterministic, avoids connection-loss request storms, and retains successful work.

Up to two isolated bad responses may occur while useful downloads continue; the third stops new scheduling. A final incomplete state is returned even for one bad response. A final `storage-failed` stops scheduling immediately. All stop paths drain bounded in-flight operations where the channel still responds and reconcile actual storage before returning.

No automatic retry loop exists. Continue is a new reconciled session.

## Completion, retention and manifest updates

Complete is emitted only when final worker reconciliation reports every unique current-manifest URL present as a valid exact full response. Scheduled requests, successful fetches, store acknowledgements, and page counters are never sufficient.

After one complete missing-queue pass, if there were no network, bad-response, storage, or channel errors but final reconciliation still reports missing entries, the engine returns `retention-conflict`. It does not redownload automatically, clear legacy entries, or raise `AUDIO_CACHE_MAX_ENTRIES`.

The clean exact 3,621-entry committed set completes below the 4,200 ceiling with zero retention deletions. A deterministic 4,200-existing-entry case triggers current FIFO trimming, loses current-set entries, finishes `retention-conflict`, and proves only one originally missing URL was fetched.

For a synthetic future manifest of 3,680 entries over a complete current 3,621-entry cache, reconciliation reports the set difference and the engine fetches exactly 59 URLs. Existing content-hashed entries remain untouched. No downloaded-version flag or second manifest exists.

## Files changed

- `sw.js` — shared audio store, coalesced quota recovery, bounded reconciliation, typed message protocol, and downloader mutation ordering.
- `index.html` — dormant inline page engine only; no markup, screen, menu entry, route, copy, or ordinary playback changes.
- `tests/test_offline_audio_phase1_engine.js` — focused deterministic shipping-code harness.
- `reports/offline-audio-phase-1-engine.md` — this report.

## Deterministic and protected test results

### Current Phase 1 and behavioral suites

| Command | Result |
|---|---:|
| `osascript -l JavaScript tests/test_offline_audio_phase1_engine.js` | **77 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_fallback.js` | **585 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_failure_inline_feedback.js` | **38 passed, 0 failed** |
| `osascript -l JavaScript tests/test_priority8_phase1_playback.js` | **25 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1a_accessibility.js` | **82 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1b_keyboard_focus.js` | **214 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_accessibility.js` | **229 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_variety.js` | **193 passed, 0 failed** |
| `osascript -l JavaScript tests/test_mixed_audio.js` | **260 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase3b_overlays.js` | **108 passed, 0 failed** |
| `python3 tests/test_priority8_phase1.py` | **17 passed, 0 failed** |

The Phase 1 suite covers the committed 3,621-identity scale set with synthetic responses; existing-entry skip; partial/reload resume; exact invalid-entry filtering; future +59; concurrency 3; cooperative Pause/Continue; bounded network/bad/storage failures; single and concurrent quota failures; final retry failure; response rejection matrix; duplicate messages; clean and legacy retention cases; exact Remove; store/remove races; ordinary lazy rewarming; storage-nonblocking playback; warm/cold/unsatisfiable/If-Range behavior; offline warm playback; unchanged fallback/Retry contract; stale generations; channel loss/replacement; URL/count trust boundaries; no body reads; no page cache writes/persistent tracking; and no telemetry.

### Repository validators

| Command | Result |
|---|---|
| `python3 validate_content.py` | passed — 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline intact |
| `python3 verify_audio.py` | passed — 3,621 required, 3,621 manifest, 3,621 MP3, 0 missing, 0 orphaned |
| `python3 validate_priority8_staging.py` | passed — read-only revision 8 valid |
| `python3 build_pages.py --check` | passed — committed generated output current |
| `git diff --check` | passed |

The manifest SHA-256 remains `09f038097c118c6c55c00f15185a5e4207d02f103480675ad0b3a499ab3ad0a7`.

## Historical and frozen-suite exceptions

No historical suite was edited or weakened.

- `tests/test_phase4b3_audio_resilience_range_storage.js`: **555 passed, 8 failed**. Five failures are frozen release/content locks (`popolsku-v66`, app `8.11`, and 3,377 clips). Three are exact old source-shape locks: the former `afterAudioWrite`/`recoverAudioWrite` call strings, the exact old audio-diagnostic key list, and the old count of write-validation call sites. The maintained Phase 1 suite directly executes and passes the replacement shared-store, coalesced-recovery, validation, retention, and Range invariants.
- `tests/test_phase4b2_offline_navigation_installability.js`: **185 passed, 3 failed**, all frozen `v66` / `8.11` release locks.
- `tests/test_phase2c_navigation.js`: **391 passed, 2 failed**, both frozen `v66` / `8.11` release locks.
- `tests/test_phase3b_focus_scroll.js`: **315 passed, 1 failed**, frozen app `8.11` lock.
- `tests/test_phase3b_mobile_layout.js`: **168 passed, 1 failed**, frozen app `8.11` lock.
- `tests/test_priority8_phase4f1_verb_patterns_search.py`: 11 behavioral tests passed; one frozen `8.13` release/scope test failed.
- `tests/test_priority8_phase4d1_speaker_icon_ui.py`: four behavioral tests passed; one frozen `8.13` release/input-scope test failed.
- `tests/test_phase4b1_service_worker_cache.js` reaches an existing frozen `v66` seed and aborts when the current `v70` cache correctly does not populate that seed's expected invalid-read record. Its committed assertions also explicitly prohibit the message protocol that Phase 1 is authorized to add. The current worker/cache/message behavior is covered in the maintained Phase 1 harness.
- `tests/test_priority7_patterns_ui.js` aborts against its historical `p7-fixture-card-001` support fixture. Phase 1 changes neither Verb Patterns runtime nor content; current pronunciation and search suites above cover the affected boundary.

These exceptions remain visible for provenance. No old version/count was mass-replaced.

## Frozen invariants and scope confirmation

- `APP_VERSION = "9.15"` unchanged.
- `CACHE = "popolsku-v70"` unchanged.
- `AUDIO_CACHE = "popolsku-audio"` unchanged.
- Retention remains 4,200 maximum / 4,000 trim target / 64 quota eviction / one retry.
- Audio remains 3,621 required / 3,621 manifest / 3,621 files / 0 missing / 0 orphaned and 54,378,576 bytes (51.859451 MiB).
- Verb Patterns remains 98 lemmas / 129 meanings / 269 patterns / 269 examples / 269 pronunciation-enabled examples.
- No audio, manifest, content, Verb Patterns runtime/content, generated page, sitemap, privacy, install/about, analytics, Listening, or pronunciation-eligibility file changed.
- No second manifest, cache, MP3 copy, ZIP, IndexedDB store, completion flag, telemetry, endpoint, persistent identifier, `skipWaiting()`, or `clients.claim()` was introduced.
- There is no learner-visible Offline audio screen or menu entry.
- Git remotes remain empty. Nothing was pushed or deployed. Production was never accessed.
