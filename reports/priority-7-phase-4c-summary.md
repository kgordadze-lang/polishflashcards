# Priority 7 — Phase 4C: Applying Human Review to Canonical Editorial Data

**Verdict: GO WITH GOVERNANCE BLOCKER**

The human review is real, complete, and green. Phase 4C applied every consequence the locked
governance contract legitimately permits, and stopped at two dependencies it cannot satisfy
without fabricating provenance. No pattern reached `native-reviewed`; the five accepted
replacement sentences did not enter the canonical corpus. Both refusals are proven mechanically
below, not asserted.

> **Revision note.** The first candidate was independently reviewed by Codex and returned
> **NO-GO**. The governance conclusion above was confirmed correct and is unchanged. Three
> defects in the supporting evidence were found and repaired — see **§17a**. This report
> reflects the repaired state; §17a records what the initial implementation got wrong.

## 1. Repository baseline

| Check | Expected | Observed |
|---|---|---|
| Working directory | Phase 4C repo | `/Users/Kaj/Downloads/Repository for Claude - Priority 7 Phase 4C` |
| Branch | `priority-7-phase-4c-apply-human-review` | matches |
| HEAD | `66f9d68871a0862bcbe8bd04804fb3fc3ca4131c` | matches |
| HEAD tree | `a5efadc95ae4bec477a36ccab06bd812a27180c0` | matches |
| Git remotes | zero | zero |
| `push.default` | `nothing` | `nothing` |
| Starting worktree | clean | clean |
| Commit / push | none | none; HEAD unchanged |

## 2. Baseline tests (before any edit)

| Check | Expected ballpark | Observed |
|---|---|---|
| Python suite | 449 | **449 passed, 0 failed** |
| JXA suites | 36 / 10,544 assertions | **36 suites, 10,544 assertions, 0 failed** |
| `validate_content.py` | pass | OK, forward baseline `2a71401d…1ce50` |
| `verify_audio.py` | pass | 3377 phrases / 3377 manifest / 3377 MP3s, nothing orphaned |
| `build_pages.py --check` | pass | committed output current, 32 sitemap URLs |
| `git diff --check` | clean | clean |
| `validate-editorial` | valid | `Priority 7 private editorial record: valid` |

Baseline was green, so the phase proceeded.

## 3. Human-review input and integrity

External evidence directory, outside Git:
`/Users/Kaj/Downloads/Priority_7_Phase_4B_Human_Attestation`.

| Artifact | SHA-256 | Status |
|---|---|---|
| `phase4b-validated-ledger.json` | `7196ef6a6bc41042ebb1b2c3f4d365c66a8e680a89052ff62437301ffe9fb209` | **matches the expected value; verified before editing** |
| `review-attestation.json` | `1e97a63dea0bce20f5a86b74d364ae641947299f9bd4f3df7342cadc15e9b6a8` | matches Phase 4B |
| `decision-ledger.json` | `f0dcf46f5da950baa06003fa4a7a82f342d75a82098b6414388c8edfadbac961` | matches Phase 4B |

No attestation artifact, screenshot or reviewer communication was copied into the repository.
The validated-ledger SHA-256 is referenced in this report and in the reviewer registry record;
nothing else from the external package is embedded.

The reviewer supplied exactly one blanket judgment. Nothing was reinterpreted or expanded:
no `Natural = Yes`, no `Structure = Yes`, no separate treatment answers, no comments, no
explanations, no teaching credentials. Every row carries `specificFeedback: null`,
`reviewerComment: null`, `flagged: false`, `unresolved: false`.

## 4. Reviewer record

Recorded in `editorial/priority-7-authoring-context.json` under `reviewerRegistry`:

| Field | Value |
|---|---|
| Stable ID | `native-reviewer-001` |
| Display / initials | `AB` |
| Background | `Native Polish speaker` |
| `nativePolishSpeaker` | `true` |
| `human` | `true` |
| `roles` | `["native-linguistic"]` — and nothing else |
| `ownerAllowsMultipleRoles` | **deliberately absent** |
| Review date | `2026-08-13` (exact date from the attestation) |
| `attestationLedgerSha256` | `7196ef6a…fb209` |

No teacher, linguist, professor or editor credential was added, because none appears in the
attestation. No contact detail or additional personal information was recorded. AB holds no
external-verification, product-approval, correction or reopen authority, and is not an author.

## 5. The governance contract, as the tooling actually defines it

Read before editing: `priority7_tooling.py`, the Phase 1 provenance/review specification, the
stable-ID specification, Phase 2A tests, the Phase 2B source-evidence audit, Phase 4A/4B
reports, Phase 5-A summary and governance tests, and the real corpus.

The locked progression is `research → externally-verified → native-reviewed → approved`, and
`priority7_tooling.py` enforces it fail-closed:

- `_review_history_state` raises `REVIEW_STAGE_ORDER` for any `native-linguistic` acceptance
  whose history state is not already `externally-verified`.
