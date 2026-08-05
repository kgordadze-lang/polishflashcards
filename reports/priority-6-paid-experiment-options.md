# Priority 6 — Low-Budget Paid-Experiment Options

**Phase:** 0 (reports-only).

> **No campaign was launched. No platform account was created or accessed. No campaign was configured. No money was spent. No advertising platform was contacted.**

**Every budget figure, reach estimate, cost-per-click, and duration in this report is a PROVISIONAL PLANNING ASSUMPTION.** No live market research, rate-card check, auction data, or competitor research was permitted in this phase. Every figure **Requires external web research** and current validation before any spend decision. Nothing here is a forecast, a quote, or a recommendation to spend.

---

## 1. Precondition: do not spend yet

Three blocking gaps make **any** paid experiment premature today:

| # | Gap | Consequence |
|---|---|---|
| 1 | **No measurement of any kind** (measurement §1) | Spend would produce no learning. There is no way to tell whether a click became a learner |
| 2 | **Homepage does not state the positioning** (positioning finding 1) | Paid traffic lands on a page that does not confirm what the ad promised |
| 3 | **No correction/feedback route** (feedback F-1) | Paid traffic that finds an error has no route to report it |

**Recommendation: complete Phases 1–4 and configure Search Console before considering any spend.** Paid acquisition into an unmeasured funnel converts money into noise.

A further structural point: the product is **free with no account and no revenue**. There is no payback mechanism, so every złoty spent is a permanent cost, not an investment with a return. The only rational objectives are *learning* (which channels reach the audience) and *reach* (getting the tool to people who need it) — never ROI.

### 1a. What is and is not attributable today

This constraint applies to **every** option below and is stricter than the earlier draft acknowledged.

