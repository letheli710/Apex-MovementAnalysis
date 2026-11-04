"""Movement and the held gun: steady ranges, sprint transitions, main sequences per run. Read-only on the gun-measure raw frames.
  py -3 -I an_sequences.py <gun-measure raw dir>"""
import gzip,csv,sys,math,statistics as st,collections,bisect,json
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
def cut(T,F,a,b): return F[bisect.bisect_left(T,a):bisect.bisect_right(T,b)]
def seqs(fr):
    o=[]
    for f in fr:
        if not o or o[-1][0]!=f['seq']:o.append([f['seq'],f['t'],f['t'],f['cyc'],f['cyc']])
        o[-1][2]=f['t'];o[-1][4]=f['cyc']
    return o
def period(fr,k):
    # dominant period by autocorrelation on a uniform 200 Hz grid
    if len(fr)<40:return None
    t=[f['t'] for f in fr];v=[f[k] for f in fr];m=sum(v)/len(v)
    n=int((t[-1]-t[0])*200);g=[];j=0
    for i in range(n):
        x=t[0]+i/200
        while j<len(t)-2 and t[j+1]<x:j+=1
        g.append(v[j]-m)
    best=(0,None);c0=sum(a*a for a in g) or 1
    for lag in range(30,min(n//2,300)):
        c=sum(g[i]*g[i+lag] for i in range(n-lag))/c0*n/(n-lag)
        if c>best[0]:
            best=(c,lag/200)
            
    return best[1],round(best[0],2)
def stats(fr):
    o={}
    for k in('vmF','vmR','vmU','vmaP','vmaY','vmaR'):
        v=[f[k] for f in fr];o[k]=(round(min(v),2),round(max(v),2))
    return o
M,F,T=load('s3')
print('--- steady windows + periods')
for tag,a0,b0 in [('sw_r301_stand_hip',.5,1.9),('sw_r301_walk_hip',1.0,2.4),('sw_r301_walk_ads',1.2,2.4),('sw_r301_sprint_hip',1.0,2.7),('sw_r301_crouchwalk_hip',1.0,2.4),('sw_r301_slide_hip',2.05,2.9),('sw_wingman_walk_hip',1.0,2.4),('sw_wingman_sprint_hip',1.0,2.7)]:
    if tag not in M:continue
    z=M[tag][0][0];fr=cut(T,F,z+a0,z+b0)
    spd=st.mean(math.hypot(f['vx'],f['vy']) for f in fr)
    print(tag,'spd %.0f zf %.2f'%(spd,st.mean(f['zf'] for f in fr)),stats(fr));print('   period',{k:period(fr,k) for k in('vmR','vmU','vmaP','vmaY','vmaR')})
print('--- fade: walk sway envelope after +forward / -forward (R-301)')
tag='sw_r301_walk_hip';z=M[tag][0][0];mk=dict((m,t) for t,m in M[tag]);
for name,t0 in(('+forward',mk['+forward']),('-forward',mk['-forward'])):
    for s in(0,.1,.2,.3,.4,.6,.8,1.0):
        fr=cut(T,F,t0+s,t0+s+.1)
        if fr:print(name,s,'R %.2f U %.2f F %.2f aR %.2f spd %.0f'%(st.mean(f['vmR'] for f in fr),st.mean(f['vmU'] for f in fr),st.mean(f['vmF'] for f in fr),st.mean(f['vmaR'] for f in fr),st.mean(math.hypot(f['vx'],f['vy']) for f in fr)))
print('--- sprint enter/exit path; 63 cycle rate; max frame step')
for g,tag in(('r301','sw_r301_sprint_hip'),('wing','sw_wingman_sprint_hip')):
    mk=dict((m,t) for t,m in M[tag]);a=mk['+speed'];b=mk['-speed']
    for lab,t0,dur in(('enter',a,.8),('exit',b,.8)):
        print(g,lab,[ (round(s,2),)+tuple(round(st.mean(f[k] for f in cut(T,F,t0+s,t0+s+.03)),2) for k in('vmF','vmR','vmU','vmaP','vmaY','vmaR')) for s in(-.05,0,.05,.1,.15,.2,.25,.3,.35,.4,.5,.6,.8)])
    fr=cut(T,F,a+.05,b-.05);c=[(f['t'],f['cyc']) for f in fr if f['seq']==fr[len(fr)//2]['seq']]
    print(g,'cyc rate /s',(c[-1][1]-c[0][1])/(c[-1][0]-c[0][0]),'speed',round(st.mean(math.hypot(f['vx'],f['vy']) for f in fr)))
    fr=cut(T,F,a-.2,b+.6);print(g,'max step per frame F,R,U',[round(max(abs(fr[i][k]-fr[i-1][k]) for i in range(1,len(fr))),3) for k in('vmF','vmR','vmU')])
print('--- all seqs in other runs')
for tag in['s2_r301_mantle_hip','s2_r301_zipline_hip','s2_r301_grapple_hip','s2_r301_stim_hip','s2_r301_launch_hip','st_r301_sprint_hip','st_r301_slide_hip','st_r301_walk_hip']:
    if tag not in M:continue
    a,b=M[tag][0][0],M[tag][-1][0];fr=cut(T,F,a,b);print(tag,[(int(q[0]),round(q[1]-a,2),round(q[2]-a,2),round(q[3],2),round(q[4],2)) for q in seqs(fr)][:16],[(round(t-a,2),m) for t,m in M[tag] if m[0] in '+-'])
M,F,T=load('s4')
print('--- s4 movement + reload')
for tag in sorted(M):
    if tag.startswith(('rm_r301','rc_r301_sprint','rc_r301_jump','rt_r301_tac_1','rc_r301_ads')):
        a,b=M[tag][0][0],M[tag][-1][0];fr=cut(T,F,a,b)
        print(tag,[(int(q[0]),round(q[1]-a,2),round(q[2]-a,2),round(q[3],2),round(q[4],2)) for q in seqs(fr)][:14],[(round(t-a,2),m) for t,m in M[tag] if m[0] in '+-'],'maxspd %.0f'%max([math.hypot(f['vx'],f['vy']) for f in fr] or [0]))
