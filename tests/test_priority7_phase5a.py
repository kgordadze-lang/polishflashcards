"""Priority 7 Phase 5-A synthetic freeze and authorization rehearsal.

Every editorial record, reviewer, author, source and sentence exercised here is
invented and marked TEST-ONLY.  Nothing in this suite is a linguistic claim, a
human review decision, a real approval, or a real release.  The suite proves one
thing: that a completely fictional candidate can travel the real governance
machinery -- editorial validation, review-state derivation, freeze/allocation,
release-authoritative projection, public-runtime validation and the Phase 3F-A
shipping loader -- while every invalid, stale or incompletely reviewed candidate
is refused.

The real 45-pattern corpus is never read as input to any governance operation
here; it is only checked for byte-identity against HEAD.
"""

from __future__ import annotations

import builtins
import copy
import csv
import hashlib
import inspect
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import priority7_tooling as T
from priority7_tooling import (
    FORBIDDEN_RUNTIME_KEYS,
    FROZEN_ARTIFACT_STATUS,
    GOVERNANCE_PRIVATE_KEYS,
    NONRELEASE_PROJECTION_STATUS,
    PRIVATE_RUNTIME_KEYS,
    RepositoryIndex,
    ValidationContext,
    ValidationFailure,
    allocate_example_id,
    allocate_pattern_id,
    evidence_digest,
    freeze_editorial,
    project_nonrelease_fixture,
    project_runtime_nonrelease,
    review_scope_digest,
    validate_editorial,
    validate_frozen_release,
    validate_runtime,
    verified_runtime_from_frozen,
)

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
import priority7_phase4fh3_normalizer as H3


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

def i1_baseline_reference():
    """Phase 4F-I1 baseline comparisons in this suite are made against HEAD."""
    return "HEAD"

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


def i1_baseline_blob(reference, path):
    """The bytes of ``path`` at ``reference``, or ``None`` when it is absent."""
    result = subprocess.run(
        ["git", "show", f"{reference}:{path}"], cwd=str(ROOT),
        capture_output=True, check=False)
    return result.stdout if result.returncode == 0 else None


def is_only_the_i1_activation(path, reference=None):
    """True when ``path``'s whole difference from the baseline is the I1 layer.

    Phase 4F-I1 is the release that activates Priority 7.  A path qualifies
    only when it is one of the paths I1 was entitled to move AND the pinned I1
    layer accounts for every byte of the difference:

    * ``content/verb-patterns.json`` -- present with exactly the pinned release
      digest, byte length and revision, and nothing else in ``content/``;
    * ``index.html`` / ``sw.js`` -- classified through the all-or-nothing
      bundle, so neither can qualify unless the runtime and the other file
      moved with it;
    * a generated page -- differing by its one footer version stamp alone;
    * ``sitemap.xml`` -- differing by ``<lastmod>`` values alone, with an
      identical URL set, order and structure.

    Every other path, and any other edit to these paths, is still reported.
    """
    reference = i1_baseline_reference() if reference is None else reference
    path = path.rstrip("/")
    if path == "content":
        present = sorted(
            str(p.relative_to(ROOT)) for p in (ROOT / "content").rglob("*")
            if p.is_file())
        if present != [I1.PHASE_4FI1_RUNTIME_PATH]:
            return False
        path = I1.PHASE_4FI1_RUNTIME_PATH
    if not I1.is_phase_4fi1_path(path):
        return False
    if path == I1.PHASE_4FI1_RUNTIME_PATH:
        return i1_bundle().state == "complete"
    baseline = i1_baseline_blob(reference, path)
    if baseline is None:
        return False
    return I1.is_exactly_the_i1_transition(
        path, baseline.decode("utf-8"),
        (ROOT / path).read_text(encoding="utf-8"), bundle=i1_bundle())
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "priority7"
SYNTHETIC_FIXTURE = FIXTURE_DIR / "synthetic-release-editorial.json"
LOADER_HARNESS = FIXTURE_DIR / "phase5a-loader-harness.js"
CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CONTEXT_FILE = ROOT / "editorial" / "priority-7-authoring-context.json"
PUBLIC_RUNTIME = ROOT / "content" / "verb-patterns.json"

SYNTHETIC_CARD_ID = "p7-phase5a-synthetic-card-001"
REVIEWED_AT = "2026-08-08"
LATER_REVIEWED_AT = "2026-08-09"


# --------------------------------------------------------------------------
# fixture loading and synthetic scaffolding
# --------------------------------------------------------------------------

def payload():
    return json.loads(SYNTHETIC_FIXTURE.read_text(encoding="utf-8"))


def editorial():
    """A fresh deep copy of the synthetic private editorial document."""
    return payload()["editorial"]


def context(*, repository_index=None):
    data = payload()
    identities = data["syntheticIdentities"]
    if repository_index is None:
        repository_index = RepositoryIndex.from_sources(
            data["syntheticRepositorySources"])
    return ValidationContext(
        source_registry=identities["sourceRegistry"],
        reviewer_registry=identities["reviewerRegistry"],
        author_registry=identities["authorRegistry"],
        editorial_actor_registry=identities["editorialActorRegistry"],
        repository_index=repository_index,
        today=date.fromisoformat(data["reviewContextDate"]),
    )


def parts(document, lemma_index=0, meaning_index=0, pattern_index=0):
    lemma = document["lemmas"][lemma_index]
    meaning = lemma["meanings"][meaning_index]
    pattern = meaning["patterns"][pattern_index]
    return lemma, meaning, pattern


def acceptance_events(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    """Rebuild a complete, currently-valid three-stage acceptance chain."""
    pins = sorted({
        evidence_digest(record) for record in pattern["evidence"]
        if record["sourceKind"] in {
            "contemporary-reference", "contemporary-corpus"}
    })
    return [
        {
            "kind": "external-verification",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "external-verification", lemma, meaning, pattern),
            "supportingEvidenceDigests": pins,
            "reviewerRef": "test-reviewer-external-001",
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "native-linguistic",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "native-linguistic", lemma, meaning, pattern),
            "reviewerRef": "test-reviewer-native-001",
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": "test-reviewer-product-001",
            "reviewedAt": reviewed_at,
        },
    ]


def restamp(document, reviewed_at=REVIEWED_AT):
    """Replace every approved pattern's review chain with a current one."""
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    pattern["reviewEvents"] = acceptance_events(
                        lemma, meaning, pattern, reviewed_at)
    return document


def append_review(document, reviewed_at=LATER_REVIEWED_AT):
    """Append a fresh acceptance chain, preserving the append-only prefix."""
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") == "approved":
                    pattern["reviewEvents"].extend(
                        acceptance_events(lemma, meaning, pattern, reviewed_at))
    return document


def append_correction_and_review(document, note, reviewed_at=LATER_REVIEWED_AT):
    """Released content changes need an owner correction plus a fresh review.

    This APPENDS to the existing chain and never rewrites it: a released
    pattern's review history must stay an exact prefix of its successor, so
    restamping a document that already has a frozen predecessor is itself a
    governance violation (FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY).
    """
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") != "approved":
                    continue
                pattern["reviewEvents"].append({
                    "kind": "correction",
                    "decision": "accept",
                    "reviewerRef": "test-reviewer-product-001",
                    "reviewedAt": reviewed_at,
                    "note": note,
                })
                pattern["reviewEvents"].extend(
                    acceptance_events(lemma, meaning, pattern, reviewed_at))
    return document


def add_approved_pattern(document, key="second-direct-object"):
    """Clone the reviewed direct-object frame under a freshly allocated ID."""
    lemma, meaning, template = parts(document)
    pattern = copy.deepcopy(template)
    pattern_id = allocate_pattern_id(
        meaning["id"], lemma["canonicalLemma"], meaning["key"], key)
    pattern["id"] = pattern_id
    pattern["key"] = key
    for example in pattern.get("examples", []):
        example["id"] = allocate_example_id(pattern_id, example["key"])
    meaning["patterns"].append(pattern)
    # Only the newly added pattern is stamped: its siblings already carry a
    # released, currently-valid chain that must remain an exact prefix.
    pattern["reviewEvents"] = acceptance_events(lemma, meaning, pattern)
    return pattern_id


def approved_pattern_ids(document):
    return {
        pattern["id"]
        for lemma in document["lemmas"]
        for meaning in lemma["meanings"]
        for pattern in meaning["patterns"]
        if pattern["reviewState"] == "approved"
    }


