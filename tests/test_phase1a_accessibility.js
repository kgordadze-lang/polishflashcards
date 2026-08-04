// Deterministic tests for the Phase 1A app-shell accessibility foundation.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase1a_accessibility.js
//
// These tests exercise the shipping face-state, language and audio-name helpers
// from index.html, and inspect the semantic/contrast contract that surrounds them.
// They do not claim to replace browser accessibility-tree or screen-reader tests.

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
function countOf(hay, needle) {
  var n = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { n++; at += needle.length; }
  return n;
}
function squash(s) { return s.replace(/\s+/g, ''); }
function hasCode(hay, needle) { return squash(hay).indexOf(squash(needle)) !== -1; }

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
function tagFor(id) {
  var at = INDEX.indexOf('id="' + id + '"');
  if (at === -1) throw new Error('markup: no #' + id);
  return INDEX.slice(INDEX.lastIndexOf('<', at), INDEX.indexOf('>', at) + 1);
}
function attr(tag, name) {
  var m = tag.match(new RegExp('\\s' + name + '\\s*=\\s*"([^"]*)"'));
  return m ? m[1] : null;
}
function hasAttr(tag, name) {
  return new RegExp('\\s' + name + '(?:\\s*=|\\s|>)').test(tag);
}
function matchingDivEnd(id) {
  var idAt = INDEX.indexOf('id="' + id + '"');
  var start = INDEX.lastIndexOf('<div', idAt);
  var re = /<\/?div\b[^>]*>/gi, depth = 0, m;
  re.lastIndex = start;
  while ((m = re.exec(INDEX)) !== null) {
    if (m[0].slice(0, 2) === '</') depth--;
    else depth++;
    if (depth === 0) return re.lastIndex;
  }
  throw new Error('markup: unclosed div #' + id);
}
function section(id) {
  var marker = 'id="' + id + '"';
  var idAt = INDEX.indexOf(marker), start = INDEX.lastIndexOf('<section', idAt);
  var end = INDEX.indexOf('</section>', idAt);
  if (start === -1 || end === -1) throw new Error('markup: no section #' + id);
  return INDEX.slice(start, end + 10);
}

var STYLE = (function () {
  var out = '', at = 0;
  while ((at = INDEX.indexOf('<style', at)) !== -1) {
    var start = INDEX.indexOf('>', at) + 1, end = INDEX.indexOf('</style>', start);
    out += INDEX.slice(start, end); at = end;
  }
  return out.replace(/\/\*[\s\S]*?\*\//g, '');
})();
function cssBody(selector) {
  var re = /([^{}]+)\{([^{}]*)\}/g, m, bodies = [];
  while ((m = re.exec(STYLE)) !== null) {
    var selectors = m[1].split(',').map(function (x) { return x.trim(); });
    if (selectors.indexOf(selector) !== -1) bodies.push(m[2]);
  }
  return bodies.join(';');
}
function cssProp(selector, prop) {
  var body = cssBody(selector);
  var m = body.match(new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;}]*)'));
  return m ? m[1].trim() : null;
}

// -------------------------------------------------------------------------
// A. Inactive flip faces and native interaction structure
// -------------------------------------------------------------------------
var STUDY_FLIP = tagFor('flip'), GRAMMAR_FLIP = tagFor('gFlip');
eq('A1 study flip container has no interactive role', attr(STUDY_FLIP, 'role'), null);
eq('A1 study flip container is not a tab stop', attr(STUDY_FLIP, 'tabindex'), null);
eq('A1 grammar flip container has no interactive role', attr(GRAMMAR_FLIP, 'role'), null);
eq('A1 grammar flip container is not a tab stop', attr(GRAMMAR_FLIP, 'tabindex'), null);
['flipControl', 'gFlipControl'].forEach(function (id) {
  var tag = tagFor(id);
  ok('A2 #' + id + ' is a native button', /^<button\b/.test(tag));
  eq('A2 #' + id + ' has non-submitting type', attr(tag, 'type'), 'button');
  ok('A2 #' + id + ' has a non-generic accessible name', /^Show|^Reveal/.test(attr(tag, 'aria-label') || ''));
});
ok('A2 study native control is a sibling, not a flip descendant',
   INDEX.indexOf('id="flipControl"') > matchingDivEnd('flip'));
