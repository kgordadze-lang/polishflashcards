"""Priority 7 Phase 3D-1 - the synthetic grammar-choose mechanics prototype.

Phase 3B proved the passive reference surface; Phase 3C connected it to existing
content.  Phase 3D-1 asks one engineering question and answers it by building:
*can the existing Grammar ``choose`` mechanics carry a future verb-pattern
practice item without a second activity engine?*  It answers it against records
that are obviously synthetic, through a path no learner can reach.

Four things need proving here, at the file and corpus level:

  1. the synthetic exercise fixture is a TEST INPUT.  It is wrapped, it says in
     its own bytes that it is not release-authorised, it lives only under
     ``tests/fixtures/priority7/``, and no shipping file can name it, fetch it or
     unwrap it;
  2. its identifiers are UNMISTAKABLY NONCANONICAL.  Every one is test-scoped,
     none sits in the reserved ``vp-`` release family, and this phase allocates,
     freezes and persists no real exercise identity at all;
  3. ordinary startup is UNCHANGED.  No extra level, no extra tile, no extra
     screen, no route, no request and no call site reaches the prototype;
  4. the real corpus, the review state, the activity allowlists, the audio
     eligibility, the storage schema and every version and cache marker are
     exactly where Phase 3C left them.

The behavioural proof - the adapter, the round, the choice mechanics, feedback,
focus, injection safety and the layout contract - lives in
``tests/test_priority7_choose_ui.js``, which executes the shipping code.  This
module is the file- and corpus-level half.

Nothing here is a linguistic claim, an activity-eligibility decision, a review
outcome or a release authorisation, and Phase 3D-2 remains blocked.

Run:  python3 -m unittest tests.test_priority7_phase3d1
"""

import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import build_pages

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
INDEX = ROOT / "index.html"
LOADER = ROOT / "pp-verb-patterns.js"
WORKER = ROOT / "sw.js"
SITEMAP = ROOT / "sitemap.xml"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "priority7"
EXERCISE_FIXTURE = FIXTURE_DIR / "exercise-fixture.json"
RUNTIME_FIXTURE = FIXTURE_DIR / "runtime-fixture.json"
EDITORIAL_CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
UI_SUITE = ROOT / "tests" / "test_priority7_choose_ui.js"

EXERCISE_MARKER = "priority-7-exercise-fixture-synthetic-nonrelease"
MARK = "SYNTHETIC-NONRELEASE"
# The test-only identifier namespace this phase uses, and the release namespace
# it must stay outside of.  `vp-x-...` is the Priority 7 stable-ID specification's
# reserved family for real activity items; nothing in this phase may allocate,
# freeze, persist or resemble one.
TEST_ID_PREFIX = "p7-fixture-"
RESERVED_ID_PREFIX = "vp-"
RESERVED_EXERCISE_FAMILY = "vp-x-"

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


def read(path):
    return Path(path).read_text(encoding="utf-8")


def fixture():
    return json.loads(read(EXERCISE_FIXTURE))


def items():
    return fixture()["syntheticExercises"]["items"]


def flat(value):
    """The words a learner sees, whichever form the field takes.

    A text field is either a plain string - one language for the whole of it -
    or a list of ``{text, lang}`` fragments.  Fragments exist because a
    structural label genuinely mixes languages, and the record is where those
    languages are known; deriving them in the consumer would be the consumer
    inventing a linguistic claim.
    """
    if isinstance(value, list):
        return "".join(part["text"] for part in value)
    return "" if value is None else str(value)


def text_fields(item):
    """Every learner-facing string in one record, flattened."""
    out = [flat(item[name]) for name in
           ("prompt", "feedbackStructure", "feedbackExplanation")]
    out += [flat(item[name]) for name in ("promptEn", "cue") if name in item]
    out += [flat(option["label"]) for option in item["options"]]
    return out


