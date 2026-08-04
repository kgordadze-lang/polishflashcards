/* Po polsku service worker
   - Bump CACHE whenever you deploy a change you want pushed to everyone. The new
     worker stages that release in its OWN cache and then waits. Tabs that were
     opened under the previous release keep being served by the previous worker
     out of the previous cache, so no page can ever get half of one release and
     half of the next. The new worker takes over the normal way: when every tab
     under the old worker is gone. There is deliberately no skipWaiting() and no
     clients.claim() here, and no update banner or forced reload.
   - Strategy: network-first for the things that change between deploys (pages,
     data-*.js, audio-manifest.json), cache-first for the things that cannot
     (scripts, fonts, icons, content-hashed MP3s).
   - Only same-origin requests in a category listed below are ever cached.
     Everything else - other origins, unknown endpoints, non-GET, non-http(s)
     schemes - is handed straight back to the browser untouched. A Range request
     for a warm clip is answered from the audio cache as a real 206 slice and is
     never written to any cache.
   - AUDIO_CACHE is deliberately versionless: MP3 filenames are content hashes,
     so a clip can never go stale. Keeping audio out of the versioned cache means
     users' accumulated clips (up to ~34MB) survive every deploy instead of being
     deleted and re-downloaded on mobile data. */

/* Machine counter for the app-shell cache. It is independent of APP_VERSION in
   index.html: a technical cache revision (a worker/caching change with no
   learner-visible difference) bumps this alone, and a release that changes what
   the learner sees bumps APP_VERSION. Either may move without the other. */
const CACHE = "popolsku-v59";
const AUDIO_CACHE = "popolsku-audio";

/* ------------------------------------------------------------------ *
 * Bounded audio retention (MLG-4A-08)
 *
 * popolsku-audio is versionless and everything in it is a validated, immutable,
 * content-hashed MP3, so the only way it can grow without bound is by
 * accumulating clips. The bound is therefore an ENTRY COUNT, not a byte budget:
 * the Cache API exposes no per-cache size, and navigator.storage.estimate() is
 * an advisory whole-origin figure that cannot be attributed to one cache. It is
 * a practical bound, not a mathematically exact byte limit, and it is honest
 * about that.
 *
 * 3,377 clips is today's complete library (verify_audio.py), so the ceiling
 * leaves room for roughly 800 future clips before anything is ever evicted: a
 * learner who warms the whole library never loses a clip to this policy.
 *
 * The policy is INSERTION-ORDER (FIFO) trimming, not LRU. Cache.keys()
 * enumerates in insertion order and a cache hit does not re-insert anything, so
 * a read cannot update recency - calling this LRU would be a lie. Because every
 * clip is immutable and re-downloadable, dropping the oldest inserted clips is
 * the cheapest correct choice: a re-played evicted clip is an ordinary cache
 * miss online, and offline it reaches the same accessible retry state as any
 * other unavailable clip.
 * ------------------------------------------------------------------ */
const AUDIO_CACHE_MAX_ENTRIES = 4200;   /* ceiling: today's 3,377 clips + ~24% headroom */
const AUDIO_CACHE_TRIM_TO = 4000;       /* trim target, so trimming is not a per-write cost */
const AUDIO_QUOTA_EVICTION_BATCH = 64;  /* oldest clips dropped before one quota retry */
const AUDIO_QUOTA_RETRY_LIMIT = 1;      /* one retry per write, structurally never a loop */
/* Cleanup on activate matches ONLY a numbered app-shell cache: "popolsku-v"
   followed by digits and nothing else. A prefix test would also swallow
   popolsku-video, popolsku-vocabulary, popolsku-vectors or a "popolsku-v56-beta"
   staging cache. The audio cache and every unrelated same-origin cache survive. */
const SHELL_CACHE_PATTERN = /^popolsku-v[0-9]+$/;

/* ------------------------------------------------------------------ *
 * Precache inventory
 *
 * REQUIRED = the offline shell. If any one of these cannot be stored the
 * install FAILS: a worker that half-installed the shell would claim to work
 * offline and then not. The document, the four helper scripts and the seven
 * data files are what the app is; audio-manifest.json is the index for the
 * pre-generated Polish pronunciation this app exists to teach with.
 *
 * OPTIONAL = everything whose absence degrades appearance or installability
 * but leaves a working, learnable offline app: the web-app manifest, the icons,
 * and the web fonts (the app has a system-font stack behind them). A flaky CDN
 * hop or a single 404 on one of these must never cost the learner their offline
 * shell - that was the Phase 4A P1.
 *
 * The root document is listed once, as "./". "./index.html" is not a second
 * entry: both URLs are the same file on this host, and canonicalKeyFor() maps
 * them (and "/?pwa=1") onto one cache key instead of storing duplicates.
 * ------------------------------------------------------------------ */
const REQUIRED_ASSETS = [
  "./",
  "./pp-usage.js",
  "./pp-answer.js",
  "./pp-distractor.js",
  "./pp-migrate.js",
  "./data-a1.js",
  "./data-a2.js",
  "./data-b1.js",
  "./data-grammar.js",
  "./data-verbs.js",
  "./data-scenarios.js",
  "./data-podcasts.js",
  "./audio-manifest.json"
];

