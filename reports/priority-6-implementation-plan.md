# Priority 6 — Phased Implementation Plan

**Phase:** 0 (reports-only). **No phase below has been implemented.** Each phase is independently reviewable and independently shippable.

**Baseline at time of planning:** `APP_VERSION` 8.4 · shell cache `popolsku-v59` · audio cache `popolsku-audio` · `schemaVersion` 2 · `CONTENT_MIGRATION_REVISION` 2 · 10 levels / 97 topics / 1,215 cards / 353 drills / 1,675 ids / 3,377 audio phrases.

---

## Rules applying to every phase

| Rule | Detail |
|---|---|
| **Never change** | `AUDIO_CACHE` (`popolsku-audio`) — renaming discards up to ~34 MB of cached audio for every existing user |
| **Never change without a migration** | `schemaVersion`, `CONTENT_MIGRATION_REVISION` — progress-loss risk |
| **Always bump** | `CACHE` in `sw.js` when `index.html` or any precached asset changes, or the release will not reach existing users |
| **Always bump** | `APP_VERSION` when the change is learner-visible |
| **Always run** | `validate_content.py`, `verify_audio.py`, 149 Python tests, 32 JavaScript suites — before every commit |
| **Never introduce** | cookies, identifiers, third-party scripts, or a widened CSP without a separate explicit decision |
| **Every copy change** | Requires human copy approval before implementation |

**Expected totals must not move in any phase** unless the phase explicitly adds content (only Phase 3 does, via generated pages — which add no cards, drills, or ids).

---

## File-scope categories

Every phase below lists its expected files in five categories. **A phase's "product change" and its "repository diff" are not the same thing** — the earlier draft conflated them and described Phase 1 as a pure `index.html` diff while simultaneously requiring a service-worker cache bump and a version change. That was inconsistent.

| Category | Contents |
|---|---|
| **A. Public / product behaviour** | `index.html`, `manifest.json`, page copy, styles, behaviour |
| **B. Release markers and service worker** | `sw.js` (`CACHE`), `APP_VERSION` in `index.html` |
| **C. Generated outputs** | the 31 generated pages, redirect stubs, `sitemap.xml` |
| **D. Tests** | assertion files pinned to version, cache, copy, navigation, metadata, or generated output |
| **E. Internal documentation** | release notes, internal reports |

### Repository facts that drive these lists (verified this session)

**Tests hard-asserting `APP_VERSION == "8.4"` — 8 JavaScript + 1 Python.** Any `APP_VERSION` bump changes all of them:

`test_phase2c_navigation.js:688,695,718` · `test_phase3_closeout.js:621` · `test_phase3b_mobile_layout.js:591` · `test_phase3b_focus_scroll.js:1100` · `test_phase4b1_service_worker_cache.js:2145,2168` · `test_phase4b2_offline_navigation_installability.js:298` · `test_phase4b3_audio_resilience_range_storage.js:1991` · `test_build_pages.py:628-630,650,1258,1485,1704`

**Tests hard-asserting `CACHE == "popolsku-v59"` — 5 JavaScript.** Any `CACHE` bump changes all of them:

`test_phase2c_navigation.js:721` · `test_phase3_closeout.js:626` · `test_phase4b1_service_worker_cache.js:611,615-617` · `test_phase4b2_offline_navigation_installability.js:187,299` · `test_phase4b3_audio_resilience_range_storage.js:540,1993`

`test_phase4b1_service_worker_cache.js:616-617` additionally asserts that superseded cache names (`v55`, `v57`, `v58`) are **absent**; a bump to `v60` requires extending that supersede list.

**Tests hard-asserting exact public copy:**

| Copy | Test |
|---|---|
| About's three paragraphs, verbatim | `test_phase2c_navigation.js:288` |
| Privacy intro, verbatim | `test_phase2c_navigation.js:297` |
| Privacy pronunciation sentence, verbatim (`"pre-recorded audio"`) | `test_phase2c_navigation.js:305` |
| Contact supporting paragraph, verbatim | `test_phase2c_navigation.js:316` |
| Home hero and search copy | `test_phase3_closeout.js:668-669` |
| Generated-page ending line, verbatim | `test_phase2c_navigation.js:671` · `test_phase3_closeout.js:557,562` · `test_build_pages.py:639` |
| `Home › Guide` breadcrumb on generated pages | `test_build_pages.py:1253` |
| `Home › Guide › What I listen to` breadcrumb | `test_build_pages.py:1455` |
| Committed sitemap URL set and order | `test_build_pages.py:1271-1304,1546-1551` |

