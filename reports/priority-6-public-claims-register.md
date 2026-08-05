# Priority 6 — Public-Claims Register

**Phase:** 0 (reports-only). Every recommended wording below is an internal proposal and **Requires human copy approval**.

Classification key for **evidence-based product claims**: **Verified** (repository evidence fully supports it) · **Needs qualification** (true in a narrower sense than the wording implies, or open to a broader reading than intended) · **Not yet supportable** (repository evidence does not establish it).

A separate category, **Founder assertion**, is used for first-person biographical statements. These are *not* product claims and are **not** classified against repository evidence, because the repository is not the kind of source that could confirm or refute them. They require founder confirmation instead, and they are excluded from the evidence-based classification totals.

Risk key: **High** — could mislead a user about money, privacy, or functionality they will actually rely on. **Medium** — could disappoint, confuse, or be read more broadly than intended. **Low** — cosmetic or inconsistency only.

Machine-readable twin: `priority-6-claims.json`.

---

## Summary

**Evidence-based product claims (19)**

| Classification | Count |
|---|---:|
| Verified | 10 |
| Needs qualification | 9 |
| Not yet supportable | 0 |
| **Total** | **19** |

**Separately tracked**

| Category | Count |
|---|---:|
| Founder assertion (requires founder confirmation) | 1 |

**Risk across all 20 entries**

| Risk | Count |
|---|---:|
| High | 1 |
| Medium | 6 |
| Low | 13 |

**No comparative-superiority claims** ("one of the best", "better than…") and **no numeric content claims** ("1,215 cards", "3,377 clips") appear anywhere in public copy. **Repository finding** — verified by pattern search across all public HTML. This is a good position and should be preserved: numeric claims would create a permanent maintenance obligation.

---

## C-001 — "Completely free"

- **Wording:** `Completely free`
- **Location:** [index.html:1083](index.html:1083) (home hero badge)
- **Pages:** `/`
- **Intended meaning:** no charge, no paid tier.
- **Evidence:** no payment code, no pricing, no paywall anywhere in the repository. JSON-LD asserts `"isAccessibleForFree": true` and `offers.price: "0"` — [index.html:54-55](index.html:54).
- **Contradictory evidence:** none.
- **Classification:** **Verified**
- **Risk:** Low — but *terminology drift*: the Phase 0 locked proof point is **"Genuinely free"**, which is the wording already used on every generated page ending ([build_pages.py:628](build_pages.py:628)).
- **Recommendation:** align the hero badge to `Genuinely free` so all surfaces match.
- **Approval:** Requires human copy approval.

## C-002 — "Po polsku is completely free"

- **Wording:** `Po polsku is completely free, requires no account, and keeps your learning progress on your device.`
- **Location:** [index.html:1628](index.html:1628) (About)
- **Classification:** **Verified**
- **Risk:** Low — same terminology drift as C-001.

## C-003 — "Genuinely free. No account. Works offline."

- **Wording:** `Genuinely free. No account. Works offline.`
- **Location:** [build_pages.py:628](build_pages.py:628) → rendered on all 31 generated pages
- **Classification:** **Needs qualification** (the "Works offline" third of it — see C-005)
- **Risk:** Medium
- **Note:** this line appears on generated pages, which are themselves *not* precached and are unavailable offline before a first visit ([sw.js:908-911](sw.js:908)). The claim is literally about the app it links to, but it is displayed on the surface where it is least true — and for a visitor arriving from search, a generated page may be **the only surface they ever see**.
- **Recommendation (internal proposal, Requires human copy approval).** The generated-page ending must not be left outside the offline mitigation.

  **Recommended default:**

  > Genuinely free. No account required.

  Removing the offline phrase from the generated-page ending is the safest compact option, because no short phrase in that position can be made accurate.

- **Why "Works offline once installed" was rejected as the default.** It reads as a guarantee that installation makes the product available offline, and three separate facts contradict that:
  1. **Previously unplayed pronunciation clips still require a connection** — MP3s are cache-first at runtime and are never precached ([sw.js:923](sw.js:923)).
  2. **Generated pages are not precached before a first visit** — an installed user opening a grammar URL offline that they have never visited is redirected to root ([sw.js:908-911](sw.js:908)).
  3. **Installation alone does not make every generated URL or every clip available offline.** Installing changes presentation and launch behaviour, not cache contents.

  A phrase that names installation as the condition therefore replaces one inaccuracy with another.

