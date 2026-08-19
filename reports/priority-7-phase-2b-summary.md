# Priority 7 — Phase 2B Authoring Summary

**Phase:** 2B — 30-verb private editorial candidate authoring
**Outcome:** a complete, validating, private 30-lemma candidate corpus exists. **No record is
approved, no production baseline was frozen, no public runtime corpus exists, and no
learner-facing file changed.**
**Next-step status:** NO-GO for anything beyond independent review. Phase 2B is not
self-approving.

## 1. Safety baseline

All eight required checks passed before any work began, and none was relaxed.

| Check | Required | Verified |
|---|---|---|
| Branch | `priority-7-phase-2b-candidate-authoring` | matches |
| HEAD | `7e08fcb1eabfce12a706fded116d1dce598f8fa2` | matches |
| Tree | `9417acab477c3e87d6d4bee6de14b8a9e98061cc` | matches |
| Initial worktree | clean | clean |
| `git remote -v` | empty | empty |
| `git config --get push.default` | `nothing` | `nothing` |
| `_research/medak-verb-connectivity-source.pdf` | exists | exists (1,158,905 bytes) |
| `_research/` ignored, absent from status | true | ignored via `.git/info/exclude:8`; not in `git status` |

Underlying production baseline confirmed unchanged at the end of the phase: `APP_VERSION`
`8.10`, shell cache `popolsku-v65`, `AUDIO_CACHE` `popolsku-audio`, progress
`schemaVersion` `2`, `CONTENT_MIGRATION_REVISION` `2`.

## 2. Files created

| Path | Kind | Tracked? |
|---|---|---|
| `editorial/verb-pattern-candidates.json` | private editorial candidate corpus | untracked, uncommitted |
| `editorial/priority-7-authoring-context.json` | private source/reviewer/author/allocation registries required by the Phase 2A validator | untracked, uncommitted |
| `reports/priority-7-phase-2b-source-evidence-audit.md` | Phase 2B report | untracked, uncommitted |
| `reports/priority-7-phase-2b-pilot-coverage.md` | Phase 2B report | untracked, uncommitted |
| `reports/priority-7-phase-2b-native-review-queue.md` | Phase 2B report | untracked, uncommitted |
| `reports/priority-7-phase-2b-summary.md` | this report | untracked, uncommitted |

**One tracked file was modified**, in the post-review correction pass:
`tests/test_priority7_phase2a.py`, to replace a Phase 2A-era assertion with a Phase 2B-aware
privacy invariant (§13). `priority7_tooling.py`, every Phase 1 specification, and every
application, content, service-worker, audio, generated-page, migration and version file
remain **unchanged**.

## 3. Candidate artifact

`editorial/verb-pattern-candidates.json` carries exactly the Phase 1 editorial envelope:

```json
{ "artifactStatus": "priority-7-editorial-nonproduction", "formatVersion": 1, "lemmas": [ … ] }
```

No `patternDataRevision` field exists. `content/verb-patterns.json` was **not** created.

**Coverage:** 30 lemmas (all 30 requested, in the requested order, no substitutions, no
additions), 34 meanings, 45 patterns, 54 complements, 23 examples, 122 evidence records,
101 typed content references, 24 error notes, 132 unique stable IDs.

Full breakdowns are in
[`priority-7-phase-2b-pilot-coverage.md`](priority-7-phase-2b-pilot-coverage.md).

## 4. Authoring methodology

1. Read every Phase 0, Phase 1 and Phase 2A report, `priority7_tooling.py` and
   `tests/test_priority7_phase2a.py` before authoring anything.
2. Established Mędak headword presence from the Phase 0 rights-safe artifacts; located and
   read the demo's detailed sample entries for the three pilot lemmas inside the 1–50 range.
3. Consulted the contemporary reference (WSJP PAN) sense by sense for all 30 lemmas and
   recorded the `Składnia` schema class, never the prose.
4. Surveyed the current app corpus read-only for every lemma to find existing cards, drills,
   lessons and exact reusable sentences.
5. Authored a compact declarative spec and generated the JSON with IDs allocated by
   `priority7_tooling.allocate_*`. No ID was typed by hand.
6. Validated after each of the six prescribed batches (1–5, 6–10, 11–15, 16–20, 21–25,
   26–30). Every batch validated clean before the next was authored.