- `native_current` additionally requires `external_current`, which requires a valid external
  acceptance with `scopeVersion 1`, a current `scopeDigest`, and pinned **contemporary**
  evidence digests.
- `_validate_review_event` requires `reviewerRef` to resolve to a registry record with
  `human: true` and the exact role for that stage; an AI identity is rejected outright by
  `REVIEWER_NOT_HUMAN`.
- One human performing two stages requires an explicit `ownerAllowsMultipleRoles` allowance.
- `_validate_origin` requires `origin.kind = "original"` to carry `authorRef` + `authoredAt`,
  with `authorRef` resolving to a registered **human** author.
- `_resolve_repository_reuse` requires a `repository-reuse` example's `pl` to equal the
  referenced repository field **exactly**.

The tracked authoring context already stated the same rule in prose, and Phase 4A's closing
section named both gaps in advance: converting the review into events "requires a named
native-linguistic reviewer authority, which does not yet exist, and applying any accepted
example still requires a named example-authoring authority, which also does not yet exist."

Phase 4C closed the first of those two. It could not close the second, and it discovered that
closing the first is not sufficient on its own.

## 6. Highest legitimate review state — and why it is still `research`

Native acceptance by AB legitimately establishes **native linguistic review**. It does not
establish external/source verification, and the schema requires that as a separate, earlier
stage performed by a different competent human.

The project does not possess such a human. Phase 2B's source work was AI-performed and its own
audit says so explicitly: it "is *not* the `external-verification` review gate, which requires a
named human," and the Phase 1 specification states that AI agreement is never a review event.

The consequence is stronger than "the state cannot advance": **the review event cannot even be
recorded.** A `native-linguistic` acceptance is rejected by the validator regardless of what
`reviewState` is written alongside it. This was proven by running the real validator against
in-memory candidate documents:

| Attempted transition | Validator result |
|---|---|
| `native-linguistic` accept, `reviewState` left truthfully at `research` | `REVIEW_STAGE_ORDER` |
| `native-linguistic` accept, `reviewState` set to `native-reviewed` | `REVIEW_STAGE_ORDER` + `REVIEW_STATE_MISMATCH` |
| **Case B** — AB keeps the real `native-linguistic`-only role but is used as external verifier as well | `REVIEWER_ROLE` + `REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` |
| **Case A** — AB *granted* both roles and used for both stages | `REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` **only** |
| An AI identity registered as the external verifier | `REVIEWER_NOT_HUMAN` |
| AB added to `reviewerRegistry`, zero review events | **valid — 0 issues** |

Cases A and B are worth separating, because the difference shows the gap is not a registry
typo. Granting AB the extra role clears `REVIEWER_ROLE` and leaves
`REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` standing: one human spanning two stages needs an explicit
owner allowance, and that allowance would still not make AB someone who actually performed
external verification. The remaining error is precisely the one that cannot be cleared by
editing a field.

Only the last row is legitimate, so only the last row was applied. Manufacturing an earlier
stage to reach `native-reviewed` was available and was refused: a clean NO-GO on state
advancement is preferable to fake provenance. **All 45 patterns remain `research`. Zero review
events exist. 0 of 45 reached `native-reviewed`.**

## 7. Exact 45-row mapping

45 unique Review IDs, exactly `P7-NR-001` … `P7-NR-045`; 12 priority, 5 example, 28
confirmation; zero omissions, zero duplicates. Every mapped lemma, meaning, pattern and example
ID resolves in the real corpus, every pattern is owned by its mapped lemma and meaning, and the
45 pattern IDs are a **bijection onto the 45 real corpus patterns** — no pattern received two
decisions and none was skipped. No `P7-NR-` identifier was written into canonical data.

