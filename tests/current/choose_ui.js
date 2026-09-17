// Maintained current regression extraction; release markers are injected by run_current_tests.py.
// Deterministic tests for Priority 7 Phase 3D-1 - the synthetic grammar-choose
// MECHANICS PROTOTYPE.  Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_priority7_choose_ui.js
//
// What runs here is the shipping code.  pp-verb-patterns.js is loaded as-is and
// its adapter is driven directly; the Grammar choose engine, the shared focus
// and status helpers and the Priority 7 practice entry are extracted from
// index.html and executed against a deterministic fake DOM.  No parallel engine,
// no parallel adapter and no parallel accessibility framework exists here.
//
// THE TWO THINGS TO UNDERSTAND ABOUT THIS SUITE:
//   1. the exercise fixture it feeds is WRAPPED, and the shipping adapter
//      refuses the wrapper.  The wrapper is opened here, in the harness, by a
//      function that asserts the non-release markers before it opens anything.
//      Shipping code performs none of those steps and has no path to the file.
//   2. nothing this suite proves is a statement about Polish, about activity
//      eligibility, or about anything being allowed to reach a learner.  The
//      fixture's "correct" answers are correct inside the fixture and nowhere
//      else.  test fixture != validated shape != authorized release.
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
(0, eval)(LOADER_SRC);                                 // defines global PP_VERB_PATTERNS
var WRAPPED_EXERCISES = JSON.parse(
  readFile(ROOT + 'tests/fixtures/priority7/exercise-fixture.json'));
var WRAPPED_RUNTIME = JSON.parse(
  readFile(ROOT + 'tests/fixtures/priority7/runtime-fixture.json'));

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function clone(value) { return JSON.parse(JSON.stringify(value)); }
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
function throws(fn) { try { fn(); return false; } catch (e) { return true; } }
// Fixture text fields are either a plain string or {text, lang} fragments; this
// flattens either to the words a learner actually sees, so an assertion can be
// written against the record without caring which form it took.
function flat(value) {
  if (!Array.isArray(value)) return value === undefined || value === null ? '' : String(value);
  return value.map(function (part) { return part.text || ''; }).join('');
}
function langsOf(value) {
  return (Array.isArray(value) ? value : [{ text: value }])
    .map(function (part) { return part.lang || null; });
}
// What an assistive technology would compute as the button's accessible NAME.
// aria-label, when present, replaces the whole thing; otherwise the name is
// built from the child nodes - which is the only form that can keep language
// segmentation.  This is a DOM contract, not a screen-reader test: the harness
// computes no accessibility tree, and real AT name resolution stays a human
// check, exactly as this repository's other suites state.
function accName(btn) {
  var label = btn.getAttribute('aria-label');
  return label === null ? btn.textContent : label;
}
// What the button SHOWS, which is its accessible name minus the hidden verdict.
function visibleText(btn) {
  return btn.children.filter(function (n) {
    return !(n.classList && n.classList.contains('sr-only'));
  }).map(function (n) { return n.textContent; }).join('');
}
// The language runs an AT would traverse for that name, in order.
function nameLangs(btn) {
  if (btn.getAttribute('aria-label') !== null) return 'flattened';
  return btn.children.filter(function (n) { return (n.textContent || '') !== ''; })
    .map(function (n) {
      return [n.tag === '#text' ? null : n.getAttribute('lang'),
              n.classList && n.classList.contains('sr-only') ? 'sr-only' : null,
              n.textContent];
    });
}
var STYLE = (function () {
  var out = '', at = 0;
  while ((at = INDEX.indexOf('<style', at)) !== -1) {
    var s = INDEX.indexOf('>', at) + 1, e = INDEX.indexOf('</style>', s);
    out += INDEX.slice(s, e);
    at = e;
  }
  return out;
})();

// =========================================================================
// THE HARNESS.  The only place the synthetic exercise wrapper is ever opened.
// It asserts first and reads second: if the wrapper, its marker or its
// releaseAuthorized:false is missing, it throws rather than quietly consuming a
// bare or authorised-looking value.
// =========================================================================
var EXERCISE_MARKER = 'priority-7-exercise-fixture-synthetic-nonrelease';
var RUNTIME_MARKER = 'priority-7-runtime-projection-nonrelease-fixture';
var TEST_ID_PREFIX = 'p7-fixture-';
var RESERVED_ID_PREFIX = 'vp-';

function unwrapSyntheticExercisesForTest(wrapped) {
  if (!wrapped || typeof wrapped !== 'object' || Array.isArray(wrapped)) {
    throw new Error('harness: the exercise fixture is not an object');
  }
  if (wrapped.artifactStatus !== EXERCISE_MARKER) {
    throw new Error('harness: the non-release marker is missing');
  }
  if (wrapped.releaseAuthorized !== false) {
    throw new Error('harness: releaseAuthorized must be exactly false');
  }
  if (!wrapped.syntheticExercises || !Array.isArray(wrapped.syntheticExercises.items) ||
      !wrapped.syntheticExercises.items.length) {
    throw new Error('harness: the wrapper carries no synthetic items');
  }
  // Test identity, asserted before anything is injected: every identifier is
  // test-scoped and none of them sits in the reserved release family.
  wrapped.syntheticExercises.items.forEach(function (item) {
    [item.exerciseId, item.patternRef].forEach(function (id) {
      if (typeof id !== 'string' || id.indexOf(TEST_ID_PREFIX) !== 0) {
        throw new Error('harness: a fixture identifier is not test-scoped');
      }
      if (id.indexOf(RESERVED_ID_PREFIX) === 0) {
        throw new Error('harness: a fixture identifier is in the reserved family');
      }
    });
  });
  return clone(wrapped.syntheticExercises.items);
}
var ITEMS = unwrapSyntheticExercisesForTest(WRAPPED_EXERCISES);
function itemNamed(suffix) {
  var found = null;
  ITEMS.forEach(function (item) {
    if (item.exerciseId.indexOf(suffix) !== -1) found = clone(item);
  });
  if (!found) throw new Error('harness: no fixture item matching ' + suffix);
  return found;
}

// =========================================================================
// A. Harness boundary: the fixture is test-only and the shell cannot reach it.
// =========================================================================
eq('A1 the exercise fixture carries the non-release marker in its own bytes',
   WRAPPED_EXERCISES.artifactStatus, EXERCISE_MARKER);
eq('A1 the exercise fixture states it is not release-authorised',
   WRAPPED_EXERCISES.releaseAuthorized, false);
eq('A1 the harness refuses a fixture with no wrapper',
   [throws(function () { unwrapSyntheticExercisesForTest(WRAPPED_EXERCISES.syntheticExercises); }),
    throws(function () { unwrapSyntheticExercisesForTest(null); }),
    throws(function () { unwrapSyntheticExercisesForTest([]); }),
    throws(function () { unwrapSyntheticExercisesForTest('items'); })],
   [true, true, true, true]);
eq('A1 the harness refuses a tampered marker or authorisation flag', (function () {
  var noMarker = clone(WRAPPED_EXERCISES); delete noMarker.artifactStatus;
  var wrongMarker = clone(WRAPPED_EXERCISES); wrongMarker.artifactStatus = RUNTIME_MARKER;
  var authorised = clone(WRAPPED_EXERCISES); authorised.releaseAuthorized = true;
  var truthy = clone(WRAPPED_EXERCISES); truthy.releaseAuthorized = 'false';
  var empty = clone(WRAPPED_EXERCISES); empty.syntheticExercises.items = [];
  return [noMarker, wrongMarker, authorised, truthy, empty].map(function (doc) {
    return throws(function () { unwrapSyntheticExercisesForTest(doc); });
  });
})(), [true, true, true, true, true]);
eq('A1 the harness refuses an identifier in the reserved release family', (function () {
  var reserved = clone(WRAPPED_EXERCISES);
  reserved.syntheticExercises.items[0].exerciseId =
    'vp-x-fikcjonowac-grammar-choose-first-000000000000';
  var untagged = clone(WRAPPED_EXERCISES);
  untagged.syntheticExercises.items[0].patternRef = 'something-else';
  return [throws(function () { unwrapSyntheticExercisesForTest(reserved); }),
          throws(function () { unwrapSyntheticExercisesForTest(untagged); })];
})(), [true, true]);

// Every identifier in the committed fixture is test-scoped and none of them can
// be mistaken for, or reused as, a real Priority 7 exercise identity.
eq('A2 every fixture identifier is test-scoped and outside the reserved family',
   ITEMS.filter(function (item) {
     return item.exerciseId.indexOf(TEST_ID_PREFIX) !== 0 ||
            item.patternRef.indexOf(TEST_ID_PREFIX) !== 0 ||
            /^vp-/.test(item.exerciseId) || /^vp-/.test(item.patternRef);
   }).length, 0);
eq('A2 no fixture identifier resembles the reserved exercise family',
   ITEMS.filter(function (item) {
     return /vp-x-/.test(item.exerciseId) || /vp-p-/.test(item.patternRef);
   }).length, 0);
eq('A2 the fixture declares exactly one activity family',
   ITEMS.filter(function (item) { return item.activityType !== 'grammar-choose'; }).length, 0);

// The shipping shell can neither name nor reach the fixture.
eq('A3 the shipping app has no code path to a tests/ file or a fixture',
   countOf(INDEX, '"tests/') + countOf(INDEX, "'tests/") +
   countOf(INDEX, '"fixture') + countOf(INDEX, "'fixture") +
   countOf(INDEX, 'exercise-fixture') + countOf(INDEX, 'runtime-fixture'), 0);
eq('A3 the shipping app never names either non-release wrapper',
   countOf(INDEX, 'syntheticExercises') + countOf(INDEX, 'runtimeProjection') +
   countOf(INDEX, 'releaseAuthorized') + countOf(INDEX, 'artifactStatus') +
   countOf(INDEX, EXERCISE_MARKER), 0);
eq('A3 no developer switch, query parameter or fixture mode was added',
   countOf(INDEX, 'loadFixture') + countOf(INDEX, 'searchParams') +
   countOf(INDEX, 'URLSearchParams') + countOf(INDEX, '?fixture') +
   countOf(INDEX, 'localStorage.getItem("pp-dev') + countOf(INDEX, 'devMenu'), 0);
// SUPERSEDED by Priority 7 Phase 4F-I1, the atomic release. The choose
// prototype still adds nothing: the shell's third fetch is the one production
// runtime load, it names the official URL once, and no XHR was introduced.
eq('A3 the shipping app makes exactly the one production runtime request',
   [countOf(INDEX, 'fetch('), countOf(INDEX, 'verb-patterns.json'),
    countOf(INDEX, 'content/'), countOf(INDEX, 'XMLHttpRequest')], [3, 1, 1, 0]);
eq('A3 the loader never opens a wrapper either',
   countOf(LOADER_SRC, 'syntheticExercises') + countOf(LOADER_SRC, 'runtimeProjection') +
   countOf(LOADER_SRC, 'releaseAuthorized') + countOf(LOADER_SRC, 'artifactStatus="'), 0);

// The practice entry exists in the shell and is called by NOTHING in it.
eq('A4 the practice entry is defined exactly once and invoked nowhere',
   countOf(INDEX, 'pStartChoosePractice'), 1);
eq('A4 the adapter is referenced exactly once, by that entry',
   [countOf(INDEX, 'grammarChooseDrills'), countOf(INDEX, 'grammarChooseDrill(')], [1, 0]);
eq('A4 no tile, pill, route or level was added for it',
   [countOf(INDEX, 'LEVELS.push('), countOf(INDEX, 'level:"Verb Patterns"'),
    countOf(INDEX, 'CATEGORIES = ['), countOf(INDEX, 'kind:"patterns"')], [2, 1, 1, 1]);
eq('A4 the routing dispatch gained no branch for a practice kind',
   [countOf(stripComments(extractFunction(INDEX, 'routeTopic')), 'pStartChoosePractice'),
    countOf(stripComments(extractFunction(INDEX, 'routeTopic')), 'grammar-choose')], [0, 0]);
eq('A4 the established pattern and grammar screens remain singular',
   [countOf(INDEX, 'id="patterns"'), countOf(INDEX, 'id="grammar"')], [1, 1]);
eq('A4 the lemma entry renders no practice affordance',
   countOf(stripComments(extractFunction(INDEX, 'pRenderLemma')), 'Practice'), 0);

var ENTRY_CODE = stripComments(extractFunction(INDEX, 'pStartChoosePractice'));
eq('A5 the practice entry writes no storage and records no progress',
   countOf(ENTRY_CODE, 'localStorage') + countOf(ENTRY_CODE, 'sessionStorage') +
   countOf(ENTRY_CODE, 'rRecord') + countOf(ENTRY_CODE, 'saveV2') +
   countOf(ENTRY_CODE, 'persistProgress') + countOf(ENTRY_CODE, 'indexedDB'), 0);
eq('A5 the practice entry parses nothing and fetches nothing',
   countOf(ENTRY_CODE, 'JSON.parse') + countOf(ENTRY_CODE, 'fetch(') +
   countOf(ENTRY_CODE, 'innerHTML') + countOf(ENTRY_CODE, 'eval('), 0);
