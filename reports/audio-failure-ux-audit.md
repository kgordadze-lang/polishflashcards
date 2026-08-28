# Audio Failure UX Audit — Non-Overlapping Inline Feedback

## Repository and pre-flight

- Repository: `/Users/Kaj/Downloads/Repository for Codex - Audio Failure UX Fix`
- Branch: `fix/audio-failure-inline-feedback`
- Starting commit: `4d83882b123802f7be2f2c4ddc64a998cea0bd30`
- Starting tree: `ef464688a515113b863d8afd60990782a4abfada`
- Working tree at pre-flight: clean (`git status --short` produced no rows)
- Remotes at pre-flight: none (`git remote -v` produced no rows)
- `push.default`: `nothing`
- Stop-condition result: none applies. The defect can be corrected in the existing shared app-shell playback/status path without changing audio identity, manifests, assets, eligibility, service-worker behavior, Listening design, generated pages, or Priority 8 search.

## Architecture discovered

### App-shell pronunciation controller

`index.html` owns one shared app-shell pronunciation controller. Its public entry points are `speakText(txt, btn)` for an arbitrary eligible Polish utterance and `speakCardMain(card, btn)` for a card's canonical eligible utterance. `speakCardMain` delegates to `speakText`; it does not create another player.

The controller state is:

- `audioMap`: normalized Polish text to content-hashed MP3 path.
- `audioManifestStatus`: `loading`, `ready`, or `unavailable`.
- `currentAudio`: the one live pre-generated `<audio>` attempt.
- `currentUtterance`: the one speech-synthesis attempt allowed to report back.
- `speakBtn`: the control carrying the visual playing state.
- `audioRetryRequest`: `{text, btn}` for the one phrase/control Retry must repeat.
- `audioStatusEl`, `audioStatusMsgEl`, and `audioRetryEl`: one reused status subtree.
- `audioStatusOwner`: the control described by the visible status.

`speakText` begins by calling `stopAllAudio`, stores the new retry request, then either calls `playPreGenerated` for a mapped MP3 or goes directly to `speakFallback`. `playPreGenerated` configures the selected speed and preserves pitch. A clip error or rejected `play()` promise may invoke exactly one speech-synthesis fallback. If speech synthesis is absent, unusable, throws, or emits an error, `showAudioStatus("failed", btn)` exposes the terminal failure and Retry.

### Generated-page pronunciation controller

`build_pages.py` owns a second, intentionally page-local runtime (`PLAYER_JS`) for the static grammar and vocabulary pages. It implements the same product policy but does not share live state with the single-page app: one clip, one speech fallback, one reused status/retry subtree, and one monotonically increasing `token` to invalidate stale callbacks. Generated output is committed, but `build_pages.py` is its source.

This is not a competing app-shell state machine: static pages are separate documents and cannot share the app document's JS state. The generator implementation is already in normal flow and its status is placed into the ordinary `.ex`/card layout. No generated output change is required for the reported flashcard defect, and the task forbids regeneration.

## Current playback and failure flow

1. A pronunciation control invokes `speakCardMain` or the delegated `[data-say]` handler invokes `speakText`.
2. `speakText` calls `stopAllAudio`, which pauses the previous clip, invalidates the previous utterance, cancels synthesis, clears the speaking marker, clears the status, and clears the retry request.
3. The new `{text, btn}` retry identity is stored.
4. A manifest hit creates one `Audio(file)` in `playPreGenerated`; a miss starts device speech directly.
5. A pre-generated clip failure settles once and tries device speech once. A fallback notice uses the same status element without Retry.
6. A terminal speech failure changes that same element to `Audio couldn't play. Check your connection, then try again.` and exposes the single `Try again` button.
7. Retry focuses the originating pronunciation control, then calls the same `speakText(request.text, request.btn)` path. A successful fresh attempt clears the previous failure at its start. A repeated failure reuses the same two-child status subtree.

## Exact failure-UI owner and root cause

The app-shell failure UI is owned by `index.html`:

