# Priority 6 — SEO and Social-Sharing Audit

**Phase:** 0 (reports-only). No metadata, sitemap, or page was modified.

**Scope limit:** this audit is repository-only. No live crawl, no Search Console, no rank data, no competitor research. Nothing below asserts indexing status, ranking, or traffic.

---

## 1. What is already right

Stating this first, because it is a lot and it constrains the recommendations:

| Check | Result |
|---|---|
| Canonical on every page | 34 / 34 |
| `lang="en"` on every page | 34 / 34 |
| Meta description on every indexable page | 32 / 32 |
| Heading order valid on every generated page | 32 / 32 |
| Broken internal repository links | 0 |
| Orphaned indexable pages | 0 |
| Duplicate content | 0 |
| Sitemap ↔ filesystem reconciliation | exact, both directions |
| Redirect stubs correctly `noindex` + canonicalised + sitemap-excluded | 2 / 2 |
| Invalid JSON-LD | 0 |
| Structured data present | `WebApplication`, `CollectionPage`, `Article`, `LearningResource` ×29 |
| Self-hosted fonts (no render-blocking third-party) | yes |
| No third-party scripts / iframes / embeds | verified |
| `robots.txt` valid, sitemap declared | yes |

This is a well-maintained technical baseline. The findings below are gaps and opportunities, not defects in the fundamentals.

---

## 2. Findings

### S-1 — Homepage title and description omit the locked positioning · Medium

| Element | Current |
|---|---|
| `<title>` | `Po polsku - learn the Polish you'll actually use` — [index.html:7](index.html:7) |
| Description | `Polish flashcards with Polish pronunciation audio - everyday vocabulary, useful grammar, conversation practice, and phrases from real podcasts.` — [index.html:8](index.html:8) |

Neither contains "Poland", "A1", "B1", or any everyday-life intent. The JSON-LD description ([index.html:50](index.html:50)) and `manifest.json` **do** carry "for A1-B1" — so the strongest-signal fields are the weakest ones.

**Recommendation (Requires human copy approval):** carry the locked positioning into the title and description, without keyword stuffing. Illustrative:

> `Po polsku - practical Polish for real life in Poland`
> `Free Polish flashcards with pronunciation audio for A1-B1 adults living in Poland: everyday vocabulary, grammar drills, conversations, and phrases from real podcasts. No account, works offline.`

### S-2 — No generated pages target everyday-life search intent · **High**

**Repository finding.** All 29 content pages are generated from `data-grammar.js`, `data-verbs.js` (23 grammar pages) and `data-b1.js` (6 vocabulary pages — slang, idioms, proverbs, exclamations, corporate, party).

Meanwhile `data-a1.js` (15 topics, 340 cards) and `data-a2.js` (22 topics, 514 cards) — the material that most directly matches the Phase 0 example intents — generate **no public pages at all**.

Mapping the brief's example intents against current coverage:

| Example search intent | Covered? | Nearest existing source |
|---|---|---|
| Polish phrases for booking a doctor's appointment | **No** | `a2-health-body`, `a2-pharmacy` topics |
| Useful Polish phrases for daily life | **No** | `a1-first-phrases`, `a2-daily-life` |
| Polish vocabulary for renting a flat | **No** | `a2-home-family` and related |
| Polish slang explained | **Yes** | 4 of the 6 vocabulary pages |
| Polish grammar explained simply | **Yes** | 23 grammar pages |

**This is the single largest discoverability opportunity in the repository.** The content already exists, is already validated, and already has pronunciation audio; only a generator extension is missing. It is also the intent set most aligned with the locked audience — someone who has just moved to Poland searches for "how to say I have an appointment in Polish", not "Polish locative case".

**Recommendation:** in Phase 3, extend `build_pages.py` to emit a small number (5–8, not 37) of high-intent A1/A2 topic pages. Selecting few and choosing them for intent, rather than generating one page per topic, avoids thin-content risk. **Requires external web research** to prioritise, and **Requires Search Console access** to measure.

### S-3 — Three names for the `/guide/` destination · High

Covered fully in the Explore more Polish audit (G-1, G-2). SEO consequence: the `<title>`, H1, JSON-LD `name`, and 31 breadcrumbs disagree, which weakens entity consistency for that destination.

### S-4 — No `BreadcrumbList` structured data · Medium

31 generated pages render visible, correctly-marked-up breadcrumb `<nav>` elements ([build_pages.py:728](build_pages.py:728), [:781](build_pages.py:781), [:809](build_pages.py:809), [:863](build_pages.py:863)) with no corresponding structured data. Adding `BreadcrumbList` is a single generator change covering all 31 pages and is well-supported for search result presentation.

