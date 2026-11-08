#!/usr/bin/env python3
"""Peacekeeper with the Precision Choke (mods hopup_energy_choke / choke): R5 switches to Crosshair_Hopup (ui/crosshair_shotgun_hopup, arg charge).
  py -3 -I choke.py <out dir>"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr  # noqa: E402

CH = r'''
entity w = GetLocalClientPlayer().GetActiveWeapon( eActiveInventorySlot.mainHand )
array<string> m = w.GetMods()
printt( format( "[RT] choke charge=%.3f zf=%.3f mods=%s", w.GetWeaponChargeFraction(), GetLocalClientPlayer().GetZoomFrac(), m.join( "," ) ) )
AgentLink_Reply( "c" )
'''


def main():
    out = sys.argv[1]
    r = sr.R5(out)
    try:
        for mods in ("hopup_energy_choke", "hopup_energy_choke,choke"):
            tag = mods.replace(",", "+")
            r.give(sr.GUNS["peacekeeper"], 0, mods=mods)
            r.cl(CH); r.shot(f"pk_{tag}_hip")
            r.key("+", "zoom")
            for i, dt in enumerate((0.35, 0.5, 1.4)):
                r.pl.sleep(dt); r.cl(CH); r.shot(f"pk_{tag}_ads{i}")
            r.key("-", "zoom"); r.pl.sleep(0.5); r.cl(CH); r.shot(f"pk_{tag}_after"); r.pl.sleep(1.0)
    finally:
        r.close()
        print("\n".join(l[:150] for l in r.pl.lines["c"] if "choke" in l))


if __name__ == "__main__":
    main()
