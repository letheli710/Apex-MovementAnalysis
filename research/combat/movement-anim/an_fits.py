"""Movement and the held gun: sine fits of bob and sway, sprint exit against the first shot, sprint loop period, reload with movement minus reload standing.
  py -3 -I an_fits.py <gun-measure raw dir>"""
import gzip,csv,sys,math,statistics as st,collections,bisect,re
D=sys.argv[1]
K=('t','zf','fov','vmF','vmR','vmU','vmaP','vmaY','vmaR','cyc','seq','vx','vy','vz','ws','clip')
def load(s):
    wall=int(open(f'{D}/{s}/wall.txt').read().split()[0])/1000
    M=collections.defaultdict(list)
    for l in open(f'{D}/{s}/marks.tsv',encoding='utf8'):
        p=l.rstrip('\n').split('\t')
        if len(p)>=3:
            try:M[p[0]].append((float(p[1])-wall,p[2]))
            except:pass
    F=[]
    for x in csv.DictReader(gzip.open(f'{D}/{s}/frames.csv.gz','rt')):
        try:F.append({k:float(x[k] or 0) for k in K})
        except:pass
    return M,F,[f['t'] for f in F]
cut=lambda T,F,a,b:F[bisect.bisect_left(T,a):bisect.bisect_right(T,b)]
def seqs(fr):
    o=[]
    for f in fr:
        if not o or o[-1][0]!=f['seq']:o.append([int(f['seq']),f['t'],f['t'],f['cyc'],f['cyc']])
        o[-1][2]=f['t'];o[-1][4]=f['cyc']
    return o
def sinefit(fr,k,pmin,pmax):
    best=(1e18,None,None)
    t=[f['t'] for f in fr];v=[f[k] for f in fr];m=sum(v)/len(v);v=[x-m for x in v]
    p=pmin
    while p<=pmax:
        w=2*math.pi/p;ss=sum(math.sin(w*a)*b for a,b in zip(t,v));cc=sum(math.cos(w*a)*b for a,b in zip(t,v));n=len(t)
        a=2*ss/n;b=2*cc/n;r=sum((x-a*math.sin(w*y)-b*math.cos(w*y))**2 for x,y in zip(v,t))
        if r<best[0]:best=(r,p,math.hypot(a,b))
        p+=.002
    return round(best[1],3),round(best[2],3),round(m,3),round(math.sqrt(best[0]/len(t)),3)
M,F,T=load('s3')
print('=== bob sine fit (steady), period, amp, mean, rms')
for tag,a0,b0 in [('sw_r301_walk_hip',1.0,2.4),('sw_wingman_walk_hip',1.0,2.4),('sw_r301_crouchwalk_hip',1.0,2.4),('sw_wingman_crouchwalk_hip',1.0,2.4),('sw_r301_sprint_hip',1.0,2.7),('sw_wingman_sprint_hip',1.0,2.7),('sw_r301_walk_ads',1.5,2.4),('sw_wingman_walk_ads',1.5,2.4)]:
    if tag not in M:continue
    z=M[tag][0][0];fr=cut(T,F,z+a0,z+b0);print(tag,'zf %.2f spd %.0f'%(st.mean(f['zf'] for f in fr),st.mean(math.hypot(f['vx'],f['vy']) for f in fr)))
    for k in('vmF','vmR','vmU','vmaP','vmaY','vmaR'):print('  ',k,sinefit(fr,k,.25,1.2))
print('=== exit clip and fire: st_*_sprint_hip all guns: seq cut when fire')
shots=collections.defaultdict(list)
for x in csv.DictReader(open(f'{D}/s3/shots.csv')):
    try:shots['a'].append(float(x['t']))
    except:break
SH=sorted(shots['a'])
rows=[]
for tag in sorted(M):
    g=re.match(r'st_(\w+?)_(sprint|slide)_hip$',tag)
    if not g:continue
    mk=M[tag];a=mk[0][0];b=mk[-1][0];atk=[t for t,m in mk if m=='+attack']
    if not atk:continue
    fr=cut(T,F,a,b);s=seqs(fr);tk=atk[0];i=bisect.bisect_left(SH,tk);first=SH[i]-tk if i<len(SH) else None
    # seq active right after attack
    cutseq=[q for q in s if q[1]>=tk-.02 and q[1]<tk+.08]
    q=cutseq[0] if cutseq else None
    rows.append((tag,round(first,3) if first else None,q and (q[0],round(q[2]-q[1],3),round(q[4],2))))