### S-5 — `og:image:width` / `og:image:height` on 1 of 34 pages · Medium

Only [index.html:23-24](index.html:23) declares dimensions. All 31 generated pages reference the same 1200×630 `og-image.png` without them ([build_pages.py:562](build_pages.py:562)). Some scrapers defer or downgrade a card while they fetch the image to determine size. One-line generator fix.

### S-6 — `twitter:image` absent on 33 of 34 pages · Low

Generated pages declare `twitter:card = summary_large_image` ([build_pages.py:563](build_pages.py:563)) but no `twitter:image`. Most consumers fall back to `og:image`, so this is likely cosmetic. **Requires live-browser verification** with a card validator.

### S-7 — One shared social image for 34 pages · Medium

Every page shares `og-image.png?v=2`. A shared brand image is a reasonable choice for a one-founder project, but it means a shared grammar page and a shared slang page look identical in a feed. Per-page images are almost certainly not worth the maintenance cost; **per-section** images (app / grammar / vocabulary / listening) would be four assets and would meaningfully improve link previews. **Assumption requiring validation** — depends on whether sharing actually happens, which **Requires analytics or traffic access** to know.

### S-8 — Homepage content is JavaScript-rendered · Medium

The served HTML contains the hero, badges, search input, and empty containers; all 97 topics render from `data-*.js` at runtime ([index.html:5536](index.html:5536)). The `<noscript>` block ([index.html:1047-1055](index.html:1047)) points to `/guide/`, which is good practice.

**Consequence:** the homepage's indexable text is roughly two sentences plus two badges. The generated pages carry the site's real crawlable substance — which makes S-2 more important, not less.

**No recommendation to server-render.** That would be a disproportionate architectural change for a static, offline-first app. The correct mitigation is S-1 (stronger static hero text) plus S-2 (more high-intent generated pages). **Requires live-browser verification** to confirm what a rendering crawler actually sees.

### S-9 — Every generator run resets all 32 sitemap `lastmod` dates · Medium

**Repository finding, observed directly this session.** `build_pages.py` takes no arguments, has no dry-run or check mode, and ignores anything passed to it — it regenerates unconditionally on invocation. Running it rewrites all 31 generated pages and sets **every** `<lastmod>` in `sitemap.xml` to the current date, including for pages whose bytes did not change.

Verified side-effect: after one accidental invocation, all 31 pages regenerated **byte-identically** while `sitemap.xml` showed 32 changed `lastmod` values (`2026-08-04` → `2026-08-05`). The change was reverted with `git checkout -- sitemap.xml`; the working tree is clean and the tree hash matches the expected baseline.

Two consequences:

1. **SEO:** `lastmod` stops being a truthful signal. A crawler told that all 32 URLs changed on every deploy learns to discount the field.
2. **Operational:** there is no safe way to check generator drift without dirtying the working tree. A `--check` mode would make generator verification a routine, safe step.

**Recommendation (Phase 3):** derive `lastmod` per URL from actual content change (e.g. only update when the rendered bytes differ), and add a `--check` mode that renders to memory and reports drift without writing. Both are maintenance-plan items too.

**Useful corollary:** because output is byte-identical, the committed generated pages are provably in sync with the generator at this HEAD.

### S-10 — `manifest.json` description drops "pronunciation" · Low

See claim C-008. `manifest.json:5` says "flashcards with audio"; every other surface says "Polish pronunciation audio".

### S-11 — Redirect stubs use meta-refresh · Low

`/grammar/` and `/vocabulary/` use `<meta http-equiv="refresh" content="0; …">` plus canonical plus `noindex` — [grammar/index.html:6-7](grammar/index.html:6). A 301 is preferable but unavailable on GitHub Pages for a static path (**Supported inference**). Current construction is the correct approximation. **No change recommended**, beyond the wording fix in the Explore more Polish audit.

### S-12 — `sitemap.xml` has no `changefreq` or `priority` · Informational

Both are widely ignored by major search engines. **No change recommended.**

### S-13 — `Disallow: /audio/` · Informational

[robots.txt:3](robots.txt:3). Sensible: 3,377 MP3s have no search value and would waste crawl budget. Note it does not prevent audio from being *fetched* by users — only crawled. **No change recommended.**

---

## 3. Search-intent assessment of existing generated pages

**Repository finding** for what the pages contain; **Requires external web research** for demand, and **Requires Search Console access** for performance. Nothing below asserts ranking.

