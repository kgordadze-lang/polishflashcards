/* Po polsku - usage metadata and activity eligibility
   ------------------------------------------------------------------------
   Pure helpers: no DOM, no app state, no side effects. index.html renders with
   them and tests/test_activities.js exercises them directly, so the rules the
   app runs are literally the rules under test.

   Four optional card fields drive everything here:
     register   formal | neutral | informal | slang | vulgar
     region     general | warsaw | regional
     production active | recognition-only
     warning    free learner-facing text

   All four are optional. Absent means the schema default - neutral / general /
   active - and a card carrying no metadata renders no chips at all. Most cards
   have none, so "no metadata" must stay the quiet, unremarkable case. */
(function (global) {
  "use strict";
  var PP_USAGE = {};

  /* "neutral" and "general" deliberately have no label: defaults are not shown. */
  PP_USAGE.REGISTER_LABEL = { formal: "Formal", informal: "Informal", slang: "Slang", vulgar: "Vulgar" };
  /* "Warsaw-associated", never "Warsaw only". `Mordor` names a specific Warsaw
     office district; `słoik` is merely associated with Warsaw and is understood
     well beyond it. The finer distinction lives in each card's hint. */
  PP_USAGE.REGION_LABEL = { warsaw: "Warsaw-associated", regional: "Regional" };
  PP_USAGE.RECOGNITION_LABEL = "Recognition only";

  PP_USAGE.isRecognitionOnly = function (card) {
    return !!card && card.production === "recognition-only";
  };

  /* ---- main-card audio ---------------------------------------------------
     WHICH string the main speaker plays, and whether the card has one at all.
     index.html plays what this returns; pp_audio_rule.py generates and verifies
     the same set from the same rule, so the clip that exists is always the clip
     the app asks for.

     A template's `pl` is a display PATTERN, not an utterance - nobody says
     "Gdzie jest...?" on its own. Speaking it taught the learner an unfinished
     phrase, so a template gets main audio only from a complete `audioText`, and
     when there is none it gets NO main audio. Falling back to `pl` is precisely
     the bug this rule exists to prevent, so there is deliberately no fallback -
     not to a clip, not to speechSynthesis. The card still DISPLAYS its canonical
     `pl`, and its complete `ex` keeps its own example audio.

     No card carries `audioText` today; authoring one is new learning content. */
  PP_USAGE.INCOMPLETE_MARK = /\.\.\.|…|[{}]/;
  PP_USAGE.isCompleteUtterance = function (text) {
    if (typeof text !== "string") return false;
    var t = text.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
    return !!t && !PP_USAGE.INCOMPLETE_MARK.test(t);
  };
  PP_USAGE.mainAudioText = function (card) {
    if (!card) return "";
    if (card.cardType === "template") {
      return PP_USAGE.isCompleteUtterance(card.audioText) ? card.audioText : "";
    }
    /* Standard cards are unchanged: `pl` is spoken as authored. The rule keys off
       cardType, never off how the text looks. */
    return typeof card.pl === "string" ? card.pl : "";
  };
  PP_USAGE.hasMainAudio = function (card) {
    return PP_USAGE.mainAudioText(card).replace(/\s+/g, " ").trim() !== "";
  };

  /* Chips to show beside the term: [{ text, cls }]. Empty for a default card.
     By DEFAULT this returns the COMPLETE label set - every surface that has no
     strength badge of its own (the card back, and the Type It / Listening / mixed
     answer panels) must show "Vulgar", because nothing else there says it.

     Pass { suppressStrengthDuplicate: true } ONLY on a surface that is already
     showing the strength badge - today just the flashcard FRONT - where a
     register chip reading the same word would print "Vulgar" twice. Suppression
     is a display choice on one surface; card.register and card.strength are never
     modified. */
  PP_USAGE.labels = function (card, opts) {
    if (!card) return [];
    var out = [];
    var reg = PP_USAGE.REGISTER_LABEL[card.register];
    var suppress = !!(opts && opts.suppressStrengthDuplicate);
    var dupOfStrength = suppress && reg && card.strength &&
      reg.toLowerCase() === String(card.strength).toLowerCase();
    if (reg && !dupOfStrength) out.push({ text: reg, cls: "u-" + card.register });
    var rgn = PP_USAGE.REGION_LABEL[card.region];
    if (rgn) out.push({ text: rgn, cls: "u-region" });
    if (PP_USAGE.isRecognitionOnly(card)) out.push({ text: PP_USAGE.RECOGNITION_LABEL, cls: "u-recognition" });
    return out;
  };

  /* One sentence for assistive tech: "Usage: Slang. Warsaw-associated. Recognition only."
     Takes the same options as labels() so the spoken text always matches the chips
     actually rendered on that surface. */
  PP_USAGE.summary = function (card, opts) {
    var ls = PP_USAGE.labels(card, opts);
    return ls.length ? "Usage: " + ls.map(function (l) { return l.text; }).join(". ") + "." : "";
  };

  /* May this card appear in a given activity?

       flashcard - everything, including podcast intros and templates: both are
                   explanatory cards the learner is meant to read
       search    - everything, for the same reason. The search screen indexes a
                   whole topic (every card's text) and returns TOPICS, so no card
                   is filtered out of it; this branch states that contract
                   explicitly rather than leaving it to fall through
       listen    - a RECOGNITION activity, so recognition-only cards are KEPT
       typeit    - active production, so recognition-only cards are excluded
       mixed     - the mixed quiz types answers, so it follows the production rule

     Templates and podcast intros stay excluded from every *practice* activity:
     both are explanatory, not producible. Topic-level gates (mature) stay in the caller.

     UNKNOWN ACTIVITY -> false. A typo'd or new activity name fails CLOSED: an
     empty pool is an obvious, visible breakage, whereas silently defaulting to
     the production rule would quietly let recognition-only cards into something
     that asks the learner to produce them. */
  PP_USAGE.eligibleFor = function (card, activity) {
    if (!card) return false;
    if (activity === "flashcard" || activity === "search") return true;
    if (card.intro || !card.pl || !card.en) return false;
    if (card.cardType === "template") return false;
    if (activity === "listen") return true;
    if (activity === "typeit" || activity === "mixed") return !PP_USAGE.isRecognitionOnly(card);
    return false;
  };

  global.PP_USAGE = PP_USAGE;
})(typeof window !== "undefined" ? window : this);
