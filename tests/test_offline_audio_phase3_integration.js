// Deterministic Phase 3 offline-pronunciation integration/lifecycle tests.
//
//   osascript -l JavaScript tests/test_offline_audio_phase3_integration.js
//
// The Phase 1 shipping-code harness is executed first and its live fixtures are
// reused below. Historical worker evidence is read from immutable Git history.
// No real network request or MP3 body is used.
ObjC.import('Foundation');

function phase3Root(){
  var fm=$.NSFileManager.defaultManager,cwd=ObjC.unwrap(fm.currentDirectoryPath);
  return fm.fileExistsAtPath(cwd+'/index.html') ? cwd+'/' : cwd+'/../';
}
function phase3Read(path){
  var value=$.NSString.stringWithContentsOfFileEncodingError(path,$.NSUTF8StringEncoding,null);
  return ObjC.unwrap(value);
}
function runGit(args){
  var task=$.NSTask.alloc.init,pipe=$.NSPipe.pipe;
  task.currentDirectoryPath=$(phase3Root());
  task.launchPath='/usr/bin/git'; task.arguments=args;
  task.standardOutput=pipe; task.standardError=pipe;
  task.launch; task.waitUntilExit;
  return {status:Number(task.terminationStatus),output:ObjC.unwrap(
    $.NSString.alloc.initWithDataEncoding(pipe.fileHandleForReading.readDataToEndOfFile,$.NSUTF8StringEncoding))};
}

var PHASE3_ROOT=phase3Root();
eval(phase3Read(PHASE3_ROOT+'tests/test_offline_audio_phase1_engine.js'));
var PHASE1_PASS=PASS,PHASE1_FAIL=FAIL;
PASS=0; FAIL=0; FAILURES=[];

var CURRENT_SW=SW_SRC,CURRENT_INDEX=INDEX;
var UI_SRC=CURRENT_INDEX.slice(CURRENT_INDEX.indexOf('/* OFFLINE_AUDIO_UI_START'),
  CURRENT_INDEX.indexOf('/* OFFLINE_AUDIO_UI_END */'));
var oldCommit='9931aed6585012a0a407e0cd50d141de5f58639a';
var oldTree='0717d2ab7a04f02c5e9d378f4df5e59c25f44f52';
var oldWorkerResult=runGit(['show',oldCommit+':sw.js']);
var OLD_SW=oldWorkerResult.output;

// Evaluate the shipping default MessageChannel transport against a chosen
// active worker. Timers are controlled explicitly, so the unsupported-worker
// path is deterministic and never waits in wall-clock time.
function defaultTransportHarness(protocolWorker,registrationExtras){
  var posts=[],timers=[],timerSequence=0;
  function Channel(){
    var own=this;
    this.port1={onmessage:null,onmessageerror:null,closed:false,close:function(){this.closed=true;}};
    this.port2={postMessage:function(value){
      if(typeof own.port1.onmessage==='function') own.port1.onmessage({data:value});
    }};
  }
  var active={postMessage:function(data,ports){
    posts.push(data);
    if(protocolWorker) protocolWorker.fire('message',{data:data,ports:ports,
      waitUntil:function() {}});
  }};
  var registration=Object.assign({active:active},registrationExtras||{});
  var nav={serviceWorker:{ready:P.resolve(registration)}};
  function setTimer(fn,ms){var timer={id:++timerSequence,fn:fn,ms:ms,canceled:false};timers.push(timer);return timer.id;}
  function clearTimer(id){timers.forEach(function(timer){if(timer.id===id)timer.canceled=true;});}
  var win={},doc={baseURI:ORIGIN+'/'},loc={href:ORIGIN+'/'};
  var engine=(new Function('window','document','location','navigator','MessageChannel','URL','Promise',
    'setTimeout','clearTimeout',ENGINE_SRC+'\nreturn window.PPOfflineAudioEngine;'))(
      win,doc,loc,nav,Channel,FakeURL,P,setTimer,clearTimer);
  return {engine:engine,posts:posts,timers:timers,registration:registration};
}

