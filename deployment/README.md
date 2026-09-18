# GitHub Pages deployment boundary

GitHub Pages must serve only files explicitly approved as learner-facing runtime material. The repository contains additional maintained build, validation, test, documentation, and deployment files that must remain public in Git without becoming website resources.

`pages-runtime-allowlist.txt` is the complete `DEPLOY` set. Every listed file is copied byte-for-byte into the Pages artifact.

`pages-repository-only-allowlist.txt` is the complete `REPOSITORY_ONLY` set. These files remain tracked but must never enter the artifact. This includes the manifests, builder, tests, workflow, developer tools, and `CNAME`.

Together the manifests must equal `git ls-files`, with no overlap. A newly tracked file therefore fails validation until a maintainer deliberately adds it to exactly one sorted manifest.

## Local verification

Validate the partition without building:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 build_pages_artifact.py --check
```

Build and fully verify an artifact outside the repository:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 build_pages_artifact.py \
  --output /tmp/popolsku-pages-artifact
```

The builder requires the explicit output directory not to exist, creates it fresh, copies only `DEPLOY` files, compares every SHA-256, rejects symlinks and hidden deploy files, and proves the resulting file set is exact. It never empties or replaces an existing output path.

Run the complete maintained product gate before building:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 validate_content.py
PYTHONDONTWRITEBYTECODE=1 python3 verify_audio.py
PYTHONDONTWRITEBYTECODE=1 python3 validate_current_release.py
PYTHONDONTWRITEBYTECODE=1 python3 build_pages.py --check
PYTHONDONTWRITEBYTECODE=1 python3 tests/current/run_current_tests.py
```

## Classifying a new tracked file

Decide whether the path is required by the learner-facing web/PWA runtime. Add it to `pages-runtime-allowlist.txt` only when it is intentionally public and required at runtime. Otherwise add it to `pages-repository-only-allowlist.txt`. Keep one repository-relative path per line, with no globs, comments, duplicates, or traversal, and sort the complete file lexicographically.

`CNAME` is repository-only deployment metadata. With a GitHub Actions Pages source, the custom-domain setting in GitHub Pages is the source of truth; copying `CNAME` does not configure or remove that setting.

## Live activation remains separate

The workflow builds and verifies on pushes and pull requests, but its deploy job is available only for a manual run from the repository's default branch. This implementation does not change GitHub Pages settings, the custom domain, Cloudflare DNS, or the live site.

As defense in depth, checkout does not persist GitHub credentials because the build job does not perform authenticated Git operations.

During a separately reviewed activation, change the Pages publishing source to GitHub Actions, verify that GitHub Settings → Pages still contains the custom domain before and after the first deployment, and leave Cloudflare DNS managed separately.
