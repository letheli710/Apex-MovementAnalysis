#!/usr/bin/env python3
"""手册总表的校验脚本（hb-tables，2026-11-14）。

为什么要有它：手册里的数同时写 [u]（R5 原值、Unity 现在的值）和 [m]（换算出来的）。以后 Unity 改了参数、改了量纲标记、
或者有人在表里手改了一个数，[u] 和 [m] 就会串。这个脚本把表和 Unity 的单位导出逐行对一遍，对不上就报错（退出码 1）。

查什么（params.tsv，每一行）：
  1. "参数名(Unity 导出)" 在导出里存在（没有 = Unity 改名或删了这个参数）。
  2. 量纲、单位[u] 和导出一样（不一样 = 有人改了量纲标记，[m] 列会算错）。
  3. "Unity 现在的值 [u]" 等于导出的 value_u；"回放电机 [u]" 等于导出的 preset.R5Reference 同名参数。
  4. 导出自己：value_m = value_u × 0.0254^k（k = 量纲里长度的次方：长度、速度、加速度 1，长度平方 2，1/长度 −1……）。
  5. "[m]" = "R5 原值 [u]" × 0.0254^k；"身高比例" = R5 原值 ÷ 72^k（H = 72 u）；不换算的量（k = 0）这两列必须是"—"。
  6. "和 R5 一致吗"和两个数对得上：相等写"一致"，不等写"不一致"或"近似…"。
level-scale.tsv：[m] = [u] × 0.0254^k、身高比例 = [u] ÷ 72^k。
camera-events.tsv：[m] 列里每个"X u = Y m"（u/s、u/s² 同理）都要 Y = X × 0.0254。

怎么跑（在研究仓库根目录或任何地方）：
    py -3 handbook/tables/check_params.py                     # 用 tables/unity-export/units-params.tsv
    py -3 handbook/tables/check_params.py --export <新导出的 units-params.tsv>

怎么重新导出 Unity 的参数（HSD-Unity，需要 units/switch 分支的代码，PR #88 合并后任何 checkout 都行；当前单位模式不影响结果）：
    "C:\\Program Files\\Unity\\Hub\\Editor\\6000.6.5f1\\Editor\\Unity.exe" -batchmode -quit -projectPath <HSD-Unity 工作树> ^
        -executeMethod HSD.Game.Editor.UnitsExport.Run -out <目录> -logFile <目录>\\export.log
  输出 <目录>/units-params.tsv、units-registry.tsv。先用 --export 跑这个脚本；报错的行逐条看：
  是 Unity 有意改了（改 params.tsv 的"Unity 现在的值"和"和 R5 一致吗"，差别列写 D-xx），还是串了（修 Unity 的标记或代码）。
  全部通过以后，把新导出复制进 tables/unity-export/ 覆盖旧的，再提交。
  注意：Unity 批处理会占用工程；不要按进程名杀 Unity（别的会话可能也在用），用 -quit 让它自己退出。
"""
import argparse, csv, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
K = 0.0254
H = 72.0
POW = {'Length': 1, 'Velocity': 1, 'Acceleration': 1, 'Jerk': 1, 'LengthSq': 2, 'VelocitySq': 2,
       'InvLength': -1, 'InvVelocity': -1, 'InvVelocitySq': -2}
HUNIT = {1: None, 2: None, -1: None}
HLABEL = {'Length': 'H', 'Velocity': 'H/s', 'Acceleration': 'H/s²', 'Jerk': 'H/s³', 'InvLength': '1/H', 'InvVelocity': 's/H'}
DASH = {'—', '-', ''}

errors = []
def err(table, rid, msg): errors.append(f"{table} {rid}: {msg}")

def num(s):
    s = (s or '').strip()
    try: return float(s)
    except ValueError: return None

def close(a, b, rel):
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-12)

def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))

