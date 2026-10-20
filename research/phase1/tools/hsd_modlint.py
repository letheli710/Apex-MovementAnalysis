#!/usr/bin/env python3
"""Static checks for an R5Flowstate mod folder, mirroring the SDK loader rules.

Rules come from s21-r5sdk (commit 10077bb):
  - mod.vdf required keys author/name/id/description/version, non-empty
    (pluginsystem/modsystem.cpp:971-1017)
  - mod id: 4..32 chars, starts with a letter, [A-Za-z0-9._] only, and the
    namespace (id, '.'->'_', lowercase) may not contain "__" (modsystem.cpp:895-1009)
  - every shipped file is owned: a fixed manifest file, or a path component that
    starts with "<namespace>__" or equals "<namespace>" (modsystem.cpp:1360-1555)
  - script entry points are <Prefix>_<id with '.'->'_'>_ModInit
    (game/shared/pluginsystem/modsystem.cpp:84, vscript/languages/squirrel_re/vsquirrel.h:100-108)
  - scripts.rson When uses only SERVER CLIENT UI SP MP DEV with && || ! ( )
    (vscript/vscript.cpp:440-446)

It also cross-references every global function and entity method the mod's
scripts call against a base script tree (--base), so a misspelt API shows up.
A name "seen in base" only proves the base scripts use it, not its signature.
This is not a Squirrel compiler.
"""
import argparse
import os
import re
import sys

FIXED_FILES = {
    "mod.vdf", "manifest.json", "icon.png", "readme.md", "changelog.md", "license", "license.md",
    "license.txt", "scripts/vscripts/scripts.rson", "paks/win64/preload.rson",
    "paks/win64_server/preload.rson", "playlists_r5_patch.txt",
}
WHEN_WORDS = {"SERVER", "CLIENT", "UI", "SP", "MP", "DEV"}
PREFIX = {"SERVER": "CodeCallback", "CLIENT": "ClientCodeCallback", "UI": "UICodeCallback"}
SQ_KEYWORDS = {
    "if", "else", "while", "for", "foreach", "return", "function", "switch", "case", "try", "catch",
    "thread", "delete", "typeof", "in", "array", "table", "format", "expect", "waitthread", "wait",
    "void", "int", "float", "bool", "string", "vector", "entity", "var", "const", "global", "struct",
}


def kv_parse(text):
    """Tiny Valve KeyValues reader: returns nested dicts, strips // comments."""
    toks = re.findall(r'"((?:[^"\\]|\\.)*)"|([{}])|//[^\n]*', text)
    pos = 0

    def block():
        nonlocal pos
        out = {}
        while pos < len(toks):
            s, br = toks[pos]
            if br == "}":
                pos += 1
                return out
            if br == "{":
                raise ValueError("unexpected {")
            if s == "" and br == "":
                pos += 1
                continue
            key = s
            pos += 1
            s2, br2 = toks[pos]
            if br2 == "{":
                pos += 1
                out[key] = block()
            else:
                out[key] = s2
                pos += 1
        return out

    root = block()
    return root


def strip_sq(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r'"(?:[^"\\\n]|\\.)*"', '""', src)
    return src


