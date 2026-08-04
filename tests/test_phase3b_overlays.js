// Deterministic tests for Phase 3B-1A modal overlays.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase3b_overlays.js
//
// Issues covered:
//   MLG-3A-02  the maturity gate could not scroll; both actions left the viewport under
//              enlarged text and in short landscape.
//   MLG-3A-07  the maturity gate was the only overlay outside the Phase 2C overlay
//              contract, including Android Back.
//
// The suite executes the shipping shared-overlay helpers and background-isolation
// helpers against a realistic fake DOM, and asserts the CSS sizing contract from the
// shipping stylesheet. Real top-layer rendering, real Escape/Back key synthesis, real
// screen readers, real OS text scaling and real safe-area insets remain human checks.

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
// The shell ships more than one <style> block (fonts first, then the app sheet).
function allStyleBlocks(src) {
  var out = [], re = /<style>([\s\S]*?)<\/style>/g, m;
  while ((m = re.exec(src))) out.push(m[1]);
  return out.join('\n');
}
var STYLE = allStyleBlocks(INDEX);
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
function squash(s) { return String(s).replace(/\s+/g, ''); }
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
function elementFor(src, id) {
  var re = new RegExp('<([a-z]+)([^>]*\\sid="' + id + '")([^>]*)>');
  var m = src.match(re);
  return m ? { tag: m[1], open: m[0] } : { tag: '', open: '' };
}
function attr(tag, name) {
  var m = tag && tag.match(new RegExp('\\s' + name + '="([^"]*)"'));
  if (m) return m[1];
  return tag && new RegExp('\\s' + name + '(?:\\s|>|/)').test(tag) ? '' : null;
}
// Minimal CSS reader over the shipping <style> block: top-level rules only, comments removed.
function stripComments(css) { return css.replace(/\/\*[\s\S]*?\*\//g, ''); }
function topLevelRules(css) {
  var src = stripComments(css), out = [], i = 0;
  while (i < src.length) {
    var brace = src.indexOf('{', i);
    if (brace === -1) break;
    var prelude = src.slice(i, brace).trim();
    var depth = 0, j = brace;
    for (; j < src.length; j++) {
      if (src[j] === '{') depth++;
      else if (src[j] === '}') { depth--; if (depth === 0) break; }
    }
    out.push({ prelude: prelude, body: src.slice(brace + 1, j) });
    i = j + 1;
  }
  return out;
}
var RULES = topLevelRules(STYLE);
function ruleBody(selector) {
  for (var i = 0; i < RULES.length; i++) {
    if (RULES[i].prelude === selector) return RULES[i].body;
  }
  return null;
}
// Every declaration block in the sheet, including those nested inside media queries.
function allDeclBlocks(css) {
  var out = [];
  topLevelRules(css).forEach(function (rule) {
    if (rule.prelude.charAt(0) === '@') {
      if (/^@media/.test(rule.prelude)) {
        topLevelRules(rule.body).forEach(function (inner) {
          out.push({ selector: inner.prelude, body: inner.body, media: rule.prelude });
        });
      }
      return;
    }
    out.push({ selector: rule.prelude, body: rule.body, media: '' });
  });
  return out;
}
var DECL_BLOCKS = allDeclBlocks(STYLE);
function decl(body, prop) {
  if (body === null) return null;
  var re = new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;]+)', 'i');
  var m = body.match(re);
  return m ? m[1].trim() : null;
}

// -------------------------------------------------------------------------
// A. One modal-overlay markup contract (MLG-3A-07).
// -------------------------------------------------------------------------
var GATE = elementFor(INDEX, 'matureGate');
var DRAWER = elementFor(INDEX, 'siteDrawer');
eq('A1 the maturity gate is a native dialog', GATE.tag, 'dialog');
eq('A1 the site drawer is a native dialog', DRAWER.tag, 'dialog');
eq('A1 the old non-dialog overlay div is gone', countOf(INDEX, '<div class="modal-overlay"'), 0);
eq('A1 the gate carries no initial open attribute', attr(GATE.open, 'open'), null);
eq('A1 the gate is no longer toggled by the hidden attribute', attr(GATE.open, 'hidden'), null);
eq('A1 every modal overlay in the shell is a dialog',
   countOf(INDEX, 'class="modal-overlay"') + countOf(INDEX, 'class="site-drawer"'),
   countOf(INDEX, '<dialog class="modal-overlay"') + countOf(INDEX, '<dialog class="site-drawer"'));
