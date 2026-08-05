# Priority 6 — Contact and Feedback Audit

**Phase:** 0 (reports-only). All wording proposals **Require human copy approval**.

---

## 1. Current state

**Repository finding.** The entire contact and feedback surface is one screen and one link.

| Property | Value | Evidence |
|---|---|---|
| Location | `/#contact`, reachable only from the navigation drawer | [index.html:1634-1653](index.html:1634), [index.html:1751](index.html:1751) |
| H1 | `Contact` | [index.html:1640](index.html:1640) |
| Lead (h2) | `Have an idea, want to collaborate, or simply want to connect?` | [index.html:1647](index.html:1647) |
| Body | `Po polsku is an independent and evolving project. I'm always open to thoughtful collaborations, useful resources, new ideas, and conversations about making Polish easier and more engaging to learn.` | [index.html:1648](index.html:1648) |
| Mechanism | `mailto:hello@popolsku.app` | [index.html:1649](index.html:1649) |
| Accessible name | `Email hello@popolsku.app` | [index.html:1649](index.html:1649) |
| Subject prefill | none | — |
| Body template | none | — |
| Guidance on what to include | none | — |
| Alternative channels | none | — |

There is **no** form, no ticketing, no forum, no account system, and no community platform. **This is the right architecture** for a one-founder project and the recommendations below do not change it.

---

## 2. Findings

### F-1 — No correction route for content errors · **High**

**Repository finding.** Nothing anywhere on any public surface invites or explains how to report a mistake in a card, drill, translation, or audio clip.

Why this matters more than a generic contact gap:

- The product's core value is content accuracy, and the About page claims continuous review ([index.html:1627](index.html:1627)).
- There are 1,215 cards, 353 drills, and 3,377 audio clips. **Supported inference:** at that volume, errors exist.
- Learners are the cheapest, fastest error detectors available to a solo founder, and the repository already has the machinery to act on reports — `validate_content.py` recognises review-ticket and review-reference metadata ([validate_content.py:33-36](validate_content.py:33)).
- Inviting corrections is *itself* a trust signal, and a documented correction log substantiates the quality claim far better than a sentence of undocumented scope (claim C-011).

This is the highest-value change in this report: it costs one paragraph and converts users into a quality mechanism.

### F-2 — The contact page addresses collaborators, not learners · Medium

Both the lead and the body speak to people with ideas, resources, or collaboration proposals. A learner who spotted a wrong translation, or whose audio will not play, finds nothing addressed to them. The word "collaborate" is the most prominent invitation on the page.

**Supported inference:** the current framing selects for partnership enquiries over the correction and bug reports that are more useful and more numerous.

### F-3 — No guidance on what to include · Medium

A learner reporting "the audio doesn't work" without page, card, device, or browser detail cannot be helped, and the founder must spend a round-trip asking. A `mailto:` link can carry a subject and a short body template at zero infrastructure cost.

### F-4 — Contact is two interactions deep · Medium

Reachable only by opening the drawer and selecting Contact ([index.html:1751](index.html:1751)). The footer contains only the version line ([index.html:1705](index.html:1705)); unused `.foot-guides` CSS sits at [index.html:639-644](index.html:639). Generated pages have no contact link at all ([build_pages.py:640-643](build_pages.py:640)) — so a visitor who lands on a grammar page from search and spots an error has no route to report it without first finding the app.

### F-5 — Bare `mailto:` exposes the address to harvesters · Low

`hello@popolsku.app` appears in plain text in both the `href` and the link text ([index.html:1649](index.html:1649)). It is a role address rather than a personal one, which limits the harm. Obfuscation is not recommended — it degrades accessibility and is easily defeated. **Assumption requiring validation:** current spam volume is unknown to this audit.

### F-6 — No privacy note on the contact route · Low

The Privacy page says nothing about what happens to an email a user sends. Given how strongly the product promises no data collection, a one-line statement that emails are ordinary email — received, read, and not added to any list — closes the loop. Cross-referenced as privacy finding P-9.

### F-7 — Version string is present and useful · Positive

