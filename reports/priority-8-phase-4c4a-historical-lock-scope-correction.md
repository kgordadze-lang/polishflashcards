# Priority 8 Phase 4C4A — historical Priority 7 lock scope correction

## 1. Starting endpoint

| Check | Value |
|---|---|
| Branch | `priority-8-phase-4c-architecture` |
| HEAD | `4e81202591cf2c8609983346e3c24fe2c185a8b8` |
| Subject | `Priority 8 Phase 4C4A prepare release governance` |
| Worktree / remotes / push default / pre-push | clean / zero / `nothing` / executable fail-closed |
| Editorial universe | 98 lemmas: 30 retained Priority 7 + 68 Priority 8 |
| New Priority 8 patterns | 224, all `editorial-reviewed` |
| Product approval / release authorization | zero / absent |
| Allocation registry / tombstones | `{}` / zero |

## 2. Human authorization and adjudication

The human authorized test-scope correction only. The controlling read-only
adjudication verdict was:

> ALL 32 ARE HISTORICAL PRIORITY 7 SCOPE LOCKS - SAFE TO CORRECT

The obsolete count of 30 regressions was cancelled. The verified differential
model is 611 parent failing methods, 634 current failing methods, 24 newly
failing methods, one legitimately resolved parent failure, and 32 newly red
historical assertion locations. Eight of those locations occur earlier inside
methods already failing at the parent.

## 3. Authorized files

Exactly these nine tests changed:

- `tests/test_priority7_phase3b.py`
- `tests/test_priority7_phase3d1.py`
- `tests/test_priority7_phase4c.py`
- `tests/test_priority7_phase4e.py`
- `tests/test_priority7_phase4e1.py`
- `tests/test_priority7_phase4fa.py`
- `tests/test_priority7_phase4fb3b.py`
- `tests/test_priority7_phase4fh3.py`
- `tests/test_priority7_phase4fi1.py`

This report is the tenth and only added path.

## 4. Identity-scope strategy

Each affected suite derives the exact released Priority 7 lemma, meaning and
pattern stable-ID sets from `content/verb-patterns.json`. The selector then:

1. selects by stable identity, never by position;
2. requires exact set equality at all three hierarchy levels;
3. rejects a missing, renamed or duplicated P7 identity;
4. ignores ordering;
5. permits non-P7 entities to coexist outside the historical slice.

Where a suite already reconstructed an earlier phase with normalizers, that
normalization still runs first and the exact P7 identity slice is selected
afterward. Existing exact count, state, event, evidence and semantic assertions
then run unchanged in strength over the scope they historically owned.

## 5. Exact 32 corrected locations

