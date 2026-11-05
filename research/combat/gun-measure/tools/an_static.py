#!/usr/bin/env python3
"""D: fields the client holds at run time for what has no direct probe: jolt, shake, muzzle, tracer, hit size, penetration, flinch, crosshair. No mods. Takes the first dump per weapon name.
  py -3 -I an_static.py <out.tsv> <vars.jsonl> [more vars.jsonl]"""
import json, re, sys

PAT = re.compile(r"jolt|shake|muzzle|tracer|impact_effect|pass_through|penetrat|hitsize|hit_size|bolt_|flinch|aimpunch|crosshair|deploy_time|holster_time|raise_time|lower_time|quick|sprintcycle|sprint_", re.I)


def main():
    out, paths = sys.argv[1], sys.argv[2:]
    seen = {}
    for p in paths:
        for l in open(p, encoding="utf-8"):
            try: d = json.loads(l)
            except ValueError: continue
            v = d.get("v") or {}
            n = v.get("printname")
            if n and n not in seen and not d.get("mods"): seen[n] = v
    keys = sorted({k for v in seen.values() for k in v if PAT.search(k)})
    # keep fields that are set on at least one weapon
    keys = [k for k in keys if any(v.get(k) not in (None, 0, "", False) for v in seen.values())]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("field\t" + "\t".join(seen) + "\n")
        for k in keys:
            f.write(k + "\t" + "\t".join(str(v.get(k, ""))[:60] for v in seen.values()) + "\n")
    print(len(seen), "weapons", len(keys), "fields")
    print(list(seen)[:50])
    print(keys)


if __name__ == "__main__":
    main()
