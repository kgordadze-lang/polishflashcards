// Deterministic Phase 2B conversation tests. Shipping functions are extracted from
// index.html and run against the real scenario graph in a browser-like fake DOM.
// Real accessibility trees, VoiceOver, TalkBack and visual focus remain manual.
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
var ROOT = resolveRoot(), INDEX = readFile(ROOT + 'index.html');
var SCENARIO_DATA = readFile(ROOT + 'data-scenarios.js');
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(hay, needle) {
  var count = 0, at = 0;
  while ((at = hay.indexOf(needle, at)) !== -1) { count++; at += needle.length; }
  return count;
}
function extractFunction(src, name) {
  var needle = 'function ' + name + '(', start = src.indexOf(needle);
  if (start === -1 || src.indexOf(needle, start + 1) !== -1) throw new Error('extract: ' + name);
  var open = src.indexOf('{', src.indexOf(')', start)), depth = 0, mode = 'code';
  for (var i = open; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') mode = 'code'; continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      if (c === '\\') { i++; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') ||
          (mode === 'tpl' && c === '`')) mode = 'code';
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
  throw new Error('unbalanced: ' + name);
}
function attrsFrom(source) {
  var attrs = {}, re = /([a-zA-Z_:][\w:.-]*)\s*=\s*"([^"]*)"/g, match;
  while ((match = re.exec(source)) !== null) attrs[match[1]] = match[2];
  return attrs;
}

var win = { PP_LEVELS: [] };
(new Function('window', SCENARIO_DATA))(win);
var scenarioLevel = win.PP_LEVELS[0], topics = scenarioLevel.topics;
ok('A1 real conversation data exposes at least one scenario', topics.length > 0);
ok('A1 every discovered scenario uses the conversation renderer',
   topics.every(function (topic) { return topic.kind === 'convo'; }));

function Classes(names) {
  this.names = {};
  (names || []).forEach(function (name) { this.names[name] = true; }, this);
}
Classes.prototype.contains = function (name) { return !!this.names[name]; };
Classes.prototype.add = function (name) { this.names[name] = true; };
Classes.prototype.remove = function (name) { delete this.names[name]; };
Classes.prototype.toggle = function (name, force) {
  var on = force === undefined ? !this.contains(name) : !!force;
  if (on) this.add(name); else this.remove(name);
  return on;
};

