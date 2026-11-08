"""Resolve TF2 aisettings KeyValues files (#base inheritance, [$mp]/[$sp] tags).

Usage: py -3 -I kv_resolve.py <aisettings_dir> <out_tsv>

Writes a long table: npc, key, mp, sp, mp_src, sp_src (src = file:line of the winning line).
Nested blocks such as  "mp" [$mp] { ... }  are flattened: their keys apply under the block's tag.
A later line wins over an earlier one for the same key and mode; a child file wins over its #base.
"""
import os
import re
import sys

TOKEN = re.compile(r'"([^"]*)"|(\[[^\]]*\])|(\{)|(\})|([^\s"{}\[\]]+)')


def strip_comment(line):
    out, q = [], False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"':
            q = not q
        if not q and line.startswith("//", i):
            break
        out.append(c)
        i += 1
    return "".join(out)


def cond_ok(tag, mode):
    if tag is None:
        return True
    t = tag.strip("[]").replace(" ", "")
    # supports $mp, $sp, !$mp, !$sp, and a||b
    for alt in t.split("||"):
        neg = alt.startswith("!")
        name = alt.lstrip("!").lstrip("$").lower()
        val = (name == mode)
        if neg:
            val = not val
        if val:
            return True
    return False


def parse_file(path):
    """Return (bases, name, entries) where entries = [(key, value, [tags], lineno)]."""
    bases, entries = [], []
    name = None
    stack = []  # tags of open blocks
    pending_block = None  # (key, tag) waiting for '{'
    depth = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, raw in enumerate(f, 1):
            line = strip_comment(raw).strip()
            if not line:
                continue
            if line.startswith("#base"):
                m = re.search(r'"([^"]+)"', line)
                bases.append(m.group(1) if m else line.split()[1])
                continue
            toks = []
            for m in TOKEN.finditer(line):
                if m.group(1) is not None:
                    toks.append(("s", m.group(1)))
                elif m.group(2):
                    toks.append(("tag", m.group(2)))
                elif m.group(3):
                    toks.append(("{", "{"))
                elif m.group(4):
                    toks.append(("}", "}"))
                else:
                    toks.append(("s", m.group(5)))
            i = 0
            while i < len(toks):
                kind, val = toks[i]
                if kind == "{":
                    if depth == 0:
                        if pending_block is not None and name is None:
                            name = pending_block[0]
                        stack.append(None)
                    else:
                        stack.append(pending_block[1] if pending_block else None)
                    pending_block = None
                    depth += 1
                    i += 1
                    continue
                if kind == "}":
                    depth -= 1
                    stack.pop()
                    i += 1
                    continue
                if kind == "s":
                    # key [value] [tag]
                    key = val
                    rest = toks[i + 1:]
                    value, tag = None, None
                    j = i + 1
                    if j < len(toks) and toks[j][0] == "s":
                        value = toks[j][1]
                        j += 1
                    if j < len(toks) and toks[j][0] == "tag":
                        tag = toks[j][1]
                        j += 1
                    if value is None:
                        pending_block = (key, tag)
                    else:
                        tags = [t for t in stack if t] + ([tag] if tag else [])
                        if depth >= 1:
                            entries.append((key, value, tags, ln))
                    i = j
                    continue
                i += 1
    return bases, name, entries


def resolve(d, fname, mode, cache):
    ck = (fname, mode)
    if ck in cache:
        return cache[ck]
    path = os.path.join(d, fname)
    bases, name, entries = parse_file(path)
    res = {}
    for b in bases:
        res.update(resolve(d, b, mode, cache)[1])
    for key, value, tags, ln in entries:
        if all(cond_ok(t, mode) for t in tags):
            res[key.lower()] = (key, value, f"{fname}:{ln}")
    cache[ck] = (name, res)
    return cache[ck]


def main():
    d, out = sys.argv[1], sys.argv[2]
    cache = {}
    rows = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt") or fn in ("classes.txt",):
            continue
        name_mp, mp = resolve(d, fn, "mp", cache)
        _, sp = resolve(d, fn, "sp", cache)
        npc = fn[:-4]
        for k in sorted(set(mp) | set(sp)):
            a = mp.get(k)
            b = sp.get(k)
            key = (a or b)[0]
            rows.append([npc, key, a[1] if a else "", b[1] if b else "", a[2] if a else "", b[2] if b else ""])
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("npc\tkey\tmp\tsp\tmp_src\tsp_src\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(len(rows), "rows,", len({r[0] for r in rows}), "npcs")


if __name__ == "__main__":
    main()
