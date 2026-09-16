# Offline Pronunciation Download — Phase 3 integration and lifecycle compatibility

## Scope and starting repository proof

Phase 3 validates the approved downloader/UI stack end to end and fixes one demonstrated release-lifecycle compatibility defect. It is not release preparation and does not deploy, generate audio, change learning content, or advance release markers.

| Item | Verified starting value |
|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Codex - Offline Audio Phase 3` |
| Branch | `offline-audio-phase-3-regression` |
| Starting `HEAD` | `b6f5cb8849d20944aecaa4d15bfae16aac8b9926` |
| Starting `HEAD^{tree}` | `c8a0d575264927301d8340c1d5dee01335c45e3c` |
| Starting worktree | clean |
| Git remotes | none |
| `push.default` | `nothing` |

The supplied expected starting value is the tree object, not the commit object, and matched exactly. Production and the two prohibited local repositories were never accessed. Nothing was pushed or deployed.

## Prior reports reviewed

All approved Offline-audio reports were read in full before product editing:

- `offline-audio-phase-0-current-architecture.md`
- `offline-audio-phase-0-cache-and-range-audit.md`
- `offline-audio-phase-0-ios-storage-analysis.md`
- `offline-audio-phase-0-download-engine-options.md`
- `offline-audio-phase-0-product-ui-states.md`
- `offline-audio-phase-0-test-plan.md`
- `offline-audio-phase-0-risk-register.md`
- `offline-audio-phase-0-implementation-plan.md`
- `offline-audio-phase-1-engine.md`
- `offline-audio-phase-2-ui.md`, including the independent-review correction for re-entry while stale lanes drain

The corrected stale-session/successor architecture was preserved and remains directly covered.

## Historical production-style worker evidence

The commit titled **Implement offline audio download engine** is `3a5b27ff4ae34a4aea09cef50fa8228fc789a166`. Its immediate parent is the immutable historical worker source required by this phase:

| Item | Exact value |
|---|---|
| Historical commit | `9931aed6585012a0a407e0cd50d141de5f58639a` |
| Historical tree | `0717d2ab7a04f02c5e9d378f4df5e59c25f44f52` |
| Historical `sw.js` SHA-256 | `80c48a61d62b3e2047bffabf037a48373d357e5be35117389936dedbd1f07b81` |

The Phase 3 suite reads this exact `sw.js` with `git show`. It contains none of `offline-audio-capabilities`, `offline-audio-reconcile`, `offline-audio-store-one`, or `offline-audio-remove`. No historical commit was modified and no historical worker copy was added to product assets.

## Mixed-release reproduction and pre-fix result

Before product editing, `tests/test_offline_audio_phase3_integration.js` was first created as a seven-assertion reproduction and passed **7/7**. The starting candidate had no capability command. Its first worker operation was `offline-audio-reconcile` carrying the full manifest set, through `workerRequest()`'s general `CHANNEL_TIMEOUT_MS = 30000`. The genuine historical worker ignored that unknown message and never replied.

Therefore new page + historical active worker remained in Checking until the normal 30-second channel timeout. The learner could see an apparently frozen screen, and the implementation had no basis for distinguishing an updating app from another worker-channel failure. A narrow compatibility fix was necessary.

## Compatibility fix

### Protocol

The current worker now accepts one additional local command:

```text
offline-audio-capabilities
→ outcome: supported
→ protocolVersion: 1
```

The reply uses the existing transferred `MessagePort`, token validation, reply helper, and event lifetime handling. It performs no fetch, Cache Storage operation, manifest processing, persistence, telemetry, or network communication. The existing reconcile, store-one, and remove commands are unchanged.

Before every reconciliation, the page sends this capability probe with an empty payload. Only a valid `{outcome: "supported", protocolVersion: 1}` reply permits the full manifest reconciliation. The historical worker ignores it, so it never receives the 3,621-entry manifest and can never receive a store-one operation.

### Timeout rationale

The capability timeout is **2,500 ms**, independent of the normal **30,000 ms** channel timeout. A supported worker's reply is local and effectively immediate, but a mobile browser may need to wake a suspended worker process. Two and a half seconds allows conservative wake-up slack while being twelve times shorter than the normal operation timeout and fast enough to turn Checking into an actionable state. The normal reconcile/download timeout was not weakened.

### Waiting/installing state and truthful copy

After a protocol probe failure only, the UI inspects `registration.waiting` / `registration.installing` as local context. Those fields are not treated as protocol proof. When either exists, the screen says:

> Offline audio will be available after Po polsku finishes updating.
>
> Close and reopen Po polsku, then try again.

It provides **Try again**. It does not claim that reload always activates the worker, send `SKIP_WAITING`, call `skipWaiting()` or `clients.claim()`, or reload automatically. Without a waiting/installing worker, the existing generic unavailable state remains truthful.

The opposite case is explicitly covered: if the active worker supports protocol version 1, a future waiting worker does not disable Offline audio. The supported active worker remains authoritative and reconciliation proceeds.

### Worker replacement while open

The controller listens for `controllerchange` only to invalidate the engine generation, clear its mutation generation, cooperatively stop scheduling, and publish an interrupted state. It never starts or resumes work and never reloads. A stale capability/reconciliation reply from the previous worker fails the existing generation check and cannot overwrite the newer UI state. The next explicit Retry or screen re-entry performs a fresh capability probe and reconciliation against the then-active worker.

## Integrated deterministic results

`tests/test_offline_audio_phase3_integration.js` executes the real shipping worker and page engine blocks against deterministic Cache Storage, worker, MessageChannel, timer, and controlled-promise fakes. It also executes the entire Phase 1 harness first, then adds 50 Phase 3 assertions.

Covered outcomes include:

- genuine historical worker protocol absence and the mixed-release mismatch;
- 2.5-second bounded capability failure independent of 30-second normal operations;
- no manifest, store-one, cache write, fetch, or pronunciation change on capability failure;
- waiting/installing update copy and Retry;
- supported active + future waiting behavior;
- repeated Retry/re-entry capability probes;
- controller replacement and stale capability reply suppression;
- empty, partial, and synthetic complete-3,621 reconciliation;
- concurrency 3, Pause, missing-only Continue, rapid Continue deduplication;
- stale-lane drain successor, Remove cancellation, and newer-reconciliation cancellation;
- reload reconstruction and future +59 manifest growth;
- bounded network, bad-response, storage, and retention-conflict outcomes;
- shared-cache Remove and ordinary lazy rewarming;
- warm Range, cold Range, If-Range, and complete downloader GET separation;
- no page Cache Storage mutation, durable capability/download state, telemetry, forced activation, or forced reload.

The approved page-engine architecture is unchanged: three lanes, cooperative Pause, successor-after-drain, final reconciliation as completion truth, worker-owned cache mutations, and no `AbortController` or Background Sync.

## Offline playback and missing-clip behavior

Deterministic worker/fetch coverage confirms:

- a valid full clip in `popolsku-audio` plays offline;
- a cold missing clip does not become available without a successful fetch/store;
- an intentional downloader store makes a clip available without prior media playback;
- Remove clears intentional and naturally warmed clips from `popolsku-audio` only;
- ordinary online pronunciation after Remove warms the cache again;
- warm Range synthesis returns correct 206 content while cold Range and If-Range pass through without cache writes.

The existing cold-missing pronunciation behavior remains unchanged. A failed MP3 first attempts speech synthesis; success reports **Using your device's voice.** If synthesis is absent/fails, the existing polite Retry state says **Audio couldn't play. Check your connection, then try again.** This is not materially false across the broader online decode/server failure cases, and there is no narrow deterministic distinction that improves it without coupling playback to stale screen reconciliation or `navigator.onLine`. Specific “not downloaded” copy remains a possible future product refinement, not a Phase 3 change.

## Real local registered-worker and UI QA

A temporary localhost server and the Codex in-app browser were used. Production was never opened.

The browser first reproduced the actual mixed-release lifecycle rather than a theoretical substitute: an older active worker controlled the new page while the replacement waited. The new screen left Checking and rendered the new update-pending copy with Try again. Closing that client and reopening naturally allowed the current worker to become active; no activation message or forced reload was used. The current worker then completed real capability/reconciliation communication and rendered the pre-existing local truth, **40 of 3,621 available offline**.

A second, clean localhost origin registered the current worker and reconciled a clean audio cache as **0 of 3,621 available offline**, with **Download audio**. No full-library download was started and no audio entry required cleanup on that clean origin.

The in-app browser's isolated evaluation surface does not expose application globals, service-worker APIs, or Cache Storage to its read-only evaluator. A three-file console engine/store/remove harness therefore could not be run safely. The existing 40-entry origin was deliberately not cleared or modified. Complete GET storage, fresh-engine warm retrieval, Range, and Remove round trips are claimed only from deterministic shipping-source tests, not as live-browser results.

Actual UI checks performed:

- direct `#offlineAudio` entry and screen-heading focus;
- menu item after Install and navigation back to Offline audio;
- mixed-release update-pending state and explicit Retry;
- current-worker empty and partial states;
- native progress and Download/Continue/Remove controls;
- Remove confirmation with Cancel initially focused;
- cancellation made no removal call and restored focus to Remove;
- no horizontal overflow at 390×844, 320×568, or 568×320 landscape;
- landscape and 320px states scroll vertically when necessary;
- long update-pending/supporting copy remained within the card.

