// Deterministic tests for pp-migrate.js. Runs in JavaScriptCore:
//     osascript -l JavaScript tests/test_migration.js
// Exit status is 0 only if every assertion passes (printed at the end).
ObjC.import('Foundation');

function readFile(path) {
  var s = $.NSString.stringWithContentsOfFileEncodingError(path, $.NSUTF8StringEncoding, null);
  return ObjC.unwrap(s);
}
// Portable root resolution: the documented command runs from the repo root; also tolerate
// being run from inside tests/. No hard-coded absolute path.
function resolveRoot() {
  var fm = $.NSFileManager.defaultManager;
  var cwd = ObjC.unwrap(fm.currentDirectoryPath);
  var candidates = [cwd + '/', cwd + '/../'];
  for (var i = 0; i < candidates.length; i++) {
    if (fm.fileExistsAtPath(candidates[i] + 'pp-migrate.js')) return candidates[i];
  }
  return cwd + '/';
}
var ROOT = resolveRoot();
(0, eval)(readFile(ROOT + 'pp-migrate.js'));          // defines global PP_MIGRATE

// ---------- tiny test framework ----------
var PASS = 0, FAIL = 0, LOG = [];
function norm(o) {                                     // stable stringify (sorted arrays + keys)
  function s(x) {
    if (Array.isArray(x)) return x.map(s).sort();
    if (x && typeof x === 'object') {
      var r = {}; Object.keys(x).sort().forEach(function (k) { r[k] = s(x[k]); }); return r;
    }
    return x;
  }
  return JSON.stringify(s(o));
}
function ok(name, cond) { if (cond) { PASS++; } else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, a, b) { ok(name + '  (got ' + JSON.stringify(a) + ')', norm(a) === norm(b)); }

// ---------- storage mock ----------
function Mock(init) { this.m = {}; if (init) for (var k in init) this.m[k] = init[k]; }
Mock.prototype.getItem = function (k) { return (k in this.m) ? this.m[k] : null; };
Mock.prototype.setItem = function (k, v) { this.m[k] = String(v); };
Mock.prototype.removeItem = function (k) { delete this.m[k]; };
Mock.prototype.keys = function () { return Object.keys(this.m); };

// ---------- fixtures ----------
var LEVELS = [
  { id: 'a1', level: 'A1', topics: [
    { id: 'a1-first-phrases', name: 'Pierwsze zwroty', cards: [
      { id: 'a1-first-phrases-001', pl: 'Dzień dobry', en: 'Hello' },
      { id: 'a1-first-phrases-002', pl: 'Cześć', en: 'Hi' },
      { id: 'a1-first-phrases-009', pl: 'Tak', en: 'Yes' },      // split primary
      { id: 'a1-first-phrases-028', pl: 'Nie', en: 'No' },       // split sibling
      { id: 'a1-first-phrases-014', pl: 'Mam na imię...', en: 'My name is...', cardType: 'template' }
    ] }
  ] },
  // a runtime container (no id / no cards) must be ignored by buildContext
  { level: 'Type it', topics: [ { name: 'A1', kind: 'typeit', src: ['A1'] } ] },
  // aligned to the real pp-migrate SPLITS (a2-food-shopping-008 -> [a2-food-shopping-014])
  { id: 'a2', level: 'A2', topics: [
    { id: 'a2-food-shopping', name: 'Jedzenie i zakupy', cards: [
      { id: 'a2-food-shopping-008', pl: 'targ', en: 'market / open-air market' },
      { id: 'a2-food-shopping-014', pl: 'rynek', en: 'market square' }
    ] }
  ] },
  { id: 'a2b', level: 'A2', topics: [
    { id: 'a2-public-transport', name: 'Komunikacja miejska', cards: [
      { id: 'a2-public-transport-017', pl: 'Wsiadam', en: "I'm getting on" },      // split primary
      { id: 'a2-public-transport-024', pl: 'Wysiadam', en: "I'm getting off" },    // split sibling
      // Phase 4: `pl` corrected from 'Czy to jest dobry kierunek?'; id unchanged, not a split
      { id: 'a2-public-transport-019', pl: 'Czy jadę w dobrym kierunku?', en: 'Am I going in the right direction?' }
    ] }
  ] },
  { id: 'podcasts', level: 'Podcasts', topics: [
    { id: 'podcasts-toxic-productivity', name: 'Toksyczna produktywność', cards: [
      { id: 'podcasts-toxic-productivity-intro', intro: true, pl: 'Stan umysłu · Toksyczna produktywność', en: 'State of Mind' },
      { id: 'podcasts-toxic-productivity-001', pl: 'ulegać presji', en: 'to give in to pressure' },
      // Phase 4: `pl` corrected in place; the id is unchanged, so LEGACY carries the old wording
      { id: 'podcasts-toxic-productivity-016', pl: 'odreagować po całym dniu', en: 'to unwind after a long day' }
    ] }
  ] }
];
var LEGACY = {
  schema: 2,
  topics: { 'A1|Stare zwroty': 'a1-first-phrases' },              // topic rename
  cards: {
    'a1-first-phrases': {
      'Tak / Nie': ['a1-first-phrases-009', 'a1-first-phrases-028'],  // split
      'Dzien dobry': ['a1-first-phrases-001']                          // wording correction (old spelling)
    },
    'a2-food-shopping': {
      'targ / rynek': ['a2-food-shopping-008', 'a2-food-shopping-014']  // corrected: split, not synonym
    },
    'podcasts-toxic-productivity': {
      'odreagować dzień': ['podcasts-toxic-productivity-016']            // Phase-4 wording fix, no split
    },
    'a2-public-transport': {
      'Wsiadam / Wysiadam': ['a2-public-transport-017', 'a2-public-transport-024'],  // Phase-3 split
      'Czy to jest dobry kierunek?': ['a2-public-transport-019']         // Phase-4 wording fix, no split
    }
  },
  retired: {}
};
var CTX = PP_MIGRATE.buildContext(LEVELS, LEGACY);
var NOW = '2026-07-22T00:00:00Z';
function v1json(o) { return JSON.stringify(o); }

