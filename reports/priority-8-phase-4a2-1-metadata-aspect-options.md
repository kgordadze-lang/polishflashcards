# Priority 8 Phase 4A2-1 — Decision A: Metadata-Only Aspect Partners

**Status:** OPTIONS AND RECOMMENDATION ONLY. No schema, runtime, or editorial-corpus change is made by this report. HUMAN DECISION REQUIRED before Phase 4B.

## 1. Current architecture

A lemma is a required-shape object (`id`, `canonicalLemma`, `reflexive`, `aspect`, `meanings`) in both the private editorial schema and the public runtime schema (`priority7_tooling.py`, current-model-audit §2). The only field that can express a cross-lemma relationship is the optional lemma-level array `aspectPartnerIds` (0 of 30 released lemmas use it today).

`aspectPartnerIds` is not a free-form label — it is a **resolved reference**, validated by `_validate_hierarchy` (editorial, `priority7_tooling.py` lines ~2281–2310) and again by `validate_runtime` (lines ~2836–2847):

- a target ID that resolves to no lemma record in the same document → `ASPECT_LINK_DANGLING`;
- the target's own `aspectPartnerIds` must list the source back → `ASPECT_LINK_NONRECIPROCAL`;
- **both** linked lemmas must already own at least one pattern in a `REVIEWED_STATES` state → `ASPECT_LINK_UNREVIEWED`.

Independently, every lemma — editorial and runtime — must have a non-empty `meanings` array (`MEANINGS_REQUIRED` / `RUNTIME_MEANINGS_REQUIRED`); `meanings: []` is rejected outright.

## 2. Why the current contract is insufficient

The Phase 3B freeze requires exactly this shape for two identities:

- `zaczynać` → anchor `zacząć` (metadata-only, verified, not rejected)
- `przeczytać` → anchor `czytać` (metadata-only, verified, not rejected)

Both must **not** receive a separate Phase 4 full-pattern record, and metadata must **never transfer syntax** (`priority-8-phase-3b-phase4-handoff.md` §"Metadata-only aspect partners", global constraints 6–7).

But `aspectPartnerIds` mechanically requires the target to be a real lemma record with ≥1 already-reviewed pattern (`ASPECT_LINK_UNREVIEWED`) and a non-empty `meanings` array (`MEANINGS_REQUIRED`). A zero-content stub for `zaczynać`/`przeczytać` **cannot validate** as either side of a reciprocal `aspectPartnerIds` link. Giving it real pattern content to pass validation would directly contradict "no separate Phase 4 full-pattern record." There is no current field that means "this lemma text is a verified aspect partner, but intentionally carries no pattern content."

The only presently-valid workaround — leaving `aspectPartnerIds` unpopulated on both sides and recording the relationship solely in governance prose — is schema-legal but encodes the relationship **nowhere** in the architecture, exactly as all of the released 30's own (undeclared) aspect pairs already do.

## 3. Options

### Option A1 — Governance-only, no runtime encoding at all
Keep the relationship recorded only in reports/private governance documents (this report, the Phase 3B freeze, and a private note in `editorial/priority-7-authoring-context.json` if desired). No schema field is added anywhere.

- Private vs public: private only (or not encoded in tooling-readable form at all).
- Learner UI: cannot show the partner. No mechanism exists to surface it.
- IDs needed: none.
- Reciprocal relationship: not representable (nothing to be reciprocal *to*).
- Validator/projector/JS loader/UI impact: **zero**.
- Stable-ID implications: none.
- Migration implications: none.
- `formatVersion`/`patternDataRevision`: no impact.
- Compatibility with existing 30: trivially compatible (no change).
- Risk of syntax transfer: none (nothing links anything).
- Complexity: minimal — but the relationship becomes invisible to any tooling, future audits, or the learner-facing product, and is not "truthfully preserved" by the *architecture* — only by prose the architecture cannot check.

### Option A2 — Metadata-only textual partner identity on the anchor lemma (RECOMMENDED)
Add two new **optional, string-valued, non-resolved** fields to the lemma object — present only on the two anchor lemmas (`zacząć`, `czytać`), both of which are already full-pattern lemmas among the frozen 68:

- a lemma-text field naming the metadata-only partner (conceptually `aspectPartnerLemma`), and
- a short fixed-vocabulary label making the relationship's nature explicit (conceptually `aspectPartnerLabel`, e.g. a value drawn from a closed 1–2 value enum such as `metadata-only`), so nothing downstream can mistake it for a resolved-ID relationship.