ok('A2 grammar native control is a sibling, not a flip descendant',
   INDEX.indexOf('id="gFlipControl"') > matchingDivEnd('gFlip'));
['flip', 'gFlip'].forEach(function (id) {
  var block = INDEX.slice(INDEX.lastIndexOf('<div', INDEX.indexOf('id="' + id + '"')), matchingDivEnd(id));
  var back = block.match(/<div\b[^>]*class="[^"]*\bback-face\b[^"]*"[^>]*>/);
  ok('A3 #' + id + ' ships its back face aria-hidden', !!back && attr(back[0], 'aria-hidden') === 'true');
  ok('A3 #' + id + ' ships its back face inert', !!back && hasAttr(back[0], 'inert'));
});

function FakeEl() { this.attrs = {}; this.inert = false; this.textContent = ''; this.innerHTML = 'unchanged'; }
FakeEl.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
FakeEl.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
FakeEl.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
function FakeClasses() { this.names = {}; }
FakeClasses.prototype.contains = function (name) { return !!this.names[name]; };
FakeClasses.prototype.add = function (name) { this.names[name] = true; };
FakeClasses.prototype.remove = function (name) { delete this.names[name]; };
FakeClasses.prototype.toggle = function (name) {
  if (this.contains(name)) this.remove(name); else this.add(name);
};
function FakeFlip() {
  this.classList = new FakeClasses(); this.faces = [new FakeEl(), new FakeEl()];
  this.faces[0].focusables = [new FakeEl(), new FakeEl()];
  this.faces[1].focusables = [new FakeEl(), new FakeEl()];
}
FakeFlip.prototype.querySelectorAll = function (selector) { return selector === '.face' ? this.faces : []; };

(0, eval)(extractFunction(INDEX, 'ppSyncFlipFaces'));
var fakeFlip = new FakeFlip();
ppSyncFlipFaces(fakeFlip);
eq('A4 front face is exposed initially', [fakeFlip.faces[0].inert, fakeFlip.faces[0].getAttribute('aria-hidden')], [false, null]);
eq('A4 back face is fully inactive initially', [fakeFlip.faces[1].inert, fakeFlip.faces[1].getAttribute('aria-hidden')], [true, 'true']);
ok('A4 inactive descendants are unreachable through the face contract',
   fakeFlip.faces[1].focusables.every(function () { return fakeFlip.faces[1].inert; }));
fakeFlip.classList.add('flipped'); ppSyncFlipFaces(fakeFlip);
eq('A5 front face becomes fully inactive after flip', [fakeFlip.faces[0].inert, fakeFlip.faces[0].getAttribute('aria-hidden')], [true, 'true']);
eq('A5 back face is exposed after flip', [fakeFlip.faces[1].inert, fakeFlip.faces[1].getAttribute('aria-hidden')], [false, null]);
fakeFlip.classList.remove('flipped'); ppSyncFlipFaces(fakeFlip);
eq('A5 state swaps back deterministically', [fakeFlip.faces[0].inert, fakeFlip.faces[1].inert], [false, true]);
var FLIP_LABEL = extractFunction(INDEX, 'flipLabel');
var G_FLIP_LABEL = extractFunction(INDEX, 'gFlipLabel');
ok('A6 study label sync covers normal and reversed directions',
   FLIP_LABEL.indexOf('enFront()') !== -1 && FLIP_LABEL.indexOf('Show Polish') !== -1 && FLIP_LABEL.indexOf('Show English') !== -1);
ok('A6 both card variants invoke the complete face synchronizer',
   hasCode(FLIP_LABEL, 'ppSyncFaceA11y()') && hasCode(G_FLIP_LABEL, 'ppSyncFlipFaces($("gFlip"))'));