// =========================================================================
// 1. one known card
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T1 one known card', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-001'], still: [] });
  ok('T1 status migrated', r.status === 'migrated');
})();

// 2. one still-learning card
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: [], still: ['Cześć'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T2 one still card', v2.progress['a1-first-phrases'], { known: [], still: ['a1-first-phrases-002'] });
})();

// 3. migration after a visible wording correction (old spelling -> id via LEGACY.cards)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Dzien dobry'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T3 wording correction', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-001'], still: [] });
})();

// 4. migration after a topic display-name change (old key -> id via LEGACY.topics)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Stare zwroty': { known: ['Cześć'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T4 topic rename', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-002'], still: [] });
})();

// 5. migration of a split slash card (old known -> BOTH children known)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Tak / Nie'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T5 split -> both known', v2.progress['a1-first-phrases'],
     { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] });
})();

// 6. migration run twice (idempotent; second run is a no-op "current")
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: ['Cześć'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var after1 = s.getItem('popolsku-progress-v2');
  var r2 = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var after2 = s.getItem('popolsku-progress-v2');
  ok('T6 second run current', r2.status === 'current');
  ok('T6 store unchanged', after1 === after2);
})();

// 7. malformed old localStorage data (raw preserved, empty v2 built)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': '{ this is not valid json' });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('T7 status migrated', r.status === 'migrated');
  eq('T7 empty progress', v2.progress, {});
  ok('T7 schemaVersion 2', v2.schemaVersion === 2);
  ok('T7 raw v1 preserved', s.getItem('popolsku-progress-v1-backup') === '{ this is not valid json');
})();

// 8. empty old progress
(function () {
  var s = new Mock({ 'popolsku-progress-v1': '{}' });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T8 empty', v2.progress, {});
  ok('T8 at target revision', v2.migrationRevision === PP_MIGRATE.CONTENT_MIGRATION_REVISION);
})();

// 9. unknown legacy card -> reported unmapped, not silently dropped
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Nieznane słowo'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('T9 not in progress', v2.progress['a1-first-phrases'] || { known: [], still: [] }, { known: [], still: [] });
  ok('T9 reported unmapped (result)', r.unmapped.length === 1 && r.unmapped[0].pl === 'Nieznane słowo');
  ok('T9 persisted unmapped key', !!s.getItem('popolsku-progress-v2-unmapped'));
})();

// 10. backup created BEFORE migration (envelope has schemaVersion; counts fall back to v1)
(function () {
  var v1 = v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry', 'Cześć'], still: ['Tak'] } });
  var data = { 'popolsku-progress-v1': v1 };
  var env = PP_MIGRATE.buildBackupEnvelope(data, '7.4', NOW);
  ok('T10 envelope schemaVersion', env.schemaVersion === 2 && env.app === 'popolsku.app');
  eq('T10 v1 counts', PP_MIGRATE.progressCounts(data), { known: 2, still: 1 });
})();

