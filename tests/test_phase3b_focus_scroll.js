// Deterministic tests for Phase 3B-2B focus visibility, conversation turn continuity
// and screen-position restoration. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase3b_focus_scroll.js
//
// Issues covered:
//   MLG-3A-09  Type It (and the Mixed Quiz typed format) focused an off-screen Next.
//   MLG-3A-10  conversations never brought a new turn or its replies into view, and
//              the declared thread auto-scroll was inert.
//   MLG-3A-13  showScreen's scroll reset raced the browser's own history restoration.
//
// Every assertion drives shipping source extracted from index.html - the shared reveal
// helper, Type It, the Mixed Quiz typed path, the conversation renderer and the screen
// router - against a fake DOM with browser-like focus rejection and an explicit
// animation-frame queue. JavaScriptCore has no layout engine, so real geometry, real
// virtual keyboards, hardware Android Back, iOS Safari restoration, VoiceOver and
// TalkBack remain human checks; the Phase 3B-2B evidence reports record the browser
// measurements taken alongside this suite.

ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++)
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  return cwd + '/';
}
var ROOT = resolveRoot();
var INDEX = readFile(ROOT + 'index.html');
var SCENARIO_DATA = readFile(ROOT + 'data-scenarios.js');

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
// Fixture elements carry parent links, so they are compared by identity token rather
// than serialized: a fake DOM is a graph, and an assertion must not depend on that.
var SEEN = 0;
function stamp(value) {
  return JSON.stringify(value, function (key, v) {
    if (v && typeof v === 'object' && v.nodeType === 1) {
      if (!v.__token) v.__token = '<' + v.tagName.toLowerCase() + '#' + (v.id || '-') + ':' + (++SEEN) + '>';
      return v.__token;
    }
    return v;
  });
}
function eq(name, actual, expected) {
  var a = stamp(actual), e = stamp(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}
function squash(s) { return String(s).replace(/\s+/g, ''); }
function stripComments(src) {
  var out = '', mode = 'code';
  for (var i = 0; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') { mode = 'code'; out += c; } continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      out += c;
      if (c === '\\') { out += src[i + 1]; i++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; i++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; i++; continue; }
    if (c === "'") mode = 'sq'; else if (c === '"') mode = 'dq'; else if (c === '`') mode = 'tpl';
    out += c;
  }
  return out;
}
function extractFunction(src, name) {
  var needle = 'function ' + name + '(', start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: missing ' + name);
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: duplicate ' + name);
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0, mode = 'code';
  for (var i = open; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { i++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') || (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; i++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; i++; continue; }
    if (c === "'") { mode = 'sq'; continue; }
    if (c === '"') { mode = 'dq'; continue; }
    if (c === '`') { mode = 'tpl'; continue; }
    if (c === '{') depth++;
    else if (c === '}') { depth--; if (depth === 0) return src.slice(start, i + 1); }
  }
  throw new Error('extract: unbalanced ' + name);
}
function codeOf(name) { return squash(stripComments(extractFunction(INDEX, name))); }
function attrsFrom(source) {
  var attrs = {}, re = /([a-zA-Z_:][\w:.-]*)\s*=\s*"([^"]*)"/g, match;
  while ((match = re.exec(source)) !== null) attrs[match[1]] = match[2];
  return attrs;
}

// =========================================================================
// Fake DOM. Focus rejection matches the shipping validity boundary, and every
// scrollIntoView request is recorded verbatim so the reveal contract can be read
// back rather than inferred.
// =========================================================================
var BODY = null, DOC = null, REVEALS = [];
function ClassList(names) {
  this.names = {};
  (names || []).forEach(function (name) { this.names[name] = true; }, this);
}
ClassList.prototype.contains = function (name) { return !!this.names[name]; };
ClassList.prototype.add = function (name) { this.names[name] = true; };
ClassList.prototype.remove = function (name) { delete this.names[name]; };
ClassList.prototype.toggle = function (name, force) {
  var on = force === undefined ? !this.contains(name) : !!force;
  if (on) this.add(name); else this.remove(name);
  return on;
};
function TextNode(value) { this.nodeType = 3; this.textContent = String(value); this.parentElement = null; }
function El(id, tag) {
  this.id = id || ''; this.tagName = (tag || 'div').toUpperCase(); this.nodeType = 1;
  this.attrs = {}; this.children = []; this.parentElement = null; this.connected = true;
  this.hidden = false; this.inert = false; this.style = {}; this.className = '';
  this.classList = new ClassList(); this.value = ''; this.focusCount = 0;
  this.lastFocusOptions = null; this.revealCount = 0; this.listeners = {};
  this._disabled = false; this._text = ''; this._html = ''; this._queries = {};
}
Object.defineProperty(El.prototype, 'disabled', {
  get: function () { return this._disabled; },
  set: function (value) {
    this._disabled = !!value;
    if (this._disabled && DOC && DOC.activeElement === this) DOC.activeElement = BODY;
  }
});
Object.defineProperty(El.prototype, 'textContent', {
  get: function () {
    return this._text + this.children.map(function (child) { return child.textContent || ''; }).join('');
  },
  set: function (value) { this._text = String(value); this.children = []; this._html = ''; }
});
Object.defineProperty(El.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (value) {
    this._html = String(value); this._text = ''; this.children = []; this._queries = {};
    var classes = ['v-pl', 'v-altk', 'v-altv'];
    for (var i = 0; i < classes.length; i++)
      if (this._html.indexOf('class="' + classes[i] + '"') !== -1)
        this._queries['.' + classes[i]] = new El(this.id + '-' + classes[i], 'span');
    var open = this._html.match(/<button\b([^>]*class="mini-audio"[^>]*)>/);
    if (open) {
      var audio = new El(this.id + '-mini-audio', 'button'), attrs = attrsFrom(open[1]);
      Object.keys(attrs).forEach(function (name) { audio.setAttribute(name, attrs[name]); });
      audio.parentElement = this;
      this._queries['.mini-audio'] = audio;
    }
  }
});
Object.defineProperty(El.prototype, 'childNodes', { get: function () { return this.children; } });
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.hasAttribute = function (name) { return Object.prototype.hasOwnProperty.call(this.attrs, name); };
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.appendChild = function (child) { child.parentElement = this; this.children.push(child); return child; };
El.prototype.append = El.prototype.appendChild;
El.prototype.addEventListener = function (type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); };
El.prototype.click = function () {
  if (this.disabled || !this.connected) return;
  (this.listeners.click || []).slice().forEach(function (fn) { fn({ target: this }); }, this);
};
El.prototype.querySelector = function (selector) {
  var list = this._queries[selector];
  return Array.isArray(list) ? (list[0] || null) : (list || null);
};
El.prototype.querySelectorAll = function (selector) {
  var list = this._queries[selector];
  return Array.isArray(list) ? list : (list ? [list] : []);
};
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
    if (node.classList && node.classList.contains('screen') && !node.classList.contains('active')) return;
  }
  this.focusCount++; this.lastFocusOptions = options || null; DOC.activeElement = this;
};
// The one thing the reveal contract is read back from.
El.prototype.scrollIntoView = function (options) {
  this.revealCount++;
  REVEALS.push({ id: this.id, tag: this.tagName, options: options });
};
El.prototype.closest = function (selector) {
  if (selector === '.screen') {
    for (var node = this; node; node = node.parentElement)
      if (node.classList && node.classList.contains('screen')) return node;
    return null;
  }
  var tag = this.tagName.toLowerCase();
  if (selector && selector.indexOf(tag) !== -1) return this;
  return null;
};
El.prototype.insertAdjacentHTML = function (position, html) {
  if (position !== 'beforeend') return;
  this._html += String(html);
};
function lastReveal() { return REVEALS.length ? REVEALS[REVEALS.length - 1] : null; }
function resetReveals() { REVEALS = []; }

BODY = new El('body', 'body');
DOC = {
  body: BODY,
  activeElement: BODY,
  contains: function (el) { return !!(el && el.connected); },
  createTextNode: function (value) { return new TextNode(value); },
  createElement: function (tag) { return new El('', tag); }
};
var WIN = {
  getComputedStyle: function (el) {
    return { display: el.style.display || 'block', visibility: el.style.visibility || 'visible' };
  }
};

