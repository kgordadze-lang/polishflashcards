#!/usr/bin/env python3
"""
Po polsku - validate_content.py

Reusable content-integrity validator for the lesson data. Reuses build_pages.py's
json5-based `load_levels` so it needs no browser/node - just `pip install json5`.

Checks (fatal = non-zero exit):
  IDENTITY
    - every level / topic / card / drill has an explicit `id`
    - ids are lowercase ASCII [a-z0-9-] only
    - ids are unique within their kind AND globally
    - relatedIds (when present) resolve to existing card ids
  STRUCTURE (parity with the Phase-0 baseline audit)
    - no card missing `pl` / `en`
    - no duplicate `pl` or `en` within a topic
    - `choose` drills: answer is one of the options
    - `build` drills: no duplicated answer tokens
    - optional build `acceptedOrders` preserve the keyed tile multiset and change order
    - scenario `goto` destinations all resolve; no unreachable scenes
  SENSE GROUPS (Phase 4E, optional `senseGroups` metadata)
    - non-empty array of unique, non-blank, untrimmed-free lowercase-kebab keys
    - every group names at least two distinct cards
  MIGRATION MAPS (when pp-migrate.js is present)
    - PP_MIGRATE.LEGACY.topics values resolve to existing topic ids
    - PP_MIGRATE.LEGACY.cards[topicId] keys map to existing card id(s)

Reports (informational, never fatal): slash `pl`, ellipsis/template `pl`,
parenthesis `pl`, template cards, recognition-only cards.

Run from the project root:   python3 validate_content.py
Exit 0 = all fatal checks pass.
"""
import glob, hashlib, json, os, re, sys
from collections import Counter

import json5  # noqa: F401  (used transitively by load_levels)
import pp_audio_rule
from pp_audio_rule import load_levels, fix_surrogates

DATA_GLOB = "data-*.js"
ID_RE = re.compile(r"^[a-z0-9-]+$")
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
    return t.get("kind") or "unknown"


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


def check_frozen_snapshot(levels, all_ids, topic_ids, card_ids, mig_target):
    """Guard the two things Phase 4+ must never silently break:

    1. IDS ARE PERMANENT. Every id that existed at the end of Phase 3 must still exist -
       a wording correction must never renumber, regenerate or drop an id.
    2. PROGRESS SURVIVES A WORDING CHANGE. Every exact Phase-0 production `pl` must still
       resolve to a current card id, either because the wording is unchanged or because
       PP_MIGRATE.LEGACY maps it. This is what catches a corrected `pl` that was shipped
       without its legacy entry - i.e. silently orphaned learner progress.

    Snapshot lives in reports/priority-0-frozen-snapshot.json (see its _comment)."""
    path = os.path.join("reports", "priority-0-frozen-snapshot.json")
    if not os.path.exists(path):
        warn(f"[frozen] {path} not found - skipping id/legacy regression checks")
        return None
    snap = json.load(open(path, encoding="utf-8"))

    missing = [i for i in snap.get("phase3Ids", []) if i not in all_ids]
    if missing:
        err(f"[frozen] {len(missing)} id(s) from the end of Phase 3 no longer exist "
            f"(ids are permanent - never renumber for a wording fix): {missing[:10]}")

    exp = snap.get("expectedMigrationRevision")
    if exp is not None and mig_target is not None and mig_target != exp:
        err(f"[frozen] CONTENT_MIGRATION_REVISION is {mig_target}, snapshot expects {exp}. "
            f"Ordinary wording corrections must NOT add a revision; if a structural change "
            f"really was approved, update expectedMigrationRevision deliberately.")

    # current wording index, mirroring PP_MIGRATE.buildContext / resolveCardIds
    tid_by_key, cur = {}, {}
    for L in levels:
        for t in L.get("topics", []):
            if not t.get("id") or "cards" not in t:
                continue
            tid_by_key[f"{L.get('level')}|{t.get('name')}"] = t["id"]
            rec = {"pl": set(), "intro": set()}
            for c in t["cards"]:
                if not c.get("id") or not c.get("pl"):
                    continue
                (rec["intro"] if c.get("intro") else rec["pl"]).add(c["pl"])
            cur[t["id"]] = rec

    legacy = load_legacy()
    lt, lc, lr = (legacy.get("topics") or {}), (legacy.get("cards") or {}), (legacy.get("retired") or {})
    unresolved, checked = [], 0
    for key, pls in (snap.get("phase0Cards") or {}).items():
        tid = tid_by_key.get(key) or lt.get(key)
        if not tid:
            err(f"[frozen] Phase-0 topic {key!r} no longer resolves to a topic id "
                f"(add LEGACY.topics[{key!r}] = \"<topicId>\" if it was renamed)")
            continue
        rec, mp = cur.get(tid, {"pl": set(), "intro": set()}), (lc.get(tid) or {})
        for pl in pls:
            checked += 1
            if pl in mp or pl in rec["pl"] or pl in rec["intro"] or pl in (lr.get(tid) or []):
                continue
            unresolved.append((tid, pl))
    for tid, pl in unresolved:
        err(f"[frozen] Phase-0 wording {pl!r} in {tid} no longer resolves - its `pl` changed "
            f"without a legacy entry. Add LEGACY.cards[{tid!r}][{pl!r}] = [\"<cardId>\"].")
    return (f"frozen: {len(snap.get('phase3Ids', []))} Phase-3 ids present, "
            f"{checked} Phase-0 wording(s) resolve, {len(unresolved)} orphaned")


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


