"""How aiming is shared across the body: neutral aim pose + delta grid, joint changes vs neutral."""
import csv,math,os,sys
from anim53 import *
from joints import *
OUT='out'
def apply(base,delta,m):
    r=[]
    for n in range(m.numbones):
        b=base[n]; d=delta[n]
        if b is None: b=(m.bones[n]['pos'],m.bones[n]['quat'])
        if d is None: r.append(b); continue
        r.append((tuple(b[0][k]+d[0][k] for k in range(3)),qmul(b[1],d[1])))
    return r
rows=[]
for ch in CHASSIS:
    m=Mdl(os.path.join(ROOT,CHASSIS[ch]+'_mp_core.mdl')); rig=Rig(m)
    anims={Anim(m,k).name:Anim(m,k) for k in range(m.numlocalanim)}
    sets=[('stand','a_aim_stand'),('ads','a_ADS_stand'),('crouch','a_aim_crouch')]
    print(ch,'seqs',[ (Seq(m,k).label,Seq(m,k).paramstart,Seq(m,k).paramend) for k in range(m.numlocalseq) if Seq(m,k).label in('MP_stand_Aim_all','MP_ADS_stand_Aim_all','MP_crouch_Aim_all')])
    for name,pre in sets:
        if pre+'_neutral_MP' not in anims: print('no',pre); continue
        base=anims[pre+'_neutral_MP'].local(0)
        W0=world(m,base); M0=metrics(rig,W0)
        for pose in ['mid_center','mid_left','mid_right','up_center','up_left','up_right','down_center','down_left','down_right','straightup']:
            a=anims.get(f'{pre}_{pose}_MP')
            if a is None: continue
            W=world(m,apply(base,a.local(0),m)); M=metrics(rig,W)
            d=lambda k:round(M[k]-M0[k],1)
            rows.append([ch,name,pose,d('chest_yaw'),d('chest_pitch'),d('chest_roll'),d('pelvis_yaw'),d('pelvis_pitch'),d('waist_twist'),d('waist_bend'),d('neck_yaw'),d('neck_pitch'),d('head_yaw'),d('head_pitch'),d('r_sh_elev'),d('r_elbow'),d('l_sh_elev'),d('l_elbow'),d('hip_z'),round(M['r_elbow'],1),round(M['r_sh_elev'],1)])
csv.writer(open(OUT+'/aim_grid.csv','w',newline='')).writerows([['ch','set','pose','chest_yaw','chest_pitch','chest_roll','pelvis_yaw','pelvis_pitch','waist_twist','waist_bend','neck_yaw','neck_pitch','head_yaw','head_pitch','r_sh_elev','r_elbow','l_sh_elev','l_elbow','hip_z','abs_r_elbow','abs_r_sh_elev']]+rows)
for r in rows:
    if r[1]=='stand': print(r)
