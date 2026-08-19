# Priority 7 — Phase 4F-B3B — Editorial Correction Implementation

*Including the Phase 4F-B3B.1 targeted tier-1 reference refresh and the
Phase 4F-B3B.2 committed-state guard hardening.*

## Verdict

**GO**

All five B3A corrections are implemented. The two that reach tier-1 reference
scope received a fresh, truthful reference verification backed by a re-opened
source. The two prior-phase guards that Codex found went vacuous once the
candidate is itself committed are now pinned to the immutable pre-B3B baseline
and proved non-vacuous by committed-state controls. All 45 patterns are
reference-verified, and the canonical corpus is byte-identical to the candidate
Codex reviewed.

---

## 1. How this phase actually went

The sequence matters, and is preserved rather than tidied away:

1. **Five-change implementation attempted.** B3B set out to apply all five
   approved B3A corrections.
2. **P7-NR-029 and P7-NR-030 invalidated their own tier-1 state.** The approved
   change flips `complements[0].required` from `true` to `false`.
   `_project_complement()` puts `required` inside the **external-verification**
   scope tier — the tier a `reference-verification` event stands over. The real
   validator dropped both rows from `reference-verified` to `research`.
3. **B3B correctly stopped those two.** Rewriting the 2026-08-14 acceptances'
   `scopeDigest` in place would have asserted that a past verification covered a
   frame it never saw. B3B declined, implemented the other three, and returned
   **GO WITH CHANGES REQUIRED** as an intermediate finding.
4. **The source was re-inspected.** Phase 4F-B3B.1 re-opened the WSJP PAN entry
   at the cited locator rather than trusting the stored note or B3A's summary.
5. **Optional Dative was directly supported** — for both patterns, separately
   (§3 below).
6. **`required: false` was implemented** on both rows, with the approved learner
   explanations.
7. **The old acceptances were preserved as history** — byte-for-byte, digests
   and notes and dates intact.
8. **Two fresh reference-verification acceptances were created**, one per row,
   over the corrected tier-1 scope.
9. **All 45 returned to reference-verified**, with zero validator issues.
10. **Codex reviewed the candidate and returned GO WITH CHANGES REQUIRED.** It
    accepted the canonical changes, source verification, reference refresh,
    governance state, evidence preservation, B3B suite and shipping boundary,
    and raised one contained blocker: two of the retargeted prior-phase guards
    reconstructed the pre-B3B corpus by reading `HEAD`, which is sound only
    while B3B is an uncommitted working tree. Codex proved the defect by
    committing a sixth unauthorized explanation change in scratch — the full
    4E.1 and 5-A suites still passed.
11. **Phase 4F-B3B.2 repaired both guards**, pinning them to the immutable
    baseline `7beb50d` and adding committed-state negative controls (§10a).

The intermediate **GO WITH CHANGES REQUIRED** results stand on the record as
real findings, not false starts: at step 3 the scope boundary worked exactly as
designed, and at step 10 an independent reviewer caught a guard that had been
correct when written and was quietly invalidated by the very commit it was
meant to police.

---

## 2. Baseline

| Item | Value |
| --- | --- |
| Baseline commit | `7beb50d7b3463d7745352f1608f1e30019529fdf` |
| Baseline tree | `ad6095037214360836b1bd9a5bb06326e0b809d7` |
| Remotes | zero |
| `push.default` | `nothing` |
| Real repository committed? | **no** — B3B is uncommitted by instruction |

### B3A inputs, byte-identical

| Artifact | SHA-256 |
| --- | --- |
| `reports/phase-4fb3a/adjudication-matrix.csv` | `95f0551c…0a5e27cd` |
| `reports/phase-4fb3a/summary.md` | `3eec5862…7e77109f` |

### B3A plan, parsed from the matrix

| Disposition | Count |
| --- | --- |
| ACCEPT AS IS | 21 |
| ACCEPT WITH NONBLOCKING NOTE | 19 |
| CHANGE BEFORE EDITORIAL ACCEPTANCE | 5 |
| DEFER | 0 |
| **Total** | **45** |

CHANGE rows exactly `P7-NR-005`, `P7-NR-029`, `P7-NR-030`, `P7-NR-037`,
`P7-NR-040`.

