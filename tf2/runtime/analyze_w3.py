"""W3 analysis (2026-10-29). Usage: python -I analyze_w3.py <run dir> [rewind|npc|smart]
rewind: per hsd_w3_rewind use, the buffer, the path the server reports, phase time, end spot,
velocity and view after (client frames)."""
import sys
from pathlib import Path


def rows(run):
    for line in (Path(run) / "diag.tsv").read_text(encoding="utf-8").splitlines():
        yield line.split()


def rewind(run):
    uses, cur, tag = [], None, "-"
    client = []
    for p in rows(run):
        k = p[1] if len(p) > 1 else ""
        if k == "TAG":
            tag = p[2]
        elif k == "W3RW":
            cur = {"label": p[2], "t": float(p[3]), "n": int(p[4][2:]), "now": tuple(map(float, p[6:9])), "buf": [],
                   "watch": [], "tag": tag}
            if p[2] == "use":
                uses.append(cur)
        elif k == "W3RWB" and cur is not None:
            cur["buf"].append((int(p[2]), tuple(map(float, p[3:6])), float(p[7]), tuple(map(float, p[9:12])), p[13]))
        elif k == "W3RWT" and uses:
            uses[-1]["watch"].append((float(p[2]), tuple(map(float, p[3:6])), (float(p[7]), float(p[8])),
                                      tuple(map(float, p[10:13])), int(p[14]), int(p[16])))
        elif k == "C":
            client.append((float(p[2]), tuple(map(float, p[3:6])), tuple(map(float, p[6:9])), float(p[10]), p[11]))
    for u in uses:
        print("== %s  t=%.3f  n=%d  now=%s" % (u["tag"], u["t"], u["n"], u["now"]))
        for b in u["buf"]:
            print("   buf %2d %s yaw %.1f vel %s crouch %s" % b)
        w = u["watch"]
        ph = [x for x in w if x[4]]
        par = [x for x in w if x[5]]
        if ph:
            print("   phase on %.3f .. %.3f (%.2f s server samples)" % (ph[0][0], ph[-1][0], ph[-1][0] - ph[0][0]))
        if par:
            print("   parented %.3f .. %.3f (%.2f s)" % (par[0][0], par[-1][0], par[-1][0] - par[0][0]))
        for x in w[::3]:
            print("   sv %.3f pos %s ang %s vel %s phase %d parent %d" % x)
        end = par[-1][0] if par else u["t"]
        after = [c for c in client if end < c[0] < end + 1.0]
        if after:
            c0 = after[0]
            print("   client after: t %.3f pos %s vel %s yaw %.1f ground %s" % c0)
            c1 = after[-1]
            print("   client +1s:   t %.3f pos %s vel %s yaw %.1f ground %s" % c1)
        if u["buf"]:
            o = u["buf"][0][1]
            print("   oldest buf %s; end-oldest %s" % (o, tuple(round(a - b, 1) for a, b in zip(w[-1][1], o)) if w else ""))


def npc(run):
    """turrets / ticks: per tag, hits on the player (time, damage, gap), NPC samples (every 5th), spawn lines.
    The tag is switched by the client CMD line (the server TAG line can lag a frame)."""
    tag, hits, samples = "-", {}, {}
    for p in rows(run):
        k = p[1] if len(p) > 1 else ""
        if k == "TAG":
            tag = p[2]
        elif k in ("W3TUR", "W3TICK", "W3KILL", "NPC"):
            print(tag, " ".join(p[1:]))
        elif k == "DMG":
            hits.setdefault(tag, []).append((float(p[2]), float(p[3]), p[-1], int(p[-2])))
        elif k == "W3DMG":
            print(tag, " ".join(p[1:]))
        elif k == "W3NPC":
            samples.setdefault(tag, []).append(p[2:])
    for t in sorted(set(hits) | set(samples), key=lambda x: (min([h[0] for h in hits.get(x, [])] +
                                                                  [float(s[0]) for s in samples.get(x, [])]))):
        h = hits.get(t, [])
        print("== %s: %d hits on the player" % (t, len(h)))
        if h:
            gaps = [round(b[0] - a[0], 3) for a, b in zip(h, h[1:])]
            print("   first %.3f last %.3f  damage %s" % (h[0][0], h[-1][0], sorted(set(round(x[1], 2) for x in h))))
            print("   inflictors %s  hp after last %d" % (sorted(set(x[2] for x in h)), h[-1][3]))
            print("   gaps %s" % gaps[:60])
        for s in samples.get(t, [])[::5]:
            print("   " + " ".join(s))


def smart(run):
    """per tag: lock fraction over time per target (W3SM, server 10 Hz), hits on targets (NDMG),
    shots fired (client attack held) and the spawn / hp lines."""
    tag, sm, dmg = "-", {}, {}
    for p in rows(run):
        k = p[1] if len(p) > 1 else ""
        if k == "TAG":
            tag = p[2]
        elif k == "W3SM":
            t = float(p[2])
            for x in p[4:]:
                name, frac, dist = x.split(":")
                sm.setdefault(tag, {}).setdefault(name, []).append((t, float(frac), float(dist)))
        elif k == "NDMG":
            dmg.setdefault(tag, []).append((float(p[2]), p[3], float(p[4]), float(p[5]), p[7]))
        elif k in ("NPC", "NHP", "NDEAD") and p[2] not in ("list",):
            print(tag, " ".join(p[1:]))
    for t in list(dict.fromkeys(list(sm) + list(dmg))):
        print("== " + t)
        for name, xs in sm.get(t, {}).items():
            t0 = xs[0][0]
            first_full = next((x[0] for x in xs if x[1] >= 1.0), None)
            print("   %s dist %.0f: first seen %.3f, frac %s, reaches 1 at %s, max %.3f" % (
                name, xs[0][2], t0, [round(x[1], 2) for x in xs[:12]],
                "%.3f (+%.2f s)" % (first_full, first_full - t0) if first_full else "-", max(x[1] for x in xs)))
        d = dmg.get(t, [])
        if d:
            print("   hits %d: %s" % (len(d), [(round(x[0], 3), x[1], x[2], x[3]) for x in d]))


if __name__ == "__main__":
    {"rewind": rewind, "npc": npc, "smart": smart}[sys.argv[2] if len(sys.argv) > 2 else "rewind"](sys.argv[1])
