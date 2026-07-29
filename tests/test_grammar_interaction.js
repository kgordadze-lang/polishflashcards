// Behavioral tests for the shipping Grammar choose-drill interaction.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_grammar_interaction.js
//
// The suite extracts the real Grammar functions from index.html and drives them
// against a fake DOM that preserves the browser rules this interaction depends on:
// a disabled/hidden element cannot receive focus, disabling the focused control
// moves focus to BODY, textContent stays text, and aria-label owns an accessible
// name when present. Grammar content is loaded from the real data files.

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

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) {
  if (cond) PASS++;
  else { FAIL++; LOG.push('FAIL: ' + name); }
}
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function info(msg) { console.log('  [info] ' + msg); }

function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  if (src.indexOf(needle, start + 1) !== -1) {
    throw new Error('extract: function ' + name + ' declared more than once');
  }
  var open = src.indexOf('{', src.indexOf(')', start));
  if (open === -1) throw new Error('extract: no body for ' + name);
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
    else if (c === '}') {
      depth--;
      if (depth === 0) return src.slice(start, j + 1);
    }
  }
  throw new Error('extract: unbalanced braces for ' + name);
}
function codeOnly(src) {
  var out = '', mode = 'code';
  for (var j = 0; j < src.length; j++) {
    var c = src[j], n = src[j + 1];
    if (mode === 'line') { if (c === '\n') { mode = 'code'; out += c; } continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; j++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      out += c;
      if (c === '\\') { out += src[j + 1]; j++; continue; }
      if (mode === 'sq' && c === "'") mode = 'code';
      else if (mode === 'dq' && c === '"') mode = 'code';
      else if (mode === 'tpl' && c === '`') mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; j++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; j++; continue; }
    if (c === "'" || c === '"' || c === '`') {
      mode = c === "'" ? 'sq' : c === '"' ? 'dq' : 'tpl';
      out += c;
      continue;
    }
    out += c;
  }
  return out;
}
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  if (at === -1) return '';
  var open = INDEX.lastIndexOf('<', at), close = INDEX.indexOf('>', at);
  return open === -1 || close === -1 ? '' : INDEX.slice(open, close + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}
