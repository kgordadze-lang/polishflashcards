# Priority 7 — Provenance and Review Specification

**Phase:** 1 specification, amended by Phase 4E and Phase 4E.1

**Status:** fail-closed review workflow locked; two release modes, both fail-closed

> **Phase 4E amendment.** Sections 1–10 below describe the original fully human-reviewed release
> chain. That chain is unchanged and remains available. Section 11 adds a second, equally
> fail-closed chain for a project maintained by one owner without access to a human external
> verifier, a second human native reviewer, or a human example author. Read §11 alongside §§1–10;
> where §11 states a rule for the solo-maintainer mode, that rule is additional, never a relaxation
> of the human-reviewed mode. The statement in §1 that "AI agreement is never a review event"
> is narrowed by §11.3, and only there: structured, corroborated, evidence-bound model review
> becomes a recordable event of its own named kind, and it never becomes native review.
>
> **Phase 4E.1 amendment.** Phase 4E shipped `reference-verification` requiring a human
> `reviewerRef` while `editorial-review` required a nonhuman `actorRef`. That mismatch would have
> forced the project to name a person — realistically the owner — as a human reference verifier
> they are not. Phase 4E.1 moves `reference-verification` onto its own nonhuman
> source-analysis actor in the solo-maintainer mode, and removes the stage from the human chain
> entirely. Nothing had been written under the mode when the mismatch was found, so no recorded
> event changed meaning. The human-reviewed chain is untouched, and the solo chain became
> **stricter**: the two nonhuman tiers must now be independent identities (§11.3), and every
> evidence condition is unchanged. Where §11 below says "human" of `reference-verification`,
> §11.3 as amended governs.

## 1. Separation of evidence and approval

Repository material, Mędak research, contemporary references, native review, product approval, and original example authorship are different claims. No single one substitutes for another. AI agreement is never a review event and never advances a state.

The source dictionary remains research evidence, not copy-ready content. Store locators and fact classifications, never passages, screenshots, source examples, definitions, synonym sets, or the full index.

## 2. Evidence record

Every pattern candidate has one or more `evidence` records:

```json
{
  "sourceId": "repository",
  "sourceKind": "repository",
  "locator": "data-grammar.js#review-stable-locator",
  "factType": "complement-frame",
  "checkedAt": "2026-08-08",
  "note": "Optional concise internal scope note; no copied passage."
}
```

| Field | Required | Allowed values / meaning | Learner-facing | Change / validation |
|---|---:|---|---:|---|
| `sourceId` | yes | stable internal reference identifier; non-empty ASCII-safe token | no | resolves to approved internal source registry |
| `sourceKind` | yes | `repository`, `medak-research`, `contemporary-reference`, `contemporary-corpus` | no | closed enum; source registry must agree |
| `locator` | yes | file+stable ID, entry/page/section, URL/edition locator, or corpus query reference | no | must permit rechecking without embedding content |
| `factType` | yes | `lemma`, `meaning`, `complement-frame`, `usage-register`, `contrast`, `cefr` | no | closed enum |
| `checkedAt` | yes | ISO `YYYY-MM-DD` | no | real date, not in future at validation time |
| `note` | no | max 240 characters; summary only | no | prohibited from reproducing protected text |

`sourceKind` makes the required distinctions queryable without building a bibliographic system. Full citation details belong in a small controlled source registry owned by editorial tooling, not repeated per pattern. Mędak headword-only evidence can support `lemma`, not a detailed `complement-frame` unless the available detailed entry was actually reviewed.

## 3. Example origin

Each example contains:

```json
{
  "origin": {
    "kind": "original",
    "authorRef": "human-author-record",
    "authoredAt": "2026-08-08"
  }
}
```

Production learner examples may be genuinely original or explicitly approved reuse of independently originated existing Po polsku content. Source-derived or lightly paraphrased dictionary examples remain prohibited.

For `kind: original`, `authorRef` and `authoredAt` are required and `repositorySource` is forbidden. `authorRef` resolves only inside the private editorial workflow.

For `kind: repository-reuse`, `repositorySource` is required and `authorRef`/`authoredAt` MUST be omitted. A future private provenance specification would need to define any different, separately justified field. The exact shape is:

```json
{
  "origin": {
    "kind": "repository-reuse",
    "repositorySource": {
      "kind": "card",
      "id": "existing-stable-card-id",
      "field": "ex"
    }
  }
}
```

