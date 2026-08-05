# Priority 6 — Risk Register

**Phase:** 0 (reports-only).

Priority = Likelihood × Impact, adjusted for reversibility. **P1** = address in Phase 1. **P2** = address in the named phase. **P3** = monitor.

| Field | Meaning |
|---|---|
| Likelihood | How likely the harm is to occur if nothing changes |
| Impact | Severity if it does occur |
| Human decision | What the founder must decide before the mitigation can proceed |

---

**Priority vs Phase.** *Priority* rates the risk. *Phase* says when it is scheduled. Two Medium-priority items (R-01, R-02) are still scheduled in **Phase 1** because they are inexpensive copy changes touching the same paragraphs as the P1 work — low risk does not mean low convenience.

## Priority 1 — address in Phase 1

### R-03 · Claims accuracy / offline

- **Risk:** "Works offline" is stated without qualification on six surfaces, but MP3s and generated pages are **never precached** — audio works offline only for clips already played, and generated pages redirect to root when offline and cold.
- **Evidence:** [sw.js:81-110](sw.js:81), [sw.js:908-911](sw.js:908), [sw.js:923](sw.js:923); claim C-005.
- **Affected surface:** `/`, `/#install`, all 31 generated pages, `manifest.json`
- **Likelihood:** High (any offline learner with unplayed clips) · **Impact:** Medium-High · **Priority: P1**
- **Mitigation:** **two parts, both required.** (a) On the app shell: keep the short badge and add one clarifying sentence on Install and Privacy. (b) **On the 31 generated pages:** qualify or remove the offline phrase in the shared ending — clarifying only Install and Privacy leaves the claim unqualified on the surfaces a search visitor sees first, and those pages are themselves not precached. Options and the recommended default are in claim C-003.
- **Phase:** 1 for the app-shell wording; **3 for the generated-page ending**, because that string lives in `build_pages.py` and any generator run rewrites all generated outputs and the sitemap. The split is deliberate — see the implementation plan, Phase 1 generator strategy.
- **Human decision:** approve clarifying wording; choose among the three generated-page options in C-003.

### R-04 · Positioning

- **Risk:** the homepage never states the locked positioning — no Poland, no A1–B1, no everyday-life context — so the best-fit audience cannot recognise that the product was built for them. Growth work sending traffic here would be wasted.
- **Evidence:** [index.html:7-8](index.html:7), [index.html:1077-1079](index.html:1077); positioning §1.
- **Affected surface:** `/` (title, description, hero)
- **Likelihood:** High · **Impact:** High (gates every growth channel) · **Priority: P1**
- **Mitigation:** rewrite H1/sub/title/description per positioning §5; add founder line.
- **Phase:** 1 (copy) / 3 (metadata)
- **Human decision:** choose the one-line promise; approve all wording.

---

## Priority 2 — address in the named phase

### R-01 · Trust / claims scope *(re-rated from P1/High after review)*

- **Risk:** the About page's quality sentence — "with help from native Polish speakers around me, including my teacher" — has **undocumented scope and coverage** and is **open to a broader reading than intended**: a visitor may take it to mean a Polish teacher systematically checks the app.
- **What this risk is not.** The sentence names no particular person; "my teacher" is a relationship, not an identity. It asserts no partnership, no professional review, and no endorsement. The repository cannot establish whether permission to mention it was requested or granted, and **absence of consent evidence in a code repository is not evidence that consent was absent** — no such inference is made. Nothing shows the statement to be false.
- **Evidence:** [index.html:1627](index.html:1627); claim C-011; partnership readiness §1.
- **Affected surface:** `/#about`
- **Likelihood:** Medium (depends on how a reader interprets it) · **Impact:** Medium · **Priority: P2**
- **Mitigation:** adopt the approved process wording — *"New major content releases follow a structured linguistic and audio-review process."* — which is clearer, does not depend on an individual relationship, and stays accurate as content grows.
- **Phase:** 1 (cheap; same paragraph as R-04)
- **Human decision:** approve replacement wording, **or** confirm the scope of the help if a people-based framing is preferred. **Requires founder confirmation.**

### R-02 · Claims accuracy / audio terminology *(re-rated from P1/High after review)*

