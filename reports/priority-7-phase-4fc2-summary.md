# Priority 7 — Phase 4F-C2: Implementing the Adjudicated Canonical Examples

**Verdict: GO**

Phase 4F-C1 assessed the 13-row example queue, Phase 4F-C1B reviewed it blind, and Phase 4F-C1C
adjudicated the two into one locked result per row. This phase implemented that result exactly:
two rows kept, five replaced, six created, one nonhuman example-generation actor registered, and
nothing else. No editorial-review event was created, nothing was product-approved, nothing was
frozen, and no runtime was generated.

**Baseline** — pinned by SHA, never resolved as `HEAD`:
`080d92ad49a514332f21ecd90b4a11de070a243f`, tree `74dd8cbebc303b646e4e38e2082d25c91b1cf6e1`.

---

## 1. The plan, read from the locked matrix

`reports/phase-4fc1c/adjudication-matrix.csv` parses as **13 rows** covering exactly the queue
`P7-NR-007, 011, 012, 014, 018, 031, 032, 033, 035, 036, 042, 043, 044`.

| Dimension | Locked value | Read back |
|---|---:|---|
| KEEP CURRENT | 2 | ✅ 007, 014 |
| REPLACE | 5 | ✅ 011, 012, 018, 033, 036 |
| CREATE | 6 | ✅ 031, 032, 035, 042, 043, 044 |
| ADD | 0 | ✅ |
| NO IMPLEMENTATION YET (open) | 0 | ✅ |
| MUST CHANGE / USEFUL IMPROVEMENT / NO CHANGE | 10 / 1 / 2 | ✅ |
| REQUIRED / OPTIONAL POLISH / NOT APPLICABLE | 10 / 1 / 2 | ✅ |
| Final origins | 2 repository-reuse, 11 editorial-generated, 0 original | ✅ |

Nothing was re-adjudicated. Every final Polish sentence was re-verified against its pattern's
actual complement, case, preposition, aspect, participant structure and CEFR band before it was
stored, and no contradiction was found, so nothing had to stop.

---

## 2. The anchor — the matrix describes the immutable baseline

Every check below compares the corpus against the matrix. If the matrix were the only reference,
an edit applied to both would agree with itself, so the matrix is first tied to history that no
phase can rewrite:

- all 13 `currentPolish` / `currentEnglish` / `currentOrigin` / `currentRepositorySource` columns
  reproduce the baseline commit's corpus **byte for byte**, and the four ABSENT rows really do
  have no `examples` key at the baseline;
- all 13 `lemma` and `meaningId` columns reproduce the baseline;
- the baseline holds **45 patterns and 23 canonical examples, all `repository-reuse`**;
- four of the eleven final sentences — 011, 012, 042, 044 — appear verbatim in
  `reports/priority-7-phase-4c-summary.md` **as committed at the baseline**, which records the
  text AB accepted as presented. That is an anchor outside both the matrix and this phase's work.
- 033 is the row where C1C did **not** adopt AB's sentence: the Phase 4C candidate
  `Czy widzisz tę górę na horyzoncie?` is in that committed summary and the implemented final is
  not, which is asserted directly.

---

## 3. The 13 dispositions as implemented

