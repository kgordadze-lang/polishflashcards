# Offline Pronunciation Download — iPhone and storage analysis

## Evidence boundary

This report is based only on the supplied repository, its deterministic tests, and the supplied physical-iPhone observation. Production and external sites were not accessed. Platform behavior that is not executable in this repository remains a real-device acceptance requirement, not a claim.

The observed iPhone result is positive and specific: a full MP3 previously warmed online is served offline, while an unwarmed clip is unavailable. That validates the existing Cache Storage/Range playback mechanism on the tested device. It does not establish quota, 3,621-file acquisition, eviction, background continuation, or browser-restart behavior.

## Capability gates

The first implementation should require only capabilities essential to the design:

- `"serviceWorker" in navigator`;
- a successfully installed/active worker from `navigator.serviceWorker.ready`;
- guarded access to `window.caches` / Cache Storage;
- a usable active audio manifest.

If any essential gate fails, show the unsupported/unavailable state and preserve ordinary playback/fallback. Do not make learning flows depend on the feature.

The following are optional enhancements only:

- `navigator.storage`;
- `navigator.storage.estimate()`;
- `navigator.storage.persisted()`;
- `navigator.storage.persist()`;
- `AbortController`.

The current app already guards every persistence API access/call and treats absence, throwing getters, sync returns, rejected promises, and denial as non-blocking. The downloader should reuse that posture.

## Storage estimate

`navigator.storage.estimate()` can be advisory before download and useful after a quota failure, but it must not be a prerequisite or a promise:

- it can be absent;
- it reports whole-origin usage/quota, not `popolsku-audio` alone;
- reported free space need not equal writable Cache Storage;
- the browser/device can evict data or reject writes independently;
- payload is 54,378,576 bytes, while practical stored/transfer cost can be higher.

A conservative warning threshold can compare estimated free space with payload still missing plus headroom, but “enough” should permit an attempt, not guarantee success. An estimate that suggests too little space should ask the learner to free space and retry, while still allowing a deliberate attempt if product chooses; actual `cache.put` outcomes remain authoritative.

Do not show a false exact requirement such as “51.859451 MiB free”. Learner copy should remain “About 52 MB”; optionally “You may need a little more free space.”

## Persistence

Call the existing guarded persistence request opportunistically after explicit Download/Update intent if it has not already been asked in the session. A grant improves eviction resistance; denial, absence, or failure must not block the download or change completion criteria.

Neither an installed PWA nor a granted persistence request justifies “permanent”. Accurate supporting copy is:

> Your browser or device may remove downloaded website data when storage is low or site data is cleared. You can return here to check or download it again.

The Privacy page already says browser/device data can be removed. A later product phase should align its lazy-audio description with the new optional download feature, without adding tracking or new data disclosure categories.

## Lifecycle and background limits

Do not promise background downloading on iPhone. The safe contract is foreground, resumable work:

- while the Offline audio screen/page is active, schedule at most three full downloads;
- Pause stops scheduling and allows in-flight items to finish;
- navigating elsewhere in the single-page app stops new scheduling; in-flight operations may settle;
- backgrounding, closing, process eviction, or browser restart may stop the session at any point;
- reopening Offline audio performs a fresh cache reconciliation and offers Continue for only missing clips.

This makes interruption normal rather than exceptional. It also avoids a fragile long-lived in-memory counter or claim that `ExtendableMessageEvent.waitUntil()` can hold a mobile worker alive for an entire 52 MB library.

`AbortController` is not needed for the smallest reliable Pause. Aborting up to three full MP3s saves little (mean file about 15 KB), complicates whether a write committed just before abort, and adds more race states. Let them settle, update from acknowledgements, then reconcile. A future Stop-now control could use abort only after deterministic tests.

## Concurrency recommendation

Use **3** full MP3 requests concurrently.

| Limit | Assessment |
|---:|---|
| 2 | Very conservative, but unnecessarily lengthens 3,621-request completion and makes latency dominate more strongly. |
| 3 | Recommended balance: bounded memory/radio/server load, responsive pause (at most three small clips drain), and useful latency hiding. |
| 4 | Plausible, but provides modest additional throughput for tiny files while increasing simultaneous response clones/cache writes and quota races. |
| 3,621 | Prohibited: unbounded memory, sockets, server load, failure fan-out, and unusable pause. |

This is a conservative product default, not a benchmark claim. Physical-iPhone acceptance should compare 2 and 3 on the target devices/network if sustained download exposes instability; correctness must be independent of the chosen constant.

Because the worker store path may hold a response plus validation/write clones for quota recovery, concurrency bounds response memory as well as network pressure. With the observed max file 42,048 bytes, three bodies are modest, but browser implementation overhead and Cache Storage serialization remain reasons not to increase casually.

## Network truth and failures

Never treat `navigator.onLine` as authoritative. It may be used only to tailor a hint or defer an eager retry. A full fetch and acknowledged store outcome establish whether one clip succeeded.

On network loss:

- stop scheduling after the first small bounded set of network failures rather than hammering all 3,621 URLs;
- allow successful in-flight writes to settle;
- reconcile actual cache state;
- show `N of M available offline` and Continue;
- resume only after learner action (or a deliberately tested online event as a convenience, never as proof).

An individual bad HTTP/MIME/redirect response must be reported separately from quota pressure. The engine should continue past a small number of isolated bad files so one corrupt origin response does not discard 3,620 successes, then finish in an incomplete state listing a concise count, not thousands of errors.

## Quota behavior

The existing worker recovery evicts 64 oldest approved clips and retries once. During a whole-library download this can produce progress that goes backward: a new clip may be stored while an old current-manifest clip is evicted. UI progress must be monotonic only within acknowledged operations for presentation; completion and post-failure totals must come from reconciliation.

After any quota-recovery failure:

1. stop scheduling new downloads;
2. let at most three in-flight operations settle;
3. reconcile the actual cache;
4. show an honest storage failure with the retained count;
5. suggest freeing device/browser storage and trying Continue;
6. never clear progress automatically.

The count-based 4,200 ceiling permits the clean current library. It cannot guarantee that an individual device grants ~52 MB.

## Real-device acceptance matrix

Run on at least one supported current iPhone/Safari configuration and the installed Home Screen app; record device model, OS/browser build, free device storage, connection, and whether persistence/estimate APIs appear. Do not infer one environment from the other.

1. Fresh site data: open Offline audio, confirm checking and 0/3,621 state.
2. Start over Wi-Fi; verify count advances, controls remain responsive, screen stays usable with VoiceOver.
3. Pause; verify no new scheduling and no more than three in-flight completions.
4. Continue; verify already cached files are not requested again.
5. Background and foreground after short and longer intervals; accept suspension, require correct reconciliation.
6. Close/force-quit, reopen, and Continue; verify no reset to zero.
7. Disable network mid-download; verify bounded failure, honest partial count, and later recovery.
8. Complete; enable flight mode; sample clips from early/middle/late manifest positions plus Listening and Verb Patterns.
9. Request a never-cached synthetic/test fixture where safely available; verify current cold-offline fallback/failure behavior.
10. Exercise scrub/Range playback on warm clips offline.
11. Simulate low storage where practicable; verify no loop, crash, or false completion.
12. Remove offline audio; confirm cache disappears, status becomes not downloaded, and ordinary online play warms one clip again.
13. Relaunch and re-check after device/browser cleanup or simulated eviction.
14. Test large text, reduced motion, keyboard-equivalent external input where available, and VoiceOver announcements at milestones only.

Release acceptance requires exact 3,621/3,621 reconciliation on the tested active manifest, not merely a 100% in-memory counter.