7. Ran a negative control mid-way to confirm the validator was genuinely checking.
8. Ran the diagnostic nonrelease projection and every existing regression suite.

**Selection principle:** one to three high-value patterns per lemma, chosen for everyday
usefulness at A1–B1 and for structural importance to case learning — not dictionary
completeness. `mieć` gets 1 of 19 contemporary senses; `być` gets 1 of 8. Every deliberate
omission is listed in the review queue rather than parked as a hidden record, which is why
the corpus contains **zero** `deferred` patterns.

## 5. Source methodology and copyright safeguards

Four separated source identities, with the Mędak split enforced by the validator:

| `sourceId` | Kind | May support |
|---|---|---|
| `repository` | repository | what the app currently teaches |
| `medak-2011-headword-index` | medak-research, `detailedEntryReviewed: false` | `factType: lemma` only |
| `medak-2011-detailed-entry` | medak-research, `detailedEntryReviewed: true` | `complement-frame`, for the 3 entries actually read |
| `wsjp-pan` | contemporary-reference | sense boundaries and `Składnia` schema class |

`MEDAK_DETAIL_NOT_ESTABLISHED` mechanically rejects any non-`lemma` fact attributed to a
headword-only registry entry, so "the book lists this verb" can never silently become
"the book supports this case".

Safeguards applied:

- The PDF stayed untracked in `_research/`; it was not modified, copied or committed.
- No headword list, definition, entry prose, synonym set or example sentence from Mędak or
  WSJP appears anywhere in the corpus or in any report.
- No dictionary example was copied, paraphrased, translated-and-rewritten, or reconstructed.
- Evidence stores only source ID, locator, fact type, date and a short internal note
  (≤ 240 characters).
- No endorsement by the author, the publisher, or PAN is stated or implied.
- All 23 corpus examples are exact reuses of pre-existing Po polsku sentences; the 22 draft
  sentences in the review queue were composed from the abstract grammatical fact alone.

## 6. Contemporary verification methodology and coverage

Every one of the 45 patterns carries at least one contemporary WSJP evidence record naming
the exact entry, the exact numbered sense, and the exact section consulted. Those 46 records
resolve to 44 locator strings over 34 distinct numbered senses across the 30 lemmas.
**Consultation coverage is 45/45.**

That is deliberately *not* stated as "45/45 verified syntax". Classified against the cited
formal `Składnia` lists:

| Class | Meaning | Patterns |
|---|---|---:|
| A | authored frame corresponds to a complete listed schema (or its minimal realisation where the dropped slots are optional in that schema) | **40** |
| B | the slot is listed, but every schema containing it also carries a further non-optional participant the pilot drops for teaching reasons | **3** |
| C | the complete combined realisation is in neither the formal syntax list nor the collocation section | **1** |
| D | the authored frame adds a slot the schema does not name; that slot is the editor's analysis | **1** |

So **40 of 45 authored frames map onto a verbatim contemporary schema, and 5 carry an
explicit recorded gap**. Class B is `pomagać` + Dat, `dziękować` + `za` + Acc and `pytać` +
`o` + Acc; class C is `prosić KOGO + o CO`; class D is `podobać się`. Full detail and the
exact per-section provenance of the `prosić` candidate are in the source-evidence audit §2
and §4.1.

This is *evidence gathering*, not the `external-verification` review stage. That stage
requires a named human and cannot be performed by an agent, so no
`external-verification` event exists.

**Gap:** no `contemporary-corpus` evidence was gathered. Frequency, register and
competition-between-constructions claims therefore rest on editorial judgment, which
Phase 1 §8 says corpus evidence should support. This is recorded as an open gap, not
papered over.

## 7. ID results

- Families used: `vp-l-*` (30), `vp-m-*` (34), `vp-p-*` (45), `vp-e-*` (23). No `vp-x-*`
  exercise ID was allocated — Phase 1 does not require candidate activity items at this
  stage, and allocating speculative identities would be waste.
- 132 IDs, all globally unique, no duplicates.
- Every ID recomputes exactly from `allocate_lemma_id` / `allocate_meaning_id` /
  `allocate_pattern_id` / `allocate_example_id`, verified independently of the validator.
