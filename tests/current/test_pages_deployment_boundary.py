#!/usr/bin/env python3
"""Focused tests for the fail-closed GitHub Pages deployment boundary."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from build_pages_artifact import (  # noqa: E402
    BoundaryError,
    build_artifact,
    load_boundary,
    verify_artifact,
)


DEPLOY_MANIFEST = Path("deployment/deploy.txt")
REPOSITORY_ONLY_MANIFEST = Path("deployment/repository-only.txt")
DEPLOY_GUARD = (
    "github.event_name == 'workflow_dispatch' && "
    "github.ref == format('refs/heads/{0}', "
    "github.event.repository.default_branch)"
)


class PagesDeploymentGuardTests(unittest.TestCase):
    @staticmethod
    def guard_allows(event_name: str, ref: str, default_branch: str) -> bool:
        return (
            event_name == "workflow_dispatch"
            and ref == f"refs/heads/{default_branch}"
        )

    def test_workflow_uses_full_default_branch_ref_guard(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(
            encoding="utf-8")
        deploy_job = workflow.split("\n  deploy:\n", 1)[1]
        condition_block = deploy_job.split("    if: >-\n", 1)[1].split(
            "\n    needs:", 1)[0]
        condition = " ".join(
            line.strip() for line in condition_block.splitlines())
        self.assertEqual(condition, DEPLOY_GUARD)
        self.assertNotIn("github.ref_name ==", workflow)

    def test_workflow_dispatch_default_branch_is_allowed(self) -> None:
        self.assertTrue(self.guard_allows(
            "workflow_dispatch", "refs/heads/main", "main"))

    def test_workflow_dispatch_other_branch_is_denied(self) -> None:
        self.assertFalse(self.guard_allows(
            "workflow_dispatch", "refs/heads/release", "main"))

    def test_workflow_dispatch_same_named_tag_is_denied(self) -> None:
        self.assertFalse(self.guard_allows(
            "workflow_dispatch", "refs/tags/main", "main"))

    def test_push_default_branch_is_denied(self) -> None:
        self.assertFalse(self.guard_allows(
            "push", "refs/heads/main", "main"))

    def test_pull_request_is_denied(self) -> None:
        self.assertFalse(self.guard_allows(
            "pull_request", "refs/pull/17/merge", "main"))


class PagesDeploymentBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pages-boundary-")
        self.base = Path(self.temporary.name)
        self.root = self.base / "repository"
        self.output = self.base / "pages-artifact"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, relative: str, content: str = "content\n") -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def fixture(
        self,
        deploy: list[str] | None = None,
        repository_only: list[str] | None = None,
        extra_tracked: list[str] | None = None,
    ) -> None:
        deploy = ["index.html"] if deploy is None else deploy
        repository_only = ["tool.py"] if repository_only is None else repository_only
        extra_tracked = [] if extra_tracked is None else extra_tracked
        for relative in sorted(set(deploy + repository_only + extra_tracked)):
            if relative.startswith("/") or ".." in Path(relative).parts:
                continue
            self.write(relative)
        self.write(DEPLOY_MANIFEST.as_posix(), "\n".join(sorted(deploy)) + "\n")
        classified_repository_only = sorted(set(repository_only) | {
            DEPLOY_MANIFEST.as_posix(), REPOSITORY_ONLY_MANIFEST.as_posix()})
        self.write(
            REPOSITORY_ONLY_MANIFEST.as_posix(),
            "\n".join(classified_repository_only) + "\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)

    def boundary(self):
        return load_boundary(
            self.root, DEPLOY_MANIFEST, REPOSITORY_ONLY_MANIFEST)

    def test_fresh_output_directory_succeeds(self) -> None:
        self.fixture()
        boundary = self.boundary()
        report = build_artifact(boundary, self.output)
        self.assertEqual(report.artifact_count, 1)
        self.assertEqual(report.repository_only_count, 3)

    def test_existing_output_directory_is_rejected(self) -> None:
        self.fixture()
        self.output.mkdir()
        with self.assertRaisesRegex(BoundaryError, "already exists"):
            build_artifact(self.boundary(), self.output)

    def test_existing_output_contents_remain_byte_identical(self) -> None:
        self.fixture()
        self.output.mkdir()
        marker = self.output / "keep.bin"
        original = b"must remain untouched\x00\xff"
        marker.write_bytes(original)
        with self.assertRaisesRegex(BoundaryError, "already exists"):
            build_artifact(self.boundary(), self.output)
        self.assertEqual(marker.read_bytes(), original)
        self.assertEqual([path.name for path in self.output.iterdir()], ["keep.bin"])

    def test_existing_output_file_is_rejected_and_untouched(self) -> None:
        self.fixture()
        original = b"existing file\x00"
        self.output.write_bytes(original)
        with self.assertRaisesRegex(BoundaryError, "already exists"):
            build_artifact(self.boundary(), self.output)
        self.assertEqual(self.output.read_bytes(), original)

    def test_repository_root_as_output_is_rejected(self) -> None:
        self.fixture()
        with self.assertRaisesRegex(BoundaryError, "dangerous"):
            build_artifact(self.boundary(), self.root)

    def test_output_inside_repository_is_rejected(self) -> None:
        self.fixture()
        with self.assertRaisesRegex(BoundaryError, "dangerous"):
            build_artifact(self.boundary(), self.root / "artifact-output")

    def test_relative_output_path_is_rejected(self) -> None:
        self.fixture()
        with self.assertRaisesRegex(BoundaryError, "absolute path"):
            build_artifact(self.boundary(), Path("relative-artifact"))

    def test_filesystem_root_as_output_is_rejected(self) -> None:
        self.fixture()
        with self.assertRaisesRegex(BoundaryError, "dangerous"):
            build_artifact(self.boundary(), Path(self.base.anchor))

    def test_home_directory_as_output_is_rejected(self) -> None:
        self.fixture()
        with self.assertRaisesRegex(BoundaryError, "dangerous"):
            build_artifact(self.boundary(), Path.home())

    def test_symlink_output_is_rejected_and_target_is_untouched(self) -> None:
        self.fixture()
        target = self.base / "existing-target"
        target.mkdir()
        marker = target / "keep.txt"
        marker.write_bytes(b"keep")
        link = self.base / "artifact-link"
        try:
            os.symlink(target, link, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        with self.assertRaisesRegex(BoundaryError, "must not be a symlink"):
            build_artifact(self.boundary(), link)
        self.assertEqual(marker.read_bytes(), b"keep")

    def test_overlap_fails(self) -> None:
        self.fixture(deploy=["index.html", "tool.py"])
        with self.assertRaisesRegex(BoundaryError, "both manifests"):
            self.boundary()

    def test_unclassified_tracked_file_fails(self) -> None:
        self.fixture(extra_tracked=["forgotten.txt"])
        with self.assertRaisesRegex(BoundaryError, "unclassified"):
            self.boundary()

    def test_duplicate_manifest_entry_fails(self) -> None:
        self.fixture()
        self.write(DEPLOY_MANIFEST.as_posix(), "index.html\nindex.html\n")
        with self.assertRaisesRegex(BoundaryError, "duplicate"):
            self.boundary()

    def test_missing_deploy_source_fails(self) -> None:
        self.fixture()
        (self.root / "index.html").unlink()
        with self.assertRaisesRegex(BoundaryError, "missing"):
            self.boundary()

    def test_path_traversal_fails(self) -> None:
        self.fixture(deploy=["../escape.txt"])
        with self.assertRaisesRegex(BoundaryError, "path traversal"):
            self.boundary()

    def test_absolute_path_fails(self) -> None:
        self.fixture(deploy=["/tmp/escape.txt"])
        with self.assertRaisesRegex(BoundaryError, "absolute path"):
            self.boundary()

    def test_symlink_is_rejected(self) -> None:
        self.fixture(deploy=["target.txt"])
        link = self.root / "link.txt"
        try:
            os.symlink("target.txt", link)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.write(DEPLOY_MANIFEST.as_posix(), "link.txt\ntarget.txt\n")
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        with self.assertRaisesRegex(BoundaryError, "symlink"):
            self.boundary()

    def test_unexpected_artifact_file_fails(self) -> None:
        self.fixture()
        boundary = self.boundary()
        build_artifact(boundary, self.output)
        (self.output / "unexpected.txt").write_text("no\n", encoding="utf-8")
        with self.assertRaisesRegex(BoundaryError, "unexpected artifact"):
            verify_artifact(boundary, self.output)

    def test_missing_artifact_file_fails(self) -> None:
        self.fixture()
        boundary = self.boundary()
        build_artifact(boundary, self.output)
        (self.output / "index.html").unlink()
        with self.assertRaisesRegex(BoundaryError, "missing artifact"):
            verify_artifact(boundary, self.output)

    def test_byte_mismatch_fails(self) -> None:
        self.fixture()
        boundary = self.boundary()
        build_artifact(boundary, self.output)
        (self.output / "index.html").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(BoundaryError, "checksum mismatch"):
            verify_artifact(boundary, self.output)

    def test_repository_only_file_cannot_appear_in_artifact(self) -> None:
        self.fixture()
        boundary = self.boundary()
        build_artifact(boundary, self.output)
        shutil.copyfile(self.root / "tool.py", self.output / "tool.py")
        with self.assertRaisesRegex(BoundaryError, "repository-only files leaked"):
            verify_artifact(boundary, self.output)


if __name__ == "__main__":
    unittest.main()