// 11. backup created AFTER migration (data has v2; counts use v2)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: ['Cześć', 'Tak'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var data = { 'popolsku-progress-v2': s.getItem('popolsku-progress-v2') };
  var env = PP_MIGRATE.buildBackupEnvelope(data, '7.4', NOW);
  ok('T11 envelope schemaVersion', env.schemaVersion === 2);
  // 'Tak' (a1-first-phrases-009) is a split primary -> rev 2 adds 'Nie' (028) to still: 2 -> 3
  eq('T11 v2 counts', PP_MIGRATE.progressCounts(data), { known: 1, still: 3 });
})();

// 12. restore of a PRE-migration backup (only v1) -> migration rebuilds v2
(function () {
  var restored = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Tak / Nie'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(restored, CTX, NOW);
  var v2 = JSON.parse(restored.getItem('popolsku-progress-v2'));
  ok('T12 rebuilt', r.status === 'migrated');
  eq('T12 split restored', v2.progress['a1-first-phrases'],
     { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] });
})();

// 13. restore of a POST-migration backup (v2 already present, current) -> used directly
(function () {
  var s0 = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s0, CTX, NOW);
  var v2raw = s0.getItem('popolsku-progress-v2');
  var restored = new Mock({ 'popolsku-progress-v2': v2raw });
  var r = PP_MIGRATE.migrateAtStartup(restored, CTX, NOW);
  ok('T13 used directly (current)', r.status === 'current');
  ok('T13 store unchanged', restored.getItem('popolsku-progress-v2') === v2raw);
})();

// 14. current progress counting after migration
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({
    'A1|Pierwsze zwroty': { known: ['Dzień dobry', 'Tak / Nie'], still: ['Cześć'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var data = { 'popolsku-progress-v2': s.getItem('popolsku-progress-v2') };
  // "Tak / Nie" split -> two known ids, so known = 1 + 2 = 3, still = 1
  eq('T14 counts after migration', PP_MIGRATE.progressCounts(data), { known: 3, still: 1 });
})();

// ---- additional-decision tests ----

// A. status conflict: same card in known AND still -> still wins
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({
    'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: ['Dzień dobry'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('A conflict still-wins', v2.progress['a1-first-phrases'], { known: [], still: ['a1-first-phrases-001'] });
})();

// B. podcast intro card progress -> retired (not unmapped, not in progress)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({
    'Podcasts|Toksyczna produktywność': { known: ['Stan umysłu · Toksyczna produktywność'], still: ['ulegać presji'] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('B intro excluded, phrase kept', v2.progress['podcasts-toxic-productivity'],
     { known: [], still: ['podcasts-toxic-productivity-001'] });
  ok('B intro reported retired', r.retired.length === 1);
  ok('B intro NOT unmapped', r.unmapped.length === 0);
})();

// C. structural revision runs once, in sequence, and is idempotent
(function () {
  var savedRev = PP_MIGRATE.CONTENT_MIGRATION_REVISION, savedList = PP_MIGRATE.REVISIONS;
  var applied = 0;
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = 2;
  PP_MIGRATE.REVISIONS = [{ rev: 2, apply: function (store) { applied++; store.progress.__rev2 = { known: ['x'], still: [] }; return {}; } }];
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('C revision applied once', applied === 1 && v2.migrationRevision === 2 && !!v2.progress.__rev2);
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);          // re-run: must NOT re-apply
  ok('C revision not re-applied', applied === 1);
  // restored OLD v2 (rev 1) must be upgraded by the pending revision
  var oldV2 = { schemaVersion: 2, migrationRevision: 1, progress: {} };
  var s2 = new Mock({ 'popolsku-progress-v2': JSON.stringify(oldV2) });
  var r2 = PP_MIGRATE.migrateAtStartup(s2, CTX, NOW);
  ok('C old-v2 upgraded', r2.status === 'upgraded' && applied === 2);
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = savedRev; PP_MIGRATE.REVISIONS = savedList;
})();

