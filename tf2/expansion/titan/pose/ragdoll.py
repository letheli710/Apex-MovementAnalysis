import re,sys,os,csv
ROOT='../../../local/titan-models/models/titans/'
files={'light':'light/titan_light_locust.mdl','light(ronin)':'light/titan_light_raptor.mdl','medium':'medium/titan_medium_vanguard.mdl','medium(ajax)':'medium/titan_medium_ajax.mdl','heavy':'heavy/titan_heavy_ogre.mdl'}
out=[]
for k,f in files.items():
    b=open(ROOT+f,'rb').read()
    txt=b.decode('latin1')
    start=txt.find('solid {')
    end=txt.find('editparams',start)
    t=txt[start:end if end>0 else start+60000]
    solids={}
    for m in re.finditer(r'solid \{\s*"index" "(\d+)"\s*"name" "([^"]+)"\s*"parent" "([^"]*)"\s*"mass" "([\d.]+)"',t):
        solids[int(m[1])]=(m[2],m[3],float(m[4]))
    print('==',k,len(solids),'solids; total mass',round(sum(v[2] for v in solids.values())))
    for m in re.finditer(r'ragdollconstraint \{\s*"parent" "(\d+)"\s*"child" "(\d+)"\s*"xmin" "([-\d.]+)"\s*"xmax" "([-\d.]+)"\s*"xfriction" "[-\d.]+"\s*"ymin" "([-\d.]+)"\s*"ymax" "([-\d.]+)"\s*"yfriction" "[-\d.]+"\s*"zmin" "([-\d.]+)"\s*"zmax" "([-\d.]+)"',t):
        p,c=int(m[1]),int(m[2])
        row=(k,solids[p][0],solids[c][0])+tuple(round(float(m[i])) for i in range(3,9))
        print(f"{solids[c][0]:22s} parent {solids[p][0]:20s} x {row[3]:4d}..{row[4]:4d}  y {row[5]:4d}..{row[6]:4d}  z {row[7]:4d}..{row[8]:4d}")
        out.append(row)
os.makedirs('out',exist_ok=True)
csv.writer(open('out/ragdoll_limits.csv','w',newline='')).writerows([('titan','parent','child','xmin','xmax','ymin','ymax','zmin','zmax')]+out)
