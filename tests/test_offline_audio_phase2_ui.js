// Deterministic Phase 2 Offline audio UI/accessibility tests.
//
//   osascript -l JavaScript tests/test_offline_audio_phase2_ui.js
//
// This suite inspects the shipping markup/CSS/controller and the committed
// manifest. It makes no network request and never reads MP3 bodies.
ObjC.import('Foundation');

function readFile(path) {
  var s=$.NSString.stringWithContentsOfFileEncodingError(path,$.NSUTF8StringEncoding,null);
  return ObjC.unwrap(s);
}
function rootDir(){
  var fm=$.NSFileManager.defaultManager,cwd=ObjC.unwrap(fm.currentDirectoryPath);
  return fm.fileExistsAtPath(cwd+'/index.html') ? cwd+'/' : cwd+'/../';
}
var ROOT=rootDir(), INDEX=readFile(ROOT+'index.html'), SW=readFile(ROOT+'sw.js');
var MANIFEST=JSON.parse(readFile(ROOT+'audio-manifest.json'));
var PASS=0,FAIL=0,LOG=[];
function ok(name,value){ if(value) PASS++; else { FAIL++; LOG.push('FAIL: '+name); } }
function eq(name,actual,expected){
  var a=JSON.stringify(actual),e=JSON.stringify(expected);
  ok(name+(a===e?'':' (got '+a+', want '+e+')'),a===e);
}
function count(hay,needle){ var n=0,at=0; while((at=hay.indexOf(needle,at))!==-1){n++;at+=needle.length;} return n; }
function between(src,start,end){ var a=src.indexOf(start),b=src.indexOf(end,a+start.length); return a<0||b<0?'':src.slice(a,b); }
function section(id){ return between(INDEX,'<section class="screen" id="'+id+'">','</section>'); }
function tag(id){ var m=INDEX.match(new RegExp('<([a-z]+)([^>]*\\sid="'+id+'")([^>]*)>')); return m?m[0]:''; }
function squash(s){ return String(s).replace(/\s+/g,''); }
function hasCode(hay,needle){ return squash(hay).indexOf(squash(needle))!==-1; }

var UI=between(INDEX,'/* OFFLINE_AUDIO_UI_START','/* OFFLINE_AUDIO_UI_END */');
var ENGINE=between(INDEX,'/* OFFLINE_AUDIO_ENGINE_START','/* OFFLINE_AUDIO_ENGINE_END */');
var SCREEN=section('offlineAudio');
var MENU=between(INDEX,'<ul class="site-nav-list">','</ul>');
var DIALOG=between(INDEX,'<dialog class="modal-overlay" id="offlineAudioRemoveDialog"','</dialog>');
var STYLE='',styleRe=/<style>([\s\S]*?)<\/style>/g,styleMatch;
while((styleMatch=styleRe.exec(INDEX))) STYLE+='\n'+styleMatch[1];
var files=Object.keys(MANIFEST.entries).map(function(k){return MANIFEST.entries[k].file;});

// Placement, route, and entry behavior.
eq('menu has Offline audio exactly once',count(MENU,'>Offline audio</a>'),1);
ok('menu item is immediately after Install',MENU.indexOf('id="siteInstallItem"')<MENU.indexOf('>Offline audio</a>') &&
   MENU.indexOf('>Offline audio</a>')<MENU.indexOf('>Privacy</a>'));
ok('menu link uses the shared screen contract',MENU.indexOf('href="#offlineAudio" data-app-screen="offlineAudio"')!==-1);
ok('menu action contains no download operation',between(MENU,'href="#offlineAudio"','</a>').indexOf('download')===-1);
ok('offlineAudio is a real screen',/^<section class="screen" id="offlineAudio">/.test(SCREEN));
eq('offlineAudio screen exists once',count(INDEX,'id="offlineAudio"'),1);
ok('direct hash route includes offlineAudio',INDEX.indexOf('["about","privacy","contact","install","offlineAudio"].includes(ppInitialScreen)')!==-1);
ok('screen has shared Back control',tag('backOfflineAudio').indexOf('class="back"')!==-1);
ok('screen has shared Home control',SCREEN.indexOf('class="back home-btn"')!==-1);
ok('Back uses shared show(home)',INDEX.indexOf('$("backOfflineAudio").addEventListener("click", ()=>show("home"))')!==-1);
ok('screen entry calls controller enter',INDEX.indexOf('scr==="offlineAudio" && window.PPOfflineAudioUI')!==-1);
ok('screen exit calls nonblocking controller leave',INDEX.indexOf('window.PPOfflineAudioUI.leave()')!==-1);
ok('entry performs reconcile',UI.indexOf('engineRecord.engine.reconcile()')!==-1);
ok('entry never starts download',between(UI,'function enter()','function leave()').indexOf('.start(')===-1);

