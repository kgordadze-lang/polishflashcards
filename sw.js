/* Po polsku service worker
   - Bump CACHE version whenever you deploy a change you want pushed to everyone.
   - Strategy: network-first for the page itself (fresh content when online,
     cached copy when offline), cache-first for everything else (fonts, icons).
   - AUDIO_CACHE is deliberately versionless: MP3 filenames are content hashes,
     so a clip can never go stale. Keeping audio out of the versioned cache means
     users' accumulated clips (up to ~34MB) survive every deploy instead of being
     deleted and re-downloaded on mobile data. */

const CACHE = "popolsku-v38";        /* machine counter - also bump APP_VERSION in index.html (human-facing, date format) */
const AUDIO_CACHE = "popolsku-audio";
const ASSETS = [
  "./",
  "./index.html",
  "./data-a1.js",
  "./data-a2.js",
  "./data-b1.js",
  "./data-grammar.js",
  "./data-verbs.js",
  "./data-scenarios.js",
  "./data-podcasts.js",
  "./audio-manifest.json",
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

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE && k !== AUDIO_CACHE)   /* audio survives version bumps */
            .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;

  /* Ignore anything that isn't an http(s) request. Browser extensions inject
     chrome-extension:// requests into every page, and the Cache API only supports
     http/https - trying to cache them throws "Request scheme 'chrome-extension' is
     unsupported". Skipping here lets the browser handle those requests normally. */
  const url = new URL(e.request.url);
  if (url.protocol !== "http:" && url.protocol !== "https:") return;

  /* Page navigations: network-first so deploys reach users, cache fallback offline.
     Only the app shell itself ("/" or "/index.html") may overwrite the cached shell -
     other pages (e.g. /grammar/...) are cached under their own URL. Without this
     split, visiting a grammar page would replace the cached shell, and the next
     offline launch of the installed app would open that page instead of the app.
     cache:"no-store" skips the browser's regular HTTP cache too, so this always asks
     the network for the real latest copy instead of a possibly-stale in-between one. */
  if (e.request.mode === "navigate") {
    const isShell = url.pathname === "/" || url.pathname === "/index.html";
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then(res => {
          if (res.ok) {                     /* never cache an error page */
            const copy = res.clone();
            caches.open(CACHE).then(c => c.put(isShell ? "./index.html" : e.request, copy));
          }
          return res;
        })
        .catch(() =>
          caches.match(isShell ? "./index.html" : e.request)
            .then(hit => hit || caches.match("./index.html"))   /* unvisited page offline -> open the app */
        )
    );
    return;
  }

  /* Lesson data: network-first too, so editing a data-*.js file and re-uploading
     reaches users on their next online visit with no cache-version bump needed.
     Falls back to the cached copy when offline. cache:"no-store" skips the browser's
     regular HTTP cache too, so edits show up immediately instead of waiting on it. */
  if (/\/data-[a-z0-9-]+\.js(\?|$)/.test(e.request.url)) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, copy));
          }
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  /* The audio manifest: network-first, so when you regenerate audio and re-upload
     the manifest, users pick up the new entries on their next online visit.
     Falls back to the cached copy when offline. */
  if (/\/audio-manifest\.json(\?|$)/.test(e.request.url)) {
    e.respondWith(
      fetch(e.request, { cache: "no-store" })
        .then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then(c => c.put(e.request, copy));
          }
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  /* Audio MP3 files: cache-first, because the filename IS the content hash -
     if the URL is the same, the audio is the same. Never needs revalidation.
     Stored in the versionless AUDIO_CACHE so clips survive version bumps.
     Populates the cache on first play, then serves from cache forever after. */
  if (/\/audio\/[a-f0-9]+\.mp3(\?|$)/.test(e.request.url)) {
    e.respondWith(
      caches.match(e.request).then(hit =>
        hit ||
        fetch(e.request).then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(AUDIO_CACHE).then(c => c.put(e.request, copy));
          }
          return res;
        })
      )
    );
    return;
  }

  /* Everything else (fonts, icons): cache-first, populate on first fetch. */
  e.respondWith(
    caches.match(e.request, { ignoreSearch: false }).then(hit =>
      hit ||
      fetch(e.request).then(res => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      })
    )
  );
});