eq('A5 the practice entry adds no analytics of any kind',
   countOf(ENTRY_CODE, 'gtag') + countOf(ENTRY_CODE, 'analytics') +
   countOf(ENTRY_CODE, 'cookie') + countOf(ENTRY_CODE, 'navigator.send'), 0);
ok('A5 the practice entry fails closed before it starts anything',
   hasCode(ENTRY_CODE, 'if(!drills || !drills.length) return false;'));
ok('A5 the practice entry reuses the existing Grammar round rather than its own',
   ENTRY_CODE.indexOf('gStartPractice()') !== -1 &&
   ENTRY_CODE.indexOf('show("grammar", true)') !== -1);

// =========================================================================
// B. The adapter: deterministic mapping, and fail-closed on everything else.
// =========================================================================
PP_VERB_PATTERNS.reset();
var DRILLS = PP_VERB_PATTERNS.grammarChooseDrills(ITEMS);
ok('B1 the whole synthetic set maps to choose drills', !!DRILLS);
eq('B1 every fixture item is present exactly once', DRILLS.length, ITEMS.length);
eq('B1 every drill is a choose drill for the existing engine',
   DRILLS.filter(function (d) { return d.type !== 'choose'; }).length, 0);
eq('B1 every drill is flagged as data rather than authored markup',
   DRILLS.filter(function (d) { return d.textOnly !== true; }).length, 0);
eq('B1 the mapping is deterministic',
   JSON.stringify(PP_VERB_PATTERNS.grammarChooseDrills(ITEMS)), JSON.stringify(DRILLS));
eq('B1 items are ordered by their authored order, never by arrival',
   PP_VERB_PATTERNS.grammarChooseDrills(ITEMS.slice().reverse())
     .map(function (d) { return d.order; }),
   [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
eq('B1 every drill carries exactly one intended answer',
   DRILLS.filter(function (d) {
     return d.options.filter(function (o) { return o.value === d.answer; }).length !== 1;
   }).length, 0);
eq('B1 no drill carries an English feedback line it does not have',
   DRILLS.filter(function (d) { return d.fullEn !== ''; }).length, 0);
eq('B1 the instruction says the task is choosing a structure',
   DRILLS[0].instruction, 'Choose the pattern');

// The adapter must not consult - or be able to consult - pattern state.
var BEFORE_INJECTION = JSON.stringify(PP_VERB_PATTERNS.grammarChooseDrills(ITEMS));
PP_VERB_PATTERNS.__acceptForTest(clone(WRAPPED_RUNTIME.runtimeProjection));
eq('B2 the adapter answers identically with and without accepted pattern data',
   JSON.stringify(PP_VERB_PATTERNS.grammarChooseDrills(ITEMS)), BEFORE_INJECTION);
// Eligibility is a separate, explicit allowlist that defaults closed.  Running
// the adapter must neither consult it nor move it: a pattern whose allowlist is
// empty still answers `false` afterwards, and one that lists the activity still
// answers `true` - the adapter simply is not part of that question.
eq('B2 running the adapter changes no eligibility answer either way', (function () {
  var closed = { activityEligibility: [], teachingStatus: 'active-production' };
  var open = { activityEligibility: ['grammar-choose'], teachingStatus: 'active-production' };
  var before = [PP_VERB_PATTERNS.eligibleFor(closed, 'grammar-choose'),
                PP_VERB_PATTERNS.eligibleFor(open, 'grammar-choose')];
  PP_VERB_PATTERNS.grammarChooseDrills(ITEMS);
  var after = [PP_VERB_PATTERNS.eligibleFor(closed, 'grammar-choose'),
               PP_VERB_PATTERNS.eligibleFor(open, 'grammar-choose')];
  return [before, after];
})(), [[false, true], [false, true]]);
eq('B2 an item maps whether or not any pattern allowlist mentions the activity',
   [!!PP_VERB_PATTERNS.grammarChooseDrill(itemNamed('choose-01')),
    PP_VERB_PATTERNS.eligibleFor(
      { activityEligibility: [], teachingStatus: 'active-production' }, 'grammar-choose')],
   [true, false]);
var ADAPTER_SRC = LOADER_SRC.slice(
  LOADER_SRC.indexOf('function grammarChooseDrill(item)'),
  LOADER_SRC.indexOf('function patternOrder('));
eq('B2 the adapter reads no pattern state, allowlist or teaching status',
   countOf(ADAPTER_SRC, 'STATE') + countOf(ADAPTER_SRC, 'eligibleFor') +
   countOf(ADAPTER_SRC, 'activityEligibility') + countOf(ADAPTER_SRC, 'teachingStatus') +
   countOf(ADAPTER_SRC, 'cefr') + countOf(ADAPTER_SRC, 'contentRefs') +
   countOf(ADAPTER_SRC, 'api.available'), 0);
PP_VERB_PATTERNS.reset();

// Fail-closed: every rejection returns null, and null starts nothing.
function rejected(name, mutate) {
  var item = itemNamed('choose-01');
  mutate(item);
  eq('B3 ' + name + ' fails closed for one item',
     PP_VERB_PATTERNS.grammarChooseDrill(item), null);
  eq('B3 ' + name + ' fails the whole set closed',
     PP_VERB_PATTERNS.grammarChooseDrills([item, itemNamed('choose-02')]), null);
}
eq('B3 a value that is not an object at all is refused',
   [PP_VERB_PATTERNS.grammarChooseDrill(null), PP_VERB_PATTERNS.grammarChooseDrill([]),
    PP_VERB_PATTERNS.grammarChooseDrill('item'), PP_VERB_PATTERNS.grammarChooseDrill(7),
    PP_VERB_PATTERNS.grammarChooseDrill(undefined)],
   [null, null, null, null, null]);
eq('B3 an empty, absent or non-array set is refused',
   [PP_VERB_PATTERNS.grammarChooseDrills([]), PP_VERB_PATTERNS.grammarChooseDrills(null),
    PP_VERB_PATTERNS.grammarChooseDrills({ items: [] }),
    PP_VERB_PATTERNS.grammarChooseDrills('items')],
   [null, null, null, null]);
rejected('an unsupported activity kind',
         function (i) { i.activityType = 'grammar-build'; });
rejected('a misspelled activity kind',
         function (i) { i.activityType = 'grammar-Choose'; });
rejected('an absent activity kind', function (i) { delete i.activityType; });
rejected('a non-string activity kind', function (i) { i.activityType = 1; });
rejected('a missing correct option',
         function (i) { i.answerValue = 'opt-that-is-not-there'; });
rejected('an absent answer', function (i) { delete i.answerValue; });
rejected('an empty answer', function (i) { i.answerValue = ''; });
rejected('two options claiming the same identity',
         function (i) { i.options[1].value = i.options[0].value; });
rejected('two options that are both the answer', function (i) {
  i.options[1].value = i.options[0].value + '-copy';
  i.answerValue = i.options[0].value;
  i.options[1].value = i.options[0].value;
});
rejected('a single option', function (i) { i.options = [i.options[0]]; });
rejected('no options at all', function (i) { i.options = []; });
rejected('an option that is not an object', function (i) { i.options[1] = 'plain'; });
rejected('an option with no label', function (i) { delete i.options[1].label; });
rejected('an option with an empty label', function (i) { i.options[1].label = ''; });
rejected('an option with an extra field',
         function (i) { i.options[1].correct = true; });
rejected('an identifier in the reserved release family',
         function (i) { i.exerciseId = 'vp-x-something-grammar-choose-key-0123456789ab'; });
rejected('a pattern reference in the reserved release family',
         function (i) { i.patternRef = 'vp-p-something-0123456789ab'; });
rejected('an absent identifier', function (i) { delete i.exerciseId; });
rejected('an unknown extra field', function (i) { i.reviewNote = 'anything'; });
rejected('a private editorial field at the top level',
         function (i) { i.reviewState = 'research'; });
rejected('a private editorial field nested inside an option',
         function (i) { i.options[0].evidence = [{ sourceId: 's' }]; });
rejected('an absent prompt', function (i) { delete i.prompt; });
rejected('an empty prompt', function (i) { i.prompt = ''; });
rejected('an absent explanation', function (i) { delete i.feedbackExplanation; });
rejected('an absent structural feedback line',
         function (i) { delete i.feedbackStructure; });
rejected('a non-integer order', function (i) { i.order = 1.5; });
rejected('a zero order', function (i) { i.order = 0; });
rejected('a negative order', function (i) { i.order = -1; });
eq('B4 the whole wrapped fixture is refused as an item',
   [PP_VERB_PATTERNS.grammarChooseDrill(WRAPPED_EXERCISES),
    PP_VERB_PATTERNS.grammarChooseDrills([WRAPPED_EXERCISES]),
    PP_VERB_PATTERNS.grammarChooseDrills([WRAPPED_EXERCISES.syntheticExercises])],
   [null, null, null]);
eq('B4 a runtime pattern record is not an exercise item',
   PP_VERB_PATTERNS.grammarChooseDrill(
     WRAPPED_RUNTIME.runtimeProjection.lemmas[0].meanings[0].patterns[0]), null);
eq('B4 duplicate identifiers fail the set closed',
   PP_VERB_PATTERNS.grammarChooseDrills([itemNamed('choose-01'), itemNamed('choose-01')]),
   null);
eq('B4 duplicate orders fail the set closed', (function () {
  var second = itemNamed('choose-02');
  second.order = 1;
  return PP_VERB_PATTERNS.grammarChooseDrills([itemNamed('choose-01'), second]);
})(), null);
eq('B4 one bad record in an otherwise good set starts nothing', (function () {
  var bad = itemNamed('choose-03');
  bad.activityType = 'type-it';
  return PP_VERB_PATTERNS.grammarChooseDrills(
    [itemNamed('choose-01'), bad, itemNamed('choose-02')]);
})(), null);
eq('B4 the adapter never repairs, never guesses and never invents an answer',
   countOf(ADAPTER_SRC, 'Math.random') + countOf(ADAPTER_SRC, 'shuffle') +
   countOf(ADAPTER_SRC, '|| "') + countOf(ADAPTER_SRC, 'toLowerCase'), 0);

// =========================================================================
// FAKE DOM.  Browser rules this interaction depends on: a disabled or hidden
// element cannot take focus, disabling the focused control hands focus to
// <body>, and textContent is text.
// =========================================================================
var BODY = null;
function El(tag, id) {
  this.tag = tag; this.id = id || ''; this.className = '';
  this.children = []; this.parentElement = null; this._text = '';
  this.attrs = {}; this.listeners = {}; this._disabled = false;
  this.hidden = false; this.inert = false; this.style = {};
  this.focusCount = 0; this.revealCount = 0; this.connected = true;
  var self = this;
  this.classList = {
    add: function (c) { self.className = (self.className + ' ' + c).trim(); },
    remove: function (c) {
      self.className = self.className.split(/\s+/).filter(function (x) {
        return x && x !== c;
      }).join(' ');
    },
    contains: function (c) { return self.className.split(/\s+/).indexOf(c) !== -1; }
  };
}
Object.defineProperty(El.prototype, 'disabled', {
  get: function () { return this._disabled; },
  set: function (v) {
    this._disabled = !!v;
    if (this._disabled && fakeDocument.activeElement === this) fakeDocument.activeElement = BODY;
  }
});
El.prototype.appendChild = function (child) {
  child.parentElement = this; child.connected = true; this.children.push(child);
  return child;
};
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.addEventListener = function (type, handler) {
  (this.listeners[type] = this.listeners[type] || []).push(handler);
};
El.prototype.fire = function (type) {
  var self = this;
  if (typeof this['on' + type] === 'function') this['on' + type]();
  (this.listeners[type] || []).forEach(function (h) { h.call(self, { target: self }); });
};
El.prototype.click = function () { this.fire('click'); };
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
  if (selector.charAt(0) === '#') return this.id === selector.slice(1);
  if (selector.charAt(0) === '.') return this.classList.contains(selector.slice(1));
  return this.tag === selector;
};
El.prototype.querySelectorAll = function (selector) {
  return this.descendants().filter(function (n) { return n.matches && n.matches(selector); });
};
El.prototype.querySelector = function (selector) {
  return this.querySelectorAll(selector)[0] || null;
};
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
    if (node.style && node.style.display === 'none') return;
    if (node.classList.contains('screen') && !node.classList.contains('active')) return;
  }
  this.focusCount++;
  this.lastFocusOptions = options || null;
  fakeDocument.activeElement = this;
};
El.prototype.scrollIntoView = function () { this.revealCount++; };
// innerHTML exists here only so an unexpected markup write is VISIBLE rather
// than silently landing on a plain property.  Nothing parses it: the authored
// markup path is owned by tests/test_grammar_interaction.js, which has a parser.
Object.defineProperty(El.prototype, 'innerHTML', {
  get: function () { return this._html || ''; },
  set: function (value) {
    this._html = String(value);
    this.htmlWrites = (this.htmlWrites || 0) + 1;
    this.children = [];
    this._text = '';
  }
});
Object.defineProperty(El.prototype, 'textContent', {
  get: function () {
    return this._text + this.children.map(function (c) { return c.textContent; }).join('');
  },
  set: function (value) { this.children = []; this._text = String(value); }
});
function TextNode(value) { this.tag = '#text'; this._text = String(value); this.children = []; }
Object.defineProperty(TextNode.prototype, 'textContent', {
  get: function () { return this._text; },
  set: function (value) { this._text = String(value); }
});
TextNode.prototype.matches = function () { return false; };
TextNode.prototype.descendants = function () { return []; };

