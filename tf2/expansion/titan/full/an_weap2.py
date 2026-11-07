"""Firing-only camera stats, reload camera curve, step jolt fit. Usage: an_weap2.py <g_weap run> <g_sway run>"""
import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from g_tools import load,tags
import numpy as np
rng=np.random.default_rng(1)
d,c=load(sys.argv[1])
CAM=np.array([x[:8] for x in d['CAM']]);T={n:(a,b) for a,b,n in tags(c)}
GW=d['GW']
def wrap(a): return (a+180)%360-180
F={"monarch":dict(c="mp_titanweapon_xo16_vanguard",k=(55,8),ka=(55,8),yk=(80,15),yka=(45,7),rk=(20000,15),pb=-.2,pr=.5,ps=.5,ph=0,yb=.2,yr=.15,ys=.5,yh=0,rmin=.15,rmax=.2,rs=.2,rh=.75,wf=.7,wa=.6,rate=12,smh=(.6,1.),sma=(.3,.8),l=(5,50)),
   "legion":dict(c="mp_titanweapon_predator_cannon",k=(35,12),ka=(55,15),yk=(35,12),yka=(55,15),rk=(18000,23),pb=0,pr=.46,ps=.65,ph=2,yb=0,yr=1.,ys=1.1,yh=1.35,rmin=.3,rmax=.25,rs=.2,rh=1.75,wf=.7,wa=.6,rate=15,smh=(1,1),sma=(1,1),l=(1,2)),
   "ronin":dict(c="mp_titanweapon_leadwall",k=(300,30),ka=(300,30),yk=(300,30),yka=(300,30),rk=(16000,15),pb=-2.25,pr=1,ps=6,ph=1,yb=-.95,yr=.5,ys=.5,yh=2,rmin=.6,rmax=.8,rs=.2,rh=2.75,wf=.1,wa=.1,rate=2.5,smh=(1,1),sma=(1,1),l=(1,2))}
def mc(w,ads,n=60):
    "peak |view| per axis while firing with uniform random +-r around base"
    out=[]
    for trial in range(40):
        res={}
        for ax,(sp,b,r,s,h) in {'p':((w['ka'] if ads else w['k']),w['pb'],w['pr'],w['ps'],w['ph']),'y':((w['yka'] if ads else w['yk']),w['yb'],w['yr'],w['ys'],w['yh'])}.items():
            k,dm=sp;x=v=0;dt=1/1000;rec=[];val=0;nxt=0;shots=0;t=0
            while t<n/w['rate']:
                if t>=nxt:
                    val+=1;shots+=1;nxt+=1/w['rate']
                    fr=np.clip((val-w['l'][0])/(w['l'][1]-w['l'][0]),0,1);mn,mx=(w['sma'] if ads else w['smh']);sc=mn+(mx-mn)*fr
                    kick=(b+rng.uniform(-r,r))*sc
                    x+=h*kick;v+=s*20*kick
                v+=(-k*x-dm*v)*dt;x+=v*dt;rec.append(x);t+=dt
            rec=np.array(rec)*(1-(w['wa'] if ads else w['wf']))
            res[ax]=(rec.min(),rec.max(),rec.std())
        out.append(res)
    return {ax:np.round(np.mean([o[ax] for o in out],axis=0),2) for ax in 'py'}
