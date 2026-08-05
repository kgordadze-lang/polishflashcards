// Deterministic Phase 4B-2 coverage for the shipping sw.js and PP_A2HS block.
// Runs with: osascript -l JavaScript tests/test_phase4b2_offline_navigation_installability.js
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
var MANIFEST = readFile(ROOT + 'manifest.json');
var BUILD = readFile(ROOT + 'build_pages.py');
var MIGRATE = readFile(ROOT + 'pp-migrate.js');
var PASS = 0, FAIL = 0, LOG = [];
function ok(name, condition) { if (condition) PASS++; else { FAIL++; LOG.push('FAIL: ' + name); } }
function eq(name, actual, expected) {
  var a = JSON.stringify(actual), e = JSON.stringify(expected);
  ok(name + (a === e ? '' : ' (got ' + a + ', want ' + e + ')'), a === e);
}
function countOf(source, needle) {
  var count = 0, at = source.indexOf(needle);
  while (at !== -1) { count++; at = source.indexOf(needle, at + needle.length); }
  return count;
}
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

// Manually drained promises make service-worker writes and prompt outcomes exact in JXA.
var QUEUE = [];
function schedule(job) { QUEUE.push(job); }
function drain() {
  var guard = 0;
  while (QUEUE.length) { if (++guard > 100000) throw new Error('runaway queue'); QUEUE.shift()(); }
}
function P(executor) {
  this.state = 'pending'; this.value = undefined; this.handlers = [];
  var p = this;
  if (executor) try { executor(function (v) { resolveP(p, v); }, function (e) { rejectP(p, e); }); }
  catch (e) { rejectP(p, e); }
}
function resolveP(p, value) {
  if (p.state !== 'pending') return;
  if (value && typeof value.then === 'function') {
    var called = false;
    try { value.then(function (v) { if (!called) { called = true; resolveP(p, v); } },
                     function (e) { if (!called) { called = true; rejectP(p, e); } }); }
    catch (e) { if (!called) { called = true; rejectP(p, e); } }
    return;
  }
  p.state = 'fulfilled'; p.value = value; flushP(p);
}
function rejectP(p, error) { if (p.state === 'pending') { p.state = 'rejected'; p.value = error; flushP(p); } }
function flushP(p) {
  var hs = p.handlers; p.handlers = [];
  hs.forEach(function (h) { schedule(function () { runHandler(p, h); }); });
}
function runHandler(p, h) {
  var fn = p.state === 'fulfilled' ? h.ok : h.bad;
  if (typeof fn !== 'function') { (p.state === 'fulfilled' ? resolveP : rejectP)(h.next, p.value); return; }
  try { resolveP(h.next, fn(p.value)); } catch (e) { rejectP(h.next, e); }
}
P.prototype.then = function (yes, no) {
  var next = new P(), h = {ok:yes, bad:no, next:next}, p = this;
  if (this.state === 'pending') this.handlers.push(h); else schedule(function () { runHandler(p, h); });
  return next;
};
P.prototype['catch'] = function (no) { return this.then(undefined, no); };
P.resolve = function (v) { if (v instanceof P) return v; var p = new P(); resolveP(p, v); return p; };
P.reject = function (e) { var p = new P(); rejectP(p, e); return p; };
P.all = function (items) { return new P(function (resolve, reject) {
  items = Array.prototype.slice.call(items); var left = items.length, out = [];
  if (!left) { resolve(out); return; }
  items.forEach(function (item, i) { P.resolve(item).then(function (v) {
    out[i] = v; if (--left === 0) resolve(out);
  }, reject); });
}); };
function watch(value) {
  var rec = {state:'pending', value:undefined};
  P.resolve(value).then(function (v) { rec.state='fulfilled'; rec.value=v; },
                        function (e) { rec.state='rejected'; rec.value=e; });
  return rec;
}