var REGISTRY = {};
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
var SCREENS = { active: null };
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
BODY = fakeDocument.body;
// No getComputedStyle, so ppIsHiddenOrInert falls back to the explicit checks -
// exactly the branch a headless run must take.
var fakeWindow = { getComputedStyle: null, scrollTo: function () {} };

function register(el) { REGISTRY[el.id] = el; return el; }
var grammarScreen = register(new El('section', 'grammar'));
grammarScreen.classList.add('screen');
grammarScreen.classList.add('active');
fakeDocument.body.appendChild(grammarScreen);
SCREENS.active = grammarScreen;
function child(parent, tag, id) {
  return parent.appendChild(register(new El(tag, id)));
}
child(grammarScreen, 'h1', 'gTitle');
child(grammarScreen, 'span', 'gPhase');
var gProgress = child(grammarScreen, 'div', 'gProgress');
child(gProgress, 'div', 'gFill');
child(gProgress, 'div', 'gCount');
var gLearn = child(grammarScreen, 'div', 'gLearn');
var gPractice = child(grammarScreen, 'div', 'gPractice');
var gDrillCard = child(gPractice, 'div', 'gDrillCard');
var gStatus = child(gPractice, 'div', 'gStatus');
var gDrillNext = child(gPractice, 'button', 'gDrillNext');
gDrillNext.disabled = true;
child(gDrillNext, 'span', 'gDrillNextLabel');
var gDone = child(grammarScreen, 'div', 'gDone');
child(gDone, 'h2', 'gDoneTitle');
child(gDone, 'p', 'gDoneMsg');
child(gDone, 'span', 'gScore');
child(gDone, 'span', 'gTotal');
child(gDone, 'button', 'gAgain');
child(gDone, 'button', 'gReview');
child(gDone, 'button', 'gHome');
var gPatternLine = child(gDone, 'div', 'gPatternLine');
var gPatternLink = child(gPatternLine, 'button', 'gPatternLink');
child(gPatternLink, 'span', 'gPatternLabel');
var gPatternCaseName = child(gPatternLink, 'span', 'gPatternCaseName');
gPatternCaseName.classList.add('sr-only');
gPatternCaseName.setAttribute('lang', 'pl');

// The shipping activity helpers, taken whole rather than re-implemented.
var FOCUS_BLOCK = sliceBetween(INDEX, 'var ppScreenReturnTargets = new Map();',
                               "/* ---------------- the app's one screen-scroll contract");
var GNAMES = [
  'gPhaseView', 'gStartPractice', 'gUpdateNextLabel', 'gRenderDrill',
  'gOptionValue', 'gOptionLabel', 'gOptionLang', 'gTextEl', 'gAppendDrillText',
  'gPaintChooseText', 'gPaintChooseFeedbackText', 'gRenderChoose',
  'gSetStatus', 'gAnnounceWrong', 'gAnnounceCorrect', 'gAnnounceRevealed',
  'gFocusNextOption', 'gRevealChooseAnswer', 'gChooseFeedback', 'gDrillAdvance',
  'gHasLesson', 'gShowDone', 'gPatternContinuation', 'gRenderPatternLink',
  'gRetryOutcome', 'gDoneMessage', 'gTextFragments', 'gFragmentText',
  'gAppendFragment', 'gAppendTextParts', 'gChooseOptionLabel', 'gSetOptionVerdict'
];
var GSRC = GNAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n');
var ENV = { shows: [], shuffle: function (a) { return a.slice(); } };
var APP = Function(
  'document', 'window', '$', 'PP_VERB_PATTERNS', 'env',
  'var G = { topic:null, li:0, tpi:0, ti:0, di:0, results:[], attempted:false,' +
  ' state:"ask", build:{pool:[],row:[]} };\n' +
  'function show(scr, defer){ env.shows.push([scr, defer]); return true; }\n' +
  'function gShuffle(a){ return env.shuffle(a); }\n' +
  'function gSampleMix(){ throw new Error("a synthetic set is never a mix topic"); }\n' +
  'function gRenderBuild(){ env.builtInstead = (env.builtInstead||0)+1; }\n' +
  'function gRenderTeach(){ throw new Error("a set with no lesson has nothing to teach"); }\n' +
  'function ppSetAudioControlName(){ env.audioNamed = (env.audioNamed||0)+1; }\n' +
  'var G_AUDIO = "<svg></svg>";\n' +
  FOCUS_BLOCK + '\n' + GSRC + '\n' +
  extractFunction(INDEX, 'pStartChoosePractice') + '\n' +
  'return { G: G, start: pStartChoosePractice, renderDrill: gRenderDrill,' +
  ' advance: gDrillAdvance, hasLesson: gHasLesson, showDone: gShowDone,' +
  ' phaseView: gPhaseView, startRound: gStartPractice, renderChoose: gRenderChoose };'
)(fakeDocument, fakeWindow, lookup, PP_VERB_PATTERNS, ENV);

function opts() {
  var box = gDrillCard.querySelector('.opts');
  return box ? box.querySelectorAll('.opt') : [];
}
function byValue(value) {
  return opts().filter(function (b) { return b.getAttribute('data-val') === value; })[0] || null;
}
function statusText() { return gStatus.textContent; }
function feedbackBox() { return gDrillCard.querySelector('.fb-box'); }
function drillNodes() { return gDrillCard.descendants(); }
function nodeTags() {
  var seen = {};
  drillNodes().forEach(function (n) { if (n.tag) seen[n.tag] = true; });
  return Object.keys(seen).sort();
}
function startWith(items) {
  ENV.shows = [];
  fakeDocument.activeElement = BODY;
  return APP.start(items);
}

// =========================================================================
// C. The round runs on the existing Grammar engine, and only on it.
// =========================================================================
eq('C1 a good synthetic set starts the round on the Grammar screen',
   [startWith(ITEMS), ENV.shows], [true, [['grammar', true]]]);
eq('C1 the round is queued by the existing Grammar practice starter',
   [APP.G.queue.length, APP.G.di, APP.G.results.length], [10, 0, 0]);
eq('C1 the engine chose the choose renderer and never fell through to build',
   ENV.builtInstead, undefined);
eq('C1 the practice phase is the visible one',
   [gPractice.style.display, gLearn.style.display, gDone.style.display],
   ['flex', 'none', 'none']);
eq('C1 the round has no lesson behind it, so Back will leave rather than teach',
   APP.hasLesson(), false);
eq('C2 an unusable set starts nothing at all', (function () {
  var bad = itemNamed('choose-01');
  delete bad.answerValue;
  ENV.shows = [];
  return [startWith([bad]), ENV.shows.length];
})(), [false, 0]);
eq('C2 an empty or absent set starts nothing',
   [startWith([]), startWith(null), startWith('items')], [false, false, false]);
startWith(ITEMS);

// The first item, rendered by the shipping choose renderer.
eq('C3 the instruction, prompt and meaning are all present',
   [lookup('gInstruction').textContent, lookup('gQuestion').textContent,
    lookup('gQuestionMeaning').textContent.indexOf('SYNTHETIC-NONRELEASE') === 0],
   ['Choose the pattern', 'Fikcjonuje  .', true]);
eq('C3 the blank survives as a real element rather than as parsed markup',
   lookup('gQuestion').querySelectorAll('.blank').length, 1);
eq('C3 every option is a native button with an explicit identity',
   [opts().length, opts().filter(function (b) { return b.tag !== 'button'; }).length,
    opts().map(function (b) { return b.getAttribute('data-val'); })],
   [3, 0, ['opt-01-accusative', 'opt-01-genitive', 'opt-01-instrumental']]);
eq('C3 every option shows its own label and nothing else',
   opts().map(function (b) { return b.textContent; }),
   ['kogo? co? · Accusative', 'kogo? czego? · Genitive', 'kim? czym? · Instrumental']);
eq('C3 no option is pre-selected and none is pre-disabled',
   [opts().filter(function (b) { return b.getAttribute('aria-pressed') !== 'false'; }).length,
    opts().filter(function (b) { return b.disabled; }).length], [0, 0]);
eq('C3 feedback is not shown before an answer',
   [feedbackBox().textContent, feedbackBox().classList.contains('show')], ['', false]);
eq('C3 Next is unavailable until the item is answered', lookup('gDrillNext').disabled, true);
eq('C3 the prompt takes focus on entry, ahead of the options',
   fakeDocument.activeElement === lookup('gQuestion'), true);
eq('C3 the option group is labelled by the instruction and the prompt',
   gDrillCard.querySelector('.opts').getAttribute('aria-labelledby'),
   'gInstruction gQuestion');

// C4 - the correct answer, first time.  Unchanged by the correction.
byValue('opt-01-accusative').fire('click');
eq('C4 the correct option is marked correct and said to be correct in words',
   [byValue('opt-01-accusative').classList.contains('correct'),
    byValue('opt-01-accusative').getAttribute('aria-label'),
    accName(byValue('opt-01-accusative'))],
   [true, null, 'kogo? co? · Accusative, correct']);
eq('C4 the verdict joins the computed name instead of replacing it',
   nameLangs(byValue('opt-01-accusative')),
   [['pl', null, 'kogo? co?'], [null, null, ' · Accusative'],
    [null, 'sr-only', ', correct']]);
eq('C4 every option is disabled once the item is settled',
   opts().filter(function (b) { return !b.disabled; }).length, 0);
eq('C4 exactly one option is left in the selected state',
   opts().filter(function (b) { return b.getAttribute('aria-pressed') === 'true'; }).length, 1);
eq('C4 the correct verdict is announced in words',
   [statusText().indexOf('Correct.') === 0,
    statusText().indexOf('kogo? co? · Accusative') !== -1,
    statusText().indexOf('Next is ready') !== -1], [true, true, true]);
eq('C4 Next becomes available and takes focus',
   [lookup('gDrillNext').disabled, fakeDocument.activeElement === lookup('gDrillNext')],
   [false, true]);
eq('C4 a first-time correct answer counts towards the score', APP.G.results[0], true);
eq('C4 the correct path never enters the revealed state',
   gDrillCard.querySelector('.opts').classList.contains('revealed'), false);
eq('C4 a second click after the item is settled changes nothing', (function () {
  var before = [statusText(), feedbackBox().textContent];
  byValue('opt-01-genitive').fire('click');
  return [statusText() === before[0], feedbackBox().textContent === before[1],
          byValue('opt-01-genitive').classList.contains('wrong')];
})(), [true, true, false]);

// =========================================================================
// C5 - THE CORRECTED INCORRECT FLOW.
//   wrong choice -> incorrect verdict -> reveal the correct structure and the
//   explanation -> every choice closed -> Next.
// The learner does not brute-force the remaining options inside one
// presentation, and is not made to click the answer they have already been
// shown.  The miss is still banked, so the round's own requeue rule is
// untouched (section F).
// =========================================================================
startWith(ITEMS);
byValue('opt-01-genitive').fire('click');
eq('C5 the chosen option is marked incorrect and said so without a retry promise',
   [byValue('opt-01-genitive').classList.contains('wrong'),
    byValue('opt-01-genitive').getAttribute('aria-pressed'),
    byValue('opt-01-genitive').getAttribute('aria-label'),
    accName(byValue('opt-01-genitive'))],
   [true, 'true', null, 'kogo? czego? · Genitive, incorrect']);
eq('C5 the incorrect verdict is stated in words',
   [statusText().indexOf('kogo? czego? · Genitive is not correct.') === 0,
    statusText().indexOf('The answer is kogo? co? · Accusative') !== -1,
    statusText().indexOf('Explanation available below') !== -1,
    statusText().indexOf('Next is ready') !== -1], [true, true, true, true]);
eq('C5 the correct option becomes identifiable, and not by colour alone',
   [byValue('opt-01-accusative').classList.contains('correct'),
    accName(byValue('opt-01-accusative')),
    byValue('opt-01-accusative').getAttribute('aria-label'),
    byValue('opt-01-accusative').getAttribute('aria-pressed')],
   [true, 'kogo? co? · Accusative, correct answer', null, 'false']);
eq('C5 every option is closed, so nothing can be brute-forced',
   [opts().filter(function (b) { return !b.disabled; }).length, APP.G.state],
   [0, 'done']);
eq('C5 a further click on any remaining option does nothing at all', (function () {
  var before = [statusText(), feedbackBox().textContent,
                opts().map(function (b) { return b.className; }).join('|')];
  opts().forEach(function (b) { b.fire('click'); });
  return [statusText() === before[0], feedbackBox().textContent === before[1],
          opts().map(function (b) { return b.className; }).join('|') === before[2]];
})(), [true, true, true]);
eq('C5 the feedback region is revealed by the miss itself',
   [feedbackBox().classList.contains('show'),
    feedbackBox().querySelector('.fb-good').textContent,
    feedbackBox().querySelector('.fb-explain').textContent.indexOf(
      'SYNTHETIC-NONRELEASE: inside this fixture') === 0],
   [true, 'fikcjonowac + kogo? co? · Accusative', true]);
eq('C5 the option row enters the revealed state, so the wrong option stops promising a retry',
   [gDrillCard.querySelector('.opts').classList.contains('revealed'),
    STYLE.indexOf('.opts.revealed .opt.wrong::after{content:"\\2715\\00a0 Incorrect"}') !== -1],
   [true, true]);
