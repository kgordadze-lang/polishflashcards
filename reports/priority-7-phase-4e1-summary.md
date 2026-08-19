# Priority 7 — Phase 4E.1 Summary

## Nonhuman reference verification for solo-maintainer mode

**Verdict: GO.**

Reference verification under `solo-maintainer-reference-backed` is now performed by a nonhuman
source-analysis workflow actor. No human is named as a reference verifier, the fully human-reviewed
chain is unchanged, and the solo chain came out of this amendment **stricter** than it went in.

---

## 1. The mismatch this amendment corrects

Phase 4E built the solo-maintainer chain:

```
reference-verification → editorial-review → product-approval
```

and gave the two stages contradictory contracts:

| Stage | Phase 4E contract | Reality |
|---|---|---|
| `reference-verification` | required a **human** `reviewerRef` holding a `reference-verification` role | no such person exists or will exist |
| `editorial-review` | required a **nonhuman** `actorRef` | correct |
| `product-approval` | required a **human** `reviewerRef` | correct |

The only way to use the mode as shipped was to record a person — realistically the project owner —
as a human reference verifier. That is exactly the dishonesty Phase 4E was written to avoid, and it
had been reintroduced at tier 1. The synthetic Phase 4E fixture demonstrates the problem: it granted
`test-reviewer-owner-001` a `reference-verification` role and leaned on `ownerAllowsMultipleRoles`
to let the same person verify and approve.

The mismatch was found **before** Phase 4F-A wrote any real review event. Nothing had been recorded
under the mode, so no existing event changed meaning and no history needed migrating.

The truthful operating model, and what is now implemented:

| Stage | Performed by | Assurance |
|---|---|---|
| `reference-verification` | nonhuman source-analysis workflow actor | current authoritative source evidence |
| `editorial-review` | a **distinct** nonhuman editorial actor | independent corroboration, no unresolved blocking finding |
| `product-approval` | **human** project owner | explicit release-mode acknowledgement |

State progression is unchanged: `research → reference-verified → editorial-reviewed → approved`.
The names survive because `reference-verified` means "the recorded reference evidence passed the
reference-verification workflow", never "a human verified this externally", and
`editorial-reviewed` never means native-reviewed.

---

## 2. What was built

### 2.1 The actor contract is chosen from the mode, not the stage name

The decisive change. `_validate_review_event` now resolves the governing release mode **before** it
closes the event schema, because which of `actorRef` and `reviewerRef` an event may carry is a
consequence of the mode:

```python
MODE_NONHUMAN_STAGE_KINDS = {
    HUMAN_REVIEWED_MODE: frozenset({"editorial-review"}),
    SOLO_MAINTAINER_MODE: frozenset({"editorial-review", "reference-verification"}),
}
MODE_FORBIDDEN_STAGE_KINDS = {
    HUMAN_REVIEWED_MODE: frozenset({"reference-verification"}),
    SOLO_MAINTAINER_MODE: frozenset(),
}
```

The resulting contract matrix:

| Mode | Stage | Reference field | On-chain |
|---|---|---|---|
| `solo-maintainer-reference-backed` | `reference-verification` | `actorRef` only | tier 1 |
| `solo-maintainer-reference-backed` | `editorial-review` | `actorRef` only | tier 2 |
| `solo-maintainer-reference-backed` | `product-approval` | `reviewerRef` only | tier 3 |
| `solo-maintainer-reference-backed` | `external-verification` / `native-linguistic` | `reviewerRef` only | supplementary, may block |
| `human-reviewed` | `external-verification` | `reviewerRef` only | tier 1 |
| `human-reviewed` | `native-linguistic` | `reviewerRef` only | tier 2 |
| `human-reviewed` | `product-approval` | `reviewerRef` only | tier 3 |
| `human-reviewed` | `editorial-review` | `actorRef` only | supplementary, may block |
| `human-reviewed` | `reference-verification` | **refused outright** | — |

`reference-verification` is not merely non-advancing under the human chain; it is refused with a
dedicated `REVIEW_STAGE_NOT_IN_MODE`. Leaving it representable there would make a human-reviewed
history ambiguous about whether a person verified the claim, which is the exact confusion this
amendment removes.