var SHARED_NAMES = ['ppIsInteractiveTarget', 'ppIsHiddenOrInert', 'ppCanFocus', 'ppFocusElement',
  'ppFocusActivityTarget', 'ppRevealFocusedTarget', 'ppFocusAndRevealActivityTarget',
  'ppKeepActivityFocusOr', 'ppSetActivityStatus', 'ppAnnounceTypedActivityResult',
  'ppSetActivityOptionState', 'ppAudioControlName', 'ppSetAudioControlName'];
var SHARED = (new Function('document', 'window', 'PP_INTERACTIVE_SELECTOR',
  SHARED_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + SHARED_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};'
))(DOC, WIN, 'button,input,[role="button"]');

// =========================================================================
// A. The shared reveal helper.
// =========================================================================
var screen = new El('screen'); screen.classList.add('screen'); screen.classList.add('active');
var revealTarget = new El('revealTarget', 'button'); revealTarget.parentElement = screen;

resetReveals();
eq('A1 a null element is safe and reports nothing revealed', SHARED.ppRevealFocusedTarget(null), false);
eq('A1 undefined is safe', SHARED.ppRevealFocusedTarget(undefined), false);
eq('A1 a non-element value is safe', SHARED.ppRevealFocusedTarget({}), false);
eq('A1 an element without the API is safe', SHARED.ppRevealFocusedTarget({ scrollIntoView: 1 }), false);
eq('A1 no safe-input case scrolled anything', REVEALS.length, 0);

resetReveals();
DOC.activeElement = BODY; revealTarget.focusCount = 0;
ok('A2 the combined helper focuses and reveals a valid target', SHARED.ppFocusAndRevealActivityTarget(revealTarget));
eq('A2 the target the app chose is the one that took focus', DOC.activeElement, revealTarget);
eq('A2 exactly one focus move occurs', revealTarget.focusCount, 1);
eq('A2 the focus call still prevents scrolling', revealTarget.lastFocusOptions, { preventScroll: true });
eq('A2 exactly one reveal occurs', REVEALS.length, 1);
eq('A2 the reveal is asked for on the focused element', lastReveal().id, 'revealTarget');
eq('A2 the reveal asks for the nearest block edge', lastReveal().options.block, 'nearest');
eq('A2 the reveal asks for the nearest inline edge', lastReveal().options.inline, 'nearest');
eq('A2 the reveal requests no animated behavior', lastReveal().options.behavior, undefined);
eq('A2 the reveal requests exactly the two documented options',
   Object.keys(lastReveal().options).sort(), ['block', 'inline']);

resetReveals();
var alreadyFocused = new El('alreadyFocused', 'button'); alreadyFocused.parentElement = screen;
DOC.activeElement = alreadyFocused; alreadyFocused.focusCount = 0;
ok('A3 an already-focused valid target is kept, not re-focused',
   SHARED.ppFocusAndRevealActivityTarget(alreadyFocused) && alreadyFocused.focusCount === 0);
eq('A3 keeping a target still reveals it exactly once', REVEALS.length, 1);
eq('A3 the kept target is the revealed one', lastReveal().id, 'alreadyFocused');

// Rejected targets: the same classes the shared focus boundary already rejects.
[['disabled', function (el) { el.disabled = true; }],
 ['hidden', function (el) { el.hidden = true; }],
 ['inert', function (el) { el.inert = true; }],
 ['aria-hidden', function (el) { el.setAttribute('aria-hidden', 'true'); }],
 ['display:none', function (el) { el.style.display = 'none'; }],
 ['detached', function (el) { el.connected = false; }],
 ['aria-disabled', function (el) { el.setAttribute('aria-disabled', 'true'); }]].forEach(function (pair) {
  resetReveals();
  var el = new El('rejected-' + pair[0], 'button'); el.parentElement = screen; pair[1](el);
  eq('A4 a ' + pair[0] + ' control is not revealed', SHARED.ppRevealFocusedTarget(el), false);
  eq('A4 a ' + pair[0] + ' control is neither focused nor revealed',
     [SHARED.ppFocusAndRevealActivityTarget(el), REVEALS.length], [false, 0]);
});
resetReveals();
var inactiveScreen = new El('inactiveScreen'); inactiveScreen.classList.add('screen');
var staleControl = new El('staleControl', 'button'); staleControl.parentElement = inactiveScreen;
eq('A4 a control on an inactive screen is not revealed', SHARED.ppRevealFocusedTarget(staleControl), false);
eq('A4 no stale-screen control scrolled anything', REVEALS.length, 0);

// Source contract: this is the only scrolling the app performs, and none of it is
// global, continuous, animated or timer-driven.
var REVEAL_SRC = codeOf('ppRevealFocusedTarget');
ok('A5 the helper asks for the nearest block and inline edge',
   REVEAL_SRC.indexOf('block:"nearest"') !== -1 && REVEAL_SRC.indexOf('inline:"nearest"') !== -1);
eq('A5 the helper never requests smooth behavior', countOf(REVEAL_SRC, 'smooth'), 0);
eq('A5 the helper moves no focus itself', countOf(REVEAL_SRC, '.focus('), 0);
ok('A5 the helper refuses targets the shared boundary rejects', REVEAL_SRC.indexOf('ppCanFocus(el)') !== -1);
ok('A6 the combined helper focuses before it reveals',
   codeOf('ppFocusAndRevealActivityTarget').indexOf('ppFocusActivityTarget(el)') <
   codeOf('ppFocusAndRevealActivityTarget').indexOf('ppRevealFocusedTarget(el)'));
ok('A6 every focus move still keeps preventScroll',
   codeOf('ppFocusElement').indexOf('el.focus({preventScroll:true})') !== -1);
eq('A7 scrollIntoView exists only in the shared helper', countOf(INDEX, 'scrollIntoView'),
   countOf(REVEAL_SRC, 'scrollIntoView'));
eq('A7 no global scroll listener is introduced',
   countOf(INDEX, 'addEventListener("scroll"') + countOf(INDEX, "addEventListener('scroll'") +
   countOf(INDEX, 'onscroll'), 0);
eq('A7 no VisualViewport infrastructure is introduced', countOf(INDEX, 'visualViewport'), 0);
eq('A7 no smooth scroll is requested anywhere',
   countOf(squash(INDEX), 'behavior:"smooth"') + countOf(squash(INDEX), "behavior:'smooth'") +
   countOf(squash(INDEX), 'scroll-behavior:smooth'), 0);
eq('A7 overflow is not hidden globally',
   countOf(squash(INDEX), 'html{overflow:hidden') + countOf(squash(INDEX), '*{overflow:hidden'), 0);

// =========================================================================
// B. Type It - MLG-3A-09.
// =========================================================================
var appWindow = {};
(new Function('window', readFile(ROOT + 'pp-answer.js')))(appWindow);
var ANSWER = appWindow.PP_ANSWER;
var TYPE_NAMES = ['startTypeit', 'tRender', 'tRevealLetter', 'tCheckAnswer', 'tShowDone'];
var TYPE_COMPILE = new Function('$', 'T', 'LEVELS', 'poolFor', 'gShuffle', 'show',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'ppVariantParts',
  'ppAppendUsageTo', 'G_AUDIO', 'window', 'ppSetActivityStatus',
  'ppAnnounceTypedActivityResult', 'ppFocusActivityTarget', 'ppFocusAndRevealActivityTarget',
  'ppKeepActivityFocusOr', 'ppSetAudioControlName',
  TYPE_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + TYPE_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};');

function typeHarness(card) {
  var nodes = {}, root = new El('typeit-screen');
  root.classList.add('screen'); root.classList.add('active');
  function get(id) {
    if (!nodes[id]) {
      var tag = id === 'tInput' ? 'input'
              : /^(tCheck|tHint|tNext|tAgain|tHome)$/.test(id) ? 'button'
              : id.indexOf('Title') !== -1 || id === 'tEn' ? 'h2' : 'div';
      nodes[id] = new El(id, tag); nodes[id].parentElement = root;
    }
    return nodes[id];
  }
  var T = { topicRef: null, li: 0, ti: 0, qs: [], i: 0, right: 0, almost: 0,
            hinted: 0, revealed: 0, state: 'ask' };
  var api = TYPE_COMPILE(get, T, [{ topics: [{ name: 'Topic', src: 'topic' }] }],
    function () { return [{ c: card, topic: 'Topic' }]; }, function (a) { return a.slice(); },
    function () {}, ANSWER, ANSWER.buildIndex([card]), function () { return true; },
    function (c) { return c.pl; }, function () { return null; }, function () {}, '', {},
    SHARED.ppSetActivityStatus, SHARED.ppAnnounceTypedActivityResult, SHARED.ppFocusActivityTarget,
    SHARED.ppFocusAndRevealActivityTarget, SHARED.ppKeepActivityFocusOr, SHARED.ppSetAudioControlName);
  return { T: T, $: get, api: api, card: card };
}

