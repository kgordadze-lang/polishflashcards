# Priority 7 — Phase 4E Summary

## Solo-maintainer governance amendment

**Branch:** `priority-7-phase-4e-solo-maintainer-governance`
**Baseline:** HEAD `34680d2a3e50ca55979f41062ea856c017d1e127`, tree `1f6e8efb8e0707c3a98d93f27257b3454c9fdcd6`
**Scope:** governance capability only. No real review event, no real approval, no freeze, no release, no runtime change.
**Verdict:** **GO** after repair — see §11. The first implementation was returned **NO-GO** by independent review; see §0.

---

## 0. Independent review: initial NO-GO, and what was actually broken

Codex reviewed the first Phase 4E implementation and returned **NO-GO**. Its architectural findings
were that the model itself was sound — both modes valid, AI review never masquerading as human or
native review, editorial-generated provenance distinct from human-original, `releaseAuthorization`
genuinely derived, frozen mode/tombstone handling correct, public privacy holding, real corpus
untouched — but it proved two concrete validator defects. Both were real, both were mine, and both
are recorded here rather than smoothed over.

### Defect 1 — a stage could be accepted twice (release-authority defect)

Codex proved that these histories validated, froze, passed frozen validation, **and produced an
authoritative runtime document**:

```text
human:  external-verification accept → external-verification accept → native-linguistic → product-approval
solo:   reference-verification accept → reference-verification accept → editorial-review → product-approval
```

The order replay treated a tier-1 acceptance as unconditional (`history_state = STAGE_STATE[kind]`),
because tier 1 is the only stage with no predecessor state to check. A second acceptance therefore
re-established the tier instead of being rejected. Tiers 2 and 3 were *incidentally* protected — a
repeated acceptance there fails the preceding-state check with `REVIEW_STAGE_ORDER` — which is
precisely why the gap was easy to miss: five of the six stage positions looked correct.

I re-probed all six stage positions across both modes rather than trusting that finding's scope.
Confirmed: only tier 1 was reachable, and tiers 2–3 failed only as a side effect of stage-ordering,
not because any rule named duplicates.

### Defect 2 — a container-valued `releaseMode` crashed the validator

`declared_release_mode` tested `mode in RELEASE_MODES` — a dict membership test — before proving the
value was a string. `releaseMode: []` and `releaseMode: {}` therefore raised an uncaught
`TypeError: unhashable type` out of a public entry point instead of returning a validation issue.
Every other malformed value (null, boolean, integer, float, empty string, unknown string) already
validated correctly, which again is what made the hole easy to miss.

---

## 1. The problem Phase 4E solves

Priority 7 governance assumed four available humans: an external verifier, a native reviewer, a
product approver, and an original-example author. The project has one owner and one genuine native
review — `native-reviewer-001` ("AB"), who reviewed the Phase 4A package on 2026-08-13 and accepted
all 45 rows as presented.

Under the locked chain that is not a slow path, it is a closed one. `native-reviewed` is unreachable
without a prior human external verification nobody can perform, and the five accepted replacement
sentences are unusable because `origin.kind: "original"` requires a human author record that does not
and will not exist. Phase 4C and Phase 4D-A both terminated on exactly these blockers and correctly
refused to invent a way around them.

Two dishonest escapes were available. Both are rejected, permanently and mechanically:

- recording model output in fields that mean "identified human reviewer";
- recording model-drafted sentences as human-authored.

Phase 4E takes the third option: name the process the project actually performs, and gate it at least
as strictly as the chain it stands beside.

## 2. What was built

A second fail-closed release mode, declared per pattern:

| `releaseMode` | Chain | Reached states |
|---|---|---|
| `human-reviewed` (default) | `external-verification` → `native-linguistic` → `product-approval` | `externally-verified` → `native-reviewed` → `approved` |
| `solo-maintainer-reference-backed` | `reference-verification` → `editorial-review` → `product-approval` | `reference-verified` → `editorial-reviewed` → `approved` |