function absoluteParts(input) {
  var m = /^([a-zA-Z][a-zA-Z0-9+.\-]*):([\s\S]*)$/.exec(String(input));
  if (!m) return null;
  var protocol=m[1].toLowerCase()+':', rest=m[2], host='', path=rest;
  if (rest.slice(0,2)==='//') {
    var after=rest.slice(2), cut=after.length;
    ['/', '?', '#'].forEach(function(ch){var at=after.indexOf(ch); if(at!==-1&&at<cut)cut=at;});
    host=after.slice(0,cut); path=after.slice(cut); if(!path||path[0]!=='/')path='/'+path;
  }
  var hash='', search='', at=path.indexOf('#');
  if(at!==-1){hash=path.slice(at);path=path.slice(0,at);} at=path.indexOf('?');
  if(at!==-1){search=path.slice(at);path=path.slice(0,at);}
  return {protocol:protocol,host:host,pathname:path,search:search,hash:hash};
}
function normalizePath(path) {
  var parts=path.split('/'), out=[];
  parts.forEach(function(seg,i){ if(seg==='.')return; if(seg==='..'){if(out.length>1)out.pop();return;} out.push(seg); });
  return out.join('/')||'/';
}
function FakeURL(input, base) {
  var p=absoluteParts(input);
  if(!p){
    var b=absoluteParts(base); if(!b)throw new TypeError('Invalid URL');
    var ref=String(input), hash='', search='', at=ref.indexOf('#');
    if(at!==-1){hash=ref.slice(at);ref=ref.slice(0,at);} at=ref.indexOf('?');
    if(at!==-1){search=ref.slice(at);ref=ref.slice(0,at);}
    var path=ref===''?b.pathname:(ref[0]==='/'?ref:normalizePath(b.pathname.replace(/[^/]*$/,'')+ref));
    p={protocol:b.protocol,host:b.host,pathname:path,search:search,hash:hash};
  }
  this.protocol=p.protocol;this.host=p.host;this.pathname=p.pathname;this.search=p.search;this.hash=p.hash;
  this.origin=(p.protocol==='http:'||p.protocol==='https:')&&p.host?p.protocol+'//'+p.host:'null';
  this.href=(p.host?p.protocol+'//'+p.host:p.protocol)+p.pathname+p.search+p.hash;
}
function Headers(map){this.map={};var h=this;Object.keys(map||{}).forEach(function(k){h.map[k.toLowerCase()]=map[k];});}
Headers.prototype.get=function(name){var v=this.map[String(name).toLowerCase()];return v===undefined?null:v;};
function Request(url, opts){opts=opts||{};this.url=url;this.method=opts.method||'GET';this.mode=opts.mode||'no-cors';this.headers=new Headers(opts.headers);}
function mime(url){var p=String(url).split('?')[0];if(p.slice(-1)==='/')return'text/html';if(/\.js$/.test(p))return'text/javascript';if(/\.json$/.test(p))return'application/json';if(/\.mp3$/.test(p))return'audio/mpeg';if(/\.svg$/.test(p))return'image/svg+xml';if(/\.png$/.test(p))return'image/png';if(/\.woff2$/.test(p))return'font/woff2';return'text/plain';}
var RESPONSE_ID=0;
function Response(opts){opts=opts||{};this.id=++RESPONSE_ID;this.status=opts.status===undefined?200:opts.status;this.ok=opts.ok===undefined?(this.status>=200&&this.status<300):opts.ok;this.type=opts.type===undefined?'basic':opts.type;this.redirected=!!opts.redirected;this.url=opts.url||'';this.label=opts.label||('body-'+this.id);this.headers=new Headers(opts.headers||{'Content-Type':mime(this.url)});this.bodyUsed=false;}
Response.prototype.clone=function(){return new Response({status:this.status,ok:this.ok,type:this.type,redirected:this.redirected,url:this.url,label:this.label,headers:this.headers.map});};
Response.redirect=function(url,status){return new Response({status:status||302,ok:false,type:'default',url:url,label:'redirect',headers:{Location:url}});};
function typed(url,label){return new Response({url:url,label:label||url,headers:{'Content-Type':mime(url)}});}
function badHtml(url,label){return new Response({url:url,label:label||'root-html',headers:{'Content-Type':'text/html'}});}
function keyOf(x){return typeof x==='string'?x:x.url;}
function Cache(name,storage){this.name=name;this.storage=storage;this.entries={};this.order=[];this.puts=[];this.deletes=[];}
Cache.prototype.match=function(req){var hit=this.entries[keyOf(req)];return P.resolve(hit===undefined?undefined:hit);};
Cache.prototype.put=function(req,res){var key=keyOf(req);this.puts.push(key);if(this.order.indexOf(key)===-1)this.order.push(key);this.entries[key]=res;return P.resolve();};
Cache.prototype['delete']=function(req){var key=keyOf(req);this.deletes.push(key);if(this.entries[key]===undefined)return P.resolve(false);delete this.entries[key];this.order=this.order.filter(function(k){return k!==key;});return P.resolve(true);};
function CacheStorage(seed){this.caches={};this.names=[];var s=this;Object.keys(seed||{}).forEach(function(name){var c=s.raw(name);Object.keys(seed[name]).forEach(function(key){c.order.push(key);c.entries[key]=seed[name][key];});});}
CacheStorage.prototype.raw=function(name){if(!this.caches[name]){this.caches[name]=new Cache(name,this);this.names.push(name);}return this.caches[name];};
CacheStorage.prototype.open=function(name){return P.resolve(this.raw(name));};
CacheStorage.prototype.keys=function(){return P.resolve(this.names.slice());};
CacheStorage.prototype['delete']=function(name){if(!this.caches[name])return P.resolve(false);delete this.caches[name];this.names=this.names.filter(function(n){return n!==name;});return P.resolve(true);};
CacheStorage.prototype.match=function(req){var key=keyOf(req);for(var i=0;i<this.names.length;i++){var hit=this.caches[this.names[i]].entries[key];if(hit!==undefined)return P.resolve(hit);}return P.resolve(undefined);};
function nav(url){return new Request(url,{mode:'navigate'});} function get(url,opts){return new Request(url,opts);}
var ORIGIN='https://popolsku.app';
var SW_EPILOGUE='\nreturn {CACHE:CACHE,AUDIO_CACHE:AUDIO_CACHE,ROOT_KEY:ROOT_KEY,SCOPE_PATH:SCOPE_PATH,'+
  'GENERATED_PAGE_ASSETS:GENERATED_PAGE_ASSETS,GENERATED_PAGE_PATHS:GENERATED_PAGE_PATHS,'+
  'classifyRequest:classifyRequest,canonicalKeyFor:canonicalKeyFor,parseUrl:parseUrl,state:SW_STATE};';