- **Accepted alternative** — keep an offline mention, but only alongside a precise explanation rather than compressed into the proof-point line: an adjacent sentence stating that the app works offline after a first visit, that pages open offline once visited, and that pronunciation clips are saved as they are played. Only worth doing if the extra length on 31 pages is acceptable.
- **The detailed offline qualification stays on Install and Privacy**, where there is room to be accurate about all three limits. The generated-page ending should not attempt to carry it.
- **Implementation note:** this is a single string in [build_pages.py:628](build_pages.py:628) that regenerates all 31 pages. See the implementation plan for why that places it in Phase 3 rather than Phase 1.

## C-004 — "No account needed" / "no account"

- **Wording:** `No account needed` (badge); `requires no account`; `No app store, no account.`
- **Location:** [index.html:1087](index.html:1087), [index.html:1628](index.html:1628), [index.html:1675](index.html:1675); `manifest.json:5`
- **Evidence:** no authentication code, no sign-in UI, no user identifier of any kind. Progress lives in `localStorage` under `popolsku-*` keys — [pp-migrate.js:27-33](pp-migrate.js:27).
- **Classification:** **Verified**
- **Risk:** Low

## C-005 — "Works offline"

- **Wording:** `works offline` / `Works offline.` / `it launches full screen and runs offline`
- **Location:** [index.html:1110](index.html:1110), [index.html:1675](index.html:1675), [index.html:1699](index.html:1699), [build_pages.py:628](build_pages.py:628), `manifest.json:5`, [index.html:50](index.html:50)
- **Intended meaning:** the app is usable without a network connection.
- **Evidence supporting:** `REQUIRED_ASSETS` precaches the document, four helper scripts, seven data files, and the audio manifest; install **fails** if any required asset cannot be stored — [sw.js:81-95](sw.js:81), [sw.js:716](sw.js:716). Icons and fonts are best-effort optional — [sw.js:97-110](sw.js:97).
- **Limiting evidence:** three real limits, all **Repository finding**:
  1. **MP3s are never precached.** Audio is cache-first at runtime only — [sw.js:923](sw.js:923). A learner offline who has not previously played a clip gets no clip.
  2. **Generated pages are never precached.** `GENERATED_PAGE_ASSETS` ([sw.js:127](sw.js:127)) feeds request *classification*, not the install step; generated pages are network-first and redirect to root on an offline miss — [sw.js:908-911](sw.js:908).
  3. Offline capability begins only **after** a first successful online visit installs the worker.
- **Classification:** **Needs qualification**
- **Risk:** **High** — a learner who installs on airport Wi-Fi and expects offline audio on the plane will find silent cards. This is the one claim in the register where the gap is functional rather than terminological.
- **Recommendation (internal proposal):** keep the short badge as-is on the app shell, and add one clarifying sentence on Install and Privacy, e.g. *"After your first visit the app works offline. Pronunciation clips are saved as you play them, so clips you have not played yet need a connection the first time."*
- **Generated pages must also be covered.** Clarifying only Install and Privacy leaves the claim unqualified on the 31 generated pages, which are precisely the surfaces a search visitor sees first and which are themselves not available offline before a first visit. See C-003 for the three options and the recommended default.
- **Approval:** Requires human copy approval.

## C-006 — "One tap to open, works offline" (install banner)

- **Wording:** `One tap to open, works offline.`
- **Location:** [index.html:1110](index.html:1110)
- **Classification:** **Needs qualification** — same audio limitation as C-005.
- **Risk:** Medium

## C-007 — "Polish pronunciation audio"

- **Wording:** `Polish flashcards with Polish pronunciation audio`
- **Location:** [index.html:8](index.html:8), [index.html:22](index.html:22), [index.html:30](index.html:30), [index.html:1079](index.html:1079), plus generated-page descriptions
- **Evidence:** 3,377 required phrases, 3,377 manifest entries, 3,377 MP3s on disk; 0 missing, 0 orphaned — `verify_audio.py`, run this session.
- **Classification:** **Verified**
- **Risk:** Low
- **Note:** this wording is **exactly** the approved audio terminology. It should be treated as the canonical phrasing and protected from drift.

## C-008 — `manifest.json` "flashcards with audio"