No physical iPhone, VoiceOver, reliable 200% OS text scaling, storage-pressure behavior, or full-library browser download is claimed.

## Test results

### Required Offline-audio suites

| Command | Result |
|---|---:|
| `osascript -l JavaScript tests/test_offline_audio_phase1_engine.js` | **89 passed, 0 failed** |
| `osascript -l JavaScript tests/test_offline_audio_phase2_ui.js` | **104 passed, 0 failed** |
| `osascript -l JavaScript tests/test_offline_audio_phase3_integration.js` | **50 passed, 0 failed** (and internally reruns Phase 1 at 89/0) |

### Maintained protected regressions

These maintained suites total **3,630 passed, 0 failed**:

| Area | Result |
|---|---:|
| audio fallback | 585/0 |
| inline audio failure/Retry | 38/0 |
| Priority 8 playback | 25/0 |
| accessibility foundation | 82/0 |
| keyboard/focus | 214/0 |
| core activity accessibility | 127/0 |
| Listening accessibility | 229/0 |
| Listening variety | 193/0 |
| Mixed Quiz audio | 260/0 |
| Mixed Quiz accessibility | 411/0 |
| Mixed Quiz distractors | 195/0 |
| Mixed Quiz round legibility | 346/0 |
| Conversations | 101/0 |
| Podcasts | 100/0 |
| Grammar | 616/0 |
| shared overlays | 108/0 |

