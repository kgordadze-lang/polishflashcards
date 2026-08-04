// Deterministic Phase 4B-1 tests for the shipping service worker.
//
// These run the REAL sw.js. The file is evaluated inside a fake worker global
// (self, caches, fetch, Promise, URL, console) and then driven with fake install,
// activate and fetch events, so install failure, activation cleanup, request
// classification, canonical cache keys and cache-write lifetime are executed, not
// pattern-matched. Source-level assertions are used only for boundaries a runtime
// test cannot prove absent (no automatic skipWaiting, no clients.claim, no
// catch-all cache write) and for protected release identifiers.
//
// Promises are a local A+ implementation with a manually drained microtask queue:
// JavaScriptCore under osascript only drains native microtasks after the whole
// script has finished, which would make every asynchronous assertion untestable.
// Draining by hand also makes "delayed cache.put" and "quota rejection" exact
// rather than timing-dependent.
//
// Real browsers, real Cache Storage, real quota pressure, real worker termination,
// installed PWAs and physical devices remain manual verification.
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
var SW_SRC = readFile(ROOT + 'sw.js');
var INDEX = readFile(ROOT + 'index.html');
var MANIFEST = readFile(ROOT + 'manifest.json');
var MIGRATE = readFile(ROOT + 'pp-migrate.js');
var BUILD = readFile(ROOT + 'build_pages.py');
var GEN_PAGE = readFile(ROOT + 'grammar/biernik-accusative/index.html');

var PASS = 0, FAIL = 0, LOG = [];
function ok(name, cond) { if (cond) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(src, needle) {
  var n = 0, at = src.indexOf(needle);
  while (at !== -1) { n++; at = src.indexOf(needle, at + needle.length); }
  return n;
}
// Comment-stripped source, so a boundary assertion cannot be satisfied or broken
// by prose. Handles line comments, block comments and the three string forms.
function codeOnly(src) {
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
    if (c === "'") mode = 'sq';
    else if (c === '"') mode = 'dq';
    else if (c === '`') mode = 'tpl';
    out += c;
  }
  return out;
}
var SW_CODE = codeOnly(SW_SRC);

// =========================================================================
// Deterministic promises: an A+ core over a queue this suite drains by hand.
// =========================================================================
var QUEUE = [];
function schedule(job) { QUEUE.push(job); }
function drain() {
  var guard = 0;
  while (QUEUE.length) {
    if (++guard > 200000) throw new Error('drain: runaway microtask queue');
    QUEUE.shift()();
  }
}
function P(executor) {
  this.state = 'pending'; this.value = undefined; this.handlers = [];
  var self_ = this;
  if (executor) {
    try { executor(function (v) { settleP(self_, v); }, function (e) { rejectP(self_, e); }); }
    catch (err) { rejectP(self_, err); }
  }
}
function settleP(p, v) {
  if (p.state !== 'pending') return;
  if (v && (typeof v === 'object' || typeof v === 'function') && typeof v.then === 'function') {
    var called = false;
    try {
      v.then(function (val) { if (!called) { called = true; settleP(p, val); } },
             function (err) { if (!called) { called = true; rejectP(p, err); } });
    } catch (err) { if (!called) { called = true; rejectP(p, err); } }
    return;
  }
  p.state = 'fulfilled'; p.value = v; flushP(p);
}
function rejectP(p, e) {
  if (p.state !== 'pending') return;
  p.state = 'rejected'; p.value = e; flushP(p);
}
function flushP(p) {
  var hs = p.handlers; p.handlers = [];
  hs.forEach(function (h) { schedule(function () { runHandler(p, h); }); });
}
function runHandler(p, h) {
  var fn = p.state === 'fulfilled' ? h.onOk : h.onErr;
  if (typeof fn !== 'function') {
    if (p.state === 'fulfilled') settleP(h.next, p.value); else rejectP(h.next, p.value);
    return;
  }
  try { settleP(h.next, fn(p.value)); } catch (err) { rejectP(h.next, err); }
}
P.prototype.then = function (onOk, onErr) {
  var next = new P(), h = { onOk: onOk, onErr: onErr, next: next }, self_ = this;
  if (this.state === 'pending') this.handlers.push(h);
  else schedule(function () { runHandler(self_, h); });
  return next;
};
P.prototype['catch'] = function (onErr) { return this.then(undefined, onErr); };
P.resolve = function (v) { if (v instanceof P) return v; var p = new P(); settleP(p, v); return p; };
P.reject = function (e) { var p = new P(); rejectP(p, e); return p; };
P.all = function (list) {
  return new P(function (res, rej) {
    var items = Array.prototype.slice.call(list), left = items.length, out = new Array(items.length);
    if (!left) { res(out); return; }
    items.forEach(function (item, i) {
      P.resolve(item).then(function (v) { out[i] = v; if (--left === 0) res(out); }, rej);
    });
  });
};
function deferred() {
  var d = {};
  d.promise = new P(function (res, rej) { d.resolve = res; d.reject = rej; });
  return d;
}
// Records how a promise settled without changing what the code under test sees.
function watch(promise) {
  var rec = { state: 'pending', value: undefined };
  P.resolve(promise).then(function (v) { rec.state = 'fulfilled'; rec.value = v; },
                          function (e) { rec.state = 'rejected'; rec.value = e; });
  return rec;
}

// Harness self-check: the fake promise must behave, or nothing below means anything.
(function () {
  var order = [], d = deferred();
  P.resolve('a').then(function (v) { order.push(v); });
  d.promise.then(function (v) { order.push(v); });
  eq('H1 nothing runs before the queue is drained', order, []);
  drain();
  eq('H1 resolved work runs on drain', order, ['a']);
  d.resolve('b'); drain();
  eq('H1 deferred work runs when it is resolved', order, ['a', 'b']);
  var chained = watch(P.resolve(1).then(function (v) { return P.resolve(v + 1); }));
  drain();
  eq('H2 a promise returned from then is adopted', [chained.state, chained.value], ['fulfilled', 2]);
  var failed = watch(P.reject(new Error('x')).then(function () { return 'unused'; }));
  drain();
  eq('H2 rejection skips the fulfil handler', failed.state, 'rejected');
  var recovered = watch(P.reject(new Error('x'))['catch'](function () { return 'ok'; }));
  drain();
  eq('H2 catch recovers', [recovered.state, recovered.value], ['fulfilled', 'ok']);
  var all = watch(P.all([P.resolve(1), P.resolve(2)]));
  drain();
  eq('H3 all collects in order', [all.state, all.value], ['fulfilled', [1, 2]]);
  var allFail = watch(P.all([P.resolve(1), P.reject(new Error('no'))]));
  drain();
  eq('H3 all rejects on first failure', allFail.state, 'rejected');
})();

// =========================================================================
// Fake URL. JavaScriptCore has no URL, and the worker parses every request.
// =========================================================================
function parseAbsolute(input) {
  var m = /^([a-zA-Z][a-zA-Z0-9+.\-]*):([\s\S]*)$/.exec(input);
  if (!m) return null;
  var protocol = m[1].toLowerCase() + ':', rest = m[2], host = '', path = rest;
  if (rest.slice(0, 2) === '//') {
    var after = rest.slice(2), cut = after.length;
    ['/', '?', '#'].forEach(function (ch) {
      var at = after.indexOf(ch);
      if (at !== -1 && at < cut) cut = at;
    });
    host = after.slice(0, cut);
    path = after.slice(cut);
    if (path === '' || path[0] !== '/') path = '/' + path;
  }
  var hash = '', search = '', at = path.indexOf('#');
  if (at !== -1) { hash = path.slice(at); path = path.slice(0, at); }
  at = path.indexOf('?');
  if (at !== -1) { search = path.slice(at); path = path.slice(0, at); }
  return { protocol: protocol, host: host, pathname: path, search: search, hash: hash };
}
function normalizePath(path) {
  var parts = path.split('/'), out = [];
  for (var i = 0; i < parts.length; i++) {
    var seg = parts[i];
    if (seg === '.') { if (i === parts.length - 1) out.push(''); continue; }
    if (seg === '..') { if (out.length > 1) out.pop(); if (i === parts.length - 1) out.push(''); continue; }
    out.push(seg);
  }
  return out.join('/') || '/';
}
function FakeURL(input, base) {
  var parsed = parseAbsolute(String(input));
  if (!parsed) {
    if (base === undefined || base === null) throw new TypeError('Invalid URL: ' + input);
    var b = parseAbsolute(String(base));
    if (!b) throw new TypeError('Invalid base URL: ' + base);
    var ref = String(input), path, search = '', hash = '';
    var at = ref.indexOf('#');
    if (at !== -1) { hash = ref.slice(at); ref = ref.slice(0, at); }
    at = ref.indexOf('?');
    if (at !== -1) { search = ref.slice(at); ref = ref.slice(0, at); }
    if (ref === '') { path = b.pathname; if (search === '') search = b.search; }
    else if (ref[0] === '/') path = ref;
    else path = normalizePath(b.pathname.replace(/[^/]*$/, '') + ref);
    parsed = { protocol: b.protocol, host: b.host, pathname: path, search: search, hash: hash };
  }
  this.protocol = parsed.protocol;
  this.host = parsed.host;
  this.pathname = parsed.pathname;
  this.search = parsed.search;
  this.hash = parsed.hash;
  var opaque = (this.protocol !== 'http:' && this.protocol !== 'https:') || this.host === '';
  this.origin = opaque ? 'null' : this.protocol + '//' + this.host;
  this.href = (this.host === '' ? this.protocol : this.protocol + '//' + this.host) +
              this.pathname + this.search + this.hash;
}

(function () {
  var u = new FakeURL('https://popolsku.app/guide/index.html?a=1#top');
  eq('H4 absolute URL parses', [u.origin, u.pathname, u.search, u.hash],
     ['https://popolsku.app', '/guide/index.html', '?a=1', '#top']);
  eq('H4 relative asset resolves against the worker',
     new FakeURL('./fonts/x.woff2', 'https://popolsku.app/sw.js').href,
     'https://popolsku.app/fonts/x.woff2');
  eq('H4 directory-relative root resolves', new FakeURL('./', 'https://popolsku.app/sw.js').href,
     'https://popolsku.app/');
  eq('H4 root-absolute reference resolves',
     new FakeURL('/audio/ab12.mp3', 'https://popolsku.app/grammar/x/').href,
     'https://popolsku.app/audio/ab12.mp3');
  eq('H4 an extension scheme keeps its protocol and has no web origin',
     [new FakeURL('chrome-extension://abc/injected.js').protocol,
      new FakeURL('chrome-extension://abc/injected.js').origin], ['chrome-extension:', 'null']);
  eq('H4 a data URL keeps its protocol', new FakeURL('data:text/plain,hi').protocol, 'data:');
  var threw = false;
  try { new FakeURL('not a url'); } catch (e) { threw = true; }
  ok('H4 an unparseable URL throws, so the worker can catch it', threw);
})();

// =========================================================================
// Fake Request / Response / Headers
// =========================================================================
function FakeHeaders(map) {
  this.map = {};
  var self_ = this;
  Object.keys(map || {}).forEach(function (k) { self_.map[k.toLowerCase()] = map[k]; });
}
FakeHeaders.prototype.get = function (name) {
  var v = this.map[String(name).toLowerCase()];
  return v === undefined ? null : v;
};
function FakeRequest(url, opts) {
  opts = opts || {};
  this.url = url;
  this.method = opts.method || 'GET';
  this.mode = opts.mode || 'no-cors';
  this.headers = new FakeHeaders(opts.headers);
  this.tag = opts.tag || null;
}
// Content-Type values measured against the running deployment (python3 -m
// http.server over this working tree): see the manual-checks report.
function mimeFor(url) {
  var path = String(url).split('?')[0];
  if (path.slice(-1) === '/') return 'text/html';
  if (/\.js$/.test(path)) return 'text/javascript';
  if (/\.json$/.test(path)) return 'application/json';
  if (/\.mp3$/.test(path)) return 'audio/mpeg';
  if (/\.svg$/.test(path)) return 'image/svg+xml';
  if (/\.png$/.test(path)) return 'image/png';
  if (/\.woff2$/.test(path)) return 'font/woff2';
  if (/\.xml$/.test(path)) return 'application/xml';
  return 'text/plain';
}
// A cache entry as a real worker would have left it: typed for its own key.
// Anything seeded WITHOUT this helper is a deliberately invalid inherited entry.
function seeded(key, label, extra) {
  var opts = { url: key, label: label, headers: { 'Content-Type': mimeFor(key) } };
  Object.keys(extra || {}).forEach(function (k) { opts[k] = extra[k]; });
  return new FakeResponse(opts);
}
function typed(url, extra) {
  var opts = { url: url, headers: { 'Content-Type': mimeFor(url) } };
  Object.keys(extra || {}).forEach(function (k) { opts[k] = extra[k]; });
  return new FakeResponse(opts);
}

var RESPONSE_SEQ = 0;
// Phase 4B-3's Range branch builds real responses the web way -
// new Response(body, init) - so the fake accepts that form as well as the
// harness's own option bag. A first argument that is not a plain option bag,
// or any call with a second argument, is the web form.
function FakeResponse(opts, init) {
  if (init !== undefined || opts === null ||
      (opts && typeof ArrayBuffer !== 'undefined' && opts instanceof ArrayBuffer)) {
    var body = opts, cfg = init || {};
    opts = {
      status: cfg.status, type: 'basic', headers: cfg.headers,
      label: 'synthetic-' + (cfg.status === undefined ? 200 : cfg.status), body: body
    };
  }
  opts = opts || {};
  this.id = ++RESPONSE_SEQ;
  this.status = opts.status === undefined ? 200 : opts.status;
  this.ok = opts.ok === undefined ? (this.status >= 200 && this.status < 300) : opts.ok;
  this.type = opts.type === undefined ? 'basic' : opts.type;
  this.redirected = opts.redirected === true;
  this.url = opts.url === undefined ? '' : opts.url;
  this.label = opts.label === undefined ? ('body#' + this.id) : opts.label;
  this.headers = new FakeHeaders(opts.headers);
  this.bodyUsed = false;
  this.cloneCount = 0;
  this.source = this;
  /* Bytes, so a cached clip can really be sliced. Derived from the label when
     the harness did not supply a body, which keeps every seeded entry readable
     and deterministic. */
  this.body = opts.body === undefined ? null : opts.body;
}
function bytesOf(text) {
  var out = new Uint8Array(text.length);
  for (var i = 0; i < text.length; i++) out[i] = text.charCodeAt(i) & 255;
  return out.buffer;
}
FakeResponse.prototype.clone = function () {
  if (this.bodyUsed) throw new TypeError('Response body is already used');
  this.cloneCount++;
  var copy = new FakeResponse({
    status: this.status, ok: this.ok, type: this.type, redirected: this.redirected,
    url: this.url, label: this.label, headers: this.headers.map, body: this.body
  });
  copy.source = this.source;
  return copy;
};
FakeResponse.prototype.text = function () { this.bodyUsed = true; return P.resolve(this.label); };
FakeResponse.prototype.arrayBuffer = function () {
  this.bodyUsed = true;
  return P.resolve(this.body === null ? bytesOf(this.label) : this.body);
};
FakeResponse.redirect = function (url, status) {
  return new FakeResponse({
    status: status || 302, ok: false, type: 'default', url: url, label: 'redirect-to-root',
    headers: { Location: url }
  });
};