// D. failed migration must NOT overwrite a valid existing v2
(function () {
  var savedRev = PP_MIGRATE.CONTENT_MIGRATION_REVISION, savedList = PP_MIGRATE.REVISIONS;
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = 2;
  PP_MIGRATE.REVISIONS = [{ rev: 2, apply: function (store) { delete store.schemaVersion; return {}; } }]; // corrupts
  var goodV2 = { schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-001'], still: [] } } };
  var raw = JSON.stringify(goodV2);
  var s = new Mock({ 'popolsku-progress-v2': raw });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('D status failed', r.status === 'failed');
  ok('D existing v2 preserved', s.getItem('popolsku-progress-v2') === raw);
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = savedRev; PP_MIGRATE.REVISIONS = savedList;
})();

// E. v1 is never deleted and raw is preserved verbatim
(function () {
  var raw = v1json({ 'A1|Pierwsze zwroty': { known: ['Dzień dobry'], still: [] } });
  var s = new Mock({ 'popolsku-progress-v1': raw });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('E v1 still present', s.getItem('popolsku-progress-v1') === raw);
  ok('E v1 backup == raw', s.getItem('popolsku-progress-v1-backup') === raw);
})();

// F. runtime containers ignored by buildContext (no topic id leaked)
(function () {
  ok('F no runtime container in ctx', Object.keys(CTX.topics).indexOf('undefined') < 0 &&
     !CTX.topicIdByLegacyKey['Type it|A1']);
})();

// ========================= item 1: fail-closed revision pipeline =========================
function withRevisions(target, list, fn) {
  var sr = PP_MIGRATE.CONTENT_MIGRATION_REVISION, sl = PP_MIGRATE.REVISIONS;
  PP_MIGRATE.CONTENT_MIGRATION_REVISION = target; PP_MIGRATE.REVISIONS = list;
  try { fn(); } finally { PP_MIGRATE.CONTENT_MIGRATION_REVISION = sr; PP_MIGRATE.REVISIONS = sl; }
}
function freshV1Storage() { return new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) }); }

// G1 target 2 but revision 2 absent -> fails, no v2 written
withRevisions(2, [], function () {
  var s = freshV1Storage();
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('G1 missing revision -> failed', r.status === 'failed');
  ok('G1 no v2 written', s.getItem('popolsku-progress-v2') === null);
});
// G2 duplicate revision 2 handlers -> fails
withRevisions(2, [{ rev: 2, apply: function () { } }, { rev: 2, apply: function () { } }], function () {
  var r = PP_MIGRATE.migrateAtStartup(freshV1Storage(), CTX, NOW);
  ok('G2 duplicate revision -> failed', r.status === 'failed');
});
// G3 gap: revs 2 and 4 with target 4 -> missing rev 3 -> fails
withRevisions(4, [{ rev: 2, apply: function () { } }, { rev: 4, apply: function () { } }], function () {
  var r = PP_MIGRATE.migrateAtStartup(freshV1Storage(), CTX, NOW);
  ok('G3 revision gap -> failed', r.status === 'failed');
});
// G4 handler throws -> fails, and a valid existing v2 is preserved
withRevisions(2, [{ rev: 2, apply: function () { throw new Error('boom'); } }], function () {
  var good = JSON.stringify({ schemaVersion: 2, migrationRevision: 1, progress: {} });
  var s = new Mock({ 'popolsku-progress-v2': good });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('G4 throwing revision -> failed', r.status === 'failed');
  ok('G4 valid v2 preserved', s.getItem('popolsku-progress-v2') === good);
});
// G5 handler returns invalid progress -> fails
withRevisions(2, [{ rev: 2, apply: function (st) { delete st.schemaVersion; } }], function () {
  var r = PP_MIGRATE.migrateAtStartup(freshV1Storage(), CTX, NOW);
  ok('G5 invalid revision output -> failed', r.status === 'failed');
});
// G6 successful sequential revisions, each exactly once, migrationRevision advances to target
withRevisions(3, [
  { rev: 2, apply: function (st) { st._r = (st._r || 0) + 1; } },
  { rev: 3, apply: function (st) { st._r = (st._r || 0) + 1; } }
], function () {
  var s = freshV1Storage();
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('G6 sequential revisions ok', r.status === 'migrated' && v2.migrationRevision === 3 && v2._r === 2);
});

