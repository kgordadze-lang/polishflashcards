// Deterministic tests for Priority 7 Phase 3B - the passive Verb Patterns
// reference surface, its loader boundary, and the topic-routing default-deny
// remediation the phase is gated on. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_priority7_patterns_ui.js
//
// What runs here is the shipping code: pp-verb-patterns.js is loaded as-is, and
// the renderers, the focus helpers and the routing dispatch are extracted from
// index.html and executed against a deterministic fake DOM.
//
// THE ONE THING TO UNDERSTAND ABOUT THIS SUITE:
//   the fixture it feeds the UI is wrapped, and the shipping loader REFUSES the
//   wrapper. The wrapper is opened here, in the harness, by a function that
//   asserts the non-release markers before it opens anything, and the unwrapped
//   projection is then handed to the loader's test-only injection entry point.
//   Production code performs none of those steps and has no path to this file.
//   test fixture != validated runtime shape != authorized release, and this
//   suite only ever touches the first two.
//
// Real rendered geometry, real screen readers, real key synthesis and real
// device text scaling remain human checks.

ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager;
  var cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++) {
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();
var INDEX = readFile(ROOT + 'index.html');
var LOADER_SRC = readFile(ROOT + 'pp-verb-patterns.js');
(0, eval)(LOADER_SRC);                                  // defines global PP_VERB_PATTERNS
var WRAPPED_FIXTURE = JSON.parse(readFile(ROOT + 'tests/fixtures/priority7/runtime-fixture.json'));
var RELEASE_REHEARSAL_FIXTURE = JSON.parse(
  readFile(ROOT + 'tests/fixtures/priority7/release-runtime-fixture.json'));

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }
function Immediate(state, value) { this.state = state; this.value = value; }
Immediate.resolve = function (value) {
  return value instanceof Immediate ? value : new Immediate('fulfilled', value);
};
Immediate.reject = function (value) { return new Immediate('rejected', value); };
Immediate.prototype.then = function (onFulfilled, onRejected) {
  var callback = this.state === 'fulfilled' ? onFulfilled : onRejected;
  if (typeof callback !== 'function') return this;
  try {
    var next = callback(this.value);
    return next instanceof Immediate ? next : Immediate.resolve(next);
  } catch (error) {
    return Immediate.reject(error);
  }
};
// osascript does not drain native Promise jobs. The shipping loader still calls
// Promise.resolve; this deterministic stand-in lets the DOM harness settle it.
Promise = Immediate;
function immediateValue(value) {
  if (!(value instanceof Immediate)) return value;
  if (value.state === 'rejected') throw value.value;
  return value.value;
}
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}
function squash(s) { return String(s).replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }
function stripComments(src) {
  return src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^\s*\/\/.*$/gm, '');
}
function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found');
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: duplicate ' + name);
  var open = src.indexOf('{', src.indexOf(')', start));
  var depth = 0, mode = 'code';
  for (var j = open; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { j++; continue; }
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, j + 1); }
  }
  throw new Error('extract: unbalanced ' + name);
}
function sliceBetween(src, from, to) {
  var start = src.indexOf(from);
  var end = src.indexOf(to, start + 1);
  if (start === -1 || end === -1) throw new Error('slice not found: ' + from);
  return src.slice(start, end);
}

// =========================================================================
// THE HARNESS. The only place a non-release wrapper is ever opened.
// It asserts first and reads second: if the wrapper or its
// releaseAuthorized:false is missing, the harness throws instead of quietly
// consuming a bare or authorized-looking value.
// =========================================================================
var NONRELEASE_MARKER = 'priority-7-runtime-projection-nonrelease-fixture';
function unwrapNonReleaseFixtureForTest(wrapped) {
  if (!wrapped || typeof wrapped !== 'object' || Array.isArray(wrapped)) {
    throw new Error('harness: the fixture is not an object');
  }
  if (wrapped.artifactStatus !== NONRELEASE_MARKER) {
    throw new Error('harness: the non-release marker is missing');
  }
  if (wrapped.releaseAuthorized !== false) {
    throw new Error('harness: releaseAuthorized must be exactly false');
  }
  if (!wrapped.runtimeProjection) {
    throw new Error('harness: the wrapper carries no projection');
  }
  return clone(wrapped.runtimeProjection);
}
function injectFixture() {
  return PP_VERB_PATTERNS.__acceptForTest(unwrapNonReleaseFixtureForTest(WRAPPED_FIXTURE));
}
function throws(fn) {
  try { fn(); return false; } catch (e) { return true; }
}

// =========================================================================
// A. Source-level contracts.
// =========================================================================
var SCRIPTS = [];
(function () {
  var re = /<script src="([^"]+)"/g, m;
  while ((m = re.exec(INDEX))) SCRIPTS.push(m[1]);
})();
eq('A1 the consumer ships as the fifth isolated helper, after pp-migrate.js', SCRIPTS, [
  'data-a1.js', 'data-a2.js', 'data-b1.js', 'data-grammar.js', 'data-verbs.js',
  'data-scenarios.js', 'data-podcasts.js', 'pp-usage.js', 'pp-answer.js',
  'pp-distractor.js', 'pp-migrate.js', 'pp-verb-patterns.js']);

// The injection entry point must be unreachable from the shipping application.
eq('A2 the test-only injection entry point is not referenced by index.html',
   countOf(INDEX, '__acceptForTest'), 0);
// String literals only: the two pre-existing prose comments that name a test file
// are not code paths, and a comment cannot fetch anything.
eq('A2 the shipping app has no code path to a tests/ file or a fixture',
   countOf(INDEX, '"tests/') + countOf(INDEX, "'tests/") +
   countOf(INDEX, '"fixture') + countOf(INDEX, "'fixture") +
   countOf(INDEX, 'runtime-fixture'), 0);
eq('A2 the shipping app never names the non-release wrapper',
   countOf(INDEX, 'runtimeProjection') + countOf(INDEX, 'releaseAuthorized') +
   countOf(INDEX, NONRELEASE_MARKER), 0);
eq('A2 no developer switch, query parameter or fixture mode was added',
   countOf(INDEX, 'loadFixture') + countOf(INDEX, 'searchParams') +
   countOf(INDEX, 'URLSearchParams') + countOf(INDEX, '?fixture'), 0);
// SUPERSEDED by Priority 7 Phase 4F-I1, the atomic release that activates the
// surface. The claim narrows rather than disappearing: the shell names the
// official runtime URL exactly once, in one production constant, and names no
// other runtime document at all.
eq('A2 the shipping app names the official runtime URL exactly once',
   [countOf(INDEX, 'verb-patterns.json'),
    countOf(INDEX, 'const PRIORITY7_RUNTIME_URL = "./content/verb-patterns.json";'),
    countOf(INDEX, 'loadRuntimeDocument')], [1, 1, 1]);

var PATTERNS_BLOCK = sliceBetween(
  INDEX, 'const P = { li:0, ti:0, topicRef:null',
  '/* ---------------- grammar (teach -> drill) ---------------- */');
var PATTERNS_CODE = stripComments(PATTERNS_BLOCK);
['innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval('].forEach(function (token) {
  eq('A3 the reference renderers never use ' + token, countOf(PATTERNS_CODE, token), 0);
});
ok('A3 every rendered string goes through textContent',
   countOf(PATTERNS_CODE, 'textContent') > 0);
eq('A3 the renderers write no storage',
   countOf(PATTERNS_CODE, 'localStorage') + countOf(PATTERNS_CODE, 'sessionStorage') +
   countOf(PATTERNS_CODE, 'persistProgress') + countOf(PATTERNS_CODE, 'saveV2'), 0);
eq('A3 the surface adds no history entry of its own',
   countOf(PATTERNS_CODE, 'pushState') + countOf(PATTERNS_CODE, 'history.'), 0);
eq('A3 no runtime identifier is written into the DOM by the renderers',
   countOf(PATTERNS_CODE, 'vp-l-') + countOf(PATTERNS_CODE, 'vp-m-') +
   countOf(PATTERNS_CODE, 'vp-p-') + countOf(PATTERNS_CODE, 'vp-e-'), 0);
// Editorial vocabulary must never reach learner-facing copy.
['relationType', 'lexical-frame', 'means-method', 'subject-experiencer',
 'active-production', 'recognition-only', 'research', 'deferred', 'teachingStatus',
 'activityEligibility', 'reviewState', 'contentRef', 'patternDataRevision',
 'valency', 'government', 'complement'].forEach(function (term) {
  eq('A4 the reference surface never renders the editorial term "' + term + '"',
     countOf(PATTERNS_CODE, '"' + term + '"') + countOf(PATTERNS_CODE, "'" + term + "'"), 0);
});
ok('A4 the recognition signal uses the approved learner label',
   hasCode(PATTERNS_CODE, '"Understand for now"'));
ok('A4 the retired recognition label is gone from the surface entirely',
   countOf(PATTERNS_CODE, 'Understand this one') === 0);

// The screen itself: a reference header, with no activity furniture.
var SCREEN = sliceBetween(INDEX, '<section class="screen" id="patterns">', '</section>');
ok('A5 the new screen is an ordinary app screen', SCREEN.indexOf('<div class="sbar">') !== -1);
eq('A5 it has a Back control and a Home control',
   [countOf(SCREEN, 'id="pBack"'), countOf(SCREEN, 'class="back home-btn"')], [1, 1]);
eq('A5 it has exactly one h1, in the shared title slot', countOf(SCREEN, '<h1 id="pTitle">'), 1);
eq('A5 nothing plays here, so there is no speed control', countOf(SCREEN, 'speed-toggle'), 0);
eq('A5 nothing is scored here, so there is no progress bar', countOf(SCREEN, 'class="progress"'), 0);
eq('A5 exactly one polite atomic status region',
   countOf(SCREEN, 'role="status" aria-live="polite" aria-atomic="true"'), 1);
eq('A5 the content region is empty in the markup and built by the renderer',
   countOf(SCREEN, '<div class="vp-body" id="pBody"></div>'), 1);
eq('A5 the screen stays out of the hash deep-link allowlist',
   [countOf(INDEX, '["about","privacy","contact","install"].includes(ppInitialScreen)'),
    countOf(INDEX, '"patterns"].includes'), countOf(INDEX, '"patterns","')], [1, 0, 0]);
ok('A5 the screen is declared after the round screen and before privacy',
   INDEX.indexOf('id="round"') < INDEX.indexOf('id="patterns"') &&
   INDEX.indexOf('id="patterns"') < INDEX.indexOf('id="privacy"'));

// Level synthesis: one topic, no identifier on it, and no fourth tab.
eq('A6 the pattern level joins the Grammar category with no engine edit',
   countOf(INDEX, 'level:"Verb Patterns", group:"grammar"'), 1);
// The entry is part of the ordinary information architecture, not something that
// appears only once data exists: a surface that vanishes when it has nothing to
// show cannot have its empty state validated, and the learner cannot find it.
eq('A6 the level is created unconditionally, gated on no data and no request',
   [countOf(INDEX, 'if(PP_VERB_PATTERNS && PP_VERB_PATTERNS.available){'),
    countOf(INDEX, 'LEVELS.push({ level:"Verb Patterns", group:"grammar",')], [0, 1]);
eq('A6 exactly one Verb Patterns level and one push site exist',
   [countOf(INDEX, 'level:"Verb Patterns"'), countOf(INDEX, 'LEVELS.push(')], [1, 2]);
eq('A6 nothing else can add a second Verb Patterns entry later',
   countOf(LOADER_SRC, 'LEVELS.push') + countOf(LOADER_SRC, 'PP_LEVELS') +
   countOf(PATTERNS_CODE, 'LEVELS.push'), 0);
// Creating and opening the surface must not depend on a network request. The two
// pre-existing fetches (the audio manifest and the freshness HEAD) are unchanged.
// SUPERSEDED by Priority 7 Phase 4F-I1. Creating and opening the surface still
// does not depend on a network request - the unavailable state is reachable and
// testable with no data at all - but the release adds exactly ONE fetch, in the
// Priority 7 block, through the shipping transport primitive. The two
// pre-existing fetches (the audio manifest and the freshness HEAD) are
// unchanged, and no second transport, await or XHR was introduced.
eq('A6 exactly one runtime fetch exists, and it is the one production load',
   [countOf(INDEX, 'fetch('), countOf(INDEX, 'content/'),
    countOf(PATTERNS_CODE, 'fetch('), countOf(PATTERNS_CODE, 'await'),
    countOf(PATTERNS_CODE, 'XMLHttpRequest'),
    countOf(PATTERNS_CODE, 'PP_VERB_PATTERNS.loadRuntimeDocument(')],
   [3, 1, 1, 0, 0, 1]);
eq('A6 the tile claims no size it cannot back up',
   hasCode(INDEX, 'return PP_VERB_PATTERNS.available ? PP_VERB_PATTERNS.countLabel() : "Not ready yet";'),
   true);
eq('A6 the three-tab category row is untouched',
   countOf(INDEX, '{ key:"vocab",    label:"Vocabulary", sub:"Choose the level" }') +
   countOf(INDEX, '{ key:"grammar",  label:"Grammar",    sub:"Choose a set" }') +
   countOf(INDEX, '{ key:"practice", label:"More",       sub:"Choose an activity" }'), 3);
eq('A6 no fourth top-level category was added', countOf(INDEX, 'CATEGORIES = ['), 1);
// AMENDED by Priority 7 Phase 3C.  These two assertions pinned the 3B/3C phase
// boundary: the cross-links and the card pointer did not exist yet.  They are
// now inverted rather than deleted, and each keeps the half of its original
// meaning that is still a safety property - the case-topic ids and the link
// wording live in the loader's static map and NOT in the shell, and the card
// pointer is derived through cardSupport and nowhere else.
eq('A7 no case lesson was edited, and no case-topic id was hard-coded into the shell',
   [countOf(INDEX, 'grammar-cases-genitive'), countOf(INDEX, 'Verbs that take the'),
    countOf(LOADER_SRC, 'grammar-cases-genitive')], [0, 0, 1]);
eq('A7 the card pointer is derived through the two-gate index and nothing else',
   [countOf(PATTERNS_CODE, 'cardSupport'), countOf(INDEX, 'patternLine') > 0,
    countOf(PATTERNS_CODE, 'contentRefs')], [1, true, 0]);
eq('A7 no pattern activity, queue or score exists',
   countOf(PATTERNS_CODE, 'pStartPractice') + countOf(PATTERNS_CODE, 'queue') +
   countOf(PATTERNS_CODE, 'score') + countOf(PATTERNS_CODE, 'rRecord'), 0);

// =========================================================================
// B. The harness contract, proven from both sides (runtime contract 4.5a).
// =========================================================================
PP_VERB_PATTERNS.reset();
eq('B1 the loader starts unavailable', PP_VERB_PATTERNS.available, false);
eq('B1 an unavailable loader offers no index', PP_VERB_PATTERNS.hasIndex(), false);
eq('B1 an unavailable loader offers no rows', PP_VERB_PATTERNS.index().length, 0);
eq('B1 an unavailable loader offers no filters', PP_VERB_PATTERNS.filters().length, 0);
eq('B1 an unavailable loader resolves no lemma', PP_VERB_PATTERNS.lemma(0), null);
eq('B1 an unavailable loader claims no counts', PP_VERB_PATTERNS.summary(), { lemmas: 0, patterns: 0 });

// Side one: the shipping path REFUSES the wrapped fixture.
eq('B2 the shipping loader rejects the wrapped non-release fixture',
   PP_VERB_PATTERNS.acceptRuntimeDocument(WRAPPED_FIXTURE), false);
eq('B2 a rejected document leaves the surface unavailable', PP_VERB_PATTERNS.available, false);
eq('B2 the injection entry point is not a wrapper-stripper either',
   PP_VERB_PATTERNS.__acceptForTest(WRAPPED_FIXTURE), false);
eq('B2 a bare projection with a wrapper field bolted on is still rejected', (function () {
  var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
  doc.releaseAuthorized = false;
  return PP_VERB_PATTERNS.acceptRuntimeDocument(doc);
})(), false);
eq('B2 a projection carrying the non-release status field is rejected', (function () {
  var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
  doc.artifactStatus = NONRELEASE_MARKER;
  return PP_VERB_PATTERNS.acceptRuntimeDocument(doc);
})(), false);
eq('B2 a document that merely CONTAINS a valid projection is rejected', (function () {
  return PP_VERB_PATTERNS.acceptRuntimeDocument(
    { formatVersion: 1, patternDataRevision: 1, lemmas: [], extra: WRAPPED_FIXTURE });
})(), false);

// Side two: the harness may deliberately inject the projection it contains.
ok('B3 the harness asserts the wrapper before it opens it',
   throws(function () { unwrapNonReleaseFixtureForTest({ runtimeProjection: {} }); }) &&
   throws(function () {
     unwrapNonReleaseFixtureForTest(
       { artifactStatus: NONRELEASE_MARKER, releaseAuthorized: true,
         runtimeProjection: {} });
   }) &&
   throws(function () {
     unwrapNonReleaseFixtureForTest(
       { artifactStatus: 'something-else', releaseAuthorized: false,
         runtimeProjection: {} });
   }) &&
   throws(function () { unwrapNonReleaseFixtureForTest(null); }));
ok('B3 the harness accepts the committed fixture', !throws(injectFixture));
eq('B3 the injected projection makes the surface available', PP_VERB_PATTERNS.available, true);
eq('B3 the same derivation code now has an index', PP_VERB_PATTERNS.hasIndex(), true);
eq('B4 the fixture is what the phase says it is',
   [WRAPPED_FIXTURE.artifactStatus, WRAPPED_FIXTURE.releaseAuthorized],
   [NONRELEASE_MARKER, false]);
eq('B4 accepting a value proves nothing about release authorization - the loader has no such API',
   Object.keys(PP_VERB_PATTERNS).filter(function (key) {
     return /releas|authoriz|verified|frozen|approv/i.test(key);
   }), []);

// =========================================================================
// C. Envelope validation, in order, and whole-candidate atomic rejection.
// =========================================================================
function acceptClone(mutate) {
  var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
  mutate(doc);
  var accepted = PP_VERB_PATTERNS.__acceptForTest(doc);
  return accepted;
}
eq('C1 a non-object is rejected', [
  PP_VERB_PATTERNS.__acceptForTest(null), PP_VERB_PATTERNS.__acceptForTest(undefined),
  PP_VERB_PATTERNS.__acceptForTest('{}'), PP_VERB_PATTERNS.__acceptForTest(42),
  PP_VERB_PATTERNS.__acceptForTest([]), PP_VERB_PATTERNS.__acceptForTest(true)
], [false, false, false, false, false, false]);
eq('C1 a missing envelope key is rejected',
   acceptClone(function (d) { delete d.patternDataRevision; }), false);
eq('C1 an unexpected envelope key is rejected',
   acceptClone(function (d) { d.somethingElse = 1; }), false);
eq('C2 a wrong format version is rejected',
   [acceptClone(function (d) { d.formatVersion = 2; }),
    acceptClone(function (d) { d.formatVersion = '1'; })], [false, false]);
eq('C3 a non-positive or non-integer revision is rejected',
   [acceptClone(function (d) { d.patternDataRevision = 0; }),
    acceptClone(function (d) { d.patternDataRevision = -1; }),
    acceptClone(function (d) { d.patternDataRevision = 1.5; }),
    acceptClone(function (d) { d.patternDataRevision = '1'; })],
   [false, false, false, false]);
eq('C4 an empty or non-array lemma list is rejected',
   [acceptClone(function (d) { d.lemmas = []; }),
    acceptClone(function (d) { d.lemmas = {}; })], [false, false]);