| Row | Lemma | Disposition | Final Polish | Final English | Origin | Source |
|---|---|---|---|---|---|---|
| `P7-NR-007` | potrzebować | KEEP CURRENT | `Potrzebuję zaświadczenia z pracy.` | I need a certificate from work. | repository-reuse | card `a2-official-matters-019` field `ex` |
| `P7-NR-011` | dziękować | REPLACE | `Dziękuję siostrze za kolację.` | I thank my sister for dinner. | editorial-generated | — |
| `P7-NR-012` | płacić | REPLACE | `Płacę za kawę i gazetę.` | I am paying for a coffee and a newspaper. | editorial-generated | — |
| `P7-NR-014` | używać | KEEP CURRENT | `Używam tej aplikacji do nauki języków.` | I use this app for learning languages. | repository-reuse | card `b1-media-technology-001` field `ex` |
| `P7-NR-018` | dbać | REPLACE | `Codziennie dbam o kondycję.` | I look after my fitness every day. | editorial-generated | — |
| `P7-NR-031` | pytać | CREATE | `Zawsze pytam o cenę.` | I always ask about the price. | editorial-generated | — |
| `P7-NR-032` | pytać | CREATE | `Pytam koleżankę o nową restaurację.` | I am asking my friend about the new restaurant. | editorial-generated | — |
| `P7-NR-033` | widzieć | REPLACE | `Czy widzisz tę górę?` | Do you see that mountain? | editorial-generated | — |
| `P7-NR-035` | myśleć | CREATE | `Ciągle myślę o egzaminie.` | I keep thinking about the exam. | editorial-generated | — |
| `P7-NR-036` | znaleźć | REPLACE | `W końcu znalazłam nową pracę.` | I finally found a new job. | editorial-generated | — |
| `P7-NR-042` | zajmować się | CREATE | `Kiedy siostra jest w pracy, zajmuję się jej córką.` | When my sister is at work, I look after her daughter. | editorial-generated | — |
| `P7-NR-043` | opiekować się | CREATE | `Opiekuję się chorą babcią.` | I look after my sick grandmother. | editorial-generated | — |
| `P7-NR-044` | zależeć | CREATE | `Nasze plany zależą od pogody.` | Our plans depend on the weather. | editorial-generated | — |

### The two KEEP CURRENT rows

007 and 014 hold the **byte-identical baseline example object** — id, key, `pl`, `en`,
`audioEligible` and the complete `origin` including `repositorySource`. No punctuation,
translation, origin, source or identity was tidied. Both sources were re-resolved against the live
repository index and still match byte-exactly on `pl`.

### The four rows the brief singles out

- **P7-NR-033 (widzieć).** The adjudicated visual-perception sense is implemented as
  `Czy widzisz tę górę?` — an inanimate geographic object, so the encounter reading both reviews
  worried about is unavailable. `tę górę` shows the Accusative on demonstrative and noun. The
  rejected `Widziałam wczoraj twoją siostrę.` does not appear anywhere in the corpus, and neither
  does the longer Phase 4C candidate.
- **P7-NR-012 (płacić).** The morphologically opaque `wszystko` is gone; `za kawę i gazetę` shows
  two overt feminine Accusatives.
- **P7-NR-018 (dbać).** Implemented as REPLACE, not ADD. The pattern ends with exactly one
  example.
- **P7-NR-044 (zależeć).** The single adjudicated sentence, not the rejected two-sentence
  repository-reuse candidate, which appears nowhere in the corpus.
- **P7-NR-036 (znaleźć).** The old `udało mi się … mieszkanie` teaching example is gone; neither
  `udało mi się` nor `mieszkanie` occurs in the new sentence.

No pattern gained a second example. All 45 patterns carry at most one, and every one of the 13
queue patterns ends the phase with exactly one — the single release-facing example C1C specified.
`pp-verb-patterns.js` still projects `examples[0]` only, which is why ADD stayed unavailable.

---

## 4. Actor registration

Exactly one new identity was added to `editorialActorRegistry`:

```json
"priority7-example-generation": {
  "human": false,
  "kind": "example-generation-workflow",
  "roles": ["example-generation"],
  "namedInPhase": "Priority 7 Phase 4F-C2"
}
```

- `human: false`, stated explicitly, as `_validate_editorial_actor` requires.
- **One role, `example-generation`**, which is the exact schema-supported role the
  `editorial-generated` origin resolves through. It holds no `reference-verification` and no
  `editorial-review` role, so it cannot verify a reference, cannot review editorially, and cannot
  advance any pattern.
- Deliberately **distinct** from `priority7-reference-analysis`, whose record is byte-identical to
  the baseline.
- The key is claimed by no human registry. `authorRegistry` stays **empty** and no
  `origin.kind = "original"` exists anywhere, so no human-authorship claim was created and AB was
  not recorded as an author. AB's reviewer record is byte-identical to the baseline.