| Review ID | Group | Canonical pattern ID | Human decision | Canonical example / draft ref | Applied outcome |
|---|---|---|---|---|---|
| P7-NR-001 | confirmation | `vp-p-szukac-seek-genitive-target-71dc6eff512c` | `looks-good` | `vp-e-szukac-seek-genitive-target-looking-for-cafe-efdccf7a5ba6` | preserved as presented; state stays `research` |
| P7-NR-002 | priority | `vp-p-pomagac-assist-dative-recipient-9f0a375c5e81` | `accepted-as-presented` | B-01 (draft) | preserved as presented; state stays `research` |
| P7-NR-003 | confirmation | `vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869` | `looks-good` | B-02 (draft) | preserved as presented; state stays `research` |
| P7-NR-004 | confirmation | `vp-p-sluchac-listen-to-genitive-target-a274f84c8d93` | `looks-good` | `vp-e-sluchac-listen-to-genitive-target-music-on-the-way-ecf258289d6e` | preserved as presented; state stays `research` |
| P7-NR-005 | priority | `vp-p-sluchac-obey-genitive-object-674adae2dec3` | `accepted-as-presented` | B-03 (draft) | preserved as presented; state stays `research` |
| P7-NR-006 | confirmation | `vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde` | `looks-good` | `vp-e-czekac-wait-for-na-accusative-target-waiting-for-bus-c7204269b040` | preserved as presented; state stays `research` |
| P7-NR-007 | confirmation | `vp-p-potrzebowac-need-genitive-object-437fafad17d2` | `looks-good` | `vp-e-potrzebowac-need-genitive-object-certificate-from-work-9bb3306bf0ee` | preserved as presented; state stays `research` |
| P7-NR-008 | confirmation | `vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7` | `looks-good` | `vp-e-uczyc-sie-study-genitive-subject-matter-polish-for-a-year-180cd560a0ec` | preserved as presented; state stays `research` |
| P7-NR-009 | priority | `vp-p-uczyc-sie-study-infinitive-skill-ab708776387e` | `accepted-as-presented` | `vp-e-uczyc-sie-study-infinitive-skill-learning-guitar-fc75e418733b` | preserved as presented; state stays `research` |
| P7-NR-010 | confirmation | `vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad` | `looks-good` | `vp-e-dziekowac-thank-za-accusative-reason-thanks-for-help-edd6c7bb9169` | preserved as presented; state stays `research` |
| P7-NR-011 | example | `vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f` | `replacement-accepted-as-presented` | `vp-e-dziekowac-thank-dative-recipient-za-accusative-thanks-for-cooperation-92656ebcc371` | replacement NOT applied — authorship blocker |
| P7-NR-012 | example | `vp-p-placic-pay-za-accusative-goods-73c6760c091d` | `replacement-accepted-as-presented` | `vp-e-placic-pay-za-accusative-goods-how-much-for-everything-dd5e5c88cfd4` | replacement NOT applied — authorship blocker |
| P7-NR-013 | confirmation | `vp-p-placic-pay-instrumental-method-ef4313d0d5ce` | `looks-good` | `vp-e-placic-pay-instrumental-method-paying-cash-e1eba53e074b` | preserved as presented; state stays `research` |
| P7-NR-014 | confirmation | `vp-p-uzywac-use-genitive-object-2c5cb44fe85d` | `looks-good` | `vp-e-uzywac-use-genitive-object-using-an-app-4ea0e75b504a` | preserved as presented; state stays `research` |
| P7-NR-015 | confirmation | `vp-p-prosic-request-o-accusative-request-06d776fbfd20` | `looks-good` | `vp-e-prosic-request-o-accusative-request-passport-please-37568555b13c` | preserved as presented; state stays `research` |
| P7-NR-016 | priority | `vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99` | `accepted-as-presented` | B-04 (draft) | preserved as presented; state stays `research` |
| P7-NR-017 | confirmation | `vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01` | `looks-good` | `vp-e-interesowac-sie-be-interested-in-instrumental-topic-politics-and-sport-9678fabc81e9` | preserved as presented; state stays `research` |
| P7-NR-018 | confirmation | `vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c` | `looks-good` | `vp-e-dbac-take-care-of-o-accusative-target-care-every-day-171833c3174d` | preserved as presented; state stays `research` |
| P7-NR-019 | priority | `vp-p-tesknic-miss-za-instrumental-target-f866502502c7` | `accepted-as-presented` | `vp-e-tesknic-miss-za-instrumental-target-missing-you-b98f2f56ea9f` | preserved as presented; state stays `research` |
| P7-NR-020 | confirmation | `vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca` | `looks-good` | B-05 (draft) | preserved as presented; state stays `research` |
| P7-NR-021 | confirmation | `vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05` | `looks-good` | B-06 (draft) | preserved as presented; state stays `research` |
| P7-NR-022 | confirmation | `vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98` | `looks-good` | B-07 (draft) | preserved as presented; state stays `research` |
| P7-NR-023 | priority | `vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144` | `accepted-as-presented` | `vp-e-bac-sie-be-afraid-of-genitive-stimulus-spiders-and-flying-05ebb1adaeeb` | preserved as presented; state stays `research` |
| P7-NR-024 | confirmation | `vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b` | `looks-good` | B-08 (draft) | preserved as presented; state stays `research` |
| P7-NR-025 | confirmation | `vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30` | `looks-good` | `vp-e-byc-predicate-role-instrumental-predicate-first-year-student-181cc5a0b335` | preserved as presented; state stays `research` |
| P7-NR-026 | confirmation | `vp-p-znac-be-acquainted-with-accusative-object-379e19b36299` | `looks-good` | `vp-e-znac-be-acquainted-with-accusative-object-know-this-restaurant-966b2c8de5a3` | preserved as presented; state stays `research` |
| P7-NR-027 | confirmation | `vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f` | `looks-good` | `vp-e-lubic-enjoy-thing-or-activity-accusative-object-polish-food-857835bb5b81` | preserved as presented; state stays `research` |
| P7-NR-028 | confirmation | `vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45` | `looks-good` | `vp-e-lubic-enjoy-thing-or-activity-infinitive-activity-reading-before-sleep-d573db6f04d1` | preserved as presented; state stays `research` |
| P7-NR-029 | priority | `vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960` | `accepted-as-presented` | B-09 (draft) | preserved as presented; state stays `research` |
| P7-NR-030 | confirmation | `vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736` | `looks-good` | B-10 (draft) | preserved as presented; state stays `research` |
| P7-NR-031 | confirmation | `vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8` | `looks-good` | B-11 (draft) | preserved as presented; state stays `research` |
| P7-NR-032 | confirmation | `vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a` | `looks-good` | B-12 (draft) | preserved as presented; state stays `research` |
| P7-NR-033 | example | `vp-p-widziec-perceive-visually-accusative-object-80b697e51432` | `replacement-accepted-as-presented` | `vp-e-widziec-perceive-visually-accusative-object-saw-your-sister-ec51af47f224` | replacement NOT applied — authorship blocker |
| P7-NR-034 | confirmation | `vp-p-miec-possess-accusative-object-7181f802bd57` | `looks-good` | `vp-e-miec-possess-accusative-object-two-cats-and-a-dog-2ce2746c0cfc` | preserved as presented; state stays `research` |
| P7-NR-035 | confirmation | `vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2` | `looks-good` | B-22 (draft) | preserved as presented; state stays `research` |
| P7-NR-036 | priority | `vp-p-znalezc-find-accusative-object-d80c52211462` | `accepted-as-presented` | `vp-e-znalezc-find-accusative-object-finally-found-a-flat-3609f7a71e3f` | preserved as presented; state stays `research` |
| P7-NR-037 | priority | `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9` | `accepted-as-presented` | B-13 (draft) | preserved as presented; state stays `research` |
| P7-NR-038 | confirmation | `vp-p-ufac-trust-dative-object-10988adac8cd` | `looks-good` | B-14 (draft) | preserved as presented; state stays `research` |
| P7-NR-039 | priority | `vp-p-wierzyc-have-trust-dative-object-f38bb3e72123` | `accepted-as-presented` | B-15 (draft) | preserved as presented; state stays `research` |
| P7-NR-040 | priority | `vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1` | `accepted-as-presented` | B-16 (draft) | preserved as presented; state stays `research` |
| P7-NR-041 | confirmation | `vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e` | `looks-good` | B-17 (draft) | preserved as presented; state stays `research` |
| P7-NR-042 | example | `vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` | `replacement-accepted-as-presented` | B-18 (draft) | replacement NOT applied — authorship blocker |
| P7-NR-043 | confirmation | `vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b` | `looks-good` | B-19 (draft) | preserved as presented; state stays `research` |
| P7-NR-044 | example | `vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318` | `replacement-accepted-as-presented` | B-20 (draft) | replacement NOT applied — authorship blocker |
| P7-NR-045 | priority | `vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc` | `accepted-as-presented` | B-21 (draft) | preserved as presented; state stays `research` |