// Every private editorial key, at three depths.
var PRIVATE_KEYS = JSON.parse('[' + (function () {
  var block = LOADER_SRC.slice(LOADER_SRC.indexOf('var PRIVATE_KEYS = ['));
  block = block.slice(block.indexOf('[') + 1, block.indexOf(']'));
  return block.replace(/\s+/g, ' ');
})() + ']');
eq('C5 the loader mirrors all 26 private editorial keys', PRIVATE_KEYS.length, 26);
var privateLeaks = PRIVATE_KEYS.filter(function (key) {
  var atRoot = acceptClone(function (d) { d[key] = 'x'; });
  var atLemma = acceptClone(function (d) { d.lemmas[0][key] = 'x'; });
  var atPattern = acceptClone(function (d) {
    d.lemmas[0].meanings[0].patterns[0][key] = 'x';
  });
  var atExample = acceptClone(function (d) {
    var found = null;
    d.lemmas.forEach(function (lemma) {
      lemma.meanings.forEach(function (meaning) {
        meaning.patterns.forEach(function (pattern) {
          if (pattern.examples && !found) found = pattern.examples[0];
        });
      });
    });
    found[key] = 'x';
  });
  return atRoot || atLemma || atPattern || atExample;
});
eq('C5 a private key at any depth rejects the whole document', privateLeaks, []);
eq('C5 an immutable authoring key is refused like any other private field',
   acceptClone(function (d) {
     d.lemmas[0].meanings[0].patterns[0].key = 'genitive-target';
   }), false);

// Phase 3F-A tightens step 6 at the public load boundary: a malformed nested
// entity rejects the WHOLE candidate. The previously accepted state stays
// byte-for-byte intact; there is no pruned/partial acceptance.
function acceptAndCount(mutate) {
  var before = JSON.stringify({
    summary: PP_VERB_PATTERNS.summary(),
    index: PP_VERB_PATTERNS.index(),
    filters: PP_VERB_PATTERNS.filters()
  });
  var accepted = acceptClone(mutate);
  return {
    accepted: accepted,
    unchanged: JSON.stringify({
      summary: PP_VERB_PATTERNS.summary(),
      index: PP_VERB_PATTERNS.index(),
      filters: PP_VERB_PATTERNS.filters()
    }) === before,
    summary: PP_VERB_PATTERNS.summary()
  };
}
injectFixture();
var FULL = PP_VERB_PATTERNS.summary();
eq('C6 the whole fixture is admitted', FULL, { lemmas: 6, patterns: 10 });
function multiPatternPath(doc) {
  // metodowac is the lemma with three sibling patterns in one meaning
  var found = null;
  doc.lemmas.forEach(function (lemma) {
    lemma.meanings.forEach(function (meaning) {
      if (meaning.patterns.length === 3) found = meaning;
    });
  });
  return found;
}
eq('C6 an unknown complement type rejects the candidate without changing state',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].complements[0].type = 'ablative';
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 an unknown case id rejects the candidate without changing state',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].complements[0].case = 'partitive';
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 a direct Locative complement rejects the candidate atomically',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].complements[0] =
       { type: 'case', case: 'locative', required: true, role: 'topic' };
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 an unknown relation type rejects the candidate atomically',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].relationType = 'mystery-frame';
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 an unknown role rejects the candidate atomically',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].complements[0].role = 'beneficiary';
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 a non-public teaching status rejects the candidate atomically',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].teachingStatus = 'deferred';
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 an unknown activity key rejects the candidate atomically',
   acceptAndCount(function (d) {
     multiPatternPath(d).patterns[0].activityEligibility = ['teleport'];
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 a malformed only pattern cannot prune and partly accept its lemma',
   acceptAndCount(function (d) {
     d.lemmas.forEach(function (lemma) {
       if (lemma.canonicalLemma === 'fikcjonować') {
         lemma.meanings[0].patterns[0].learnerExplanationEn = '';
       }
     });
   }), { accepted: false, unchanged: true, summary: FULL });
eq('C6 a document whose every pattern is malformed is rejected and retains valid state',
   (function () {
  return acceptAndCount(function (d) {
    d.lemmas.forEach(function (lemma) {
      lemma.meanings.forEach(function (meaning) {
        meaning.patterns.forEach(function (pattern) { pattern.cefr = { recognition: 'C2' }; });
      });
    });
  });
})(), { accepted: false, unchanged: true, summary: FULL });
injectFixture();

// =========================================================================
// D. Central case metadata and question derivation.
// =========================================================================
function directQuestions(caseId) {
  return PP_VERB_PATTERNS.questionsFor(
    { type: 'case', case: caseId, required: true, role: 'object' }).join(' ');
}
function prepQuestions(preposition, caseId) {
  return PP_VERB_PATTERNS.questionsFor(
    { type: 'preposition-case', preposition: preposition, case: caseId,
      required: true, role: 'object' }).join(' ');
}
eq('D1 all seven cases are known centrally',
   PP_VERB_PATTERNS.CASE_ORDER,
   ['nominative', 'genitive', 'dative', 'accusative', 'instrumental', 'locative', 'vocative']);
eq('D1 each case knows both of its names', PP_VERB_PATTERNS.CASE_ORDER.map(function (id) {
  var meta = PP_VERB_PATTERNS.caseMeta(id);
  return meta.pl + '|' + meta.en;
}), ['Mianownik|Nominative', 'Dopełniacz|Genitive', 'Celownik|Dative',
     'Biernik|Accusative', 'Narzędnik|Instrumental', 'Miejscownik|Locative',
     'Wołacz|Vocative']);
eq('D1 an unknown case id resolves to nothing', PP_VERB_PATTERNS.caseMeta('partitive'), null);
eq('D2 direct questions derive exactly', [
  directQuestions('nominative'), directQuestions('genitive'), directQuestions('dative'),
  directQuestions('accusative'), directQuestions('instrumental')
], ['kto? co?', 'kogo? czego?', 'komu? czemu?', 'kogo? co?', 'kim? czym?']);
eq('D2 Vocative fabricates no diagnostic question', directQuestions('vocative'), '');
ok('D2 Vocative carries a direct-address cue instead',
   PP_VERB_PATTERNS.caseMeta('vocative').address === true);
eq('D3 every preposition+case combination derives to natural Polish', [
  prepQuestions('od', 'genitive'), prepQuestions('o', 'accusative'),
  prepQuestions('na', 'accusative'), prepQuestions('za', 'accusative'),
  prepQuestions('w', 'accusative'), prepQuestions('z', 'instrumental'),
  prepQuestions('za', 'instrumental'), prepQuestions('w', 'locative'),
  prepQuestions('o', 'locative'), prepQuestions('na', 'locative'),
  prepQuestions('przeciwko', 'dative')
], ['od kogo? od czego?', 'o kogo? o co?', 'na kogo? na co?', 'za kogo? za co?',
    'w kogo? w co?', 'z kim? z czym?', 'za kim? za czym?', 'w kim? w czym?',
    'o kim? o czym?', 'na kim? na czym?', 'przeciwko komu? przeciwko czemu?']);
eq('D4 the chip bonds the preposition, the questions and the full case name',
   PP_VERB_PATTERNS.chipFor(
     { type: 'preposition-case', preposition: 'z', case: 'instrumental',
       required: true, role: 'interlocutor' }, 'lexical-frame').text,
   'z kim? z czym? · Instrumental');
eq('D4 a direct case chip reads the same way',
   PP_VERB_PATTERNS.chipFor(
     { type: 'case', case: 'genitive', required: true, role: 'object' },
     'lexical-frame').text, 'kogo? czego? · Genitive');
eq('D4 the Polish half and the English half carry their own language',
   PP_VERB_PATTERNS.chipFor(
     { type: 'case', case: 'genitive', required: true, role: 'object' },
     'lexical-frame').parts.map(function (part) { return part.lang; }), ['pl', null]);
eq('D4 an infinitive complement has a chip of the same shape, with no case',
   PP_VERB_PATTERNS.chipFor(
     { type: 'infinitive', required: true, role: 'content' }, 'lexical-frame').text,
   '+ bezokolicznik · Infinitive');
eq('D4 a clause complement renders its own clause token', [
  PP_VERB_PATTERNS.chipFor({ type: 'clause', clauseKind: 'ze', required: true, role: 'content' }, 'lexical-frame').text,
  PP_VERB_PATTERNS.chipFor({ type: 'clause', clauseKind: 'czy', required: true, role: 'content' }, 'lexical-frame').text,
  PP_VERB_PATTERNS.chipFor({ type: 'clause', clauseKind: 'zeby', required: true, role: 'content' }, 'lexical-frame').text
], ['+ że … · Clause', '+ czy … · Clause', '+ żeby … · Clause']);
eq('D4 non-case complements share one filter bucket', [
  PP_VERB_PATTERNS.chipFor({ type: 'infinitive', required: true, role: 'content' }, 'lexical-frame').bucket,
  PP_VERB_PATTERNS.chipFor({ type: 'clause', clauseKind: 'ze', required: true, role: 'content' }, 'lexical-frame').bucket
], [PP_VERB_PATTERNS.NO_CASE_BUCKET, PP_VERB_PATTERNS.NO_CASE_BUCKET]);
eq('D5 every closed role has exactly one fixed English phrasing',
   Object.keys(PP_VERB_PATTERNS.ROLE_PHRASES).sort(),
   ['content', 'experiencer', 'interlocutor', 'means', 'object', 'predicate',
    'recipient', 'subject', 'target', 'topic']);
eq('D5 the role line is the disambiguator when two chips share a case', (function () {
  var asked = PP_VERB_PATTERNS.chipFor(
    { type: 'case', case: 'accusative', required: true, role: 'interlocutor' }, 'lexical-frame');
  var wanted = PP_VERB_PATTERNS.chipFor(
    { type: 'preposition-case', preposition: 'o', case: 'accusative', required: true, role: 'target' },
    'lexical-frame');
  return [asked.caseName === wanted.caseName, asked.role !== wanted.role];
})(), [true, true]);
eq('D5 subject-experiencer takes its own subject phrasing',
   PP_VERB_PATTERNS.roleFor(
     { type: 'case', case: 'nominative', required: true, role: 'subject' },
     'subject-experiencer'), 'the thing that appeals');
eq('D6 only the recognition level is ever badged', (function () {
  var badge = PP_VERB_PATTERNS.badgeFor(
    { cefr: { recognition: 'A2', production: 'B1' }, teachingStatus: 'active-production' });
  return [badge.text, badge.srText, badge.text.indexOf('B1')];
})(), ['A2', 'Recognise from A2', -1]);
eq('D6 an above-B1 recognition level is labelled honestly',
   PP_VERB_PATTERNS.badgeFor({ cefr: { recognition: 'above-b1' } }).text, 'B1+');

// =========================================================================
// E. Activity eligibility: an allowlist that fails closed.
// =========================================================================
var refPattern = { teachingStatus: 'active-production', activityEligibility: ['reference', 'search', 'grammar-choose'] };
var emptyPattern = { teachingStatus: 'active-production', activityEligibility: [] };
var recogPattern = { teachingStatus: 'recognition-only', activityEligibility: ['reference', 'search', 'grammar-choose'] };
eq('E1 an empty allowlist admits nothing', [
  PP_VERB_PATTERNS.eligibleFor(emptyPattern, 'type-it'),
  PP_VERB_PATTERNS.eligibleFor(emptyPattern, 'grammar-choose'),
  PP_VERB_PATTERNS.eligibleFor(emptyPattern, 'reference')
], [false, false, false]);
eq('E1 an unknown activity name fails closed', [
  PP_VERB_PATTERNS.eligibleFor(refPattern, 'typeit'),
  PP_VERB_PATTERNS.eligibleFor(refPattern, 'grammar_choose'),
  PP_VERB_PATTERNS.eligibleFor(refPattern, ''),
  PP_VERB_PATTERNS.eligibleFor(refPattern, null),
  PP_VERB_PATTERNS.eligibleFor(refPattern, undefined)
], [false, false, false, false, false]);
eq('E1 a missing or non-array allowlist fails closed', [
  PP_VERB_PATTERNS.eligibleFor({ teachingStatus: 'active-production' }, 'reference'),
  PP_VERB_PATTERNS.eligibleFor({ activityEligibility: 'reference' }, 'reference'),
  PP_VERB_PATTERNS.eligibleFor(null, 'reference'),
  PP_VERB_PATTERNS.eligibleFor(undefined, 'reference')
], [false, false, false, false]);
eq('E1 an allowed activity is allowed', [
  PP_VERB_PATTERNS.eligibleFor(refPattern, 'reference'),
  PP_VERB_PATTERNS.eligibleFor(refPattern, 'grammar-choose'),
  PP_VERB_PATTERNS.eligibleFor(refPattern, 'type-it')
], [true, true, false]);
eq('E2 a recognition-only pattern can never request a production activity', [
  PP_VERB_PATTERNS.eligibleFor(recogPattern, 'type-it'),
  PP_VERB_PATTERNS.eligibleFor(recogPattern, 'grammar-build'),
  PP_VERB_PATTERNS.eligibleFor(recogPattern, 'grammar-choose'),
  PP_VERB_PATTERNS.eligibleFor(recogPattern, 'reference')
], [false, false, true, true]);
eq('E3 no pattern in the fixture is offered any activity affordance by the UI',
   countOf(PATTERNS_CODE, 'eligibleFor'), 0);

// =========================================================================
// F. Information architecture: one lemma, one entry, case as a view.
// =========================================================================
injectFixture();
var INDEX_ROWS = PP_VERB_PATTERNS.index();
eq('F1 the index holds exactly one canonical row per lemma', INDEX_ROWS.length, 6);
eq('F1 the index is A-Z by folded lemma, with `się` intact',
   INDEX_ROWS.map(function (row) { return row.lemma; }),
   ['bezokolicznikować', 'fikcjonować',
    'konstrukcjować (synthetic-nonrelease display form, deliberately long)',
    'metodować', 'podobnikować się', 'zetafikcjonować się']);
eq('F1 letter headings come from the folded sort key',
   INDEX_ROWS.map(function (row) { return row.letter; }), ['B', 'F', 'K', 'M', 'P', 'Z']);
eq('F1 an index row carries no chip - a chip would assert one answer',
   INDEX_ROWS.filter(function (row) { return row.chips && row.chips.length; }).length, 0);
eq('F2 a lemma with two meanings stays ONE lemma with two meanings', (function () {
  var row = INDEX_ROWS.filter(function (r) { return r.lemma === 'zetafikcjonować się'; })[0];
  var entry = PP_VERB_PATTERNS.lemma(row.key);
  return [row.meaningCount, row.patternCount, entry.meanings.length, entry.multiMeaning];
})(), [2, 2, 2, true]);
eq('F2 a meaning with three patterns keeps all three, none hidden', (function () {
  var row = INDEX_ROWS.filter(function (r) { return r.lemma === 'metodować'; })[0];
  var entry = PP_VERB_PATTERNS.lemma(row.key);
  return [entry.meanings.length, entry.meanings[0].patterns.length];
})(), [1, 3]);
eq('F2 sibling patterns are ordered simplest frame first', (function () {
  var row = INDEX_ROWS.filter(function (r) { return r.lemma === 'metodować'; })[0];
  return PP_VERB_PATTERNS.lemma(row.key).meanings[0].patterns.map(function (pattern) {
    return pattern.chips.length;
  });
})(), [1, 1, 2]);
eq('F3 the filter row is derived from the cases actually present, plus no-case',
   PP_VERB_PATTERNS.filters().map(function (option) { return option.id; }),
   ['all', 'nominative', 'genitive', 'dative', 'accusative', 'instrumental',
    'locative', 'no-case']);
eq('F3 filter labels are full case names, never abbreviations',
   PP_VERB_PATTERNS.filters().map(function (option) { return option.label; }),
   ['All verbs', 'Nominative', 'Genitive', 'Dative', 'Accusative',
    'Instrumental', 'Locative', 'No case (verb / clause)']);
eq('F3 the accessible name adds the Polish name around the visible English one',
   PP_VERB_PATTERNS.filters().map(function (option) { return option.srLabel; }),
   ['All verbs', 'Nominative (Mianownik)', 'Genitive (Dopełniacz)',
    'Dative (Celownik)', 'Accusative (Biernik)', 'Instrumental (Narzędnik)',
    'Locative (Miejscownik)', 'No case (verb / clause)']);
eq('F3 eight chips is the whole filter row', PP_VERB_PATTERNS.filters().length, 8);
eq('F4 filtering owns nothing: every filter state still resolves to one entry per lemma',
   PP_VERB_PATTERNS.filters().map(function (option) {
     var seen = {}, duplicates = 0;
     PP_VERB_PATTERNS.rows(option.id).forEach(function (row) {
       var entry = PP_VERB_PATTERNS.lemma(row.key);
       if (!entry) duplicates++;
       if (!seen[row.key]) seen[row.key] = 0;
       seen[row.key]++;
     });
     return duplicates;
   }), [0, 0, 0, 0, 0, 0, 0, 0]);
eq('F4 a filtered row is a pointer with a summary, never a rendering', (function () {
  var rows = PP_VERB_PATTERNS.rows('dative');
  return rows.every(function (row) {
    return row.isSummary === true && row.chips.length > 0 &&
      row.explanation === undefined && row.example === undefined &&
      row.eligibility === undefined;
  });
})(), true);
eq('F5 filtering a two-complement pattern keeps the COMPLETE frame', (function () {
  var rows = PP_VERB_PATTERNS.rows('locative');
  var target = rows.filter(function (row) { return row.chips.length === 2; })[0];
  return [target.chips.map(function (chip) { return chip.text; }),
          target.chips.map(function (chip) { return chip.match; })];
})(), [['komu? czemu? · Dative', 'w kim? w czym? · Locative'], [false, true]]);
eq('F5 the same pattern is reachable from the other case it contains too', (function () {
  var dative = PP_VERB_PATTERNS.rows('dative').filter(function (row) {
    return row.chips.length === 2 && row.chips[1].text.indexOf('Locative') !== -1;
  });
  return [dative.length, dative[0].chips[0].match, dative[0].chips[1].match];
})(), [1, true, false]);
eq('F5 a mixed case-and-clause pattern shows its clause token in a case filter', (function () {
  var rows = PP_VERB_PATTERNS.rows('dative');
  var mixed = rows.filter(function (row) {
    return row.chips.some(function (chip) { return chip.caseName === 'Clause'; });
  })[0];
  return mixed.chips.map(function (chip) { return chip.text; });
})(), ['komu? czemu? · Dative', '+ że … · Clause']);
eq('F6 infinitive and clause complements are discoverable under the no-case filter',
   PP_VERB_PATTERNS.rows('no-case').map(function (row) {
     return row.lemma + ' :: ' + row.chips.map(function (chip) { return chip.caseName; }).join('+');
   }), ['bezokolicznikować :: Infinitive', 'bezokolicznikować :: Dative+Clause']);
eq('F6 filter counts report verbs AND patterns, because they differ',
   PP_VERB_PATTERNS.filterCounts('dative'), { verbs: 3, patterns: 3 });
eq('F6 the unfiltered count is the whole corpus, not the row count',
   PP_VERB_PATTERNS.filterCounts('all'), { verbs: 6, patterns: 10 });
eq('F7 no runtime identifier crosses the loader boundary', (function () {
  var payload = JSON.stringify([
    PP_VERB_PATTERNS.index(), PP_VERB_PATTERNS.filters(),
    PP_VERB_PATTERNS.rows('genitive'), PP_VERB_PATTERNS.rows('all'),
    PP_VERB_PATTERNS.lemma(0), PP_VERB_PATTERNS.lemma(1),
    PP_VERB_PATTERNS.lemma(2), PP_VERB_PATTERNS.lemma(3),
    PP_VERB_PATTERNS.lemma(4), PP_VERB_PATTERNS.lemma(5),
    PP_VERB_PATTERNS.searchText(), PP_VERB_PATTERNS.countLabel()
  ]);
  return [countOf(payload, 'vp-l-'), countOf(payload, 'vp-m-'),
          countOf(payload, 'vp-p-'), countOf(payload, 'vp-e-')];
})(), [0, 0, 0, 0]);
eq('F7 no private editorial value crosses it either', (function () {
  var payload = JSON.stringify([
    PP_VERB_PATTERNS.index(), PP_VERB_PATTERNS.rows('all'),
    PP_VERB_PATTERNS.lemma(0), PP_VERB_PATTERNS.lemma(3)
  ]);
  return PRIVATE_KEYS.filter(function (key) {
    return key !== 'key' && payload.indexOf('"' + key + '"') !== -1;
  });
})(), []);
eq('F8 the searchable string is small, flat and identifier-free', (function () {
  var text = PP_VERB_PATTERNS.searchText();
  return [text.indexOf('vp-'), text.indexOf('Genitive') !== -1,
          text.indexOf('Dopełniacz') !== -1, text.indexOf('kogo? czego?') !== -1,
          text.indexOf('bezokolicznik') !== -1,
          text.indexOf('SYNTHETIC-NONRELEASE: act on') !== -1];
})(), [-1, true, true, true, true, false]);
eq('F8 the tile reports verbs and patterns, which are different numbers',
   PP_VERB_PATTERNS.countLabel(), '6 verbs · 10 patterns');

// =========================================================================
// G. The card support index: derived in this phase, rendered in a later one.
// =========================================================================
function cardDocument(refs) {
  var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
  var single = null, multi = null;
  doc.lemmas.forEach(function (lemma) {
    if (lemma.canonicalLemma === 'fikcjonować') single = lemma;
    if (lemma.canonicalLemma === 'metodować') multi = lemma;
  });
  single.meanings[0].patterns[0].contentRefs = refs.single || [];
  multi.meanings[0].patterns[0].contentRefs = refs.multiA || [];
  multi.meanings[0].patterns[1].contentRefs = refs.multiB || [];
  if (!refs.single || !refs.single.length) delete single.meanings[0].patterns[0].contentRefs;
  if (!refs.multiA || !refs.multiA.length) delete multi.meanings[0].patterns[0].contentRefs;
  if (!refs.multiB || !refs.multiB.length) delete multi.meanings[0].patterns[1].contentRefs;
  PP_VERB_PATTERNS.__acceptForTest(doc);
  return true;
}
var support = { kind: 'card', id: 'p7-fixture-card-001', purpose: 'support' };
var contrast = { kind: 'card', id: 'p7-fixture-card-001', purpose: 'contrast' };
cardDocument({});
eq('G1 an unreferenced card gets nothing',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'none');
eq('G1 an unknown card id gets nothing',
   PP_VERB_PATTERNS.cardSupport('no-such-card').state, 'none');
cardDocument({ single: [support] });
eq('G2 one support reference on a single-meaning single-pattern lemma yields the chip',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'chip');
eq('G2 the chip is the pattern\'s own complete chip set',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').chips.map(function (chip) {
     return chip.text;
   }), ['kogo? co? · Accusative']);
