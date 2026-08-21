# Priority 8 Phase 4A2-1 — Decision B: Direct-Speech Clause Representation

**Status:** OPTIONS AND RECOMMENDATION ONLY. No schema, runtime, or editorial-corpus change is made by this report. HUMAN DECISION REQUIRED before Phase 4B.

## 1. Current architecture

`complements[]` has exactly four locked types (`priority7_tooling.py` `COMPLEMENT_TYPES`, mirrored in `pp-verb-patterns.js` `COMPLEMENT_TYPES` line 150): `case`, `preposition-case`, `infinitive`, `clause`. The `clause` type requires `clauseKind` and forbids `case`/`preposition`. `clauseKind` is itself a closed enum:

```
CLAUSE_KINDS = {"ze", "czy", "zeby", "interrogative"}   # priority7_tooling.py line 64
CLAUSE_KINDS = ["ze", "czy", "zeby", "interrogative"]    // pp-verb-patterns.js line 167
```

Rendering is entirely table-driven, not hand-authored per clause kind: `CLAUSE_TOKENS` (`pp-verb-patterns.js` line 168) maps each `clauseKind` to a fixed Polish token (`ze: "że …"`, `czy: "czy …"`, `zeby: "żeby …"`, `interrogative: "pytanie …"`), and both `chipFor` (line ~485) and `headlineFor` (line ~533) look this table up generically — there is no clause-kind-specific branch anywhere in the rendering code beyond the table lookup itself.

There is no `direct-speech` value anywhere in `priority7_tooling.py`, `pp-verb-patterns.js`, or any schema/spec JSON in the repository (confirmed by full-repository search in Phase 4A-1).

## 2. Why the current contract is insufficient

Phase 3 evidence verifies direct speech as a real alternative construction for **8 of the frozen 68** full-pattern lemmas — `odpowiadać`, `czytać`, `pisać`, `napisać`, `powiedzieć`, `zgadzać się`, `polecać`, `radzić` — plus the metadata-only `przeczytać` (anchored by `czytać`, not itself one of the 68). The Phase 3B handoff's global constraint #9 is explicit and binding: **"Preserve exact clause distinctions: `że`, `żeby`, interrogative-dependent, and direct speech."** This reads as a requirement to preserve the distinction, not merely to document it in prose — and the other three distinctions (`że`/`żeby`/interrogative) are all preserved as real, projected `clauseKind` values today. Authoring cannot represent a verified direct-speech alternative as a `clause` complement for any of these 8 lemmas until the enum gap is resolved one way or another.

## 3. Options

### Option B1 — Add `direct-speech` to `clauseKind` (RECOMMENDED)
Add one value to the existing closed enum in both languages, and one entry to the JS `CLAUSE_TOKENS` table (e.g. a token representing a quoted utterance, such as `„…”`).

- Linguistic fidelity: direct speech is not a subordinate clause the way `że`/`żeby`/interrogative-dependent are (it is a quoted independent utterance, not introduced by a subordinator) — this is a real, if narrow, fidelity compromise: `clauseKind` becomes "the discriminator for a clause-shaped complement," not strictly "subordinating conjunction." However, structurally direct speech behaves exactly like the other three for every mechanical purpose the schema cares about (it fills the same complement slot, forbids `case`/`preposition`, is a closed discriminated alternative), and the task brief itself frames it as an evaluable `clauseKind` addition, not a rejected idea.
- Compatibility with locked complement types: **fully compatible** — no new complement type, no change to `COMPLEMENT_TYPES`, no change to the four-type architecture at all.
- Private/editorial schema changes: none beyond the enum widening (which is shared by editorial and runtime, since `CLAUSE_KINDS` is one constant used by both validators).
- Frozen schema changes: `CLAUSE_KINDS` in `priority7_tooling.py` (+1 member).
- Runtime schema changes: same constant is shared; no separate runtime-only change.
- JS parser/loader changes: `CLAUSE_KINDS` (+1 member) and `CLAUSE_TOKENS` (+1 entry) in `pp-verb-patterns.js`. No new branch in `chipFor`/`headlineFor` — both already key off `CLAUSE_TOKENS[complement.clauseKind]` generically (lines ~486, ~535), so a new table entry is sufficient; no new rendering code path is needed.
- Rendering implications: minimal — the existing "`+ <token> · Clause`" chip/headline shape is reused unchanged; only the token text is new.
- ID consequences: none — `clauseKind` is never part of any ID seed (`allocate_pattern_id` seeds on `meaning_id`+`pattern_key` only).
- `formatVersion` consequences: adding a legal value to a previously-closed enum is a schema-shape change under this project's own framing (§7) — see decision summary. Recommend increment.
- `patternDataRevision` consequences: increments with the batch that ships the first pattern actually using `direct-speech` (tied to the same revision-3 expansion).
- Test changes: any test that enumerates `CLAUSE_KINDS` verbatim (or asserts Python/JS parity, per the 4A-1 risk review §6 open question) must be updated in the same change; a parity test between the two `CLAUSE_KINDS` lists is worth adding as part of this change if one does not already exist (4A-1 risk review flagged this as unconfirmed either way).
- Backwards compatibility: an already-shipped old JS bundle would reject a runtime document containing `direct-speech` (strict enum rejection, `inList(CLAUSE_KINDS, ...)`), so the JS loader and the runtime content must ship together — this is already true of this single-repository, same-release deployment model, but is worth stating explicitly as a deployment-ordering constraint, not a data-only migration.

