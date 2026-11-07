"""Extract crosshair / reticle / on-gun RUI data from R5 S21 weapon settings files.
usage: py -3 -I xhair.py <weapons dir> <out dir> <id list...>
Writes ui-crosshair.tsv (one row per weapon crosshair), ui-reticles.tsv (UiData blocks + which mod enables them),
ui-crosshair-mods.tsv (mods that change crosshair fields)."""
import os, re, sys

TOK = re.compile(r'"((?:[^"\\]|\\.)*)"|(\{)|(\})|//[^\n]*')


def parse(text):
    toks = [m for m in TOK.finditer(text)]
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(toks):
            m = toks[pos]
            if m.group(3):
                pos += 1
                return items
            if m.group(1) is None:
                pos += 1
                continue
            key = m.group(1)
            pos += 1
            if pos < len(toks) and toks[pos].group(2):
                pos += 1
                items.append((key, block()))
            elif pos < len(toks) and toks[pos].group(1) is not None:
                items.append((key, toks[pos].group(1)))
                pos += 1
        return items

    return block()


def get(items, key):
    for k, v in items:
        if k == key:
            return v
    return None


def fields_matching(items, pred):
    return [(k, v) for k, v in items if isinstance(v, str) and pred(k)]


def main():
    wdir, out = sys.argv[1], sys.argv[2]
    ids = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    xr, rr, mr = [], [], []
    XKEYS = ('active_crosshair_count', 'rui_crosshair_index', 'red_crosshair_range', 'viewmodel_ads_rui_bottomleft_attachment',
             'spread_stand_hip', 'spread_stand_hip_run', 'spread_stand_hip_sprint', 'spread_crouch_hip', 'spread_air_hip',
             'spread_stand_ads', 'spread_air_ads', 'spread_kick_on_fire_stand_hip', 'spread_max_kick_stand_hip',
             'blast_pattern', 'projectiles_per_shot', 'charge_time', 'ammo_clip_size', 'fire_mode')
    for wid in ids:
        p = os.path.join(wdir, wid + '.txt')
        if not os.path.exists(p):
            print('missing', wid, file=sys.stderr)
            continue
        root = parse(open(p, encoding='utf-8', errors='replace').read())
        w = root[0][1] if root and isinstance(root[0][1], list) else root
        base = {k: get(w, k) for k in XKEYS}
        cd = get(w, 'RUI_CrosshairData')
        dargs = ''
        if isinstance(cd, list):
            da = get(cd, 'DefaultArgs')
            if isinstance(da, list):
                dargs = ','.join(k for k, _ in da)
            for k, v in cd:
                if k.startswith('Crosshair_') and isinstance(v, list):
                    args = get(v, 'Args')
                    xr.append([wid, k, get(v, 'ui') or '', get(v, 'base_spread') or '',
                               ','.join(a for a, _ in args) if isinstance(args, list) else '', dargs] + [base[x] or '' for x in XKEYS])
        enabled = {k: v for k, v in w if isinstance(v, str) and re.fullmatch(r'ui\d+_enable', k)}
        mods = get(w, 'Mods')
        modmap = {}
        if isinstance(mods, list):
            for mname, mv in mods:
                if not isinstance(mv, list):
                    continue
                for k, v in mv:
                    if not isinstance(v, str):
                        continue
                    if re.fullmatch(r'ui\d+_enable', k) and v.strip('+*') not in ('0',):
                        modmap.setdefault(k, []).append(mname)
                    if 'crosshair' in k or k in ('viewmodel_ads_rui_bottomleft_attachment',):
                        mr.append([wid, mname, k, v])
        for k, v in w:
            m = re.fullmatch(r'UiData(\d+)', k)
            if m and isinstance(v, list):
                n = m.group(1)
                args = get(v, 'Args')
                rr.append([wid, 'ui' + n, get(v, 'ui') or '', get(v, 'mesh') or '', enabled.get('ui%s_enable' % n, ''),
                           ' '.join(sorted(set(modmap.get('ui%s_enable' % n, [])))),
                           ','.join(a for a, _ in args) if isinstance(args, list) else ''])
    with open(os.path.join(out, 'ui-crosshair.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('\t'.join(['weapon', 'slot', 'ui', 'base_spread', 'args', 'default_args'] + list(XKEYS)) + '\n')
        for r in xr:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(out, 'ui-reticles.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('weapon\tslot\tui\tmesh\tbase_enable\tenabled_by_mods\targs\n')
        for r in rr:
            f.write('\t'.join(r) + '\n')
    with open(os.path.join(out, 'ui-crosshair-mods.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('weapon\tmod\tfield\tvalue\n')
        for r in mr:
            f.write('\t'.join(r) + '\n')
    print(len(xr), len(rr), len(mr))


main()
