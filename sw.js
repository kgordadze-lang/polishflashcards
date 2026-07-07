/* Po polsku service worker
   - Bump CACHE version whenever you deploy a change you want pushed to everyone.
   - Strategy: network-first for the page itself (fresh content when online,
     cached copy when offline), cache-first for everything else (fonts, icons). */

const CACHE = "popolsku-v5";
const ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./favicon.svg",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png",
  "./og-image.png"
];

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;

  /* The app shell: try the network first so deploys reach users, fall back to cache offline. */
  if (e.request.mode === "navigate") {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put("./index.html", copy));
          return res;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  /* Everything else (fonts, icons): cache-first, populate on first fetch. */
  e.respondWith(
    caches.match(e.request, { ignoreSearch: false }).then(hit =>
      hit ||
      fetch(e.request).then(res => {
        if (res.ok || res.type === "opaque") {
          const copy = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, copy));
        }
        return res;
      })
    )
  );
});
