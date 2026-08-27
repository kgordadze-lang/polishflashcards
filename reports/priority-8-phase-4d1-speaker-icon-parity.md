# Priority 8 Phase 4D1 — Verb Patterns speaker-icon parity

## Starting endpoint

This checkpoint started on `priority-8-phase-4c-architecture` at
`00362a66e2e3984f73f9eeebf70ecef4b1e3ecb7`, tree
`d8b6c855c575e1c96d4ddd30f7c1ae96232e0288`, parent
`63a13767450246d9a22f6d883a4d86b4a173b95a`, subject `Priority 8 Phase 4D
release Verb Patterns runtime`. The worktree was clean; no remotes were
configured, `push.default` was `nothing`, and the fail-closed pre-push hook was
executable.

## Root cause and correction

`pRenderLemma(entry)` created eligible Verb Patterns example buttons with the
established `mini-audio vp-example-audio` classes, shared `data-say` player
route, shared accessible-name helper, and manifest readiness gate. Its visible
content alone differed: it assigned the Unicode speaker emoji `🔊` through
`audio.textContent`.

The application already defines `G_AUDIO`, the monochrome outline speaker SVG
using `stroke="currentColor"`, and uses it in established `mini-audio`
controls. Phase 4D1 replaces only the Verb Patterns assignment with
`audio.innerHTML = G_AUDIO;`. No new icon or SVG constant was introduced.

The now-obsolete emoji-specific `font-size:16px` was removed from
`.vp-example-audio`. Its existing 44px button dimensions and layout remain;
the shared `.mini-audio svg { width:15px; height:15px }` rule supplies the
icon size.

## Behavioural parity

- Normal, hover, and focus: Verb Patterns uses the exact shared outline SVG and
  inherits `currentColor`, including the existing hover foreground/background.
- Speaking: the unchanged `.mini-audio.speaking` selector recolours the SVG and
  retains the existing pulse.
- Loading: `syncPatternAudioReadiness` and the renderer's loading-only disabled
  assignment are unchanged.
- Failure and retry: the shared audio status/retry route is unchanged.
- Speech fallback: `speakText`, `playPreGenerated`, and `speakFallback` remain
  unchanged. An eligible sentence with no MP3, including `Biorę udział w
  konferencji.`, stays enabled after settlement and reaches the existing device
  speech fallback through the same `data-say` click delegate.
- Accessibility: `ppSetAudioControlName(audio, "Play example sentence",
  pattern.example.pl)` is unchanged, so the meaningful generated accessible
  label remains intact.

## Browser smoke

The local app was opened in the available browser at `http://127.0.0.1:8765/`.
`gotować`, `brać`, and `wziąć` all rendered `.mini-audio.vp-example-audio` with
the shared `24×24`, `fill="none"`, `stroke="currentColor"` SVG, sized by the
shared rule to 15px inside the unchanged 44px target. No emoji text was present.
The browser confirmed the generated meaningful label and encoded `data-say`.
Hover preserved `currentColor` through the SVG. The missing-MP3 example `Biorę
udział w konferencji.` was enabled after manifest settlement, entered the
existing `.speaking` state on activation, and exposed no retry failure. Audible
device speech remains a manual check; this browser smoke does not claim to have
heard it.

## Immutability and verification

`content/verb-patterns.json` remains byte-identical at SHA-256
`66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`.
`APP_VERSION` remains `8.13`; the shell cache remains `popolsku-v68`; and
`AUDIO_CACHE` remains `popolsku-audio`. No audio files or manifest, production
content, activity eligibility, loader semantics, governance, migration data, or
service worker were changed.

The dedicated `tests/test_priority8_phase4d1_speaker_icon_ui.py` checks shared
SVG reuse, emoji removal, class and data wiring, accessible naming, readiness,
shared SVG/hover/speaking styling, audio-player/fallback routing, version/cache
markers, and the production-data SHA.

| Gate | Result before this commit |
|---|---|
| `python3 validate_priority8_staging.py` | PASS before and after the edit |
| 16 governed Priority 8 suites at a clean starting endpoint | 483/483 PASS |
| Phase 4C4C1 parity | 5/5 PASS |
| Phase 4C4C release freeze | 78/78 PASS |
| Phase 4D1 speaker-icon suite | 5/5 PASS |
| Migration JXA suite | 121/121 PASS |
| Audio fallback JXA suite | 585/585 PASS |

The post-edit, pre-commit governed run was 482/483. Its one failure was the
expected Phase 4C3 clean-worktree sentinel, which reported exactly the three
authorized Phase 4D1 paths. No product assertion failed. The clean post-commit
run is required to return that sentinel and the governed total to 483/483.

`tests/test_priority8_phase1_playback.js` remains a historical Phase-1 snapshot
and was not modified. It fails against the legitimate 4D release state at its
old 45-example, cache-v67, APP_VERSION-8.12, and emoji locks; it is not a
Phase 4D1 product regression gate.

## Phase 4D2 handoff

Phase 4D1 is a view-layer-only checkpoint. It neither generates nor changes
audio. Audio generation remains blocked pending independent verification of
this committed endpoint.
