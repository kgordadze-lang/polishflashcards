"""Priority 7 Phase 4F-G1 — approval-gated freeze and public runtime projection.

Phase 4F-F2 recorded the human product owner's ``APPROVE ALL`` over all 45
patterns.  Phase 4F-G1 is the first phase entitled to *use* that approval: it
runs the repository's own approval-gated freeze over the real corpus and
derives the public runtime projection from the frozen envelope.

**What this phase did, and all it did.**  It performed the freeze, verified the
projection, and pinned the exact bytes a future release must reproduce.  It
wrote nothing outside ``tests/`` and ``reports/``.

**What this phase deliberately did NOT do, and why.**  It did not create
``content/verb-patterns.json``.  That is not caution — it is the repository's
established contract.  Three independent live guards bind the public runtime
file's *existence* to the complete atomic release bundle:

* ``tests/test_priority7_phase3fa.py`` ::
  ``test_future_activation_is_guarded_as_one_atomic_dependency_bundle`` treats
  a present runtime file as release intent and then requires loader activation
  in ``index.html``, the runtime path named in ``index.html``, both files in
  the service worker's ``REQUIRED_ASSETS``, an advanced ``APP_VERSION`` and an
  advanced shell cache generation.  Its name states its purpose: the dormant
  path may not be activated one file at a time.
* ``tests/test_priority7_phase5a.py`` restricts the working tree to
  ``tests/``, ``reports/`` and three named private files — ``content/`` is not
  among them.
* ``tests/test_priority7_phase2a.py`` and
  ``tests/test_priority7_phase5a_bridge.js`` assert the file and the
  ``content/`` directory are absent.

``priority-7-frozen-data-and-persistence-specification.md`` §7 says the same in
prose: the runtime snapshot, consumer adapters, service-worker classification
and shell cache update *deploy atomically*.  Phase 4F-G1 was scoped to exclude
every one of those.  Materialising the artifact here would require weakening a
forward-looking release guard, so the artifact was not materialised and the
boundary is proven below instead.  No normaliser was written: because no
shipping file was created, every historical suite stays green unmodified.

Run:  python3 -m unittest tests.test_priority7_phase4fg1
"""

from __future__ import annotations

import collections
import copy
import functools
import hashlib
import json
import os.path as _g1_os_path
import re
import subprocess
import sys as _g1_sys
import unittest
from pathlib import Path

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
    """The commit each Phase 4F-I1 baseline comparison is made against.

    Resolved lazily so this helper can sit beside the other Phase 4F-I1
    plumbing, above the suite's own pinned-baseline constant.
    """
    return BASELINE_COMMIT

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
if str(ROOT) not in _g1_sys.path:
    _g1_sys.path.insert(0, str(ROOT))
_G1_DIR = _g1_os_path.dirname(_g1_os_path.abspath(__file__))
if _G1_DIR not in _g1_sys.path:
    _g1_sys.path.insert(0, _G1_DIR)

import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402
import priority7_phase4fh3_normalizer as H3  # noqa: E402
import priority7_tooling as T  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
SUMMARY_PATH = "reports/priority-7-phase-4fg1-freeze-projection-summary.md"
MANIFEST_PATH = "reports/priority-7-phase-4fg1-freeze-manifest.json"

#: Phase 4F-G1 arrived on top of this commit and states every immutability
#: claim against it, never against a moving ``HEAD``.
BASELINE_COMMIT = "3fd3355c263f91abc4b9bc0e5aa9050a1f3a4f4a"
BASELINE_TREE = "3cb8ec017a7df54890ecda7128801731d3cc1176"
CANONICAL_SHA256 = (
    "cbd416a4f81757a39cf9418ba954e4947e333b96700d2ff52f5246e5460299d3")
CONTEXT_SHA256 = (
    "807eaa7aa9917b4786495ebf959fdf1bd365f4fcf41f81a1832c7e71ebfcf6ce")

#: The public runtime artifact path locked by the frozen-data specification §7
#: and by the Phase 3A runtime contract §2.  It must not exist in this phase.
PUBLIC_RUNTIME_PATH = "content/verb-patterns.json"

#: ``previous is None`` makes this the first released snapshot, and
#: ``freeze_editorial`` then admits exactly one value.  Nothing was chosen.
EXPECTED_REVISION = 1

#: The canonical serialisation convention the tooling's own CLI uses when it
#: writes a projection to a file.  The pinned digest below is the digest of
#: these exact bytes.
RUNTIME_SHA256 = (
    "4a42cd6a15b5a52246484aa82bbbf214b3525b88ea11756b0fac937793606671")
RUNTIME_BYTE_LENGTH = 86619
PATTERN_ID_SET_DIGEST = (
    "be25c5cc78a9a42e0868aef0829c270bb0f42806f1397ae1f08f5639b4372d7d")
LEMMA_ID_SET_DIGEST = (
    "323b26bfd579c48c4c2a6cca00d664468ec64defba71146ffff93c73bbea0ca2")

EXPECTED_LEMMAS = 30
EXPECTED_MEANINGS = 34
EXPECTED_PATTERNS = 45
EXPECTED_EXAMPLES = 29
EXPECTED_CONTENT_REFS = 101
EXPECTED_ERROR_NOTES = 24

EXPECTED_REFERENCE_ACCEPTS = 47
EXPECTED_EDITORIAL_ACCEPTS = 45
EXPECTED_PRODUCT_APPROVALS = 45
PRODUCT_OWNER = "product-owner-001"

#: Identities that must never reach a learner, whatever key they hide under.
SENSITIVE_IDENTIFIERS = (
    "product-owner-001",
    "priority7-reference-analysis",
    "priority7-editorial-review",
    "priority7-editorial-corroboration",
    "priority7-example-generation",
    "native-reviewer-001",
)