### The `APP_VERSION` → generated-page coupling

**Repository finding, and the single most consequential scoping fact in this plan.** `learning_footer()` reads `APP_VERSION` from `index.html` and writes it into every generated page ([build_pages.py:637-643](build_pages.py:637)). All 31 committed generated pages currently carry `v8.4` in their footer, and `test_build_pages.py` asserts that value against freshly built pages.

**Therefore any `APP_VERSION` bump has generated-output consequences even if no generator string is edited.** A phase that bumps `APP_VERSION` without regenerating leaves the committed pages showing the previous version — a real, if cosmetic, skew that must be an explicit decision rather than an oversight. Each phase below states which choice it takes.

---

## Phase 1 — Positioning, trust, and public claims

**Objective:** make every public claim accurate and state the locked positioning. This is a claims-accuracy phase, not a marketing phase.

**Issues addressed:** R-04, R-03 (app-shell portion), R-01, R-02 (wording), R-18 · claims C-001, C-002, C-005 (app-shell surfaces), C-006, C-009, C-011 · positioning findings 1, 2, 4, 6.

### Generator strategy — the decision that defines this phase

The earlier draft of this plan was internally inconsistent: it proposed editing `build_pages.py` while simultaneously claiming that only one generated page changes, that expected files are just `index.html` and `build_pages.py`, and that the result is a pure copy diff. **Under the current generator none of those can all be true.** `build_pages.py` takes no arguments, has no dry-run mode, and regenerates unconditionally: any invocation rewrites **all 31 generated pages** and resets **every `lastmod` in `sitemap.xml`** to the run date (SEO S-9, R-13).

**Chosen strategy: defer all generator-dependent changes to Phase 3, after the generator safety work.**

| Option considered | Decision |
|---|---|
| (a) Defer generator-dependent disclosure changes to Phase 3, after generator safety work | **Chosen** |
| (b) Move the generator safety fix ahead of the first Priority 6 regeneration, then edit in Phase 1 | Rejected for Phase 1 — it turns a copy phase into a tooling phase and enlarges the first reviewable diff |
| (c) Explicitly include all 31 generated outputs and `sitemap.xml` in Phase 1 | Rejected — it makes the first and most copy-sensitive diff the largest one to review |

**Consequences of the choice, stated plainly:**

- **The only *public/product* file Phase 1 edits is `index.html`.** `build_pages.py` is **not** edited and no generator run occurs.
- **R-12 (the `/guide/listening/` disclosure, C-020) moves to Phase 3.** It is a `build_pages.py` string.
- **C-003 / R-03's generated-page portion moves to Phase 3.** It is a `build_pages.py` string.
- **C-008 (`manifest.json`) also sits outside Phase 1** for the same reason.
- **Phase 1 is *not* a "pure `index.html` diff".** It is a **public-copy-only product change**, but the complete repository diff also carries release plumbing (`sw.js`) and the tests pinned to the changed values. Describing it as a pure copy diff was inconsistent with requiring a `CACHE` bump and an `APP_VERSION` change.

### Expected files by category

| Cat. | Files | Why |
|---|---|---|
| **A. Public / product** | `index.html` | Home H1, hero sub, hero badges; About paragraphs 2–3; Privacy pronunciation sentence; Install offline note |
| **B. Release markers / SW** | `index.html` (`APP_VERSION` → next), **`sw.js`** (`CACHE` `popolsku-v59` → `popolsku-v60`) | `index.html` is precached, so the release does not reach existing users without a `CACHE` bump |
| **C. Generated outputs** | **none edited** — but see the version-skew decision below | No generator run occurs |
| **D. Tests** | `test_phase2c_navigation.js` (About copy :288, Privacy pronunciation :305, `APP_VERSION` :688/:695/:718, `CACHE` :721) · `test_phase3_closeout.js` (hero copy :668-669, `APP_VERSION` :621, `CACHE` :626) · `test_phase3b_mobile_layout.js` (:591) · `test_phase3b_focus_scroll.js` (:1100) · `test_phase4b1_service_worker_cache.js` (:2145, :611, :615-617 incl. supersede list) · `test_phase4b2_offline_navigation_installability.js` (:298, :187, :299) · `test_phase4b3_audio_resilience_range_storage.js` (:1991, :540, :1993) · `test_build_pages.py` (`APP_VERSION` :628-630, :650, :1258, :1485, :1704) | Each pins a value this phase changes |
| **E. Internal docs** | release notes | Record of what shipped |