This composes with the existing fail-closed mode normalisation to produce a second layer of
protection: an absent, malformed or unknown `releaseMode` resolves to `human-reviewed`, whose chain
has no reference tier — so an unreadable mode **cannot leave a nonhuman verification standing**.

### 2.2 A real nonhuman role, not a fake reviewer

`reference-verification` joins the nonhuman actor role vocabulary:

```python
EDITORIAL_ACTOR_ROLES = {
    "editorial-review", "example-generation", "reference-verification",
}
```

This constant was previously defined and never read. It is now enforced: an actor record may hold
only these three roles, and any other value — above all one borrowed from the human vocabulary, such
as `native-linguistic` — is refused with `EDITORIAL_ACTOR_ROLE_UNKNOWN`. `_validate_review_event`
requires the role matching the stage being performed, so an editorial-only actor cannot perform
reference verification and an example generator cannot either.

No fake reviewer was created, `human: false` is still mandatory and still must be stated explicitly,
and `reviewerRegistry` is not reused: the registry-collision check that already forbade one identity
key spanning registries is untouched and now covers the reference actor too.

### 2.3 Reference and editorial actors must be independent

`REVIEW_ACTOR_INDEPENDENCE`: the actor of a `reference-verification` acceptance may not appear as the
actor of an `editorial-review` acceptance, nor among its `corroboratingActorRefs`, anywhere in the
same pattern's history. The check lives in `_replay_review_order`, which is the one replay both the
editorial record and the frozen envelope already run, so the frozen release gets it for free.

This integrates with the existing corroboration mechanism rather than duplicating it. The minimum
valid solo chain now needs **three distinct nonhuman identities**: a reference actor, an editorial
actor, and at least one independent corroborator. `corroboratingActorRefs` and `findings` stay
scoped to `editorial-review` exactly as before — a reference verification's corroboration is the
cited sources, not a second opinion about the sources.

### 2.4 Source authority stayed evidence, not model identity

Deliberately unchanged. The actor records only that the workflow ran. Every Phase 4E evidence
condition still decides whether the claim is verified:

| Input | Result |
|---|---|
| no pinned evidence | `REVIEW_EVIDENCE_REQUIRED` |
| pins that do not resolve to current evidence | not accepted → `REVIEW_STATE_MISMATCH` |
| lemma-only / headword-only | `REFERENCE_PATTERN_EVIDENCE_REQUIRED` |
| Mędak headword-only | `REVIEW_CONTEMPORARY_EVIDENCE_REQUIRED` |
| stale evidence (record edited after acceptance) | acceptance retires → `REVIEW_STATE_MISMATCH` |
| stale scope (copy edited after acceptance) | acceptance retires → `REVIEW_STATE_MISMATCH` |

A perfectly registered actor plus no qualifying evidence yields `research`. That property is asserted
directly.

### 2.5 No vendor name is load-bearing

Stable actor identity is a workflow role. The synthetic reference actor is
`test-actor-reference-analysis-001`, and the real-world naming the specification recommends is
`priority7-reference-analysis` / `priority7-independent-editorial-review`. Model and run identifiers
may be recorded on the actor record as private audit metadata; the schema neither requires nor reads
them. This is proven, not asserted: the same release freezes to **byte-identical** output with the
audit metadata absent, rewritten, or naming a vendor, and no vendor or model token appears anywhere
in `priority7_tooling.py`.

### 2.6 The release describes its own assurance per pattern

`releaseAuthorization` gains one derived field:

```json
{
  "releaseModes": ["solo-maintainer-reference-backed"],
  "humanVerifiedPatternIds": [],
  "humanNativeReviewedPatternIds": []
}
```

`humanVerifiedPatternIds` names the patterns over which a current **human** `external-verification`
acceptance still stands. It exists because a mixed release was otherwise ambiguous about which
patterns a person actually verified: the mode list alone could not distinguish them.

Under the solo mode both coverage lists are ordinarily empty, and that emptiness is the honest
statement. A valid solo release reports its mode, and claims no human external verification, no human
reference verification and no native review — because it has none. Every field is recomputed from the
retained history at validation time, so a forged value is refused with
`FROZEN_RELEASE_AUTHORIZATION_PARITY`.

