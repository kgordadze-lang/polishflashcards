/* Po polsku - progress migration engine (v1 -> v2, and future v2 -> v2 revisions)
   -------------------------------------------------------------------------------
   Loaded by index.html BEFORE the app reads any progress. Also loadable standalone
   in JavaScriptCore for deterministic tests (see tests/test_migration.js) - it
   touches no browser API except through the `storage` object you pass in.

   Design:
   - Learning identity lives on stable content IDs (see data-*.js `id` fields).
     This engine maps the old text-keyed v1 store onto those IDs.
   - Audio stays content-hash keyed elsewhere; IDs are never tied to audio files.
   - v2 carries schemaVersion (2) AND migrationRevision, so later STRUCTURAL
     migrations (a card split/merge/retire) can each run exactly once, in order,
     even on a store that is already v2 (e.g. a restored old backup).
     We never rely on a blunt "if v2 exists, return".
   - Raw v1 is preserved before anything and never auto-deleted. A migration that
     fails validation never overwrites a valid existing v2. */
(function (global) {
  "use strict";
  var PP_MIGRATE = {};

  PP_MIGRATE.SCHEMA_VERSION = 2;
  /* Bump this (and push a matching entry to REVISIONS) when a content change alters
     STRUCTURE rather than wording - e.g. splitting one card into two became revision 2.
     A pure wording correction keeps its id and needs no new revision. */
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = 2;

  PP_MIGRATE.KEYS = {
    v1: "popolsku-progress-v1",
    v1backup: "popolsku-progress-v1-backup",
    v2: "popolsku-progress-v2",
    v2recovery: "popolsku-progress-v2-recovery",   /* invalid v2 is parked here before a rebuild */
    unmapped: "popolsku-progress-v2-unmapped"
  };

  /* Legacy maps - keys are FROZEN to the ORIGINAL text-keyed wording, i.e. exactly what
     real users still have in their v1 store. Never "tidy" a key to match the current
     `pl`: the key is the old text, and changing it silently orphans that user's progress.
     Card renames, wording corrections and splits extend `cards`; a retired intro card
     would extend `retired`, which is empty today. */
  PP_MIGRATE.LEGACY = {
    schema: 2,
    topics: {},   /* "LEVEL|display name" -> topic id            (topic renames)   */
    /* original combined `pl` -> final card id(s). Split cards map to
       [primary, ...siblings]; kept cards whose `pl` changed map to [id]. */
    cards: {
    "a1-about-me": {"mój / moja": ["a1-about-me-017"], "żonaty / mężatka": ["a1-about-me-024"], "kawaler / panna": ["a1-about-me-025"], "nauczyciel / nauczycielka": ["a1-about-me-026", "a1-about-me-029"], "lekarz / lekarka": ["a1-about-me-027", "a1-about-me-030"]},
    "a1-cafe": {"karta / menu": ["a1-cafe-015"], "gorący / zimny": ["a1-cafe-017", "a1-cafe-021"], "duży / mały": ["a1-cafe-018", "a1-cafe-022"]},
    "a1-days-time": {"dzień / tydzień": ["a1-days-time-008", "a1-days-time-023"], "dziś / dzisiaj": ["a1-days-time-010"], "o siódmej / o ósmej": ["a1-days-time-019"], "teraz / później": ["a1-days-time-021", "a1-days-time-024"], "zawsze / nigdy": ["a1-days-time-022", "a1-days-time-025"]},
    "a1-directions": {"tutaj / tu": ["a1-directions-007"]},
    "a1-family-people": {"syn / córka": ["a1-family-people-006", "a1-family-people-019"], "mąż / żona": ["a1-family-people-007", "a1-family-people-020"], "dziecko / dzieci": ["a1-family-people-008", "a1-family-people-021"], "przyjaciel / przyjaciółka": ["a1-family-people-011", "a1-family-people-022"], "znajomy / znajoma": ["a1-family-people-012", "a1-family-people-023"], "kolega / koleżanka": ["a1-family-people-013", "a1-family-people-024"], "chłopak / dziewczyna": ["a1-family-people-014", "a1-family-people-025"], "pan / pani": ["a1-family-people-018", "a1-family-people-026"]},
    "a1-first-phrases": {"Tak / Nie": ["a1-first-phrases-009", "a1-first-phrases-028"]},
    "a1-food-basics": {"ryż / makaron": ["a1-food-basics-015", "a1-food-basics-022"], "lubię / nie lubię": ["a1-food-basics-019", "a1-food-basics-023"], "głodny / chce mi się pić": ["a1-food-basics-021", "a1-food-basics-024"]},
    "a1-fruit-vegetables": {"kilo / pół kilo": ["a1-fruit-vegetables-021", "a1-fruit-vegetables-024"], "świeży / dojrzały": ["a1-fruit-vegetables-022", "a1-fruit-vegetables-025"]},
    "a1-numbers-prices": {"drogo / tanio": ["a1-numbers-prices-020", "a1-numbers-prices-021"]},
    "a2-appearance-clothes": {"założyć / zakładać": ["a2-appearance-clothes-005"], "blondyn / blondynka": ["a2-appearance-clothes-019", "a2-appearance-clothes-032"], "za mały / za duży": ["a2-appearance-clothes-026", "a2-appearance-clothes-033"]},
    "a2-daily-life": {"często / rzadko": ["a2-daily-life-003", "a2-daily-life-013"]},
    "a2-describing-past": {"byłem / byłam": ["a2-describing-past-001"], "miałem / miałam": ["a2-describing-past-002"], "robiłem / zrobiłem": ["a2-describing-past-003"], "poszedłem / poszłam": ["a2-describing-past-004"], "widziałem / widziałam": ["a2-describing-past-005"], "mówiłem / powiedziałem": ["a2-describing-past-006"], "chciałem / chciałam": ["a2-describing-past-007"], "musiałem / musiałam": ["a2-describing-past-008"], "mogłem / mogłam": ["a2-describing-past-009"], "zapomniałem / zapomniałam": ["a2-describing-past-024"]},
    "a2-directions-orientation": {"skręcić w lewo / w prawo": ["a2-directions-orientation-005", "a2-directions-orientation-023"], "blisko / daleko": ["a2-directions-orientation-017", "a2-directions-orientation-024"], "po lewej / prawej stronie": ["a2-directions-orientation-018", "a2-directions-orientation-025"], "pieszo / na piechotę": ["a2-directions-orientation-021"], "mapa / nawigacja": ["a2-directions-orientation-022", "a2-directions-orientation-026"]},
    "a2-ecology": {"oddawać / oddać": ["a2-ecology-001"], "zwracać / zwrócić": ["a2-ecology-002"], "zbierać / zebrać": ["a2-ecology-003"], "wyrzucać / wyrzucić": ["a2-ecology-004"], "oszczędzać / oszczędzić": ["a2-ecology-013"], "wyłączać / wyłączyć": ["a2-ecology-014"], "zakręcać / zakręcić": ["a2-ecology-015"], "marnować / zmarnować": ["a2-ecology-016"], "brać / wziąć prysznic": ["a2-ecology-020"], "kupować / kupić": ["a2-ecology-021"], "wymieniać się / wymienić się": ["a2-ecology-022"], "pakować / zapakować": ["a2-ecology-023"], "używać / użyć": ["a2-ecology-024"], "inwestować / zainwestować": ["a2-ecology-026"], "redukować / zredukować": ["a2-ecology-027"], "wycinać / wyciąć": ["a2-ecology-028"]},
    "a2-food-shopping": {"targ / rynek": ["a2-food-shopping-008", "a2-food-shopping-014"], "puszka / słoik": ["a2-food-shopping-012", "a2-food-shopping-013"]},
    "a2-health-body": {"oko / oczy": ["a2-health-body-011", "a2-health-body-029"], "ząb / zęby": ["a2-health-body-014", "a2-health-body-030"], "ucho / uszy": ["a2-health-body-015", "a2-health-body-031"], "kość / kości": ["a2-health-body-019", "a2-health-body-032"]},
    "a2-home-family": {"wujek / ciocia": ["a2-home-family-003", "a2-home-family-015"]},
    "a2-pharmacy": {"lek / lekarstwo": ["a2-pharmacy-002"]},
    "a2-public-transport": {"Wsiadam / Wysiadam": ["a2-public-transport-017", "a2-public-transport-024"],
                            /* `pl` corrected to "Czy jadę w dobrym kierunku?"; id unchanged, not a split. */
                            "Czy to jest dobry kierunek?": ["a2-public-transport-019"]},
    "a2-quantities-money": {"dużo / mało": ["a2-quantities-money-015", "a2-quantities-money-025"], "płacić kartą / gotówką": ["a2-quantities-money-022", "a2-quantities-money-026"], "przecena / wyprzedaż": ["a2-quantities-money-023", "a2-quantities-money-027"], "złoty (zł)": ["a2-quantities-money-003"], "kilogram (kilo)": ["a2-quantities-money-007"], "deko(gram)": ["a2-quantities-money-008"]},
    "a2-restaurant": {"karta / menu": ["a2-restaurant-003"], "widelec / nóż / łyżka": ["a2-restaurant-013", "a2-restaurant-021", "a2-restaurant-022"]},
    "a2-work-education": {"nauczyciel / nauczycielka": ["a2-work-education-001", "a2-work-education-015"], "uczeń / student": ["a2-work-education-002", "a2-work-education-016"]},
    "b1-career": {"CV / życiorys": ["b1-career-011"]},
    "b1-culture-entertainment": {"autor / autorka": ["b1-culture-entertainment-012", "b1-culture-entertainment-022"], "nudny / wciągający": ["b1-culture-entertainment-020", "b1-culture-entertainment-023"]},
    "b1-relationships": {"kochać / lubić": ["b1-relationships-005", "b1-relationships-022"], "chłopak / dziewczyna": ["b1-relationships-007", "b1-relationships-023"], "narzeczony / narzeczona": ["b1-relationships-008", "b1-relationships-024"]},
    /* Wording correction: the card keeps its id, only its `pl` changed, so the original
       wording needs an explicit key to keep resolving. Not a split - no rev-2 entry. */
    "podcasts-toxic-productivity": {"odreagować dzień": ["podcasts-toxic-productivity-016"]},
    },
    retired: {}   /* topicId -> [oldPl, ...]                     (intentionally retired) */
  };

  /* Structural revisions (rev >= 2). Each: { rev:Number, apply:function(store, ctx)
     -> {unmapped?, retired?} }. Applied in ascending order, each at most once. */
  PP_MIGRATE.REVISIONS = [
    /* Revision 2: expand each split card's progress onto its new sibling id(s).
       For a v2 store keyed by the original (primary) id: primary known -> add siblings to
       known; primary still-learning -> add siblings to still (still wins). Primary stays.
       Idempotent: sets dedupe and migrationRevision gates a single run. */
    { rev: 2, apply: function (store) {
        var SPLITS = {
    "a1-about-me-026": ["a1-about-me-029"],
    "a1-about-me-027": ["a1-about-me-030"],
    "a1-cafe-017": ["a1-cafe-021"],
    "a1-cafe-018": ["a1-cafe-022"],
    "a1-days-time-008": ["a1-days-time-023"],
    "a1-days-time-021": ["a1-days-time-024"],
    "a1-days-time-022": ["a1-days-time-025"],
    "a1-family-people-006": ["a1-family-people-019"],
    "a1-family-people-007": ["a1-family-people-020"],
    "a1-family-people-008": ["a1-family-people-021"],
    "a1-family-people-011": ["a1-family-people-022"],
    "a1-family-people-012": ["a1-family-people-023"],
    "a1-family-people-013": ["a1-family-people-024"],
    "a1-family-people-014": ["a1-family-people-025"],
    "a1-family-people-018": ["a1-family-people-026"],
    "a1-first-phrases-009": ["a1-first-phrases-028"],
    "a1-food-basics-015": ["a1-food-basics-022"],
    "a1-food-basics-019": ["a1-food-basics-023"],
    "a1-food-basics-021": ["a1-food-basics-024"],
    "a1-fruit-vegetables-021": ["a1-fruit-vegetables-024"],
    "a1-fruit-vegetables-022": ["a1-fruit-vegetables-025"],
    "a1-numbers-prices-020": ["a1-numbers-prices-021"],
    "a2-appearance-clothes-019": ["a2-appearance-clothes-032"],
    "a2-appearance-clothes-026": ["a2-appearance-clothes-033"],
    "a2-daily-life-003": ["a2-daily-life-013"],
    "a2-directions-orientation-005": ["a2-directions-orientation-023"],
    "a2-directions-orientation-017": ["a2-directions-orientation-024"],
    "a2-directions-orientation-018": ["a2-directions-orientation-025"],
    "a2-directions-orientation-022": ["a2-directions-orientation-026"],
    "a2-food-shopping-008": ["a2-food-shopping-014"],
    "a2-food-shopping-012": ["a2-food-shopping-013"],
    "a2-health-body-011": ["a2-health-body-029"],
    "a2-health-body-014": ["a2-health-body-030"],
    "a2-health-body-015": ["a2-health-body-031"],
    "a2-health-body-019": ["a2-health-body-032"],
    "a2-home-family-003": ["a2-home-family-015"],
    "a2-public-transport-017": ["a2-public-transport-024"],
    "a2-quantities-money-015": ["a2-quantities-money-025"],
    "a2-quantities-money-022": ["a2-quantities-money-026"],
    "a2-quantities-money-023": ["a2-quantities-money-027"],
    "a2-restaurant-013": ["a2-restaurant-021", "a2-restaurant-022"],
    "a2-work-education-001": ["a2-work-education-015"],
    "a2-work-education-002": ["a2-work-education-016"],
    "b1-culture-entertainment-012": ["b1-culture-entertainment-022"],
    "b1-culture-entertainment-020": ["b1-culture-entertainment-023"],
    "b1-relationships-005": ["b1-relationships-022"],
    "b1-relationships-007": ["b1-relationships-023"],
    "b1-relationships-008": ["b1-relationships-024"],
        };
        Object.keys(store.progress).forEach(function (tid) {
          var rec = store.progress[tid];
          var known = {}, still = {};
          (rec.known || []).forEach(function (x) { known[x] = true; });
          (rec.still || []).forEach(function (x) { still[x] = true; });
          Object.keys(SPLITS).forEach(function (p) {
            if (still[p]) SPLITS[p].forEach(function (k) { still[k] = true; delete known[k]; });
            else if (known[p]) SPLITS[p].forEach(function (k) { known[k] = true; });
          });
          rec.known = Object.keys(known); rec.still = Object.keys(still);
        });
        return {};
    } }
  ];

  /* ---------------- small helpers ---------------- */
  function safeParse(s) { try { return JSON.parse(s); } catch (e) { return undefined; } }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }
  function toSet(arr) { var s = {}; (arr || []).forEach(function (x) { s[x] = true; }); return s; }
  function keys(set) { return Object.keys(set); }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }

  /* Enumerate the keys of a storage-like object (localStorage OR a mem mock). */
  function storageKeys(storage) {
    if (storage && typeof storage.keys === "function") return storage.keys();
    if (storage && typeof storage.length === "number" && typeof storage.key === "function") {
      var ks = []; for (var i = 0; i < storage.length; i++) ks.push(storage.key(i)); return ks;
    }
    return [];
  }
  function snapshotPrefix(storage, prefix) {
    var snap = {};
    storageKeys(storage).forEach(function (k) { if (k.indexOf(prefix) === 0) snap[k] = storage.getItem(k); });
    return snap;
  }
  function restoreSnapshot(storage, snap, prefix) {
    storageKeys(storage).forEach(function (k) { if (k.indexOf(prefix) === 0) storage.removeItem(k); });
    Object.keys(snap).forEach(function (k) { storage.setItem(k, snap[k]); });
  }

  /* In-memory storage - used by the backup preflight (browser) and by tests. Optional
     opts.throwOnSetCall / opts.throwOnRemoveCall make the Nth call throw once (test hooks). */
  PP_MIGRATE.createMemStorage = function (init, opts) {
    opts = opts || {};
    var m = {}; if (init) for (var k in init) if (has(init, k)) m[k] = String(init[k]);
    var setN = 0, remN = 0;
    return {
      getItem: function (k) { return has(m, k) ? m[k] : null; },
      setItem: function (k, v) {
        setN++;
        if (opts.throwOnSetCall && setN === opts.throwOnSetCall) throw new Error("setItem failed (test hook)");
        if (opts.throwOnSetKey && k === opts.throwOnSetKey) throw new Error("setItem failed for " + k + " (test hook)");
        m[k] = String(opts.mutateSet ? opts.mutateSet(k, v) : v);   /* mutateSet: corrupt-on-write test hook */
      },
      removeItem: function (k) { remN++; if (opts.throwOnRemoveCall && remN === opts.throwOnRemoveCall) throw new Error("removeItem failed (test hook)"); delete m[k]; },
      keys: function () { return Object.keys(m); }
    };
  };

  /* ---------------- context (pure; built from LEVELS or a test fixture) ----------------
     Only card-bearing topics that have an `id` participate in progress. Runtime
     containers (Type it / Listening / mixes) have no cards/id and are skipped. */
  PP_MIGRATE.buildContext = function (levels, legacy) {
    legacy = legacy || PP_MIGRATE.LEGACY;
    var topicIdByLegacyKey = {};
    var topics = {};
    (levels || []).forEach(function (L) {
      (L.topics || []).forEach(function (t) {
        if (!t.id || !t.cards) return;
        topicIdByLegacyKey[L.level + "|" + t.name] = t.id;
        var rec = { plToIds: {}, introPls: {}, ids: {} };
        t.cards.forEach(function (c) {
          if (!c.id) return;
          rec.ids[c.id] = true;
          if (c.intro) { if (c.pl) rec.introPls[c.pl] = true; }
          else if (c.pl) { (rec.plToIds[c.pl] = rec.plToIds[c.pl] || []).push(c.id); }
        });
        topics[t.id] = rec;
      });
    });
    var lt = (legacy && legacy.topics) || {};
    for (var k in lt) { if (has(lt, k)) topicIdByLegacyKey[k] = lt[k]; }
    return { topicIdByLegacyKey: topicIdByLegacyKey, topics: topics, legacy: legacy };
  };

  /* Resolve an old (baseline) pl string to new card id(s), or classify it as an
     intentionally-retired intro card, or genuinely unmapped. Priority:
     explicit legacy map > current wording match > retired (intro/legacy) > unmapped. */
  function resolveCardIds(ctx, topicId, oldPl) {
    var legacy = ctx.legacy || {};
    var lc = (legacy.cards && legacy.cards[topicId]) || null;
    if (lc && has(lc, oldPl)) return { kind: "mapped", ids: lc[oldPl] };
    var rec = ctx.topics[topicId];
    if (rec) {
      if (has(rec.plToIds, oldPl)) return { kind: "mapped", ids: rec.plToIds[oldPl] };
      if (rec.introPls[oldPl]) return { kind: "retired" };
    }
    var lr = (legacy.retired && legacy.retired[topicId]) || null;
    if (lr && lr.indexOf(oldPl) >= 0) return { kind: "retired" };
    return { kind: "unmapped" };
  }

  /* ---------------- v1 -> v2 (schema migration, produces migrationRevision:1) ---------------- */
  PP_MIGRATE.buildV2FromV1 = function (v1obj, ctx, nowIso) {
    var store = { schemaVersion: 2, migrationRevision: 1, updated: nowIso || null, progress: {} };
    var unmapped = [], retired = [];
    if (v1obj && typeof v1obj === "object") {
      Object.keys(v1obj).forEach(function (oldTopicKey) {
        var recIn = v1obj[oldTopicKey];
        if (!recIn || typeof recIn !== "object") {
          unmapped.push({ topic: oldTopicKey, reason: "malformed record" }); return;
        }
        var topicId = ctx.topicIdByLegacyKey[oldTopicKey];
        if (!topicId) { unmapped.push({ topic: oldTopicKey, reason: "unknown topic" }); return; }
        var b = store.progress[topicId] || (store.progress[topicId] = { known: [], still: [] });
        var kset = toSet(b.known), sset = toSet(b.still);
        ["known", "still"].forEach(function (status) {
          var arr = Array.isArray(recIn[status]) ? recIn[status] : [];
          arr.forEach(function (oldPl) {
            var res = resolveCardIds(ctx, topicId, oldPl);
            if (res.kind === "retired") { retired.push({ topic: topicId, pl: oldPl }); return; }
            if (res.kind === "unmapped") { unmapped.push({ topic: topicId, pl: oldPl, reason: "no card match" }); return; }
            res.ids.forEach(function (id) { (status === "known" ? kset : sset)[id] = true; });
          });
        });
        b.known = keys(kset); b.still = keys(sset);
      });
    }
    return { store: store, unmapped: unmapped, retired: retired };
  };

  /* ---------------- conflict precedence: still-learning wins ---------------- */
  PP_MIGRATE.resolveConflicts = function (store) {
    if (!store || !store.progress) return store;
    Object.keys(store.progress).forEach(function (tid) {
      var rec = store.progress[tid];
      if (!rec || !Array.isArray(rec.known) || !Array.isArray(rec.still)) return;  // leave malformed for validateStore
      var stillSet = toSet(rec.still);
      rec.known = rec.known.filter(function (id) { return !stillSet[id]; });
    });
    return store;
  };

  /* ---------------- structural revisions (rev >= 2), each once, in order ----------------
     FAIL CLOSED: every integer revision in (current, target] must have exactly one handler.
     A missing / duplicate / throwing / invalid-output revision aborts with ok:false and
     migrationRevision only advances after a revision completes AND the store still validates.
     migrationRevision is NEVER force-assigned to the target just because no handler ran. */
  PP_MIGRATE.applyRevisions = function (store, ctx) {
    var unmapped = [], retired = [];
    var target = PP_MIGRATE.CONTENT_MIGRATION_REVISION;
    var start = (store.migrationRevision || 0);

    /* index handlers, rejecting invalid rev numbers and duplicates */
    var byRev = {};
    for (var i = 0; i < PP_MIGRATE.REVISIONS.length; i++) {
      var r = PP_MIGRATE.REVISIONS[i];
      if (!r || typeof r.rev !== "number" || r.rev < 2 || Math.floor(r.rev) !== r.rev || typeof r.apply !== "function")
        return { ok: false, error: "invalid revision handler at index " + i };
      if (has(byRev, r.rev)) return { ok: false, error: "duplicate revision handler: " + r.rev };
      byRev[r.rev] = r;
    }

    for (var rev = start + 1; rev <= target; rev++) {
      if (!has(byRev, rev)) return { ok: false, error: "missing required revision handler: " + rev };
      var out;
      try { out = byRev[rev].apply(store, ctx) || {}; }
      catch (e) { return { ok: false, error: "revision " + rev + " threw: " + e }; }
      /* resolve known/still conflicts the revision may have introduced BEFORE validating
         (still-learning wins); the mid-revision check then guards structure, not conflicts. */
      PP_MIGRATE.resolveConflicts(store);
      var v = PP_MIGRATE.validateStore(store);
      if (!v.ok) return { ok: false, error: "revision " + rev + " produced an invalid store: " + v.errors.join("; ") };
      if (out.unmapped) unmapped = unmapped.concat(out.unmapped);
      if (out.retired) retired = retired.concat(out.retired);
      store.migrationRevision = rev;   /* advance only after this revision succeeded */
    }
    return { ok: true, unmapped: unmapped, retired: retired };
  };

  /* ---------------- validate a v2 store shape ---------------- */
  PP_MIGRATE.validateStore = function (store) {
    var e = [];
    if (!store || typeof store !== "object") { return { ok: false, errors: ["not an object"] }; }
    if (store.schemaVersion !== 2) e.push("schemaVersion !== 2");
    /* migrationRevision must be an integer in [1, CONTENT_MIGRATION_REVISION]. A higher
       value means the store was written by a newer app version we don't understand: reject
       it (never treat as current), so it routes to the recovery path instead of a clobber. */
    var mr = store.migrationRevision;
    if (typeof mr !== "number" || !isFinite(mr) || Math.floor(mr) !== mr ||
        mr < 1 || mr > PP_MIGRATE.CONTENT_MIGRATION_REVISION)
      e.push("migrationRevision unsupported: " + mr);
    if (!store.progress || typeof store.progress !== "object") e.push("progress missing");
    else Object.keys(store.progress).forEach(function (tid) {
      var r = store.progress[tid];
      if (!r || !Array.isArray(r.known) || !Array.isArray(r.still)) { e.push("bad record " + tid); return; }
      var sset = toSet(r.still);
      r.known.forEach(function (id) { if (sset[id]) e.push("conflict id in known+still: " + tid + "/" + id); });
    });
    return { ok: e.length === 0, errors: e };
  };

  /* ---------------- orchestration against a storage-like object ----------------
     `storage` needs getItem/setItem (localStorage or a test mock). Idempotent:
     a fully up-to-date v2 short-circuits with NO write. */
  PP_MIGRATE.migrateAtStartup = function (storage, ctx, nowIso) {
    var K = PP_MIGRATE.KEYS;
    var rawV1 = storage.getItem(K.v1);
    if (rawV1 != null && storage.getItem(K.v1backup) == null) {
      try { storage.setItem(K.v1backup, rawV1); } catch (e) { /* keep going */ }
    }
    var rawV2 = storage.getItem(K.v2);
    var existingV2 = safeParse(rawV2);
    var existingValid = !!(existingV2 && PP_MIGRATE.validateStore(existingV2).ok);
    var v1obj = safeParse(rawV1);
    var v1Usable = !!(v1obj && typeof v1obj === "object");

    var candidate, unmapped = [], retired = [], mode, recovered = false;

    if (existingValid) {
      /* Case C: valid v2 - never touch the recovery key. */
      if ((existingV2.migrationRevision || 0) >= PP_MIGRATE.CONTENT_MIGRATION_REVISION) {
        return { status: "current", unmapped: [], retired: [] };
      }
      candidate = clone(existingV2);
      var r1 = PP_MIGRATE.applyRevisions(candidate, ctx);
      if (!r1.ok) return { status: "failed", error: r1.error };   /* don't overwrite the valid v2 */
      unmapped = r1.unmapped; retired = r1.retired; mode = "upgraded";
    } else {
      var hadRawV2 = (rawV2 != null);
      if (hadRawV2 && !v1Usable) {
        /* Case A: invalid v2, no usable v1 to rebuild from. Preserve v2 as-is; do NOT
           overwrite it or create an empty store. */
        return { status: "recovery-required", reason: "invalid v2 and no usable v1 to rebuild from" };
      }
      if (hadRawV2 && v1Usable) {
        /* Case B: invalid v2 but usable v1. Parking the invalid v2 is MANDATORY before we
           replace it. If no recovery copy exists yet and we cannot write one, refuse to
           rebuild - leave the original v2 byte-for-byte and do not write a candidate. An
           existing recovery copy is preserved (never overwritten) and rebuild continues. */
        if (storage.getItem(K.v2recovery) == null) {
          try { storage.setItem(K.v2recovery, rawV2); recovered = true; }
          catch (e) { return { status: "recovery-required", reason: "could not save recovery copy of invalid v2" }; }
        }
      }
      var built = PP_MIGRATE.buildV2FromV1(v1Usable ? v1obj : {}, ctx, nowIso);
      candidate = built.store;
      var r2 = PP_MIGRATE.applyRevisions(candidate, ctx);
      if (!r2.ok) return { status: "failed", error: r2.error };   /* leave existing keys untouched */
      unmapped = built.unmapped.concat(r2.unmapped);
      retired = built.retired.concat(r2.retired);
      mode = "migrated";
    }

    candidate.updated = nowIso || candidate.updated || null;
    PP_MIGRATE.resolveConflicts(candidate);
    var v = PP_MIGRATE.validateStore(candidate);
    if (!v.ok) return { status: "failed", errors: v.errors, unmapped: unmapped, retired: retired };
    try {
      storage.setItem(K.v2, JSON.stringify(candidate));
      if (unmapped.length) storage.setItem(K.unmapped, JSON.stringify(unmapped));
    } catch (e) { return { status: "write-error", error: String(e) }; }
    return { status: mode, unmapped: unmapped, retired: retired, store: candidate, recovered: recovered };
  };

  /* ---------------- backup helpers (pure) ---------------- */
  PP_MIGRATE.buildBackupEnvelope = function (dataObj, appVersion, nowIso) {
    return {
      app: "popolsku.app",
      version: appVersion,
      schemaVersion: PP_MIGRATE.SCHEMA_VERSION,
      exported: nowIso,
      data: dataObj
    };
  };
  /* Count progress for a backup's `data` map. Prefer v2; fall back to v1. DEFENSIVE:
     never throws, even on malformed records / non-array known|still / non-object input. */
  PP_MIGRATE.progressCounts = function (dataObj) {
    var known = 0, still = 0;
    if (!dataObj || typeof dataObj !== "object") return { known: 0, still: 0 };
    function tally(map) {
      if (!map || typeof map !== "object") return;
      Object.keys(map).forEach(function (t) {
        var r = map[t] || {};
        known += Array.isArray(r.known) ? r.known.length : 0;
        still += Array.isArray(r.still) ? r.still.length : 0;
      });
    }
    try {
      var v2 = safeParse(dataObj[PP_MIGRATE.KEYS.v2]);
      if (v2 && v2.progress && typeof v2.progress === "object") { tally(v2.progress); return { known: known, still: still }; }
      tally(safeParse(dataObj[PP_MIGRATE.KEYS.v1]));
    } catch (e) { /* never throw */ }
    return { known: known, still: still };
  };

  /* ---------------- backup preflight (item 4) ----------------
     Validate a backup against an ISOLATED in-memory copy before any device data is
     touched. Returns { ok, reason, counts }. A rejected backup implies zero real writes. */
  function v1RecordsOk(o) {
    if (!o || typeof o !== "object") return false;
    return Object.keys(o).every(function (k) {
      var r = o[k];
      if (!r || typeof r !== "object") return false;
      if (r.known !== undefined && !Array.isArray(r.known)) return false;
      if (r.still !== undefined && !Array.isArray(r.still)) return false;
      return true;
    });
  }
  PP_MIGRATE.preflightBackup = function (backupObj, ctx, nowIso) {
    if (!backupObj || backupObj.app !== "popolsku.app" || typeof backupObj.data !== "object" || backupObj.data === null)
      return { ok: false, reason: "That file doesn't look like a Po polsku backup." };
    var K = PP_MIGRATE.KEYS, data = backupObj.data;

    var rawV1 = (typeof data[K.v1] === "string") ? data[K.v1] : null;
    var rawV2 = (typeof data[K.v2] === "string") ? data[K.v2] : null;
    var v1obj = (rawV1 != null) ? safeParse(rawV1) : undefined;
    var v2obj = (rawV2 != null) ? safeParse(rawV2) : undefined;

    var v1Present = (rawV1 != null), v2Present = (rawV2 != null);
    var v1Recoverable = v1Present && !!(v1obj && typeof v1obj === "object" && v1RecordsOk(v1obj));
    var v2Valid = v2Present && !!(v2obj && PP_MIGRATE.validateStore(v2obj).ok);
    var v1Malformed = v1Present && !v1Recoverable;
    var v2Malformed = v2Present && !v2Valid;

    /* explicit reject cases (before running anything) */
    if (v1Malformed && !v2Valid) return { ok: false, reason: "This backup's saved progress is damaged and can't be restored safely." };
    if (v2Malformed && !v1Recoverable) return { ok: false, reason: "This backup's saved progress is damaged and can't be restored safely." };
    if (v2Present && v2obj && typeof v2obj === "object" && v2obj.schemaVersion !== undefined
        && v2obj.schemaVersion !== 2 && !v1Recoverable)
      return { ok: false, reason: "This backup was made by an unsupported app version." };

    /* run the real pipeline against an isolated copy (catches revision/handler issues) */
    var mem = PP_MIGRATE.createMemStorage();
    Object.keys(data).forEach(function (k) {
      if (k.indexOf("popolsku-") === 0 && typeof data[k] === "string") mem.setItem(k, data[k]);
    });
    var res;
    try { res = PP_MIGRATE.migrateAtStartup(mem, ctx, nowIso); }
    catch (e) { return { ok: false, reason: "This backup couldn't be processed safely." }; }
    if (res.status === "failed" || res.status === "recovery-required" || res.status === "write-error")
      return { ok: false, reason: "This backup's progress couldn't be restored safely." };
    var finalV2 = safeParse(mem.getItem(K.v2));
    if (!finalV2 || !PP_MIGRATE.validateStore(finalV2).ok)
      return { ok: false, reason: "This backup's progress couldn't be validated." };

    /* Counts come from the FINAL migrated v2 (not the original backup records), so the
       confirmation reflects any structural revisions - e.g. a split turning one legacy
       item into two card ids. */
    var counts;
    try { counts = PP_MIGRATE.progressCounts({ "popolsku-progress-v2": mem.getItem(K.v2) }); }
    catch (e) { return { ok: false, reason: "This backup's progress couldn't be read." }; }
    return { ok: true, counts: counts };
  };

  /* ---------------- rollback-safe restore (item 5) ----------------
     Preflight, snapshot every current popolsku-* value, apply, re-validate; on ANY failure
     roll the device back to the exact snapshot. Never leaves partially-restored data. */
  PP_MIGRATE.restoreBackup = function (storage, backupObj, ctx, nowIso) {
    var K = PP_MIGRATE.KEYS;
    var pf = PP_MIGRATE.preflightBackup(backupObj, ctx, nowIso);
    if (!pf.ok) return { ok: false, stage: "preflight", reason: pf.reason };

    var snapshot = snapshotPrefix(storage, "popolsku-");
    try {
      Object.keys(snapshot).forEach(function (k) { storage.removeItem(k); });
      var data = backupObj.data;
      Object.keys(data).forEach(function (k) {
        if (k.indexOf("popolsku-") === 0 && typeof data[k] === "string") storage.setItem(k, data[k]);
      });
      var res = PP_MIGRATE.migrateAtStartup(storage, ctx, nowIso);
      if (res.status === "failed" || res.status === "recovery-required" || res.status === "write-error")
        throw new Error("post-restore migration " + res.status);
      var v2 = safeParse(storage.getItem(K.v2));
      if (!v2 || !PP_MIGRATE.validateStore(v2).ok) throw new Error("post-restore validation failed");
    } catch (e) {
      try { restoreSnapshot(storage, snapshot, "popolsku-"); } catch (e2) { /* best effort */ }
      return { ok: false, stage: "apply", reason: String(e), rolledBack: true };
    }
    return { ok: true, counts: pf.counts };
  };

  global.PP_MIGRATE = PP_MIGRATE;
})(typeof window !== "undefined" ? window : this);
