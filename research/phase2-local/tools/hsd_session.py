#!/usr/bin/env python3
"""One-click game session: launch -> wait for the level -> N automated trials -> quit
-> collect logs -> one data folder with runner.json, platform/logs and report/.

  py -3 hsd_session.py --label M1_loop_s3 --trials 5 --run-base 21 --batch-base 21
  py -3 hsd_session.py --label M1_loop_s4 --trials 1 --run-base 26 --batch-base 26

Pass any extra hsd_trial.py options after '--'. One session at a time: this script
drives the game, so nothing else may control the game or the Unity editor meanwhile.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentlink import AgentLink, AgentLinkError, DEFAULT_GAME  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DATA = os.path.join(REPO, "research", "phase2-local", "data")
PS = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", os.path.join(HERE, "hsd_launch.ps1")]


def wait_alive(game, timeout):
    """Until the local player is alive in the level (both AgentLinks answer)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with AgentLink("client", game, timeout=10) as c, AgentLink("server", game, timeout=10) as s:
                cl = c.eval('entity p = GetLocalClientPlayer(); AgentLink_Reply( IsValid( p ) && IsAlive( p ) ? "alive" : "no" )', check=False)
                sv = s.eval('AgentLink_Reply( GetPlayerArray().len() > 0 && IsAlive( GetPlayerArray()[0] ) ? "alive" : "no" )', check=False)
                if cl.get("reply") == "alive" and sv.get("reply") == "alive":
                    return True
        except (OSError, AgentLinkError, FileNotFoundError):
            pass
        time.sleep(5)
    return False


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--label", required=True)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--run-base", type=int, required=True)
    ap.add_argument("--batch-base", type=int, required=True)
    ap.add_argument("--load-timeout", type=int, default=900)
    ap.add_argument("trial_args", nargs="*", help="extra hsd_trial.py options (after --)")
    a = ap.parse_args(argv)
    py = sys.executable

    t0 = time.time()
    subprocess.run(PS, check=True)                      # stops leftovers, starts dedi, waits host-ready, starts client
    if not wait_alive(a.game, a.load_timeout):
        subprocess.run(PS + ["-Stop"])
        print("level did not load in time"); return 2
    print(f"[session] in level after {time.time() - t0:.0f} s")

    before = set(glob.glob(os.path.join(DATA, f"*_{a.label}")))
    rc = subprocess.run([py, os.path.join(HERE, "hsd_trial.py"), "--game", a.game, "--trials", str(a.trials),
                         "--run-base", str(a.run_base), "--batch-base", str(a.batch_base),
                         "--label", a.label] + a.trial_args).returncode
    runner_dir = sorted(set(glob.glob(os.path.join(DATA, f"*_{a.label}"))) - before)

    try:
        with AgentLink("client", a.game, timeout=10) as c:
            c.cmd("quit")
    except (OSError, AgentLinkError):
        pass
    time.sleep(8)
    subprocess.run(PS + ["-Stop"])

    subprocess.run([py, os.path.join(REPO, "research", "phase2-prep", "tools", "hsd_collect.py"), "--game", a.game,
                    "--out", DATA, "--label", a.label + "_game"], check=True)
    game_dir = sorted(glob.glob(os.path.join(DATA, f"*_{a.label}_game")))[-1]
    final = game_dir[: -len("_game")]
    if runner_dir:
        shutil.move(os.path.join(runner_dir[-1], "runner.json"), os.path.join(game_dir, "runner.json"))
        os.rmdir(runner_dir[-1])
    os.rename(game_dir, final)
    print(f"[session] {os.path.relpath(final, REPO)} (trials rc={rc}, {time.time() - t0:.0f} s total)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