const OPTIONAL_ASSETS = [
  "./manifest.json",
  "./favicon.svg",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png",
  "./og-image.png",
  "./fonts/plus-jakarta-sans-v12-latin-regular.woff2",
  "./fonts/plus-jakarta-sans-v12-latin-500.woff2",
  "./fonts/plus-jakarta-sans-v12-latin-600.woff2",
  "./fonts/plus-jakarta-sans-v12-latin-700.woff2",
  "./fonts/plus-jakarta-sans-v12-latin-800.woff2"
];

/* Where this worker is deployed. Everything below is expressed relative to the
   worker's own directory, so the same file works from a sub-path deployment. */
const SCOPE_PATH = self.location.pathname.replace(/[^/]*$/, "");
const ROOT_KEY = self.location.origin + SCOPE_PATH;
const INDEX_FILE = "index.html";

const DATA_FILE = /\/data-[a-z0-9-]+\.js$/;
const AUDIO_FILE = /\/audio\/[a-f0-9]+\.mp3$/;
const AUDIO_MANIFEST_PATH = SCOPE_PATH + "audio-manifest.json";

/* Generated navigation is intentionally an exact inventory, not a rule such as
   "every nested URL" or even "everything below /grammar". Each entry corresponds
   to a committed generator-owned index.html. Directory and explicit index.html
   requests share the same canonical key. Keep the deterministic Phase 4B-2
   inventory test green whenever generated pages are added or removed. */
const GENERATED_PAGE_ASSETS = [
  "./guide/",
  "./guide/listening/",
  "./grammar/",
  "./grammar/biernik-accusative/",
  "./grammar/celownik-dative/",
  "./grammar/dopelniacz-genitive/",
  "./grammar/jesli-i-gdyby-conditions/",
  "./grammar/kazdy-i-wszyscy-every-vs-all/",
  "./grammar/korespondencja-formal-writing/",
  "./grammar/ktory-relative-clauses/",
  "./grammar/liczebniki-numbers-meet-cases/",
  "./grammar/mianownik-nominative/",
  "./grammar/miejscownik-locative/",
  "./grammar/narodowosci-nationalities/",
  "./grammar/narzednik-instrumental/",
  "./grammar/pan-i-pani-formal-address/",
  "./grammar/panowie-panie-panstwo-plural-formal-address/",
  "./grammar/przeczenie-negation/",
  "./grammar/przymiotniki-adjectives-traits/",
  "./grammar/stopniowanie-comparison/",
  "./grammar/tryb-przypuszczajacy-conditional/",
  "./grammar/wolacz-vocative/",
  "./grammar/zaimki-pronouns-determiners/",
  "./grammar/zawody-professions/",
  "./grammar/zdrobnienia-diminutives/",
  "./grammar/zeby-so-that-want-to/",
  "./vocabulary/",
  "./vocabulary/everyday-polish-slang/",
  "./vocabulary/polish-corporate-slang/",
  "./vocabulary/polish-exclamations/",
  "./vocabulary/polish-idioms/",
  "./vocabulary/polish-party-slang/",
  "./vocabulary/polish-proverbs/"
];
const GENERATED_PAGE_PATHS = GENERATED_PAGE_ASSETS.map(asset => canonicalPathOf(asset));

/* The runtime cache-first allowlist is DERIVED from the precache inventory, so a
   file can never be cached at runtime under rules the install step doesn't know
   about (and vice versa). The root document is navigation, and the data files and
   the audio manifest have their own network-first branches, so they drop out. */
const STATIC_ASSET_PATHS = REQUIRED_ASSETS.concat(OPTIONAL_ASSETS)
  .map(asset => canonicalPathOf(asset))
  .filter(path => path !== null && path !== SCOPE_PATH &&
                  !DATA_FILE.test(path) && path !== AUDIO_MANIFEST_PATH);

/* Diagnostics. A cache write that fails silently is how "visit online, then use
   offline" quietly stops being true, so every skipped/failed write is counted and
   the last few failures are kept for inspection from the application panel. */
const SW_STATE = {
  cacheName: CACHE,
  audioCacheName: AUDIO_CACHE,
  requiredCached: 0,
  optionalCached: [],
  optionalFailed: [],
  installFailures: [],
  writes: { scheduled: 0, succeeded: 0, failed: 0, skipped: 0 },
  writeFailures: [],
  /* Reads that found an entry which no longer passes the write-time contract -
     almost always an entry inherited from an older worker that had no media-type
     gate. Bounded: counters plus at most 20 {key, reason} records. No bodies, no
     learner data, no unbounded URL history. */
  reads: { invalid: 0, evicted: 0, evictionFailed: 0 },
  invalidReads: [],
  /* Range work (MLG-4A-05) and audio retention (MLG-4A-08). Counters plus at
     most 20 {reason, key, message} records - no bodies, no learner content, no
     unbounded URL history, no progress. */
  range: { synthesized: 0, unsatisfiable: 0, cacheMiss: 0, passthrough: 0, bodyReadFailed: 0 },
  audio: {
    retentionChecks: 0, trimmed: 0, writeFailures: 0,
    recoveryAttempts: 0, recovered: 0, recoveryFailed: 0
  },
  audioFailures: []
};
self.ppSwState = SW_STATE;

