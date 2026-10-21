#!/usr/bin/env python3
"""Automated movement trials over AgentLink: reset the local player on the dedi,
then play a frame-indexed input schedule in the client VM.

Per trial:
  1. run label N on the dedi console (hsd_md_run N); the client label is set by the
     schedule thread itself once the reset has settled (step 3), so the client trial
     window starts after the teleport.
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

# Test field on mp_rr_canyonlands_staging_mu1 found by map_scan.py (m2/map/lanes_wide.json): flat floor at
# z 294.92, about x -14800..-12800 by y 5600..7200, standing-hull clear along +X. Every schedule is run
# with a yaw that makes its motion go along +X (SCHEDULE_YAW). The M1 runs used the spawn pad
# (-11699, 512, 1577.046), which is clear for only about 1100 u.
DEFAULT_ORIGIN = (-14750.0, 6500.0, 294.92)
DEFAULT_YAW = 0.0

# Frame counts assume 144 fps (fps_max in hsd_client.cfg): 72 = 0.5 s, 144 = 1 s, 288 = 2 s, 432 = 3 s.
# On flat ground take-off -> landing is 109 usercmds and press -> take-off 1 (M1), so a jump pressed
# 110 frames after the previous press lands on the very frame it is pressed.
SCHEDULES = {
    # M1 minimal loop: still 0.5 s -> forward 3 s -> release, stop 3 s -> one jump -> land 2 s
    "basic": "wait 72; down forward; wait 432; up forward; wait 432; tap jump; wait 288",
    # E1 ground: start / cruise / stop per input direction and stance
    "e1_walk": "wait 72; down forward; wait 432; up forward; wait 288",
    "e1_sprint": "wait 72; down speed; down forward; wait 432; up forward; up speed; wait 288",
    "e1_crouch": "wait 72; down duck; wait 144; down forward; wait 432; up forward; wait 288; up duck; wait 72",
    "e1_back": "wait 72; down backward; wait 432; up backward; wait 288",
    "e1_side": "wait 72; down moveright; wait 432; up moveright; wait 288",
    "e1_diag": "wait 72; down forward; down moveright; wait 432; up forward; up moveright; wait 288",
    # E1 turning: sprint, then turn right at cl_yawspeed for 1 s while holding forward
    "e1_turn": "wait 72; down speed; down forward; wait 288; down right; wait 144; up right; wait 144; up forward; up speed; wait 288",
    # E2 air: sprint 2 s, jump, then (a) strafe right + turn right, (b) no input, (c) keep forward
    "e2_strafe": "wait 72; down speed; down forward; wait 288; tap jump; wait 4; up forward; up speed; down moveright; down right; wait 100; up right; up moveright; wait 288",
    "e2_noinput": "wait 72; down speed; down forward; wait 288; tap jump; wait 4; up forward; up speed; wait 288",
    "e2_keepfwd": "wait 72; down speed; down forward; wait 288; tap jump; wait 288; up forward; up speed; wait 144",
    # E4 jump: standing jump; hop chains with a fixed delay after landing (frames after the landing frame)
    "e4_stand": "wait 72; tap jump; wait 288",
    "e4_hop0": "wait 72; down speed; down forward; wait 144; tap jump; wait 109; tap jump; wait 109; tap jump; wait 109; tap jump; wait 109; tap jump; wait 110; up forward; up speed; wait 216",
    "e4_hop3": "wait 72; down speed; down forward; wait 144; tap jump; wait 112; tap jump; wait 112; tap jump; wait 112; tap jump; wait 112; tap jump; wait 110; up forward; up speed; wait 216",
    "e4_hop43": "wait 72; down speed; down forward; wait 144; tap jump; wait 152; tap jump; wait 152; tap jump; wait 152; tap jump; wait 152; tap jump; wait 110; up forward; up speed; wait 216",
    # E5 slide: sprint 2 s then hold crouch; slide jump early (0.2 s) and late (0.6 s)
    "e5_slide": "wait 72; down speed; down forward; wait 288; down duck; wait 432; up duck; up forward; up speed; wait 144",
    "e5_slidejump02": "wait 72; down speed; down forward; wait 288; down duck; wait 29; tap jump; wait 288; up duck; up forward; up speed; wait 144",
    "e5_slidejump06": "wait 72; down speed; down forward; wait 288; down duck; wait 86; tap jump; wait 288; up duck; up forward; up speed; wait 144",
}

KEYS = {"forward", "backward", "moveleft", "moveright", "jump", "duck", "speed", "left", "right"}

# Facing so that the schedule's ground motion runs along +X (Source yaw: 0 = +X, 90 = +Y; right = (sin, -cos)).
SCHEDULE_YAW = {"e1_side": 90.0, "e1_back": 180.0, "e1_diag": 45.0}

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
	// The client label starts here, after the reset has settled, so a trial never contains the
	// teleport (the dedi label was set before the reset and is inherited through the cmd join).
	SetConVarInt( "hsd_md_run", $run )
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
	SetConVarInt( "hsd_md_run", 0 )
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
    ap.add_argument("--schedule", default="basic",
                    help=f"comma-separated names ({', '.join(SCHEDULES)}) or one literal step list; "
                         "each schedule runs --trials times in the given order")
    ap.add_argument("--legend", default="gibraltar",
                    help="legend set at session start with Agent_SetLegend (sv_agent_api.nut:739-774); the firing "
                         "range otherwise spawns a random legend per session (M2: Pathfinder, Wraith), and legends "
                         "differ in some class vars (Wraith sprintAcceleration 102 vs 100); '' keeps the spawn legend")
    ap.add_argument("--no-census", action="store_true",
                    help="skip the E0 census at the start (class vars + settings dump on both sides)")
    ap.add_argument("--origin", type=float, nargs=3, default=DEFAULT_ORIGIN)
    ap.add_argument("--yaw", type=float, default=DEFAULT_YAW)
    ap.add_argument("--settle-frames", type=int, default=30)
    ap.add_argument("--settle-timeout", type=int, default=1440)
    ap.add_argument("--fps", type=float, default=144.0, help="planned client frame rate (fps_max in hsd_client.cfg)")
    ap.add_argument("--fps-tol", type=float, default=0.03, help="allowed relative deviation of the measured frame rate")
    ap.add_argument("--warmup", type=int, default=1,
                    help="unscored warm-up trials first (run labels r90+, batches 900+); the first trial "
                         "after a level load hitched in M1 session 3")
    ap.add_argument("--label", default="trials")
    ap.add_argument("--out", default=os.path.join(REPO, "research", "phase2-local", "data"))
    a = ap.parse_args(argv)

    names = a.schedule.split(",") if all(n in SCHEDULES for n in a.schedule.split(",")) else [a.schedule]
    scheds = {n: parse_schedule(SCHEDULES.get(n, n)) for n in names}
    ox, oy, oz = a.origin
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest = {"schema": "hsd-runner/2", "label": a.label, "created": stamp,
                "schedules": {n: {"steps": st, "frames": schedule_frames(st)} for n, st in scheds.items()},
                "origin": list(a.origin), "yaw": a.yaw, "census": not a.no_census, "legend": a.legend or None,
                "legend_reply": None, "trials": []}

    with AgentLink("server", a.game) as server, AgentLink("client", a.game) as client:
        if a.legend:
            r = server.eval('Agent_SetLegend( "me", "%s" )' % a.legend.replace('"', ''))
            manifest["legend_reply"] = r.get("reply", "")
            print("legend:", manifest["legend_reply"])
            if '"ok":true' not in manifest["legend_reply"].replace(" ", ""):
                raise SystemExit("could not set the legend: " + manifest["legend_reply"])
            time.sleep(2.0)
        if not a.no_census:
            # E0 census: client class vars (bridge_classvar_get) and both sides' settings dump.
            for side, line in ((client, "exec user/hsd_e0_classvars"), (client, "hsd_md_dump_now 1"),
                               (server, "hsd_md_dump_now 1")):
                side.cmd(line)
            time.sleep(2.0)
        plan = [(names[0], 90 + w, 900 + w, True) for w in range(a.warmup)]
        k = 0
        for n in names:
            for _ in range(a.trials):
                plan.append((n, a.run_base + k, a.batch_base + k, False))
                k += 1
        for name, run, batch, warm in plan:
            trial = batch
            steps = scheds[name]
            frames = schedule_frames(steps)
            server.cmd(f"hsd_md_run {run}")
            client.cmd("hsd_md_run 0")           # the schedule thread sets the client label once settled
            since = client.info()["logSeq"]
            yaw = SCHEDULE_YAW.get(name, a.yaw)
            reset = server.eval(RESET_SERVER.substitute(ox=ox, oy=oy, oz=oz, yaw=yaw, batch=batch, run=run))
            sched = client.eval(SCHED_CLIENT.substitute(
                steps=", ".join(json.dumps(s) for s in steps), ox=ox, oy=oy, oz=oz,
                settle_frames=a.settle_frames, settle_timeout=a.settle_timeout, trial=trial, run=run))
            lines, gap = wait_for_end(client, since, trial, timeout=(frames + a.settle_timeout) / a.fps * 3 + 30)
            server.cmd("hsd_md_run 0")
            client.cmd("hsd_md_run 0")
            ok, why, fps = check_pacing(lines, frames, a.fps, a.fps_tol)
            manifest["trials"].append({"trial": trial, "run": run, "batch": batch, "schedule": name, "yaw": yaw,
                                       "schedule_frames": frames, "reset": reset.get("reply", ""),
                                       "scheduled": sched.get("reply", ""), "sched_lines": lines,
                                       "log_gap": gap, "measured_fps": fps, "ok": ok, "why": why, "warmup": warm})
            tag = "warm-up " if warm else ""
            print(f"{tag}trial {trial} run r{run} {name}: {'ok' if ok else 'FAILED (' + why + ')'} fps={fps}")
            time.sleep(1.0)

    out = os.path.join(a.out, f"{stamp}_{a.label}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "runner.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    print("wrote", os.path.relpath(os.path.join(out, "runner.json"), REPO))
    return 0 if all(t["ok"] for t in manifest["trials"] if not t["warmup"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
