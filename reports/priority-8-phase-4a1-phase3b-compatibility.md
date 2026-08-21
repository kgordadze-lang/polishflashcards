# Priority 8 Phase 4A-1 — Phase 3B Compatibility Assessment

**Scope:** whether the *current* architecture (as audited in the other four reports) can eventually support the frozen Phase 3B requirements. No authoring is done here. Classifications: `SUPPORTED AS-IS`, `SUPPORTED WITH EDITORIAL DISCIPLINE`, `REQUIRES FUTURE MODEL/SCHEMA CHANGE`, `UNKNOWN`.

## 0. Mechanical reconfirmation of Phase 3B inputs

Reproduced directly from `reports/priority-8-phase-3b-final-lemma-freeze.csv` (70 rows) rather than trusted from narrative text:

- 70 researched rows. ✓
- 68 rows with `full_pattern_in_phase4 = yes`. ✓
- 2 rows with `full_pattern_in_phase4 = no`, exactly `zaczynać → zacząć` and `przeczytać → czytać`. ✓
- 16 rows with `phase3_disposition = KEEP WITH NARROWING`. ✓
- 21 rows with `phase3_representation_fit = compatible with narrowing` (the same 16 plus 5 additional `KEEP VERIFIED` rows: `iść`, `chodzić`, `jechać`, `jeździć`, `dojechać`). ✓
- The 68-item list programmatically extracted from the CSV (in verification order) is **identical** to the frozen list given in the Phase 4A-1 task brief, order 1–16 then 18–70 (orders 17 and 37 correctly absent as the two metadata-only identities). ✓
- Cross-check against `reports/priority-8-phase-3-final-synthesis.csv`: 70 rows, 54 `KEEP VERIFIED` + 16 `KEEP WITH NARROWING` = 70, zero rows in any other disposition, `evidence_strength = A` for all 70 rows. ✓

No reserve lemma is present in either CSV (`reserve_backfill = no` / `reserve_gate_needed = no` for every row).

## Per-capability classification

**1. 68 new full-pattern lemma identities** — `SUPPORTED AS-IS`. The lemma/meaning/pattern/example hierarchy and the deterministic ID allocator have no ceiling tied to the current 30; nothing in the schema, validator, or projector encodes "30" as a limit. Scaling to ~98 lemmas is a volume change, not a structural one.

**2. Multiple meanings per lemma** — `SUPPORTED AS-IS`. Already exercised today: 30 lemmas produce 34 meanings, i.e. some lemmas already carry more than one meaning (e.g. `bać się` has at least two, observed directly in `content/verb-patterns.json`).

**3. Multiple patterns per meaning** — `SUPPORTED AS-IS`. The schema places `patterns[]` under each meaning with no cardinality cap; the array shape is validated but not length-limited.

**4. Alternative schemas** (§6 rule 5 of the task brief — alternatives must remain alternative, not merged into one maximal frame) — `SUPPORTED WITH EDITORIAL DISCIPLINE`. The schema has no mechanism that *detects* an over-combined maximal pattern versus two correctly separate alternative patterns — that judgment is entirely editorial (this is exactly why the Phase 3B authoring constraints for `pozwalać`, `umówić się`, `zamawiać`, etc. read as prose instructions rather than schema constraints). The architecture supports the *correct* representation (multiple sibling patterns under one meaning) equally well as the *incorrect* one (one maximal pattern); nothing mechanically prevents the latter.

**5. Optional complements** — `SUPPORTED AS-IS`. `complements[].required` is a validated Boolean on every complement; optionality is a first-class, already-used field (observed in the runtime file, e.g. `bać się` patterns).