- Rebuilding the artifact from the spec produced a **byte-identical** file.
- Keys encode durable structure (`genitive-target`, `instrumental-method`,
  `dative-experiencer-na-locative`), never English wording.
- Lexical `się` participates in identity: `uczyć się` slugs to `uczyc-sie` and could never
  collide with `uczyć`.

## 8. Validation results

```text
python3 priority7_tooling.py validate-editorial \
  editorial/verb-pattern-candidates.json \
  --context editorial/priority-7-authoring-context.json \
  --repository-root .
→ Priority 7 private editorial record: valid
```

Batch-by-batch (each validated before the next batch was authored):

| Batch | Lemmas | Meanings | Patterns | Examples | Result |
|---|---:|---:|---:|---:|---|
| 1 (1–5) | 5 | 6 | 7 | 4 | valid |
| 2 (6–10) | 10 | 11 | 16 | 12 | valid |
| 3 (11–15) | 15 | 17 | 24 | 16 | valid |
| 4 (16–20) | 20 | 22 | 32 | 20 | valid |
| 5 (21–25) | 25 | 27 | 37 | 24 | valid |
| 6 (26–30) | 30 | 35 | 45 | 24 | valid |

After the post-review correction pass the whole corpus was rebuilt and revalidated:
**30 lemmas, 34 meanings, 45 patterns, 23 examples — valid.**

**Negative control.** Mutating one reused sentence and one pattern ID produced exactly the
expected refusals, proving the pass is meaningful:

```text
REPOSITORY_SOURCE_MISMATCH  $.lemmas[0]…examples[0]: Example text is not exactly equal to the referenced repository field.
ID_RECOMPUTATION            $.lemmas[1]…patterns[0].id: Pattern ID must recompute exactly as 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81'.
```

**Diagnostic nonrelease projection** (run for diagnosis only; its output is not a deployable
corpus and no file was written):

```text
python3 priority7_tooling.py project-fixture … → exit 1
PROJECTION_EMPTY $.lemmas: No current approved active/recognition pattern can be projected.
```

This is the correct fail-closed result: with zero approved patterns, nothing is projectable.
It is direct evidence that no public runtime corpus can be derived from this data in its
current state. The Phase 2A frozen-release machinery (`freeze_editorial`,
`validate_frozen_release`, `verified_runtime_from_frozen`) was **not** invoked.

Committed Phase 1 fixture still validates:
`python3 priority7_tooling.py validate-specification reports/priority-7-pattern-schema.example.json`
→ valid.

## 9. Repository-reuse results

- 23 examples, all `origin.kind: repository-reuse`, each resolving to a card `ex` field.
- Validator enforces byte-exact equality against the parsed repository field. No sentence
  was altered to qualify.
- Drill reuse was evaluated and rejected: scalar `choose` answers are single words and
  `build` answers are token arrays, so neither yields a complete sentence. This matches the
  Phase 2A finding about the 68 build drills.
- 101 typed `contentRefs` resolve by both ID and kind: 73 support, 17 practice, 11 contrast.
- 22 patterns carry no example — see the blocker in §11.

## 10. Research and review status

All 45 patterns: `reviewState: research`, `reviewEvents: []`, `activityEligibility: []`.

- **No** external-verification, native-linguistic or product-approval event was created.
- **No** reviewer or author identity was invented; `reviewerRegistry` and `authorRegistry`
  in the private context are deliberately empty.
- **No** acceptance scope digest was computed or stored.
- **No** pattern is `approved`.
- `activityEligibility` is empty on every pattern, which is the only value the validator
  permits below `approved` (`UNAPPROVED_ACTIVITY`). Proposed post-approval eligibility is
  recorded in the review queue as a question, not as data.
- `audioEligible` is `false` on all 23 examples. No audio was generated, requested or
  inventoried.
- Zero `aspectPartnerIds` and zero `aspectEquivalentPatternIds`: reciprocal links require a
  current external-or-later review on both sides (`ASPECT_LINK_UNREVIEWED`), which no
  research record can have. Free-text repository `pair` strings were not promoted.

## 11. Unresolved issues discovered in this phase

### 11.1 Blocker — no example-author authority exists (governance, not linguistics)