Truthfulness runs both ways: a genuine human `external-verification` or `native-linguistic` event on
a solo-maintainer pattern is reported rather than discarded, and both are live digest claims that
stop being reported when the text they covered changes.

### 2.7 Frozen history keeps the distinction structurally

The frozen review-history validator previously called `_validate_review_event` **without** the row's
release mode. It now passes it, so a released history is held to exactly the contract the editorial
record was held to. Consequences, each tested:

- a frozen `reference-verification` retains `actorRef` and cannot carry `reviewerRef`;
- substituting `actorRef` → `reviewerRef` in frozen data is refused;
- relabelling a frozen reference event as `external-verification` yields
  `FROZEN_REVIEW_STATE_MISMATCH`, not a silently stronger-looking release;
- a frozen human-mode row cannot gain a reference event (`REVIEW_STAGE_NOT_IN_MODE`).

`ReleaseAuthorization` remains fully derived and recomputed.

---

## 3. Human mode is unchanged, and human review stays optional-strengthening

No human-mode regression. `external-verification` and `native-linguistic` still require an identified
human `reviewerRef` with the matching role; `human: true` requirements, role requirements, the
`ownerAllowsMultipleRoles` restriction, native-review semantics and every digest/freeze/release rule
are untouched. Human mode got *stricter* in exactly one respect — it now refuses a
`reference-verification` event outright.

Human native review in solo mode remains optional strengthening evidence, with its veto intact: a
native `reject` is terminal and a native `changes-requested` still drops the pattern back to
`reference-verified`. AB (`native-reviewer-001`) is unchanged — `human: true`,
`nativePolishSpeaker: true`, roles exactly `["native-linguistic"]`, no multi-role allowance, no mode
acknowledgement — and no new AB event exists.

One consequence worth recording: because the solo owner now performs exactly **one** review stage,
the `ownerAllowsMultipleRoles` allowance no longer has anything to govern in the solo chain. Rather
than let the gate quietly stop being tested, the two tests covering it were moved to the case where
it now actually bites — a human-mode release in which one person acts as external verifier and then
as product approver — with both a positive and a negative control.

---

## 4. Product approval remains human

Unchanged and mandatory. `product-approval` requires `reviewerRef` and forbids `actorRef`, so it can
never become machine-performed; a nonhuman approver is refused; the owner's registry record must
still list the mode in `acknowledgedReleaseModes`; and a release without a current approval cannot
reach `approved`. The owner remains responsible for learner-facing usefulness, UX, the inclusion
decision, the release-mode acknowledgement, and acceptance of the solo-maintainer limitations.

The synthetic owner's roles are now `["product-approval", "correction", "reopen"]` — the
`reference-verification` role was removed, because the owner does not perform it.

---

## 5. Files changed

| File | Change |
|---|---|
| `priority7_tooling.py` | mode-sensitive actor contract; `reference-verification` actor role; enforced actor role vocabulary; `REVIEW_STAGE_NOT_IN_MODE`; `REVIEW_ACTOR_INDEPENDENCE`; frozen events validated under their own mode; derived `humanVerifiedPatternIds` |
| `tests/fixtures/priority7/synthetic-release-editorial.json` | added `test-actor-reference-analysis-001` (nonhuman, `reference-verification`, private audit metadata); removed `reference-verification` from the owner's reviewer roles |
| `tests/test_priority7_phase4e1.py` | **new** — 89 tests |
| `tests/test_priority7_phase4e.py` | reference events now actor-borne; multi-role gate moved to where it bites; authorization expectations |
| `tests/test_priority7_phase5a.py` | solo chain's reference event now actor-borne; mode-distinguishability and runtime-privacy assertions extended |
| `reports/priority-7-provenance-and-review-specification.md` | Phase 4E.1 amendment: §11.3 rewritten, §11.5 authorization table, §11.10 limitations |
| `editorial/priority-7-authoring-context.json` | `contextNotice` only — records the corrected capability and that `reference-verification` is no longer a reviewer role |
| `reports/priority-7-phase-4e1-summary.md` | this document |

Not touched: `editorial/verb-pattern-candidates.json`, shipping/browser files, runtime, generated
pages.

