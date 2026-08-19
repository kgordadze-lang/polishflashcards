# Priority 7 Phase 4F-C2B — Independent Post-Implementation Closure Review

**Verdict: NO-GO**

The linguistic implementation, identity treatment, governance currency and
single-example product shape are internally sound.  Integration is blocked by
an independently discovered external-source collision in canonical row
P7-NR-043: its full Polish sentence is identical to the worked A2 example used
to teach the same instrumental construction in the published textbook
*Gramatyka dla praktyka — składnia*.  A second exact language-learning-source
collision exists for P7-NR-033.  The candidate labels both as
`editorial-generated` and its report claims that the generated examples are
not copied source examples.  On this record that claim cannot be independently
confirmed.  Resolving it requires provenance adjudication and, if necessary,
new canonical wording; this reviewer did not silently modify canonical text.

The arriving candidate also contained an independent technical blocker: six
historical suites reverted C2 examples after matching only Polish, English and
`origin.kind`, and removed the generation actor by ID alone.  Those helpers
could conceal mutations to durable identity, audio eligibility, detailed
provenance, or actor-role escalation.  This C2B workspace contains a narrow
test-only repair and negative controls.  That repair is necessary regardless
of the canonical NO-GO.

## 1. Candidate reconstruction

The supplied baseline resolves exactly:

- commit `080d92ad49a514332f21ecd90b4a11de070a243f`;
- tree `74dd8cbebc303b646e4e38e2082d25c91b1cf6e1`;
- zero remotes;
- `push.default=nothing`.

The arriving uncommitted candidate was exactly 20 files:

| Classification | Count | Paths |
|---|---:|---|
| canonical content/context | 2 | `editorial/verb-pattern-candidates.json`; `editorial/priority-7-authoring-context.json` |
| C1/C1B/C1C carried history | 8 | three `reports/phase-4fc1/*`; two `reports/phase-4fc1b/*`; two `reports/phase-4fc1c/*`; `tests/test_priority7_phase4fc1c.py` |
| C2 report/test | 2 | `reports/priority-7-phase-4fc2-summary.md`; `tests/test_priority7_phase4fc2.py` |
| historical test repair | 8 | Phase 3D-1, 3F-A, 4C, 4E, 4E.1, 4F-A, 4F-B3B and 5-A Python suites |

No path was unexplained.  C2B adds only this report and
`tests/test_priority7_phase4fc2b.py`; the contained repair changes no path
outside the eight already-modified historical suites.

## 2. Locked C1C implementation and sentence review

The carried adjudication matrix independently parses to 13 unique queue rows:

- 2 KEEP CURRENT: P7-NR-007 and P7-NR-014;
- 5 REPLACE: P7-NR-011, 012, 018, 033 and 036;
- 6 CREATE: P7-NR-031, 032, 035, 042, 043 and 044;
- 0 ADD and 0 open.

Both KEEP example objects are byte-identical to the pinned baseline, including
ID, key, bilingual text, audio flag and complete repository provenance.  All
five replacements carry the exact locked bilingual wording under their
unchanged durable key and ID.  All six creates carry the exact locked wording,
one deterministic new key/ID and no baseline predecessor.  No re-adjudication
or schema-only wording normalization occurred.

All 11 implemented examples were reviewed in their actual lemma, meaning,
aspect, complement, participant, CEFR and evidence context.  Their Polish is
contemporary and natural; their governed cases and prepositions are correct;
the English meanings are equivalent.  Enhanced scrutiny found no linguistic
defect in the rows for płacić, dbać, pytać, widzieć, myśleć, znaleźć,
opiekować się or zależeć.  In particular P7-NR-033 is unambiguously visual:
the inanimate geographic object cannot support the rejected encounter reading.

All 45 patterns have at most one example.  Every queue pattern has exactly
one, and the runtime continues to select only `examples[0]`; no invisible
second release-facing example was introduced.

## 3. Actor, provenance and reuse

Exactly one actor was added:
`priority7-example-generation`.  Its record is nonhuman, has kind
`example-generation-workflow`, and contains only the schema-valid
`example-generation` role.  It has no reference-verification,
editorial-review or product-approval role and no human/native/reviewer status.
The pre-existing `priority7-reference-analysis` record is byte-identical to
the baseline.  `authorRegistry` remains empty.

All 11 changed/created examples carry exactly the locked
`editorial-generated` origin with that actor, adoption date 2026-08-16 and no
repository or human-author fields.  The corpus has 29 examples: 18
repository-reuse, 11 editorial-generated and 0 original.  The two queue KEEP
sources independently resolve byte-for-byte and teach the intended patterns.

