import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr
r = sr.R5(sys.argv[1])
try:
    r.give(sr.GUNS["eva8"], 0)
    for i, dt in enumerate((0.4, 0.8, 1.2, 1.6)):
        r.sv(sr.RESET.replace("{pitch}", "0")); r.pl.sleep(0.4)
        r.sv('SetConVarFloat( "host_timescale", 0.05 ); AgentLink_Reply( "h" )'); r.pl.sleep(0.3)
        r.key("+", "zoom"); r.pl.sleep(dt); r.state(f"slow{dt} pre"); r.shot(f"adsslow_{i}"); r.state(f"slow{dt} post")
        r.sv('SetConVarFloat( "host_timescale", 1.0 ); AgentLink_Reply( "h" )'); r.key("-", "zoom"); r.pl.sleep(1.0)
finally:
    r.sv('SetConVarFloat( "host_timescale", 1.0 ); AgentLink_Reply( "h" )')
    r.close()
    print("\n".join(l[:120] for l in r.log if "st t=" in l))
