"""Priority 7 Phase 4F-H3 — the UI wording change, and nothing else.

Phase 4F-H2.1 recorded the product owner's approval of the corrected H2
content and closed with one item outstanding: the learner-facing wording.
Phase 4F-H3 is that item.  It makes exactly two approved changes, both inside
``index.html``:

1. **Title case for the surface name.**  ``Verb patterns`` became ``Verb
   Patterns`` at its five *title/label* sites -- the static ``<h1>``, the
   runtime ``pTitle`` assignment, the unavailable-state lead that stands in for
   the title, the Grammar topic tile's ``name`` and the ``LEVELS`` entry's
   ``level``.  Mid-sentence prose was left in sentence case.
2. **The recognition-only learner badge** says ``Understand for now`` instead
   of ``Understand this one``.

**What it deliberately did not change, and why.**  Two phrases contain the
surface name but are not titles, so they keep sentence case:

* ``See verb patterns`` -- a card-back doorway, and the sibling of ``See how
  this verb is used``.  Both are call-to-action sentences on the same control,
  and title casing one of a matched pair would break the pair.
* ``Verb patterns with the <Case>`` -- the label on the ``.vp-continue``
  button at the end of a case lesson, and its accessible name.  The loader
  comment that owns it states its job in so many words: it promises exactly
  what the destination shows.  It is a description of a filtered view, not the
  name of a surface, and it reads as one sentence with the case name inside
  it.

Both live in ``pp-verb-patterns.js``, which is therefore byte-identical to the
baseline, and both were classified as phrases rather than titles by Phase
4F-H1.  Re-inspected against this tree, that classification still holds and is
re-asserted below rather than assumed.

**Boundary.**  This is the first phase since ``f339efb`` entitled to change a
shipping file.  It changed six lines of one file.  No canonical content, no
governance event, no audio, no activity eligibility, no runtime projection, no
version, no cache generation and no service worker moved.  The historical
suites that state "``index.html`` did not move" now state it over the shell
with the H3 layer removed, via the phase-owned
``tests/priority7_phase4fh3_normalizer.py``.

Run:  python3 -m unittest tests.test_priority7_phase4fh3
"""

from __future__ import annotations

import ast
import collections
import difflib
import hashlib
import json
import os.path as _h3_os_path
import re
import subprocess
import sys as _h3_sys
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
if str(ROOT) not in _h3_sys.path:
    _h3_sys.path.insert(0, str(ROOT))
_H3_DIR = _h3_os_path.dirname(_h3_os_path.abspath(__file__))
if _H3_DIR not in _h3_sys.path:
    _h3_sys.path.insert(0, _H3_DIR)

import priority7_phase4fh3_normalizer as H3  # noqa: E402

CORPUS_PATH = "editorial/verb-pattern-candidates.json"
CONTEXT_PATH = "editorial/priority-7-authoring-context.json"
NORMALISER_PATH = "tests/priority7_phase4fh3_normalizer.py"
SUMMARY_PATH = "reports/priority-7-phase-4fh3-ui-wording-summary.md"
PUBLIC_RUNTIME_PATH = "content/verb-patterns.json"

#: Phase 4F-H3 arrived on top of this commit and states every immutability
#: claim against it, never against a moving ``HEAD``.
BASELINE_COMMIT = "fa524f68bada3f0b893c8ed94835bfaa274a9b35"
BASELINE_TREE = "c95e19834d863f2c7690147d856e01428e2b4190"

#: Digests of the two private editorial files, which H3 must not have touched.
CORPUS_SHA256 = (
    "3613a841a992d5848b4c422b247075c15a75efcf69b85070c6fb4168a011ee3f")
CONTEXT_SHA256 = (
    "4ab2bb4b1ae0fa522ec68822731a547cc04a51858beab6e2cd6ff9ae69c79a1c")

#: The governance state H3 inherited and must return unchanged.
PATTERN_COUNT = 45
EXAMPLE_COUNT = 45
APPROVED_COUNT = 45
LEMMA_COUNT = 30
MEANING_COUNT = 34
RECOGNITION_ONLY_COUNT = 4
ACTIVE_PRODUCTION_COUNT = 41
EXPECTED_EVENTS = {
    "reference-verification": 47,
    "editorial-review": 133,
    "correction": 42,
    "product-approval": 89,
}

#: Every shipping file except the one H3 was entitled to change.  Each must be
#: byte-identical to the baseline commit.
UNTOUCHED_SHIPPING_FILES = (
    "sw.js", "manifest.json", "pp-verb-patterns.js", "pp-usage.js",
    "pp-answer.js", "pp-distractor.js", "pp-migrate.js", "sitemap.xml",
    "audio-manifest.json", "data-a1.js", "data-a2.js", "data-b1.js",
    "data-grammar.js", "data-podcasts.js", "data-scenarios.js",
    "data-verbs.js", "validate_content.py", "build_pages.py",
    "verify_audio.py", "pp_audio_rule.py", "priority7_tooling.py",
    "generate_audio.py", "robots.txt", "CNAME",
)