- **Wording:** `Free Polish flashcards with audio for A1-B1`
- **Location:** `manifest.json:5`
- **Classification:** **Needs qualification**
- **Risk:** Low
- **Reason:** the only public surface that drops "pronunciation" from the approved phrase. `index.html:50` uses the full approved form for the same sentence. Inconsistency, not inaccuracy.
- **Recommendation:** align to `Polish pronunciation audio`. Note this changes the installed-app description and **has a service-worker cache implication** (see implementation plan, Phase 3).

## C-009 — "pre-recorded audio provided with the app"

- **Wording:** `Pronunciation normally uses pre-recorded audio provided with the app. If a clip cannot play, the app may use your browser's built-in speech feature.`
- **Location:** [index.html:1594](index.html:1594) (Privacy → Pronunciation)
- **Evidence:** `audio-manifest.json` declares `"voice": "pl-PL-MarekNeural"`, a synthetic neural text-to-speech voice, and 3,377 MP3 files ship with the app.
- **Assessment:** the statement is **not** established as false. The clips genuinely are produced in advance and shipped with the app, and "pre-recorded" is a defensible description of a pre-generated audio file. The issue is **ambiguity**, not misrepresentation: "pre-recorded" is open to a human-recording inference that the underlying process would not support, and it drifts from the approved terminology ("pronunciation-audio clip", "Polish pronunciation audio") used consistently on every other surface.
- **Classification:** **Needs qualification**
- **Risk:** **Medium** — an ambiguous provenance term that a reader could interpret more narrowly than intended, and an internal consistency gap against the approved wording. Not an established provenance misrepresentation.
- **Recommendation (internal proposal):** adopt the approved terminology, e.g. *"Pronunciation normally plays a pronunciation-audio clip supplied with the app. If a clip cannot play, the app may use your browser's built-in speech feature."* This removes the ambiguity without asserting anything new about provenance.
- **Approval:** Requires human copy approval. Whether to describe the audio's provenance positively and explicitly is a founder decision, not one the repository can settle.

## C-010 — Pronunciation fallback to browser speech

- **Wording:** as C-009, second sentence.
- **Evidence:** app fallback at [index.html:3193](index.html:3193) and [index.html:3215-3236](index.html:3215); generated-page fallback at [build_pages.py:311-327](build_pages.py:311). Generated pages emit a control even when no clip exists, with an empty `data-audio` — [build_pages.py:660-676](build_pages.py:660).
- **Classification:** **Verified** — the disclosure is accurate and appropriately placed.
- **Risk:** Low

## C-011 — "with help from native Polish speakers around me, including my teacher"

- **Wording:** `I review and improve the content continuously, with help from native Polish speakers around me, including my teacher.`
- **Location:** [index.html:1627](index.html:1627) (About)
- **Intended meaning:** informal quality help from Polish speakers the founder knows.
- **Evidence in repository:** `validate_content.py` recognises review-ticket and review-reference metadata ([validate_content.py:33-36](validate_content.py:33)), which shows a review *mechanism* exists.
- **Limiting evidence:** the repository holds no record of **what** was reviewed, **how much** of the content was covered, or **when** — there is no coverage figure and no review log. The sentence itself is unremarkable and is very likely true of the founder's circumstances; the repository simply cannot characterise the scope of the help.
- **What this claim does *not* do:** it does not name or identify any particular person — "my teacher" is a relationship, not an identity — and it asserts no partnership, no professional review, and no endorsement. The repository also cannot establish whether the founder asked for or received permission to mention this, and **the absence of consent evidence in a code repository is not evidence that consent was absent.** No inference about consent is drawn here.
- **The genuine issue:** the wording is **open to a broader reading than intended**. "with help from native Polish speakers around me, including my teacher" can be read by a visitor as "a Polish teacher checks this app", which would overstate a documented, ongoing quality process. Process-based wording is clearer, is not dependent on any individual, and stays accurate as the content grows.
- **Classification:** **Needs qualification** — the underlying statement is not shown to be false; it is undocumented in scope and open to over-reading.
- **Risk:** **Medium** — a reader may infer more systematic external review than the repository can evidence.
- **Recommendation (internal proposal):** replace the trust framing with the approved process wording, e.g. *"I review and improve the content continuously. New major content releases follow a structured linguistic and audio-review process."* This is more sustainable than a sentence whose accuracy depends on an individual relationship, and it does not require documenting anyone's involvement.
- **Approval:** Requires human copy approval. **Requires founder confirmation** of what the help actually consists of, if the founder prefers to keep a people-based framing rather than adopt the process wording.

