# Offline Pronunciation Download — Phase 2 learner UI

## Scope and starting repository proof

Phase 2 adds the learner-facing Offline audio screen and connects it to the approved Phase 1 engine. It does not release, deploy, generate audio, change content, or modify the worker engine.

| Item | Verified starting value |
|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Codex - Offline Audio Phase 2` |
| Branch | `offline-audio-phase-2-ui` |
| Starting commit (`HEAD`) | `3a5b27ff4ae34a4aea09cef50fa8228fc789a166` |
| Starting tree (`HEAD^{tree}`) | `ecd512b3abbf0445dd3893a251b4518a12d42f20` |
| Starting worktree | clean |
| Git remotes | none |
| `push.default` | `nothing` |

The supplied expected value is the tree object, not the commit object, and matched `HEAD^{tree}` exactly. All nine required Phase 0/1 reports were read before product editing. No production site, deployment target, remote repository, or disallowed local repository was accessed.

## Screen and menu placement

`index.html` now contains one real `.screen` with `id="offlineAudio"`, headed **Offline audio**. Its shared header contains the established Back and Home controls. The site drawer contains one **Offline audio** link immediately after Install and before Privacy. Activating that link only routes to the screen; it cannot start a download.

`#offlineAudio` is included in the same direct-hash startup allowlist as About, Privacy, Contact, and Install, with the same marked history entry, focus routing, manual scroll restoration, Back, and Home behavior. Browser inspection uncovered and fixed a pre-existing lexical-initialization hazard in direct informational hash startup: `stopAllAudio()` could run before idle audio ownership/status variables initialized. Those idle references are now hoisted `var` state, preserving their null/undefined idle semantics and allowing all direct informational routes to use the shared router successfully.

No Offline audio prompt, badge, count, or action was added to study, Listening, Verb Patterns, Grammar, search, completion screens, or the install banner.

## Manifest integration

The existing startup `audio-manifest.json` request is now wrapped in one small reusable `loadAudioManifest(force)` function:

- startup still issues exactly one `cache: "no-store"` request;
- ordinary pronunciation still builds and uses `audioMap` from normalized `pl` values;
- the same successfully loaded manifest retains `Object.values(entries).map(entry => entry.file)` separately for Offline audio;
- the UI passes those file values through `PPOfflineAudioEngine.prepareManifest()`, which remains the canonical validator/deduplicator;
- any malformed or empty offline inventory fails the optional capability closed without changing ordinary speech-synthesis fallback;
- only an explicit learner Retry after manifest failure can force one new request for the same manifest;
- there is no polling, second manifest, duplicate generated list, hard-coded 3,621-file array, or manifest-derived persistent version flag.

If a successful explicit reload yields a different canonical URL set, the controller pauses the old active instance if needed, invalidates its callback identity, creates an engine for the new set, and reconciles without starting a download.

## Controller and screen-entry truth

The inline `PPOfflineAudioUI` controller owns only the active/reused engine reference, manifest-set identity, rendering, live-announcement milestones, screen lifecycle, persistence request, and confirmation flow. It never opens or mutates Cache Storage.

Every entry:

1. renders Checking;
2. obtains the active loaded manifest set;
3. validates/canonicalizes it through `prepareManifest()`;
4. creates or safely reuses the matching Phase 1 engine;
5. calls `engine.reconcile()`;
6. renders from the engine's worker-backed reconciliation result.

Leaving the screen disables callbacks from that entry. Re-entry enables callbacks only immediately before a new reconciliation increments the engine generation, preventing an earlier entry/session from overwriting the new screen. A replaced manifest engine also fails a record-identity guard.

No downloaded count, completion boolean, manifest version, or update provenance is stored in localStorage or any other parallel store.

## UI state mapping

The controller maps the Phase 1 statuses to the approved learner states:

- `checking` → indeterminate **Checking downloaded pronunciation audio…** with no action;
- reconciled `ready` at zero → **0 of N available offline** and **Download audio**;
- reconciled `ready` above zero → generic **Download incomplete**, exact count, Continue, and Remove;
- `downloading` → exact present/total, supplemental nearest-whole percentage, and Pause;
- `pausing` → **Pausing after current downloads…** with the control briefly disabled;
- `paused` → generic incomplete state, **You can continue any time**, Continue, and Remove;
- `complete` → **Pronunciation audio available offline**, exact pluralized count, and Remove;
- `network-failed`, `storage-failed`, and `incomplete` → their truthful approved partial copy and explicit retry/continue actions;
- `retention-conflict` → honest browser-retention copy and Remove only, with no automatic/endless Continue loop;
- `interrupted` or unavailable manifest/capability → optional unavailable state and Retry;
- `removing`, `removed`, and `remove-failed` → their approved destructive-operation states.

