"""Sequence events: footsteps and anything else, per chassis locomotion and special sequences."""
import csv,os,re,struct
from anim53 import *
from joints import ROOT,CHASSIS,PARTS
def events(m,s):
    b=m.b;i=m.i
    if not s.numevents: return []
    out=[]
    for st in (0x50,0x54,0x58,0x110,0x114,0x118):
        ok=True;tmp=[]
        for k in range(s.numevents):
            o=s.off+s.eventindex+k*st
            c=struct.unpack_from('<f',b,o)[0]
            if not(-0.01<=c<=1.01): ok=False;break
            nameoff=i(o+st-4)
            tmp.append((round(c,3),i(o+4),i(o+8),cstr(b,o+12)[:60],cstr(b,o+nameoff)[:40] if 0<o+nameoff<len(b) else ''))
        if ok: return tmp
    return [('?',)]
rows=[]
for ch in CHASSIS:
  for part in PARTS[:-1]:
    p=os.path.join(ROOT,CHASSIS[ch]+'_'+part+'.mdl')
    if not os.path.exists(p): continue
    m=Mdl(p)
    for k in range(m.numlocalseq):
        s=Seq(m,k)
        an=s.anims(); 
        fr=Anim(m,an[len(an)//2]).frames if an else 0; fps=Anim(m,an[len(an)//2]).fps if an else 30
        ev=events(m,s)
        rows.append([ch,part,s.label,s.activity,fr,round(fps,1),round((fr-1)/fps,3) if fps else 0,round(s.fadein,3),round(s.fadeout,3),len(ev),' ; '.join(f"{e[0]}:{e[1]}:{e[3]}:{e[4]}" for e in ev)[:900] if ev and ev[0]!=('?',) else '?'])
csv.writer(open('out/sequences.csv','w',newline='',encoding='utf-8')).writerows([['ch','part','seq','activity','frames','fps','dur','fadein','fadeout','n_events','events']]+rows)
for r in rows:
    if r[0]=='medium' and r[2] in('Walk_forward_MP','Run_forward_MP','Sprint_mp_forward','at_MP_dodge_Start','at_MP_dodge_land','Jump_end_MP','at_mount_kneel_front','at_mount_stand_front','at_dismount_stand','at_dismount_crouch','at_MP_eject_stand_start','at_MP_stand2knee_straight','at_hotdrop_01','at_doomed_idle','at_player_melee_punch_01','at_MP_embark_start','at_MP_embark'):
        print(r)