| # | Historical location | Correction |
|---:|---|---|
| 1 | `phase3b:752` fixture corpus pattern count | Count the exact P7 slice; retain full-corpus leakage sweeps. |
| 2 | `phase3b:812` historical state count | Apply phase normalization, then select exact P7 identities; keep live activity/audio totals global. |
| 3 | `phase3d1:895` Phase 3D2 advancement prerequisite | Evaluate P7 patterns and P7-owned actors only. |
| 4 | `phase3d1:767` 30-lemma checkpoint | Select exact P7 identities after normalization. |
| 5 | `phase3d1:432` 30-lemma stable-ID-space snapshot | Scope only the count; keep no-exercise/no-freeze token checks global. |
| 6 | `phase4c:1322` normalized corpus shape | Select exact P7 identities after the historical normalizer. |
| 7 | `phase4c:1344` 122-record evidence lock | Count evidence owned by exact P7 patterns. |
| 8 | `phase4c:340` 45-row ledger bijection | Compare ledger IDs with exact P7 pattern IDs. |
| 9 | `phase4c:762` Phase 4F-A 45-pattern state lock | Evaluate the exact P7 pattern set. |
| 10 | `phase4e:2384` Phase 4F-A actor set | Select exact historical P7 actor identities. |
| 11 | `phase4e:2334` 45-pattern tier-one checkpoint | Evaluate the exact normalized P7 set. |
| 12 | `phase4e:2291` solo-chain 45-pattern count | Scope P7 chain assertions while retaining global human-authority exclusions. |
| 13 | `phase4e1:2199` fixed P7 actor on every event | Apply the fixed actor assertion only to P7 histories. |
| 14 | `phase4e1:2166` exact Phase 4F-A inventory | Evaluate exact P7 identities after normalization. |
| 15 | `phase4e1:2250` Phase 4E.1 actor set | Select exact historical P7 actor identities. |
| 16 | `phase4fa:948` no row above reference-verified | Apply the Phase 4F-A state ceiling to P7 patterns. |
| 17 | `phase4fa:855` 30/34/45 inventory | Preserve exact totals over exact P7 identities. |
| 18 | `phase4fa:1377` WSJP reinspection total | Count P7-owned WSJP evidence only. |
| 19 | `phase4fa:1372` historical evidence date set | Preserve the exact P7 source/date distribution. |
| 20 | `phase4fa:1346` repaired evidence total | Count P7-owned evidence only. |
| 21 | `phase4fa:1489` Phase 4F-A matrix coverage | Bijection against exact P7 pattern IDs. |
| 22 | `phase4fa:1180` one review actor at Phase 4F-A | Select P7 actors before asserting that phase's role boundary. |
| 23 | `phase4fa:1012` standing reference scope digest | Apply the reference-stage-last-event assumption only to Phase 4F-A P7 histories. |
| 24 | `phase4fa:1092` Phase 4F-A inspection date in event notes | Apply the fixed historical date to P7 events only. |
| 25 | `phase4fb3b:1461` no editorial advancement | Apply the B3B state snapshot to P7 patterns. |
| 26 | `phase4fb3b:1410` 45 reference-verified patterns | Evaluate exact P7 pattern identities. |
| 27 | `phase4fb3b:1383` 54/52/2 complement statistics | Count complements owned by exact P7 patterns. |
| 28 | `phase4fh3:702` H2.1 governance totals | Preserve exact counts and approval totals over P7 patterns. |
| 29 | `phase4fh3:725` teaching-status split | Preserve the exact historical P7 badge population. |
| 30 | `phase4fi1:455` editorial/runtime pattern-ID equality | Compare runtime with the exact released P7 pattern set. |
| 31 | `phase4fi1:494` editorial/runtime example equality | Compare runtime examples with exact P7 examples. |
| 32 | `phase4fi1:290` I1 30/34/45/45 approved checkpoint | Preserve all exact assertions over exact P7 identities. |

Distribution remains 2 / 3 / 4 / 3 / 3 / 9 / 3 / 2 / 3 across the nine files.

## 6. Scope by category

### Corpus identity

The selectors require the complete released P7 lemma, meaning and pattern ID
sets with no missing, renamed or duplicated identity. The original exact phase
statistics continue to apply after that fail-closed identity gate.

### Actor registry

The exact P7 actor identities are selected explicitly. The historical tests
continue to require the same actor records, roles and fixed event actor. No
global actor count was introduced. Global tooling still requires `human:false`,
recognized roles, role possession, correct actor/reviewer reference types and
reference/editorial independence.

### Evidence

The Phase 2B and Phase 4F-A totals, source distributions and dates remain exact
over evidence owned by P7 patterns. Global evidence validation remains over the
full corpus; the 224 grounded P8 evidence records are neither discarded nor
relabelled as P7 history.

### Matrix and optional complements

The historical 45-row matrix bijects exactly to the 45 P7 pattern IDs. The
54-complement / 52-required / two-optional characterization remains exact over
the P7 patterns containing the two named refreshed rows.

### Global checks retained

