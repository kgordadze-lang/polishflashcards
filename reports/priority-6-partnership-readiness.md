# Priority 6 — Partnership Readiness

**Phase:** 0 (reports-only).

> **No teacher, reviewer, creator, or organisation is an approved public partner for Priority 6 purposes.** Nothing in this report designates, implies, or prepares the announcement of any partner. No partner logo, collaboration badge, review badge, named-review claim, or endorsement wording is recommended for publication. This report is generic readiness assessment only.

---

## 1. Current state

| Item | Status | Evidence |
|---|---|---|
| Partner logos published | **None** | verified across all public files |
| Collaboration badges | **None** | verified |
| "In collaboration with" wording | **None** | verified |
| Named professional-review claims | **None** | verified |
| Whole-app endorsements | **None** | verified |
| Review badges | **None** | verified |
| Partnership enquiry route | Contact page invites collaboration | [index.html:1647-1648](index.html:1647) |
| Third parties named publicly | 3 creators, as personal recommendations | [guide/listening/index.html:126](guide/listening/index.html:126) |

**Assessment: the public surface is currently clean of partnership claims.** That is the correct starting position and the main thing to protect.

### Two existing exposures

**Exposure 1 — the About page names the founder's teacher in a quality context.**

> …with help from native Polish speakers around me, including my teacher.
> — [index.html:1627](index.html:1627)

This is claim C-011, classified **Needs qualification** at **Medium** risk.

To be precise about what the issue is and is not:

- The sentence **names no particular person** — "my teacher" is a relationship, not an identity.
- It **asserts no partnership, no professional review, and no endorsement**, and it is not treated as any of those here.
- The repository **cannot establish whether permission to mention this was requested or granted**, and the absence of such evidence in a code repository is **not** evidence that permission was absent. No inference about consent is drawn.
- The repository **does not show the sentence to be false.**

The genuine issue is that **the scope and coverage of the help are undocumented**, and the wording is **open to a broader reading than intended** — a visitor may take it to mean a Polish teacher systematically checks the app. Process-based wording is clearer, does not depend on any individual relationship, and stays accurate as the content grows. **Adopting the approved process wording in Phase 1 is recommended** on those grounds.

**Exposure 2 — three creators are named on a public page.**

`/guide/listening/` names Real Polish, Polish with Kamil, and Ratio viva, with the disclosure:

> These are personal recommendations. None of the creators paid to be included here.
> — [build_pages.py:914](build_pages.py:914)

This is honest and well-placed. It is also **incomplete** against the four points Phase 0 requires:

| Required disclosure point | Present |
|---|---|
| Recommendations are personal | **Yes** |
| Creators did not pay to be included | **Yes** — but see the evidence limit below |
| Inclusion does not imply a formal partnership | **No** |
| Inclusion does not imply whole-app endorsement | **No** |

**What the repository can and cannot establish.** The four outbound links carry no affiliate parameters, no tracking parameters, and no sponsorship markup. That is **not** proof that no commercial or review relationship exists — money, agreements, and reviews leave no trace in static markup. The repository cannot establish whether any creator paid to be included, whether any creator is a partner, whether any creator has reviewed any part of the app, whether any creator has endorsed it, or whether any creator is aware of their inclusion. The already-published payment sentence therefore rests on **founder knowledge, not on code**.

**Recommended internal wording** (**Requires human copy approval** and **Requires founder confirmation**):

> These are personal recommendations. None of the creators paid to be included. Inclusion here does not indicate a formal partnership with Po polsku or an endorsement of the app.

This is **implication-based**: the third sentence states what inclusion *means*, which is within the founder's authority to state, rather than asserting facts about other people's relationships or activities.

**Do not use** "none of them is a partner", "none of them has reviewed", or any other categorical statement about a third party's relationship or activity unless each is separately confirmed. Such wording claims knowledge about other people that neither the repository nor, necessarily, the founder possesses — and it is a stronger claim than the disclosure needs.

**Founder confirmations required before publication:** (1) that no creator paid to be included; (2) each creator's actual relationship status; (3) whether each creator is aware of their inclusion — question (3) is independent of the wording and does not block it.

**Phase:** this string lives in [build_pages.py:914](build_pages.py:914), so it is scheduled in **Phase 3** with all other generator-dependent work (risk R-12), not in Phase 1.

**Note:** "What else I listen to" remains the destination name, and it should continue to be treated as a personal recommendation page, not a partnership page. Nothing about its framing should shift toward partnership.

---

## 2. Partnership types that could provide real value

Generic assessment. No specific person or organisation is proposed.

| Type | Potential value | Main risk | Complexity |
|---|---|---|---|
| **Limited content review** — a qualified Polish speaker reviews a defined subset | High — substantiates quality with a bounded, truthful claim | Scope creep into whole-app endorsement | Medium |
| **Reciprocal promotion with a creator** | Moderate–high reach | Blurring into paid endorsement; disclosure obligations | Low |
| **Institutional listing** (university, student office, relocation organisation) | Durable referral + backlink | May trigger accessibility/data assurances that cannot be given | Medium |
| **Community partnership** (expat group, learner community) | Sustained access to the locked audience | Ongoing presence obligation | Low |
| **Teacher/school adoption as a supplementary resource** | High leverage | Strongest pull toward endorsement language | Medium |
| **Content contribution** (a creator contributes a topic) | Fresh content + built-in promotion | Attribution, licensing, and maintenance obligations | High |

---

## 3. What Po polsku can offer

**Repository finding** — genuine, verifiable assets:

- A free product with no account requirement, usable immediately with no barrier.
- A verifiable privacy position: no analytics or telemetry in application code, no application cookie, no third-party scripts, CSP-enforced same-origin for app-initiated requests (claim C-015). State it in those terms — a bare "no cookies" would be a claim about the live hosting path that the repository cannot support, and **Requires live-browser verification**.
- 32 indexable pages with substantive content and a demonstrated willingness to recommend others generously and without payment.
- A demonstrated quality process: deterministic content validation, a frozen forward baseline, 149 Python tests, 32 JavaScript suites, complete audio verification.
- Reciprocal linking with genuine editorial context, as already demonstrated on `/guide/listening/`.

## 4. What Po polsku should request

| Request | Rationale |
|---|---|
| Explicit written permission before any public naming | Required whenever a specific person or organisation is identified publicly — a separate matter from C-011, which names no one |
| A precisely defined review scope (which topics, which release, what "reviewed" means) | Makes a truthful bounded claim possible |
| Agreed wording, approved in advance by both parties | Prevents drift into endorsement |
| Permission terms for name and logo, with duration | Prevents stale claims |
| A stated withdrawal process | Enables clean removal |

---

## 5. Limited content review — boundaries

The only partnership type that could support a public quality claim, and only if bounded precisely.

**A truthful bounded claim would look like:**

> The A1 vocabulary topics were reviewed by a qualified Polish teacher in August 2026.

**It must NOT become:**

- "Reviewed by a Polish teacher" (unbounded — implies everything)
- "Professionally reviewed" (implies all content)
- "Endorsed by…" / "Approved by…" (endorsement, not review)
- "Created in partnership with…" (unless a partnership genuinely exists and is settled)
- A badge or seal implying whole-application validation

**Required record for any such claim:** scope, reviewer identity and qualification, date, release/version reviewed, what was and was not examined, and written permission. Without all six, no public claim should be made.

**Distinguishing limited review from whole-app endorsement** — three tests any proposed wording must pass:

1. **Scope test** — does the wording state exactly what was reviewed? If a reader could reasonably infer "the whole app", it fails.
2. **Time test** — does it state when? An undated claim implies perpetual currency, which becomes false at the next content release.
3. **Nature test** — does it say *reviewed* rather than *endorsed*, *approved*, *validated*, or *certified*?

---

## 6. Name, logo, and badge requirements

**Before publishing any partner name or logo:**

| # | Requirement |
|---|---|
| 1 | Written permission naming the specific use |
| 2 | Logo files supplied by the partner, with usage guidelines |
| 3 | Agreed placement and prominence |
| 4 | Agreed duration and renewal |
| 5 | A withdrawal process and a committed removal timeframe |
| 6 | Confirmation the partner is content with the surrounding claims |

**Review badges specifically:** a badge is a compressed claim and compresses badly. A badge reading "Reviewed by a Polish teacher" cannot carry scope or date, so it fails tests 1 and 2 in §5. **Recommendation: no review badges.** A sentence with scope and date is both more honest and more informative.

---

## 7. Disclosure requirements

| Situation | Required disclosure |
|---|---|
| Any payment in either direction | Explicit — "sponsored"/"paid" |
| Reciprocal promotion without payment | State the arrangement |
| Free product given for review | Disclose |
| Personal recommendation, no relationship | Current `/guide/listening/` pattern, extended per §1 |
| Limited content review | Scope, date, and nature per §5 |

---

## 8. Maintenance, termination, and standing obligations

**Every partnership creates permanent obligations.** For a one-founder project this is the decisive consideration.

| Obligation | Ongoing cost |
|---|---|
| Keeping review claims current across releases | Each content release potentially invalidates a dated claim |
| Verifying partner links still resolve | Periodic (see maintenance plan) |
| Honouring reciprocal commitments | Ongoing |
| Responding to partner communication | Ongoing |
| Removing wording on termination | One-off but time-sensitive |

**Termination requirements to agree in advance:** notice period, removal timeframe, what happens to already-published claims, and whether a review claim survives (recommended: dated claims may remain if clearly historical; undated claims must be removed).

---

## 9. Recommendations

| # | Recommendation | Phase |
|---|---|---|
| PR-1 | Replace the people-based quality framing in About with the approved process wording, so the claim no longer depends on an individual relationship and cannot be read more broadly than intended | **1** |
| PR-2 | Replace the `/guide/listening/` disclosure with the implication-based wording above, after founder confirmation | **3** (generator-dependent) |
| PR-3 | Publish no partner logo, badge, or collaboration wording until a partnership is settled in writing | ongoing |
| PR-4 | If limited review is pursued, agree scope, date, wording, and permission **before** any review begins | future |
| PR-5 | Keep "What else I listen to" framed as personal recommendations, never as partnerships | ongoing |
| PR-6 | Before any teacher or creator outreach, complete PR-1 and PR-2 so the public surface is consistent with the boundaries being described | **1** |
| PR-7 | Prepare an internal partner one-pager (not published) for institutional conversations | future |

**PR-6 matters more than it looks.** Approaching a teacher or creator while the site still carries an open-ended reference to informal teacher help sends a mixed signal about how carefully claims are scoped — which is precisely the thing a prospective reviewer would judge.

---

## 10. What cannot be established here

| Question | Label |
|---|---|
| Whether any specific person would partner | **Requires external web research** |
| Typical terms for creator collaborations | **Requires external web research** |
| What the help referred to in the About page actually consists of, and its scope | **Requires founder confirmation** |
| Whether the three recommended creators are aware of their inclusion | **Requires founder confirmation** — the repository cannot show this either way |
| Contractual/legal requirements for review claims | **Requires legal review** |
| Disclosure obligations in Poland/EU | **Requires legal review** |