eq('C5 Next becomes available and takes focus, and nothing is stranded',
   [lookup('gDrillNext').disabled,
    fakeDocument.activeElement === lookup('gDrillNext'),
    fakeDocument.activeElement === BODY], [false, true, false]);
eq('C5 the miss is banked in memory for this item only',
   [APP.G.results[0], APP.G.attempted, APP.G.results.length], [false, true, 1]);
eq('C5 the learner is never sent back to click the answer they were shown',
   [opts().filter(function (b) { return !b.disabled; }).length,
    lookup('gDrillNextLabel').textContent], [0, 'Next']);

// =========================================================================
// D. Feedback: correct, incorrect, the structure, and one short explanation.
// =========================================================================
eq('D1 the feedback region is revealed only after the answer',
   feedbackBox().classList.contains('show'), true);
eq('D1 the feedback names the correct structural pattern',
   feedbackBox().querySelector('.fb-good').textContent,
   'fikcjonowac + kogo? co? · Accusative');
eq('D1 the feedback carries one short learner-facing explanation',
   feedbackBox().querySelector('.fb-explain').textContent.indexOf(
     'SYNTHETIC-NONRELEASE: inside this fixture') === 0, true);
eq('D1 the feedback offers no audio control and names none',
   [feedbackBox().querySelectorAll('.mini-audio').length,
    feedbackBox().descendants().filter(function (n) {
      return n.getAttribute && n.getAttribute('data-say') !== null;
    }).length, ENV.audioNamed], [0, 0, undefined]);
eq('D1 the feedback region is not a second live region',
   [feedbackBox().getAttribute('aria-live'), feedbackBox().getAttribute('role')],
   [null, null]);
eq('D1 the empty English line is not rendered as an empty row',
   feedbackBox().querySelectorAll('.e').length, 0);
// The same feedback, reached either way: a miss now shows exactly what a correct
// answer shows, so the learner who missed is not told less than the one who did not.
eq('D2 the correct path and the revealed path show identical feedback', (function () {
  var revealed = feedbackBox().textContent;
  startWith(ITEMS);
  byValue('opt-01-accusative').fire('click');
  return feedbackBox().textContent === revealed;
})(), true);
eq('D2 neither path offers an audio control',
   [feedbackBox().querySelectorAll('.mini-audio').length, ENV.audioNamed],
   [0, undefined]);

// =========================================================================
// E. Explicit option identity: the label is never the key.
// =========================================================================
var TWIN = {
  exerciseId: 'p7-fixture-x-choose-twin-labels',
  patternRef: 'p7-fixture-pattern-twin-labels',
  activityType: 'grammar-choose', order: 1,
  prompt: 'Zetafikcjonuje ___ .',
  options: [
    { value: 'opt-twin-right', label: 'kogo? co? · Accusative' },
    { value: 'opt-twin-wrong', label: 'kogo? co? · Accusative' }
  ],
  answerValue: 'opt-twin-right',
  feedbackStructure: 'zetafikcjonowac + kogo? co? · Accusative',
  feedbackExplanation: 'SYNTHETIC-NONRELEASE: identical labels, different answers.'
};
startWith([TWIN]);
eq('E1 two options may read identically and remain different answers',
   [opts().length, opts()[0].textContent === opts()[1].textContent,
    opts().map(function (b) { return b.getAttribute('data-val'); })],
   [2, true, ['opt-twin-right', 'opt-twin-wrong']]);
byValue('opt-twin-wrong').fire('click');
eq('E1 the option that merely reads correct is scored wrong',
   [byValue('opt-twin-wrong').classList.contains('wrong'), APP.G.results[0]],
   [true, false]);
// The reveal has to identify the right option by IDENTITY, not by its words:
// both options read the same, so a renderer that matched on text would mark the
// wrong one - or both.
eq('E1 the reveal marks the correct option by identity, not by its label',
   [byValue('opt-twin-right').classList.contains('correct'),
    byValue('opt-twin-wrong').classList.contains('correct'),
    opts().filter(function (b) { return b.classList.contains('correct'); }).length],
   [true, false, 1]);
startWith([TWIN]);
byValue('opt-twin-right').fire('click');
eq('E1 the option that IS correct is scored correct',
   [byValue('opt-twin-right').classList.contains('correct'), APP.G.state,
    APP.G.results[0]], [true, 'done', true]);
// Option order must never become the scoring key.
ENV.shuffle = function (a) { return a.slice().reverse(); };
startWith([TWIN]);
eq('E2 reversing the presented order does not move the answer',
   opts().map(function (b) { return b.getAttribute('data-val'); }),
   ['opt-twin-wrong', 'opt-twin-right']);
byValue('opt-twin-right').fire('click');
eq('E2 the same option is still the correct one after reordering',
   [byValue('opt-twin-right').classList.contains('correct'), APP.G.results[0]],
   [true, true]);
ENV.shuffle = function (a) { return a.slice(); };

// =========================================================================
// F. Progression, requeue and the end of the session.
// =========================================================================
var THREE = [itemNamed('choose-01'), itemNamed('choose-02'), itemNamed('choose-03')];
startWith(THREE);
function answerCurrent(correctly) {
  var drill = APP.G.queue[APP.G.di];
  var target = correctly ? drill.answer
    : drill.options.filter(function (o) { return o.value !== drill.answer; })[0].value;
  byValue(target).fire('click');
  return target;
}
eq('F1 the first item is announced as one of three',
   [lookup('gPhase').textContent, lookup('gCount').textContent],
   ['Practice · 1 of 3', '1 / 3']);
answerCurrent(true);
eq('F1 Next reads Next while items remain',
   lookup('gDrillNextLabel').textContent, 'Next');
APP.advance();
eq('F2 advancing renders the next item and clears the prior verdict',
   [APP.G.di, statusText(), lookup('gQuestion').textContent.indexOf('Metoduje o') === 0],
   [1, '', true]);
eq('F2 the new item starts unanswered', [APP.G.state, APP.G.attempted], ['ask', false]);
eq('F2 the cue is rendered beside the instruction as text',
   [lookup('gInstruction').textContent,
    lookup('gInstruction').querySelectorAll('b').length],
   ['Choose the pattern · Preposition + case', 1]);
// One wrong choice ends this presentation - and only this presentation.  The
// round's own requeue rule is untouched by the correction, which is the point:
// the item still comes back, it just is not brute-forced on the way there.
answerCurrent(false);
eq('F3 one miss ends the presentation without ending the item',
   [APP.G.state, opts().filter(function (b) { return !b.disabled; }).length,
    lookup('gDrillNext').disabled, lookup('gDrillNextLabel').textContent],
   ['done', 0, false, 'Next']);
APP.advance();
eq('F3 the missed item came back exactly once',
   [APP.G.queue.length, APP.G.queue[3] && APP.G.queue[3]._requeue,
    APP.G.queue[3] && APP.G.queue[3].exerciseId === APP.G.queue[1].exerciseId],
   [4, true, true]);
eq('F3 the requeue rule is the existing engine rule, not a new one',
   [hasCode(stripComments(extractFunction(INDEX, 'gDrillAdvance')),
            'G.queue.push(Object.assign({}, c, { _requeue:true }));'),
    countOf(stripComments(extractFunction(INDEX, 'gDrillAdvance')), 'G.queue.push(')],
   [true, 1]);
eq('F3 the next presentation starts open again, with nothing revealed',
   [APP.G.state, APP.G.attempted, feedbackBox().textContent,
    gDrillCard.querySelector('.opts').classList.contains('revealed')],
   ['ask', false, '', false]);
answerCurrent(true);
APP.advance();
eq('F4 the retry is the last item and Next offers the results',
   [APP.G.di, lookup('gDrillNextLabel').textContent], [3, 'See results']);
answerCurrent(true);
APP.advance();
eq('F5 the round ends on the existing completion panel',
   [gDone.style.display, gPractice.style.display, gProgress.style.display],
   ['flex', 'none', 'none']);
eq('F5 the score counts originals only and excludes the retry',
   [lookup('gScore').textContent, lookup('gTotal').textContent], ['2', '3']);
eq('F5 completion focuses the completion heading',
   fakeDocument.activeElement === lookup('gDoneTitle'), true);
eq('F5 the completion copy claims no mastery and no persistence',
   ['master', 'saved', 'progress', 'unlock', 'complete for good', 'approved']
     .filter(function (word) {
       return (lookup('gDoneMsg').textContent + ' ' + lookup('gDoneTitle').textContent)
         .toLowerCase().indexOf(word) !== -1;
     }), []);
eq('F5 a set with no lesson offers no control that would open one',
   [lookup('gReview').hidden, APP.hasLesson()], [true, false]);
eq('F5 the completion panel offers no pattern continuation either',
   gPatternLine.hidden, true);
eq('F5 the verdict region is cleared at the end of the round', statusText(), '');

// The same completion panel, for an ordinary authored topic, is unchanged.
eq('F6 a topic that HAS a lesson still offers Review the lesson', (function () {
  APP.G.topic = { name: 'Authored', teach: [{ front: 'authored' }], drills: [] };
  APP.showDone();
  return [lookup('gReview').hidden, APP.hasLesson()];
})(), [false, true]);

// =========================================================================
// G. Injection safety: every synthetic string is data, and stays data.
// =========================================================================
var HOSTILE = itemNamed('choose-09');
startWith([HOSTILE]);
// The one thing the renderer is allowed to change about a prompt is the blank,
// which it creates itself as an element; every other character survives exactly.
eq('G1 a hostile prompt is rendered verbatim as text',
   lookup('gQuestion').textContent, flat(HOSTILE.prompt).split('___').join(''));
// Everything the renderer added to the prompt is either the blank it creates
// itself or a language span carrying nothing but a lang - the hostile payload
// survives INSIDE a lang="pl" fragment and is still only ever text.
eq('G1 the blank and the language spans are all the renderer added to the prompt',
   [lookup('gQuestion').querySelectorAll('.blank').length,
    lookup('gQuestion').children
      .filter(function (n) { return n.tag !== '#text' && !n.classList.contains('blank'); })
      .map(function (n) { return [n.tag, Object.keys(n.attrs).sort().join(','), n.children.length]; })],
   [1, [['span', 'lang', 0], ['span', 'lang', 0]]]);
eq('G1 a hostile option label is rendered verbatim as text',
   byValue('opt-09-hostile').textContent,
   flat(HOSTILE.options.filter(function (o) { return o.value === 'opt-09-hostile'; })[0].label));
eq('G1 a hostile cue is rendered verbatim as text',
   lookup('gInstruction').textContent.indexOf(flat(HOSTILE.cue)) !== -1, true);
byValue('opt-09-hostile').fire('click');
eq('G1 hostile feedback and explanation are rendered verbatim as text',
   [feedbackBox().querySelector('.fb-good').textContent,
    feedbackBox().querySelector('.fb-explain').textContent],
   [flat(HOSTILE.feedbackStructure), flat(HOSTILE.feedbackExplanation)]);
eq('G2 no element was created that the renderer did not create itself',
   nodeTags().filter(function (tag) {
     return ['div', 'h2', 'span', 'button', 'b', '#text'].indexOf(tag) === -1;
   }), []);
eq('G2 no img, script, iframe, a or style node was injected',
   ['img', 'script', 'iframe', 'a', 'style', 'svg', 'object', 'embed']
     .filter(function (tag) { return gDrillCard.querySelectorAll(tag).length > 0; }), []);
eq('G2 no event-handler attribute was created anywhere in the card',
   drillNodes().filter(function (n) {
     return n.attrs && Object.keys(n.attrs).some(function (a) { return /^on/i.test(a); });
   }).length, 0);
eq('G2 no href, src or javascript: URL reached an attribute',
   drillNodes().filter(function (n) {
     if (!n.attrs) return false;
     return Object.keys(n.attrs).some(function (a) {
       return a === 'href' || a === 'src' || /javascript:/i.test(n.attrs[a]);
     });
   }).length, 0);
eq('G2 the hostile payload never executed',
   [typeof fakeWindow.__p7Pwned, typeof globalThis.__p7Pwned],
   ['undefined', 'undefined']);
var TEXT_PAINTERS = ['gPaintChooseText', 'gPaintChooseFeedbackText', 'gAppendDrillText',
                     'gTextEl'];
eq('G3 the data painters never touch a markup API',
   TEXT_PAINTERS.filter(function (name) {
     var src = stripComments(extractFunction(INDEX, name));
     return ['innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write',
             'eval(', 'srcdoc'].some(function (t) { return src.indexOf(t) !== -1; });
   }), []);
ok('G3 the data path is chosen before any string is placed',
   hasCode(stripComments(extractFunction(INDEX, 'gRenderChoose')),
           'if(c.textOnly) box=gPaintChooseText(card, c, instruction);'));
ok('G3 the data feedback path is chosen before any string is placed',
   hasCode(stripComments(extractFunction(INDEX, 'gChooseFeedback')),
           'if(c.textOnly){ gPaintChooseFeedbackText(fb,c); return; }'));

