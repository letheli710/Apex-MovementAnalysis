#!/usr/bin/env python3
"""A1: each kept gun bare and with each mod alone. The probe dumps all client vars when the weapon changes; this reads back the mods and a set of vars on the server, so client and server can be compared.
  py -3 -I sweep_mods.py <weapons dir> <out.tsv> [gun ...]   Appends; skips lines already in out.tsv."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "w2-runtime"))
from guns import GUNS, mods
from rt_probe import AgentLink, DEFAULT_GAME
SKIP = {("tripletake", "hopup_kinetic_loader")}  # closes the host
V = ["fire_rate", "damage_near_value", "damage_far_value", "damage_headshot_scale", "ammo_clip_size", "reload_time", "reloadempty_time", "reload_time_late1", "zoom_fov", "zoom_time_in", "zoom_time_out",
     "spread_stand_hip", "spread_stand_ads", "spread_kick_on_fire_stand_hip", "viewkick_pitch_base", "viewkick_pitch_random", "viewkick_yaw_base", "projectile_launch_speed", "holster_time", "deploy_time", "raise_time", "lower_time", "burst_fire_count", "burst_fire_delay", "ads_move_speed_scale"]
READ1 = 'try {{ out += " {v}=" + w.GetWeaponSettingFloat( eWeaponVar.{v} ) }} catch ( e_{v} ) {{ try {{ out += " {v}=" + w.GetWeaponSettingInt( eWeaponVar.{v} ) }} catch ( e2_{v} ) {{ out += " {v}=?" }} }}'
READS = " ".join(READ1.format(v=v) for v in V)
SN = """
string out = ""
try {
entity p = GetPlayerArray()[0]
foreach ( w0 in p.GetMainWeapons() ) p.TakeWeaponByEntNow( w0 )
array<string> mods = {{MODS}}
entity w = p.GiveWeapon( "{{W}}", WEAPON_INVENTORY_SLOT_PRIMARY_0, mods )
p.SetActiveWeaponByName( eActiveInventorySlot.mainHand, "{{W}}" )
out += "gotmods="
foreach ( mn in w.GetMods() ) out += mn + ","
{{R}}
} catch ( err ) { out += " ERR=" + string( err ) }
AgentLink_Reply( out )
"""

def main():
    wd, outp = sys.argv[1], sys.argv[2]; gs = sys.argv[3:] or list(GUNS)
    done = set()
    if os.path.exists(outp):
        for l in open(outp, encoding="utf-8"): done.add(tuple(l.split("\t")[1:3]))
    with AgentLink("server", DEFAULT_GAME, timeout=20) as s, open(outp, "a", encoding="utf-8") as f:
        for g in gs:
            fn = "mp_weapon_" + GUNS[g]
            if not os.path.exists(os.path.join(wd, fn + ".txt")):
                print(g, "no .txt", flush=True); continue
            for m in ["none"] + sorted(mods(os.path.join(wd, fn + ".txt"))):
                if (g, m) in done or (g, m) in SKIP: continue
                ms = "[]" if m == "none" else f'["{m}"]'
                t = time.time()
                r = s.eval(SN.replace("{{MODS}}", ms).replace("{{W}}", fn).replace("{{R}}", READS), check=False)
                f.write(f"{t:.3f}\t{g}\t{m}\t{str(r.get('reply'))}\t{r.get('error')}\n"); f.flush()
                time.sleep(0.55)
            print(g, "done", flush=True)
    print("SWEEP_DONE", flush=True)

if __name__ == "__main__":
    main()
