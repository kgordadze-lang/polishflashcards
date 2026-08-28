# Priority 8 Phase 4G1 — scope historical release locks

## 1. Integration starting endpoint

Phase 4G1 began in the remote-free integration repository on
`priority-8-integration` at
`e8064b6d7fefaebc2b494433130dd36f74f2475e`, tree
`b2275437edf251ca2aa8316d65b46d346c6bed35`, subject `Priority 8 Phase 4F1
fix Verb Patterns search refresh`. The worktree and index were clean, remotes
and stashes were absent, `push.default` was `nothing`, and the executable
pre-push hook rejected pushes.

## 2. Original Phase 4C4C failures

The integration checkout reproduced 76/78 Phase 4C4C tests and 604/606 full
Priority 8 Python tests. The only failures were:

- `test_57_verify_only_mode_writes_nothing` expected `release.main([])` to
  return `0` but observed `1`;
- `test_58_repo_safety_controls_hold` expected the read-only safety gate to
  return normally but observed `GateFailure("wrong branch")`.

Both reached `priority8_phase4c4c_release_freeze.py:176`, where the historical
Phase 4C4C helper requires the current checkout to retain
`priority-8-phase-4c-architecture`.

## 3. First candidate and exposed Phase 4F1 lock

The first 4C4C-only candidate moved the old branch value to immutable
historical report evidence and passed 78/78. Full discovery then exposed
`test_12_release_markers_and_change_scope_are_frozen`: it used a HEAD-relative
diff from Phase 4E2 and treated the original Phase 4F1 path set as a permanent
allowlist for every later commit. That candidate was reverted and the retry
explicitly authorized correction of this second historical contract.

## 4. Contract classification

- The Phase 4C4C development branch value is a
  `HISTORICAL_PHASE_SNAPSHOT`.
- The Phase 4F1 parent-to-endpoint path delta is a
  `HISTORICAL_PHASE_SNAPSHOT`.
- Product structure, frozen identities, governance projection, lexical rules,
  direct speech, stable IDs, production digests, release markers, search
  behavior, audio/manifest identity, and migration/activity boundaries remain
  `CURRENT_GLOBAL_INVARIANT` checks.
- The current checkout branch, clean state, remotes, `push.default`, stash, and
  pre-push blocker are `WORKFLOW_SAFETY_ONLY` gates verified externally before
  and after the commit.

## 5. Authoritative Phase 4C4C endpoint and branch evidence

Local history verifies commit
`3d60bc61a85066007a659be4837aafc16131f0e4`, subject `Priority 8 Phase 4C4C
freeze approved release governance`, as the Phase 4C4C freeze endpoint. Its
immutable `reports/priority-8-phase-4c4c-release-freeze.md` records exactly that
the work began on `priority-8-phase-4c-architecture`.

The corrected test reads that report with `git show` at the full historical
commit SHA. Missing objects, invalid UTF-8, a missing marker, or duplicate
markers fail closed. The release helper's other branch-independent safety
checks remain live during the historical verify-only rehearsal.

## 6. Authoritative Phase 4F1 transition

The historical transition is pinned to:

- parent `61108de211934d50d44f89d3fc1876c5752f0f06`;
- endpoint `e8064b6d7fefaebc2b494433130dd36f74f2475e`.

An explicit local `git diff --name-status` between those objects must return
exactly, including status:

```text
M\tindex.html
A\treports/priority-8-phase-4f1-verb-patterns-search.md
A\ttests/test_priority8_phase4f1_verb_patterns_search.py
```

The corrected test no longer compares the current checkout to the Phase 4E2
parent. Missing objects, malformed rows, path changes, or status changes fail
closed.

## 7. No current allowlists

No development/integration/main branch allowlist was added. No Phase 4G1 path
was added to the historical Phase 4F1 set. The exact old values remain strict;
only their evaluation moved from mutable current workflow state to immutable
historical objects.

## 8. Historical negative controls

The Phase 4C4C test mutates the historical branch marker in memory from
`priority-8-phase-4c-architecture` to `main` and requires rejection. The Phase
4F1 test separately removes a required path, adds a fourth path, and changes
`index.html` from `M` to `A`; every mutation must be rejected.

## 9. Future-main compatibility

The tests prove a conceptual current branch of `main` cannot influence either
contract: the 4C4C branch proof reads only the historical report object, and
the 4F1 path proof reads only the explicit historical parent and endpoint.
Neither test switches branches or queries the current branch for release
correctness.

## 10. Live invariants preserved

All existing current semantic and product assertions remain live. The only
replaced assertions were the current checkout's old branch name and the
HEAD-relative interpretation of Phase 4F1's historical change scope. No skip,
xfail, expected failure, inequality weakening, checkout, network read, or
worktree mutation was introduced.

## 11. Verification results

The corrected targeted suites pass at their unchanged counts:

- Phase 4C4C: 78/78;
- Phase 4F1: 12/12.

The ordinary uncommitted full discovery is 605/606: its sole failure is the
unchanged Phase 4C3 `git status --short` dirty-worktree guard, which correctly
sees the authorized uncommitted Phase 4G1 paths and requires no fourth source
change. A clean proposed-endpoint run and the mandatory post-commit run are
required to pass 606/606.

All other named gates pass: `verify_audio.py`; Phase 1 17/17; Phase 1 playback
25/25; Phase 1B 1/1; Phase 4D1 5/5; Phase 4E1 5/5; migration 121/121; audio
fallback 585/585; and the staging validator.

The short learner check passes: Grammar → Verb Patterns reports 98 verbs and
269 patterns; global searches for `odpowiadać` and `radzić sobie` each return
Verb Patterns exactly once; and new MP3 `audio/9b1ffa9729fd.mp3` returns HTTP
200 as `audio/mpeg`.

## 12. Product, audio, and version immutability

No product or generation path differs from the Phase 4F1 endpoint.
`content/verb-patterns.json` retains SHA-256
`66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`
and counts 98/129/269/269. `APP_VERSION` is 8.13, shell cache is
`popolsku-v68`, and `AUDIO_CACHE` is `popolsku-audio`.

Audio verification retains 3,621 required phrases, 3,621 manifest entries,
3,621 MP3 files, 269/269 Verb Patterns coverage, and zero missing, orphaned,
empty, duplicate-normalization, or collision failures. The human-QA CSV,
governance inputs, activity eligibility, migration, and generation tooling are
unchanged.

## 13. Source repository and release handoff

The read-only source repository remains clean and remote-free at
`e8064b6d7fefaebc2b494433130dd36f74f2475e`, tree
`b2275437edf251ca2aa8316d65b46d346c6bed35`. Phase 4G1 is integration-only and
must not be ported to that source in this task.

After the single local Phase 4G1 commit, all clean-endpoint gates must be rerun.
No push or release is authorized; the next gate is independent read-only Phase
4G1 release verification.
