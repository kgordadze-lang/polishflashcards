// Deterministic Phase 4B-3 tests: audio resilience (MLG-4A-04), the MP3 Range
// contract (MLG-4A-05) and bounded audio retention (MLG-4A-08).
//
//     osascript -l JavaScript tests/test_phase4b3_audio_resilience_range_storage.js
//
// WHAT RUNS HERE IS THE SHIPPING CODE
//   - sw.js is evaluated whole inside a fake worker global and driven with real
//     fetch events, so Range synthesis, 416, eviction, retention and quota
//     recovery are executed rather than described.
//   - the app-shell audio engine and the audio status surface are read OUT OF
//     index.html and run against a fake DOM.
//   - the generated-page runtime is read out of a COMMITTED generated page, so
//     what is tested is what the generator actually emitted.
//   - the 206 slices are compared against the bytes of a real repository MP3.
//
// Promises are a local A+ implementation over a hand-drained queue:
// JavaScriptCore under osascript drains no microtasks until the script ends, so
// a real promise assertion could never be made mid-script. Draining by hand also
// makes "the put rejected, then the retry succeeded" exact instead of timed.
//
// Real browsers, real quota pressure, installed PWAs, VoiceOver/TalkBack and
// physical devices remain human verification.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// Real bytes, not a text approximation: latin-1 maps every byte 0-255 to one
// code unit, so a decoded MP3 round-trips exactly.
function readBytes(path) {
  var data = $.NSData.dataWithContentsOfFile(path);
  if (!data || !data.length) return null;
  var s = ObjC.unwrap($.NSString.alloc.initWithDataEncoding(data, $.NSISOLatin1StringEncoding));
  var out = new Uint8Array(s.length);
  for (var i = 0; i < s.length; i++) out[i] = s.charCodeAt(i) & 255;
  return out;
}
function rootDir() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  return fm.fileExistsAtPath(cwd + '/index.html') ? cwd + '/' : cwd + '/../';
}
var ROOT = rootDir();
var SW_SRC = readFile(ROOT + 'sw.js');
var INDEX = readFile(ROOT + 'index.html');
var BUILD = readFile(ROOT + 'build_pages.py');
var MIGRATE = readFile(ROOT + 'pp-migrate.js');
var GEN_PAGE_PATH = 'grammar/biernik-accusative/index.html';
var GEN_PAGE = readFile(ROOT + GEN_PAGE_PATH);
var CLIP_FILE = 'audio/000311d1288f.mp3';
var CLIP_BYTES = readBytes(ROOT + CLIP_FILE);

var PASS = 0, FAIL = 0, LOG = [], INFO = [];
function ok(name, condition) { if (condition) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : '  (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(source, needle) {
  var count = 0, at = source.indexOf(needle);
  while (at !== -1) { count++; at = source.indexOf(needle, at + needle.length); }
  return count;
}
// Comment-stripped source, so a boundary assertion cannot be satisfied by prose.
function codeOnly(src) {
  var out = '', mode = 'code';
  for (var i = 0; i < src.length; i++) {
    var c = src[i], n = src[i + 1];
    if (mode === 'line') { if (c === '\n') { mode = 'code'; out += c; } continue; }
    if (mode === 'block') { if (c === '*' && n === '/') { mode = 'code'; i++; } continue; }
    if (mode === 'sq' || mode === 'dq' || mode === 'tpl') {
      out += c;
      if (c === '\\') { out += src[++i]; continue; }
      if ((mode === 'sq' && c === "'") || (mode === 'dq' && c === '"') ||
          (mode === 'tpl' && c === '`')) mode = 'code';
      continue;
    }
    if (c === '/' && n === '/') { mode = 'line'; i++; continue; }
    if (c === '/' && n === '*') { mode = 'block'; i++; continue; }
    if (c === "'") mode = 'sq'; else if (c === '"') mode = 'dq'; else if (c === '`') mode = 'tpl';
    out += c;
  }
  return out;
}
var SW_CODE = codeOnly(SW_SRC), INDEX_CODE = codeOnly(INDEX);

ok('H0 the repository clip used for byte comparison was read', !!CLIP_BYTES && CLIP_BYTES.length > 1000);
var CLIP_LEN = CLIP_BYTES ? CLIP_BYTES.length : 0;

