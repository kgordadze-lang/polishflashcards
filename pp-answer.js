/* Po polsku - shared typed-answer validation
   ------------------------------------------------------------------------
   Pure helpers: no DOM, no app state, no storage, no audio, no randomness.
   Type It and the Mixed Quiz's typed questions both compare through here, so
   the two activities cannot drift apart, and tests/test_answer_validation.js
   exercises the same code the app runs.

   Two comparison tiers, tried in this order:
     normalize() - case, ellipsis, terminal punctuation, whitespace -> "right"
     fold()      - normalize() plus Polish diacritics removed       -> "almost"
   Neither key is ever displayed; both exist only to compare.

   THE "ALMOST" TIER HAS ONE GUARD. Dropping the diacritics can map two
   genuinely different Polish words onto the same folded key. Calling one of
   them an "almost" for the other tells the learner they nearly spelled a word
   they in fact spelled perfectly - it just belongs to a different card. So
   when the typed text is itself the exact answer of ANOTHER card the learner
   can be asked to type, the verdict is "wrong", not "almost".

   Which words those are is DATA, never a list in this file. The caller passes
   an answer index built from the cards the app has loaded (buildIndex below).
   Called with no index, classify() behaves exactly as it always did: the guard
   simply has nothing to consult, which is what the isolated comparator tests
   exercise.

   Rules preserved from the original inline tNormAns / tFold / tAccepted,
   awkward ones included, because none of them is this file's decision to make:

     - a hyphen is not folded to a space, so "adres e mail" still fails
       against "adres e-mail";
     - a slash in visible text still creates no alternatives, and parenthetical
       text is still compared literally;
     - there is no edit-distance or typo tolerance of any kind. */
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

  /* WHICH CARD OWNS AN EXACT ANSWER. Pure, built once from the cards the app
     already has in memory; nothing here reads the DOM, storage or the clock.

     Shape - deliberately plain data, so tests can read it directly:
         { owners: { <normalized answer> : [ <card id>, ... ] } }

     Keys are normalize() output, the same key the "right" tier compares on.
     Values are STABLE CARD IDS, not card objects, so the index stays a small
     serialisable thing and two copies of one card cannot look like two owners.

     A card with no stable id owns nothing: it cannot be told apart from the
     card being answered, so counting it could turn a correct "almost" into a
     wrong "wrong". Skipping it keeps the pre-existing verdict instead.
     Empty answers are skipped, and a card that lists the same answer twice is
     recorded once.

     WHICH cards to pass in is the caller's decision, not this file's - see
     PP_USAGE.typedPracticeCards, which collects exactly the cards a learner
     can be asked to type. */
  PP_ANSWER.buildIndex = function (cards) {
    var owners = Object.create(null);   /* null prototype: no inherited keys to collide with */
    (cards || []).forEach(function (card) {
      if (!card || !card.id) return;
      var id = String(card.id);
      PP_ANSWER.accepted(card).forEach(function (a) {
        if (typeof a !== "string") return;
        var key = PP_ANSWER.normalize(a);
        if (!key) return;
        var list = owners[key] || (owners[key] = []);
        if (list.indexOf(id) < 0) list.push(id);
      });
    });
    return { owners: owners };
  };

  /* Is `text` the exact accepted answer of some card OTHER than `card`?
     False whenever the question cannot be answered safely - no index, no index
     contents, or a card with no id to compare against - so every uncertain case
     falls back to the verdict this guard did not exist to change. */
  PP_ANSWER.ownedByOther = function (index, text, card) {
    if (!index || !index.owners) return false;
    var self = card && card.id ? String(card.id) : "";
    if (!self) return false;
    var list = index.owners[PP_ANSWER.normalize(text)];
    if (!Array.isArray(list)) return false;   /* also shrugs off an inherited key on a hand-built index */
    return list.some(function (id) { return id !== self; });
  };

  /* The verdict for one typed answer against one card: "right" | "almost" |
     "wrong". The fold tier is only reached when the normalize tier misses,
     exactly as the two inline copies did.

     `index` is optional. Passing one only ever downgrades an "almost" to a
     "wrong"; it can never change a "right", because an exact answer for THIS
     card is settled by the first tier before the guard is consulted. Two cards
     sharing the same exact Polish answer therefore both keep it as "right".

     Blank input is NOT special-cased here. Both callers guard with
     `if(!PP_ANSWER.normalize(val))` before they get this far, because what
     happens on blank input is a UI decision (keep focus, change nothing) that
     belongs with the DOM, not in a pure comparator. */
  PP_ANSWER.classify = function (input, card, index) {
    var acc = PP_ANSWER.accepted(card);
    var norm = PP_ANSWER.normalize(input);
    if (acc.some(function (a) { return PP_ANSWER.normalize(a) === norm; })) return "right";
    var folded = PP_ANSWER.fold(input);
    if (acc.some(function (a) { return PP_ANSWER.fold(a) === folded; }))
      return PP_ANSWER.ownedByOther(index, input, card) ? "wrong" : "almost";
    return "wrong";
  };

  global.PP_ANSWER = PP_ANSWER;
})(typeof window !== "undefined" ? window : this);
