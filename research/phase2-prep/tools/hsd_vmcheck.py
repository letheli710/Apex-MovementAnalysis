#!/usr/bin/env python3
"""Per-VM API evidence check for an R5Flowstate Squirrel mod.

Why: Respawn Squirrel resolves global functions and constants when a script is
compiled. A global name that does not exist in a VM is expected to fail that
VM's compile, not just the mod (inference from how the base scripts are
structured; not observed here). Entity methods are looked up at run time, so a
missing method fails only the calling code and a try/catch can contain it
(also an inference).

What it does: indexes the base script tree (scripts.rson When blocks plus
#if/#elseif/#else/#endif guards), then for every global call, enum/constant
and method in the mod's scripts reports, per VM (SERVER, CLIENT), the
strongest evidence that the name exists there:

  DEF   a `global function` declaration compiled in that VM
  USE   the base calls/uses the name in code compiled in that VM
  WEAK  only uses whose guard or When cannot be decided statically
        (DEVELOPER, DEV, MAP_*, GAMEMODE_*, ...)
  NONE  no evidence at all -> reported as an error for globals/constants

Evidence is "the base does this too", not a signature check. Standard library only.
"""
import argparse
import os
import re
import sys

VMS = ("SERVER", "CLIENT", "UI")
YES, MAYBE, NO = 2, 1, 0
SQ_KEYWORDS = {
    "if", "else", "while", "for", "foreach", "return", "function", "switch", "case", "try", "catch",
    "thread", "delete", "typeof", "in", "array", "table", "expect", "waitthread", "wait", "void", "int",
    "float", "bool", "string", "vector", "entity", "var", "const", "global", "struct", "enum", "local",
    "functionref", "ornull", "asset", "clone", "resume", "yield", "throw", "break", "continue", "default",
    "null", "true", "false", "this", "extends", "class", "static", "untyped", "unreachable",
}


def tri_and(a, b):
    return min(a, b)


def tri_or(a, b):
    return max(a, b)


def tri_not(a):
    return {YES: NO, NO: YES, MAYBE: MAYBE}[a]


def eval_expr(expr, values):
    """Tri-state evaluation of a `When` / `#if` expression. Unknown words -> MAYBE."""
    toks = re.findall(r"&&|\|\||!|\(|\)|[A-Za-z_][A-Za-z_0-9]*|\S", expr)
    pos = 0

    def peek():
        return toks[pos] if pos < len(toks) else None

    def unary():
        nonlocal pos
        t = peek()
        if t == "!":
            pos += 1
            return tri_not(unary())
        if t == "(":
            pos += 1
            v = orexpr()
            if peek() == ")":
                pos += 1
            return v
        pos += 1
        if t is None:
            return MAYBE
        if re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", t):
            return values.get(t, MAYBE)
        return MAYBE

    def andexpr():
        nonlocal pos
        v = unary()
        while peek() == "&&":
            pos += 1
            v = tri_and(v, unary())
        return v

    def orexpr():
        nonlocal pos
        v = andexpr()
        while peek() == "||":
            pos += 1
            v = tri_or(v, andexpr())
        return v

    return orexpr()


def vm_values(vm):
    v = {name: (YES if name == vm else NO) for name in VMS}
    v.update({"MP": YES, "SP": NO})
    return v