// =========================================================================
// Deterministic promises
// =========================================================================
var QUEUE = [];
function schedule(job) { QUEUE.push(job); }
function drain() {
  var guard = 0;
  while (QUEUE.length) { if (++guard > 200000) throw new Error('drain: runaway microtask queue'); QUEUE.shift()(); }
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
function rejectP(p, e) { if (p.state !== 'pending') return; p.state = 'rejected'; p.value = e; flushP(p); }
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
function deferred() { var d = {}; d.promise = new P(function (r, j) { d.resolve = r; d.reject = j; }); return d; }
function watch(promise) {
  var rec = { state: 'pending', value: undefined };
  P.resolve(promise).then(function (v) { rec.state = 'fulfilled'; rec.value = v; },
                          function (e) { rec.state = 'rejected'; rec.value = e; });
  return rec;
}
(function () {
  var order = [], d = deferred();
  P.resolve('a').then(function (v) { order.push(v); });
  d.promise.then(function (v) { order.push(v); });
  eq('H1 nothing runs before the queue is drained', order, []);
  drain(); eq('H1 resolved work runs on drain', order, ['a']);
  d.resolve('b'); drain(); eq('H1 deferred work runs when resolved', order, ['a', 'b']);
  var chained = watch(P.resolve(1).then(function (v) { return P.resolve(v + 1); }));
  drain(); eq('H1 a returned promise is adopted', [chained.state, chained.value], ['fulfilled', 2]);
  var recovered = watch(P.reject(new Error('x'))['catch'](function () { return 'ok'; }));
  drain(); eq('H1 catch recovers', [recovered.state, recovered.value], ['fulfilled', 'ok']);
})();

// =========================================================================
// Fake URL
// =========================================================================
function parseAbsolute(input) {
  var m = /^([a-zA-Z][a-zA-Z0-9+.\-]*):([\s\S]*)$/.exec(input);
  if (!m) return null;
  var protocol = m[1].toLowerCase() + ':', rest = m[2], host = '', path = rest;
  if (rest.slice(0, 2) === '//') {
    var after = rest.slice(2), cut = after.length;
    ['/', '?', '#'].forEach(function (ch) { var at = after.indexOf(ch); if (at !== -1 && at < cut) cut = at; });
    host = after.slice(0, cut); path = after.slice(cut);
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
  this.protocol = parsed.protocol; this.host = parsed.host; this.pathname = parsed.pathname;
  this.search = parsed.search; this.hash = parsed.hash;
  var opaque = (this.protocol !== 'http:' && this.protocol !== 'https:') || this.host === '';
  this.origin = opaque ? 'null' : this.protocol + '//' + this.host;
  this.href = (this.host === '' ? this.protocol : this.protocol + '//' + this.host) +
              this.pathname + this.search + this.hash;
}
eq('H2 the fake URL parser keeps query and path apart',
   [new FakeURL('https://popolsku.app/audio/ab.mp3?v=2').pathname,
    new FakeURL('https://popolsku.app/audio/ab.mp3?v=2').search],
   ['/audio/ab.mp3', '?v=2']);

// =========================================================================
// Fake Headers / Request / Response with real bytes
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
function bytesToBuffer(bytes) {
  var copy = new Uint8Array(bytes.length);
  copy.set(bytes);
  return copy.buffer;
}
function bufferToArray(buffer) {
  var view = new Uint8Array(buffer), out = [];
  for (var i = 0; i < view.length; i++) out.push(view[i]);
  return out;
}
// A compact, comparable description of a byte run: length, the first and last
// four bytes and a checksum. Two different runs of the same length practically
// never agree on all of it, and a failure message stays readable.
function fingerprint(bytes) {
  var sum = 0, head = [], tail = [];
  for (var i = 0; i < bytes.length; i++) sum = (sum + bytes[i] * (i % 7 + 1)) % 1000003;
  for (i = 0; i < Math.min(4, bytes.length); i++) head.push(bytes[i]);
  for (i = Math.max(0, bytes.length - 4); i < bytes.length; i++) tail.push(bytes[i]);
  return [bytes.length, head, tail, sum];
}
function realSlice(start, end) {
  var out = [];
  for (var i = start; i <= end && i < CLIP_LEN; i++) out.push(CLIP_BYTES[i]);
  return out;
}

var RESPONSE_SEQ = 0;
function FakeResponse(opts, init) {
  // Web form - new Response(body, init) - which is how the worker builds a 206
  // or a 416. Anything else is the harness's own option bag.
  if (init !== undefined || opts === null ||
      (opts && typeof ArrayBuffer !== 'undefined' && opts instanceof ArrayBuffer)) {
    var body = opts, cfg = init || {};
    opts = { status: cfg.status, statusText: cfg.statusText, type: 'basic',
             headers: cfg.headers, label: 'synthetic', body: body, synthetic: true };
  }
  opts = opts || {};
  this.id = ++RESPONSE_SEQ;
  this.status = opts.status === undefined ? 200 : opts.status;
  this.statusText = opts.statusText === undefined ? '' : opts.statusText;
  this.ok = opts.ok === undefined ? (this.status >= 200 && this.status < 300) : opts.ok;
  this.type = opts.type === undefined ? 'basic' : opts.type;
  this.redirected = opts.redirected === true;
  this.url = opts.url === undefined ? '' : opts.url;
  this.label = opts.label === undefined ? ('body#' + this.id) : opts.label;
  this.headers = new FakeHeaders(opts.headers);
  this.synthetic = opts.synthetic === true;
  this.bodyUsed = false;
  this.cloneCount = 0;
  this.bodyRejects = opts.bodyRejects === true;
  this.body = opts.body === undefined ? null : opts.body;
  this.source = this;
}
FakeResponse.prototype.clone = function () {
  if (this.bodyUsed) throw new TypeError('Response body is already used');
  this.cloneCount++;
  var copy = new FakeResponse({
    status: this.status, statusText: this.statusText, ok: this.ok, type: this.type,
    redirected: this.redirected, url: this.url, label: this.label, headers: this.headers.map,
    body: this.body, bodyRejects: this.bodyRejects, synthetic: this.synthetic
  });
  copy.source = this.source;
  return copy;
};
FakeResponse.prototype.arrayBuffer = function () {
  this.bodyUsed = true;
  if (this.bodyRejects) return P.reject(new TypeError('body unreadable'));
  if (this.body === null) return P.resolve(new ArrayBuffer(0));
  return P.resolve(this.body);
};
FakeResponse.prototype.text = function () { this.bodyUsed = true; return P.resolve(this.label); };
FakeResponse.redirect = function (url, status) {
  return new FakeResponse({ status: status || 302, ok: false, type: 'default', url: url,
                            label: 'redirect', headers: { Location: url } });
};
function bodyArray(response) {
  if (!response || response.body === null || response.body === undefined) return [];
  return bufferToArray(response.body);
}
function headerOf(response, name) {
  return response && response.headers ? response.headers.get(name) : null;
}

// A cached clip exactly as a correctly behaving worker would have left it:
// 200, audio/mpeg, real bytes, real validators.
function cachedClip(url, bytes, extra) {
  var opts = {
    url: url, label: 'cached-clip', body: bytesToBuffer(bytes || CLIP_BYTES),
    headers: { 'Content-Type': 'audio/mpeg', 'Content-Length': String((bytes || CLIP_BYTES).length),
               'ETag': '"clip-v1"', 'Last-Modified': 'Tue, 01 Aug 2026 10:00:00 GMT' }
  };
  Object.keys(extra || {}).forEach(function (k) { opts[k] = extra[k]; });
  return new FakeResponse(opts);
}
function mimeFor(url) {
  var path = String(url).split('?')[0];
  if (path.slice(-1) === '/') return 'text/html';
  if (/\.js$/.test(path)) return 'text/javascript';
  if (/\.json$/.test(path)) return 'application/json';
  if (/\.mp3$/.test(path)) return 'audio/mpeg';
  if (/\.svg$/.test(path)) return 'image/svg+xml';
  if (/\.png$/.test(path)) return 'image/png';
  if (/\.woff2$/.test(path)) return 'font/woff2';
  return 'text/plain';
}
function typed(url, extra) {
  var opts = { url: url, headers: { 'Content-Type': mimeFor(url) } };
  Object.keys(extra || {}).forEach(function (k) { opts[k] = extra[k]; });
  return new FakeResponse(opts);
}

// =========================================================================
// Fake Cache Storage. Insertion order is real, because the retention policy is
// insertion-order trimming and a fake that sorted its keys would prove nothing.
// =========================================================================
function keyOf(request) { return typeof request === 'string' ? request : request.url; }
function FakeCache(name, storage) {
  this.name = name; this.storage = storage; this.entries = {}; this.order = [];
  this.puts = []; this.deletes = []; this.keyCalls = 0;
}
FakeCache.prototype['delete'] = function (request) {
  var key = keyOf(request);
  this.deletes.push(key);
  var behavior = this.storage.entryDeleteBehavior ? this.storage.entryDeleteBehavior(this.name, key) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (behavior && behavior.miss) return P.resolve(false);
  if (this.entries[key] === undefined) return P.resolve(false);
  delete this.entries[key];
  this.order = this.order.filter(function (k) { return k !== key; });
  return P.resolve(true);
};
FakeCache.prototype.put = function (request, response) {
  var self_ = this, key = keyOf(request);
  this.puts.push(key);
  var attempt = this.puts.filter(function (k) { return k === key; }).length;
  var behavior = this.storage.putBehavior ? this.storage.putBehavior(this.name, key, response, attempt) : null;
  var store = function () {
    if (self_.order.indexOf(key) === -1) self_.order.push(key);
    self_.entries[key] = response;
  };
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (behavior && behavior.defer) {
    var d = deferred();
    this.storage.pendingPuts.push({ cache: this.name, key: key,
      settle: function () { store(); d.resolve(undefined); }, fail: function (e) { d.reject(e); } });
    return d.promise;
  }
  store();
  return P.resolve(undefined);
};
// The real Cache.match hands back a fresh Response every time, which is why
// reading a cached body can never consume the stored entry.
FakeCache.prototype.match = function (request) {
  var key = keyOf(request);
  var behavior = this.storage.matchBehavior ? this.storage.matchBehavior(this.name, key) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  var hit = this.entries[key];
  return P.resolve(hit === undefined ? undefined : hit.clone());
};
FakeCache.prototype.keys = function () {
  this.keyCalls++;
  var behavior = this.storage.keysBehavior ? this.storage.keysBehavior(this.name) : null;
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  return P.resolve(this.order.map(function (k) { return new FakeRequest(k); }));
};
function FakeCacheStorage(seed) {
  this.caches = {}; this.names = []; this.pendingPuts = [];
  this.openBehavior = null; this.putBehavior = null; this.deleteBehavior = null;
  this.matchBehavior = null; this.entryDeleteBehavior = null; this.keysBehavior = null;
  this.deleted = []; this.opened = []; this.globalMatches = 0;
  var self_ = this;
  Object.keys(seed || {}).forEach(function (name) {
    var cache = self_.rawOpen(name);
    Object.keys(seed[name]).forEach(function (key) { cache.order.push(key); cache.entries[key] = seed[name][key]; });
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
  return cache ? cache.order.slice() : null;
};

// =========================================================================
// The shipping worker in a fake global
// =========================================================================
var ORIGIN = 'https://popolsku.app';
var EPILOGUE = '\nreturn { CACHE: CACHE, AUDIO_CACHE: AUDIO_CACHE, classifyRequest: classifyRequest,' +
  ' canonicalKeyFor: canonicalKeyFor, canonicalPath: canonicalPath, parseUrl: parseUrl,' +
  ' parseByteRange: parseByteRange, resolveByteRange: resolveByteRange,' +
  ' isApprovedAudioKey: isApprovedAudioKey, isCacheableResponse: isCacheableResponse,' +
  ' AUDIO_CACHE_MAX_ENTRIES: AUDIO_CACHE_MAX_ENTRIES, AUDIO_CACHE_TRIM_TO: AUDIO_CACHE_TRIM_TO,' +
  ' AUDIO_QUOTA_EVICTION_BATCH: AUDIO_QUOTA_EVICTION_BATCH,' +
  ' AUDIO_QUOTA_RETRY_LIMIT: AUDIO_QUOTA_RETRY_LIMIT, state: SW_STATE };\n';

function makeWorker(options) {
  options = options || {};
  var storage = new FakeCacheStorage(options.seed || {});
  var route = options.route || function (url) { return { response: typed(url) }; };
  var fetchCalls = [], warnings = [], listeners = {};
  function fetchFn(input, init) {
    var url = keyOf(input);
    fetchCalls.push({ url: url, init: init || null, request: typeof input === 'string' ? null : input });
    var outcome = route(url, init, input);
    if (!outcome) return P.reject(new TypeError('Failed to fetch ' + url));
    if (outcome.reject) return P.reject(outcome.reject);
    return P.resolve(outcome.response || typed(url));
  }
  fetchFn.calls = fetchCalls;
  var swSelf = {
    location: { origin: ORIGIN, href: ORIGIN + '/sw.js', pathname: '/sw.js' },
    skipWaitingCalls: 0, claimCalls: 0,
    addEventListener: function (type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    skipWaiting: function () { swSelf.skipWaitingCalls++; return P.resolve(); },
    clients: { claim: function () { swSelf.claimCalls++; return P.resolve(); } },
    registration: { scope: ORIGIN + '/' }
  };
  var consoleFake = { warn: function (m) { warnings.push(String(m)); }, error: function (m) { warnings.push(String(m)); }, log: function () {} };
  var api = (new Function('self', 'caches', 'fetch', 'Promise', 'URL', 'Response', 'console',
    SW_SRC + EPILOGUE))(swSelf, storage, fetchFn, P, FakeURL, FakeResponse, consoleFake);
  return {
    self: swSelf, caches: storage, fetch: fetchFn, api: api, warnings: warnings,
    fire: function (type, event) { (listeners[type] || []).forEach(function (fn) { fn(event); }); return event; }
  };
}
function FetchEvent(request) { this.request = request; this.waits = []; this.responses = []; }
FetchEvent.prototype.waitUntil = function (p) { this.waits.push(p); return undefined; };
FetchEvent.prototype.respondWith = function (p) { this.responses.push(p); return undefined; };
function runFetch(worker, request) {
  var e = new FetchEvent(request);
  worker.fire('fetch', e);
  drain();
  var responses = e.responses.map(watch), writes = e.waits.map(watch);
  drain();
  return { event: e, responses: responses, writes: writes, intercepted: e.responses.length > 0 };
}
function respState(run, i) { var r = run.responses[i || 0]; return r ? r.state : 'no-response'; }
function respValue(run, i) { var r = run.responses[i || 0]; return r ? r.value : undefined; }
function respStatus(run) { var v = respValue(run); return v && v.status !== undefined ? v.status : 'no-response'; }
function respLabel(run) { var v = respValue(run); return v && v.label !== undefined ? v.label : null; }
function writeState(run, i) { var w = run.writes[i || 0]; return w ? w.state : 'no-write'; }
function inv(worker, name) { var i = worker.caches.inventory(name); return i === null ? 'no-cache' : i; }
function invLen(worker, name) { var i = worker.caches.inventory(name); return i === null ? -1 : i.length; }
function storedKeys(worker) {
  var out = [];
  worker.caches.names.forEach(function (n) {
    worker.caches.caches[n].order.forEach(function (k) { out.push(n + ' :: ' + k); });
  });
  return out.sort();
}
function get(url, opts) { return new FakeRequest(url, opts); }
function ranged(url, value, extra) {
  var headers = { Range: value };
  Object.keys(extra || {}).forEach(function (k) { headers[k] = extra[k]; });
  return new FakeRequest(url, { headers: headers });
}
var CLIP_URL = ORIGIN + '/' + CLIP_FILE;
var CLIP2_URL = ORIGIN + '/audio/004363602321.mp3';
var W0 = makeWorker();
var API = W0.api;
var SHELL = API.CACHE, AUDIO = API.AUDIO_CACHE;
function audioSeed(url, response) { var s = {}; s[AUDIO] = {}; s[AUDIO][url] = response; return s; }

// =========================================================================
// R. MLG-4A-05 - the Range contract
// =========================================================================
eq('R0 the shell cache is the current shell revision', SHELL, 'popolsku-v60');
eq('R0 the audio cache name is unchanged', AUDIO, 'popolsku-audio');

// --- the grammar this worker accepts, and what it refuses to guess about ---
[
  ['bytes=0-99', { suffix: null, start: 0, end: 99 }],
  ['bytes=100-', { suffix: null, start: 100, end: null }],
  ['bytes=-100', { suffix: 100, start: null, end: null }],
  ['bytes=0-0', { suffix: null, start: 0, end: 0 }],
  ['BYTES=0-9', { suffix: null, start: 0, end: 9 }],
  ['  bytes = 5-9  ', { suffix: null, start: 5, end: 9 }],
  ['bytes=-0', { suffix: 0, start: null, end: null }]
].forEach(function (row) {
  eq('R1 supported syntax ' + JSON.stringify(row[0]), API.parseByteRange(row[0]), row[1]);
});
['bytes=0-99,200-299', 'bytes=0-0,-1', 'items=0-1', 'seconds=0-1', 'bytes=', 'bytes=-',
 'bytes=a-b', 'bytes=1-2-3', 'bytes=0-1x', 'bytes=x', '0-99', '', null, undefined
].forEach(function (value) {
  eq('R2 unsupported syntax is refused, not guessed: ' + JSON.stringify(value),
     API.parseByteRange(value), null);
});
// --- resolution against a known length, including clamping and 416 cases ---
[
  ['bytes=0-0', 100, { start: 0, end: 0, length: 1, total: 100 }],
  ['bytes=0-99', 100, { start: 0, end: 99, length: 100, total: 100 }],
  ['bytes=10-19', 100, { start: 10, end: 19, length: 10, total: 100 }],
  ['bytes=10-', 100, { start: 10, end: 99, length: 90, total: 100 }],
  ['bytes=-10', 100, { start: 90, end: 99, length: 10, total: 100 }],
  ['bytes=-500', 100, { start: 0, end: 99, length: 100, total: 100 }],
  ['bytes=90-500', 100, { start: 90, end: 99, length: 10, total: 100 }],
  ['bytes=99-99', 100, { start: 99, end: 99, length: 1, total: 100 }],
  ['bytes=100-', 100, null],
  ['bytes=100-200', 100, null],
  ['bytes=-0', 100, null],
  ['bytes=0-0', 0, null],
  ['bytes=5-3', 100, null]
].forEach(function (row) {
  eq('R3 resolve ' + row[0] + ' over ' + row[1] + ' bytes',
     API.resolveByteRange(API.parseByteRange(row[0]), row[1]), row[2]);
});

// 1. full MP3 GET, online and cold.
(function () {
  var worker = makeWorker({ route: function (url) { return { response: cachedClip(url) }; } });
  var run = runFetch(worker, get(CLIP_URL));
  eq('R4 a cold full clip is fetched and returned', [respState(run), respStatus(run)], ['fulfilled', 200]);
  eq('R4 a cold full clip is stored in the audio cache under its canonical key', inv(worker, AUDIO), [CLIP_URL]);
  eq('R4 nothing else was cached', invLen(worker, SHELL), -1);
})();
// 2. full MP3 GET, warm.
(function () {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run = runFetch(worker, get(CLIP_URL));
  eq('R5 a warm full clip is served from cache', [respStatus(run), respLabel(run)], [200, 'cached-clip']);
  eq('R5 a warm full clip asks the network for nothing', worker.fetch.calls.length, 0);
  eq('R5 a warm full clip writes nothing', worker.self.ppSwState.writes.scheduled, 0);
})();

// 3-9. Synthesized 206 responses, compared with the real repository MP3.
[
  { name: 'bytes=0-0', header: 'bytes=0-0', start: 0, end: 0 },
  { name: 'bytes=0-99', header: 'bytes=0-99', start: 0, end: 99 },
  { name: 'bytes=100-199', header: 'bytes=100-199', start: 100, end: 199 },
  { name: 'bytes=100- (open ended)', header: 'bytes=100-', start: 100, end: CLIP_LEN - 1 },
  { name: 'bytes=-100 (suffix)', header: 'bytes=-100', start: CLIP_LEN - 100, end: CLIP_LEN - 1 },
  { name: 'end beyond the clip is clamped', header: 'bytes=' + (CLIP_LEN - 50) + '-' + (CLIP_LEN + 5000),
    start: CLIP_LEN - 50, end: CLIP_LEN - 1 },
  { name: 'the final byte alone', header: 'bytes=' + (CLIP_LEN - 1) + '-' + (CLIP_LEN - 1),
    start: CLIP_LEN - 1, end: CLIP_LEN - 1 }
].forEach(function (row) {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run = runFetch(worker, ranged(CLIP_URL, row.header));
  var res = respValue(run);
  var length = row.end - row.start + 1;
  eq('R6 ' + row.name + ' answers 206', [respState(run), respStatus(run)], ['fulfilled', 206]);
  eq('R6 ' + row.name + ' has the exact Content-Range', headerOf(res, 'content-range'),
     'bytes ' + row.start + '-' + row.end + '/' + CLIP_LEN);
  eq('R6 ' + row.name + ' has the partial Content-Length', headerOf(res, 'content-length'), String(length));
  eq('R6 ' + row.name + ' is audio/mpeg', headerOf(res, 'content-type'), 'audio/mpeg');
  eq('R6 ' + row.name + ' advertises byte ranges', headerOf(res, 'accept-ranges'), 'bytes');
  eq('R6 ' + row.name + ' keeps the cached validators',
     [headerOf(res, 'etag'), headerOf(res, 'last-modified')],
     ['"clip-v1"', 'Tue, 01 Aug 2026 10:00:00 GMT']);
  eq('R6 ' + row.name + ' returns exactly the repository bytes',
     fingerprint(bodyArray(res)), fingerprint(realSlice(row.start, row.end)));
  eq('R6 ' + row.name + ' asks the network for nothing', worker.fetch.calls.length, 0);
  eq('R6 ' + row.name + ' never reaches the cache writer at all',
     [worker.self.ppSwState.writes.scheduled, worker.self.ppSwState.writes.succeeded,
      worker.self.ppSwState.writes.failed, worker.self.ppSwState.writes.skipped], [0, 0, 0, 0]);
  eq('R6 ' + row.name + ' leaves one full entry in the audio cache', inv(worker, AUDIO), [CLIP_URL]);
  eq('R6 ' + row.name + ' does not mutate the cached full response',
     [worker.caches.caches[AUDIO].entries[CLIP_URL].status,
      worker.caches.caches[AUDIO].entries[CLIP_URL].bodyUsed,
      fingerprint(bufferToArray(worker.caches.caches[AUDIO].entries[CLIP_URL].body))],
     [200, false, fingerprint(realSlice(0, CLIP_LEN - 1))]);
});

// 10-11. Unsatisfiable single ranges.
[['bytes=' + CLIP_LEN + '-', 'a start beyond the clip'],
 ['bytes=' + (CLIP_LEN + 10) + '-' + (CLIP_LEN + 20), 'a whole range beyond the clip'],
 ['bytes=-0', 'a zero-length suffix']
].forEach(function (row) {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run = runFetch(worker, ranged(CLIP_URL, row[0]));
  var res = respValue(run);
  eq('R7 ' + row[1] + ' returns 416', [respState(run), respStatus(run)], ['fulfilled', 416]);
  eq('R7 ' + row[1] + ' reports the full length', headerOf(res, 'content-range'), 'bytes */' + CLIP_LEN);
  eq('R7 ' + row[1] + ' returns no MP3 body', bodyArray(res), []);
  eq('R7 ' + row[1] + ' is not cached', storedKeys(worker), [AUDIO + ' :: ' + CLIP_URL]);
  eq('R7 ' + row[1] + ' writes nothing', worker.self.ppSwState.writes.scheduled, 0);
});

// 12-14. Malformed, multiple and unsupported units are handed to the network.
['bytes=0-99,200-299', 'bytes=abc', 'bytes=1-2-3', 'items=0-1', 'seconds=0-9', 'bytes=', 'bytes=-'
].forEach(function (value) {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run = runFetch(worker, ranged(CLIP_URL, value));
  ok('R8 ' + JSON.stringify(value) + ' is not answered from cache', !run.intercepted);
  eq('R8 ' + JSON.stringify(value) + ' makes no worker fetch', worker.fetch.calls.length, 0);
  eq('R8 ' + JSON.stringify(value) + ' writes nothing', worker.self.ppSwState.writes.scheduled, 0);
  eq('R8 ' + JSON.stringify(value) + ' is counted as a pass-through',
     worker.self.ppSwState.range.passthrough, 1);
  eq('R8 ' + JSON.stringify(value) + ' synthesizes nothing',
     [worker.self.ppSwState.range.synthesized, worker.self.ppSwState.range.unsatisfiable], [0, 0]);
});

// 15. If-Range: the documented conservative pass-through.
(function () {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99', { 'If-Range': '"clip-v1"' }));
  ok('R9 a conditional If-Range resume is never answered from cache', !run.intercepted);
  eq('R9 If-Range is counted as a pass-through', worker.self.ppSwState.range.passthrough, 1);
  eq('R9 If-Range synthesizes nothing', worker.self.ppSwState.range.synthesized, 0);
  var dated = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var run2 = runFetch(dated, ranged(CLIP_URL, 'bytes=0-99', { 'if-range': 'Tue, 01 Aug 2026 10:00:00 GMT' }));
  ok('R9 a date-form If-Range follows the same policy', !run2.intercepted);
  ok('R9 the policy is documented in the worker', SW_SRC.indexOf('If-Range asks us to compare a validator') !== -1);
})();

// 16. Cache miss keeps the original request, Range header intact.
(function () {
  var worker = makeWorker({ route: function (url) {
    return { response: new FakeResponse({ url: url, status: 206, label: 'network-206',
      headers: { 'Content-Type': 'audio/mpeg', 'Content-Range': 'bytes 0-99/' + CLIP_LEN } }) };
  } });
  var request = ranged(CLIP_URL, 'bytes=0-99');
  var run = runFetch(worker, request);
  eq('R10 a Range cache miss reaches the network', worker.fetch.calls.length, 1);
  ok('R10 the network gets the original request object', worker.fetch.calls[0].request === request);
  eq('R10 the Range header survives', worker.fetch.calls[0].request.headers.get('range'), 'bytes=0-99');
  eq('R10 the network partial is returned to the page', [respState(run), respStatus(run)], ['fulfilled', 206]);
  eq('R10 a Range network response is never cached', storedKeys(worker), []);
  eq('R10 and never even offered to the cache writer',
     [worker.self.ppSwState.writes.scheduled, worker.self.ppSwState.writes.skipped,
      worker.self.ppSwState.writes.failed], [0, 0, 0]);
  eq('R10 the miss is counted', worker.self.ppSwState.range.cacheMiss, 1);
})();

// 17-18. Offline.
(function () {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)),
                            route: function () { return { reject: new TypeError('offline') }; } });
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=200-299'));
  eq('R11 offline, a warm clip still answers a Range request', respStatus(run), 206);
  eq('R11 offline, the bytes are still exact',
     fingerprint(bodyArray(respValue(run))), fingerprint(realSlice(200, 299)));
  eq('R11 offline, nothing reached the network', worker.fetch.calls.length, 0);
  var cold = makeWorker({ route: function () { return { reject: new TypeError('offline') }; } });
  var coldRun = runFetch(cold, ranged(CLIP2_URL, 'bytes=0-99'));
  eq('R12 offline, a cold Range request fails normally', respState(coldRun), 'rejected');
  eq('R12 offline, a failed Range request caches nothing', storedKeys(cold), []);
})();

// 19-21. An entry that does not pass the write-time contract is never sliced.
[
  ['a text/html body under an MP3 key', { headers: { 'Content-Type': 'text/html' } }],
  ['a stored 206 partial', { status: 206, headers: { 'Content-Type': 'audio/mpeg' } }],
  ['an entry with no Content-Type', { headers: {} }],
  ['a redirected entry', { redirected: true }],
  ['an opaque entry', { type: 'opaque' }]
].forEach(function (row) {
  var bad = cachedClip(CLIP_URL);
  Object.keys(row[1]).forEach(function (k) {
    if (k === 'headers') bad.headers = new FakeHeaders(row[1].headers); else bad[k] = row[1][k];
  });
  if (row[1].status !== undefined) bad.ok = row[1].status >= 200 && row[1].status < 300;
  bad.label = 'invalid-entry';
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, bad), route: function (url) {
    return { response: new FakeResponse({ url: url, status: 206, label: 'network-206',
      headers: { 'Content-Type': 'audio/mpeg' } }) };
  } });
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99'));
  ok('R13 ' + row[0] + ' is never sliced', respLabel(run) !== 'invalid-entry');
  eq('R13 ' + row[0] + ' falls through to the original Range request',
     [worker.fetch.calls.length, worker.fetch.calls[0] ? worker.fetch.calls[0].request.headers.get('range') : null],
     [1, 'bytes=0-99']);
  eq('R13 ' + row[0] + ' is evicted from the audio cache', inv(worker, AUDIO), []);
  eq('R13 ' + row[0] + ' produces no synthetic partial', worker.self.ppSwState.range.synthesized, 0);
  eq('R13 ' + row[0] + ' writes nothing', storedKeys(worker), []);
});