**6. Generalized-role realization labels** (DOKĄD/SKĄD/GDZIE as selected semantic roles, not new complement types) — `SUPPORTED WITH EDITORIAL DISCIPLINE`. `ROLES` already includes `target`/`topic`/`content`/etc. but has **no generalized-direction role values** (no `dokąd`/`skąd`/`gdzie`-equivalent). The task brief's own rule (§6.2) is explicit that these are "selected semantic roles but NOT new complement types" — meaning the intended representation is: author each concrete realization (`do + Genitive`, `na + Accusative`, …) as its own `preposition-case` complement, and keep the *generalized-role* framing only in `learnerExplanationEn`/prose, never as a schema value. The current `ROLES` enum is compatible with this discipline (it doesn't need a `dokąd` role — the existing roles like `target` already cover the concrete realizations), so no schema change is required, but nothing mechanically stops an author from inventing a pseudo-generalized-role label inside a free-text field like `learnerExplanationEn` or a `usage.note`. Enforcement is editorial, not structural.

**7. Lexical `się`/`sobie` identities** — `SUPPORTED AS-IS`. `się`/`sobie` are part of `canonicalLemma` normalization itself (`normalize_canonical_lemma`, `lemma_slug`), so `radzić sobie`, `kłócić się`, `spotkać się`, `umówić się`, `cieszyć się`, `martwić się`, `zgadzać się` — all present among the frozen 68 — already produce distinct deterministic lemma IDs from their non-reflexive counterparts, exactly as today's released `bać się` does. `reflexive` is separately, mechanically checked to match the lemma text (§6 of the stable-ID spec).

**8. Fixed lexical `udział`** (`brać udział w + Locative`, `wziąć udział w + Locative`) — `SUPPORTED WITH EDITORIAL DISCIPLINE`. There is no schema field for "required lexical material embedded inside a complement" beyond the complement's own `type`/`case`/`preposition`/`role`. `udział` is a noun, not a case/preposition — the current model has no first-class way to pin a required lexical noun as part of a pattern's identity; it would have to live in `learnerExplanationEn` and/or the pattern's readable `key` (e.g. `udział-w-locative`) as an editorial convention, with nothing mechanically checking that the noun `udział` is actually present in every example sentence for that pattern. This is a real (if narrow) representational gap: the schema can *label* the pattern correctly but cannot *enforce* that examples contain the required lexical item.

**9. Exact clause distinctions** (`że`, `żeby`, interrogative-dependent, direct speech) — **`REQUIRES FUTURE MODEL/SCHEMA CHANGE`**. This is the most significant finding of this audit. `CLAUSE_KINDS = {"ze", "czy", "zeby", "interrogative"}` (`priority7_tooling.py`) — there is **no `direct-speech` value**. This audit searched `priority7_tooling.py`, `pp-verb-patterns.js`, every schema/spec JSON file, and every `reports/*.md` spec document: the string `direct-speech` (or `direct speech` as a schema token) appears **nowhere** in code or schema, only in Phase 3 linguistic-evidence prose. Phase 3 evidence explicitly and repeatedly maps "direct speech" to the `clause` complement type as a real, verified alternative construction for **9 researched identities**, reconfirmed by re-checking each source section: **8 of the frozen 68 full-pattern lemmas** — `odpowiadać` (`reports/priority-8-phase-3-batch-02.md`), `czytać`, `pisać`, `napisać` (`reports/priority-8-phase-3-batch-04.md`, `reports/priority-8-phase-3-batch-04-risk-review.md`), `powiedzieć`, `zgadzać się`, `polecać`, `radzić` (`reports/priority-8-phase-3-batch-06.md`, `reports/priority-8-phase-3-batch-06-risk-review.md`) — **plus 1 metadata-only verified aspect identity**, `przeczytać` (same batch-04 sources; anchored by `czytać` per the Phase 3B freeze, and not itself one of the 68). Phase 4 authoring cannot represent a direct-speech alternative as a `clause` complement for any of the 8 full-pattern lemmas above until either (a) `CLAUSE_KINDS` gains a new enum value and the corresponding validators/runtime consumer are updated to accept it, or (b) a product decision is made to omit direct-speech alternatives from Phase 4 patterns entirely (which would silently under-represent evidence Phase 3 explicitly verified). **PHASE 4A-2 DECISION NEEDED.**

