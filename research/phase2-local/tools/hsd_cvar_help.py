#!/usr/bin/env python3
"""Run `help <cvar>` for a list of ConVars on the live client and dedi consoles.

Starts the game the way hsd_session.py does (hsd_launch.ps1, firing range),
waits until the local player is alive, sends `help <name>` to both AgentLinks,
saves every raw reply as JSON, then quits and stops the game.

  py -3 hsd_cvar_help.py --names ../static-values/ghidra/convar-names.txt --out <dir>

Output: <out>/cvar_help.json  {"client": {name: help reply}, "server": {...},
        "client_script": {name: GetConVarString value}, "server_script": {...}}
The client is r5apex_dx12.exe (S21), the dedi r5apex_ds.exe (S3), so a name can
exist on one side only. Standard library only.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentlink import AgentLink, AgentLinkError, DEFAULT_GAME  # noqa: E402
from hsd_session import PS, wait_alive  # noqa: E402


def read_names(path):
    names = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            s = line.split("#", 1)[0].strip()
            if s:
                names.append(s)
    return names


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--names", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--load-timeout", type=int, default=900)
    a = ap.parse_args(argv)
    names = read_names(a.names)
    os.makedirs(a.out, exist_ok=True)

    subprocess.run(PS, check=True)
    try:
        if not wait_alive(a.game, a.load_timeout):
            print("level did not load in time")
            return 2
        time.sleep(10)
        # The client does not echo `help` output through AgentLink (only the dedi
        # does), so also read each value from script with GetConVarString.
        result = {"names": names, "client": {}, "server": {}, "client_script": {}, "server_script": {}}
        for side in ("client", "server"):
            with AgentLink(side, a.game, timeout=30) as link:
                for n in names:
                    result[side][n] = link.cmd(f"help {n}")
                    code = (f'try {{ AgentLink_Reply( GetConVarString( "{n}" ) ) }} '
                            f'catch ( e ) {{ AgentLink_Reply( "ERR " + e ) }}')
                    result[side + "_script"][n] = link.eval(code, check=False).get("reply")
        with open(os.path.join(a.out, "cvar_help.json"), "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=1, ensure_ascii=False)
        print(f"saved {len(names)} names x 2 sides to {a.out}")
    finally:
        try:
            with AgentLink("client", a.game, timeout=10) as c:
                c.cmd("quit")
        except (OSError, AgentLinkError):
            pass
        time.sleep(8)
        subprocess.run(PS + ["-Stop"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
