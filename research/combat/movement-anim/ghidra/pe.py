import struct,sys,re
import os
EXE=os.environ['R5_EXE']  # path to r5apex_dx12.exe
d=open(EXE,'rb').read()
pe=struct.unpack_from('<I',d,0x3c)[0]
ns=struct.unpack_from('<H',d,pe+6)[0]; osz=struct.unpack_from('<H',d,pe+20)[0]
base=0x140000000
secs=[]
o=pe+24+osz
for i in range(ns):
    name,vs,va,rs,ra=struct.unpack_from('<8sIIII',d,o+i*40)[:5]
    secs.append((name.rstrip(b'\0'),va,vs,ra,rs))
def v2o(v):
    r=v-base
    for n,va,vs,ra,rs in secs:
        if va<=r<va+max(vs,rs): return ra+r-va
def rd(v,n): o=v2o(v); return d[o:o+n]
if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='strs':
        a=int(sys.argv[2],16); b=int(sys.argv[3],16)
        blob=rd(a,b-a)
        for m in re.finditer(rb'[\x20-\x7e]{4,}',blob):
            print(hex(a+m.start()),m.group().decode())
    elif cmd=='f':
        for x in sys.argv[2:]:
            v=int(x,16); print(x,'f',struct.unpack('<f',rd(v,4))[0],'d',struct.unpack('<d',rd(v,8))[0])
    elif cmd=='grep':
        pat=sys.argv[2].encode()
        for m in re.finditer(re.escape(pat),d):
            print(hex(m.start()))
