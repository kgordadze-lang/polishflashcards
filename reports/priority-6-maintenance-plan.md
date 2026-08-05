# Priority 6 — Sustainable One-Founder Maintenance Plan

**Phase:** 0 (reports-only). This is a proposed routine, not an implemented process.

**Design principle:** a checklist a single person can actually sustain beats an operational system nobody runs. Everything below is either monthly or release-triggered. Nothing requires new tooling, a dashboard, or a service.

---

## 1. What already protects the product automatically

**Repository finding.** A substantial safety net exists and needs no ongoing effort:

| Safeguard | What it catches |
|---|---|
| `validate_content.py` | ID integrity, wording/policy/structure drift against the frozen forward baseline, card policy, CEFR validity, duplicates, conversation-graph termination, audio planning |
| `reports/priority-5-forward-frozen-baseline.json` | Unapproved changes to 1,675 ids, 13,387 wording entries, 1,312 policy entries, 1,777 structure entries |
| `verify_audio.py` | Missing and orphaned audio across 3,377 phrases |
| 149 Python tests | Generator and content rules |
| 32 JavaScript suites (9,535 assertions) | Runtime behaviour, accessibility, service worker, migration |

**Consequence: the routine below deliberately does not re-check anything these already cover.** It covers only what automation cannot see.

---

## 2. Monthly checklist

**Estimated total: 45–70 minutes per month.**

| # | Task | Trigger | Effort | Evidence / tool | Escalation threshold | Record to retain |
|---|---|---|---|---|---|---|
| M1 | Read and triage the `hello@` inbox; batch corrections | Monthly | 15–20 min | Mail client, filtered by subject prefix | >10 unhandled corrections → schedule a content release | Running list of accepted corrections + release they landed in |
| M2 | Apply accepted content corrections | Monthly, if any | 15–30 min | `validate_content.py` after edits | A correction that fails validation → investigate before shipping | Correction log entry with card id |
| M3 | Check the 3 outbound creator links on `/guide/listening/` still resolve | Monthly | 5 min | Browser | Any dead link → fix in the next release | Date checked |
| M4 | Check Search Console coverage and top queries **(only once configured)** | Monthly | 10 min | Search Console | Indexed count drops below 32, or any manual action → investigate immediately | Screenshot or short note: indexed count, top 5 queries |
| M5 | Review the claims register for drift | Monthly | 5 min | `priority-6-public-claims-register.md` | Any live claim no longer supported → fix in next release | Date reviewed |
| M6 | Confirm the site loads and one activity completes on a real phone | Monthly | 5 min | Physical device | Any failure → treat as urgent | Date + device |

**Note on M4:** Search Console is not configured today (measurement §2). Until it is, M4 is unavailable — and its absence means **there is currently no way to notice if the site falls out of the index.** This is the strongest practical argument for configuring it. Note also that Search Console covers **Google Search only**; it is not a referral analytics system and will not show arrivals from newsletters, directories, creators, communities, or social posts.

---

## 2a. Working method — the isolated repository workflow

**This applies to every task in this plan that changes a file**: user corrections, technical fixes, generator changes, and releases. It is the established workflow and is not optional.

| # | Step | Why |
|---|---|---|
| 1 | **Work in a fresh, remote-free disposable clone.** Never in the production repository | A disposable clone cannot push, cannot be pulled from, and cannot damage production by accident |
| 2 | **Verify preconditions before touching anything** — exact path, branch, HEAD, clean working tree, no remotes, no Git alternates, no linked worktrees | Catches a wrong-repository mistake before, not after, the first edit |
| 3 | **Create a focused branch** for the single change | Keeps the diff reviewable and revertible |
| 4 | **Run full validation** — `validate_content.py`, `verify_audio.py`, the Python suite, all 32 JavaScript suites | Nothing ships without the safety net in §1 |
| 5 | **Review the diff independently**, path by path, before committing | The step that catches accidental generator runs and scope violations |
| 6 | **Confirm scope**: every changed path is one you intended, and no public, content, audio, version, cache, schema, or migration file changed unless that was the point of the change | Explicit scope confirmation, not assumption |
| 7 | **Transfer approved files manually** to the persistent Priority 6 integration repository | Manual transfer forces a second look at exactly what moves |
| 8 | **No direct work in the production repository. No push, no deploy, before release-candidate approval** | Deployment is a decision, never a side effect |

**Two hazards this workflow exists to catch**, both observed in practice:

- **`build_pages.py` regenerates unconditionally.** It takes no arguments and has no dry-run mode, so *any* invocation — including an accidental one while exploring — rewrites all 31 generated pages and resets every `lastmod` in `sitemap.xml` to the run date. Step 5 is what turns this from a silent commit into a caught mistake. Until the `--check` mode from Phase 3 exists, treat every generator run as a change to the working tree.
- **A clean `git status` is not the same as an unchanged tree.** Verify against the expected HEAD and tree hash (step 2), not just against "no output".

---

## 3. Release checklist

Triggered by any content or code release. **Estimated 30–50 minutes**, most of it automated.