var DOM = {}, ACTIVE = null, BODY = null;
function El(id, tag) {
  this.id = id || ''; this.tagName = (tag || 'div').toUpperCase(); this.attrs = {};
  this.classList = new Classes(); this.listeners = {}; this.connected = true;
  this.hidden = false; this.inert = false; this.style = {}; this.children = [];
  this._html = ''; this._text = ''; this._disabled = false; this.focusCount = 0;
  this._queries = {};
}
El.prototype.setAttribute = function (name, value) { this.attrs[name] = String(value); };
El.prototype.getAttribute = function (name) {
  return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
};
El.prototype.removeAttribute = function (name) { delete this.attrs[name]; };
El.prototype.addEventListener = function (type, fn) {
  (this.listeners[type] = this.listeners[type] || []).push(fn);
};
El.prototype.appendChild = function (child) {
  this.children.push(child); if (child.id) DOM[child.id] = child; return child;
};
El.prototype.click = function () {
  if (this.disabled || !this.connected) return;
  (this.listeners.click || []).slice().forEach(function (fn) { fn({ target: this }); }, this);
};
El.prototype.focus = function () {
  if (!this.connected || this.disabled || this.hidden || this.inert ||
      this.getAttribute('aria-hidden') === 'true') return;
  this.focusCount++; ACTIVE = this;
};
Object.defineProperty(El.prototype, 'disabled', {
  get: function () { return this._disabled; },
  set: function (value) {
    this._disabled = !!value;
    if (this._disabled && ACTIVE === this) ACTIVE = BODY;
  }
});
Object.defineProperty(El.prototype, 'textContent', {
  get: function () { return this._text; },
  set: function (value) { this._text = String(value); }
});
El.prototype._retire = function () {
  Object.keys(this._queries).forEach(function (selector) {
    var values = Array.isArray(this._queries[selector]) ? this._queries[selector] : [this._queries[selector]];
    values.forEach(function (el) { if (el) el.connected = false; });
  }, this);
};
// Phase 3B-2B: the shipping thread renderer now has two paths - a full reset render
// (innerHTML) and an append for ordinary turn advancement (insertAdjacentHTML). The
// fixture models both: a reset retires everything it previously parsed, an append adds
// to what is already there and retires nothing, which is exactly the node-preservation
// property the append path exists for.
El.prototype._parse = function (html) {
  var buttons = [], buttonRe = /<button\b([^>]*)>/g, match;
  while ((match = buttonRe.exec(html)) !== null) {
    var attrs = attrsFrom(match[1]), button = new El(attrs.id || '', 'button');
    Object.keys(attrs).forEach(function (name) { button.setAttribute(name, attrs[name]); });
    (attrs['class'] || '').split(/\s+/).filter(Boolean).forEach(function (name) { button.classList.add(name); });
    if (button.id) DOM[button.id] = button;
    buttons.push(button);
  }
  function collect(selector, list) {
    this._queries[selector] = (this._queries[selector] || []).concat(list);
  }
  collect.call(this, '.reply-opt', buttons.filter(function (b) { return b.classList.contains('reply-opt'); }));
  collect.call(this, '.mini-audio[data-mi]', buttons.filter(function (b) { return b.classList.contains('mini-audio'); }));
  collect.call(this, '.veil-reveal', buttons.filter(function (b) { return b.classList.contains('veil-reveal'); }));
  var ens = [], enRe = /<span\b([^>]*)class="ro-en"([^>]*)>/g;
  while ((match = enRe.exec(html)) !== null) {
    var en = new El('', 'span'), enAttrs = attrsFrom(match[1] + match[2]);
    Object.keys(enAttrs).forEach(function (name) { en.setAttribute(name, enAttrs[name]); });
    ens.push(en);
  }
  collect.call(this, '.ro-en', ens);
  var divRe = /<div\b([^>]*)>/g;
  while ((match = divRe.exec(html)) !== null) {
    var divAttrs = attrsFrom(match[1]);
    if (!divAttrs.id) continue;
    var content = new El(divAttrs.id, 'div');
    Object.keys(divAttrs).forEach(function (name) { content.setAttribute(name, divAttrs[name]); });
    (divAttrs['class'] || '').split(/\s+/).filter(Boolean).forEach(function (name) { content.classList.add(name); });
    DOM[content.id] = content;
  }
  var bolds = [], boldRe = /<b\b([^>]*)>([\s\S]*?)<\/b>/g;
  while ((match = boldRe.exec(html)) !== null) {
    var boldAttrs = attrsFrom(match[1]), bold = new El('', 'b');
    Object.keys(boldAttrs).forEach(function (name) { bold.setAttribute(name, boldAttrs[name]); });
    bold.textContent = match[2].replace(/<[^>]+>/g, '');
    bolds.push(bold);
  }
  collect.call(this, '.cdone-recap li b', bolds);
  var headingRe = /<h2\b([^>]*)>([\s\S]*?)<\/h2>/g;
  while ((match = headingRe.exec(html)) !== null) {
    var headingAttrs = attrsFrom(match[1]), heading = new El(headingAttrs.id || '', 'h2');
    Object.keys(headingAttrs).forEach(function (name) { heading.setAttribute(name, headingAttrs[name]); });
    heading.textContent = match[2].replace(/<[^>]+>/g, ''); if (heading.id) DOM[heading.id] = heading;
  }
};
Object.defineProperty(El.prototype, 'innerHTML', {
  get: function () { return this._html; },
  set: function (value) {
    this._retire(); this._html = String(value); this._queries = {};
    this._parse(this._html);
  }
});
El.prototype.querySelectorAll = function (selector) { return this._queries[selector] || []; };
El.prototype.querySelector = function (selector) {
  if (selector === '.reply-opt') return (this._queries['.reply-opt'] || [])[0] || null;
  var audio = selector.match(/^\.mini-audio\[data-mi="(\d+)"\]$/);
  if (audio) return (this._queries['.mini-audio[data-mi]'] || []).filter(function (button) {
    return button.getAttribute('data-mi') === audio[1];
  })[0] || null;
  var list = this._queries[selector]; return Array.isArray(list) ? list[0] || null : list || null;
};
El.prototype.insertAdjacentHTML = function (position, html) {
  if (position !== 'beforeend') return;
  this._html += String(html); this._parse(String(html));
};

