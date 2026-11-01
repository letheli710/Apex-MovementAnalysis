import sys,re,statistics as st
d={}
for l in open(sys.argv[1]):
    m=re.search(r'k=(\d) sev=([\d.]+) t=([\d.]+) spd=([\d.]+) getsev=([\d.]+) sprint=(\d) gnd=(\d)',l)
    if m:
        k,s,t,v,g,sp,gn=m.groups(); d.setdefault((k,s),[]).append((float(t),float(v),g,sp))
for (k,s),rows in d.items():
    late=[v for t,v,g,sp in rows if t>2.0]
    print(k,s,'n',len(rows),'median t>2:',round(st.median(late),2),'getsev',rows[-1][2],'sprint(t>2)',set(sp for t,v,g,sp in rows if t>2))
