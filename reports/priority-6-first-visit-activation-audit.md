# Priority 6 — First-Visit Activation Audit

**Phase:** 0 (reports-only).

**Conversion definition for Priority 6:** a visitor begins and completes a meaningful learning activity. Not registration, not payment, not account creation, not email capture.

---

## 1. Headline result

**The activation fundamentals are already right, and Priority 6 should protect them rather than redesign them.**

Three structural decisions in the current build are worth naming explicitly, because the most likely way to damage activation is to undo one of them:

1. **The learning controls are the first interactive thing on the page.** Search box, category tabs, and the topic list sit directly beneath a two-line hero — [index.html:1092-1103](index.html:1092).
2. **The app opens on Vocabulary → A1 every single time, statelessly.** "Exactly one level is active (`S.levelIdx`); its category is derived, not stored, so the page is fully stateless - it opens on Vocabulary -> A1 every time." — [index.html:2335-2337](index.html:2335). A first-time visitor and a returning visitor both land on a sensible default; there is no empty state and no configuration step.
3. **There is no gate of any kind.** No modal, no cookie banner, no account wall, no email capture, no onboarding carousel. Verified by search: the only two overlays are the adult-language gate ([index.html:1719](index.html:1719)), which fires only on explicit-content topics, and the navigation drawer.

The gaps found below are about **understanding**, not friction.

---

## 2. Journey map

### Arrival

**What is on screen (Repository finding):** logo, menu button, H1 "Learn the Polish you'll *actually* use.", one sub-line, two badges ("Completely free", "No account needed"), search box, three category tabs (Vocabulary / Grammar / More), level pills (A1 / A2 / B1), a topics header showing the level and topic count, and the A1 topic list — 15 topics.

**Assessment:** strong. The visitor sees the product immediately.

### Understanding

**Gap A-1 — the visitor is not told who this is for. Severity: High.**

Nothing on the first screen says Poland, A1–B1, or everyday life. A visitor who has just moved to Kraków and searched for practical Polish cannot tell that this was built for exactly their situation. See positioning finding 1 and SEO finding S-1.

**Gap A-2 — the visitor is not told what the activities are. Severity: Medium.**

The category tabs read "Vocabulary", "Grammar", "More". "More" ([index.html:2331](index.html:2331)) hides Type it and Listening behind a label that describes nothing. Its sub-label "Choose an activity" only appears after the tab is selected. Conversations and mixed quizzes are not visible from the home screen at all — they are reached from inside a topic.

**Supported inference:** a first-time visitor most likely perceives Po polsku as "a flashcard site" and never discovers the branching conversations (8 scenarios) or mixed quizzes, which are among its strongest differentiators.

### Choosing content

**Assessment:** strong. 15 A1 topics with emoji, name, description, and card count. Search spans all levels ([index.html:1101](index.html:1101)). The topics header names the active level and count ([index.html:2387-2400](index.html:2387)).

**Gap A-3 — no starting-point guidance. Severity: Medium.**

15 topics presented as equals. Nothing marks "First phrases" as the natural beginning. A visitor who does not know their own level has no way to self-place. The `/guide/` page has the same gap (see Explore more Polish audit §5).

### Starting an activity

**Assessment:** strong. One tap from topic to study screen ([index.html:3319](index.html:3319)). No configuration, no difficulty picker, no pre-quiz.

### Completing meaningful learning

**Repository finding.** The app already computes a local proxy for meaningful engagement: an `engagement` counter incremented on card reveals, with `THRESHOLD = 5` before the install banner may appear — [index.html:5280-5285](index.html:5280). Grammar drills, type-it, listening, and mixed rounds all have explicit completion states with scoring (e.g. [index.html:4540-4541](index.html:4540)).

So "completed a meaningful learning activity" is already a **defined, observable moment in the code** — it is simply never counted beyond the install heuristic. This is the single most useful fact for the measurement report.

**Gap A-4 — completion is not connected to a next step. Severity: Medium.**

**Requires live-browser verification** to confirm exactly what the end-of-round screen offers. From source, `rAgain` restarts the same round ([index.html:5168](index.html:5168)) and `rBackBtn` exits. There is no "try a different activity" or "continue to the next topic" suggestion at the moment a learner has just succeeded — which is precisely when a suggestion is most welcome.

### Returning or installing

**Assessment:** well-judged. The install banner appears only after 5 card reveals, respects a 10-day cooldown after dismissal, and derives installed-state from the runtime rather than a stored flag ([index.html:5280-5296](index.html:5280)). This is engagement-gated rather than immediate — the right call.

**Gap A-5 — the offline benefit is asserted, not explained. Severity: Low.**

The banner says "One tap to open, works offline." Given the real limits on offline audio (claim C-005), a learner who installs expecting offline pronunciation may be disappointed. Accuracy here supports retention rather than harming conversion.

---

## 3. Friction inventory