def main():
    levels = load_all_levels()

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

    # frozen integrity snapshot: ids never disappear, and every Phase-0 wording still resolves
    frozen_summary = check_frozen_snapshot(levels, all_ids, topic_ids, card_ids, mig_target)
    # Phase-5 usage labels + eligibility wiring
    usage_tally = check_usage_labels(levels)
    # Phase-6 correction: incomplete template pl is never main-card audio
    audio_tally = check_main_audio(levels)

    # ---- report ----
    print("=" * 60)
    print("CONTENT VALIDATION")
    print("=" * 60)
    print(f"levels={n_lvl} topics={n_top} cards={n_card} drills={n_drill}")
    print(f"unique ids: {len(all_ids)}  (topics={len(topic_ids)} cards={len(card_ids)})")
    if mig_target is not None:
        print(f"migration: CONTENT_MIGRATION_REVISION={mig_target}  REVISIONS={mig_revs or '[]'}")
    if os.path.exists("pp-migrate.js"):
        print(f"legacy maps: {legacy_topics} topic mapping(s), {legacy_cards} card mapping(s)")
    if frozen_summary:
        print(frozen_summary)
    if usage_tally:
        print("usage metadata: " + "  ".join(f"{k}={v}" for k, v in sorted(usage_tally.items())))
    if audio_tally:
        print("main-card audio: " + "  ".join(f"{k}={v}" for k, v in sorted(audio_tally.items())))
    print(f"accepted build orders: {accepted_build_drills} drill(s), "
          f"{accepted_build_orders} order(s)")
    # Phase-4E: reported, never pinned. The number of groups is an editorial
    # decision that is allowed to grow as glosses are reviewed, so asserting it
    # here would only make honest content work fail the validator.
    if sense_groups:
        grouped_cards = set()
        for members in sense_groups.values():
            grouped_cards |= members
        print(f"sense groups: {len(sense_groups)} group(s) over {len(grouped_cards)} card(s)")
        for gkey, members in sorted(sense_groups.items()):
            print(f"  {gkey}: " + ", ".join(sorted(members)))

    print(f"\ninfo: slash-pl={len(slash_pl)}  ellipsis-pl={len(ellipsis_pl)}  "
          f"paren-pl={len(paren_pl)}  templates={len(templates)}  recognition-only={len(recognition)}")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings: print("  -", w)

    if errors:
        print(f"\n{len(errors)} ERROR(S):")
        for e in errors: print("  x", e)
        print("\nFAIL")
        sys.exit(1)
    print("\nAll content-integrity checks passed. OK")


if __name__ == "__main__":
    main()
