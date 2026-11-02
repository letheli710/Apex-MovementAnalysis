#!/usr/bin/env python3
"""The kept guns (W0) and their mods from the local install's .txt. py -3 -I guns.py <weapons dir> prints a count per gun, or import it."""
import os, re, sys
GUNS = {"r301": "rspn101", "r99": "r97", "car": "car", "flatline": "vinson", "spitfire": "lmg", "alternator": "alternator_smg", "re45": "autopistol", "volt": "volt_smg", "p2020": "semipistol",
        "hemlok": "hemlok", "prowler": "pdw", "nemesis": "nemesis", "ehemlok": "auto_hemlok",
        "eva8": "shotgun", "mastiff": "mastiff", "peacekeeper": "energy_shotgun", "mozambique": "shotgun_pistol", "tripletake": "doubletake",
        "kraber": "sniper", "longbow": "dmr", "sentinel": "sentinel", "g7": "g2", "wingman": "wingman", "chargerifle": "defender",
        "havoc": "energy_ar", "devotion": "esaw", "rampage": "dragon_lmg", "lstar": "lstar", "r3030": "3030", "bocek": "bow",
        "sheila": "mounted_turret_weapon", "vantage": "sniper_ult"}


def blocks(txt, start):
    """Top-level "name" { ... } children of the block opening at start; returns {name: body}."""
    out, i, depth, name, s0 = {}, start, 0, None, None
    toks = re.finditer(r'"([^"]*)"|(\{)|(\})|(//[^\n]*)', txt[start:])
    last = None
    for m in toks:
        if m.group(4): continue
        if m.group(2):
            depth += 1
            if depth == 2: name, s0 = last, start + m.end()
        elif m.group(3):
            depth -= 1
            if depth == 1 and name is not None: out[name] = txt[s0:start + m.start()]; name = None
            if depth == 0: break
        else:
            last = m.group(1)
    return out


def mods(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r'"Mods"\s*\{', txt)
    return blocks(txt, m.start()) if m else {}


if __name__ == "__main__":
    wd = sys.argv[1]; tot = 0; names = {}
    for g, f in GUNS.items():
        p = os.path.join(wd, f"mp_weapon_{f}.txt")
        if not os.path.exists(p): print(g, "MISSING", f); continue
        M = mods(p); tot += len(M)
        for n in M: names.setdefault(n, []).append(g)
        print(g, len(M))
    print("total", tot, "distinct", len(names))
    for n, v in sorted(names.items(), key=lambda kv: -len(kv[1])): print(f"{n}\t{len(v)}")