## 8. The 40 non-example decisions (12 priority + 28 confirmation)

The human judgment was **accepted as presented**, not *rewritten by reviewer*. Accordingly:

- linguistic structure preserved exactly as presented — complement types, cases, prepositions,
  clause kinds, roles and `required` flags are untouched;
- meaning boundaries preserved — 34 meanings, unchanged glosses and internal scopes;
- complement structure preserved;
- CEFR and `teachingStatus` preserved exactly as already represented;
- no new wording, no structural change, no reinterpretation.

Human acceptance could not be recorded through the review machinery, because that machinery
refuses the event (§6). It is recorded instead in the reviewer registry and in this report,
which is the only truthful place available.

## 9. The five accepted replacement examples — authorship gate

The five sentences AB accepted as presented:

| Review ID | Accepted replacement | Slot before review |
|---|---|---|
| `P7-NR-011` | `Dziękuję siostrze za kolację.` | `repository-reuse` example, `Dziękuję wszystkim za owocną współpracę.` |
| `P7-NR-012` | `Płacę za kawę i gazetę.` | `repository-reuse` example, `Ile płacę za wszystko?` |
| `P7-NR-033` | `Czy widzisz tę górę na horyzoncie?` | `repository-reuse` example, `Widziałam wczoraj twoją siostrę.` |
| `P7-NR-042` | `Kiedy siostra jest w pracy, zajmuję się jej córką.` | no canonical example (draft `B-18`) |
| `P7-NR-044` | `Nasze plany zależą od pogody.` | no canonical example (draft `B-20`) |

All five originated as `ai-draft-noncanonical`, `humanAuthored: false`. AB's acceptance
establishes **human linguistic acceptance of the proposed text**. It does not establish that AB
wrote it.

**Outcome B applies.** The canonical schema requires valid human authorship before the
replacement can be stored, and no human author exists. Proven against the real validator:

| Attempt | Validator result |
|---|---|
| Accepted text, origin left as `repository-reuse` | `REPOSITORY_SOURCE_MISMATCH` — the sentence is not the repository sentence |
| Accepted text, `origin.kind = "original"`, no author fields | `SCHEMA_REQUIRED` on `authorRef` and `authoredAt` |
| `origin.kind = "original"` with an unregistered `authorRef` | `AUTHOR_REGISTRY_DANGLING` |
| `origin.kind = "original"` with a registered non-human author | `AUTHOR_NOT_HUMAN` |