// ========================= item 2: invalid-v2 recovery =========================
// H1 invalid v2 + no usable v1 -> recovery-required, v2 byte-for-byte unchanged, nothing created
(function () {
  var badV2 = '{"broken":true}';
  var s = new Mock({ 'popolsku-progress-v2': badV2 });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('H1 status recovery-required', r.status === 'recovery-required');
  ok('H1 v2 unchanged', s.getItem('popolsku-progress-v2') === badV2);
  ok('H1 no recovery key', s.getItem('popolsku-progress-v2-recovery') === null);
  ok('H1 no empty store created', JSON.stringify(s.keys().sort()) === JSON.stringify(['popolsku-progress-v2']));
})();
// H2 invalid v2 + usable v1 -> park invalid v2 under recovery (never overwritten), rebuild from v1
(function () {
  var badV2 = '{"broken":true}';
  var s = new Mock({ 'popolsku-progress-v2': badV2, 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('H2 rebuilt from v1', r.status === 'migrated' && r.recovered === true);
  ok('H2 invalid v2 parked in recovery', s.getItem('popolsku-progress-v2-recovery') === badV2);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('H2 v2 rebuilt', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-002'], still: [] });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);   // re-run
  ok('H2 recovery never overwritten', s.getItem('popolsku-progress-v2-recovery') === badV2);
})();
// H3 valid v2 -> recovery key never set
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify({ schemaVersion: 2, migrationRevision: 1, progress: {} }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('H3 valid v2 leaves no recovery copy', s.getItem('popolsku-progress-v2-recovery') === null);
})();

// ========================= item 4: backup preflight =========================
function backup(dataObj) { return { app: 'popolsku.app', version: '7.4', schemaVersion: 2, exported: NOW, data: dataObj }; }
(function () {
  ok('P1 v1-only backup accepted', PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) }), CTX, NOW).ok);
  var goodV2 = JSON.stringify({ schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-001'], still: [] } } });
  ok('P2 current-v2 backup accepted', PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v2': goodV2 }), CTX, NOW).ok);
  ok('P4 v1+v2 backup accepted', PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v2': goodV2, 'popolsku-progress-v1': v1json({}) }), CTX, NOW).ok);
  // rejects
  ok('P5 malformed v1, no v2 -> reject', !PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v1': '{bad json' }), CTX, NOW).ok);
  ok('P6 malformed v2, no v1 -> reject', !PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v2': '{bad json' }), CTX, NOW).ok);
  ok('P7 known/still not arrays -> reject', !PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v1': JSON.stringify({ 'A1|Pierwsze zwroty': { known: 'nope', still: [] } }) }), CTX, NOW).ok);
  ok('P8 unsupported schema version -> reject', !PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v2': JSON.stringify({ schemaVersion: 99, migrationRevision: 1, progress: {} }) }), CTX, NOW).ok);
  ok('P9 not-a-backup -> reject', !PP_MIGRATE.preflightBackup({ app: 'something-else', data: {} }, CTX, NOW).ok);
  // earlier-v2 requiring a structural revision -> accepted when a handler exists
  withRevisions(2, [{ rev: 2, apply: function () { } }], function () {
    var oldV2 = JSON.stringify({ schemaVersion: 2, migrationRevision: 1, progress: {} });
    ok('P3 earlier-v2 needing revision accepted', PP_MIGRATE.preflightBackup(backup({ 'popolsku-progress-v2': oldV2 }), CTX, NOW).ok);
  });
})();
// progressCounts is defensive (never throws on malformed records)
(function () {
  var bad = { 'popolsku-progress-v2': JSON.stringify({ schemaVersion: 2, progress: { t: { known: 'x', still: 3 } } }) };
  var c; var threw = false;
  try { c = PP_MIGRATE.progressCounts(bad); } catch (e) { threw = true; }
  ok('P10 progressCounts never throws', !threw && c.known === 0 && c.still === 0);
  ok('P11 progressCounts null-safe', PP_MIGRATE.progressCounts(null).known === 0);
})();

// ========================= item 5: rollback-safe restore =========================
function dump(storage) { var o = {}; storage.keys().forEach(function (k) { o[k] = storage.getItem(k); }); return o; }
// I5 successful restore replaces original values
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|W kawiarni': { known: ['kawa'], still: [] } }), 'popolsku-speed': 'slow' });
  var b = backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) });
  var r = PP_MIGRATE.restoreBackup(s, b, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('I5 restore ok', r.ok);
  eq('I5 replaced with backup', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-002'], still: [] });
})();
// I1 setItem failure midway -> rollback to exact original
(function () {
  var orig = { 'popolsku-progress-v1': v1json({ 'A1|W kawiarni': { known: ['kawa'], still: [] } }), 'popolsku-speed': 'slow' };
  var s = PP_MIGRATE.createMemStorage(orig, { throwOnSetCall: 2 });
  var before = dump(s);
  var b = backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }), 'popolsku-speed': 'normal' });
  var r = PP_MIGRATE.restoreBackup(s, b, CTX, NOW);
  ok('I1 restore failed + rolled back', r.ok === false && r.rolledBack === true);
  eq('I1 storage byte-for-byte original', dump(s), before);
})();
// I2 removeItem failure -> rollback to exact original
(function () {
  var orig = { 'popolsku-progress-v1': v1json({ 'A1|W kawiarni': { known: ['kawa'], still: [] } }) };
  var s = PP_MIGRATE.createMemStorage(orig, { throwOnRemoveCall: 1 });
  var before = dump(s);
  var r = PP_MIGRATE.restoreBackup(s, backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) }), CTX, NOW);
  ok('I2 restore failed + rolled back', r.ok === false && r.rolledBack === true);
  eq('I2 storage unchanged', dump(s), before);
})();
// I3 final validation failure after writing (v2 corrupted on write) -> rollback
(function () {
  var orig = { 'popolsku-progress-v1': v1json({ 'A1|W kawiarni': { known: ['kawa'], still: [] } }) };
  var s = PP_MIGRATE.createMemStorage(orig, { mutateSet: function (k, v) { return k === 'popolsku-progress-v2' ? '{"corrupt":1}' : v; } });
  var before = dump(s);
  var r = PP_MIGRATE.restoreBackup(s, backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) }), CTX, NOW);
  ok('I3 post-write validation failure -> rolled back', r.ok === false && r.rolledBack === true);
  eq('I3 storage restored to original', dump(s), before);
})();

