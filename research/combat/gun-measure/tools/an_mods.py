#!/usr/bin/env python3
"""A1 analysis: join sweep.tsv to vars.jsonl by time; for each gun + mod compare the client's vars with the bare gun and with what the mod's .txt block asks for; and the server's read-back set.
  py -3 -I an_mods.py <dir with sweep.tsv vars.jsonl wall.txt> <weapons dir> <out.tsv> <summary.tsv>"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guns import GUNS, mods


def kv(body):
    return {a: b for a, b in re.findall(r'"([^"]+)"\s+"([^"]*)"', body)}


def expect(base, op):
    try:
        if op.startswith("*"): return base * float(op[1:])
        if op.startswith("++"): return base + float(op[2:])
        if op.startswith("+"): return base + float(op[1:])
        if op.startswith("--"): return base - float(op[2:])
        return float(op)
    except (TypeError, ValueError):
        return None


def main():
    d, wd, out, summ = sys.argv[1:5]
    wall = int(open(os.path.join(d, "wall.txt")).read()) / 1000
    dumps = []
    for l in open(os.path.join(d, "vars.jsonl"), encoding="utf-8"):
        try: j = json.loads(l); dumps.append((j["t"] + wall, j["v"]))
        except ValueError: pass
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(d, "sweep.tsv"), encoding="utf-8")]
    rows = [r for r in rows if len(r) >= 5]
    res, base, sbase = [], {}, {}
    for i, r in enumerate(rows):
        t, g, m, rep, err = float(r[0]), r[1], r[2], r[3], r[4]
        tn = float(rows[i + 1][0]) if i + 1 < len(rows) else t + 1
        ds = [v for tt, v in dumps if t < tt <= tn + 0.05]
        v = ds[-1] if ds else None
        sv = dict(re.findall(r" (\w+)=(\S+)", rep))
        got = re.search(r"gotmods=(\S*)", rep)
        res.append(dict(g=g, m=m, v=v, sv=sv, got=got.group(1) if got else "", err=("ERR=" in rep) or err != "False", rep=rep))
        if m == "none": base[g] = v; sbase[g] = sv
    S = {}
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("gun\tmod\tgiven\tn_file_keys\tn_in_var_table\tn_as_file\tn_other\tclient_changed\tserver_changed\tdiffs_from_file\tnote\n")
        for x in res:
            if x["m"] == "none": continue
            g, m, v, b = x["g"], x["m"], x["v"], base.get(x["g"])
            M = mods(os.path.join(wd, f"mp_weapon_{GUNS[g]}.txt")).get(m, "")
            K = kv(M)
            given = "yes" if (m + ",") in x["got"] else ("error" if x["err"] else "no")
            if v is None or b is None:
                f.write(f"{g}\t{m}\t{given}\t{len(K)}\t\t\t\t\t\t\tno client dump\n"); continue
            changed = {k for k in v if v[k] != b.get(k)}
            intab = [k for k in K if k in v]
            okc, oth = 0, []
            for k in intab:
                bb, op, val = b.get(k), K[k], v[k]
                if isinstance(val, list) or not isinstance(bb, (int, float)):
                    continue
                e = expect(bb, op)
                if e is None: continue
                if abs(val - e) <= max(0.002, abs(e) * 0.002): okc += 1
                else: oth.append(f"{k}:{bb}->{val}(file {op})")
            sch = [k for k in x["sv"] if x["sv"][k] != sbase.get(g, {}).get(k)]
            f.write(f"{g}\t{m}\t{given}\t{len(K)}\t{len(intab)}\t{okc}\t{len(oth)}\t{len(changed)}\t{','.join(sch)}\t{'; '.join(oth)[:400]}\t\n")
            s = S.setdefault(m, dict(n=0, given=0, keys=0, ok=0, oth=0, ch=0, srv=0, guns=[]))
            s["n"] += 1; s["given"] += given == "yes"; s["keys"] += len(intab); s["ok"] += okc; s["oth"] += len(oth); s["ch"] += bool(changed); s["srv"] += bool(sch); s["guns"].append(g)
    with open(summ, "w", encoding="utf-8", newline="\n") as f:
        f.write("mod\tguns\tgiven\tkeys_in_table\tas_file\tnot_as_file\tguns_client_changed\tguns_server_changed\texample_guns\n")
        for m, s in sorted(S.items()):
            f.write(f"{m}\t{s['n']}\t{s['given']}\t{s['keys']}\t{s['ok']}\t{s['oth']}\t{s['ch']}\t{s['srv']}\t{','.join(s['guns'][:6])}\n")
    json.dump({g: base[g] for g in base if base[g]}, open(os.path.join(d, "base_vars.json"), "w"), indent=0)
    bad = [x for x in res if x["err"]]
    print("rows", len(res), "errors", len(bad), [(b["g"], b["m"]) for b in bad][:20])
    print("no client dump", sum(1 for x in res if x["v"] is None))


if __name__ == "__main__":
    main()
