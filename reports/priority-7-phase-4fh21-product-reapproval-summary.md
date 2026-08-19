# Priority 7 — Phase 4F-H2.1

## Product re-approval after H2 content completion

**Baseline commit:** `98cd258016564a381856d7b86cccf9e6402b458d`
**Baseline tree:** `1523e7e70edb5f7bcfecc8ec64e0841a47390e43`
**Phase date:** 2026-08-18
**Matrix:** `reports/priority-7-phase-4fh21-product-approval-matrix.csv`
**Tests:** `tests/test_priority7_phase4fh21.py`
**Normaliser:** `tests/priority7_phase4fh21_normalizer.py`

---

## 0. What this phase is

Phase 4F-H2 completed the learner-facing content and then deliberately stopped
one tier short of release. It left the 44 rows it changed at
`editorial-reviewed`, with their Phase 4F-F2 product approvals preserved but
honestly stale, precisely so the product owner could look at the corrected
material before anything derived `approved`.

On 2026-08-18, after reviewing the H2 learner-facing preview, the owner said:

> H2 approved.

This phase records that decision and **nothing else**. It appends exactly one
`product-approval` acceptance to each of the 44 changed patterns, bound to that
pattern's freshly recomputed *current* tier-3 scope digest, and moves those rows
to `approved`. It is governance-only: no learner-facing field, no example, no
provenance record, no registry identity and no shipping file moved.

---

## 1. Baseline confirmation

Recomputed independently from the baseline commit before any edit, not taken on
trust from the H2 report. Every figure matched.

| Finding | Expected | Reconfirmed |
| --- | --- | --- |
| Patterns | 45 | 45 |
| Examples | 45 | 45 (20 repository-reuse, 25 editorial-generated, 0 original) |
| `editorial-reviewed` | 44 | 44 |
| `approved` | 1 | 1 |
| The one approved row | the untouched pattern | `vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` |
| Correction accepts (2026-08-18) | 42 | 42 |
| `editorial-review` / changes-requested (2026-08-18) | 44 | 44 |
| Fresh `editorial-review` accepts (2026-08-18) | 44 | 44 |
| Product approvals after H2 | 0 | 0 |
| `reference-verification` accepts | 47 | 47 |
| `editorial-review` accepts (total) | 89 | 89 |
| `product-approval` accepts (total) | 45 | 45 |
| `reopen` events | 0 | 0 |
| Tier-1 digests current | 45 / 45 | 45 / 45 |
| Tier-2 digests current | 45 / 45 | 45 / 45 |
| Tier-3 digests current | 1 / 45 | 1 / 45 — the untouched row |
| Tier-3 digests stale | the same 44 | exactly the 44 H2 changed |

The stale-tier-3 set and the H2-changed set are the same 44 identities, and the
untouched pattern's tier-1, tier-2 **and** tier-3 acceptances all still cover its
current scope. The baseline was what H2 said it was, so the phase proceeded.

---

## 2. Product-owner authority

`product-owner-001`, the existing registry identity Phase 4F-F2 named. Nothing
about it changed:

* `human: true`;
* `roles: ["product-approval"]` — the same single role, not widened;
* `acknowledgedReleaseModes` still names `solo-maintainer-reference-backed`;
* `ownerAllowsMultipleRoles` still deliberately absent.

No reviewer was registered, no nonhuman actor was registered, and **no
correction, reopen or external-verification authority was created**. The
`reviewerRegistry`, `editorialActorRegistry`, `authorRegistry`, `sourceRegistry`
and `allocationRegistry` objects are byte-identical to the baseline;
`authorRegistry` stays empty.

Every new event carries `reviewerRef`, never `actorRef`: a product approval is a
human decision by construction and is structurally incapable of naming a model.
`native-reviewer-001` (AB) appears in no new event.

---

## 3. The exact 44 approvals

One event appended per changed pattern, all identical apart from the digest:

```json
{
  "kind": "product-approval",
  "decision": "accept",
  "scopeVersion": 1,
  "scopeDigest": "<this pattern's freshly recomputed tier-3 digest>",
  "reviewerRef": "product-owner-001",
  "reviewedAt": "2026-08-18",
  "note": "<the note below>"
}
```

The note, identical on all 44 and 239 characters against the schema's 240-character
limit:

> Product owner visually reviewed the corrected H2 learner content - completed
> examples, translated Polish illustrations - approved it 2026-08-18. Not a new
> linguistic, reference or native-speaker review. Audio deferred; UI wording
> separate.

