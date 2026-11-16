"""hb-judge: score the rebuild (hb-rebuild) against the answer key.

    py -3 compare.py                               # build CSVs from git: origin/handbook/rebuild-build:handbook/rebuild-test/build/out/<id>.csv
    py -3 compare.py --build-dir <dir>             # or from a local folder of <id>.csv
    py -3 compare.py --ref <branch>                # another branch / commit for the git read
    options: --answers <dir> (default ./answers), --md <file> (default ./compare_result.md), --no-fetch

Pass lines (lead, 2026-11-14):
  speed_h, vel_z: |Δ| <= 0.5 u/s on every common tick;  position (x and z; landing problems z only): |Δ| <= 0.5 u;
  events (slide_start / slide_end / jump / land): the same tick = 过, ±1 tick = 基本过 (the speed / position checks then skip the
  ticks between the two event ticks and the tick after), worse = 不过;
  landing problems (L*): camera punch peak |Δ| <= 0.05°, peak tick ±1, the tick it is back within 0.05° for good ±2.
Informational, not scored: state column, eye height, row count, the slide-problem camera column.
Standard library only. Columns: tick,t_s,pos_x_u,pos_z_u,speed_h_u_s,vel_z_u_s,state,events,cam_pitch_punch_deg,eye_height_u
"""
import argparse
import csv
import io
import os
import subprocess
import sys

IDS = ['S1', 'S2', 'S3', 'S4', 'S5', 'L1_50', 'L1_100', 'L1_200', 'L1_400', 'L2']
EVENTS = ['slide_start', 'slide_end', 'jump', 'land']
TOL_V, TOL_P, TOL_CAM, TOL_CAM_BACK = 0.5, 0.5, 0.05, 0.05


def parse(text):
    rows = {}
    for r in csv.DictReader(io.StringIO(text.lstrip('﻿'))):
        r = {k.strip(): (v or '').strip() for k, v in r.items() if k is not None}
        try:
            rows[int(float(r['tick']))] = r
        except (KeyError, ValueError):
            continue
    return rows


def num(r, key):
    try:
        return float(r.get(key, ''))
    except ValueError:
        return None


def events(rows):
    out = {e: [] for e in EVENTS}
    for k in sorted(rows):
        for e in rows[k].get('events', '').replace(',', ';').split(';'):
            e = e.strip()
            if e in out:
                out[e].append(k)
    return out


def cam_metrics(rows, after):
    """Peak |punch| at or after tick `after` (the landing), its tick, and the first tick after which |punch| stays <= 0.05°."""
    ks = [k for k in sorted(rows) if k >= after and num(rows[k], 'cam_pitch_punch_deg') is not None]
    if not ks:
        return None
    vals = [(k, num(rows[k], 'cam_pitch_punch_deg')) for k in ks]
    pk, pv = max(vals, key=lambda kv: abs(kv[1]))
    back = None
    for k, v in vals:
        if k <= pk:
            continue
        if abs(v) <= TOL_CAM_BACK:
            if back is None:
                back = k
        else:
            back = None
    return dict(peak=pv, peak_tick=pk, back_tick=back)