**Nine test files (8 JS + 1 Python) are in scope.** This is anticipated, mechanical test work, not failure.

### Version-skew decision (must be explicit)

Bumping `APP_VERSION` while not regenerating leaves all 31 committed generated pages showing the previous version in their footer, because `learning_footer()` bakes the version into each page.

| Option | Consequence |
|---|---|
| **(i) Accept the skew until Phase 3 — recommended** | Generated pages read `v8.4` while the app reads `v8.5`. Cosmetic only; no functional or SEO effect. Keeps Phase 1 free of generated outputs. `test_build_pages.py` still needs its `APP_VERSION` assertions updated, because it asserts against *freshly built* pages |
| (ii) Regenerate in Phase 1 | Pulls all 31 pages **and** `sitemap.xml` `lastmod` churn into the most copy-sensitive diff, before the generator safety work exists. Rejected |

**Recommendation: (i), stated in the release notes as a known, temporary skew closed by Phase 3.**

| Aspect | Detail |
|---|---|
| **Public copy affected** | Home H1, hero sub, hero badges; About paragraphs 2–3; Privacy → Pronunciation sentence; Install offline note |
| **Generated-page impact** | No generated file is edited. **Footer version skew** per the decision above |
| **Service-worker impact** | **`CACHE` bump required**, so `sw.js` **is** in the diff |
| **Privacy impact** | Pronunciation wording clarified; no behaviour change |
| **SEO impact** | None — title and description changes are held for Phase 3 with the rest of the metadata work |
| **Automated tests** | Full suite. **Nine test files require assertion updates** (category D above). Content totals must not move |
| **Manual checks** | Hero at 320 px; badge row wrapping; About and Privacy readability; no regression in drawer or screen navigation |
| **Physical-device limitations** | Hero layout and text scaling **Require physical-device verification** |
| **Claims requiring approval** | Every wording change — **Requires human copy approval**. C-011 additionally **Requires founder confirmation** if a people-based framing is preferred over the process wording |
| **Version implications** | `APP_VERSION` → next (learner-visible) |
| **Cache implications** | `CACHE` `popolsku-v59` → `popolsku-v60`; extend the supersede list in `test_phase4b1_service_worker_cache.js:616-617`. `AUDIO_CACHE`, `schemaVersion`, `CONTENT_MIGRATION_REVISION` unchanged |
| **Integration** | Single commit. Reviewable as a **public-copy-only product change** plus release plumbing and test updates |
| **Stop conditions** | Any test failure left unresolved; any content total moving; a badge row breaking at 320 px; **any diff in `build_pages.py`, `sitemap.xml`, `manifest.json`, or any generated page — that would mean the generator was run and the phase boundary was crossed** |
| **Rollback** | Revert the commit; no data, cache, or schema migration involved |
| **Dependencies** | None — **Phase 1 is the entry point** |

---

## Phase 2 — Privacy and transparency

**Objective:** restructure Privacy into a two-level document and close the accuracy and completeness gaps.

**Issues addressed:** R-08, R-09, R-16 · privacy P-1, P-2, P-3, P-6, P-7, P-8, P-9 · claim C-017, C-018.

### Legal-review scope — what is and is not gated

The earlier draft made the whole phase contingent on legal review. **That is wrong and would stall accurate factual corrections behind a gate they do not need.**

**Not gated — factual transparency work, drafted and reviewed as ordinary factual accuracy:**

| Content | Basis |
|---|---|
| What is stored on the device (the nine `localStorage` keys) | Directly observable in code |
| Service-worker cache behaviour and footprint (P-2) | Directly observable in `sw.js` |
| What a backup contains and excludes (P-1, C-018) | Directly observable |
| What clearing browser storage does (P-8) | Directly observable |
| That external links exist and what leaving the site means (P-3) | Directly observable |
| That app-initiated fetches are same-origin, and the CSP that enforces it (P-6) | Directly observable |
| Last-updated date and a contact route (P-7, P-9) | Editorial |

Describing observable behaviour accurately is not a legal claim, and this work must **not** assert legal conclusions or imply certification.

**Gated — specific legal conclusions only, each requiring a qualified reviewer:**

| # | Gated item |
|---|---|
| L-1 | Whether the browser speech-synthesis fallback is a disclosable third-party processing activity |
| L-2 | Processor terminology — whether GitHub Pages / Cloudflare must be named as processors |
| L-3 | Polish/EU-specific obligations for a service aimed at residents of Poland |
| L-4 | Any age-assurance obligation attaching to the adult-language gate |
| L-5 | Consent obligations for any future analytics |

