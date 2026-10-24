"""N6 camera trials: max roll, camera-eye position and angle offsets per trial. Run inside a session folder.

  py -3 <this file>   (cwd = phase2-local/data/<session>)
Standard library only. Part of rea-native N6 (n6/N6-MEASURE.md).
"""
import re,glob,math,json
KV=re.compile(r"([A-Za-z_0-9]+)=(\S+)")
fr={}
for f in glob.glob('platform/logs/client/*/*.log'):
    for l in open(f,encoding='utf-8',errors='replace'):
        if 'kind=frame' in l and 'side=cl' in l and 'cang=' in l:
            k=dict(KV.findall(l)); fr.setdefault(k.get('run'),[]).append(k)
v=lambda s:tuple(map(float,s.split(',')))
names={str(t['run']):t['schedule'] for t in json.load(open('runner.json'))['trials']}
for run in sorted(fr,key=lambda r:int(r) if r.isdigit() else 0):
    R=sorted(fr[run],key=lambda k:float(k['t']))
    if names.get(run) is None: continue
    rolls=[v(k['cang'])[2] for k in R]; dp=[math.dist(v(k['cpos']),v(k['epos'])) for k in R]
    dang=[max(abs(a-b) for a,b in zip(v(k['cang'])[:2],v(k['eang'])[:2])) for k in R]
    i=max(range(len(rolls)),key=lambda i:abs(rolls[i]))
    print(names[run],run,'max|roll| %.3f (spd %.0f sprint %s)'%(rolls[i],float(R[i]['spd2d']),R[i]['sprint']),'max|cpos-epos| %.3f'%max(dp),'max|cang-eang| pitch/yaw %.3f'%max(dang))
