#!/usr/bin/env python3
"""Build and verify the allowlisted GitHub Pages artifact."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
DEPLOY_MANIFEST = Path("deployment/pages-runtime-allowlist.txt")
REPOSITORY_ONLY_MANIFEST = Path(
    "deployment/pages-repository-only-allowlist.txt")


class BoundaryError(RuntimeError):
    """Raised when the deployment boundary is invalid."""


@dataclass(frozen=True)
class Boundary:
    root: Path
    deploy: tuple[str, ...]
    repository_only: tuple[str, ...]
    tracked: frozenset[str]


@dataclass(frozen=True)
class ArtifactReport:
    deploy_count: int
    repository_only_count: int
    tracked_count: int
    artifact_count: int
    artifact_bytes: int
    checksum_mismatches: tuple[str, ...]
    unexpected_files: tuple[str, ...]
    missing_files: tuple[str, ...]
    repository_only_leaks: tuple[str, ...]
    symlink_count: int
    hidden_file_count: int


def _format_paths(paths: Iterable[str]) -> str:
    return ", ".join(sorted(paths))


def _validate_relative_path(value: str, manifest: Path, line: int) -> None:
    label = f"{manifest}:{line}"
    if not value:
        raise BoundaryError(f"{label}: blank paths are forbidden")
    if value != value.strip():
        raise BoundaryError(f"{label}: surrounding whitespace is forbidden")
    if "\\" in value:
        raise BoundaryError(f"{label}: paths must use '/' separators: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or value.startswith("/"):
        raise BoundaryError(f"{label}: absolute path is forbidden: {value!r}")
    if len(value) >= 2 and value[1] == ":":
        raise BoundaryError(f"{label}: absolute path is forbidden: {value!r}")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise BoundaryError(f"{label}: path traversal is forbidden: {value!r}")


def read_manifest(root: Path, relative_manifest: Path) -> tuple[str, ...]:
    manifest = root / relative_manifest
    try:
        source = manifest.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise BoundaryError(f"cannot read UTF-8 manifest {relative_manifest}: {exc}") from exc
    entries = source.splitlines()
    for line, value in enumerate(entries, 1):
        _validate_relative_path(value, relative_manifest, line)
    duplicates = sorted(
        value for value, count in Counter(entries).items() if count > 1)
    if duplicates:
        raise BoundaryError(
            f"{relative_manifest}: duplicate paths: {_format_paths(duplicates)}")
    if entries != sorted(entries):
        raise BoundaryError(f"{relative_manifest}: paths are not lexicographically sorted")
    return tuple(entries)


def tracked_files(root: Path) -> frozenset[str]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"], cwd=root, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        decoded = result.stdout.decode("utf-8", errors="strict")
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise BoundaryError(f"cannot enumerate tracked files with Git: {exc}") from exc
    paths = decoded.split("\0")
    if paths and paths[-1] == "":
        paths.pop()
    if any("\n" in path or "\r" in path for path in paths):
        raise BoundaryError("tracked paths containing newlines cannot be classified safely")
    return frozenset(paths)


def _validate_source(root: Path, relative: str) -> None:
    candidate = root / PurePosixPath(relative)
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if current.is_symlink():
            raise BoundaryError(f"symlink is forbidden: {relative}")
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise BoundaryError(f"missing or out-of-root source: {relative}") from exc
    if not resolved.is_file():
        raise BoundaryError(f"manifest path is not a regular file: {relative}")


def load_boundary(
    root: Path = ROOT,
    deploy_manifest: Path = DEPLOY_MANIFEST,
    repository_only_manifest: Path = REPOSITORY_ONLY_MANIFEST,
) -> Boundary:
    root = root.resolve(strict=True)
    deploy = read_manifest(root, deploy_manifest)
    repository_only = read_manifest(root, repository_only_manifest)
    tracked = tracked_files(root)
    deploy_set = set(deploy)
    repository_only_set = set(repository_only)

    overlap = deploy_set & repository_only_set
    unclassified = tracked - deploy_set - repository_only_set
    untracked_entries = (deploy_set | repository_only_set) - tracked
    if overlap:
        raise BoundaryError(f"paths in both manifests: {_format_paths(overlap)}")
    if unclassified:
        raise BoundaryError(f"tracked paths are unclassified: {_format_paths(unclassified)}")
    if untracked_entries:
        raise BoundaryError(
            f"manifest paths are not tracked: {_format_paths(untracked_entries)}")

    for relative in (*deploy, *repository_only):
        _validate_source(root, relative)
    hidden_deploy = [
        path for path in deploy
        if any(part.startswith(".") for part in PurePosixPath(path).parts)
    ]
    if hidden_deploy:
        raise BoundaryError(
            f"hidden DEPLOY paths require explicit review: {_format_paths(hidden_deploy)}")
    return Boundary(root, deploy, repository_only, tracked)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _artifact_inventory(output: Path) -> tuple[set[str], int, int, int]:
    files: set[str] = set()
    total_bytes = 0
    symlink_count = 0
    hidden_count = 0
    for path in output.rglob("*"):
        relative = path.relative_to(output).as_posix()
        if path.is_symlink():
            symlink_count += 1
            continue
        if path.is_file():
            files.add(relative)
            total_bytes += path.stat().st_size
            if any(part.startswith(".") for part in PurePosixPath(relative).parts):
                hidden_count += 1
    return files, total_bytes, symlink_count, hidden_count


def verify_artifact(boundary: Boundary, output: Path) -> ArtifactReport:
    output = output.resolve(strict=True)
    artifact_files, artifact_bytes, symlink_count, hidden_count = (
        _artifact_inventory(output))
    deploy_set = set(boundary.deploy)
    repository_only_set = set(boundary.repository_only)
    unexpected = tuple(sorted(artifact_files - deploy_set))
    missing = tuple(sorted(deploy_set - artifact_files))
    leaks = tuple(sorted(artifact_files & repository_only_set))
    mismatches = tuple(sorted(
        relative for relative in deploy_set & artifact_files
        if sha256(boundary.root / relative) != sha256(output / relative)
    ))
    report = ArtifactReport(
        deploy_count=len(boundary.deploy),
        repository_only_count=len(boundary.repository_only),
        tracked_count=len(boundary.tracked),
        artifact_count=len(artifact_files),
        artifact_bytes=artifact_bytes,
        checksum_mismatches=mismatches,
        unexpected_files=unexpected,
        missing_files=missing,
        repository_only_leaks=leaks,
        symlink_count=symlink_count,
        hidden_file_count=hidden_count,
    )
    errors: list[str] = []
    if unexpected:
        errors.append(f"unexpected artifact files: {_format_paths(unexpected)}")
    if missing:
        errors.append(f"missing artifact files: {_format_paths(missing)}")
    if leaks:
        errors.append(f"repository-only files leaked: {_format_paths(leaks)}")
    if mismatches:
        errors.append(f"checksum mismatches: {_format_paths(mismatches)}")
    if symlink_count:
        errors.append(f"artifact symlinks: {symlink_count}")
    if hidden_count:
        errors.append(f"hidden artifact files: {hidden_count}")
    if errors:
        raise BoundaryError("; ".join(errors))
    return report


def _prepare_output(root: Path, supplied: Path) -> Path:
    if not supplied.is_absolute():
        raise BoundaryError("--output must be an absolute path")
    if supplied.is_symlink():
        raise BoundaryError("--output must not be a symlink")
    output = supplied.resolve(strict=False)
    home = Path.home().resolve()
    anchor = Path(output.anchor)
    if output in (anchor, home, root) or output in root.parents or root in output.parents:
        raise BoundaryError(f"refusing dangerous artifact output path: {output}")
    if output.exists():
        raise BoundaryError(
            f"artifact output already exists; choose a fresh path: {output}")
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise BoundaryError(
            f"artifact output already exists; choose a fresh path: {output}") from exc
    except OSError as exc:
        raise BoundaryError(f"cannot create artifact output {output}: {exc}") from exc
    return output


def build_artifact(boundary: Boundary, supplied_output: Path) -> ArtifactReport:
    output = _prepare_output(boundary.root, supplied_output)
    for relative in boundary.deploy:
        destination = output / PurePosixPath(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(boundary.root / relative, destination)
    return verify_artifact(boundary, output)


def _print_partition(boundary: Boundary) -> None:
    print(f"deploy files: {len(boundary.deploy)}")
    print(f"repository-only files: {len(boundary.repository_only)}")
    print(f"total classified tracked files: {len(boundary.tracked)}")
    print("overlap: 0")
    print("unclassified: 0")


def _print_report(report: ArtifactReport) -> None:
    print(f"artifact files: {report.artifact_count}")
    print(f"artifact bytes: {report.artifact_bytes}")
    print(f"checksum mismatches: {len(report.checksum_mismatches)}")
    print(f"unexpected artifact files: {len(report.unexpected_files)}")
    print(f"missing artifact files: {len(report.missing_files)}")
    print(f"repository-only leaks: {len(report.repository_only_leaks)}")
    print(f"artifact symlinks: {report.symlink_count}")
    print(f"hidden artifact files: {report.hidden_file_count}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Pages partition and build its exact artifact.")
    parser.add_argument("--root", type=Path, default=ROOT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true",
                      help="validate only the two-way tracked-file partition")
    mode.add_argument("--output", type=Path,
                      help="absolute path to a fresh Pages artifact directory")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        boundary = load_boundary(args.root)
        _print_partition(boundary)
        if args.output is not None:
            report = build_artifact(boundary, args.output)
            _print_report(report)
    except BoundaryError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: GitHub Pages deployment boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