---

## 6. Validation performed

| Gate | Result |
|---|---|
| Phase 4E.1 (new) | **89 passed** |
| Phase 4E | 103 passed |
| Phase 5-A | 112 passed |
| Phase 4C | 53 passed |
| Phase 3F-A | 17 passed |
| Phase 2A | 77 passed |
| Phase 3B / 3C / 3D-1 | 19 / 22 / 44 passed |
| Full Python | **711 passed, 0 failed** (was 622 before this phase) |
| Full JXA | **36 suites, 0 failed** |
| `validate_content.py` | OK — forward baseline sha256 `2a71401d…3a1ce50` unchanged |
| `verify_audio.py` | OK — 3377 phrases, nothing orphaned |
| `build_pages.py --check` | OK — committed output current |
| Editorial validation of the real corpus (CLI) | valid |
| `git diff --check` | clean |
| Committed-scratch survivability | **Python + 36 JXA + content + pages, all pass committed** |

Fifteen single-mutation editorial gates are matrix-tested against a proven-clean control, alongside
the Phase 4E matrices which still pass unchanged.

### Adversarial results

Every probe drives the real release path — `validate_editorial` → `freeze_editorial` →
`validate_frozen_release` → `verified_runtime_from_frozen`.

| Probe | Result |
|---|---|
| solo `reference-verification` with `reviewerRef` | ✕ `SCHEMA_REQUIRED` + `SCHEMA_UNKNOWN_FIELD` |
| solo `reference-verification` carrying **both** references | ✕ `SCHEMA_UNKNOWN_FIELD` |
| solo `reference-verification` with `actorRef`, otherwise valid | ✓ validates, freezes, projects authoritative runtime |
| actor record `human: true` | ✕ `EDITORIAL_ACTOR_NOT_NONHUMAN` |
| actor record omitting `human` | ✕ `EDITORIAL_ACTOR_NOT_NONHUMAN` |
| actor missing the `reference-verification` role | ✕ `EDITORIAL_ACTOR_ROLE` |
| actor holding a borrowed human role | ✕ `EDITORIAL_ACTOR_ROLE_UNKNOWN` |
| unknown actor | ✕ `EDITORIAL_ACTOR_REGISTRY_DANGLING` |
| editorial actor reused as reference actor | ✕ `REVIEW_ACTOR_INDEPENDENCE` |
| reference actor reappearing as a corroborator | ✕ `REVIEW_ACTOR_INDEPENDENCE` |
| the two identities swapped in a later round | ✕ `REVIEW_ACTOR_INDEPENDENCE` |
| reference actor used as human external verifier | ✕ `REVIEWER_REGISTRY_DANGLING` |
| reference actor used as native reviewer | ✕ `REVIEWER_REGISTRY_DANGLING` |
| reference actor used as example generator | ✕ `EDITORIAL_ACTOR_ROLE` |
| AB (human native reviewer) used as solo reference actor | ✕ `EDITORIAL_ACTOR_REGISTRY_DANGLING`; re-registering as an actor ✕ `REGISTRY_KEY_COLLISION` |
| product owner used as actor | ✕ `EDITORIAL_ACTOR_REGISTRY_DANGLING`; relisted as nonhuman ✕ `REGISTRY_KEY_COLLISION` |
| reference accept with no qualifying evidence | ✕ (see §2.4 table) |
| stale evidence / stale scope | ✕ `REVIEW_STATE_MISMATCH` |
| duplicate reference accept | ✕ `REVIEW_DUPLICATE_STAGE_ACCEPTANCE`, at validation and again at freeze |
| duplicate reference accept under a *different* actor | ✕ `REVIEW_DUPLICATE_STAGE_ACCEPTANCE` |
| out-of-order editorial review | ✕ `REVIEW_STAGE_ORDER` |
| `reference-verification` in human mode | ✕ `REVIEW_STAGE_NOT_IN_MODE` |
| malformed / unknown / absent mode | ✕ `SCHEMA_ENUM` **and** `REVIEW_STAGE_NOT_IN_MODE`, no exception raised |
| product approval performed by an actor | ✕ `SCHEMA_REQUIRED` + `SCHEMA_UNKNOWN_FIELD` |
| owner approval missing | ✕ `REVIEW_STATE_MISMATCH` |
| frozen `actorRef` → `reviewerRef` substitution | ✕ refused |
| frozen reference event relabelled as human verification | ✕ `FROZEN_REVIEW_STATE_MISMATCH` |
| forged `humanVerifiedPatternIds` / `humanNativeReviewedPatternIds` | ✕ `FROZEN_RELEASE_AUTHORIZATION_PARITY` |