Phase 1 requires `origin.kind: original` examples to carry an `authorRef` resolving to a
private author-registry record with `human: true`
(`priority7_tooling.py:906`–`913`, codes `AUTHOR_REGISTRY_DANGLING` / `AUTHOR_NOT_HUMAN`). The
Phase 2A/2B readiness checklist lists approved "authoring ownership" as a Phase 2B
prerequisite, and no such authority was named in the Phase 2B authorisation.

Claude is the drafting agent, not a human author. Fabricating an author record would forge
provenance in a system whose entire purpose is provenance integrity. Therefore:

- no `original` example was written into the corpus;
- 22 draft Polish sentences were written and placed in the native-review queue instead,
  where a named human author can adopt or replace them;
- the corpus is fully valid without them, because examples are optional in research records
  and no activity is eligible.

**To unblock:** name an example-authoring authority, add one author-registry record, and the
22 drafts can be moved into the corpus in a single mechanical step.

### 11.2 Two constructions the locked model cannot represent

Both were left **out of corpus** rather than forced into a wrong shape:

1. **`czekać, aż …`** — the contemporary reference lists `aż` as a core clause frame; the
   closed `clauseKind` enum is `ze | czy | zeby | interrogative`. Encoding it as `zeby`
   would be false.
2. **`mówić po polsku`** — `po polsku` is an adverbial, not preposition + inflected case,
   and the complement taxonomy has no adverbial slot. The `mówić` meaning scope explicitly
   excludes it.

Classification of both: **unresolved linguistic modelling within an intentionally closed
taxonomy** — not bad candidate data and not a tooling defect. Phase 1 chose a small closed
model knowing it would exclude some constructions (the `to jest` boundary is the same
decision). Whether to widen the taxonomy is a Phase 1 specification question, raised as
NRQ-14 and NRQ-06.

### 11.3 Phase 1 boundary cases: how each was resolved

| Fixture | Resolution | Confidence |
|---|---|---|
| `płacić` | Two patterns: `za` + Acc lexical frame for the goods; bare Ins typed **`means-method`** for the method, so no "always takes Instrumental" claim is possible | wording needs review (NRQ-01) |
| `być` | Exactly one pattern, Ins predicate, typed **`constructional-frame`**. `to jest` produced **no** record; the Nominative grammar topic is linked as a typed `contrast` reference | boundary respected as specified |
| `podobać się` | **`subject-experiencer`** with Nom subject + Dat experiencer; held **recognition-only** because reversed-mapping production is error-prone at A2 | production level open (NRQ-04) |
| `zależeć` | Two meanings. `od` + Gen is a normal lexical frame. `komuś na czymś` has a Dat experiencer but **no subject**, so it is typed `lexical-frame` with an `experiencer` role — `subject-experiencer` would have been wrong, and the validator would have rejected it for lacking a `subject` role | typing sound, wording open (NRQ-05) |

### 11.4 Other open linguistic questions

`czekać` bare Genitive (2011 vs contemporary); `tęsknić do` alternant; the `nie lubię`
presentation inherited from Phase 0; whether `słuchać`, `zajmować się` and `wierzyć` are
correctly split into two meanings; whether `prosić`/`pytać` two-complement patterns are
production-ready; every CEFR, teaching status and priority value; all 24 predicted
distractors; every aspect pairing. Full detail with reviewer context is in the review queue
(NRQ-01 … NRQ-16).

### 11.5 No Phase 1/2A modelling blocker attributable to the tooling

No validator rule was found to be wrong, and no change to `priority7_tooling.py` was needed
or made. Every refusal encountered during authoring was the validator correctly rejecting
data that would have overclaimed.

## 11.6 Corrections applied after independent review

Independent review returned three content defects and one obsolete test assertion. All four
were corrected in a focused pass; no new lemma, meaning or pattern was invented, no CEFR,
register or teaching status was changed, and no open question was silently closed.

