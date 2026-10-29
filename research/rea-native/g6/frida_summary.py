#!/usr/bin/env python3
"""G-6: summarise the frida_impact.js messages (a JSON list of the send() payloads) per detach.

  py -3 frida_summary.py frida_impact_out.json
"""
import json
import sys


def main(path):
    msgs = json.load(open(path, encoding="utf-8"))
    det = {}
    for m in msgs:
        if m.get("ev") == "detach":
            det[m["seq"]] = {"d": m, "upd": None, "moves": []}
        elif m.get("ev") == "update_ret" and m["seq"] in det:
            det[m["seq"]]["upd"] = m
        elif m.get("ev") == "move" and m["seq"] in det:
            det[m["seq"]]["moves"].append(m)
    for k in sorted(det):
        e = det[k]
        d = e["d"]
        print("detach %d t=%.3f parent %s pulling %s  vz %.1f -> %.1f  (|vxy| %.0f)" % (
            k, d["t"], d["p148"], d["pulling"], d["vin"][2], d["vout"][2], (d["vout"][0] ** 2 + d["vout"][1] ** 2) ** 0.5))
        if e["upd"]:
            print("   after the grapple update: vz %.1f" % e["upd"]["v"][2])
        for m in e["moves"][:12]:
            print("   move %2d t=%.3f vz %7.1f -> %7.1f  vx %7.1f" % (m["n"], m["t"], m["vin"][2], m["vout"][2], m["vout"][0]))


if __name__ == "__main__":
    main(sys.argv[1])