### Historical/frozen exceptions

No historical provenance test was weakened:

- navigation: **393 passed, 2 failed**, frozen app `8.11` / shell `v66` locks;
- focus/scroll: **315 passed, 1 failed**, frozen app `8.11` lock;
- mobile layout: **168 passed, 1 failed**, frozen app `8.11` lock;
- offline navigation/installability: **185 passed, 3 failed**, frozen app `8.11` / shell `v66` locks;
- Range/storage resilience: **554 passed, 9 failed** — frozen shell/count/app locks plus old exact source-shape, diagnostic-key, string-occurrence, and validation-call counts; its maintained replacements pass in Phase 1/3;
- Verb Patterns search: 11 behavioral tests passed and one frozen app `8.13` scope assertion failed;
- speaker-icon UI: four behavioral tests passed and one frozen app `8.13` input-scope assertion failed;
- historical Priority 7 patterns UI still aborts at its removed `p7-fixture-card-001` support fixture, as documented in Phase 1/2.

## Validators and protected invariants

| Command | Result |
|---|---|
| `python3 validate_content.py` | passed — 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline intact |
| `python3 verify_audio.py` | passed — 3,621 required, 3,621 manifest, 3,621 MP3, 0 missing, 0 orphaned |
| `python3 validate_priority8_staging.py` | passed — read-only revision 8 valid |
| `python3 build_pages.py --check` | passed — generated output current |
| `git diff --check` | passed |