#: The five sites where the surface name functions as a title or a label.
#: Every one of them is title case after H3.
TITLE_SITES = (
    '<h1 id="pTitle">Verb Patterns</h1>',
    '    name:"Verb Patterns", emoji:',
    'LEVELS.push({ level:"Verb Patterns", group:"grammar",',
    '  $("pTitle").textContent = "Verb Patterns";',
    '  body.appendChild(pEl("p", "vp-lead", "Verb Patterns"));',
)

#: Wording that contains the surface name but is prose or a call to action.
#: H3 left every one of these in sentence case.  Sourced from the phase-owned
#: normaliser so the decision is recorded once.
SENTENCE_CASE_SITES = H3.H3_UNCHANGED_PHRASES

(RECOGNITION_BADGE,) = H3.H3_INTRODUCED_LEARNER_STRINGS
(RETIRED_BADGE,) = H3.H3_RETIRED_LEARNER_STRINGS


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


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_function(source, name):
    """Return one top-level ``function name(...){...}`` body, braces matched.

    A blunt brace counter is enough here because the shell's Priority 7
    functions contain no brace inside a string or a regular expression; the
    guard below fails loudly rather than returning a truncated body.
    """
    start = source.index(f"function {name}(")
    depth = 0
    for position in range(start, len(source)):
        character = source[position]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[start:position + 1]
    raise AssertionError(f"unbalanced braces extracting {name}")


def iter_patterns(corpus):
    for lemma in corpus.get("lemmas", []):
        for meaning in lemma.get("meanings", []):
            for pattern in meaning.get("patterns", []):
                yield lemma, meaning, pattern


def load_corpus():
    return json.loads(read(CORPUS_PATH))


def footprint():
    """Every path this workspace has touched, committed or not.

    Read from both ``git status`` and the diff against the pinned baseline, so
    the claim means the same before and after the candidate is committed.
    """
    changed = set()
    status = git("status", "--porcelain")
    changed |= {line[3:].strip().strip('"')
                for line in status.stdout.splitlines() if line.strip()}
    committed = git("diff", "--name-only", BASELINE_COMMIT, "HEAD")
    if committed.returncode == 0:
        changed |= {line.strip() for line in committed.stdout.splitlines()
                    if line.strip()}
    return changed


# ---------------------------------------------------------------------------
# 1.  The title-case decision, at exactly five sites
# ---------------------------------------------------------------------------