function swWarn(message, detail) {
  if (typeof console !== "undefined" && console && typeof console.warn === "function") {
    console.warn("[po polsku sw] " + message + (detail ? " - " + detail : ""));
  }
}

function describeResponse(res) {
  if (!res) return "no response";
  return "status " + res.status + ", type " + res.type +
         ", content-type " + (mediaTypeOf(res) || "none") +
         (res.redirected ? ", redirected" : "");
}

/* ------------------------------------------------------------------ *
 * URLs and canonical cache keys
 * ------------------------------------------------------------------ */

/* Never throws: a request URL the URL parser rejects is simply not ours. */
function parseUrl(value, base) {
  try { return base === undefined ? new URL(value) : new URL(value, base); }
  catch (err) { return null; }
}

function sameOrigin(url) {
  return !!url && url.origin === self.location.origin;
}

/* "/guide/index.html" -> "/guide/", "/index.html" -> "/". Everything else is
   returned unchanged. On this host a directory URL and its index.html are the
   same bytes (see sitemap.xml and every generated page's rel=canonical), so
   caching them under two keys is how one visit ends up half-cached. */
function canonicalPath(pathname) {
  const suffix = "/" + INDEX_FILE;
  if (pathname.length >= suffix.length && pathname.slice(-suffix.length) === suffix) {
    return pathname.slice(0, pathname.length - INDEX_FILE.length);
  }
  return pathname;
}

/* THE cache key helper. It is only ever called for a same-origin request in one
   of the approved categories below, and it does three things and no more:
     - drops the fragment (never part of an HTTP cache key anyway);
     - drops the query, because for every approved category the query is either a
       cache-buster ("favicon.svg?v=17") or page-level state ("/?pwa=1") and the
       bytes on the server are identical either way;
     - folds a trailing "index.html" into its directory URL.
   It returns null for anything cross-origin, so it can never rewrite an external
   request, and it is deliberately NOT applied to unknown same-origin endpoints,
   whose responses could legitimately vary by query. It changes only the cache
   key: the browser's URL, and everything index.html reads out of location.search,
   are untouched. */
function canonicalKeyFor(url) {
  if (!sameOrigin(url)) return null;
  return url.origin + canonicalPath(url.pathname);
}

function canonicalPathOf(asset) {
  const key = canonicalKeyFor(parseUrl(asset, self.location.href));
  return key === null ? null : key.slice(self.location.origin.length);
}

/* ------------------------------------------------------------------ *
 * Response validation - one gate in front of every cache write
 *
 * A 200 is not enough. A captive portal, a misconfigured rewrite or a host that
 * answers every unknown path with the SPA shell all return a perfectly healthy
 * 200 text/html - and storing that under data-a1.js, audio-manifest.json or an
 * MP3 key poisons the offline app until the next cache version. So every write
 * also has to agree with what the key says it is.
 *
 * The accepted types are the ones this repository is actually served with, as
 * measured against the deployment, not a generic list. Two spellings are allowed
 * where both are current and standards-blessed: JavaScript may arrive as
 * text/javascript (what the deployment sends today, and what the HTML spec now
 * prescribes) or application/javascript (the older registration still emitted by
 * plenty of static hosts), and the web-app manifest may arrive as
 * application/manifest+json (its registered type) or application/json (what a
 * plain static host derives from the .json extension).
 * ------------------------------------------------------------------ */
const MEDIA_GROUPS = {
  document: ["text/html"],
  script: ["text/javascript", "application/javascript"],
  json: ["application/json"],
  manifest: ["application/manifest+json", "application/json"],
  audio: ["audio/mpeg"],
  svg: ["image/svg+xml"],
  png: ["image/png"],
  font: ["font/woff2"]
};

const WEB_APP_MANIFEST_PATH = SCOPE_PATH + "manifest.json";

/* Which group a cache key belongs to, decided from the canonical key alone so
   that install and runtime can never disagree. A path this worker has no media
   rule for is not cacheable at all: fail closed, so adding an asset class to the
   allowlist without deciding its type cannot silently cache anything. */
function mediaGroupForPath(path) {
  if (typeof path !== "string" || path === "") return null;
  if (path.slice(-1) === "/") return "document";       /* "/" and every generated page directory */
  if (path === WEB_APP_MANIFEST_PATH) return "manifest";
  if (/\.js$/.test(path)) return "script";
  if (/\.json$/.test(path)) return "json";
  if (/\.mp3$/.test(path)) return "audio";
  if (/\.svg$/.test(path)) return "svg";
  if (/\.png$/.test(path)) return "png";
  if (/\.woff2$/.test(path)) return "font";
  return null;
}

/* "text/HTML; charset=UTF-8" -> "text/html". Null when the header is absent. */
function mediaTypeOf(res) {
  if (!res || !res.headers || typeof res.headers.get !== "function") return null;
  const raw = res.headers.get("content-type");
  if (!raw) return null;
  const type = String(raw).split(";")[0].trim().toLowerCase();
  return type === "" ? null : type;
}

/* A response with no Content-Type at all is NOT cached. Every asset this worker
   stores is served by the app's own origin, which types all of them; a response
   we cannot check is a response we cannot key correctly, and a missing type is
   exactly what a stripped-down error path or an interception layer produces. */
