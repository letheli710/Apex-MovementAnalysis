#!/usr/bin/env python3
"""Cases that need the player to move, with the player put back first. Without the reset, forward runs add up until the player stands against a wall (x -5934) and speed reads 0.
Takes the earlier cases and adds the reset in front of them. py -3 -I gen_c3.py cases_c.txt cases_c2.txt > cases_c3.txt"""
import re, sys
RST = 'sv try { entity p = GetPlayerArray()[0] ~ p.SetOrigin( <-11699, 512, 1579> ) ~ p.SetVelocity( <0, 0, 0> ) ~ p.SetAngles( <0, 0, 0> ) } catch ( e ) { printt( "[RT] rst err " + string( e ) ) } ~ AgentLink_Reply( "r" ); wait 0.5'
WANT = re.compile(r"^(ra_\w+|rc_\w+_sprint_[\d.]+|rm_\w+)\|")
out = {}
for p in sys.argv[1:]:
    for l in open(p, encoding="utf-8"):
        if WANT.match(l) and "|" in l:
            tag, w, m, s, *k = l.rstrip("\n").split("|")
            # rm_ and rc_ come from the later file, which has the ammo pools filled
            out[tag] = "|".join([tag, w, m, RST + "; " + s, *k])
print("\n".join(v for t, v in out.items() if not re.match(r"rc_(mastiff|wingman|r301)_sprint_(0.5|1.9|1.5)$", t) or "AmmoPool" in v))