var TYPE_CARD = { id: 'phase3b-card', pl: 'mąka', en: 'flour', exEn: 'We need flour.' };

function typedRun(label, typed, expect) {
  var h = typeHarness(TYPE_CARD);
  h.api.startTypeit(0, 0);
  resetReveals();
  h.$('tInput').value = typed;
  h.api.tCheckAnswer();
  eq('B1 ' + label + ' still focuses the existing #tNext control', DOC.activeElement, h.$('tNext'));
  eq('B1 ' + label + ' enables Next before focusing it', h.$('tNext').disabled, false);
  eq('B1 ' + label + ' reveals exactly one control', REVEALS.length, 1);
  eq('B1 ' + label + ' reveals the focused Next control', lastReveal().id, 'tNext');
  eq('B1 ' + label + ' reveals with the shared nearest contract',
     [lastReveal().options.block, lastReveal().options.inline], ['nearest', 'nearest']);
  eq('B1 ' + label + ' keeps preventScroll on the focus move',
     h.$('tNext').lastFocusOptions, { preventScroll: true });
  eq('B1 ' + label + ' preserves its verdict scoring', [h.T.right, h.T.almost], expect.score);
  eq('B1 ' + label + ' preserves its announcement', h.$('tStatus').textContent, expect.status);
  ok('B1 ' + label + ' preserves its visible verdict class',
     h.$('tVerdict').className.indexOf('v-' + expect.verdict) !== -1);
  ok('B1 ' + label + ' preserves its visible verdict head',
     h.$('tVerdict').innerHTML.indexOf(expect.head) !== -1);
  // A settled question must not move or scroll again, however many times Check fires.
  var revealsAfterFirst = REVEALS.length, focusAfterFirst = h.$('tNext').focusCount;
  var stateAfterFirst = JSON.stringify([h.T.right, h.T.almost, h.T.hinted, h.T.state]);
  h.api.tCheckAnswer(); h.api.tCheckAnswer();
  eq('B2 ' + label + ' repeated submission scrolls nothing further', REVEALS.length, revealsAfterFirst);
  eq('B2 ' + label + ' repeated submission moves no focus again', h.$('tNext').focusCount, focusAfterFirst);
  eq('B2 ' + label + ' repeated submission changes no state',
     JSON.stringify([h.T.right, h.T.almost, h.T.hinted, h.T.state]), stateAfterFirst);
  return h;
}

typedRun('a right answer', 'mąka',
  { score: [1, 0], verdict: 'right', head: 'Dobrze!', status: 'Correct. The answer is mąka. Next is ready.' });
typedRun('an almost answer', 'maka',
  { score: [0, 1], verdict: 'almost', head: 'Almost - watch',
    status: 'Almost correct. Check the Polish spelling: mąka. Next is ready.' });
typedRun('a wrong answer', 'ziemniak',
  { score: [0, 0], verdict: 'wrong', head: 'Not this time',
    status: 'Incorrect. The answer is mąka. Next is ready.' });

var blank = typeHarness(TYPE_CARD); blank.api.startTypeit(0, 0);
resetReveals();
DOC.activeElement = blank.$('tInput');
blank.$('tInput').value = '   ';
blank.api.tCheckAnswer();
eq('B3 an empty answer still returns focus to the input', DOC.activeElement, blank.$('tInput'));
eq('B3 an empty answer leaves Next closed', blank.$('tNext').disabled, true);
eq('B3 an empty answer reveals nothing', REVEALS.length, 0);
eq('B3 an empty answer keeps its exact wording',
   blank.$('tStatus').textContent, 'Type the Polish answer first.');
eq('B3 an empty answer does not settle the question', blank.T.state, 'ask');

var hinted = typeHarness(TYPE_CARD); hinted.api.startTypeit(0, 0);
resetReveals();
DOC.activeElement = hinted.$('tHint');
hinted.api.tRevealLetter();
eq('B4 revealing a letter reveals no control', REVEALS.length, 0);
eq('B4 revealing a letter keeps its still-valid trigger', DOC.activeElement, hinted.$('tHint'));
ok('B4 the hint line still shows the canonical prefix', /^Starts with:/.test(hinted.$('tHintLine').textContent));
hinted.$('tInput').value = 'mąka'; hinted.api.tCheckAnswer();
eq('B4 a hinted answer keeps its own verdict and hint tally',
   [hinted.T.right, hinted.T.hinted], [1, 1]);
eq('B4 a hinted answer reveals the focused Next once', [REVEALS.length, lastReveal().id], [1, 'tNext']);

var advance = typeHarness(TYPE_CARD); advance.api.startTypeit(0, 0);
advance.$('tInput').value = 'mąka'; advance.api.tCheckAnswer();
resetReveals();
advance.T.i++; advance.api.tRender();
eq('B5 advancing to the completion screen focuses its heading', DOC.activeElement, advance.$('tDoneTitle'));
eq('B5 advancing reveals nothing new', REVEALS.length, 0);
eq('B5 completion arithmetic is unchanged',
   [advance.$('tScoreN').textContent, advance.$('tAlmostN').textContent, advance.$('tMissN').textContent],
   ['1', '0', '0']);
resetReveals();
advance.api.startTypeit(0, 0);
eq('B5 restarting focuses the prompt, not a Next control', DOC.activeElement, advance.$('tEn'));
eq('B5 restarting reveals nothing', REVEALS.length, 0);
eq('B5 restarting resets every counter',
   [advance.T.i, advance.T.right, advance.T.almost], [0, 0, 0]);

var TCHECK = codeOf('tCheckAnswer');
ok('B6 Type It enables Next before the focus/reveal move',
   TCHECK.indexOf('$("tNext").disabled=false') < TCHECK.indexOf('ppFocusAndRevealActivityTarget'));
eq('B6 Type It performs exactly one focus-and-reveal move',
   countOf(TCHECK, 'ppFocusAndRevealActivityTarget($("tNext"))'), 1);
ok('B6 Type It keeps its guarded fallback to the plain focus adapter',
   TCHECK.indexOf('ppFocusActivityTarget($("tNext"))') !== -1);
ok('B6 the blank-answer path still keeps its trigger and never reveals',
   TCHECK.indexOf('ppKeepActivityFocusOr($("tInput"),[$("tInput"),$("tCheck")])') !== -1);
ok('B6 the settled-question guard is unchanged', TCHECK.indexOf('if(T.state!=="ask")return;') !== -1);
['tRender', 'tRevealLetter', 'tShowDone', 'startTypeit'].forEach(function (name) {
  eq('B7 ' + name + ' gains no reveal call',
     countOf(codeOf(name), 'ppRevealFocusedTarget') + countOf(codeOf(name), 'ppFocusAndRevealActivityTarget'), 0);
});

// =========================================================================
// C. Mixed Quiz - the typed format only.
// =========================================================================
var ROUND_NAMES = ['rCheckAnswer', 'rPickOption', 'rRecord'];
var ROUND_COMPILE = new Function('$', 'R', 'document', 'PP_ANSWER', 'PP_TYPED_INDEX',
  'rSetStatus', 'rSyncNextLabel', 'rAnnounceCorrect', 'rAnnounceWrong', 'rFocusNextOption',
  'rBuildOptions', 'ppHasMainAudio', 'ppMainAudioText', 'ppVariantParts', 'ppAppendUsageTo',
  'G_AUDIO', 'ppSetActivityStatus', 'ppAnnounceTypedActivityResult', 'ppSetActivityOptionState',
  'ppFocusActivityTarget', 'ppFocusAndRevealActivityTarget', 'ppKeepActivityFocusOr',
  'ppSetAudioControlName',
  ROUND_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + ROUND_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};');