cardDocument({ multiA: [support] });
eq('G3 a lemma with more than one pattern gets the neutral doorway, never a chip',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'doorway');
cardDocument({ single: [support], multiA: [support] });
eq('G3 a card claimed by two patterns gets the neutral doorway',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'doorway');
cardDocument({ single: [contrast] });
eq('G4 a contrast reference is invisible to the feature - it shows nothing',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'none');
cardDocument({ single: [{ kind: 'card', id: 'p7-fixture-card-001', purpose: 'practice' }] });
eq('G4 a practice card reference is not an instantiation claim either',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'none');
cardDocument({ single: [{ kind: 'drill', id: 'p7-fixture-card-001', purpose: 'practice' },
                        { kind: 'topic', id: 'p7-fixture-card-001', purpose: 'support' }] });
eq('G4 drill and topic references never reach the card surface',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'none');
cardDocument({ single: [contrast], multiA: [support] });
eq('G4 a contrast reference cannot downgrade or upgrade another pattern\'s outcome',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'doorway');
injectFixture();
eq('G5 the committed fixture carries no card reference at all, and the UI renders none',
   PP_VERB_PATTERNS.cardSupport('p7-fixture-card-001').state, 'none');

// =========================================================================
// H. Topic routing: every branch is a positive match, the default denies.
// =========================================================================
function Classes(owner) { this.owner = owner; }
Classes.prototype.contains = function (name) {
  return (' ' + (this.owner.className || '') + ' ').indexOf(' ' + name + ' ') !== -1;
};
Classes.prototype.add = function (name) {
  if (!this.contains(name)) this.owner.className = ((this.owner.className || '') + ' ' + name).trim();
};
Classes.prototype.remove = function (name) {
  this.owner.className = (' ' + (this.owner.className || '') + ' ')
    .split(' ' + name + ' ').join(' ').trim();
};
function El(tag, id) {
  this.tag = (tag || 'div').toLowerCase();
  this.id = id || '';
  this.className = '';
  this.classList = new Classes(this);
  this.attrs = {};
  this.children = [];
  this.parentElement = null;
  this._text = '';
  this.hidden = false;
  this.inert = false;
  this.disabled = false;
  this.connected = true;
  this.focusCount = 0;
  this.listeners = {};
  this.style = { display: '', visibility: '' };
  this.isContentEditable = false;
  this.open = false;
}
El.prototype.appendChild = function (child) {
  child.parentElement = this;
  this.children.push(child);
  return child;
};
El.prototype.setAttribute = function (name, value) {
  if (name === 'class') { this.className = String(value); return; }
  if (name === 'id') { this.id = String(value); return; }
  this.attrs[name] = String(value);
};
El.prototype.getAttribute = function (name) {
  if (name === 'class') return this.className || null;
  if (name === 'id') return this.id || null;
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.hasAttribute = function (name) { return this.getAttribute(name) !== null; };
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.addEventListener = function (type, handler) {
  if (!this.listeners[type]) this.listeners[type] = [];
  this.listeners[type].push(handler);
};
El.prototype.fire = function (type) {
  var self = this;
  if (typeof this['on' + type] === 'function') this['on' + type]();
  (this.listeners[type] || []).forEach(function (handler) { handler.call(self, { target: self }); });
};
El.prototype.closest = function (selector) {
  var interactive = ['button', 'a', 'input', 'textarea', 'select', 'summary'];
  for (var node = this; node; node = node.parentElement) {
    if (selector === '.screen') { if (node.classList.contains('screen')) return node; continue; }
    if (interactive.indexOf(node.tag) !== -1 && selector.indexOf(node.tag) !== -1) return node;
  }
  return null;
};
El.prototype.descendants = function () {
  var out = [];
  this.children.forEach(function (child) {
    out.push(child);
    if (child.descendants) out = out.concat(child.descendants());
  });
  return out;
};
El.prototype.matches = function (selector) {
  var m = selector.match(/^\[([a-z-]+)="([^"]*)"\]$/);
  if (m) return this.getAttribute(m[1]) === m[2];
  if (selector.charAt(0) === '.') return this.classList.contains(selector.slice(1));
  return this.tag === selector;
};
El.prototype.querySelectorAll = function (selector) {
  return this.descendants().filter(function (node) {
    return node.matches && node.matches(selector);
  });
};
El.prototype.querySelector = function (selector) {
  return this.querySelectorAll(selector)[0] || null;
};
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
    if (node.classList.contains('screen') && !node.classList.contains('active')) return;
  }
  this.focusCount++;
  this.lastFocusOptions = options || null;
  fakeDocument.activeElement = this;
};
El.prototype.scrollIntoView = function () { this.revealCount = (this.revealCount || 0) + 1; };
Object.defineProperty(El.prototype, 'textContent', {
  get: function () {
    return this._text + this.children.map(function (child) { return child.textContent; }).join('');
  },
  set: function (value) { this.children = []; this._text = String(value); }
});
function TextNode(value) { this.tag = '#text'; this._text = String(value); this.children = []; }
Object.defineProperty(TextNode.prototype, 'textContent', {
  get: function () { return this._text; },
  set: function (value) { this._text = String(value); }
});

var fakeDocument = {
  body: new El('body', 'body'),
  activeElement: null,
  createElement: function (tag) { return new El(tag); },
  createTextNode: function (text) { return new TextNode(text); },
  contains: function (el) { return !!(el && el.connected !== false); },
  querySelector: function (selector) {
    return selector === '.screen.active' ? SCREENS.active : null;
  },
  querySelectorAll: function () { return []; },
  getElementById: function (id) { return lookup(id); }
};
var fakeWindow = { getComputedStyle: null, scrollTo: function () {}, history: null };
var REGISTRY = {};
var SCREENS = { active: null };
function register(el) { REGISTRY[el.id] = el; return el; }
// Elements the renderer creates (#pList, #pCount) are found the way the browser
// finds them: by id, anywhere in the live tree.
function findById(node, id) {
  if (!node || !node.children) return null;
  for (var i = 0; i < node.children.length; i++) {
    var child = node.children[i];
    if (child.id === id) return child;
    var deeper = findById(child, id);
    if (deeper) return deeper;
  }
  return null;
}
function lookup(id) { return REGISTRY[id] || findById(fakeDocument.body, id); }

// The routing dispatch, executed as it ships, with recording stubs in place of
// every destination so a denied route is visible as "nothing was called".
var ROUTE_BLOCK = sliceBetween(INDEX, 'let pendingTopic = null;',
                               'function ppGlobalShortcutBlocked(');
var calls = [];
var routeEnv = {
  startGrammar: function () { calls.push('startGrammar'); },
  startConvo: function () { calls.push('startConvo'); },
  startTypeit: function () { calls.push('startTypeit'); },
  startListen: function () { calls.push('startListen'); },
  startPatterns: function () { calls.push('startPatterns'); },
  startTopic: function () { calls.push('startTopic'); },
  patternsReady: true,
  focusMoves: [],
  navigations: [],
  historyEntries: 0,
  gateOpen: false,
  invoker: null
};
var routeState = { levelIdx: 7, topicIdx: 3 };
var gateEl = register(new El('dialog', 'matureGate'));
var gateCancel = register(new El('button', 'matureCancel'));
var gateContinue = register(new El('button', 'matureContinue'));
var tileEl = new El('button', 'topicTile');
fakeDocument.body.appendChild(tileEl);
var ROUTING = Function('env', '$', 'console', 'S', 'document',
  'var startGrammar=env.startGrammar, startConvo=env.startConvo, startTypeit=env.startTypeit,' +
  ' startListen=env.startListen, startPatterns=env.startPatterns, startTopic=env.startTopic;\n' +
  'function pPatternSurfaceReady(t){ return !!(t && t.kind === "patterns" && t.surface === "verb-index"); }\n' +
  'function ppOpenSharedOverlay(overlay, initial){ env.gateOpen = true; env.invoker = document.activeElement; return true; }\n' +
  'function ppTakeSharedOverlayInvoker(overlay){ var i = env.invoker; env.invoker = null; return i; }\n' +
  'function ppCloseSharedOverlay(overlay, restore){ env.gateOpen = false; env.closedWithRestore = restore; return true; }\n' +
  'function ppUseInvokerForNextScreen(candidate){ env.nextInvoker = candidate || null; return true; }\n' +
  'function ppFocusActivityTarget(el){ if(!el) return false; env.focusMoves.push(el.id || el.tag); el.focus(); return true; }\n' +
  'function ppScreenEntryTarget(screen){ return screen ? screen.heading || null : null; }\n' +
  'function ppCurrentScreen(){ return null; }\n' +
  'function ppRestoreSiteMenuBackground(){ return true; }\n' +
  ROUTE_BLOCK +
  '\nreturn { routeTopic: routeTopic, openTopic: openTopic, closeMatureGate: closeMatureGate,' +
  ' pending: function(){ return pendingTopic; } };')(
  routeEnv, lookup, { info: function () { routeEnv.logs = (routeEnv.logs || 0) + 1; } },
  routeState, fakeDocument);

function routeAttempt(topic) {
  calls = [];
  routeEnv.focusMoves = [];
  routeEnv.logs = 0;
  fakeDocument.activeElement = tileEl;
  var before = tileEl.focusCount;
  var result = ROUTING.routeTopic(7, 3, topic);
  return { result: result, calls: calls.slice(), focusMoves: routeEnv.focusMoves.slice(),
           movedFocus: tileEl.focusCount !== before || fakeDocument.activeElement !== tileEl,
           logs: routeEnv.logs };
}
// 1 + 2: every shipping kind still reaches its own destination, and the new one
// reaches the new screen.
eq('H1 the new pattern kind reaches the reference surface and nothing else',
   routeAttempt({ kind: 'patterns', surface: 'verb-index' }).calls, ['startPatterns']);
eq('H2 grammar still routes to Grammar', routeAttempt({ kind: 'grammar' }).calls, ['startGrammar']);
eq('H2 convo still routes to Conversations', routeAttempt({ kind: 'convo' }).calls, ['startConvo']);
eq('H2 typeit still routes to Type It', routeAttempt({ kind: 'typeit' }).calls, ['startTypeit']);
eq('H2 listen still routes to Listening', routeAttempt({ kind: 'listen' }).calls, ['startListen']);
eq('H2 podcast still routes to flashcards', routeAttempt({ kind: 'podcast', cards: [] }).calls, ['startTopic']);
eq('H2 a vocabulary topic with no kind at all still routes to flashcards',
   routeAttempt({ cards: [] }).calls, ['startTopic']);
eq('H2 every known kind returns truthy', [
  routeAttempt({ kind: 'grammar' }).result, routeAttempt({ kind: 'convo' }).result,
  routeAttempt({ kind: 'typeit' }).result, routeAttempt({ kind: 'listen' }).result,
  routeAttempt({ kind: 'podcast' }).result, routeAttempt({ cards: [] }).result,
  routeAttempt({ kind: 'patterns', surface: 'verb-index' }).result
], [true, true, true, true, true, true, true]);
// 3: an unrecognised kind reaches NOTHING.
var UNKNOWN = [
  { kind: 'pattern' }, { kind: 'Patterns' }, { kind: 'typeIt' }, { kind: '' },
  { kind: null }, { kind: 0 }, { kind: {} }, { kind: [] }, { kind: false },
  { kind: 'flashcard' }, { kind: 'grammar-choose' }, { kind: 'PATTERNS' }
];
eq('H3 no unknown kind reaches any start function',
   UNKNOWN.map(function (topic) { return routeAttempt(topic).calls.length; }),
   UNKNOWN.map(function () { return 0; }));
eq('H3 an unknown kind never reaches the flashcard renderer',
   UNKNOWN.filter(function (topic) {
     return routeAttempt(topic).calls.indexOf('startTopic') !== -1;
   }).length, 0);
eq('H3 an unknown kind never reaches Grammar',
   UNKNOWN.filter(function (topic) {
     return routeAttempt(topic).calls.indexOf('startGrammar') !== -1;
   }).length, 0);
eq('H3 a topic that is not an object at all is denied without throwing',
   [routeAttempt(null).result, routeAttempt(undefined).result,
    routeAttempt('grammar').result, routeAttempt(7).result],
   [false, false, false, false]);
// 4 + 9: a denied route navigates nowhere and says so.
eq('H4 a denied route returns falsy',
   UNKNOWN.map(function (topic) { return routeAttempt(topic).result; }),
   UNKNOWN.map(function () { return false; }));
eq('H4 a denied route leaves exactly one quiet console note',
   UNKNOWN.map(function (topic) { return routeAttempt(topic).logs; }),
   UNKNOWN.map(function () { return 1; }));
eq('H4 a successful route logs nothing',
   routeAttempt({ kind: 'grammar' }).logs, 0);
// 5: no state moves.
eq('H5 a denied route mutates no activity state', (function () {
  routeState.levelIdx = 7; routeState.topicIdx = 3;
  UNKNOWN.forEach(function (topic) { routeAttempt(topic); });
  return [routeState.levelIdx, routeState.topicIdx];
})(), [7, 3]);
var ROUTE_FN = stripComments(extractFunction(INDEX, 'routeTopic'));
eq('H5 the dispatch mutates no activity state itself - only the destinations do',
   countOf(ROUTE_FN, 'S.') + countOf(ROUTE_FN, 'levelIdx') + countOf(ROUTE_FN, 'topicIdx'), 0);
eq('H5 the dispatch ends in an explicit deny rather than a fallthrough',
   hasCode(ROUTE_FN, 'else { console.info("Po polsku: unknown topic kind was not opened."); return false; }'),
   true);
eq('H5 startTopic is a named destination for the two kinds it can render',
   hasCode(ROUTE_FN, 'else if(typeof t.kind === "undefined" || t.kind === "podcast") startTopic(li, ti);'),
   true);
// 6: focus does not move.
eq('H6 a denied route leaves focus exactly where it was',
   UNKNOWN.map(function (topic) { return routeAttempt(topic).movedFocus; }),
   UNKNOWN.map(function () { return false; }));
eq('H6 a denied route calls no focus helper at all',
   UNKNOWN.map(function (topic) { return routeAttempt(topic).focusMoves.length; }),
   UNKNOWN.map(function () { return 0; }));
// 8: a pattern topic with a missing or invalid surface is denied, not rendered.
eq('H8 a pattern topic with no surface payload is denied',
   [routeAttempt({ kind: 'patterns' }).result,
    routeAttempt({ kind: 'patterns', surface: '' }).result,
    routeAttempt({ kind: 'patterns', surface: 'something-else' }).result],
   [false, false, false]);
// Having nothing to list is NOT a routing failure: the route succeeds and the
// screen says so. Only an unrecognised surface is denied.
eq('H8 a pattern topic routes successfully even with no reference data at all',
   (function () {
     PP_VERB_PATTERNS.reset();
     var run = routeAttempt({ kind: 'patterns', surface: 'verb-index' });
     return [run.result, run.calls, run.logs];
   })(), [true, ['startPatterns'], 0]);
eq('H8 the deny is on the routing decision, before the renderer',
   hasCode(extractFunction(INDEX, 'routeTopic'), 'if(!pPatternSurfaceReady(t)){'), true);
eq('H8 the routing precondition asks about the surface, never about the data',
   [hasCode(extractFunction(INDEX, 'pPatternSurfaceReady'), 'PP_VERB_PATTERNS'),
    hasCode(extractFunction(INDEX, 'pPatternDataReady'), 'PP_VERB_PATTERNS.available')],
   [false, true]);
// 7: the mature gate - the one path that could strand focus on <body>.
function gateAttempt(topic) {
  calls = [];
  routeEnv.focusMoves = [];
  fakeDocument.activeElement = tileEl;
  var opened = ROUTING.openTopic(7, 3, topic);
  gateContinue.fire('click');
  return { opened: opened, calls: calls.slice(), focusMoves: routeEnv.focusMoves.slice(),
           active: fakeDocument.activeElement, nextInvoker: routeEnv.nextInvoker };
}
eq('H7 the gate still routes an allowed mature topic and keeps the tile as its return target',
   (function () {
     var run = gateAttempt({ mature: true, cards: [] });
     return [run.opened, run.calls, run.nextInvoker === tileEl];
   })(), [false, ['startTopic'], true]);
eq('H7 a denied route THROUGH the gate returns focus to the remembered invoker',
   (function () {
     var run = gateAttempt({ mature: true, kind: 'not-a-kind' });
     return [run.calls.length, run.active === tileEl, run.focusMoves];
   })(), [0, true, ['topicTile']]);
eq('H7 a denied route through the gate retires the unused invoker',
   (function () { gateAttempt({ mature: true, kind: 'not-a-kind' }); return routeEnv.nextInvoker; })(), null);
eq('H7 focus never lands on the document body through the gate',
   (function () {
     var run = gateAttempt({ mature: true, kind: 'not-a-kind' });
     return run.active === fakeDocument.body;
   })(), false);
eq('H7 the gate itself is left closed either way',
   (function () { gateAttempt({ mature: true, kind: 'not-a-kind' }); return routeEnv.gateOpen; })(), false);
eq('H9 openTopic propagates the routing answer to a direct caller', [
  ROUTING.openTopic(7, 3, { kind: 'grammar' }),
  ROUTING.openTopic(7, 3, { kind: 'not-a-kind' }),
  ROUTING.openTopic(7, 3, { kind: 'patterns', surface: 'verb-index' }),
  ROUTING.openTopic(7, 3, { kind: 'patterns' })
], [true, false, true, false]);
eq('H9 the shipping call site propagates it too',
   hasCode(INDEX, 'return routeTopic(li, ti, t);') &&
   hasCode(INDEX, 'const routed = p ? routeTopic(p.li, p.ti, p.t) : false;'), true);

