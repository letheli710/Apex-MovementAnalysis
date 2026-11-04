import sys,re,os,json; sys.path.insert(0,'.')
from sl import *
W=os.path.expanduser("~/Games/R5Flowstate/platform/scripts/weapons/")
IDS=json.load(open(r"C:\Workspace\Playground\ReApex-DataAnalysis\HSD-Unity-GUNMODEL\Docs\tools\gun-models\r5_dims.json"))["guns"]
guns={k:g["id"] for k,g in IDS.items()}
guns["mounted_turret"]="mp_weapon_mounted_turret_weapon"; guns["vantage"]="mp_ability_sniper_ult"
L=Link()
out={}
for s,wid in guns.items():
    t=open(W+wid+".txt",encoding="utf-8",errors="replace").read()
    head=t.split('"Mods"')[0]
    vm=re.search(r'"viewmodel"\s+"([^"]+)"',head)[1]
    names=sorted(set(re.findall(r'"bodygroup\d+_name"\s+"([^"]+)"',t)))
    sets={m[1]:None for m in re.finditer(r'"bodygroup(\d+)_name"\s+"([^"]+)"',head)}
    nm={m[1]:m[2] for m in re.finditer(r'"bodygroup(\d+)_name"\s+"([^"]+)"',head)}
    dflt={nm[m[1]]:m[2] for m in re.finditer(r'"bodygroup(\d+)_set"\s+"([^"]+)"',head)}
    names=[n for n in names]
    code='entity q = CreateClientSidePropDynamic( <0,0,25000>, <0,0,0>, $"%s" )\nprintt( "[RT] model " + q.GetModelName() )\n'%vm
    for n in names:
        code+='{ int i = q.FindBodygroup( "%s" ); if ( i >= 0 ) printt( "[RT] bg %s idx=" + i + " n=" + q.GetBodygroupModelCount( i ) ) }\n'%(n,n)
    code+='q.Destroy()\n'
    r=L.cl(code,0.25)
    bg={m[1]:{"idx":int(m[2]),"n":int(m[3]),"set":dflt.get(m[1])} for m in (re.search(r'bg (\S+) idx=(-?\d+) n=(\d+)',x) for x in r) if m}
    err=[x for x in r if "ERR" in x]
    out[s]={"id":wid,"vm":vm,"bg":bg,"err":err}
    print(s,vm.split('/')[-1],{k:(v['n'],v['set']) for k,v in bg.items() if not k.startswith(('suppressor','barrel','stock','mag','clip','hopup','laser'))},err,flush=True)
json.dump(out,open("bg_scan.json","w"),indent=1)
