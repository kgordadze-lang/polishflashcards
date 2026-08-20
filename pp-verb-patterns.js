/* =========================================================================
   pp-verb-patterns.js - the verb-pattern reference consumer.

   The fifth isolated helper, alongside pp-usage.js / pp-answer.js /
   pp-distractor.js / pp-migrate.js: one global, no DOM and no storage, so
   tests can drive exactly the code the app runs. Module evaluation performs no
   network work. The one transport primitive below is dormant unless a caller
   explicitly invokes it with an injected request function and URL; ordinary
   startup has no such call site in Phase 3F-A.

   WHAT THIS FILE DECIDES, and all it decides:
     whether a parsed runtime document has the expected public shape, carries
     no private editorial field, and is therefore SAFE TO RENDER - plus the
     derived views the reference surface needs (the A-Z verb index, the case
     filter, chip/question/role/headline text, the card support index and the
     activity allowlist) - plus the two static case cross-link maps, which are
     pure lookups and hold no runtime state at all.

   WHAT THIS FILE CANNOT DECIDE, and must never be read as deciding:
     that a document came from an authorized release. A hand-written file of
     the right shape is indistinguishable here from an authorized one. Active
     membership, retained-identity history, review state and an authorized
     projection are established only by the build-time release machinery, on
     private inputs the browser never receives. This file therefore has no
     vocabulary for that concept and must not acquire one: nothing here may
     emit, log, name or infer a claim about release authorization.

   Accepting a document proves the document looked right. Rejecting one is the
   part that actually protects the learner.

   Three entry points, deliberately named apart:
     acceptRuntimeDocument(doc)  the parsed-document entry - it takes the bare
                                 public envelope {formatVersion,
                                 patternDataRevision, lemmas} and nothing else.
                                 A wrapped non-release fixture is REFUSED
                                 here, because the envelope check is closed.
     loadRuntimeDocument(request, url)
                                 the dormant shipping transport primitive. It
                                 requires an injected fetch-like function,
                                 accepts only an explicitly successful response,
                                 parses its JSON body once, and hands the whole
                                 candidate to acceptRuntimeDocument. Every path
                                 returns Promise<boolean>. It owns no URL, retry,
                                 timer, DOM or persistence policy.
     __acceptForTest(projection) the test-only injection entry. It runs the
                                 same validation and builds the same views, so
                                 the UI tests exercise the shipping derivation
                                 rather than a parallel one. Unwrapping a
                                 fixture wrapper happens in the test harness,
                                 never in this file and never in the app.
   ========================================================================= */
