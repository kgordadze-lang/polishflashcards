#!/usr/bin/env python3
"""
Po polsku - build static, crawlable grammar pages from data-grammar.js.

Why this exists: the app is a single-page PWA, so all lesson content lives in
JS and is invisible to search engines. This script renders every grammar
topic's TEACH content (not the drills) as real HTML at /grammar/<slug>/,
plus a /grammar/ hub page and the /guide/listening/ recommendations page,
and regenerates sitemap.xml. Each page links back
into the app to practice.

Run it from the project root whenever data-grammar.js changes:

    pip install json5
    python3 build_pages.py

Then commit the regenerated  grammar/  folder and  sitemap.xml.
No cache bump needed for page-content changes (pages are network-first),
but the FIRST deploy that introduces /grammar/ must ship together with the
sw.js navigate-handler fix - see the deploy notes.
"""

import datetime
import html
import json
import os
import re
import shutil
import unicodedata

# The data-file parser and ppNormalize() equivalent live in pp_audio_rule.py, which
# also owns the main-card audio rule. One parser, one normalizer: a page's audio
# lookup can't disagree with what generate_audio.py actually built.
from pp_audio_rule import load_levels, normalize

DATA_FILE = "data-grammar.js"
VOCAB_FILE = "data-b1.js"
# Vocabulary topics rendered as pages, with SEO-targeted slugs that match what
# learners actually search. Topics NOT listed here (notably Przekleństwa, which
# is mature-gated in the app by design) are never built - the gate stays a gate.
VOCAB_PAGES = {
    "Idiomy": ("polish-idioms", "Polish idioms explained - with literal translations and audio"),
    "Przys\u0142owia": ("polish-proverbs", "Polish proverbs explained - with literal translations and audio"),
    "Codzienny slang": ("everyday-polish-slang", "Everyday Polish slang - what Poles actually say"),
    "Reakcje (Ale masakra!)": ("polish-exclamations", "Polish exclamations and reactions - ale masakra, tragedia, dramat"),
    "Korpo-slang": ("polish-corporate-slang", "Polish corporate slang - office Polish decoded"),
    "Slang miejski i imprezowy": ("polish-party-slang", "Polish urban and party slang"),
}
VOCAB_PAGES = { k.encode().decode("unicode_escape") if "\\u" in k else k: v for k, v in VOCAB_PAGES.items() }
AUDIO_MANIFEST = "audio-manifest.json"
OUT_DIR = "grammar"
SITE = "https://popolsku.app"

# The app shell owns the viewport contract; generated pages read it rather than
# restating it, so the two surfaces cannot drift apart again (MLG-3A-15). The
# contract is device-width layout at normal initial scale with viewport-fit
# support, and it must never disable pinch zoom - a maximum-scale or
# user-scalable=no here would be an accessibility regression on 31 pages at
# once, so the build refuses to emit one.
REQUIRED_VIEWPORT_DIRECTIVES = ("width=device-width", "initial-scale=1.0")
ZOOM_BLOCKING_VIEWPORT_DIRECTIVES = ("maximum-scale", "minimum-scale", "user-scalable")

# ---------------------------------------------------------------- parsing


def load_audio_index():
    """normalized Polish phrase -> /audio/<hash>.mp3. The manifest is trusted:
    since the generate_audio.py integrity fix, an entry exists only if its
    clip was verifiably written, so no per-file disk check is needed here."""
    if not os.path.exists(AUDIO_MANIFEST):
        return {}
    entries = json.load(open(AUDIO_MANIFEST, encoding="utf-8")).get("entries", {})
    return {e["pl"]: "/" + e["file"] for e in entries.values()}


def slugify(name):
    """'Dopełniacz (Genitive)' -> 'dopelniacz-genitive'."""
    s = unicodedata.normalize("NFKD", name)
    s = s.replace("ł", "l").replace("Ł", "L")           # ł doesn't decompose
    s = s.encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s

# ---------------------------------------------------------------- rendering