// =========================================================================
// Fake Cache Storage. Failure injection is explicit so every branch of the
// write contract can be exercised without timing games.
// =========================================================================
function keyOf(request) { return typeof request === 'string' ? request : request.url; }
function FakeCache(name, storage) {
  this.name = name; this.storage = storage; this.entries = {}; this.order = [];
  this.puts = []; this.deletes = [];
}
FakeCache.prototype['delete'] = function (request) {
  var key = keyOf(request);
  this.deletes.push(key);
  var behavior = this.storage.entryDeleteBehavior
    ? this.storage.entryDeleteBehavior(this.name, key) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (behavior && behavior.miss) return P.resolve(false);
  if (this.entries[key] === undefined) return P.resolve(false);
  delete this.entries[key];
  var self_ = this;
  this.order = this.order.filter(function (k) { return k !== key; });
  return P.resolve(true);
};
FakeCache.prototype.put = function (request, response) {
  var self_ = this, key = keyOf(request);
  this.puts.push(key);
  var behavior = this.storage.putBehavior ? this.storage.putBehavior(this.name, key, response) : null;
  var store = function () {
    if (self_.order.indexOf(key) === -1) self_.order.push(key);
    self_.entries[key] = response;
  };
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (behavior && behavior.defer) {
    var d = deferred();
    this.storage.pendingPuts.push({
      cache: this.name, key: key,
      settle: function () { store(); d.resolve(undefined); },
      fail: function (err) { d.reject(err); }
    });
    return d.promise;
  }
  store();
  return P.resolve(undefined);
};
FakeCache.prototype.match = function (request) {
  var key = keyOf(request);
  var behavior = this.storage.matchBehavior ? this.storage.matchBehavior(this.name, key) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  var hit = this.entries[key];
  return P.resolve(hit === undefined ? undefined : hit);
};
FakeCache.prototype.keys = function () {
  var self_ = this;
  return P.resolve(this.order.map(function (k) { return new FakeRequest(k); }));
};
function FakeCacheStorage(seed) {
  this.caches = {}; this.names = []; this.pendingPuts = [];
  this.openBehavior = null; this.putBehavior = null; this.deleteBehavior = null;
  this.matchBehavior = null; this.entryDeleteBehavior = null;
  this.deleted = []; this.opened = []; this.globalMatches = 0;
  var self_ = this;
  Object.keys(seed || {}).forEach(function (name) {
    var cache = self_.rawOpen(name);
    Object.keys(seed[name]).forEach(function (key) {
      cache.order.push(key);
      cache.entries[key] = seed[name][key];
    });
  });
}
FakeCacheStorage.prototype.rawOpen = function (name) {
  if (!this.caches[name]) { this.caches[name] = new FakeCache(name, this); this.names.push(name); }
  return this.caches[name];
};
FakeCacheStorage.prototype.open = function (name) {
  this.opened.push(name);
  var behavior = this.openBehavior ? this.openBehavior(name) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  return P.resolve(this.rawOpen(name));
};
FakeCacheStorage.prototype.keys = function () { return P.resolve(this.names.slice()); };
FakeCacheStorage.prototype['delete'] = function (name) {
  this.deleted.push(name);
  var behavior = this.deleteBehavior ? this.deleteBehavior(name) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (!this.caches[name]) return P.resolve(false);
  delete this.caches[name];
  this.names = this.names.filter(function (n) { return n !== name; });
  return P.resolve(true);
};
// Unnamed CacheStorage.match: searches every cache in creation order, exactly
// like the real one. The worker must never reach this.
FakeCacheStorage.prototype.match = function (request) {
  this.globalMatches++;
  var key = keyOf(request);
  for (var i = 0; i < this.names.length; i++) {
    var hit = this.caches[this.names[i]].entries[key];
    if (hit !== undefined) return P.resolve(hit);
  }
  return P.resolve(undefined);
};
FakeCacheStorage.prototype.inventory = function (name) {
  var cache = this.caches[name];
  return cache ? cache.order.slice().sort() : null;
};

// =========================================================================
// Fake worker global + evaluation of the shipping sw.js
// =========================================================================
var ORIGIN = 'https://popolsku.app';
// Appended to the shipping source so the suite can call the worker's own helpers
// instead of reimplementing them. Everything named here is declared by sw.js.
var EPILOGUE = '\nreturn {' +
  ' CACHE: CACHE, AUDIO_CACHE: AUDIO_CACHE, SHELL_CACHE_PATTERN: SHELL_CACHE_PATTERN,' +
  ' REQUIRED_ASSETS: REQUIRED_ASSETS, OPTIONAL_ASSETS: OPTIONAL_ASSETS,' +
  ' STATIC_ASSET_PATHS: STATIC_ASSET_PATHS, ROOT_KEY: ROOT_KEY, SCOPE_PATH: SCOPE_PATH,' +
  ' canonicalKeyFor: canonicalKeyFor, canonicalPath: canonicalPath, parseUrl: parseUrl,' +
  ' classifyRequest: classifyRequest, isCacheableResponse: isCacheableResponse,' +
  ' isRangeRequest: isRangeRequest, isObsoleteShellCache: isObsoleteShellCache,' +
  ' cacheWrite: cacheWrite, cacheMatch: cacheMatch, mediaGroupForPath: mediaGroupForPath,' +
  ' mediaTypeOf: mediaTypeOf, hasExpectedMediaType: hasExpectedMediaType,' +
  ' MEDIA_GROUPS: MEDIA_GROUPS, state: SW_STATE };\n';

function defaultRoute(url) { return { response: typed(url) }; }

function makeWorker(options) {
  options = options || {};
  var storage = new FakeCacheStorage(options.seed || {});
  var route = options.route || defaultRoute;
  var fetchCalls = [];
  var warnings = [];
  function fetchFn(input, init) {
    var url = keyOf(input);
    fetchCalls.push({ url: url, init: init || null, request: typeof input === 'string' ? null : input });
    var outcome = route(url, init, input);
    if (!outcome) return P.reject(new TypeError('Failed to fetch ' + url));
    if (outcome.reject) return P.reject(outcome.reject);
    if (outcome.defer) {
      var d = deferred();
      fetchFn.pending.push({ url: url, resolve: d.resolve, reject: d.reject });
      return d.promise;
    }
    return P.resolve(outcome.response || typed(url));
  }
  fetchFn.calls = fetchCalls;
  fetchFn.pending = [];
  var listeners = {};
  var swSelf = {
    location: { origin: ORIGIN, href: ORIGIN + '/sw.js', pathname: '/sw.js' },
    skipWaitingCalls: 0,
    claimCalls: 0,
    addEventListener: function (type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    skipWaiting: function () { swSelf.skipWaitingCalls++; return P.resolve(); },
    clients: { claim: function () { swSelf.claimCalls++; return P.resolve(); } },
    registration: { scope: ORIGIN + '/' }
  };
  var consoleFake = {
    warn: function (m) { warnings.push(String(m)); },
    error: function (m) { warnings.push('error: ' + String(m)); },
    log: function () {}
  };
  var api = (new Function('self', 'caches', 'fetch', 'Promise', 'URL', 'Response', 'console',
    SW_SRC + EPILOGUE))(swSelf, storage, fetchFn, P, FakeURL, FakeResponse, consoleFake);
  return {
    self: swSelf, caches: storage, fetch: fetchFn, api: api,
    listeners: listeners, warnings: warnings,
    fire: function (type, event) {
      (listeners[type] || []).forEach(function (fn) { fn(event); });
      return event;
    }
  };
}

function InstallEvent() { this.waits = []; }
InstallEvent.prototype.waitUntil = function (p) { this.waits.push(p); return undefined; };
function ActivateEvent() { this.waits = []; }
ActivateEvent.prototype.waitUntil = function (p) { this.waits.push(p); return undefined; };
function FetchEvent(request) { this.request = request; this.waits = []; this.responses = []; }
FetchEvent.prototype.waitUntil = function (p) { this.waits.push(p); return undefined; };
FetchEvent.prototype.respondWith = function (p) { this.responses.push(p); return undefined; };

function runInstall(worker) {
  var e = new InstallEvent();
  worker.fire('install', e);
  var recs = e.waits.map(watch);
  drain();
  return { event: e, results: recs };
}
function runActivate(worker) {
  var e = new ActivateEvent();
  worker.fire('activate', e);
  var recs = e.waits.map(watch);
  drain();
  return { event: e, results: recs };
}
// respondWith is called synchronously, but a runtime write is only scheduled
// once the network promise settles - so the queue is drained before the event's
// extend-lifetime promises are observed, and again afterwards.
function runFetch(worker, request) {
  var e = new FetchEvent(request);
  worker.fire('fetch', e);
  drain();
  var responses = e.responses.map(watch);
  var writes = e.waits.map(watch);
  drain();
  return { event: e, responses: responses, writes: writes, intercepted: e.responses.length > 0 };
}
// Safe readers. A regression should surface as a named failed assertion, never
// as a crash that hides every assertion after it.
function respState(run, i) { var r = run.responses[i || 0]; return r ? r.state : 'no-response'; }
function respValue(run, i) { var r = run.responses[i || 0]; return r ? r.value : undefined; }
function respLabel(run, i) { var v = respValue(run, i); return v && v.label !== undefined ? v.label : null; }
function writeState(run, i) { var w = run.writes[i || 0]; return w ? w.state : 'no-write'; }
function inv(worker, name) { var i = worker.caches.inventory(name); return i === null ? 'no-cache' : i; }
function invList(worker, name) { var i = worker.caches.inventory(name); return i === null ? [] : i; }
function invLen(worker, name) { var i = worker.caches.inventory(name); return i === null ? -1 : i.length; }
function entry(worker, name, key) {
  var c = worker.caches.caches[name];
  return c ? c.entries[key] : undefined;
}
function entryLabel(worker, name, key) {
  var e = entry(worker, name, key);
  return e && e.label !== undefined ? e.label : null;
}
function storedKeys(worker) {
  var out = [];
  worker.caches.names.forEach(function (n) {
    worker.caches.caches[n].order.forEach(function (k) { out.push(n + ' :: ' + k); });
  });
  return out.sort();
}
function pending(worker, i) {
  return worker.caches.pendingPuts[i || 0] || { settle: function () {}, fail: function () {} };
}

function nav(url) { return new FakeRequest(url, { mode: 'navigate' }); }
function get(url, opts) { return new FakeRequest(url, opts); }

var W0 = makeWorker();
var API = W0.api;
var SHELL = API.CACHE, AUDIO = API.AUDIO_CACHE;

// =========================================================================
// A. Cache names and cleanup
// =========================================================================
eq('A1 the app-shell cache is popolsku-v59', API.CACHE, 'popolsku-v59');
eq('A1 the audio cache is unchanged', API.AUDIO_CACHE, 'popolsku-audio');
eq('A1 the shell cleanup matcher is numeric-only', String(API.SHELL_CACHE_PATTERN), '/^popolsku-v[0-9]+$/');
ok('A1 the source declares the shell cache exactly once',
   countOf(SW_CODE, 'const CACHE = "popolsku-v59"') === 1 &&
   countOf(SW_CODE, 'popolsku-v55') === 0 && countOf(SW_CODE, '"popolsku-v57"') === 0 &&
   countOf(SW_CODE, '"popolsku-v58"') === 0);
ok('A1 the source declares the audio cache exactly once',
   countOf(SW_CODE, 'const AUDIO_CACHE = "popolsku-audio"') === 1);
eq('A1 the canonical root key is the deployed root', API.ROOT_KEY, ORIGIN + '/');

// v55 must not be touched while v56 installs.
(function () {
  var v55Shell = seeded(ORIGIN + '/', 'v55-shell');
  var worker = makeWorker({ seed: {
    'popolsku-v55': { 'https://popolsku.app/': v55Shell, 'https://popolsku.app/pp-answer.js': seeded('https://popolsku.app/pp-answer.js', 'v55-answer') },
    'popolsku-audio': { 'https://popolsku.app/audio/ab12ef34.mp3': seeded('https://popolsku.app/audio/ab12ef34.mp3', 'clip') },
    'unrelated-tool-cache': { 'https://popolsku.app/other/thing.txt': seeded('https://popolsku.app/other/thing.txt', 'other') }
  } });
  var before = inv(worker, 'popolsku-v55');
  var run = runInstall(worker);
  eq('A2 install resolves with every required and optional asset available', run.results[0].state, 'fulfilled');
  eq('A2 the previous shell cache is untouched by the new install',
     inv(worker, 'popolsku-v55'), before);
  eq('A2 the previous shell response object is still the one stored',
     entryLabel(worker, 'popolsku-v55', 'https://popolsku.app/'), 'v55-shell');
  eq('A2 no cache was deleted during installation', worker.caches.deleted, []);
  ok('A2 the new shell cache was opened and populated',
     invLen(worker, SHELL) === API.REQUIRED_ASSETS.length + API.OPTIONAL_ASSETS.length);
  eq('A2 the audio cache was never opened during install',
     worker.caches.opened.filter(function (n) { return n === AUDIO; }), []);

  // Activation is what cleans up, and only shell caches.
  runActivate(worker);
  eq('A3 activation deletes the obsolete shell cache', worker.caches.deleted, ['popolsku-v55']);
  ok('A3 the new shell cache survives activation', !!worker.caches.caches[SHELL]);
  ok('A3 the audio cache survives activation', !!worker.caches.caches[AUDIO]);
  eq('A3 the audio cache still holds its clip',
     entryLabel(worker, AUDIO, 'https://popolsku.app/audio/ab12ef34.mp3'), 'clip');
  ok('A3 an unrelated same-origin cache survives activation', !!worker.caches.caches['unrelated-tool-cache']);
})();

// Cleanup predicate, exhaustively.
[
  // deleted: a real numbered shell cache that is not the current one - including
  // popolsku-v58, the shell this release supersedes, and popolsku-v590, which merely
  // starts with the current name and must not survive a naive prefix match
  ['popolsku-v1', true], ['popolsku-v50', true], ['popolsku-v54', true], ['popolsku-v55', true],
  ['popolsku-v58', true], ['popolsku-v590', true], ['popolsku-v7', true], ['popolsku-v0', true],
  // preserved: the current shell, the audio cache, and everything that merely
  // begins with the same letters
  ['popolsku-v59', false], ['popolsku-audio', false],
  ['popolsku-video', false], ['popolsku-vocabulary', false], ['popolsku-vectors', false],
  ['popolsku-v59-beta', false], ['popolsku-v', false], ['popolsku-v59.1', false],
  ['popolsku-va', false], ['popolsku-v-56', false], ['popolsku-a2hs', false],
  ['unrelated-tool-cache', false], ['workbox-precache', false], ['workbox-runtime', false],
  ['', false], ['popolsku', false], ['xpopolsku-v55', false], ['popolsku-v55 ', false]
].forEach(function (row) {
  eq('A4 cleanup decision for ' + JSON.stringify(row[0]), API.isObsoleteShellCache(row[0]), row[1]);
});
eq('A4 a non-string cache name is never deleted',
   [API.isObsoleteShellCache(null), API.isObsoleteShellCache(undefined), API.isObsoleteShellCache(56)],
   [false, false, false]);

(function () {
  var worker = makeWorker({ seed: {
    'popolsku-v53': {}, 'popolsku-v54': {}, 'popolsku-v55': {}, 'popolsku-v58': {},
    'popolsku-v59': {}, 'popolsku-audio': {}, 'popolsku-a2hs-backup': {}, 'some-other-cache': {},
    'popolsku-video': {}, 'popolsku-vocabulary': {}, 'popolsku-vectors': {}, 'popolsku-v59-beta': {},
    'popolsku-v': {}
  } });
  runActivate(worker);
  eq('A5 every obsolete shell cache is removed in one activation',
     worker.caches.deleted.slice().sort(),
     ['popolsku-v53', 'popolsku-v54', 'popolsku-v55', 'popolsku-v58']);
  eq('A5 the surviving cache names are exactly the protected ones',
     worker.caches.names.slice().sort(),
     ['popolsku-a2hs-backup', 'popolsku-audio', 'popolsku-v', 'popolsku-v59', 'popolsku-v59-beta',
      'popolsku-vectors', 'popolsku-video', 'popolsku-vocabulary', 'some-other-cache']);
})();

// =========================================================================
// B. Required and optional precache
// =========================================================================
eq('B1 the required inventory is the offline shell', API.REQUIRED_ASSETS, [
  './', './pp-usage.js', './pp-answer.js', './pp-distractor.js', './pp-migrate.js',
  './data-a1.js', './data-a2.js', './data-b1.js', './data-grammar.js', './data-verbs.js',
  './data-scenarios.js', './data-podcasts.js', './audio-manifest.json'
]);
eq('B1 the optional inventory is presentation and installability only', API.OPTIONAL_ASSETS, [
  './manifest.json', './favicon.svg', './icon-192.png', './icon-512.png',
  './icon-maskable-512.png', './apple-touch-icon.png', './og-image.png',
  './fonts/plus-jakarta-sans-v12-latin-regular.woff2',
  './fonts/plus-jakarta-sans-v12-latin-500.woff2',
  './fonts/plus-jakarta-sans-v12-latin-600.woff2',
  './fonts/plus-jakarta-sans-v12-latin-700.woff2',
  './fonts/plus-jakarta-sans-v12-latin-800.woff2'
]);
eq('B1 the two inventories do not overlap',
   API.REQUIRED_ASSETS.filter(function (a) { return API.OPTIONAL_ASSETS.indexOf(a) !== -1; }), []);
ok('B1 no MP3 is precached',
   API.REQUIRED_ASSETS.concat(API.OPTIONAL_ASSETS).every(function (a) { return a.indexOf('.mp3') === -1; }));
ok('B1 the audio directory is not precached',
   API.REQUIRED_ASSETS.concat(API.OPTIONAL_ASSETS).every(function (a) { return a.indexOf('/audio/') === -1; }));
eq('B1 the inventory is bounded', API.REQUIRED_ASSETS.length + API.OPTIONAL_ASSETS.length, 25);
ok('B1 the shared helper scripts are all required',
   ['./pp-usage.js', './pp-answer.js', './pp-distractor.js', './pp-migrate.js']
     .every(function (a) { return API.REQUIRED_ASSETS.indexOf(a) !== -1; }));
ok('B1 all seven data files are required',
   API.REQUIRED_ASSETS.filter(function (a) { return /^\.\/data-/.test(a); }).length === 7);
ok('B1 installation is not one all-or-nothing transaction over a mixed list',
   SW_CODE.indexOf('addAll') === -1);
ok('B1 the root document is listed once and not duplicated as index.html',
   API.REQUIRED_ASSETS.indexOf('./') !== -1 &&
   API.REQUIRED_ASSETS.concat(API.OPTIONAL_ASSETS).indexOf('./index.html') === -1);

// All assets succeed.
(function () {
  var worker = makeWorker();
  var run = runInstall(worker);
  eq('B2 installation succeeds', run.results[0].state, 'fulfilled');
  var stored = invList(worker, SHELL);
  eq('B2 every required asset is stored under its canonical key',
     API.REQUIRED_ASSETS.map(function (a) { return API.canonicalKeyFor(API.parseUrl(a, ORIGIN + '/sw.js')); })
       .every(function (k) { return stored.indexOf(k) !== -1; }), true);
  eq('B2 every optional asset is stored too',
     API.OPTIONAL_ASSETS.map(function (a) { return API.canonicalKeyFor(API.parseUrl(a, ORIGIN + '/sw.js')); })
       .every(function (k) { return stored.indexOf(k) !== -1; }), true);
  eq('B2 the root document is stored once, under the root key',
     stored.filter(function (k) { return k === ORIGIN + '/'; }), [ORIGIN + '/']);
  ok('B2 no index.html key was created', stored.indexOf(ORIGIN + '/index.html') === -1);
  eq('B2 precache counts are reported', [worker.self.ppSwState.requiredCached,
     worker.self.ppSwState.optionalCached.length, worker.self.ppSwState.optionalFailed.length],
     [13, 12, 0]);
  ok('B2 precache bypasses the HTTP cache',
     worker.fetch.calls.every(function (c) { return c.init && c.init.cache === 'reload'; }));
  eq('B2 exactly one network request per inventory entry', worker.fetch.calls.length, 25);
  eq('B2 the network was never asked for /index.html',
     worker.fetch.calls.filter(function (c) { return /index\.html/.test(c.url); }), []);
})();

// Required failures: rejected fetch, 404, redirect, opaque.
[
  { name: 'a rejected network request', asset: ORIGIN + '/data-a1.js', outcome: { reject: new TypeError('offline') } },
  { name: 'an HTTP 404', asset: ORIGIN + '/pp-answer.js', outcome: { response: typed(ORIGIN + '/pp-answer.js', { status: 404, ok: false }) } },
  { name: 'an HTTP 500', asset: ORIGIN + '/audio-manifest.json', outcome: { response: typed(ORIGIN + '/audio-manifest.json', { status: 500, ok: false }) } },
  { name: 'a redirected response', asset: ORIGIN + '/', outcome: { response: typed(ORIGIN + '/', { redirected: true }) } },
  { name: 'an opaque response', asset: ORIGIN + '/data-grammar.js', outcome: { response: typed(ORIGIN + '/data-grammar.js', { type: 'opaque', status: 0, ok: false }) } },
  { name: 'an opaqueredirect response', asset: ORIGIN + '/pp-migrate.js', outcome: { response: typed(ORIGIN + '/pp-migrate.js', { type: 'opaqueredirect', status: 0, ok: false }) } },
  { name: 'a 206 partial response', asset: ORIGIN + '/data-b1.js', outcome: { response: typed(ORIGIN + '/data-b1.js', { status: 206 }) } },
  { name: 'an HTML body under a script key', asset: ORIGIN + '/pp-usage.js', outcome: { response: new FakeResponse({ url: ORIGIN + '/pp-usage.js', headers: { 'Content-Type': 'text/html; charset=utf-8' }, label: 'captive-portal' }) } },
  { name: 'a JSON body under a script key', asset: ORIGIN + '/data-a2.js', outcome: { response: new FakeResponse({ url: ORIGIN + '/data-a2.js', headers: { 'Content-Type': 'application/json' } }) } },
  { name: 'an HTML body under the audio manifest key', asset: ORIGIN + '/audio-manifest.json', outcome: { response: new FakeResponse({ url: ORIGIN + '/audio-manifest.json', headers: { 'Content-Type': 'text/html' } }) } },
  { name: 'a typeless response', asset: ORIGIN + '/data-b1.js', outcome: { response: new FakeResponse({ url: ORIGIN + '/data-b1.js' }) } }
].forEach(function (bad) {
  var worker = makeWorker({
    seed: { 'popolsku-v55': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'v55-shell') } },
    route: function (url) { return url === bad.asset ? bad.outcome : defaultRoute(url); }
  });
  var run = runInstall(worker);
  eq('B3 ' + bad.name + ' for a required asset fails the install', run.results[0].state, 'rejected');
  ok('B3 ' + bad.name + ' removes the incomplete new cache',
     worker.caches.deleted.indexOf(SHELL) !== -1 && !worker.caches.caches[SHELL]);
  eq('B3 ' + bad.name + ' does not delete the active shell cache',
     worker.caches.deleted.filter(function (n) { return n === 'popolsku-v55'; }), []);
  ok('B3 ' + bad.name + ' leaves the active shell cache intact',
     !!worker.caches.caches['popolsku-v55'] &&
     entryLabel(worker, 'popolsku-v55', 'https://popolsku.app/') === 'v55-shell');
  ok('B3 ' + bad.name + ' is reported', worker.self.ppSwState.installFailures.length > 0);
});