Proven negatively as well: removing the actor from the registry raises
`EDITORIAL_ACTOR_REGISTRY_DANGLING`; setting `human: true` raises
`EDITORIAL_ACTOR_NOT_NONHUMAN`; giving it `reference-verification` instead raises
`EDITORIAL_ACTOR_ROLE`.

---

## 5. Provenance and copyright

All 11 `editorial-generated` examples carry exactly
`{"kind": "editorial-generated", "generatorRef": "priority7-example-generation", "adoptedAt": "2026-08-16"}`
— no `repositorySource`, no `authorRef`, no `authoredAt`. Attaching a repository source to one of
them raises `ORIGIN_EDITORIAL_FIELD_FORBIDDEN`; switching one to `original` raises
`AUTHOR_REGISTRY_DANGLING`.

The C1C generated-string checks were re-run in this phase against the live data rather than taken
on C1C's word: each of the 22 generated strings (11 Polish, 11 English) was searched, verbatim and
as a substring, across **all strings in the 1,665 indexed repository entities** and across the
whole baseline corpus. **Zero occurrences.** No generated sentence is trimmed or rewritten
repository text under a new provenance, and none silently duplicates shipped content. No WSJP PAN
or Mędak example sentence, definition, collocation list or citation was consulted or reproduced;
no such text appears in any canonical example. No false repository source is attached anywhere.

---

## 6. Example identity — baseline → C2

| Row | Disposition | Baseline example ID | C2 example ID | Durable key |
|---|---|---|---|---|
| `P7-NR-007` | KEEP | `vp-e-potrzebowac-need-genitive-object-certificate-from-work-9bb3306bf0ee` | **identical** | `certificate-from-work` |
| `P7-NR-011` | REPLACE | `vp-e-dziekowac-thank-dative-recipient-za-accusative-thanks-for-cooperation-92656ebcc371` | **identical** | `thanks-for-cooperation` |
| `P7-NR-012` | REPLACE | `vp-e-placic-pay-za-accusative-goods-how-much-for-everything-dd5e5c88cfd4` | **identical** | `how-much-for-everything` |
| `P7-NR-014` | KEEP | `vp-e-uzywac-use-genitive-object-using-an-app-4ea0e75b504a` | **identical** | `using-an-app` |
| `P7-NR-018` | REPLACE | `vp-e-dbac-take-care-of-o-accusative-target-care-every-day-171833c3174d` | **identical** | `care-every-day` |
| `P7-NR-031` | CREATE | none | `vp-e-pytac-ask-for-information-o-accusative-topic-asking-about-the-price-662fceb895d3` | `asking-about-the-price` |
| `P7-NR-032` | CREATE | none | `vp-e-pytac-ask-for-information-accusative-person-o-accusative-topic-asking-a-friend-about-a-restaurant-4e51f8927a78` | `asking-a-friend-about-a-restaurant` |
| `P7-NR-033` | REPLACE | `vp-e-widziec-perceive-visually-accusative-object-saw-your-sister-ec51af47f224` | **identical** | `saw-your-sister` |
| `P7-NR-035` | CREATE | none | `vp-e-myslec-think-about-o-locative-topic-thinking-about-the-exam-10ede796a5be` | `thinking-about-the-exam` |
| `P7-NR-036` | REPLACE | `vp-e-znalezc-find-accusative-object-finally-found-a-flat-3609f7a71e3f` | **identical** | `finally-found-a-flat` |
| `P7-NR-042` | CREATE | none | `vp-e-zajmowac-sie-look-after-person-instrumental-object-looking-after-my-sisters-daughter-1976cdf5b971` | `looking-after-my-sisters-daughter` |
| `P7-NR-043` | CREATE | none | `vp-e-opiekowac-sie-care-for-instrumental-object-caring-for-a-sick-grandmother-5d1ea100cdfa` | `caring-for-a-sick-grandmother` |
| `P7-NR-044` | CREATE | none | `vp-e-zalezec-depend-on-od-genitive-source-plans-depend-on-the-weather-e539ac27be66` | `plans-depend-on-the-weather` |

