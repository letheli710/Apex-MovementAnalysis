import json, os, re, sys
W = os.path.expanduser("~/Games/R5Flowstate/platform/scripts/weapons/")
info = json.load(open(sys.argv[1], encoding="utf-8"))
keys = ["zoom_fov","zoom_toggle_fov","zoom_fov_viewmodel","viewmodel_offset_ads","viewmodel_offset_ads_by_centerpoint","viewmodel_ads_centerpoint_attachment","zoom_time_in"]
rows=[]; bg={}
def block(t, start):
    i=t.index("{",start); d=0
    for j in range(i,len(t)):
        if t[j]=="{": d+=1
        elif t[j]=="}":
            d-=1
            if d==0: return t[i+1:j]
    return t[i+1:]
for g,i in info.items():
    t=open(W+i["id"]+".txt",encoding="utf-8",errors="replace").read()
    num={m[1]:m[2] for m in re.finditer(r'"bodygroup(\d+)_name"\s+"([^"]+)"',t)}
    head=t.split('"Mods"')[0]
    def f(k,s): 
        m=re.search(r'"%s"\s+"([^"]*)"'%k,s); return m[1] if m else ""
    rows.append([g,"(iron)"]+[f(k,head) for k in keys]+["",""])
    for m in re.finditer(r'"(optic_[a-z0-9_]+)"\s*\n?\s*\{',t):
        b=block(t,m.start())
        on=[num.get(x[1],x[1]) for x in re.finditer(r'"bodygroup(\d+)_set"\s+"1"',b)]
        off=[num.get(x[1],x[1]) for x in re.finditer(r'"bodygroup(\d+)_set"\s+"0"',b)]
        rows.append([g,m[1]]+[f(k,b) for k in keys]+[",".join(on),",".join(off)])
out=sys.argv[2]
with open(out,"w",encoding="utf-8",newline="\n") as fh:
    fh.write("\t".join(["gun","mod"]+keys+["bodygroup_on","bodygroup_off"])+"\n")
    for r in rows: fh.write("\t".join(r)+"\n")
print(len(rows))
