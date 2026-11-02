#!/usr/bin/env python3
"""Run a cases file: tag|weapon|mods|schedule|k=v k=v  (# comments). Skips tags already in marks. py -3 -I batch.py <cases> <marks> <runs dir>"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gm_run

def main():
    cases, marks, runs = sys.argv[1:4]
    done = set()
    if os.path.exists(marks):
        done = {l.split("\t")[0] for l in open(marks, encoding="utf-8")}
    fails = 0  # a dead client shows up as timeouts, not as a refused connection
    for l in open(cases, encoding="utf-8"):
        l = l.strip()
        if not l or l.startswith("#"): continue
        tag, weap, mods, sched, *kv = [x.strip() for x in l.split("|")]
        if tag in done: continue
        k = dict(a.split("=", 1) for a in (kv[0].split() if kv else []))
        try:
            rep, pl = gm_run.run(marks, runs, tag, "mp_weapon_" + weap if not weap.startswith("mp_") else weap, mods, sched, k)
            bad = [x[:100] for x in pl.lines["c"] + pl.lines["s"] if " err" in x]
            print(tag, str(rep)[:60], len(pl.lines["c"]), bad[:1], flush=True)
            fails = 0
        except Exception as e:
            print(tag, "EXC", repr(e)[:200], flush=True)
            fails += 1
            if "not running" in repr(e) or "connect" in repr(e).lower() or fails >= 2: print("HOST_DOWN", flush=True); sys.exit(3)
    print("BATCH_DONE", flush=True)

if __name__ == "__main__":
    main()