The field is optional and **absence means `human-reviewed`**, so no existing record drifts into the
weaker chain by omission, and the 45 untouched real patterns are governed exactly as before. An
unrecognised value fails closed twice: the closed enum rejects it, and an unknown mode establishes no
stage, so the pattern cannot rise above `research`.

Crucially, the solo chain **does not reuse the human chain's state names**. An item reviewed by a
model is `editorial-reviewed`, never `native-reviewed`. An item whose sources the owner checked is
`reference-verified`, never `externally-verified`. Only `approved` is shared, because it means the
same thing in both: the project owner accepted the record for product inclusion.

### 2.1 The three solo stages

**`reference-verification`** — a human act by the owner, and the strictest evidence gate in either
mode. It carries every §5 requirement of external verification plus one more: the pinned evidence
must include a record whose `factType` is `complement-frame` or `meaning`. Headword presence can
never verify a pattern. WSJP PAN remains the preferred contemporary reference; Mędak remains research
evidence under the unchanged rights rules.

**`editorial-review`** — performed by a nonhuman actor, and *structurally incapable* of naming a
person. The event requires `actorRef` and forbids `reviewerRef`; `actorRef` resolves only in a
separate `editorialActorRegistry` whose records must state `human: false`. An acceptance additionally
requires at least one distinct corroborating registered actor, so no single model's opinion is ever
release-authoritative, and any `findings` it carries must have no unresolved `high` severity. A
resolved finding must record how it was resolved, which is where model disagreement is reconciled.

**`product-approval`** — unchanged in kind, stricter in this mode: the approver's registry record must
list the mode in `acknowledgedReleaseModes`. The owner cannot approve under the weaker chain without
having recorded that they understand which assurance they are accepting. The pre-existing
`ownerAllowsMultipleRoles` allowance still governs one person performing two stages, and now covers
the new stage kinds.

### 2.2 Truthful example provenance

`origin.kind` gains `editorial-generated`, requiring `generatorRef` (resolving to a registered
nonhuman actor with the `example-generation` role) and `adoptedAt`, and forbidding `authorRef`,
`authoredAt` and `repositorySource`. It is neither repository reuse nor human authorship, and it never
claims a person wrote the sentence.

The `original` guard is untouched. A human author record is still required and a nonhuman one still
refused, so no model can be laundered into authorship — and the owner is never asked to falsely adopt
authorship of a sentence they did not write.

### 2.3 The release states its own governance

The frozen envelope gains a derived `releaseAuthorization` record:

```json
{
  "releaseModes": ["solo-maintainer-reference-backed"],
  "humanNativeReviewedPatternIds": []
}
```

Both fields are **recomputed and compared**, never asserted, so a release cannot describe itself as
more human-reviewed than its own retained history proves. `releaseMode` is also stored on each frozen
`policy` row and on each `reviewHistory` row, with parity enforced between them; the history row is
the durable home because a tombstoned pattern keeps no policy row.

## 3. Preserved historical truth

AB is unchanged and unmoved: `human: true`, `nativePolishSpeaker: true`, `roles: ["native-linguistic"]`,
no `ownerAllowsMultipleRoles`, no `acknowledgedReleaseModes`, not an author, not a verifier, not an
approver. Phase 4A/4B/4C records remain historically correct. Phase 4E changes forward policy only.

Human native review stays fully representable in both modes and is never required by the
solo-maintainer one. A `native-linguistic` event on a solo pattern is recorded and validated in full
but does not advance the chain, so no AI-reviewed item is ever backfilled into AB's genuine review.

The asymmetry is deliberate and tested: **human review can always block and is never required to
pass.** A human native `reject` is terminal in both modes; a human native `changes-requested`
invalidates its scope tier and everything above it.

Reported human native coverage is a live digest claim, not a badge. If text changes and is
re-reviewed through the solo chain, the pattern silently stops being reported as human-native
reviewed.

## 3a. The two repairs