class TitleCaseTests(unittest.TestCase):
    """``Verb Patterns`` where the name is a title or a label, and nowhere else."""

    def setUp(self):
        self.index = read("index.html")

    def test_every_title_and_label_site_is_title_case(self):
        for site in TITLE_SITES:
            with self.subTest(site=site.strip()):
                self.assertEqual(1, self.index.count(site))

    def test_there_are_exactly_five_title_sites_and_no_sixth(self):
        """The count is pinned, so a sixth site cannot appear unnoticed.

        Comments are excluded: the shell's prose about the surface is not a
        learner-facing label, and three CSS/JS comments already said ``Verb
        Patterns`` before this phase.
        """
        code = re.sub(r"/\*.*?\*/", "", self.index, flags=re.S)
        self.assertEqual(5, code.count('Verb Patterns'))
        self.assertEqual(0, code.count('"Verb patterns"'))
        self.assertEqual(0, code.count('>Verb patterns<'))

    def test_the_static_and_runtime_titles_agree(self):
        """The markup title and the title the renderer reasserts are one string."""
        self.assertIn('<h1 id="pTitle">Verb Patterns</h1>', self.index)
        self.assertIn('$("pTitle").textContent = "Verb Patterns";',
                      extract_function(self.index, "pRenderIndex"))

    def test_the_unavailable_state_still_names_the_surface(self):
        unavailable = extract_function(self.index, "pRenderUnavailable")
        self.assertIn('pEl("p", "vp-lead", "Verb Patterns")', unavailable)
        self.assertIn("This reference isn’t ready to open yet.", unavailable)

    def test_the_tile_and_the_level_carry_the_same_name(self):
        topics = extract_function(self.index, "patternIndexTopics")
        self.assertIn('name:"Verb Patterns"', topics)
        self.assertIn('LEVELS.push({ level:"Verb Patterns", group:"grammar",',
                      self.index)
        self.assertEqual(1, self.index.count('level:"Verb Patterns"'))
        self.assertEqual(2, self.index.count("LEVELS.push("))

    def test_mid_sentence_prose_stays_sentence_case(self):
        """The negative half of the decision, stated as explicitly as the positive.

        ``No verb patterns with ...`` is a sentence about an empty result, and
        the two loader-owned strings are a call to action and a description of
        a filtered view.  None of them names a surface.
        """
        for relative, snippet, count in SENTENCE_CASE_SITES:
            with self.subTest(site=snippet):
                self.assertEqual(count, read(relative).count(snippet))

    def test_the_two_phrases_are_phrases_because_of_what_renders_them(self):
        """Re-inspected from the live tree, not inherited from Phase 4F-H1.

        ``See verb patterns`` is one of two mutually exclusive labels on the
        same card-back control; its sibling is a plain sentence.  ``Verb
        patterns with the <Case>`` is the label of a ``.vp-continue`` button
        and the text half of its accessible name.  Neither is a heading, a
        screen title, a level name or a tile name.
        """
        loader = read("pp-verb-patterns.js")
        self.assertIn('CARD_DOORWAY_LABEL = "See how this verb is used"', loader)
        self.assertIn('CARD_INDEX_DOORWAY_LABEL = "See verb patterns"', loader)
        # One control, two labels: the renderer picks exactly one of them.
        renderer = extract_function(self.index, "ppRenderCardPattern")
        self.assertIn("PP_VERB_PATTERNS.CARD_INDEX_DOORWAY_LABEL", renderer)
        self.assertIn("PP_VERB_PATTERNS.CARD_DOORWAY_LABEL", renderer)
        # The continuation is a button label plus its accessible name half.
        self.assertIn('label: "Verb patterns with the " + meta.en,', loader)
        self.assertIn(
            'srLabel: "Verb patterns with the " + meta.en + " (" + meta.pl + ")",',
            loader)
        self.assertIn('<button class="vp-continue" id="gPatternLink"', self.index)
        self.assertNotIn("Verb Patterns with the", loader)
        self.assertNotIn("See Verb Patterns", loader)

    def test_the_surface_name_is_not_a_key_for_anything(self):
        """Renaming a label may not move behaviour, so nothing may key off it.

        Routing keys off ``kind`` and ``surface``; the category keys off
        ``group``.  The one place the level name reaches a derived string is
        Listening's in-memory recency scope, which a reference topic can never
        enter.
        """
        self.assertIn('t.kind === "patterns" && t.surface === "verb-index"',
                      self.index)
        self.assertIn('if(lv.group === "grammar") return "grammar";', self.index)
        self.assertEqual(1, self.index.count('lv.level === "Grammar Cases"'))
        self.assertEqual(0, self.index.count('lv.level === "Verb Patterns"'))
        self.assertEqual(0, self.index.count('level === "Verb Patterns"'))
        # Search is case-folded, so the tile stays findable by either casing.
        self.assertIn('h = parts.join(" ").toLowerCase();', self.index)
        self.assertIn("const q = S.query.trim().toLowerCase();", self.index)


# ---------------------------------------------------------------------------
# 2.  The recognition-only badge
# ---------------------------------------------------------------------------

