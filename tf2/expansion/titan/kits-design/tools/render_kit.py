# Blockout renders of M-1 with kit modules (concept only; the model file is NOT saved).
# blender -b Titan_M1.blend -P render_kit.py -- <kit> <outdir>
import bpy, sys, math, json, os
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index('--') + 1:]
KIT, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)

COL = {
    'base':    (0.62, 0.63, 0.65, 1),
    'mount':   (0.30, 0.32, 0.36, 1),   # shared hardpoint seats
    'energy':  (0.69, 0.30, 1.00, 1),   # 能量
    'kinetic': (0.85, 0.64, 0.25, 1),   # 实弹
    'arc':     (0.31, 0.89, 1.00, 1),   # 电
    'barrier': (0.86, 0.92, 1.00, 1),   # 屏障
    'restore': (0.36, 1.00, 0.62, 1),   # 回补
    'mark':    (1.00, 0.82, 0.25, 1),   # 标记 / 锁定
    'body':    (1.00, 0.35, 0.12, 1),   # 机体发光色（升级刻度）
    'dark':    (0.10, 0.10, 0.11, 1),
}

new_objs = []

def _finish(o, col):
    o.color = COL[col]
    new_objs.append(o)
    return o

def box(name, mn, mx, col):
    c = [(a + b) / 2 for a, b in zip(mn, mx)]
    s = [(b - a) for a, b in zip(mn, mx)]
    bpy.ops.mesh.primitive_cube_add(size=1, location=c)
    o = bpy.context.active_object; o.name = name; o.scale = s
    return _finish(o, col)

