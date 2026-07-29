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
     - the same stable id, or literally the same card object;
     - the same AUTHORED SENSE GROUP - different sentences, one shared meaning.

   The first three are decided on a normalised key (below), never on raw text.

   WHY THE FOURTH RULE IS AUTHORED AND NOT INFERRED
   Normalising a whole string catches a gloss written twice with one bracket
   moved. It cannot catch two DIFFERENT sentences that happen to share one true
   meaning: the strings genuinely differ, and no fold of them will ever say
   otherwise. What makes such a question unfair is a fact about MEANING - both
   buttons hold a true answer to the one prompt - and meaning is not recoverable
   from the characters.

   Everything automatic that could be tried here is wrong in one of two
   directions. Splitting on slashes, matching substrings or counting shared
   words would fire on a masculine job title beside its feminine form, on an
   adjective beside its own negation, on a bare verb beside every phrase built
   from it. Those pairs are precisely the useful question, and refusing them
   would teach less, not more. Tightening the heuristic until they survive drops
   the real collisions along with them. An audit of every pair of cards that can
   share a pool ran a deliberately generous net over the whole corpus: it caught
   441 candidates, of which 23 were genuine. No rule over the text alone divides
   those two sets, and this file is not the place to pretend otherwise - it holds
   no word, no card id and no gloss from the data, and that is not an accident.

   So the conflict is DECLARED instead, one narrow shared answer sense at a time,
   by the person writing the glosses - `senseGroups: ["a-named-sense"]` - and
   this file only reads it. It never guesses one, and a card that declares
   nothing is governed by the three text rules exactly as before.

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
  /* The authored sense groups a card belongs to, or nothing. Reading `senseGroups`
     off the card is the DEFAULT, so both call sites - Listening and the Mixed Quiz -
     get the rule without either of them naming it, and neither has to keep its own
     copy of what "these two mean the same thing" means. */
  function defaultSenseOf(card) {
    return card ? card.senseGroups : null;
  }
  function identity(list) { return list; }

  /* ---- sense-group keys ---------------------------------------------------
     An authored key is an IDENTIFIER, not learner-facing text, so it is folded
     by case and surrounding whitespace only. normalizeKey() is deliberately not
     reused: it folds punctuation to spaces, which would make "a-named-sense"
     and "a named sense" the same group and quietly widen what an editor wrote.

     Everything else here is defensive rather than corrective. The runtime never
     throws and never repairs: a value that is not an array, an entry that is not
     a string, a blank entry, are all simply not restrictions, and the question is
     built by the three text rules alone. That is the safe direction to fail -
     the worst case is the question Phase 4D already shipped.

     Being lenient here does NOT make malformed metadata acceptable in the
     corpus; validate_content.py rejects every one of those shapes before it can
     be committed. The two are deliberately different: the validator's job is to
     stop bad data being authored, and this file's job is to keep a learner's
     round working if any ever escapes it.

     The returned array is always new, so a caller's `senseGroups` is never
     handed out, reordered or written to. */
  function senseSetOf(list) {
    if (!Array.isArray(list)) return [];
    var out = [], seen = Object.create(null);
    for (var i = 0; i < list.length; i++) {
      if (typeof list[i] !== "string") continue;
      var k = list[i].trim().toLowerCase();
      if (!k || seen[k]) continue;                     /* blank, or already counted */
      seen[k] = true;
      out.push(k);
    }
    return out;
  }
  /* Two option records conflict when their sense-group SETS intersect: one shared
     key is enough, and a card may hold several because one gloss can overlap two
     different neighbours in two different ways without those neighbours
     overlapping each other. */
  function sharesSense(a, b) {
    for (var i = 0; i < a.length; i++) {
      if (b.indexOf(a[i]) !== -1) return true;
    }
    return false;
  }

  function fn(candidate, fallback) {
    return typeof candidate === "function" ? candidate : fallback;
  }

  /* ---- the builder -------------------------------------------------------
     buildOptions({ correct, candidates, count, shuffle, ... }) ->
       { options: [record...], correct: record|null }

     A record is { label, card, item, topic, id, correct }: the visible text PLUS
     the source it came from, because "which option is right" has to survive two
     cards sharing a gloss. Sense groups are read to DECIDE the set and are then
     dropped: they are not part of a record, because nothing downstream renders,
     scores or announces them, and putting them on one would invite a caller to
     re-decide a question this builder has already answered.

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
    var senseOf = fn(s.senseOf, defaultSenseOf);
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
    /* The answer's own groups, so "you are not another way of saying the answer"
       covers the authored senses too and not only the printed string. */
    var rightSenses = senseSetOf(senseOf(right.card));

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
      var sk = senseSetOf(senseOf(source));
      if (sharesSense(rightSenses, sk)) continue;            /* a declared second way of meaning it */
      usable.push({ rec: rec, l: lk, h: hk, id: rec.id, card: source, s: sk });
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

     Authored sense groups are a pair rule of exactly that shape, so they are
     decided HERE, inside the search, and not by filtering chooseBest's answer
     afterwards. A post-filter would be the greedy bug wearing a different hat:
     it would drop a grouped option out of a finished set of four and hand back
     three, when swapping that one candidate for the next ungrouped one would
     have kept the question full. Because the rule lives in `compatible`, a
     grouped candidate is simply backtracked over, and four options are still
     found whenever four exist.

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

     Sense groups add no third pruning and need none. Both bounds above are still
     upper bounds once a rule is ADDED - a further constraint can only make sets
     smaller, never larger - and the countdown from `ceiling` to 1 already tries
     every smaller size in turn. So the search stays exact for free: it simply
     finds the largest set that satisfies four rules instead of three.

     Real pools settle in a handful of steps: production looks for three among a
     few hundred and the first three it tries almost always fit. */
  function compatible(chosen, cand) {
    for (var i = 0; i < chosen.length; i++) {
      var c = chosen[i];
      if (c.card === cand.card) return false;                /* the same card twice */
      if (c.l === cand.l) return false;                      /* the same answer printed twice */
      if (c.h === cand.h) return false;                      /* two ways of writing one clip */
      if (cand.id && c.id === cand.id) return false;         /* the same card by identity */
      if (sharesSense(c.s, cand.s)) return false;            /* one declared sense, two buttons */
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