// =========================================================================
// I. The rendered surface, executed against the fake DOM.
// =========================================================================
var FOCUS_BLOCK = sliceBetween(INDEX, 'var ppScreenReturnTargets = new Map();',
                               "/* ---------------- the app's one screen-scroll contract");
var patternsScreen = register(new El('section', 'patterns'));
patternsScreen.classList.add('screen');
patternsScreen.classList.add('active');
fakeDocument.body.appendChild(patternsScreen);
SCREENS.active = patternsScreen;
var homeScreen = register(new El('section', 'home'));
homeScreen.classList.add('screen');
homeScreen.classList.add('active');
homeScreen.heading = homeScreen.appendChild(new El('h1', 'homeTitle'));
fakeDocument.body.appendChild(homeScreen);
var pTitle = register(new El('h1', 'pTitle'));
var pSub = register(new El('span', 'pSub'));
var pBody = register(new El('div', 'pBody'));
var pStatus = register(new El('div', 'pStatus'));
var pBack = register(new El('button', 'pBack'));
patternsScreen.appendChild(pBack);
patternsScreen.appendChild(pTitle);
patternsScreen.appendChild(pSub);
patternsScreen.appendChild(pBody);
patternsScreen.appendChild(pStatus);
patternsScreen.heading = pTitle;
patternsScreen.querySelector = function (selector) {
  return selector === 'h1' ? pTitle : El.prototype.querySelector.call(this, selector);
};
var uiEnv = { shows: [], storage: 0, grammarStarts: [] };
var PATTERN_TOPIC = { name: 'Verb Patterns', emoji: '🎯', kind: 'patterns',
  chip: 'Reference', desc: 'Look up a verb and see the case it takes',
  surface: 'verb-index', searchText: PP_VERB_PATTERNS.searchText() };
// The Grammar side of the cross-link, shaped exactly as data-grammar.js ships
// it for the only two fields the link resolver looks at: the topic id and
// kind:"grammar". The Mix topic comes first and carries NO id, as the app builds
// it, so it is a live negative case rather than an invented one.
var CASE_NAMES = ['nominative', 'genitive', 'dative', 'accusative',
                  'instrumental', 'locative', 'vocative'];
var GRAMMAR_TOPICS = [{ name: 'Wszystkie przypadki (Mix)', kind: 'grammar',
                        mixOf: 'Grammar Cases', teach: [{ front: 'authored' }], drills: [] }];
CASE_NAMES.forEach(function (name) {
  GRAMMAR_TOPICS.push({ id: 'grammar-cases-' + name, name: name, kind: 'grammar',
                        teach: [{ front: 'authored' }], drills: [] });
});
var FAKE_LEVELS = [
  { level: 'Verb Patterns', group: 'grammar', topics: [PATTERN_TOPIC] },
  { level: 'Grammar Cases', group: 'grammar', topics: GRAMMAR_TOPICS },
  { level: 'A1', topics: [{ name: 'First verbs', cards: [] }] }
];
var UI = Function('document', 'window', '$', 'LEVELS', 'PP_VERB_PATTERNS', 'env',
  'function show(scr, defer){ env.shows.push([scr, defer]); return true; }\n' +
  'function startGrammar(li, ti){ env.grammarStarts.push([li, ti]); return true; }\n' +
  FOCUS_BLOCK + '\n' + PATTERNS_BLOCK +
  '\nreturn { P: P, startPatterns: startPatterns, renderIndex: pRenderIndex,' +
  ' applyFilter: pApplyFilter, openLemma: pOpenLemma, ready: pPatternSurfaceReady,' +
  ' dataReady: pPatternDataReady, remember: ppRememberScreenInvoker,' +
  ' routeFocus: ppRouteScreenFocus, entry: ppScreenEntryTarget,' +
  ' patternsAt: ppPatternsLocation, caseLessonAt: ppCaseLessonLocation,' +
  ' openFiltered: ppOpenPatternsFiltered, openLemmaScreen: ppOpenPatternsLemma,' +
  ' openCaseLesson: ppOpenCaseLesson, cardClaim: ppCardPatternClaim,' +
  ' openIndex: ppOpenPatternsIndex, openCardPattern: ppOpenCardPattern,' +
  ' renderCardPattern: ppRenderCardPattern, continuation: gPatternContinuation,' +
  ' renderGrammarLink: gRenderPatternLink,' +
  ' nextInvoker: function(){ return ppNextScreenInvoker; },' +
  ' back: function(){ $("pBack").fire("click"); } };')(
  fakeDocument, fakeWindow, lookup, FAKE_LEVELS, PP_VERB_PATTERNS, uiEnv);

function allNodes() { return pBody.descendants(); }
function nodesWithClass(cls) {
  return allNodes().filter(function (node) { return node.classList && node.classList.contains(cls); });
}
function filterButton(id) {
  return nodesWithClass('vp-filter').filter(function (node) {
    return node.getAttribute('data-vp-filter') === id;
  })[0] || null;
}
function textsOf(cls) {
  return nodesWithClass(cls).map(function (node) { return node.textContent; });
}
function tagsUsed() {
  var seen = {};
  allNodes().forEach(function (node) { if (node.tag) seen[node.tag] = true; });
  return Object.keys(seen).sort();
}

injectFixture();
UI.startPatterns(0, 0);
eq('I1 entering the surface shows the screen once, with focus deferred to the renderer',
   uiEnv.shows, [['patterns', true]]);
ok('I1 the renderer focuses the screen heading on entry', fakeDocument.activeElement === pTitle);
eq('I1 the heading is given a programmatic focus target', pTitle.getAttribute('tabindex'), '-1');
eq('I1 the title names the surface, not a lemma', pTitle.textContent, 'Verb Patterns');
eq('I1 the index is the default view', UI.P.view, 'index');
eq('I1 no filter is applied on entry', UI.P.filter, 'all');
eq('I2 the index renders every lemma exactly once',
   textsOf('vp-row-lemma').length, 6);
eq('I2 the index rows are the canonical A-Z list', textsOf('vp-row-lemma'),
   ['bezokolicznikować', 'fikcjonować',
    'konstrukcjować (synthetic-nonrelease display form, deliberately long)',
    'metodować', 'podobnikować się', 'zetafikcjonować się']);
eq('I2 each lemma row is a native button with a 44px target class',
   nodesWithClass('vp-row').map(function (node) { return node.tag; }),
   ['button', 'button', 'button', 'button', 'button', 'button']);
eq('I2 the Polish lemma carries its own language attribute',
   nodesWithClass('vp-row-lemma').map(function (node) { return node.getAttribute('lang'); }),
   ['pl', 'pl', 'pl', 'pl', 'pl', 'pl']);
eq('I2 letter headings group the list', textsOf('vp-letter'), ['B', 'F', 'K', 'M', 'P', 'Z']);
eq('I2 the index row says how many patterns the verb has, and shows no chip',
   [textsOf('vp-row-count'), nodesWithClass('vp-chip').length],
   [['2 patterns', '1 pattern', '1 pattern', '3 patterns', '1 pattern', '2 patterns'], 0]);
eq('I2 the count line reports verbs and patterns', textsOf('vp-count'), ['6 verbs · 10 patterns']);
eq('I3 the filter row is eight native buttons that wrap',
   nodesWithClass('vp-filter').map(function (node) { return node.tag; }),
   ['button', 'button', 'button', 'button', 'button', 'button', 'button', 'button']);
eq('I3 every filter button carries aria-pressed, and exactly one is pressed',
   nodesWithClass('vp-filter').map(function (node) { return node.getAttribute('aria-pressed'); }),
   ['true', 'false', 'false', 'false', 'false', 'false', 'false', 'false']);
eq('I3 the filter group is labelled', [pBody.querySelector('.vp-filters').getAttribute('role'),
   pBody.querySelector('.vp-filters').getAttribute('aria-labelledby')], ['group', 'pFilterLabel']);
eq('I3 the visible label is inside the accessible name',
   nodesWithClass('vp-filter').map(function (node) {
     return node.getAttribute('aria-label') === null && node.children[0].textContent.length > 0;
   }), [true, true, true, true, true, true, true, true]);
eq('I3 Polish filter names stay in Polish-language child nodes',
   nodesWithClass('vp-filter').slice(1, 7).map(function (node) {
     var name = node.querySelector('.sr-only');
     return [name && name.getAttribute('lang'), name && name.textContent];
   }), [['pl', ' (Mianownik)'], ['pl', ' (Dopełniacz)'], ['pl', ' (Celownik)'],
         ['pl', ' (Biernik)'], ['pl', ' (Narzędnik)'], ['pl', ' (Miejscownik)']]);

// Filtering happens in place: the pressed control keeps focus.
var genitiveButton = filterButton('genitive');
genitiveButton.focus();
var focusBefore = fakeDocument.activeElement;
genitiveButton.fire('click');
ok('I4 applying a filter does not steal focus from the control that was pressed',
   fakeDocument.activeElement === focusBefore && focusBefore === genitiveButton);
eq('I4 the filter state moved', UI.P.filter, 'genitive');
eq('I4 aria-pressed follows the active filter',
   nodesWithClass('vp-filter').filter(function (node) {
     return node.getAttribute('aria-pressed') === 'true';
   }).map(function (node) { return node.getAttribute('data-vp-filter'); }), ['genitive']);
eq('I4 the filtered result count is announced once, atomically',
   pStatus.textContent, '1 verb · 1 pattern with Dopełniacz (Genitive)');
eq('I4 the sub-title names the filtered view in both languages',
   pSub.textContent, 'Dopełniacz (Genitive)');
eq('I4 the sub-title and live count preserve their Polish language part',
   [pSub.children[0].getAttribute('lang'), pSub.children[0].textContent,
    pStatus.children[0].children[1].getAttribute('lang')],
   ['pl', 'Dopełniacz', 'pl']);
eq('I4 the filtered list shows the matching pattern as a summary row',
   [textsOf('vp-row-lemma'), textsOf('vp-chip')],
   [['zetafikcjonować się'], ['kogo? czego? · Genitive (matches this filter)']]);
eq('I4 a filtered row still renders no explanation, example or link',
   [nodesWithClass('vp-explain').length, nodesWithClass('vp-example').length], [0, 0]);
eq('I4 the match is stated in text, not only in weight or colour',
   nodesWithClass('vp-chip').map(function (chip) {
     var match = chip.querySelector('.sr-only');
     return match ? match.textContent : null;
   }).filter(function (text) { return text; }),
   [' (matches this filter)']);
eq('I4 no letter headings in a filtered result list', textsOf('vp-letter'), []);

// A two-complement pattern keeps its whole frame under either of its cases.
filterButton('locative').fire('click');
eq('I5 filtering by Locative keeps the complete Dative+Locative frame',
   textsOf('vp-chip').filter(function (text) { return text.indexOf('Dative') !== -1; }),
   ['komu? czemu? · Dative']);
eq('I5 both chips of that frame are present, with the matched one marked',
   nodesWithClass('vp-row').filter(function (row) {
     return row.querySelectorAll('.vp-chip').length === 2;
   }).map(function (row) {
     return row.querySelectorAll('.vp-chip').map(function (chip) {
       return chip.classList.contains('is-match');
     });
   }), [[false, true]]);
filterButton('no-case').fire('click');
eq('I6 the no-case filter makes infinitive and clause patterns discoverable',
   textsOf('vp-chip'),
   ['+ bezokolicznik · Infinitive (matches this filter)',
    'komu? czemu? · Dative', '+ że … · Clause (matches this filter)']);
filterButton('all').fire('click');
eq('I6 returning to All restores the canonical index', textsOf('vp-row-lemma').length, 6);

// The lemma entry: the one canonical owner.
var multiRow = nodesWithClass('vp-row').filter(function (row) {
  return row.textContent.indexOf('metodować') === 0;
})[0];
multiRow.fire('click');
eq('I7 opening a lemma stays on the same screen and adds no history entry',
   [uiEnv.shows.length, UI.P.view], [1, 'lemma']);
eq('I7 focus moves to the lemma heading and is revealed',
   [fakeDocument.activeElement.className, fakeDocument.activeElement.revealCount],
   ['vp-lemma-head', 1]);
eq('I7 the lemma heading is a level-2 heading, in Polish, programmatically focusable',
   [fakeDocument.activeElement.tag, fakeDocument.activeElement.getAttribute('lang'),
    fakeDocument.activeElement.getAttribute('tabindex')], ['h2', 'pl', '-1']);
eq('I7 the header title becomes the lemma', [pTitle.textContent, pTitle.getAttribute('lang')],
   ['metodować', 'pl']);
eq('I7 the aspect is shown, and no editorial vocabulary with it', pSub.textContent, 'imperfective');
eq('I7 entering a lemma retires the prior filter announcement', pStatus.textContent, '');
eq('I8 all three sibling patterns are rendered, none behind a toggle',
   nodesWithClass('vp-pattern').length, 3);
eq('I8 the meaning is a level-3 heading under the lemma',
   nodesWithClass('vp-meaning-head').map(function (node) { return node.tag; }), ['h3']);
eq('I8 each pattern is a labelled section, not a heading',
   nodesWithClass('vp-pattern').map(function (node) {
     return node.tag + ':' + (node.getAttribute('aria-labelledby') || '').slice(0, 9);
   }), ['section:pPattern0', 'section:pPattern0', 'section:pPattern0']);
eq('I8 the headline is generated from the lemma plus one token per complement',
   textsOf('vp-headline'),
   ['metodować czym?', 'metodować o czym?', 'metodować komu? w czym?']);
eq('I8 the chips are the whole frame, in authored order, each with its role line',
   textsOf('vp-chip'),
   ['kim? czym? · Instrumental', 'o kim? o czym? · Locative',
    'komu? czemu? · Dative', 'w kim? w czym? · Locative']);
eq('I8 every chip carries its plain-English role phrase',
   textsOf('vp-role'),
   ['how it is done', 'what it is about', 'the person who receives it',
    'what is learned, said or done']);
eq('I8 the chip list is a real list, and no chip is a control',
   [pBody.querySelector('.vp-chips').tag,
    nodesWithClass('vp-chip-item').map(function (node) { return node.tag; }).join(','),
    nodesWithClass('vp-chip').filter(function (node) { return node.tag === 'button'; }).length],
   ['ul', 'li,li,li,li', 0]);
eq('I8 only the recognition level is badged, and the badge says what it means',
   [textsOf('vp-badge'), nodesWithClass('vp-badge').map(function (node) {
     return node.getAttribute('aria-label');
   })], [['A2', 'A2', 'B1'],
         ['Recognise from A2', 'Recognise from A2', 'Recognise from B1']]);
eq('I9 an example is rendered when the pattern has one, in both languages',
   [nodesWithClass('vp-example').length, textsOf('vp-example-pl').length,
    nodesWithClass('vp-example-pl')[0].getAttribute('lang')], [1, 1, 'pl']);
eq('I9 a pattern with no example renders no example box and no placeholder', (function () {
  var text = pBody.textContent;
  return [nodesWithClass('vp-example').length,
          text.indexOf('TODO'), text.indexOf('coming soon'), text.indexOf('await')];
})(), [1, -1, -1, -1]);
eq('I9 long runtime strings are rendered in full, to be wrapped by CSS rather than cut',
   nodesWithClass('vp-explain').filter(function (node) {
     return node.textContent.length > 200;
   }).length, 1);

// Hostile runtime text is data, never markup.
eq('I10 hostile runtime text is rendered as text, verbatim', (function () {
  var hostile = '<img src=x onerror="window.__vpPwned=1"></span><script>window.__vpPwned=1</script>';
  return [pBody.textContent.indexOf(hostile) !== -1,
          tagsUsed().indexOf('img'), tagsUsed().indexOf('script')];
})(), [true, -1, -1]);
// AMENDED by Priority 7 Phase 3C: `button` joins the set, because the lemma
// entry now carries the one route back to the case lesson.  The property being
// asserted is unchanged - nothing arrived that the renderer did not create, and
// no markup was parsed out of runtime text.
eq('I10 the rendered tree contains only the element types the renderer created',
   tagsUsed(), ['button', 'div', 'h2', 'h3', 'li', 'p', 'section', 'span', 'ul']);
eq('I10 no runtime identifier appears anywhere in the rendered tree, text or attribute',
   ['vp-l-', 'vp-m-', 'vp-p-', 'vp-e-', 'vp-x-'].filter(function (prefix) {
     var payload = pBody.textContent + ' ' + allNodes().map(function (node) {
       return Object.keys(node.attrs || {}).map(function (name) {
         return name + '=' + node.attrs[name];
       }).join(' ') + ' ' + (node.className || '') + ' ' + (node.id || '');
     }).join(' ');
     return payload.indexOf(prefix) !== -1;
   }), []);
eq('I10 nothing in the tree carries an event-handler attribute',
   allNodes().filter(function (node) {
     return Object.keys(node.attrs || {}).some(function (name) {
       return name.slice(0, 2) === 'on';
     });
   }).length, 0);

// Back is two steps, and focus comes back with it.
UI.back();
eq('I11 Back from a lemma returns to the index without leaving the surface',
   [UI.P.view, uiEnv.shows.length], ['index', 1]);
eq('I11 focus returns to the row that was opened',
   [fakeDocument.activeElement.className,
    fakeDocument.activeElement.textContent.indexOf('metodować')], ['vp-row', 0]);
eq('I11 the filter survives the round trip', UI.P.filter, 'all');
eq('I11 the header title returns to the surface name',
   [pTitle.textContent, pTitle.getAttribute('lang')], ['Verb Patterns', null]);
UI.back();
eq('I11 Back from the index leaves the surface for home',
   uiEnv.shows[uiEnv.shows.length - 1], ['home', undefined]);

// A filter applied, then a lemma opened, then Back: the filtered view returns.
UI.startPatterns(0, 0, 'dative');
eq('I12 a deep-linked case filter is state on entry, not a navigation step',
   [UI.P.filter, uiEnv.shows[uiEnv.shows.length - 1]], ['dative', ['patterns', true]]);
eq('I12 an unknown deep-link filter falls back to the canonical index', (function () {
  UI.startPatterns(0, 0, 'ablative');
  return UI.P.filter;
})(), 'all');

// Phase 3E correction pass: the index row was already protected, but the same
// runtime lemma and gloss must remain safe after the learner opens the detail.
var detailToken = 'fikcjo' + new Array(361).join('x');
var detailGloss = 'meaning' + new Array(361).join('y');
var longDetailDoc = clone(WRAPPED_FIXTURE.runtimeProjection);
longDetailDoc.lemmas.filter(function (lemma) {
  return lemma.canonicalLemma === 'fikcjonować';
})[0].displayLemma = detailToken;
longDetailDoc.lemmas.filter(function (lemma) {
  return lemma.canonicalLemma === 'fikcjonować';
})[0].meanings[0].glossesEn = [detailGloss];
ok('I13-E the long-token detail runtime remains a valid public shape',
   PP_VERB_PATTERNS.__acceptForTest(longDetailDoc));
UI.startPatterns(0, 0);
var longDetailRow = nodesWithClass('vp-row').filter(function (row) {
  return row.textContent.indexOf(detailToken) === 0;
})[0];
ok('I13-E the long-token lemma is reachable from its real index row', !!longDetailRow);
longDetailRow.fire('click');
eq('I13-E the detail renders the complete long lemma and gloss without truncation',
   [textsOf('vp-lemma-head'), textsOf('vp-meaning-head')],
   [[detailToken], [detailGloss]]);

// One lemma contributes two distinct Locative rows in the committed fixture.
// Their lemma key is deliberately the same. The locked renderer boundary strips
// runtime IDs, so deterministic sorted meaning/pattern positions are the stable
// JS-only rendered-origin descriptor that distinguishes them.
injectFixture();
UI.startPatterns(0, 0, 'locative');
var duplicateRows = nodesWithClass('vp-row');
eq('I14-E the Locative filter has two distinct rows for the same lemma',
   [duplicateRows.length,
    duplicateRows.map(function (row) { return row.getAttribute('data-vp-row'); }),
    duplicateRows.map(function (row) {
      var ref = row._vpRowRef;
      return [ref.lemmaKey, ref.meaningIndex, ref.patternIndex];
    })],
   [2, ['3', '3'], [[3, 0, 1], [3, 0, 2]]]);
