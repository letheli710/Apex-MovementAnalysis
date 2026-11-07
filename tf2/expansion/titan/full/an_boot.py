"""Boot reveal timeline from g_boot frames: fraction of each screen block that is lit, against time since the cockpit started.
Usage: an_boot.py <run dir> <frame dir> <prefix> <t0>"""
import glob,os,re,sys
import numpy as np
from PIL import Image
run,fd,pre,t0=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4])
T={}
for l in open(os.path.join(run,'diag.tsv'),encoding='utf-8',errors='replace'):
    m=re.match(r'HSDDIAG CMD (\S+) jpeg t1_(%s_\d+)'%pre,l)
    if m: T[m.group(2)]=float(m.group(1))
B={'left':(0,.33,.2,.8),'mid':(.33,.66,.2,.8),'right':(.66,1,.2,.8),'top':(0,1,0,.2),'bottom':(0,1,.8,1),'all':(0,1,0,1)}
print('frame t '+' '.join(B))
for f in sorted(glob.glob(os.path.join(fd,'t1_%s_*.jpg'%pre))):
    n=os.path.basename(f)[3:-4]
    a=np.asarray(Image.open(f).convert('L'),float)
    H,W=a.shape
    r=[]
    for k,(x0,x1,y0,y1) in B.items():
        s=a[int(y0*H):int(y1*H),int(x0*W):int(x1*W)]
        r.append((s>35).mean())
    print(n,f"{T.get(n,0)-t0:+.3f}",' '.join(f"{v:.2f}" for v in r), f"mean={a.mean():.0f}")
