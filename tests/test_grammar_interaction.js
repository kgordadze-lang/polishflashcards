// Behavioral tests for the shipping Grammar choose- and build-drill interactions.
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
function applyShippingGrammarMix(levels) {
  var anchor = INDEX.indexOf(
    'const gc = LEVELS.find(lv => lv.level === "Grammar Cases");'
  );
  if (anchor === -1) throw new Error('extract: shipping Grammar Mix injection not found');
  var start = INDEX.lastIndexOf('(function(){', anchor);
  var end = INDEX.indexOf('})();', anchor);
  if (start === -1 || end === -1) {
    throw new Error('extract: shipping Grammar Mix injection is incomplete');
  }
  (new Function('LEVELS', INDEX.slice(start, end + 5)))(levels);
}
applyShippingGrammarMix(GRAMMAR_LEVELS);
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
var EXPECTED_ACCEPTED_ORDERS = {
  'grammar-cases-vocative-004': [['Chodź', 'tutaj', 'Piotrze']],
  'grammar-cases-vocative-008': [['Chodźcie', 'tu', 'dzieci']],
  'grammar-cases-vocative-011': [['Tęsknię', 'za', 'tobą', 'babciu']],
  'grammar-cases-vocative-014': [['Dziękuję', 'kochani']],
  'verbs-future-tense-005': [['Wieczorem', 'napiszę', 'do', 'ciebie']],
  'verbs-verbs-of-motion-006': [['Proszę', 'wejdź']]
};
var EXPECTED_ACCEPTED_IDS = Object.keys(EXPECTED_ACCEPTED_ORDERS).sort();
var EXPLICITLY_NON_ACCEPTED_IDS = [
  'people-numbers-every-all-011',
  'verbs-imperative-007',
  'grammar-cases-locative-013',
  'verbs-reflexive-006',
  'grammar-cases-instrumental-013'
];
function usableString(v) { return typeof v === 'string' && v.trim().length > 0; }
function optionNorm(v) {
  return v.normalize('NFC').trim().toLocaleLowerCase().replace(/\s+/g, ' ');
}
function drillById(id) {
  var found = DRILLS.filter(function (entry) { return entry.drill.id === id; });
  return found.length ? found[0].drill : null;
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
ok('B2 build gFbBox is not a competing live region',
   CODE_RENDER_BUILD.indexOf('gFbBox') !== -1 &&
   CODE_RENDER_BUILD.indexOf('aria-live') === -1 &&
   CODE_RENDER_BUILD.indexOf('role="status"') === -1);
ok('B2 build gFbBox remains the visible feedback box',
   CODE_RENDER_BUILD.indexOf('gFbBox') !== -1 &&
   CODE_RENDER_BUILD.indexOf('fb-box') !== -1);
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
    var focused = ACTIVE;
    while (focused && focused !== this) focused = focused.parentNode;
    if (focused === this && ACTIVE !== this) ACTIVE = BODY;
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
      var rowPoolIds = ['gBuildRow', 'gBuildPool'];
      rowPoolIds.forEach(function (id) {
        var rm = this._html.match(new RegExp(
          '<div\\b([^>]*\\bid\\s*=\\s*"' + id + '"[^>]*)>'
        ));
        if (rm) {
          var box = new FakeEl('div');
          parseAttrs(rm[1], box);
          this.appendChild(register(box));
        }
      }, this);
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
    } else if (this.id === 'gBuildRow' || this.id === 'gBuildPool') {
      var wr = /<button\b([^>]*)>([\s\S]*?)<\/button>/g, wm;
      while ((wm = wr.exec(this._html)) !== null) {
        var chip = new FakeEl('button');
        parseAttrs(wm[1], chip);
        if (/\bdisabled(?:\s|>|$)/.test(wm[1])) chip.disabled = true;
        chip._html = wm[2];
        chip._htmlText = decodeHtmlText(wm[2]);
        this.appendChild(register(chip));
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
      if (hit && selector.indexOf(':not(.used)') !== -1 && classHas(child, 'used')) hit = false;
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
  'gBuildTokenKey',
  'gPhaseView', 'gStartPractice', 'gUpdateNextLabel', 'gRenderDrill',
  'gRenderChoose', 'gSetStatus', 'gAnnounceWrong', 'gAnnounceCorrect',
  'gAnnounceBuildWrong', 'gAnnounceBuildIncomplete', 'gFocusNextOption',
  'gChooseFeedback', 'gRenderBuild', 'gPaintBuild', 'gCheckBuild',
  'gDrillAdvance', 'gShowDone'
];
var GSRC = {};
GNAMES.forEach(function (name) {
  try { GSRC[name] = extractFunction(INDEX, name); }
  catch (_) {
    GSRC[name] = name === 'gBuildTokenKey'
      ? 'function gBuildTokenKey(token){return token;}'
      : 'function ' + name + '(){}';
  }
});
var SHUFFLE_SRC = extractFunction(INDEX, 'gShuffle');
var SAMPLE_MIX_SRC = extractFunction(INDEX, 'gSampleMix');
var AUDIO_STARTS = 0;
function speakText() { AUDIO_STARTS++; }
function speakCardMain() { AUDIO_STARTS++; }
function stopAllAudio() {}
function identityShuffle(a) { return a.slice(); }
function noMix() {}
function immediateTimer(fn) { fn(); }
function grammarRuntime(shuffle, sampleMix) {
  return (new Function(
    '$', 'document', 'G', 'G_AUDIO', 'gShuffle', 'gSampleMix', 'setTimeout',
    GNAMES.map(function (n) { return GSRC[n]; }).join('\n') +
    '\nreturn {' + GNAMES.map(function (n) { return n + ':' + n; }).join(',') + '};'
  ))(el, fakeDocument, G, '<svg class="audio-icon"></svg>',
     shuffle, sampleMix || noMix, immediateTimer);
}
function controlledShippingShuffle(initialValues) {
  var values = initialValues ? initialValues.slice() : [0];
  var at = 0;
  var calls = [];
  var shipping = (new Function(
    'Math', SHUFFLE_SRC + '\nreturn gShuffle;'
  ))({
    floor: Math.floor,
    random: function () {
      var value = values.length ? values[at % values.length] : 0;
      at++;
      return value;
    }
  });
  function instrumented(a) {
    var out = shipping(a);
    calls.push({ input: a, output: out.slice() });
    return out;
  }
  instrumented.use = function (nextValues) {
    values = nextValues.slice();
    at = 0;
  };
  instrumented.clear = function () {
    calls.length = 0;
    at = 0;
  };
  instrumented.calls = calls;
  return instrumented;
}
function shippingSampleMix(levels, shuffle) {
  return (new Function(
    'LEVELS', 'gShuffle', SAMPLE_MIX_SRC + '\nreturn gSampleMix;'
  ))(levels, shuffle);
}
function shippingStartOnly(shuffle, sampleMix, events) {
  return (new Function(
    'G', 'gShuffle', 'gSampleMix', 'gPhaseView', 'gRenderDrill',
    GSRC.gStartPractice + '\nreturn gStartPractice;'
  ))(
    G, shuffle, sampleMix || noMix,
    function (phase) { events.push('phase:' + phase); },
    function () {
      events.push('render:' + (G.queue[G.di] && G.queue[G.di].id));
    }
  );
}
var GRAMMAR = grammarRuntime(identityShuffle, noMix);

function add(parent, id, tag) {
  var node = new FakeEl(tag || 'div');
  node.id = id;
  DOM[id] = node;
  if (parent) parent.appendChild(node);
  return node;
}
function resetDom(runtime) {
  var activeRuntime = runtime || GRAMMAR;
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
  next.addEventListener('click', activeRuntime.gDrillAdvance);
  el('gAgain').addEventListener('click', activeRuntime.gStartPractice);
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
function build(id, answer, acceptedOrders) {
  var drill = {
    id: id, type: 'build', promptEn: 'Build the sentence.',
    answer: answer.slice(),
    explain: 'Keep <b>the authored order</b>.',
    full: answer.join(' '), fullEn: 'The built sentence.'
  };
  if (acceptedOrders !== undefined) {
    drill.acceptedOrders = acceptedOrders.map(function (order) { return order.slice(); });
  }
  return drill;
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
function rowButtons() { return el('gBuildRow').querySelectorAll('.wchip'); }
function poolButtons() { return el('gBuildPool').querySelectorAll('.wchip'); }
function tileById(buttons, id) {
  var found = buttons.filter(function (b) { return b.getAttribute('data-id') === id; });
  return found.length ? found[0] : null;
}
function rowTile(id) { return tileById(rowButtons(), id); }
function poolTile(id) { return tileById(poolButtons(), id); }
function unusedPoolButtons() {
  return poolButtons().filter(function (b) { return !classHas(b, 'used'); });
}
function placeTile(id) { press(poolTile(id)); }
function placeTiles(ids) { ids.forEach(placeTile); }
function buildTokenKey(token) { return GRAMMAR.gBuildTokenKey(token); }
function keyedOrder(order) { return order.map(buildTokenKey); }
function keyedMultiset(order) { return keyedOrder(order).slice().sort(); }
function placeWords(words) {
  words.forEach(function (word) {
    var key = buildTokenKey(word);
    var tile = G.build.pool.filter(function (candidate) {
      return !candidate.used && buildTokenKey(candidate.w) === key;
    })[0];
    if (tile) placeTile(tile.id);
  });
}
function submitWords(words) {
  placeWords(words);
  press(el('gCheckBtn'));
}
function authoredPoolIds() { return G.build.pool.map(function (t) { return t.id; }); }
function solveBuildExact() {
  placeTiles(authoredPoolIds());
  press(el('gCheckBtn'));
}
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
// A4. PHASE 4J AUTHORED ACCEPTED-ORDER CONTRACT
// =========================================================================
var ACTUAL_ACCEPTED_ORDERS = {};
DRILLS.forEach(function (entry) {
  if (Object.prototype.hasOwnProperty.call(entry.drill, 'acceptedOrders')) {
    ACTUAL_ACCEPTED_ORDERS[entry.drill.id] = entry.drill.acceptedOrders;
  }
});
eq('A4 exactly the six reviewed drills carry their exact accepted orders',
   ACTUAL_ACCEPTED_ORDERS, EXPECTED_ACCEPTED_ORDERS);
eq('A4 no unexpected drill carries acceptedOrders',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).sort(), EXPECTED_ACCEPTED_IDS);
ok('A4 every acceptedOrders field belongs to a build drill',
   DRILLS.filter(function (entry) {
     return Object.prototype.hasOwnProperty.call(entry.drill, 'acceptedOrders');
   }).every(function (entry) { return entry.drill.type === 'build'; }));
ok('A4 every acceptedOrders field is a non-empty array',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).every(function (id) {
     return Array.isArray(ACTUAL_ACCEPTED_ORDERS[id]) &&
            ACTUAL_ACCEPTED_ORDERS[id].length > 0;
   }));
ok('A4 every accepted order is a non-empty token array',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).every(function (id) {
     return ACTUAL_ACCEPTED_ORDERS[id].every(function (order) {
       return Array.isArray(order) && order.length > 0;
     });
   }));
