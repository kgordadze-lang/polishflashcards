# Priority 6 — Measurement-Readiness Audit

**Phase:** 0 (reports-only). **No analytics were installed. No tracking code, cookie, or identifier was added.** Nothing in this report is approved for implementation; measurement is Phase 5 at the earliest and requires separate approval.

Machine-readable twin: `priority-6-measurement-events.csv`.

---

## 1. Measurement that exists today

**Repository finding — verified by exhaustive search.**

| Measurement type | Present |
|---|---|
| Analytics SDK (GA, Plausible, Fathom, Umami, …) | **None** |
| Cookies (`document.cookie`) | **None** |
| Tracking pixels / beacons | **None** |
| Third-party scripts | **None** |
| Error / crash reporting | **None** |
| Session recording | **None** |
| A/B testing framework | **None** |
| Persistent user identifier of any kind | **None** |
| Server-side logging under founder control | **None** (static hosting) |

**The application contains no analytics or telemetry, and no learner data is transmitted by application code.** This is not the same as saying nothing about a user reaches anyone: serving any web page delivers ordinary network metadata (IP address, user agent, requested path, timestamp) to whoever hosts it, and clicking an external link sends ordinary request data to that destination. Those flows are inherent to the web rather than product decisions, but they are real and are covered in §1 of the privacy audit.

### Data already collected — all local, not transmitted by application code

| Data | Storage | Transmitted? |
|---|---|---|
| Per-topic known / still-learning card ids | `popolsku-progress-v2` | No |
| Audio speed preference | `popolsku-speed` | No |
| Voice-hint shown flag | `popolsku-voicehint` | No |
| Install-prompt engagement counter + dismissal time | `popolsku-a2hs` — [index.html:5279-5285](index.html:5279) | No |
| Card direction | `pp-card-dir` | No |
| Service-worker write/audio failure diagnostics (≤20 each) | worker memory only — [sw.js:552-557](sw.js:552) | No |

### Third parties currently receiving information

| Party | What it necessarily sees | Under founder control? |
|---|---|---|
| GitHub Pages | server logs: IP, user agent, path, timestamp | **No** — not exposed to the founder |
| Cloudflare (**unverified**, claim C-017) | same, if in path | Possibly, if an account exists — **Requires validation** |
| YouTube / Patreon / realpolish.pl | referrer + request data, **only** when a user clicks out | No |

**Important:** GitHub Pages does not expose per-site traffic analytics to the repository owner. **Supported inference:** the founder currently has *no* visibility into traffic at all.

---

## 2. What is observable without any new code

| Signal | Source | Available now |
|---|---|---|
| Google Search impressions, clicks, queries, indexed pages | Google Search Console | **Requires Search Console access** — not configured |
| Whether a URL is indexed by Google | Search Console | **Requires Search Console access** |
| Backlink/link discovery reported by Google | Search Console | **Requires Search Console access** |
| Clicks on a post, ad, or sponsored placement | the platform's or sponsor's own reporting, destination-side | Partially, per platform, and only if that platform reports it |
| **Arrivals on this site from a newsletter, directory, creator, or social post** | — | **Not observable.** Static hosting, no accessible request logs, no analytics |
| Total visits, sessions, returning users | — | **Not observable** without new code |
| Activity starts / completions | — | **Not observable** without new code |
| Install events | — | **Not observable** without new code |

**Highest-value, lowest-cost next step by a wide margin: configure Google Search Console.** Stated precisely, and no more broadly than the evidence supports:

- configuring it **requires no instrumentation code in Po polsku**;
- it **adds no application cookie and no application-assigned identifier**;
- it **does not change what Po polsku application code sends**;
- it **reports Google Search performance** and does not measure non-Google referrals or on-site activity;
- **account-level, provider, disclosure, and legal implications remain a separate human review question** — this report does not conclude that configuring it carries no privacy impact, requires no consent, or needs no Privacy-page change. Those are determinations about a third-party service account and its terms, not about this repository.