| # | Defect | Correction | Consequence |
|---|---|---|---|
| 1 | `lubić`: one meaning `like-entity` spanned the contemporary people sense and thing/activity sense; the Accusative pattern cited the people sense while its example and sibling infinitive pattern belonged to the other | One meaning keyed `enjoy-thing-or-activity`, both patterns citing the single thing/activity sense whose `Składnia` lists `CO` and `BEZOKOLICZNIK` together; glosses, scope and Accusative wording updated; people sense explicitly excluded and raised as NRQ-17 | meaning/pattern/example IDs recomputed |
| 2 | `wierzyć`: `believe-in` combined several contemporary senses under one scope, cited the truth/existence sense, and illustrated with `wierzę w siebie` (a third sense) | Both frames placed under one meaning keyed `have-trust`, citing the trust sense whose `Składnia` lists **both** `KOMU/CZEMU` and `w KOGO/CO`; wording changed to `wierzę w tego lekarza`; the truth, self-confidence, ideological and religious senses explicitly excluded and raised as NRQ-18 | 2 meanings → 1; meaning/pattern IDs recomputed |
| 3 | `myśleć`: the reused sentence `Co o tym myślisz?` realises the opinion sense the meaning excludes | Example withdrawn; the card re-typed `purpose: contrast` with a `factType: contrast` evidence record explaining why; draft B-22 added to the review queue; the `full`-field provenance enum was **not** widened | 24 examples → 23 |
| 4 | Phase 2A test asserted `editorial/` must not exist | Replaced with a stricter Phase 2B-aware privacy invariant — see §13 | 1 tracked file changed |

Both WSJP senses behind corrections 1 and 2 were **re-fetched during the correction pass**
specifically to confirm that one numbered sense licenses every frame now attributed to it.
Neither merge invents a broader sense: each rests on *one* contemporary sense where the
previous version implied two, so the attribution is narrower than before.

Because nothing has been released, the incorrect pre-release IDs were **not** preserved. All
affected identities were recomputed through `priority7_tooling.py` and re-verified.

A related reporting error was also corrected: the earlier summary claimed every pattern
carried repository evidence. Three recognition-only second-sense patterns
(`bać się` + `o` + Acc, `wierzyć` + `w` + Acc, `zajmować się` for a person) have none,
because the current app corpus contains nothing for them. Repository evidence covers 42 of
45 patterns.

## 11.7 Final source-precision pass

A second independent review found four provenance defects. All were corrected as
**evidence-only** changes; no pattern was deleted, no frame was redesigned, and no review
state moved.

| # | Defect | Correction |
|---|---|---|
| 1 | `widzieć` cited sense `4938155` ("kolegę"), the separately numbered encounter/meet sense | now cites `4938152` ("dziurę"), the visual-perception sense whose `Składnia` gives `KOGO/CO`; `internalScope` narrowed accordingly |
| 2 | `zależeć` (depend-on) cited sense `3938839` ("ktoś od kogoś"), the personal-dependency sense | now cites `3938838` ("coś od czegoś"), which gives `od CZEGO`; `internalScope` narrowed to a thing or circumstance |
| 3 | `interesować się` cited sense `4723956` ("sytuacją") | now cites `4723955` ("muzyką"), the hobbies-and-interests sense, same bare `CZYM` frame; `internalScope` narrowed |
| 4 | `prosić KOGO + o CO` claimed `Składnia, o CO plus personal object` | split into two section-exact records: `Składnia` establishes `o CO` and a bare `CO` slot and explicitly does **not** encode the combination; `Połączenia` attests human Accusative objects but explicitly does **not** attest them combined with an `o` phrase; the repository record states the combined frame stays a research candidate |

Each replacement sense page was fetched during this pass and its `Składnia` transcribed
before the locator was changed. Four further notes were tightened where they credited
`Składnia` with an editorial judgment (`pomagać`, `dziękować`, `pytać`, `podobać się`) or
characterised an alternant the source does not characterise (`myśleć`).

**Identity stability was the acceptance test:** every ID was captured before the rebuild and
compared after. All **132** lemma/meaning/pattern/example IDs are byte-identical, which is
the expected result for evidence-only edits and confirms no key or canonical form moved.

### Re-audit of all 45 WSJP records

Because three wrong sense identifiers had reached this stage, a mechanical audit was run
across the whole corpus against a transcript of every `Składnia` list actually fetched in
Phase 2B. It asserts each cited sense exists in that transcript, that no sense is cited which
was never fetched, and that no `Połączenia`-sourced fact is credited to `Składnia`.

- 45 patterns, 34 distinct senses, all present in the verified transcript, none unused;
- section-attribution check: pass;
- **no further mismatch found**; no pattern required a linguistic or model change.