eq('A1 the app ships exactly two modal overlays', countOf(INDEX, '<dialog '), 2);

var SHELL_START = INDEX.indexOf('<div class="wrap" id="appShell">');
var SHELL_END = INDEX.indexOf('<dialog class="modal-overlay" id="matureGate"');
ok('A2 both modal overlays live outside the app shell so shell isolation cannot reach them',
   SHELL_START !== -1 && SHELL_END !== -1 && SHELL_END > SHELL_START &&
   INDEX.slice(SHELL_START, SHELL_END).lastIndexOf('</div>') > INDEX.slice(SHELL_START, SHELL_END).lastIndexOf('<div'));
ok('A2 the gate precedes the drawer and neither is nested in the other',
   INDEX.indexOf('</dialog>', SHELL_END) < INDEX.indexOf('<dialog class="site-drawer"'));

eq('A3 the gate names itself from its visible heading', attr(GATE.open, 'aria-labelledby'), 'matureTitle');
eq('A3 the gate still describes itself from its body copy', attr(GATE.open, 'aria-describedby'), 'matureBody');
eq('A3 no redundant hand-written dialog role remains on the card', countOf(INDEX, 'class="modal-card" role="dialog"'), 0);
eq('A3 no redundant aria-modal remains anywhere', countOf(INDEX, 'aria-modal'), 0);
ok('A3 the gate keeps its exact approved heading and both actions',
   INDEX.indexOf('<h3 id="matureTitle">Adult language ahead</h3>') !== -1 &&
   INDEX.indexOf('<button class="modal-btn ghost" id="matureCancel">Not now</button>') !== -1 &&
   INDEX.indexOf('<button class="modal-btn solid" id="matureContinue">I\'m 18+, continue</button>') !== -1);
ok('A3 the gate keeps its exact approved body copy',
   INDEX.indexOf('This topic teaches real Polish swearing and slang, including strong, vulgar words - each shown with what it means and how offensive it is.') !== -1);

// -------------------------------------------------------------------------
// B. The gate's sizing contract (MLG-3A-02).
// -------------------------------------------------------------------------
var OVERLAY = ruleBody('.modal-overlay');
var OVERLAY_OPEN = ruleBody('.modal-overlay[open]');
var BACKDROP = ruleBody('.modal-overlay::backdrop');
var CARD = ruleBody('.modal-card');
var ACTIONS = ruleBody('.modal-actions');
var BTN = ruleBody('.modal-btn');
ok('B1 the overlay is hidden until the dialog is open', decl(OVERLAY, 'display') === 'none');
ok('B1 the open dialog centers its card', OVERLAY_OPEN !== null && decl(OVERLAY_OPEN, 'display') === 'flex' &&
   decl(OVERLAY_OPEN, 'align-items') === 'center' && decl(OVERLAY_OPEN, 'justify-content') === 'center');
