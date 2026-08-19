"""Priority 7 Phase 4F-H2 — authorized learner-content completion.

The product owner authorized a correction plan on 2026-08-18.  Authorizing a
plan is not approving its output, so this phase deliberately stops one tier
short of release: it completes the content, re-enters the editorial chain, and
leaves the corrected rows at ``editorial-reviewed`` for the owner to look at.

This suite treats the delivered candidate as read-only and proves, against the
immutable baseline ``4141872721d097e53c40f05e83b3ea730c38eff0``:

1.  **The scope is the audited scope.**  Recomputed from the baseline, not
    from the candidate: 55 Polish illustrations sit in 54 learner-facing
    English prose fields on 42 patterns; 16 patterns have no example; exactly
    3 patterns have no translation defect; exactly 2 of those change by
    example only; exactly 1 is untouched by this phase.
2.  **Every illustration got its gloss, and nothing else moved.**  Deleting
    the 55 inserted glosses reproduces the baseline prose byte for byte, so no
    field was rewritten for style, and grammatical labels such as ``kogo?
    czego?`` and formulas such as ``za + Accusative`` were left alone.
3.  **The example corpus is complete and honestly sourced.**  45 examples on
    45 patterns, exactly one each; 2 repository-reuse rows byte-identical to
    the repository fields they cite and resolving through the repository
    index; 14 editorial-generated rows naming ``priority7-example-generation``;
    every ID recomputing through ``allocate_example_id``; the pre-existing 29
    byte-identical; no ``origin.kind=original`` and an empty ``authorRegistry``.
4.  **Governance says only what happened.**  42 ``correction`` events on
    exactly the 42 patterns whose existing prose changed and nowhere else; one
    ``editorial-review`` change request and one fresh ``editorial-review``
    acceptance on each of the 44 changed patterns, each acceptance pinned to
    its recomputed tier-2 digest and independently corroborated; the 47
    reference acceptances and the 45 product approvals preserved byte for
    byte; **no** new reference verification and **no** new product approval.
5.  **The derived state is 44 + 1.**  44 patterns at ``editorial-reviewed``,
    ``vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939``
    still ``approved`` with all three of its digests intact, and no changed
    pattern deriving ``approved``.
6.  **Digests moved exactly where content moved.**  Tier 1 on 0 of 45; tier 2
    and tier 3 on the same 44.
7.  **Nothing shipped and nothing was enabled.**  Every shipping file
    byte-identical, ``content/verb-patterns.json`` absent, ``APP_VERSION``
    unchanged, ``activityEligibility`` empty on all 45, no ``audioEligible``
    true, no freeze and no runtime projection.
8.  **The boundary has teeth.**  A wording mutation, a wrong gloss, a missing
    or extra example, an edited existing example, forged provenance, a stale
    or repinned tier-2 digest, a missing correction, a correction on an
    unauthorized pattern, a new reference verification, a new product approval
    and a premature release action are each rejected -- by the validator, by
    the derived state, or by surviving the Phase 4F-H2 normaliser and still
    breaking the historical guard.

Every mutation below is applied to an in-memory copy.  Nothing here writes to
the corpus, the context, the tooling or any shipping file.

**Future safety.**  This suite describes the immutable H2 transition.  A later
phase may product-approve the corrected content, freeze it, project a runtime
and add its own reports and tests without any assertion here failing merely
because those artifacts exist.  The boundary claims below are stated over the
files Phase 4F-H2 itself owned, at the revision it owned them, and never as a
ban on future paths or a comparison against a moving ``HEAD``.

Run:  python3 -m unittest tests.test_priority7_phase4fh2
"""

from __future__ import annotations

import collections
import copy
import csv
import functools
import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path

import os.path as _h2_os_path
import sys as _h2_sys

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
if str(ROOT) not in _h2_sys.path:
    _h2_sys.path.insert(0, str(ROOT))
_H2_DIR = _h2_os_path.dirname(_h2_os_path.abspath(__file__))
if _H2_DIR not in _h2_sys.path:
    _h2_sys.path.insert(0, _H2_DIR)

import priority7_tooling as T  # noqa: E402
from priority7_tooling import ValidationContext, validate_editorial  # noqa: E402

import priority7_phase4fh2_normalizer as H2  # noqa: E402
import priority7_phase4fh21_normalizer as H21  # noqa: E402
import priority7_phase4fh3_normalizer as H3  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
MATRIX_PATH = "reports/priority-7-phase-4fh2-content-matrix.csv"
SUMMARY_PATH = "reports/priority-7-phase-4fh2-content-completion-summary.md"
NORMALISER_PATH = "tests/priority7_phase4fh2_normalizer.py"
PUBLIC_RUNTIME_PATH = "content/verb-patterns.json"

#: Phase 4F-H2 arrived on top of this commit and states every immutability
#: claim against it, never against a moving ``HEAD``.
BASELINE_COMMIT = "4141872721d097e53c40f05e83b3ea730c38eff0"
BASELINE_TREE = "1e34a1b0a86aaca5d6ab3caa2e936d522756c224"

H2_DATE = "2026-08-18"
OWNER = "product-owner-001"
EDITORIAL_ACTOR = "priority7-editorial-review"
CORROBORATOR = "priority7-editorial-corroboration"
GENERATOR = "priority7-example-generation"
REFERENCE_ACTOR = "priority7-reference-analysis"
NATIVE_REVIEWER = "native-reviewer-001"

PATTERN_COUNT = 45
CHANGED_COUNT = 44
TRANSLATION_PATTERN_COUNT = 42
TRANSLATION_FIELD_COUNT = 54
ILLUSTRATION_COUNT = 55
NEW_EXAMPLE_COUNT = 16
BASELINE_EXAMPLE_COUNT = 29
FINAL_EXAMPLE_COUNT = 45
REPOSITORY_REUSE_TOTAL = 20
EDITORIAL_GENERATED_TOTAL = 25
REFERENCE_ACCEPTANCES = 47
PRODUCT_APPROVALS = 45
BASELINE_EDITORIAL_ACCEPTANCES = 45

UNTOUCHED = "vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939"
EXAMPLE_ONLY = frozenset({
    "vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98",
    "vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc",
})

#: The grammatical labels and formulas the locked plan says are notation, not
#: illustrations.  None of them may have acquired a gloss.
GRAMMAR_LABELS = (
    "kogo? czego?", "komu? czemu?", "kim? czym?", "na kogo? na co?", "czego?",
)
CASE_FORMULA_RE = re.compile(
    r"\b(?:na|o|od|w|za|z) \+ (?:Genitive|Dative|Accusative|Instrumental|Locative)\b")

