// Deterministic tests for the Phase 1B shared keyboard and focus foundation.
// Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_phase1b_keyboard_focus.js
//
// The suite drives the shipping helpers extracted from index.html against a fake
// DOM. It proves routing and shortcut decisions, not browser rendering, platform
// key synthesis, accessibility-tree output, or screen-reader announcements.

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

// -------------------------------------------------------------------------
// Fake DOM: visibility/inertness, active screens, focus, and closest owners.
// -------------------------------------------------------------------------
function Classes(names) {
  this.names = {};
  (names || []).forEach(function (name) { this.names[name] = true; }, this);
}
Classes.prototype.contains = function (name) { return !!this.names[name]; };
Classes.prototype.add = function (name) { this.names[name] = true; };
Classes.prototype.remove = function (name) { delete this.names[name]; };

function El(id, tag) {
  this.id = id || '';
  this.tag = tag || 'div';
  this.attrs = {};
  this.classList = new Classes();
  this.style = { display: '', visibility: '' };
  this.hidden = false;
  this.inert = false;
  this.disabled = false;
  this.connected = true;
  this.parentElement = null;
  this.children = [];
  this.heading = null;
  this.focusCount = 0;
  this.lastFocusOptions = null;
  this.dataset = {};
  this.role = '';
  this.isContentEditable = false;
  this.open = false;
}
// Modal overlays are native dialogs, so the shared overlay helpers drive showModal/close
// rather than the hidden attribute. Phase 3B-1A converted the maturity gate to that
// contract; tests/test_phase3b_overlays.js owns the full modal contract.
El.prototype.showModal = function () { if (this.open) throw new Error('already open'); this.open = true; };
El.prototype.close = function () { this.open = false; };
El.prototype.append = function (child) { child.parentElement = this; this.children.push(child); return child; };
El.prototype.setAttribute = function (name, value) {
  this.attrs[name] = String(value);
  if (name === 'role') this.role = String(value);
};
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.hasAttribute = function (name) { return Object.prototype.hasOwnProperty.call(this.attrs, name); };
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; if (name === 'role') this.role = ''; };
El.prototype.querySelector = function (selector) { return selector === 'h1' ? this.heading : null; };
El.prototype.closest = function (selector) {
  for (var node = this; node; node = node.parentElement) {
    if (selector === '.screen' && node.classList.contains('screen')) return node;
    if (selector !== '.screen') {
      if (node.tag === 'button' && selector.indexOf('button') !== -1) return node;
      if (node.tag === 'a' && node.getAttribute('href') !== null && selector.indexOf('a[href]') !== -1) return node;
      if (['input','textarea','select','summary','audio','video','iframe','object','embed'].indexOf(node.tag) !== -1 && selector.indexOf(node.tag) !== -1) return node;
      if (node.isContentEditable && selector.indexOf('[contenteditable]') !== -1) return node;
      if (node.disabled && selector.indexOf('[disabled]') !== -1) return node;
      if (node.getAttribute('aria-disabled') === 'true' && selector.indexOf("[aria-disabled='true']") !== -1) return node;
      if (node.role && selector.indexOf("[role='" + node.role + "']") !== -1) return node;
      if (node.getAttribute('tabindex') !== null && node.getAttribute('tabindex') !== '-1' && selector.indexOf('[tabindex]') !== -1) return node;
    }
  }
  return null;
};
El.prototype.focus = function (options) {
  if (!this.connected || this.disabled) return;
  for (var node = this; node; node = node.parentElement) {
    if (node.hidden || node.inert || node.getAttribute('aria-hidden') === 'true') return;
    if (node.classList.contains('screen') && !node.classList.contains('active')) return;
  }
  this.focusCount++;
  this.lastFocusOptions = options || null;
  document.activeElement = this;
};

