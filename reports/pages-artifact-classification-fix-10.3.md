# Release 10.3 Pages artifact classification correction

## Starting state and failure

- Branch: `fix/pages-artifact-classification-10.3`.
- Starting HEAD: `df1cd78fd5e94fa4aa3ce05d846d4ac9d23f2c4c`.
- Starting tree: `8bad848f3e04dc7ab25a27eabaf1a9a1e664d5d3`.
- The starting worktree was clean, `git remote -v` was empty, and `push.default` was `nothing`.
- The push-triggered **Verify and stage GitHub Pages** workflow failed in **Build exact allowlisted artifact** on `python build_pages_artifact.py --output "$PAGES_ARTIFACT"`. Its exact error was: `FAIL: tracked paths are unclassified: reports/card-flip-control-layout-fix.md, reports/card-flip-control-layout-release-10.3.md, tests/current/test_card_flip_layout.py`. The maintained product gate passed and deployment was skipped.

## Classification correction

`build_pages_artifact.py` reads two lexicographically sorted manifests of exact repository-relative paths. The deploy manifest names every public file; the repository-only manifest names every tracked file excluded from the artifact. Their disjoint union must equal `git ls-files`. A missing, overlapping, untracked, duplicate, hidden deploy, or symlink path fails validation. Artifact verification compares the exact output file set and SHA-256 checksums.

The three new release files were tracked but absent from both manifests. The sole classification change adds these exact repository-only entries:

- `reports/card-flip-control-layout-fix.md`
- `reports/card-flip-control-layout-release-10.3.md`
- `tests/current/test_card_flip_layout.py`

This report, `reports/pages-artifact-classification-fix-10.3.md`, is also newly tracked and explicitly classified as repository-only. None of these four paths is in the deploy manifest or the built artifact. No wildcard or prefix rule was introduced; a newly tracked path still fails closed.

Changed paths in the corrective commit:

- `deployment/pages-repository-only-allowlist.txt`: four exact sorted entries.
- `tests/current/test_pages_deployment_boundary.py`: focused assertion that the three release paths are tracked, repository-only, and absent from the deploy set.
- `reports/pages-artifact-classification-fix-10.3.md`: this repository-only record.

## Verification

The complete intended worktree, including this staged report, passed `build_pages_artifact.py --check` and the exact local equivalent of CI's `--output` command. The temporary output was removed after verification.

| Boundary result | Count |
| --- | ---: |
| Classified tracked files | 3,762 |
| Deploy manifest and artifact files | 3,684 |
| Repository-only files | 78 |
| Unclassified tracked files | 0 |
| Repository-only leaks | 0 |
| Unexpected artifact files | 0 |
| Missing artifact files | 0 |
| Checksum mismatches | 0 |
| Artifact symlinks | 0 |
| Hidden artifact files | 0 |

Artifact size is 57,436,780 bytes. Its deterministic path-and-content digest is `a6488cae882169547768dd22fac590d489db34fa371bcdee07d214c7d00bfb80`, identical to the pre-change digest of all 3,684 intended release 10.3 deploy paths. Builder checksum verification additionally found that every artifact file matches its worktree source. Therefore the reviewed `index.html`, `sw.js`, generated pages, sitemap, and all other public bytes are unchanged from starting HEAD.

Regression and gate results:

- `tests/current/test_pages_deployment_boundary.py`: 37 passed, including explicit classification of the three release paths, rejection of a newly tracked unclassified file, rejection of repository-only leaks, and inclusion of legitimate deploy files.
- `tests/current/test_card_flip_layout.py`: 3 passed.
- `tests/current/run_current_tests.py`: 117 Python tests and all 10 current JavaScript regressions passed.
- `validate_content.py`: passed; 1,675 IDs and forward baseline intact.
- `verify_audio.py`: passed; 3,621 required phrases, manifest entries, and MP3s match.
- `verb_patterns_runtime_validator.py`: passed.
- `validate_current_release.py`: passed; version, cache, schema, migration, and runtime contracts intact.
- `build_pages.py --check`: passed; 23 grammar pages, 6 vocabulary pages, guide hub, and 32 sitemap URLs current.
- `git diff --check` and staged diff check: passed.

## Release protection and repository handling

The pre-change deterministic digest of all 3,684 deploy paths, hashing each UTF-8 path, a NUL byte, its eight-byte big-endian length, and its contents in manifest order, was `a6488cae882169547768dd22fac590d489db34fa371bcdee07d214c7d00bfb80` (57,436,780 total bytes). The same digest will be compared with the finished artifact.

`APP_VERSION` remains `10.3`, shell cache remains `popolsku-v76`, and `AUDIO_CACHE` remains `popolsku-audio`. No generated page, sitemap, card implementation, or public content is edited. This checkout has zero remotes. Nothing is pushed or deployed. The production repository is never accessed.

The final commit and tree IDs are read from Git metadata after the commit and recorded in the final task response. Embedding either ID in this committed report would change the report blob and thus change both IDs.
