#!/usr/bin/env python3
"""Validate current release contracts without historical governance evidence.

This command owns only checks that are not already the responsibility of
validate_content.py, verify_audio.py, or build_pages.py --check. Those delegated
validators remain separate entries in the current release gate.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Sequence

from verb_patterns_runtime_validator import runtime_counts, validate_runtime


ROOT = Path(__file__).resolve().parent


def _one_match(
        source: str, pattern: str, label: str, issues: list[str]) -> str | None:
    matches = re.findall(pattern, source)
    if len(matches) != 1:
        issues.append(f"{label}: expected one declaration, found {len(matches)}")
        return None
    return matches[0]


def validate_release(root: Path = ROOT) -> tuple[list[str], dict[str, object]]:
    """Return current-only validation issues and an operator-facing summary."""
    issues: list[str] = []
    summary: dict[str, object] = {}

    try:
        index = (root / "index.html").read_text(encoding="utf-8")
        worker = (root / "sw.js").read_text(encoding="utf-8")
        migration = (root / "pp-migrate.js").read_text(encoding="utf-8")
        runtime = json.loads(
            (root / "content/verb-patterns.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"current canonical input could not be loaded: {exc}"], summary

    app_version = _one_match(
        index, r'\bconst\s+APP_VERSION\s*=\s*"([^"]+)"\s*;',
        "index.html APP_VERSION", issues)
    shell_cache = _one_match(
        worker, r'\bconst\s+CACHE\s*=\s*"([^"]+)"\s*;',
        "sw.js CACHE", issues)
    audio_cache = _one_match(
        worker, r'\bconst\s+AUDIO_CACHE\s*=\s*"([^"]+)"\s*;',
        "sw.js AUDIO_CACHE", issues)
    schema_version = _one_match(
        migration, r'\bSCHEMA_VERSION\s*=\s*(\d+)\s*;',
        "pp-migrate.js SCHEMA_VERSION", issues)
    content_revision = _one_match(
        migration, r'\bCONTENT_MIGRATION_REVISION\s*=\s*(\d+)\s*;',
        "pp-migrate.js CONTENT_MIGRATION_REVISION", issues)

    if app_version is not None and not re.fullmatch(r"[1-9]\d*\.\d+", app_version):
        issues.append(
            "index.html APP_VERSION must be a positive major.minor release marker")
    if shell_cache is not None and not re.fullmatch(r"popolsku-v[1-9]\d*", shell_cache):
        issues.append("sw.js CACHE must use the versioned popolsku-vN namespace")
    if audio_cache is not None and audio_cache != "popolsku-audio":
        issues.append("sw.js AUDIO_CACHE must remain the stable popolsku-audio namespace")
    if shell_cache is not None and shell_cache == audio_cache:
        issues.append("shell and audio caches must use separate namespaces")
    for label, value in (
            ("SCHEMA_VERSION", schema_version),
            ("CONTENT_MIGRATION_REVISION", content_revision)):
        if value is not None and int(value) < 1:
            issues.append(f"pp-migrate.js {label} must be a positive integer")

    runtime_issues = validate_runtime(runtime)
    issues.extend(f"Verb Patterns: {issue}" for issue in runtime_issues)

    summary.update({
        "appVersion": app_version,
        "shellCache": shell_cache,
        "audioCache": audio_cache,
        "schemaVersion": int(schema_version) if schema_version else None,
        "contentMigrationRevision": (
            int(content_revision) if content_revision else None),
        "verbPatterns": runtime_counts(runtime),
    })
    return issues, summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate maintained current release contracts.")
    parser.add_argument(
        "--root", type=Path, default=ROOT,
        help="repository root (defaults to the validator's directory)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    issues, summary = validate_release(args.root.resolve())
    if issues:
        print(f"FAIL: {len(issues)} current release issue(s)", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    counts = summary["verbPatterns"]
    print("PASS: current release contracts are valid")
    print(
        "  release: "
        f"APP_VERSION={summary['appVersion']} "
        f"shell={summary['shellCache']} audio={summary['audioCache']}")
    print(
        "  storage: "
        f"schema={summary['schemaVersion']} "
        f"contentMigration={summary['contentMigrationRevision']}")
    print(
        "  Verb Patterns: "
        + " ".join(f"{key}={value}" for key, value in counts.items()))
    print("  delegated: validate_content.py owns product content and forward-baseline checks")
    print("  delegated: verify_audio.py owns required/manifest/disk audio parity")
    print("  delegated: build_pages.py --check owns generated-page freshness")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