function makeScreen(id) {
  var screen = new El(id, 'section');
  screen.classList.add('screen');
  var heading = screen.append(new El(id + 'Heading', 'h1'));
  screen.heading = heading;
  return screen;
}
var home = makeScreen('home'), study = makeScreen('study'), about = makeScreen('about');
var screens = [home, study, about];
var footer = new El('footer', 'footer');
var body = new El('body', 'body');
// The shared overlay contract isolates the app shell and locks body scrolling, so the
// harness supplies both. Screens sit inside the shell, exactly as they ship.
var appShell = body.append(new El('appShell'));
screens.forEach(function (s) { appShell.append(s); });
var byId = { home:home, study:study, about:about, appShell:appShell };
var document = {
  body: body,
  activeElement: body,
  contains: function (el) { return !!(el && el.connected); },
  querySelector: function (selector) {
    if (selector === '.screen.active') {
      for (var i = 0; i < screens.length; i++) if (screens[i].classList.contains('active')) return screens[i];
    }
    if (selector === 'footer') return footer;
    return null;
  },
  querySelectorAll: function (selector) { return selector === '.screen' ? screens : []; }
};
var window = { PP_A2HS:null, scrollCount:0, scrollTo:function () { this.scrollCount++; } };
function lookup(id) { return byId[id]; }
function activate(screen) {
  screens.forEach(function (s) { s.classList.remove('active'); });
  screen.classList.add('active');
}
function clearFocusCounts() {
  [home, study, about, home.heading, study.heading, about.heading, footer, body].forEach(function (el) { el.focusCount = 0; });
}

var FOCUS_START = INDEX.indexOf('var ppScreenReturnTargets = new Map();');
var FOCUS_END = INDEX.indexOf('function showScreen(', FOCUS_START);
if (FOCUS_START === -1 || FOCUS_END === -1) throw new Error('focus helper block not found');
var FOCUS_FACTORY = Function('document', 'window', 'lookup',
  'var $ = lookup;\n' + INDEX.slice(FOCUS_START, FOCUS_END) + '\n' + extractFunction(INDEX, 'showScreen') +
  '\nreturn {' +
  'ppScreenReturnTargets:ppScreenReturnTargets,ppOverlayReturnTargets:ppOverlayReturnTargets,' +
  'ppIsInteractiveTarget:ppIsInteractiveTarget,ppIsHiddenOrInert:ppIsHiddenOrInert,' +
  'ppCanFocus:ppCanFocus,ppFocusElement:ppFocusElement,ppScreenEntryTarget:ppScreenEntryTarget,' +
  'ppCurrentScreen:ppCurrentScreen,ppRememberScreenInvoker:ppRememberScreenInvoker,' +
  'ppUseInvokerForNextScreen:ppUseInvokerForNextScreen,ppRouteScreenFocus:ppRouteScreenFocus,' +
  'ppOpenSharedOverlay:ppOpenSharedOverlay,ppTakeSharedOverlayInvoker:ppTakeSharedOverlayInvoker,' +
  'ppCloseSharedOverlay:ppCloseSharedOverlay,showScreen:showScreen};');
var FOCUS = FOCUS_FACTORY(document, window, lookup);
var ppScreenReturnTargets=FOCUS.ppScreenReturnTargets, ppOverlayReturnTargets=FOCUS.ppOverlayReturnTargets;
var ppIsInteractiveTarget=FOCUS.ppIsInteractiveTarget, ppIsHiddenOrInert=FOCUS.ppIsHiddenOrInert;
var ppCanFocus=FOCUS.ppCanFocus, ppFocusElement=FOCUS.ppFocusElement, ppScreenEntryTarget=FOCUS.ppScreenEntryTarget;
var ppRememberScreenInvoker=FOCUS.ppRememberScreenInvoker, ppUseInvokerForNextScreen=FOCUS.ppUseInvokerForNextScreen;
var ppRouteScreenFocus=FOCUS.ppRouteScreenFocus;
var ppOpenSharedOverlay=FOCUS.ppOpenSharedOverlay, ppTakeSharedOverlayInvoker=FOCUS.ppTakeSharedOverlayInvoker;
var ppCloseSharedOverlay=FOCUS.ppCloseSharedOverlay, showScreen=FOCUS.showScreen;