class SyntheticExerciseFixtureTests(unittest.TestCase):
    """The fixture is a test input, and says so in its own bytes."""

    def test_the_fixture_is_wrapped_and_declares_itself_non_release(self):
        doc = fixture()
        self.assertEqual(EXERCISE_MARKER, doc["artifactStatus"])
        self.assertIs(False, doc["releaseAuthorized"])
        self.assertIn(MARK, doc["fixtureNotice"])
        # The wrapper is load-bearing, not decorative: the payload is reachable
        # only by stepping through it deliberately.
        self.assertEqual({"artifactStatus", "releaseAuthorized", "fixtureNotice",
                          "syntheticExercises"}, set(doc))
        self.assertEqual({"fixtureFormat", "items"}, set(doc["syntheticExercises"]))
        self.assertEqual(1, doc["syntheticExercises"]["fixtureFormat"])

    def test_the_fixture_covers_the_required_mechanics_shapes(self):
        """One compact set, ten shapes, no second corpus."""
        got = [item["exerciseId"] for item in items()]
        self.assertEqual(10, len(got))
        self.assertEqual(len(got), len(set(got)))
        for shape in ("single-case", "preposition-case", "same-case-two-structures",
                      "multi-complement", "infinitive-vs-nominal",
                      "clause-vs-nominal", "lexical-sie", "recognition-shaped",
                      "hostile-text", "long-wrapping-text"):
            with self.subTest(shape=shape):
                self.assertTrue(any(shape in name for name in got), shape)

    def test_every_item_is_one_activity_family_with_one_intended_answer(self):
        for item in items():
            with self.subTest(item=item["exerciseId"]):
                self.assertEqual("grammar-choose", item["activityType"])
                values = [option["value"] for option in item["options"]]
                self.assertGreaterEqual(len(values), 2)
                self.assertEqual(len(values), len(set(values)),
                                 "two options may not share an identity")
                self.assertEqual(
                    1, values.count(item["answerValue"]),
                    "exactly one option is the intended answer")
                # Scoring must never be able to fall back on the words on the
                # button or on the position an option occupies.
                for option in item["options"]:
                    self.assertNotEqual(option["value"], flat(option["label"]))

    def test_orders_are_explicit_unique_and_never_the_scoring_key(self):
        orders = [item["order"] for item in items()]
        self.assertEqual(sorted(orders), orders)
        self.assertEqual(len(orders), len(set(orders)))
        self.assertEqual(list(range(1, len(orders) + 1)), orders)
        # The intended answer is not always in the same slot, so a fixture that
        # was scored by position would fail rather than pass by accident.
        positions = {
            [option["value"] for option in item["options"]].index(item["answerValue"])
            for item in items()
        }
        self.assertGreater(len(positions), 1)

    def test_no_runtime_pattern_object_is_duplicated_into_an_item(self):
        """An item names its owning pattern; it never carries a copy of one."""
        allowed = {"exerciseId", "patternRef", "activityType", "order", "prompt",
                   "promptEn", "cue", "options", "answerValue",
                   "feedbackStructure", "feedbackExplanation"}
        for item in items():
            with self.subTest(item=item["exerciseId"]):
                self.assertTrue(set(item) <= allowed, set(item) - allowed)
                self.assertIsInstance(item["patternRef"], str)
                for forbidden in ("complements", "cefr", "teachingStatus",
                                  "activityEligibility", "relationType",
                                  "learnerExplanationEn", "contentRefs",
                                  "examples", "usage", "errorNotes"):
                    self.assertNotIn(forbidden, item)

    def test_learner_facing_text_carries_its_own_language(self):
        """The record declares the languages; no consumer derives them.

        A structural label mixes languages - Polish diagnostic questions, a
        separator, an English case name - so the fixture authors it as explicit
        ``{text, lang}`` fragments.  That is the only representation in the
        record: there is no second, separately formatted copy for the status
        region to drift away from.
        """
        for item in items():
            with self.subTest(item=item["exerciseId"]):
                for name in ("prompt", "feedbackStructure"):
                    self.assertIsInstance(item[name], list, name)
                for option in item["options"]:
                    self.assertIsInstance(option["label"], list, option["value"])
                # English-only fields stay plain strings and are never marked.
                for name in ("promptEn", "cue", "feedbackExplanation"):
                    if name in item:
                        self.assertIsInstance(item[name], str, name)

    def test_every_fragment_is_well_formed_and_none_is_blank(self):
        for item in items():
            for name, value in (("prompt", item["prompt"]),
                                ("feedbackStructure", item["feedbackStructure"]),
                                *[(o["value"], o["label"]) for o in item["options"]]):
                with self.subTest(item=item["exerciseId"], field=name):
                    self.assertTrue(value, "a field may not be an empty list")
                    for part in value:
                        self.assertEqual(
                            set(part) - {"lang"}, {"text"},
                            "a fragment carries text and, optionally, lang")
                        self.assertTrue(part["text"], "no fragment may be empty")
                        if "lang" in part:
                            self.assertTrue(part["lang"].strip())
                    self.assertTrue(flat(value).strip(),
                                    "fragments must add up to something visible")
                    # Adjacent fragments in one language would be two spans where
                    # one belongs, and would read as two runs to a screen reader.
                    for before, after in zip(value, value[1:]):
                        self.assertNotEqual(before.get("lang"), after.get("lang"))

    def test_mixed_labels_are_split_rather_than_wrapped_in_one_language(self):
        """The finding: `kogo? czego? · Genitive` is not one language.

        Marking all of it Polish makes a screen reader pronounce "Genitive" as
        Polish; marking none of it makes it pronounce the Polish half as English.
        Every mixed label here therefore carries at least one Polish fragment and
        at least one unmarked (document-language) fragment.
        """
        mixed = 0
        for item in items():
            for option in item["options"]:
                label = option["label"]
                if len(label) == 1:
                    continue
                mixed += 1
                with self.subTest(option=option["value"]):
                    self.assertTrue(any(part.get("lang") == "pl" for part in label))
                    self.assertTrue(any("lang" not in part for part in label))
                    # The English half must be the case name, never the questions.
                    for part in label:
                        if "lang" in part:
                            continue
                        self.assertNotIn("?", part["text"],
                                         "a diagnostic question is Polish")
        self.assertGreaterEqual(mixed, 20, "the fixture must exercise mixed labels")

    def test_english_explanatory_text_is_never_marked_polish(self):
        for item in items():
            with self.subTest(item=item["exerciseId"]):
                self.assertIsInstance(item["feedbackExplanation"], str)
                self.assertTrue(flat(item["feedbackExplanation"]).startswith(MARK))
                if "promptEn" in item:
                    self.assertTrue(flat(item["promptEn"]).startswith(MARK))

    def test_no_private_editorial_or_review_field_is_present_at_any_depth(self):
        from priority7_tooling import PRIVATE_RUNTIME_KEYS

        def walk(node, path=""):
            if isinstance(node, dict):
                for key, value in node.items():
                    # `artifactStatus` is the wrapper's own non-release marker and
                    # is exactly why the shipping adapter refuses this document.
                    if path or key != "artifactStatus":
                        self.assertNotIn(key, PRIVATE_RUNTIME_KEYS, f"{path}.{key}")
                    walk(value, f"{path}.{key}")
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    walk(value, f"{path}[{i}]")

        walk(fixture())

    def test_the_fixture_exercises_hostile_and_long_learner_facing_text(self):
        by_id = {item["exerciseId"]: item for item in items()}
        hostile = next(v for k, v in by_id.items() if "hostile-text" in k)
        for field in ("prompt", "cue", "feedbackStructure", "feedbackExplanation"):
            with self.subTest(field=field):
                self.assertTrue(
                    re.search(r"<\w+|javascript:|on\w+=", flat(hostile[field])),
                    f"{field} must carry hostile text")
        self.assertTrue(
            any(re.search(r"<\w+", flat(option["label"]))
                for option in hostile["options"]),
            "at least one option label must carry hostile text")
        # Hostile text also has to survive INSIDE a language fragment, which is
        # the case a naive "wrap the whole label" implementation would get wrong.
        self.assertTrue(
            any(re.search(r"<\w+", part["text"]) and part.get("lang")
                for part in hostile["prompt"]),
            "the hostile prompt must sit inside a language fragment")
        long_item = next(v for k, v in by_id.items() if "long-wrapping-text" in k)
        self.assertGreater(len(flat(long_item["prompt"])), 200)
        self.assertGreater(len(flat(long_item["feedbackExplanation"])), 250)
        self.assertTrue(
            all(len(flat(option["label"])) > 120 for option in long_item["options"]),
            "every option in the wrapping case must be long, not just the answer")


