"""M10 track R loader: the M6-A2 raw-log loader (../../m6/a2_climb/a2_load.py, imported unchanged) plus the M10 logger lines.

load(folder) -> a2_load.load(folder) and, per scored trial:
  grc  client [M10-GRC] lines of the run (fc, t, act, att, pull, hook (x, y, z), eye, zip), sorted by fc
  grs  dedi [M10-GRS] lines of the run (t, act, att, pull, hook, o, v, eye, gnd), sorted by t (dedi frames, 10 Hz here)
  pitch per usercmd (from the joined client HSD frame, matched by game time t)
and session-wide:
  classvars  {key: value string} from the client [CLASSVAR] lines (bridge_classvar_get census; unknown keys -> None)
stdlib only; no local paths (the folder comes from the caller).
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

KV_RE = re.compile(r"(\w+)=(\S+)")
CV_RE = re.compile(r"\[CLASSVAR\] (\w+) = (.*?) \(type=")
CVU_RE = re.compile(r"\[CLASSVAR\] unknown key '(\w+)'")


def _f3(s):
    return tuple(float(x) for x in s.split(","))


def _b(s):
    return s == "true"


def parse_tag(folder, side, stem, tag):
    out = {}
    for f in sorted(L._files(folder, side, stem)):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if tag not in raw:
                    continue
                body = raw.split(tag, 1)[1]
                if " error " in body:
                    continue
                kv = dict(KV_RE.findall(body))
                if "run" not in kv:
                    continue
                out.setdefault(int(kv["run"]), []).append(kv)
    return out


def classvars(folder):
    cv = {}
    for f in sorted(L._files(folder, "client", "message")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[CLASSVAR]" not in raw:
                    continue
                m = CV_RE.search(raw)
                if m:
                    cv[m.group(1)] = m.group(2).strip()
                    continue
                m = CVU_RE.search(raw)
                if m:
                    cv.setdefault(m.group(1), None)
    return cv


def load(folder):
    D = L.load(folder)
    grc = parse_tag(folder, "client", "script", "[M10-GRC]")
    grs = parse_tag(folder, "server", "script", "[M10-GRS]")
    for T in D["trials"]:
        rows = []
        for kv in grc.get(T["run"], []):
            rows.append({"fc": int(kv["fc"]), "t": float(kv["t"]), "act": _b(kv["act"]), "att": _b(kv["att"]),
                         "pull": _b(kv["pull"]), "hook": _f3(kv["hook"]), "eye": float(kv["eye"]), "zip": _b(kv.get("zip", "false"))})
        rows.sort(key=lambda r: r["fc"])
        T["grc"] = rows
        srows = []
        for kv in grs.get(T["run"], []):
            srows.append({"t": float(kv["t"]), "act": _b(kv["act"]), "att": _b(kv["att"]), "pull": _b(kv["pull"]),
                          "hook": _f3(kv["hook"]), "o": _f3(kv["o"]), "v": _f3(kv["v"]), "gnd": _b(kv["gnd"])})
        srows.sort(key=lambda r: r["t"])
        T["grs"] = srows
        by_t = {round(f["t"], 5): f for f in T["frames"]}
        for c in T["cmds"]:
            f = by_t.get(round(c["t"], 5)) if c.get("t") is not None else None
            c["pitch"] = f.get("pitch") if f else None
    D["classvars"] = classvars(folder)
    return D