// ========================= finding 1: reject unsupported migrationRevision =========================
(function () {
  var T = PP_MIGRATE.CONTENT_MIGRATION_REVISION;
  ok('J1 mr 0 invalid', !PP_MIGRATE.validateStore({ schemaVersion: 2, migrationRevision: 0, progress: {} }).ok);
  ok('J2 mr negative invalid', !PP_MIGRATE.validateStore({ schemaVersion: 2, migrationRevision: -1, progress: {} }).ok);
  ok('J3 mr decimal invalid', !PP_MIGRATE.validateStore({ schemaVersion: 2, migrationRevision: 1.5, progress: {} }).ok);
  ok('J4 mr above target invalid', !PP_MIGRATE.validateStore({ schemaVersion: 2, migrationRevision: T + 1, progress: {} }).ok);
  ok('J5 mr == target valid', PP_MIGRATE.validateStore({ schemaVersion: 2, migrationRevision: T, progress: {} }).ok);
})();
// future revision, no v1 -> recovery-required, v2 untouched (not treated as current)
(function () {
  var raw = JSON.stringify({ schemaVersion: 2, migrationRevision: 99, progress: {} });
  var s = new Mock({ 'popolsku-progress-v2': raw });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('J6 future rev + no v1 -> recovery-required', r.status === 'recovery-required');
  ok('J6 future rev v2 unchanged', s.getItem('popolsku-progress-v2') === raw);
})();
// future revision + valid v1 -> rebuild to a supported store
(function () {
  var raw = JSON.stringify({ schemaVersion: 2, migrationRevision: 99, progress: {} });
  var s = new Mock({ 'popolsku-progress-v2': raw, 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('J7 future rev + v1 -> rebuilt/migrated', r.status === 'migrated' && v2.migrationRevision <= PP_MIGRATE.CONTENT_MIGRATION_REVISION);
  ok('J7 invalid future v2 parked', s.getItem('popolsku-progress-v2-recovery') === raw);
  eq('J7 rebuilt from v1', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-002'], still: [] });
})();
// preflight rejects a future-revision backup with no v1 recovery path
(function () {
  var b = { app: 'popolsku.app', data: { 'popolsku-progress-v2': JSON.stringify({ schemaVersion: 2, migrationRevision: 99, progress: {} }) } };
  ok('J8 preflight rejects future-rev backup', !PP_MIGRATE.preflightBackup(b, CTX, NOW).ok);
})();

// ========================= finding 2: recovery-copy save must not be silently skipped =========================
(function () {
  var badV2 = '{"broken":true}';
  var s = PP_MIGRATE.createMemStorage(
    { 'popolsku-progress-v2': badV2, 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) },
    { throwOnSetKey: 'popolsku-progress-v2-recovery' });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('K1 recovery-copy fail -> recovery-required', r.status === 'recovery-required');
  ok('K1 original v2 unchanged', s.getItem('popolsku-progress-v2') === badV2);        // no rebuilt candidate written
  ok('K1 no recovery key created', s.getItem('popolsku-progress-v2-recovery') === null);
})();
// existing recovery key preserved, rebuild still succeeds
(function () {
  var badV2 = '{"broken":true}';
  var s = PP_MIGRATE.createMemStorage({
    'popolsku-progress-v2': badV2, 'popolsku-progress-v2-recovery': 'OLD-RECOVERY',
    'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Cześć'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('K2 existing recovery preserved', s.getItem('popolsku-progress-v2-recovery') === 'OLD-RECOVERY');
  ok('K2 rebuild succeeds', r.status === 'migrated');
  eq('K2 rebuilt from v1', v2.progress['a1-first-phrases'], { known: ['a1-first-phrases-002'], still: [] });
})();

// ========================= finding 3: preflight counts from the final migrated v2 =========================
(function () {
  // one legacy combined card "Tak / Nie" splits into two ids -> preflight must report 2 known
  var b = backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Tak / Nie'], still: [] } }) });
  var pf = PP_MIGRATE.preflightBackup(b, CTX, NOW);
  ok('L1 split -> counts from final v2 (2 known)', pf.ok && pf.counts.known === 2 && pf.counts.still === 0);
})();

// ========================= Phase 3: split migration through revision 2 =========================
// The real pp-migrate SPLITS map has a1-first-phrases-009 -> [a1-first-phrases-028]; the fixture's
// cards (009=Tak, 028=Nie) and LEGACY ("Tak / Nie" -> [009,028]) align with it.
// M1 direct v1 -> final split (both children); other split classes via LEGACY (T5 covers contrast)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Tak / Nie'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('M1 v1 split -> both children known', v2.progress['a1-first-phrases'],
     { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] });
  ok('M1 reached target revision', v2.migrationRevision === PP_MIGRATE.CONTENT_MIGRATION_REVISION);
})();
// M2 revision-1 v2 upgraded through revision 2: primary known -> add siblings to known
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-009'], still: [] } } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('M2 upgraded', r.status === 'upgraded' && v2.migrationRevision === 2);
  eq('M2 known primary -> both children known', v2.progress['a1-first-phrases'],
     { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] });
})();
// M3 still-learning primary -> siblings to still
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: [], still: ['a1-first-phrases-009'] } } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('M3 still primary -> both children still', v2.progress['a1-first-phrases'],
     { known: [], still: ['a1-first-phrases-009', 'a1-first-phrases-028'] });
})();
// M4 conflict precedence: primary still + a child already known -> still wins (child moves to still)
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-028'], still: ['a1-first-phrases-009'] } } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('M4 still wins on split', v2.progress['a1-first-phrases'],
     { known: [], still: ['a1-first-phrases-009', 'a1-first-phrases-028'] });
})();
// M5 revision 2 runs only once (idempotent): re-running yields "current", no change
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-009'], still: [] } } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var after1 = s.getItem('popolsku-progress-v2');
  var r2 = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('M5 second run current', r2.status === 'current');
  ok('M5 unchanged', s.getItem('popolsku-progress-v2') === after1);
})();
// M6 old backup preflight reports FINAL split counts (one combined item -> two ids)
(function () {
  var b = backup({ 'popolsku-progress-v1': v1json({ 'A1|Pierwsze zwroty': { known: ['Tak / Nie'], still: [] } }) });
  var pf = PP_MIGRATE.preflightBackup(b, CTX, NOW);
  ok('M6 preflight split counts = 2', pf.ok && pf.counts.known === 2 && pf.counts.still === 0);
})();
// M7 a revision-2 backup restores without re-running the revision (already at target)
(function () {
  var done = { schemaVersion: 2, migrationRevision: 2, progress: { 'a1-first-phrases': { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] } } };
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(done) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('M7 current (no re-run)', r.status === 'current');
  eq('M7 progress unchanged', JSON.parse(s.getItem('popolsku-progress-v2')).progress['a1-first-phrases'],
     { known: ['a1-first-phrases-009', 'a1-first-phrases-028'], still: [] });
})();