### Why the five REPLACE rows keep their IDs

The locked stable-ID specification's own change matrix places *example wording* in the keep-identity
row: "Learner explanation, gloss wording, **example wording**, usage note — yes; frozen
wording/policy approval still required." Its section 3 additionally freezes keys after allocation,
and only an identity error — a changed parent, participant structure, case, preposition or
relation — creates and retires. A replacement sentence in the same pattern's single example slot is
none of those. Phase 4C reached the same reading on these same rows and recorded it in its section
10. So the durable key is untouched and the ID, which is
`sha256("v1|example|<patternId>|<key>")` over exactly those two inputs, recomputes to the value it
already held. This was verified, not assumed: `allocate_example_id` was re-run for all five and
returned the existing ID each time.

The C1C summary's implementation note says "**Existing example IDs** that can carry new wording,
with re-minted keys". Those two halves cannot both hold: the ID *is* a function of the key, so a
re-minted key necessarily yields a different ID, which would contradict "existing example IDs" and
would require `allocationRegistry` records — for the example, its pattern, its meaning and its
lemma — that the never-frozen corpus has no basis to write. The locked architecture resolves it,
and it resolves in favour of the identity-preserving reading: keys are frozen, wording is not.

### Allocation state

| Check | Result |
|---|---|
| Canonical examples | 23 → **29** |
| Every example ID recomputes from `(patternId, key)` | **29 / 29** |
| Duplicate example IDs | **0** |
| Duplicate `(patternId, key)` pairs | **0** |
| Baseline IDs retired | **0** — all 23 retained |
| New IDs | **6** |
| Tombstoned IDs reused | **0** — there are no tombstones; the corpus has never been frozen |
| `allocationRegistry` | **still empty**, correctly: no released ID has drifted from its seed |
| Hand-authored ID probe | `ID_RECOMPUTATION` raised, so the guard is not vacuous |

Every pattern outside the 13-row queue keeps its `examples` array byte-identical.

---

## 7. Whole-corpus provenance counts

Calculated from the data, not assumed:

| Origin | Baseline | After C2 |
|---|---:|---:|
| `repository-reuse` | 23 | **18** |
| `editorial-generated` | 0 | **11** |
| `original` | 0 | **0** |
| **Total** | **23** | **29** |

Across the 13 C1C queue rows: **2 repository-reuse, 11 editorial-generated, 0 original** — exactly
the locked split. All 18 surviving repository-reuse sources resolve byte-exactly against the live
repository index. **Zero newly-created `original` examples**; the string `"original"` does not
occur in the corpus.

---

## 8. Reference verification survives

| Item | Baseline | After C2 |
|---|---:|---:|
| Patterns | 45 | **45** |
| `reference-verified` | 45 | **45** |
| `research` | 0 | **0** |
| `reference-verification` acceptances | 47 | **47** |
| `editorial-review` events | 0 | **0** |
| `product-approval` events | 0 | **0** |
| `editorial-reviewed` / `approved` patterns | 0 | **0** |

Proven through the real review-state tooling, not by reading `reviewState`:
`_derive_review_currency` was replayed over every pattern's history, digests and evidence for both
the baseline and the C2 corpus. All 45 derive `reference-verified`, with zero diagnostics, and the
complete `ReviewCurrency` value — state, verification pins, human-native-review currency, human
verification currency — is **identical to the baseline for all 45 patterns**. No pattern fell below
`reference-verified`, so nothing had to stop.

The mechanism is the locked scope-tier split: examples live in the tier-2 (`native-linguistic` /
`editorial-review`) projection and above, and are absent from the tier-1
(`external-verification` / `reference-verification`) projection. Measured directly:

- **tier-1 scope digests: unchanged on all 45 patterns**, so no reference-verification event was
  invalidated and no fresh one was needed. None was created, re-dated or edited — every pattern's
  `reviewEvents` array is byte-identical to the baseline.