function roundHarness(question) {
  var nodes = {}, root = new El('round-screen');
  root.classList.add('screen'); root.classList.add('active');
  function get(id) {
    if (!nodes[id]) {
      var tag = id === 'rInput' ? 'input'
              : /^(rCheck|rHint|rNext|rPlay)$/.test(id) ? 'button' : 'div';
      nodes[id] = new El(id, tag); nodes[id].parentElement = root;
    }
    return nodes[id];
  }
  var R = { li: 0, ti: 0, qs: [question], i: 0, state: 'ask', attempted: false,
            revealed: 0, hinted: 0 };
  var calls = { status: [], nextLabel: 0, correct: [], wrong: [], nextOption: 0 };
  var api = ROUND_COMPILE(get, R, DOC, ANSWER, ANSWER.buildIndex([question.c]),
    function (parts) { calls.status.push(parts); return SHARED.ppSetActivityStatus(get('rStatus'), parts); },
    function () { calls.nextLabel++; },
    function (pl) { calls.correct.push(pl); },
    function (label) { calls.wrong.push(label); },
    function () { calls.nextOption++; },
    function () { return []; },
    function () { return true; }, function (c) { return c.pl; }, function () { return null; },
    function () {}, '', SHARED.ppSetActivityStatus, SHARED.ppAnnounceTypedActivityResult,
    SHARED.ppSetActivityOptionState, SHARED.ppFocusActivityTarget,
    SHARED.ppFocusAndRevealActivityTarget, SHARED.ppKeepActivityFocusOr, SHARED.ppSetAudioControlName);
  return { R: R, $: get, api: api, calls: calls };
}

var MIX_CARD = { id: 'phase3b-mixed', pl: 'chleb', en: 'bread' };
[['a right typed answer', 'chleb', 'right'],
 ['an almost typed answer', 'chleb ', 'right'],
 ['a wrong typed answer', 'masło', 'wrong']].forEach(function (row) {
  var h = roundHarness({ c: MIX_CARD, fmt: 'type', options: [], result: null });
  resetReveals();
  h.$('rInput').value = row[1];
  h.api.rCheckAnswer();
  eq('C1 ' + row[0] + ' still focuses the existing #rNext control', DOC.activeElement, h.$('rNext'));
  eq('C1 ' + row[0] + ' enables Next before focusing it', h.$('rNext').disabled, false);
  eq('C1 ' + row[0] + ' reveals the focused Next exactly once',
     [REVEALS.length, lastReveal().id], [1, 'rNext']);
  eq('C1 ' + row[0] + ' reveals with the shared nearest contract',
     [lastReveal().options.block, lastReveal().options.inline], ['nearest', 'nearest']);
  eq('C1 ' + row[0] + ' keeps preventScroll on the focus move',
     h.$('rNext').lastFocusOptions, { preventScroll: true });
  eq('C1 ' + row[0] + ' records exactly one result on the question', h.R.qs[0].result, row[2] === 'right' ? 'right' : 'miss');
  eq('C1 ' + row[0] + ' re-asks the Next wording exactly once', h.calls.nextLabel, 1);
  var before = [REVEALS.length, h.$('rNext').focusCount, JSON.stringify(h.R.qs.length)];
  h.api.rCheckAnswer();
  eq('C1 ' + row[0] + ' repeated submission changes nothing',
     [REVEALS.length, h.$('rNext').focusCount, JSON.stringify(h.R.qs.length)], before);
});

// The two answer-button formats settle on a control that is already on screen; the
// typed fix must not have leaked into them.
['mc', 'listen'].forEach(function (fmt) {
  var right = { label: 'bread', correct: true, item: { c: MIX_CARD } };
  var q = { c: MIX_CARD, fmt: fmt, options: [right], result: null };
  var h = roundHarness(q);
  var box = h.$('rOpts'), btn = new El(fmt + '-opt', 'button');
  btn.parentElement = box.parentElement;
  box._queries['.opt'] = [btn];
  resetReveals();
  h.api.rPickOption(btn, right, q, box);
  eq('D1 the ' + fmt + ' format still focuses its existing Next control', DOC.activeElement, h.$('rNext'));
  eq('D1 the ' + fmt + ' format gains no typed-flow scrolling', REVEALS.length, 0);
  eq('D1 the ' + fmt + ' format still scores unchanged', q.result, 'right');
  eq('D1 the ' + fmt + ' format still announces the correct answer', h.calls.correct, [MIX_CARD.pl]);
});

var RCHECK = codeOf('rCheckAnswer');
ok('D2 the Mixed typed path enables Next before the focus/reveal move',
   RCHECK.indexOf('$("rNext").disabled=false') < RCHECK.indexOf('ppFocusAndRevealActivityTarget'));
eq('D2 the Mixed typed path performs exactly one focus-and-reveal move',
   countOf(RCHECK, 'ppFocusAndRevealActivityTarget($("rNext"))'), 1);
ok('D2 the Mixed typed path keeps its guarded fallback',
   RCHECK.indexOf('ppFocusActivityTarget($("rNext"))') !== -1);
ok('D2 the Mixed typed verdict still banks through rRecord',
   RCHECK.indexOf('rRecord(q,verdict==="wrong"?"miss":verdict)') !== -1);
['rPickOption', 'rRender', 'rFocusNextOption', 'rShowDone', 'rPlayCurrent',
 'lPlayCurrent', 'lRender', 'gRenderTeach', 'gDrillAdvance'].forEach(function (name) {
  eq('D3 ' + name + ' gains no reveal call',
     countOf(codeOf(name), 'ppRevealFocusedTarget') + countOf(codeOf(name), 'ppFocusAndRevealActivityTarget'), 0);
});
eq('D3 exactly two typed activity paths reveal a focused Next',
   countOf(squash(stripComments(INDEX)), 'ppFocusAndRevealActivityTarget($("tNext"))') +
   countOf(squash(stripComments(INDEX)), 'ppFocusAndRevealActivityTarget($("rNext"))'), 2);

// =========================================================================
// E. Conversations - MLG-3A-10.
// =========================================================================
var convoWindow = { PP_LEVELS: [] };
(new Function('window', SCENARIO_DATA))(convoWindow);
var SCENARIO_LEVEL = convoWindow.PP_LEVELS[0], SCENARIO_TOPICS = SCENARIO_LEVEL.topics;