- `ppAudioStatusHost()` creates and parks the single live-region/status subtree.
- `showAudioStatus(kind, btn)` populates it, exposes Retry when terminal, associates the failed control with `aria-describedby`, and moves the subtree.
- `clearAudioStatus()` removes the visible/accessible failure state.
- `retryAudio()` replays `audioRetryRequest` through `speakText`.
- `.audio-status` and `.audio-retry` provide the layout and presentation.

The status box's computed position is `static`; it is not itself `absolute`, `fixed`, portal-positioned, or transformed. The unsafe part is its placement policy: `showAudioStatus` always calls `btn.insertAdjacentElement("afterend", box)`. On a flashcard, the main `.fab` pronunciation control is `position:absolute` inside a transformed 3D `.face`. Its DOM position therefore does not represent its visual or reading-order position. The shared helper moves normal-flow feedback into that transformed card-face layer immediately after a control that is itself outside flow. That makes the feedback's placement depend on the internals of the layered flip card instead of placing it in the established page flow between learning content and navigation controls.

A local 320×568 reproduction of the clip-failure/device-voice fallback confirmed the mixed mechanism: `.fab` computed `position:absolute`, the reused status computed `position:static`, and the status became a child of `.face` above the Polish text. The status did not overlap in that short baseline card, but the architecture has no invariant keeping the full failure/Retry panel outside the transformed card layers for longer content, larger text, or the opposite face. Moving the overlay a few pixels or changing coordinates would preserve the same unsafe coupling.

The smallest robust correction is to keep the same shared status node and same state machine, but select an in-flow contextual anchor. For any control inside `#flip`, place the status immediately after `.stage` and before `.controls` in `#cardView`. This is the existing safe structural boundary:

`learning card/stage → audio status → Prev/Shuffle/Next`.

For non-flashcard pronunciation controls, retain the established adjacent in-flow placement. Those controls are not children of the transformed flashcard layers, and the existing flex/reflow rules already keep their status readable. Generated pages likewise already follow a safe in-flow card structure and need no change.

## Product surfaces using the app-shell path

The following all reach `speakText` and the same app-shell status/retry implementation:

- ordinary vocabulary flashcards: front and back main pronunciation controls;
- podcast-phrase flashcards: canonical phrase and example pronunciation where eligible;
- flashcard example sentences;
- Grammar lesson example controls;
- Grammar choose/build feedback answer controls;
- conversation transcript phrase controls, including challenge-mode hidden-phrase controls;
- Type It answer feedback controls;
- Listening's main Play control and its example-feedback controls;
- Mixed Quiz listening questions, canonical-answer feedback, and example feedback;
- Verb Patterns example controls;
- other app-shell controls carrying `[data-say]`, through the single delegated click handler.

Static generated learning pages use the generator-owned equivalent path. There are 29 generated audio pages (23 grammar and 6 vocabulary pages) with 380 pronunciation buttons in the current generated inventory. Their status is already an ordinary-flow sibling in the static card layout.

## Listening relationship and boundary

Listening shares the app shell's playback logic, player state, active audio identity, speech fallback, retry state, status rendering, failure UI, and cleanup primitive. `lPlayCurrent()` delegates through `speakCardMain`. Listening separately owns question selection/eligibility, manifest-readiness gating (`syncListeningAudioReadiness`), answer/result state, and its answer-feedback live region. Those Listening-specific concerns do not need to change.

The existing Listening boundaries call `stopAllAudio` on round start, question advance, and exit. Mixed Quiz has the same explicit boundaries for its listening-format questions and audio feedback. Listening eligibility and behavior remain out of scope and can remain byte-identical.

## Retry, identity, stale-result, and duplicate safeguards

Retry is wired as a native `button type="button"` with visible text `Try again`. It is hidden, disabled, and removed from the tab order unless a terminal failure is active. The status uses `role="status"`, `aria-live="polite"`, and `aria-atomic="true"`; the failed source control gets `aria-describedby` pointing at the message. Failure does not move focus. Activating Retry deliberately focuses the source control before the Retry button disappears, then uses the normal `speakText` path.

The retried identity is exactly `audioRetryRequest = {text, btn}`. It carries the original utterance and the originating control, while canonical file identity remains derived by `ppNormalize(text)` and the manifest-backed `audioMap`.

