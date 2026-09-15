# Audio Status Layout Audit — Contextual Vertical-Flow Ownership

## Repository and pre-flight

- Repository: `/Users/Kaj/Downloads/Repository for Codex - Audio Status Layout Fix`
- Branch: `fix/audio-status-layout`
- Starting commit: `a17564aee77584c7c2dcc12dca4a0117b5c1b87d`
- Starting tree: `b249cfc691d54186e425a1e36dd075bc4c37bf7a`
- Working tree at pre-flight: clean (`git status --short` produced no rows)
- Remotes at pre-flight: none (`git remote -v` produced no rows)
- `push.default`: `nothing`
- Stop-condition result: none applies. The defect is confined to the shared app-shell status anchor. No audio, content, generated-page, service-worker, version, cache, search, or Listening change is required.

## Exact Verb Patterns DOM

`pRenderLemma()` in `index.html` is the only renderer for a released Verb Patterns lemma. For each meaning it builds a `.vp-meaning` section, and for each pattern it builds this structure:

```text
section.vp-meaning
└── section.vp-pattern [aria-labelledby=pPatternM-P]
    ├── div.vp-headline-row
    │   ├── p.vp-headline
    │   ├── span.vp-badge (when authored)
    │   └── span.vp-recognition (when recognition-only)
    ├── ul.vp-chips
    ├── p.vp-explain
    ├── div.vp-example (when an example exists)
    │   ├── div.vp-example-pl-row
    │   │   ├── p.vp-example-pl[lang=pl]
    │   │   └── button.mini-audio.vp-example-audio (when audioEligible)
    │   └── p.vp-example-en
    └── div.vp-case-links (when applicable)
```

The pronunciation control therefore lives beside the Polish sentence inside `.vp-example-pl-row`. The English translation is the following child of `.vp-example`.

The relevant layout ownership is explicit in the stylesheet:

- `.vp-pattern` is `display:flex; flex-direction:column`.
- `.vp-example` is `display:flex; flex-direction:column`.
- `.vp-example-pl-row` is `display:flex; align-items:center`.
- `.vp-example-pl` is the flexible text item (`flex:1; min-width:0`).
- `.vp-example-audio` has a fixed 44px square and `margin-left:auto`.

This arrangement is safe while the Polish sentence and speaker are the row's only children: the sentence receives the remaining width, the speaker retains its target size, and the English translation occupies its own line below.

## Current shared status placement and the defect

The app shell owns one shared status subtree through `ppAudioStatusHost()`:

```text
div#ppAudioStatus.audio-status[role=status][aria-live=polite][aria-atomic=true]
├── span#ppAudioStatusMsg.audio-status-msg
└── button#ppAudioRetry.audio-retry (terminal failure only)
```

`showAudioStatus(kind, btn)` moves that same node for every status update. Its one existing contextual rule detects a control inside `#flip`, promotes the anchor to `.stage`, and inserts the status after the stage / before `.controls`. Every other app-shell control uses the default `btn.insertAdjacentElement("afterend", box)` path.

For a Verb Patterns example, the default path produces this runtime DOM:

```text
div.vp-example
├── div.vp-example-pl-row  (horizontal flex container)
│   ├── p.vp-example-pl
│   ├── button.vp-example-audio
│   └── div#ppAudioStatus  <-- current insertion point
└── p.vp-example-en
```

The status is `position:static` and is readable in isolation, but normal flow alone is not sufficient when the owning flow is horizontal. It becomes a third flex item with an intrinsic text/button width. At a 320px or 390px viewport, and more severely at 200% text scaling, the fixed speaker and the status consume the row width. Because `.vp-example-pl` is the only flexible item and has `min-width:0`, it absorbs the deficit and collapses to a very narrow column. Its `overflow-wrap:anywhere` then permits the reported fragmentary wrapping. This is why the status itself remains readable while the principal Polish learning content becomes unusable.

No overlap, absolute positioning, audio generation, fallback decision, or phrase-identity error is involved. This is an anchor-ownership defect.

## Status types and lifecycle

