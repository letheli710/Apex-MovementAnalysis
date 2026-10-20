#!/usr/bin/env python3
"""Automated movement trials over AgentLink: reset the local player on the dedi,
then play a frame-indexed input schedule in the client VM.

Per trial:
  1. run label N on both consoles (hsd_md_run N; tags every [HSD-MD] line).
  2. dedi EVAL: the fs_1v1 teleport recipe (SetVelocity 0, SettleStance, SetOrigin,
     SetAngles, SetVelocity 0, PlantOnGround, SnapEyeAngles, SnapFeetToEyes;
     s21-platform/scripts/vscripts/gamemodes/fs_1v1/_1v1_match.nut:2087-2103), and a
     [HSD-RESET] line with the reset batch number.
  3. client EVAL: a thread that waits until the client-predicted state has settled at
     the target (script SetOrigin is not predicted; the client adopts the server state,
     s21-r5sdk/src/game/client/pred_authority.cpp:101-107), then sends +/- console
     button commands through player.ClientCommand on counted script frames, logging
     each edge as [HSD-SCHED] with FrameCount(), PlatformTime() and Time().
  4. waits for the schedule's 'end' line in the client log ring, then label 0.

The schedule language (one step per ';'):  wait <frames> | down <key> | up <key> |
tap <key>  (down now, up on the next frame).  Keys: forward back moveleft moveright
jump duck speed (console +<key>).

  py -3 hsd_trial.py --trials 5 --run-base 11 --label M1_loop --schedule basic
"""
import argparse
import datetime
import json
import os
import string
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agentlink import AgentLink, DEFAULT_GAME  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

# Firing range spawn on mp_rr_canyonlands_staging_mu1; +X is clear for > 1000 u (T0).
DEFAULT_ORIGIN = (-11699.0, 512.0, 1577.046)
DEFAULT_YAW = 0.0

SCHEDULES = {
    # M1 minimal loop: still 0.5 s -> forward 3 s -> release, stop 3 s -> one jump -> land 2 s  (144 fps frames)
    "basic": "wait 72; down forward; wait 432; up forward; wait 432; tap jump; wait 288",
}

KEYS = {"forward", "back", "moveleft", "moveright", "jump", "duck", "speed"}

RESET_SERVER = string.Template(r'''
entity p = GetPlayerArray()[0]
vector o = <$ox, $oy, $oz>
vector a = <0, $yaw, 0>
p.SetVelocity( <0, 0, 0> )
p.SettleStance()
p.SetOrigin( o )
p.SetAngles( a )
p.SetVelocity( <0, 0, 0> )
p.PlantOnGround()
p.SnapEyeAngles( a )
p.SnapFeetToEyes()
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
string wn = w == null ? "none" : w.GetWeaponClassName()
string s = "[HSD-RESET] ver=1 batch=$batch run=$run ent=" + p.GetEntIndex() + " o=" + p.GetOrigin().x + "," + p.GetOrigin().y + "," + p.GetOrigin().z + " vel=" + p.GetVelocity().x + "," + p.GetVelocity().y + "," + p.GetVelocity().z + " yaw=" + p.EyeAngles().y + " ground=" + ( p.IsOnGround() ? 1 : 0 ) + " slide=" + ( p.IsSliding() ? 1 : 0 ) + " weapon=" + wn + " t=" + Time()
printt( s )
AgentLink_Reply( s )
''')

SCHED_CLIENT = string.Template(r'''
array<string> steps = [ $steps ]
void functionref() f = void function() : ( steps ) {
	entity p = GetLocalClientPlayer()
	vector target = <$ox, $oy, $oz>
	int settled = 0
	int waited = 0
	while ( settled < $settle_frames )
	{
		WaitFrame()
		waited++
		if ( !IsValid( p ) || !IsAlive( p ) )
			return
		vector d = p.GetOrigin() - target
		vector v = p.GetVelocity()
		if ( fabs( d.x ) < 1.0 && fabs( d.y ) < 1.0 && fabs( d.z ) < 2.0 && Length( v ) < 1.0 && p.IsOnGround() )
			settled++
		else
			settled = 0
		if ( waited > $settle_timeout )
		{
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=settle_timeout frame=0 fc=" + FrameCount() + " o=" + p.GetOrigin() )
			return
		}
	}
	int f0 = FrameCount()
	printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=start frame=0 fc=" + f0 + " pt=" + PlatformTime() + " t=" + Time() + " o=" + p.GetOrigin().x + "," + p.GetOrigin().y + "," + p.GetOrigin().z + " yaw=" + p.EyeAngles().y + " settle_frames=" + waited )
	foreach ( string st in steps )
	{
		array<string> parts = split( st, " " )
		string verb = parts[0]
		if ( verb == "wait" )
		{
			int n = parts[1].tointeger()
			for ( int i = 0; i < n; i++ )
				WaitFrame()
			continue
		}
		string key = parts[1]
		if ( verb == "down" || verb == "tap" )
		{
			p.ClientCommand( "+" + key )
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=down key=" + key + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() )
		}
		if ( verb == "tap" )
			WaitFrame()
		if ( verb == "up" || verb == "tap" )
		{
			p.ClientCommand( "-" + key )
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=up key=" + key + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() )
		}
	}
	printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=end frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() + " o=" + p.GetOrigin().x + "," + p.GetOrigin().y + "," + p.GetOrigin().z )
}
thread f()
AgentLink_Reply( "scheduled trial=$trial fc=" + FrameCount() )
''')