It says what happened and no more. The owner looked at the corrected
learner-facing result — the completed examples and the English translations of
the Polish illustrations — and accepted it for product inclusion. It does not
claim the owner authored the Polish, and it does not claim any external
linguistic check: `approved` here means a human product decision over a treatment
whose two lower tiers were performed by the project's own nonhuman workflows.

Every digest was computed fresh from the live row through
`review_scope_digest("product-approval", …)`. **No stale H2 or F2 digest was
reused**: on all 44 rows the new digest differs from every digest already present
in that row's history, and the superseded 2026-08-17 approval is left in place,
still visibly stale. The full 44-row table, with each pattern's new digest beside
the digest it supersedes, is in the matrix.

The schema is the existing one exactly: seven keys, closed, no new field, no
`supportingEvidenceDigests`, no `corroboratingActorRefs`.

---

## 4. The untouched pattern

`vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` received
**no** new approval. Its row object is byte-identical to the baseline, it still
carries exactly one product approval (2026-08-17), and that approval still pins
its current tier-3 digest. A second approval there would have been a duplicate
acceptance of an unchanged scope — the tooling rejects it as
`REVIEW_DUPLICATE_STAGE_ACCEPTANCE`, and the test suite proves that it does.

That identity is outside the H2.1 allowlist entirely: `approved_h21_event` raises
`KeyError` for it, and the matrix never names it.

---

## 5. Final governance state

| State | Count |
| --- | --- |
| `approved` | **45** |
| everything else | 0 |

All 45 rows also *derive* `approved` from their own histories and live digests —
the recorded state is not merely asserted.

### Event ledger

| Event | H2 baseline | H2.1 added | Final |
| --- | --- | --- | --- |
| `reference-verification` / accept | 47 | **0** | 47 |
| `editorial-review` / accept | 89 | **0** | 89 |
| `editorial-review` / changes-requested | 44 | **0** | 44 |
| `correction` / accept | 42 | **0** | 42 |
| `product-approval` / accept | 45 | **+44** | **89** |
| `reopen` | 0 | **0** | 0 |

89 = 45 historical + 44 fresh, exactly as projected. The 44 appended approvals are
the only new events anywhere in the corpus; every pattern's prior history is a
byte-identical prefix of its new history, so the record is strictly append-only.
`releaseMode` stays `solo-maintainer-reference-backed` on all 45.

A freeze of the live corpus now admits all 45 patterns, where at the H2 baseline
it admitted exactly one. That is the intended consequence of the owner's
decision, and no freeze was performed in this phase.

---

## 6. Digest currency

| Tier | Scope | Digests moved from the H2 baseline | Current after H2.1 |
| --- | --- | --- | --- |
| 1 — `external-verification` | structure, complements, usage | **0 / 45** | 45 / 45 |
| 2 — `native-linguistic` | + CEFR, teaching status, explanation, examples, error notes | **0 / 45** | 45 / 45 |
| 3 — `product-approval` | + contentRefs | **0 / 45** | **45 / 45** |

Tier-3 *content* digests did not move either, and that is the point: a product
approval is an event recorded *over* the current scope, not a mutation of it. What
changed is that each of those 44 already-current tier-3 scopes is now accepted.
The 44 superseded approvals remain in the history and remain stale against those
same scopes; that staleness is preserved rather than rewritten.

---

## 7. Content immutability

The corpus is byte-identical to the H2 baseline apart from `reviewEvents` and
`reviewState`. Proved mechanically: stripping exactly those two keys from every
pattern in both documents makes them equal.

Unchanged on all 45 rows: pattern identities and keys, `relationType`,
`complements`, `usage`, `cefr`, `teachingStatus`, `learnerExplanationEn`,
`errorNotes`, `examples` (text, IDs, origin and provenance), `contentRefs`,
`activityEligibility`, `evidence`, `releaseMode`, and the lemma/meaning
scaffolding above them. The corpus envelope (`artifactStatus`, `formatVersion`)
is unchanged.

Examples remain **45 total — 20 repository-reuse, 25 editorial-generated, 0
original**. `authorRegistry` stays empty and `origin.kind = original` remains
unused.

---

## 8. Audio, UI and shipping invariants

* `activityEligibility` is `[]` on all 45 patterns.
* `audioEligible` is `true` on 0 of 45 examples — audio remains deferred.
* `audio-manifest.json`, every file under `audio/`, `pp_audio_rule.py`,
  `generate_audio.py` and `verify_audio.py` are byte-identical. No MP3 was
  synthesised.
