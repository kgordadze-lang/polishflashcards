# Priority 6 Phase 4C — Contact and Footer Refinement

Review report for the tightly scoped post-release refinement described in the Phase 4C
brief. Work was performed entirely inside this repository, on the branch named below.

## 1. Precondition gate

All preconditions verified before any file was changed:

| Check | Result |
|---|---|
| Repository path | `/Users/Kaj/Downloads/Repository for Claude - Priority 6 Phase 4C` — confirmed |
| Branch | `priority-6-phase-4c-contact-footer-refinement` — confirmed |
| Baseline HEAD | `58344c06194b2203ae17ed6596f89b4438d08aaf` — confirmed (`git rev-parse HEAD`) |
| Baseline tree | `102999355f140ae9868e173bb6432b513538df28` — confirmed (`git rev-parse HEAD^{tree}`) |
| Working tree clean | Confirmed (`git status --porcelain` empty) |
| No Git remotes | Confirmed (`git remote -v` empty) |
| No alternate object store | Confirmed (`.git/objects/info/alternates` does not exist) |
| Not a linked worktree | Confirmed (`.git` is a real directory; `git worktree list` shows exactly one entry, this one) |
| Baseline commit exists locally | Confirmed (`git cat-file -e` on the baseline SHA succeeded) |
| Baseline tree matches | Confirmed (`git cat-file -e` on the baseline tree SHA succeeded, and it equals `HEAD^{tree}` above) |

No precondition failed. Implementation proceeded.

## 2. Exact approved changes implemented

### A. Contact screen simplification
Replaced four repeated `<div class="privacy-section">` blocks — each with its own `<h2>`,
supporting `<p>`, and a `mailto:` button carrying a distinct `?subject=` — with:
- the unchanged `<h1>Contact</h1>` and lead sentence,
- one new introductory sentence, exact text: `Email me about any of the following:`
- one semantic `<ul class="privacy-list"><li>…</li></ul>` with the four approved
  label/guidance pairs, labels marked up with `<strong>`,
- exactly one `<a class="contact-email" href="mailto:hello@popolsku.app">` at the end,
  visible text `Email hello@popolsku.app`, no `aria-label` (the accessible name now comes
  directly from the visible text), envelope icon retained and still `aria-hidden`.