- **Risk:** the Privacy page's "pre-recorded audio" is **ambiguous about provenance** and **drifts from the approved terminology** used on every other surface. It is open to a human-recording inference the process would not support.
- **What this risk is not.** The statement is **not shown to be false.** Clips are genuinely produced in advance and shipped with the app, and a synthetic clip generated ahead of time can fairly be called pre-recorded or pre-generated. This is a terminology and consistency issue, not an established provenance misrepresentation.
- **Evidence:** [index.html:1594](index.html:1594); `audio-manifest.json` (`"voice": "pl-PL-MarekNeural"`); claim C-009; privacy P-5.
- **Affected surface:** `/#privacy`
- **Likelihood:** Medium · **Impact:** Medium · **Priority: P2**
- **Mitigation:** adopt the approved terminology ("pronunciation-audio clip"), which removes the ambiguity without asserting anything new about provenance.
- **Phase:** 1 (wording) / 2 (full Privacy restructure)
- **Human decision:** approve wording; decide separately whether to describe audio provenance positively and explicitly.

### R-05 · Discoverability

- **Risk:** no generated page targets everyday-life search intent (doctor, renting, daily phrases) despite A1/A2 containing 37 topics and 854 cards of exactly that material. The largest organic opportunity is unexploited.
- **Evidence:** SEO S-2; `data-a1.js` 15 topics/340 cards, `data-a2.js` 22 topics/514 cards.
- **Affected surface:** generated pages, sitemap
- **Likelihood:** High · **Impact:** High · **Priority: P2**
- **Mitigation:** extend `build_pages.py` to emit 5–8 chosen high-intent pages. Do **not** generate one page per topic.
- **Phase:** 3
- **Human decision:** select which intents; approve page copy. **Requires external web research.**

### R-06 · Naming consistency

- **Risk:** the "Explore more Polish" destination has three public names, and "Guide" persists across 33 pages in 11 surfaces.
- **Evidence:** Explore more Polish audit §2.
- **Affected surface:** `/guide/`, 31 generated pages, 2 stubs, `<noscript>`
- **Likelihood:** Certain (already true) · **Impact:** Medium · **Priority: P2**
- **Mitigation:** resolve the canonical name; update title, H1, JSON-LD, 31 breadcrumbs, stubs, `<noscript>`.
- **Phase:** 3
- **Human decision:** **blocking** — decide the destination's public name.

### R-07 · Content quality feedback loop

- **Risk:** with 1,215 cards, 353 drills, and 3,377 clips, errors exist; no public surface invites or explains how to report one. Errors persist indefinitely and the "continuous review" claim is weakened.
- **Evidence:** feedback F-1; [index.html:1634-1653](index.html:1634).
- **Affected surface:** `/#contact`, generated pages
- **Likelihood:** High · **Impact:** Medium-High · **Priority: P2**
- **Mitigation:** restructure Contact around four reasons with prefilled subjects; add a correction line to generated pages.
- **Phase:** 4
- **Human decision:** approve wording; accept the correspondence volume.

### R-08 · Privacy accuracy

- **Risk:** the Privacy page names Cloudflare as a processor, which cannot be verified from the repository. Naming a processor that is not in the path is a factual error in the document users rely on most for trust.
- **Evidence:** [index.html:1590](index.html:1590); claim C-017.
- **Affected surface:** `/#privacy`
- **Likelihood:** Medium · **Impact:** Medium · **Priority: P2**
- **Mitigation:** confirm the actual delivery path; correct or remove.
- **Phase:** 2
- **Human decision:** confirm hosting configuration. **Requires live-browser verification.**

### R-09 · Privacy completeness

- **Risk:** the Privacy page omits the on-device storage footprint (up to ~34 MB of audio plus the app shell, persisting across deploys), outbound links, and the effect of clearing browser storage.
- **Evidence:** privacy P-2, P-3, P-8; [sw.js:52-53](sw.js:52).
- **Affected surface:** `/#privacy`
- **Likelihood:** Medium · **Impact:** Medium · **Priority: P2**
- **Mitigation:** two-level Privacy structure per privacy audit §10.
- **Phase:** 2
- **Human decision:** approve structure and wording — **Requires human copy approval**. The factual completeness work here (storage footprint, cache behaviour, backups, clearing browser storage, external links, app fetch behaviour) is **ordinary factual transparency work and is not gated by legal review**; it describes observable behaviour and asserts no legal characterisation. **Requires legal review** applies only to the specific legal conclusions L-1 … L-5 (speech-service disclosure duty, processor terminology, Polish/EU obligations, age assurance, future analytics consent).