function worker(options){
  options=options||{};var caches=new CacheStorage(options.seed||{}), listeners={}, calls=[];
  function fetchFn(input,init){var url=keyOf(input);calls.push({url:url,input:input,init:init});if(options.offline)return P.reject(new TypeError('offline'));var result=options.route?options.route(url,input,init):null;return result&&result.reject?P.reject(result.reject):P.resolve(result&&result.response?result.response:typed(url));}
  var self={location:{origin:ORIGIN,href:ORIGIN+'/sw.js',pathname:'/sw.js'},ppSwState:null,addEventListener:function(type,fn){listeners[type]=fn;}};
  var api=(new Function('self','caches','fetch','Promise','URL','Response','console',SW_SRC+SW_EPILOGUE))(self,caches,fetchFn,P,FakeURL,Response,{warn:function(){}});
  return {api:api,self:self,caches:caches,calls:calls,fire:function(type,event){listeners[type](event);}};
}
function FetchEvent(request){this.request=request;this.responses=[];this.waits=[];}
FetchEvent.prototype.respondWith=function(p){this.responses.push(p);};FetchEvent.prototype.waitUntil=function(p){this.waits.push(p);};
function runFetch(w,request){var e=new FetchEvent(request);w.fire('fetch',e);drain();var r=e.responses.map(watch);drain();return{event:e,responses:r,intercepted:!!e.responses.length};}
function response(run){return run.responses[0]&&run.responses[0].value;}
function responseLabel(run){var r=response(run);return r?r.label:null;}
function responseStatus(run){var r=response(run);return r?r.status:null;}
function responseUrl(run){var r=response(run);return r?r.url:null;}
function responseLocation(run){var r=response(run);return r&&r.headers?r.headers.get('location'):null;}
function inventory(w,name){var c=w.caches.caches[name];return c?c.order.slice().sort():[];}
function seed(name,key,res){var all={};all[name]={};all[name][key]=res;return all;}

// A. Exact generated route inventory and classification.
var W=worker(), API=W.api, SHELL=API.CACHE;
eq('A1 shell cache revision is popolsku-v61',SHELL,'popolsku-v61');
eq('A1 audio cache remains popolsku-audio',API.AUDIO_CACHE,'popolsku-audio');
var generated=[];
['guide','grammar','vocabulary'].forEach(function(dir){
  var items=ObjC.deepUnwrap($.NSFileManager.defaultManager.subpathsAtPath(ROOT+dir));
  items.forEach(function(item){var rel=dir+'/'+item;if(/(^|\/)index\.html$/.test(rel))generated.push('./'+rel.replace(/index\.html$/,''));});
});
generated.sort();
eq('A2 explicit worker inventory exactly matches all committed generated pages',API.GENERATED_PAGE_ASSETS.slice().sort(),generated);
eq('A2 there are exactly 33 generated routes',generated.length,33);
generated.forEach(function(asset){
  var dir=asset.slice(1), explicit=dir+'index.html';
  eq('A3 directory classifies as generated: '+dir,API.classifyRequest(nav(ORIGIN+dir)),'generated-navigation');
  eq('A3 index alias classifies as generated: '+explicit,API.classifyRequest(nav(ORIGIN+explicit)),'generated-navigation');
});
eq('A4 root directory is distinct',API.classifyRequest(nav(ORIGIN+'/')),'root-navigation');
eq('A4 root index is distinct',API.classifyRequest(nav(ORIGIN+'/index.html')),'root-navigation');
['/grammar/not-real/','/vocabulary/not-real/','/guide/not-real/','/other/nested/'].forEach(function(path){eq('A4 unknown nested route stays unknown: '+path,API.classifyRequest(nav(ORIGIN+path)),'unknown-navigation');});
eq('A4 generated path requested as a script is not a generated navigation',API.classifyRequest(get(ORIGIN+'/guide/')),'unknown');