| Signal | Attributable today? |
|---|---|
| Clicks reported by the platform or sponsor (ad manager, newsletter click count, creator's own stats) | **Yes, if that party reports it** — destination-side, outside this repository |
| Directory listing accepted / live | **Yes** — observable by inspection |
| Backlink discovered by Google | **Yes, once Search Console is configured** |
| Google Search impressions and clicks | **Yes, once Search Console is configured** |
| **Arrivals on this site from a newsletter, directory, creator, or social placement** | **No** |
| **Meaningful-learning completions from any paid or referral source** | **No** |

**Why.** The site is statically hosted, the founder has no access to server request logs, and there is no analytics. Nothing counts requests to any path.

**A distinct landing URL is not a measurement method.** Giving a placement its own landing path makes arrivals *distinguishable in principle*, but with nothing counting requests to that path, no number is produced. A distinct path is a prerequisite for future attribution, not attribution itself. The earlier draft of this report treated "distinct landing path" as a sufficient measurement method for Options 4, 5, and 6; that was wrong and is corrected throughout.

**Search Console does not fill this gap.** It reports Google Search performance — impressions, clicks from Google results, queries, indexing, and link discovery. It is **not a referral analytics system** and cannot count newsletter, directory, creator, or social arrivals, nor anything a visitor does after arriving.

**Consequence:** any experiment whose success metric is a *completion* — which is every option whose objective is "test whether this channel produces learners" — **remains blocked until an approved measurement mechanism exists** (measurement §7–8, Phase 5, not currently approved). Experiments whose success criterion is *placement* or *reported clicks* can proceed without it, and those are precisely Options 4 and 5.

---

## 2. Options evaluated

### Option 1 — Limited boost of a strong founder post

| Field | Assessment |
|---|---|
| **Platform** | Facebook/Instagram or LinkedIn boost of an existing organic post |
| **Audience** | Foreigners living in Poland; international students |
| **Objective** | One only: test whether the founder story travels beyond organic reach |
| **Provisional budget** | **PROVISIONAL ASSUMPTION:** €20–50 total |
| **Duration** | **PROVISIONAL:** 5–7 days |
| **Required asset** | A post that already performed organically — **do not boost an untested post** |
| **Success metric** | *Intended:* sessions reaching a completed activity. **Not attributable today** — requires E-3 and an approved mechanism. *Available today:* platform-reported clicks and engagement only |
| **Minimum meaningful result** | **Cannot be defined** for completions today. Run on reported clicks alone, the result is a reach signal, not an activation signal |
| **Stop condition** | Halt at 50% of budget if click-through is indistinguishable from organic |
| **Measurement** | Platform-reported clicks and engagement only. No pixel, no remarketing tag. **Arrivals and completions on the site are not observable** |
| **Data implications** | **Significant.** Platform pixels are exactly what the privacy position forbids. Must run **without** any pixel on the site — accepting weaker attribution as the price of keeping claim C-015 true |
| **Reputational risk** | Low–medium. A boosted post in a community group can read as intrusive |
| **Maintenance** | Comment moderation during the run |
| **External validation** | **Required** — current costs, targeting availability, policy |

**Assessment: the most defensible first experiment**, because it tests a message that already worked and requires no new creative.

---

### Option 2 — Highly specific search-intent advertising

| Field | Assessment |
|---|---|
| **Platform** | Google Ads, exact-match only |
| **Audience** | People searching specific practical Polish phrases |
| **Objective** | Test whether high-intent search traffic completes a learning activity |
| **Provisional budget** | **PROVISIONAL:** €50–100 total, hard daily cap |
| **Duration** | **PROVISIONAL:** 2–3 weeks |
| **Required asset** | Landing pages matching each intent — **these do not exist yet** (SEO S-2) |
| **Success metric** | *Intended:* completed activities per click. **Not attributable today** |
| **Minimum meaningful result** | **Cannot be defined** without completion measurement |
| **Stop condition** | Stop if cost per completed activity exceeds a pre-set ceiling, or at budget |
| **Measurement** | Ad-platform click reporting only. Search Console reports Google **organic** search, not ad referrals or on-site behaviour. **No conversion pixel**, therefore no completion data |
| **Data implications** | **High tension.** Google Ads conversion tracking uses cookies. Running without it means near-blind optimisation. Running with it **breaks claim C-015 and requires a Privacy rewrite and a CSP change** |
| **Reputational risk** | Low |
| **Maintenance** | Active management |
| **External validation** | **Required** — keyword costs, volumes, competition all unknown |

**Assessment: strategically interesting but currently blocked twice** — the landing pages do not exist, and the measurement it needs conflicts with the privacy position. **Notable alternative:** the same intents can be pursued organically via SEO S-2 at zero cash cost. **Recommend organic first.**

---

### Option 3 — Small campaign aimed at foreigners living in Poland

| Field | Assessment |
|---|---|
| **Platform** | Meta, geo-targeted to Poland, language/interest targeting for non-Polish speakers |
| **Audience** | The locked primary audience |
| **Objective** | Test whether the locked positioning resonates when stated plainly |
| **Provisional budget** | **PROVISIONAL:** €50–75 |
| **Duration** | **PROVISIONAL:** 7–10 days |
| **Required asset** | Creative built on the locked positioning; homepage that matches it (**not ready**) |
| **Success metric** | *Intended:* completed activities. **Not attributable today** |
| **Minimum meaningful result** | **Cannot be defined** for completions today |
| **Stop condition** | 50% budget with no engagement lift |
| **Measurement** | Platform-reported clicks and engagement only; no pixel. **Arrivals and completions are not observable** |
| **Data implications** | Same pixel tension as Option 1 |
| **Reputational risk** | Low–medium |
| **Maintenance** | Comment moderation |
| **External validation** | **Required** |

**Assessment: the best audience match**, and it doubles as a positioning test. Blocked on Phase 1.

---

### Option 4 — Newsletter or community sponsorship

| Field | Assessment |
|---|---|
| **Platform** | A newsletter serving expats in Poland or language learners |
| **Audience** | Pre-qualified, high fit |
| **Objective** | Test whether a trusted third-party mention drives meaningful use |
| **Provisional budget** | **PROVISIONAL:** €50–200 per placement — **highly variable and entirely unverified** |
| **Duration** | Single placement |
| **Required asset** | Short copy block + the social image |
| **Success metric** | *Available today:* sponsor-reported click count, plus the placement running as agreed. *Not available:* arrivals or completions on this site |
| **Minimum meaningful result** | Placement delivered as agreed and sponsor-reported clicks recorded. Completion-based thresholds **cannot be defined** today |
| **Stop condition** | Single placement; evaluate before repeating |
| **Measurement** | Sponsor-reported clicks. A distinct landing path should still be used — **not because it measures anything today**, but so attribution becomes possible if a mechanism is ever approved. **No tracking parameters carrying user data** |
| **Data implications** | **Lowest of all options.** No pixel, no cookie, no CSP change, nothing added to the site |
| **Reputational risk** | Low — but **disclosure is mandatory** if the placement is paid |
| **Maintenance** | None after placement |
| **External validation** | **Required** — identify newsletters and real rates |

**Assessment: the most privacy-compatible paid option**, and the only one that needs no compromise on measurement principles. **Recommended as the first paid experiment if any spend occurs.**

---

### Option 5 — Low-cost directory placement

| Field | Assessment |
|---|---|
| **Platform** | Reputable PWA / education / language-learning directories |
| **Audience** | Discovery-oriented browsers |
| **Objective** | Durable backlinks + passive discovery |
| **Provisional budget** | **PROVISIONAL:** €0–50; many reputable directories are free |
| **Duration** | Permanent |
| **Required asset** | Description, icon (**exists**), screenshots (**do not exist**) |
| **Success metric** | Listing accepted and live; backlink discovered in Search Console. **Referral traffic is not observable** |
| **Minimum meaningful result** | Listing accepted and the backlink discovered |
| **Stop condition** | n/a — one-off |
| **Measurement** | Search Console for **link discovery and Google organic search only** — not for referral traffic from the directory |
| **Data implications** | None |
| **Reputational risk** | Low, **provided** low-quality link-farm directories are avoided |
| **Maintenance** | Near-zero |
| **External validation** | **Required** — identify reputable directories |

**Assessment: best effort-to-value ratio.** Mostly free, permanent, no privacy implications. Should be pursued regardless of whether any paid experiment happens.

---

### Option 6 — Tightly defined creator collaboration

| Field | Assessment |
|---|---|
| **Platform** | A Polish-learning YouTube or podcast creator |
| **Audience** | Engaged learners |
| **Objective** | Test whether creator endorsement drives meaningful use |
| **Provisional budget** | **PROVISIONAL:** €100–300 — **entirely unverified**; many creators decline paid placement for free tools |
| **Duration** | Single mention |
| **Required asset** | Clear brief; agreed wording |
| **Success metric** | *Available today:* creator-reported reach and clicks, if shared. *Not available:* arrivals or completions on this site |
| **Minimum meaningful result** | **Cannot be defined** for completions today |
| **Stop condition** | Single collaboration |
| **Measurement** | Creator-reported figures only. A distinct landing path enables future attribution but **counts nothing today** |
| **Data implications** | Low |
| **Reputational risk** | **Highest of all six options.** A paid mention creates a commercial relationship that must be disclosed, and it risks blurring into the endorsement and partnership claims the Phase 0 brief forbids |
| **Maintenance** | Relationship management; ongoing disclosure upkeep |
| **External validation** | **Required** |

**Assessment: not recommended in the near term** — primarily because it is the highest-risk option and cannot be measured, not because of a conflict with the existing recommendations page.

### Correcting an error in the earlier draft

The earlier draft claimed that paying a creator would contradict the `/guide/listening/` disclosure and concluded that any paid experiment **must never** involve the three currently recommended creators. Both parts were wrong.

**The disclosure is about payment flowing *to* Po polsku, not *from* it.** The published sentence is:

> These are personal recommendations. None of the creators paid to be included here.
> — [build_pages.py:914](build_pages.py:914)

That statement concerns creators paying for inclusion. **A future payment from Po polsku to a creator for a sponsored mention would not make it false.** The categorical prohibition is therefore withdrawn.

**What a payment from Po polsku to a creator would genuinely require:**

| # | Requirement |
|---|---|
| 1 | **Explicit sponsored disclosure** on the paid placement itself, in the creator's channel, in the form that channel and its jurisdiction require |
| 2 | **Clear separation between editorial recommendation and paid promotion** — the `/guide/listening/` entry and any sponsored mention must be visibly distinct pieces of communication, not blended |
| 3 | **Agreed wording in advance**, covering both what the creator says and what Po polsku publishes about the relationship |
| 4 | **A review of whether the personal recommendation remains editorially independent.** If a creator is being paid, the honest question is whether their `/guide/listening/` entry can still be presented as an unpaid personal recommendation. If it cannot, the entry should be updated to disclose the commercial relationship, or removed — this is a judgement, not an automatic disqualification |
| 5 | Confirmation that the existing disclosure sentence remains accurate, and extension of it if the relationship changes what a reader needs to know |

**Practical consequence.** Involving a currently recommended creator is permissible but raises the disclosure and independence burden, because two different relationships would then exist with the same person. Involving a creator *not* currently recommended keeps editorial and commercial cleanly separate and is the simpler path — a preference, not a prohibition.

---

## 3. Summary

| Option | Provisional budget | Privacy compatibility | Reputational risk | Success measurable today? | Blocked today? | Rank |
|---|---|---|---|---|---|---|
| 5 · Directory placement | €0–50 | **Full** | Low | **Yes** — placement + backlink discovery | No | **1** |
| 4 · Newsletter sponsorship | €50–200 | **Full** | Low | **Partly** — sponsor-reported clicks only | Partly | **2** |
| 1 · Boost proven founder post | €20–50 | Good (no pixel) | Low–med | **Partly** — platform-reported clicks only | Partly | 3 |
| 3 · Foreigners-in-Poland campaign | €50–75 | Good (no pixel) | Low–med | **No** for its stated objective | **Yes** (Phase 1 + measurement) | 4 |
| 2 · Search-intent ads | €50–100 | **Poor** if conversion tracking used | Low | **No** | **Yes** (no pages + measurement) | 5 |
| 6 · Creator collaboration | €100–300 | Good | **High** | **No** | **Yes** (measurement + disclosure design) | 6 |

**All budget figures are provisional planning assumptions requiring current external validation.**

**Read the "Success measurable today?" column as the decisive one.** Options 3, 2, and 6 all state objectives framed around producing learners, and none of that is attributable without an approved measurement mechanism. They are blocked on measurement, not only on the gaps noted in §1. Options 5 and 4 are ranked first precisely because their success criteria — a listing going live, a backlink appearing, a sponsor's own click count — are observable without instrumenting the site at all.

---

## 4. Overall recommendation

**Do not spend money in the near term.**

The strongest argument is not caution but sequencing: the product's two largest growth opportunities — high-intent generated pages (SEO S-2) and a homepage that states its positioning (S-1) — are both **free**, both **compound**, and both **must happen anyway**. Paid spend before them buys traffic for a page not ready to receive it.

If spend does occur later, the recommended order is: **directories (mostly free) → one newsletter placement → one boosted post that already performed organically.** Stop after each and evaluate.

**Evaluate against what is actually observable.** For each of those three, the evaluable question is "did the placement run and what did the platform or sponsor report?", **not** "how many learners did it produce" — the second cannot be answered today by any of these options. Any experiment whose objective is stated in terms of completions should wait for an approved measurement mechanism rather than proceed on an unmeasurable success criterion.

**Hard constraint carried into any future phase:** no advertising pixel, no conversion cookie, and no CSP widening for an ad platform without an explicit, separate decision that accepts rewriting the Privacy page and forfeiting claim C-015. The privacy position is a genuine differentiator; trading it for attribution on a €50 test would be a poor exchange.

---

## 5. What this report cannot establish

| Question | Label |
|---|---|
| Actual advertising costs on any platform | **Requires external web research** |
| Keyword volumes, competition, CPCs | **Requires external web research** |
| Newsletter sponsorship rates | **Requires external web research** |
| Creator collaboration rates | **Requires external web research** |
| Which directories are reputable and current | **Requires external web research** |
| Baseline traffic to define a meaningful result | **Requires analytics or traffic access** |
| Whether any option would convert | **Requires analytics or traffic access** — and note that this cannot be answered by Search Console, by a distinct landing path, or by any combination of the two |
| Arrivals on this site from any non-Google channel | **Requires analytics or traffic access** |
| Disclosure requirements binding on a specific creator's channel and jurisdiction | **Requires external web research** + **Requires legal review** |
| Ad-platform policy on this product category | **Requires external web research** |
| Disclosure obligations for paid placements in Poland/EU | **Requires legal review** |
