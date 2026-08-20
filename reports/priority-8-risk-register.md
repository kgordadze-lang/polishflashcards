# Priority 8 Phase 0 — risk register

| Category | Risk | Impact | Mitigation | Owning phase |
|---|---|---|---|---|
| Linguistic | Wrong case/preposition government | teaches error | contemporary sense-specific verification; independent editorial review | 3–5 |
| Linguistic | Valid but uncommon/dated frame | distorted priorities | usage/register evidence; defer weak frames | 3 |
| Linguistic | Meaning and pattern conflated | misleading inheritance | selective meaning scopes; separate IDs | 3–5 |
| Linguistic | Complement confused with adjunct | false valency claim | explicitly test destination/source/time/vehicle/beneficiary status | 3–4 |
| Linguistic | Incorrect aspect relationship | wrong transfer | research each lemma independently; reciprocal links only | 3–5 |
| Linguistic | Reflexive/non-reflexive conflation | wrong identity/meaning | lexical `się` in lemma identity; no inheritance | 3–5 |
| Linguistic | A1–B1 overloaded by advanced frames | poor sequencing | pattern-level CEFR; recognition/defer policy | 4–5 |
| Linguistic | Ambiguous English translation | wrong learner interpretation | bilingual editorial review against exact meaning | 4–5 |
| Audio | TTS mispronunciation/prosody | bad model | generate after freeze; human QA exact 25/current and all later new | 1, 7 |
| Audio | Generation before text freeze | orphan/rework | generation gate after current-digest approval | 1, 7 |
| Audio | Duplicate clips/collisions | drift/overwrite | one normalized set; explicit duplicate map; fail on differing-text key collision | 1 |
| Audio | Manifest drift/missing/orphans | silent fallback/storage | bidirectional verifier in release gate | 1, 7, 9 |
| Audio | Stale/overlapping playback | wrong sentence speaks | one owner, settled latch, identity guards, switching tests | 1 |
| Audio | Offline regression | unusable control | warm/unwarmed/Range/cache-skew tests | 1, 9 |
| Audio | Excess volume/cache growth | eviction/data cost | reuse first; lazy cache; monitor 4,200-entry headroom | 7, 9 |
| Audio | Voice inconsistency | learner confusion | Marek clip first; visible device-voice fallback; QA | 1, 7 |
| Technical | Unstable/recycled IDs | broken audit history | frozen allocations/tombstones; never position-derived | 4–6 |
| Technical | Wrong runtime revision | cache/governance ambiguity | official transition only; staged revision 2 then 3 | 1, 6 |
| Technical | Service-worker regression | offline/cache failure | preserve strategies; no forced activation; full JXA worker suites | 1, 9 |
| Technical | Private data leaks public | copyright/governance breach | official closed projection; privacy sweep | 5–6 |
| Technical | Audio and activity policy drift | accidental Listening | one-way invariant and explicit negative tests | 1, 8 |
| Technical | Schema creep | unnecessary migration | keep schema/migration 2; separate approval for persistence | all |
| Technical | Duplicate player/parser | maintenance divergence | extend shared rule/player/runtime loader only | 1 |
| Governance | Unsupported AI linguistic claims | false authority | label provisional; human-owned approval; source locators | 0, 3–5 |
| Governance | Insufficient corroboration | weak corpus | WSJP PAN preferred; defer/replace | 3 |
| Governance | Over-expansion | diluted quality | freeze ~70, reserve pool, per-phase exit gates | 2 |
| Governance | Copyright/source misuse | legal/reputational harm | paraphrase facts; no private examples/index publication | 3–4 |
| Governance | Reviewer-role confusion | invalid approval | actor roles/digests; AI not linguistic/product approval | 3–5 |
| Governance | Approval-state drift after flag/text change | stale release | recompute digests; re-review/reapprove | 1, 5, 7 |
| Process | Bundle audio and 70 lemmas | unreviewable release | staged revision 2 audio then revision 3 expansion | 1–7 |
| Process | Trust prose counts | hidden drift | machine-readable CSV and recalculation gates | all |
| Process | Self-referential discovery diff | unstable artifact | generate diff last excluding itself | 0 |
| Process | Alter historical provenance tests | destroys evidence | add successor tests, never rewrite history | all |
| Process | Start learner work before shortlist approval | wasted/unauthorized scope | Phase 2 human freeze gate | 2 |
| Process | Cross repository/security boundary | production risk | exact path/remotes/hook checks before/after; reports-only diff | 0 |

The highest combined risks are policy coupling (`audioEligible` vs Listening), premature synthesis, weak external support for low-evidence include candidates, and a combined mega-release. The staged plan directly addresses each.
