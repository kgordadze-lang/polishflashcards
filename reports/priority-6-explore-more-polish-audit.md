# Priority 6 — "Explore more Polish" Audit

**Phase:** 0 (reports-only). All wording proposals **Require human copy approval**.

The former public-facing "Guide" destination is now named **Explore more Polish**. This report audits every public-facing reference and assesses whether the destination does its job.

---

## 1. Headline result

**The rename is one line deep.** Only the navigation-drawer label was changed. Every other public-facing surface — page title, H1, breadcrumbs on 31 pages, structured data, redirect stubs, and the `<noscript>` fallback — still says "Guide".

The repository is explicit that this was deliberate and scoped:

> Approved refinement: the /guide/ destination keeps its URL and page metadata; only the menu label and its position in this list changed.
> — [index.html:1747-1748](index.html:1747)

So this is **known scope, not an accident**. Priority 6 §7 nonetheless requires the public-facing wording to be consistent, so the remaining work is inventoried here.

**Separately, there is a naming problem the rename did not create:** the destination has *three* different names even ignoring "Guide" — the menu says "Explore more Polish", the title says "Polish guide…", and the H1 says "Polish, explained simply".

---

## 2. Complete public-facing naming inventory

| # | Surface | Current public wording | File | Generator |
|---|---|---|---|---|
| 1 | Drawer link label | **Explore more Polish** ✅ | [index.html:1749](index.html:1749) | — |
| 2 | `/guide/` `<title>` | `Polish guide - grammar, slang and idioms explained simply \| Po polsku` | [guide/index.html:7](guide/index.html:7) | [build_pages.py:796](build_pages.py:796) |
| 3 | `/guide/` `og:title` | same as above | [guide/index.html:14](guide/index.html:14) | [build_pages.py:796](build_pages.py:796) |
| 4 | `/guide/` H1 | `Polish, explained simply` | [guide/index.html:126](guide/index.html:126) | [build_pages.py](build_pages.py) |
| 5 | `/guide/` JSON-LD `name` | `Polish guide` | [guide/index.html:20](guide/index.html:20) | [build_pages.py:802](build_pages.py:802) |
| 6 | `/guide/` breadcrumb | `Home › Guide` | [guide/index.html:126](guide/index.html:126) | [build_pages.py:809](build_pages.py:809) |
| 7 | 23 grammar page breadcrumbs | `Home › Guide › <Name>` | each `grammar/<slug>/index.html:126` | [build_pages.py:728-730](build_pages.py:728) |
| 8 | 6 vocabulary page breadcrumbs | `Home › Guide › <Name>` | each `vocabulary/<slug>/index.html:126` | [build_pages.py:781-783](build_pages.py:781) |
| 9 | `/guide/listening/` breadcrumb | `Home › **Guide** › What I listen to` | [guide/listening/index.html:126](guide/listening/index.html:126) | [build_pages.py:863-864](build_pages.py:863) |
| 10 | `/grammar/` stub title + body | `Po polsku guide` / `Moved to the Po polsku guide.` | [grammar/index.html:5](grammar/index.html:5) | [build_pages.py:928](build_pages.py:928), [:933](build_pages.py:933) |
| 11 | `/vocabulary/` stub title + body | same | [vocabulary/index.html:5](vocabulary/index.html:5) | [build_pages.py:928](build_pages.py:928), [:933](build_pages.py:933) |
| 12 | `<noscript>` fallback | `grammar & vocabulary guide` | [index.html:1052](index.html:1052) | — |

**Count: 1 surface updated, 11 surfaces (covering 33 pages) still saying "Guide".**

### A second inconsistency inside the listening page

| Surface | Wording |
|---|---|
| Drawer label | What else I listen to |
| Page H1 | What else I listen to |
| JSON-LD headline | What else I listen to |
| **Breadcrumb** | **What I listen to** — [build_pages.py:864](build_pages.py:864) |
| **`<title>`** | **Polish podcasts worth listening to \| Po polsku** — [build_pages.py:849](build_pages.py:849) |