// Canonical manifest reuse and safe failure.
ok('startup and Retry share one manifest loader',INDEX.indexOf('function loadAudioManifest(force)')!==-1);
eq('there is one audio-manifest URL literal',count(INDEX,'"audio-manifest.json"'),1);
ok('startup performs one non-forced load',INDEX.indexOf('loadAudioManifest(false);')!==-1);
ok('explicit retry is the only forced path',UI.indexOf('check(unavailableReason === "manifest")')!==-1);
ok('canonical files are retained from entries file fields',INDEX.indexOf('Object.values(entries).map(entry => entry && entry.file)')!==-1);
ok('Offline audio never derives its inventory from audioMap',UI.indexOf('audioMap')===-1);
ok('engine prepareManifest validates the retained inventory',UI.indexOf('PPOfflineAudioEngine.prepareManifest(audioManifestFiles)')!==-1);
ok('malformed or empty inventory becomes unavailable',UI.indexOf('unavailableReason="manifest"')!==-1);
eq('committed manifest remains 3,621 entries',files.length,3621);
eq('committed manifest files remain unique',new Set(files).size,3621);

// Semantic structure and responsive accessibility.
ok('screen heading is exact',SCREEN.indexOf('<h1>Offline audio</h1>')!==-1);
ok('main card heading is exact',SCREEN.indexOf('<h2>Pronunciation audio</h2>')!==-1);
ok('size copy is exact',SCREEN.indexOf('About 52 MB')!==-1);
ok('screen uses one native progress element',count(SCREEN,'<progress'),1);
ok('progress has accessible name',tag('offlineAudioProgress').indexOf('aria-label="Downloading pronunciation audio"')!==-1);
ok('primary control is a native typed button',/^<button\b/.test(tag('offlineAudioPrimary')) && tag('offlineAudioPrimary').indexOf('type="button"')!==-1);
ok('remove control is a native typed button',/^<button\b/.test(tag('offlineAudioRemove')) && tag('offlineAudioRemove').indexOf('type="button"')!==-1);
eq('screen has one polite atomic status region',count(SCREEN,'role="status"'),1);
ok('status region is polite and atomic',tag('offlineAudioLive').indexOf('aria-live="polite"')!==-1 && tag('offlineAudioLive').indexOf('aria-atomic="true"')!==-1);
ok('buttons have a 44px minimum touch target',STYLE.indexOf('.offline-audio-btn{min-height:44px')!==-1);
ok('narrow actions stack without fixed width',STYLE.indexOf('.offline-audio-actions{flex-direction:column}')!==-1 && STYLE.indexOf('.offline-audio-btn{width:100%}')!==-1);
ok('copy can wrap long words',STYLE.indexOf('overflow-wrap:anywhere')!==-1);
ok('no fixed card width is added',STYLE.indexOf('.offline-audio-card{width:')===-1);
ok('reduced motion contract still covers screens',INDEX.indexOf('@media (prefers-reduced-motion:reduce)')!==-1 && INDEX.indexOf('.flip,.screen,.done')!==-1);

