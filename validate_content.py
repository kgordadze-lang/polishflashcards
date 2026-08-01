#!/usr/bin/env python3
"""
Po polsku - validate_content.py

Deterministic content-integrity validator for lesson data.  It preserves the
existing ID, migration, relation, sense-group, usage, and audio checks and adds
the Priority 5 forward safeguards: exact wording/policy/structure snapshots,
card-policy and CEFR validation, duplicate/prompt gates, activity inventories,
conversation graph termination, and read-only audio planning.

Normal validation is read-only:
    python3 validate_content.py
    python3 validate_content.py --report-json -

The forward baseline can only be created or updated through the explicit guarded
modes documented in the Priority 5 implementation brief.
"""
import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter

import json5  # noqa: F401  (used transitively by load_levels)
import pp_audio_rule
from pp_audio_rule import load_levels, fix_surrogates

DATA_GLOB = "data-*.js"
ID_RE = re.compile(r"^[a-z0-9-]+$")
REVIEW_TICKET_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]+-\d+$")
REVIEW_REFERENCE_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:[/#:][A-Za-z0-9][A-Za-z0-9._-]*)+$")
FORWARD_BASELINE_PATH = os.path.join(
    "reports", "priority-5-forward-frozen-baseline.json")
FORWARD_BASELINE_KIND = "forward-looking"
FORWARD_BASELINE_FORMAT = 2
FORWARD_BASELINE_ORIGIN = "d703f4041ec67cb43a2eb85553ca077f780456a2"
FORWARD_BASELINE_APP_VERSION = "7.30"
FORWARD_BASELINE_LIMITATIONS = [
    "This is a forward-looking baseline beginning at application 7.30.",
    "It does not reconstruct the missing Priority 0 snapshot.",
    "It proves nothing about wording changes before application 7.30.",
    "It protects the reviewed application 7.30 state from this point forward.",
]
# Phase-4E authored sense groups. A key names ONE narrow shared answer sense, so it
# is held to the same lowercase-kebab shape as an id: no leading/trailing/doubled
# hyphen, no whitespace, nothing a copy-paste could smuggle in. The runtime
# (pp-distractor.js) is deliberately forgiving about all of this so a learner's
# round never breaks; that is exactly why the strictness has to live HERE, where a
# malformed group can still be fixed instead of silently doing nothing.
SENSE_GROUP_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_RELATION = {"synonym", "contrast", "gender-variant", "number-variant", "aspect-pair", "register-variant"}
# Phase-4 usage metadata. Absent means the schema default (neutral / general / active).
ALLOWED_REGISTER = {"formal", "neutral", "informal", "slang", "vulgar"}
ALLOWED_REGION = {"general", "warsaw", "regional"}
ALLOWED_PRODUCTION = {"active", "recognition-only"}
# Cards that legitimately keep a "/" in pl (display only, never assessed) - each with a reason.
SLASH_ALLOWLIST = {
    "a1-family-people-015": "template display pattern (mój/moja); cardType:template, excluded from Type It",
}
# Cards with "..." in pl that are intentionally NOT exact-answer templates.
ELLIPSIS_ALLOWLIST = {
    "podcasts-meaning-of-life-002": "podcast lexical pattern; podcast phrase cards are not in Type It/Listening",
}

errors = []
warnings = []
def err(msg): errors.append(msg)
def warn(msg): warnings.append(msg)


def topic_kind(t):
    if "scenes" in t: return "convo"
    if t.get("kind") == "podcast": return "podcast"
    if "drills" in t or t.get("kind") == "grammar": return "grammar"
    if "cards" in t: return "vocab"
    declared = t.get("kind")
    return declared if _nonempty_string(declared) else "unknown"


def build_token_key(token):
    """Grammar build-tile identity: only sentence-position case may differ."""
    if not isinstance(token, str) or not token:
        return token
    return token[0].lower() + token[1:]


def check_accepted_orders(drill, drill_ref):
    """Validate optional Grammar build acceptedOrders; return (drills, orders)."""
    if "acceptedOrders" not in drill:
        return (0, 0)
    if drill.get("type") != "build":
        err(f"[acceptedOrders] only allowed on build drills: {drill_ref}")
        return (0, 0)

    accepted = drill["acceptedOrders"]
    if not isinstance(accepted, list):
        err(f"[acceptedOrders] must be a non-empty list: {drill_ref}")
        return (1, 0)
    if not accepted:
        err(f"[acceptedOrders] must not be empty: {drill_ref}")
        return (1, 0)

    toks = drill.get("answer", [])
    answer_keys = (
        [build_token_key(token) for token in toks]
        if isinstance(toks, list) else None
    )
    seen_orders = set()
    for order_idx, order in enumerate(accepted):
        order_ref = f"{drill_ref}/acceptedOrders[{order_idx}]"
        if not isinstance(order, list):
            err(f"[acceptedOrders] order must be a non-empty list: {order_ref}")
            continue
        if not order:
            err(f"[acceptedOrders] order must not be empty: {order_ref}")
            continue
        if not all(isinstance(token, str) and token.strip() for token in order):
            err(f"[acceptedOrders] every token must be a non-empty string: {order_ref}")
            continue
        if not isinstance(toks, list):
            err(f"[acceptedOrders] build answer must be a list: {drill_ref}")
            continue
        order_keys = [build_token_key(token) for token in order]
        if len(order) != len(toks):
            err(f"[acceptedOrders] token count must match answer: {order_ref}")
        elif Counter(order_keys) != Counter(answer_keys):
            err(f"[acceptedOrders] keyed token multiset must match answer: {order_ref}")
        if order_keys == answer_keys:
            err(f"[acceptedOrders] must change tile order, not capitalization "
                f"alone: {order_ref}")
        order_key = tuple(order_keys)
        if order_key in seen_orders:
            err(f"[acceptedOrders] duplicate accepted order: {order_ref}")
        else:
            seen_orders.add(order_key)
    return (1, len(accepted))


def load_all_levels():
    levels = []
    for path in sorted(glob.glob(DATA_GLOB)):
        levels.extend(load_levels(path))
    return levels


def _balanced(src, open_idx, open_ch, close_ch):
    """Return the substring of a string/comment-aware balanced [..] or {..} region."""
    depth, in_str, esc, k = 0, None, False, open_idx
    while k < len(src):
        ch = src[k]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == in_str: in_str = None
        else:
            if ch in "\"'": in_str = ch
            elif ch == open_ch: depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return src[open_idx:k + 1]
        k += 1
    return src[open_idx:]


def check_migration_config():
    """Validate pp-migrate.js revision wiring: target matches a unique, contiguous
    2..target handler set (Phase 2's target 1 + empty REVISIONS is valid). Also confirm
    the recovery/migration keys exist. Returns (target, revs) for the report."""
    if not os.path.exists("pp-migrate.js"):
        warn("[migration] pp-migrate.js not found - skipping revision-config checks")
        return (None, [])
    src = open("pp-migrate.js", encoding="utf-8").read()
    mt = re.search(r"CONTENT_MIGRATION_REVISION\s*=\s*(\d+)", src)
    if not mt:
        err("[migration] CONTENT_MIGRATION_REVISION not found in pp-migrate.js")
        return (None, [])
    target = int(mt.group(1))
    mr = re.search(r"REVISIONS\s*=\s*\[", src)
    if not mr:
        err("[migration] REVISIONS array not found in pp-migrate.js")
        return (target, [])
    arr = _balanced(src, mr.end() - 1, "[", "]")
    revs = [int(x) for x in re.findall(r"\brev\s*:\s*(\d+)", arr)]

    if len(revs) != len(set(revs)):
        err(f"[migration] duplicate revision numbers in REVISIONS: {sorted(revs)}")
    if target < 1:
        err(f"[migration] CONTENT_MIGRATION_REVISION must be >= 1 (got {target})")
    elif target == 1:
        if revs:
            err(f"[migration] target revision 1 requires an empty REVISIONS list, found {sorted(set(revs))}")
    else:
        expected = list(range(2, target + 1))
        if sorted(set(revs)) != expected:
            err(f"[migration] REVISIONS {sorted(set(revs))} must be unique & contiguous 2..{target} "
                f"(expected {expected}) to match CONTENT_MIGRATION_REVISION")
    for tok in ("v2recovery", "popolsku-progress-v2-recovery", "v1backup", "popolsku-progress-v2-unmapped"):
        if tok not in src:
            err(f"[migration] expected recovery/migration token missing from pp-migrate.js: {tok!r}")
    return (target, sorted(set(revs)))


def load_legacy():
    """Parse PP_MIGRATE.LEGACY out of pp-migrate.js. Returns {} when unavailable."""
    if not os.path.exists("pp-migrate.js"):
        return {}
    src = open("pp-migrate.js", encoding="utf-8").read()
    m = re.search(r"LEGACY\s*[:=]\s*(\{)", src)
    if not m:
        return {}
    try:
        return fix_surrogates(json5.loads(_balanced(src, m.end(1) - 1, "{", "}")))
    except Exception:
        return {}


def check_usage_labels(levels):
    """Phase 5: every metadata value the data uses must map to an approved
    learner-facing label, and the label vocabulary itself must stay correct.

    The labels live in pp-usage.js, which is also what index.html renders with and
    what tests/test_activities.js exercises - so this check ties the DATA to the
    single source of truth rather than to a copy. Returns a per-label tally."""
    path = "pp-usage.js"
    if not os.path.exists(path):
        err("[usage] pp-usage.js not found - Phase-5 labels and eligibility rules are missing")
        return {}
    src = open(path, encoding="utf-8").read()

    def parse_map(name):
        m = re.search(re.escape(name) + r"\s*=\s*(\{)", src)
        if not m:
            err(f"[usage] PP_USAGE.{name} not found in pp-usage.js")
            return {}
        try:
            return json5.loads(_balanced(src, m.end(1) - 1, "{", "}"))
        except Exception as e:
            err(f"[usage] could not parse PP_USAGE.{name}: {e}")
            return {}

    reg_lbl = parse_map("PP_USAGE.REGISTER_LABEL")
    rgn_lbl = parse_map("PP_USAGE.REGION_LABEL")
    m = re.search(r"PP_USAGE\.RECOGNITION_LABEL\s*=\s*\"([^\"]*)\"", src)
    rec_lbl = m.group(1) if m else None
    if not rec_lbl:
        err("[usage] PP_USAGE.RECOGNITION_LABEL not found in pp-usage.js")

    APPROVED = {"Formal", "Informal", "Slang", "Vulgar", "Warsaw-associated", "Regional", "Recognition only"}
    for src_name, mp in (("REGISTER_LABEL", reg_lbl), ("REGION_LABEL", rgn_lbl)):
        for k, v in mp.items():
            if v not in APPROVED:
                err(f"[usage] {src_name}[{k!r}] = {v!r} is not an approved learner-facing label "
                    f"(approved: {sorted(APPROVED)})")
    if rec_lbl and rec_lbl not in APPROVED:
        err(f"[usage] RECOGNITION_LABEL {rec_lbl!r} is not an approved learner-facing label")

    # the wording decision from the Phase-4 review, pinned so it cannot regress
    if rgn_lbl.get("warsaw") != "Warsaw-associated":
        err(f"[usage] region 'warsaw' must render as 'Warsaw-associated', got "
            f"{rgn_lbl.get('warsaw')!r}. It means ESPECIALLY associated with Warsaw, not exclusive.")
    for k, v in rgn_lbl.items():
        low = v.lower()
        if "only" in low or "specific" in low:
            err(f"[usage] region label {v!r} implies exclusivity - forbidden wording for `region`")
    # defaults must stay unlabelled, so ordinary cards render no chips
    if "neutral" in reg_lbl:
        err("[usage] register 'neutral' is a default and must have no label")
    if "general" in rgn_lbl:
        err("[usage] region 'general' is a default and must have no label")

    # index.html must actually consume the shared module (guards app/test drift)
    if os.path.exists("index.html"):
        idx = open("index.html", encoding="utf-8").read()
        if 'src="pp-usage.js"' not in idx:
            err("[usage] index.html does not load pp-usage.js")
        for fn in ("PP_USAGE.eligibleFor", "PP_USAGE.labels"):
            if fn not in idx:
                err(f"[usage] index.html does not use {fn} - the app may have drifted from the tested rules")
        if 'poolFor(T.topicRef.src, "typeit")' not in idx:
            err("[usage] Type It does not request the production-safe pool "
                "(expected poolFor(..., \"typeit\"))")
        if 'poolFor(L.topicRef.src, "listen")' not in idx:
            err("[usage] Listening does not request the recognition pool "
                "(expected poolFor(..., \"listen\"))")
        # --- Phase-5 correction pass: the three gaps found in review ---
        # 1. every answer panel renders usage metadata, not just the typed ones.
        #    4 call sites: Type It verdict, Listening feedback, mixed typed verdict, mixed MC/listen.
        live = re.sub(r"^\s*//.*$", "", idx, flags=re.M)          # ignore commented-out calls
        n_append = len(re.findall(r"\bppAppendUsageTo\s*\(", live)) - live.count("function ppAppendUsageTo(")
        if n_append < 4:
            err(f"[usage] ppAppendUsageTo is wired into only {n_append} answer panel(s); all 4 "
                f"(Type It, Listening, mixed typed, mixed multiple-choice/listen) must render usage metadata")
        # 2. the strength duplicate is suppressed ONLY on the face that shows the badge
        if "suppressStrengthDuplicate: true" not in idx:
            err("[usage] the flashcard front no longer opts into strength de-duplication")
        if idx.count("suppressStrengthDuplicate") > 1:
            err("[usage] strength de-duplication is requested on more than one surface - only the "
                "flashcard FRONT shows a strength badge, so only it may suppress the register chip")
        if 'ppFillUsageRow($("usageBack"), card)' not in idx:
            err("[usage] the flashcard back must render the COMPLETE label set (no options), so a "
                "'Vulgar' register chip is not hidden from a surface with no strength badge")
        # 3. only the active face exposes its usage summary to assistive tech
        # the eligibility contract must name every activity the report documents,
        # and must fail closed on anything else
        up = open("pp-usage.js", encoding="utf-8").read()
        m = re.search(r"PP_USAGE\.eligibleFor\s*=\s*function[\s\S]*?\n  \};", up)
        body = m.group(0) if m else ""
        if not body:
            err("[usage] could not read PP_USAGE.eligibleFor to check the activity contract")
        else:
            for act in ("flashcard", "search", "listen", "typeit", "mixed"):
                if '"' + act + '"' not in body:
                    err(f"[usage] PP_USAGE.eligibleFor does not handle the {act!r} activity explicitly - "
                        f"the documented contract lists it")
            if not re.search(r"return false;\s*\n  \};\s*$", body):
                err("[usage] PP_USAGE.eligibleFor must end with `return false;` so an unknown activity "
                    "fails closed instead of inheriting the production rule")
        if "function ppSyncFaceA11y(" not in idx:
            err("[usage] ppSyncFaceA11y() is missing - both card faces would expose a usage summary")
        elif len(re.findall(r"\bppSyncFaceA11y\s*\(\s*\)", idx)) < 2:
            err("[usage] ppSyncFaceA11y() is defined but not called on render/flip")

    # per-value tally over the real data + recognition-only invariants
    tally = Counter()
    for L in levels:
        for t in L.get("topics", []):
            for c in t.get("cards", []) or []:
                if c.get("register"): tally["register:" + c["register"]] += 1
                if c.get("region"): tally["region:" + c["region"]] += 1
                if c.get("production"): tally["production:" + c["production"]] += 1
                if c.get("warning"): tally["warning"] += 1
                if c.get("production") == "recognition-only":
                    # it must still be a real, displayable flashcard - never hidden away
                    if c.get("intro") or not c.get("pl") or not c.get("en"):
                        err(f"[usage] recognition-only card is not a usable flashcard: {c.get('id')}")
                    if c.get("cardType") == "template":
                        err(f"[usage] recognition-only must not be combined with cardType:template: "
                            f"{c.get('id')} - templates are already excluded from every activity")
    return tally


def check_main_audio(levels):
    """Phase-6 correction: an incomplete template `pl` must never be main-card audio.

    Three things have to stay true at once, and this checks all three rather than
    trusting any one of them:
      1. the DATA is shaped so the rule can be applied (audioText only on templates,
         and complete when present);
      2. the two implementations of the rule AGREE - pp_audio_rule.py (what gets
         generated and verified) and pp-usage.js (what the app plays);
      3. index.html actually routes its speakers through the rule, and no longer
         reaches for `currentCard().pl` directly.

    Drift in any one of them puts an unfinished phrase back in the learner's ear,
    which is the exact defect this correction exists to remove. Returns a tally."""
    tally = Counter()

    # --- 1. data shape -----------------------------------------------------
    for L in levels:
        for t in L.get("topics", []):
            for c in t.get("cards", []) or []:
                cid = c.get("id")
                is_tmpl = c.get("cardType") == "template"
                at = c.get("audioText")
                if is_tmpl:
                    tally["template"] += 1
                if at is not None:
                    if not is_tmpl:
                        err(f"[audio] audioText is only meaningful on cardType:template: {cid} - "
                            f"a standard card already speaks its pl")
                    if not isinstance(at, str) or not at.strip():
                        err(f"[audio] audioText must be a non-empty string when present: {cid}")
                    elif not pp_audio_rule.is_complete_utterance(at):
                        err(f"[audio] audioText must be a complete utterance, not another pattern: "
                            f"{cid} {at!r} - a template with no complete audioText correctly gets "
                            f"NO main-card audio, which is better than speaking an unfinished one")
                    elif is_tmpl:
                        tally["template-with-audioText"] += 1
                if is_tmpl and not pp_audio_rule.main_audio_text(c):
                    tally["template-silent"] += 1
                # the template still has to work as a flashcard - silence is only about audio
                if is_tmpl and not (c.get("pl") and c.get("en")):
                    err(f"[audio] template card is not displayable: {cid}")

    # --- 2. the two implementations of the rule agree ----------------------
    path = "pp-usage.js"
    if not os.path.exists(path):
        err("[audio] pp-usage.js not found - the app has no main-audio rule to follow")
    else:
        up = open(path, encoding="utf-8").read()
        for fn in ("PP_USAGE.mainAudioText", "PP_USAGE.isCompleteUtterance", "PP_USAGE.hasMainAudio"):
            if fn + " =" not in up:
                err(f"[audio] {fn} is missing from pp-usage.js")
        m = re.search(r"PP_USAGE\.INCOMPLETE_MARK\s*=\s*/(.+?)/;", up)
        if not m:
            err("[audio] PP_USAGE.INCOMPLETE_MARK not found in pp-usage.js")
        elif m.group(1) != pp_audio_rule.INCOMPLETE_MARK.pattern:
            err(f"[audio] the JS and Python completeness rules have drifted: "
                f"pp-usage.js /{m.group(1)}/ vs pp_audio_rule.py "
                f"/{pp_audio_rule.INCOMPLETE_MARK.pattern}/ - the app would play a string the "
                f"generator never built, or refuse one it did")
        mb = re.search(r"PP_USAGE\.mainAudioText\s*=\s*function[\s\S]*?\n  \};", up)
        body = mb.group(0) if mb else ""
        if body and 'cardType === "template"' not in body:
            err("[audio] PP_USAGE.mainAudioText no longer branches on cardType:template")

    # --- 3. the app is wired to the rule -----------------------------------
    if os.path.exists("index.html"):
        idx = open("index.html", encoding="utf-8").read()
        live = re.sub(r"^\s*//.*$", "", idx, flags=re.M)
        if "function speakCardMain(" not in live:
            err("[audio] speakCardMain() is missing from index.html - main-card audio has no single "
                "entry point applying the rule")
        if "ppHasMainAudio(c)" not in live:
            err("[audio] render() does not gate the main speaker on ppHasMainAudio - a template "
                "would show a speaker with nothing to play")
        for bad in ('speakText(currentCard().pl', 'speakText(L.qs[L.i].c.pl', 'speakText(R.qs[R.i].c.pl'):
            if bad in live:
                err(f"[audio] index.html still speaks a raw `pl` ({bad}...) - route it through "
                    f"speakCardMain so template patterns cannot be spoken")
        # the fallback path is the subtle one: deleting the clips is not enough if a
        # missing clip silently hands the text to speechSynthesis instead.
        mfn = re.search(r"function speakCardMain\([\s\S]*?\n\}", live)
        if mfn and "ppHasMainAudio" not in mfn.group(0):
            err("[audio] speakCardMain does not check ppHasMainAudio before speaking - a template "
                "would fall through to the speechSynthesis fallback")

    # --- 4. and finally: no obsolete clip is still reachable ---------------
    if os.path.exists("audio-manifest.json"):
        entries = json.load(open("audio-manifest.json", encoding="utf-8")).get("entries", {})
        required = {pp_audio_rule.normalize(p) for p in pp_audio_rule.required_phrases(DATA_GLOB)}
        for L in levels:
            for t in L.get("topics", []):
                for c in t.get("cards", []) or []:
                    if c.get("cardType") != "template":
                        continue
                    pl = pp_audio_rule.normalize(c.get("pl") or "")
                    if not pl or pl in required:
                        continue
                    h = hashlib.sha256(pl.encode("utf-8")).hexdigest()[:12]
                    if h in entries:
                        err(f"[audio] obsolete template clip still in the manifest: {c.get('id')} "
                            f"{pl!r} -> {entries[h].get('file')}")
        tally["required-phrases"] = len(required)
        tally["manifest-entries"] = len(entries)
    return tally


def check_id(kind, obj, where, seen):
    i = obj.get("id")
    if i is None:
        err(f"[id] {kind} missing id: {where}")
        return None
    if not isinstance(i, str) or not ID_RE.match(i):
        err(f"[id] {kind} id not lowercase-ascii [a-z0-9-]: {i!r} ({where})")
    if i in seen:
        err(f"[id] duplicate id {i!r}: {where}  AND  {seen[i]}")
    else:
        seen[i] = where
    return i


def run_existing_checks(levels=None, emit=False):
    """Run the pre-Phase-1B checks without exiting the interpreter."""
    global errors, warnings
    errors, warnings = [], []
    levels = load_all_levels() if levels is None else levels

    all_ids = {}          # id -> where (global uniqueness)
    card_ids = set()
    topic_ids = set()
    rel_map = {}          # card id -> set(relatedIds)  (for reciprocity)
    sense_groups = {}     # sense-group key -> set(card ids)  (Phase 4E)

    # informational tallies
    slash_pl, ellipsis_pl, paren_pl, templates, recognition = [], [], [], [], []

    n_lvl = n_top = n_card = n_drill = 0
    accepted_build_drills = accepted_build_orders = 0

    for L in levels:
        n_lvl += 1
        lname = L.get("level")
        check_id("level", L, f"level {lname!r}", all_ids)
        for t in L.get("topics", []):
            n_top += 1
            tname = t.get("name")
            tid = check_id("topic", t, f"topic {lname}/{tname!r}", all_ids)
            if tid:
                topic_ids.add(tid)
            k = topic_kind(t)

            # cards
            if "cards" in t:
                pls, ens = [], []
                for idx, c in enumerate(t["cards"]):
                    n_card += 1
                    cid = check_id("card", c, f"card {tname}/#{idx} pl={c.get('pl')!r}", all_ids)
                    if cid:
                        card_ids.add(cid)
                    is_tmpl = c.get("cardType") == "template"
                    if not c.get("intro"):
                        pl, en = c.get("pl"), c.get("en")
                        if pl is None: err(f"[field] card missing pl: {tname}/#{idx}")
                        else:
                            pls.append(pl)
                            if "/" in pl:
                                slash_pl.append((tid, pl))
                                if not is_tmpl and cid not in SLASH_ALLOWLIST:
                                    err(f"[slash] unreviewed '/' in assessable pl: {cid} {pl!r} "
                                        f"(split it, use acceptedAnswers, or allowlist with a reason)")
                            if "..." in pl or "…" in pl:
                                ellipsis_pl.append((tid, pl))
                                if not is_tmpl and cid not in ELLIPSIS_ALLOWLIST:
                                    err(f"[template] '...' in pl but not classified as a template: {cid} {pl!r}")
                            if "(" in pl or ")" in pl: paren_pl.append((tid, pl))
                        if en is None: err(f"[field] card missing en: {tname}/{pl!r}")
                        else: ens.append(en)
                    if is_tmpl: templates.append((tid, c.get("pl")))
                    if c.get("production") == "recognition-only": recognition.append((tid, c.get("pl")))
                    # optional-metadata structure checks (defensive: only when present)
                    aa = c.get("acceptedAnswers")
                    if aa is not None:
                        if not isinstance(aa, list) or not aa:
                            err(f"[acceptedAnswers] must be a non-empty array: {cid}")
                        else:
                            if any((not isinstance(x, str) or not x.strip()) for x in aa):
                                err(f"[acceptedAnswers] must be non-empty strings: {cid}")
                            if len(set(aa)) != len(aa):
                                err(f"[acceptedAnswers] contains duplicates: {cid} {aa}")
                            if c.get("pl") in aa:
                                err(f"[acceptedAnswers] duplicates canonical pl: {cid} {c.get('pl')!r}")
                    # Phase-4E: "these answer choices must not appear together".
                    # It says nothing else - not that the Polish is interchangeable,
                    # not that Type It should accept either answer, not that the two
                    # cards are duplicates or should merge.
                    sg = c.get("senseGroups")
                    if sg is not None:
                        if not isinstance(sg, list) or not sg:
                            err(f"[senseGroups] must be a non-empty array when present: {cid}")
                        else:
                            # ONE pass, and duplicate tracking that only ever sees
                            # confirmed string keys. Hashing the raw array instead -
                            # `set(sg)` - raises TypeError on an unhashable entry such
                            # as {} or [], which killed the run with a traceback before
                            # the "entries must be strings" error it had already
                            # recorded could be printed. A validator must report bad
                            # data, not crash on it, so every entry is rejected on its
                            # own terms first and only a fully valid key reaches the
                            # seen-set or the group membership map.
                            seen_keys = set()
                            for g in sg:
                                if not isinstance(g, str):
                                    err(f"[senseGroups] entries must be strings: {cid} {g!r}")
                                elif not g.strip():
                                    err(f"[senseGroups] entries must not be blank: {cid}")
                                elif g != g.strip():
                                    err(f"[senseGroups] entry has surrounding whitespace: {cid} {g!r}")
                                elif not SENSE_GROUP_RE.match(g):
                                    err(f"[senseGroups] key is not lowercase kebab-case: {cid} {g!r}")
                                elif g in seen_keys:
                                    err(f"[senseGroups] contains duplicate keys: {cid} {sg}")
                                else:
                                    seen_keys.add(g)
                                    sense_groups.setdefault(g, set()).add(cid)
                    va = c.get("variants")
                    if va is not None:
                        if not isinstance(va, list) or not all(
                                isinstance(x, dict) and isinstance(x.get("form"), str) and x.get("form")
                                and isinstance(x.get("label"), str) and x.get("label") for x in va):
                            err(f"[variants] must be a list of {{form,label}} with non-empty strings: {cid}")
                    rt = c.get("relationType")
                    if rt is not None and rt not in ALLOWED_RELATION:
                        err(f"[relationType] not an allowed value: {cid} {rt!r}")
                    # Phase-4 usage metadata: closed vocabularies, and a recognition-only
                    # card must say WHY (a warning, or a usage note in the hint).
                    for fld, allowed in (("register", ALLOWED_REGISTER),
                                         ("region", ALLOWED_REGION),
                                         ("production", ALLOWED_PRODUCTION)):
                        v = c.get(fld)
                        if v is not None and v not in allowed:
                            err(f"[{fld}] not an allowed value: {cid} {v!r} (allowed: {sorted(allowed)})")
                    w = c.get("warning")
                    if w is not None and (not isinstance(w, str) or not w.strip()):
                        err(f"[warning] must be a non-empty string when present: {cid}")
                    if c.get("production") == "recognition-only" and not (
                            (c.get("warning") or "").strip() or len((c.get("hint") or "")) > 40):
                        err(f"[production] recognition-only card needs a warning or a clear usage "
                            f"note in its hint: {cid}")
                    if cid:
                        rel_map[cid] = set(c.get("relatedIds") or [])
                for pl, n in Counter(pls).items():
                    if n > 1: err(f"[dup] duplicate pl within topic {tid}: {pl!r} x{n}")
                for en, n in Counter(ens).items():
                    if n > 1: err(f"[dup] duplicate en within topic {tid}: {en!r} x{n}")

            # drills
            if "drills" in t:
                for idx, d in enumerate(t["drills"]):
                    n_drill += 1
                    did = check_id("drill", d, f"drill {tname}/#{idx} ({d.get('type')})", all_ids)
                    drill_ref = did or f"{tid}/#{idx}"
                    dtype = d.get("type")
                    accepted_drills, accepted_orders = check_accepted_orders(d, drill_ref)
                    accepted_build_drills += accepted_drills
                    accepted_build_orders += accepted_orders
                    if dtype == "choose":
                        opts, ans = d.get("options", []), d.get("answer")
                        if ans not in opts:
                            err(f"[drill] choose answer {ans!r} not in options {opts} ({tid}/#{idx})")
                    elif dtype == "build":
                        toks = d.get("answer", [])
                        if isinstance(toks, list):
                            dups = [w for w, n in Counter(toks).items() if n > 1]
                            if dups: err(f"[drill] build duplicated tokens {dups} ({tid}/#{idx})")

            # scenarios
            if "scenes" in t:
                scenes = t["scenes"]
                keys = set(scenes.keys())
                for sk, sc in scenes.items():
                    for o in sc.get("options", []):
                        g = o.get("goto")
                        if g is not None and g not in keys:
                            err(f"[scenario] broken goto {g!r} from {tid}/{sk}")
                start = t.get("start")
                reach = set()
                if start in scenes:
                    stack = [start]
                    while stack:
                        cur = stack.pop()
                        if cur in reach: continue
                        reach.add(cur)
                        for o in scenes.get(cur, {}).get("options", []):
                            g = o.get("goto")
                            if g in scenes and g not in reach: stack.append(g)
                for sk in keys:
                    if sk not in reach:
                        err(f"[scenario] unreachable scene {tid}/{sk}")

    # a sense group is a statement about a PAIR, so one member is never a group -
    # it is a typo in the second card's key, or an edit that removed the other side.
    for gkey, members in sorted(sense_groups.items()):
        if len(members) < 2:
            err(f"[senseGroups] group {gkey!r} has only {len(members)} member "
                f"({', '.join(sorted(members))}) - a group must name at least two distinct cards")

    # relatedIds resolve + reciprocity
    for cid, targets in rel_map.items():
        for rid in targets:
            if rid not in card_ids:
                err(f"[rel] relatedIds -> unknown card id {rid!r} (from {cid})")
            elif cid not in rel_map.get(rid, set()):
                err(f"[rel] non-reciprocal relatedIds: {cid} -> {rid} but {rid} does not link back")

    # legacy maps (pp-migrate.js), if present
    legacy_topics = legacy_cards = 0
    if os.path.exists("pp-migrate.js"):
        src = open("pp-migrate.js", encoding="utf-8").read()
        m = re.search(r"LEGACY\s*[:=]\s*(\{)", src)
        if m:
            # extract the balanced object literal, then json5-parse it
            start = m.end(1) - 1
            depth, in_str, esc, k = 0, None, False, start
            while k < len(src):
                ch = src[k]
                if in_str:
                    if esc: esc = False
                    elif ch == "\\": esc = True
                    elif ch == in_str: in_str = None
                else:
                    if ch in "\"'": in_str = ch
                    elif ch == "{": depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            k += 1; break
                k += 1
            try:
                legacy = fix_surrogates(json5.loads(src[start:k]))
            except Exception as e:
                legacy = None
                warn(f"[legacy] could not parse PP_MIGRATE.LEGACY: {e}")
            split_legacy = {}   # primary id -> [sibling ids]  (from LEGACY multi-id mappings)
            if legacy:
                for old_key, tid in (legacy.get("topics") or {}).items():
                    legacy_topics += 1
                    if tid not in topic_ids:
                        err(f"[legacy] topics[{old_key!r}] -> unknown topic id {tid!r}")
                for tid, mp in (legacy.get("cards") or {}).items():
                    if tid not in topic_ids:
                        err(f"[legacy] cards key is not a topic id: {tid!r}")
                    for old_pl, ids in (mp or {}).items():
                        legacy_cards += 1
                        ids = ids if isinstance(ids, list) else [ids]
                        for cid in ids:
                            if cid not in card_ids:
                                err(f"[legacy] cards[{tid}][{old_pl!r}] -> unknown card id {cid!r}")
                        if len(ids) > 1:            # a split: [primary, ...siblings]
                            split_legacy[ids[0]] = ids[1:]
                for tid, pls in (legacy.get("retired") or {}).items():
                    if tid not in topic_ids:
                        err(f"[legacy] retired key is not a topic id: {tid!r}")

            # every split must be handled by revision 2 (for existing v2 stores), and vice-versa
            ms = re.search(r"var\s+SPLITS\s*=\s*(\{)", src)
            splits_rev2 = {}
            if ms:
                try:
                    splits_rev2 = fix_surrogates(json5.loads(_balanced(src, ms.end(1) - 1, "{", "}")))
                except Exception as e:
                    err(f"[rev2] could not parse revision-2 SPLITS: {e}")
            elif split_legacy:
                err("[rev2] LEGACY declares splits but no revision-2 SPLITS map was found in pp-migrate.js")
            for primary, sibs in split_legacy.items():
                if splits_rev2.get(primary) != sibs:
                    err(f"[rev2] split {primary} -> {sibs} not matched in revision-2 SPLITS "
                        f"(found {splits_rev2.get(primary)})")
            for primary, sibs in splits_rev2.items():
                if primary not in card_ids:
                    err(f"[rev2] SPLITS primary is not a card id: {primary!r}")
                for s in sibs:
                    if s not in card_ids:
                        err(f"[rev2] SPLITS sibling is not a card id: {s!r}")
                if split_legacy.get(primary) != sibs:
                    err(f"[rev2] SPLITS {primary} -> {sibs} has no matching v1 legacy mapping")

    # migration revision config (pp-migrate.js)
    mig_target, mig_revs = check_migration_config()

    # Phase-5 usage labels + eligibility wiring
    usage_tally = check_usage_labels(levels)
    # Phase-6 correction: incomplete template pl is never main-card audio
    audio_tally = check_main_audio(levels)

    summary = {
        "levels": n_lvl,
        "topics": n_top,
        "cards": n_card,
        "drills": n_drill,
        "uniqueIds": len(all_ids),
        "topicIds": len(topic_ids),
        "cardIds": len(card_ids),
        "migrationRevision": mig_target,
        "migrationRevisions": mig_revs,
        "legacyTopicMappings": legacy_topics,
        "legacyCardMappings": legacy_cards,
        "acceptedBuildDrills": accepted_build_drills,
        "acceptedBuildOrders": accepted_build_orders,
        "senseGroups": len(sense_groups),
        "slashPolish": len(slash_pl),
        "ellipsisPolish": len(ellipsis_pl),
        "parenthesizedPolish": len(paren_pl),
        "templates": len(templates),
        "recognitionOnly": len(recognition),
        "usage": dict(sorted(usage_tally.items())),
        "audio": dict(sorted(audio_tally.items())),
    }
    result = {
        "errors": list(errors),
        "warnings": list(warnings),
        "summary": summary,
    }
    if emit:
        print("=" * 60)
        print("CONTENT VALIDATION")
        print("=" * 60)
        print(f"levels={n_lvl} topics={n_top} cards={n_card} drills={n_drill}")
        print(f"unique ids: {len(all_ids)}  "
              f"(topics={len(topic_ids)} cards={len(card_ids)})")
        if mig_target is not None:
            print("migration: CONTENT_MIGRATION_REVISION="
                  f"{mig_target}  REVISIONS={mig_revs or '[]'}")
        if os.path.exists("pp-migrate.js"):
            print(f"legacy maps: {legacy_topics} topic mapping(s), "
                  f"{legacy_cards} card mapping(s)")
        if usage_tally:
            print("usage metadata: " + "  ".join(
                f"{k}={v}" for k, v in sorted(usage_tally.items())))
        if audio_tally:
            print("main-card audio: " + "  ".join(
                f"{k}={v}" for k, v in sorted(audio_tally.items())))
        print(f"accepted build orders: {accepted_build_drills} drill(s), "
              f"{accepted_build_orders} order(s)")
        print(f"\ninfo: slash-pl={len(slash_pl)}  "
              f"ellipsis-pl={len(ellipsis_pl)}  paren-pl={len(paren_pl)}  "
              f"templates={len(templates)}  recognition-only={len(recognition)}")
    return result


# ============================================================================
# Priority 5 forward safeguards

POLICY_FIELDS = {
    "cardType", "register", "region", "production", "practice", "intro",
    "mature", "cefr", "strength",
}
STRUCTURAL_FIELDS = {
    "id", "kind", "group", "start", "goto", "end", "relatedIds",
    "relationType", "senseGroups", "type", "host", "link",
}
# Topic-level host/link remain structural presence facts. Card-level host/link
# are exact learner-facing podcast-intro metadata and must be wording-frozen.
CARD_STRUCTURAL_FIELDS = STRUCTURAL_FIELDS - {"host", "link"}
CARD_FIELDS = {
    "id", "pl", "en", "hint", "ex", "exEn", "pair", "relationType",
    "relatedIds", "senseGroups", "register", "acceptedAnswers", "strength",
    "cardType", "pattern", "variants", "practice", "typeItCue", "warning",
    "intro", "host", "link", "region", "production", "audioText",
}
INTRO_CARD_FIELDS = {"id", "intro", "pl", "en", "hint", "host", "link"}
ALLOWED_STRENGTH = {"mild", "medium", "strong", "vulgar"}
ALLOWED_CEFR = {"A1", "A2", "B1"}
ACTIVITY_NAMES = ("flashcard", "search", "typeit", "listen", "mixed")
CONTENT_SHAPE_CODES = {
    "SOURCE_CONTAINER_INVALID", "SOURCE_RECORD_INVALID",
    "SOURCE_ISSUES_INVALID", "SOURCE_LEVELS_INVALID",
    "LEVEL_RECORD_INVALID", "LEVEL_TOPICS_INVALID",
    "TOPIC_RECORD_INVALID", "TOPIC_KIND_INVALID",
    "TOPIC_CONTAINER_CONFLICT", "TOPIC_KIND_CONTAINER_MISMATCH",
    "TOPIC_CARDS_INVALID",
    "CARD_RECORD_INVALID", "CARD_FIELD_KEY_INVALID",
    "TOPIC_DRILLS_INVALID",
    "DRILL_RECORD_INVALID", "DRILL_FIELD_SHAPE",
    "GRAPH_SCENES_INVALID", "GRAPH_SCENE_KEY_INVALID",
    "GRAPH_SCENE_INVALID", "GRAPH_OPTIONS_INVALID",
    "GRAPH_OPTION_INVALID", "GRAPH_TERMINAL_INVALID",
}


def issue(code, message, path=None, severity="error"):
    """A stable, JSON-serialisable validation finding."""
    out = {"code": code, "message": message, "severity": severity}
    if path is not None:
        out["path"] = path
    return out


def issue_codes(issues):
    return {
        item["code"] for item in issues
        if isinstance(item, dict) and isinstance(item.get("code"), str)
    }


def is_meaningful_review_reference(value):
    """Accept a concrete ticket or namespaced review reference, never prose."""
    if not isinstance(value, str):
        return False
    value = value.strip()
    return bool(
        REVIEW_TICKET_RE.fullmatch(value) or
        REVIEW_REFERENCE_RE.fullmatch(value))


def canonical_json(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def _strict_object_key_issues(path):
    """Reparse push payloads with duplicate object keys forbidden.

    The normal JSON5 loader returns dictionaries, so a repeated scene key would
    otherwise be overwritten before graph validation could observe it.
    """
    with open(path, encoding="utf-8") as handle:
        source = handle.read()
    findings = []
    offset = 0
    push_index = 0
    while True:
        marker = source.find(".push(", offset)
        if marker < 0:
            break
        cursor = marker + len(".push(")
        start = cursor
        depth = 1
        quote = None
        escaped = False
        while cursor < len(source) and depth:
            character = source[cursor]
            if quote:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
            else:
                if character in "\"'":
                    quote = character
                elif character == "(":
                    depth += 1
                elif character == ")":
                    depth -= 1
            cursor += 1
        payload = source[start:cursor - 1].strip()
        try:
            json5.loads(
                "[" + payload + "]", allow_duplicate_keys=False)
        except ValueError as exc:
            findings.append(issue(
                "SOURCE_DUPLICATE_OBJECT_KEY",
                f"JSON5 object keys must be unique in push "
                f"{push_index}: {exc}", path))
        push_index += 1
        offset = cursor
    return findings


def load_source_corpus(data_glob=DATA_GLOB):
    sources = []
    for path in sorted(glob.glob(data_glob)):
        source_name = path.replace(os.sep, "/")
        findings = []
        levels = []
        try:
            levels = load_levels(path)
            findings.extend(_strict_object_key_issues(path))
        except (Exception, SystemExit) as exc:
            findings.append(issue(
                "SOURCE_PARSE_FAILED",
                f"Could not parse learner content: "
                f"{type(exc).__name__}: {exc}",
                source_name))
        sources.append({
            "source": source_name,
            "levels": levels,
            "sourceIssues": findings,
        })
    return sources


def corpus_from_levels(levels, source="data-fixture.js"):
    """Wrap in-memory fixture levels in the repository corpus shape."""
    return [{"source": source, "levels": levels}]


def corpus_levels(sources):
    if not isinstance(sources, list):
        return []
    levels = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        values = source.get("levels")
        if isinstance(values, list):
            levels.extend(level for level in values if isinstance(level, dict))
    return levels


def _presence(obj, key, effective=None):
    record = {"present": key in obj}
    if key in obj:
        record["value"] = obj[key]
    if effective is not None:
        record["effective"] = effective
    return record


def _record_strings(value, path, field, out):
    """Record exact strings without normalising or re-encoding their content."""
    if isinstance(value, str):
        out.append({"path": path, "field": field, "value": value})
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _record_strings(item, path, f"{field}[{index:03d}]", out)
    elif isinstance(value, dict):
        for key in sorted(value):
            child = f"{field}.{key}" if field else key
            _record_strings(value[key], path, child, out)


def _wording_for_object(obj, path, excluded, out):
    for key in sorted(obj):
        if key in excluded:
            continue
        _record_strings(obj[key], path, key, out)


def _source_snapshot(source_record):
    """Return the five forward-protected sections for one parsed source."""
    source = source_record["source"]
    stable_ids = []
    wording = []
    policy = []
    structure = []

    for level_index, level in enumerate(source_record.get("levels", [])):
        level_id = level.get("id")
        level_path = f"{source}#/level:{level_id}"
        stable_ids.append({
            "id": level_id,
            "kind": "level",
            "path": level_path,
            "source": source,
        })
        _wording_for_object(
            level, level_path, STRUCTURAL_FIELDS | POLICY_FIELDS | {"topics"},
            wording)
        topic_ids = [
            topic.get("id") for topic in level.get("topics", [])
        ]
        structure.append({
            "kind": "level",
            "path": level_path,
            "sourceIndex": level_index,
            "group": _presence(level, "group"),
            "topicOrder": topic_ids,
        })

        for topic_index, topic in enumerate(level.get("topics", [])):
            topic_id = topic.get("id")
            topic_path = f"{level_path}/topic:{topic_id}"
            kind = topic_kind(topic)
            stable_ids.append({
                "id": topic_id,
                "kind": "topic",
                "path": topic_path,
                "source": source,
            })
            _wording_for_object(
                topic, topic_path,
                STRUCTURAL_FIELDS | POLICY_FIELDS |
                {"cards", "drills", "scenes"},
                wording)
            policy.append({
                "kind": "topic",
                "path": topic_path,
                "cefr": _presence(topic, "cefr"),
                "mature": _presence(topic, "mature", bool(topic.get("mature"))),
            })
            topic_structure = {
                "kind": "topic",
                "path": topic_path,
                "sourceIndex": topic_index,
                "parentLevelId": level_id,
                "topicKind": kind,
                "declaredKind": _presence(topic, "kind"),
                "host": _presence(topic, "host"),
                "link": _presence(topic, "link"),
                "cardOrder": [
                    card.get("id") for card in topic.get("cards", [])
                ],
                "drillOrder": [
                    drill.get("id") for drill in topic.get("drills", [])
                ],
            }
            if "scenes" in topic:
                scenes = topic.get("scenes") or {}
                topic_structure["start"] = _presence(topic, "start")
                topic_structure["sceneOrder"] = list(scenes)
            structure.append(topic_structure)

            for card_index, card in enumerate(topic.get("cards", [])):
                card_id = card.get("id")
                card_path = f"{topic_path}/card:{card_id}"
                stable_ids.append({
                    "id": card_id,
                    "kind": "card",
                    "path": card_path,
                    "source": source,
                })
                _wording_for_object(
                    card, card_path,
                    CARD_STRUCTURAL_FIELDS | POLICY_FIELDS, wording)
                policy.append({
                    "kind": "card",
                    "path": card_path,
                    "cardType": _presence(
                        card, "cardType", card.get("cardType", "standard")),
                    "register": _presence(
                        card, "register", card.get("register", "neutral")),
                    "region": _presence(
                        card, "region", card.get("region", "general")),
                    "production": _presence(
                        card, "production",
                        card.get("production", "active")),
                    "practice": _presence(card, "practice"),
                    "intro": _presence(
                        card, "intro", bool(card.get("intro"))),
                    "strength": _presence(card, "strength"),
                    "warningPlacement": {"present": "warning" in card},
                })
                structure.append({
                    "kind": "card",
                    "path": card_path,
                    "sourceIndex": card_index,
                    "parentTopicId": topic_id,
                    "relationType": _presence(card, "relationType"),
                    "relatedIds": _presence(card, "relatedIds"),
                    "senseGroups": _presence(card, "senseGroups"),
                    "acceptedAnswerCount": (
                        len(card.get("acceptedAnswers", []))
                        if isinstance(card.get("acceptedAnswers", []), list)
                        else None),
                    "variantCount": (
                        len(card.get("variants", []))
                        if isinstance(card.get("variants", []), list)
                        else None),
                })

            for drill_index, drill in enumerate(topic.get("drills", [])):
                drill_id = drill.get("id")
                drill_path = f"{topic_path}/drill:{drill_id}"
                stable_ids.append({
                    "id": drill_id,
                    "kind": "drill",
                    "path": drill_path,
                    "source": source,
                })
                _wording_for_object(
                    drill, drill_path, STRUCTURAL_FIELDS | POLICY_FIELDS,
                    wording)
                structure.append({
                    "kind": "drill",
                    "path": drill_path,
                    "sourceIndex": drill_index,
                    "parentTopicId": topic_id,
                    "drillType": _presence(drill, "type"),
                    "acceptedOrderCount": (
                        len(drill.get("acceptedOrders", []))
                        if isinstance(drill.get("acceptedOrders", []), list)
                        else None),
                })

            for scene_index, (scene_key, scene) in enumerate(
                    (topic.get("scenes") or {}).items()):
                scene_path = f"{topic_path}/scene:{scene_key}"
                _wording_for_object(
                    scene, scene_path, STRUCTURAL_FIELDS | POLICY_FIELDS,
                    wording)
                structure.append({
                    "kind": "scene",
                    "path": scene_path,
                    "sourceIndex": scene_index,
                    "parentTopicId": topic_id,
                    "sceneKey": scene_key,
                    "terminal": _presence(
                        scene, "end", bool(scene.get("end"))),
                    "optionRoutes": [
                        {
                            "index": index,
                            "goto": _presence(option, "goto"),
                        }
                        for index, option in enumerate(
                            scene.get("options", []))
                    ],
                })

    stable_ids.sort(key=lambda row: (
        str(row.get("id")), row["kind"], row["path"]))
    wording.sort(key=lambda row: (
        row["path"], row["field"], row["value"]))
    policy.sort(key=lambda row: (row["path"], row["kind"]))
    structure.sort(key=lambda row: (row["path"], row["kind"]))
    return stable_ids, wording, policy, structure


def read_repo_metadata():
    app_version = None
    schema_version = None
    migration_revision = None
    if os.path.exists("index.html"):
        source = open("index.html", encoding="utf-8").read()
        match = re.search(r'APP_VERSION\s*=\s*"([^"]+)"', source)
        if match:
            app_version = match.group(1)
    if os.path.exists("pp-migrate.js"):
        source = open("pp-migrate.js", encoding="utf-8").read()
        match = re.search(r"SCHEMA_VERSION\s*=\s*(\d+)", source)
        if match:
            schema_version = int(match.group(1))
        match = re.search(
            r"CONTENT_MIGRATION_REVISION\s*=\s*(\d+)", source)
        if match:
            migration_revision = int(match.group(1))
    return {
        "appVersion": app_version,
        "schemaVersion": schema_version,
        "migrationRevision": migration_revision,
    }


def baseline_digest(document):
    protected = dict(document)
    protected.pop("contentSha256", None)
    payload = canonical_json(protected).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_forward_baseline(
        sources, origin=FORWARD_BASELINE_ORIGIN,
        app_version=FORWARD_BASELINE_APP_VERSION, schema_version=None,
        migration_revision=None, legacy=None):
    stable_ids = []
    wording = []
    policy = []
    structure = []
    for source in sources:
        source_ids, source_wording, source_policy, source_structure = (
            _source_snapshot(source))
        stable_ids.extend(source_ids)
        wording.extend(source_wording)
        policy.extend(source_policy)
        structure.extend(source_structure)
    stable_ids.sort(key=lambda row: (
        str(row.get("id")), row["kind"], row["path"]))
    wording.sort(key=lambda row: (
        row["path"], row["field"], row["value"]))
    policy.sort(key=lambda row: (row["path"], row["kind"]))
    structure.sort(key=lambda row: (row["path"], row["kind"]))
    document = {
        "formatVersion": FORWARD_BASELINE_FORMAT,
        "baselineKind": FORWARD_BASELINE_KIND,
        "baselineOriginCommit": origin,
        "baselineOriginAppVersion": app_version,
        "limitations": FORWARD_BASELINE_LIMITATIONS,
        "schemaVersion": schema_version,
        "migrationRevision": migration_revision,
        "approvedChanges": [],
        "stableIds": stable_ids,
        "legacy": legacy if legacy is not None else {},
        "wording": wording,
        "policy": policy,
        "structure": structure,
    }
    document["contentSha256"] = baseline_digest(document)
    return document


def _record_map(records, fields):
    return {
        tuple(record.get(field) for field in fields): record
        for record in records if isinstance(record, dict)
    }


def _section_changes(before, after, key_fields):
    old = _record_map(before, key_fields)
    new = _record_map(after, key_fields)
    added = [new[key] for key in sorted(new.keys() - old.keys())]
    removed = [old[key] for key in sorted(old.keys() - new.keys())]
    changed = [
        {"before": old[key], "after": new[key]}
        for key in sorted(old.keys() & new.keys())
        if old[key] != new[key]
    ]
    return added, removed, changed


def _baseline_format(issues, message):
    issues.append(issue("BASELINE_FORMAT", message))


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_string_list(value):
    return (
        isinstance(value, list) and
        all(isinstance(item, str) for item in value)
    )


def _valid_presence_record(value, effective=None):
    if not isinstance(value, dict):
        return False
    expected = {"present"}
    if value.get("present") is True:
        expected.add("value")
    if effective is True:
        expected.add("effective")
    elif effective is None and "effective" in value:
        expected.add("effective")
    if set(value) != expected or not isinstance(value.get("present"), bool):
        return False
    return effective is not False or "effective" not in value


def _presence_values_match(value, value_check=None, effective_check=None):
    if not isinstance(value, dict):
        return False
    if value.get("present") is True and value_check is not None:
        if not value_check(value.get("value")):
            return False
    if "effective" in value and effective_check is not None:
        if not effective_check(value.get("effective")):
            return False
    return True


def _validate_baseline_stable_ids(rows, issues):
    identities = []
    placements = []
    for index, row in enumerate(rows):
        if (
                not isinstance(row, dict) or
                set(row) != {"id", "kind", "path", "source"} or
                not all(_nonempty_string(row.get(key))
                        for key in ("id", "kind", "path", "source")) or
                row.get("kind") not in {"level", "topic", "card", "drill"} or
                not ID_RE.fullmatch(row.get("id", ""))):
            _baseline_format(
                issues, f"stableIds[{index}] has an invalid record schema.")
            continue
        identities.append(row["id"])
        placements.append((row["kind"], row["path"]))
    if len(identities) != len(set(identities)):
        _baseline_format(issues, "stableIds contains duplicate IDs.")
    if len(placements) != len(set(placements)):
        _baseline_format(
            issues, "stableIds contains duplicate kind/path records.")


def _validate_baseline_wording(rows, issues):
    identities = []
    for index, row in enumerate(rows):
        if (
                not isinstance(row, dict) or
                set(row) != {"path", "field", "value"} or
                not all(isinstance(row.get(key), str)
                        for key in ("path", "field", "value")) or
                not row.get("path") or not row.get("field")):
            _baseline_format(
                issues, f"wording[{index}] has an invalid record schema.")
            continue
        identities.append((row["path"], row["field"]))
    if len(identities) != len(set(identities)):
        _baseline_format(
            issues, "wording contains duplicate path/field records.")


def _validate_baseline_policy(rows, issues):
    card_fields = {
        "kind", "path", "cardType", "register", "region", "production",
        "practice", "intro", "strength", "warningPlacement",
    }
    topic_fields = {"kind", "path", "cefr", "mature"}
    effective_fields = {
        "cardType", "register", "region", "production", "intro",
        "mature",
    }
    string_value = _nonempty_string
    bool_value = lambda value: isinstance(value, bool)
    value_checks = {
        "cefr": lambda value: (
            isinstance(value, str) and value in ALLOWED_CEFR),
        "mature": bool_value,
        "cardType": lambda value: value == "template",
        "register": lambda value: (
            isinstance(value, str) and value in ALLOWED_REGISTER),
        "region": lambda value: (
            isinstance(value, str) and value in ALLOWED_REGION),
        "production": lambda value: (
            isinstance(value, str) and value in ALLOWED_PRODUCTION),
        "practice": lambda value: (
            isinstance(value, dict) and value == {"typeIt": False}),
        "intro": lambda value: value is True,
        "strength": lambda value: (
            isinstance(value, str) and value in ALLOWED_STRENGTH),
    }
    effective_checks = {
        "mature": bool_value,
        "cardType": lambda value: value in {"standard", "template"},
        "register": lambda value: (
            isinstance(value, str) and value in ALLOWED_REGISTER),
        "region": lambda value: (
            isinstance(value, str) and value in ALLOWED_REGION),
        "production": lambda value: (
            isinstance(value, str) and value in ALLOWED_PRODUCTION),
        "intro": bool_value,
    }
    identities = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            _baseline_format(
                issues, f"policy[{index}] must be an object.")
            continue
        kind = row.get("kind")
        expected = card_fields if kind == "card" else (
            topic_fields if kind == "topic" else None)
        valid = (
            expected is not None and set(row) == expected and
            _nonempty_string(row.get("path")))
        if valid:
            for field in expected - {"kind", "path"}:
                if field == "warningPlacement":
                    if not (
                            isinstance(row.get(field), dict) and
                            set(row[field]) == {"present"} and
                            isinstance(row[field].get("present"), bool)):
                        valid = False
                    continue
                effective = True if field in effective_fields else False
                if (
                        not _valid_presence_record(row.get(field), effective) or
                        not _presence_values_match(
                            row.get(field), value_checks.get(
                                field, string_value),
                            effective_checks.get(field))):
                    valid = False
                    break
        if not valid:
            _baseline_format(
                issues, f"policy[{index}] has an invalid {kind!r} schema.")
            continue
        identities.append((row["path"], kind))
    if len(identities) != len(set(identities)):
        _baseline_format(
            issues, "policy contains duplicate path/kind records.")


def _validate_baseline_structure(rows, issues):
    schemas = {
        "level": {
            "kind", "path", "sourceIndex", "group", "topicOrder"},
        "topic": {
            "kind", "path", "sourceIndex", "parentLevelId", "topicKind",
            "declaredKind", "host", "link", "cardOrder", "drillOrder"},
        "card": {
            "kind", "path", "sourceIndex", "parentTopicId", "relationType",
            "relatedIds", "senseGroups", "acceptedAnswerCount",
            "variantCount"},
        "drill": {
            "kind", "path", "sourceIndex", "parentTopicId", "drillType",
            "acceptedOrderCount"},
        "scene": {
            "kind", "path", "sourceIndex", "parentTopicId", "sceneKey",
            "terminal", "optionRoutes"},
    }
    presence_fields = {
        "group", "declaredKind", "host", "link", "relationType",
        "relatedIds", "senseGroups", "drillType", "start",
    }
    identities = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            _baseline_format(
                issues, f"structure[{index}] must be an object.")
            continue
        kind = row.get("kind")
        expected = schemas.get(kind) if isinstance(kind, str) else None
        if kind == "topic" and (
                "start" in row or "sceneOrder" in row):
            expected = set(expected or ()) | {"start", "sceneOrder"}
        valid = (
            expected is not None and set(row) == expected and
            _nonempty_string(row.get("path")) and
            _is_int(row.get("sourceIndex")) and
            row.get("sourceIndex") >= 0)
        if valid:
            for field in presence_fields & expected:
                presence = row.get(field)
                value_check = (
                    (lambda value: _valid_string_list(value) and
                     len(value) == len(set(value)))
                    if field in {"relatedIds", "senseGroups"}
                    else _nonempty_string)
                if (
                        not _valid_presence_record(presence, False) or
                        not _presence_values_match(
                            presence, value_check=value_check)):
                    valid = False
            for field in (
                    "parentLevelId", "parentTopicId", "topicKind", "sceneKey"):
                if field in expected and not _nonempty_string(row.get(field)):
                    valid = False
            for field in ("topicOrder", "cardOrder", "drillOrder", "sceneOrder"):
                if field in expected:
                    values = row.get(field)
                    if (
                            not _valid_string_list(values) or
                            len(values) != len(set(values))):
                        valid = False
            for field in (
                    "acceptedAnswerCount", "variantCount",
                    "acceptedOrderCount"):
                if field in expected and not (
                        row.get(field) is None or
                        (_is_int(row.get(field)) and row.get(field) >= 0)):
                    valid = False
            if kind == "scene":
                terminal = row.get("terminal")
                valid = (
                    valid and _valid_presence_record(terminal, True) and
                    _presence_values_match(
                        terminal,
                        value_check=lambda value: value is True,
                        effective_check=lambda value: isinstance(value, bool)))
                routes = row.get("optionRoutes")
                valid = valid and isinstance(routes, list)
                if isinstance(routes, list):
                    valid = valid and all(
                        isinstance(route, dict) and
                        set(route) == {"index", "goto"} and
                        _is_int(route.get("index")) and
                        route.get("index") >= 0 and
                        _valid_presence_record(route.get("goto"), False) and
                        _presence_values_match(
                            route.get("goto"),
                            value_check=_nonempty_string)
                        for route in routes)
                    if valid:
                        route_indexes = [
                            route["index"] for route in routes]
                        valid = len(route_indexes) == len(set(route_indexes))
        if not valid:
            _baseline_format(
                issues, f"structure[{index}] has an invalid {kind!r} schema.")
            continue
        identities.append((row["path"], kind))
    if len(identities) != len(set(identities)):
        _baseline_format(
            issues, "structure contains duplicate path/kind records.")


def _validate_baseline_legacy(value, issues):
    valid = (
        isinstance(value, dict) and
        set(value) == {"schema", "topics", "cards", "retired"} and
        _is_int(value.get("schema")) and
        isinstance(value.get("topics"), dict) and
        isinstance(value.get("cards"), dict) and
        isinstance(value.get("retired"), dict))
    if valid:
        valid = all(
            _nonempty_string(key) and _nonempty_string(mapped)
            for key, mapped in value["topics"].items())
        valid = valid and all(
            _nonempty_string(topic_id) and isinstance(mapping, dict) and all(
                isinstance(wording, str) and
                _valid_string_list(ids) and
                all(_nonempty_string(stable_id) for stable_id in ids)
                for wording, ids in mapping.items())
            for topic_id, mapping in value["cards"].items())
        valid = valid and all(
            _nonempty_string(topic_id) and _valid_string_list(wordings) and
            all(isinstance(wording, str) for wording in wordings)
            for topic_id, wordings in value["retired"].items())
    if not valid:
        _baseline_format(
            issues, "legacy must match the exact nested migration schema.")


def validate_baseline_document(document):
    issues = []
    if not isinstance(document, dict):
        return [issue(
            "BASELINE_FORMAT", "Forward baseline must be a JSON object.")]
    required_fields = {
        "formatVersion", "baselineKind", "baselineOriginCommit",
        "baselineOriginAppVersion", "limitations", "schemaVersion",
        "migrationRevision", "approvedChanges", "stableIds", "legacy",
        "wording", "policy", "structure", "contentSha256",
    }
    if set(document) != required_fields:
        _baseline_format(
            issues, "Forward baseline has missing or unsupported fields.")
    if document.get("formatVersion") != FORWARD_BASELINE_FORMAT:
        issues.append(issue(
            "BASELINE_FORMAT",
            f"formatVersion must be {FORWARD_BASELINE_FORMAT}."))
    if document.get("baselineKind") != FORWARD_BASELINE_KIND:
        issues.append(issue(
            "BASELINE_KIND",
            f"baselineKind must be {FORWARD_BASELINE_KIND!r}."))
    if document.get("baselineOriginCommit") != FORWARD_BASELINE_ORIGIN:
        issues.append(issue(
            "BASELINE_ORIGIN",
            f"baselineOriginCommit must be {FORWARD_BASELINE_ORIGIN}."))
    if document.get(
            "baselineOriginAppVersion") != FORWARD_BASELINE_APP_VERSION:
        issues.append(issue(
            "BASELINE_APP_VERSION",
            "baselineOriginAppVersion must be 7.30."))
    if document.get("limitations") != FORWARD_BASELINE_LIMITATIONS:
        issues.append(issue(
            "BASELINE_LIMITATIONS",
            "Forward-baseline limitations are missing or altered."))
    expected_types = {
        "stableIds": list,
        "legacy": dict,
        "wording": list,
        "policy": list,
        "structure": list,
        "approvedChanges": list,
    }
    for section, expected_type in expected_types.items():
        if not isinstance(document.get(section), expected_type):
            _baseline_format(
                issues,
                f"Forward baseline section {section!r} must be a "
                f"{expected_type.__name__}.")
    for field in ("schemaVersion", "migrationRevision"):
        if not _is_int(document.get(field)):
            _baseline_format(issues, f"{field} must be an integer.")
    stable_rows = document.get("stableIds", [])
    if isinstance(stable_rows, list):
        _validate_baseline_stable_ids(stable_rows, issues)
    wording_rows = document.get("wording")
    if isinstance(wording_rows, list):
        _validate_baseline_wording(wording_rows, issues)
    policy_rows = document.get("policy")
    if isinstance(policy_rows, list):
        _validate_baseline_policy(policy_rows, issues)
    structure_rows = document.get("structure")
    if isinstance(structure_rows, list):
        _validate_baseline_structure(structure_rows, issues)
    if isinstance(document.get("legacy"), dict):
        _validate_baseline_legacy(document["legacy"], issues)
    approved = document.get("approvedChanges")
    if isinstance(approved, list) and not all(
            is_meaningful_review_reference(value) for value in approved):
        _baseline_format(
            issues,
            "approvedChanges must contain meaningful review references.")
    actual = document.get("contentSha256")
    expected = baseline_digest(document)
    if not isinstance(actual, str) or actual != expected:
        issues.append(issue(
            "BASELINE_DIGEST",
            f"contentSha256 does not match canonical content ({expected})."))
    return issues


def load_forward_baseline(path=FORWARD_BASELINE_PATH):
    if not os.path.exists(path):
        return None, [issue(
            "BASELINE_MISSING",
            f"Required forward baseline is missing: {path}", path)]
    try:
        with open(path, encoding="utf-8") as handle:
            document = json.load(
                handle, object_pairs_hook=_reject_duplicate_json_keys)
    except (OSError, ValueError) as exc:
        return None, [issue(
            "BASELINE_FORMAT", f"Cannot read forward baseline: {exc}", path)]
    return document, validate_baseline_document(document)


def compare_forward_baseline(baseline, candidate, allow_delta=False):
    """Compare every protected section and return issues plus classified delta."""
    issues = list(validate_baseline_document(baseline))
    delta = {
        "additions": {"stableIds": [], "wording": []},
        "wordingChanges": [],
        "policyChanges": [],
        "structuralChanges": [],
        "removals": {"stableIds": [], "wording": []},
        "idChanges": [],
        "legacyChanges": [],
    }
    if issues:
        return issues, delta

    old_ids = {row["id"]: row for row in baseline.get("stableIds", [])}
    new_ids = {row["id"]: row for row in candidate.get("stableIds", [])}
    for stable_id in sorted(new_ids.keys() - old_ids.keys()):
        delta["additions"]["stableIds"].append(new_ids[stable_id])
        if not allow_delta:
            issues.append(issue(
                "BASELINE_ID_ADDITION",
                f"New stable ID is not in the forward baseline: {stable_id}",
                new_ids[stable_id]["path"]))
    for stable_id in sorted(old_ids.keys() - new_ids.keys()):
        delta["removals"]["stableIds"].append(old_ids[stable_id])
        if not allow_delta:
            issues.append(issue(
                "BASELINE_ID_REMOVED",
                f"Protected stable ID disappeared: {stable_id}",
                old_ids[stable_id]["path"]))
    for stable_id in sorted(old_ids.keys() & new_ids.keys()):
        if old_ids[stable_id] != new_ids[stable_id]:
            change = {
                "id": stable_id,
                "before": old_ids[stable_id],
                "after": new_ids[stable_id],
            }
            delta["idChanges"].append(change)
            if not allow_delta:
                issues.append(issue(
                    "BASELINE_ID_REPURPOSED",
                    f"Stable ID changed kind, source, or placement: {stable_id}",
                    new_ids[stable_id]["path"]))

    added, removed, changed = _section_changes(
        baseline.get("wording", []), candidate.get("wording", []),
        ("path", "field"))
    delta["additions"]["wording"] = added
    delta["removals"]["wording"] = removed
    delta["wordingChanges"] = changed
    if not allow_delta:
        for record in added:
            issues.append(issue(
                "BASELINE_WORDING_ADDITION",
                f"Unreviewed learner-facing string added: {record['field']}",
                record["path"]))
        for record in removed + changed:
            path = record["path"] if "path" in record else record["after"]["path"]
            issues.append(issue(
                "BASELINE_WORDING_DRIFT",
                "Protected learner-facing wording changed or disappeared.",
                path))

    for section, key_fields, delta_key, code in (
            ("policy", ("path", "kind"), "policyChanges",
             "BASELINE_POLICY_DRIFT"),
            ("structure", ("path", "kind"), "structuralChanges",
             "BASELINE_STRUCTURE_DRIFT")):
        sec_added, sec_removed, sec_changed = _section_changes(
            baseline.get(section, []), candidate.get(section, []), key_fields)
        changes = (
            [{"change": "added", "after": row} for row in sec_added] +
            [{"change": "removed", "before": row} for row in sec_removed] +
            [{"change": "changed", **row} for row in sec_changed]
        )
        delta[delta_key] = changes
        if changes and not allow_delta:
            for change in changes:
                record = change.get("after") or change.get("before")
                issues.append(issue(
                    code, f"Protected {section} changed.", record["path"]))

    if baseline.get("legacy") != candidate.get("legacy"):
        delta["legacyChanges"].append({
            "before": baseline.get("legacy"),
            "after": candidate.get("legacy"),
        })
        if not allow_delta:
            issues.append(issue(
                "BASELINE_LEGACY_DRIFT",
                "Protected legacy mappings or migration facts changed."))
    if baseline.get("schemaVersion") != candidate.get("schemaVersion"):
        delta["structuralChanges"].append({
            "change": "schemaVersion",
            "before": baseline.get("schemaVersion"),
            "after": candidate.get("schemaVersion"),
        })
        if not allow_delta:
            issues.append(issue(
                "BASELINE_STRUCTURE_DRIFT",
                "Protected schemaVersion changed."))
    if baseline.get("migrationRevision") != candidate.get(
            "migrationRevision"):
        delta["structuralChanges"].append({
            "change": "migrationRevision",
            "before": baseline.get("migrationRevision"),
            "after": candidate.get("migrationRevision"),
        })
        if not allow_delta:
            issues.append(issue(
                "BASELINE_STRUCTURE_DRIFT",
                "Protected migrationRevision changed."))
    return issues, delta


def answer_normalize(value):
    """Mirror PP_ANSWER.normalize for accepted-answer identity."""
    value = value.lower()
    value = re.sub(r"\.\.\.|…", " ", value)
    value = re.sub(r"""[?!.,;:“”"']""", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def eligible_for(card, activity):
    """Exact Python mirror of the current PP_USAGE.eligibleFor contract."""
    if not isinstance(card, dict):
        return False
    if activity in ("flashcard", "search"):
        return True
    if card.get("intro") or not card.get("pl") or not card.get("en"):
        return False
    if card.get("cardType") == "template":
        return False
    if activity == "listen":
        return True
    practice = card.get("practice")
    opted_out = (
        isinstance(practice, dict) and practice.get("typeIt") is False)
    if activity == "typeit" and opted_out:
        return False
    if activity in ("typeit", "mixed"):
        return card.get("production") != "recognition-only"
    return False


def activity_counts(cards):
    return {
        "flashcards": sum(eligible_for(card, "flashcard") for card in cards),
        "search": sum(eligible_for(card, "search") for card in cards),
        "typeIt": sum(eligible_for(card, "typeit") for card in cards),
        "listening": sum(eligible_for(card, "listen") for card in cards),
        "mixedQuiz": sum(eligible_for(card, "mixed") for card in cards),
    }


def topic_activity_counts(level, topic):
    """Apply PP_USAGE.eligibleFor plus the runtime's existing topic gates."""
    cards = topic.get("cards", [])
    counts = activity_counts(cards if isinstance(cards, list) else [])
    topics = level.get("topics", [])
    if not isinstance(topics, list):
        topics = []
    plain_vocabulary_level = bool(topics) and all(
        isinstance(item, dict) and not item.get("kind") for item in topics)
    if topic.get("kind"):
        counts["typeIt"] = 0
        counts["listening"] = 0
        if topic.get("kind") != "podcast":
            counts["mixedQuiz"] = 0
    else:
        if not plain_vocabulary_level or topic.get("mature"):
            counts["typeIt"] = 0
            counts["listening"] = 0
        # Mature vocabulary remains reachable through its gated study screen,
        # so Mixed Quiz keeps the card-level production count.
    return counts


def validate_audio_normalization_parity(normalizer=pp_audio_rule.normalize):
    samples = (
        "  Zażółć   gęślą  ",
        "<b>Dzień</b> dobry",
        "Co słychać?",
        "A… B",
    )
    for sample in samples:
        if normalizer(sample) != pp_audio_rule.normalize(sample):
            return [issue(
                "AUDIO_NORMALIZATION_PARITY",
                "Audio reporting must use pp_audio_rule.normalize exactly.")]
    return []


def _nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def validate_topic_architecture(topic, path):
    """Enforce the four supported topic kind/container combinations."""
    if not isinstance(topic, dict):
        return [issue(
            "TOPIC_RECORD_INVALID", "Topic must be an object.", path)]

    issues = []
    declared_present = "kind" in topic
    declared = topic.get("kind")
    supported_declared = {"podcast", "grammar", "convo"}
    declared_valid = (
        declared_present and isinstance(declared, str) and
        declared in supported_declared)
    if declared_present and not declared_valid:
        issues.append(issue(
            "TOPIC_KIND_INVALID",
            "Authored topic kind must be 'podcast', 'grammar', or 'convo'; "
            "plain vocabulary topics must omit kind.",
            path))

    containers = [
        name for name in ("cards", "drills", "scenes") if name in topic
    ]
    if len(containers) > 1:
        issues.append(issue(
            "TOPIC_CONTAINER_CONFLICT",
            "Topic may contain exactly one of cards, drills, or scenes; "
            f"found {containers}.",
            path))
        return issues

    inferred = {
        "cards": "vocab",
        "drills": "grammar",
        "scenes": "convo",
    }.get(containers[0] if containers else None)
    if declared_valid:
        expected = declared
        # Podcasts intentionally share the cards container with vocabulary.
        matches = (
            inferred == "vocab" if expected == "podcast"
            else inferred == expected)
        if not matches:
            required_container = {
                "podcast": "cards",
                "grammar": "drills",
                "convo": "scenes",
            }[expected]
            issues.append(issue(
                "TOPIC_KIND_CONTAINER_MISMATCH",
                f"kind:{expected!r} requires {required_container} "
                "and forbids the other topic containers.",
                path))
    elif not declared_present and inferred != "vocab":
        issues.append(issue(
            "TOPIC_KIND_CONTAINER_MISMATCH",
            "A topic without kind must contain cards only; grammar, "
            "conversation, and podcast topics require their supported kind.",
            path))
    return issues


def validate_card(card, path):
    issues = []
    if not isinstance(card, dict):
        return [issue(
            "CARD_RECORD_INVALID", "Card must be an object.", path)]
    if not all(isinstance(key, str) for key in card):
        issues.append(issue(
            "CARD_FIELD_KEY_INVALID",
            "Card field names must be strings.", path))

    if "intro" in card:
        if card.get("intro") is not True:
            issues.append(issue(
                "INTRO_FLAG_INVALID",
                "Authored intro must be exactly true.", path))
        else:
            for key in sorted(
                    set(card) - INTRO_CARD_FIELDS, key=lambda value: str(value)):
                issues.append(issue(
                    "INTRO_FIELD_UNSUPPORTED",
                    f"Unsupported intro field: {key}", path))
            for field in ("id", "pl", "en", "hint", "host", "link"):
                if not _nonempty_string(card.get(field)):
                    issues.append(issue(
                        "INTRO_REQUIRED_FIELD",
                        f"Podcast intro requires non-empty {field!r}.", path))
            return issues

    if "cefr" in card:
        issues.append(issue(
            "CEFR_CARD_UNSUPPORTED",
            "Vocabulary cards inherit CEFR; per-card cefr is unsupported.",
            path))
    for key in sorted(
            set(card) - CARD_FIELDS - {"cefr"},
            key=lambda value: str(value)):
        issues.append(issue(
            "CARD_FIELD_UNKNOWN",
            f"Unsupported card field: {key}", path))

    for field in ("id", "pl", "en", "hint", "ex", "exEn"):
        if not _nonempty_string(card.get(field)):
            issues.append(issue(
                "CARD_REQUIRED_FIELD",
                f"Standard practice card requires non-empty {field!r}.",
                path))
    for field in ("host", "link"):
        if field in card:
            issues.append(issue(
                "INTRO_FIELD_UNSUPPORTED",
                f"{field} is supported only on a podcast intro.", path))

    for field, allowed in (
            ("register", ALLOWED_REGISTER),
            ("region", ALLOWED_REGION),
            ("production", ALLOWED_PRODUCTION),
            ("strength", ALLOWED_STRENGTH)):
        if field in card and card.get(field) not in allowed:
            issues.append(issue(
                "CARD_POLICY_ENUM",
                f"{field} must be one of {sorted(allowed)}.", path))
    if "warning" in card and not _nonempty_string(card.get("warning")):
        issues.append(issue(
            "CARD_WARNING_SHAPE",
            "warning must be a non-empty string when present.", path))
    if "typeItCue" in card and not _nonempty_string(card.get("typeItCue")):
        issues.append(issue(
            "CARD_TYPEIT_CUE_SHAPE",
            "typeItCue must be a non-empty string when present.", path))
    for field in ("pair", "host", "link"):
        if field in card and not _nonempty_string(card.get(field)):
            issues.append(issue(
                "CARD_OPTIONAL_FIELD_SHAPE",
                f"{field} must be a non-empty string when present.", path))
    if "practice" in card:
        practice = card.get("practice")
        if not isinstance(practice, dict):
            issues.append(issue(
                "CARD_PRACTICE_INVALID",
                "practice must be an object containing only typeIt:false.",
                path))
        else:
            unknown = sorted(
                set(practice) - {"typeIt"}, key=lambda value: str(value))
            if unknown:
                issues.append(issue(
                    "CARD_PRACTICE_UNKNOWN",
                    f"Unknown practice keys: {unknown}", path))
            if "typeIt" not in practice or practice.get("typeIt") is not False:
                issues.append(issue(
                    "CARD_PRACTICE_INVALID",
                    "The only supported authored practice value is typeIt:false.",
                    path))

    if card.get("cardType") not in (None, "template"):
        issues.append(issue(
            "CARD_TYPE_INVALID",
            "cardType must be absent (standard) or 'template'.", path))
    if card.get("cardType") == "template":
        if not _nonempty_string(card.get("pattern")):
            issues.append(issue(
                "TEMPLATE_PATTERN_REQUIRED",
                "Template cards require a complete non-empty pattern.", path))
        if "audioText" in card and not pp_audio_rule.is_complete_utterance(
                card.get("audioText")):
            issues.append(issue(
                "TEMPLATE_AUDIO_INCOMPLETE",
                "Template audioText must be a complete utterance or absent.",
                path))
        if card.get("production") == "recognition-only":
            issues.append(issue(
                "TEMPLATE_RECOGNITION_ONLY",
                "Recognition-only templates are invalid.", path))
    elif "audioText" in card:
        issues.append(issue(
            "TEMPLATE_AUDIO_UNSUPPORTED",
            "audioText is only supported on a template card.", path))
    elif "pattern" in card:
        issues.append(issue(
            "TEMPLATE_PATTERN_UNSUPPORTED",
            "pattern is only supported on a template card.", path))

    accepted = card.get("acceptedAnswers")
    if accepted is not None:
        if not isinstance(accepted, list) or not accepted:
            issues.append(issue(
                "ACCEPTED_ANSWER_INVALID",
                "acceptedAnswers must be a non-empty list.", path))
        else:
            seen = set()
            canonical = (
                answer_normalize(card["pl"])
                if isinstance(card.get("pl"), str) else None)
            for answer in accepted:
                if not _nonempty_string(answer):
                    issues.append(issue(
                        "ACCEPTED_ANSWER_INVALID",
                        "Every accepted answer must be a non-empty string.",
                        path))
                    continue
                key = answer_normalize(answer)
                if key == canonical:
                    issues.append(issue(
                        "ACCEPTED_ANSWER_CANONICAL",
                        "Accepted answer duplicates canonical pl after "
                        "runtime normalization.", path))
                if key in seen:
                    issues.append(issue(
                        "ACCEPTED_ANSWER_DUPLICATE",
                        "Accepted answers must be distinct after runtime "
                        "normalization.", path))
                seen.add(key)

    variants = card.get("variants")
    if variants is not None:
        if not isinstance(variants, list):
            issues.append(issue(
                "VARIANT_INVALID",
                "variants must be a list of {form,label}.", path))
        else:
            for variant in variants:
                if not isinstance(variant, dict) or set(variant) != {
                        "form", "label"} or not _nonempty_string(
                            variant.get("form")) or not _nonempty_string(
                                variant.get("label")):
                    issues.append(issue(
                        "VARIANT_INVALID",
                        "Each variant requires exactly non-empty form and label.",
                        path))

    if "relatedIds" in card:
        related = card.get("relatedIds")
        if not isinstance(related, list) or not all(
                isinstance(item, str) and ID_RE.match(item)
                for item in related):
            issues.append(issue(
                "RELATED_IDS_INVALID",
                "relatedIds must contain lowercase-ASCII stable IDs.", path))
        elif len(related) != len(set(related)):
            issues.append(issue(
                "RELATED_IDS_INVALID",
                "relatedIds must not contain duplicates.", path))
    if "senseGroups" in card:
        groups = card.get("senseGroups")
        if not isinstance(groups, list) or not groups or not all(
                isinstance(group, str) and SENSE_GROUP_RE.fullmatch(group)
                for group in groups) or len(groups) != len(set(groups)):
            issues.append(issue(
                "SENSE_GROUP_INVALID",
                "senseGroups must be a non-empty list of distinct "
                "lowercase-kebab keys.", path))
    if "relationType" in card and card.get(
            "relationType") not in ALLOWED_RELATION:
        issues.append(issue(
            "RELATION_TYPE_INVALID",
            "relationType is not supported.", path))
    return issues


def validate_conversation_graph(topic, path):
    issues = []
    if not isinstance(topic, dict):
        return [issue(
            "TOPIC_RECORD_INVALID", "Topic must be an object.", path)]
    scenes = topic.get("scenes")
    if not isinstance(scenes, dict) or not scenes:
        return [issue(
            "GRAPH_SCENES_INVALID",
            "Conversation topic requires a non-empty scenes object.", path)]
    invalid_keys = [
        key for key in scenes if not _nonempty_string(key)
    ]
    for key in invalid_keys:
        issues.append(issue(
            "GRAPH_SCENE_KEY_INVALID",
            f"Scene key must be a non-empty string: {key!r}", path))
    scenes = {
        key: value for key, value in scenes.items()
        if _nonempty_string(key)
    }
    if not scenes:
        return issues
    issues.extend(validate_unique_scene_keys(list(scenes), path))
    start = topic.get("start")
    if not _nonempty_string(start):
        issues.append(issue(
            "GRAPH_START_MISSING",
            "Conversation topic requires a non-empty start.", path))
    elif start not in scenes:
        issues.append(issue(
            "GRAPH_START_UNKNOWN",
            f"Conversation start does not name a scene: {start!r}", path))

    edges = {key: [] for key in scenes}
    terminals = set()
    npc_count = 0
    choice_count = 0
    for scene_key, scene in scenes.items():
        scene_path = f"{path}/scene:{scene_key}"
        if not isinstance(scene, dict):
            issues.append(issue(
                "GRAPH_SCENE_INVALID", "Scene must be an object.", scene_path))
            continue
        if not _nonempty_string(scene.get("npc")) or not _nonempty_string(
                scene.get("npcEn")):
            issues.append(issue(
                "GRAPH_NPC_LANGUAGE",
                "Every scene requires non-empty npc and npcEn.", scene_path))
        else:
            npc_count += 1
        if scene.get("end") is True:
            terminals.add(scene_key)
        elif "end" in scene:
            issues.append(issue(
                "GRAPH_TERMINAL_INVALID",
                "Scene end must be exactly true when present.", scene_path))
        options = scene.get("options", [])
        if not isinstance(options, list):
            issues.append(issue(
                "GRAPH_OPTIONS_INVALID",
                "Scene options must be a list.", scene_path))
            continue
        for index, option in enumerate(options):
            option_path = f"{scene_path}/option:{index:03d}"
            choice_count += 1
            if not isinstance(option, dict):
                issues.append(issue(
                    "GRAPH_OPTION_INVALID",
                    "Conversation option must be an object.", option_path))
                continue
            if not _nonempty_string(option.get("pl")) or not _nonempty_string(
                    option.get("en")):
                issues.append(issue(
                    "GRAPH_OPTION_LANGUAGE",
                    "Every option requires non-empty pl and en.", option_path))
            goto = option.get("goto")
            if not _nonempty_string(goto) or goto not in scenes:
                issues.append(issue(
                    "GRAPH_GOTO_UNKNOWN",
                    f"Option goto does not name a scene: {goto!r}",
                    option_path))
            else:
                edges[scene_key].append(goto)

    reachable = set()
    if isinstance(start, str) and start in scenes:
        stack = [start]
        while stack:
            scene_key = stack.pop()
            if scene_key in reachable:
                continue
            reachable.add(scene_key)
            stack.extend(
                target for target in edges.get(scene_key, [])
                if target not in reachable)
        for scene_key in sorted(set(scenes) - reachable):
            issues.append(issue(
                "GRAPH_UNREACHABLE",
                f"Scene is unreachable from start: {scene_key}",
                f"{path}/scene:{scene_key}"))

    reachable_terminals = terminals & reachable
    if not reachable_terminals:
        issues.append(issue(
            "GRAPH_NO_TERMINAL",
            "Conversation has no reachable terminal route.", path))
    reverse = {key: [] for key in scenes}
    for source, targets in edges.items():
        for target in targets:
            reverse[target].append(source)
    can_terminate = set(reachable_terminals)
    stack = list(reachable_terminals)
    while stack:
        target = stack.pop()
        for source in reverse.get(target, []):
            if source not in can_terminate:
                can_terminate.add(source)
                stack.append(source)
    for scene_key in sorted(reachable - can_terminate):
        issues.append(issue(
            "GRAPH_NON_TERMINATING",
            f"Reachable scene has no path to an ending: {scene_key}",
            f"{path}/scene:{scene_key}"))
    return issues


def validate_unique_scene_keys(scene_keys, path):
    duplicates = sorted(
        key for key, count in Counter(scene_keys).items() if count > 1)
    if not duplicates:
        return []
    return [issue(
        "GRAPH_SCENE_KEY_DUPLICATE",
        f"Conversation scene keys must be unique: {duplicates}", path)]


def _cards_with_context(sources):
    rows = []
    if not isinstance(sources, list):
        return rows
    for source in sources:
        if not isinstance(source, dict):
            continue
        source_name = source.get("source", "data-fixture.js")
        levels = source.get("levels", [])
        if not isinstance(levels, list):
            continue
        for level in levels:
            if not isinstance(level, dict):
                continue
            topics = level.get("topics", [])
            if not isinstance(topics, list):
                continue
            for topic in topics:
                if not isinstance(topic, dict):
                    continue
                cards = topic.get("cards", [])
                if not isinstance(cards, list):
                    continue
                for index, card in enumerate(cards):
                    if not isinstance(card, dict):
                        continue
                    rows.append({
                        "source": source_name,
                        "level": level,
                        "topic": topic,
                        "card": card,
                        "index": index,
                        "path": (
                            f"{source_name}#/level:{level.get('id')}"
                            f"/topic:{topic.get('id')}/card:{card.get('id')}")
                    })
    return rows


def duplicate_groups(sources, origin_ids=frozenset()):
    cards = _cards_with_context(sources)

    def normalized_text(value):
        return (
            pp_audio_rule.normalize(value).casefold()
            if isinstance(value, str) else "")

    def grouped(key_function, rows=cards):
        buckets = {}
        for row in rows:
            if not isinstance(row["card"].get("id"), str):
                continue
            key = key_function(row["card"])
            if not key:
                continue
            buckets.setdefault(key, []).append(row)
        result = []
        for key, members in sorted(buckets.items()):
            ids = sorted({row["card"]["id"] for row in members})
            if len(ids) < 2:
                continue
            new_ids = sorted(stable_id for stable_id in ids
                             if stable_id not in origin_ids)
            status = (
                "origin-existing" if not new_ids else
                "candidate-new" if len(new_ids) == len(ids) else
                "mixed-candidate")
            result.append({
                "key": key,
                "ids": ids,
                "newIds": new_ids,
                "status": status,
            })
        return result

    productive = [
        row for row in cards
        if eligible_for(row["card"], "typeit") or
        eligible_for(row["card"], "mixed")
    ]
    accepted_rows = []
    for row in cards:
        card = row["card"]
        for value in [card.get("pl")] + (
                card.get("acceptedAnswers")
                if isinstance(card.get("acceptedAnswers"), list) else []):
            if isinstance(value, str) and answer_normalize(value):
                clone = dict(row)
                clone["card"] = {
                    "id": card.get("id"),
                    "answerValue": value,
                }
                accepted_rows.append(clone)

    audio_buckets = {}
    for source in sources if isinstance(sources, list) else []:
        if not isinstance(source, dict):
            continue
        levels = source.get("levels", [])
        if not isinstance(levels, list):
            continue
        for level in levels:
            if not isinstance(level, dict):
                continue
            topics = level.get("topics", [])
            if not isinstance(topics, list):
                continue
            for topic in topics:
                if not isinstance(topic, dict):
                    continue
                audio_texts = []
                # Collection and normalization both come from the shared audio
                # module; the topic ID only supplies origin/candidate ownership.
                try:
                    pp_audio_rule.walk_audio_texts(topic, audio_texts)
                except (AttributeError, TypeError, ValueError):
                    continue
                for value in audio_texts:
                    key = pp_audio_rule.normalize(value)
                    if key and isinstance(topic.get("id"), str):
                        audio_buckets.setdefault(key, []).append(
                            topic.get("id"))

    return {
        "normalizedPolish": grouped(
            lambda card: normalized_text(card.get("pl"))),
        "normalizedEnglish": grouped(
            lambda card: normalized_text(card.get("en"))),
        "examples": grouped(
            lambda card: normalized_text(card.get("ex"))),
        "strictReplicas": grouped(
            lambda card: "\u241f".join(
                normalized_text(card.get(field))
                for field in ("pl", "en", "ex"))),
        "acceptedAnswerOwnership": grouped(
            lambda card: answer_normalize(card.get("answerValue", "")),
            accepted_rows),
        "audioUtterances": [
            {
                "normalized": key,
                "occurrences": len(owners),
                "ownerIds": sorted(set(owners)),
                "newOwnerIds": sorted({
                    owner for owner in owners if owner not in origin_ids
                }),
                "status": _origin_status(
                    sorted(set(owners)), origin_ids),
            }
            for key, owners in sorted(audio_buckets.items())
            if len(owners) > 1
        ],
        "_productiveEnglish": grouped(
            lambda card: normalized_text(card.get("en")),
            productive),
    }


def _reviewed_exception_ids(candidate_expectations, section, issues):
    entries = candidate_expectations.get(section, [])
    if not isinstance(entries, list):
        issues.append(issue(
            "REVIEW_EXCEPTION_FORMAT",
            f"{section} must be a list of structured review records."))
        return set()
    reviewed = set()
    for index, entry in enumerate(entries):
        valid = (
            isinstance(entry, dict) and
            set(entry) == {"ids", "reason", "reviewReference"} and
            isinstance(entry.get("ids"), list) and
            len(entry["ids"]) >= 2 and
            all(isinstance(stable_id, str) and
                ID_RE.fullmatch(stable_id)
                for stable_id in entry["ids"]) and
            len(entry["ids"]) == len(set(entry["ids"])) and
            _nonempty_string(entry.get("reason")) and
            is_meaningful_review_reference(entry.get("reviewReference")))
        if not valid:
            issues.append(issue(
                "REVIEW_EXCEPTION_FORMAT",
                f"{section}[{index}] requires exactly distinct lowercase IDs, "
                "a non-empty reason, and a review reference."))
            continue
        reviewed.add(tuple(sorted(entry["ids"])))
    return reviewed


def validate_duplicate_policy(
        sources, origin_ids=frozenset(), candidate_expectations=None):
    candidate_expectations = (
        {} if candidate_expectations is None else candidate_expectations)
    issues = []
    if not isinstance(candidate_expectations, dict):
        issues.append(issue(
            "REVIEW_EXCEPTION_FORMAT",
            "Candidate expectations must be a JSON object."))
        candidate_expectations = {}
    reviewed_replicas = _reviewed_exception_ids(
        candidate_expectations, "reviewedReplicas", issues)
    reviewed_ownership = _reviewed_exception_ids(
        candidate_expectations, "reviewedAnswerOwnership", issues)
    groups = duplicate_groups(sources, origin_ids)
    for group in groups["strictReplicas"]:
        if (
                group["newIds"] and
                tuple(group["ids"]) not in reviewed_replicas):
            issues.append(issue(
                "DUPLICATE_STRICT_REPLICA",
                "New strict replica requires an explicit reviewed purpose: "
                + ", ".join(group["ids"])))
    for group in groups["acceptedAnswerOwnership"]:
        if (
                group["newIds"] and
                tuple(group["ids"]) not in reviewed_ownership):
            issues.append(issue(
                "ANSWER_OWNERSHIP_COLLISION",
                "New accepted-answer ownership collision requires an "
                "explicit reviewed purpose: " + ", ".join(group["ids"])))

    cards_by_id = {
        row["card"].get("id"): row["card"]
        for row in _cards_with_context(sources)
    }
    for group in groups["_productiveEnglish"]:
        if not group["newIds"]:
            continue
        polish = {
            pp_audio_rule.normalize(
                cards_by_id[stable_id].get("pl", "")).casefold()
            for stable_id in group["ids"]
        }
        if len(polish) < 2:
            continue
        cues = [
            cards_by_id[stable_id].get("typeItCue")
            for stable_id in group["ids"]
        ]
        normalized_cues = [
            pp_audio_rule.normalize(value).casefold()
            if isinstance(value, str) else ""
            for value in cues
        ]
        if any(not value for value in normalized_cues) or len(
                set(normalized_cues)) != len(normalized_cues):
            issues.append(issue(
                "PROMPT_CUE_REQUIRED",
                "New productive same-English/different-Polish cards require "
                "distinct non-empty typeItCue values: "
                + ", ".join(group["ids"])))
    return issues, groups


def validate_activity_expectations(sources, expectations=None):
    if expectations is None:
        return []
    if not isinstance(expectations, dict):
        return [issue(
            "ACTIVITY_EXPECTATION_FORMAT",
            "activityExpectations must be a JSON object.")]
    actual = {}
    for source in sources if isinstance(sources, list) else []:
        if not isinstance(source, dict):
            continue
        levels = source.get("levels", [])
        if not isinstance(levels, list):
            continue
        for level in levels:
            if not isinstance(level, dict):
                continue
            topics = level.get("topics", [])
            if not isinstance(topics, list):
                continue
            for topic in topics:
                if not isinstance(topic, dict):
                    continue
                if "cards" in topic:
                    actual[topic.get("id")] = topic_activity_counts(
                        level, topic)
    issues = []
    for topic_id, expected in sorted(
            expectations.items(), key=lambda item: str(item[0])):
        if (
                not isinstance(topic_id, str) or
                not isinstance(expected, dict) or
                set(expected) != {
                    "flashcards", "search", "typeIt", "listening",
                    "mixedQuiz"} or
                not all(_is_int(value) and value >= 0
                        for value in expected.values())):
            issues.append(issue(
                "ACTIVITY_EXPECTATION_FORMAT",
                f"Activity expectation for {topic_id!r} has an invalid "
                "schema."))
            continue
        if actual.get(topic_id) != expected:
            issues.append(issue(
                "ACTIVITY_EXPECTATION_CONFLICT",
                f"Activity expectation for {topic_id!r} is {expected!r}; "
                f"actual is {actual.get(topic_id)!r}."))
    return issues


def stable_id_set(document):
    if not isinstance(document, dict):
        return set()
    return {
        row.get("id") for row in document.get("stableIds", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def corpus_stable_id_set(sources):
    """Collect valid IDs without assuming any corpus container is well formed."""
    result = set()
    if not isinstance(sources, list):
        return result
    for source in sources:
        if not isinstance(source, dict):
            continue
        levels = source.get("levels")
        if not isinstance(levels, list):
            continue
        for level in levels:
            if not isinstance(level, dict):
                continue
            if isinstance(level.get("id"), str):
                result.add(level["id"])
            topics = level.get("topics")
            if not isinstance(topics, list):
                continue
            for topic in topics:
                if not isinstance(topic, dict):
                    continue
                if isinstance(topic.get("id"), str):
                    result.add(topic["id"])
                for field in ("cards", "drills"):
                    records = topic.get(field, [])
                    if not isinstance(records, list):
                        continue
                    result.update(
                        record["id"] for record in records
                        if isinstance(record, dict) and
                        isinstance(record.get("id"), str))
    return result


def validate_drill_shape(drill, path):
    if not isinstance(drill, dict):
        return [issue(
            "DRILL_RECORD_INVALID", "Drill must be an object.", path)]
    issues = []
    drill_type = drill.get("type")
    if not _nonempty_string(drill_type):
        issues.append(issue(
            "DRILL_FIELD_SHAPE",
            "Drill type must be a non-empty string.", path))
    if "options" in drill and (
            not isinstance(drill.get("options"), list) or
            not all(_nonempty_string(value)
                    for value in drill.get("options", []))):
        issues.append(issue(
            "DRILL_FIELD_SHAPE",
            "Drill options must be a list of non-empty strings.", path))
    answer = drill.get("answer")
    if drill_type == "build":
        if (
                not isinstance(answer, list) or not answer or
                not all(_nonempty_string(value) for value in answer)):
            issues.append(issue(
                "DRILL_FIELD_SHAPE",
                "Build answer must be a non-empty list of strings.", path))
    elif "answer" in drill and not _nonempty_string(answer):
        issues.append(issue(
            "DRILL_FIELD_SHAPE",
            "Non-build answer must be a non-empty string.", path))
    if "acceptedOrders" in drill:
        orders = drill.get("acceptedOrders")
        if (
                not isinstance(orders, list) or not orders or
                not all(isinstance(order, list) and order and
                        all(_nonempty_string(token) for token in order)
                        for order in orders)):
            issues.append(issue(
                "DRILL_FIELD_SHAPE",
                "acceptedOrders must contain non-empty string lists.", path))
    return issues


def validate_corpus(
        sources, origin_ids=frozenset(), candidate_expectations=None,
        activity_expectations=None,
        audio_normalizer=pp_audio_rule.normalize):
    """Validate synthetic or shipping content without writing any artifact."""
    issues = []
    seen = {}
    topic_ids = set()
    card_ids = set()
    related = {}
    new_suffixes = {}

    def check_stable_id(kind, obj, path):
        stable_id = obj.get("id") if isinstance(obj, dict) else None
        if not isinstance(stable_id, str) or not ID_RE.fullmatch(stable_id):
            issues.append(issue(
                "ID_FORMAT",
                f"{kind} requires a lowercase-ASCII [a-z0-9-]+ id.",
                path))
            return None
        if stable_id in seen:
            issues.append(issue(
                "ID_DUPLICATE_GLOBAL",
                f"Stable ID {stable_id!r} collides with {seen[stable_id]}.",
                path))
        else:
            seen[stable_id] = path
        return stable_id

    if not isinstance(sources, list):
        issues.append(issue(
            "SOURCE_CONTAINER_INVALID",
            "Content corpus must be a list of source records."))
        issues.extend(validate_audio_normalization_parity(audio_normalizer))
        return issues

    for source_index, source in enumerate(sources):
        if not isinstance(source, dict):
            issues.append(issue(
                "SOURCE_RECORD_INVALID",
                "Content source must be an object.",
                f"source:{source_index:03d}"))
            continue
        source_name = source.get("source", f"source:{source_index:03d}")
        if not _nonempty_string(source_name):
            issues.append(issue(
                "SOURCE_RECORD_INVALID",
                "Content source requires a non-empty source path.",
                f"source:{source_index:03d}"))
            source_name = f"source:{source_index:03d}"
        source_findings = source.get("sourceIssues", [])
        if not isinstance(source_findings, list):
            issues.append(issue(
                "SOURCE_ISSUES_INVALID",
                "sourceIssues must be a list.", source_name))
        else:
            for finding in source_findings:
                if (
                        isinstance(finding, dict) and
                        isinstance(finding.get("code"), str) and
                        isinstance(finding.get("message"), str)):
                    issues.append(finding)
                else:
                    issues.append(issue(
                        "SOURCE_ISSUES_INVALID",
                        "Every source issue must be a finding object.",
                        source_name))
        levels = source.get("levels")
        if not isinstance(levels, list):
            issues.append(issue(
                "SOURCE_LEVELS_INVALID",
                "Source levels must be a list.", source_name))
            continue
        for level_index, level in enumerate(levels):
            if not isinstance(level, dict):
                issues.append(issue(
                    "LEVEL_RECORD_INVALID", "Level must be an object.",
                    f"{source_name}#/level:{level_index:03d}"))
                continue
            level_path = f"{source_name}#/level:{level.get('id')}"
            level_id = check_stable_id("level", level, level_path)
            topics = level.get("topics")
            if not isinstance(topics, list):
                issues.append(issue(
                    "LEVEL_TOPICS_INVALID",
                    "Level topics must be a list.", level_path))
                continue
            for topic_index, topic in enumerate(topics):
                if not isinstance(topic, dict):
                    issues.append(issue(
                        "TOPIC_RECORD_INVALID", "Topic must be an object.",
                        f"{level_path}/topic:{topic_index:03d}"))
                    continue
                topic_path = f"{level_path}/topic:{topic.get('id')}"
                topic_id = check_stable_id("topic", topic, topic_path)
                if topic_id:
                    topic_ids.add(topic_id)
                issues.extend(validate_topic_architecture(topic, topic_path))
                kind = topic_kind(topic)
                is_new_topic = topic_id not in origin_ids

                if is_new_topic and kind == "vocab" and level_id and topic_id:
                    expected_prefix = level_id.lower() + "-"
                    if not topic_id.startswith(expected_prefix):
                        issues.append(issue(
                            "ID_TOPIC_NAMESPACE",
                            f"New vocabulary topic ID must start with "
                            f"{expected_prefix!r}.", topic_path))
                if is_new_topic and kind == "convo" and topic_id and not (
                        topic_id.startswith("scenarios-")):
                    issues.append(issue(
                        "ID_SCENARIO_NAMESPACE",
                        "New scenario topic ID must start with 'scenarios-'.",
                        topic_path))

                if "cefr" in topic and kind != "convo":
                    issues.append(issue(
                        "CEFR_TOPIC_UNSUPPORTED",
                        "Topic-level cefr is supported only for conversations.",
                        topic_path))
                if kind == "convo":
                    cefr = topic.get("cefr")
                    if cefr is not None and cefr not in ALLOWED_CEFR:
                        issues.append(issue(
                            "CEFR_SCENARIO_INVALID",
                            f"Scenario cefr must be one of {sorted(ALLOWED_CEFR)}.",
                            topic_path))
                    if is_new_topic and cefr is None:
                        issues.append(issue(
                            "CEFR_SCENARIO_REQUIRED",
                            "A new scenario topic must declare cefr.",
                            topic_path))
                    issues.extend(validate_conversation_graph(
                        topic, topic_path))

                cards = topic.get("cards", [])
                if not isinstance(cards, list):
                    issues.append(issue(
                        "TOPIC_CARDS_INVALID",
                        "Topic cards must be a list.", topic_path))
                    cards = []
                for card_index, card in enumerate(cards):
                    card_path = (
                        f"{topic_path}/card:{card.get('id')}"
                        if isinstance(card, dict) else
                        f"{topic_path}/card:{card_index:03d}")
                    if not isinstance(card, dict):
                        issues.append(issue(
                            "CARD_RECORD_INVALID",
                            "Card must be an object.", card_path))
                        continue
                    card_id = check_stable_id("card", card, card_path)
                    if card_id:
                        card_ids.add(card_id)
                    issues.extend(validate_card(card, card_path))
                    if card_id:
                        related[card_id] = card.get("relatedIds", [])

                    if card.get("intro") is True:
                        if kind != "podcast":
                            issues.append(issue(
                                "INTRO_TOPIC_UNSUPPORTED",
                                "Intro cards are supported only in podcast "
                                "topics.", card_path))
                        if not topic_id or card_id != f"{topic_id}-intro":
                            issues.append(issue(
                                "ID_INTRO_NAMESPACE",
                                "Podcast intro ID must be exactly "
                                f"{topic_id}-intro.", card_path))

                    if (
                            card_id and card_id not in origin_ids and
                            kind in {"vocab", "podcast"} and
                            card.get("intro") is not True):
                        prefix = (topic_id or "") + "-"
                        if not topic_id or not card_id.startswith(prefix):
                            issues.append(issue(
                                "ID_CARD_NAMESPACE",
                                f"New card ID must start with {prefix!r}.",
                                card_path))
                        else:
                            suffix = card_id[len(prefix):]
                            if (
                                    not re.fullmatch(r"\d{3}", suffix) or
                                    int(suffix) <= 0):
                                issues.append(issue(
                                    "ID_CARD_SUFFIX",
                                    "New card suffix must be a positive "
                                    "zero-padded three-digit value.",
                                    card_path))
                            else:
                                key = (topic_id, suffix)
                                if key in new_suffixes:
                                    issues.append(issue(
                                        "ID_DUPLICATE_SUFFIX",
                                        f"New suffix {suffix!r} is already used "
                                        f"by {new_suffixes[key]}.", card_path))
                                else:
                                    new_suffixes[key] = card_id

                drills = topic.get("drills", [])
                if not isinstance(drills, list):
                    issues.append(issue(
                        "TOPIC_DRILLS_INVALID",
                        "Topic drills must be a list.", topic_path))
                    drills = []
                for drill_index, drill in enumerate(drills):
                    drill_path = (
                        f"{topic_path}/drill:{drill.get('id')}"
                        if isinstance(drill, dict) else
                        f"{topic_path}/drill:{drill_index:03d}")
                    if not isinstance(drill, dict):
                        issues.append(issue(
                            "DRILL_RECORD_INVALID",
                            "Drill must be an object.", drill_path))
                        continue
                    drill_id = check_stable_id("drill", drill, drill_path)
                    issues.extend(validate_drill_shape(drill, drill_path))
                    if drill_id and drill_id not in origin_ids:
                        prefix = (topic_id or "") + "-"
                        if not topic_id or not drill_id.startswith(prefix):
                            issues.append(issue(
                                "ID_DRILL_NAMESPACE",
                                f"New drill ID must start with {prefix!r}.",
                                drill_path))
                        else:
                            suffix = drill_id[len(prefix):]
                            if (
                                    not re.fullmatch(r"\d{3}", suffix) or
                                    int(suffix) <= 0):
                                issues.append(issue(
                                    "ID_DRILL_SUFFIX",
                                    "New drill suffix must be a positive "
                                    "zero-padded three-digit value.",
                                    drill_path))

    for card_id, targets in sorted(related.items()):
        if not isinstance(targets, list):
            continue
        for target in targets:
            if not isinstance(target, str):
                continue
            if target not in card_ids:
                issues.append(issue(
                    "RELATED_ID_UNKNOWN",
                    f"{card_id} relates to unknown card {target!r}."))
            elif card_id not in related.get(target, []):
                issues.append(issue(
                    "RELATED_ID_NONRECIPROCAL",
                    f"{card_id} -> {target} is not reciprocal."))

    duplicate_issues, _ = validate_duplicate_policy(
        sources, origin_ids, candidate_expectations)
    issues.extend(duplicate_issues)
    issues.extend(validate_activity_expectations(
        sources, activity_expectations))
    issues.extend(validate_audio_normalization_parity(audio_normalizer))
    return issues


def _group_counter(values):
    return dict(sorted(Counter(values).items()))


def _origin_status(ids, origin_ids):
    new_ids = [stable_id for stable_id in ids if stable_id not in origin_ids]
    if not new_ids:
        return "origin-existing"
    if len(new_ids) == len(ids):
        return "candidate-new"
    return "mixed-candidate"


def build_inventory(
        sources, baseline=None, baseline_issues=None,
        manifest_path="audio-manifest.json", audio_glob="audio/*.mp3"):
    levels = corpus_levels(sources)
    origin_ids = stable_id_set(baseline)
    candidate = build_forward_baseline(
        sources,
        schema_version=(
            baseline.get("schemaVersion")
            if baseline else read_repo_metadata()["schemaVersion"]),
        migration_revision=(
            baseline.get("migrationRevision")
            if baseline else read_repo_metadata()["migrationRevision"]),
        legacy=(baseline.get("legacy") if baseline else load_legacy()),
    )
    candidate_ids = stable_id_set(candidate)
    per_source = []
    per_topic = []
    card_type_counter = Counter()
    register_counter = Counter()
    region_counter = Counter()
    production_counter = Counter()
    practice_counter = Counter()
    scenario_cefr = Counter()
    scenario_rows = []
    total_counts = Counter()

    for source in sources:
        source_counts = Counter()
        for level in source.get("levels", []):
            source_counts["levels"] += 1
            for topic in level.get("topics", []):
                source_counts["topics"] += 1
                cards = topic.get("cards", [])
                drills = topic.get("drills", [])
                source_counts["cards"] += len(cards)
                source_counts["drills"] += len(drills)
                if cards:
                    per_topic.append({
                        "source": source["source"],
                        "levelId": level.get("id"),
                        "topicId": topic.get("id"),
                        "cards": len(cards),
                        "activities": topic_activity_counts(level, topic),
                    })
                for card in cards:
                    card_type_counter[
                        card.get("cardType", "standard")] += 1
                    register_counter[
                        card.get("register", "neutral")] += 1
                    region_counter[card.get("region", "general")] += 1
                    production_counter[
                        card.get("production", "active")] += 1
                    practice_counter[
                        "typeIt:false"
                        if isinstance(card.get("practice"), dict) and
                        card["practice"].get("typeIt") is False
                        else "default"] += 1
                if topic_kind(topic) == "convo":
                    cefr = topic.get("cefr", "not stated (legacy)")
                    scenario_cefr[cefr] += 1
                    scenes = topic.get("scenes") or {}
                    choices = sum(
                        len(scene.get("options", []))
                        for scene in scenes.values()
                        if isinstance(scene, dict))
                    scenario_rows.append({
                        "topicId": topic.get("id"),
                        "cefr": cefr,
                        "scenes": len(scenes),
                        "npcAudioOccurrences": sum(
                            _nonempty_string(scene.get("npc"))
                            for scene in scenes.values()
                            if isinstance(scene, dict)),
                        "choiceAudioOccurrences": choices,
                    })
        per_source.append({
            "source": source["source"],
            **dict(sorted(source_counts.items())),
        })
        total_counts.update(source_counts)

    audio_occurrences = []
    pp_audio_rule.walk_audio_texts(levels, audio_occurrences)
    normalized_audio = [
        pp_audio_rule.normalize(value)
        for value in audio_occurrences
        if pp_audio_rule.normalize(value)
    ]
    distinct_audio = sorted(set(normalized_audio))
    manifest_entries = {}
    if os.path.exists(manifest_path):
        with open(manifest_path, encoding="utf-8") as handle:
            manifest_entries = json.load(handle).get("entries", {})
    manifest_utterances = {
        pp_audio_rule.normalize(entry.get("pl", ""))
        for entry in manifest_entries.values()
        if isinstance(entry, dict) and pp_audio_rule.normalize(
            entry.get("pl", ""))
    }
    reuse = sorted(set(distinct_audio) & manifest_utterances)
    required_new = sorted(set(distinct_audio) - manifest_utterances)

    duplicates = duplicate_groups(sources, origin_ids)
    duplicates.pop("_productiveEnglish", None)
    baseline_issues = baseline_issues or []
    report = {
        "formatVersion": 1,
        "counts": {
            "sources": len(sources),
            **dict(sorted(total_counts.items())),
            "stableIds": len(candidate_ids),
        },
        "perSource": sorted(per_source, key=lambda row: row["source"]),
        "stableIds": {
            "additions": sorted(candidate_ids - origin_ids),
            "removals": sorted(origin_ids - candidate_ids),
        },
        "cardTypes": dict(sorted(card_type_counter.items())),
        "activityCounts": sorted(
            per_topic, key=lambda row: (
                row["source"], str(row["levelId"]), str(row["topicId"]))),
        "usage": {
            "register": dict(sorted(register_counter.items())),
            "region": dict(sorted(region_counter.items())),
            "production": dict(sorted(production_counter.items())),
            "practice": dict(sorted(practice_counter.items())),
        },
        "cefr": {
            "scenarioTopics": dict(sorted(scenario_cefr.items())),
            "podcasts": "not stated (unchanged)",
        },
        "duplicates": duplicates,
        "collisions": duplicates["acceptedAnswerOwnership"],
        "scenarios": sorted(
            scenario_rows, key=lambda row: str(row["topicId"])),
        "audio": {
            "bearingOccurrences": len(normalized_audio),
            "distinctNormalizedUtterances": len(distinct_audio),
            "exactManifestReuse": reuse,
            "requiredNewUtterances": required_new,
            "manifestEntries": len(manifest_entries),
            "mp3Files": len(glob.glob(audio_glob)),
        },
        "baseline": {
            "path": FORWARD_BASELINE_PATH,
            "present": baseline is not None,
            "valid": baseline is not None and not baseline_issues,
            "errorCodes": sorted(issue_codes(baseline_issues)),
            "origin": baseline.get("baselineOriginCommit") if baseline else None,
            "digest": baseline.get("contentSha256") if baseline else None,
        },
    }
    return report


def build_repo_candidate(sources):
    metadata = read_repo_metadata()
    return build_forward_baseline(
        sources,
        origin=FORWARD_BASELINE_ORIGIN,
        # This remains the origin version even when an explicitly reviewed
        # future content update occurs under a later application version.
        app_version=FORWARD_BASELINE_APP_VERSION,
        schema_version=metadata["schemaVersion"],
        migration_revision=metadata["migrationRevision"],
        legacy=load_legacy(),
    )


def write_json_atomic(path, document, replace=False):
    """Write canonical JSON via a same-directory temporary file."""
    if os.path.exists(path) and not replace:
        return [issue(
            "BASELINE_EXISTS",
            "Initial creation refuses to replace an existing baseline.", path)]
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=".priority-5-forward-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as out:
            out.write(canonical_json(document))
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
    return []


def update_forward_baseline_file(
        path, baseline, candidate, approved_change, nonbaseline_issues=None):
    """Testable core of the explicit future update workflow."""
    issues = list(validate_baseline_document(baseline))
    issues.extend(nonbaseline_issues or [])
    if not approved_change:
        issues.append(issue(
            "BASELINE_APPROVAL_REQUIRED",
            "Update mode requires a non-empty approval/review reference.",
            path))
    elif not is_meaningful_review_reference(approved_change):
        issues.append(issue(
            "BASELINE_APPROVAL_INVALID",
            "Approval must be a concrete ticket or namespaced review "
            "reference.", path))
    if issues:
        return issues, None
    compare_issues, delta = compare_forward_baseline(
        baseline, candidate, allow_delta=True)
    issues.extend(compare_issues)
    has_delta = any((
        delta["additions"]["stableIds"],
        delta["additions"]["wording"],
        delta["wordingChanges"],
        delta["policyChanges"],
        delta["structuralChanges"],
        delta["removals"]["stableIds"],
        delta["removals"]["wording"],
        delta["idChanges"],
        delta["legacyChanges"],
    ))
    if not has_delta:
        issues.append(issue(
            "BASELINE_UPDATE_NOOP",
            "Update mode refuses a no-op baseline refresh.", path))
        return issues, delta
    updated = dict(candidate)
    history = baseline.get("approvedChanges", [])
    if not isinstance(history, list):
        history = []
    updated["approvedChanges"] = history + [approved_change.strip()]
    updated["contentSha256"] = baseline_digest(updated)
    issues.extend(write_json_atomic(path, updated, replace=True))
    return issues, delta


def validate_report_destination(destination):
    if destination is None or destination == "-":
        return []
    return [issue(
        "REPORT_WRITE_FORBIDDEN",
        "The deterministic report is read-only and supports stdout ('-') only.",
        destination)]


def _git_output(*args):
    completed = subprocess.run(
        ["git", *args], check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def initial_creation_guards(path, requested_origin):
    issues = []
    expected = os.path.abspath(FORWARD_BASELINE_PATH)
    if os.path.abspath(path) != expected:
        issues.append(issue(
            "BASELINE_PATH_UNEXPECTED",
            f"Forward baseline path must be {FORWARD_BASELINE_PATH}.", path))
    if requested_origin != FORWARD_BASELINE_ORIGIN:
        issues.append(issue(
            "BASELINE_ORIGIN",
            f"Creation origin must be {FORWARD_BASELINE_ORIGIN}."))
    if os.path.exists(path):
        issues.append(issue(
            "BASELINE_EXISTS",
            "Initial creation refuses to replace an existing baseline.", path))
    code, remote, remote_error = _git_output("remote", "-v")
    if code != 0:
        issues.append(issue(
            "GIT_REMOTE_CHECK_FAILED",
            f"Could not inspect Git remotes: {remote_error}"))
    elif remote:
        issues.append(issue(
            "GIT_REMOTE_CONFIGURED",
            "Initial creation requires an empty Git remote list."))
    code, head, head_error = _git_output("rev-parse", "HEAD")
    if code != 0:
        issues.append(issue(
            "GIT_HEAD_CHECK_FAILED",
            f"Could not inspect HEAD: {head_error}"))
    elif head != FORWARD_BASELINE_ORIGIN:
        issues.append(issue(
            "BASELINE_ORIGIN_HEAD",
            f"Initial creation requires HEAD {FORWARD_BASELINE_ORIGIN}."))
    metadata = read_repo_metadata()
    if metadata["appVersion"] != FORWARD_BASELINE_APP_VERSION:
        issues.append(issue(
            "BASELINE_APP_VERSION",
            "Initial creation requires application version 7.30."))
    code, tracked_data, tracked_error = _git_output(
        "diff", "--name-only", "HEAD", "--", "data-*.js")
    if code != 0:
        issues.append(issue(
            "GIT_STATUS_CHECK_FAILED",
            f"Could not inspect tracked learner data: {tracked_error}"))
    else:
        changed_data = tracked_data.splitlines()
        # A new untracked data file is not in `git diff HEAD`, but it would be
        # parsed into the candidate and therefore must also block creation.
        status_code, status, status_error = _git_output(
            "status", "--porcelain", "--untracked-files=all")
        if status_code != 0:
            issues.append(issue(
                "GIT_STATUS_CHECK_FAILED",
                f"Could not inspect untracked learner data: {status_error}"))
        for line in status.splitlines():
            path_part = line[3:] if len(line) >= 4 else ""
            if line.startswith("?? ") and re.fullmatch(
                    r"data-[^/]+\.js", path_part):
                changed_data.append(path_part)
        if changed_data:
            issues.append(issue(
                "BASELINE_LEARNER_DATA_DIRTY",
                "Initial creation refuses changed learner-data files: "
                + ", ".join(sorted(set(changed_data)))))
    return issues


def _legacy_issue_code(message):
    match = re.match(r"\[([A-Za-z0-9_-]+)\]", message)
    suffix = match.group(1).replace("-", "_").upper() if match else "CHECK"
    return "EXISTING_" + suffix


def validate_nonbaseline_repository(
        sources, origin_ids, candidate_expectations=None,
        activity_expectations=None):
    findings = validate_corpus(
        sources, origin_ids, candidate_expectations,
        activity_expectations)
    if findings:
        levels = corpus_levels(sources)
        topics = [
            topic for level in levels
            for topic in (
                level.get("topics", [])
                if isinstance(level.get("topics"), list) else [])
            if isinstance(topic, dict)
        ]
        cards = [
            card for topic in topics
            for card in (
                topic.get("cards", [])
                if isinstance(topic.get("cards"), list) else [])
            if isinstance(card, dict)
        ]
        drills = [
            drill for topic in topics
            for drill in (
                topic.get("drills", [])
                if isinstance(topic.get("drills"), list) else [])
            if isinstance(drill, dict)
        ]
        ids = corpus_stable_id_set(sources)
        existing = {
            "errors": [],
            "warnings": [],
            "summary": {
                "levels": len(levels),
                "topics": len(topics),
                "cards": len(cards),
                "drills": len(drills),
                "uniqueIds": len(ids),
                "topicIds": sum(
                    isinstance(topic.get("id"), str) for topic in topics),
                "cardIds": sum(
                    isinstance(card.get("id"), str) for card in cards),
            },
        }
        return findings, existing
    existing = run_existing_checks(corpus_levels(sources), emit=False)
    findings.extend(
        issue(_legacy_issue_code(message), message)
        for message in existing["errors"])
    return findings, existing


def _load_expectations(path):
    if not path:
        return {}, {}
    with open(path, encoding="utf-8") as handle:
        document = json.load(
            handle, object_pairs_hook=_reject_duplicate_json_keys)
    return (
        document,
        document.get("activityExpectations", {})
        if isinstance(document, dict) else {},
    )


def _print_findings(findings):
    for finding in findings:
        path = f" ({finding['path']})" if finding.get("path") else ""
        print(f"  x {finding['code']}: {finding['message']}{path}")


def _baseline_summary(document):
    legacy = document.get("legacy") or {}
    legacy_cards = sum(
        len(mapping or {})
        for mapping in (legacy.get("cards") or {}).values())
    legacy_retired = sum(
        len(values or [])
        for values in (legacy.get("retired") or {}).values())
    return {
        "stableIds": len(document.get("stableIds", [])),
        "wordingRecords": len(document.get("wording", [])),
        "policyRecords": len(document.get("policy", [])),
        "structureRecords": len(document.get("structure", [])),
        "legacyTopicMappings": len(legacy.get("topics") or {}),
        "legacyCardWordingKeys": legacy_cards,
        "legacyRetiredWordings": legacy_retired,
        "schemaVersion": document.get("schemaVersion"),
        "migrationRevision": document.get("migrationRevision"),
        "contentSha256": document.get("contentSha256"),
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Po polsku learner content deterministically.")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--write-forward-baseline")
    modes.add_argument("--update-forward-baseline")
    parser.add_argument("--baseline-origin")
    parser.add_argument("--approved-change")
    parser.add_argument("--report-json")
    parser.add_argument("--candidate-expectations")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    destination_issues = validate_report_destination(args.report_json)
    if destination_issues:
        _print_findings(destination_issues)
        return 1
    if args.report_json and (
            args.write_forward_baseline or args.update_forward_baseline):
        findings = [issue(
            "MODE_CONFLICT",
            "--report-json cannot write or update a baseline.")]
        _print_findings(findings)
        return 1

    try:
        sources = load_source_corpus()
        candidate_expectations, activity_expectations = _load_expectations(
            args.candidate_expectations)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _print_findings([issue(
            "INPUT_PARSE_FAILED", f"Could not load content/expectations: {exc}")])
        return 1

    safe_candidate_ids = corpus_stable_id_set(sources)
    baseline = None
    baseline_findings = []
    if not args.write_forward_baseline:
        baseline, baseline_findings = load_forward_baseline(
            args.update_forward_baseline or FORWARD_BASELINE_PATH)
    origin_ids = (
        safe_candidate_ids
        if args.write_forward_baseline or baseline is None or baseline_findings
        else stable_id_set(baseline))
    nonbaseline, existing = validate_nonbaseline_repository(
        sources, origin_ids, candidate_expectations, activity_expectations)
    unsafe_content = any(
        finding.get("code") in CONTENT_SHAPE_CODES or
        finding.get("code") == "SOURCE_PARSE_FAILED"
        for finding in nonbaseline
        if isinstance(finding, dict))
    if unsafe_content:
        findings = list(baseline_findings) + nonbaseline
        if args.report_json == "-":
            print(canonical_json({
                "formatVersion": 1,
                "counts": existing["summary"],
                "validation": {
                    "valid": False,
                    "errors": findings,
                    "warnings": [],
                },
            }), end="")
        else:
            if args.write_forward_baseline:
                print("Forward baseline was not created.")
            elif args.update_forward_baseline:
                print("Forward baseline was not updated.")
            else:
                print("CONTENT VALIDATION")
            _print_findings(findings)
        return 1

    try:
        candidate = build_repo_candidate(sources)
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        findings = list(baseline_findings) + nonbaseline + [issue(
            "CANDIDATE_BUILD_FAILED",
            f"Could not build deterministic content snapshot: "
            f"{type(exc).__name__}: {exc}")]
        if args.report_json == "-":
            print(canonical_json({
                "formatVersion": 1,
                "counts": existing["summary"],
                "validation": {
                    "valid": False,
                    "errors": findings,
                    "warnings": [],
                },
            }), end="")
        else:
            _print_findings(findings)
        return 1
    if args.write_forward_baseline:
        findings = initial_creation_guards(
            args.write_forward_baseline, args.baseline_origin)
        findings.extend(nonbaseline)
        if findings:
            print("Forward baseline was not created.")
            _print_findings(findings)
            return 1
        findings.extend(write_json_atomic(
            args.write_forward_baseline, candidate, replace=False))
        if findings:
            _print_findings(findings)
            return 1
        print(canonical_json({
            "mode": "created-forward-baseline",
            "path": args.write_forward_baseline,
            **_baseline_summary(candidate),
        }), end="")
        return 0

    if args.update_forward_baseline:
        findings = list(baseline_findings)
        if os.path.abspath(args.update_forward_baseline) != os.path.abspath(
                FORWARD_BASELINE_PATH):
            findings.append(issue(
                "BASELINE_PATH_UNEXPECTED",
                f"Forward baseline path must be {FORWARD_BASELINE_PATH}.",
                args.update_forward_baseline))
        findings.extend(nonbaseline)
        if baseline is None:
            print("Forward baseline was not updated.")
            _print_findings(findings)
            return 1
        update_findings, delta = update_forward_baseline_file(
            args.update_forward_baseline, baseline, candidate,
            args.approved_change, findings)
        if update_findings:
            print("Forward baseline was not updated.")
            _print_findings(update_findings)
            return 1
        updated, updated_findings = load_forward_baseline(
            args.update_forward_baseline)
        print(canonical_json({
            "mode": "updated-forward-baseline",
            "path": args.update_forward_baseline,
            "approvedChange": args.approved_change.strip(),
            "delta": delta,
            "result": _baseline_summary(updated),
            "validationErrorCodes": sorted(issue_codes(updated_findings)),
        }), end="")
        return 0

    comparison_findings = []
    if baseline is not None and not baseline_findings:
        comparison_findings, _ = compare_forward_baseline(
            baseline, candidate, allow_delta=False)
    findings = baseline_findings + comparison_findings + nonbaseline

    if args.report_json == "-":
        report = build_inventory(
            sources, baseline if isinstance(baseline, dict) else None,
            baseline_findings + comparison_findings)
        report["validation"] = {
            "valid": not findings,
            "errors": findings,
            "warnings": [
                issue(_legacy_issue_code(message), message, severity="warning")
                for message in existing["warnings"]
            ],
        }
        print(canonical_json(report), end="")
        return 0 if not findings else 1

    print("=" * 60)
    print("CONTENT VALIDATION")
    print("=" * 60)
    summary = existing["summary"]
    print(
        f"levels={summary['levels']} topics={summary['topics']} "
        f"cards={summary['cards']} drills={summary['drills']}")
    print(
        f"unique ids: {summary['uniqueIds']} "
        f"(topics={summary['topicIds']} cards={summary['cardIds']})")
    if isinstance(baseline, dict):
        print(
            "forward baseline: "
            f"{len(baseline.get('stableIds', []))} ids, "
            f"{len(baseline.get('wording', []))} wording, "
            f"{len(baseline.get('policy', []))} policy, "
            f"{len(baseline.get('structure', []))} structure, "
            f"sha256={baseline.get('contentSha256')}")
    if existing["warnings"]:
        print(f"\n{len(existing['warnings'])} warning(s):")
        for warning in existing["warnings"]:
            print("  -", warning)
    if findings:
        print(f"\n{len(findings)} ERROR(S):")
        _print_findings(findings)
        print("\nFAIL")
        return 1
    print("\nAll content-integrity and forward-baseline checks passed. OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