// B. Full offline-navigation matrix against shipping worker code.
(function(){var w=worker(),run=runFetch(w,nav(ORIGIN+'/'));eq('B1 root online is returned',responseStatus(run),200);eq('B1 root online is cached once',inventory(w,SHELL),[ORIGIN+'/']);})();
(function(){var w=worker({seed:seed(SHELL,ORIGIN+'/',typed(ORIGIN+'/','root-shell')),offline:true});eq('B2 root offline uses shell',responseLabel(runFetch(w,nav(ORIGIN+'/'))),'root-shell');eq('B3 /index.html offline aliases shell',responseLabel(runFetch(w,nav(ORIGIN+'/index.html'))),'root-shell');})();
(function(){var key=ORIGIN+'/grammar/biernik-accusative/';var w=worker();var a=runFetch(w,nav(key));eq('B4 generated directory online returns exact HTML',responseUrl(a),key);eq('B4 generated directory is cached under exact canonical key',inventory(w,SHELL),[key]);runFetch(w,nav(key+'index.html'));eq('B5 generated index online preserves original network request',w.calls[1]?w.calls[1].url:null,key+'index.html');eq('B5 directory/index aliases remain one cache entry',inventory(w,SHELL),[key]);})();
(function(){var key=ORIGIN+'/guide/listening/';var w=worker({seed:seed(SHELL,key,typed(key,'visited-listening')),offline:true});eq('B6 visited generated directory is exact offline',responseLabel(runFetch(w,nav(key))),'visited-listening');eq('B7 visited generated index alias is exact offline',responseLabel(runFetch(w,nav(key+'index.html'))),'visited-listening');})();
(function(){var key=ORIGIN+'/vocabulary/polish-idioms/';var w=worker();runFetch(w,nav(key+'?source=test#x'));runFetch(w,nav(key+'index.html?source=other'));eq('B8 irrelevant generated queries share one canonical entry',inventory(w,SHELL),[key]);eq('B8 browser-visible request URL is preserved',w.calls[1]?w.calls[1].url:null,key+'index.html?source=other');})();
(function(){
  var root=ORIGIN+'/', key=ORIGIN+'/grammar/wolacz-vocative/';
  [key,key+'index.html'].forEach(function(url){var w=worker({seed:seed(SHELL,root,typed(root,'root-shell')),offline:true});var run=runFetch(w,nav(url));eq('B9/B10 unvisited generated URL returns intentional redirect: '+url,[responseStatus(run),responseLocation(run),responseLabel(run)],[302,root,'redirect']);eq('B11 nested URL never receives root HTML body: '+url,responseLabel(run)!=='root-shell',true);eq('B12 redirect is not cached: '+url,inventory(w,SHELL),[root]);});
  var rootWorker=worker({seed:seed(SHELL,root,typed(root,'root-shell')),offline:true});eq('B13 redirected root does not loop',responseLabel(runFetch(rootWorker,nav(root))),'root-shell');
  var emptyRoot=worker({offline:true});eq('B13 an offline root miss never redirects to itself',responseStatus(runFetch(emptyRoot,nav(root))),null);
  eq('B14 root-relative dependency resolves at root after redirect',new FakeURL('pp-answer.js',root).href,ORIGIN+'/pp-answer.js');
})();
(function(){var w=worker({seed:seed(SHELL,ORIGIN+'/',typed(ORIGIN+'/','root-shell')),offline:true});var run=runFetch(w,nav(ORIGIN+'/unknown/nested/'));ok('B15 unknown nested route is not intercepted with a shell',!run.intercepted);})();
(function(){var w=worker({seed:seed(SHELL,ORIGIN+'/',typed(ORIGIN+'/','root-shell')),offline:true});['/pp-answer.js','/data-a1.js','/audio-manifest.json','/manifest.json'].forEach(function(path){var run=runFetch(w,get(ORIGIN+path));ok('B16 '+path+' never receives HTML fallback',!run.intercepted||!response(run)||response(run).label!=='root-shell');});})();
(function(){var w=worker({offline:true});ok('B17 cross-origin navigation remains outside app strategy',!runFetch(w,nav('https://example.com/guide/')).intercepted);})();
(function(){var key=ORIGIN+'/grammar/biernik-accusative/',own=typed(key,'own-page'),intruder=typed(key,'intruder-page'),seededCaches={'unrelated-tool-cache':{}};seededCaches[SHELL]={};var w=worker({seed:seededCaches,offline:true});w.caches.caches['unrelated-tool-cache'].entries[key]=intruder;w.caches.caches['unrelated-tool-cache'].order=[key];w.caches.caches[SHELL].entries[key]=own;w.caches.caches[SHELL].order=[key];eq('B18 generated read stays in named shell cache',responseLabel(runFetch(w,nav(key))),'own-page');})();
(function(){var key=ORIGIN+'/grammar/biernik-accusative/',bad=badHtml(key,'invalid-json');bad.headers=new Headers({'Content-Type':'application/json'});var w=worker({seed:seed(SHELL,key,bad),offline:true});var run=runFetch(w,nav(key));eq('B19 invalid inherited generated entry is evicted then redirected',[responseStatus(run),responseLocation(run)],[302,ORIGIN+'/']);eq('B19 invalid generated entry is gone',inventory(w,SHELL),[]);})();