function hasExpectedMediaType(res, key) {
  const group = mediaGroupForPath(pathOfKey(key));
  if (group === null) return false;
  const type = mediaTypeOf(res);
  if (type === null) return false;
  return MEDIA_GROUPS[group].indexOf(type) !== -1;
}

function pathOfKey(key) {
  if (typeof key !== "string") return null;
  const origin = self.location.origin;
  return key.slice(0, origin.length) === origin ? key.slice(origin.length) : null;
}

function isCacheableResponse(res, key) {
  if (!res) return false;
  if (res.ok !== true) return false;                  /* never cache an error page */
  if (res.status !== 200) return false;               /* also rules out 206 partial bodies */
  if (res.redirected === true) return false;          /* the key would not describe the body */
  if (res.type !== undefined && res.type !== "basic" && res.type !== "default") {
    return false;                                     /* opaque/opaqueredirect/error/cors */
  }
  return hasExpectedMediaType(res, key);              /* the body must match the key */
}

function isRangeRequest(request) {
  if (!request || !request.headers || typeof request.headers.get !== "function") return false;
  return !!request.headers.get("range");
}

function requestHeader(request, name) {
  if (!request || !request.headers || typeof request.headers.get !== "function") return null;
  return request.headers.get(name);
}

/* Is this cache key one of the immutable content-hashed clips? Used to keep both
   Range synthesis and retention eviction inside the one asset class they are
   allowed to touch. */
function isApprovedAudioKey(key) {
  const path = pathOfKey(key);
  return typeof path === "string" && AUDIO_FILE.test(path);
}

/* ------------------------------------------------------------------ *
 * Range (MLG-4A-05)
 *
 * A media element that asks for part of a clip must not be told "here is all of
 * it, status 200" - that is not what it asked for, and on the browsers that
 * enforce it, offline replay simply fails. This worker answers a partial request
 * for a WARM, VALIDATED clip with a real 206 sliced out of the cached body, and
 * refuses to guess about anything else.
 * ------------------------------------------------------------------ */

/* One byte range, as much of the RFC 9110 grammar as this worker supports:
   "bytes=" then exactly one of first-last / first- / -suffix. Whitespace around
   the unit and the spec is tolerated and the unit is case-insensitive. A comma
   (multiple ranges), a unit other than bytes, a non-numeric bound, an empty spec
   or a second dash is deliberately NOT ours: the caller leaves such a request to
   the network instead of inventing a partial response for it. */
function parseByteRange(header) {
  if (typeof header !== "string") return null;
  const raw = header.trim();
  const eq = raw.indexOf("=");
  if (eq === -1) return null;
  if (raw.slice(0, eq).trim().toLowerCase() !== "bytes") return null;
  const spec = raw.slice(eq + 1).trim();
  if (spec === "" || spec.indexOf(",") !== -1) return null;
  const dash = spec.indexOf("-");
  if (dash === -1 || spec.indexOf("-", dash + 1) !== -1) return null;
  const first = spec.slice(0, dash).trim();
  const last = spec.slice(dash + 1).trim();
  const DIGITS = /^[0-9]+$/;
  if (first === "") {
    if (!DIGITS.test(last)) return null;
    return { suffix: parseInt(last, 10), start: null, end: null };
  }
  if (!DIGITS.test(first)) return null;
  if (last === "") return { suffix: null, start: parseInt(first, 10), end: null };
  if (!DIGITS.test(last)) return null;
  return { suffix: null, start: parseInt(first, 10), end: parseInt(last, 10) };
}

/* Resolve a parsed range against the real length of the cached body. Returns
   null when the range cannot be satisfied - which is a 416, never a guess.
   An end beyond the last byte is clamped, as the specification requires; a start
   beyond the last byte is not satisfiable; a zero-length suffix asks for nothing
   and is not satisfiable either. */
function resolveByteRange(range, total) {
  if (!range || typeof total !== "number" || total < 0) return null;
  let start, end;
  if (range.suffix !== null) {
    if (range.suffix === 0 || total === 0) return null;
    start = range.suffix >= total ? 0 : total - range.suffix;
    end = total - 1;
  } else {
    if (total === 0 || range.start >= total) return null;
    start = range.start;
    end = range.end === null ? total - 1 : Math.min(range.end, total - 1);
    if (end < start) return null;
  }
  return { start: start, end: end, length: end - start + 1, total: total };
}

/* Validators travel with the bytes they describe, so a synthesized 206 carries
   the cached response's own ETag/Last-Modified. The full body's Content-Length
   is deliberately NOT carried over - it would describe bytes this response does
   not contain. */
function partialHeaders(res, span) {
  const headers = {
    "Content-Type": "audio/mpeg",
    "Content-Range": "bytes " + span.start + "-" + span.end + "/" + span.total,
    "Content-Length": String(span.length),
    "Accept-Ranges": "bytes"
  };
  const etag = res && res.headers && typeof res.headers.get === "function" ? res.headers.get("etag") : null;
  const modified = res && res.headers && typeof res.headers.get === "function" ? res.headers.get("last-modified") : null;
  if (etag) headers["ETag"] = etag;
  if (modified) headers["Last-Modified"] = modified;
  return headers;
}

