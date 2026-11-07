"""Landing camera per tag. Usage: an_land.py <run dir>"""
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from g_tools import *
import numpy as np
d,c=load(sys.argv[1])
CAM=np.array([x[:8] for x in d['CAM']]);C=np.array([x[:9] for x in d['C']]);GK=[x for x in d['GK'] if len(x)>=8]
G=np.array([x[:8] for x in GK])
print('tag land_t h_start z_land vz cam: pPeak tPeak pMin pos_u_min dur(<0.05) | ck: uPeak pPeak | speed')
for a,b,n in tags(c):
    if not n.startswith('land'): continue
    S=C[(C[:,0]>=a)&(C[:,0]<b)]
    if len(S)<5: continue
    gr=S[:,9-1] if False else S[:,7+2-1] if False else None
    # C columns: t ox oy oz vx vy vz pitch yaw ground...
    full=np.array([x[:10] for x in d['C'] if a<=x[0]<b])
    gd=full[:,9]
    idx=[i for i in range(1,len(full)) if gd[i]==1 and gd[i-1]==0]
    if not idx: print(n,'no landing');continue
    i=idx[-1]; tl=full[i,0]; vz=full[i-1,6]; z0=full[:i,3].max(); zl=full[i,3]; h=z0-zl
    K=CAM[(CAM[:,0]>=tl-0.05)&(CAM[:,0]<tl+2.0)]
    t=K[:,0]-tl; base=np.median(CAM[(CAM[:,0]>=a-0.5)&(CAM[:,0]<a),2]) if ((CAM[:,0]>=a-0.5)&(CAM[:,0]<a)).any() else K[0,2]
    p=K[:,2]-K[0,2]; dz=K[:,7]-K[0,7]; r=K[:,4]-K[0,4]; y=(K[:,3]-K[0,3]+180)%360-180
    ip=np.argmax(np.abs(p)); iz=np.argmax(np.abs(dz))
    after=[j for j in range(len(p)) if t[j]>t[ip] and abs(p[j])<0.05*max(abs(p[ip]),1e-3)]
    over=p[ip:].min()*np.sign(p[ip]) if len(p[ip:]) else 0
    gk=G[(G[:,0]>=tl-0.05)&(G[:,0]<tl+2.0)]
    gu=(gk[:,4]-gk[0,4]) if len(gk) else np.zeros(1); gp=(gk[:,5]-gk[0,5]) if len(gk) else np.zeros(1)
    sp=np.hypot(full[:,4],full[:,5]); sb=sp[i-1]; smin=sp[i:].min() if i<len(sp) else 0; 
    print(f"{n:22s} h={h:6.1f} vz={vz:7.1f} p={p[ip]:+6.2f}@{t[ip]:.3f} over={over:+5.2f} back5%@{(t[after[0]] if after else -1):.2f} dz={dz[iz]:+6.2f}@{t[iz]:.3f} roll={np.abs(r).max():.2f} yaw={np.abs(y).max():.2f} ck_u={gu[np.argmax(np.abs(gu))]:+5.2f} ck_p={gp[np.argmax(np.abs(gp))]:+5.2f} sp {sb:.0f}->{smin:.0f}")