| Potential friction | Present? |
|---|---|
| Account / login wall | **No** |
| Email capture | **No** |
| Cookie / consent banner | **No** (nothing to consent to) |
| Onboarding carousel or tour | **No** |
| Modal on load | **No** |
| Difficulty or goal selection | **No** |
| Paywall or trial | **No** |
| Ads or interstitials | **No** |
| Adult-content gate | Only on explicit topics — [index.html:1719](index.html:1719) |
| Install prompt before engagement | **No** — gated at 5 reveals |

**This is close to a best-case activation surface.** The recommendations below add understanding without adding steps.

---

## 4. Competing actions and hierarchy

On the home screen the visitor can: search, switch category, switch level, open a topic, open the menu, or (after 5 reveals) install.

**Assessment: hierarchy is correct.** The topic list dominates. The menu is a single icon button ([index.html:1069](index.html:1069)). Nothing competes with starting to learn.

**One observation:** About, Privacy, Contact, "What else I listen to", and "Explore more Polish" are *only* reachable through the drawer ([index.html:1741-1752](index.html:1741)) — the footer holds just the version line, and `.foot-guides` styling exists with no markup ([index.html:639-644](index.html:639)).

**Supported inference:** trust pages (About, Privacy) and the SEO destinations are one interaction less discoverable than they would be with a footer links row. This is a defensible trade — it keeps the learning surface clean — but it means a visitor evaluating trustworthiness must first find a hamburger menu. Given that "genuinely free" invites the question "what's the catch?", making About and Privacy reachable without opening a menu is worth considering.

---

## 5. Trust gaps at first visit

| Question a visitor may ask | Answered on first screen? |
|---|---|
| Is this really free? | Yes — badge |
| Do I need an account? | Yes — badge |
| Who made this and why? | **No** |
| Why is it free — what's the catch? | **No** (not answered anywhere) |
| Is the Polish any good? | **No** |
| Will it track me? | **No** (Privacy is two interactions away) |
| Is it for my level? | **No** |

---

## 6. Recommendations

**All Require human copy approval. None implemented in Phase 0.**

Constraint respected throughout: no mandatory multi-step onboarding, no guided learning paths, no marketing-dominated homepage. The learning controls stay central.

### R-1 — Rewrite the hero sub-line to name the audience (highest value, zero added friction)

Addresses A-1 and S-1. Replaces existing text; adds no element. See the positioning audit §5 for proposed wording.

### R-2 — Rename the "More" category tab

Addresses A-2. "More" describes nothing. `Practice` or `Listening & typing` would let a first-time visitor discover Type it and Listening. One-word change at [index.html:2331](index.html:2331).

### R-3 — Add one lightweight starting-point line above the topic list

Addresses A-3. A single sentence, not a flow. Illustrative:

> New to Polish? Start with **First phrases**. Already know some? Try the **search** or jump to A2.

Recommended shown to everyone (not first-visit-only) to avoid introducing per-visitor state, which would carry privacy implications the current build deliberately avoids. **Requires live-browser verification** for mobile layout impact.

### R-4 — Suggest a next step at activity completion

Addresses A-4. When a learner finishes a round, offer one contextual next action alongside "Again" — the next topic, or a different activity on the same topic. This is the highest-leverage retention change available and it costs no first-visit friction. **Requires live-browser verification** to design against the actual completion screens.

### R-5 — Add a minimal footer links row

Addresses the §4 observation and the trust gaps in §5. `About · Privacy · Explore more Polish · Contact`. The CSS already exists unused at [index.html:639-644](index.html:639).

### R-6 — Extend the badge row to the approved proof points

Addresses §5 and positioning finding 4. See positioning audit §5 step 4.

### Explicitly **not** recommended

| Rejected | Reason |
|---|---|
| Mandatory onboarding flow | Forbidden by brief; would damage a working funnel |
| Guided learning paths | Forbidden by brief |
| Level-placement quiz | Adds a step before learning; R-3 solves the same problem for free |
| Marketing sections above the topic list | Forbidden by brief |
| Email capture / newsletter | Outside the Priority 6 conversion definition; creates data-protection obligations the product currently has none of |
| Immediate install prompt | Current engagement gating is better |

---

## 7. Findings summary

| # | Finding | Severity |
|---|---|---|
| A-1 | Audience, level, and Poland context absent from first screen | High |
| A-2 | Activities not discoverable; "More" tab hides Type it and Listening; conversations and mixed quizzes invisible from home | Medium |
| A-3 | No starting-point guidance among 15 equal-weight A1 topics | Medium |
| A-4 | No next-step suggestion at the moment of completion | Medium |
| A-5 | Offline benefit asserted without its real limits | Low |
| A-6 | Trust pages reachable only via the drawer; footer has no links | Low |
| A-7 | "Why is it free?" never answered | Medium |

---

## 8. What cannot be established here

| Question | Label |
|---|---|
| Actual first-visit drop-off | **Requires analytics or traffic access** |
| Whether visitors find the topic list | **Requires live-browser verification** |
| Whether the hero is above the fold on real phones | **Requires physical-device verification** |
| Whether install steps work on real iOS/Android | **Requires physical-device verification** |
| How visitors arrive and what they expect | **Requires Search Console access** |
| Whether real learners understand "More" | **Requires external web research** (user research) |