// Historical provenance and protocol boundary.
eq('P3-01 engine suite remains at least the approved 89/0 baseline',[PHASE1_PASS,PHASE1_FAIL],[89,0]);
eq('P3-02 historical commit is the exact engine parent',
   runGit(['rev-parse','3a5b27ff4ae34a4aea09cef50fa8228fc789a166^']).output.trim(),oldCommit);
eq('P3-03 historical tree is exact',runGit(['rev-parse',oldCommit+'^{tree}']).output.trim(),oldTree);
eq('P3-04 historical worker object loads from Git',oldWorkerResult.status,0);
ok('P3-05 historical worker genuinely lacks the Offline-audio protocol',
   OLD_SW.indexOf('offline-audio-capabilities')===-1 && OLD_SW.indexOf('offline-audio-reconcile')===-1 &&
   OLD_SW.indexOf('offline-audio-store-one')===-1 && OLD_SW.indexOf('offline-audio-remove')===-1);
ok('P3-06 current worker exposes all four protocol commands',
   ['offline-audio-capabilities','offline-audio-reconcile','offline-audio-store-one','offline-audio-remove']
     .every(function(command){return CURRENT_SW.indexOf(command)!==-1;}));
var capabilityWorker=makeWorker(),capabilityReply=send(capabilityWorker,'offline-audio-capabilities',{}).value;
eq('P3-07 current worker capability reply is typed and versioned',
   [capabilityReply.outcome,capabilityReply.protocolVersion],['supported',1]);
eq('P3-08 capability command performs no fetch or cache mutation',
   [capabilityWorker.fetchCalls.length,capabilityWorker.caches.names.length],[0,0]);

// New page + genuine old behavior: old postMessage is represented by a worker
// that accepts and ignores the unknown command, exactly as the historical source.
var oldHarness=defaultTransportHarness(null),oldEngine=oldHarness.engine.create([hashFile(30001)],{baseHref:ORIGIN+'/'});
var oldProtocolRun=watch(oldEngine.reconcile()); drain();
eq('P3-09 new page sends only a lightweight capability probe to the old worker',
   [oldHarness.posts.length,oldHarness.posts[0].command,oldHarness.posts[0].files],
   [1,'offline-audio-capabilities',undefined]);
eq('P3-10 capability probe uses an independent short timeout',oldHarness.timers[0].ms,2500);
ok('P3-11 capability timeout is much shorter than the normal channel timeout',
   oldHarness.timers[0].ms*10 < 30000);
oldHarness.timers[0].fn(); drain();
eq('P3-12 ignored historical command becomes actionable without a store operation',
   [oldProtocolRun.value.status,oldProtocolRun.value.reason,oldHarness.posts.filter(function(p){return p.command==='offline-audio-store-one';}).length],
   ['interrupted','worker-protocol',0]);
eq('P3-13 unsupported active worker never receives the manifest or mutates page Cache Storage',
   [oldHarness.posts.some(function(p){return Array.isArray(p.files);}),ENGINE_SRC.indexOf('caches.')],[false,-1]);
ok('P3-14 ordinary pronunciation/fallback functions are outside capability failure handling',
   UI_SRC.indexOf('speakText')===-1 && CURRENT_INDEX.indexOf("Using your device's voice.")!==-1 &&
   CURRENT_INDEX.indexOf("Audio couldn't play. Check your connection, then try again.")!==-1);

// Supported active worker remains authoritative even with a future worker waiting.
var supportedWorker=makeWorker(),futureWaiting={postMessage:function(){}},supportedHarness=
  defaultTransportHarness(supportedWorker,{waiting:futureWaiting});
var supportedEngine=supportedHarness.engine.create([hashFile(30002)],{baseHref:ORIGIN+'/'});
var supportedCheck=watch(supportedEngine.reconcile()); drain();
eq('P3-15 supported active worker proceeds to reconciliation while a future worker waits',
   [supportedCheck.value.status,supportedHarness.posts.map(function(p){return p.command;})],
   ['ready',['offline-audio-capabilities','offline-audio-reconcile']]);