// A thread element that tells a reset render apart from an append, and keeps the
// identity of every bubble it has already rendered.
var THREAD_REGISTRY = {};
function BubbleEl(id, openTag) {
  El.call(this, id, 'div');
  var attrs = attrsFrom(openTag);
  Object.keys(attrs).forEach(function (name) { this.setAttribute(name, attrs[name]); }, this);
  (attrs['class'] || '').split(/\s+/).filter(Boolean).forEach(function (name) { this.classList.add(name); }, this);
  this.renderCount = 0; this.audio = null;
}
BubbleEl.prototype = Object.create(El.prototype);
BubbleEl.prototype.constructor = BubbleEl;
Object.defineProperty(BubbleEl.prototype, 'innerHTML', {
  get: function () { return this._inner || ''; },
  set: function (value) {
    this.renderCount++;
    if (this.audio) this.audio.connected = false;
    this._inner = String(value);
    this.audio = null;
    var audioOpen = this._inner.match(/<button\b([^>]*class="mini-audio"[^>]*)>/);
    if (audioOpen) {
      var audio = new El('', 'button'), attrs = attrsFrom(audioOpen[1]);
      Object.keys(attrs).forEach(function (name) { audio.setAttribute(name, attrs[name]); });
      audio.classList.add('mini-audio'); audio.parentElement = this;
      this.audio = audio;
    }
    var heading = this._inner.match(/<h2\b([^>]*)>/);
    if (heading) {
      var hAttrs = attrsFrom(heading[1]), h2 = new El(hAttrs.id || '', 'h2');
      Object.keys(hAttrs).forEach(function (name) { h2.setAttribute(name, hAttrs[name]); });
      h2.parentElement = this;
      if (h2.id) THREAD_REGISTRY[h2.id] = h2;
    }
    var speaker = this._inner.match(/<div class="bubble-speaker" id="(cSpeaker\d+)">/);
    if (speaker) {
      var sp = new El(speaker[1], 'div'); sp.parentElement = this;
      THREAD_REGISTRY[speaker[1]] = sp;
    }
  }
});
function ThreadEl() {
  El.call(this, 'cThread', 'div');
  this.bubbles = []; this.resetCount = 0; this.appendCount = 0; this.intro = '';
}
ThreadEl.prototype = Object.create(El.prototype);
ThreadEl.prototype.constructor = ThreadEl;
ThreadEl.prototype._parse = function (html) {
  var re = /<div class="bubble [a-z]+" id="(cBubble\d+)"[^>]*>/g, marks = [], m;
  while ((m = re.exec(html)) !== null) marks.push({ at: m.index, id: m[1], open: m[0] });
  marks.forEach(function (mark, i) {
    var end = i + 1 < marks.length ? marks[i + 1].at : html.length;
    var bubble = new BubbleEl(mark.id, mark.open);
    bubble.parentElement = this;
    bubble.innerHTML = html.slice(mark.at + mark.open.length, end);
    this.bubbles.push(bubble);
    THREAD_REGISTRY[mark.id] = bubble;
  }, this);
};
Object.defineProperty(ThreadEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (value) {
    this.resetCount++;
    this.bubbles.forEach(function (b) { b.connected = false; if (b.audio) b.audio.connected = false; });
    this.bubbles = []; this._html = String(value);
    this.intro = this._html.slice(0, this._html.indexOf('<div class="bubble ') === -1
      ? this._html.length : this._html.indexOf('<div class="bubble '));
    this._parse(this._html);
  }
});
ThreadEl.prototype.insertAdjacentHTML = function (position, html) {
  if (position !== 'beforeend') return;
  this.appendCount++; this._html += String(html); this._parse(String(html));
};
ThreadEl.prototype.querySelectorAll = function (selector) {
  if (selector !== '.mini-audio[data-mi]') return [];
  return this.bubbles.filter(function (b) { return !!b.audio; }).map(function (b) { return b.audio; });
};
ThreadEl.prototype.querySelector = function (selector) {
  var m = selector.match(/^\.mini-audio\[data-mi="(\d+)"\]$/);
  if (!m) return null;
  return this.querySelectorAll('.mini-audio[data-mi]').filter(function (b) {
    return b.getAttribute('data-mi') === m[1];
  })[0] || null;
};

// #cReply is rebuilt wholesale every turn, exactly as it ships.
function ReplyEl(id) { El.call(this, id, 'div'); }
ReplyEl.prototype = Object.create(El.prototype);
ReplyEl.prototype.constructor = ReplyEl;
Object.defineProperty(ReplyEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (value) {
    (this._queries['.reply-opt'] || []).forEach(function (b) { b.connected = false; });
    this._html = String(value); this._queries = {};
    var buttons = [], re = /<button\b([^>]*)>/g, m;
    while ((m = re.exec(this._html)) !== null) {
      var attrs = attrsFrom(m[1]), b = new El(attrs.id || '', 'button');
      Object.keys(attrs).forEach(function (name) { b.setAttribute(name, attrs[name]); });
      (attrs['class'] || '').split(/\s+/).filter(Boolean).forEach(function (name) { b.classList.add(name); });
      b.parentElement = this; buttons.push(b);
      if (b.id) THREAD_REGISTRY[b.id] = b;
    }
    this._queries['.reply-opt'] = buttons.filter(function (b) { return b.classList.contains('reply-opt'); });
    var hRe = /<h2\b([^>]*)>/g;
    while ((m = hRe.exec(this._html)) !== null) {
      var hAttrs = attrsFrom(m[1]), h2 = new El(hAttrs.id || '', 'h2');
      Object.keys(hAttrs).forEach(function (name) { h2.setAttribute(name, hAttrs[name]); });
      h2.parentElement = this;
      if (h2.id) THREAD_REGISTRY[h2.id] = h2;
    }
    var dRe = /<div\b([^>]*)>/g;
    while ((m = dRe.exec(this._html)) !== null) {
      var dAttrs = attrsFrom(m[1]);
      if (!dAttrs.id) continue;
      var div = new El(dAttrs.id, 'div');
      Object.keys(dAttrs).forEach(function (name) { div.setAttribute(name, dAttrs[name]); });
      (dAttrs['class'] || '').split(/\s+/).filter(Boolean).forEach(function (name) { div.classList.add(name); });
      div.parentElement = this; THREAD_REGISTRY[div.id] = div;
    }
    this._queries['.cdone-recap li b'] = [];
  }
});

var CONVO_NAMES = ['cComputeDist', 'startConvo', 'cSetStatus', 'cBubbleSpeakerId',
  'cBubbleInnerHTML', 'cBubbleHTML', 'cThreadIntroHTML', 'cThreadBubblesHTML',
  'cNameThreadAudio', 'cRenderThread', 'cSettleThreadBubble', 'cAdvanceThread',
  'cProgress', 'cRenderNode', 'cRenderOptions', 'cChooseOption', 'cScopeRecapLanguage',
  'cShowDone'];
var CONVO_COMPILE = new Function('$', 'document', 'window', 'C', 'C_CHECK', 'G_AUDIO',
  'LEVELS', 'show', 'modeLabel', 'ppSetActivityStatus', 'ppFocusActivityTarget',
  'ppRevealFocusedTarget', 'ppFocusAndRevealActivityTarget', 'ppSetAudioControlName',
  CONVO_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + CONVO_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};');

function convoHarness() {
  THREAD_REGISTRY = {};
  var thread = new ThreadEl(), reply = new ReplyEl('cReply');
  var root = new El('convo-screen'); root.classList.add('screen'); root.classList.add('active');
  thread.parentElement = root; reply.parentElement = root;
  THREAD_REGISTRY.cThread = thread; THREAD_REGISTRY.cReply = reply;
  ['cTitle', 'cLevel', 'cFill', 'cCount', 'cStatus', 'cChallenge'].forEach(function (id) {
    var el = new El(id, id === 'cChallenge' ? 'button' : 'div');
    el.parentElement = root; THREAD_REGISTRY[id] = el;
  });
  function get(id) { return THREAD_REGISTRY[id] || null; }
  var doc = {
    body: BODY,
    activeElement: DOC.activeElement,
    contains: function (el) { return !!(el && el.connected); },
    createElement: function (tag) { return new El('', tag); },
    createTextNode: function (v) { return new TextNode(v); },
    getElementById: get
  };
  // The shared helpers and the conversation code must see one activeElement.
  Object.defineProperty(doc, 'activeElement', {
    get: function () { return DOC.activeElement; },
    set: function (v) { DOC.activeElement = v; }
  });
  var C = { topic: null, li: 0, tpi: 0, node: null, transcript: [], rendered: 0, dist: {},
            maxDist: 1, challenge: false, curOptions: null, transitioning: false };
  var shown = [];
  var api = CONVO_COMPILE(get, doc, {}, C, '<svg></svg>', '<svg data-audio></svg>',
    [SCENARIO_LEVEL], function (s, d) { shown.push([s, !!d]); },
    function (lv) { return lv.level === 'Scenarios' ? 'Conversations' : lv.level; },
    SHARED.ppSetActivityStatus, SHARED.ppFocusActivityTarget, SHARED.ppRevealFocusedTarget,
    SHARED.ppFocusAndRevealActivityTarget, SHARED.ppSetAudioControlName);
  return { C: C, $: get, api: api, thread: thread, reply: reply, shown: shown };
}

var convo = convoHarness();
resetReveals();
convo.api.startConvo(0, 0);
eq('E1 opening a conversation uses the clean reset path',
   [convo.thread.resetCount, convo.thread.appendCount], [1, 0]);
eq('E1 opening renders exactly the transcript it has', convo.thread.bubbles.length, convo.C.transcript.length);
eq('E1 opening records how much of the transcript the page holds',
   convo.C.rendered, convo.C.transcript.length);
eq('E1 opening focuses the stable scene heading', DOC.activeElement.id, 'cSceneHeading');
ok('E1 opening reveals the reply block and finishes on the focused scene',
   REVEALS.length === 2 && REVEALS[0].id === 'cReply' && REVEALS[1].id === 'cSceneHeading');
eq('E1 the reveals use the shared nearest contract',
   REVEALS.map(function (r) { return [r.options.block, r.options.inline].join('/'); }),
   ['nearest/nearest', 'nearest/nearest']);