var PP_VERB_PATTERNS = (function () {
  "use strict";

  var FORMAT_VERSION = 1;
  /* The public envelope is closed: exactly these three keys, in any order.
     Anything else - including a non-release wrapper's own fields - is not the
     public runtime shape and is refused whole. */
  var ENVELOPE_KEYS = ["formatVersion", "patternDataRevision", "lemmas"];

  /* An exact mirror of PRIVATE_RUNTIME_KEYS in priority7_tooling.py, and a
     REJECTION LIST - not a set of fields this file reads. Defence in depth: the
     projector already guarantees their absence, and this is the last check
     before the DOM, where a private field reaching a learner cannot be undone.
     One member at any depth rejects the whole runtime value, because the
     presence of one is a whole-value failure and not a field to skip. */
  var PRIVATE_KEYS = [
    "artifactStatus", "specificationNotice", "internalScope", "key",
    "evidence", "sourceId", "sourceKind", "locator", "factType",
    "checkedAt", "reviewState", "reviewEvents", "reviewerRef", "reviewedAt",
    "scopeVersion", "scopeDigest", "supportingEvidenceDigests", "origin",
    "authorRef", "authoredAt", "repositorySource", "evidenceRefs",
    "sourceRegistry", "reviewerRegistry", "authorRegistry", "editorialNotes"
  ];

  /* ---------------- central case metadata ----------------
     The runtime document carries structure, not prose about structure: no case
     name and no diagnostic question is stored in it. Both are derived here,
     from one table, for all seven cases - so a corpus cannot disagree with
     itself about what Genitive is called or what it answers. */
  var CASE_ORDER = [
    "nominative", "genitive", "dative", "accusative", "instrumental",
    "locative", "vocative"
  ];
  var CASES = {
    nominative: { pl: "Mianownik", en: "Nominative",
      questions: ["kto?", "co?"], direct: true, prepositional: false },
    genitive: { pl: "Dopełniacz", en: "Genitive",
      questions: ["kogo?", "czego?"], direct: true, prepositional: true },
    dative: { pl: "Celownik", en: "Dative",
      questions: ["komu?", "czemu?"], direct: true, prepositional: true },
    accusative: { pl: "Biernik", en: "Accusative",
      questions: ["kogo?", "co?"], direct: true, prepositional: true },
    instrumental: { pl: "Narzędnik", en: "Instrumental",
      questions: ["kim?", "czym?"], direct: true, prepositional: true },
    /* never a direct complement - the editorial validator forbids it - so its
       questions exist only in the prepositional form. */
    locative: { pl: "Miejscownik", en: "Locative",
      questions: ["kim?", "czym?"], direct: false, prepositional: true },
    /* direct address, so it has no diagnostic question to fabricate. It cannot
       occur as a complement today; the row exists so a future document that
       carried one would render honestly rather than blank. */
    vocative: { pl: "Wołacz", en: "Vocative",
      questions: [], direct: false, prepositional: false, address: true }
  };
  /* The one non-case filter bucket. Infinitive and clause complements have no
     case at all, which is exactly why case cannot own the hierarchy. */
  var NO_CASE_BUCKET = "no-case";
  var NO_CASE_LABEL = "No case (verb / clause)";

  /* ---------------- case teaching stays where it is ----------------
     The seven dedicated case topics remain the owners of case teaching. This
     table is the ONLY thing either surface knows about the other: a static,
     two-way map between a case id and the id of the topic that teaches it.
     Nothing about a pattern is copied into a lesson and no case explanation is
     copied into a pattern - both directions are links, and this map is what
     makes them resolvable without either surface knowing the other's shape.

     It is deliberately independent of the runtime document. A case lesson can
     offer its continuation with no reference data accepted at all, and the link
     then lands on the reference surface's own neutral unavailable state - the
     same state its tile already routes to. An affordance that existed only once
     data existed could not have its empty state validated, and could not be
     found by a learner. */
  var CASE_LESSON_TOPICS = {
    nominative: "grammar-cases-nominative",
    genitive: "grammar-cases-genitive",
    dative: "grammar-cases-dative",
    accusative: "grammar-cases-accusative",
    instrumental: "grammar-cases-instrumental",
    locative: "grammar-cases-locative",
    vocative: "grammar-cases-vocative"
  };

  /* The card back's learner-facing strings. They live here, beside the
     derivation that decides which of them applies, so a renderer cannot invent a
     fourth outcome or soften a doorway into a claim.

     There are TWO doorways, because there are two different things a doorway can
     honestly promise. When every eligible claim belongs to the same verb, the
     ambiguity is only about which of that verb's meanings or patterns applies,
     so the doorway may name the verb and open its entry. When the claims belong
     to DIFFERENT verbs, nothing about "this verb" is established at all, and a
     doorway that said so would be asserting the very thing the ambiguity
     prevents - so it promises less and opens the whole index. */
  var CARD_POINTER_KEY = "Pattern";
  var CARD_DOORWAY_LABEL = "See how this verb is used";
  var CARD_INDEX_DOORWAY_LABEL = "See verb patterns";

  var COMPLEMENT_TYPES = ["case", "preposition-case", "infinitive", "clause"];
  var RELATION_TYPES = [
    "lexical-frame", "constructional-frame", "means-method",
    "subject-experiencer"
  ];
  var TEACHING_STATUSES = ["active-production", "recognition-only"];
  var ROLES = [
    "subject", "object", "recipient", "experiencer", "predicate", "content",
    "topic", "interlocutor", "means", "target"
  ];
  var ACTIVITY_KEYS = [
    "reference", "search", "grammar-choose", "grammar-build", "type-it",
    "listening", "mixed-quiz", "case-mix", "conversation"
  ];
  var CEFR_LEVELS = ["A1", "A2", "B1", "above-b1"];
  var USAGE_PRIORITIES = ["core", "common", "limited"];
  var REGISTERS = ["neutral", "formal", "informal"];
  var CLAUSE_KINDS = ["ze", "czy", "zeby", "interrogative"];
  var CLAUSE_TOKENS = {
    ze: "że …", czy: "czy …", zeby: "żeby …",
    interrogative: "pytanie …"
  };
  var CONTENT_KINDS = ["card", "topic", "drill", "scenario"];
  var CONTENT_PURPOSES = ["support", "practice", "context", "contrast"];

  /* One closed role -> one fixed English phrasing. The only place a role
     becomes words. `prosic kogos o cos` is the reason this line is never
     optional: two chips can carry the same case name, and then the role
     phrase is the only thing that tells them apart. */
  var ROLE_PHRASES = {
    subject: "the thing that does it",
    object: "what it applies to",
    recipient: "the person who receives it",
    experiencer: "the person it happens to",
    predicate: "the role or job",
    content: "what is learned, said or done",
    topic: "what it is about",
    interlocutor: "the person you talk to",
    means: "how it is done",
    target: "what it is aimed at"
  };
  /* One context-sensitive override, per the locked phrasebook. */
  var SUBJECT_EXPERIENCER_SUBJECT = "the thing that appeals";
  /* Which diagnostic question a headline placeholder uses. A person-shaped
     role takes the animate question, everything else the inanimate one. */
  var ANIMATE_ROLES = ["recipient", "interlocutor", "experiencer"];

  var LEVEL_LABELS = {
    A1: "A1", A2: "A2", B1: "B1", "above-b1": "B1+"
  };

  /* Polish letters fold onto their ASCII base for sorting and for the A-Z
     headings only. Lexical `sie` is part of the lemma and is never stripped:
     `bac sie` sorts under B, as one entry. */
  var FOLD = {
    "ą": "a", "ć": "c", "ę": "e", "ł": "l",
    "ń": "n", "ó": "o", "ś": "s", "ź": "z",
    "ż": "z"
  };

  var STATE = null;

  /* ---------------- small helpers ---------------- */
  function isPlainObject(value) {
    return !!value && typeof value === "object" && !Array.isArray(value);
  }
  function isNonEmptyString(value) {
    return typeof value === "string" && value.length > 0;
  }
  /* Own properties only, and it is deliberately NOT the `in` operator.
     `in` answers for the prototype chain too, so a recognised optional field
     inherited from a prototype would be treated as supplied - and reading it
     afterwards would run an inherited getter, executing somebody else's code
     during validation. A record is exactly its own properties: an inherited one
     is ignored, and an inherited getter is never touched, not even to ask
     whether it is there. */
  function hasOwn(value, key) {
    return Object.prototype.hasOwnProperty.call(value, key);
  }
  /* Required learner-facing and mechanics text. A run of spaces is not text: it
     renders as nothing, it reads as nothing, and a record carrying one is
     malformed rather than merely untidy. The record is REJECTED - never trimmed
     and accepted, because storing a value the record did not declare is exactly
     how an authored record and a rendered one drift apart. */
  function isFilledString(value) {
    return isNonEmptyString(value) && /\S/.test(value);
  }
  /* A uniqueness set that cannot be talked out of its own invariant.
     An ordinary {} cannot be used for this: `dict["__proto__"] = true` does not
     create an own property, it invokes the inherited setter, so two records that
     both use that exact string would each report "not seen yet" and the
     duplicate would be accepted. A prototype-less object has no such setter, so
     the invariant holds for ARBITRARY strings rather than for a blacklist of the
     ones somebody remembered. */
  function emptyDict() { return Object.create(null); }
  function seenBefore(dict, key) {
    if (hasOwn(dict, key)) return true;
    dict[key] = true;
    return false;
  }
  function isPositiveInteger(value) {
    return typeof value === "number" && isFinite(value) &&
      Math.floor(value) === value && value > 0;
  }
  function inList(list, value) { return list.indexOf(value) !== -1; }
  function keysOf(value) {
    var out = [], key;
    for (key in value) {
      if (hasOwn(value, key)) out.push(key);
    }
    return out;
  }
  /* Detach accepted JSON data from the caller's candidate. Validation finishing
     before STATE changes is only half of atomic acceptance if a caller can then
     mutate the same object and silently alter live views. Public runtime values
     contain only arrays, plain objects and JSON primitives, so this narrow copy
     is complete without serialization or a second schema. */
  function copyPublicValue(value) {
    var out, present, i;
    if (Array.isArray(value)) return value.map(copyPublicValue);
    if (!isPlainObject(value)) return value;
    out = {};
    present = keysOf(value);
    for (i = 0; i < present.length; i++) {
      out[present[i]] = copyPublicValue(value[present[i]]);
    }
    return out;
  }
  function closedKeys(value, required, optional) {
    var present = keysOf(value), i;
    for (i = 0; i < required.length; i++) {
      if (present.indexOf(required[i]) === -1) return false;
    }
    for (i = 0; i < present.length; i++) {
      if (required.indexOf(present[i]) === -1 &&
          optional.indexOf(present[i]) === -1) return false;
    }
    return true;
  }
  function fold(value) {
    var out = "", i, ch;
    for (i = 0; i < value.length; i++) {
      ch = value.charAt(i).toLowerCase();
      out += Object.prototype.hasOwnProperty.call(FOLD, ch) ? FOLD[ch] : ch;
    }
    return out;
  }
  /* Defence in depth behind the primary closed-key validators. Today every
     private name is also unknown at the public record level where it appears,
     so closedKeys() rejects it first. This recursive sweep intentionally stays
     as a second, independently testable barrier: if a private name ever
     overlaps a future public key, it still cannot cross this boundary. */
  function holdsPrivateKey(value) {
    var i, present;
    if (Array.isArray(value)) {
      for (i = 0; i < value.length; i++) {
        if (holdsPrivateKey(value[i])) return true;
      }
      return false;
    }
    if (!isPlainObject(value)) return false;
    present = keysOf(value);
    for (i = 0; i < present.length; i++) {
      if (inList(PRIVATE_KEYS, present[i])) return true;
      if (holdsPrivateKey(value[present[i]])) return true;
    }
    return false;
  }

  /* ---------------- nested public-shape validation -------------------------
     The projector prunes private editorial ancestors BEFORE it emits a public
     runtime. Once a public candidate reaches the browser, every remaining
     lemma, meaning and pattern is part of that candidate's claim. A malformed
     nested entity therefore rejects the candidate whole: silently dropping it
     would turn a failed load into a partial acceptance. */
  function validComplement(value) {
    if (!isPlainObject(value)) return false;
    if (!closedKeys(value, ["type", "required", "role"],
                    ["case", "preposition", "clauseKind",
                     "questionOverridePl"])) return false;
    if (typeof value.required !== "boolean") return false;
    if (!inList(ROLES, value.role)) return false;
    if (!inList(COMPLEMENT_TYPES, value.type)) return false;
    if (Object.prototype.hasOwnProperty.call(value, "questionOverridePl")) {
      if (!Array.isArray(value.questionOverridePl) ||
          !value.questionOverridePl.length) return false;
      if (!value.questionOverridePl.every(isNonEmptyString)) return false;
    }
    if (value.type === "case") {
      if (!Object.prototype.hasOwnProperty.call(CASES, value.case)) return false;
      if (!CASES[value.case].direct) return false;
      return !("preposition" in value) && !("clauseKind" in value);
    }
    if (value.type === "preposition-case") {
      if (!Object.prototype.hasOwnProperty.call(CASES, value.case)) return false;
      if (!CASES[value.case].prepositional) return false;
      if (!isNonEmptyString(value.preposition)) return false;
      return !("clauseKind" in value);
    }
    if (value.type === "infinitive") {
      return !("case" in value) && !("preposition" in value) &&
        !("clauseKind" in value);
    }
    /* clause */
    if (!inList(CLAUSE_KINDS, value.clauseKind)) return false;
    return !("case" in value) && !("preposition" in value);
  }

  function validPattern(value) {
    if (!isPlainObject(value)) return false;
    if (!closedKeys(
        value,
        ["id", "relationType", "complements", "cefr", "teachingStatus",
         "usage", "learnerExplanationEn", "activityEligibility"],
        ["aspectEquivalentPatternIds", "examples", "contentRefs",
         "errorNotes"])) return false;
    if (!isNonEmptyString(value.id)) return false;
    if (!inList(RELATION_TYPES, value.relationType)) return false;
    if (!inList(TEACHING_STATUSES, value.teachingStatus)) return false;
    if (!isNonEmptyString(value.learnerExplanationEn)) return false;
    if (!Array.isArray(value.complements) || !value.complements.length) return false;
    if (!value.complements.every(validComplement)) return false;
    if (!isPlainObject(value.cefr)) return false;
    if (!closedKeys(value.cefr, ["recognition"], ["production"])) return false;
    if (!inList(CEFR_LEVELS, value.cefr.recognition)) return false;
    if ("production" in value.cefr && !inList(CEFR_LEVELS, value.cefr.production)) {
      return false;
    }
    if (!isPlainObject(value.usage)) return false;
    if (!closedKeys(value.usage, ["priority", "register"], ["note"])) return false;
    if (!inList(USAGE_PRIORITIES, value.usage.priority)) return false;
    if (!inList(REGISTERS, value.usage.register)) return false;
    if ("note" in value.usage && !isNonEmptyString(value.usage.note)) return false;
    if (!Array.isArray(value.activityEligibility)) return false;
    if (!value.activityEligibility.every(function (activity) {
      return inList(ACTIVITY_KEYS, activity);
    })) return false;
    if ("examples" in value) {
      if (!Array.isArray(value.examples)) return false;
      if (!value.examples.every(function (example) {
        return isPlainObject(example) &&
          closedKeys(example, ["id", "pl", "en", "audioEligible"], []) &&
          isNonEmptyString(example.id) && isNonEmptyString(example.pl) &&
          isNonEmptyString(example.en) &&
          typeof example.audioEligible === "boolean";
      })) return false;
    }
    if ("contentRefs" in value) {
      if (!Array.isArray(value.contentRefs)) return false;
      if (!value.contentRefs.every(function (ref) {
        return isPlainObject(ref) &&
          closedKeys(ref, ["kind", "id", "purpose"], []) &&
          inList(CONTENT_KINDS, ref.kind) && isNonEmptyString(ref.id) &&
          inList(CONTENT_PURPOSES, ref.purpose);
      })) return false;
    }
    if ("errorNotes" in value) {
      if (!Array.isArray(value.errorNotes)) return false;
      if (!value.errorNotes.every(function (note) {
        return isPlainObject(note) &&
          closedKeys(note, ["kind", "incorrectForm", "guidanceEn"], []) &&
          isNonEmptyString(note.incorrectForm) &&
          isNonEmptyString(note.guidanceEn);
      })) return false;
    }
    if ("aspectEquivalentPatternIds" in value) {
      if (!Array.isArray(value.aspectEquivalentPatternIds) ||
          !value.aspectEquivalentPatternIds.every(isNonEmptyString)) return false;
    }
    return true;
  }

  function validMeaningShell(value) {
    return isPlainObject(value) &&
      closedKeys(value, ["id", "glossesEn", "patterns"], []) &&
      isNonEmptyString(value.id) && Array.isArray(value.glossesEn) &&
      value.glossesEn.length > 0 && value.glossesEn.every(isNonEmptyString) &&
      Array.isArray(value.patterns);
  }

  function validLemmaShell(value) {
    return isPlainObject(value) &&
      closedKeys(value, ["id", "canonicalLemma", "reflexive", "aspect",
                         "meanings"],
                 ["displayLemma", "aspectPartnerIds"]) &&
      isNonEmptyString(value.id) && isNonEmptyString(value.canonicalLemma) &&
      typeof value.reflexive === "boolean" &&
      isNonEmptyString(value.aspect) && Array.isArray(value.meanings) &&
      (!("displayLemma" in value) || isNonEmptyString(value.displayLemma)) &&
      (!("aspectPartnerIds" in value) ||
        (Array.isArray(value.aspectPartnerIds) &&
         value.aspectPartnerIds.every(isNonEmptyString)));
  }

  /* ---------------- derivation ---------------- */
  function questionsFor(complement) {
    var meta = CASES[complement.case], base;
    if (Array.isArray(complement.questionOverridePl) &&
        complement.questionOverridePl.length) {
      base = complement.questionOverridePl.slice();
      if (complement.type === "preposition-case") {
        return base.map(function (question) {
          return complement.preposition + " " + question;
        });
      }
      return base;
    }
    if (!meta) return [];
    if (complement.type === "preposition-case") {
      return meta.questions.map(function (question) {
        return complement.preposition + " " + question;
      });
    }
    return meta.questions.slice();
  }

  /* One chip type everywhere: the question(s), then the full case name, with
     the preposition bonded inside the same chip because a preposition is not a
     separate slot. Non-case complements use the same shape so the reading
     order never changes. Parts carry their own language, because "kogo?
     czego?" is Polish and "Genitive" is not. */
  function chipFor(complement, relationType) {
    var meta = CASES[complement.case], questions, parts, caseName;
    if (complement.type === "infinitive") {
      parts = [
        { text: "+ ", lang: null },
        { text: "bezokolicznik", lang: "pl" },
        { text: " · Infinitive", lang: null }
      ];
      return {
        bucket: NO_CASE_BUCKET, parts: parts, caseName: "Infinitive",
        question: "bezokolicznik", role: roleFor(complement, relationType),
        text: "+ bezokolicznik · Infinitive"
      };
    }
    if (complement.type === "clause") {
      questions = CLAUSE_TOKENS[complement.clauseKind];
      parts = [
        { text: "+ ", lang: null },
        { text: questions, lang: "pl" },
        { text: " · Clause", lang: null }
      ];
      return {
        bucket: NO_CASE_BUCKET, parts: parts, caseName: "Clause",
        question: questions, role: roleFor(complement, relationType),
        text: "+ " + questions + " · Clause"
      };
    }
    questions = questionsFor(complement).join(" ");
    caseName = meta ? meta.en : "";
    parts = [];
    if (questions) parts.push({ text: questions, lang: "pl" });
    /* Vocative has no question to fabricate, so it names the case and says
       what it is for instead. */
    if (!questions && meta && meta.address) {
      parts.push({ text: "direct address", lang: null });
    }
    parts.push({ text: (parts.length ? " · " : "") + caseName, lang: null });
    return {
      bucket: complement.case, parts: parts, caseName: caseName,
      question: questions, role: roleFor(complement, relationType),
      text: parts.map(function (part) { return part.text; }).join("")
    };
  }

  function roleFor(complement, relationType) {
    if (relationType === "subject-experiencer" && complement.role === "subject") {
      return SUBJECT_EXPERIENCER_SUBJECT;
    }
    return ROLE_PHRASES[complement.role] || "";
  }

  /* The headline is generated from structure, never authored per pattern, so
     it cannot drift from the data it summarises. */
  function headlineFor(displayLemma, pattern) {
    var parts = [{ text: displayLemma, lang: "pl" }];
    pattern.complements.forEach(function (complement) {
      var questions, animate, token;
      if (complement.type === "infinitive") {
        parts.push({ text: "+", lang: null });
        parts.push({ text: "bezokolicznik", lang: "pl" });
        return;
      }
      if (complement.type === "clause") {
        parts.push({ text: "+", lang: null });
        parts.push({ text: CLAUSE_TOKENS[complement.clauseKind], lang: "pl" });
        return;
      }
      questions = questionsFor(complement);
      if (!questions.length) {
        parts.push({ text: CASES[complement.case].en, lang: null });
        return;
      }
      animate = inList(ANIMATE_ROLES, complement.role);
      token = questions.length > 1 && !animate ? questions[1] : questions[0];
      parts.push({ text: token, lang: "pl" });
    });
    return parts;
  }

  /* ---------------- the two cross-link directions ----------------
     Both are pure lookups over the static table above: deterministic, closed,
     and dependent on no runtime state whatsoever. An unknown case id or an
     unknown topic id resolves to null - never to a guess, and never to a
     "nearest" case. */

  /* Verb Patterns -> Grammar. One route from a pattern to the lesson that would
     fix the actual gap: knowing that a verb takes the Genitive does not help a
     learner who cannot form it. */
  function caseLessonFor(caseId) {
    if (!isNonEmptyString(caseId)) return null;
    if (!Object.prototype.hasOwnProperty.call(CASE_LESSON_TOPICS, caseId)) return null;
    return {
      caseId: caseId,
      topicId: CASE_LESSON_TOPICS[caseId],
      label: "Learn the " + CASES[caseId].en,
      srLabel: "Learn the " + CASES[caseId].en + " (" + CASES[caseId].pl + ")",
      polishName: CASES[caseId].pl
    };
  }

  /* Grammar -> Verb Patterns. One continuation from a case lesson into the
     case-filtered VIEW of the one canonical index - a filter, never a second
     container, so nothing is duplicated and no lemma is shredded across cases. */
  function caseFilterFor(topicId) {
    var found = null, meta;
    if (!isNonEmptyString(topicId)) return null;
    CASE_ORDER.forEach(function (caseId) {
      if (CASE_LESSON_TOPICS[caseId] === topicId) found = caseId;
    });
    if (!found) return null;
    meta = CASES[found];
    /* A case that can occur as NEITHER a direct nor a prepositional complement
       cannot appear in any pattern the runtime contract admits - the editorial
       validator refuses one - so there is no filter for it to open and no view
       for it to describe. Vocative is that case today. Offering a deep link to a
       state that cannot exist would be a promise the corpus can never keep, so
       the continuation simply does not exist on that lesson. The lesson itself,
       and this table, are untouched: if a future schema admits a genuine
       Vocative complement, this answers differently with no edit here. */
    if (!meta.direct && !meta.prepositional) return null;
    /* The wording deliberately does not say a verb TAKES the case. A case
       complement is not always a governed object - a Nominative subject and a
       constructional frame are neither - and what this opens is a filtered view
       of patterns, not a list of verbs that govern the case. The label promises
       exactly what the destination shows, and nothing more. */
    return {
      caseId: found,
      filter: found,
      label: "Verb patterns with the " + meta.en,
      srLabel: "Verb patterns with the " + meta.en + " (" + meta.pl + ")",
      polishName: meta.pl
    };
  }

  /* One link per DISTINCT nominal case in the frame, in authored complement
     order. A single-case pattern therefore gets exactly one, which is the shape
     the architecture describes. A two-case frame gets both, deliberately: the
     design reports do not rank the complements of a multi-case pattern, and
     picking one of them here would invent exactly the linguistic hierarchy the
     design refuses. Offering both ranks nothing.

     An infinitive or clause complement contributes NOTHING - there is no case
     lesson for "+ bezokolicznik", and fabricating one would teach a case that
     the pattern does not take. A pattern with no nominal case gets no link. */
  function caseLinksFor(pattern) {
    var out = [], seen = {};
    pattern.complements.forEach(function (complement) {
      var link;
      if (complement.type !== "case" && complement.type !== "preposition-case") return;
      if (Object.prototype.hasOwnProperty.call(seen, complement.case)) return;
      seen[complement.case] = true;
      link = caseLessonFor(complement.case);
      if (link) out.push(link);
    });
    return out;
  }

  function badgeFor(pattern) {
    var level = LEVEL_LABELS[pattern.cefr.recognition] || "";
    return {
      text: level,
      /* Only the recognition level is ever shown. A production gap is real, so
         it is never collapsed into this badge: it shows up as the absence of a
         production activity, and the accessible name says what the badge is. */
      srText: level ? "Recognise from " + level : ""
    };
  }

  function isRecognitionOnly(pattern) {
    return !!pattern && pattern.teachingStatus === "recognition-only";
  }

  /* activityEligibility is an allowlist and defaults to closed, exactly as
     PP_USAGE.eligibleFor already does for cards: an unknown or misspelled
     activity name fails CLOSED. */
  function eligibleFor(pattern, activity) {
    if (!isPlainObject(pattern)) return false;
    if (!inList(ACTIVITY_KEYS, activity)) return false;
    if (!Array.isArray(pattern.activityEligibility)) return false;
    if (isRecognitionOnly(pattern) &&
        (activity === "grammar-build" || activity === "type-it")) return false;
    return pattern.activityEligibility.indexOf(activity) !== -1;
  }

  /* ---------------- grammar-choose mechanics adapter ----------------
     A PURE mapping from one exercise record to the drill shape the app's
     existing Grammar `choose` engine already consumes. It exists so a
     pattern-practice item can reuse that engine - its question progression,
     option rendering, selected/correct/incorrect states, feedback region, Next
     action, keyboard behaviour and focus contract - instead of growing a second
     activity engine beside it.

     WHAT THIS ADAPTER DECIDES: whether a record is structurally usable as a
     choose item, and what its mechanics are.

     WHAT IT DOES NOT DECIDE, and must never be read as deciding:
       - whether the owning pattern may be practised at all. It never consults
         a pattern, an eligibility allowlist, a teaching status, a CEFR level, a
         content reference or whether the surface is visible. Eligibility is a
         separate, explicit allowlist (eligibleFor above) that defaults closed,
         and an item existing is not an entry in it;
       - whether the record was authored, reviewed, or authorized to reach a
         learner. Those live outside the browser entirely.
     A record reaching this function proves only that something handed it one.

     Fail-closed everywhere: every rejection returns null, and null starts
     nothing. There is no partial item and no repaired item. */
  var CHOOSE_ACTIVITY = "grammar-choose";
  /* The learner-facing instruction. The task is choosing a STRUCTURE, so the
     wording says so rather than borrowing the form-selection wording the
     authored case drills use. */
  var CHOOSE_INSTRUCTION = "Choose the pattern";
  /* `vp-` is the Priority 7 identity space: lemma, meaning, pattern, example and
     the reserved future exercise family. A mechanics adapter has no business
     handling one, so an identifier in that space is refused outright - which is
     what stops a prototype from consuming, minting or appearing to reserve an
     identity that belongs to the release architecture. */
  var RESERVED_ID_PREFIX = "vp-";

  function usableId(value) {
    return isFilledString(value) && value.indexOf(RESERVED_ID_PREFIX) !== 0;
  }

  /* ---------------- learner-facing text, with its language ----------------
     A text field is either a plain STRING - one language for the whole of it -
     or an array of {text, lang} FRAGMENTS.

     Fragments exist because a structural label genuinely mixes languages:
     `kogo? co? · Accusative` is Polish, a separator, then English. In an English
     document, marking the whole of it lang="pl" makes a screen reader read
     "Accusative" as Polish; leaving it unmarked makes it read the Polish half as
     English. Neither is acceptable, and only fragments describe it correctly.

     The RECORD carries the languages, because the record is where they are
     known. Deriving them here - splitting on a separator, assuming a prompt is
     Polish - would be this file inventing a linguistic claim, which is the one
     thing it must never do. A field with no language metadata simply has none,
     and is left to the document's own language. */
  function validTextFragment(fragment) {
    return isPlainObject(fragment) &&
      closedKeys(fragment, ["text"], ["lang"]) &&
      isNonEmptyString(fragment.text) &&
      (!hasOwn(fragment, "lang") || isFilledString(fragment.lang));
  }
  function validTextValue(value) {
    if (Array.isArray(value)) {
      if (!value.length || !value.every(validTextFragment)) return false;
      /* Fragments that add up to nothing visible are as malformed as a blank
         string, and fail the same way. */
      return isFilledString(value.map(function (fragment) {
        return fragment.text;
      }).join(""));
    }
    return isFilledString(value);
  }
  /* The copy is built from OWN properties only, so whatever the renderer
     receives is an ordinary object with no prototype behaviour left in it. */
  function copyTextValue(value) {
    if (!Array.isArray(value)) return value;
    return value.map(function (fragment) {
      var out = { text: fragment.text };
      if (hasOwn(fragment, "lang") && isFilledString(fragment.lang)) {
        out.lang = fragment.lang;
      }
      return out;
    });
  }

  /* An option carries an explicit stable `value` alongside the words on the
     button. That separation is the point: two options may legitimately read the
     same and still be different answers, so scoring must never depend on
     displayed text or on the position an option happens to occupy. */
  function validChooseOption(option) {
    return isPlainObject(option) &&
      closedKeys(option, ["value", "label"], []) &&
      isFilledString(option.value) && validTextValue(option.label);
  }

  function grammarChooseDrill(item) {
    var options = [], seen = emptyDict(), answered = 0, i, option;
    /* isPlainObject is deliberately NOT tightened to "prototype is exactly
       Object.prototype". Every required key must be an OWN property - closedKeys
       reads through hasOwnProperty - every value is separately type-checked, and
       nothing here reads an inherited member, so an object carrying a prototype
       behaves identically to the JSON object the harness actually supplies. An
       inherited "required" key fails closed, and a test proves it. */
    if (!isPlainObject(item)) return null;
    /* An editorial or envelope record is not an exercise item. A private field
       at any depth refuses the whole record rather than being skipped. */
    if (holdsPrivateKey(item)) return null;
    if (!closedKeys(item,
        ["exerciseId", "patternRef", "activityType", "order", "prompt",
         "options", "answerValue", "feedbackStructure", "feedbackExplanation"],
        ["promptEn", "cue"])) return null;
    /* One activity family, matched positively. An unknown or misspelled
       activityType is refused HERE rather than being handed on: "anything that
       is not choose behaves as build" is not a safe extension contract, and an
       adapter is exactly where that has to stop. */
    if (item.activityType !== CHOOSE_ACTIVITY) return null;
    if (!usableId(item.exerciseId) || !usableId(item.patternRef)) return null;
    if (!isPositiveInteger(item.order)) return null;
    if (!validTextValue(item.prompt)) return null;
    /* An optional field that is PRESENT is held to the same standard as a
       required one: a blank-looking optional string is a malformed record, not
       an absent field, and guessing which was meant is not this file's job. */
    if (hasOwn(item, "promptEn") && !validTextValue(item.promptEn)) return null;
    if (hasOwn(item, "cue") && !validTextValue(item.cue)) return null;
    if (!validTextValue(item.feedbackStructure)) return null;
    if (!validTextValue(item.feedbackExplanation)) return null;
    if (!Array.isArray(item.options) || item.options.length < 2) return null;
    if (!isFilledString(item.answerValue)) return null;
    for (i = 0; i < item.options.length; i++) {
      option = item.options[i];
      if (!validChooseOption(option)) return null;
      /* Two options that share an identity cannot be told apart by a score, so
         the set is refused rather than silently collapsed. */
      if (seenBefore(seen, option.value)) return null;
      if (option.value === item.answerValue) answered++;
      options.push({ value: option.value, label: copyTextValue(option.label) });
    }
    /* Exactly one option must be the answer: none means the item is unscorable,
       and the engine would present a question with no way to finish it. */
    if (answered !== 1) return null;
    return {
      /* the existing engine's own drill vocabulary, so nothing is translated
         twice and the engine needs no knowledge of where this came from */
      type: "choose",
      /* every string below arrived as DATA, so the renderer must build it as
         text and never parse it as markup */
      textOnly: true,
      /* The first choice is the attempt. These options are STRUCTURES, not
         inflected forms, and the set is small: letting a learner eliminate the
         remaining ones would hand over the answer without a second decision
         being made, and would score identically either way. So a miss ends the
         presentation, shows which option was right and why, and moves on - the
         existing round mechanics still bring the item back. Every authored
         Grammar drill omits this property and keeps the retry mechanic. */
      revealOnIncorrect: true,
      instruction: CHOOSE_INSTRUCTION,
      prompt: copyTextValue(item.prompt),
      promptEn: hasOwn(item, "promptEn") ? copyTextValue(item.promptEn) : "",
      /* the optional short learner-facing cue shown beside the instruction,
         reusing the engine's existing slot rather than adding a second one */
      _case: hasOwn(item, "cue") ? copyTextValue(item.cue) : "",
      options: options,
      answer: item.answerValue,
      full: copyTextValue(item.feedbackStructure),
      fullEn: "",
      explain: copyTextValue(item.feedbackExplanation),
      exerciseId: item.exerciseId,
      patternRef: item.patternRef,
      order: item.order
    };
  }

  /* Whole-set fail-closed, matching the runtime consumer's atomic rule. A
     SCORED round cannot quietly run four of five items and report a total
     nobody wrote, so one malformed item refuses the whole candidate set. */
  function grammarChooseDrills(items) {
    var out = [], ids = emptyDict(), orders = emptyDict(), i, drill;
    if (!Array.isArray(items) || !items.length) return null;
    for (i = 0; i < items.length; i++) {
      drill = grammarChooseDrill(items[i]);
      if (!drill) return null;
      if (seenBefore(ids, drill.exerciseId)) return null;
      if (seenBefore(orders, String(drill.order))) return null;
      out.push(drill);
    }
    /* Explicit authored ordering, so the sequence never depends on the order the
       records happened to arrive in. */
    out.sort(function (a, b) { return a.order - b.order; });
    return out;
  }

  /* Simplest frame first: fewer slots, then earlier recognition level, then
     teaching priority. `rozmawiac z` before `rozmawiac z ... o ...` is how the
     frames are actually acquired, and no sibling is ever hidden. */
  function patternOrder(a, b) {
    if (a.complements.length !== b.complements.length) {
      return a.complements.length - b.complements.length;
    }
    var levelA = CEFR_LEVELS.indexOf(a.cefr.recognition);
    var levelB = CEFR_LEVELS.indexOf(b.cefr.recognition);
    if (levelA !== levelB) return levelA - levelB;
    var priorityA = USAGE_PRIORITIES.indexOf(a.usage.priority);
    var priorityB = USAGE_PRIORITIES.indexOf(b.usage.priority);
    if (priorityA !== priorityB) return priorityA - priorityB;
    return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
  }

  function glossText(glosses) { return glosses.join(" / "); }

  /* ---------------- accept + build ---------------- */
  function build(runtime) {
    var lemmas = [], cards = {}, invalid = false;
    runtime.lemmas.forEach(function (lemma) {
      var meanings = [], display;
      if (!validLemmaShell(lemma)) { invalid = true; return; }
      lemma.meanings.forEach(function (meaning) {
        var patterns;
        if (!validMeaningShell(meaning)) { invalid = true; return; }
        patterns = meaning.patterns.filter(function (pattern) {
          var valid = validPattern(pattern);
          if (!valid) invalid = true;
          return valid;
        }).map(copyPublicValue).sort(patternOrder);
        if (!patterns.length) { invalid = true; return; }
        meanings.push({ glosses: meaning.glossesEn.slice(), patterns: patterns });
      });
      if (!meanings.length) { invalid = true; return; }
      display = isNonEmptyString(lemma.displayLemma) ? lemma.displayLemma
        : lemma.canonicalLemma;
      lemmas.push({
        display: display,
        sortKey: fold(display),
        letter: fold(display).charAt(0).toUpperCase(),
        aspect: lemma.aspect,
        reflexive: lemma.reflexive,
        meanings: meanings
      });
    });
    if (invalid || !lemmas.length) return null;
    lemmas.sort(function (a, b) {
      if (a.sortKey !== b.sortKey) return a.sortKey < b.sortKey ? -1 : 1;
      return a.display < b.display ? -1 : (a.display > b.display ? 1 : 0);
    });
    lemmas.forEach(function (lemma, key) {
      lemma.key = key;
      lemma.patternCount = 0;
      lemma.meanings.forEach(function (meaning, meaningIndex) {
        lemma.patternCount += meaning.patterns.length;
        meaning.patterns.forEach(function (pattern) {
          /* Only one relation may put a pattern pointer on a vocabulary card:
             kind "card" with purpose "support". A contrast reference asserts
             that the card DIFFERS, so printing the pattern there would assert
             the opposite of what the reference says - it is invisible to this
             index in both directions. */
          (pattern.contentRefs || []).forEach(function (ref) {
            if (ref.kind !== "card" || ref.purpose !== "support") return;
            /* hasOwnProperty, not truthiness: a card id that happens to spell an
               Object.prototype member ("constructor", "toString") would
               otherwise find an inherited value here and be treated as an
               existing claim list. The index must answer for the ids it was
               given and for no others. */
            if (!Object.prototype.hasOwnProperty.call(cards, ref.id)) cards[ref.id] = [];
            cards[ref.id].push({ lemmaKey: key, meaningIndex: meaningIndex,
              pattern: pattern });
          });
        });
      });
    });
    return { lemmas: lemmas, cards: cards };
  }

  /* The seven-step envelope check, in order. Validation and view construction
     complete against a candidate before either STATE or `available` changes.
     A rejected candidate therefore cannot clear, corrupt or partly replace the
     last valid in-memory value. With no prior value, rejection simply leaves the
     neutral unavailable state in place. */
  function accept(runtime) {
    var revision, candidate;
    if (!isPlainObject(runtime)) return false;                         /* 1 */
    if (!closedKeys(runtime, ENVELOPE_KEYS, [])) return false;         /* 2 */
    if (runtime.formatVersion !== FORMAT_VERSION) return false;        /* 3 */
    revision = runtime.patternDataRevision;
    if (!isPositiveInteger(revision)) return false;                    /* 4 */
    if (!Array.isArray(runtime.lemmas) || !runtime.lemmas.length) return false; /* 5 */
    if (holdsPrivateKey(runtime)) return false;                        /* 7 */
    candidate = build(runtime);                                        /* 6 */
    if (!candidate) return false;
    STATE = candidate;
    api.available = true;
    return true;
  }

  /* A deliberately small transport boundary. `request` is dependency-injected
     so the function can be rehearsed without a network and so this helper never
     reaches for a global fetch on its own. Real Response.json() is asynchronous;
     a non-thenable body is refused rather than treated as a special test mode.

     Every branch returns a Promise that settles to Boolean success, with no
     retry and no learner-facing error. The loader is designed for one startup
     invocation. Overlapping calls are deliberately not coordinated: they are
     last-to-settle. Any future refresh/retry feature must add an in-flight
     generation guard before it can issue more than one load.
     The accepted state is changed only inside accept(), after complete public-
     shape validation and candidate construction. */
  function loadRuntimeDocument(request, url) {
    function rejected() { return false; }
    var responsePromise;
    if (typeof request !== "function" || !isNonEmptyString(url)) {
      return Promise.resolve(false);
    }
    try {
      responsePromise = request(url, { cache: "no-store" });
      if (!responsePromise || typeof responsePromise.then !== "function") {
        return Promise.resolve(false);
      }
      return Promise.resolve(responsePromise).then(function (response) {
        var bodyPromise;
        if (!response || response.ok !== true ||
            typeof response.json !== "function") return false;
        try {
          bodyPromise = response.json();
          if (!bodyPromise || typeof bodyPromise.then !== "function") return false;
          return bodyPromise.then(function (document) {
            return accept(document);
          }, rejected);
        } catch (error) {
          return false;
        }
      }, rejected).then(function (accepted) {
        return accepted === true;
      }, rejected);
    } catch (error) {
      return Promise.resolve(false);
    }
  }

  /* ---------------- views ---------------- */
  function summary() {
    if (!STATE) return { lemmas: 0, patterns: 0 };
    return {
      lemmas: STATE.lemmas.length,
      patterns: STATE.lemmas.reduce(function (total, lemma) {
        return total + lemma.patternCount;
      }, 0)
    };
  }

  function countLabel() {
    var counts = summary();
    return counts.lemmas + (counts.lemmas === 1 ? " verb" : " verbs") +
      " · " + counts.patterns +
      (counts.patterns === 1 ? " pattern" : " patterns");
  }

  function bucketsOf(pattern) {
    var out = [];
    pattern.complements.forEach(function (complement) {
      var bucket = complement.type === "case" ||
        complement.type === "preposition-case" ? complement.case
        : NO_CASE_BUCKET;
      if (out.indexOf(bucket) === -1) out.push(bucket);
    });
    return out;
  }

  /* Filter options are derived from what the document actually contains, in
     canonical case order, so a corpus that gains a case gains an option rather
     than a container. */
  function filters() {
    var present = {}, options, hasNoCase = false;
    if (!STATE) return [];
    STATE.lemmas.forEach(function (lemma) {
      lemma.meanings.forEach(function (meaning) {
        meaning.patterns.forEach(function (pattern) {
          bucketsOf(pattern).forEach(function (bucket) {
            if (bucket === NO_CASE_BUCKET) hasNoCase = true;
            else present[bucket] = true;
          });
        });
      });
    });
    options = [{ id: "all", label: "All verbs", srLabel: "All verbs" }];
    CASE_ORDER.forEach(function (caseId) {
      if (!present[caseId]) return;
      options.push({
        id: caseId,
        label: CASES[caseId].en,
        srLabel: CASES[caseId].en + " (" + CASES[caseId].pl + ")",
        polishName: CASES[caseId].pl
      });
    });
    if (hasNoCase) {
      options.push({ id: NO_CASE_BUCKET, label: NO_CASE_LABEL,
        srLabel: NO_CASE_LABEL });
    }
    return options;
  }

  function filterLabel(filterId) {
    var found = null;
    filters().forEach(function (option) {
      if (option.id === filterId) found = option;
    });
    if (!found) return "";
    if (found.polishName) return found.polishName + " (" + found.label + ")";
    return found.label;
  }

  /* The canonical index: one row per lemma, always, whatever the filter. A row
     here carries no chip, because a chip would assert one answer for a lemma
     that may have several. */
  function index() {
    if (!STATE) return [];
    return STATE.lemmas.map(function (lemma) {
      return {
        key: lemma.key,
        lemma: lemma.display,
        letter: lemma.letter,
        glosses: lemma.meanings.map(function (meaning) {
          return glossText(meaning.glosses);
        }).join(" · "),
        meaningCount: lemma.meanings.length,
        patternCount: lemma.patternCount
      };
    });
  }

  /* A filtered row is a POINTER WITH A SUMMARY, never a second copy: it names
     the lemma, the meaning that matched, and the pattern's complete chip set
     with the matching chip marked. Showing only the matching chip would teach
     half a frame, so every chip of a multi-complement pattern is present. */
  function rows(filterId) {
    var out = [];
    if (!STATE) return out;
    if (!filterId || filterId === "all") {
      return index().map(function (row) {
        row.chips = [];
        row.isSummary = false;
        return row;
      });
    }
    STATE.lemmas.forEach(function (lemma) {
      lemma.meanings.forEach(function (meaning, meaningIndex) {
        meaning.patterns.forEach(function (pattern, patternIndex) {
          var buckets = bucketsOf(pattern);
          if (buckets.indexOf(filterId) === -1) return;
          out.push({
            key: lemma.key,
            lemma: lemma.display,
            letter: lemma.letter,
            glosses: glossText(meaning.glosses),
            meaningIndex: meaningIndex,
            /* The loader boundary deliberately strips runtime IDs. These are
               stable positions in its deterministic sorted public lemma view,
               used only for rendered navigation restoration. */
            patternIndex: patternIndex,
            isSummary: true,
            recognitionOnly: isRecognitionOnly(pattern),
            chips: pattern.complements.map(function (complement) {
              var chip = chipFor(complement, pattern.relationType);
              chip.match = chip.bucket === filterId;
              return chip;
            })
          });
        });
      });
    });
    return out;
  }

  function filterCounts(filterId) {
    /* Unfiltered, this is the corpus: every lemma and every pattern, not the
       number of rows on screen - the canonical index shows one row per lemma. */
    if (!filterId || filterId === "all") {
      var totals = summary();
      return { verbs: totals.lemmas, patterns: totals.patterns };
    }
    var matched = rows(filterId), verbs = {}, count = 0;
    matched.forEach(function (row) {
      if (!verbs[row.key]) { verbs[row.key] = true; count++; }
    });
    return { verbs: count, patterns: matched.length };
  }

  /* The one canonical owner. Only this view carries an explanation, an example
     or a role line; the index and every filtered row are summaries that point
     here. */
  function lemma(key) {
    var record = STATE && STATE.lemmas[key];
    if (!record) return null;
    return {
      key: record.key,
      lemma: record.display,
      aspect: record.aspect,
      multiMeaning: record.meanings.length > 1,
      leadIn: record.meanings.length > 1
        ? record.display + " has " + record.meanings.length +
          " meanings, and they behave differently."
        : "",
      leadInParts: record.meanings.length > 1
        ? [{ text: record.display, lang: "pl" },
           { text: " has " + record.meanings.length +
             " meanings, and they behave differently." }]
        : [],
      meanings: record.meanings.map(function (meaning) {
        return {
          glosses: glossText(meaning.glosses),
          patterns: meaning.patterns.map(function (pattern) {
            return {
              headline: headlineFor(record.display, pattern),
              badge: badgeFor(pattern),
              recognitionOnly: isRecognitionOnly(pattern),
              chips: pattern.complements.map(function (complement) {
                return chipFor(complement, pattern.relationType);
              }),
              explanation: pattern.learnerExplanationEn,
              example: pattern.examples && pattern.examples.length
                ? { pl: pattern.examples[0].pl, en: pattern.examples[0].en,
                    audioEligible: pattern.examples[0].audioEligible }
                : null,
              /* Pointers back to the existing case lessons. Grammar keeps the
                 teaching; this view carries only the way back to it. */
              caseLinks: caseLinksFor(pattern),
              eligibility: pattern.activityEligibility.slice()
            };
          })
        };
      })
    };
  }

  /* Two gates, three outcomes, fail closed. Reference ambiguity and MEANING
     ambiguity are different failure modes, and only the first is visible in
     the reference counts: a card claimed by exactly one pattern of a lemma
     that has two meanings would otherwise teach half the lemma confidently.
     The eligibility rule is `kind === "card" && purpose === "support"` and
     nothing else, applied where the index is BUILT (see build()), so no other
     relation can reach this function to be re-judged. A `contrast` reference
     asserts that the card differs from the pattern, so it is invisible here in
     both directions: it adds no claim, it removes none, and it produces no
     doorway of its own.

     Nothing about the card itself is consulted - not its Polish, not its
     English, not its topic, not how closely its text resembles a lemma. Only an
     explicit runtime reference to this exact card id can create a pointer. */
  function cardSupport(cardId) {
    var claims, owner;
    if (!STATE) return { state: "none" };
    if (!isNonEmptyString(cardId)) return { state: "none" };
    /* Own properties only: an id such as "constructor" must find nothing rather
       than an inherited member of Object.prototype. */
    if (!Object.prototype.hasOwnProperty.call(STATE.cards, cardId)) {
      return { state: "none" };
    }
    claims = STATE.cards[cardId];
    if (!Array.isArray(claims) || !claims.length) return { state: "none" };
    if (claims.length > 1) {
      /* Gate 1 - reference ambiguity. No pattern is selected either way. What
         still has to be decided is WHERE the doorway may lead, and that is not
         one question but two:

           every claim owned by the SAME lemma - the claims disagree about which
             meaning or pattern applies, but they agree about the verb. Opening
             that lemma's entry asserts nothing the references do not already
             agree on, and the entry is where the disambiguation belongs.

           claims owned by DIFFERENT lemmas - nothing about "this verb" is
             established at all. Picking one would be a tie-break, and every
             available tie-break (claim order, lemma order, the card's own text)
             is arbitrary: the runtime order of two references carries no
             meaning, so a destination derived from it would be a claim invented
             by the sort. The doorway therefore selects NO lemma and opens the
             canonical index, which is the one honest destination. */
      var owners = {}, distinct = 0;
      claims.forEach(function (claim) {
        if (Object.prototype.hasOwnProperty.call(owners, claim.lemmaKey)) return;
        owners[claim.lemmaKey] = true;
        distinct++;
      });
      if (distinct > 1) return { state: "doorway", scope: "index", lemmaKey: null };
      return { state: "doorway", scope: "lemma", lemmaKey: claims[0].lemmaKey };
    }
    owner = STATE.lemmas[claims[0].lemmaKey];
    /* Gate 2 - owning-lemma ambiguity. One claim, so the verb is established;
       only which of its meanings or patterns applies is not. */
    if (owner.meanings.length > 1 || owner.patternCount > 1) {
      return { state: "doorway", scope: "lemma", lemmaKey: owner.key };
    }
    return {
      state: "chip",
      scope: "lemma",
      lemmaKey: owner.key,
      chips: claims[0].pattern.complements.map(function (complement) {
        return chipFor(complement, claims[0].pattern.relationType);
      })
    };
  }

  /* One deliberately small, flat search string: display lemmas, case names in
     both languages, prepositions and diagnostic questions - and nothing else.
     The topic object must never carry a runtime entity or an identifier,
     because the home search walks every string it can reach. */
  function searchText() {
    var parts = [];
    if (!STATE) return "";
    STATE.lemmas.forEach(function (record) {
      parts.push(record.display);
      record.meanings.forEach(function (meaning) {
        meaning.patterns.forEach(function (pattern) {
          pattern.complements.forEach(function (complement) {
            var meta = CASES[complement.case];
            if (meta) parts.push(meta.en, meta.pl);
            if (complement.preposition) parts.push(complement.preposition);
            questionsFor(complement).forEach(function (question) {
              parts.push(question);
            });
            if (complement.type === "infinitive") parts.push("bezokolicznik");
            if (complement.type === "clause") {
              parts.push(CLAUSE_TOKENS[complement.clauseKind]);
            }
          });
        });
      });
    });
    return parts.join(" ");
  }

  function reset() {
    STATE = null;
    api.available = false;
    return true;
  }

  var api = {
    /* DATA availability, and nothing else.

       false until a document of the expected public shape has been accepted;
       true once one has. The Verb Patterns level and its screen exist
       independently of this flag - the surface is ordinary information
       architecture, not something that appears only when there is data - so
       while this is false the existing surface opens normally and renders its
       neutral unavailable state. That is the intended passive behaviour, not an
       error state.

       This flag says nothing about release authorization, and must never be
       read as saying anything about it: it means "a value of the right shape
       has been accepted", which a hand-written value also satisfies. */
    available: false,
    FORMAT_VERSION: FORMAT_VERSION,
    ENVELOPE_KEYS: ENVELOPE_KEYS.slice(),
    CASE_ORDER: CASE_ORDER.slice(),
    NO_CASE_BUCKET: NO_CASE_BUCKET,
    NO_CASE_LABEL: NO_CASE_LABEL,
    ROLE_PHRASES: ROLE_PHRASES,
    /* The card back's two strings, so the renderer quotes them rather than
       authoring its own. */
    CARD_POINTER_KEY: CARD_POINTER_KEY,
    CARD_DOORWAY_LABEL: CARD_DOORWAY_LABEL,
    CARD_INDEX_DOORWAY_LABEL: CARD_INDEX_DOORWAY_LABEL,

    /* parsed public envelope acceptance, plus a dormant injected transport */
    acceptRuntimeDocument: accept,
    loadRuntimeDocument: loadRuntimeDocument,
    /* test-only injection; the same validation, the same views, and never
       referenced by index.html */
    __acceptForTest: accept,
    /* Direct proof that the redundant private-key sweep remains live. This
       test-only exposure answers only Boolean shape; it reveals no private data
       and is never referenced by the learner-facing application. */
    __holdsPrivateKeyForTest: holdsPrivateKey,
    reset: reset,

    caseMeta: function (caseId) {
      return Object.prototype.hasOwnProperty.call(CASES, caseId)
        ? CASES[caseId] : null;
    },
    /* The two cross-link directions. Both are static lookups: they answer the
       same way whether or not any runtime document has been accepted. */
    caseLessonFor: caseLessonFor,
    caseFilterFor: caseFilterFor,
    questionsFor: questionsFor,
    chipFor: chipFor,
    roleFor: roleFor,
    headlineFor: headlineFor,
    badgeFor: badgeFor,
    isRecognitionOnly: isRecognitionOnly,
    eligibleFor: eligibleFor,
    /* The mechanics adapter. It answers "is this record usable as a choose
       item, and what are its mechanics" - never "may this be practised", which
       is eligibleFor's question and defaults closed. */
    CHOOSE_ACTIVITY_TYPE: CHOOSE_ACTIVITY,
    CHOOSE_INSTRUCTION: CHOOSE_INSTRUCTION,
    grammarChooseDrill: grammarChooseDrill,
    grammarChooseDrills: grammarChooseDrills,
    hasIndex: function () { return !!(STATE && STATE.lemmas.length); },
    summary: summary,
    countLabel: countLabel,
    filters: filters,
    filterLabel: filterLabel,
    filterCounts: filterCounts,
    index: index,
    rows: rows,
    lemma: lemma,
    cardSupport: cardSupport,
    searchText: searchText
  };
  return api;
})();
