# Priority 8 Phase 4C0 — human architecture adjudication

This report records the human resolution of the two architecture decisions left open by
`reports/priority-8-phase-4c0-architecture-freeze.md`. It is governance only: it changes
no frozen candidate key or implementation artifact and allocates no stable ID.

## 1. Starting architecture endpoint

The adjudication begins from the committed Phase 4C0 architecture endpoint:

| Check | Observed endpoint |
|---|---|
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `e30cd0cff83937f9b8c76386a7ff984b9c719844` |
| Subject | `Priority 8 Phase 4C0 freeze canonical architecture` |
| Worktree before this report | clean |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |
| Architecture artifact | `reports/priority-8-phase-4c0-architecture-freeze.md` |
| Incoming gate | `HUMAN ARCHITECTURE DECISION REQUIRED BEFORE PHASE 4C1` |

The frozen Phase 4C0 architecture, stable-ID policy, D01–D13 dispositions, and subphase
plan are the binding basis for this adjudication. Only HD-4C-01 and HD-4C-02 are resolved
here; no other disposition is reopened.

## 2. Human decision HD-4C-01

HD-4C-01 APPROVED

Add the canonical/runtime role `source`.

The approval resolves D01 and D06. The affected frozen source/provider family is:
`wracać`, `wrócić`, `wyjść`, `wyjechać`, `kupować`, `kupić`, and `zamawiać`.

## 3. HD-4C-01 rationale

The seven frozen rows express an origin or provider, whereas the Phase 4B `target` value
was a temporary coarse fallback and is directionally wrong for that meaning. The frozen
keys already encode the source/provider identity, so the accurate canonical role can be
adopted without changing identity keys. Existing released `target` rows describe genuine
targets and therefore require no migration. A first-class role also preserves the
canonical-to-runtime one-to-one model without introducing a row-name exception layer.

## 4. HD-4C-01 binding implementation consequence

In the later schema/content subphases identified by the frozen Phase 4C0 plan:

- canonical and runtime role vocabularies gain `source`;
- the seven approved source/provider rows use `source` while their frozen keys remain
  unchanged;
- all existing released `target` rows remain unchanged;
- `source` remains outside `ANIMATE_ROLES` unless later governed evidence requires a
  change;
- person-origin question wording may use existing wording mechanisms such as
  `questionOverridePl`;
- Phase 4B governance does not reopen.

This report does not implement any of those consequences.

## 5. Human decision HD-4C-02

HD-4C-02 APPROVED

Add the optional pattern-level structural field `requiredLexicalItems`.

The approval resolves D12. Its initial required use preserves lexical `udział` in
`brać udział w` plus Locative and `wziąć udział w` plus Locative.

## 6. HD-4C-02 rationale

The lexical item `udział` is required by the two constructions and must be present in
the generated learner-facing pattern. It is part of structural canonical pattern
identity/content: treating it only as explanation text would not preserve it through
promotion and rendering, while treating it as a fillable Accusative complement would
misrepresent the construction. An optional pattern-level structural field records the
constraint directly and mechanically without changing either frozen key.

## 7. HD-4C-02 binding implementation consequence

In the later schema/content subphases identified by the frozen Phase 4C0 plan:

- `requiredLexicalItems` is an optional pattern-level field in the structural dimension;
- it survives canonical promotion and runtime rendering;
- the two approved participation patterns preserve and render lexical `udział`;
- `udział` is not represented as a fake Accusative complement;
- the requirement is not reduced to `learnerExplanation` wording;
- Phase 4B governance does not reopen.

This report does not implement the field or modify canonical/runtime content.

## 8. Candidate-key confirmation

HD-4C-01 and HD-4C-02 change no frozen candidate key. No key is renamed, removed,
reassigned, reparented, reused, or added. The Phase 4B frozen semantic identity layer
remains intact.

## 9. Phase 4B governance confirmation

Phase 4B does not reopen. Both approvals operate within the architecture boundary frozen
by Phase 4C0, and neither changes the Phase 4B candidate-key inventory or ownership.
All other Phase 4C0 decisions and preservation boundaries remain binding.

## 10. Stable-ID allocation confirmation

This adjudication allocates **ZERO** stable IDs. It does not invoke the allocator, create
an ID mapping, print an allocated value, or persist an allocation. No synthetic concrete
ID example appears in this report.

## 11. Final D01–D13 governance status

| Debt | Final binding governance status |
|---|---|
| D01 | **Resolved — HD-4C-01 APPROVED.** Add canonical/runtime `source` for the seven frozen source/provider rows. |
| D02 | Settled as frozen: preserve direct-speech canonical support and implement it before canonical projection. |
| D03 | Settled as frozen: unrepresented generalized roles remain non-structural governance metadata. |
| D04 | Settled as frozen: `umówić się` appointment `KIEDY` remains outside structural canonical representation. |
| D05 | Settled as frozen: do not add `co do` plus Genitive capability or content in current Phase 4C. |
| D06 | **Resolved — HD-4C-01 APPROVED.** Keep existing role assignments and add exactly `source`. |
| D07 | Settled as frozen: no action for `pasować`; preserve the frozen `lexical-frame`. |
| D08 | Settled as frozen: preserve neutral register for `kochać` plus infinitive. |
| D09 | Settled as frozen: use generated canonical-projection invariants rather than legacy guard backfill. |
| D10 | Settled as frozen: preserve the canonical, provenance, stable-ID, and promotion architecture. |
| D11 | Settled as frozen: enforce metadata-only exclusion and positive lexical-identity invariants. |
| D12 | **Resolved — HD-4C-02 APPROVED.** Add structural pattern-level `requiredLexicalItems` and preserve `udział` in the two approved patterns. |
| D13 | Settled as frozen: preserve the `Czy mogę…?` packaging invariant without a new schema feature. |

No D01–D13 disposition remains open. Apart from the two approvals recorded here, no
Phase 4C0 disposition is reopened or altered.

## 12. Phase 4C1 entry gate

The human-decision prerequisite is satisfied. Phase 4C1 may now:

- verify the locked stable-ID allocator;
- create the private stable-ID mapping manifest;
- allocate the 611 new stable IDs deterministically;
- validate collisions, no-recycle behavior, and determinism;
- preserve all 154 existing released IDs.

Phase 4C1 must not:

- modify canonical runtime content;
- promote the 68 records;
- implement `source`;
- implement direct-speech schema support;
- implement `requiredLexicalItems`;
- change `formatVersion`;
- generate audio.

Those changes remain assigned to later subphases under the frozen Phase 4C0 plan.
Phase 4C1 remains subject to every other entry and stop condition in the architecture
freeze, including frozen-key equality, released-ID reproduction, deterministic
allocation, path confinement, and fail-closed handling of any mismatch.

READY FOR PHASE 4C1 STABLE-ID TOOLING DESIGN/IMPLEMENTATION