// 22. Headers say clip, body cannot be read.
(function () {
  var unreadable = cachedClip(CLIP_URL, CLIP_BYTES, { bodyRejects: true, label: 'unreadable' });
  var seed = {}; seed[AUDIO] = {};
  seed[AUDIO][CLIP_URL] = unreadable;
  seed[AUDIO][CLIP2_URL] = cachedClip(CLIP2_URL);
  var worker = makeWorker({ seed: seed, route: function (url) {
    return { response: new FakeResponse({ url: url, status: 206, label: 'network-206',
      headers: { 'Content-Type': 'audio/mpeg' } }) };
  } });
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99'));
  eq('R14 an unreadable cached body never becomes a broken partial', respLabel(run), 'network-206');
  eq('R14 the original Range request is used for the retry',
     worker.fetch.calls[0].request.headers.get('range'), 'bytes=0-99');
  eq('R14 exactly that one entry is dropped', inv(worker, AUDIO), [CLIP2_URL]);
  eq('R14 the audio cache is not cleared', invLen(worker, AUDIO), 1);
  eq('R14 the failure is counted', worker.self.ppSwState.range.bodyReadFailed, 1);
  eq('R14 the failure is recorded without a body',
     [worker.self.ppSwState.audioFailures.length, worker.self.ppSwState.audioFailures[0].reason,
      worker.self.ppSwState.audioFailures[0].key,
      Object.keys(worker.self.ppSwState.audioFailures[0]).sort().join(',')],
     [1, 'body-read', CLIP_URL, 'key,message,reason']);
  eq('R14 nothing was written back', storedKeys(worker), [AUDIO + ' :: ' + CLIP2_URL]);
})();
// 22b. A delete failure still refuses to serve the broken entry.
(function () {
  var unreadable = cachedClip(CLIP_URL, CLIP_BYTES, { bodyRejects: true, label: 'unreadable' });
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, unreadable),
    route: function (url) { return { response: new FakeResponse({ url: url, status: 206, label: 'network-206', headers: { 'Content-Type': 'audio/mpeg' } }) }; } });
  worker.caches.entryDeleteBehavior = function () { return { reject: new Error('delete denied') }; };
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99'));
  eq('R15 a failed drop still does not serve the unreadable entry', respLabel(run), 'network-206');
  eq('R15 the eviction failure is counted', worker.self.ppSwState.reads.evictionFailed, 1);
})();

// 24. Approved query variants resolve to the one canonical cached body.
(function () {
  var worker = makeWorker({ seed: audioSeed(CLIP_URL, cachedClip(CLIP_URL)) });
  var plain = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99'));
  var variant = runFetch(worker, ranged(CLIP_URL + '?v=2', 'bytes=0-99'));
  var another = runFetch(worker, ranged(CLIP_URL + '?cachebust=9#frag', 'bytes=0-99'));
  eq('R16 a query variant is answered from the same canonical body',
     [fingerprint(bodyArray(respValue(variant))), fingerprint(bodyArray(respValue(another)))],
     [fingerprint(bodyArray(respValue(plain))), fingerprint(bodyArray(respValue(plain)))]);
  eq('R16 a query variant creates no second audio-cache key', inv(worker, AUDIO), [CLIP_URL]);
  eq('R16 no partial entry is ever stored', storedKeys(worker), [AUDIO + ' :: ' + CLIP_URL]);
  eq('R16 three Range requests, three synthetic partials, zero writes',
     [worker.self.ppSwState.range.synthesized, worker.self.ppSwState.writes.scheduled], [3, 0]);
})();

// 25. An unrelated cache holding the same key must not answer.
(function () {
  var intruderBytes = new Uint8Array(CLIP_LEN);
  for (var i = 0; i < CLIP_LEN; i++) intruderBytes[i] = (i * 7 + 1) & 255;
  var seed = {};
  seed['unrelated-tool-cache'] = {};
  seed['unrelated-tool-cache'][CLIP_URL] = cachedClip(CLIP_URL, intruderBytes, { label: 'intruder' });
  seed[AUDIO] = {};
  seed[AUDIO][CLIP_URL] = cachedClip(CLIP_URL);
  var worker = makeWorker({ seed: seed });
  var run = runFetch(worker, ranged(CLIP_URL, 'bytes=0-99'));
  eq('R17 the slice comes from the named audio cache',
     fingerprint(bodyArray(respValue(run))), fingerprint(realSlice(0, 99)));
  eq('R17 no global cache lookup was used', worker.caches.globalMatches, 0);
  eq('R17 the unrelated cache was never opened',
     worker.caches.opened.filter(function (n) { return n === 'unrelated-tool-cache'; }), []);
  eq('R17 the unrelated cache is untouched', inv(worker, 'unrelated-tool-cache'), [CLIP_URL]);
  var onlyIntruder = makeWorker({ seed: (function () { var s = {}; s['unrelated-tool-cache'] = {}; s['unrelated-tool-cache'][CLIP_URL] = cachedClip(CLIP_URL, intruderBytes, { label: 'intruder' }); return s; })(),
    route: function () { return { reject: new TypeError('offline') }; } });
  var borrowed = runFetch(onlyIntruder, ranged(CLIP_URL, 'bytes=0-99'));
  eq('R17 an unrelated cache alone cannot satisfy a Range request', respState(borrowed), 'rejected');
})();

// 26. Only audio is covered by this policy.
[ORIGIN + '/data-a1.js', ORIGIN + '/', ORIGIN + '/pp-answer.js', ORIGIN + '/audio-manifest.json',
 ORIGIN + '/icon-192.png'].forEach(function (url) {
  var worker = makeWorker();
  var run = runFetch(worker, ranged(url, 'bytes=0-99'));
  ok('R18 a non-audio Range request is not intercepted by the audio policy: ' + url, !run.intercepted);
  eq('R18 and it writes nothing: ' + url, storedKeys(worker), []);
});
(function () {
  var worker = makeWorker();
  var run = runFetch(worker, ranged('https://cdn.example.com/audio/ab12ef34.mp3', 'bytes=0-99'));
  ok('R18 a cross-origin Range request is not intercepted', !run.intercepted);
  var post = makeWorker();
  var postRun = runFetch(post, new FakeRequest(CLIP_URL, { method: 'POST', headers: { Range: 'bytes=0-99' } }));
  ok('R18 a non-GET Range request is not intercepted', !postRun.intercepted);
})();
eq('R19 a Range request is still its own request class',
   [API.classifyRequest(ranged(CLIP_URL, 'bytes=0-1')),
    API.classifyRequest(ranged(ORIGIN + '/data-a1.js', 'bytes=0-1'))], ['range', 'range']);
ok('R20 no synthesized partial is ever multipart',
   SW_CODE.indexOf('multipart') === -1 && SW_CODE.indexOf('boundary') === -1);

// =========================================================================
// S. MLG-4A-08 - bounded retention, quota recovery, arbitrary eviction
// =========================================================================
eq('S0 the retention constants are named and ordered',
   [API.AUDIO_CACHE_MAX_ENTRIES, API.AUDIO_CACHE_TRIM_TO, API.AUDIO_QUOTA_EVICTION_BATCH,
    API.AUDIO_QUOTA_RETRY_LIMIT], [4200, 4000, 64, 1]);
ok('S0 the trim target is below the ceiling, so trimming is not a per-write cost',
   API.AUDIO_CACHE_TRIM_TO < API.AUDIO_CACHE_MAX_ENTRIES);
(function () {
  var manifest = JSON.parse(readFile(ROOT + 'audio-manifest.json'));
  var clips = Object.keys(manifest.entries).length;
  eq('S1 the shipped library is still 3,377 clips', clips, 3377);
  ok('S1 the whole shipped library fits inside the retention bound with headroom',
     clips < API.AUDIO_CACHE_MAX_ENTRIES && clips < API.AUDIO_CACHE_TRIM_TO);
  INFO.push('retention bound ' + API.AUDIO_CACHE_MAX_ENTRIES + ' entries leaves ' +
            (API.AUDIO_CACHE_MAX_ENTRIES - clips) + ' clips of headroom over the shipped library');
})();
ok('S1 the policy names itself accurately as insertion order, not LRU',
   SW_SRC.indexOf('INSERTION-ORDER (FIFO) trimming, not LRU') !== -1);
ok('S1 the bound is documented as an entry count, not a byte limit',
   SW_SRC.indexOf('ENTRY COUNT, not a byte budget') !== -1);

function clipUrl(i) {
  var hex = ('00000000' + i.toString(16)).slice(-8) + 'abcd';
  return ORIGIN + '/audio/' + hex + '.mp3';
}
function seedClips(count) {
  var entries = {};
  for (var i = 0; i < count; i++) entries[clipUrl(i)] = cachedClip(clipUrl(i), new Uint8Array([1, 2, 3]));
  var seed = {}; seed[AUDIO] = entries; return seed;
}
function audioRoute(url) { return { response: cachedClip(url, new Uint8Array([9, 9, 9])) }; }

// Normal operation: no trimming, and a warm hit never scans.
(function () {
  var worker = makeWorker({ seed: seedClips(10), route: audioRoute });
  var run = runFetch(worker, get(clipUrl(500)));
  eq('S2 a new clip below the bound is stored', respStatus(run), 200);
  eq('S2 the audio cache grew by exactly one', invLen(worker, AUDIO), 11);
  eq('S2 one retention check ran, nothing was trimmed',
     [worker.self.ppSwState.audio.retentionChecks, worker.self.ppSwState.audio.trimmed], [1, 0]);
  var warm = runFetch(worker, get(clipUrl(500)));
  eq('S3 a warm hit is served from cache', respStatus(warm), 200);
  eq('S3 a warm hit schedules no write', worker.self.ppSwState.writes.scheduled, 1);
  eq('S3 a warm hit runs no retention check', worker.self.ppSwState.audio.retentionChecks, 1);
  eq('S3 a warm hit never enumerates the cache', worker.caches.caches[AUDIO].keyCalls, 1);
  var second = runFetch(worker, get(clipUrl(501)));
  eq('S4 a second cold write does not rescan the whole cache', worker.caches.caches[AUDIO].keyCalls, 1);
  eq('S4 the estimate keeps growing without a scan', invLen(worker, AUDIO), 12);
})();

// At the bound: insertion-order trim down to the target.
(function () {
  var worker = makeWorker({ seed: seedClips(API.AUDIO_CACHE_MAX_ENTRIES), route: audioRoute });
  var fresh = clipUrl(999999);
  var run = runFetch(worker, get(fresh));
  eq('S5 the online response is still delivered', respStatus(run), 200);
  eq('S5 the cache is trimmed to the target', invLen(worker, AUDIO), API.AUDIO_CACHE_TRIM_TO);
  eq('S5 the newly written clip is protected',
     worker.caches.caches[AUDIO].entries[fresh] !== undefined, true);
  eq('S5 the oldest inserted clips are the ones that went',
     [worker.caches.caches[AUDIO].entries[clipUrl(0)] === undefined,
      worker.caches.caches[AUDIO].entries[clipUrl(200)] === undefined,
      worker.caches.caches[AUDIO].entries[clipUrl(201)] !== undefined,
      worker.caches.caches[AUDIO].entries[clipUrl(API.AUDIO_CACHE_MAX_ENTRIES - 1)] !== undefined],
     [true, true, true, true]);
  eq('S5 the trim is counted', worker.self.ppSwState.audio.trimmed,
     API.AUDIO_CACHE_MAX_ENTRIES + 1 - API.AUDIO_CACHE_TRIM_TO);
  eq('S5 the trim work is bound to the fetch event', run.event.waits.length, 1);
  eq('S5 the trim ran inside that one bound promise', writeState(run), 'fulfilled');
})();

