/* Po polsku - shared typed-answer validation
   ------------------------------------------------------------------------
   Pure helpers: no DOM, no app state, no storage, no audio, no randomness.
   Type It and the Mixed Quiz's typed questions both compare through here, so
   the two activities cannot drift apart, and tests/test_answer_validation.js
   exercises the same code the app runs.

   Two verdict tiers, tried in this order:
     normalize() - case, ellipsis, terminal punctuation, whitespace -> "right"
     a NEAR MISS - the same answer with something small mis-typed   -> "almost"
   Neither key is ever displayed; both exist only to compare.

   Two things count as a near miss, and they compose:
     fold()          - normalize() plus Polish diacritics removed
     hyphenVariants()- a word-forming hyphen written as nothing, or as a space

   THE "ALMOST" TIER HAS ONE GUARD, and it covers both near misses. Dropping
   the diacritics can map two genuinely different Polish words onto the same
   folded key, and a hyphen-free spelling can likewise be some other card's word
   as written. Calling either an "almost" tells the learner they nearly spelled
   a word they in fact spelled perfectly - it just belongs to a different card.
   So when the typed text is itself the exact answer of ANOTHER card the learner
   can be asked to type, the verdict is "wrong", not "almost".

   Which words those are is DATA, never a list in this file. The caller passes
   an answer index built from the cards the app has loaded (buildIndex below).
   Called with no index, classify() behaves exactly as it always did: the guard
   simply has nothing to consult, which is what the isolated comparator tests
   exercise.

   Rules preserved from the original inline tNormAns / tFold / tAccepted,
   awkward ones included, because none of them is this file's decision to make:

     - a slash in visible text still creates no alternatives, and parenthetical
       text is still compared literally;
     - apostrophes, colons and commas still split a word rather than vanish;
     - there is no edit-distance or typo tolerance of any kind. */
(function (global) {
  "use strict";
  var PP_ANSWER = {};

  /* Comparison key for the "right" tier.
     Note what is deliberately absent: hyphens, parentheses and slashes are all
     left alone, so the "right" tier still matches them literally. A hyphen is
     forgiven one tier down, and only there - see hyphenVariants. */
  PP_ANSWER.normalize = function (s) {
    return s.toLowerCase()
      .replace(/\.\.\.|…/g, " ")
      .replace(/[?!.,;:“”"']/g, " ")
      .replace(/\s+/g, " ").trim();
  };

  /* The key EVERY "almost" comparison is made on: the normalized form with
     every Polish diacritic removed. NFD decomposes a-ogonek, e-ogonek, o-acute and
     friends into a base letter plus a combining mark, which the range strip
     then removes. The stroked l has no decomposition, so it is mapped by hand. */
  PP_ANSWER.fold = function (s) {
    return PP_ANSWER.normalize(s).normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/ł/g, "l");                    /* stroked l doesn't decompose */
  };

  /* ---- the hyphen near miss ----------------------------------------------
     A learner who writes the two halves of a hyphenated word as one word, or
     with a space between them, has produced the right letters in the right
     order and got one mark of punctuation wrong. That is a near miss, not a
     wrong answer. It is never RIGHT either: the card teaches a spelling, and
     the hyphen is part of it.

     WHICH CHARACTERS JOIN WORD PARTS. Only the three whose Unicode job is
     exactly that: the ASCII hyphen-minus and its two typographic spellings. En
     and em dashes are punctuation - they separate clauses, not word parts - and
     nothing in this file treats one mark of punctuation as another. */
  var HYPHENS = "-‐‑";   /* hyphen-minus, hyphen, non-breaking hyphen */

  /* WHICH HYPHENS COUNT: only a WORD-FORMING one, meaning it has a non-space
     character on both sides. A dash standing alone between spaces is being used
     as punctuation, and one at either end of the text is a stray mark. Removing
     either would weld two separate words together rather than repair one word
     the learner split. Positions, not a rewritten string, so the caller can put
     a different filler in each place. */
  function hyphenSpots(s) {
    var at = [];
    for (var i = 1; i < s.length - 1; i++) {
      if (HYPHENS.indexOf(s.charAt(i)) === -1) continue;
      if (/\s/.test(s.charAt(i - 1)) || /\s/.test(s.charAt(i + 1))) continue;
      at.push(i);
    }
    return at;
  }

  /* Each hyphen is dropped or spaced INDEPENDENTLY, so N of them make 2^N
     spellings - a learner with two hyphens to forget need not forget both the
     same way. The cap keeps that bounded whatever content ever lands; past it
     only the two uniform spellings are offered (all dropped, or all spaced),
     which is how someone who ignores hyphens altogether would type anyway. */
  var HYPHEN_LIMIT = 4;

  /* The supported near-miss spellings of ONE accepted answer: same characters
     in the same order, with each word-forming hyphen replaced by nothing or by
     a single space. Returns [] when there is nothing to vary, never returns the
     answer itself, and never repeats a spelling.
     Pure, and small: a short array of short strings, kept by nobody. */
  PP_ANSWER.hyphenVariants = function (answer) {
    if (typeof answer !== "string") return [];
    var at = hyphenSpots(answer);
    if (!at.length) return [];
    var out = [], seen = Object.create(null);   /* null prototype: a variant spelling is never an inherited key */
    function emit(chars) {
      var v = chars.join("");
      if (seen[v]) return;
      seen[v] = true;
      out.push(v);
    }
    function uniform(fill) {
      var chars = answer.split("");
      at.forEach(function (i) { chars[i] = fill; });
      emit(chars);
    }
    if (at.length > HYPHEN_LIMIT) { uniform(""); uniform(" "); return out; }
    for (var mask = 0; mask < (1 << at.length); mask++) {
      var chars = answer.split("");
      for (var b = 0; b < at.length; b++) chars[at[b]] = (mask >> b) & 1 ? " " : "";
      emit(chars);
    }
    return out;
  };

  /* Is `input` a supported near miss for this ONE accepted answer?
     Both near misses compare on the FOLD key, so they compose: dropping the
     hyphen AND the diacritics is still one verdict away from right, rather than
     two mistakes that cancel into "wrong".

     Variants come from the ACCEPTED answer only, never from the input. An
     answer the card spells WITHOUT a hyphen therefore stays wrong when the
     learner adds one: nothing here knows where a hyphen the card never wrote
     was supposed to go, and inventing a place for it would start accepting
     spellings no card teaches. */
  PP_ANSWER.nearMatch = function (input, answer) {
    if (typeof answer !== "string") return false;
    var folded = PP_ANSWER.fold(input);
    if (PP_ANSWER.fold(answer) === folded) return true;
    return PP_ANSWER.hyphenVariants(answer).some(function (v) {
      return PP_ANSWER.fold(v) === folded;
    });
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
     "wrong". The near-miss tier is only reached when the exact tier misses, so
     an answer spelled exactly as the card teaches it is settled before any
     near-miss spelling is even generated.

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
    if (acc.some(function (a) { return PP_ANSWER.nearMatch(input, a); }))
      return PP_ANSWER.ownedByOther(index, input, card) ? "wrong" : "almost";
    return "wrong";
  };

  global.PP_ANSWER = PP_ANSWER;
})(typeof window !== "undefined" ? window : this);
