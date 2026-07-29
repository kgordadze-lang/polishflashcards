// Deterministic tests for the MIXED QUIZ's option builder in index.html.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_mixed_distractors.js
// Exit status is 0 only if every assertion passes (printed at the end).
//
// WHAT THIS FILE IS FOR
// Priority 3 Phase 4D. Listening was taught in Phase 3A that two cards may not sit
// in one question when the learner cannot tell them apart from what the question
// gives them - same visible answer, same prompt, same source. The Mixed Quiz asks
// the same shape of question twice over (hear a clip and pick the meaning; read the
// Polish and pick the meaning) and answered to none of those rules: it built PLAIN
// STRINGS with `pool.filter(c => c !== card && c.en !== card.en)` and then decided
// correctness by comparing the pressed string with `q.c.en`.
//
// Three things were wrong with that, and this file owns all three:
//   the SOURCE was thrown away, so "which option is right" was a string comparison
//   two cards can win by accident;
//   the filter was EXACT, so "Answer" and "answer!" were two different options;
//   the fewer-than-four fallback concatenated the level's cards onto the topic's
//   own, so a card could be offered to itself twice.
//
// HOW IT TESTS
// Two halves, deliberately. Synthetic fixtures pin the CONTRACT - no Polish word and
// no card id from the shipping data decides anything in sections A-I, so the rules
// stay true for cards nobody has written yet. Sections J and K then sweep the REAL
// corpus through the REAL shipping functions, extracted from index.html and run in a
// fake DOM, so what is asserted is what the app does rather than a copy of it.
// Corpus figures are REPORTED, never asserted: the corpus is allowed to grow.
//
// WHAT IT DELIBERATELY DOES NOT OWN
//   - the shared builder's own rules, its normalisation and its exhaustive search:
//     tests/test_distractors.js
//   - Mixed Quiz focus, announcements and accessible names in general:
//     tests/test_mixed_accessibility.js
//   - the Mixed Quiz audio lifecycle and readiness: tests/test_mixed_audio.js
//   - scoring tiers, progress write-back and completion wording:
//     tests/test_round_scoring.js
//   - which cards may be asked at all: tests/test_typeit_eligibility.js and
//     tests/test_activities.js
//
// AND WHAT IS STILL OUT OF SCOPE AFTER THIS PHASE
// Two glosses that share a SENSE while differing as text - "What's up? / How's it
// going?" beside "What's up? (very casual)" - are not synonyms this builder can
// infer, and it deliberately does not try. Section J discovers and REPORTS today's
// examples so the boundary is visible; removing them needs authored sense identity,
// which is Phase 4E. Nothing here pretends they are fixed.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// The documented command runs from the repo root; also tolerate being run from tests/.
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
var DISTRACTOR_SRC = readFile(ROOT + 'pp-distractor.js');

// ---------- tiny test framework (same shape as the other suites) ----------
var PASS = 0, FAIL = 0, LOG = [], INFO = [];
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function info(s) { INFO.push('  [info] ' + s); }
// A block that cannot even be SET UP is a failure of the thing it tests, not a crash
// of the suite. Against a build that still hands back plain strings there is no
// record to read, no correct flag to find and no fixture to drive - and the report
// should NAME that rather than stop at the first dereference.
function section(name, fn) {
  try { fn(); }
  catch (e) { FAIL++; LOG.push('FAIL: ' + name + ' could not run - ' + ((e && e.message) || e)); }
}
function countOf(hay, needle) {
  if (!needle) return 0;
  var n = 0, i = 0;
  while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}
// Comments are prose; a rule must be visible in CODE, not only described.
function codeOnly(s) {
  return s.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:])\/\/[^\n]*/g, '$1 ');
}
// Whitespace-free view, for source checks whose claim is about TOKENS and their
// order rather than about how the line happens to be typed.
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }
// String-, comment- and regex-aware brace matcher: a Mixed Quiz function body holds
// braces inside string literals, so a naive count cuts one in half.
function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: function ' + name + ' declared more than once');
  var open = src.indexOf('{', src.indexOf(')', start));
  if (open === -1) throw new Error('extract: no body for ' + name);
  var depth = 0, mode = 'code';
  for (var j = open; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { j++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
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
  throw new Error('extract: unbalanced braces in ' + name);
}

// ---------- the shared helpers, loaded exactly as index.html loads them ----------
var window = {};
['data-a1.js', 'data-a2.js', 'data-b1.js', 'data-grammar.js', 'data-verbs.js',
 'data-scenarios.js', 'data-podcasts.js', 'pp-usage.js', 'pp-answer.js', 'pp-distractor.js']
  .forEach(function (f) { (0, eval)(readFile(ROOT + f)); });
var REAL_LEVELS = window.PP_LEVELS;
var U = window.PP_USAGE;
var D = window.PP_DISTRACTOR;
var PP_ANSWER = window.PP_ANSWER;
var ppMainAudioText = U.mainAudioText;                 // index.html binds them the same way
var ppHasMainAudio = U.hasMainAudio;
var ppEligibleFor = U.eligibleFor;                     // the REAL eligibility rule, unchanged by this phase
function nk(s) { return D.normalizeKey(s); }

// ---------- injected randomness ----------
function seededShuffle(seed) {
  var state = (seed >>> 0) || 1;
  function next() {                                    // mulberry32
    state = (state + 0x6D2B79F5) >>> 0;
    var t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }
  return function (a) {
    var out = a.slice();
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(next() * (i + 1));
      var tmp = out[i]; out[i] = out[j]; out[j] = tmp;
    }
    return out;
  };
}
var KEEP = function (a) { return a.slice(); };         // no reordering, still a copy
var REVERSE = function (a) { return a.slice().reverse(); };
var SEEDS = [1, 2, 3, 7, 11];                          // the deterministic sweep

// =========================================================================
// A FAKE DOM - only as much of one as the Mixed Quiz actually touches
// =========================================================================
// It models the two browser rules the option path depends on: focus() on a disabled
// element is a no-op, and disabling the focused element hands focus to <body>.
var BODY = null, ACTIVE = null, HTML_WRITES = {};

function FakeEl(tag) {
  this.tag = tag || 'div';
  this.className = '';
  this._disabled = false;
  this.hidden = false;
  this.value = '';
  this.style = {};
  this.children = [];
  this.classes = {};
  this._own = '';
  this._html = '';
  this._attrs = {};
  this._on = {};
  var self = this;
  this.classList = {
    add: function (c) { self.classes[c] = true; },
    remove: function (c) { delete self.classes[c]; },
    contains: function (c) { return !!self.classes[c]; }
  };
}
Object.defineProperty(FakeEl.prototype, 'disabled', {
  get: function () { return this._disabled; },
  set: function (v) {
    this._disabled = !!v;
    if (this._disabled && ACTIVE === this) ACTIVE = BODY;
  }
});
Object.defineProperty(FakeEl.prototype, 'textContent', {
  get: function () {
    if (!this.children.length) return this._own;
    return this.children.map(function (c) { return c.textContent; }).join('');
  },
  set: function (v) { this._own = String(v); this.children = []; this._html = ''; }
});
Object.defineProperty(FakeEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (v) {
    this._html = String(v);
    HTML_WRITES[this.id] = (HTML_WRITES[this.id] || 0) + 1;
    this._own = '';
    this.children = [];
  }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', { get: function () { return this.children; } });
FakeEl.prototype.appendChild = function (el) { this.children.push(el); return el; };
FakeEl.prototype.setAttribute = function (k, v) { this._attrs[k] = String(v); };
FakeEl.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null; };
FakeEl.prototype.addEventListener = function (t, fn) { (this._on[t] = this._on[t] || []).push(fn); };
FakeEl.prototype.click = function () { (this._on.click || []).forEach(function (fn) { fn({}); }); };
FakeEl.prototype.focus = function () {
  if (this._disabled) return;
  if (this.hidden) return;
  ACTIVE = this;
};
FakeEl.prototype.querySelectorAll = function (sel) {
  var want = sel.replace('.', '');
  return this.children.filter(function (c) { return (' ' + c.className + ' ').indexOf(' ' + want + ' ') !== -1; });
};
FakeEl.prototype.querySelector = function (sel) {
  var hits = this.querySelectorAll(sel);
  return hits.length ? hits[0] : null;
};
// The accessible name as a browser computes it for these buttons: aria-label wins
// outright, otherwise the button's own text.
FakeEl.prototype.accName = function () {
  var l = this.getAttribute('aria-label');
  return l === null ? this.textContent : l;
};