Therefore the five replacements were **not applied**. They remain human-accepted but pending
author adoption, recorded in the external validated ledger as `inCanonicalCorpus: false`.

No author was fabricated. AB was not recorded as author. Kaj / the project owner / product owner
/ founder was not recorded as author — project ownership is not authorship evidence. The
`authorRegistry` remains empty, which is the truthful state.

Nothing was half-applied: the three existing sentences are still byte-identical, and the two
empty slots gained no example.

## 10. Example IDs

No ID policy was invented and none was needed. The stable-ID specification permits example
wording change under the same identity ("Learner explanation, gloss wording, example wording,
usage note — same identity; frozen wording/policy approval still required"), and the real corpus
has never been frozen or released, so post-release retire/tombstone restrictions do not apply
yet. Since no wording was legitimately applied, **no example ID was created, changed, retired or
tombstoned.**

## 11. Review digests and evidence

No review event could be legitimately recorded, so no review-scope digest was written into
canonical data. No digest was hand-written anywhere. The digest machinery
(`review_scope_digest`, `evidence_digest`) was used only to construct the sandbox probes in §6
and §9 that prove the refusals, and in the Phase 4C tests.

Evidence is untouched: all **122** evidence records across the 45 patterns are unchanged, no
evidence record was edited, added, removed or reordered, and no evidence digest was repinned.
No Mędak/WSJP/source conclusion was reinterpreted. No new outside research was performed.

## 12. Learner-facing treatment, eligibility, freeze, runtime

Blanket acceptance means the reviewer did not flag the existing learner-facing treatment, so the
current proposed status/treatment is preserved unchanged. That was **not** translated into
activity eligibility, active exercises or runtime publication.

- `activityEligibility` — empty on all 45 patterns (0 entries total).
- `audioEligible` — `false` on all 23 canonical examples.
- No exercise IDs; no `vp-x-` identifier; no `exerciseId` key.
- No product approval. No `approved` state. No product-approval event. AB was not used as a
  product approver. At final state **no real pattern is release-authorized.**
- No freeze. No real allocations, tombstones, frozen snapshots or `patternDataRevision`.
- No public runtime. `content/verb-patterns.json` does not exist; `content/` does not exist.
  The Phase 3F-A loader was not activated.
- No shipping change. `index.html`, `pp-verb-patterns.js`, `sw.js`, `manifest.json`,
  `APP_VERSION = "8.10"`, service-worker cache `popolsku-v65`, audio cache, `schemaVersion`,
  `CONTENT_MIGRATION_REVISION` and generated pages are all untouched.

## 13. Canonical diff summary

**`editorial/verb-pattern-candidates.json` — byte-identical to HEAD.**
Worktree blob `f3b8d2d704699125aecf8858eca01e0c6ec84c26`; HEAD blob
`f3b8d2d704699125aecf8858eca01e0c6ec84c26`; SHA-256
`b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f` — the same digest Phase 4B
recorded.

| Diff category | Change |
|---|---|
| Reviewer registry additions | **1** — `native-reviewer-001` (`AB`), role `native-linguistic` only |
| Review events added | **0** — blocked by the missing external-verification stage |
| Review states changed | **0** — all 45 remain `research` |
| Five example wording changes | **0** — blocked by the missing human author |
| Example provenance changes | **0** — all 23 examples remain `repository-reuse` |
| Evidence | unchanged — 122 records, no edit, no repin |
| Structures | unchanged — 45 patterns, complements untouched |
| Meanings | unchanged — 34 meanings, boundaries untouched |
| Lemmas / examples | unchanged — 30 lemmas, 23 examples |
| Activity eligibility | unchanged — empty everywhere |
| Author registry | unchanged — empty |
| Allocation registry | unchanged — empty |

The only canonical-side change in the entire phase is the reviewer registry entry plus the
context notice that describes it. There is no unexpected structural, meaning or evidence change.

## 14. Files touched

| Path | Change |
|---|---|
| `editorial/priority-7-authoring-context.json` | reviewer registry entry for `native-reviewer-001`; `contextNotice` updated to state the new truthful position |
| `tests/test_priority7_phase4c.py` | **new** — 53 Phase 4C governance tests |
| `tests/test_priority7_phase3d1.py` | two assertions narrowed (see below) |
| `tests/test_priority7_phase3fa.py` | one assertion narrowed |
| `tests/test_priority7_phase5a.py` | assertions narrowed; commit-dependent context test replaced by three durable ones |
| `reports/priority-7-phase-4c-summary.md` | **new** — this report |

The repair pass stayed inside these same six paths. No new file was created and no file outside
the candidate scope was touched.

`editorial/priority-7-authoring-context.json` is the file the current schema legitimately uses to
store reviewer registries; `ValidationContext` takes the registries as explicit private inputs
and never as fields of the corpus document, so naming a reviewer necessarily touches this file
and not the corpus. No shipping file was modified.

### Prior-phase assertions that Phase 4C truthfully supersedes

Four earlier assertions pinned "no reviewer identity exists". That was true when written and is
now false, because a real human reviewer exists. Each was narrowed rather than deleted, and each
became **stricter** about what remains forbidden:

| Test | Before | After |
|---|---|---|
| `phase3d1::…identity_was_created…` | both registries `{}` | `authorRegistry` still `{}`; reviewer registry pinned to exactly `native-reviewer-001` with role `native-linguistic` |
| `phase3d1::…3d2_prerequisites…` | reviewer registry `{}` | `authorRegistry` `{}` **and** zero review events across the corpus |
| `phase3fa::…` | both registries `{}` | reviewer set + role pinned exactly; `authorRegistry` still `{}` |
| `phase5a::…registries_stay_empty…` | both `{}` "until human review exists" | human review now exists; `authorRegistry` still `{}`, reviewer role pinned, `ownerAllowsMultipleRoles` asserted absent |
| `phase5a::…byte_identical_to_head` | both editorial files byte-identical | corpus assertion **unchanged and still enforced**; context file covered by durable semantic tests instead |
| `phase5a::…touched_no_shipping_file` | only `tests/`+`reports/` | plus the one authoring-context path; corpus and every shipping file still forbidden |

## 15. Tests

New suite `tests/test_priority7_phase4c.py` — **53 tests**, covering:

- **Ledger coverage (6)** — exactly `P7-NR-001..045`; 12/5/28 partition; per-group decision;
  every mapped canonical ID resolves and is correctly owned; bijection onto the 45 real
  patterns; no `P7-NR-` leak into canonical data. The mapping is read from the tracked Phase 4B
  report rather than restated, so the test also proves the tracked mapping still agrees with the
  corpus. Coverage is verified at ID level, not by a hard-coded count of 45.
- **Duplicate-row rejection (5)** — the real 45-row source parses; a duplicated Review ID raises
  `DuplicateReviewIdError`; the duplicate is reported *as* a duplicate rather than as a count
  mismatch; the mutation is shown to be invisible to a naive keyed mapping; a short mapping is
  rejected by the row-count guard. Added in response to review — see §20.
- **Reviewer record (6)** — AB is human, native, `native-linguistic` only; not multi-role; no
  invented credential; no contact/owner identity; ledger referenced by digest not embedded;
  no author identity exists.
- **`native-reviewed` is blocked (5)** — bare native acceptance rejected even at `research`;
  claiming `native-reviewed` rejected twice over; case B (AB used externally while holding only
  the native role) and case A (AB granted both roles) asserted separately with their distinct
  error codes; an AI identity can never stand in.
- **Authorship is blocked (7)** — repository-reuse mismatch; missing author; dangling author;
  non-human author; AB not recorded as author; none of the five sentences in the corpus; the
  three existing sentences and two empty slots intact.
- **Truthful lower state pinned (8)** — corpus validates; 45 patterns `research`; zero events;
  nothing approved; eligibility empty; no audio-eligible example; no exercise identity;
  treatment preserved.
- **Corpus unchanged (4)** — byte digest equals the Phase 4B digest; 30/34/45/23 shape; 122
  evidence records; no registry key bolted onto the corpus.
- **No freeze / runtime / shipping change (6)** — no public runtime; no freeze artifact; no
  allocation or revision; `APP_VERSION = "8.10"` and `popolsku-v65` intact; nonproduction
  markers; private keys excluded from runtime projection.
- **Outstanding blockers (4)** — no external-verification authority; no product-approval
  authority; no example-authoring authority; the stage order is still the one reasoned about.

The five accepted sentences are tested by exact wording, as required — asserted **absent** from
canonical data, since Outcome B applied.

## 16. Full validation after implementation

All totals below are **post-repair** (see §20).

| Check | Baseline | Final |
|---|---|---|
| Phase 4C targeted tests | — | **53 passed** |
| Phase 2A governance tests | 77 | **77 passed** |
| Phase 3B | 19 | **19 passed** |
| Phase 3C | 22 | **22 passed** |
| Phase 3D-1 | 44 | **44 passed** |
| Phase 3F-A | 17 | **17 passed** |
| Phase 5-A | 95 | **98 passed** (+3 durable governance-boundary tests) |
| **Full Python** | **449 passed** | **505 passed, 0 failed** (+56) |
| **Full JXA** | **36 suites / 10,544 assertions / 0 failed** | **36 suites / 10,544 assertions / 0 failed** (unchanged) |
| `validate_content.py` | OK | **OK**, forward baseline `2a71401d…1ce50` unchanged |
| `verify_audio.py` | OK | **OK** — 3377 / 3377 / 3377, nothing orphaned |
| `build_pages.py --check` | current | **current** — 23 grammar + 6 vocabulary + hub, 32 URLs |
| `validate-editorial` | valid | **`Priority 7 private editorial record: valid`** |
| `git diff --check` | clean | **clean** |

## 17. Remaining governance blockers before product approval / freeze

| # | Blocker | Consequence | What would clear it |
|---|---|---|---|
| **1** | **No external-verification authority exists.** No competent human researcher has been named to verify the claims against contemporary references. | The entire corpus is pinned at `research`. AB's green native review cannot be recorded as a review event at all. 0 of 45 patterns reached `native-reviewed`. | A named human with the `external-verification` role performing and recording that stage per pattern, pinning contemporary evidence digests. AB must not be used for this unless AB actually did the work and the owner explicitly allows multiple roles. |
| **2** | **No example-authoring authority exists.** | The five accepted replacement sentences cannot enter the corpus. Two patterns still have no example at all. | A named human author adopting authorship of the sentences, registered in `authorRegistry` with `human: true`. |
| **3** | **Product approval intentionally pending.** | No pattern is release-authorized; no freeze, no runtime, no activity eligibility. | A named product owner, after blockers 1 and 2 clear and native review is recorded. |

Blocker 1 is the binding one: it gates blocker 3, and it is why an entirely green native review
produced no state advancement. None of this is hidden behind the fact that all Polish review was
green — the linguistic verdict was green, and the provenance chain is what is missing.

## 17a. Independent review, initial NO-GO, and the repairs it forced

The first Phase 4C candidate was reviewed independently by Codex, which returned **NO-GO**. The
substantive governance conclusion was confirmed correct — classification B, native review
genuine but blocked on the missing prior external-verification event, and the five replacements
correctly blocked because acceptance is not authorship — but three defects were found in how
that conclusion was *proven and recorded*. All three were real. None of them was in the
governance reasoning; all three were in the evidence supporting it, which is exactly the kind of
defect that makes a correct conclusion untrustworthy.

The initial implementation was not clean, and this section records that rather than presenting
the repaired state as the original one.

### Defect 1 — a permanent test that did not survive commit

`tests/test_priority7_phase5a.py` compared the authoring context against
`git show HEAD:editorial/priority-7-authoring-context.json` and asserted that HEAD's
`reviewerRegistry` was empty. That holds only while Phase 4C is uncommitted. Once the candidate
is committed, HEAD legitimately contains AB and the assertion inverts — a permanent test whose
result depended on whether the phase had been committed yet.

Reproduced concretely in the scratch repository: after committing the candidate,
HEAD's `reviewerRegistry` is `['native-reviewer-001']`, so the old assertion evaluates to
**FAIL**.

**Repair.** The commit-dependent test was replaced with three durable ones that assert the
truthful post-Phase-4C governance boundary directly, with no reference to HEAD:

- `test_real_authoring_context_holds_exactly_the_phase_4c_boundary` — exactly one reviewer,
  `native-reviewer-001` / `AB` / human / `Native Polish speaker` / `native-linguistic` only, no
  `ownerAllowsMultipleRoles`; no external-verification holder; no product-approval holder;
  `authorRegistry` empty; `allocationRegistry` empty; the four 2B source registry entries intact;
- `test_no_synthetic_phase_5a_identity_leaked_into_the_real_context` — no `test-` prefixed
  Phase 5-A fixture identity reached real editorial data;
- `test_no_real_state_advancement_accompanied_the_reviewer_record` — 45 patterns, all
  `research`, zero review events: a reviewer identity is not a review event.

**Corpus isolation was not weakened.** `test_real_corpus_is_byte_identical_to_head` still
compares `editorial/verb-pattern-candidates.json` against HEAD and stays strict. That comparison
is commit-safe precisely because Phase 4C changed none of the corpus, so it holds identically
before and after any commit.

### Defect 2 — duplicate mapping rows were silently swallowed

The Phase 4B mapping parser wrote `rows[review_id] = …` *before* testing uniqueness. A repeated
Review ID therefore overwrote the row parsed before it, and the resulting mapping still had 45
unique keys. Codex injected a second `P7-NR-001` row and **all six coverage tests still
passed**, while one real decision had been dropped — so the suite did not actually prove the
duplicate-rejection property it claimed.

**Repair.** Parsing was split so that uniqueness is enforced before any keying:

- `parse_mapping_rows(text)` returns an *ordered list*, preserving duplicates;
- `build_mapping(text, expected_row_count=None)` counts occurrences across that list and raises
  `DuplicateReviewIdError` on any repeat. The duplicate check runs **before** the row-count
  guard, so a duplicated row is reported as a duplicate rather than masked as a count mismatch;
- only then is the Review-ID-keyed mapping constructed, with a redundant post-check.

A reusable explicit-rejection helper was preferred over a bare test-method assertion, so every
caller inherits the guarantee.

**Mutation proof.** Repeating Codex's exact mutation against the repaired validation:

| Step | Result |
|---|---|
| Raw rows parsed from the mutated source | **46** |
| Naive keyed mapping (the old behaviour) | **45** — the extra row is invisible |
| `build_mapping` on the mutated source | **`DuplicateReviewIdError: duplicate Review ID(s) in the mapping source: ['P7-NR-001']`** |
| `build_mapping` on the real 45-row source | **succeeds**, exactly `P7-NR-001..045` |

The external validated ledger and the tracked Phase 4B report were not modified; the mutation is
applied to scratch text inside the test.

### Defect 3 — the report stated the wrong error combination

§6 described the multi-role row as "AB given the `external-verification` role too" while listing
the error codes for the *other* case. Codex independently reproduced the validator and was
right. The two cases are genuinely different:

| Case | Setup | Validator result |
|---|---|---|
| **A** | AB *granted* both `native-linguistic` and `external-verification`, used for both stages | `REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` **only** |
| **B** | AB holds `native-linguistic` only, used as external verifier as well | `REVIEWER_ROLE` + `REVIEWER_MULTI_ROLE_NOT_AUTHORIZED` |

The §6 table now states both cases correctly, and the suite asserts each with `assertEqual` on
the exact code set rather than `assertIn`, so a future drift in either direction fails. The
governance interpretation is unchanged: neither case opens a legitimate path, and case A is the
sharper illustration — granting the role clears `REVIEWER_ROLE` and leaves the multi-role error
standing, which is the error that cannot be cleared by editing a registry field.

### Commit-survivability verification

Performed in a scratch copy only. The real Phase 4C repository remains uncommitted.

| Item | Result |
|---|---|
| Scratch commit hash | `8c650ccebb9906bb22fb5dfd5a1b16b5f665f7bc` |
| Scratch worktree after commit | **clean** — `git status --short --untracked-files=all` empty |
| Paths in the scratch commit | exactly the six candidate paths |
| `editorial/verb-pattern-candidates.json` in the commit diff | **absent** — corpus untouched |
| `tests/test_priority7_phase4c.py` from committed HEAD | **53 passed** |
| `tests/test_priority7_phase5a.py` from committed HEAD | **98 passed** |
| `tests/test_priority7_phase3fa.py` from committed HEAD | **17 passed** |
| `tests/test_priority7_phase2a.py` from committed HEAD | **77 passed** |
| **Full Python suite from committed HEAD** | **505 passed, 0 failed** |

The candidate is green both uncommitted and from a clean committed HEAD, which is the property
Defect 1 had broken.

## 18. Final boundary proof

| Requirement | Status |
|---|---|
| Human review ledger mapped 45/45 | **yes** — ID-level, bijective onto the 45 real patterns |
| Only legitimate canonical review changes applied | **yes** — one reviewer registry entry, nothing else |
| No invented human comments | **yes** — zero notes, zero comments written anywhere |
| No invented reviewer role | **yes** — `native-linguistic` only |
| No invented author | **yes** — `authorRegistry` empty |
| No invented external verifier | **yes** — none named; the gap is reported instead |
| No product approval | **yes** — no `approved` state, no product-approval event |
| No real freeze | **yes** |
| No real revision | **yes** — no `patternDataRevision` |
| No real runtime | **yes** |
| No `content/verb-patterns.json` | **yes** — `content/` does not exist |
| Activity eligibility remains empty | **yes** — 0 entries across 45 patterns |
| No exercises enabled | **yes** — no `exerciseId`, no `vp-x-` |
| No SW / index / version / cache changes | **yes** — `APP_VERSION = "8.10"`, `popolsku-v65` |
| Production untouched | **yes** |
| Zero remotes | **yes** |
| No commit | **yes** — HEAD still `66f9d68871a0862bcbe8bd04804fb3fc3ca4131c` |
| No push | **yes** — zero remotes, `push.default=nothing` |

Ending `git status --porcelain`:

```text
 M editorial/priority-7-authoring-context.json
 M tests/test_priority7_phase3d1.py
 M tests/test_priority7_phase3fa.py
 M tests/test_priority7_phase5a.py
?? tests/test_priority7_phase4c.py
?? reports/priority-7-phase-4c-summary.md
```

## 19. Verdict

**GO WITH GOVERNANCE BLOCKER.**

Human review was applied as far as legitimately possible. The real human native reviewer is now
named in the canonical governance record with native-linguistic authority and nothing more, all
45 decisions are mapped and accounted for, and the corpus is preserved exactly as the reviewer
accepted it.

Two explicit governance dependencies remain before product approval or freeze: the absent
external-verification identity/event, and unresolved authorship for the accepted AI-draft
examples. Neither was bypassed and neither was fabricated. This is not a failure — it is the
fail-closed contract working as designed.

The first candidate was correctly returned NO-GO by independent review. The governance
conclusion survived that review unchanged; three defects in the supporting evidence — a
permanent test that did not survive commit, a duplicate-row check that could be silently
defeated, and a wrong error-code pairing in this report — were repaired and are recorded in
§17a with their reproductions and proofs. Commit-survivability now passes, and the duplicate
mutation is rejected.

Do not begin Governance Closure. Do not start product approval. Do not freeze. Do not publish
runtime.
