#!/usr/bin/env python3
"""Copy the newest R5Flowstate SDK log sessions into a dated research folder
and run the hsd_tel report on them. Read-only on the game folder.

  python hsd_collect.py --game "D:\\R5Flowstate" [--server-game "D:\\R5FServer"]
                        [--out research\\data] [--label E1_ground] [--sessions 1]

Looks for (relative to each game root):
  platform/logs/client/<GUID>/   newest N by modification time
  platform/logs/server/<GUID>/   newest N by modification time
  platform/cfg/movementlab/*.csv Movement Lab profiles (copied as-is)
  scriptdump_*                   DevTextBufferDumpToFile output (searched, max depth 3)
The report goes to <out>/<date>_<label>/report/. Standard library only.
"""
import argparse
import datetime
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def newest_dirs(path, n):
    if not os.path.isdir(path):
        return []
    dirs = [os.path.join(path, d) for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    dirs.sort(key=lambda d: max([os.path.getmtime(os.path.join(d, f)) for f in os.listdir(d)] + [os.path.getmtime(d)]),
              reverse=True)
    return dirs[:n]


def find_scriptdumps(root, max_depth=3):
    out = []
    base_depth = root.rstrip(os.sep).count(os.sep)
    for cur, dirs, files in os.walk(root):
        if cur.count(os.sep) - base_depth >= max_depth:
            dirs[:] = []
        if os.path.basename(cur).lower() in ("logs", "paks", "vpk", "stbsp", "audio", "media"):
            dirs[:] = []
        out += [os.path.join(cur, f) for f in files if f.lower().startswith("scriptdump_")]
    return out


def collect(game_roots, out_root, label, sessions, now=None):
    now = now or datetime.datetime.now()
    dest = os.path.join(out_root, now.strftime("%Y%m%d_%H%M%S") + ("_" + label if label else ""))
    copied = []
    for root in game_roots:
        for role in ("client", "server"):
            for d in newest_dirs(os.path.join(root, "platform", "logs", role), sessions):
                target = os.path.join(dest, "platform", "logs", role, os.path.basename(d))
                shutil.copytree(d, target, dirs_exist_ok=True)
                copied.append(target)
        lab = os.path.join(root, "platform", "cfg", "movementlab")
        if os.path.isdir(lab):
            target = os.path.join(dest, "movementlab")
            shutil.copytree(lab, target, dirs_exist_ok=True)
            copied.append(target)
        for f in find_scriptdumps(root):
            os.makedirs(os.path.join(dest, "scriptdump"), exist_ok=True)
            target = os.path.join(dest, "scriptdump", os.path.basename(f))
            shutil.copy2(f, target)
            copied.append(target)
    return dest, copied


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", required=True, help="client game root (folder with platform/)")
    ap.add_argument("--server-game", help="dedi root when the dedi runs from another folder")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "..", "data"))
    ap.add_argument("--label", default="")
    ap.add_argument("--sessions", type=int, default=1, help="newest N log sessions per role")
    ap.add_argument("--no-report", action="store_true")
    a = ap.parse_args(argv)
    roots = [a.game] + ([a.server_game] if a.server_game else [])
    dest, copied = collect(roots, os.path.abspath(a.out), a.label, a.sessions)
    for c in copied:
        print("copied", c)
    if not any(os.sep + "logs" + os.sep in c for c in copied):
        print("no platform/logs/<client|server>/<GUID> sessions found -- were the games started with Developer/-devsdk?")
        return 1
    if a.no_report:
        return 0
    r = subprocess.run([sys.executable, os.path.join(HERE, "hsd_tel.py"), "report",
                        os.path.join(dest, "platform", "logs"), "-o", os.path.join(dest, "report")])
    print("report:", os.path.join(dest, "report", "report.md"))
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
