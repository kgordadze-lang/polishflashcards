# Priority 7 Phase 4F-E1 — Final Editorial-Review Governance Advancement

Baseline `5aef7e4a447b57f862dabf098b575a431f5f8484`
(tree `2dc8d799d5dd22056139abee629a8f98907932ac`).

This phase performed **no content review**. The substantive final editorial
review was completed by Phases 4F-D1, 4F-D2, 4F-D3 and 4F-D3.1 and is already
persisted in this repository. Phase 4F-E1 records the governance events that
make the completed review visible to the tooling, and nothing else.

All 45 patterns move from `reference-verified` to `editorial-reviewed`.
Nothing was product-approved, frozen, released or projected to runtime.

## The governance contract, as found

The repository already defined this stage in full. It was read out of
`priority7_tooling.py` before anything was written, and **the tooling was not
changed**.

| Question | What the repository actually says |
|---|---|
| Chain for `solo-maintainer-reference-backed` | `SOLO_STAGE_KINDS` — `reference-verification` → `editorial-review` → `product-approval` |
| Who performs `editorial-review` | A **nonhuman actor**. `MODE_NONHUMAN_STAGE_KINDS` makes the stage actor-borne in both release modes, so the event carries `actorRef` and is structurally incapable of naming a human `reviewerRef` |
| Where the actor lives | `editorialActorRegistry` in the authoring context, resolved by `_validate_editorial_actor`, which requires `human: false` and refuses any role outside `EDITORIAL_ACTOR_ROLES` |
| Required actor role | The stage name itself: `editorial-review` |
| Corroboration | `corroboratingActorRefs` **on the event**, required and non-empty on every acceptance (`EDITORIAL_CORROBORATION_REQUIRED`), sorted and unique, and never containing the accepting actor (`EDITORIAL_CORROBORATION_SELF`). Each corroborator must itself resolve as a nonhuman actor holding the `editorial-review` role |
| Corroboration is per-event | Yes. It is recorded on each acceptance, not registered once |
| Independence | `_replay_actor_independence` refuses any identity that is both a reference actor and an editorial actor or corroborator anywhere in a pattern's history |
| Digest scope | `STAGE_SCOPE_TIER["editorial-review"] == "native-linguistic"` — tier 2. `scopeVersion` stays `1` |
| Transition rule | `_derive_review_currency`: tier 2 becomes current only if tier 1 is current **and** the acceptance pins the current tier-2 digest. `_replay_review_order` additionally requires the preceding `reference-verification` acceptance and rejects a repeated acceptance of the same scope |
| One actor for all 45? | Permitted. No per-actor cap exists; the multi-role restriction applies only to human `reviewerRef` |
| One corroborator for all 45? | Permitted, on the same terms |
| `supportingEvidenceDigests` | **Forbidden** here — allowed only on an accepted tier-1 verification |

The architecture supported this phase without modification. `priority7_tooling.py`
is byte-identical to the baseline.

## Actors registered

Two nonhuman actors were added to `editorialActorRegistry`. Both state
`human: false` and hold `["editorial-review"]` and nothing else.

| Actor | Role | What it truthfully records |
|---|---|---|
| `priority7-editorial-review` | `editorial-review` | The tier-2 editorial review of the learner-facing treatment — the Phase 4F-D1 primary pass |
| `priority7-editorial-corroboration` | `editorial-review` | The independent blind second pass — Phase 4F-D2 |

Independence holds in substance, not just in form:

```
priority7-reference-analysis    ≠  priority7-editorial-review
priority7-editorial-review      ≠  priority7-editorial-corroboration
priority7-example-generation    ∉  {editorial actor, corroborator}
```

`priority7-example-generation` holds only the `example-generation` role, so it
is structurally incapable of appearing at this tier.

**No human identity was invented.** `authorRegistry` stays empty.
`reviewerRegistry` still holds exactly AB (`native-reviewer-001`), unchanged,
with no new event and no new authority. AB's Phase 4C native review remains
supplementary evidence and is not the basis of any event created here. The
product owner is not named anywhere in this phase and remains reserved for
product approval.

`editorial-reviewed` means: **two independent nonhuman editorial passes agreed
on the learner-facing treatment against the current tier-2 scope digest.** It
does not mean native-speaker review, professional linguistic review, or any
human review.

## Events created

Exactly one `editorial-review` acceptance per pattern — 45 in total.

```json
{
  "kind": "editorial-review",
  "decision": "accept",
  "scopeVersion": 1,
  "scopeDigest": "<current tier-2 digest of this pattern>",
  "actorRef": "priority7-editorial-review",
  "corroboratingActorRefs": ["priority7-editorial-corroboration"],
  "reviewedAt": "2026-08-17",
  "note": "…"
}
```

Four rows additionally carry a `findings` entry, because the blind D2 pass
raised a blocking finding on them. Each is recorded `severity: high`,
`resolved: true`, with a `resolutionNote` stating how the D3 adjudication
disposed of it. The 41 rows the two passes agreed on carry none, and no
acceptance carries an unresolved blocking finding.