// -------------------------------------------------------------------------
// A. Shared screen routing and return focus.
// -------------------------------------------------------------------------
activate(home);
var topic = home.append(new El('topic', 'button'));
document.activeElement = topic;
clearFocusCounts();
showScreen('study');
ok('A1 opening Study focuses its stable heading', document.activeElement === study.heading);
eq('A1 exactly one final focus move occurs', study.heading.focusCount, 1);
eq('A1 programmatic heading stays out of the Tab sequence', study.heading.getAttribute('tabindex'), '-1');
ok('A1 destination is active before focus', study.classList.contains('active'));
ok('A1 focus target is visible and not inert', !ppIsHiddenOrInert(study.heading));
eq('A1 focus requests prevent scrolling', study.heading.lastFocusOptions, {preventScroll:true});
eq('A1 transition scrolls once through the existing shell behavior', window.scrollCount, 1);

var renderedEntry = study.append(new El('renderedEntry', 'input'));
activate(home); document.activeElement = topic; renderedEntry.focusCount = 0; study.heading.focusCount = 0;
showScreen('study', true); renderedEntry.focus();
ok('A2 a visible activity entry target is retained', document.activeElement === renderedEntry);
eq('A2 pointer-originated transition creates no duplicate focus move', [renderedEntry.focusCount, study.heading.focusCount], [1,0]);

activate(home); document.activeElement = topic; ppScreenReturnTargets.clear();
ppRememberScreenInvoker('study');
showScreen('study');
clearFocusCounts();
showScreen('home');
ok('A3 returning from Study restores its invoking topic', document.activeElement === topic);
eq('A3 restored invoker is focused exactly once', topic.focusCount, 1);

function invalidReturnCase(name, mutate) {
  topic.connected = true; topic.hidden = false; topic.inert = false; topic.disabled = false; topic.tag = 'button';
  topic.attrs = {}; topic.focusCount = 0; activate(home); document.activeElement = topic; ppScreenReturnTargets.clear();
  ppRememberScreenInvoker('study'); showScreen('study'); mutate(topic);
  home.heading.focusCount = 0; showScreen('home');
  ok(name + ' uses the home heading fallback', document.activeElement === home.heading);
  eq(name + ' does not focus the invalid invoker', topic.focusCount, 0);
}
invalidReturnCase('A4 disconnected invoker', function (el) { el.connected = false; });
invalidReturnCase('A4 hidden invoker', function (el) { el.hidden = true; });
invalidReturnCase('A4 disabled invoker', function (el) { el.disabled = true; });
invalidReturnCase('A4 inert invoker', function (el) { el.inert = true; });
invalidReturnCase('A4 no-longer-operable invoker', function (el) { el.tag = 'div'; });

topic.connected = true; topic.hidden = false; topic.inert = false; topic.disabled = false; topic.tag = 'button';
var inactiveFace = study.append(new El('inactiveFace'));
inactiveFace.inert = true; inactiveFace.setAttribute('aria-hidden', 'true');
var faceControl = inactiveFace.append(new El('faceControl', 'button'));
activate(home); document.activeElement = topic; faceControl.focusCount = 0; study.heading.focusCount = 0;
showScreen('study', true); faceControl.focus(); ppRouteScreenFocus(home, study);
ok('A5 inactive-face content is rejected as the final target', document.activeElement === study.heading);
eq('A5 the shared router never focuses inactive-face content itself', faceControl.focusCount, 0);
eq('A5 the visible heading receives the final routed focus', study.heading.focusCount, 1);

activate(study); document.activeElement = study.heading; study.heading.focusCount = 0;
showScreen('study');
eq('A6 re-showing the active screen does not move focus', study.heading.focusCount, 0);