function unsatisfiableRangeResponse(total) {
  return new Response(null, {
    status: 416,
    statusText: "Range Not Satisfiable",
    headers: { "Content-Range": "bytes */" + total, "Accept-Ranges": "bytes" }
  });
}

/* Remove exactly one entry from the audio cache. Used when a cached clip passes
   header validation but its body cannot be read: the entry is unusable, but a
   failed delete must still degrade to "not served this time", never to "served
   anyway", and never to clearing the cache. */
function dropAudioEntry(key) {
  return caches.open(AUDIO_CACHE).then(cache => cache.delete(key)).then(deleted => {
    if (deleted) SW_STATE.reads.evicted++;
    else SW_STATE.reads.evictionFailed++;
    if (deleted && audioEntryEstimate !== null) audioEntryEstimate--;
  }, err => {
    SW_STATE.reads.evictionFailed++;
    swWarn("could not drop unreadable clip " + key, err && err.message);
  });
}

/* The whole Range contract for one warm-or-cold clip:
     valid cached full body  -> exact 206 slice, never cached, cache untouched
     valid body, bad range   -> 416 with bytes STAR/total, never cached
     unreadable cached body  -> drop that one entry, then the original request
     cache miss              -> the original request, Range header intact
   The synthetic response is built from a copy of the cached bytes; the stored
   entry itself is never rewritten. */
function audioRangeResponse(event, key, range) {
  return cacheMatch(AUDIO_CACHE, key).then(hit => {
    if (!hit) {
      SW_STATE.range.cacheMiss++;
      return fetch(event.request);
    }
    return hit.arrayBuffer().then(buffer => {
      const total = buffer && typeof buffer.byteLength === "number" ? buffer.byteLength : 0;
      const span = resolveByteRange(range, total);
      if (!span) {
        SW_STATE.range.unsatisfiable++;
        return unsatisfiableRangeResponse(total);
      }
      SW_STATE.range.synthesized++;
      return new Response(buffer.slice(span.start, span.end + 1), {
        status: 206,
        statusText: "Partial Content",
        headers: partialHeaders(hit, span)
      });
    }, err => {
      SW_STATE.range.bodyReadFailed++;
      recordAudioFailure("body-read", key, err);
      swWarn("cached clip body unreadable " + key, err && err.message);
      return dropAudioEntry(key).then(() => fetch(event.request));
    });
  });
}

/* ------------------------------------------------------------------ *
 * Request classification - the whole contract in one readable function
 * ------------------------------------------------------------------ */
function classifyRequest(request) {
  if (!request || request.method !== "GET") return "non-get";
  const url = parseUrl(request.url);
  if (!url) return "unsupported-scheme";
  /* Browser extensions inject chrome-extension:// requests into every page and the
     Cache API only supports http/https - trying to cache one throws. */
  if (url.protocol !== "http:" && url.protocol !== "https:") return "unsupported-scheme";
  if (!sameOrigin(url)) return "cross-origin";
  /* Range: no whole response may ever be stored for a partial request. The
     branch below answers a warm clip with a 206 and leaves everything else to
     the network; either way nothing is written. */
  if (isRangeRequest(request)) return "range";
  const path = canonicalPath(url.pathname);
  if (request.mode === "navigate") {
    if (path === SCOPE_PATH) return "root-navigation";
    if (GENERATED_PAGE_PATHS.indexOf(path) !== -1) return "generated-navigation";
    return "unknown-navigation";
  }
  if (DATA_FILE.test(path)) return "data";
  if (path === AUDIO_MANIFEST_PATH) return "audio-manifest";
  if (AUDIO_FILE.test(path)) return "audio";
  if (STATIC_ASSET_PATHS.indexOf(path) !== -1) return "static";
  return "unknown";                                   /* network-only, never cached */
}

/* ------------------------------------------------------------------ *
 * The shared runtime cache-write contract
 *
 * Every runtime branch writes through this one function. It clones before the
 * page reads the body, validates before it writes, keeps the fetch event alive
 * until the write settles, and swallows open/put/quota failures so that a cache
 * problem can never turn a successful online response into a failed one.
 * ------------------------------------------------------------------ */
function keepAlive(event, promise) {
  if (!event || typeof event.waitUntil !== "function") return;
  /* If the event is already past its extendable lifetime the browser throws; the
     write still runs, it just no longer holds the worker open. */
  try { event.waitUntil(promise); } catch (err) { swWarn("waitUntil unavailable", err && err.message); }
}

function recordWriteFailure(key, err) {
  SW_STATE.writes.failed++;
  if (SW_STATE.writeFailures.length < 20) SW_STATE.writeFailures.push({ key: key, message: err && err.message });
  swWarn("cache write failed for " + key, err && err.message);
}

/* Bounded audio diagnostics: at most 20 records, each one a reason, a cache key
   and an error message. Never a body, never learner content. */
function recordAudioFailure(reason, key, err) {
  if (SW_STATE.audioFailures.length < 20) {
    SW_STATE.audioFailures.push({ reason: reason, key: key, message: err && err.message });
  }
}