| Review | D2 blocker | D3 | Recorded resolution |
|---|---|---|---|
| `P7-NR-011` | English example a literal gloss | **overturned** | Row stands exactly as authored |
| `P7-NR-018` | `look after my fitness` non-idiomatic | upheld | D3.1 set `examples[0].en` |
| `P7-NR-028` | reused English drifted from its card | upheld, card edit rejected | D3.1 realigned the canonical copy to card `a1-free-time-003` |
| `P7-NR-037` | marked clitic order in the positive model | upheld | D3.1 replaced the model in exactly two fields |

## Digests

Every acceptance binds to the pattern's **current** post-D3.1 tier-2 digest,
recomputed with `review_scope_digest`. No D1/D2-era digest was reused.

| Scope tier | Rows whose digest differs from the pre-D3.1 corpus |
|---|---|
| tier-1 — `reference-verification` | **0 of 45** |
| tier-2 — `editorial-review` | **3 of 45** — `P7-NR-018`, `P7-NR-028`, `P7-NR-037` |

Because tier 1 did not move, no reference-verification event was created,
altered or invalidated.

## Counts after this phase

| | |
|---|---|
| patterns | 45 |
| canonical examples | 29 |
| `reference-verification` events | 47 (45 current + 2 historical superseded) |
| `reference-verification` acceptances | 47 |
| `editorial-review` acceptances | **45** |
| `reviewState: editorial-reviewed` | **45** |
| `product-approval` events | **0** |
| `reviewState: approved` | **0** |
| canonical learner-content changes | **0** |
| runtime / shipping file changes | **0** |
| `patternDataRevision` increments | 0 |
| freeze / release / runtime projections | 0 |

The two known stale `mówić` reference events remain in history exactly as they
were. Their later current-digest acceptances remain the active reference basis.

## Content

Governance-only. Outside `reviewEvents` and `reviewState`, every pattern
object is byte-equivalent to the baseline: lemma, meaning, pattern key,
`relationType`, complements, roles, CEFR, `teachingStatus`,
`activityEligibility`, `learnerExplanationEn`, `errorNotes`, examples, example
provenance, evidence, `contentRefs`, IDs, allocation records and tombstones are
all untouched. The three D3.1 corrections stand exactly as adjudicated.

`releaseMode` remains `solo-maintainer-reference-backed` on all 45. The
governance specification defines no different value at `editorial-reviewed`,
so none was invented.

## Authoring context

Two changes only, both required by the established schema:

1. two new `editorialActorRegistry` records;
2. one appended `contextNotice` paragraph.

The appended paragraph names the exactly two Phase 4F-A statements it
supersedes — that no editorial-review actor is registered and that no
editorial-review event exists — and leaves every other statement standing. No
unrelated context history was rewritten. Every other top-level key is
byte-identical.

## Historical suites

Phase 4F-E1 repaired exactly **14 historical suites** that were written to
prove these events absent. Following the repair discipline Phase 4F-D3.1
already established, those suites now state their historical claims over the
corpus and context with this phase's approved governance work reverted,
through one phase-owned normaliser:
`tests/priority7_phase4fe1_normalizer.py`.

The normaliser statically pins the exact 45 E1 pattern identities and the exact
approved E1 event data for each, including every post-D3.1 tier-2 digest. It
derives no expected identity, event or digest from the live row. It removes
only the byte-equal approved E1 acceptance while the row is in E1's exact
`editorial-reviewed` final state. A duplicate or altered event, an unauthorized
content mutation with a freshly repinned digest, or an E1-shaped event on a
non-E1 identity is therefore not hidden. Where a suite compared file bytes,
the normaliser reconstructs the pre-E1 text and the byte comparison is kept.

Where a claim is substantive rather than historical — zero activity
eligibility, zero audio, no `approved` row, no product authority, no human
`reviewerRef`, every actor nonhuman — it is now asserted against the **live**
files, so this phase strengthened those guards rather than relaxing them.

## Future safety

`tests/test_priority7_phase4fe1.py` reads the phase-owned candidate, not
arbitrary future `HEAD`: the transition is `baseline → first descendant` via
`git rev-list --ancestry-path`, and every artifact is read at that revision
(or from the working tree while the phase is uncommitted). A later
product-approval phase may add files, add events and move `reviewState` without
making these tests fail merely because later work exists. That property is
itself tested, in committed scratch, by adding a hypothetical later commit and
re-running this suite.

## Validation

All green against the delivered candidate, in the working tree and again in a
fresh zero-remote committed scratch built from the baseline:

| Check | Result |
|---|---|
| `validate-editorial` | valid |
| Python suites | 22 suites, **1473 tests**, all OK |
| JXA suites | **36 / 36** |
| `validate_content.py` | OK — 1675 ids, forward baseline matched |
| `verify_audio.py` | 3377 / 3377 phrases, nothing orphaned |
| `build_pages.py --check` | committed output current |
| `git diff --check` | clean |

Run the Python suites with both the repository root and `tests/` on the import
path:

```
PYTHONPATH=".:tests" python3 -m unittest tests.<suite>
```

`test_priority7_phase4fc1c` requires `tests/` on `sys.path` for a bare
`import test_priority7_phase4fb3b`. That is an invocation-mode requirement
which predates this phase and is not a defect introduced here.

## Verdict

**GO** — see the closing report.

Not done, deliberately: no product approval, no `approved` state, no freeze, no
release authorisation, no runtime projection, no push.
