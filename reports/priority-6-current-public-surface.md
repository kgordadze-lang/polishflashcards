# Priority 6 — Current Public-Surface Inventory

**Phase:** 0 (reports-only)
**Repository state:** branch `priority-6-phase-0-audit`, HEAD `91fa7c00ebdf76282908e3efccf7134078f685b7`, tree `d1806488b4ae94aa0f3c6bd76fc16f8cd5af3e90`
**Status:** internal recommendation document. Nothing here has been implemented.

Evidence labels used throughout this report set:

| Label | Meaning |
|---|---|
| **Repository finding** | Directly observable in a file in this repository |
| **Supported inference** | Reasoned from repository evidence, not directly stated |
| **Assumption requiring validation** | Plausible but unverified |
| **Requires live-browser verification** | Needs a rendered page |
| **Requires physical-device verification** | Needs real iPhone / iPad / Android hardware |
| **Requires Search Console access** | Needs Google Search Console |
| **Requires analytics or traffic access** | Needs traffic data that does not exist yet |
| **Requires external web research** | Needs off-repository research |
| **Requires legal review** | Needs a qualified reviewer |
| **Requires human copy approval** | Wording decision reserved for the founder |

---

## 1. Surface counts (Repository finding)

| Category | Count | Evidence |
|---|---:|---|
| HTML documents in repository | 34 | filesystem walk, excluding `.git/`, `audio/`, `tests/`, `fonts/` |
| Indexable HTML pages | 32 | 34 minus two `noindex` redirect stubs |
| URLs in `sitemap.xml` | 32 | [sitemap.xml](sitemap.xml) |
| `noindex` redirect stubs | 2 | [grammar/index.html:7](grammar/index.html:7), [vocabulary/index.html:7](vocabulary/index.html:7) |
| Generated grammar pages | 23 | `grammar/<slug>/index.html` |
| Generated vocabulary pages | 6 | `vocabulary/<slug>/index.html` |
| Application screens inside the SPA | 11 | `<section class="screen">` in [index.html](index.html) |
| Outbound external destinations | 4 | 3 on `/guide/listening/`, 3 podcast episode links in-app (YouTube) |

**Sitemap reconciliation (Repository finding).** Every one of the 32 indexable pages appears in `sitemap.xml`, and every sitemap entry corresponds to a file on disk. There are no dead sitemap entries and no indexable orphans missing from the sitemap. The two `noindex` stubs are correctly excluded.

---

## 2. Root application — `https://popolsku.app/`

**Source:** [index.html](index.html) (337 KB single-file SPA)

| Property | Value | Evidence |
|---|---|---|
| Title | `Po polsku - learn the Polish you'll actually use` | [index.html:7](index.html:7) |
| Meta description | `Polish flashcards with Polish pronunciation audio - everyday vocabulary, useful grammar, conversation practice, and phrases from real podcasts.` | [index.html:8](index.html:8) |
| Canonical | `https://popolsku.app/` | [index.html:9](index.html:9) |
| `lang` | `en` | [index.html:2](index.html:2) |
| H1 (home) | `Learn the Polish you'll actually use.` | [index.html:1077](index.html:1077) |
| Hero sub | same text as the meta description | [index.html:1079](index.html:1079) |
| Hero badges | `Completely free`, `No account needed` | [index.html:1083](index.html:1083), [index.html:1087](index.html:1087) |
| OG | type/site_name/locale/url/title/description/image + width, height, type, alt | [index.html:17-27](index.html:17) |
| Twitter | `summary_large_image` + title/description/image/image:alt | [index.html:28-32](index.html:28) |
| Structured data | `WebApplication`, `isAccessibleForFree: true`, `offers` price 0 | [index.html:43-59](index.html:43) |
| CSP | `default-src 'self'` — all fetch directives same-origin | [index.html:38](index.html:38) |
| Referrer policy | `strict-origin-when-cross-origin` | [index.html:39](index.html:39) |
| Manifest | `manifest.json` | [index.html:12](index.html:12) |

**Purpose:** the learning product itself. **Intended audience:** the copy names no audience, level, or country (see §11 of the positioning audit). **Primary call to action:** none explicit — the topic list is the CTA, rendered directly beneath the hero.

**Screens inside the SPA (Repository finding).** Eleven `<section class="screen">` elements: `home`, `study`, `grammar`, `convo`, `typeit`, `listen`, `round`, `privacy`, `about`, `contact`, `install` — [index.html:1060](index.html:1060) onward. Four are reachable as deep links (`#about`, `#privacy`, `#contact`, `#install`) via [index.html:2303](index.html:2303).

