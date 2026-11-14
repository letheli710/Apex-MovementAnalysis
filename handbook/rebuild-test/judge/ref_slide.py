"""hb-judge: cross-check of the Unity answer key (answers/S*.csv) against the chapter-04 slide pseudocode.

The slide rules of handbook/04-slide-mantle.md §4.7 (the same rules as handbook/04-slide-mantle/slide_ref.py on branch handbook/ch04,
here with msc = 1 and a slope term) are stepped from the speed the Unity body has on the command before each slide starts, with the
scenario's crouch / jump inputs, and compared command by command with the Unity rows. Only the slide phases are modelled (sprinting
from rest and the air are chapter 03): the entry speed of every slide comes from the Unity row before it.

    py -3 ref_slide.py [answers_dir]      -> prints one line per slide phase and writes ref_slide.md next to this script
Standard library only.
"""
import csv
import math
import os
import sys

MSC = 1.0
G = 750.0
DT = 1.0 / 120
P = dict(start=200.0, boost=150.0, cap=400.0, rearm=2.0, decel=100.0, stop_decel=400.0, decay=0.7, stop=125.0, max_stop=350.0,
         refund_window=0.4, duck_transition=0.2, floor=350.0, floor_low=0.85)


def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def ev(row, name):
    return name in row['events'].split(';')


class Slide:
    """§4.1 – §4.6 for one body: the boost clock survives across slides."""

    def __init__(self):
        self.sliding = False
        self.boosted = False
        self.last_boost = 0.0
        self.boost_time = -math.inf
        self.start_time = -math.inf
        self.duck_tr = -math.inf

    def press(self, s, now):
        boost = now - self.start_time >= P['rearm'] - 1e-9
        if boost:
            peak = min(s + P['boost'] * MSC, P['cap'] * MSC)
            self.last_boost, self.boost_time, s = peak - s, now, peak
        self.sliding, self.boosted, self.start_time, self.duck_tr = True, boost, now, now + DT
        return s

    def resume(self, now):                        # §4.4 landing with crouch held: no boost, cooldown refreshed
        self.sliding, self.boosted, self.start_time = True, False, now

    def ground(self, s, duck, slope_a):
        """Returns (speed after the command, ended_this_command)."""
        releasing = not duck
        if releasing and s <= P['max_stop']:
            self.sliding = False
            return None, True                     # the command is a crouch-walk command (chapter 03), not modelled here
        s += slope_a * DT                         # §4.5, straight downhill: g·n_z·|n_h|
        D = P['stop_decel'] if releasing else P['decel']
        s = max(0.0, (s - D * DT) * P['decay'] ** DT)
        if s < P['stop']:
            self.sliding = False
            return s, True
        return s, False

    def jump(self, s, now):
        if self.boosted:
            if now - self.boost_time < P['refund_window'] and now - self.duck_tr < P['duck_transition'] - 1e-9:
                s = max(0.0, s - self.last_boost)
            if P['floor_low'] * P['floor'] < s < P['floor']:
                s = P['floor']
        self.sliding = self.boosted = False
        return s


def check(name, rows, slope_deg=0.0):
    """Walks the Unity rows; inside every slide phase steps the reference and compares the horizontal speed."""
    sl = Slide()
    slope_a = G * math.cos(math.radians(slope_deg)) * math.sin(math.radians(slope_deg))
    out = []
    s_ref = None
    seg = None
    for i, r in enumerate(rows):
        k = int(r['tick'])
        now = k * DT
        su = float(r['speed_h_u_s'])
        pre = float(rows[i - 1]['speed_h_u_s']) if i > 0 else 0.0
        if ev(r, 'slide_start') and not ev(r, 'land'):
            s_ref = sl.press(pre, now)
            seg = dict(kind='press', start=k, entry=pre, boosted=sl.boosted, peak=s_ref, maxd=0.0, n=0)
        elif ev(r, 'land') and ev(r, 'slide_start'):
            sl.resume(now)
            s_ref = su                            # the resumed slide starts from the Unity landing speed (air is chapter 03)
            seg = dict(kind='resume', start=k, entry=su, boosted=False, peak=su, maxd=0.0, n=0)
            continue
        if seg is None or not sl.sliding:
            continue
        if ev(r, 'jump'):
            exit_ref = sl.jump(s_ref, now)
            seg.update(end=k, how='jump', exit_ref=exit_ref, exit_unity=su)
            out.append(seg); seg = None
            continue
        duck = not (name == 'S2' and k >= 300)  # S2 releases crouch 0.5 s after the slide start; every other slide holds it
        s_new, ended = sl.ground(s_ref, duck, slope_a)   # the press command itself already moves as a slide (§4.1 rule 3)
        if s_new is not None:
            d = abs(s_new - su)
            seg['maxd'] = max(seg['maxd'], d); seg['n'] += 1
            s_ref = s_new
        if ended:
            seg.update(end=k, how='end', ref_end=k, unity_end=k if ev(r, 'slide_end') else None, exit_ref=s_new, exit_unity=su)
            out.append(seg); seg = None
    if seg is not None:
        seg.update(end=int(rows[-1]['tick']), how='open', exit_ref=s_ref, exit_unity=float(rows[-1]['speed_h_u_s']))
        out.append(seg)
    # Unity's own end ticks
    unity_ends = [int(r['tick']) for r in rows if ev(r, 'slide_end')]
    return out, unity_ends


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ans = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'answers')
    lines = ['# ref_slide: chapter-04 pseudocode (msc 1) against the Unity answer key', '',
             '| 题 | 段 | 开始 tick | 入口速度 | 加成 | 峰值 | 结束 tick（参考 / Unity） | 结束方式 | 出口速度 参考 / Unity | 逐命令最大速度差 |',
             '|---|---|---|---|---|---|---|---|---|---|']
    for name, slope in (('S1', 0), ('S2', 0), ('S3', 0), ('S4', 20), ('S5', 0)):
        rows = read(os.path.join(ans, name + '.csv'))
        segs, uends = check(name, rows, slope)
        for j, sg in enumerate(segs):
            ue = [e for e in uends if e >= sg['start']]
            uend = ue[0] if ue else '—'
            ex_u = sg.get('exit_unity'); ex_r = sg.get('exit_ref')
            line = '| %s | %d %s | %d | %.3f | %s | %.3f | %s / %s | %s | %s / %.3f | %.4f (%d 条) |' % (
                name, j + 1, sg['kind'], sg['start'], sg['entry'], '有' if sg['boosted'] else '无', sg['peak'],
                sg['end'], uend, sg['how'], '%.3f' % ex_r if ex_r is not None else '蹲走（不算）', ex_u, sg['maxd'], sg['n'])
            lines.append(line)
            print(line)
    lines += ['', '- 起跳那一行的 Unity 速度含起跳命令的空中加速（`extraAirAccel` 2 u/s²·dt 和 3D 上限，03 章），比参考多约 0.02 u/s 以内。',
              '- 松蹲 ≤ 350 结束的那条命令是蹲走（03 章），参考不算，所以"出口速度"写"蹲走"。']
    with open(os.path.join(here, 'ref_slide.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(lines) + '\n')


if __name__ == '__main__':
    main()