### Repair 1 — duplicate stage acceptances

The guard lives in the shared order replay, so it applies identically to the editorial record and to
the frozen envelope, and to both chains:

> An on-chain acceptance is **refused** when that tier already stands over the identical scope
> digest, with no intervening correction, reopen, change request, terminal decision, completed
> round, or scope change.

New issue code: `REVIEW_DUPLICATE_STAGE_ACCEPTANCE`.

Choosing the *standing scope digest* rather than "has this stage appeared before" is what keeps the
guard honest in both directions. An identical digest proves that nothing the tier reviews has
changed, so the second acceptance establishes nothing the first did not; a different digest means
the material genuinely moved, which is legitimate re-review. That distinction is why the guard
rejects the defect without closing any real path.

The resets that legitimately reopen a tier are all pre-existing governance events, not new
inventions:

| Event | Effect on the duplicate guard |
|---|---|
| `correction` (owner-authorized) | reopens every tier — this is already the architecture's licence to change released material |
| `reopen` | reopens every tier |
| `changes-requested` at tier *T* | reopens tier *T* and everything above it |
| `defer` / `reject` | reopens every tier (a reopen is required anyway) |
| acceptance at tier *T* | reopens every tier above *T* |
| acceptance at the product tier | closes the round and reopens tiers 1–2, **but not itself**, so a repeated approval is still caught until a new verification reopens it |
| a scope-changing edit | no longer matches the standing digest, so the tier is genuinely stale |

The "completed round" rule was not in my first attempt at the fix, and its absence made the guard
reject a legitimate flow: appending a *complete* new review round after a finished one. Seven
pre-existing Phase 2A and Phase 5-A tests exercise that flow (their helpers append a fresh chain to
every approved pattern, including patterns whose content did not change). Rather than edit those
suites — which are outside the seven Phase 4E candidate paths — I made the semantics correct:
repeating a stage *within* a round is forbidden, starting a new round is not.

### Repair 2 — malformed `releaseMode`

`declared_release_mode` now proves the value is a string before any membership test, and a new
`release_mode_chain` helper does the same for chain lookup. Both normalise every malformed value to
the strictest chain instead of raising. The malformed value is still reported — by the closed-enum
check at each entry point — so nothing is silently accepted; what changed is that no caller can be
crashed by an unhashable value.

Every site that maps by mode was audited: editorial validation, both replays, freeze,
`_policy_for_entity`, frozen policy and history validation, and `releaseAuthorization` derivation.
The derivation now normalises too, so a malformed stored value can never be echoed into a derived
governance record — the record a later tool reads to learn how the release was reviewed.

## 4. Design decisions worth recording

**Shared scope tiers, unshared authority.** `reference-verification` projects exactly the
`external-verification` scope and `editorial-review` exactly the `native-linguistic` scope, so
`scopeVersion` stays `1` and no historical digest is reinterpreted. Their digests are consequently
identical for the same content. That is safe because currency is keyed on the event kind the declared
mode requires: relabelling an event as the other chain's kind establishes nothing, and switching a
released pattern's mode mechanically invalidates its approval. Both directions are tested.

**One derivation, two callers.** The editorial validator and the frozen release validator now share a
single `_derive_review_currency` implementation, replacing two hand-maintained copies of the same
state machine. The two can no longer disagree about what a history proves.

**The shipping loader was not touched.** `PRIVATE_RUNTIME_KEYS` remains the exact mirror the loader
comments describe; the Phase 4E vocabulary is layered separately in `FORBIDDEN_RUNTIME_KEYS`. The
closed runtime schema already gives every new key nowhere to appear, which is asserted directly
rather than assumed.

## 5. English translations codified (§7)

Authorship and provenance concern `example.pl`. `example.en` is an editorial translation carrying no
separate authorship claim unless separately attributed. The consequence is now codified and tested:
an English-only edit leaves reference/external verification scope byte-identical while invalidating
the editorial/native and product scopes, dropping the stored state to `reference-verified` or
`externally-verified` respectively.