def check(mod_dir, base_dir):
    errs, notes = [], []
    vdf_path = os.path.join(mod_dir, "mod.vdf")
    kv = kv_parse(open(vdf_path, encoding="utf-8").read())
    if len(kv) != 1:
        errs.append("mod.vdf must have exactly one root block")
    settings = next(iter(kv.values()))
    for k in ("author", "name", "id", "description", "version"):
        if not isinstance(settings.get(k), str) or not settings.get(k):
            errs.append(f"mod.vdf missing/empty required key '{k}'")
    mod_id = settings.get("id", "")
    if not (4 <= len(mod_id) <= 32) or not mod_id[:1].isalpha() or not re.fullmatch(r"[A-Za-z0-9._]+", mod_id):
        errs.append(f"invalid mod id '{mod_id}'")
    ns = mod_id.replace(".", "_").lower()
    norm = mod_id.replace(".", "_")
    if "__" in ns:
        errs.append(f"namespace '{ns}' contains '__'")
    notes.append(f"id={mod_id} namespace={ns} entry-point suffix=_{norm}_ModInit")
    for name, cv in (settings.get("ConVars") or {}).items():
        if not name.startswith("hsd_") and not name.startswith(ns):
            notes.append(f"ConVar '{name}' is not prefixed with the mod's namespace (allowed, but collides more easily)")
        if re.search(r'["\r\n \t;]', name):
            errs.append(f"ConVar '{name}' has a forbidden character")

    # file ownership
    for root, _dirs, files in os.walk(mod_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), mod_dir).replace("\\", "/").lower()
            if rel in FIXED_FILES:
                continue
            comps = rel.split("/")
            owned = any(c.startswith(ns + "__") and len(c) > len(ns) + 2 for c in comps) or \
                any(c == ns for c in comps[:-1])
            if not owned:
                errs.append(f"file '{rel}' is outside namespace '{ns}' -> the loader refuses the whole mod")

    # scripts.rson
    rson = os.path.join(mod_dir, "scripts", "vscripts", "scripts.rson")
    scripts = []
    if os.path.exists(rson):
        text = re.sub(r"/\*.*?\*/", "", open(rson, encoding="utf-8").read(), flags=re.S)
        for when, body in re.findall(r'When:\s*"([^"]*)"\s*Scripts:\s*\[(.*?)\]', text, flags=re.S):
            words = set(re.findall(r"[A-Za-z_]+", when))
            bad = words - WHEN_WORDS
            if bad or re.search(r"[^A-Za-z_ &|!()]", when):
                errs.append(f"When '{when}' uses tokens outside {sorted(WHEN_WORDS)}: {sorted(bad)}")
            for s in body.split():
                p = os.path.join(mod_dir, "scripts", "vscripts", s)
                if not os.path.exists(p):
                    errs.append(f"scripts.rson lists missing file '{s}'")
                scripts.append((p, words))

    # script checks
    base_globals, base_text = set(), ""
    if base_dir:
        chunks = []
        for root, _d, files in os.walk(base_dir):
            for f in files:
                if f.endswith((".nut", ".gnut")):
                    t = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
                    chunks.append(t)
                    base_globals.update(re.findall(r"global\s+function\s+(\w+)", t))
        base_text = "\n".join(chunks)

    for path, vms in scripts:
        src = open(path, encoding="utf-8").read()
        code = strip_sq(src)
        for a, b in ("{}", "()", "[]"):
            if code.count(a) != code.count(b):
                errs.append(f"{os.path.basename(path)}: unbalanced {a}{b} ({code.count(a)} vs {code.count(b)})")
        depth = 0
        for ln, line in enumerate(code.splitlines(), 1):
            t = line.strip()
            if t.startswith("#if"):
                depth += 1
            elif t.startswith("#endif"):
                depth -= 1
                if depth < 0:
                    errs.append(f"{os.path.basename(path)}:{ln}: #endif without #if")
        if depth != 0:
            errs.append(f"{os.path.basename(path)}: {depth} unclosed #if")

        defined = set(re.findall(r"function\s+(\w+)\s*\(", code))
        declared = set(re.findall(r"global\s+function\s+(\w+)", code))
        for vm in sorted(vms & set(PREFIX)):
            ep = f"{PREFIX[vm]}_{norm}_ModInit"
            if ep not in declared or ep not in defined:
                errs.append(f"{os.path.basename(path)}: entry point {ep} for {vm} not declared+defined")
            else:
                notes.append(f"entry point {ep} present")
        undefined_decl = declared - defined
        if undefined_decl:
            errs.append(f"declared but not defined: {sorted(undefined_decl)}")

        if base_dir:
            calls = set(re.findall(r"(?<![.\w])([A-Za-z_]\w*)\s*\(", code)) - defined - SQ_KEYWORDS
            methods = set(re.findall(r"\.([A-Za-z_]\w*)\s*\(", code))
            for name in sorted(calls):
                if name in base_globals:
                    tag = "base global function"
                elif re.search(r"(?<![.\w])" + re.escape(name) + r"\s*\(", base_text):
                    tag = "used in base (native)"
                else:
                    tag = None
                    errs.append(f"call '{name}' not found anywhere in base scripts")
                if tag:
                    notes.append(f"call   {name:32s} {tag}")
            for name in sorted(methods):
                if re.search(r"\." + re.escape(name) + r"\s*\(", base_text):
                    notes.append(f"method .{name:31s} used in base")
                else:
                    errs.append(f"method '.{name}' not used anywhere in base scripts")
    return errs, notes


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mod_dir")
    ap.add_argument("--base", help="base scripts/vscripts tree to cross-reference API names")
    a = ap.parse_args(argv)
    errs, notes = check(a.mod_dir, a.base)
    for n in notes:
        print("  ok  " + n)
    for e in errs:
        print("ERROR " + e)
    print(f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
