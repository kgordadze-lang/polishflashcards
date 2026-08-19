# Priority 7 — Stable ID Specification

**Phase:** 1 specification only  
**Status:** locked allocation and retirement policy; no production IDs allocated

## 1. ID families

All IDs are globally unique within the Priority 7 corpus and match the existing repository-safe character set `[a-z0-9-]+`.

| Entity | Format |
|---|---|
| Lemma | `vp-l-<lemma-slug>-<digest12>` |
| Meaning | `vp-m-<lemma-slug>-<meaning-key>-<digest12>` |
| Pattern | `vp-p-<lemma-slug>-<meaning-key>-<pattern-key>-<digest12>` |
| Example | `vp-e-<pattern-readable-stem>-<example-key>-<digest12>` |
| Future activity item | `vp-x-<pattern-readable-stem>-<activity-type>-<item-key>-<digest12>` |

`vp` is the Priority 7 verb-pattern namespace. Family letters are fixed. IDs never depend on array position, CEFR, topic placement, activity eligibility, display gloss, example text, or learner explanation.

## 2. Normalization and digest algorithm

Tooling allocates an ID exactly once.

1. Normalize input text to Unicode NFC.
2. For the canonical lemma, remove leading/trailing whitespace, collapse each internal whitespace run to one ASCII space, and apply Unicode lowercase. This full result is the normalized canonical lemma.
3. To make `lemma-slug`, transliterate Polish `ą ć ę ł ń ó ś ź ż` to `a c e l n o s z z` in the normalized canonical lemma.
4. Replace each run of characters outside ASCII `[a-z0-9]` with one hyphen, collapse any repeated hyphens, and trim leading/trailing hyphens.
5. If the result is longer than 32 ASCII characters, take exactly its first 32 characters, then remove any trailing hyphen created by that truncation. The final slug MUST be non-empty. There is no discretionary word-boundary handling.
6. `key` fields are already lowercase ASCII kebab-case and are not derived from learner wording.
7. The seed is UTF-8 encoded without a trailing newline, hashed with SHA-256, and the first 12 lowercase hexadecimal characters are used.

The lemma seed always contains the full normalized canonical lemma, never the possibly truncated `lemma-slug`. Slug truncation affects readability only, not digest collision resistance.

Seed strings are:

```text
v1|lemma|<normalized-canonical-lemma>
v1|meaning|<lemma-id>|<meaning-key>
v1|pattern|<meaning-id>|<pattern-key>
v1|example|<pattern-id>|<example-key>
v1|exercise|<pattern-id>|<activity-type>|<item-key>
```

### Pattern-readable stem

`pattern-readable-stem` is exactly the readable portion of the already allocated owning pattern ID. Given `vp-p-<readable-stem>-<digest12>`, derive it only by:

1. requiring the owning pattern ID to be valid;
2. removing the exact `vp-p-` prefix;
3. removing the final hyphen and 12 lowercase hexadecimal digest characters;
4. using the non-empty remaining string unchanged.

At initial pattern allocation this remaining string is equivalent to `<lemma-slug>-<meaning-key>-<pattern-key>`. Example and exercise allocation MUST derive it from the stable owning pattern ID, not reconstruct it independently from current lemma text or keys.

Worked example:

```text
owning pattern:        vp-p-fikcjonowac-test-content-direct-target-fe6705e214bf
pattern-readable-stem: fikcjonowac-test-content-direct-target
example:               vp-e-fikcjonowac-test-content-direct-target-first-context-718f9ecca50f
exercise item 1:       vp-x-fikcjonowac-test-content-direct-target-grammar-choose-first-context-ccadf037a929
exercise item 2:       vp-x-fikcjonowac-test-content-direct-target-grammar-choose-second-context-60e1fb776c5f
```

The two exercise IDs share the owning pattern and `grammar-choose` activity type but use different immutable `itemKey` values and therefore different deterministic seeds and digests.

The readable portion supports debugging; the digest provides deterministic collision resistance. Every new entity MUST reproduce exactly from this allocation algorithm, and the validator MUST reject any global collision. Twelve hex characters provide 48 digest bits; if an actual collision occurs before release, the format specification must be revised globally rather than adding an ad hoc suffix.

## 3. Key rules

- `meaning.key`, `pattern.key`, `example.key`, future `activityType`, and future exercise `itemKey` match `[a-z0-9]+(?:-[a-z0-9]+)*`.
- Keys describe durable semantic/structural identity, not mutable display copy: `seek`, `payment-method`, `genitive-target` are suitable conceptual examples.
- Keys are unique among siblings and frozen after ID allocation.
- A changed English gloss does not change `meaning.key`.
- A changed case, preposition, relation type, complement count, or meaning boundary normally requires a new pattern or meaning key and ID; the old ID is retired.