> **What Search Console is not.** Search Console reports **Google Search performance** — impressions, clicks from Google results, queries, indexing status, and link discovery. It is **not a referral analytics system**. It cannot count visits arriving from a newsletter, a directory listing, a creator mention, a Reddit thread, or a social post, and it cannot observe anything a visitor does after arriving — including whether they completed a learning activity. Any plan that depends on attributing arrivals or completions to a non-Google channel needs an approved measurement mechanism that does not currently exist.

**A distinct landing URL does not solve this.** Giving a newsletter or directory its own landing path makes arrivals *distinguishable in principle*, but with static hosting, no accessible server logs, and no analytics, **there is nothing that counts requests to that path.** A distinct path is a prerequisite for future attribution, not a measurement method in itself.

**Note:** Phase 0 explicitly forbids configuring or accessing Search Console. This is a recommendation for a later phase and a separate human decision.

---

## 3. Constraints any measurement must satisfy

Derived from current public commitments and code:

| # | Constraint | Source |
|---|---|---|
| M-1 | Cannot use cookies without making the Privacy page false | [index.html:1589](index.html:1589) |
| M-2 | Cannot build a learner profile | [index.html:1578](index.html:1578) |
| M-3 | Cannot use "analytics tools" without rewriting the Privacy page in the same release | [index.html:1589](index.html:1589) |
| M-4 | Any third-party endpoint requires widening `connect-src 'self'` | [index.html:38](index.html:38) |
| M-5 | Must not break offline operation | [sw.js](sw.js) |
| M-6 | Must not require an account | claim C-004 |

**M-4 is the useful gate.** The CSP is a structural guarantee, not a policy statement. Any proposal that requires editing it should face a high bar and be visible in review.

---

## 4. Primary success metric

**Meaningful learning sessions completed.**

**Repository finding — this is already a defined moment in the code**, which is what makes it measurable at all:

- An `engagement` counter already increments on card reveals with `THRESHOLD = 5` — [index.html:5280-5285](index.html:5280).
- Grammar, type-it, listening, and mixed rounds have explicit completion states with scores — e.g. [index.html:4540-4541](index.html:4540).

A defensible definition: *a learner completed a round of any activity, or revealed at least N cards in one topic.* The app can already determine this locally without any new tracking concept.

---

## 5. Candidate event evaluation

### What the verdicts mean

> **"Approve" here means one thing only: *worth considering from a product-decision perspective*.**
>
> It does **not** mean the event is privacy-approved, legally cleared, consent-assessed, or approved for implementation. Those are separate determinations, none of which this report can make. Every event — including every "Approve" — carries **Requires legal review** for its consent and lawful-basis status.

Each event is assessed across seven separate dimensions, deliberately kept apart because conflating them is how measurement decisions go wrong:

| Dimension | Question |
|---|---|
| **Product-decision value** | Would the answer change what gets built? |
| **Payload** | What fields would the event body carry? |
| **Technical identifier or linkage** | Does it need an identifier, or enable linking events together? |
| **Network metadata** | What does the request itself reveal, regardless of payload? |
| **Cookie or storage requirement** | Does it need a cookie or persistent client storage? |
| **Privacy implications** | What does it mean for the stated privacy posture? |
| **Legal status** | Consent and lawful basis. |

**Network metadata applies to every event below and is never zero.** Any request to a collection endpoint delivers an IP address, a user agent, timing, and whatever the path reveals. No event in this report can be described as sending "no personal data"; the accurate formulation is that a payload carries no identifier and no learner content, while the request still carries ordinary network metadata whose legal characterisation is unresolved.

**Assumed measurement shape for all "Approve" verdicts:** a self-hosted, cookieless, aggregate-only counter that assigns no application identifier and performs no intentional event joining. **No such mechanism exists today and none is approved.**