class StableIdSpaceTests(unittest.TestCase):
    """No real exercise identity is allocated, frozen, persisted or resembled."""

    def test_every_fixture_identifier_is_test_scoped(self):
        for item in items():
            for field in ("exerciseId", "patternRef"):
                with self.subTest(item=item["exerciseId"], field=field):
                    value = item[field]
                    self.assertTrue(value.startswith(TEST_ID_PREFIX), value)
                    self.assertFalse(value.startswith(RESERVED_ID_PREFIX), value)
                    self.assertNotIn(RESERVED_EXERCISE_FAMILY, value)

    def test_no_fixture_identifier_could_be_reused_as_a_release_identity(self):
        """A release id is `vp-<family>-<stem>-<12 hex>`; none of these is."""
        release_shape = re.compile(r"^vp-[lmpex]-[a-z0-9-]+-[0-9a-f]{12}$")
        for item in items():
            for field in ("exerciseId", "patternRef"):
                with self.subTest(item=item["exerciseId"], field=field):
                    self.assertIsNone(release_shape.match(item[field]))

    def test_the_adapter_refuses_the_reserved_release_family_outright(self):
        loader = read(LOADER)
        self.assertIn('var RESERVED_ID_PREFIX = "vp-";', loader)
        self.assertIn(
            "if (!usableId(item.exerciseId) || !usableId(item.patternRef)) return null;",
            loader)

    def test_this_phase_allocates_no_real_exercise_id_anywhere(self):
        """No shipping file, corpus or projection holds a `vp-x-...` identity.

        The exercise fixture's own notice and the JXA suite both NAME the
        reserved family - one to say it stays outside it, the other to prove the
        adapter refuses it - which is the opposite of allocating one.  What must
        stay clean is everything that could carry an identity forward.
        """
        for path in (INDEX, LOADER, WORKER, SITEMAP, RUNTIME_FIXTURE,
                     EDITORIAL_CORPUS,
                     ROOT / "editorial" / "priority-7-authoring-context.json"):
            with self.subTest(path=path.name):
                self.assertNotIn(RESERVED_EXERCISE_FAMILY, read(path))
        # In the fixture, the family may appear only in the prose notice, never
        # as the value of an identifier field.
        self.assertNotIn(
            RESERVED_EXERCISE_FAMILY,
            json.dumps([[item["exerciseId"], item["patternRef"]] for item in items()]))

    def test_no_frozen_allocation_tombstone_or_candidate_record_was_created(self):
        corpus = json.loads(read(EDITORIAL_CORPUS))
        text = read(EDITORIAL_CORPUS)
        self.assertNotIn("grammar-choose", text)
        self.assertNotIn(TEST_ID_PREFIX, text)
        for registry in ("allocationRegistry", "tombstoneRegistry", "frozen"):
            self.assertNotIn(f'"{registry}"', text)
        # The corpus knows nothing about exercises, and gained nothing here.
        self.assertNotIn("exercise", text.lower())
        self.assertEqual(30, len(corpus["lemmas"]))