// -------------------------------------------------------------------------
// B. Shared overlay invocation, restoration, and fallback.
// -------------------------------------------------------------------------
// The overlay is a native dialog outside the app shell, as the maturity gate ships.
var overlay = new El('matureGate', 'dialog');
var cancel = overlay.append(new El('matureCancel', 'button'));
activate(home); topic.connected = true; topic.hidden = false; topic.inert = false; topic.disabled = false;
document.activeElement = topic; ppOverlayReturnTargets.clear(); topic.focusCount = 0; cancel.focusCount = 0;
ok('B1 overlay opens and focuses its safe initial control', ppOpenSharedOverlay(overlay, cancel));
ok('B1 opening focus lands after the overlay is in the top layer', overlay.open && document.activeElement === cancel);
ok('B1 the app shell is isolated while the overlay is open',
   appShell.inert && appShell.getAttribute('aria-hidden') === 'true' && body.classList.contains('site-menu-open'));
ok('B1 closing the overlay reports a completed close', ppCloseSharedOverlay(overlay));
ok('B1 close leaves the dialog closed and the shell interactive',
   !overlay.open && !appShell.inert && appShell.getAttribute('aria-hidden') === null && !body.classList.contains('site-menu-open'));
ok('B1 close restores the valid invoker', document.activeElement === topic);
eq('B1 valid invoker is restored once', topic.focusCount, 1);
eq('B1 closing an already-closed overlay is ignored', ppCloseSharedOverlay(overlay), false);

function invalidOverlayCase(name, mutate) {
  if (overlay.open) ppCloseSharedOverlay(overlay, false);
  topic.connected = true; topic.hidden = false; topic.inert = false; topic.disabled = false; topic.tag = 'button'; topic.attrs = {};
  activate(home); document.activeElement = topic; ppOverlayReturnTargets.clear();
  ppOpenSharedOverlay(overlay, cancel); mutate(topic); home.heading.focusCount = 0; topic.focusCount = 0;
  ppCloseSharedOverlay(overlay);
  ok(name + ' falls back to the active screen heading', document.activeElement === home.heading);
  eq(name + ' is never focused', topic.focusCount, 0);
}
invalidOverlayCase('B2 disconnected overlay invoker', function (el) { el.connected = false; });
invalidOverlayCase('B2 hidden overlay invoker', function (el) { el.hidden = true; });
invalidOverlayCase('B2 disabled overlay invoker', function (el) { el.disabled = true; });
invalidOverlayCase('B2 inert overlay invoker', function (el) { el.inert = true; });
invalidOverlayCase('B2 no-longer-operable overlay invoker', function (el) { el.tag = 'div'; });

topic.connected = true; topic.hidden = false; topic.inert = false; topic.disabled = false; topic.tag = 'button';
if (overlay.open) ppCloseSharedOverlay(overlay, false);
activate(home); document.activeElement = topic; ppOverlayReturnTargets.clear();
ppOpenSharedOverlay(overlay, cancel);
// "I'm 18+, continue" takes the invoker itself, then closes without an intermediate focus move.
var continuedInvoker = ppTakeSharedOverlayInvoker(overlay); ppCloseSharedOverlay(overlay, false);
ppUseInvokerForNextScreen(continuedInvoker); document.activeElement = cancel;
ppRememberScreenInvoker('study');
ok('B3 continuing through the gate preserves the topic as Study return target', ppScreenReturnTargets.get('study') === topic);

// -------------------------------------------------------------------------
// C. Actual shipping Study shortcut decision path.
// -------------------------------------------------------------------------
var KEYBOARD_SOURCE = [
  extractFunction(INDEX, 'ppGlobalShortcutBlocked'),
  extractFunction(INDEX, 'ppHandleStudyShortcut'),
  extractFunction(INDEX, 'ppStudyShortcutKeydown')
].join('\n');