// C. Execute the shipping PP_A2HS state machine.
var A2HS_START=INDEX.indexOf('const PP_A2HS = (function(){'),A2HS_END=INDEX.indexOf('})();',A2HS_START);
var A2HS_SOURCE=INDEX.slice(A2HS_START,A2HS_END+4);
var A2HS_FACTORY=Function('document','window','navigator','localStorage','matchMedia','location','URLSearchParams','show','ppUseInvokerForNextScreen','ppCloseSiteMenu','setTimeout','Promise',A2HS_SOURCE+'\nreturn PP_A2HS;');
function El(id){this.id=id;this.hidden=false;this.disabled=false;this.tabIndex=0;this.attrs={};this.textContent='';this.removed=false;}
El.prototype.setAttribute=function(k,v){this.attrs[k]=String(v);};El.prototype.getAttribute=function(k){return this.attrs[k]===undefined?null:this.attrs[k];};
El.prototype.remove=function(){this.removed=true;};
function Store(seed,throws){this.data=seed||{};this.throws=throws||{};this.sets=[];this.removes=[];}
Store.prototype.getItem=function(k){if(this.throws.read)throw new Error('read denied');return Object.prototype.hasOwnProperty.call(this.data,k)?this.data[k]:null;};
Store.prototype.setItem=function(k,v){if(this.throws.write)throw new Error('write denied');this.sets.push([k,String(v)]);this.data[k]=String(v);};
Store.prototype.removeItem=function(k){if(this.throws.remove)throw new Error('remove denied');this.removes.push(k);delete this.data[k];};
function a2hs(options){
  options=options||{};var ids={siteInstallItem:new El('siteInstallItem'),siteInstall:new El('siteInstall'),siteInstallDetail:new El('siteInstallDetail'),siteInstallStatus:new El('siteInstallStatus'),siteMenuButton:new El('siteMenuButton'),ppBanner:new El('ppBanner'),ppNative:new El('ppNative')};ids.ppNative.hidden=true;
  var windowEvents={},documentEvents={},created=[],shown=[],closed=[],nudges=[];
  if(options.visibleSurfaces){ids.ppNative.hidden=false;ids.ppBanner.hidden=false;var nudge=new El('existingNudge');nudge.installButton=new El('existingNudgeButton');nudge.remove=function(){this.removed=true;this.installButton.removed=true;};nudges.push(nudge);}
  var doc={body:{appendChild:function(x){created.push(x);}},getElementById:function(id){return ids[id]||null;},querySelectorAll:function(selector){return selector==='.pp-nudge'?nudges.filter(function(n){return!n.removed;}):[];},addEventListener:function(type,fn){documentEvents[type]=fn;},createElement:function(){return new El('created');}};
  var nav={userAgent:options.userAgent||'Desktop',platform:options.platform||'MacIntel',maxTouchPoints:options.maxTouchPoints||0,standalone:!!options.navigatorStandalone,storage:{persisted:function(){return P.resolve(true);},persist:function(){return P.resolve(true);}}};
  var win={navigator:nav,addEventListener:function(type,fn){windowEvents[type]=fn;}};
  var store=options.store||new Store(options.storage||{},options.storageThrows);
  function media(q){return{matches:!!options.standalone&&q==='(display-mode: standalone)'};}
  function Params(search){this.search=search||'';} Params.prototype.has=function(key){return this.search==='?'+key||this.search.indexOf('?'+key+'=')===0||this.search.indexOf('&'+key+'=')!==-1;};
  var api=A2HS_FACTORY(doc,win,nav,store,media,{search:options.search||''},Params,function(id){shown.push(id);},function(){},function(restore){closed.push(restore);return true;},function(){},P);
  api.init();drain();return{api:api,ids:ids,store:store,windowEvents:windowEvents,documentEvents:documentEvents,created:created,shown:shown,closed:closed,nudges:nudges};
}
function promptEvent(options){options=options||{};var e={prevented:0,prompts:0,preventDefault:function(){this.prevented++;},prompt:function(){this.prompts++;if(options.promptThrows)throw new Error('prompt failed');if(options.promptRejects)return P.reject(new Error('prompt rejected'));return P.resolve();}};Object.defineProperty(e,'userChoice',{get:function(){if(options.choiceThrows)throw new Error('choice getter failed');if(options.choiceRejects)return P.reject(new Error('choice rejected'));return P.resolve({outcome:options.outcome||'dismissed'});}});return e;}
function dispatchPrompt(env,event){if(env.windowEvents.beforeinstallprompt)env.windowEvents.beforeinstallprompt(event);drain();}
function activate(env){var result=env.api.install(),rec=typeof result==='string'?{state:'fulfilled',value:result}:watch(result);drain();return rec;}