Allowed stable source entities are `card` and `drill`. Card `field` is `pl` or `ex`; drill `field` is `prompt` or `answer`. The dedicated validator resolves kind, ID, field presence, and exact equality with the example sentence. Scenario/teaching prose without an exact stable utterance entity is not eligible for repository reuse until such identity exists. Pattern-level `contentRefs` never substitute for this per-example provenance.

The complete origin object is included in native and product review fingerprints. It is excluded from the public runtime example projection. The Phase 1 example artifact uses `specification-fixture`, allowed only by the report-time fixture Schema and forbidden in editorial production candidates/runtime.

## 4. Review states

Closed `reviewState` values:

| State | Meaning | Learner eligibility |
|---|---|---|
| `research` | Candidate assembled from preliminary evidence; meaning/frame may be wrong | none |
| `externally-verified` | A competent editor checked the exact claim against a contemporary reputable reference (and corpus where needed) | none |
| `native-reviewed` | A competent native Polish reviewer accepted lemma, sense, relation type, complements, questions, register, examples, glosses, CEFR, and proposed activities | none until owner approval |
| `approved` | Product owner accepted the exact reviewed record and scope | only explicitly eligible surfaces |
| `deferred` | Plausible/valid but not currently suitable or sufficiently resolved | none |
| `rejected` | Claim or treatment was rejected | none |

Minimum forward path is:

```text
research → externally-verified → native-reviewed → approved
```

At any nonterminal state, a human review may set `deferred` or `rejected`. Reopening `deferred` creates a new external-verification event and returns to `externally-verified`; rejected treatment is not silently reopened—create a corrected candidate or explicit owner-authorized reopen record.

## 5. Review events and authority

Each state transition is justified by append-only `reviewEvents`:

```json
{
  "kind": "native-linguistic",
  "decision": "accept",
  "scopeVersion": 1,
  "scopeDigest": "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "reviewerRef": "human-reviewer-record",
  "reviewedAt": "2026-08-08"
}
```

| Field | Required | Allowed values |
|---|---:|---|
| `kind` | yes | `external-verification`, `native-linguistic`, `product-approval`, `reopen`, `correction` |
| `decision` | yes | `accept`, `changes-requested`, `defer`, `reject` |
| `scopeVersion` | acceptance events only | integer `1`; identifies the exact projection rules below |
| `scopeDigest` | acceptance events only | `sha256:` plus 64 lowercase hexadecimal characters |
| `supportingEvidenceDigests` | accepted external verification only | non-empty, sorted unique array of full evidence-record digests |
| `reviewerRef` | yes | reference to an identified human with the required role |
| `reviewedAt` | yes | ISO date |
| `note` | yes for non-accept and for `reopen`/`correction`; optional for stage acceptance | concise reason, no source passage |

Only accepted `external-verification`, `native-linguistic`, and `product-approval` events carry scope fields. `reopen` and `correction` are audit events, require a note, and do not establish a review stage. A non-`accept` decision requires a note and MUST NOT carry a scope digest.

Authority rules:

- `external-verification`: competent linguistic/content researcher; must cite contemporary evidence.
- `native-linguistic`: identified native Polish reviewer competent for the editorial task; cannot be an AI identity.
- `product-approval`: named product owner or delegated content authority.
- The same human MAY perform multiple roles only if the owner explicitly allows it, but all three events remain separate.
- Approval covers only the exact canonical projection proven by its current digest.

## 6. Deterministic review-scope fingerprints

### 6.1 Canonical serialization and digest

For each pattern, the validator constructs a stage-specific JSON projection. It does not hash the source file text.

1. Validate all source strings as Unicode NFC and all values against the closed schema; floating-point numbers are forbidden in reviewed projections.
2. Include every property named for that stage below. An absent optional property is represented as JSON `null` in the projection, so omission and presence cannot drift invisibly.
3. Preserve semantically ordered arrays: `glossesEn`, `complements`, `examples`, and `errorNotes`. Within an error note, preserve the authored order of its evidence references.
4. Sort set-like arrays lexicographically by Unicode code point: `aspectPartnerIds`, `aspectEquivalentPatternIds`, and `activityEligibility`. Sort `contentRefs` by `(kind,id,purpose)`.
5. Serialize the projection using RFC 8785 JSON Canonicalization Scheme, with no BOM or trailing newline.
6. Hash the exact UTF-8 bytes with SHA-256 and store all 64 lowercase hexadecimal characters prefixed by `sha256:`.

