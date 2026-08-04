// Deterministic Phase 2A tests for the shared activity status/focus foundation
// and the four covered activity families. Runs with:
//   osascript -l JavaScript tests/test_phase2a_core_activity_accessibility.js
//
// The suite executes shipping functions extracted from index.html against a fake
// DOM with browser-like focus rejection. Existing activity suites continue to own
// exhaustive scoring, distractor, retry, grammar-order and audio-lifecycle matrices.
// A fake DOM cannot prove browser accessibility-tree output, visual focus, virtual-
// keyboard behavior, VoiceOver or TalkBack; those remain manual checks.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++) {
    if (fm.fileExistsAtPath(candidates[i] + 'index.html')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot(), INDEX = readFile(ROOT + 'index.html');

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) {
  var sa = JSON.stringify(a), sb = JSON.stringify(b);
  ok(name + (sa === sb ? '' : '  (got ' + sa + ', want ' + sb + ')'), sa === sb);
}
function countOf(hay, needle) {
  var count = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { count++; at += needle.length; }
  return count;
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
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
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
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  if (at === -1) throw new Error('markup: missing ' + id);
  return INDEX.slice(INDEX.lastIndexOf('<', at), INDEX.indexOf('>', at) + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}

// -------------------------------------------------------------------------
// Fake DOM shared by the shipping helpers and Type It.
// -------------------------------------------------------------------------
var BODY = null, DOC = null;
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
    for (var i = 0; i < classes.length; i++) {
      if (this._html.indexOf('class="' + classes[i] + '"') !== -1)
        this._queries['.' + classes[i]] = new El(this.id + '-' + classes[i], 'span');
    }
    if (this._html.indexOf('class="mini-audio"') !== -1) {
      var audio = new El(this.id + '-mini-audio', 'button'), open = this._html.match(/<button\b([^>]*class="mini-audio"[^>]*)>/);
      if (open) {
        var attrs = /([a-zA-Z_:][\w:.-]*)\s*=\s*"([^"]*)"/g, match;
        while ((match = attrs.exec(open[1])) !== null) audio.setAttribute(match[1], match[2]);
      }
      audio.parentElement = this;
      this._queries['.mini-audio'] = audio;
    }
  }
});
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.appendChild = function (child) {
  child.parentElement = this; this.children.push(child); return child;
};
El.prototype.querySelector = function (selector) { return this._queries[selector] || null; };
El.prototype.querySelectorAll = function (selector) { return this._queries[selector] || []; };
El.prototype.focus = function () { this.focusCount++; DOC.activeElement = this; };
El.prototype.closest = function (selector) {
  if (selector === '.screen') {
    for (var node = this; node; node = node.parentElement)
      if (node.classList && node.classList.contains('screen')) return node;
  }
  var tag = this.tagName.toLowerCase();
  if (selector && selector.indexOf(tag) !== -1) return this;
  return null;
};

BODY = new El('body', 'body');
DOC = {
  activeElement: BODY,
  contains: function (el) { return !!(el && el.connected); },
  createTextNode: function (value) { return new TextNode(value); },
  createElement: function (tag) { return new El('', tag); }
};
var WIN = { getComputedStyle: function (el) {
  return { display: el.style.display || 'block', visibility: el.style.visibility || 'visible' };
} };

var SHARED_NAMES = ['ppIsInteractiveTarget', 'ppIsHiddenOrInert', 'ppCanFocus', 'ppFocusElement',
  'ppFocusActivityTarget', 'ppKeepActivityFocusOr', 'ppSetActivityStatus',
  'ppAnnounceTypedActivityResult', 'ppSetActivityOptionState',
  'ppAudioControlName', 'ppSetAudioControlName'];
var SHARED = (new Function('document', 'window', 'PP_INTERACTIVE_SELECTOR',
  SHARED_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + SHARED_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};'
))(DOC, WIN, 'button,input,[role="button"]');

