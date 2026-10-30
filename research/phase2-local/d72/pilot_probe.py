import sys,re,glob,json
sys.path.insert(0,'../b1'); import analyze_b1 as B
R=re.compile(r"kind=frame run=(\d+) seq=\d+ t=([\d.]+) .*?o=([-\d.]+),([-\d.]+),([-\d.]+) .*?crouch=(\d) .*?epos=([-\d.]+),([-\d.]+),([-\d.]+)")
for D in sys.argv[1:]:
    s=B.load_session(D); man=json.load(open(D+'/runner.json',encoding='utf-8'))
    md={}
    for f in glob.glob(D+'/platform/logs/client/*/script.log'):
        for ln in open(f,encoding='utf-8',errors='replace'):
            m=R.search(ln)
            if m: g=m.groups(); md.setdefault(int(g[0]),[]).append((float(g[1]),float(g[4]),int(g[5]),float(g[8])-float(g[4])))
    for tr in man['trials']:
        run=tr['run']
        if run not in s['frames'] or tr.get('warmup'): continue
        fr=[s['frames'][run][k] for k in sorted(s['frames'][run])]; blk=[f for f in fr if f['mant']]
        if not blk: print(run,tr['schedule'],'NO MANTLE'); continue
        t0=blk[0]['t']; t1=blk[-1]['t']
        td=next((float(re.search(r' t=([\d.]+)',l).group(1)) for l in tr['sched_lines'] if 'key=duck' in l and 'edge=down' in l),None)
        rows=sorted(md.get(run,[]))
        snap=next((rows[i][0] for i in range(1,len(rows)) if rows[i][2]==1 and rows[i-1][2]==0 and (td is None or rows[i][0]>td)),None)
        print(run, tr['schedule'][4:], 'dur %.3f'%(t1-t0), 'lead', None if td is None else '%.3f'%(t0-td), 'snap-m0', None if snap is None else '%.3f'%(snap-t0),
              'snap-td', None if snap is None or td is None else '%.3f'%(snap-td), 'end-snap', None if snap is None else '%.3f'%(t1-snap), 'ztop %.2f'%blk[-1]['z'])
