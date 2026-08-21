# Priority 8 Phase 4A-1 — Stable-ID Architecture Audit

**Scope:** factual inventory of the ID namespaces relevant to Verb Patterns. No IDs are allocated, changed, or recomputed in this report.

## 1. ID namespaces (OBSERVED FROM SCRIPT/VALIDATOR: `priority7_tooling.py` `ID_RES`, `reports/priority-7-stable-id-specification.md`)

| Namespace | Format | Current count in runtime | Allocator function |
|---|---|---|---|
| Lemma | `vp-l-<lemma-slug>-<digest12>` | 30 | `allocate_lemma_id(canonical_lemma)` |
| Meaning | `vp-m-<lemma-slug>-<meaning-key>-<digest12>` | 34 | `allocate_meaning_id(lemma_id, canonical_lemma, meaning_key)` |
| Pattern | `vp-p-<lemma-slug>-<meaning-key>-<pattern-key>-<digest12>` | 45 | `allocate_pattern_id(meaning_id, canonical_lemma, meaning_key, pattern_key)` |
| Example | `vp-e-<pattern-readable-stem>-<example-key>-<digest12>` | 45 | `allocate_example_id(pattern_id, example_key)` |
| Exercise (future, unused) | `vp-x-<pattern-readable-stem>-<activity-type>-<item-key>-<digest12>` | 0 | `allocate_exercise_id(pattern_id, activity_type, item_key)` |

`vp` is a fixed namespace prefix; the second segment (`l`/`m`/`p`/`e`/`x`) is a fixed family letter. All IDs match `[a-z0-9-]+`.

## 2. Allocation method: deterministic content hash, not a counter

Every ID is `<readable-prefix>-<digest12>` where `digest12` is the first 12 lowercase hex characters of `SHA-256(seed)`, and the seed is built entirely from already-known identifiers/text, never from a counter, timestamp, or array position:

```
v1|lemma|<normalized-canonical-lemma>
v1|meaning|<lemma-id>|<meaning-key>
v1|pattern|<meaning-id>|<pattern-key>
v1|example|<pattern-id>|<example-key>
v1|exercise|<pattern-id>|<activity-type>|<item-key>
```

- **Allocation is automatic, not manual**: given the same normalized lemma text and the same author-chosen `key` values, the same ID is always produced. There is no incrementing sequence and therefore no "next available ID" or "highest ID" concept anywhere in this namespace.
- **Semantics are partially encoded**: the human-readable prefix (slug + keys) is derived from the lemma text and the immutable authoring `key`s, purely for debugging/readability. The trailing 12-hex digest is what actually guarantees uniqueness; the spec is explicit that the digest, not the readable stem, provides collision resistance (`reports/priority-7-stable-id-specification.md` §2).
- **Ordering assumptions**: none. `reports/priority-7-stable-id-specification.md` §5 states array reordering has no effect and IDs must never be renumbered to close gaps.
- **Where allocation happens**: entirely inside `priority7_tooling.py` (`allocate_lemma_id`, `allocate_meaning_id`, `allocate_pattern_id`, `allocate_example_id`, `allocate_exercise_id`, lines 396–448). Nothing in `content/verb-patterns.json` itself, nor in `pp-verb-patterns.js`, allocates IDs — the runtime consumer only validates ID *shape* (`ID_RES`-equivalent regexes reimplemented in JS), it never generates one.
- **Uniqueness validation**: mechanically checked. This audit independently re-verified 30/30 lemma IDs, 34/34 meaning IDs, 45/45 pattern IDs, and 45/45 example IDs are unique in the current runtime file (zero duplicates found). The validator additionally checks global cross-namespace uniqueness and sibling-key uniqueness (`_validate_hierarchy`, `_closed_object`/`_key` calls throughout `priority7_tooling.py`).

`meaning.key` / `pattern.key` / `example.key` (and future `activityType`/`itemKey`) are immutable, author-chosen, lowercase-kebab-case identifiers of durable semantic identity (`seek`, `genitive-target`, etc.) — never derived from mutable display text. A changed English gloss never changes a `key`, hence never changes an ID. A changed case/preposition/relationType/complement count/meaning boundary requires a **new** key and ID; the old one is retired, never edited in place (`reports/priority-7-stable-id-specification.md` §3–4).

## 3. Tombstones / non-recycling

### What the architecture supports (OBSERVED FROM SCRIPT/VALIDATOR)

`priority7_tooling.py` has a fully-specified tombstone schema and validator (`_validate_tombstone`, lines 4450–4507) that is invoked as part of `freeze_editorial`/the frozen-document validation path. A tombstone record requires exactly `{id, kind, formerParentId, retirementRevision, reason, replacementIds}` and is mechanically checked for:

- `retirementRevision` must equal the transition's target revision;
- `replacementIds` must be unique, non-self-referential, must resolve to a *currently active* entity of the *same kind*, and that entity must itself have an allocation record;
- the tombstoned `id` must have existed in the *previous* frozen identity snapshot, with matching `kind` and `formerParentId` — you cannot tombstone something that was never really there, or that had a different parent.

`reports/priority-7-stable-id-specification.md` §5 states the governing policy explicitly: **IDs are never deleted from the frozen registry and never reused**, retired entities remain in a tombstone registry with kind/former-parent/retirement-revision/reason/replacements, and array reordering/renumbering never happens.

### What currently exists (OBSERVED FROM PRIVATE GOVERNANCE)

`editorial/verb-pattern-candidates.json` currently has **no `tombstones` key at all** — not even an empty array. No lemma, meaning, pattern, or example has ever been retired in the released corpus; there is nothing to tombstone yet. This is expected: the corpus has only ever grown (revision 1 → revision 2 changed only audio eligibility, no entity was added, removed, or replaced).

### Classification

