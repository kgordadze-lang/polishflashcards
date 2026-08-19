"""Phase 4F-H3 normalisation, shared by every historical Priority 7 suite.

Phase 4F-H3 is the UI wording phase.  It made exactly two learner-facing
wording changes, both of them inside ``index.html`` and nowhere else:

1. the Priority 7 surface name is title case at its five **title/label** sites
   -- ``Verb patterns`` became ``Verb Patterns`` in the static ``<h1>``, in the
   runtime ``pTitle`` assignment, in the unavailable-state lead, in the topic
   ``name`` and in the ``LEVELS`` entry's ``level``;
2. the recognition-only learner badge says ``Understand for now`` instead of
   ``Understand this one``.

Nothing else moved.  Mid-sentence prose stays sentence case (``No verb
patterns with ...``), and the two loader-owned phrases -- ``See verb
patterns`` and ``Verb patterns with the <Case>`` -- are phrases rather than
titles and were deliberately left alone, so ``pp-verb-patterns.js`` is
untouched.

Every Priority 7 phase between ``f339efb`` and Phase 4F-H2.1 was editorial or
governance only and each states, against its own pinned baseline commit, that
``index.html`` did not move.  Phase 4F-H3 is the first phase since ``f339efb``
entitled to change a shipping file, so those historical claims need the
established phase-aware repair: they are restated over the shell with the H3
layer removed, exactly as the corpus claims are restated over the corpus with
the H2 and H2.1 layers removed::

    self.assertEqual(git_blob("index.html"),
                     H3.without_phase_4fh3_ui_wording(read("index.html")))

**The guarantee, and its whole basis.**  This module performs *only* the six
pinned reverse substitutions below and passes every other byte through
untouched.  It can therefore hide exactly those six strings and nothing else.
A caller that compares the normalised text to its baseline blob still sees, in
full:

* any other edit to ``index.html``, anywhere in the file;
* loader activation -- a runtime path named in the shell, a fetch, a
  ``loadRuntimeDocument`` call;
* runtime materialisation -- ``content/verb-patterns.json`` is a separate path
  this module never reads or reports on;
* an ``APP_VERSION``, shell-cache, ``schemaVersion`` or service-worker change;
* changed recognition-only semantics -- ``row.recognitionOnly`` and
  ``pattern.recognitionOnly`` are the guards around the badge, not the badge
  literal, and they lie outside every pinned string;
* governance or content mutation -- those live in ``editorial/`` and in
  ``pp-verb-patterns.js``, which this module refuses to touch.

A *partly* applied wording change is refused rather than half-reverted:
:func:`without_phase_4fh3_ui_wording` raises unless all six sites are on the
same side of the change.  So a shell where the badge was relabelled but the
title was not -- or where a sixth site was invented -- cannot pass anywhere.

This module is phase-owned and additive.  It imports nothing from the suites
that use it, so it can be imported from any of them without a cycle, it opens
no file, runs no subprocess and writes nothing.
"""

from __future__ import annotations

#: The only shipping path Phase 4F-H3 was entitled to touch.
PHASE_4FH3_SHIPPING_PATHS = ("index.html",)

#: The six pinned ``(pre-H3, post-H3)`` pairs, in file order.  Each side must
#: occur exactly once in the shell it belongs to; nothing here is derived from
#: the text being normalised.
H3_WORDING_EDITS = (
    # 1. the static screen title of the Priority 7 surface
    ('<h1 id="pTitle">Verb patterns</h1>',
     '<h1 id="pTitle">Verb Patterns</h1>'),
    # 2. the topic tile's name in the Grammar tab
    ('    name:"Verb patterns", emoji:',
     '    name:"Verb Patterns", emoji:'),
    # 3. the level name, which is the Grammar tab's own label for the surface
    ('LEVELS.push({ level:"Verb patterns", group:"grammar",',
     'LEVELS.push({ level:"Verb Patterns", group:"grammar",'),
    # 4. the runtime title, reasserted on every index render
    ('  $("pTitle").textContent = "Verb patterns";',
     '  $("pTitle").textContent = "Verb Patterns";'),
    # 5. the recognition-only learner badge
    ('"usage-badge u-recognition vp-recognition", "Understand this one"',
     '"usage-badge u-recognition vp-recognition", "Understand for now"'),
    # 6. the unavailable state's lead line, which stands in for the title
    ('  body.appendChild(pEl("p", "vp-lead", "Verb patterns"));',
     '  body.appendChild(pEl("p", "vp-lead", "Verb Patterns"));'),
)