No new CSS was added. The four-item list reuses the existing `.privacy-list` rule
(already shipped for the Privacy screen's summary list); the only CSS edit was extending
the existing `.privacy-list li b{…}` selector to also cover `.privacy-list li strong{…}`,
since the bold labels use `<strong>` per the brief. `.privacy-section`, `.privacy-card`,
`.privacy-wrap`, `.contact-lead` and `.contact-email` remain in use elsewhere (Privacy
screen and the one remaining Contact button) and were left untouched.

### B. Duplicate app-shell footer navigation removed
Removed the `<nav class="foot-guides" id="footGuides" aria-label="About this site">` row
(About · Privacy · Explore more Polish · Contact) from `<footer>` in `index.html`, along
with its delegated click handler (`$("footGuides").addEventListener("click", …)`) in the
shipped script. The `<div class="foot-version">` line is untouched and is now the
footer's only content. The CSS rules that existed solely to style the removed row
(`.foot-guides`, `.foot-guides a`, `.foot-guides a:hover`, `.foot-guides a:focus-visible`,
`.foot-sep`, `.foot-guides .foot-version`) were removed as dead code left behind by the
row's removal; `.foot-version` itself, and unrelated pre-existing unused rules
(`.foot-note`, `.foot-link`) that predate this change, were left alone.

The drawer/menu (`<nav aria-label="Site menu">` inside `#siteDrawer`) was not touched:
same items, same order, same behaviour.

## 3. Files changed

```
index.html                                                    (Contact markup + CSS, footer markup, JS handler removal, APP_VERSION)
sw.js                                                          (CACHE constant)
grammar/*/index.html                                          (23 files — deterministic version-footer regeneration only)
guide/index.html                                               (deterministic version-footer regeneration only)
guide/listening/index.html                                     (deterministic version-footer regeneration only)
vocabulary/*/index.html                                       (6 files — deterministic version-footer regeneration only)
tests/test_phase2c_navigation.js                              (Contact + footer-row test contract)
tests/test_phase3_closeout.js                                 (Contact email-control test contract, version/cache pins)
tests/test_phase3b_focus_scroll.js                             (version pin)
tests/test_phase3b_mobile_layout.js                            (Contact reflow contract, version pin)
tests/test_phase4b1_service_worker_cache.js                    (cache-name literal, obsolete-cache boundary shift)
tests/test_phase4b2_offline_navigation_installability.js       (version/cache pins)
tests/test_phase4b3_audio_resilience_range_storage.js          (version/cache pins)
tests/test_build_pages.py                                      (version pin, "guide/" surface-count contract)
```

41 files changed: 300 insertions(+), 511 deletions(-). No file outside this list was
touched. `sitemap.xml` was regenerated by the tool but produced no byte differences
(membership and `<lastmod>` values were already dated to today from the prior commit), so
it does not appear in `git status`.

## 4. Contact structure — before and after

**Before:** H1, lead sentence, one supporting sentence ("Choose the option that fits
best…"), then four repeated blocks, each an `<h2>` + a paragraph + a
`<a class="contact-email" href="mailto:hello@popolsku.app?subject=…">` button whose
visible text was just the bare address (`hello@popolsku.app`) with the word "Email"
carried only in `aria-label`.

**After:** H1, lead sentence (unchanged), one intro sentence, one `<ul>` of four `<li>`
items (bold label + guidance sentence each), and one
`<a class="contact-email" href="mailto:hello@popolsku.app">` button whose visible text is
`Email hello@popolsku.app` (no `aria-label` needed or present).

## 5. Final mailto contract

- Route: `mailto:hello@popolsku.app` — exactly one, no query string of any kind.
- No `subject`, `body`, `cc`, or `bcc` parameter.
- Visible text and accessible name: `Email hello@popolsku.app` (identical, since the
  name is derived from the link's own text content rather than a separate label).
- Plain static `<a>` markup, no script involvement — remains usable if Cloudflare Email
  Address Obfuscation rewrites the deployed markup, and works with JavaScript disabled.
- Icon retained (inline SVG envelope, `aria-hidden="true"`, `focusable="false"`).

## 6. Footer/navigation impact

- The four-link footer row (About · Privacy · Explore more Polish · Contact) is gone from
  the main app shell.
- The version line footer is unchanged in markup and behaviour; after the version bump it
  renders `Po polsku · v8.9 · 2026` (verified live in a browser against the local build).
- Standalone generated pages (`grammar/`, `vocabulary/`, `guide/`) were never part of the
  app-shell footer and are unaffected beyond the deterministic version-footer text update
  described in §8.

## 7. Drawer navigation — confirmed unchanged

The drawer (`#siteDrawer` → `<nav aria-label="Site menu"><ul class="site-nav-list">`)
still lists, in the same order: About, Install, Privacy, What else I listen to, Explore
more Polish, Contact. Markup, item order, and the drawer's open/close/focus behaviour were
not touched by this change (confirmed by the unmodified `git diff` for that block, and by
`tests/test_phase2c_navigation.js` section A, which was not edited and still passes).

## 8. Release-marker changes

| Marker | Before | After |
|---|---|---|
| `APP_VERSION` (`index.html`) | `8.8` | `8.9` |
| Shell cache `CACHE` (`sw.js`) | `popolsku-v63` | `popolsku-v64` |
| `AUDIO_CACHE` (`sw.js`) | `popolsku-audio` | unchanged |
| `PP_MIGRATE.SCHEMA_VERSION` | `2` | unchanged |
| `PP_MIGRATE.CONTENT_MIGRATION_REVISION` | `2` | unchanged |

## 9. Generated-output impact

`python3 build_pages.py` (write mode) was run once, after the `APP_VERSION` bump, to
propagate `v8.9` into every committed generated page's footer. It rewrote exactly 31
files: 23 grammar pages, 6 vocabulary pages, `guide/index.html`, and
`guide/listening/index.html`. No generated page's navigation, headings, body content, or
JSON-LD changed — the diff on each file is a single line (the footer's
`&middot; v8.8 &middot; 2026` → `&middot; v8.9 &middot; 2026`). `sitemap.xml` was
regenerated but produced byte-identical output (still 32 URLs, same order, same
`<lastmod>` values, since those pages were already dated to today from the prior
commit) — it is not part of this change's file list. A follow-up `build_pages.py --check`
confirms committed output is current.

## 10. Test and validation results

All commands run from the repository root, after the implementation and test-suite
changes described above.

| Check | Result |
|---|---|
| `python3 validate_content.py` | Passed — levels=10, topics=97, cards=1215, drills=353, unique ids=1675 |
| `python3 verify_audio.py` | Passed — 3377 required phrases checked against 3377 manifest entries and 3377 MP3s on disk; nothing orphaned |
| `python3 -m unittest discover -s tests -p 'test_*.py'` | Passed — 175 tests, 0 failures |
| `tests/*.js` via `osascript -l JavaScript` | Passed — 32 files, 9665 assertions, 0 failures |
| `python3 build_pages.py --check` | Passed — committed output current, 23 grammar + 6 vocabulary pages + `/guide/` hub, sitemap lists 32 URLs |
| `git diff --check` | Clean — no whitespace errors |
| Working tree after final commit | Clean (verified below, §12) |
| Git remotes | None |
| Alternate object store | None (`.git/objects/info/alternates` absent) |

Recorded totals:
- Content totals: levels=10, topics=97, cards=1215, drills=353, unique ids=1675
- Audio totals: 3377 required phrases / 3377 manifest entries / 3377 MP3s on disk
- Python test count: 175
- JavaScript suite count: 32 files
- JavaScript assertion count: 9665
- Failure count: 0 (across content, audio, Python, JavaScript, and build-check validation)
- Generated-page count: 31 regenerated (23 grammar + 6 vocabulary + guide hub + guide/listening)
- Sitemap URL count: 32 (unchanged)
- Final `APP_VERSION`: 8.9
- Final shell cache: `popolsku-v64`
- Final audio cache: `popolsku-audio` (unchanged)

A local `python3 -m http.server` build was also opened in a browser to visually confirm
the Contact screen (intro sentence, four bulleted reasons, one button) and the footer
(`Po polsku · v8.9 · 2026`, no nav row); the accessibility tree was inspected directly and
reports the Contact button's accessible name as exactly `Email hello@popolsku.app` with
`href="mailto:hello@popolsku.app"`. No console errors were observed.

`ResourceWarning` messages about unclosed files were observed from `pp_audio_rule.py` /
`build_pages.py` during the Python test run; these are pre-existing, unrelated to this
change, and did not cause any test failure, so they are noted here per instruction and not
otherwise acted on.

## 11. Non-goals — confirmed unchanged

Verified by inspecting the diff (§3) and by the fact that no unrelated test assertion
needed to change: no analytics/telemetry/tracking/cookies/identifiers were added; Privacy
wording is untouched; the Home hero is untouched; the start-guidance sentence is
untouched; the More tab name is untouched; activity completion screens are untouched;
Flashcards, Listening, Type It, Mixed Quiz, Grammar, Conversations, and Podcasts are
untouched; content data and audio files are untouched (`verify_audio.py` and
`validate_content.py` both pass against the unmodified data files); the drawer's design
and item order are untouched; generated-page learning content is untouched beyond the
deterministic version-footer text; no dependency, framework, API, build system, or
external service was added; no unrelated report was modified.

## 12. Unresolved observations

- Two footer-adjacent CSS rules, `.foot-note` and `.foot-link`, are unused in the shipped
  markup and were already unused before this change (they do not style the removed
  footer row). They were left alone per the "no opportunistic cleanup" instruction; noted
  here for a future, separately scoped cleanup if desired.
- No other issues were identified in scope for this refinement.

## 13. Final commit and tree

This report is committed together with the code and test changes it describes, in the one
commit specified by the brief (`Refine Priority 6 contact and footer`). Because a file
cannot contain the hash of the commit it is itself part of, the resulting commit and tree
SHAs are not embedded here; they are recorded in `review/head.txt` and `review/tree.txt`
in the accompanying review archive, and were reported directly to the requester after the
commit was made.
