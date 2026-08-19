"""Priority 7 Phase 3C - cross-links and the vocabulary-card pointer.

Phase 3B proved the reference surface in isolation.  Phase 3C connects it to
content the learner already has, in both directions, and adds one derived
pointer to the vocabulary card back.  Three new things therefore need proving
here, at the file level, alongside everything Phase 3B already asserts and which
re-runs unchanged against the edited shell:

  1. the case cross-links are *links*.  No pattern content, no chip row, no verb
     list and no generated block entered ``data-grammar.js`` or the lesson
     renderers, and the seven case-topic ids live in one static map in the pure
     helper rather than being scattered through the shell;
  2. the card pointer is *derived*.  No card data file changed, no card authors a
     backlink, the closed card schema was not reopened, and nothing in the
     derivation path reads an editorial file;
  3. the synthetic card objects used to exercise it are *test-only*.  They exist
     in one JXA suite, they name no real vocabulary card, and no invented support
     relationship was attached to a shipping card.

The behavioural proof - the two gates, contrast-only, the eight synthetic
outcomes, focus, and the rendered DOM - lives in
``tests/test_priority7_patterns_ui.js``, which executes the shipping code.  This
module is the file- and corpus-level half.

Run:  python3 -m unittest tests.test_priority7_phase3c
"""

import json
import re
import unittest
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
EDITORIAL_CORPUS = ROOT / "editorial" / "verb-pattern-candidates.json"
CARD_DATA = ("data-a1.js", "data-a2.js", "data-b1.js")
UI_SUITE = ROOT / "tests" / "test_priority7_patterns_ui.js"

# The seven dedicated case topics.  Grammar owns case teaching; this phase adds
# one continuation to each and copies nothing into any of them.
CASE_TOPIC_IDS = tuple(
    f"grammar-cases-{name}" for name in (
        "nominative", "genitive", "dative", "accusative", "instrumental",
        "locative", "vocative"))

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


class CaseCrossLinkTests(unittest.TestCase):
    """One link each way, and no content moved with it."""

    def test_the_case_topic_map_lives_once_in_the_pure_helper(self):
        loader = read(LOADER)
        index = read(INDEX)
        for topic_id in CASE_TOPIC_IDS:
            with self.subTest(topic=topic_id):
                self.assertEqual(1, loader.count(topic_id))
                self.assertNotIn(
                    topic_id, index,
                    "A case-topic id hard-coded into the shell is a second "
                    "source of truth for which lesson owns which case.")

    def test_no_pattern_content_was_copied_into_the_grammar_data(self):
        grammar = read(ROOT / "data-grammar.js")
        for marker in (
            "vp-", "verb-patterns", "Verbs that take the",
            "Verb patterns with the", "Learn the Genitive",
            "patternLine", "contentRef", "PP_VERB_PATTERNS",
        ):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, grammar)

    def test_the_continuation_wording_claims_no_government(self):
        """A case complement is not always a governed object.

        A Nominative subject and a constructional frame are neither, and what
        the link opens is a filtered view of PATTERNS, not a list of verbs that
        govern the case.  The overstated wording must be gone everywhere,
        including from comments, so a later grep cannot resurrect it.
        """
        for name in ("pp-verb-patterns.js", "index.html", "data-grammar.js"):
            with self.subTest(file=name):
                self.assertNotIn("Verbs that take the", read(ROOT / name))
        loader = read(LOADER)
        # Once for the visible label, once for the accessible name it wraps.
        self.assertEqual(2, loader.count('"Verb patterns with the "'))
        # The reverse label is unchanged: a lesson does take a name.
        self.assertEqual(2, loader.count('"Learn the "'))

    def test_a_case_that_cannot_occur_offers_no_continuation(self):
        """Vocative can be neither a direct nor a prepositional complement.

        No pattern the runtime contract admits can carry it, so there is no
        filtered view for a Vocative deep link to open.  The exclusion is
        DERIVED from the central case metadata rather than hard-coded, so a
        future schema that admitted a genuine Vocative complement would answer
        differently with no edit here - and the Vocative lesson, the case table
        and the case order are all left intact.
        """
        loader = read(LOADER)
        self.assertIn(
            "if (!meta.direct && !meta.prepositional) return null;", loader)
        self.assertNotIn('found === "vocative"', loader)
        self.assertNotIn('caseId !== "vocative"', loader)
        # The lesson, the metadata and the reverse map all survive.
        self.assertIn('vocative: { pl: "Wołacz", en: "Vocative"', loader)
        self.assertIn('vocative: "grammar-cases-vocative"', loader)
        self.assertIn('"locative", "vocative"', loader)
        self.assertIn(
            'id:"grammar-cases-vocative"', read(ROOT / "data-grammar.js"))

    def test_the_authored_lesson_arrays_were_not_extended(self):
        """The continuation is rendered around the lesson, never into it."""
        index = read(INDEX)
        for forbidden in ("teach.push", "teach.concat", "drills.push"):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, index)

    def test_the_reverse_link_names_a_lesson_and_never_reproduces_one(self):
        loader = read(LOADER)
        # The back-link carries a label and a topic id.  It must not carry any
        # of the case teaching itself.
        for forbidden in ("endTable", "declension", "Answers kto?", "rule-list",
                          "end-table"):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, loader)

    def test_both_directions_are_pure_lookups_with_no_runtime_dependency(self):
        """A case lesson can link out before any document is ever accepted."""
        loader = read(LOADER)
        block = re.search(
            r"function caseFilterFor\(topicId\) \{(.*?)\n  \}", loader, re.S)
        self.assertIsNotNone(block)
        for forbidden in ("STATE", "available", "fetch", "lemmas"):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, block.group(1))