`scopeVersion: 1` fixes these rules. Any future projection change increments the scope version and requires re-acceptance; it does not reinterpret old digests.

Each evidence record has its own digest using the same NFC → RFC 8785 → SHA-256 rule over the entire record, including `note`. An accepted external event records the exact supporting evidence digests. Adding a new corroborating evidence record does not invalidate an accepted claim while every originally pinned record remains byte-semantically unchanged and resolvable. Adding separate append-only audit metadata outside evidence records may also be non-invalidating. Editing or removing any field—including `note`—of a pinned evidence record changes/breaks its digest and invalidates that external acceptance until reverification.

Editorial `errorNotes[].evidenceRefs` remain numeric authoring references, but raw indexes are not claim-bearing values in native/product fingerprints. After structural validation, each index is resolved against the current pattern evidence array and represented in the canonical error-note projection by the complete evidence-record digest. The ordered digest list is stored as `evidenceDigests`; it is `null` when the optional authoring property is absent. Therefore reordering evidence so a numeric index resolves to another record changes native/product scope, while moving the same evidence record and updating the index leaves those scopes unchanged. Appending unrelated evidence at the end remains non-invalidating. Editing referenced evidence both breaks any external pin and changes the native/product claim fingerprint. This pre-release clarification retains `scopeVersion: 1`; no real acceptance exists to reinterpret.

### 6.2 Common parent projection

Every stage includes this complete ancestor/identity projection:

```text
scopeVersion
lemma: id, canonicalLemma, displayLemma|null, reflexive, aspect,
       sorted aspectPartnerIds|[]
meaning: id, key, glossesEn, internalScope
pattern: id, key
```

Because every descendant pattern digest includes its current lemma and meaning fields, changing canonical/display lemma, reflexivity, aspect/partners, meaning glosses, scope, keys, IDs, or ownership invalidates affected descendant acceptance automatically. Review state is not duplicated onto lemma or meaning.

### 6.3 External-verification scope

The external projection is the common projection plus:

```text
relationType
complements (including type, case/preposition/clauseKind, required, role,
             questionOverridePl|null)
sorted aspectEquivalentPatternIds|[]
usage (priority, register, note|null)
```

This stage verifies the lexical/constructional claim, participant structure, optionality, question override, aspect relationship, and contemporary usage/register claim. It excludes learner sequencing and copy.

### 6.4 Native-linguistic scope

The native projection contains the entire external projection plus:

```text
cefr
teachingStatus
learnerExplanationEn
examples (id, key, pl, en, exact origin, audioEligible)
errorNotes (kind, incorrectForm, guidanceEn,
            ordered resolved evidenceDigests|null)|[]
sorted activityEligibility
```

This makes native acceptance sensitive to the exact learner gloss/scope inherited from the meaning, explanation, Polish/English examples, error claims, CEFR, production disposition, proposed activity use, and audio eligibility.

### 6.5 Product-approval scope

The product projection contains the entire native projection plus sorted `contentRefs|[]`. It therefore covers every deployable claim-bearing field: canonical/display lemma, reflexivity/aspect, meaning gloss/scope, relation type, complements, CEFR, teaching status, usage, explanation, examples/origin/audio eligibility, error notes, activity eligibility, and integration references.

Explicitly excluded from all scope projections are `reviewState`, `reviewEvents`, raw evidence records, raw numeric evidence indexes, reviewer/source registry records, `patternDataRevision`, array placement among sibling entities, and append-only frozen/tombstone audit history. A complete evidence digest is nevertheless included when an error claim references that record, so all evidence fields—including `checkedAt`—are bound indirectly without copying private evidence into the projection. Other excluded material is validated separately and cannot alter learner or linguistic meaning without a covered field also changing.

### 6.6 Validity and invalidation

`reviewState` is stored for fail-closed collection but is valid only if the dedicated validator can recompute and match the required current acceptance events:

- `externally-verified`: current external digest matches and every cited evidence digest resolves;
- `native-reviewed`: external remains valid and current native digest matches;
- `approved`: external and native remain valid and current product digest matches.

If an external-covered field changes, the maximum valid state falls below `externally-verified`. If only a native-covered field changes, it falls to `externally-verified`. If only a product-only field changes, it falls to `native-reviewed`. The stored state must be changed accordingly or validation fails. A released `relationType` change additionally requires a new pattern ID and tombstone because it is structural identity.