// Truthful state mapping and progress.
[
  'Checking downloaded pronunciation audio…','Download all pronunciation audio so it works without an internet connection.',
  'Download incomplete','Downloading pronunciation audio','Pausing after current downloads…',
  'You can continue any time.','Pronunciation audio available offline',
  'Download paused because the audio couldn’t be reached.','There isn’t enough browser storage to finish.',
  'One or more pronunciations couldn’t be downloaded.',
  'The browser couldn’t keep the full pronunciation library in offline storage.',
  'Offline audio isn’t available in this browser right now.',
  'Removing downloaded pronunciation audio…','Downloaded pronunciation audio removed.',
  'Downloaded audio couldn’t be removed. Nothing else was changed.'
].forEach(function(copy){ ok('state copy exists: '+copy,UI.indexOf(copy)!==-1 || SCREEN.indexOf(copy)!==-1); });
ok('ready zero maps to Download audio',UI.indexOf('status === "ready" && present === 0')!==-1 && UI.indexOf('setPrimary("Download audio", "download"')!==-1);
ok('partial maps to Continue and Remove',UI.indexOf('setPrimary("Continue download", "continue"')!==-1 && UI.indexOf('setRemove(present>0, false)')!==-1);
ok('Pause delegates only to engine pause',UI.indexOf('engineRecord.engine.pause()')!==-1 && UI.indexOf('AbortController')===-1);
ok('Continue delegates to engine continueDownload',UI.indexOf('engineRecord.engine.continueDownload()')!==-1);
ok('Download delegates to engine start',UI.indexOf('engineRecord.engine.start()')!==-1);
ok('progress max is the current total',UI.indexOf('progress.max=total || 1')!==-1);
ok('progress value is the durable present count',UI.indexOf('progress.value=present')!==-1);
ok('percentage consistently uses nearest whole percent',UI.indexOf('Math.round((present/total)*100)')!==-1);
ok('checking progress is indeterminate',hasCode(UI,'if(status === "checking"){') && UI.indexOf('progress.removeAttribute("value")')!==-1);
ok('100 percent is withheld for final reconciliation',UI.indexOf('present >= total')!==-1 && UI.indexOf('Final check…')!==-1);
ok('complete is accepted only as an engine state',UI.indexOf('status === "complete"')!==-1 && UI.indexOf('status="complete"')===-1);
ok('retention conflict offers no Continue',between(UI,'status === "retention-conflict"','status === "removing"').indexOf('setPrimary')===-1);
ok('generic partial does not invent update provenance',UI.indexOf('Update available')===-1 && UI.indexOf('new pronunciations')===-1);
ok('pluralization helper handles one pronunciation',UI.indexOf('Number(value) === 1 ? "pronunciation" : "pronunciations"')!==-1);

// Live announcements and focus.
ok('download start is announced',UI.indexOf('Download started.')!==-1);
ok('milestones are bucketed by ten percent',UI.indexOf('Math.floor((present*10)/total)')!==-1 && UI.indexOf('(bucket*10)+" percent downloaded.')!==-1);
ok('100 percent is not a pre-completion milestone',UI.indexOf('bucket < 10')!==-1);
ok('render does not call focus',between(UI,'function renderOfflineAudio(state)','function handleEngineState').indexOf('.focus(')===-1);
ok('controller uses shared overlay opener',UI.indexOf('ppOpenSharedOverlay(el("offlineAudioRemoveDialog"), el("offlineAudioRemoveCancel"))')!==-1);
ok('Cancel closes via shared overlay with focus restoration',UI.indexOf('offlineAudioRemoveCancel").addEventListener("click", ()=>ppCloseSharedOverlay')!==-1);
ok('Escape cancel closes via shared overlay',UI.indexOf('offlineAudioRemoveDialog").addEventListener("cancel"')!==-1);

