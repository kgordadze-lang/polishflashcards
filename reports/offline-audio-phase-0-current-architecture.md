# Offline Pronunciation Download — Phase 0 current architecture

## Scope and repository proof

This is a reports-only audit. It does not implement downloading and does not alter the product, tests, content, manifest, audio, generated pages, versions, or caches.

| Item | Verified value |
|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Codex - Offline Audio Phase 0` |
| Branch | `offline-audio-phase-0-audit` |
| Starting commit | `b97bc8af090acf339f4902954b51354eac9fb512` |
| Starting tree | `486f4c0ddbed5ecca48e23cc227b13580a222a77` |
| Starting worktree | clean |
| Git remotes | none |
| `push.default` | `nothing` |

The expected value supplied for the “starting Git tree” is the tree object of the starting commit, not the commit object itself. `git show -s --format='%H%n%T' HEAD` establishes that relationship exactly.

No production site, deployment, remote repository, or disallowed local repository was accessed.

## Independently verified audio inventory

The repository contains:

- 3,621 unique required normalized utterances (`python3 verify_audio.py`);
- 3,621 manifest entries;
- 3,621 unique manifest file paths;
- 3,621 non-empty `audio/*.mp3` files;
- 0 missing manifest files;
- 0 orphaned manifest entries or MP3 files;
- 54,378,576 MP3 bytes = 51.859451 MiB, suitable for learner copy as “About 52 MB”.

The MP3 size range is 8,928–42,048 bytes, with a mean of 15,017.56 bytes. These are payload bytes only; browser storage accounting and transfer overhead can be higher.

`verify_audio.py` also independently reports the source breakdown as 647, 997, 615, 627, 95, 289, and 215 phrases from the seven `data-*.js` files plus 269 Verb Patterns pronunciations, de-duplicated to 3,621 required phrases.

The protected Verb Patterns content remains 98 lemmas, 129 meanings, 269 patterns, 269 examples, and 269 pronunciation-eligible examples. No content edit is part of this feature.

## Manifest contract

[`audio-manifest.json`](../audio-manifest.json) is a JSON object with four top-level fields:

```json
{
  "audioDir": "audio",
  "voice": "pl-PL-MarekNeural",
  "generatedAt": "2026-08-27T15:22:52.769972Z",
  "entries": {
    "000311d1288f": {
      "pl": "dowód osobisty",
      "file": "audio/000311d1288f.mp3"
    }
  }
}
```

`entries` is a dictionary keyed by the first 12 hexadecimal characters of SHA-256 over the normalized Polish utterance. Each value has exactly the learner text in `pl` and its relative `file`. `verify_audio.manifest_integrity_problems()` checks the digest/key relationship, canonical `audio/<key>.mp3` path, normalized uniqueness, presence, and non-empty file.

All 3,621 canonical URLs are obtained without inventing another index: enumerate `Object.values(manifest.entries)`, require a non-empty string `file`, resolve it against the application scope, and accept it only if the resulting URL is same-origin and its canonical path matches `/audio/[a-f0-9]+\.mp3`. The service worker must repeat that trust-boundary validation.

The 3,621 file values and normalized utterances are unique. JSON insertion order is not lexicographically sorted and is not a semantic contract. The generator preserves the loaded dictionary and appends newly discovered entries in deterministic content-discovery order. Download correctness must be set-based; manifest order can be used merely as a deterministic queue order.

The current file SHA-256 is `09f038097c118c6c55c00f15185a5e4207d02f103480675ad0b3a499ab3ad0a7`, but a deploy must not hard-code it. `generatedAt` is also unsuitable as semantic identity because regeneration can change it without changing the URL set. If a cached UI summary is later useful, derive an identity from the sorted canonical file-URL set (plus count); never use that summary as proof of completion. No new manifest field is required for Phase 1.

## Runtime playback path

[`index.html`](../index.html) fetches `audio-manifest.json` at startup with `cache: "no-store"`. The service worker treats the manifest network-first and supplies its precached copy offline. The page builds `audioMap` from normalized `pl` to relative `file`; only the loading state disables affected controls.

On learner activation:

1. `speakText()` stops the prior owner and resolves the normalized phrase in `audioMap`.
2. A mapped phrase creates a fresh `Audio(file)` and calls `play()`.
3. A successful ordinary full GET is cache-first in `popolsku-audio`; a cold response is validated and stored asynchronously.
4. MP3 failure falls back once to browser `speechSynthesis` and announces “Using your device's voice.”
5. If that route is missing or fails, the shared polite/atomic status says “Audio couldn't play. Check your connection, then try again.” and exposes a native Retry button.
6. Attempt ownership and settled latches suppress duplicate and stale error callbacks.

This matches the physical-device observation: a previously played clip works in flight mode; an unplayed clip does not. The cache mechanism is working. The missing product capability is intentional whole-library acquisition.

## Current offline and lifecycle behavior

- The shell and manifest are available offline after successful service-worker installation.
- Generated guide/grammar/vocabulary pages are cached as visited, not all at once.
- MP3s are lazy, immutable, cache-first assets stored outside the versioned shell cache.
- `popolsku-audio` survives numbered shell-cache activation cleanup.
- The worker does not call `skipWaiting()` or `clients.claim()`.
- The page already requests persistent storage opportunistically after meaningful engagement or immediately in installed display mode. Denial is silent and non-blocking.
- `navigator.onLine` is used only as an optimization before an update HEAD check; it is not proof that audio can be fetched.
- There is no current use of `navigator.storage.estimate()` and no download/background API.

## Navigation and recommended placement

The home-screen menu is an accessible modal drawer with About, Install, Privacy, listening/guide links, and Contact. About, Privacy, Contact, and Install are in-app screens using the existing history/focus/scroll contract. There is no general Settings screen.

The natural minimal addition is a dedicated in-app screen named **Offline audio**, linked from the menu near Install. It is intentional, discoverable, and keeps a ~52 MB action out of ordinary study, Listening, Verb Patterns, and search flows. It should reuse the existing screen header/back/home and routing contracts.

Privacy currently accurately describes lazy audio. A future implementation release will need copy consistency review, but Phase 0 makes no privacy or product edits and adds no analytics, telemetry, identifiers, cookies, or endpoints.

## Completion definition

“Pronunciation audio available offline” means:

> Every canonical MP3 URL in the active, usable audio manifest has an exact canonical cache entry in `popolsku-audio` that satisfies the service worker’s full-response validation contract.

Today, a valid stored representation means status 200, `ok`, non-redirected, basic/default response, and `Content-Type: audio/mpeg`. Status 206 can never qualify. Completeness is inferred safely from the only approved write path: Range responses are structurally excluded, while accepted full requests are status 200. Re-reading all 52 MB merely to display status is neither necessary nor desirable.

Reconcile when the Offline audio screen opens and after downloader/removal mutations, not on every app render. Enumerate real cache keys, intersect them with the current manifest URL set, and validate candidate responses through shared worker logic. In-memory UI state is a view of that result, never the durable source of truth.

## Future growth

If a future manifest grows from 3,621 to 3,680 canonical files, the versionless content-hashed cache preserves the original matching entries. Reconciliation reports `3,621 of 3,680 available offline` and 59 missing. **Update offline audio** queues only those 59. Nothing requires deleting or redownloading the existing 3,621.

The manifest revision is therefore the canonical URL set itself. Content hashes provide clip identity; the cache provides presence truth.

## Phase 0 decision summary

- Keep `audio-manifest.json`, `audio/<hash>.mp3`, `popolsku-audio`, and the existing playback path.
- Add a worker-mediated, acknowledged full-response store operation in Phase 1.
- Reconcile against Cache Storage, not a localStorage completed flag.
- Use concurrency 3, with pause stopping new scheduling and allowing at most three in-flight writes to settle.
- Do not promise background downloading on iPhone or permanent storage anywhere.
- Remove means clearing the shared pronunciation cache after confirmation; ordinary playback warms it again.