def strip_code(src):
    """Blank out comments and string contents, keeping line structure."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j]))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and src[j] != '"' and src[j] != "\n":
                j += 2 if src[j] == "\\" else 1
            out.append('""' + " " * max(0, min(j, n - 1) - i - 1))
            i = min(j + 1, n)
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_rson(path):
    """Return [(when_expr, [script paths])] from a scripts.rson."""
    text = open(path, encoding="utf-8", errors="replace").read()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    blocks = []
    for when, body in re.findall(r'When:\s*"([^"]*)"\s*Scripts:\s*\[(.*?)\]', text, flags=re.S):
        blocks.append((when, [s.replace("\\", "/") for s in body.split()]))
    return blocks


def file_vm_states(blocks):
    """script path (lowercase) -> {vm: tri-state}"""
    states = {}
    for when, scripts in blocks:
        for vm in VMS:
            st = eval_expr(when, vm_values(vm))
            for s in scripts:
                d = states.setdefault(s.lower(), {x: NO for x in VMS})
                d[vm] = tri_or(d[vm], st)
    return states


def line_guards(code, vm):
    """Per line: tri-state that the line is compiled in `vm` given #if guards."""
    vals = vm_values(vm)
    stack = []  # entries: [parent_active, branch_taken, current_active]
    active = YES
    res = []
    for line in code.split("\n"):
        t = line.strip()
        m = re.match(r"#\s*(if|elseif|else|endif)\b(.*)", t)
        if m:
            kw, rest = m.group(1), m.group(2)
            if kw == "if":
                cond = eval_expr(rest, vals)
                stack.append([active, cond, tri_and(active, cond)])
                active = stack[-1][2]
            elif kw == "elseif" and stack:
                parent, taken, _ = stack[-1]
                cond = eval_expr(rest, vals)
                cur = tri_and(parent, tri_and(tri_not(taken), cond))
                stack[-1] = [parent, tri_or(taken, cond), cur]
                active = cur
            elif kw == "else" and stack:
                parent, taken, _ = stack[-1]
                cur = tri_and(parent, tri_not(taken))
                stack[-1] = [parent, YES, cur]
                active = cur
            elif kw == "endif" and stack:
                active = stack.pop()[0]
            res.append(NO)
            continue
        res.append(active)
    return res


class Index:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.blocks = parse_rson(os.path.join(base_dir, "scripts.rson"))
        self.fstates = file_vm_states(self.blocks)
        self.decl = {}     # name -> {vm: tri}
        self.defined = set()
        self.use = {}      # name -> {vm: tri}
        self.meth = {}     # name -> {vm: tri}
        self.sites = {}    # name -> [(vm, tri, "file:line")] for --why
        self.files = 0
        for root, _d, files in os.walk(base_dir):
            for f in files:
                if f.endswith((".nut", ".gnut")):
                    self._index_file(os.path.join(root, f))

    @staticmethod
    def _bump(table, name, vm, st):
        d = table.setdefault(name, {x: NO for x in VMS})
        d[vm] = tri_or(d[vm], st)

    def _site(self, name, vm, st, where):
        lst = self.sites.setdefault(name, [])
        if len(lst) < 400:
            lst.append((vm, st, where))

    def _index_file(self, path):
        rel = os.path.relpath(path, self.base_dir).replace("\\", "/").lower()
        fst = self.fstates.get(rel)
        if fst is None:
            return
        self.files += 1
        code = strip_code(open(path, encoding="utf-8", errors="replace").read())
        lines = code.split("\n")
        for name in re.findall(r"\bfunction\s+(\w+)\s*\(", code):
            self.defined.add(name)
        for vm in VMS:
            if fst[vm] == NO:
                continue
            guards = line_guards(code, vm)
            for ln, line in enumerate(lines):
                st = tri_and(fst[vm], guards[ln])
                if st == NO:
                    continue
                where = f"{rel}:{ln + 1}"
                for name in re.findall(r"global\s+function\s+(\w+)", line):
                    self._bump(self.decl, name, vm, st)
                    self._site(name, vm, st, where + " (decl)")
                for name in re.findall(r"global\s+(?:const\s+)?enum\s+(\w+)", line):
                    self._bump(self.decl, name, vm, st)
                    self._site(name, vm, st, where + " (decl)")
                for name in re.findall(r"(?<![.\w])([A-Za-z_]\w*)\s*\(", line) + re.findall(r"\b(IN_[A-Z0-9_]+)\b", line):
                    self._bump(self.use, name, vm, st)
                    self._site(name, vm, st, where)
                for name in re.findall(r"\.([A-Za-z_]\w*)\s*\(", line):
                    self._bump(self.meth, name, vm, st)
                    self._site("." + name, vm, st, where)