Both visible status types use the exact same `showAudioStatus(kind, btn)` placement path:

- `fallback` renders `Using your device's voice.` with Retry hidden.
- `failed` renders `Audio couldn't play. Check your connection, then try again.` with the native `Try again` button exposed and the source control associated through `aria-describedby=ppAudioStatusMsg`.

There is no separate placement for Retry, fallback, speech errors, clip errors, rejected `play()` promises, or thrown playback/synthesis calls. All terminal routes converge on `showAudioStatus("failed", btn)`; the successful post-clip fallback calls `showAudioStatus("fallback", btn)`. Consequently the reported fallback and the longer terminal-failure/Retry panel have the same horizontal competition, with the terminal panel potentially consuming more width.

The state and safety behavior established by the preceding fix is otherwise correct and must remain unchanged:

- one shared status node and one Retry button;
- `stopAllAudio()` clears the visible state, owner association, retry request, current audio, current utterance, and speaking marker;
- each clip has a `settled` latch and current-audio identity check;
- each utterance callback checks current-utterance identity;
- successful Retry starts through `speakText()`, which clears the old status first;
- repeated failure mutates the same node rather than appending another;
- `pRenderIndex()` calls `stopAllAudio()`, so returning from one lemma before opening another clears the old status and invalidates late callbacks;
- `render()` and screen transitions clear flashcard status, so old state cannot migrate to another card/topic.

## Other pronunciation surfaces

The app-shell controller is shared by flashcards, Verb Patterns, Grammar, Conversations, Type It, Listening, Mixed Quiz, and delegated `[data-say]` controls. Static generated grammar/vocabulary pages have a separate document-local equivalent emitted by `build_pages.py`; that runtime is not part of this defect and generated pages must remain unchanged.

The audit found these app-shell placement classes:

| Surface | Control container | Container flow | Current risk |
| --- | --- | --- | --- |
| Main flashcard front/back and flashcard example | inside `#flip` | transformed card layers | Already promoted to `.stage`; safe and unchanged |
| Verb Patterns example | `.vp-example-pl-row` | horizontal flex | Reported defect: status competes with Polish text |
| Grammar teaching example | `.ex-line` | horizontal flex | Same structural risk with Polish and English in `.t` |
| Grammar/quiz answer feedback | `.fb-good` | horizontal flex | Same structural risk with answer and translation in `.t` |
| Conversation phrase | `.brow` | horizontal flex | Same structural risk with `.bubble-content` |
| Type It / Mixed answer | `.v-row` | horizontal flex | Same structural risk with the Polish answer |
| Listening and Mixed main Play | activity card/column | vertical flow | Default adjacent placement is already safe |

The exact screenshot is specific to Verb Patterns because its long example, 44px speaker, and `overflow-wrap:anywhere` make the failure conspicuous. The same insertion mechanism can, however, compress text on the other horizontal content rows. Fixing only the `.vp-example-pl-row` selector would leave a known equivalent failure mode in the same shared helper. A small explicit host/anchor-selection function should therefore preserve contextual ownership while promoting any speaker inside a known horizontal content row to that row's semantic outer host. This is a placement correction, not a redesign of those surfaces.

## Existing regression coverage