class RecognitionBadgeTests(unittest.TestCase):
    """One producer, two guarded call sites, and no semantics moved."""

    def setUp(self):
        self.index = read("index.html")
        self.loader = read("pp-verb-patterns.js")

    def test_the_phase_retired_one_string_and_introduced_one(self):
        """The badge change is a swap, not an addition to a growing set."""
        self.assertEqual(("Understand this one",),
                         H3.H3_RETIRED_LEARNER_STRINGS)
        self.assertEqual(("Understand for now",),
                         H3.H3_INTRODUCED_LEARNER_STRINGS)

    def test_the_badge_says_the_approved_words(self):
        self.assertIn(
            'return pEl("span", "usage-badge u-recognition vp-recognition", '
            f'"{RECOGNITION_BADGE}");', self.index)

    def test_the_retired_label_is_absent_from_every_shipping_file(self):
        for relative in ("index.html", "pp-verb-patterns.js", "pp-usage.js",
                         "sw.js", "manifest.json"):
            with self.subTest(path=relative):
                self.assertNotIn(RETIRED_BADGE, read(relative))

    def test_the_retired_label_is_absent_from_every_generated_page(self):
        for area in ("grammar", "guide", "vocabulary"):
            for page in sorted((ROOT / area).rglob("*.html")):
                with self.subTest(path=str(page.relative_to(ROOT))):
                    text = page.read_text(encoding="utf-8")
                    self.assertNotIn(RETIRED_BADGE, text)
                    self.assertNotIn(RECOGNITION_BADGE, text)

    def test_the_badge_has_exactly_one_producer(self):
        self.assertEqual(1, self.index.count("function pRecognitionChip()"))
        self.assertEqual(1, self.index.count(f'"{RECOGNITION_BADGE}"'))
        self.assertEqual(3, self.index.count("pRecognitionChip()"))
        self.assertEqual(2, self.index.count("appendChild(pRecognitionChip())"))

    def test_both_call_sites_are_guarded_by_recognition_only_and_nothing_else(self):
        """The guard is the whole eligibility rule, and it did not move."""
        row = extract_function(self.index, "pBuildRow")
        self.assertIn("if(row.recognitionOnly) main.appendChild(pRecognitionChip());",
                      row)
        self.assertEqual(1, row.count("pRecognitionChip"))
        self.assertNotIn("else", row.split("pRecognitionChip")[1].split("\n")[0])
        lemma = extract_function(self.index, "pRenderLemma")
        self.assertIn(
            "if(pattern.recognitionOnly) row.appendChild(pRecognitionChip());",
            lemma)
        self.assertEqual(1, lemma.count("pRecognitionChip"))

    def test_an_active_production_pattern_can_never_reach_the_badge(self):
        """There is no branch that badges anything but a recognition-only row.

        ``active-production`` is an editorial term and never appears in the
        shell at all, so no renderer can key off it even by accident.
        """
        self.assertNotIn("active-production", self.index)
        self.assertNotIn("teachingStatus", self.index)
        for name in ("pBuildRow", "pRenderLemma", "pRecognitionChip"):
            with self.subTest(function=name):
                body = extract_function(self.index, name)
                self.assertNotIn("active-production", body)
                self.assertNotIn("teachingStatus", body)

    def test_the_recognition_only_semantics_live_in_the_untouched_loader(self):
        """The derivation is upstream of the label and is byte-identical."""
        self.assertEqual(git_blob("pp-verb-patterns.js"), self.loader)
        self.assertIn(
            'return !!pattern && pattern.teachingStatus === "recognition-only";',
            self.loader)
        self.assertIn('TEACHING_STATUSES = ["active-production", "recognition-only"]',
                      self.loader)
        self.assertEqual(2, self.loader.count("recognitionOnly: isRecognitionOnly(pattern)"))

    def test_the_canonical_index_rows_carry_no_recognition_field_at_all(self):
        """An A-Z row is a lemma, not a pattern, so it can claim nothing.

        ``rows("all")`` sets ``isSummary = false`` and never sets
        ``recognitionOnly``; ``pBuildRow`` only reaches the badge inside the
        ``isSummary`` branch.
        """
        rows = extract_function(self.loader, "rows")
        canonical = rows.split("STATE.lemmas.forEach")[0]
        self.assertIn("row.isSummary = false;", canonical)
        self.assertNotIn("recognitionOnly", canonical)
        build = extract_function(self.index, "pBuildRow")
        self.assertLess(build.index("if(row.isSummary){"),
                        build.index("pRecognitionChip"))

    def test_the_badge_keeps_its_style_hooks_and_adds_no_new_one(self):
        """Wording only: the shorter label needed no style or colour change."""
        self.assertEqual(git_blob("index.html").count(".usage-badge.u-recognition{"),
                         self.index.count(".usage-badge.u-recognition{"))
        self.assertIn(
            ".usage-badge.u-recognition{border-color:#fcd34d;background:#fffbeb;"
            "color:#92400e}", self.index)
        self.assertIn(".vp-recognition{flex:0 0 auto;align-self:center}", self.index)
        self.assertLess(len(RECOGNITION_BADGE), len(RETIRED_BADGE))

    def test_the_badge_stays_plain_readable_text(self):
        """Accessibility is unchanged: no aria-label, no aria-hidden, no role.

        The badge is read as part of the row button's name and as ordinary
        text inside a pattern block, exactly as it was before the rewording.
        """
        chip = extract_function(self.index, "pRecognitionChip")
        for token in ("aria-label", "aria-hidden", "setAttribute", "role",
                      "innerHTML", "sr-only"):
            with self.subTest(token=token):
                self.assertNotIn(token, chip)
        self.assertIn("pEl(", chip)

    def test_the_card_side_recognition_label_is_a_different_string_untouched(self):
        """``pp-usage.js`` owns the card chip and was explicitly out of scope."""
        usage = read("pp-usage.js")
        self.assertEqual(git_blob("pp-usage.js"), usage)
        self.assertIn('PP_USAGE.RECOGNITION_LABEL = "Recognition only";', usage)
        self.assertNotIn(RECOGNITION_BADGE, usage)
        self.assertNotIn(RETIRED_BADGE, usage)


# ---------------------------------------------------------------------------
# 3.  Nothing else in the surface moved
# ---------------------------------------------------------------------------