- The two `mówić` rows that carry a superseded earlier digest carried it at the baseline too; C2
  neither created that condition nor healed it.

---

## 9. Changed tier-2 / editorial scope digests

Exactly the **11 implemented rows**, and no others. There are no editorial-review acceptances
anywhere in the corpus, so no editorial history was made stale and none was created:

```
vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c
vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f
vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2
vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b
vp-p-placic-pay-za-accusative-goods-73c6760c091d
vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a
vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8
vp-p-widziec-perceive-visually-accusative-object-80b697e51432
vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939
vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318
vp-p-znalezc-find-accusative-object-d80c52211462
```

The `product-approval` (tier-3) digests moved on the same 11 and no others. The two KEEP CURRENT
rows are untouched at every tier.

---

## 10. Canonical boundary against the pinned baseline

The corpus with `examples` stripped from every pattern is **equal to the baseline with the same
projection**. Field by field, across all 45 patterns, nothing moved in:

`key`, `relationType`, `complements`, `cefr`, `teachingStatus`, `usage`, `learnerExplanationEn`,
`activityEligibility`, `evidence`, `releaseMode`, `reviewState`, `reviewEvents`, `contentRefs`,
`errorNotes` — nor in any lemma or meaning field. `activityEligibility` is still empty on all 45,
every example is still `audioEligible: false`, and the document envelope is unchanged
(`artifactStatus: priority-7-editorial-nonproduction`, `formatVersion: 1`).

`errorNotes` were deliberately **not** edited to match the new sentences, as section 24 requires:
the `znaleźć` note still corrects `mieszkania` and the `dziękować` note still uses `mamie`. C1C
accepted that cost explicitly on both rows.

### Every canonical and context field that changed

| File | Field | Change | Why |
|---|---|---|---|
| `editorial/verb-pattern-candidates.json` | `pattern.examples[0].pl` / `.en` on 5 patterns | replaced | REPLACE rows 011, 012, 018, 033, 036 |
| | `pattern.examples[0].origin` on those 5 | `repository-reuse` → `editorial-generated` | the new sentences are not repository text and have no human author |
| | `pattern.examples` on 6 patterns | key added, one example | CREATE rows 031, 032, 035, 042, 043, 044. The key is placed immediately after `reviewEvents`, matching all 23 existing example-bearing patterns |
| `editorial/priority-7-authoring-context.json` | `editorialActorRegistry["priority7-example-generation"]` | added | required for `origin.kind = "editorial-generated"` to resolve |
| | `contextNotice` | extended | maintainer-facing prose; it previously stated that no editorial-generated example may exist yet, which C2 makes false. No identity lives in this field |

Nothing else changed anywhere. All 13 shipping and runtime sentinels — `index.html`, `sw.js`,
`manifest.json`, `priority7_tooling.py`, `pp-verb-patterns.js`, `build_pages.py`,
`validate_content.py`, the five `data-*.js` files and `audio-manifest.json` — are byte-identical to
the baseline. `content/verb-patterns.json` does not exist, no `releaseAuthorization`,
`patternDataRevision` or freeze artifact was written, and the copied C1 / C1B / C1C review
artifacts are unedited.

---

## 11. C2 footprint, and the historical-footprint bug

The C2 boundary guard measures the working candidate against the pinned baseline SHA, folding
`git diff --name-only <baseline>` with `git status --porcelain -uall`, so it means the same thing
whether C2 sits untracked in the real workspace or committed in a scratch rehearsal. It is a
**prefix allowlist** (`editorial/`, `reports/`, `tests/`) plus a positive statement of what C2 must
not touch — shipping sentinels, runtime payloads, and every canonical field outside the example
work. It is deliberately **not** a closed set of file paths: a closed set is exactly the bug Phase
4F-C1.1 had to repair, and it would forbid every file a successor phase adds.

Within `editorial/`, exactly the two known files changed.