class HarnessBoundaryTests(unittest.TestCase):
    """Shipping code can neither name, fetch nor unwrap the fixture."""

    def test_the_fixture_lives_only_under_the_approved_test_path(self):
        self.assertTrue(EXERCISE_FIXTURE.is_file())
        # EXTENDED by Priority 7 Phase 5-A, not relaxed: the synthetic private
        # editorial fixture and its test-only loader harness join the same
        # enumerated, test-only directory.
        self.assertEqual(
            ["exercise-fixture.json", "phase5a-loader-harness.js",
             "release-runtime-fixture.json", "runtime-fixture.json",
             "synthetic-release-editorial.json"],
            sorted(path.name for path in FIXTURE_DIR.rglob("*") if path.is_file()))
        for directory in ("content", "grammar", "vocabulary", "guide", "audio", ""):
            with self.subTest(directory=directory or "<root>"):
                self.assertFalse((ROOT / directory / "exercise-fixture.json").exists())

    def test_no_shipping_file_can_name_or_reach_the_fixture(self):
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        public = "\n".join([read(INDEX), read(LOADER), read(WORKER), read(SITEMAP),
                            *outputs.values()])
        # `artifactStatus` is excluded deliberately: the loader names it in its
        # private-key REJECTION list, which is how the wrapper is refused.
        for marker in ("exercise-fixture", "tests/fixtures", EXERCISE_MARKER, MARK,
                       "syntheticExercises", "releaseAuthorized", "fixtureNotice",
                       TEST_ID_PREFIX):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, public)
        # Nor may any synthetic sentence appear in a shipped file.  Option LABELS
        # are excluded on purpose: they deliberately reuse the app's own central
        # chip vocabulary ("+ bezokolicznik · Infinitive"), which is shipping
        # code the fixture quotes rather than fixture content that escaped.
        for item in items():
            with self.subTest(item=item["exerciseId"]):
                self.assertNotIn(flat(item["prompt"]), public)
                self.assertNotIn(flat(item["feedbackExplanation"]), public)
                self.assertNotIn(flat(item["feedbackStructure"]), public)
        self.assertEqual(32, len(ET.fromstring(read(SITEMAP))))

    def test_shipping_code_cannot_unwrap_the_exercise_envelope(self):
        """The unwrap step exists in test code only."""
        for path in (INDEX, LOADER):
            source = read(path)
            with self.subTest(path=path.name):
                for token in ("syntheticExercises", "runtimeProjection",
                              "releaseAuthorized", "fixtureNotice",
                              '"tests/', "'tests/", "fixtures", "runtime-fixture",
                              "exercise-fixture", "editorial/"):
                    self.assertNotIn(token, source)
        self.assertNotIn("__acceptForTest", read(INDEX))

    def test_the_harness_asserts_the_wrapper_before_it_reads_the_payload(self):
        suite = read(UI_SUITE)
        self.assertIn("function unwrapSyntheticExercisesForTest(wrapped)", suite)
        for guard in ("wrapped.artifactStatus !== EXERCISE_MARKER",
                      "wrapped.releaseAuthorized !== false"):
            with self.subTest(guard=guard):
                self.assertIn(guard, suite)
                self.assertLess(
                    suite.index(guard),
                    suite.index("return clone(wrapped.syntheticExercises.items);"),
                    "the harness must assert before it reads")

    def test_the_test_and_shipping_paths_stay_mechanically_distinguishable(self):
        loader = read(LOADER)
        # One shipping entry for pattern data, one test-only injection entry, and
        # an adapter that takes already-unwrapped records and nothing else.
        self.assertIn("acceptRuntimeDocument: accept,", loader)
        self.assertIn("__acceptForTest: accept,", loader)
        self.assertIn("grammarChooseDrills: grammarChooseDrills,", loader)
        self.assertNotIn("__acceptForTest", read(INDEX))