## 7. Deterministic gates and corpus admission

The private editorial canonical record contains review state, events, evidence, origins, registries, and digests. After full validation, an approval/projector admits only current-digest-valid `reviewState: approved` records with `active-production` or `recognition-only`, removes private/editorial fields, validates a separate runtime schema, and only then emits public `content/verb-patterns.json`.

If Phase 2B is authorized, `editorial/verb-pattern-candidates.json` is a working name inside the isolated local Priority 7 workflow only. “Not loaded” and the directory name are not privacy controls in a static-site repository. The editorial file MUST be absent from the production/public repository transfer set and final site tree. A durable private home beyond the local workflow is a separate Phase 2B operational decision required before real authoring/review.

Before active grammar/Type It, `approved`, `active-production`, an A1–B1 production CEFR, native-accepted deterministic prompts, and explicit activity eligibility are all required. Before pronunciation audio, the exact example string must be inside the current owner-approved scope, `audioEligible: true`, and pass separate audio/native listening QA.

Changing an approved structured fact, learner wording, example, usage, CEFR, or eligibility invalidates the existing product-approval coverage. The state returns to the latest still-valid stage:

- product-only integration-reference change: at most `native-reviewed`, followed by product approval;
- explanation/example/CEFR/eligibility change: at most `externally-verified`, then repeat native and owner review;
- linguistic/structural/parent change: below `externally-verified`, then repeat every stage;
- a new corroborating evidence record or separate append-only audit metadata: state may remain `approved` only while every evidence digest pinned by existing acceptance remains unchanged and resolvable.

## 8. Required contemporary checks

Every pilot pattern needs evidence beyond headword presence. Contemporary corpus evidence is required when frequency, register, optionality, competition between constructions, or datedness affects teaching. Required native review explicitly covers the Phase 0 inconsistencies around `nie lubię` and `chcieć` before any affected pattern ships.

The fixtures `płacić`, `być`, `podobać się`, and `zależeć` require a recorded decision on relation type and learner wording. `to jest` remains an out-of-corpus grammar contrast and requires no fake pattern approval. Aspect and reflexive links require separate explicit review; they are not implied by shared roots or repository `pair` strings.

## 9. Privacy and retention

The private editorial record may store stable reviewer/source references, never unnecessary biography/contact data. Controlled registries are access-limited. Review history is append-only and retained with private frozen/audit records. The public runtime projection contains no reviewer/source references, review events/digests, evidence, origin/author references, or registries.

## 10. Decision log

| Decision | Alternatives | Why selected | Reopen trigger |
|---|---|---|---|
| Six fail-closed states | one approved Boolean; many workflow states | enough to separate evidence, native judgment, owner decision, and terminal outcomes | editorial process cannot express a real transition |
| Append-only events, current state, and scoped SHA-256 | current state only; whole-file revision | machine-verifiable exact coverage without duplicating state on parents | scope projection changes require new `scopeVersion` |
| Lightweight evidence refs | full bibliography/passages | recheckable and rights-safe | source registry proves insufficient |
| Pinned digest covers the complete evidence record | exclude mutable notes from digest | edits/removals, including note edits, invalidate acceptance; separate new evidence can corroborate without rewriting history | only an equivalently tamper-evident evidence model |
| Per-example typed `repositorySource` | infer origin from pattern `contentRefs` | exact card/drill utterance is independently resolvable and fingerprinted | stable repository entities gain a stronger universal source-reference type |
| Descendant digest includes parent projection | state on every entity | parent changes invalidate every affected pattern mechanically with one state location | only if entity-level approvals later have independent consumers |
| Private editorial authority projected to approved-only public runtime | expose review/audit fields to runtime; admit externally/native-reviewed candidates | runtime safety is decided before projection and private provenance never ships | only a future secure authoring service may replace the isolated file split |
| Human-role requirement for the `human-reviewed` mode | AI consensus | mandatory linguistic accountability | not reversible for this mode; a project without the human roles uses §11 instead of weakening this one |
| A second named mode rather than relaxing the first | loosen the human-role checks; ship unreviewed | the two modes carry different assurance and must stay distinguishable forever | only if human native review becomes routinely available, which would make §11 unnecessary rather than wrong |

## 11. Solo-maintainer reference-backed release mode (Phase 4E)

### 11.1 Why this mode exists

