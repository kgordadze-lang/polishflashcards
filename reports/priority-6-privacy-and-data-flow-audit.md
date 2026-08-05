# Priority 6 — Privacy and Actual Data-Flow Audit

**Phase:** 0 (reports-only). This report describes what the code does and where the Privacy page diverges from it. It is **not** a legal opinion and provides **no legal certification**. Items marked **Requires legal review** need a qualified reviewer.

---

## 1. Headline result

The implementation is **materially more private than most learning products, and the Privacy page is broadly accurate**. Stated precisely — and these are the supportable findings, not absolutes:

- The application contains **no analytics or telemetry code**, sets **no cookie** (no `document.cookie` anywhere), and loads no third-party scripts or external asset hosts. This is a statement about **application code**; whether the live hosting path sets a cookie of its own is **Requires live-browser verification**.
- **Learner progress and local preferences are not transmitted by application code.**
- **All app-initiated fetches are same-origin**, and `connect-src 'self'` enforces that structurally.
- **Ordinary hosting requests still expose normal network metadata** (IP address, user agent, requested path, timestamp) to whoever serves the site — this is inherent to the web, not a defect, but it is real.
- **Clicked external links send ordinary request data to their destinations**, including a referrer.
- **Browser speech synthesis may involve platform-controlled processing** outside the app's control.

The gaps found are precision and completeness gaps rather than misrepresentations.

**A note on absolutes.** This report deliberately avoids phrasing such as "nothing about any user is transmitted anywhere", "no personal data", or "the app only ever contacts its own domain". Each is either unprovable from a repository or contradicted by the hosting, external-link, and speech-fallback analysis below. Whether any of the metadata described here constitutes personal data in a given jurisdiction is a legal question — **Requires legal review**.

---

## 2. Client-side storage — complete inventory

**Repository finding.** `localStorage` only. Exhaustive search found **no** IndexedDB use and **no** `sessionStorage` use (the single textual match, [index.html:4256](index.html:4256), is a comment stating that neither is used).

| Key | Written at | Contents | In backup? |
|---|---|---|---|
| `popolsku-progress-v2` | [pp-migrate.js:29](pp-migrate.js:29) | schemaVersion, migrationRevision, updated timestamp, per-topic known/still card-id arrays | Yes |
| `popolsku-progress-v1` | [pp-migrate.js:28](pp-migrate.js:28) | legacy text-keyed progress | Yes |
| `popolsku-progress-v1-backup` | [pp-migrate.js:29](pp-migrate.js:29) | pre-migration safety copy | Yes |
| `popolsku-progress-v2-recovery` | [pp-migrate.js:31](pp-migrate.js:31) | invalid v2 parked before rebuild | Yes |
| `popolsku-progress-v2-unmapped` | [pp-migrate.js:32](pp-migrate.js:32) | ids that could not be mapped | Yes |
| `popolsku-speed` | [index.html:2938](index.html:2938) | audio playback speed | Yes |
| `popolsku-voicehint` | [index.html:3248-3250](index.html:3248) | `"1"` once the no-Polish-voice hint has been shown | Yes |
| `popolsku-a2hs` | [index.html:5279](index.html:5279) | install-prompt engagement counter, dismissal timestamp | Yes |
| **`pp-card-dir`** | [index.html:1889](index.html:1889), [index.html:3270](index.html:3270) | `"pl"` or `"en"` card direction | **No** |

**No identifier of any kind is generated or stored.** No UUID, no device id, no session id, no fingerprint. Progress is keyed by stable *content* ids, never by user.

### Finding P-1 — backup key-prefix mismatch

`ppBackupData()` copies only keys beginning `popolsku-` ([index.html:5176-5181](index.html:5176)), so `pp-card-dir` is silently excluded from every backup and restore. The Privacy page says a backup contains "your Po polsku progress and **app data**" ([index.html:1599](index.html:1599)), which overstates coverage by one preference. Impact is cosmetic (no progress is lost), but the wording is inaccurate. **Repository finding.**

---

## 3. Service-worker caches

| Cache | Name | Lifecycle | Contents |
|---|---|---|---|
| App shell | `popolsku-v59` | deleted on activate when the version changes — [sw.js:750-772](sw.js:750) | document, 4 helper scripts, 7 data files, audio manifest, manifest, icons, 5 fonts |
| Audio | `popolsku-audio` | **versionless — survives every deploy** — [sw.js:27](sw.js:27) | content-hashed MP3s, added as played |

