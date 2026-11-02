#!/usr/bin/env python3
"""Why only some guns start a reload from the empty path: fields shared by the guns that reloaded and different on all that did not. py -3 -I an_reload_diff.py <vars.jsonl>"""
import json, sys

YES = ["Volt SMG", "Devotion LMG"]
NO = ["R-301 Carbine", "R-99 SMG", "M600 Spitfire", "P2020", "Wingman", "L-STAR EMG", "EVA-8 Auto", "G7 Scout", "Hemlok Burst AR"]
seen = {}
for l in open(sys.argv[1], encoding="utf-8"):
    try: d = json.loads(l)
    except ValueError: continue
    v = d.get("v") or {}
    n = v.get("printname")
    if n in YES + NO and n not in seen: seen[n] = v
print("found", list(seen))
for k in sorted(seen[YES[0]]):
    ys = {str(seen[n].get(k)) for n in YES if n in seen}
    ns = {str(seen[n].get(k)) for n in NO if n in seen}
    if not ys & ns:
        print(k, "YES", sorted(ys)[:3], "NO", sorted(ns)[:4])
print("--- reload fields")
for k in sorted(seen[YES[0]]):
    if "reload" in k.lower() or "autoreload" in k.lower():
        print(k, [str(seen[n].get(k))[:8] for n in YES + NO if n in seen])