ok('B1 the scrim moved to the native ::backdrop pseudo-element', BACKDROP !== null && /rgba\(/.test(decl(BACKDROP, 'background') || ''));
eq('B1 the old overlay-level scrim and hidden rule are gone',
   [countOf(STYLE, '.modal-overlay[hidden]'), countOf(STYLE, '.modal-overlay{position:fixed;inset:0;z-index:1000;background:rgba')], [0, 0]);
ok('B1 the dialog resets the user-agent dialog box so it can fill the viewport',
   decl(OVERLAY, 'border') === '0' && decl(OVERLAY, 'padding') === '0' &&
   decl(OVERLAY, 'margin') === '0' && decl(OVERLAY, 'max-width') === '100%' && decl(OVERLAY, 'max-height') === '100%');

var CARD_MAX_HEIGHT = decl(CARD, 'max-height');
ok('B2 the card declares a max-height', CARD_MAX_HEIGHT !== null);
ok('B2 the card height is bound to the dynamic viewport, not a static pixel height',
   /100dvh/.test(CARD_MAX_HEIGHT || ''));
ok('B2 the card height bound subtracts the overlay padding and the vertical safe areas',
   /env\(safe-area-inset-top\)/.test(CARD_MAX_HEIGHT || '') && /env\(safe-area-inset-bottom\)/.test(CARD_MAX_HEIGHT || ''));
eq('B2 the card scrolls internally when its content is taller', decl(CARD, 'overflow-y'), 'auto');
eq('B2 internal scrolling does not chain to the page behind', decl(CARD, 'overscroll-behavior'), 'contain');
eq('B3 the action row wraps instead of squeezing both buttons onto one line', decl(ACTIONS, 'flex-wrap'), 'wrap');
ok('B3 the actions keep a proportional basis so they can wrap under enlarged text',
   /^1\s+1\s+/.test(decl(BTN, 'flex') || '') && (decl(BTN, 'flex') || '').indexOf('0%') === -1);
['top', 'right', 'bottom', 'left'].forEach(function (side) {
  ok('B4 the open dialog pads the ' + side + ' safe-area inset',
     (decl(OVERLAY_OPEN, 'padding') || '').indexOf('env(safe-area-inset-' + side + ')') !== -1);
});
ok('B4 the drawer keeps its own safe-area padding contract unchanged',
   (decl(ruleBody('.site-drawer-panel'), 'padding') || '').indexOf('env(safe-area-inset-top)') !== -1);

// -------------------------------------------------------------------------
// C. Execute the shipping overlay contract against a realistic fake DOM.
// -------------------------------------------------------------------------
function Classes() { this.names = {}; }
Classes.prototype.contains = function (name) { return !!this.names[name]; };
Classes.prototype.add = function (name) { this.names[name] = true; };
Classes.prototype.remove = function (name) { delete this.names[name]; };
function El(id, tag) {
  this.id = id || ''; this.tag = tag || 'div'; this.attrs = {}; this.classList = new Classes();
  this.style = { display: '', visibility: '' };
  this.hidden = false; this.inert = false; this.disabled = false; this.connected = true;
  this.parentElement = null; this.children = []; this.focusCount = 0;
  this.open = false; this.showCount = 0; this.closeCount = 0; this.heading = null;
  this.isContentEditable = false; this.role = '';
}
El.prototype.append = function (child) { child.parentElement = this; this.children.push(child); return child; };
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); if (name === 'role') this.role = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.hasAttribute = function (name) { return Object.prototype.hasOwnProperty.call(this.attrs, name); };
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.closest = function (selector) {
  for (var node = this; node; node = node.parentElement) {
    if (selector === '.screen' && node.classList.contains('screen')) return node;
    if (selector !== '.screen' && node.tag === 'button' && selector.indexOf('button') !== -1) return node;
  }
  return null;
};
El.prototype.querySelector = function (selector) { return selector === 'h1' ? this.heading : null; };
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
    if (node.classList.contains('screen') && !node.classList.contains('active')) return;
  }
  this.focusCount++; this.lastFocusOptions = options || null; fakeDocument.activeElement = this;
};
El.prototype.showModal = function () { if (this.open) throw new Error('already open'); this.open = true; this.showCount++; };
El.prototype.close = function () { this.open = false; this.closeCount++; };

function makeScreen(id) {
  var screen = new El(id, 'section');
  screen.classList.add('screen');
  screen.heading = screen.append(new El(id + 'Heading', 'h1'));
  return screen;
}
var fakeBody = new El('body', 'body');
var appShell = fakeBody.append(new El('appShell'));
var home = makeScreen('home'); appShell.append(home); home.classList.add('active');
var topicTile = home.append(new El('topicTile', 'button'));
var gate = fakeBody.append(new El('matureGate', 'dialog'));
var gateCancel = gate.append(new El('matureCancel', 'button'));
var gateContinue = gate.append(new El('matureContinue', 'button'));
var drawer = fakeBody.append(new El('siteDrawer', 'dialog'));
var drawerClose = drawer.append(new El('siteMenuClose', 'button'));
var menuButton = appShell.append(new El('siteMenuButton', 'button'));
menuButton.setAttribute('aria-expanded', 'false');
var byId = { appShell: appShell, home: home, matureGate: gate, matureCancel: gateCancel,
             matureContinue: gateContinue, siteDrawer: drawer, siteMenuClose: drawerClose,
             siteMenuButton: menuButton };
var fakeDocument = {
  body: fakeBody,
  activeElement: fakeBody,
  contains: function (el) { return !!(el && el.connected); },
  querySelector: function (selector) { return selector === '.screen.active' ? home : null; },
  querySelectorAll: function (selector) { return selector === '.screen' ? [home] : []; }
};
var fakeWindow = { PP_A2HS: null, scrollTo: function () {} };
function lookup(id) { return byId[id] || null; }