STYLE = """
:root{--bg:#f8fafc;--card:#ffffff;--forest:#1e293b;--mint-bg:#e0e7ff;--mint-text:#4338ca;
--emerald:#4f46e5;--cream:#eef2ff;--logo-back:#a5b4fc;--sage-hover:#3730a3;--muted:#64748b;
--border:#e6ebf1;--shadow-sm:0 1px 2px rgba(30,27,75,.05),0 4px 12px rgba(30,27,75,.05);
--r-lg:26px;--r-md:18px;--r-sm:13px}
@font-face{font-family:"Plus Jakarta Sans";font-style:normal;font-weight:400;font-display:swap;src:url("/fonts/plus-jakarta-sans-v12-latin-regular.woff2") format("woff2")}
@font-face{font-family:"Plus Jakarta Sans";font-style:normal;font-weight:600;font-display:swap;src:url("/fonts/plus-jakarta-sans-v12-latin-600.woff2") format("woff2")}
@font-face{font-family:"Plus Jakarta Sans";font-style:normal;font-weight:700;font-display:swap;src:url("/fonts/plus-jakarta-sans-v12-latin-700.woff2") format("woff2")}
@font-face{font-family:"Plus Jakarta Sans";font-style:normal;font-weight:800;font-display:swap;src:url("/fonts/plus-jakarta-sans-v12-latin-800.woff2") format("woff2")}
*{box-sizing:border-box}
/* Safe-area contract: the insets live on <body> only - the same declaration the
app shell uses - so nothing double-applies them, the centred .wrap keeps its
own 20px gutter inside them, and a zero-inset device is byte-for-byte the old
layout. Padding on an auto-width block can never widen the document. */
body{margin:0;background:var(--bg);color:var(--forest);
font-family:"Plus Jakarta Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
-webkit-font-smoothing:antialiased;line-height:1.55;overflow-wrap:break-word;
padding:env(safe-area-inset-top,0px) env(safe-area-inset-right,0px)
        env(safe-area-inset-bottom,0px) env(safe-area-inset-left,0px)}
.wrap{max-width:640px;margin:0 auto;padding:0 20px 48px}
a{color:var(--emerald)}a:hover{color:var(--sage-hover)}
a:focus-visible,button:focus-visible{outline:2px solid var(--emerald);outline-offset:2px}
.top{display:flex;align-items:center;gap:12px;padding:26px 0 6px}
.logo-mark{position:relative;width:38px;height:38px;flex:0 0 auto}
.lm-back{position:absolute;inset:0;border-radius:11px;background:var(--logo-back);transform:rotate(-5deg) translate(-2px,1px)}
.lm-front{position:absolute;inset:0;border-radius:11px;background:var(--forest);color:var(--cream);
display:grid;place-items:center;font-weight:800;font-size:14px;letter-spacing:-.5px;box-shadow:0 4px 10px rgba(30,27,75,.18)}
.lm-kreska{position:absolute;top:6px;right:6px;width:9px;height:2.6px;border-radius:2px;background:var(--emerald);transform:rotate(-28deg);z-index:2}
.top a{text-decoration:none;color:var(--forest)}.top b{font-size:17px;font-weight:700;letter-spacing:-.3px}
.crumbs{font-size:13px;color:var(--muted);margin:14px 0 0}
.crumbs a{text-decoration:none}
h1{font-size:30px;line-height:1.1;font-weight:800;letter-spacing:-.9px;margin:16px 0 6px}
.lede{color:var(--muted);font-weight:500;margin:0 0 6px}
.chip{display:inline-block;background:var(--mint-bg);color:var(--mint-text);font-size:12px;font-weight:700;
padding:4px 10px;border-radius:999px;margin:8px 0 20px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r-lg);
box-shadow:var(--shadow-sm);padding:22px 22px 18px;margin:0 0 16px}
.card h2{font-size:19px;font-weight:800;letter-spacing:-.4px;margin:0 0 4px}
.card .sub{color:var(--muted);font-size:14.5px;margin:0 0 12px}
.card ul{margin:0 0 12px;padding-left:20px}.card li{margin:4px 0}
table{width:100%;border-collapse:collapse;font-size:14px;margin:0 0 12px}
/* Reflow contract: an auto-layout table cannot render narrower than the widest
unbreakable word in each column, which is what pushed 11 grammar pages past the
viewport at 320px. overflow-wrap:anywhere lowers that floor to one character, so
the table reflows inside the card instead of widening the page - the row stays a
real table row and no cell is clipped or hidden. */
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--border);vertical-align:top;
overflow-wrap:anywhere}
th{font-size:12px;text-transform:uppercase;letter-spacing:.4px;color:var(--muted)}
.note,.explain{background:var(--cream);border-radius:var(--r-sm);padding:10px 14px;font-size:14px;margin:0 0 12px}
.ex{display:flex;align-items:flex-start;gap:10px;border-top:1px dashed var(--border);padding:10px 0 2px}
.ex:first-of-type{border-top:0}
.ex .pl{font-weight:700}.ex .en{color:var(--muted);font-size:14px}
.say{flex:0 0 auto;width:34px;height:34px;border-radius:10px;border:1px solid var(--border);background:var(--card);
color:var(--emerald);cursor:pointer;display:grid;place-items:center}
.say svg{width:17px;height:17px}
.say[data-playing]{background:var(--mint-bg)}
/* Audio status and retry (MLG-4A-04): one live region, moved next to whichever
control failed, holding the message and a single keyboard-operable retry. Laid
out in flow, so it can never cover the sentence it is talking about. */
.audio-status{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 0;
padding:9px 12px;border:1px solid var(--border);border-radius:var(--r-sm);background:var(--card);
color:var(--forest);font-size:13.5px;font-weight:600;line-height:1.4;text-align:left}
.audio-status[hidden]{display:none}
.audio-status .audio-retry{flex:0 0 auto;border:1px solid var(--emerald);background:var(--card);
color:var(--emerald);font:inherit;font-weight:700;padding:6px 12px;border-radius:999px;cursor:pointer}
.audio-status .audio-retry:hover{background:var(--mint-bg)}
.audio-status .audio-retry[hidden]{display:none}
.hub-list{list-style:none;margin:20px 0;padding:0;display:flex;flex-direction:column;gap:10px}
.hub-list a{display:flex;align-items:center;gap:12px;background:var(--card);border:1px solid var(--border);
border-radius:var(--r-md);box-shadow:var(--shadow-sm);padding:14px 16px;text-decoration:none;color:var(--forest)}
.hub-list .t{font-weight:700}.hub-list .d{color:var(--muted);font-size:13.5px}
.hub-list .ic{flex:0 0 auto;width:38px;height:38px;border-radius:12px;background:var(--cream);
color:var(--emerald);display:grid;place-items:center}
.hub-list .ic svg{width:19px;height:19px}
/* Every flex row on a generated page has one fixed child (the 34px audio
button, the 38px logo tile, the 38px hub icon, the retry button) and one text
child. The text child needs min-width:0, or its automatic minimum size keeps it
at min-content width and the row widens the page instead of wrapping. */
.top a>b,.ex>div,.hub-list a>span,.audio-status .audio-status-msg{min-width:0}
footer{color:var(--muted);font-size:13px;text-align:center;padding:26px 0 0}
footer a{text-decoration:none}
"""

LEARNING_ENDING_STYLE = """
.guide-ending{margin:28px 0 0;padding:20px;background:var(--card);border:1px solid var(--border);
border-radius:var(--r-md);box-shadow:var(--shadow-sm)}
.guide-ending h2{font-size:20px;line-height:1.3;font-weight:800;letter-spacing:-.35px;margin:0 0 7px}
.guide-ending-support{color:var(--muted);font-size:14.5px;margin:0 0 16px}
.guide-primary{display:inline-flex;align-items:center;justify-content:center;background:var(--emerald);color:#fff;
text-decoration:none;font-weight:700;padding:11px 17px;border-radius:var(--r-sm)}
.guide-primary:hover{background:var(--sage-hover);color:#fff}
.guide-reassurance{color:var(--forest);font-size:12.5px;font-weight:700;margin:14px 0 5px}
footer.guide-footer{color:var(--muted);font-size:12px;font-weight:600;letter-spacing:.2px;
text-align:center;padding:20px 0 0}
@media (max-width:420px){
  .guide-ending{padding:18px}
  .guide-primary{display:flex;width:100%}
}
"""

def _icon(paths):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>')