PROTECTED_SHIPPING_FILES = (
    "index.html", "sw.js", "manifest.json", "pp-verb-patterns.js",
    "pp-usage.js", "pp-answer.js", "pp-distractor.js", "pp-migrate.js",
    "sitemap.xml", "audio-manifest.json", "data-a1.js", "data-a2.js",
    "data-b1.js", "data-grammar.js", "data-podcasts.js", "data-scenarios.js",
    "data-verbs.js", "validate_content.py", "build_pages.py", "verify_audio.py",
    "pp_audio_rule.py", "priority7_tooling.py", "generate_audio.py",
    "robots.txt", "CNAME",
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def git(*arguments):
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True,
                          text=True, check=False)


def git_blob(relative, revision=BASELINE_COMMIT):
    result = git("show", f"{revision}:{relative}")
    if result.returncode != 0:
        raise AssertionError(f"missing at {revision}: {relative}")
    return result.stdout


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def is_only_the_h3_ui_wording(path):
    """True for ``index.html`` when its only change is the Phase 4F-H3 layer.

    Phase 4F-H3 is the UI wording phase, and the first phase since ``f339efb``
    entitled to change a shipping file at all.  A path qualifies only when
    removing H3's six pinned strings reproduces this phase's baseline bytes
    exactly, so any other shell edit -- a version or cache bump, a loader
    activation, a change to the recognition-only guards -- any other path, and
    any partly applied layer are still reported exactly as before.
    """
    if not H3.is_phase_4fh3_path(path):
        return False
    baseline = git("show", f"{BASELINE_COMMIT}:{path}")
    if baseline.returncode != 0:
        return False
    # LAYERED by Priority 7 Phase 4F-I1: the shell now carries the I1 release
    # layer on top of the H3 wording layer, so the H3 classification is made
    # over the shell with the I1 layer removed.  Both layers are pinned and
    # all-or-nothing, so an edit outside either pinned set is still reported.
    return H3.is_exactly_the_h3_ui_wording(path, baseline.stdout, pre_i1(path))