Do not assume `aspectPartnerLemma`/`aspectPartnerLabel` are the correct final field names — that naming is a Phase 4A2-2 human decision; the point is the field carries **plain lemma text**, not an ID, and is never resolved, dereferenced, or reciprocity-checked.

- Private vs public: available in **both** — this is exactly the kind of fact (a verified, human-approved linguistic relationship) the Phase 3 evidence record already establishes, and there is no private-only reason to hide it from learners.
- Learner UI: **yes** — a short subtitle under the anchor's headline (e.g. "Aspectual partner: zaczynać (imperfective) — metadata only, not a separate pattern") is a direct, low-risk rendering addition (`pp-verb-patterns.js` `headlineFor`/card-rendering already composes per-lemma display strings from structured data).
- IDs needed: **none**. This is the central advantage — the field is prose-shaped text, never an ID, so `ASPECT_LINK_DANGLING`/`ASPECT_LINK_NONRECIPROCAL`/`ASPECT_LINK_UNREVIEWED` simply never apply to it.
- Reciprocal relationship: **not representable, by design** — this is asymmetric (only the anchor carries it), because there is no lemma record for the metadata-only partner to reciprocate from. This is an accurate reflection of the Phase 3B freeze, not a gap: the freeze forbids the partner from having its own record at all.
- Validator impact: small — add the two optional keys to the lemma's closed-key allowlist in both `validate_editorial` and `validate_runtime`; type-check as non-empty strings; if a label enum is used, validate membership. No cross-reference/graph logic needed.
- Projector impact: trivial passthrough (public field, no stripping).
- JS loader impact: add the two keys to the lemma shape check (`validLemmaShell`, alongside `displayLemma`/`aspectPartnerIds` at line ~434) and a small render addition. Mirrors the existing pattern used for `displayLemma`/`aspectPartnerIds` almost exactly.
- Stable-ID implications: none — no ID is allocated for `zaczynać`/`przeczytać`, ever, under this option.
- Migration implications: none for the existing 30 (the fields are optional and appear on exactly 2 of the ~98 eventual lemma records).
- `formatVersion`: this widens what a "closed" lemma object may legally contain — a schema-shape change (see the format-version discussion in the decision summary). Recommend increment.
- `patternDataRevision`: increments together with the batch that ships these two anchors' full content (already planned to move to revision 3 for the expansion).
- Compatibility with existing 30: fully additive/optional; zero impact.
- Risk of accidentally transferring syntax: effectively zero — the field carries display text only; there is no code path by which a pattern, complement, or example could be copied or inherited through it.
- Complexity: low — two optional string fields, no graph validation, no new entity kind, no new ID namespace.

### Option A3 — Separate metadata-only entity registry outside full-pattern lemmas
Create a new, small registry (e.g. `aspectMetadataPartners: [{ anchorLemmaId, partnerLemma, note }]`) either at the top level of the runtime/editorial document or as a wholly separate file.