def cyl(name, c, r, depth, axis, col, verts=24, rot_extra=0.0):
    rot = {'X': (0, math.pi / 2, 0), 'Y': (math.pi / 2, 0, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=c, rotation=rot)
    o = bpy.context.active_object; o.name = name
    if rot_extra:
        o.rotation_euler.rotate_axis(axis, rot_extra) if False else None
    return _finish(o, col)

def cone(name, c, r1, r2, depth, axis, col):
    rot = {'X': (0, math.pi / 2, 0), 'Y': (-math.pi / 2, 0, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=r1, radius2=r2, depth=depth, location=c, rotation=rot)
    o = bpy.context.active_object; o.name = name
    return _finish(o, col)

def torus(name, c, R, r, axis, col):
    rot = {'X': (0, math.pi / 2, 0), 'Y': (math.pi / 2, 0, 0), 'Z': (0, 0, 0)}[axis]
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=c, rotation=rot,
                                     major_segments=32, minor_segments=8)
    o = bpy.context.active_object; o.name = name
    return _finish(o, col)

def hide(name):
    o = bpy.data.objects.get(name)
    if o: o.hide_render = True

def chest_y(z):  # surface of hatch slope near the chest launcher (35 deg back-tilt)
    return -1.084 + (z - 4.78) * 0.70 - 0.04

# ---------- shared seats (every kit) ----------
def shared_seats():
    hide('M1_Cannon'); hide('M1_Pod_L')
    box('HP1_seat', (-1.60, -0.30, 3.00), (-1.00, 0.30, 3.87), 'mount')     # 右前臂炮座
    box('HP2_seat', (0.25, 0.25, 5.52), (0.98, 0.85, 5.70), 'mount')        # 左肩舱座
    box('HP3_rail', (1.62, -0.20, 2.98), (1.66, 0.20, 3.80), 'mount')       # 左前臂外侧导轨

# ---------- modules ----------
def spectra():
    shared_seats()
    cyl('SPC_P1_barrel', (-1.30, 0, 2.35), 0.31, 1.30, 'Z', 'energy', verts=3)
    for s in (-1, 1):
        box(f'SPC_P1_vane{s}', (-1.30 + s * 0.30 - 0.03, -0.05, 1.72), (-1.30 + s * 0.30 + 0.03, 0.05, 2.12), 'energy')
    for i, z in enumerate((2.30, 2.55, 2.80)):
        box(f'SPC_P1_slot{i}', (-1.40, -0.20, z), (-1.20, -0.16, z + 0.16), 'body')
    box('SPC_O1_needle', (0.48, -0.42, 5.70), (0.74, 0.55, 5.90), 'energy')
    for i, y in enumerate((0.38, 0.46)):
        box(f'SPC_O1_fin{i}', (0.42, y, 5.90), (0.80, y + 0.04, 5.96), 'mount')
    for i, x in enumerate((0.34, 0.61, 0.88)):
        cyl(f'SPC_T1_stake{i}', (x, 0.72, 5.80), 0.08, 0.22, 'Y', 'energy', verts=3)
    for i, (dy, dz) in enumerate(((-0.25, 0.0), (0.0, 0.0), (0.25, 0.0))):
        box(f'SPC_D1_petal{i}', (1.64, dy - 0.11, 2.95), (1.74, dy + 0.11, 3.78), 'barrier')
    for i, (dx, dz) in enumerate(((0, 0.40), (0.35, -0.22), (-0.35, -0.22))):
        z = 4.78 + dz
        cyl(f'SPC_C1_leaf{i}', (dx, chest_y(z), z), 0.10, 0.06, 'Y', 'energy', verts=3)

def tally():
    shared_seats()
    cyl('TLY_P1_barrel', (-1.30, 0, 2.55), 0.29, 0.90, 'Z', 'kinetic')
    cyl('TLY_P1_brake', (-1.30, 0, 2.10), 0.34, 0.18, 'Z', 'kinetic', verts=6)
    cyl('TLY_P1_drum', (-1.72, 0, 2.75), 0.20, 0.42, 'Z', 'kinetic', verts=6)
    for i in range(3):
        box(f'TLY_P1_pip{i}', (-1.95, -0.10 + i * 0.07, 2.88), (-1.91, -0.06 + i * 0.07, 2.94), 'mark')
    box('TLY_O1_pod', (0.27, -0.10, 5.55), (0.96, 0.80, 5.94), 'kinetic')
    for i in range(1, 7):
        o = bpy.data.objects['S_Rocket_%d' % i].matrix_world.translation
        box(f'TLY_O1_tube{i}', (o.x - 0.06, -0.13, o.z - 0.06), (o.x + 0.06, -0.09, o.z + 0.06), 'dark')
    cyl('TLY_O1_seeker', (1.00, 0.10, 5.75), 0.07, 0.08, 'X', 'mark')
    cone('TLY_T1_bell', (0.62, 0.95, 5.75), 0.14, 0.05, 0.30, 'Y', 'mark')
    box('TLY_D1_proj', (1.64, -0.16, 2.90), (1.76, 0.16, 3.85), 'barrier')
    for i in range(4):
        box(f'TLY_D1_slat{i}', (1.76, -0.14, 2.98 + i * 0.22), (1.79, 0.14, 3.12 + i * 0.22), 'mount')
    for i, x in enumerate((-0.18, 0.0, 0.18)):
        cyl(f'TLY_C1_cell{i}', (x, chest_y(4.47) - 0.02, 4.47), 0.06, 0.06, 'Y', 'dark')

def _stepgun(coils):
    for s in (-1, 1):
        cyl(f'P1_barrel{s}', (-1.30 + s * 0.13, 0, 2.38), 0.10, 1.25, 'Z', 'kinetic')
    box('P1_shroud', (-1.50, -0.16, 2.85), (-1.10, 0.16, 3.00), 'kinetic')
    box('P1_feed', (-1.62, -0.18, 2.60), (-1.50, 0.18, 3.00), 'kinetic')
    if coils:
        for i, z in enumerate((2.00, 2.25, 2.50)):
            torus(f'ASC_up1_coil{i}', (-1.30, 0, z), 0.27, 0.035, 'Z', 'arc')

def _smoke_racks(rods):
    for s, (x0, x1) in enumerate(((0.38, 0.74), (-0.62, -0.26))):
        box(f'SMK_rack{s}', (x0, 1.08, 5.57), (x1, 1.40, 5.66), 'mount')
        for j in range(2):
            cx = x0 + 0.09 + j * 0.18
            cyl(f'SMK_can{s}{j}', (cx, 1.24, 5.76), 0.075, 0.20, 'Z', 'arc' if rods else 'mount')
        if rods:
            cyl(f'ASC_up2_rod{s}', ((x0 + x1) / 2, 1.38, 5.80), 0.02, 0.34, 'Z', 'arc')

def ascent():
    shared_seats()
    _stepgun(coils=True)
    cyl('ASC_O1_rosette', (0.62, 0.30, 5.66), 0.30, 0.90, 'Y', 'kinetic', verts=6)
    for k in range(6):
        a = math.radians(60 * k)
        cyl(f'ASC_O1_tube{k}', (0.62 + 0.18 * math.cos(a), -0.16, 5.66 + 0.18 * math.sin(a)), 0.055, 0.04, 'Y', 'dark')
    for s, (x0, x1) in enumerate(((0.18, 0.28), (0.96, 1.06))):
        box(f'ASC_up3_cheek{s}', (x0, -0.05, 5.52), (x1, 0.60, 5.84), 'mark')
    cyl('ASC_D1_lens', (1.72, -0.15, 3.35), 0.11, 0.22, 'Y', 'restore')
    torus('ASC_up2_dish', (1.72, -0.27, 3.35), 0.20, 0.03, 'Y', 'restore')
    torus('ASC_up1_band', (1.30, 0, 3.62), 0.34, 0.03, 'Z', 'restore')
    _smoke_racks(rods=True)
    for i, z in enumerate((5.00, 5.13, 5.26)):
        box(f'ASC_C1_chev{i}', (-1.97, -0.28, z), (-1.93, 0.28, z + 0.07), 'body')

def wayfarer():
    shared_seats()
    _stepgun(coils=False)
    for i in range(3):
        a = math.radians(120 * i)
        box(f'WAY_C1_fin{i}', (-1.30 + 0.20 * math.cos(a) - 0.02, 0.20 * math.sin(a) - 0.02, 1.80),
            (-1.30 + 0.20 * math.cos(a) + 0.02, 0.20 * math.sin(a) + 0.02, 2.30), 'kinetic')
    box('WAY_O1_pod', (0.27, -0.10, 5.55), (0.96, 0.80, 5.90), 'kinetic')
    for i in range(1, 7):
        o = bpy.data.objects['S_Rocket_%d' % i].matrix_world.translation
        box(f'WAY_O1_tube{i}', (o.x - 0.06, -0.13, o.z - 0.06), (o.x + 0.06, -0.09, o.z + 0.06), 'dark')
        box(f'WAY_O1_lamp{i}', (o.x - 0.04, -0.06, 5.90), (o.x + 0.04, 0.02, 5.95), 'mark')
    box('TLY_D1_proj', (1.64, -0.16, 2.90), (1.76, 0.16, 3.85), 'barrier')
    for i in range(4):
        box(f'TLY_D1_slat{i}', (1.76, -0.14, 2.98 + i * 0.22), (1.79, 0.14, 3.12 + i * 0.22), 'mount')
    _smoke_racks(rods=False)

def base():
    pass

{'base': base, 'spectra': spectra, 'tally': tally, 'ascent': ascent, 'wayfarer': wayfarer}[KIT]()

# ---------- base colours ----------
for o in bpy.data.objects:
    if o.type == 'MESH' and o not in new_objs:
        o.color = COL['base']

# ---------- render setup ----------
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'; sh.color_type = 'OBJECT'
sh.show_object_outline = True; sh.object_outline_color = (0.05, 0.05, 0.05)
sh.show_cavity = True; sh.cavity_type = 'WORLD'
sc.render.resolution_x = 700; sc.render.resolution_y = 900
sc.render.film_transparent = False
sc.world.color = (1, 1, 1) if sc.world else None
sh.background_type = 'VIEWPORT'; sh.background_color = (1, 1, 1)

ORTHO = 7.0  # height 7.0 m fits 0..6.5 ; width 7*700/900
CZ = 3.05
cam_data = bpy.data.cameras.new('kitcam'); cam_data.type = 'ORTHO'; cam_data.ortho_scale = ORTHO
cam = bpy.data.objects.new('kitcam', cam_data); sc.collection.objects.link(cam); sc.camera = cam
views = {
    'front': ((0, -30, CZ), (math.pi / 2, 0, 0)),          # looks +Y
    'side':  ((30, 0, CZ), (math.pi / 2, 0, math.pi / 2)),  # from titan's left (+X), looks -X
    'back':  ((0, 30, CZ), (math.pi / 2, 0, math.pi)),      # looks -Y
}
meta = {'ortho': ORTHO, 'cz': CZ, 'w': 700, 'h': 900, 'sockets': {}}
for v, (loc, rot) in views.items():
    cam.location = loc; cam.rotation_euler = rot
    sc.render.filepath = os.path.join(OUT, f'{KIT}_{v}.png')
    bpy.ops.render.render(write_still=True)
for o in bpy.data.objects:
    if o.type == 'EMPTY' and (o.name.startswith('S_') or o.name.startswith('J_') or o.name.startswith('W_')):
        p = o.matrix_world.translation; meta['sockets'][o.name] = [p.x, p.y, p.z]
json.dump(meta, open(os.path.join(OUT, f'{KIT}_meta.json'), 'w'), indent=1)
print('DONE', KIT)
