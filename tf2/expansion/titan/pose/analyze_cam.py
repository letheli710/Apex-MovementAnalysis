"""Per-tag camera, cockpit, FOV and body numbers from a t1_cam run. Usage: analyze_cam.py <run dir>"""
import csv,math,re,sys,os
from collections import defaultdict
run=sys.argv[1]
cam=[];ck=[];bd=defaultdict(list);tags=[];cmds=[];tt=[]
for l in open(os.path.join(run,'diag.tsv'),encoding='utf-8',errors='replace'):
    p=l.split()
    if len(p)<3: continue
    k=p[1]
    if k=='CAM' and len(p)>=9: cam.append((float(p[2]),int(p[3]),*map(float,p[4:10])))
    elif k=='CK' and len(p)>=9: ck.append((float(p[2]),*map(float,p[3:10])))
    elif k=='BD' and len(p)>=10: bd[p[3]].append((float(p[2]),*map(float,p[4:10])))
    elif k=='CMD':
        c=' '.join(p[3:]); t=float(p[2])
        cmds.append((t,c))
        if c.startswith('hsd_tag '): tags.append((t,c.split()[1]))
    elif k=='TT' and len(p)>=8: tt.append((float(p[2]),int(p[3]),float(p[4]),int(p[5]),int(p[6]),int(p[7])))
print(len(cam),len(ck),len(tags),{k:len(v) for k,v in bd.items()})
def wrap(a):
    return (a+180)%360-180
rows=[]
for i,(t0,name) in enumerate(tags):
    t1=tags[i+1][0] if i+1<len(tags) else t0+3
    C=[c for c in cam if t0<=c[0]<t1]
    K=[c for c in ck if t0<=c[0]<t1]
    if not C: continue
    # baseline: first 3 frames
    yaw0=C[0][3]; pit0=C[0][2]
    roll=[c[4] for c in C]; pit=[wrap(c[2]-pit0) for c in C]; yaw=[wrap(c[3]-yaw0) for c in C]; dz=[c[7] for c in C]; dx=[c[5] for c in C]; dy=[c[6] for c in C]
    fov=[k[1] for k in K] or [0]
    kz=[k[7] for k in K] or [0]; kx=[k[5] for k in K] or [0]; ky=[k[6] for k in K] or [0]
    kr=[k[4] for k in K] or [0];kp=[k[2] for k in K] or [0]
    # time of extreme roll and when back within 10 %
    b=lambda v:(round(min(v),2),round(max(v),2))
    tr=C[max(range(len(C)),key=lambda j:abs(roll[j]))][0]-t0
    tp=C[max(range(len(C)),key=lambda j:abs(pit[j]))][0]-t0
    rows.append(dict(tag=name,dur=round(t1-t0,2),titan=C[-1][1],roll=b(roll),roll_t=round(tr,2),pitch=b(pit),pitch_t=round(tp,2),yaw=b(yaw),dz=b(dz),dxy=(round(max(map(abs,dx)),2),round(max(map(abs,dy)),2)),fov=b(fov),ck_z=b(kz),ck_xy=(round(max(map(abs,kx)),2),round(max(map(abs,ky)),2)),ck_rp=(b(kr),b(kp))))
w=csv.DictWriter(open('expansion/titan/pose/out/cam_by_tag.csv','w',newline=''),fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
for r in rows: print(r)
# Body yaw vs camera yaw per tag
print()
for i,(t0,name) in enumerate(tags):
    t1=tags[i+1][0] if i+1<len(tags) else t0+3
    if not re.match(r'(idle|walk|sprint|back|strafe|turn\d+|crouch|ads|fire|dashf|dashr|dashb|doom)_',name): continue
    C=[c for c in cam if t0<=c[0]<t1]
    if not C: continue
    A=[b for b in bd['CHESTFOCUS'] if t0<=b[0]<t1]
    H=[b for b in bd['HEADFOCUS'] if t0<=b[0]<t1]
    FL=[b for b in bd['foot_L_sole'] if t0<=b[0]<t1]; FR=[b for b in bd['foot_R_sole'] if t0<=b[0]<t1]
    HR=[b for b in bd['HAND_R'] if t0<=b[0]<t1]
    if not A: continue
    cy=C[-1][3]
    chest=[wrap(a[2]-cy) for a in A[-40:]]; 
    cz=[a[6] for a in A]; cp=[a[1] for a in A]; cr=[a[3] for a in A]
    fx=lambda F:(round(min(f[4] for f in F)),round(max(f[4] for f in F)),round(max(f[6] for f in F)))
    print(name,'cam_yaw',round(cy,1),'chest-cam yaw end',round(sum(chest)/len(chest),1),'chestZ',round(min(cz),1),round(max(cz),1),'chestP',round(min(cp),1),round(max(cp),1),'chestR',round(min(cr),1),round(max(cr),1),'footL xminmax,zmax',fx(FL),'footR',fx(FR),'first-chest-yaw',round(wrap(A[0][2]-cy),1),'mid',round(wrap(A[len(A)//2][2]-cy),1))
