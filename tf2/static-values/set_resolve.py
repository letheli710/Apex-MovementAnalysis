"""Resolve TF2 playersettings (.set) files with their #base chains.

Usage: python -I set_resolve.py <players_dir> <out_csv> [setname ...]
  players_dir: unpacked scripts/players/mp
  setname: files to resolve (default: every pilot_*.set); without the .set suffix.

Output rows: set, section (global/stand/crouch/...), key, value, defined_in.
ClassMods / PoseMods blocks are written as section "ClassMods:<mod>" / "PoseMods:<section>:<mod>"
and do not override the base value.
"""
import csv
import re
import sys
from pathlib import Path

TOKEN = re.compile(r'"([^"]*)"|([{}])|([^\s{}"]+)')


def tokenize(text):
    out = []
    for line in text.splitlines():
        line = line.split("//", 1)[0]
        for m in TOKEN.finditer(line):
            if m.group(1) is not None:
                out.append(m.group(1))
            else:
                out.append(m.group(2) or m.group(3))
    return out


def parse_block(tokens, i):
    """Parse 'key value' and 'key { ... }' pairs until '}'. Returns (list of (key, value), next index)."""
    items = []
    while i < len(tokens):
        t = tokens[i]
        if t == "}":
            return items, i + 1
        if i + 1 < len(tokens) and tokens[i + 1] == "{":
            sub, i = parse_block(tokens, i + 2)
            items.append((t, sub))
        else:
            items.append((t, tokens[i + 1] if i + 1 < len(tokens) else ""))
            i += 2
    return items, i


def load(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    base = None
    lines = []
    for line in text.splitlines():
        m = re.match(r'\s*#base\s+"([^"]+)"', line)
        if m:
            base = m.group(1)
        else:
            lines.append(line)
    tokens = tokenize("\n".join(lines))
    items, _ = parse_block(tokens, 0)
    # top level: "name" { sections }, plus a few loose keys such as raceOrSex
    root = {}
    loose = {}
    for k, v in items:
        if isinstance(v, list):
            root = v
        else:
            loose[k] = v
    return base, root, loose


def flatten(set_name, sections, src, table):
    for sec, body in sections:
        if not isinstance(body, list):
            table[("global", sec)] = (body, src)
            continue
        for k, v in body:
            if isinstance(v, list) and k in ("ClassMods", "PoseMods"):
                for mod, mbody in v:
                    for mk, mv in mbody if isinstance(mbody, list) else []:
                        if isinstance(mv, list):
                            for mmk, mmv in mv:
                                table[(f"{k}:{sec}:{mod}:{mk}" if k == "PoseMods" else f"{k}:{mod}:{mk}", mmk)] = (mmv, src)
                        else:
                            name = f"PoseMods:{sec}:{mod}" if k == "PoseMods" else f"ClassMods:{mod}"
                            table[(name, mk)] = (mv, src)
            elif isinstance(v, list):
                for kk, vv in v:
                    table[(f"{sec}.{k}", kk)] = (vv if not isinstance(vv, list) else "<block>", src)
            else:
                table[(sec, k)] = (v, src)


def resolve(players, name, cache):
    if name in cache:
        return cache[name]
    path = players / (name + ".set")
    base, root, loose = load(path)
    table = {}
    if base:
        table.update(resolve(players, base[:-4] if base.endswith(".set") else base, cache))
    for k, v in loose.items():
        table[("global", k)] = (v, path.name)
    flatten(name, root, path.name, table)
    cache[name] = table
    return table


def main():
    players = Path(sys.argv[1])
    out = Path(sys.argv[2])
    names = sys.argv[3:] or sorted(p.stem for p in players.glob("pilot_*.set"))
    cache = {}
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["set", "section", "key", "value", "defined_in"])
        for n in names:
            for (sec, k), (v, src) in sorted(resolve(players, n, cache).items(), key=lambda x: (x[0][0].lower(), x[0][1].lower())):
                w.writerow([n, sec, k, v, src])


if __name__ == "__main__":
    main()
