# N8-D: per-run phase window and launch from the [N8-PP] server log lines.
# Usage: python pp_analysis.py <session folder> (with runner.json and platform/logs)
import glob, re, sys, json, collections
base = sys.argv[1]
names = {t['run']: t['schedule'] for t in json.load(open(base + '/runner.json'))['trials']}
rows = collections.defaultdict(list)
for f in glob.glob(base + '/platform/logs/server/**/*', recursive=True):
    try: txt = open(f, encoding='utf-8', errors='replace').read()
    except Exception: continue
    for m in re.finditer(r'\[N8-PP\] run=(\d+) t=([\d.]+) ph=(\d) type=(-?\d+) z=([-\d.]+) vz=([-\d.]+) boost=([\d.]+)', txt):
        r = int(m.group(1)); rows[r].append(tuple(float(x) for x in m.groups()[1:]))
print('run schedule        n  phase_s  types  rise_max  vz_max  ph_at_vzmax  boost_max')
for r in sorted(rows):
    v = sorted(set(rows[r]))
    t0 = v[0][0]; z0 = v[0][3]
    ph = [x for x in v if x[1] == 1]
    ph_s = (ph[-1][0] - ph[0][0]) if ph else 0
    top = max(v, key=lambda x: x[4])
    print('%d %-14s %4d  %5.2f  %-6s %7.1f  %7.1f  %d (t=%.2f)  %.2f' % (r, names.get(r, '?'), len(v), ph_s,
          ','.join(sorted({str(int(x[2])) for x in ph})) or '-', max(x[3] for x in v) - z0, top[4], int(top[1]), top[0] - t0, max(x[5] for x in v)))
