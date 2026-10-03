# Release 10.3 flip-control visual polish

## Baseline and defect

- Working checkout: `fix/flip-control-visual-polish-10.3` at `/Users/Kaj/Downloads/Repository for Codex - Flip Control Visual Polish 10.3`.
- Starting HEAD: `cbe0f4a3bbc7213b4804577ec9575e51519fc8fd`.
- Starting tree: `c995a29ed2627d290effe58adc9bfa011f81a689`.
- The starting worktree was clean, `git remote -v` was empty, and `push.default` was `nothing`.
- The 40px circular flip button was bottom-aligned flush with the next rotating face. Its lower antialiased edge and small shadow visually met that face, making the circle look slightly flattened.

## Correction and invariant

- `index.html` retains the shared, normal-flow 55px `.flip-control-row` and adds `box-sizing:border-box` plus `padding-bottom:4px`. Its total height stays 55px; the 40px button, icon, and card face dimensions are unchanged. Both vocabulary/podcast and grammar Learn cards use the same rule.
- The control row remains a sibling before `.flip`, outside both rotating faces. Learner-facing text stays inside those faces and cannot occupy the control's area. No absolute positioning, overlap, or transform was introduced.
- `tests/current/test_card_flip_layout.py` retains all existing structural and accessibility assertions and now checks that the row reserves positive internal bottom spacing without enlarging its box.
- `deployment/pages-repository-only-allowlist.txt` classifies this exact report path as repository-only before the artifact check. The deploy manifest is unchanged.
- Exact changed paths: `index.html`, `tests/current/test_card_flip_layout.py`, `deployment/pages-repository-only-allowlist.txt`, and `reports/flip-control-visual-polish-10.3.md`.

## Local visual and interaction QA

- Served the checkout on loopback and inspected the actual **Mianownik (Nominative)** Learn card at 320, 375, 390, 430, and 1024 CSS px. Both the front concept and back explanation, including “It marks the subject - the person or thing doing the action,” remained legible and unobstructed. The circular outline and shadow have breathing room without excessive blank space; the card remains visually balanced.
- Browser layout readings at all five widths showed a 55px control row, a 40px button, 4px between the button border box and rotating face, exact horizontal centering, and no document horizontal overflow. The unchanged row height avoids increasing overall card height.
- Inspected a vocabulary Learn card (`Pierwsze zwroty`) and a podcast phrase Learn card (`Toksyczna produktywność`, phrase “ulegać presji”) at 390px. Each shared the centered 4px gap, complete circle and shadow, and unobstructed text.
- Flipped grammar front/back and podcast front/back. The same single control stayed in its row while the faces rotated; the settled layout had no jump, clipping, or front/back spacing mismatch. On the podcast card, button top/left and scene height were identical before and after the reverse flip.
- Native button, changing accessible name, keyboard activation with Enter and Space, visible focus outline, logical tab order, and 40px touch target were preserved. Browser inspection found exactly one flip button in the vocabulary/podcast scene and one in the grammar scene.

## Verification

- Focused card-flip regression: **3/3 passed**. Focused Pages deployment boundary: **37/37 passed**.
- Maintained current product gate: **117/117 Python tests and all 10 JavaScript suites passed**.
- `validate_content.py`: passed; 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs; forward baseline unchanged.
- `verify_audio.py`: passed; 3,621 required phrases, 3,621 manifest entries, and 3,621 MP3 files, with none missing or orphaned.
- `verb_patterns_runtime_validator.py`: passed; 98 lemmas, 129 meanings, 269 patterns, 269 examples, 269 pronunciation-enabled examples.
- `validate_current_release.py`: passed; version, shell/audio caches, schema, and migration all valid.
- `build_pages.py --check`: passed; 23 grammar pages, 6 vocabulary pages, guide hub, and 32 sitemap URLs current without regeneration.
- `build_pages_artifact.py --check`: passed with 3,684 deploy files, 79 repository-only files, 3,763 classified tracked files, 0 overlap, and **0 unclassified**.
- Exact temporary Pages artifact build: 3,684 files, 57,436,826 bytes, 0 checksum mismatches, 0 unexpected files, 0 missing files, 0 repository-only leaks, 0 symlinks, and 0 hidden files. The artifact was removed with its temporary directory after verification.
- Final deterministic public artifact digest (manifest order, UTF-8 path, NUL, eight-byte big-endian length, contents): `c361dfaafb351536a07ca674fedef7d9ca1f1c4d322e4134c1eb647fab8d9903`. It differs from the previous candidate because deployable `index.html` changed.
- `git diff --check` and staged diff check passed. Git diff against the starting HEAD names only the four paths listed above, so generated pages and sitemap remain byte-for-byte unchanged.

## Frozen release and handoff

- `APP_VERSION` remains `10.3`; shell `CACHE` remains `popolsku-v76`; `AUDIO_CACHE` remains `popolsku-audio`; schema and content migration remain `2`.
- Generated learner pages and `sitemap.xml` are unchanged.
- This checkout has zero remotes. Nothing was pushed or deployed, and the production repository was never accessed.
- A committed report cannot contain its own final commit or tree identifier without changing those identifiers. The final commit and tree are recorded in the task completion report after the single commit.
- Independent review is required before this visual-polish commit is integrated.