class ValidationHardeningTests(unittest.TestCase):
    """Source-level guards for the two ways validation was talked out of itself.

    The behavioural proof is in ``tests/test_priority7_choose_ui.js``; these
    assertions exist so a silent regression to the old constructs is caught in
    the diff rather than only in a behaviour that happens to be tested.
    """

    def _adapter(self):
        loader = read(LOADER)
        return loader[loader.index("function grammarChooseDrill(item)"):
                      loader.index("function patternOrder(")]

    def test_uniqueness_sets_carry_no_prototype(self):
        """`{}` is not a uniqueness set: `d["__proto__"] = x` sets no own key."""
        adapter = self._adapter()
        self.assertNotIn("= {}", adapter)
        self.assertEqual(3, adapter.count("emptyDict()"))
        self.assertEqual(3, adapter.count("seenBefore("))
        self.assertIn("return Object.create(null);", read(LOADER))

    def test_required_text_rejects_blank_looking_values(self):
        adapter = self._adapter()
        # Every required-text check goes through the filled/text validators; the
        # bare length check is not enough on its own here.
        self.assertNotIn("isNonEmptyString(item.", adapter)
        self.assertNotIn("isNonEmptyString(option.", adapter)
        self.assertIn("function isFilledString(value)", read(LOADER))
        self.assertIn("/\\S/.test(value)", read(LOADER))

    def test_recognised_optional_fields_are_read_as_own_properties_only(self):
        """`in` answers for the prototype chain; a record is its own properties.

        Reading an inherited optional field would also run an inherited getter -
        somebody else's code, executed during validation - so presence is asked
        with hasOwnProperty and the value is never touched otherwise.
        """
        adapter = self._adapter()
        for token in ('" in item', '" in fragment', '" in option', '" in value'):
            with self.subTest(token=token):
                self.assertNotIn(token, adapter)
        self.assertIn('hasOwn(item, "promptEn")', adapter)
        self.assertIn('hasOwn(item, "cue")', adapter)
        loader = read(LOADER)
        self.assertIn('!hasOwn(fragment, "lang")', loader)
        self.assertIn('if (hasOwn(fragment, "lang") && isFilledString(fragment.lang))',
                      loader)
        self.assertIn("function hasOwn(value, key)", loader)

    def test_a_settled_mixed_option_is_never_flattened_into_one_aria_label(self):
        """An aria-label replaces the computed name and loses the languages.

        A structured option therefore appends its verdict as visually hidden
        text inside itself, keeping a name computed from its own language-tagged
        children.  A plain string option is one language, so the aria-label it
        has always had loses nothing and is retained.
        """
        index = read(INDEX)
        self.assertIn("function gSetOptionVerdict(btn, label, verdict){", index)
        verdict = index[index.index("function gSetOptionVerdict(btn, label, verdict){"):
                        index.index("/* Which words a given option shows")]
        self.assertIn("if(!Array.isArray(label))", verdict)
        self.assertIn('gTextEl("span","sr-only")', verdict)
        # Exactly one aria-label write in it, on the string branch only.
        self.assertEqual(1, verdict.count("setAttribute(\"aria-label\""))
        # And the choose path writes option verdicts through it and nowhere else.
        for name in ("gRenderChoose", "gRevealChooseAnswer"):
            body = index[index.index("function " + name + "("):]
            body = body[:body.index("\n}")]
            with self.subTest(function=name):
                self.assertNotIn('setAttribute("aria-label"', body)
                self.assertIn("gSetOptionVerdict(", body)
        # No Priority 7 branch decides any of it.
        for token in ("priority7", "PP_VERB_PATTERNS", "patternRef", "p7-fixture"):
            with self.subTest(token=token):
                self.assertNotIn(token, verdict)

    def test_validation_never_rewrites_the_record_it_was_handed(self):
        adapter = self._adapter()
        for token in (".trim()", "= value.trim", "item.prompt =", "option.label ="):
            with self.subTest(token=token):
                self.assertNotIn(token, adapter)

    def test_the_completion_summary_is_derived_from_what_happened(self):
        index = read(INDEX)
        self.assertIn("function gRetryOutcome(){", index)
        self.assertIn("function gDoneMessage(score, total){", index)
        # `G.results` records first-try only, so it cannot answer "was this
        # retry cleared" and must not be the source for that sentence.
        outcome = index[index.index("function gRetryOutcome(){"):
                        index.index("function gDoneMessage(")]
        self.assertIn("_requeue", outcome)
        self.assertNotIn("G.results", outcome)
        self.assertEqual(1, index.count("G.cleared=[]"))

    def test_the_completion_copy_cannot_claim_an_uncleared_retry_was_cleared(self):
        index = read(INDEX)
        message = index[index.index("function gDoneMessage(score, total){"):
                        index.index("function gShowDone(){")]
        self.assertIn("if(!retry.open) return lead+\" and you cleared \"", message)
        self.assertIn("still need", message)
        for word in ("master", "unlock", "saved", "approved"):
            with self.subTest(word=word):
                self.assertNotIn(word, message.lower())