---

## 3. Source re-verification (§2 of the B3B.1 brief)

Both patterns cite the same contemporary entry:
`wsjp.pl/haslo/podglad/7908/mowic/4854655`, sense cue *mówić (o miłości)*,
**Składnia** section. The entry was re-opened and its valency frames read
directly.

The Składnia section lists seven frames. The two that matter:

| Row | Frame as printed | Verdict |
| --- | --- | --- |
| **P7-NR-029** | `mówić + (KOMU) + CO` | **Optional Dative licensed** |
| **P7-NR-030** | `mówić + (KOMU) + że ZDANIE\|żeby ZDANIE\|ZDANIE PYTAJNOZALEŻNE` | **Optional Dative licensed** |

In both, `KOMU` is parenthesised while the content argument is not. The entry
also lists `mówić + MOWA WPROST`, with no recipient slot at all, which is
consistent. The `do KOGO` alternants are likewise parenthesised.

Both patterns confirmed **separately**, from the source itself. Neither depended
on the stored note or on B3A's conclusion. §2's NO-GO condition did not trigger.

The sense cue `o miłości` recorded in the Phase 4F-A locator was also checked
and is accurate: it is the entry's own heading disambiguator, `mówić (o
miłości)`, and also appears as a collocation under *Połączenia*.

---

## 4. Evidence (§10)

**No evidence field changed anywhere in the corpus.** The existing WSJP records
already record the parenthesised KOMU truthfully and already qualify for the new
scope, so they were reused exactly:

| Row | Evidence record | Digest | Qualifies |
| --- | --- | --- | --- |
| P7-NR-029 | `wsjp-pan`, `contemporary-reference`, `complement-frame` | `sha256:6c2cda28…61b2cba2` | contemporary ✓ reference-fact ✓ |
| P7-NR-030 | `wsjp-pan`, `contemporary-reference`, `complement-frame` | `sha256:8ed08248…c2bd9516` | contemporary ✓ reference-fact ✓ |

- P7-NR-029's note already read *"Contemporary Skladnia lists (KOMU) + CO
  alongside a do KOGO alternant for the addressee."*
- P7-NR-030's locator already read *"…Skladnia, (KOMU) + ze ZDANIE frame"*.

Nothing was rewritten to make the new events pass. Unrelated evidence untouched.

---

## 5. Exact five-row canonical diff

Against `7beb50d`. Exactly five pattern rows differ, in exactly the approved
fields.

### P7-NR-005 — `słuchać` obey / Genitive

`vp-p-sluchac-obey-genitive-object-674adae2dec3`

| Field | Before | After |
| --- | --- | --- |
| `learnerExplanationEn` | `…the Genitive: nie słucha rodziców.` | `…the Genitive: dziecko słucha mamy.` |

The old illustration was negated, and the genitive of negation independently
forces the Genitive on any object, so it could not demonstrate Genitive
government. The replacement is affirmative *and* case-transparent: Genitive
`mamy` is distinct from Accusative `mamę`, whereas `rodziców` is syncretic.
Nothing else moved — including its reference event.

### P7-NR-029 — `mówić` + Dative + Accusative

`vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960`

| Field | Before | After |
| --- | --- | --- |
| `complements[0].required` | `true` | **`false`** |
| `learnerExplanationEn` | `Two roles: the person told is Dative, the thing told is Accusative.` | `The thing told is Accusative and the person told is Dative; the person can be left out: mówię prawdę.` |
| `reviewEvents` | 1 event | 2 events (original + refresh) |

`complements[1]` (Accusative content) stays `required: true`. No new pattern was
created. `cefr`, `teachingStatus`, `relationType` and evidence unchanged.

### P7-NR-030 — `mówić` + Dative + `że`-clause

`vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736`

| Field | Before | After |
| --- | --- | --- |
| `complements[0].required` | `true` | **`false`** |
| `learnerExplanationEn` | `The same meaning with clause content: the person stays Dative and że introduces what is said.` | `The same meaning with clause content: że introduces what is said, and the person, if named, is Dative: mówię, że to prawda.` |
| `reviewEvents` | 1 event | 2 events (original + refresh) |

The clause complement stays `required: true`. **`clauseKind` was not touched**:
the ASCII enum key `"ze"` is deliberate and `CLAUSE_TOKENS` in
`pp-verb-patterns.js` renders it as `"że …"`. B2's diacritic complaint was
correctly rejected by B3A and is not revisited.

### P7-NR-037 — `podobać się` + Nom + Dat

`vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9`

| Field | Before | After |
| --- | --- | --- |
| `teachingStatus` | `recognition-only` | `active-production` |
| `cefr.production` | *(absent)* | `A2` |
| `cefr.recognition` | `A2` | `A2` (unchanged) |

Meaning, `relationType` (`subject-experiencer`), complements, roles,
`learnerExplanationEn` and evidence unchanged. No WSJP sense-2 evidence added.
`ROLE_PHRASES` untouched.

### P7-NR-040 — `wierzyć w` + Accusative

`vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1`

| Field | Before | After |
| --- | --- | --- |
| `teachingStatus` | `recognition-only` | `active-production` |
| `cefr.production` | *(absent)* | `B1` |
| `cefr.recognition` | `B1` | `B1` (unchanged) |

The broad parent meaning is kept verbatim: **not split**, no new meaning id,
`internalScope` and its religious / ideological / self-confidence exclusions
unchanged. The Dative sibling
`vp-p-wierzyc-have-trust-dative-object-f38bb3e72123` was **not** touched — it was
already `active-production` (`recognition A2`, `production B1`), and that
pre-existing asymmetry is precisely what promoting `wierzyć w` removes.

### Everything else

Across all 45 patterns: no pattern ID, meaning ID or lemma ID changed; no
meaning, `internalScope`, evidence, example, `contentRefs`, `errorNotes`,
`activityEligibility`, `usage`, `relationType` or `releaseMode` changed. No
complement moved outside the two `mówić` rows. `reviewState` is
`reference-verified` on all 45.

---

## 6. Review history

### Preservation of the Phase 4F-A record (§6)

All 45 original acceptances survive **verbatim**. None was redigested,
re-dated, re-noted, deleted, or reinterpreted. Verified by comparing each
pattern's `reviewEvents` prefix against the `7beb50d` blob.

### The two fresh acceptances (§7)

Appended, one per row, using the existing actor. No actor was registered.

| Field | P7-NR-029 | P7-NR-030 |
| --- | --- | --- |
| `kind` | `reference-verification` | `reference-verification` |
| `decision` | `accept` | `accept` |
| `scopeVersion` | `1` | `1` |
| `scopeDigest` | `sha256:c7a75ea949cb9ef6d2514c3f312b739894f7847f2113c3a5160ab82dc346aa70` | `sha256:f7c96a0297be3542f194e4419d2f8302d1b32d281ef07b2f1bae9bd73692c51c` |
| `supportingEvidenceDigests` | `[sha256:6c2cda28…61b2cba2]` | `[sha256:8ed08248…c2bd9516]` |
| `actorRef` | `priority7-reference-analysis` | `priority7-reference-analysis` |
| `reviewedAt` | `2026-08-14` | `2026-08-14` |

Notes identify the source support for the optional recipient and mark the event
as a post-correction re-verification:

> Phase 4F-B3B.1 re-verification after the recipient was corrected to optional.
> WSJP Skladnia re-opened at the cited locator: `'mowic + (KOMU) + CO'`
> parenthesises KOMU, so an omitted Dative is licensed.

Every digest was recomputed through `priority7_tooling.py`; none was written by
hand. No `correction`, `reopen`, `external-verification`, `native-linguistic`,
`editorial-review` or `product-approval` event was created — the existing event
model accepted a second `reference-verification` acceptance directly, because
the scope genuinely moved.

**The duplicate-stage guard was not weakened.** It is still armed: appending a
third acceptance carrying the identical digest still raises
`REVIEW_DUPLICATE_STAGE_ACCEPTANCE`, and a test proves it.

### Final counts

| Metric | Value |
| --- | --- |
| Patterns | 45 |
| `reference-verified` | **45** |
| Phase 4F-A acceptances (historical) | **45** |
| Phase 4F-B3B.1 refresh acceptances | **2** |
| **Total `reference-verification` accepts** | **47** |
| `editorial-review` events | **0** |
| `product-approval` events | **0** |
| `editorial-reviewed` states | **0** |
| `approved` states | **0** |
| Reference actor | `priority7-reference-analysis` (unchanged) |
| `editorialActorRegistry` | byte-identical to baseline |
| `authorRegistry` | `{}` |
| `releaseMode` | `solo-maintainer-reference-backed` ×45 |

No `releaseAuthorization`, no freeze, no runtime projection, no tier-2 or tier-3
advancement.

---

## 7. Proof of the temporary 43 / 2 state (§5)

Measured **before** any refresh event was written, with the corrections applied:

```
validate_editorial issues: 2
  REVIEW_STATE_MISMATCH  $.lemmas[18].meanings[0].patterns[0].reviewState
      Current event history and digests require 'research', not 'reference-verified'.
  REVIEW_STATE_MISMATCH  $.lemmas[18].meanings[0].patterns[1].reviewState
      Current event history and digests require 'research', not 'reference-verified'.

