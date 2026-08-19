# Priority 7 — Phase 4B Human Review Ingestion

**Verdict: GO**

This phase validates and ingests the external human-review outcome. It does not perform a new
linguistic review, edit canonical data, advance canonical review state, freeze data, or start
Phase 4C.

## 1. Repository baseline and scope

| Check | Observed |
|---|---|
| Working directory | `/Users/Kaj/Downloads/Repository for Codex - Priority 7 Phase 4B` |
| Branch | `priority-7-phase-4b-human-review-ingest` |
| HEAD | `5ed1826992f4ec9f17c1d548b3aa903c2efa7963` |
| HEAD tree | `4e7d783b6387b8fe5c929313bfa0084548bd7b96` |
| Git remotes | zero |
| `push.default` | `nothing` |
| Starting worktree | clean |
| Ending Git status | exactly `?? reports/priority-7-phase-4b-summary.md` |
| Commit | none; HEAD unchanged |
| Push | none; zero remotes |

No repository file other than this untracked report was created or modified.

## 2. Human-review source and integrity

Source directory, outside Git:
`/Users/Kaj/Downloads/Priority_7_Phase_4B_Human_Attestation`.

`SHA256.txt` was verified with `shasum -a 256 -c`; both listed files passed:

| Source | SHA-256 |
|---|---|
| `review-attestation.json` | `1e97a63dea0bce20f5a86b74d364ae641947299f9bd4f3df7342cadc15e9b6a8` |
| `decision-ledger.json` | `f0dcf46f5da950baa06003fa4a7a82f342d75a82098b6414388c8edfadbac961` |

The attestation's Phase 4A source hashes were also matched to the files in
`/Users/Kaj/Downloads/Priority_7_Phase_4A_Reviewer_Package`:

- workbook: `69ed564026954021c5908e86c0c06023409fa058e8f7b869621d2f1920e63d7e`;
- `human-priority.csv`: `7b9cdb55f13de6c45af86f207094ecc1e975d5bbceb5a6e4380a28dcd9f60587`;
- `example-replacements.csv`: `6009a328d3a38911822cd6f246b53c1e43befd5640c489f12b14eda01bfbfb5b`;
- `low-risk-confirmation.csv`: `99ad48e80951d252cd3dd6bd0590ecfd07b48cfd11c40d43058c0f324839628a`.

## 3. Reviewer record

| Field | Recorded value |
|---|---|
| Stable reviewer ID | `native-reviewer-001` |
| Display initials | `AB` |
| Native Polish speaker | `true` |
| Background | `Native Polish speaker` |
| Review date | `2026-08-13` |
| Teaching qualification | not recorded; none inferred |

The record contains a real human reviewer identifier and privacy-safe initials. The background
is reproduced without embellishment. This external attestation does not modify the empty
canonical `reviewerRegistry`.

## 4. Coverage and exact interpretation

The attestation and decision ledger contain identical row arrays. Mechanical validation proves
45 unique IDs, exactly `P7-NR-001` through `P7-NR-045`, partitioned with no overlap or omission:

| Group | Count | Recorded human outcome |
|---|---:|---|
| Priority | 12 | `accepted-as-presented` |
| Example replacement | 5 | `replacement-accepted-as-presented` |
| Confirmation | 28 | `looks-good` |
| **Total** | **45** | **45/45 covered** |

Across all 45 rows there are zero flags, edits, rejections, unresolved rows, specific-feedback
entries, or reviewer comments.

The governance interpretation is row-level acceptance of the Phase 4A package as presented.
It preserves the package's existing provisional structure, meaning, CEFR/teaching treatment,
and presentation; it does not silently create or alter a dimension-level linguistic answer.
The Phase 4A response fields remained blank, so this phase does **not** manufacture
`Natural = Yes`, `Structure = Yes`, any learner-facing treatment selection, suggested wording,
or additional comments. Those values remain unavailable/null in the validated ledger.

## 5. Example replacements

For the five example rows, blanket acceptance applies to the exact proposed Phase 2C.2 sentence
shown in the Phase 4A package:

| Review ID | Human-accepted proposed replacement |
|---|---|
| `P7-NR-011` | `Dziękuję siostrze za kolację.` |
| `P7-NR-012` | `Płacę za kawę i gazetę.` |
| `P7-NR-033` | `Czy widzisz tę górę na horyzoncie?` |
| `P7-NR-042` | `Kiedy siostra jest w pracy, zajmuję się jej córką.` |
| `P7-NR-044` | `Nasze plany zależą od pogody.` |

The sentences were matched byte-for-byte to `manifest.json` and
`example-replacements.csv`. They are now human-accepted as presented, but remain noncanonical;
none was inserted into `editorial/verb-pattern-candidates.json`. Phase 4C owns any canonical
example change and authorship/provenance treatment.

## 6. Exact Review ID to canonical mapping

Every Review ID resolves to exactly one of the 45 real canonical patterns. Canonical example IDs
are shown only where an example currently exists in the corpus. `B-*` values are preserved Phase
2B draft references, explicitly noncanonical; they are not presented as canonical example IDs.

| Review ID | Group | Human decision | Lemma ID | Meaning ID | Pattern ID | Canonical example ID | Noncanonical draft ref |
|---|---|---|---|---|---|---|---|
| P7-NR-001 | confirmation | looks-good | `vp-l-szukac-0daf5e6b5693` | `vp-m-szukac-seek-35b07b1cceb1` | `vp-p-szukac-seek-genitive-target-71dc6eff512c` | `vp-e-szukac-seek-genitive-target-looking-for-cafe-efdccf7a5ba6` | — |
| P7-NR-002 | priority | accepted-as-presented | `vp-l-pomagac-54633912de9a` | `vp-m-pomagac-assist-a4c05bbfc25c` | `vp-p-pomagac-assist-dative-recipient-9f0a375c5e81` | — | `B-01` |
| P7-NR-003 | confirmation | looks-good | `vp-l-pomagac-54633912de9a` | `vp-m-pomagac-assist-a4c05bbfc25c` | `vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869` | — | `B-02` |
| P7-NR-004 | confirmation | looks-good | `vp-l-sluchac-301b09233922` | `vp-m-sluchac-listen-to-d981b432efa8` | `vp-p-sluchac-listen-to-genitive-target-a274f84c8d93` | `vp-e-sluchac-listen-to-genitive-target-music-on-the-way-ecf258289d6e` | — |
| P7-NR-005 | priority | accepted-as-presented | `vp-l-sluchac-301b09233922` | `vp-m-sluchac-obey-eb23d8503e9a` | `vp-p-sluchac-obey-genitive-object-674adae2dec3` | — | `B-03` |
| P7-NR-006 | confirmation | looks-good | `vp-l-czekac-c6c3d0da2caa` | `vp-m-czekac-wait-for-bfb4d11f9655` | `vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde` | `vp-e-czekac-wait-for-na-accusative-target-waiting-for-bus-c7204269b040` | — |
| P7-NR-007 | confirmation | looks-good | `vp-l-potrzebowac-8b78ee8b092d` | `vp-m-potrzebowac-need-1112b46d1be1` | `vp-p-potrzebowac-need-genitive-object-437fafad17d2` | `vp-e-potrzebowac-need-genitive-object-certificate-from-work-9bb3306bf0ee` | — |
| P7-NR-008 | confirmation | looks-good | `vp-l-uczyc-sie-a01d00cb7f2f` | `vp-m-uczyc-sie-study-bd96ff26cc60` | `vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7` | `vp-e-uczyc-sie-study-genitive-subject-matter-polish-for-a-year-180cd560a0ec` | — |
| P7-NR-009 | priority | accepted-as-presented | `vp-l-uczyc-sie-a01d00cb7f2f` | `vp-m-uczyc-sie-study-bd96ff26cc60` | `vp-p-uczyc-sie-study-infinitive-skill-ab708776387e` | `vp-e-uczyc-sie-study-infinitive-skill-learning-guitar-fc75e418733b` | — |
| P7-NR-010 | confirmation | looks-good | `vp-l-dziekowac-8e4ca359cb86` | `vp-m-dziekowac-thank-f19a15334790` | `vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad` | `vp-e-dziekowac-thank-za-accusative-reason-thanks-for-help-edd6c7bb9169` | — |
| P7-NR-011 | example | replacement-accepted-as-presented | `vp-l-dziekowac-8e4ca359cb86` | `vp-m-dziekowac-thank-f19a15334790` | `vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f` | `vp-e-dziekowac-thank-dative-recipient-za-accusative-thanks-for-cooperation-92656ebcc371` | — |
| P7-NR-012 | example | replacement-accepted-as-presented | `vp-l-placic-d709669437d2` | `vp-m-placic-pay-dd4705572184` | `vp-p-placic-pay-za-accusative-goods-73c6760c091d` | `vp-e-placic-pay-za-accusative-goods-how-much-for-everything-dd5e5c88cfd4` | — |
| P7-NR-013 | confirmation | looks-good | `vp-l-placic-d709669437d2` | `vp-m-placic-pay-dd4705572184` | `vp-p-placic-pay-instrumental-method-ef4313d0d5ce` | `vp-e-placic-pay-instrumental-method-paying-cash-e1eba53e074b` | — |
| P7-NR-014 | confirmation | looks-good | `vp-l-uzywac-a617dcf0b2fc` | `vp-m-uzywac-use-bf360f430fed` | `vp-p-uzywac-use-genitive-object-2c5cb44fe85d` | `vp-e-uzywac-use-genitive-object-using-an-app-4ea0e75b504a` | — |
| P7-NR-015 | confirmation | looks-good | `vp-l-prosic-82f143d28483` | `vp-m-prosic-request-12aaa8159096` | `vp-p-prosic-request-o-accusative-request-06d776fbfd20` | `vp-e-prosic-request-o-accusative-request-passport-please-37568555b13c` | — |
| P7-NR-016 | priority | accepted-as-presented | `vp-l-prosic-82f143d28483` | `vp-m-prosic-request-12aaa8159096` | `vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99` | — | `B-04` |
| P7-NR-017 | confirmation | looks-good | `vp-l-interesowac-sie-594d3cf1b5a6` | `vp-m-interesowac-sie-be-interested-in-7a9b8150975b` | `vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01` | `vp-e-interesowac-sie-be-interested-in-instrumental-topic-politics-and-sport-9678fabc81e9` | — |
| P7-NR-018 | confirmation | looks-good | `vp-l-dbac-15ed83f8434d` | `vp-m-dbac-take-care-of-2b403d3e1b49` | `vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c` | `vp-e-dbac-take-care-of-o-accusative-target-care-every-day-171833c3174d` | — |
| P7-NR-019 | priority | accepted-as-presented | `vp-l-tesknic-3c9b07c066c3` | `vp-m-tesknic-miss-d796ac98d4f5` | `vp-p-tesknic-miss-za-instrumental-target-f866502502c7` | `vp-e-tesknic-miss-za-instrumental-target-missing-you-b98f2f56ea9f` | — |
| P7-NR-020 | confirmation | looks-good | `vp-l-rozmawiac-dd7ecc80c231` | `vp-m-rozmawiac-talk-with-73fae3a5d72c` | `vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca` | — | `B-05` |
| P7-NR-021 | confirmation | looks-good | `vp-l-rozmawiac-dd7ecc80c231` | `vp-m-rozmawiac-talk-with-73fae3a5d72c` | `vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05` | — | `B-06` |
| P7-NR-022 | confirmation | looks-good | `vp-l-rozmawiac-dd7ecc80c231` | `vp-m-rozmawiac-talk-with-73fae3a5d72c` | `vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98` | — | `B-07` |
| P7-NR-023 | priority | accepted-as-presented | `vp-l-bac-sie-0fcafe1aef9f` | `vp-m-bac-sie-be-afraid-of-60cc08a05be5` | `vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144` | `vp-e-bac-sie-be-afraid-of-genitive-stimulus-spiders-and-flying-05ebb1adaeeb` | — |
| P7-NR-024 | confirmation | looks-good | `vp-l-bac-sie-0fcafe1aef9f` | `vp-m-bac-sie-worry-about-3a50faed54bf` | `vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b` | — | `B-08` |
| P7-NR-025 | confirmation | looks-good | `vp-l-byc-8deae1e7376a` | `vp-m-byc-predicate-role-93c209d5654b` | `vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30` | `vp-e-byc-predicate-role-instrumental-predicate-first-year-student-181cc5a0b335` | — |
| P7-NR-026 | confirmation | looks-good | `vp-l-znac-a4c921e7688c` | `vp-m-znac-be-acquainted-with-54b71d59f073` | `vp-p-znac-be-acquainted-with-accusative-object-379e19b36299` | `vp-e-znac-be-acquainted-with-accusative-object-know-this-restaurant-966b2c8de5a3` | — |
| P7-NR-027 | confirmation | looks-good | `vp-l-lubic-a9766b487203` | `vp-m-lubic-enjoy-thing-or-activity-fd56f32d6d55` | `vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f` | `vp-e-lubic-enjoy-thing-or-activity-accusative-object-polish-food-857835bb5b81` | — |
| P7-NR-028 | confirmation | looks-good | `vp-l-lubic-a9766b487203` | `vp-m-lubic-enjoy-thing-or-activity-fd56f32d6d55` | `vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45` | `vp-e-lubic-enjoy-thing-or-activity-infinitive-activity-reading-before-sleep-d573db6f04d1` | — |
| P7-NR-029 | priority | accepted-as-presented | `vp-l-mowic-5f4740bd3f57` | `vp-m-mowic-tell-content-15073cbb8666` | `vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960` | — | `B-09` |
| P7-NR-030 | confirmation | looks-good | `vp-l-mowic-5f4740bd3f57` | `vp-m-mowic-tell-content-15073cbb8666` | `vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736` | — | `B-10` |
| P7-NR-031 | confirmation | looks-good | `vp-l-pytac-0410b0f88718` | `vp-m-pytac-ask-for-information-edc2b66ff9d6` | `vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8` | — | `B-11` |
| P7-NR-032 | confirmation | looks-good | `vp-l-pytac-0410b0f88718` | `vp-m-pytac-ask-for-information-edc2b66ff9d6` | `vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a` | — | `B-12` |
| P7-NR-033 | example | replacement-accepted-as-presented | `vp-l-widziec-59dbe12f8b3d` | `vp-m-widziec-perceive-visually-65710cb07f86` | `vp-p-widziec-perceive-visually-accusative-object-80b697e51432` | `vp-e-widziec-perceive-visually-accusative-object-saw-your-sister-ec51af47f224` | — |
| P7-NR-034 | confirmation | looks-good | `vp-l-miec-3d78141ba164` | `vp-m-miec-possess-1ba1201b22bf` | `vp-p-miec-possess-accusative-object-7181f802bd57` | `vp-e-miec-possess-accusative-object-two-cats-and-a-dog-2ce2746c0cfc` | — |
| P7-NR-035 | confirmation | looks-good | `vp-l-myslec-8be636ebca9e` | `vp-m-myslec-think-about-fa2e0ab5d95a` | `vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2` | — | `B-22` |
| P7-NR-036 | priority | accepted-as-presented | `vp-l-znalezc-eec53e19f1a0` | `vp-m-znalezc-find-8a0f0f34b6e8` | `vp-p-znalezc-find-accusative-object-d80c52211462` | `vp-e-znalezc-find-accusative-object-finally-found-a-flat-3609f7a71e3f` | — |
| P7-NR-037 | priority | accepted-as-presented | `vp-l-podobac-sie-26084690c7ca` | `vp-m-podobac-sie-appeal-to-a74665181e3f` | `vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9` | — | `B-13` |
| P7-NR-038 | confirmation | looks-good | `vp-l-ufac-6a061471e40a` | `vp-m-ufac-trust-92b1bdb490f0` | `vp-p-ufac-trust-dative-object-10988adac8cd` | — | `B-14` |
| P7-NR-039 | priority | accepted-as-presented | `vp-l-wierzyc-171eb7790262` | `vp-m-wierzyc-have-trust-0a6cbf4eee17` | `vp-p-wierzyc-have-trust-dative-object-f38bb3e72123` | — | `B-15` |
| P7-NR-040 | priority | accepted-as-presented | `vp-l-wierzyc-171eb7790262` | `vp-m-wierzyc-have-trust-0a6cbf4eee17` | `vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1` | — | `B-16` |
| P7-NR-041 | confirmation | looks-good | `vp-l-zajmowac-sie-176f8a1300f8` | `vp-m-zajmowac-sie-occupation-activity-7e3a8332a3bc` | `vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e` | — | `B-17` |
| P7-NR-042 | example | replacement-accepted-as-presented | `vp-l-zajmowac-sie-176f8a1300f8` | `vp-m-zajmowac-sie-look-after-person-b23fbb8fc99b` | `vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` | — | `B-18` |
| P7-NR-043 | confirmation | looks-good | `vp-l-opiekowac-sie-3a290ee21577` | `vp-m-opiekowac-sie-care-for-278e820d8562` | `vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b` | — | `B-19` |
| P7-NR-044 | example | replacement-accepted-as-presented | `vp-l-zalezec-679daa27f9be` | `vp-m-zalezec-depend-on-d640b1729639` | `vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318` | — | `B-20` |
| P7-NR-045 | priority | accepted-as-presented | `vp-l-zalezec-679daa27f9be` | `vp-m-zalezec-matter-to-someone-e7bf97e3c145` | `vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc` | — | `B-21` |