class OrdinaryStartupTests(unittest.TestCase):
    """A learner cannot reach the prototype, by any route."""

    def test_no_activity_entry_point_is_called_by_the_shipping_shell(self):
        index = read(INDEX)
        # Defined exactly once - its own declaration - and invoked nowhere.
        self.assertEqual(1, index.count("pStartChoosePractice"))
        self.assertEqual(1, index.count("grammarChooseDrills"))
        self.assertEqual(0, index.count("grammarChooseDrill("))

    def test_no_tile_level_screen_or_route_was_added(self):
        index = read(INDEX)
        self.assertEqual(2, index.count("LEVELS.push("))
        self.assertEqual(1, index.count('level:"Verb Patterns"'))
        self.assertEqual(1, index.count("CATEGORIES = ["))
        self.assertEqual(11, index.count('<section class="screen"'))
        for token in ("Practice these verbs", "pill-practice-pattern",
                      "startPatternPractice", "patterns-practice"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)

    def test_no_activation_switch_of_any_kind_was_added(self):
        index = read(INDEX)
        # `location.search` is excluded: the shell has used it since long before
        # Priority 7, to preserve an existing query string across history
        # replacement.  It reads no parameter and switches nothing on.
        for token in ("URLSearchParams", "searchParams", "get(\"fixture",
                      "?fixture", "loadFixture", "devMenu", "debugMode",
                      "pp-dev", "enablePractice"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)

    def test_startup_still_makes_no_request_for_priority_7_data(self):
        # Superseded by Phase 4F-I1's one production activation; restated over
        # the shell with the pinned I1 layer removed.
        index = pre_i1("index.html")
        self.assertEqual(2, index.count("fetch("))
        self.assertNotIn("content/", index)
        self.assertNotIn("verb-patterns.json", index)
        for token in ("XMLHttpRequest", "EventSource", "importScripts"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)

    def test_the_service_worker_learned_nothing_about_this_phase(self):
        # Superseded by Phase 4F-I1, which is the release that gives the worker
        # its runtime entry; restated over the pre-I1 worker.
        worker = pre_i1("sw.js")
        for token in ("exercise-fixture", "verb-patterns", "pp-verb-patterns",
                      "grammar-choose", TEST_ID_PREFIX):
            with self.subTest(token=token):
                self.assertNotIn(token, worker)


class NoPersistenceTests(unittest.TestCase):
    """Nothing is written, migrated, measured or remembered."""

    ENTRY = "function pStartChoosePractice(items){"

    def _entry_source(self):
        index = read(INDEX)
        start = index.index(self.ENTRY)
        return index[start:index.index("\n}", start)]

    def test_the_practice_entry_writes_nothing(self):
        source = self._entry_source()
        for token in ("localStorage", "sessionStorage", "indexedDB", "document.cookie",
                      "rRecord", "saveV2", "loadV2", "persistProgress", "fetch(",
                      "innerHTML", "gtag", "sendBeacon", "navigator.send"):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

    def test_the_adapter_writes_nothing_and_measures_nothing(self):
        loader = read(LOADER)
        for token in ("localStorage", "sessionStorage", "indexedDB", "cookie",
                      "gtag", "analytics", "sendBeacon", "fetch(", "XMLHttpRequest"):
            with self.subTest(token=token):
                self.assertNotIn(token, loader)

    def test_no_mastery_or_completion_concept_was_created(self):
        index, loader = read(INDEX), read(LOADER)
        for token in ("patternMastery", "patternProgress", "completedPatterns",
                      "patternStrength", "masteredPatterns"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)
                self.assertNotIn(token, loader)

    def test_the_storage_schema_and_migration_revision_are_unmoved(self):
        migrate = read(ROOT / "pp-migrate.js")
        self.assertIn("schemaVersion: 2", migrate.replace("schemaVersion:2",
                                                          "schemaVersion: 2"))
        self.assertIn("CONTENT_MIGRATION_REVISION = 2", migrate.replace(
            "CONTENT_MIGRATION_REVISION=2", "CONTENT_MIGRATION_REVISION = 2"))
        self.assertNotIn("grammar-choose", migrate)
        self.assertNotIn(TEST_ID_PREFIX, migrate)


