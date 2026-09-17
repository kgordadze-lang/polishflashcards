#!/usr/bin/env python3
"""Run maintained current regressions without historical test originals."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
JAVASCRIPT_TESTS = (
    "navigation.js",
    "responsive_closeout.js",
    "focus_scroll.js",
    "mobile_layout.js",
    "service_worker_cache.js",
    "offline_navigation.js",
    "audio_resilience.js",
    "choose_ui.js",
    "patterns_ui.js",
    "release_loader.js",
)


def _match(source: str, pattern: str, label: str) -> str:
    found = re.findall(pattern, source)
    if len(found) != 1:
        raise ValueError(f"{label}: expected one declaration, found {len(found)}")
    return found[0]


def current_markers(root: Path) -> dict[str, str]:
    index = (root / "index.html").read_text(encoding="utf-8")
    worker = (root / "sw.js").read_text(encoding="utf-8")
    manifest = json.loads(
        (root / "audio-manifest.json").read_text(encoding="utf-8"))
    return {
        "__CURRENT_APP_VERSION__": _match(
            index, r'\bconst\s+APP_VERSION\s*=\s*"([^"]+)"', "APP_VERSION"),
        "__CURRENT_SHELL_CACHE__": _match(
            worker, r'\bconst\s+CACHE\s*=\s*"([^"]+)"', "CACHE"),
        "__CURRENT_AUDIO_COUNT__": str(len(manifest["entries"])),
    }


def run_javascript(root: Path, markers: dict[str, str]) -> int:
    current_dir = root / "tests/current"
    with tempfile.TemporaryDirectory(prefix="current-js-tests-") as directory:
        temp_dir = Path(directory)
        for name in JAVASCRIPT_TESTS:
            source = (current_dir / name).read_text(encoding="utf-8")
            for token, value in markers.items():
                source = source.replace(token, value)
            leftovers = sorted(set(re.findall(r"__CURRENT_[A-Z_]+__", source)))
            if leftovers:
                print(f"FAIL: {name} has unresolved markers: {leftovers}", file=sys.stderr)
                return 1
            runnable = temp_dir / name
            runnable.write_text(source, encoding="utf-8")
            run = subprocess.run(
                ["osascript", "-l", "JavaScript", str(runnable)],
                cwd=root, text=True, capture_output=True)
            if run.stdout:
                print(run.stdout, end="" if run.stdout.endswith("\n") else "\n")
            if run.returncode:
                if run.stderr:
                    print(run.stderr, file=sys.stderr, end="")
                return run.returncode
            print(f"PASS: current JavaScript {name}")
    return 0


def run_python(root: Path) -> int:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    run = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests/current",
         "-p", "test_*.py", "-v"],
        cwd=root, env=environment)
    return run.returncode


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the maintained current Python and JavaScript regressions.")
    parser.add_argument(
        "--root", type=Path, default=ROOT,
        help="repository root (defaults to this script's repository)")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    root = parse_args(argv).root.resolve()
    try:
        markers = current_markers(root)
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: could not load current release markers: {exc}", file=sys.stderr)
        return 1
    print(
        "CURRENT REGRESSION SUITE: "
        f"APP_VERSION={markers['__CURRENT_APP_VERSION__']} "
        f"shell={markers['__CURRENT_SHELL_CACHE__']} "
        f"audio={markers['__CURRENT_AUDIO_COUNT__']}")
    result = run_javascript(root, markers)
    if result:
        return result
    result = run_python(root)
    if result:
        return result
    print("PASS: maintained current regression suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