**MECHANICALLY ENFORCED**, with the caveat that enforcement has never yet been exercised against a real retirement, because none has happened. The validator code exists, is wired into the frozen-document validation path, and rejects malformed/dangling/self-referential/resurrected tombstones by construction — but this audit found zero tombstone records in the repository to observe the check firing against real data. Confidence is high because the same `freeze_editorial`/`verified_runtime_from_frozen` pipeline that produced the current byte-identical runtime file was independently re-run and re-verified by `priority8_phase1_transition.py`'s own internal check (`serialized(projected_previous) == baseline_runtime_bytes`), which exercises the "previous frozen state must reproduce exactly" guarantee this tombstone mechanism depends on.

## 4. Collision audit (OBSERVED FROM RUNTIME, computed directly)

- Lemma IDs: 30 unique / 30 total — no duplicates.
- Meaning IDs: 34 unique / 34 total — no duplicates.
- Pattern IDs: 45 unique / 45 total — no duplicates.
- Example IDs: 45 unique / 45 total — no duplicates.
- No malformed IDs found (all match their respective `vp-{l,m,p,e}-...-<12 hex>` shape by construction, since the runtime validator (`validate_runtime`) rejects the file otherwise, and this audit ran that validator successfully against the committed file).
- No `vp-x-` (exercise) IDs exist yet — the namespace is defined but unused.
- Because the ID space is a 48-bit hash digest per entity rather than a sequential range, there is **no numeric "highest ID"** and no notion of a "gap" to reuse — gaps/ranges are not a meaningful concept in this architecture the way they would be for sequential integer IDs.
- Cross-namespace collision is structurally prevented by the fixed family-letter prefix (`l`/`m`/`p`/`e`/`x`) — an `l`-prefixed and a `p`-prefixed ID cannot collide even if their digests matched, because the strings differ by prefix.
- Future automated collision detection **can** be implemented on the existing architecture without change: `priority7_tooling.py` already builds a `RepositoryIndex`/`RepositoryEntity` structure that maps every allocated ID to an entity and flags collisions (`index.issues`); the same machinery that would allocate the frozen-68's IDs already validates a full-corpus ID index as a side effect of `freeze_editorial`. Twelve hex digits give 48 digest bits; the spec (`reports/priority-7-stable-id-specification.md` §2) explicitly states that if an actual collision were ever observed pre-release, the fix is a global format-version revision, not an ad hoc per-ID suffix.

## 5. Aspect-partner architecture (see also the current-model-audit report §2)

- `aspectPartnerIds` is a lemma-level array field, currently **present in zero released lemmas** (0 of 30). It is validated when present (`_string_list(... unique=True)`, `UNRESOLVED_ASPECT_LINK` check) and is checked for **reciprocity**: `priority7_tooling.py` (lines ~2287–2342, ~2829–2870) resolves each partner ID against the entity index and checks the relationship points back.
- `aspectEquivalentPatternIds` is a separate, pattern-level (not lemma-level) optional field for linking specific patterns across aspect partners — also present in zero released patterns.
- The runtime consumer (`pp-verb-patterns.js`, `validLemmaShell`) already accepts optional `aspectPartnerIds` on any lemma without requiring the partner lemma to exist in the same file as a full record — the JS shape check only verifies `aspectPartnerIds` is an array of non-empty strings, it does not require each string to resolve to another lemma present in the same runtime document.
- `reports/priority-7-pattern-data-specification.md` line 48 states the authoritative rule: "Omit when no reviewed link exists. Links are reciprocal, non-self, human-confirmed, and never imply pattern inheritance. `unresolved` lemmas cannot publish partner links."

This directly matters for the two frozen Phase 3B metadata-only identities, `zaczynać → zacząć` and `przeczytać → czytać`: see `priority-8-phase-4a1-phase3b-compatibility.md` §10–11 for the classification of whether the current architecture supports that relationship as-is.

## 6. What Phase 4A-2 must decide before the 68 can receive IDs

This audit does not make these decisions; it only surfaces that they are unmade:

- **PHASE 4A-2 DECISION NEEDED** — whether `key` values (meaning/pattern/example) for the 68 frozen lemmas will be authored fresh per lemma, or whether any naming convention is expected to carry information from the Phase 3/3B verification records (e.g. matching `narrowing_summary` wording). The current allocator is agnostic to this; it only requires the key to be lowercase kebab-case and unique among siblings.
- **PHASE 4A-2 DECISION NEEDED** — whether the two metadata-only identities (`zaczynać`, `przeczytać`) will ever receive their own lemma ID (with `aspectPartnerIds` pointing at `zacząć`/`czytać`) as a metadata-only, meaning-less lemma record, or whether "metadata-only" means no lemma record is created for them at all in `editorial/verb-pattern-candidates.json`. Section 5 above shows the architecture can technically represent a lemma with `aspectPartnerIds` and no full pattern content is a separate question from whether such a stub lemma record should exist; the spec text does not resolve this by itself.
- **PHASE 4A-2 DECISION NEEDED** — how the `clauseKind` gap for `direct-speech` (current-model-audit §2) is resolved before any of the frozen 68 whose Phase 3 evidence includes direct speech (`czytać`, `przeczytać`, `pisać`, `napisać`, `powiedzieć`, `zgadzać się`, `polecać`, `radzić`, `odpowiadać`) can have that alternative authored as a `clause` complement. This is a schema question (add an enum value) as much as an editorial one.
- **PHASE 4A-2 DECISION NEEDED** — whether `formatVersion` needs to bump for the expansion (it has never moved from 1) or whether `patternDataRevision` alone (moving to 3, per `reports/priority-8-runtime-revision-options.md`'s own recommendation) is sufficient, given the expansion adds ~68 new lemmas rather than changing the data contract itself.