eq('E1 the scene card is rendered once', countOf(convo.thread.innerHTML, 'class="scene-card"'), 1);

// Three turns: the measurement the register asked for.
var turnLog = [];
for (var turn = 0; turn < 3 && convo.C.curOptions; turn++) {
  var beforeBubbles = convo.thread.bubbles.length;
  var beforeIdentity = convo.thread.bubbles.slice();
  var beforeRenders = convo.thread.bubbles.map(function (b) { return b.renderCount; });
  var beforeReset = convo.thread.resetCount, beforeAppend = convo.thread.appendCount;
  var beforeTranscript = convo.C.transcript.length;
  resetReveals();
  convo.reply.querySelectorAll('.reply-opt')[0].click();
  var label = 'turn ' + (turn + 1);
  eq('E2 ' + label + ' does not replace the complete thread', convo.thread.resetCount, beforeReset);
  eq('E2 ' + label + ' appends exactly once', convo.thread.appendCount, beforeAppend + 1);
  eq('E2 ' + label + ' adds the learner reply and the new scene', convo.C.transcript.length, beforeTranscript + 2);
  eq('E2 ' + label + ' adds exactly as many bubbles as transcript entries',
     convo.thread.bubbles.length, convo.C.transcript.length);
  ok('E2 ' + label + ' preserves every earlier bubble node',
     beforeIdentity.every(function (b, i) { return convo.thread.bubbles[i] === b && b.connected; }));
  eq('E2 ' + label + ' leaves the page holding the whole transcript',
     convo.C.rendered, convo.C.transcript.length);
  eq('E2 ' + label + ' exposes exactly one current scene heading',
     convo.thread.bubbles.filter(function (b) {
       return b.getAttribute('aria-labelledby') === 'cSceneHeading';
     }).length, 1);
  eq('E2 ' + label + ' re-renders exactly one previously rendered bubble',
     beforeRenders.filter(function (n, i) { return convo.thread.bubbles[i].renderCount !== n; }).length, 1);
  eq('E2 ' + label + ' re-renders the bubble that stopped being the current scene',
     convo.thread.bubbles[beforeBubbles - 1].getAttribute('aria-labelledby'), 'cSpeaker' + (beforeBubbles - 1));
  eq('E2 ' + label + ' produces no duplicate bubble ids',
     convo.thread.bubbles.map(function (b) { return b.id; }).length,
     convo.thread.bubbles.map(function (b) { return b.id; }).filter(function (id, i, all) {
       return all.indexOf(id) === i;
     }).length);
  ok('E2 ' + label + ' brings the new turn and its replies into view',
     REVEALS.length >= 1 &&
     REVEALS.some(function (r) { return r.id === 'cReply' || r.id === 'cDoneTitle'; }));
  ok('E2 ' + label + ' finishes on the focused element',
     lastReveal().id === DOC.activeElement.id);
  eq('E2 ' + label + ' requests no animated scroll',
     REVEALS.filter(function (r) { return r.options && r.options.behavior; }).length, 0);
  turnLog.push({ turn: turn + 1, bubbles: convo.thread.bubbles.length,
                 resets: convo.thread.resetCount, appends: convo.thread.appendCount,
                 active: DOC.activeElement.id });
}
eq('E2 three turns ran on a single reset render', convo.thread.resetCount, 1);
eq('E2 three turns appended three times', convo.thread.appendCount, 3);

// Every settled scene must read exactly as a full reset render would have written it.
var settledSnapshot = convo.thread.bubbles.map(function (b) {
  return [b.id, b.getAttribute('aria-labelledby'), b.getAttribute('class')].join('|');
});
resetReveals();
convo.api.cRenderThread();
eq('E3 an explicit reset render rebuilds the thread', convo.thread.resetCount, 2);
eq('E3 the reset render reproduces the appended structure exactly',
   convo.thread.bubbles.map(function (b) {
     return [b.id, b.getAttribute('aria-labelledby'), b.getAttribute('class')].join('|');
   }), settledSnapshot);
eq('E3 the reset render exposes one current scene heading',
   countOf(convo.thread.innerHTML, 'id="cSceneHeading"'), 1);
eq('E3 the reset render reveals nothing by itself', REVEALS.length, 0);

// Playing a whole conversation still terminates on the authored ending.
var ending = convoHarness();
ending.api.startConvo(0, 0);
var guard = 200;
while (ending.C.curOptions && guard-- > 0) ending.reply.querySelectorAll('.reply-opt')[0].click();
ok('E4 a real route still terminates', guard > 0 && ending.C.curOptions === null);
eq('E4 the ending still focuses its completion heading', DOC.activeElement.id, 'cDoneTitle');
eq('E4 the ending reveals the focused completion heading', lastReveal().id, 'cDoneTitle');
ok('E4 the ending card still renders', ending.reply.innerHTML.indexOf('cdone') !== -1);
eq('E4 the ending never rebuilt the thread more than once', ending.thread.resetCount, 1);
var endingBubbles = ending.thread.bubbles.length;
eq('E4 the ending keeps the whole conversation in the page', endingBubbles, ending.C.transcript.length);
resetReveals();
ending.$('cAgain').click();
eq('E5 restarting uses the clean reset path', ending.thread.resetCount, 2);
eq('E5 restarting clears every earlier turn', ending.thread.bubbles.length, 1);
eq('E5 restarting returns to the authored start', ending.C.node, ending.C.topic.start);
eq('E5 restarting refocuses the first scene', DOC.activeElement.id, 'cSceneHeading');

// Structural coverage over the frozen graph: every scene, route and ending survives.
var scenes = 0, routes = 0, endings = 0;
SCENARIO_TOPICS.forEach(function (topic) {
  Object.keys(topic.scenes).forEach(function (id) {
    scenes++;
    var scene = topic.scenes[id];
    if (scene.end) endings++;
    routes += (scene.options || []).length;
  });
});
eq('E6 the frozen conversation graph is unchanged', [scenes, routes, endings], [102, 194, 8]);
SCENARIO_TOPICS.forEach(function (topic) {
  var h = convoHarness();
  h.C.topic = topic; h.C.li = 0; h.C.tpi = SCENARIO_TOPICS.indexOf(topic);
  h.C.node = topic.start; h.C.transcript = []; h.C.rendered = 0;
  h.C.dist = h.api.cComputeDist(topic);
  h.C.maxDist = Math.max(1, Math.max.apply(null, Object.keys(h.C.dist).map(function (k) { return h.C.dist[k]; })));
  h.api.cRenderNode(true);
  var reached = 0, hop = 300;
  while (h.C.curOptions && hop-- > 0) { h.reply.querySelectorAll('.reply-opt')[0].click(); reached++; }
  ok('E6 ' + topic.id + ' still reaches an ending', hop > 0 && h.C.curOptions === null);
  eq('E6 ' + topic.id + ' rendered every turn exactly once',
     h.thread.bubbles.length, h.C.transcript.length);
  eq('E6 ' + topic.id + ' rebuilt the thread exactly once', h.thread.resetCount, 1);
  eq('E6 ' + topic.id + ' appended once per advancement', h.thread.appendCount, reached);
});

// Source contract for the thread renderer.
var THREAD_SQUASHED = squash(stripComments(INDEX));
eq('E7 the inert thread auto-scroll is gone', countOf(THREAD_SQUASHED, 'scrollTop='), 0);
eq('E7 no element scroll offset is read or written anywhere',
   countOf(THREAD_SQUASHED, '.scrollTop') + countOf(THREAD_SQUASHED, '.scrollHeight'), 0);
eq('E8 ordinary advancement no longer replaces the whole thread',
   countOf(codeOf('cRenderNode'), 'cRenderThread('), 0);
ok('E8 ordinary advancement runs the append path', codeOf('cRenderNode').indexOf('cAdvanceThread()') !== -1);
ok('E8 the append path writes with insertAdjacentHTML, not innerHTML',
   codeOf('cAdvanceThread').indexOf('insertAdjacentHTML("beforeend"') !== -1 &&
   countOf(codeOf('cAdvanceThread'), 'innerHTML') === 0);
ok('E8 the append path falls back to the reset render out of step',
   codeOf('cAdvanceThread').indexOf('cRenderThread();return"reset"') !== -1);