class BehaviourIsUnchangedTests(unittest.TestCase):
    """Everything outside the six pinned strings is baseline-identical."""

    def setUp(self):
        # RESTATED over the pre-Phase-4F-I1 shell.  I1 is the atomic release:
        # it advanced APP_VERSION and added the one production loader call, on
        # top of the H3 wording layer this class owns.  Removing the pinned I1
        # layer puts the shell back where these claims were written, and every
        # byte I1 did not pin is still compared.
        self.index = pre_i1("index.html")
        self.baseline_index = git_blob("index.html")

    def test_the_shell_differs_from_the_baseline_by_exactly_the_wording(self):
        self.assertNotEqual(self.baseline_index, self.index)
        self.assertEqual(self.baseline_index,
                         H3.without_phase_4fh3_ui_wording(self.index))

    def test_the_change_is_six_lines_and_they_are_all_wording(self):
        # Computed over the pre-I1 shell rather than by shelling out to `git
        # diff`, so the six-line claim keeps meaning what it meant once the I1
        # release layer sits on top of it.
        diff_lines = list(difflib.unified_diff(
            self.baseline_index.splitlines(), self.index.splitlines(),
            lineterm="", n=0))
        added = [line for line in diff_lines
                 if line.startswith("+") and not line.startswith("+++")]
        removed = [line for line in diff_lines
                   if line.startswith("-") and not line.startswith("---")]
        self.assertEqual(6, len(added))
        self.assertEqual(6, len(removed))
        for line in added:
            with self.subTest(line=line.strip()):
                self.assertTrue("Verb Patterns" in line
                                or RECOGNITION_BADGE in line, line)

    def test_no_other_shipping_file_moved(self):
        """Compared with the Phase 4F-I1 release layer removed.

        H3 moved none of these.  I1 later moved ``sw.js`` and ``sitemap.xml``
        as part of one atomic release, so those two are admitted only by their
        own pinned I1 delta and every other path is still byte-identical.
        """
        bundle = i1_bundle()
        for relative in UNTOUCHED_SHIPPING_FILES:
            with self.subTest(path=relative):
                if i1_is_generated_output(relative):
                    self.assertTrue(I1.is_exactly_the_i1_transition(
                        relative, git_blob(relative), read(relative),
                        bundle=bundle), relative)
                    continue
                self.assertEqual(git_blob(relative), i1_shipping_text(relative))

    def test_no_generated_page_or_sitemap_moved(self):
        """H3 moved none of them; Phase 4F-I1 legitimately regenerated them.

        I1 advances APP_VERSION, which the generator stamps into every footer.
        Every path that moved is admitted only by its own pinned I1 delta --
        one footer version stamp per page, <lastmod> values alone in the
        sitemap -- and ``audio/`` still may not move at all.
        """
        bundle = i1_bundle()
        for area in ("grammar", "guide", "vocabulary", "sitemap.xml", "audio"):
            with self.subTest(path=area):
                changed = git("diff", "--name-only", BASELINE_COMMIT, "--", area)
                for relative in sorted(
                        line for line in changed.stdout.splitlines() if line):
                    with self.subTest(page=relative):
                        self.assertTrue(
                            i1_is_generated_output(relative), relative)
                        self.assertTrue(I1.is_exactly_the_i1_transition(
                            relative, git_blob(relative), read(relative),
                            bundle=bundle), relative)

    def test_the_wording_is_not_part_of_any_generated_output(self):
        """The generator neither writes nor knows either string, so nothing
        needed regenerating and nothing was regenerated."""
        generator = read("build_pages.py")
        for token in ("Verb Patterns", "Verb patterns", RECOGNITION_BADGE,
                      RETIRED_BADGE):
            with self.subTest(token=token):
                self.assertNotIn(token, generator)

    def test_navigation_filtering_and_the_card_doorway_are_untouched(self):
        for name in ("startPatterns", "pApplyFilter", "pRenderRows",
                     "pOpenLemma", "ppOpenCardPattern", "ppRenderCardPattern",
                     "gRenderPatternLink", "pBuildChip", "pFilterLabelParts",
                     "tCount", "categoryOf"):
            with self.subTest(function=name):
                self.assertEqual(extract_function(self.baseline_index, name),
                                 extract_function(self.index, name))

    def test_the_accessibility_helpers_and_focus_path_are_untouched(self):
        for name in ("ppSetActivityStatus", "ppFocusActivityTarget",
                     "ppScreenEntryTarget", "ppFocusAndRevealActivityTarget",
                     "pFocusRow", "pSetTextParts", "pAppendTextParts", "pEl"):
            with self.subTest(function=name):
                self.assertEqual(extract_function(self.baseline_index, name),
                                 extract_function(self.index, name))

    def test_the_layout_and_mobile_rules_are_untouched(self):
        style = self.index[self.index.index("<style>"):self.index.index("</style>")]
        baseline_style = self.baseline_index[
            self.baseline_index.index("<style>"):self.baseline_index.index("</style>")]
        self.assertEqual(baseline_style, style)

    def test_no_ui_element_was_added_or_removed(self):
        for token in ('<section class="screen"', "<button", "<h1", "<dialog",
                      'id="patterns"', "vp-recognition", "vp-row", "vp-filter"):
            with self.subTest(token=token):
                self.assertEqual(self.baseline_index.count(token),
                                 self.index.count(token))

    def test_no_audio_control_appeared_on_the_surface(self):
        screen = self.index[self.index.index('<section class="screen" id="patterns">'):]
        screen = screen[:screen.index("</section>")]
        for token in ("speed-toggle", "audio", "play", "Listen", "<audio"):
            with self.subTest(token=token):
                self.assertNotIn(token, screen)