def parse_schedule(spec):
    steps = [s.strip() for s in spec.split(";") if s.strip()]
    for s in steps:
        verb, _, arg = s.partition(" ")
        if verb == "wait":
            if not arg.isdigit():
                raise ValueError(f"bad wait: {s!r}")
        elif verb in ("down", "up", "tap"):
            if arg not in KEYS:
                raise ValueError(f"unknown key in {s!r}")
        else:
            raise ValueError(f"unknown step {s!r}")
    return steps


def schedule_frames(steps):
    n = 0
    for s in steps:
        verb, _, arg = s.partition(" ")
        n += int(arg) if verb == "wait" else (1 if verb == "tap" else 0)
    return n


def _field(line, key):
    for tok in line.split():
        if tok.startswith(key + "="):
            return tok[len(key) + 1:]
    return None


def check_pacing(lines, frames, fps, tol):
    """A frame-indexed schedule only means the planned durations at the planned frame rate.
    Returns (ok, reason, measured fps from PlatformTime between 'start' and 'end')."""
    start = next((l for l in lines if "edge=start" in l), None)
    end = next((l for l in lines if "edge=end" in l), None)
    if not start or not end:
        return False, "no start/end edge (settle timeout?)", None
    n = int(_field(end, "frame")) - int(_field(start, "frame"))
    if n != frames:
        return False, f"schedule ran {n} frames, planned {frames}", None
    dt = float(_field(end, "pt")) - float(_field(start, "pt"))
    measured = round(n / dt, 2) if dt > 0 else None
    if not measured or abs(measured / fps - 1) > tol:
        return False, f"frame rate {measured} outside {fps} +/- {tol:.0%}", measured
    return True, "", measured


def wait_for_end(client, since, trial, timeout):
    """Collect this trial's [HSD-SCHED] lines from the client log ring until 'end'."""
    lines, nxt, deadline = [], since, time.time() + timeout
    tag = f"trial={trial} "
    while time.time() < deadline:
        r = client.log(nxt, 500)
        nxt = r.get("next", nxt)
        for e in r.get("lines", []):
            t = e.get("text", "")
            if "[HSD-SCHED]" in t and tag in t:
                lines.append(t[t.index("[HSD-SCHED]"):])
                if "edge=end" in t or "edge=settle_timeout" in t:
                    return lines, r.get("gap", False)
        time.sleep(0.25)
    raise TimeoutError(f"trial {trial}: no end line after {timeout} s")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=DEFAULT_GAME)
    ap.add_argument("--trials", type=int, default=5)
    ap.add_argument("--run-base", type=int, default=11, help="run label of the first trial; +1 per trial")
    ap.add_argument("--batch-base", type=int, default=1, help="reset batch number of the first trial")
    ap.add_argument("--schedule", default="basic", help=f"name ({', '.join(SCHEDULES)}) or a literal step list")
    ap.add_argument("--origin", type=float, nargs=3, default=DEFAULT_ORIGIN)
    ap.add_argument("--yaw", type=float, default=DEFAULT_YAW)
    ap.add_argument("--settle-frames", type=int, default=30)
    ap.add_argument("--settle-timeout", type=int, default=1440)
    ap.add_argument("--fps", type=float, default=144.0, help="planned client frame rate (fps_max in hsd_client.cfg)")
    ap.add_argument("--fps-tol", type=float, default=0.03, help="allowed relative deviation of the measured frame rate")
    ap.add_argument("--label", default="trials")
    ap.add_argument("--out", default=os.path.join(REPO, "research", "phase2-local", "data"))
    a = ap.parse_args(argv)

    steps = parse_schedule(SCHEDULES.get(a.schedule, a.schedule))
    frames = schedule_frames(steps)
    ox, oy, oz = a.origin
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest = {"schema": "hsd-runner/1", "label": a.label, "created": stamp, "schedule": steps,
                "schedule_frames": frames, "origin": list(a.origin), "yaw": a.yaw, "trials": []}

    with AgentLink("server", a.game) as server, AgentLink("client", a.game) as client:
        for k in range(a.trials):
            run, batch, trial = a.run_base + k, a.batch_base + k, a.batch_base + k
            server.cmd(f"hsd_md_run {run}")
            client.cmd(f"hsd_md_run {run}")
            since = client.info()["logSeq"]
            reset = server.eval(RESET_SERVER.substitute(ox=ox, oy=oy, oz=oz, yaw=a.yaw, batch=batch, run=run))
            sched = client.eval(SCHED_CLIENT.substitute(
                steps=", ".join(json.dumps(s) for s in steps), ox=ox, oy=oy, oz=oz,
                settle_frames=a.settle_frames, settle_timeout=a.settle_timeout, trial=trial, run=run))
            lines, gap = wait_for_end(client, since, trial, timeout=(frames + a.settle_timeout) / a.fps * 3 + 30)
            server.cmd("hsd_md_run 0")
            client.cmd("hsd_md_run 0")
            ok, why, fps = check_pacing(lines, frames, a.fps, a.fps_tol)
            manifest["trials"].append({"trial": trial, "run": run, "batch": batch, "reset": reset.get("reply", ""),
                                       "scheduled": sched.get("reply", ""), "sched_lines": lines,
                                       "log_gap": gap, "measured_fps": fps, "ok": ok, "why": why})
            print(f"trial {trial} run r{run}: {'ok' if ok else 'FAILED (' + why + ')'} fps={fps}")
            time.sleep(1.0)

    out = os.path.join(a.out, f"{stamp}_{a.label}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "runner.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    print("wrote", os.path.relpath(os.path.join(out, "runner.json"), REPO))
    return 0 if all(t["ok"] for t in manifest["trials"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
