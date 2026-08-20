# Priority 8 Phase 0 — audio architecture audit

## End-to-end ownership

1. `pp_audio_rule.py` is the build/check source of truth for which current `data-*.js` strings require audio. It parses every `PP_LEVELS.push(...)`, selects standard-card `pl`, complete template `audioText`, and every `ex`, `full` and `npc`, then normalizes and ordered-de-duplicates.
2. `generate_audio.py` consumes that list, computes the content name, reuses non-empty files, synthesizes only missing files with `pl-PL-MarekNeural`, and writes the manifest. Its optional prune removes stale manifest entries but only lists orphan files.
3. `verify_audio.py` consumes the same rule and checks both directions: every required phrase has a manifest entry/non-empty file, and every manifest/file key is live.
4. `index.html` mirrors the rule through `PP_USAGE.mainAudioText()` and normalizes requested playback through `ppNormalize()`.
5. `audio-manifest.json` is fetched once at startup with `cache:"no-store"`; usable values become a normalized-text → file map.
6. The shared `speakText()` engine owns one current HTML audio element or one current speech utterance. All controls route through it.
7. `sw.js` handles the manifest network-first, hashed MP3s cache-first in the versionless `popolsku-audio` cache, and warm single-byte Range requests as exact 206 responses.

Verb Patterns are not currently discovered by `pp_audio_rule.py`, because the rule only reads `data-*.js`. The released runtime carries `audioEligible`, but all values are false. The loader validates the field, then its derived view currently drops it; `pRenderLemma()` renders only Polish/English text and no control.

## Exact normalization and naming

Normalization is identical in Python and browser JavaScript:

1. remove substrings matching `<[^>]+>`;
2. replace every whitespace run with one ordinary space;
3. trim leading/trailing whitespace.

It does not lowercase, change punctuation, normalize Unicode, expand numbers/abbreviations or remove diacritics. The filename key is `sha256(normalized UTF-8)[:12]`. The manifest is an object keyed by that 12-hex ID; each value is `{"pl": normalized text, "file": "audio/<id>.mp3"}`.

The full manifest has no normalized duplicates, key/hash mismatch, file-path mismatch or zero-byte file. A 48-bit truncated name has a theoretical collision possibility, so future tooling must continue rejecting a key that resolves to different text rather than overwriting it.

## Playback, switching and error state

- Every new request starts with `stopAllAudio()`: pause current MP3, invalidate the current utterance, cancel speech synthesis, remove speaking state, clear stale status and replace retry ownership.
- MP3 playback uses a fresh `Audio(file)`, the shared Normal/Slow rate and pitch preservation.
- A per-attempt `settled` latch prevents the same failed clip’s `error` event and rejected `play()` promise from launching two fallbacks.
- Current-object identity prevents superseded audio, late aborts and stale speech events from clearing or speaking over the new request.
- A failed clip gets exactly one device speech-synthesis fallback and a polite “Using your device's voice” status. If neither path works, the shared live region exposes a “Try again” button.
- Retry returns focus to the initiating control before replacing the status. Playback never changes score, question index, progress or focus otherwise.
- Several visible buttons are safe because there is a single playback owner. Rapid switching is cancel-and-replace, never overlap.

## Accessibility and offline behavior

Existing controls receive contextual `aria-label` values such as “Play example sentence: <Polish>”. Buttons use native keyboard semantics. Playing state is visual; failures are also textual in an atomic polite live region. Hidden controls leave neither layout nor tab stops. Verb Patterns already have width-agnostic wrapping, 44px targets, language tagging and no local animation; a control must preserve those properties. The global speaking animation is suppressed by the existing reduced-motion media rule.

The shell precaches the manifest and Verb Patterns runtime. A previously fetched MP3 is available offline from `popolsku-audio`; an unwarmed clip falls through to the network, then to device voice/failure status. “Offline” therefore guarantees the reference and manifest, not every one of 3,377 clips.

## Service-worker details

- Runtime and manifest: network-first with cached offline fallback.
- MP3: cache-first after MIME/status/redirect validation.
- Range: warm validated full body → correct 206 slice; bad satisfiable form → network passthrough; unsatisfiable valid range → 416; partial network bodies are never cached.
- Retention: ceiling 4,200 entries, FIFO trim target 4,000, current headroom 823; cache hits do not claim LRU behavior.
- Quota recovery: evict at most 64 approved audio entries and retry one write once.
- Activation deletes only numbered shell caches and preserves `popolsku-audio`; there is intentionally no `skipWaiting()` or `clients.claim()`.

## Smallest maintainable future change set

A future Phase 1 should:

1. approve one clarified invariant: `audioEligible` authorizes pronunciation playback; Listening still separately requires `activityEligibility:["listening"]`;
2. update the existing governance/runtime validators and tests for that one-way rule (Listening ⇒ approved audio, but audio ⇏ Listening);
3. carry `audioEligible` through the existing `pp-verb-patterns.js` derived example view;
4. extend the one `pp_audio_rule.py` required-set implementation to ingest eligible examples from the official validated runtime/release projection, and let generator/verifier/validator continue consuming that single function;
5. add one existing-style `.mini-audio` button beside an eligible example in `pRenderLemma()`, named through `ppSetAudioControlName()` and played through `speakText()`;
6. reuse 20 clips, generate only the 25 approved missing utterances, perform human audio QA, then update the manifest/audio files;
7. add deterministic tests for discovery, collision refusal, playback ownership, offline/Range/failure/accessibility.

This is an extension of the existing parser, renderer and player paths. No second audio component, preview source, fallback runtime or hand-built manifest is justified.
