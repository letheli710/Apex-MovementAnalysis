"""T0 inventory: game binaries (size + sha256), VPK list, and a location map of .set/.nut files.

Usage: python -I inventory.py
Writes binaries.csv, vpks.csv, scripts-map.csv next to this file.
Needs ../local/vpk-lists/*.txt (tf2vpk list output) for the VPK script map.
"""
import csv
import hashlib
import os
import subprocess
from pathlib import Path

GAME = Path(r"C:\SteamLibrary\steamapps\common\Titanfall2")
HERE = Path(__file__).resolve().parent
TF2VPK = Path(r"C:\Tools\tf2vpk\tf2vpk.exe")
LISTS = HERE.parent / "local" / "vpk-lists"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def binaries():
    rows = []
    for d in (GAME, GAME / "bin" / "x64_retail", GAME / "R2Northstar", GAME / "R2Northstar" / "plugins"):
        for p in sorted(d.iterdir()):
            if p.suffix.lower() in (".dll", ".exe"):
                rows.append([str(p.relative_to(GAME)), p.stat().st_size, sha256(p)])
    with open(HERE / "binaries.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "size", "sha256"])
        w.writerows(rows)


def vpks():
    rows = []
    LISTS.mkdir(parents=True, exist_ok=True)
    for p in sorted((GAME / "vpk").glob("englishclient_*_dir.vpk")):
        name = p.name[len("english"):-len("_dir.vpk")]
        out = LISTS / (name + ".txt")
        if not out.exists():
            res = subprocess.run([str(TF2VPK), "list", "--vpk-dir", str(GAME / "vpk"), name],
                                 capture_output=True, text=True, check=True)
            out.write_text(res.stdout)
        files = out.read_text().splitlines()
        rows.append([name, len(files),
                     sum(f.endswith(".set") for f in files),
                     sum(f.endswith((".nut", ".gnut")) for f in files)])
    with open(HERE / "vpks.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["vpk", "files", "set_files", "nut_files"])
        w.writerows(rows)


def scripts_map():
    """One row per distinct .set/.nut path: which VPKs contain it, and whether a Northstar mod overrides it."""
    where = {}
    for lst in sorted(LISTS.glob("*.txt")):
        for line in lst.read_text().splitlines():
            if line.endswith((".set", ".nut", ".gnut")):
                where.setdefault(line, []).append(lst.stem)
    mods = GAME / "R2Northstar" / "mods"
    override = {}
    for mod in mods.iterdir():
        for root in (mod / "mod", mod / "keyvalues"):
            if root.is_dir():
                for p in root.rglob("*"):
                    if p.suffix in (".set", ".nut", ".gnut"):
                        override.setdefault(p.relative_to(root).as_posix(), []).append(mod.name)
    with open(HERE / "scripts-map.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "dir", "vpk_count", "first_vpk", "northstar_override"])
        for path in sorted(set(where) | set(override)):
            v = where.get(path, [])
            w.writerow([path, os.path.dirname(path), len(v), v[0] if v else "",
                        ";".join(override.get(path, []))])


if __name__ == "__main__":
    binaries()
    vpks()
    scripts_map()