// ========================= correction pass: targ / rynek split =========================
// N1 direct v1 migration -> both cards (via LEGACY.cards)
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A2|Jedzenie i zakupy': { known: ['targ / rynek'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('N1 v1 targ/rynek -> both known', v2.progress['a2-food-shopping'],
     { known: ['a2-food-shopping-008', 'a2-food-shopping-014'], still: [] });
})();
// N2 rev1 v2 (Phase-2 user knew the targ primary) -> revision 2 adds rynek
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a2-food-shopping': { known: ['a2-food-shopping-008'], still: [] } } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('N2 upgraded', r.status === 'upgraded');
  eq('N2 targ primary known -> rynek added', v2.progress['a2-food-shopping'],
     { known: ['a2-food-shopping-008', 'a2-food-shopping-014'], still: [] });
})();
// N3 still-learning propagation
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a2-food-shopping': { known: [], still: ['a2-food-shopping-008'] } } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('N3 targ still -> rynek to still', v2.progress['a2-food-shopping'],
     { known: [], still: ['a2-food-shopping-008', 'a2-food-shopping-014'] });
})();
// N4 still-learning conflict precedence (rynek already known, targ still -> rynek moves to still)
(function () {
  var s = new Mock({ 'popolsku-progress-v2': JSON.stringify(
    { schemaVersion: 2, migrationRevision: 1, progress: { 'a2-food-shopping': { known: ['a2-food-shopping-014'], still: ['a2-food-shopping-008'] } } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('N4 still wins on targ/rynek', v2.progress['a2-food-shopping'],
     { known: [], still: ['a2-food-shopping-008', 'a2-food-shopping-014'] });
})();

// ============== Phase 4: a corrected `pl` keeps its progress (no new revision) ==============
// P1 the exact Phase-0 wording still resolves, via the new LEGACY.cards entry
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'Podcasts|Toksyczna produktywność': { known: ['odreagować dzień'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('P1 migrated, nothing unmapped', r.status === 'migrated' && r.unmapped.length === 0);
  eq('P1 old wording -> current id', v2.progress['podcasts-toxic-productivity'],
     { known: ['podcasts-toxic-productivity-016'], still: [] });
})();
// P2 the corrected wording is NOT a progress key - identity lives on the id, not the text
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'Podcasts|Toksyczna produktywność': { known: ['odreagować po całym dniu'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  eq('P2 current wording also resolves to the same id', v2.progress['podcasts-toxic-productivity'],
     { known: ['podcasts-toxic-productivity-016'], still: [] });
})();
// P3 a Phase-4 wording fix adds no revision: an existing rev-2 store is untouched
(function () {
  var done = { schemaVersion: 2, migrationRevision: 2, progress: { 'podcasts-toxic-productivity': { known: ['podcasts-toxic-productivity-016'], still: [] } } };
  var before = JSON.stringify(done);
  var s = new Mock({ 'popolsku-progress-v2': before });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('P3 already current', r.status === 'current');
  ok('P3 store byte-for-byte unchanged', s.getItem('popolsku-progress-v2') === before);
  ok('P3 revision still 2', PP_MIGRATE.CONTENT_MIGRATION_REVISION === 2);
})();

// ====== Phase 4 correction pass: the direction card's `pl` changed (id unchanged) ======
// P4 the exact Phase-0 wording resolves to a2-public-transport-019 via LEGACY
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A2|Komunikacja miejska': { known: ['Czy to jest dobry kierunek?'], still: [] } }) });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  var v2 = JSON.parse(s.getItem('popolsku-progress-v2'));
  ok('P4 migrated, nothing unmapped', r.status === 'migrated' && r.unmapped.length === 0);
  eq('P4 Phase-0 wording -> a2-public-transport-019', v2.progress['a2-public-transport'],
     { known: ['a2-public-transport-019'], still: [] });
})();
// P5 the corrected wording resolves to the SAME stable id
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A2|Komunikacja miejska': { known: ['Czy jadę w dobrym kierunku?'], still: [] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  eq('P5 corrected wording -> same id', JSON.parse(s.getItem('popolsku-progress-v2')).progress['a2-public-transport'],
     { known: ['a2-public-transport-019'], still: [] });
})();
// P6 an existing revision-2 v2 store is left completely alone (no revision 3)
(function () {
  var done = JSON.stringify({ schemaVersion: 2, migrationRevision: 2, progress: {
    'a2-public-transport': { known: ['a2-public-transport-019', 'a2-public-transport-017'], still: ['a2-public-transport-024'] } } });
  var s = new Mock({ 'popolsku-progress-v2': done });
  var r = PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  ok('P6 already current', r.status === 'current');
  ok('P6 store byte-for-byte unchanged', s.getItem('popolsku-progress-v2') === done);
  ok('P6 revision still 2', PP_MIGRATE.CONTENT_MIGRATION_REVISION === 2);
})();
// P7 the Phase-3 split in the same topic still works alongside the new wording mapping
(function () {
  var s = new Mock({ 'popolsku-progress-v1': v1json({ 'A2|Komunikacja miejska': {
    known: ['Wsiadam / Wysiadam'], still: ['Czy to jest dobry kierunek?'] } }) });
  PP_MIGRATE.migrateAtStartup(s, CTX, NOW);
  eq('P7 split + wording fix in one topic', JSON.parse(s.getItem('popolsku-progress-v2')).progress['a2-public-transport'],
     { known: ['a2-public-transport-017', 'a2-public-transport-024'], still: ['a2-public-transport-019'] });
})();

// ---------- report ----------
console.log('Migration tests: ' + PASS + ' passed, ' + FAIL + ' failed.');
LOG.forEach(function (l) { console.log('  ' + l); });
if (FAIL > 0) { throw new Error('TESTS FAILED: ' + FAIL + ' assertion(s) failed'); }