var STYLE = (function () {
  var out = '', at = 0;
  while ((at = INDEX.indexOf('<style', at)) !== -1) {
    var s = INDEX.indexOf('>', at) + 1, e = INDEX.indexOf('</style>', s);
    out += INDEX.slice(s, e);
    at = e;
  }
  return out.replace(/\/\*[\s\S]*?\*\//g, '');
})();
function cssBlocks(selectorNeedle) {
  var hits = [], re = /([^{}]+)\{([^{}]*)\}/g, m;
  while ((m = re.exec(STYLE)) !== null) {
    if (m[1].indexOf(selectorNeedle) !== -1) hits.push({ sel: m[1].trim(), body: m[2] });
  }
  return hits;
}

// =========================================================================
// A. CORPUS INTEGRITY
// =========================================================================
var savedWindow = typeof window === 'undefined' ? undefined : window;
var window = { PP_LEVELS: [] };
(0, eval)(readFile(ROOT + 'data-grammar.js'));
(0, eval)(readFile(ROOT + 'data-verbs.js'));
var GRAMMAR_LEVELS = window.PP_LEVELS.slice();
if (savedWindow !== undefined) window = savedWindow;

var DRILLS = [];
GRAMMAR_LEVELS.forEach(function (level) {
  (level.topics || []).forEach(function (topic) {
    (topic.drills || []).forEach(function (drill) {
      DRILLS.push({ level: level, topic: topic, drill: drill });
    });
  });
});
var CHOOSE = DRILLS.filter(function (x) { return x.drill.type === 'choose'; });
var BUILD = DRILLS.filter(function (x) { return x.drill.type === 'build'; });
var IDS = DRILLS.map(function (x) { return x.drill.id; });
function usableString(v) { return typeof v === 'string' && v.trim().length > 0; }
function optionNorm(v) {
  return v.normalize('NFC').trim().toLocaleLowerCase().replace(/\s+/g, ' ');
}

ok('A1 Grammar data files expose at least one drill', DRILLS.length > 0);
ok('A1 every drill has a non-empty stable id', IDS.every(usableString));
eq('A1 drill ids are unique', new Set(IDS).size, IDS.length);
eq('A1 only choose and build drill types exist',
   Array.from(new Set(DRILLS.map(function (x) { return x.drill.type; }))).sort(),
   ['build', 'choose']);
ok('A2 every choose drill has at least two options', CHOOSE.every(function (x) {
  return Array.isArray(x.drill.options) && x.drill.options.length >= 2;
}));
ok('A2 every choose option is a non-empty string', CHOOSE.every(function (x) {
  return x.drill.options.every(usableString);
}));
ok('A2 every choose answer is a non-empty string', CHOOSE.every(function (x) {
  return usableString(x.drill.answer);
}));
ok('A2 every choose answer appears exactly once', CHOOSE.every(function (x) {
  return x.drill.options.filter(function (o) { return o === x.drill.answer; }).length === 1;
}));
ok('A2 no choose drill has exact duplicate options', CHOOSE.every(function (x) {
  return new Set(x.drill.options).size === x.drill.options.length;
}));
ok('A2 no choose drill has duplicates after NFC/trim/lowercase/space normalization',
   CHOOSE.every(function (x) {
     var n = x.drill.options.map(optionNorm);
     return new Set(n).size === n.length;
   }));
ok('A2 required choose teaching fields are usable', CHOOSE.every(function (x) {
  var d = x.drill;
  return usableString(d.prompt) && usableString(d.promptEn) && usableString(d.full) &&
         usableString(d.fullEn) && usableString(d.explain);
}));
ok('A3 build drills meet the existing minimal structure', BUILD.every(function (x) {
  var d = x.drill;
  return usableString(d.id) && usableString(d.promptEn) &&
         Array.isArray(d.answer) && d.answer.length > 0 && d.answer.every(usableString) &&
         usableString(d.full) && usableString(d.fullEn) && usableString(d.explain);
}));
var SPECIAL_REAL = [];
CHOOSE.forEach(function (x) {
  x.drill.options.forEach(function (o) {
    if (/['"<>&]/.test(o)) SPECIAL_REAL.push({ id: x.drill.id, option: o });
  });
});
info('Grammar corpus: ' + DRILLS.length + ' drills (' + CHOOSE.length +
     ' choose, ' + BUILD.length + ' build); counts are discovered, not pinned');
info('real choose options containing quote/HTML-like characters: ' + SPECIAL_REAL.length);

// =========================================================================
// B. MARKUP SEMANTICS
// =========================================================================
var GRAMMAR_SCREEN = (function () {
  var s = INDEX.indexOf('<section class="screen" id="grammar"');
  var e = INDEX.indexOf('<section', s + 10);
  return s === -1 ? '' : INDEX.slice(s, e === -1 ? INDEX.length : e);
})();
var TAG_STATUS = tagFor('gStatus');
eq('B1 exactly one gStatus exists', countOf(INDEX, 'id="gStatus"'), 1);
eq('B1 gStatus lives in Grammar', countOf(GRAMMAR_SCREEN, 'id="gStatus"'), 1);
eq('B1 gStatus is sr-only', attr(TAG_STATUS, 'class'), 'sr-only');
eq('B1 gStatus has role=status', attr(TAG_STATUS, 'role'), 'status');
eq('B1 gStatus announces politely', attr(TAG_STATUS, 'aria-live'), 'polite');
eq('B1 gStatus is atomic', attr(TAG_STATUS, 'aria-atomic'), 'true');
ok('B1 gStatus ships empty', /id="gStatus"[^>]*>\s*<\//.test(INDEX));
ok('B1 gStatus is outside gDrillCard and before Grammar controls', (function () {
  var card = GRAMMAR_SCREEN.indexOf('id="gDrillCard"');
  var status = GRAMMAR_SCREEN.indexOf('id="gStatus"');
  var next = GRAMMAR_SCREEN.indexOf('id="gDrillNext"');
  return card !== -1 && status > card && status < next;
})());
var CODE_RENDER_CHOOSE = codeOnly(extractFunction(INDEX, 'gRenderChoose'));
var CODE_RENDER_BUILD = codeOnly(extractFunction(INDEX, 'gRenderBuild'));
ok('B2 choose gFbBox is not a competing live region',
   CODE_RENDER_CHOOSE.indexOf('aria-live') === -1 &&
   CODE_RENDER_CHOOSE.indexOf('role="status"') === -1);
ok('B2 choose gFbBox remains the visible feedback box',
   CODE_RENDER_CHOOSE.indexOf('gFbBox') !== -1 &&
   CODE_RENDER_CHOOSE.indexOf('fb-box') !== -1);
ok('B2 build feedback behavior remains live and out of Phase 4G',
   CODE_RENDER_BUILD.indexOf('gFbBox') !== -1 &&
   CODE_RENDER_BUILD.indexOf('aria-live="polite"') !== -1);
var TAG_DONE = tagFor('gDoneTitle');
ok('B3 gDoneTitle is the existing h2', /^<h2\b/.test(TAG_DONE));
eq('B3 exactly one gDoneTitle exists', countOf(INDEX, 'id="gDoneTitle"'), 1);
eq('B3 gDoneTitle is script-focusable only', attr(TAG_DONE, 'tabindex'), '-1');
ok('B3 completion wording remains Brawo!', /id="gDoneTitle"[^>]*>Brawo!</.test(INDEX));
ok('B4 only the Grammar completion anchor loses its decorative focus outline', (function () {
  var rules = cssBlocks('#gDoneTitle:focus').filter(function (b) {
    return /outline\s*:\s*(none|0)/.test(b.body);
  });
  return rules.length >= 1 && rules.every(function (b) {
    return b.sel.split(',').every(function (s) { return /^#gDoneTitle:focus$/.test(s.trim()); });
  });
})());
ok('B4 real Grammar controls retain focus indicators',
   cssBlocks('.opt:focus-visible').length >= 1 &&
   cssBlocks('.ctrl:focus-visible').length >= 1);

// =========================================================================
// FAKE DOM + SHIPPING GRAMMAR FUNCTIONS
// =========================================================================
var BODY = null, ACTIVE = null, DOM = {}, HTML_WRITES = {};
function classHas(el, name) {
  return !!el.classes[name] ||
    (' ' + el.className.replace(/\s+/g, ' ') + ' ').indexOf(' ' + name + ' ') !== -1;
}
function decodeHtmlText(s) {
  return s.replace(/<[^>]*>/g, '')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'");
}
function FakeEl(tag) {
  this.tag = tag || 'div';
  this.id = '';
  this.className = '';
  this.classes = {};
  this._disabled = false;
  this.hidden = false;
  this.style = {};
  this.children = [];
  this.parentNode = null;
  this._own = '';
  this._html = '';
  this._htmlText = null;
  this._attrs = {};
  this._on = {};
  this.focusCount = 0;
  var self = this;
  this.classList = {
    add: function (c) { self.classes[c] = true; },
    remove: function (c) { delete self.classes[c]; },
    contains: function (c) { return classHas(self, c); }
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
    if (this._htmlText !== null) return this._htmlText;
    if (this.children.length) {
      return this.children.map(function (c) { return c.textContent; }).join('');
    }
    return this._own;
  },
  set: function (v) {
    this._own = String(v);
    this._html = '';
    this._htmlText = null;
    this.children = [];
  }
});
function parseAttrs(raw, node) {
  var re = /([a-zA-Z_:][\w:.-]*)\s*=\s*"([^"]*)"/g, m;
  while ((m = re.exec(raw)) !== null) node.setAttribute(m[1], m[2]);
}
function register(node) {
  if (node.id) DOM[node.id] = node;
  return node;
}
Object.defineProperty(FakeEl.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (v) {
    this._html = String(v);
    this._own = '';
    this._htmlText = decodeHtmlText(this._html);
    this.children = [];
    if (this.id) HTML_WRITES[this.id] = (HTML_WRITES[this.id] || 0) + 1;

    if (this.id === 'gDrillCard') {
      var opts = null;
      var om = this._html.match(/<div\b([^>]*\bclass\s*=\s*"[^"]*\bopts\b[^"]*"[^>]*)>/);
      if (om) {
        opts = new FakeEl('div');
        parseAttrs(om[1], opts);
        this.appendChild(register(opts));
      }
      var fm = this._html.match(/<div\b([^>]*\bid\s*=\s*"gFbBox"[^>]*)>/);
      if (fm) {
        var fb = new FakeEl('div');
        parseAttrs(fm[1], fb);
        this.appendChild(register(fb));
      }
      var br = /<button\b([^>]*)>([\s\S]*?)<\/button>/g, bm;
      while ((bm = br.exec(this._html)) !== null) {
        var b = new FakeEl('button');
        parseAttrs(bm[1], b);
        b._html = bm[2];
        b._htmlText = decodeHtmlText(bm[2]);
        var nested = /<([a-zA-Z][\w-]*)\b([^>]*)>/g, nm;
        while ((nm = nested.exec(bm[2])) !== null) {
          var kid = new FakeEl(nm[1]);
          parseAttrs(nm[2], kid);
          b.appendChild(kid);
        }
        (classHas(b, 'opt') && opts ? opts : this).appendChild(register(b));
      }
    } else {
      var tr = /<([a-zA-Z][\w-]*)\b([^>]*)>/g, tm;
      while ((tm = tr.exec(this._html)) !== null) {
        var child = new FakeEl(tm[1]);
        parseAttrs(tm[2], child);
        this.appendChild(register(child));
      }
    }
  }
});
Object.defineProperty(FakeEl.prototype, 'childNodes', {
  get: function () { return this.children; }
});
FakeEl.prototype.appendChild = function (node) {
  this._htmlText = null;
  node.parentNode = this;
  this.children.push(node);
  return node;
};
FakeEl.prototype.replaceChildren = function () {
  this.children = [];
  this._own = '';
  this._html = '';
  this._htmlText = null;
  for (var i = 0; i < arguments.length; i++) this.appendChild(arguments[i]);
};
FakeEl.prototype.setAttribute = function (k, v) {
  this._attrs[k] = String(v);
  if (k === 'class') this.className = String(v);
  if (k === 'id') { this.id = String(v); register(this); }
};
FakeEl.prototype.getAttribute = function (k) {
  return Object.prototype.hasOwnProperty.call(this._attrs, k) ? this._attrs[k] : null;
};
FakeEl.prototype.addEventListener = function (type, fn) {
  (this._on[type] = this._on[type] || []).push(fn);
};
FakeEl.prototype.click = function () {
  if (this.disabled || this.hidden) return;
  (this._on.click || []).slice().forEach(function (fn) { fn({}); });
};
FakeEl.prototype.isHidden = function () {
  var at = this;
  while (at) {
    if (at.hidden || at.style.display === 'none') return true;
    at = at.parentNode;
  }
  return false;
};
FakeEl.prototype.focus = function () {
  if (this.disabled || this.isHidden()) return;
  this.focusCount++;
  ACTIVE = this;
};
FakeEl.prototype.querySelectorAll = function (selector) {
  var out = [];
  var classMatch = selector.match(/^\.([\w-]+)/);
  var idMatch = selector.match(/^#([\w-]+)/);
  function visit(node) {
    node.children.forEach(function (child) {
      var hit = classMatch ? classHas(child, classMatch[1]) :
                idMatch ? child.id === idMatch[1] : false;
      if (hit && selector.indexOf(':not(:disabled)') !== -1 && child.disabled) hit = false;
      if (hit) out.push(child);
      if (child.children) visit(child);
    });
  }
  visit(this);
  return out;
};
FakeEl.prototype.querySelector = function (selector) {
  var all = this.querySelectorAll(selector);
  return all.length ? all[0] : null;
};
FakeEl.prototype.accName = function () {
  var aria = this.getAttribute('aria-label');
  return aria === null ? this.textContent : aria;
};
function el(id) {
  if (!DOM[id]) {
    DOM[id] = new FakeEl('div');
    DOM[id].id = id;
  }
  return DOM[id];
}
var fakeDocument = {
  createElement: function (tag) { return new FakeEl(tag); },
  createTextNode: function (text) {
    return { nodeType: 3, textContent: String(text), parentNode: null };
  },
  get activeElement() { return ACTIVE; },
  get body() { return BODY; }
};

var G_STATE_MATCH = INDEX.match(/const\s+G\s*=\s*(\{[^\n]*\})\s*;/);
if (!G_STATE_MATCH) throw new Error('extract: Grammar state object G not found');
function freshG() { return (0, eval)('(' + G_STATE_MATCH[1] + ')'); }
var G = freshG();
var GNAMES = [
  'gPhaseView', 'gStartPractice', 'gUpdateNextLabel', 'gRenderDrill',
  'gRenderChoose', 'gSetStatus', 'gAnnounceWrong', 'gAnnounceCorrect',
  'gFocusNextOption', 'gChooseFeedback', 'gRenderBuild', 'gPaintBuild',
  'gCheckBuild', 'gDrillAdvance', 'gShowDone'
];
var GSRC = {};
GNAMES.forEach(function (name) {
  try { GSRC[name] = extractFunction(INDEX, name); }
  catch (_) { GSRC[name] = 'function ' + name + '(){}'; }
});
var AUDIO_STARTS = 0;
function speakText() { AUDIO_STARTS++; }
function speakCardMain() { AUDIO_STARTS++; }
function stopAllAudio() {}
function identityShuffle(a) { return a.slice(); }
function noMix() {}
function immediateTimer(fn) { fn(); }
var GRAMMAR = (new Function(
  '$', 'document', 'G', 'G_AUDIO', 'gShuffle', 'gSampleMix', 'setTimeout',
  GNAMES.map(function (n) { return GSRC[n]; }).join('\n') +
  '\nreturn {' + GNAMES.map(function (n) { return n + ':' + n; }).join(',') + '};'
))(el, fakeDocument, G, '<svg class="audio-icon"></svg>', identityShuffle, noMix, immediateTimer);

function add(parent, id, tag) {
  var node = new FakeEl(tag || 'div');
  node.id = id;
  DOM[id] = node;
  if (parent) parent.appendChild(node);
  return node;
}
function resetDom() {
  DOM = {};
  HTML_WRITES = {};
  AUDIO_STARTS = 0;
  BODY = add(null, 'BODY', 'body');
  ACTIVE = BODY;
  var learn = add(BODY, 'gLearn');
  var practice = add(BODY, 'gPractice');
  var done = add(BODY, 'gDone');
  add(BODY, 'gProgress');
  learn.style.display = 'none';
  practice.style.display = 'none';
  done.style.display = 'none';
  add(practice, 'gDrillCard');
  var status = add(practice, 'gStatus');
  status.className = 'sr-only';
  var next = add(practice, 'gDrillNext', 'button');
  add(next, 'gDrillNextLabel', 'span');
  add(done, 'gDoneTitle', 'h2');
  add(done, 'gDoneMsg', 'p');
  add(done, 'gScore', 'span');
  add(done, 'gTotal', 'span');
  add(done, 'gAgain', 'button');
  add(done, 'gReview', 'button');
  add(done, 'gHome', 'button');
  add(BODY, 'gPhase');
  add(BODY, 'gCount');
  add(BODY, 'gFill');
  next.addEventListener('click', GRAMMAR.gDrillAdvance);
  el('gAgain').addEventListener('click', GRAMMAR.gStartPractice);
}
function resetG(topic) {
  Object.keys(G).forEach(function (k) { delete G[k]; });
  var start = freshG();
  Object.keys(start).forEach(function (k) { G[k] = start[k]; });
  G.topic = topic;
}
function choose(id, options, answer) {
  return {
    id: id, type: 'choose', prompt: 'Ja ___ tutaj.', promptEn: 'I live here.',
    options: options.slice(), answer: answer,
    explain: 'Use <b>the authored rule</b>.', full: 'Ja ' + answer + ' tutaj.',
    fullEn: 'I live here.'
  };
}
function topicOf(drills) {
  return { id: 'synthetic-topic', name: 'Synthetic Grammar', teach: [], drills: drills };
}
function start(drills) {
  resetDom();
  resetG(topicOf(drills));
  GRAMMAR.gStartPractice();
}
function optionButtons() { return el('gDrillCard').querySelectorAll('.opt'); }
function byValue(value) {
  var found = optionButtons().filter(function (b) { return b.getAttribute('data-val') === value; });
  return found.length ? found[0] : null;
}
function status() { return el('gStatus'); }
function press(button) {
  if (!button) return;
  button.focus();
  button.click();
}
function handler(button) {
  return button && button._on.click && button._on.click[0];
}
function activateNext() { el('gDrillNext').click(); }

// =========================================================================
// C. INITIAL FOCUS
// =========================================================================
var cInitial = choose('c-initial', ['mieszkam', 'mieszkasz', 'mieszka'], 'mieszkam');
start([cInitial]);
eq('C1 entering a choose drill renders every option', optionButtons().length, cInitial.options.length);
ok('C1 entering a choose drill focuses its first option',
   optionButtons().length > 0 && ACTIVE === optionButtons()[0]);
ok('C1 BODY does not retain focus', ACTIVE !== BODY);
eq('C2 Next begins disabled', el('gDrillNext').disabled, true);
eq('C2 choose state begins ask', G.state, 'ask');

// =========================================================================
// D. WRONG ANSWER
// =========================================================================
var cWrong = choose('c-wrong', ['mieszkam', 'mieszkasz', 'mieszka'], 'mieszkam');
start([cWrong]);
var wrong = byValue('mieszkasz');
press(wrong);
ok('D1 wrong class is applied', wrong && wrong.classList.contains('wrong'));
ok('D1 the wrong option is disabled', wrong && wrong.disabled);
eq('D1 a miss marks the drill attempted', G.attempted, true);
eq('D1 a miss banks false', G.results[0], false);
eq('D1 a miss keeps choose state open', G.state, 'ask');
eq('D1 Next stays disabled', el('gDrillNext').disabled, true);
ok('D2 status names the exact rejected choice', status().textContent.indexOf('mieszkasz') !== -1);
ok('D2 status says the choice is incorrect', /not correct|incorrect/i.test(status().textContent));
ok('D2 status tells the learner to try another answer', /try another answer/i.test(status().textContent));
eq('D2 status is never written through innerHTML', HTML_WRITES.gStatus, undefined);
eq('D3 the wrong option accessible name carries its state',
   wrong ? wrong.accName() : null, 'mieszkasz, incorrect. Try again');
ok('D4 focus moves to the next enabled option',
   wrong && ACTIVE !== BODY && ACTIVE !== wrong && !ACTIVE.disabled);
eq('D4 Next is not the wrong-answer focus target', ACTIVE === el('gDrillNext'), false);

var cWrap = choose('c-wrap', ['dobrze', 'źle-a', 'źle-b'], 'dobrze');
start([cWrap]);
var wrapFrom = byValue('źle-b');
press(wrapFrom);
ok('D5 wrong-answer focus wraps to the first enabled option', ACTIVE === byValue('dobrze'));

var cMany = choose('c-many', ['źle-a', 'źle-b', 'dobrze'], 'dobrze');
start([cMany]);
press(byValue('źle-a'));
ok('D6 first wrong answer does not strand focus on BODY',
   ACTIVE === byValue('źle-b') && ACTIVE !== BODY);
press(byValue('źle-b'));
ok('D6 several wrong answers do not strand focus on BODY',
   ACTIVE === byValue('dobrze') && ACTIVE !== BODY);

// =========================================================================
// E. CORRECT ANSWER
// =========================================================================
var cCorrect = choose('c-correct', ['mieszkam', 'mieszkasz', 'mieszka'], 'mieszkam');
start([cCorrect]);
var right = byValue('mieszkam');
press(right);
ok('E1 correct class is applied', right && right.classList.contains('correct'));
ok('E1 every option is disabled', optionButtons().every(function (b) { return b.disabled; }));
eq('E1 choose state becomes done', G.state, 'done');
eq('E2 a first-attempt success banks true', G.results[0], true);
eq('E2 first-attempt success leaves attempted false', G.attempted, false);
var fb = el('gFbBox');
ok('E3 full Polish feedback still renders', fb && fb.innerHTML.indexOf(cCorrect.full) !== -1);
ok('E3 English translation still renders', fb && fb.innerHTML.indexOf(cCorrect.fullEn) !== -1);
ok('E3 authored explanation markup still renders',
   fb && fb.innerHTML.indexOf(cCorrect.explain) !== -1 &&
   fb.innerHTML.indexOf('<b>') !== -1);
ok('E3 feedback box still opens visibly', fb && fb.classList.contains('show'));
eq('E3 one mini-audio button remains', fb ? fb.querySelectorAll('.mini-audio').length : 0, 1);
eq('E3 success does not autoplay', AUDIO_STARTS, 0);
ok('E4 status explicitly begins with Correct', /^Correct\b/.test(status().textContent));
ok('E4 status says Next is ready', /Next is ready/.test(status().textContent));
var statusPl = status().children.filter(function (n) {
  return n.getAttribute && n.getAttribute('lang') === 'pl';
});
eq('E4 correct answer appears in one lang=pl node', statusPl.length, 1);
eq('E4 the lang=pl node contains the exact Polish answer',
   statusPl.length ? statusPl[0].textContent : null, cCorrect.answer);
eq('E5 the correct option accessible name carries its state',
   right ? right.accName() : null, 'mieszkam, correct');
eq('E6 Next is enabled', el('gDrillNext').disabled, false);
ok('E6 focus lands on enabled Next', ACTIVE === el('gDrillNext') && !ACTIVE.disabled);

start([cCorrect]);
press(byValue('mieszkasz'));
press(byValue('mieszkam'));
eq('E7 wrong then correct remains false', G.results[0], false);
eq('E7 wrong then correct settles state', G.state, 'done');

// =========================================================================
// F. SETTLED GUARD
// =========================================================================
start([cCorrect]);
var guardedWrong = byValue('mieszkasz');
var guardedRight = byValue('mieszkam');
press(guardedRight);
var beforeResult = G.results[0];
var beforeAttempted = G.attempted;
var beforeQueue = JSON.stringify(G.queue);
var beforeFeedback = el('gFbBox').innerHTML;
var beforeFeedbackWrites = HTML_WRITES.gFbBox;
var beforeStatus = status().textContent;
var beforeStatusChildren = status().children;
var beforeFocus = ACTIVE;
var beforeNextDisabled = el('gDrillNext').disabled;
var wrongDirect = handler(guardedWrong);
if (wrongDirect) wrongDirect({});
eq('F1 direct post-success invocation cannot change result', G.results[0], beforeResult);
eq('F1 direct post-success invocation cannot change attempted state', G.attempted, beforeAttempted);
eq('F1 direct post-success invocation cannot change queue', JSON.stringify(G.queue), beforeQueue);
eq('F1 direct post-success invocation cannot change feedback', el('gFbBox').innerHTML, beforeFeedback);
eq('F1 direct post-success invocation cannot change status', status().textContent, beforeStatus);
ok('F1 direct post-success invocation does not rebuild status nodes',
   status().children === beforeStatusChildren);
ok('F1 direct post-success invocation cannot change focus', ACTIVE === beforeFocus);
eq('F1 direct post-success invocation cannot change Next', el('gDrillNext').disabled, beforeNextDisabled);
ok('F1 direct post-success invocation cannot mark another option wrong',
   guardedWrong && !guardedWrong.classList.contains('wrong'));
var rightDirect = handler(guardedRight);
if (rightDirect) rightDirect({});
eq('F2 repeated direct success cannot rebuild feedback', HTML_WRITES.gFbBox, beforeFeedbackWrites);

// =========================================================================
// G. SAFE OPTION CONSTRUCTION
// =========================================================================
var WEIRD = [
  "apostrophe's",
  'double "quote"',
  'fish & chips',
  '2 < 3 > 1',
  '<em>"tak" & \'nie\'</em>',
  'zażółć gęślą'
];
var cWeird = choose('c-weird', WEIRD, WEIRD[4]);
start([cWeird]);
eq('G1 every weird option survives construction', optionButtons().length, WEIRD.length);
eq('G1 every displayed option is exact authored text',
   optionButtons().map(function (b) { return b.textContent; }), WEIRD);
eq('G1 exact option identities survive',
   optionButtons().map(function (b) { return b.getAttribute('data-val'); }), WEIRD);
var htmlLooking = byValue(WEIRD[4]);
ok('G1 HTML-looking option is present by exact identity', !!htmlLooking);
eq('G1 HTML-looking option creates no child markup',
   htmlLooking ? htmlLooking.children.length : null, 0);
eq('G1 HTML-looking option innerHTML remains empty',
   htmlLooking ? htmlLooking.innerHTML : null, '');
if (htmlLooking) press(htmlLooking);
eq('G2 weird correct option can be selected', G.results[0], true);
ok('G2 weird correct option reaches the status literally',
   status().textContent.indexOf(WEIRD[4]) !== -1);
ok('G3 shipping code creates option buttons with createElement',
   hasCode(CODE_RENDER_CHOOSE, 'document.createElement("button")'));
ok('G3 shipping code writes option labels with textContent',
   /\.textContent\s*=\s*[A-Za-z_$]/.test(CODE_RENDER_CHOOSE));
ok('G3 shipping code does not interpolate an option button as HTML',
   !/<button[^'"]*["'][^;\n]*\+\s*[A-Za-z_$]/.test(CODE_RENDER_CHOOSE) &&
   CODE_RENDER_CHOOSE.indexOf("'<button") === -1 &&
   CODE_RENDER_CHOOSE.indexOf('"<button') === -1);
eq('G3 options are shuffled exactly once', countOf(CODE_RENDER_CHOOSE, 'gShuffle(c.options)'), 1);

// =========================================================================
// H. ADVANCE AND REQUEUE
// =========================================================================
var hOne = choose('h-one', ['a1', 'a2'], 'a1');
var hTwo = choose('h-two', ['b1', 'b2'], 'b1');
start([hOne, hTwo]);
press(byValue('a1'));
eq('H1 a non-final clean answer says Next', el('gDrillNextLabel').textContent, 'Next');
activateNext();
eq('H1 clean success advances without requeue', G.queue.length, 2);
eq('H1 clean success advances to the next drill', G.di, 1);
ok('H1 next choose drill focuses its first option', ACTIVE === optionButtons()[0] && ACTIVE !== BODY);

start([hOne, hTwo]);
press(byValue('a2'));
press(byValue('a1'));
eq('H2 a missed original still predicts a future retry', el('gDrillNextLabel').textContent, 'Next');
activateNext();
eq('H2 wrong then correct appends exactly one requeued copy', G.queue.length, 3);
ok('H2 requeued copy is marked', G.queue[2]._requeue === true && G.queue[2].id === hOne.id);
press(byValue('b1'));
eq('H3 last original says Next while retry remains', el('gDrillNextLabel').textContent, 'Next');
activateNext();
ok('H3 requeued choose drill focuses its first option', ACTIVE === optionButtons()[0] && ACTIVE !== BODY);
press(byValue('a1'));
eq('H3 final retry says See results', el('gDrillNextLabel').textContent, 'See results');
activateNext();
eq('H3 a requeued drill cannot create another requeue', G.queue.length, 3);
eq('H3 requeued success stays excluded from score', el('gScore').textContent, '1');
eq('H3 original total stays unchanged', el('gTotal').textContent, '2');

start([hOne]);
press(byValue('a1'));
eq('H4 final clean answer says See results', el('gDrillNextLabel').textContent, 'See results');

// =========================================================================
// I. COMPLETION
// =========================================================================
start([hOne]);
press(byValue('a1'));
ok('I1 final answer enables and focuses See results',
   el('gDrillNextLabel').textContent === 'See results' &&
   !el('gDrillNext').disabled && ACTIVE === el('gDrillNext'));
activateNext();
eq('I1 done screen is visible', el('gDone').style.display, 'flex');
eq('I1 practice screen is hidden', el('gPractice').style.display, 'none');
ok('I2 completion heading receives focus', ACTIVE === el('gDoneTitle') && ACTIVE !== BODY);
eq('I3 perfect score arithmetic is unchanged', el('gScore').textContent, '1');
eq('I3 original total arithmetic is unchanged', el('gTotal').textContent, '1');
eq('I3 perfect completion wording is unchanged',
   el('gDoneMsg').textContent, 'Every answer right on the first try. This is clicking.');
el('gAgain').click();
eq('I4 Practice again resets choose state', G.state, 'ask');
eq('I4 Practice again resets the result list', G.results.length, 0);
ok('I4 Practice again focuses the first choose option',
   optionButtons().length > 0 && ACTIVE === optionButtons()[0] && ACTIVE !== BODY);

// =========================================================================
// J. STATUS LIFECYCLE
// =========================================================================
start([hOne, hTwo]);
eq('J1 a new drill starts with an empty status', status().textContent, '');
press(byValue('a2'));
var wrongVerdict = status().textContent;
ok('J1 wrong verdict is present before correction', /not correct|incorrect/i.test(wrongVerdict));
press(byValue('a1'));
ok('J1 correct replaces rather than appends to the wrong verdict',
   /^Correct\b/.test(status().textContent) &&
   status().textContent.indexOf(wrongVerdict) === -1);
activateNext();
eq('J2 advancing clears the prior result', status().textContent, '');
eq('J2 status still has no innerHTML writes', HTML_WRITES.gStatus, undefined);
eq('J3 Grammar adds only one verdict status region', countOf(GRAMMAR_SCREEN, 'role="status"'), 1);
ok('J3 choose feedback is ordinary visible content', CODE_RENDER_CHOOSE.indexOf('aria-live') === -1);
['gSetStatus', 'gAnnounceWrong', 'gAnnounceCorrect'].forEach(function (name) {
  ok('J4 ' + name + ' never uses innerHTML', codeOnly(GSRC[name]).indexOf('innerHTML') === -1);
});
ok('J4 status writer uses safe DOM APIs',
   /textContent|createTextNode|createElement|appendChild|replaceChildren/.test(codeOnly(GSRC.gSetStatus)));
ok('J4 correct answer is created as its own lang=pl element',
   codeOnly(GSRC.gAnnounceCorrect).indexOf('createElement') !== -1 &&
   codeOnly(GSRC.gAnnounceCorrect).indexOf('lang') !== -1);

// =========================================================================
// K. SOURCE WIRING
// =========================================================================
var CODE_G = {};
GNAMES.forEach(function (name) { CODE_G[name] = codeOnly(GSRC[name]); });
ok('K1 choose handler has an explicit ask-state guard',
   hasCode(CODE_G.gRenderChoose, 'if(G.state!=="ask")return;') ||
   hasCode(CODE_G.gRenderChoose, "if(G.state!=='ask')return;"));
ok('K1 each new drill resets state to ask',
   hasCode(CODE_G.gRenderDrill, 'G.state="ask"') ||
   hasCode(CODE_G.gRenderDrill, "G.state='ask'"));
ok('K1 correct choice settles state to done',
   hasCode(CODE_G.gRenderChoose, 'G.state="done"') ||
   hasCode(CODE_G.gRenderChoose, "G.state='done'"));
var WRONG_AT = CODE_G.gRenderChoose.indexOf('classList.add("wrong")');
var CORRECT_AT = CODE_G.gRenderChoose.indexOf('classList.add("correct")');
var WRONG_TAIL = WRONG_AT === -1 ? '' : CODE_G.gRenderChoose.slice(WRONG_AT);
var CORRECT_TAIL = CORRECT_AT === -1 ? '' :
  CODE_G.gRenderChoose.slice(CORRECT_AT, WRONG_AT === -1 ? CODE_G.gRenderChoose.length : WRONG_AT);
ok('K1 wrong path leaves state open',
   WRONG_TAIL.indexOf('G.state="done"') === -1 && WRONG_TAIL.indexOf("G.state='done'") === -1);
ok('K2 safe option construction uses createElement + textContent + exact identity',
   hasCode(CODE_G.gRenderChoose, 'document.createElement("button")') &&
   CODE_G.gRenderChoose.indexOf('textContent') !== -1 &&
   (CODE_G.gRenderChoose.indexOf('data-val') !== -1 ||
    CODE_G.gRenderChoose.indexOf('dataset') !== -1 ||
    CODE_G.gRenderChoose.indexOf('addEventListener') !== -1));
var LAST_APPEND = CODE_G.gRenderChoose.lastIndexOf('appendChild');
var LAST_LISTENER = CODE_G.gRenderChoose.lastIndexOf('addEventListener');
var LAST_INITIAL_FOCUS = CODE_G.gRenderChoose.lastIndexOf('.focus(');
ok('K2 initial focus occurs after all option construction and listeners',
   LAST_APPEND !== -1 && LAST_LISTENER !== -1 && LAST_INITIAL_FOCUS > LAST_APPEND &&
   LAST_INITIAL_FOCUS > LAST_LISTENER);
var W_DISABLE = WRONG_TAIL.indexOf('disabled=true');
var W_ANNOUNCE = WRONG_TAIL.indexOf('gAnnounceWrong');
var W_FOCUS = WRONG_TAIL.indexOf('gFocusNextOption');
ok('K3 wrong disables before announcing', W_DISABLE !== -1 && W_DISABLE < W_ANNOUNCE);
ok('K3 wrong announces before moving focus',
   W_ANNOUNCE !== -1 && W_FOCUS !== -1 && W_ANNOUNCE < W_FOCUS);
var C_MARK = CORRECT_TAIL.indexOf('classList.add("correct")');
var C_DISABLE = CORRECT_TAIL.indexOf('disabled=true');
var C_BANK = CORRECT_TAIL.indexOf('G.results');
var C_FEEDBACK = CORRECT_TAIL.indexOf('gChooseFeedback');
var C_LABEL = CORRECT_TAIL.indexOf('gUpdateNextLabel');
var C_ANNOUNCE = CORRECT_TAIL.indexOf('gAnnounceCorrect');
var C_OPEN = CORRECT_TAIL.indexOf('disabled=false');
var C_FOCUS = CORRECT_TAIL.indexOf('.focus(');
ok('K4 correct path preserves mark/disable/bank/feedback/label/announce/open/focus order',
   C_MARK !== -1 && C_MARK < C_DISABLE && C_DISABLE < C_BANK && C_BANK < C_FEEDBACK &&
   C_FEEDBACK < C_LABEL && C_LABEL < C_ANNOUNCE && C_ANNOUNCE < C_OPEN && C_OPEN < C_FOCUS);
ok('K4 correct focus occurs only after Next is enabled', C_OPEN !== -1 && C_OPEN < C_FOCUS);
ok('K5 gShowDone shows done before focusing its heading',
   hasCode(CODE_G.gShowDone, 'gPhaseView("done")') &&
   CODE_G.gShowDone.indexOf('gPhaseView') < CODE_G.gShowDone.indexOf('gDoneTitle') &&
   CODE_G.gShowDone.indexOf('.focus(') !== -1);
ok('K6 gDrillAdvance retains the existing one-requeue rule',
   hasCode(CODE_G.gDrillAdvance, 'if(G.results[G.di]===false&&!c._requeue)') &&
   hasCode(CODE_G.gDrillAdvance, 'G.queue.push(Object.assign({},c,{_requeue:true}))') &&
   countOf(CODE_G.gDrillAdvance, 'G.queue.push(') === 1);
ok('K6 gDrillAdvance retains the same advance-or-done branch',
   hasCode(CODE_G.gDrillAdvance,
     'if(G.di<G.queue.length-1){G.di++;gRenderDrill();}else gShowDone();'));
ok('K6 gUpdateNextLabel retains future-retry prediction',
   hasCode(CODE_G.gUpdateNextLabel,
     'const willRequeue=G.results[G.di]===false&&!G.queue[G.di]._requeue'));
ok('K7 build path is not wired to Phase 4G state, verdict or focus helpers',
   ['gStatus', 'gSetStatus', 'gAnnounce', 'gFocusNextOption', 'G.state'].every(function (t) {
     return CODE_G.gRenderBuild.indexOf(t) === -1 &&
            CODE_G.gPaintBuild.indexOf(t) === -1 &&
            CODE_G.gCheckBuild.indexOf(t) === -1;
   }));
ok('K7 Grammar interaction functions add no persistence behavior',
   GNAMES.every(function (name) {
     return !/localStorage|saveV2|loadV2|progress/.test(CODE_G[name]);
   }));
ok('K7 teaching feedback keeps its deliberate markup path',
   CODE_G.gChooseFeedback.indexOf('innerHTML') !== -1 &&
   CODE_G.gChooseFeedback.indexOf('c.explain') !== -1);
eq('K7 no render/verdict/focus path autoplays',
   ['gRenderDrill', 'gRenderChoose', 'gSetStatus', 'gAnnounceWrong',
    'gAnnounceCorrect', 'gFocusNextOption', 'gChooseFeedback', 'gShowDone']
     .filter(function (name) {
       return /speakText|speakCardMain|new Audio|SpeechSynthesisUtterance/.test(CODE_G[name]);
     }), []);

info('assertions drive the shipping Grammar functions extracted from index.html');
info('fake DOM models disabled-focus -> BODY, hidden-focus no-op, textContent vs innerHTML, and aria-label names');

console.log('Grammar interaction tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