// =========================================================================
// H. Accessibility, reusing the shipping helpers rather than a second set.
// =========================================================================
startWith([itemNamed('choose-04')]);
eq('H1 reading order is instruction, prompt, meaning, options, feedback',
   gDrillCard.children.map(function (n) { return n.id || n.className; }),
   ['gInstruction', 'gQuestion', 'gQuestionMeaning', 'opts', 'gFbBox']);
eq('H1 the prompt is a heading and is script-focusable only',
   [lookup('gQuestion').tag, lookup('gQuestion').getAttribute('tabindex')], ['h2', '-1']);
eq('H1 every option is keyboard-operable as a native button, with no key handler',
   [opts().every(function (b) { return b.tag === 'button'; }),
    opts().every(function (b) { return !b.listeners.keydown && !b.listeners.keyup; })],
   [true, true]);
eq('H1 the selected state is carried by aria-pressed, not by class alone',
   opts().every(function (b) { return b.getAttribute('aria-pressed') !== null; }), true);
eq('H2 exactly one polite atomic status region carries the verdict', (function () {
  var tag = INDEX.slice(INDEX.lastIndexOf('<', INDEX.indexOf('id="gStatus"')),
                        INDEX.indexOf('>', INDEX.indexOf('id="gStatus"')) + 1);
  return [/role="status"/.test(tag), /aria-live="polite"/.test(tag),
          /aria-atomic="true"/.test(tag), /class="sr-only"/.test(tag)];
})(), [true, true, true, true]);
eq('H2 the status is written as text and never as markup',
   countOf(stripComments(extractFunction(INDEX, 'gSetStatus')), 'innerHTML'), 0);
// Three independent, non-visual carriers on the revealed path: the chosen
// option's own accessible name, the correct option's accessible name, and the
// one polite status region.  Losing any one still leaves the answer legible.
eq('H2 nothing about the revealed verdict is carried by colour alone', (function () {
  var drill = APP.G.queue[0];
  var wrong = drill.options.filter(function (o) { return o.value !== drill.answer; })[0];
  byValue(wrong.value).fire('click');
  return [accName(byValue(wrong.value)).indexOf(', incorrect') !== -1,
          accName(byValue(drill.answer)).indexOf(', correct answer') !== -1,
          statusText().indexOf('is not correct. The answer is') !== -1,
          statusText().indexOf('Explanation available below') !== -1];
})(), [true, true, true, true]);
eq('H2 the correct answer is stated in words as well as marked', (function () {
  var drill = APP.G.queue[0];
  var marked = opts().filter(function (b) { return b.classList.contains('correct'); });
  return [marked.length, marked[0].getAttribute('data-val') === drill.answer,
          statusText().indexOf(visibleText(marked[0])) !== -1];
})(), [1, true, true]);
eq('H2 the structural feedback follows the verdict in reading order', (function () {
  var ids = gDrillCard.children.map(function (n) { return n.id || n.className; });
  return [ids.indexOf('opts') < ids.indexOf('gFbBox'),
          feedbackBox().children.map(function (n) { return n.className; })];
})(), [true, ['fb-good', 'fb-explain']]);
eq('H2 the correct-answer path still states its own verdict in words', (function () {
  startWith([itemNamed('choose-04')]);
  var drill = APP.G.queue[0];
  byValue(drill.answer).fire('click');
  return [accName(byValue(drill.answer)).indexOf(', correct') !== -1,
          statusText().indexOf('Correct.') === 0];
})(), [true, true]);
eq('H3 a settled item leaves every option disabled and understandable',
   [opts().every(function (b) { return b.disabled; }),
    opts().every(function (b) { return /, (correct|incorrect)/.test(accName(b)) ||
                                       b.getAttribute('aria-pressed') !== null; })],
   [true, true]);
eq('H3 a revealed item leaves every option disabled too, and nothing focusable behind', (function () {
  startWith([itemNamed('choose-04')]);
  var drill = APP.G.queue[0];
  byValue(drill.options.filter(function (o) { return o.value !== drill.answer; })[0].value)
    .fire('click');
  return [opts().every(function (b) { return b.disabled; }),
          opts().filter(function (b) { return !b.disabled; }).length,
          fakeDocument.activeElement === lookup('gDrillNext'),
          fakeDocument.activeElement === BODY];
})(), [true, 0, true, false]);
eq('H3 focus is never left on the document body through a whole item',
   fakeDocument.activeElement === BODY, false);
eq('H4 the phase and count are updated for assistive technology each item',
   [lookup('gPhase').textContent, lookup('gCount').textContent],
   ['Practice · 1 of 1', '1 / 1']);
eq('H5 no parallel focus, status or option-state helper was created',
   ['ppFocusActivityTarget', 'ppSetActivityStatus', 'ppSetActivityOptionState']
     .filter(function (name) {
       return countOf(stripComments(extractFunction(INDEX, 'gRenderChoose')), name) === 0 &&
              countOf(stripComments(extractFunction(INDEX, 'gSetStatus')), name) === 0;
     }), []);

// =========================================================================
// I. Mobile and layout: no new selector, no new breakpoint, no new rule.
// =========================================================================
eq('I1 every class the data path uses already exists in the stylesheet',
   ['.d-type', '.q-prompt', '.q-en', '.opts', '.opt', '.fb-box', '.fb-good',
    '.fb-explain'].filter(function (sel) { return STYLE.indexOf(sel) === -1; }), []);
eq('I1 the blank keeps the one rule it already had',
   STYLE.indexOf('.q-prompt .blank{display:inline-block') !== -1, true);
eq('I2 no new media-query width was introduced', (function () {
  var widths = [], re = /@media\s*\(max-width:\s*(\d+)px\)/g, m;
  while ((m = re.exec(STYLE))) widths.push(Number(m[1]));
  return widths.sort(function (a, b) { return a - b; });
})(), [360, 400, 400]);
eq('I2 no media query at all was added', countOf(STYLE, '@media'), 5);
eq('I2 this phase added no selector of its own to the stylesheet',
   ['p7-', 'choose-practice', 'vp-choose', 'pattern-practice']
     .filter(function (token) { return STYLE.indexOf(token) !== -1; }), []);
eq('I2 nothing anywhere hides horizontal overflow',
   /overflow-x\s*:\s*(hidden|clip)/.test(STYLE), false);
eq('I2 hostile unbroken runtime text gets an emergency wrap without clipping',
   ['.opt{', '.d-type{', '.q-prompt{', '.q-en{', '.fb-good .p{',
    '.fb-good .e{', '.fb-explain{'].filter(function (sel) {
     var at = STYLE.indexOf(sel);
     if (at === -1) return false;
     var body = STYLE.slice(at, STYLE.indexOf('}', at));
     return /overflow-wrap\s*:\s*anywhere/.test(body);
   }), ['.opt{', '.q-prompt{', '.q-en{', '.fb-good .p{',
         '.fb-good .e{', '.fb-explain{']);
eq('I3 long text arrives as ordinary wrapping text, not as fixed-width nodes',
   (function () {
     startWith([itemNamed('choose-10')]);
     var longest = opts().map(function (b) { return b.textContent.length; })
       .sort(function (a, b) { return b - a; })[0];
     return [longest > 120, opts().every(function (b) {
       return !b.style.width && !b.style.minWidth && !b.getAttribute('style');
     })];
   })(), [true, true]);
eq('I3 a long prompt is one text run the browser is free to wrap',
   [lookup('gQuestion').textContent.length > 200,
    lookup('gQuestion').getAttribute('style')], [true, null]);
eq('I3 a long explanation stays inside the existing feedback region', (function () {
  byValue(APP.G.queue[0].answer).fire('click');
  return [feedbackBox().querySelector('.fb-explain').textContent.length > 250,
          feedbackBox().querySelector('.fb-explain').getAttribute('style')];
})(), [true, null]);
eq('I4 the data path never wrote markup into the drill card at any point',
   [gDrillCard.htmlWrites || 0, gDrillCard.innerHTML], [0, '']);

// =========================================================================
// J. Nothing is persisted, measured or migrated.
// =========================================================================
eq('J1 the whole round runs with no storage object in scope at all',
   [typeof globalThis.localStorage, typeof globalThis.sessionStorage],
   ['undefined', 'undefined']);
eq('J2 no Grammar function on the choose path records progress', (function () {
  return GNAMES.filter(function (name) {
    var src = stripComments(extractFunction(INDEX, name));
    return /rRecord|localStorage|sessionStorage|saveV2|loadV2|indexedDB|persistProgress/
      .test(src);
  });
})(), []);
eq('J2 the adapter writes nothing and measures nothing',
   ['localStorage', 'sessionStorage', 'indexedDB', 'cookie', 'gtag', 'analytics',
    'navigator.send', 'fetch(']
     .filter(function (token) { return ADAPTER_SRC.indexOf(token) !== -1; }), []);
// The storage key and schema version are unmoved. APP_VERSION advanced to the
// Priority 7 Phase 4F-I1 release, __CURRENT_APP_VERSION__, and is pinned at that exact value.
eq('J3 no storage key or schema version moved, and the current version is declared once',
   [countOf(INDEX, 'popolsku-progress-v2'), countOf(INDEX, 'schemaVersion'),
    countOf(INDEX, 'APP_VERSION="__CURRENT_APP_VERSION__"') + countOf(INDEX, "APP_VERSION='__CURRENT_APP_VERSION__'") +
    countOf(INDEX, 'APP_VERSION = "__CURRENT_APP_VERSION__"')],
   [countOf(INDEX, 'popolsku-progress-v2'), countOf(INDEX, 'schemaVersion'), 1]);
eq('J4 the round state is ordinary in-memory activity state',
   [typeof APP.G.queue, typeof APP.G.results, typeof APP.G.di], ['object', 'object', 'number']);
eq('J5 no pattern mastery, completion or strength concept was created',
   ['mastery', 'patternProgress', 'patternMastery', 'completedPatterns', 'strength']
     .filter(function (token) {
       return ENTRY_CODE.indexOf(token) !== -1 || ADAPTER_SRC.indexOf(token) !== -1;
     }), []);

// =========================================================================
// K. Authored Grammar content is untouched by the extension points.
// =========================================================================
// Authored-drill BEHAVIOUR is owned by tests/test_grammar_interaction.js, which
// has a markup-parsing fake DOM and 612 assertions over exactly this path; the
// proof that it is unchanged is that suite staying green.  What is asserted here
// is that the authored path still exists, byte for byte, and is still the one an
// authored drill takes.
// The reveal is an OPT-IN DRILL PROPERTY, not a Priority 7 branch.  The generic
// answer handler asks the drill, never the corpus: a synthetic drill that omits
// the flag gets the retry mechanic every authored drill gets, driven here through
// the same shipping engine.
var RETRY_DRILL = {
  type: 'choose', textOnly: true, instruction: 'Choose the pattern',
  prompt: 'Fikcjonuje ___ .', promptEn: 'SYNTHETIC-NONRELEASE: no flag.', _case: '',
  options: [{ value: 'opt-retry-right', label: 'kogo? co? · Accusative' },
            { value: 'opt-retry-wrong-a', label: 'kogo? czego? · Genitive' },
            { value: 'opt-retry-wrong-b', label: 'kim? czym? · Instrumental' }],
  answer: 'opt-retry-right', full: 'fikcjonowac + kogo? co? · Accusative', fullEn: '',
  explain: 'SYNTHETIC-NONRELEASE: the retry mechanic, unchanged.'
};
APP.G.topic = { name: 'No flag', teach: [], drills: [RETRY_DRILL] };
APP.G.queue = [RETRY_DRILL]; APP.G.di = 0; APP.G.results = []; APP.G.attempted = false;
APP.G.state = 'ask';
APP.renderDrill();
byValue('opt-retry-wrong-a').fire('click');
eq('K0 a drill without the flag keeps the retry mechanic exactly',
   [byValue('opt-retry-wrong-a').getAttribute('aria-label'),
    byValue('opt-retry-wrong-a').disabled,
    opts().filter(function (b) { return !b.disabled; }).length,
    APP.G.state, lookup('gDrillNext').disabled, feedbackBox().textContent,
    gDrillCard.querySelector('.opts').classList.contains('revealed')],
   ['kogo? czego? · Genitive, incorrect. Try again', true, 2, 'ask', true, '', false]);
eq('K0 without the flag the answer stays hidden and focus moves on to another option',
   [opts().filter(function (b) { return b.classList.contains('correct'); }).length,
    statusText().indexOf('Try another answer') !== -1,
    fakeDocument.activeElement.getAttribute('data-val')],
   [0, true, 'opt-retry-wrong-b']);
eq('K0 the generic handler asks the DRILL, never the corpus', (function () {
  var handler = stripComments(extractFunction(INDEX, 'gRenderChoose')) +
                stripComments(extractFunction(INDEX, 'gRevealChooseAnswer'));
  return ['priority7', 'PP_VERB_PATTERNS', 'patternRef', 'exerciseId', 'vp-',
          'p7-fixture'].filter(function (token) { return handler.indexOf(token) !== -1; });
})(), []);
eq('K0 the flag is read in exactly one place and defaults to the retry mechanic',
   [countOf(stripComments(extractFunction(INDEX, 'gRenderChoose')), 'revealOnIncorrect'),
    countOf(stripComments(INDEX), 'revealOnIncorrect')], [1, 1]);
