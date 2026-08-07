# Priority 6 Phase 4D — Contact CTA Polish

## 1. Precondition result

All checks passed before any edit was made:

| Check | Expected | Observed | Result |
|---|---|---|---|
| Repository | `/Users/Kaj/Downloads/Repository for Claude - Priority 6 Phase 4D` | match | PASS |
| Branch | `priority-6-phase-4d-contact-cta-polish` | match | PASS |
| Baseline HEAD | `3d28ef995e65672297e8602bc7cf970c12f0bf16` | match | PASS |
| Baseline tree | `f7a3ec3fbbc4e6618573a773deb6a849ba365dd4` | match | PASS |
| Working tree | clean | clean | PASS |
| Remotes | none | none | PASS |
| `.git/objects/info/alternates` | absent | absent | PASS |
| Linked worktree | no | no (`.git` is a real directory; `git worktree list` shows one entry) | PASS |

## 2. Exact implementation

Two visual/product changes, both on the Contact screen in [index.html](index.html):

**A. Spacing above the email CTA**
`.contact-email { margin-top: 4px }` → `margin-top: 20px`. This reuses the same `20px` spacing token already used elsewhere on the page (`.privacy-section`, `.about-contact`), adding 16px of extra separation above the button while leaving `.privacy-list { gap: 16px }` (spacing between the four bullets) untouched.

**B. Visible CTA text**
- Before: `<a class="contact-email" href="mailto:hello@popolsku.app">[icon]Email hello@popolsku.app</a>`
- After: `<a class="contact-email" href="mailto:hello@popolsku.app" aria-label="Email hello@popolsku.app">[icon]hello@popolsku.app</a>`

The visible word "Email" is removed; the icon is unchanged (still `aria-hidden="true" focusable="false"`); the accessible name is restored via `aria-label="Email hello@popolsku.app"` so assistive technology still announces the same name as before. The `mailto:` href is unchanged — still exactly `mailto:hello@popolsku.app`, no query string.

## 3. Exact spacing/CSS change

```diff
- .contact-email{display:inline-flex;align-items:center;justify-content:center;gap:8px;margin-top:4px;
+ .contact-email{display:inline-flex;align-items:center;justify-content:center;gap:8px;margin-top:20px;
```

## 4. CTA before/after

| | Before | After |
|---|---|---|
| Visible text | `[✉] Email hello@popolsku.app` | `[✉] hello@popolsku.app` |
| Accessible name | `Email hello@popolsku.app` (from visible text) | `Email hello@popolsku.app` (from `aria-label`) |
| href | `mailto:hello@popolsku.app` | `mailto:hello@popolsku.app` (unchanged) |
| Gap above button | 4px | 20px |

## 5. Accessible-name contract

- `aria-label="Email hello@popolsku.app"` is the sole source of the accessible name (no `aria-labelledby`, no `title`).
- Icon stays `aria-hidden="true" focusable="false"`, so it never contributes to the name.
- Verified live in the browser: `getAttribute('aria-label')` returns exactly `Email hello@popolsku.app`; `textContent` is exactly `hello@popolsku.app`.

## 6. Files changed

**Product code (1 file, hand-edited):**
- [index.html](index.html) — `.contact-email` spacing, CTA markup, `APP_VERSION`

**Service worker (1 file, hand-edited):**
- [sw.js](sw.js) — `CACHE` constant

**Generator-owned pages (regenerated via `python3 build_pages.py`, not hand-edited — 30 files):**
- `grammar/*/index.html` (23 files)
- `vocabulary/*/index.html` (6 files)
- `guide/index.html`, `guide/listening/index.html`
- `sitemap.xml`