> **What can and cannot be promised about linkability.** The application can control what *it* does: it can decline to assign or transmit a persistent application identifier, decline to set a cookie, and decline to join events to one another. It **cannot** promise that requests are unlinkable, because a collection endpoint and its hosting infrastructure receive ordinary network metadata — IP address, user agent, timing, and path — and **server or provider logs may permit correlation between requests**, including requests from the same visitor across visits.
>
> Use this vocabulary throughout, and avoid the stronger forms:
>
> | Say this | Not this |
> |---|---|
> | no application-assigned persistent identifier | "identifier-free" |
> | no intentional event-level or cross-visit joining | "cannot be linked across visits" |
> | no learner-content payload | "no personal data" |
> | no cookie and no new client-side identifier | "no tracking of any kind" |
> | ordinary server and network logs may still contain IP address, user agent, timing, and path | (omitted entirely) |
>
> Log retention, access control, aggregation, deletion, and the real possibility of correlation are **technical design questions and Requires legal review** — they are not settled by choosing a payload shape.

---

### E-1 · Topic opened — **Defer**

- **Product-decision value:** moderate — which topics attract attention; whether A1 dominates.
- **Payload:** topic id, timestamp.
- **Identifier or linkage:** none required.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** none required.
- **Privacy implications:** low in isolation; a 97-value dimension is more granular than the decision needs.
- **Legal status:** **Requires legal review.**
- **Why defer:** genuinely useful for content prioritisation, but 97 topics produce a wide, low-signal distribution at current (unknown) traffic. Defer until E-2/E-3 establish that volume is sufficient for topic-level data to mean anything.

### E-2 · Activity started — **Approve** *(product-decision perspective only)*

- **Product-decision value:** high — directly tests activation finding A-2 (are Type it, Listening, conversations, and mixed quizzes ever discovered?). Near-zero conversation starts would be a strong, actionable navigation signal.
- **Payload:** activity type (one of six), timestamp.
- **Identifier or linkage:** none required.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** none required.
- **Privacy implications:** low — a six-value enumeration with no learner content.
- **Legal status:** **Requires legal review.**

### E-3 · Activity completed — **Approve** *(product-decision perspective only)*

- **Product-decision value:** highest — **this is the primary success metric.** Paired with E-2 it yields a start→completion ratio per activity, the single most useful number in Priority 6.
- **Payload:** activity type, completion flag, timestamp. **No score, no card ids, no answers.**
- **Identifier or linkage:** none required for an aggregate count. Note that a *ratio* per activity is computable from two aggregate counters and does not require linking a start to its completion.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** none required.
- **Privacy implications:** low.
- **Legal status:** **Requires legal review.**

### E-4 · Pronunciation audio played — **Defer**

- **Product-decision value:** low as a raw count; **moderate-to-high** as a fallback-rate signal, which would reveal manifest or caching problems in the field.
- **Payload:** a play event; optionally whether the MP3 or the speech fallback was used.
- **Identifier or linkage:** none required.
- **Network metadata:** standard, but at high frequency.
- **Cookie or storage:** none required.
- **Privacy implications:** volume is the concern, not payload sensitivity.
- **Legal status:** **Requires legal review.**
- **Why defer:** revisit as a **fallback-rate-only** counter after E-2/E-3 are established.

### E-5 · Question completed — **Reject**

- **Product-decision value:** **low** — E-3 already answers the actionable question ("did they finish?"). Per-question counts would not change what gets built.
- **Payload:** a per-question event — the highest-frequency signal in the app.
- **Identifier or linkage:** none required.
- **Network metadata:** standard, at the highest volume of any candidate.
- **Cookie or storage:** none required.
- **Privacy implications:** **note the corrected reasoning.** An earlier draft claimed that per-question data "is where a behavioural profile starts to form". That is not correct as stated: **high-frequency aggregate events do not by themselves create a behavioural profile without an identifier or some linkage mechanism.** Unlinked aggregate counters remain unlinked however often they fire.
- **Why reject nonetheless:** **low decision value, event volume, proportionality, and unnecessary granularity.** Collecting the app's highest-frequency signal to answer a question already answered by a far cheaper event fails a proportionality test on its own terms — no profiling argument is needed, and none is claimed.
- **Legal status:** **Requires legal review.**