var DOM = {};
function el(id) {                                      // index.html's $()
  if (!DOM[id]) { DOM[id] = new FakeEl('#' + id); DOM[id].id = id; }
  return DOM[id];
}
var fakeDoc = {
  createElement: function (t) { return new FakeEl(t); },
  createTextNode: function (t) { return { nodeType: 3, textContent: String(t) }; }
};

// ---------- the rest of the environment the extracted code runs in ----------
// These are file-level vars on purpose: a `new Function` body resolves its free
// variables globally, so this is how the shipping code reaches them.
var STOPS = 0;
function stopAllAudio() { STOPS++; }
var SPOKEN = [];
function speakCardMain(card) { SPOKEN.push(card.pl); }
var audioManifestStatus = 'ready';
function syncListeningAudioReadiness() {}
function syncRoundAudioReadiness() { return MIXED.syncReadiness(); }
var shown = [];
function fakeShow(id) { shown.push(id); }

// Swappable fixtures. LEVELS is passed by reference and its CONTENTS are replaced,
// so one compiled scope serves both the synthetic topics and the real corpus.
var LEVELS = [];
var POOL_FOR = function () { return []; };
function fakePoolFor(src, act) { return POOL_FOR(src, act); }
var SHUFFLE = KEEP;
function fakeShuffle(a) { return SHUFFLE(a); }
function fakeAppendUsage() {}                          // owned by tests/test_activities.js
function ppVariantPartsStub() { return null; }         // owned by tests/test_typeit_feedback.js
function fakeProgressWritable() { return false; }      // owned by tests/test_round_scoring.js
var STORE = { progress: {} };
function fakeLoadV2() { return STORE; }
function fakeSaveV2(s) { STORE = s; }

// A SPY on the shared builder, injected into the Mixed Quiz scope only. It never
// replaces any rule - every call is delegated to the real PP_DISTRACTOR - it just
// records the spec the Mixed Quiz handed over, so "which prompt extractor did the
// mc format pass?" is answered by what ran rather than by how the call is typed.
// Scoped deliberately: nothing here counts PP_DISTRACTOR calls made anywhere else
// in index.html, which would be a claim about the app's shape, not about this path.
var BUILD_CALLS = [];
var SPY = {
  normalizeKey: D.normalizeKey,
  labelsOf: D.labelsOf,
  buildOptions: function (spec) {
    var out = D.buildOptions(spec);
    BUILD_CALLS.push({ spec: spec, out: out });
    return out;
  }
};

var RNAMES = ['rBuildOptions', 'startRound', 'rSetBlocks',
              'rSetStatus', 'rAnnounceWrong', 'rAnnounceCorrect', 'rFocusNextOption',
              'rRender', 'syncRoundAudioReadiness', 'rPlayCurrent',
              'rPickOption', 'rRevealLetter', 'rCheckAnswer', 'rRecord', 'rShowDone',
              'rAdvance', 'rExit'];
var RSRC = {};
RNAMES.forEach(function (n) { RSRC[n] = extractFunction(INDEX, n); });
var rStateMatch = INDEX.match(/const\s+R\s*=\s*(\{[^}]*\})\s*;/);
if (!rStateMatch) throw new Error('extract: Mixed Quiz state object R not found in index.html');
var R = (0, eval)('(' + rStateMatch[1] + ')');

var PP_TYPED_INDEX = PP_ANSWER.buildIndex([]);

// `$` is JXA's ObjC bridge here, so the shipping code's helpers are handed in as
// PARAMETERS of a generated scope rather than planted as globals.
var MIXED = (new Function('$', 'document', 'show', 'R', 'LEVELS', 'poolFor', 'gShuffle',
  'ppEligibleFor', 'ppAppendUsageTo', 'ppVariantParts', 'ppProgressWritable', 'loadV2', 'saveV2',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'G_AUDIO', 'PP_DISTRACTOR',
  RNAMES.map(function (n) { return RSRC[n]; }).join('\n') + '\n' +
  'return {\n' +
  '  rBuildOptions: function(a,b,c){ return rBuildOptions(a,b,c); },\n' +
  '  startRound: function(a,b){ return startRound(a,b); },\n' +
  '  rRender: function(){ return rRender(); },\n' +
  '  rRecord: function(q,res){ return rRecord(q,res); },\n' +
  '  rAdvance: function(){ return rAdvance(); },\n' +
  '  syncReadiness: function(){ return syncRoundAudioReadiness(); }\n' +
  '};'
))(el, fakeDoc, fakeShow, R, LEVELS, fakePoolFor, fakeShuffle,
   ppEligibleFor, fakeAppendUsage, ppVariantPartsStub, fakeProgressWritable, fakeLoadV2, fakeSaveV2,
   PP_ANSWER, PP_TYPED_INDEX, ppHasMainAudio, ppMainAudioText, '<svg data-icon="audio"></svg>', SPY);

function buildRaw(correctItem, candidates, fmt) { return MIXED.rBuildOptions(correctItem, candidates, fmt); }
// A safe VIEW of an option set. Whether the options are records at all is asserted
// once, on the raw result, in A1; every claim after that reads through here, so a
// build that still hands back plain strings produces a named failure per rule
// instead of one dereference error that hides the other nineteen.
function recs(list) {
  return (Array.isArray(list) ? list : []).map(function (o) {
    return o && typeof o === 'object' ? o : {};
  });
}
function build(correctItem, candidates, fmt) { return recs(buildRaw(correctItem, candidates, fmt)); }
function labelsOf(list) { return list.map(function (o) { return o && o.label; }); }
function idsOf(list) { return list.map(function (o) { return o && o.id; }); }
function correctOf(list) { return list.filter(function (o) { return o && o.correct === true; }); }
// The correct record, or a blank stand-in - so an assertion about it reports a
// mismatch rather than throwing when there is no such record at all.
function theCorrect(list) { return correctOf(list)[0] || {}; }
function item(card, topic) { return { c: card, topic: topic || 'T' }; }

// =========================================================================
// A. THE RETURNED RECORD CONTRACT
// =========================================================================
// An option is no longer a string. It is the visible label PLUS the source it came
// from, because "which option is right" has to survive two cards sharing a gloss.
var A_ANSWER = { id: 'a-1', pl: 'aaa', en: 'alpha' };
var A_CARDS = [A_ANSWER,
               { id: 'a-2', pl: 'bbb', en: 'beta' },
               { id: 'a-3', pl: 'ccc', en: 'gamma' },
               { id: 'a-4', pl: 'ddd', en: 'delta' },
               { id: 'a-5', pl: 'eee', en: 'epsilon' }];
var A_POOL = A_CARDS.map(function (c) { return item(c, 'Fixture topic'); });
SHUFFLE = KEEP;
var A_RAW = buildRaw(A_POOL[0], A_POOL, 'mc');
var A_BUILT = recs(A_RAW);

eq('A1 an option-bearing question gets four options', A_RAW.length, 4);
ok('A1 every option is a record, not a string',
   A_RAW.length > 0 &&
   A_RAW.every(function (o) { return o && typeof o === 'object' && typeof o.label === 'string'; }));