**Tests (8 files, hand-edited):**
- [tests/test_phase2c_navigation.js](tests/test_phase2c_navigation.js) — Contact CTA visible text, new aria-label assertion, release markers
- [tests/test_phase3_closeout.js](tests/test_phase3_closeout.js) — Contact CTA visible text, aria-label contract, new CSS spacing assertions, release markers
- [tests/test_phase3b_mobile_layout.js](tests/test_phase3b_mobile_layout.js) — Contact CTA visible text, release marker
- [tests/test_phase3b_focus_scroll.js](tests/test_phase3b_focus_scroll.js) — release marker
- [tests/test_phase4b1_service_worker_cache.js](tests/test_phase4b1_service_worker_cache.js) — shell cache revision (`popolsku-v64` → `popolsku-v65`) throughout
- [tests/test_phase4b2_offline_navigation_installability.js](tests/test_phase4b2_offline_navigation_installability.js) — release markers
- [tests/test_phase4b3_audio_resilience_range_storage.js](tests/test_phase4b3_audio_resilience_range_storage.js) — release markers
- [tests/test_build_pages.py](tests/test_build_pages.py) — `APP_VERSION` pin

42 files changed in total.

## 7. Release-marker changes

| Marker | Before | After |
|---|---|---|
| `APP_VERSION` (index.html) | `8.9` | `8.10` |
| Shell cache (`sw.js` `CACHE`) | `popolsku-v64` | `popolsku-v65` |
| `AUDIO_CACHE` | `popolsku-audio` | `popolsku-audio` (unchanged) |
| `schemaVersion` | `2` | `2` (unchanged) |
| `CONTENT_MIGRATION_REVISION` | `2` | `2` (unchanged) |

## 8. Generated-output impact

Ran `python3 build_pages.py` from repo root. 32 files changed (23 grammar pages, 6 vocabulary pages, `guide/index.html`, `guide/listening/index.html`, `sitemap.xml`). The diff on every generated page is exactly the footer version string (`v8.9` → `v8.10`); `sitemap.xml`'s diff is exactly the `<lastmod>` dates advancing to today (2026-08-07), which is expected deterministic generator behavior on any regeneration, not content drift. `python3 build_pages.py --check` now exits 0 ("committed output is current").

No generator-owned page was hand-edited.

## 9. Tests and validation

**Contact CTA / release-marker test updates**, all owning-suite assertions rewritten to match the new contract (visible text `hello@popolsku.app`, `aria-label="Email hello@popolsku.app"`, `.contact-email` `margin-top: 20px`, `.privacy-list` `gap: 16px` unchanged, `APP_VERSION 8.10`, shell cache `popolsku-v65`). No unrelated assertion was weakened.

**Validation run from repo root, in order:**

1. `python3 validate_content.py` — **PASS** (levels=10, topics=97, cards=1215, drills=353, 1675 unique ids)
2. `python3 verify_audio.py` — **PASS** (3,377 required phrases checked against 3,377 manifest entries and 3,377 MP3s on disk; nothing orphaned)
3. `python3 -m unittest discover -s tests -p 'test_*.py'` — **PASS**, 175 tests, 0 failures
4. every `tests/*.js` via `osascript -l JavaScript` — **PASS**, 32 suites, 9,670 assertions, 0 failures
5. `python3 build_pages.py --check` — **PASS**, exit 0, committed output current
6. `git diff --check` — **PASS**, no whitespace errors, exit 0

**Recorded counts:**
- Python test count: 175
- JS suite count: 32
- JS assertion count: 9,670
- Failure count (all validation steps combined): 0
- Generated-page count: 31 (23 grammar + 6 vocabulary + `guide/index.html` + `guide/listening/index.html`)
- Sitemap URL count: 32
- Content/audio totals: unchanged (1,675 unique ids; 3,377 audio phrases/manifest entries/MP3s)
- Final version/cache markers: `APP_VERSION = "8.10"`, shell cache `popolsku-v65`, `AUDIO_CACHE = "popolsku-audio"`, `schemaVersion = 2`, `CONTENT_MIGRATION_REVISION = 2`

## 10. Local visual check

Served the repo root with `python3 -m http.server` and inspected the Contact screen in-browser at desktop (800px) and mobile (375px) widths:

- Final bullet ("Something else: …") no longer crowds the CTA; the added 20px gap reads as modest, not excessive.
- CTA text reads only `hello@popolsku.app`; the envelope icon stays left-aligned and unshrunk.
- No overflow or wrapping regression at either width.
- Footer shows only `Po polsku · v8.10 · 2026` (single version line, no duplicate navigation).
- No console errors in the browser during navigation to Contact or at either viewport width.
- DOM inspection confirmed `href="mailto:hello@popolsku.app"` (no query string) and `aria-label="Email hello@popolsku.app"`.

## 11. Unresolved observations

- None remaining. The stale test label noted in the first pass of this report (`D1 shell cache is v61` in `tests/test_phase4b2_offline_navigation_installability.js`) was corrected in the final correction pass below (§13).
- Cloudflare Email Address Obfuscation was not touched or worked around, per instructions.

## 12. Final commit/tree

- Commit message: `Polish Priority 6 contact CTA`
- Parent: `3d28ef995e65672297e8602bc7cf970c12f0bf16` (the baseline HEAD — this commit is a direct, single-commit descendant of it)
- Branch: `priority-6-phase-4d-contact-cta-polish`
- Working tree after commit: clean
- Remotes: none

(The exact commit and tree hash are necessarily self-referential — including this report's own bytes changes them — so they are not pinned as a literal value here. Run `git log -1` / `git rev-parse HEAD HEAD^{tree}` on this branch for the authoritative values; they were reported to the user in the chat response that completed this task.)

## 13. Final correction pass (pre-integration)

A second, test/documentation-only pass, applied before Phase 4D integration and folded into the same local commit (no separate commit created):

1. **[tests/test_phase4b1_service_worker_cache.js](tests/test_phase4b1_service_worker_cache.js)** — the A4 exhaustive `isObsoleteShellCache` predicate table and the A5 activation-cleanup fixture previously jumped straight from `popolsku-v63` (obsolete) to `popolsku-v65` (current), skipping the immediately-superseded `popolsku-v64` entirely. Added `['popolsku-v64', true]` to A4, seeded `'popolsku-v64': {}` in A5, and added `'popolsku-v64'` to A5's expected deleted-cache list. This now explicitly proves that a learner who was still on the prior `v64` shell has that cache removed on `v65` activation, closing the coverage gap left by the version-bump find/replace in §6.
2. **[index.html](index.html)** — the `.contact-email` explanatory comment (directly above the rule) said "Label, mailto target and the 43px touch height are unchanged," which stopped being true once §2.B removed the visible word "Email." Reworded to keep the original responsive-history explanation (why the address is bounded and allowed to wrap) while accurately stating that the mailto target and touch height are unchanged and the visible label was later simplified in Phase 4D. No CSS rule or rendered behavior changed — comment only.
3. **[tests/test_phase4b2_offline_navigation_installability.js](tests/test_phase4b2_offline_navigation_installability.js)** — the D1 assertion label read `'D1 shell cache is v61'` while the assertion itself checked `popolsku-v65`; corrected the descriptive label to `'D1 shell cache is v65'`. Assertion logic and expected value were not touched.

**Constraints honored:** `APP_VERSION` stayed `8.10`; shell cache stayed `popolsku-v65`; no other files were touched; `python3 build_pages.py --check` still exits 0 (no regeneration was required or performed).

**Re-run validation after this pass, from repo root:**

1. `python3 validate_content.py` — **PASS** (unchanged: 1,675 unique ids)
2. `python3 verify_audio.py` — **PASS** (unchanged: 3,377/3,377)
3. `python3 -m unittest discover -s tests -p 'test_*.py'` — **PASS**, 175 tests, 0 failures
4. every `tests/*.js` via `osascript -l JavaScript` — **PASS**, 32 suites, 9,670 assertions (+1 vs. the first pass, from the new A5 deleted-cache-list entry — not a net-new test row, since the same eq() call now carries one more element), 0 failures
5. `python3 build_pages.py --check` — **PASS**, exit 0, no regeneration needed
6. `git diff --check` — **PASS**, exit 0

This correction pass was amended into the existing local Phase 4D commit rather than added as a second commit, per instruction to produce one clean final Phase 4D commit.