class CardPointerDerivationTests(unittest.TestCase):
    """The pointer is derived at runtime; no card data participates."""

    def test_the_closed_card_schema_was_not_reopened(self):
        """No field was added to carry the pointer, and none was needed.

        `pattern` and `relationType` are PRE-EXISTING vocabulary-card fields
        with their own long-standing meaning; they are not Priority 7 and are
        not read by this feature.  What matters is that the closed set is the
        same size it was and gained no reference-shaped member.
        """
        import validate_content

        self.assertEqual(25, len(validate_content.CARD_FIELDS))
        for forbidden in ("patternRef", "patternId", "contentRef", "contentRefs",
                          "verbPattern", "verbPatternId", "vpId", "lemmaRef"):
            with self.subTest(field=forbidden):
                self.assertNotIn(forbidden, validate_content.CARD_FIELDS)

    def test_no_card_authors_a_backlink(self):
        for name in CARD_DATA:
            source = read(ROOT / name)
            for marker in ("vp-", "contentRef", "patternLine", "verb-patterns"):
                with self.subTest(file=name, marker=marker):
                    self.assertNotIn(marker, source)

    def test_only_card_plus_support_is_eligible(self):
        """The one eligible pair is tested where the index is built."""
        loader = read(LOADER)
        self.assertEqual(
            1, loader.count('ref.kind !== "card" || ref.purpose !== "support"'))
        # `contrast` is invisible to the feature: it is never named as a branch,
        # in either direction, so it can neither add nor remove a claim.
        self.assertNotIn('purpose === "contrast"', loader)
        self.assertNotIn('purpose !== "contrast"', loader)

    def test_the_derivation_reads_no_editorial_file(self):
        """Neither the pointer nor either cross-link can reach editorial data.

        The loader NAMES several private editorial keys, because its rejection
        list has to; naming a key in order to refuse it is not reading it, and
        ``tests/test_priority7_phase3b.py`` asserts that no access form of any
        of them appears.  What is asserted here is narrower and complementary:
        no editorial file, path or corpus is referenced at all.
        """
        for source, name in ((read(LOADER), "pp-verb-patterns.js"),
                             (read(INDEX), "index.html")):
            for marker in ("editorial/", "verb-pattern-candidates",
                           "priority-7-authoring-context", "reviewEvents:",
                           "readFileSync", "require(", "XMLHttpRequest"):
                with self.subTest(source=name, marker=marker):
                    self.assertNotIn(marker, source)

    def test_a_cross_lemma_ambiguity_can_never_select_a_lemma(self):
        """Two eligible claims owned by different verbs establish no verb.

        The unsafe shape is a doorway that reaches for ``claims[0]``: the
        runtime order of two references carries no meaning, so a destination
        derived from it would be a claim invented by the sort.  The loader must
        count DISTINCT owners and, when there is more than one, select nothing.
        """
        loader = read(LOADER)
        self.assertIn(
            'if (distinct > 1) return { state: "doorway", scope: "index", '
            'lemmaKey: null };', loader)
        # No outcome may be built from a positional claim any more.
        self.assertNotIn('state: "doorway", lemmaKey: claims[0].lemmaKey', loader)
        # ... and the same-lemma doorway keeps naming its verb.
        self.assertIn(
            'return { state: "doorway", scope: "lemma", '
            'lemmaKey: claims[0].lemmaKey };', loader)
        self.assertEqual(3, loader.count('scope: "lemma"'))
        self.assertEqual(1, loader.count('scope: "index"'))

    def test_the_two_doorways_promise_different_things(self):
        loader = read(LOADER)
        index = read(INDEX)
        self.assertIn('CARD_DOORWAY_LABEL = "See how this verb is used"', loader)
        self.assertIn('CARD_INDEX_DOORWAY_LABEL = "See verb patterns"', loader)
        # The renderer quotes them; it never authors a third.
        self.assertNotIn("See how this verb is used", index)
        self.assertNotIn('"See verb patterns"', index)
        # The destination is carried by the claim, not re-derived at the click.
        self.assertIn("function ppOpenCardPattern(claim, invoker){", index)
        self.assertIn("ppOpenCardPattern(claim, link)", index)

    def test_the_card_surface_reads_exactly_one_field_off_a_card(self):
        index = read(INDEX)
        claim = re.search(
            r"function ppCardPatternClaim\(card\)\{(.*?)\n\}", index, re.S)
        self.assertIsNotNone(claim)
        body = claim.group(1)
        self.assertEqual(body.count("card."), body.count("card.id"))
        # No text-matching, no normalisation, no topic membership: a card whose
        # visible word looks like a lemma is not a claim about that lemma.
        for forbidden in ("card.pl", "card.en", "card.hint", "normalize",
                          "toLowerCase", "PP_ANSWER"):
            with self.subTest(token=forbidden):
                self.assertNotIn(forbidden, body)


