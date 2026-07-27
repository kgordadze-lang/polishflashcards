/* Po polsku - shared typed-answer validation
   ------------------------------------------------------------------------
   Pure helpers: no DOM, no app state, no storage, no audio, no randomness.
   Type It and the Mixed Quiz's typed questions both compare through here, so
   the two activities cannot drift apart, and tests/test_answer_validation.js
   exercises the same code the app runs.

   EXTRACTION ONLY. Every rule below is lifted verbatim from the former inline
   tNormAns / tFold / tAccepted in index.html, escapes included. Nothing here
   is a fix, and the known-awkward cases are preserved on purpose so this step
   can be proved behaviour-neutral:

     - a hyphen is not folded to a space, so "adres e mail" still fails
       against "adres e-mail";
     - "piec" and the number five fold to the same key, so typing one for the
       other still lands in the "almost" tier;
     - a slash in visible text still creates no alternatives, and parenthetical
       text is still compared literally;
     - there is no edit-distance or typo tolerance of any kind.

   Whether any of those should change is a separate decision. This file exists
   to make that decision testable, not to pre-empt it.

   Two comparison tiers, tried in this order:
     normalize() - case, ellipsis, terminal punctuation, whitespace -> "right"
     fold()      - normalize() plus Polish diacritics removed       -> "almost"
   Neither key is ever displayed; both exist only to compare. */
(function (global) {
  "use strict";
  var PP_ANSWER = {};

  /* Comparison key for the "right" tier.
     Note what is deliberately absent: hyphens, parentheses and slashes are all
     left alone, so they must match literally. */
  PP_ANSWER.normalize = function (s) {
    return s.toLowerCase()
      .replace(/\.\.\.|…/g, " ")
      .replace(/[?!.,;:“”"']/g, " ")
      .replace(/\s+/g, " ").trim();
  };

  /* Comparison key for the "almost" tier: the normalized form with every
     Polish diacritic removed. NFD decomposes a-ogonek, e-ogonek, o-acute and
     friends into a base letter plus a combining mark, which the range strip
     then removes. The stroked l has no decomposition, so it is mapped by hand. */
  PP_ANSWER.fold = function (s) {
    return PP_ANSWER.normalize(s).normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/ł/g, "l");                    /* stroked l doesn't decompose */
  };

  /* Accepted answers = the canonical `pl` PLUS any explicit `acceptedAnswers`.
     No implicit split on "/" - a slash in visible text never creates
     alternatives. The canonical `pl` is always first: the "Reveal a letter"
     hint reads element 0 and must spell out the form the card displays.
     A bare string is accepted as shorthand for { pl: string }.
     The card and its acceptedAnswers array are never mutated. */
  PP_ANSWER.accepted = function (card) {
    if (typeof card === "string") card = { pl: card };
    var out = [card.pl];
    (card.acceptedAnswers || []).forEach(function (a) {
      if (a && out.indexOf(a) < 0) out.push(a);
    });
    return out;
  };

  /* The verdict for one typed answer against one card: "right" | "almost" |
     "wrong". The fold tier is only reached when the normalize tier misses,
     exactly as the two inline copies did.

     Blank input is NOT special-cased here. Both callers guard with
     `if(!PP_ANSWER.normalize(val))` before they get this far, because what
     happens on blank input is a UI decision (keep focus, change nothing) that
     belongs with the DOM, not in a pure comparator. */
  PP_ANSWER.classify = function (input, card) {
    var acc = PP_ANSWER.accepted(card);
    var norm = PP_ANSWER.normalize(input);
    if (acc.some(function (a) { return PP_ANSWER.normalize(a) === norm; })) return "right";
    var folded = PP_ANSWER.fold(input);
    if (acc.some(function (a) { return PP_ANSWER.fold(a) === folded; })) return "almost";
    return "wrong";
  };

  global.PP_ANSWER = PP_ANSWER;
})(typeof window !== "undefined" ? window : this);