eq('K0 the adapter is what opts the synthetic items in',
   [PP_VERB_PATTERNS.grammarChooseDrills(ITEMS)
      .filter(function (d) { return d.revealOnIncorrect === true; }).length,
    countOf(LOADER_SRC, 'revealOnIncorrect')], [10, 1]);
eq('K0 no authored Grammar drill opts in, and none can be given the flag by data',
   [countOf(readFile(ROOT + 'data-grammar.js'), 'revealOnIncorrect'),
    countOf(readFile(ROOT + 'data-grammar.js'), 'textOnly')], [0, 0]);
eq('K1 an authored drill keeps the authored instruction wording',
   stripComments(extractFunction(INDEX, 'gRenderChoose'))
     .indexOf('"Choose the right form"') !== -1, true);
eq('K1 an authored drill still takes the markup path',
   hasCode(stripComments(extractFunction(INDEX, 'gRenderChoose')),
           'card.innerHTML=\'<div class="d-type" id="gInstruction">\'+dt+\'</div>'), true);
eq('K1 authored feedback keeps its deliberate markup path and its audio control',
   [countOf(stripComments(extractFunction(INDEX, 'gChooseFeedback')), 'innerHTML'),
    countOf(stripComments(extractFunction(INDEX, 'gChooseFeedback')), 'mini-audio')],
   [1, 2]);
eq('K2 a data option carries no language it cannot claim',
   [PP_VERB_PATTERNS.grammarChooseDrills(ITEMS)[0].options[0].lang, undefined],
   [undefined, undefined]);
eq('K2 the option helpers answer a plain string exactly as before',
   (function () {
     var helpers = Function(
       extractFunction(INDEX, 'gOptionValue') + extractFunction(INDEX, 'gOptionLabel') +
       extractFunction(INDEX, 'gOptionLang') +
       'return [gOptionValue("moja"), gOptionLabel("moja"), gOptionLang("moja"),' +
       ' gOptionValue({value:"v",label:"l"}), gOptionLabel({value:"v",label:"l"}),' +
       ' gOptionLang({value:"v",label:"l"})];')();
     return helpers;
   })(), ['moja', 'moja', 'pl', 'v', 'l', null]);
eq('K3 the authored data files were not touched by this phase',
   [countOf(readFile(ROOT + 'data-grammar.js'), 'textOnly'),
    countOf(readFile(ROOT + 'data-grammar.js'), 'grammar-choose'),
    countOf(readFile(ROOT + 'data-grammar.js'), 'p7-fixture')], [0, 0, 0]);
eq('K3 no authored drill opts into the data path',
   countOf(readFile(ROOT + 'data-grammar.js'), 'instruction:'), 0);

// =========================================================================
// M. RETRY OUTCOMES.  The completion summary must describe what actually
// happened to the drills that came back, not what the retry mechanic used to
// guarantee would happen to them.
// =========================================================================
function runRound(items, plan) {
  // `plan` answers each presentation in turn: true = pick the answer,
  // false = pick a distractor.  Returns the completion state.
  startWith(items);
  var step = 0;
  while (gDone.style.display === 'none' && step < 24) {
    var drill = APP.G.queue[APP.G.di];
    var correctly = plan[step] !== false;
    var pick = correctly ? drill.answer
      : drill.options.filter(function (o) { return o.value !== drill.answer; })[0].value;
    byValue(pick).fire('click');
    step++;
    APP.advance();
  }
  return {
    steps: step,
    queue: APP.G.queue.length,
    requeued: APP.G.queue.filter(function (d) { return d._requeue; }).length,
    score: lookup('gScore').textContent,
    total: lookup('gTotal').textContent,
    message: lookup('gDoneMsg').textContent,
    results: APP.G.results.slice(),
    cleared: APP.G.cleared.slice()
  };
}
var ONE = [itemNamed('choose-01')];
var TWO = [itemNamed('choose-01'), itemNamed('choose-02')];
var FOUR = [itemNamed('choose-01'), itemNamed('choose-02'),
            itemNamed('choose-03'), itemNamed('choose-04')];

eq('M1 correct first try: no retry, no retry sentence', (function () {
  var run = runRound(ONE, [true]);
  return [run.steps, run.queue, run.requeued, run.score, run.total, run.message];
})(), [1, 1, 0, '1', '1',
       'Every answer right on the first try. This is clicking.']);

eq('M2 wrong then correct on the retry: still truthfully cleared', (function () {
  var run = runRound(ONE, [false, true]);
  return [run.steps, run.queue, run.requeued, run.score, run.total, run.message,
          run.cleared];
})(), [2, 2, 1, '0', '1',
       'Nice work through the set - 1 drill came back for a second pass and you cleared it.',
       [false, true]]);

// The finding.  The old sentence claimed this one was cleared; it was not.
eq('M3 wrong then wrong on the retry: never claims it was cleared', (function () {
  var run = runRound(ONE, [false, false]);
  return [run.steps, run.queue, run.requeued, run.score, run.total, run.message,
          run.cleared];
})(), [2, 2, 1, '0', '1',
       'Nice work through the set - 1 drill came back for a second pass and still needs practice.',
       [false, false]]);
eq('M3 the uncleared retry created no third attempt',
   (function () { return runRound(ONE, [false, false, true]).steps; })(), 2);
eq('M3 the word "cleared" never appears when nothing was cleared',
   runRound(ONE, [false, false]).message.indexOf('cleared'), -1);

eq('M4 several misses, every retry cleared', (function () {
  // two originals missed, both retries answered
  var run = runRound(TWO, [false, false, true, true]);
  return [run.queue, run.requeued, run.score, run.total, run.message];
})(), [4, 2, '0', '2',
       'Nice work through the set - 2 drills came back for a second pass and you cleared them.']);

eq('M4 several misses, no retry cleared', (function () {
  var run = runRound(TWO, [false, false, false, false]);
  return [run.queue, run.requeued, run.score, run.total, run.message];
})(), [4, 2, '0', '2',
       'Nice work through the set - 2 drills came back for a second pass and still need practice.']);

eq('M4 several misses, some cleared and some not', (function () {
  var run = runRound(TWO, [false, false, true, false]);
  return [run.queue, run.requeued, run.score, run.total, run.message];
})(), [4, 2, '0', '2',
       'Nice work through the set - 2 drills came back for a second pass and you cleared 1 of them.']);

eq('M5 scoring, denominator and requeue policy are untouched by the wording', (function () {
  var run = runRound(FOUR, [true, false, true, false, false, true]);
  //            originals: 1 right, 2 wrong, 3 right, 4 wrong -> 2 retries
  return [run.total, run.score, run.queue, run.requeued,
          run.results.filter(function (r) { return r === true; }).length];
})(), ['4', '2', 6, 2, 3]);
eq('M5 a retry is never itself requeued, however it ends',
   [runRound(ONE, [false, false]).queue, runRound(ONE, [false, true]).queue,
    runRound(TWO, [false, false, false, false]).queue], [2, 2, 4]);
eq('M5 the retry summary is derived, not stored',
   [countOf(stripComments(extractFunction(INDEX, 'gRetryOutcome')), 'localStorage'),
    countOf(stripComments(extractFunction(INDEX, 'gRetryOutcome')), '_requeue'),
    countOf(stripComments(extractFunction(INDEX, 'gDoneMessage')), 'G.results')],
   [0, 1, 0]);
eq('M5 an unrecorded outcome still reads as cleared, exactly as it always did',
   (function () {
     startWith(ONE);
     APP.G.queue.push({ _requeue: true });
     APP.G.di = 1;
     APP.G.results = [false, false];
     APP.G.cleared = [false];              // nothing recorded for the retry
     APP.showDone();
     return lookup('gDoneMsg').textContent;
   })(),
   'Nice work through the set - 1 drill came back for a second pass and you cleared it.');
eq('M6 no mastery or persistence language entered the completion copy',
   ['master', 'saved', 'unlock', 'progress', 'approved', 'streak', 'level up']
     .filter(function (word) {
       return [runRound(ONE, [true]).message, runRound(ONE, [false, true]).message,
               runRound(ONE, [false, false]).message,
               runRound(TWO, [false, false, true, false]).message]
         .join(' ').toLowerCase().indexOf(word) !== -1;
     }), []);

// =========================================================================
// N. VALIDATION THAT CANNOT BE TALKED OUT OF ITS OWN INVARIANT.
// =========================================================================
function withItem(mutate) {
  var item = itemNamed('choose-01');
  mutate(item);
  return item;
}
// Special property names.  An ordinary {} uniqueness map is defeated by
// "__proto__": assigning it invokes the inherited setter instead of creating an
// own property, so both copies report "not seen yet".
// The duplicate must be the ONLY thing wrong with the record.  An earlier
// version of this test made "__proto__" the answer as well, so the old broken
// implementation still rejected the item - for having two correct options - and
// the uniqueness regression could have come back with the test still green.
// Here the answer is a distinct, valid, singly-used value, and the two
// DISTRACTORS collide; nothing else about the record is invalid.
function duplicateDistractors(name) {
  return withItem(function (i) {
    i.options = [
      { value: 'answer-ok', label: i.options[0].label },
      { value: name, label: i.options[1].label },
      { value: name, label: i.options[2].label }
    ];
    i.answerValue = 'answer-ok';
  });
}
eq('N1 the isolated duplicate record is invalid for exactly one reason', (function () {
  var item = duplicateDistractors('__proto__');
  var values = item.options.map(function (o) { return o.value; });
  return [values.length, values.filter(function (v) { return v === item.answerValue; }).length,
          values.filter(function (v) { return v === '__proto__'; }).length,
          item.options.every(function (o) { return !!o.value && !!o.label; })];
})(), [3, 1, 2, true]);
eq('N1 two DISTRACTORS may not share the identity "__proto__"',
   PP_VERB_PATTERNS.grammarChooseDrill(duplicateDistractors('__proto__')), null);
eq('N1 and the whole set fails closed on it',
   PP_VERB_PATTERNS.grammarChooseDrills(
     [duplicateDistractors('__proto__'), itemNamed('choose-02')]), null);
eq('N1 the same holds for every other special name, and for ordinary ones',
   ['constructor', 'toString', 'hasOwnProperty', 'valueOf', 'prototype',
    '__defineGetter__', 'opt-ordinary', '0']
     .filter(function (name) {
       return PP_VERB_PATTERNS.grammarChooseDrill(duplicateDistractors(name)) !== null;
     }), []);
eq('N1 the identical record with the collision removed IS accepted', (function () {
  var item = duplicateDistractors('__proto__');
  item.options[2].value = '__proto__-second';
  var drill = PP_VERB_PATTERNS.grammarChooseDrill(item);
  return [!!drill, drill && drill.answer,
          drill && drill.options.map(function (o) { return o.value; })];
})(), [true, 'answer-ok', ['answer-ok', '__proto__', '__proto__-second']]);
eq('N1 two exercises may not share the identity "__proto__"', (function () {
  var a = withItem(function (i) { i.exerciseId = '__proto__'; });
  var b = itemNamed('choose-02');
  b.exerciseId = '__proto__';
  return PP_VERB_PATTERNS.grammarChooseDrills([a, b]);
})(), null);
eq('N1 two exercises may not share an order, whatever it is', (function () {
  var a = itemNamed('choose-01'), b = itemNamed('choose-02');
  b.order = a.order;
  return PP_VERB_PATTERNS.grammarChooseDrills([a, b]);
})(), null);
eq('N1 a special name is still perfectly usable as a UNIQUE identity',
   (function () {
     var drill = PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
       i.exerciseId = '__proto__';
       i.options[0].value = 'constructor';
       i.answerValue = 'constructor';
     }));
     return [!!drill, drill && drill.exerciseId, drill && drill.answer];
   })(), [true, '__proto__', 'constructor']);
eq('N1 the uniqueness sets carry no prototype at all',
   [countOf(ADAPTER_SRC, 'emptyDict()'), countOf(ADAPTER_SRC, 'seenBefore('),
    countOf(LOADER_SRC, 'return Object.create(null);'),
    countOf(ADAPTER_SRC, '= {}')], [3, 3, 1, 0]);

// Whitespace-only required text.  A run of spaces renders as nothing and reads
// as nothing; the record is rejected rather than trimmed into something else.
var BLANKS = ['', ' ', '   ', '\t', '\n', ' \t\n '];
[['exerciseId', function (i, v) { i.exerciseId = v; }],
 ['patternRef', function (i, v) { i.patternRef = v; }],
 ['prompt', function (i, v) { i.prompt = v; }],
 ['answerValue', function (i, v) { i.answerValue = v; }],
 ['feedbackStructure', function (i, v) { i.feedbackStructure = v; }],
 ['feedbackExplanation', function (i, v) { i.feedbackExplanation = v; }],
 ['promptEn (optional, but present)', function (i, v) { i.promptEn = v; }],
 ['cue (optional, but present)', function (i, v) { i.cue = v; }],
 ['an option value', function (i, v) { i.options[1].value = v; }],
 ['an option label', function (i, v) { i.options[1].label = v; }]
].forEach(function (field) {
  eq('N2 a blank-looking ' + field[0] + ' fails closed',
     BLANKS.filter(function (blank) {
       return PP_VERB_PATTERNS.grammarChooseDrill(
         withItem(function (i) { field[1](i, blank); })) !== null;
     }), []);
  eq('N2 a blank-looking ' + field[0] + ' fails the whole set closed',
     PP_VERB_PATTERNS.grammarChooseDrills(
       [withItem(function (i) { field[1](i, '   '); }), itemNamed('choose-02')]), null);
});
eq('N2 a blank fragment, and fragments that add up to nothing, both fail closed',
   [PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
      i.prompt = [{ text: '', lang: 'pl' }];
    })),
    PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
      i.prompt = [{ text: '  ', lang: 'pl' }, { text: ' ' }];
    })),
    PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) { i.prompt = []; })),
    PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
      i.options[0].label = [{ text: 'ok', lang: '  ' }];
    }))],
   [null, null, null, null]);