class SyntheticCardIsolationTests(unittest.TestCase):
    """The synthetic cards used to test the pointer stay in the test suite."""

    SYNTHETIC_MARKERS = ("p7-fixture-card", "SYNTHETIC-NONRELEASE")

    def test_synthetic_card_objects_exist_only_in_the_test_suite(self):
        outputs, _, _ = build_pages.build_outputs(str(ROOT))
        public_text = "\n".join([
            read(INDEX), read(LOADER), read(ROOT / "sw.js"),
            read(ROOT / "sitemap.xml"),
            *(read(ROOT / name) for name in CARD_DATA),
            *outputs.values(),
        ])
        for marker in self.SYNTHETIC_MARKERS:
            with self.subTest(marker=marker):
                self.assertNotIn(marker, public_text)

    def test_no_real_card_id_was_given_an_invented_support_relationship(self):
        """The fixture references no card at all, real or invented."""
        fixture = json.loads(
            read(ROOT / "tests" / "fixtures" / "priority7" / "runtime-fixture.json"))
        refs = []
        for lemma in fixture["runtimeProjection"]["lemmas"]:
            for meaning in lemma["meanings"]:
                for pattern in meaning["patterns"]:
                    refs.extend(pattern.get("contentRefs", []))
        self.assertEqual([], refs)

    def test_the_suite_uses_no_real_vocabulary_card_id_as_a_claim(self):
        """Real card ids appear in the suite only as things that get NOTHING."""
        suite = read(UI_SUITE)
        real_ids = set()
        for name in CARD_DATA:
            real_ids.update(re.findall(r'id:"((?:a1|a2|b1)-[a-z0-9-]+)"', read(ROOT / name)))
        self.assertTrue(real_ids, "card ids should be discoverable")
        for card_id in sorted(real_ids):
            if card_id not in suite:
                continue
            for line in suite.splitlines():
                if card_id not in line:
                    continue
                with self.subTest(card=card_id, line=line.strip()[:70]):
                    self.assertNotIn("supportRef(", line)
                    self.assertNotIn("purpose: 'support'", line)