#: The learner-facing strings Phase 4F-H3 retired.  No shell carrying the H3
#: layer may still show either of them.
H3_RETIRED_LEARNER_STRINGS = (
    "Understand this one",
)

#: The learner-facing strings Phase 4F-H3 introduced.
H3_INTRODUCED_LEARNER_STRINGS = (
    "Understand for now",
)

#: Wording Phase 4F-H3 deliberately did NOT change, as ``(path, snippet,
#: occurrences)``: mid-sentence prose in the shell, and the two loader-owned
#: phrases.  Listed so a suite can state the negative half of the decision from
#: one place instead of re-deriving it.
H3_UNCHANGED_PHRASES = (
    ("index.html", 'text:"No verb patterns with "', 1),
    ("pp-verb-patterns.js",
     'CARD_INDEX_DOORWAY_LABEL = "See verb patterns"', 1),
    ("pp-verb-patterns.js", '"Verb patterns with the "', 2),
)


def _edit_state(text: str, pre: str, post: str) -> str:
    """Report one pinned edit as ``absent``, ``complete`` or ``unrecognised``."""
    before, after = text.count(pre), text.count(post)
    if before == 1 and after == 0:
        return "absent"
    if after == 1 and before == 0:
        return "complete"
    return "unrecognised"


def phase_4fh3_layer_state(text: str) -> str:
    """Report the H3 layer in ``text`` as ``absent``, ``complete`` or ``partial``.

    ``absent`` and ``complete`` require *all six* sites to agree.  Anything
    else -- a site left behind, a site applied twice, a site edited into a
    seventh shape -- is ``partial``, which callers must not normalise.
    """
    states = {_edit_state(text, pre, post) for pre, post in H3_WORDING_EDITS}
    if states == {"absent"}:
        return "absent"
    if states == {"complete"}:
        return "complete"
    return "partial"


def without_phase_4fh3_ui_wording(text: str) -> str:
    """Return ``text`` as the shell stood before Phase 4F-H3.

    Only the six pinned strings are reversed, each exactly once.  Every other
    byte is passed through, so whatever the caller compares the result against
    still sees every other difference.

    A partly applied layer is refused, because half-reverting it would report a
    shell that never existed.
    """
    state = phase_4fh3_layer_state(text)
    if state == "partial":
        raise AssertionError(
            "the Phase 4F-H3 UI wording layer is present on some but not all "
            "of its six pinned sites; it is incomplete and must not be "
            "normalised away")
    if state == "absent":
        return text
    for pre, post in H3_WORDING_EDITS:
        text = text.replace(post, pre, 1)
    if phase_4fh3_layer_state(text) != "absent":       # pragma: no cover
        raise AssertionError(
            "reverting the Phase 4F-H3 layer did not reach the pre-H3 wording")
    return text


def with_phase_4fh3_ui_wording(text: str) -> str:
    """Return ``text`` with the H3 layer applied.  The exact inverse of above."""
    state = phase_4fh3_layer_state(text)
    if state == "partial":
        raise AssertionError(
            "the Phase 4F-H3 UI wording layer is present on some but not all "
            "of its six pinned sites; it cannot be completed mechanically")
    if state == "complete":
        return text
    for pre, post in H3_WORDING_EDITS:
        text = text.replace(pre, post, 1)
    return text


def is_phase_4fh3_path(path: str) -> bool:
    """True for the one shipping path Phase 4F-H3 was entitled to touch."""
    return path in PHASE_4FH3_SHIPPING_PATHS


def is_exactly_the_h3_ui_wording(path: str, baseline_text: str,
                                 live_text: str) -> bool:
    """True only when ``path``'s sole difference from baseline is the H3 layer.

    For the footprint guards.  Any other path is False, and ``index.html`` is
    True only when removing the pinned layer reproduces the baseline bytes
    exactly -- so a version bump, a loader activation, a semantics change or
    any unrelated shell edit is still reported as an unexpected footprint.
    """
    if not is_phase_4fh3_path(path):
        return False
    try:
        return without_phase_4fh3_ui_wording(live_text) == baseline_text
    except AssertionError:
        return False
