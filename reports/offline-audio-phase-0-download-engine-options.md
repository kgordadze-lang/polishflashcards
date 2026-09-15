# Offline Pronunciation Download — engine options and recommendation

## Decision

Recommend a **page-orchestrated, active-service-worker store protocol**:

- the page owns UI, queue intent, pause, and a concurrency limit of 3;
- the active worker owns URL approval, complete network fetch, validation, cache write, retention, quota recovery, reconciliation, and removal;
- every item operation acknowledges durable outcome;
- Cache Storage plus the active manifest remains the only completion truth.

Use the existing `audio-manifest.json`, content-hashed MP3 URLs, and `popolsku-audio`. Do not introduce another storage or playback architecture.

## Options compared

| Option | Benefits | Material problems | Decision |
|---|---|---|---|
| Page `fetch()` of every full MP3; existing fetch handler writes | Minimal new worker surface; ordinary controlled pages inherit validation/retention/quota | First uncontrolled visit bypasses worker; page fetch resolves before asynchronous `cache.put`; current write failures are swallowed, so progress cannot mean durable storage; pause/reload races require repeated cache polling | Reject as primary engine |
| Page sends approved URLs/requests to active worker; worker fetches/stores | Works through `registration.active` even before the page is controlled; can await exact shared store result; centralizes trust, quota, estimate reset, removal, and diagnostics | Requires a small message protocol and refactoring current write helper to return a result | **Recommend** |
| Page directly opens cache and `cache.put()` | Simple acknowledgements | Duplicates/bypasses worker validation, retention, quota recovery, invalid eviction, and entry estimate; creates two writers | Reject |
| Worker downloads all 3,621 in one message/event | Central ownership | Fragile long-lived worker/session, slow pause, poor iPhone lifecycle fit, large failure domain | Reject |
| Programmatically play every clip | Reuses playback UI superficially | Gesture/media/Range/decoder issues, audible/UX side effects, partial requests never cache, slow and unreliable | Reject |
| ZIP download/extract | Fewer requests | New artifact/build/deployment/extraction path; double storage risk; no natural Cache API identity; updates become coarse | Reject |
| IndexedDB blobs | Explicit database state | Duplicates MP3 bytes and playback architecture; extra quota/schema/migration/removal work | Reject |
| Second manifest/cache/library | Isolation | Drift, duplicate storage, update and ownership complexity | Reject |

## Why ordinary page fetch is not sufficient

Calling `fetch(fullUrl)` from a currently controlled page would reach the existing non-Range audio branch and is safer than direct `cache.put`. However, the worker returns the network response while its cache write continues under `waitUntil`; `cacheWrite()` deliberately swallows write/quota failure. Page-level fetch success therefore means “bytes arrived”, not “available offline”.

The page could poll Cache Storage after every request, but then it still duplicates validation and is coupled to whether the page is controlled. An explicit feature deserves a durable acknowledgement from the component that performs the write.

## Minimal worker protocol

Use structured local messages only; no endpoint, telemetry, identifier, or analytics.

### `offline-audio-reconcile`

Input: the current manifest’s file values (or canonical URLs) and a request token meaningful only to this page instance.

Worker behavior:

1. Validate array/count bounds.
2. Resolve and canonicalize every entry within worker scope.
3. Reject cross-origin, query-bearing/noncanonical, duplicate, or non-hashed MP3 requests.
4. Open only `popolsku-audio`.
5. Enumerate stored keys once and intersect exact canonical keys with manifest keys.
6. For candidates, apply the shared response validation; evict invalid hits.
7. Return total, valid-present canonical URLs (or missing URLs), invalid count, and no bodies.

For a 3,621-file set, returning the missing list is acceptable but should remain bounded by the validated manifest count. The UI derives counts; it does not trust arbitrary worker URLs.

### `offline-audio-store-one`

Input: one canonical candidate URL and ephemeral request token.

Worker behavior:

1. Revalidate same origin, scope, canonical exact path, and hashed MP3 pattern.
2. Check for an exact valid cached response; return `already-present` if found.
3. Construct a full GET with no `Range`/`If-Range` and fetch it directly from the worker.
4. Require the existing full-response gate.
5. Await the extracted shared audio-store promise, including retention and one quota recovery.
6. Recheck the exact key if necessary and return `stored`, `bad-response`, `network-failed`, or `storage-failed`.
7. Bind the operation to the message event with `waitUntil`, but keep it one small file, not the whole library.

The page keeps at most three such operations outstanding. A `MessageChannel` reply per operation avoids global listener ambiguity. Tokens prevent stale replies from an earlier screen/session changing current UI; they are in-memory correlation values, not persistent identifiers.