### E-6 · Conversation opened — **Approve** *(product-decision perspective only)*

- **Product-decision value:** high — conversations are among the strongest differentiators and are invisible from the home screen (activation A-2).
- **Payload:** a flag that the conversation activity was entered.
- **Identifier or linkage:** none required.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** none required.
- **Privacy implications:** low.
- **Legal status:** **Requires legal review.**
- **Implementation note:** this is a subset of E-2's activity-type dimension. **Recommended: fold into E-2 rather than ship separately.**

### E-7 · Explore more Polish opened — **Approve** *(product-decision perspective only)*

- **Product-decision value:** moderate — whether the renamed destination is used, and whether the rename helped.
- **Payload:** in-app navigation to `/guide/`.
- **Identifier or linkage:** none required.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** none required.
- **Privacy implications:** low.
- **Legal status:** **Requires legal review.**
- **Caveat:** for *inbound search* traffic to `/guide/`, Search Console answers this with no code at all. This event is only needed for *in-app* navigation.

### E-8 · Installation action — **Approve** *(product-decision perspective only)*

- **Product-decision value:** moderate — whether the 5-reveal threshold and 10-day cooldown are well tuned.
- **Payload:** install prompt shown / accepted / dismissed.
- **Identifier or linkage:** none required.
- **Network metadata:** standard request metadata; low volume.
- **Cookie or storage:** none *new* — the app already keeps this state locally in `popolsku-a2hs`.
- **Privacy implications:** low.
- **Legal status:** **Requires legal review.**

### E-9 · Return visit — **Reject**

- **Product-decision value:** low-to-moderate — retention is interesting, but no currently planned decision depends on it.
- **Payload:** a flag that this browser has been seen before.
- **Identifier or linkage:** **note the corrected reasoning.** An earlier draft asserted that this event "requires a persistent identifier by definition". That is not correct. **Local state already present on the device can trigger an aggregate return event without transmitting any application identifier**: the existence of `popolsku-progress-v2` is sufficient for the client to decide it is a return visit and to send a single counter carrying no application-assigned identifier and involving no intentional joining to any earlier event.
- **What must not be claimed about it.** It would be wrong to go further and say the request "would not be linkable to the previous visit". The request still delivers IP address, user agent, timing, and path to the endpoint and its hosting provider, and **server or provider logs may permit correlation with earlier requests from the same visitor.** The accurate statement is *no application-assigned identifier and no intentional joining* — not *unlinkable*.
- **Network metadata:** standard request metadata.
- **Cookie or storage:** no *new* storage — it would read state the app already keeps.
- **Privacy implications:** the *mechanism* can avoid an application-assigned identifier, but the *concept* is retention measurement, which sits closest to the "without building a learner profile" commitment (claim C-019). It is also the event most likely to attract future pressure toward deliberate linkage — a cohort breakdown, a first-seen date, a frequency bucket — each of which would convert "no intentional joining" into intentional joining.
- **Why reject nonetheless:** **limited decision value, tension with the intended privacy posture, and the risk of future linkage creep.** Not because it is technically impossible to do without an identifier.
- **Legal status:** **Requires legal review.**
- **Local alternative (not measurement):** the same local state could inform in-app behaviour — for example the starting-point line in activation recommendation R-3 — with nothing transmitted at all. That is a product feature, not analytics, and carries none of the above concerns.

---

## 6. Verdict summary

All verdicts below are **product-decision verdicts only**. None carries privacy, legal, consent, or implementation approval.

