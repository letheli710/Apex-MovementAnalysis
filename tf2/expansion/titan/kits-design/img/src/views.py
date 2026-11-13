# blender -b <blend> -P views.py -- <tag> <outdir>
import bpy, sys, math, json, mathutils
from bpy_extras.object_utils import world_to_camera_view
argv = sys.argv[sys.argv.index("--")+1:]
tag, out = argv[0], argv[1]
sc = bpy.context.scene
O = bpy.data.objects
def rotx(name, deg):
    o=O[name]; o.rotation_mode='XYZ'; o.rotation_euler.x += math.radians(deg)
def wings(open_):
    for side,ax,s in (("L",(-0.441,-0.829,0.343),-1),("R",(0.441,-0.829,0.343),1)):
        o=O["J_Wing_"+side]; o.rotation_mode='QUATERNION'
        o.rotation_quaternion=mathutils.Quaternion(mathutils.Vector(ax).normalized(), s*math.radians(86.4 if open_ else 0))
if tag in ("H1","H2"):
    rotx("J_Elbow_R",-90); rotx("J_Elbow_L",-75)
bpy.context.view_layer.update()
W = lambda n: O[n].matrix_world.translation.copy() if n in O else None
# ---- proposal parts (model-change candidates), Blender coords: X=left, -Y=forward, Z=up
mat = bpy.data.materials.new("PROPOSAL"); mat.diffuse_color=(1.0,0.0,0.85,1)
props=[]
def box(name, loc, size, parent=None, rot=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob=bpy.context.active_object; ob.name="P_"+name; ob.scale=size; ob.data.materials.append(mat)
    if rot: ob.rotation_euler=rot
    props.append(ob.name); return ob
def cyl(name, loc, r, depth, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=24)
    ob=bpy.context.active_object; ob.name="P_"+name; ob.data.materials.append(mat); props.append(ob.name); return ob
extra={}
if tag=="L2":
    sb=W("S_Sword_Back"); t=W("J_Torso")
    # rack arm: hinge on upper back right, arm runs to the hilt
    mid=(sb+mathutils.Vector((t.x-0.35,t.y+0.55,sb.z-0.25)))/2
    box("SwordRack", mid, (0.22,0.22,0.9), rot=(math.radians(25),0,math.radians(10)))
    extra["P_RackHinge"]=mathutils.Vector((t.x-0.35,t.y+0.55,sb.z-0.25))
if tag=="H1":
    a=W("W_Cannon"); m=W("S_Muzzle"); c=a+(m-a)*0.35
    cyl("Cylinder3", c, 0.42, 0.55, rot=(math.radians(90),0,0)); extra["P_Cylinder3"]=c
    t=W("J_Torso")
    for i,dx in enumerate((-0.45,0,0.45)):
        box("HearthVent%d"%i, (t.x+dx, t.y-1.05, t.z+0.25), (0.26,0.12,0.16))
    extra["P_HearthVents"]=mathutils.Vector((t.x, t.y-1.12, t.z+0.25))
if tag=="H2":
    g=W("S_GunShield"); m=W("S_Muzzle")
    d=(m-g).normalized()
    cyl("ChokeSleeve", g+d*0.15, 0.62, 0.35, rot=(math.radians(90),0,0))
    extra["P_ChokeSleeve"]=g+d*0.15
    cyl("MuzzleRing", m-d*0.12, 0.70, 0.08, rot=(math.radians(90),0,0)); extra["P_MuzzleRing"]=m-d*0.12
bpy.context.view_layer.update()
# ---- sockets
names=[o.name for o in O if (o.name.startswith(("S_","W_","J_Wing","J_Barrel","J_Drum")))]
pts={n:W(n) for n in names}; pts.update(extra)
# ---- render setup
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_cavity=True; sh.show_shadows=False; sh.show_object_outline=True
sc.render.resolution_x=760; sc.render.resolution_y=900; sc.render.film_transparent=True
w=bpy.data.worlds.new("w"); sc.world=w; w.color=(0.86,0.87,0.88)
sh.background_type='WORLD' if hasattr(sh,'background_type') else None
cam=bpy.data.objects.new("CAM", bpy.data.cameras.new("CAM")); sc.collection.objects.link(cam); sc.camera=cam
cam.data.type='ORTHO'; cam.data.ortho_scale=8.6 if tag.startswith("L") else 8.0
cz=3.0
views={"front":((0,-30,cz),(math.radians(90),0,0)),
       "side":((30,0,cz),(math.radians(90),0,math.radians(90))),   # from titan's left (+X)
       "back":((0,30,cz),(math.radians(90),0,math.radians(180)))}
res={"tag":tag,"W":760,"H":900,"views":{}}
def render(vname, suffix=""):
    loc,rot=views[vname]; cam.location=loc; cam.rotation_euler=rot
    # centre horizontally on the model bbox
    bpy.context.view_layer.update()
    sc.render.filepath=f"{out}/{tag}_{vname}{suffix}.png"; bpy.ops.render.render(write_still=True)
    deps=bpy.context.evaluated_depsgraph_get(); P={}
    for n,p in pts.items():
        u,v,dpt=world_to_camera_view(sc,cam,p)
        d=(p-cam.location); dist=d.length
        hit,loc_,nrm,idx,ob,mx=sc.ray_cast(deps,cam.location if False else p-(cam.matrix_world.to_quaternion()@mathutils.Vector((0,0,-1)))*29.0+0*p, (cam.matrix_world.to_quaternion()@mathutils.Vector((0,0,-1))).normalized(), distance=60)
        start=p-(cam.matrix_world.to_quaternion()@mathutils.Vector((0,0,-1)))*29.0
        occ = hit and (loc_-start).length < 29.0-0.08
        P[n]=[round(u*760,1), round((1-v)*900,1), bool(occ), [round(x,3) for x in p]]
    res["views"][vname+suffix]=P
for vn in views: render(vn)
if tag=="L1":
    wings(True); bpy.context.view_layer.update()
    pts.update({n:W(n) for n in names})
    render("front","_open"); render("side","_open")
json.dump(res, open(f"{out}/{tag}_pts.json","w"), indent=0)
print("DONE", tag, len(pts))