Legitimate paths still succeed: a `changes-requested` permits a fresh reference verification; an
owner `correction` permits a fresh round that freezes and validates; three distinct actor identities
is the clean shape.

### Both modes end to end

| Mode | Chain | Result |
|---|---|---|
| `human-reviewed` | human `external-verification` → human `native-linguistic` → human `product-approval` | validates → freezes → frozen-valid → authoritative runtime |
| `solo-maintainer-reference-backed` | actor A `reference-verification` → actor B `editorial-review` (+ corroborator) → human `product-approval` | validates → freezes → frozen-valid → authoritative runtime |

Both project the **identical** public runtime — governance decides what may ship, never what shipping
looks like — and neither ships any governance vocabulary: no `actorRef`, `releaseMode`,
`releaseAuthorization`, stage kind, actor ID or reviewer ID appears in the runtime document.

---

## 7. Final boundary — the real corpus advanced by nothing

| Requirement | Verified |
|---|---|
| `editorial/verb-pattern-candidates.json` byte-identical to HEAD | yes (asserted against `git show HEAD:…`) |
| 30 lemmas / 34 meanings / 45 patterns | yes |
| 45/45 `research` | yes |
| Zero real review events | yes (0) |
| Zero activity eligibility | yes (0) |
| No real `releaseMode` assignment | yes — no governance token appears in the corpus |
| No reference actor used on any real pattern | yes — `editorialActorRegistry` is absent from the real context |
| Five pending replacement slots unchanged | yes — all real example origins still `repository-reuse`, zero `editorial-generated` |
| AB unchanged | yes — `["native-linguistic"]`, human, native, no allowances |
| No product approval, no freeze, no runtime | yes — `content/` absent |
| No commit, no push, no remote added | yes — HEAD still `22cef59`, zero remotes, `push.default=nothing` |
| Phase 4F-A not begun | yes |

---

## 8. Verdict

**GO.**

Solo reference verification can now be performed truthfully by a nonhuman source-analysis actor. No
fake human identity is required anywhere in either chain, and neither release path became weaker:

- the human-reviewed chain is unchanged except that it now refuses a stage that never belonged to it;
- the solo chain gained an independence requirement and an enforced actor role vocabulary, and kept
  every evidence, duplicate, ordering, freeze, digest and privacy protection intact;
- the frozen release distinguishes nonhuman from human verification structurally, and states its own
  human coverage per pattern in a form that is derived and cannot be forged.

`human-reviewed` remains the stronger independent-human-assurance path and should be used whenever
the human roles are actually available.

---

## 9. Limitations — read this before releasing under this mode

`reference-verification` under the solo mode is a **nonhuman reference-analysis workflow backed by
explicit authoritative evidence**. It is not human external verification, not professional linguistic
review, and not native-speaker review. `editorial-review` is likewise nonhuman and is not native
review. Reference-backed model review can be wrong in ways a native speaker would catch immediately.
The single human judgement in the chain is the owner's product approval, which is a usefulness and
inclusion decision rather than a linguistic one.

Independence between the two nonhuman tiers is an independence of *identity and workflow*, not
necessarily of underlying model family. The schema deliberately does not — and cannot — verify that
two actors are genuinely uncorrelated; it verifies that the project recorded two distinct workflow
identities and did not let one stand in for both.

## 10. What the next phase must do

Phase 4F-A was **not** started here, as required. Before any real event is written under this mode
the owner must, at minimum: register the real nonhuman reference and editorial actors under
workflow-role names in `editorialActorRegistry`; register themselves with `product-approval` and an
`acknowledgedReleaseModes` entry naming the solo mode; and accept §9 above in the knowledge that no
human external verification or native review is being claimed for anything released under it.