ok('A1 every record carries its card', A_BUILT.every(function (o) { return o.card && A_CARDS.indexOf(o.card) !== -1; }));
ok('A1 every record carries its pool item', A_BUILT.every(function (o) { return A_POOL.indexOf(o.item) !== -1; }));
ok('A1 every record carries its topic', A_BUILT.every(function (o) { return o.topic === 'Fixture topic'; }));
ok('A1 every record carries its stable id', A_BUILT.every(function (o) { return o.card && o.id === o.card.id; }));
ok('A1 every record carries a boolean correct flag',
   A_BUILT.every(function (o) { return o.correct === true || o.correct === false; }));
ok('A1 the visible label is the card gloss', A_BUILT.every(function (o) { return o.card && o.label === o.card.en; }));
ok('A1 every label is a non-empty string', A_BUILT.every(function (o) { return typeof o.label === 'string' && o.label.length > 0; }));

eq('A2 exactly one record is the correct one', correctOf(A_BUILT).length, 1);
ok('A2 the correct record is the asked card', theCorrect(A_BUILT).card === A_ANSWER);
ok('A2 the correct record is the asked card\'s own pool item', theCorrect(A_BUILT).item === A_POOL[0]);
eq('A2 the correct record carries the asked card\'s stable id', theCorrect(A_BUILT).id, 'a-1');
eq('A2 the correct record shows the asked card\'s gloss', theCorrect(A_BUILT).label, 'alpha');
eq('A2 the answer is offered exactly once by label',
   A_BUILT.filter(function (o) { return o.label === 'alpha'; }).length, 1);

// Nothing handed in is modified: the pool the caller keeps is the pool it passed.
var A_POOL_SNAPSHOT = JSON.stringify(A_POOL);
buildRaw(A_POOL[0], A_POOL, 'mc');
eq('A3 the candidate pool is never mutated', JSON.stringify(A_POOL), A_POOL_SNAPSHOT);
ok('A3 the source cards are never mutated',
   A_CARDS.every(function (c) { return Object.keys(c).sort().join(',') === 'en,id,pl'; }));
ok('A3 a fresh array is returned each time', buildRaw(A_POOL[0], A_POOL, 'mc') !== A_RAW);

// =========================================================================
// B. FORMAT-SPECIFIC PROMPT IDENTITY
// =========================================================================
// The two option-bearing formats print the same English on the buttons, so the
// LABEL rule is shared. Their PROMPTS are different senses, and the fixtures below
// are the one card shape where those two senses genuinely disagree: a template's
// `pl` is a display pattern shown on screen, while the main speaker plays only its
// complete `audioText`. So the same three cards must be filtered differently
// depending on which format is asking.
var B_ANSWER = { id: 'b-0', pl: 'Gdzie jest...?', en: 'Where is...?',
                 cardType: 'template', audioText: 'Gdzie jest dworzec?' };
var B_SAME_HEARD = { id: 'b-1', pl: 'Inny wzor...?', en: 'a heard twin',
                     cardType: 'template', audioText: 'Gdzie jest dworzec?' };
var B_SAME_PRINTED = { id: 'b-2', pl: 'Gdzie jest...?', en: 'a printed twin',
                       cardType: 'template', audioText: 'Gdzie jest apteka?' };
var B_SAFE_1 = { id: 'b-3', pl: 'Ile to kosztuje?', en: 'safe one' };
var B_SAFE_2 = { id: 'b-4', pl: 'Dzien dobry', en: 'safe two' };
var B_POOL = [B_ANSWER, B_SAME_HEARD, B_SAME_PRINTED, B_SAFE_1, B_SAFE_2]
               .map(function (c) { return item(c, 'T'); });

// The fixture only means anything if the two extractors really do disagree on it.
eq('B0 the answer is heard as its complete utterance', ppMainAudioText(B_ANSWER), 'Gdzie jest dworzec?');
eq('B0 the answer is printed as its display pattern', B_ANSWER.pl, 'Gdzie jest...?');
ok('B0 the heard and the printed prompt are genuinely different',
   nk(ppMainAudioText(B_ANSWER)) !== nk(B_ANSWER.pl));

SHUFFLE = KEEP;
var B_LISTEN = build(B_POOL[0], B_POOL, 'listen');
eq('B1 a listen question still gets four options', B_LISTEN.length, 4);
eq('B1 the card that SOUNDS like the question is excluded',
   B_LISTEN.filter(function (o) { return o.card === B_SAME_HEARD; }).length, 0);
eq('B1 the card that merely LOOKS like the question is allowed in',
   B_LISTEN.filter(function (o) { return o.card === B_SAME_PRINTED; }).length, 1);

var B_MC = build(B_POOL[0], B_POOL, 'mc');
eq('B2 an mc question still gets four options', B_MC.length, 4);
eq('B2 the card that is PRINTED like the question is excluded',
   B_MC.filter(function (o) { return o.card === B_SAME_PRINTED; }).length, 0);
eq('B2 the card that merely SOUNDS like the question is allowed in',
   B_MC.filter(function (o) { return o.card === B_SAME_HEARD; }).length, 1);

// The extractors themselves, taken from the calls the Mixed Quiz actually made -
// not from how the call is typed. A build that never reaches the shared builder has
// no spec to show, which is itself the failure.
function specAt(fromEnd) {
  var hit = BUILD_CALLS[BUILD_CALLS.length - fromEnd];
  return (hit && hit.spec) || {};
}
function prompt(spec, card) {
  return typeof spec.heardOf === 'function' ? spec.heardOf(card) : '(no prompt extractor was passed)';
}
var B_LISTEN_SPEC = specAt(2), B_MC_SPEC = specAt(1);
ok('B3 both formats reached the shared builder', BUILD_CALLS.length >= 2);
ok('B3 both asked for four options', B_LISTEN_SPEC.count === 4 && B_MC_SPEC.count === 4);
ok('B3 both injected the app shuffle',
   B_LISTEN_SPEC.shuffle === fakeShuffle && B_MC_SPEC.shuffle === fakeShuffle);
ok('B3 the listen format passes the real main-audio rule', B_LISTEN_SPEC.heardOf === ppMainAudioText);
ok('B3 the mc format passes a different extractor',
   typeof B_MC_SPEC.heardOf === 'function' && B_MC_SPEC.heardOf !== ppMainAudioText);
eq('B3 the mc extractor reads the printed Polish', prompt(B_MC_SPEC, B_ANSWER), B_ANSWER.pl);
eq('B3 ... on an ordinary card too', prompt(B_MC_SPEC, B_SAFE_1), 'Ile to kosztuje?');
ok('B3 neither format uses English as prompt identity',
   prompt(B_LISTEN_SPEC, B_SAFE_1) !== B_SAFE_1.en && prompt(B_MC_SPEC, B_SAFE_1) !== B_SAFE_1.en);

// The typed format asks the learner to produce, not to choose. It never reaches the
// builder at all - which is why a typed question cannot gain a button by accident.
var B_BEFORE = BUILD_CALLS.length;
var B_TYPE = build(B_POOL[0], B_POOL, 'type');
eq('B4 a typed question builds no options', B_TYPE, []);
eq('B4 the shared builder was not called for it', BUILD_CALLS.length, B_BEFORE);
var B_UNKNOWN = build(B_POOL[0], B_POOL, 'something-else');
eq('B4 an unknown format builds nothing either', B_UNKNOWN, []);
eq('B4 ... and still does not reach the builder', BUILD_CALLS.length, B_BEFORE);