(function(){var e=a2hs();eq('C1 normal browser without prompt shows instructions',e.api.installState(),'instructions');eq('C1 visible install control is enabled and keyboard reachable',[e.ids.siteInstallItem.hidden,e.ids.siteInstall.disabled,e.ids.siteInstall.tabIndex],[false,false,0]);})();
(function(){var e=a2hs({standalone:true});eq('C2 display-mode standalone is installed',e.api.installState(),'installed');eq('C2 standalone install control is coherently hidden',[e.ids.siteInstallItem.hidden,e.ids.siteInstall.disabled,e.ids.siteInstall.tabIndex,e.ids.siteInstallItem.getAttribute('aria-hidden')],[true,true,-1,'true']);var p=promptEvent();dispatchPrompt(e,p);eq('C2 stray prompt cannot override standalone',[e.api.installState(),p.prevented],["installed",1]);})();
(function(){var e=a2hs({navigatorStandalone:true});eq('C3 navigator.standalone is installed',e.api.installState(),'installed');eq('C3 iOS standalone hides install',e.ids.siteInstallItem.hidden,true);})();
['true','false'].forEach(function(v){var e=a2hs({storage:{'popolsku-a2hs':JSON.stringify({installed:v==='true'})}});eq('C4/C5 stale installed '+v+' is not authoritative',e.api.installState(),'instructions');eq('C4/C5 legacy installed '+v+' is removed',e.store.getItem('popolsku-a2hs'),null);});
(function(){var e=a2hs({storageThrows:{read:true}});eq('C6 storage read failure does not abort initialization',e.api.installState(),'instructions');})();
(function(){var store=new Store({'popolsku-a2hs':JSON.stringify({installed:true})},{remove:true});var e=a2hs({store:store});eq('C7 storage removal failure does not abort initialization',e.api.installState(),'instructions');})();
['?pwa','?pwa=0','?pwa=1','?pwa=false','?pwa=true','?x=1'].forEach(function(search){var e=a2hs({search:search});eq('C8-C13 query is never installation authority: '+search,e.api.installState(),'instructions');});
(function(){var e=a2hs(),p=promptEvent();dispatchPrompt(e,p);eq('C14 beforeinstallprompt is prevented and offered',[p.prevented,e.api.installState(),e.ids.siteInstallDetail.textContent],[1,'prompt','Ready']);eq('C14 beforeinstallprompt reveals the native install surface',e.ids.ppNative.hidden,false);})();
(function(){var e=a2hs({storage:{'popolsku-a2hs':JSON.stringify({installed:true,dismissed:1})}}),p=promptEvent();dispatchPrompt(e,p);eq('C15 stale installed state cannot suppress a new prompt',e.api.installState(),'prompt');eq('C15 unrelated A2HS cooldown field survives migration',JSON.parse(e.store.getItem('popolsku-a2hs')).dismissed,1);})();
(function(){var e=a2hs({standalone:true}),p=promptEvent();dispatchPrompt(e,p);eq('C16 beforeinstallprompt in standalone stays unavailable',e.api.installState(),'installed');eq('C16 standalone never exposes native install shortcut',e.ids.ppNative.hidden,true);})();
(function(){var e=a2hs(),p=promptEvent({outcome:'dismissed'});dispatchPrompt(e,p);var a=activate(e),b=activate(e);eq('C17 one event prompts at most once',p.prompts,1);eq('C18 dismissed choice returns safely',[a.state,a.value,e.api.installState()],['fulfilled','prompt','instructions']);eq('C17 consumed prompt is cleared before a second activation',b.value,'instructions');})();
(function(){var e=a2hs(),choice=new P(),p={prevented:0,prompts:0,preventDefault:function(){this.prevented++;},prompt:function(){this.prompts++;return P.resolve();},userChoice:choice};dispatchPrompt(e,p);var first=e.api.install(),second=e.api.install();eq('C17 concurrent activation is blocked while one prompt is pending',[p.prompts,second],[1,'busy']);resolveP(choice,{outcome:'dismissed'});watch(first);drain();})();
(function(){var e=a2hs(),p=promptEvent({outcome:'accepted'});dispatchPrompt(e,p);activate(e);eq('C19 accepted userChoice alone is not installed',e.api.installState(),'instructions');eq('C19 accepted choice makes no success announcement',e.created.length,0);eq('C19 accepted choice writes no installed boolean',e.store.sets.some(function(row){return row[1].indexOf('installed')!==-1;}),false);})();
(function(){var e=a2hs({visibleSurfaces:true}),p=promptEvent();dispatchPrompt(e,p);e.windowEvents.appinstalled();eq('C20 appinstalled becomes current-session authority without install()',e.api.installState(),'installed');eq('C20 appinstalled clears prompt and hides/locks the drawer action',[e.ids.siteInstallItem.hidden,e.ids.siteInstall.disabled,e.ids.siteInstall.tabIndex,e.ids.siteInstallItem.getAttribute('aria-hidden')],[true,true,-1,'true']);eq('C20 appinstalled retires native, banner, and completion-nudge surfaces',[e.ids.ppNative.hidden,e.ids.ppBanner.hidden,e.nudges[0].removed,e.nudges[0].installButton.removed],[true,true,true,true]);eq('C20 removed completion nudge no longer exposes its install button',e.nudges.filter(function(n){return!n.removed;}).length,0);eq('C20 appinstalled alone owns success announcement',e.created.length,1);eq('C20 appinstalled writes no permanent boolean',e.store.sets.some(function(row){return row[1].indexOf('installed')!==-1;}),false);})();
(function(){
  var choice=new P(),e=a2hs({visibleSurfaces:true}),p={prevented:0,prompts:0,preventDefault:function(){this.prevented++;},prompt:function(){this.prompts++;return P.resolve();},userChoice:choice};
  dispatchPrompt(e,p);var pending=watch(e.api.install());drain();eq('C20 pending prompt enters the busy state',e.api.install(),'busy');
  e.windowEvents.appinstalled();
  eq('C20 appinstalled immediately clears pending/busy state',[e.api.installState(),e.api.install(),e.ids.ppNative.hidden,e.ids.ppBanner.hidden,e.nudges[0].removed],['installed','installed',true,true,true]);
  resolveP(choice,{outcome:'accepted'});drain();
  eq('C20 late userChoice fulfillment cannot restore install surfaces',[pending.state,e.api.installState(),e.ids.ppNative.hidden,e.ids.ppBanner.hidden,e.ids.siteInstallItem.hidden,e.nudges[0].removed],['fulfilled','installed',true,true,true,true]);
  eq('C20 late userChoice creates no second success claim',e.created.length,1);
  eq('C20 late userChoice writes no installed boolean',e.store.sets.some(function(row){return row[1].indexOf('installed')!==-1;}),false);
})();
(function(){
  var promptPending=new P(),e=a2hs({visibleSurfaces:true}),p={prevented:0,prompts:0,preventDefault:function(){this.prevented++;},prompt:function(){this.prompts++;return promptPending;},userChoice:P.resolve({outcome:'accepted'})};
  dispatchPrompt(e,p);var pending=watch(e.api.install());drain();e.windowEvents.appinstalled();rejectP(promptPending,new Error('late prompt rejection'));drain();
  eq('C20 late prompt rejection after appinstalled is contained',[pending.state,e.api.installState(),e.ids.ppNative.hidden,e.ids.ppBanner.hidden,e.nudges[0].removed,e.created.length],['fulfilled','installed',true,true,true,1]);
})();
(function(){
  var choicePending=new P(),e=a2hs({visibleSurfaces:true}),p={prevented:0,prompts:0,preventDefault:function(){this.prevented++;},prompt:function(){this.prompts++;return P.resolve();},userChoice:choicePending};
  dispatchPrompt(e,p);var pending=watch(e.api.install());drain();e.windowEvents.appinstalled();rejectP(choicePending,new Error('late choice rejection'));drain();
  eq('C20 late userChoice rejection after appinstalled is contained',[pending.state,e.api.installState(),e.ids.ppNative.hidden,e.nudges[0].removed,e.created.length],['fulfilled','installed',true,true,1]);
})();
(function(){var e=a2hs({visibleSurfaces:true});e.windowEvents.appinstalled();var stray=promptEvent();dispatchPrompt(e,stray);eq('C20 stray post-install prompt is prevented but cannot reactivate install',[stray.prevented,e.api.installState(),e.ids.ppNative.hidden,e.ids.ppBanner.hidden,e.ids.siteInstallItem.hidden,e.ids.siteInstall.disabled,e.ids.siteInstall.tabIndex,e.nudges[0].removed],[1,'installed',true,true,true,true,-1,true]);})();
[{name:'prompt rejection',opts:{promptRejects:true}},{name:'prompt throw',opts:{promptThrows:true}},{name:'choice rejection',opts:{choiceRejects:true}},{name:'choice getter throw',opts:{choiceThrows:true}}].forEach(function(row){var e=a2hs(),p=promptEvent(row.opts);dispatchPrompt(e,p);var result=activate(e);eq('C21/C22 '+row.name+' is contained',result.state,'fulfilled');eq('C21/C22 '+row.name+' clears deferred state',e.api.installState(),'instructions');});
(function(){var e=a2hs(),first=promptEvent(),second=promptEvent();dispatchPrompt(e,first);dispatchPrompt(e,second);activate(e);eq('C23 duplicate event is deterministic: latest replaces prior',[first.prompts,second.prompts],[0,1]);})();
(function(){var first=a2hs();first.windowEvents.appinstalled();var second=a2hs({storage:first.store.data}),p=promptEvent();dispatchPrompt(second,p);eq('C24 new page session does not inherit appinstalled',second.api.installState(),'prompt');})();
(function(){var e=a2hs({storage:{'popolsku-a2hs':JSON.stringify({installed:true,other:'keep'})}}),p=promptEvent();dispatchPrompt(e,p);eq('C25 reinstall sequence offers new prompt',e.api.installState(),'prompt');eq('C25 migration preserves unrelated data in the A2HS record',JSON.parse(e.store.getItem('popolsku-a2hs')).other,'keep');})();
(function(){var e=a2hs({standalone:true});eq('C26 hidden install control cannot receive focus',[e.ids.siteInstall.disabled,e.ids.siteInstall.tabIndex],[true,-1]);var normal=a2hs();eq('C27 visible install control remains keyboard-operable',[normal.ids.siteInstall.disabled,normal.ids.siteInstall.tabIndex,typeof normal.documentEvents.click],[false,0,'function']);})();
(function(){var e=a2hs(),p=promptEvent({outcome:'accepted'});dispatchPrompt(e,p);activate(e);eq('C28 no success claim precedes authoritative event',e.created.length,0);e.windowEvents.appinstalled();eq('C28 authoritative event adds exactly one success claim',e.created.length,1);})();
(function(){var e=a2hs({storage:{unrelated:'untouched','popolsku-a2hs':JSON.stringify({installed:true})}});eq('C29/C30 migration never clears unrelated localStorage',e.store.getItem('unrelated'),'untouched');eq('C29 no permanent installed boolean remains',countOf(JSON.stringify(e.store.data),'installed'),0);})();