## C-012 — "I review and improve the content continuously"

- **Wording:** as above, first clause.
- **Evidence:** `validate_content.py` (150 KB deterministic validator), 149 Python tests, 32 JavaScript suites, a frozen forward baseline at `reports/priority-5-forward-frozen-baseline.json` covering 1,675 ids / 13,387 wording / 1,312 policy / 1,777 structure entries. This substantiates *systematic safeguarding*, and release history substantiates *ongoing work*.
- **Classification:** **Verified**
- **Risk:** Low

## C-013 — "It has grown into a practical learning app with vocabulary, grammar, listening, typing, mixed quizzes, conversations, and pronunciation audio"

- **Evidence:** all seven named activities exist — vocabulary (A1/A2/B1, 1,215 cards), grammar (353 drills), listening + typing (synthetic levels, [index.html:1846-1847](index.html:1846)), mixed quizzes (`round` screen, [index.html:1469](index.html:1469)), conversations (8 `convo` scenarios), pronunciation audio (3,377 clips).
- **Classification:** **Verified**
- **Risk:** Low

## C-014 — "I'm a foreigner living in Poland, learning Polish while studying for a master's degree"

- **Location:** [index.html:1626](index.html:1626) (About)
- **Classification:** **Founder assertion** — excluded from the evidence-based product-claim totals.
- **Why it is not classified as Verified:** a statement being first-person does not make it repository-verified. The repository contains no biographical records and **no attempt was made to verify the founder's biography from repository contents** — that would be neither possible nor appropriate. Being unverifiable *here* is not a defect; it simply means this is not the kind of claim a code audit can adjudicate.
- **Risk:** Low
- **Approval:** **Requires founder confirmation** that the statement remains current (for example, that the master's study is still accurate at publication time).
- **Note:** the *framing* is the correct pattern and should be preserved in Phase 1. Founder biography and opinion are clearly separated from product claims by voice and placement, which is exactly how it should stay.

## C-015 — "Po polsku does not use advertising, marketing cookies, or analytics tools"

- **Location:** [index.html:1589](index.html:1589) (Privacy)
- **Evidence:** exhaustive search finds **zero** occurrences of `document.cookie`, zero analytics SDKs, zero third-party scripts, zero iframes/embeds. The only external hosts referenced anywhere in shipped code are `youtube.com`, `patreon.com`, `realpolish.pl` (user-initiated links) and `schema.org` (a JSON-LD namespace URI, not a network request). CSP `default-src 'self'` blocks the rest — [index.html:38](index.html:38).
- **Classification:** **Verified**
- **Risk:** Low — and this is the product's strongest trust asset.

## C-016 — "stored locally in your browser on this device"

- **Location:** [index.html:1582](index.html:1582)
- **Evidence:** `localStorage` only. No IndexedDB anywhere; no `sessionStorage` (the single match at [index.html:4256](index.html:4256) is a comment saying it is deliberately *not* used).
- **Classification:** **Verified**
- **Risk:** Low

## C-017 — "The site is delivered through GitHub Pages and Cloudflare"

- **Location:** [index.html:1590](index.html:1590)
- **Evidence:** `CNAME` contains `popolsku.app`, consistent with GitHub Pages custom-domain hosting. Cloudflare is **not** verifiable from the repository.
- **Classification:** **Needs qualification** — accurate as far as the repository shows for GitHub Pages; Cloudflare is an **Assumption requiring validation**.
- **Risk:** Medium — naming a specific processor that may not be in the path is a factual exposure.
- **Verification needed:** **Requires live-browser verification** (response headers) to confirm Cloudflare is actually in front of the site.

## C-018 — "A backup downloads a JSON file containing your Po polsku progress and app data"

- **Location:** [index.html:1599](index.html:1599)
- **Evidence:** `ppBackupData()` copies **only** keys prefixed `popolsku-` — [index.html:5176-5181](index.html:5176).
- **Limiting evidence:** the card-direction preference is stored as **`pp-card-dir`** ([index.html:1889](index.html:1889), [index.html:3270](index.html:3270)) — a `pp-` prefix, not `popolsku-`. It is therefore **excluded from every backup**.
- **Classification:** **Needs qualification**
- **Risk:** Low (one cosmetic preference, no progress loss) — but the Privacy page says "app data", which overstates coverage.
- **Recommendation:** either narrow the wording to "your progress and settings saved under Po polsku's own storage keys", or treat the key-prefix mismatch as a Phase 2+ code fix. **Reports-only in Phase 0.**

## C-019 — "Po polsku is designed to help you learn Polish without requiring an account or building a learner profile"

- **Location:** [index.html:1578](index.html:1578)
- **Evidence:** no identifier is generated, stored, or transmitted. The only persisted values are progress, a speed preference (`popolsku-speed`), a one-time voice hint flag (`popolsku-voicehint`), an install-prompt state (`popolsku-a2hs`), and `pp-card-dir`.
- **Classification:** **Verified**
- **Risk:** Low

## C-020 — "These are personal recommendations. None of the creators paid to be included here."

- **Location:** [build_pages.py:914](build_pages.py:914) → `/guide/listening/`
- **Repository evidence:** the four outbound links carry no affiliate parameters, no tracking parameters, and no sponsorship markup — [guide/listening/index.html:126](guide/listening/index.html:126).
- **What that evidence does *not* establish.** The absence of affiliate or tracking parameters is **not** proof that no commercial or review relationship exists. Money, agreements, and reviews leave no trace in a static site's markup. Specifically, the repository **cannot** establish:
  - whether any creator paid to be included;
  - whether any creator is currently a partner;
  - whether any creator has reviewed any part of the app;
  - whether any creator has endorsed the app;
  - whether any creator is aware of their inclusion.
- **Consequence for the existing published sentence.** "None of the creators paid to be included here" is a **factual assertion about payment that the repository cannot verify**. It is very likely true, but it rests on founder knowledge, not on code. It therefore **Requires founder confirmation** before it is republished or extended.
- **Classification:** **Needs qualification**
- **Risk:** Medium
- **Missing:** the disclosure does not address what a reader may *infer* about partnership or endorsement.
- **Recommendation (internal proposal).** Use **implication-based** wording, which addresses what inclusion signals without asserting relationship facts the repository cannot support:

  > These are personal recommendations. None of the creators paid to be included. Inclusion here does not indicate a formal partnership with Po polsku or an endorsement of the app.

  The third sentence is a statement about **what inclusion means**, which is within the founder's authority to state. The first two sentences remain factual assertions and **Require founder confirmation** before publication.

- **Explicitly rejected wording.** Do **not** use "none of them is a partner", "none of them has reviewed", or any other categorical statement about a third party's relationship or activity, unless each is separately confirmed. Such wording asserts knowledge about other people that neither the repository nor, necessarily, the founder possesses — and it would be a stronger claim than the disclosure needs in order to do its job.
- **Approval:** Requires human copy approval **and Requires founder confirmation** on three separate questions: (1) that no creator paid to be included; (2) each creator's actual relationship status; (3) whether each creator is aware of their inclusion. Question (3) is independent of the wording and does not block it.
- **Phase:** **3** — this string lives in [build_pages.py:914](build_pages.py:914), so it is deferred with all other generator-dependent work (R-12).

---

## Claims deliberately **absent** (and worth keeping absent)

**Repository finding** — verified by search; none of the following appear anywhere in public copy:

| Absent claim | Why keeping it absent matters |
|---|---|
| "native speaker audio" / "human-recorded" | Would misdescribe the process: the manifest voice is `pl-PL-MarekNeural`, a synthetic neural TTS voice |
| "professionally reviewed" | No coverage record exists |
| Whole-app teacher endorsement | Forbidden by the Phase 0 brief. C-011 does not make this claim, but its current wording is open to being read that way |
| Card / audio / topic totals | Would create a permanent maintenance obligation |
| "one of the best", comparative superiority | Unverifiable |
| Accessibility conformance ("WCAG AA", "fully accessible") | Extensive a11y test coverage exists, but conformance is not certified |
| Partnership or collaboration with a named person or organisation | No approved partner exists |
| iPhone/Android *verified* support | Physical-device verification is explicitly incomplete |

The Install page describes iOS and Android install *steps* ([index.html:1678-1697](index.html:1678)) without claiming verified support. That is the right side of the line, but the steps themselves are **Requires physical-device verification**.