// =========================================================================
// C. VISIBLE-LABEL SAFETY
// =========================================================================
// The old exact-string filter let every one of these through.
var C_ANSWER = { id: 'c-0', pl: 'c-ans', en: 'To be sure' };
function cPool(extra) {
  return [C_ANSWER].concat(extra).concat([
    { id: 'c-s1', pl: 'c-s1', en: 'safe one' },
    { id: 'c-s2', pl: 'c-s2', en: 'safe two' },
    { id: 'c-s3', pl: 'c-s3', en: 'safe three' }
  ]).map(function (c) { return item(c, 'T'); });
}
function cBuild(extra) {
  SHUFFLE = KEEP;
  var pool = cPool(extra);
  return build(pool[0], pool, 'mc');
}
function isCard(o, card) { return !!o && o.card === card; }
function hasId(o, id) { return !!o && !!o.card && o.card.id === id; }
function labelKeys(built) { return built.map(function (o) { return nk(o && o.label); }); }
function hasDupKey(built) {
  var seen = {}, dup = false;
  labelKeys(built).forEach(function (k) { if (seen[k]) dup = true; seen[k] = 1; });
  return dup;
}
var C_EXACT = cBuild([{ id: 'c-1', pl: 'c-1', en: 'To be sure' }]);
eq('C1 an exact duplicate of the answer never appears', C_EXACT.filter(function (o) { return hasId(o, 'c-1'); }).length, 0);
eq('C1 the question is still full', C_EXACT.length, 4);
var C_CASE = cBuild([{ id: 'c-2', pl: 'c-2', en: 'TO BE SURE' }]);
eq('C2 a case-only duplicate never appears', C_CASE.filter(function (o) { return hasId(o, 'c-2'); }).length, 0);
var C_SPACE = cBuild([{ id: 'c-3', pl: 'c-3', en: '  To   be  sure  ' }]);
eq('C3 a whitespace-only duplicate never appears', C_SPACE.filter(function (o) { return hasId(o, 'c-3'); }).length, 0);
var C_PUNCT = cBuild([{ id: 'c-4', pl: 'c-4', en: 'To be sure!' }]);
eq('C4 a punctuation-only duplicate never appears', C_PUNCT.filter(function (o) { return hasId(o, 'c-4'); }).length, 0);
// Two DISTRACTORS that read the same as each other, neither of them the answer.
var C_TWINS = cBuild([{ id: 'c-5', pl: 'c-5', en: 'A twin gloss' },
                      { id: 'c-6', pl: 'c-6', en: 'a twin gloss.' }]);
eq('C5 two distractors that read the same never share a question',
   C_TWINS.filter(function (o) { return hasId(o, 'c-5') || hasId(o, 'c-6'); }).length, 1);
ok('C5 no two options share a normalised label', !hasDupKey(C_TWINS));
eq('C5 the question is still full', C_TWINS.length, 4);
[C_EXACT, C_CASE, C_SPACE, C_PUNCT].forEach(function (b, i) {
  ok('C6 no two options share a normalised label (case ' + (i + 1) + ')', !hasDupKey(b));
  eq('C6 the answer is still offered exactly once (case ' + (i + 1) + ')', correctOf(b).length, 1);
});

// =========================================================================
// D. SOURCE SAFETY
// =========================================================================
// The fewer-than-four fallback concatenates the level's records onto the topic's
// own, so the SAME source arriving twice is the ordinary case, not an edge one.
var D_ANSWER = { id: 'd-0', pl: 'd-ans', en: 'the answer' };
var D_SAFE = [{ id: 'd-1', pl: 'd-1', en: 'one' },
              { id: 'd-2', pl: 'd-2', en: 'two' },
              { id: 'd-3', pl: 'd-3', en: 'three' }];
var D_ANSWER_ITEM = item(D_ANSWER, 'T');

SHUFFLE = KEEP;
// ...the same card object offered twice
var D_TWICE = build(D_ANSWER_ITEM,
                    [D_ANSWER_ITEM, item(D_SAFE[0]), item(D_SAFE[0]), item(D_SAFE[1]), item(D_SAFE[2])], 'mc');
eq('D1 the same card offered twice appears once',
   D_TWICE.filter(function (o) { return o.card === D_SAFE[0]; }).length, 1);
eq('D1 the question is still full', D_TWICE.length, 4);
// ...cloned pool ITEMS wrapping one card, as the level-wide join really produces
var D_CLONED = build(D_ANSWER_ITEM,
                     [D_ANSWER_ITEM, { c: D_SAFE[0], topic: 'T' }, { c: D_SAFE[0], topic: 'Elsewhere' },
                      item(D_SAFE[1]), item(D_SAFE[2])], 'mc');
eq('D2 two pool items wrapping one card yield one option',
   D_CLONED.filter(function (o) { return o.card === D_SAFE[0]; }).length, 1);
ok('D2 no source object is used twice', (function () {
  var seen = [];
  return D_CLONED.every(function (o) { if (seen.indexOf(o.card) !== -1) return false; seen.push(o.card); return true; });
})());
// ...two DIFFERENT card objects carrying one stable id
var D_SAMEID = build(D_ANSWER_ITEM,
                     [D_ANSWER_ITEM,
                      { c: { id: 'd-9', pl: 'd-9a', en: 'first face' }, topic: 'T' },
                      { c: { id: 'd-9', pl: 'd-9b', en: 'second face' }, topic: 'T' },
                      item(D_SAFE[0]), item(D_SAFE[1])], 'mc');
eq('D3 one stable id is offered once however many objects carry it',
   D_SAMEID.filter(function (o) { return o.id === 'd-9'; }).length, 1);
eq('D3 no two options share a stable id', (function () {
  var seen = {}, dups = [];
  idsOf(D_SAMEID).forEach(function (i) { if (seen[i]) dups.push(i); seen[i] = 1; });
  return dups;
})(), []);
// ...the answer itself duplicated in the fallback, by object AND by id
var D_SELF = build(D_ANSWER_ITEM,
                   [D_ANSWER_ITEM, D_ANSWER_ITEM, { c: D_ANSWER, topic: 'Elsewhere' },
                    { c: { id: 'd-0', pl: 'd-0b', en: 'another face of the answer' }, topic: 'T' },
                    item(D_SAFE[0]), item(D_SAFE[1]), item(D_SAFE[2])], 'mc');
eq('D4 the correct source is offered exactly once', D_SELF.filter(function (o) { return o.card === D_ANSWER; }).length, 1);
eq('D4 the correct record is still the only correct one', correctOf(D_SELF).length, 1);
eq('D4 no other card wearing the answer\'s id gets in', D_SELF.filter(function (o) { return o.id === 'd-0'; }).length, 1);
eq('D4 the question is still full', D_SELF.length, 4);

// =========================================================================
// E. THE LARGEST SAFE SET, NOT THE FIRST ONE FOUND
// =========================================================================
// Safety is a rule about PAIRS, so an early pick can rule out two later cards
// through two different keys. A greedy builder would hand the learner three buttons
// where four were available; the shared exhaustive search must not.
var E_ANSWER = { id: 'e-0', pl: 'e-ans', en: 'the answer' };
var E_P = { id: 'e-1', pl: 'clip-one', en: 'gloss one' };     // greedy takes this first...
var E_Q = { id: 'e-2', pl: 'clip-two', en: 'gloss one' };     // ...and it blocks this by label
var E_R = { id: 'e-3', pl: 'clip-one', en: 'gloss two' };     // ...and this by prompt
var E_S = { id: 'e-4', pl: 'clip-three', en: 'gloss three' };
SHUFFLE = KEEP;
var E_ITEM = item(E_ANSWER, 'T');
var E_BUILT = build(E_ITEM, [E_ITEM, item(E_P), item(E_Q), item(E_R), item(E_S)], 'mc');
eq('E1 the question is filled from a pool a greedy pick would underfill', E_BUILT.length, 4);
eq('E1 it is the combination that actually fits',
   idsOf(E_BUILT).filter(function (i) { return i !== 'e-0'; }).sort(), ['e-2', 'e-3', 'e-4']);
ok('E1 the greedy first candidate was dropped to make room',
   E_BUILT.filter(function (o) { return o.card === E_P; }).length === 0);