// The trim never leaves its own cache or its own asset class.
(function () {
  /* The foreign key is seeded FIRST, so it sits among the OLDEST entries: a trim
     that stopped filtering by asset class would take it before any clip. */
  var seed = {}; seed[AUDIO] = {};
  seed[AUDIO][ORIGIN + '/audio/notes.txt'] = typed(ORIGIN + '/audio/notes.txt', { label: 'foreign' });
  var full = seedClips(API.AUDIO_CACHE_MAX_ENTRIES);
  Object.keys(full[AUDIO]).forEach(function (k) { seed[AUDIO][k] = full[AUDIO][k]; });
  seed[SHELL] = {}; seed[SHELL][ORIGIN + '/'] = typed(ORIGIN + '/', { label: 'shell' });
  seed['unrelated-tool-cache'] = {}; seed['unrelated-tool-cache'][ORIGIN + '/keep-me'] = typed(ORIGIN + '/keep-me', { label: 'keep' });
  var worker = makeWorker({ seed: seed, route: audioRoute });
  runFetch(worker, get(clipUrl(999998)));
  eq('S6 the shell cache is untouched by retention', inv(worker, SHELL), [ORIGIN + '/']);
  eq('S6 an unrelated cache is untouched by retention', inv(worker, 'unrelated-tool-cache'), [ORIGIN + '/keep-me']);
  eq('S6 a non-MP3 key inside the audio cache is never trimmed',
     worker.caches.caches[AUDIO].entries[ORIGIN + '/audio/notes.txt'] !== undefined, true);
  eq('S6 no cache was deleted wholesale', worker.caches.deleted, []);
})();

// Failure containment in maintenance.
(function () {
  var worker = makeWorker({ seed: seedClips(API.AUDIO_CACHE_MAX_ENTRIES), route: audioRoute });
  worker.caches.entryDeleteBehavior = function () { return { reject: new Error('delete denied') }; };
  var run = runFetch(worker, get(clipUrl(999997)));
  eq('S7 a delete rejection never fails the response', respStatus(run), 200);
  eq('S7 the bound write still settles', writeState(run), 'fulfilled');
  eq('S7 nothing was counted as trimmed', worker.self.ppSwState.audio.trimmed, 0);
  var scanFail = makeWorker({ seed: seedClips(5), route: audioRoute });
  scanFail.caches.keysBehavior = function () { return { reject: new Error('keys denied') }; };
  var scanRun = runFetch(scanFail, get(clipUrl(999996)));
  eq('S8 a keys() rejection never fails the response', respStatus(scanRun), 200);
  eq('S8 the retention failure is contained and recorded',
     [writeState(scanRun), scanFail.self.ppSwState.audioFailures.length > 0], ['fulfilled', true]);
})();

// Replacing an existing canonical key is not growth.
(function () {
  var worker = makeWorker({ seed: seedClips(3), route: audioRoute });
  runFetch(worker, get(clipUrl(1)));
  eq('S9 a repaired existing key does not add an entry', invLen(worker, AUDIO), 3);
  eq('S9 and nothing is trimmed because of it', worker.self.ppSwState.audio.trimmed, 0);
})();

// Quota: the response survives, one bounded recovery, one retry, no loop.
function quotaWorker(options) {
  options = options || {};
  var worker = makeWorker({ seed: seedClips(options.clips === undefined ? 200 : options.clips), route: audioRoute });
  worker.caches.putBehavior = function (name, key, response, attempt) {
    if (name !== AUDIO) return null;
    if (options.alwaysFail) return { reject: options.error || new Error('QuotaExceededError') };
    return attempt === 1 ? { reject: options.error || new Error('QuotaExceededError') } : null;
  };
  return worker;
}
(function () {
  var worker = quotaWorker();
  var fresh = clipUrl(999995);
  var run = runFetch(worker, get(fresh));
  eq('S10 a quota failure never costs the learner the online response',
     [respState(run), respStatus(run)], ['fulfilled', 200]);
  eq('S10 the write failure is recorded', worker.self.ppSwState.audio.writeFailures, 1);
  eq('S10 recovery ran exactly once', worker.self.ppSwState.audio.recoveryAttempts, 1);
  eq('S10 a bounded batch of older clips was evicted',
     worker.self.ppSwState.audio.trimmed, API.AUDIO_QUOTA_EVICTION_BATCH);
  eq('S10 the retry stored the new clip',
     [worker.self.ppSwState.audio.recovered, worker.caches.caches[AUDIO].entries[fresh] !== undefined],
     [1, true]);
  eq('S10 the new key was never a candidate for its own eviction',
     worker.caches.caches[AUDIO].deletes.indexOf(fresh), -1);
  eq('S10 exactly two put attempts were made for that key',
     worker.caches.caches[AUDIO].puts.filter(function (k) { return k === fresh; }).length, 2);
  eq('S10 recovery is bound to the fetch event', [run.event.waits.length, writeState(run)], [1, 'fulfilled']);
})();
(function () {
  var worker = quotaWorker({ alwaysFail: true });
  var fresh = clipUrl(999994);
  var run = runFetch(worker, get(fresh));
  eq('S11 a still-failing retry never breaks the online response', respStatus(run), 200);
  eq('S11 the final failure is recorded once', worker.self.ppSwState.audio.recoveryFailed, 1);
  eq('S11 there is no retry loop',
     worker.caches.caches[AUDIO].puts.filter(function (k) { return k === fresh; }).length, 2);
  eq('S11 the rejection is contained, not unhandled', writeState(run), 'fulfilled');
  eq('S11 the diagnostics name the failure without a body',
     worker.self.ppSwState.audioFailures.map(function (r) { return r.reason; }), ['write', 'quota-retry']);
  var later = runFetch(worker, get(clipUrl(999993)));
  eq('S12 a later request still tries normally', respStatus(later), 200);
  eq('S12 and recovers again on its own', worker.self.ppSwState.audio.recoveryAttempts, 2);
})();
(function () {
  // Not a quota-named error at all: the recovery is deliberately name-agnostic.
  var worker = quotaWorker({ error: new TypeError('storage went away') });
  var fresh = clipUrl(999992);
  runFetch(worker, get(fresh));
  eq('S13 recovery does not depend on one browser-specific error name',
     [worker.self.ppSwState.audio.recoveryAttempts, worker.self.ppSwState.audio.recovered], [1, 1]);
})();
(function () {
  var seed = seedClips(100);
  seed[SHELL] = {}; seed[SHELL][ORIGIN + '/'] = typed(ORIGIN + '/', { label: 'shell' });
  seed['unrelated-tool-cache'] = {}; seed['unrelated-tool-cache'][ORIGIN + '/keep-me'] = typed(ORIGIN + '/keep-me', { label: 'keep' });
  var worker = makeWorker({ seed: seed, route: audioRoute });
  worker.caches.putBehavior = function (name, key, response, attempt) {
    return name === AUDIO && attempt === 1 ? { reject: new Error('QuotaExceededError') } : null;
  };
  runFetch(worker, get(clipUrl(999991)));
  eq('S14 quota recovery never touches the shell cache', inv(worker, SHELL), [ORIGIN + '/']);
  eq('S14 quota recovery never touches an unrelated cache', inv(worker, 'unrelated-tool-cache'), [ORIGIN + '/keep-me']);
  eq('S14 quota recovery never deletes a whole cache', worker.caches.deleted, []);
})();
(function () {
  var worker = makeWorker({ seed: seedClips(2) });
  worker.caches.putBehavior = function (name, key, response, attempt) {
    return name === SHELL && attempt === 1 ? { reject: new Error('QuotaExceededError') } : null;
  };
  var run = runFetch(worker, get(ORIGIN + '/pp-answer.js'));
  eq('S15 a shell write failure is contained without audio recovery',
     [respStatus(run), worker.self.ppSwState.audio.recoveryAttempts, writeState(run)],
     [200, 0, 'fulfilled']);
})();

// Arbitrary browser eviction of individual entries.
(function () {
  var seed = seedClips(3);
  var worker = makeWorker({ seed: seed, route: audioRoute });
  delete worker.caches.caches[AUDIO].entries[clipUrl(1)];
  worker.caches.caches[AUDIO].order = worker.caches.caches[AUDIO].order.filter(function (k) { return k !== clipUrl(1); });
  var survivor = runFetch(worker, get(clipUrl(0)));
  eq('S16 a partially evicted audio cache still serves what it kept', respStatus(survivor), 200);
  eq('S16 the survivor came from cache', worker.fetch.calls.length, 0);
  var missing = runFetch(worker, get(clipUrl(1)));
  eq('S17 an evicted clip is an ordinary cache miss online', respStatus(missing), 200);
  eq('S17 and it is re-cached', worker.caches.caches[AUDIO].entries[clipUrl(1)] !== undefined, true);
  var offline = makeWorker({ route: function () { return { reject: new TypeError('offline') }; } });
  var gone = runFetch(offline, get(clipUrl(1)));
  eq('S18 offline, an evicted clip fails normally so the app can show its retry state',
     respState(gone), 'rejected');
  var wiped = makeWorker({ route: audioRoute });
  var rebuilt = runFetch(wiped, get(clipUrl(1)));
  eq('S19 a completely wiped origin store rebuilds on the next online play',
     [respStatus(rebuilt), invLen(wiped, AUDIO)], [200, 1]);
})();

// Bounded diagnostics.
(function () {
  var worker = quotaWorker({ alwaysFail: true, clips: 5 });
  for (var i = 0; i < 25; i++) runFetch(worker, get(clipUrl(900000 + i)));
  eq('S20 the audio failure history is bounded at 20 records',
     worker.self.ppSwState.audioFailures.length, 20);
  ok('S20 no record carries a body, a phrase or anything but a key and a message',
     worker.self.ppSwState.audioFailures.every(function (r) {
       return Object.keys(r).sort().join(',') === 'key,message,reason';
     }));
  eq('S20 the counters kept counting past the record bound',
     [worker.self.ppSwState.audio.writeFailures, worker.self.ppSwState.audio.recoveryFailed], [25, 25]);
})();
eq('S24 the exact entry just written is excluded from its own eviction, in both paths',
   [countOf(SW_CODE, '.filter(entry => entry.url !== protectedKey);'),
    countOf(SW_CODE, '.filter(entry => entry.url !== key)')], [1, 1]);
eq('S24 retention classifies by canonical identity but deletes the stored request',
   [countOf(SW_CODE, 'function audioCacheEntries('), countOf(SW_CODE, 'cache.delete(entry.request)'),
    countOf(SW_CODE, 'cache.delete(canonicalKey'), countOf(SW_CODE, 'function deleteAudioEntries(')],
   [1, 1, 0, 1]);
/* Lifetime binding is structural: both follow-up jobs are RETURNED into the one
   write promise that keepAlive() hands to event.waitUntil(), so a worker cannot
   be killed between "the clip was stored" and "the cache was tidied". */
eq('S23 retention and quota recovery run inside the event-bound write chain',
   [countOf(SW_CODE, 'return clip ? afterAudioWrite(key) : undefined;'),
    countOf(SW_CODE, 'return recoverAudioWrite(key, spare, 1);'),
    countOf(SW_CODE, 'keepAlive(event, write);'), countOf(SW_CODE, 'function keepAlive(')], [1, 1, 1, 1]);
ok('S21 retention diagnostics exist and are counters, not URL histories',
   SW_CODE.indexOf('SW_STATE.audio.retentionChecks++') !== -1 &&
   SW_CODE.indexOf('SW_STATE.audioFailures.length < 20') !== -1);
eq('S22 the range diagnostics are all counters',
   Object.keys(W0.self.ppSwState.range).sort(),
   ['bodyReadFailed', 'cacheMiss', 'passthrough', 'synthesized', 'unsatisfiable']);
eq('S22 the audio diagnostics are all counters',
   Object.keys(W0.self.ppSwState.audio).sort(),
   ['recovered', 'recoveryAttempts', 'recoveryFailed', 'retentionChecks', 'trimmed', 'writeFailures']);