// -------------------------------------------------------------------------
// A. Shared announcement contract, executed from shipping helpers.
// -------------------------------------------------------------------------
var status = new El('status');
ok('A1 first status write changes the region', SHARED.ppSetActivityStatus(status, ['Ready.']));
eq('A1 status text is concise', status.textContent, 'Ready.');
var firstChildren = status.children;
eq('A2 unchanged status is suppressed', SHARED.ppSetActivityStatus(status, ['Ready.']), false);
ok('A2 unchanged status keeps the same nodes', status.children === firstChildren);
SHARED.ppSetActivityStatus(status, ['<b>not markup</b>']);
eq('A3 raw HTML is exposed as text', status.textContent, '<b>not markup</b>');
eq('A3 status writer never creates markup', status.innerHTML, '');
SHARED.ppSetActivityStatus(status, []);
eq('A4 stale status is deterministically cleared', status.textContent, '');

ok('A5 right typed result writes once',
   SHARED.ppAnnounceTypedActivityResult(status, 'right', 'mąka'));
eq('A5 right result wording is explicit', status.textContent,
   'Correct. The answer is mąka. Next is ready.');
eq('A5 right result has one Polish node', status.children.filter(function (n) {
  return n.nodeType === 1 && n.getAttribute('lang') === 'pl';
}).length, 1);
var typedChildren = status.children;
eq('A6 duplicate typed result is suppressed',
   SHARED.ppAnnounceTypedActivityResult(status, 'right', 'mąka'), false);
ok('A6 duplicate typed result keeps prior nodes', status.children === typedChildren);
SHARED.ppAnnounceTypedActivityResult(status, 'almost', 'mąka');
ok('A7 almost result is textual', /^Almost correct\./.test(status.textContent));
SHARED.ppAnnounceTypedActivityResult(status, 'wrong', 'mąka');
ok('A7 incorrect result is textual', /^Incorrect\./.test(status.textContent));

var optionBox = new El('options'), oa = new El('a', 'button'), ob = new El('b', 'button');
optionBox._queries['.opt'] = [oa, ob];
SHARED.ppSetActivityOptionState(optionBox, ob);
eq('A8 unselected option state is false', oa.getAttribute('aria-pressed'), 'false');
eq('A8 selected option state is true', ob.getAttribute('aria-pressed'), 'true');
SHARED.ppSetActivityOptionState(optionBox, oa);
eq('A8 selection moves instead of accumulating',
   [oa.getAttribute('aria-pressed'), ob.getAttribute('aria-pressed')], ['true', 'false']);

// -------------------------------------------------------------------------
// B. Shared focus contract, including every rejected target class.
// -------------------------------------------------------------------------
var screen = new El('screen'); screen.classList.add('screen'); screen.classList.add('active');
var target = new El('target', 'h2'); target.parentElement = screen;
ok('B1 a connected visible target receives focus', SHARED.ppFocusActivityTarget(target));
eq('B1 focus moved exactly once', target.focusCount, 1);
ok('B2 an already-focused valid target is retained', SHARED.ppFocusActivityTarget(target));
eq('B2 retaining focus adds no second move', target.focusCount, 1);
function rejected(name, mutate) {
  var el = new El(name, 'button'); el.parentElement = screen; mutate(el);
  var before = DOC.activeElement;
  eq('B3 ' + name + ' is rejected', SHARED.ppFocusActivityTarget(el), false);
  ok('B3 ' + name + ' does not move focus', DOC.activeElement === before && el.focusCount === 0);
}
rejected('disconnected target', function (el) { el.connected = false; });
rejected('disabled target', function (el) { el.disabled = true; });
rejected('aria-disabled target', function (el) { el.setAttribute('aria-disabled', 'true'); });
rejected('hidden target', function (el) { el.hidden = true; });
rejected('display-none target', function (el) { el.style.display = 'none'; });
rejected('visibility-hidden target', function (el) { el.style.visibility = 'hidden'; });
rejected('aria-hidden target', function (el) { el.setAttribute('aria-hidden', 'true'); });
rejected('inert target', function (el) { el.inert = true; });
var hiddenParent = new El('hidden-parent'); hiddenParent.parentElement = screen;
hiddenParent.setAttribute('aria-hidden', 'true');
var hiddenChild = new El('hidden-child', 'button'); hiddenChild.parentElement = hiddenParent;
eq('B4 an aria-hidden ancestor rejects its child', SHARED.ppFocusActivityTarget(hiddenChild), false);
var inactive = new El('inactive'); inactive.classList.add('screen');
var inactiveChild = new El('inactive-child', 'button'); inactiveChild.parentElement = inactive;
eq('B4 an inactive screen rejects its child', SHARED.ppFocusActivityTarget(inactiveChild), false);
var liveButton = new El('live-trigger', 'button'); liveButton.parentElement = screen;
liveButton.closest = function () { return this; };
var unusedFallback = new El('unused-fallback', 'input'); unusedFallback.parentElement = screen;
DOC.activeElement = liveButton;
ok('B4 an enabled interactive trigger is preserved', SHARED.ppKeepActivityFocusOr(unusedFallback, liveButton));
ok('B4 preserving a trigger makes no fallback focus move',
   DOC.activeElement === liveButton && unusedFallback.focusCount === 0);