**If legal review is unavailable, the factual sections still ship**; the gated sentences are held back or written in plainly descriptive terms that assert no legal characterisation.

| Aspect | Detail |
|---|---|
| **Public copy affected** | Entire Privacy screen |
| **Expected files (A)** | `index.html` — the whole Privacy screen |
| **Expected files (B)** | `index.html` (`APP_VERSION` → next), **`sw.js`** (`CACHE` bump) |
| **Expected files (C)** | None edited. Footer version skew continues per the Phase 1 decision, closed by Phase 3 |
| **Expected files (D)** | `test_phase2c_navigation.js` (Privacy intro :297, pronunciation sentence :305, `APP_VERSION`, `CACHE`) · `test_phase3_closeout.js` · `test_phase3b_mobile_layout.js` · `test_phase3b_focus_scroll.js` · `test_phase4b1_service_worker_cache.js` · `test_phase4b2_offline_navigation_installability.js` · `test_phase4b3_audio_resilience_range_storage.js` · `test_build_pages.py` — **same nine files as Phase 1**, because `APP_VERSION` and `CACHE` move again |
| **Expected files (E)** | Release notes |
| **Generated-page impact** | None edited; version skew persists until Phase 3 |
| **Service-worker impact** | **`CACHE` bump required**, so `sw.js` is in the diff |
| **Privacy impact** | This *is* the privacy change — documents cache footprint, outbound links, CSP guarantee, storage clearing, backup coverage, last-updated date, contact route |
| **SEO impact** | None |
| **Automated tests** | Full suite; check accessibility suites for Privacy-screen structure assertions |
| **Manual checks** | Both levels readable on mobile; expand/collapse keyboard-operable if a disclosure pattern is used; Level 1 summary must not contradict the speech-fallback or external-link sections |
| **Physical-device limitations** | Screen-reader behaviour of any new disclosure widget **Requires physical-device verification** |
| **Claims requiring approval** | Every statement **Requires human copy approval**. **Requires legal review** applies to L-1 … L-5 only |
| **Version implications** | `APP_VERSION` → next |
| **Cache implications** | `CACHE` bump |
| **Integration** | Single commit |
| **Stop conditions** | Any factual statement that cannot be substantiated from code; any absolute phrasing that contradicts §5/§6 of the privacy audit (for example "the app only ever contacts its own domain", "no personal data", "nothing is transmitted anywhere"); any legal characterisation asserted without review. **Legal review being unavailable is not a stop condition for the factual sections** — it only holds L-1 … L-5 |
| **Rollback** | Revert |
| **Dependencies** | **Phase 1** — pronunciation wording clarified first, so Phase 2 restructures a document already free of the ambiguity |

---

## Phase 3 — SEO and social discoverability

**Objective:** resolve destination naming, add high-intent generated pages, and fix metadata gaps.

**Issues addressed:** R-05, R-06, R-13, R-17, R-19, R-21 · **plus the generator-dependent items deferred from Phase 1: R-12 (`/guide/listening/` disclosure, C-020), the generated-page portion of R-03 (C-003 offline ending), and C-008 (`manifest.json` description)** · SEO S-1 … S-7, S-9, S-10 · Explore more Polish G-1 … G-8.

**Order within the phase matters.** Commit (b) — the generator safety work — **must land before** the commits that regenerate content, so that `lastmod` churn stops before the large regenerations and a `--check` mode exists to verify drift safely.

