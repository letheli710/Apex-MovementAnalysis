#!/usr/bin/env python3
"""Check `path:line` references in the research Markdown against the sources.

  python check_refs.py [--src-root /home/user/research-src] [docs...]

For every backticked reference like `game/server/tapstrafe.cpp:31-41` or
`s21-platform/scripts/vscripts/sh_consts.gnut:1000-1015` it resolves the file
(repo-relative, s21-r5sdk/src-relative, s21-platform/scripts/vscripts-relative
or by unique basename) and checks that every cited line exists. A basename that
matches several files passes if any candidate has the lines (reported as
'ambiguous'). Without the source clones, external references are 'unchecked'.
Exit 1 when a reference names a missing file or a line past the end of the file.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
EXT = r"(?:cpp|h|inl|gnut|nut|cfg|md|txt|rson|vdf|py|json|cs|xaml|csv)"
REF_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\." + EXT + r")(?::([0-9][0-9,\- ]*))?`")
MD_LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
# Files that only exist inside a game install at run time, not in any repository.
RUNTIME_RE = re.compile(r"(^|/)(mods\.vdf|required_mods\.vdf|allowed_mods\.vdf|scriptdump_[^/]*|hsd_[a-z0-9_]*\.cfg)$|^\.|^mods/|^<")
SKIP_MARK = "refcheck:skip"   # put <!-- refcheck:skip --> on a line that quotes an old/wrong reference on purpose


def default_src_root():
    """HSD_SRC_ROOT, else the cloud path, else a research-src/ folder beside the repository."""
    if os.environ.get("HSD_SRC_ROOT"):
        return os.environ["HSD_SRC_ROOT"]
    for p in ("/home/user/research-src", os.path.join(REPO, os.pardir, "research-src")):
        if os.path.isdir(p):
            return os.path.normpath(p)
    return "/home/user/research-src"


def line_numbers(spec):
    out = []
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            if a.isdigit() and b.isdigit():
                out += [int(a), int(b)]
        elif part.isdigit():
            out.append(int(part))
    return out


class Resolver:
    def __init__(self, src_root):
        self.roots = [REPO]
        self.ext_roots = []
        if src_root and os.path.isdir(src_root):
            for sub in ("s21-r5sdk/src", "s21-r5sdk", "s21-platform", "s21-platform/scripts/vscripts",
                        "s21-platform/scripts", "launcher", "launcher/src", ""):
                p = os.path.join(src_root, sub)
                if os.path.isdir(p):
                    self.ext_roots.append(p)
        self.by_base = {}
        for root in [REPO] + ([src_root] if src_root and os.path.isdir(src_root) else []):
            for cur, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "thirdparty", "node_modules")]
                for f in files:
                    self.by_base.setdefault(f, []).append(os.path.join(cur, f))
        self._lines = {}

    def count(self, path):
        if path not in self._lines:
            with open(path, "rb") as fh:
                self._lines[path] = fh.read().count(b"\n") + 1
        return self._lines[path]

    def candidates(self, ref, doc_dir):
        ref = ref.replace("\\", "/")
        out = []
        for root in [doc_dir, REPO] + self.ext_roots:
            p = os.path.normpath(os.path.join(root, ref))
            if os.path.isfile(p):
                out.append(p)
        if out:
            return sorted(set(out)), False
        tail = [p for p in self.by_base.get(os.path.basename(ref), []) if p.replace("\\", "/").endswith(ref)]
        return sorted(set(tail)), len(set(tail)) > 1


def external(ref):
    return not ref.startswith(("research/", "tools/", "tests/", "cfg/", "fixtures/", "results/", "mod/"))


def check(docs, src_root):
    res = Resolver(src_root)
    have_src = bool(res.ext_roots)
    rows = []
    for doc in docs:
        doc_dir = os.path.dirname(os.path.abspath(doc))
        with open(doc, encoding="utf-8") as fh:
            text = fh.read()
        for ln, line in enumerate(text.split("\n"), 1):
            if SKIP_MARK in line:
                continue
            for m in REF_RE.finditer(line):
                ref, spec = m.group(1).replace("\\", "/"), m.group(2) or ""
                if ref.startswith(("http", "<")) or "*" in ref or RUNTIME_RE.search(ref):
                    continue
                cands, ambiguous = res.candidates(ref, doc_dir)
                lines = line_numbers(spec)
                if not cands:
                    if "/" not in ref and not spec:
                        status = "bare_name"       # an output/file name mentioned in prose, not a path
                    elif not have_src and external(ref):
                        status = "unchecked"
                    else:
                        status = "missing_file"
                    rows.append((doc, ln, ref + (":" + spec if spec else ""), status, ""))
                    continue
                okc = [c for c in cands if not lines or max(lines) <= res.count(c)]
                if not okc and not have_src and external(ref) and "/" not in ref:
                    # only an unrelated in-repo file shares the basename; the real file is in a clone
                    rows.append((doc, ln, ref + (":" + spec if spec else ""), "unchecked", ""))
                    continue
                if not okc:
                    status = "line_out_of_range"
                    detail = f"max cited {max(lines)} > {res.count(cands[0])} lines in {os.path.relpath(cands[0], REPO if REPO in cands[0] else src_root)}"
                else:
                    status = "ambiguous" if ambiguous and len(okc) > 1 else "ok"
                    detail = ""
                rows.append((doc, ln, ref + (":" + spec if spec else ""), status, detail))
            for m in MD_LINK_RE.finditer(line):
                target = m.group(1)
                if target.startswith(("http", "mailto:")):
                    continue
                p = os.path.normpath(os.path.join(doc_dir, target))
                rows.append((doc, ln, "link " + target, "ok" if os.path.exists(p) else "missing_file", ""))
    return rows


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docs", nargs="*")
    ap.add_argument("--src-root", default=default_src_root())
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)
    docs = a.docs or sorted(
        [os.path.join(REPO, "research", "phase1", f) for f in os.listdir(os.path.join(REPO, "research", "phase1")) if f.endswith(".md")]
        + [os.path.join(REPO, "research", "phase2-prep", f) for f in os.listdir(os.path.join(REPO, "research", "phase2-prep")) if f.endswith(".md")]
        + [os.path.join(REPO, "research", "phase1", "mod", "hsd_movediag", "readme.md")])
    rows = check(docs, a.src_root)
    bad = [r for r in rows if r[3] in ("missing_file", "line_out_of_range")]
    counts = {}
    for r in rows:
        counts[r[3]] = counts.get(r[3], 0) + 1
    for doc, ln, ref, status, detail in rows:
        if a.verbose or status in ("missing_file", "line_out_of_range"):
            print(f"{status:18s} {os.path.relpath(doc, REPO)}:{ln} {ref} {detail}")
    print("refs:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
