# Offline Pronunciation Download — cache and Range audit

## Cache names and asset classification

[`sw.js`](../sw.js) currently declares:

- versioned shell cache: `popolsku-v70`;
- deliberately versionless audio cache: `popolsku-audio`;
- approved audio path: `/audio/[a-f0-9]+\.mp3` under the worker scope and same origin.

`classifyRequest()` rejects non-GET, unsupported scheme, cross-origin, and unknown requests from application caching. It classifies any request carrying `Range` before ordinary route classification. A non-Range approved MP3 goes to the audio cache-first branch. The audio manifest is a required shell asset and network-first at runtime.

Activation deletes only names matching `^popolsku-v[0-9]+$`, excluding the current shell and `popolsku-audio`. It never performs prefix-wide deletion.

## Full-response validation

`isCacheableResponse(response, key)` is the single current write/read gate. An audio response is accepted only when all are true:

- response exists and `ok === true`;
- status is exactly 200 (therefore never 206);
- it was not redirected;
- response type is `basic`, `default`, or omitted in the test model;
- canonical key maps to the audio media group;
- normalized `Content-Type` is exactly `audio/mpeg`.

The gate is designed to reject captive-portal HTML, rewrites, opaque responses, missing MIME, and partial bodies. `cacheMatch()` applies the same validation to inherited entries. An invalid hit is deleted and treated as a miss; deletion failure is contained and the invalid response is still never served.

This validates headers and response shape, not audio semantics or a content digest of the body. That is appropriate because canonical filenames are content-addressed and repository generation/QA owns the file. The explicit downloader must not weaken this contract.

## Ordinary cache-first path

For a non-Range MP3:

1. Open the named `popolsku-audio` cache.
2. Match the canonical query-free key.
3. Return a valid warm hit immediately.
4. Otherwise fetch the original full request.
5. Return the network response to playback even if storage later fails.
6. Clone, validate, and schedule the cache write under `FetchEvent.waitUntil()`.
7. After a successful audio write, run retention maintenance.

Write failures are swallowed so storage failure cannot turn working online playback into a playback failure. Bounded diagnostic counters and up to 20 failure records are retained only in worker memory.

The current helper returns only “write scheduled”, not an awaitable success/failure result. That is correct for playback but insufficient for a downloader that must report durable completion. Phase 1 should extract one promise-returning audio-store primitive and keep `cacheWrite()` as the playback wrapper around it. Both ordinary playback and explicit download must call the same primitive.

## Range contract

The worker supports one `bytes` range in `first-last`, `first-`, or `-suffix` form.

| Situation | Result | Cache mutation |
|---|---|---|
| Valid full clip already cached, satisfiable Range | Read cached full body; return synthetic 206 with exact slice, `Content-Range`, sliced `Content-Length`, `Accept-Ranges`, and cached validators | none |
| Valid full clip cached, syntactically valid but unsatisfiable Range | synthetic 416 with `Content-Range: bytes */total` | none |
| Cached header-valid body cannot be read | delete that one entry, send original Range request to network | never store Range result |
| Cache miss | send original request, including Range header, unchanged | none |
| Multiple/malformed/unsupported Range | pass through without interception | none |
| `If-Range` present | conservative pass-through | none |
| Range for non-audio, cross-origin, or non-GET | outside audio policy | none |

The crucial invariant is structural: every Range request is classified before the full-audio branch, and no Range branch invokes `cacheWrite()`. A cold browser media Range can return network 206 but can never poison `popolsku-audio` with a partial representation.

Therefore explicit download must issue worker-owned full GET requests with no `Range` or `If-Range` headers. Programmatically playing 3,621 files is wrong: media elements may choose Range requests, require gestures, allocate decoder/media state, trigger fallback UX, and still fail to populate the full-response cache.

## Retention and capacity

Current constants:

| Constant | Value | Meaning |
|---|---:|---|
| `AUDIO_CACHE_MAX_ENTRIES` | 4,200 | scan/trim threshold |
| `AUDIO_CACHE_TRIM_TO` | 4,000 | target after threshold is crossed |
| `AUDIO_QUOTA_EVICTION_BATCH` | 64 | oldest approved entries dropped before retry |
| `AUDIO_QUOTA_RETRY_LIMIT` | 1 | one retry per failed write |

The policy is insertion-order FIFO, not LRU. `Cache.keys()` order is used, and a hit does not reinsert the entry. Only approved MP3 entries are candidates; shell, unrelated caches, and non-audio entries are not. The just-written exact key is protected.

The current 3,621-file library is 379 entries below the trim target and 579 below the ceiling. A complete clean library therefore safely coexists with count-based retention and leaves about 10.5% headroom to the target / 16.0% to the ceiling relative to current count.

Important nuance: a user may already have legacy or future audio entries not in the active manifest. If those plus the active 3,621 exceed 4,200, normal FIFO trimming can remove older active entries while a full download is underway. A Phase 1 completion check must therefore reconcile after the queue drains. It must never assume “3,621 successful requests” equals 3,621 present entries.

Also, the leading `sw.js` comment still says accumulated clips are “up to ~34MB”; that comment is stale against the measured 51.86 MiB library. It is a documentation risk for the implementation phase, not a Phase 0 product edit.

## Quota recovery and failure behavior

Any failed audio `cache.put` is treated conservatively as storage pressure, regardless of exception name. The worker:

1. opens `popolsku-audio`;
2. enumerates approved audio entries in insertion order;
3. excludes the key being written;
4. deletes at most 64 oldest candidates;
5. retries the same full response once using a spare clone;
6. records and contains a second failure.

This is intentionally not a byte-budget guarantee. `navigator.storage.estimate()` would describe the whole origin and remains advisory. A device can fail before or after an estimate suggests adequate space.

For ordinary playback, a final storage failure remains invisible because the online response still plays. For explicit download, the new promise-returning shared store path must return a typed local result such as `stored`, `already-present`, `bad-response`, `network-failed`, or `storage-failed-after-retry`. It must not expose learner data or send telemetry.

## Cache-entry estimates

`audioEntryEstimate` starts `null` and is a retention trigger, not durable accounting. The first successful new write scans actual keys. Later writes increment the estimate until the threshold forces another scan. Replacements can over-count temporarily, but every trim resets from real keys.

Explicit reconciliation and Remove must be worker-owned or must explicitly reset this estimate. Deleting `popolsku-audio` directly from the page while the active worker retains a non-null estimate would make its next retention decision stale.

## Required Phase 1 refactor boundary

Extract, without changing semantics:

- `storeValidatedAudio(key, response)` → promise that validates, clones as needed, performs `cache.put`, retention, one-shot recovery, and resolves with an explicit outcome;
- existing `cacheWrite(event, AUDIO_CACHE, key, response)` → schedules that promise and preserves ordinary playback’s swallow/return behavior;
- message-command download → fetches a complete approved same-origin MP3 and awaits the same store promise;
- reconciliation → applies the same key and response validation and evicts invalid exact hits;
- removal → deletes only `popolsku-audio` and sets `audioEntryEstimate = null`.

Do not add a second cache, direct page `cache.put`, ZIP, IndexedDB blob copy, or partial-response exception.

## Existing executable evidence

`tests/test_phase4b3_audio_resilience_range_storage.js` executed 558 passing behavior assertions in this audit. Its five failures are historical release-lock assertions expecting shell `v66`, app `8.11`, and 3,377 clips; the behavioral Range/cache/retention/quota assertions passed and the test itself reported the current 579-entry headroom. `tests/test_audio_fallback.js` passed 585/585 and `tests/test_audio_failure_inline_feedback.js` passed 38/38.

One Python suite likewise exposed a historical `APP_VERSION = 8.13` lock, not a current audio-integrity failure. `python3 verify_audio.py` passed the current 3,621/3,621/3,621 reconciliation.