- Private vs public: could be either; a top-level array is simplest to keep public.
- Learner UI: possible, but requires new lookup code (join the registry against the anchor's `id` at render time) rather than reading a field already on the lemma object.
- IDs needed: arguably yes, if the registry entries are meant to be independently addressable (e.g. for future tooling) — otherwise no.
- Reciprocal relationship: same asymmetry as A2, just modeled as a one-sided registry row instead of a one-sided lemma field.
- Validator/projector/JS loader/UI impact: **larger** than A2 — a new top-level document key changes `ENVELOPE_KEYS` (`pp-verb-patterns.js` line 59) itself, which is a more invasive shape change than adding an optional key to an existing object, and requires new validator code paths on both sides rather than reusing the existing per-lemma shape check.
- Stable-ID/migration/formatVersion/patternDataRevision: same direction as A2 but with a larger blast radius for no additional expressive power (A3 encodes exactly the same fact A2 does, at a higher structural cost).
- Compatibility with existing 30: additive, but touches the document's outermost shape, which is more conservative to avoid touching without need.
- Complexity: higher than A2 for equivalent expressiveness. **Not recommended** — A2 achieves the same result as a smaller, localized change.

### Option A4 — Generalize `aspectPartnerIds` to resolve to either a full-pattern lemma or a metadata-only lemma identity
Keep `aspectPartnerIds` as an ID-resolving field, but introduce an explicit "entity kind" so a target may resolve to a new, deliberately exempt "metadata-only lemma identity" kind that:
- is allowed to have `meanings: []` (an explicit carve-out from `MEANINGS_REQUIRED`), and
- is exempt from `ASPECT_LINK_UNREVIEWED`'s "must already own a reviewed pattern" requirement.

- Private vs public: could support both, and — unlike A2 — this *would* let `zaczynać`/`przeczytać` have their own addressable lemma record (answering the "is it independently discoverable in the UI" question A2 leaves open).
- Learner UI: yes, and potentially richer (a dedicated, if minimal, lemma entry).
- IDs needed: **yes** — this is the one option that would actually allocate a `vp-l-` lemma ID for `zaczynać`/`przeczytać`. That is a materially different product/architecture decision than "metadata only," and risks blurring exactly the line the Phase 3B freeze is protecting (a metadata-only identity starting to look, structurally, like a 69th/70th full lemma in every way except pattern count).
- Reciprocal relationship: **yes**, properly two-sided, since both sides would now be real lemma records.
- Validator impact: **large** — every one of `MEANINGS_REQUIRED`, `RUNTIME_MEANINGS_REQUIRED`, `ASPECT_LINK_UNREVIEWED`, and the reciprocity checks needs an explicit lemma-kind branch; a new closed enum for lemma "kind" (`full-pattern` vs `metadata-only`) must be introduced and threaded through both the editorial and runtime validators.
- Projector/JS loader/UI impact: moderate-to-large — the loader must learn a new lemma kind and decide what to render for a lemma with zero patterns (today's UI has no code path for that at all).
- Stable-ID implications: **allocates 2 new lemma IDs that do not correspond to full-pattern content** — a new category of ID the current stable-ID specification does not anticipate (`priority-7-stable-id-specification.md` describes lemma IDs as always owning ≥1 meaning).
- `formatVersion`: unambiguously a schema-shape change; increment required.
- Compatibility with existing 30: additive but conceptually changes what a "lemma" can mean in this system.
- Risk of accidentally transferring syntax: **higher** than A2 — once `zaczynać` is a real lemma record with its own ID, every future contentRef/tooling pass that walks "all lemmas" must remember to special-case it, which is exactly the kind of surface where an accidental partial-pattern edit could creep in over time.
- Complexity: **highest of the viable options**, for a capability (independent discoverability of the metadata-only identity) the Phase 3B freeze does not actually require.

### Option A5 — No materially better minimal design found
No smaller mechanism than A2 was found that both (a) satisfies "no separate Phase 4 full-pattern record" and (b) encodes the relationship *somewhere* the architecture can read, rather than only in prose.

## 4. Recommendation

**Recommend Option A2** (metadata-only textual partner identity, unresolved, on the anchor lemma only).

Reasoning against the recommendation standard (§13 of the task brief):
- **Truthfulness**: A2 states exactly what the Phase 3B freeze says — a verified relationship to lemma text, not a resolved entity — and cannot silently imply more (no ID, no reciprocity, no pattern linkage exists to be mistaken for inheritance).
- **Smallest maintainable architecture**: two optional string fields on an existing object, versus a new registry (A3) or a new lemma-kind + validator branch family (A4).
- **No syntax inheritance**: A2 has no code path capable of copying pattern content between the anchor and its partner, because the partner never becomes a resolvable entity.
- **Backwards compatibility / stable-ID safety**: zero ID or migration impact; A1 is equally safe but forfeits any machine-readable trace of the relationship, which risks the *next* audit (or a future author) rediscovering the same ambiguity Phase 4A-1 just resolved.

A1 remains an acceptable fallback if the human reviewer decides even a plain-text, unresolved field is more schema surface than the product wants for two identities — it is strictly safer, only less useful.

## 5. Open product question this report does not resolve

A2 makes `zaczynać`/`przeczytać` mentionable from their anchor's card, but **not independently searchable or landable** in the learner UI (there is no lemma record to land on). If the product wants the metadata-only identity to be independently discoverable, that requires something closer to A4 and a materially larger, riskier change. This is itself a sub-question of Decision A and must be resolved by the human alongside the primary recommendation.

## HUMAN DECISION REQUIRED

1. Approve Option A2 (or A1) as the Phase 4B architecture for metadata-only aspect partners.
2. Decide the exact field name(s) and whether a closed label enum (e.g. `metadata-only`) is required or a free string suffices.
3. Decide whether independent learner-UI discoverability of `zaczynać`/`przeczytać` is required (if yes, this decision must be reopened toward something like A4).
4. Confirm `formatVersion` increments for this schema-shape addition (see decision summary §formatVersion).
