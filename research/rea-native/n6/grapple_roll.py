"""Grapple camera roll (CAM-11): native Grapple_CameraRoll formula vs measured camera roll. Run inside a session folder.

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
def vecs(p,y):
    p,y=math.radians(p),math.radians(y)
    f=(math.cos(p)*math.cos(y),math.cos(p)*math.sin(y),-math.sin(p))
    r=(math.sin(y),-math.cos(y),0.0)   # right
    u=(r[1]*f[2]-r[2]*f[1], r[2]*f[0]-r[0]*f[2], r[0]*f[1]-r[1]*f[0])  # up = right x fwd
    return f,r,u
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
def remap(x,a,b): return 0.0 if b==a else max(0.0,min(1.0,(x-a)/(b-a)))
def pred(e,h,f,u):
    d=[h[i]-e[i] for i in range(3)]; L=math.sqrt(dot(d,d))
    sd=remap(L,0,150); c=max(-1,min(1,dot(d,f)/L)); th=math.degrees(math.acos(c)); sa=remap(th,0,65)
    p=[d[i]-f[i]*dot(d,f) for i in range(3)]; pl=math.sqrt(dot(p,p))
    if pl<=0: return 0
    p=[x/pl for x in p]; cu=max(-1,min(1,dot(p,u))); phi=math.acos(cu); k=max(0,min(1,(phi-math.pi/2)/(math.pi/2)))
    cr=[p[1]*u[2]-p[2]*u[1],p[2]*u[0]-p[0]*u[2],p[0]*u[1]-p[1]*u[0]]
    if dot(cr,f)<0: phi=-phi
    return sd*sa*(1-k)*max(-20,min(20,math.degrees(phi)))
for run in sorted(gr):
    G=sorted(gr[run],key=lambda k:float(k['t'])); F=sorted(fr.get(run,[]),key=lambda k:float(k['t']))
    att=[(float(a['t']),v(a['hook'])) for a in G if a['att']=='true']
    if not att or not F: continue
    t0,h=att[0]; t1=max(a[0] for a in att)
    rows=[];sm=0;prev=None
    for k in F:
        t=float(k['t'])
        if t<t0-0.05 or t>t1+0.4: continue
        ea=v(k['eang']); f,r,u=vecs(ea[0],ea[1])
        target=pred(v(k['epos']),h,f,u) if t<=t1 else 0
        dt=(t-prev) if prev else 0; prev=t
        sm+= (target-sm)*min(1,6.667*dt)
        rows.append((t-t0,target,sm,v(k['cang'])[2]))
    if rows:
        mx=max(rows,key=lambda x:abs(x[3]))
        err=math.sqrt(sum((x[2]-x[3])**2 for x in rows)/len(rows))
        errneg=math.sqrt(sum((-x[2]-x[3])**2 for x in rows)/len(rows))
        print(run,'n',len(rows),'max meas roll %.2f at %.2f s (pred sm %.2f)'%(mx[3],mx[0],mx[2]),'rms %.2f (sign flipped %.2f)'%(err,errneg))
