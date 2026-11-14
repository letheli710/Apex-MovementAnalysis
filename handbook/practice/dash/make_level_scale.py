# hb-slam (practice A2): dash_harness/output.tsv -> LEVEL-SCALE.tsv (level-scale.tsv columns) and the table rows pasted into LEVEL-SCALE.md.
# py -3 -I make_level_scale.py   (from this folder)
import csv, io, os
here = os.path.dirname(os.path.abspath(__file__))
U2M, H = 0.0254, 72.0
rows = list(csv.DictReader(io.open(os.path.join(here, 'dash_harness', 'output.tsv'), encoding='utf-8'), delimiter='\t'))
def cols(v, dim):
    if v in ('—', ''): return '—', '—', '—'
    x = float(v)
    if dim == 'Time': return f'{x:.3f} s', '—', '—'
    if dim == 'Speed': return f'{x:.1f} u/s', f'{x*U2M:.3f} m/s', f'{x/H:.3f} H/s'
    return f'{x:.1f} u', f'{x*U2M:.3f} m', f'{x/H:.3f} H'
tsv = ['id\t项\t条件\t量纲\t[u]\t[m]\t身高比例\t怎么算的\tR5 对照\t备注']
md = ['| id | 项 | 条件 | [u] | [m] | 身高比例 | 备注 |', '|---|---|---|---|---|---|---|']
how = 'Unity 模拟：handbook/practice/dash/dash_harness/Program.cs（游戏身体 Reference / Wraith S21，冲刺设计值，120 Hz，[u]）'
for r in rows:
    u, m, h = cols(r['[u]'], r['量纲'])
    tsv.append('\t'.join([r['id'], r['项'], r['条件'], r['量纲'], u, m, h, how, 'R5 没有冲刺', r['备注']]))
    md.append(f"| {r['id']} | {r['项']} | {r['条件']} | {u} | {m} | {h} | {r['备注']} |")
io.open(os.path.join(here, 'LEVEL-SCALE.tsv'), 'w', encoding='utf-8', newline='\n').write('\n'.join(tsv) + '\n')
io.open(os.path.join(here, 'level-scale-rows.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(md) + '\n')
print(len(tsv) - 1, 'rows')