// =========================================================================
// L. MLG-4A-08 - legacy query-bearing entries are really deletable
//
// popolsku-audio is versionless: it survives every deploy, so it can still hold
// entries a much older worker stored under a query-bearing URL. Classifying such
// an entry by its canonical path is right; DELETING by that canonical key is not
// - it would remove a different record, or nothing, and the real one would stay
// in the cache outside every bound. These cases exist because the first pass of
// this phase had exactly that defect.
// =========================================================================
function legacyClipUrl(i, query) {
  return clipUrl(i) + (query === undefined ? '?legacy=1' : query);
}
function seedLegacyClips(count) {
  var entries = {};
  for (var i = 0; i < count; i++) {
    var url = legacyClipUrl(i);
    entries[url] = cachedClip(url, new Uint8Array([1, 2, 3]));
  }
  var seed = {}; seed[AUDIO] = entries; return seed;
}
(function () {
  var seed = seedLegacyClips(API.AUDIO_CACHE_MAX_ENTRIES);
  /* A non-MP3 query-bearing entry sits FIRST, among the oldest, so a trim that
     stopped filtering by asset class would take it before any clip. */
  var notes = ORIGIN + '/audio/notes.txt?legacy=1';
  var fresh = clipUrl(999900);
  /* A redundant legacy variant of the very clip about to be written, seeded among
     the OLDEST entries: duplicate storage for bytes the cache is about to hold
     canonically, so the trim is right to reach it. */
  var redundant = legacyClipUrl(999900);
  var ordered = {}; ordered[notes] = typed(ORIGIN + '/audio/notes.txt', { label: 'foreign' });
  ordered[redundant] = cachedClip(redundant, new Uint8Array([1, 2, 3]));
  Object.keys(seed[AUDIO]).forEach(function (k) { ordered[k] = seed[AUDIO][k]; });
  seed[AUDIO] = ordered;
  seed[SHELL] = {}; seed[SHELL][ORIGIN + '/'] = typed(ORIGIN + '/', { label: 'shell' });
  seed['unrelated-tool-cache'] = {};
  seed['unrelated-tool-cache'][ORIGIN + '/keep-me'] = typed(ORIGIN + '/keep-me', { label: 'keep' });
  var worker = makeWorker({ seed: seed, route: audioRoute });
  var before = invLen(worker, AUDIO);
  var run = runFetch(worker, get(fresh));
  var audioCache = worker.caches.caches[AUDIO];
  var remaining = worker.caches.inventory(AUDIO);
  var approved = remaining.filter(function (url) { return /\/audio\/[a-f0-9]+\.mp3/.test(url); });
  eq('L1 the cache really was full of legacy query-bearing clips',
     [before, Object.keys(seed[AUDIO]).length], [API.AUDIO_CACHE_MAX_ENTRIES + 2, API.AUDIO_CACHE_MAX_ENTRIES + 2]);
  eq('L2 the online response still succeeds', [respState(run), respStatus(run)], ['fulfilled', 200]);
  eq('L3 retention brings approved audio entries down to the trim target',
     approved.length, API.AUDIO_CACHE_TRIM_TO);
  eq('L4 the deleted entries are the actual stored query-bearing URLs',
     [audioCache.deletes.length > 0,
      audioCache.deletes.every(function (url) { return url.indexOf('?legacy=1') !== -1; })],
     [true, true]);
  eq('L5 the newly written canonical clip survives',
     audioCache.entries[fresh] !== undefined, true);
  eq('L5 a redundant legacy variant of that same clip was removed, not protected',
     audioCache.entries[redundant] === undefined, true);
  eq('L6 no shell or unrelated cache changed',
     [inv(worker, SHELL), inv(worker, 'unrelated-tool-cache')],
     [[ORIGIN + '/'], [ORIGIN + '/keep-me']]);
  eq('L7 a non-MP3 query-bearing entry inside the audio cache survives',
     audioCache.entries[notes] !== undefined, true);
  eq('L8 deletion never used a canonical key that is not in the cache',
     audioCache.deletes.filter(function (url) { return url.indexOf('?') === -1; }), []);
  eq('L8 every delete really removed something', worker.self.ppSwState.audio.trimmed,
     audioCache.deletes.length);
  eq('L9 no cache was deleted wholesale', worker.caches.deleted, []);
})();
(function () {
  var seed = seedLegacyClips(API.AUDIO_CACHE_MAX_ENTRIES);
  var worker = makeWorker({ seed: seed, route: audioRoute });
  worker.caches.entryDeleteBehavior = function () { return { reject: new Error('delete denied') }; };
  var run = runFetch(worker, get(clipUrl(999901)));
  eq('L10 a delete rejection is contained and never fails the response',
     [respStatus(run), writeState(run), worker.self.ppSwState.audio.trimmed], [200, 'fulfilled', 0]);
  ok('L10 the failure is recorded against the real stored URL',
     worker.self.ppSwState.audioFailures.length > 0 &&
     worker.self.ppSwState.audioFailures[0].key.indexOf('?legacy=1') !== -1);
})();
(function () {
  /* The quota path, over the same legacy shape. */
  var seed = seedLegacyClips(200);
  seed[SHELL] = {}; seed[SHELL][ORIGIN + '/'] = typed(ORIGIN + '/', { label: 'shell' });
  seed['unrelated-tool-cache'] = {};
  seed['unrelated-tool-cache'][ORIGIN + '/keep-me'] = typed(ORIGIN + '/keep-me', { label: 'keep' });
  var fresh = clipUrl(999902);
  var worker = makeWorker({ seed: seed, route: audioRoute });
  worker.caches.putBehavior = function (name, key, response, attempt) {
    return name === AUDIO && attempt === 1 ? { reject: new Error('QuotaExceededError') } : null;
  };
  var run = runFetch(worker, get(fresh));
  var audioCache = worker.caches.caches[AUDIO];
  eq('L11 the online response still reaches the learner', respStatus(run), 200);
  eq('L12 quota recovery evicted a bounded batch of ACTUAL legacy entries',
     [worker.self.ppSwState.audio.trimmed,
      audioCache.deletes.every(function (url) { return url.indexOf('?legacy=1') !== -1; })],
     [API.AUDIO_QUOTA_EVICTION_BATCH, true]);
  eq('L13 the retry happened exactly once',
     audioCache.puts.filter(function (k) { return k === fresh; }).length, 2);
  eq('L14 the new canonical entry is stored',
     [worker.self.ppSwState.audio.recovered, audioCache.entries[fresh] !== undefined], [1, true]);
  eq('L15 no other cache was touched',
     [inv(worker, SHELL), inv(worker, 'unrelated-tool-cache'), worker.caches.deleted],
     [[ORIGIN + '/'], [ORIGIN + '/keep-me'], []]);
  eq('L16 the legacy cache shrank by exactly the evicted batch',
     invLen(worker, AUDIO), 200 - API.AUDIO_QUOTA_EVICTION_BATCH + 1);
})();
(function () {
  /* Fragments are not part of a cache key in the first place: the browser strips
     them before the request exists, so nothing special is needed for them. */
  var url = clipUrl(5);
  eq('L17 a fragment is not part of the stored identity',
     API.canonicalKeyFor(API.parseUrl(url + '#t=10')), url);
  eq('L17 a query variant keeps its own stored identity but one canonical one',
     [API.canonicalKeyFor(API.parseUrl(url + '?legacy=1')), API.isApprovedAudioKey(url)], [url, true]);
})();

// =========================================================================
// A fake DOM, shared by the app-shell and generated-page audio sections
// =========================================================================
function El(tag) {
  this.tagName = String(tag || 'div').toUpperCase();
  this.id = ''; this.className = ''; this.type = ''; this.textContent = '';
  this.hidden = false; this.disabled = false; this.tabIndex = 0;
  this.attrs = {}; this.children = []; this.parentNode = null; this.dataset = {};
  this.listeners = {}; this.focusCount = 0; this.classes = [];
  var self_ = this;
  this.classList = {
    add: function (c) { if (self_.classes.indexOf(c) === -1) self_.classes.push(c); },
    remove: function (c) { self_.classes = self_.classes.filter(function (x) { return x !== c; }); },
    contains: function (c) { return self_.classes.indexOf(c) !== -1; }
  };
}
El.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
El.prototype.getAttribute = function (k) { return this.attrs[k] === undefined ? null : this.attrs[k]; };
El.prototype.removeAttribute = function (k) { delete this.attrs[k]; };
El.prototype.appendChild = function (child) {
  if (child.parentNode) child.parentNode.removeChild(child);
  child.parentNode = this; this.children.push(child); return child;
};
El.prototype.removeChild = function (child) {
  this.children = this.children.filter(function (x) { return x !== child; });
  child.parentNode = null; return child;
};
// Real behaviour, including the throw: a node with no parent cannot have a
// sibling inserted after it, which is why the shipping code guards the call.
El.prototype.insertAdjacentElement = function (position, el) {
  if (position !== 'afterend') throw new Error('unsupported position ' + position);
  var parent = this.parentNode;
  if (!parent) throw new Error('no parent to insert after');
  if (el.parentNode) el.parentNode.removeChild(el);
  var at = parent.children.indexOf(this);
  parent.children.splice(at + 1, 0, el);
  el.parentNode = parent;
  return el;
};
El.prototype.closest = function (selector) {
  var attr = selector.replace(/^\[/, '').replace(/\]$/, ''), node = this;
  while (node) { if (node.getAttribute && node.getAttribute(attr) !== null) return node; node = node.parentNode; }
  return null;
};
El.prototype.addEventListener = function (type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); };
El.prototype.focus = function () { this.focusCount++; if (this.ownerDoc) this.ownerDoc.activeElement = this; };
El.prototype.click = function () {
  var self_ = this;
  /* A browser dispatches no click on a disabled control, and a hidden control
     cannot be clicked or tabbed to at all. Modelling that is what makes
     "the retry is gone when it is hidden" a real assertion. */
  if (this.disabled || this.hidden) return;
  (this.listeners.click || []).forEach(function (fn) {
    fn({ type: 'click', target: self_, stopPropagation: function () {}, preventDefault: function () {} });
  });
};
function makeDocument() {
  var listeners = {}, body = new El('body');
  var doc = {
    body: body, activeElement: null, created: [], listeners: listeners,
    createElement: function (tag) { var el = new El(tag); el.ownerDoc = doc; doc.created.push(el); return el; },
    addEventListener: function (type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    dispatch: function (type, event) { (listeners[type] || []).forEach(function (fn) { fn(event); }); }
  };
  body.ownerDoc = doc;
  return doc;
}
function makeButton(doc, parent, attrs) {
  var btn = doc.createElement('button');
  Object.keys(attrs || {}).forEach(function (k) { btn.setAttribute(k, attrs[k]); });
  parent.appendChild(btn);
  return btn;
}
// A hand-settled thenable, exactly as tests/test_audio_fallback.js uses: the
// suite decides the interleaving of the error event and the play() rejection.
function Thenable() { this.onRejected = null; this.done = false; }
Thenable.prototype['catch'] = function (fn) { this.onRejected = fn; return this; };
Thenable.prototype.then = function (onF, onR) { if (onR) this.onRejected = onR; return this; };
Thenable.prototype.reject = function (err) {
  if (this.done) return;
  this.done = true;
  if (this.onRejected) this.onRejected(err);
};
Thenable.prototype.resolve = function () { this.done = true; };
function FakeAudio(src) {
  this.src = src; this.playbackRate = 1; this.preservesPitch = false;
  this.onended = null; this.onerror = null; this.listeners = {};
  this.pauses = 0; this.playCount = 0; this.promise = null;
  FakeAudio.created.push(this);
}
FakeAudio.created = [];
FakeAudio.prototype.play = function () { this.playCount++; this.promise = new Thenable(); return this.promise; };
FakeAudio.prototype.pause = function () { this.pauses++; };
FakeAudio.prototype.addEventListener = function (type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); };
FakeAudio.prototype.fire = function (type) {
  var handler = this['on' + type];
  if (handler) handler({ type: type });
  (this.listeners[type] || []).forEach(function (fn) { fn({ type: type }); });
};
FakeAudio.prototype.fireError = function () { this.fire('error'); };
FakeAudio.prototype.fireEnded = function () { this.fire('ended'); };
FakeAudio.prototype.rejectPlay = function () { if (this.promise) this.promise.reject({ name: 'NotSupportedError' }); };
function FakeSynth() { this.spoken = []; this.cancels = 0; this.throwOnSpeak = false; }
FakeSynth.prototype.speak = function (u) { if (this.throwOnSpeak) throw new Error('speech unavailable'); this.spoken.push(u); };
FakeSynth.prototype.cancel = function () { this.cancels++; };
FakeSynth.prototype.getVoices = function () { return []; };
function FakeUtterance(text) { this.text = text; this.lang = ''; this.rate = 1; this.voice = null; this.onend = null; this.onerror = null; }

// =========================================================================
// M. MLG-4A-04 - the app-shell audio contract, run out of index.html
// =========================================================================
function extractFunction(src, name) {
  var needle = 'function ' + name + '(';
  var start = src.indexOf(needle);
  if (start === -1) throw new Error('extract: function ' + name + ' not found in index.html');
  if (src.indexOf(needle, start + 1) !== -1) throw new Error('extract: function ' + name + ' declared more than once');
  var open = src.indexOf('{', src.indexOf(')', start));
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
  throw new Error('extract: unbalanced braces for ' + name);
}
function constString(name) {
  var m = INDEX.match(new RegExp('const\\s+' + name + '\\s*=\\s*"([^"]*)"\\s*;'));
  if (!m) throw new Error('extract: ' + name + ' not found in index.html');
  return m[1];
}
var FALLBACK_MSG = constString('AUDIO_FALLBACK_MSG');
var FAILED_MSG = constString('AUDIO_FAILED_MSG');
var RETRY_MSG = constString('AUDIO_RETRY_MSG');
eq('M0 the shared fallback wording', FALLBACK_MSG, "Using your device's voice.");
eq('M0 the shared failure wording', FAILED_MSG, "Audio couldn't play. Check your connection, then try again.");
eq('M0 the shared retry wording', RETRY_MSG, 'Try again');

var SRC = {};
['ppNormalize', 'clearSpeaking', 'ppAudioStatusHost', 'showAudioStatus', 'clearAudioStatus',
 'retryAudio', 'stopAllAudio', 'speakText', 'playPreGenerated', 'speakCardMain', 'speakFallback',
 'currentRate', 'settleAudioManifest'].forEach(function (n) { SRC[n] = extractFunction(INDEX, n); });

var speedsMatch = INDEX.match(/const\s+SPEEDS\s*=\s*(\{[^}]*\})\s*;/);
var SPEEDS = (0, eval)('(' + speedsMatch[1] + ')');
var window = {};
(0, eval)(readFile(ROOT + 'pp-usage.js'));
var PP_USAGE = window.PP_USAGE;
var ppMainAudioText = PP_USAGE.mainAudioText;
var ppHasMainAudio = PP_USAGE.hasMainAudio;

var document = makeDocument();
var synth = new FakeSynth();
var speechSynthesis = synth;
var SpeechSynthesisUtterance = FakeUtterance;
var Audio = FakeAudio;
var voiceHintCalls = 0;
function voiceHint() { voiceHintCalls++; }
var listeningSyncs = 0, roundSyncs = 0;
function syncListeningAudioReadiness() { listeningSyncs++; }
function syncRoundAudioReadiness() { roundSyncs++; }

// module state the extracted functions own
var audioMap = {}, audioManifestStatus = 'ready';
var currentAudio = null, currentUtterance = null, speakBtn = null, plVoice = null;
var audioRetryRequest = null;
var audioStatusEl = null, audioStatusMsgEl = null, audioRetryEl = null, audioStatusOwner = null;
var currentSpeed = 'normal';
var AUDIO_FALLBACK_MSG = FALLBACK_MSG, AUDIO_FAILED_MSG = FAILED_MSG, AUDIO_RETRY_MSG = RETRY_MSG;
Object.keys(SRC).forEach(function (n) { (0, eval)(SRC[n]); });

var CLIP = 'audio/deadbeef.mp3', CLIP_B = 'audio/cafe1234.mp3';
var row, btn, other;
function resetMain(options) {
  options = options || {};
  document = makeDocument();
  row = document.createElement('div');
  document.body.appendChild(row);
  btn = makeButton(document, row, {});
  other = makeButton(document, row, {});
  FakeAudio.created = [];
  synth = new FakeSynth();
  speechSynthesis = synth;
  SpeechSynthesisUtterance = options.noUtteranceClass ? undefined : FakeUtterance;
  window = { PP_USAGE: PP_USAGE };
  if (!options.noSpeech) window.speechSynthesis = synth;
  currentAudio = null; currentUtterance = null; speakBtn = null; plVoice = null;
  audioRetryRequest = null; currentSpeed = 'normal'; voiceHintCalls = 0;
  audioStatusEl = null; audioStatusMsgEl = null; audioRetryEl = null; audioStatusOwner = null;
  audioManifestStatus = 'ready';
  audioMap = { 'kawa': CLIP, 'Gdzie jest apteka?': CLIP_B };
  ppAudioStatusHost();          /* index.html parks the live region at startup */
}
function lastAudio() { return FakeAudio.created[FakeAudio.created.length - 1]; }
function statusText() { return audioStatusMsgEl ? audioStatusMsgEl.textContent : '(no status element)'; }
function statusVisible() { return audioStatusEl ? !audioStatusEl.hidden : false; }
function retryShape() { return [audioRetryEl.hidden, audioRetryEl.disabled, audioRetryEl.tabIndex]; }
function statusFollows(control) {
  var parent = control.parentNode;
  if (!parent) return false;
  return parent.children[parent.children.indexOf(control) + 1] === audioStatusEl;
}
function spokenText(i) { var u = synth.spoken[i]; return u ? u.text : '(nothing was spoken)'; }