patterns with stale tier-1 digest: 2   (both mówić rows)
patterns still digest-current:     43 / 45
```

No pattern other than P7-NR-029 and P7-NR-030 lost reference verification. The
invalidation was exactly as intended and is kept executable by
`TemporaryInvalidationTests`, so the reason the refresh exists cannot quietly
evaporate.

---

## 8. Scope digest results (§11)

| Row | tier-1 `reference-verification` | tier-2 `editorial-review` |
| --- | --- | --- |
| P7-NR-005 | unchanged | **moved** |
| P7-NR-029 | **moved** → fresh acceptance | **moved** |
| P7-NR-030 | **moved** → fresh acceptance | **moved** |
| P7-NR-037 | unchanged | **moved** |
| P7-NR-040 | unchanged | **moved** |

- **43 patterns** keep exactly the tier-1 scope/event relationship they had
  after Phase 4F-A.
- **2 patterns** carry a new tier-1 scope plus a new current acceptance; their
  superseded originals retain their historical digests, as history requires.
- **5 patterns** have changed tier-2 (editorial) scope digests. Since **no
  editorial acceptance exists**, this creates no stale editorial history — there
  is nothing at tier 2 to invalidate.

---

## 9. Activity eligibility and the `required` flag

`activityEligibility` is `[]` on all 45 patterns, before and after. Promoting
two patterns to `active-production` enabled **no** exercise: eligibility is not
derived from `teachingStatus`, and no derivation was added.

`pp-verb-patterns.js` type-checks `required` and demands it as a closed schema
key, but **no renderer branch reads it**. So the flag change is invisible to a
learner today — which is why the adjudication paired it with the learner
explanation, and why the correction could not be smuggled in without the tier-1
re-verification the flag's scope demands. The canonical value is now truthful
and available to future UI. The corpus now holds 52 required and **2 optional**
complements, against 54 required at baseline.

---

## 10. Prior-phase test retargeting (§13)

Five earlier suites encoded assumptions that a later authorized phase broke.
All were **retargeted, never relaxed**.

### Linguistic-content guards

`test_priority7_phase4c.py`, `test_priority7_phase4e1.py`,
`test_priority7_phase4fa.py`, `test_priority7_phase5a.py` each asserted that no
later phase changes learner-facing content. Each now normalises away **exactly
the five approved edits** before comparing, reverting a field only when it holds
the precise value B3B wrote.

- No generic exclusion set was widened — the blanket exclusions are still only
  `releaseMode`, `reviewState`, `reviewEvents`, `evidence`.
- A sixth linguistic edit anywhere still fails.
- A *wrong* value on any approved field still fails, because it would not match
  the revert key.
- Each suite carries a negative-control test proving its own normalisation
  cannot hide an unapproved edit.

### Review-event counts

`test_priority7_phase3d1.py`, `test_priority7_phase4c.py`,
`test_priority7_phase4e.py`, `test_priority7_phase4e1.py`,
`test_priority7_phase4fa.py` and
`test_priority7_phase5a.py` asserted a flat 45 events. History was **not**
rewritten to imply Phase 4F-A created 47. Each suite now reads the Phase 4F-A
checkpoint back from the commit that phase produced (`7beb50d`) and holds the
two facts apart:

- `PHASE_4FA_EVENT_COUNT = 45` — what Phase 4F-A actually wrote;
- `CURRENT_EVENT_COUNT = 47` — what stands after the targeted refresh.

`test_priority7_phase4fa.py` additionally gained tests that the originals
survive verbatim, that only the two refreshed rows gained an acceptance, and
that every *standing* digest recomputes while the superseded set is pinned to
exactly those two rows.

---

## 10a. Committed-state guard hardening (Phase 4F-B3B.2)

### The defect

Two of the retargeted guards reconstructed the pre-B3B corpus by reading
`HEAD`:

| Suite | Guard | Read |
| --- | --- | --- |
| `test_priority7_phase4e1.py` | `RealGovernanceBoundary.test_the_real_corpus_changed_only_governance_and_evidence` | `git show HEAD:editorial/verb-pattern-candidates.json` |
| `test_priority7_phase5a.py` | `RealCorpusBoundaryTests.test_real_corpus_changed_only_governance_and_evidence_since_head` | `git show HEAD:<corpus>` |

While B3B is an uncommitted working-tree candidate, `HEAD` is still the B3B
baseline, so the comparison is real. The moment the candidate is itself
committed, `HEAD` *contains* it: both sides of the comparison carry the same
edits, both are normalised identically, and the guard passes regardless of what
changed. Codex demonstrated this by committing a sixth unauthorized
`learnerExplanationEn` change in scratch — both suites passed in full.

This was a latent defect from the B3B retarget, not from B3B.1. It was noted at
the time and misjudged as harmless because the committed-state run still
*passed*; passing unconditionally is precisely the failure.

### The repair

Both guards now read the immutable pre-B3B baseline:

```python
PHASE_4FB3B_BASELINE_SHA = PHASE_4FA_CHECKPOINT_COMMIT
#  == "7beb50d7b3463d7745352f1608f1e30019529fdf"
```

Aliased to the existing checkpoint constant rather than re-spelled, so the two
names cannot drift: 4F-A produced that commit and B3B began from it, so they are
one commit seen from two sides.

Two further tightenings fell out of the repair:

- **Only the working side is normalised.** The baseline predates B3B and holds
  none of the values `without_phase_4fb3b_edits` reverts, so normalising it was
  a no-op that could only ever mask a difference. The guard now reads: *the
  working corpus, with the five approved edits reverted, equals the pre-B3B
  corpus.*
- The projection and the four governance exclusions moved into named module
  helpers (`corpus_projection`, `GOVERNANCE_KEYS`) so a regression can assert
  the exclusion set was not widened.

**Nothing else changed.** The normalisation table is exactly as Codex accepted
it: the same five patterns, the same exact values, reverted only when the field
holds the precise value B3B wrote. No ignored-field widening, no category-based
matching, no "later phases may differ" escape.

### Committed-state negative controls

Each suite gained a `CommittedStateGuard` class that builds a throwaway
repository in a temporary directory, commits the pre-B3B baseline, then commits
the candidate on top so `HEAD` has genuinely moved past the baseline. The real
repository is never written to and its HEAD is never moved.

| Control | Expectation |
| --- | --- |
| Legitimate candidate committed as HEAD | pinned guard **passes** |
| Sixth unauthorized edit committed | pinned guard **fails** |
| Wrong value on an approved field (`cefr.production`) | **fails** |
| Approved field set to some third value | **fails** |
| Unauthorized `required` flip on an untouched pattern | **fails** |
| Sixth edit, read via the superseded `HEAD` form | **passes** — the defect, kept executable |
| Guard body inspected for the pinned constant | reads `PHASE_4FB3B_BASELINE_SHA`, not `HEAD` |

The sixth-edit control is the decisive one: same repository, same unauthorized
commit, same guard body, only the revision differs. Read from `HEAD` it passes;
read from the pinned baseline it fails. That test would have failed under the
old implementation and passes only after this repair.

`tests/test_priority7_phase4fb3b.py` gained a cross-suite
`CommittedStateGuardRegressionTests` that loads both suites and drives *their
own* guard bodies against one isolated committed repository — behavioural proof
rather than source-string matching, so it fails if either suite regresses to a
HEAD-relative baseline.

### Search across all six retargeted suites

| Suite | Baseline reads | Verdict |
| --- | --- | --- |
| `test_priority7_phase3d1.py` | `PHASE_4FA_CHECKPOINT_COMMIT` only | commit-independent — untouched |
| `test_priority7_phase4c.py` | `PHASE_4FA_CHECKPOINT_COMMIT` only | commit-independent — untouched |
| `test_priority7_phase4e.py` | `PHASE_4FA_CHECKPOINT_COMMIT` only | commit-independent — untouched |
| `test_priority7_phase4e1.py` | `HEAD:` at line 1509 | **repaired** |
| `test_priority7_phase4fa.py` | `BASELINE_COMMIT` throughout; `diff BASELINE_COMMIT HEAD` at 1134 | sound — the immutable commit is the fixed side and `HEAD` the moving one, unioned with `git status`, so it is meaningful committed *and* uncommitted. Untouched. |
| `test_priority7_phase5a.py` | `HEAD:` at line 2443 | **repaired** |

Codex found exactly the two that were defective. No third genuinely vacuous
corpus guard exists.

One adjacent observation, recorded but deliberately **not** changed:
`test_priority7_phase5a.py`'s shipping-file allowlist reads only
`git status --porcelain`, which goes empty once the candidate is committed. It
is a shipping-file guard rather than a B3B linguistic guard, it lies outside the
B3B.2 mandate, and the same surface is independently covered committed-state by
`test_priority7_phase4fa.py::test_no_shipping_file_was_modified` (which unions
`git status` with `diff BASELINE_COMMIT HEAD`) and by
`test_priority7_phase4fb3b.py::ShippingBoundaryTests`. Flagged for a future
phase rather than redesigned here.

---

## 11. Phase 4F-C handoff

Example work was not begun. No example, origin or author record changed; 23
examples remain, all `repository-reuse`, zero `editorial-generated`,
`authorRegistry` still `{}`.

### Already-pending example slots — preserved untouched

| Row | Lemma | State |
| --- | --- | --- |
| P7-NR-011 | dziękować | example present, `origin.kind = repository-reuse` |
| P7-NR-012 | płacić | example present, `origin.kind = repository-reuse` |
| P7-NR-033 | widzieć | example present, `origin.kind = repository-reuse` |
| P7-NR-042 | zajmować się | `examples: null` — empty slot |
| P7-NR-044 | zależeć | `examples: null` — empty slot |

### B3A example findings routed to 4F-C, with B3A's own severity preserved

| Row | Lemma | B3A severity | Disposition |
| --- | --- | --- | --- |
| P7-NR-007 | potrzebować | LOW | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-014 | używać | LOW | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-018 | dbać | LOW | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-031 | pytać | LOW | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-032 | pytać | LOW | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-035 | myśleć | MEDIUM | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-036 | znaleźć | MEDIUM | ACCEPT WITH NONBLOCKING NOTE |
| P7-NR-043 | opiekować się | MEDIUM | ACCEPT WITH NONBLOCKING NOTE |

All eight are **nonblocking** in B3A's classification; the MEDIUM rows are the
higher-priority example work within that class. None blocks editorial
acceptance.

### Directives carried forward from the corrected rows

- **P7-NR-005** — the canonical example must also be affirmative and
  case-transparent, matching the corrected explanation.
- **P7-NR-029 / P7-NR-030** — **no longer blocked.** The tier-1 refresh is
  complete, so 4F-C may author examples against the corrected optional-recipient
  frame. Examples should show the recipient both present and omitted.
- **P7-NR-037** — author a contrastive canonical example pairing `podobać się`
  with `lubić`.
- **P7-NR-040** — author a contrastive canonical example pairing `wierzę ci`
  with `wierzę w ciebie`.

---

## 12. Validation

| Gate | Result |
| --- | --- |
| Full Python (`pytest tests/`) | **922 passed, 0 failed** |
| Full JXA (36 files, `osascript -l JavaScript`) | **10,544 assertions, 0 failed** |
| `validate_content.py` | OK — 1215 cards, 353 drills, 1675 ids |
| `verify_audio.py` | OK — 3377 phrases, 3377 manifest entries, 3377 MP3s |
| `build_pages.py --check` | OK — committed output current, 32 sitemap URLs |
| `priority7_tooling.py validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |

### Named suites

| Suite | Result |
| --- | --- |
| `test_priority7_phase4fb3b.py` | 120 passed |
| `test_priority7_phase4fa.py` | 73 passed |
| `test_priority7_phase4e1.py` | 97 passed |
| `test_priority7_phase4e.py` | 104 passed |
| `test_priority7_phase5a.py` | 118 passed |
| `test_priority7_phase4c.py` | 56 passed |
| `test_priority7_phase3fa.py` | 17 passed |
| `test_priority7_phase3d1.py` | 44 passed |
| `test_priority7_phase2a.py` | 77 passed |

Phase 4F-B3B.2 added 7 controls to 4E.1 (90→97), 6 to 5-A (112→118) and 6
cross-suite regressions to the B3B suite (114→120).

B3A has no executable suite; its artifacts are consumed and byte-pinned instead.

### Committed-scratch rehearsal (§18)

Superseded scratch candidates were **not** reused:
`4c2334991921ee9361da848ea3aa7683717acc08` (three-change),
`42998a94bdc05548c4b96e85e2d5ace4dc8c036b` and
`83de4de71af56e93b64e8ea821f78002380f98ad` (pre-B3B.2). A fresh isolated scratch
was created from the final B3B.2 candidate, committed there only, and the whole
battery re-run: B3B tests, full Python, full JXA, content, audio, pages,
editorial validation, and `git diff --check HEAD^ HEAD`. The scratch working
tree is clean and has zero remotes.