# ---------------------------------------------------------------------------
# 4.  Content and governance are untouched
# ---------------------------------------------------------------------------

class ContentAndGovernanceTests(unittest.TestCase):
    """H3 is a UI phase: it may not read the corpus, let alone write it."""

    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus()
        cls.patterns = [pattern for _l, _m, pattern in iter_patterns(cls.corpus)]

    def test_the_two_editorial_files_are_byte_identical_to_the_baseline(self):
        for relative, digest in ((CORPUS_PATH, CORPUS_SHA256),
                                 (CONTEXT_PATH, CONTEXT_SHA256)):
            with self.subTest(path=relative):
                text = read(relative)
                self.assertEqual(git_blob(relative), text)
                self.assertEqual(digest, sha256_text(text))

    def test_the_governance_totals_are_exactly_what_h21_left(self):
        self.assertEqual(LEMMA_COUNT, len(self.corpus["lemmas"]))
        self.assertEqual(MEANING_COUNT,
                         sum(len(lemma["meanings"])
                             for lemma in self.corpus["lemmas"]))
        self.assertEqual(PATTERN_COUNT, len(self.patterns))
        self.assertEqual(EXAMPLE_COUNT,
                         sum(len(pattern["examples"]) for pattern in self.patterns))
        self.assertEqual(
            APPROVED_COUNT,
            sum(1 for pattern in self.patterns
                if pattern["reviewState"] == "approved"))

    def test_no_review_event_of_any_kind_was_created(self):
        counted = collections.Counter(
            event["kind"] for pattern in self.patterns
            for event in pattern["reviewEvents"])
        self.assertEqual(EXPECTED_EVENTS, dict(counted))
        self.assertEqual(0, counted["reopen"])

    def test_the_teaching_status_split_did_not_move(self):
        """The badge's population is a content fact, and H3 changed no content."""
        counted = collections.Counter(
            pattern["teachingStatus"] for pattern in self.patterns)
        self.assertEqual(RECOGNITION_ONLY_COUNT, counted["recognition-only"])
        self.assertEqual(ACTIVE_PRODUCTION_COUNT, counted["active-production"])
        self.assertEqual(PATTERN_COUNT, sum(counted.values()))

    def test_the_corpus_is_still_a_private_nonproduction_artifact(self):
        self.assertEqual("priority-7-editorial-nonproduction",
                         self.corpus["artifactStatus"])
        for token in ("releaseAuthorization", "patternDataRevision", "freeze"):
            with self.subTest(token=token):
                self.assertNotIn(token, read(CORPUS_PATH))


# ---------------------------------------------------------------------------
# 5.  Audio, activities and release stay exactly where they were
# ---------------------------------------------------------------------------

class AudioActivityAndReleaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.corpus = load_corpus()

    def test_activity_eligibility_is_empty_on_all_forty_five(self):
        self.assertEqual(
            0, sum(len(pattern["activityEligibility"])
                   for _l, _m, pattern in iter_patterns(self.corpus)))

    def test_no_example_is_audio_eligible(self):
        self.assertEqual(
            0, sum(1 for _l, _m, pattern in iter_patterns(self.corpus)
                   for example in pattern["examples"]
                   if example["audioEligible"] is True))

    def test_no_audio_file_or_manifest_entry_moved(self):
        self.assertEqual(git_blob("audio-manifest.json"),
                         read("audio-manifest.json"))
        changed = git("diff", "--name-only", BASELINE_COMMIT, "--", "audio")
        self.assertEqual("", changed.stdout.strip())

    def test_the_audio_rule_and_usage_module_are_untouched(self):
        for relative in ("pp_audio_rule.py", "pp-usage.js"):
            with self.subTest(path=relative):
                self.assertEqual(git_blob(relative), read(relative))

    def test_the_public_runtime_artifact_still_does_not_exist(self):
        # Superseded by Priority 7 Phase 4F-I1, the release that materialised
        # the official runtime.  The only document that may occupy that path
        # is exactly the I1 release artifact, pinned by digest and revision,
        # and it may only exist alongside the matching shell and worker.
        self.assertEqual("complete", i1_bundle().state)

    def test_the_loader_was_not_activated(self):
        """H3 activated nothing; Phase 4F-I1 is the phase that did.

        Restated over the shell and worker with the pinned I1 layer removed,
        so a SECOND activation, a different runtime URL, a preview or fixture
        URL, or any transport H3 could not have added is still reported here.
        """
        index = pre_i1("index.html")
        self.assertNotIn("content/verb-patterns.json", index)
        self.assertNotIn("loadRuntimeDocument", index)
        self.assertEqual(2, index.count("fetch("))
        for token in ("XMLHttpRequest", "EventSource", "importScripts"):
            with self.subTest(token=token):
                self.assertNotIn(token, index)
        self.assertNotIn("content/verb-patterns.json", pre_i1("sw.js"))

    def test_the_version_cache_and_migration_revision_did_not_advance(self):
        # The version and cache halves are superseded by Phase 4F-I1 and are
        # restated over the pre-I1 shell and worker.  The audio cache and the
        # migration markers are asserted LIVE: audio stays deferred and the
        # storage schema did not move, in I1 any more than in H3.
        self.assertIn('const APP_VERSION = "8.10";', pre_i1("index.html"))
        self.assertIn('const CACHE = "popolsku-v65";', pre_i1("sw.js"))
        self.assertIn('const AUDIO_CACHE = "popolsku-audio";', read("sw.js"))
        self.assertIn("PP_MIGRATE.CONTENT_MIGRATION_REVISION = 2;",
                      read("pp-migrate.js"))
        self.assertIn("PP_MIGRATE.SCHEMA_VERSION", read("pp-migrate.js"))

    def test_the_parked_g2_activation_was_not_recreated(self):
        for token in ("syntheticExercises", "runtimeProjection",
                      "releaseAuthorized"):
            with self.subTest(token=token):
                self.assertNotIn(token, read("index.html"))