### `offline-audio-remove`

Worker behavior: after explicit page confirmation, delete exactly `popolsku-audio`, set `audioEntryEstimate = null`, and return success/failure. Never touch the versioned shell or localStorage progress.

## Shared write refactor

The implementation should have one internal promise-returning primitive with these unchanged semantics:

```text
approved key + valid status-200 audio/mpeg response
    -> cache.put(full response)
    -> afterAudioWrite / FIFO retention
    -> on put failure: evict up to 64 approved oldest entries
    -> retry once with spare clone
    -> typed result
```

The existing fetch path wraps it, calls `event.waitUntil`, and continues returning the online response independent of storage. The message path awaits it and reports the typed result. This is reuse of the exact write path, not a parallel approximation.

Phase 1 tests must prove that both callers reach the same primitive and that Range responses cannot reach it.

## Resume and state architecture

1. Offline screen opens in **checking cache**.
2. Load/use the active manifest and derive the unique canonical URL set.
3. Ask the worker to reconcile actual exact valid cache entries.
4. Render `present / total`; calculate missing set.
5. On Download/Continue/Update, optionally request persistence and schedule missing URLs with concurrency 3.
6. Each acknowledged durable result updates the session view. Network/storage failures stop or bound further scheduling as specified below.
7. Pause, navigation away, visibility loss, restart, or worker termination may end scheduling.
8. On re-entry/restart, discard old counters and reconcile again.
9. After apparent completion, perform a final reconciliation. Only exact total equality renders Complete.

No localStorage `completed` flag is needed. If a later optimization stores `{manifestSetIdentity, presentCount, checkedAt}`, it is display-cache only and must never skip reconciliation when entering the Offline screen after restart, manifest change, removal, quota recovery, or error.

## Pause, cancel, and navigation

Pause is cooperative:

- immediately set queue state to paused;
- schedule nothing new;
- allow at most three in-flight full requests/writes to finish;
- accept their acknowledgements and update the retained count;
- render “Download incomplete” / “Continue download”.

Do not use `AbortController` in the minimal release. Files are small, and settle-not-abort yields simpler durable state. Remove is a separate confirmed destructive action and must first stop scheduling, wait for current operations to settle or invalidate their session token, then execute worker-owned deletion. A late store reply must not resurrect Complete after Remove; worker serialization or a generation token should make ordering deterministic.

Leaving the Offline screen should behave like Pause. It must not steal focus, show a global download overlay, or promise background completion. Returning reconciles and continues on learner action.

## Failure policy

- **Network failure:** after a small threshold (recommended first failed wave or 3 consecutive failures), stop scheduling, drain in-flight work, reconcile, show partial state and Continue.
- **Bad response:** record the affected file locally for the session, continue other files up to a bounded error count, finish incomplete, and offer Retry. Never cache it.
- **Storage/quota failure after worker retry:** stop immediately, drain, reconcile, show storage failure and retained count.
- **Worker/channel loss:** transition to interrupted, then reconcile when a worker is available.
- **Manifest changes mid-session:** pin the queue to the manifest set loaded for that session; on next entry or final reconciliation, load active manifest again and present any delta as Update.

Do not infer network truth from `navigator.onLine` and do not turn an individual failure into deletion of valid cached work.

## Manifest identity and update behavior

The canonical manifest identity is a deterministic digest/fingerprint over the **sorted unique canonical URL set**, not JSON insertion order or `generatedAt`. Cryptographic hashing is optional for a UI summary; the actual set comparison is authoritative and needs no new manifest revision field.

Example release growth:

```text
old cached set: 3,621
new manifest set: 3,680
intersection: 3,621
missing: 59
```

Render `3,621 of 3,680 available offline`, `59 new pronunciations available`, and **Update offline audio**. Queue only the 59 missing URLs. Removed historical manifest entries may remain in the shared cache until FIFO pressure or Remove; they do not count toward completion. A later optional maintenance policy could delete nonmanifest entries, but it is unnecessary and risks surprising loss of naturally warmed future/legacy audio.

## Remove semantics

Because deliberate downloads and ordinary warm playback share `popolsku-audio`, the clearest behavior is:

> Remove all saved pronunciation audio on this device. Pronunciations will be saved again as you play them online.

After confirmation, delete the whole pronunciation cache. This removes both intentionally downloaded and naturally warmed clips. Do not create per-file ownership metadata: it adds state and ambiguity without meaningful learner value for a ~52 MB all-or-nothing library control.

After success, reconcile/render not downloaded and announce completion politely. On deletion failure, retain the actual state and show Retry; never claim removal based only on the API call being scheduled.