duplicateRows[0].fire('click');
UI.back();
eq('I14-E Back from the first duplicate restores the first row and filter',
   [UI.P.filter, fakeDocument.activeElement === nodesWithClass('vp-row')[0]],
   ['locative', true]);
nodesWithClass('vp-row')[1].fire('click');
UI.back();
eq('I14-E Back from the second duplicate restores that exact second row',
   [UI.P.filter, fakeDocument.activeElement === nodesWithClass('vp-row')[1]],
   ['locative', true]);

// A vanished exact descriptor must not degrade into "first duplicate wins".
nodesWithClass('vp-row')[1].fire('click');
UI.P.lastRowRef = { lemmaKey: 3, meaningIndex: 99, patternIndex: 99 };
UI.back();
eq('I14-E a missing exact duplicate falls back to the index heading, not another row',
   [fakeDocument.activeElement === pTitle,
    nodesWithClass('vp-row').indexOf(fakeDocument.activeElement)], [true, -1]);

// Unique filtered rows and the canonical All index keep their established path.
UI.startPatterns(0, 0, 'genitive');
nodesWithClass('vp-row')[0].fire('click');
UI.back();
eq('I14-E a unique filtered row still restores normally',
   [UI.P.filter, fakeDocument.activeElement === nodesWithClass('vp-row')[0]],
   ['genitive', true]);
UI.startPatterns(0, 0);
var allOrigin = nodesWithClass('vp-row')[2];
allOrigin.fire('click');
UI.back();
eq('I14-E the All-verbs index still restores its unique lemma row',
   [UI.P.filter, fakeDocument.activeElement === nodesWithClass('vp-row')[2]],
   ['all', true]);

// I15. The recognition-only badge: its wording, and the guard that decides who
// gets one. The badge is carried entirely by its TEXT - colour is decoration -
// so the text is asserted on every surface that can show it, and the guard is
// asserted by the patterns that must NOT carry it. Nothing here reads the
// editorial term: the shipping loader derives `recognitionOnly` and the
// renderer only obeys it.
UI.startPatterns(0, 0);
eq('I15 the canonical A-Z index badges nobody: its rows are lemmas, not patterns',
   [nodesWithClass('vp-row').length, nodesWithClass('vp-recognition').length], [6, 0]);
UI.startPatterns(0, 0, 'dative');
eq('I15 a filtered row is badged only where that pattern is recognition-only',
   [textsOf('vp-row-lemma'), textsOf('vp-recognition')],
   [['bezokolicznikować', 'metodować', 'podobnikować się'], ['Understand for now']]);
eq('I15 the badge lands on the recognition-only row and on no other',
   nodesWithClass('vp-row').map(function (node) {
     return node.textContent.indexOf('Understand for now') !== -1;
   }), [false, false, true]);
UI.startPatterns(0, 0);
UI.openLemma(lemmaKeyFor('metodować'));
eq('I15 an all-active-production lemma renders no recognition badge at all',
   [nodesWithClass('vp-pattern').length, nodesWithClass('vp-recognition').length], [3, 0]);
UI.openLemma(lemmaKeyFor('zetafikcjonować się'));
eq('I15 a mixed lemma badges its recognition-only pattern and only that one',
   [nodesWithClass('vp-pattern').length, textsOf('vp-recognition')],
   [2, ['Understand for now']]);
eq('I15 the badge is plain text: not a control, not hidden, no separate name',
   (function () {
     var chip = nodesWithClass('vp-recognition')[0];
     return [chip.tag, chip.className, chip.getAttribute('aria-hidden'),
             chip.getAttribute('aria-label')];
   })(), ['span', 'usage-badge u-recognition vp-recognition', null, null]);
eq('I15 the retired label reaches no rendered surface',
   [pBody.textContent.indexOf('Understand this one'),
    pBody.textContent.indexOf('Understand for now') !== -1], [-1, true]);

// =========================================================================
// J. THE SHIPPING PATH: no runtime data, and the surface still works.
// This is the state the application is actually in at this tree - ordinary
// startup, no injection, nothing fetched, nothing read from tests/.
// =========================================================================
PP_VERB_PATTERNS.reset();
uiEnv.shows = [];
eq('J0 ordinary startup builds the entry with no data and no request',
   (function () {
     var topics = Function('PP_VERB_PATTERNS',
       extractFunction(INDEX, 'patternIndexTopics') + '\nreturn patternIndexTopics();')(
       PP_VERB_PATTERNS);
     return [topics.length, topics[0].name, topics[0].kind, topics[0].surface,
             topics[0].searchText];
   })(), [1, 'Verb Patterns', 'patterns', 'verb-index', '']);
eq('J0 the tile is honest about having nothing to list yet', (function () {
  var count = Function('PP_VERB_PATTERNS', 'poolFor', 'convoLen',
    extractFunction(INDEX, 'tCount') + '\nreturn tCount;')(
    PP_VERB_PATTERNS, function () { return []; }, function () { return 0; });
  return count(PATTERN_TOPIC, { level: 'Verb Patterns' }, { progress: {} });
})(), 'Not ready yet');
eq('J0 the routing precondition still recognises the surface with no data',
   UI.ready(PATTERN_TOPIC), true);
calls = [];
var noDataRoute = ROUTING.openTopic(0, 0, PATTERN_TOPIC);
eq('J0 activating it is a successful route, not an unknown-kind failure',
   [noDataRoute, calls], [true, ['startPatterns']]);
fakeDocument.activeElement = tileEl;
UI.startPatterns(0, 0);
eq('J0 the screen is shown once, with focus deferred to the renderer',
   uiEnv.shows, [['patterns', true]]);
ok('J0 screen-entry focus lands on the screen heading',
   fakeDocument.activeElement === pTitle);
eq('J0 the title names the surface', pTitle.textContent, 'Verb Patterns');
eq('J1 an unavailable surface still renders a complete, calm screen',
   [nodesWithClass('vp-row').length, nodesWithClass('vp-filter').length], [0, 0]);
ok('J1 the unavailable copy is learner-facing and blames nothing',
   pBody.textContent.indexOf('isn’t ready to open yet') !== -1);
eq('J1 the unavailable copy exposes nothing internal', (function () {
  var text = pBody.textContent + ' ' + pStatus.textContent;
  return ['research', 'review', 'approv', 'corpus', 'editorial', 'error', 'failed',
          'fixture', 'JSON', 'loader'].filter(function (token) {
    return text.toLowerCase().indexOf(token.toLowerCase()) !== -1;
  });
})(), []);
ok('J1 the unavailable state is announced', pStatus.textContent.length > 0);
ok('J1 focus still lands somewhere real', fakeDocument.activeElement === pTitle);
eq('J1 nothing was read from a fixture or an editorial file to reach this state',
   [countOf(PATTERNS_CODE, 'fixture'), countOf(PATTERNS_CODE, 'editorial'),
    countOf(PATTERNS_CODE, '__acceptForTest'), countOf(PATTERNS_CODE, 'JSON.parse')],
   [0, 0, 0, 0]);
eq('J1 the precondition refuses a topic with the wrong surface key, data or not',
   [UI.ready({ kind: 'patterns', surface: 'something-else' }), UI.ready({}),
    UI.ready(null), UI.ready({ surface: 'verb-index' })],
   [false, false, false, false]);
// Leaving the no-data surface must return focus like any other screen.
UI.back();
eq('J2 Back from the no-data surface leaves for home',
   uiEnv.shows[uiEnv.shows.length - 1], ['home', undefined]);
// Return focus runs through the shipping helpers, not a re-implementation: the
// invoker is remembered against the #patterns screen id on the way in and
// restored by ppRouteScreenFocus on the way out. (show()/showScreen() themselves
// are owned by test_phase1b_keyboard_focus.js and test_phase3b_focus_scroll.js.)
eq('J2 startPatterns defers focus so the screen transition cannot steal it',
   hasCode(extractFunction(INDEX, 'startPatterns'), 'show("patterns", true);'), true);
eq('J2 the invoking tile is remembered against this screen and restored on exit',
   (function () {
     fakeDocument.activeElement = tileEl;
     UI.remember('patterns');
     var before = tileEl.focusCount;
     var restored = UI.routeFocus(patternsScreen, homeScreen);
     return [restored === tileEl, fakeDocument.activeElement === tileEl,
             tileEl.focusCount - before];
   })(), [true, true, 1]);
// Same surface, same code: injection populates it, and creates nothing new.
injectFixture();
UI.startPatterns(0, 0);
eq('J3 the SAME screen and the SAME renderers now show the populated index',
   [nodesWithClass('vp-row').length, nodesWithClass('vp-filter').length,
    pBody.parentElement === patternsScreen], [6, 8, true]);
eq('J3 injection creates no second surface, level or topic',
   [countOf(INDEX, '<section class="screen" id="patterns">'),
    countOf(INDEX, 'level:"Verb Patterns"'), countOf(LOADER_SRC, 'createElement'),
    countOf(LOADER_SRC, 'LEVELS.push') + countOf(LOADER_SRC, 'PP_LEVELS')],
   [1, 1, 0, 0]);
eq('J3 the populated surface is reached through the same routing branch',
   (function () {
     var run = routeAttempt(PATTERN_TOPIC);
     return [run.result, run.calls];
   })(), [true, ['startPatterns']]);
eq('J3 and the loader still refuses the wrapper it was fed from',
   PP_VERB_PATTERNS.acceptRuntimeDocument(WRAPPED_FIXTURE), false);
injectFixture();

// =========================================================================
// K. Home integration: the topic tile, the count and the search string.
// =========================================================================
var TOPICS_FN = Function('PP_VERB_PATTERNS', extractFunction(INDEX, 'patternIndexTopics') +
  '\nreturn patternIndexTopics();')(PP_VERB_PATTERNS);
eq('K1 the level contributes exactly one topic - the index', TOPICS_FN.length, 1);
eq('K1 the topic is recognisable as the reference surface',
   [TOPICS_FN[0].name, TOPICS_FN[0].kind, TOPICS_FN[0].chip], ['Verb Patterns', 'patterns', 'Reference']);
eq('K1 the topic carries no cards, drills, scenes or mixOf', [
  TOPICS_FN[0].cards, TOPICS_FN[0].drills, TOPICS_FN[0].scenes, TOPICS_FN[0].mixOf
], [undefined, undefined, undefined, undefined]);
eq('K1 the topic carries no identifier of any kind',
   [TOPICS_FN[0].id, JSON.stringify(TOPICS_FN[0]).indexOf('vp-')], [undefined, -1]);
var HAY_BLOCK = sliceBetween(INDEX, 'const HAY = new WeakMap();', 'function getVisibleTopics()');
var HAYSTACK = Function('WeakMap', HAY_BLOCK + '\nreturn topicHaystack;')(WeakMap);
eq('K2 nothing identifier-shaped becomes searchable',
   HAYSTACK(TOPICS_FN[0]).indexOf('vp-'), -1);
ok('K2 the searchable text still finds a verb, a case and a question',
   HAYSTACK(TOPICS_FN[0]).indexOf('metodować') !== -1 &&
   HAYSTACK(TOPICS_FN[0]).indexOf('genitive') !== -1 &&
   HAYSTACK(TOPICS_FN[0]).indexOf('dopełniacz') !== -1 &&
   HAYSTACK(TOPICS_FN[0]).indexOf('kogo? czego?') !== -1);
var T_COUNT = Function('PP_VERB_PATTERNS', 'poolFor', 'convoLen',
  extractFunction(INDEX, 'tCount') + '\nreturn tCount;')(
  PP_VERB_PATTERNS, function () { return []; }, function () { return 0; });
eq('K3 the tile count names verbs and patterns, and never reads undefined cards',
   T_COUNT(TOPICS_FN[0], { level: 'Verb Patterns' }, { progress: {} }),
   '6 verbs · 10 patterns');
eq('K3 an unknown kind can no longer reach the card branch of the count',
   /kind==="patterns"/.test(squash(extractFunction(INDEX, 'tCount'))), true);
eq('K4 the pattern topic can never enter a typed or listening pool',
   hasCode(INDEX, 'const VOCAB_SRC = LEVELS.filter(lv => lv.topics.length>0 && lv.topics.every(t=> !t.kind));'),
   true);
eq('K4 no Quiz pill can appear on a reference row',
   hasCode(INDEX, 'const showPill = (!t.kind || t.kind==="podcast") && t.cards && !t.mature;'), true);

// =========================================================================
// L. Nothing is persisted, and no new key appears.
// =========================================================================
eq('L1 the reference surface writes no progress and reads no store',
   [countOf(PATTERNS_CODE, 'loadV2'), countOf(PATTERNS_CODE, 'saveV2'),
    countOf(PATTERNS_CODE, 'STORE_KEY'), countOf(PATTERNS_CODE, 'localStorage')],
   [0, 0, 0, 0]);
// The traversal above - enter, filter four times, open two lemmas, go back twice,
// re-enter with a filter, hit the unavailable state - ran to completion in an
// environment where no storage object exists at all. Any read or write would have
// thrown a ReferenceError and failed this suite loudly, so "no progress byte
// changed" is not an assertion about intent here: it is the only way the run
// could have finished.
eq('L1 the whole traversal completed with no storage object in scope',
   [typeof localStorage, typeof sessionStorage, typeof indexedDB],
   ['undefined', 'undefined', 'undefined']);
eq('L1 the loader touches no storage API',
   [countOf(LOADER_SRC, 'localStorage'), countOf(LOADER_SRC, 'sessionStorage'),
    countOf(LOADER_SRC, 'indexedDB'), countOf(LOADER_SRC, 'document.cookie')],
   [0, 0, 0, 0]);
eq('L1 the loader owns no global/network API and only calls its injected request once',
   [countOf(LOADER_SRC, 'fetch('), countOf(LOADER_SRC, 'XMLHttpRequest'),
    countOf(LOADER_SRC, 'import('), countOf(LOADER_SRC, 'request(url, { cache: "no-store" })')],
   [0, 0, 0, 1]);
eq('L2 the progress schema and migration revision are untouched',
   [/schemaVersion:PP_MIGRATE\.SCHEMA_VERSION/.test(INDEX),
    countOf(INDEX, 'PP_MIGRATE.CONTENT_MIGRATION_REVISION') > 0], [true, true]);
// Advanced by Priority 7 Phase 4F-I1, the release that ships this surface.
eq('L2 the app version is the 8.11 release',
   (INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1], '8.11');
eq('L3 no analytics, telemetry, cookie or identifier was introduced',
   [countOf(PATTERNS_CODE, 'gtag'), countOf(PATTERNS_CODE, 'analytics'),
    countOf(PATTERNS_CODE, 'cookie'), countOf(PATTERNS_CODE, 'navigator.send'),
    countOf(LOADER_SRC, 'analytics'), countOf(LOADER_SRC, 'cookie')],
   [0, 0, 0, 0, 0, 0]);

// =========================================================================
// M. PHASE 3C - the cross-links and the vocabulary-card pointer.
//
//   M1  the static case map, both directions, independent of any runtime
//   M2  Grammar -> Verb Patterns: one continuation, seven topics, no copying
//   M3  the case-filter deep link, with data and without
//   M4  Verb Patterns -> Grammar: the reverse link, and where it is absent
//   M5  card derivation: the eight required safety cases
//   M6  card-back rendering: chip / doorway / nothing
//   M7  interaction, focus and the invoker hand-over
//   M8  layout, mobile and the pinned CSS constraints
//   M9  the shipping path: no runtime, no pointer, no request
// =========================================================================

// ---- fake DOM for the two new host surfaces -----------------------------
var studyScreen = register(new El('section', 'study'));
studyScreen.classList.add('screen');
studyScreen.classList.add('active');
fakeDocument.body.appendChild(studyScreen);
var patternLine = register(new El('div', 'patternLine'));
patternLine.classList.add('pair-line');
patternLine.hidden = true;
var patternK = register(new El('span', 'patternK'));
patternK.classList.add('pair-k');
patternK.textContent = 'Pattern';
var patternLink = register(new El('button', 'patternLink'));
patternLink.classList.add('vp-card-link');
patternLine.appendChild(patternK);
patternLine.appendChild(patternLink);
studyScreen.appendChild(patternLine);

var grammarScreen = register(new El('section', 'grammar'));
grammarScreen.classList.add('screen');
grammarScreen.classList.add('active');
fakeDocument.body.appendChild(grammarScreen);
var gPatternLine = register(new El('div', 'gPatternLine'));
gPatternLine.classList.add('vp-continue-line');
gPatternLine.hidden = true;
var gPatternLink = register(new El('button', 'gPatternLink'));
gPatternLink.classList.add('vp-continue');
var gPatternLabel = register(new El('span', 'gPatternLabel'));
var gPatternCaseName = register(new El('span', 'gPatternCaseName'));
gPatternCaseName.classList.add('sr-only');
gPatternCaseName.setAttribute('lang', 'pl');
gPatternLink.appendChild(gPatternLabel);
gPatternLink.appendChild(gPatternCaseName);
gPatternLine.appendChild(gPatternLink);
grammarScreen.appendChild(gPatternLine);

function cardLinkNodes() { return patternLink.descendants(); }
function cardLinkClasses(cls) {
  return cardLinkNodes().filter(function (node) {
    return node.classList && node.classList.contains(cls);
  });
}

// A synthetic document builder that can attach references to ANY pattern of the
// fixture, addressed by its invented lemma. Every reference in every test below
// is created here: no real vocabulary card and no real pattern is involved, and
// the committed fixture on disk still carries no contentRefs at all.
function refDoc(assign) {
  var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
  doc.lemmas.forEach(function (lemma) {
    lemma.meanings.forEach(function (meaning) {
      meaning.patterns.forEach(function (pattern) { delete pattern.contentRefs; });
    });
  });
  function attach(canonical, mi, pi, refs) {
    doc.lemmas.forEach(function (lemma) {
      if (lemma.canonicalLemma !== canonical) return;
      lemma.meanings[mi].patterns[pi].contentRefs = refs;
    });
  }
  if (assign) assign(attach, doc);
  return PP_VERB_PATTERNS.__acceptForTest(doc);
}
var CARD_ID = 'p7-fixture-card-back-001';
function supportRef(id) { return { kind: 'card', id: id || CARD_ID, purpose: 'support' }; }
function contrastRef(id) { return { kind: 'card', id: id || CARD_ID, purpose: 'contrast' }; }
// Synthetic cards. These are test objects, not repository content: no real card
// id, no real Polish, and nothing here is written to any data file.
function fakeCard(over) {
  var card = { id: CARD_ID, pl: 'fikcjonować', en: 'SYNTHETIC-NONRELEASE: to act on' };
  if (over) { for (var key in over) { if (Object.prototype.hasOwnProperty.call(over, key)) card[key] = over[key]; } }
  return card;
}

// -------------------------------------------------------------------------
// M1. The static case map: two directions, one table, no runtime dependency.
// -------------------------------------------------------------------------
PP_VERB_PATTERNS.reset();
// Vocative can occur as NEITHER a direct nor a prepositional complement - the
// editorial validator refuses one - so no pattern under this contract can carry
// it, there is no filtered view for it to open, and it therefore offers no
// continuation at all.  The other six do.
eq('M1 every case that CAN occur as a complement resolves to its case',
   CASE_NAMES.map(function (name) {
     var link = PP_VERB_PATTERNS.caseFilterFor('grammar-cases-' + name);
     return link ? link.caseId + '|' + link.filter : null;
   }),
   ['nominative|nominative', 'genitive|genitive', 'dative|dative',
    'accusative|accusative', 'instrumental|instrumental', 'locative|locative',
    null]);
eq('M1 Vocative offers no continuation, because no pattern can carry it',
   [PP_VERB_PATTERNS.caseFilterFor('grammar-cases-vocative'),
    PP_VERB_PATTERNS.caseMeta('vocative').direct,
    PP_VERB_PATTERNS.caseMeta('vocative').prepositional], [null, false, false]);