var BLOCK_START = INDEX.indexOf('var ppScreenReturnTargets = new Map();');
var BLOCK_END = INDEX.indexOf('function showScreen(', BLOCK_START);
if (BLOCK_START === -1 || BLOCK_END === -1) throw new Error('shipping overlay helper block not found');
var BLOCK = INDEX.slice(BLOCK_START, BLOCK_END);
var OVERLAY_API = Function('document', 'window', 'lookup',
  'var $ = lookup;\n' + BLOCK + '\nreturn {' +
  'open:ppOpenSharedOverlay,close:ppCloseSharedOverlay,take:ppTakeSharedOverlayInvoker,' +
  'isolate:ppIsolateSiteMenuBackground,restore:ppRestoreSiteMenuBackground,' +
  'openMenu:ppOpenSiteMenu,closeMenu:ppCloseSiteMenu,menuOpen:ppSiteMenuIsOpen,' +
  'background:function(){return ppSiteMenuBackground;}};')(fakeDocument, fakeWindow, lookup);

fakeDocument.activeElement = topicTile;
ok('C1 the gate opens through the shared contract', OVERLAY_API.open(gate, gateCancel));
ok('C1 opening goes through the native modal path', gate.open && gate.showCount === 1);
ok('C1 focus lands on the safe default action', fakeDocument.activeElement === gateCancel);
eq('C1 the initial action receives one explicit focus move', gateCancel.focusCount, 1);
eq('C1 focus uses preventScroll', gateCancel.lastFocusOptions, { preventScroll: true });
ok('C1 the app shell becomes inert', appShell.inert && appShell.hasAttribute('inert'));
eq('C1 the app shell is hidden from the accessibility tree', appShell.getAttribute('aria-hidden'), 'true');
ok('C1 body scrolling is locked by the same reversible class the drawer uses',
   fakeBody.classList.contains('site-menu-open'));
topicTile.focus();
ok('C2 a background control cannot take focus while the gate is open', fakeDocument.activeElement === gateCancel);
eq('C2 repeated open is ignored', OVERLAY_API.open(gate, gateCancel), false);
eq('C2 repeated open does not call showModal twice', gate.showCount, 1);
eq('C2 the drawer cannot stack on top of the gate', OVERLAY_API.openMenu(), false);
eq('C2 no second modal layer opened', drawer.open, false);

ok('C3 the gate closes through the shared contract', OVERLAY_API.close(gate));
ok('C3 the dialog is closed', !gate.open);
ok('C3 app-shell inertness is removed', !appShell.inert && !appShell.hasAttribute('inert'));
eq('C3 app-shell aria-hidden is removed', appShell.getAttribute('aria-hidden'), null);
ok('C3 body scrolling is restored', !fakeBody.classList.contains('site-menu-open'));
ok('C3 focus returns to the control that opened the gate', fakeDocument.activeElement === topicTile);
eq('C3 the invoker is restored exactly once', topicTile.focusCount, 1);
eq('C3 repeated close is ignored', OVERLAY_API.close(gate), false);
topicTile.focus();
ok('C3 no focus trap remains after close', fakeDocument.activeElement === topicTile);

// Verbatim restoration of pre-existing background state, as the drawer already guarantees.
appShell.inert = true; appShell.setAttribute('inert', 'existing');
appShell.setAttribute('aria-hidden', 'false'); fakeBody.classList.add('site-menu-open');
ok('C4 isolation records pre-existing background state', OVERLAY_API.isolate());
eq('C4 isolation still hides the shell while active', appShell.getAttribute('aria-hidden'), 'true');
ok('C4 restoration succeeds', OVERLAY_API.restore());
ok('C4 a prior inert property is restored', appShell.inert);
eq('C4 a prior inert attribute value is restored verbatim', appShell.getAttribute('inert'), 'existing');
eq('C4 a prior aria-hidden value is restored verbatim', appShell.getAttribute('aria-hidden'), 'false');
ok('C4 a pre-existing body lock class is not removed', fakeBody.classList.contains('site-menu-open'));
appShell.inert = false; appShell.removeAttribute('inert');
appShell.removeAttribute('aria-hidden'); fakeBody.classList.remove('site-menu-open');
eq('C4 one overlay cannot isolate over another overlay\'s recorded state',
   [OVERLAY_API.isolate(), OVERLAY_API.isolate()], [true, false]);
