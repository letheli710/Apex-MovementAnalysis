"""Look-away detach (P-10): time from the hook crossing 90 deg off the view to the first client release (M10-GRC + camera frames). Run inside a session folder.

  py -3 <this file>   (cwd = phase2-local/data/<session>)
Standard library only. Part of rea-native N6 (n6/N6-MEASURE.md).
"""
import re,glob,math,bisect
KV=re.compile(r"([A-Za-z_]+)=(\S+)")
fr={};gr={}
for f in glob.glob('platform/logs/client/*/*.log'):
    for l in open(f,encoding='utf-8',errors='replace'):
        if 'kind=frame' in l and 'side=cl' in l and 'vv=' in l:
            k=dict(KV.findall(l)); fr.setdefault(k.get('run'),[]).append(k)
        elif '[M10-GRC]' in l:
            k=dict(KV.findall(l)); gr.setdefault(k['run'],[]).append(k)
v=lambda s:tuple(map(float,s.split(',')))
def ang(a,b):
    c=sum(x*y for x,y in zip(a,b))/math.hypot(*a)/math.hypot(*b); return math.degrees(math.acos(max(-1,min(1,c))))
for run in sorted(gr):
    G=sorted(gr[run],key=lambda k:float(k['t'])); F=sorted(fr.get(run,[]),key=lambda k:float(k['t']))
    att=[(float(a['t']),v(a['hook'])) for a in G if a['att']=='true']
    rel=next((float(b['t']) for a,b in zip(G,G[1:]) if a['att']=='true' and b['att']=='false'),None)
    if not att or rel is None: continue
    t_att,h=att[0]
    for pt in ('epos','o'):
        cross=None
        for k in F:
            t=float(k['t'])
            if t<t_att: continue
            p=v(k[pt]); a=ang(v(k['vv']),[h[j]-p[j] for j in range(3)])
            if a>=90: cross=(t,a); break
        print(run,pt,'cross90 t=%.3f'%cross[0] if cross else 'no cross','release t=%.3f'%rel,'lag %.3f s'%(rel-cross[0]) if cross else '')