/* How many clips popolsku-audio holds, or null when this worker does not know
   yet. It is a TRIGGER, not an accounting record: every trim works from the
   cache's real keys and resets this to the truth, so an over-count (a repair
   write replacing an existing key, say) costs at most one extra scan and can
   never delete more than the real key list allows. */
let audioEntryEstimate = null;

/* Retention maintenance, run only after a NEW clip was stored. A cache HIT does
   no bookkeeping at all, so warm offline playback never scans the cache. */
function afterAudioWrite(key) {
  if (audioEntryEstimate !== null) {
    audioEntryEstimate++;
    if (audioEntryEstimate <= AUDIO_CACHE_MAX_ENTRIES) return undefined;
  }
  return trimAudioCache(key);
}

/* One stored audio-cache entry as retention sees it.

   The distinction matters: `request`/`url` is what the cache ACTUALLY holds and
   therefore what must be deleted, while `canonicalKey` is identity only - is this
   an approved hashed MP3, and is it the clip we have just written?

   popolsku-audio is versionless and survives every deploy, so it can still hold
   an entry a much older worker stored under a query-bearing URL such as
   "/audio/<hash>.mp3?legacy=1". Deleting canonicalKey for that entry would delete
   a different record - or nothing at all - and the real one would sit in the
   cache forever, outside any bound. Retention therefore classifies by canonical
   path and deletes by stored request. */
function audioCacheEntries(requests) {
  const entries = [];
  (requests || []).forEach(request => {
    const url = request && typeof request.url === "string" ? request.url : null;
    if (url === null) return;
    const canonicalKey = canonicalKeyFor(parseUrl(url));
    if (canonicalKey === null || !isApprovedAudioKey(canonicalKey)) return;
    entries.push({ request: request, url: url, canonicalKey: canonicalKey });
  });
  return entries;
}

/* Delete a bounded list of approved MP3 entries from popolsku-audio, containing
   every individual failure. Nothing but audioCacheEntries() output is ever
   passed in here, and each delete targets the exact stored request. */
function deleteAudioEntries(cache, entries) {
  return Promise.all(entries.map(entry => cache.delete(entry.request).then(deleted => {
    if (!deleted) return;
    SW_STATE.audio.trimmed++;
    if (audioEntryEstimate !== null) audioEntryEstimate--;
  }, err => {
    swWarn("audio retention could not delete " + entry.url, err && err.message);
    recordAudioFailure("trim", entry.url, err);
  })));
}

/* Insertion-order (FIFO) trim down to AUDIO_CACHE_TRIM_TO. Only approved MP3
   keys are considered and only approved MP3 keys are deleted; the clip that was
   just written is protected; the complete cache is never cleared. */
function trimAudioCache(protectedKey) {
  SW_STATE.audio.retentionChecks++;
  return caches.open(AUDIO_CACHE).then(cache => cache.keys().then(requests => {
    const entries = audioCacheEntries(requests);
    audioEntryEstimate = entries.length;
    if (entries.length <= AUDIO_CACHE_MAX_ENTRIES) return undefined;
    /* Only the EXACT entry just written is protected. A redundant legacy query
       variant of that same clip is not the clip we wrote - it is duplicate
       storage for bytes we already hold, and removing it is the point. */
    const victims = entries.slice(0, entries.length - AUDIO_CACHE_TRIM_TO)
      .filter(entry => entry.url !== protectedKey);
    return deleteAudioEntries(cache, victims);
  })).then(undefined, err => {
    swWarn("audio retention check failed", err && err.message);
    recordAudioFailure("retention", protectedKey, err);
    audioEntryEstimate = null;
  });
}

/* A cache.put failure for a clip is treated as storage pressure whatever the
   browser called it - QuotaExceededError, a bare DOMException, a vendor name we
   have never seen. Sniffing one error name would silently skip recovery on the
   browsers this was not tested on, and the recovery is safe either way: bounded
   eviction of already-expendable immutable clips, then exactly one retry.
   `attempt` makes the "at most once" structural rather than a comment. */
function recoverAudioWrite(key, spare, attempt) {
  if (!spare || attempt > AUDIO_QUOTA_RETRY_LIMIT) return undefined;
  SW_STATE.audio.recoveryAttempts++;
  audioEntryEstimate = null;
  return caches.open(AUDIO_CACHE).then(cache => cache.keys().then(requests => {
    const victims = audioCacheEntries(requests)
      .filter(entry => entry.url !== key)
      .slice(0, AUDIO_QUOTA_EVICTION_BATCH);
    return deleteAudioEntries(cache, victims);
  }).then(() => cache.put(key, spare))).then(() => {
    SW_STATE.audio.recovered++;
  }, err => {
    SW_STATE.audio.recoveryFailed++;
    recordAudioFailure("quota-retry", key, err);
    swWarn("audio quota recovery failed for " + key, err && err.message);
  });
}

/* Returns true when a write was scheduled, false when the response was not
   cacheable. Never returns a promise the response path has to wait on. */