Stale and duplicate safeguards already present:

- `currentAudio` is the single active clip identity.
- Every clip attempt has a closure-local `settled` latch. The first of `error`, rejected `play()`, or completion wins; later channels for the same attempt do nothing.
- `settle()` checks `currentAudio === audio`; a superseded/stopped clip cannot fall back, clear a newer playing marker, or announce into a newer context.
- `currentUtterance === u` gates speech `onend`/`onerror`; cancelled or superseded utterances cannot change the current state.
- `stopAllAudio` nulls both active identities before late callbacks can act.
- One `audioStatusEl` is created and reused. Repeated failure mutates its message/retry state rather than appending a second node.
- One `audioRetryRequest` is replaced after each `stopAllAudio`; Retry cannot accumulate attempts or target an older phrase.
- Generated pages implement the same guarantees with one reused status element, a per-attempt `settled` latch, and a monotonic `token` checked by every callback.

These safeguards do not need replacement or parallel state. The proposed patch will only change status anchoring and ensure flashcard content changes call the existing cleanup primitive.

## Navigation and content cleanup

Existing explicit cleanup is strongest in Listening and Mixed Quiz: start, next, and exit all call `stopAllAudio`. Leaving Verb Patterns through `showScreen`, and rebuilding the Verb Patterns index, also stops audio. Starting a new pronunciation request always cleans the prior request.

The audit found a concrete missing boundary in ordinary flashcards. `render()` is called for initial content, Next, Previous, Shuffle, mark-and-advance, and direction changes, but it does not call `stopAllAudio`. `startTopic()` also reaches that render without its own stop. Consequently a visible failure or a still-live attempt from card A can survive a render of card B until another playback starts; the reused status remains attached to the persistent face while its text changes. Topic/content navigation through generic `show()` is not a global audio boundary either.

The minimal correction is to call the existing `stopAllAudio()` once at the beginning of `render()`. That covers initial topic render, Next, Previous, Shuffle, mark-and-advance, and direction changes without adding state. The generic `showScreen()` boundary should also retire audio whenever the active screen changes, while retaining the existing explicit Verb Patterns branch. The existing identity checks then make any delayed A rejection harmless. Screen-specific Listening/Mixed/Verb-Patterns boundaries remain unchanged and remain safe when the idempotent cleanup is called again.

## Accessibility and focus

The existing accessibility architecture is appropriate and should be preserved:

- polite status semantics (`role="status"`, `aria-live="polite"`, `aria-atomic="true"`);
- explicit text, not color or icon alone;
- a native Retry button with an accessible visible name and native Enter/Space activation;
- `aria-describedby` association from the failed control to the failure message;
- no automatic focus move when failure appears;
- deliberate focus return to the source control only after the user activates Retry;
- no animation on the status, and existing reduced-motion rules for speaking/flip animation.

The proposed anchoring change preserves these semantics and does not add a second live region. Clearing the status empties its text and removes the description, preventing stale or repeated announcements after success/content change.

## DOM/layout placement

Current flashcard structure is:

- `#cardView` (column flex)
  - `.stage`
    - `.scene`
      - `#flip` (transformed grid)
        - front `.face`
        - back `.face.back-face`
        - absolutely positioned pronunciation controls within faces
  - `.controls` (Prev / Shuffle / Next)

The proposed placement reuses `#cardView` without adding a wrapper: insert the shared status immediately before `.controls` (equivalently after `.stage`). It is outside `#flip`, outside both transformed faces, and inside the existing column flow. Intrinsically tall content can grow, the document can scroll, and navigation remains after the failure in reading order.

For non-flashcard app-shell controls, retain the established adjacent placement. The status retains wrapping and `min-width:0`, and no fixed height, clipping, coordinate, text reduction, or viewport magic number is introduced.

## Existing relevant tests

