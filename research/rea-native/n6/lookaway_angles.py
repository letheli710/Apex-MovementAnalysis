"""Look-away detach (P-10): view-to-hook angle at every client release. Run inside a session folder.

  py -3 <this file>   (cwd = phase2-local/data/<session>)
Standard library only. Part of rea-native N6 (n6/N6-MEASURE.md).
"""
import re,glob,math,bisect,sys
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
    G=sorted(gr[run],key=lambda k:float(k['t'])); F=sorted(fr.get(run,[]),key=lambda k:float(k['t'])); ft=[float(k['t']) for k in F]
    if not F: continue
    out=[]
    for a,b in zip(G,G[1:]):
        if a['att']=='true' and b['att']=='false':
            t=float(b['t']); i=max(0,bisect.bisect_left(ft,t)-1)
            k=F[i]; h=v(a['hook']); e=v(k['epos']); vv=v(k['vv']); o=v(k['o'])
            out.append('t=%.3f eye=%.1f org=%.1f d=%.0f'%(t,ang(vv,[h[j]-e[j] for j in range(3)]),ang(vv,[h[j]-o[j] for j in range(3)]),math.dist(e,h)))
    print(run, ' | '.join(out[:5]))