**Audio retention.** FIFO trim at 4,200 entries down to 4,000 ([sw.js:52-53](sw.js:52)). Today's full library is 3,377 clips, so a learner who warms the entire library never loses one to this policy. Up to roughly 34 MB may persist on the device indefinitely — **explicitly not disclosed on the Privacy page**.

### Finding P-2 — cache footprint not disclosed

The Privacy page's "Your learning data" section covers progress and settings but never mentions that the app may retain tens of megabytes of audio and the full app shell in browser storage indefinitely. A privacy-conscious reader clearing "site data" would want to know this. **Repository finding.**

**Diagnostics.** `SW_STATE` retains at most 20 write failures and 20 audio failures, each holding only a reason, a cache key, and an error message — explicitly "never a body, never learner content" ([sw.js:552-557](sw.js:552)). Held in worker memory, never persisted, never transmitted. No privacy concern.

---

## 4. Network calls — complete inventory

**Repository finding.** Every fetch **initiated by application code** is same-origin. This is a statement about app-initiated requests, not a claim that the browser contacts nothing else: navigating away via an external link, and any platform speech service used by the fallback, are outside this table by nature.

| Call | Origin | Purpose |
|---|---|---|
| `fetch("audio-manifest.json")` — [index.html:3017](index.html:3017) | same | audio index |
| `fetch("./")` — [index.html:5260](index.html:5260) | same | connectivity/shell check |
| MP3 requests | same | pronunciation clips |
| `data-*.js`, helper scripts, fonts, icons | same | app assets |

**External hosts referenced anywhere in shipped code:** `youtube.com`, `patreon.com`, `realpolish.pl` (user-initiated links only) and `schema.org` (a JSON-LD namespace URI — an identifier, not a request).

**No iframes, no embeds, no `<script src="http…">`, no web fonts from a CDN, no analytics beacon, no error reporting service.** Fonts are self-hosted ([index.html:64-69](index.html:64)).

**CSP** ([index.html:38](index.html:38), and identically on every generated page via [build_pages.py](build_pages.py)):

```
default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';
font-src 'self'; img-src 'self'; connect-src 'self'; media-src 'self';
base-uri 'self'; form-action 'self'
```

`connect-src 'self'` means an accidental third-party beacon would be **blocked by policy**, not merely absent. This is a genuinely strong control and worth stating publicly — described accurately as *app-initiated requests go only to this site's own domain*, rather than as an absolute claim that nothing else is ever contacted.

---

## 5. Third parties actually in the path

| Party | Role | Data it necessarily sees | Disclosed? |
|---|---|---|---|
| GitHub Pages | static host | IP, user agent, requested paths, timestamps | Yes — [index.html:1590](index.html:1590) |
| Cloudflare | CDN/proxy — **unverified from repository** | same, if in path | Yes, but see claim C-017 |
| YouTube / Patreon / realpolish.pl | destinations of user-initiated clicks | referrer + normal request data, only on click | **No** |

### Finding P-3 — outbound links not covered by the Privacy page

Three podcast episode links in-app ([index.html:1174](index.html:1174)) and four links on `/guide/listening/` send the user to third parties. The Privacy page does not mention that leaving the site is a thing that happens, or what is shared when it does.

With `strict-origin-when-cross-origin` ([index.html:39](index.html:39)), the referrer sent is the **origin only** (`https://popolsku.app/`), never the full path. That is a good default and worth stating plainly.

### Finding P-4 — inconsistent `rel` on outbound links

| Location | Attributes |
|---|---|
| In-app YouTube link, [index.html:1174](index.html:1174) | `rel="noopener noreferrer"` |
| 4 links on `/guide/listening/`, [guide/listening/index.html:126](guide/listening/index.html:126) | `rel="noopener"` only |

The generated-page links therefore transmit the origin referrer while the in-app link suppresses it. Harmonising on `noopener noreferrer` would be a one-line generator change. **Repository finding.**

---

## 6. Pronunciation and the browser speech fallback

**Repository finding.** `audio-manifest.json` declares `"voice": "pl-PL-MarekNeural"` — a synthetic neural text-to-speech voice.

The Privacy page says:

> Pronunciation normally uses **pre-recorded** audio provided with the app.
> — [index.html:1594](index.html:1594)

### Finding P-5 — "pre-recorded" is ambiguous about provenance

**This is a terminology and consistency issue, not an established inaccuracy.** The clips genuinely are produced in advance and shipped with the app, and a synthetic clip generated ahead of time can fairly be described as pre-recorded or pre-generated. Nothing in the repository establishes that the sentence is false.