def check_params(export_rows):
    path = os.path.join(HERE, 'params.tsv')
    rows = read_tsv(path)
    need = ['R5 原值 [u]', '[m]', '身高比例', 'TF2 值 [u]', 'Unity 现在的值 [u]', '回放电机 [u]']
    for c in need:
        if c not in rows[0]: err('params', 'header', f'缺列 "{c}"（列名必须带 [u] / [m] 标记）')
    n_exp = 0
    for r in rows:
        rid, p = r['id'], r['参数名(Unity 导出)']
        dim = r['量纲']; k = POW.get(dim, 0)
        in_export = not p.startswith('（')
        u_val = num(r['Unity 现在的值 [u]'])
        if in_export:
            n_exp += 1
            e = export_rows.get(p)
            if e is None:
                err('params', rid, f'"{p}" 在 Unity 导出里没有（改名或删了？）'); continue
            if e['dim'] != dim: err('params', rid, f'量纲：表 {dim}，导出 {e["dim"]}（量纲标记改了，[m] 列要重算）')
            if e['unit_u'] != r['单位[u]']: err('params', rid, f'单位：表 {r["单位[u]"]}，导出 {e["unit_u"]}')
            ev = num(e['value_u'])
            if r['Unity 现在的值 [u]'] != e['value_u'] and not (ev is not None and u_val is not None and close(ev, u_val, 1e-12)):
                err('params', rid, f'Unity 值变了：表 {r["Unity 现在的值 [u]"]}，导出 {e["value_u"]}')
            em = num(e['value_m'])
            if ev is not None and em is not None and math.isfinite(ev) and not close(em, ev * K ** k, 1e-9):
                err('params', rid, f'导出自己的 [m] 不等于 [u] × 0.0254^{k}：{e["value_u"]} → {e["value_m"]}')
            if p.startswith('preset.Reference.motor.'):
                rp = export_rows.get('preset.R5Reference.' + p[len('preset.Reference.motor.'):])
                if rp is not None and r['回放电机 [u]'] != rp['value_u']:
                    err('params', rid, f'回放电机值：表 {r["回放电机 [u]"]}，导出 {rp["value_u"]}')
        r5 = num(r['R5 原值 [u]'])
        if r5 is not None:
            if k == 0:
                if r['[m]'] not in DASH: err('params', rid, f'不换算的量（{dim}），[m] 应为"—"，现在是 {r["[m]"]}')
                if r['身高比例'] not in DASH: err('params', rid, f'不换算的量，身高比例应为"—"')
            else:
                m = num(r['[m]'])
                if m is None or not close(m, r5 * K ** k, 5e-4):
                    err('params', rid, f'[m] = {r["[m]"]}，应为 {r5} × 0.0254^{k} = {r5 * K ** k:.6g}（[u] 和 [m] 串了？）')
                hr = r['身高比例'].split(' ')
                if dim in HLABEL:
                    if len(hr) != 2 or num(hr[0]) is None or not close(num(hr[0]), r5 / H ** k, 5e-4) or hr[1] != HLABEL[dim]:
                        err('params', rid, f'身高比例 "{r["身高比例"]}"，应为 {r5 / H ** k:.4g} {HLABEL[dim]}')
            v = r['和 R5 一致吗']
            if u_val is not None and in_export:
                same = close(u_val, r5, 1e-9) or u_val == r5
                if same and v != '一致': err('params', rid, f'两个数相等，"和 R5 一致吗"却写 "{v}"')
                if not same and not (v == '不一致' or v.startswith('近似')): err('params', rid, f'R5 {r5} ≠ Unity {u_val}，"和 R5 一致吗"却写 "{v}"')
        elif r['[m]'] not in DASH:
            err('params', rid, 'R5 原值不是数，[m] 应为"—"')
    return len(rows), n_exp

def check_level():
    path = os.path.join(HERE, 'level-scale.tsv')
    if not os.path.exists(path): return 0
    rows = read_tsv(path)
    for r in rows:
        rid = r['id']; dim = r['量纲']; k = POW.get(dim, 0)
        u = num(r['[u]'])
        if u is None: continue
        if k == 0:
            if r['[m]'] not in DASH: err('level', rid, f'不换算的量（{dim}），[m] 应为"—"')
            continue
        m = num(r['[m]'])
        if m is None or not close(m, u * K ** k, 5e-4): err('level', rid, f'[m] = {r["[m]"]}，应为 {u * K ** k:.6g}')
        hr = r['身高比例'].split(' ')
        if dim in HLABEL and (len(hr) != 2 or num(hr[0]) is None or not close(num(hr[0]), u / H ** k, 5e-4) or hr[1] != HLABEL[dim]):
            err('level', rid, f'身高比例 "{r["身高比例"]}"，应为 {u / H ** k:.4g} {HLABEL[dim]}')
    return len(rows)

PAIR = re.compile(r'([−-]?\d+(?:\.\d+)?)\s*(u/s²|u/s|u)\s*=\s*([−-]?\d+(?:\.\d+)?)\s*(m/s²|m/s|m)(?![a-zA-Z])')
UM = {'u': 'm', 'u/s': 'm/s', 'u/s²': 'm/s²'}
def check_camera():
    path = os.path.join(HERE, 'camera-events.tsv')
    if not os.path.exists(path): return 0, 0
    rows = read_tsv(path)
    n = 0
    for r in rows:
        for mt in PAIR.finditer(r.get('[m]') or ''):
            n += 1
            u = float(mt.group(1).replace('−', '-')); m = float(mt.group(3).replace('−', '-'))
            if UM[mt.group(2)] != mt.group(4): err('camera', r.get('id', '?'), f'单位对不上：{mt.group(0)}')
            elif not close(m, u * K, 5e-3) and not (u == 0 and m == 0): err('camera', r.get('id', '?'), f'"{mt.group(0)}"，应为 {u * K:.4g} {mt.group(4)}')
    return len(rows), n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--export', default=os.path.join(HERE, 'unity-export', 'units-params.tsv'))
    a = ap.parse_args()
    export_rows = {r['param']: r for r in read_tsv(a.export)}
    n, ne = check_params(export_rows)
    nl = check_level()
    nc, ncm = check_camera()
    print(f'params.tsv {n} 行（{ne} 行对 Unity 导出）；level-scale.tsv {nl} 行；camera-events.tsv {nc} 行（{ncm} 处 "u = m" 查了）；导出 {len(export_rows)} 个参数')
    if errors:
        for e in errors: print('错误 ' + e)
        print(f'不通过：{len(errors)} 处')
        return 1
    print('通过：表里的 Unity 值、量纲、[m] 列和身高比例都和导出一致')
    return 0

if __name__ == '__main__':
    sys.exit(main())