| Aspect | Detail |
|---|---|
| **Public copy affected** | Home title + description; `/guide/` title, H1, JSON-LD name; 31 breadcrumbs; 2 redirect stubs; `<noscript>`; `manifest.json` description; **the shared generated-page ending (offline phrasing, C-003)**; **the `/guide/listening/` disclosure (C-020)**; new page copy |
| **Expected files (A)** | `build_pages.py`, `index.html`, `manifest.json` |
| **Expected files (B)** | `index.html` (`APP_VERSION` → next), **`sw.js`** — `CACHE` bump **and** `GENERATED_PAGE_ASSETS` extension for the 5–8 new pages ([sw.js:127](sw.js:127)) |
| **Expected files (C)** | All 31 regenerated pages, 5–8 new pages, both redirect stubs, `sitemap.xml`. **This phase closes the Phase 1/2 footer version skew** |
| **Expected files (D)** | `test_build_pages.py` — the largest test change of any phase: `Home › Guide` breadcrumb (:1253), `Home › Guide › What I listen to` (:1455), ending line (:639), committed sitemap URL set and order (:1271-1304, :1546-1551), `APP_VERSION` (:628-630, :650, :1258, :1485, :1704), plus new assertions for new page types · `test_phase2c_navigation.js` (ending line :671, `APP_VERSION`, `CACHE`) · `test_phase3_closeout.js` (ending line :557/:562, `APP_VERSION`, `CACHE`) · `test_phase4b1_service_worker_cache.js` (`GENERATED_PAGE_ASSETS`, `APP_VERSION` :2145/:2168, `CACHE`) · `test_phase4b2_offline_navigation_installability.js` (`GENERATED_PAGE_ASSETS`, sitemap, markers) · `test_phase4b3_audio_resilience_range_storage.js` (`GENERATED_PAGE_ASSETS`, sitemap, markers) · `test_phase3b_mobile_layout.js` · `test_phase3b_focus_scroll.js` |
| **Expected files (E)** | Release notes |
| **Generated-page impact** | **Largest of any phase** — all 31 regenerated, plus 5–8 new pages |
| **Service-worker impact** | **Two changes:** `CACHE` bump (`index.html` + `manifest.json` are precached), **and** new pages must be added to `GENERATED_PAGE_ASSETS` ([sw.js:127](sw.js:127)) or they will not be classified as generated navigations |
| **Privacy impact** | Add `noreferrer` to outbound links (R-15) |
| **SEO impact** | The point of the phase. Sitemap grows from 32 to 37–40 URLs |
| **Automated tests** | Full suite. `tests/test_build_pages.py` will need extension for new page types — **this is expected test work, not a failure** |
| **Manual checks** | Every new page renders; breadcrumbs correct on all pages; sitemap reconciles; canonical correct on new pages; social preview renders |
| **Physical-device limitations** | New-page layout at 320 px **Requires physical-device verification**; table reflow contract at [build_pages.py:120-126](build_pages.py:120) must hold |
| **Claims requiring approval** | Destination name (**blocking decision**, G-1); the chosen generated-page offline option (C-003, three options); extended recommendation disclosure (C-020); new page copy; title/description |
| **Version implications** | `APP_VERSION` → next |
| **Cache implications** | `CACHE` bump **and** `GENERATED_PAGE_ASSETS` update |
| **Integration** | **Split into 4 commits, in this order:** **(b) generator safety first** — content-derived `lastmod`, `--check` mode, `BreadcrumbList`, OG dimensions; then (a) naming resolution across existing pages; then (c) deferred Phase 1 disclosure work — generated-page offline ending (C-003), `/guide/listening/` disclosure (C-020), `manifest.json` description (C-008); then (d) new high-intent pages |
| **Stop conditions** | Destination name undecided; generated-page offline option not chosen; `test_build_pages.py` failures unresolved; any content total moves (new pages must add **no** cards, drills, or ids); **generator safety work not landed before the first bulk regeneration** |
| **Rollback** | Per-commit revert; new pages can be removed without touching existing ones |
| **Dependencies** | **Phase 1** (positioning must be settled before it is carried into metadata); **G-1 decision** |

---

## Phase 4 — First-visit activation and feedback

**Objective:** improve understanding and completion, and open a correction route.

**Issues addressed:** R-07, R-10, R-11, R-20 · activation A-2, A-3, A-4, A-6 · feedback F-1 … F-4, F-6.