## 4. Identity

The Phase 1 stable-ID specification is authoritative over C1C's internally
inconsistent phrase “existing example IDs ... with re-minted keys.”  Keys are
durable semantic identity and example wording is explicitly an identity-
preserving change.  Re-minting a key would necessarily re-mint its deterministic
ID and contradict the first half of C1C's note.

All 29 IDs recompute from `(patternId, key)`; there are no duplicates, no
duplicate sibling keys, no tombstones, no tombstone reuse and no arbitrary
hand-authored ID.  The five REPLACE rows keep their baseline identities, the
six CREATE rows have deterministic new identities, and all other examples are
unchanged.

## 5. Governance and canonical field diff

The real derivation yields exactly:

- 45 `reference-verified`, 0 `research`;
- 47 reference-verification acceptances;
- 0 editorial-review events and 0 product-approval events;
- 0 editorial-reviewed and 0 approved patterns.

All 45 tier-1 scope digests and all review-event arrays are unchanged.  Tier-2
and tier-3 digests move on exactly the 11 REPLACE/CREATE rows and no others.

The corpus JSON diff has only these paths:

- for each of five REPLACE objects: `.pl`, `.en`, `.origin.kind`, removal of
  `.origin.repositorySource`, and addition of `.origin.generatorRef` and
  `.origin.adoptedAt`;
- addition of one `.examples` array on each of six CREATE patterns.

Enumerated by stable pattern identity, the changed corpus paths are:

| Pattern ID | Changed path(s) |
|---|---|
| `vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f` | `examples[0].pl`, `.en`, `.origin.kind`, `.origin.generatorRef`, `.origin.adoptedAt`; `.origin.repositorySource` removed |
| `vp-p-placic-pay-za-accusative-goods-73c6760c091d` | same six replacement paths |
| `vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c` | same six replacement paths |
| `vp-p-widziec-perceive-visually-accusative-object-80b697e51432` | same six replacement paths |
| `vp-p-znalezc-find-accusative-object-d80c52211462` | same six replacement paths |
| `vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8` | `examples` added |
| `vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a` | `examples` added |
| `vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2` | `examples` added |
| `vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939` | `examples` added |
| `vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b` | `examples` added |
| `vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318` | `examples` added |

The context JSON diff has only `$.contextNotice` and the added
`$.editorialActorRegistry.priority7-example-generation` object.  The notice is
necessary, specific and truthful about the actor, counts, provenance and
unchanged governance ceiling.  No lemma, meaning, complement, relation type,
CEFR, teaching status, eligibility, evidence, review event, release mode,
shipping field or runtime field changed.

## 6. External-source boundary — blocker

The repository-local scan confirms that none of the 11 generated examples is
falsely labelled repository reuse and none matches a shippable repository
entity.  The independent external scan does not support the broader C2 claim:

- P7-NR-043 exactly duplicates a worked example in [*Gramatyka dla praktyka —
  składnia*](https://sjo.wum.edu.pl/system/files/gramatyka_dla_praktyka_-_przykladowe_strony.pdf),
  where it explicitly teaches the same `opiekować się` / Instrumental
  construction at A2.  The 2017 book predates this candidate and its sample
  pages are publicly available from institutional and bookseller sites.
- P7-NR-033 has an exact pre-existing hit in an [A1/A2 language-course
  script](https://audioacademyeu.eu/pl/wp-content/uploads/sites/5/2018/10/Audioacademyeu_skrypt_Slownictwo-anglielskie-A1A2_part02.pdf).
- P7-NR-018 has exact pre-existing public-prose hits.  Because it is a short,
  ordinary sentence rather than a worked language example, that collision is
  noted but is not independently blocking.

This report does not reproduce any external source example.  It identifies
canonical row IDs only.  Coincidence is possible for short learner sentences,
but the explicit same-construction textbook collision means an independent
reviewer cannot affirm “not copied source examples” without provenance
adjudication.  Canonical correction is outside C2B authority.

## 7. Historical-suite audit and contained repair

The eight modified historical suites are Phase 3D-1, 3F-A, 4C, 4E, 4E.1,
4F-A, 4F-B3B and 5-A.  The first two replace closed actor-key-set assertions
with the actual historical release blocker: no actor has an editorial-review
capability.  That remains meaningful and detects role escalation.

The other six normalize later C2 example/actor work before asserting their
historical checkpoint.  Their arriving implementation was over-broad:

- a CREATE example was dropped after checking only Polish, English and origin
  kind, hiding any ID, key, audio, generator, date or extra-provenance mutation;
- a REPLACE object had the same gap before its old text/source was restored;
- the C2 actor was removed by key regardless of human flag, kind, role set,
  phase, note or extra fields.

The repair now recognizes the complete approved example object: locked text,
locked key, recomputed ID, `audioEligible=false`, and the exact provenance
object.  It removes the actor only when every field and the note digest match
the approved C2 record.  Any mutation therefore remains in the historical
comparison.  `tests/test_priority7_phase4fc2b.py` exercises every one of the
six normalizers with identity, audio, provenance, second/out-of-queue example,
meaning, complement, evidence, reference-event, extra-actor and role-escalation
controls.  The exact legitimate C2 candidate still normalizes to the pinned
checkpoint.

## 8. C1C path and B3B transition repairs

The transferred C1C suite now resolves the exact artifacts under
`reports/phase-4fc1c/`.  Its source inputs retain their supplied SHA-256
digests, and only the path/location constants changed; no C1C assertion or
review artifact was weakened.

The B3B historical transition remains exactly
`7beb50d7b3463d7745352f1608f1e30019529fdf` to
`080d92ad49a514332f21ecd90b4a11de070a243f`.  `B3B_FOOTPRINT` remains its
original 11 paths and contains no C2/C2B file.  Executable three-commit replay
tests prove that an unauthorized file inside the transition fails while later
phase files do not widen the historical answer.

The known Phase 5-A status-only shipping allowlist debt was not expanded.  No
new uncovered shipping mutation was found.

## 9. Validation

The final uncommitted C2B workspace passes every requested technical gate:

| Gate | Result |
|---|---|
| C2B | 15 tests, 0 failures/errors |
| Required targeted Python (C2B, C2, C1C, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A) | 910 tests, 0 failures/errors |
| Full Python discovery | 1,126 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| `validate_content.py` | pass: 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs |
| `verify_audio.py` | pass: 3,377 required phrases, manifest entries and MP3 files; 0 missing/orphaned |
| `build_pages.py --check` | current: 23 grammar, 6 vocabulary and guide hub; 32 sitemap URLs; 380 audio-bearing strings |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | pass |

The Python runs emit pre-existing `ResourceWarning` diagnostics for unclosed
read handles; they do not fail a gate and are outside this closure scope.

## 10. Fresh committed-scratch rehearsal

A fresh local clone was overlaid with the reviewed candidate, its `origin`
remote was removed, and exactly the 22 reviewed files were committed on top of
the supplied baseline.  The final rehearsal state is clean, has zero remotes,
and has `080d92ad49a514332f21ecd90b4a11de070a243f` as `HEAD^`.

The first committed run correctly exposed a defect in the new C2B test: it
required a dirty workspace and therefore failed after commit.  The guard was
repaired to accept exactly either an uncommitted candidate at the pinned
baseline or a clean one-commit scratch whose parent is that baseline.  The
committed targeted C2B/C2/C1C/B3B battery then passed 322 tests.  The final
committed battery records:

| Gate | Result |
|---|---|
| C2B + C2 + C1C + B3B | 322 tests, 0 failures/errors |
| Full Python discovery | 1,126 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| content / audio / pages / editorial | all pass, with the same totals as the real workspace |
| `git diff --check HEAD^ HEAD` | pass |
| clean / zero remotes | pass |

Representative committed negative controls were applied and restored only in
the scratch:

- wording mutation on an example outside the C1C queue: all six exact
  historical normalizer comparisons failed;
- unauthorized meaning mutation: the C2 field guard failed and the validator
  returned `REVIEW_STATE_MISMATCH`;
- generation-actor role escalation: both the C2 minimal-role guard and all six
  C2B actor-normalizer comparisons failed;
- shipping mutation in `priority7_tooling.py`: the pinned shipping guard
  failed.

After restoration the scratch was clean.  These controls demonstrate that the
normalizers no longer erase unauthorized content and that the committed-state
guards retain teeth.

## Final verdict

**NO-GO**

The implementation is linguistically and structurally coherent and the
historical guards retain teeth after the contained repair, but the external
source/provenance boundary for canonical P7-NR-043 (and independently
P7-NR-033) is unresolved.  Do not integrate, create review events, approve,
freeze, project runtime or begin the next phase.  Return the source collision
to adjudication.