The concern is that "pre-recorded" is **open to a human-recording inference** that the underlying process would not support, and that it **drifts from the approved terminology** ("pronunciation-audio clip", "Polish pronunciation audio") used consistently on every other public surface. Adopting the approved wording removes the ambiguity without asserting anything new about how the audio was made.

**Recommended internal wording** (**Requires human copy approval**):

> Pronunciation normally plays a pronunciation-audio clip supplied with the app. If a clip cannot play, the app may use your browser's built-in speech feature, which is controlled by your browser or device.

**Fallback data flow.** When `speechSynthesis` is used ([index.html:3215-3236](index.html:3215); generated pages [build_pages.py:311-327](build_pages.py:311)), the Polish text is handed to the browser. **Some platform speech engines process text server-side.** The current sentence — "That fallback is controlled by your browser or device" — is honest but understates this. **Requires legal review** for whether a more explicit statement is warranted under the applicable data-protection regime.

---

## 7. Backup and restore

`buildBackupEnvelope()` ([pp-migrate.js:404-412](pp-migrate.js:404)) produces:

```json
{ "app": "popolsku.app", "version": "8.4", "schemaVersion": 2,
  "exported": "<ISO timestamp>", "data": { "popolsku-*": "…" } }
```

Downloaded via an object URL to a user-chosen location ([index.html:5185-5197](index.html:5185)). **The backup is produced locally and is not transmitted by application code.** The file contains no name, no email address, and no device identifier — only content ids, counts, timestamps, and preferences. Whether a progress record of this kind constitutes personal data once exported is a legal question — **Requires legal review**.

**Assessment: accurate and well-designed.** The only defect is P-1.

---

## 8. Privacy-page accuracy scorecard

| Statement | Verdict |
|---|---|
| "stored locally in your browser on this device" | **Accurate** |
| "does not send this learning data to an account or central database" | **Accurate** |
| "asks your browser to keep this storage persistently… the browser decides" | **Accurate** — [index.html:5429-5438](index.html:5429) |
| "does not use advertising, marketing cookies, or analytics tools" | **Accurate** |
| "delivered through GitHub Pages and Cloudflare" | GitHub Pages consistent with `CNAME`; **Cloudflare unverified** |
| "does not use this information to build learner profiles" | **Accurate** |
| "pre-recorded audio" | **Ambiguous, not shown to be inaccurate** — Finding P-5 |
| "may use your browser's built-in speech feature" | **Accurate but incomplete** |
| "JSON file containing your Po polsku progress and app data" | **Slightly overstated** — Finding P-1 |

### Omissions

| # | Omission |
|---|---|
| P-2 | Audio/shell cache footprint (up to ~34 MB, persists across deploys) |
| P-3 | Outbound links and what is shared on click |
| P-6 | No statement that CSP structurally blocks third-party connections — a strength left unclaimed |
| P-7 | No "last updated" date on the Privacy page |
| P-8 | No statement of what happens when the user clears browser storage (progress is lost; backup is the remedy) — partially implied but never stated |
| P-9 | No contact route named on the Privacy page for privacy questions |

### Overbroad promises

Only one, and it is mild: **"Privacy - your data stays yours"** as the page H1 ([index.html:1570](index.html:1570)). Defensible given local-only storage, but it is a slogan sitting where a factual heading belongs. **Requires human copy approval** on whether to keep it.

---

## 9. Future-analytics constraints implied by current wording

If analytics are ever introduced (Phase 5 at the earliest, and only after separate approval), the current page creates these constraints:

1. "does not use… analytics tools" would become false and **must** change in the same release.
2. "without… building a learner profile" forbids any persistent cross-visit identifier.
3. The absence of a cookie banner is only sustainable while nothing requiring consent exists.
4. `connect-src 'self'` would have to be widened for any third-party endpoint — a visible, reviewable weakening of a real control.

Constraint 4 is the useful one: **the CSP is a structural guarantee, and any analytics proposal that requires editing it should face a high bar.**

**A caution that must survive into any future measurement design.** It would be wrong to assert that a future collection endpoint "receives no personal data" merely because the payload carries no identifier and no free text. Any HTTP request to a collection endpoint necessarily also delivers **network metadata** — IP address, user agent, timing, and whatever the request path reveals — and that metadata may itself be relevant to the applicable definition of personal data, particularly in combination. The honest formulation is that a proposed payload contains no identifier and no learner content, while the request itself still carries ordinary network metadata. Whether the result is personal data, and what consent obligations follow, is **Requires legal review** and must not be pre-judged in a product report.

---

## 10. Recommended two-level Privacy structure

