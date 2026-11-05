import sys,os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vmcal import *
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
L=Link()
L.give(INFO["r301"]["id"])
L.cl('SetConVarInt( "r_drawviewmodel", 1 ); SetConVarInt( "mat_fullbright", 1 ); SetConVarFloat( "cl_fovScale", 1.27 )')
L.sv('entity p = GetPlayerArray()[0]; p.SetPhysics( MOVETYPE_WALK ); p.SetOrigin( <-11699, 512, 1579> ); p.SetVelocity( <0, 0, 0> ); p.SnapEyeAngles( <0, 0, 0> )')
L.sleep(0.8)
L.cl('GetLocalClientPlayer().ClientCommand( "+zoom" )', 0.1); L.sleep(1.2)
for i,a in enumerate([(-30,0),(-60,0),(0,90),(-40,90),(-15,-90),(0,180),(-45,180),(-5,20)]):
    L.sv(f'entity p = GetPlayerArray()[0]; p.SnapEyeAngles( <{a[0]}, {a[1]}, 0> )'); L.sleep(0.8)
    shot(L,os.path.join(out,f"bg{i}.png"))
L.cl('GetLocalClientPlayer().ClientCommand( "-zoom" )',0.3)
from PIL import Image
s=Image.new('RGB',(1600,800))
for i in range(8):
    s.paste(Image.open(os.path.join(out,f"bg{i}.png")).resize((400,225)),((i%4)*400,(i//4)*400))
s.save(os.path.join(out,"sheet.png"))
