# Priority 7 Phase 4F-C2D — Final Independent Closure

**Original C2D verdict: GO WITH CHANGES REQUIRED**

**Final verdict: GO**

Canonical content is sound. The final C2C sentence pairs, process-based
provenance, durable identities, governance state, and the six C2B historical
normalizers close cleanly. C2D originally repaired the C2B/C2C footprint tests
by naming and excluding C2D's two artifacts. That justified the original
`GO WITH CHANGES REQUIRED`, but the exclusion architecture was still not
future-safe: another honest phase would have required another historical edit.
C2D.1 removes that successor-name coupling entirely. Each historical suite now
inspects only its own artifacts, immutable baseline, reconstruction, and
protected canonical/governance behavior. The exact current 27-path candidate
transition remains independently enforced by C2D.

Nothing in this review creates an editorial-review event, product-approves,
freezes, projects runtime, pushes, adds a remote, or begins another phase.

## Closure result

- The C2C adjudication CSV has exactly `P7-NR-033` and `P7-NR-043`.
- `P7-NR-033` is exactly `Czy widzisz tę czerwoną torbę?` / `Do you see that
  red bag?`.
- `P7-NR-043` is exactly `Dziś opiekuję się młodszą siostrą.` / `Today I'm
  looking after my younger sister.`.
- Undoing those two pairs reproduces the arriving C2 corpus byte-for-byte.
  Relative to C2, only the four `.pl`/`.en` values moved; the authoring context
  is byte-identical.
- The two superseded Polish strings are absent from canonical content and
  remain present in historical C1C/C2/C2B material.
- All eleven implemented examples are grammatical, natural, level-appropriate,
  and English-equivalent. The two `pytać` frames remain distinct; the C2
  Accusative corrections on 012/018/036 remain transparent; 044 remains one
  sentence.
- `tę czerwoną torbę` is overt feminine Accusative and its inanimate visual
  object removes the encounter reading. `młodszą siostrą` is overt feminine
  Instrumental and directly realizes `opiekować się` + Instrumental.
- The disclosed shorter span inside a different punctuation example is
  non-blocking under the process-based provenance standard. Targeted searches
  on 2026-08-16 found no exact complete-sentence hit for either final Polish
  sentence; this is a best-effort screen, not a global-uniqueness claim.

## Canonical, identity, actor, and governance boundary

- Baseline → final changes exactly eleven pattern rows, through their example
  lists: five replacements and six creates. No non-example pattern field,
  lemma, meaning, complement, relation type, CEFR, teaching status,
  activity eligibility, evidence, review history, or release mode changed.
- The only context changes from the immutable baseline are `contextNotice` and
  the one added `priority7-example-generation` actor. The existing reference
  actor is byte-identical.
- The generation actor exists once with `human=false`, kind
  `example-generation-workflow`, and roles exactly `["example-generation"]`.
  `authorRegistry` remains empty.
- There are 29 examples: 18 repository reuse and 11 editorial generated. All
  IDs recompute, all IDs and sibling keys are unique, the five replacements
  retain identity, the six creates use deterministic new identity, and C2C
  minted no new key or ID.
- Governance remains 45 `reference-verified` rows and 47
  `reference-verification` acceptances, with zero research,
  editorial-reviewed, approved, editorial-review events, or product-approval
  events. Tier-1 digests equal baseline. Against baseline the higher-scope
  changed set is the same eleven C2 rows; relative to C2 only 033 and 043 have
  changed higher-scope values.

## History and negative controls

C1, C1B, C1C, C2, the C2B **NO-GO**, and C2C remain historical artifacts and
were not rewritten. B3B still checks the immutable transition
`7beb50d7b3463d7745352f1608f1e30019529fdf` →
`080d92ad49a514332f21ecd90b4a11de070a243f`, with exactly eleven paths.

All six repaired historical normalizers accept the exact final candidate and
reject mutations to a third example, either overridden wording, example ID or
key, provenance, actor role, meaning, complement, evidence, and review event.
The C2C mechanism is exactly two rows wide. The known 5-A status-only shipping
allowlist remains separate and nonblocking because the committed-state guards
in the historical suites remain pinned and mutation-tested.

## Contained technical repairs

The final repair changes the same four C2D-owned/test paths and no production,
canonical, context, or historical report path:

- `tests/test_priority7_phase4fc2b.py` — removes all successor-artifact lists,
  live status/diff footprint comparison, and one-commit workspace assumptions;
  it now proves its own two artifacts, the immutable baseline, exact candidate
  reconstruction, normalizer behavior, C2B findings, and C2B NO-GO.
- `tests/test_priority7_phase4fc2c.py` — removes the C2D exception and live
  global footprint/workspace assumptions; it now proves its own three
  nonshipping artifacts plus the exact two-row override, preserved history,
  identity, provenance, governance, source boundary, and normalizer teeth.
- `tests/test_priority7_phase4fc2d.py` — verifies that neither historical suite
  names C2D, keeps the exact 27-path candidate boundary as the first immutable
  transition after the baseline, and behaviorally commits harmless later
  report/test artifacts in an isolated repository and runs C2B/C2C there.
- `reports/priority-7-phase-4fc2d-summary.md` — records the original verdict,
  the architectural defect in the first repair, the future-safe replacement,
  behavioral contrast, validation, and final verdict.

### Demonstrated old and new behavior

Before C2D.1, adding an untracked harmless later report to a committed C2D
scratch produced four failures: C2B and C2C each failed both their closed
footprint and one-commit workspace-mode assertion. Committing that same report
still produced the same four failures: the report entered the baseline-to-HEAD
diff and `HEAD^` was no longer the baseline. Thus both untracked and committed
later files participated, and a hypothetical Phase 4F-D report/test would
fail.

After C2D.1, C2B/C2C do not read live untracked paths or a baseline-to-current
global footprint at all. Committed later files also do not participate: the
historical suites check their phase-owned artifact constants and contents,
while protected content is reconstructed against the immutable baseline and
mutation-tested. C2D's current exact boundary is separately defined as the
baseline-to-first-descendant transition, so later commits do not widen it.

Repository-wide search found no other Priority 7 historical test that passes
by explicitly enumerating C2D or another later phase's report/test filenames.
C1C uses a phase-owned prefix model; B3B names an immutable two-commit
transition and includes a later-phase replay; C2 uses a current candidate-stage
prefix boundary. The known 5-A status-only debt was not changed.

## Validation

### Real uncommitted C2D workspace

| Gate | Result |
|---|---|
| C2D | 28 tests, 0 failures/errors |
| Named phase battery (C2D, C2C, C2B, C2, C1C, B3B, 4F-A, 4E.1, 4E, 5-A, 4C, 3D-1, 3F-A, 2A) | 1,018 tests, 0 failures/errors |
| Full Python discovery | 1,234 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| `validate_content.py` | 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs; pass |
| `verify_audio.py` | 3,377 required phrases, 3,377 manifest entries, 3,377 MP3 files, 0 missing/orphaned |
| `build_pages.py --check` | current: 23 grammar, 6 vocabulary, guide hub, 32 sitemap URLs, 380 audio-bearing strings |
| `priority7_tooling.py validate-editorial` | valid |
| `git diff --check` | pass |

Python emits the same pre-existing unclosed-read-handle `ResourceWarning`
diagnostics recorded by prior phases. They fail no gate and were not broadened
into this closure.

### Fresh committed scratch

A fresh isolated clone received the complete candidate and was committed only
there. The final commit has exactly 27 paths over the baseline; `HEAD^` is
`080d92ad49a514332f21ecd90b4a11de070a243f`; the working tree is clean; and
the scratch has zero remotes.

| Gate | Result |
|---|---|
| C2D + C2C + C2B + C2 + C1C + B3B | 430 tests, 0 failures/errors |
| Full Python discovery | 1,234 tests, 0 failures/errors |
| Full JXA | 36 suites, 10,544 assertions, 0 failed |
| Content / audio / pages / editorial | all pass with the same totals as the real workspace |
| `git diff --check HEAD^ HEAD` | pass |

Six committed-scratch mutations were applied one at a time and restored:
third-row wording, example key, generator provenance, actor-role escalation,
complement case, and reference-event decision. Every mutation made C2D exit
nonzero; the exact candidate passed again after restoration and the scratch
returned clean. The in-memory C2D controls additionally cover meaning,
evidence, both overridden rows, and all six historical normalizers.

The real C2D workspace remains uncommitted and has zero remotes.