#: The commit Phase 4F-A produced; its review history is the checkpoint.
#: Phase 4F-B3B.1 appended one fresh tier-1 acceptance to each of the two rows
#: whose optionality correction moved their reference scope, and rewrote none
#: of the original 45.  Asserting 47 as "Phase 4F-A's inventory" would rewrite
#: history; asserting 45 as the current total would deny the refresh.
PHASE_4FA_CHECKPOINT_COMMIT = "7beb50d7b3463d7745352f1608f1e30019529fdf"

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


class ReleaseBoundaryTests(unittest.TestCase):
    """The corpus, the review state and every marker are where 3C left them."""

    def test_the_real_corpus_is_untouched_research_with_no_review(self):
        # Phase 4F-E1's approved tier-2 acceptances are reverted first, so the
        # historical state and event-count claims below still mean what they
        # meant when they were written.  Shape, eligibility and audio -- what
        # this test actually guards -- are unaffected by that normalisation
        # because Phase 4F-E1 touched none of them.
        corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(
                        json.loads(read(EDITORIAL_CORPUS))))))
        states, events, eligibility, audio, meanings = [], 0, 0, 0, 0
        for lemma in corpus["lemmas"]:
            for meaning in lemma["meanings"]:
                meanings += 1
                for pattern in meaning["patterns"]:
                    states.append(pattern["reviewState"])
                    events += len(pattern["reviewEvents"])
                    eligibility += len(pattern["activityEligibility"])
                    audio += sum(1 for example in pattern.get("examples", [])
                                 if example["audioEligible"])
        self.assertEqual(30, len(corpus["lemmas"]))
        self.assertEqual(34, meanings)
        self.assertEqual(45, len(states))
        # Phase 4F-A raised all 45 rows to tier 1 of three, and Phase 4F-B3B.1
        # appended two fresh tier-1 acceptances for the rows whose optionality
        # correction moved their reference scope.  Everything this test
        # actually guards -- shape, eligibility, audio -- is unmoved.
        self.assertEqual({"reference-verified"}, set(states))
        self.assertEqual(PHASE_4FA_EVENT_COUNT,
                         sum(len(history) for history in
                             phase_4fa_review_events().values()))
        self.assertEqual(CURRENT_EVENT_COUNT, events)
        self.assertEqual(0, eligibility, "no real pattern became eligible")
        self.assertEqual(0, audio)

    def test_no_reviewer_or_author_identity_was_created_by_this_phase(self):
        """3D-1 itself created no identity; Phase 4C later named one reviewer.

        The original assertion pinned both registries as empty.  Phase 4C named
        a real human native-linguistic reviewer, so the reviewerRegistry is now
        pinned to exactly that one native-only identity instead of to ``{}``.
        Phase 4F-F2 later registered the human product owner; that approved
        registration is reverted before the identity claim is made, so this
        still states what it stated when written.  The authorRegistry
        assertion is unchanged, live and still fail-closed: no human example
        author exists, and product approval created none.
        """
        live_context = json.loads(
            read(ROOT / "editorial" / "priority-7-authoring-context.json"))
        context = F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(live_context)))
        self.assertEqual({}, live_context.get("authorRegistry", {}) or {})
        reviewers = context.get("reviewerRegistry", {}) or {}
        self.assertEqual({"native-reviewer-001"}, set(reviewers))
        self.assertEqual(["native-linguistic"],
                         reviewers["native-reviewer-001"]["roles"])

    def test_the_synthetic_fixture_leaks_no_real_corpus_content(self):
        """No real lemma, identity, explanation, example or gloss got in.

        Distinctive strings - lemmas, ids, explanations, example sentences - are
        swept as substrings.  Glosses are compared as WHOLE VALUES rather than as
        substrings, because the corpus contains bare English verbs ("ask",
        "use", "learn") that occur incidentally in ordinary English prose; a
        substring sweep over those would fail on any sentence in English and
        would prove nothing about content having leaked.
        """
        corpus = json.loads(read(EDITORIAL_CORPUS))
        haystack = read(EXERCISE_FIXTURE)
        real_glosses = set()
        fixture_values = set()
        for item in items():
            fixture_values.update(text_fields(item))
        for lemma in corpus["lemmas"]:
            with self.subTest(lemma=lemma["canonicalLemma"]):
                self.assertNotIn(lemma["canonicalLemma"], haystack)
                self.assertNotIn(lemma["id"], haystack)
            for meaning in lemma["meanings"]:
                real_glosses.update(meaning["glossesEn"])
                for pattern in meaning["patterns"]:
                    self.assertNotIn(pattern["id"], haystack)
                    self.assertNotIn(pattern["learnerExplanationEn"], haystack)
                    for example in pattern.get("examples", []):
                        self.assertNotIn(example["pl"], haystack)
                        self.assertNotIn(example["en"], haystack)
        self.assertEqual(set(), fixture_values & real_glosses)

    def test_no_public_priority_7_runtime_artifact_exists(self):
        # Superseded by Phase 4F-I1: the only runtime document that may exist
        # is exactly the I1 release artifact, pinned by digest.
        self.assertEqual("complete", i1_bundle().state)

    def test_version_and_cache_markers_are_unmoved(self):
        index, worker = pre_i1("index.html"), pre_i1("sw.js")
        self.assertIn('APP_VERSION="8.10"',
                      index.replace('APP_VERSION = "8.10"', 'APP_VERSION="8.10"'))
        self.assertIn('const CACHE="popolsku-v65"',
                      worker.replace('const CACHE = "popolsku-v65"',
                                     'const CACHE="popolsku-v65"'))
        self.assertIn("popolsku-audio", worker)
        self.assertNotIn("patternDataRevision", index)
        self.assertNotIn("patternDataRevision", worker)

    def test_nothing_here_claims_approval_review_or_release(self):
        for path in (INDEX, LOADER, EXERCISE_FIXTURE):
            source = read(path)
            if path is LOADER:
                # The loader names the private review keys in order to REFUSE
                # them; that list is the guard, not a claim.
                source = source[source.index("var CASE_ORDER"):]
            with self.subTest(path=path.name):
                for token in ("release-ready", "releaseAuthorized: true",
                              "reviewState", "nativeReview", "isRelease"):
                    self.assertNotIn(token, source)
        notice = fixture()["fixtureNotice"]
        self.assertIn("nothing here was reviewed", notice)
        self.assertIn("no statement in it is a claim about Polish", notice)

    def test_phase_3d2_prerequisites_are_all_still_unmet(self):
        """Completing 3D-1 moves none of them, and this states which.

        Phase 4F-E1 is the first phase to move any of them: it registered the
        tier-2 editorial actors and reached ``editorial-reviewed``.  Phase
        4F-F2 then met the product-approval prerequisites by registering a
        human product owner and recording 45 approvals.  Every historical
        claim is therefore stated over the normalised corpus and context,
        where it still says what it said when written.  The one prerequisite
        neither phase met -- the empty author registry -- stays asserted
        against the live file, where it is what still blocks 3D-2.
        """
        live_corpus = json.loads(read(EDITORIAL_CORPUS))
        live_context = json.loads(
            read(ROOT / "editorial" / "priority-7-authoring-context.json"))
        corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live_corpus))))
        context = E1.without_phase_4fe1_actors(
            F2.without_phase_4ff2_reviewer(
                H2.without_phase_4fh2_context(
                    H21.without_phase_4fh21_context(live_context))))
        advanced = [
            pattern for lemma in corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
            if pattern["reviewState"] not in {"research", "reference-verified"}
        ]
        self.assertEqual([], advanced, "no pattern passed tier 1")
        # Phase 4C named a native reviewer but could record no review event.
        # Phase 4F-A registered a nonhuman reference actor and reached tier 1.
        # The prerequisites that still block 3D-2 are the empty authorRegistry,
        # the unregistered editorial actor and the absent product authority.
        self.assertEqual({}, context.get("authorRegistry", {}) or {})
        actors = context.get("editorialActorRegistry", {})
        self.assertIn("priority7-reference-analysis", actors)
        # Stated as the missing capability rather than as a closed key set:
        # what blocks 3D-2 is that no actor can perform the tier-2 editorial
        # review, not how many workflow identities happen to be registered.
        # Phase 4F-C2's example generator holds no review role.
        self.assertEqual(
            [], [actor_id for actor_id, record in actors.items()
                 if "editorial-review" in (record.get("roles") or [])])
        self.assertEqual(
            {"reference-verification"},
            {event["kind"]
             for lemma in corpus["lemmas"]
             for meaning in lemma["meanings"]
             for pattern in meaning["patterns"]
             for event in pattern["reviewEvents"]})
        # Phase 4F-F2 met the product-approval prerequisites: it registered a
        # human product owner and recorded 45 approvals.  Those three claims
        # are therefore made over the normalised view, where they still say
        # what they said when written.
        self.assertEqual(
            [], [reviewer_id
                 for reviewer_id, record in
                 (context.get("reviewerRegistry") or {}).items()
                 if "product-approval" in (record.get("roles") or [])])
        self.assertNotIn(
            "approved",
            {pattern["reviewState"] for lemma in corpus["lemmas"]
             for meaning in lemma["meanings"]
             for pattern in meaning["patterns"]})
        # Live, and still unmet: no human example author exists.  That is what
        # 3D-2 continues to wait on, and product approval created no author.
        self.assertEqual({}, live_context.get("authorRegistry", {}) or {})
        self.assertNotIn("grammar-choose", read(EDITORIAL_CORPUS))
        # The runtime this phase found absent is now the I1 release artifact,
        # and nothing else may occupy that path.
        self.assertEqual("complete", i1_bundle().state)


if __name__ == "__main__":
    unittest.main()