**Crawlability:** the home screen's topic list is rendered by JavaScript from `data-*.js` ([index.html:5536](index.html:5536)); only the hero, badges, search box, and the `<noscript>` block are in the served HTML. **Requires live-browser verification** to confirm what a rendering crawler indexes.

**Inconsistency.** The `<noscript>` fallback calls the secondary destination "grammar & vocabulary guide" ([index.html:1052](index.html:1052)) — stale naming, see the Explore more Polish audit.

**Dead style rules.** `.foot-guides` is defined at [index.html:639-644](index.html:639) but no element in the document uses that class; the footer contains only the version line ([index.html:1705](index.html:1705)). **Supported inference:** a footer links row was removed and its CSS was left behind.

---

## 3. In-app destinations

### 3.1 About — `/#about`

**Source:** [index.html:1613-1632](index.html:1613)

| Property | Value |
|---|---|
| H1 | `About` |
| Purpose | founder story, product summary, free/no-account restatement |
| Public claims | see claims register `C-011`–`C-014` |
| CTA | none |

Exact wording (three paragraphs), [index.html:1626-1628](index.html:1626):

> I'm a foreigner living in Poland, learning Polish while studying for a master's degree - and trying to use the language in everyday life, not just in a textbook. Po polsku began as a simple way to remember the words and phrases I kept needing in real situations.

> It has grown into a practical learning app with vocabulary, grammar, listening, typing, mixed quizzes, conversations, and pronunciation audio. I review and improve the content continuously, with help from native Polish speakers around me, including my teacher.

> Po polsku is completely free, requires no account, and keeps your learning progress on your device. It is built for learners who want Polish they can understand, remember, and actually use.

### 3.2 Privacy — `/#privacy`

**Source:** [index.html:1565-1611](index.html:1565)

| Property | Value |
|---|---|
| H1 | `Privacy - your data stays yours` |
| Sections | Your learning data · Analytics and hosting · Pronunciation · Progress and backups |
| Trust signals | no account, no learner profile, no analytics, local storage |
| Interactive | Back up my progress / Restore from backup buttons |

Full analysis in the privacy and data-flow audit.

### 3.3 Contact — `/#contact`

**Source:** [index.html:1634-1653](index.html:1634)

| Property | Value |
|---|---|
| H1 | `Contact` |
| Lead (h2) | `Have an idea, want to collaborate, or simply want to connect?` |
| Mechanism | single `mailto:hello@popolsku.app` link, [index.html:1649](index.html:1649) |
| Accessible name | `Email hello@popolsku.app` |
| Guidance offered | none |

### 3.4 Install — `/#install`

**Source:** [index.html:1655-1701](index.html:1655)

| Property | Value |
|---|---|
| H1 | `Install` |
| Content | native install button (when available), iPhone & iPad (Safari) steps, Android (Chrome) steps |
| Claims | "works offline", "No app store, no account", "runs offline" |

Platform coverage is iOS Safari and Android Chrome only; desktop browsers are installable but undocumented. **Repository finding.**

---

## 4. Explore more Polish — `https://popolsku.app/guide/`

**Source:** [guide/index.html](guide/index.html), generated by [build_pages.py:790-830](build_pages.py:790)

| Property | Value | Evidence |
|---|---|---|
| Navigation label | `Explore more Polish` | [index.html:1749](index.html:1749) |
| Page title | `Polish guide - grammar, slang and idioms explained simply \| Po polsku` | [guide/index.html:7](guide/index.html:7), generator [build_pages.py:796](build_pages.py:796) |
| H1 | `Polish, explained simply` | [guide/index.html:126](guide/index.html:126) |
| Breadcrumb | `Home › Guide` | [build_pages.py:809](build_pages.py:809) |
| Structured data | `CollectionPage`, `"name": "Polish guide"` | [build_pages.py:802](build_pages.py:802) |
| Canonical | `https://popolsku.app/guide/` | [guide/index.html:9](guide/index.html:9) |
| Lede | `Built by a foreigner living in Poland and learning the language through everyday life - with practical flashcards, clear explanations, pronunciation audio, and free interactive practice for every topic.` | [guide/index.html:126](guide/index.html:126) |

**Three different names for one destination**: menu label, page title, and H1 all differ. Full treatment in the Explore more Polish audit.

**Internal links out:** 23 grammar pages, 6 vocabulary pages, `/guide/listening/`, and two links to `/` — [guide/index.html:126](guide/index.html:126).