ok('E1 the returned set is internally safe', (function () {
  var l = {}, h = {}, okAll = true;
  E_BUILT.forEach(function (o) {
    if (!o || !o.card) { okAll = false; return; }
    var lk = nk(o.label), hk = nk(o.card.pl);
    if (l[lk] || h[hk]) okAll = false;
    l[lk] = 1; h[hk] = 1;
  });
  return okAll;
})());
// An honestly short pool returns the honest maximum rather than padding.
var E_SHORT = build(E_ITEM, [E_ITEM, item(E_P), item(E_Q)], 'mc');
eq('E2 a pool holding one safe distractor returns two options', E_SHORT.length, 2);
eq('E2 ... and the answer is one of them', correctOf(E_SHORT).length, 1);
var E_NONE = build(E_ITEM, [E_ITEM], 'mc');
eq('E3 a pool holding nothing safe still returns the answer alone', E_NONE.length, 1);
eq('E3 ... and it is the correct record', correctOf(E_NONE).length, 1);

// =========================================================================
// F. TOPIC PREFERENCE
// =========================================================================
// Wrong answers should be plausible neighbours, so same-topic candidates are
// preferred - but never at the cost of an option.
var F_ANSWER = { id: 'f-0', pl: 'f-ans', en: 'the answer' };
function fCard(n, t) { return { id: 'f-' + n, pl: 'f-pl-' + n, en: 'f-gloss-' + n }; }
var F_NEAR = [fCard(1), fCard(2), fCard(3)];
var F_FAR = [fCard(4), fCard(5), fCard(6)];
SHUFFLE = KEEP;
var F_ITEM = item(F_ANSWER, 'Near topic');
var F_FULL = build(F_ITEM, [F_ITEM]
  .concat(F_FAR.map(function (c) { return item(c, 'Far topic'); }))
  .concat(F_NEAR.map(function (c) { return item(c, 'Near topic'); })), 'mc');
eq('F1 every distractor comes from the asked topic when that is possible',
   F_FULL.filter(function (o) { return o.topic === 'Near topic'; }).length, 4);
eq('F1 ... even though the far cards were offered first', F_FULL.length, 4);
// Only one same-topic card is safe: the rest of the question comes from further out.
var F_THIN = build(F_ITEM, [F_ITEM, item(F_NEAR[0], 'Near topic')]
  .concat(F_FAR.map(function (c) { return item(c, 'Far topic'); })), 'mc');
eq('F2 the question is still full when the topic runs out', F_THIN.length, 4);
eq('F2 the one safe same-topic distractor is still used',
   F_THIN.filter(function (o) { return o.card === F_NEAR[0]; }).length, 1);
eq('F2 the rest come from the wider pool',
   F_THIN.filter(function (o) { return o.topic === 'Far topic'; }).length, 2);
// Order is the injected randomness's business; correctness is not.
SHUFFLE = REVERSE;
var F_REV = build(F_ITEM, [F_ITEM]
  .concat(F_NEAR.map(function (c) { return item(c, 'Near topic'); })), 'mc');
eq('F3 a different shuffle still yields exactly one correct record', correctOf(F_REV).length, 1);
ok('F3 ... and it is still the asked card', theCorrect(F_REV).card === F_ANSWER);
eq('F3 ... and the question is still full', F_REV.length, 4);
SHUFFLE = KEEP;

// =========================================================================
// G. RENDERING - what the button shows, and what decides the answer
// =========================================================================
// Authored content that would become markup if anything interpolated it.
var G_CARDS = [
  { id: 'g1', pl: '<b>zly</b> & "gorszy"', en: 'bad & <i>worse</i>' },
  { id: 'g2', pl: 'cudzyslow "test"', en: 'quote "mark" test' },
  { id: 'g3', pl: 'znak <mniejszy', en: 'less < than' },
  { id: 'g4', pl: "apostrof 'jeden'", en: "it's an apostrophe" },
  { id: 'g5', pl: 'ampersand & spojnik', en: 'fish & chips' },
  { id: 'g6', pl: 'cudzy > wiekszy', en: 'greater > than' }
];
// One compiled scope, two fixture worlds: the contents of LEVELS are replaced, never
// the array, because the shipping code closed over the reference at compile time.
function setTopic(o) {
  LEVELS.length = 0;
  LEVELS.push({ level: o.level || 'A1', topics: [{
    id: o.id || 'topic-1', name: o.name || 'Fixture topic', src: [o.level || 'A1'],
    kind: o.kind, mature: !!o.mature, cards: o.cards
  }] });
  POOL_FOR = o.poolFor || function () { return []; };
}
function resetRound(o) {
  o = o || {};
  DOM = {}; shown = []; HTML_WRITES = {}; SPOKEN = []; STOPS = 0;
  STORE = { progress: {} };
  audioManifestStatus = 'ready';
  SHUFFLE = o.shuffle || KEEP;
  BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
  ACTIVE = BODY;
  MIXED.startRound(0, 0);
  if (o.at !== undefined) { R.i = o.at; MIXED.rRender(); }
}
function opts() { return el('rOpts').children; }
function q() { return R.qs[R.i]; }
// The button for a given RECORD - looked up by identity, never by its text, because
// the whole point of the phase is that the text is not the key.
function btnFor(rec) {
  var at = q().options.indexOf(rec);
  if (at === -1) throw new Error('fixture: that record is not in the current question');
  return opts()[at];
}
function correctRec() {
  var hit = correctOf(q().options);
  if (hit.length !== 1) throw new Error('fixture: expected exactly one correct record');
  return hit[0];
}
function wrongRecs() { return recs(q().options).filter(function (o) { return !o.correct; }); }