def walk(value, path="$"):
    """Yield every (path, key, value) pair at any depth of a JSON value."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield f"{path}.{key}", key, child
            yield from walk(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f"{path}[{index}]")


def git(*arguments):
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, text=True,
        check=False)


def is_only_the_h3_ui_wording(path):
    """True for ``index.html`` when its only change is the Phase 4F-H3 layer.

    This guard reads the working tree against ``HEAD``, so that is the
    baseline the comparison uses.  Phase 4F-H3 is the UI wording phase and the
    first phase since ``f339efb`` entitled to change a shipping file at all;
    removing its six pinned strings must reproduce ``HEAD``'s bytes exactly,
    so any other shell edit -- a version or cache bump, a loader activation, a
    change to the recognition-only guards -- any other path, and any partly
    applied layer are still reported as an unexpected footprint.
    """
    if not H3.is_phase_4fh3_path(path):
        return False
    baseline = git("show", f"HEAD:{path}")
    if baseline.returncode != 0:
        return False
    # LAYERED by Priority 7 Phase 4F-I1, the same way the corpus claims are
    # layered through E1/F2/H2/H2.1: the shell now carries the I1 release layer
    # on top of the H3 wording layer, so the H3 classification is made over the
    # shell with the I1 layer removed.  Both layers are all-or-nothing and
    # neither hides anything the other could not, so an edit outside the two
    # pinned sets is still reported here exactly as before.
    return H3.is_exactly_the_h3_ui_wording(path, baseline.stdout, pre_i1(path))


class Phase5ATestCase(unittest.TestCase):
    maxDiff = None

    def assertCode(self, issues, code):
        codes = [issue.code for issue in issues]
        self.assertIn(code, codes, f"expected {code} in {codes}")

    def assertFailsWith(self, code, callable_object, *arguments, **keywords):
        with self.assertRaises(ValidationFailure) as caught:
            callable_object(*arguments, **keywords)
        self.assertCode(caught.exception.issues, code)
        return caught.exception.issues

    def assertValidEditorial(self, document, validation_context=None):
        issues = validate_editorial(
            document, validation_context or context())
        self.assertEqual([], issues, f"unexpected editorial issues: {issues}")

    def baseline(self, document=None, revision=1):
        return freeze_editorial(document or editorial(), revision, context())

    def released_runtime(self, frozen):
        return verified_runtime_from_frozen(frozen)


# --------------------------------------------------------------------------
# §7/§8  the fixture itself is unmistakably synthetic and self-contained
# --------------------------------------------------------------------------

class SyntheticFixtureTests(Phase5ATestCase):

    def test_fixture_is_marked_test_only_and_carries_no_real_identity(self):
        data = payload()
        self.assertIn("SYNTHETIC TEST-ONLY", data["testOnlyNotice"])
        self.assertIn("synthetic", data["artifactStatus"])
        self.assertNotEqual(
            data["artifactStatus"],
            data["editorial"]["artifactStatus"],
            "the harness envelope must not impersonate an editorial corpus")

        raw = SYNTHETIC_FIXTURE.read_text(encoding="utf-8")
        for forbidden in (
                "Kaj", "kaj", "GPT", "Claude", "Codex", "OpenAI", "Anthropic",
                "gordadze"):
            self.assertNotIn(
                forbidden, raw,
                f"{forbidden!r} must never appear as synthetic review identity")

        identities = data["syntheticIdentities"]
        for registry_name in ("reviewerRegistry", "authorRegistry"):
            registry = identities[registry_name]
            self.assertTrue(registry)
            for reference in registry:
                self.assertTrue(
                    reference.startswith("test-"),
                    f"{reference!r} must be an obviously test-only identity")

    def test_fixture_shares_no_lemma_example_or_content_ref_with_the_real_corpus(self):
        real = json.loads(CORPUS.read_text(encoding="utf-8"))
        real_strings = set()
        real_ids = set()
        for _, key, value in walk(real):
            if isinstance(value, str):
                if key in {"canonicalLemma", "displayLemma", "pl", "en"}:
                    real_strings.add(value)
                if key == "id":
                    real_ids.add(value)

        synthetic = payload()["editorial"]
        synthetic_strings = set()
        synthetic_ids = set()
        for _, key, value in walk(synthetic):
            if isinstance(value, str):
                if key in {"canonicalLemma", "displayLemma", "pl", "en"}:
                    synthetic_strings.add(value)
                if key == "id":
                    synthetic_ids.add(value)

        self.assertTrue(synthetic_strings)
        self.assertTrue(synthetic_ids)
        self.assertEqual(set(), real_strings & synthetic_strings)
        self.assertEqual(set(), real_ids & synthetic_ids)

        # contentRefs must not point at any real repository entity either.
        synthetic_refs = {
            reference["id"]
            for _, key, value in walk(synthetic) if key == "contentRefs"
            for reference in (value if isinstance(value, list) else [])
        }
        self.assertEqual({SYNTHETIC_CARD_ID}, synthetic_refs)

    def test_fixture_text_is_invented_and_not_polish(self):
        synthetic = payload()["editorial"]
        polish_only = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
        for path, key, value in walk(synthetic):
            if key in {"canonicalLemma", "pl", "en", "glossesEn"} and isinstance(
                    value, str):
                self.assertFalse(
                    polish_only & set(value),
                    f"{path} carries Polish-specific characters: {value!r}")
        lemmas = [lemma["canonicalLemma"] for lemma in synthetic["lemmas"]]
        self.assertEqual(["zorbulate", "quuxify"], lemmas)

    def test_fixture_editorial_document_validates_against_real_tooling(self):
        self.assertValidEditorial(editorial())

    def test_fixture_exercises_the_states_the_rehearsal_needs(self):
        document = editorial()
        states = [
            pattern["reviewState"]
            for lemma in document["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        self.assertIn("approved", states)
        self.assertIn("research", states)
        statuses = {
            pattern["teachingStatus"]
            for lemma in document["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        }
        self.assertIn("active-production", statuses)
        self.assertIn("recognition-only", statuses)
        origins = {
            example["origin"]["kind"]
            for _, key, value in walk(document) if key == "examples"
            for example in (value if isinstance(value, list) else [])
        }
        self.assertEqual({"original", "repository-reuse"}, origins)


# --------------------------------------------------------------------------
# §10  standalone projection is not release authority
# --------------------------------------------------------------------------

class ReleaseAuthorityPathTests(Phase5ATestCase):

    def test_standalone_projection_is_shape_valid_but_not_release_authoritative(self):
        document = editorial()
        standalone = project_runtime_nonrelease(document, 1, context())

        # It is a perfectly valid PUBLIC SHAPE ...
        self.assertEqual([], validate_runtime(standalone))
        self.assertEqual(
            ["formatVersion", "lemmas", "patternDataRevision"],
            sorted(standalone))

        # ... and it still proves nothing about release authority: it accepts
        # any positive revision it is handed, with no previous snapshot, no
        # allocation registry, no tombstone history and no freeze.
        for invented_revision in (1, 2, 7, 424242):
            projected = project_runtime_nonrelease(
                document, invented_revision, context())
            self.assertEqual(
                invented_revision, projected["patternDataRevision"])

        # The CLI-facing wrapper says so in the artifact itself.
        wrapper = project_nonrelease_fixture(document, 99, context())
        self.assertEqual(NONRELEASE_PROJECTION_STATUS, wrapper["artifactStatus"])
        self.assertIs(False, wrapper["releaseAuthorized"])

    def test_release_authoritative_path_requires_the_governance_envelope(self):
        frozen = self.baseline()
        self.assertEqual(FROZEN_ARTIFACT_STATUS, frozen["artifactStatus"])
        self.assertEqual([], validate_frozen_release(frozen))

        runtime = self.released_runtime(frozen)
        self.assertEqual(frozen["runtimeProjection"], runtime)
        self.assertEqual([], validate_runtime(runtime))

        # The runtime alone cannot re-enter the release-authoritative path: it
        # carries no allocations, identity, structure, wording, policy,
        # tombstones or review history.
        issues = self.assertFailsWith(
            "SCHEMA_REQUIRED", verified_runtime_from_frozen, runtime)
        missing = {issue.path.rsplit(".", 1)[-1] for issue in issues}
        self.assertLessEqual(
            {"allocations", "identity", "structure", "wording", "policy",
             "tombstones", "reviewHistory", "artifactStatus"}, missing)

        # Nor can the explicitly nonrelease wrapper stand in for the envelope.
        wrapper = project_nonrelease_fixture(editorial(), 1, context())
        self.assertFailsWith(
            "SCHEMA_REQUIRED", verified_runtime_from_frozen, wrapper)

    def test_release_authority_cannot_be_inferred_from_public_json_shape(self):
        """A hand-written document of the right shape is shape-valid only."""
        frozen = self.baseline()
        forged = copy.deepcopy(self.released_runtime(frozen))
        forged["patternDataRevision"] = 999

        # The public validator answers shape, and says yes.
        self.assertEqual([], validate_runtime(forged))
        # The release-authoritative validator is the one that says no, because
        # the forged revision no longer matches the frozen envelope.
        forged_envelope = copy.deepcopy(frozen)
        forged_envelope["runtimeProjection"] = forged
        self.assertNotEqual([], validate_frozen_release(forged_envelope))

    def test_release_authoritative_path_has_no_command_line_wrapper_yet(self):
        """Phase 5-A deliberately leaves the release command unimplemented.

        The release-authoritative path is a library API only.  Nothing on the
        command line can emit a frozen envelope or an authoritative runtime, so
        no accidental invocation can produce a release artifact.
        """
        import priority7_tooling

        completed = subprocess.run(
            [sys.executable, "-c",
             "import priority7_tooling, sys;"
             "sys.exit(priority7_tooling.main(['--help']))"],
            capture_output=True, text=True, cwd=ROOT, check=False)
        offered = completed.stdout + completed.stderr
        self.assertIn("project-fixture", offered)
        for absent in ("freeze", "release", "publish"):
            self.assertNotIn(
                f"{absent}\n", offered,
                f"the CLI must not offer a {absent!r} subcommand yet")

        # And the pure entry points really are the release-authoritative ones.
        for name in ("freeze_editorial", "validate_frozen_release",
                     "verified_runtime_from_frozen"):
            self.assertTrue(callable(getattr(priority7_tooling, name)))


# --------------------------------------------------------------------------
# §11/§12  freeze, allocation, ID stability and tombstones
# --------------------------------------------------------------------------

class FreezeAllocationTests(Phase5ATestCase):

    def test_first_freeze_allocates_every_entity_deterministically(self):
        frozen = self.baseline()
        self.assertEqual(1, frozen["patternDataRevision"])
        self.assertEqual([], frozen["tombstones"])

        allocated = {row["id"]: row for row in frozen["allocations"]}
        kinds = sorted({row["kind"] for row in frozen["allocations"]})
        self.assertEqual(["example", "lemma", "meaning", "pattern"], kinds)
        for entity_id, row in allocated.items():
            self.assertTrue(entity_id.startswith(
                {"lemma": "vp-l-", "meaning": "vp-m-",
                 "pattern": "vp-p-", "example": "vp-e-"}[row["kind"]]))
            self.assertIn("seed", row)

        # Freezing the identical document twice is byte-identical.
        self.assertEqual(frozen, self.baseline())

    def test_A_unchanged_entity_keeps_its_frozen_id_in_a_later_snapshot(self):
        baseline = self.baseline()
        unchanged = editorial()
        advanced = freeze_editorial(unchanged, 1, context(), previous=baseline)

        self.assertEqual(
            [row["id"] for row in baseline["allocations"]],
            [row["id"] for row in advanced["allocations"]])
        self.assertEqual(baseline["allocations"], advanced["allocations"])
        self.assertEqual(baseline["identity"], advanced["identity"])
        self.assertEqual(1, advanced["patternDataRevision"])

    def test_B_new_entity_receives_a_new_deterministic_frozen_allocation(self):
        baseline = self.baseline()
        document = editorial()
        new_id = add_approved_pattern(document)
        self.assertValidEditorial(document)

        advanced = freeze_editorial(document, 2, context(), previous=baseline)
        before = {row["id"] for row in baseline["allocations"]}
        after = {row["id"] for row in advanced["allocations"]}
        self.assertTrue(before < after, "previous allocations must be retained")
        self.assertIn(new_id, after - before)

        # The new ID is the deterministic function of its own seed, and the two
        # example IDs beneath it were allocated too.
        new_rows = {row["id"]: row for row in advanced["allocations"]}
        self.assertEqual("pattern", new_rows[new_id]["kind"])
        self.assertEqual(
            2, len([row for row in advanced["allocations"]
                    if row["kind"] == "example" and row["parentId"] == new_id]))

    def test_C_removed_entity_requires_a_tombstone_and_D_cannot_be_reused(self):
        baseline = self.baseline()
        document = editorial()
        lemma, meaning, _ = parts(document)
        retired = meaning["patterns"].pop(1)          # the clause-content frame
        retired_id = retired["id"]
        self.assertValidEditorial(document)

        # C1: silent removal of a released ID is refused.
        self.assertFailsWith(
            "FROZEN_REMOVAL_WITHOUT_TOMBSTONE",
            freeze_editorial, document, 2, context(), previous=baseline)

        tombstone = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": meaning["id"],
            "retirementRevision": 2,
            "reason": "TEST-ONLY synthetic retirement for the Phase 5-A rehearsal.",
            "replacementIds": [],
        }
        retired_frozen = freeze_editorial(
            document, 2, context(), previous=baseline, tombstones=[tombstone])
        self.assertEqual(
            [retired_id], [row["id"] for row in retired_frozen["tombstones"]])
        self.assertNotIn(
            retired_id, {row["id"] for row in retired_frozen["identity"]})
        # The allocation record survives: a retired ID stays reserved, it is
        # not released back into the pool.
        self.assertIn(
            retired_id, {row["id"] for row in retired_frozen["allocations"]})

        # D1: the retired entity itself cannot simply come back.
        self.assertFailsWith(
            "TOMBSTONE_RESURRECTION",
            freeze_editorial, editorial(), 3, context(),
            previous=retired_frozen)

        # D2: a DIFFERENT semantic entity cannot wear the retired ID either.
        # Two independent guards refuse it before the tombstone check is even
        # reached, which is the point: the ID is a deterministic function of
        # the entity's own seed, and the released allocation pins its key.
        resurrect = editorial()
        _, r_meaning, _ = parts(resurrect)
        r_meaning["patterns"][1]["key"] = "different-semantic-frame"
        r_meaning["patterns"][1]["id"] = retired_id
        issues = self.assertFailsWith(
            "ALLOCATION_KEY",
            freeze_editorial, resurrect, 3, context(), previous=retired_frozen)
        self.assertCode(issues, "REVIEW_STATE_MISMATCH")

        # And with no prior allocation to hide behind, the ID simply does not
        # recompute for a different entity.
        fresh = editorial()
        _, f_meaning, _ = parts(fresh)
        f_meaning["patterns"][1]["key"] = "different-semantic-frame"
        f_meaning["patterns"][1]["id"] = retired_id
        self.assertCode(
            validate_editorial(fresh, context()), "ID_RECOMPUTATION")

    def test_D_tombstones_are_immutable_within_a_transition(self):
        baseline = self.baseline()
        document = editorial()
        _, meaning, _ = parts(document)
        retired_id = meaning["patterns"].pop(1)["id"]
        tombstone = {
            "id": retired_id,
            "kind": "pattern",
            "formerParentId": meaning["id"],
            "retirementRevision": 2,
            "reason": "TEST-ONLY synthetic retirement.",
            "replacementIds": [],
        }
        retired = freeze_editorial(
            document, 2, context(), previous=baseline, tombstones=[tombstone])

        # Re-adding an existing tombstone is refused rather than merged.
        self.assertFailsWith(
            "TOMBSTONE_IMMUTABLE", freeze_editorial, copy.deepcopy(document), 2,
            context(), previous=retired, tombstones=[tombstone])

        # Supplying a DIFFERENT tombstone for an already-retired ID is refused
        # by the same guard, so a retirement reason cannot be rewritten through
        # the transition interface.
        self.assertFailsWith(
            "TOMBSTONE_IMMUTABLE", freeze_editorial, copy.deepcopy(document), 2,
            context(), previous=retired,
            tombstones=[dict(tombstone, reason="TEST-ONLY rewritten reason.")])

    def test_tombstone_tampering_inside_the_stored_baseline_is_out_of_scope(self):
        """An honest limitation, recorded rather than overstated.

        freeze_editorial treats `previous` as trusted input: it revalidates the
        baseline's shape, but it has no independent memory of what the baseline
        used to say, so an edit made directly to a stored frozen file is not
        detectable here. Integrity of the stored artifact belongs to the
        eventual release command/storage layer, not to this pure function.
        """
        baseline = self.baseline()
        document = editorial()
        _, meaning, _ = parts(document)
        retired_id = meaning["patterns"].pop(1)["id"]
        retired = freeze_editorial(
            document, 2, context(), previous=baseline, tombstones=[{
                "id": retired_id,
                "kind": "pattern",
                "formerParentId": meaning["id"],
                "retirementRevision": 2,
                "reason": "TEST-ONLY synthetic retirement.",
                "replacementIds": [],
            }])

        tampered = copy.deepcopy(retired)
        tampered["tombstones"][0]["reason"] = "TEST-ONLY altered reason."
        # It still validates, because nothing here can know it changed ...
        self.assertEqual([], validate_frozen_release(tampered))
        # ... but the retirement itself still holds: the ID cannot come back.
        self.assertFailsWith(
            "TOMBSTONE_RESURRECTION", freeze_editorial, editorial(), 3,
            context(), previous=tampered)

    def test_tombstone_retirement_revision_must_match_the_transition(self):
        baseline = self.baseline()
        document = editorial()
        _, meaning, _ = parts(document)
        retired_id = meaning["patterns"].pop(1)["id"]
        self.assertFailsWith(
            "TOMBSTONE_REVISION", freeze_editorial, document, 2, context(),
            previous=baseline, tombstones=[{
                "id": retired_id,
                "kind": "pattern",
                "formerParentId": meaning["id"],
                "retirementRevision": 1,
                "reason": "TEST-ONLY wrong retirement revision.",
                "replacementIds": [],
            }])

    def test_tombstoning_an_id_that_was_never_released_is_refused(self):
        baseline = self.baseline()
        document = editorial()
        self.assertFailsWith(
            "TOMBSTONE_UNKNOWN_ID", freeze_editorial, document, 1, context(),
            previous=baseline, tombstones=[{
                "id": "vp-p-zorbulate-test-object-never-existed-000000000000",
                "kind": "pattern",
                "formerParentId": parts(document)[1]["id"],
                "retirementRevision": 1,
                "reason": "TEST-ONLY tombstone for an unreleased ID.",
                "replacementIds": [],
            }])

    def test_E_released_relation_type_mutation_requires_replacement(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["relationType"] = "constructional-frame"
        append_correction_and_review(
            document, "TEST-ONLY correction attempting a relationType change.")
        self.assertValidEditorial(document)

        self.assertFailsWith(
            "FROZEN_RELATION_REPLACEMENT_REQUIRED",
            freeze_editorial, document, 2, context(), previous=baseline)

    def test_E_released_identity_fields_cannot_drift_in_place(self):
        """The released immutable key is pinned by its allocation record.

        The guard fires as ALLOCATION_KEY rather than FROZEN_IDENTITY_DRIFT:
        the allocation registry is consulted during editorial validation, so a
        renamed released entity is refused before the freeze stage compares
        identity rows at all.  Both guards exist; this is the first one.
        """
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        # Same frozen ID, different owning key: an identity change in place.
        pattern["key"] = "renamed-frame"
        append_correction_and_review(
            document, "TEST-ONLY correction attempting an identity rename.")
        self.assertFailsWith(
            "ALLOCATION_KEY",
            freeze_editorial, document, 2, context(), previous=baseline)

    def test_released_complement_identity_change_requires_replacement(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["complements"][0]["case"] = "genitive"
        append_correction_and_review(
            document, "TEST-ONLY correction attempting a complement change.")
        self.assertFailsWith(
            "FROZEN_COMPLEMENT_REPLACEMENT_REQUIRED",
            freeze_editorial, document, 2, context(), previous=baseline)

    def test_frozen_allocation_registry_cannot_be_forged(self):
        frozen = self.baseline()
        forged = copy.deepcopy(frozen)
        for row in forged["allocations"]:
            if row["kind"] == "pattern":
                row["seed"] = "v1|pattern|forged"
                break
        self.assertCode(validate_frozen_release(forged), "FROZEN_SEED")

        missing = copy.deepcopy(frozen)
        missing["allocations"] = [
            row for row in missing["allocations"] if row["kind"] != "example"]
        issues = validate_frozen_release(missing)
        self.assertCode(issues, "FROZEN_IDENTITY_UNALLOCATED")
        self.assertCode(issues, "FROZEN_ALLOCATION_COVERAGE")


# --------------------------------------------------------------------------
# §13  evidence digest invalidation
# --------------------------------------------------------------------------

class EvidenceDigestTests(Phase5ATestCase):

    def test_evidence_digest_covers_the_complete_record_including_note(self):
        _, _, pattern = parts(editorial())
        record = pattern["evidence"][0]
        self.assertIn("note", record)
        without_note = {
            key: value for key, value in record.items() if key != "note"}
        self.assertNotEqual(
            evidence_digest(record), evidence_digest(without_note))
        altered_note = dict(record, note=record["note"] + " altered")
        self.assertNotEqual(
            evidence_digest(record), evidence_digest(altered_note))

    def test_current_evidence_digest_passes_the_release_authoritative_path(self):
        frozen = self.baseline()
        self.assertEqual([], validate_frozen_release(frozen))
        self.assertEqual([], validate_runtime(self.released_runtime(frozen)))

    def test_mutating_evidence_after_review_makes_the_review_stale(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"][0]["locator"] += "/mutated-after-review"

        # The stored approval no longer matches the evidence it pinned, so the
        # derived state collapses and the record is refused before freeze.
        issues = validate_editorial(document, context())
        self.assertCode(issues, "REVIEW_STATE_MISMATCH")
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_mutating_an_evidence_note_alone_is_enough_to_invalidate(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"][0]["note"] += " quietly edited"
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_STATE_MISMATCH")

    def test_pinned_evidence_alone_can_invalidate_the_external_acceptance(self):
        """Isolates the evidence PIN from the review scope.

        The second evidence record is not referenced by any error note, so it
        contributes nothing to any stage's scope digest.  Editing it can only
        break the external acceptance's pinned digests -- which is exactly the
        guard under test, and which must be enough on its own to collapse the
        derived state all the way back to 'research'.
        """
        document = editorial()
        _, _, pattern = parts(document)
        self.assertEqual(
            [0], pattern["errorNotes"][0]["evidenceRefs"],
            "this test relies on evidence[1] being unreferenced")
        pattern["evidence"][1]["locator"] += "/pin-only-mutation"

        issues = validate_editorial(document, context())
        mismatch = [
            issue for issue in issues if issue.code == "REVIEW_STATE_MISMATCH"]
        self.assertEqual(1, len(mismatch))
        self.assertIn("'research'", mismatch[0].message)
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_removing_pinned_evidence_invalidates_the_external_acceptance(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"].pop(0)
        # The error note referenced index 0; drop it so the failure under test
        # is the pin, not a dangling reference.
        pattern["errorNotes"][0].pop("evidenceRefs")
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_STATE_MISMATCH")

    def test_recomputed_review_restores_the_release_authoritative_path(self):
        """§13 steps 4 and 5, on a candidate that has not been released yet."""
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"][0]["locator"] += "/mutated-after-review"

        # Step 3: the stale review is rejected.
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

        # Step 4: recompute and re-review in the synthetic model.
        restamp(document)
        self.assertValidEditorial(document)

        # Step 5: the release-authoritative path passes again.
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        self.assertEqual([], validate_runtime(self.released_runtime(frozen)))

    def test_after_release_evidence_may_be_appended_but_not_edited(self):
        """Released evidence is append-only, so §13's repair path is an append.

        Editing a released evidence record in place is refused outright,
        because error-note references are positional: silently rewriting a
        record could retarget a published error claim.
        """
        baseline = self.baseline()

        edited = editorial()
        _, _, pattern = parts(edited)
        pattern["evidence"][0]["locator"] += "/edited-after-release"
        append_correction_and_review(
            edited, "TEST-ONLY correction: evidence locator restated.")
        self.assertFailsWith(
            "FROZEN_EVIDENCE_NOT_APPEND_ONLY",
            freeze_editorial, edited, 1, context(), previous=baseline)

        # The supported repair is to append a new record and re-review.
        appended = editorial()
        _, _, pattern = parts(appended)
        pattern["evidence"].append({
            "sourceId": "test-source-corpus-001",
            "sourceKind": "contemporary-corpus",
            "locator": "fixture://phase5a/synthetic/appended-corroboration",
            "factType": "complement-frame",
            "checkedAt": REVIEWED_AT,
            "note": "TEST-ONLY appended corroboration record.",
        })
        append_correction_and_review(
            appended, "TEST-ONLY correction: corroboration appended.")
        self.assertValidEditorial(appended)

        # Evidence is private, so the public payload and revision are unchanged.
        advanced = freeze_editorial(appended, 1, context(), previous=baseline)
        self.assertEqual(1, advanced["patternDataRevision"])
        self.assertEqual([], validate_frozen_release(advanced))
        self.assertEqual(
            baseline["runtimeProjection"], advanced["runtimeProjection"])

    def test_released_evidence_order_is_append_only(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"].reverse()
        pattern["errorNotes"][0]["evidenceRefs"] = [1]
        append_correction_and_review(
            document, "TEST-ONLY correction reordering evidence.")
        self.assertFailsWith(
            "FROZEN_EVIDENCE_NOT_APPEND_ONLY",
            freeze_editorial, document, 1, context(), previous=baseline)


# --------------------------------------------------------------------------
# §14  review scope digest / parent invalidation
# --------------------------------------------------------------------------

class ReviewDigestTests(Phase5ATestCase):

    def test_parent_lemma_change_invalidates_every_child_review(self):
        document = editorial()
        lemma, _, _ = parts(document)
        lemma["aspect"] = "perfective"

        issues = validate_editorial(document, context())
        mismatches = [
            issue for issue in issues if issue.code == "REVIEW_STATE_MISMATCH"]
        self.assertEqual(
            2, len(mismatches),
            "a lemma-level change must invalidate both reviewed patterns")
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_parent_meaning_change_invalidates_child_reviews(self):
        document = editorial()
        _, meaning, _ = parts(document)
        meaning["glossesEn"] = ["TEST-ONLY silently restated gloss"]
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_STATE_MISMATCH")

    def test_reviewed_child_field_change_invalidates_the_stored_digest(self):
        for field, value in (
                ("learnerExplanationEn", "TEST-ONLY silently restated text."),
                ("teachingStatus", "recognition-only"),
                ("relationType", "means-method")):
            with self.subTest(field=field):
                document = editorial()
                _, _, pattern = parts(document)
                pattern[field] = value
                if field == "teachingStatus":
                    # recognition-only forbids production activities; drop them
                    # so the failure under test is the stale digest.
                    pattern["activityEligibility"] = ["reference", "search"]
                self.assertCode(
                    validate_editorial(document, context()),
                    "REVIEW_STATE_MISMATCH")

    def test_a_correctly_updated_review_lets_release_proceed_again(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY visible clarification."

        # Stale first ...
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_STATE_MISMATCH")

        # ... then correctly re-reviewed, with the owner correction that a
        # released wording change additionally requires.
        append_correction_and_review(
            document, "TEST-ONLY correction: learner explanation clarified.")
        self.assertValidEditorial(document)

        advanced = freeze_editorial(document, 2, context(), previous=baseline)
        self.assertEqual(2, advanced["patternDataRevision"])
        self.assertEqual([], validate_frozen_release(advanced))
        runtime = self.released_runtime(advanced)
        self.assertIn(
            "TEST-ONLY visible clarification",
            json.dumps(runtime, ensure_ascii=False))

    def test_scope_version_and_digest_must_both_be_current(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewEvents"][1]["scopeVersion"] = 2
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_SCOPE_VERSION")

        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewEvents"][2]["scopeDigest"] = "sha256:" + "0" * 64
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_STATE_MISMATCH")

    def test_stage_order_cannot_be_skipped(self):
        document = editorial()
        _, _, pattern = parts(document)
        del pattern["reviewEvents"][1]                # remove native review
        issues = validate_editorial(document, context())
        self.assertCode(issues, "REVIEW_STAGE_ORDER")
        self.assertCode(issues, "REVIEW_STATE_MISMATCH")

    def test_native_acceptance_requires_a_preceding_external_acceptance(self):
        """The native stage owns its own ordering rule, not just the product one."""
        document = editorial()
        _, _, pattern = parts(document)
        del pattern["reviewEvents"][0]                # remove external review
        issues = validate_editorial(document, context())
        native_order = [
            issue for issue in issues
            if issue.code == "REVIEW_STAGE_ORDER" and
            issue.path.endswith("reviewEvents[0]")]
        self.assertTrue(
            native_order,
            "an unbacked native acceptance must be refused at the native stage")

    def test_a_stale_native_digest_degrades_the_state_to_externally_verified(self):
        """The derived state is asserted exactly, not merely 'not approved'.

        If only the native acceptance goes stale, the record must fall back to
        'externally-verified' and no further -- a product approval may not carry
        it over a native review that no longer matches what it reviewed.
        """
        document = editorial()
        _, _, pattern = parts(document)
        native = next(
            event for event in pattern["reviewEvents"]
            if event["kind"] == "native-linguistic")
        native["scopeDigest"] = "sha256:" + "1" * 64

        issues = validate_editorial(document, context())
        mismatch = [
            issue for issue in issues if issue.code == "REVIEW_STATE_MISMATCH"]
        self.assertEqual(1, len(mismatch))
        self.assertIn("'externally-verified'", mismatch[0].message)

    def test_a_stale_product_digest_degrades_the_state_to_native_reviewed(self):
        document = editorial()
        _, _, pattern = parts(document)
        product = next(
            event for event in pattern["reviewEvents"]
            if event["kind"] == "product-approval")
        product["scopeDigest"] = "sha256:" + "2" * 64

        issues = validate_editorial(document, context())
        mismatch = [
            issue for issue in issues if issue.code == "REVIEW_STATE_MISMATCH"]
        self.assertEqual(1, len(mismatch))
        self.assertIn("'native-reviewed'", mismatch[0].message)

    def test_one_reviewer_cannot_silently_hold_several_stages(self):
        document = editorial()
        _, _, pattern = parts(document)
        for event in pattern["reviewEvents"]:
            event["reviewerRef"] = "test-reviewer-product-001"
        issues = validate_editorial(document, context())
        self.assertCode(issues, "REVIEWER_MULTI_ROLE_NOT_AUTHORIZED")

    def test_review_events_require_an_identified_human_reviewer(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewEvents"][1]["reviewerRef"] = "test-reviewer-unknown-999"
        self.assertCode(
            validate_editorial(document, context()),
            "REVIEWER_REGISTRY_DANGLING")

        machine_context = context()
        machine_context = ValidationContext(
            source_registry=machine_context.source_registry,
            reviewer_registry=dict(
                machine_context.reviewer_registry,
                **{"test-reviewer-native-001": {
                    "human": False, "roles": ["native-linguistic"]}}),
            author_registry=machine_context.author_registry,
            repository_index=machine_context.repository_index,
            today=machine_context.today,
        )
        self.assertCode(
            validate_editorial(editorial(), machine_context),
            "REVIEWER_NOT_HUMAN")


# --------------------------------------------------------------------------
# §15  example provenance
# --------------------------------------------------------------------------

class ExampleProvenanceTests(Phase5ATestCase):

    def test_repository_reuse_requires_the_exact_repository_source(self):
        frozen = self.baseline()
        self.assertEqual([], validate_frozen_release(frozen))

        # Wrong text for the referenced field.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][1]["pl"] = "TEST-ONLY text that is not the source."
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "REPOSITORY_SOURCE_MISMATCH")

        # Dangling source id.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][1]["origin"]["repositorySource"]["id"] = "no-such-id"
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "REPOSITORY_SOURCE_DANGLING")

        # Wrong field of the right source.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][1]["origin"]["repositorySource"]["field"] = "pl"
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "REPOSITORY_SOURCE_MISMATCH")

        # Missing repositorySource entirely.
        document = editorial()
        _, _, pattern = parts(document)
        del pattern["examples"][1]["origin"]["repositorySource"]
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "ORIGIN_REPOSITORY_REQUIRED")

    def test_repository_reuse_without_an_index_fails_closed(self):
        document = editorial()
        indexless = ValidationContext(
            source_registry=context().source_registry,
            reviewer_registry=context().reviewer_registry,
            author_registry=context().author_registry,
            repository_index=None,
            today=context().today,
        )
        self.assertCode(
            validate_editorial(document, indexless),
            "REPOSITORY_INDEX_REQUIRED")

    def test_original_example_requires_a_registered_human_author(self):
        # Missing author identity.
        document = editorial()
        _, _, pattern = parts(document)
        del pattern["examples"][0]["origin"]["authorRef"]
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()), "SCHEMA_REQUIRED")

        # Unregistered author identity.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][0]["origin"]["authorRef"] = "test-author-unknown-999"
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "AUTHOR_REGISTRY_DANGLING")

        # A non-human "author" cannot stand in for one.
        base = context()
        nonhuman = ValidationContext(
            source_registry=base.source_registry,
            reviewer_registry=base.reviewer_registry,
            author_registry={"test-author-original-001": {"human": False}},
            repository_index=base.repository_index,
            today=base.today,
        )
        self.assertCode(
            validate_editorial(editorial(), nonhuman), "AUTHOR_NOT_HUMAN")

    def test_origin_kinds_cannot_borrow_each_other_s_fields(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][0]["origin"]["repositorySource"] = {
            "kind": "card", "id": SYNTHETIC_CARD_ID, "field": "ex"}
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "ORIGIN_REPOSITORY_FORBIDDEN")

        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][1]["origin"]["authorRef"] = "test-author-original-001"
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "ORIGIN_AUTHOR_FORBIDDEN")

    def test_changing_a_released_origin_requires_an_owner_correction(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        # Convert the reused example into an original one, keeping its ID.
        pattern["examples"][1]["pl"] = "TEST-ONLY newly authored replacement."
        pattern["examples"][1]["origin"] = {
            "kind": "original",
            "authorRef": "test-author-original-001",
            "authoredAt": REVIEWED_AT,
        }
        append_review(document)
        self.assertValidEditorial(document)
        self.assertFailsWith(
            "FROZEN_WORDING_CORRECTION_REQUIRED",
            freeze_editorial, document, 2, context(), previous=baseline)


# --------------------------------------------------------------------------
# §16  activity and audio eligibility
# --------------------------------------------------------------------------

class EligibilityTests(Phase5ATestCase):

    def test_recognition_only_cannot_authorize_production_activities(self):
        for activity in ("grammar-build", "type-it"):
            with self.subTest(activity=activity):
                document = editorial()
                _, meaning, _ = parts(document)
                recognition = meaning["patterns"][1]
                self.assertEqual(
                    "recognition-only", recognition["teachingStatus"])
                recognition["activityEligibility"] = sorted(
                    recognition["activityEligibility"] + [activity])
                restamp(document)
                self.assertCode(
                    validate_editorial(document, context()),
                    "RECOGNITION_PRODUCTION_ACTIVITY")

    def test_deferred_teaching_status_cannot_expose_any_activity(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["teachingStatus"] = "deferred"
        restamp(document)
        issues = validate_editorial(document, context())
        self.assertCode(issues, "DEFERRED_ACTIVITY")

    def test_eligibility_requires_approved_review_state(self):
        document = editorial()
        research = document["lemmas"][1]["meanings"][0]["patterns"][0]
        self.assertEqual("research", research["reviewState"])
        research["activityEligibility"] = ["reference"]
        self.assertCode(
            validate_editorial(document, context()), "UNAPPROVED_ACTIVITY")

    def test_audio_requires_listening_eligibility_and_approval(self):
        # Listening removed while an example still claims audio.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["activityEligibility"] = [
            item for item in pattern["activityEligibility"]
            if item != "listening"]
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()), "AUDIO_NOT_AUTHORIZED")

        # An unapproved pattern can never carry audio.
        document = editorial()
        research = document["lemmas"][1]["meanings"][0]["patterns"][0]
        research["examples"] = [{
            "id": allocate_example_id(research["id"], "audio-attempt"),
            "key": "audio-attempt",
            "pl": "TEST-ONLY unreviewed sentence claiming audio.",
            "en": "TEST-ONLY unreviewed sentence.",
            "origin": {
                "kind": "original",
                "authorRef": "test-author-original-001",
                "authoredAt": REVIEWED_AT,
            },
            "audioEligible": True,
        }]
        self.assertCode(
            validate_editorial(document, context()), "AUDIO_NOT_AUTHORIZED")

    def test_active_grammar_and_listening_require_a_reviewed_example(self):
        document = editorial()
        _, meaning, _ = parts(document)
        recognition = meaning["patterns"][1]
        recognition["activityEligibility"] = sorted(
            recognition["activityEligibility"] + ["grammar-choose"])
        restamp(document)
        self.assertCode(
            validate_editorial(document, context()),
            "ACTIVITY_EXAMPLE_REQUIRED")

    def test_eligibility_defaults_closed_and_survives_projection_exactly(self):
        frozen = self.baseline()
        runtime = self.released_runtime(frozen)
        by_id = {
            pattern["id"]: pattern
            for lemma in runtime["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        }
        document = editorial()
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] in by_id:
                        self.assertEqual(
                            sorted(pattern["activityEligibility"]),
                            by_id[pattern["id"]]["activityEligibility"])
        # The unreviewed lemma contributes no eligibility at all, because it
        # contributes nothing to the runtime.
        self.assertEqual(1, len(runtime["lemmas"]))


# --------------------------------------------------------------------------
# §17  freeze versus review ordering
# --------------------------------------------------------------------------

class FreezeReviewOrderTests(Phase5ATestCase):

    def test_unreviewed_data_cannot_be_frozen_as_approved(self):
        document = editorial()
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["reviewState"] == "approved":
                        pattern["reviewEvents"] = []
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_research_only_document_cannot_produce_a_release(self):
        document = editorial()
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    pattern["reviewState"] = "research"
                    pattern["reviewEvents"] = []
                    pattern["activityEligibility"] = []
                    for example in pattern.get("examples", []):
                        example["audioEligible"] = False
        self.assertValidEditorial(document)
        self.assertFailsWith(
            "PROJECTION_EMPTY", project_runtime_nonrelease, document, 1,
            context())
        self.assertFailsWith(
            "PROJECTION_EMPTY", freeze_editorial, document, 1, context())

    def test_approve_then_mutate_cannot_retain_release_authorization(self):
        """The only safe ordering is: change, re-review, then freeze."""
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY post-approval edit."

        # Order 1 -- mutate and freeze: refused, the review is stale.
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH",
            freeze_editorial, document, 2, context(), previous=baseline)

        # Order 2 -- mutate, re-review, freeze, but with no owner correction:
        # still refused, because the wording was already released.
        append_review(document)
        self.assertValidEditorial(document)
        self.assertFailsWith(
            "FROZEN_WORDING_CORRECTION_REQUIRED",
            freeze_editorial, document, 2, context(), previous=baseline)

        # Order 3 -- mutate, correct, re-review, freeze: accepted.
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY post-approval edit."
        append_correction_and_review(
            document, "TEST-ONLY owner correction authorising the edit.")
        advanced = freeze_editorial(document, 2, context(), previous=baseline)
        self.assertEqual([], validate_frozen_release(advanced))

    def test_released_review_history_must_stay_an_append_only_prefix(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewEvents"] = acceptance_events(
            *parts(document), reviewed_at=LATER_REVIEWED_AT)
        self.assertValidEditorial(document)
        self.assertFailsWith(
            "FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY",
            freeze_editorial, document, 1, context(), previous=baseline)

    def test_a_terminal_rejection_cannot_be_reopened_without_authority(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewState"] = "rejected"
        pattern["reviewEvents"] = pattern["reviewEvents"][:1] + [{
            "kind": "native-linguistic",
            "decision": "reject",
            "reviewerRef": "test-reviewer-native-001",
            "reviewedAt": REVIEWED_AT,
            "note": "TEST-ONLY synthetic rejection.",
        }]
        pattern["activityEligibility"] = []
        for example in pattern["examples"]:
            example["audioEligible"] = False
        self.assertValidEditorial(document)

        # A rejected treatment cannot simply take another stage event.
        document["lemmas"][0]["meanings"][0]["patterns"][0][
            "reviewEvents"].append({
                "kind": "native-linguistic",
                "decision": "accept",
                "scopeVersion": 1,
                "scopeDigest": review_scope_digest(
                    "native-linguistic", *parts(document)),
                "reviewerRef": "test-reviewer-native-001",
                "reviewedAt": LATER_REVIEWED_AT,
            })
        self.assertCode(
            validate_editorial(document, context()), "REVIEW_REOPEN_REQUIRED")


# --------------------------------------------------------------------------
# §18  patternDataRevision contract
# --------------------------------------------------------------------------

class RevisionTests(Phase5ATestCase):

    def test_first_synthetic_release_is_revision_one(self):
        self.assertEqual(1, self.baseline()["patternDataRevision"])
        for wrong in (0, 2, 3, -1):
            with self.subTest(revision=wrong):
                if wrong < 1:
                    self.assertFailsWith(
                        "FROZEN_REVISION", freeze_editorial, editorial(),
                        wrong, context())
                else:
                    self.assertFailsWith(
                        "FROZEN_INITIAL_REVISION", freeze_editorial,
                        editorial(), wrong, context())

    def test_identical_reprojection_keeps_the_same_revision(self):
        baseline = self.baseline()
        again = freeze_editorial(
            editorial(), 1, context(), previous=baseline)
        self.assertEqual(1, again["patternDataRevision"])
        self.assertEqual(
            baseline["runtimeProjection"], again["runtimeProjection"])

        # An unchanged payload may not advance the revision either.
        self.assertFailsWith(
            "FROZEN_REVISION_TRANSITION", freeze_editorial,
            editorial(), 2, context(), previous=baseline)

    def test_changed_public_payload_advances_the_revision_by_exactly_one(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY public change."
        append_correction_and_review(
            document, "TEST-ONLY correction for a public wording change.")

        self.assertFailsWith(
            "FROZEN_REVISION_TRANSITION", freeze_editorial, document, 1,
            context(), previous=baseline)
        advanced = freeze_editorial(document, 2, context(), previous=baseline)
        self.assertEqual(2, advanced["patternDataRevision"])

    def test_private_only_change_keeps_the_previous_revision(self):
        """Determined from the implementation, not assumed.

        freeze_editorial compares the revision-stripped runtimeProjection only.
        A change confined to private editorial metadata therefore leaves the
        public payload identical and the revision exactly where it was.
        """
        baseline = self.baseline()
        document = editorial()
        _, meaning, _ = parts(document)
        meaning["internalScope"] += " TEST-ONLY private clarification."
        append_correction_and_review(
            document, "TEST-ONLY correction for a private-scope change.")

        advanced = freeze_editorial(document, 1, context(), previous=baseline)
        self.assertEqual(1, advanced["patternDataRevision"])
        self.assertEqual(
            baseline["runtimeProjection"], advanced["runtimeProjection"])
        # The private dimension really did change, so this is not a no-op.
        self.assertNotEqual(baseline["wording"], advanced["wording"])
        # And claiming an advance for a private-only change is refused.
        self.assertFailsWith(
            "FROZEN_REVISION_TRANSITION", freeze_editorial, document, 2,
            context(), previous=baseline)

    def test_illegal_revision_skip_is_refused(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY public change."
        append_correction_and_review(
            document, "TEST-ONLY correction for a public wording change.")
        for skipped in (3, 4, 42):
            with self.subTest(revision=skipped):
                self.assertFailsWith(
                    "FROZEN_REVISION_TRANSITION", freeze_editorial, document,
                    skipped, context(), previous=baseline)

    def test_multi_release_sequence_advances_one_step_at_a_time(self):
        first = self.baseline()
        second_document = editorial()
        _, _, pattern = parts(second_document)
        pattern["learnerExplanationEn"] += " TEST-ONLY change one."
        append_correction_and_review(second_document, "TEST-ONLY correction 1.")
        second = freeze_editorial(
            second_document, 2, context(), previous=first)

        third_document = copy.deepcopy(second_document)
        _, _, pattern = parts(third_document)
        pattern["learnerExplanationEn"] += " TEST-ONLY change two."
        append_correction_and_review(third_document, "TEST-ONLY correction 2.")
        third = freeze_editorial(
            third_document, 3, context(), previous=second)

        self.assertEqual([1, 2, 3], [
            frozen["patternDataRevision"] for frozen in (first, second, third)])
        self.assertEqual([], validate_frozen_release(third))
        self.assertEqual(
            3, self.released_runtime(third)["patternDataRevision"])


# --------------------------------------------------------------------------
# §19/§20  public projection privacy and public runtime validation
# --------------------------------------------------------------------------

class PublicProjectionPrivacyTests(Phase5ATestCase):

    def released(self):
        return self.released_runtime(self.baseline())

    def test_public_runtime_top_level_is_exactly_the_three_public_keys(self):
        runtime = self.released()
        self.assertEqual(
            ["formatVersion", "lemmas", "patternDataRevision"], sorted(runtime))

    def test_no_private_key_appears_at_any_depth(self):
        runtime = self.released()
        found = [
            path for path, key, _ in walk(runtime)
            if key in PRIVATE_RUNTIME_KEYS]
        self.assertEqual([], found)

    def test_no_private_value_appears_anywhere_in_the_serialized_runtime(self):
        runtime = self.released()
        serialized = json.dumps(runtime, ensure_ascii=False)
        data = payload()
        identities = data["syntheticIdentities"]

        leaks = []
        for reference in list(identities["reviewerRegistry"]) + list(
                identities["authorRegistry"]) + list(
                identities["sourceRegistry"]):
            if reference in serialized:
                leaks.append(reference)

        # Only genuinely private prose is checked here.  `usage.note` is a
        # deliberate PUBLIC field (see _project_usage), so a blanket "no key
        # called note" sweep would assert something the contract never claimed.
        document = editorial()
        private_prose = set()
        for _, key, value in walk(document):
            if key in {"evidence", "reviewEvents"} and isinstance(value, list):
                for record in value:
                    if not isinstance(record, dict):
                        continue
                    for field in ("locator", "note", "scopeDigest",
                                  "reviewedAt", "checkedAt", "sourceId",
                                  "reviewerRef"):
                        if isinstance(record.get(field), str):
                            private_prose.add(record[field])
            if key == "internalScope" and isinstance(value, str):
                private_prose.add(value)
            if key == "origin" and isinstance(value, dict):
                for field in ("authorRef", "authoredAt"):
                    if isinstance(value.get(field), str):
                        private_prose.add(value[field])
        self.assertTrue(private_prose)
        leaks.extend(item for item in private_prose if item in serialized)
        self.assertEqual([], leaks)

        # Categorically: no digest, freeze metadata or tombstone marker.
        for marker in ("sha256:", FROZEN_ARTIFACT_STATUS,
                       "priority-7-editorial-nonproduction", "tombstone",
                       "retirementRevision", "allocations", "reviewHistory"):
            self.assertNotIn(marker, serialized)

    def test_unreviewed_and_research_material_never_reaches_the_public_runtime(self):
        runtime = self.released()
        serialized = json.dumps(runtime, ensure_ascii=False)
        document = editorial()
        research_lemma = document["lemmas"][1]
        self.assertNotIn(research_lemma["id"], serialized)
        self.assertNotIn(research_lemma["canonicalLemma"], serialized)
        self.assertEqual(
            approved_pattern_ids(document),
            {pattern["id"]
             for lemma in runtime["lemmas"]
             for meaning in lemma["meanings"]
             for pattern in meaning["patterns"]})

    def test_public_validator_is_a_second_check_not_the_only_privacy_proof(self):
        runtime = self.released()
        self.assertEqual([], validate_runtime(runtime))
        for key in sorted(PRIVATE_RUNTIME_KEYS):
            with self.subTest(private_key=key):
                injected = copy.deepcopy(runtime)
                injected["lemmas"][0]["meanings"][0]["patterns"][0][key] = (
                    "TEST-ONLY injected private value")
                self.assertNotEqual(
                    [], validate_runtime(injected),
                    f"private key {key!r} must be refused")

    def test_malformed_nested_public_structures_are_refused(self):
        runtime = self.released()
        cases = {
            "null patterns": lambda value: value["lemmas"][0]["meanings"][0]
                .__setitem__("patterns", None),
            "string lemmas": lambda value: value.__setitem__("lemmas", "no"),
            "empty lemmas": lambda value: value.__setitem__("lemmas", []),
            "bad complement case": lambda value: value["lemmas"][0]["meanings"]
                [0]["patterns"][0]["complements"][0].__setitem__(
                    "case", "not-a-case"),
            "bad teaching status": lambda value: value["lemmas"][0]["meanings"]
                [0]["patterns"][0].__setitem__("teachingStatus", "deferred"),
            "float revision": lambda value: value.__setitem__(
                "patternDataRevision", 1.0),
            "zero revision": lambda value: value.__setitem__(
                "patternDataRevision", 0),
            "wrong format version": lambda value: value.__setitem__(
                "formatVersion", 2),
            "extra envelope key": lambda value: value.__setitem__(
                "releaseAuthorized", True),
        }
        for name, mutate in cases.items():
            with self.subTest(case=name):
                candidate = copy.deepcopy(runtime)
                mutate(candidate)
                self.assertNotEqual([], validate_runtime(candidate))


# --------------------------------------------------------------------------
# §21/§22  the Python -> JS bridge into the Phase 3F-A shipping loader
# --------------------------------------------------------------------------

class LoaderBridgeTests(Phase5ATestCase):
    """Feed the ACTUAL release-authoritative projection to the shipping loader.

    Nothing is rewritten into a hand-authored loader fixture on the way: the
    bytes the Python release-authoritative path produced are the bytes the
    JavaScript consumer parses.
    """

    @classmethod
    def setUpClass(cls):
        cls.frozen = freeze_editorial(editorial(), 1, context())
        cls.runtime = verified_runtime_from_frozen(cls.frozen)
        cls.temporary = tempfile.TemporaryDirectory(prefix="p7-phase5a-")
        cls.runtime_path = Path(cls.temporary.name) / "synthetic-runtime.json"
        cls.runtime_path.write_text(
            json.dumps(cls.runtime, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def drive_loader(self, mutation="none"):
        completed = subprocess.run(
            ["osascript", "-l", "JavaScript", str(LOADER_HARNESS), str(ROOT),
             str(self.runtime_path), mutation],
            capture_output=True, text=True, check=False, cwd=ROOT)
        self.assertEqual(
            0, completed.returncode,
            f"loader harness failed: {completed.stderr}")
        return json.loads(completed.stdout)

    def test_1_to_7_release_authoritative_output_reaches_the_shipping_loader(self):
        result = self.drive_loader()

        # 1. the release-authoritative projector emitted a public runtime
        self.assertEqual(self.frozen["runtimeProjection"], self.runtime)
        # 2. it passes the Python public validator
        self.assertEqual([], validate_runtime(self.runtime))
        # 3. the Phase 3F-A shipping loader accepts it
        self.assertIs(True, result["settled"])
        # 4. availability flips only after acceptance
        self.assertIs(False, result["availableBeforeLoad"])
        self.assertIs(True, result["available"])
        # 5. index and summary derive from it
        self.assertEqual({"lemmas": 1, "patterns": 2}, result["summary"])
        self.assertEqual("1 verb · 2 patterns", result["countLabel"])
        self.assertIs(True, result["hasIndex"])
        self.assertEqual(
            ["ZORBULATE — TEST-ONLY SYNTHETIC"], result["indexLemmas"])
        self.assertEqual([2], result["indexPatternCounts"])
        self.assertEqual(1, result["allRowCount"])
        self.assertEqual(
            ["all", "accusative", "no-case"], result["filterIds"])
        # the projected contentRef resolves the card-back cross-link
        self.assertEqual("doorway", result["cardSupport"]["state"])
        self.assertEqual("none", result["unknownCardSupport"]["state"])
        # 6. no private state entered the shipping runtime
        self.assertIs(False, result["holdsPrivateKey"])
        # 7. exactly one no-store transport call, and nothing persisted
        self.assertEqual(1, result["requestCount"])
        self.assertEqual("no-store", result["requestCache"])

    def test_loader_refuses_every_negative_bridge_case(self):
        negatives = [
            "private-review-state", "private-evidence", "private-origin-deep",
            "private-key-field", "extra-envelope-key", "nonrelease-wrapper",
            "malformed-complement", "malformed-nested-null",
            "malformed-example", "revision-zero", "revision-not-integer",
            "format-version-drift", "empty-lemmas",
        ]
        for mutation in negatives:
            with self.subTest(mutation=mutation):
                result = self.drive_loader(mutation)
                self.assertIs(
                    False, result["settled"],
                    f"{mutation} must not be accepted")
                self.assertIs(False, result["available"])
                self.assertEqual({"lemmas": 0, "patterns": 0}, result["summary"])

    def test_cross_language_contract_constants_agree(self):
        """§22: the same enumerations must not drift between the two languages.

        ``PRIVATE_RUNTIME_KEYS`` stays exactly what the shipping loader
        mirrors, so this equality is untouched by Phase 4E.  The Phase 4E
        governance vocabulary is layered in ``FORBIDDEN_RUNTIME_KEYS``
        instead and asserted separately below.
        """
        result = self.drive_loader()
        from priority7_tooling import CASE_IDS, FORMAT_VERSION

        self.assertEqual(FORMAT_VERSION, result["formatVersion"])
        self.assertEqual(
            ["formatVersion", "patternDataRevision", "lemmas"],
            result["envelopeKeys"])
        self.assertEqual(CASE_IDS, set(result["caseOrder"]))

        # The JS private-key rejection list mirrors PRIVATE_RUNTIME_KEYS.
        source = (ROOT / "pp-verb-patterns.js").read_text(encoding="utf-8")
        start = source.index("var PRIVATE_KEYS = [")
        block = source[start:source.index("];", start)]
        js_keys = set(json.loads(
            "[" + block[block.index("[") + 1:].replace("\n", " ") + "]"))
        self.assertEqual(PRIVATE_RUNTIME_KEYS, js_keys)
        self.assertEqual(
            PRIVATE_RUNTIME_KEYS | GOVERNANCE_PRIVATE_KEYS,
            FORBIDDEN_RUNTIME_KEYS)
        self.assertEqual(
            set(), PRIVATE_RUNTIME_KEYS & GOVERNANCE_PRIVATE_KEYS)

    def test_governance_keys_have_nowhere_to_appear_in_a_runtime_document(self):
        """The reason the shipping loader needs no Phase 4E extension.

        The runtime schema is closed at every level, so injecting any Phase 4E
        governance key into an otherwise valid released runtime document is
        refused outright -- by the generic unknown-field rule, before the
        private-key sweep is even consulted.
        """
        frozen = self.baseline()
        for key in sorted(GOVERNANCE_PRIVATE_KEYS):
            for injection_point in ("envelope", "lemma", "pattern"):
                with self.subTest(key=key, at=injection_point):
                    runtime = self.released_runtime(frozen)
                    target = runtime
                    if injection_point == "lemma":
                        target = runtime["lemmas"][0]
                    elif injection_point == "pattern":
                        target = runtime["lemmas"][0]["meanings"][0]["patterns"][0]
                    target[key] = "leaked"
                    issues = validate_runtime(runtime)
                    self.assertTrue(issues, f"{key} must not be accepted")
                    self.assertIn(
                        "SCHEMA_UNKNOWN_FIELD",
                        [issue.code for issue in issues])

    def test_bridge_creates_no_repository_runtime_artifact(self):
        released = PUBLIC_RUNTIME.read_bytes() if PUBLIC_RUNTIME.is_file() else None
        self.drive_loader()
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path is
        # exactly the I1 release artifact, pinned by digest and revision, and it
        # may only exist alongside the matching shell and worker.  Nothing about
        # the synthetic Phase 5-A bridge may reach it.
        self.assertEqual("complete", i1_bundle().state)
        # Driving the synthetic bridge changed nothing at that path.
        self.assertEqual(
            released,
            PUBLIC_RUNTIME.read_bytes() if PUBLIC_RUNTIME.is_file() else None)
        self.assertTrue(
            str(self.runtime_path).startswith(tempfile.gettempdir()),
            "the generated runtime must live outside the repository")


# --------------------------------------------------------------------------
# §23  the negative end-to-end matrix, restated as one table
# --------------------------------------------------------------------------

class NegativeMatrixTests(Phase5ATestCase):

    def test_A_research_only_record_cannot_be_released(self):
        document = editorial()
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    pattern["reviewState"] = "research"
                    pattern["reviewEvents"] = []
                    pattern["activityEligibility"] = []
                    for example in pattern.get("examples", []):
                        example["audioEligible"] = False
        self.assertFailsWith(
            "PROJECTION_EMPTY", freeze_editorial, document, 1, context())

    def test_B_missing_native_review_blocks_release(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["reviewEvents"] = [
            event for event in pattern["reviewEvents"]
            if event["kind"] != "native-linguistic"]
        self.assertFailsWith(
            "REVIEW_STAGE_ORDER", freeze_editorial, document, 1, context())

    def test_C_stale_evidence_digest_blocks_release(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["evidence"][0]["checkedAt"] = "2026-08-07"
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_D_stale_review_digest_blocks_release(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["usage"]["register"] = "formal"
        self.assertFailsWith(
            "REVIEW_STATE_MISMATCH", freeze_editorial, document, 1, context())

    def test_E_invalid_or_missing_frozen_allocation_blocks_release(self):
        frozen = self.baseline()
        stripped = copy.deepcopy(frozen)
        stripped["allocations"] = []
        self.assertFailsWith(
            "FROZEN_IDENTITY_UNALLOCATED", verified_runtime_from_frozen,
            stripped)

        corrupted = copy.deepcopy(frozen)
        corrupted["allocations"][0]["seed"] = "v1|lemma|forged"
        self.assertNotEqual([], validate_frozen_release(corrupted))

    def test_F_tombstoned_id_reuse_blocks_release(self):
        baseline = self.baseline()
        document = editorial()
        _, meaning, _ = parts(document)
        retired_id = meaning["patterns"].pop(1)["id"]
        retired = freeze_editorial(
            document, 2, context(), previous=baseline, tombstones=[{
                "id": retired_id,
                "kind": "pattern",
                "formerParentId": meaning["id"],
                "retirementRevision": 2,
                "reason": "TEST-ONLY synthetic retirement.",
                "replacementIds": [],
            }])
        self.assertFailsWith(
            "TOMBSTONE_RESURRECTION", freeze_editorial, editorial(),
            3, context(), previous=retired)

    def test_G_invalid_example_provenance_blocks_release(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][1]["origin"]["repositorySource"]["id"] = "wrong-id"
        restamp(document)
        self.assertFailsWith(
            "REPOSITORY_SOURCE_DANGLING", freeze_editorial, document, 1,
            context())

        document = editorial()
        _, _, pattern = parts(document)
        pattern["examples"][0]["origin"]["authorRef"] = "test-author-missing"
        restamp(document)
        self.assertFailsWith(
            "AUTHOR_REGISTRY_DANGLING", freeze_editorial, document, 1,
            context())

    def test_H_eligibility_violating_status_blocks_release(self):
        document = editorial()
        _, meaning, _ = parts(document)
        meaning["patterns"][1]["activityEligibility"] = sorted(
            meaning["patterns"][1]["activityEligibility"] + ["type-it"])
        restamp(document)
        self.assertFailsWith(
            "RECOGNITION_PRODUCTION_ACTIVITY", freeze_editorial, document, 1,
            context())

    def test_I_private_field_injected_into_runtime_fails_public_validation(self):
        runtime = self.released_runtime(self.baseline())
        injected = copy.deepcopy(runtime)
        injected["lemmas"][0]["meanings"][0]["reviewState"] = "approved"
        issues = validate_runtime(injected)
        self.assertCode(issues, "RUNTIME_PRIVATE_FIELD")

    def test_J_payload_change_without_a_correct_revision_advance_fails(self):
        baseline = self.baseline()
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY changed payload."
        append_correction_and_review(document, "TEST-ONLY correction.")
        self.assertFailsWith(
            "FROZEN_REVISION_TRANSITION", freeze_editorial, document, 1,
            context(), previous=baseline)

    def test_matrix_coverage_is_complete_and_honest(self):
        """Every lettered case above is enforced; none is documented-only."""
        cases = sorted(
            name.split("_")[1] for name in dir(self)
            if name.startswith("test_") and len(name.split("_")) > 1 and
            len(name.split("_")[1]) == 1)
        self.assertEqual(
            list("ABCDEFGHIJ"), cases,
            "the negative matrix must cover A through J")


# --------------------------------------------------------------------------
# §24/§25  atomicity: a failed candidate produces no artifact and no writes
# --------------------------------------------------------------------------

class AtomicityTests(Phase5ATestCase):

    def test_failed_release_returns_no_result_at_all(self):
        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY stale edit."
        with self.assertRaises(ValidationFailure) as caught:
            freeze_editorial(document, 1, context())
        self.assertTrue(caught.exception.issues)
        # There is no partially built envelope to inspect: the call raised.
        self.assertNotIn("runtimeProjection", dir(caught.exception))

    def test_failed_release_does_not_mutate_its_inputs(self):
        baseline = self.baseline()
        baseline_bytes = json.dumps(baseline, sort_keys=True)

        document = editorial()
        _, _, pattern = parts(document)
        pattern["learnerExplanationEn"] += " TEST-ONLY stale edit."
        document_bytes = json.dumps(document, sort_keys=True)

        with self.assertRaises(ValidationFailure):
            freeze_editorial(document, 2, context(), previous=baseline)

        self.assertEqual(baseline_bytes, json.dumps(baseline, sort_keys=True))
        self.assertEqual(document_bytes, json.dumps(document, sort_keys=True))

    def test_a_good_snapshot_survives_a_later_failed_transition(self):
        baseline = self.baseline()
        good_runtime = self.released_runtime(baseline)

        broken = editorial()
        _, _, pattern = parts(broken)
        pattern["evidence"][0]["locator"] += "/broken"
        with self.assertRaises(ValidationFailure):
            freeze_editorial(broken, 2, context(), previous=baseline)

        # The previous good snapshot is untouched and still releasable.
        self.assertEqual([], validate_frozen_release(baseline))
        self.assertEqual(good_runtime, self.released_runtime(baseline))

    def test_the_release_authoritative_path_writes_no_files(self):
        """§25: the freeze/projection tooling is pure and in-memory.

        Proven mechanically rather than asserted: every filesystem write
        primitive is replaced with a trap for the duration of the call.
        """
        document = editorial()
        validation_context = context()

        def trap(*arguments, **keywords):
            raise AssertionError(
                "the release-authoritative path attempted a filesystem write")

        original_open = builtins.open
        original_write_text = pathlib.Path.write_text
        original_write_bytes = pathlib.Path.write_bytes
        original_replace = os.replace
        original_rename = os.rename

        def guarded_open(file, mode="r", *arguments, **keywords):
            if any(flag in mode for flag in ("w", "a", "x", "+")):
                trap()
            return original_open(file, mode, *arguments, **keywords)

        builtins.open = guarded_open
        pathlib.Path.write_text = trap
        pathlib.Path.write_bytes = trap
        os.replace = trap
        os.rename = trap
        try:
            frozen = freeze_editorial(document, 1, validation_context)
            runtime = verified_runtime_from_frozen(frozen)
            standalone = project_runtime_nonrelease(
                document, 1, validation_context)
        finally:
            builtins.open = original_open
            pathlib.Path.write_text = original_write_text
            pathlib.Path.write_bytes = original_write_bytes
            os.replace = original_replace
            os.rename = original_rename

        self.assertEqual(runtime, standalone)
        self.assertEqual([], validate_runtime(runtime))

    def test_only_the_nonrelease_cli_can_write_and_only_where_told(self):
        """The one writing entry point is explicitly nonrelease."""
        import priority7_tooling

        with tempfile.TemporaryDirectory(prefix="p7-phase5a-cli-") as folder:
            source = Path(folder) / "editorial.json"
            source.write_text(
                json.dumps(editorial(), ensure_ascii=False), encoding="utf-8")
            context_file = Path(folder) / "context.json"
            data = payload()
            context_file.write_text(json.dumps({
                "sourceRegistry": data["syntheticIdentities"]["sourceRegistry"],
                "reviewerRegistry": data["syntheticIdentities"][
                    "reviewerRegistry"],
                "authorRegistry": data["syntheticIdentities"]["authorRegistry"],
                "today": data["reviewContextDate"],
            }, ensure_ascii=False), encoding="utf-8")
            output = Path(folder) / "projection.json"

            code = priority7_tooling.main([
                "project-fixture", str(source),
                "--test-pattern-data-revision", "1",
                "--context", str(context_file),
                "--output", str(output),
            ])

            if code == 0:
                written = json.loads(output.read_text(encoding="utf-8"))
                self.assertEqual(
                    NONRELEASE_PROJECTION_STATUS, written["artifactStatus"])
                self.assertIs(False, written["releaseAuthorized"])
            else:
                # Repository reuse needs a repository root; either way the CLI
                # never emits a release-authoritative artifact.
                self.assertFalse(output.exists())
        # The nonrelease CLI cannot have written the official runtime: what is
        # there is exactly the Phase 4F-I1 release artifact, and the CLI marks
        # everything it writes as explicitly non-release.
        self.assertEqual("complete", i1_bundle().state)


# --------------------------------------------------------------------------
# Phase 4E  the same machinery, driven by the solo-maintainer release mode
# --------------------------------------------------------------------------

def solo_acceptance_events(lemma, meaning, pattern, reviewed_at=REVIEWED_AT):
    """The Phase 4E chain: reference check, editorial review, owner approval."""
    pins = sorted({
        evidence_digest(record) for record in pattern["evidence"]
        if record["sourceKind"] in {
            "contemporary-reference", "contemporary-corpus"}
    })
    return [
        {
            "kind": "reference-verification",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "reference-verification", lemma, meaning, pattern),
            "supportingEvidenceDigests": pins,
            # Phase 4E.1: reference verification is performed by the project's
            # own nonhuman source-analysis workflow, not by a human reviewer.
            "actorRef": "test-actor-reference-analysis-001",
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "editorial-review",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "editorial-review", lemma, meaning, pattern),
            "actorRef": "test-actor-editorial-001",
            "corroboratingActorRefs": ["test-actor-editorial-002"],
            "reviewedAt": reviewed_at,
        },
        {
            "kind": "product-approval",
            "decision": "accept",
            "scopeVersion": 1,
            "scopeDigest": review_scope_digest(
                "product-approval", lemma, meaning, pattern),
            "reviewerRef": "test-reviewer-owner-001",
            "reviewedAt": reviewed_at,
        },
    ]


def solo_editorial():
    """The synthetic release re-governed under the solo-maintainer mode.

    The human-authored example becomes a truthfully labelled editorially
    generated one, because that is what the amended workflow produces.
    """
    document = editorial()
    for lemma in document["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                if pattern.get("reviewState") != "approved":
                    continue
                pattern["releaseMode"] = "solo-maintainer-reference-backed"
                for example in pattern.get("examples", []):
                    if example["origin"]["kind"] == "original":
                        example["origin"] = {
                            "kind": "editorial-generated",
                            "generatorRef": "test-actor-editorial-001",
                            "adoptedAt": REVIEWED_AT,
                        }
                pattern["reviewEvents"] = solo_acceptance_events(
                    lemma, meaning, pattern)
    return document


class SoloMaintainerReleasePathTests(Phase5ATestCase):
    """Phase 4E: the solo-maintainer chain travels the same real machinery.

    This is the sibling of the human-reviewed rehearsal above, not a
    replacement for it.  Both modes are proven here, so retiring the human
    chain is never a silent consequence of adopting the other one.
    """

    def test_the_solo_release_freezes_projects_and_validates(self):
        document = solo_editorial()
        self.assertValidEditorial(document)
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        runtime = verified_runtime_from_frozen(frozen)
        self.assertEqual([], validate_runtime(runtime))
        self.assertEqual(frozen["runtimeProjection"], runtime)

    def test_both_modes_project_the_identical_public_runtime(self):
        """Governance decides what may ship, never what shipping looks like."""
        human = self.baseline()
        solo = freeze_editorial(solo_editorial(), 1, context())
        self.assertEqual(
            self.released_runtime(human), self.released_runtime(solo))

    def test_the_two_modes_are_distinguishable_in_the_release_envelope(self):
        human = self.baseline()
        solo = freeze_editorial(solo_editorial(), 1, context())
        self.assertEqual(
            ["human-reviewed"], human["releaseAuthorization"]["releaseModes"])
        self.assertEqual(
            ["solo-maintainer-reference-backed"],
            solo["releaseAuthorization"]["releaseModes"])
        self.assertTrue(
            human["releaseAuthorization"]["humanNativeReviewedPatternIds"])
        self.assertEqual(
            [], solo["releaseAuthorization"]["humanNativeReviewedPatternIds"])
        # Phase 4E.1: the human chain's tier-1 verifier is a person and the
        # solo chain's is not, and the envelope says so per pattern rather
        # than leaving a reader to infer it from the mode name.
        self.assertTrue(
            human["releaseAuthorization"]["humanVerifiedPatternIds"])
        self.assertEqual(
            [], solo["releaseAuthorization"]["humanVerifiedPatternIds"])

    def test_solo_freeze_keeps_identical_allocations_and_stable_ids(self):
        human = self.baseline()
        solo = freeze_editorial(solo_editorial(), 1, context())
        self.assertEqual(human["allocations"], solo["allocations"])
        self.assertEqual(human["identity"], solo["identity"])
        self.assertEqual(human["structure"], solo["structure"])
        self.assertEqual(human["wording"], solo["wording"])

    def test_solo_freeze_supports_tombstones_and_revision_advance(self):
        """The retirement machinery is mode-independent."""
        baseline = freeze_editorial(solo_editorial(), 1, context())
        document = solo_editorial()
        lemma, meaning, _ = parts(document)
        retired = meaning["patterns"].pop()
        advanced = freeze_editorial(
            document, 2, context(), previous=baseline,
            tombstones=[{
                "id": retired["id"],
                "kind": "pattern",
                "formerParentId": meaning["id"],
                "retirementRevision": 2,
                "reason": "TEST-ONLY invented synthetic retirement.",
                "replacementIds": [],
            }])
        self.assertEqual([], validate_frozen_release(advanced))
        self.assertEqual(2, advanced["patternDataRevision"])
        self.assertEqual(
            [retired["id"]], [row["id"] for row in advanced["tombstones"]])
        self.assertIn(
            retired["id"], {row["id"] for row in advanced["allocations"]})

    def test_a_solo_release_carries_no_private_governance_into_runtime(self):
        runtime = self.released_runtime(
            freeze_editorial(solo_editorial(), 1, context()))
        for path, key, value in walk(runtime):
            with self.subTest(path=path):
                self.assertNotIn(key, FORBIDDEN_RUNTIME_KEYS)
        blob = json.dumps(runtime, ensure_ascii=False)
        for token in ("solo-maintainer-reference-backed", "editorial-review",
                      "reference-verification", "editorial-generated",
                      "test-actor-editorial-001", "test-reviewer-owner-001",
                      "test-actor-reference-analysis-001"):
            with self.subTest(token=token):
                self.assertNotIn(token, blob)

    def test_the_nonrelease_cli_projection_still_refuses_to_look_released(self):
        projected = project_nonrelease_fixture(solo_editorial(), 424242, context())
        self.assertEqual(NONRELEASE_PROJECTION_STATUS, projected["artifactStatus"])
        self.assertIs(False, projected["releaseAuthorized"])


class DuplicateStageAcceptanceTests(Phase5ATestCase):
    """Phase 4E repair: a repeated stage acceptance cannot travel this path.

    Proven against the real freeze/projection machinery rather than against the
    validator alone, because the defect this covers originally survived
    editorial validation, freeze *and* frozen validation, and produced an
    authoritative runtime document.
    """

    def duplicate_at(self, document, tier, builder):
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern.get("reviewState") != "approved":
                        continue
                    chain = builder(lemma, meaning, pattern)
                    events = list(chain)
                    events.insert(tier + 1, copy.deepcopy(chain[tier]))
                    pattern["reviewEvents"] = events
        return document

    def test_no_duplicated_stage_survives_the_release_path_in_either_mode(self):
        for label, document_factory, builder in (
                ("human-reviewed", editorial, acceptance_events),
                ("solo-maintainer", solo_editorial, solo_acceptance_events)):
            for tier in range(3):
                with self.subTest(mode=label, tier=tier):
                    document = self.duplicate_at(
                        document_factory(), tier, builder)
                    issues = validate_editorial(document, context())
                    self.assertIn(
                        "REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                        [issue.code for issue in issues])
                    self.assertFailsWith(
                        "REVIEW_DUPLICATE_STAGE_ACCEPTANCE",
                        freeze_editorial, document, 1, context())

    def test_re_review_after_a_real_change_still_freezes_and_projects(self):
        """The repair must not have closed the legitimate re-review path."""
        document = solo_editorial()
        for lemma in document["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern.get("reviewState") != "approved":
                        continue
                    pattern["learnerExplanationEn"] += " TEST-ONLY re-review."
                    pattern["reviewEvents"] = pattern["reviewEvents"] + (
                        solo_acceptance_events(
                            lemma, meaning, pattern, LATER_REVIEWED_AT))
        self.assertValidEditorial(document)
        frozen = freeze_editorial(document, 1, context())
        self.assertEqual([], validate_frozen_release(frozen))
        self.assertEqual([], validate_runtime(self.released_runtime(frozen)))


class MalformedReleaseModeTests(Phase5ATestCase):
    """Phase 4E repair: no malformed mode may crash a tooling entry point."""

    MALFORMED = (None, True, 1, 1.5, [], {}, ["human-reviewed"],
                 {"mode": "human-reviewed"}, "", "unknown-mode")

    def test_every_malformed_mode_is_refused_without_an_exception(self):
        for value in self.MALFORMED:
            with self.subTest(value=repr(value)):
                document = solo_editorial()
                for lemma in document["lemmas"]:
                    for meaning in lemma["meanings"]:
                        for pattern in meaning["patterns"]:
                            if pattern.get("reviewState") == "approved":
                                pattern["releaseMode"] = copy.deepcopy(value)
                issues = validate_editorial(document, context())
                self.assertIn(
                    "SCHEMA_ENUM", [issue.code for issue in issues])
                self.assertFailsWith(
                    "SCHEMA_ENUM", freeze_editorial, document, 1, context())

    def test_the_nonrelease_projector_also_refuses_a_malformed_mode(self):
        """Every public entry point, not only the release-authoritative one."""
        for value in ([], {}, None, "unknown-mode"):
            with self.subTest(value=repr(value)):
                document = solo_editorial()
                for lemma in document["lemmas"]:
                    for meaning in lemma["meanings"]:
                        for pattern in meaning["patterns"]:
                            if pattern.get("reviewState") == "approved":
                                pattern["releaseMode"] = copy.deepcopy(value)
                self.assertFailsWith(
                    "SCHEMA_ENUM", project_runtime_nonrelease,
                    document, 424242, context())


class SoloMaintainerLoaderBridgeTests(Phase5ATestCase):
    """A solo-mode release must reach the shipping JavaScript consumer intact.

    The governance amendment changed which evidence authorises a release.  It
    must not have changed a single byte of what a release looks like, and the
    only way to prove that is to hand the real projected bytes to the real
    shipping loader.
    """

    @classmethod
    def setUpClass(cls):
        cls.frozen = freeze_editorial(solo_editorial(), 1, context())
        cls.runtime = verified_runtime_from_frozen(cls.frozen)
        cls.temporary = tempfile.TemporaryDirectory(prefix="p7-phase4e-")
        cls.runtime_path = Path(cls.temporary.name) / "solo-runtime.json"
        cls.runtime_path.write_text(
            json.dumps(cls.runtime, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def drive_loader(self, mutation="none"):
        completed = subprocess.run(
            ["osascript", "-l", "JavaScript", str(LOADER_HARNESS), str(ROOT),
             str(self.runtime_path), mutation],
            capture_output=True, text=True, check=False, cwd=ROOT)
        self.assertEqual(
            0, completed.returncode,
            f"loader harness failed: {completed.stderr}")
        return json.loads(completed.stdout)

    def test_the_shipping_loader_accepts_a_solo_maintainer_release(self):
        result = self.drive_loader()
        self.assertIs(True, result["settled"])
        self.assertIs(True, result["available"])
        self.assertEqual({"lemmas": 1, "patterns": 2}, result["summary"])
        self.assertIs(False, result["holdsPrivateKey"])
        self.assertEqual(1, result["requestCount"])
        self.assertEqual("no-store", result["requestCache"])

    def test_the_loader_still_refuses_the_negative_cases_under_this_mode(self):
        for mutation in ("private-review-state", "private-origin-deep",
                         "private-key-field", "extra-envelope-key",
                         "nonrelease-wrapper", "empty-lemmas"):
            with self.subTest(mutation=mutation):
                result = self.drive_loader(mutation)
                self.assertIs(False, result["settled"])
                self.assertIs(False, result["available"])


# --------------------------------------------------------------------------
# §26/§32/§35  the real release boundary is untouched
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Phase 4F-B3B editorial delta
#
# Phase 4F-B3B implemented the five approved editorial corrections from the B3A
# adjudication -- rows P7-NR-005, P7-NR-029, P7-NR-030, P7-NR-037 and
# P7-NR-040.  They change learner-facing canonical fields by design, which is
# exactly what the guard below forbids *for its own phase*.  Normalising them
# away keeps that guard truthful about the phase it belongs to, instead of
# reporting a later phase's authorised work as this phase's violation.
#
# The normalisation is deliberately exact: it reverts a field only when that
# field currently holds the precise value B3B wrote.  Any other edit -- to
# these patterns, to these fields, or anywhere else in the corpus -- survives
# normalisation and still fails the guard.  The corrected values themselves are
# pinned independently by tests/test_priority7_phase4fb3b.py.
# --------------------------------------------------------------------------

#: pattern id -> field -> (value B3B wrote, value it replaced)
PHASE_4FB3B_APPROVED_EDITS = {
    "vp-p-sluchac-obey-genitive-object-674adae2dec3": {
        "learnerExplanationEn": (
            "In the obey sense słuchać still takes the Genitive: "
            "dziecko słucha mamy.",
            "In the obey sense słuchać still takes the Genitive: "
            "nie słucha rodziców."),
    },
    "vp-p-mowic-tell-content-dative-recipient-accusative-content"
    "-2f2b1add1960": {
        "learnerExplanationEn": (
            "The thing told is Accusative and the person told is Dative; the "
            "person can be left out: mówię prawdę.",
            "Two roles: the person told is Dative, the thing told is "
            "Accusative."),
        "complements": (
            [{"type": "case", "case": "dative", "required": False,
              "role": "recipient"},
             {"type": "case", "case": "accusative", "required": True,
              "role": "content"}],
            [{"type": "case", "case": "dative", "required": True,
              "role": "recipient"},
             {"type": "case", "case": "accusative", "required": True,
              "role": "content"}]),
    },
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736": {
        "learnerExplanationEn": (
            "The same meaning with clause content: że introduces what is "
            "said, and the person, if named, is Dative: mówię, że to prawda.",
            "The same meaning with clause content: the person stays Dative "
            "and że introduces what is said."),
        "complements": (
            [{"type": "case", "case": "dative", "required": False,
              "role": "recipient"},
             {"type": "clause", "clauseKind": "ze", "required": True,
              "role": "content"}],
            [{"type": "case", "case": "dative", "required": True,
              "role": "recipient"},
             {"type": "clause", "clauseKind": "ze", "required": True,
              "role": "content"}]),
    },
    "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
    "-ef199e675ee9": {
        "teachingStatus": ("active-production", "recognition-only"),
        "cefr": ({"recognition": "A2", "production": "A2"},
                 {"recognition": "A2"}),
    },
    "vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1": {
        "teachingStatus": ("active-production", "recognition-only"),
        "cefr": ({"recognition": "B1", "production": "B1"},
                 {"recognition": "B1"}),
    },
}


def without_phase_4fb3b_edits(corpus):
    """Return a copy of ``corpus`` with the three B3B corrections reverted."""
    corpus = copy.deepcopy(corpus)
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                edits = PHASE_4FB3B_APPROVED_EDITS.get(pattern["id"], {})
                for field, (written, replaced) in edits.items():
                    if pattern.get(field) == written:
                        pattern[field] = replaced
    return corpus


# --------------------------------------------------------------------------
# Phase 4F-C2 normalisation
#
# Phase 4F-C2 implemented the canonical example specification locked by Phase
# 4F-C1C: five existing canonical examples took new wording under their
# unchanged durable keys and IDs, six patterns gained their first example, and
# one nonhuman example-generation actor was registered to carry the resulting
# `editorial-generated` provenance.  This suite's historical claims are stated
# over the corpus with that approved work reverted, exactly as Phase 4F-B3B's
# corrections already are.
#
# The revert is keyed on the complete approved example object: locked text,
# durable key, deterministic ID, audio flag and every provenance field.  Any
# mutation, second example or example on a fourteenth pattern remains visible
# and still breaks the historical guard.
# --------------------------------------------------------------------------

PHASE_4FC1C_MATRIX = ROOT / "reports" / "phase-4fc1c" / "adjudication-matrix.csv"

#: The nonhuman actor Phase 4F-C2 registered.  It holds the
#: `example-generation` role only and never appears in a review event.
PHASE_4FC2_ACTOR = "priority7-example-generation"
PHASE_4FC2_ADOPTED_AT = "2026-08-16"
PHASE_4FC2_EXAMPLE_KEYS = {
    "vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f":
        "thanks-for-cooperation",
    "vp-p-placic-pay-za-accusative-goods-73c6760c091d":
        "how-much-for-everything",
    "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c":
        "care-every-day",
    "vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8":
        "asking-about-the-price",
    "vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a":
        "asking-a-friend-about-a-restaurant",
    "vp-p-widziec-perceive-visually-accusative-object-80b697e51432":
        "saw-your-sister",
    "vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2":
        "thinking-about-the-exam",
    "vp-p-znalezc-find-accusative-object-d80c52211462":
        "finally-found-a-flat",
    "vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939":
        "looking-after-my-sisters-daughter",
    "vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b":
        "caring-for-a-sick-grandmother",
    "vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318":
        "plans-depend-on-the-weather",
}
PHASE_4FC2_ACTOR_NOTE_SHA256 = (
    "82065a16d79829e6e4526880009e84dfb0982ed4e1b4a49e7695e72ed93558d6")


#: Phase 4F-C2C superseded the wording of exactly these two Phase 4F-C1C rows
#: after an exact collision with pre-existing language-teaching material was
#: found before release.  Only ``pl`` and ``en`` move: the durable key, the
#: deterministic ID, ``audioEligible`` and the whole ``origin`` object are the
#: C2 ones.  The map is a closed literal keyed by review ID; no other row may
#: be overridden, and an unauthorized wording mutation anywhere else must
#: still survive normalization.
PHASE_4FC2C_WORDING_OVERRIDE = {
    "P7-NR-033": {
        "priorPl": "Czy widzisz tę górę?",
        "priorEn": "Do you see that mountain?",
        "finalPl": "Czy widzisz tę czerwoną torbę?",
        "finalEn": "Do you see that red bag?",
    },
    "P7-NR-043": {
        "priorPl": "Opiekuję się chorą babcią.",
        "priorEn": "I look after my sick grandmother.",
        "finalPl": "Dziś opiekuję się młodszą siostrą.",
        "finalEn": "Today I'm looking after my younger sister.",
    },
}


def phase_4fc2c_final_wording(row):
    """C1C's locked wording, with exactly the two C2C rows superseded.

    The override refuses to fire unless the matrix still carries the exact
    C1C wording it supersedes, so an edit to the historical adjudication
    artifact cannot be absorbed here silently.
    """
    override = PHASE_4FC2C_WORDING_OVERRIDE.get(row["reviewId"])
    if override is None:
        return row["finalPolish"], row["finalEnglish"]
    if (row["finalPolish"], row["finalEnglish"]) != (
            override["priorPl"], override["priorEn"]):
        raise AssertionError(
            "Phase 4F-C2C override no longer supersedes the C1C wording it "
            f"was written against: {row['reviewId']}")
    return override["finalPl"], override["finalEn"]


def phase_4fc2_rows():
    """The Phase 4F-C1C rows Phase 4F-C2 implemented, keyed by pattern ID."""
    with PHASE_4FC1C_MATRIX.open(newline="", encoding="utf-8") as handle:
        return {row["patternId"]: row for row in csv.DictReader(handle)
                if row["implementationDisposition"] in {"REPLACE", "CREATE"}}


def phase_4fc2_repository_source(locator):
    kind, rest = locator.split(":", 1)
    entity_id, field = rest.rsplit(".", 1)
    return {"kind": kind, "id": entity_id, "field": field}


# --------------------------------------------------------------------------
# Phase 4F-D3.1 normalisation
#
# The locked D3 adjudication approved exactly three editorial-tier wording
# corrections on patterns that were already reference-verified: two English
# example translations and one positive Polish model that appears in two
# learner-facing fields of a single pattern.  No Polish example text, no
# provenance, no identity and no reference evidence moved, so every tier-1
# reference digest is unchanged and only the tier-2 editorial scope of these
# three rows differs.
#
# This suite's historical claims are stated over the corpus with that approved
# work reverted, exactly as Phase 4F-B3B's corrections and Phase 4F-C2's
# examples already are.  The revert is keyed on the exact approved final
# string in the exact field of the exact pattern: an unauthorized fourth
# wording change, or any mutation of one of these three, is not recognised,
# stays visible, and still breaks the historical guard.
# --------------------------------------------------------------------------

#: Closed literal.  Review ID -> the single pattern the correction lives on and
#: the exact (prior, final) strings per field.  No other row may be normalised,
#: and no field outside these three may be normalised on these rows.
PHASE_4FD31_EDITORIAL_CORRECTION = {
    "P7-NR-018": {
        "patternId":
            "vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c",
        "exampleEn": ("I look after my fitness every day.",
                      "I work on my fitness every day."),
    },
    "P7-NR-028": {
        "patternId": "vp-p-lubic-enjoy-thing-or-activity-infinitive-activity"
                     "-be3742b7ce45",
        "exampleEn": ("I like reading before sleep.",
                      "I like reading before bed."),
    },
    "P7-NR-037": {
        "patternId":
            "vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer"
            "-ef199e675ee9",
        "learnerExplanationEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
        "guidanceEn": (
            "The thing liked is the subject and the person is Dative: "
            "ten film podoba mi się.",
            "The thing liked is the subject and the person is Dative: "
            "ten film mi się podoba."),
    },
}

PHASE_4FD31_BY_PATTERN = {
    row["patternId"]: row
    for row in PHASE_4FD31_EDITORIAL_CORRECTION.values()
}


def without_phase_4fd31_corrections(corpus):
    """Return a copy of ``corpus`` with the three D3.1 corrections reverted.

    Each field reverts only when it currently holds the exact approved final
    string, so a wording mutation anywhere -- including a fourth canonical
    edit on one of these same three patterns -- survives normalisation.
    """
    corpus = copy.deepcopy(corpus)
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                row = PHASE_4FD31_BY_PATTERN.get(pattern["id"])
                if row is None:
                    continue
                if "exampleEn" in row:
                    prior, final = row["exampleEn"]
                    examples = pattern.get("examples") or []
                    if len(examples) == 1 and examples[0].get("en") == final:
                        examples[0]["en"] = prior
                if "learnerExplanationEn" in row:
                    prior, final = row["learnerExplanationEn"]
                    if pattern.get("learnerExplanationEn") == final:
                        pattern["learnerExplanationEn"] = prior
                if "guidanceEn" in row:
                    prior, final = row["guidanceEn"]
                    notes = pattern.get("errorNotes") or []
                    if notes and notes[0].get("guidanceEn") == final:
                        notes[0]["guidanceEn"] = prior
    return corpus


def without_phase_4fc2_examples(corpus):
    """Return a copy of ``corpus`` with the C1C example work reverted.

    Later approved wording is absorbed first: the Phase 4F-C2C two-row
    override through :func:`phase_4fc2c_final_wording`, and the Phase
    4F-D3.1 editorial corrections through
    :func:`without_phase_4fd31_corrections`.  The result is the corpus as
    it stood before Phase 4F-C2, which is what this suite's historical
    claims are stated over.
    """
    corpus = without_phase_4fd31_corrections(corpus)
    rows = phase_4fc2_rows()
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                row = rows.get(pattern["id"])
                if row is None:
                    continue
                examples = pattern.get("examples") or []
                if len(examples) != 1:
                    continue
                example = examples[0]
                key = PHASE_4FC2_EXAMPLE_KEYS[pattern["id"]]
                final_pl, final_en = phase_4fc2c_final_wording(row)
                expected = {
                    "id": T.allocate_example_id(pattern["id"], key),
                    "key": key,
                    "pl": final_pl,
                    "en": final_en,
                    "audioEligible": False,
                    "origin": {
                        "kind": "editorial-generated",
                        "generatorRef": PHASE_4FC2_ACTOR,
                        "adoptedAt": PHASE_4FC2_ADOPTED_AT,
                    },
                }
                if example != expected:
                    continue
                if row["implementationDisposition"] == "CREATE":
                    # The baseline omits the key entirely on a pattern that
                    # has no example; restoring [] would not be the baseline.
                    pattern.pop("examples")
                    continue
                example["pl"] = row["currentPolish"]
                example["en"] = row["currentEnglish"]
                example["origin"] = {
                    "kind": row["currentOrigin"],
                    "repositorySource": phase_4fc2_repository_source(
                        row["currentRepositorySource"]),
                }
    return corpus


def without_phase_4fc2_actor(context_document):
    """Remove only the exact approved C2 actor, never a mutated record."""
    context_document = copy.deepcopy(context_document)
    registry = context_document.get("editorialActorRegistry", {})
    record = registry.get(PHASE_4FC2_ACTOR)
    if (isinstance(record, dict) and
            set(record) == {"human", "kind", "roles", "namedInPhase", "note"} and
            record["human"] is False and
            record["kind"] == "example-generation-workflow" and
            record["roles"] == ["example-generation"] and
            record["namedInPhase"] == "Priority 7 Phase 4F-C2" and
            hashlib.sha256(record["note"].encode("utf-8")).hexdigest() ==
            PHASE_4FC2_ACTOR_NOTE_SHA256):
        registry.pop(PHASE_4FC2_ACTOR)
    return context_document



#: The commit Phase 4F-A produced; its review history is the checkpoint.
#: Phase 4F-B3B.1 appended one fresh tier-1 acceptance to each of the two rows
#: whose optionality correction moved their reference scope, and rewrote none
#: of the original 45.  Asserting 47 as "Phase 4F-A's inventory" would rewrite
#: history; asserting 45 as the current total would deny the refresh.
PHASE_4FA_CHECKPOINT_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"

#: The same commit named for its other role: the parent Phase 4F-B3B started
#: from, and therefore the immutable pre-B3B corpus any "did a later phase
#: change linguistic content?" guard must compare against.  Aliased rather than
#: re-spelled so the two names can never drift apart -- 4F-A produced this
#: commit and B3B began from it, so they are one commit seen from two sides.
PHASE_4FB3B_BASELINE_SHA = PHASE_4FA_CHECKPOINT_COMMIT

#: Fields a governance-only phase may move.  Deliberately the same four the
#: guard has always excluded; Phase 4F-B3B.2 widened nothing.
GOVERNANCE_KEYS = frozenset(
    {"releaseMode", "reviewState", "reviewEvents", "evidence"})


def corpus_projection(corpus):
    """Every lemma, meaning and pattern fact outside the governance keys."""
    return [
        {"lemma": {k: v for k, v in lemma.items() if k != "meanings"},
         "meaning": {k: v for k, v in meaning.items() if k != "patterns"},
         "pattern": {k: v for k, v in pattern.items()
                     if k not in GOVERNANCE_KEYS}}
        for lemma in corpus["lemmas"]
        for meaning in lemma["meanings"]
        for pattern in meaning["patterns"]]


def guard_holds(repository, revision, *, normalise_baseline=False,
                corpus_name="corpus.json"):
    """Run the later-change guard inside ``repository`` against ``revision``.

    The repaired guard is ``revision=<pinned baseline>`` with
    ``normalise_baseline=False``: the working corpus, with the five approved
    B3B edits reverted, must equal the immutable pre-B3B corpus.

    ``revision="HEAD", normalise_baseline=True`` reproduces the superseded
    form exactly, so the controls can show it passing where the repaired form
    fails.  Both sides had to be normalised there, because both sides carried
    the candidate's edits once the candidate was HEAD -- which is precisely
    what made it a comparison of the corpus with itself.

    Returns a bool rather than asserting so a control can require either
    outcome.
    """
    blob = subprocess.run(
        ["git", "show", f"{revision}:{corpus_name}"],
        cwd=repository, capture_output=True, text=True)
    if blob.returncode != 0:
        raise AssertionError(blob.stderr)
    baseline = json.loads(blob.stdout)
    if normalise_baseline:
        baseline = without_phase_4fb3b_edits(baseline)
    working = json.loads(
        (Path(repository) / corpus_name).read_text(encoding="utf-8"))
    return (corpus_projection(baseline)
            == corpus_projection(without_phase_4fb3b_edits(working)))


#: pattern id -> fresh tier-1 acceptances appended by Phase 4F-B3B.1.
PHASE_4FB3B1_REFRESHED = {
    "vp-p-mowic-tell-content-dative-recipient-accusative-content"
    "-2f2b1add1960": 1,
    "vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736": 1,
}

PHASE_4FA_EVENT_COUNT = 45
CURRENT_EVENT_COUNT = (
    PHASE_4FA_EVENT_COUNT + sum(PHASE_4FB3B1_REFRESHED.values()))


def phase_4fa_review_events():
    """pattern id -> the reviewEvents Phase 4F-A actually wrote."""
    blob = subprocess.run(
        ["git", "show", PHASE_4FA_CHECKPOINT_COMMIT
         + ":editorial/verb-pattern-candidates.json"],
        cwd=ROOT, capture_output=True, text=True)
    if blob.returncode != 0:
        raise AssertionError(blob.stderr)
    return {pattern["id"]: pattern["reviewEvents"]
            for lemma in json.loads(blob.stdout)["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]}


class CommittedStateGuard(unittest.TestCase):
    """The later-change guard must stay meaningful once the candidate is HEAD.

    Every control below runs inside a throwaway repository built in a temporary
    directory.  The real repository is never written to, never committed and
    never has its HEAD moved; only the two corpora are borrowed from it.

    The point the controls establish is narrow and behavioural: with HEAD moved
    past the baseline, pinning to the baseline commit still discriminates,
    while reading ``HEAD`` no longer does.
    """

    #: A pattern none of the five approved B3B edits touches.
    UNRELATED_PATTERN = "vp-p-szukac-seek-genitive-target-71dc6eff512c"

    def isolated_repository(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)

        def run(*arguments):
            return subprocess.run(
                ["git", *arguments], cwd=holder.name, capture_output=True,
                text=True, check=True)

        run("init", "-q")
        run("config", "user.email", "phase5a@example.invalid")
        run("config", "user.name", "phase 5a control")
        return holder.name, run

    def commit_corpus(self, directory, run, corpus, message):
        (Path(directory) / "corpus.json").write_text(
            json.dumps(corpus, ensure_ascii=False, indent=2), encoding="utf-8")
        run("add", "-A")
        run("commit", "-q", "-m", message)
        return run("rev-parse", "HEAD").stdout.strip()

    def baseline_corpus(self):
        blob = git("show", f"{PHASE_4FB3B_BASELINE_SHA}"
                           ":editorial/verb-pattern-candidates.json")
        self.assertEqual(0, blob.returncode, blob.stderr)
        return json.loads(blob.stdout)

    def candidate_corpus(self):
        # The Phase 4F-B3B candidate this guard is about: the live corpus with
        # the later Phase 4F-H2 content completion and Phase 4F-C2 example
        # work reverted, newest layer first.
        return without_phase_4fc2_examples(
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(
                    json.loads(CORPUS.read_text(encoding="utf-8")))))

    def with_sixth_edit(self):
        """The candidate plus one unauthorised learner-facing change."""
        corpus = self.candidate_corpus()
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == self.UNRELATED_PATTERN:
                        pattern["learnerExplanationEn"] = "unauthorised sixth"
                        return corpus
        self.fail("control pattern not found")

    def committed_history(self, *corpora):
        """Commit each corpus in turn; return (dir, first sha, last sha)."""
        directory, run = self.isolated_repository()
        shas = [self.commit_corpus(directory, run, corpus, f"step {index}")
                for index, corpus in enumerate(corpora)]
        return directory, shas[0], shas[-1]

    # -- the repair works ---------------------------------------------------

    def test_the_legitimate_candidate_passes_once_it_is_head(self):
        directory, baseline, head = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus())
        self.assertNotEqual(baseline, head, "HEAD must have moved")
        self.assertTrue(guard_holds(directory, baseline))

    def test_a_sixth_committed_edit_fails_against_the_pinned_baseline(self):
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus(),
            self.with_sixth_edit())
        self.assertFalse(guard_holds(directory, baseline))

    def test_a_wrong_value_on_an_approved_field_fails(self):
        corpus = self.candidate_corpus()
        wierzyc = next(key for key in PHASE_4FB3B_APPROVED_EDITS
                       if "wierzyc" in key)
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == wierzyc:
                        pattern["cefr"]["production"] = "A2"
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), corpus)
        self.assertFalse(guard_holds(directory, baseline))

    def test_an_unauthorised_required_flip_fails(self):
        corpus = self.candidate_corpus()
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    if pattern["id"] == self.UNRELATED_PATTERN:
                        pattern["complements"][0]["required"] = False
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), corpus)
        self.assertFalse(guard_holds(directory, baseline))

    # -- why the repair was needed, kept executable -------------------------

    def test_the_old_head_form_would_have_missed_the_sixth_edit(self):
        """The defect Codex found, pinned so it cannot return.

        Same repository, same unauthorised commit, same guard body -- only the
        revision differs.  Read from ``HEAD`` the comparison is the corpus
        against itself and passes; read from the pinned baseline it fails.
        """
        directory, baseline, _ = self.committed_history(
            self.baseline_corpus(), self.candidate_corpus(),
            self.with_sixth_edit())
        self.assertTrue(
            guard_holds(directory, "HEAD", normalise_baseline=True),
            "the superseded HEAD form is expected to be vacuous")
        self.assertFalse(guard_holds(directory, baseline),
                         "the pinned form must catch what HEAD misses")

    def test_the_production_guard_reads_the_pinned_baseline(self):
        """Read the guard's executable body, not the whole file."""
        source = inspect.getsource(
            RealCorpusBoundaryTests
            .test_real_corpus_changed_only_governance_since_the_pinned_baseline)
        body = source.split('"""')[-1]
        self.assertIn("PHASE_4FB3B_BASELINE_SHA", body)
        self.assertNotIn("HEAD", body)