// The live region exists before it is ever needed, with the attributes that make
// it one polite announcement rather than two fragments.
resetMain();
eq('M1 the status region is parked in the document at startup',
   [audioStatusEl.parentNode === document.body, audioStatusEl.hidden], [true, true]);
eq('M1 the status region announces politely and atomically',
   [audioStatusEl.getAttribute('role'), audioStatusEl.getAttribute('aria-live'),
    audioStatusEl.getAttribute('aria-atomic')], ['status', 'polite', 'true']);
eq('M1 the retry action is a real button with the shared label',
   [audioRetryEl.tagName, audioRetryEl.type, audioRetryEl.textContent], ['BUTTON', 'button', RETRY_MSG]);
eq('M1 a hidden retry is out of the keyboard order', retryShape(), [true, true, -1]);
eq('M1 the status element is built once', document.created.filter(function (e) { return e.id === 'ppAudioStatus'; }).length, 1);
ppAudioStatusHost();
eq('M1 asking for it again does not build a second one',
   document.created.filter(function (e) { return e.id === 'ppAudioStatus'; }).length, 1);

// 1. A clip that plays says nothing at all.
resetMain();
speakText('kawa', btn);
eq('M2 the pre-generated clip is attempted', [FakeAudio.created.length, lastAudio().src], [1, CLIP]);
eq('M2 a successful attempt shows no status', [statusVisible(), statusText()], [false, '']);
lastAudio().fireEnded();
eq('M2 completion releases the button and stays silent',
   [currentAudio, btn.classList.contains('speaking'), statusVisible()], [null, false, false]);
eq('M2 success is never announced merely because play() was called', synth.spoken.length, 0);

// 2-4. One failed attempt produces exactly one fallback and one announcement.
resetMain();
speakText('kawa', btn);
lastAudio().fireError();
eq('M3 an error event falls back to the device voice', synth.spoken.length, 1);
eq('M3 the fallback speaks the original phrase', spokenText(0), 'kawa');
eq('M3 the fallback is announced with the shared wording', [statusVisible(), statusText()], [true, FALLBACK_MSG]);
eq('M3 the fallback state offers no retry', retryShape(), [true, true, -1]);
eq('M3 the status sits next to the control that failed', statusFollows(btn), true);
lastAudio().rejectPlay();
eq('M4 the second failure channel adds no second fallback', synth.spoken.length, 1);
eq('M4 and no second announcement', statusText(), FALLBACK_MSG);

resetMain();
speakText('kawa', btn);
lastAudio().rejectPlay();
eq('M5 a rejected play() falls back once', [synth.spoken.length, statusText()], [1, FALLBACK_MSG]);
lastAudio().fireError();
eq('M5 a later error event on the same attempt changes nothing', [synth.spoken.length, statusText()], [1, FALLBACK_MSG]);

// 5-6. No clip for the phrase: speech is the first attempt, not a fallback.
resetMain();
speakText('nieznane zdanie', btn);
eq('M6 a phrase with no clip goes straight to the device voice',
   [FakeAudio.created.length, synth.spoken.length, spokenText(0)], [0, 1, 'nieznane zdanie']);
eq('M6 and is not announced as a fallback from a failure', [statusVisible(), statusText()], [false, '']);

resetMain();
settleAudioManifest(null);
eq('M7 an unusable manifest settles without crashing', audioManifestStatus, 'unavailable');
speakText('kawa', btn);
eq('M7 with no manifest the device voice still speaks', [synth.spoken.length, spokenText(0)], [1, 'kawa']);
eq('M7 and nothing is announced as a failure', statusVisible(), false);
resetMain();
settleAudioManifest({ entries: { a: { pl: 'kawa', file: 'audio/deadbeef.mp3' } } });
eq('M8 a usable manifest settles ready', [audioManifestStatus, audioMap['kawa']], ['ready', 'audio/deadbeef.mp3']);

// 7-9. The terminal state: nothing can make a sound.
resetMain({ noSpeech: true });
speakText('kawa', btn);
lastAudio().fireError();
eq('M9 no speech synthesis turns a failed clip into a visible failure',
   [statusVisible(), statusText()], [true, FAILED_MSG]);
eq('M9 the retry action is keyboard reachable', retryShape(), [false, false, 0]);
eq('M9 the failure is tied to the control that failed',
   btn.getAttribute('aria-describedby'), 'ppAudioStatusMsg');
eq('M9 the failure state steals no focus', [document.activeElement, btn.focusCount], [null, 0]);
eq('M9 nothing was spoken', synth.spoken.length, 0);

resetMain({ noSpeech: true });
speakText('brak nagrania', btn);
eq('M10 a phrase with no clip and no speech reaches the same failure',
   [statusVisible(), statusText(), retryShape()], [true, FAILED_MSG, [false, false, 0]]);

resetMain({ noUtteranceClass: true });
speakText('kawa', btn);
lastAudio().fireError();
eq('M11 a speech engine that cannot build an utterance is terminal, not silent',
   [statusVisible(), statusText()], [true, FAILED_MSG]);

resetMain();
speakText('kawa', btn);
lastAudio().fireError();
eq('M12 the fallback is announced first', statusText(), FALLBACK_MSG);
synth.spoken[0].onerror({ type: 'error' });
eq('M12 an utterance error replaces it with the failure state',
   [statusVisible(), statusText(), retryShape()], [true, FAILED_MSG, [false, false, 0]]);
eq('M12 exactly one message is present at a time',
   [audioStatusMsgEl.textContent === FAILED_MSG, audioStatusEl.children.length], [true, 2]);
eq('M12 the failed utterance released the button', speakBtn, null);

resetMain();
synth.throwOnSpeak = true;
speakText('kawa', btn);
lastAudio().fireError();
eq('M13 a speak() that throws is terminal, not silent', [statusVisible(), statusText()], [true, FAILED_MSG]);

// 10. A normal utterance completion clears nothing but the speaking state.
resetMain();
speakText('nieznane', btn);
synth.spoken[0].onend({ type: 'end' });
eq('M14 a completed utterance releases the button and leaves no status',
   [speakBtn, currentUtterance, statusVisible()], [null, null, false]);

// 11-13. Retry.
resetMain({ noSpeech: true });
speakText('kawa', btn);
lastAudio().fireError();
eq('M15 the failure is showing before retry', statusText(), FAILED_MSG);
audioRetryEl.click();
eq('M15 retry re-attempts the same phrase through the same clip',
   [FakeAudio.created.length, lastAudio().src], [2, CLIP]);
eq('M15 retry clears the previous failure before starting', statusVisible(), false);
eq('M15 retry hands focus back to the control it belongs to',
   [btn.focusCount, document.activeElement === btn], [1, true]);
eq('M15 retry starts exactly one attempt', lastAudio().playCount, 1);
eq('M15 retry creates no overlapping audio',
   [FakeAudio.created[0].playCount, FakeAudio.created[0] === currentAudio, currentAudio === lastAudio()],
   [1, false, true]);
lastAudio().fireEnded();
eq('M16 a successful retry leaves no stale failure', [statusVisible(), statusText()], [false, '']);

resetMain({ noSpeech: true });
speakText('Gdzie jest apteka?', other);
lastAudio().fireError();
audioRetryEl.click();
eq('M15b retry replays the phrase that failed, not another one',
   [FakeAudio.created.length, lastAudio().src, audioRetryRequest.text],
   [2, CLIP_B, 'Gdzie jest apteka?']);
eq('M15b and it belongs to the control that failed', audioRetryRequest.btn === other, true);

resetMain({ noSpeech: true });
speakText('kawa', btn);
lastAudio().fireError();
audioRetryEl.click();
lastAudio().fireError();
eq('M17 a retry that fails again reaches the same accessible state',
   [statusVisible(), statusText(), retryShape()], [true, FAILED_MSG, [false, false, 0]]);
eq('M17 one retry is one attempt, not a loop', FakeAudio.created.length, 2);
audioRetryEl.click();
eq('M17 each activation is one further bounded attempt', FakeAudio.created.length, 3);

resetMain();
speakText('kawa', btn);
lastAudio().fireError();
eq('M18 the device-voice fallback is showing', statusText(), FALLBACK_MSG);
audioRetryEl.click();
eq('M18 a hidden retry cannot be activated',
   [FakeAudio.created.length, synth.spoken.length], [1, 1]);

// 14. Rapid switching and stale callbacks.
resetMain();
speakText('kawa', btn);
var first = lastAudio();
speakText('Gdzie jest apteka?', other);
var second = lastAudio();
eq('M19 the previous clip is stopped and superseded',
   [first.pauses, currentAudio === second, FakeAudio.created.length], [1, true, 2]);
first.fireError();
eq('M19 a stale error speaks nothing', synth.spoken.length, 0);
eq('M19 a stale error announces nothing', [statusVisible(), statusText()], [false, '']);
eq('M19 a stale error does not release the new attempt', currentAudio === second, true);
second.fireError();
eq('M19 the live attempt still falls back exactly once',
   [synth.spoken.length, spokenText(0), statusText()], [1, 'Gdzie jest apteka?', FALLBACK_MSG]);
eq('M19 the announcement belongs to the new control', statusFollows(other), true);

resetMain({ noSpeech: true });
speakText('kawa', btn);
var stale = lastAudio();
speakText('Gdzie jest apteka?', other);
stale.fireError();
eq('M20 a stale error never restores an old retry', [statusVisible(), retryShape()], [false, [true, true, -1]]);

resetMain();
speakText('nieznane', btn);
var staleUtterance = synth.spoken[0];
speakText('inne nieznane', other);
staleUtterance.onerror({ type: 'error' });
eq('M21 a stale utterance error announces no failure', [statusVisible(), statusText()], [false, '']);
staleUtterance.onend({ type: 'end' });
eq('M21 a stale utterance completion does not clear the new attempt',
   [speakBtn === other, other.classList.contains('speaking')], [true, true]);

// 15-16. Stop boundaries.
resetMain({ noSpeech: true });
speakText('kawa', btn);
lastAudio().fireError();
stopAllAudio();
eq('M22 stopAllAudio clears the failure state',
   [statusVisible(), statusText(), retryShape()], [false, '', [true, true, -1]]);
eq('M22 stopAllAudio releases the description on the control', btn.getAttribute('aria-describedby'), null);
audioRetryEl.click();
eq('M22 nothing is left for retry to replay after a stop', FakeAudio.created.length, 1);

resetMain();
speakText('kawa', btn);
lastAudio().fireError();
eq('M23 the fallback status is showing', statusVisible(), true);
stopAllAudio();
eq('M23 leaving the activity clears it and cancels speech',
   [statusVisible(), synth.cancels > 0], [false, true]);

// 17. Template cards still play nothing at all.
resetMain();
speakCardMain({ cardType: 'template', pl: 'Gdzie jest ...?', audioText: 'Gdzie jest ...?' }, btn);
eq('M24 a template card plays nothing and announces nothing',
   [FakeAudio.created.length, synth.spoken.length, statusVisible()], [0, 0, false]);
resetMain();
speakCardMain({ intro: true, pl: 'kawa' }, btn);
eq('M24 a podcast intro card is unchanged too',
   [FakeAudio.created.length, synth.spoken.length, statusVisible()], [0, 0, false]);
resetMain();
speakCardMain({ pl: 'kawa', en: 'coffee' }, btn);
eq('M24 an ordinary card still plays its clip', [FakeAudio.created.length, lastAudio().src], [1, CLIP]);

// 18. The failure path touches nothing but audio.
resetMain({ noSpeech: true });
var scoreProbe = { score: 3, index: 7 };
listeningSyncs = 0; roundSyncs = 0;
speakText('kawa', btn);
lastAudio().fireError();
eq('M25 an audio failure changes no activity state', [scoreProbe.score, scoreProbe.index], [3, 7]);
eq('M25 an audio failure re-renders nothing', [listeningSyncs, roundSyncs], [0, 0]);
eq('M25 an audio failure moves no focus', [document.activeElement, btn.focusCount, other.focusCount], [null, 0, 0]);
eq('M25 the playback rate contract is untouched', [currentRate(), SPEEDS.normal, SPEEDS.slow], [1, 1, 0.7]);
resetMain();
currentSpeed = 'slow';
speakText('kawa', btn);
eq('M26 the slow toggle still reaches the clip', lastAudio().playbackRate, 0.7);
lastAudio().fireError();
eq('M26 and the device voice', synth.spoken[0].rate, 0.7);
eq('M26 the fallback still asks for Polish', synth.spoken[0].lang, 'pl-PL');

// =========================================================================
// G. MLG-4A-04 - the generated-page contract, run out of a committed page
// =========================================================================
(function () {
  var open = BUILD.indexOf('PLAYER_JS = """');
  var start = open + 'PLAYER_JS = """'.length;
  var end = BUILD.indexOf('"""', start);
  var generatorPlayer = BUILD.slice(start, end);
  var scriptOpen = GEN_PAGE.lastIndexOf('<script>');
  var scriptEnd = GEN_PAGE.indexOf('</script>', scriptOpen);
  var pagePlayer = GEN_PAGE.slice(scriptOpen + '<script>'.length, scriptEnd);
  eq('G1 the committed page carries exactly the generator runtime, byte for byte',
     pagePlayer === generatorPlayer, true);
  PLAYER_SRC = pagePlayer;
})();
var PLAYER_SRC;
(function () {
  var open = BUILD.indexOf('PLAYER_JS = """');
  PLAYER_SRC = BUILD.slice(open + 'PLAYER_JS = """'.length, BUILD.indexOf('"""', open + 20));
})();
eq('G1 the generated runtime uses the same three learner-facing strings as the app shell',
   [countOf(PLAYER_SRC, '"' + FALLBACK_MSG + '"'), countOf(PLAYER_SRC, '"' + FAILED_MSG + '"'),
    countOf(PLAYER_SRC, '"' + RETRY_MSG + '"')], [1, 1, 1]);
ok('G1 the generated runtime never recovers Polish by parsing the accessible name',
   PLAYER_SRC.indexOf('aria-label') === -1 && PLAYER_SRC.indexOf('data-pl') !== -1);

