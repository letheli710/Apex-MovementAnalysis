"""Resolve TF2 pilot weapon .txt files into multiplayer values (2026-11-08, session tf2-weapons).

Usage: python -I wpn_extract.py <weapons_dir> <out_dir>
Writes:
  wpn-values.tsv   long table: weapon, scope, key, value
                   scope = mp   (base keys, then MP_BASE overrides: what a multiplayer pilot gets)
                         = sp   (base keys, then SP_BASE overrides: campaign)
                         = mod:<name> (each Mods block; "*0.7" style values are multipliers on the mp value)
  wpn-mods.tsv     weapon, mod, key, value, resolved_mp (multipliers applied to the mp value)
Rules:
  - "//" starts a comment (outside quotes).
  - A value followed by a platform tag ([$WINDOWS], [$PS4], ...) is kept only for [$WINDOWS]
    or when untagged; mp_weapon_g2.txt is the only file with tags (viewkick_perm_pitch_base).
  - Nested blocks other than MP_BASE / SP_BASE / Mods (UiData*, RUI_CrosshairData) are skipped.
"""
import re
import sys
from pathlib import Path

TOKEN = re.compile(r'"([^"]*)"|([{}])|(\[\$[^\]]*\])|([^\s{}"\[]+)')

PILOT = [
    # (class, English name, slot)
    ("mp_weapon_rspn101", "R-201 Carbine", "primary/ar"),
    ("mp_weapon_rspn101_og", "R-101 Carbine", "primary/ar"),
    ("mp_weapon_hemlok", "Hemlok BF-R", "primary/ar"),
    ("mp_weapon_g2", "G2A5", "primary/ar"),
    ("mp_weapon_vinson", "V-47 Flatline", "primary/ar"),
    ("mp_weapon_car", "CAR", "primary/smg"),
    ("mp_weapon_alternator_smg", "Alternator", "primary/smg"),
    ("mp_weapon_hemlok_smg", "Volt", "primary/smg"),
    ("mp_weapon_r97", "R-97", "primary/smg"),
    ("mp_weapon_lmg", "Spitfire", "primary/lmg"),
    ("mp_weapon_lstar", "L-STAR", "primary/lmg"),
    ("mp_weapon_esaw", "X-55 Devotion", "primary/lmg"),
    ("mp_weapon_sniper", "Kraber-AP Sniper", "primary/sniper"),
    ("mp_weapon_doubletake", "D-2 Double Take", "primary/sniper"),
    ("mp_weapon_dmr", "Longbow-DMR", "primary/sniper"),
    ("mp_weapon_shotgun", "EVA-8 Auto", "primary/shotgun"),
    ("mp_weapon_mastiff", "Mastiff", "primary/shotgun"),
    ("mp_weapon_pulse_lmg", "EM-4 Cold War", "primary/grenadier"),
    ("mp_weapon_epg", "EPG-1", "primary/grenadier"),
    ("mp_weapon_softball", "R-6P Softball", "primary/grenadier"),
    ("mp_weapon_smr", "Sidewinder SMR", "primary/grenadier"),
    ("mp_weapon_smart_pistol", "Smart Pistol", "primary/pistol"),
    ("mp_weapon_wingman_n", "Wingman Elite", "primary/pistol"),
    ("mp_weapon_autopistol", "RE-45 Auto", "secondary"),
    ("mp_weapon_semipistol", "Hammond P2016", "secondary"),
    ("mp_weapon_wingman", "B3 Wingman", "secondary"),
    ("mp_weapon_shotgun_pistol", "SA-3 Mozambique", "secondary"),
    ("mp_weapon_defender", "Charge Rifle", "anti-titan"),
    ("mp_weapon_mgl", "MGL Mag Launcher", "anti-titan"),
    ("mp_weapon_arc_launcher", "LG-97 Thunderbolt", "anti-titan"),
    ("mp_weapon_rocket_launcher", "Archer", "anti-titan"),
]


