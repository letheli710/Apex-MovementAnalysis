"""Light terrain score (lead 11-13), from terrain_stats.py --json files (replay_terrain.py mesh numbers).

  py -3 light_terrain_score.py <c1-off L1.json> <run L1.json> [<run L2.json> ...]

Per feature (12 features x walk out / sprint back = 24), mesh lines as the heavy's (model/v3/H/score2.py):
  normal: planted >= -0.02, planted high <= +0.03, swing >= +0.05, 0 contact frames
  extreme (stairs80x300, ramp30): planted >= -0.05, high <= +0.05, swing >= 0, contacts <= 1 % of the feature's checked frames
Slide (lead): per feature no worse than C1 off (hard), total <= 2 x the light's flat value. Flat value: the 2c walk route, 1.97 m / 100 m
(HSD-Unity #74, tall default) -> 3.94.
'shortfall' = sum of how far each line is missed (metres), as score2.py."""
import json
import sys

F = ['drop', 'ramp5', 'ramp10', 'ramp15', 'ramp20', 'ramp30', 'stairs11x60', 'stairs20x80', 'stairs20x200', 'stairs40x100', 'stairs40x250', 'stairs80x300']
EXT = {'ramp30', 'stairs80x300'}
FLAT = 1.97


def load(p):
    return {(r['feature'], r['part']): r for r in json.load(open(p)) if r['feature'] in F}


def score(off, rows, verbose=False):
    pen = ok = okslide = cc = 0
    lines = []
    for k, r in sorted(rows.items(), key=lambda kv: (kv[0][1], F.index(kv[0][0]))):
        ext = k[0] in EXT
        lp, ls, lh, lc = (-0.05, 0.0, 0.05, 0.01) if ext else (-0.02, 0.05, 0.03, 0.0)
        lo, hi, sw, c = r['m_planted_low'], r['m_planted_high'], r['m_swing_low'], r['m_contacts']
        p = max(0, lp - lo) + max(0, ls - sw) + max(0, hi - lh)
        good = lo >= lp and sw >= ls and hi <= lh and c <= lc * max(1, r['m_frames'])
        so = off.get(k, {}).get('slide_per_100m', 9e9)
        sgood = r['slide_per_100m'] <= so + 1e-6
        pen += p; ok += good; okslide += good and sgood; cc += c
        if verbose:
            lines.append('%-6s %-13s planted %6.3f..%6.3f swing %6.3f contacts %3d/%3d slide %5.1f (off %5.1f)%s%s' % (
                k[1], k[0], lo, hi, sw, c, r['m_frames'], r['slide_per_100m'], so, '' if good else '  LINE', '' if sgood else '  SLIDE'))
    sl = sum(r['slide'] for r in rows.values()) / sum(r['dist'] for r in rows.values()) * 100
    return dict(shortfall=round(pen, 2), passed=ok, passed_with_slide=okslide, of=len(rows), contacts=cc, slide=round(sl, 2), slide_limit=2 * FLAT), lines


if __name__ == '__main__':
    off = load(sys.argv[1])
    for p in [a for a in sys.argv[2:] if not a.startswith('-')]:
        s, lines = score(off, load(p), verbose='-v' in sys.argv)
        print(p.replace('\\', '/').split('/')[-2] + '/' + p.replace('\\', '/').split('/')[-1], json.dumps(s))
        for l in lines:
            print('   ', l)