The chain in §§4–5 assumes four available humans: an external verifier, a native reviewer, a product
approver, and an example author. This project has one owner and one genuine native reviewer
(`native-reviewer-001`, "AB") who reviewed the Phase 4A package and is not a standing resource.
Under §§4–5 the project can never release, because `native-reviewed` is unreachable without a prior
human external verification that no one is available to perform.

Two dishonest escapes were available and are both rejected: recording model output in human
reviewer fields, and recording model-drafted sentences as human-authored. Phase 4E takes the third
option — naming the actual process truthfully and gating it explicitly.

### 11.2 Declaring the mode

Every pattern may carry `releaseMode`, one of:

| Value | Chain | Meaning |
|---|---|---|
| `human-reviewed` | `external-verification` → `native-linguistic` → `product-approval` | §§4–5 unchanged |
| `solo-maintainer-reference-backed` | `reference-verification` → `editorial-review` → `product-approval` | §11 |

The field is optional and **absence means `human-reviewed`**: no existing record can drift into the
weaker chain by omission. An unrecognised value fails closed twice — the closed enum rejects it, and
an unknown mode establishes no stage, so the pattern cannot rise above `research`.

The mode is recorded on the frozen `policy` row for active patterns and on the frozen `reviewHistory`
row for every pattern including retired ones, with parity enforced between them. A tombstoned
pattern keeps no policy row, so the history is the durable home for the governance its events ran
under.

### 11.3 The three solo-maintainer stages

**`reference-verification`** replaces `external-verification`. **(Phase 4E.1)** It is performed by a
**nonhuman source-analysis workflow actor**, not by a person: the event requires `actorRef`, forbids
`reviewerRef`, and its `actorRef` must resolve in the `editorialActorRegistry` to a record stating
`human: false` and carrying the `reference-verification` role. No human reference-verifier role is
required, offered or implied by this stage, because the project has no such person and will not
invent one.

The actor records only **that the project's reference-verification workflow ran**. It confers no
authority of its own, and it is the strictest evidence gate in either mode. Beyond every §5
requirement it additionally demands that the pinned evidence include at least one record whose
`factType` is `complement-frame` or `meaning`. Headword-presence evidence alone can never verify a
pattern. WSJP PAN is the preferred contemporary reference; Mędak remains research evidence under the
existing §2 rights rules and cannot carry a non-`lemma` fact without a reviewed detailed entry. No
evidence, lemma-only evidence, headword-only Mędak evidence and stale evidence each fail closed
exactly as before. Reaching this stage sets `reference-verified`, never `externally-verified` — no
human external verifier was involved and the state name must not claim one. `reference-verified`
means "the recorded reference evidence passed the reference-verification workflow", and never
"a human verified this externally".

**`reference-verification` is not a stage of the human-reviewed chain at all.** Under
`human-reviewed`, tier 1 is `external-verification` by an identified human, and a
`reference-verification` event is refused outright rather than merely not advancing the chain
(`REVIEW_STAGE_NOT_IN_MODE`). Leaving it representable there would make a human-reviewed history
ambiguous about whether a person verified the claim. Because an absent, malformed or unknown
`releaseMode` resolves to `human-reviewed`, an unreadable mode also cannot leave a nonhuman
verification standing.

The applicable release mode is therefore resolved **before** the event schema is closed: which of
`actorRef` and `reviewerRef` an event may carry is a consequence of the governing mode, not of the
stage name alone. The same rule is applied to the frozen release history, which carries its own
`releaseMode`, so a released history is held to exactly the contract the editorial record was.

**`editorial-review`** replaces `native-linguistic` and is performed by a nonhuman actor. Its event
is structurally incapable of naming a person: it requires `actorRef` and forbids `reviewerRef`.
`actorRef` resolves only in a separate `editorialActorRegistry` whose records must state
`human: false` and carry the `editorial-review` role; the reviewer, author and actor registries may
not share an identity key. An acceptance additionally requires:

- `corroboratingActorRefs` — at least one *distinct* registered nonhuman actor, so no single model's
  opinion is ever release-authoritative on its own;
- `findings` (optional) — structured `{severity, summary, resolved, resolutionNote}` records. An
  acceptance carrying an unresolved `high` finding is refused. A resolved finding must state how it
  was resolved, which is where model disagreement is reconciled on the record.

Reaching this stage sets `editorial-reviewed`, never `native-reviewed`.

