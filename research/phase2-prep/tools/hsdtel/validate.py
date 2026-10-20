"""Data-quality checks on parsed + derived rows. Returns Issue lists; severities:
error (data unusable as-is), warning (usable with care), info (expected/benign)."""
import math
from collections import Counter

from .parse import Issue
from .schema import HSD_REQUIRED
from .derive import streams


def validate(rows, parse_issues, min_join=0.9):
    issues = list(parse_issues)
    mt = [r for r in rows if r["source"] == "MT"]
    hsd = [r for r in rows if r["source"] == "HSD"]
    if not mt:
        issues.append(Issue("info", "I_NO_MT", "", 0, "no [MOVE-TRACE] rows (bridge_move_trace off or wrong log file?)"))
    if not hsd:
        issues.append(Issue("info", "I_NO_HSD", "", 0, "no [HSD-MD] rows (mod not loaded or wrong log file?)"))

    # Required keys and contained script errors
    for r in hsd:
        req = HSD_REQUIRED.get(r.get("kind"))
        kv = r.get("_kv", {})
        if req is None:
            issues.append(Issue("warning", "W_HSD_KIND", r["file"], r["line_no"], f"unknown kind={r.get('kind')}"))
        elif r.get("_ver") == "2":
            missing = [k for k in req if k not in kv]
            if missing:
                issues.append(Issue("error", "E_MISSING_FIELD", r["file"], r["line_no"],
                                    f"kind={r['kind']} missing {','.join(missing)}"))
        if r.get("kind") == "error":
            issues.append(Issue("warning", "W_SCRIPT_ERROR", r["file"], r["line_no"],
                                f"mod contained an error where={kv.get('where')}: {kv.get('msg', '')[:120]}"))
        if r.get("kind") == "setting" and r.get("vtype") == "ERR":
            issues.append(Issue("info", "I_SETTING_ERR", r["file"], r["line_no"], f"settings key {r.get('key')} unreadable"))

    # seq continuity per (file, side) for HSD v2
    per = {}
    for r in sorted(hsd, key=lambda x: (x["_rank"], x["line_no"])):
        if r.get("_ver") != "2" or r.get("seq") is None:
            continue
        k = (r["file"], r["side"])
        last = per.get(k)
        s = int(r["seq"])
        if last is not None:
            if s == last + 1:
                pass
            elif s <= 1 or s < last:
                issues.append(Issue("info", "I_SEQ_RESET", r["file"], r["line_no"], f"seq {last} -> {s} (VM restart/map change)"))
            else:
                issues.append(Issue("warning", "W_SEQ_GAP", r["file"], r["line_no"],
                                    f"{s - last - 1} [HSD-MD] line(s) missing on side {r['side']} (seq {last} -> {s})"))
        per[k] = s

    for key, srows in streams(rows).items():
        source = key[0]
        flags = Counter()
        for r in srows:
            for f in filter(None, (r.get("drv_flags") or "").split("|")):
                flags[f] += 1
                if f in ("nonfinite", "teleport") and flags[f] <= 5:
                    sev = "error" if f == "nonfinite" else "warning"
                    issues.append(Issue(sev, "E_NONFINITE" if f == "nonfinite" else "W_TELEPORT",
                                        r["file"], r["line_no"], f"{f} in stream {key}"))
        if flags.get("api_missing"):
            issues.append(Issue("warning", "W_API_MISSING", srows[0]["file"], srows[0]["line_no"],
                                f"{flags['api_missing']} row(s) with ground/slide=-1 (method unavailable) in {key}"))
        for f in ("nonfinite", "teleport"):
            if flags[f] > 5:
                issues.append(Issue("warning", "W_MORE", srows[0]["file"], 0, f"{flags[f] - 5} more {f} rows in {key}"))
        if source == "MT":
            seen = Counter(r["cmd"] for r in srows if not r.get("replay"))
            dups = [c for c, n in seen.items() if n > 1]
            if dups:
                issues.append(Issue("warning", "W_DUP_CMD", srows[0]["file"], 0,
                                    f"{len(dups)} command number(s) logged twice without rp=1 in {key} (e.g. {dups[:3]})"))
            bursts = len({r.get("drv_burst") for r in srows})
            if bursts > 1:
                issues.append(Issue("info", "I_BURSTS", srows[0]["file"], 0, f"{bursts} command bursts in {key}"))
            nrep = sum(1 for r in srows if r.get("replay"))
            if nrep:
                issues.append(Issue("info", "I_REPLAYS", srows[0]["file"], 0, f"{nrep} re-predicted (rp=1) rows in {key}"))
        else:
            back = 0
            prev = None
            for r in srows:
                t = r.get("t")
                if prev is not None and isinstance(t, float) and math.isfinite(t) and t < prev - 1e-6:
                    back += 1
                    if back <= 3:
                        issues.append(Issue("warning", "W_TIME_BACKWARDS", r["file"], r["line_no"], f"t {prev} -> {t} in {key}"))
                if isinstance(t, float) and math.isfinite(t):
                    prev = t

    # client/server command coverage
    cl = {r["cmd"] for r in mt if r.get("side") == "cl" and not r.get("replay")}
    sv = {r["cmd"] for r in mt if r.get("side") == "sv"}
    if cl and sv:
        ratio = len(cl & sv) / len(cl)
        sev = "info" if ratio >= min_join else "warning"
        issues.append(Issue(sev, "I_JOIN" if sev == "info" else "W_JOIN_LOW", "", 0,
                            f"{ratio:.1%} of client commands have a dedi line with the same cmd ({len(cl & sv)}/{len(cl)})"))
    return issues


def summarize(issues):
    c = Counter(i.severity for i in issues)
    return {"errors": c.get("error", 0), "warnings": c.get("warning", 0), "infos": c.get("info", 0),
            "codes": dict(Counter(i.code for i in issues))}