**Note (Repository finding):** the `/guide/` lede is the single strongest statement of the locked founder positioning anywhere on the site, and it sits on a secondary page rather than the homepage.

---

## 5. What else I listen to — `https://popolsku.app/guide/listening/`

**Source:** [guide/listening/index.html](guide/listening/index.html), generator [build_pages.py:845-920](build_pages.py:845)

| Property | Value | Evidence |
|---|---|---|
| Navigation label | `What else I listen to` | [index.html:1746](index.html:1746) |
| Title | `Polish podcasts worth listening to \| Po polsku` | [build_pages.py:849](build_pages.py:849) |
| H1 | `What else I listen to` | [build_pages.py:865](build_pages.py:865) |
| Breadcrumb | `Home › Guide › What I listen to` | [build_pages.py:863-864](build_pages.py:863) |
| Structured data | `Article`, headline `What else I listen to` | [build_pages.py:856](build_pages.py:856) |
| Recommended creators | Real Polish (realpolish.pl), Polish with Kamil (YouTube + Patreon), Ratio viva (YouTube) | [guide/listening/index.html:126](guide/listening/index.html:126) |
| Disclosure | `These are personal recommendations. None of the creators paid to be included here.` | [build_pages.py:914](build_pages.py:914) |
| External link attributes | `target="_blank" rel="noopener"` (4 links) | [guide/listening/index.html:126](guide/listening/index.html:126) |

**Breadcrumb says "What I listen to"; the H1 and the menu say "What else I listen to."** Repository finding.

**Disclosure gap.** Two of the four points required by the Phase 0 brief are present (personal; nobody paid). Absent: that inclusion implies no formal partnership, and that inclusion implies no whole-application endorsement. See the partnership readiness report.

**Privacy note.** These four links carry `rel="noopener"` but not `noreferrer`; the in-app YouTube link at [index.html:1174](index.html:1174) carries `rel="noopener noreferrer"`. Inconsistent referrer handling — see the privacy audit.

---

## 6. Generated grammar pages (23)

**Generator:** [build_pages.py:720-760](build_pages.py:720). **Source data:** `data-grammar.js`, `data-verbs.js`.

Common shape (Repository finding):

| Property | Pattern |
|---|---|
| URL | `/grammar/<slug>/` |
| Title | `<Name> - Polish grammar explained \| Po polsku` |
| H1 | `<Name>` (e.g. `Mianownik (Nominative)`) |
| Breadcrumb | `Home › Guide › <Name>` — [build_pages.py:728-730](build_pages.py:728) |
| Structured data | `LearningResource` (29 across grammar + vocabulary) |
| Canonical | self |
| OG | type/site_name/url/title/description/image; **no** `og:image:width`/`height` |
| Twitter | `summary_large_image` card; **no** `twitter:image` |
| Ending | `Ready to keep learning?` → `Open the app` → `Genuinely free. No account. Works offline.` — [build_pages.py:622-630](build_pages.py:622) |
| Audio | per-example `.say` buttons with `data-audio` + `data-pl` — [build_pages.py:660-676](build_pages.py:660) |

Full slug list is in `priority-6-public-surface.csv`.

**Search intent fit:** the grammar set maps cleanly onto "Polish grammar explained simply" and per-case queries. **Requires Search Console access** and **Requires external web research** to confirm actual demand and competition.

---

## 7. Generated vocabulary pages (6)

**Generator:** [build_pages.py:775-790](build_pages.py:775). **Source data:** `data-b1.js` (B1 chip hard-coded at [build_pages.py:786](build_pages.py:786)).

| URL | H1 |
|---|---|
| `/vocabulary/polish-idioms/` | Polish idioms explained - with literal translations and audio |
| `/vocabulary/polish-proverbs/` | Polish proverbs explained - with literal translations and audio |
| `/vocabulary/everyday-polish-slang/` | Everyday Polish slang - what Poles actually say |
| `/vocabulary/polish-exclamations/` | Polish exclamations and reactions - ale masakra, tragedia, dramat |
| `/vocabulary/polish-corporate-slang/` | Polish corporate slang - office Polish decoded |
| `/vocabulary/polish-party-slang/` | Polish urban and party slang |

**Search intent fit:** strong for "Polish slang explained". **Gap:** no generated page targets the everyday-life intents named in the Phase 0 brief — booking a doctor's appointment, renting a flat, daily-life phrases — even though `data-a1.js`/`data-a2.js` contain exactly that material (A1 15 topics, A2 22 topics). See the SEO audit.