def score(pid, ans, bld):
    res = dict(id=pid, notes=[], verdict='过')
    if bld is None:
        res.update(verdict='没交', notes=['没有这一题的文件'])
        return res
    landing = pid.startswith('L')
    common = sorted(set(ans) & set(bld))
    res['rows'] = (len(ans), len(bld), len(common))
    if len(ans) != len(bld):
        res['notes'].append(f'行数不同：答案 {len(ans)}，重建 {len(bld)}（只比共同的 {len(common)} 条）')
    # events
    ea, eb = events(ans), events(bld)
    skip = set()
    ev_rows = []
    worst = 0
    for e in EVENTS:
        a, b = ea[e], eb[e]
        if not a and not b:
            continue
        line = f'{e}: 答案 {a} / 重建 {b}'
        if len(a) != len(b):
            worst = max(worst, 99)
            line += '（次数不同）'
        else:
            for ta, tb in zip(a, b):
                d = abs(ta - tb)
                worst = max(worst, d)
                if d == 1:
                    skip.update(range(min(ta, tb), max(ta, tb) + 2))
        ev_rows.append(line)
    res['events'] = ev_rows
    if worst > 1:
        res['verdict'] = '不过'
        res['notes'].append('事件差 > 1 条命令或次数不同')
    elif worst == 1:
        res['verdict'] = '基本过'
    # kinematics
    cols = [('pos_z_u', TOL_P)] if landing else [('pos_x_u', TOL_P), ('pos_z_u', TOL_P), ('speed_h_u_s', TOL_V)]
    cols.append(('vel_z_u_s', TOL_V))
    kin = []
    for col, tol in cols:
        md, mk, first_bad = 0.0, None, None
        for k in common:
            if k in skip:
                continue
            a, b = num(ans[k], col), num(bld[k], col)
            if a is None:
                continue
            if b is None:
                first_bad = first_bad if first_bad is not None else k
                md, mk = float('inf'), k
                continue
            d = abs(a - b)
            if d > md:
                md, mk = d, k
            if d > tol + 1e-9 and first_bad is None:
                first_bad = k
        kin.append(f'{col}: 最大差 {md:.4f}（tick {mk}）' + (f'，第一次超线 tick {first_bad}' if first_bad is not None else ''))
        if first_bad is not None:
            res['verdict'] = '不过'
            res['notes'].append(f'{col} 超过 {tol}：第一次在 tick {first_bad}（答案 {ans[first_bad].get(col)}，重建 {bld.get(first_bad, {}).get(col)}）')
    res['kin'] = kin
    # camera (landing problems)
    if landing:
        land_a = ea['land'][0] if ea['land'] else min(ans)
        land_b = eb['land'][0] if eb['land'] else land_a
        ca, cb = cam_metrics(ans, land_a), cam_metrics(bld, land_b)
        if cb is None:
            res['verdict'] = '不过'
            res['notes'].append('镜头列是空的')
        else:
            dp = abs(ca['peak'] - cb['peak'])
            dt_peak = cb['peak_tick'] - ca['peak_tick']
            dt_back = None if ca['back_tick'] is None or cb['back_tick'] is None else cb['back_tick'] - ca['back_tick']
            res['cam'] = (f"峰值 答案 {ca['peak']:.4f}° @ {ca['peak_tick']} / 重建 {cb['peak']:.4f}° @ {cb['peak_tick']}（差 {dp:.4f}°，{dt_peak:+d} 帧）；"
                          f"回到 0.05° 以内 答案 {ca['back_tick']} / 重建 {cb['back_tick']}" + (f'（{dt_back:+d} 帧）' if dt_back is not None else ''))
            bad = []
            if dp > TOL_CAM + 1e-9:
                bad.append(f'峰值差 {dp:.4f}° > 0.05°')
            if abs(dt_peak) > 1:
                bad.append(f'峰值时刻差 {dt_peak:+d} 帧')
            if dt_back is None and (ca['back_tick'] is None) != (cb['back_tick'] is None):
                bad.append('回到 0.05° 以内的时刻一边没有')
            elif dt_back is not None and abs(dt_back) > 2:
                bad.append(f'回到 0.05° 的时刻差 {dt_back:+d} 帧')
            if bad:
                res['verdict'] = '不过'
                res['notes'] += bad
    # informational
    st = sum(1 for k in common if ans[k].get('state') != bld[k].get('state'))
    eye = [abs(num(ans[k], 'eye_height_u') - num(bld[k], 'eye_height_u')) for k in common
           if num(ans[k], 'eye_height_u') is not None and num(bld[k], 'eye_height_u') is not None]
    res['info'] = f'state 不同 {st} 条；眼高最大差 ' + (f'{max(eye):.3f} u' if eye else '（重建没写）')
    return res


def load_build(args, pid):
    if args.build_dir:
        p = os.path.join(args.build_dir, pid + '.csv')
        return parse(open(p, encoding='utf-8').read()) if os.path.exists(p) else None
    spec = f'{args.ref}:handbook/rebuild-test/build/out/{pid}.csv'
    r = subprocess.run(['git', 'show', spec], capture_output=True, cwd=os.path.dirname(os.path.abspath(__file__)))
    return parse(r.stdout.decode('utf-8', 'replace')) if r.returncode == 0 else None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('--answers', default=os.path.join(here, 'answers'))
    ap.add_argument('--build-dir')
    ap.add_argument('--ref', default='origin/handbook/rebuild-build')
    ap.add_argument('--md', default=os.path.join(here, 'compare_result.md'))
    ap.add_argument('--no-fetch', action='store_true')
    args = ap.parse_args()
    if not args.build_dir and not args.no_fetch:
        subprocess.run(['git', 'fetch', '-q', 'origin'], cwd=here)
    out = ['# 重建检验评分（compare.py 输出）', '', f"重建来源：{args.build_dir or args.ref}", '',
           '| 题 | 结果 | 说明 |', '|---|---|---|']
    detail = []
    for pid in IDS:
        ans = parse(open(os.path.join(args.answers, pid + '.csv'), encoding='utf-8').read())
        r = score(pid, ans, load_build(args, pid))
        out.append(f"| {pid} | {r['verdict']} | {'；'.join(r['notes']) or '—'} |")
        detail += [f'## {pid}：{r["verdict"]}', '']
        for key in ('events', 'kin'):
            detail += [f'- {x}' for x in r.get(key, [])]
        if 'cam' in r:
            detail.append(f"- 镜头：{r['cam']}")
        if 'info' in r:
            detail.append(f"- 参考（不计分）：{r['info']}")
        detail.append('')
        print(f"{pid}: {r['verdict']}  {'; '.join(r['notes'])}")
    with open(args.md, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out + [''] + detail) + '\n')
    print('->', args.md)


if __name__ == '__main__':
    sys.exit(main())