ICONS = {
    "flag":     _icon('<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>'),
    "box":      _icon('<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.3 7 12 12 20.7 7"/><line x1="12" y1="22" x2="12" y2="12"/>'),
    "gift":     _icon('<polyline points="20 12 20 22 4 22 4 12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/>'),
    "target":   _icon('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'),
    "tool":     _icon('<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>'),
    "pin":      _icon('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
    "megaphone":_icon('<path d="M3 11l18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>'),
    "smile":    _icon('<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>'),
    "briefcase":_icon('<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'),
    "compass":  _icon('<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'),
    "plane":    _icon('<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>'),
    "check":    _icon('<polyline points="20 6 9 17 4 12"/>'),
    "users":    _icon('<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>'),
    "hand":     _icon('<path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v6"/><path d="M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>'),
    "sparkles": _icon('<path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z"/>'),
    "mail":     _icon('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>'),
    "quote":    _icon('<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2H4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2h-4c-1.25 0-2 .75-2 2v6c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2z"/>'),
    "scroll":   _icon('<path d="M19 17V5a2 2 0 0 0-2-2H4"/><path d="M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3"/>'),
    "chat":     _icon('<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'),
    "zap":      _icon('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'),
    "music":    _icon('<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>'),
    "book":     _icon('<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>'),
}

ICON_MAP = [
    ("mianownik","flag"),("dopelniacz","box"),("celownik","gift"),("biernik","target"),
    ("narzednik","tool"),("miejscownik","pin"),("wolacz","megaphone"),
    ("przymiotniki","smile"),("zawody","briefcase"),("zaimki","compass"),
    ("narodowosci","plane"),("kazdy","check"),
    ("pan-i-pani","hand"),("panowie","users"),("tryb","sparkles"),
    ("zdrobnienia","smile"),("korespondencja","mail"),
    ("polish-idioms","quote"),("polish-proverbs","scroll"),("everyday","chat"),
    ("exclamations","zap"),("corporate","briefcase"),("party","music"),
]

def pick_icon(slug):
    for key, name in ICON_MAP:
        if key in slug:
            return ICONS[name]
    return ICONS["book"]


AUDIO_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/></svg>')

# The generated-page audio runtime. It is deliberately the same POLICY as the app
# shell's: the pre-generated clip first, ONE speech-synthesis fallback if it
# fails, and an announced, visible failure with a single retry when neither can
# make a sound. Before this, a generated page did nothing but drop the playing
# marker - no fallback, no message, no way to try again.
#
# The Polish text for the fallback comes from the button's own data-pl attribute,
# written by this generator. It is never recovered by parsing the aria-label:
# the label is a sentence for a screen reader ("Play Polish example: ..."), not a
# machine-readable field, and speaking it back would speak the English purpose
# text too.
#
# Every attempt carries a token. A late error, rejection or completion from an
# attempt the learner has already replaced must not announce an old failure,
# restore an old retry, clear the new control's playing marker, or start speech
# for a phrase that is no longer on screen.
PLAYER_JS = """
(function(){
  var FALLBACK_MSG = "Using your device's voice.";
  var FAILED_MSG = "Audio couldn't play. Check your connection, then try again.";
  var RETRY_MSG = "Try again";
  var token = 0, playing = null, marked = null, request = null;
  var box = null, msg = null, retry = null, owner = null;
  function host(){
    if(box) return box;
    box = document.createElement("div");
    box.id = "pp-audio-status";
    box.className = "audio-status";
    box.setAttribute("role", "status");
    box.setAttribute("aria-live", "polite");
    box.setAttribute("aria-atomic", "true");
    box.hidden = true;
    msg = document.createElement("span");
    msg.id = "pp-audio-status-msg";
    msg.className = "audio-status-msg";
    retry = document.createElement("button");
    retry.id = "pp-audio-retry";
    retry.className = "audio-retry";
    retry.type = "button";
    retry.textContent = RETRY_MSG;
    retry.hidden = true; retry.disabled = true; retry.tabIndex = -1;
    retry.addEventListener("click", function(e){ e.stopPropagation(); again(); });
    box.appendChild(msg); box.appendChild(retry);
    document.body.appendChild(box);
    return box;
  }
  function clear(){
    if(!box) return;
    box.hidden = true;
    msg.textContent = "";
    retry.hidden = true; retry.disabled = true; retry.tabIndex = -1;
    if(owner && owner.getAttribute && owner.getAttribute("aria-describedby") === "pp-audio-status-msg"){
      owner.removeAttribute("aria-describedby");
    }
    owner = null;
  }
  function show(kind, btn){
    var el = host();
    if(btn && btn.insertAdjacentElement){ try{ btn.insertAdjacentElement("afterend", el); }catch(e){} }
    var failed = kind === "failed";
    msg.textContent = failed ? FAILED_MSG : FALLBACK_MSG;
    retry.hidden = !failed; retry.disabled = !failed; retry.tabIndex = failed ? 0 : -1;
    el.hidden = false;
    owner = btn || null;
    if(failed && btn && btn.setAttribute) btn.setAttribute("aria-describedby", "pp-audio-status-msg");
  }
  function unmark(){
    if(marked && marked.dataset) delete marked.dataset.playing;
    marked = null;
  }
  function stop(){
    token++;
    if(playing){ try{ playing.pause(); }catch(e){} playing = null; }
    if(window.speechSynthesis){ try{ window.speechSynthesis.cancel(); }catch(e){} }
    unmark();
    clear();
  }
  function speak(text, btn, mine, afterFailedClip){
    if(!text || !window.speechSynthesis || typeof window.SpeechSynthesisUtterance !== "function"){
      show("failed", btn); return;
    }
    var u;
    try{ u = new window.SpeechSynthesisUtterance(text); }
    catch(e){ show("failed", btn); return; }
    u.lang = "pl-PL";
    u.onend = function(){ if(mine !== token) return; unmark(); };
    u.onerror = function(){ if(mine !== token) return; unmark(); show("failed", btn); };
    if(afterFailedClip) show("fallback", btn);
    if(btn && btn.dataset){ marked = btn; btn.dataset.playing = "1"; }
    try{ window.speechSynthesis.speak(u); }
    catch(e){ unmark(); show("failed", btn); }
  }
  function play(btn){
    stop();
    var mine = token;
    var url = btn.getAttribute("data-audio");
    var text = btn.getAttribute("data-pl") || "";
    request = { btn: btn, text: text };
    if(!url){ speak(text, btn, mine, false); return; }
    var a = new Audio(url);
    playing = a; marked = btn; btn.dataset.playing = "1";
    var settled = false;
    function settle(){
      if(settled) return false;
      settled = true;
      if(mine !== token) return false;
      playing = null; unmark();
      return true;
    }
    a.addEventListener("ended", function(){ settle(); });
    a.addEventListener("error", function(){ if(settle()) speak(text, btn, mine, true); });
    a.play().catch(function(){ if(settle()) speak(text, btn, mine, true); });
  }
  function again(){
    if(!request) return;
    var btn = request.btn;
    if(btn && btn.focus){ try{ btn.focus(); }catch(e){} }
    if(btn) play(btn);
  }
  document.addEventListener("click", function(e){
    var b = e.target.closest("[data-audio]"); if(!b) return;
    play(b);
  });
  /* Parked before it is ever needed: a live region has to exist before its text
     changes for the change to be announced reliably. Same reason, same moment,
     as the app shell. */
  host();
})();
"""

CSP = ('<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; '
       'script-src \'self\' \'unsafe-inline\'; style-src \'self\' \'unsafe-inline\'; '
       'font-src \'self\'; img-src \'self\'; connect-src \'self\'; media-src \'self\'; '
       'base-uri \'self\'; form-action \'self\'">')

esc = html.escape           # for plain-text fields
# front/sub/points/explain/note legitimately contain <b>/<i> authored markup -
# rendered as-is, same trust model as the app itself.
_ESCAPED_BOLD_TAG = re.compile(r"&lt;(/?)b&gt;")


def render_example_emphasis(text):
    """Escape an authored table example, then restore only balanced <b> pairs."""
    rendered = esc(text)
    expect_closing = False
    for match in _ESCAPED_BOLD_TAG.finditer(rendered):
        is_closing = bool(match.group(1))
        if is_closing != expect_closing:
            return rendered
        expect_closing = not expect_closing
    if expect_closing:
        return rendered
    return rendered.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


# The grammar source predates generated-page language metadata, and its table
# fields do not have one stable meaning: `g`, `e` and `ex` each contain English,
# Polish or both in different lessons.  This is therefore an explicit contract
# for every shipping table, keyed by the stable generated slug and teach-card
# index rather than inferred from a column, spelling or presence of diacritics.
# The three values describe (g, e, ex); English inherits the root language.
TABLE_LANGUAGE_CONTRACT = {
    ("mianownik-nominative", 2): ("en", "pl", "pl"),
    ("mianownik-nominative", 4): ("en", "pl", "pl"),
    ("mianownik-nominative", 5): ("en", "pl", "pl"),
    ("dopelniacz-genitive", 2): ("en", "pl", "pl"),
    ("dopelniacz-genitive", 3): ("en", "pl", "pl"),
    ("dopelniacz-genitive", 4): ("pl", "pl", "pl"),
    ("dopelniacz-genitive", 5): ("en", "pl", "pl"),
    ("celownik-dative", 2): ("en", "pl", "pl"),
    ("celownik-dative", 3): ("en", "pl", "pl"),
    ("celownik-dative", 4): ("pl", "pl", "pl"),
    ("celownik-dative", 5): ("en", "pl", "pl"),
    ("celownik-dative", 6): ("en", "pl", "pl"),
    ("biernik-accusative", 2): ("pl", "pl", "pl"),
    ("biernik-accusative", 3): ("pl", "pl", "pl"),
    ("biernik-accusative", 4): ("en", "en", "pl"),
    ("biernik-accusative", 5): ("en", "en", "pl"),
    ("biernik-accusative", 6): ("en", "pl", "pl"),
    ("narzednik-instrumental", 2): ("en", "pl", "pl"),
    ("narzednik-instrumental", 3): ("pl", "pl", "pl"),
    ("narzednik-instrumental", 4): ("en", "pl", "pl"),
    ("narzednik-instrumental", 6): ("en", "pl", "pl"),
    ("miejscownik-locative", 2): ("en", "pl", "pl"),
    ("miejscownik-locative", 3): ("en", "pl", "pl"),
    ("miejscownik-locative", 4): ("en", "pl", "pl"),
    ("miejscownik-locative", 5): ("en", "pl", "pl"),
    ("wolacz-vocative", 2): ("en", "pl", "pl"),
    ("wolacz-vocative", 3): ("en", "pl", "pl"),
    ("wolacz-vocative", 4): ("en", "en", "pl"),
    ("wolacz-vocative", 5): ("en", "pl", "pl"),
    ("przymiotniki-adjectives-traits", 1): ("en", "pl", "pl"),
    ("przymiotniki-adjectives-traits", 2): ("en", "pl", "pl"),
    ("przymiotniki-adjectives-traits", 3): ("en", "pl", "pl"),
    ("przymiotniki-adjectives-traits", 4): ("en", "pl", "pl"),
    ("przymiotniki-adjectives-traits", 5): ("en", "pl", "pl"),
    ("zawody-professions", 1): ("en", "pl", "pl"),
    ("zawody-professions", 2): ("en", "pl", "pl"),
    ("zawody-professions", 3): ("en", "pl", "pl"),
    ("zawody-professions", 4): ("en", "pl", "pl"),
    ("zawody-professions", 5): ("en", "pl", "pl"),
    ("zawody-professions", 6): ("en", "pl", "pl"),
    ("zaimki-pronouns-determiners", 1): ("en", "pl", "pl"),
    ("zaimki-pronouns-determiners", 2): ("en", "pl", "pl"),
    ("zaimki-pronouns-determiners", 4): ("en", "pl", "pl"),
    ("zaimki-pronouns-determiners", 5): ("en", "pl", "en"),
    ("narodowosci-nationalities", 1): ("en", "pl", "pl"),
    ("narodowosci-nationalities", 2): ("en", "pl", "pl"),
    ("narodowosci-nationalities", 3): ("en", "pl", "pl"),
    ("narodowosci-nationalities", 4): ("en", "pl", "pl"),
    ("narodowosci-nationalities", 5): ("en", "pl", "pl"),
    ("narodowosci-nationalities", 6): ("en", "pl", "pl"),
    ("kazdy-i-wszyscy-every-vs-all", 1): ("en", "pl", "pl"),
    ("kazdy-i-wszyscy-every-vs-all", 2): ("en", "pl", "pl"),
    ("kazdy-i-wszyscy-every-vs-all", 4): ("en", "pl", "pl"),
    ("stopniowanie-comparison", 1): ("pl", "en", "pl"),
    ("stopniowanie-comparison", 2): ("pl", "en", "pl"),
    ("stopniowanie-comparison", 5): ("pl", "en", "pl"),
    ("stopniowanie-comparison", 6): ("pl", "en", "pl"),
    ("liczebniki-numbers-meet-cases", 1): ("en", "pl", "pl"),
    ("liczebniki-numbers-meet-cases", 3): ("en", "pl", "pl"),
    ("liczebniki-numbers-meet-cases", 4): ("en", "pl", "pl"),
    ("liczebniki-numbers-meet-cases", 6): ("en", "pl", "pl"),
    ("pan-i-pani-formal-address", 1): ("pl", "pl", "pl"),
    ("pan-i-pani-formal-address", 2): ("pl", "pl", "pl"),
    ("pan-i-pani-formal-address", 3): ("pl", "en", "pl"),
    ("panowie-panie-panstwo-plural-formal-address", 1): ("pl", "pl", "pl"),
    ("panowie-panie-panstwo-plural-formal-address", 2): ("pl", "pl", "pl"),
    ("panowie-panie-panstwo-plural-formal-address", 3): ("pl", "pl", "pl"),
    ("panowie-panie-panstwo-plural-formal-address", 4): ("pl", "pl", "pl"),
    ("tryb-przypuszczajacy-conditional", 1): ("pl", "pl", "pl"),
    ("tryb-przypuszczajacy-conditional", 2): ("en", "pl", "pl"),
    ("zdrobnienia-diminutives", 1): ("pl", "pl", "pl"),
    ("zdrobnienia-diminutives", 2): ("pl", "pl", "pl"),
    ("korespondencja-formal-writing", 0): ("en", "pl", "pl"),
    ("korespondencja-formal-writing", 2): ("en", "pl", "pl"),
    ("korespondencja-formal-writing", 3): ("en", "pl", "pl"),
    ("ktory-relative-clauses", 1): ("en", "pl", "pl"),
    ("ktory-relative-clauses", 3): ("en", "pl", "pl"),
    ("jesli-i-gdyby-conditions", 2): ("pl", "pl", "pl"),
    ("jesli-i-gdyby-conditions", 4): ("en", "pl", "pl"),
    ("zeby-so-that-want-to", 2): ("pl", "pl", "pl"),
    ("zeby-so-that-want-to", 3): ("pl", "en", "pl"),
    ("przeczenie-negation", 2): ("pl", "en", "pl"),
    ("przeczenie-negation", 4): ("en", "pl", "pl"),
}


# Exceptions are also corpus-owned.  A string replaces the table contract for
# one pure-language cell; a tuple scopes the exact authored fragments in a mixed
# cell.  Exact rendering validation plus exhaustive generator tests make wording
# drift fail loudly instead of silently receiving stale language metadata.
TABLE_CELL_LANGUAGE_OVERRIDES = {
    ("dopelniacz-genitive", 5, 2, "e"): "en",
    ("dopelniacz-genitive", 5, 3, "e"): "en",
    ("celownik-dative", 3, 0, "e"): (("pl", "-e"), ("en", " (with softening)")),
    ("celownik-dative", 4, 2, "ex"): "en",
    ("biernik-accusative", 5, 0, "g"): (("en", "Masculine personal "), ("pl", "(oni)")),
    ("biernik-accusative", 5, 1, "g"): (("en", "Everything else "), ("pl", "(one)")),
    ("miejscownik-locative", 3, 0, "e"): (("pl", "-e"), ("en", " (with softening)")),
    ("miejscownik-locative", 4, 0, "e"): (("pl", "-e"), ("en", " (softening)")),
    ("miejscownik-locative", 4, 2, "g"): "pl",
    ("wolacz-vocative", 2, 2, "ex"): (("pl", "pani → pani"), ("en", " (no change)")),
    ("wolacz-vocative", 3, 0, "e"): (("pl", "-e"), ("en", " (with softening)")),
    ("wolacz-vocative", 3, 1, "g"): (("en", "After k, g, ch (and "), ("pl", "syn"), ("en", ")")),
    ("wolacz-vocative", 5, 1, "ex"): (("pl", "Pani doktor!"), ("en", " (title often stays in Nom)")),
    ("stopniowanie-comparison", 6, 0, "g"): (("pl", "coraz"), ("en", " + comparative")),
    ("stopniowanie-comparison", 6, 2, "g"): (("pl", "jak naj"), ("en", " + superlative")),
    ("panowie-panie-panstwo-plural-formal-address", 1, 0, "g"): (("pl", "wy"), ("en", " (informal)")),
    ("zdrobnienia-diminutives", 1, 0, "g"): (("pl", "-ek"), ("en", " (masc)")),
    ("zdrobnienia-diminutives", 1, 1, "g"): (("pl", "-ka"), ("en", " (fem)")),
    ("zdrobnienia-diminutives", 1, 2, "g"): (("pl", "-ko"), ("en", " (neut)")),
    ("zdrobnienia-diminutives", 1, 4, "g"): (("pl", "-usia"), ("en", " (extra warm)")),
    ("ktory-relative-clauses", 3, 0, "g"): (("pl", "z"), ("en", " + Instrumental")),
    ("ktory-relative-clauses", 3, 1, "g"): (("pl", "w"), ("en", " + Locative")),
    ("ktory-relative-clauses", 3, 2, "g"): (("pl", "o"), ("en", " + Locative")),
    ("ktory-relative-clauses", 3, 3, "g"): (("pl", "na"), ("en", " + Accusative")),
    ("ktory-relative-clauses", 3, 4, "g"): (("pl", "do"), ("en", " + Genitive")),
}


def table_cell_language(slug, teach_index, row_index, field):
    """Return the explicit language contract for one shipping table cell."""
    key = (slug, teach_index)
    if key not in TABLE_LANGUAGE_CONTRACT:
        raise ValueError(f"missing table language contract: {key}")
    base = dict(zip(("g", "e", "ex"), TABLE_LANGUAGE_CONTRACT[key]))[field]
    return TABLE_CELL_LANGUAGE_OVERRIDES.get((slug, teach_index, row_index, field), base)


def render_table_cell(value, language):
    """Render one cell without changing its text or trusting arbitrary markup."""
    if isinstance(language, str):
        if language not in {"en", "pl"}:
            raise ValueError(f"invalid table language: {language}")
        content = render_example_emphasis(value)
        return f'<td lang="pl">{content}</td>' if language == "pl" else f"<td>{content}</td>"
    if "".join(text for _, text in language) != value:
        raise ValueError(f"stale mixed table language contract: {value!r}")
    parts = []
    for part_language, text in language:
        if part_language not in {"en", "pl"}:
            raise ValueError(f"invalid table fragment language: {part_language}")
        rendered = render_example_emphasis(text)
        parts.append(f'<span lang="pl">{rendered}</span>' if part_language == "pl" else rendered)
    return "<td>" + "".join(parts) + "</td>"


def head(title, desc, canon, ld, extra_style=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="{esc(read_app_viewport())}">
<meta name="theme-color" content="#f8fafc">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg?v=17">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Po polsku">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-image.png?v=2">
<meta name="twitter:card" content="summary_large_image">
{CSP}
<meta name="referrer" content="strict-origin-when-cross-origin">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{STYLE}{extra_style}</style>
</head>
<body>
<div class="wrap">
<header class="top"><a href="/" aria-label="Po polsku home" style="display:flex;align-items:center;gap:12px">
<span class="logo-mark"><span class="lm-back"></span><span class="lm-kreska"></span><span class="lm-front">PL</span></span>
<b>Po polsku</b></a></header>
<main>
"""

def extract_app_version(source):
    """Read the sole human-facing version declaration without duplicating it."""
    match = re.search(r'\bconst\s+APP_VERSION\s*=\s*"([^"]+)"\s*;', source)
    if not match or not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+(?:-[0-9]+)?", match.group(1)):
        raise RuntimeError("could not find a valid APP_VERSION in index.html")
    return match.group(1)


def extract_app_viewport(source):
    """Read the app shell's viewport declaration - the contract both surfaces share."""
    match = re.search(r'<meta\s+name="viewport"\s+content="([^"]*)"\s*/?>', source)
    if not match:
        raise RuntimeError("could not find the app shell viewport declaration in index.html")
    viewport = match.group(1)
    directives = [part.strip() for part in viewport.split(",")]
    missing = [name for name in REQUIRED_VIEWPORT_DIRECTIVES if name not in directives]
    if missing:
        raise RuntimeError(f"app shell viewport is missing {missing}: {viewport!r}")
    blocking = [name for name in ZOOM_BLOCKING_VIEWPORT_DIRECTIVES
                if any(directive.split("=")[0].strip() == name for directive in directives)]
    if blocking:
        raise RuntimeError(f"app shell viewport blocks user zoom via {blocking}: {viewport!r}")
    return viewport


def read_app_shell(purpose="the app shell contract"):
    """The app shell is the single source of truth for version and viewport."""
    app_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
    try:
        with open(app_source, encoding="utf-8") as source_file:
            return source_file.read()
    except OSError as exc:
        raise RuntimeError(f"could not read index.html for {purpose}") from exc


def read_app_version():
    return extract_app_version(read_app_shell("APP_VERSION"))


def read_app_viewport():
    return extract_app_viewport(read_app_shell("the viewport contract"))


def learning_ending():
    """Shared calm closing card for every learner-facing generated page."""
    return (
        '<section class="guide-ending" aria-labelledby="guideEndingTitle">'
        '<h2 id="guideEndingTitle">Ready to keep learning?</h2>'
        '<p class="guide-ending-support">Practice the same Polish with flashcards, drills, '
        'conversations, and listening.</p>'
        '<a class="guide-primary" href="/">Open the app</a>'
        '<p class="guide-reassurance">Genuinely free. No account. Works offline.</p>'
        '</section>'
    )


def learning_footer(js=""):
    """Shared versioned footer, preserving optional page-specific JavaScript."""
    version = esc(read_app_version())
    year = datetime.date.today().year
    return (f'</main><footer class="guide-footer"><a href="/">Po polsku</a> &middot; '
            f'v{version} &middot; {year}</footer></div><script>{js}</script></body></html>')


def audio_control_name(purpose, phrase):
    """Contextual text-only name for one generated-page audio control."""
    context = re.sub(r"\s+", " ", str(phrase or "")).strip()
    return f"{purpose}: {context}" if context else purpose


def pronunciation_button(purpose, pl, audio_idx):
    """One pronunciation control, with or without a pre-generated clip.

    The page runtime plays the MP3 when there is one and speaks the Polish
    directly when there is not, so a phrase whose clip has not been generated yet
    still deserves a control - it simply carries an empty data-audio. The old
    conditional dropped the button entirely whenever the lookup missed, which made
    the generated pages silently weaker than the app shell: the shell has always
    fallen back to the device voice for a phrase the manifest does not cover.

    data-pl is the SAME normalized text generate_audio.py keys its clips by, so
    the spoken phrase is exactly the phrase the button is about. A phrase that
    normalizes to nothing gets no control at all: there would be nothing to say.
    """
    spoken = normalize(pl)
    if not spoken:
        return ""
    url = audio_idx.get(spoken, "")
    return (f'<button class="say" data-audio="{esc(url)}" data-pl="{esc(spoken)}" '
            f'type="button" '
            f'aria-label="{esc(audio_control_name(purpose, pl))}">{AUDIO_SVG}</button>')


def render_examples(examples, audio_idx):
    out = []
    for ex in examples:
        pl, en = ex.get("pl", ""), ex.get("en", "")
        btn = pronunciation_button("Play Polish example", pl, audio_idx)
        out.append(f'<div class="ex">{btn}<div><div class="pl" lang="pl">{esc(pl)}</div>'
                   f'<div class="en">{esc(en)}</div></div></div>')
    return "".join(out)


def render_teach_card(item, audio_idx, slug=None, teach_index=None):
    h = ['<section class="card">']
    h.append(f'<h2>{item.get("front","")}</h2>')
    if item.get("sub"):
        h.append(f'<p class="sub">{item["sub"]}</p>')
    if item.get("points"):
        h.append("<ul>" + "".join(f'<li>{p}</li>' for p in item["points"]) + "</ul>")
    if item.get("table"):
        rows = "".join(
            "<tr>" + "".join(
                render_table_cell(r.get(field, ""), table_cell_language(slug, teach_index, row_index, field))
                for field in ("g", "e", "ex")
            ) + "</tr>"
            for row_index, r in enumerate(item["table"])
        )
        h.append('<table><thead><tr><th>Group</th><th>Ending</th><th>Example</th></tr></thead>'
                 f'<tbody>{rows}</tbody></table>')
    if item.get("note"):
        h.append(f'<div class="note">{item["note"]}</div>')
    if item.get("explain"):
        h.append(f'<div class="explain">{item["explain"]}</div>')
    if item.get("examples"):
        h.append(render_examples(item["examples"], audio_idx))
    h.append("</section>")
    return "".join(h)


def topic_page(level, topic, slug, audio_idx):
    name = topic["name"]
    desc = topic.get("desc", "")
    canon = f"{SITE}/grammar/{slug}/"
    title = f"{name} - Polish grammar explained | Po polsku"
    meta_desc = (f"{desc}. Clear explanations with tables, examples with Polish pronunciation audio, "
                 f"and free practice drills - {topic.get('chip','')} on Po polsku.")
    ld = {
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "name": name,
        "description": desc,
        "url": canon,
        "inLanguage": "en",
        "teaches": f"Polish grammar: {name}",
        "educationalLevel": topic.get("chip", "").replace("Grammar ", ""),
        "learningResourceType": "Lesson",
        "isAccessibleForFree": True,
        "provider": {"@type": "Organization", "name": "Po polsku", "url": SITE + "/"},
    }
    body = [head(title, meta_desc, canon, ld, LEARNING_ENDING_STYLE)]
    body.append('<nav class="crumbs" aria-label="Breadcrumb">'
                '<a href="/">Home</a> &rsaquo; <a href="/guide/">Guide</a> '
                f'&rsaquo; {esc(name)}</nav>')
    body.append(f'<h1>{esc(name)}</h1>')
    body.append(f'<p class="lede">{esc(desc)}</p>')
    body.append(f'<span class="chip">{esc(topic.get("chip",""))}</span>')
    for teach_index, item in enumerate(topic.get("teach", [])):
        body.append(render_teach_card(item, audio_idx, slug, teach_index))
    body.append(learning_ending())
    body.append(learning_footer(PLAYER_JS))
    return "".join(body)


def vocab_card(c, audio_idx):
    """One vocabulary entry: word + audio, meaning, usage note, example."""
    pl, en = c.get("pl", ""), c.get("en", "")
    btn = pronunciation_button("Play Polish pronunciation", pl, audio_idx)
    h = ['<section class="card">']
    h.append(f'<div class="ex" style="border-top:0;padding-top:0">{btn}'
             f'<div><h2 lang="pl" style="margin:0">{esc(pl)}</h2>'
             f'<div class="en" style="font-size:15px">{esc(en)}</div></div></div>')
    if c.get("pair"):
        h.append(f'<div class="note"><b>Aspect pair:</b> <span lang="pl">{esc(c["pair"])}</span></div>')
    if c.get("hint"):
        h.append(f'<div class="note">{c["hint"]}</div>')
    if c.get("ex"):
        h.append(render_examples([{"pl": c["ex"], "en": c.get("exEn", "")}], audio_idx))
    h.append("</section>")
    return "".join(h)


def vocab_page(topic, slug, page_title, audio_idx):
    name = topic["name"]
    desc = topic.get("desc", "")
    canon = f"{SITE}/vocabulary/{slug}/"
    title = f"{page_title} | Po polsku"
    n = len(topic.get("cards", []))
    meta_desc = (f"{desc} {n} expressions with meanings, usage notes, real example "
                 f"sentences, and Polish pronunciation audio - free on Po polsku.")
    ld = {
        "@context": "https://schema.org",
        "@type": "LearningResource",
        "name": page_title,
        "description": desc,
        "url": canon,
        "inLanguage": "en",
        "teaches": f"Polish vocabulary: {name}",
        "educationalLevel": "B1",
        "learningResourceType": "Vocabulary list",
        "isAccessibleForFree": True,
        "provider": {"@type": "Organization", "name": "Po polsku", "url": SITE + "/"},
    }
    body = [head(title, meta_desc, canon, ld, LEARNING_ENDING_STYLE)]
    body.append('<nav class="crumbs" aria-label="Breadcrumb">'
                '<a href="/">Home</a> &rsaquo; <a href="/guide/">Guide</a> '
                f'&rsaquo; {esc(page_title)}</nav>')
    body.append(f'<h1>{esc(page_title)}</h1>')
    body.append(f'<p class="lede">{esc(desc)}</p>')
    body.append('<span class="chip">B1</span>')
    for c in topic.get("cards", []):
        body.append(vocab_card(c, audio_idx))
    body.append(learning_ending())
    body.append(learning_footer(PLAYER_JS))
    return "".join(body)


def guide_page(topics_by_level, vocab_items):
    canon = f"{SITE}/guide/"
    title = "Polish guide - grammar, slang and idioms explained simply | Po polsku"
    meta_desc = ("Free Polish for learners: all seven cases, formal address, adjectives - plus real "
                 "slang, idioms and proverbs. Tables, usage notes, and examples with Polish pronunciation audio.")
    ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Polish guide",
        "description": meta_desc,
        "url": canon,
        "inLanguage": "en",
        "provider": {"@type": "Organization", "name": "Po polsku", "url": SITE + "/"},
    }
    body = [head(title, meta_desc, canon, ld, LEARNING_ENDING_STYLE)]
    body.append('<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; Guide</nav>')
    body.append('<h1>Polish, explained simply</h1>')
    body.append('<p class="lede">Built by a foreigner living in Poland and learning the language '
                'through everyday life - with practical flashcards, clear explanations, pronunciation '
                'audio, and free interactive practice for every topic.</p>')
    body.append('<div class="note" style="margin:16px 0 22px">These pages are a sample - a taste of each '
                'topic. The full library, with every card, drill, and conversation, lives in the free app.</div>')
    for level_name, items in topics_by_level:
        body.append(f'<span class="chip">{esc(level_name)}</span>')
        body.append('<ul class="hub-list">')
        for name, desc, slug, emoji in items:
            body.append(f'<li><a href="/grammar/{slug}/"><span class="ic">{pick_icon(slug)}</span>'
                        f'<span><span class="t">{esc(name)}</span><br>'
                        f'<span class="d">{esc(desc)}</span></span></a></li>')
        body.append('</ul>')
    body.append('<span class="chip">Slang &amp; idioms</span>')
    body.append('<ul class="hub-list">')
    for page_title, desc, slug, emoji, n in vocab_items:
        body.append(f'<li><a href="/vocabulary/{slug}/"><span class="ic">{pick_icon(slug)}</span>'
                    f'<span><span class="t">{esc(page_title)}</span><br>'
                    f'<span class="d">{esc(desc)} ({n} expressions)</span></span></a></li>')
    body.append('</ul>')
    body.append('<span class="chip">Beyond the app</span>')
    body.append('<ul class="hub-list">')
    body.append('<li><a href="/guide/listening/"><span class="ic">' + ICONS["music"] + '</span>'
                '<span><span class="t">What else I listen to</span><br>'
                '<span class="d">Three Polish listening resources that actually helped</span>'
                '</span></a></li>')
    body.append('</ul>')
    body.append(learning_ending())
    body.append(learning_footer())
    return "".join(body)


def listening_page():
    """A hand-written recommendation page. Unlike every other page here it isn't
    derived from the data files - it's editorial, so the copy lives inline. It
    still goes through build_pages.py because /guide/ is wiped and rebuilt on
    every run, so anything dropped in there by hand would not survive."""
    canon = f"{SITE}/guide/listening/"
    title = "Polish podcasts worth listening to | Po polsku"
    meta_desc = ("Three Polish listening resources that actually helped - from learner-friendly "
                 "input to natural Polish at full speed. Honest notes on what's free, what isn't, "
                 "and what level each works best for.")
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "What else I listen to",
        "description": meta_desc,
        "url": canon,
        "inLanguage": "en",
        "publisher": {"@type": "Organization", "name": "Po polsku", "url": SITE + "/"},
    }
    body = [head(title, meta_desc, canon, ld, LEARNING_ENDING_STYLE)]
    body.append('<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> &rsaquo; '
                '<a href="/guide/">Guide</a> &rsaquo; What I listen to</nav>')
    body.append('<h1>What else I listen to</h1>')
    body.append('<p class="lede">Flashcards help you learn words. Getting used to the sound of Polish '
                'takes hours of listening. These are three resources I keep coming back to because they '
                'cover different stages of the same journey: clear learner-friendly Polish, real-life '
                'listening with plenty of visual context, and natural Polish at full speed.</p>')

    body.append('<div class="card">')
    body.append('<h2>Real Polish</h2>')
    body.append('<p class="sub"><a href="https://realpolish.pl/" target="_blank" rel="noopener">realpolish.pl</a> '
                '&middot; also on Spotify and YouTube</p>')
    body.append('<p>Piotr records in Polish, slowly and clearly, about culture, history and ordinary '
                'life. The idea is comprehensible input - you should understand most of it and be '
                'stretched by the rest, which is a very different feeling from being lost.</p>')
    body.append('<p>The episodes are free. Transcripts and the extra study material are paid. I got a '
                'long way on the free episodes alone, so start there and decide later.</p>')
    body.append('<div class="note">Works from roughly A2 onward. Below that it will feel fast - that is '
                'normal, and it is worth coming back to in a month or two.</div>')
    body.append('</div>')

    body.append('<div class="card">')
    body.append('<h2>Polish with Kamil</h2>')
    body.append('<p class="sub"><a href="https://www.youtube.com/@polishwithkamil" target="_blank" '
                'rel="noopener">youtube.com/@polishwithkamil</a> &middot; extra podcasts, transcripts '
                'and exercises on <a href="https://www.patreon.com/cw/polishwithkamil" target="_blank" '
                'rel="noopener">Patreon</a></p>')
    body.append('<p>Kamil teaches Polish through comprehensible input: everyday vlogs, short lessons, '
                'games and interviews that help you understand the message without needing to know '
                'every word. He speaks clearly and gives you plenty of visual context, but the Polish '
                'still feels natural and connected to real situations.</p>')
    body.append('<p>The YouTube content is free. His Patreon adds a weekly slow-Polish podcast with '
                'full transcripts and extra practice exercises.</p>')
    body.append('<div class="note">Good from beginner level onward. Start with the comprehensible-input '
                'videos and vlogs; the interviews are a natural next step when you want faster, less '
                'predictable Polish.</div>')
    body.append('</div>')

    body.append('<div class="card">')
    body.append('<h2>Ratio viva</h2>')
    body.append('<p class="sub"><a href="https://www.youtube.com/@Ratio_viva" target="_blank" rel="noopener">'
                'youtube.com/@Ratio_viva</a> &middot; also on Spotify</p>')
    body.append('<p>Not a learning channel at all. Nikodem makes short videos about psychology and '
                'the thinking errors behind everyday decisions - made for Poles, at Polish speed. '
                'That is exactly why it is useful: real pace, real vocabulary, nobody slowing down '
                'for you. Closed captions are on, so you can read along when your ears give out.</p>')
    body.append('<div class="note">Harder than Real Polish. I treat it as the thing I graduate into, '
                'and I still pause it constantly.</div>')
    body.append('</div>')

    body.append('<p class="note" style="margin:22px 0 4px;text-align:center">These are personal '
                'recommendations. None of the creators paid to be included here.</p>')
    body.append(learning_ending())
    body.append(learning_footer())
    return "".join(body)