## 6. Files changed

| File | Change |
|---|---|
| `priority7_tooling.py` | The amendment: modes, stages, states, actor registry, findings, `editorial-generated` origin, `releaseAuthorization`, shared currency derivation. **Repairs:** duplicate-acceptance guard; type-safe mode normalisation |
| `tests/test_priority7_phase4e.py` | New — 103 tests (88 + 15 repair tests) |
| `tests/test_priority7_phase5a.py` | Solo-maintainer release path + loader bridge; two reconciliations (§7); **repair proofs on the real freeze path** |
| `tests/fixtures/priority7/synthetic-release-editorial.json` | Synthetic owner reviewer and two synthetic nonhuman actors |
| `reports/priority-7-provenance-and-review-specification.md` | New §11; amended header and decision log |
| `editorial/priority-7-authoring-context.json` | `contextNotice` prose only — no registry gained an entry |

**Not modified:** `editorial/verb-pattern-candidates.json`, `index.html`, `pp-verb-patterns.js`,
`sw.js`, `manifest.json`, `APP_VERSION`, cache names, runtime data, generated pages.

## 7. Phase 5-A reconciliations

Two Phase 5-A tests needed honest reconciliation rather than accommodation:

1. `test_no_shipping_file_was_touched` — its allowlist did not contemplate a phase amending the
   governance module. `priority7_tooling.py` is private editorial tooling: never served, never
   precached, never executed by any loader. Added to the allowlist; the shipping-surface assertions
   beside it are unchanged and still pass.
2. `test_cross_language_contract_constants_agree` — the constant split described in §4. The
   Python↔JavaScript equality it guards is **unchanged**; a new assertion pins the layering, and a new
   test proves every governance key is refused by the closed runtime schema at three injection points.

Phase 5-A now proves **both** modes: the human-reviewed path is untouched and still exercised
end-to-end, and the solo path travels the same freeze, allocation, tombstone, revision, privacy and
JXA loader-bridge machinery.

## 8. Validation performed

All totals below are post-repair.

| Gate | Result | Before repair |
|---|---|---|
| Phase 4E (new) | **103 passed** | 88 |
| Phase 5-A | **112 passed** | 108 (98 pre-4E) |
| Phase 4C | 53 passed | 53 |
| Phase 3F-A | 17 passed | 17 |
| Phase 2A | 77 passed | 77 |
| Phase 3B / 3C / 3D-1 | 19 / 22 / 44 passed | unchanged |
| Full Python (10 modules) | **622 passed, 0 failed** | 603 |
| Full JXA (36 suites) | **all 36 pass, 0 failed** — incl. Phase 5-A bridge 47, 3F-A loader 57 | 36 |
| `validate_content.py` | OK — forward baseline sha256 `2a71401d…3a1ce50` unchanged |
| `verify_audio.py` | OK — 3377 phrases, nothing orphaned |
| `build_pages.py --check` | OK — committed output current |
| Editorial validation of the real corpus | valid |
| `git diff --check` | clean |

Load-bearing gates are mutation-tested: 16 single-mutation editorial cases and 7 frozen-envelope
cases, each against a proven-clean control.

### Adversarial probe results (post-repair)

Every probe was re-run independently against the repaired validator, driving the **real release
path** — `validate_editorial` → `freeze_editorial` → `validate_frozen_release` →
`verified_runtime_from_frozen` — not a single check in isolation.

**Duplicate-stage matrix.** All six stage positions across both chains, each refused at editorial
validation and again at freeze, none reaching an authoritative runtime document:

| Mode | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| `human-reviewed` | `external-verification` ✕ | `native-linguistic` ✕ | `product-approval` ✕ |
| `solo-maintainer-reference-backed` | `reference-verification` ✕ | `editorial-review` ✕ | `product-approval` ✕ |

