"""Merge the N4-A setfile read-back sessions into one table per legend.

  py -3 classvars_by_legend.py <data dir> <out.csv>

Reads every <data dir>/*N4A_classvars*/platform/logs/client/*/message*.log, takes the
legend from runner.json, and writes key, then one column per legend, then 'varies'
(true when the legends disagree). Standard library only.
"""
import csv
import glob
import json
import os
import re
import sys

CV = re.compile(r"\[CLASSVAR\] (\w+) = (.*?) \(type=(\d+) off=(\d+)\)")


def main(data, out):
    table, legends = {}, []
    for d in sorted(glob.glob(os.path.join(data, "*N4A_classvars*"))):
        if d.endswith("_game") or not os.path.exists(os.path.join(d, "runner.json")):
            continue
        with open(os.path.join(d, "runner.json"), encoding="utf-8") as fh:
            legend = (json.load(fh).get("legend") or "gibraltar").replace("character_", "")
        vals = {}
        for f in glob.glob(os.path.join(d, "platform", "logs", "client", "*", "message*.log")):
            with open(f, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    m = CV.search(line)
                    if m:
                        vals[m.group(1)] = m.group(2)
        if not vals:
            continue
        legends.append(legend)
        for k, v in vals.items():
            table.setdefault(k, {})[legend] = v
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["key"] + legends + ["varies"])
        for k in sorted(table):
            row = [table[k].get(lg, "") for lg in legends]
            w.writerow([k] + row + [len(set(row)) > 1])
    varies = sum(1 for k in table if len({table[k].get(lg, "") for lg in legends}) > 1)
    print(f"legends {len(legends)}: {', '.join(legends)}; keys {len(table)}; varying {varies}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
