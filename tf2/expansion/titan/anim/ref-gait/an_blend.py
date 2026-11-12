"""Sequence changes and how long the crossfade lasts, from the body re-pose pattern.

Outside a crossfade the local titan body is re-posed ~20 Hz (every ~7th client frame); while two sequences are
blended it is re-posed every client frame (runs gait_a / gait_b). A crossfade = a stretch of consecutive
re-poses < 0.02 s apart. Its start is the sequence change, its length is the blend time.
Usage: py -3 -I an_blend.py <run> <tag prefix> <command that starts the event: +forward | +speed | -forward>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gaitlib import anim_updates, between, load, speed2d, tag_windows  # noqa: E402


def blends(G, gap=0.02, min_len=4):
    out, cur = [], [G[0]]
    for a, b in zip(G, G[1:]):
        if b["t"] - a["t"] < gap:
            cur.append(b)
        else:
            if len(cur) >= min_len:
                out.append((cur[0]["t"], cur[-1]["t"]))
            cur = [b]
    if len(cur) >= min_len:
        out.append((cur[0]["t"], cur[-1]["t"]))
    return out


def main():
    run = load(sys.argv[1])
    pre, cmd = sys.argv[2], sys.argv[3]
    for name, t0, t1 in tag_windows(run):
        if not name.startswith(pre):
            continue
        tc = next((t for t, c in run["cmds"] if t0 - 0.01 <= t < t1 + 0.5 and c == cmd), None)
        if tc is None:
            continue
        G = anim_updates(between(run["GC"], tc - 0.2, tc + 2.0))
        C = between(run["C"], tc - 0.2, tc + 2.0)
        bl = [b for b in blends(G) if b[1] > tc]
        def v_at(t):
            return speed2d(min(C, key=lambda c: abs(c["t"] - t))["v"])
        desc = "  ".join("%.3f..%.3f (%.3f s, v %.0f->%.0f)" % (a - tc, b - tc, b - a, v_at(a), v_at(b)) for a, b in bl[:3])
        print("%-12s %s at 0: %s" % (name, cmd, desc or "-"))


if __name__ == "__main__":
    main()