## 7. Validated outcome ledger

Created outside Git:

`/Users/Kaj/Downloads/Priority_7_Phase_4B_Human_Attestation/phase4b-validated-ledger.json`

SHA-256:
`7196ef6a6bc41042ebb1b2c3f4d365c66a8e680a89052ff62437301ffe9fb209`.

The ledger preserves the source attestation hash, source decision-ledger hash, reviewer ID and
recorded metadata, all 45 Review IDs, group, exact human decision, zero-feedback/zero-flag status,
and canonical IDs where they exist. Missing canonical examples remain `null`; Phase 2B draft
references are kept separately and are not promoted into invented canonical IDs. The five exact
accepted replacement sentences are recorded as human-accepted but `inCanonicalCorpus: false`.

## 8. Canonical, governance, release, and production proofs

- `editorial/verb-pattern-candidates.json` is byte-identical to HEAD: worktree and HEAD Git blob
  are both `f3b8d2d704699125aecf8858eca01e0c6ec84c26`; file SHA-256 remains
  `b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`.
- The real corpus remains 30 lemmas, 34 meanings, 45 patterns, and 23 canonical examples.
- All 45/45 real patterns remain `reviewState: research`; zero real `reviewEvents` exist.
- All real `activityEligibility` arrays remain empty; zero canonical examples are audio-eligible.
- `reviewerRegistry` and `authorRegistry` remain empty. The external reviewer was not inserted
  into either registry in this ingestion-only phase.
- No real example changed. The five accepted replacements remain external/noncanonical.
- The canonical validator reports `Priority 7 private editorial record: valid`.
- The 44 Phase 3D-1 tests pass, including real-corpus, review-state, eligibility, audio, registry,
  production-runtime, version, and cache boundary checks.
- The 95 Phase 5A governance/freeze/release tests pass. Those tests use synthetic nonrelease
  fixtures only; no real freeze or release artifact was created.
- No real `content/verb-patterns.json` exists; no runtime projection was produced.
- No eligibility, runtime, release, public data, application, audio, service-worker, version,
  cache, schema, or migration file changed. Existing markers remain `APP_VERSION="8.10"`,
  service-worker cache `popolsku-v65`, storage schema version 2, and content migration revision 2.
- All tracked repository paths are byte-identical to HEAD. Production is untouched.

## 9. Phase boundary and verdict

Phase 4B is complete as an ingestion/validation phase. The accepted row-level outcomes and five
accepted proposed replacement sentences are recorded externally and traceable to exact canonical
objects, without inventing answers or changing canonical data. No review event is created yet,
no eligibility changes, and no freeze/runtime/release action occurs.

**Final verdict: GO. Do not start Phase 4C in this phase.**