ok('A4 every accepted token is a raw non-empty string',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).every(function (id) {
     return ACTUAL_ACCEPTED_ORDERS[id].every(function (order) {
       return order.every(usableString);
     });
   }));
ok('A4 every accepted order has the canonical token count',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).every(function (id) {
     var drill = drillById(id);
     return ACTUAL_ACCEPTED_ORDERS[id].every(function (order) {
       return drill && order.length === drill.answer.length;
     });
   }));
ok('A4 every accepted order preserves the narrow keyed token multiset',
   EXPECTED_ACCEPTED_IDS.every(function (id) {
     var drill = drillById(id);
     return drill && EXPECTED_ACCEPTED_ORDERS[id].every(function (order) {
       return JSON.stringify(keyedMultiset(order)) ===
              JSON.stringify(keyedMultiset(drill.answer));
     });
   }));
ok('A4 every accepted order changes tile order, not capitalization alone',
   EXPECTED_ACCEPTED_IDS.every(function (id) {
     var drill = drillById(id);
     return drill && EXPECTED_ACCEPTED_ORDERS[id].every(function (order) {
       return JSON.stringify(keyedOrder(order)) !== JSON.stringify(keyedOrder(drill.answer));
     });
   }));
ok('A4 no accepted order duplicates another keyed order',
   Object.keys(ACTUAL_ACCEPTED_ORDERS).every(function (id) {
     var keyed = ACTUAL_ACCEPTED_ORDERS[id].map(function (order) {
       return JSON.stringify(keyedOrder(order));
     });
     return new Set(keyed).size === keyed.length;
   }));
ok('A4 all six alternatives contain the required sentence-position case change',
   EXPECTED_ACCEPTED_IDS.every(function (id) {
     var drill = drillById(id);
     var accepted = EXPECTED_ACCEPTED_ORDERS[id][0];
     return drill && accepted.some(function (surface) {
       return drill.answer.indexOf(surface) === -1 &&
              drill.answer.some(function (canonical) {
                return buildTokenKey(canonical) === buildTokenKey(surface);
              });
     });
   }));
ok('A4 explicitly excluded drills remain free of acceptedOrders',
   EXPLICITLY_NON_ACCEPTED_IDS.every(function (id) {
     var drill = drillById(id);
     return drill && !Object.prototype.hasOwnProperty.call(drill, 'acceptedOrders');
   }));

eq('A5 narrow key equates chodź only across first-letter case',
   buildTokenKey('chodź'), buildTokenKey('Chodź'));
eq('A5 narrow key equates Dzieci only across first-letter case',
   buildTokenKey('Dzieci'), buildTokenKey('dzieci'));
eq('A5 narrow key equates Napiszę only across first-letter case',
   buildTokenKey('Napiszę'), buildTokenKey('napiszę'));
ok('A5 changed diacritic remains a different tile',
   buildTokenKey('tobą') !== buildTokenKey('toba'));
ok('A5 changed non-initial spelling remains a different tile',
   buildTokenKey('chodź') !== buildTokenKey('chodz'));
ok('A5 changed punctuation remains a different tile',
   buildTokenKey('proszę!') !== buildTokenKey('Proszę?'));
ok('A5 trailing whitespace remains a different tile',
   buildTokenKey('do') !== buildTokenKey('Do '));
ok('A5 a different word remains a different tile',
   buildTokenKey('wejdź') !== buildTokenKey('wejść'));
eq('A5 non-string tile values pass through without normalization',
   [buildTokenKey(null), buildTokenKey(7)], [null, 7]);

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
ok('K7 build initial paint carries an explicit first-pool focus intent',
   hasCode(CODE_G.gRenderBuild, 'gPaintBuild({kind:"first-pool"})') ||
   hasCode(CODE_G.gRenderBuild, "gPaintBuild({kind:'first-pool'})"));
ok('K7 build placement and removal repaint with stable-id focus intents',
   CODE_G.gPaintBuild.indexOf('data-id') !== -1 &&
   CODE_G.gPaintBuild.indexOf('after-pool') !== -1 &&
   CODE_G.gPaintBuild.indexOf('pool-id') !== -1);