The Phase 4F-C1.1 repair in `tests/test_priority7_phase4fb3b.py` is preserved: it still tests the
immutable `7beb50d7… → 080d92ad…` transition, `B3B_FOOTPRINT` still holds exactly its 11 approved
paths, no C2 path was added to it, and the historical transition still resolves to that footprint.
This is asserted from outside the module by the C2 suite.

---

## 12. Test debt this phase had to repair

C2 is the first phase since Phase 4F-A entitled to change canonical data, and doing so exposed a
pre-existing bug of the same class Phase 4F-C1.1 repaired once: **eight closed phase suites stated
their own phase-closing claims over the *live* editorial documents** rather than over the state
they described. Every one of them failed the moment the adjudicated examples were stored — 51
failures in total, none of them a real defect in the implementation.

The repair follows the project's own established idiom. Phase 4F-B3B, when it changed canonical
fields, added a `without_phase_4fb3b_edits` normalisation to the suites that asserted over them;
C2 adds the parallel `without_phase_4fc2_examples` / `without_phase_4fc2_actor`. The normalisation
is **keyed on the adjudicated final text**, so it cannot hide an unapproved change: a sentence C1C
did not lock, an example on a fourteenth pattern, or a different origin is left in place and still
breaks the guard. Two new non-vacuity tests (in 4F-A and 4C) assert exactly that.

| Suite | Failures | Repair |
|---|---:|---|
| `test_priority7_phase4fb3b.py` | 14 | `load_corpus` / `load_context_document` return the B3B candidate — the live documents with C2's approved work reverted. One test narrowed from whole-document to per-registry equality, excluding `contextNotice` |
| `test_priority7_phase4fa.py` | 4 | normalisation applied to the linguistic projection and the pending-slot claims; the closed actor-key-set assertion restated as the review-role boundary 4F-A actually established |
| `test_priority7_phase4e1.py` | 7 | `real_corpus` / `real_context_document` / `candidate_corpus` normalised |
| `test_priority7_phase4e.py` | 9 | same |
| `test_priority7_phase5a.py` | 3 | same, plus the Phase 4C context boundary |
| `test_priority7_phase4c.py` | 12 | the "five accepted sentences did not enter the corpus" family stated over the corpus 4C left behind |
| `test_priority7_phase3d1.py` | 1 | closed actor-key-set restated as "no actor holds `editorial-review`" |
| `test_priority7_phase3fa.py` | 1 | same |

`tests/test_priority7_phase4fc1c.py` needed a separate repair and **arrived already failing**: 37
errors and 1 failure before this phase touched anything, because the C1C artifacts were handed over
under `reports/phase-4fc1c/` while the suite still pointed at the flat
`reports/priority-7-phase-4fc1c-*` paths its own summary records. Beyond re-pointing those two
constants, its `load_corpus` now reads the **pinned baseline** rather than the working tree — C1C
wrote nothing canonical, so at the time the two were the same document, and reading the immutable
one keeps every C1C claim about the corpus that was actually adjudicated. Its workspace-footprint
guards were scoped to C1C's own three artifacts for the same reason the C2 guard is prefix-based.

No assertion was deleted to make C2 pass. Where a claim was restated, it was restated as the thing
the phase actually established.

---

## 13. Validation — real C2 workspace

The workspace was **never committed**.

| Suite (§27) | Result |
|---|---|
| C2 (`test_priority7_phase4fc2.py`) | **106 passed** |
| C1C (`test_priority7_phase4fc1c.py`) | **73 passed** |
| B3B | **128 passed** |
| 4F-A | **74 passed** |
| 4E.1 | **97 passed** |
| 4E | **104 passed** |
| 5-A | **118 passed** |
| 4C | **57 passed** |
| 3D-1 | **44 passed** |
| 3F-A | **17 passed** |
| 2A | **77 passed** |
| **Full Python (`tests/`)** | **1111 passed, 0 failed** |
| **Full JXA (36 suites, `osascript -l JavaScript`)** | **36 suites, 0 failed** |
| `validate_content.py` | pass — forward baseline `2a71401d…1ce50`, 1675 ids |
| `verify_audio.py` | 3377 phrases / 3377 manifest entries / 3377 MP3s, nothing orphaned |
| `build_pages.py --check` | committed output current, 32 sitemap URLs |
| `validate-editorial` | `Priority 7 private editorial record: valid` |
| `git diff --check` | clean |

