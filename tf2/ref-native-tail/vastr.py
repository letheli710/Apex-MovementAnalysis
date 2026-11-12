import sys,struct
def load(p):
    b=open(p,'rb').read()
    pe=struct.unpack_from('<I',b,0x3c)[0]
    ns=struct.unpack_from('<H',b,pe+6)[0]; opt=struct.unpack_from('<H',b,pe+20)[0]
    base=struct.unpack_from('<Q',b,pe+24+24)[0]
    secs=[]
    o=pe+24+opt
    for i in range(ns):
        vs,va,rs,ra=struct.unpack_from('<IIII',b,o+8); secs.append((va,max(vs,rs),ra)); o+=40
    return b,base,secs
def off(b,base,secs,va):
    r=va-base
    for v,s,ra in secs:
        if v<=r<v+s: return r-v+ra
b,base,secs=load(sys.argv[1])
mode=sys.argv[2]
for a in sys.argv[3:]:
    o=off(b,base,secs,int(a,16))
    if mode=='s': print(a, repr(b[o:b.index(b'\0',o)].decode('latin1')))
    elif mode=='f': print(a, struct.unpack_from('<f',b,o)[0])
    elif mode=='d': print(a, struct.unpack_from('<d',b,o)[0])