**Requires human copy approval.** The factual transparency content below can be drafted and reviewed as ordinary factual work; **Requires legal review** applies to the specific legal conclusions listed in §11, not to the factual corrections themselves.

### Level 1 — concise human-readable summary (top of page)

Five or six plain lines. Every line below is consistent with the speech-fallback (§6) and external-link (§5) analysis — no absolutes:

- Po polsku has no accounts and does not ask who you are.
- Your progress stays in your browser on this device and is not sent anywhere by the app.
- Po polsku does not use advertising, marketing cookies, or analytics tools.
- The app itself only requests files from this site. Links to other sites, and your browser's own speech feature, are outside that.
- Pronunciation clips are saved on your device as you play them.
- You can back up or restore your progress. Clearing Po polsku's site data in your browser removes locally stored progress, settings, downloaded app files, and cached pronunciation clips.

**Note on the third line.** The earlier draft read "No advertising, no analytics, no cookies, no tracking." The repository establishes that **application code** contains no analytics or telemetry and sets no cookie (no `document.cookie` anywhere). It does **not** establish that the live hosting path never sets a cookie — a CDN or host can do so independently of application code. The wording above is exactly the product's existing, correctly-scoped sentence (claim C-015) and claims no more than the evidence supports. **If a bare "no cookies" is retained anywhere, it must be marked Requires live-browser verification before publication.**

**Note on the fourth line.** The earlier draft read "The app only ever contacts its own domain", which contradicts §5 and §6. The wording above keeps the strength of the CSP guarantee while remaining accurate about outbound links and the speech fallback.

**Note on the sixth line — deletion.** The earlier draft said "You can back up, restore, or delete your data at any time." **There is no in-app delete or reset control.** The Privacy screen offers exactly two buttons, `Back up my progress` and `Restore from backup` ([index.html:1602-1603](index.html:1602)); the only `localStorage.removeItem` in the app operates on the install-prompt key, not on learner data ([index.html:5319](index.html:5319)). Deletion happens through the browser's own site-data controls, which clear `localStorage` **and** both service-worker caches — so it removes progress, settings, the cached app shell, and accumulated pronunciation clips together. The replacement wording says that and does not imply a control that does not exist. **Whether a genuine in-app "delete my data" control should be added is a separate product decision, not a wording question.**

### Level 2 — detailed factual explanation (below, expandable)

Existing sections, corrected and extended:

1. **What is stored on your device** — the nine keys, in plain language; the cache footprint (P-2); what clearing browser storage does (P-8).
2. **What the app sends** — app-initiated requests are same-origin; explain CSP as the structural control (P-6). State plainly that delivering any web page involves ordinary network metadata (IP address, browser, page requested, time) reaching whoever serves it.
3. **Hosting** — GitHub Pages (+ Cloudflare only if confirmed, C-017).
4. **Pronunciation** — corrected wording (P-5) plus the speech-fallback nuance, including that some platform speech engines process text on their own servers.
5. **Links to other sites** — the outbound-link disclosure (P-3) and the origin-only referrer.
6. **Backups** — what the file contains and what it does not; corrected coverage (P-1).
7. **Contact and last updated** — (P-9, P-7).

---

## 11. Items requiring legal review

| # | Item |
|---|---|
| L-1 | Whether browser speech-synthesis fallback constitutes a disclosable third-party processing activity |
| L-2 | Whether GitHub Pages / Cloudflare require naming as processors under the applicable regime |
| L-3 | Whether a service aimed at residents of Poland has Polish/EU-specific obligations beyond a plain privacy notice |
| L-4 | Whether the adult-language gate ([index.html:1719-1727](index.html:1719)) carries any age-assurance obligation |
| L-5 | Whether any future analytics event set would trigger consent requirements |

---

## 12. Findings summary

| # | Finding | Severity |
|---|---|---|
| P-5 | "pre-recorded audio" is ambiguous about provenance and drifts from the approved terminology | Medium |
| C-017 | Cloudflare named but unverifiable from repository | Medium |
| P-2 | Audio/shell cache footprint undisclosed | Medium |
| P-3 | Outbound links undisclosed | Medium |
| P-1 | `pp-card-dir` excluded from backups; "app data" overstated | Low |
| P-4 | Inconsistent `rel` on outbound links (referrer leak on generated pages) | Low |
| P-6 | CSP guarantee unclaimed | Low (missed opportunity) |
| P-7 | No "last updated" date | Low |
| P-8 | Effect of clearing browser storage not stated | Low |
| P-9 | No privacy contact route | Low |