One earlier gap was closed in passing: `bać się` sense `5056329` had been cited from a
search summary without a direct page fetch. It was fetched and confirmed —
`bać się + o KOGO/CO`, worrying about future harm — so the existing record stands unchanged.

Three native-review questions were added (NRQ-20 `widzieć` example ambiguity, NRQ-21
`prosić` combined frame, NRQ-22 the three class-B one-slot patterns).

## 12. Native review requirement

Nothing authored here is linguistically approved. Claude-authored Polish and Claude-selected
structure are drafts. `reports/priority-7-phase-2b-native-review-queue.md` is written for a
native reviewer and covers: 22 targeted structural questions, 22 draft sentences, 23 reuse
confirmations, a 45-row level/status pass, and a list of 24 deliberate omissions to confirm.
It explicitly asks the reviewer **not** to rubber-stamp the corpus.

Native review remains a hard gate. After it, a named external verifier and a named product
authority are still required before any record can reach a learner.

## 13. Deployment isolation

Direct evidence that the editorial path is not publicly discoverable:

- The strings `editorial/`, `verb-pattern-candidates` and `priority-7-authoring-context`
  appear **only** in `tests/test_priority7_phase2a.py` and in Phase 1/2A specification
  reports. They appear in no HTML, CSS, JS, service worker, sitemap, manifest, generated
  page, build script, audio tool or data file.
- `data-*.js` glob still resolves to exactly the seven existing files.
- `index.html` still loads exactly the same eleven scripts.
- `sitemap.xml` still lists 32 URLs.
- `content/verb-patterns.json` does not exist.
- Generated output has zero drift; no generated directory contains the editorial artifact.

Phase 2A deployment-isolation suite, run test by test — **all five pass**:

| Test | Result |
|---|---|
| `test_private_editorial_workspace_is_local_only_and_never_published` | **PASS** (new) |
| `test_fixture_cannot_enter_data_or_audio_discovery_globs` | **PASS** |
| `test_app_service_worker_sitemap_and_generated_outputs_exclude_private_paths` | **PASS** |
| `test_generator_outputs_remain_current_and_owned_directories_contain_no_fixture` | **PASS** |
| `test_protected_application_surface_matches_untouched_production_baseline` | **PASS** (unchanged) |

### The Phase 2A → 2B invariant transition

The original Phase 2B pass reported one failure:
`test_no_committed_priority7_editorial_or_runtime_asset_exists`, which asserted
`assertFalse((ROOT / "editorial").exists())`. That was a Phase 2A-era invariant written when
no editorial artifact was permitted to exist anywhere. It could not distinguish
*existing locally in the isolated authoring workspace* from *authorised for public transfer*,
which are not the same thing.

Independent review authorised replacing it. `tests/test_priority7_phase2a.py` is the **only**
tracked file changed in this phase, and the replacement is **stricter**, not weaker:

**Removed** — a single existence check that Phase 2B authorisation supersedes.

**Added** — `test_private_editorial_workspace_is_local_only_and_never_published`, which:

1. permits `editorial/` to exist locally, but asserts its file set is **exactly**
   `{verb-pattern-candidates.json, priority-7-authoring-context.json}` — any other file
   appearing under it, now or later, fails closed;
2. keeps asserting `content/verb-patterns.json` does not exist;
3. keeps asserting the other private path markers do not exist;
4. still passes if `editorial/` is absent, so a future phase that removes it is unaffected.

**Strengthened** — `PRIVATE_PATH_MARKERS` now also covers
`editorial/priority-7-authoring-context.json`, and a new `PRIVATE_PATH_PREFIXES = ("editorial/",)`
is asserted absent from the combined browser-facing text (`index.html`, `sw.js`,
`sitemap.xml` and every generated page). The prefix check means a future private file
*renamed* inside the workspace still cannot leak by escaping the explicit marker list.

**Unchanged** — the protected-application-surface `git diff` comparison against the
production baseline `f6bdc73a…`, and every other public-surface assertion.

Both new assertions were negative-controlled and confirmed to fail closed:

```text
stray file editorial/leaked-notes.json  → AssertionError: … must contain exactly the
                                          authorised Phase 2B files …
content/verb-patterns.json created      → AssertionError: True is not false
```

Both controls were reverted immediately; the workspace holds exactly the two authorised
files. No production transfer mechanism was created in this phase.