| Aspect | Detail |
|---|---|
| **Public copy affected** | "More" tab label; starting-point line; completion next-step; Contact restructure; footer links; generated-page correction line |
| **Expected files (A)** | `index.html`, `build_pages.py` |
| **Expected files (B)** | `index.html` (`APP_VERSION` → next), **`sw.js`** (`CACHE` bump) |
| **Expected files (C)** | **All 31 generated pages regenerate** because the shared correction line is added to `learning_footer`/`learning_ending` output, **and `sitemap.xml` is rewritten** by the same generator run. With the Phase 3 `lastmod` fix in place, only genuinely changed pages should move their date — **verify this, do not assume it** |
| **Expected files (D)** | `test_phase2c_navigation.js` (navigation structure for the footer links row and the renamed tab, plus `APP_VERSION`/`CACHE`) · `test_build_pages.py` (the new generated-page correction line, sitemap assertions, `APP_VERSION`) · `test_phase3_closeout.js` · `test_phase3b_overlays.js` (drawer/overlay structure if the drawer changes) · `test_phase3b_mobile_layout.js` · `test_phase3b_focus_scroll.js` · `test_phase4b1_service_worker_cache.js` · `test_phase4b2_offline_navigation_installability.js` · `test_phase4b3_audio_resilience_range_storage.js` · plus the accessibility suites covering any new control (`test_phase1a_accessibility.js`, `test_phase1b_keyboard_focus.js`, `test_phase2a_core_activity_accessibility.js`) |
| **Expected files (E)** | Release notes |
| **Generated-page impact** | All 31 regenerated **and `sitemap.xml` rewritten** — this is a generator phase, not an `index.html` phase |
| **Service-worker impact** | **`CACHE` bump required**, so `sw.js` is in the diff |
| **Privacy impact** | One line about email handling; **no new data collection** |
| **SEO impact** | Footer links slightly improve internal linking |
| **Automated tests** | Full suite. `tests/test_phase2c_navigation.js` asserts navigation structure — **footer links and tab renaming will likely require test updates** |
| **Manual checks** | Keyboard operability of new controls; focus order; `mailto:` subject prefills in common clients; completion screen on mobile |
| **Physical-device limitations** | `mailto:` behaviour and completion-screen layout **Require physical-device verification**; VoiceOver/TalkBack on new controls |
| **Claims requiring approval** | Contact wording; starting-point line; correction invitation |
| **Version implications** | `APP_VERSION` → next |
| **Cache implications** | `CACHE` bump |
| **Integration** | **Split into 2 commits:** (a) activation changes, (b) feedback/contact changes |
| **Stop conditions** | Any change that adds a step before learning; any onboarding flow; navigation test failures unresolved |
| **Rollback** | Per-commit revert |
| **Dependencies** | **Phase 1** (Contact copy should reflect corrected claims); **Phase 3 required first, not merely recommended** — the generated-page correction line is a `build_pages.py` change, and the generator safety work in Phase 3 commit (b) must precede it |

---

## Phase 5 — Measurement (only after separate approval)

**Objective:** decide whether measurement is needed at all; implement only the minimum if so.

**Issues addressed:** R-14, R-24 · measurement E-2, E-3, E-7, E-8.

> **This phase is not approved.** It requires a separate, explicit human decision. The measurement report's honest recommendation is that **Search Console plus qualitative feedback may make this phase unnecessary.**
>
> **The "Approve" verdicts on E-2, E-3, E-7, and E-8 are product-decision verdicts only.** They mean those events are worth considering because they would change what gets built. They carry **no** privacy, legal, consent, or implementation approval, all of which remain open.

> **What this phase unblocks elsewhere.** Attribution for every non-Google channel depends on this phase. Without an approved mechanism, arrivals from newsletters, directories, creators, communities, and social posts are **not observable**, and no channel's contribution to meaningful-learning completions is attributable — a distinct landing path does not change that, and Search Console does not cover it. Growth and paid experiments whose success criterion is a completion stay blocked until this phase exists (growth §1, paid experiments §1a).