* Every shipping file is byte-identical to the baseline: `index.html`, `sw.js`,
  `manifest.json`, `pp-verb-patterns.js`, `pp-usage.js`, `pp-answer.js`,
  `pp-distractor.js`, `pp-migrate.js`, `sitemap.xml`, every `data-*.js`,
  `validate_content.py`, `build_pages.py`, `priority7_tooling.py`, `robots.txt`,
  `CNAME`, every generated page under `grammar/`, `guide/` and `vocabulary/`.
* `APP_VERSION` stays `8.10`, the shell cache stays `popolsku-v65`, the audio
  cache stays `popolsku-audio`, `CONTENT_MIGRATION_REVISION` stays `2` and
  `schemaVersion` is untouched.
* The UI still says **"Verb Patterns"** and **"Understand this one"**. The
  capitalisation and label change is H3 and was not made here.
* `content/verb-patterns.json` does not exist, no `content/` directory exists,
  and the parked G2 workspace was not recreated. Nothing was frozen, released or
  projected to runtime.

---

## 9. Context record

Repository precedent is unambiguous: Phase 4F-A, 4F-C2, 4F-E1, 4F-F2 and 4F-H2
each appended one paragraph to `contextNotice` recording what the phase did to
the governance state, and Phase 4F-H2 explicitly wrote there that the corrected
content is **not** product-approved and that no new product-approval event was
created. H2.1 makes both of those statements false. Leaving the notice unchanged
would leave the private governance record actively wrong, so the precedent
requires an append here.

One paragraph was appended. It supersedes exactly those two statements, leaves
every other statement standing, and records: the owner's 2026-08-18 decision, the
44 approvals against freshly recomputed current tier-3 digests, the untouched
pattern's deliberate exclusion, 45/45 approved, the disclaimers (not a new
linguistic, reference or native-speaker review; the Polish was not authored or
externally verified by the owner), and the unchanged invariants (no registry
change, reopen still 0, activity empty, audio deferred, UI wording outstanding,
nothing frozen or released).

No historical notice text was modified — the live notice is the baseline notice
plus this suffix, byte for byte. No `reviewerRegistry` change was necessary and
none was made.

---

## 10. File footprint

Changed:

* `editorial/verb-pattern-candidates.json` — the 44 appended events and 44
  `reviewState` transitions.
* `editorial/priority-7-authoring-context.json` — one appended `contextNotice`
  paragraph. No registry gained, lost or altered an identity.

Added:

* `reports/priority-7-phase-4fh21-product-reapproval-summary.md` (this file)
* `reports/priority-7-phase-4fh21-product-approval-matrix.csv`
* `tests/test_priority7_phase4fh21.py`
* `tests/priority7_phase4fh21_normalizer.py`

Repaired to compose the H2.1 normaliser (§11): 17 historical suites. One of
those, `tests/test_priority7_phase4fc2d.py`, additionally names the new
normaliser in the dependency list its reconstructed clone copies, exactly as it
already names E1's, F2's and H2's.

Nothing outside `editorial/`, `reports/` and `tests/` was touched.

---

## 11. Historical test handling

H2.1 legitimately supersedes the `editorial-reviewed` state that Phase 4F-H2 —
and, through it, every earlier suite — was written about. That needed a
phase-aware repair, and the repair is the phase-owned normaliser
`tests/priority7_phase4fh21_normalizer.py`, composed **innermost**: H2.1 comes
off before H2's content completion, which comes off before F2's approvals, which
come off before E1's editorial review.

```python
E1.without_phase_4fe1_editorial_review(
    F2.without_phase_4ff2_product_approval(
        H2.without_phase_4fh2_content_completion(
            H21.without_phase_4fh21_product_reapproval(live_corpus))))
```

The normaliser is closed over exactly the 44 appended product-approval events and
the one appended context notice, and **derives nothing from the live rows**. For
each of 44 allow-listed identities it pins the complete acceptance object,
including a statically pinned tier-3 digest. A row is reverted only when it is at
exactly `approved`, the pinned event is present exactly once, and it is the
*last* event in the history. It imports only `copy` and `json`, opens no file,
runs no subprocess and computes no digest, and a test asserts all of that.

Each of the following therefore survives normalisation and still breaks the guard
it would otherwise hide behind, or is refused outright:

| Mutation | Caught by |
| --- | --- |
| One missing H2.1 approval | layer refused as `partial`; `REVIEW_STATE_MISMATCH` if the row still claims `approved` |
| Approval on the untouched pattern | `REVIEW_DUPLICATE_STAGE_ACCEPTANCE`; the extra event survives normalisation and stays visible |
| Duplicate new approval | `REVIEW_DUPLICATE_STAGE_ACCEPTANCE`; layer refused |
| Wrong `reviewerRef` | `REVIEWER_ROLE` / `REVIEWER_REGISTRY_DANGLING`; layer refused |
| `actorRef` instead of `reviewerRef` | `SCHEMA_REQUIRED` + `SCHEMA_UNKNOWN_FIELD`; layer refused |
| Wrong date (future / backdated / 2026-08-17) | `DATE_IN_FUTURE` / `REVIEW_EVENT_ORDER`; layer refused |
| Stale or repinned tier-3 digest | `REVIEW_STATE_MISMATCH`; layer refused |
| Changed note | layer refused |
| Approval ahead of editorial currency | derives `reference-verified`, `REVIEW_STATE_MISMATCH` |
| Example edited after the digest was computed | `REVIEW_STATE_MISMATCH` |
| `learnerExplanationEn` edited after the digest was computed | `REVIEW_STATE_MISMATCH`; survives into the H2 layer and breaks its pin |
| Extra reference-verification | validator issues; layer refused |
| Extra correction | layer refused |
| Reopen event | `REVIEW_REOPEN_ORDER`; layer refused |
| `audioEligible` change | `AUDIO_NOT_AUTHORIZED` |
| `activityEligibility` change | validator issues |
| Shipping / runtime materialisation | footprint and existence assertions |

A *missing* approval is the one defect a per-row pin cannot expose, because
removing an H2.1 event returns that row to a state Phase 4F-H2 legitimately
described. It is therefore refused at the layer rather than the row: the
normaliser raises when the corpus carries H2.1 on some but not all of the
allow-listed identities it contains. Every historical suite runs the normaliser,
so a partial H2.1 layer cannot pass anywhere.

No earlier expectation was weakened, no historical digest was repinned, and no
normalised value was read from a live row. Phase 4F-H2's own suite now states its
claims over the H2.1-normalised documents and keeps its on-disk claims — the
byte-for-byte normaliser round trip — against the raw files.

---

## 12. Validation

| Check | Result |
| --- | --- |
| `python3 -m unittest tests.test_priority7_phase4fh21` | 106 tests, OK |
| `python3 -m unittest tests.test_priority7_phase4fh2` | 92 tests, OK |
| `python3 -m unittest tests.test_priority7_phase4fg1` | 75 tests, OK |
| `python3 -m unittest tests.test_priority7_phase4ff2` | 99 tests, OK |
| `python3 -m unittest tests.test_priority7_phase4fe1` | 101 tests, OK |
| Full Python discovery (`tests/`), working tree | 1845 tests, OK |
| Full Python discovery (`tests/`), committed scratch | 1845 tests, OK |
| JXA suites (`osascript -l JavaScript`) | 36 files, 10544 assertions, 0 failures |
| `validate-editorial` (real private context, real repository index) | valid |
| `python3 validate_content.py` | OK — 10 levels, 97 topics, 1215 cards, 353 drills |
| `python3 verify_audio.py` | OK — 3377 phrases, 3377 manifest entries, 3377 MP3s |
| `python3 build_pages.py --check` | OK — committed output current, 32 sitemap URLs |
| `git diff --check` | clean |

The committed-state column above was produced in a disposable zero-remote
scratch clone whose single commit is the direct first descendant of the baseline
and whose tree reproduces byte for byte from an independent clone of the same
candidate. That scratch was clean, carried no remote, was never pushed, and was
deleted after validation. The real H2.1 workspace stays uncommitted.

`validate-runtime` was not run: no official runtime file exists in this phase and
none was created in order to run it. The known Phase 4F-C1C standalone-import
issue was left untouched.

---

## 13. What remains

* **H3** — the UI capitalisation and card-label change. Untouched here.
* **Audio** — still deferred. No pattern example is audio-eligible and no
  listening behaviour exists for Priority 7 content.
* **Activities** — `activityEligibility` is empty on all 45; no activity has been
  enabled.
* **Freeze / release / runtime projection** — none performed. All 45 patterns are
  now eligible for a freeze, but freezing, projecting `content/verb-patterns.json`
  and shipping remain separate, unperformed phases.

---

**Verdict: GO**

The 44 H2-changed patterns now carry fresh human product approval against their
current tier-3 scopes; the untouched pattern retains its existing current
approval; all 45 derive `approved`; no content, audio, UI or shipping state
changed.