var doneView = new El('doneView'); doneView.style.display = 'none';
var flipCard = study.append(new El('flip')); flipCard.dataset = {};
byId.doneView = doneView; byId.flip = flipCard;
var S = { queue:[0,1,2], pos:1 };
var actions = { advance:0, prev:0, flip:0 };
function advance() { actions.advance++; }
function goPrev() { actions.prev++; }
function flip() { actions.flip++; }
var KEYBOARD_FACTORY = Function('lookup', 'ppIsHiddenOrInert', 'ppIsInteractiveTarget', 'S', 'advance', 'goPrev', 'flip',
  'var $ = lookup;\n' + KEYBOARD_SOURCE +
  '\nreturn {ppGlobalShortcutBlocked:ppGlobalShortcutBlocked,ppHandleStudyShortcut:ppHandleStudyShortcut,ppStudyShortcutKeydown:ppStudyShortcutKeydown};');
var KEYBOARD = KEYBOARD_FACTORY(lookup, ppIsHiddenOrInert, ppIsInteractiveTarget, S, advance, goPrev, flip);
var ppGlobalShortcutBlocked=KEYBOARD.ppGlobalShortcutBlocked;
var ppHandleStudyShortcut=KEYBOARD.ppHandleStudyShortcut;
var ppStudyShortcutKeydown=KEYBOARD.ppStudyShortcutKeydown;
function keyEvent(key, target, options) {
  var e = { key:key, target:target, defaultPrevented:false, repeat:false, isComposing:false,
            altKey:false, ctrlKey:false, metaKey:false, shiftKey:false, preventCount:0 };
  Object.keys(options || {}).forEach(function (k) { e[k] = options[k]; });
  e.preventDefault = function () { this.defaultPrevented = true; this.preventCount++; };
  return e;
}
function runIgnored(name, key, target, options) {
  actions = { advance:0, prev:0, flip:0 };
  var e = keyEvent(key, target, options);
  eq(name + ' is ignored', ppStudyShortcutKeydown(e), false);
  eq(name + ' runs no app action', actions, {advance:0,prev:0,flip:0});
  eq(name + ' is not cancelled', e.preventCount, 0);
}

activate(study); doneView.style.display = 'none'; S.queue = [0,1,2]; S.pos = 1; flipCard.dataset = {};
var cardSpace = study.append(new El('cardSpace'));
actions = {advance:0,prev:0,flip:0};
var space = keyEvent(' ', cardSpace);
eq('C1 Space on non-interactive card space is handled', ppStudyShortcutKeydown(space), true);
eq('C1 Space flips once', actions.flip, 1);
eq('C1 performed Space shortcut is cancelled once', space.preventCount, 1);
actions = {advance:0,prev:0,flip:0};
var right = keyEvent('ArrowRight', cardSpace);
ppStudyShortcutKeydown(right);
eq('C1 ArrowRight advances once', actions.advance, 1);
eq('C1 performed ArrowRight is cancelled once', right.preventCount, 1);
actions = {advance:0,prev:0,flip:0};
var left = keyEvent('ArrowLeft', cardSpace);
ppStudyShortcutKeydown(left);
eq('C1 ArrowLeft moves back once when available', actions.prev, 1);
eq('C1 performed ArrowLeft is cancelled once', left.preventCount, 1);

