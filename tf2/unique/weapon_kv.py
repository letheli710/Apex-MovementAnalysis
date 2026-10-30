"""Print the base WeaponData values and each Mod's overrides for TF2 weapon .txt files.

Usage: python -I weapon_kv.py <weapons_dir> <out_csv> <weapon> [weapon ...]
Rows: weapon, scope (base / mod:<name>), key, value.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "static-values"))
from set_resolve import parse_block, tokenize  # noqa: E402


def rows_for(path):
    items, _ = parse_block(tokenize(path.read_text(encoding="utf-8", errors="replace")), 0)
    data = next((v for k, v in items if k == "WeaponData" and isinstance(v, list)), [])
    out = []
    for k, v in data:
        if k == "Mods" and isinstance(v, list):
            for mod, body in v:
                for mk, mv in body if isinstance(body, list) else []:
                    if not isinstance(mv, list):
                        out.append((f"mod:{mod}", mk, mv))
        elif k in ("MP_BASE", "SP_BASE") and isinstance(v, list):
            for bk, bv in v:
                if not isinstance(bv, list):
                    out.append((k.lower(), bk, bv))
        elif not isinstance(v, list):
            out.append(("base", k, v))
    return out


def main():
    wdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["weapon", "scope", "key", "value"])
        for name in sys.argv[3:]:
            for scope, k, v in rows_for(wdir / (name + ".txt")):
                w.writerow([name, scope, k, v])


if __name__ == "__main__":
    main()