# ---------------------------------------------------------------------------
# 6.  The phase-owned normaliser
# ---------------------------------------------------------------------------

class NormaliserTests(unittest.TestCase):
    """A closed, exact, six-string reverse patch -- and nothing wider."""

    def setUp(self):
        # The H3 normaliser's subject is the shell as H3 left it.  Phase
        # 4F-I1 later added its own pinned release layer on top, so the I1
        # layer is removed first; the H3 layer is what remains, and every byte
        # neither layer pins is still present for these tests to see.
        self.index = pre_i1("index.html")
        self.baseline_index = git_blob("index.html")

    def test_the_layer_is_complete_here_and_absent_at_the_baseline(self):
        self.assertEqual("complete", H3.phase_4fh3_layer_state(self.index))
        self.assertEqual("absent",
                         H3.phase_4fh3_layer_state(self.baseline_index))

    def test_the_revert_and_the_apply_are_exact_inverses(self):
        self.assertEqual(self.baseline_index,
                         H3.without_phase_4fh3_ui_wording(self.index))
        self.assertEqual(self.index,
                         H3.with_phase_4fh3_ui_wording(self.baseline_index))
        self.assertEqual(self.index, H3.with_phase_4fh3_ui_wording(
            H3.without_phase_4fh3_ui_wording(self.index)))

    def test_it_pins_six_edits_and_owns_one_path(self):
        self.assertEqual(6, len(H3.H3_WORDING_EDITS))
        self.assertEqual(("index.html",), H3.PHASE_4FH3_SHIPPING_PATHS)
        self.assertTrue(H3.is_phase_4fh3_path("index.html"))
        for other in ("sw.js", "pp-verb-patterns.js", CORPUS_PATH,
                      PUBLIC_RUNTIME_PATH):
            with self.subTest(path=other):
                self.assertFalse(H3.is_phase_4fh3_path(other))

    def test_a_partly_applied_layer_is_refused_not_half_reverted(self):
        for pre, post in H3.H3_WORDING_EDITS:
            with self.subTest(site=post.strip()):
                partial = self.index.replace(post, pre, 1)
                self.assertEqual("partial", H3.phase_4fh3_layer_state(partial))
                with self.assertRaises(AssertionError):
                    H3.without_phase_4fh3_ui_wording(partial)
                self.assertFalse(H3.is_exactly_the_h3_ui_wording(
                    "index.html", self.baseline_index, partial))

    def test_it_hides_nothing_but_its_own_six_strings(self):
        """Each forbidden mutation stays visible through the normaliser.

        This is the whole basis on which the historical suites may state their
        immutability claims over the normalised shell.
        """
        mutations = {
            "version bump":
                ('const APP_VERSION = "8.10";', 'const APP_VERSION = "8.11";'),
            "runtime path named in the shell":
                ('const APP_VERSION = "8.10";',
                 'const RUNTIME = "content/verb-patterns.json";\n'
                 'const APP_VERSION = "8.10";'),
            "loader activation":
                ('function pRenderIndex(enterScreen){',
                 'function pRenderIndex(enterScreen){ loadRuntimeDocument();'),
            "recognition-only guard widened":
                ("if(row.recognitionOnly) main.appendChild(pRecognitionChip());",
                 "main.appendChild(pRecognitionChip());"),
            "recognition-only guard inverted":
                ("if(pattern.recognitionOnly) row.appendChild(pRecognitionChip());",
                 "if(!pattern.recognitionOnly) row.appendChild(pRecognitionChip());"),
            "an unrelated label edited":
                ('blurb:"Which case does this verb take?"',
                 'blurb:"Which case?"'),
        }
        for label, (old, new) in mutations.items():
            with self.subTest(mutation=label):
                self.assertEqual(1, self.index.count(old), label)
                tampered = self.index.replace(old, new, 1)
                self.assertNotEqual(
                    self.baseline_index,
                    H3.without_phase_4fh3_ui_wording(tampered), label)
                self.assertFalse(H3.is_exactly_the_h3_ui_wording(
                    "index.html", self.baseline_index, tampered), label)

    def test_it_opens_no_file_imports_nothing_and_runs_no_subprocess(self):
        """A pure text function, so importing it from any suite is inert.

        Checked over the parse tree rather than the file text, so the module's
        own prose about subprocesses and writes cannot satisfy or break it.
        """
        tree = ast.parse(read(NORMALISER_PATH))
        modules = sorted(
            node.module if isinstance(node, ast.ImportFrom)
            else node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom)))
        self.assertEqual(["__future__"], modules)
        called = sorted({ast.unparse(node.func) for node in ast.walk(tree)
                         if isinstance(node, ast.Call)})
        # Only ``str`` methods, the module's own helpers and the exception it
        # raises.  Nothing that could reach a file, a process or the network.
        allowed = {"AssertionError", "text.count", "text.replace",
                   "_edit_state", "phase_4fh3_layer_state",
                   "without_phase_4fh3_ui_wording", "is_phase_4fh3_path"}
        self.assertEqual(set(), set(called) - allowed, called)

    def test_every_historical_suite_that_needed_it_uses_it(self):
        """Non-vacuity: the repair is applied everywhere it was required."""
        expected = (
            "test_priority7_phase4fa.py", "test_priority7_phase4fb3b.py",
            "test_priority7_phase4fc1c.py", "test_priority7_phase4fc2.py",
            "test_priority7_phase4fd31.py", "test_priority7_phase4ff2.py",
            "test_priority7_phase4fg1.py", "test_priority7_phase4fh2.py",
            "test_priority7_phase4fh21.py", "test_priority7_phase5a.py",
        )
        for name in expected:
            with self.subTest(suite=name):
                source = read(f"tests/{name}")
                self.assertIn("priority7_phase4fh3_normalizer", source)

    def test_the_c2d_reconstructed_clone_carries_the_normaliser(self):
        """Phase 4F-C2D rebuilds a clone and copies the suites into it.

        Those suites now import this normaliser, so the file has to travel
        with them or they cannot be imported at all.  Every earlier phase that
        repaired a historical suite added its normaliser to the same set.
        """
        source = read("tests/test_priority7_phase4fc2d.py")
        block = source.split("REPAIRED_SUITE_DEPENDENCIES = {")[1].split("}")[0]
        self.assertIn('"tests/priority7_phase4fh3_normalizer.py"', block)