The footer renders `v8.4` from `APP_VERSION` ([index.html:1705](index.html:1705), [index.html:1776](index.html:1776)), and generated pages carry the same version ([build_pages.py:640-643](build_pages.py:640)). Asking reporters to include it costs nothing and is already possible.

---

## 3. Recommendation — the minimum effective solution

**All Require human copy approval. None implemented in Phase 0.**

The design goal is to raise report *quality* without raising report *volume* beyond what one founder can handle, and without building any system.

### R-1 — Restructure the Contact page around four named reasons

Replace the single collaboration-oriented lead with four short blocks, each with a purpose-built `mailto:` carrying a prefilled subject:

| Reason | Subject prefill | What to include |
|---|---|---|
| Report a mistake in the content | `Correction` | the topic name, the Polish phrase, and what is wrong |
| Something is not working | `Technical issue` | what you were doing, your device and browser, and the version from the footer |
| Suggest a topic or phrase | `Suggestion` | what you were trying to say and where |
| Something else | `Hello` | — |

`mailto:` supports `?subject=` and `?body=` with no infrastructure. This directly addresses F-1, F-2, and F-3.

**Note:** the request for device and browser detail is a request for *technical context*, not personal data, and should be worded to make that obvious. Screenshots should be described as optional and never as required.

### R-2 — Add a short correction invitation where errors are seen

One line at the end of generated pages and reachable from the app, e.g.:

> Spotted a mistake? [Tell me](mailto:hello@popolsku.app?subject=Correction) — corrections are welcome and get fixed.

Placing it on generated pages (a single change in [build_pages.py](build_pages.py) covering 31 pages) addresses F-4 for search visitors.

### R-3 — Add a minimal footer links row

`About · Privacy · Explore more Polish · Contact`. Addresses F-4 and activation finding A-6. CSS already exists at [index.html:639-644](index.html:639).

### R-4 — Add one line to the Privacy page about contact

> If you email me, I read your message and reply. Your email address is not added to any list and is not used for anything else.

Addresses F-6 and P-9.

### R-5 — Keep the collaboration invitation, but demote it

The existing collaboration paragraph is worth keeping — partnership readiness depends on being reachable — but as the fourth block, not the headline. Any partnership wording must stay inside the boundaries of the partnership readiness report: no named partners, no endorsement implications.

### Explicitly **not** recommended

| Rejected | Reason |
|---|---|
| Contact form | Requires a form backend — a third party receiving user data, contradicting the privacy position and `connect-src 'self'` |
| Ticketing system | Disproportionate; ongoing cost |
| Forum or community | Moderation load incompatible with one founder |
| In-app feedback widget | Third-party script; contradicts CSP and the no-third-party promise |
| Accounts for reporting | Contradicts "no account required" |
| Public issue tracker for learners | Raises expectations of public triage |
| Chat / Discord | Ongoing presence obligation |

---

## 4. Founder maintenance burden

| Aspect | Assessment |
|---|---|
| Current burden | Minimal — one inbox, no system |
| Burden after R-1…R-5 | Slightly higher volume, **substantially** higher per-report usefulness |
| Risk of overwhelm | Low. **Assumption requiring validation** — depends on traffic, which **Requires analytics or traffic access** |
| Mitigation | Subject prefills allow inbox filters and batched handling; see the maintenance plan |
| Escalation | If volume becomes unmanageable, narrow the invitation (e.g. corrections only) before building any system |

---

## 5. Findings summary

| # | Finding | Severity |
|---|---|---|
| F-1 | No correction route for content errors | **High** |
| F-2 | Contact page addresses collaborators, not learners | Medium |
| F-3 | No guidance on what to include | Medium |
| F-4 | Contact two interactions deep; absent from generated pages | Medium |
| F-6 | No privacy note on the contact route | Low |
| F-5 | Plain-text address exposed to harvesters | Low |

---

## 6. What cannot be established here

| Question | Label |
|---|---|
| Current email volume and spam load | **Requires analytics or traffic access** (or founder knowledge) |
| Whether `mailto:` works acceptably on real mobile devices | **Requires physical-device verification** |
| Whether learners would use a correction route | **Requires external web research** (user research) |
| Whether prefilled subjects survive common mail clients | **Requires live-browser verification** |