The runtime projector still fails closed with `PROJECTION_EMPTY`: nothing is approved, so there is
nothing it may publish, and the new examples did not make any pattern publishable. All 29 examples
nevertheless validate in the runtime shape the projector would emit, and `origin` is refused there
as an unknown field, confirming provenance stays private.

---

## 14. Committed-scratch survivability

A fresh isolated scratch repository was created by local clone of the complete C2 candidate, its
remote removed and `push.default` set to `nothing`. The candidate was committed **there only**.

| Check (scratch, C2 as HEAD) | Result |
|---|---|
| Commit | `74097dc8b8564325cab757e5641a3cd8ad4ede8a` |
| Tree | `80980cd847fb8697988ed9e341f370d4c4d625f7` |
| Remotes | **zero** |
| Working tree after commit | **clean** |
| `git diff --check HEAD^ HEAD` | clean |
| `git diff --name-only HEAD^ HEAD` | the 20 C2 candidate files, nothing else |
| C2 suite | **106 passed** |
| C1C suite | **73 passed** |
| B3B suite | **128 passed** |
| Full Python | **1111 passed, 0 failed** — identical to the real workspace |
| Full JXA | **36 suites, 0 failed** |
| `validate_content.py` / `verify_audio.py` / `build_pages.py --check` | pass |
| `validate-editorial` | valid |

C2's own guards stay meaningful once C2 is HEAD because every one of them reads the pinned baseline
SHA. The scratch run proves it behaviourally rather than by inspection: the same 106 assertions hold
with `HEAD` moved past the baseline, and the baseline blob is still not the working tree.

---

## 15. State at the end of C2

| Item | Value |
|---|---|
| Patterns | 45 |
| `reference-verified` | **45** |
| `editorial-reviewed` | **0** |
| `approved` | **0** |
| `reference-verification` accepts | **47** |
| `editorial-review` accepts | **0** |
| `product-approval` events | **0** |
| Canonical examples | **29** (18 repository-reuse, 11 editorial-generated, 0 original) |
| `authorRegistry` | **empty** |
| `editorialActorRegistry` | 2 nonhuman actors: `priority7-reference-analysis` (reference-verification), `priority7-example-generation` (example-generation) |
| `allocationRegistry` | **empty** |
| Runtime payload | **none** |

No editorial-review event was created. No product approval was performed. Nothing was frozen. The
next phase independently verifies the implemented corpus before any editorial-review event exists.

---

## 16. Residual risk

Unchanged in kind from C1C and recorded rather than resolved: **seven of the eleven final sentences
carry no native-speaker acceptance of any kind** — 018, 031, 032, 033, 035, 036, 043 — and four
carry AB's recorded Phase 4C acceptance of the *text* only, which is acceptance, never authorship.
The corpus states this truthfully: the sentences are `editorial-generated` by a named nonhuman
workflow, `authorRegistry` is empty, and no pattern claims a tier above `reference-verified`.

Two sentences sit marginally below the content-authoring specification's advisory word-count band
for their production level (`Opiekuję się chorą babcią.` and `Codziennie dbam o kondycję.` at four
orthographic words against a B1 guidance of six to eighteen). The band is Phase 1 guidance for a
future authoring subdivision, is not validator-enforced, and C1C assessed CEFR fit on every row
explicitly. Recorded here rather than silently overridden.

---

**Verdict: GO** — the locked C1C example decisions were implemented exactly, with truthful
provenance and stable identity; reference verification survives on all 45 patterns; canonical
boundaries hold; and the corpus is ready for final post-example editorial verification.
