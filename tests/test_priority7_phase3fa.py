"""Priority 7 Phase 3F-A release-readiness and deployment-isolation guards.

These tests rehearse structure only. They never project the real corpus, create
release authority, activate startup loading, or modify the production worker.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import build_pages
from priority7_tooling import PRIVATE_RUNTIME_KEYS, ValidationContext, validate_runtime

# Phase 4F-E1 normalisation.  Imported by path, with no dependency on any
# other import in this module, so it resolves identically under
# `python3 -m unittest`, a direct script run, and the importlib loading
# the later closure suites use.
import os.path as _e1_os_path
import sys as _e1_sys

_E1_DIR = _e1_os_path.dirname(_e1_os_path.abspath(__file__))
if _E1_DIR not in _e1_sys.path:
    _e1_sys.path.insert(0, _E1_DIR)

import priority7_phase4fe1_normalizer as E1
import priority7_phase4ff2_normalizer as F2
import priority7_phase4fh2_normalizer as H2
import priority7_phase4fh21_normalizer as H21


ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# Phase 4F-I1 normalisation, shared by every historical Priority 7 suite.
#
# Phase 4F-I1 activated the Priority 7 release as one atomic bundle: the
# official runtime document appeared at content/verb-patterns.json, index.html
# gained the single production loader call and APP_VERSION 8.10 -> 8.11, sw.js
# advanced popolsku-v65 -> v66 and learned the runtime's required-precache
# entry and its network-first classification, and the generator-owned pages
# were regenerated because their footer stamps APP_VERSION.
#
# The claims restated through this helper were true statements about the tiers
# that had run when this phase closed.  I1 legitimately supersedes them, so
# they are now made over the bundle with the I1 layer removed -- the same
# phase-aware repair the E1/F2/H2/H2.1/H3 layers already use.  The normaliser
# is all-or-nothing: it refuses any tree in which the runtime, the shell and
# the worker did not move together, or in which the runtime bytes are not the
# pinned I1 release, and it hides nothing beyond its own pinned strings.
#
# Imported by path, with no dependency on any other import in this module.
# ---------------------------------------------------------------------------
import os.path as _i1_os_path
import sys as _i1_sys

_I1_DIR = _i1_os_path.dirname(_i1_os_path.abspath(__file__))
if _I1_DIR not in _i1_sys.path:
    _i1_sys.path.insert(0, _I1_DIR)

import priority7_phase4fi1_normalizer as I1


def i1_bundle(root=ROOT):
    """The validated Phase 4F-I1 transition for this tree, or its absence."""
    root = Path(root)
    runtime = root / I1.PHASE_4FI1_RUNTIME_PATH
    return I1.bundle(
        index_text=(root / "index.html").read_text(encoding="utf-8"),
        worker_text=(root / "sw.js").read_text(encoding="utf-8"),
        runtime_bytes=runtime.read_bytes() if runtime.is_file() else None)


def pre_i1(path, root=ROOT):
    """``path`` as it stood before Phase 4F-I1 activated the release."""
    return i1_bundle(root).without_activation(path)


def i1_shipping_text(path, root=ROOT):
    """``path``'s text with the Phase 4F-I1 release layer removed.

    Ordinary text for every path I1 did not edit, so a loop over shipping
    sentinels can use it unconditionally.  It composes with the older layer
    helpers: the shell carries the I1 layer on top of the H3 wording layer, so
    a caller strips I1 here and H3 afterwards, exactly as the corpus claims
    strip H2.1 then H2 then F2 then E1.
    """
    if path in I1.PHASE_4FI1_SHIPPING_PATHS:
        return pre_i1(path, root)
    return (Path(root) / path).read_text(encoding="utf-8")
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "priority7"
FIXTURE = FIXTURE_DIR / "release-runtime-fixture.json"
CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT = ROOT / "editorial" / "priority-7-authoring-context.json"
PUBLIC_RUNTIME = ROOT / "content" / "verb-patterns.json"

RUNTIME_REPOSITORY_PATH = "content/verb-patterns.json"
RELEASE_COMPONENT_PATHS = (
    "index.html", "sw.js", "pp-verb-patterns.js", RUNTIME_REPOSITORY_PATH)

def i1_is_generated_output(path):
    """True for the generator-owned outputs Phase 4F-I1 regenerated.

    I1 advances APP_VERSION, which the page generator stamps into every
    generated footer, so ``build_pages.py`` rewrites the 31 pages and the
    sitemap.  They are regenerated, never hand-edited, and each is admitted
    only by its own pinned delta -- one footer version stamp per page, and
    ``<lastmod>`` values alone in the sitemap.
    """
    return (path in I1.PHASE_4FI1_GENERATED_PAGES
            or path == I1.PHASE_4FI1_SITEMAP_PATH)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(*arguments: str, root: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments], cwd=root, capture_output=True, text=True, check=False)


def strip_javascript_comments(source: str) -> str:
    source = re.sub(r"/\*[\s\S]*?\*/", "", source)
    return re.sub(r"^\s*//.*$", "", source, flags=re.M)


def extract_app_version(index: str) -> tuple[int, ...]:
    match = re.search(r'APP_VERSION\s*=\s*["\']([0-9]+(?:\.[0-9]+)*)["\']', index)
    if not match:
        raise ValueError("APP_VERSION is missing or non-numeric")
    return tuple(int(part) for part in match.group(1).split("."))


def extract_shell_generation(worker: str) -> int:
    match = re.search(r'\bCACHE\s*=\s*["\']popolsku-v([0-9]+)["\']', worker)
    if not match:
        raise ValueError("numbered popolsku shell cache is missing")
    return int(match.group(1))


def extract_required_assets(worker: str) -> set[str]:
    match = re.search(r"\bREQUIRED_ASSETS\s*=\s*\[(.*?)\]\s*;", worker, re.S)
    if not match:
        return set()
    return set(re.findall(r'["\']([^"\']+)["\']', match.group(1)))


def release_bundle_errors(
        index: str,
        worker: str,
        loader: str,
        runtime: object | None,
        previous_index: str | None = None,
        previous_worker: str | None = None,
) -> list[str]:
    """Return semantic errors for an active/candidate Priority 7 release.

    A helper may exist before release, including in the SW inventory. Release
    intent starts only when a runtime file/path or loader call appears.
    """
    index_code = strip_javascript_comments(index)
    worker_code = strip_javascript_comments(worker)
    call_exists = bool(re.search(r"\bloadRuntimeDocument\s*\(", index_code))
    runtime_named = RUNTIME_REPOSITORY_PATH in index_code
    release_intent = (
        call_exists or runtime_named or runtime is not None
        or RUNTIME_REPOSITORY_PATH in worker_code
    )
    if not release_intent:
        return []

    errors: list[str] = []
    if not call_exists:
        errors.append("loader activation missing")
    if not runtime_named:
        errors.append("runtime path missing from application")

    if runtime is None:
        errors.append("public runtime missing")
    else:
        validation_errors = validate_runtime(runtime, ValidationContext())
        if validation_errors:
            errors.append("public runtime invalid")
        loader_format = re.search(r"\bFORMAT_VERSION\s*=\s*([0-9]+)", loader)
        runtime_format = runtime.get("formatVersion") if isinstance(runtime, dict) else None
        if not loader_format or runtime_format != int(loader_format.group(1)):
            errors.append("loader/runtime format mismatch")

    required = extract_required_assets(worker)
    if "./pp-verb-patterns.js" not in required:
        errors.append("helper missing from required precache")
    if "./content/verb-patterns.json" not in required:
        errors.append("runtime missing from required precache")

    static_is_derived = re.search(
        r"\bSTATIC_ASSET_PATHS\s*=\s*REQUIRED_ASSETS\s*\.\s*concat\s*"
        r"\(\s*OPTIONAL_ASSETS\s*\)", worker_code)
    static_uses_cache_first = re.search(
        r'''category\s*===\s*["']static["'][\s\S]{0,180}?\bcacheFirst\s*\(''',
        worker_code,
    )
    if not static_is_derived or not static_uses_cache_first:
        errors.append("required static inventory is not cache-first")

    if previous_index is not None and previous_worker is not None:
        try:
            if extract_app_version(index) <= extract_app_version(previous_index):
                errors.append("APP_VERSION did not advance")
        except ValueError:
            errors.append("APP_VERSION is not comparable")
        try:
            if extract_shell_generation(worker) <= extract_shell_generation(previous_worker):
                errors.append("shell cache generation did not advance")
        except ValueError:
            errors.append("shell cache generation is not comparable")
    return errors


def bytes_at(repository: Path, reference: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{reference}:{path}"], cwd=repository,
        capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


def current_bytes(repository: Path, path: str) -> bytes | None:
    candidate = repository / path
    return candidate.read_bytes() if candidate.is_file() else None


def previous_release_reference(repository: Path = ROOT) -> str | None:
    """Select the immediately preceding state only for a release component change.

    A working candidate compares with HEAD. A clean HEAD that itself changed a
    release component compares with HEAD^. Later unrelated clean commits impose
    no spurious version bump.
    """
    inside = git("rev-parse", "--is-inside-work-tree", root=repository)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return None
    head = git("rev-parse", "--verify", "HEAD", root=repository)
    if head.returncode != 0:
        return None
    if any(current_bytes(repository, path) != bytes_at(repository, "HEAD", path)
           for path in RELEASE_COMPONENT_PATHS):
        return "HEAD"
    parent = git("rev-parse", "--verify", "HEAD^", root=repository)
    if parent.returncode != 0:
        return None
    changed = git(
        "diff", "--quiet", "HEAD^", "HEAD", "--", *RELEASE_COMPONENT_PATHS,
        root=repository)
    return "HEAD^" if changed.returncode == 1 else None


def walk_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


class SyntheticPublicRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(read(FIXTURE))

    def test_fixture_is_bare_closed_public_shape_and_tooling_valid(self):
        self.assertEqual(
            {"formatVersion", "patternDataRevision", "lemmas"},
            set(self.fixture),
        )
        self.assertEqual(1, self.fixture["formatVersion"])
        self.assertEqual(424242, self.fixture["patternDataRevision"])
        self.assertEqual([], validate_runtime(self.fixture, ValidationContext()))

    def test_fixture_is_unmistakably_synthetic_non_polish_and_small(self):
        lemmas = [lemma["canonicalLemma"] for lemma in self.fixture["lemmas"]]
        self.assertEqual(["quuxify", "zorbulate"], lemmas)
        self.assertEqual(2, len(lemmas))
        self.assertTrue(all(re.fullmatch(r"[a-z]+", lemma) for lemma in lemmas))
        payload = json.dumps(self.fixture, ensure_ascii=False)
        self.assertIn("TEST-ONLY", payload)
        self.assertNotIn("SYNTHETIC-NONRELEASE", payload)

        real = json.loads(read(CORPUS))
        real_lemmas = {lemma["canonicalLemma"] for lemma in real["lemmas"]}
        real_patterns = {
            pattern["id"]
            for lemma in real["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        }
        fixture_payload = read(FIXTURE)
        self.assertTrue(real_lemmas.isdisjoint(lemmas))
        self.assertFalse(any(value in fixture_payload for value in real_patterns))

    def test_fixture_has_no_private_or_authority_envelope_at_any_depth(self):
        present = {
            key
            for record in walk_objects(self.fixture)
            for key in record
            if key in PRIVATE_RUNTIME_KEYS
        }
        self.assertEqual(set(), present)
        for forbidden in (
            "releaseAuthorized", "runtimeProjection", "reviewState",
            "reviewEvents", "reviewerRef", "authorRef", "sourceRegistry",
            "reviewerRegistry", "authorRegistry", "editorialNotes",
        ):
            with self.subTest(key=forbidden):
                self.assertNotIn(forbidden, read(FIXTURE))

    def test_fixture_has_zero_activity_and_audio_eligibility(self):
        patterns = [
            pattern
            for lemma in self.fixture["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        self.assertEqual(2, len(patterns))
        self.assertEqual(0, sum(len(pattern["activityEligibility"])
                                for pattern in patterns))
        self.assertEqual(
            0,
            sum(
                example["audioEligible"] is True
                for pattern in patterns
                for example in pattern.get("examples", [])
            ),
        )

    def test_explicit_candidate_validation_command_accepts_only_the_fixture_path(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "priority7_tooling.py"),
                "validate-runtime",
                str(FIXTURE),
                "--repository-root",
                str(ROOT),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("runtime projection: valid", result.stdout)


class DormantLoaderAndIsolationTests(unittest.TestCase):
    def test_fixture_inventory_is_exact_and_test_only(self):
        present = sorted(
            str(path.relative_to(FIXTURE_DIR))
            for path in FIXTURE_DIR.rglob("*")
            if path.is_file()
        )
        # EXTENDED by Priority 7 Phase 5-A, not relaxed: that phase adds the
        # synthetic private editorial fixture it freezes and the test-only JXA
        # harness that feeds the resulting projection to the shipping loader.
        self.assertEqual(
            [
                "exercise-fixture.json",
                "phase5a-loader-harness.js",
                "release-runtime-fixture.json",
                "runtime-fixture.json",
                "synthetic-release-editorial.json",
            ],
            present,
        )
        self.assertFalse((ROOT / "release-runtime-fixture.json").exists())
        for directory in ("content", "grammar", "vocabulary", "guide"):
            self.assertFalse((ROOT / directory / FIXTURE.name).exists())

    def test_public_surfaces_never_reference_the_fixture(self):
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        public_sources = {
            "index.html": read(ROOT / "index.html"),
            "sw.js": read(ROOT / "sw.js"),
            "manifest.json": read(ROOT / "manifest.json"),
            "sitemap.xml": read(ROOT / "sitemap.xml"),
            **outputs,
        }
        for name, source in public_sources.items():
            with self.subTest(surface=name):
                self.assertNotIn("release-runtime-fixture.json", source)
                self.assertNotIn("tests/fixtures/priority7", source)
                self.assertNotIn("quuxify", source)
                self.assertNotIn("zorbulate", source)

    def test_ordinary_startup_and_every_shipping_helper_keep_transport_dormant(self):
        """Restated over the pre-Phase-4F-I1 shell and worker.

        Phase 4F-I1 is the atomic release that activates the transport, and it
        is the only phase entitled to.  With its pinned layer removed the
        dormancy claim still holds in full, so a SECOND activation, a different
        runtime URL, a preview or fixture URL, or a transport added anywhere
        else -- including in a generated page or another shipping helper, none
        of which the I1 layer touches at all -- is still reported here.
        """
        index = pre_i1("index.html")
        self.assertEqual(2, index.count("fetch("))
        self.assertEqual(1, index.count('fetch("audio-manifest.json"'))
        self.assertEqual(1, index.count('fetch("./", { method:"HEAD"'))
        scripts = re.findall(r'<script src="([^"]+)"', index)
        shipping_sources = {"index.html": index, "sw.js": pre_i1("sw.js")}
        shipping_sources.update({path: read(ROOT / path) for path in scripts})
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        shipping_sources.update(outputs)
        for name, source in shipping_sources.items():
            executable = strip_javascript_comments(source)
            if name == "pp-verb-patterns.js":
                executable = re.sub(
                    r"\bfunction\s+loadRuntimeDocument\s*\(",
                    "function __dormantLoaderDefinition(", executable,
                )
            with self.subTest(source=name):
                self.assertNotRegex(executable, r"\bloadRuntimeDocument\s*\(")
                self.assertNotIn(RUNTIME_REPOSITORY_PATH, executable)

    def test_transport_is_dormant_dependency_injected_and_non_persistent(self):
        loader = read(ROOT / "pp-verb-patterns.js")
        self.assertEqual(1, loader.count("function loadRuntimeDocument(request, url)"))
        self.assertEqual(1, loader.count('request(url, { cache: "no-store" })'))
        self.assertEqual(1, loader.count("loadRuntimeDocument: loadRuntimeDocument"))
        self.assertNotIn("fetch(", loader)
        self.assertNotIn("content/verb-patterns.json", loader)
        for forbidden in (
            "localStorage", "sessionStorage", "indexedDB", "setInterval",
            "document.getElementById", "innerHTML", "XMLHttpRequest",
        ):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, loader)

    def test_future_activation_is_guarded_as_one_atomic_dependency_bundle(self):
        """The dormant path may not be activated one file at a time."""
        index = read(ROOT / "index.html")
        worker = read(ROOT / "sw.js")
        loader = read(ROOT / "pp-verb-patterns.js")
        runtime = json.loads(read(PUBLIC_RUNTIME)) if PUBLIC_RUNTIME.is_file() else None
        previous_ref = previous_release_reference()
        release_intent = (
            runtime is not None
            or bool(re.search(r"\bloadRuntimeDocument\s*\(",
                              strip_javascript_comments(index)))
            or RUNTIME_REPOSITORY_PATH in strip_javascript_comments(index)
            or RUNTIME_REPOSITORY_PATH in strip_javascript_comments(worker)
        )
        if release_intent and previous_ref is None:
            self.skipTest("Priority 7 release comparison requires usable Git history")
        previous_index = (
            bytes_at(ROOT, previous_ref, "index.html").decode("utf-8")
            if previous_ref else None)
        previous_worker = (
            bytes_at(ROOT, previous_ref, "sw.js").decode("utf-8")
            if previous_ref else None)
        self.assertEqual([], release_bundle_errors(
            index, worker, loader, runtime, previous_index, previous_worker))
        if runtime is None:
            self.assertFalse(PUBLIC_RUNTIME.exists())
            self.assertNotIn(RUNTIME_REPOSITORY_PATH, worker)

    def test_current_service_worker_forbids_runtime_without_pinning_helper_inventory(self):
        """The pre-I1 worker knew no runtime; the I1 worker pins both entries.

        Both halves are stated, because the point of the original claim was
        that a runtime entry may not appear without the helper beside it.  The
        pre-release half is made over the normalised worker; the release half
        is made LIVE, where the required inventory must carry the helper AND
        the runtime, and the runtime must be classified network-first rather
        than swept into the cache-first static inventory.

        The skipWaiting/clients.claim ban is asserted LIVE and unconditionally:
        I1 advances the shell cache generation, and it does so without giving
        the worker any way to seize control of an open tab.
        """
        pre_release = pre_i1("sw.js")
        self.assertNotIn(RUNTIME_REPOSITORY_PATH, pre_release)
        self.assertNotIn("./content/verb-patterns.json",
                         extract_required_assets(pre_release))

        worker = read(ROOT / "sw.js")
        required = extract_required_assets(worker)
        self.assertIn("./pp-verb-patterns.js", required)
        self.assertIn("./content/verb-patterns.json", required)
        executable = strip_javascript_comments(worker)
        branches = [line for line in executable.splitlines()
                    if 'category === "pattern-runtime"' in line]
        self.assertEqual(1, len(branches))
        self.assertIn("networkFirst(", branches[0])
        self.assertNotIn("cacheFirst(", branches[0])
        # ...and it is kept out of the cache-first static inventory, so it can
        # never be answered from cache under the "static" classification.
        self.assertIn("path !== PATTERN_RUNTIME_PATH", executable)
        self.assertNotIn(
            "content/verb-patterns.json",
            "\n".join(line for line in executable.splitlines()
                      if "STATIC_ASSET_PATHS" in line))

        self.assertNotIn("skipWaiting()", executable)
        self.assertNotIn("clients.claim()", executable)

    def test_generated_and_release_owned_public_outputs_remain_coherent(self):
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        self.assertEqual([], build_pages.drift_report(outputs, str(ROOT)))
        self.assertTrue((ROOT / "manifest.json").is_file())
        self.assertTrue((ROOT / "audio-manifest.json").is_file())
        self.assertTrue((ROOT / "sitemap.xml").is_file())

    def test_version_cache_schema_and_migration_markers_remain_well_formed(self):
        index = read(ROOT / "index.html")
        worker = read(ROOT / "sw.js")
        migrate = read(ROOT / "pp-migrate.js")
        self.assertGreaterEqual(len(extract_app_version(index)), 2)
        self.assertGreater(extract_shell_generation(worker), 0)
        self.assertRegex(worker, r'\bAUDIO_CACHE\s*=\s*["\']popolsku-audio["\']')
        schema = int(re.search(r"SCHEMA_VERSION\s*=\s*(\d+)", migrate).group(1))
        migration = int(re.search(
            r"CONTENT_MIGRATION_REVISION\s*=\s*(\d+)", migrate).group(1))
        self.assertGreater(schema, 0)
        self.assertGreater(migration, 0)


class ReleaseGateMutationTests(unittest.TestCase):
    def setUp(self):
        # The mutation controls model a release TRANSITION, so their "previous"
        # side must be the shell and worker as they stood before one.  Phase
        # 4F-I1 is now that release, so the pre-I1 bytes are the baseline here
        # and the complete bundle it builds is literally the I1 transition:
        # APP_VERSION 8.10 -> 8.11 and popolsku-v65 -> v66.
        self.index = pre_i1("index.html")
        self.worker = pre_i1("sw.js")
        self.loader = read(ROOT / "pp-verb-patterns.js")
        self.runtime = json.loads(read(FIXTURE))

    @staticmethod
    def versioned_index(source: str, version: str, activate: bool = True) -> str:
        source = re.sub(
            r'(APP_VERSION\s*=\s*)["\'][0-9.]+["\']',
            rf'\1"{version}"', source, count=1)
        if activate:
            source += (
                "\nvoid PP_VERB_PATTERNS.loadRuntimeDocument("
                "priority7Request, './content/verb-patterns.json');\n")
        return source

    @staticmethod
    def versioned_worker(
            source: str,
            generation: int,
            include_helper: bool = True,
            include_runtime: bool = True,
    ) -> str:
        source = re.sub(
            r'(\bCACHE\s*=\s*)["\']popolsku-v[0-9]+["\']',
            rf'\1"popolsku-v{generation}"', source, count=1)
        additions = []
        if include_helper and "./pp-verb-patterns.js" not in extract_required_assets(source):
            additions.append('  "./pp-verb-patterns.js",')
        if include_runtime and "./content/verb-patterns.json" not in extract_required_assets(source):
            additions.append('  "./content/verb-patterns.json",')
        if additions:
            source = re.sub(
                r"(\bREQUIRED_ASSETS\s*=\s*\[)",
                r"\1\n" + "\n".join(additions), source, count=1)
        return source

    def errors(self, index, worker, loader, runtime):
        return release_bundle_errors(
            index, worker, loader, runtime, self.index, self.worker)

    def test_partial_bundle_mutations_A_through_F_fail_and_complete_bundle_passes(self):
        active_index = self.versioned_index(self.index, "8.11")
        ready_worker = self.versioned_worker(self.worker, 66)
        self.assertEqual([], self.errors(
            active_index, ready_worker, self.loader, self.runtime))

        cases = {
            "A loader enabled / runtime missing": (
                active_index, ready_worker, self.loader, None,
                "public runtime missing"),
            "B runtime present / old application": (
                self.index, ready_worker, self.loader, self.runtime,
                "loader activation missing"),
            "C new application / old worker": (
                active_index, self.worker, self.loader, self.runtime,
                "runtime missing from required precache"),
            "D new helper format / old runtime": (
                active_index, ready_worker,
                re.sub(r"\bFORMAT_VERSION\s*=\s*1", "FORMAT_VERSION = 2", self.loader),
                self.runtime, "loader/runtime format mismatch"),
            "E malformed private runtime": (
                active_index, ready_worker, self.loader,
                {**self.runtime, "reviewState": "approved"},
                "public runtime invalid"),
            "F new cache / incomplete required inventory": (
                active_index,
                self.versioned_worker(
                    self.worker, 66, include_helper=True, include_runtime=False),
                self.loader, self.runtime, "runtime missing from required precache"),
        }
        for name, (index, worker, loader, runtime, expected) in cases.items():
            with self.subTest(case=name):
                errors = self.errors(index, worker, loader, runtime)
                self.assertIn(expected, errors)
                self.assertNotEqual([], errors)

    def test_second_release_uses_worktree_HEAD_then_clean_HEAD_parent(self):
        first_index = self.versioned_index(self.index, "8.11")
        first_worker = self.versioned_worker(self.worker, 66)
        second_runtime = json.loads(json.dumps(self.runtime))
        second_runtime["patternDataRevision"] += 1

        with tempfile.TemporaryDirectory(
                prefix="priority7-no-git-history-") as no_git_directory:
            self.assertIsNone(previous_release_reference(Path(no_git_directory)))

        with tempfile.TemporaryDirectory(prefix="priority7-release-gate-") as directory:
            repository = Path(directory)
            self.assertEqual(0, git("init", "-q", root=repository).returncode)
            (repository / "content").mkdir()
            (repository / "index.html").write_text(first_index, encoding="utf-8")
            (repository / "sw.js").write_text(first_worker, encoding="utf-8")
            (repository / "pp-verb-patterns.js").write_text(self.loader, encoding="utf-8")
            (repository / RUNTIME_REPOSITORY_PATH).write_text(
                json.dumps(self.runtime), encoding="utf-8")
            self.assertEqual(0, git("add", ".", root=repository).returncode)
            committed = git(
                "-c", "user.name=Priority 7 Test", "-c",
                "user.email=priority7-test@example.invalid", "commit", "-qm",
                "synthetic release one", root=repository)
            self.assertEqual(0, committed.returncode, committed.stderr)

            (repository / RUNTIME_REPOSITORY_PATH).write_text(
                json.dumps(second_runtime), encoding="utf-8")
            self.assertEqual("HEAD", previous_release_reference(repository))
            unchanged_errors = release_bundle_errors(
                first_index, first_worker, self.loader, second_runtime,
                bytes_at(repository, "HEAD", "index.html").decode("utf-8"),
                bytes_at(repository, "HEAD", "sw.js").decode("utf-8"),
            )
            self.assertIn("APP_VERSION did not advance", unchanged_errors)
            self.assertIn("shell cache generation did not advance", unchanged_errors)

            second_index = self.versioned_index(self.index, "8.12")
            second_worker = self.versioned_worker(self.worker, 67)
            self.assertEqual([], release_bundle_errors(
                second_index, second_worker, self.loader, second_runtime,
                first_index, first_worker))
            (repository / "index.html").write_text(second_index, encoding="utf-8")
            (repository / "sw.js").write_text(second_worker, encoding="utf-8")
            self.assertEqual(0, git("add", ".", root=repository).returncode)
            committed = git(
                "-c", "user.name=Priority 7 Test", "-c",
                "user.email=priority7-test@example.invalid", "commit", "-qm",
                "synthetic release two", root=repository)
            self.assertEqual(0, committed.returncode, committed.stderr)
            self.assertEqual("HEAD^", previous_release_reference(repository))
            self.assertEqual([], release_bundle_errors(
                read(repository / "index.html"), read(repository / "sw.js"),
                read(repository / "pp-verb-patterns.js"),
                json.loads(read(repository / RUNTIME_REPOSITORY_PATH)),
                bytes_at(repository, "HEAD^", "index.html").decode("utf-8"),
                bytes_at(repository, "HEAD^", "sw.js").decode("utf-8"),
            ))


class ReleaseBoundaryTests(unittest.TestCase):
    def test_real_corpus_remains_unreleased_below_editorial_review(self):
        """Phase 4F-A reached tier 1 only; nothing here is released.

        The corpus may now hold ``reference-verified`` rows, but the release
        path this suite rehearses still needs an editorial review and a human
        product approval, neither of which exists.

        Phase 4F-E1 later supplied the editorial review and Phase 4F-F2 the
        human product approval.  That approved governance work is reverted
        before the historical tier-1 claims are made.  What this test still
        guards about *release* is asserted against the LIVE files -- zero
        eligibility, zero audio, no public runtime -- because neither later
        tier moved any of it.  The former live claims that no row is
        ``approved`` and that no ``product-approval`` event exists were
        statements about which tiers had run; Phase 4F-F2 legitimately
        superseded both, so they are now made over the normalised corpus.
        Governance approval is not release: it authorises inclusion and
        switches nothing on.
        """
        live_corpus = json.loads(read(CORPUS))
        live_context = json.loads(read(CONTEXT))
        corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live_corpus))))
        context = E1.without_phase_4fe1_actors(
            F2.without_phase_4ff2_reviewer(
                H2.without_phase_4fh2_context(
                    H21.without_phase_4fh21_context(live_context))))
        patterns = [
            pattern
            for lemma in corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        live_patterns = [
            pattern
            for lemma in live_corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        self.assertEqual(45, len(patterns))
        self.assertEqual(45, len(live_patterns))
        self.assertEqual({"reference-verified"},
                         {pattern["reviewState"] for pattern in patterns})
        self.assertEqual(
            {"reference-verification"},
            {event["kind"] for pattern in patterns
             for event in pattern["reviewEvents"]})
        self.assertNotIn(
            "approved", {pattern["reviewState"] for pattern in patterns})
        self.assertNotIn(
            "product-approval",
            {event["kind"] for pattern in patterns
             for event in pattern["reviewEvents"]})
        self.assertEqual(0, sum(len(pattern["activityEligibility"])
                                for pattern in live_patterns))
        self.assertEqual(
            0,
            sum(
                example["audioEligible"] is True
                for pattern in live_patterns
                for example in pattern.get("examples", [])
            ),
        )
        # Phase 4C named one real human native-linguistic reviewer; the
        # authorRegistry stays empty because no human example author exists.
        self.assertEqual({"native-reviewer-001"}, set(context["reviewerRegistry"]))
        self.assertEqual(
            ["native-linguistic"],
            context["reviewerRegistry"]["native-reviewer-001"]["roles"])
        self.assertEqual({}, context["authorRegistry"])
        # Phase 4F-A registered exactly one nonhuman actor, for tier 1 only.
        # Phase 4F-C2 added a second for example generation, which carries no
        # review role, so the release boundary is stated over the review roles
        # rather than over the registry key set.
        actors = context["editorialActorRegistry"]
        self.assertIn("priority7-reference-analysis", actors)
        self.assertIs(False, actors["priority7-reference-analysis"]["human"])
        self.assertEqual(["reference-verification"],
                         actors["priority7-reference-analysis"]["roles"])
        self.assertEqual(
            {"priority7-reference-analysis"},
            {actor_id for actor_id, record in actors.items()
             if {"reference-verification", "editorial-review"}
             & set(record.get("roles") or [])})
        # Live, and unconditional: no registered editorial actor may ever be
        # a person, whichever phase registered it.
        for actor_id, record in live_context["editorialActorRegistry"].items():
            self.assertIs(False, record["human"], actor_id)
        self.assertEqual({}, live_context["authorRegistry"])
        corpus_text = read(CORPUS)
        self.assertNotRegex(corpus_text, r'"exerciseId"\s*:')
        self.assertNotRegex(corpus_text, r'"vp-x-[^"]+"')
        # Superseded by Priority 7 Phase 4F-I1, the release phase.  Governance
        # approval is still not release; what IS release is exactly the pinned
        # I1 artifact, which may only exist beside its matching shell and
        # worker.  Nothing about the tier claims above authorised it.
        self.assertEqual("complete", i1_bundle().state)

    def test_priority7_path_adds_no_progress_mastery_or_analytics(self):
        loader = read(ROOT / "pp-verb-patterns.js")
        index = read(ROOT / "index.html")
        patterns_block = index[
            index.index("const P = { li:0, ti:0, topicRef:null"):
            index.index("/* ---------------- grammar (teach -> drill) ---------------- */")
        ]
        for source in (loader, patterns_block):
            executable = re.sub(r"/\*[\s\S]*?\*/", "", source)
            executable = re.sub(r"^\s*//.*$", "", executable, flags=re.M)
            for forbidden in (
                "localStorage", "sessionStorage", "indexedDB", "mastery",
                "analytics", "gtag", "sendBeacon", "persistProgress",
            ):
                with self.subTest(token=forbidden):
                    self.assertNotIn(forbidden, executable)


if __name__ == "__main__":
    unittest.main()