var audioButton = study.append(new El('speak', 'button'));
runIgnored('C2 Space on an audio button', ' ', audioButton);
runIgnored('C2 Enter on an audio button', 'Enter', audioButton);
var flipButton = study.append(new El('flipControl', 'button'));
runIgnored('C2 Space on the native flip button', ' ', flipButton);
runIgnored('C2 Enter on the native flip button', 'Enter', flipButton);
var link = study.append(new El('link', 'a')); link.setAttribute('href', '#target');
runIgnored('C2 Enter on a link', 'Enter', link);
['input','textarea','select','summary','audio','video'].forEach(function (tag) {
  runIgnored('C3 ArrowRight on ' + tag, 'ArrowRight', study.append(new El('native-' + tag, tag)));
});
var editable = study.append(new El('editable')); editable.isContentEditable = true;
runIgnored('C3 Space on contenteditable', ' ', editable);
['button','radio','slider','menu','menubar','listbox','radiogroup','tablist','tree','grid','toolbar'].forEach(function (role) {
  var control = study.append(new El('role-' + role)); control.setAttribute('role', role);
  runIgnored('C3 ArrowRight on ARIA ' + role, 'ArrowRight', control);
});
var composite = study.append(new El('composite')); composite.setAttribute('role', 'menu');
var compositeChild = composite.append(new El('compositeChild'));
runIgnored('C3 descendant inside a composite', 'ArrowDown', compositeChild);
var buttonOwner = study.append(new El('buttonOwner', 'button'));
var buttonChild = buttonOwner.append(new El('buttonChild'));
runIgnored('C3 descendant inside a native button', ' ', buttonChild);
var disabled = study.append(new El('disabled', 'button')); disabled.disabled = true;
runIgnored('C3 disabled control', ' ', disabled);
var hiddenParent = study.append(new El('hiddenParent')); hiddenParent.hidden = true;
runIgnored('C3 hidden subtree', ' ', hiddenParent.append(new El('hiddenChild')));
var inertParent = study.append(new El('inertParent')); inertParent.inert = true;
runIgnored('C3 inert subtree', 'ArrowRight', inertParent.append(new El('inertChild')));
var ariaHiddenParent = study.append(new El('ariaHiddenParent')); ariaHiddenParent.setAttribute('aria-hidden', 'true');
runIgnored('C3 aria-hidden subtree', 'ArrowLeft', ariaHiddenParent.append(new El('ariaHiddenChild')));

runIgnored('C4 already-handled event', ' ', cardSpace, {defaultPrevented:true});
runIgnored('C4 repeated keydown', ' ', cardSpace, {repeat:true});
runIgnored('C4 composing key event', ' ', cardSpace, {isComposing:true});
['altKey','ctrlKey','metaKey','shiftKey'].forEach(function (modifier) {
  var options = {}; options[modifier] = true;
  runIgnored('C4 ' + modifier + ' combination', 'ArrowRight', cardSpace, options);
});
runIgnored('C4 unclaimed Enter key', 'Enter', cardSpace);
runIgnored('C4 unclaimed ArrowUp key', 'ArrowUp', cardSpace);
runIgnored('C4 unclaimed ArrowDown key', 'ArrowDown', cardSpace);

activate(home);
runIgnored('C5 shortcut on an inactive Study screen', ' ', cardSpace);
activate(study); doneView.style.display = 'flex';
runIgnored('C5 shortcut on the completion view', ' ', cardSpace);
doneView.style.display = 'none'; S.pos = 0;
runIgnored('C5 unavailable previous action', 'ArrowLeft', cardSpace);
S.pos = 1; flipCard.dataset.leaving = '1';
runIgnored('C5 shortcut while the card is leaving', ' ', cardSpace);
flipCard.dataset = {}; S.queue = [];
runIgnored('C5 shortcut without an available card', 'ArrowRight', cardSpace);
S.queue = [0,1,2]; S.pos = 1;

actions = {advance:0,prev:0,flip:0};
var nativeSpace = keyEvent(' ', flipButton);
ppStudyShortcutKeydown(nativeSpace); flip(); // the browser's one native click
eq('C6 native Space plus the global path produces exactly one flip', actions.flip, 1);
eq('C6 native Space is not cancelled by the global path', nativeSpace.preventCount, 0);
actions = {advance:0,prev:0,flip:0};
var nativeEnter = keyEvent('Enter', flipButton);
ppStudyShortcutKeydown(nativeEnter); flip(); // the browser's one native click
eq('C6 native Enter plus the global path produces exactly one flip', actions.flip, 1);
eq('C6 native Enter is not cancelled by the global path', nativeEnter.preventCount, 0);
actions = {advance:0,prev:0,flip:0};
var audioSpace = keyEvent(' ', audioButton);
ppStudyShortcutKeydown(audioSpace);
eq('C6 Space on audio never flips the card', actions.flip, 0);