---

## 8. Redirect stubs (2)

**Source:** [grammar/index.html](grammar/index.html), [vocabulary/index.html](vocabulary/index.html); generator [build_pages.py:925-935](build_pages.py:925).

| Property | Value |
|---|---|
| Title | `Po polsku guide` |
| Mechanism | `<meta http-equiv="refresh" content="0; url=/guide/">` |
| Canonical | `https://popolsku.app/guide/` |
| Robots | `noindex` |
| Body | `Moved to <a href="/guide/">the Po polsku guide</a>.` |

Correctly excluded from the sitemap and correctly canonicalised. Two issues: stale "guide" wording in both the title and the visible link text, and meta-refresh rather than a server 301 (GitHub Pages cannot issue one for a static path — **Supported inference**).

---

## 9. Non-page public assets

| Asset | Purpose | Notes |
|---|---|---|
| [robots.txt](robots.txt) | crawl policy | `Allow: /`, `Disallow: /audio/`, sitemap declared |
| [sitemap.xml](sitemap.xml) | 32 URLs | `lastmod` only; no `changefreq`/`priority` |
| [manifest.json](manifest.json) | PWA identity | name, short_name, description, 3 icons, `start_url: ./?pwa=1` |
| [CNAME](CNAME) | `popolsku.app` | GitHub Pages custom domain |
| `og-image.png` | 1200×630 social preview | referenced as `?v=2` everywhere |
| `favicon.svg?v=17`, `apple-touch-icon.png`, `icon-192/512`, `icon-maskable-512` | identity | consistent across pages |
| `fonts/*.woff2` | 5 self-hosted weights | no external font requests |
| [sw.js](sw.js) | service worker | `popolsku-v59` shell cache, `popolsku-audio` audio cache |

**Manifest/description mismatch (Repository finding).** `manifest.json` says "Free Polish flashcards with **audio**"; the equivalent JSON-LD description in `index.html:50` says "**Polish pronunciation audio**". The manifest is the one place using the shorter, looser word.

---

## 10. Crawlability and canonical summary

| Check | Result |
|---|---|
| Pages with canonical | 34 / 34 |
| Pages with meta description | 32 / 34 (both stubs lack one, correctly) |
| Pages with `lang="en"` | 34 / 34 |
| Heading order valid (h1 then non-skipping) | 32 / 32 generated pages |
| Pages with `og:image:width`/`height` | 1 / 34 (root only) |
| Pages with `twitter:image` | 1 / 34 (root only) |
| `BreadcrumbList` structured data | 0 / 34 — visible breadcrumbs exist but are not marked up |
| Structured-data types | `WebApplication` ×1, `CollectionPage` ×1, `Article` ×1, `LearningResource` ×29 |
| Invalid JSON-LD | 0 |
| Broken internal repository links | 0 |

---

## 11. Offline availability by surface (Repository finding)

The service worker precaches **only** the app shell. Generated pages are network-first and cached opportunistically on first visit.

| Surface | Precached at install | Offline before first visit |
|---|---|---|
| `/` (app shell, 4 helper scripts, 7 data files, audio manifest) | Yes — `REQUIRED_ASSETS`, [sw.js:81-95](sw.js:81) | Yes |
| Manifest, icons, fonts | Yes — `OPTIONAL_ASSETS`, [sw.js:97-110](sw.js:97) | Yes (best-effort) |
| `/guide/`, `/guide/listening/`, all 29 generated pages, both stubs | **No** — `GENERATED_PAGE_ASSETS` is used only for request classification, [sw.js:127](sw.js:127), [sw.js:162](sw.js:162) | **No** — redirects to root, [sw.js:908-911](sw.js:908) |
| MP3 clips | **No** | **No** — cache-first at runtime, [sw.js:923](sw.js:923) |

This materially qualifies the "Works offline" claim. See claims `C-005` and `C-006`.

---

## 12. Required live checks

| Check | Label |
|---|---|
| Rendered home screen content as seen by a rendering crawler | **Requires live-browser verification** |
| Actual HTTP status/headers for `/grammar/` and `/vocabulary/` | **Requires live-browser verification** |
| Social preview rendering on X, LinkedIn, Facebook, WhatsApp, Slack | **Requires live-browser verification** |
| Index coverage of all 32 URLs | **Requires Search Console access** |
| Install, offline, and audio behaviour on real hardware | **Requires physical-device verification** |
| Whether the three recommended creators still exist at those URLs | **Requires external web research** |