## 14. Existing-application regression results

| Suite | Result |
|---|---|
| `validate_content.py` | **PASS** — 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs; forward baseline 1,675 ids / 13,387 wording / 1,312 policy / 1,777 structure, sha256 `2a71401d…a3a1ce50` — identical to the Phase 2A baseline |
| `verify_audio.py` | **PASS** — 3,377 required phrases = 3,377 manifest entries = 3,377 MP3s; nothing missing or orphaned |
| `build_pages.py --check` | **PASS** — committed output current; 23 grammar + 6 vocabulary pages + guide hub; 32 sitemap URLs; 380 pronunciation-bearing strings |
| `priority7_tooling.py validate-specification` | **PASS** |
| `tests.test_priority7_phase2a` | **76 tests, 76 pass, 0 fail** |
| Full Python discovery (`unittest discover -s tests`) | **251 tests, 251 pass, 0 fail** |
| JavaScript/JXA (`osascript -l JavaScript tests/*.js`) | **PASS** — 32 suites, 9,670 assertions passed, 0 failed |

Every count matches the Phase 2A baseline exactly, and the suite totals are unchanged (76 and
251) because one test was replaced, not added or removed. No snapshot, expected count or
unrelated test was updated. The Python runs emitted the same pre-existing unclosed-file
`ResourceWarning`s as in Phase 2A; no exit code was affected.

## 15. Final git scope

```text
$ git status --short
 M tests/test_priority7_phase2a.py
?? editorial/
?? reports/priority-7-phase-2b-native-review-queue.md
?? reports/priority-7-phase-2b-pilot-coverage.md
?? reports/priority-7-phase-2b-source-evidence-audit.md
?? reports/priority-7-phase-2b-summary.md

$ git diff --stat
 tests/test_priority7_phase2a.py | 51 +++++++++++++++++++++++++++++++++++++++--
 1 file changed, 49 insertions(+), 2 deletions(-)

$ git diff --name-only
tests/test_priority7_phase2a.py

$ git ls-files --others --exclude-standard
editorial/priority-7-authoring-context.json
editorial/verb-pattern-candidates.json
reports/priority-7-phase-2b-native-review-queue.md
reports/priority-7-phase-2b-pilot-coverage.md
reports/priority-7-phase-2b-source-evidence-audit.md
reports/priority-7-phase-2b-summary.md
```

One tracked file modified — the Phase 2A deployment-isolation test, by explicit review
authorisation (§13). Six untracked files: the private editorial artifact, the private
authoring context the validator requires, and four Phase 2B reports. Nothing else.

Confirmed unchanged: every existing card, drill, grammar topic, conversation, podcast, HTML,
CSS, JS runtime, service worker, audio file, audio manifest, generated page, migration
script and progress-handling file. `APP_VERSION` `8.10`; shell cache `popolsku-v65`;
`AUDIO_CACHE` `popolsku-audio`; `schemaVersion` `2`; `CONTENT_MIGRATION_REVISION` `2`.
Zero remotes. `push.default=nothing`. **No commit. No push.**

## 16. Explicit end-of-phase confirmations

- **No pattern is approved.** All 45 are `reviewState: research` with zero review events.
- **No frozen production baseline was created.** `freeze_editorial` was never called.
- **No public runtime corpus exists.** `content/verb-patterns.json` was not created, and the
  diagnostic projection refused with `PROJECTION_EMPTY`.
- **No learner-facing file changed.** Zero tracked files were modified.
- **No audio, progress, migration, UI, service-worker entry or runtime revision** was
  created or altered.
- **No reviewer or author identity was fabricated**, and no acceptance digest was
  manufactured to simulate approval.
- **Phase 2A tooling and tests were not modified.**

## 17. Recommended next steps (not authorised by this phase)

1. Independent review of this phase's four reports and the candidate artifact.
2. Owner decision on the example-author authority blocker (§11.1) — one registry record
   unblocks 21 examples.
3. Owner decision on the two unrepresentable constructions (§11.2) — widen the Phase 1
   taxonomy, or accept the omissions. These remain deliberately unsolved.
4. Only then: appoint the named external verifier, native reviewer and product authority
   that Phase 1 requires before any candidate advances beyond `research`.