// A cache.open failure at install time behaves the same way.
(function () {
  var worker = makeWorker({ seed: { 'popolsku-v55': {} } });
  worker.caches.openBehavior = function (name) {
    return name === SHELL ? { reject: new Error('QuotaExceededError') } : null;
  };
  var run = runInstall(worker);
  eq('B4 an unopenable new cache fails the install', run.results[0].state, 'rejected');
  ok('B4 the previous shell cache survives', !!worker.caches.caches['popolsku-v55']);
  eq('B4 no old cache was cleaned up', worker.caches.deleted, [SHELL]);
})();

// Optional failures: contained.
(function () {
  var failing = [ORIGIN + '/og-image.png', ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-800.woff2'];
  var worker = makeWorker({ route: function (url) {
    if (url === failing[0]) return { response: typed(url, { status: 404, ok: false }) };
    if (url === failing[1]) return { reject: new TypeError('offline') };
    return defaultRoute(url);
  } });
  var run = runInstall(worker);
  eq('B5 an optional failure does not reject the install', run.results[0].state, 'fulfilled');
  var stored = invList(worker, SHELL);
  ok('B5 the failed optional assets are not cached',
     stored.indexOf(failing[0]) === -1 && stored.indexOf(failing[1]) === -1);
  ok('B5 the other optional assets are still cached',
     stored.indexOf(ORIGIN + '/favicon.svg') !== -1 && stored.indexOf(ORIGIN + '/manifest.json') !== -1 &&
     stored.indexOf(ORIGIN + '/icon-512.png') !== -1);
  ok('B5 every required asset is still cached',
     API.REQUIRED_ASSETS.every(function (a) {
       return stored.indexOf(API.canonicalKeyFor(API.parseUrl(a, ORIGIN + '/sw.js'))) !== -1;
     }));
  eq('B5 the failures are observable', worker.self.ppSwState.optionalFailed.sort(),
     ['./fonts/plus-jakarta-sans-v12-latin-800.woff2', './og-image.png']);
  eq('B5 the successes are observable', worker.self.ppSwState.optionalCached.length, 10);
  eq('B5 nothing was deleted', worker.caches.deleted, []);
  ok('B5 each failure is logged once',
     worker.warnings.filter(function (w) { return /optional asset skipped/.test(w); }).length === 2);
})();

// Every optional asset can fail without costing the shell.
(function () {
  var worker = makeWorker({ route: function (url) {
    var isOptional = API.OPTIONAL_ASSETS.some(function (a) {
      return url === API.canonicalKeyFor(API.parseUrl(a, ORIGIN + '/sw.js'));
    });
    return isOptional ? { reject: new TypeError('offline') } : defaultRoute(url);
  } });
  var run = runInstall(worker);
  eq('B6 installation still succeeds with no optional asset at all', run.results[0].state, 'fulfilled');
  eq('B6 the shell cache holds exactly the required assets',
     invLen(worker, SHELL), 13);
  eq('B6 the shell cache was not discarded', worker.caches.deleted, []);
})();

// Required failure wins even when optional assets would have succeeded.
(function () {
  var worker = makeWorker({ route: function (url) {
    return url === ORIGIN + '/data-podcasts.js' ? { reject: new TypeError('offline') } : defaultRoute(url);
  } });
  var run = runInstall(worker);
  eq('B7 one failed required asset fails the whole install', run.results[0].state, 'rejected');
  eq('B7 optional assets are never fetched after a required failure',
     worker.fetch.calls.filter(function (c) { return /favicon|icon-|og-image|fonts\//.test(c.url); }), []);
  ok('B7 the incomplete cache is gone', !worker.caches.caches[SHELL]);
})();

// =========================================================================
// C. Update lifecycle
// =========================================================================
ok('C1 the source never calls skipWaiting', SW_CODE.indexOf('skipWaiting') === -1);
ok('C1 the source never calls clients.claim',
   SW_CODE.indexOf('clients.claim') === -1 && SW_CODE.indexOf('claim(') === -1);
ok('C1 no message-based control protocol was introduced',
   SW_CODE.indexOf('addEventListener("message"') === -1 &&
   SW_CODE.indexOf("addEventListener('message'") === -1 &&
   SW_CODE.indexOf('postMessage') === -1);
ok('C1 no automatic reload or update UI was introduced',
   SW_CODE.indexOf('location.reload') === -1 && SW_CODE.indexOf('showNotification') === -1);
ok('C1 index.html still registers the worker without a skip-waiting handshake',
   INDEX.indexOf('navigator.serviceWorker.register("sw.js")') !== -1 &&
   INDEX.indexOf('skipWaiting') === -1 && INDEX.indexOf('controllerchange') === -1);

// A. First install, no existing worker.
(function () {
  var worker = makeWorker();
  var run = runInstall(worker);
  eq('C2 first install succeeds', run.results[0].state, 'fulfilled');
  eq('C2 first install never takes over the page that installed it', worker.self.skipWaitingCalls, 0);
  var act = runActivate(worker);
  eq('C2 activation succeeds', act.results[0].state, 'fulfilled');
  eq('C2 activation never claims the loaded page', worker.self.claimCalls, 0);
  eq('C2 a first install has nothing to clean up', worker.caches.deleted, []);
  eq('C2 the shell is ready for the next navigation', invLen(worker, SHELL), 25);
})();

// B. Update with an open v55 tab: install and wait, change nothing.
(function () {
  var worker = makeWorker({ seed: {
    'popolsku-v55': {
      'https://popolsku.app/': seeded('https://popolsku.app/', 'v55-shell'),
      'https://popolsku.app/data-a1.js': seeded('https://popolsku.app/data-a1.js', 'v55-data')
    },
    'popolsku-audio': { 'https://popolsku.app/audio/ab12ef34.mp3': seeded('https://popolsku.app/audio/ab12ef34.mp3', 'clip') }
  } });
  var run = runInstall(worker);
  eq('C3 the new worker installs', run.results[0].state, 'fulfilled');
  eq('C3 it does not skip waiting', worker.self.skipWaitingCalls, 0);
  eq('C3 it does not claim the open tab', worker.self.claimCalls, 0);
  eq('C3 a waiting worker deletes nothing', worker.caches.deleted, []);
  eq('C3 the open tab still has its whole v55 cache',
     inv(worker, 'popolsku-v55'),
     ['https://popolsku.app/', 'https://popolsku.app/data-a1.js']);
  eq('C3 the v55 shell body is untouched',
     entryLabel(worker, 'popolsku-v55', 'https://popolsku.app/'), 'v55-shell');
  // The open tab keeps being served from v55 by its own (old) worker: this worker
  // writes only into v56, so the two generations cannot mix.
  eq('C3 the new worker writes only into its own cache',
     worker.caches.opened.filter(function (n) { return n !== SHELL; }), []);

  // C. Activation once the old clients are gone.
  var act = runActivate(worker);
  eq('C4 activation succeeds', act.results[0].state, 'fulfilled');
  eq('C4 activation removes the superseded shell', worker.caches.deleted, ['popolsku-v55']);
  eq('C4 activation keeps the new shell and the audio cache',
     worker.caches.names.slice().sort(), ['popolsku-audio', 'popolsku-v59']);
  eq('C4 activation still does not claim anyone', worker.self.claimCalls, 0);
})();

// D. Failed v56 install leaves v55 alone and cleans up after itself.
(function () {
  var worker = makeWorker({
    seed: { 'popolsku-v55': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'v55-shell') },
            'popolsku-audio': {} },
    route: function (url) {
      return url === ORIGIN + '/pp-usage.js' ? { response: typed(url, { status: 503, ok: false }) } : defaultRoute(url);
    }
  });
  var run = runInstall(worker);
  eq('C5 the install fails', run.results[0].state, 'rejected');
  eq('C5 only the incomplete new cache is deleted', worker.caches.deleted, [SHELL]);
  eq('C5 v55 and the audio cache both remain',
     worker.caches.names.slice().sort(), ['popolsku-audio', 'popolsku-v55']);
  eq('C5 no takeover was attempted', [worker.self.skipWaitingCalls, worker.self.claimCalls], [0, 0]);
})();

// =========================================================================
// D. Request classification
// =========================================================================
[
  [get(ORIGIN + '/data-a1.js', { method: 'POST' }), 'non-get'],
  [get(ORIGIN + '/', { method: 'HEAD' }), 'non-get'],
  [get(ORIGIN + '/api', { method: 'PUT' }), 'non-get'],
  [get('chrome-extension://abcdef/injected.js'), 'unsupported-scheme'],
  [get('data:text/plain,hello'), 'unsupported-scheme'],
  [get('blob:https://popolsku.app/1234'), 'unsupported-scheme'],
  [get('not a url'), 'unsupported-scheme'],
  [get('https://example.com/tracker.js'), 'cross-origin'],
  [nav('https://example.com/'), 'cross-origin'],
  [get('http://popolsku.app/favicon.svg'), 'cross-origin'],
  [get('https://cdn.popolsku.app/favicon.svg'), 'cross-origin'],
  [get(ORIGIN + '/audio/ab12ef34.mp3', { headers: { Range: 'bytes=0-' } }), 'range'],
  [get(ORIGIN + '/data-a1.js', { headers: { range: 'bytes=100-200' } }), 'range'],
  [nav(ORIGIN + '/'), 'root-navigation'],
  [nav(ORIGIN + '/index.html'), 'root-navigation'],
  [nav(ORIGIN + '/?pwa=1'), 'root-navigation'],
  [nav(ORIGIN + '/grammar/biernik-accusative/'), 'generated-navigation'],
  [nav(ORIGIN + '/guide/listening/index.html'), 'generated-navigation'],
  [nav(ORIGIN + '/grammar/not-a-generated-page/'), 'unknown-navigation'],
  [get(ORIGIN + '/data-a1.js'), 'data'],
  [get(ORIGIN + '/data-grammar.js?v=9'), 'data'],
  [get(ORIGIN + '/data-podcasts.js'), 'data'],
  [get(ORIGIN + '/audio-manifest.json'), 'audio-manifest'],
  [get(ORIGIN + '/audio-manifest.json?t=17'), 'audio-manifest'],
  [get(ORIGIN + '/audio/ab12ef34.mp3'), 'audio'],
  [get(ORIGIN + '/audio/000311d1288f.mp3?v=2'), 'audio'],
  [get(ORIGIN + '/pp-answer.js'), 'static'],
  [get(ORIGIN + '/pp-usage.js'), 'static'],
  [get(ORIGIN + '/pp-distractor.js'), 'static'],
  [get(ORIGIN + '/pp-migrate.js'), 'static'],
  [get(ORIGIN + '/manifest.json'), 'static'],
  [get(ORIGIN + '/favicon.svg?v=17'), 'static'],
  [get(ORIGIN + '/icon-192.png'), 'static'],
  [get(ORIGIN + '/icon-maskable-512.png'), 'static'],
  [get(ORIGIN + '/apple-touch-icon.png'), 'static'],
  [get(ORIGIN + '/og-image.png?v=2'), 'static'],
  [get(ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-regular.woff2'), 'static'],
  [get(ORIGIN + '/sitemap.xml'), 'unknown'],
  [get(ORIGIN + '/robots.txt'), 'unknown'],
  [get(ORIGIN + '/api/progress?user=7'), 'unknown'],
  [get(ORIGIN + '/data-a1.json'), 'unknown'],
  [get(ORIGIN + '/audio/notahash.mp3'), 'unknown'],
  [get(ORIGIN + '/audio/ab12ef34.wav'), 'unknown'],
  [get(ORIGIN + '/grammar/biernik-accusative/'), 'unknown'],
  [get(ORIGIN + '/fonts/other.woff2'), 'unknown']
].forEach(function (row) {
  eq('D1 ' + row[1] + ': ' + row[0].method + ' ' + row[0].url +
     (row[0].headers.get('range') ? ' (Range)' : '') + (row[0].mode === 'navigate' ? ' (navigate)' : ''),
     API.classifyRequest(row[0]), row[1]);
});
eq('D1 the static allowlist is derived from the precache inventory',
   API.STATIC_ASSET_PATHS.slice().sort(), [
     '/apple-touch-icon.png', '/favicon.svg',
     '/fonts/plus-jakarta-sans-v12-latin-500.woff2', '/fonts/plus-jakarta-sans-v12-latin-600.woff2',
     '/fonts/plus-jakarta-sans-v12-latin-700.woff2', '/fonts/plus-jakarta-sans-v12-latin-800.woff2',
     '/fonts/plus-jakarta-sans-v12-latin-regular.woff2', '/icon-192.png', '/icon-512.png',
     '/icon-maskable-512.png', '/manifest.json', '/og-image.png', '/pp-answer.js',
     '/pp-distractor.js', '/pp-migrate.js', '/pp-usage.js'
   ]);

// Pass-through categories must not be intercepted at all.
(function () {
  [get(ORIGIN + '/', { method: 'POST' }),
   get('chrome-extension://abcdef/injected.js'),
   get('https://example.com/tracker.js'),
   nav('https://example.com/'),
   get(ORIGIN + '/api/progress?user=7'),
   get(ORIGIN + '/sitemap.xml')].forEach(function (request) {
    var worker = makeWorker();
    var run = runFetch(worker, request);
    ok('D2 ' + request.method + ' ' + request.url + ' is not intercepted', !run.intercepted);
    eq('D2 ' + request.url + ' triggers no worker fetch', worker.fetch.calls, []);
    eq('D2 ' + request.url + ' opens no cache', worker.caches.opened, []);
    eq('D2 ' + request.url + ' schedules no write', worker.self.ppSwState.writes.scheduled, 0);
  });
})();

// A cross-origin GET the app might make is never written to an application cache.
// Deliberately uses paths that ARE on the same-origin allowlist, so that losing
// the origin gate would show up as a cached cross-origin response.
(function () {
  ['https://cdn.popolsku.app/favicon.svg?v=17', 'https://example.com/data-a1.js',
   'https://example.com/audio/ab12ef34.mp3', 'https://example.com/manifest.json'].forEach(function (url) {
    var worker = makeWorker({ route: function (u) { return { response: typed(u, { type: 'cors' }) }; } });
    var run = runFetch(worker, get(url));
    ok('D3 cross-origin ' + url + ' is left to the browser', !run.intercepted);
    eq('D3 cross-origin ' + url + ' is never cached', storedKeys(worker), []);
    eq('D3 cross-origin ' + url + ' schedules no write', worker.self.ppSwState.writes.scheduled, 0);
  });
})();

// Navigation strategy: network-first, cached under the canonical key.
(function () {
  var worker = makeWorker();
  var run = runFetch(worker, nav(ORIGIN + '/?pwa=1'));
  ok('D4 a navigation is intercepted', run.intercepted);
  eq('D4 the network is asked first with no-store', worker.fetch.calls.length, 1);
  eq('D4 no-store is preserved', worker.fetch.calls[0].init.cache, 'no-store');
  eq('D4 the shell is cached under the canonical root key',
     inv(worker, SHELL), [ORIGIN + '/']);
  eq('D4 the response is returned to the page', respState(run), 'fulfilled');
})();

// A generated page is cached under its own directory key, never over the shell.
(function () {
  var worker = makeWorker({ seed: { 'popolsku-v59': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'shell') } } });
  runFetch(worker, nav(ORIGIN + '/grammar/biernik-accusative/'));
  eq('D5 the generated page gets its own key',
     inv(worker, SHELL), [ORIGIN + '/', ORIGIN + '/grammar/biernik-accusative/']);
  eq('D5 the cached shell was not overwritten',
     entryLabel(worker, SHELL, 'https://popolsku.app/'), 'shell');
})();

// Offline navigation uses the exact page, then an intentional redirect for an
// unvisited generated route. Root still uses only the canonical root shell.
(function () {
  var worker = makeWorker({
    seed: { 'popolsku-v59': {
      'https://popolsku.app/': seeded('https://popolsku.app/', 'shell'),
      'https://popolsku.app/guide/': seeded('https://popolsku.app/guide/', 'guide')
    } },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  var visited = runFetch(worker, nav(ORIGIN + '/guide/index.html'));
  eq('D6 a visited generated page is served from cache offline',
     respLabel(visited), 'guide');
  var unvisited = runFetch(worker, nav(ORIGIN + '/grammar/wolacz-vocative/'));
  eq('D6 an unvisited generated page redirects instead of receiving the shell',
     [respValue(unvisited).status, respValue(unvisited).headers.get('location'), respLabel(unvisited)],
     [302, ORIGIN + '/', 'redirect-to-root']);
  var root = runFetch(worker, nav(ORIGIN + '/index.html'));
  eq('D6 /index.html offline resolves to the cached root shell', respLabel(root), 'shell');
})();

// Non-navigation requests never receive the HTML shell.
(function () {
  var worker = makeWorker({
    seed: { 'popolsku-v59': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'shell') } },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  [get(ORIGIN + '/data-a1.js'), get(ORIGIN + '/audio-manifest.json'),
   get(ORIGIN + '/manifest.json'), get(ORIGIN + '/icon-192.png'),
   get(ORIGIN + '/audio/ab12ef34.mp3'), get(ORIGIN + '/pp-answer.js')].forEach(function (request) {
    var run = runFetch(worker, request);
    ok('D7 offline ' + request.url + ' does not return the HTML shell',
       respState(run) !== 'fulfilled' || respLabel(run) !== 'shell');
  });
})();

// Data / manifest strategy: network-first, no-store, cache fallback.
[['data-a1.js', '/data-a1.js'], ['audio-manifest.json', '/audio-manifest.json']].forEach(function (row) {
  var worker = makeWorker();
  var online = runFetch(worker, get(ORIGIN + row[1] + '?v=3'));
  eq('D8 ' + row[0] + ' asks the network first', worker.fetch.calls.length, 1);
  eq('D8 ' + row[0] + ' keeps cache:no-store', worker.fetch.calls[0].init.cache, 'no-store');
  eq('D8 ' + row[0] + ' is cached under one canonical key',
     inv(worker, SHELL), [ORIGIN + row[1]]);
  eq('D8 ' + row[0] + ' returns the network response', respState(online), 'fulfilled');

  var offline = makeWorker({
    seed: { 'popolsku-v59': (function () { var s = {}; s[ORIGIN + row[1]] = seeded(ORIGIN + row[1], 'cached-' + row[0]); return s; })() },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  var run = runFetch(offline, get(ORIGIN + row[1] + '?v=4'));
  eq('D8 ' + row[0] + ' falls back to the cached copy offline',
     respLabel(run), 'cached-' + row[0]);
});

// MP3 strategy: cache-first out of the audio cache.
(function () {
  var worker = makeWorker({ seed: { 'popolsku-audio': {
    'https://popolsku.app/audio/ab12ef34.mp3': seeded('https://popolsku.app/audio/ab12ef34.mp3', 'warm-clip') } } });
  var warm = runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3'));
  eq('D9 a warm clip is served from cache', respLabel(warm), 'warm-clip');
  eq('D9 a warm clip makes no network request', worker.fetch.calls, []);

  var cold = makeWorker();
  var run = runFetch(cold, get(ORIGIN + '/audio/000311d1288f.mp3'));
  eq('D9 a cold clip is fetched', cold.fetch.calls.length, 1);
  eq('D9 a cold clip is stored in the audio cache',
     inv(cold, AUDIO), [ORIGIN + '/audio/000311d1288f.mp3']);
  eq('D9 a cold clip never touches the shell cache', inv(cold, SHELL), 'no-cache');
  eq('D9 the clip is returned to the player', respState(run), 'fulfilled');
})();

// Static asset strategy: cache-first into the shell cache, query-tolerant.
(function () {
  var worker = makeWorker({ seed: { 'popolsku-v59': {
    'https://popolsku.app/favicon.svg': seeded('https://popolsku.app/favicon.svg', 'precached-favicon') } } });
  var run = runFetch(worker, get(ORIGIN + '/favicon.svg?v=17'));
  eq('E0 the query-bearing favicon is served by the precached entry',
     respLabel(run), 'precached-favicon');
  eq('E0 no duplicate key is created', inv(worker, SHELL), [ORIGIN + '/favicon.svg']);
  eq('E0 no network request was needed', worker.fetch.calls, []);
})();

// Range requests: never written, warm audio still served.
(function () {
  var worker = makeWorker({ seed: { 'popolsku-audio': {
    'https://popolsku.app/audio/ab12ef34.mp3': seeded('https://popolsku.app/audio/ab12ef34.mp3', 'warm-clip') } } });
  var run = runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3', { headers: { Range: 'bytes=0-' } }));
  eq('D10 a Range request for a warm clip is answered from the audio cache as a partial',
     [respState(run), respValue(run) ? respValue(run).status : 'no-response'], ['fulfilled', 206]);
  eq('D10 the Range request wrote nothing', worker.self.ppSwState.writes.scheduled, 0);

  var cold = makeWorker({ route: function (url) {
    return { response: typed(url, { status: 206, label: 'partial' }) };
  } });
  var coldRun = runFetch(cold, get(ORIGIN + '/audio/000311d1288f.mp3', { headers: { Range: 'bytes=0-99' } }));
  eq('D10 a cold Range request still reaches the network', cold.fetch.calls.length, 1);
  eq('D10 the partial response is returned to the player', respLabel(coldRun), 'partial');
  eq('D10 no partial response is ever cached', storedKeys(cold), []);
  eq('D10 no write is scheduled for a partial response', cold.self.ppSwState.writes.scheduled, 0);

  // Some servers ignore Range and answer with the whole file; that whole response
  // must not be stored either, because the request was a partial one.
  var whole = makeWorker({ route: function (url) {
    return { response: typed(url, { label: 'whole-file' }) };
  } });
  var wholeRun = runFetch(whole, get(ORIGIN + '/audio/000311d1288f.mp3', { headers: { Range: 'bytes=0-' } }));
  eq('D10 a full response to a Range request is returned', respLabel(wholeRun), 'whole-file');
  eq('D10 a full response to a Range request is not cached', storedKeys(whole), []);
  eq('D10 and it schedules no write', whole.self.ppSwState.writes.scheduled, 0);

  var other = makeWorker();
  var otherRun = runFetch(other, get(ORIGIN + '/data-a1.js', { headers: { Range: 'bytes=0-10' } }));
  ok('D10 a Range request for a non-audio asset is not intercepted', !otherRun.intercepted);
  eq('D10 and it is not cached', storedKeys(other), []);
})();

// Response validation before every write.
var JS_KEY = ORIGIN + '/pp-answer.js';
function withType(type, extra) {
  var opts = { headers: type === null ? {} : { 'Content-Type': type } };
  Object.keys(extra || {}).forEach(function (k) { opts[k] = extra[k]; });
  return new FakeResponse(opts);
}
[
  ['a 404', withType('text/javascript', { status: 404, ok: false }), false],
  ['a 500', withType('text/javascript', { status: 500, ok: false }), false],
  ['a 302 marked ok', withType('text/javascript', { status: 302, ok: false }), false],
  ['a redirected 200', withType('text/javascript', { redirected: true }), false],
  ['an opaque response', withType('text/javascript', { type: 'opaque', status: 0, ok: false }), false],
  ['an opaqueredirect response', withType('text/javascript', { type: 'opaqueredirect', status: 0, ok: false }), false],
  ['an error response', withType('text/javascript', { type: 'error', status: 0, ok: false }), false],
  ['a cors response', withType('text/javascript', { type: 'cors' }), false],
  ['a 206 partial', withType('text/javascript', { status: 206 }), false],
  ['a 204 no-content', withType('text/javascript', { status: 204 }), false],
  ['a missing response', undefined, false],
  ['a basic 200 of the right type', withType('text/javascript'), true],
  ['a default-typed 200 of the right type', withType('text/javascript', { type: 'default' }), true]
].forEach(function (row) {
  eq('D11 cacheability of ' + row[0], API.isCacheableResponse(row[1], JS_KEY), row[2]);
});

// ...and the same rule enforced through a real branch.
[
  ['404', function (url) { return typed(url, { status: 404, ok: false }); }],
  ['opaque', function (url) { return typed(url, { type: 'opaque', status: 0, ok: false }); }],
  ['redirected', function (url) { return typed(url, { redirected: true }); }]
].forEach(function (row) {
  ['/data-a1.js', '/audio-manifest.json', '/pp-answer.js', '/audio/ab12ef34.mp3'].forEach(function (path) {
    var worker = makeWorker({ route: function (url) { return { response: row[1](url) }; } });
    var run = runFetch(worker, get(ORIGIN + path));
    eq('D12 ' + row[0] + ' on ' + path + ' is not cached', storedKeys(worker), []);
    eq('D12 ' + row[0] + ' on ' + path + ' is still returned to the page',
       respState(run), 'fulfilled');
    eq('D12 ' + row[0] + ' on ' + path + ' schedules no write',
       worker.self.ppSwState.writes.scheduled, 0);
  });
  var navWorker = makeWorker({ route: function (url) { return { response: row[1](url) }; } });
  runFetch(navWorker, nav(ORIGIN + '/'));
  eq('D12 ' + row[0] + ' on a navigation is not cached', storedKeys(navWorker), []);
});

// No catch-all: an unknown same-origin GET stays out of the caches even when the
// response would be perfectly cacheable.
(function () {
  var worker = makeWorker();
  runFetch(worker, get(ORIGIN + '/some/new/endpoint.json'));
  eq('D13 an unknown same-origin endpoint is never cached', storedKeys(worker), []);
  ok('D13 the fetch handler has no default cache-everything branch',
     countOf(SW_CODE, 'cacheWrite(') === 3 &&
     SW_CODE.indexOf('caches.open(CACHE).then(c => c.put') === -1);
})();

// =========================================================================
// E. Canonical keys
// =========================================================================
function key(url) { return API.canonicalKeyFor(API.parseUrl(url)); }
[
  [ORIGIN + '/', ORIGIN + '/'],
  [ORIGIN + '/index.html', ORIGIN + '/'],
  [ORIGIN + '/?pwa=1', ORIGIN + '/'],
  [ORIGIN + '/?pwa=0', ORIGIN + '/'],
  [ORIGIN + '/index.html?pwa=1', ORIGIN + '/'],
  [ORIGIN + '/#privacy', ORIGIN + '/'],
  [ORIGIN + '/?pwa=1#install', ORIGIN + '/'],
  [ORIGIN + '/data-a1.js', ORIGIN + '/data-a1.js'],
  [ORIGIN + '/data-a1.js?v=17', ORIGIN + '/data-a1.js'],
  [ORIGIN + '/data-grammar.js?bust=1754246400000', ORIGIN + '/data-grammar.js'],
  [ORIGIN + '/audio-manifest.json', ORIGIN + '/audio-manifest.json'],
  [ORIGIN + '/audio-manifest.json?v=2', ORIGIN + '/audio-manifest.json'],
  [ORIGIN + '/guide/', ORIGIN + '/guide/'],
  [ORIGIN + '/guide/index.html', ORIGIN + '/guide/'],
  [ORIGIN + '/grammar/biernik-accusative/', ORIGIN + '/grammar/biernik-accusative/'],
  [ORIGIN + '/grammar/biernik-accusative/index.html', ORIGIN + '/grammar/biernik-accusative/'],
  [ORIGIN + '/vocabulary/polish-idioms/index.html?x=1', ORIGIN + '/vocabulary/polish-idioms/'],
  [ORIGIN + '/audio/ab12ef34.mp3', ORIGIN + '/audio/ab12ef34.mp3'],
  [ORIGIN + '/audio/ab12ef34.mp3?v=2', ORIGIN + '/audio/ab12ef34.mp3'],
  [ORIGIN + '/favicon.svg?v=17', ORIGIN + '/favicon.svg'],
  [ORIGIN + '/manifest.json', ORIGIN + '/manifest.json'],
  [ORIGIN + '/some/new/endpoint.json?user=7', ORIGIN + '/some/new/endpoint.json']
].forEach(function (row) {
  eq('E1 canonical key for ' + row[0], key(row[0]), row[1]);
});
eq('E2 an external URL is never canonicalized', key('https://example.com/x.js?a=1'), null);
eq('E2 a protocol-different same-host URL is never canonicalized', key('http://popolsku.app/'), null);
eq('E2 a subdomain URL is never canonicalized', key('https://cdn.popolsku.app/favicon.svg'), null);
eq('E2 an extension URL is never canonicalized', key('chrome-extension://abc/x.js'), null);
eq('E2 an unparseable URL yields no key', API.canonicalKeyFor(API.parseUrl('not a url')), null);

eq('E3 / and /index.html resolve to one key', key(ORIGIN + '/') === key(ORIGIN + '/index.html'), true);
eq('E3 ?pwa=1 and ?pwa=0 resolve to the same shell key',
   key(ORIGIN + '/?pwa=1') === key(ORIGIN + '/?pwa=0'), true);
eq('E3 a generated directory URL and its index.html resolve to one key',
   key(ORIGIN + '/guide/listening/') === key(ORIGIN + '/guide/listening/index.html'), true);
ok('E3 canonicalization does not collide different resources',
   key(ORIGIN + '/') !== key(ORIGIN + '/guide/') &&
   key(ORIGIN + '/data-a1.js') !== key(ORIGIN + '/data-a2.js') &&
   key(ORIGIN + '/favicon.svg') !== key(ORIGIN + '/manifest.json') &&
   key(ORIGIN + '/audio/aa.mp3') !== key(ORIGIN + '/audio/bb.mp3'));
ok('E3 an index.html-like filename is not truncated',
   key(ORIGIN + '/guide/myindex.html') === ORIGIN + '/guide/myindex.html' &&
   key(ORIGIN + '/index.htmlx') === ORIGIN + '/index.htmlx');
eq('E4 canonicalPath is a pure path rule',
   ['/index.html', '/guide/index.html', '/guide/', '/x/index.htm', '/index.html/more']
     .map(function (p) { return API.canonicalPath(p); }),
   ['/', '/guide/', '/guide/', '/x/index.htm', '/index.html/more']);

// The browser-visible URL is never rewritten: only the key changes.
(function () {
  var worker = makeWorker();
  var request = nav(ORIGIN + '/?pwa=1');
  runFetch(worker, request);
  eq('E5 the request object handed to the network is the original', worker.fetch.calls[0].request, request);
  eq('E5 the page URL still carries its query', request.url, ORIGIN + '/?pwa=1');
  eq('E5 only the cache key was canonicalized', inv(worker, SHELL), [ORIGIN + '/']);
})();

// One warmed shell entry serves every root variant offline.
(function () {
  var worker = makeWorker({
    seed: { 'popolsku-v59': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'shell') } },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  [ORIGIN + '/', ORIGIN + '/index.html', ORIGIN + '/?pwa=1', ORIGIN + '/?pwa=0'].forEach(function (url) {
    var run = runFetch(worker, nav(url));
    eq('E6 offline ' + url + ' is served by the one cached shell entry',
       respLabel(run), 'shell');
  });
  eq('E6 no duplicate shell entries were created', inv(worker, SHELL), [ORIGIN + '/']);
})();

// Query variants of an immutable asset do not multiply cache entries.
(function () {
  var worker = makeWorker();
  runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3?v=1'));
  runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3?v=2'));
  runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3'));
  eq('E7 one clip, one audio cache entry', inv(worker, AUDIO), [ORIGIN + '/audio/ab12ef34.mp3']);
  eq('E7 the network was only needed once', worker.fetch.calls.length, 1);

  var data = makeWorker();
  runFetch(data, get(ORIGIN + '/data-a1.js?v=1'));
  runFetch(data, get(ORIGIN + '/data-a1.js?v=2'));
  eq('E7 one data file, one shell cache entry', inv(data, SHELL), [ORIGIN + '/data-a1.js']);
})();

// =========================================================================
// F. Runtime cache-write lifetime
// =========================================================================
var WRITE_BRANCHES = [
  { name: 'navigation', request: nav(ORIGIN + '/'), cache: 'popolsku-v59', key: ORIGIN + '/' },
  { name: 'generated page', request: nav(ORIGIN + '/guide/'), cache: 'popolsku-v59', key: ORIGIN + '/guide/' },
  { name: 'data file', request: get(ORIGIN + '/data-a1.js'), cache: 'popolsku-v59', key: ORIGIN + '/data-a1.js' },
  { name: 'audio manifest', request: get(ORIGIN + '/audio-manifest.json'), cache: 'popolsku-v59', key: ORIGIN + '/audio-manifest.json' },
  { name: 'mp3', request: get(ORIGIN + '/audio/ab12ef34.mp3'), cache: 'popolsku-audio', key: ORIGIN + '/audio/ab12ef34.mp3' },
  { name: 'static asset', request: get(ORIGIN + '/pp-answer.js'), cache: 'popolsku-v59', key: ORIGIN + '/pp-answer.js' },
  { name: 'font', request: get(ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-regular.woff2'), cache: 'popolsku-v59', key: ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-regular.woff2' },
  { name: 'web app manifest', request: get(ORIGIN + '/manifest.json'), cache: 'popolsku-v59', key: ORIGIN + '/manifest.json' }
];

WRITE_BRANCHES.forEach(function (branch) {
  // Success: response returned, write bound to the event, stored in the right cache.
  var worker = makeWorker();
  var run = runFetch(worker, branch.request);
  eq('F1 ' + branch.name + ' returns the network response', respState(run), 'fulfilled');
  eq('F1 ' + branch.name + ' binds exactly one write to the fetch event', run.event.waits.length, 1);
  eq('F1 ' + branch.name + ' completes its write', writeState(run), 'fulfilled');
  eq('F1 ' + branch.name + ' writes into the intended cache',
     inv(worker, branch.cache), [branch.key]);
  eq('F1 ' + branch.name + ' writes nowhere else',
     storedKeys(worker), [branch.cache + ' :: ' + branch.key]);
  eq('F1 ' + branch.name + ' records one successful write',
     [worker.self.ppSwState.writes.scheduled, worker.self.ppSwState.writes.succeeded,
      worker.self.ppSwState.writes.failed], [1, 1, 0]);
  var served = respValue(run);
  ok('F1 ' + branch.name + ' hands the page an unconsumed body', served && served.bodyUsed === false);
  eq('F1 ' + branch.name + ' cached a clone, not the served response',
     entry(worker, branch.cache, branch.key) === served, false);
  eq('F1 ' + branch.name + ' cached a copy of the same body',
     entryLabel(worker, branch.cache, branch.key), served ? served.label : null);

  // Delayed put: the response is available before the write settles, and the
  // event stays extended until it does.
  var slow = makeWorker();
  slow.caches.putBehavior = function () { return { defer: true }; };
  var slowRun = runFetch(slow, branch.request);
  eq('F2 ' + branch.name + ' returns before a slow write finishes', respState(slowRun), 'fulfilled');
  eq('F2 ' + branch.name + ' keeps the event alive while the write is pending',
     [slowRun.event.waits.length, writeState(slowRun)], [1, 'pending']);
  eq('F2 ' + branch.name + ' has one write in flight', slow.caches.pendingPuts.length, 1);
  pending(slow).settle();
  drain();
  eq('F2 ' + branch.name + ' the delayed write completes on the event', writeState(slowRun), 'fulfilled');
  eq('F2 ' + branch.name + ' the delayed write reached the cache',
     inv(slow, branch.cache), [branch.key]);

  // cache.open rejects.
  var openFail = makeWorker();
  openFail.caches.openBehavior = function () { return { reject: new Error('cache open blocked') }; };
  var openRun = runFetch(openFail, branch.request);
  eq('F3 ' + branch.name + ' survives a cache.open rejection', respState(openRun), 'fulfilled');
  eq('F3 ' + branch.name + ' contains the open failure', writeState(openRun), 'fulfilled');
  eq('F3 ' + branch.name + ' records the failure',
     [openFail.self.ppSwState.writes.failed, openFail.self.ppSwState.writes.succeeded], [1, 0]);
  ok('F3 ' + branch.name + ' logs the failure',
     openFail.warnings.some(function (w) { return /cache write failed/.test(w); }));

  // cache.put rejects.
  var putFail = makeWorker();
  putFail.caches.putBehavior = function () { return { reject: new Error('put blocked') }; };
  var putRun = runFetch(putFail, branch.request);
  eq('F4 ' + branch.name + ' survives a cache.put rejection', respState(putRun), 'fulfilled');
  eq('F4 ' + branch.name + ' still returns a usable response',
     respValue(putRun) ? respValue(putRun).bodyUsed : null, false);
  eq('F4 ' + branch.name + ' contains the put failure', writeState(putRun), 'fulfilled');
  eq('F4 ' + branch.name + ' records the put failure', putFail.self.ppSwState.writes.failed, 1);

  // Quota rejection, and the next request still works.
  var quota = makeWorker();
  var quotaHits = 0;
  quota.caches.putBehavior = function () {
    quotaHits++;
    if (quotaHits > 1) return null;
    var err = new Error('The quota has been exceeded.');
    err.name = 'QuotaExceededError';
    return { reject: err };
  };
  var quotaRun = runFetch(quota, branch.request);
  eq('F5 ' + branch.name + ' survives a quota rejection', respState(quotaRun), 'fulfilled');
  eq('F5 ' + branch.name + ' contains the quota failure', writeState(quotaRun), 'fulfilled');
  eq('F5 ' + branch.name + ' reports the quota failure', quota.self.ppSwState.writes.failed, 1);
  var afterQuota = runFetch(quota, branch.request);
  eq('F5 ' + branch.name + ' remains usable after a quota failure',
     respState(afterQuota), 'fulfilled');

  // Non-cacheable response: nothing is scheduled at all.
  var bad = makeWorker({ route: function (url) {
    return { response: typed(url, { status: 404, ok: false }) };
  } });
  var badRun = runFetch(bad, branch.request);
  eq('F6 ' + branch.name + ' schedules no write for an uncacheable response', badRun.event.waits.length, 0);
  eq('F6 ' + branch.name + ' counts the skip', bad.self.ppSwState.writes.skipped, 1);
  eq('F6 ' + branch.name + ' still returns the response', respState(badRun), 'fulfilled');
  eq('F6 ' + branch.name + ' leaves the caches empty', storedKeys(bad), []);
});

// Cache-first branches must not schedule a write when the cache already answers.
[
  { name: 'mp3', request: get(ORIGIN + '/audio/ab12ef34.mp3'), cache: 'popolsku-audio', key: ORIGIN + '/audio/ab12ef34.mp3' },
  { name: 'static asset', request: get(ORIGIN + '/pp-answer.js'), cache: 'popolsku-v59', key: ORIGIN + '/pp-answer.js' }
].forEach(function (branch) {
  var seed = {};
  seed[branch.cache] = {};
  seed[branch.cache][branch.key] = seeded(branch.key, 'warm');
  var worker = makeWorker({ seed: seed });
  var run = runFetch(worker, branch.request);
  eq('F7 a warm ' + branch.name + ' is served from cache', respLabel(run), 'warm');
  eq('F7 a warm ' + branch.name + ' schedules no write', run.event.waits.length, 0);
  eq('F7 a warm ' + branch.name + ' makes no network request', worker.fetch.calls, []);
});

// Every runtime write goes through the shared helper, bound to the event.
(function () {
  var worker = makeWorker();
  var events = WRITE_BRANCHES.map(function (branch) { return runFetch(worker, branch.request); });
  eq('F8 every runtime branch bound its write to its own fetch event',
     events.map(function (r) { return r.event.waits.length; }),
     WRITE_BRANCHES.map(function () { return 1; }));
  eq('F8 every write succeeded',
     [worker.self.ppSwState.writes.scheduled, worker.self.ppSwState.writes.succeeded],
     [WRITE_BRANCHES.length, WRITE_BRANCHES.length]);
  eq('F8 writes landed in exactly the two application caches',
     worker.caches.names.slice().sort(), ['popolsku-audio', 'popolsku-v59']);
  ok('F8 the source has no unbound cache write',
     SW_CODE.indexOf('.then(c => c.put(') === -1 && countOf(SW_CODE, 'cache.put(') === 3);
  eq('F8 waitUntil is only reached through the shared keepAlive helper',
     [countOf(SW_CODE, 'waitUntil('), countOf(SW_CODE, 'event.waitUntil('),
      countOf(SW_CODE, 'e.waitUntil(')], [3, 1, 2]);
  eq('F8 there is exactly one runtime write helper', countOf(SW_CODE, 'function cacheWrite('), 1);
})();

// The helper itself, exercised directly.
(function () {
  var worker = makeWorker();
  var event = new FetchEvent(get(ORIGIN + '/pp-answer.js'));
  var response = typed(ORIGIN + '/pp-answer.js', { label: 'direct' });
  var scheduled = worker.api.cacheWrite(event, 'popolsku-v59', ORIGIN + '/pp-answer.js', response);
  eq('F9 a cacheable response schedules a write', scheduled, true);
  eq('F9 the write is bound to the event', event.waits.length, 1);
  eq('F9 the source response body is left alone', response.bodyUsed, false);
  eq('F9 exactly one clone was taken', response.cloneCount, 1);
  drain();
  eq('F9 the write landed', inv(worker, 'popolsku-v59'), [ORIGIN + '/pp-answer.js']);

  var event2 = new FetchEvent(get(ORIGIN + '/pp-answer.js'));
  eq('F9 a null key schedules nothing',
     worker.api.cacheWrite(event2, 'popolsku-v59', null, typed(ORIGIN + '/pp-answer.js')), false);
  eq('F9 an uncacheable response schedules nothing',
     worker.api.cacheWrite(event2, 'popolsku-v59', ORIGIN + '/x', typed(ORIGIN + '/x', { status: 404, ok: false })), false);
  eq('F9 neither attempt touched the event', event2.waits.length, 0);

  // An event that can no longer be extended must not break the response path.
  var hostile = { waitUntil: function () { throw new Error('InvalidStateError'); } };
  var late = worker.api.cacheWrite(hostile, 'popolsku-v59', ORIGIN + '/pp-usage.js', typed(ORIGIN + '/pp-usage.js'));
  drain();
  eq('F9 a rejected waitUntil is contained', late, true);
  ok('F9 the write still completed',
     inv(worker, 'popolsku-v59').indexOf(ORIGIN + '/pp-usage.js') !== -1);
})();

// =========================================================================
// H. Category-aware media-type validation
//
// A 200 is not proof. A captive portal, a rewrite rule or a host that answers
// every unknown path with the SPA shell returns a healthy 200 text/html, and
// storing that under data-a1.js or an MP3 key poisons the offline app for a
// whole cache generation.
// =========================================================================
eq('H1 the accepted media types are the ones this deployment serves', API.MEDIA_GROUPS, {
  document: ['text/html'],
  script: ['text/javascript', 'application/javascript'],
  json: ['application/json'],
  manifest: ['application/manifest+json', 'application/json'],
  audio: ['audio/mpeg'],
  svg: ['image/svg+xml'],
  png: ['image/png'],
  font: ['font/woff2']
});

// Every key the worker can ever write must map to a media group: fail closed.
(function () {
  var keys = API.REQUIRED_ASSETS.concat(API.OPTIONAL_ASSETS).map(function (a) {
    return API.canonicalKeyFor(API.parseUrl(a, ORIGIN + '/sw.js'));
  });
  var untyped = keys.filter(function (k) {
    return API.mediaGroupForPath(k.slice(ORIGIN.length)) === null;
  });
  eq('H2 every precache entry has a media rule', untyped, []);
  var staticUntyped = API.STATIC_ASSET_PATHS.filter(function (path) {
    return API.mediaGroupForPath(path) === null;
  });
  eq('H2 every runtime static asset has a media rule', staticUntyped, []);
})();

[
  ['/', 'document'], ['/guide/', 'document'], ['/grammar/biernik-accusative/', 'document'],
  ['/pp-answer.js', 'script'], ['/data-a1.js', 'script'],
  ['/audio-manifest.json', 'json'],
  ['/manifest.json', 'manifest'],
  ['/audio/ab12ef34.mp3', 'audio'],
  ['/favicon.svg', 'svg'],
  ['/icon-192.png', 'png'], ['/apple-touch-icon.png', 'png'], ['/og-image.png', 'png'],
  ['/fonts/plus-jakarta-sans-v12-latin-regular.woff2', 'font'],
  ['/sitemap.xml', null], ['/robots.txt', null], ['/unknown', null], ['', null]
].forEach(function (row) {
  eq('H3 media group for ' + JSON.stringify(row[0]), API.mediaGroupForPath(row[0]), row[1]);
});
eq('H3 a non-string path has no media group',
   [API.mediaGroupForPath(null), API.mediaGroupForPath(undefined), API.mediaGroupForPath(7)],
   [null, null, null]);

// Content-Type parsing: parameters stripped, case folded, absence reported.
[
  ['text/html', 'text/html'],
  ['text/html; charset=utf-8', 'text/html'],
  ['TEXT/HTML; CHARSET=UTF-8', 'text/html'],
  ['  Text/JavaScript ; charset=UTF-8  ', 'text/javascript'],
  ['application/manifest+json', 'application/manifest+json'],
  ['audio/mpeg;', 'audio/mpeg'],
  ['', null],
  [null, null]
].forEach(function (row) {
  eq('H4 media type parsed from ' + JSON.stringify(row[0]),
     API.mediaTypeOf(new FakeResponse(row[0] === null ? {} : { headers: { 'Content-Type': row[0] } })),
     row[1]);
});
eq('H4 a response without headers has no media type', API.mediaTypeOf({ status: 200 }), null);

// The correct type for every category is accepted.
[
  ['HTML document', ORIGIN + '/', 'text/html'],
  ['HTML document with charset', ORIGIN + '/', 'text/html; charset=utf-8'],
  ['generated page', ORIGIN + '/guide/listening/', 'text/html'],
  ['helper script', ORIGIN + '/pp-answer.js', 'text/javascript'],
  ['helper script, legacy spelling', ORIGIN + '/pp-answer.js', 'application/javascript'],
  ['data file', ORIGIN + '/data-grammar.js', 'text/javascript; charset=utf-8'],
  ['audio manifest', ORIGIN + '/audio-manifest.json', 'application/json'],
  ['web app manifest, registered type', ORIGIN + '/manifest.json', 'application/manifest+json'],
  ['web app manifest, static-host type', ORIGIN + '/manifest.json', 'application/json'],
  ['MP3', ORIGIN + '/audio/ab12ef34.mp3', 'audio/mpeg'],
  ['SVG', ORIGIN + '/favicon.svg', 'image/svg+xml'],
  ['PNG', ORIGIN + '/icon-512.png', 'image/png'],
  ['WOFF2', ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-600.woff2', 'font/woff2']
].forEach(function (row) {
  ok('H5 correct ' + row[0] + ' is cacheable',
     API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': row[2] } }), row[1]));
});

// 200 text/html under every non-HTML key, and JSON under binary/script keys.
var MISMATCH_KEYS = [
  ['a JavaScript key', ORIGIN + '/pp-answer.js'],
  ['a data-file key', ORIGIN + '/data-a1.js'],
  ['audio-manifest.json', ORIGIN + '/audio-manifest.json'],
  ['manifest.json', ORIGIN + '/manifest.json'],
  ['an MP3 key', ORIGIN + '/audio/ab12ef34.mp3'],
  ['an icon key', ORIGIN + '/icon-192.png'],
  ['an SVG key', ORIGIN + '/favicon.svg'],
  ['a font key', ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-500.woff2']
];
MISMATCH_KEYS.forEach(function (row) {
  ok('H6 a 200 text/html body is never cached under ' + row[0],
     !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'text/html' } }), row[1]));
  ok('H6 a 200 text/html; charset body is never cached under ' + row[0],
     !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'text/html; charset=utf-8' } }), row[1]));
});
[
  ['an MP3 key', ORIGIN + '/audio/ab12ef34.mp3'],
  ['a JavaScript key', ORIGIN + '/pp-answer.js'],
  ['a data-file key', ORIGIN + '/data-a1.js'],
  ['an icon key', ORIGIN + '/icon-512.png'],
  ['a font key', ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-700.woff2']
].forEach(function (row) {
  ok('H7 a 200 application/json body is never cached under ' + row[0],
     !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'application/json' } }), row[1]));
});
ok('H7 JavaScript is not cached under the audio manifest key',
   !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'text/javascript' } }),
                            ORIGIN + '/audio-manifest.json'));
