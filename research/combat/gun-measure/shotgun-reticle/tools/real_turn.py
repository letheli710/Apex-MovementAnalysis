import sys, os
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr
r = sr.R5(sys.argv[1])
try:
    for yaw in ("0", "4"):
        r.give(sr.GUNS["eva8"], 0, target="body", dist="300", snap="0", secs="10")

        r.key("+", "attack"); r.pl.sleep(0.04); r.key("-", "attack"); r.pl.sleep(0.04)
        if yaw != "0":
            r.sv('entity p = GetPlayerArray()[0]; vector a = p.EyeAngles(); p.SnapEyeAngles( <a.x, a.y + ' + yaw + ', 0> ); AgentLink_Reply( "t" )')
        r.pl.sleep(0.04)
        r.shot("real_turn_" + yaw, crop=500)
        r.pl.sleep(8)
finally:
    r.close()