| # | Task | Effort | Evidence / tool | Escalation threshold | Record |
|---|---|---|---|---|---|
| R1 | Run `python3 validate_content.py` | 1 min | expects `levels=10 topics=97 cards=1215 drills=353`, 1,675 ids | **Any** failure blocks the release | Console output in release notes |
| R2 | Run `python3 verify_audio.py` | 2 min | expects 3,377/3,377/3,377, 0 missing, 0 orphaned | Any missing/orphaned blocks the release | Output |
| R3 | Run `python3 -m pytest tests/ -q` | ~80 s | expects 149 passed | Any failure blocks | Count |
| R4 | Run all 32 JavaScript suites via `osascript -l JavaScript` | ~2 min | expects 0 failures | Any failure blocks | Suite count + assertion total |
| R5 | If generated pages changed: regenerate and review the diff | 5 min | `build_pages.py` | Unexpected diff → investigate before committing | Diff summary |
| R6 | Bump `APP_VERSION` if learner-visible | 1 min | [index.html:1775](index.html:1775) | — | New version |
| R7 | Bump `CACHE` in `sw.js` if the shell changed | 1 min | [sw.js:26](sw.js:26) | Shell changed without a bump → users keep the old release | New cache name |
| R8 | Verify `AUDIO_CACHE` still `popolsku-audio` | <1 min | [sw.js:27](sw.js:27) | **Never change** — would discard every user's cached audio | Confirmed |
| R9 | Verify `schemaVersion` / `CONTENT_MIGRATION_REVISION` unchanged unless a migration is intended | 1 min | [pp-migrate.js:21](pp-migrate.js:21), [:25](pp-migrate.js:25) | Unintended change → progress-loss risk | Confirmed |
| R10 | Check any public claim touched by the release against the claims register | 5 min | claims register | New unsupported claim → fix before release | Claim IDs reviewed |
| R11 | Spot-check the release on a real phone | 5 min | Physical device | Any regression → hold | Date + device |
| R12 | Write short release notes | 5 min | — | — | Release note entry |

### Standing hazards worth naming

- **R7 is the easiest step to forget and one of the most consequential**: a shell change without a `CACHE` bump means the release silently does not reach existing users.
- **R8 must never change.** `popolsku-audio` is versionless by design ([sw.js:17-20](sw.js:17)); renaming it would discard up to ~34 MB of cached audio for every existing user and force a full re-download on mobile data.
- **`build_pages.py` regenerates unconditionally and resets every sitemap `lastmod`** (SEO S-9). Until a `--check` mode exists, R5 dirties the working tree by design — review the diff before committing, and revert if the only change is `lastmod` churn.

---

## 4. Quarterly checklist

**Estimated 60–90 minutes per quarter.**

| # | Task | Effort | Escalation | Record |
|---|---|---|---|---|
| Q1 | Full read of the Privacy page against actual behaviour | 20 min | Any mismatch → fix in next release | Date + findings |
| Q2 | Full read of the claims register against live copy | 20 min | Any unsupported claim → Phase-1-style fix | Date |
| Q3 | Verify the sitemap matches the filesystem | 5 min | Mismatch → regenerate | Count |
| Q4 | Review traffic sources **(once measurable)** | 15 min | — | Summary |
| Q5 | Review partnership status and any published third-party wording | 10 min | Stale or unconsented wording → remove immediately | Date |
| Q6 | Re-read the maintenance plan itself; drop steps that never fire | 10 min | — | Revision note |

**Q6 exists deliberately.** A checklist that only grows gets abandoned. Removing steps that have never caught anything is part of keeping it alive.

---

## 5. Event-triggered tasks

| Trigger | Action | Effort |
|---|---|---|
| User reports a content error | Verify → fix → validate → include in next release | 10–20 min |
| User reports a technical issue | Reproduce; if reproducible, treat as release-blocking | 20–60 min |
| Broken outbound link found | Fix or remove in next release | 10 min |
| A recommended creator stops publishing | Reassess the recommendation | 15 min |
| Search Console flags an issue | Investigate immediately | Variable |
| Someone asks about partnership | Apply partnership readiness boundaries; do not publish anything | 15 min |
| A claim is challenged publicly | Check the register; correct promptly if wrong | Variable |

---

## 6. Records to retain

Minimal, all plain text in the repository:

| Record | Where | Why |
|---|---|---|
| Release notes (version, date, what changed, validation results) | repository | Substantiates "continuous review" (claim C-012) |
| Correction log (report → card id → release) | repository | Substantiates the quality process; feeds review scope |
| Claims register review dates | this report set | Shows claims are actively governed |
| Monthly Search Console snapshot | repository or local | Trend detection |
| Partnership permissions and scope | private | Required before any public naming |

**The correction log is the highest-value record.** It converts scattered user emails into evidence of an actual quality process — which is exactly what the approved wording ("New major content releases follow a structured linguistic and audio-review process") needs in order to be truthful.

---

## 7. Explicitly not recommended

| Rejected | Reason |
|---|---|
| Ticketing system | Disproportionate; ongoing cost |
| Uptime monitoring service | Static hosting; M6 is sufficient |
| Automated link checker service | Three outbound links; M3 takes 5 minutes |
| Content calendar | The product is not a publication |
| Community platform | Moderation load incompatible with one founder |
| Weekly cadence for anything | Unsustainable; monthly + release-triggered is the right granularity |
| Dashboards | Nothing to display until measurement exists |
| Editing production directly for "small" fixes | The isolated workflow in §2a applies to every change, however small; a one-character content fix still regenerates and revalidates the same way |

---

## 8. Honest assessment of sustainability

| Cadence | Estimated time |
|---|---|
| Monthly | 45–70 min |
| Per release | 30–50 min |
| Quarterly | 60–90 min |
| **Annual total** | **roughly 18–25 hours**, assuming ~6 releases/year |

This is sustainable for one person alongside a master's degree — **provided** the automated safety net stays healthy. The largest risk to sustainability is not the checklist; it is the volume of user correspondence if the correction route (feedback R-1/R-2) succeeds. Mitigation is built in: subject prefixes enable inbox filters and batching, and if volume ever exceeds capacity the correct response is to narrow the invitation rather than build a system.