// Remove, lifecycle, persistence, and protected boundaries.
ok('remove confirmation is a native shared dialog',/^<dialog\b/.test(tag('offlineAudioRemoveDialog')) && tag('offlineAudioRemoveDialog').indexOf('class="modal-overlay"')!==-1);
ok('remove copy includes naturally warmed clips',DIALOG.indexOf('including clips saved when you played them online')!==-1);
ok('remove copy protects learning progress',DIALOG.indexOf('Your learning progress is not affected')!==-1);
ok('Cancel is the initial focus target',UI.indexOf('el("offlineAudioRemoveCancel"))')!==-1);
ok('confirmation delegates to engine remove',UI.indexOf('engineRecord.engine.remove()')!==-1);
ok('confirmation is guarded against duplicate removal',UI.indexOf('if(!engineRecord || removalPending) return')!==-1);
ok('removing disables destructive control',UI.indexOf('setRemove(true, true)')!==-1);
ok('UI controller never opens or writes Cache Storage',UI.indexOf('caches.open')===-1 && UI.indexOf('cache.put')===-1 && UI.indexOf('cache.delete')===-1);
ok('navigation leave pauses active work without awaiting',between(INDEX,'function showScreen(','/* history-aware navigation').indexOf('PPOfflineAudioUI.leave();')!==-1);
ok('hidden document pauses active work',UI.indexOf('document.visibilityState === "hidden"')!==-1 && UI.indexOf('engineRecord.engine.pause()')!==-1);
ok('visible document never auto-resumes',between(UI,'document.addEventListener("visibilitychange"','if(el("offlineAudio")').indexOf('continueDownload')===-1);
ok('persistence helper is exposed once through PP_A2HS',INDEX.indexOf('nudgeHTML, requestPersist')!==-1);
ok('explicit Download or Continue requests persistence best effort',UI.indexOf('requestPersistence();')!==-1 && UI.indexOf('catch(e){}')!==-1);
ok('persistence does not gate engine start',between(UI,'function begin(action)','function confirmRemoval').indexOf('await')===-1);
ok('no localStorage completion/count/version state',UI.indexOf('localStorage')===-1);
ok('no polling or background sync in controller',UI.indexOf('setInterval')===-1 && UI.indexOf('SyncManager')===-1 && UI.indexOf('backgroundSync')===-1);
ok('stale engine and prior-entry callbacks are rejected',UI.indexOf('if(record !== engineRecord || !record.accept) return')!==-1 && UI.indexOf('engineRecord.accept=false')!==-1);
ok('manifest replacement recreates engine without auto-download',UI.indexOf('engineRecord.identity!==identity')!==-1 && between(UI,'if(!engineRecord || engineRecord.identity!==identity)','return engineRecord.engine.reconcile()').indexOf('.start(')===-1);

// Copy and frozen release/content invariants.
ok('Privacy describes lazy and optional full audio',INDEX.indexOf('Pronunciation clips continue to be saved one at a time as you play them.')!==-1 && INDEX.indexOf('download the full pronunciation library from Offline audio')!==-1);
ok('Privacy says audio stays local and outside backups',INDEX.indexOf('Saved pronunciation audio stays in this browser on this device, is not included in progress backups')!==-1);
ok('Privacy describes removal and eviction',INDEX.indexOf('can be removed from Offline audio')!==-1 && INDEX.indexOf('clear or evict saved audio')!==-1);
ok('Privacy date is 15 September 2026',INDEX.indexOf('Last updated 15 September 2026')!==-1);
ok('Install says install alone does not download all audio',INDEX.indexOf('installing the app by itself does not download them all')!==-1);
eq('APP_VERSION remains 9.15',count(INDEX,'const APP_VERSION = "9.15"'),1);
eq('shell cache remains popolsku-v70',count(SW,'const CACHE = "popolsku-v70"'),1);
eq('audio cache remains popolsku-audio',count(SW,'const AUDIO_CACHE = "popolsku-audio"'),1);
ok('worker file contains no Phase 2 screen markup or controller',SW.indexOf('id="offlineAudio"')===-1 && SW.indexOf('PPOfflineAudioUI')===-1);
ok('ordinary audioMap lookup remains present',INDEX.indexOf('const file = audioMap[key]')!==-1);
ok('no learner-flow prompt text was added to activity screens',
   ['study','grammar','convo','typeit','listen','round','patterns'].every(function(id){return section(id).indexOf('Offline audio')===-1;}));
ok('no analytics or telemetry added to controller',UI.indexOf('analytics')===-1 && UI.indexOf('telemetry')===-1);

console.log('Offline audio Phase 2 UI: '+PASS+' passed, '+FAIL+' failed');
LOG.forEach(function(line){console.log(line);});
if(FAIL) throw new Error(FAIL+' Phase 2 UI assertions failed');
