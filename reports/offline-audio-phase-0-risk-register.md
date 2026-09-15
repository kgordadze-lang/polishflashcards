# Offline Pronunciation Download — Phase 0 risk register

| ID | Risk | Impact | Evidence / trigger | Mitigation and acceptance gate |
|---|---|---|---|---|
| OA-01 | Page reports fetched bytes as downloaded before Cache Storage write settles | High | Current `cacheWrite()` is asynchronous, swallowed, and boolean-only | Worker-mediated acknowledged shared store; final cache reconciliation |
| OA-02 | Partial/206 MP3 is cached and later served as full | Critical | Media may issue Range; partial poisoning breaks offline | Full worker GET without Range; status exactly 200; retain classification-before-write tests |
| OA-03 | New path bypasses MIME/redirect/origin validation | High | Direct page `cache.put` or permissive message input | One shared validation/store primitive; worker revalidates canonical same-origin hashed URL |
| OA-04 | Complete library exceeds retention | Medium | 3,621 current vs trim 4,000 / max 4,200 | Clean library fits; test legacy/future entries; final reconciliation; review limits as library approaches 4,000 |
| OA-05 | Quota recovery evicts current clips while adding new ones | High | FIFO deletes 64 oldest on failed put | Stop after final recovery failure; reconcile actual set; never use monotonic success counter as truth |
| OA-06 | Device grants less than ~52 MB | High | Cache quota is per browser/device and estimate advisory | Optional estimate warning; actual typed storage failure; retain partial work; real-device low-storage test |
| OA-07 | Browser/OS later evicts downloaded site data | High | Current Privacy/storage code already treats persistence as best effort | Honest copy; opportunistic persistence; screen reconciliation; never promise permanence |
| OA-08 | iPhone suspends/terminates page or worker | High | Repository proves warm playback, not long background jobs | Foreground small per-file message operations; resume from cache; no background promise; force-quit tests |
| OA-09 | 3,621 concurrent requests overload memory/radio/server | Critical | Naive `Promise.all` | Hard concurrency 3; deterministic unresolved-request ceiling test |
| OA-10 | Pause abort race loses/duplicates progress | Medium | Fetch/cache commit can win just before abort | Minimal Pause stops scheduling and lets ≤3 settle; no AbortController in first release |
| OA-11 | Reload/navigation resets progress to zero | High | In-memory counters are ephemeral | Reconcile real Cache Storage on screen entry/restart; missing-only queue |
| OA-12 | Duplicate/query/legacy cache keys inflate count | High | Versionless cache may contain historical variants | Count only exact canonical current-manifest keys; dedupe manifest; validate candidate response |
| OA-13 | Manifest order or timestamp is mistaken for identity | Medium | Insertion order not sorted; `generatedAt` can change without set change | Set-based reconciliation; optional identity from sorted unique canonical URL set |
| OA-14 | Future release forces full redownload | High | Coarse version flag or cache rename | Keep content-hashed URLs and versionless cache; download set difference only |
| OA-15 | Remove deletes progress/shell or only intentional subset unexpectedly | Critical | Shared audio cache has natural + explicit clips | Clear only `popolsku-audio` after explicit copy/confirmation; preserve shell/localStorage; test cancellation |
| OA-16 | In-flight store resurrects state after Remove | High | Late message/put race | Stop scheduling; worker serialization/generation token; invalidate stale page replies; reconcile after delete |
| OA-17 | Bad single origin response blocks entire useful download | Medium | One 404/MIME error among 3,621 | Continue bounded isolated errors; finish incomplete; retry missing only; never cache bad response |
| OA-18 | Network-loss loop hammers server/battery | High | Automatic immediate retry across large queue | Stop after failed wave/consecutive threshold; learner-initiated Continue; `navigator.onLine` not truth |
| OA-19 | Long cache scan makes every render slow | Medium | 3,621 keys/responses | Reconcile only on Offline screen entry and mutations; enumerate keys once; validate candidates; cache session view |
| OA-20 | Header-valid but corrupt/truncated 200 is counted | Medium | Existing gate does not digest/read full body | Retain repository content-address generation/QA; status-200-only write; real playback sampling; do not read 52 MB on every check |
| OA-21 | First visit page is not yet controlled by worker | High | No `clients.claim()` by design | Message `navigator.serviceWorker.ready.active`; do not depend on page fetch interception; explicit unavailable/retry state |
| OA-22 | Worker protocol weakens update lifecycle or adds forced activation | High | Temptation to add skip-waiting handshake | Preserve no `skipWaiting()`/`clients.claim()`; protocol works with active worker; versioned release tests |
| OA-23 | Progress announcements overwhelm VoiceOver | High | 3,621 increments | Throttled visual updates; announce 10%/state milestones only; polite atomic live region |
| OA-24 | Focus moves/disappears when button state changes | Medium | Pause→Continue and removal state replace actions | Reuse native control DOM where possible; no automatic focus; confirmation returns focus; deterministic tests |
| OA-25 | UI claims offline while current manifest changed | High | Network-first manifest can update independently | Pin session manifest; reload/reconcile active manifest at entry/final; render Update for delta |
| OA-26 | Speech-synthesis fallback regresses | High | More specific offline messaging could short-circuit fallback | Keep additive engine; current fallback/Retry tests; specific cold message only after separate Phase 3 design |
| OA-27 | Listening/Verb Patterns/search/stale async behavior regresses | High | Large inline shell and shared audio owner | Protect named existing suites and manual routes; downloader never calls playback functions |
| OA-28 | Cache name changes and strands 52 MB | Critical | Version bump habit applied to audio | Freeze `AUDIO_CACHE = "popolsku-audio"`; explicit static gate |
| OA-29 | Library growth reaches 4,000 trim target | Medium, increasing | Current headroom is 379 | Add release-time check/warning; revisit count ceiling before manifest reaches target; avoid silent full-download impossibility |
| OA-30 | Stale documentation/product copy contradicts feature | Medium | SW comment says ~34 MB; Privacy/Install say clips only lazy | Phase 2 copy review; keep Privacy factual; no Phase 0 product edit |
| OA-31 | Historical release-lock tests obscure real failures | Medium | Audit saw 5 JXA and 1 Python lock failures for old versions/counts | Separate behavioral assertions from historical snapshots; update authorized current locks in implementation phase, never ignore behavior failures |
| OA-32 | External/platform assumptions are overstated | High | Phase 0 prohibited production/external access; one iPhone observation only | Label evidence boundary; physical iPhone acceptance; no background/permanence claim |
| OA-33 | New local state enters backup/privacy surface | Low if design followed | Temptation to persist completion/download IDs | No required localStorage metadata; Cache Storage is truth; no IDs/telemetry/cookies |
| OA-34 | Direct deletion leaves worker entry estimate stale | Medium | `audioEntryEstimate` lives in worker memory | Worker-owned Remove resets estimate; test next ordinary write |
| OA-35 | Concurrent quota failures cause excessive FIFO eviction | High | Three writes could each run 64-entry recovery | Serialize quota recovery/store critical section or stop queue on first storage failure; concurrency/quota deterministic test |

## Highest-priority gates

The implementation must not proceed to UI integration unless OA-01 through OA-05, OA-08 through OA-12, OA-16, OA-21, OA-28, and OA-35 have deterministic executable coverage.

Physical iPhone release acceptance is mandatory for OA-06 through OA-08, OA-20, OA-23/24, and OA-32. Repository simulation alone cannot close them.

## Residual risks accepted by design

- Cache Storage can be evicted even after a successful complete reconciliation.
- Storage estimates and persistence requests are advisory/best effort.
- Foreground download can be suspended; the product promises resumability, not continuous background work.
- A valid stored status-200 `audio/mpeg` response is treated as complete without rereading/digesting all bodies on each status check.
- Remove clears both intentional and naturally warmed pronunciation clips because per-file ownership metadata is not worth its complexity.