class ReleaseBoundaryTests(unittest.TestCase):
    """Nothing this phase touched moved the release boundary."""

    def test_no_public_runtime_projection_exists(self):
        # Superseded by Phase 4F-I1: the only runtime document that may exist
        # is exactly the I1 release artifact, pinned by digest.
        self.assertEqual("complete", i1_bundle().state)

    def test_the_shell_still_makes_no_pattern_request(self):
        index = pre_i1("index.html")
        self.assertEqual(2, index.count("fetch("))
        self.assertNotIn("verb-patterns.json", index)
        self.assertNotIn("content/", index)

    def test_no_real_pattern_carries_eligibility_whatever_its_review_state(self):
        """Phase 4F-A moved review states; eligibility needs ``approved``.

        Reference verification is tier 1 of three and authorises nothing
        learner-facing on its own, so the eligibility and audio counts that
        gate this phase's release boundary must still both be zero.

        Phase 4F-E1 later added tier 2 and Phase 4F-F2 added tier 3.  The
        historical state claim is made over the corpus with that approved
        governance work reverted.  The eligibility and audio counts stay on
        the LIVE corpus, which is the whole point of this test's name: no
        tier above 1 may authorise anything learner-facing on its own, and
        the human product approval Phase 4F-F2 recorded is an inclusion
        decision that grants no activity and no audio by itself.  The former
        live prohibition on ``approved`` was a statement about which tiers
        had run, not about learner exposure, and Phase 4F-F2 legitimately
        superseded it; the zero counts below are what this test guards.
        """
        live = json.loads(read(EDITORIAL_CORPUS))
        corpus = E1.without_phase_4fe1_editorial_review(
            F2.without_phase_4ff2_product_approval(
                H2.without_phase_4fh2_content_completion(
                    H21.without_phase_4fh21_product_reapproval(live))))
        patterns = [
            pattern
            for lemma in corpus["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        live_patterns = [
            pattern
            for lemma in live["lemmas"]
            for meaning in lemma["meanings"]
            for pattern in meaning["patterns"]
        ]
        self.assertEqual(45, len(patterns))
        self.assertEqual(45, len(live_patterns))
        self.assertEqual({"reference-verified"},
                         {p["reviewState"] for p in patterns})
        self.assertEqual(
            {"reference-verification"},
            {event["kind"] for p in patterns
             for event in p.get("reviewEvents", [])})
        self.assertEqual(
            0,
            sum(len(p.get("activityEligibility", [])) for p in live_patterns))
        self.assertEqual(
            0,
            sum(1 for p in live_patterns for example in p.get("examples", [])
                if example.get("audioEligible")))

    def test_version_and_cache_markers_are_unmoved(self):
        index = pre_i1("index.html")
        worker = pre_i1("sw.js")
        self.assertIn('const APP_VERSION = "8.10";', index)
        self.assertIn("popolsku-v65", worker)
        self.assertIn("popolsku-audio", worker)
        self.assertNotIn("verb-patterns", worker)
        self.assertNotIn("patternDataRevision", index)

    def test_no_activity_progress_or_analytics_arrived_with_the_cross_links(self):
        """No scoring, progress, mastery or measurement rides on the links.

        AMENDED by Priority 7 Phase 3D-1, and split rather than dropped.  The
        original assertion swept one list over both files under the heading
        "Phase 3D has not started".  Phase 3D-1 has now deliberately started, as
        a mechanics prototype, so the half of the sweep that was a PHASE BOUNDARY
        is applied where it is still true - the reference surface itself, which
        gained no round, no scoring and no activity vocabulary - while the half
        that is a permanent SAFETY property is applied to both files, unchanged.
        Nothing was weakened: the second list below is the original one minus the
        two activity words the mechanics adapter must now be able to say in order
        to refuse everything else, and the positive assertions that follow pin
        exactly what it is allowed to say them about.
        """
        index = read(INDEX)
        loader = read(LOADER)
        # The Priority 7 code paths only: `analytics` occurs elsewhere in the
        # shell as privacy COPY stating that the app has none, which is the
        # opposite of a regression.
        block = index[index.index("const P = { li:0, ti:0, topicRef:null"):
                      index.index("/* ---------------- grammar (teach -> drill)")]
        # Permanent, and true of both files: nothing here scores a learner,
        # remembers a learner, or measures a learner.
        for marker in ("pStartPractice", "patternMastery", "patternProgress",
                       "gtag", "analytics", "sendBeacon", "localStorage",
                       "sessionStorage", "indexedDB", "rRecord", "grammar-build"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, block)
                self.assertNotIn(marker, loader.replace('"grammar-build"', ""))
        # The reference surface stays a reference surface: the round the
        # mechanics prototype starts is the existing Grammar one, and none of its
        # vocabulary was copied into the passive block.
        for marker in ("grammar-choose", "score", "queue", "requeue", "results["):
            with self.subTest(surface_marker=marker):
                self.assertNotIn(marker, block)
        # What the adapter IS allowed to say, and the shape of saying it: one
        # named activity family, matched positively so everything else fails
        # closed, and no eligibility grant derived from it.
        self.assertIn('var CHOOSE_ACTIVITY = "grammar-choose";', loader)
        self.assertIn("if (item.activityType !== CHOOSE_ACTIVITY) return null;", loader)
        self.assertEqual(2, loader.count('"grammar-choose"'))
        for forbidden in ("activityEligibility.push", "eligibility =",
                          "markEligible", "allowActivity"):
            with self.subTest(grant=forbidden):
                self.assertNotIn(forbidden, loader)


if __name__ == "__main__":
    unittest.main()