Protected values remain exact:

- audio payload: 54,378,576 bytes / 51.859451 MiB;
- `audio-manifest.json` SHA-256: `09f038097c118c6c55c00f15185a5e4207d02f103480675ad0b3a499ab3ad0a7`;
- 98 lemmas, 129 meanings, 269 patterns, 269 examples, 269 pronunciation-enabled examples;
- `audio-manifest.json`, all `audio/*.mp3`, `content/verb-patterns.json`, generated pages, and `sitemap.xml` are unchanged;
- `APP_VERSION = "9.15"`, `CACHE = "popolsku-v70"`, and `AUDIO_CACHE = "popolsku-audio"` are unchanged;
- no analytics, telemetry, cookies, identifiers, external API, server progress, persistent capability state, second cache/manifest, direct page cache writes, skip-waiting path, client claim, Background Sync, or automatic background continuation was added.

## Files changed

- `index.html` — short capability probe, protocol-failure state, update-pending rendering, Retry/re-entry behavior, and controller-change invalidation.
- `sw.js` — immediate version-1 capability reply through the existing message protocol.
- `tests/test_offline_audio_phase1_engine.js` — one custom transport fixture acknowledges the newly required capability probe; no existing assertion changed or removed.
- `tests/test_offline_audio_phase3_integration.js` — focused 50-assertion lifecycle/integration suite using shipping source and immutable history.
- `reports/offline-audio-phase-3-integration.md` — this evidence report.

## Phase 4 physical-iPhone acceptance checklist

Phase 4 remains required before release preparation. Record device model, iOS/browser build, Safari versus Home Screen context, available device storage, connection, manifest total, and final reconciled count for each run.

1. Begin with the old released worker active, deploy/install the candidate as waiting, load the new page through the old worker, and confirm fast update-pending copy with no manifest/store command or false completion.
2. Close every client, reopen naturally, use Try again, and confirm the current worker reconciles; also confirm a supported active worker continues to work while a future worker waits.
3. Fresh site data: verify 0/3,621 and start on stable Wi-Fi; confirm responsiveness and maximum concurrency 3.
4. Pause at several counts; verify at most three in-flight completions and no further scheduling. Continue once during stale-lane drain and confirm automatic missing-only successor completion without a second activation.
5. Navigate away and background/foreground for short and long intervals; confirm navigation is never blocked, no auto-resume occurs, and re-entry reconciles.
6. Force-quit/relaunch partial state and Continue; confirm reconstruction solely from Cache Storage.
7. Lose the network mid-download, then recover; confirm bounded failure, retained partial truth, explicit Continue, and no request storm.
8. Exercise storage pressure where safe; confirm one recovery wave, bounded failure, no loop, and no false Complete.
9. Complete to exactly 3,621/3,621 by reconciliation, then use flight mode to sample early/middle/late manifest clips across study, Listening, Mixed Quiz, Grammar/generated pages, and Verb Patterns.
10. Scrub a warm clip offline and confirm Range behavior; request a cold clip and confirm device-voice fallback or visible Retry without claiming it was downloaded.
11. Test Safari and installed Home Screen app separately; repeat background, termination, update-waiting, and offline playback cases.
12. Verify Remove confirmation, cancellation, focus return, confirmed removal of intentional and warmed audio, and ordinary online lazy rewarming afterward.
13. Test 320/390 portrait, landscape, enlarged text/200% where measurable, reduced motion, keyboard-equivalent input, safe areas, and VoiceOver announcements/focus.
14. Recheck after browser/device cleanup or eviction and confirm the UI reconstructs truth rather than trusting a durable completion/version flag.

Physical acceptance and release-marker/cache advancement are explicitly outside Phase 3.