| Page group | Intent served | Fit |
|---|---|---|
| 7 grammar case pages | "Polish cases explained", "dopełniacz explained" | Strong — real, sustained learner intent |
| 16 other grammar pages | "pan/pani formal Polish", "Polish diminutives", "żeby Polish" | Strong and specific |
| `everyday-polish-slang`, `polish-party-slang`, `polish-corporate-slang` | "Polish slang explained" | Strong — directly matches a brief example |
| `polish-idioms`, `polish-proverbs` | "Polish idioms with meaning" | Strong |
| `polish-exclamations` | "what does masakra mean" | Moderate — long-tail |
| `/guide/listening/` | "best Polish podcasts for learners" | Strong — and genuinely differentiated content |
| `/guide/` | navigational hub | Weak standalone; strong as an internal-link hub |

**Content quality signals (Repository finding):** every generated page carries structured explanations, tables, usage notes, worked examples with pronunciation audio, and a `LearningResource` JSON-LD block. Vocabulary pages carry 10–27 expressions each with literal translations. This is substantive content, not thin doorway material — which is what makes S-2 a low-risk expansion.

**Explicitly not recommended:** keyword-stuffed headings, doorway pages for near-identical queries, or one generated page per A1/A2 topic (37 more pages of similar shape would risk exactly the thin-content problem the current set avoids).

---

## 4. Performance signals observable from repository structure

**Repository finding** only — no field data, no Lighthouse run.

| Signal | Observation |
|---|---|
| `index.html` size | 337 KB single file, inline CSS + JS |
| Data payload | 7 `data-*.js` files, ~640 KB total, all loaded before app init ([index.html:1755-1762](index.html:1755)) |
| Generated pages | self-contained, inline CSS, ~1 small inline script |
| Fonts | 5 self-hosted woff2 with `font-display: swap` |
| Render-blocking third parties | none |
| Images | one 57 KB PNG (social only), icons; UI is inline SVG |
| Service worker | precaches shell for repeat visits |

**Supported inference:** generated pages should be fast (self-contained, no third parties). The app shell's first load is heavier — roughly 1 MB of HTML + data before the first topic renders — which matters most for the mobile-first, possibly-metered audience this product targets. **Requires live-browser verification** and **Requires physical-device verification** to quantify; no Core Web Vitals claim is made here.

---

## 5. Social-sharing summary

| Element | Root | Generated pages |
|---|---|---|
| `og:type` | `website` | `article` |
| `og:site_name` | ✅ | ✅ |
| `og:locale` | ✅ | ❌ |
| `og:url` | ✅ | ✅ |
| `og:title` / `og:description` | ✅ | ✅ |
| `og:image` | ✅ | ✅ (same asset) |
| `og:image:width` / `height` / `type` / `alt` | ✅ | ❌ |
| `twitter:card` | ✅ | ✅ |
| `twitter:title` / `description` / `image` / `image:alt` | ✅ | ❌ (card falls back to OG) |

**Requires live-browser verification** for actual rendering on X, LinkedIn, Facebook, WhatsApp, Slack, and Signal.

---

## 6. Prioritised recommendations

| Priority | Finding | Action | Phase |
|---|---|---|---|
| 1 | S-2 | Generate 5–8 high-intent A1/A2 everyday-life pages | 3 |
| 2 | S-1 | Carry locked positioning into homepage title + description | 1 / 3 |
| 3 | S-3 | Resolve the `/guide/` naming across title, H1, JSON-LD, breadcrumbs | 3 |
| 4 | S-4 | Add `BreadcrumbList` structured data | 3 |
| 5 | S-9 | Content-derived `lastmod` + generator `--check` mode | 3 |
| 6 | S-5 | Add `og:image:width`/`height` to generated pages | 3 |
| 7 | S-7 | Consider 4 per-section social images | 3 (optional) |
| 8 | S-10 | Align `manifest.json` description | 3 |
| 9 | S-6 | Add explicit `twitter:image` | 3 (optional) |

---

## 7. What this audit cannot establish

| Question | Label |
|---|---|
| Are all 32 URLs indexed? | **Requires Search Console access** |
| What queries produce impressions? | **Requires Search Console access** |
| Do generated pages receive organic traffic? | **Requires analytics or traffic access** |
| How competitive are the target intents? | **Requires external web research** |
| Do social cards render correctly? | **Requires live-browser verification** |
| What does a rendering crawler see on `/`? | **Requires live-browser verification** |
| Real-device performance | **Requires physical-device verification** |
| Do the three recommended creator URLs still resolve? | **Requires external web research** |