eq('P3-16 successful capability/reconciliation performs no network request',supportedWorker.fetchCalls.length,0);
var postsBeforeRetry=supportedHarness.posts.length;
watch(supportedEngine.reconcile()); drain();
eq('P3-17 Retry or re-entry performs a fresh active-worker capability check',
   supportedHarness.posts.slice(postsBeforeRetry).map(function(p){return p.command;}),
   ['offline-audio-capabilities','offline-audio-reconcile']);
ok('P3-18 capability request contains no manifest, audio URL, or persistent identifier',
   supportedHarness.posts.filter(function(p){return p.command==='offline-audio-capabilities';}).every(function(p){
     return Object.keys(p).sort().join(',')==='command,token' && /^oa-/.test(p.token);
   }));
ok('P3-19 waiting/installing state is used only for truthful update-pending copy',
   UI_SRC.indexOf('reg.waiting || reg.installing')!==-1 &&
   UI_SRC.indexOf('Offline audio will be available after Po polsku finishes updating.')!==-1 &&
   UI_SRC.indexOf('Close and reopen Po polsku, then try again.')!==-1);
ok('P3-20 update-pending UI has an explicit Retry action',
   UI_SRC.indexOf('setPrimary("Try again", "retry-check", false)')!==-1);

// Replacement invalidates an in-progress probe without auto-starting work.
var heldCapability=deferred(),replacementCommands=[];
var replacementTransport=function(command,payload){
  replacementCommands.push({command:command,payload:payload});
  if(command==='offline-audio-capabilities') return heldCapability.promise;
  return P.resolve({outcome:'reconciled',total:1,presentCount:0,missingCount:1,
    present:[],missing:[absolute(hashFile(30003))],invalid:0,mutationGeneration:0});
};
var controllerEngine=ENGINE.create([hashFile(30003)],{baseHref:ORIGIN+'/',transport:replacementTransport});
var controllerCheck=watch(controllerEngine.reconcile()); drain();
controllerEngine.invalidateWorker();
heldCapability.resolve({outcome:'supported',protocolVersion:1}); drain();
eq('P3-21 controller replacement invalidates the stale capability operation',
   [controllerCheck.value.status,controllerEngine.getState().reason],['interrupted','worker-changed']);
eq('P3-22 stale capability success cannot launch reconciliation or overwrite UI truth',
   [replacementCommands.length,replacementCommands[0].command], [1,'offline-audio-capabilities']);
ok('P3-23 controllerchange never auto-starts a download or reload',
   UI_SRC.indexOf('addEventListener("controllerchange"')!==-1 &&
   UI_SRC.slice(UI_SRC.indexOf('addEventListener("controllerchange"')).indexOf('.start()')===-1 &&
   UI_SRC.indexOf('location.reload')===-1);

// Current-stack integration results are live values from the shipping Phase 1 harness.
eq('P3-24 empty cache reconciliation is truthful',[supportedCheck.value.present,supportedCheck.value.missing],[0,1]);
eq('P3-25 partial warmed cache reconciliation is truthful',[exactReply.presentCount,exactReply.missingCount],[1,5]);
eq('P3-26 synthetic complete 3,621 library is truthful',
   [scaleRun.value.status,scaleRun.value.present,scaleWorker.fetchCalls.length],['complete',3621,3621]);
ok('P3-27 download concurrency remains at most three',scaleRun.value.maxActive<=3 && reentryMax<=3);
eq('P3-28 Pause permits only the three in-flight operations to finish',
   [pauseRun.value.status,pauseRun.value.present,pauseRun.value.maxActive],['paused',3,3]);
eq('P3-29 Continue resumes missing only',[continueRun.value.status,continueRun.value.present],['complete',8]);
eq('P3-30 stale-session successor correction remains green',
   [queuedRun.value.status,queuedRun.value.present,reentryMax],['complete',8,3]);
ok('P3-31 rapid Continue is deduplicated',queuedTwo===queuedOne && queuedThree===queuedOne);
eq('P3-32 Remove invalidates a queued successor',
   [canceledByRemove.value.status,queuedRemoveWorker.fetchCalls.length],['removed',3]);
