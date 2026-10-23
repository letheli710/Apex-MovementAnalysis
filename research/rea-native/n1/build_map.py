"""Build the N1 map tables from the raw Ghidra exports.

Inputs (all TSV, from the Ghidra scripts in this folder, kept under local/):
  functions.tsv, edges.tsv, convars.tsv   MapMovement.java
  setfile-descriptors.tsv                 scan_setfile_desc.py
  setfile-readers.tsv                     SetfileReaders.java
plus the SDK source tree (hooks) and seeds-dx12.tsv (SDK names).

Outputs (CSV, addresses and names only):
  map/functions.csv  every map function with its subsystem guess
  map/reads.csv      function x ConVar / setfile key read sites
  map/sdk-hooks.csv  SDK client detours and patches on native functions
  map/setfile-keys.csv  every setfile key descriptor, with reader count

Usage: build_map.py <raw dir> <sdk src> <out dir>
"""
import csv
import pathlib
import re
import sys
from collections import Counter, defaultdict

# Subsystem codes follow REA-PLAN-DRAFT.md section 5. Order matters: the first
# matching rule wins for a name, so camera rules come before their movement parents.
RULES = [
    ('C', r'viewpunch|viewDrift|viewTilt|ViewTilt|sprinttilt|banktilt|BankTilt|cockpitDrift|view_offset|ViewOffset'
          r'|grapple_roll|_fov|Fov|FOV|eyeOffset|EyeOffset|viewHeight|cameraShake|camera'),
    ('L', r'^jump_grace'),
    ('S', r'slide|Slide'),
    ('P', r'grapple|Grapple'),
    ('Z', r'zipline|ziprail|Zipline|tether'),
    ('M', r'traversal|mantle|Mantle|wallrun|wallRun|Wallrun|wallclimb|wall_climb|wallHang|hang|window_hint|climb'),
    ('F', r'jumppad|jumpPad|superjump|gravityCannon|launch|Launch|skyward'),
    ('J', r'^skip_|jump|Jump|air|Air|gravity|Gravity|landSlowdown|land|fall|Fall|doubleJump'),
    ('G', r'^sv_friction|^sv_stopspeed|^sv_maxspeed|^sv_backspeed|speed|Speed|accel|Accel|decel|Decel|stepHeight|step'),
    ('X', r'melee|lunge|dodge|airslowmo|armored_leap|freefall|stim|phase'),
]
SEED_RULES = [
    ('C', r'Eye|View|Punch'),
    ('L', r'TapStrafe'),
    ('S', r'Slide'),
    ('P', r'Grapple'),
    ('Z', r'Zipline'),
    ('M', r'Traversal|WallRun|Mantle'),
    ('F', r'JumpPad|GravityCannon|Launch'),
    ('J', r'Jump|AirMove|AirAccelerate|TouchGround|SetGroundEntity'),
    ('G', r'FullWalkMove|WalkMove|Duck|GroundMove'),
    ('X', r'Melee|Lunge'),
]


def classify(name, rules):
    for code, rx in rules:
        if re.search(rx, name):
            return code
    return None