for r in rows:print(r)
print('=== natural exit clip length sw_*: seq after -speed; slide clip')
for tag in sorted(M):
    g=re.match(r'sw_(\w+?)_(sprint|slide|sprintjump)_hip$',tag)
    if not g:continue
    a,b=M[tag][0][0],M[tag][-1][0];s=seqs(cut(T,F,a,b));print(tag,[(q[0],round(q[2]-q[1],2),round(q[3],2),round(q[4],2)) for q in s if q[2]-q[1]>.03])
print('=== sprint loop cycle: dcyc/dt with wrap')
for tag in('sw_r301_sprint_hip','sw_wingman_sprint_hip'):
    a,b=M[tag][0][0],M[tag][-1][0];fr=[f for f in cut(T,F,a,b)];ids=collections.Counter(f['seq'] for f in fr);sq=[q for q,_ in ids.most_common(2) if q not in(34,58)][0]
    fr=[f for f in fr if f['seq']==sq];tot=0;w=0
    for i in range(1,len(fr)):
        d=fr[i]['cyc']-fr[i-1]['cyc']
        if d<0:d+=1;w+=1
        tot+=d
    print(tag,'seq',sq,'turns %.2f in %.2f s -> period %.3f s wraps %d'%(tot,fr[-1]['t']-fr[0]['t'],(fr[-1]['t']-fr[0]['t'])/tot,w),'speed end',round(math.hypot(fr[-1]['vx'],fr[-1]['vy'])))
print('=== sway offset settle after stop (R-301 walk), fit tau on vmU, vmF, |aR|')
tag='sw_r301_walk_hip';mk=dict((m,t) for t,m in M[tag]);t0=mk['-forward']+.15;fr=cut(T,F,t0,t0+.75)
base={k:st.mean(f[k] for f in cut(T,F,M[tag][0][0]+.3,M[tag][0][0]+.33)) for k in('vmU','vmF')}
print(base)
for k in('vmU','vmF'):
    xs=[(f['t']-t0,abs(f[k]-base[k])) for f in fr if abs(f[k]-base[k])>1e-3];n=len(xs);sx=sum(x for x,_ in xs);sy=sum(math.log(y) for _,y in xs);sxx=sum(x*x for x,_ in xs);sxy=sum(x*math.log(y) for x,y in xs);print(k,'tau %.3f'%(-(n*sxx-sx*sx)/(n*sxy-sx*sy)))
print('=== jump/land vm path R301 sw_jump: min/max vs t')
tag='sw_r301_jump_hip';mk=dict((m,t) for t,m in M[tag]);t0=mk['+jump'];print([(s,)+tuple(round(st.mean(f[k] for f in cut(T,F,t0+s,t0+s+.03)),2) for k in('vmF','vmU','vmaP','vmaR','vz')) for s in(0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0,1.1,1.2)])
M,F,T=load('s4')
print('=== reload + motion: vm diff with standing, same reload cycle')
def rel(tag):
    a,b=M[tag][0][0],M[tag][-1][0];fr=[f for f in cut(T,F,a,b) if f['seq']==15];return fr
S=rel('rt_r301_tac_1');
def at(fr,c):
    v=[f for f in fr if abs(f['cyc']-c)<.012]
    return {k:st.mean(f[k] for f in v) for k in('vmF','vmR','vmU','vmaP','vmaY','vmaR')} if v else None
for tag in('rm_r301_tacwalk','rm_r301_tacsprint'):
    W=rel(tag);print(tag,'n',len(W),'cycle end',round(W[-1]['cyc'],2),'speed',round(st.mean(math.hypot(f['vx'],f['vy']) for f in W)))
    D_=[]
    for c in[x/20 for x in range(0,20)]:
        a=at(S,c);b=at(W,c)
        if a and b:D_.append((c,{k:b[k]-a[k] for k in a}))
    for k in('vmF','vmR','vmU','vmaP','vmaY','vmaR'):
        v=[d[1][k] for d in D_];print('  ',k,'diff min %.2f max %.2f mean %.2f'%(min(v),max(v),st.mean(v)))