function resetDom() {
  DOM = {}; BODY = new El('BODY', 'body'); ACTIVE = BODY;
  ['cTitle', 'cLevel', 'cThread', 'cReply', 'cFill', 'cCount', 'cStatus', 'cChallenge'].forEach(function (id) {
    DOM[id] = new El(id, id === 'cChallenge' ? 'button' : 'div');
  });
}
function byId(id) { return DOM[id] || null; }
var documentFake = { getElementById: byId, createElement: function (tag) { return new El('', tag); } };
function ppSetActivityStatus(box, parts) {
  var next = (parts || []).map(function (part) { return String(part); }).join('');
  if (box.textContent === next) return false;
  box.textContent = next; return true;
}
function ppFocusActivityTarget(el) {
  if (!el || !el.connected || el.disabled || el.hidden || el.inert ||
      el.getAttribute('aria-hidden') === 'true') return false;
  if (ACTIVE !== el) el.focus();
  return ACTIVE === el;
}
function ppAudioControlName(purpose, phrase) {
  var context = typeof phrase === 'string' ? phrase.replace(/\s+/g, ' ').trim() : '';
  return context ? purpose + ': ' + context : purpose;
}
function ppSetAudioControlName(button, purpose, phrase) {
  if (button) button.setAttribute('aria-label', ppAudioControlName(purpose, phrase));
}

var C = { topic: null, li: 0, tpi: 0, node: null, transcript: [], rendered: 0, dist: {}, maxDist: 1,
          challenge: false, curOptions: null, transitioning: false };
var shown = [];
function show(screen, deferFocus) { shown.push([screen, !!deferFocus]); }
function modeLabel(level) { return level.level === 'Scenarios' ? 'Conversations' : level.level; }
// Phase 3B-2B split the thread renderer into a reset path and an append path, so the
// extracted set grows with the helpers those two paths are built from.
var NAMES = ['cComputeDist', 'convoLen', 'startConvo', 'cSetStatus', 'cBubbleSpeakerId',
  'cBubbleInnerHTML', 'cBubbleHTML', 'cThreadIntroHTML', 'cThreadBubblesHTML',
  'cNameThreadAudio', 'cRenderThread', 'cSettleThreadBubble', 'cAdvanceThread',
  'cRevealBubble', 'cProgress', 'cRenderNode', 'cRenderOptions',
  'cRevealChoiceTranslations', 'cChooseOption', 'cScopeRecapLanguage', 'cShowDone',
  'cSyncChallengeControl'];
var API = (new Function('$', 'document', 'window', 'C', 'C_CHECK', 'G_AUDIO', 'LEVELS',
  'show', 'modeLabel', 'ppSetActivityStatus', 'ppFocusActivityTarget', 'ppSetAudioControlName',
  NAMES.map(function (name) { return extractFunction(INDEX, name); }).join('\n') +
  '\nreturn {' + NAMES.map(function (name) { return name + ':' + name; }).join(',') + '};'))(
    byId, documentFake, {}, C, '<svg></svg>', '<svg data-audio></svg>', [scenarioLevel],
    show, modeLabel, ppSetActivityStatus, ppFocusActivityTarget, ppSetAudioControlName);

// Real graph coverage and termination remain exactly the authored data's.
topics.forEach(function (topic) {
  var dist = API.cComputeDist(topic), sceneIds = Object.keys(topic.scenes);
  ok('B1 ' + topic.id + ' keeps every scene on a terminating path',
     sceneIds.every(function (id) { return dist[id] !== undefined; }));
  ok('B1 ' + topic.id + ' keeps every destination valid', sceneIds.every(function (id) {
    return (topic.scenes[id].options || []).every(function (option) { return !!topic.scenes[option.goto]; });
  }));
  ok('B1 ' + topic.id + ' keeps its start reachable', !!topic.scenes[topic.start]);
  ok('B1 ' + topic.id + ' retains a finite displayed length', API.convoLen(topic) > 0);
});

resetDom(); shown = [];
API.startConvo(0, 0);
eq('C1 launch defers shared screen focus to the scene renderer', shown, [['convo', true]]);
eq('C1 launch focuses the stable scene heading', ACTIVE.id, 'cSceneHeading');
eq('C1 heading is programmatic but absent from normal Tab order', ACTIVE.getAttribute('tabindex'), '-1');
ok('C2 active scene exposes exactly one current heading', countOf(DOM.cThread.innerHTML, 'id="cSceneHeading"') === 1);
ok('C2 active scene exposes the authored speaker', DOM.cThread.innerHTML.indexOf(C.topic.role) !== -1);
ok('C2 Polish and English boundaries are separate',
   DOM.cThread.innerHTML.indexOf('class="b-pl" lang="pl"') !== -1 &&
   DOM.cThread.innerHTML.indexOf('class="b-en"') !== -1);
