"""Smoke-run checks from the client per-frame log (HSDDIAG C), segmented by the server's
TAG times: frame rate, ground speed while walking forward, stop and no-input deceleration,
jump take-off speed. Usage: python -I analyze_smoke.py <run dir>"""
import statistics
import sys
from pathlib import Path


def load(run):
    frames, tags = [], []
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8").splitlines():
        p = line.split()
        if len(p) > 13 and p[1] == "C":
            t, ox, oy, oz, vx, vy, vz = map(float, p[2:9])
            frames.append(dict(t=t, z=oz, vz=vz, h=(vx * vx + vy * vy) ** 0.5, ground=p[11] == "1"))
        elif len(p) > 3 and p[1] == "TAG":
            tags.append((float(p[3]), p[2]))
    for f in frames:
        f["tag"] = "-"
        for t, name in tags:
            if f["t"] >= t:
                f["tag"] = name
    return frames


def rates(seg, sign, label, n=10):
    mv = [k for k in seg if k["h"] > 1][: n + 1]
    vals = []
    for a, b in zip(mv, mv[1:]):
        dt = b["t"] - a["t"]
        if dt > 0:
            vals.append(sign * (b["h"] - a["h"]) / dt)
    if vals:
        print(f"  {label}: median {statistics.median(vals):.1f} u/s^2 over {len(vals)} frames "
              f"(h {mv[0]['h']:.1f} -> {mv[-1]['h']:.1f})")


def main():
    fr = load(sys.argv[1])
    dts = [b["t"] - a["t"] for a, b in zip(fr, fr[1:]) if b["t"] > a["t"]]
    print(f"client frames {len(fr)}; median dt {statistics.median(dts) * 1000:.2f} ms "
          f"({1 / statistics.median(dts):.1f} fps); p95 {sorted(dts)[int(0.95 * len(dts))] * 1000:.2f} ms")
    for tag in ("forward", "stop", "jump", "kick_decel"):
        seg = [k for k in fr if k["tag"] == tag]
        if not seg:
            print(f"[{tag}] no frames")
            continue
        print(f"[{tag}] {len(seg)} frames {seg[0]['t']:.3f}-{seg[-1]['t']:.3f}; max h {max(k['h'] for k in seg):.2f}")
        if tag == "forward":
            rates(seg, 1, "accel")
            print(f"  plateau h {statistics.median(k['h'] for k in seg[-20:]):.3f}")
        elif tag in ("stop", "kick_decel"):
            rates(seg, -1, "decel")
        elif tag == "jump":
            air = [k for k in seg if not k["ground"]]
            if air:
                i = seg.index(air[0])
                pre = seg[i - 1] if i else air[0]
                print(f"  first air vz {air[0]['vz']:.3f} (prev {pre['vz']:.3f}); peak z gain "
                      f"{max(k['z'] for k in seg) - seg[0]['z']:.3f}; air {air[-1]['t'] - air[0]['t']:.3f} s")


if __name__ == "__main__":
    main()