// Every committed generated page: markup contract.
(function () {
  /* The page list is the worker's own generated-route inventory, so this
     section and the offline-navigation contract can never disagree about which
     pages exist. */
  var inventory = (SW_SRC.match(/GENERATED_PAGE_ASSETS = \[([\s\S]*?)\];/) || ['', ''])[1];
  var pages = [];
  inventory.replace(/"\.\/([^"]*)"/g, function (whole, route) { pages.push(route + 'index.html'); return whole; });
  eq('G2 the inventory names every committed generated page', pages.length, 33);
  var withAudio = 0, buttons = 0, badPl = [], badLabel = [], withPlayer = 0;
  pages.forEach(function (relative) {
    var markup = readFile(ROOT + relative);
    var count = countOf(markup, '<button class="say" data-audio=');
    if (countOf(markup, '(function(){\n  var FALLBACK_MSG') === 1) withPlayer++;
    if (!count) return;
    withAudio++;
    buttons += count;
    var re = /<button class="say" data-audio="([^"]*)" data-pl="([^"]*)" type="button" aria-label="([^"]*)">/g;
    var matched = 0, m;
    while ((m = re.exec(markup)) !== null) {
      matched++;
      if (!m[2] || m[2].indexOf('<') !== -1) badPl.push(relative);
      if (m[3].indexOf('Play Polish') !== 0 || m[3].indexOf(': ') === -1) badLabel.push(relative);
    }
    if (matched !== count) badPl.push(relative + ' (attribute order)');
  });
  eq('G2 every generated pronunciation button carries a URL, Polish text and a name',
     [badPl.length, badLabel.length], [0, 0]);
  eq('G2 the audio pages are the 29 the generator owns', withAudio, 29);
  eq('G2 the shared runtime ships on exactly those pages', withPlayer, 29);
  ok('G2 every audio button was checked', buttons >= 380);
  INFO.push(withAudio + ' generated pages carry ' + buttons + ' pronunciation buttons, each with data-pl fallback text');
})();

// The runtime itself, driven against a fake DOM.
var genDoc, genWindow, genSynth, genRow, genA, genB, genStatus, genMsg, genRetry;
function runPlayer(options) {
  options = options || {};
  genDoc = makeDocument();
  genSynth = new FakeSynth();
  genWindow = {};
  if (!options.noSpeech) {
    genWindow.speechSynthesis = genSynth;
    genWindow.SpeechSynthesisUtterance = options.noUtteranceClass ? undefined : FakeUtterance;
  }
  FakeAudio.created = [];
  genRow = genDoc.createElement('div');
  genDoc.body.appendChild(genRow);
  genA = makeButton(genDoc, genRow, { 'data-audio': '/audio/aaa.mp3', 'data-pl': 'Dzień dobry',
                                      'aria-label': 'Play Polish example: Dzień dobry' });
  genB = makeButton(genDoc, genRow, { 'data-audio': '/audio/bbb.mp3', 'data-pl': 'Do widzenia',
                                      'aria-label': 'Play Polish example: Do widzenia' });
  genA.className = 'say'; genB.className = 'say';
  (new Function('document', 'window', 'Audio', PLAYER_SRC))(genDoc, genWindow, FakeAudio);
}
function clickGen(button) {
  genDoc.dispatch('click', { target: button, stopPropagation: function () {}, preventDefault: function () {} });
  refreshGenStatus();
}
function refreshGenStatus() {
  genStatus = null; genMsg = null; genRetry = null;
  genDoc.created.forEach(function (el) {
    if (el.id === 'pp-audio-status') genStatus = el;
    if (el.id === 'pp-audio-status-msg') genMsg = el;
    if (el.id === 'pp-audio-retry') genRetry = el;
  });
}
function genStatusText() { return genMsg ? genMsg.textContent : '(no status element)'; }
function genVisible() { return genStatus ? !genStatus.hidden : false; }
function genRetryShape() { return genRetry ? [genRetry.hidden, genRetry.disabled, genRetry.tabIndex] : 'no-retry'; }
function playingMark(button) { return button.dataset.playing === '1'; }
function genSpoken(i) { var u = genSynth.spoken[i]; return u ? u.text : '(nothing was spoken)'; }

runPlayer();
clickGen(genA);
eq('G3 a click starts that button\'s clip', [FakeAudio.created.length, lastAudio().src], [1, '/audio/aaa.mp3']);
eq('G3 the control shows it is playing', playingMark(genA), true);
eq('G3 a successful attempt announces nothing', genVisible(), false);
lastAudio().fire('ended');
eq('G3 completion clears the playing marker', playingMark(genA), false);
eq('G3 completion still announces nothing', [genVisible(), genSynth.spoken.length], [false, 0]);

runPlayer();
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
eq('G4 a failed clip falls back to the device voice with the page\'s own Polish text',
   [genSynth.spoken.length, genSpoken(0)], [1, 'Dzień dobry']);
eq('G4 the fallback uses the shared wording', [genVisible(), genStatusText()], [true, FALLBACK_MSG]);
eq('G4 the fallback offers no retry', genRetryShape(), [true, true, -1]);
eq('G4 the status is placed next to the control that failed',
   genRow.children[genRow.children.indexOf(genA) + 1] === genStatus, true);
lastAudio().rejectPlay();
eq('G5 the second failure channel adds no second fallback', genSynth.spoken.length, 1);

runPlayer();
clickGen(genA);
lastAudio().rejectPlay();
refreshGenStatus();
eq('G6 a rejected play() falls back exactly once',
   [genSynth.spoken.length, genStatusText()], [1, FALLBACK_MSG]);
lastAudio().fire('error');
eq('G6 a later error event changes nothing', genSynth.spoken.length, 1);

runPlayer({ noSpeech: true });
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
eq('G7 with no speech synthesis a generated page shows the shared failure',
   [genVisible(), genStatusText()], [true, FAILED_MSG]);
eq('G7 the retry action is keyboard reachable', genRetryShape(), [false, false, 0]);
eq('G7 the failure is tied to the control', genA.getAttribute('aria-describedby'), 'pp-audio-status-msg');
eq('G7 the failure state steals no focus', [genDoc.activeElement, genA.focusCount], [null, 0]);
eq('G7 the playing marker was cleared as well', playingMark(genA), false);

runPlayer({ noUtteranceClass: true });
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
eq('G8 an unusable speech API is terminal, not silent', [genVisible(), genStatusText()], [true, FAILED_MSG]);

runPlayer();
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
genSynth.spoken[0].onerror({ type: 'error' });
refreshGenStatus();
eq('G9 an utterance error replaces the fallback with the failure state',
   [genVisible(), genStatusText(), genRetryShape()], [true, FAILED_MSG, [false, false, 0]]);
eq('G9 exactly one message is present', genStatus.children.length, 2);

runPlayer({ noSpeech: true });
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
genRetry.click();
refreshGenStatus();
eq('G10 retry replays the same phrase from the same clip',
   [FakeAudio.created.length, lastAudio().src], [2, '/audio/aaa.mp3']);
eq('G10 retry clears the previous failure first', genVisible(), false);
eq('G10 retry hands focus back to the control', [genA.focusCount, genDoc.activeElement === genA], [1, true]);
lastAudio().fire('ended');
refreshGenStatus();
eq('G11 a recovered retry leaves no stale status', [genVisible(), playingMark(genA)], [false, false]);

runPlayer({ noSpeech: true });
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
genRetry.click();
lastAudio().fire('error');
refreshGenStatus();
eq('G12 a retry that fails again reaches the same accessible state',
   [genVisible(), genStatusText(), genRetryShape()], [true, FAILED_MSG, [false, false, 0]]);
eq('G12 one activation is one attempt', FakeAudio.created.length, 2);

runPlayer();
clickGen(genA);
var genFirst = lastAudio();
clickGen(genB);
var genSecond = lastAudio();
refreshGenStatus();
eq('G13 switching stops the old clip and marks only the new control',
   [genFirst.pauses, playingMark(genA), playingMark(genB)], [1, false, true]);
eq('G13 switching cancels any speech in flight', genSynth.cancels > 0, true);
genFirst.fire('error');
refreshGenStatus();
eq('G13 a stale error speaks nothing', genSynth.spoken.length, 0);
eq('G13 a stale error announces nothing', genVisible(), false);
eq('G13 a stale error does not clear the new control\'s playing marker', playingMark(genB), true);
genSecond.fire('error');
refreshGenStatus();
eq('G13 the live attempt still falls back once, for its own phrase',
   [genSynth.spoken.length, genSpoken(0), genStatusText()], [1, 'Do widzenia', FALLBACK_MSG]);

runPlayer({ noSpeech: true });
clickGen(genA);
var genStale = lastAudio();
clickGen(genB);
genStale.fire('error');
refreshGenStatus();
eq('G14 a stale error never restores an old retry', [genVisible(), genRetryShape()], [false, [true, true, -1]]);

runPlayer();
clickGen(genA);
lastAudio().fire('error');
refreshGenStatus();
var genStaleUtterance = genSynth.spoken[0];
clickGen(genB);
genStaleUtterance.onerror({ type: 'error' });
refreshGenStatus();
eq('G15 a stale utterance error announces nothing for the new control',
   [genVisible(), playingMark(genB)], [false, true]);
genStaleUtterance.onend({ type: 'end' });
eq('G15 a stale utterance completion does not clear the new marker', playingMark(genB), true);

/* The markup below is what build_pages.pronunciation_button() emits for a phrase
   the audio manifest does not cover. It is pinned as MISSING_MAPPING_BUTTON in
   tests/test_build_pages.py, which asserts the generator really produces it, so
   the two sides describe one shape rather than two guesses. Nothing here edits an
   otherwise mapped button into a blank one: the attributes are parsed out of the
   generator's own emitted string. */
var GENERATED_MISSING_MAPPING_BUTTON =
  '<button class="say" data-audio="" data-pl="Nowe zdanie." type="button" ' +
  'aria-label="Play Polish example: Nowe zdanie.">';
function attributesOf(markup) {
  var out = {}, re = /([a-zA-Z-]+)="([^"]*)"/g, m;
  while ((m = re.exec(markup)) !== null) out[m[1]] = m[2];
  return out;
}
(function () {
  var attrs = attributesOf(GENERATED_MISSING_MAPPING_BUTTON);
  eq('G16 the generator emits a control even with no clip, with a blank URL',
     [attrs['data-audio'], attrs['data-pl'], attrs['type'], attrs['aria-label']],
     ['', 'Nowe zdanie.', 'button', 'Play Polish example: Nowe zdanie.']);
  /* And the generator source really is unconditional now: the old `if a else ""`
     dropped the control entirely, which is the defect this closes. */
  ok('G16 the generator no longer drops the control when a mapping is missing',
     BUILD.indexOf('def pronunciation_button(') !== -1 &&
     BUILD.indexOf('audio_idx.get(spoken, "")') !== -1 &&
     BUILD.indexOf('if a else ""') === -1);
  ok('G16 and it still never invents a URL',
     BUILD.indexOf('data-audio="{esc(url)}"') !== -1);
})();
function buildEmittedButton(doc, parent, markup) {
  var attrs = attributesOf(markup), btn = doc.createElement('button');
  Object.keys(attrs).forEach(function (name) {
    if (name === 'class') btn.className = attrs[name];
    else if (name === 'type') btn.type = attrs[name];
    else btn.setAttribute(name, attrs[name]);
  });
  parent.appendChild(btn);
  return btn;
}

runPlayer();
var emitted = buildEmittedButton(genDoc, genRow, GENERATED_MISSING_MAPPING_BUTTON);
clickGen(emitted);
refreshGenStatus();
eq('G16 the emitted blank-URL control speaks its own Polish directly',
   [FakeAudio.created.length, genSynth.spoken.length, genSpoken(0)], [0, 1, 'Nowe zdanie.']);
eq('G16 and it is not announced as a fallback from a failure', genVisible(), false);
genSynth.spoken[0].onend({ type: 'end' });
eq('G16 completion clears the control cleanly', [emitted.dataset.playing === '1', genVisible()], [false, false]);

runPlayer({ noSpeech: true });
var emittedNoSpeech = buildEmittedButton(genDoc, genRow, GENERATED_MISSING_MAPPING_BUTTON);
clickGen(emittedNoSpeech);
refreshGenStatus();
eq('G17 the emitted blank-URL control with no speech reaches the shared failure',
   [genVisible(), genStatusText(), genRetryShape()], [true, FAILED_MSG, [false, false, 0]]);
eq('G17 the failure is tied to that control', emittedNoSpeech.getAttribute('aria-describedby'), 'pp-audio-status-msg');
genRetry.click();
refreshGenStatus();
eq('G17 retry repeats the same phrase, still with no clip to try',
   [FakeAudio.created.length, genVisible(), genStatusText()], [0, true, FAILED_MSG]);

runPlayer();
var emittedRetry = buildEmittedButton(genDoc, genRow, GENERATED_MISSING_MAPPING_BUTTON);
clickGen(emittedRetry);
genSynth.spoken[0].onerror({ type: 'error' });
refreshGenStatus();
eq('G17 a speech error on a clipless phrase is terminal, not silent',
   [genVisible(), genStatusText()], [true, FAILED_MSG]);
genRetry.click();
refreshGenStatus();
eq('G17 retry speaks the same phrase again', [genSynth.spoken.length, genSpoken(1)], [2, 'Nowe zdanie.']);

/* The hand-set variant stays as a pure runtime case: a mapped control whose URL
   is cleared at runtime must behave the same way. */
runPlayer();
genA.setAttribute('data-audio', '');
clickGen(genA);
refreshGenStatus();
eq('G17 a blank URL on any control goes straight to the device voice',
   [FakeAudio.created.length, genSynth.spoken.length, genSpoken(0)], [0, 1, 'Dzień dobry']);

runPlayer();
clickGen(genA);
refreshGenStatus();
eq('G18 the generated status region has the same live-region contract as the app shell',
   [genStatus.getAttribute('role'), genStatus.getAttribute('aria-live'), genStatus.getAttribute('aria-atomic')],
   ['status', 'polite', 'true']);
eq('G18 the generated retry carries the same label', genRetry.textContent, RETRY_MSG);
eq('G18 the generated retry starts out of the keyboard order', genRetryShape(), [true, true, -1]);

// =========================================================================
// W. Shared wording, and the safeguards this phase must not move
// =========================================================================
eq('W1 the app shell states each learner-facing audio string exactly once',
   [countOf(INDEX_CODE, '"' + FALLBACK_MSG + '"'), countOf(INDEX_CODE, '"' + FAILED_MSG + '"'),
    countOf(INDEX_CODE, '"' + RETRY_MSG + '"')], [1, 1, 1]);
(function () {
  var page = readFile(ROOT + GEN_PAGE_PATH);
  eq('W1 a generated page states them exactly once too',
     [countOf(page, FALLBACK_MSG), countOf(page, FAILED_MSG), countOf(page, '"' + RETRY_MSG + '"')], [1, 1, 1]);
})();
ok('W2 no second, competing audio failure message was introduced',
   countOf(INDEX, "Audio couldn't") === 1 && countOf(BUILD, "Audio couldn't") === 1);
ok('W3 the failure message claims nothing it cannot know',
   FAILED_MSG.indexOf('offline') === -1 && FAILED_MSG.indexOf('Offline') === -1 &&
   FALLBACK_MSG.indexOf('offline') === -1);
ok('W4 the existing one-time voice hint is untouched',
   INDEX.indexOf("Playing with your device's fallback voice") !== -1 &&
   countOf(INDEX, 'function voiceHint(') === 1);

