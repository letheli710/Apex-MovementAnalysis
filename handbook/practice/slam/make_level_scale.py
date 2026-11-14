# hb-slam: slam_harness/output.tsv -> LEVEL-SCALE.tsv (level-scale.tsv schema) and the table body of LEVEL-SCALE.md.
# py -3 -I make_level_scale.py   (from this folder)
import csv, io, os
here = os.path.dirname(os.path.abspath(__file__))
U2M, H = 0.0254, 72.0
rows = list(csv.DictReader(io.open(os.path.join(here, 'slam_harness', 'output.tsv'), encoding='utf-8'), delimiter='\t'))

QUANT = [  # column, name, dimension
    ('land_vz_u_s', '落地前竖直速度（向下）', 'Speed'),
    ('land_vh_after_u_s', '冲出去的速度（落地后水平）', 'Speed'),
    ('slide_time_s', '滑多久（落地到滑铲结束）', 'Time'),
    ('slide_dist_u', '滑多远（落地到滑铲结束）', 'Length'),
    ('fall_time_s', '下落用时（起砸 / 离开台边到落地）', 'Time'),
    ('total_dist_u', '总距离（起砸到滑铲结束，水平）', 'Length'),
]

def cols(v, dim):
    if v in ('—', ''):
        return '—', '—', '—'
    x = float(v)
    if dim == 'Time':
        return f'{x:.3f} s', '—', '—'
    if dim == 'Speed':
        return f'{x:.1f} u/s', f'{x * U2M:.3f} m/s', f'{x / H:.3f} H/s'
    return f'{x:.1f} u', f'{x * U2M:.3f} m', f'{x / H:.3f} H'

tsv = ['id\t项\t条件\t量纲\t[u]\t[m]\t身高比例\t怎么算的\t开关\t备注']
md = ['| id | 项 | 条件 | [u] | [m] | 身高比例 | 开关 | 备注 |', '|---|---|---|---|---|---|---|---|']
for r in rows:
    for col, name, dim in QUANT:
        u, m, h = cols(r[col], dim)
        slam = r['slam']
        note = r['note'] or ''
        if col == 'land_vh_after_u_s' and slam == 'yes' and r['land_vh_before_u_s'] not in ('—', ''):
            note = (note + f' 转换前 {float(r["land_vh_before_u_s"]):.1f} u/s').strip()
        rid = r['id'] + '.' + {'land_vz_u_s': 'vz', 'land_vh_after_u_s': 'vh', 'slide_time_s': 'slideT', 'slide_dist_u': 'slideD', 'fall_time_s': 'fallT', 'total_dist_u': 'total'}[col]
        cond = r['case'] + f'；起砸 / 离台时离地 {r["height_u"]} u，水平 {r["start_vh_u_s"]} u/s'
        how = 'Unity 模拟：handbook/practice/slam/slam_harness/Program.cs（游戏身体 Reference / Wraith S21，120 Hz，[u]）'
        tsv.append('\t'.join([rid, name, cond, dim, u, m, h, how, slam, note]))
        md.append(f'| {rid} | {name} | {cond} | {u} | {m} | {h} | {slam} | {note} |')
io.open(os.path.join(here, 'LEVEL-SCALE.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tsv) + '\n')
io.open(os.path.join(here, 'level-scale-rows.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
print(len(tsv) - 1, 'rows')