eq('N2 an unusual but non-blank string is still accepted',
   ['0', '·', '—', '\u00a0x', 'ß', '   x   ', '<b>'].filter(function (value) {
     return PP_VERB_PATTERNS.grammarChooseDrill(
       withItem(function (i) { i.feedbackExplanation = value; })) === null;
   }), []);
eq('N2 nothing was trimmed on the way through', (function () {
  var drill = PP_VERB_PATTERNS.grammarChooseDrill(
    withItem(function (i) { i.feedbackExplanation = '   padded   '; }));
  return drill.explain;
})(), '   padded   ');
eq('N2 validation mutates no record it was handed', (function () {
  var before = JSON.stringify(ITEMS);
  PP_VERB_PATTERNS.grammarChooseDrills(ITEMS);
  PP_VERB_PATTERNS.grammarChooseDrill(ITEMS[0]);
  return JSON.stringify(ITEMS) === before;
})(), true);
eq('N2 the emitted fragments are copies rather than the record own arrays', (function () {
  var drill = PP_VERB_PATTERNS.grammarChooseDrill(ITEMS[0]);
  return [drill.prompt === ITEMS[0].prompt,
          drill.options[0].label === ITEMS[0].options[0].label,
          JSON.stringify(drill.prompt) === JSON.stringify(ITEMS[0].prompt)];
})(), [false, false, true]);

// The plain-object contract, reviewed rather than tightened: every required key
// must be an OWN property, so an inherited one fails closed and a prototype
// cannot smuggle a field in.
eq('N3 an inherited required key does not satisfy the record contract', (function () {
  var base = itemNamed('choose-01');
  var derived = Object.create(base);        // every key inherited, none own
  return [PP_VERB_PATTERNS.grammarChooseDrill(derived),
          PP_VERB_PATTERNS.grammarChooseDrills([derived])];
})(), [null, null]);
eq('N3 an inherited PRIVATE key cannot be smuggled past the check either',
   (function () {
     var item = itemNamed('choose-01');
     var carrier = Object.create({ reviewState: 'research' });
     Object.keys(item).forEach(function (key) { carrier[key] = item[key]; });
     // Own keys are exactly the contract; the inherited private key is not read.
     var drill = PP_VERB_PATTERNS.grammarChooseDrill(carrier);
     return [!!drill, drill && drill.exerciseId === item.exerciseId,
             JSON.stringify(drill) === JSON.stringify(
               PP_VERB_PATTERNS.grammarChooseDrill(item))];
   })(), [true, true, true]);
eq('N3 an OWN private key still refuses the record whole',
   PP_VERB_PATTERNS.grammarChooseDrill(
     withItem(function (i) { i.reviewState = 'research'; })), null);

// N4.  A RECOGNISED OPTIONAL FIELD IS ONLY EVER AN OWN PROPERTY.
// `in` answers for the prototype chain, so an inherited promptEn/cue/lang would
// be treated as supplied - and reading it would then run somebody else's getter
// during validation.  Every counter below must stay at zero: the getters are not
// merely ignored, they are never touched.
function withInheritedOptionals() {
  var touched = { promptEn: 0, cue: 0 };
  // The record must NOT own these, so the prototype is their only source.
  var own = itemNamed('choose-01');
  delete own.promptEn;
  delete own.cue;
  var proto = {};
  Object.defineProperty(proto, 'promptEn', {
    get: function () { touched.promptEn++; return '   '; }, enumerable: false
  });
  Object.defineProperty(proto, 'cue', {
    get: function () { touched.cue++; return { not: 'a text value' }; }, enumerable: false
  });
  var item = Object.create(proto);
  Object.keys(own).forEach(function (key) {
    Object.defineProperty(item, key, {
      value: own[key], enumerable: true, writable: true, configurable: true
    });
  });
  return { item: item, touched: touched, own: own };
}
eq('N4 the probe really does inherit, and own, exactly what it claims to',
   (function () {
     var probe = withInheritedOptionals();
     return [Object.prototype.hasOwnProperty.call(probe.item, 'promptEn'),
             Object.prototype.hasOwnProperty.call(probe.item, 'cue'),
             'promptEn' in probe.item, 'cue' in probe.item,
             Object.prototype.hasOwnProperty.call(probe.item, 'exerciseId'),
             probe.touched.promptEn + probe.touched.cue];
   })(), [false, false, true, true, true, 0]);
eq('N4 an inherited optional field is neither consumed nor even looked at',
   (function () {
     var probe = withInheritedOptionals();
     var drill = PP_VERB_PATTERNS.grammarChooseDrill(probe.item);
     return [!!drill, probe.touched.promptEn, probe.touched.cue,
             drill && drill.promptEn, drill && drill._case];
   })(), [true, 0, 0, '', '']);
eq('N4 the drill built from it is identical to the one built from own data alone',
   (function () {
     var probe = withInheritedOptionals();
     return JSON.stringify(PP_VERB_PATTERNS.grammarChooseDrill(probe.item)) ===
            JSON.stringify(PP_VERB_PATTERNS.grammarChooseDrill(probe.own));
   })(), true);
eq('N4 a whole set built from such records is unaffected too',
   (function () {
     var probe = withInheritedOptionals();
     var drills = PP_VERB_PATTERNS.grammarChooseDrills([probe.item]);
     return [!!drills, drills && drills.length, probe.touched.promptEn, probe.touched.cue];
   })(), [true, 1, 0, 0]);
// A getter that THROWS makes any read fatal rather than merely countable.
eq('N4 a hostile inherited getter is never executed', (function () {
  var own = itemNamed('choose-01');
  delete own.promptEn;
  delete own.cue;
  var proto = {};
  ['promptEn', 'cue'].forEach(function (key) {
    Object.defineProperty(proto, key, {
      get: function () { throw new Error('validation read an inherited ' + key); }
    });
  });
  var item = Object.create(proto);
  Object.keys(own).forEach(function (key) {
    Object.defineProperty(item, key, {
      value: own[key], enumerable: true, writable: true, configurable: true
    });
  });
  return [!throws(function () { PP_VERB_PATTERNS.grammarChooseDrill(item); }),
          !!PP_VERB_PATTERNS.grammarChooseDrill(item)];
})(), [true, true]);
// The same rule one level down, on a fragment's optional language.
eq('N4 an inherited fragment language is neither consumed nor executed', (function () {
  var reads = 0;
  var proto = {};
  Object.defineProperty(proto, 'lang', {
    get: function () { reads++; return 'pl'; }, enumerable: false
  });
  var fragment = Object.create(proto);
  fragment.text = 'kogo? co?';
  var drill = PP_VERB_PATTERNS.grammarChooseDrill(
    withItem(function (i) { i.prompt = [fragment, { text: ' ___ .' }]; }));
  return [!!drill, reads, drill && JSON.stringify(drill.prompt)];
})(), [true, 0, '[{"text":"kogo? co?"},{"text":" ___ ."}]']);
eq('N4 an inherited fragment language that would be INVALID is ignored, not rejected',
   (function () {
     var proto = {};
     Object.defineProperty(proto, 'lang', { get: function () { return '   '; } });
     var fragment = Object.create(proto);
     fragment.text = 'still fine';
     return !!PP_VERB_PATTERNS.grammarChooseDrill(
       withItem(function (i) { i.prompt = [fragment]; }));
   })(), true);
// Positive control: the very same fields, defined as OWN properties, still work.
eq('N4 own optional fields are still read, validated and emitted', (function () {
  var drill = PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
    i.promptEn = 'SYNTHETIC-NONRELEASE: an own gloss.';
    i.cue = 'An own cue';
    i.prompt = [{ text: 'kogo? co?', lang: 'pl' }, { text: ' ___ .' }];
  }));
  return [drill.promptEn, drill._case, JSON.stringify(drill.prompt)];
})(), ['SYNTHETIC-NONRELEASE: an own gloss.', 'An own cue',
       '[{"text":"kogo? co?","lang":"pl"},{"text":" ___ ."}]']);
eq('N4 an own optional field that is invalid still fails the record closed',
   [PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) { i.promptEn = '  '; })),
    PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) { i.cue = 7; })),
    PP_VERB_PATTERNS.grammarChooseDrill(withItem(function (i) {
      i.prompt = [{ text: 'x', lang: '  ' }];
    }))],
   [null, null, null]);
// And the required half of the same contract, restated where it belongs.
eq('N4 a REQUIRED field that exists only on a prototype does not satisfy anything',
   ['exerciseId', 'prompt', 'answerValue', 'options', 'feedbackStructure']
     .filter(function (key) {
       var own = itemNamed('choose-01');
       var proto = {};
       proto[key] = own[key];
       var item = Object.create(proto);
       Object.keys(own).forEach(function (other) {
         if (other !== key) item[other] = own[other];
       });
       return PP_VERB_PATTERNS.grammarChooseDrill(item) !== null;
     }), []);
eq('N4 the parser reaches for no recognised field through the prototype chain',
   [countOf(ADAPTER_SRC, '" in item'), countOf(ADAPTER_SRC, '" in fragment'),
    countOf(ADAPTER_SRC, '" in option'), countOf(ADAPTER_SRC, 'hasOwn(item, "promptEn")'),
    countOf(ADAPTER_SRC, 'hasOwn(item, "cue")')], [0, 0, 0, 2, 2]);
eq('N4 the fragment copier reads a language only when it owns one',
   countOf(LOADER_SRC, 'if (hasOwn(fragment, "lang") && isFilledString(fragment.lang))'), 1);

// =========================================================================
// O. LANGUAGE OF PARTS.  The document is English; a structural label is not.
// =========================================================================
startWith([itemNamed('choose-01')]);
function langMap(el) {
  return el.children.map(function (n) {
    return n.tag === '#text' ? [null, n.textContent]
      : [n.getAttribute('lang'), n.textContent];
  });
}
eq('O1 a Polish-only prompt is marked Polish, once, around all of it',
   langMap(lookup('gQuestion')).filter(function (part) { return part[1] !== ''; }),
   [['pl', 'Fikcjonuje '], ['pl', ' .']]);
eq('O1 the prompt element itself claims no language',
   lookup('gQuestion').getAttribute('lang'), null);
eq('O2 a mixed option label is split into a Polish part and an English part',
   langMap(byValue('opt-01-accusative')),
   [['pl', 'kogo? co?'], [null, ' · Accusative']]);
eq('O2 the option button itself claims no language, so nothing over-claims',
   opts().map(function (b) { return b.getAttribute('lang'); }), [null, null, null]);
eq('O2 every option is segmented the same way',
   opts().map(function (b) { return langMap(b).map(function (p) { return p[0]; }); }),
   [['pl', null], ['pl', null], ['pl', null]]);
eq('O3 the English gloss under the prompt is not marked Polish',
   [lookup('gQuestionMeaning').getAttribute('lang'),
    lookup('gQuestionMeaning').children.filter(function (n) {
      return n.getAttribute && n.getAttribute('lang');
    }).length], [null, 0]);
byValue('opt-01-genitive').fire('click');
eq('O4 the revealed answer keeps the same segmentation, plus a hidden verdict',
   langMap(byValue('opt-01-accusative')),
   [['pl', 'kogo? co?'], [null, ' · Accusative'], [null, ', correct answer']]);
eq('O4 and the verdict is the only thing added, in the document language',
   [byValue('opt-01-accusative').querySelectorAll('.sr-only').length,
    byValue('opt-01-accusative').querySelector('.sr-only').getAttribute('lang'),
    visibleText(byValue('opt-01-accusative'))],
   [1, null, 'kogo? co? · Accusative']);
eq('O5 the status announcement is segmented exactly like the buttons', (function () {
  var spans = gStatus.children.filter(function (n) { return n.tag === 'span'; });
  return spans.map(function (span) {
    return [span.getAttribute('lang'), langMap(span)];
  });
})(), [
  [null, [['pl', 'kogo? czego?'], [null, ' · Genitive']]],
  [null, [['pl', 'kogo? co?'], [null, ' · Accusative']]]
]);
eq('O5 the status still reads as one sentence',
   [statusText().indexOf('kogo? czego? · Genitive is not correct.') === 0,
    statusText().indexOf('The answer is kogo? co? · Accusative') !== -1], [true, true]);
eq('O6 the structural feedback is segmented, and the explanation is not',
   [langMap(feedbackBox().querySelector('.fb-good').querySelector('.p'))
      .map(function (p) { return p[0]; }),
    feedbackBox().querySelector('.fb-explain').children
      .filter(function (n) { return n.getAttribute && n.getAttribute('lang'); }).length,
    feedbackBox().querySelector('.fb-explain').getAttribute('lang')],
   [['pl', null, 'pl', null], 0, null]);