# ---------------------------------------------------------------------------
# 7.  The phase boundary
# ---------------------------------------------------------------------------

class PhaseBoundaryTests(unittest.TestCase):

    def test_the_baseline_is_the_declared_commit_and_tree(self):
        self.assertEqual(
            BASELINE_TREE,
            git("rev-parse", f"{BASELINE_COMMIT}^{{tree}}").stdout.strip())

    def test_this_phase_touched_only_the_shell_tests_and_reports(self):
        touched = footprint()
        self.assertTrue(touched, "the footprint guard must have evidence")
        unexpected = sorted(
            path for path in touched
            if path != "index.html"
            and not path.startswith(("tests/", "reports/"))
            and not is_only_the_i1_activation(path))
        self.assertEqual([], unexpected, f"unexpected footprint: {unexpected}")

    def test_the_shell_is_in_the_footprint_and_is_only_the_wording(self):
        self.assertIn("index.html", footprint())
        self.assertTrue(H3.is_exactly_the_h3_ui_wording(
            "index.html", git_blob("index.html"), pre_i1("index.html")))

    def test_no_editorial_file_is_in_the_footprint(self):
        self.assertEqual(
            [], sorted(path for path in footprint()
                       if path.startswith("editorial/")))

    def test_the_phase_owned_artifacts_exist(self):
        for relative in (NORMALISER_PATH, SUMMARY_PATH,
                         "tests/test_priority7_phase4fh3.py"):
            with self.subTest(path=relative):
                self.assertTrue((ROOT / relative).exists(), relative)

    def test_no_release_or_push_action_occurred(self):
        self.assertEqual("", git("remote").stdout.strip())


if __name__ == "__main__":
    unittest.main()