ok('H7 an MP3 body is not cached under the shell key',
   !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'audio/mpeg' } }), ORIGIN + '/'));
ok('H7 a PNG body is not cached under the SVG key',
   !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'image/png' } }),
                            ORIGIN + '/favicon.svg'));
ok('H7 an SVG body is not cached under a PNG key',
   !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'image/svg+xml' } }),
                            ORIGIN + '/icon-192.png'));
ok('H7 a font body is not cached under a script key',
   !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'font/woff2' } }),
                            ORIGIN + '/pp-usage.js'));

// Documented policy: no Content-Type at all is not cacheable, anywhere.
MISMATCH_KEYS.concat([['the root shell', ORIGIN + '/']]).forEach(function (row) {
  ok('H8 a response with no Content-Type is not cached under ' + row[0],
     !API.isCacheableResponse(new FakeResponse({}), row[1]));
  ok('H8 an empty Content-Type is not cached under ' + row[0],
     !API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': '   ' } }), row[1]));
});
eq('H8 a key outside this origin has no media rule and is not cacheable',
   API.isCacheableResponse(new FakeResponse({ headers: { 'Content-Type': 'text/javascript' } }),
                           'https://example.com/pp-answer.js'), false);

// Required precache: wrong type fails the install and discards the new cache.
[
  ['HTML under a required script', ORIGIN + '/pp-answer.js', 'text/html'],
  ['HTML under the audio manifest', ORIGIN + '/audio-manifest.json', 'text/html'],
  ['JSON under a required data file', ORIGIN + '/data-verbs.js', 'application/json'],
  ['plain text under the shell', ORIGIN + '/', 'text/plain'],
  ['no type under a required script', ORIGIN + '/pp-migrate.js', null]
].forEach(function (row) {
  var worker = makeWorker({
    seed: { 'popolsku-v55': { 'https://popolsku.app/': seeded('https://popolsku.app/', 'v55-shell') } },
    route: function (url) {
      if (url !== row[1]) return defaultRoute(url);
      return { response: new FakeResponse(row[2] === null ? { url: url }
                                          : { url: url, headers: { 'Content-Type': row[2] } }) };
    }
  });
  var run = runInstall(worker);
  eq('H9 ' + row[0] + ' fails the install', run.results[0].state, 'rejected');
  ok('H9 ' + row[0] + ' discards the incomplete new cache', !worker.caches.caches[SHELL]);
  ok('H9 ' + row[0] + ' leaves the active shell cache intact', !!worker.caches.caches['popolsku-v55']);
  ok('H9 ' + row[0] + ' reports the content type in the failure',
     worker.self.ppSwState.installFailures.some(function (m) { return /content-type/.test(String(m)); }));
});

// Optional precache: wrong type is skipped, the required shell still installs.
(function () {
  var wrong = ORIGIN + '/favicon.svg';
  var worker = makeWorker({ route: function (url) {
    return url === wrong ? { response: new FakeResponse({ url: url, headers: { 'Content-Type': 'text/html' } }) }
                         : defaultRoute(url);
  } });
  var run = runInstall(worker);
  eq('H10 a wrong-type optional asset does not fail the install', run.results[0].state, 'fulfilled');
  ok('H10 the wrong-type optional asset is not cached', invList(worker, SHELL).indexOf(wrong) === -1);
  eq('H10 the required shell is complete', worker.self.ppSwState.requiredCached, 13);
  eq('H10 the skip is observable', worker.self.ppSwState.optionalFailed, ['./favicon.svg']);
  eq('H10 nothing was discarded', worker.caches.deleted, []);
})();

// Runtime: a wrong-type response is returned to the page but never persisted.
[
  { name: 'data file', request: get(ORIGIN + '/data-a1.js'), type: 'text/html' },
  { name: 'audio manifest', request: get(ORIGIN + '/audio-manifest.json'), type: 'text/html' },
  { name: 'static script', request: get(ORIGIN + '/pp-answer.js'), type: 'text/html' },
  { name: 'web app manifest', request: get(ORIGIN + '/manifest.json'), type: 'text/html' },
  { name: 'icon', request: get(ORIGIN + '/icon-192.png'), type: 'text/html' },
  { name: 'font', request: get(ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-800.woff2'), type: 'text/html' },
  { name: 'navigation', request: nav(ORIGIN + '/'), type: 'application/json' },
  { name: 'mp3 answered with HTML', request: get(ORIGIN + '/audio/ab12ef34.mp3'), type: 'text/html' },
  { name: 'mp3 answered with JSON', request: get(ORIGIN + '/audio/ab12ef34.mp3'), type: 'application/json' },
  { name: 'mp3 answered with no type', request: get(ORIGIN + '/audio/ab12ef34.mp3'), type: null }
].forEach(function (branch) {
  var worker = makeWorker({ route: function (url) {
    return { response: new FakeResponse(branch.type === null ? { url: url, label: 'wrong' }
                                        : { url: url, label: 'wrong', headers: { 'Content-Type': branch.type } }) };
  } });
  var run = runFetch(worker, branch.request);
  eq('H11 ' + branch.name + ' still returns the online response', respState(run), 'fulfilled');
  eq('H11 ' + branch.name + ' returns exactly what the network sent', respLabel(run), 'wrong');
  eq('H11 ' + branch.name + ' persists nothing', storedKeys(worker), []);
  eq('H11 ' + branch.name + ' schedules no write', run.event.waits.length, 0);
  eq('H11 ' + branch.name + ' counts the skip', worker.self.ppSwState.writes.skipped, 1);
});

// The persistent audio cache is the one cache a version bump never clears, so a
// poisoned entry there would outlive every future release. That splits into three
// separate claims, proven separately: a wrong-MIME response is never WRITTEN
// (H12a), an inherited wrong-MIME entry is never SERVED (H12b), and it is
// repaired or evicted rather than left in place (H12c).
(function () {
  // H12a - prevention: nothing wrong-typed is written in the first place.
  var worker = makeWorker({ route: function (url) {
    return { response: new FakeResponse({ url: url, label: 'not-audio',
                                          headers: { 'Content-Type': 'text/html' } }) };
  } });
  runFetch(worker, get(ORIGIN + '/audio/000311d1288f.mp3'));
  runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3'));
  eq('H12a a wrong media type is never written to the persistent audio cache',
     invList(worker, AUDIO), []);
  eq('H12a no other cache absorbed it either', storedKeys(worker), []);
  var good = makeWorker();
  runFetch(good, get(ORIGIN + '/audio/000311d1288f.mp3'));
  eq('H12a a correct audio/mpeg response is still cached',
     invList(good, AUDIO), [ORIGIN + '/audio/000311d1288f.mp3']);

  // H12b - inherited poison is never served, even offline where the alternative
  // is failing the request.
  var clip = ORIGIN + '/audio/ab12ef34.mp3';
  var poisoned = {};
  poisoned[clip] = new FakeResponse({ url: clip, label: 'captive-portal',
                                      headers: { 'Content-Type': 'text/html' } });
  var offline = makeWorker({ seed: { 'popolsku-audio': poisoned },
                             route: function () { return { reject: new TypeError('offline') }; } });
  var offlineRun = runFetch(offline, get(clip));
  ok('H12b an inherited wrong-MIME clip is never served offline', respLabel(offlineRun) !== 'captive-portal');

  // H12c - and it is removed, so the next online request can repair it.
  eq('H12c the inherited entry is evicted', invList(offline, AUDIO), []);
  eq('H12c the eviction is recorded',
     [offline.self.ppSwState.reads.invalid, offline.self.ppSwState.reads.evicted], [1, 1]);
  var repaired = {};
  repaired[clip] = new FakeResponse({ url: clip, label: 'captive-portal',
                                      headers: { 'Content-Type': 'text/html' } });
  var online = makeWorker({ seed: { 'popolsku-audio': repaired } });
  var onlineRun = runFetch(online, get(clip));
  eq('H12c an online request repairs the entry', invList(online, AUDIO), [clip]);
  eq('H12c the repaired entry is the network audio', entryLabel(online, AUDIO, clip),
     respLabel(onlineRun));
  eq('H12c the repaired entry has the right media type',
     entry(online, AUDIO, clip).headers.get('content-type'), 'audio/mpeg');
})();

// =========================================================================
// I. Named-cache read isolation
//
// caches.match(key) with no cacheName searches every cache on the origin in
// creation order. An older cache, an unrelated tool's cache or a stale audio
// entry could therefore answer an app request. Every application read names its
// cache.
// =========================================================================
ok('I1 the source never performs an unnamed CacheStorage read',
   SW_CODE.indexOf('caches.match(') === -1);
eq('I1 there is exactly one named read helper', countOf(SW_CODE, 'function cacheMatch('), 1);
// One definition plus four call sites: the navigation exact key, the navigation
// root fallback, the shared cache-first read (static + MP3) and the Range read.
eq('I1 every application read goes through it', countOf(SW_CODE, 'cacheMatch('), 4);

// 1-3: an unrelated cache created FIRST holding the same key must never win.
[
  { name: 'root shell key', seedKey: ORIGIN + '/', request: nav(ORIGIN + '/'),
    ownCache: 'popolsku-v59' },
  { name: 'static asset key', seedKey: ORIGIN + '/pp-answer.js', request: get(ORIGIN + '/pp-answer.js'),
    ownCache: 'popolsku-v59' },
  { name: 'MP3 key', seedKey: ORIGIN + '/audio/ab12ef34.mp3', request: get(ORIGIN + '/audio/ab12ef34.mp3'),
    ownCache: 'popolsku-audio' }
].forEach(function (row) {
  var seed = { 'unrelated-tool-cache': {} };
  seed['unrelated-tool-cache'][row.seedKey] = seeded(row.seedKey, 'intruder');
  seed[row.ownCache] = {};
  seed[row.ownCache][row.seedKey] = seeded(row.seedKey, 'ours');
  var worker = makeWorker({ seed: seed, route: function () { return { reject: new TypeError('offline') }; } });
  eq('I2 the unrelated cache was created first for the ' + row.name,
     worker.caches.names[0], 'unrelated-tool-cache');
  var run = runFetch(worker, row.request);
  eq('I2 the ' + row.name + ' is answered from ' + row.ownCache, respLabel(run), 'ours');
  eq('I2 the ' + row.name + ' never used a global cache lookup', worker.caches.globalMatches, 0);
});

// 4: only an unrelated cache holds the key -> the app must miss, not borrow.
[
  { name: 'navigation', request: nav(ORIGIN + '/'), key: ORIGIN + '/' },
  { name: 'static asset', request: get(ORIGIN + '/pp-answer.js'), key: ORIGIN + '/pp-answer.js' },
  { name: 'data file', request: get(ORIGIN + '/data-a1.js'), key: ORIGIN + '/data-a1.js' },
  { name: 'audio manifest', request: get(ORIGIN + '/audio-manifest.json'), key: ORIGIN + '/audio-manifest.json' },
  { name: 'mp3', request: get(ORIGIN + '/audio/ab12ef34.mp3'), key: ORIGIN + '/audio/ab12ef34.mp3' }
].forEach(function (row) {
  var seed = { 'unrelated-tool-cache': {} };
  seed['unrelated-tool-cache'][row.key] = seeded(row.key, 'intruder');
  var worker = makeWorker({ seed: seed, route: function () { return { reject: new TypeError('offline') }; } });
  var run = runFetch(worker, row.request);
  ok('I3 an entry only in an unrelated cache never satisfies the ' + row.name,
     respLabel(run) !== 'intruder');
  eq('I3 the ' + row.name + ' made no global cache lookup', worker.caches.globalMatches, 0);
});

// 5: the shell cache and the audio cache holding the same key must not cross.
(function () {
  var shared = ORIGIN + '/audio/ab12ef34.mp3';
  var shellSide = ORIGIN + '/pp-usage.js';
  var seed = { 'popolsku-v59': {}, 'popolsku-audio': {} };
  seed['popolsku-v59'][shared] = seeded(shared, 'shell-copy');
  seed['popolsku-v59'][shellSide] = seeded(shellSide, 'shell-script');
  seed['popolsku-audio'][shared] = seeded(shared, 'audio-copy');
  seed['popolsku-audio'][shellSide] = seeded(shellSide, 'audio-script');
  var worker = makeWorker({ seed: seed, route: function () { return { reject: new TypeError('offline') }; } });
  eq('I4 an MP3 request reads the audio cache, not the shell cache',
     respLabel(runFetch(worker, get(shared))), 'audio-copy');
  eq('I4 a static request reads the shell cache, not the audio cache',
     respLabel(runFetch(worker, get(shellSide))), 'shell-script');
  eq('I4 neither used a global cache lookup', worker.caches.globalMatches, 0);
})();

// 6: a Range request for a warm clip also reads only the audio cache.
(function () {
  var clip = ORIGIN + '/audio/ab12ef34.mp3';
  var seed = { 'unrelated-tool-cache': {}, 'popolsku-v59': {}, 'popolsku-audio': {} };
  seed['unrelated-tool-cache'][clip] = seeded(clip, 'intruder');
  seed['popolsku-v59'][clip] = seeded(clip, 'shell-copy');
  seed['popolsku-audio'][clip] = seeded(clip, 'audio-copy');
  var worker = makeWorker({ seed: seed, route: function () { return { reject: new TypeError('offline') }; } });
  var run = runFetch(worker, get(clip, { headers: { Range: 'bytes=0-' } }));
  eq('I5 a Range request for a warm clip reads only the audio cache',
     [respState(run), respValue(run) ? respValue(run).status : 'no-response'], ['fulfilled', 206]);
  eq('I5 the Range read made no global cache lookup', worker.caches.globalMatches, 0);
  eq('I5 the Range request still wrote nothing', worker.self.ppSwState.writes.scheduled, 0);
})();

// 7: a failing named read is contained by the existing strategy.
(function () {
  var openFail = makeWorker({
    seed: { 'popolsku-v59': {} },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  openFail.caches.openBehavior = function (name) {
    return name === SHELL ? { reject: new Error('cache open blocked') } : null;
  };
  var offlineNav = runFetch(openFail, nav(ORIGIN + '/'));
  eq('I6 a rejected cache.open during an offline read is contained',
     offlineNav.responses.length, 1);
  ok('I6 the response settles instead of hanging', respState(offlineNav) !== 'pending');
  ok('I6 the failure is logged',
     openFail.warnings.some(function (w) { return /cache read failed/.test(w); }));

  var matchFail = makeWorker({
    seed: { 'popolsku-audio': { 'https://popolsku.app/audio/ab12ef34.mp3': seeded('https://popolsku.app/audio/ab12ef34.mp3', 'warm') } },
    route: function (url) { return defaultRoute(url); }
  });
  matchFail.caches.matchBehavior = function () { return { reject: new Error('match blocked') }; };
  var run = runFetch(matchFail, get(ORIGIN + '/audio/ab12ef34.mp3'));
  eq('I6 a rejected cache.match falls through to the network', respState(run), 'fulfilled');
  eq('I6 the network answered', matchFail.fetch.calls.length, 1);
  ok('I6 the read failure is logged',
     matchFail.warnings.some(function (w) { return /cache read failed/.test(w); }));
})();

// A whole session across every branch must never touch the unnamed lookup.
(function () {
  var worker = makeWorker();
  WRITE_BRANCHES.forEach(function (branch) { runFetch(worker, branch.request); });
  runFetch(worker, get(ORIGIN + '/audio/ab12ef34.mp3', { headers: { Range: 'bytes=0-' } }));
  runFetch(worker, get(ORIGIN + '/sitemap.xml'));
  eq('I7 no branch ever used the unnamed CacheStorage lookup', worker.caches.globalMatches, 0);
  eq('I7 writes still landed in exactly the two application caches',
     worker.caches.names.slice().sort(), ['popolsku-audio', 'popolsku-v59']);
})();

// =========================================================================
// J. Validated cache hits, eviction and audio-cache migration
//
// Writing correctly is only half the contract. popolsku-audio is deliberately
// versionless and survives every deploy, so it can still hold entries written by
// the v55 worker, which had no media-type gate. A shell cache can inherit the
// same way within a release. Every named read is therefore held to the same
// standard as a write, and an entry that fails it is evicted rather than served.
// =========================================================================
var CLIP = ORIGIN + '/audio/ab12ef34.mp3';
var CLIP2 = ORIGIN + '/audio/000311d1288f.mp3';

function audioSeed(response) { var o = {}; o[CLIP] = response; return { 'popolsku-audio': o }; }
function shellSeed(key, response) { var o = {}; o[key] = response; return { 'popolsku-v59': o }; }
function inherited(key, type, label) {
  var opts = { url: key, label: label || 'inherited' };
  if (type !== null) opts.headers = { 'Content-Type': type };
  return new FakeResponse(opts);
}

// 1. A valid inherited clip is still a plain cache hit: untouched, no network.
(function () {
  var worker = makeWorker({ seed: audioSeed(seeded(CLIP, 'warm-clip')) });
  var run = runFetch(worker, get(CLIP));
  eq('J1 a valid cached MP3 is served from the audio cache', respLabel(run), 'warm-clip');
  eq('J1 it costs no network request', worker.fetch.calls, []);
  eq('J1 it is not deleted', invList(worker, AUDIO), [CLIP]);
  eq('J1 it is not rewritten', worker.self.ppSwState.writes.scheduled, 0);
  eq('J1 the entry object is unchanged', entryLabel(worker, AUDIO, CLIP), 'warm-clip');
  eq('J1 nothing is recorded as invalid',
     [worker.self.ppSwState.reads.invalid, worker.self.ppSwState.reads.evicted], [0, 0]);
  eq('J1 the served body was never consumed', respValue(run).bodyUsed, false);
})();

// 2-5. Every shape of invalid inherited clip: never served, always evicted.
[
  ['a 200 text/html body', inherited(CLIP, 'text/html', 'login-page')],
  ['a 200 application/json body', inherited(CLIP, 'application/json', 'error-json')],
  ['no Content-Type at all', inherited(CLIP, null, 'typeless')],
  ['an empty Content-Type', inherited(CLIP, '   ', 'blank-type')],
  ['a status 206 partial', new FakeResponse({ url: CLIP, status: 206, label: 'partial',
                                              headers: { 'Content-Type': 'audio/mpeg' } })],
  ['a status 404 body', new FakeResponse({ url: CLIP, status: 404, ok: false, label: 'not-found',
                                           headers: { 'Content-Type': 'audio/mpeg' } })],
  ['a redirected response', new FakeResponse({ url: CLIP, redirected: true, label: 'redirected',
                                               headers: { 'Content-Type': 'audio/mpeg' } })],
  ['an opaque response', new FakeResponse({ url: CLIP, type: 'opaque', status: 0, ok: false,
                                            label: 'opaque' })],
  ['a text/plain body', inherited(CLIP, 'text/plain', 'plain')]
].forEach(function (row) {
  // Online: rejected, deleted, and replaced by the real clip on the way back.
  var worker = makeWorker({ seed: audioSeed(row[1]) });
  var run = runFetch(worker, get(CLIP));
  ok('J2 an inherited clip with ' + row[0] + ' is never served',
     respLabel(run) !== row[1].label);
  ok('J2 the inherited entry no longer occupies the key for ' + row[0],
     entryLabel(worker, AUDIO, CLIP) !== row[1].label);
  ok('J2 a delete was issued for that exact key for ' + row[0],
     worker.caches.caches[AUDIO].deletes.indexOf(CLIP) !== -1);
  eq('J2 the eviction is counted for ' + row[0],
     [worker.self.ppSwState.reads.invalid, worker.self.ppSwState.reads.evicted,
      worker.self.ppSwState.reads.evictionFailed], [1, 1, 0]);
  eq('J2 the network was asked instead for ' + row[0], worker.fetch.calls.length, 1);
  eq('J2 what ends up cached is valid audio for ' + row[0],
     entry(worker, AUDIO, CLIP).headers.get('content-type'), 'audio/mpeg');
  eq('J2 the eviction is described without a body for ' + row[0],
     Object.keys(worker.self.ppSwState.invalidReads[0]).sort(), ['cache', 'key', 'reason']);
  eq('J2 the eviction names the audio cache for ' + row[0],
     worker.self.ppSwState.invalidReads[0].cache, AUDIO);
  ok('J2 the eviction is logged for ' + row[0],
     worker.warnings.some(function (w) { return /evicting invalid cache entry/.test(w); }));

  // Offline: rejected and deleted, with nothing to put back.
  var away = makeWorker({ seed: audioSeed(row[1]),
                          route: function () { return { reject: new TypeError('offline') }; } });
  var awayRun = runFetch(away, get(CLIP));
  ok('J2 offline, an inherited clip with ' + row[0] + ' is still not served',
     respLabel(awayRun) !== row[1].label);
  eq('J2 offline, the entry is removed from popolsku-audio for ' + row[0],
     invList(away, AUDIO), []);
  eq('J2 offline, nothing is written back for ' + row[0], away.self.ppSwState.writes.scheduled, 0);
});

// 6-7. Online: the invalid entry is replaced by a real clip.
(function () {
  var worker = makeWorker({ seed: audioSeed(inherited(CLIP, 'text/html', 'login-page')) });
  var run = runFetch(worker, get(CLIP));
  eq('J3 the online response is returned', respState(run), 'fulfilled');
  eq('J3 the served clip is the network one, not the inherited one',
     respValue(run).headers.get('content-type'), 'audio/mpeg');
  eq('J3 the repaired cache holds exactly one entry', invList(worker, AUDIO), [CLIP]);
  eq('J3 the repaired entry is the valid audio response',
     entry(worker, AUDIO, CLIP).headers.get('content-type'), 'audio/mpeg');
  eq('J3 the repair went through the shared write contract',
     [worker.self.ppSwState.writes.scheduled, worker.self.ppSwState.writes.succeeded], [1, 1]);
  eq('J3 the repair write was bound to the fetch event', run.event.waits.length, 1);
  eq('J3 the delete happened before the repair write',
     worker.caches.caches[AUDIO].deletes.length, 1);
  // A second request now finds a valid entry and stops touching the network.
  var again = runFetch(worker, get(CLIP));
  eq('J3 the repaired entry is a plain hit next time', worker.fetch.calls.length, 1);
  eq('J3 and it is served', respValue(again).headers.get('content-type'), 'audio/mpeg');
})();

// 8. Offline: the invalid entry is still not served, and the request fails normally.
(function () {
  var worker = makeWorker({ seed: audioSeed(inherited(CLIP, 'text/html', 'login-page')),
                            route: function () { return { reject: new TypeError('offline') }; } });
  var run = runFetch(worker, get(CLIP));
  ok('J4 an invalid entry is not served offline', respLabel(run) !== 'login-page');
  eq('J4 the request follows the existing offline failure path', respState(run), 'rejected');
  eq('J4 the invalid entry is still evicted', invList(worker, AUDIO), []);
  eq('J4 nothing was written', worker.self.ppSwState.writes.scheduled, 0);
})();

// 9-10. Deletion failure: contained, and the invalid entry is still not served.
[
  ['cache.delete rejects', function () { return { reject: new Error('delete blocked') }; }, 'evictionFailed'],
  ['cache.delete reports no match', function () { return { miss: true }; }, 'evictionFailed']
].forEach(function (row) {
  var worker = makeWorker({ seed: audioSeed(inherited(CLIP, 'text/html', 'login-page')) });
  worker.caches.entryDeleteBehavior = row[1];
  var run = runFetch(worker, get(CLIP));
  ok('J5 ' + row[0] + ': the invalid entry is still not served', respLabel(run) !== 'login-page');
  eq('J5 ' + row[0] + ': the online response still succeeds', respState(run), 'fulfilled');
  eq('J5 ' + row[0] + ': the failure is recorded',
     [worker.self.ppSwState.reads.invalid, worker.self.ppSwState.reads.evicted,
      worker.self.ppSwState.reads[row[2]]], [1, 0, 1]);
  ok('J5 ' + row[0] + ': the failure is logged',
     worker.warnings.some(function (w) { return /evict|not removed/.test(w); }));
  eq('J5 ' + row[0] + ': the network was still asked', worker.fetch.calls.length, 1);
});
(function () {
  var worker = makeWorker({ seed: audioSeed(inherited(CLIP, 'text/html', 'login-page')),
                            route: function () { return { reject: new TypeError('offline') }; } });
  worker.caches.entryDeleteBehavior = function () { return { reject: new Error('delete blocked') }; };
  var run = runFetch(worker, get(CLIP));
  ok('J5 a failed delete offline still does not serve the invalid entry',
     respLabel(run) !== 'login-page');
  eq('J5 and the read failure is contained, not thrown', respState(run), 'rejected');
})();

// 11-13. Cached Range audio.
(function () {
  var warm = makeWorker({ seed: audioSeed(seeded(CLIP, 'warm-clip')) });
  var warmRun = runFetch(warm, get(CLIP, { headers: { Range: 'bytes=0-' } }));
  eq('J6 a valid cached clip still answers a Range request',
     [respState(warmRun), respValue(warmRun) ? respValue(warmRun).status : 'no-response'],
     ['fulfilled', 206]);
  eq('J6 the valid entry is not evicted', invList(warm, AUDIO), [CLIP]);
  eq('J6 a Range request over a valid hit writes nothing', warm.self.ppSwState.writes.scheduled, 0);

  [
    ['text/html', inherited(CLIP, 'text/html', 'login-page')],
    ['application/json', inherited(CLIP, 'application/json', 'error-json')],
    ['no Content-Type', inherited(CLIP, null, 'typeless')],
    ['status 206', new FakeResponse({ url: CLIP, status: 206, label: 'partial',
                                      headers: { 'Content-Type': 'audio/mpeg' } })]
  ].forEach(function (row) {
    var worker = makeWorker({ seed: audioSeed(row[1]) });
    var run = runFetch(worker, get(CLIP, { headers: { Range: 'bytes=0-99' } }));
    ok('J7 an invalid cached clip (' + row[0] + ') never answers a Range request',
       respLabel(run) !== row[1].label);
    eq('J7 it is evicted (' + row[0] + ')', invList(worker, AUDIO), []);
    eq('J7 the original Range request reaches the network (' + row[0] + ')',
       worker.fetch.calls.length, 1);
    eq('J7 the Range header is preserved on the network request (' + row[0] + ')',
       worker.fetch.calls[0].request.headers.get('range'), 'bytes=0-99');
    eq('J7 no Range response is written (' + row[0] + ')',
       worker.self.ppSwState.writes.scheduled, 0);
    eq('J7 the audio cache stays empty (' + row[0] + ')', invList(worker, AUDIO), []);
  });

  var cold = makeWorker();
  runFetch(cold, get(CLIP2, { headers: { Range: 'bytes=0-' } }));
  eq('J8 an uncached Range request still reaches the network unchanged', cold.fetch.calls.length, 1);
  eq('J8 and still writes nothing', cold.self.ppSwState.writes.scheduled, 0);
})();

// 14-15. The same rule applies to every named application cache, not just audio.
[
  { name: 'root shell', key: ORIGIN + '/', request: nav(ORIGIN + '/'), type: 'application/json' },
  { name: 'generated page', key: ORIGIN + '/guide/', request: nav(ORIGIN + '/guide/'), type: 'audio/mpeg' },
  { name: 'data file', key: ORIGIN + '/data-a1.js', request: get(ORIGIN + '/data-a1.js'), type: 'text/html' },
  { name: 'audio manifest', key: ORIGIN + '/audio-manifest.json', request: get(ORIGIN + '/audio-manifest.json'), type: 'text/html' },
  { name: 'static script', key: ORIGIN + '/pp-answer.js', request: get(ORIGIN + '/pp-answer.js'), type: 'text/html' },
  { name: 'icon', key: ORIGIN + '/icon-192.png', request: get(ORIGIN + '/icon-192.png'), type: 'text/html' },
  { name: 'font', key: ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-500.woff2', request: get(ORIGIN + '/fonts/plus-jakarta-sans-v12-latin-500.woff2'), type: null }
].forEach(function (row) {
  var bad = makeWorker({ seed: shellSeed(row.key, inherited(row.key, row.type, 'inherited-junk')),
                         route: function () { return { reject: new TypeError('offline') }; } });
  var badRun = runFetch(bad, row.request);
  ok('J9 an invalid ' + row.name + ' entry in the shell cache is never served',
     respLabel(badRun) !== 'inherited-junk');
  eq('J9 an invalid ' + row.name + ' entry is evicted', invList(bad, SHELL), []);
  eq('J9 the eviction names the shell cache for ' + row.name,
     bad.self.ppSwState.invalidReads[0].cache, SHELL);

  var good = makeWorker({ seed: shellSeed(row.key, seeded(row.key, 'valid-entry')),
                          route: function () { return { reject: new TypeError('offline') }; } });
  var goodRun = runFetch(good, row.request);
  eq('J10 a valid ' + row.name + ' entry is still served offline', respLabel(goodRun), 'valid-entry');
  eq('J10 a valid ' + row.name + ' entry is not evicted', invList(good, SHELL), [row.key]);
  eq('J10 nothing is recorded as invalid for ' + row.name, good.self.ppSwState.reads.invalid, 0);
});

// Generated fallback no longer reads the root shell at all, so an invalid root
// entry cannot be laundered through it (and is left for validation on a root read).
(function () {
  var worker = makeWorker({
    seed: { 'popolsku-v59': {
      'https://popolsku.app/': inherited(ORIGIN + '/', 'application/json', 'junk-shell'),
      'https://popolsku.app/guide/': seeded(ORIGIN + '/guide/', 'guide')
    } },
    route: function () { return { reject: new TypeError('offline') }; }
  });
  var run = runFetch(worker, nav(ORIGIN + '/grammar/wolacz-vocative/'));
  ok('J11 an invalid root shell is not used as the navigation fallback',
     respLabel(run) !== 'junk-shell');
  eq('J11 generated fallback never reads or mutates the root shell',
     invList(worker, SHELL), [ORIGIN + '/', ORIGIN + '/guide/']);
  eq('J11 the valid generated page survives', entryLabel(worker, SHELL, ORIGIN + '/guide/'), 'guide');
})();

// 16-17. Isolation and the no-global-read boundary survive validation.
(function () {
  var seed = { 'unrelated-tool-cache': {}, 'popolsku-audio': {} };
  seed['unrelated-tool-cache'][CLIP] = seeded(CLIP, 'intruder');
  seed['popolsku-audio'][CLIP] = inherited(CLIP, 'text/html', 'inherited-junk');
  var worker = makeWorker({ seed: seed, route: function () { return { reject: new TypeError('offline') }; } });
  var run = runFetch(worker, get(CLIP));
  ok('J12 eviction never falls back to an unrelated cache', respLabel(run) !== 'intruder');
  ok('J12 and never serves the inherited junk', respLabel(run) !== 'inherited-junk');
  eq('J12 only the named cache entry was evicted', invList(worker, AUDIO), []);
  eq('J12 the unrelated cache is untouched', invList(worker, 'unrelated-tool-cache'), [CLIP]);
  eq('J12 no global cache lookup was used', worker.caches.globalMatches, 0);
  eq('J12 the unrelated cache was never opened',
     worker.caches.opened.filter(function (n) { return n === 'unrelated-tool-cache'; }), []);
})();

eq('J13 validation happens inside the one named-read helper',
   [countOf(SW_CODE, 'function cacheMatch('), countOf(SW_CODE, 'function evictInvalidEntry('),
    countOf(SW_CODE, 'caches.match(')], [1, 1, 0]);
eq('J13 the read gate is the same function as the write gate',
   countOf(SW_CODE, 'isCacheableResponse(hit, key)'), 1);
/* Entry-level deletes live in exactly three single-entry helpers: the invalid-hit
   eviction, the unreadable-clip drop, and the retention/quota deleter - which
   deletes the STORED request, not a canonical string, so a legacy query-bearing
   entry can really be removed. */
eq('J13 entry-level deletes exist only in the three single-entry helpers',
   [countOf(SW_CODE, 'cache.delete(key)'), countOf(SW_CODE, 'cache.delete(entry.request)')], [2, 1]);
/* Whole-cache deletion stays where Phase 4B-1 put it: discarding a failed
   install, and activation cleanup. Retention never clears a cache. */
eq('J13 whole-cache deletion has not spread', countOf(SW_CODE, 'caches.delete('), 2);
(function () {
  /* Phase 4B-3 reads a cached clip's bytes - but only to slice a 206 out of
     them. Validation and eviction still read headers only, which is what keeps
     the learner's response intact whichever way a read goes. */
  var at = SW_CODE.indexOf('function audioRangeResponse(');
  var end = SW_CODE.indexOf('\nfunction ', at + 1);
  var rangeBranch = at === -1 ? '' : SW_CODE.slice(at, end === -1 ? SW_CODE.length : end);
  var elsewhere = SW_CODE.slice(0, at === -1 ? 0 : at) +
                  (end === -1 ? '' : SW_CODE.slice(end));
  ok('J13 validation never reads the body',
     SW_CODE.indexOf('.text()') === -1 && SW_CODE.indexOf('.json()') === -1 &&
     SW_CODE.indexOf('.blob()') === -1 && elsewhere.indexOf('.arrayBuffer()') === -1);
  eq('J13 the only body read is the Range slice',
     [countOf(SW_CODE, '.arrayBuffer()'), countOf(rangeBranch, 'hit.arrayBuffer()')], [1, 1]);
})();
ok('J14 the diagnostics are bounded',
   countOf(SW_CODE, 'SW_STATE.invalidReads.length < 20') === 1 &&
   countOf(SW_CODE, 'SW_STATE.writeFailures.length < 20') === 1);
(function () {
  // 25 invalid reads, only 20 recorded, counters keep counting.
  var worker = makeWorker({ route: function () { return { reject: new TypeError('offline') }; } });
  for (var i = 0; i < 25; i++) {
    var key = ORIGIN + '/audio/' + ('00000000000' + i).slice(-12) + '.mp3';
    var seed = {}; seed[key] = inherited(key, 'text/html', 'junk');
    worker.caches.rawOpen(AUDIO).entries[key] = seed[key];
    worker.caches.rawOpen(AUDIO).order.push(key);
    runFetch(worker, get(key));
  }
  eq('J14 every invalid read is counted', worker.self.ppSwState.reads.invalid, 25);
  eq('J14 the recorded sample is capped', worker.self.ppSwState.invalidReads.length, 20);
  eq('J14 no response body is retained',
     worker.self.ppSwState.invalidReads.every(function (r) {
       return Object.keys(r).length === 3 && typeof r.reason === 'string';
     }), true);
})();

// =========================================================================
// G. Regression boundaries
// =========================================================================
eq('G1 APP_VERSION is the 8.4 release', (INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1], '8.4');
eq('G1 the app-shell cache is the new revision',
   (SW_SRC.match(/CACHE\s*=\s*"([^"]+)"/) || [])[1], 'popolsku-v59');
eq('G1 the audio cache name is unchanged',
   (SW_SRC.match(/AUDIO_CACHE\s*=\s*"([^"]+)"/) || [])[1], 'popolsku-audio');
eq('G1 the storage schema version is unchanged',
   (MIGRATE.match(/SCHEMA_VERSION\s*=\s*(\d+)/) || [])[1], '2');
eq('G1 the content migration revision is unchanged',
   (MIGRATE.match(/CONTENT_MIGRATION_REVISION\s*=\s*(\d+)/) || [])[1], '2');
ok('G2 the web app manifest is untouched',
   MANIFEST.indexOf('"start_url": "./?pwa=1"') !== -1 &&
   MANIFEST.indexOf('"scope": "./"') !== -1 &&
   MANIFEST.indexOf('"display": "standalone"') !== -1 &&
   MANIFEST.indexOf('"id": "./"') !== -1);
eq('G2 the manifest still declares its three icons', countOf(MANIFEST, '"src": "icon'), 3);
ok('G2 index.html still links the manifest and the versioned favicon',
   INDEX.indexOf('<link rel="manifest" href="manifest.json">') !== -1 &&
   INDEX.indexOf('href="favicon.svg?v=17"') !== -1);
ok('G3 the audio contract is unchanged',
   INDEX.indexOf('fetch("audio-manifest.json", { cache: "no-store" })') !== -1 &&
   /data-audio="\/audio\/[a-f0-9]+\.mp3"/.test(GEN_PAGE));
ok('G3 the generated page output is unchanged',
   GEN_PAGE.indexOf('<link rel="canonical" href="https://popolsku.app/grammar/biernik-accusative/">') !== -1 &&
   GEN_PAGE.indexOf('v8.4') !== -1);
ok('G3 build_pages.py still derives the version it always did', countOf(BUILD, 'read_app_version()') === 2);
ok('G4 Phase 3 focus and scroll behaviour is untouched',
   countOf(INDEX, 'function ppRevealFocusedTarget(') === 1 &&
   countOf(INDEX, 'el.scrollIntoView({block:"nearest", inline:"nearest"})') === 1);
ok('G4 Phase 2C routing is untouched',
   INDEX.indexOf('history.pushState') !== -1 && countOf(INDEX, 'hashchange') === 0 &&
   INDEX.indexOf('data-app-screen="privacy"') !== -1);
ok('G4 conversation rendering is untouched',
   countOf(INDEX, 'function cRenderThread(') === 1 && countOf(INDEX, 'function cRenderNode(') === 1 &&
   countOf(INDEX, 'function cThreadBubblesHTML(') === 1);
eq('G5 the worker is the only file that mentions the shell cache revision',
   [countOf(INDEX, 'popolsku-v59'), countOf(MANIFEST, 'popolsku-v59'), countOf(BUILD, 'popolsku-v59')],
   [0, 0, 0]);
ok('G5 no learner-visible copy lives in the worker',
   SW_SRC.indexOf('You are offline') === -1 && SW_SRC.indexOf('Update available') === -1 &&
   SW_SRC.indexOf('innerHTML') === -1 && SW_SRC.indexOf('<html') === -1);
ok('G5 the only strings the worker emits are developer diagnostics',
   countOf(SW_CODE, 'console.warn(') === 1 && countOf(SW_CODE, '[po polsku sw] ') === 1);
ok('G6 the worker keeps the shared helper scripts in its precache inventory',
   countOf(SW_SRC, '"./pp-distractor.js"') === 1 && SW_SRC.indexOf('"./pp-answer.js"') !== -1 &&
   SW_SRC.indexOf('"./pp-usage.js"') !== -1 && SW_SRC.indexOf('"./pp-migrate.js"') !== -1);
eq('G6 the worker never mentions activity internals', countOf(SW_SRC, 'typeItCue'), 0);

console.log('Phase 4B-1 service worker cache tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log(line); });
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