OVERLAY_API.restore();

fakeDocument.activeElement = topicTile;
ok('C5 the drawer opens when nothing is stacked', OVERLAY_API.openMenu());
eq('C5 the gate cannot stack on top of the drawer', OVERLAY_API.open(gate, gateCancel), false);
eq('C5 the refused gate never entered the top layer', [gate.open, gate.showCount], [false, 1]);
ok('C5 the drawer close path is unaffected', OVERLAY_API.closeMenu(true));
ok('C5 both overlays end closed and the app is interactive',
   !gate.open && !drawer.open && !appShell.inert && !fakeBody.classList.contains('site-menu-open'));

// Fail closed: an unusable initial target must leave nothing open and nothing isolated.
fakeDocument.activeElement = topicTile;
gateCancel.connected = false;
eq('C6 an unusable initial action aborts the open', OVERLAY_API.open(gate, gateCancel), false);
ok('C6 a failed open leaves no dialog open, no inert shell and no recorded background',
   !gate.open && !appShell.inert && !fakeBody.classList.contains('site-menu-open') && !OVERLAY_API.background());
gateCancel.connected = true;

// The continue path takes the invoker itself and closes without an intermediate focus move.
fakeDocument.activeElement = topicTile; topicTile.focusCount = 0;
OVERLAY_API.open(gate, gateCancel);
var continuedInvoker = OVERLAY_API.take(gate);
ok('C7 the continue path receives the original invoker', continuedInvoker === topicTile);
ok('C7 closing without focus restoration still closes', OVERLAY_API.close(gate, false));
eq('C7 no intermediate focus move happens before the activity renders', topicTile.focusCount, 0);
ok('C7 the background is released even on the no-focus close path',
   !appShell.inert && !fakeBody.classList.contains('site-menu-open'));

// A dead invoker falls back to the current screen rather than focusing nothing.
fakeDocument.activeElement = topicTile;
OVERLAY_API.open(gate, gateCancel);
topicTile.connected = false; home.heading.focusCount = 0;
OVERLAY_API.close(gate);
ok('C8 an invalid invoker falls back to the active screen heading', fakeDocument.activeElement === home.heading);
eq('C8 the fallback focuses exactly once', home.heading.focusCount, 1);
topicTile.connected = true;

for (var cycle = 0; cycle < 3; cycle++) {
  fakeDocument.activeElement = topicTile;
  ok('C9 repeated cycle ' + (cycle + 1) + ' opens', OVERLAY_API.open(gate, gateCancel));
  ok('C9 repeated cycle ' + (cycle + 1) + ' closes', OVERLAY_API.close(gate));
}
ok('C9 repeated cycles end with the app fully interactive',
   !gate.open && !appShell.inert && !appShell.hasAttribute('aria-hidden') &&
   !fakeBody.classList.contains('site-menu-open') && !OVERLAY_API.background());
eq('C9 repeated cycles leave no leaked return targets', OVERLAY_API.take(gate), null);

// -------------------------------------------------------------------------
// D. Shipping wiring: cancel, close, backdrop, and the removed manual trap.
// -------------------------------------------------------------------------
ok('D1 Escape and Android Back reach the gate as the dialog cancel event',
   INDEX.indexOf('$("matureGate").addEventListener("cancel"') !== -1);
ok('D1 the gate consumes cancel only after a successful close, exactly as the drawer does',
   hasCode(INDEX, '$("matureGate").addEventListener("cancel", e=>{ if(closeMatureGate()) e.preventDefault(); });'));
ok('D1 the drawer keeps its own identical cancel contract',
   hasCode(INDEX, 'if(ppCloseSiteMenu(true)) e.preventDefault()'));
eq('D2 the old manual Escape and Tab focus trap is gone',
   countOf(INDEX, '$("matureGate").addEventListener("keydown"'), 0);
eq('D2 no hand-rolled Tab cycling remains for the gate', countOf(INDEX, 'e.shiftKey && document.activeElement === first'), 0);
eq('D2 no document-level Escape handler was introduced',
   countOf(INDEX, 'document.addEventListener("keydown", e=>{ if(e.key === "Escape"'), 0);