ok('E8 the reset render is still what Challenge mode and restart use',
   codeOf('startConvo').indexOf('C.rendered=0') !== -1 &&
   squash(stripComments(INDEX)).indexOf('C.challenge=!C.challenge;cSyncChallengeControl();if(C.topic){cRenderThread();') !== -1);
ok('E9 the reply block and the new scene are both revealed',
   codeOf('cRenderNode').indexOf('ppRevealFocusedTarget($("cReply"))') !== -1 &&
   codeOf('cRenderNode').indexOf('ppRevealFocusedTarget($("cSceneHeading"))') !== -1);
ok('E9 the focused scene is revealed last',
   codeOf('cRenderNode').indexOf('ppRevealFocusedTarget($("cReply"))') <
   codeOf('cRenderNode').indexOf('ppFocusActivityTarget($("cSceneHeading"))') &&
   codeOf('cRenderNode').indexOf('ppFocusActivityTarget($("cSceneHeading"))') <
   codeOf('cRenderNode').indexOf('ppRevealFocusedTarget($("cSceneHeading"))'));
ok('E9 no nested conversation scroll region is introduced', (function () {
  var m = INDEX.match(/\.thread\s*\{([^}]*)\}/);
  if (!m) return false;
  var body = squash(m[1]);
  return body.indexOf('height:') === -1 && body.indexOf('max-height') === -1 &&
         body.indexOf('overscroll') === -1;
})());
eq('E9 the conversation screen gains no second scroll container',
   countOf(squash(INDEX), '#cThread{'), 0);

// =========================================================================
// F. Screen scroll restoration - MLG-3A-13.
// =========================================================================
var ROUTE_START = INDEX.indexOf('var ppScreenReturnTargets = new Map();');
var ROUTE_END = INDEX.indexOf('function showScreen(', ROUTE_START);
if (ROUTE_START === -1 || ROUTE_END === -1) throw new Error('shipping routing helper block not found');
var ROUTE_BLOCK = INDEX.slice(ROUTE_START, ROUTE_END);
var ROUTE_FACTORY = Function('document', 'window', 'lookup',
  'var $ = lookup;\n' + ROUTE_BLOCK + '\n' + extractFunction(INDEX, 'showScreen') +
  '\nreturn {showScreen:showScreen, offsets:ppScreenScrollOffsets,' +
  'remember:ppRememberScreenScroll, apply:ppApplyScreenScroll, currentY:ppCurrentScrollY,' +
  'manual:ppUseManualScrollRestoration, targets:ppScreenReturnTargets,' +
  'rememberInvoker:ppRememberScreenInvoker, openOverlay:ppOpenSharedOverlay,' +
  'closeOverlay:ppCloseSharedOverlay, token:function(){return ppScrollRestoreToken;}};');

function routeHarness(options) {
  options = options || {};
  var screens = {}, frames = [], scrolls = [];
  // Parent links only, never child arrays: the assertions below compare elements by
  // value, so the fixture must stay acyclic.
  ['home', 'study', 'privacy', 'about'].forEach(function (id) {
    var s = new El(id, 'section'); s.classList.add('screen');
    var heading = new El(id + 'Heading', 'h1'); heading.parentElement = s;
    s._queries.h1 = heading; s.heading = heading;
    screens[id] = s;
  });
  screens.home.classList.add('active');
  var shell = new El('appShell');
  Object.keys(screens).forEach(function (id) { screens[id].parentElement = shell; });
  var overlay = new El('matureGate', 'dialog');
  overlay.showModal = function () { this.open = true; };
  overlay.close = function () { this.open = false; };
  var overlayAction = new El('matureCancel', 'button'); overlayAction.parentElement = overlay;
  var footer = new El('footer', 'footer');
  var doc = {
    body: BODY,
    contains: function (el) { return !!(el && el.connected); },
    querySelector: function (selector) {
      if (selector === '.screen.active') {
        var keys = Object.keys(screens);
        for (var i = 0; i < keys.length; i++)
          if (screens[keys[i]].classList.contains('active')) return screens[keys[i]];
        return null;
      }
      return selector === 'footer' ? footer : null;
    },
    querySelectorAll: function (selector) {
      return selector === '.screen' ? Object.keys(screens).map(function (k) { return screens[k]; }) : [];
    },
    createElement: function (tag) { return new El('', tag); }
  };
  Object.defineProperty(doc, 'activeElement', {
    get: function () { return DOC.activeElement; },
    set: function (v) { DOC.activeElement = v; }
  });
  var win = {
    PP_A2HS: null,
    scrollY: 0,
    getComputedStyle: WIN.getComputedStyle,
    scrollTo: function (x, y) { this.scrollY = y; scrolls.push(y); },
    requestAnimationFrame: options.noRaf ? undefined : function (fn) { frames.push(fn); return frames.length; },
    history: options.noRestoration ? {} : { scrollRestoration: 'auto' }
  };
  if (options.throwOnRestoration) {
    Object.defineProperty(win.history, 'scrollRestoration', {
      get: function () { return 'auto'; },
      set: function () { throw new Error('locked'); }
    });
  }
  var byId = { appShell: shell, matureGate: overlay, matureCancel: overlayAction };
  Object.keys(screens).forEach(function (id) { byId[id] = screens[id]; });
  var api = ROUTE_FACTORY(doc, win, function (id) { return byId[id] || null; });
  return { api: api, win: win, screens: screens, frames: frames, scrolls: scrolls,
           overlay: overlay, overlayAction: overlayAction, shell: shell,
           runFrames: function () { var q = frames.splice(0, frames.length); q.forEach(function (fn) { fn(); }); } };
}

var route = routeHarness();
eq('F1 explicit manual scroll restoration is applied when supported', route.api.manual(), true);
eq('F1 the browser no longer restores screen offsets itself', route.win.history.scrollRestoration, 'manual');
eq('F2 an engine without scrollRestoration is safe', routeHarness({ noRestoration: true }).api.manual(), false);
eq('F2 an engine that refuses the assignment is safe', routeHarness({ throwOnRestoration: true }).api.manual(), false);
ok('F2 the app sets the property once, at routing initialization',
   INDEX.indexOf('ppUseManualScrollRestoration();') !== -1 &&
   INDEX.indexOf('ppUseManualScrollRestoration();') < INDEX.indexOf('window.addEventListener("popstate"'));
eq('F2 scrollRestoration is written in exactly one place',
   countOf(squash(stripComments(INDEX)), 'scrollRestoration="manual"'), 1);

// The Home topic-list use case, end to end.
var homeTile = new El('homeTile', 'button');
homeTile.parentElement = route.screens.home;
route.win.scrollY = 1200;
DOC.activeElement = homeTile;
route.api.rememberInvoker('study');
route.api.showScreen('study');
eq('F3 leaving Home records exactly where the list was', route.api.offsets.get('home'), 1200);
eq('F3 the destination starts at the top', route.win.scrollY, 0);
eq('F3 the forward transition scrolls exactly once', route.scrolls.length, 1);
eq('F3 the destination focus behavior is unchanged', DOC.activeElement, route.screens.study.heading);
eq('F3 the destination focus still prevents scrolling',
   route.screens.study.heading.lastFocusOptions, { preventScroll: true });
eq('F3 forward navigation schedules no deferred restoration', route.frames.length, 0);

route.scrolls.length = 0;
homeTile.focusCount = 0;
route.api.showScreen('home', false, true);
eq('F4 Back restores the remembered Home offset', route.win.scrollY, 1200);
eq('F4 Back restores the existing focus-return target', DOC.activeElement, homeTile);
eq('F4 the restored invoker is focused exactly once', homeTile.focusCount, 1);
eq('F4 focus restoration still prevents scrolling', homeTile.lastFocusOptions, { preventScroll: true });
eq('F4 focus restoration did not move the restored offset', route.win.scrollY, 1200);
eq('F4 Back records where the outgoing screen was left', route.api.offsets.get('study'), 0);
route.runFrames();
eq('F4 the deferred re-apply keeps the same offset', route.win.scrollY, 1200);
eq('F4 the deferred re-apply does not scroll again when the page is already there',
   route.scrolls.filter(function (y) { return y === 1200; }).length, 1);