- `tests/test_audio_failure_inline_feedback.js` is the focused deterministic fake-DOM/fake-Audio suite for the preceding release. It covers the single shared node, flashcard placement after `.stage` and before `.controls`, live-region semantics, `aria-describedby`, native Retry, no focus theft, successful Retry cleanup, repeated-failure reuse, stale callbacks, render/screen cleanup, and the shared Verb Patterns path. Its current Verb Patterns assertion explicitly pins the defective after-button insertion and must be corrected.
- `tests/test_phase4b3_audio_resilience_range_storage.js` exercises the full shared app-shell and generated-page failure/fallback state machines, stale and duplicate signals, Retry, accessibility semantics, offline behavior, Range responses, retention, and quota handling.
- `tests/test_audio_fallback.js` and `tests/test_mixed_audio.js` cover the established clip/fallback ordering and active-audio identity.
- `tests/test_priority8_phase1_playback.js` covers released Priority 8 / Verb Patterns playback delegation and cleanup on leaving the surface.
- `tests/test_priority7_patterns_ui.js`, `tests/test_priority7_choose_ui.js`, the Priority 7 Python suites, and `tests/test_priority8_phase4f1_verb_patterns_search.py` cover the rendered Verb Patterns projection, recognition-only content, multiple-pattern lemmas, navigation/focus, and the asynchronous 98-lemma search refresh.
- `tests/test_listening_accessibility.js`, `tests/test_listening_variety.js`, `tests/test_mixed_accessibility.js`, `tests/test_phase1a_accessibility.js`, `tests/test_phase1b_keyboard_focus.js`, `tests/test_phase2a_core_activity_accessibility.js`, and `tests/test_phase3b_focus_scroll.js` protect relevant accessibility, navigation, and focus behavior.
- `tests/test_build_pages.py` protects generated-page status semantics and generator/output currency.

## Smallest architectural correction

Add one pure `ppAudioStatusAnchor(btn)` helper beside `showAudioStatus()` and make `showAudioStatus()` use its returned anchor. The helper should apply ordered ownership rules:

1. A control inside the flashcard `#flip` remains owned by `.stage`, preserving the released `stage → status → controls` invariant.
2. A control inside a known horizontal learner-content row is owned by the row's semantic outer host: `.vp-example`, `.ex-line`, `.fb-good`, `.brow`, or `.v-row`.
3. Any other control retains the existing direct-adjacency default.

For Verb Patterns this changes only the status location:

```text
section.vp-pattern  (vertical flex)
├── ...
├── div.vp-example
│   ├── div.vp-example-pl-row
│   │   ├── p.vp-example-pl
│   │   └── button.vp-example-audio
│   └── p.vp-example-en
├── div#ppAudioStatus  <-- new insertion point
└── div.vp-case-links (when present)
```

The association remains contextual: the status immediately follows the complete example that owns the pressed speaker, after both Polish and English, and before any case links. Its parent `.vp-pattern` is a vertical flex container, so added status height extends the document normally. The status is no longer a child of the horizontal Polish row and therefore cannot participate in that row's width allocation. The sentence keeps all width except the existing 44px speaker and 10px gap; English retains the full example width. Long Polish, multi-line English, recognition-only metadata, multiple patterns, narrow viewports, desktop, and 200% text scaling can all grow vertically without a competing status column.

No CSS change, breakpoint, fixed/absolute positioning, duplicate controller, duplicate live region, hidden feedback, magic width, generated-page change, content change, or fallback-policy change is needed.

## Planned deterministic coverage

Extend `tests/test_audio_failure_inline_feedback.js` rather than add a parallel harness. The focused additions will assert:

- Verb Patterns fallback and terminal failure both place the shared node after `.vp-example`, outside `.vp-example-pl-row`;
- the Polish sentence remains a child of the intended row and the English translation remains inside the example;
- status ownership stays associated with the pressed speaker;
- the flashcard stage/controls placement is unchanged;
- horizontal Grammar, feedback, conversation, and verdict controls use safe contextual outer anchors, while a genuinely vertical control retains direct adjacency;
- Retry remains native and functional, success clears status, repeated fallback/failure never duplicates it, and semantics stay `role=status` / `aria-live=polite`;
- returning to the Verb Patterns index clears old status and invalidates stale callbacks, and flashcard render cleanup remains intact;
- status CSS stays in normal flow with natural wrapping and no responsive overlay override;
- exactly one app-shell status implementation remains.

## Audit conclusion

No stop condition applies. The required correction is a small explicit anchor-ownership helper in `index.html`, plus focused extensions to the existing deterministic status test. It preserves the complete released audio state machine and accessibility contract while removing the shared status from horizontal learner-text rows. The implementation does not need to touch `APP_VERSION`, cache names, `sw.js`, `build_pages.py`, generated pages, audio files/manifest, runtime content, Priority 8 identity/eligibility, Listening logic, or Verb Patterns search.
