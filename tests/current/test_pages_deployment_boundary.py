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

    def test_valid_partition_passes(self) -> None:
        self.fixture()
        boundary = self.boundary()
        report = build_artifact(boundary, self.output)
        self.assertEqual(report.artifact_count, 1)
        self.assertEqual(report.repository_only_count, 3)

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