LABEL = {YES: "USE", MAYBE: "WEAK", NO: "NONE"}


def evidence(idx, kind, name, vm):
    if kind == "method":
        return LABEL[idx.meth.get(name, {}).get(vm, NO)]
    d = idx.decl.get(name, {}).get(vm, NO)
    if d == YES:
        return "DEF"
    u = idx.use.get(name, {}).get(vm, NO)
    best = max(d, u)
    return LABEL[best] if best != YES else "USE"


def check_mod(mod_dir, idx):
    rson = os.path.join(mod_dir, "scripts", "vscripts", "scripts.rson")
    blocks = parse_rson(rson)
    rows, errors = [], []
    seen = set()
    for when, scripts in blocks:
        for s in scripts:
            path = os.path.join(mod_dir, "scripts", "vscripts", s)
            code = strip_code(open(path, encoding="utf-8").read())
            lines = code.split("\n")
            local_defs = set(re.findall(r"\bfunction\s+(\w+)\s*\(", code))
            local_consts = set(re.findall(r"\bconst\s+[\w<>\[\] ]+?\s+(\w+)\s*=", code))
            for vm in ("SERVER", "CLIENT"):
                fst = eval_expr(when, vm_values(vm))
                if fst == NO:
                    continue
                guards = line_guards(code, vm)
                for ln, line in enumerate(lines, 1):
                    if tri_and(fst, guards[ln - 1]) == NO:
                        continue
                    items = []
                    items += [("global", n) for n in re.findall(r"(?<![.\w])([A-Za-z_]\w*)\s*\(", line)
                              if n not in SQ_KEYWORDS and n not in local_defs]
                    items += [("const", n) for n in re.findall(r"\b(IN_[A-Z0-9_]+)\b", line)]
                    items += [("enum", n) for n in re.findall(r"\b(e[A-Z]\w+)\s*\.", line) if n not in local_consts]
                    items += [("method", n) for n in re.findall(r"\.([A-Za-z_]\w*)\s*\(", line)]
                    for kind, name in items:
                        key = (vm, kind, name)
                        if key in seen:
                            continue
                        seen.add(key)
                        ev = evidence(idx, kind, name, vm)
                        rows.append((vm, kind, name, ev, f"{s}:{ln}"))
                        if kind != "method" and ev == "NONE":
                            errors.append(f"{vm}: {kind} '{name}' ({s}:{ln}) has no evidence in the base {vm} VM")
    return rows, errors


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mod_dir")
    ap.add_argument("--base", required=True, help="base scripts/vscripts directory (contains scripts.rson)")
    ap.add_argument("--strict", action="store_true", help="also fail on methods without evidence and on WEAK globals")
    ap.add_argument("--why", action="append", default=[], metavar="NAME",
                    help="print the base sites behind NAME's evidence (prefix methods with '.')")
    a = ap.parse_args(argv)
    idx = Index(a.base)
    for name in a.why:
        for vm, st, where in idx.sites.get(name, []):
            if st != NO:
                print(f"why {name:30s} {vm:7s} {LABEL[st]:5s} {where}")
    rows, errors = check_mod(a.mod_dir, idx)
    print(f"indexed {idx.files} base files listed in scripts.rson")
    print(f"{'VM':7s} {'kind':7s} {'name':40s} {'evidence':8s} first use")
    for vm, kind, name, ev, where in sorted(rows):
        print(f"{vm:7s} {kind:7s} {name:40s} {ev:8s} {where}")
    if a.strict:
        errors += [f"{vm}: {kind} '{n}' evidence {ev}" for vm, kind, n, ev, _ in rows
                   if (kind == "method" and ev == "NONE") or ev == "WEAK"]
    for e in errors:
        print("ERROR " + e)
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