The breadcrumb drops "else". The title is a deliberate SEO variant, which is legitimate — search intent for "Polish podcasts" is real — but it should be a conscious decision rather than drift.

---

## 3. URL, canonical, sitemap, redirect, and duplication behaviour

| Check | Result | Evidence |
|---|---|---|
| URL | `/guide/` retained | intentional per [index.html:1747](index.html:1747) |
| Canonical | self-referential and correct on all 3 guide-family pages | [guide/index.html:9](guide/index.html:9), [guide/listening/index.html:9](guide/listening/index.html:9) |
| Sitemap | `/guide/` and `/guide/listening/` both present | [sitemap.xml](sitemap.xml) |
| Redirect stubs | `/grammar/` and `/vocabulary/` → `/guide/` | meta-refresh + canonical + `noindex` |
| Stub indexing | correctly `noindex`, correctly excluded from sitemap | [grammar/index.html:7](grammar/index.html:7) |
| Duplicate content | **none** — no page duplicates `/guide/` | link-graph analysis |
| Orphaned generated pages | **none** — all 29 linked from `/guide/` | link-graph analysis |
| Crawlability | `robots.txt` allows all except `/audio/` | [robots.txt](robots.txt) |
| Offline availability | **not precached** — redirects to root when offline and cold | [sw.js:908-911](sw.js:908) |

**Assessment: the technical SEO of this destination is sound.** Keeping the `/guide/` URL is the right call — changing it would forfeit whatever authority the URL has accrued for no user benefit, since users navigate by label, not by path. **Requires Search Console access** to confirm accrued authority.

### Redirect-stub mechanism

Meta-refresh with `content="0"` plus a canonical and `noindex`. A server-issued 301 would be preferable, but GitHub Pages cannot issue one for a static path (**Supported inference**). The current construction is the correct static-hosting approximation. **No change recommended** beyond the wording in row 10/11 above.

---

## 4. Accessible names

**Repository finding.** The drawer link ([index.html:1749](index.html:1749)) is a plain `<a>` whose accessible name is its text content, "Explore more Polish" — correct, with no conflicting `aria-label`. Same for "What else I listen to" ([index.html:1746](index.html:1746)).

Breadcrumb navs are correctly labelled `aria-label="Breadcrumb"` on all 31 generated pages. The accessible name of the breadcrumb *link* is "Guide" — so a screen-reader user hears "Guide" where a sighted user who arrived via the menu expects "Explore more Polish".

**Requires live-browser verification** for the rendered accessibility tree; **Requires physical-device verification** for VoiceOver and TalkBack.

---

## 5. Does the destination do its job?

Phase 0 §7 lists seven jobs. Assessed against actual page content ([guide/index.html:126](guide/index.html:126)):

| Job | Status | Evidence |
|---|---|---|
| Understand how the application works | **Weak** | The lede names the app's features in one clause; there is no explanation of *how it works* |
| Understand the learning activities | **Weak** | "flashcards, drills, conversations, and listening" appears only in the closing card, [build_pages.py:625-626](build_pages.py:625) |
| Use pronunciation audio | **Absent** | Audio buttons exist on sub-pages; nothing explains them |
| Understand offline behaviour | **Absent** | "Works offline" asserted in the ending line, never explained |
| Understand levels and navigation | **Partial** | The page groups grammar into four thematic sections, which implicitly teaches structure; A1/A2/B1 levels are never explained |
| Decide where to begin | **Absent** | No starting-point guidance anywhere |
| Discover additional learning options | **Strong** | 29 topic links + the listening page, well organised |

**Assessment.** The page is currently a well-built *link hub* — it does the discovery job well and the explanation job barely at all. It is not an oversized manual, which is good; it is closer to the opposite problem.

Two lines already do real work and should be preserved verbatim:

> Built by a foreigner living in Poland and learning the language through everyday life…

> These pages are a sample - a taste of each topic. The full library, with every card, drill, and conversation, lives in the free app.