// A restore whose offset was lost to a shorter document is re-applied after layout.
route.win.scrollY = 0;
route.api.showScreen('study');
route.win.scrollY = 640;
route.api.showScreen('home', false, true);
route.win.scrollY = 0;                      /* the destination was still shorter than the offset */
route.runFrames();
eq('F5 a deferred restoration re-applies the remembered offset once laid out',
   route.win.scrollY, route.api.offsets.get('home'));

// A frame scheduled by an earlier navigation must never move a later destination.
route.win.scrollY = 900;
route.api.showScreen('study');
route.win.scrollY = 0;
route.api.showScreen('home', false, true);  /* schedules a restore to 900 */
route.api.showScreen('about');              /* a newer navigation supersedes it */
eq('F6 the newer forward navigation starts at the top', route.win.scrollY, 0);
route.runFrames();
eq('F6 a stale deferred restoration cannot move a newer screen', route.win.scrollY, 0);
eq('F6 the newer navigation took the restoration token', route.api.token() >= 1, true);

var noRaf = routeHarness();
noRaf.win.requestAnimationFrame = undefined;
noRaf.win.scrollY = 480;
noRaf.api.showScreen('study');
noRaf.api.showScreen('home', false, true);
eq('F7 an engine without animation frames still restores immediately', noRaf.win.scrollY, 480);

// Overlays are not screens and must neither create nor consume an offset entry.
var overlayRoute = routeHarness();
overlayRoute.win.scrollY = 310;
overlayRoute.api.showScreen('study');
var offsetsBefore = JSON.stringify(Array.from(overlayRoute.api.offsets.entries()));
DOC.activeElement = overlayRoute.screens.study.heading;
ok('F8 the overlay opens through the unchanged shared contract',
   overlayRoute.api.openOverlay(overlayRoute.overlay, overlayRoute.overlayAction));
eq('F8 opening an overlay creates no screen-scroll entry',
   JSON.stringify(Array.from(overlayRoute.api.offsets.entries())), offsetsBefore);
ok('F8 the overlay closes through the unchanged shared contract',
   overlayRoute.api.closeOverlay(overlayRoute.overlay));
eq('F8 closing an overlay creates no screen-scroll entry',
   JSON.stringify(Array.from(overlayRoute.api.offsets.entries())), offsetsBefore);
eq('F8 the overlay never moved the page', overlayRoute.win.scrollY, 0);

// Direct fragment routing and its Back behavior are untouched.
var direct = routeHarness();
direct.api.showScreen('privacy');
eq('F9 a direct Privacy arrival starts at the top', direct.win.scrollY, 0);
ok('F9 a direct Privacy arrival is shown', direct.screens.privacy.classList.contains('active'));
ok('F9 direct fragment routing still marks its own history entry',
   INDEX.indexOf('history.replaceState({scr:ppInitialScreen,direct:true}') !== -1 &&
   INDEX.indexOf('["about","privacy","contact","install"].includes(ppInitialScreen)') !== -1);
ok('F9 the in-app Back route for a direct arrival is unchanged',
   squash(stripComments(extractFunction(INDEX, 'show')))
     .indexOf('if(history.state.direct){history.replaceState({scr:"home"},"",location.pathname+location.search);showScreen("home",deferFocus);}elsehistory.back();') !== -1);
eq('F9 routing creates no extra history entry',
   [countOf(INDEX, 'history.pushState'), countOf(INDEX, 'history.replaceState')], [1, 3]);
eq('F9 no parallel hashchange model was introduced', countOf(INDEX, 'hashchange'), 0);

// Source contract for the restoration architecture.
var APPLY = codeOf('ppApplyScreenScroll');
var SHOW_SCREEN = codeOf('showScreen');
ok('G1 exactly one caller asks for restoration',
   INDEX.indexOf('showScreen((e.state && e.state.scr) || "home", false, true)') !== -1);
eq('G1 restoration is requested from exactly one place',
   countOf(squash(stripComments(INDEX)), 'showScreen((e.state&&e.state.scr)||"home",false,true)'), 1);
ok('G1 forward navigation still resets the destination',
   APPLY.indexOf('target=restore?(ppScreenScrollOffsets.get(scr)||0):0') !== -1);
ok('G1 the outgoing screen offset is recorded before the swap',
   SHOW_SCREEN.indexOf('ppRememberScreenScroll(fromScreen.id)') <
   SHOW_SCREEN.indexOf('toScreen.classList.add("active")'));
ok('G1 the destination is placed before focus routes',
   SHOW_SCREEN.indexOf('ppApplyScreenScroll(scr,restoreScroll===true)') <
   SHOW_SCREEN.indexOf('ppRouteScreenFocus(fromScreen,toScreen)'));
ok('G2 the deferred re-apply is guarded by the navigation token',
   APPLY.indexOf('if(token!==ppScrollRestoreToken)return;') !== -1);
eq('G2 no arbitrary delay is introduced anywhere in the scroll contract',
   countOf(squash(ROUTE_BLOCK), 'setTimeout') + countOf(squash(ROUTE_BLOCK), 'setInterval') +
   countOf(APPLY, 'setTimeout') + countOf(SHOW_SCREEN, 'setTimeout'), 0);
eq('G2 the scroll contract uses one animation frame and nothing else',
   countOf(APPLY, 'requestAnimationFrame'), 2);
eq('G2 offsets are keyed by screen identity, not by visible text',
   [countOf(codeOf('ppRememberScreenScroll'), 'textContent'),
    countOf(codeOf('ppRememberScreenScroll'), 'innerHTML')], [0, 0]);
eq('G2 the scroll store adds no persistence',
   countOf(squash(ROUTE_BLOCK), 'localStorage') + countOf(squash(ROUTE_BLOCK), 'sessionStorage'), 0);
eq('G3 page scrolling happens only in the shared apply helper',
   countOf(squash(stripComments(INDEX)), 'window.scrollTo('), countOf(APPLY, 'window.scrollTo('));

// =========================================================================
// H. Unchanged safeguards.
// =========================================================================
ok('H1 app version is the 8.10 release', /const APP_VERSION = "8\.10"/.test(INDEX));
ok('H1 the shared status writer is untouched',
   codeOf('ppSetActivityStatus').indexOf('if(box.textContent===next)returnfalse;') !== -1);
ok('H1 the typed announcement wording is untouched',
   codeOf('ppAnnounceTypedActivityResult').indexOf('"Correct.Theansweris"') !== -1 &&
   codeOf('ppAnnounceTypedActivityResult').indexOf('"Almostcorrect.CheckthePolishspelling:"') !== -1 &&
   codeOf('ppAnnounceTypedActivityResult').indexOf('"Incorrect.Theansweris"') !== -1);
ok('H1 the conversation reply label is untouched',
   INDEX.indexOf('<div class="reply-label" id="cReplyLabel">Choose your reply</div>') !== -1);
ok('H1 the conversation completion heading is untouched',
   INDEX.indexOf('Rozmowa sko\\u0144czona!') !== -1);
ok('H1 the challenge-mode announcements are untouched',
   INDEX.indexOf('Challenge mode on. Translations are hidden.') !== -1 &&
   INDEX.indexOf('Challenge mode off. Translations are shown.') !== -1);
eq('H2 the shipping bubble contract still names its parts',
   [countOf(codeOf('cBubbleInnerHTML'), 'class="bubble-heading"'),
    countOf(codeOf('cBubbleInnerHTML'), 'class="bubble-speaker"'),
    countOf(codeOf('cBubbleInnerHTML'), 'lang="pl"'),
    countOf(codeOf('cBubbleHTML'), 'class="you-note"')], [1, 1, 2, 1]);
ok('H2 the audio control naming rule is unchanged',
   codeOf('cNameThreadAudio').indexOf('"PlayPolishphrase"') !== -1 &&
   codeOf('cNameThreadAudio').indexOf('"PlayhiddenPolishphrasefrom"') !== -1);

console.log('Phase 3B-2B focus and scroll tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] three-turn conversation measurements: ' + JSON.stringify(turnLog));
console.log('  [info] frozen conversation graph: ' + scenes + ' scenes, ' + routes + ' routes, ' + endings + ' endings');
console.log('  [info] MLG-3A-09, 10, 13 run against shipping source in a deterministic fake DOM with an explicit animation-frame queue');
console.log('  [info] real geometry, virtual keyboards, hardware Android Back, iOS Safari restoration, VoiceOver and TalkBack remain manual');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
