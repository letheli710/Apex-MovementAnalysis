"""Cockpit attachment relative to the camera, step phase. Usage: an_sway.py <run dir>"""
import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from g_tools import load,tags
import numpy as np
d,c=load(sys.argv[1])
CAM=np.array([x[:8] for x in d['CAM']]);G=np.array([x[:14] for x in d['GK'] if len(x)>=14]);C=np.array([x[:10] for x in d['C']])
FL=np.array([x[:7] for x in d['BD_foot_L_sole']]);FR=np.array([x[:7] for x in d['BD_foot_R_sole']])
print("tag | ck f r u p y r: mean(last half) & range | cam: dz range pitch range yaw-speed")
for a,b,n in tags(c):
    if not n.startswith('sw_'): continue
    g=G[(G[:,0]>=a)&(G[:,0]<b)]
    K=CAM[(CAM[:,0]>=a)&(CAM[:,0]<b)]
    if len(g)<10: continue
    v=g[:,2:8]; base=v[0]
    print(f"{n:22s} max|Δ| {np.round(np.abs(v-base).max(0),2)} peakΔ {np.round((v-base)[np.abs(v-base).argmax(0),range(6)],2)} | cam dz {np.ptp(K[:,7]):.2f} roll {np.ptp(K[:,4]):.2f} pitchΔ {np.ptp(K[:,2]):.2f}")
# step phase: foot contact (speed goes to ~0) against camera dz, walk tags
print()
for a,b,n in tags(c):
    if not (n.endswith('walk') or n.endswith('sprint')): continue
    if not n.startswith('sw_'): continue
    K=CAM[(CAM[:,0]>=a+1.0)&(CAM[:,0]<a+3.3)]
    for name,F in (('L',FL),('R',FR)):
        f=F[(F[:,0]>=a+1.0)&(F[:,0]<a+3.3)]
        tt=f[:,0]; z=f[:,6]; x=f[:,4];y=f[:,5]
        # world-relative foot speed: body moves, so use height minima
        i=[j for j in range(2,len(z)-2) if z[j]<=z[j-1] and z[j]<z[j+1] and z[j]<z.min()+6]
        print(n,name,'foot z min',round(z.min(),1),'max',round(z.max(),1),'contact t',[round(tt[j]-a,3) for j in i][:8])
    t=K[:,0]-a; dz=K[:,7]-np.median(K[:,7])
    im=[j for j in range(2,len(dz)-2) if dz[j]<dz[j-1] and dz[j]<=dz[j+1] and dz[j]<dz.min()*0.6]
    ip=[j for j in range(2,len(dz)-2) if dz[j]>dz[j-1] and dz[j]>=dz[j+1] and dz[j]>dz.max()*0.6]
    print(n,'cam dz range',round(np.ptp(K[:,7]),2),'min t',[round(t[j],3) for j in im][:8],'max t',[round(t[j],3) for j in ip][:8])
    g=G[(G[:,0]>=a+1.0)&(G[:,0]<a+3.3)]
    print('   ck u range',round(np.ptp(g[:,4]),2),'p',round(np.ptp(g[:,5]),2),'r',round(np.ptp(g[:,7]),2), 'f',round(np.ptp(g[:,2]),2),' r',round(np.ptp(g[:,3]),2))
