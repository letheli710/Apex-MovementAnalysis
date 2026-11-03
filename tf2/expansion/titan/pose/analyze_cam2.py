"""Curves from t1_cam / t1_ext: jolt, sprint, dash, melee, embark, eject, body lag on key turns, pitch limits."""
import os,sys,bisect
RUN1,RUN2=sys.argv[1],sys.argv[2]
def wrap(a): return (a+180)%360-180
def load(run):
    cam=[];bd={};tags=[];C=[]
    for l in open(os.path.join(run,'diag.tsv'),encoding='utf-8',errors='replace'):
        p=l.split()
        if len(p)<3: continue
        if p[1]=='CAM' and len(p)>=10: cam.append((float(p[2]),int(p[3]),*map(float,p[4:10])))
        elif p[1]=='BD' and len(p)>=10: bd.setdefault(p[3],[]).append((float(p[2]),*map(float,p[4:10])))
        elif p[1]=='C' and len(p)>=9: C.append((float(p[2]),*map(float,p[3:9])))
        elif p[1]=='CMD' and p[3]=='hsd_tag': tags.append((float(p[2]),p[4]))
    return cam,bd,tags,C
def win(tags,name):
    for i,(t,n) in enumerate(tags):
        if n==name: return t,(tags[i+1][0] if i+1<len(tags) else t+5)
    return None
def curve(cam,t0,t1,step=0.1,base=None):
    out=[];nxt=t0
    for c in cam:
        if c[0]<t0: continue
        if c[0]>t1: break
        if c[0]>=nxt:
            out.append((round(c[0]-t0,2),c[1],round(c[2],2),round(c[3],1),round(c[4],2),round(c[5],1),round(c[6],1),round(c[7],1)));nxt+=step
    return out
cam,bd,tags,CL=load(RUN1)
for name,dt,st in (('hurtbig_ion',1.5,0.05),('hurtside_ion',1.2,0.05),('melee_ion',1.7,0.1),('melee_ronin',1.7,0.1),('dashr_ion',1.6,0.1),('sprint_ion',3.8,0.2),('fire_ronin',1.8,0.1),('core_ion',3,0.25),('doom_ion',1.4,0.1),('disembark_ion',3.0,0.15),('embarkanim_ion',7.0,0.25),('eject_ion',10.5,0.25)):
    w=win(tags,name)
    print('==',name,'(t,titan,pitch,yaw,roll,dx,dy,dz)')
    for r in curve(cam,w[0],w[0]+dt,st): print(r)
# player velocity during eject
w=win(tags,'eject_ion')
print('eject velocity samples t vx vy vz z')
nxt=w[0]
for c in CL:
    if c[0]<w[0]: continue
    if c[0]>w[0]+11: break
    if c[0]>=nxt: print(round(c[0]-w[0],2),round(c[4]),round(c[5]),round(c[6]),'z',round(c[3]));nxt+=0.5
cam,bd,tags,CL=load(RUN2)
def lag(tagname,dt):
    w=win(tags,tagname)
    A=bd['CHESTFOCUS']; F=bd['foot_L_sole']; times=[c[0] for c in cam]
    print('==',tagname,'t camYaw chest-cam  footLx,y,z')
    nxt=w[0]
    for a,f in zip(A,F):
        if a[0]<w[0]: continue
        if a[0]>w[0]+dt: break
        if a[0]>=nxt:
            c=cam[min(bisect.bisect(times,a[0]),len(cam)-1)]
            print(round(a[0]-w[0],2),round(c[3],1),round(wrap(a[2]-c[3]),1),round(f[4]),round(f[5]),round(f[6]));nxt+=0.25
for c in ('ion',):
    lag('ts30_'+c,5.5);lag('ts90_'+c,3.5);lag('ts300_'+c,2.6);lag('walkturn_'+c,2.8)
for c in ('pilot_pitch','pitchup_ion','pitchdn_ion','pitchup_ronin','pitchdn_ronin','pitchup_legion','pitchdn_legion'):
    w=win(tags,c)
    P=[x[2] for x in cam if w[0]<=x[0]<w[1]]
    print(c,'pitch min',round(min(P),2),'max',round(max(P),2))
for c in ('ion','ronin','legion'):
    w=win(tags,'dashl_'+c)
    R=[x[4] for x in cam if w[0]<=x[0]<w[1]]; print('dashl',c,'roll',round(min(R),2),round(max(R),2))
