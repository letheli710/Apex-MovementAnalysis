"""Annotate Ghidra-decompiled TF2 C files with ConVar and .set schema names.

- `*(float *)(DAT_<ptr> + 0x58)` -> `CV(<name>).f`, `+ 0x5c` -> `CV(<name>).i`
  Code reads a ConVar through the parent pointer stored at object + 0x38 (checked on
  sv_friction and sv_maxspeed in server.dll); the parent keeps the float value at
  +0x58 and the int value at +0x5c.
- other references to a ConVar object are tagged with /* cv:<name> */
Writes annotated copies next to the input directory (<dir>-ann).

Usage: python -I annotate.py <convar-defaults.tsv> <dll name> <decomp dir> [<decomp dir> ...]
"""
import csv
import re
import sys
from pathlib import Path


def main():
    table, dll = sys.argv[1], sys.argv[2]
    objs = {}
    with open(table, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r["dll"] == dll and r.get("object"):
                objs[f'{int(r["object"], 16) + 0x38:x}'] = r["convar"]
    val = re.compile(r"\*\((float|int|uint|undefined4) \*\)\(DAT_([0-9a-f]+) \+ 0x(58|5c)\)")
    ref = re.compile(r"DAT_([0-9a-f]+)")
    for d in sys.argv[3:]:
        src = Path(d)
        dst = src.with_name(src.name + "-ann")
        dst.mkdir(exist_ok=True)
        for p in src.glob("*.c"):
            text = p.read_text(encoding="utf-8")

            def v(m):
                name = objs.get(m.group(2))
                return f"CV({name}).{'f' if m.group(3) == '58' else 'i'}" if name else m.group(0)

            text = val.sub(v, text)
            text = ref.sub(lambda m: m.group(0) + (f"/* cv:{objs[m.group(1)]} */" if m.group(1) in objs else ""), text)
            (dst / p.name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
