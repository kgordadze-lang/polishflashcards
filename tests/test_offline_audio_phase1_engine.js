// Deterministic Phase 1 offline-pronunciation engine tests.
//
//   osascript -l JavaScript tests/test_offline_audio_phase1_engine.js
//
// Shipping sw.js and the marked engine block in index.html run against fake
// Cache Storage, Request, Response, fetch, MessagePort and controlled promises.
// No real network request or MP3 body is used.
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
function rootDir() {
  var fm = $.NSFileManager.defaultManager, cwd = ObjC.unwrap(fm.currentDirectoryPath);
  return fm.fileExistsAtPath(cwd + '/index.html') ? cwd + '/' : cwd + '/../';
}
var ROOT = rootDir();
var SW_SRC = readFile(ROOT + 'sw.js');
var INDEX = readFile(ROOT + 'index.html');
var MANIFEST = JSON.parse(readFile(ROOT + 'audio-manifest.json'));
var PASS = 0, FAIL = 0, FAILURES = [];
function ok(name, value) { if (value) PASS++; else { FAIL++; FAILURES.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}

// -------------------------------------------------------------------------
// Hand-drained promises: timing and races are assertions, not wall-clock luck.
// -------------------------------------------------------------------------
var JOBS = [];
function schedule(job) { JOBS.push(job); }
function drain() {
  var guard = 0;
  while (JOBS.length) {
    if (++guard > 3000000) throw new Error('runaway deterministic queue');
    JOBS.shift()();
  }
}
function P(executor) {
  this.state = 'pending'; this.value = undefined; this.handlers = [];
  var self_ = this;
  if (executor) {
    try { executor(function (v) { settle(self_, v); }, function (e) { reject(self_, e); }); }
    catch (e) { reject(self_, e); }
  }
}
function settle(p, value) {
  if (p.state !== 'pending') return;
  if (value && typeof value.then === 'function') {
    var called = false;
    try { value.then(function (v) { if (!called) { called = true; settle(p, v); } },
                     function (e) { if (!called) { called = true; reject(p, e); } }); }
    catch (e) { if (!called) { called = true; reject(p, e); } }
    return;
  }
  p.state = 'fulfilled'; p.value = value; flush(p);
}
function reject(p, error) { if (p.state === 'pending') { p.state = 'rejected'; p.value = error; flush(p); } }
function flush(p) {
  var handlers = p.handlers; p.handlers = [];
  handlers.forEach(function (h) { schedule(function () { runHandler(p, h); }); });
}
function runHandler(p, h) {
  var fn = p.state === 'fulfilled' ? h.ok : h.bad;
  if (typeof fn !== 'function') {
    if (p.state === 'fulfilled') settle(h.next, p.value); else reject(h.next, p.value);
    return;
  }
  try { settle(h.next, fn(p.value)); } catch (e) { reject(h.next, e); }
}
P.prototype.then = function (yes, no) {
  var next = new P(), h = { ok: yes, bad: no, next: next }, self_ = this;
  if (this.state === 'pending') this.handlers.push(h);
  else schedule(function () { runHandler(self_, h); });
  return next;
};
P.prototype['catch'] = function (no) { return this.then(undefined, no); };
P.resolve = function (v) { var p = new P(); settle(p, v); return p; };
P.reject = function (e) { var p = new P(); reject(p, e); return p; };
P.all = function (items) {
  return new P(function (resolve, rejectAll) {
    var list = Array.prototype.slice.call(items), left = list.length, out = new Array(left);
    if (!left) { resolve(out); return; }
    list.forEach(function (item, i) { P.resolve(item).then(function (v) {
      out[i] = v; if (--left === 0) resolve(out);
    }, rejectAll); });
  });
};
function deferred() { var d = {}; d.promise = new P(function (yes, no) { d.resolve = yes; d.reject = no; }); return d; }
function watch(promise) {
  var record = { state: 'pending', value: undefined };
  P.resolve(promise).then(function (v) { record.state = 'fulfilled'; record.value = v; },
                          function (e) { record.state = 'rejected'; record.value = e; });
  return record;
}

// -------------------------------------------------------------------------
// Minimal URL / Request / Response fakes.
// -------------------------------------------------------------------------
function FakeURL(input, base) {
  var raw = String(input), absolute = /^https?:\/\//.test(raw), root = base ? String(base) : '';
  if (!absolute) {
    if (!root) throw new TypeError('relative URL without base');
    root = root.replace(/[^/]*$/, '');
    raw = root + raw;
  }
  var m = /^(https?):\/\/([^/?#]+)([^?#]*)(\?[^#]*)?(#.*)?$/.exec(raw);
  if (!m) throw new TypeError('invalid URL');
  var parts = [], source = m[3] || '/';
  source.split('/').forEach(function (part) {
    if (part === '..') { if (parts.length > 1) parts.pop(); }
    else if (part !== '.') parts.push(part);
  });
  this.protocol = m[1] + ':'; this.host = m[2]; this.origin = this.protocol + '//' + this.host;
  this.pathname = parts.join('/') || '/'; this.search = m[4] || ''; this.hash = m[5] || '';
  this.href = this.origin + this.pathname + this.search + this.hash;
}
FakeURL.prototype.toString = function () { return this.href; };
function FakeHeaders(values) {
  this.map = {};
  var self_ = this;
  Object.keys(values || {}).forEach(function (name) { self_.map[name.toLowerCase()] = values[name]; });
}
FakeHeaders.prototype.get = function (name) {
  var value = this.map[String(name).toLowerCase()]; return value === undefined ? null : value;
};
function FakeRequest(url, options) {
  options = options || {};
  this.url = typeof url === 'string' ? url : url.url;
  this.method = options.method || 'GET'; this.mode = options.mode || 'no-cors';
  this.credentials = options.credentials; this.cache = options.cache;
  this.headers = new FakeHeaders(options.headers);
}
var BODY_READS = 0;
function FakeResponse(options, init) {
  if (init !== undefined || options === null || options instanceof ArrayBuffer) {
    options = { body: options, status: (init || {}).status, statusText: (init || {}).statusText,
                headers: (init || {}).headers, type: 'basic' };
  }
  options = options || {};
  this.status = options.status === undefined ? 200 : options.status;
  this.ok = options.ok === undefined ? this.status >= 200 && this.status < 300 : options.ok;
  this.type = options.type === undefined ? 'basic' : options.type;
  this.redirected = options.redirected === true; this.url = options.url || '';
  this.headers = new FakeHeaders(options.headers || { 'Content-Type': 'audio/mpeg' });
  this.body = options.body || new ArrayBuffer(4); this.statusText = options.statusText || '';
  this.bodyUsed = false;
}
FakeResponse.prototype.clone = function () {
  if (this.bodyUsed) throw new TypeError('used body');
  return new FakeResponse({ status:this.status, ok:this.ok, type:this.type, redirected:this.redirected,
    url:this.url, headers:this.headers.map, body:this.body, statusText:this.statusText });
};
FakeResponse.prototype.arrayBuffer = function () { BODY_READS++; this.bodyUsed = true; return P.resolve(this.body); };
FakeResponse.redirect = function (url, status) { return new FakeResponse({ status:status || 302, ok:false, redirected:true, url:url }); };
function keyOf(value) { return typeof value === 'string' ? value : value.url; }
function audioResponse(url, changes) {
  var options = { url:url, headers:{ 'Content-Type':'audio/mpeg' } };
  Object.keys(changes || {}).forEach(function (key) { options[key] = changes[key]; });
  return new FakeResponse(options);
}

// -------------------------------------------------------------------------
// Insertion-ordered Cache Storage with programmable failures.
// -------------------------------------------------------------------------
function FakeCache(name, storage) {
  this.name = name; this.storage = storage; this.entries = {}; this.order = [];
  this.puts = []; this.deletes = []; this.keyCalls = 0; this.matchCalls = 0;
}
FakeCache.prototype.match = function (request) {
  var key = keyOf(request), self_ = this; this.matchCalls++;
  this.storage.matchActive++;
  this.storage.matchMax = Math.max(this.storage.matchMax, this.storage.matchActive);
  var behavior = this.storage.matchBehavior && this.storage.matchBehavior(this.name, key);
  var result = behavior && behavior.defer ? behavior.defer.promise :
    (behavior && behavior.reject ? P.reject(behavior.reject) :
      P.resolve(this.entries[key] === undefined ? undefined : this.entries[key].clone()));
  return result.then(function (value) { self_.storage.matchActive--; return value; }, function (error) {
    self_.storage.matchActive--; throw error;
  });
};
FakeCache.prototype.put = function (request, response) {
  var key = keyOf(request), self_ = this; this.puts.push(key);
  var attempt = this.puts.filter(function (item) { return item === key; }).length;
  var behavior = this.storage.putBehavior && this.storage.putBehavior(this.name, key, response, attempt);
  function store() {
    if (self_.order.indexOf(key) === -1) self_.order.push(key);
    self_.entries[key] = response;
  }
  if (behavior && behavior.reject) return P.reject(behavior.reject);
  if (behavior && behavior.defer) return behavior.defer.promise.then(function () { store(); });
  store(); return P.resolve();
};
FakeCache.prototype['delete'] = function (request) {
  var key = keyOf(request); this.deletes.push(key);
  if (this.entries[key] === undefined) return P.resolve(false);
  delete this.entries[key]; this.order = this.order.filter(function (item) { return item !== key; });
  return P.resolve(true);
};
FakeCache.prototype.keys = function () {
  this.keyCalls++;
  return P.resolve(this.order.map(function (key) { return new FakeRequest(key); }));
};
function FakeCaches(seed) {
  this.map = {}; this.names = []; this.deleted = []; this.putBehavior = null;
  this.matchBehavior = null; this.matchActive = 0; this.matchMax = 0;
  var self_ = this;
  Object.keys(seed || {}).forEach(function (name) {
    var cache = self_.raw(name);
    Object.keys(seed[name]).forEach(function (key) { cache.order.push(key); cache.entries[key] = seed[name][key]; });
  });
}
FakeCaches.prototype.raw = function (name) {
  if (!this.map[name]) { this.map[name] = new FakeCache(name, this); this.names.push(name); }
  return this.map[name];
};
FakeCaches.prototype.open = function (name) { return P.resolve(this.raw(name)); };
FakeCaches.prototype.keys = function () { return P.resolve(this.names.slice()); };
FakeCaches.prototype['delete'] = function (name) {
  this.deleted.push(name);
  if (!this.map[name]) return P.resolve(false);
  delete this.map[name]; this.names = this.names.filter(function (item) { return item !== name; });
  return P.resolve(true);
};
FakeCaches.prototype.inventory = function (name) { return this.map[name] ? this.map[name].order.slice() : null; };

// -------------------------------------------------------------------------
// Shipping worker and marked shipping page engine.
// -------------------------------------------------------------------------
var ORIGIN = 'https://popolsku.app';
var SW_EPILOGUE = '\nreturn { state:SW_STATE, AUDIO_CACHE:AUDIO_CACHE, CACHE:CACHE,' +
  ' storeValidatedAudio:storeValidatedAudio, reconcileOfflineAudio:reconcileOfflineAudio,' +
  ' removeOfflineAudio:removeOfflineAudio, offlineAudioKey:offlineAudioKey };';
function makeWorker(options) {
  options = options || {};
  var caches = new FakeCaches(options.seed || {}), listeners = {}, fetchCalls = [];
  var route = options.route || function (url) { return P.resolve(audioResponse(url)); };
  function fetchFn(input, init) {
    var call = { url:keyOf(input), request:typeof input === 'string' ? null : input, init:init || null };
    fetchCalls.push(call);
    var result;
    try { result = route(call.url, input, init); } catch (e) { return P.reject(e); }
    return P.resolve(result);
  }
  var self_ = {
    location:{ origin:ORIGIN, href:ORIGIN + '/sw.js', pathname:'/sw.js', protocol:'https:' },
    registration:{ scope:ORIGIN + '/' }, clients:{ claim:function () { return P.resolve(); } },
    addEventListener:function (kind, fn) { (listeners[kind] = listeners[kind] || []).push(fn); }
  };
  var console_ = { warn:function () {}, log:function () {}, error:function () {} };
  var api = (new Function('self','caches','fetch','Request','Response','URL','Promise','console',
    SW_SRC + SW_EPILOGUE))(self_, caches, fetchFn, FakeRequest, FakeResponse, FakeURL, P, console_);
  return {
    self:self_, api:api, caches:caches, fetchCalls:fetchCalls,
    fire:function (kind, event) { (listeners[kind] || []).forEach(function (fn) { fn(event); }); }
  };
}
function protocolTransport(worker) {
  return function (command, payload, token) {
    var reply = deferred(), waits = [];
    var data = Object.assign({ command:command, token:token }, payload || {});
    worker.fire('message', { data:data, ports:[{ postMessage:function (value) { reply.resolve(value); } }],
      waitUntil:function (promise) { waits.push(promise); } });
    return reply.promise;
  };
}
function send(worker, command, payload, token) {
  var rec = watch(protocolTransport(worker)(command, payload, token || 'test-token'));
  drain(); return rec;
}
function fireFetch(worker, request) {
  var event = { request:request, waits:[], responses:[],
    waitUntil:function (p) { this.waits.push(p); }, respondWith:function (p) { this.responses.push(p); } };
  worker.fire('fetch', event); drain();
  return { event:event, response:event.responses.length ? watch(event.responses[0]) : null,
           writes:event.waits.map(watch) };
}

var markerStart = INDEX.indexOf('/* OFFLINE_AUDIO_ENGINE_START');
var markerEnd = INDEX.indexOf('/* OFFLINE_AUDIO_ENGINE_END */');
ok('engine markers exist in the shipping page', markerStart !== -1 && markerEnd > markerStart);
var ENGINE_SRC = INDEX.slice(markerStart, markerEnd + '/* OFFLINE_AUDIO_ENGINE_END */'.length);
var engineWindow = {}, engineDocument = { baseURI:ORIGIN + '/' }, engineLocation = { href:ORIGIN + '/' };
var ENGINE = (new Function('window','document','location','navigator','MessageChannel','URL','Promise',
  'setTimeout','clearTimeout', ENGINE_SRC + '\nreturn window.PPOfflineAudioEngine;'))(
    engineWindow, engineDocument, engineLocation, {}, function () {}, FakeURL, P,
    function () { return 1; }, function () {});
ok('shipping page engine evaluates', !!ENGINE && typeof ENGINE.create === 'function');

function hashFile(number) {
  var hex = Number(number).toString(16); return 'audio/' + ('000000000000' + hex).slice(-12) + '.mp3';
}
function files(count, offset) {
  var out = []; for (var i = 0; i < count; i++) out.push(hashFile((offset || 0) + i + 1)); return out;
}
function absolute(file) { return ORIGIN + '/' + file; }
function seedAudio(list, responseFactory) {
  var seed = { 'popolsku-audio':{} };
  list.forEach(function (file) { var url = absolute(file); seed['popolsku-audio'][url] =
    responseFactory ? responseFactory(url, file) : audioResponse(url); });
  return seed;
}
function runEngine(worker, manifestFiles, options) {
  options = options || {}; options.baseHref = ORIGIN + '/';
  if (!options.transport) options.transport = protocolTransport(worker);
  return ENGINE.create(manifestFiles, options);
}

// A. Trust boundary, manifest preparation and protocol envelope.
eq('A1 constants are locked', ENGINE.constants, { MAX_MANIFEST_ITEMS:5000, CONCURRENCY:3, BAD_RESPONSE_LIMIT:3 });
eq('A2 page preparation deduplicates canonical identities',
   ENGINE.prepareManifest([hashFile(1), hashFile(1), absolute(hashFile(2))], ORIGIN + '/'),
   [absolute(hashFile(1)), absolute(hashFile(2))]);
[
  ['cross origin', 'https://evil.example/audio/000000000001.mp3'],
  ['query', hashFile(1) + '?x=1'], ['fragment', hashFile(1) + '#x'],
  ['dot segment', './' + hashFile(1)], ['leading slash', '/' + hashFile(1)],
  ['uppercase hash', 'audio/ABCDEF000001.mp3'], ['not hashed', 'audio/word.mp3'],
  ['wrong folder', 'media/000000000001.mp3']
].forEach(function (row) {
  var threw = false; try { ENGINE.prepareManifest([row[1]], ORIGIN + '/'); } catch (e) { threw = true; }
  ok('A3 page rejects ' + row[0], threw);
});
var tooMany = files(5001, 10000), tooManyThrew = false;
try { ENGINE.prepareManifest(tooMany, ORIGIN + '/'); } catch (e) { tooManyThrew = true; }
ok('A4 page rejects oversized manifest input', tooManyThrew);
var validationWorker = makeWorker();
eq('A5 worker rejects duplicate reconciliation input',
   send(validationWorker, 'offline-audio-reconcile', { files:[hashFile(1), hashFile(1)] }).value.outcome,
   'invalid-request');
['https://evil.example/audio/000000000001.mp3', hashFile(1) + '?x=1', './' + hashFile(1),
 'audio/not-a-hash.mp3'].forEach(function (value, i) {
  eq('A6 worker rejects malformed candidate ' + i,
     send(validationWorker, 'offline-audio-store-one', { file:value, mutationGeneration:0 }).value.outcome,
     'invalid-request');
});
eq('A7 worker rejects unbounded reconciliation input',
   send(validationWorker, 'offline-audio-reconcile', { files:tooMany }).value.outcome, 'invalid-request');
ok('A8 protocol is local-only and has no reporting vocabulary',
   !/telemetry|analytics|sendBeacon|reporting endpoint/i.test(ENGINE_SRC + SW_SRC));

// B. Exact reconciliation: one key scan, sequential metadata reads, no bodies.
var exactFiles = files(6, 100), exactSeed = seedAudio([exactFiles[0]]);
exactSeed['popolsku-audio'][absolute(exactFiles[1])] = audioResponse(absolute(exactFiles[1]), { status:206 });
exactSeed['popolsku-audio'][absolute(exactFiles[2])] = audioResponse(absolute(exactFiles[2]), { headers:{'Content-Type':'text/html'} });
exactSeed['popolsku-audio'][absolute(exactFiles[3])] = audioResponse(absolute(exactFiles[3]), { redirected:true });
exactSeed['popolsku-audio'][absolute(exactFiles[4]) + '?legacy=1'] = audioResponse(absolute(exactFiles[4]));
exactSeed['popolsku-audio'][ORIGIN + '/audio/ffffffffffff.mp3'] = audioResponse(ORIGIN + '/audio/ffffffffffff.mp3');
var exactWorker = makeWorker({ seed:exactSeed }), beforeReads = BODY_READS;
var exactReply = send(exactWorker, 'offline-audio-reconcile', { files:exactFiles }).value;
eq('B1 only exact valid current entry is present', [exactReply.presentCount, exactReply.missingCount, exactReply.invalid], [1,5,3]);
eq('B2 reconciliation enumerates cache keys once', exactWorker.caches.raw('popolsku-audio').keyCalls, 1);
eq('B3 reconciliation Cache API concurrency is bounded to one',
   [exactWorker.caches.matchMax, exactWorker.api.state.offlineAudio.reconcileCacheOpsMax], [1,1]);
eq('B4 reconciliation reads no MP3 bodies', BODY_READS, beforeReads);
ok('B5 invalid exact hits are evicted but query/unrelated entries remain',
   exactWorker.caches.inventory('popolsku-audio').indexOf(absolute(exactFiles[1])) === -1 &&
   exactWorker.caches.inventory('popolsku-audio').indexOf(absolute(exactFiles[4]) + '?legacy=1') !== -1);

// C. Full synthetic scale run using every exact committed manifest identity.
var committedFiles = Object.keys(MANIFEST.entries).map(function (key) { return MANIFEST.entries[key].file; });
eq('C1 committed scale fixture is exactly 3,621 unique identities',
   [committedFiles.length, ENGINE.prepareManifest(committedFiles, ORIGIN + '/').length], [3621,3621]);
var scaleWorker = makeWorker(), scaleEngine = runEngine(scaleWorker, committedFiles);
var scaleRun = watch(scaleEngine.start()); drain();
eq('C2 full 3,621 synthetic download completes from final reconciliation',
   [scaleRun.state, scaleRun.value.status, scaleRun.value.present, scaleRun.value.missing],
   ['fulfilled','complete',3621,0]);
eq('C3 full scale fetches each identity exactly once', scaleWorker.fetchCalls.length, 3621);
eq('C4 scheduler reaches and never exceeds exactly three active operations', scaleRun.value.maxActive, 3);
eq('C5 clean full library stays below retention and trims nothing',
   [scaleWorker.caches.inventory('popolsku-audio').length, scaleWorker.api.state.audio.trimmed], [3621,0]);
ok('C6 downloader requests are complete GETs without Range or If-Range', scaleWorker.fetchCalls.every(function (call) {
  return call.request && call.request.method === 'GET' && !call.request.headers.get('range') &&
    !call.request.headers.get('if-range');
}));

// D. Existing entries, partial resume, future +59, duplicate messages.
var partialFiles = files(12, 5000), partialWorker = makeWorker({ seed:seedAudio(partialFiles.slice(0,5)) });
var partialEngine = runEngine(partialWorker, partialFiles), partialRun = watch(partialEngine.start()); drain();
eq('D1 partial cache queues only missing clips', [partialWorker.fetchCalls.length, partialRun.value.status], [7,'complete']);
var reloadEngine = runEngine(partialWorker, partialFiles), reload = watch(reloadEngine.reconcile()); drain();
eq('D2 fresh engine reconstructs truth solely from Cache Storage',
   [reload.value.presentCount || reloadEngine.getState().present, reloadEngine.getState().missing], [12,0]);
var oldSeed = seedAudio(committedFiles), updateFiles = committedFiles.slice(), seenUpdate = {};
committedFiles.forEach(function (file) { seenUpdate[file] = true; });
var candidate = 0xff0000000000;
while (updateFiles.length < 3680) { var f = hashFile(candidate++); if (!seenUpdate[f]) { seenUpdate[f] = true; updateFiles.push(f); } }
var updateWorker = makeWorker({ seed:oldSeed }), updateEngine = runEngine(updateWorker, updateFiles);
var updateRun = watch(updateEngine.start()); drain();
eq('D3 future 3,680 manifest fetches only 59 missing clips',
   [updateWorker.fetchCalls.length, updateRun.value.present, updateRun.value.status], [59,3680,'complete']);
var repeatWorker = makeWorker(), repeatFile = hashFile(7000);
var gen = send(repeatWorker, 'offline-audio-reconcile', { files:[repeatFile] }).value.mutationGeneration;
var first = send(repeatWorker, 'offline-audio-store-one', { file:repeatFile, mutationGeneration:gen }).value;
var second = send(repeatWorker, 'offline-audio-store-one', { file:repeatFile, mutationGeneration:gen }).value;
eq('D4 repeated store messages are idempotent',
   [first.outcome, second.outcome, repeatWorker.caches.inventory('popolsku-audio').length], ['stored','already-present',1]);

// E. Cooperative pause and missing-only continue.
var pauseFiles = files(8, 8000), held = [], pauseWorker = makeWorker({ route:function (url) {
  if (held.length < 3) { var d = deferred(); held.push({ url:url, deferred:d }); return d.promise; }
  return P.resolve(audioResponse(url));
} });
var pauseEngine = runEngine(pauseWorker, pauseFiles), pauseRun = watch(pauseEngine.start()); drain();
eq('E1 exactly three operations are held before Pause', [held.length, pauseWorker.fetchCalls.length, pauseEngine.getState().active], [3,3,3]);
pauseEngine.pause(); drain();
eq('E2 Pause schedules no fourth item', pauseWorker.fetchCalls.length, 3);
held.forEach(function (item) { item.deferred.resolve(audioResponse(item.url)); }); drain();
eq('E3 in-flight acknowledgements settle into paused partial state',
   [pauseRun.value.status, pauseRun.value.present, pauseRun.value.maxActive], ['paused',3,3]);
var continueRun = watch(pauseEngine.continueDownload()); drain();
eq('E4 Continue reconciles and fetches missing only',
   [continueRun.value.status, continueRun.value.present, pauseWorker.fetchCalls.length], ['complete',8,8]);

// E2. Independent-review regression: re-entry while the old Pause drain is alive.
var reentryFiles = files(8, 8500), reentryHeld = [], reentryActive = 0, reentryMax = 0, reentryStates = [];
var reentryWorker = makeWorker({ route:function (url) {
  reentryActive++; reentryMax = Math.max(reentryMax, reentryActive);
  if (reentryHeld.length < 3) {
    var d = deferred();
    reentryHeld.push({ url:url, deferred:d });
    return d.promise.then(function (response) { reentryActive--; return response; }, function (error) {
      reentryActive--; throw error;
    });
  }
  reentryActive--;
  return P.resolve(audioResponse(url));
} });
var reentryEngine = runEngine(reentryWorker, reentryFiles, { onState:function (state) { reentryStates.push(state); } });
var reentrySession = reentryEngine.start();
eq('E5 same-generation Start/Continue calls join the exact active session promise',
   [reentryEngine.start() === reentrySession, reentryEngine.continueDownload() === reentrySession], [true,true]);
var reentryOldRun = watch(reentrySession); drain();
eq('E6 re-entry fixture holds exactly three old operations',
   [reentryHeld.length, reentryWorker.fetchCalls.length, reentryEngine.getState().active], [3,3,3]);
reentryEngine.pause(); drain();
var reentryCheck = watch(reentryEngine.reconcile()); drain();
eq('E7 authoritative re-entry reconciliation advances to truthful ready state while old lanes drain',
   [reentryCheck.value.status, reentryCheck.value.present, reentryEngine.getState().active], ['ready',0,3]);
var queuedOne = reentryEngine.continueDownload();
var queuedTwo = reentryEngine.continueDownload();
var queuedThree = reentryEngine.continueDownload();
var queuedRun = watch(queuedOne); drain();
eq('E8 rapid Continue presses join one queued successor and start no fourth request',
   [queuedTwo === queuedOne, queuedThree === queuedOne, queuedRun.state, reentryWorker.fetchCalls.length],
   [true,true,'pending',3]);
var stateEventsBeforeStaleTail = reentryStates.length;
reentryHeld[0].deferred.resolve(audioResponse(reentryHeld[0].url)); drain();
eq('E9 a stale lane tail decrements accounting without publishing into the new generation',
   [reentryEngine.getState().status, reentryEngine.getState().active, reentryStates.length],
   ['ready',2,stateEventsBeforeStaleTail]);
reentryHeld.slice(1).forEach(function (item) { item.deferred.resolve(audioResponse(item.url)); }); drain();
eq('E10 one queued Continue automatically completes after the stale three-lane drain',
   [queuedRun.state, queuedRun.value.status, queuedRun.value.present, reentryWorker.fetchCalls.length],
   ['fulfilled','complete',8,8]);
eq('E11 old and successor sessions never overlap above concurrency three',
   [reentryMax, queuedRun.value.maxActive, reentryActive], [3,3,0]);
eq('E12 the superseded old session cannot overwrite successor completion',
   [reentryOldRun.state, reentryEngine.getState().status], ['fulfilled','complete']);

// A queued successor is generation-owned: Remove cancels it before the stale drain ends.
var queuedRemoveFiles = files(8, 8600), queuedRemoveHeld = [];
var queuedRemoveWorker = makeWorker({ route:function (url) {
  if (queuedRemoveHeld.length < 3) { var d = deferred(); queuedRemoveHeld.push({url:url,deferred:d}); return d.promise; }
  return P.resolve(audioResponse(url));
} });
var queuedRemoveEngine = runEngine(queuedRemoveWorker, queuedRemoveFiles);
queuedRemoveEngine.start(); drain(); queuedRemoveEngine.pause();
watch(queuedRemoveEngine.reconcile()); drain();
var canceledByRemove = watch(queuedRemoveEngine.continueDownload()); drain();
var authoritativeRemove = watch(queuedRemoveEngine.remove()); drain();
eq('E13 Remove becomes authoritative while the queued successor is waiting',
   [authoritativeRemove.value.status, canceledByRemove.state, queuedRemoveWorker.fetchCalls.length],
   ['removed','pending',3]);
queuedRemoveHeld.forEach(function (item) { item.deferred.resolve(audioResponse(item.url)); }); drain();
eq('E14 Remove cancels the queued successor with no post-Remove store request',
   [canceledByRemove.value.status, queuedRemoveEngine.getState().status, queuedRemoveWorker.fetchCalls.length],
   ['removed','removed',3]);

// A newer reconciliation likewise invalidates an older queued Continue.
var queuedCheckFiles = files(8, 8700), queuedCheckHeld = [];
var queuedCheckWorker = makeWorker({ route:function (url) {
  if (queuedCheckHeld.length < 3) { var d = deferred(); queuedCheckHeld.push({url:url,deferred:d}); return d.promise; }
  return P.resolve(audioResponse(url));
} });
var queuedCheckEngine = runEngine(queuedCheckWorker, queuedCheckFiles);
queuedCheckEngine.start(); drain(); queuedCheckEngine.pause();
watch(queuedCheckEngine.reconcile()); drain();
var canceledByCheck = watch(queuedCheckEngine.continueDownload()); drain();
var newerCheck = watch(queuedCheckEngine.reconcile()); drain();
eq('E15 newer reconciliation supersedes the queued Continue before stale drain completion',
   [newerCheck.value.status, canceledByCheck.state, queuedCheckWorker.fetchCalls.length],
   ['ready','pending',3]);
queuedCheckHeld.forEach(function (item) { item.deferred.resolve(audioResponse(item.url)); }); drain();
eq('E16 newer reconciliation cancels the old successor without new scheduler lanes',
   [canceledByCheck.value.status, queuedCheckEngine.getState().status, queuedCheckWorker.fetchCalls.length],
   ['ready','ready',3]);

// F. Bounded failures and valid partial retention.
var networkCalls = 0, networkWorker = makeWorker({ route:function (url) {
  networkCalls++; return networkCalls === 1 ? P.reject(new TypeError('offline')) : P.resolve(audioResponse(url));
} });
var networkEngine = runEngine(networkWorker, files(20, 9000)), networkRun = watch(networkEngine.start()); drain();
eq('F1 first failed wave stops bounded scheduling and retains successes',
   [networkRun.value.status, networkWorker.fetchCalls.length, networkRun.value.present], ['network-failed',3,2]);
var badCalls = 0, badWorker = makeWorker({ route:function (url) {
  badCalls++; return P.resolve(badCalls === 1 ? audioResponse(url, { status:404, ok:false }) : audioResponse(url));
} });
var badEngine = runEngine(badWorker, files(7, 9500)), badRun = watch(badEngine.start()); drain();
eq('F2 one isolated bad response lets useful clips continue but cannot report Complete',
   [badWorker.fetchCalls.length, badRun.value.status, badRun.value.present, badRun.value.badResponses], [7,'incomplete',6,1]);
var badLimitWorker = makeWorker({ route:function (url) {
  return P.resolve(audioResponse(url, { status:404, ok:false }));
} });
var badLimitEngine = runEngine(badLimitWorker, files(20, 9700)), badLimitRun = watch(badLimitEngine.start()); drain();
eq('F3 three bad responses stop scheduling at the bounded policy',
   [badLimitWorker.fetchCalls.length, badLimitRun.value.status, badLimitRun.value.reason], [3,'incomplete','bad-response']);
var storageStopWorker = makeWorker();
storageStopWorker.caches.putBehavior = function (name) {
  return name === 'popolsku-audio' ? { reject:new Error('storage full') } : null;
};
var storageStopEngine = runEngine(storageStopWorker, files(20, 9800));
var storageStopRun = watch(storageStopEngine.start()); drain();
eq('F4 final storage failure stops scheduling, reconciles and retains truth',
   [storageStopWorker.fetchCalls.length, storageStopRun.value.status,
    storageStopRun.value.present, storageStopRun.value.missing], [3,'storage-failed',0,20]);
var badKinds = [
  { status:404, ok:false }, { status:206 }, { redirected:true }, { type:'opaque' },
  { headers:{'Content-Type':'text/html'} }, { headers:{} }, { type:'error', status:0, ok:false }
];
badKinds.forEach(function (changes, i) {
  var worker = makeWorker({ route:function (url) { return P.resolve(audioResponse(url, changes)); } });
  var file = hashFile(10000 + i), generation = send(worker, 'offline-audio-reconcile', { files:[file] }).value.mutationGeneration;
  var result = send(worker, 'offline-audio-store-one', { file:file, mutationGeneration:generation }).value;
  eq('F5 bad response kind ' + i + ' is never cached', [result.outcome, worker.caches.inventory('popolsku-audio').length], ['bad-response',0]);
});

// G. Shared store primitive and coalesced quota recovery.
var quotaFile = hashFile(11000), quotaUrl = absolute(quotaFile), quotaSeed = seedAudio(files(70, 12000));
var quotaWorker = makeWorker({ seed:quotaSeed });
quotaWorker.caches.putBehavior = function (name, key, response, attempt) {
  return key === quotaUrl && attempt === 1 ? { reject:new Error('quota') } : null;
};
var quotaResult = watch(quotaWorker.api.storeValidatedAudio(quotaUrl, audioResponse(quotaUrl))); drain();
eq('G1 first put failure performs one 64-entry recovery and one successful retry',
   [quotaResult.value.outcome, quotaWorker.api.state.audio.recoveryAttempts,
    quotaWorker.api.state.audio.trimmed, quotaWorker.caches.raw('popolsku-audio').puts.filter(function (k) { return k === quotaUrl; }).length],
   ['stored',1,64,2]);
var concurrentWorker = makeWorker({ seed:seedAudio(files(100, 13000)) }), concurrentUrls = files(3, 14000).map(absolute);
concurrentWorker.caches.putBehavior = function (name, key, response, attempt) {
  return concurrentUrls.indexOf(key) !== -1 && attempt === 1 ? { reject:new Error('quota') } : null;
};
var concurrent = concurrentUrls.map(function (url) { return watch(concurrentWorker.api.storeValidatedAudio(url, audioResponse(url))); });
drain();
eq('G2 three concurrent failures coalesce into one eviction wave',
   [concurrentWorker.api.state.audio.recoveryAttempts, concurrentWorker.api.state.audio.trimmed,
    concurrent.map(function (r) { return r.value.outcome; })], [1,64,['stored','stored','stored']]);
var failWorker = makeWorker({ seed:seedAudio(files(70, 15000)) }), failUrl = absolute(hashFile(16000));
failWorker.caches.putBehavior = function (name, key) { return key === failUrl ? { reject:new Error('quota') } : null; };
var finalFailure = watch(failWorker.api.storeValidatedAudio(failUrl, audioResponse(failUrl))); drain();
eq('G3 final retry failure is typed and never loops',
   [finalFailure.value.outcome, failWorker.api.state.audio.recoveryAttempts,
    failWorker.caches.raw('popolsku-audio').puts.filter(function (k) { return k === failUrl; }).length],
   ['storage-failed',1,2]);
var sharedWorker = makeWorker(), sharedFile = hashFile(17000), sharedUrl = absolute(sharedFile);
var ordinary = fireFetch(sharedWorker, new FakeRequest(sharedUrl)); drain();
var sharedGen = send(sharedWorker, 'offline-audio-reconcile', { files:[hashFile(17001)] }).value.mutationGeneration;
send(sharedWorker, 'offline-audio-store-one', { file:hashFile(17001), mutationGeneration:sharedGen });
eq('G4 ordinary playback and explicit download call the same store primitive',
   sharedWorker.api.state.audio.storeValidatedCalls, 2);
var failedPlayback = makeWorker();
failedPlayback.caches.putBehavior = function () { return { reject:new Error('storage') }; };
var playbackRun = fireFetch(failedPlayback, new FakeRequest(absolute(hashFile(17100)))); drain();
eq('G5 failed background storage never breaks successful online playback',
   [playbackRun.response.state, playbackRun.response.value.status], ['fulfilled',200]);

// H. Retention conflict is final and never causes an automatic redownload loop.
var conflictFiles = files(5, 18000), conflictSeed = seedAudio(conflictFiles.slice(0,4));
for (var legacy = 0; legacy < 4196; legacy++) {
  var legacyUrl = absolute(hashFile(0x100000 + legacy));
  conflictSeed['popolsku-audio'][legacyUrl] = audioResponse(legacyUrl);
}
var conflictWorker = makeWorker({ seed:conflictSeed }), conflictEngine = runEngine(conflictWorker, conflictFiles);
var conflictRun = watch(conflictEngine.start()); drain();
eq('H1 >4,200 FIFO pressure yields explicit retention conflict',
   [conflictRun.value.status, conflictWorker.fetchCalls.length, conflictWorker.api.state.audio.trimmed > 0],
   ['retention-conflict',1,true]);
ok('H2 retention conflict does not enter a redownload loop', conflictWorker.fetchCalls.length === 1);

// I. Remove ordering, exact cache deletion and ordinary lazy rewarming.
var raceFile = hashFile(20000), raceDeferred = deferred();
var raceSeed = seedAudio([hashFile(20001)]); raceSeed['popolsku-v71'] = { [ORIGIN + '/']:new FakeResponse({headers:{'Content-Type':'text/html'}}) };
raceSeed['unrelated-cache'] = { [ORIGIN + '/tool']:new FakeResponse({headers:{'Content-Type':'text/plain'}}) };
var raceWorker = makeWorker({ seed:raceSeed, route:function () { return raceDeferred.promise; } });
var raceGeneration = send(raceWorker, 'offline-audio-reconcile', { files:[raceFile] }).value.mutationGeneration;
var staleStore = watch(protocolTransport(raceWorker)('offline-audio-store-one',
  { file:raceFile, mutationGeneration:raceGeneration }, 'race-store')); drain();
var learningState = { progress:'unchanged' };
var removal = send(raceWorker, 'offline-audio-remove', {}, 'race-remove');
eq('I1 Remove deletes exactly popolsku-audio and preserves other caches/state',
   [removal.value.outcome, raceWorker.caches.names.sort(), learningState.progress],
   ['removed',['popolsku-v71','unrelated-cache'],'unchanged']);
raceDeferred.resolve(audioResponse(absolute(raceFile))); drain();
eq('I2 late downloader fetch is stale and cannot resurrect audio after Remove',
   [staleStore.value.outcome, raceWorker.caches.inventory('popolsku-audio')], ['stale',null]);
ok('I3 Remove resets the worker audio entry estimate contract', SW_SRC.indexOf('audioEntryEstimate = null;') !== -1);
var rewarm = fireFetch(raceWorker, new FakeRequest(absolute(raceFile))); drain();
eq('I4 ordinary playback after Remove can warm one clip again',
   [rewarm.response.value.status, raceWorker.caches.inventory('popolsku-audio')], [200,[absolute(raceFile)]]);

// J. Protected Range separation and offline warm behavior.
var rangeFile = hashFile(21000), rangeUrl = absolute(rangeFile), bytes = new Uint8Array([1,2,3,4,5,6]).buffer;
var rangeWorker = makeWorker({ seed:seedAudio([rangeFile], function (url) { return audioResponse(url, {body:bytes}); }) });
var warmRange = fireFetch(rangeWorker, new FakeRequest(rangeUrl, { headers:{ Range:'bytes=1-3' } })); drain();
eq('J1 warm Range still synthesizes correct 206',
   [warmRange.response.value.status, warmRange.response.value.headers.get('content-range')], [206,'bytes 1-3/6']);
var unsat = fireFetch(rangeWorker, new FakeRequest(rangeUrl, { headers:{ Range:'bytes=99-' } })); drain();
eq('J2 unsatisfiable Range remains 416', unsat.response.value.status, 416);
var coldWorker = makeWorker(), coldRequest = new FakeRequest(absolute(hashFile(21001)), { headers:{ Range:'bytes=0-1' } });
var coldRange = fireFetch(coldWorker, coldRequest); drain();
eq('J3 cold Range passes the original request through and never caches',
   [coldWorker.fetchCalls[0].request === coldRequest, coldWorker.caches.inventory('popolsku-audio')], [true,[]]);
var ifRangeWorker = makeWorker(), ifRangeRequest = new FakeRequest(absolute(hashFile(21002)),
  { headers:{ Range:'bytes=0-1', 'If-Range':'"etag"' } });
var ifRange = fireFetch(ifRangeWorker, ifRangeRequest); drain();
eq('J4 If-Range remains un-intercepted pass-through', [ifRange.response, ifRangeWorker.fetchCalls.length], [null,0]);
var offlineWorker = makeWorker({ seed:seedAudio([hashFile(21003)]), route:function () { return P.reject(new Error('offline')); } });
var offlineWarm = fireFetch(offlineWorker, new FakeRequest(absolute(hashFile(21003)))); drain();
eq('J5 downloaded warm clip plays without network while offline',
   [offlineWarm.response.value.status, offlineWorker.fetchCalls.length], [200,0]);
ok('J6 existing device-voice and terminal Retry strings remain unchanged',
   INDEX.indexOf("Using your device's voice.") !== -1 &&
   INDEX.indexOf("Audio couldn't play. Check your connection, then try again.") !== -1 &&
   INDEX.indexOf('const AUDIO_RETRY_MSG = "Try again";') !== -1);

// K. Stale page replies and recoverable worker/channel replacement.
var channelBroken = true, replacementWorker = makeWorker();
var replaceTransport = function (command, payload, token) {
  return channelBroken ? P.reject(new Error('worker replaced')) : protocolTransport(replacementWorker)(command, payload, token);
};
var replaceEngine = runEngine(replacementWorker, files(4, 22000), { transport:replaceTransport });
var interrupted = watch(replaceEngine.start()); drain();
eq('K1 worker/channel loss yields interrupted state', interrupted.value.status, 'interrupted');
channelBroken = false;
var recovered = watch(replaceEngine.continueDownload()); drain();
eq('K2 Continue uses a fresh reconciliation and recovers', [recovered.value.status, recovered.value.present], ['complete',4]);
var staleHeld = [], staleTransport = function (command, payload, token) {
  if (command === 'offline-audio-capabilities') return P.resolve({ outcome:'supported', protocolVersion:1 });
  if (command === 'offline-audio-store-one') { var d = deferred(); staleHeld.push(d); return d.promise; }
  if (command === 'offline-audio-remove') return P.resolve({ outcome:'removed' });
  return P.resolve({ outcome:'reconciled', total:4, presentCount:0, missingCount:4,
    present:[], missing:files(4,23000).map(absolute), invalid:0, mutationGeneration:0 });
};
var staleEngine = runEngine(null, files(4,23000), { transport:staleTransport });
var oldRun = watch(staleEngine.start()); drain();
var removeRun = watch(staleEngine.remove()); drain();
eq('K3 new generation owns state before old replies arrive', removeRun.value.status, 'removed');
staleHeld.forEach(function (d) { d.resolve({ outcome:'stored' }); }); drain();
eq('K4 stale replies from old generation cannot mutate current engine state', staleEngine.getState().status, 'removed');
var unsupportedEngine = ENGINE.create([hashFile(24000)], { baseHref:ORIGIN + '/' });
var unsupportedRun = watch(unsupportedEngine.start()); drain();
eq('K5 absent service worker/MessageChannel degrades to interrupted state', unsupportedRun.value.status, 'interrupted');
var throwingEngine = runEngine(null, [hashFile(24001)], { transport:function () { throw new Error('gone'); } });
var throwingRun = watch(throwingEngine.start()); drain();
eq('K6 synchronous channel failure is contained and recoverable', throwingRun.value.status, 'interrupted');

// L. Static scope/release guards.
ok('L1 Phase 2 adds exactly one learner-visible Offline audio screen and menu entry without changing the engine',
   (INDEX.match(/id="offlineAudio"/g) || []).length === 1 &&
   (INDEX.match(/>Offline audio<\/a>/g) || []).length === 1);
eq('L2 release markers match the current candidate',
   [(INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/) || [])[1],
    (SW_SRC.match(/const CACHE\s*=\s*"([^"]+)"/) || [])[1],
    (SW_SRC.match(/const AUDIO_CACHE\s*=\s*"([^"]+)"/) || [])[1]],
   ['9.16','popolsku-v71','popolsku-audio']);
ok('L3 page engine never accesses Cache Storage directly or persistent tracking',
   ENGINE_SRC.indexOf('caches.') === -1 && ENGINE_SRC.indexOf('localStorage') === -1 &&
   ENGINE_SRC.indexOf('navigator.storage') === -1);
ok('L4 no forced service-worker activation is introduced',
   SW_SRC.indexOf('self.skipWaiting(') === -1 && SW_SRC.indexOf('self.clients.claim(') === -1);

console.log('Offline audio Phase 1 engine tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
FAILURES.forEach(function (line) { console.log('  ' + line); });
if (FAIL) throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed');