function cacheWrite(event, cacheName, key, response) {
  if (!key || !isCacheableResponse(response, key)) { SW_STATE.writes.skipped++; return false; }
  const clip = cacheName === AUDIO_CACHE && isApprovedAudioKey(key);
  let copy, spare = null;
  try {
    copy = response.clone();
    /* One extra clone, taken before anything can read the body, is what makes a
       single quota retry possible at all: a consumed response cannot be stored. */
    if (clip) spare = response.clone();
  }
  catch (err) { recordWriteFailure(key, err); return false; }
  const write = caches.open(cacheName)
    .then(cache => cache.put(key, copy))
    .then(() => {
      SW_STATE.writes.succeeded++;
      return clip ? afterAudioWrite(key) : undefined;
    }, err => {
      recordWriteFailure(key, err);
      if (!clip) return undefined;
      SW_STATE.audio.writeFailures++;
      recordAudioFailure("write", key, err);
      return recoverAudioWrite(key, spare, 1);
    });
  SW_STATE.writes.scheduled++;
  keepAlive(event, write);
  return true;
}

/* ------------------------------------------------------------------ *
 * Install
 * ------------------------------------------------------------------ */
function settleAll(promises) {
  return Promise.all(promises.map(p => p.then(
    value => ({ ok: true, value: value }),
    error => ({ ok: false, error: error })
  )));
}

/* One precache entry: fetch it past the HTTP cache, validate it, store it under
   its canonical key. Rejects - loudly - if the asset cannot be trusted. */
function precacheOne(cache, asset) {
  const key = canonicalKeyFor(parseUrl(asset, self.location.href));
  if (!key) return Promise.reject(new Error("unusable precache entry " + asset));
  return fetch(key, { cache: "reload" }).then(res => {
    if (!isCacheableResponse(res, key)) {
      throw new Error("unusable precache response for " + asset + " (" + describeResponse(res) + ")");
    }
    return cache.put(key, res);
  });
}

function precacheRequired(cache) {
  return settleAll(REQUIRED_ASSETS.map(asset => precacheOne(cache, asset))).then(results => {
    const failed = results.filter(r => !r.ok);
    if (failed.length) {
      failed.forEach(r => SW_STATE.installFailures.push(r.error && r.error.message));
      throw failed[0].error;
    }
    SW_STATE.requiredCached = results.length;
  });
}

/* Attempted one by one; a failure is recorded and dropped. The install event is
   never rejected because a font or an icon did not arrive. */
function precacheOptional(cache) {
  return settleAll(OPTIONAL_ASSETS.map(asset => precacheOne(cache, asset))).then(results => {
    results.forEach((result, i) => {
      if (result.ok) { SW_STATE.optionalCached.push(OPTIONAL_ASSETS[i]); return; }
      SW_STATE.optionalFailed.push(OPTIONAL_ASSETS[i]);
      swWarn("optional asset skipped: " + OPTIONAL_ASSETS[i], result.error && result.error.message);
    });
  });
}

/* A failed install must leave nothing behind: the half-written new cache is
   removed, the currently active worker keeps its own cache and its clients, and
   the browser is free to retry the install later. */
function installShell() {
  return caches.open(CACHE)
    .then(cache => precacheRequired(cache).then(() => precacheOptional(cache)))
    .catch(err => {
      swWarn("install failed, discarding incomplete " + CACHE, err && err.message);
      return caches.delete(CACHE).then(() => { throw err; }, () => { throw err; });
    });
}

self.addEventListener("install", e => {
  e.waitUntil(installShell());
});

/* ------------------------------------------------------------------ *
 * Activate
 *
 * This only ever runs once the previous worker no longer controls a page, so
 * deleting the previous shell cache here cannot pull assets out from under an
 * open tab. A worker that is merely waiting deletes nothing.
 * ------------------------------------------------------------------ */
function isObsoleteShellCache(name) {
  if (typeof name !== "string") return false;
  if (name === CACHE || name === AUDIO_CACHE) return false;
  return SHELL_CACHE_PATTERN.test(name);
}

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(isObsoleteShellCache).map(k => caches.delete(k))
    ))
  );
});

/* ------------------------------------------------------------------ *
 * Fetch
 * ------------------------------------------------------------------ */

/* THE cache read helper. Every application read names the cache it reads from
   AND re-validates what it finds.

   Naming the cache matters because caches.match() without a cacheName searches
   EVERY cache on the origin in creation order, so an older, unrelated or
   third-party cache holding the same URL would win over this release's own
   shell - and a shell entry could answer an audio request, or vice versa.

   Re-validating matters because writing correctly is only half the contract.
   popolsku-audio is deliberately versionless and survives every deploy, so it
   can still hold clips written by a worker that had no media-type gate: a
   captive-portal login page stored under an MP3 key stays there forever and no
   cache version bump will ever remove it. A read is therefore held to exactly
   the same standard as a write - isCacheableResponse(hit, key) - and an entry
   that fails is evicted rather than served.

   The eviction is chained, not fired and forgotten, for two reasons: the caller
   only continues once the bad entry is really gone, so a repair write cannot
   race the delete; and the whole thing sits inside the fetch event's
   respondWith chain, so the event stays alive for it. Validation reads headers
   only - the body is never touched, so the learner's response is intact either
   way. Whatever happens, an invalid entry is never returned: a failed delete
   degrades to "not served this time", not to "served anyway". */
function cacheMatch(cacheName, key) {
  return caches.open(cacheName)
    .then(cache => cache.match(key).then(hit => {
      if (!hit) return undefined;
      if (isCacheableResponse(hit, key)) return hit;
      return evictInvalidEntry(cache, cacheName, key, hit);
    }))
    .then(hit => hit, err => {
      swWarn("cache read failed for " + key, err && err.message);
      return undefined;
    });
}