ok('D3 an unexpected native close still releases the background',
   hasCode(extractFunction(INDEX, 'closeMatureGate'), 'ppCloseSharedOverlay($("matureGate"))') &&
   INDEX.indexOf('$("matureGate").addEventListener("close"') !== -1 &&
   hasCode(INDEX.slice(INDEX.indexOf('$("matureGate").addEventListener("close"')), 'ppRestoreSiteMenuBackground()'));
ok('D3 an unexpected native close also clears the pending topic',
   hasCode(INDEX.slice(INDEX.indexOf('$("matureGate").addEventListener("close"')), 'pendingTopic = null'));
ok('D4 backdrop activation reuses the one close helper',
   hasCode(INDEX, '$("matureGate").addEventListener("click", e=>{ if(e.target === $("matureGate")) closeMatureGate(); });'));
ok('D4 the visible Not now action reuses the same close helper',
   INDEX.indexOf('$("matureCancel").addEventListener("click", closeMatureGate)') !== -1);
ok('D5 the gate fails closed when the modal cannot be opened',
   hasCode(extractFunction(INDEX, 'openTopic'),
           'if(!ppOpenSharedOverlay($("matureGate"), $("matureCancel"))) pendingTopic = null;'));
ok('D5 the continue path routes the topic and keeps the tile as the return target',
   hasCode(INDEX, 'ppCloseSharedOverlay($("matureGate"), false);') &&
   hasCode(INDEX, 'ppUseInvokerForNextScreen(invoker);') &&
   hasCode(INDEX, 'if(p) routeTopic(p.li, p.ti, p.t);'));
eq('D5 the gate no longer toggles the hidden attribute anywhere',
   countOf(INDEX, '$("matureGate").hidden'), 0);
ok('D6 both overlays isolate the background through the same function',
   hasCode(extractFunction(INDEX, 'ppOpenSharedOverlay'), 'ppIsolateSiteMenuBackground()') &&
   hasCode(extractFunction(INDEX, 'ppOpenSiteMenu'), 'ppIsolateSiteMenuBackground()'));
ok('D6 both overlays restore the background through the same function',
   hasCode(extractFunction(INDEX, 'ppCloseSharedOverlay'), 'ppRestoreSiteMenuBackground()') &&
   hasCode(extractFunction(INDEX, 'ppCloseSiteMenu'), 'ppRestoreSiteMenuBackground()'));
eq('D6 there is exactly one isolate and one restore implementation',
   [countOf(INDEX, 'function ppIsolateSiteMenuBackground('), countOf(INDEX, 'function ppRestoreSiteMenuBackground(')], [1, 1]);
eq('D6 one body scroll-lock class serves both overlays', countOf(STYLE, 'body.site-menu-open{overflow:hidden}'), 1);
ok('D7 the shared open helper refuses to stack a second modal layer',
   hasCode(extractFunction(INDEX, 'ppOpenSharedOverlay'), 'if(ppSiteMenuIsOpen()) return false'));
ok('D7 the drawer refuses to stack on the gate by reading its open state',
   hasCode(extractFunction(INDEX, 'ppOpenSiteMenu'), 'if(mature && mature.open) return false'));
eq('D8 the gate helpers create no History API state of their own',
   [countOf(extractFunction(INDEX, 'openTopic'), 'history.'),
    countOf(extractFunction(INDEX, 'closeMatureGate'), 'history.'),
    countOf(extractFunction(INDEX, 'ppOpenSharedOverlay'), 'history.'),
    countOf(extractFunction(INDEX, 'ppCloseSharedOverlay'), 'history.')], [0, 0, 0, 0]);
eq('D8 the gate does not stop or restart audio, or touch stored progress',
   countOf(extractFunction(INDEX, 'ppOpenSharedOverlay'), 'localStorage') +
   countOf(extractFunction(INDEX, 'ppCloseSharedOverlay'), 'localStorage') +
   countOf(extractFunction(INDEX, 'openTopic'), 'stopAllAudio'), 0);
ok('D9 the adult-language gate is still shown on every open and never persisted',
   INDEX.indexOf('/* re-prompt every time; never persisted */') !== -1 &&
   countOf(INDEX, 'popolsku-mature') === 0);

console.log('Phase 3B-1A overlay tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] MLG-3A-02 and MLG-3A-07: shipping shared-overlay and isolation helpers run against deterministic modal, focus, inert and stacking state');
console.log('  [info] real top-layer rendering, Escape/Android Back key synthesis, screen readers, OS text scaling and safe-area insets remain manual');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