The second is an unusually honest expectation-setter and directly supports activation.

---

## 6. Recommendations

**All Require human copy approval. None implemented in Phase 0.**

### R-1 — Decide the destination's public name (blocking decision)

Three names exist for one page. Recommended resolution:

| Surface | Recommended |
|---|---|
| Menu label | `Explore more Polish` (locked, no change) |
| H1 | `Explore more Polish` |
| `<title>` | `Explore more Polish - Polish grammar, slang and idioms explained simply \| Po polsku` |
| JSON-LD `name` | `Explore more Polish` |
| Breadcrumbs (31 pages) | `Home › Explore more Polish › <Name>` |

Rationale for keeping the descriptive tail in the `<title>`: "Explore more Polish" alone carries no search intent, while "Polish grammar, slang and idioms explained simply" does. The title is the one place where a descriptive variant earns its keep. **This is the single decision that unblocks Phase 1/3 work on this destination.**

### R-2 — Fix the two stray strings

- `<noscript>`: "grammar & vocabulary guide" → "Explore more Polish" — [index.html:1052](index.html:1052)
- Redirect stubs: `Po polsku guide` → `Explore more Polish` in title and link text — [build_pages.py:928](build_pages.py:928), [:933](build_pages.py:933)

### R-3 — Align the listening breadcrumb

`What I listen to` → `What else I listen to` — [build_pages.py:864](build_pages.py:864). Keep the SEO `<title>` as-is, deliberately.

### R-4 — Add a compact "How Po polsku works" block

Four or five short items on `/guide/`, immediately below the lede — enough to close the four Absent/Weak rows in §5 without becoming a manual. Suggested shape:

- **Levels** — A1, A2, B1 vocabulary, plus grammar, verbs, conversations, and podcast phrases.
- **Activities** — flashcards, grammar drills, type-it, listening, mixed quizzes, and branching conversations.
- **Pronunciation audio** — tap the speaker on any Polish phrase.
- **Offline** — after your first visit the app works without a connection; clips are saved as you play them.
- **Where to begin** — new to Polish? Start with A1 → First phrases. Already speaking a little? Try a mixed quiz.

This directly serves activation (see the first-visit audit) and adds indexable, intent-matching text to a page that is currently mostly link anchors.

### R-5 — Add `BreadcrumbList` structured data

Visible breadcrumbs exist on 31 pages with no corresponding markup. Cheap, generator-level, one implementation. See the SEO audit.

---

## 7. Implementation notes for later phases

- Items 2–11 in §2 are **all generator-owned** — they are single-line edits in [build_pages.py](build_pages.py) that regenerate 33 pages. Item 12 and item 1 are hand-edited in `index.html`.
- **Any** `build_pages.py` run rewrites all 31 generated pages and resets every `<lastmod>` in `sitemap.xml` to the run date. See the SEO audit finding S-9.
- Generated pages are network-first, so wording changes reach users on their next online visit without a service-worker cache bump ([sw.js:908-911](sw.js:908)). Changing `index.html` (items 1 and 12) **does** require a shell-cache bump.
- **Verified this session:** regenerating produces byte-identical output for all 31 pages, so the committed pages are exactly in sync with the generator. Any diff after a Phase 3 edit is attributable solely to that edit.

---

## 8. Findings summary

| # | Finding | Severity |
|---|---|---|
| G-1 | Destination has three different public names | High |
| G-2 | "Guide" persists on 33 pages across 11 surfaces | High |
| G-3 | Page does not explain how the app works, the activities, audio, offline, or where to begin | Medium |
| G-4 | `<noscript>` says "grammar & vocabulary guide" | Medium |
| G-5 | Redirect stubs say "Po polsku guide" | Medium |
| G-6 | Listening breadcrumb says "What I listen to" | Low |
| G-7 | No `BreadcrumbList` markup despite visible breadcrumbs | Low |
| G-8 | Screen-reader users hear "Guide" in breadcrumbs | Low |
