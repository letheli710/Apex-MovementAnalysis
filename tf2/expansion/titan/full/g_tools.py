"""Shared loaders for the gap analyses. Usage: from g_tools import load"""
import os, collections
def load(run):
    d = collections.defaultdict(list); cmds = []
    for l in open(os.path.join(run, 'diag.tsv'), encoding='utf-8', errors='replace'):
        p = l.split()
        if len(p) < 3: continue
        k = p[1]
        if k == 'CMD':
            cmds.append((float(p[2]), ' '.join(p[3:])))
        elif k in ('CAM','CK','GK','C','TT','PET'):
            try: d[k].append([float(x) for x in p[2:]])
            except ValueError: pass
        elif k == 'GW':
            try: d[k].append([float(p[2]), p[3]] + [float(x) for x in p[4:]])
            except ValueError: pass
        elif k == 'BD':
            try: d['BD_'+p[3]].append([float(p[2])] + [float(x) for x in p[4:]])
            except ValueError: pass
    return d, cmds
def tags(cmds):
    t = [(a, b.split()[1]) for a, b in cmds if b.startswith('hsd_tag ')]
    return [(a, t[i+1][0] if i+1 < len(t) else a+5, n) for i, (a, n) in enumerate(t)]