- `tests/test_phase4b3_audio_resilience_range_storage.js` already drives both app-shell and generated-page runtimes with deterministic fake Audio, speech synthesis, DOM, promises, error events, and stale callback orderings. It covers wording, live-region semantics, accessible Retry, focus behavior, successful Retry cleanup, repeated Retry failure, one-status reuse, duplicate fallback suppression, stale audio/speech callbacks, stop cleanup, generated-page parity, offline-unavailable behavior, and cache/Range/quota invariants.
- `tests/test_audio_fallback.js` protects the older shared playback/fallback and active-audio behavior, including duplicate failure channels and stale/superseded attempts.
- `tests/test_priority8_phase1_playback.js` protects the released Verb Patterns delegation to the shared audio controller and the pattern-leaving stop boundary.
- `tests/test_priority8_phase4d1_speaker_icon_ui.py` protects speaker controls and released markers.
- `tests/test_listening_accessibility.js`, `tests/test_mixed_audio.js`, `tests/test_mixed_accessibility.js`, and related activity suites protect Listening/Mixed entry points, accessibility, and activity boundaries.
- `tests/test_build_pages.py` protects the generated-page source/output structure, live-region/flex wrapping contracts, and generator currency.
- Service-worker suites protect cached audio, offline navigation, content validation, Range requests, FIFO retention, quota recovery, and the unchanged `popolsku-audio` cache.

## Missing deterministic regression coverage

The existing audio tests do not prove the flashcard-specific placement boundary or call real flashcard navigation functions. Focused coverage should add:

- the app-shell status for a flashcard main speaker is outside `#flip`, between `.stage` and `.controls`;
- the shared Verb Patterns example path still uses the corrected `showAudioStatus` implementation without a second status implementation;
- the status CSS is neither absolute nor fixed and narrow-screen rules do not override it;
- first failure yields one message and one Retry;
- repeated failure/rejected `play()` and repeated Retry failure keep one logical status node;
- successful Retry clears it;
- `render()` cleanup covers Next, Previous, Shuffle, topic/content render, and direction change;
- delayed rejection/error from A after render/playback B cannot render A's error into B;
- failure handling does not steal focus, while Retry remains a native keyboard-reachable named button.

Tests should extend the existing deterministic JXA/Node extraction/fake-DOM convention, not require network timing or weaken historical tests.

## Smallest expected implementation file set

1. `index.html`: add a small flashcard-only contextual anchoring branch inside `showAudioStatus`, make `render()` an existing-state cleanup boundary, and apply the same cleanup on generic screen changes.
2. `tests/test_audio_failure_inline_feedback.js`: focused deterministic regression coverage for placement, lifecycle, cleanup, stale callbacks, shared flashcard/Verb-Patterns use, accessibility, and CSS contract.
3. `reports/audio-failure-ux-audit.md`: this required architecture audit.

`build_pages.py`, generated HTML, `sw.js`, audio identity/rules, manifest, MP3s, content, eligibility, Priority 8 search, stable IDs, and QA records should not change.

## Risks and controls

- Moving a live region can affect announcement behavior. Control: keep the element created before use, preserve its identity/semantics, move it before changing text, and retain `aria-describedby`.
- A generic anchor rule could disturb a flex row. Control: scope the anchoring exception to controls inside `#flip`; leave every other established surface unchanged.
- Cleanup could cancel audio during a render that does not change content. Here every `render()` call represents a flashcard content/direction lifecycle boundary, and cancellation is the required safe behavior; no score or progress state is touched.
- Retry focus could point at a removed dynamic control. Existing rendering cleanup will clear `audioRetryRequest` before replacement, so stale Retry is unavailable.
- Historical tests pin old release markers and transitions. They must not be weakened; current invariants will be validated separately and any provenance-only limitation reported.
- Browser speech varies by host. Deterministic fake-Audio/fake-speech tests must own failure ordering; browser smoke should validate visual flow, reachability, normal playback, and available local failure behavior without treating speech-engine availability as a release invariant.

## Audit conclusion

No stop condition applies. The existing shared architecture already has the correct single-player, Retry, stale-attempt, duplicate-fallback, accessibility, offline, and service-worker foundations. A small app-shell-only placement and flashcard-cleanup patch can satisfy the locked requirement without a rewrite, second state machine, generated-page change, audio change, Listening redesign, or Priority 8 change.