### R-10 · Activation

- **Risk:** activities are not discoverable from the home screen. The "More" tab hides Type it and Listening; conversations and mixed quizzes are invisible until inside a topic. Differentiating features go unused.
- **Evidence:** [index.html:2328-2332](index.html:2328); activation A-2.
- **Affected surface:** `/` home screen
- **Likelihood:** High · **Impact:** Medium · **Priority: P2**
- **Mitigation:** rename the "More" tab; consider surfacing conversations.
- **Phase:** 4
- **Human decision:** approve the label.

### R-11 · Activation

- **Risk:** no next-step suggestion at activity completion — the moment of highest receptiveness passes unused.
- **Evidence:** activation A-4; [index.html:5168](index.html:5168).
- **Affected surface:** activity completion screens
- **Likelihood:** High · **Impact:** Medium · **Priority: P2**
- **Mitigation:** offer one contextual next action alongside "Again".
- **Phase:** 4
- **Human decision:** approve the pattern. **Requires live-browser verification.**

### R-12 · Partnership boundary

- **Risk:** the `/guide/listening/` disclosure addresses payment and personal framing but does not address the implications a reader may draw about partnership or endorsement; three named creators could be read as partners or endorsers.
- **Evidence:** [build_pages.py:914](build_pages.py:914); claim C-020.
- **Affected surface:** `/guide/listening/`
- **Likelihood:** Medium · **Impact:** Medium · **Priority: P2**
- **Mitigation:** adopt implication-based wording that does not assert relationship facts the repository cannot establish — see C-020 for the recommended sentence.
- **Phase:** **3** — the disclosure is a `build_pages.py` string ([build_pages.py:914](build_pages.py:914)), so it is deferred with all other generator-dependent work under the chosen generator strategy. It is **not** a Phase 1 item.
- **Human decision:** **Requires founder confirmation** that no creator paid to be included and of each creator's actual relationship status, before any wording is published; then approve wording; separately decide whether to notify the creators.

### R-13 · SEO signal integrity

- **Risk:** every `build_pages.py` run resets all 32 sitemap `lastmod` values to the run date regardless of whether content changed, degrading the signal. There is also no safe way to check generator drift without dirtying the working tree.
- **Evidence:** SEO S-9; observed directly this session.
- **Affected surface:** `sitemap.xml`
- **Likelihood:** Certain on every regeneration · **Impact:** Low-Medium · **Priority: P2**
- **Mitigation:** derive `lastmod` from actual content change; add a `--check` mode.
- **Phase:** 3
- **Human decision:** approve the generator change.

### R-14 · Measurement / decision-making

- **Risk:** there is no visibility into traffic or usage of any kind, and Search Console is not configured — so it is not currently possible to notice if the site falls out of the index.
- **Evidence:** measurement §1–2.
- **Affected surface:** whole product
- **Likelihood:** Certain · **Impact:** Medium · **Priority: P2**
- **Mitigation:** configure Search Console. It requires no instrumentation code in Po polsku, adds no application cookie or application-assigned identifier, and does not change what application code sends. It reports Google Search performance only — not non-Google referrals or on-site activity. **Account-level, provider, disclosure, and legal implications are a separate human review question** and are not concluded here.
- **Phase:** separate decision, before Phase 5
- **Human decision:** **explicit approval required** — Phase 0 forbids configuring or accessing it.

---

## Priority 3 — monitor

### R-15 · Privacy consistency
Outbound links on `/guide/listening/` carry `rel="noopener"` without `noreferrer`, unlike the in-app YouTube link. Origin referrer leaks. Evidence: privacy P-4. **Likelihood:** Certain · **Impact:** Low · **Phase:** 3.

### R-16 · Backup completeness
`pp-card-dir` is excluded from backups because it lacks the `popolsku-` prefix, while Privacy says backups contain "app data". Evidence: privacy P-1; [index.html:5176-5181](index.html:5176). **Impact:** Low · **Phase:** 2 (wording) or later (code).

### R-17 · Social sharing
`og:image:width`/`height` on 1 of 34 pages; `twitter:image` on 1 of 34; one shared image sitewide. Evidence: SEO S-5, S-6, S-7. **Impact:** Low · **Phase:** 3.