ok('C2 current audio control has a phrase-specific name',
   DOM.cThread.querySelectorAll('.mini-audio[data-mi]').some(function (button) {
     return button.getAttribute('aria-label') === 'Play Polish phrase: ' + C.transcript[+button.getAttribute('data-mi')].pl;
   }));
var choices = DOM.cReply.querySelectorAll('.reply-opt'), firstChoice = choices[0];
ok('C3 replies are native non-submitting buttons',
   choices.length > 0 && choices.every(function (button) { return button.getAttribute('type') === 'button'; }));
ok('C3 Polish reply text carries its language boundary', DOM.cReply.innerHTML.indexOf('class="ro-pl" lang="pl"') !== -1);
var firstNode = C.node; firstChoice.focus(); firstChoice.click();
ok('C4 one choice advances to its authored destination', C.node !== firstNode);
eq('C4 removed choice cannot retain focus', [firstChoice.connected, ACTIVE.id], [false, 'cSceneHeading']);
var afterOneChoice = C.node; firstChoice.click();
eq('C4 a stale removed choice cannot activate a second transition', C.node, afterOneChoice);
eq('C4 the transition produces one learner transcript entry',
   C.transcript.filter(function (message) { return message.who === 'you'; }).length, 1);

// Follow the first authored option until the real graph terminates.
var guard = 100;
while (C.curOptions && guard-- > 0) DOM.cReply.querySelectorAll('.reply-opt')[0].click();
ok('C5 a terminal scene is reached without changing routing', guard > 0 && C.curOptions === null);
eq('C5 terminal focus lands on the completion heading', ACTIVE.id, 'cDoneTitle');
eq('C5 terminal heading is Polish and script-focusable',
   [ACTIVE.getAttribute('lang'), ACTIVE.getAttribute('tabindex')], ['pl', '-1']);
var again = DOM.cAgain; again.click();
eq('C6 restart resets to the authored start', C.node, C.topic.start);
eq('C6 restart clears terminal history and focuses the first scene',
   [C.transcript.length, DOM.cStatus.textContent, ACTIVE.id], [1, '', 'cSceneHeading']);

// Challenge content is fully hidden until the native disclosure is activated.
C.challenge = true; C.transcript[0].revealed = false; API.cRenderThread(); API.cRenderOptions(C.curOptions);
var reveal = DOM.cThread.querySelectorAll('.veil-reveal')[0];
var controlled = DOM[reveal.getAttribute('aria-controls')];
eq('D1 hidden challenge content is removed from the accessibility tree', controlled.getAttribute('aria-hidden'), 'true');
eq('D1 reveal is a native button with a disclosure relationship',
   [reveal.tagName, reveal.getAttribute('type'), reveal.getAttribute('aria-expanded')],
   ['BUTTON', 'button', 'false']);
var hiddenMessage = C.transcript[+reveal.getAttribute('data-mi')];
var hiddenAudio = DOM.cThread.querySelector('.mini-audio[data-mi="' + reveal.getAttribute('data-mi') + '"]');
ok('D1 hidden audio name gives context without exposing the phrase',
   hiddenAudio.getAttribute('aria-label').indexOf(C.topic.role) !== -1 &&
   hiddenAudio.getAttribute('aria-label').indexOf(hiddenMessage.pl) === -1);
var nodeBeforeReveal = C.node, transcriptBeforeReveal = C.transcript.length;
ok('D2 Enter activation reveals exactly once', API.cRevealBubble(reveal));
eq('D2 expanded and revealed state is exposed',
   [reveal.getAttribute('aria-expanded'), controlled.getAttribute('aria-hidden'), hiddenMessage.revealed],
   ['true', null, true]);
eq('D2 reveal preserves conversation state', [C.node, C.transcript.length], [nodeBeforeReveal, transcriptBeforeReveal]);
eq('D2 reveal announces once and moves to a valid audio control',
   [DOM.cStatus.textContent, ACTIVE], ['Phrase and translation revealed.', hiddenAudio]);
eq('D2 repeated activation cannot reveal twice', API.cRevealBubble(reveal), false);

// Recreate a closed disclosure and exercise the same native click path used by Space.
hiddenMessage.revealed = false; API.cRenderThread();
reveal = DOM.cThread.querySelectorAll('.veil-reveal')[0];
ok('D3 Space activation reaches the same single shipping action', API.cRevealBubble(reveal));
eq('D3 a second Space activation is ignored', API.cRevealBubble(reveal), false);