`activityType` identifies the consumer family (for example `grammar-choose`, `grammar-build`, or `type-it`). `itemKey` is an immutable authored semantic discriminator within one pattern and activity type, such as `person-form-context` or `payment-method-card`. Multiple items of the same activity type therefore receive different identities without array positions or numeric sequences. `(patternId, activityType, itemKey)` must be unique.

## 4. Post-release corrections

Released IDs are identifiers, not live hashes. If an ordinary spelling correction preserves the same lexical form, the existing ID remains stable even though recomputing from corrected text would yield a different candidate. The frozen registry records that the ID was validly allocated from its original seed. This exception requires an explicit correction record and owner approval. Adding or removing lexical `się` is never such a spelling correction: it changes lemma identity and requires a new lemma ID after release.

Released/frozen IDs are validated against their frozen allocation records, not treated as live hashes of mutable display or canonical wording. A permitted same-identity post-release correction does not cause descendants to reconstruct a new readable stem: every new example or exercise derives `pattern-readable-stem` from its stable owning pattern ID.

Before a candidate has entered the first approved frozen production baseline, an identity error—including `relationType`—may be corrected by replacing the unshipped candidate and recomputing its key/ID. After release, `relationType` is structural identity: every change creates a replacement pattern and tombstones the old ID.

Use this matrix:

| Change | Keep ID? |
|---|---|
| Learner explanation, gloss wording, example wording, usage note | yes; frozen wording/policy approval still required |
| CEFR, eligibility, teaching status, review state | yes; policy approval required |
| Corrected typo that preserves lexical/semantic identity | yes, through correction workflow |
| New meaning boundary, repurposed meaning, different participant structure | no; create and retire |
| Case/preposition/complement/relation change that changes the construction | no; create and retire |
| Moving an entity under another parent | no; identity includes ownership |

## 5. Retirement and non-reuse

IDs are never deleted from the frozen ID registry and never reused, even if no persistent learner progress exists. A retired entity remains in the tombstone registry with entity kind, former parent, retirement revision, reason, and replacement ID(s) if any. Replacements are informational and do not imply progress migration.

Array reordering has no effect. IDs MUST NOT be renumbered to close gaps. No ID aliases are created merely for display/search wording.

## 6. Aspect, reflexivity, and links

`się` is part of the lemma normalization and readable slug, so reflexive and non-reflexive forms receive different deterministic identities. The stored `reflexive` Boolean is intentionally redundant for readability and fail-closed mechanical validation; it must equal the `canonicalLemma` form and never defines a second notion of reflexivity. Correcting only a mistaken Boolean while the lemma text was already right keeps the ID and repeats covered review. Correcting the lemma by adding/removing lexical `się` replaces the released identity. Aspect partners likewise receive separate lemma, meaning, and pattern IDs. Reciprocal links point to IDs; shared roots or similar English glosses never create identity equivalence.

## 7. Examples (fictional form only)

These demonstrate format and are not allocated production IDs; digest placeholders are intentionally invalid:

```text
vp-l-fikcjonowac-000000000000
vp-m-fikcjonowac-test-sense-000000000000
vp-p-fikcjonowac-test-sense-clause-content-000000000000
vp-e-fikcjonowac-test-clause-content-first-000000000000
vp-x-fikcjonowac-test-clause-content-grammar-choose-first-context-000000000000
```

The example JSON uses correctly shaped `vp-…` IDs so allocation mechanics can be checked, but its top-level `artifactStatus`, fictional lemmas, deferred status, and empty eligibility make it explicitly nonproduction.

## 8. Validation ownership

A future dedicated validator checks exact algorithmic recomputation for newly proposed entities; released entities instead check against their frozen allocation records. It also checks syntax, family/kind agreement, sibling keys, global uniqueness, parent ownership, reference resolution, reciprocal aspect links, tombstones, and frozen registry drift. Existing `validate_content.py` does not gain this responsibility in Phase 1.

## 9. Decision log

| Decision | Alternatives considered | Why selected | Reversible? |
|---|---|---|---|
| Namespaced family prefixes | one flat `vp-…`; existing card IDs | visible kind and no collision with PP_LEVELS | only before first released record |
| Readable slug + 12-hex SHA-256 prefix | array numbers; slug only; random UUID | deterministic, readable, resistant to transliteration collisions | only by format-version change |
| Immutable authored keys | derive from gloss/display | wording edits cannot rename entities | key errors require retire/recreate |
| Tombstones and no reuse | delete retired IDs | frozen links remain interpretable | locked after first release |
| Example/exercise IDs | anonymous nested strings; activity type alone | supports multiple stable items per activity type plus frozen wording, feedback, and future references | exercise object fields beyond `activityType`/`itemKey` remain for the activity-authoring phase |