// D. Cross-phase source safeguards and frozen scope.
eq('D1 APP_VERSION is the 8.6 release',(INDEX.match(/APP_VERSION\s*=\s*"([^"]+)"/)||[])[1],'8.6');
eq('D1 shell cache is v61',(SW_SRC.match(/const CACHE\s*=\s*"([^"]+)"/)||[])[1],'popolsku-v61');
eq('D1 audio cache is unchanged',(SW_SRC.match(/const AUDIO_CACHE\s*=\s*"([^"]+)"/)||[])[1],'popolsku-audio');
eq('D1 schema and migration revisions stay 2',[(MIGRATE.match(/SCHEMA_VERSION\s*=\s*(\d+)/)||[])[1],(MIGRATE.match(/CONTENT_MIGRATION_REVISION\s*=\s*(\d+)/)||[])[1]],['2','2']);
eq('D2 no executable skipWaiting exists',countOf(SW_CODE,'skipWaiting('),0);eq('D2 no executable clients.claim exists',countOf(SW_CODE,'clients.claim('),0);eq('D2 cache.addAll is absent',countOf(SW_CODE,'.addAll('),0);
ok('D3 Phase 4B-1 MIME validation remains present',SW_CODE.indexOf('isCacheableResponse(')!==-1&&SW_CODE.indexOf('hasExpectedMediaType(')!==-1&&SW_CODE.indexOf('mediaTypeOf(')!==-1);
ok('D3 validated named-cache reads remain present',SW_CODE.indexOf('function cacheMatch(cacheName, key)')!==-1&&countOf(SW_CODE,'caches.match(')===0);
ok('D3 numeric-only shell cleanup remains present',SW_CODE.indexOf('/^popolsku-v[0-9]+$/')!==-1);
ok('D3 lifetime-bound writes remain present',SW_CODE.indexOf('event.waitUntil(promise)')!==-1&&SW_CODE.indexOf('cacheWrite(event, cacheName, key, response)')!==-1);
ok('D3 no broad GET interception or Range write was introduced',SW_CODE.indexOf('category === "unknown-navigation"')!==-1&&SW_CODE.indexOf('if (category === "range")')!==-1);
ok('D4 URL query markers are absent from installation authority',A2HS_SOURCE.indexOf('URLSearchParams')===-1&&A2HS_SOURCE.indexOf('location.search')===-1);
ok('D4 persisted installed state is never read or written as authority',A2HS_SOURCE.indexOf('read().installed')===-1&&A2HS_SOURCE.indexOf('s.installed = true')===-1);
ok('D4 current-session appinstalled authority is explicit',A2HS_SOURCE.indexOf('installedThisSession=true')!==-1);
ok('D4 appinstalled finalizer explicitly clears the deferred prompt',/function finalizeInstalled\(\)\{[^}]*deferred=null;[^}]*\}/.test(A2HS_SOURCE));
ok('D5 manifest/build/generated-content production inputs are not part of the implementation contract',MANIFEST.indexOf('"start_url": "./?pwa=1"')!==-1&&BUILD.indexOf('def write_sitemap(')!==-1);

console.log('Phase 4B-2 offline navigation/installability tests: '+PASS+' passed, '+FAIL+' failed.');
LOG.forEach(function(line){console.log(line);});
if(FAIL)throw new Error('TESTS FAILED: '+FAIL+' assertion(s) failed');