def redirect_stub(target):
    """Old hub URLs point to the merged guide. GitHub Pages can't do server
    redirects, so: instant meta refresh + canonical (search engines follow
    the canonical, so no duplicate-content issue) + a visible link fallback."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Po polsku guide</title>
<meta http-equiv="refresh" content="0; url={target}">
<link rel="canonical" href="{SITE}{target}">
<meta name="robots" content="noindex">
</head>
<body><main><p>Moved to <a href="{target}">the Po polsku guide</a>.</p></main></body>
</html>
"""


def write_sitemap(slugs, vslugs=()):
    today = datetime.date.today().isoformat()
    urls = ([f"{SITE}/", f"{SITE}/guide/", f"{SITE}/guide/listening/"]
            + [f"{SITE}/grammar/{s}/" for s in slugs]
            + [f"{SITE}/vocabulary/{s}/" for s in vslugs])
    items = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n" for u in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f'{items}</urlset>\n')
    open("sitemap.xml", "w", encoding="utf-8").write(xml)
    return len(urls)

# ---------------------------------------------------------------- main

def main():
    levels = load_levels(DATA_FILE)
    vocab_levels = load_levels(VOCAB_FILE)
    audio_idx = load_audio_index()

    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)          # full rebuild - output is derived, never hand-edited
    os.makedirs(OUT_DIR)

    slugs, hub, with_audio = [], [], 0
    for level in levels:
        items = []
        for topic in level.get("topics", []):
            if topic.get("kind") != "grammar":
                continue
            slug = slugify(topic["name"])
            if slug in slugs:
                raise SystemExit(f"slug collision: {slug}")
            slugs.append(slug)
            os.makedirs(f"{OUT_DIR}/{slug}")
            page = topic_page(level, topic, slug, audio_idx)
            open(f"{OUT_DIR}/{slug}/index.html", "w", encoding="utf-8").write(page)
            n_audio = page.count('class="say" data-audio')
            with_audio += n_audio
            items.append((topic["name"], topic.get("desc", ""), slug, topic.get("emoji", "")))
            print(f"  + /grammar/{slug}/  ({len(topic.get('teach',[]))} sections, {n_audio} audio examples)")
        if items:
            hub.append((level.get("level", ""), items))


    # ---- vocabulary pages (slang / idioms / proverbs) ----
    if os.path.isdir("vocabulary"):
        shutil.rmtree("vocabulary")
    os.makedirs("vocabulary")
    vslugs, vitems = [], []
    for level in vocab_levels:
        for topic in level.get("topics", []):
            cfg = VOCAB_PAGES.get(topic.get("name"))
            if not cfg:
                continue                        # unlisted topics (incl. mature) are never built
            if topic.get("mature"):
                raise SystemExit(f"refusing to build page for mature topic: {topic['name']}")
            slug, page_title = cfg
            os.makedirs(f"vocabulary/{slug}")
            page = vocab_page(topic, slug, page_title, audio_idx)
            open(f"vocabulary/{slug}/index.html", "w", encoding="utf-8").write(page)
            n_audio = page.count('class="say" data-audio')
            with_audio += n_audio
            vslugs.append(slug)
            vitems.append((page_title, topic.get("desc", ""), slug, topic.get("emoji", ""),
                           len(topic.get("cards", []))))
            print(f"  + /vocabulary/{slug}/  ({len(topic.get('cards',[]))} expressions, {n_audio} audio clips)")
    # merged hub + redirect stubs for the old hub URLs
    if os.path.isdir("guide"):
        shutil.rmtree("guide")
    os.makedirs("guide")
    open("guide/index.html", "w", encoding="utf-8").write(guide_page(hub, vitems))
    os.makedirs("guide/listening")
    open("guide/listening/index.html", "w", encoding="utf-8").write(listening_page())
    print("  + /guide/listening/  (recommendations)")
    open(f"{OUT_DIR}/index.html", "w", encoding="utf-8").write(redirect_stub("/guide/"))
    open("vocabulary/index.html", "w", encoding="utf-8").write(redirect_stub("/guide/"))

    n = write_sitemap(slugs, vslugs)
    print(f"\nDone. {len(slugs)} grammar pages + {len(vslugs)} vocabulary pages + /guide/ hub. "
          f"sitemap.xml now lists {n} URLs. {with_audio} sentences/words carry pronunciation audio.")


if __name__ == "__main__":
    main()