eq('W5 APP_VERSION is the 8.5 release', (INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1], '8.5');
eq('W5 the shell cache is the current shell revision',
   (SW_SRC.match(/const CACHE\s*=\s*"([^"]+)"/) || [])[1], 'popolsku-v60');
eq('W5 the audio cache name is unchanged',
   (SW_SRC.match(/const AUDIO_CACHE\s*=\s*"([^"]+)"/) || [])[1], 'popolsku-audio');
eq('W5 the storage schema is unchanged',
   (MIGRATE.match(/SCHEMA_VERSION\s*=\s*(\d+)/) || [])[1], '2');
eq('W5 the content migration revision is unchanged',
   (MIGRATE.match(/CONTENT_MIGRATION_REVISION\s*=\s*(\d+)/) || [])[1], '2');

ok('W6 there is still no automatic skipWaiting or clients.claim',
   SW_CODE.indexOf('skipWaiting') === -1 && SW_CODE.indexOf('clients.claim') === -1);
ok('W6 install is still not one all-or-nothing transaction', SW_CODE.indexOf('addAll') === -1);
ok('W6 every application read still names its cache', SW_CODE.indexOf('caches.match(') === -1);
eq('W6 required and optional precache are still separate',
   [countOf(SW_CODE, 'const REQUIRED_ASSETS'), countOf(SW_CODE, 'const OPTIONAL_ASSETS'),
    countOf(SW_CODE, 'function precacheRequired('), countOf(SW_CODE, 'function precacheOptional(')],
   [1, 1, 1, 1]);
eq('W6 the shell cleanup matcher is still numeric-only',
   (SW_SRC.match(/SHELL_CACHE_PATTERN\s*=\s*(\/[^;]+\/)/) || [])[1], '/^popolsku-v[0-9]+$/');
eq('W6 category-aware media validation still gates every write',
   [countOf(SW_CODE, 'function isCacheableResponse('), countOf(SW_CODE, 'function hasExpectedMediaType('),
    countOf(SW_CODE, 'return hasExpectedMediaType(res, key);'),
    countOf(SW_CODE, 'isCacheableResponse(hit, key)')], [1, 1, 1, 1]);
eq('W6 the generated-route inventory is unchanged',
   (SW_SRC.match(/GENERATED_PAGE_ASSETS = \[([\s\S]*?)\]/) || ['', ''])[1].split('"./').length - 1, 33);
ok('W6 the generated deep-link redirect is unchanged',
   SW_CODE.indexOf('Response.redirect(ROOT_KEY, 302)') !== -1);
ok('W6 install-state authority is still runtime-only',
   INDEX_CODE.indexOf('matchMedia("(display-mode: standalone)")') !== -1 &&
   INDEX_CODE.indexOf('read().installed') === -1);
(function () {
  var worker = makeWorker();
  eq('W7 no request class started being intercepted by this phase',
     [worker.api.classifyRequest(new FakeRequest(ORIGIN + '/sitemap.xml')),
      worker.api.classifyRequest(new FakeRequest('https://example.com/x.mp3')),
      worker.api.classifyRequest(new FakeRequest(ORIGIN + '/audio/ab12ef34.mp3')),
      worker.api.classifyRequest(new FakeRequest(ORIGIN + '/', { mode: 'navigate' }))],
     ['unknown', 'cross-origin', 'audio', 'root-navigation']);
  eq('W7 first install still takes over nobody',
     [worker.self.skipWaitingCalls, worker.self.claimCalls], [0, 0]);
})();
(function () {
  var manifest = readFile(ROOT + 'audio-manifest.json');
  var parsed = JSON.parse(manifest);
  var files = {}, ids = Object.keys(parsed.entries);
  ids.forEach(function (id) { files[parsed.entries[id].file] = true; });
  eq('W8 the audio manifest identity is unchanged',
     [ids.length, Object.keys(files).length], [3377, 3377]);
})();

// =========================================================================
// P. MLG-4A-08 - the persistent-storage request stays best effort
// =========================================================================
var A2HS_SOURCE = (function () {
  var at = INDEX.indexOf('const PP_A2HS = (function(){');
  return INDEX.slice(at, INDEX.indexOf('})();', at) + 4);
})();
var A2HS_FACTORY = Function('document', 'window', 'navigator', 'localStorage', 'matchMedia', 'location',
  'URLSearchParams', 'show', 'ppUseInvokerForNextScreen', 'ppCloseSiteMenu', 'setTimeout', 'Promise',
  A2HS_SOURCE + '\nreturn PP_A2HS;');
function PEl(id) { this.id = id; this.hidden = false; this.disabled = false; this.tabIndex = 0; this.attrs = {}; this.textContent = ''; }
PEl.prototype.setAttribute = function (k, v) { this.attrs[k] = String(v); };
PEl.prototype.getAttribute = function (k) { return this.attrs[k] === undefined ? null : this.attrs[k]; };
PEl.prototype.remove = function () { this.removed = true; };
function PStore() { this.data = {}; }
PStore.prototype.getItem = function (k) { return this.data[k] === undefined ? null : this.data[k]; };
PStore.prototype.setItem = function (k, v) { this.data[k] = String(v); };
PStore.prototype.removeItem = function (k) { delete this.data[k]; };

/* Unhandled-rejection detector. Every promise this section hands to the shipping
   code is created here, so any rejection that nothing in the shipping code
   handles is visible: a promise that settles rejected and was never given a
   rejection handler is counted. That is what "no branch creates an unhandled
   rejection" has to mean in a suite that drains its own microtasks. */
var UNHANDLED = [];
function TrackedP(executor) { P.call(this, executor); }
TrackedP.prototype = Object.create(P.prototype);
TrackedP.prototype.constructor = TrackedP;
function tracked(value, mode) {
  var p = new P(function (resolve, reject) {
    if (mode === 'reject') reject(value); else resolve(value);
  });
  var handled = false;
  var realThen = p.then;
  p.then = function (onOk, onErr) {
    if (typeof onErr === 'function') handled = true;
    var next = realThen.call(this, onOk, onErr);
    next.parentTracked = p;
    return next;
  };
  p['catch'] = function (onErr) { handled = true; return this.then(undefined, onErr); };
  p.check = function () {
    if (p.state === 'rejected' && !handled) UNHANDLED.push('rejected promise with no handler');
  };
  UNHANDLED.pending = UNHANDLED.pending || [];
  UNHANDLED.pending.push(p);
  return p;
}
function unhandledCount() {
  (UNHANDLED.pending || []).forEach(function (p) { p.check(); });
  return UNHANDLED.length;
}

/* One synthetic navigator.storage. Every switch below models a real failure mode
   a browser, a locked-down context or a partial polyfill can present. */
function storageEnv(options) {
  options = options || {};
  var calls = { persisted: 0, persist: 0 };
  var ids = {};
  ['siteInstallItem', 'siteInstall', 'siteInstallDetail', 'siteInstallStatus', 'siteMenuButton',
   'ppBanner', 'ppNative'].forEach(function (id) { ids[id] = new PEl(id); });
  var created = [];
  var doc = {
    body: { appendChild: function (x) { created.push(x); } },
    getElementById: function (id) { return ids[id] || null; },
    querySelectorAll: function () { return []; },
    addEventListener: function () {},
    createElement: function () { return new PEl('created'); }
  };
  var storage = null;
  if (options.storage === 'missing') storage = undefined;
  else if (options.storage === 'partial') storage = { persist: function () { return P.resolve(true); } };
  else if (options.storage === 'not-callable') storage = { persist: 1, persisted: 2 };
  else {
    storage = {};
    if (options.persistedGetterThrows) {
      Object.defineProperty(storage, 'persisted', { get: function () { throw new Error('persisted getter'); } });
    } else {
      storage.persisted = function () {
        calls.persisted++;
        if (options.persistedThrows) throw new Error('persisted threw');
        if (options.persistedReturns !== undefined) return options.persistedReturns;   /* plain value */
        return tracked(options.persistedValue === true, options.persistedRejects ? 'reject' : 'resolve');
      };
    }
    if (options.persistGetterThrows) {
      Object.defineProperty(storage, 'persist', { get: function () { throw new Error('persist getter'); } });
    } else {
      storage.persist = function () {
        calls.persist++;
        if (options.persistThrows) throw new Error('persist threw');
        if (options.persistReturns !== undefined) return options.persistReturns;       /* plain value */
        return tracked(options.persistValue === true, options.persistRejects ? 'reject' : 'resolve');
      };
    }
  }
  var nav = { userAgent: 'Desktop', platform: 'MacIntel', maxTouchPoints: 0, standalone: false };
  if (options.storageGetterThrows) {
    Object.defineProperty(nav, 'storage', { get: function () { throw new Error('storage access denied'); } });
  } else {
    nav.storage = storage;
  }
  var win = { navigator: nav, addEventListener: function () {} };
  function Params(search) { this.search = search || ''; }
  Params.prototype.has = function () { return false; };
  var api = A2HS_FACTORY(doc, win, nav, new PStore(), function () { return { matches: false }; },
    { search: '' }, Params, function () {}, function () {}, function () { return true; }, function () {}, P);
  api.init();
  drain();
  return { api: api, calls: calls, win: win, created: created, ids: ids };
}
function askPersist(env) {
  env.api.bump(99);          /* engagement threshold reached: the one moment it asks */
  drain();
  return env.win.ppStorageState;
}
function persistCase(label, options, expected, extra) {
  var env = storageEnv(options);
  var state = askPersist(env);
  var actual = { supported: state.supported, persisted: state.persisted,
                 requested: state.requested, granted: state.granted, error: state.error };
  /* `requested` is a boolean the shipping state initialises to false; everything
     else starts as null, meaning "not answered". */
  var defaults = { supported: null, persisted: null, requested: false, granted: null, error: null };
  var wanted = {};
  Object.keys(actual).forEach(function (k) {
    wanted[k] = expected[k] === undefined ? defaults[k] : expected[k];
  });
  eq('P ' + label, actual, wanted);
  eq('P ' + label + ' - nothing learner-facing was created', env.created.length, 0);
  eq('P ' + label + ' - install state is untouched', env.api.installState(), 'instructions');
  if (extra) extra(env, state);
  return env;
}

/* 1-3. Property access can throw before any call happens. */
persistCase('1 the navigator.storage getter throws',
  { storageGetterThrows: true }, { supported: false, error: 'access' });
persistCase('2 the persisted property getter throws',
  { persistedGetterThrows: true }, { supported: false, error: 'method-access' });
persistCase('3 the persist property getter throws',
  { persistGetterThrows: true }, { supported: false, error: 'method-access' });
persistCase('3b a browser with no storage API at all',
  { storage: 'missing' }, { supported: false });
persistCase('3c a partial storage API',
  { storage: 'partial' }, { supported: false });
persistCase('3d non-callable members',
  { storage: 'not-callable' }, { supported: false });

/* 4-9. persisted(): throwing, rejecting, plain values and promises. */
persistCase('4 persisted() throws synchronously',
  { persistedThrows: true }, { supported: true, error: 'persisted-threw' },
  function (env) { eq('P 4 - persist() was never reached', env.calls.persist, 0); });
persistCase('5 persisted() rejects',
  { persistedRejects: true }, { supported: true, error: 'persisted-rejected' },
  function (env) { eq('P 5 - persist() was never reached', env.calls.persist, 0); });
persistCase('6 persisted() returns true synchronously',
  { persistedReturns: true }, { supported: true, persisted: true, granted: true },
  function (env) { eq('P 6 - already persistent, so nothing is requested', env.calls.persist, 0); });
persistCase('7 persisted() returns false synchronously',
  { persistedReturns: false, persistValue: true },
  { supported: true, persisted: false, requested: true, granted: true });
persistCase('8 persisted() resolves true',
  { persistedValue: true }, { supported: true, persisted: true, granted: true },
  function (env) { eq('P 8 - already persistent, so nothing is requested', env.calls.persist, 0); });
persistCase('9 persisted() resolves false',
  { persistedValue: false, persistValue: true },
  { supported: true, persisted: false, requested: true, granted: true });

/* 10-15. persist(): throwing inside the asynchronous continuation, rejecting,
   plain values and promises. */
persistCase('10 persist() throws synchronously after persisted() resolved false',
  { persistedValue: false, persistThrows: true },
  { supported: true, persisted: false, requested: true, granted: false, error: 'persist-threw' });
persistCase('11 persist() rejects',
  { persistedValue: false, persistRejects: true },
  { supported: true, persisted: false, requested: true, granted: false, error: 'persist-rejected' });
persistCase('12 persist() returns true synchronously',
  { persistedValue: false, persistReturns: true },
  { supported: true, persisted: false, requested: true, granted: true });
persistCase('13 persist() returns false synchronously',
  { persistedValue: false, persistReturns: false },
  { supported: true, persisted: false, requested: true, granted: false });
persistCase('14 persist() resolves true',
  { persistedValue: false, persistValue: true },
  { supported: true, persisted: false, requested: true, granted: true });
persistCase('15 persist() resolves false',
  { persistedValue: false, persistValue: false },
  { supported: true, persisted: false, requested: true, granted: false });

/* 16-20. Diagnostics, containment, and the once-per-page rule. */
(function () {
  var env = storageEnv({ persistedValue: false, persistValue: false });
  var state = askPersist(env);
  eq('P 16 the diagnostics are a small fixed record of short reasons',
     Object.keys(state).sort(), ['asked', 'error', 'granted', 'persisted', 'requested', 'supported']);
  ok('P 16 no raw exception object is exposed',
     state.error === null || typeof state.error === 'string');
  env.api.bump(99); env.api.bump(99); drain();
  eq('P 17 a denial never prompts again', [env.calls.persisted, env.calls.persist], [1, 1]);
})();
eq('P 18 no branch left an unhandled rejection behind', unhandledCount(), 0);
(function () {
  var env = storageEnv({ persistedRejects: true });
  askPersist(env);
  eq('P 19 audio and installability are untouched by a storage failure',
     [env.api.installState(), env.created.length], ['instructions', 0]);
})();
ok('P 20 the containment is explicit in the shipping source, not incidental',
   INDEX_CODE.indexOf('Promise.resolve(query).then') !== -1 &&
   INDEX_CODE.indexOf('Promise.resolve(ask).then') !== -1 &&
   countOf(INDEX_CODE, 'persistState.error = "persist-chain"') === 1 &&
   countOf(INDEX_CODE, 'try{ persisted = storage.persisted; persist = storage.persist; }') === 1 &&
   countOf(INDEX_CODE, 'try{ ask = persist.call(storage); }') === 1);
ok('P 21 the persistence diagnostics are non-learner-facing and bounded',
   INDEX_CODE.indexOf('window.ppStorageState = persistState') !== -1 &&
   INDEX.indexOf('Bounded, non-learner-facing diagnostics') !== -1);

// =========================================================================
// Result
// =========================================================================
console.log('Phase 4B-3 audio resilience/range/storage tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (line) { console.log('  ' + line); });
INFO.forEach(function (line) { console.log('  [info] ' + line); });
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