def tokenize(text):
    out = []
    for line in text.splitlines():
        # strip // comments that are outside quotes
        buf, inq, i = [], False, 0
        while i < len(line):
            ch = line[i]
            if ch == '"':
                inq = not inq
            if not inq and line.startswith("//", i):
                break
            buf.append(ch)
            i += 1
        for m in TOKEN.finditer("".join(buf)):
            if m.group(1) is not None:
                out.append(("s", m.group(1)))
            elif m.group(2):
                out.append(("b", m.group(2)))
            elif m.group(3):
                out.append(("c", m.group(3)))
            else:
                out.append(("s", m.group(4)))
    return out


def parse_block(tokens, i):
    items = []
    while i < len(tokens):
        kind, t = tokens[i]
        if kind == "b" and t == "}":
            return items, i + 1
        if kind == "c":
            i += 1
            continue
        if i + 1 < len(tokens) and tokens[i + 1] == ("b", "{"):
            sub, i = parse_block(tokens, i + 2)
            items.append((t, sub))
            continue
        val = tokens[i + 1][1] if i + 1 < len(tokens) else ""
        i += 2
        cond = None
        if i < len(tokens) and tokens[i][0] == "c":
            cond = tokens[i][1]
            i += 1
        if cond is None or cond == "[$WINDOWS]":
            items.append((t, val))
    return items, i


def weapon_data(path):
    items, _ = parse_block(tokenize(path.read_text(encoding="utf-8", errors="replace")), 0)
    return next((v for k, v in items if k == "WeaponData" and isinstance(v, list)), [])


def resolve(data):
    base, mp, sp, mods = {}, {}, {}, {}
    for k, v in data:
        if isinstance(v, list):
            if k == "MP_BASE":
                mp.update({bk: bv for bk, bv in v if not isinstance(bv, list)})
            elif k == "SP_BASE":
                sp.update({bk: bv for bk, bv in v if not isinstance(bv, list)})
            elif k == "Mods":
                for mod, body in v:
                    if isinstance(body, list):
                        mods[mod] = [(mk, mv) for mk, mv in body if not isinstance(mv, list)]
        else:
            base[k] = v
    rmp = dict(base)
    rmp.update({k: v for k, v in mp.items() if v != "<KEEP_DEFAULT>"})
    rsp = dict(base)
    rsp.update({k: v for k, v in sp.items() if v != "<KEEP_DEFAULT>"})
    return rmp, rsp, mods


def apply_mod(val, base):
    """'*0.7' multiplies, '++2' / '--2' add (TF2 mod syntax), anything else replaces."""
    try:
        if val.startswith("*"):
            return "%g" % (float(base) * float(val[1:]))
        if val.startswith("++"):
            return "%g" % (float(base) + float(val[2:]))
        if val.startswith("--"):
            return "%g" % (float(base) - float(val[2:]))
    except (TypeError, ValueError):
        return ""
    return val


def main():
    wdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    rows, modrows = [], []
    for cls, name, slot in PILOT:
        mp, sp, mods = resolve(weapon_data(wdir / (cls + ".txt")))
        for k in sorted(mp):
            rows.append((cls, "mp", k, mp[k]))
        for k in sorted(sp):
            if sp[k] != mp.get(k):
                rows.append((cls, "sp", k, sp[k]))
        for mod, kv in mods.items():
            if not kv:
                modrows.append((cls, mod, "", "", ""))
            for k, v in kv:
                rows.append((cls, "mod:" + mod, k, v))
                modrows.append((cls, mod, k, v, apply_mod(v, mp.get(k, ""))))
    with open(out / "wpn-values.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("weapon\tscope\tkey\tvalue\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    with open(out / "wpn-mods.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("weapon\tmod\tkey\tvalue\tresolved_mp\n")
        for r in modrows:
            f.write("\t".join(r) + "\n")
    print("rows", len(rows), "mod rows", len(modrows))


if __name__ == "__main__":
    main()