✕ = refused with `REVIEW_DUPLICATE_STAGE_ACCEPTANCE`. Before the repair, tier 1 in both modes reached
authoritative runtime; tiers 2–3 failed only incidentally with `REVIEW_STAGE_ORDER`, and now fail
with the dedicated code. Duplicates injected directly into a **frozen** envelope (which freeze itself
now refuses to produce) are likewise refused by `validate_frozen_release`.

**Legitimate re-review still succeeds**, proven to full authoritative runtime in both modes:

| Flow | Result |
|---|---|
| scope-changing edit, then a fresh chain (solo and human) | freezes, validates, projects |
| owner `correction`, then a fresh chain | freezes, validates, projects |
| `changes-requested`, then a fresh chain | validates |
| a complete round followed by a complete new round | validates |
| a repeated closing approval with no new verification | refused |

**Malformed `releaseMode` table.** Every value below returns deterministic issues from
`validate_editorial`, is refused by `freeze_editorial`, produces no runtime, and raises nothing:

| Value | Editorial | Freeze | Frozen policy row | Frozen history row |
|---|---|---|---|---|
| `null`, `true`, `1`, `1.5`, `""`, `"unknown-mode"` | `SCHEMA_ENUM` | refused | `SCHEMA_ENUM` | `SCHEMA_ENUM` |
| `[]`, `["human-reviewed"]` | `SCHEMA_ENUM` | refused | `SCHEMA_ENUM` | `SCHEMA_ENUM` |
| `{}`, `{"mode": …}` | `SCHEMA_ENUM` | refused | `SCHEMA_ENUM` | `SCHEMA_ENUM` |
| absent | accepted → `human-reviewed` | — | — | — |
| a known mode string | accepted | — | — | — |

The two container cases raised `TypeError` before the repair. The non-release CLI projector
(`project_runtime_nonrelease`) is covered too, since "no public entry point" has to mean all of them.

### Clean committed-scratch survivability

Performed in an isolated scratch clone only; the real repository remains uncommitted with zero
remotes.

| Item | Result |
|---|---|
| Scratch clone base | `34680d2` — this branch, remote removed |
| Scratch commit (repaired candidate) | `ea06a697c2e396993bf541a14c8bc4ffaad277a2` |
| Paths in the scratch commit | exactly the seven candidate paths |
| `editorial/verb-pattern-candidates.json` in the commit diff | **absent** — corpus untouched |
| Scratch worktree after commit | **clean** — `git status --short --untracked-files=all` empty |
| Phase 4E / 5-A / 4C / 3F-A / 2A from committed HEAD | 103 / 112 / 53 / 17 / 77 passed |
| Full Python suite from committed HEAD | **622 passed, 0 failed** |
| `validate_content.py` / `build_pages.py --check` from committed HEAD | OK |
| Editorial validation from committed HEAD | valid |
| JS release bridges from committed HEAD | 47 + 57 + 438 + 327 passed |
| `git diff --check` from committed HEAD | clean |

(The pre-repair candidate was separately survivability-checked at scratch commit
`2d939772bb3c9eab4fdf691fc94cf45f2449ba8c` with 603 tests; that run is superseded by the one above.)

The candidate is green both uncommitted and from a clean committed HEAD. This matters because two
Phase 5-A tests consult git directly (`git status --porcelain` and `git show HEAD:`), and a change
that only passes in one of the two states would be a latent failure.

## 9. Final boundary

Re-proven after the repair:

| Requirement | Verified |
|---|---|
| `editorial/verb-pattern-candidates.json` byte-identical to HEAD | yes |
| 30 lemmas / 34 meanings / 45 patterns | yes |
| 45/45 `research` | yes |
| Zero review events | yes (0) |
| Zero activity eligibility | yes (0) |
| No `releaseMode` on any real pattern | yes — no governance token appears anywhere in the corpus |
| Five pending replacements unchanged and noncanonical | yes — 3 originals intact and still `repository-reuse`, 2 slots still `examples: null` |
| Zero product approvals, zero freeze, zero `patternDataRevision` | yes |
| Zero public runtime (`content/` absent, no freeze/release artifact) | yes |
| No shipping change | yes — `APP_VERSION 8.10`, `popolsku-v65`, loader untouched |
| Zero remotes, no commit, no push | yes — HEAD still `34680d2` |