| Event | Product verdict | Priority | Identifier required | New cookie/storage | Network metadata | Legal status |
|---|---|---|---|---|---|---|
| E-3 Activity completed | **Approve** | 1 | No | No | Yes (inherent) | Requires legal review |
| E-2 Activity started | **Approve** | 2 | No | No | Yes (inherent) | Requires legal review |
| E-8 Installation action | **Approve** | 3 | No | No | Yes (inherent) | Requires legal review |
| E-6 Conversation opened | **Approve** (fold into E-2) | 4 | No | No | Yes (inherent) | Requires legal review |
| E-7 Explore more Polish opened | **Approve** | 5 | No | No | Yes (inherent) | Requires legal review |
| E-1 Topic opened | **Defer** | — | No | No | Yes (inherent) | Requires legal review |
| E-4 Audio played | **Defer** (revisit as fallback-rate) | — | No | No | Yes (inherent) | Requires legal review |
| E-5 Question completed | **Reject** — low decision value, volume, proportionality, granularity | — | No | No | Yes (inherent) | Requires legal review |
| E-9 Return visit | **Reject** — limited value, privacy posture, future linkage risk | — | **No** (local state suffices) | No | Yes (inherent) | Requires legal review |

**The "Consent risk" column present in an earlier draft has been removed.** Estimating consent risk is a legal determination this report is not able to make, and phrasing such as "Consent: unlikely" gave false assurance. Every row now carries **Requires legal review** instead.

**Net recommendation: four distinct events** (E-2 with an activity-type dimension covering E-6, E-3, E-8, E-7) — enough to compute the primary success metric and to test the main activation hypothesis, and no more. This remains a product-decision recommendation only.

---

## 7. Data-policy and Privacy-page implications

Any implementation, even the minimal set above, requires:

1. **Rewriting** "Po polsku does not use advertising, marketing cookies, or analytics tools" ([index.html:1589](index.html:1589)) in the **same release**. Shipping measurement before the wording change would make a live public claim false.
2. A new Privacy section stating what is counted and that it is aggregate, described in the precise vocabulary of §5: **no application-assigned persistent identifier, no intentional event-level or cross-visit joining, no learner-content payload, no cookie or new client identifier**, and an explicit acknowledgement that **ordinary server and network logs may still contain IP address, user agent, timing, and path**. It must **not** claim that the endpoint receives no personal data, nor that events cannot be linked across visits. Log retention, access, aggregation, deletion, and possible correlation are **Requires legal review**.
3. A decision on `connect-src` (M-4). A self-hosted, same-origin endpoint would avoid widening the CSP — but the site is statically hosted, so a same-origin collection endpoint **does not exist today** and would be a new piece of infrastructure with its own maintenance and privacy surface. **This is the main practical obstacle** and should be resolved before any event work.
4. **Requires legal review** for whether the chosen mechanism triggers consent obligations for users in Poland/the EU.

---

## 8. Recommended sequence

| Step | Action | Cost | Requires |
|---|---|---|---|
| 1 | Configure Search Console | No instrumentation code in Po polsku; no application cookie or application-assigned identifier; no change to what application code sends | Separate human decision; account-level, provider, disclosure, and legal implications are a **separate human review** |
| 2 | Operate on Search Console data alone for one full cycle | — | Patience |
| 3 | Decide whether product questions remain unanswered | — | Judgement |
| 4 | Only if yes: choose a cookieless same-origin mechanism that assigns no application identifier and performs no intentional joining, and design its log retention, access, and deletion policy explicitly | Infrastructure | Separate approval + legal review |
| 5 | Ship E-2/E-3/E-8/E-7 **with** the Privacy rewrite in one release | — | Human copy approval |

**The honest recommendation is that steps 1–3 may be sufficient.** For a free, no-account product whose main open questions are discoverability and activity discovery, Search Console plus the qualitative signal from an invited correction route (feedback audit R-1/R-2) may answer enough to make step 4 unnecessary. Building a collection endpoint is the single largest new maintenance burden proposed anywhere in this audit, and it trades away a genuinely differentiating privacy position.

---

## 9. What cannot be established here

| Question | Label |
|---|---|
| Current traffic volume | **Requires analytics or traffic access** |
| Whether traffic is sufficient for event data to be meaningful | **Requires analytics or traffic access** |
| Whether GitHub Pages / Cloudflare logs are reachable | **Requires validation** |
| Consent obligations under Polish/EU law | **Requires legal review** |
| Which self-hosted analytics options are viable on static hosting | **Requires external web research** |
