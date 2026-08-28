# Priority 8 — final pre-release cleanup

## 1. Starting committed endpoint

This continuation used only
`/Users/Kaj/Documents/polishflashcards-priority-8-integration` on branch
`priority-8-integration`.

| Check | Observed |
|---|---|
| HEAD | `957554d88a3b59acf78f6cae131a3585538ae962` |
| Tree | `4fcbf25cc27457a0bf8a9ea205d428847d5c3180` |
| Remotes | zero |
| `push.default` | `nothing` |
| Pre-push hook | executable and fail-closed |
| Stash | empty |

The continuation began with exactly 34 preserved, authorized paths: 32
generator-owned outputs plus comment-only edits to `sw.js` and
`pp-verb-patterns.js`. No report or commit yet existed.

## 2. Hygiene audit findings

The final read-only hygiene audit found three stale release-maintenance items:

1. the checked-in public-page projection was stale after APP_VERSION moved from
   8.12 to 8.13;
2. the service-worker cache-policy explanation still described the former
   3,402-clip library rather than the released 3,621-clip library;
3. the verb-pattern transport comment still described the obsolete Phase 3F-A
   startup state.

No product logic, learner content, audio, manifest, QA adjudication, release
marker, debugger, unintended production logging, credential, or production
AI/model-attribution issue was found.

## 3. Generator drift and regeneration

Before regeneration, `python3 build_pages.py --check` identified 32 stale
generator outputs. The authorized correction was produced by:

```text
python3 build_pages.py
```

The exact regenerated output was:

```text
M grammar/biernik-accusative/index.html
M grammar/celownik-dative/index.html
M grammar/dopelniacz-genitive/index.html
M grammar/jesli-i-gdyby-conditions/index.html
M grammar/kazdy-i-wszyscy-every-vs-all/index.html
M grammar/korespondencja-formal-writing/index.html
M grammar/ktory-relative-clauses/index.html
M grammar/liczebniki-numbers-meet-cases/index.html
M grammar/mianownik-nominative/index.html
M grammar/miejscownik-locative/index.html
M grammar/narodowosci-nationalities/index.html
M grammar/narzednik-instrumental/index.html
M grammar/pan-i-pani-formal-address/index.html
M grammar/panowie-panie-panstwo-plural-formal-address/index.html
M grammar/przeczenie-negation/index.html
M grammar/przymiotniki-adjectives-traits/index.html
M grammar/stopniowanie-comparison/index.html
M grammar/tryb-przypuszczajacy-conditional/index.html
M grammar/wolacz-vocative/index.html
M grammar/zaimki-pronouns-determiners/index.html
M grammar/zawody-professions/index.html
M grammar/zdrobnienia-diminutives/index.html
M grammar/zeby-so-that-want-to/index.html
M guide/index.html
M guide/listening/index.html
M sitemap.xml
M vocabulary/everyday-polish-slang/index.html
M vocabulary/polish-corporate-slang/index.html
M vocabulary/polish-exclamations/index.html
M vocabulary/polish-idioms/index.html
M vocabulary/polish-party-slang/index.html
M vocabulary/polish-proverbs/index.html
```

Each of the 31 HTML pages has one generated version-line replacement from
v8.12 to v8.13. None retains v8.12. The generator also refreshed all 31
corresponding sitemap `<lastmod>` values from `2026-08-20` to `2026-08-28`.
No hand-edited generated output is present.

The post-regeneration check passes:

```text
build_pages.py --check: committed output is current. 23 grammar pages +
6 vocabulary pages + /guide/ hub. sitemap.xml lists 32 URLs.
380 sentences/words carry pronunciation audio.
```

## 4. Comment cleanup

`sw.js` now describes the verified 3,621-clip library and the unchanged 4,200
entry ceiling as 579 entries of headroom, about 16%. Only comments changed;
`AUDIO_CACHE_MAX_ENTRIES`, trimming, retry, and all runtime behavior are
unchanged.

`pp-verb-patterns.js` now states the released transport contract: a caller must
supply an injected request function and URL; application startup supplies the
released runtime document and tests may supply isolated inputs. Only the
obsolete Phase 3F-A comment changed.

## 5. Phase 4C3 historical scope-lock failure

The original full Priority 8 run executed 606 tests with exactly one failure:

```text
Priority8Phase4C3CanonicalProjectionTests.
test_46_no_unexpected_changed_paths_exist
```

The assertion at the former line 530 ran:

```text
git status --short
```

It stripped each current status row to a path set and asserted that the set was
a subset of a Phase 4C3-era allowlist. It did not start from any immutable
historical endpoint; its effective reference was the current index/worktree.
Consequently, all 32 later generator outputs plus `sw.js` and
`pp-verb-patterns.js` were rejected even though no canonical or product
assertion failed.

## 6. Classification

The exact files changed by Phase 4C3 are a
`HISTORICAL_PHASE_SNAPSHOT`. They must be checked against the immutable Phase
4C3 transition.

The remainder of the Phase 4C3 suite continues to enforce
`CURRENT_GLOBAL_INVARIANT` behavior where appropriate, including the canonical
structure, counts, IDs, semantics, source/target roles, direct speech,
required lexical items, recognition-only handling, audio eligibility, and
production digest. Branch/remotes/worktree policy is
`WORKFLOW_SAFETY_ONLY` and is verified by the release workflow, not by changing
the historical Phase 4C3 delta.

This classification is confirmed by the Phase 4C3 report, commit history, file
blame, and the later Phase 4D0 historical-release-lock report. It was not
inferred from a similar phase.

## 7. Authoritative Phase 4C3 transition

Immutable local Git history establishes:

| Role | Full SHA |
|---|---|
| Phase 4C3 parent | `a858cf83a7f9d979feecfecef32c42937b5e9eec` |
| Phase 4C3 endpoint | `816176f591909d505549e2818d6b8d6d75c67f25` |

The endpoint subject is `Priority 8 Phase 4C3 project canonical candidates`.
Independent `git diff --name-status --no-renames <parent> <endpoint>` output is
exactly:

```text
A editorial/priority-8-phase4c-canonical-candidates.json
A priority8_phase4c3_canonical_projection.py
A reports/priority-8-phase-4c3-canonical-projection.md
A tests/test_priority8_phase4c3_canonical_projection.py
```

## 8. Historical-contract correction

Only `tests/test_priority8_phase4c3_canonical_projection.py` was changed. It
now pins both full SHAs, obtains the exact four-row name/status delta with local
`git diff --name-status --no-renames`, rejects any non-two-field output, fails
closed when either object is unavailable, and requires tuple-for-tuple equality
with the actual Phase 4C3 delta.

The helper uses no network, checkout, current HEAD, current branch, or
worktree-mutating operation. No cleanup path, report path, later test path, or
growing allowlist was added to the Phase 4C3 snapshot.

## 9. Strictness and future-release compatibility

In-memory/mocked negative controls in the existing test method prove rejection
when:

- one historical path is removed;
- one unexpected path is added;
- one status changes from `A` to `M`;
- a historical diff row is malformed;
- a historical object is unavailable.

The focused check passes in the current later, dirty release worktree. A mocked
current-branch query is asserted unused. Because both endpoints are pinned,
the same check is independent of this cleanup commit, a later main
fast-forward, and later legitimate commits while those historical objects
remain available and unchanged.

The complete Phase 4C3 suite remains 46 methods and passes 46/46. No skip,
xfail, expected failure, subset, superset, branch exception, or current-release
special case was introduced.

## 10. Product, audio, and QA immutability

`content/verb-patterns.json` is unchanged with SHA-256
`66a02804b8ea1bb2b8a4ec7260855018db0e32f7a0623b78dc8b62fd58801ff1`.
It remains format version 2, pattern-data revision 3, with 98 lemmas, 129
meanings, 269 patterns, and 269 examples. There is no linguistic or content
change.

`verify_audio.py` reports 3,621 required phrases, 3,621 manifest entries,
3,621 MP3s, all 269 verb-pattern phrases covered, and zero missing or orphaned
audio. `audio-manifest.json`, every `audio/*.mp3`, and the QA CSV are unchanged.
The QA CSV remains 219 technical PASS and 219 human PENDING rows. No collision
was reported.

Release markers remain exactly:

```text
APP_VERSION = "8.13"
CACHE = "popolsku-v68"
AUDIO_CACHE = "popolsku-audio"
```

They were not bumped by this cleanup.

## 11. AI/model and code hygiene

A production/user-facing scan found no Claude, Codex, ChatGPT, OpenAI, or GPT
attribution and no `/Users/Kaj` dependency. Historical reports and tests remain
intact as evidence. Production HTML/JavaScript contains no `debugger` and no
unintended `console.log`, `console.debug`, or `console.trace`. The changed diff
contains no credential-shaped addition. The stale `3,402` service-worker
comment, Phase 3F-A startup wording, and generated-page v8.12 markers are gone.

## 12. Automated release gates

| Gate | Result |
|---|---|
| `python3 verify_audio.py` | PASS; 3,621 / 3,621 / 3,621; zero orphan |
| Phase 1 | 17/17 PASS |
| Phase 1 playback JXA | 25/25 PASS |
| Phase 1B | 1/1 PASS |
| Phase 4C3 canonical projection | 46/46 PASS |
| Phase 4C4C release freeze | 78/78 PASS |
| Phase 4D1 | 5/5 PASS |
| Phase 4E1 | 5/5 PASS |
| Phase 4F1 | 12/12 PASS |
| Migration JXA | 121/121 PASS |
| Audio fallback JXA | 585/585 PASS |
| `validate_priority8_staging.py` | PASS |
| `python3 build_pages.py --check` | PASS |
| Full `test_priority8_*.py` discovery | 606/606 PASS in 275.680 s |

The harmless macOS JXA connection-invalid diagnostic appeared after the
playback/migration/fallback PASS lines; all three commands exited zero.

## 13. Targeted browser product check

A temporary localhost server and the in-app browser verified:

- a generated grammar page renders v8.13;
- `/guide/` renders v8.13;
- `/guide/listening/` renders v8.13;
- a generated vocabulary page renders v8.13;
- none of those pages renders v8.12;
- Grammar → Verb Patterns displays `98 verbs · 269 patterns`;
- global search for `odpowiadać` returns the Verb Patterns result exactly once;
- global search for `radzić sobie` returns the Verb Patterns result exactly
  once;
- Phase 4E1 MP3 `/audio/0329b14c8894.mp3` returns HTTP 200;
- all observed product requests return 200 or cache-validating 304;
- zero product 404s and zero console warnings/errors were observed.

The temporary browser tab and localhost server were closed after testing.

## 14. Final release handoff

The authorized final scope is exactly 36 paths: the 32 generator outputs,
comment-only `sw.js`, comment-only `pp-verb-patterns.js`, this historical test
correction, and this report. The intended single local commit subject is
`Priority 8 final pre-release cleanup` with direct parent
`957554d88a3b59acf78f6cae131a3585538ae962`.

No push, deployment, merge, rebase, cherry-pick, or release is authorized. The
next release gate after a clean committed endpoint is an independent read-only
final cleanup verification.