## 10. Limitations — read this before releasing under this mode

This must not be presented as equivalent to professional linguistic review.

- **This mode provides materially less independent human assurance than a fully human-reviewed
  release.** It substitutes documented reference checking and corroborated model review for a native
  speaker's judgement. Those are not the same thing.
- **AI and reference review can be wrong.** A model can misread a source, agree with a plausible
  error, or corroborate a second model's mistake — the corroboration requirement reduces single-model
  failure, it does not eliminate correlated failure. Reference verification can also cite a genuine
  source for a claim the source does not actually support at the level of detail required.
- **The owner is not independent.** Performing both reference verification and product approval is a
  real weakness that `ownerAllowsMultipleRoles` makes visible rather than solves.
- **Human native review remains desirable wherever it can be obtained**, and is strictly stronger
  evidence than anything this mode produces. It stays representable, is reported per pattern, and can
  always block.
- **The project owner accepts this limitation for the current release**, which is why
  `acknowledgedReleaseModes` is mandatory: the acceptance is on the record, per approver.
- **Correction and re-review remain fully supported.** Every invalidation, correction, reopen and
  re-acceptance path works identically in this mode, so a later human review can overturn any
  editorial acceptance without rewriting history.

## 11. Verdict

**GO** — after repair, and only after repair.

Both technical NO-GO findings are closed:

- **Duplicate stage acceptance** is refused deterministically at every one of the six stage
  positions across both chains, with a dedicated issue code, at editorial validation, at freeze, and
  in a directly tampered frozen envelope. No duplicate history reaches an authoritative runtime
  document. Legitimate re-review after a scope change, a correction, a change request, or a
  completed round still succeeds end-to-end.
- **Malformed `releaseMode`** is a validation issue on every value tested — including the two
  container cases that previously raised `TypeError` — at every public entry point, with no
  coercion, no crash, and no leakage into any derived governance record.

The architecture Codex confirmed is unchanged. Both chains, both state vocabularies, the strict
default, actor/reviewer separation, evidence and corroboration requirements, the unresolved-blocker
rule, mandatory acknowledged owner approval, provenance rules, the English-translation rule, frozen
mode retention, derived `releaseAuthorization`, runtime privacy, and the ID/tombstone/revision
protections all stand exactly as reviewed. Nothing was weakened to make a test pass; the one place
where my first repair attempt was too broad, I corrected the *semantics* rather than the tests.

The amended model has not been applied to the real 45 patterns. Doing so is the next phase's work.

## 12. What the next phase must do

1. Name the real authorities in `editorial/priority-7-authoring-context.json`: the owner's reviewer
   record with `reference-verification` + `product-approval` roles, `ownerAllowsMultipleRoles`, and
   `acknowledgedReleaseModes: ["solo-maintainer-reference-backed"]`; plus at least two nonhuman
   editorial actors in a new `editorialActorRegistry`.
2. Assemble the reference evidence bundle per pattern, with pattern-or-meaning-level source evidence.
3. Run the independent multi-model editorial review and record its findings and resolutions.
4. Apply truthful `editorial-generated` provenance to the five sentences (P7-NR-011, 012, 033, 042,
   044) — no fictional human authorship required, and the three existing stable IDs and keys stay
   stable through the wording change.
5. Record the owner's product approval, then freeze.

The one nonblocking follow-up: the comment at `pp-verb-patterns.js:61` describes its list as mirroring
`PRIVATE_RUNTIME_KEYS`, which remains exactly true, but a reader may now wonder where the Phase 4E
keys are. A phase permitted to touch shipping files could add a clarifying clause. It changes no
behaviour and was deliberately not done here under the no-shipping-changes boundary.
