import re, sys, os
src = open(sys.argv[1], encoding='utf-8').read()
tabs = dict(re.findall(r'static readonly double\[\] (\w+) = \{([^}]*)\}', src))
classes = ['StandH80','StandH100','StandH120','StandH120Yaw45','CrouchH80','CrouchH100','CrouchH120','CrouchH120Short']
out = os.path.join(sys.argv[2], 'traversal-curves.tsv')
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write('# 07-camera traversal (mantle) camera pitch offset. Two tables per class, 21 points each at u = 0, 0.05, ..., 1.\n')
    f.write('# anim_<class>: animation fraction at traversal TIME fraction u (u = time since mantle start / mantle duration).\n')
    f.write('# delta_<class>: pitch offset [deg, + = view down] at ANIMATION fraction. Camera pitch offset(t) = delta(anim(u)) * smoothstep(t / 0.15 s); linear between points.\n')
    f.write('# Measured averages of 61 R5 traversals (B1), first point extrapolated, tail below 0 set to 0. Copied from HSD-Unity Assets/HSD/R5Replay/Runtime/MantleBoostS27.cs (main 17260f2).\n')
    f.write('# StandH120 blends toward StandH120Yaw45 by w = clamp(|view-to-wall yaw| / 45 deg) (standing h120 only).\n')
    f.write('# Class by standing traversal time T: h80 < 0.390 s <= h100 < 0.519 s <= h120+ (class times 0.313 / 0.467 / 0.571 s); crouched at start -> Crouch*; CrouchH120Short = crouched h120 that starts in the low base state (D-75 B).\n')
    f.write('u\t' + '\t'.join(['anim_'+c+'\tdelta_'+c for c in classes]) + '\n')
    cols = []
    for c in classes:
        an = [float(x) for x in tabs[c+'Anim'].split(',')]
        de = [float(x) for x in tabs[c].split(',')]
        assert len(an) == 21 and len(de) == 21, c
        cols.append((an, de))
    for i in range(21):
        f.write(f'{i*0.05:.2f}\t' + '\t'.join(f'{an[i]:g}\t{de[i]:g}' for an, de in cols) + '\n')
print('ok')