The controller deliberately does **not** label a future partial manifest as “Update available” or claim a count of new pronunciations. Without durable provenance, `3,621 of 3,680` is truthfully a generic partial state. Continue still asks the Phase 1 engine to fetch only the missing set.

## Progress and announcements

The screen uses one native `<progress>` with an accessible name. Its maximum is the current unique manifest total and its determinate value is the engine's durable-present count. Checking and removing are indeterminate. Visible exact count always accompanies active progress.

Percentages use `Math.round((present / total) * 100)` consistently. If the last durable acknowledgement momentarily reaches total before final reconciliation, the UI switches to an indeterminate **Final check…** rather than showing 100%. Complete is rendered only from the engine's post-reconciliation `complete` state.

One persistent `role="status" aria-live="polite" aria-atomic="true"` region announces download start, each newly crossed 10% threshold from 10–90%, paused, failures, retention conflict, complete, removed, and removal failure. It never announces every file. Rendering and state changes contain no focus calls.

## Pause, Continue, and lifecycle

Download and Continue delegate to the existing engine `start()` / `continueDownload()` methods. Pause delegates only to `engine.pause()`; the UI contains no scheduler, AbortController, or timer. The approved engine therefore remains the authority for concurrency exactly 3, bounded failure handling, missing-only resume, and final reconciliation.

Navigating away calls the controller's cooperative `leave()` synchronously and does not await or block navigation. A hidden document cooperatively pauses active work. Returning/visibility restoration never resumes automatically; returning to the screen reconciles and requires explicit Continue.

No Background Sync or background-download promise was added.

## Persistent-storage reuse

The existing guarded once-per-page `requestPersist()` function is exposed through `PP_A2HS`. Explicit Download/Continue calls it best-effort before delegating to the engine. Unsupported APIs, denial, synchronous throws, and rejection remain contained by the existing helper and never block downloading or change learner copy. No estimate or persistence result is used as a prerequisite or permanence claim.

## Remove dialog

Remove opens a native `<dialog class="modal-overlay">` through `ppOpenSharedOverlay()` with Cancel as initial focus. Cancel and native Escape/cancel close through `ppCloseSharedOverlay()`, make no engine call, and restore focus to the Remove control. The dialog says that removal clears every saved pronunciation clip, including naturally warmed clips, while leaving learning progress untouched.

Confirmation is guarded against duplicate activation and calls `engine.remove()` once per confirmed/retry activation. Removing disables the destructive control. Worker-owned removal remains responsible for deleting the entire shared `popolsku-audio` cache and resetting its estimate. The page never accesses Cache Storage directly.

The shared overlay stacking guard was extended narrowly so the maturity gate, Offline audio confirmation, and menu drawer cannot stack. No second modal/focus system exists.

## Privacy, Install, and About

Privacy now explains both lazy per-play saving and the optional full-library download, local browser/device storage, exclusion from progress backups, removal from Offline audio, and possible browser/device clearing or eviction. Its factual no-account/no-analytics/no-telemetry/no-cookie/no-identifier/no-reporting model is unchanged. The date is **15 September 2026**.

Install now says ordinary clips are saved as played, the full set may be downloaded explicitly from Offline audio, and installation alone does not download all clips. About was reviewed and remains accurate, so it was not changed.

## Accessibility and responsive implementation

- Native typed buttons are used for all feature actions.
- The native progress element has an accessible name and exact `aria-valuetext`.
- One polite/atomic live region handles meaningful announcements.
- State is conveyed in text rather than color.
- Feature buttons have a 44px minimum touch target.
- Long copy uses wrapping; action rows wrap and stack at 320–360px.
- No fixed-width Offline audio card or horizontal clipping rule was introduced.
- Existing safe-area, shared header, focus, screen-entry, modal, and reduced-motion contracts are reused.
- Progress, pause completion, failure, and completion do not programmatically move focus.

## Files changed