| Aspect | Detail |
|---|---|
| **Prerequisite (no instrumentation code)** | Configure Search Console; operate on it alone for one full cycle; then decide whether questions remain unanswered. It requires no instrumentation code in Po polsku, adds no application cookie or application-assigned identifier, and does not change what application code sends. It answers **Google Search** questions only — not referral or on-site behaviour. **Account-level, provider, disclosure, and legal implications are a separate human review question** and are not concluded by this plan |
| **Public copy affected** | Privacy "Analytics and hosting" section **must** be rewritten in the same release |
| **Expected files** | **Conditional on an architecture that has not been chosen.** The list below is what each option would imply, not a known scope |
| **Expected files (A)** | `index.html` (event emission + Privacy analytics section). If a collection endpoint is introduced it is **new infrastructure outside this repository**, with its own files, hosting, and privacy surface |
| **Expected files (B)** | `index.html` (`APP_VERSION` → next), **`sw.js`** (`CACHE` bump; also required if the worker participates in queuing or offline suppression). **A widened `connect-src` would change the CSP in `index.html` and on every generated page via `build_pages.py`** — which would pull categories C and D in as well |
| **Expected files (C)** | None **if and only if** generated pages are not instrumented and the CSP is unchanged. Instrumenting generated pages, or widening the CSP, regenerates all 31 pages and `sitemap.xml` |
| **Expected files (D)** | The nine `APP_VERSION`/`CACHE` files as in Phase 1, plus **new tests** proving no application-assigned identifier is created, no cookie is set, and nothing is emitted while offline. If the CSP changes, the CSP assertions in `test_build_pages.py` and the service-worker suites are also in scope |
| **Expected files (E)** | Release notes; updated Privacy documentation |
| **Generated-page impact** | None if generated pages are not instrumented and the CSP is unchanged; **all 31 pages plus `sitemap.xml` otherwise** |
| **Service-worker impact** | `CACHE` bump; must not break offline operation |
| **Privacy impact** | **Highest of any phase.** Falsifies claim C-015 unless the wording changes in the same release |
| **SEO impact** | None |
| **Automated tests** | Full suite plus new tests proving no application identifier is created, no cookie is set, no intentional joining occurs, and nothing is emitted while offline |
| **Manual checks** | Verify no cookie is set; verify the payload carries no application-assigned identifier and no learner content; verify offline still works. **Log-side behaviour cannot be verified from the client** and needs the endpoint's own retention and access design |
| **Physical-device limitations** | Offline behaviour with measurement present **Requires physical-device verification** |
| **Claims requiring approval** | Entire Privacy analytics section. The new wording must use the precise vocabulary of measurement §5: **no application-assigned persistent identifier, no intentional event-level or cross-visit joining, no learner-content payload, no cookie or new client identifier**, plus an explicit acknowledgement that **ordinary server and network logs may still contain IP address, user agent, timing, and path**. It must **not** claim the endpoint receives no personal data, and must **not** claim events cannot be linked across visits — logs may permit correlation. **Requires legal review** for consent obligations, for how that metadata is characterised, and for log retention, access, aggregation, and deletion |
| **Version implications** | `APP_VERSION` → next |
| **Cache implications** | `CACHE` bump |
| **Integration** | Single commit containing **both** the measurement code and the Privacy rewrite — they must never ship separately |
| **Stop conditions** | **Any** proposal requiring a cookie, a persistent identifier, or a widened `connect-src`; no same-origin collection endpoint available; legal review unavailable |
| **Rollback** | Revert; no persisted data to migrate (by design) |
| **Dependencies** | **Phase 2** (Privacy structure must exist first); separate explicit approval |

---

## Phase 6 — Launch and growth package

**Objective:** prepare assets for organic outreach. **No spending, no campaigns.**

**Issues addressed:** growth channels §1–4 · R-25.

| Aspect | Detail |
|---|---|
| **Public copy affected** | None on the product — this phase produces **internal and off-site** assets |
| **Expected files (A)** | **None by default** — this phase produces internal and off-site assets. If per-section social images are adopted (S-7), `build_pages.py` changes to reference them |
| **Expected files (B)** | **None by default.** If new image assets are added to the precache inventory, `sw.js` and `APP_VERSION`/`CACHE` come into scope and this stops being a documentation-only phase |
| **Expected files (C)** | None by default; all 31 pages plus `sitemap.xml` if per-section OG images are adopted |
| **Expected files (D)** | None by default; `test_build_pages.py` OG assertions and the service-worker precache suites if images are added |
| **Expected files (E)** | Internal outreach notes, directory copy, partner one-pager — **not published from this repository** |
| **Generated-page impact** | None by default; all 31 regenerated if per-section OG images are adopted (S-7) |
| **Service-worker impact** | None by default; precache inventory + `CACHE` bump if new assets are added |
| **Privacy impact** | None |
| **SEO impact** | Indirect, via directory backlinks |
| **Automated tests** | Full suite (regression only) |
| **Manual checks** | Social previews render; directory listings accurate |
| **Physical-device limitations** | n/a |
| **Claims requiring approval** | **All outreach wording** — must comply with the claims register and partnership boundaries |
| **Version implications** | None unless assets change |
| **Cache implications** | Only if new precached assets are added |
| **Integration** | Separate from product commits |
| **Stop conditions** | Any wording implying partnership or endorsement; any identical text copied across communities |
| **Rollback** | n/a |
| **Dependencies** | **Phases 1, 3, 4** — do not send traffic before positioning, discoverability, and feedback are in place |

---

## Phase 7 — Verification and release candidate

**Objective:** verify the accumulated changes and prepare a release candidate.

**Issues addressed:** R-22 · all prior phases.