// -------------------------------------------------------------------------
// B. One main landmark and per-screen headings
// -------------------------------------------------------------------------
eq('B1 document has exactly one native main landmark', countOf(INDEX, '<main '), 1);
ok('B1 #appMain is the native main element', /^<main\b/.test(tagFor('appMain')));
var MAIN_START = INDEX.indexOf('<main '), MAIN_END = INDEX.indexOf('</main>', MAIN_START);
ok('B1 footer remains outside main', MAIN_END !== -1 && MAIN_END < INDEX.indexOf('<footer'));
var SCREENS = ['home', 'study', 'grammar', 'convo', 'typeit', 'listen', 'round', 'privacy', 'about', 'contact', 'install'];
SCREENS.forEach(function (id) {
  var s = section(id), at = INDEX.indexOf('id="' + id + '"');
  ok('B2 #' + id + ' is contained by the one main', at > MAIN_START && at < MAIN_END);
  eq('B2 #' + id + ' has exactly one h1', (s.match(/<h1\b/g) || []).length, 1);
});
ok('B3 hidden screens are removed from layout', /display\s*:\s*none/.test(cssBody('.screen')));
ok('B3 only the active screen is displayed', /display\s*:\s*flex/.test(cssBody('.screen.active')));
ok('B3 completion headings remain subordinate h2 elements',
   ['doneTitle', 'gDoneTitle', 'lDoneTitle', 'rDoneTitle'].every(function (id) { return /^<h2\b/.test(tagFor(id)); }));

// -------------------------------------------------------------------------
// C. Shared language boundaries and text safety
// -------------------------------------------------------------------------
eq('C1 root document language remains English', attr(INDEX.match(/<html\b[^>]*>/)[0], 'lang'), 'en');
['appMain', 'flip', 'gFlip'].forEach(function (id) {
  eq('C1 mixed container #' + id + ' is not wholesale Polish', attr(tagFor(id), 'lang'), null);
});
(0, eval)(extractFunction(INDEX, 'ppSetSharedCardText'));
var textEl = new FakeEl(), unsafeText = 'Zażółć <img src=x onerror=alert(1)> "gęślą"';
ppSetSharedCardText(textEl, unsafeText, 'pl');
eq('C2 shared Polish text is assigned literally', textEl.textContent, unsafeText);
eq('C2 shared Polish text receives lang=pl', textEl.getAttribute('lang'), 'pl');
eq('C2 text assignment never touches innerHTML', textEl.innerHTML, 'unchanged');
ppSetSharedCardText(textEl, 'English meaning', null);
eq('C2 switching to English removes the local override', textEl.getAttribute('lang'), null);
var RENDER = extractFunction(INDEX, 'render');
ok('C3 normal Polish-front rendering uses the shared safe helper',
   hasCode(RENDER, 'ppSetSharedCardText($("plText"),c.pl,"pl")'));
ok('C3 reversed rendering moves Polish metadata with the Polish text',
   hasCode(RENDER, 'ppSetSharedCardText($("enText"),c.pl,"pl")') &&
   hasCode(RENDER, 'ppSetSharedCardText($("plText"),c.en,null)'));
ok('C3 podcast introductions explicitly restore the Polish boundary',
   RENDER.indexOf('if(c.intro)') !== -1 && hasCode(RENDER, 'ppSetSharedCardText($("plText"),c.pl,"pl")'));
ok('C3 shared Polish examples use the safe language helper',
   hasCode(RENDER, 'ppSetSharedCardText($("exPl"),c.ex,"pl")'));

// -------------------------------------------------------------------------
// D. Contextual names for shared card-face audio controls
// -------------------------------------------------------------------------
(0, eval)(extractFunction(INDEX, 'ppAudioControlName') + '\n' + extractFunction(INDEX, 'ppSetAudioControlName'));
eq('D1 pronunciation name includes the relevant Polish phrase',
   ppAudioControlName('Play pronunciation', '  dzień   dobry  '), 'Play pronunciation: dzień dobry');
