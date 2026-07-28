/* Po polsku - shared multiple-choice option builder
   ------------------------------------------------------------------------
   Pure helpers: no DOM, no app state, no storage, no playback, no Math.random.
   Randomness is INJECTED (`shuffle`), so the same input with the same shuffle
   always produces the same options and tests/test_distractors.js can exercise
   the code the app actually runs.

   WHY THIS FILE EXISTS
   A Listening question plays one Polish clip and offers four English meanings,
   exactly one of which is meant to be right. The corpus, though, teaches the
   same Polish word in more than one topic, and each topic writes its own gloss
   for it - one plain, one with a parenthetical, one with a second synonym
   after a slash. Choosing distractors by "any other card whose English text
   differs" let two of those into the same question. The learner heard one clip,
   both offered meanings were true of it, and whichever they picked, one of them
   was going to be marked wrong.

   That is not a handful of special cases to be listed here. It is a shape the
   data keeps producing, so no word and no card id is written into this file:
   tests/test_distractors.js rediscovers the whole affected set from the
   shipping corpus on every run and sweeps each one through this builder.

   THE RULE
   Two cards may not appear in one question when the learner cannot possibly
   tell them apart from what the question gives them:

     - the same HEARD PROMPT - they sound alike, so both answers are true;
     - the same VISIBLE LABEL - the same answer printed twice;
     - the same stable id, or literally the same card object.

   All three are decided on a normalised key (below), never on raw text.

   WHAT IS NOT DECIDED HERE
   Which cards may be asked at all (pp-usage.js), which question comes next, how
   an answer is scored, and what any of it looks like. This file only chooses a
   set of option SOURCES and hands them back with their identity intact, so the
   caller marks the right answer by the retained `correct` flag instead of
   comparing two strings that may be equal by accident. */
