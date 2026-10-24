"""Low-speed timeout attempt (P-07): speed, ground state and hook distance between attach and release. Run inside a session folder.

  py -3 <this file>   (cwd = phase2-local/data/<session>)
Standard library only. Part of rea-native N6 (n6/N6-MEASURE.md).
"""
import re,glob,math
KV=re.compile(r"([A-Za-z_0-9]+)=(\S+)")
fr={};gr={}
for f in glob.glob('platform/logs/client/*/*.log'):
    for l in open(f,encoding='utf-8',errors='replace'):
        if 'kind=frame' in l and 'side=cl' in l:
            k=dict(KV.findall(l)); fr.setdefault(k.get('run'),[]).append(k)
        elif '[M10-GRC]' in l:
            k=dict(KV.findall(l)); gr.setdefault(k['run'],[]).append(k)
v=lambda s:tuple(map(float,s.split(',')))
for run in sorted(gr, key=lambda r:int(r)):
    G=sorted(gr[run],key=lambda k:float(k['t'])); F=sorted(fr.get(run,[]),key=lambda k:float(k['t']))
    att=[(float(a['t']),v(a['hook'])) for a in G if a['att']=='true']
    if not att: continue
    ta,h=att[0]; rel=next((float(b['t']) for a,b in zip(G,G[1:]) if a['att']=='true' and b['att']=='false'),None)
    rows=[]
    for k in F:
        t=float(k['t'])
        if ta-0.02<=t<=rel+0.02:
            ve=v(k['vel']); o=v(k['o']); rows.append((t-ta, math.sqrt(sum(x*x for x in ve)), int(k['ground']), math.dist(o,h), o[2]-294.92))
    first_air=next((r[0] for r in rows if r[2]==0),None)
    last_ground=max((r[0] for r in rows if r[2]==1),default=None)
    print(run,'held %.3f'%(rel-ta),'max |v| %.1f'%max(r[1] for r in rows),'first air %s'%(None if first_air is None else round(first_air,3)),
          'last ground %s'%(None if last_ground is None else round(last_ground,3)),'dist at release %.0f'%rows[-1][3],'z rise %.1f'%max(r[4] for r in rows), 'hook z %.1f'%(h[2]-294.92))