/* Always resolves undefined, so the caller falls through to its normal network
   or offline path and repairs the entry on the way if it can. */
function evictInvalidEntry(cache, cacheName, key, hit) {
  const reason = describeResponse(hit);
  SW_STATE.reads.invalid++;
  if (SW_STATE.invalidReads.length < 20) {
    SW_STATE.invalidReads.push({ cache: cacheName, key: key, reason: reason });
  }
  swWarn("evicting invalid cache entry " + key + " from " + cacheName, reason);
  return cache.delete(key).then(deleted => {
    if (deleted) SW_STATE.reads.evicted++;
    else {
      SW_STATE.reads.evictionFailed++;
      swWarn("invalid cache entry not removed " + key, "delete reported no match");
    }
    return undefined;
  }, err => {
    SW_STATE.reads.evictionFailed++;
    swWarn("could not evict invalid cache entry " + key, err && err.message);
    return undefined;
  });
}

/* Network-first: fresh when online, cached copy when offline. Used for the things
   that legitimately change between deploys. cache:"no-store" skips the browser's
   own HTTP cache so this always asks for the real latest copy. */
function networkFirst(event, key, offlineMiss) {
  event.respondWith(
    fetch(event.request, { cache: "no-store" })
      .then(res => { cacheWrite(event, CACHE, key, res); return res; })
      .catch(() => cacheMatch(CACHE, key).then(hit =>
        hit || (offlineMiss ? offlineMiss() : undefined)))
  );
}

/* An unvisited generated page cannot safely receive the root document while the
   address bar stays nested: index.html has relative dependencies. Redirect the
   navigation itself to the canonical root instead. The redirect has no PWA/query
   marker, is never passed to cacheWrite(), and cannot loop because root navigation
   has no redirect fallback. */
function redirectGeneratedNavigationToRoot() {
  return Response.redirect(ROOT_KEY, 302);
}

/* Cache-first: immutable assets. Populate on first fetch, serve from cache after.
   Reads and writes name the same cache. */
function cacheFirst(event, cacheName, key) {
  event.respondWith(
    cacheMatch(cacheName, key).then(hit => hit || fetch(event.request).then(res => {
      cacheWrite(event, cacheName, key, res);
      return res;
    }))
  );
}

self.addEventListener("fetch", e => {
  const category = classifyRequest(e.request);

  /* Not ours: no respondWith at all, so the browser does exactly what it would do
     without a service worker. */
  if (category === "non-get" || category === "unsupported-scheme" ||
      category === "cross-origin" || category === "unknown" ||
      category === "unknown-navigation") return;

  const url = parseUrl(e.request.url);
  const key = canonicalKeyFor(url);
  if (!key) return;

  /* A partial request never produces a cache write, in any branch. A warm,
     validated clip is answered with a real 206 sliced out of the cached body
     (MLG-4A-05); everything this worker cannot answer exactly is handed to the
     network with its original headers intact. */
  if (category === "range") {
    if (!AUDIO_FILE.test(canonicalPath(url.pathname))) return;   /* not this policy's business */
    /* If-Range asks us to compare a validator against the CURRENT representation.
       This worker holds a copy whose validators may be older than the origin's,
       so answering a conditional resume from cache risks handing back bytes from
       the wrong representation. Documented, conservative and tested: the original
       request goes to the network untouched. */
    if (requestHeader(e.request, "if-range")) { SW_STATE.range.passthrough++; return; }
    const range = parseByteRange(requestHeader(e.request, "range"));
    /* Multiple ranges, an unsupported unit, or anything malformed: no partial
       response is invented and no multipart body is ever synthesized. */
    if (!range) { SW_STATE.range.passthrough++; return; }
    e.respondWith(audioRangeResponse(e, key, range));
    return;
  }

  /* Root and generated pages are both network-first. Root falls back only to its
     own canonical shell key. A generated page falls back only to its own exact
     canonical page; on a miss it redirects to root. Unknown navigations are left
     to the browser above and never receive a silent shell response. */
  if (category === "root-navigation") { networkFirst(e, key, null); return; }
  if (category === "generated-navigation") {
    networkFirst(e, key, redirectGeneratedNavigationToRoot);
    return;
  }

  /* Lesson data: editing a data-*.js file and re-uploading reaches users on their
     next online visit with no cache-version bump needed. */
  if (category === "data") { networkFirst(e, key, false); return; }

  /* The audio manifest: regenerate audio, re-upload the manifest, users pick up
     the new entries on their next online visit. */
  if (category === "audio-manifest") { networkFirst(e, key, false); return; }

  /* MP3s: the filename IS the content hash, so if the URL is the same the audio is
     the same and it never needs revalidation. Stored in the versionless audio
     cache so clips survive version bumps. */
  if (category === "audio") { cacheFirst(e, AUDIO_CACHE, key); return; }

  /* Scripts, fonts, icons, the web-app manifest: same-origin, in the precache
     inventory, immutable within a release. */
  if (category === "static") { cacheFirst(e, CACHE, key); return; }
});