for cls,w in F.items():
    g=[x for x in GW if x[1]==w['c']]
    t=np.array([x[0] for x in g]);clip=np.array([x[2] for x in g]);rel=np.array([x[3] for x in g])
    for n,ads in (('burst',False),('hold',False),('adshold',True)):
        if ('wp_%s_%s'%(cls,n)) not in T: continue
        a,b=T['wp_%s_%s'%(cls,n)]
        s=(t>=a)&(t<b);ii=np.where(s)[0];sh=[t[i] for i in ii[1:] if clip[i]<clip[i-1]]
        if len(sh)<3: continue
        K=CAM[(CAM[:,0]>=sh[0])&(CAM[:,0]<=sh[-1])]
        p0=CAM[np.searchsorted(CAM[:,0],sh[0])-1]
        p=K[:,2]-p0[2];y=wrap(K[:,3]-p0[3]);r=K[:,4]-p0[4]
        print(f"{cls:8s}{n:8s} shots {len(sh)} {sh[0]-a:.2f}..{sh[-1]-a:.2f} real pitch {p.min():+.2f}..{p.max():+.2f} sd {p.std():.2f} yaw {y.min():+.2f}..{y.max():+.2f} sd {y.std():.2f} roll {r.min():+.2f}..{r.max():+.2f} | sim(mc) p {mc(w,ads,len(sh))['p']} y {mc(w,ads,len(sh))['y']}")
    # reload camera
    on=[i for i in range(1,len(t)) if rel[i] and not rel[i-1]]
    i=[q for q in on if clip[q]<=clip[on[0]]][-1] if on else None
    if on:
        i=on[1] if len(on)>1 else on[0]
        t0=t[i]; K=CAM[(CAM[:,0]>=t0-0.02)&(CAM[:,0]<t0+5)]
        tt=K[:,0]-t0;p=K[:,2]-K[0,2];y=wrap(K[:,3]-K[0,3]);r=K[:,4]-K[0,4]
        print(cls,'reload cam curve t:p/y/r',' '.join(f"{tq:.1f}:{np.interp(tq,tt,p):+.1f}/{np.interp(tq,tt,y):+.1f}/{np.interp(tq,tt,r):+.1f}" for tq in np.arange(0,4.6 if cls=='legion' else 3.0,.2)))
        print('   peak p',round(p.max(),2),round(tt[p.argmax()],2),round(p.min(),2),round(tt[p.argmin()],2),'y',round(y.min(),2),round(tt[y.argmin()],2),round(y.max(),2),'r',round(r.min(),2),round(r.max(),2),'pos',np.round(np.ptp(K[:,5:8],axis=0),2))
# step jolt
d2,c2=load(sys.argv[2])
CAM=np.array([x[:8] for x in d2['CAM']])
def imp(t,k,dm,v0):
    a=dm/2;w=np.sqrt(k-a*a)
    return v0*np.exp(-a*t)*np.sin(w*t)/w
for a,b,n in tags(c2):
    if not(n.endswith('_walk') or n.endswith('_sprint')) or not n.startswith('sw_'): continue
    K=CAM[(CAM[:,0]>=a)&(CAM[:,0]<b)]
    tt=K[:,0]-a; dz=K[:,7]
    # local minima of a detrended signal: remove sprint sink first
    from scipy.ndimage import uniform_filter1d as uf
    m=(tt>1.2)&(tt<3.4 if 'walk' in n else tt<3.0)
    x=dz[m]-uf(dz[m],95) if 'sprint' in n else dz[m]-np.median(dz[m])
    ts=tt[m]
    im=[j for j in range(3,len(x)-3) if x[j]==x[max(0,j-30):j+30].min()]
    mins=[round(ts[j],3) for j in im]
    print(n,'dz range',round(np.ptp(x),3),'min times',mins,'intervals',np.round(np.diff(mins),3))
    if 'walk' in n:
        j=im[1] if len(im)>1 else im[0]
        cur=[(round(ts[q]-ts[j],3),round(x[q],3)) for q in range(max(0,j-30),min(len(x),j+80),10)]
        print('   curve around a min',cur)
for name,v0 in (('ion',5),('ronin',6),('legion',4)):
    t=np.arange(0,1,.001);y=imp(t,65,9,-v0)
    print(name,'stepJolt sim k65 d9: min',round(y.min(),3),'@',round(t[y.argmin()],3),'overshoot',round(y.max(),3),'@',round(t[y.argmax()],3))