**10. Metadata-only aspect partner `zaczynać → zacząć`** — **`REQUIRES FUTURE MODEL/SCHEMA/CONTRACT CHANGE`** (correcting this audit's original classification of `SUPPORTED WITH EDITORIAL DISCIPLINE` / "leaning `SUPPORTED AS-IS`", which was not justified by the evidence). Direct static reading of `priority7_tooling.py` answers the five diagnostic questions precisely:

- **(A) Absent-partner resolution.** If a full lemma's `aspectPartnerIds` references an ID for which no lemma record exists in the same document, `_validate_hierarchy` raises `ASPECT_LINK_DANGLING` (editorial, lines 2297–2300) and `validate_runtime` raises the runtime-projection equivalent (lines 2839–2842). This is a hard validation failure, not a permitted state.
- **(B) Does Python validation require the target to resolve?** Yes — proven by (A). Confirmed independently in both the editorial validator and the runtime validator, and `freeze_editorial` calls `_validate_hierarchy` a second time on top of `validate_editorial` (lines 4659–4667), so the full official freeze/projection path enforces this at least twice.
- **(C) Does reciprocity require the partner's own record to list the link back?** Yes — `ASPECT_LINK_NONRECIPROCAL` is raised if the target lemma's `aspectPartnerIds` does not contain the source lemma's ID (editorial: lines 2307–2310; runtime: lines 2844–2847). Additionally — a stricter requirement than plain reciprocity — the editorial validator requires **both** linked lemmas to already own at least one pattern with a `reviewState` in `REVIEWED_STATES`, or it raises `ASPECT_LINK_UNREVIEWED` (lines 2281–2306). A lemma that owns zero patterns can never be in the reviewed set, so it can never pass this check as either side of a reciprocal link.
- **(D) Does the schema allow a lemma record with zero meanings/patterns (`meanings: []`)?** No. Both the editorial validator (`MEANINGS_REQUIRED`, lines 2181–2184: `if not isinstance(meanings, list) or not meanings`) and the runtime validator (`RUNTIME_MEANINGS_REQUIRED`, lines 2672–2676, identical logic) reject an empty or missing `meanings` array outright, for every lemma without exception.
- **(E) Is a metadata-only stub consistent with the current stable-ID contract?** No, not as a lemma that participates in a validated reciprocal `aspectPartnerIds` link: (C) and (D) together mean such a lemma would need real, already-reviewed pattern content to exist at all — which is precisely the "separate Phase 4 full-pattern record" the Phase 3B freeze says `zaczynać` must **not** receive. And per (A)/(B), the anchor (`zacząć`) cannot reference `zaczynać` via `aspectPartnerIds` unless `zaczynać`'s lemma record exists and validates.

None of A–E were resolved by appeal to the JS loader's shape check (`pp-verb-patterns.js`), which was deliberately excluded as evidence per the correction's instruction — the JS loader only validates the shape of an already-produced runtime file, not what the editorial/freeze/validation gate will admit.

The only representation that **is** already valid under the current contract is to never populate `aspectPartnerIds` for either `zacząć` or `zaczynać`, and keep "metadata-only aspect partner" as a fact recorded solely in governance reports (as is already true of every aspect pair among the released 30 — 0 of 30 use `aspectPartnerIds` today). That satisfies the schema trivially but does not encode the relationship in the architecture at all. **PHASE 4A-2 DECISION NEEDED**: whether Phase 4 requires the relationship to be schema-encoded (in which case a contract change — e.g. a new lemma-level flag that exempts a declared "metadata-only" lemma from `MEANINGS_REQUIRED`/`ASPECT_LINK_UNREVIEWED` — is needed), or whether governance-report-only documentation, with no schema encoding, satisfies the freeze's intent.

**11. Metadata-only aspect partner `przeczytać → czytać`** — same classification (`REQUIRES FUTURE MODEL/SCHEMA/CONTRACT CHANGE`) and identical reasoning to item 10, substituting `przeczytać`/`czytać` for `zaczynać`/`zacząć`.

**12. Binding authoring/narrowing constraints** (the 21 `compatible with narrowing` rows) — `SUPPORTED WITH EDITORIAL DISCIPLINE`. Every one of the 21 narrowing constraints reviewed (e.g. "author only the production sense with nad + Instrumental," "label do/z forms as goal/source realizations, never as exclusive government") is expressible using only the existing complement/role/relationType vocabulary — none requires a new complement type or field. What the architecture *cannot* do is enforce the "do not encode X" half of each constraint mechanically; it can represent the correct narrower pattern, but nothing stops an author from also encoding the excluded, wider pattern. Compliance is entirely a matter of editorial review at authoring time, same as item 4/6 above.

**13. `activityEligibility` remaining separate/inactive** — `SUPPORTED AS-IS`. The field defaults to (and today universally is) an empty array; nothing in the schema requires it to be populated, and the mechanical gate (`reviewState == "approved"` required for any non-empty eligibility) gives an explicit, already-enforced off switch. Phase 4 authoring can add 68 lemmas' worth of patterns with `activityEligibility: []` throughout with zero schema friction, exactly as the current 45 already do.

**14. `audioEligible` pronunciation permission (separate from activityEligibility)** — `SUPPORTED AS-IS`. Confirmed both by schema (an example-level Boolean wholly independent of the pattern-level `activityEligibility` array) and by the actual audio pipeline (`pp_audio_rule.verb_pattern_audio_examples()` reads only `audioEligible`, never `activityEligibility`; `verify_audio.py` run in this audit reports the 45 current audioEligible examples fully covered with zero coupling to activity state).

**15. Stable-ID expansion (68 new lemma identities' worth of IDs)** — `SUPPORTED AS-IS` for the allocation mechanism itself (deterministic hash allocation has no ceiling and no collision risk beyond the documented 48-bit digest space); `SUPPORTED WITH EDITORIAL DISCIPLINE` for the *process* around it, since Phase 4A-2 must still decide and lock the exact `key` values before any ID can be computed (see `priority-8-phase-4a1-stable-id-audit.md` §6). No IDs were allocated in this audit.

## Summary table

| # | Capability | Classification |
|---|---|---|
| 1 | 68 new full-pattern lemma identities | SUPPORTED AS-IS |
| 2 | Multiple meanings per lemma | SUPPORTED AS-IS |
| 3 | Multiple patterns per meaning | SUPPORTED AS-IS |
| 4 | Alternative schemas stay alternative | SUPPORTED WITH EDITORIAL DISCIPLINE |
| 5 | Optional complements | SUPPORTED AS-IS |
| 6 | Generalized-role realization labels | SUPPORTED WITH EDITORIAL DISCIPLINE |
| 7 | Lexical się/sobie identities | SUPPORTED AS-IS |
| 8 | Fixed lexical udział | SUPPORTED WITH EDITORIAL DISCIPLINE |
| 9 | Exact clause distinctions (incl. direct speech; 8 full-pattern + 1 metadata-only affected) | **REQUIRES FUTURE MODEL/SCHEMA CHANGE** |
| 10 | Metadata-only partner zaczynać→zacząć | **REQUIRES FUTURE MODEL/SCHEMA/CONTRACT CHANGE** |
| 11 | Metadata-only partner przeczytać→czytać | **REQUIRES FUTURE MODEL/SCHEMA/CONTRACT CHANGE** |
| 12 | Binding narrowing constraints (21) | SUPPORTED WITH EDITORIAL DISCIPLINE |
| 13 | activityEligibility stays inactive | SUPPORTED AS-IS |
| 14 | audioEligible independent permission | SUPPORTED AS-IS |
| 15 | Stable-ID expansion | SUPPORTED AS-IS (mechanism) / EDITORIAL DISCIPLINE (process) |

Three items (**#9, #10, #11**) are classified `REQUIRES FUTURE MODEL/SCHEMA(/CONTRACT) CHANGE`, each backed by direct static-code proof rather than inference: #9 by the absence of a `direct-speech` value in `CLAUSE_KINDS`; #10/#11 by the combination of `MEANINGS_REQUIRED`/`RUNTIME_MEANINGS_REQUIRED` (no zero-content lemma is valid) and `ASPECT_LINK_UNREVIEWED` (both sides of a reciprocal aspect link must already own reviewed pattern content) in `priority7_tooling.py`. All three remain open Phase 4A-2 decisions this audit does not resolve.