| Aspect | Detail |
|---|---|
| **Public copy affected** | None — verification only |
| **Expected files (A–D)** | **None.** Phase 7 is verification only and must not change public, release-marker, generated, or test files. A change needed here belongs in the phase that owns it |
| **Expected files (E)** | Release notes; the release-candidate record |
| **Generated-page impact** | Verify all pages regenerate byte-identically (generator drift check) |
| **Service-worker impact** | Verify `CACHE` bumped exactly once per release; `AUDIO_CACHE` unchanged |
| **Privacy impact** | Verify the Privacy page matches actual behaviour |
| **SEO impact** | Verify sitemap reconciles; canonicals correct |
| **Automated tests** | Full suite; record commands, suites, totals, failures, skipped and unavailable checks |
| **Manual checks** | Full claims-register pass against live copy |
| **Physical-device limitations** | **This is the phase where R-22 must be resolved or formally accepted:** iPhone Safari, iPhone installed PWA, iPad, Android Chrome, Android installed PWA, VoiceOver, TalkBack, text scaling, safe areas, orientation, weak network, storage pressure, install/remove/reinstall |
| **Claims requiring approval** | Final sign-off on every changed claim |
| **Version implications** | Final `APP_VERSION` for the release |
| **Cache implications** | Final `CACHE` value confirmed |
| **Integration** | Release-candidate tag |
| **Stop conditions** | Any failing test; any unverified claim; any content total moved; physical-device verification neither completed nor formally accepted as a limitation |
| **Rollback** | Do not release |
| **Dependencies** | All prior phases |

---

## Sequencing summary

```
Phase 1 (claims + positioning)  ── entry point, no dependencies
   ├─> Phase 2 (privacy)
   ├─> Phase 3 (SEO)  ← blocked on the destination-name decision
   │      └─> Phase 4 (activation + feedback)
   │             └─> Phase 6 (growth package)
   └─> Phase 5 (measurement) ← requires Phase 2 + separate approval; may be skipped
                                     │
                                     └─> Phase 7 (verification + RC)
```

**Recommended Phase 1 scope, restated:** **public-copy changes in `index.html` only** — homepage positioning (R-04), the app-shell portion of the offline qualification (R-03), the About quality-wording change (R-01), the pronunciation-terminology change (R-02), and the "Genuinely free" alignment (R-18).

**Explicitly deferred out of Phase 1 to Phase 3**, because each lives in `build_pages.py` or `manifest.json` and would force a full regeneration: the `/guide/listening/` disclosure (R-12, C-020), the generated-page offline ending (C-003), and the `manifest.json` description (C-008).

**The complete Phase 1 repository diff is larger than the product change**, and should be reviewed as three separable parts:

| Part | Files |
|---|---|
| Public copy (the substance of the review) | `index.html` |
| Release plumbing | `index.html` `APP_VERSION`, `sw.js` `CACHE` |
| Test assertion updates | 9 files (8 JS + `test_build_pages.py`) |

**Phase 1 is therefore a public-copy-only *product* change, not a "pure `index.html` diff".** Calling it the latter contradicted its own requirement for a cache bump, a version bump, and the test updates those force.

---

## Cross-phase cache and version summary

| Phase | `APP_VERSION` | `CACHE` bump | `sw.js` in diff | Generated outputs (C) | Test files (D) |
|---|---|---|---|---|---|
| 1 | bump | **yes** → `v60` | **yes** | none edited; **footer version skew accepted** | **9** (8 JS + `test_build_pages.py`) |
| 2 | bump | **yes** | **yes** | none edited; skew persists | **9** (same set) |
| 3 | bump | **yes** + `GENERATED_PAGE_ASSETS` | **yes** | **all 31 + 5–8 new + 2 stubs + `sitemap.xml`; closes the skew** | **9+**, `test_build_pages.py` heaviest |
| 4 | bump | **yes** | **yes** | **all 31 regenerated + `sitemap.xml`** | **9+** incl. navigation, overlay, accessibility suites |
| 5 | bump | **yes** | **yes** | none **iff** pages uninstrumented and CSP unchanged; otherwise all 31 + `sitemap.xml` | **9 + new**; **conditional on architecture** |
| 6 | only if assets change | conditional | only if assets change | none by default; all 31 + `sitemap.xml` if per-section OG images adopted | none by default |
| 7 | final | confirm once, do not move | **verify byte-identical regeneration**; edit nothing | verification only | verification only |

**`AUDIO_CACHE` (`popolsku-audio`), `schemaVersion` 2, and `CONTENT_MIGRATION_REVISION` 2 must remain unchanged across all seven phases.**

**Two rules this table enforces**, both violated by the earlier draft:

1. **A `CACHE` bump always puts `sw.js` in the diff.** A phase cannot require the bump and also claim it touches only `index.html`.
2. **Moving `APP_VERSION` or `CACHE` always puts test files in the diff** — at minimum the nine listed in the file-scope section, because each pins one of those values.