def live_corpus():
    """The corpus exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CORPUS_PATH))


def live_context_document():
    """The context exactly as it stands on disk, with no normalisation."""
    return json.loads(read(CONTEXT_PATH))


def h2_corpus():
    """The corpus as Phase 4F-H2 left it, with later phases normalised away.

    Phase 4F-H2.1 legitimately superseded this phase's ``editorial-reviewed``
    state on all 44 changed rows by recording the product owner's decision on
    the corrected content.  Its phase-owned normaliser is closed over exactly
    those 44 appended acceptances and derives nothing from the live rows, so
    removing that layer here restores the document this suite's claims were
    written about without absorbing anything Phase 4F-H2.1 did not do.
    """
    return H21.without_phase_4fh21_product_reapproval(live_corpus())


def h2_context_document():
    """The context as Phase 4F-H2 left it, with later phases normalised away."""
    return H21.without_phase_4fh21_context(live_context_document())


def baseline_corpus():
    return json.loads(git_blob(CORPUS_PATH))


def baseline_context_document():
    return json.loads(git_blob(CONTEXT_PATH))


@functools.lru_cache(maxsize=1)
def repository_index():
    return T.repository_index_from_root(str(ROOT))


def build_context(document=None, *, resolve_repository=True):
    document = h2_context_document() if document is None else document
    return ValidationContext(
        source_registry=document["sourceRegistry"],
        reviewer_registry=document["reviewerRegistry"],
        author_registry=document["authorRegistry"],
        allocation_registry=document["allocationRegistry"],
        repository_index=repository_index() if resolve_repository else None,
        editorial_actor_registry=document.get("editorialActorRegistry", {}),
        today=H2_DATE,
    )


def iter_patterns(corpus):
    for lemma in corpus["lemmas"]:
        for meaning in lemma["meanings"]:
            for pattern in meaning["patterns"]:
                yield lemma, meaning, pattern


def rows_by_id(corpus):
    return {pattern["id"]: (lemma, meaning, pattern)
            for lemma, meaning, pattern in iter_patterns(corpus)}


def prose_fields(pattern):
    """Every learner-facing English prose field, keyed by its pinned path."""
    fields = {"learnerExplanationEn": pattern["learnerExplanationEn"]}
    for index, note in enumerate(pattern.get("errorNotes", [])):
        fields[f"errorNotes[{index}].guidanceEn"] = note["guidanceEn"]
    return fields


GLOSS_RE = re.compile(r" \([^()]*\)")


def strip_h2_glosses(text, glosses):
    """Remove exactly the pinned ``(gloss)`` insertions from ``text``."""
    for gloss in glosses:
        marker = f" ({gloss})"
        if marker not in text:
            raise AssertionError(f"gloss {gloss!r} absent from {text!r}")
        text = text.replace(marker, "", 1)
    return text


def pinned_glosses(pattern_id, path):
    """The glosses H2 inserted into one field, in insertion order."""
    before, after = H2.H2_FIELD_REWRITES[pattern_id][path]
    found, cursor = [], before
    for match in GLOSS_RE.finditer(after):
        found.append(match.group(0)[2:-1])
    # Only the insertions matter: anything already parenthesised in the
    # baseline text is not an H2 gloss.
    baseline_parens = [m.group(0)[2:-1] for m in GLOSS_RE.finditer(cursor)]
    for existing in baseline_parens:
        if existing in found:
            found.remove(existing)
    return found


def stage_digests(lemma, meaning, pattern):
    return {
        "tier1": T.review_scope_digest("external-verification", lemma, meaning, pattern),
        "tier2": T.review_scope_digest("native-linguistic", lemma, meaning, pattern),
        "tier3": T.review_scope_digest("product-approval", lemma, meaning, pattern),
    }


def events_of(corpus, kind=None, decision=None):
    return [event for _l, _m, pattern in iter_patterns(corpus)
            for event in pattern["reviewEvents"]
            if (kind is None or event["kind"] == kind)
            and (decision is None or event["decision"] == decision)]


def codes(issues):
    return sorted({issue.code for issue in issues})


class Phase4FH2TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = h2_corpus()
        cls.context_document = h2_context_document()
        cls.on_disk = live_corpus()
        cls.on_disk_context = live_context_document()
        cls.baseline = baseline_corpus()
        cls.baseline_context = baseline_context_document()
        cls.rows = rows_by_id(cls.corpus)
        cls.baseline_rows = rows_by_id(cls.baseline)

    def mutated(self):
        return copy.deepcopy(type(self).corpus)

    def mutated_context(self):
        return copy.deepcopy(type(self).context_document)

    def a_translation_pattern(self, corpus):
        pattern_id = sorted(H2.H2_TRANSLATION_PATTERN_IDS)[0]
        return rows_by_id(corpus)[pattern_id][2]

    def an_example_pattern(self, corpus):
        pattern_id = sorted(H2.H2_EXAMPLE_PATTERN_IDS)[0]
        return rows_by_id(corpus)[pattern_id][2]


# ---------------------------------------------------------------------------
# 1.  The scope is the audited scope, recomputed from the baseline
# ---------------------------------------------------------------------------

class ScopeReconfirmation(Phase4FH2TestCase):
    """Everything here is derived from the BASELINE, never from the candidate."""

    def test_the_baseline_holds_forty_five_patterns_and_twenty_nine_examples(self):
        self.assertEqual(PATTERN_COUNT, len(self.baseline_rows))
        self.assertEqual(
            BASELINE_EXAMPLE_COUNT,
            sum(len(pattern.get("examples", []))
                for _l, _m, pattern in iter_patterns(self.baseline)))

    def test_exactly_sixteen_baseline_patterns_had_no_example(self):
        missing = {pattern_id for pattern_id, (_l, _m, pattern)
                   in self.baseline_rows.items() if not pattern.get("examples")}
        self.assertEqual(NEW_EXAMPLE_COUNT, len(missing))
        self.assertEqual(set(H2.H2_EXAMPLE_PATTERN_IDS), missing)

    def test_the_pinned_rewrites_match_the_baseline_prose_exactly(self):
        """54 fields, and each ``before`` is what the baseline really said."""
        total = 0
        for pattern_id, rewrites in H2.H2_FIELD_REWRITES.items():
            fields = prose_fields(self.baseline_rows[pattern_id][2])
            for path, (before, after) in rewrites.items():
                total += 1
                with self.subTest(pattern_id=pattern_id, path=path):
                    self.assertIn(path, fields)
                    self.assertEqual(before, fields[path])
                    self.assertNotEqual(before, after)
        self.assertEqual(TRANSLATION_FIELD_COUNT, total)
        self.assertEqual(TRANSLATION_PATTERN_COUNT, len(H2.H2_FIELD_REWRITES))

    def test_the_field_split_is_thirty_two_explanations_and_twenty_two_notes(self):
        paths = [path for rewrites in H2.H2_FIELD_REWRITES.values()
                 for path in rewrites]
        self.assertEqual(32, sum(1 for path in paths
                                 if path == "learnerExplanationEn"))
        self.assertEqual(22, sum(1 for path in paths
                                 if path != "learnerExplanationEn"))

    def test_the_changed_set_is_forty_four_and_the_untouched_one_is_named(self):
        changed = set(H2.H2_TRANSLATION_PATTERN_IDS) | set(H2.H2_EXAMPLE_PATTERN_IDS)
        self.assertEqual(CHANGED_COUNT, len(changed))
        self.assertEqual(set(H2.H2_EXPECTED_PATTERN_IDS), changed)
        self.assertEqual({UNTOUCHED}, set(self.baseline_rows) - changed)
        self.assertEqual(UNTOUCHED, H2.H2_UNTOUCHED_PATTERN_ID)

    def test_exactly_three_patterns_had_no_translation_defect(self):
        clean = set(self.baseline_rows) - set(H2.H2_TRANSLATION_PATTERN_IDS)
        self.assertEqual(3, len(clean))
        self.assertEqual(EXAMPLE_ONLY | {UNTOUCHED}, clean)

    def test_exactly_two_patterns_change_by_example_alone(self):
        example_only = (set(H2.H2_EXAMPLE_PATTERN_IDS)
                        - set(H2.H2_TRANSLATION_PATTERN_IDS))
        self.assertEqual(EXAMPLE_ONLY, example_only)

    def test_the_two_reuse_sources_resolve_and_are_the_only_reuse(self):
        reuse = {pattern_id: example for pattern_id, example
                 in H2.H2_NEW_EXAMPLES.items()
                 if example["origin"]["kind"] == "repository-reuse"}
        self.assertEqual(2, len(reuse))
        index = repository_index()
        self.assertEqual([], index.issues)
        for pattern_id, example in reuse.items():
            source = example["origin"]["repositorySource"]
            with self.subTest(pattern_id=pattern_id):
                entity = index.get(source["id"])
                self.assertIsNotNone(entity)
                self.assertEqual(source["kind"], entity.kind)
                self.assertEqual(example["pl"], entity.record[source["field"]])
        self.assertEqual(
            {"b1-career-006", "b1-expressing-opinions-004"},
            {example["origin"]["repositorySource"]["id"]
             for example in reuse.values()})


# ---------------------------------------------------------------------------
# 2.  Every illustration got its gloss, and nothing else moved
# ---------------------------------------------------------------------------

class TranslationWork(Phase4FH2TestCase):

    def test_fifty_five_glosses_were_inserted_across_fifty_four_fields(self):
        total = 0
        for pattern_id, rewrites in H2.H2_FIELD_REWRITES.items():
            for path in rewrites:
                inserted = pinned_glosses(pattern_id, path)
                self.assertTrue(inserted, f"{pattern_id} {path}")
                total += len(inserted)
        self.assertEqual(ILLUSTRATION_COUNT, total)

    def test_removing_the_glosses_restores_the_baseline_prose_exactly(self):
        """Proof that no field was rewritten for style."""
        for pattern_id, rewrites in H2.H2_FIELD_REWRITES.items():
            live = prose_fields(self.rows[pattern_id][2])
            base = prose_fields(self.baseline_rows[pattern_id][2])
            for path in rewrites:
                with self.subTest(pattern_id=pattern_id, path=path):
                    self.assertEqual(rewrites[path][1], live[path])
                    self.assertEqual(
                        base[path],
                        strip_h2_glosses(live[path],
                                         pinned_glosses(pattern_id, path)))

    def test_every_gloss_sits_immediately_after_its_polish_illustration(self):
        for row in self.matrix_rows():
            if not row["polishIllustration"]:
                continue
            with self.subTest(reviewId=row["reviewId"],
                              polish=row["polishIllustration"]):
                self.assertIn(
                    f"{row['polishIllustration']} ({row['newEnglishGloss']})",
                    row["afterFieldText"])

    def test_no_prose_field_outside_the_pinned_fifty_four_changed(self):
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            base = prose_fields(self.baseline_rows[pattern_id][2])
            live = prose_fields(pattern)
            self.assertEqual(set(base), set(live), pattern_id)
            rewritten = set(H2.H2_FIELD_REWRITES.get(pattern_id, {}))
            for path, value in live.items():
                if path in rewritten:
                    continue
                with self.subTest(pattern_id=pattern_id, path=path):
                    self.assertEqual(base[path], value)

    def test_grammar_labels_and_case_formulas_were_left_alone(self):
        for pattern_id, (_l, _m, pattern) in self.rows.items():
            for path, value in prose_fields(pattern).items():
                with self.subTest(pattern_id=pattern_id, path=path):
                    for label in GRAMMAR_LABELS:
                        self.assertNotIn(f"{label} (", value)
                    for formula in CASE_FORMULA_RE.finditer(value):
                        tail = value[formula.end():formula.end() + 2]
                        self.assertNotEqual(" (", tail)

    def test_no_learner_field_carries_an_empty_or_doubled_gloss(self):
        for _pattern_id, (_l, _m, pattern) in self.rows.items():
            for path, value in prose_fields(pattern).items():
                with self.subTest(pattern_id=pattern["id"], path=path):
                    self.assertNotIn("()", value)
                    self.assertNotIn("((", value)
                    self.assertNotIn("  ", value)
                    self.assertEqual(value.strip(), value)

    @functools.lru_cache(maxsize=1)
    def matrix_rows(self):
        with (ROOT / MATRIX_PATH).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))


# ---------------------------------------------------------------------------
# 3.  The example corpus is complete and honestly sourced
# ---------------------------------------------------------------------------

class ExampleWork(Phase4FH2TestCase):

    def test_forty_five_patterns_carry_exactly_one_example_each(self):
        counts = collections.Counter(
            len(pattern.get("examples", []))
            for _l, _m, pattern in iter_patterns(self.corpus))
        self.assertEqual({1: PATTERN_COUNT}, dict(counts))
        self.assertEqual(
            FINAL_EXAMPLE_COUNT,
            sum(len(pattern["examples"])
                for _l, _m, pattern in iter_patterns(self.corpus)))

    def test_the_final_origin_split_is_twenty_and_twenty_five(self):
        origins = collections.Counter(
            example["origin"]["kind"]
            for _l, _m, pattern in iter_patterns(self.corpus)
            for example in pattern["examples"])
        self.assertEqual(
            {"repository-reuse": REPOSITORY_REUSE_TOTAL,
             "editorial-generated": EDITORIAL_GENERATED_TOTAL},
            dict(origins))

    def test_no_example_claims_a_human_author(self):
        for _l, _m, pattern in iter_patterns(self.corpus):
            for example in pattern["examples"]:
                with self.subTest(example_id=example["id"]):
                    self.assertNotEqual("original", example["origin"]["kind"])
                    self.assertNotIn("authorRef", example["origin"])
                    self.assertNotIn("authoredAt", example["origin"])
        self.assertEqual({}, self.context_document["authorRegistry"])

    def test_the_twenty_nine_pre_existing_examples_are_byte_identical(self):
        checked = 0
        for pattern_id, (_l, _m, pattern) in self.baseline_rows.items():
            if not pattern.get("examples"):
                continue
            checked += 1
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(pattern["examples"],
                                 self.rows[pattern_id][2]["examples"])
        self.assertEqual(BASELINE_EXAMPLE_COUNT, checked)

    def test_the_sixteen_new_examples_are_exactly_the_pinned_ones(self):
        for pattern_id in H2.H2_EXAMPLE_PATTERN_IDS:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual([H2.H2_NEW_EXAMPLES[pattern_id]],
                                 self.rows[pattern_id][2]["examples"])

    def test_every_new_example_id_recomputes_from_its_durable_key(self):
        for pattern_id, example in H2.H2_NEW_EXAMPLES.items():
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    T.allocate_example_id(pattern_id, example["key"]),
                    example["id"])

    def test_new_example_keys_and_ids_are_unique_across_the_corpus(self):
        examples = [example for _l, _m, pattern in iter_patterns(self.corpus)
                    for example in pattern["examples"]]
        self.assertEqual(FINAL_EXAMPLE_COUNT,
                         len({example["id"] for example in examples}))
        self.assertEqual(FINAL_EXAMPLE_COUNT,
                         len({example["pl"] for example in examples}))
        self.assertEqual(FINAL_EXAMPLE_COUNT,
                         len({example["en"] for example in examples}))

    def test_the_fourteen_generated_examples_name_the_generation_workflow(self):
        generated = [example for example in H2.H2_NEW_EXAMPLES.values()
                     if example["origin"]["kind"] == "editorial-generated"]
        self.assertEqual(14, len(generated))
        for example in generated:
            with self.subTest(example_id=example["id"]):
                self.assertEqual(GENERATOR, example["origin"]["generatorRef"])
                self.assertEqual(H2_DATE, example["origin"]["adoptedAt"])
                self.assertNotIn("repositorySource", example["origin"])

    def test_the_two_reused_examples_are_byte_identical_to_their_sources(self):
        index = repository_index()
        for example in H2.H2_NEW_EXAMPLES.values():
            if example["origin"]["kind"] != "repository-reuse":
                continue
            source = example["origin"]["repositorySource"]
            entity = index.get(source["id"])
            with self.subTest(source=source["id"]):
                self.assertEqual(entity.record[source["field"]], example["pl"])
                self.assertEqual(entity.record["exEn"], example["en"])
                self.assertNotIn("generatorRef", example["origin"])
                self.assertNotIn("adoptedAt", example["origin"])

    def test_the_generation_actor_holds_only_the_generation_role(self):
        record = self.context_document["editorialActorRegistry"][GENERATOR]
        self.assertIs(False, record["human"])
        self.assertEqual(["example-generation"], record["roles"])


# ---------------------------------------------------------------------------
# 4.  Governance says only what happened
# ---------------------------------------------------------------------------

class GovernanceLedger(Phase4FH2TestCase):

    def test_exactly_forty_two_corrections_exist_on_the_authorized_rows(self):
        holders = {pattern["id"] for _l, _m, pattern in iter_patterns(self.corpus)
                   for event in pattern["reviewEvents"]
                   if event["kind"] == "correction"}
        self.assertEqual(set(H2.H2_TRANSLATION_PATTERN_IDS), holders)
        self.assertEqual(TRANSLATION_PATTERN_COUNT,
                         len(events_of(self.corpus, "correction")))

    def test_no_correction_sits_on_an_example_only_or_untouched_row(self):
        for pattern_id in EXAMPLE_ONLY | {UNTOUCHED}:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    [], [event for event
                         in self.rows[pattern_id][2]["reviewEvents"]
                         if event["kind"] == "correction"])

    def test_every_correction_is_the_owner_acting_under_product_authority(self):
        registry = self.context_document["reviewerRegistry"]
        for event in events_of(self.corpus, "correction"):
            with self.subTest(event=event["note"][:40]):
                self.assertEqual(OWNER, event["reviewerRef"])
                self.assertEqual("accept", event["decision"])
                self.assertEqual(H2_DATE, event["reviewedAt"])
                self.assertNotIn("actorRef", event)
                self.assertNotIn("scopeDigest", event)
        self.assertIs(True, registry[OWNER]["human"])
        self.assertEqual(["product-approval"], registry[OWNER]["roles"])

    def test_the_correction_note_does_not_claim_approval_of_the_new_wording(self):
        for event in events_of(self.corpus, "correction"):
            note = event["note"].lower()
            with self.subTest(note=note[:40]):
                self.assertIn("authorized", note)
                self.assertIn("not product-approved", note)
                self.assertNotIn("approved the wording", note)

    def test_each_changed_row_carries_one_change_request_and_one_acceptance(self):
        for pattern_id in H2.H2_EXPECTED_PATTERN_IDS:
            appended = H2.appended_h2_events(pattern_id)
            kinds = collections.Counter(
                (event["kind"], event["decision"]) for event in appended)
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(1, kinds[("editorial-review", "changes-requested")])
                self.assertEqual(1, kinds[("editorial-review", "accept")])
                self.assertEqual(
                    1 if pattern_id in H2.H2_TRANSLATION_PATTERN_IDS else 0,
                    kinds[("correction", "accept")])
                self.assertEqual(
                    appended,
                    self.rows[pattern_id][2]["reviewEvents"][-len(appended):])

    def test_every_new_acceptance_pins_the_recomputed_tier_two_digest(self):
        for pattern_id in H2.H2_EXPECTED_PATTERN_IDS:
            lemma, meaning, pattern = self.rows[pattern_id]
            accept = pattern["reviewEvents"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual("editorial-review", accept["kind"])
                self.assertEqual("accept", accept["decision"])
                self.assertEqual(1, accept["scopeVersion"])
                self.assertEqual(
                    T.review_scope_digest("native-linguistic", lemma, meaning,
                                          pattern),
                    accept["scopeDigest"])

    def test_every_new_acceptance_is_independently_corroborated(self):
        for pattern_id in H2.H2_EXPECTED_PATTERN_IDS:
            accept = self.rows[pattern_id][2]["reviewEvents"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(EDITORIAL_ACTOR, accept["actorRef"])
                self.assertEqual([CORROBORATOR], accept["corroboratingActorRefs"])
                self.assertNotIn("reviewerRef", accept)
        registry = self.context_document["editorialActorRegistry"]
        for reference in (EDITORIAL_ACTOR, CORROBORATOR):
            self.assertIs(False, registry[reference]["human"])
            self.assertEqual(["editorial-review"], registry[reference]["roles"])
        self.assertNotEqual(EDITORIAL_ACTOR, CORROBORATOR)

    def test_no_editorial_event_names_the_reference_actor_or_a_human(self):
        for event in events_of(self.corpus, "editorial-review"):
            with self.subTest(reviewedAt=event["reviewedAt"]):
                self.assertNotIn("reviewerRef", event)
                self.assertNotEqual(REFERENCE_ACTOR, event["actorRef"])
                self.assertNotIn(
                    REFERENCE_ACTOR, event.get("corroboratingActorRefs", []))

    def test_no_event_anywhere_names_the_native_reviewer(self):
        self.assertNotIn(NATIVE_REVIEWER, read(CORPUS_PATH))

    def test_the_forty_seven_reference_acceptances_are_untouched(self):
        for pattern_id, (_l, _m, pattern) in self.baseline_rows.items():
            before = [event for event in pattern["reviewEvents"]
                      if event["kind"] == "reference-verification"]
            after = [event for event in self.rows[pattern_id][2]["reviewEvents"]
                     if event["kind"] == "reference-verification"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after)
        self.assertEqual(REFERENCE_ACCEPTANCES,
                         len(events_of(self.corpus, "reference-verification")))

    def test_the_forty_five_product_approvals_are_untouched_and_unextended(self):
        for pattern_id, (_l, _m, pattern) in self.baseline_rows.items():
            before = [event for event in pattern["reviewEvents"]
                      if event["kind"] == "product-approval"]
            after = [event for event in self.rows[pattern_id][2]["reviewEvents"]
                     if event["kind"] == "product-approval"]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(before, after)
        approvals = events_of(self.corpus, "product-approval")
        self.assertEqual(PRODUCT_APPROVALS, len(approvals))
        self.assertEqual({"2026-08-17"},
                         {event["reviewedAt"] for event in approvals})

    def test_no_event_of_any_kind_is_dated_after_the_authorized_day(self):
        for event in [event for _l, _m, pattern in iter_patterns(self.corpus)
                      for event in pattern["reviewEvents"]]:
            self.assertLessEqual(event["reviewedAt"], H2_DATE)

    def test_the_forty_five_baseline_editorial_acceptances_still_stand(self):
        accepts = events_of(self.corpus, "editorial-review", "accept")
        self.assertEqual(BASELINE_EDITORIAL_ACCEPTANCES + CHANGED_COUNT,
                         len(accepts))
        self.assertEqual(
            BASELINE_EDITORIAL_ACCEPTANCES,
            sum(1 for event in accepts if event["reviewedAt"] == "2026-08-17"))

    def test_no_reopen_event_was_used(self):
        self.assertEqual([], events_of(self.corpus, "reopen"))

    def test_no_registry_gained_or_lost_an_identity(self):
        for key in ("reviewerRegistry", "editorialActorRegistry",
                    "authorRegistry", "sourceRegistry", "allocationRegistry"):
            with self.subTest(registry=key):
                self.assertEqual(self.baseline_context[key],
                                 self.context_document[key])

    def test_the_context_changed_only_by_an_appended_notice_paragraph(self):
        base = self.baseline_context["contextNotice"]
        live = self.context_document["contextNotice"]
        self.assertTrue(live.startswith(base))
        self.assertEqual(base + H2.H2_CONTEXT_NOTICE_SUFFIX, live)
        self.assertEqual(set(self.baseline_context), set(self.context_document))


# ---------------------------------------------------------------------------
# 5.  The derived state is 44 + 1
# ---------------------------------------------------------------------------

class DerivedState(Phase4FH2TestCase):

    def test_the_candidate_validates_under_the_real_private_context(self):
        self.assertEqual([], validate_editorial(self.corpus, build_context()))

    def test_forty_four_are_editorial_reviewed_and_one_is_approved(self):
        states = collections.Counter(
            pattern["reviewState"] for _l, _m, pattern
            in iter_patterns(self.corpus))
        self.assertEqual({"editorial-reviewed": CHANGED_COUNT, "approved": 1},
                         dict(states))
        self.assertEqual("approved", self.rows[UNTOUCHED][2]["reviewState"])

    def test_no_changed_pattern_derives_approved(self):
        for pattern_id in H2.H2_EXPECTED_PATTERN_IDS:
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual("editorial-reviewed",
                                 self.rows[pattern_id][2]["reviewState"])

    def test_the_untouched_pattern_is_byte_identical_to_its_baseline_row(self):
        self.assertEqual(self.baseline_rows[UNTOUCHED][2],
                         self.rows[UNTOUCHED][2])

    def test_lowering_the_state_of_the_untouched_row_is_refused(self):
        corpus = self.mutated()
        rows_by_id(corpus)[UNTOUCHED][2]["reviewState"] = "editorial-reviewed"
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_claiming_approved_on_a_changed_row_is_refused(self):
        corpus = self.mutated()
        pattern_id = sorted(H2.H2_EXPECTED_PATTERN_IDS)[0]
        rows_by_id(corpus)[pattern_id][2]["reviewState"] = "approved"
        self.assertIn("REVIEW_STATE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))


# ---------------------------------------------------------------------------
# 6.  Digests moved exactly where content moved
# ---------------------------------------------------------------------------

class DigestMovement(Phase4FH2TestCase):

    @functools.cached_property
    def movement(self):
        moved = {"tier1": set(), "tier2": set(), "tier3": set()}
        for pattern_id in self.rows:
            before = stage_digests(*self.baseline_rows[pattern_id])
            after = stage_digests(*self.rows[pattern_id])
            for tier in moved:
                if before[tier] != after[tier]:
                    moved[tier].add(pattern_id)
        return moved

    def test_no_tier_one_digest_moved_on_any_of_the_forty_five(self):
        self.assertEqual(set(), self.movement["tier1"])

    def test_tier_two_moved_on_exactly_the_forty_four_changed_patterns(self):
        self.assertEqual(set(H2.H2_EXPECTED_PATTERN_IDS), self.movement["tier2"])

    def test_tier_three_moved_on_exactly_the_same_forty_four(self):
        self.assertEqual(self.movement["tier2"], self.movement["tier3"])

    def test_the_untouched_pattern_keeps_all_three_digests(self):
        self.assertEqual(stage_digests(*self.baseline_rows[UNTOUCHED]),
                         stage_digests(*self.rows[UNTOUCHED]))

    def test_the_stale_product_approvals_no_longer_cover_their_tier_three(self):
        """Preserved, and honestly stale: that is why nothing derives approved."""
        for pattern_id in H2.H2_EXPECTED_PATTERN_IDS:
            _l, _m, pattern = self.rows[pattern_id]
            approval = [event for event in pattern["reviewEvents"]
                        if event["kind"] == "product-approval"][0]
            with self.subTest(pattern_id=pattern_id):
                self.assertNotEqual(stage_digests(*self.rows[pattern_id])["tier3"],
                                    approval["scopeDigest"])

    def test_the_reference_acceptances_still_pin_their_live_tier_one(self):
        for pattern_id, (lemma, meaning, pattern) in self.rows.items():
            accepted = [event for event in pattern["reviewEvents"]
                        if event["kind"] == "reference-verification"][-1]
            with self.subTest(pattern_id=pattern_id):
                self.assertEqual(
                    T.review_scope_digest("external-verification", lemma,
                                          meaning, pattern),
                    accepted["scopeDigest"])


# ---------------------------------------------------------------------------
# 7.  Nothing shipped and nothing was enabled
# ---------------------------------------------------------------------------

class ReleaseAndActivityBoundary(Phase4FH2TestCase):

    def test_activity_eligibility_is_empty_on_all_forty_five(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for _l, _m, pattern in iter_patterns(self.corpus)))

    def test_no_example_is_audio_eligible(self):
        self.assertEqual(
            0, sum(1 for _l, _m, pattern in iter_patterns(self.corpus)
                   for example in pattern["examples"]
                   if example["audioEligible"] is True))

    def test_every_shipping_file_is_byte_identical_to_the_baseline(self):
        """Compared with the Phase 4F-I1 and 4F-H3 layers removed.

        Two phases have been entitled to change a shipping file since this
        baseline: H3, the UI wording phase, and I1, the atomic release.  Both
        layers are pinned and all-or-nothing, so removing them must reproduce
        these bytes exactly and every other shell or worker edit still fails
        here.  I1 is stripped first because it sits on top of H3, and the
        generator-owned outputs it regenerated are admitted only by their own
        pinned delta.
        """
        for name in PROTECTED_SHIPPING_FILES:
            with self.subTest(path=name):
                if i1_is_generated_output(name):
                    self.assertTrue(I1.is_exactly_the_i1_transition(
                        name, git_blob(name), read(name),
                        bundle=i1_bundle()), name)
                    continue
                text = i1_shipping_text(name)
                if H3.is_phase_4fh3_path(name):
                    text = H3.without_phase_4fh3_ui_wording(text)
                self.assertEqual(git_blob(name), text)

    def test_the_public_runtime_artifact_does_not_exist(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_the_app_version_and_shell_cache_did_not_advance(self):
        """The version claim is stated over the LIVE shell, never normalised.

        Only the shell-identity half is taken with the Phase 4F-H3 wording
        layer removed.  ``APP_VERSION`` lies outside every string H3 pinned,
        so it is read from the shipping file exactly as it stands.
        """
        self.assertEqual(git_blob("index.html"),
                         H3.without_phase_4fh3_ui_wording(pre_i1("index.html")))
        # Superseded by Phase 4F-I1, which advanced it as part of the release.
        # Restated over the shell with the pinned I1 layer removed; APP_VERSION
        # is one of the two strings that layer pins, and nothing else moves it.
        self.assertIn('const APP_VERSION = "8.10";', pre_i1("index.html"))

    def test_this_phase_touched_only_editorial_tests_and_reports(self):
        status = git("status", "--porcelain")
        self.assertEqual(0, status.returncode, status.stderr)
        changed = {line[3:].strip().strip('"')
                   for line in status.stdout.splitlines() if line.strip()}
        committed = git("diff", "--name-only", BASELINE_COMMIT, "HEAD")
        if committed.returncode == 0:
            changed |= {line.strip() for line in committed.stdout.splitlines()
                        if line.strip()}
        unexpected = sorted(
            path for path in changed
            if not path.startswith(("tests/", "reports/", "editorial/"))
            and not is_only_the_h3_ui_wording(path)
            and not is_only_the_i1_activation(path))
        self.assertEqual([], unexpected, f"unexpected footprint: {unexpected}")

    def test_the_baseline_is_the_declared_commit_and_tree(self):
        self.assertEqual(BASELINE_TREE,
                         git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}")
                         .stdout.strip())

    def test_no_release_or_push_action_occurred(self):
        self.assertEqual("", git("remote").stdout.strip())


# ---------------------------------------------------------------------------
# 8.  The reports say what the corpus says
# ---------------------------------------------------------------------------

class Reports(Phase4FH2TestCase):

    @classmethod
    def matrix(cls):
        with (ROOT / MATRIX_PATH).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_the_matrix_covers_every_pattern_and_every_illustration(self):
        rows = self.matrix()
        self.assertEqual(PATTERN_COUNT, len({row["patternId"] for row in rows}))
        self.assertEqual(
            ILLUSTRATION_COUNT,
            sum(1 for row in rows if row["polishIllustration"]))
        self.assertEqual(
            NEW_EXAMPLE_COUNT,
            len({row["patternId"] for row in rows if row["newExamplePl"]}))

    def test_every_matrix_row_agrees_with_the_corpus(self):
        for row in self.matrix():
            pattern_id = row["patternId"]
            _l, _m, pattern = self.rows[pattern_id]
            with self.subTest(reviewId=row["reviewId"], path=row["fieldPath"]):
                self.assertEqual(pattern["reviewState"], row["finalState"])
                self.assertEqual("approved", row["priorState"])
                self.assertEqual("no", row["freshProductApprovalCreated"])
                self.assertEqual("no", row["tier1Changed"])
                expected_correction = (
                    "yes" if pattern_id in H2.H2_TRANSLATION_PATTERN_IDS else "no")
                self.assertEqual(expected_correction,
                                 row["correctionEventCreated"])
                expected_moved = (
                    "yes" if pattern_id in H2.H2_EXPECTED_PATTERN_IDS else "no")
                self.assertEqual(expected_moved, row["tier2Changed"])
                self.assertEqual(expected_moved, row["tier3Changed"])
                if row["fieldPath"]:
                    self.assertEqual(
                        row["afterFieldText"],
                        prose_fields(pattern)[row["fieldPath"]])
                    self.assertEqual(
                        row["beforeFieldText"],
                        prose_fields(self.baseline_rows[pattern_id][2])[
                            row["fieldPath"]])
                if row["newExamplePl"]:
                    example = pattern["examples"][0]
                    self.assertEqual(example["pl"], row["newExamplePl"])
                    self.assertEqual(example["en"], row["newExampleEn"])
                    self.assertEqual(example["origin"]["kind"],
                                     row["exampleOrigin"])

    def test_the_matrix_review_ids_match_the_established_numbering(self):
        established = {}
        with (ROOT / "reports/priority-7-phase-4ff2-product-approval-matrix.csv"
              ).open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                established[row["patternId"]] = row["reviewId"]
        for row in self.matrix():
            with self.subTest(patternId=row["patternId"]):
                self.assertEqual(established[row["patternId"]], row["reviewId"])

    def test_the_summary_states_the_governance_outcome_truthfully(self):
        summary = " ".join(read(SUMMARY_PATH).lower().replace("*", "").split())
        for claim in (
                "44 patterns are editorial-reviewed",
                "no product-approval event was created",
                "not product-approved",
                "no reference-verification event was created",
                "authoring pass",
                "final editorial pass",
                "not human review",
        ):
            with self.subTest(claim=claim):
                self.assertIn(claim, summary)

    def test_the_summary_does_not_claim_human_or_native_review(self):
        summary = " ".join(read(SUMMARY_PATH).lower().replace("*", "").split())
        for forbidden in (
                "native-speaker reviewed", "a native speaker checked",
                "the product owner approved the new wording",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, summary)


# ---------------------------------------------------------------------------
# 9.  Negative controls — the boundary has teeth
# ---------------------------------------------------------------------------

class NegativeControls(Phase4FH2TestCase):

    def assert_survives_normalisation(self, corpus, label):
        normalised = H2.without_phase_4fh2_content_completion(
            H21.without_phase_4fh21_product_reapproval(corpus))
        self.assertNotEqual(
            self.baseline, normalised,
            f"the normaliser absorbed an unauthorized change: {label}")
        return normalised

    def test_a_reworded_learner_explanation_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["learnerExplanationEn"] += " Extra unauthorised sentence."
        self.assert_survives_normalisation(corpus, "reworded explanation")

    def test_a_wrong_gloss_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["learnerExplanationEn"] = pattern[
            "learnerExplanationEn"].replace("(", "(WRONG ", 1)
        self.assert_survives_normalisation(corpus, "wrong gloss")

    def test_an_edited_pre_existing_example_is_not_absorbed(self):
        corpus = self.mutated()
        pattern_id = "vp-p-szukac-seek-genitive-target-71dc6eff512c"
        rows_by_id(corpus)[pattern_id][2]["examples"][0]["pl"] = "Szukam pracy."
        normalised = self.assert_survives_normalisation(corpus, "edited example")
        self.assertEqual(
            "Szukam pracy.",
            rows_by_id(normalised)[pattern_id][2]["examples"][0]["pl"])

    def test_an_edited_new_example_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.an_example_pattern(corpus)
        pattern["examples"][0]["pl"] = "Zupełnie inne zdanie."
        self.assert_survives_normalisation(corpus, "edited new example")

    def test_a_second_example_on_a_pattern_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.an_example_pattern(corpus)
        pattern["examples"].append(copy.deepcopy(pattern["examples"][0]))
        self.assert_survives_normalisation(corpus, "duplicated example")

    def test_a_repinned_tier_two_digest_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["reviewEvents"][-1]["scopeDigest"] = "sha256:" + "0" * 64
        self.assert_survives_normalisation(corpus, "repinned digest")

    def test_a_duplicated_editorial_acceptance_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["reviewEvents"].append(copy.deepcopy(pattern["reviewEvents"][-1]))
        normalised = self.assert_survives_normalisation(corpus, "duplicate accept")
        self.assertIn(
            "editorial-review",
            {event["kind"] for event
             in rows_by_id(normalised)[pattern["id"]][2]["reviewEvents"]})

    def test_a_missing_correction_where_prose_changed_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["reviewEvents"] = [event for event in pattern["reviewEvents"]
                                   if event["kind"] != "correction"]
        self.assert_survives_normalisation(corpus, "missing correction")

    def test_a_correction_on_an_unauthorized_pattern_is_not_absorbed(self):
        corpus = self.mutated()
        pattern = rows_by_id(corpus)[UNTOUCHED][2]
        pattern["reviewEvents"].append({
            "kind": "correction", "decision": "accept", "reviewerRef": OWNER,
            "reviewedAt": H2_DATE, "note": "unauthorized"})
        normalised = self.assert_survives_normalisation(corpus, "stray correction")
        self.assertIn(
            "correction",
            {event["kind"] for event
             in rows_by_id(normalised)[UNTOUCHED][2]["reviewEvents"]})

    def test_a_fresh_product_approval_is_not_absorbed_and_is_visible(self):
        corpus = self.mutated()
        lemma, meaning, pattern = rows_by_id(corpus)[
            sorted(H2.H2_EXPECTED_PATTERN_IDS)[0]]
        pattern["reviewEvents"].append({
            "kind": "product-approval", "decision": "accept", "scopeVersion": 1,
            "scopeDigest": T.review_scope_digest("product-approval", lemma,
                                                 meaning, pattern),
            "reviewerRef": OWNER, "reviewedAt": H2_DATE,
            "note": "premature approval"})
        pattern["reviewState"] = "approved"
        normalised = self.assert_survives_normalisation(corpus, "fresh approval")
        self.assertEqual(
            2, len([event for event
                    in rows_by_id(normalised)[pattern["id"]][2]["reviewEvents"]
                    if event["kind"] == "product-approval"]))

    def test_a_fresh_reference_verification_is_not_absorbed(self):
        """Tier 1 was never re-run; one appended here stays visible."""
        corpus = self.mutated()
        _l, _m, pattern = rows_by_id(corpus)[
            sorted(H2.H2_EXPECTED_PATTERN_IDS)[0]]
        existing = [event for event in pattern["reviewEvents"]
                    if event["kind"] == "reference-verification"][-1]
        replayed = copy.deepcopy(existing)
        replayed["reviewedAt"] = H2_DATE
        replayed["note"] = "an unauthorised tier-1 re-run"
        pattern["reviewEvents"].append(replayed)
        normalised = self.assert_survives_normalisation(
            corpus, "fresh reference verification")
        self.assertIn(
            replayed,
            rows_by_id(normalised)[pattern["id"]][2]["reviewEvents"])

    def test_a_reference_verification_naming_a_human_is_refused(self):
        corpus = self.mutated()
        _l, _m, pattern = rows_by_id(corpus)[
            sorted(H2.H2_EXPECTED_PATTERN_IDS)[0]]
        for event in pattern["reviewEvents"]:
            if event["kind"] == "reference-verification":
                del event["actorRef"]
                event["reviewerRef"] = OWNER
                break
        self.assertNotEqual([], validate_editorial(corpus, build_context()))

    def test_an_editorial_acceptance_without_corroboration_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        del pattern["reviewEvents"][-1]["corroboratingActorRefs"]
        self.assertIn("EDITORIAL_CORROBORATION_REQUIRED",
                      codes(validate_editorial(corpus, build_context())))

    def test_the_reference_actor_cannot_corroborate_the_editorial_pass(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["reviewEvents"][-1]["corroboratingActorRefs"] = [REFERENCE_ACTOR]
        self.assertIn("REVIEW_ACTOR_INDEPENDENCE",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_forged_repository_reuse_is_refused(self):
        corpus = self.mutated()
        pattern_id = sorted(
            pattern_id for pattern_id, example in H2.H2_NEW_EXAMPLES.items()
            if example["origin"]["kind"] == "repository-reuse")[0]
        rows_by_id(corpus)[pattern_id][2]["examples"][0]["pl"] = "Nie to zdanie."
        self.assertIn("REPOSITORY_SOURCE_MISMATCH",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_generated_example_claiming_a_human_author_is_refused(self):
        corpus = self.mutated()
        pattern_id = sorted(
            pattern_id for pattern_id, example in H2.H2_NEW_EXAMPLES.items()
            if example["origin"]["kind"] == "editorial-generated")[0]
        origin = rows_by_id(corpus)[pattern_id][2]["examples"][0]["origin"]
        origin["authorRef"] = NATIVE_REVIEWER
        origin["authoredAt"] = H2_DATE
        self.assertIn("ORIGIN_EDITORIAL_FIELD_FORBIDDEN",
                      codes(validate_editorial(corpus, build_context())))

    def test_enabling_an_activity_on_an_editorial_reviewed_row_is_refused(self):
        corpus = self.mutated()
        pattern = self.a_translation_pattern(corpus)
        pattern["activityEligibility"] = ["reference"]
        self.assertIn("UNAPPROVED_ACTIVITY",
                      codes(validate_editorial(corpus, build_context())))

    def test_enabling_audio_on_any_example_is_refused(self):
        corpus = self.mutated()
        pattern = self.an_example_pattern(corpus)
        pattern["examples"][0]["audioEligible"] = True
        self.assertIn("AUDIO_NOT_AUTHORIZED",
                      codes(validate_editorial(corpus, build_context())))

    def test_a_freeze_admits_only_the_one_still_approved_pattern(self):
        """The 44 corrected rows are structurally unable to reach a release."""
        frozen = T.freeze_editorial(self.mutated(), 1, build_context())
        admitted = [pattern["id"]
                    for lemma in frozen["runtimeProjection"]["lemmas"]
                    for meaning in lemma["meanings"]
                    for pattern in meaning["patterns"]]
        self.assertEqual([UNTOUCHED], admitted)
        self.assertEqual(
            set(), set(admitted) & set(H2.H2_EXPECTED_PATTERN_IDS))


# ---------------------------------------------------------------------------
# 10.  The normaliser contract
# ---------------------------------------------------------------------------

class NormaliserContract(Phase4FH2TestCase):

    def test_the_normaliser_reproduces_the_baseline_corpus_byte_for_byte(self):
        self.assertEqual(git_blob(CORPUS_PATH),
                         H2.without_phase_4fh2_corpus_text(
                             H21.without_phase_4fh21_corpus_text(read(CORPUS_PATH))))

    def test_the_normaliser_reproduces_the_baseline_context_byte_for_byte(self):
        self.assertEqual(git_blob(CONTEXT_PATH),
                         H2.without_phase_4fh2_context_text(
                             H21.without_phase_4fh21_context_text(read(CONTEXT_PATH))))

    def test_the_document_normaliser_reproduces_the_baseline_document(self):
        self.assertEqual(
            self.baseline,
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(self.on_disk)))
        self.assertEqual(
            self.baseline_context,
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(self.on_disk_context)))

    def test_the_normaliser_is_idempotent_on_an_already_reverted_corpus(self):
        once = H2.without_phase_4fh2_content_completion(
            H21.without_phase_4fh21_product_reapproval(self.on_disk))
        self.assertEqual(once, H2.without_phase_4fh2_content_completion(
            H21.without_phase_4fh21_product_reapproval(once)))

    def test_the_text_normaliser_refuses_a_noncanonical_corpus_form(self):
        with self.assertRaises(AssertionError):
            H2.without_phase_4fh2_corpus_text(
                H21.without_phase_4fh21_corpus_text(
                    json.dumps(self.on_disk, ensure_ascii=False)))

    def test_the_normaliser_refuses_an_identity_outside_the_transition(self):
        with self.assertRaises(KeyError):
            H2.appended_h2_events("vp-p-not-a-real-pattern-000000000000")

    def test_the_pinned_transition_is_forty_four_rows_and_one_hundred_thirty_events(self):
        self.assertEqual(CHANGED_COUNT, len(H2.H2_EXPECTED_PATTERN_IDS))
        self.assertEqual(CHANGED_COUNT, len(H2.H2_APPENDED_EVENTS))
        self.assertEqual(
            TRANSLATION_PATTERN_COUNT * 3 + len(EXAMPLE_ONLY) * 2,
            sum(len(events) for events in H2.H2_APPENDED_EVENTS.values()))

    def test_the_normaliser_never_reads_a_live_row_to_decide_the_revert(self):
        source = read(NORMALISER_PATH)
        body = source.split('H2_CONTEXT_NOTICE_SUFFIX = (', 1)[1]
        for forbidden in ("review_scope_digest", "import priority7_tooling",
                          "subprocess", "open("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
