"""M9 track R zipline loader: the M6-A2 raw-log loader plus the SDK zipline diag lines of both sides.

load(folder) -> dict from a2_load.load(folder) (cmds / frames / states per scored trial), and per trial:
  cl_zip  client lines [ZIPRAIL-USE] / [ZIP-DISC] / [ZIP-JUMPOFF] with cmd numbers inside the trial's usercmd range
  sv_zip  dedi lines [ZIPRAIL-USE] / [ZIP-MOVESTOP] / [ZIP-DISC] / [ZIP-JUMPOFF] inside the same usercmd range; each dedi
          [ZIPRAIL-FIND] line is attached to the next dedi line that carries a cmd number (the Use it belongs to)
The usercmd range of a trial is [first, last] client first-time MOVE-TRACE cmd of the run (the zipline ride is a gap in
MOVE-TRACE, M6-A3), extended past the last traced usercmd by the number of later client frames (a ride to the trial end). stdlib only; no local paths.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "m6", "a2_climb")))
import a2_load as L  # noqa: E402

TAG_RE = re.compile(r"\[(ZIPRAIL-USE|ZIPRAIL-FIND|ZIP-MOVESTOP|ZIP-DISC|ZIP-JUMPOFF)\]\s*(.*)$")
VEC_RE = re.compile(r"(\w+)=\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)")
KV_RE = re.compile(r"(\w+)=([^\s(]+)")


def _parse_line(tag, body):
    d = {"tag": tag}
    for k, x, y, z in VEC_RE.findall(body):
        d[k] = (float(x), float(y), float(z))
    for k, v in KV_RE.findall(VEC_RE.sub("", body)):
        if k in d:
            continue
        try:
            d[k] = int(v)
        except ValueError:
            try:
                d[k] = float(v)
            except ValueError:
                d[k] = v
    if tag == "ZIP-DISC":
        m = re.match(r"(\S+)", body)
        d["what"] = m.group(1) if m else ""
    return d


def parse_zip(folder, side):
    out, pend = [], []
    for f in sorted(L._files(folder, side, "message")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                if "[ZIP" not in raw:
                    continue
                m = TAG_RE.search(raw)
                if not m:
                    continue
                d = _parse_line(m.group(1), m.group(2))
                if "first call" in m.group(2) or "hook live" in m.group(2) or "unresolved" in m.group(2):
                    continue
                if d["tag"] == "ZIPRAIL-FIND":
                    pend.append(d)
                    continue
                if isinstance(d.get("cmd"), int):
                    if pend:
                        d["finds"] = pend
                        pend = []
                    out.append(d)
    return out


def load(folder):
    D = L.load(folder)
    cl = parse_zip(folder, "client")
    sv = parse_zip(folder, "server")
    for T in D["trials"]:
        cs = [c["cmd"] for c in T["cmds"]]
        lo, hi = (min(cs), max(cs)) if cs else (0, -1)
        # a ride that lasts to the end of the trial leaves no MOVE-TRACE after the mount: extend the range by the client
        # frames after the last traced usercmd (one usercmd per frame)
        tl = max((c["t"] for c in T["cmds"] if c.get("t") is not None), default=None)
        if tl is not None:
            hi += sum(1 for f in T["frames"] if f["t"] > tl + 1e-6) + 2
        T["cmd_range"] = (lo, hi)
        T["cl_zip"] = [d for d in cl if lo <= d["cmd"] <= hi]
        T["sv_zip"] = [d for d in sv if lo <= d["cmd"] <= hi]
    D["zip_lines"] = {"client": len(cl), "server": len(sv)}
    return D
