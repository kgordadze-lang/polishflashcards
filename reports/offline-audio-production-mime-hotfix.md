# Offline Audio production MIME hotfix

Date: 16 September 2026
Branch: `fix/offline-audio-production-mime`

## Repository and production starting point

This disposable repository was confirmed before the change as:

- path: `/Users/Kaj/Downloads/Repository for Codex - Offline Audio MIME Hotfix`;
- production-derived starting commit: `4b577f094c7c0096fc6de3938652edf577dd0d80`;
- starting tree: `79e720f77a0cb2b831dd2ddcc113d6b4da0902a4`;
- clean worktree;
- zero configured remotes;
- `push.default=nothing`.

The production repository at `/Users/Kaj/Documents/GitHub/polishflashcards` was
never accessed. Nothing was pushed or deployed.

## Production failure and evidence

Post-release-9.16 smoke testing showed Offline Audio failing on both iPhone and
Mac with `0 of 3,621` pronunciations available and the learner-facing
`Download incomplete` message.

The supplied browser evidence for a canonical production MP3 was:

- status `200` and `ok: true`;
- response type `basic`;
- `redirected: false`;
- `Content-Type: audio/mp3`.

The supplied curl evidence for the same production asset was HTTP/2 `200`,
`content-type: audio/mp3`, and `content-length: 13248`. The network and payload
therefore succeeded; the worker rejected the response at its MIME gate.

## Root cause and fix

`sw.js` used the shared media allowlist:

```js
audio: ["audio/mpeg"]
```

The production host serves canonical `.mp3` files as `audio/mp3`. The shared
`isCacheableResponse()` check consequently rejected every production clip,
causing the explicit downloader to reach its bounded bad-response threshold
without storing an entry.

The allowlist is now exactly:

```js
audio: ["audio/mpeg", "audio/mp3"]
```

`audio/mp3` is accepted because it is the normalized media type observed on a
successful canonical production response. Acceptance was not broadened to
`audio/*`, `application/octet-stream`, absent Content-Type, or extension-only
validation.

This is a change to the existing shared validator. There is no downloader-only
exception and no duplicated MIME check. Ordinary lazy warming and explicit
Offline Audio storage both reach `storeValidatedAudio()`; explicit download
also performs the same validation immediately before queueing the write; and
reconciliation validates cached entries with `isCacheableResponse()`.

All other gates remain unchanged: canonical approved audio key, same origin,
status `200`, `response.ok`, not redirected, `basic`/`default` response type,
and a complete response. HTML, malformed, opaque, redirected, cross-origin,
noncanonical, bad-status, untyped, and unexpected-media responses remain
rejected.

## Range safety

Range architecture was not changed. A warm valid full MP3 can still produce a
synthetic `206`; a cold Range request still passes through to the network; and
a `206` response still fails the status-200 full-storage gate regardless of
whether its Content-Type is `audio/mpeg` or `audio/mp3`. No partial response is
written to `popolsku-audio`.

## Deterministic regression coverage

The Phase 1 shipping-worker harness now proves locally that:

1. canonical status-200 `audio/mpeg` remains accepted;
2. canonical status-200 `audio/mp3` is accepted by `isCacheableResponse()`;
3. `storeValidatedAudio()` stores that `audio/mp3` response through the shared gate;
4. `offline-audio-store-one` stores a production-style `audio/mp3` response;
5. reconciliation counts a valid cached `audio/mp3` entry as present;
6. ordinary lazy warming stores `audio/mp3`;
7. status `206` plus `audio/mp3` is rejected from full storage;
8. redirected `audio/mp3` is rejected;
9. cross-origin and noncanonical audio keys are rejected;
10. `text/html` is rejected;
11. `application/octet-stream` is rejected;
12. missing Content-Type is rejected;
13. bad status is rejected;
14. the existing `audio/mpeg` path remains green.

The fixtures are deterministic and local. There is no runtime or test
dependency on the live host.

## Validation results

Required Offline Audio suites:

| Command | Result |
|---|---:|
| `osascript -l JavaScript tests/test_offline_audio_phase1_engine.js` | 102 passed, 0 failed |
| `osascript -l JavaScript tests/test_offline_audio_phase2_ui.js` | 104 passed, 0 failed |
| `osascript -l JavaScript tests/test_offline_audio_phase3_integration.js` | 50 passed, 0 failed; nested Phase 1 102/0 |

Maintained affected-area suites:

| Area / command | Result |
|---|---:|
| `tests/test_audio_fallback.js` | 585 passed, 0 failed |
| `tests/test_audio_failure_inline_feedback.js` (includes Audio Status Layout) | 38 passed, 0 failed |
| `tests/test_phase4b3_audio_resilience_range_storage.js` | 554 passed, 9 historical frozen failures |
| `tests/test_priority8_phase1_playback.js` | 25 passed, 0 failed |
| `tests/test_listening_accessibility.js` | 229 passed, 0 failed |
| `tests/test_listening_variety.js` | 193 passed, 0 failed |
| `tests/test_priority8_phase4f1_verb_patterns_search.py` | 11 behavioral tests passed, 1 historical frozen app-8.13 scope assertion failed |

The resilience suite remains at the release-9.16 documented `554/9`
historical baseline: its failures pin app `8.11`, shell `v66`, the old 3,377
inventory, and pre-Offline-Audio source shapes. The historical Priority 7
patterns UI suite also still aborts on its removed
`p7-fixture-card-001` fixture, as documented for release 9.16. No frozen
assertion was weakened or rewritten to manufacture a green result. Current
Offline Audio and Priority 8 behavioral replacements are green.

Repository validators:

| Command | Result |
|---|---|
| `python3 validate_content.py` | passed: 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline intact |
| `python3 verify_audio.py` | passed: 3,621 required, 3,621 manifest entries, 3,621 MP3s, zero missing/orphaned |
| `python3 validate_priority8_staging.py` | passed: staging revision 8 remains read-only valid |
| `python3 build_pages.py --check` | passed: committed generated output is current |
| `git diff --check` | passed |

Direct protected-data inspection confirms Verb Patterns remains 98 lemmas,
129 meanings, 269 patterns, 269 examples, and 269 audio-eligible examples.

## Release markers

The repository's service-worker convention explicitly separates the technical
shell-cache generation from the learner-visible app version. Because this
hotfix changes worker caching behavior without changing learner-visible product
content:

- `APP_VERSION` remains `9.16`;
- `CACHE` advances from `popolsku-v71` to `popolsku-v72` so clients fetch a new
  worker/cache generation;
- `AUDIO_CACHE` remains exactly `popolsku-audio`, preserving downloaded audio.

No generated page output was changed; `build_pages.py --check` confirms none is
required.

## Change scope

Files changed by the hotfix:

- `sw.js` — one MIME allowlist addition and one shell-cache generation bump;
- `tests/test_offline_audio_phase1_engine.js` — focused production MIME and
  shared-path regressions plus the current cache marker;
- `tests/test_offline_audio_phase2_ui.js` — current cache marker;
- `tests/test_offline_audio_phase3_integration.js` — current cache marker and
  exact expanded Phase 1 assertion count;
- `reports/offline-audio-production-mime-hotfix.md` — this evidence report.

No manifest, MP3, learning content, pronunciation eligibility, Listening
eligibility, copy, scheduler, capability protocol, privacy model, or analytics
behavior changed.
