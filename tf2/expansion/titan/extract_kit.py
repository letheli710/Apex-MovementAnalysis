"""Static kit reader for the 7 MP titans: pulls the gameplay keys out of each kit weapon file
(scripts/weapons/mp_titan*.txt in the unpacked client_mp_common VPK) and writes one dump per titan.

Rules: MP_BASE wins over SP_BASE; a value tagged [$sp] is dropped, [$mp] kept; presentation keys
(sounds, fx, models, anims, hud, viewkick, sway, npc_*) are left out. Mods are listed with their
changes, except Frontier Defense (fd_*), dev_* and burn-card mods, which are not part of the MP kit.

Usage: python -I extract_kit.py  -> writes static/<titan>.txt and prints a short summary.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEAPONS = HERE.parent.parent / "local" / "vpk" / "client_mp_common" / "scripts" / "weapons"
OUT = HERE / "static"

KITS = {
    "ion": ["mp_titanweapon_particle_accelerator", "mp_titanweapon_laser_lite", "mp_titanweapon_vortex_shield_ion",
            "mp_titanability_laser_trip", "mp_titancore_laser_cannon", "melee_titan_punch_ion"],
    "scorch": ["mp_titanweapon_meteor", "mp_titanweapon_flame_wall", "mp_titanweapon_heat_shield",
               "mp_titanability_slow_trap", "mp_titancore_flame_wave", "melee_titan_punch_scorch"],
    "northstar": ["mp_titanweapon_sniper", "mp_titanweapon_dumbfire_rockets", "mp_titanability_tether_trap",
                  "mp_titanability_hover", "mp_titancore_flight_core", "mp_titanweapon_flightcore_rockets", "melee_titan_punch_northstar"],
    "ronin": ["mp_titanweapon_leadwall", "mp_titanweapon_arc_wave", "mp_titanability_basic_block",
              "mp_titanability_phase_dash", "mp_titancore_shift_core", "melee_titan_sword"],
    "tone": ["mp_titanweapon_sticky_40mm", "mp_titanweapon_tracker_rockets", "mp_titanability_particle_wall",
             "mp_titanability_sonar_pulse", "mp_titancore_salvo_core", "melee_titan_punch_tone"],
    "legion": ["mp_titanweapon_predator_cannon", "mp_titanability_power_shot", "mp_titanability_gun_shield",
               "mp_titanability_ammo_swap", "mp_titancore_siege_mode", "melee_titan_punch_legion"],
    "monarch": ["mp_titanweapon_xo16_vanguard", "mp_titanweapon_salvo_rockets", "mp_titanweapon_shoulder_rockets",
                "mp_titanweapon_stun_laser", "mp_titanability_rearm", "mp_titancore_upgrade", "melee_titan_punch_vanguard"],
}

SKIP = re.compile(r"sound|fx|effect|model|anim|hud|rui|icon|viewkick|sway|bob|menu|print|desc|npc_|proficiency|"
                  r"rumble|tracer|trail|impact_table|crosshair|ui_|viewmodel|playermodel|holster|deploy_time|"
                  r"raise_time|lower_time|vortex_absorb|decal|shell|chroma|bodygroup|camo|^stat_|readymessage|"
                  r"readyhint|^Ondevelop|dof_|smart_ammo_draw|screen|glint|light|zoom_angle|zoom_scope|"
                  r"challenge|aimassist|ammo_display|ammo_suck|damage_flags|damage_type|attack_button|"
                  r"^On[A-Z]", re.I)
SKIP_MOD = re.compile(r"^(fd_|dev_|burn_mod|sp_|training|bc_|npc_|LTS|lts_)", re.I)

TOKEN = re.compile(r'"([^"]*)"|(\{)|(\})|(\[[^\]]*\])|([^\s"{}\[\]]+)')


def tokens(text):
    text = re.sub(r"//[^\n]*", "", text)
    for m in TOKEN.finditer(text):
        s, ob, cb, cond, bare = m.groups()
        if ob:
            yield ("{", None)
        elif cb:
            yield ("}", None)
        elif cond:
            yield ("cond", cond)
        else:
            yield ("str", s if s is not None else bare)


def parse(text):
    """-> nested list of (key, value_or_children, cond)"""
    toks = list(tokens(text))
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(toks):
            kind, val = toks[pos]
            if kind == "}":
                pos += 1
                return items
            if kind != "str":
                pos += 1
                continue
            key = val
            pos += 1
            if pos < len(toks) and toks[pos][0] == "{":
                pos += 1
                items.append((key, block(), None))
                continue
            if pos < len(toks) and toks[pos][0] == "str":
                value = toks[pos][1]
                pos += 1
                cond = None
                if pos < len(toks) and toks[pos][0] == "cond":
                    cond = toks[pos][1]
                    pos += 1
                items.append((key, value, cond))
        return items
    return block()


def mp_ok(cond):
    return cond is None or "$sp" not in cond.lower() or "!$sp" in cond.lower()


def flatten(items):
    """top-level keys of WeaponData with MP_BASE merged in; mods separately"""
    root = items
    for k, v, c in items:
        if k == "WeaponData" and isinstance(v, list):
            root = v
    base, mods = {}, {}
    for k, v, c in root:
        if isinstance(v, list):
            if k == "MP_BASE" or k == "#base":
                for k2, v2, c2 in v:
                    if not isinstance(v2, list) and mp_ok(c2):
                        base[k2] = v2
            elif k == "Mods":
                for mk, mv, mc in v:
                    if isinstance(mv, list) and not SKIP_MOD.match(mk):
                        mods[mk] = {k2: v2 for k2, v2, c2 in mv if not isinstance(v2, list) and mp_ok(c2) and not SKIP.search(k2)}
            continue
        if mp_ok(c) and k not in base:
            base[k] = v
    keep = {k: v for k, v in base.items() if not SKIP.search(k)}
    return keep, mods


def load(name):
    """flattened keys of one weapon file, with its #base file underneath"""
    text = (WEAPONS / (name + ".txt")).read_text(encoding="utf-8", errors="replace")
    base, mods = flatten(parse(text))
    m = re.match(r'﻿?\s*#base\s+"([^"]+)\.txt"', text)
    if m:
        b, bm = load(m.group(1))
        b.update(base)
        bm.update(mods)
        base, mods = b, bm
    return base, mods


def dump(name):
    p = WEAPONS / (name + ".txt")
    if not p.exists():
        return "## %s\n(missing)\n" % name
    base, mods = load(name)
    out = ["## %s  (scripts/weapons/%s.txt)" % (name, name)]
    for k in sorted(base):
        out.append("  %-46s %s" % (k, base[k]))
    if mods:
        out.append("  -- mods")
        for m, kv in mods.items():
            out.append("  [%s] %s" % (m, ", ".join("%s=%s" % x for x in kv.items()) or "(no gameplay keys)"))
    return "\n".join(out) + "\n"


def main():
    OUT.mkdir(exist_ok=True)
    for titan, names in KITS.items():
        text = "# %s kit: static keys (generated by extract_kit.py; MP values)\n\n" % titan + "\n".join(dump(n) for n in names)
        (OUT / (titan + ".txt")).write_text(text, encoding="utf-8")
        print(titan, len(text.splitlines()), "lines")


if __name__ == "__main__":
    main()