(function (global) {
  "use strict";
  var PP_DISTRACTOR = {};

  /* ---- comparison keys ---------------------------------------------------
     Normalisation answers one question: "would the learner experience these two
     as the same thing?" The key is never displayed and never written to a card.

     Punctuation folds to a space because it survives neither the ear nor a
     glance: the corpus holds one greeting written with a final "!" in two
     topics and without it in a third - one clip, three cards, and glosses that
     differ only by that mark. Case folds for the same reason.

     Diacritics do NOT fold. Two Polish words that differ only by a stroke or an
     ogonek are different words, and hearing them apart is the skill Listening
     is teaching; folding them would refuse to offer one as the other's
     distractor, which is precisely the useful question.

     toLowerCase() takes no locale argument on purpose: a locale-sensitive fold
     would make the key depend on the device's language settings, and this key
     is only ever compared with another key made by this same function. */
  PP_DISTRACTOR.normalizeKey = function (text) {
    if (typeof text !== "string") return "";
    var t = text;
    if (typeof t.normalize === "function") {
      try { t = t.normalize("NFC"); } catch (e) { /* older engines: compare as authored */ }
    }
    return t
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  };

  /* ---- default accessors -------------------------------------------------
     A caller may pass raw cards or pool items ({ c, topic }). These defaults
     read both shapes so the usual call site stays one line; every one of them
     can be replaced through the spec.

     A pool item whose `c` is missing is BROKEN, not a raw card: falling back to
     the wrapper would hand back an option with no text at all. */
  function defaultCardOf(item) {
    if (!item || typeof item !== "object") return null;
    if ("c" in item) return item.c && typeof item.c === "object" ? item.c : null;
    return item;
  }
  function defaultTopicOf(item, card) {
    if (item && typeof item === "object" && typeof item.topic === "string") return item.topic;
    return card && typeof card.topic === "string" ? card.topic : "";
  }
  function defaultLabelOf(card) {
    return card && typeof card.en === "string" ? card.en : "";
  }
  /* The heard prompt is whatever the main speaker would play. PP_USAGE owns that
     rule - a template speaks only a complete `audioText`, never its display
     pattern - so use it when it is loaded. The Listening call site passes
     PP_USAGE.mainAudioText explicitly, so this only covers a caller that does
     not, and `pl` is the answer that rule gives for an ordinary card anyway. */
  function defaultHeardOf(card) {
    if (!card) return "";
    if (global.PP_USAGE && typeof global.PP_USAGE.mainAudioText === "function") {
      return global.PP_USAGE.mainAudioText(card);
    }
    return typeof card.pl === "string" ? card.pl : "";
  }
  function defaultIdOf(card) {
    return card && typeof card.id === "string" ? card.id : "";
  }
  function identity(list) { return list; }

  function fn(candidate, fallback) {
    return typeof candidate === "function" ? candidate : fallback;
  }

  /* ---- the builder -------------------------------------------------------
     buildOptions({ correct, candidates, count, shuffle, ... }) ->
       { options: [record...], correct: record|null }

     A record is { label, card, item, topic, id, correct }: the visible text PLUS
     the source it came from, because "which option is right" has to survive two
     cards sharing a gloss.

     Nothing handed in is modified. `candidates` is only read, and every array
     returned is newly built, so a caller reshuffling the result cannot reach
     back into the pool. `shuffle` is expected to return a NEW array (index.html's
     gShuffle does); it is called on private copies either way.

     It never throws on bad data. A null candidate, a card with no gloss, a card
     with nothing to play: each is skipped, and when too few safe sources remain
     the question comes back SHORT rather than padded with an option that might
     also be right. Three honest choices beat four dishonest ones - but SHORT
     always means "no larger safe set exists in this pool", never "the first pick
     painted us into a corner" and never "the search gave up looking". Picking is
     an exhaustive search, not a single pass; see chooseBest.

     The CORRECT card is held to the same standard, and failing it is fatal to
     the whole question rather than to one option: with no card, no gloss or no
     heard prompt there is nothing to ask, and the answer is `{ options: [],
     correct: null }`. A caller must be able to tell "no question here" from "a
     question with a blank button". */
  PP_DISTRACTOR.buildOptions = function (spec) {
    var s = spec || {};
    var cardOf  = fn(s.cardOf, defaultCardOf);
    var topicOf = fn(s.topicOf, defaultTopicOf);
    var labelOf = fn(s.labelOf, defaultLabelOf);
    var heardOf = fn(s.heardOf, defaultHeardOf);
    var idOf    = fn(s.idOf, defaultIdOf);
    var shuffle = fn(s.shuffle, identity);

    var total = Math.floor(s.count);
    if (!(total > 0)) total = 4;

    function record(item, isCorrect) {
      var card = cardOf(item);
      return {
        label: card ? labelOf(card) : "",
        card: card,
        item: item,
        topic: topicOf(item, card),
        id: card ? idOf(card) : "",
        correct: !!isCorrect
      };
    }

    var right = s.correct == null ? null : record(s.correct, true);
    var rightLabel = right ? PP_DISTRACTOR.normalizeKey(right.label) : "";
    var rightHeard = right && right.card ? PP_DISTRACTOR.normalizeKey(heardOf(right.card)) : "";
    /* Three things make a question askable, and all three are required.

       No card, or nothing to print on the button, and there is nothing to ask:
       returning empty beats returning a blank option the learner cannot read.

       No HEARD PROMPT is the same refusal for the same reason. A card the main
       speaker cannot play gives the learner nothing to answer FROM - the clip
       is the whole question - and the answer would have to be guessed off the
       distractors. Worse, an empty heard key seeds nothing into the seen-set,
       so every other silent card in the pool would pass the "sounds the same"
       rule and could line up beside it. A caller handed an unplayable card has
       a pool problem, not a distractor problem; pp-usage.js already keeps those
       out of Listening, and this is the backstop for a caller that does not. */
    if (!right || !right.card || !rightLabel || !rightHeard) return { options: [], correct: null };

    /* The seen-sets start seeded with the answer itself, so the first rule any
       candidate meets is "you are not another way of saying the answer". */
    var seenLabel = Object.create(null);   /* null prototype: a gloss like "constructor" is just a gloss */
    var seenHeard = Object.create(null);
    var seenId    = Object.create(null);
    var seenCard  = [];

    seenLabel[rightLabel] = true;
    seenHeard[rightHeard] = true;
    if (right.id) seenId[right.id] = true;
    seenCard.push(right.card);

    var pool = Array.isArray(s.candidates) ? s.candidates : [];
    var wantTopic = right.topic;

    /* Same topic first, so the wrong answers are plausible neighbours rather
       than obviously unrelated words. Order inside each band is the caller's
       injected randomness; the two bands are never shuffled into each other. */
    var near = [], far = [];
    for (var i = 0; i < pool.length; i++) {
      var item = pool[i];
      var card = cardOf(item);
      if (!card) continue;
      (topicOf(item, card) === wantTopic ? near : far).push(item);
    }
    var ordered = shuffle(near.slice()).concat(shuffle(far.slice()));

    /* Individually safe candidates, still in near-then-far order. "Safe" here
       means only "may sit beside the ANSWER"; whether two of these may sit
       beside EACH OTHER is the search's problem, below. */
    var usable = [];
    for (var k = 0; k < ordered.length; k++) {
      var rec = record(ordered[k], false);
      var source = rec.card;
      if (!source) continue;
      if (seenCard.indexOf(source) !== -1) continue;         /* the answer, offered back */
      if (rec.id && seenId[rec.id]) continue;                /* the answer, by identity */
      var lk = PP_DISTRACTOR.normalizeKey(rec.label);
      var hk = PP_DISTRACTOR.normalizeKey(heardOf(source));
      if (!lk || !hk) continue;                              /* nothing to show, or nothing to play */
      if (seenLabel[lk] || seenHeard[hk]) continue;          /* reads the same, or sounds the same */
      usable.push({ rec: rec, l: lk, h: hk, id: rec.id, card: source });
    }

    return { options: shuffle([right].concat(chooseBest(usable, total - 1))), correct: right };
  };

  /* ---- choosing WHICH safe candidates, together --------------------------
     Taking the first safe candidate, then the next one still safe, and so on
     is the obvious way to fill a question and it is wrong. Safety is a rule
     about PAIRS, so an early pick can rule out two later cards through two
     different keys and leave the question an option short while a perfectly good
     combination sat there unused. Concretely, with one clip written two ways
     and one gloss written two ways among four candidates, the greedy first pick
     collides with two of the remaining three and the learner gets three buttons
     where four were available.

     So this searches instead. It looks for a full set of `want` candidates that
     are compatible with one another, and only when no such set exists does it
     settle for one fewer, and so on down. The search walks the candidates in
     the order it was given - same-topic first, each band already shuffled by the
     caller - and returns the FIRST complete combination in that order, so the
     topic preference and the injected randomness both survive intact and the
     same input still gives the same output. Backtracking away from an early
     same-topic card is allowed, and happens only when keeping it would cost the
     learner an option: a full question outranks any one preferred distractor.

     The search is EXACT. A short result always means the same thing - no larger
     mutually safe set exists anywhere in the pool - and never that the search
     gave up part way. There is deliberately no step budget and no approximation
     cutoff: a builder that quietly returns three buttons because it stopped
     looking is indistinguishable, from the outside, from a pool that honestly
     held only three, and that is exactly the confusion this phase exists to
     remove. Every short question must be the pool's fault, provably.

     Exactness is affordable because the DEPTH is tiny. A question asks for four
     options, so the search is for three distractors and never nests deeper than
     three levels. Two prunings keep even a hostile pool cheap, and both are
     exact - they only ever discard branches that provably cannot complete:

       - `want` never starts above the number of distinct labels or distinct
         clips actually present, since no combination can beat either count;
       - a branch is abandoned the moment too few candidates remain after the
         current position to finish the set.

     Real pools settle in a handful of steps: production looks for three among a
     few hundred and the first three it tries almost always fit. */
  function compatible(chosen, cand) {
    for (var i = 0; i < chosen.length; i++) {
      var c = chosen[i];
      if (c.card === cand.card) return false;                /* the same card twice */
      if (c.l === cand.l) return false;                      /* the same answer printed twice */
      if (c.h === cand.h) return false;                      /* two ways of writing one clip */
      if (cand.id && c.id === cand.id) return false;         /* the same card by identity */
    }
    return true;
  }

  /* The first compatible combination of exactly `want`, in list order, or null
     when the list holds none. Exhaustive: a null here is a fact about the pool,
     never about how long the search ran. */
  function combinationOf(list, want) {
    var chosen = [];
    function walk(start) {
      if (chosen.length === want) return true;
      for (var i = start; i < list.length; i++) {
        if (list.length - i < want - chosen.length) return false;   /* too few left to finish */
        if (!compatible(chosen, list[i])) continue;
        chosen.push(list[i]);
        if (walk(i + 1)) return true;
        chosen.pop();
      }
      return false;
    }
    return walk(0) ? chosen : null;
  }

  function chooseBest(list, want) {
    var labels = Object.create(null), heards = Object.create(null), nl = 0, nh = 0;
    for (var i = 0; i < list.length; i++) {
      if (!labels[list[i].l]) { labels[list[i].l] = true; nl++; }
      if (!heards[list[i].h]) { heards[list[i].h] = true; nh++; }
    }
    var ceiling = Math.min(want, list.length, nl, nh);
    for (var n = ceiling; n >= 1; n--) {
      var found = combinationOf(list, n);
      if (found) return found.map(function (x) { return x.rec; });
    }
    return [];
  }

  /* Convenience for a caller that only wants the visible strings (tests, mostly).
     Production deliberately does not use it: throwing the source away is what
     made two glosses of one word indistinguishable in the first place. */
  PP_DISTRACTOR.labelsOf = function (built) {
    var opts = built && built.options ? built.options : [];
    return opts.map(function (o) { return o.label; });
  };

  global.PP_DISTRACTOR = PP_DISTRACTOR;
})(typeof window !== "undefined" ? window : this);