// -------------------------------------------------------------------------
// D. Source-level integration and Phase 1A regression boundaries.
// -------------------------------------------------------------------------
var SHOW = extractFunction(INDEX, 'show');
var SHOW_SCREEN = extractFunction(INDEX, 'showScreen');
ok('D1 screen routing remains on the existing History API', INDEX.indexOf('history.pushState') !== -1 && INDEX.indexOf('history.back()') !== -1 && INDEX.indexOf('popstate') !== -1);
ok('D1 no parallel hashchange navigation model was added', INDEX.indexOf('hashchange') === -1);
ok('D1 deferred activity focus runs only after the destination becomes active', hasCode(SHOW_SCREEN, 'toScreen.classList.add("active")') && hasCode(SHOW_SCREEN, 'if(!deferFocus) ppRouteScreenFocus(fromScreen, toScreen)'));
ok('D1 activities with existing stable entry focus defer the shared heading move', hasCode(extractFunction(INDEX, 'startTypeit'), 'show("typeit", true); tRender()') && hasCode(extractFunction(INDEX, 'startListen'), 'show("listen", true); lRender()') && hasCode(extractFunction(INDEX, 'startRound'), 'show("round", true); rRender()'));
ok('D1 same-screen calls remain history-neutral', SHOW.indexOf('classList.contains("active")') < SHOW.indexOf('history.pushState'));
ok('D2 Study installs one named document-level shortcut handler', countOf(INDEX, 'document.addEventListener("keydown", ppStudyShortcutKeydown)') === 1);
// Phase 3B-1A: the maturity gate is a native <dialog>, so Escape (and Android Back)
// arrive as its own cancel event. The old manual keydown Escape/Tab trap is gone.
ok('D2 the maturity Escape key is owned by its overlay, not document',
   INDEX.indexOf('$("matureGate").addEventListener("cancel"') !== -1 &&
   INDEX.indexOf('document.addEventListener("keydown", e=>{ if(e.key === "Escape"') === -1);
eq('D2 no competing manual key handler remains on the maturity gate',
   countOf(INDEX, '$("matureGate").addEventListener("keydown"'), 0);
ok('D2 action cancellation follows a successful shipping action', hasCode(extractFunction(INDEX, 'ppStudyShortcutKeydown'), 'if(!ppHandleStudyShortcut(e)) return false; e.preventDefault();'));
['study','grammar','convo','typeit','listen','round','privacy','about','contact','install'].forEach(function (id) {
  var at = INDEX.indexOf('id="' + id + '"');
  var end = INDEX.indexOf('</section>', at);
  ok('D3 #' + id + ' retains a screen h1', at !== -1 && INDEX.slice(at, end).indexOf('<h1') !== -1);
});
eq('D3 app shell still has one main landmark', countOf(INDEX, '<main '), 1);
['flip','gFlip'].forEach(function (id) {
  var at = INDEX.indexOf('id="' + id + '"');
  var controlId = id === 'flip' ? 'flipControl' : 'gFlipControl';
  var end = INDEX.indexOf('id="' + controlId + '"', at);
  ok('D4 #' + id + ' remains a non-interactive container', INDEX.slice(INDEX.lastIndexOf('<div', at), INDEX.indexOf('>', at) + 1).indexOf('role=') === -1);
  ok('D4 #' + id + ' retains an inert/hidden back face contract', INDEX.slice(at, end).indexOf('aria-hidden="true" inert') !== -1);
});
ok('D4 Phase 1A native flip controls remain sibling buttons', /<button class="flip-control" id="flipControl" type="button"/.test(INDEX) && /<button class="flip-control" id="gFlipControl" type="button"/.test(INDEX));
ok('D4 complete face synchronizer remains shipping code', INDEX.indexOf('function ppSyncFlipFaces') !== -1 && INDEX.indexOf('ppSyncFaceA11y()') !== -1);

console.log('Phase 1B keyboard/focus tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
console.log('  [info] shipping helpers are exercised with a deterministic fake DOM; browser key synthesis, visual focus, accessibility trees and screen readers remain manual');
LOG.forEach(function (line) { console.log('  ' + line); });
if (FAIL > 0) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