eq('M1 the Vocative lesson and the central case metadata are untouched',
   [PP_VERB_PATTERNS.caseMeta('vocative').pl, PP_VERB_PATTERNS.caseMeta('vocative').en,
    PP_VERB_PATTERNS.caseLessonFor('vocative').topicId,
    PP_VERB_PATTERNS.CASE_ORDER.indexOf('vocative')],
   ['Wołacz', 'Vocative', 'grammar-cases-vocative', 6]);
// The wording must not assert that every occurrence of a case is a governed
// object: a Nominative subject and a constructional frame are neither.
eq('M1 the continuation wording claims no government',
   PP_VERB_PATTERNS.caseFilterFor('grammar-cases-genitive').label,
   'Verb patterns with the Genitive');
eq('M1 its accessible name adds the Polish case name around the visible one',
   PP_VERB_PATTERNS.caseFilterFor('grammar-cases-genitive').srLabel,
   'Verb patterns with the Genitive (Dopełniacz)');
eq('M1 no continuation anywhere says a verb TAKES the case',
   CASE_NAMES.filter(function (name) {
     var link = PP_VERB_PATTERNS.caseFilterFor('grammar-cases-' + name);
     return link && (/take/.test(link.label) || /take/.test(link.srLabel));
   }), []);
eq('M1 the overstated wording is gone from every shipping file',
   [countOf(LOADER_SRC, 'Verbs that take the'), countOf(INDEX, 'Verbs that take the'),
    countOf(readFile(ROOT + 'data-grammar.js'), 'Verbs that take the')], [0, 0, 0]);
eq('M1 the visible label is contained in the accessible name everywhere',
   CASE_NAMES.filter(function (name) {
     var link = PP_VERB_PATTERNS.caseFilterFor('grammar-cases-' + name);
     return link && link.srLabel.indexOf(link.label) === -1;
   }), []);
eq('M1 anything that is not one of the seven case topics resolves to nothing',
   [PP_VERB_PATTERNS.caseFilterFor('grammar-cases'),
    PP_VERB_PATTERNS.caseFilterFor('grammar-cases-genitive-014'),
    PP_VERB_PATTERNS.caseFilterFor('a1-first-verbs'),
    PP_VERB_PATTERNS.caseFilterFor('grammar-verbs-aspect'),
    PP_VERB_PATTERNS.caseFilterFor(''), PP_VERB_PATTERNS.caseFilterFor(null),
    PP_VERB_PATTERNS.caseFilterFor(undefined), PP_VERB_PATTERNS.caseFilterFor(7),
    PP_VERB_PATTERNS.caseFilterFor('constructor'),
    PP_VERB_PATTERNS.caseFilterFor('toString')],
   [null, null, null, null, null, null, null, null, null, null]);
eq('M1 the reverse direction names the lesson that owns each case',
   CASE_NAMES.map(function (name) {
     return PP_VERB_PATTERNS.caseLessonFor(name).topicId;
   }),
   CASE_NAMES.map(function (name) { return 'grammar-cases-' + name; }));
// The REVERSE label is unchanged by this correction: "Learn the Genitive"
// names a lesson, and a lesson does take a name.
eq('M1 the back-link wording points at the lesson, never at a copy of it',
   [PP_VERB_PATTERNS.caseLessonFor('genitive').label,
    PP_VERB_PATTERNS.caseLessonFor('genitive').srLabel,
    PP_VERB_PATTERNS.caseLessonFor('locative').label],
   ['Learn the Genitive', 'Learn the Genitive (Dopełniacz)', 'Learn the Locative']);
eq('M1 an unknown case, and an inherited property name, resolve to nothing',
   [PP_VERB_PATTERNS.caseLessonFor('partitive'), PP_VERB_PATTERNS.caseLessonFor('no-case'),
    PP_VERB_PATTERNS.caseLessonFor('constructor'), PP_VERB_PATTERNS.caseLessonFor('toString'),
    PP_VERB_PATTERNS.caseLessonFor(''), PP_VERB_PATTERNS.caseLessonFor(null),
    PP_VERB_PATTERNS.caseLessonFor({})],
   [null, null, null, null, null, null, null]);
eq('M1 both directions answer identically before and after data is accepted',
   (function () {
     var before = JSON.stringify([PP_VERB_PATTERNS.caseFilterFor('grammar-cases-dative'),
                                  PP_VERB_PATTERNS.caseLessonFor('dative')]);
     injectFixture();
     var after = JSON.stringify([PP_VERB_PATTERNS.caseFilterFor('grammar-cases-dative'),
                                 PP_VERB_PATTERNS.caseLessonFor('dative')]);
     return before === after;
   })(), true);
eq('M1 no runtime identifier or editorial term rides along on either link',
   (function () {
     var payload = JSON.stringify(CASE_NAMES.map(function (name) {
       return [PP_VERB_PATTERNS.caseFilterFor('grammar-cases-' + name),
               PP_VERB_PATTERNS.caseLessonFor(name)];
     }));
     return ['vp-', 'reviewState', 'contentRef', 'research', 'teachingStatus']
       .filter(function (token) { return payload.indexOf(token) !== -1; });
   })(), []);

// -------------------------------------------------------------------------
// M2. Grammar -> Verb Patterns: one continuation, and only where it belongs.
// -------------------------------------------------------------------------
var GRAMMAR_BLOCK = sliceBetween(
  INDEX, '/* ---------------- grammar (teach -> drill) ---------------- */',
  '/* ---------------- conversation (Rozmowy) ---------------- */');
var GRAMMAR_CODE = stripComments(GRAMMAR_BLOCK);
var GRAMMAR_DATA = readFile(ROOT + 'data-grammar.js');
eq('M2 the case lessons gained no pattern content of any kind',
   ['PP_VERB_PATTERNS', 'chipFor', 'vp-chip', 'vp-pattern', 'cardSupport',
    'caseLessonFor', 'lemma(', 'rows('].filter(function (token) {
     return countOf(GRAMMAR_CODE, token) !== 0;
   }), []);
eq('M2 the lesson renderers were not touched to host a verb list',
   [countOf(stripComments(extractFunction(INDEX, 'gRenderTeach')), 'PP_VERB_PATTERNS'),
    countOf(stripComments(extractFunction(INDEX, 'gRenderDrill')), 'PP_VERB_PATTERNS'),
    countOf(stripComments(extractFunction(INDEX, 'gStartPractice')), 'PP_VERB_PATTERNS')],
   [0, 0, 0]);
eq('M2 the authored grammar data is untouched and holds no link of its own',
   [countOf(GRAMMAR_DATA, 'Verbs that take the'), countOf(GRAMMAR_DATA, 'vp-'),
    countOf(GRAMMAR_DATA, 'verb-patterns'), countOf(GRAMMAR_DATA, 'patternLine')],
   [0, 0, 0, 0]);
eq('M2 the continuation is rendered at the END of the lesson, once',
   [countOf(GRAMMAR_CODE, 'gRenderPatternLink('),
    hasCode(extractFunction(INDEX, 'gShowDone'), 'gRenderPatternLink(G.topic);')],
   [1, true]);
eq('M2 it is added around the lesson, never into the authored teach array',
   [countOf(GRAMMAR_CODE, 'teach.push'), countOf(GRAMMAR_CODE, 'teach.concat'),
    countOf(stripComments(PATTERNS_BLOCK), 'teach.push')], [0, 0, 0]);
// Exactly the seven case topics, and nothing else on the Grammar surface.
eq('M2 exactly the six case topics whose case CAN occur receive the continuation',
   GRAMMAR_TOPICS.filter(function (topic) { return !!UI.continuation(topic); })
     .map(function (topic) { return topic.id; }),
   ['grammar-cases-nominative', 'grammar-cases-genitive', 'grammar-cases-dative',
    'grammar-cases-accusative', 'grammar-cases-instrumental',
    'grammar-cases-locative']);
eq('M2 the Vocative lesson renders no continuation at all',
   (function () {
     var vocative = GRAMMAR_TOPICS[7];
     var shown = UI.renderGrammarLink(vocative);
     return [vocative.id, UI.continuation(vocative), shown, gPatternLine.hidden,
             gPatternLabel.textContent];
   })(), ['grammar-cases-vocative', null, false, true, '']);
eq('M2 the Mix topic, which has no id, receives nothing',
   UI.continuation(GRAMMAR_TOPICS[0]), null);
eq('M2 a vocabulary, podcast, typing, listening or conversation topic receives nothing',
   [UI.continuation({ cards: [] }), UI.continuation({ kind: 'podcast' }),
    UI.continuation({ kind: 'typeit' }), UI.continuation({ kind: 'listen' }),
    UI.continuation({ kind: 'convo', id: 'grammar-cases-genitive' }),
    UI.continuation({ kind: 'patterns', surface: 'verb-index' }),
    UI.continuation(null), UI.continuation({ kind: 'grammar' })],
   [null, null, null, null, null, null, null, null]);
// Rendering it.
eq('M2 a case topic renders exactly one link, with the approved wording',
   (function () {
     var shown = UI.renderGrammarLink(GRAMMAR_TOPICS[2]);   // genitive
     return [shown, gPatternLine.hidden, gPatternLabel.textContent,
             gPatternLink.getAttribute('aria-label'), gPatternCaseName.getAttribute('lang'),
             gPatternCaseName.textContent, gPatternLink.tag,
             grammarScreen.querySelectorAll('.vp-continue').length];
   })(),
   [true, false, 'Verb patterns with the Genitive',
    null, 'pl', ' (Dopełniacz)', 'button', 1]);
eq('M2 the link carries no chip, no explanation, no example and no identifier',
   [gPatternLine.querySelectorAll('.vp-chip').length,
    gPatternLine.querySelectorAll('.vp-explain').length,
    gPatternLine.querySelectorAll('.vp-example').length,
    gPatternLine.textContent.indexOf('vp-')], [0, 0, 0, -1]);
eq('M2 moving to a non-case topic hides it again, leaving nothing stale',
   (function () {
     var shown = UI.renderGrammarLink(GRAMMAR_TOPICS[0]);
     return [shown, gPatternLine.hidden, gPatternLabel.textContent,
             gPatternCaseName.textContent, gPatternLink.getAttribute('aria-label')];
   })(), [false, true, '', '', null]);
eq('M2 each supported lesson renders its own case, never another one\'s',
   CASE_NAMES.map(function (name, i) {
     UI.renderGrammarLink(GRAMMAR_TOPICS[i + 1]);
     return gPatternLine.hidden ? null : gPatternLabel.textContent;
   }),
   ['Verb patterns with the Nominative', 'Verb patterns with the Genitive',
    'Verb patterns with the Dative', 'Verb patterns with the Accusative',
    'Verb patterns with the Instrumental', 'Verb patterns with the Locative',
    null]);

// -------------------------------------------------------------------------
// M3. The deep link: the index opens already filtered, as a VIEW.
// -------------------------------------------------------------------------
injectFixture();
uiEnv.shows = [];
UI.renderGrammarLink(GRAMMAR_TOPICS[2]);                     // genitive
gPatternLink.fire('click');
eq('M3 activating the continuation opens the reference surface once, focus deferred',
   uiEnv.shows, [['patterns', true]]);
eq('M3 the filter is already applied on arrival, as state and not as a step',
   [UI.P.filter, UI.P.view], ['genitive', 'index']);
eq('M3 the pressed filter chip shows the state, and exactly one is pressed',
   nodesWithClass('vp-filter').filter(function (node) {
     return node.getAttribute('aria-pressed') === 'true';
   }).map(function (node) { return node.getAttribute('data-vp-filter'); }), ['genitive']);
eq('M3 the filter is clearable - it is a view of one list, not a container',
   (function () {
     var all = filterButton('all');
     all.fire('click');
     return [UI.P.filter, nodesWithClass('vp-row-lemma').length];
   })(), ['all', 6]);
// Four call sites since Priority 7 Phase 4F-I1: the three entry paths, plus the
// release loader's settle handler, which re-renders the index in place when the
// runtime lands under a learner already standing on the unavailable state. All
// four render the ONE canonical index; there is still no case-owned copy.
eq('M3 the deep link lands in the canonical index, not a case-owned copy',
   [countOf(INDEX, '<section class="screen" id="patterns">'),
    countOf(stripComments(PATTERNS_BLOCK), 'pRenderIndex(')], [1, 4]);
// A multi-complement frame must survive the filter that brought the learner in.
UI.renderGrammarLink(GRAMMAR_TOPICS[6]);                     // locative
gPatternLink.fire('click');
eq('M3 arriving from the Locative lesson keeps the complete Dative+Locative frame',
   nodesWithClass('vp-row').filter(function (row) {
     return row.querySelectorAll('.vp-chip').length === 2;
   }).map(function (row) {
     return row.querySelectorAll('.vp-chip').map(function (chip) { return chip.textContent; });
   }), [['komu? czemu? · Dative', 'w kim? w czym? · Locative (matches this filter)']]);
eq('M3 the count line names the case the learner arrived from',
   textsOf('vp-count'), ['1 verb · 2 patterns with Miejscownik (Locative)']);
eq('M3 a filtered row is still a pointer: no explanation, example or back-link',
   [nodesWithClass('vp-explain').length, nodesWithClass('vp-example').length,
    nodesWithClass('vp-case-link').length], [0, 0, 0]);
// Every one of the seven, including the two cases no fixture pattern uses.
eq('M3 every offered continuation lands in the case it names - none falls back',
   CASE_NAMES.slice(0, 6).map(function (name, i) {
     UI.renderGrammarLink(GRAMMAR_TOPICS[i + 1]);
     gPatternLink.fire('click');
     return UI.P.filter;
   }),
   ['nominative', 'genitive', 'dative', 'accusative', 'instrumental', 'locative']);
// A continuation is offered only for a case that can occur, so the fallback is
// no longer reachable from any offered link.  Where it IS still reachable - a
// hand-built call, or a case the accepted corpus happens not to use - the
// surface must not present itself as filtered by a case it did not apply.
eq('M3 an unapplied filter never masquerades as a case-filtered view',
   (function () {
     UI.openFiltered('vocative', gPatternLink);
     var pressed = nodesWithClass('vp-filter').filter(function (node) {
       return node.getAttribute('aria-pressed') === 'true';
     }).map(function (node) { return node.textContent; });
     return [UI.P.filter, pSub.textContent, pressed,
             textsOf('vp-count')[0].indexOf(' with ') !== -1,
             nodesWithClass('vp-row-lemma').length];
   })(), ['all', '', ['All verbs'], false, 6]);
eq('M3 the same holds for a case the accepted corpus does not use',
   (function () {
     UI.openFiltered('partitive', gPatternLink);
     return [UI.P.filter, pSub.textContent,
             textsOf('vp-count')[0].indexOf(' with ') !== -1];
   })(), ['all', '', false]);

// Phase 3E: a KNOWN, filterable case is different from an unsupported route
// value. If a valid runtime happens to have no matching pattern, the deep link
// must remain truthful and clearable instead of silently turning into All.
var zeroCaseDoc = clone(WRAPPED_FIXTURE.runtimeProjection);
zeroCaseDoc.lemmas.forEach(function (lemma) {
  lemma.meanings.forEach(function (meaning) {
    meaning.patterns.forEach(function (pattern) {
      pattern.complements.forEach(function (complement) {
        if (complement.case === 'nominative') complement.case = 'accusative';
      });
    });
  });
});
ok('M3-E the zero-case runtime remains a valid public shape',
   PP_VERB_PATTERNS.__acceptForTest(zeroCaseDoc));
UI.openFiltered('nominative', gPatternLink);
eq('M3-E a supported zero-result filter remains selected and reports zero truthfully',
   [UI.P.filter, filterButton('nominative').getAttribute('aria-pressed'),
    textsOf('vp-count'), textsOf('vp-empty')],
   ['nominative', 'true', ['0 verbs · 0 patterns with Mianownik (Nominative)'],
    ['No verb patterns with Mianownik (Nominative).']]);
eq('M3-E the contextual zero-result filter keeps both language parts',
   [filterButton('nominative').querySelector('.sr-only').getAttribute('lang'),
    pSub.children[0].getAttribute('lang'),
    pStatus.textContent],
   ['pl', 'pl', '']);
eq('M3-E All verbs remains available and clears the zero-result filter',
   (function () {
     filterButton('all').fire('click');
     return [UI.P.filter, nodesWithClass('vp-row').length];
   })(), ['all', 6]);

// -------------------------------------------------------------------------
// M4. Verb Patterns -> Grammar: one route back per case in the frame.
// -------------------------------------------------------------------------
injectFixture();
function lemmaKeyFor(display) {
  var found = null;
  PP_VERB_PATTERNS.index().forEach(function (row) {
    if (row.lemma.indexOf(display) === 0) found = row.key;
  });
  return found;
}
function caseLinkLabels() {
  return nodesWithClass('vp-case-link').map(function (node) {
    return node.children.filter(function (child) {
      return !(child.classList && child.classList.contains('sr-only'));
    }).map(function (child) { return child.textContent; }).join('');
  });
}
UI.openLemma(lemmaKeyFor('zetafikcjonować się'));
eq('M4 the mixed-language lead-in keeps the lemma in a Polish node',
   nodesWithClass('vp-lead-in')[0].children.map(function (node) {
     return [node.getAttribute ? node.getAttribute('lang') : null, node.textContent];
   }), [['pl', 'zetafikcjonować się'],
         [null, ' has 2 meanings, and they behave differently.']]);
eq('M4 a single-case pattern offers exactly one route back',
   PP_VERB_PATTERNS.lemma(lemmaKeyFor('fikcjonować')).meanings[0].patterns[0].caseLinks
     .map(function (link) { return link.label + ' -> ' + link.topicId; }),
   ['Learn the Accusative -> grammar-cases-accusative']);
eq('M4 a two-case frame offers both, in authored order, with neither made primary',
   PP_VERB_PATTERNS.lemma(lemmaKeyFor('metodować')).meanings[0].patterns[2].caseLinks
     .map(function (link) { return link.caseId; }), ['dative', 'locative']);
eq('M4 a preposition + case complement links to the case, not to the preposition',
   PP_VERB_PATTERNS.lemma(lemmaKeyFor('metodować')).meanings[0].patterns[1].caseLinks
     .map(function (link) { return link.topicId; }), ['grammar-cases-locative']);
eq('M4 an infinitive-only pattern gets NO case link rather than a fabricated one',
   PP_VERB_PATTERNS.lemma(lemmaKeyFor('bezokolicznikować')).meanings[0].patterns[0].caseLinks,
   []);
eq('M4 a clause complement contributes no case link, and the cased slot still does',
   PP_VERB_PATTERNS.lemma(lemmaKeyFor('bezokolicznikować')).meanings[0].patterns[1].caseLinks
     .map(function (link) { return link.caseId; }), ['dative']);
eq('M4 a repeated case in one frame is offered once, not twice',
   PP_VERB_PATTERNS.caseLessonFor('accusative') !== null &&
   (function () {
     var doc = clone(WRAPPED_FIXTURE.runtimeProjection), target = null;
     doc.lemmas.forEach(function (lemma) {
       if (lemma.canonicalLemma === 'fikcjonować') target = lemma.meanings[0].patterns[0];
     });
     target.complements = [
       { type: 'case', case: 'accusative', required: true, role: 'object' },
       { type: 'preposition-case', case: 'accusative', preposition: 'o',
         required: true, role: 'target' }];
     PP_VERB_PATTERNS.__acceptForTest(doc);
     var links = PP_VERB_PATTERNS.lemma(lemmaKeyFor('fikcjonować'))
       .meanings[0].patterns[0].caseLinks;
     injectFixture();
     return links.map(function (link) { return link.caseId; });
   })(), ['accusative']);
// Rendered, in the lemma entry.
UI.startPatterns(0, 0);
UI.openLemma(lemmaKeyFor('metodować'));
eq('M4 every pattern of the entry carries its own routes back',
   caseLinkLabels(),
   ['Learn the Instrumental→', 'Learn the Locative→', 'Learn the Dative→',
    'Learn the Locative→']);