Fixture leakage still sweeps every current editorial lemma and gloss. Live
activity/audio exposure remains global. Human/nonhuman separation, actor role
validity, approval derivation, runtime isolation, closed release behavior and
full-corpus editorial validation were not narrowed.

## 7. Waterfall restoration

After correction the eight pre-existing-failure methods reach the same
historical assertions again (line numbers below are the original adjudicated
locations; inserted helper code shifts physical current line numbers only):

| Row | Before correction | Restored parent assertion |
|---:|---:|---:|
| 2 | 812 | 814 |
| 3 | 895 | 910 |
| 4 | 767 | 736 |
| 6 | 1322 | 1325 |
| 11 | 2334 | 1972 |
| 13 | 2199 | 2197 and 2213 |
| 14 | 2166 | 1896 |
| 23 | 1012 | 1009 and 1017 |

No pre-existing assertion in those methods was repaired.

## 8. Legitimately resolved parent failure

`test_priority7_phase4fi1.InvariantTests.test_the_editorial_validator_still_accepts_the_untouched_corpus`
remains passing. The parent had the sole `FORMAT_VERSION` issue; the authorized
formatVersion 1 to 2 contract transition removed it. This correction does not
recreate that defect.

## 9. Adversarial self-review

The same mutation harness was executed against all nine identity selectors:

- remove one P7 lemma: rejected;
- rename a P7 lemma, meaning or pattern stable ID: rejected;
- duplicate one P7 lemma: rejected;
- reverse corpus ordering: accepted with identical P7 identity set;
- coexist with all 68 P8 lemmas: accepted without changing P7 results.

Actor mutations showed that removing the P7 reference actor or changing its
role breaks the historical invariant; appending a valid P8 actor leaves the P7
slice unchanged; and an invalid P8 role is still rejected globally with both
`EDITORIAL_ACTOR_ROLE` and `EDITORIAL_ACTOR_ROLE_UNKNOWN`.

Removing P7 evidence or changing a historical evidence date changes the exact
historical lock. Removing a matrix row breaks the P7 bijection. Existing P8
evidence and patterns do not affect either P7 total.

## 10. Historical differential

| Measurement | Parent | Phase 4C4A before | Corrected dirty tree | Required clean committed endpoint |
|---|---:|---:|---:|---:|
| All-suite unique failing methods | 611 | 634 | 607 inferred | 610 |
| Nine-suite unique failing methods | 316 | 339 | 312 measured | 315 |
| Nine-suite failing assertion locations | 321 | 346 | 317 measured | 320 |
| Newly failing methods vs parent | — | 24 | 0 | 0 |
| Newly red adjudicated locations | — | 32 | 0 | 0 |

The dirty-tree method/location counts are three lower because three old
footprint guards see the authorized uncommitted test paths and temporarily
pass. They deterministically return to their pre-existing failure when the
worktree becomes clean. The clean endpoint therefore equals the parent
baseline minus only the one legitimate formatVersion-resolved failure.

## 11. Priority 8 verification

`python3 validate_priority8_staging.py` passes.

Before commit the 16 governed suites ran 483 tests with exactly one failure:
`test_46_no_unexpected_changed_paths_exist`. Its diagnostic was precisely the
nine authorized dirty test paths. This Phase 4C3 guard is intentionally
clean-worktree-sensitive. The required post-commit rerun is 483/483.

## 12. Governance and production immutability

All governed editorial and Phase 4C artifact hashes match their starting
values. Production runtime, tooling, shell, service worker and audio hashes
also match. This change contains tests and this report only.

## 13. Independent-review gate

The correction is ready only if the clean committed endpoint confirms:

- 610 all-suite / 315 affected-suite failing methods under the adjudicated
  comparison model;
- 320 affected-suite parent assertion locations after accounting for shifted
  source lines;
- no newly failing method or semantic assertion location;
- 483/483 governed Priority 8 tests;
- byte-identical governance and production artifacts.

Human product review remains unopened pending independent verification.