#: The shipping surface Phase 4F-G1 owns no authority over.
PROTECTED_SHIPPING_FILES = (
    "index.html", "sw.js", "manifest.json", "pp-verb-patterns.js",
    "pp-usage.js", "pp-answer.js", "pp-distractor.js", "pp-migrate.js",
    "sitemap.xml", "audio-manifest.json", "data-a1.js", "data-a2.js",
    "data-b1.js", "data-grammar.js", "data-podcasts.js", "data-scenarios.js",
    "data-verbs.js", "validate_content.py", "build_pages.py",
    "priority7_tooling.py",
)


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def g1_corpus_text() -> str:
    """The corpus text as Phase 4F-G1 froze it, later phases normalised away.

    Phase 4F-H2 legitimately reopened the editorial chain on 44 of the 45
    patterns, so the live file is no longer the freeze-ready document this
    suite was written about.  Its phase-owned normaliser is closed over that
    exact transition and derives nothing from the live rows: any edit H2 did
    not author survives it, and the pinned digests below then still fail.
    """
    return H2.without_phase_4fh2_corpus_text(
        H21.without_phase_4fh21_corpus_text(read_text(CORPUS_PATH)))


def g1_context_text() -> str:
    """The context text as Phase 4F-G1 froze it, later phases normalised away."""
    return H2.without_phase_4fh2_context_text(
        H21.without_phase_4fh21_context_text(read_text(CONTEXT_PATH)))


def is_exactly_the_h3_ui_wording(path: str) -> bool:
    """True for ``index.html`` when its only change is the Phase 4F-H3 layer.

    Phase 4F-H3 is the UI wording phase, and the first phase since ``f339efb``
    entitled to change a shipping file at all.  Removing H3's six pinned
    strings must reproduce the Phase 4F-G1 baseline bytes exactly, so any
    other shell edit -- a version or cache bump, a loader activation, a change
    to the recognition-only guards -- any other path, and any partly applied
    layer are still reported as an unexpected footprint.
    """
    if not H3.is_phase_4fh3_path(path):
        return False
    baseline = bytes_at(BASELINE_COMMIT, path)
    if baseline is None:
        return False
    # LAYERED by Priority 7 Phase 4F-I1: the shell now carries the I1 release
    # layer on top of the H3 wording layer, so the H3 classification is made
    # over the shell with the I1 layer removed.  Both layers are pinned and
    # all-or-nothing, so an edit outside either pinned set is still reported.
    return H3.is_exactly_the_h3_ui_wording(
        path, baseline.decode("utf-8"), pre_i1(path))


def is_exactly_the_h2_content_completion(path: str) -> bool:
    """True only for an editorial file whose sole change is the H2 transition.

    A path qualifies when removing the pinned Phase 4F-H2 layer reproduces the
    Phase 4F-G1 baseline bytes exactly.  Any other edit to either file, and any
    other path, is reported by the footprint claim as before.
    """
    views = {CORPUS_PATH: g1_corpus_text, CONTEXT_PATH: g1_context_text}
    if path not in views:
        return False
    baseline = bytes_at(BASELINE_COMMIT, path)
    if baseline is None:
        return False
    try:
        return baseline == views[path]().encode("utf-8")
    except AssertionError:
        return False


def git(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, text=True,
        check=False)


def bytes_at(reference: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{reference}:{path}"], cwd=ROOT, capture_output=True,
        check=False)
    return result.stdout if result.returncode == 0 else None