// Execute each shipping next-option helper with the shared target guard.
['gFocusNextOption', 'lFocusNextOption', 'rFocusNextOption'].forEach(function (name) {
  var api = (new Function('ppFocusActivityTarget', extractFunction(INDEX, name) + '\nreturn ' + name + ';'))(
    SHARED.ppFocusActivityTarget);
  var box = new El(name + '-box'), a = new El('a', 'button'), b = new El('b', 'button'), c = new El('c', 'button');
  a.parentElement = screen; b.parentElement = screen; c.parentElement = screen;
  box._queries['.opt'] = [a, b, c]; b.disabled = true; DOC.activeElement = BODY;
  eq('B5 ' + name + ' returns the next enabled option', api(box, b), c);
  ok('B5 ' + name + ' focuses once and not BODY', DOC.activeElement === c && c.focusCount === 1);
});

// -------------------------------------------------------------------------
// C. Markup semantics and language boundaries.
// -------------------------------------------------------------------------
eq('C1 document language remains English', attr((INDEX.match(/<html\b[^>]*>/) || [''])[0], 'lang'), 'en');
['tInput', 'rInput'].forEach(function (id) {
  var tag = tagFor(id);
  eq('C1 ' + id + ' answer language remains Polish', attr(tag, 'lang'), 'pl');
  ok('C1 ' + id + ' is labelled by instruction and prompt', /Instruction|rType/.test(attr(tag, 'aria-labelledby')) &&
     /tEn|rEn/.test(attr(tag, 'aria-labelledby')));
  ok('C1 ' + id + ' describes help, context and hint', /Help/.test(attr(tag, 'aria-describedby')) &&
     /Ctx/.test(attr(tag, 'aria-describedby')) && /HintLine/.test(attr(tag, 'aria-describedby')));
});
['tStatus', 'gStatus', 'lStatus', 'rStatus'].forEach(function (id) {
  var tag = tagFor(id);
  eq('C2 ' + id + ' is a status', attr(tag, 'role'), 'status');
  eq('C2 ' + id + ' is polite', attr(tag, 'aria-live'), 'polite');
  eq('C2 ' + id + ' is atomic', attr(tag, 'aria-atomic'), 'true');
});
eq('C3 Type It rich verdict is not live', attr(tagFor('tVerdict'), 'aria-live'), null);
eq('C3 Mixed typed rich verdict is not live', attr(tagFor('rVerdict'), 'aria-live'), null);
eq('C3 Type It completion target is script-only', attr(tagFor('tDoneTitle'), 'tabindex'), '-1');
eq('C3 Listening options are a named group',
   [attr(tagFor('lOpts'), 'role'), attr(tagFor('lOpts'), 'aria-labelledby')], ['group', 'lPrompt']);