// Choice translations have their own associated disclosure and restore language
// content without changing the current node/options.
API.cRenderOptions(C.curOptions);
var peek = DOM.cPeek, choiceNode = C.node, choiceOptions = C.curOptions;
ok('D4 challenge choice translations start hidden',
   DOM.cReply.querySelectorAll('.ro-en').every(function (span) { return span.getAttribute('aria-hidden') === 'true'; }));
peek.click();
eq('D4 translation disclosure exposes expanded state', peek.getAttribute('aria-expanded'), 'true');
ok('D4 translations become available afterward',
   DOM.cReply.querySelectorAll('.ro-en').every(function (span) { return span.getAttribute('aria-hidden') === null; }));
eq('D4 choice reveal preserves route and option records', [C.node, C.curOptions], [choiceNode, choiceOptions]);
ok('D4 focus moves to a valid learner choice', DOM.cReply.querySelectorAll('.reply-opt').indexOf(ACTIVE) !== -1);

C.challenge = false; API.cSyncChallengeControl();
eq('D5 Challenge off exposes pressed state and action name',
   [DOM.cChallenge.getAttribute('aria-pressed'), DOM.cChallenge.getAttribute('aria-label')],
   ['false', 'Turn Challenge mode on: hide translations and listen before revealing']);
C.challenge = true; API.cSyncChallengeControl();
eq('D5 Challenge on exposes pressed state and reverse action',
   [DOM.cChallenge.getAttribute('aria-pressed'), DOM.cChallenge.getAttribute('aria-label')],
   ['true', 'Turn Challenge mode off and show translations']);

// The real event wiring delegates only to the native reveal button; there is no
// keydown clone that could double-fire Enter or Space.
ok('E1 reveal wiring targets the native button',
   INDEX.indexOf('e.target.closest(".veil-reveal")') !== -1);
eq('E1 conversation code introduces no keydown reveal handler',
   (INDEX.slice(INDEX.indexOf('/* ---------------- conversation'),
                INDEX.indexOf('/* ---------------- Type it')).match(/addEventListener\("keydown"/g) || []).length, 0);
ok('E2 all covered focus moves use the guarded adapter',
   ['cRenderNode', 'cRevealBubble', 'cRevealChoiceTranslations', 'cShowDone'].every(function (name) {
     return extractFunction(INDEX, name).indexOf('ppFocusActivityTarget') !== -1;
   }));

// Completion text is constructed as text nodes so a Polish topic name cannot
// become markup inside the surrounding English sentence.
var hostileName = 'Rozmowa “<img src=x onerror="boom">” & quoted';
C.topic = { name: hostileName, recap: ['<b>boli mnie</b> + body part - boli mnie głowa'] };
API.cShowDone(false);
var summary = DOM.cDoneSummary, topicName = DOM.cDoneTopic;
eq('F1 completion topic name is rendered literally', topicName.textContent, hostileName);
eq('F1 completion topic name has a dedicated Polish boundary', topicName.getAttribute('lang'), 'pl');
ok('F1 topic markup-like text is absent from the terminal HTML parser input',
   DOM.cReply.innerHTML.indexOf(hostileName) === -1 && topicName.children.length === 0);
eq('F1 surrounding completion sentence stays under English document language',
   [summary.children[0].getAttribute('lang'), summary.children[2].getAttribute('lang')],
   [null, null]);
eq('F1 visible completion wording is preserved',
   summary.children.map(function (child) { return child.textContent; }).join(''),
   'You made it through “' + hostileName + '” in Polish. Replay it to lock the phrases in, or head back for another.');

// Every shipping recap uses authored <b> only for a reliable Polish phrase.
// Mixed unbolded prose remains English by inheritance rather than receiving a
// speculative whole-item language assignment.
topics.forEach(function (topic) {
  C.topic = topic; API.cShowDone(false);
  var authored = (topic.recap || []).join(''), expected = (authored.match(/<b>/g) || []).length;
  var scoped = DOM.cReply.querySelectorAll('.cdone-recap li b');
  eq('F2 ' + topic.id + ' scopes every authored recap phrase', scoped.length, expected);
  ok('F2 ' + topic.id + ' marks reliable recap phrases Polish',
     scoped.every(function (phrase) { return phrase.getAttribute('lang') === 'pl'; }));
  ok('F2 ' + topic.id + ' does not mark a mixed recap item Polish',
     DOM.cReply.innerHTML.indexOf('<li lang="pl">') === -1);
});

console.log('Conversation accessibility tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log(line); });
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