def serialize_runtime(runtime: dict) -> str:
    """The tooling's own file-writing convention, and the digest's definition."""
    return json.dumps(runtime, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def id_set_digest(identifiers) -> str:
    return sha256_text("\n".join(sorted(identifiers)))


def load_corpus() -> dict:
    return json.loads(g1_corpus_text())


@functools.lru_cache(maxsize=1)
def _repository_context() -> T.ValidationContext:
    """Built once: it indexes every shipped ``data-*.js`` file and is costly.

    ``ValidationContext`` is a frozen dataclass and ``freeze_editorial``
    derives its own copy, so one shared instance stays read-only.
    """
    return T._load_context(str(ROOT / CONTEXT_PATH), str(ROOT))


def load_context() -> T.ValidationContext:
    return _repository_context()


@functools.lru_cache(maxsize=1)
def _baseline_freeze() -> tuple[dict, dict, str]:
    corpus = load_corpus()
    frozen = T.freeze_editorial(corpus, EXPECTED_REVISION, load_context())
    runtime = T.verified_runtime_from_frozen(frozen)
    return corpus, frozen, runtime


def patterns_of(document) -> list:
    return [
        pattern
        for lemma in document["lemmas"]
        for meaning in lemma["meanings"]
        for pattern in meaning["patterns"]
    ]


def meanings_of(document) -> list:
    return [meaning for lemma in document["lemmas"] for meaning in lemma["meanings"]]


def examples_of(document) -> list:
    return [
        example for pattern in patterns_of(document)
        for example in pattern.get("examples", [])
    ]


def walk_keys(value, path="$"):
    """Every key, at every depth, with the path it was found at."""
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, f"{path}.{key}"
            yield from walk_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_keys(child, f"{path}[{index}]")


def walk_strings(value, path="$"):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_strings(child, f"{path}[{index}]")
    elif isinstance(value, str):
        yield value, path


class Phase4FG1TestCase(unittest.TestCase):
    """One freeze, shared read-only; every mutation runs on a private copy."""

    corpus: dict
    frozen: dict
    runtime: dict
    serialized: str

    @classmethod
    def setUpClass(cls):
        cls.corpus, cls.frozen, cls.runtime = _baseline_freeze()
        cls.serialized = serialize_runtime(cls.runtime)

    def corpus_copy(self) -> dict:
        return copy.deepcopy(type(self).corpus)

    def runtime_copy(self) -> dict:
        return copy.deepcopy(type(self).runtime)

    def frozen_copy(self) -> dict:
        return copy.deepcopy(type(self).frozen)

    def assertRaisesCode(self, code, callable_object, *arguments, **keywords):
        with self.assertRaises(T.ValidationFailure) as caught:
            callable_object(*arguments, **keywords)
        found = sorted({issue.code for issue in caught.exception.issues})
        self.assertIn(code, found, f"expected {code}, got {found}")
        return found

    def assertIssueCode(self, code, issues):
        found = sorted({issue.code for issue in issues})
        self.assertIn(code, found, f"expected {code}, got {found}")


# ---------------------------------------------------------------------------
# §3  Freeze preconditions, proved independently of the freeze succeeding.
# ---------------------------------------------------------------------------
class FreezePreconditionTests(Phase4FG1TestCase):

    def test_the_frozen_inputs_are_the_declared_baseline_bytes(self):
        self.assertEqual(
            CANONICAL_SHA256,
            hashlib.sha256(g1_corpus_text().encode("utf-8")).hexdigest())
        self.assertEqual(
            CONTEXT_SHA256,
            hashlib.sha256(g1_context_text().encode("utf-8")).hexdigest())

    def test_exactly_forty_five_patterns_all_at_approved(self):
        patterns = patterns_of(type(self).corpus)
        self.assertEqual(EXPECTED_PATTERNS, len(patterns))
        self.assertEqual({"approved"}, {p["reviewState"] for p in patterns})

    def test_the_governance_ledger_is_exactly_47_45_45_and_all_accepts(self):
        counts = collections.Counter()
        for pattern in patterns_of(type(self).corpus):
            for event in pattern["reviewEvents"]:
                counts[(event["kind"], event["decision"])] += 1
        self.assertEqual(
            {("reference-verification", "accept"): EXPECTED_REFERENCE_ACCEPTS,
             ("editorial-review", "accept"): EXPECTED_EDITORIAL_ACCEPTS,
             ("product-approval", "accept"): EXPECTED_PRODUCT_APPROVALS},
            dict(counts))

    def test_exactly_one_product_approval_acceptance_per_pattern(self):
        for pattern in patterns_of(type(self).corpus):
            approvals = [
                event for event in pattern["reviewEvents"]
                if event["kind"] == "product-approval"]
            with self.subTest(pattern=pattern["id"]):
                self.assertEqual(1, len(approvals))
                self.assertEqual("accept", approvals[0]["decision"])
                self.assertEqual(PRODUCT_OWNER, approvals[0]["reviewerRef"])
                self.assertNotIn("actorRef", approvals[0])

    def test_no_correction_or_reopen_activity_is_involved(self):
        kinds = {
            event["kind"] for pattern in patterns_of(type(self).corpus)
            for event in pattern["reviewEvents"]}
        self.assertEqual(
            {"reference-verification", "editorial-review", "product-approval"},
            kinds)
        decisions = {
            event["decision"] for pattern in patterns_of(type(self).corpus)
            for event in pattern["reviewEvents"]}
        self.assertEqual({"accept"}, decisions)

    def test_the_product_owner_is_valid_under_the_current_contract(self):
        registry = json.loads(read_text(CONTEXT_PATH))["reviewerRegistry"]
        owner = registry[PRODUCT_OWNER]
        self.assertIs(True, owner["human"])
        self.assertEqual(["product-approval"], owner["roles"])
        self.assertIn("solo-maintainer-reference-backed",
                      owner["acknowledgedReleaseModes"])

    def test_every_tier_digest_still_supports_approved_on_every_row(self):
        """Digest currency is read through the tooling's own derivation."""
        policy = {row["id"]: row for row in type(self).frozen["policy"]}
        history = {row["id"]: row for row in type(self).frozen["reviewHistory"]}
        stale = []
        for entity_id, row in policy.items():
            if row.get("kind") != "pattern":
                continue
            currency = T._frozen_expected_review_state(row, history[entity_id])
            if currency.state != "approved":
                stale.append((entity_id, currency.state))
        self.assertEqual([], stale)

    def test_no_row_is_dropped_so_the_freeze_is_never_partial(self):
        policy = {row["id"]: row for row in type(self).frozen["policy"]}
        self.assertEqual(EXPECTED_PATTERNS,
                         len(T._admitted_frozen_pattern_ids(policy)))

    def test_the_editorial_record_validates_before_anything_is_frozen(self):
        self.assertEqual([], T.validate_editorial(self.corpus_copy(), load_context()))


# ---------------------------------------------------------------------------
# §4  Revision selection is mechanical, not a decision.
# ---------------------------------------------------------------------------
class RevisionSelectionTests(Phase4FG1TestCase):

    def test_no_prior_frozen_baseline_exists_anywhere_in_the_repository(self):
        found = [
            path for path in ROOT.rglob("*.json")
            if ".git" not in path.parts
            and T.FROZEN_ARTIFACT_STATUS in path.read_text(
                encoding="utf-8", errors="ignore")]
        self.assertEqual([], found)

    def test_the_first_release_admits_exactly_revision_one(self):
        self.assertEqual(EXPECTED_REVISION, type(self).frozen["patternDataRevision"])
        self.assertEqual(EXPECTED_REVISION, type(self).runtime["patternDataRevision"])

    def test_any_other_first_revision_is_refused_by_the_tooling(self):
        self.assertRaisesCode(
            "FROZEN_INITIAL_REVISION", T.freeze_editorial,
            self.corpus_copy(), 2, load_context())
        self.assertRaisesCode(
            "FROZEN_REVISION", T.freeze_editorial,
            self.corpus_copy(), 0, load_context())
        self.assertRaisesCode(
            "FROZEN_REVISION", T.freeze_editorial,
            self.corpus_copy(), -1, load_context())

    def test_the_revision_is_stored_only_inside_the_runtime_document(self):
        """It is not APP_VERSION, the shell cache, schemaVersion or a migration."""
        index = read_text("index.html")
        worker = read_text("sw.js")
        self.assertNotIn("patternDataRevision", index)
        self.assertNotIn("patternDataRevision", worker)
        self.assertIn("patternDataRevision", type(self).runtime)


# ---------------------------------------------------------------------------
# §5  The official approval-gated mechanism, and nothing lower level.
# ---------------------------------------------------------------------------
class OfficialFreezeTests(Phase4FG1TestCase):

    def test_the_freeze_is_the_repository_release_authority(self):
        frozen = type(self).frozen
        self.assertEqual(T.FROZEN_ARTIFACT_STATUS, frozen["artifactStatus"])
        self.assertEqual(T.FORMAT_VERSION, frozen["formatVersion"])
        self.assertEqual([], T.validate_frozen_release(frozen))

    def test_the_public_runtime_comes_only_through_the_verified_gate(self):
        gated = T.verified_runtime_from_frozen(self.frozen_copy())
        self.assertEqual(type(self).runtime, gated)

    def test_the_nonrelease_preview_path_is_not_what_produced_this(self):
        """F1's preview wrapper is refused by the release gate, as designed."""
        preview = T.project_nonrelease_fixture(
            self.corpus_copy(), EXPECTED_REVISION, load_context())
        self.assertEqual(T.NONRELEASE_PROJECTION_STATUS, preview["artifactStatus"])
        self.assertIs(False, preview["releaseAuthorized"])
        self.assertNotIn("artifactStatus", type(self).runtime)
        self.assertNotIn("releaseAuthorized", type(self).runtime)
        self.assertRaisesCode(
            "SCHEMA_UNKNOWN_FIELD", T.verified_runtime_from_frozen, preview)

    def test_release_authorization_is_derived_and_claims_no_human_review(self):
        self.assertEqual(
            {"releaseModes": ["solo-maintainer-reference-backed"],
             "humanVerifiedPatternIds": [],
             "humanNativeReviewedPatternIds": []},
            type(self).frozen["releaseAuthorization"])

    def test_the_freeze_created_no_tombstone_and_allocated_every_entity(self):
        self.assertEqual([], type(self).frozen["tombstones"])
        allocations = {row["id"] for row in type(self).frozen["allocations"]}
        identities = {row["id"] for row in type(self).frozen["identity"]}
        self.assertEqual(allocations, identities)


# ---------------------------------------------------------------------------
# §6  The public runtime contract is closed.
# ---------------------------------------------------------------------------
class PublicRuntimeContractTests(Phase4FG1TestCase):

    def test_the_envelope_is_exactly_the_three_public_keys(self):
        self.assertEqual(
            {"formatVersion", "patternDataRevision", "lemmas"},
            set(type(self).runtime))
        self.assertEqual(T.FORMAT_VERSION, type(self).runtime["formatVersion"])

    def test_the_official_validator_accepts_it_with_and_without_allocations(self):
        self.assertEqual([], T.validate_runtime(
            type(self).runtime, T.ValidationContext()))
        allocations = {row["id"]: row for row in type(self).frozen["allocations"]}
        self.assertEqual([], T.validate_runtime(
            type(self).runtime,
            T.ValidationContext(allocation_registry=allocations)))

    def test_the_shipping_loader_envelope_matches_the_python_contract(self):
        loader = read_text("pp-verb-patterns.js")
        declared = re.search(
            r"var ENVELOPE_KEYS = \[(.*?)\];", loader, re.S).group(1)
        self.assertEqual(
            {"formatVersion", "patternDataRevision", "lemmas"},
            set(re.findall(r'"([^"]+)"', declared)))

    def test_no_governance_metadata_was_added_for_convenience(self):
        keys = {key for key, _ in walk_keys(type(self).runtime)}
        self.assertEqual(set(), keys & {
            "releaseAuthorization", "reviewHistory", "allocations", "identity",
            "structure", "wording", "policy", "tombstones", "artifactStatus",
            "releaseAuthorized", "runtimeProjection"})

    def test_the_serialization_convention_and_its_digest_are_pinned(self):
        self.assertEqual(RUNTIME_SHA256, sha256_text(type(self).serialized))
        self.assertEqual(RUNTIME_BYTE_LENGTH,
                         len(type(self).serialized.encode("utf-8")))


# ---------------------------------------------------------------------------
# §7  Private → public leakage audit.
# ---------------------------------------------------------------------------
class LeakageAuditTests(Phase4FG1TestCase):

    def test_no_forbidden_runtime_key_appears_at_any_depth(self):
        found = sorted({
            key for key, _ in walk_keys(type(self).runtime)
            if key in T.FORBIDDEN_RUNTIME_KEYS})
        self.assertEqual([], found)

    def test_the_key_vocabulary_is_a_closed_public_set(self):
        self.assertEqual(sorted({
            "activityEligibility", "aspect", "audioEligible", "canonicalLemma",
            "case", "cefr", "clauseKind", "complements", "contentRefs", "en",
            "errorNotes", "examples", "formatVersion", "glossesEn",
            "guidanceEn", "id", "incorrectForm", "kind", "learnerExplanationEn",
            "lemmas", "meanings", "patternDataRevision", "patterns", "pl",
            "preposition", "priority", "production", "purpose", "recognition",
            "reflexive", "register", "relationType", "required", "role",
            "teachingStatus", "type", "usage",
        }), sorted({key for key, _ in walk_keys(type(self).runtime)}))

    def test_the_python_and_javascript_private_key_lists_still_agree(self):
        loader = read_text("pp-verb-patterns.js")
        declared = re.search(
            r"var PRIVATE_KEYS = \[(.*?)\];", loader, re.S).group(1)
        self.assertEqual(T.PRIVATE_RUNTIME_KEYS,
                         set(re.findall(r'"([^"]+)"', declared)))

    def test_no_sensitive_actor_or_reviewer_identity_survives_projection(self):
        for identifier in SENSITIVE_IDENTIFIERS:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, type(self).serialized)

    def test_no_registry_identifier_of_any_kind_survives_projection(self):
        context = json.loads(read_text(CONTEXT_PATH))
        identifiers = set()
        for registry in ("sourceRegistry", "reviewerRegistry", "authorRegistry",
                         "editorialActorRegistry", "allocationRegistry"):
            node = context.get(registry) or {}
            if isinstance(node, dict):
                identifiers |= set(node)
        self.assertTrue(identifiers)
        self.assertEqual(
            [], sorted(i for i in identifiers if i in type(self).serialized))

    def test_no_digest_date_or_note_shaped_private_token_survives(self):
        serialized = type(self).serialized
        self.assertEqual([], re.findall(r"sha256:[0-9a-f]{64}", serialized))
        self.assertEqual([], re.findall(r'"20\d\d-\d\d-\d\d"', serialized))
        self.assertNotIn("editorialNotes", serialized)
        self.assertNotIn("APPROVE ALL", serialized)

    def test_value_level_overlap_is_only_the_public_card_vocabulary(self):
        """A private *value* must not escape under an unexpected key.

        The only strings shared between the private record's private-keyed
        subtrees and the public projection are repository content identifiers,
        and every one of them already ships publicly in ``data-*.js``.
        """
        private_values = set()

        def collect(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in T.FORBIDDEN_RUNTIME_KEYS:
                        for text, _ in walk_strings(child):
                            if len(text) >= 8:
                                private_values.add(text)
                    else:
                        collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(type(self).corpus)
        self.assertTrue(private_values)
        runtime_strings = {text for text, _ in walk_strings(type(self).runtime)}
        overlap = sorted(private_values & runtime_strings)
        shipped = "".join(
            read_text(name) for name in (
                "data-a1.js", "data-a2.js", "data-b1.js", "data-grammar.js",
                "data-scenarios.js", "data-verbs.js", "data-podcasts.js"))
        self.assertEqual(
            [], [value for value in overlap if value not in shipped],
            "a private value escaped that is not already public content")

    def test_an_injected_private_key_is_refused_by_the_official_validator(self):
        hostile = self.runtime_copy()
        hostile["lemmas"][0]["meanings"][0]["patterns"][0]["reviewState"] = "approved"
        self.assertIssueCode("RUNTIME_PRIVATE_FIELD",
                             T.validate_runtime(hostile, T.ValidationContext()))

    def test_a_private_value_hidden_under_a_public_key_is_still_detected(self):
        hostile = self.runtime_copy()
        hostile["lemmas"][0]["meanings"][0]["patterns"][0][
            "learnerExplanationEn"] = f"Approved by {PRODUCT_OWNER}."
        serialized = serialize_runtime(hostile)
        self.assertIn(PRODUCT_OWNER, serialized)
        self.assertNotIn(PRODUCT_OWNER, type(self).serialized)


# ---------------------------------------------------------------------------
# §8  The projection is exactly the approved learner-facing corpus.
# ---------------------------------------------------------------------------
class ContentCorrespondenceTests(Phase4FG1TestCase):

    def test_the_released_counts_are_exact(self):
        runtime = type(self).runtime
        self.assertEqual(EXPECTED_LEMMAS, len(runtime["lemmas"]))
        self.assertEqual(EXPECTED_MEANINGS, len(meanings_of(runtime)))
        self.assertEqual(EXPECTED_PATTERNS, len(patterns_of(runtime)))
        self.assertEqual(EXPECTED_EXAMPLES, len(examples_of(runtime)))

    def test_no_pattern_or_lemma_is_missing_added_or_renamed(self):
        canonical = {p["id"] for p in patterns_of(type(self).corpus)}
        released = {p["id"] for p in patterns_of(type(self).runtime)}
        self.assertEqual(set(), canonical - released, "missing pattern IDs")
        self.assertEqual(set(), released - canonical, "extra pattern IDs")
        self.assertEqual({l["id"] for l in type(self).corpus["lemmas"]},
                         {l["id"] for l in type(self).runtime["lemmas"]})

    def test_the_released_id_sets_hash_to_the_pinned_digests(self):
        self.assertEqual(PATTERN_ID_SET_DIGEST,
                         id_set_digest(p["id"] for p in patterns_of(type(self).runtime)))
        self.assertEqual(LEMMA_ID_SET_DIGEST,
                         id_set_digest(l["id"] for l in type(self).runtime["lemmas"]))

    def test_every_learner_facing_field_survives_projection_unchanged(self):
        def learner_view(document):
            view = {}
            for lemma in document["lemmas"]:
                for meaning in lemma["meanings"]:
                    for pattern in meaning["patterns"]:
                        view[pattern["id"]] = {
                            "lemmaId": lemma["id"],
                            "canonicalLemma": lemma["canonicalLemma"],
                            "reflexive": lemma["reflexive"],
                            "aspect": lemma["aspect"],
                            "meaningId": meaning["id"],
                            "glossesEn": meaning["glossesEn"],
                            "relationType": pattern["relationType"],
                            "complements": pattern["complements"],
                            "cefr": pattern["cefr"],
                            "teachingStatus": pattern["teachingStatus"],
                            "usage": pattern["usage"],
                            "learnerExplanationEn": pattern["learnerExplanationEn"],
                            "activityEligibility": pattern["activityEligibility"],
                            "errorNotes": pattern.get("errorNotes", []),
                            "exampleIds": sorted(
                                e["id"] for e in pattern.get("examples", [])),
                            "exampleText": sorted(
                                (e["pl"], e["en"])
                                for e in pattern.get("examples", [])),
                        }
            return view

        self.assertEqual(learner_view(type(self).corpus),
                         learner_view(type(self).runtime))

    def test_complement_case_and_preposition_structure_is_preserved(self):
        complements = [
            complement for pattern in patterns_of(type(self).runtime)
            for complement in pattern["complements"]]
        self.assertTrue(complements)
        self.assertLessEqual({c["type"] for c in complements}, T.COMPLEMENT_TYPES)
        for complement in complements:
            if complement["type"] == "case":
                self.assertIn(complement["case"], T.DIRECT_CASE_IDS)
            if complement["type"] == "preposition-case":
                self.assertIn(complement["case"], T.PREPOSITION_CASE_IDS)
                self.assertRegex(complement["preposition"], T.PREPOSITION_RE)

    def test_content_refs_and_error_notes_are_carried_at_their_pinned_counts(self):
        refs = [r for p in patterns_of(type(self).runtime)
                for r in p.get("contentRefs", [])]
        notes = [n for p in patterns_of(type(self).runtime)
                 for n in p.get("errorNotes", [])]
        self.assertEqual(EXPECTED_CONTENT_REFS, len(refs))
        self.assertEqual(EXPECTED_ERROR_NOTES, len(notes))
        self.assertEqual({"id", "kind", "purpose"}, {k for r in refs for k in r})
        self.assertEqual({"kind", "guidanceEn", "incorrectForm"},
                         {k for n in notes for k in n})

    def test_example_records_carry_no_editorial_provenance(self):
        examples = examples_of(type(self).runtime)
        self.assertEqual({"id", "pl", "en", "audioEligible"},
                         {key for example in examples for key in example})

    def test_no_synthetic_fixture_row_reached_the_projection(self):
        serialized = type(self).serialized
        for marker in ("quuxify", "zorbulate", "TEST-ONLY", "vp-x-"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, serialized)


# ---------------------------------------------------------------------------
# §9  Approval did not change eligibility.
# ---------------------------------------------------------------------------
class ActivityAndAudioTests(Phase4FG1TestCase):

    def test_activity_eligibility_is_empty_on_all_forty_five(self):
        for pattern in patterns_of(type(self).runtime):
            with self.subTest(pattern=pattern["id"]):
                self.assertEqual([], pattern["activityEligibility"])

    def test_no_audio_became_eligible(self):
        self.assertEqual(
            [], [e for e in examples_of(type(self).runtime) if e["audioEligible"]])
        self.assertNotIn('"audioEligible": true', type(self).serialized)

    def test_teaching_status_is_carried_not_promoted(self):
        canonical = {p["id"]: p["teachingStatus"]
                     for p in patterns_of(type(self).corpus)}
        released = {p["id"]: p["teachingStatus"]
                    for p in patterns_of(type(self).runtime)}
        self.assertEqual(canonical, released)
        self.assertEqual(
            {"active-production": 41, "recognition-only": 4},
            dict(collections.Counter(released.values())))

    def test_an_unauthorized_eligibility_expansion_cannot_be_frozen(self):
        document = self.corpus_copy()
        patterns_of(document)[0]["activityEligibility"] = ["type-it"]
        self.assertRaisesCode(
            "REVIEW_STATE_MISMATCH", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

    def test_newly_enabled_audio_cannot_be_frozen(self):
        document = self.corpus_copy()
        for pattern in patterns_of(document):
            if pattern.get("examples"):
                pattern["examples"][0]["audioEligible"] = True
                break
        self.assertRaisesCode(
            "AUDIO_NOT_AUTHORIZED", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

    def test_an_eligibility_expansion_smuggled_into_the_runtime_breaks_parity(self):
        forged = self.frozen_copy()
        forged["runtimeProjection"]["lemmas"][0]["meanings"][0][
            "patterns"][0]["activityEligibility"] = ["type-it"]
        self.assertRaisesCode(
            "FROZEN_RUNTIME_PARITY", T.verified_runtime_from_frozen, forged)


# ---------------------------------------------------------------------------
# §10  Freeze is a release-state operation, not another editing phase.
# ---------------------------------------------------------------------------
class SourceImmutabilityTests(Phase4FG1TestCase):

    def test_the_canonical_corpus_and_context_are_byte_identical_to_baseline(self):
        for path, digest, view in ((CORPUS_PATH, CANONICAL_SHA256,
                                    g1_corpus_text),
                                   (CONTEXT_PATH, CONTEXT_SHA256,
                                    g1_context_text)):
            with self.subTest(path=path):
                current = view().encode("utf-8")
                self.assertEqual(digest, hashlib.sha256(current).hexdigest())
                baseline = bytes_at(BASELINE_COMMIT, path)
                self.assertIsNotNone(baseline)
                self.assertEqual(baseline, current)

    def test_the_freeze_added_no_metadata_to_the_private_editorial_record(self):
        """This contract records freeze state nowhere but the frozen envelope."""
        reloaded = load_corpus()
        self.assertEqual(reloaded, type(self).corpus)
        serialized = read_text(CORPUS_PATH)
        # The record keeps its own ``priority-7-editorial-nonproduction``
        # marker, which predates this phase; what must be absent is any
        # freeze/release vocabulary.
        self.assertIn('"artifactStatus": "priority-7-editorial-nonproduction"',
                      serialized)
        for token in ("patternDataRevision", "frozenAt", "releaseRevision",
                      "runtimeProjection", "releaseAuthorization",
                      "frozenRevision"):
            with self.subTest(token=token):
                self.assertNotIn(token, serialized)

    def test_review_state_stays_approved_after_freeze(self):
        self.assertEqual(
            {"approved"},
            {p["reviewState"] for p in patterns_of(load_corpus())})

    def test_the_retained_governance_history_is_the_corpus_history_verbatim(self):
        history = {row["id"]: row for row in type(self).frozen["reviewHistory"]}
        for pattern in patterns_of(type(self).corpus):
            with self.subTest(pattern=pattern["id"]):
                self.assertEqual(pattern["reviewEvents"],
                                 history[pattern["id"]]["reviewEvents"])

    def test_a_content_mutation_after_approval_cannot_be_frozen(self):
        document = self.corpus_copy()
        patterns_of(document)[0]["learnerExplanationEn"] = (
            "Mutated after approval; this must not be freezable.")
        self.assertRaisesCode(
            "REVIEW_STATE_MISMATCH", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

    def test_a_lowered_review_state_cannot_be_frozen(self):
        document = self.corpus_copy()
        patterns_of(document)[0]["reviewState"] = "editorial-reviewed"
        self.assertRaisesCode(
            "REVIEW_STATE_MISMATCH", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

    def test_a_genuinely_unapproved_row_is_excluded_never_partially_frozen(self):
        document = self.corpus_copy()
        target = patterns_of(document)[0]
        target["reviewEvents"] = [
            e for e in target["reviewEvents"] if e["kind"] != "product-approval"]
        target["reviewState"] = "editorial-reviewed"
        frozen = T.freeze_editorial(document, EXPECTED_REVISION, load_context())
        runtime = T.verified_runtime_from_frozen(frozen)
        self.assertEqual(EXPECTED_PATTERNS - 1, len(patterns_of(runtime)))
        self.assertNotEqual(RUNTIME_SHA256, sha256_text(serialize_runtime(runtime)))

    def test_a_missing_or_duplicated_approval_is_refused(self):
        document = self.corpus_copy()
        target = patterns_of(document)[0]
        target["reviewEvents"] = [
            e for e in target["reviewEvents"] if e["kind"] != "product-approval"]
        self.assertRaisesCode(
            "REVIEW_STATE_MISMATCH", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

        document = self.corpus_copy()
        target = patterns_of(document)[0]
        approval = [e for e in target["reviewEvents"]
                    if e["kind"] == "product-approval"][0]
        target["reviewEvents"].append(copy.deepcopy(approval))
        self.assertRaisesCode(
            "REVIEW_DUPLICATE_STAGE_ACCEPTANCE", T.freeze_editorial, document,
            EXPECTED_REVISION, load_context())

    def test_an_approval_by_the_wrong_human_is_refused(self):
        document = self.corpus_copy()
        for event in patterns_of(document)[0]["reviewEvents"]:
            if event["kind"] == "product-approval":
                event["reviewerRef"] = "native-reviewer-001"
        self.assertRaisesCode(
            "REVIEWER_ROLE", T.freeze_editorial, document, EXPECTED_REVISION,
            load_context())


# ---------------------------------------------------------------------------
# §13  Runtime-side negative controls.
# ---------------------------------------------------------------------------
class RuntimeNegativeControlTests(Phase4FG1TestCase):

    def test_a_missing_runtime_row_breaks_frozen_parity(self):
        """Shape validation alone cannot see it; the release gate can."""
        forged = self.frozen_copy()
        forged["runtimeProjection"]["lemmas"].pop(0)
        self.assertEqual([], T.validate_runtime(
            forged["runtimeProjection"], T.ValidationContext()))
        self.assertRaisesCode(
            "FROZEN_RUNTIME_PARITY", T.verified_runtime_from_frozen, forged)

    def test_an_extra_runtime_row_is_refused(self):
        forged = self.frozen_copy()
        extra = copy.deepcopy(forged["runtimeProjection"]["lemmas"][0])
        forged["runtimeProjection"]["lemmas"].append(extra)
        self.assertRaisesCode(
            "FROZEN_RUNTIME_ID_GLOBAL_DUPLICATE",
            T.verified_runtime_from_frozen, forged)

    def test_a_runtime_revision_mismatch_is_refused(self):
        forged = self.frozen_copy()
        forged["runtimeProjection"]["patternDataRevision"] = 2
        self.assertRaisesCode(
            "FROZEN_RUNTIME_REVISION", T.verified_runtime_from_frozen, forged)

    def test_a_hand_written_malformed_projection_is_refused(self):
        self.assertIssueCode("RUNTIME_LEMMAS_REQUIRED", T.validate_runtime(
            {"formatVersion": 1, "patternDataRevision": 1, "lemmas": []},
            T.ValidationContext()))
        self.assertIssueCode("FORMAT_VERSION", T.validate_runtime(
            {"formatVersion": 2, "patternDataRevision": 1,
             "lemmas": type(self).runtime["lemmas"]}, T.ValidationContext()))

    def test_a_wrapped_document_is_not_the_public_shape(self):
        wrapped = dict(type(self).runtime, artifactStatus="anything")
        self.assertIssueCode("RUNTIME_PRIVATE_FIELD",
                             T.validate_runtime(wrapped, T.ValidationContext()))

    def test_content_mutated_inside_the_runtime_breaks_the_gate(self):
        forged = self.frozen_copy()
        forged["runtimeProjection"]["lemmas"][0]["canonicalLemma"] = "zmieniony"
        self.assertRaisesCode(
            "FROZEN_RUNTIME_REFLEXIVE_ASSERTION",
            T.verified_runtime_from_frozen, forged)


# ---------------------------------------------------------------------------
# §15  Determinism.
# ---------------------------------------------------------------------------
class DeterminismTests(Phase4FG1TestCase):

    def test_three_independent_freezes_produce_identical_bytes(self):
        digests = set()
        identifier_digests = set()
        for _ in range(3):
            runtime = T.verified_runtime_from_frozen(
                T.freeze_editorial(load_corpus(), EXPECTED_REVISION, load_context()))
            digests.add(sha256_text(serialize_runtime(runtime)))
            identifier_digests.add(
                id_set_digest(p["id"] for p in patterns_of(runtime)))
        self.assertEqual({RUNTIME_SHA256}, digests)
        self.assertEqual({PATTERN_ID_SET_DIGEST}, identifier_digests)

    def test_no_timestamp_or_random_identifier_entered_the_public_artifact(self):
        serialized = type(self).serialized
        self.assertEqual([], re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:", serialized))
        self.assertNotIn("generatedAt", serialized)
        self.assertNotIn("frozenAt", serialized)

    def test_ordering_is_stable_and_sorted_by_identifier(self):
        runtime = type(self).runtime
        lemma_ids = [lemma["id"] for lemma in runtime["lemmas"]]
        self.assertEqual(sorted(lemma_ids), lemma_ids)
        for lemma in runtime["lemmas"]:
            meaning_ids = [meaning["id"] for meaning in lemma["meanings"]]
            self.assertEqual(sorted(meaning_ids), meaning_ids)
            for meaning in lemma["meanings"]:
                pattern_ids = [pattern["id"] for pattern in meaning["patterns"]]
                self.assertEqual(sorted(pattern_ids), pattern_ids)


# ---------------------------------------------------------------------------
# §11 / §18  The release boundary Phase 4F-G1 did not cross.
# ---------------------------------------------------------------------------
class ReleaseBoundaryTests(Phase4FG1TestCase):

    def test_the_public_runtime_artifact_was_deliberately_not_materialized(self):
        """Superseded by Phase 4F-I1, which materialised a DIFFERENT runtime.

        G1 projected a 29-example runtime and deliberately left it unwritten.
        I1 released the completed 45-example corpus, so the file that exists
        now is the pinned I1 artifact and is provably not G1's bytes -- which
        is also the reason G1's own digest is recorded as historical.
        """
        self.assertEqual("complete", i1_bundle().state)
        released = (ROOT / PUBLIC_RUNTIME_PATH).read_bytes()
        self.assertEqual(I1.PHASE_4FI1_RUNTIME_SHA256,
                         hashlib.sha256(released).hexdigest())
        self.assertNotEqual(
            RUNTIME_SHA256,
            hashlib.sha256(released).hexdigest(),
            "the released runtime is not the Phase 4F-G1 projection")

    def test_materializing_it_here_would_break_the_atomic_release_bundle(self):
        """The reason the file is absent, stated against the guard itself.

        Phase 3F-A owns the rule.  Feeding it this phase's real projection with
        the shipping surface untouched reproduces exactly the six errors that
        make a lone runtime file illegal, so the boundary is evidence and not
        an opinion.
        """
        import test_priority7_phase3fa as F3A

        # Restated over the pre-Phase-4F-I1 shell and worker.  I1 is the
        # release that supplies all six missing halves; before it, feeding the
        # guard a lone runtime file still reproduces exactly these six errors.
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        loader = read_text("pp-verb-patterns.js")
        errors = F3A.release_bundle_errors(
            index, worker, loader, type(self).runtime,
            previous_index=index, previous_worker=worker)
        self.assertEqual(
            ["loader activation missing",
             "runtime path missing from application",
             "helper missing from required precache",
             "runtime missing from required precache",
             "APP_VERSION did not advance",
             "shell cache generation did not advance"],
            errors)
        # And with no runtime present, the same rule reports nothing at all.
        self.assertEqual([], F3A.release_bundle_errors(
            index, worker, loader, None,
            previous_index=index, previous_worker=worker))

    def test_no_application_wiring_was_added(self):
        # Restated over the pre-Phase-4F-I1 shell and worker: I1 is the phase
        # that adds the wiring, and it adds exactly the pinned layer.
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        for source in (index, worker):
            self.assertNotIn(PUBLIC_RUNTIME_PATH, source)
        self.assertNotIn("loadRuntimeDocument(", index)

    def test_app_version_and_shell_cache_are_unchanged(self):
        self.assertIn('const APP_VERSION = "8.10";', pre_i1("index.html"))
        self.assertIn('const CACHE = "popolsku-v65";', pre_i1("sw.js"))
        # The audio cache is deferred and unchanged, live as well as pre-I1.
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', read_text("sw.js"))

    def test_every_shipping_file_is_byte_identical_to_the_baseline_commit(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3.
        """
        for name in PROTECTED_SHIPPING_FILES:
            with self.subTest(path=name):
                baseline = bytes_at(BASELINE_COMMIT, name)
                self.assertIsNotNone(baseline, f"{name} missing at baseline")
                if i1_is_generated_output(name):
                    # Regenerated by the I1 release, and admitted only by its
                    # own pinned delta: <lastmod> values alone for the sitemap.
                    self.assertTrue(I1.is_exactly_the_i1_transition(
                        name, baseline.decode("utf-8"), read_text(name),
                        bundle=i1_bundle()), name)
                    continue
                text = i1_shipping_text(name)
                if H3.is_phase_4fh3_path(name):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(baseline, text.encode("utf-8"))

    def test_this_phase_wrote_only_tests_and_reports(self):
        """The footprint is stated against the baseline, not against HEAD.

        The claim must hold identically whether Phase 4F-G1 is still an
        uncommitted candidate or has been committed, so it reads both the
        working tree and everything committed since the baseline.
        """
        status = git("status", "--porcelain")
        self.assertEqual(0, status.returncode, status.stderr)
        changed = {
            line[3:].strip().strip('"')
            for line in status.stdout.splitlines() if line.strip()}
        committed = git("diff", "--name-only", BASELINE_COMMIT, "HEAD")
        if committed.returncode == 0:
            changed |= {
                line.strip() for line in committed.stdout.splitlines()
                if line.strip()}
        unexpected = sorted(
            path for path in changed
            if not path.startswith(("tests/", "reports/"))
            and not is_exactly_the_h2_content_completion(path)
            and not is_exactly_the_h3_ui_wording(path)
            and not is_only_the_i1_activation(path))
        self.assertEqual([], unexpected, f"no shipping file may change: {unexpected}")

    def test_no_release_or_push_action_occurred(self):
        """No remote exists, so nothing here could have been published.

        This deliberately makes no claim about which commit is checked out.
        A later phase may commit on top of this one without that being a
        release, and pinning HEAD would make this suite fail for the wrong
        reason the moment the phase is committed.
        """
        remotes = git("remote")
        self.assertEqual("", remotes.stdout.strip(), "this workspace has no remote")
        baseline = git("cat-file", "-t", BASELINE_COMMIT)
        self.assertEqual("commit", baseline.stdout.strip())
        baseline_tree = git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}")
        self.assertEqual(BASELINE_TREE, baseline_tree.stdout.strip())

    def test_the_editorial_workspace_still_holds_exactly_two_private_files(self):
        present = {
            str(path.relative_to(ROOT / "editorial"))
            for path in (ROOT / "editorial").rglob("*") if path.is_file()}
        self.assertEqual(
            {"verb-pattern-candidates.json", "priority-7-authoring-context.json"},
            present)


# ---------------------------------------------------------------------------
# §14  The report and manifest state the same numbers this suite proves.
# ---------------------------------------------------------------------------
class ReportArtifactTests(Phase4FG1TestCase):

    def test_the_manifest_matches_the_official_freeze_exactly(self):
        manifest = json.loads(read_text(MANIFEST_PATH))
        self.assertEqual(BASELINE_COMMIT, manifest["baselineCommit"])
        self.assertEqual(BASELINE_TREE, manifest["baselineTree"])
        self.assertEqual(CANONICAL_SHA256, manifest["canonicalSha256"])
        self.assertEqual(CONTEXT_SHA256, manifest["authoringContextSha256"])
        self.assertEqual(EXPECTED_REVISION, manifest["patternDataRevision"])
        self.assertEqual(T.FORMAT_VERSION, manifest["formatVersion"])
        self.assertEqual(RUNTIME_SHA256, manifest["runtimeSha256"])
        self.assertEqual(RUNTIME_BYTE_LENGTH, manifest["runtimeByteLength"])
        self.assertEqual(PATTERN_ID_SET_DIGEST, manifest["patternIdSetDigest"])
        self.assertEqual(LEMMA_ID_SET_DIGEST, manifest["lemmaIdSetDigest"])
        self.assertEqual(
            {"lemmas": EXPECTED_LEMMAS, "meanings": EXPECTED_MEANINGS,
             "patterns": EXPECTED_PATTERNS, "examples": EXPECTED_EXAMPLES,
             "contentRefs": EXPECTED_CONTENT_REFS,
             "errorNotes": EXPECTED_ERROR_NOTES},
            manifest["counts"])
        self.assertIs(False, manifest["publicArtifactMaterialized"])
        self.assertEqual(PUBLIC_RUNTIME_PATH, manifest["publicArtifactPath"])

    def test_the_manifest_carries_no_private_governance_data(self):
        serialized = read_text(MANIFEST_PATH)
        for identifier in SENSITIVE_IDENTIFIERS:
            with self.subTest(identifier=identifier):
                self.assertNotIn(identifier, serialized)
        manifest = json.loads(serialized)
        self.assertEqual(
            [], sorted(key for key, _ in walk_keys(manifest)
                       if key in T.FORBIDDEN_RUNTIME_KEYS))
        self.assertNotIn("lemmas", manifest)

    def test_the_summary_states_the_pinned_digests(self):
        summary = read_text(SUMMARY_PATH)
        for token in (BASELINE_COMMIT, BASELINE_TREE, CANONICAL_SHA256,
                      RUNTIME_SHA256, PATTERN_ID_SET_DIGEST):
            with self.subTest(token=token[:16]):
                self.assertIn(token, summary)


if __name__ == "__main__":
    unittest.main()