**`product-approval`** remains **human and mandatory**, and is stricter in this mode: the approver's
registry record must list the mode in `acknowledgedReleaseModes`. The owner cannot approve under the
weaker chain without having recorded that they know which assurance they are accepting. The stage
requires `reviewerRef` and forbids `actorRef`, so it can never become machine-performed, and a
release without it cannot reach `approved`. The owner remains responsible for learner-facing
usefulness, UX, the inclusion decision, the release-mode acknowledgement, and acceptance of the
solo-maintainer limitations in §11.10.

**(Phase 4E.1)** The solo owner performs exactly one review stage. Where one person does perform two
stages — the human-mode case of the same person verifying externally and then approving — the
pre-existing `ownerAllowsMultipleRoles` allowance applies unchanged and must be explicit.

**Actor independence (Phase 4E.1).** The two nonhuman tiers exist to corroborate each other, so one
identity may not perform both: the actor of a `reference-verification` acceptance may not appear as
the actor of an `editorial-review` acceptance, nor among its `corroboratingActorRefs`, anywhere in
the same pattern's history (`REVIEW_ACTOR_INDEPENDENCE`). This composes with, rather than duplicates,
the corroboration rule below: the minimum valid solo chain uses three distinct nonhuman identities —
a reference actor, an editorial actor, and at least one independent corroborator.

**Actor roles name workflows, not vendors (Phase 4E.1).** An actor record may hold only the roles
`reference-verification`, `editorial-review` and `example-generation`; any other value, above all one
borrowed from the human vocabulary, is refused (`EDITORIAL_ACTOR_ROLE_UNKNOWN`). Stable actor
identities describe the workflow role they perform — `priority7-reference-analysis`,
`priority7-independent-editorial-review` — and no release validity depends on a commercial model or
vendor name. Model and run identifiers may be recorded on the actor record as private audit
metadata; nothing in the schema requires them, reads them, or reproduces a release from them.

### 11.4 Scope tiers are shared; authority is not

The two chains cover the same three locked scope tiers, so `scopeVersion` stays `1` and no historical
digest is reinterpreted. `reference-verification` projects exactly the `external-verification` scope,
and `editorial-review` projects exactly the `native-linguistic` scope. Their digests are therefore
identical for the same content, which is deliberate and safe: currency is keyed on the *event kind
the declared mode requires*, so relabelling an event as the other chain's kind establishes nothing.
A mode switch on an already-approved pattern mechanically invalidates the approval for the same
reason.

### 11.5 Human review as strengthening evidence

Human native review remains fully representable in either mode and is never required by the
solo-maintainer mode. A `native-linguistic` event on a solo-maintainer pattern is recorded and
validated in full, but it does not advance the chain — no AI-reviewed item is ever backfilled into
AB's genuine Phase 4A review, and AB's review is never diluted into an editorial one.

The asymmetry is deliberate: human review can always **block** and is never required to **pass**. A
human native `reject` is terminal in both modes, and a human native `changes-requested` invalidates
its scope tier and everything above it, exactly as the chain's own stage would.

The frozen `releaseAuthorization` record reports genuine human coverage per pattern, derived from the
retained history rather than asserted:

| Field | Meaning |
|---|---|
| `releaseModes` | the governance modes the admitted patterns actually declared |
| `humanVerifiedPatternIds` | **(Phase 4E.1)** patterns over which a current human `external-verification` acceptance still stands |
| `humanNativeReviewedPatternIds` | patterns over which a current human `native-linguistic` acceptance still stands |

Both coverage lists are stated per pattern rather than per release, because a mixed release is
otherwise ambiguous about which patterns a person actually saw. Under the solo-maintainer mode both
are ordinarily **empty**, and that emptiness is the honest statement: reference verification and
editorial review were performed by nonhuman workflows against authoritative sources, and no human
external verification or native review is being claimed. A release therefore cannot describe itself
as human-externally-verified, human-reference-verified or native-reviewed unless the corresponding
human events exist in its own retained history; every field is recomputed at validation time and a
forged value is refused (`FROZEN_RELEASE_AUTHORIZATION_PARITY`).

Coverage is a live digest claim: if the text changes and is re-reviewed through the solo chain, the
pattern silently stops being reported as human-verified or human-native reviewed rather than carrying
a stale badge. Truthfulness runs both ways — a genuine human event on a solo-maintainer pattern is
reported, not discarded.