eq('O6 English explanatory text is never marked Polish because its subject is',
   flat(itemNamed('choose-01').feedbackExplanation).indexOf('SYNTHETIC-NONRELEASE') === 0 &&
   feedbackBox().querySelector('.fb-explain').textContent.indexOf('SYNTHETIC-NONRELEASE') === 0 &&
   langsOf(itemNamed('choose-01').feedbackExplanation).join(',') === '', true);
// The correct-first path segments identically - one model, not two.
eq('O7 the correct path announces with the same segmentation', (function () {
  startWith([itemNamed('choose-01')]);
  byValue('opt-01-accusative').fire('click');
  var span = gStatus.children.filter(function (n) { return n.tag === 'span'; })[0];
  return [span.getAttribute('lang'), langMap(span)];
})(), [null, [['pl', 'kogo? co?'], [null, ' · Accusative']]]);
eq('O7 the visible button and the announcement carry identical text',
   visibleText(byValue('opt-01-accusative')),
   gStatus.children.filter(function (n) { return n.tag === 'span'; })[0].textContent);
// A plain-string option keeps the single lang="pl" element it has always had.
eq('O8 an authored string option is still announced as one Polish element', (function () {
  APP.G.topic = { name: 'Authored', teach: [{ front: 'x' }], drills: [] };
  APP.G.queue = [{ type: 'choose', prompt: 'To jest ___ kawa.', promptEn: 'x',
                   options: ['moja', 'mój'], answer: 'moja', full: 'f', fullEn: '',
                   explain: 'e', textOnly: true }];
  APP.G.di = 0; APP.G.results = []; APP.G.cleared = []; APP.G.attempted = false;
  APP.G.state = 'ask';
  APP.renderDrill();
  byValue('moja').fire('click');
  var span = gStatus.children.filter(function (n) { return n.tag === 'span'; })[0];
  return [span.getAttribute('lang'), span.textContent,
          byValue('moja').getAttribute('lang')];
})(), ['pl', 'moja', 'pl']);
eq('O9 language handling introduced no markup path',
   ['gTextFragments', 'gFragmentText', 'gAppendFragment', 'gAppendTextParts',
    'gChooseOptionLabel', 'gAnnounceRevealed', 'gAnnounceCorrect', 'gAnnounceWrong']
     .filter(function (name) {
       var src = stripComments(extractFunction(INDEX, name));
       return ['innerHTML', 'outerHTML', 'insertAdjacentHTML', 'document.write',
               'eval('].some(function (t) { return src.indexOf(t) !== -1; });
     }), []);
eq('O9 the language helpers are generic and know nothing about Priority 7',
   ['priority7', 'PP_VERB_PATTERNS', 'patternRef', 'exerciseId', 'p7-fixture', 'vp-']
     .filter(function (token) {
       return ['gTextFragments', 'gFragmentText', 'gAppendFragment', 'gAppendTextParts',
               'gAppendDrillText', 'gChooseOptionLabel', 'gPaintChooseText',
               'gPaintChooseFeedbackText', 'gRevealChooseAnswer']
         .some(function (name) {
           return stripComments(extractFunction(INDEX, name)).indexOf(token) !== -1;
         });
     }), []);
eq('O9 one function turns fragments into DOM, so the copies cannot drift',
   [countOf(stripComments(INDEX), 'function gAppendFragment('),
    countOf(stripComments(INDEX), 'gAppendTextParts(') > 4], [1, true]);
eq('O10 hostile text inside a language fragment is still only text', (function () {
  startWith([itemNamed('choose-09')]);
  var span = lookup('gQuestion').children
    .filter(function (n) { return n.tag === 'span' && n.getAttribute('lang') === 'pl'; })[0];
  return [span.children.length, span.textContent.indexOf('<img src=x') === 0,
          gDrillCard.querySelectorAll('img').length,
          gDrillCard.querySelectorAll('script').length,
          typeof globalThis.__p7Pwned];
})(), [0, true, 0, 0, 'undefined']);

// =========================================================================
// P. THE SETTLED STATE KEEPS ITS LANGUAGE OF PARTS.
//
// A mixed option's accessible name is computed from its language-tagged child
// nodes.  An aria-label REPLACES that computed name with one flat string, which
// throws the segmentation away - and the button cannot carry one correct `lang`
// either, because its content is not one language.  So a structured option gets
// its verdict appended as visually hidden text inside itself, and keeps its
// computed name; a plain authored string option keeps the aria-label it always
// had, because flattening one language loses nothing.
//
// HARNESS LIMITATION, stated rather than glossed over: this suite computes no
// browser accessibility tree.  What is asserted below is the DOM contract that
// PRODUCES the accessible name and description - which nodes exist, which carry
// a language, and whether anything overrides them.  Real name resolution, real
// screen-reader output and real voice switching remain human checks, exactly as
// this repository's other suites state.
// =========================================================================
var MIXED = itemNamed('choose-01');
function optionShape(btn) {
  return {
    ariaLabel: btn.getAttribute('aria-label'),
    pressed: btn.getAttribute('aria-pressed'),
    disabled: btn.disabled,
    classes: btn.className,
    visible: visibleText(btn),
    name: accName(btn),
    parts: btn.children.map(function (n) {
      return [n.tag === '#text' ? null : n.getAttribute('lang'),
              n.classList && n.classList.contains('sr-only') ? 'hidden' : 'visible',
              n.textContent];
    })
  };
}
// Before settlement.
startWith([MIXED]);
eq('P1 an unsettled mixed option is already segmented, and claims nothing extra',
   optionShape(byValue('opt-01-accusative')),
   { ariaLabel: null, pressed: 'false', disabled: false, classes: 'opt',
     visible: 'kogo? co? · Accusative', name: 'kogo? co? · Accusative',
     parts: [['pl', 'visible', 'kogo? co?'], [null, 'visible', ' · Accusative']] });
eq('P1 the English case name is not inside the Polish node',
   byValue('opt-01-accusative').children
     .filter(function (n) { return n.getAttribute && n.getAttribute('lang') === 'pl'; })
     .map(function (n) { return n.textContent; }), ['kogo? co?']);

// After an incorrect answer: the chosen option, and the revealed answer.
byValue('opt-01-genitive').fire('click');
eq('P2 the chosen wrong option keeps its language-aware children',
   optionShape(byValue('opt-01-genitive')),
   { ariaLabel: null, pressed: 'true', disabled: true, classes: 'opt wrong',
     visible: 'kogo? czego? · Genitive', name: 'kogo? czego? · Genitive, incorrect',
     parts: [['pl', 'visible', 'kogo? czego?'], [null, 'visible', ' · Genitive'],
             [null, 'hidden', ', incorrect']] });
eq('P2 the revealed correct option keeps its language-aware children too',
   optionShape(byValue('opt-01-accusative')),
   { ariaLabel: null, pressed: 'false', disabled: true, classes: 'opt correct',
     visible: 'kogo? co? · Accusative',
     name: 'kogo? co? · Accusative, correct answer',
     parts: [['pl', 'visible', 'kogo? co?'], [null, 'visible', ' · Accusative'],
             [null, 'hidden', ', correct answer']] });
eq('P2 no settled mixed option carries a flattening aria-label',
   opts().filter(function (b) { return b.getAttribute('aria-label') !== null; }).length, 0);
eq('P2 the verdict is not falsely marked Polish',
   opts().map(function (b) {
     var hidden = b.querySelector('.sr-only');
     return hidden ? hidden.getAttribute('lang') : 'none';
   }), [null, null, 'none']);
eq('P2 the verdict lives inside the option, so it is part of its own name',
   opts().map(function (b) {
     var hidden = b.querySelector('.sr-only');
     return hidden ? hidden.parentElement === b : 'none';
   }), [true, true, 'none']);
eq('P2 the revealed answer is distinguishable from the learner\'s own choice',
   [byValue('opt-01-accusative').getAttribute('aria-pressed'),
    byValue('opt-01-genitive').getAttribute('aria-pressed'),
    accName(byValue('opt-01-accusative')).indexOf('correct answer') !== -1,
    accName(byValue('opt-01-genitive')).indexOf('incorrect') !== -1],
   ['false', 'true', true, true]);
eq('P2 the untouched option says nothing it has not earned',
   optionShape(byValue('opt-01-instrumental')),
   { ariaLabel: null, pressed: 'false', disabled: true, classes: 'opt',
     visible: 'kim? czym? · Instrumental', name: 'kim? czym? · Instrumental',
     parts: [['pl', 'visible', 'kim? czym?'], [null, 'visible', ' · Instrumental']] });
eq('P2 the live status keeps the same segmentation as the buttons',
   gStatus.children.filter(function (n) { return n.tag === 'span'; })
     .map(function (span) {
       return [span.getAttribute('lang'),
               span.children.map(function (n) {
                 return [n.tag === '#text' ? null : n.getAttribute('lang'), n.textContent];
               })];
     }),
   [[null, [['pl', 'kogo? czego?'], [null, ' · Genitive']]],
    [null, [['pl', 'kogo? co?'], [null, ' · Accusative']]]]);

// Correct on the first try: the same preservation.
startWith([MIXED]);
byValue('opt-01-accusative').fire('click');
eq('P3 a first-try correct option keeps its segmentation and adds only a verdict',
   optionShape(byValue('opt-01-accusative')),
   { ariaLabel: null, pressed: 'true', disabled: true, classes: 'opt correct',
     visible: 'kogo? co? · Accusative', name: 'kogo? co? · Accusative, correct',
     parts: [['pl', 'visible', 'kogo? co?'], [null, 'visible', ' · Accusative'],
             [null, 'hidden', ', correct']] });
eq('P3 nothing anywhere in the settled card was flattened',
   opts().filter(function (b) { return b.getAttribute('aria-label') !== null; }).length, 0);
eq('P3 the announcement still matches the button word for word',
   [visibleText(byValue('opt-01-accusative')),
    gStatus.children.filter(function (n) { return n.tag === 'span'; })[0].textContent],
   ['kogo? co? · Accusative', 'kogo? co? · Accusative']);

// A plain STRING option is one language, so flattening it loses nothing - and
// that is exactly what every authored Grammar drill still gets.
eq('P4 a string option keeps the aria-label it has always had', (function () {
  APP.G.topic = { name: 'Authored-shaped', teach: [{ front: 'x' }], drills: [] };
  APP.G.queue = [{ type: 'choose', prompt: 'To jest ___ kawa.', promptEn: 'x',
                   options: ['moja', 'mój'], answer: 'moja', full: 'f', fullEn: '',
                   explain: 'e', textOnly: true }];
  APP.G.di = 0; APP.G.results = []; APP.G.cleared = []; APP.G.attempted = false;
  APP.G.state = 'ask';
  APP.renderDrill();
  byValue('mój').fire('click');
  byValue('moja').fire('click');
  return [byValue('mój').getAttribute('aria-label'),
          byValue('moja').getAttribute('aria-label'),
          byValue('moja').querySelectorAll('.sr-only').length,
          byValue('moja').getAttribute('lang')];
})(), ['mój, incorrect. Try again', 'moja, correct', 0, 'pl']);
eq('P4 the engine chooses by the option SHAPE, never by who supplied it',
   ['priority7', 'PP_VERB_PATTERNS', 'patternRef', 'exerciseId', 'p7-fixture']
     .filter(function (token) {
       return stripComments(extractFunction(INDEX, 'gSetOptionVerdict')).indexOf(token) !== -1;
     }), []);
ok('P4 and it branches on Array.isArray alone',
   hasCode(stripComments(extractFunction(INDEX, 'gSetOptionVerdict')),
           'if(!Array.isArray(label)){ btn.setAttribute("aria-label", btn.textContent+verdict); return btn; }'));
eq('P4 the hidden verdict uses the app\'s existing visually-hidden class',
   [countOf(stripComments(extractFunction(INDEX, 'gSetOptionVerdict')), '"sr-only"'),
    STYLE.indexOf('.sr-only{position:absolute') !== -1], [1, true]);

// =========================================================================
// L. What this phase does not claim.
// =========================================================================
eq('L1 the shell makes no claim about approval, review or release',
   ['releaseAuthorized', 'reviewState', 'approved for release', 'release-ready']
     .filter(function (token) { return INDEX.indexOf(token) !== -1; }), []);
eq('L1 the adapter has no vocabulary for release authorisation',
   /releas|authoriz|verified|frozen|approv/i.test(
     Object.keys(PP_VERB_PATTERNS).join(' ')), false);
eq('L1 the fixture says in its own bytes what it is and is not',
   [WRAPPED_EXERCISES.fixtureNotice.indexOf('SYNTHETIC-NONRELEASE') === 0,
    WRAPPED_EXERCISES.fixtureNotice.indexOf('may reach a learner') !== -1], [true, true]);

console.log('');
LOG.forEach(function (line) { console.log(line); });
console.log('Priority 7 Phase 3D-1 choose-mechanics tests: ' + PASS + ' passed, ' +
            FAIL + ' failed.');
console.log('  [info] the shipping adapter and the shipping Grammar choose engine are');
console.log('         driven here; no second engine and no second adapter exists');
console.log('  [info] synthetic mechanics only: no linguistic claim, no activity');
console.log('         eligibility, no review and no release authorisation is implied');
if (FAIL) throw new Error(FAIL + ' failing assertion(s)');