### R-18 · Terminology drift
Hero badge says "Completely free"; the approved proof point and every generated page say "Genuinely free". Evidence: claim C-001. **Impact:** Low · **Phase:** 1.

### R-19 · Terminology drift
`manifest.json` says "flashcards with audio"; every other surface says "Polish pronunciation audio". Evidence: claim C-008. **Impact:** Low · **Phase:** 3. **Note:** changing `manifest.json` has a service-worker cache implication.

### R-20 · Discoverability of trust pages
About, Privacy, Contact, and both SEO destinations are reachable only via the drawer; the footer holds only the version line, with unused `.foot-guides` CSS at [index.html:639-644](index.html:639). Evidence: activation A-6, feedback F-4. **Impact:** Low-Medium · **Phase:** 4.

### R-21 · Structured data
No `BreadcrumbList` despite visible breadcrumbs on 31 pages. Evidence: SEO S-4. **Impact:** Low · **Phase:** 3.

### R-22 · Verification debt
Physical-device verification remains explicitly incomplete: iPhone Safari and installed PWA, iPad, Android Chrome and installed PWA, VoiceOver, TalkBack, text scaling, safe areas and orientation, weak-network transitions, storage pressure, install/remove/reinstall. **This is an accepted limitation, not evidence of failure.** **Impact:** Medium · **Phase:** 7 · **Human decision:** whether to obtain device access before a release candidate.

### R-23 · Maintenance capacity
Adding a correction route (R-07) increases correspondence volume for a solo founder alongside a master's degree. Evidence: feedback §4; maintenance §8. **Impact:** Medium · **Mitigation:** subject prefixes for filtering; narrow the invitation rather than build a system if volume exceeds capacity.

### R-24 · Future measurement conflict
Any analytics implementation would falsify "does not use… analytics tools", may require widening `connect-src 'self'`, and would forfeit a genuine differentiator. Evidence: measurement §3, §7. **Impact:** High **if mishandled** · **Phase:** 5 · **Human decision:** whether measurement value exceeds the cost of weakening the privacy position.

### R-25 · Paid-spend premature
Spending before positioning, feedback, and measurement exist converts money into noise; the two largest opportunities (S-1, S-2) are free. Evidence: paid experiments §1, §4. **Impact:** Medium · **Human decision:** defer all spend until Phases 1–4 complete.

---

## Summary

| Priority | Count | IDs |
|---|---:|---|
| P1 | 2 | R-03, R-04 |
| P2 | 12 | R-01, R-02, R-05 … R-14 |
| P3 | 11 | R-15 … R-25 |
| **Total** | **25** | |

**Scheduled in Phase 1 regardless of priority:** R-03 (app-shell portion only), R-04, R-01, R-02, R-18 — all inexpensive `index.html` copy changes touching overlapping paragraphs. **R-12 is not among them:** it lives in `build_pages.py` and is scheduled in Phase 3.

**By category:** claims accuracy 5 · privacy 5 · SEO/discoverability 6 · activation 3 · partnership 1 · measurement 2 · maintenance 2 · verification 1.

### Changes made after independent review

| Risk | Was | Now | Reason |
|---|---|---|---|
| R-01 | P1, Impact High, framed as implied endorsement citing an unconsented third party | **P2, Impact Medium**, framed as undocumented scope and over-broad readability | The sentence names no one, asserts no endorsement or partnership, and is not shown to be false. Absence of consent evidence in a repository is not evidence of absent consent, and no such inference is now drawn |
| R-02 | P1, Impact High, framed as provenance misrepresentation | **P2, Impact Medium**, framed as ambiguous terminology and consistency drift | A synthetic clip generated in advance can accurately be called pre-recorded; the statement is not shown to be false |
| R-03 | Mitigation covered Install and Privacy only | **Mitigation now explicitly covers the 31 generated pages** | Generated pages are not precached and may be a visitor's only viewed surface, so leaving them out left the claim unmitigated where it matters most |

**The two remaining P1 risks share one root cause:** the public surface does not tell a visitor who the product is for (R-04), and asserts offline capability the service worker does not deliver before a first visit (R-03). R-03 is the only entry in the register where the gap is **functional** rather than terminological — which is precisely why it retains High impact while R-01 and R-02 do not. Phase 1 remains correctly scoped as a claims-accuracy phase rather than a marketing phase.