eq('C3 duplicate Mixed feedback ids are absent', countOf(INDEX, 'id="rFb"'), 1);
ok('C3 Listening heading keeps its prior compact spacing',
   /#lPrompt\s*\{[^}]*margin\s*:\s*0\s+0\s+14px[^}]*\}/.test(INDEX));
ok('C4 contextual Play and Replay names ship in Listening',
   extractFunction(INDEX, 'syncListeningAudioReadiness').indexOf('question') !== -1 &&
   extractFunction(INDEX, 'lPlayCurrent').indexOf('Replay Polish audio') !== -1);
ok('C4 fallback-voice message is an atomic status',
   extractFunction(INDEX, 'voiceHint').indexOf('role","status') !== -1 &&
   extractFunction(INDEX, 'voiceHint').indexOf('aria-atomic","true') !== -1);

// -------------------------------------------------------------------------
// D. Type It end-to-end through shipping start/render/hint/check/done functions.
// -------------------------------------------------------------------------
var appWindow = {};
(new Function('window', readFile(ROOT + 'pp-answer.js')))(appWindow);
var ANSWER = appWindow.PP_ANSWER;
var TYPE_NAMES = ['startTypeit', 'tRender', 'tRevealLetter', 'tCheckAnswer', 'tShowDone'];
var TYPE_COMPILE = new Function('$', 'T', 'LEVELS', 'poolFor', 'gShuffle', 'show',
  'PP_ANSWER', 'PP_TYPED_INDEX', 'ppHasMainAudio', 'ppMainAudioText', 'ppVariantParts',
  'ppAppendUsageTo', 'G_AUDIO', 'window', 'ppSetActivityStatus',
  'ppAnnounceTypedActivityResult', 'ppFocusActivityTarget', 'ppKeepActivityFocusOr',
  'ppSetAudioControlName',
  TYPE_NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + TYPE_NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};');

function typeHarness(card) {
  var nodes = {}, root = new El('typeit-screen'); root.classList.add('screen'); root.classList.add('active');
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
  var index = ANSWER.buildIndex([card]);
  var api = TYPE_COMPILE(get, T, [{ topics: [{ name: 'Topic', src: 'topic' }] }],
    function () { return [{ c: card, topic: 'Topic' }]; }, function (a) { return a.slice(); },
    function () {}, ANSWER, index, function () { return true; }, function (c) { return c.pl; },
    function () { return null; }, function () {}, '', {}, SHARED.ppSetActivityStatus,
    SHARED.ppAnnounceTypedActivityResult, SHARED.ppFocusActivityTarget, SHARED.ppKeepActivityFocusOr,
    SHARED.ppSetAudioControlName);
  return { T: T, $: get, api: api, card: card };
}

var card = { id: 'phase2a-card', pl: 'mąka', en: 'flour', exEn: 'We need flour.' };
var right = typeHarness(card); right.api.startTypeit(0, 0);
eq('D1 Type It starts on the visible prompt', DOC.activeElement, right.$('tEn'));
eq('D1 Type It starts with an empty status', right.$('tStatus').textContent, '');
eq('D1 Type It starts with enabled input/submit/hint',
   [right.$('tInput').disabled, right.$('tCheck').disabled, right.$('tHint').disabled],
   [false, false, false]);
DOC.activeElement = right.$('tCheck'); right.api.tCheckAnswer();
eq('D2 blank Type It submission is announced', right.$('tStatus').textContent,
   'Type the Polish answer first.');
eq('D2 blank click keeps the still-valid Check trigger', DOC.activeElement, right.$('tCheck'));
var blankChildren = right.$('tStatus').children; var checkMoves = right.$('tCheck').focusCount;
right.api.tCheckAnswer();
ok('D2 repeated blank result is not rebuilt', right.$('tStatus').children === blankChildren);
eq('D2 repeated blank result does not re-focus the same trigger', right.$('tCheck').focusCount, checkMoves);
DOC.activeElement = right.$('tInput'); right.api.tCheckAnswer();
eq('D2 blank Enter keeps the input trigger', DOC.activeElement, right.$('tInput'));
DOC.activeElement = right.$('tHint');
right.api.tRevealLetter();
ok('D3 hint becomes visible text', !right.$('tHintLine').hidden && /^Starts with:/.test(right.$('tHintLine').textContent));
eq('D3 hint keeps its still-valid trigger', DOC.activeElement, right.$('tHint'));
ok('D3 focused hint control exposes the current hint in its name',
   right.$('tHint').getAttribute('aria-label').indexOf('Starts with:') !== -1);
right.$('tInput').value = card.pl; right.api.tCheckAnswer();
eq('D4 right answer announcement is concise', right.$('tStatus').textContent,
   'Correct. The answer is mąka. Next is ready.');
ok('D4 right answer is visible without colour', right.$('tVerdict').className.indexOf('v-right') !== -1 &&
   right.$('tVerdict').innerHTML.indexOf('Dobrze!') !== -1);
eq('D4 right answer retains unchanged scoring', [right.T.right, right.T.almost], [1, 0]);
ok('D4 settled input is invalid=false and disabled',
   right.$('tInput').disabled && right.$('tInput').getAttribute('aria-invalid') === 'false');
eq('D4 settled answer focuses enabled Next',
   [DOC.activeElement, right.$('tNext').disabled], [right.$('tNext'), false]);
eq('D4 Type It answer audio has phrase-specific context',
   right.$('tVerdict').querySelector('.mini-audio').getAttribute('aria-label'),
   'Play answer: mąka');
eq('D4 Type It answer audio keeps the exact engine phrase',
   decodeURIComponent(right.$('tVerdict').querySelector('.mini-audio').getAttribute('data-say')), 'mąka');
right.T.i++; right.api.tRender();
eq('D5 completion focuses its heading', DOC.activeElement, right.$('tDoneTitle'));
eq('D5 completion clears prior feedback', right.$('tStatus').textContent, '');
eq('D5 completion arithmetic is unchanged',
   [right.$('tScoreN').textContent, right.$('tAlmostN').textContent, right.$('tMissN').textContent],
   ['1', '0', '0']);
right.api.startTypeit(0, 0);
eq('D6 restart focuses the new prompt, not completion controls', DOC.activeElement, right.$('tEn'));
eq('D6 restart resets scoring and progress',
   [right.T.i, right.T.right, right.T.almost, right.$('tCountLbl').textContent], [0, 0, 0, '1 / 1']);

var almost = typeHarness(card); almost.api.startTypeit(0, 0);
almost.$('tInput').value = 'maka'; almost.api.tCheckAnswer();
ok('D7 almost answer is announced once and visible in words',
   /^Almost correct\./.test(almost.$('tStatus').textContent) &&
   almost.$('tVerdict').innerHTML.indexOf('Almost - watch') !== -1);
eq('D7 almost scoring stays separate', [almost.T.right, almost.T.almost], [0, 1]);
eq('D7 almost input state is invalid', almost.$('tInput').getAttribute('aria-invalid'), 'true');

var wrong = typeHarness(card); wrong.api.startTypeit(0, 0);
wrong.$('tInput').value = 'ziemniak'; wrong.api.tCheckAnswer();
ok('D8 incorrect answer is announced once and visible in words',
   /^Incorrect\./.test(wrong.$('tStatus').textContent) &&
   wrong.$('tVerdict').innerHTML.indexOf('Not this time') !== -1);
eq('D8 incorrect answer changes neither right nor almost', [wrong.T.right, wrong.T.almost], [0, 0]);

var unsafeAnswer = '<b>żółw</b> & "cytat"';
var unsafe = typeHarness({ id: 'phase2a-unsafe', pl: unsafeAnswer, en: 'unsafe fixture' });
unsafe.api.startTypeit(0, 0); unsafe.$('tInput').value = unsafeAnswer; unsafe.api.tCheckAnswer();
eq('D9 HTML-like Type It answer stays literal in the audio name',
   unsafe.$('tVerdict').querySelector('.mini-audio').getAttribute('aria-label'),
   'Play answer: ' + unsafeAnswer);
eq('D9 HTML-like Type It answer keeps its exact encoded engine phrase',
   decodeURIComponent(unsafe.$('tVerdict').querySelector('.mini-audio').getAttribute('data-say')),
   unsafeAnswer);

// -------------------------------------------------------------------------
// E. Execute each activity-specific status wrapper with the shared writer.
// -------------------------------------------------------------------------
function statusApi(prefix) {
  var names = [prefix + 'SetStatus', prefix + 'AnnounceWrong', prefix + 'AnnounceCorrect'];
  var node = new El(prefix + 'Status');
  function get() { return node; }
  var api = (new Function('$', 'document', 'ppSetActivityStatus',
    names.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
    '\nreturn {' + names.map(function (name) { return name + ':' + name; }).join(',') + '};'))(
      get, DOC, SHARED.ppSetActivityStatus);
  return { node: node, api: api, names: names };
}
['g', 'l', 'r'].forEach(function (prefix) {
  var h = statusApi(prefix);
  h.api[h.names[1]]('<wrong>');
  eq('E1 ' + prefix + ' wrong feedback stays literal text', h.node.textContent,
     '<wrong> is not correct. Try another answer.');
  h.api[h.names[2]]('mąka');
  ok('E1 ' + prefix + ' correct feedback replaces stale wrong feedback',
     /^Correct\./.test(h.node.textContent) && h.node.textContent.indexOf('<wrong>') === -1);
  eq('E1 ' + prefix + ' correct feedback keeps one Polish node',
     h.node.children.filter(function (n) { return n.nodeType === 1 && n.getAttribute('lang') === 'pl'; }).length, 1);
  h.api[h.names[0]]([]);
  eq('E1 ' + prefix + ' next-question clear removes stale feedback', h.node.textContent, '');
});
var grammarWrong = statusApi('g');
grammarWrong.api.gAnnounceWrong('<b>zły</b> & "gorszy"');
eq('E2 Grammar wrong answer keeps one Polish-language node',
   grammarWrong.node.children.filter(function (n) {
     return n.nodeType === 1 && n.getAttribute('lang') === 'pl';
   }).length, 1);
eq('E2 Grammar learner text remains literal and separate from English explanation',
   grammarWrong.node.textContent, '<b>zły</b> & "gorszy" is not correct. Try another answer.');
ok('E2 Grammar explanation remains a separate English text node',
   grammarWrong.node.children.some(function (n) {
     return n.nodeType === 3 && n.textContent === ' is not correct. Try another answer.';
   }));

// Grammar-specific semantics and all Mixed formats remain executed exhaustively by
// their established shipping-function suites; pin the Phase 2A handoff points here.
ok('E3 Grammar choose render creates a stable question heading and named option group',
   extractFunction(INDEX, 'gRenderChoose').indexOf('id="gQuestion"') !== -1 &&
   extractFunction(INDEX, 'gRenderChoose').indexOf('aria-labelledby="gInstruction gQuestion"') !== -1);
ok('E3 Grammar build render exposes selected tile state',
   extractFunction(INDEX, 'gPaintBuild').indexOf('aria-pressed="true"') !== -1 &&
   extractFunction(INDEX, 'gPaintBuild').indexOf('aria-pressed="false"') !== -1);
ok('E3 Mixed render covers type/listen/mc prompt focus targets', (function () {
  var src = extractFunction(INDEX, 'rRender');
  return src.indexOf('q.fmt==="type"') !== -1 && src.indexOf('q.fmt==="listen"') !== -1 &&
         src.indexOf('rEn') !== -1 && src.indexOf('rType') !== -1 && src.indexOf('rPl') !== -1;
})());
ok('E3 Listening and Mixed options initialize selected=false',
   extractFunction(INDEX, 'lRender').indexOf('aria-pressed","false') !== -1 &&
   extractFunction(INDEX, 'rRender').indexOf('aria-pressed","false') !== -1);

// -------------------------------------------------------------------------
// F. Phase 1A/1B regression foundations, executed rather than grepped.
// -------------------------------------------------------------------------
var syncFaces = (new Function(extractFunction(INDEX, 'ppSyncFlipFaces') + '\nreturn ppSyncFlipFaces;'))();
var faceA = new El('face-a'), faceB = new El('face-b'), flip = new El('flip');
flip._queries['.face'] = [faceA, faceB];
syncFaces(flip);
eq('F1 inactive second face remains inert/aria-hidden',
   [faceA.inert, faceA.getAttribute('aria-hidden'), faceB.inert, faceB.getAttribute('aria-hidden')],
   [false, null, true, 'true']);
flip.classList.add('flipped'); syncFaces(flip);
eq('F1 face semantics swap completely',
   [faceA.inert, faceA.getAttribute('aria-hidden'), faceB.inert, faceB.getAttribute('aria-hidden')],
   [true, 'true', false, null]);

var isInteractive = (new Function('PP_INTERACTIVE_SELECTOR',
  extractFunction(INDEX, 'ppIsInteractiveTarget') + '\nreturn ppIsInteractiveTarget;'))('button');
var nativeTarget = { isContentEditable: false, closest: function () { return { tagName: 'BUTTON' }; } };
var plainTarget = { isContentEditable: false, closest: function () { return null; } };
eq('F2 native controls remain protected from shared shortcuts', isInteractive(nativeTarget), true);
eq('F2 plain content remains available to shared shortcuts', isInteractive(plainTarget), false);

console.log('Phase 2A core activity accessibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] shipping helpers and Type It run in a deterministic fake DOM; real accessibility trees, screen readers, visual focus and mobile keyboards remain manual');
for (var li = 0; li < LOG.length; li++) console.log('  ' + LOG[li]);
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
