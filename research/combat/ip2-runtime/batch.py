#!/usr/bin/env python3
"""Run a list of gun.nut cases and print one compact line each: shots, cadence, hits, damage by hit group, drop.

  python -I batch.py <case file>
Case file lines:  tag | weapon | target dist lift | mods | schedule | secs
heat is read when the weapon is the nemesis. Raw runs land in runs/ as usual.
"""
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
num = r"(-?[\d.]+)"


def summarize(path, dist, lift):
    txt = open(path, encoding="utf-8").read()
    head = next((l for l in txt.splitlines() if l.startswith("server:")), "")
    if "err=" in head or "'error': True" in head:
        return "SNIPPET ERROR " + head[:200]
    clips = [(float(a), int(b)) for a, b in re.findall(r"\[RT\] cl t=" + num + " c=(\d+)", txt)] or         [(float(a), int(b)) for a, b in re.findall(r"\[RT\] clip t=" + num + " c=(\d+)", txt)]
    shots = [t for (t, c), (_, p) in zip(clips[1:], clips[:-1]) if c < p]
    ev = re.findall(r"\[RT\] dmg t=" + num + " amt=" + num + " hg=(\d+) src=\d+ dist=" + num + " type=\d+ pos=" + num + "," + num + "," + num, txt)
    eye = re.search(r"eo=" + num + "," + num + "," + num, txt)
    by = {}
    drops = []
    for t, amt, hg, d, x, y, z in ev:
        by.setdefault((hg, amt), 0)
        by[(hg, amt)] += 1
        if eye:
            ex, ez = float(eye.group(1)), float(eye.group(3))
            fx = (float(x) - ex) / max(1.0, float(dist))
            drops.append(ez + float(lift) * fx - float(z))
    gaps = [round(b - a, 3) for a, b in zip(shots, shots[1:])]
    parts = [f"shots={len(shots)}", f"hits={len(ev)}"]
    if gaps:
        s = sorted(gaps)
        parts.append(f"gap med={s[len(s) // 2]} min={s[0]} max={s[-1]} seq={','.join(str(g) for g in gaps[:32])}")
    parts.append("dmg " + " ".join(f"hg{k[0]}:{k[1]}x{v}" for k, v in sorted(by.items())))
    if drops:
        s = sorted(drops)
        parts.append(f"drop med={s[len(s) // 2]:.1f} [{s[0]:.1f},{s[-1]:.1f}]")
    m = re.search(r"grav=" + num + " v=" + num, head)
    if m:
        parts.append(f"grav={m.group(1)} v={m.group(2)}")
    errs = re.findall(r"\[RT\] err .*|SCRIPT ERROR.*", txt)
    if errs:
        parts.append("ERR " + errs[0][:120])
    return " ".join(parts)


def main():
    py = sys.executable
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tag, weap, tgt, mods, sched, secs = [x.strip() for x in line.split("|")]
        target, dist, lift = tgt.split()
        heat = "w.GetHeatValue()" if "nemesis" in weap else "0.0"
        args = [py, "-I", os.path.join(HERE, "run.py"), tag, "gun.nut", secs, sched, f"weap={weap}", f"mods={mods}",
                "yaw=0", f"snap={0 if target == 'none' else 1}", f"heat={heat}", "track=0", f"target={target}", f"dist={dist}", f"lift={lift}", "stock=300"]
        try:
            subprocess.run(args, capture_output=True, text=True, timeout=float(secs) + 30)
        except subprocess.TimeoutExpired:
            print(tag, "TIMEOUT (host hung?)")
            continue
        found = sorted(glob.glob(os.path.join(HERE, "runs", f"*_{tag}.txt")))
        if not found:
            print(tag, "NO RUN (server or client gone)", flush=True)
            continue
        path = found[-1]
        print(tag, summarize(path, dist, lift), flush=True)


if __name__ == "__main__":
    main()