The scratch also ran the **mutation rehearsal** the repair exists for: with the
legitimate candidate as committed HEAD the 4E.1 and 5-A guards pass; with a
sixth unauthorized linguistic edit committed on top so HEAD contains it too,
both guards **fail**. The mutation was then discarded.

The scratch commit and tree SHAs are recorded in the phase response rather than
here: this file is part of the committed candidate, so it cannot contain the
hash of the commit that contains it.

The real B3B repository remains **uncommitted**, with zero remotes.

---

## 13. Files changed

| Path | Change |
| --- | --- |
| `editorial/verb-pattern-candidates.json` | modified — five corrections + two refresh events |
| `tests/test_priority7_phase3d1.py` | modified — checkpoint split |
| `tests/test_priority7_phase4c.py` | modified — guard re-pinned, checkpoint split |
| `tests/test_priority7_phase4e.py` | modified — checkpoint split |
| `tests/test_priority7_phase4e1.py` | modified — guard re-pinned, checkpoint split |
| `tests/test_priority7_phase4fa.py` | modified — guard re-pinned, checkpoint split |
| `tests/test_priority7_phase5a.py` | modified — guard re-pinned, checkpoint split |
| `tests/test_priority7_phase4fb3b.py` | added |
| `reports/priority-7-phase-4fb3b-summary.md` | added |
| `reports/phase-4fb3a/*` | added — B3A inputs, byte-identical |

`priority7_tooling.py` is byte-identical to baseline. No shipping, browser or
runtime file moved. No `content/verb-patterns.json`, no `patternDataRevision`,
no service-worker, `APP_VERSION` or cache change.

---

## 14. Verdict rationale

- **Not NO-GO** — the fresh reference verification was established without
  weakening governance and without touching the tooling. The duplicate-stage
  guard is intact, the historical events are intact, and the source genuinely
  licenses the change.
- **Not GO WITH CHANGES REQUIRED** — no repair remains. All five adjudicated
  corrections are in, all 45 patterns are reference-verified, the two rows that
  needed re-verification have it, and the two guards Codex flagged are now
  non-vacuous under commit with executable proof.
- **GO** — ready for Phase 4F-C example work, which has not been begun.

Phase 4F-B3B.2 changed no canonical data, no review event, no evidence and no
tooling: `editorial/verb-pattern-candidates.json` is byte-identical to the
candidate Codex reviewed (`sha256:a44c7f04…39efe4a9`).