eq('K7 both build tile handlers carry an ask-state guard',
   (CODE_G.gPaintBuild.match(/G\.state\s*!==\s*["']ask["']/g) || []).length, 2);
ok('K7 gCheckBuild carries an ask-state guard',
   hasCode(CODE_G.gCheckBuild, 'if(G.state!=="ask")return;') ||
   hasCode(CODE_G.gCheckBuild, "if(G.state!=='ask')return;"));
ok('K7 canonical answer is first and acceptedOrders is read only as an array',
   hasCode(CODE_G.gCheckBuild, 'const validOrders=[c.answer].concat(accepted)') &&
   hasCode(CODE_G.gCheckBuild, 'Array.isArray(c.acceptedOrders)'));
ok('K7 accepted-order matching uses exact ordered narrow token keys',
   CODE_G.gCheckBuild.indexOf('gBuildTokenKey') !== -1 &&
   CODE_G.gCheckBuild.indexOf('.find(') !== -1 &&
   CODE_G.gCheckBuild.indexOf('.every(') !== -1);
ok('K7 comparator introduces no broad answer normalization or permutations',
   !/\.trim\(|normalize\(|sort\(|permut/i.test(CODE_G.gCheckBuild) &&
   !/toLocaleLowerCase|toLowerCase/.test(CODE_G.gCheckBuild));
ok('K7 correct build settlement sets done and announces the full Polish sentence',
   (hasCode(CODE_G.gCheckBuild, 'G.state="done"') ||
    hasCode(CODE_G.gCheckBuild, "G.state='done'")) &&
   hasCode(CODE_G.gCheckBuild, 'gAnnounceCorrect(c.full)'));
ok('K7 wrong build settlement explicitly stays ask and announces its verdict',
   (hasCode(CODE_G.gCheckBuild, 'G.state="ask"') ||
    hasCode(CODE_G.gCheckBuild, "G.state='ask'")) &&
   CODE_G.gCheckBuild.indexOf('gAnnounceBuildWrong') !== -1);
ok('K7 incomplete build announcement uses the safe status helper',
   CODE_G.gAnnounceBuildIncomplete.indexOf('gSetStatus') !== -1 &&
   CODE_G.gAnnounceBuildIncomplete.indexOf('innerHTML') === -1 &&
   /sentence is incomplete/i.test(CODE_G.gAnnounceBuildIncomplete));
ok('K7 incomplete build branch checks row length against the authored answer',
   hasCode(CODE_G.gCheckBuild,
     'const incomplete=G.build.row.length<c.answer.length'));
ok('K7 wrong-position guidance scores every valid order and keeps canonical ties',
   CODE_G.gCheckBuild.indexOf('validOrders') !== -1 &&
   CODE_G.gCheckBuild.indexOf('matches') !== -1 &&
   CODE_G.gCheckBuild.indexOf('>bestMatches') !== -1 &&
   CODE_G.gCheckBuild.indexOf('>=bestMatches') === -1);
ok('K7 incomplete build branch follows the first-mismatch branch',
   CODE_G.gCheckBuild.indexOf('if(firstBad)') !== -1 &&
   CODE_G.gCheckBuild.indexOf('else if(incomplete)') >
     CODE_G.gCheckBuild.indexOf('if(firstBad)'));
ok('K7 incomplete build branch announces and focuses the first unused pool tile',
   CODE_G.gCheckBuild.indexOf('gAnnounceBuildIncomplete') !== -1 &&
   CODE_G.gCheckBuild.indexOf('kind:"first-pool"') !== -1 &&
   CODE_G.gCheckBuild.indexOf('guideOrder:guideOrder') !== -1);
ok('K7 wrong build path labels and focuses mismatched row tiles',
   CODE_G.gCheckBuild.indexOf('aria-label') !== -1 &&
   /wrong position/i.test(CODE_G.gCheckBuild) &&
   CODE_G.gCheckBuild.indexOf('.focus(') !== -1);
ok('K8 locked build tiles disable pointer events',
   cssBlocks('.build-row.locked .wchip').some(function (b) {
     return /pointer-events\s*:\s*none/.test(b.body);
   }));
ok('K8 bad build tiles expose a visible non-colour Wrong position marker',
   cssBlocks('.wchip.bad::after').some(function (b) {
     return /content\s*:\s*"[^"]*Wrong position/i.test(b.body);
   }));
ok('K8 reduced motion disables the Grammar build-row shake',
   /@media\s*\(prefers-reduced-motion\s*:\s*reduce\)\s*\{[\s\S]*?\.build-row\.shake\s*\{[^}]*animation\s*:\s*none/.test(STYLE));
ok('K8 Conversations reply-option shake remains enabled',
   cssBlocks('.reply-opt.shake').some(function (b) {
     return /animation\s*:\s*shake/.test(b.body) &&
            !/animation\s*:\s*none/.test(b.body);
   }));
ok('K8 build feedback is ordinary visible content',
   CODE_G.gRenderBuild.indexOf('gFbBox') !== -1 &&
   CODE_G.gRenderBuild.indexOf('aria-live') === -1 &&
   CODE_G.gRenderBuild.indexOf('role="status"') === -1);
ok('K9 Grammar interaction functions add no persistence behavior',
   GNAMES.every(function (name) {
     return !/localStorage|saveV2|loadV2|progress/.test(CODE_G[name]);
   }));
ok('K9 teaching feedback keeps its deliberate markup path',
   CODE_G.gChooseFeedback.indexOf('innerHTML') !== -1 &&
   CODE_G.gChooseFeedback.indexOf('c.explain') !== -1);
eq('K9 no render/verdict/focus path autoplays',
   ['gRenderDrill', 'gRenderChoose', 'gSetStatus', 'gAnnounceWrong',
    'gAnnounceCorrect', 'gAnnounceBuildWrong', 'gAnnounceBuildIncomplete',
    'gFocusNextOption', 'gChooseFeedback', 'gRenderBuild', 'gPaintBuild',
    'gCheckBuild', 'gShowDone']
     .filter(function (name) {
       return /speakText|speakCardMain|new Audio|SpeechSynthesisUtterance/.test(CODE_G[name]);
     }), []);

// =========================================================================
// L. BUILD INITIAL STATE
// =========================================================================
var bInitial = build('b-initial', ['Ala', 'ma', 'kota']);
start([bInitial]);
var bInitialIds = authoredPoolIds();
eq('L1 a build drill renders every pool tile', poolButtons().length, bInitial.answer.length);
eq('L1 a build drill starts with an empty row', rowButtons().length, 0);
ok('L1 the first available pool tile receives focus',
   ACTIVE === poolTile(bInitialIds[0]) && ACTIVE !== BODY);
eq('L2 build Check begins disabled', el('gCheckBtn').disabled, true);
eq('L2 build Next begins disabled', el('gDrillNext').disabled, true);
eq('L2 build state begins ask', G.state, 'ask');
eq('L2 build status begins empty', status().textContent, '');
eq('L2 build render does not autoplay', AUDIO_STARTS, 0);

// =========================================================================
// M. BUILD PLACEMENT AND FOCUS
// =========================================================================
var bPlace = build('b-place', ['pierwszy', 'drugi', 'trzeci']);
start([bPlace]);
var bPlaceIds = authoredPoolIds();
placeTile(bPlaceIds[0]);
eq('M1 placement appends the exact stable tile identity',
   G.build.row.map(function (t) { return t.id; }), [bPlaceIds[0]]);
eq('M1 placement marks that exact pool tile used', G.build.pool[0].used, true);
ok('M1 placement leaves every other pool tile available',
   G.build.pool.slice(1).every(function (t) { return !t.used; }));
eq('M1 placement enables Check', el('gCheckBtn').disabled, false);
ok('M2 placement focuses the next unused pool tile',
   ACTIVE === poolTile(bPlaceIds[1]) && ACTIVE !== BODY);

start([bPlace]);
var bWrapIds = authoredPoolIds();
placeTile(bWrapIds[1]);
ok('M3 next-unused search moves forward in pool order',
   ACTIVE === poolTile(bWrapIds[2]));
placeTile(bWrapIds[2]);
ok('M3 next-unused search wraps to the first pool tile',
   ACTIVE === poolTile(bWrapIds[0]));
placeTile(bWrapIds[0]);
eq('M4 no unused pool tile remains', unusedPoolButtons().length, 0);
ok('M4 final placement focuses enabled Check',
   ACTIVE === el('gCheckBtn') && !el('gCheckBtn').disabled && ACTIVE !== BODY);

// =========================================================================
// N. BUILD REMOVAL, STABLE IDENTITIES, AND EDIT CLEANUP
// =========================================================================
var bRemove = build('b-remove', ['jeden', 'dwa', 'trzy']);
start([bRemove]);
var bRemoveIds = authoredPoolIds();
placeTiles([bRemoveIds[0], bRemoveIds[1]]);
ok('N1 correctly positioned row tiles retain the live green indication',
   rowButtons().every(function (b) { return b.classList.contains('ok'); }));
press(rowTile(bRemoveIds[1]));
eq('N1 removal deletes only the exact row tile',
   G.build.row.map(function (t) { return t.id; }), [bRemoveIds[0]]);
eq('N1 the matching pool tile becomes available', G.build.pool[1].used, false);
ok('N1 removal focuses the matching returned pool tile',
   ACTIVE === poolTile(bRemoveIds[1]) && ACTIVE !== BODY);
eq('N1 Check stays enabled while the row is non-empty', el('gCheckBtn').disabled, false);
ok('N1 the remaining correct-position indication survives repaint',
   rowTile(bRemoveIds[0]).classList.contains('ok'));
press(rowTile(bRemoveIds[0]));
eq('N2 removing the final row tile disables Check', el('gCheckBtn').disabled, true);
ok('N2 final removal still focuses its returned pool tile',
   ACTIVE === poolTile(bRemoveIds[0]) && ACTIVE !== BODY);

var bDuplicate = build('b-duplicate', ['nie', 'nie', 'teraz']);
start([bDuplicate]);
var bDuplicateIds = authoredPoolIds();
placeTile(bDuplicateIds[1]);
eq('N3 repeated-looking words retain the activated stable identity',
   G.build.row.map(function (t) { return t.id; }), [bDuplicateIds[1]]);
eq('N3 the other repeated-looking pool tile remains unused', G.build.pool[0].used, false);
press(rowTile(bDuplicateIds[1]));
ok('N3 removal focuses the exact returned duplicate by data-id',
   ACTIVE === poolTile(bDuplicateIds[1]) && ACTIVE !== poolTile(bDuplicateIds[0]));

var bEdit = build('b-edit', ['A', 'B', 'C']);
start([bEdit]);
var bEditIds = authoredPoolIds();
placeTiles([bEditIds[1], bEditIds[0], bEditIds[2]]);
press(el('gCheckBtn'));
ok('N4 a rejected order creates a persistent status before editing',
   /order is not correct/i.test(status().textContent));
ok('N4 a rejected order marks at least one bad position',
   rowButtons().some(function (b) { return b.classList.contains('bad'); }));
press(rowTile(bEditIds[1]));
eq('N4 editing clears the stale wrong-order status', status().textContent, '');
ok('N4 repaint clears every stale bad-position marker',
   rowButtons().every(function (b) { return !b.classList.contains('bad'); }));
ok('N4 editing a rejected answer keeps build state ask', G.state === 'ask');
ok('N4 edit focus lands on the returned stable pool tile',
   ACTIVE === poolTile(bEditIds[1]) && ACTIVE !== BODY);

// =========================================================================
// N5. BUILD INCOMPLETE PREFIX
// =========================================================================
var bIncomplete = build('b-incomplete', ['Ala', 'ma', 'kota']);
start([bIncomplete]);
var bIncompleteOneIds = authoredPoolIds();
placeTile(bIncompleteOneIds[0]);
press(el('gCheckBtn'));
eq('N5 one-word prefix marks the drill attempted', G.attempted, true);
eq('N5 one-word prefix banks false', G.results[0], false);
eq('N5 one-word prefix remains ask', G.state, 'ask');
eq('N5 one-word prefix keeps Next disabled', el('gDrillNext').disabled, true);
ok('N5 one-word prefix keeps Check available',
   !el('gCheckBtn').disabled && el('gCheckBtn').style.display !== 'none');
ok('N5 correct one-word prefix receives no bad marker',
   rowButtons().every(function (b) { return !b.classList.contains('bad'); }));
ok('N5 status explicitly identifies the incomplete sentence',
   /sentence is incomplete/i.test(status().textContent));
ok('N5 status does not claim unmarked words are highlighted',
   !/highlighted words/i.test(status().textContent));
ok('N5 focus moves to the first unused pool tile',
   ACTIVE === poolTile(bIncompleteOneIds[1]));
ok('N5 focus leaves Check and BODY',
   ACTIVE !== el('gCheckBtn') && ACTIVE !== BODY);
placeTile(bIncompleteOneIds[1]);
eq('N5 placing the next tile clears incomplete status', status().textContent, '');
eq('N5 incomplete one-word prefix does not autoplay', AUDIO_STARTS, 0);

start([bIncomplete]);
var bIncompleteTwoIds = authoredPoolIds();
placeTiles([bIncompleteTwoIds[0], bIncompleteTwoIds[1]]);
press(el('gCheckBtn'));
eq('N6 two-word prefix marks the drill attempted', G.attempted, true);
eq('N6 two-word prefix banks false', G.results[0], false);
eq('N6 two-word prefix remains ask', G.state, 'ask');
eq('N6 two-word prefix keeps Next disabled', el('gDrillNext').disabled, true);
ok('N6 two-word prefix keeps Check available',
   !el('gCheckBtn').disabled && el('gCheckBtn').style.display !== 'none');
ok('N6 correct two-word prefix receives no bad marker',
   rowButtons().every(function (b) { return !b.classList.contains('bad'); }));
ok('N6 status explicitly identifies the incomplete sentence',
   /sentence is incomplete/i.test(status().textContent));
ok('N6 status does not claim unmarked words are highlighted',
   !/highlighted words/i.test(status().textContent));
ok('N6 focus moves to the first unused pool tile',
   ACTIVE === poolTile(bIncompleteTwoIds[2]));
ok('N6 focus leaves Check and BODY',
   ACTIVE !== el('gCheckBtn') && ACTIVE !== BODY);
placeTile(bIncompleteTwoIds[2]);
eq('N6 placing the next tile clears incomplete status', status().textContent, '');
eq('N6 incomplete two-word prefix does not autoplay', AUDIO_STARTS, 0);

// =========================================================================
// O. BUILD WRONG-ORDER REJECTION
// =========================================================================
var bWrong = build('b-wrong', ['dobry', 'jest', 'porządek']);
start([bWrong]);
var bWrongIds = authoredPoolIds();
placeTiles([bWrongIds[1], bWrongIds[0], bWrongIds[2]]);
press(el('gCheckBtn'));
eq('O1 wrong build marks the drill attempted', G.attempted, true);
eq('O1 wrong build banks false', G.results[0], false);
eq('O1 wrong build remains ask', G.state, 'ask');
eq('O1 wrong build keeps Next disabled', el('gDrillNext').disabled, true);
ok('O1 wrong build keeps Check usable',
   !el('gCheckBtn').disabled && el('gCheckBtn').style.display !== 'none');
eq('O2 only mismatched positions receive bad state',
   rowButtons().map(function (b) { return b.classList.contains('bad'); }),
   [true, true, false]);
ok('O2 a matching position retains its live green state',
   rowButtons()[2].classList.contains('ok'));
eq('O2 the first mismatch accessible name includes word and state',
   rowButtons()[0].accName(), 'jest, wrong position');
eq('O2 the second mismatch accessible name includes word and state',
   rowButtons()[1].accName(), 'dobry, wrong position');
eq('O2 a matching tile receives no wrong-position accessible label',
   rowButtons()[2].getAttribute('aria-label'), null);
eq('O3 persistent status announces a concise actionable rejection',
   status().textContent,
   'That order is not correct. Adjust the highlighted words and try again.');
ok('O3 focus moves to the first mismatched row tile',
   ACTIVE === rowButtons()[0] && ACTIVE !== BODY);
ok('O4 the shake class is removed after its timeout',
   !el('gBuildRow').classList.contains('shake'));
eq('O4 wrong rejection does not autoplay', AUDIO_STARTS, 0);

// =========================================================================
// P. BUILD CORRECT SETTLEMENT
// =========================================================================
var bCorrect = build('b-correct', ['To', 'jest', 'dobrze']);
start([bCorrect]);
solveBuildExact();
eq('P1 first-try correct build banks true', G.results[0], true);
eq('P1 first-try correct build leaves attempted false', G.attempted, false);
eq('P1 correct build settles state to done', G.state, 'done');
ok('P2 correct build locks the row', el('gBuildRow').classList.contains('locked'));
eq('P2 correct build hides the pool', el('gBuildPool').style.display, 'none');
eq('P2 correct build hides Check', el('gCheckBtn').style.display, 'none');
eq('P3 full Polish build feedback remains', el('gFbBox').innerHTML.indexOf(bCorrect.full) !== -1, true);
eq('P3 English build feedback remains', el('gFbBox').innerHTML.indexOf(bCorrect.fullEn) !== -1, true);
ok('P3 authored build explanation markup remains',
   el('gFbBox').innerHTML.indexOf(bCorrect.explain) !== -1 &&
   el('gFbBox').innerHTML.indexOf('<b>') !== -1);
ok('P3 build feedback remains visible', el('gFbBox').classList.contains('show'));
eq('P3 one build mini-audio button remains',
   el('gFbBox').querySelectorAll('.mini-audio').length, 1);
eq('P3 build feedback is not a verdict live region',
   el('gFbBox').getAttribute('aria-live'), null);
ok('P4 build status explicitly begins with Correct', /^Correct\b/.test(status().textContent));
ok('P4 build status says Next is ready', /Next is ready/.test(status().textContent));
var buildStatusPl = status().children.filter(function (n) {
  return n.getAttribute && n.getAttribute('lang') === 'pl';
});
eq('P4 build correct status contains one lang=pl node', buildStatusPl.length, 1);
eq('P4 build status announces the full Polish sentence',
   buildStatusPl.length ? buildStatusPl[0].textContent : null, bCorrect.full);
eq('P5 final clean build labels Next as See results',
   el('gDrillNextLabel').textContent, 'See results');
eq('P5 correct build enables Next', el('gDrillNext').disabled, false);
ok('P5 correct build focuses enabled Next',
   ACTIVE === el('gDrillNext') && !ACTIVE.disabled && ACTIVE !== BODY);
eq('P5 correct build does not autoplay', AUDIO_STARTS, 0);

start([bCorrect]);
var bCorrectRetryIds = authoredPoolIds();
placeTiles([bCorrectRetryIds[1], bCorrectRetryIds[0], bCorrectRetryIds[2]]);
press(el('gCheckBtn'));
while (G.build.row.length) press(rowButtons()[rowButtons().length - 1]);
solveBuildExact();
eq('P6 correct after an earlier build miss remains false', G.results[0], false);
eq('P6 corrected build settles state to done', G.state, 'done');
ok('P6 corrected build focuses Next', ACTIVE === el('gDrillNext'));

// =========================================================================
// Q. BUILD SETTLED-STATE PROTECTION
// =========================================================================
start([bCorrect]);
placeTiles(authoredPoolIds());
var retainedRowHandler = handler(rowButtons()[0]);
press(el('gCheckBtn'));
var qRowBefore = JSON.stringify(G.build.row);
var qPoolBefore = JSON.stringify(G.build.pool);
var qRowFocus = ACTIVE;
if (retainedRowHandler) retainedRowHandler({});
eq('Q1 retained row handler cannot change a settled row',
   JSON.stringify(G.build.row), qRowBefore);
eq('Q1 retained row handler cannot change a settled pool',
   JSON.stringify(G.build.pool), qPoolBefore);
ok('Q1 retained row handler cannot move settled focus', ACTIVE === qRowFocus);
ok('Q1 settled row remains locked and complete',
   el('gBuildRow').classList.contains('locked') &&
   G.build.row.length === bCorrect.answer.length);

start([bCorrect]);
var qPoolIds = authoredPoolIds();
var retainedPoolHandler = handler(poolTile(qPoolIds[0]));
solveBuildExact();
G.build.pool[0].used = false;
var qDirectPoolBefore = JSON.stringify(G.build.pool);
var qDirectRowBefore = JSON.stringify(G.build.row);
if (retainedPoolHandler) retainedPoolHandler({});
eq('Q2 retained pool handler cannot change settled pool state',
   JSON.stringify(G.build.pool), qDirectPoolBefore);
eq('Q2 retained pool handler cannot append to a settled row',
   JSON.stringify(G.build.row), qDirectRowBefore);

start([bCorrect]);
solveBuildExact();
var qCheckResult = JSON.stringify(G.results);
var qCheckAttempted = G.attempted;
var qCheckRow = JSON.stringify(G.build.row);
var qCheckPool = JSON.stringify(G.build.pool);
var qCheckStatus = status().textContent;
var qCheckStatusChildren = status().children;
var qCheckFeedback = el('gFbBox').innerHTML;
var qCheckFeedbackWrites = HTML_WRITES.gFbBox;
var qCheckFocus = ACTIVE;
var qCheckNextDisabled = el('gDrillNext').disabled;
var qCheckNextLabel = el('gDrillNextLabel').textContent;
GRAMMAR.gCheckBuild(bCorrect);
eq('Q3 repeated gCheckBuild cannot change settled result',
   JSON.stringify(G.results), qCheckResult);
eq('Q3 repeated gCheckBuild cannot change attempted state', G.attempted, qCheckAttempted);
eq('Q3 repeated gCheckBuild cannot change settled row', JSON.stringify(G.build.row), qCheckRow);
eq('Q3 repeated gCheckBuild cannot change settled pool', JSON.stringify(G.build.pool), qCheckPool);
eq('Q3 repeated gCheckBuild cannot change status', status().textContent, qCheckStatus);
ok('Q3 repeated gCheckBuild cannot rebuild status nodes',
   status().children === qCheckStatusChildren);
eq('Q3 repeated gCheckBuild cannot change feedback', el('gFbBox').innerHTML, qCheckFeedback);
eq('Q3 repeated gCheckBuild cannot rebuild feedback',
   HTML_WRITES.gFbBox, qCheckFeedbackWrites);
ok('Q3 repeated gCheckBuild cannot move focus', ACTIVE === qCheckFocus);
eq('Q3 repeated gCheckBuild cannot change Next state',
   el('gDrillNext').disabled, qCheckNextDisabled);
eq('Q3 repeated gCheckBuild cannot change Next label',
   el('gDrillNextLabel').textContent, qCheckNextLabel);

// =========================================================================
// R. BUILD ROUND BEHAVIOR AND REAL CORPUS
// =========================================================================
var bRound = build('b-round', ['dokładnie', 'ta', 'kolejność']);
start([bRound]);
var bRoundIds = authoredPoolIds();
placeTiles([bRoundIds[1], bRoundIds[0], bRoundIds[2]]);
press(el('gCheckBtn'));
eq('R1 swapped authored words remain rejected', G.results[0], false);
eq('R1 a rejected build remains open for correction', G.state, 'ask');
while (G.build.row.length) press(rowButtons()[rowButtons().length - 1]);
solveBuildExact();
eq('R1 corrected original remains a first-attempt miss', G.results[0], false);
eq('R2 missed final original labels its advance as Next',
   el('gDrillNextLabel').textContent, 'Next');
activateNext();
eq('R2 a missed build appends exactly one retry', G.queue.length, 2);
ok('R2 build retry is marked and preserves identity',
   G.queue[1]._requeue === true && G.queue[1].id === bRound.id);
eq('R2 retry starts in ask state', G.state, 'ask');
ok('R2 retry starts focused in its build pool',
   ACTIVE === poolButtons()[0] && ACTIVE !== BODY);
solveBuildExact();
eq('R3 a clean retry can settle successfully', G.results[1], true);
eq('R3 final retry labels Next as See results',
   el('gDrillNextLabel').textContent, 'See results');
activateNext();
eq('R3 retry completion keeps original score at zero', el('gScore').textContent, '0');
eq('R3 retry completion keeps original total at one', el('gTotal').textContent, '1');
ok('R3 build completion focuses the existing done heading',
   ACTIVE === el('gDoneTitle') && ACTIVE !== BODY);

var allRealBuildsAcceptExact = true;
BUILD.forEach(function (entry) {
  start([entry.drill]);
  solveBuildExact();
  if (G.state !== 'done' || G.results[0] !== true ||
      el('gDrillNext').disabled || ACTIVE !== el('gDrillNext')) {
    allRealBuildsAcceptExact = false;
  }
});
ok('R4 every current real build drill accepts its exact authored order',
   allRealBuildsAcceptExact);

// =========================================================================
// S. PHASE 4I ORDINARY TOPIC QUEUE CREATION
// =========================================================================
function drillIds(drills) {
  return drills.map(function (d) { return d.id; });
}
function sortedDrillIds(drills) {
  return drillIds(drills).slice().sort();
}
var sA = choose('s-a', ['a-good', 'a-bad'], 'a-good');
var sB = build('s-b', ['B', 'build']);
var sC = choose('s-c', ['c-good', 'c-bad'], 'c-good');
var sD = build('s-d', ['D', 'build']);
var sDrills = [sA, sB, sC, sD];
var sTopic = topicOf(sDrills);
var sAuthoredIds = drillIds(sTopic.drills);
var sSourceArray = sTopic.drills;
var sShuffle = controlledShippingShuffle([0]);
var sEvents = [];
var sStartOnly = shippingStartOnly(sShuffle, noMix, sEvents);
resetG(sTopic);
G.di = 3;
G.results = [true, false];
sStartOnly();
eq('S1 ordinary gStartPractice calls shipping gShuffle exactly once',
   sShuffle.calls.length, 1);
eq('S1 ordinary queue follows the controlled Fisher-Yates order',
   drillIds(G.queue), ['s-b', 's-c', 's-d', 's-a']);
ok('S1 controlled ordinary queue differs from authored order',
   JSON.stringify(drillIds(G.queue)) !== JSON.stringify(sAuthoredIds));
eq('S2 ordinary queue retains the complete exact drill-id set',
   sortedDrillIds(G.queue), sAuthoredIds.slice().sort());
eq('S2 ordinary queue neither adds nor omits a drill', G.queue.length, sDrills.length);
ok('S2 ordinary queue is a new array', G.queue !== sSourceArray);
ok('S2 authored drills keep their original array identity', sTopic.drills === sSourceArray);
eq('S2 authored drill order remains unchanged', drillIds(sTopic.drills), sAuthoredIds);
ok('S2 queue entries retain the authored drill objects',
   G.queue.every(function (d) { return sDrills.indexOf(d) !== -1; }));
eq('S3 a new ordinary round resets the current index', G.di, 0);
eq('S3 a new ordinary round resets results', G.results, []);
eq('S3 practice is shown before the first drill renders',
   sEvents, ['phase:practice', 'render:s-b']);
eq('S3 the first shuffled drill is the rendered drill',
   sEvents[1], 'render:' + G.queue[0].id);

// =========================================================================
// T. PHASE 4I PRACTICE AGAIN AND INITIAL FOCUS
// =========================================================================
var tShuffle = controlledShippingShuffle([0.999]);
var tRuntime = grammarRuntime(tShuffle, noMix);
resetDom(tRuntime);
resetG(sTopic);
tRuntime.gStartPractice();
var tRoundOne = G.queue.slice();
eq('T1 first controlled round uses its deterministic order',
   drillIds(tRoundOne), ['s-a', 's-b', 's-c', 's-d']);
ok('T1 first shuffled choose drill receives existing choose focus',
   G.queue[0] === sA && ACTIVE === optionButtons()[0] && ACTIVE !== BODY);

G.results = [true, false, true, true];
G.di = 3;
G.queue.push(Object.assign({}, G.queue[1], { _requeue: true }));
G.attempted = true;
G.state = 'done';
G.build = {
  pool: [{ w: 'stale', id: 'stale', used: true }],
  row: [{ w: 'stale', id: 'stale', used: true }],
  answer: ['stale']
};
status().textContent = 'Stale verdict';
el('gDrillNext').disabled = false;
tShuffle.use([0]);
tRuntime.gStartPractice();
var tRoundTwo = G.queue.slice();
eq('T2 Practice again uses the second deterministic shuffle',
   drillIds(tRoundTwo), ['s-b', 's-c', 's-d', 's-a']);
eq('T2 both rounds contain the same complete drill-id set',
   sortedDrillIds(tRoundTwo), sortedDrillIds(tRoundOne));
eq('T2 Practice again still preserves the authored source order',
   drillIds(sTopic.drills), sAuthoredIds);
ok('T2 the two controlled round queues differ',
   JSON.stringify(drillIds(tRoundTwo)) !== JSON.stringify(drillIds(tRoundOne)));
eq('T3 Practice again resets the current index', G.di, 0);
eq('T3 Practice again clears stale results', G.results, []);
eq('T3 Practice again clears stale attempted state', G.attempted, false);
eq('T3 Practice again resets drill state to ask', G.state, 'ask');
eq('T3 the first shuffled build starts with an empty row', G.build.row, []);
eq('T3 the first shuffled build replaces the stale tile pool',
   G.build.pool.map(function (tile) { return tile.w; }).slice().sort(),
   sB.answer.slice().sort());
ok('T3 the new round contains no retry copies',
   G.queue.every(function (d) { return !d._requeue; }));
eq('T4 the new render lifecycle clears stale status', status().textContent, '');
eq('T4 Practice again begins with Next disabled', el('gDrillNext').disabled, true);
eq('T4 Practice again shows the practice phase', el('gPractice').style.display, 'flex');
ok('T4 first shuffled build receives existing first-pool focus',
   G.queue[0] === sB && ACTIVE === poolButtons()[0] && ACTIVE !== BODY);
ok('T4 the second queue still reuses authored drill objects',
   G.queue.every(function (d) { return sDrills.indexOf(d) !== -1; }));

// =========================================================================
// U. PHASE 4I MIX SAMPLING IS NOT DOUBLE-SHUFFLED
// =========================================================================
function syntheticChooseSeries(prefix, count) {
  var out = [];
  for (var i = 0; i < count; i++) {
    out.push(choose(prefix + '-' + i, [prefix + '-good-' + i, prefix + '-bad-' + i],
                    prefix + '-good-' + i));
  }
  return out;
}
var uCaseADrills = syntheticChooseSeries('u-a', 10);
var uCaseBDrills = syntheticChooseSeries('u-b', 8);
var uMix = {
  id: 'u-mix', name: 'Synthetic Mix', mixOf: 'Synthetic Cases',
  teach: [], drills: []
};
var uCaseA = { id: 'u-case-a', name: 'Case A', drills: uCaseADrills };
var uCaseB = { id: 'u-case-b', name: 'Case B', drills: uCaseBDrills };
var uLevels = [{ level: 'Synthetic Cases', topics: [uMix, uCaseA, uCaseB] }];
var uSourcesBefore = JSON.stringify([uCaseADrills, uCaseBDrills]);
var uShuffle = controlledShippingShuffle([0]);
var uSample = shippingSampleMix(uLevels, uShuffle);
var uEvents = [];
var uStart = shippingStartOnly(uShuffle, uSample, uEvents);
resetG(uMix);
uStart();
eq('U1 complete Mix start path calls shipping gShuffle exactly once',
   uShuffle.calls.length, 1);
eq('U1 the one Mix shuffle receives the complete source pool',
   uShuffle.calls[0].input.length, uCaseADrills.length + uCaseBDrills.length);
eq('U1 gSampleMix keeps exactly 15 drills when at least 15 are available',
   uMix.drills.length, 15);
eq('U1 gSampleMix order is the first 15 from its controlled shipping shuffle',
   drillIds(uMix.drills), drillIds(uShuffle.calls[0].output.slice(0, 15)));
eq('U2 gStartPractice preserves gSampleMix order in G.queue',
   drillIds(G.queue), drillIds(uMix.drills));
ok('U2 Mix queue is still a separate array from sampled topic.drills',
   G.queue !== uMix.drills);
ok('U2 every sampled drill retains its source case label',
   uMix.drills.every(function (d) {
     return (d.id.indexOf('u-a-') === 0 && d._case === 'Case A') ||
            (d.id.indexOf('u-b-') === 0 && d._case === 'Case B');
   }));
eq('U2 source topic drill arrays remain unchanged',
   JSON.stringify([uCaseADrills, uCaseBDrills]), uSourcesBefore);
ok('U2 no sampled Mix drill is a retry before answering',
   G.queue.every(function (d) { return !d._requeue; }));
eq('U2 Mix lifecycle shows practice before rendering the sampled first drill',
   uEvents, ['phase:practice', 'render:' + G.queue[0].id]);

var uShortDrills = syntheticChooseSeries('u-short', 7);
var uShortMix = {
  id: 'u-short-mix', name: 'Short Synthetic Mix', mixOf: 'Short Cases',
  teach: [], drills: []
};
var uShortTopic = { id: 'u-short-case', name: 'Short Case', drills: uShortDrills };
var uShortLevels = [{ level: 'Short Cases', topics: [uShortMix, uShortTopic] }];
var uShortBefore = JSON.stringify(uShortDrills);
var uShortShuffle = controlledShippingShuffle([0]);
var uShortError = null;
try {
  var uShortSample = shippingSampleMix(uShortLevels, uShortShuffle);
  var uShortStart = shippingStartOnly(uShortShuffle, uShortSample, []);
  resetG(uShortMix);
  uShortStart();
} catch (e) {
  uShortError = String(e);
}
eq('U3 a Mix pool smaller than 15 starts without error', uShortError, null);
eq('U3 a short Mix retains every available drill', G.queue.length, uShortDrills.length);
eq('U3 a short Mix introduces no duplicate ids',
   new Set(drillIds(G.queue)).size, uShortDrills.length);
eq('U3 a short Mix preserves the complete source id set',
   sortedDrillIds(G.queue), sortedDrillIds(uShortDrills));
eq('U3 a short Mix still shuffles exactly once', uShortShuffle.calls.length, 1);
eq('U3 a short Mix leaves its source drill array unchanged',
   JSON.stringify(uShortDrills), uShortBefore);
ok('U3 every short sample retains its case label',
   G.queue.every(function (d) { return d._case === 'Short Case'; }));

// =========================================================================
// V. PHASE 4I POSITIONAL SCORING AFTER SHUFFLE
// =========================================================================
var v1 = choose('v-1', ['v1-right', 'v1-wrong'], 'v1-right');
var v2 = choose('v-2', ['v2-right', 'v2-wrong'], 'v2-right');
var v3 = choose('v-3', ['v3-right', 'v3-wrong'], 'v3-right');
var v4 = choose('v-4', ['v4-right', 'v4-wrong'], 'v4-right');
var vTopic = topicOf([v1, v2, v3, v4]);
var vShuffle = controlledShippingShuffle([0]);
var vRuntime = grammarRuntime(vShuffle, noMix);
resetDom(vRuntime);
resetG(vTopic);
vRuntime.gStartPractice();
eq('V1 scoring scenario begins in deterministic shuffled order',
   drillIds(G.queue), ['v-2', 'v-3', 'v-4', 'v-1']);
press(byValue(G.queue[0].answer));
eq('V1 first-try correct is stored at shuffled queue index zero',
   G.results[0], true);
activateNext();
var vMissed = G.queue[1];
var vWrong = vMissed.options.filter(function (o) { return o !== vMissed.answer; })[0];
press(byValue(vWrong));
eq('V2 a miss marks the shuffled queue index false', G.results[1], false);
press(byValue(vMissed.answer));
eq('V2 correction does not overwrite the shuffled miss', G.results[1], false);
eq('V2 Next predicts the pending retry', el('gDrillNextLabel').textContent, 'Next');
activateNext();
eq('V3 advancing the miss appends one retry', G.queue.length, 5);
var vRetryPlain = Object.assign({}, G.queue[4]);
delete vRetryPlain._requeue;
ok('V3 retry is a copy of the exact missed shuffled drill',
   G.queue[4] !== vMissed &&
   G.queue[4]._requeue === true &&
   JSON.stringify(vRetryPlain) === JSON.stringify(vMissed));
eq('V3 the missed drill appears only once as a retry',
   G.queue.filter(function (d) { return d._requeue && d.id === vMissed.id; }).length, 1);
press(byValue(G.queue[G.di].answer));
activateNext();
press(byValue(G.queue[G.di].answer));
eq('V4 last original says Next while its retry remains',
   el('gDrillNextLabel').textContent, 'Next');
activateNext();
ok('V4 the pending retry is now current',
   G.queue[G.di]._requeue === true && G.queue[G.di].id === vMissed.id);
press(byValue(G.queue[G.di].answer));
eq('V4 final retry changes the label to See results',
   el('gDrillNextLabel').textContent, 'See results');
eq('V4 positional results retain first-attempt outcomes and retry success',
   G.results, [true, false, true, true, true]);
activateNext();
eq('V5 final score excludes the successful retry', el('gScore').textContent, '3');
eq('V5 final total counts shuffled originals only', el('gTotal').textContent, '4');
eq('V5 completion follows the existing done path', el('gDone').style.display, 'flex');

// =========================================================================
// W. PHASE 4I CORPUS-WIDE ROUND INVARIANTS
// =========================================================================
var wTopics = [];
GRAMMAR_LEVELS.forEach(function (level) {
  (level.topics || []).forEach(function (topic) {
    wTopics.push({ level: level, topic: topic });
  });
});
var wOrdinary = wTopics.filter(function (entry) { return !entry.topic.mixOf; });
var wMix = wTopics.filter(function (entry) { return !!entry.topic.mixOf; });
var wSmall = wOrdinary.filter(function (entry) {
  return (entry.topic.drills || []).length < 2;
});
info('Grammar topics discovered: ' + wTopics.length + ' total; ' +
     wOrdinary.length + ' ordinary; ' + wMix.length + ' Mix');
info('ordinary Grammar drill counts: ' + wOrdinary.map(function (entry) {
  return (entry.topic.id || entry.topic.name) + '=' + (entry.topic.drills || []).length;
}).join(', '));
info('ordinary Grammar topics with fewer than two drills: ' +
     (wSmall.length ? wSmall.map(function (entry) {
       return entry.topic.id || entry.topic.name;
     }).join(', ') : 'none'));

var wOrdinaryInvariant = true;
wOrdinary.forEach(function (entry) {
  var topic = entry.topic;
  var source = topic.drills;
  var idsBefore = drillIds(source);
  var jsonBefore = JSON.stringify(source);
  var shuffle = controlledShippingShuffle([0]);
  var startOnly = shippingStartOnly(shuffle, noMix, []);
  resetG(topic);
  startOnly();
  var sameIds = JSON.stringify(sortedDrillIds(G.queue)) ===
                JSON.stringify(idsBefore.slice().sort());
  if (G.queue.length !== source.length || !sameIds ||
      JSON.stringify(source) !== jsonBefore ||
      G.queue.some(function (d) { return d._requeue; })) {
    wOrdinaryInvariant = false;
  }
});
ok('W1 every real ordinary topic preserves ids, count, source order and fresh state',
   wOrdinaryInvariant);

var wMixInvariant = true;
wMix.forEach(function (entry) {
  var topic = entry.topic;
  var sourceLevel = GRAMMAR_LEVELS.find(function (level) {
    return level.level === topic.mixOf;
  });
  if (!sourceLevel) {
    wMixInvariant = false;
    return;
  }
  var sourceTopics = sourceLevel.topics.filter(function (candidate) {
    return candidate !== topic && candidate.drills && candidate.drills.length;
  });
  var available = sourceTopics.reduce(function (n, sourceTopic) {
    return n + sourceTopic.drills.length;
  }, 0);
  var sourceBefore = JSON.stringify(sourceTopics.map(function (sourceTopic) {
    return sourceTopic.drills;
  }));
  var shuffle = controlledShippingShuffle([0]);
  var sample = shippingSampleMix(GRAMMAR_LEVELS, shuffle);
  var startOnly = shippingStartOnly(shuffle, sample, []);
  resetG(topic);
  startOnly();
  var sourceNames = sourceTopics.map(function (sourceTopic) { return sourceTopic.name; });
  if (!sourceTopics.length || shuffle.calls.length !== 1 ||
      G.queue.length !== Math.min(15, available) ||
      G.queue.some(function (d) {
        return !usableString(d.id) || sourceNames.indexOf(d._case) === -1 || d._requeue;
      }) ||
      JSON.stringify(sourceTopics.map(function (sourceTopic) {
        return sourceTopic.drills;
      })) !== sourceBefore) {
    wMixInvariant = false;
  }
});
ok('W2 every real Mix discovers its pool and keeps sample ids, case labels and size',
   wMixInvariant);

// =========================================================================
// X. PHASE 4I SEMANTIC SOURCE WIRING
// =========================================================================
var X_START = codeOnly(GSRC.gStartPractice);
var X_SHUFFLE = codeOnly(SHUFFLE_SRC);
var X_SAMPLE = codeOnly(SAMPLE_MIX_SRC);
ok('X1 ordinary gStartPractice creates its queue with gShuffle',
   hasCode(X_START,
     'G.queue=G.topic.mixOf?G.topic.drills.slice():gShuffle(G.topic.drills)'));
eq('X1 gStartPractice has exactly one queue-level gShuffle call',
   countOf(X_START, 'gShuffle('), 1);
ok('X1 Mix gStartPractice copies the already randomized sample',
   hasCode(X_START, 'G.topic.mixOf?G.topic.drills.slice():gShuffle(G.topic.drills)'));
ok('X2 gSampleMix still owns random sample creation',
   hasCode(X_SAMPLE, 'topic.drills=gShuffle(all).slice(0,15)'));
ok('X2 gShuffle still clones before Fisher-Yates',
   hasCode(X_SHUFFLE, 'a=a.slice()') &&
   X_SHUFFLE.indexOf('a=a.slice()') < X_SHUFFLE.indexOf('for(') &&
   X_SHUFFLE.indexOf('Math.random()') !== -1);
ok('X3 gStartPractice still resets index and results',
   hasCode(X_START, 'G.di=0') && hasCode(X_START, 'G.results=[]'));
ok('X3 gStartPractice still shows practice before rendering',
   X_START.indexOf('gPhaseView("practice")') !== -1 &&
   X_START.indexOf('gPhaseView("practice")') < X_START.indexOf('gRenderDrill()'));
ok('X4 gDrillAdvance retains Phase 4H positional retry behavior',
   hasCode(CODE_G.gDrillAdvance, 'if(G.results[G.di]===false&&!c._requeue)') &&
   hasCode(CODE_G.gDrillAdvance,
     'G.queue.push(Object.assign({},c,{_requeue:true}))') &&
   hasCode(CODE_G.gDrillAdvance,
     'if(G.di<G.queue.length-1){G.di++;gRenderDrill();}else gShowDone()'));
ok('X4 gShowDone retains original-only positional scoring',
   hasCode(CODE_G.gShowDone, 'const total=G.queue.filter(d=>!d._requeue).length') &&
   hasCode(CODE_G.gShowDone,
     'const score=G.queue.reduce((n,d,i)=>n+((!d._requeue&&G.results[i]===true)?1:0),0)'));
ok('X5 Phase 4G choose construction and initial focus remain wired',
   hasCode(CODE_G.gRenderChoose, 'document.createElement("button")') &&
   CODE_G.gRenderChoose.indexOf('addEventListener') !== -1 &&
   hasCode(CODE_G.gRenderChoose, 'if(first)first.focus()'));
ok('X5 Phase 4H build focus and Phase 4J exact keyed matching remain wired',
   hasCode(CODE_G.gRenderBuild, 'gPaintBuild({kind:"first-pool"})') &&
   hasCode(CODE_G.gCheckBuild, 'const validOrders=[c.answer].concat(accepted)') &&
   CODE_G.gCheckBuild.indexOf('gBuildTokenKey') !== -1);

// =========================================================================
// Y. PHASE 4J CANONICAL AND ACCEPTED-ORDER INTERACTIONS
// =========================================================================
var yCanonicalFailures = [];
EXPECTED_ACCEPTED_IDS.forEach(function (id) {
  var drill = drillById(id);
  start([drill]);
  submitWords(drill.answer);
  if (G.results[0] !== true || G.attempted !== false || G.state !== 'done' ||
      !el('gBuildRow').classList.contains('locked') ||
      el('gBuildPool').style.display !== 'none' ||
      el('gCheckBtn').style.display !== 'none' ||
      el('gDrillNext').disabled || ACTIVE !== el('gDrillNext')) {
    yCanonicalFailures.push(id);
  }
});
eq('Y1 all six affected drills still accept their canonical orders completely',
   yCanonicalFailures, []);

var yAcceptedSourceBefore = {};
EXPECTED_ACCEPTED_IDS.forEach(function (id) {
  var drill = drillById(id);
  var accepted = EXPECTED_ACCEPTED_ORDERS[id][0];
  yAcceptedSourceBefore[id] = {
    json: JSON.stringify(drill),
    acceptedRef: drill.acceptedOrders
  };
  start([drill]);
  placeWords(accepted);
  var submittedIds = G.build.row.map(function (tile) { return tile.id; });
  var submittedTileWords = G.build.row.map(function (tile) { return tile.w; });
  press(el('gCheckBtn'));
  eq('Y2 ' + id + ' accepted alternative banks true', G.results[0], true);
  eq('Y2 ' + id + ' accepted alternative leaves attempted false', G.attempted, false);
  eq('Y2 ' + id + ' accepted alternative settles done', G.state, 'done');
  ok('Y2 ' + id + ' accepted row locks',
     el('gBuildRow').classList.contains('locked'));
  eq('Y2 ' + id + ' accepted settlement preserves tile identities',
     G.build.row.map(function (tile) { return tile.id; }), submittedIds);
  eq('Y2 ' + id + ' accepted settlement preserves canonical tile values internally',
     G.build.row.map(function (tile) { return tile.w; }), submittedTileWords);
  eq('Y3 ' + id + ' locked row displays authored accepted capitalization',
     rowButtons().map(function (button) { return button.textContent; }), accepted);
  ok('Y3 ' + id + ' does not retain wrong canonical capitalization in the locked row',
     JSON.stringify(rowButtons().map(function (button) { return button.textContent; })) !==
     JSON.stringify(submittedTileWords));
  eq('Y3 ' + id + ' pool hides', el('gBuildPool').style.display, 'none');
  eq('Y3 ' + id + ' Check hides', el('gCheckBtn').style.display, 'none');
  eq('Y3 ' + id + ' Next enables', el('gDrillNext').disabled, false);
  ok('Y3 ' + id + ' Next receives focus',
     ACTIVE === el('gDrillNext') && ACTIVE !== BODY);
  ok('Y4 ' + id + ' persistent status announces Correct',
     /^Correct\b/.test(status().textContent));
  ok('Y4 ' + id + ' canonical Polish teaching feedback remains visible',
     el('gFbBox').innerHTML.indexOf(drill.full) !== -1);
  ok('Y4 ' + id + ' canonical English teaching feedback remains visible',
     el('gFbBox').innerHTML.indexOf(drill.fullEn) !== -1);
  ok('Y4 ' + id + ' canonical explanation remains visible',
     el('gFbBox').innerHTML.indexOf(drill.explain) !== -1);
  eq('Y4 ' + id + ' keeps one canonical mini-audio control',
     el('gFbBox').querySelectorAll('.mini-audio').length, 1);
  eq('Y4 ' + id + ' accepted alternative never autoplays', AUDIO_STARTS, 0);
  eq('Y4 ' + id + ' authored drill and acceptedOrders remain unmodified',
     JSON.stringify(drill), yAcceptedSourceBefore[id].json);
  ok('Y4 ' + id + ' acceptedOrders array identity remains stable',
     drill.acceptedOrders === yAcceptedSourceBefore[id].acceptedRef);
});

// =========================================================================
// Z. PHASE 4J PREFIX AND CLOSEST-ORDER GUIDANCE
// =========================================================================
var zGuide = build(
  'z-guide',
  ['Piotrze', 'chodź', 'tutaj'],
  [['Chodź', 'tutaj', 'Piotrze']]
);
start([zGuide]);
placeWords(['Piotrze', 'chodź']);
press(el('gCheckBtn'));
eq('Z1 canonical incomplete prefix banks a miss', G.results[0], false);
ok('Z1 canonical incomplete prefix is announced as incomplete',
   /sentence is incomplete/i.test(status().textContent));
ok('Z1 canonical incomplete prefix has no false bad markers',
   rowButtons().every(function (button) {
     return !button.classList.contains('bad') && button.classList.contains('ok');
   }));
ok('Z1 canonical incomplete prefix focuses the first unused pool tile',
   ACTIVE === unusedPoolButtons()[0] && ACTIVE !== BODY);

start([zGuide]);
placeWords(['Chodź', 'tutaj']);
press(el('gCheckBtn'));
eq('Z2 accepted incomplete prefix banks a miss', G.results[0], false);
ok('Z2 accepted incomplete prefix is announced as incomplete',
   /sentence is incomplete/i.test(status().textContent));
ok('Z2 accepted incomplete prefix has no false bad markers',
   rowButtons().every(function (button) {
     return !button.classList.contains('bad') && button.classList.contains('ok');
   }));
ok('Z2 accepted incomplete prefix focuses the first unused pool tile',
   ACTIVE === unusedPoolButtons()[0] && ACTIVE !== BODY);

var zClosest = build(
  'z-closest',
  ['A', 'B', 'C', 'D'],
  [['B', 'C', 'D', 'a']]
);
start([zClosest]);
submitWords(['B', 'A', 'D', 'C']);
eq('Z3 genuinely wrong complete order remains rejected', G.results[0], false);
eq('Z3 closest accepted guide controls ok and bad positions',
   rowButtons().map(function (button) {
     return button.classList.contains('ok') ? 'ok' :
            button.classList.contains('bad') ? 'bad' : 'plain';
   }), ['ok', 'bad', 'ok', 'bad']);
ok('Z3 closest-guide rejection focuses its first mismatched row tile',
   ACTIVE === rowButtons()[1] && ACTIVE !== BODY);
eq('Z3 closest-guide rejection retains the existing actionable status',
   status().textContent,
   'That order is not correct. Adjust the highlighted words and try again.');
ok('Z3 reduced-motion-safe timeout still removes shake',
   !el('gBuildRow').classList.contains('shake'));

var zTie = build('z-tie', ['A', 'B', 'C'], [['B', 'C', 'a']]);
start([zTie]);
submitWords(['B', 'A', 'C']);
eq('Z4 canonical order deterministically wins equal-match ties',
   rowButtons().map(function (button) {
     return button.classList.contains('ok') ? 'ok' :
            button.classList.contains('bad') ? 'bad' : 'plain';
   }), ['bad', 'bad', 'ok']);
ok('Z4 canonical-tie guidance focuses the first canonical mismatch',
   ACTIVE === rowButtons()[0]);

// =========================================================================
// AA. NON-AUTHORED ORDERS AND THE CORRECTED TWO-TOKEN RULE
// =========================================================================
var NON_AUTHORED_ORDERS = {
  'grammar-cases-vocative-004': ['Piotrze', 'tutaj', 'chodź'],
  'grammar-cases-vocative-008': ['Dzieci', 'tu', 'chodźcie'],
  'grammar-cases-vocative-011': ['Babciu', 'za', 'tęsknię', 'tobą'],
  'verbs-future-tense-005': ['Napiszę', 'ciebie', 'do', 'wieczorem']
};
Object.keys(NON_AUTHORED_ORDERS).forEach(function (id) {
  var drill = drillById(id);
  var candidate = NON_AUTHORED_ORDERS[id];
  var validKeyed = [drill.answer].concat(EXPECTED_ACCEPTED_ORDERS[id]).map(function (order) {
    return JSON.stringify(keyedOrder(order));
  });
  ok('AA1 ' + id + ' test candidate is explicitly outside every authored valid order',
     validKeyed.indexOf(JSON.stringify(keyedOrder(candidate))) === -1);
  start([drill]);
  submitWords(candidate);
  eq('AA1 ' + id + ' non-authored complete order remains wrong',
     G.results[0], false);
  eq('AA1 ' + id + ' non-authored complete order remains open',
     G.state, 'ask');
});

var aaInstrumental = drillById('grammar-cases-instrumental-013');
start([aaInstrumental]);
submitWords(['Proszę', 'kawa', 'z', 'mlekiem']);
eq('AA2 instrumental reorder remains explicitly rejected', G.results[0], false);
eq('AA2 instrumental reorder remains open for correction', G.state, 'ask');

['grammar-cases-vocative-014', 'verbs-verbs-of-motion-006'].forEach(function (id) {
  var drill = drillById(id);
  var accepted = EXPECTED_ACCEPTED_ORDERS[id][0];
  var permutations = [
    drill.answer.slice(),
    [drill.answer[1], drill.answer[0]]
  ];
  var permutationKeys = permutations.map(function (order) {
    return JSON.stringify(keyedOrder(order));
  });
  var validKeys = [drill.answer, accepted].map(function (order) {
    return JSON.stringify(keyedOrder(order));
  }).sort();
  eq('AA3 ' + id + ' has exactly two complete distinct tile permutations',
     new Set(permutationKeys).size, 2);
  eq('AA3 ' + id + ' canonical and accepted exhaust those permutations',
     permutationKeys.slice().sort(), validKeys);

  start([drill]);
  placeWords([drill.answer[0]]);
  press(el('gCheckBtn'));
  ok('AA3 ' + id + ' canonical one-token prefix is incomplete without bad markers',
     /sentence is incomplete/i.test(status().textContent) &&
     rowButtons().every(function (button) { return !button.classList.contains('bad'); }));

  start([drill]);
  placeWords([accepted[0]]);
  press(el('gCheckBtn'));
  ok('AA3 ' + id + ' accepted one-token prefix is incomplete without bad markers',
     /sentence is incomplete/i.test(status().textContent) &&
     rowButtons().every(function (button) { return !button.classList.contains('bad'); }));
});

// =========================================================================
// AB. ACCEPTED-ORDER SCORING, RETRIES, AND REQUEUE METADATA
// =========================================================================
var abDrill = drillById('verbs-future-tense-005');
var abAccepted = EXPECTED_ACCEPTED_ORDERS[abDrill.id][0];
var abAcceptedRef = abDrill.acceptedOrders;
start([abDrill]);
submitWords(NON_AUTHORED_ORDERS[abDrill.id]);
eq('AB1 wrong first attempt banks false', G.results[0], false);
while (G.build.row.length) press(rowButtons()[rowButtons().length - 1]);
submitWords(abAccepted);
eq('AB1 accepted correction preserves original false result', G.results[0], false);
eq('AB1 accepted correction settles normally', G.state, 'done');
eq('AB1 accepted correction enables Next', el('gDrillNext').disabled, false);
activateNext();
eq('AB2 advancing requeues the missed original exactly once', G.queue.length, 2);
var abRetry = G.queue.length > 1 ? G.queue[1] : null;
ok('AB2 retry is a copy marked once with the original identity',
   !!abRetry && abRetry !== abDrill && abRetry._requeue === true &&
   abRetry.id === abDrill.id);
ok('AB2 retry preserves acceptedOrders metadata and array identity',
   !!abRetry && abRetry.acceptedOrders === abAcceptedRef &&
   JSON.stringify(abRetry.acceptedOrders) === JSON.stringify(abDrill.acceptedOrders));
if (abRetry) submitWords(abAccepted);
eq('AB3 accepted retry succeeds without changing the original miss',
   G.results, [false, true]);
eq('AB3 accepted retry causes no duplicate requeue', G.queue.length, 2);
activateNext();
eq('AB3 retry remains excluded from final score', el('gScore').textContent, '0');
eq('AB3 retry remains excluded from final denominator', el('gTotal').textContent, '1');

var abTwo = drillById('verbs-verbs-of-motion-006');
var abTwoAccepted = EXPECTED_ACCEPTED_ORDERS[abTwo.id][0];
start([abTwo]);
placeWords([abTwoAccepted[0]]);
press(el('gCheckBtn'));
eq('AB4 two-token incomplete first attempt banks false', G.results[0], false);
while (G.build.row.length) press(rowButtons()[rowButtons().length - 1]);
submitWords(abTwoAccepted);
eq('AB4 two-token accepted correction retains false', G.results[0], false);
activateNext();
eq('AB4 two-token miss requeues exactly once', G.queue.length, 2);
submitWords(abTwoAccepted);
eq('AB4 two-token accepted retry succeeds', G.results, [false, true]);
activateNext();
eq('AB4 two-token retry is excluded from score and total',
   [el('gScore').textContent, el('gTotal').textContent], ['0', '1']);

// =========================================================================
// AC. ACCEPTED-ORDER SETTLED GUARDS
// =========================================================================
var acDrill = drillById('grammar-cases-vocative-014');
var acAccepted = EXPECTED_ACCEPTED_ORDERS[acDrill.id][0];
start([acDrill]);
var acPoolHandler = handler(poolButtons()[0]);
placeWords(acAccepted);
var acRowHandler = handler(rowButtons()[0]);
press(el('gCheckBtn'));
G.build.pool[0].used = false;
var acSnapshot = {
  result: JSON.stringify(G.results),
  attempted: G.attempted,
  state: G.state,
  row: JSON.stringify(G.build.row),
  pool: JSON.stringify(G.build.pool),
  status: status().textContent,
  statusChildren: status().children,
  feedback: el('gFbBox').innerHTML,
  feedbackWrites: HTML_WRITES.gFbBox,
  focus: ACTIVE,
  nextDisabled: el('gDrillNext').disabled,
  nextLabel: el('gDrillNextLabel').textContent,
  rowSurface: rowButtons().map(function (button) { return button.textContent; })
};
if (acPoolHandler) acPoolHandler({});
if (acRowHandler) acRowHandler({});
GRAMMAR.gCheckBuild(acDrill);
eq('AC1 retained accepted-order handlers cannot change result',
   JSON.stringify(G.results), acSnapshot.result);
eq('AC1 retained accepted-order handlers cannot change attempted',
   G.attempted, acSnapshot.attempted);
eq('AC1 retained accepted-order handlers cannot change state', G.state, acSnapshot.state);
eq('AC1 retained accepted-order handlers cannot change row',
   JSON.stringify(G.build.row), acSnapshot.row);
eq('AC1 retained accepted-order handlers cannot change pool',
   JSON.stringify(G.build.pool), acSnapshot.pool);
eq('AC1 repeated accepted-order Check cannot change status',
   status().textContent, acSnapshot.status);
ok('AC1 repeated accepted-order Check cannot rebuild status',
   status().children === acSnapshot.statusChildren);
eq('AC1 repeated accepted-order Check cannot change feedback',
   el('gFbBox').innerHTML, acSnapshot.feedback);
eq('AC1 repeated accepted-order Check cannot rebuild feedback',
   HTML_WRITES.gFbBox, acSnapshot.feedbackWrites);
ok('AC1 accepted-order settled guard preserves focus', ACTIVE === acSnapshot.focus);
eq('AC1 accepted-order settled guard preserves Next',
   [el('gDrillNext').disabled, el('gDrillNextLabel').textContent],
   [acSnapshot.nextDisabled, acSnapshot.nextLabel]);
eq('AC1 accepted-order settled guard preserves authored row capitalization',
   rowButtons().map(function (button) { return button.textContent; }),
   acSnapshot.rowSurface);

// =========================================================================
// AD. PHASE 4I METADATA IMMUTABILITY AND SOURCE SCOPE
// =========================================================================
var adOrdinaryMetadata = true;
EXPECTED_ACCEPTED_IDS.forEach(function (id) {
  var entry = DRILLS.filter(function (candidate) {
    return candidate.drill.id === id;
  })[0];
  var sourceJson = JSON.stringify(entry.drill);
  var acceptedRef = entry.drill.acceptedOrders;
  var startOnly = shippingStartOnly(identityShuffle, noMix, []);
  resetG(entry.topic);
  startOnly();
  var queued = G.queue.filter(function (drill) { return drill.id === id; })[0];
  if (queued !== entry.drill || queued.acceptedOrders !== acceptedRef ||
      JSON.stringify(entry.drill) !== sourceJson) {
    adOrdinaryMetadata = false;
  }
});
ok('AD1 all six acceptedOrders survive ordinary shuffling without source mutation',
   adOrdinaryMetadata);
ok('AD1 all six authored drill objects and acceptedOrders arrays remain unchanged',
   EXPECTED_ACCEPTED_IDS.every(function (id) {
     var drill = drillById(id);
     return JSON.stringify(drill) === yAcceptedSourceBefore[id].json &&
            drill.acceptedOrders === yAcceptedSourceBefore[id].acceptedRef;
   }));

var AD_GRAMMAR_START = INDEX.indexOf('function gShuffle(');
var AD_GRAMMAR_END = INDEX.indexOf('/* ---------------- conversation (Rozmowy) ---------------- */');
var AD_OUTSIDE_GRAMMAR =
  INDEX.slice(0, AD_GRAMMAR_START) + INDEX.slice(AD_GRAMMAR_END);
eq('AD2 no non-Grammar answer system references gBuildTokenKey',
   countOf(AD_OUTSIDE_GRAMMAR, 'gBuildTokenKey'), 0);
ok('AD2 narrow helper only changes the first character and preserves the suffix',
   hasCode(CODE_G.gBuildTokenKey, 'if(typeof token!=="string"||!token)return token') &&
   hasCode(CODE_G.gBuildTokenKey,
     'return token.charAt(0).toLocaleLowerCase("pl-PL")+token.slice(1)'));
ok('AD2 gBuildTokenKey contains no trim, accent folding, punctuation stripping or whitespace collapse',
   !/trim\(|normalize\(|replace\(|split\(|join\(/.test(CODE_G.gBuildTokenKey));
ok('AD3 accepted settlement rewrites only locked-row display surface strings',
   CODE_G.gCheckBuild.indexOf('matchedOrder') !== -1 &&
   CODE_G.gCheckBuild.indexOf('textContent') !== -1);
ok('AD3 wrong-position guidance considers all valid orders through narrow keys',
   CODE_G.gCheckBuild.indexOf('validOrders') !== -1 &&
   CODE_G.gCheckBuild.indexOf('bestMatches') !== -1 &&
   CODE_G.gCheckBuild.indexOf('gBuildTokenKey') !== -1);
ok('AD3 canonical-only drills retain one valid order',
   hasCode(CODE_G.gCheckBuild, 'const validOrders=[c.answer].concat(accepted)'));

info('assertions drive the shipping Grammar functions extracted from index.html');
info('fake DOM models disabled-focus -> BODY, hidden-focus no-op, textContent vs innerHTML, and aria-label names');

console.log('Grammar interaction tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