eq('P3-33 a fresh engine reconstructs solely from Cache Storage',
   [reload.value.status,reload.value.present,reload.value.missing],['complete',12,0]);
eq('P3-34 future manifest growth queues only 59 missing clips',
   [updateRun.value.status,updateWorker.fetchCalls.length,updateRun.value.present],['complete',59,3680]);
eq('P3-35 network interruption remains bounded',
   [networkRun.value.status,networkWorker.fetchCalls.length],['network-failed',3]);
eq('P3-36 storage failure remains bounded',
   [storageStopRun.value.status,storageStopWorker.fetchCalls.length],['storage-failed',3]);
eq('P3-37 bad response is never cached',
   [badRun.value.status,badWorker.caches.inventory('popolsku-audio').length],['incomplete',6]);
eq('P3-38 retention conflict never loops',
   [conflictRun.value.status,conflictWorker.fetchCalls.length],['retention-conflict',1]);
eq('P3-39 Remove clears only popolsku-audio',
   [removal.value.outcome,raceWorker.caches.names.sort()],['removed',['popolsku-audio','popolsku-v71','unrelated-cache']]);
eq('P3-40 ordinary lazy playback warms audio again after Remove',
   [rewarm.response.value.status,raceWorker.caches.inventory('popolsku-audio').length],[200,1]);
eq('P3-41 warm Range playback remains correct',[warmRange.response.value.status,warmRange.response.value.headers.get('content-range')],[206,'bytes 1-3/6']);
eq('P3-42 cold Range remains pass-through without caching',
   [coldWorker.fetchCalls[0].request===coldRequest,coldWorker.caches.inventory('popolsku-audio')],[true,[]]);
eq('P3-43 If-Range remains pass-through',[ifRange.response,ifRangeWorker.fetchCalls.length],[null,0]);
ok('P3-44 intentional downloader requests never contain Range or If-Range',scaleWorker.fetchCalls.every(function(call){
  return call.request && call.request.method==='GET' && call.request.headers.get('range')===null &&
    call.request.headers.get('if-range')===null;
}));

// Release isolation, privacy and frozen markers.
ok('P3-45 no skipWaiting or clients.claim is introduced',
   CURRENT_SW.indexOf('self.skipWaiting(')===-1 && CURRENT_SW.indexOf('self.clients.claim(')===-1);
ok('P3-46 no automatic forced reload is introduced',UI_SRC.indexOf('location.reload')===-1);
ok('P3-47 no page-side Cache Storage mutation is added',
   ENGINE_SRC.indexOf('caches.')===-1 && UI_SRC.indexOf('caches.open')===-1 && UI_SRC.indexOf('cache.put')===-1);
ok('P3-48 no durable download/capability state is added',
   ENGINE_SRC.indexOf('localStorage')===-1 && UI_SRC.indexOf('localStorage')===-1 &&
   CURRENT_INDEX.indexOf('capabilityVersion')===-1);
ok('P3-49 no analytics or telemetry is added to Offline audio',
   ENGINE_SRC.indexOf('analytics')===-1 && ENGINE_SRC.indexOf('telemetry')===-1 &&
   UI_SRC.indexOf('analytics')===-1 && UI_SRC.indexOf('telemetry')===-1);
eq('P3-50 release markers match the current candidate',
   [(CURRENT_INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/)||[])[1],
    (CURRENT_SW.match(/const CACHE\s*=\s*"([^"]+)"/)||[])[1],
    (CURRENT_SW.match(/const AUDIO_CACHE\s*=\s*"([^"]+)"/)||[])[1]],
   ['9.16','popolsku-v71','popolsku-audio']);

console.log('Offline audio Phase 3 integration tests: '+PASS+' passed, '+FAIL+' failed.');
FAILURES.forEach(function(line){console.log('  '+line);});
if(FAIL) throw new Error('TESTS FAILED: '+FAIL+' assertion(s) failed');