### Option B2 — Represent direct speech via an existing `clauseKind` plus a qualifier field
E.g., reuse `ze` (or another existing value) and add a boolean/qualifier such as `quotative: true` to distinguish direct speech from ordinary `że`-content clauses.

- Linguistic fidelity: **worse than B1**, not better — this would mislabel a verified direct-speech construction as if it were a `że`-content clause with an extra flag, which is a more inaccurate representation of the linguistic fact than simply adding a distinct enum value. None of the four existing `clauseKind` values are a linguistically honest carrier for direct speech (unlike `że`/`żeby`/`czy`/interrogative, direct speech has no subordinator at all).
- Compatibility with locked complement types: compatible (still `clause` type), but only by overloading an existing value's meaning.
- Schema changes: adds a new complement-level field (`quotative` or similar) in addition to reusing `clauseKind` — this is not smaller than B1 (still touches both validators, both languages, plus a new field rather than one enum value), and is linguistically weaker.
- **Not recommended** — B2 is both larger in footprint than it first appears and less truthful than B1.

### Option B3 — Represent direct speech as a fifth complement type
Add `direct-speech` to `COMPLEMENT_TYPES` instead of to `CLAUSE_KINDS`.

- Linguistic fidelity: arguably no better than B1 (direct speech still fills the same complement slot as a clause, just under a new top-level type name).
- Compatibility with locked complement types: **conflicts with the locked four-type architecture** — the task brief flags this explicitly as likely unacceptable, and this audit agrees: nothing about direct speech's grammatical behavior (forbids `case`/`preposition`, is a closed discriminated alternative, needs exactly the same rendering shape as `clause`) distinguishes it structurally from the existing `clause` type. Introducing a fifth type to carry information the fourth type (`clause` + `clauseKind`) can already carry is unjustified structural growth.
- Footprint: **strictly larger than B1** — `COMPLEMENT_TYPES` (+1, both languages), new complement-shape validation branch analogous to the `clause`/`infinitive` branches (what does `direct-speech` forbid/require? — needs its own rule, since it isn't automatically covered by the existing `clause`-type rule which requires `clauseKind`), new rendering branches in `chipFor`/`headlineFor` (cannot reuse the existing `clause` branch, since that branch is keyed on `complement.type === "clause"`), plus everywhere `COMPLEMENT_TYPES` is enumerated (search bar cast, distractor logic in `pp-answer.js`/`pp-distractor.js` if those touch verb patterns — not confirmed in this audit but plausible additional surface).
- **Not recommended** — larger footprint than B1 for no linguistic-fidelity gain, and directly risks the locked four-type architecture the task brief protects.

### Option B4 — Keep direct speech governance-only; do not project it as a learner pattern
Record the 8 (+1 metadata-only) verified direct-speech identities in governance/editorial notes only; never author a corresponding `clause` complement in any released pattern.

- Would this violate the Phase 3 completeness/handoff rule? **Yes.** Handoff global constraint #9 ("Preserve exact clause distinctions: `że`, `żeby`, interrogative-dependent, and direct speech") is phrased identically to and alongside the other three distinctions, all of which *are* projected as real patterns today. Silently omitting only the fourth distinction — for which Phase 3 evidence exists for 8 full-pattern lemmas — would under-represent verified evidence Phase 3 explicitly and repeatedly documented (`priority-8-phase-3-batch-02.md`, `-batch-04.md`, `-batch-04-risk-review.md`, `-batch-06.md`, `-batch-06-risk-review.md`).
- Schema/runtime/JS/test changes: **none** — this is precisely B4's appeal, and precisely why it is not defensible on its own: zero footprint is achieved only by not doing the thing the freeze requires.
- **Not recommended as a permanent solution.** B4 could be an acceptable *temporary* sequencing choice (ship the 68 first without direct-speech patterns, add direct-speech in a fast-follow revision) only if the human explicitly accepts that interim under-representation — but as the final architecture, it contradicts the handoff's own binding language.

### Option B5 — No materially better architecture found
No representation smaller than B1 was found that both preserves the four-distinction requirement and stays inside the locked four-complement-type architecture.

## 4. Recommendation

**Recommend Option B1** — add `direct-speech` to `CLAUSE_KINDS` in both `priority7_tooling.py` and `pp-verb-patterns.js`, plus one `CLAUSE_TOKENS` entry. This is the minimum truthful solution: it is the smallest change (one enum value + one lookup-table row, no new complement type, no new rendering branch, no ID impact), it does not touch the locked four-complement-type architecture, and it is the only option among B1–B4 that both preserves handoff constraint #9 and does not misrepresent the linguistic fact (unlike B2) or over-grow the schema (unlike B3).

## HUMAN DECISION REQUIRED

1. Approve adding `direct-speech` as a fifth `clauseKind` enum value (Option B1).
2. Approve/author the exact learner-facing token/rendering text for a direct-speech clause chip (e.g. how a quoted utterance is represented in the `CLAUSE_TOKENS` table — this is a product/UI wording decision, not resolved here).
3. Confirm whether a Python/JS `CLAUSE_KINDS` parity test should be added alongside this change (4A-1 risk review §6 flagged this as an open, unconfirmed test-coverage question).
4. Confirm `formatVersion` increments for this schema-shape addition (see decision summary).