def read_tsv(p):
    with open(p, encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def sdk_hooks(src):
    rows = []
    for f in sorted(pathlib.Path(src, 'game', 'client').rglob('*.cpp')):
        txt = f.read_text(errors='replace')
        purpose = ''
        m = re.search(r'//\s*Purpose:\s*(.+)', txt)
        if m:
            purpose = m.group(1).strip()
        for m in re.finditer(r'DetourSetup\(\s*&\s*(\w+)\s*,\s*&?\s*([\w:]+)', txt):
            rows.append({'native': m.group(1), 'hook': m.group(2), 'kind': 'detour',
                         'sdk_file': 'game/client/' + f.name, 'purpose': purpose})
        for m in re.finditer(r'(\w+)\s*\.\s*(?:Offset\([^)]*\)\s*\.\s*)?Patch\(', txt):
            rows.append({'native': m.group(1), 'hook': '', 'kind': 'byte-patch',
                         'sdk_file': 'game/client/' + f.name, 'purpose': purpose})
    return rows


def main(raw, src, out):
    raw, out = pathlib.Path(raw), pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    funcs = read_tsv(raw / 'functions.tsv')
    seeds = {}
    for line in pathlib.Path(__file__).with_name('seeds-dx12.tsv').read_text().splitlines():
        if line and not line.startswith('#'):
            n, a = line.split('\t')[:2]
            seeds.setdefault(a, n)

    provisional = {}
    for line in pathlib.Path(__file__).with_name('names-dx12.tsv').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            a, n, ev = line.split('\t')[:3]
            provisional[a] = (n, ev)

    reads = []
    for r in read_tsv(raw / 'convars.tsv'):
        if r['offset'] == '0x40':  # the only offset movement code reads (ConVarReaders.java)
            reads.append({'function': r['function'], 'kind': 'convar', 'name': r['convar'], 'type': '',
                          'site': r['site']})
    for r in read_tsv(raw / 'setfile-readers.tsv'):
        if r['site'] != 'NO_READS' and r['function']:
            reads.append({'function': r['function'], 'kind': 'setfile', 'name': r['key'], 'type': r['type'],
                          'site': r['site']})
    by_fn = defaultdict(list)
    for r in reads:
        by_fn[r['function']].append(r)

    in_map = {f['entry'] for f in funcs}
    with open(out / 'reads.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, ['function', 'kind', 'name', 'type', 'site'])
        w.writeheader()
        for r in sorted(reads, key=lambda r: (r['function'], r['kind'], r['name'], r['site'])):
            if r['function'] in in_map:
                w.writerow(r)

    rows = []
    for fn in funcs:
        e = fn['entry']
        names = [r['name'] for r in by_fn.get(e, [])]
        score = Counter(c for c in (classify(n, RULES) for n in names) if c)
        seed = seeds.get(e)
        guess = classify(seed, SEED_RULES) if seed else None
        if not guess and score:
            guess = score.most_common(1)[0][0]
        top = [n for n, _ in Counter(names).most_common(8)]
        ours = provisional.get(e)
        rows.append({
            'entry_dx12': e,
            'name': seed or (ours[0] if ours else fn['name']),
            'name_source': 'sdk' if seed else ('n1' if ours else 'ghidra'),
            'name_evidence': ours[1] if ours and not seed else '',
            'reason': fn['reason'],
            'window': fn['window'],
            'size': fn['size'],
            'subsystem': guess or '',
            'subsystem_votes': ' '.join(f'{k}:{v}' for k, v in score.most_common()),
            'convar_reads': sum(1 for r in by_fn.get(e, []) if r['kind'] == 'convar'),
            'setfile_reads': sum(1 for r in by_fn.get(e, []) if r['kind'] == 'setfile'),
            'top_reads': ' '.join(top),
            'callers': fn['callers'],
            'callees': fn['callees'],
        })
    # Functions with no reads of their own take the majority subsystem of their
    # direct neighbours (callers and callees), marked with '?'. Two passes let a
    # guess spread one step further.
    nb = defaultdict(set)
    for ed in read_tsv(raw / 'edges.tsv'):
        nb[ed['caller']].add(ed['callee'])
        nb[ed['callee']].add(ed['caller'])
    sub = {r['entry_dx12']: r['subsystem'] for r in rows}
    for _ in range(2):
        new = {}
        for r in rows:
            e = r['entry_dx12']
            if sub[e]:
                continue
            votes = Counter(sub[n].rstrip('?') for n in nb[e] if sub.get(n))
            if votes:
                new[e] = votes.most_common(1)[0][0] + '?'
        sub.update(new)
    for r in rows:
        r['subsystem'] = sub[r['entry_dx12']]

    with open(out / 'functions.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    readers = Counter()
    for r in read_tsv(raw / 'setfile-readers.tsv'):
        if r['site'] != 'NO_READS':
            readers[r['key']] += 1
    with open(out / 'setfile-keys.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['key', 'type', 'descriptor_dx12', 'read_sites', 'subsystem'])
        for d in read_tsv(raw / 'setfile-descriptors.tsv'):
            w.writerow([d['key'], d['type'], d['descriptor'], readers[d['key']], classify(d['key'], RULES) or ''])

    # Several SDK names share one entry (e.g. two Jump patterns), so map every name.
    entry_of = {}
    for line in pathlib.Path(__file__).with_name('seeds-dx12.tsv').read_text().splitlines():
        if line and not line.startswith('#'):
            n, a = line.split('\t')[:2]
            if a != 'NONE':
                entry_of.setdefault(n, a)
    hooks = sdk_hooks(src)
    with open(out / 'sdk-hooks.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, ['native', 'entry_dx12', 'hook', 'kind', 'sdk_file', 'purpose'])
        w.writeheader()
        for h in hooks:
            h['entry_dx12'] = entry_of.get(h['native'], '')
            w.writerow(h)

    print('functions', len(rows), 'reads', len(reads), 'hooks', len(hooks))
    print('subsystems (window + seed):',
          Counter(r['subsystem'] or '-' for r in rows if r['window'] or r['name_source'] == 'sdk'))


if __name__ == '__main__':
    main(*sys.argv[1:4])
