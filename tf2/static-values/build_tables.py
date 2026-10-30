"""Build the T1 static-value tables with an "R5 value" column.

Usage: python -I build_tables.py
Inputs (relative to this folder):
  ../local/pilot-sets-resolved.csv           set_resolve.py output (all pilot_*.set)
  ghidra/convar-defaults.tsv                 parse_convar_dump.py output (may be missing)
  set-schema-server.tsv                      tools/scan_set_schema.py output (built-in .set defaults)
  R5 census + R5 ConVar table (read-only, from Apex-MovementAnalysis)
Outputs: setfile-values.csv, convar-values.csv
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
R5 = HERE.parents[1] / "Apex-MovementAnalysis" / "research"
R5_CENSUS = R5 / "phase2-local" / "static-values" / "classvar-census-by-legend.csv"
R5_CVARS = R5 / "rea-native" / "convar-defaults" / "CONVAR-DEFAULTS.md"

MP = "pilot_grapple_male"  # every MP wallrun pilot resolves to the same movement values (see T1 report)
SP = "pilot_solo"
COLISEUM = "pilot_coliseum_male"

MOVE = re.compile(
    r"^(speed|sprintspeed|acceleration|deceleration|lowspeed|lowacceleration|sprint|air|jump|gravity|step|slide|"
    r"wallrun|superjump|doublejump|dodge|climb|mantle|automantle|glide|hover|zipline|grapple|land|"
    r"viewkickFall|antiMultiJump|traverse|speedScale|stepheight|friction)", re.I)


def r5_census():
    out = {}
    if R5_CENSUS.exists():
        with open(R5_CENSUS, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                per = {k: v for k, v in row.items() if k not in ("key", "common_value") and v and v != "-"}
                if row["common_value"] not in ("", "VARIES"):
                    out[row["key"].lower()] = row["common_value"]
                elif per:
                    # most common value first, then the legends that differ
                    vals = sorted(set(per.values()), key=lambda v: -list(per.values()).count(v))
                    others = ";".join(f"{k}={v}" for k, v in per.items() if v != vals[0])
                    out[row["key"].lower()] = f"{vals[0]} ({others})" if others else vals[0]
    return out


def r5_cvars():
    out = {}
    if R5_CVARS.exists():
        for line in R5_CVARS.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\| `([a-z0-9_]+)` \| ([^|]+) \|", line)
            if m:
                out[m.group(1)] = m.group(2).strip()
    return out


def read_tsv(p):
    if not p.exists():
        return []
    with open(p, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_schema():
    """set-schema-server.tsv minus the few false-positive records (uppercase / DT_ names)."""
    p = HERE / "set-schema-server.tsv"
    lines = [l for l in p.read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    return [r for r in csv.DictReader(lines, delimiter="\t")
            if r["key"][:1].islower() and r["key"] not in ("playlist", "pilot", "med_short")]


def setfile_table(census):
    rows = {}
    with open(HERE.parent / "local" / "pilot-sets-resolved.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["set"] in (MP, SP, COLISEUM) and (r["section"] in ("global", "stand", "crouch")) and MOVE.match(r["key"]):
                key = r["key"] if r["section"] == "global" else f'{r["section"]}.{r["key"]}'
                d = rows.setdefault(key.lower(), {"key": key})
                d[r["set"]] = r["value"]
                if r["set"] == MP:
                    d["mp_source"] = r["defined_in"]
    for s in read_schema():
        if not MOVE.match(s["key"]):
            continue
        d = rows.setdefault(s["key"].lower(), {"key": s["key"]})
        d["code_fallback"] = s["default"]
        d["fallback_evidence"] = f'server.dll schema record {s["record"]}: {s["help"]}'
    out = HERE / "setfile-values.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["key", "tf2_mp", "mp_source", "tf2_sp", "tf2_coliseum", "code_fallback",
                    "fallback_evidence", "r5_value", "same_as_r5"])
        for k in sorted(rows):
            d = rows[k]
            mp = d.get(MP) or d.get("code_fallback", "")
            # R5 census keys are global or stand values; TF2 crouch values have no R5 counterpart there
            r5 = "" if d["key"].startswith("crouch.") else census.get(d["key"].split(".")[-1].lower(), "")
            same = "" if not (mp and r5) else ("yes" if _num(mp) == _num(r5) else "no")
            w.writerow([d["key"], d.get(MP, ""), d.get("mp_source", "code" if d.get("code_fallback") else ""),
                        d.get(SP, ""), d.get(COLISEUM, ""), d.get("code_fallback", ""),
                        d.get("fallback_evidence", ""), r5, same])


def convar_table(r5):
    overrides = {"wallrun_gravityRampUpTime": "mp 0.7 / sp 1.0 (cfg/spmp.cfg)",
                 "wallrun_slipstarttime": "mp 1.5 / sp 2.0 (cfg/spmp.cfg)"}
    merged = {}
    for r in read_tsv(HERE / "ghidra" / "convar-defaults.tsv"):
        m = merged.setdefault(r["convar"], {"default": r["default"], "dlls": [], "help": r.get("help", "")})
        m["dlls"].append(f'{r["dll"]}@{r["function"]}')
        if r["default"] != m["default"]:
            m["default"] += f' / {r["dll"]}: {r["default"]}'
        m["help"] = m["help"] or r.get("help", "")
    with open(HERE / "convar-values.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["convar", "tf2_default", "registered_in", "help", "cfg_override", "r5_value", "same_as_r5"])
        for name in sorted(merged, key=str.lower):
            m = merged[name]
            r5v = r5.get(name, "")
            same = "" if not r5v else ("yes" if _num(r5v) == _num(m["default"]) else "no")
            w.writerow([name, m["default"], " ".join(m["dlls"]), m["help"].replace("\\'", "'").replace('\\"', '"'),
                        overrides.get(name, ""), r5v, same])


def _num(s):
    s = str(s).strip().strip('"').split(" (")[0].lower()
    s = {"true": "1", "false": "0"}.get(s, s)
    try:
        return float(s)
    except ValueError:
        return s


if __name__ == "__main__":
    setfile_table(r5_census())
    convar_table(r5_cvars())