class RealCorpusBoundaryTests(Phase5ATestCase):

    def test_real_corpus_changed_only_governance_since_the_pinned_baseline(
            self):
        """The canonical corpus's linguistic content is still untouched.

        Phase 4F-A is the first phase entitled to write review events, so the
        byte-identity assertion this test used to make cannot survive it.  The
        substance it protected does survive and is asserted directly: outside
        ``releaseMode``, ``reviewState``, ``reviewEvents`` and ``evidence``,
        the corpus matches the pre-B3B baseline once the five approved B3B
        edits are normalised away.

        The baseline is pinned to the immutable commit.  This test previously
        read the corpus at ``HEAD``, which was sound only while Phase 4F-B3B
        was an uncommitted working tree; the moment the candidate is itself
        committed, ``HEAD`` contains it and the assertion degrades into the
        corpus against itself, passing whatever changed.
        ``CommittedStateGuard`` below proves that on a repository whose HEAD
        really has moved.

        Only the working side is normalised.  The baseline predates B3B, so it
        holds none of the values ``without_phase_4fb3b_edits`` reverts, and
        normalising it too could only ever mask a difference.
        """
        tracked = "editorial/verb-pattern-candidates.json"
        baseline = git("show", f"{PHASE_4FB3B_BASELINE_SHA}:{tracked}")
        self.assertEqual(0, baseline.returncode, baseline.stderr)
        # Phase 4F-C2 implemented the locked Phase 4F-C1C example
        # specification, so its approved work is reverted alongside Phase
        # 4F-B3B's before the pre-B3B claim is stated.
        on_disk = without_phase_4fc2_examples(
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(
                    json.loads((ROOT / tracked).read_text(encoding="utf-8")))))
        self.assertEqual(
            corpus_projection(json.loads(baseline.stdout)),
            corpus_projection(without_phase_4fb3b_edits(on_disk)),
            f"{tracked} may change only in governance fields")

    def test_real_authoring_context_holds_exactly_the_phase_4c_boundary(self):
        """The durable governance boundary, asserted without consulting HEAD.

        An earlier version of this test compared the authoring context against
        ``git show HEAD:...`` and asserted that HEAD's reviewerRegistry was
        empty.  That is only true while Phase 4C is uncommitted: once the
        candidate is committed, HEAD legitimately contains the reviewer and the
        test flips to failing.  A permanent test must not depend on whether a
        phase happens to be committed yet, so the assertion below states the
        truthful post-Phase-4C boundary directly.

        The sibling corpus test still compares against HEAD, and stays strict:
        the canonical corpus is byte-identical to HEAD before and after any
        commit of this candidate, because Phase 4C changed none of it.
        """
        live_context = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        context = without_phase_4fc2_actor(
            E1.without_phase_4fe1_actors(
                F2.without_phase_4ff2_reviewer(
                    H2.without_phase_4fh2_context(
                        H21.without_phase_4fh21_context(live_context)))))
        self.assertEqual(
            "priority-7-private-authoring-context-nonproduction",
            context["contextStatus"])
        # Live and unconditional: every registered editorial actor is nonhuman,
        # no actor key is also a reviewer key, and no human author exists.
        for actor_id, record in live_context["editorialActorRegistry"].items():
            self.assertIs(False, record["human"], actor_id)
        self.assertEqual(
            set(),
            set(live_context["editorialActorRegistry"]) &
            set(live_context["reviewerRegistry"]))
        self.assertEqual({}, live_context["authorRegistry"])
        self.assertEqual(
            {"contextStatus", "contextNotice", "sourceRegistry",
             "reviewerRegistry", "editorialActorRegistry", "authorRegistry",
             "allocationRegistry"},
            set(context))

        # Phase 4F-A added the fifth registry and exactly one record in it:
        # the nonhuman tier-1 workflow.  It is not a reviewer, holds no human
        # role, and the tier-2 editorial actor is still unregistered.
        actors = context["editorialActorRegistry"]
        self.assertEqual({"priority7-reference-analysis"}, set(actors))
        self.assertIs(False, actors["priority7-reference-analysis"]["human"])
        self.assertEqual(["reference-verification"],
                         actors["priority7-reference-analysis"]["roles"])
        self.assertEqual(
            set(), set(actors) & set(context["reviewerRegistry"]))

        reviewers = context["reviewerRegistry"]
        self.assertEqual({"native-reviewer-001"}, set(reviewers),
                         "exactly the one reviewer Phase 4C legitimately named")
        record = reviewers["native-reviewer-001"]
        self.assertIs(True, record["human"])
        self.assertEqual("AB", record["displayName"])
        self.assertEqual("Native Polish speaker", record["background"])
        self.assertIs(True, record["nativePolishSpeaker"])
        self.assertEqual(["native-linguistic"], record["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles", record)

        for role in ("external-verification", "product-approval"):
            with self.subTest(role=role):
                self.assertEqual(
                    [], [reference for reference, entry in reviewers.items()
                         if role in entry.get("roles", [])],
                    f"no {role} authority may exist after Phase 4C")

        self.assertEqual({}, context["authorRegistry"],
                         "no example-authoring authority exists")
        self.assertEqual({}, context["allocationRegistry"])
        self.assertEqual(
            {"repository", "medak-2011-headword-index",
             "medak-2011-detailed-entry", "wsjp-pan"},
            set(context["sourceRegistry"]), "the 2B source registry is intact")

    def test_no_synthetic_phase_5a_identity_leaked_into_the_real_context(self):
        """Phase 5-A's own fixture identities are all ``test-`` prefixed."""
        context = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        for registry in ("reviewerRegistry", "authorRegistry"):
            for reference in context[registry]:
                with self.subTest(registry=registry, reference=reference):
                    self.assertFalse(
                        reference.startswith("test-"),
                        f"synthetic identity {reference!r} leaked into real data")
        blob = json.dumps(context, ensure_ascii=False)
        for forbidden in ("test-", "synthetic", "fixture"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, blob)

    def test_no_human_reviewer_record_turned_into_a_review_event(self):
        """Naming a reviewer still advances nothing, and AB has no event.

        Phase 4F-A wrote 41 events, every one of them borne by the nonhuman
        reference actor.  AB, the one real human in the project, gained no
        event then and has gained none since: Phase 4F-F2's tier-3 approvals
        name the product owner, who is a different person and a different
        authority.  Being registered as a reviewer still creates nothing.
        """
        live = json.loads(CORPUS.read_text(encoding="utf-8"))
        real = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live))))
        patterns = [pattern for lemma in real["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual(45, len(patterns))
        events = [event for pattern in patterns
                  for event in pattern["reviewEvents"]]
        self.assertEqual(PHASE_4FA_EVENT_COUNT,
                         sum(len(history) for history in
                             phase_4fa_review_events().values()))
        self.assertEqual(CURRENT_EVENT_COUNT, len(events))
        for event in events:
            with self.subTest(event=event):
                self.assertNotIn("reviewerRef", event)
                self.assertEqual("priority7-reference-analysis",
                                 event["actorRef"])
        # Live and unconditional: AB never appears in the corpus, and no event
        # names AB.  Phase 4F-F2 legitimately recorded the one stage that is
        # human-borne by construction -- tier-3 product approval, which
        # requires a ``reviewerRef`` -- so the sweep is over *which* human a
        # live event may name, not over whether one appears at all.  Naming a
        # reviewer still advances nothing below tier 3.
        # Phase 4F-H2 additionally recorded owner-authorized ``correction``
        # audit events, the other kind that is human-borne by construction.
        # The sweep therefore names both human-borne kinds explicitly; every
        # other kind must still carry no ``reviewerRef`` at all, and neither
        # kind may ever name AB.
        human_borne_kinds = {"product-approval", "correction"}
        for event in [event for lemma in live["lemmas"]
                      for meaning in lemma["meanings"]
                      for pattern in meaning["patterns"]
                      for event in pattern["reviewEvents"]]:
            with self.subTest(event=event):
                if event["kind"] in human_borne_kinds:
                    self.assertNotEqual(
                        "native-reviewer-001", event.get("reviewerRef"))
                else:
                    self.assertNotIn("reviewerRef", event)
        self.assertNotIn("native-reviewer-001",
                         CORPUS.read_text(encoding="utf-8"))

    def test_real_corpus_remains_entirely_research_only(self):
        live = json.loads(CORPUS.read_text(encoding="utf-8"))
        real = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live))))
        patterns = [
            pattern
            for lemma in real["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        # Learner exposure is read from the LIVE corpus below: tier 2 had to
        # leave eligibility and audio exactly where tier 1 did.
        self.assertEqual(
            0,
            sum(len(pattern["activityEligibility"])
                for lemma in live["lemmas"]
                for meaning in lemma["meanings"]
                for pattern in meaning["patterns"]))
        self.assertEqual(
            0, sum(1 for _, key, value in walk(live)
                   if key == "audioEligible" and value is True))
        lemma_count = len(real["lemmas"])
        meaning_count = sum(len(lemma["meanings"]) for lemma in real["lemmas"])

        self.assertEqual(30, lemma_count)
        self.assertEqual(34, meaning_count)
        self.assertEqual(45, len(patterns))
        self.assertEqual(
            {"reference-verified"},
            {pattern["reviewState"] for pattern in patterns})
        self.assertEqual(
            {"reference-verification"},
            {event["kind"] for pattern in patterns
             for event in pattern["reviewEvents"]})
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"]) for pattern in patterns))
        self.assertEqual(
            0, sum(1 for _, key, value in walk(real)
                   if key == "audioEligible" and value is True))
        self.assertEqual(
            [], [path for path, _, _ in walk(real)
                 if isinstance(path, str) and "vp-x-" in path])
        self.assertNotIn("vp-x-", CORPUS.read_text(encoding="utf-8"))

    def test_real_author_registry_stays_empty_and_reviewers_stay_native_only(self):
        """The original condition was "empty until human review exists".

        Real human native review now exists, so Phase 4C named exactly one
        reviewer.  Phase 4F-F2 later registered the human product owner; that
        approved registration is reverted before the identity claim, which
        therefore still states what it stated when written.  The
        authorRegistry stays empty, live and unconditional, because no human
        example author has been named -- which is what still blocks the five
        accepted replacement sentences from entering the canonical corpus,
        and what product approval did not and could not supply.
        """
        authoring = json.loads(CONTEXT_FILE.read_text(encoding="utf-8"))
        self.assertEqual(
            {}, authoring.get("authorRegistry", {}),
            "the real authorRegistry must stay empty until a human author exists")
        reviewers = authoring.get("reviewerRegistry", {})
        self.assertEqual(
            {"native-reviewer-001"},
            set(F2.without_phase_4ff2_reviewer(
                H2.without_phase_4fh2_context(
                    H21.without_phase_4fh21_context(authoring)))["reviewerRegistry"]))
        self.assertEqual(["native-linguistic"],
                         reviewers["native-reviewer-001"]["roles"])
        self.assertNotIn("ownerAllowsMultipleRoles",
                         reviewers["native-reviewer-001"])

    def test_no_real_release_or_runtime_artifact_exists(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path is
        # exactly the I1 release artifact, pinned by digest and revision, and it
        # may only exist alongside the matching shell and worker.  Nothing about
        # the synthetic Phase 5-A bridge may reach it.
        self.assertEqual("complete", i1_bundle().state)
        for pattern in ("*frozen*.json", "*release*.json"):
            for found in (ROOT / "editorial").glob(pattern):
                self.fail(f"unexpected release artifact: {found}")

    def test_synthetic_work_added_no_startup_fetch_or_release_activation(self):
        """Restated over the pre-Phase-4F-I1 shell and worker.

        I1 is the release that adds the activation and the worker's runtime
        entry.  With its pinned layer removed, the synthetic Phase 5-A work
        still added neither -- and a SECOND activation, a different runtime URL
        or a preview/fixture URL would survive normalisation and fail here.
        """
        index_html = pre_i1("index.html")
        self.assertNotIn("content/verb-patterns.json", index_html)
        self.assertNotIn("loadRuntimeDocument", index_html)
        service_worker = pre_i1("sw.js")
        self.assertNotIn("content/verb-patterns.json", service_worker)

    def test_no_shipping_file_was_touched(self):
        """Phase 5-A added tests and fixtures only.

        Phase 4C is the first phase permitted to modify editorial data, and it
        modified exactly one editorial support file: the private authoring
        context that stores the reviewer registry.  That path is allowed here;
        the canonical corpus and every shipping file remain forbidden, which
        ``test_real_corpus_is_byte_identical_to_head`` re-proves directly.

        Phase 4E amended the governance model itself, which lives in
        ``priority7_tooling.py``.  That module is private editorial tooling: it
        is never served, never precached and never referenced by ``index.html``,
        ``sw.js`` or any loader, and the sibling test above keeps the actual
        shipping surface pinned.
        """
        status = git("status", "--porcelain")
        self.assertEqual(0, status.returncode, status.stderr)
        changed = [
            line[3:].strip().strip('"')
            for line in status.stdout.splitlines() if line.strip()
        ]
        allowed_prefixes = ("tests/", "reports/")
        allowed_paths = {
            "editorial/priority-7-authoring-context.json",
            # Phase 4F-A is the first phase entitled to write the canonical
            # corpus, and it wrote only governance fields and the reference
            # evidence it re-inspected.  The sibling test above proves that.
            "editorial/verb-pattern-candidates.json",
            "priority7_tooling.py",
        }
        unexpected = [
            path for path in changed
            if not path.startswith(allowed_prefixes)
            and path not in allowed_paths
            and not is_only_the_h3_ui_wording(path)
            and not is_only_the_i1_activation(path)
        ]
        self.assertEqual(
            [], unexpected,
            f"no shipping file may be modified: {unexpected}")


if __name__ == "__main__":
    unittest.main()