**(Phase 4E.1)** The frozen history retains the distinction structurally, not only descriptively: a
released `reference-verification` event still carries `actorRef` and cannot carry `reviewerRef`, and
substituting one for the other, or relabelling the event as `external-verification`, is refused by
the frozen validator rather than silently reinterpreted.

### 11.6 Example provenance

`origin.kind` gains `editorial-generated`:

```json
{
  "origin": {
    "kind": "editorial-generated",
    "generatorRef": "editorial-actor-record",
    "adoptedAt": "2026-08-13"
  }
}
```

It requires `generatorRef` (resolving in the nonhuman actor registry, with the `example-generation`
role) and `adoptedAt`, and forbids `authorRef`, `authoredAt` and `repositorySource`. It is neither
repository reuse nor human authorship, and it never claims a person wrote the sentence. The existing
`original` guard is untouched: a human author record is still required and a nonhuman one is still
refused, so no model can be laundered into authorship and no owner is asked to adopt authorship of a
sentence they did not write. As with every origin, it is included in the editorial and product
review fingerprints and excluded from the public runtime projection.

### 11.7 English translations

Authorship and provenance concern `example.pl`. `example.en` is an editorial translation of it and
carries no separate authorship claim unless one is separately attributed. This has consequences that
are now codified rather than implied: an English-only edit leaves the `reference-verification` (and
`external-verification`) scope byte-identical, so source verification survives it, while the
`editorial-review` (and `native-linguistic`) and `product-approval` scopes both change, so the
learner-facing acceptance and the owner's approval must be redone. The stored state falls to
`reference-verified` or `externally-verified` accordingly.

### 11.8 Release gate

A release under this mode requires all of: a current `reference-verification` acceptance pinning
resolvable contemporary evidence including pattern-or-meaning-level source evidence; a current
corroborated `editorial-review` acceptance with no unresolved blocking finding; a current
`product-approval` acceptance by an owner who has acknowledged the mode; `reviewState: approved` with
every scope digest recomputing; valid example provenance for every example; and every pre-existing
freeze, stable-ID, tombstone, revision-contract and public-runtime privacy protection satisfied
unchanged. Human native review, where present, is recorded as additional evidence and is not part of
this list.

### 11.9 One acceptance per stage per review round

This rule applies to **both** modes and is stated here because Phase 4E is where it was first
enforced mechanically.

A stage acceptance is refused when that tier already stands over the identical scope digest with no
intervening governance event. An identical digest proves that nothing the tier reviews has changed,
so a repeated acceptance establishes nothing the first one did not, and an append-only history must
not absorb it silently.

A tier is legitimately reopened for re-acceptance by any of: an owner-authorized `correction`; a
`reopen`; a `changes-requested` at that tier or below; a `defer` or `reject`; an acceptance at a
lower tier; the completion of the round by product approval; or an edit that moves the tier's scope
digest. Product approval reopens tiers 1 and 2 but not itself, so a repeated approval remains
refused until a new verification opens the next round.

The distinction the rule draws is between repeating a stage *within* a round, which is refused, and
starting a new round, which is not. `reviewState` is unaffected: this is a structural constraint on
history, checked wherever a history is read — the editorial record and the frozen envelope alike.

Malformed governance values are normalised before use and reported as schema issues, never coerced
and never permitted to raise: a `releaseMode` that is not a known string resolves to the strictest
chain for every downstream decision while the closed-enum check refuses the record.

### 11.10 What this mode does not claim

This mode provides materially less independent human assurance than `human-reviewed`.

`reference-verification` under this mode is a **nonhuman reference-analysis workflow backed by
explicit authoritative evidence**. It is explicitly **not**:

- human external verification;
- professional linguistic review;
- native-speaker review;
- an authority derived from any model's own competence — the cited sources carry the claim, and the
  actor records only that the workflow ran.

`editorial-review` is likewise nonhuman and is **not** native review. Reference-backed model review
can be wrong in ways a native speaker would catch immediately. The single human judgement in the
chain is the owner's product approval, which is a usefulness and inclusion decision rather than a
linguistic one.

`human-reviewed` remains the stronger independent-human-assurance path and is the mode to use
whenever the human roles are actually available. The mode is a truthful description of a real
process, not an equivalent of professional linguistic review, and the `releaseModes`,
`humanVerifiedPatternIds` and `humanNativeReviewedPatternIds` fields on every release exist so that
no later tool or reader can mistake one for the other.