eq('M4 each route is a native button with a discernible name containing its label',
   nodesWithClass('vp-case-link').map(function (node) {
     return node.tag + '|' + node.type + '|' +
       (node.getAttribute('aria-labelledby') || '').indexOf('pCaseLink');
   }), ['button|button|0', 'button|button|0', 'button|button|0', 'button|button|0']);
eq('M4 Polish case names are language-tagged and no flat aria-label overrides them',
   nodesWithClass('vp-case-link').map(function (node) {
     var polish = node.querySelector('.sr-only');
     return [node.getAttribute('aria-label'), polish.getAttribute('lang'), polish.textContent];
   }), [[null, 'pl', ' (Narzędnik)'], [null, 'pl', ' (Miejscownik)'],
         [null, 'pl', ' (Celownik)'], [null, 'pl', ' (Miejscownik)']]);
eq('M4 the arrow is decoration only and is hidden from assistive technology',
   nodesWithClass('vp-case-arrow').map(function (node) {
     return node.getAttribute('aria-hidden');
   }), ['true', 'true', 'true', 'true']);
eq('M4 no case explanation, ending table or drill was copied into the entry',
   ['end-table', 'rule-list', 'b-explain', 'drill', 'Answers kto?']
     .filter(function (token) { return pBody.textContent.indexOf(token) !== -1; }), []);
UI.openLemma(lemmaKeyFor('bezokolicznikować'));
eq('M4 the infinitive pattern renders no route back, and its sibling renders one',
   [nodesWithClass('vp-pattern').length, caseLinkLabels()],
   [2, ['Learn the Dative→']]);
// Activating one opens the real lesson.
uiEnv.grammarStarts = [];
UI.openLemma(lemmaKeyFor('metodować'));
nodesWithClass('vp-case-link')[2].fire('click');             // "Learn the Dative"
eq('M4 activating a route opens the existing case topic, resolved by id',
   uiEnv.grammarStarts, [[1, 3]]);                           // Grammar Cases -> dative
eq('M4 the invoker is handed over so Back returns to the control that was used',
   UI.nextInvoker() === nodesWithClass('vp-case-link')[2], true);
eq('M4 the destination is located by topic id and kind, never by position',
   [UI.caseLessonAt('grammar-cases-genitive'), UI.caseLessonAt('grammar-cases-vocative'),
    UI.caseLessonAt('grammar-cases-partitive'), UI.caseLessonAt(''),
    UI.caseLessonAt(null)],
   [{ li: 1, ti: 2 }, { li: 1, ti: 7 }, null, null, null]);
eq('M4 an unresolvable lesson navigates nowhere and starts nothing',
   (function () {
     uiEnv.grammarStarts = [];
     var before = uiEnv.shows.length;
     var result = UI.openCaseLesson('grammar-cases-partitive', gPatternLink);
     return [result, uiEnv.grammarStarts.length, uiEnv.shows.length - before];
   })(), [false, 0, 0]);

// -------------------------------------------------------------------------
// M5. Card derivation: the eight required safety cases, all synthetic.
// -------------------------------------------------------------------------
// 1. one card, one eligible support, single-meaning single-pattern lemma
refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
eq('M5-1 one support claim on an unambiguous lemma yields the direct pointer',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).state, 'chip');
eq('M5-1 the pointer is that pattern\'s own COMPLETE frame',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).chips.map(function (chip) { return chip.text; }),
   ['kogo? co? · Accusative']);
refDoc(function (at) { at('podobnikować się', 0, 0, [supportRef()]); });
eq('M5-1 a two-slot frame is never truncated to its first chip',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).chips.map(function (chip) { return chip.text; }),
   ['kto? co? · Nominative', 'komu? czemu? · Dative']);
// 2. the same card claimed by more than one eligible pattern.
//    No pattern is selected either way.  WHERE the doorway may lead is a second
//    question, and it has two different answers.
//
//    2a. CROSS-LEMMA: the claims do not even agree about which verb the card is
//        about, so no lemma may be selected and the doorway opens the canonical
//        index.  Any tie-break here - claim order, lemma order, the card's own
//        text - would be a claim invented by the sort.
refDoc(function (at) {
  at('fikcjonować', 0, 0, [supportRef()]);
  at('podobnikować się', 0, 0, [supportRef()]);
});
eq('M5-2a two eligible claims select NEITHER pattern - the doorway is shown',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).state,
    PP_VERB_PATTERNS.cardSupport(CARD_ID).chips], ['doorway', undefined]);
eq('M5-2a claims owned by DIFFERENT lemmas select no lemma at all',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).scope,
    PP_VERB_PATTERNS.cardSupport(CARD_ID).lemmaKey], ['index', null]);
eq('M5-2a the two claims really do belong to different lemmas',
   (function () {
     var keys = {};
     ['fikcjonować', 'podobnikować się'].forEach(function (display) {
       keys[display] = lemmaKeyFor(display);
     });
     return keys['fikcjonować'] !== keys['podobnikować się'];
   })(), true);
// Order must not be able to change the answer, in either direction.
eq('M5-2a reversing the claim order cannot change the destination',
   (function () {
     var forward = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     refDoc(function (at) {
       at('podobnikować się', 0, 0, [supportRef()]);
       at('fikcjonować', 0, 0, [supportRef()]);
     });
     var reversed = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [forward.scope === reversed.scope, forward.lemmaKey === reversed.lemmaKey,
             reversed.scope, reversed.lemmaKey];
   })(), [true, true, 'index', null]);
eq('M5-2a three claims across three lemmas resolve the same way',
   (function () {
     refDoc(function (at) {
       at('fikcjonować', 0, 0, [supportRef()]);
       at('podobnikować się', 0, 0, [supportRef()]);
       at('konstrukcjować', 0, 0, [supportRef()]);
     });
     var claim = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [claim.state, claim.scope, claim.lemmaKey, claim.chips];
   })(), ['doorway', 'index', null, undefined]);
//    2b. SAME-LEMMA: the claims disagree about which meaning or pattern applies,
//        but they agree about the verb.  Opening that verb's entry asserts
//        nothing the references do not already agree on.  This distinction is
//        the invariant.
refDoc(function (at) {
  at('metodować', 0, 0, [supportRef()]);
  at('metodować', 0, 1, [supportRef()]);
});
eq('M5-2b two claims on the SAME lemma still open that lemma entry',
   (function () {
     var claim = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [claim.state, claim.scope, claim.lemmaKey === lemmaKeyFor('metodować'),
             claim.chips];
   })(), ['doorway', 'lemma', true, undefined]);
eq('M5-2b that destination is stable under claim order too',
   (function () {
     refDoc(function (at) {
       at('metodować', 0, 1, [supportRef()]);
       at('metodować', 0, 0, [supportRef()]);
     });
     var claim = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [claim.scope, claim.lemmaKey === lemmaKeyFor('metodować')];
   })(), ['lemma', true]);
eq('M5-2b all three claims of one lemma are still one lemma',
   (function () {
     refDoc(function (at) {
       at('metodować', 0, 0, [supportRef()]);
       at('metodować', 0, 1, [supportRef()]);
       at('metodować', 0, 2, [supportRef()]);
     });
     var claim = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [claim.state, claim.scope, claim.lemmaKey === lemmaKeyFor('metodować')];
   })(), ['doorway', 'lemma', true]);
// Every non-ambiguous outcome still names its owning verb.
eq('M5-2 an unambiguous claim and a Gate 2 doorway are both lemma-scoped',
   (function () {
     refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
     var chip = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     refDoc(function (at) { at('metodować', 0, 0, [supportRef()]); });
     var gate2 = PP_VERB_PATTERNS.cardSupport(CARD_ID);
     return [chip.state + ':' + chip.scope, gate2.state + ':' + gate2.scope];
   })(), ['chip:lemma', 'doorway:lemma']);
// 3. one support, but the owning lemma has more than one meaning
refDoc(function (at) { at('zetafikcjonować się', 0, 0, [supportRef()]); });
eq('M5-3 a multi-meaning lemma yields the doorway even with exactly one claim',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).state,
    PP_VERB_PATTERNS.lemma(PP_VERB_PATTERNS.cardSupport(CARD_ID).lemmaKey).meanings.length],
   ['doorway', 2]);
eq('M5-3 the meaning that has no card of its own is still reachable from the entry',
   PP_VERB_PATTERNS.lemma(PP_VERB_PATTERNS.cardSupport(CARD_ID).lemmaKey)
     .meanings.map(function (meaning) { return meaning.patterns.length; }), [1, 1]);
// 4. one support, but the owning lemma/meaning has more than one pattern
refDoc(function (at) { at('metodować', 0, 0, [supportRef()]); });
eq('M5-4 a multi-pattern lemma yields the doorway even with exactly one claim',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).state,
    PP_VERB_PATTERNS.lemma(PP_VERB_PATTERNS.cardSupport(CARD_ID).lemmaKey).meanings[0].patterns.length],
   ['doorway', 3]);
// 5. contrast only
refDoc(function (at) { at('fikcjonować', 0, 0, [contrastRef()]); });
eq('M5-5 a contrast-only card shows NOTHING - not a chip, not a doorway',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).state, 'none');
refDoc(function (at) {
  at('fikcjonować', 0, 0, [contrastRef()]);
  at('metodować', 0, 0, [contrastRef()]);
});
eq('M5-5 several contrast references still show nothing - they never accumulate',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).state, 'none');
// 6. support + contrast on the same card: the support is evaluated alone
refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef(), contrastRef()]); });
eq('M5-6 a contrast reference beside a support one adds no second claim',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).state, 'chip');
refDoc(function (at) {
  at('fikcjonować', 0, 0, [supportRef()]);
  at('metodować', 0, 0, [contrastRef()]);
});
eq('M5-6 a contrast reference from a DIFFERENT pattern cannot make the card ambiguous',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).state,
    PP_VERB_PATTERNS.cardSupport(CARD_ID).chips.map(function (chip) { return chip.text; })],
   ['chip', ['kogo? co? · Accusative']]);
eq('M5-6 the contrast reference never makes the card look like an instantiation',
   (function () {
     var owner = PP_VERB_PATTERNS.lemma(PP_VERB_PATTERNS.cardSupport(CARD_ID).lemmaKey);
     return owner.lemma;
   })(), 'fikcjonować');
// 7. no references at all
refDoc(null);
eq('M5-7 a card with no reference gets nothing',
   [PP_VERB_PATTERNS.cardSupport(CARD_ID).state,
    PP_VERB_PATTERNS.cardSupport('a1-first-verbs-020').state], ['none', 'none']);
// 8. the visible word matches a runtime lemma, but nothing references the card
refDoc(function (at) { at('metodować', 0, 0, [supportRef('some-other-card')]); });
eq('M5-8 a card whose visible word IS a runtime lemma still gets nothing',
   [PP_VERB_PATTERNS.cardSupport('fikcjonować').state,
    PP_VERB_PATTERNS.cardSupport('metodować').state,
    PP_VERB_PATTERNS.cardSupport(CARD_ID).state], ['none', 'none', 'none']);
// Ineligible relations, in every remaining shape.
refDoc(function (at) {
  at('fikcjonować', 0, 0, [
    { kind: 'card', id: CARD_ID, purpose: 'practice' },
    { kind: 'card', id: CARD_ID, purpose: 'context' },
    { kind: 'topic', id: CARD_ID, purpose: 'support' },
    { kind: 'topic', id: CARD_ID, purpose: 'contrast' },
    { kind: 'drill', id: CARD_ID, purpose: 'practice' },
    { kind: 'scenario', id: CARD_ID, purpose: 'context' }]);
});
eq('M5 only card+support is eligible: no other combination produces anything',
   PP_VERB_PATTERNS.cardSupport(CARD_ID).state, 'none');