- `index.html` — screen, menu/route, manifest reuse, controller, progress/status rendering, persistence exposure, remove confirmation, lifecycle pause, Privacy/Install copy, and focused responsive CSS.
- `tests/test_offline_audio_phase2_ui.js` — new deterministic 104-assertion Phase 2 UI/accessibility/source-boundary suite.
- `tests/test_offline_audio_phase1_engine.js` — one narrow current-phase invariant now expects the authorized single screen/menu entry; all engine assertions remain unchanged.
- `tests/test_phase2c_navigation.js` — current menu order, route allowlist, and authorized Privacy wording/date updated; frozen version/cache assertions retained.
- `tests/test_phase3b_overlays.js` — current modal count updated from two to three; overlay behavior assertions unchanged.
- `tests/test_phase3b_focus_scroll.js` — direct informational route allowlist includes Offline audio; frozen version assertion retained.
- `tests/test_phase3b_mobile_layout.js` — current header count and the two focused narrow-layout selectors include Offline audio; frozen version assertion retained.
- `reports/offline-audio-phase-2-ui.md` — this report.

`sw.js` was not changed. No Phase 1 engine defect was found.

## Deterministic and protected test results

Maintained Phase 2/protected suites total **3,270 passed, 0 failed**:

| Command | Result |
|---|---:|
| `osascript -l JavaScript tests/test_offline_audio_phase2_ui.js` | **104 passed, 0 failed** |
| `osascript -l JavaScript tests/test_offline_audio_phase1_engine.js` | **77 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_fallback.js` | **585 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_failure_inline_feedback.js` | **38 passed, 0 failed** |
| `osascript -l JavaScript tests/test_priority8_phase1_playback.js` | **25 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1a_accessibility.js` | **82 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1b_keyboard_focus.js` | **214 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase2a_core_activity_accessibility.js` | **127 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_accessibility.js` | **229 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_variety.js` | **193 passed, 0 failed** |
| `osascript -l JavaScript tests/test_mixed_audio.js` | **260 passed, 0 failed** |
| `osascript -l JavaScript tests/test_mixed_accessibility.js` | **411 passed, 0 failed** |
| `osascript -l JavaScript tests/test_conversation_accessibility.js` | **101 passed, 0 failed** |
| `osascript -l JavaScript tests/test_podcast_accessibility.js` | **100 passed, 0 failed** |
| `osascript -l JavaScript tests/test_grammar_interaction.js` | **616 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase3b_overlays.js` | **108 passed, 0 failed** |

Repository validators:

| Command | Result |
|---|---|
| `python3 validate_content.py` | passed — 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline intact |
| `python3 verify_audio.py` | passed — 3,621 required, 3,621 manifest, 3,621 MP3, 0 missing, 0 orphaned |
| `python3 validate_priority8_staging.py` | passed — read-only revision 8 valid |
| `python3 build_pages.py --check` | passed — committed generated output current |
| `git diff --check` | passed |

## Historical/frozen test exceptions

No frozen version/cache assertion was weakened merely to make an old suite green.

- `tests/test_phase2c_navigation.js`: **393 passed, 2 failed** after every current navigation/menu/Privacy/overlay assertion passed. The two failures are frozen provenance locks expecting app `8.11` and shell `popolsku-v66`.
- `tests/test_phase3b_focus_scroll.js`: **315 passed, 1 failed**. The one failure is the frozen app `8.11` lock.
- `tests/test_phase3b_mobile_layout.js`: **168 passed, 1 failed**. The one failure is the frozen app `8.11` lock.

Current behavioral invariants in those files were updated only where the authorized Offline audio screen, route, menu item, confirmation dialog, Privacy text, and two narrow-screen selectors necessarily changed them.

## Local browser QA actually performed

A temporary localhost server and the Codex in-app browser were used; production was never opened.

Verified:

- direct `#offlineAudio` startup reaches the real screen and focuses its heading;
- Back returns Home and the drawer opens with Offline audio immediately after Install;
- the drawer link returns to `#offlineAudio` without starting a download;
- Checking uses an indeterminate named progress bar and no actions;
- a first-load worker-readiness failure becomes the truthful unavailable/retry state;
- after the local worker became active, real reconciliation rendered the existing partial cache as **40 of 3,621 available offline** with Continue and Remove;
- the partial native progress element reported `max="3621"`, `value="40"`, and `aria-valuetext="40 of 3,621, 1 percent"`;
- Remove opened the shared native dialog with Cancel initially focused; activating Cancel made no removal call and restored focus to Remove;
- desktop/default width has no horizontal overflow;
- 390×844 partial state has `scrollWidth === clientWidth === 390`;
- 320×568 partial state and dialog have no horizontal overflow (the closed page's 305 CSS-pixel client width reflected its vertical scrollbar; scroll width matched it, while the modal-locked dialog was 320/320);
- 568×320 landscape has no horizontal overflow and scrolls vertically for the content;
- long unavailable/supporting copy wraps within the card at narrow widths;
- browser zoom shortcuts were exercised and reset, but the automation surface reported the same computed font size and therefore did not provide valid 200% text-scale evidence.

The in-app browser eventually established a usable local service-worker channel but no connected external Chrome instance was available. A live full/active download was deliberately not started because Phase 2 QA must not make 3,621 real requests. Complete, active Pause, network/storage/bad-response, and confirmed-removal results therefore remain covered by the deterministic Phase 1 engine, Phase 2 UI, overlay, navigation, keyboard/focus, and mobile-layout suites above. Native Escape synthesis did not close the test dialog in this automation surface, so only the deterministic cancel-event test—not browser behavior—is claimed for Escape. No real iPhone, VoiceOver, reliable 200% OS text-scale measurement, reduced-motion rendering, full-library download, or confirmed physical cache removal was claimed. Physical iPhone acceptance remains Phase 4.

## Frozen product and content invariants

- `APP_VERSION = "9.15"` unchanged.
- `CACHE = "popolsku-v70"` unchanged.
- `AUDIO_CACHE = "popolsku-audio"` unchanged.
- Audio remains 3,621 required / 3,621 manifest entries / 3,621 MP3 files / 0 missing / 0 orphaned.
- Audio payload remains 54,378,576 bytes (51.859451 MiB), shown as **About 52 MB**.
- Verb Patterns remains 98 lemmas / 129 meanings / 269 patterns / 269 examples / 269 pronunciation-enabled examples.
- `audio-manifest.json`, `audio/*.mp3`, content, generated pages, and `sitemap.xml` were not changed.
- No analytics, telemetry, cookies, identifiers, reporting endpoint, external API, second manifest/cache/audio store, direct page Cache Storage write, Background Sync, or durable completion/version marker was added.
- Git remotes remain empty. Nothing was pushed or deployed. Production was never accessed.

## Independent review correction — stale-session re-entry race

### Review finding and deterministic reproduction

Independent review after the original Phase 2 commit found one cross-phase race in the approved page engine. The correction started from commit `62c6439271bab2c71f223cc2c0721fc7daa27098`, tree `ac0462ee44336ae707dbda9dae41d53d4b279448`, on `offline-audio-phase-2-ui`, with a clean worktree, zero remotes, and `push.default=nothing`.

The defect was reproduced with eight missing files and three controlled unresolved `offline-audio-store-one` operations:

1. `start()` created three lanes and held all three requests.
2. `pause()` stopped further scheduling.
3. `reconcile()` simulated immediate screen re-entry, advanced the page-engine generation, and truthfully published `ready` with the old lanes still draining.
4. One explicit `continueDownload()` ran before those old lanes settled.
5. The old implementation's unconditional `if(sessionPromise) return sessionPromise;` joined the obsolete session instead of arranging current-generation work.
6. After the stale replies settled, no successor scheduler began, so the learner needed a second Continue activation.

The Phase 1 suite's original 77 assertions covered ordinary Pause then Continue after the old session had already settled, but not Continue after a newer reconciliation while the old session was still alive.

### Root cause and correction architecture

`sessionPromise` described whether some scheduler session existed, but not which generation owned it. That distinction is essential after reconciliation or Remove advances `generation`.

The page engine now keeps four related in-memory values:

- `sessionPromise` — the currently draining/running session;
- `sessionGeneration` — the exact generation owned by that session;
- `queuedSuccessorPromise` — at most one actionable successor waiting for a stale session;
- `queuedSuccessorGeneration` — the authoritative generation from which the latest explicit Continue requested that successor.

The resulting contract is:

- an active session whose `sessionGeneration === generation` remains joinable, preserving rapid same-generation Start/Continue deduplication;
- a session from an older generation is never cleared or overlapped;
- one queued successor waits on the stale session promise, and repeated Continue calls join that exact successor promise;
- only after the stale session fully settles does the successor compare its owned request generation with current `generation`;
- equality begins one fresh `runStart()`, which performs its own fresh reconciliation before scheduling missing files;
- mismatch resolves harmlessly from the current snapshot and starts no lanes.

`sessionPromise` could not simply be cleared during re-entry: the three old lanes would remain alive while a fresh run created three more, permitting six simultaneous operations and violating the approved concurrency-3 architecture. Waiting on the owned stale session creates a strict drain boundary. The controlled regression observed both the transport-level maximum and engine `maxActive` as exactly 3, never 4–6.

A later explicit Continue from a newer authoritative generation may take ownership of the same one waiting successor. Without such a new explicit request, Remove or any newer reconciliation leaves the queued generation stale, so it cancels when the drain finishes. No persistent generation metadata is used.

### Stale lane callback hygiene

Each lane still decrements the shared `active` counter when its request settles. If its run generation is stale, the tail now updates only the internal counter fields without calling `publish()` and without recursively scheduling another item. Thus global accounting reaches zero correctly, but an old reply cannot emit misleading state into the newly reconciled/removed generation. Current-generation lane tails retain the original publish-and-next-lane path.

### New controlled-promise assertions

`tests/test_offline_audio_phase1_engine.js` now has 12 additional shipping-code assertions, increasing the suite from **77 to 89 passed**:

- **E5** — repeated same-generation Start/Continue returns the exact active session promise;
- **E6** — the re-entry fixture holds exactly three old operations;
- **E7** — re-entry reconciliation reaches truthful `ready` while those lanes drain;
- **E8** — three rapid Continue calls join one pending successor and start no fourth request;
- **E9** — one stale lane tail decrements active accounting without a state notification;
- **E10** — the one queued Continue automatically fresh-reconciles, downloads the five remaining clips, and reaches Complete without a second activation;
- **E11** — old drain plus successor has transport maximum 3, engine maximum 3, and ends with zero active operations;
- **E12** — the superseded old session cannot overwrite successor completion;
- **E13–E14** — Remove becomes authoritative, the queued successor remains pending until drain, then resolves Removed with exactly the original three requests and no post-Remove scheduling;
- **E15–E16** — a newer reconciliation similarly invalidates the older queued successor and creates no new lanes.

The pre-existing ordinary Pause/Continue assertion remains green and still proves missing-only continuation after a normally settled pause.

### Correction validation

The current maintained Phase 2/protected total is **3,282 passed, 0 failed**. This is the original 3,270 total plus the 12 new engine regressions; no original assertion was removed or weakened.

| Command | Current result |
|---|---:|
| `osascript -l JavaScript tests/test_offline_audio_phase1_engine.js` | **89 passed, 0 failed** |
| `osascript -l JavaScript tests/test_offline_audio_phase2_ui.js` | **104 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_fallback.js` | **585 passed, 0 failed** |
| `osascript -l JavaScript tests/test_audio_failure_inline_feedback.js` | **38 passed, 0 failed** |
| `osascript -l JavaScript tests/test_priority8_phase1_playback.js` | **25 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1a_accessibility.js` | **82 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase1b_keyboard_focus.js` | **214 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase2a_core_activity_accessibility.js` | **127 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_accessibility.js` | **229 passed, 0 failed** |
| `osascript -l JavaScript tests/test_listening_variety.js` | **193 passed, 0 failed** |
| `osascript -l JavaScript tests/test_mixed_audio.js` | **260 passed, 0 failed** |
| `osascript -l JavaScript tests/test_mixed_accessibility.js` | **411 passed, 0 failed** |
| `osascript -l JavaScript tests/test_conversation_accessibility.js` | **101 passed, 0 failed** |
| `osascript -l JavaScript tests/test_podcast_accessibility.js` | **100 passed, 0 failed** |
| `osascript -l JavaScript tests/test_grammar_interaction.js` | **616 passed, 0 failed** |
| `osascript -l JavaScript tests/test_phase3b_overlays.js` | **108 passed, 0 failed** |

All repository validators were rerun successfully: `validate_content.py`, `verify_audio.py`, `validate_priority8_staging.py`, `build_pages.py --check`, and `git diff --check`.

Only `index.html`, `tests/test_offline_audio_phase1_engine.js`, and this report changed in the correction. `sw.js` remained byte-identical at SHA-256 `00e292f31436de532f3b053e5ce63f180cb62efa41f1a31b492efc643799da82`. Release markers remain app `9.15`, shell `popolsku-v70`, and audio cache `popolsku-audio`. Audio remains 3,621 required / 3,621 manifest / 3,621 MP3 / zero missing / zero orphaned. No UI, copy, navigation, Privacy, Install, persistence, worker, content, audio, manifest, generated page, sitemap, analytics, telemetry, Background Sync, cache, or persistent download-state change was made.