section('G rendering', function () {
setTopic({ cards: G_CARDS, name: 'Nasty topic' });
resetRound();
eq('G0 the round was built', R.qs.length, G_CARDS.length);
// With an identity shuffle the formats cycle listen / type / mc from question 0.
eq('G0 question 0 is the listen format', R.qs[0].fmt, 'listen');
eq('G0 question 1 is the typed format', R.qs[1].fmt, 'type');
eq('G0 question 2 is the multiple-choice format', R.qs[2].fmt, 'mc');
eq('G0 typed questions carry no options', R.qs.filter(function (x) { return x.fmt === 'type'; })
     .every(function (x) { return x.options.length === 0; }), true);
eq('G0 option-bearing questions carry four records each',
   R.qs.filter(function (x) { return x.fmt !== 'type' && x.options.length === 4; }).length,
   R.qs.filter(function (x) { return x.fmt !== 'type'; }).length);

eq('G1 one button was rendered per option record', opts().length, q().options.length);
ok('G1 each button shows its record\'s label', q().options.every(function (o, i) {
  return opts()[i].textContent === o.label;
}));
ok('G1 the authored ampersands, quotes and angle brackets survive as text',
   recs(q().options).every(function (o, i) { return !!o.card && opts()[i].textContent === o.card.en; }));
ok('G1 an option label containing markup really is in this question',
   q().options.some(function (o) { return /[<>&"']/.test(o.label); }));
ok('G1 no option button was written through innerHTML',
   opts().every(function (b) { return b.innerHTML === ''; }));

// Correctness is read from the record, never from the visible string. Flipping the
// flags proves it: the button whose text equals the card gloss is now WRONG, and a
// button whose text does not is now RIGHT.
resetRound({ at: 2 });                                   // an mc question
var G_REAL = correctRec(), G_DECOY = wrongRecs()[0];
G_REAL.correct = false; G_DECOY.correct = true;
btnFor(G_DECOY).click();
ok('G2 the record\'s flag decides the answer, not its text', btnFor(G_DECOY).classes.correct === true);
eq('G2 the whole record reached the handler, mutation and all',
   btnFor(G_DECOY).getAttribute('aria-label'), G_DECOY.label + ', correct');
ok('G2 the label that matches the card gloss was not treated as the answer',
   G_REAL.label === q().c.en && btnFor(G_REAL).classes.correct !== true);
resetRound({ at: 2 });
var G_REAL2 = correctRec(), G_DECOY2 = wrongRecs()[0];
G_REAL2.correct = false; G_DECOY2.correct = true;
btnFor(G_REAL2).click();
ok('G3 the option whose text is the card gloss is now rejected', btnFor(G_REAL2).classes.wrong === true);
eq('G3 ... and is named by its own label',
   btnFor(G_REAL2).getAttribute('aria-label'), G_REAL2.label + ', incorrect. Try again');
eq('G3 ... and the announcement uses that label too',
   el('rStatus').textContent, G_REAL2.label + ' is not correct. Try another answer.');
});

// =========================================================================
// H. SCORING AND ACCESSIBILITY, UNCHANGED
// =========================================================================
var H_CARDS = [
  { id: 'h1', pl: 'kawa', en: 'coffee', ex: 'Popros kawe.', exEn: 'A coffee, please.' },
  { id: 'h2', pl: 'maka', en: 'flour' },
  { id: 'h3', pl: 'woda', en: 'water' },
  { id: 'h4', pl: 'sok', en: 'juice' },
  { id: 'h5', pl: 'mleko', en: 'milk' },
  { id: 'h6', pl: 'chleb', en: 'bread' }
];
section('H scoring and accessibility', function () {
setTopic({ cards: H_CARDS, name: 'W kawiarni' });

resetRound();
var H_LEN = R.qs.length;
btnFor(correctRec()).click();
eq('H1 a first-attempt success is still scored right', q().result, 'right');
eq('H1 ... and requeues nothing', R.qs.length, H_LEN);
eq('H1 the chosen button is named as correct',
   btnFor(correctRec()).getAttribute('aria-label'), correctRec().label + ', correct');
eq('H1 every option is closed once the question is settled',
   opts().filter(function (b) { return !b.disabled; }).length, 0);
eq('H1 the Polish answer is revealed on a listen question', el('rReveal').textContent, q().c.pl);
eq('H1 the announcement names the Polish answer',
   el('rStatus').textContent, 'Correct. The Polish answer is ' + q().c.pl + '. Next is ready.');
ok('H1 Next was opened', el('rNext').disabled === false);
ok('H1 focus moved to Next', ACTIVE === el('rNext'));

resetRound();
var H_WRONG = wrongRecs()[0];
btnFor(H_WRONG).click();
eq('H2 a wrong option is named by its own label',
   btnFor(H_WRONG).getAttribute('aria-label'), H_WRONG.label + ', incorrect. Try again');
eq('H2 the announcement names the same label',
   el('rStatus').textContent, H_WRONG.label + ' is not correct. Try another answer.');
ok('H2 the chosen button is closed', btnFor(H_WRONG).disabled === true);
eq('H2 no other option was closed', opts().filter(function (b) { return b.disabled; }).length, 1);
ok('H2 focus stayed among the options and is not on <body>',
   opts().indexOf(ACTIVE) !== -1 && ACTIVE !== BODY);
ok('H2 nothing was scored yet', q().result === null);
ok('H2 Next stays closed', el('rNext').disabled === true);
btnFor(correctRec()).click();
eq('H3 wrong then correct is still a miss', q().result, 'miss');
eq('H3 exactly one retry was queued', R.qs.length, H_LEN + 1);
ok('H3 the retry is marked as one', R.qs[R.qs.length - 1].requeued === true);
ok('H3 focus still ends on Next', ACTIVE === el('rNext'));
});

// =========================================================================
// I. REQUEUED QUESTIONS
// =========================================================================
section('I requeued questions', function () {
setTopic({ cards: H_CARDS, name: 'W kawiarni' });
resetRound();
var I_FIRST = R.qs[0];
var I_ORIGINAL = I_FIRST.options.slice();
btnFor(wrongRecs()[0]).click();
btnFor(correctRec()).click();
var I_RETRY = R.qs[R.qs.length - 1];
eq('I1 the retry is the same card', I_RETRY.c === I_FIRST.c, true);
eq('I1 the retry is the same format', I_RETRY.fmt, I_FIRST.fmt);
eq('I1 the retry gets four options', I_RETRY.options.length, 4);
ok('I1 the retry\'s option array is a new array', I_RETRY.options !== I_FIRST.options);
eq('I1 the retry has exactly one correct record', correctOf(I_RETRY.options).length, 1);
ok('I1 the retry\'s correct source is the same card', correctOf(I_RETRY.options)[0].card === I_FIRST.c);
eq('I1 the retry offers the same safe set',
   idsOf(I_RETRY.options).slice().sort(), idsOf(I_ORIGINAL).slice().sort());
ok('I1 the retry is internally safe', (function () {
  var l = {}, h = {}, s = [], good = true;
  I_RETRY.options.forEach(function (o) {
    var lk = nk(o.label), hk = nk(ppMainAudioText(o.card));
    if (l[lk] || h[hk] || s.indexOf(o.card) !== -1) good = false;
    l[lk] = 1; h[hk] = 1; s.push(o.card);
  });
  return good;
})());
// A retry never scores and never breeds another retry.
var I_BEFORE = R.qs.length;
MIXED.rRecord(I_RETRY, 'miss');
eq('I2 a requeued question banks no result', I_RETRY.result, null);
eq('I2 ... and queues no second retry', R.qs.length, I_BEFORE);
// Rendering the retry starts from a clean set of buttons.
R.i = R.qs.length - 1; MIXED.rRender();
eq('I3 the retry renders four fresh buttons', opts().length, 4);
eq('I3 none of them carries a stale disabled state',
   opts().filter(function (b) { return b.disabled; }).length, 0);
eq('I3 none of them carries a stale result class',
   opts().filter(function (b) { return b.classes.wrong || b.classes.correct; }).length, 0);
// A typed question's retry stays optionless.
resetRound({ at: 1 });
eq('I4 the fixture really is a typed question', q().fmt, 'type');
var I_TYPED = q(), I_TYPED_BEFORE = R.qs.length;
MIXED.rRecord(I_TYPED, 'miss');
eq('I4 a typed miss still requeues once', R.qs.length, I_TYPED_BEFORE + 1);
eq('I4 the typed retry carries no options', R.qs[R.qs.length - 1].options, []);
eq('I4 the typed retry is the same card', R.qs[R.qs.length - 1].c === I_TYPED.c, true);
});

// The reshuffle really is a reshuffle: across seeds the retry's order varies while
// its membership does not. Reported rather than asserted for any ONE seed - a
// permutation is allowed to come back in the same order by chance.
section('I retry ordering report', function () {
  var orders = {};
  SEEDS.forEach(function (s) {
    resetRound({ shuffle: seededShuffle(s) });
    var first = R.qs[0];
    if (first.fmt === 'type') return;
    btnFor(wrongRecs()[0]).click();
    btnFor(correctRec()).click();
    orders[idsOf(R.qs[R.qs.length - 1].options).join('|')] = 1;
  });
  info('distinct retry orderings observed across ' + SEEDS.length + ' seeds: ' + Object.keys(orders).length);
});

// =========================================================================
// J. THE REAL CORPUS
// =========================================================================
// Every scope the learner can actually start a Mixed Quiz in, swept through the
// SHIPPING startRound over several deterministic seeds. Counts are reported, never
// asserted: the corpus is allowed to grow.
function realPoolFor(srcLevels, activity) {
  var act = activity || 'typeit', out = [];
  REAL_VOCAB_SRC.filter(function (lv) { return !srcLevels || srcLevels.indexOf(lv.level) !== -1; })
    .forEach(function (lv) {
      lv.topics.forEach(function (t) {
        if (t.mature) return;
        t.cards.forEach(function (c) { if (ppEligibleFor(c, act)) out.push({ c: c, topic: t.name }); });
      });
    });
  return out;
}
var REAL_VOCAB_SRC = REAL_LEVELS.filter(function (lv) {
  return lv.topics.length > 0 && lv.topics.every(function (t) { return !t.kind; });
});
// The two ways in: the topic list's Quiz pill (vocabulary and podcast sets that are
// not gated) and Study's "Quiz this set" (the same sets, including the gated one,
// reached after its gate).
var SCOPES = [];
REAL_LEVELS.forEach(function (lv, li) {
  lv.topics.forEach(function (t, ti) {
    if (!t.cards) return;
    if (t.kind && t.kind !== 'podcast') return;
    SCOPES.push({ li: li, ti: ti, level: lv.level, name: t.name, mature: !!t.mature });
  });
});

section('J the real-corpus sweep', function () {
  var bad = { count: [], correct: [], card: [], id: [], source: [], label: [], prompt: [], empty: [], record: [] };
  var short = [], questions = 0, byCount = {}, mutated = [];
  var SNAPSHOT = {};
  SCOPES.forEach(function (s) {
    REAL_LEVELS[s.li].topics[s.ti].cards.forEach(function (c) {
      if (!SNAPSHOT[c.id]) SNAPSHOT[c.id] = JSON.stringify(c);
    });
  });

  SCOPES.forEach(function (s) {
    var topic = REAL_LEVELS[s.li].topics[s.ti];
    SEEDS.forEach(function (seed) {
      // The real level and the real poolFor, so the fallback rule is the shipping one.
      LEVELS.length = 0;
      REAL_LEVELS.forEach(function (lv) { LEVELS.push(lv); });
      POOL_FOR = realPoolFor;
      DOM = {}; shown = []; HTML_WRITES = {};
      SHUFFLE = seededShuffle(seed);
      BODY = new FakeEl('body'); BODY.id = 'BODY'; DOM.BODY = BODY;
      ACTIVE = BODY;
      MIXED.startRound(s.li, s.ti);
      var where = s.level + ' / ' + s.name + ' [seed ' + seed + ']';
      R.qs.forEach(function (qq) {
        if (qq.fmt === 'type') {
          if (qq.options.length) bad.count.push(where + ' typed question carries options');
          return;
        }
        questions++;
        byCount[qq.options.length] = (byCount[qq.options.length] || 0) + 1;
        if (qq.options.length !== 4) short.push(where + ' ' + qq.c.id + ' -> ' + qq.options.length);
        var right = correctOf(qq.options);
        if (right.length !== 1) bad.correct.push(where + ' ' + qq.c.id);
        else {
          if (right[0].card !== qq.c) bad.card.push(where + ' ' + qq.c.id);
          if (right[0].id !== qq.c.id) bad.id.push(where + ' ' + qq.c.id);
        }
        var seenCard = [], seenId = {}, seenLabel = {}, seenPrompt = {};
        var promptOf = qq.fmt === 'listen' ? ppMainAudioText : function (card) { return card ? card.pl : ''; };
        qq.options.forEach(function (raw) {
          if (!raw || typeof raw !== 'object' || typeof raw.correct !== 'boolean' ||
              typeof raw.topic !== 'string' || typeof raw.id !== 'string') bad.record.push(where + ' ' + qq.c.id);
        });
        recs(qq.options).forEach(function (o) {
          if (!o.card || !o.item || typeof o.label !== 'string' || !o.label.length) bad.empty.push(where + ' ' + qq.c.id);
          if (seenCard.indexOf(o.card) !== -1) bad.source.push(where + ' ' + qq.c.id);
          seenCard.push(o.card);
          if (o.id) { if (seenId[o.id]) bad.id.push(where + ' ' + qq.c.id + ' dup id ' + o.id); seenId[o.id] = 1; }
          var lk = nk(o.label);
          if (seenLabel[lk]) bad.label.push(where + ' ' + qq.c.id + ' dup label ' + o.label);
          seenLabel[lk] = 1;
          var pk = nk(promptOf(o.card));
          if (seenPrompt[pk]) bad.prompt.push(where + ' ' + qq.c.id + ' dup prompt');
          seenPrompt[pk] = 1;
        });
      });
    });
    topic.cards.forEach(function (c) {
      if (SNAPSHOT[c.id] && SNAPSHOT[c.id] !== JSON.stringify(c)) mutated.push(c.id);
    });
  });

  info('Mixed Quiz scopes swept: ' + SCOPES.length + ' (of which gated: ' +
       SCOPES.filter(function (s) { return s.mature; }).length + ', podcast: ' +
       SCOPES.filter(function (s) { return s.name && REAL_LEVELS[s.li].topics[s.ti].kind === 'podcast'; }).length + ')');
  info('option-bearing questions built across ' + SCOPES.length + ' scopes x ' + SEEDS.length + ' seeds: ' + questions);
  info('options per question: ' + Object.keys(byCount).sort().map(function (k) { return k + ' -> ' + byCount[k]; }).join(', '));
  info('option-bearing questions returning fewer than four options: ' + short.length +
       (short.length ? '\n            ' + short.slice(0, 20).join('\n            ') : ''));
  eq('J1 every option-bearing question has exactly one correct record', bad.correct.slice(0, 5), []);
  eq('J1 the correct record is always the asked card', bad.card.slice(0, 5), []);
  eq('J1 no two options share a stable id, and the answer keeps its own', bad.id.slice(0, 5), []);
  eq('J2 no source card is used twice in one question', bad.source.slice(0, 5), []);
  eq('J2 no two options share a normalised English label', bad.label.slice(0, 5), []);
  eq('J2 no two options share a normalised prompt identity', bad.prompt.slice(0, 5), []);
  eq('J3 every option retains a card, a pool item and a visible label', bad.empty.slice(0, 5), []);
  eq('J3 typed questions never carry options', bad.count.slice(0, 5), []);
  eq('J3 every option is a retained record', bad.record.slice(0, 5), []);
  eq('J4 no source card was mutated by building a round', mutated.slice(0, 5), []);
});

// Semantic sense overlap - DISCOVERED, reported, and deliberately not fixed here.
// The audit method: a gloss may name several senses at once, separated by a slash or
// qualified in parentheses. Two cards whose FULL strings differ can still share one
// of those senses, and no amount of normalising the full string will notice.
section('J the semantic-overlap report', function () {
  function senses(en) {
    return String(en).split('/').map(function (part) {
      return nk(part.replace(/\([^)]*\)/g, ' '));
    }).filter(function (k) { return k.length > 2; });
  }
  var bySense = {}, pairs = [];
  SCOPES.forEach(function (s) {
    var topic = REAL_LEVELS[s.li].topics[s.ti];
    var pool = topic.cards.filter(function (c) { return ppEligibleFor(c, 'listen'); });
    pool.forEach(function (c) {
      senses(c.en).forEach(function (k) {
        (bySense[k] = bySense[k] || []).push({ c: c, scope: s.level + ' / ' + s.name });
      });
    });
  });
  Object.keys(bySense).forEach(function (k) {
    var hits = bySense[k];
    for (var i = 0; i < hits.length; i++) {
      for (var j = i + 1; j < hits.length; j++) {
        if (hits[i].c.id === hits[j].c.id) continue;
        if (nk(hits[i].c.en) === nk(hits[j].c.en)) continue;    // the builder already stops these
        if (hits[i].scope !== hits[j].scope) continue;          // only pairs that can share a question
        pairs.push({ sense: k, a: hits[i].c, b: hits[j].c, scope: hits[i].scope });
      }
    }
  });
  info('cards in one Mixed Quiz scope whose glosses differ as text but share a named sense: ' + pairs.length);
  pairs.slice(0, 6).forEach(function (p) {
    info('  still reachable (Phase 4E, not 4D): "' + p.a.en + '" beside "' + p.b.en + '"  [' + p.scope + ']');
  });
  info('Phase 4D does NOT remove these: PP_DISTRACTOR compares whole normalised strings and');
  info('cannot infer that two different sentences mean the same thing. Authored sense identity is Phase 4E.');
  // The honest claim about scope: these survive precisely because normalisation
  // cannot fold them, and nothing in this phase pretends otherwise.
  eq('J5 every reported pair is genuinely two different normalised strings',
     pairs.filter(function (p) { return nk(p.a.en) === nk(p.b.en); }).length, 0);
});

// =========================================================================
// K. PRODUCTION WIRING - the shipping code is what all of the above describes
// =========================================================================
var CODE_BUILD = codeOnly(RSRC.rBuildOptions);
var CODE_ROUND = codeOnly(RSRC.startRound);
var CODE_RENDER = codeOnly(RSRC.rRender);
var CODE_PICK = codeOnly(RSRC.rPickOption);
var CODE_RECORD = codeOnly(RSRC.rRecord);

ok('K1 rBuildOptions delegates to the shared builder', hasCode(CODE_BUILD, 'PP_DISTRACTOR.buildOptions('));
eq('K1 it delegates exactly once', countOf(squash(CODE_BUILD), 'PP_DISTRACTOR.buildOptions('), 1);
ok('K1 it asks for four options', hasCode(CODE_BUILD, 'count: 4'));
ok('K1 it injects the app shuffle', hasCode(CODE_BUILD, 'shuffle: gShuffle'));
ok('K1 the old inline filter is gone', CODE_BUILD.indexOf('pool.filter(') === -1);
ok('K1 it no longer maps sources down to strings', CODE_BUILD.indexOf('c=>c.en') === -1 &&
   CODE_BUILD.indexOf('c => c.en') === -1);
ok('K1 it reimplements none of the shared builder\'s rules',
   ['normalizeKey', 'new Set(', 'indexOf(', 'seen'].every(function (t) { return CODE_BUILD.indexOf(t) === -1; }));
// The prompt extractors are asserted on the calls that RAN, above in section B; here
// only that the format decision is visible in the code at all.
ok('K1 the prompt identity is chosen by question format', /fmt===?"listen"/.test(squash(CODE_BUILD)) &&
   /fmt===?"mc"/.test(squash(CODE_BUILD)));
ok('K1 the listen prompt is the shared main-audio rule', hasCode(CODE_BUILD, 'ppMainAudioText'));
ok('K1 the mc prompt is the printed Polish', /card=>card\.pl/.test(squash(CODE_BUILD)));

ok('K2 startRound builds pool RECORDS rather than raw cards', hasCode(CODE_ROUND, '{ c, topic: topic.name }'));
ok('K2 the fallback concatenates the level records without flattening them',
   hasCode(CODE_ROUND, 'dPool.concat(poolFor([LEVELS[l].level], "listen"))'));
ok('K2 the old flattening map is gone', CODE_ROUND.indexOf('x=>x.c') === -1 && CODE_ROUND.indexOf('x => x.c') === -1);
ok('K2 the correct source is the asked card\'s own pool item', hasCode(CODE_ROUND, 'items.find(it => it.c === c)'));
ok('K2 the format is passed to the builder', hasCode(CODE_ROUND, 'dPool, fmt)'));
ok('K2 sampling is unchanged', hasCode(CODE_ROUND, 'gShuffle(asked).slice(0,15)'));
ok('K2 eligibility is unchanged',
   hasCode(CODE_ROUND, 'ppEligibleFor(c, "listen")') && hasCode(CODE_ROUND, 'ppEligibleFor(c, "mixed")'));
ok('K2 the format balance is unchanged',
   hasCode(CODE_ROUND, 'topic.kind==="podcast" ? ["listen","mc"] : ["listen","type","mc"]') &&
   hasCode(CODE_ROUND, 'fmts[k % fmts.length]'));
ok('K2 the final question shuffle is unchanged', hasCode(CODE_ROUND, 'R.qs = gShuffle('));
ok('K2 neither source array is mutated by the join',
   CODE_ROUND.indexOf('.push(') === -1 && CODE_ROUND.indexOf('.splice(') === -1);

ok('K3 rRender writes the record\'s label as text', hasCode(CODE_RENDER, 'b.textContent=o.label'));
ok('K3 it hands the whole record to the answer handler', hasCode(CODE_RENDER, 'rPickOption(b, o, q, box)'));
// The reveal and feedback panels still use innerHTML - that is unchanged and owned
// elsewhere. The claim here is narrower: the OPTION BUTTON `b` is never written
// through it, so an authored gloss can never become markup.
ok('K3 it never writes an option label through innerHTML',
   !/(^|[^A-Za-z0-9_$])b\.innerHTML/.test(squash(CODE_RENDER)));

ok('K4 rPickOption decides by the retained flag', hasCode(CODE_PICK, 'o.correct===true'));
ok('K4 no bare-string equality decides correctness',
   ['o===q.c.en', 'o == q.c.en', 'q.c.en===o', 'o.label===q.c.en'].every(function (t) { return !hasCode(CODE_PICK, t); }));
ok('K4 the wrong accessible name uses the record label', hasCode(CODE_PICK, 'o.label + ", incorrect. Try again"'));
ok('K4 the correct accessible name uses the record label', hasCode(CODE_PICK, 'o.label + ", correct"'));
ok('K4 the wrong announcement uses the record label', hasCode(CODE_PICK, 'rAnnounceWrong(o.label)'));
ok('K4 the correct announcement still reads the card\'s Polish', hasCode(CODE_PICK, 'rAnnounceCorrect(q.c.pl)'));
ok('K4 first-attempt scoring is unchanged', hasCode(CODE_PICK, 'rRecord(q, R.attempted ? "miss" : "right")'));
ok('K4 the wrong arm still marks the question attempted and moves focus',
   hasCode(CODE_PICK, 'R.attempted=true') && hasCode(CODE_PICK, 'rFocusNextOption(box, btn)'));

ok('K5 rRecord still refuses to score or re-requeue a retry', hasCode(CODE_RECORD, 'if(q.requeued) return;'));
ok('K5 the retry\'s options come from the shared wrapper', hasCode(CODE_RECORD, 'rBuildOptions('));
ok('K5 the retry keeps the same card and format', hasCode(CODE_RECORD, 'c:q.c, fmt:q.fmt'));
ok('K5 the retry\'s correct source is the retained correct record',
   hasCode(CODE_RECORD, 'q.options.filter(o=>o.correct)[0]'));

// pp-distractor.js is not this phase's file. What is asserted is the permanent
// claim - that it stayed a GENERAL builder and learned nothing about the Mixed
// Quiz - rather than a copy of its text, which would fail on a reworded comment.
ok('K6 pp-distractor.js still exposes its documented surface',
   typeof D.buildOptions === 'function' && typeof D.normalizeKey === 'function' &&
   typeof D.labelsOf === 'function');
eq('K6 pp-distractor.js knows nothing about the Mixed Quiz',
   ['rBuildOptions', 'startRound', 'rPickOption', 'R.qs', 'q.fmt', '"mc"', '"listen"', '"type"']
     .filter(function (t) { return DISTRACTOR_SRC.indexOf(t) !== -1; }), []);
ok('K6 it still takes its randomness by injection', codeOnly(DISTRACTOR_SRC).indexOf('Math.random') === -1);
ok('K6 it still touches no DOM', codeOnly(DISTRACTOR_SRC).indexOf('document') === -1);
ok('K7 index.html loads pp-distractor.js before the Mixed Quiz uses it',
   INDEX.indexOf('<script src="pp-distractor.js"></script>') !== -1 &&
   INDEX.indexOf('<script src="pp-distractor.js"></script>') < INDEX.indexOf('function rBuildOptions('));

info('assertions run against the shipping Mixed Quiz code in index.html');
info('sections A-I are synthetic: no shipping card decides any contract assertion');

// ---------- report ----------
INFO.forEach(function (l) { console.log(l); });
LOG.forEach(function (l) { console.log(l); });
console.log('Mixed Quiz distractor tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
if (FAIL) { $.NSApplication; throw new Error(FAIL + ' assertion(s) failed'); }