eq('M5 the derivation fails closed on a malformed or inherited card id',
   (function () {
     refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
     return [PP_VERB_PATTERNS.cardSupport('constructor').state,
             PP_VERB_PATTERNS.cardSupport('toString').state,
             PP_VERB_PATTERNS.cardSupport('__proto__').state,
             PP_VERB_PATTERNS.cardSupport('').state,
             PP_VERB_PATTERNS.cardSupport(null).state,
             PP_VERB_PATTERNS.cardSupport(undefined).state,
             PP_VERB_PATTERNS.cardSupport({}).state,
             PP_VERB_PATTERNS.cardSupport(7).state];
   })(), ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none']);
eq('M5 an unavailable loader claims nothing for any card',
   (function () {
     PP_VERB_PATTERNS.reset();
     return [PP_VERB_PATTERNS.cardSupport(CARD_ID).state, PP_VERB_PATTERNS.available];
   })(), ['none', false]);
eq('M5 the eligibility test lives where the index is built, and admits one pair',
   [countOf(LOADER_SRC, 'ref.kind !== "card" || ref.purpose !== "support"'),
    countOf(LOADER_SRC, 'purpose === "contrast"')], [1, 0]);
eq('M5 the committed fixture still carries no card reference at all',
   countOf(readFile(ROOT + 'tests/fixtures/priority7/runtime-fixture.json'), '"kind": "card"'), 0);

// -------------------------------------------------------------------------
// M6. The card back: one compact line, three outcomes, nothing else.
// -------------------------------------------------------------------------
eq('M6 the pointer reuses the card\'s own compact labelled-row idiom',
   [countOf(INDEX, '<div class="pair-line" id="patternLine" hidden>'),
    countOf(INDEX, 'id="patternLink" type="button"'),
    INDEX.indexOf('id="variantLine"') < INDEX.indexOf('id="patternLine"'),
    INDEX.indexOf('id="patternLine"') < INDEX.indexOf('id="exampleBox"')],
   [1, 1, true, true]);
// The link is DERIVED. No card authors it, no data file mentions it, and the
// only field read off a card anywhere in this feature is its id.
eq('M6 the card data schema was not reopened to carry the link',
   (function () {
     var claim = stripComments(extractFunction(INDEX, 'ppCardPatternClaim'));
     return [countOf(GRAMMAR_DATA, 'patternLine'),
             ['data-a1.js', 'data-a2.js', 'data-b1.js'].filter(function (file) {
               var src = readFile(ROOT + file);
               return countOf(src, 'patternLine') + countOf(src, 'vp-') +
                 countOf(src, 'contentRef') !== 0;
             }),
             countOf(claim, 'card.'), countOf(claim, 'card.id'),
             countOf(stripComments(extractFunction(INDEX, 'ppRenderCardPattern')), 'card.')];
   })(), [0, [], 3, 3, 0]);
// Nothing, chip and doorway, rendered.
refDoc(null);
eq('M6 no eligible claim renders no line and leaves the row empty',
   [UI.renderCardPattern(fakeCard()), patternLine.hidden,
    patternLink.textContent, patternLink.children.length], [false, true, '', 0]);
refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
eq('M6 an unambiguous card shows the direct pointer, once',
   [UI.renderCardPattern(fakeCard()), patternLine.hidden,
    patternK.textContent, cardLinkClasses('vp-chip').length,
    cardLinkClasses('vp-chip')[0].textContent],
   [true, false, 'Pattern', 1, 'kogo? co? · Accusative']);
eq('M6 the direct pointer has a discernible name that contains what is visible',
   [patternLink.getAttribute('aria-label'), patternLink.textContent,
    cardLinkClasses('vp-chip')[0].children.map(function (node) {
      return [node.getAttribute('lang'), node.textContent];
    })],
   [null, "See this verb's pattern: kogo? co? · Accusative→",
    [['pl', 'kogo? co?'], [null, ' · Accusative']]]);
eq('M6 its arrow is decoration and is hidden from assistive technology',
   cardLinkClasses('vp-card-arrow').map(function (node) {
     return node.getAttribute('aria-hidden');
   }), ['true']);
eq('M6 re-rendering the same card leaves exactly one line, never a duplicate',
   (function () {
     UI.renderCardPattern(fakeCard());
     UI.renderCardPattern(fakeCard());
     return [cardLinkClasses('vp-chip').length, cardLinkClasses('vp-card-arrow').length,
             patternLine.querySelectorAll('.vp-card-link').length];
   })(), [1, 1, 1]);
refDoc(function (at) { at('metodować', 0, 0, [supportRef()]); });
eq('M6 an ambiguous card shows the neutral doorway and names no pattern',
   (function () {
     UI.renderCardPattern(fakeCard());
     var text = patternLink.textContent;
     return [patternLine.hidden, cardLinkClasses('vp-card-doorway')[0].textContent,
             cardLinkClasses('vp-chip').length,
             ['Genitive', 'Dative', 'Locative', 'kogo?', 'komu?', 'czym?']
               .filter(function (token) { return text.indexOf(token) !== -1; })];
   })(), [false, 'See how this verb is used', 0, []]);
eq('M6 the doorway carries no more than one pattern\'s worth of anything',
   [patternLink.children.length, patternLink.getAttribute('aria-label')],
   [2, null]);   // the doorway phrase and the arrow; native content supplies the name
eq('M6 moving from a doorway card to an unreferenced one clears the row entirely',
   (function () {
     UI.renderCardPattern(fakeCard({ id: 'not-referenced-at-all' }));
     return [patternLine.hidden, patternLink.textContent,
             patternLink.getAttribute('aria-label')];
   })(), [true, '', null]);
eq('M6 a podcast introduction is not a vocabulary card and shows nothing',
   (function () {
     refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
     UI.renderCardPattern(fakeCard());
     UI.renderCardPattern(null);
     return [patternLine.hidden, patternLink.textContent];
   })(), [true, '']);
eq('M6 a card with no id, or an id of the wrong type, is never resolved',
   [UI.cardClaim({ pl: 'fikcjonować' }), UI.cardClaim({ id: '' }),
    UI.cardClaim({ id: 7 }), UI.cardClaim({ id: null }), UI.cardClaim(null)],
   [null, null, null, null, null]);
// Nothing internal reaches the card back.
eq('M6 the card back exposes no review state, evidence, identifier or reference',
   (function () {
     refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
     UI.renderCardPattern(fakeCard());
     var payload = patternLine.textContent + ' ' +
       patternLine.descendants().map(function (node) {
         return Object.keys(node.attrs || {}).map(function (name) {
           return name + '=' + node.attrs[name];
         }).join(' ') + ' ' + (node.className || '') + ' ' + (node.id || '');
       }).join(' ');
     return ['vp-p-', 'vp-l-', 'vp-m-', CARD_ID, 'research', 'reviewState',
             'contentRef', 'support', 'contrast', 'teachingStatus', 'A1', 'A2', 'B1']
       .filter(function (token) { return payload.indexOf(token) !== -1; });
   })(), []);
// Hostile runtime text on the card back is text.
eq('M6 hostile runtime text in a chip is rendered as text, never as markup',
   (function () {
     var hostile = '<img src=x onerror="window.__vpPwned=1">';
     var doc = clone(WRAPPED_FIXTURE.runtimeProjection);
     doc.lemmas.forEach(function (lemma) {
       lemma.meanings.forEach(function (meaning) {
         meaning.patterns.forEach(function (pattern) { delete pattern.contentRefs; });
       });
       if (lemma.canonicalLemma !== 'fikcjonować') return;
       lemma.meanings[0].patterns[0].complements = [
         { type: 'preposition-case', case: 'instrumental', preposition: hostile,
           required: true, role: 'means' }];
       lemma.meanings[0].patterns[0].contentRefs = [supportRef()];
     });
     PP_VERB_PATTERNS.__acceptForTest(doc);
     UI.renderCardPattern(fakeCard());
     var tags = {};
     patternLine.descendants().forEach(function (node) { if (node.tag) tags[node.tag] = true; });
     return [patternLink.textContent.indexOf(hostile) !== -1,
             Object.keys(tags).sort(), typeof fakeWindow.__vpPwned];
   })(), [true, ['button', 'span'], 'undefined']);
eq('M6 the card renderer builds DOM only through safe APIs',
   ['innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write', 'eval(']
     .filter(function (token) {
       return countOf(stripComments(extractFunction(INDEX, 'ppRenderCardPattern')), token) !== 0;
     }), []);

// -------------------------------------------------------------------------
// M7. Interaction: what the two card outcomes open, and where focus goes.
// -------------------------------------------------------------------------
refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
UI.renderCardPattern(fakeCard());
uiEnv.shows = [];
patternLink.fire('click');
eq('M7 a direct pointer opens the lemma entry in ONE step, focus deferred to it',
   [uiEnv.shows, UI.P.view, pTitle.textContent],
   [[['patterns', true]], 'lemma', 'fikcjonować']);
eq('M7 focus lands on the lemma heading, revealed, and not on the index heading',
   [fakeDocument.activeElement.className, fakeDocument.activeElement.tag,
    fakeDocument.activeElement.revealCount > 0], ['vp-lemma-head', 'h2', true]);
eq('M7 the invoking card control is handed over as the return target',
   UI.nextInvoker() === patternLink, true);
eq('M7 the entry it opens is the one canonical owner, rendered in full',
   [nodesWithClass('vp-pattern').length, nodesWithClass('vp-explain').length,
    nodesWithClass('vp-case-link').length], [1, 1, 1]);
eq('M7 Back from there returns to the index without leaving the surface',
   (function () {
     var before = uiEnv.shows.length;
     UI.back();
     return [UI.P.view, uiEnv.shows.length - before, nodesWithClass('vp-row').length];
   })(), ['index', 0, 6]);
// The doorway opens the same entry, and claims nothing about which pattern.
refDoc(function (at) { at('metodować', 0, 0, [supportRef()]); });
UI.renderCardPattern(fakeCard());
uiEnv.shows = [];
patternLink.fire('click');
eq('M7 the doorway opens the lemma entry, with every meaning and pattern present',
   [uiEnv.shows, UI.P.view, pTitle.textContent, nodesWithClass('vp-pattern').length],
   [[['patterns', true]], 'lemma', 'metodować', 3]);
eq('M7 the doorway pre-selects no pattern - the entry is where the choice is made',
   [UI.P.filter, nodesWithClass('vp-pattern').filter(function (node) {
     return node.classList.contains('is-match');
   }).length], ['all', 0]);
eq('M7 a card control is a native button, so Enter and Space activate it',
   [patternLink.tag, countOf(INDEX, 'id="patternLink" type="button"'),
    countOf(INDEX, 'id="gPatternLink" type="button"')], ['button', 1, 1]);
// The cross-lemma doorway: rendered wording, and where it actually goes.
refDoc(function (at) {
  at('fikcjonować', 0, 0, [supportRef()]);
  at('podobnikować się', 0, 0, [supportRef()]);
});
UI.renderCardPattern(fakeCard());
eq('M7 a cross-verb doorway promises only the reference, and names no verb',
   (function () {
     var text = patternLink.textContent;
     return [patternLine.hidden, cardLinkClasses('vp-card-doorway')[0].textContent,
             patternLink.getAttribute('aria-label'),
             cardLinkClasses('vp-chip').length,
             ['fikcjonować', 'podobnikować', 'this verb', 'Accusative', 'Nominative']
               .filter(function (token) { return text.indexOf(token) !== -1; })];
   })(), [false, 'See verb patterns', null, 0, []]);
uiEnv.shows = [];
patternLink.fire('click');
eq('M7 it opens the canonical all-verbs index, and does not fail silently',
   [uiEnv.shows, UI.P.view, UI.P.filter, pTitle.textContent],
   [[['patterns', true]], 'index', 'all', 'Verb Patterns']);
eq('M7 no lemma is preselected and no lemma entry is rendered',
   [UI.P.lastLemmaKey, nodesWithClass('vp-pattern').length,
    nodesWithClass('vp-explain').length, nodesWithClass('vp-row-lemma').length],
   [null, 0, 0, 6]);
eq('M7 reversing the claim order lands in exactly the same place',
   (function () {
     refDoc(function (at) {
       at('podobnikować się', 0, 0, [supportRef()]);
       at('fikcjonować', 0, 0, [supportRef()]);
     });
     UI.renderCardPattern(fakeCard());
     uiEnv.shows = [];
     patternLink.fire('click');
     return [UI.P.view, UI.P.filter, UI.P.lastLemmaKey, pTitle.textContent];
   })(), ['index', 'all', null, 'Verb Patterns']);
// The same-lemma doorway, by contrast, still opens the verb it agrees on.
eq('M7 a same-verb doorway still opens that verb\'s entry',
   (function () {
     refDoc(function (at) {
       at('metodować', 0, 0, [supportRef()]);
       at('metodować', 0, 1, [supportRef()]);
     });
     UI.renderCardPattern(fakeCard());
     uiEnv.shows = [];
     patternLink.fire('click');
     return [cardLinkClasses('vp-card-doorway')[0].textContent, UI.P.view,
             pTitle.textContent, nodesWithClass('vp-pattern').length];
   })(), ['See how this verb is used', 'lemma', 'metodować', 3]);
eq('M7 the destination is carried by the claim, never re-derived by the renderer',
   [countOf(stripComments(PATTERNS_BLOCK), 'ppOpenCardPattern(claim, link)'),
    countOf(stripComments(PATTERNS_BLOCK), 'ppOpenPatternsLemma(claim.lemmaKey, link)')],
   [1, 0]);
eq('M7 a malformed or unknown claim shape renders nothing rather than a dead control',
   (function () {
     refDoc(function (at) { at('fikcjonować', 0, 0, [supportRef()]); });
     var before = UI.cardClaim(fakeCard());
     return [before.state, before.scope,
             UI.cardClaim(fakeCard({ id: 'nothing-claims-this' }))];
   })(), ['chip', 'lemma', null]);

eq('M7 an unresolvable lemma key navigates nowhere',
   (function () {
     var before = uiEnv.shows.length;
     return [UI.openLemmaScreen(null, patternLink),
             UI.openLemmaScreen(undefined, patternLink),
             uiEnv.shows.length - before];
   })(), [false, false, 0]);
eq('M7 every lemma-scoped outcome reaches the same surface through one renderer',
   [countOf(stripComments(PATTERNS_BLOCK), 'function pRenderLemma('),
    countOf(stripComments(PATTERNS_BLOCK), 'function ppOpenCardPattern('),
    countOf(stripComments(PATTERNS_BLOCK), 'ppOpenPatternsLemma(claim.lemmaKey, invoker)')],
   [1, 1, 1]);
// The full round trip through the SHIPPING focus helpers, as J2 does.
eq('M7 the handed-over invoker is what the screen restores focus to on exit',
   (function () {
     UI.openLemmaScreen(lemmaKeyFor('fikcjonować'), patternLink);
     UI.remember('patterns');
     var before = patternLink.focusCount;
     var restored = UI.routeFocus(patternsScreen, studyScreen);
     return [restored === patternLink, patternLink.focusCount - before];
   })(), [true, 1]);
eq('M7 the same contract holds for the Grammar continuation link',
   (function () {
     UI.openFiltered('genitive', gPatternLink);
     UI.remember('patterns');
     var before = gPatternLink.focusCount;
     var restored = UI.routeFocus(patternsScreen, grammarScreen);
     return [restored === gPatternLink, gPatternLink.focusCount - before];
   })(), [true, 1]);
eq('M7 the reference surface still adds no history entry of its own',
   [countOf(stripComments(PATTERNS_BLOCK), 'pushState'),
    countOf(stripComments(PATTERNS_BLOCK), 'history.')], [0, 0]);

// -------------------------------------------------------------------------
// M8. Layout: the new controls obey every pinned constraint.
// -------------------------------------------------------------------------
var STYLE_SRC = (function () {
  var out = '', re = /<style[^>]*>([\s\S]*?)<\/style>/g, m;
  while ((m = re.exec(INDEX))) out += m[1] + '\n';
  return out;
})();
function ruleBody(selector) {
  var at = STYLE_SRC.indexOf('\n  ' + selector + '{');
  if (at === -1) at = STYLE_SRC.indexOf('\n  ' + selector + ',');
  if (at === -1) return null;
  var open = STYLE_SRC.indexOf('{', at);
  return STYLE_SRC.slice(open + 1, STYLE_SRC.indexOf('}', open));
}
var NEW_SELECTORS = ['.vp-continue-line', '.vp-continue', '.vp-case-links',
                     '.vp-case-link', '.vp-card-link', '.vp-card-doorway'];
eq('M8 every new selector exists exactly once in the sheet',
   NEW_SELECTORS.filter(function (selector) {
     return countOf(STYLE_SRC, '\n  ' + selector + '{') !== 1;
   }), []);
eq('M8 no new breakpoint was introduced - the pinned widths are unchanged',
   (function () {
     var widths = [], re = /@media[^{]*\(max-width:\s*(\d+)px\)/g, m;
     while ((m = re.exec(STYLE_SRC))) widths.push(Number(m[1]));
     return widths.sort();
   })(), [360, 400, 400]);
eq('M8 nothing was added to the 360px block',
   countOf(STYLE_SRC.slice(STYLE_SRC.indexOf('(max-width:360px)')), 'vp-'), 0);
eq('M8 no new rule breaks inside a word or hides horizontal overflow',
   NEW_SELECTORS.filter(function (selector) {
     var body = ruleBody(selector) || '';
     return /overflow-wrap|word-break|overflow-x/.test(body);
   }), []);
var P3E_DATA_SELECTORS = ['.vp-row-lemma', '.vp-row-gloss', '.vp-lemma-head',
  '.vp-meaning-head', '.vp-lead-in', '.vp-headline', '.vp-chip', '.vp-role',
  '.vp-explain', '.vp-example-pl', '.vp-example-en'];
eq('M8-E every passive runtime-data field has an emergency wrap for hostile tokens',
   P3E_DATA_SELECTORS.map(function (selector) {
     return /overflow-wrap:anywhere/.test(ruleBody(selector) || '');
   }), [true, true, true, true, true, true, true, true, true, true, true]);
eq('M8-E the hardening wraps without clipping, truncating or word-break',
   P3E_DATA_SELECTORS.filter(function (selector) {
     return /overflow(-x)?:\s*(hidden|clip)|text-overflow|word-break/.test(ruleBody(selector) || '');
   }), []);
eq('M8 the three new controls all keep a 44px touch target',
   ['.vp-continue', '.vp-case-link', '.vp-card-link'].map(function (selector) {
     return /min-height:44px/.test(ruleBody(selector) || '');
   }), [true, true, true]);
eq('M8 they wrap rather than scroll, and claim no width of their own',
   ['.vp-continue', '.vp-case-link', '.vp-card-link'].map(function (selector) {
     var body = ruleBody(selector) || '';
     return /flex-wrap:wrap/.test(body) && /max-width:100%/.test(body) &&
       !/(^|;)\s*width:/.test(body);
   }), [true, true, true]);
eq('M8 each new control has a visible focus style that is not colour alone',
   ['.vp-continue', '.vp-case-link', '.vp-card-link'].map(function (selector) {
     return countOf(STYLE_SRC, selector + ':focus-visible{');
   }), [1, 1, 1]);
eq('M8 no animation or transition was added, so reduced motion needs no new rule',
   NEW_SELECTORS.filter(function (selector) {
     return /animation|transition/.test(ruleBody(selector) || '');
   }), []);
eq('M8 the state of every new control is carried by text, never by colour alone',
   [gPatternLabel.textContent.length > 0,
    countOf(stripComments(PATTERNS_BLOCK), 'aria-hidden'), 3], [true, 3, 3]);

// -------------------------------------------------------------------------
// M9. The shipping path: ordinary startup, no data, no request, no pointer.
// -------------------------------------------------------------------------
PP_VERB_PATTERNS.reset();
eq('M9 the case-lesson continuation still exists with no reference data',
   (function () {
     var shown = UI.renderGrammarLink(GRAMMAR_TOPICS[2]);
     return [shown, gPatternLine.hidden, gPatternLabel.textContent];
   })(), [true, false, 'Verb patterns with the Genitive']);
eq('M9 activating it opens the surface safely and reaches the unavailable state',
   (function () {
     uiEnv.shows = [];
     gPatternLink.fire('click');
     return [uiEnv.shows, UI.P.filter, nodesWithClass('vp-row').length,
             pBody.textContent.indexOf('isn’t ready to open yet') !== -1];
   })(), [[['patterns', true]], 'all', 0, true]);
eq('M9 the unavailable state reached this way still exposes nothing internal',
   ['research', 'review', 'approv', 'corpus', 'editorial', 'error', 'failed',
    'fixture', 'JSON', 'loader'].filter(function (token) {
     return (pBody.textContent + ' ' + pStatus.textContent).toLowerCase()
       .indexOf(token.toLowerCase()) !== -1;
   }), []);
eq('M9 NO card back pointer appears anywhere, because nothing was accepted',
   (function () {
     var outcomes = ['a1-first-verbs-020', 'a1-first-verbs-022', 'b1-character-emotions-010',
                     CARD_ID, 'fikcjonować'].map(function (id) {
       UI.renderCardPattern(fakeCard({ id: id }));
       return patternLine.hidden;
     });
     return outcomes;
   })(), [true, true, true, true, true]);
eq('M9 a card pointer is impossible without accepted data, by construction',
   hasCode(extractFunction(INDEX, 'ppCardPatternClaim'),
           'if(!PP_VERB_PATTERNS.available) return null;'), true);
// The cross-links themselves still add no request. Priority 7 Phase 4F-I1 adds
// the one production load, and no fixture, preview or test-injection path.
eq('M9 the cross-links added no request, and none is conditional on a fixture',
   [countOf(INDEX, 'fetch('), countOf(INDEX, 'content/'),
    countOf(INDEX, 'verb-patterns.json'), countOf(PATTERNS_CODE, 'fixture'),
    countOf(PATTERNS_CODE, '__acceptForTest')], [3, 1, 1, 0, 0]);
eq('M9 opening a lemma with no data fails closed into the unavailable state',
   (function () {
     uiEnv.shows = [];
     var opened = UI.openLemmaScreen(0, patternLink);
     return [opened, UI.P.view, nodesWithClass('vp-row').length,
             pBody.textContent.indexOf('isn’t ready to open yet') !== -1];
   })(), [true, 'index', 0, true]);
eq('M9 no new storage key, analytics or identifier came in with this phase',
   [countOf(PATTERNS_CODE, 'localStorage'), countOf(PATTERNS_CODE, 'sessionStorage'),
    countOf(PATTERNS_CODE, 'analytics'), countOf(PATTERNS_CODE, 'gtag'),
    countOf(PATTERNS_CODE, 'cookie'), countOf(LOADER_SRC, 'localStorage')],
   [0, 0, 0, 0, 0, 0]);
// Advanced together by Priority 7 Phase 4F-I1, as one atomic release: the
// shell version, the shell cache generation, and the worker's three
// verb-pattern references (the helper and the runtime in REQUIRED_ASSETS, and
// the runtime's own canonical path constant).
eq('M9 the version and cache markers moved together in the I1 release',
   [(INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1],
    countOf(readFile(ROOT + 'sw.js'), 'popolsku-v65'),
    countOf(readFile(ROOT + 'sw.js'), 'popolsku-v66'),
    countOf(readFile(ROOT + 'sw.js'), 'verb-patterns')], ['8.11', 0, 1, 3]);

// -------------------------------------------------------------------------
// N. Phase 3F-A: dormant transport -> accepted state -> approved safe DOM path.
// -------------------------------------------------------------------------
PP_VERB_PATTERNS.reset();
var rehearsalCalls = [];
var rehearsalResult = PP_VERB_PATTERNS.loadRuntimeDocument(function (url, options) {
  rehearsalCalls.push([url, options]);
  return Immediate.resolve({
    ok: true,
    status: 200,
    json: function () { return Immediate.resolve(clone(RELEASE_REHEARSAL_FIXTURE)); }
  });
}, 'synthetic-test-only://priority7-runtime');
eq('N1 the injected HTTP-like rehearsal settles successfully',
   immediateValue(rehearsalResult), true);
eq('N1 the transport made one no-store request to only the injected URL',
   rehearsalCalls, [['synthetic-test-only://priority7-runtime', { cache: 'no-store' }]]);
eq('N1 loading switches data availability and builds the complete synthetic index',
   [PP_VERB_PATTERNS.available, PP_VERB_PATTERNS.summary(),
    PP_VERB_PATTERNS.index().length, PP_VERB_PATTERNS.filters().map(function (f) { return f.id; })],
   [true, { lemmas: 2, patterns: 2 }, 2, ['all', 'accusative', 'no-case']]);

UI.startPatterns(0, 0);
eq('N2 the loaded fixture renders two index rows through the shipping renderer',
   nodesWithClass('vp-row').length, 2);
var rehearsalHostile = '<img src=x onerror=window.__p7LoaderPwned=1>';
eq('N2 hostile loader-path content remains text and creates no executable element',
   [pBody.textContent.indexOf(rehearsalHostile) !== -1,
    tagsUsed().indexOf('img'), tagsUsed().indexOf('script'),
    typeof fakeWindow.__p7LoaderPwned], [true, -1, -1, 'undefined']);
nodesWithClass('vp-row').filter(function (row) {
  return row.textContent.indexOf('TEST-ONLY Quuxify') !== -1;
})[0].fire('click');
eq('N2 index, filter and lemma derivation all remain usable after transport acceptance',
   [textsOf('vp-lemma-head').length, textsOf('vp-meaning-head').length,
    textsOf('vp-chip').length, textsOf('vp-example-pl').length], [1, 1, 1, 1]);

UI.startPatterns(0, 0, 'dative');
eq('N3 a known filter with zero matches keeps the Phase 3E truthful empty state',
   [UI.P.filter, nodesWithClass('vp-row').length,
    pBody.textContent.indexOf('No verb patterns with') !== -1], ['dative', 0, true]);

var acceptedBeforeFailure = JSON.stringify({
  index: PP_VERB_PATTERNS.index(), filters: PP_VERB_PATTERNS.filters(),
  lemma: PP_VERB_PATTERNS.lemma(0), summary: PP_VERB_PATTERNS.summary()
});
var failedRefreshCalls = 0;
var failedRefresh = PP_VERB_PATTERNS.loadRuntimeDocument(function () {
  failedRefreshCalls++;
  return Immediate.reject(new Error('synthetic network rejection'));
}, 'synthetic-test-only://priority7-runtime');
eq('N4 a later network failure settles false with no retry',
   [immediateValue(failedRefresh), failedRefreshCalls], [false, 1]);
eq('N4 the failed candidate cannot clear or corrupt the accepted runtime',
   [PP_VERB_PATTERNS.available, JSON.stringify({
     index: PP_VERB_PATTERNS.index(), filters: PP_VERB_PATTERNS.filters(),
     lemma: PP_VERB_PATTERNS.lemma(0), summary: PP_VERB_PATTERNS.summary()
   }) === acceptedBeforeFailure], [true, true]);

PP_VERB_PATTERNS.reset();
var malformedFirstLoad = PP_VERB_PATTERNS.loadRuntimeDocument(function () {
  return Immediate.resolve({ ok: true, status: 200, json: function () {
    return Immediate.resolve({ formatVersion: 1, patternDataRevision: 1, lemmas: [] });
  }});
}, 'synthetic-test-only://priority7-runtime');
eq('N5 a malformed first load stays unavailable and produces no partial view',
   [immediateValue(malformedFirstLoad), PP_VERB_PATTERNS.available,
    PP_VERB_PATTERNS.index().length], [false, false, 0]);
UI.startPatterns(0, 0);
eq('N5 the learner still sees only the neutral unavailable state',
   [nodesWithClass('vp-row').length,
    pBody.textContent.indexOf('isn’t ready to open yet') !== -1], [0, true]);
injectFixture();

console.log('Priority 7 Phase 3B/3C verb-pattern tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] the shipping loader, the routing dispatch, the shared focus helpers and both');
console.log('         renderers are executed as they ship, against a deterministic fake DOM');
console.log('  [info] the wrapped fixture is opened ONLY by this suite\'s harness, which asserts');
console.log('         artifactStatus and releaseAuthorized:false before it reads the projection');
console.log('  [info] test fixture != validated runtime shape != authorized release: this suite');
console.log('         reaches the first two and cannot reach the third');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
