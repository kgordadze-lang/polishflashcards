# Card flip control layout fix

## Starting state and report

- Repository: `/Users/Kaj/Downloads/Repository for Codex - Flip Control Layout Fix`
- Branch: `fix/card-flip-control-layout`
- Starting HEAD: `5a67061f0d712adc1bc4cbcf2aae31d4bcef3814`
- Starting tree: `fe709ab5ceed0e65f328bf0ea0111cac3caf62c5`
- Initial worktree clean; `git remote -v` empty; `push.default=nothing`.
- Reported on popolsku.app v9.19, iPhone 17, iOS 26.6.2, Mianownik Learn card. The reported sentence is “It marks the subject - the person or thing doing the action.”

## Architecture, cause, and fix

`index.html` contains two static Learn scenes: the vocabulary/podcast Study scene (`#flip`, `#flipControl`) and the grammar teaching scene (`#gFlip`, `#gFlipControl`). Each scene contains one front face and one back face in a shared grid cell. JavaScript populates the faces and changes `flipped`, the control label, and the inactive face's `inert`/`aria-hidden` state. Both controls used the same `.flip-control` CSS. There was no desktop/mobile positioning split: `position:absolute; top:15px; left:50%` placed both controls over the top of their scene, independently of face content height. Grammar explanations that grow upward into that region could sit beneath the control. The same mechanism applied to wrapped text in any shared Learn face.

Each `.scene` now starts with one `.flip-control-row` in normal document flow, followed by the existing rotating `.flip` and its two faces. The scene owns the card border, background, radius, and shadow; the faces occupy the lower content area. The row owns 55px, including the existing 40px button. Its button stays centered near the top, outside the rotating faces. Text expansion grows the lower face/grid area, so face content cannot enter the button's row. No face-specific spacing, text heuristics, JavaScript measurements, or mobile coordinates are involved. The control remains one native button per scene and does not rotate with the card.

The affected surfaces are all vocabulary Learn cards across levels, podcast intro and phrase cards using the Study scene, and all ordinary grammar Learn teaching cards using the Grammar scene. Grammar practice drills and other activity controls have different markup and were not changed. Both front and back faces share the row and keep the same button position. The existing direction toggle uses a similar arrows icon but is a separate control.

## Files changed

- `index.html`: shared scene/control layout and the two static Learn scene rows.
- `tests/current/test_card_flip_layout.py`: focused structure, CSS, behavior wiring, content, and release marker checks.
- `tests/test_phase1a_accessibility.js`: update the sibling-button assertion for the new control-before-face order.
- `tests/test_phase1b_keyboard_focus.js`: keep the inactive-back-face assertion scoped to the whole flip container after that order change.
- `reports/card-flip-control-layout-fix.md`: implementation evidence.

The focused test checks that each scene has one control row before its two grid faces; the button is a labeled native button, in normal flow, with its 40px target; and flip, navigation, reported content, and release marker wiring remain. Existing executable tests cover the actual flip state, keyboard shortcuts, focus, navigation, and audio interactions. The front/back geometry was also checked in the local browser.

## Validation

- `PYTHONDONTWRITEBYTECODE=1 python3 tests/current/run_current_tests.py`: passed, 10 maintained JavaScript suites and 116 Python tests (including 3 new focused tests).
- Selected legacy suites: grammar interaction 616/616, activities 146/146, audio failure feedback 38/38, Phase 1A accessibility 82/82, Phase 1B keyboard/focus 214/214, Phase 2A core accessibility 127/127; 1,223 selected assertions passed.
- `python3 validate_content.py`: passed; 10 levels, 97 topics, 1,215 cards, 353 drills; forward baseline unchanged.
- `python3 verify_audio.py`: passed; 3,621 required phrases, 3,621 manifest entries, 3,621 MP3 files, zero missing/orphaned.
- `python3 verb_patterns_runtime_validator.py`: passed; 98 lemmas, 129 meanings, 269 patterns, 269 examples, 269 audio-eligible examples.
- `python3 validate_current_release.py`: passed; release, storage, and Verb Patterns contracts valid.
- `python3 build_pages.py --check`: passed, committed generated pages current with no drift.
- `git diff --check`: passed.
- `python3 validate_priority8_staging.py`: unavailable because this file does not exist in this checkout. No substitute script or production repository was used.

## Local browser QA and accessibility

Used the Codex in-app browser against a local-only Python HTTP server, with explicit browser viewport overrides. Inspected the reported Mianownik card at 320, 375, 390, 430, and 1024 CSS pixels on both faces. The exact reported sentence remained visible and the nearest measured button-to-sentence gap was about 29px. The card-5 grammar ending table, which contains longer Polish text, stayed inside a naturally grown face at 320px. A short vocabulary card and the wrapped Polish “Czy mówi pan po angielsku?” / English “Do you speak English?” card were checked on both faces at all five widths. The longer English “Please / Here you go / You're welcome” translation was also checked at 320px. No inspected card had button/text overlap, page-level horizontal overflow, or clipped learner content. A 320×568 short viewport remained scrollable when content exceeded the screen.

The Study button kept a changing accessible name, native Enter/Space activation, visible keyboard focus, and a 40×40px target. Front/back `aria-hidden` and `inert` state switched with the card, and Next reset the grammar card to its front state. Prev/Next and audio wiring were unchanged. Browser zoom shortcuts did not change the in-app browser zoom, so 125%, 150%, and 200% browser text enlargement were not measured directly. The normal-flow separation remains independent of text length, but device text scaling and screen-reader behavior require independent review. No physical iPhone verification was performed by the implementation agent.

## Protected state and delivery boundary

No learning content, Polish/English translations, stable IDs, legacy mappings, audio manifest or MP3s, Verb Patterns data, schema/migration code, privacy/install copy, analytics, service worker/offline-audio architecture, generated pages, or sitemap dates were edited. `APP_VERSION` remains `9.19`; shell `CACHE` remains `popolsku-v75`; `AUDIO_CACHE` remains `popolsku-audio`; schema and content migration remain `2`.

The repository has zero remotes. Nothing was pushed or deployed, no release preparation was done, and the production repository was never accessed. The final implementation commit and tree identifiers are recorded in the final completion response: an immutable report in its own commit cannot contain that commit's hash or tree hash without changing them.