eq('D1 example name includes the relevant Polish sentence',
   ppAudioControlName('Play example sentence', 'To jest żółw.'), 'Play example sentence: To jest żółw.');
ok('D1 repeated controls are distinguishable',
   ppAudioControlName('Play pronunciation', 'kot') !== ppAudioControlName('Play pronunciation', 'pies'));
ok('D1 contextual names do not degrade to generic Play',
   ppAudioControlName('Play pronunciation', 'kot') !== 'Play' && ppAudioControlName('Play example sentence', 'Kot śpi.') !== 'Play');
var audioButton = new FakeEl();
ppSetAudioControlName(audioButton, 'Play pronunciation', unsafeText);
eq('D2 learner text is assigned through the attribute API as literal text',
   audioButton.getAttribute('aria-label'), 'Play pronunciation: ' + unsafeText);
eq('D2 audio-name assignment never writes markup', audioButton.innerHTML, 'unchanged');
ok('D3 both directional main speakers use the actual shared utterance',
   hasCode(RENDER, 'const mainAudioText=ppMainAudioText(c)') &&
   hasCode(RENDER, 'ppSetAudioControlName($("speak"),"Play pronunciation",mainAudioText)') &&
   hasCode(RENDER, 'ppSetAudioControlName($("speakBack"),"Play pronunciation",mainAudioText)'));
ok('D3 shared example audio is named from its Polish example',
   hasCode(RENDER, 'ppSetAudioControlName($("speakEx"),"Play example sentence",c.ex)'));

// -------------------------------------------------------------------------
// E. Dependency-free WCAG contrast calculations and textual state cues
// -------------------------------------------------------------------------
function channel(v) {
  v /= 255;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
}
function luminance(hex) {
  var h = hex.replace('#', '');
  if (h.length === 3) h = h.split('').map(function (c) { return c + c; }).join('');
  return 0.2126 * channel(parseInt(h.slice(0, 2), 16)) +
         0.7152 * channel(parseInt(h.slice(2, 4), 16)) +
         0.0722 * channel(parseInt(h.slice(4, 6), 16));
}
function contrast(fg, bg) {
  var a = luminance(fg), b = luminance(bg), hi = Math.max(a, b), lo = Math.min(a, b);
  return (hi + 0.05) / (lo + 0.05);
}
var PAIRS = [
  ['Still learning', cssProp('.fb', 'color'), cssProp('.fb.still', 'background')],
  ['Still learning hover', cssProp('.fb', 'color'), cssProp('.fb.still:hover', 'background')],
  ['Wrong verdict', cssProp('.verdict.v-wrong', 'color'), cssProp('.verdict.v-wrong', 'background')],
  ['Wrong option', cssProp('.opt.wrong', 'color'), cssProp('.opt.wrong', 'background')]
];
PAIRS.forEach(function (pair) {
  ok('E1 ' + pair[0] + ' normal text is at least 4.5:1 (' + contrast(pair[1], pair[2]).toFixed(2) + ':1)',
     contrast(pair[1], pair[2]) >= 4.5);
});
ok('E2 original Still learning pair fails, proving the detector catches it', contrast('#ffffff', '#c97c5d') < 4.5);
ok('E2 original wrong-feedback pair fails, proving the detector catches it', contrast('#b56a4c', '#fbeee8') < 4.5);
ok('E3 Still learning remains a visible textual label', />Still learning<\/button>/.test(INDEX));
ok('E3 correct and incorrect options retain textual state cues',
   cssBody('.opt.correct::after').indexOf('Correct') !== -1 && cssBody('.opt.wrong::after').indexOf('Try again') !== -1);
ok('E3 typed wrong feedback remains textually identified', INDEX.indexOf('"Not this time"') !== -1);
ok('E3 programmatic option names still state correct and incorrect',
   INDEX.indexOf('", correct"') !== -1 && INDEX.indexOf('", incorrect. Try again"') !== -1);

console.log('Phase 1A accessibility foundation tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
