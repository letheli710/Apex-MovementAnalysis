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
tap <key>  (down now, up on the next frame) | set <cvar> <value>.  Keys: forward backward moveleft
moveright jump duck speed left right lookup lookdown offhand1 offhand4 (console +<key>).
View turns use +left/+right/+lookup/+lookdown at a constant rate set with 'set cl_yawspeed N' /
'set cl_pitchspeed N' (only VIEW_CVARS). A 'set' takes effect at the start of the trial: the runner sends it to the
client console before the schedule starts (player.ClientCommand would forward it to the server, M4b finding) and
restores the session value after the trial; the schedule thread only logs it.

  py -3 hsd_trial.py --trials 5 --run-base 11 --label M1_loop --schedule basic
"""
import argparse
import re
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
    # ---- M3 (E3 tap strafe / lurch): sprint 1 s on lane B, jump, then K frames after the jump press
    #      release W and press a direction; K is in exact frames (waitf) at any frame rate.
    "e3_right_k1": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k2": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 2; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k3": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 3; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k5": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 5; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k8": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 8; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k12": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 12; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k18": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 18; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k25": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 25; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k35": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 35; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k50": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 50; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k70": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 70; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k90": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 90; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k40": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 40; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k45": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 45; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k55": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 55; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k60": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 60; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_k65": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 65; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_back_k3": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 3; up forward; up speed; down backward; wait 0.9s; up backward; wait 0.5s",
    "e3_wtap_k3": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; waitf 2; tap forward; wait 0.9s; wait 0.5s",
    "e3_back_k12": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 12; up forward; up speed; down backward; wait 0.9s; up backward; wait 0.5s",
    "e3_wtap_k12": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; waitf 11; tap forward; wait 0.9s; wait 0.5s",
    "e3_back_k35": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 35; up forward; up speed; down backward; wait 0.9s; up backward; wait 0.5s",
    "e3_wtap_k35": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; waitf 34; tap forward; wait 0.9s; wait 0.5s",
    "e3_right_walk_k5": "wait 72; down forward; wait 1.0s; tap jump; waitf 5; up forward; down moveright; wait 0.9s; up moveright; wait 0.5s",
    "e3_right_slide350_k5": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; waitf 5; up duck; up forward; up speed; down moveright; wait 0.9s; up moveright; wait 0.5s",
    # ---- M3 (E6 climb / wall bounce, E7 mantle) on lane A against the test wall (face x ~ -13706):
    #      sprint 1.2 s, jump into the wall (contact ~0.28 s later), then climb with W held.
    "e6_climb": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 2.5s; up forward; up speed; wait 2.5s",
    "e6_bounce_none_15": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; tap jump; wait 2.5s",
    "e6_bounce_back_15": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; down backward; tap jump; wait 1.0s; up backward; wait 1.5s",
    "e6_bounce_side_15": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; down moveright; tap jump; wait 1.0s; up moveright; wait 1.5s",
    "e6_bounce_none_40": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.68s; up forward; up speed; tap jump; wait 2.5s",
    "e6_bounce_back_40": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.68s; up forward; up speed; down backward; tap jump; wait 1.0s; up backward; wait 1.5s",
    "e6_bounce_side_40": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.68s; up forward; up speed; down moveright; tap jump; wait 1.0s; up moveright; wait 1.5s",
    # E7: the climb ends (END_WALLRUN) ~161 frames (144 fps) after the jump press and the mantle follows;
    # the SDK mantle-boost sweet spot opens in the last ~0.10-0.13 s of the mantle (mantle_boost.cpp:44-46).
    # Sweep the press from 130 to 178 frames after the jump press: jump only (mantle boost, S21 input 1)
    # and jump + crouch on the next frame (classic superglide input).
    "e7_mb_f130": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 129; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f130": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 129; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f133": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 132; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f133": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 132; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f136": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 135; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f136": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 135; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f139": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 138; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f139": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 138; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f142": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 141; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f142": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 141; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f145": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 144; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f145": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 144; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f148": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 147; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f148": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 147; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f151": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 150; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f151": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 150; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f154": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 153; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f154": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 153; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f157": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 156; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f157": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 156; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f160": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 159; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f160": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 159; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f163": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 162; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f163": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 162; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f166": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 165; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f166": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 165; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f169": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 168; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f169": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 168; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f172": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 171; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f172": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 171; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f175": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 174; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f175": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 174; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_mb_f178": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 177; tap jump; wait 1.5s; up forward; up speed; wait 1.0s",
    "e7_sg_f178": "wait 72; down speed; down forward; wait 1.2s; tap jump; waitf 177; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s",
    # ---- M3 landing chains: slide-jump at 350 into hops (lane B); climb over the wall and drop 232 u (lane A)
    "e8_fast_hops": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; wait 109; tap jump; wait 109; tap jump; wait 109; tap jump; wait 110; up forward; up speed; wait 1.0s",
    "e8_slide_chain": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; wait 109; wait 0.5s; tap jump; wait 109; wait 0.5s; up duck; up forward; up speed; wait 1.0s",
    # ---- M4 legend abilities (session per legend; --kit equips the abilities; abilities refilled at every reset)
    # Octane stim on lane C: sprint 1 s, stim, sprint 3 s, release, stand 4 s (msc decay is logged per usercmd)
    "m4_stim_sprint": "wait 72; down speed; down forward; wait 1.0s; tap offhand1; wait 3.0s; up forward; up speed; wait 4.0s",
    "m4_ctrl_sprint": "wait 72; down speed; down forward; wait 1.0s; wait 3.0s; up forward; up speed; wait 4.0s",
    "m4_stim_walk": "wait 72; tap offhand1; wait 0.3s; down forward; wait 3.0s; up forward; wait 3.0s",
    "m4_stim_air": "wait 72; down speed; down forward; wait 1.0s; tap offhand1; wait 1.0s; tap jump; waitf 3; up forward; up speed; down moveright; wait 0.8s; up moveright; wait 2.0s",
    "m4_ctrl_air": "wait 72; down speed; down forward; wait 1.0s; wait 1.0s; tap jump; waitf 3; up forward; up speed; down moveright; wait 0.8s; up moveright; wait 2.0s",
    # Octane jump pad (spawned by the reset 300 u ahead on lane C): walk / sprint / crouch-walk onto it
    "m4_pad_walk": "wait 72; down forward; wait 2.5s; up forward; wait 3.5s",
    "m4_pad_sprint": "wait 72; down speed; down forward; wait 1.5s; up forward; up speed; wait 4.0s",
    "m4_pad_crouch": "wait 72; down duck; wait 0.5s; down forward; wait 4.0s; up forward; up duck; wait 3.0s",
    "m4_pad_jumpin": "wait 72; down speed; down forward; wait 0.8s; tap jump; wait 1.0s; up forward; up speed; wait 4.0s",
    # Horizon gravity lift (spawned by the reset 120 u ahead): walk in and ride; jump out early; strafe inside
    "m4_lift_ride": "wait 72; down forward; wait 0.6s; up forward; wait 7.0s; wait 3.0s",
    "m4_lift_jumpout": "wait 72; down forward; wait 0.6s; up forward; wait 1.5s; tap jump; wait 4.0s; wait 5.0s",
    "m4_lift_strafe": "wait 72; down forward; wait 0.6s; up forward; wait 1.0s; down moveright; wait 1.0s; up moveright; wait 5.0s; wait 4.0s",
    # Pathfinder grapple on lane A toward the test wall (394 u ahead): fire and hang on; fire then jump-release
    "m4_grapple_hold": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
    "m4_grapple_jump": "wait 72; tap offhand1; wait 0.6s; tap jump; wait 4.0s",
    "m4_grapple_fwd": "wait 72; tap offhand1; down forward; wait 3.0s; up forward; wait 2.5s",
    # M4b view control acceptance: constant-rate turns, checked per usercmd in MOVE-TRACE
    "m4b_view_yaw": "wait 72; set cl_yawspeed 90; down right; wait 1.0s; up right; wait 0.5s; down left; wait 0.5s; up left; wait 0.5s",
    "m4b_view_pitch": "wait 72; set cl_pitchspeed 45; down lookup; wait 0.5s; up lookup; wait 0.3s; down lookdown; wait 1.0s; up lookdown; wait 0.5s",
    "m4b_view_run": "wait 72; set cl_yawspeed 90; down speed; down forward; wait 0.8s; down right; wait 1.0s; up right; wait 0.5s; up forward; up speed; wait 0.8s",
    # M4b grapple swing: anchor offset sideways (start 150 u left of the wall centre line, aim 20 deg right of the
    # wall normal so the hook lands near the centre), then turning during the pull and a jump release
    "m4b_swing_side": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
    "m4b_swing_turn": "wait 72; set cl_yawspeed 90; tap offhand1; wait 0.45s; down right; wait 0.6s; up right; wait 2.0s; wait 2.5s",
    "m4b_swing_turn_w": "wait 72; set cl_yawspeed 90; tap offhand1; down forward; wait 0.45s; down right; wait 0.6s; up right; wait 2.0s; up forward; wait 2.5s",
    "m4b_swing_jump": "wait 72; tap offhand1; wait 0.8s; tap jump; wait 3.0s",
    "m4b_swing_turn_jump": "wait 72; set cl_yawspeed 90; tap offhand1; wait 0.45s; down right; wait 0.35s; tap jump; wait 0.25s; up right; wait 3.0s",
    # M4b swing round 2: speed across the rope at attach. Run along the wall (+Y), jump, turn ~70 deg toward the wall
    # in the air (no move keys, so the velocity keeps its direction), then grapple; _w holds forward during the pull
    "m4b_swing_cross": "wait 72; set cl_yawspeed 700; down speed; down forward; wait 1.0s; tap jump; up forward; up speed; down right; waitf 12; up right; tap offhand1; wait 3.0s; wait 2.0s",
    "m4b_swing_cross_w": "wait 72; set cl_yawspeed 700; down speed; down forward; wait 1.0s; tap jump; up forward; up speed; down right; waitf 12; up right; tap offhand1; down forward; wait 3.0s; up forward; wait 2.0s",
    "m4b_swing_cross_walk": "wait 72; set cl_yawspeed 700; down forward; wait 1.0s; tap jump; up forward; down right; waitf 12; up right; tap offhand1; wait 3.0s; wait 2.0s",
    # M4b re-jump after a jump-pad landing (3 frames after touchdown), without and with forward held
    "m4b_pad_rejump": "wait 72; down speed; down forward; wait 1.5s; up forward; up speed; waitair; waitland; waitf 3; tap jump; wait 3.0s",
    "m4b_pad_rejump_w": "wait 72; down speed; down forward; wait 1.5s; up speed; waitair; waitland; waitf 3; tap jump; wait 1.5s; up forward; wait 1.5s",
    # grapple variants: distance to the wall (244 u near, 694 u far) and pitch (0, -20)
    "m4_grapple_near": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
    "m4_grapple_far": "wait 72; tap offhand1; wait 3.5s; wait 2.5s",
    "m4_grapple_p0": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
    "m4_grapple_p20": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
    # Priority 2: Valkyrie jets (passive; hold +jump while airborne) and Revenant shadow pounce (charge +offhand1)
    "m4_valk_jets": "wait 72; tap jump; waitair; wait 0.2s; down jump; wait 2.0s; up jump; wait 3.0s",
    "m4_valk_jets_fwd": "wait 72; tap jump; waitair; wait 0.2s; down jump; down forward; wait 2.0s; up jump; up forward; wait 3.0s",
    "m4_valk_ctrl": "wait 72; tap jump; waitair; wait 0.2s; wait 2.0s; wait 3.0s",
    "m4_pounce_c0": "wait 72; tap offhand1; wait 4.0s",
    "m4_pounce_c06": "wait 72; down offhand1; wait 0.6s; up offhand1; wait 4.0s",
    "m4_pounce_c13": "wait 72; down offhand1; wait 1.3s; up offhand1; wait 4.0s",
    # ---- visible-ground cross-checks on the spawn pad (defined; not scheduled for now)
    #      and e4_stand, and a shorter slide that stays on the pad
    "x_pad_sprint": "wait 72; down speed; down forward; wait 432; up forward; up speed; wait 288",
    "x_pad_stand": "wait 72; tap jump; wait 288",
    "x_pad_slide": "wait 72; down speed; down forward; wait 1.5s; down duck; wait 2.0s; up duck; up forward; up speed; wait 1.0s",
    # M3 follow-up: hop chains above 299 u/s (slide jump at 350), each re-jump D frames after the landing frame
    "e8_hop350_d0": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; tap jump; waitair; waitland; tap jump; waitair; waitland; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_hop350_d1": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; waitf 1; tap jump; waitair; waitland; waitf 1; tap jump; waitair; waitland; waitf 1; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_hop350_d2": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; waitf 2; tap jump; waitair; waitland; waitf 2; tap jump; waitair; waitland; waitf 2; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_hop350_d3": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; waitf 3; tap jump; waitair; waitland; waitf 3; tap jump; waitair; waitland; waitf 3; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_hop350_d5": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; waitf 5; tap jump; waitair; waitland; waitf 5; tap jump; waitair; waitland; waitf 5; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_hop350_d10": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; up duck; waitair; waitland; waitf 10; tap jump; waitair; waitland; waitf 10; tap jump; waitair; waitland; waitf 10; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.5s",
    "e8_drop_land": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 4.0s; up forward; up speed; wait 1.5s",
}

KEYS = {"forward", "backward", "moveleft", "moveright", "jump", "duck", "speed", "left", "right", "lookup", "lookdown",
        "offhand1", "offhand4"}
# Client cvars a schedule may change with 'set' (constant-rate view turns, M4b).
VIEW_CVARS = ("cl_yawspeed", "cl_pitchspeed")

# View pitch per schedule (Source: + = down). Grapple trials aim slightly up at the test wall.
SCHEDULE_PITCH = {"m4_grapple_hold": -10.0, "m4_grapple_jump": -10.0, "m4_grapple_fwd": -10.0,
                  "m4_grapple_near": -10.0, "m4_grapple_far": -10.0, "m4_grapple_p0": 0.0, "m4_grapple_p20": -20.0,
                  "m4b_swing_side": -10.0, "m4b_swing_turn": -10.0, "m4b_swing_turn_w": -10.0, "m4b_swing_jump": -10.0,
                  "m4b_swing_turn_jump": -10.0, "m4b_swing_cross": -10.0, "m4b_swing_cross_w": -10.0,
                  "m4b_swing_cross_walk": -10.0}

# Server snippets run inside the reset (after the teleport, inside try/catch) for prop-based abilities.
# Every spawned prop gets the script name hsd_test_geo; the previous one is removed first.
_CLEAR_GEO = 'foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo_m4" ) ) e.Destroy()\n'
SCHEDULE_PRE = {
    ("m4_pad_", "m4b_pad_"): _CLEAR_GEO + 'entity pad = JumpPad_CreateAtLocation( o + <300, 0, 0>, <0, 0, 0>, p, true )\n'
               'if ( IsValid( pad ) ) pad.SetScriptName( "hsd_test_geo_m4" )\npre = " pad=" + IsValid( pad )\n',
    # view trials run on lane C after pad trials: remove a pad left from an earlier trial (M4b: one was run into)
    "m4b_view": _CLEAR_GEO + 'pre = " geo=cleared"\n',
    "m4_lift_": 'thread SpaceElevator_PropDeploy( p, o + <120, 0, 0>, <0, 0, 0>, null )\npre = " lift=deployed"\n',
}

# Facing so that the schedule's ground motion runs along +X (Source yaw: 0 = +X, 90 = +Y; right = (sin, -cos)).
SCHEDULE_YAW = {"e1_side": 90.0, "e1_back": 180.0, "e1_diag": 45.0,
                "m4b_swing_side": 20.0, "m4b_swing_turn": 20.0, "m4b_swing_turn_w": 20.0, "m4b_swing_jump": 20.0,
                "m4b_swing_turn_jump": 20.0, "m4b_swing_cross": 90.0, "m4b_swing_cross_w": 90.0, "m4b_swing_cross_walk": 90.0}

# Start positions per schedule prefix (M3). Lane A faces the test wall (test_geometry.py: rock face at
# x ~ -13706, y 6380..6620, top ~ +232 u); lane B is the open part of the field at y 5900.
LANE_A = (-14100.0, 6500.0, 294.92)
LANE_B = (-14200.0, 5900.0, 294.92)
# Lane C: y 6800 is flat from x -14825 to -12475 (m3/map/field_fine.json) and 81 u clear of the wall's bounds.
LANE_C = (-14800.0, 6800.0, 294.92)
SPAWN_PAD = (-11699.0, 512.0, 1577.046)  # visible firing-range floor (M0/M1)
SCHEDULE_ORIGIN_PREFIX = {"m4b_view": LANE_C, "m4b_pad": LANE_C, "m4_valk": LANE_C, "m4_pounce": LANE_C, "m4_stim": LANE_C, "m4_ctrl": LANE_C, "m4_pad": LANE_C, "m4_lift": LANE_C,
                          "m4_grapple": LANE_A, "x_pad_": SPAWN_PAD, "e8_hop350": LANE_C, "e3_": LANE_B, "e8_fast": LANE_C, "e8_slide": LANE_C, "e6_": LANE_A, "e7_": LANE_A,
                          "e8_drop": LANE_A}


# Exact-name origins take precedence over prefixes (grapple distance variants on lane A).
SCHEDULE_ORIGIN = {"m4_grapple_near": (-13950.0, 6500.0, 294.92), "m4_grapple_far": (-14400.0, 6500.0, 294.92)}
# M4b swing: lane A shifted 150 u to -Y (the wall spans y 6279..6719, so a 20 deg aim hits it near y 6493)
SCHEDULE_ORIGIN.update({n: (-14100.0, 6350.0, 294.92) for n in ("m4b_swing_side", "m4b_swing_turn", "m4b_swing_turn_w",
                                                                  "m4b_swing_jump", "m4b_swing_turn_jump")})
# round 2 starts 450 u to -Y of the wall centre, running along +Y
SCHEDULE_ORIGIN.update({n: (-14100.0, 6050.0, 294.92) for n in ("m4b_swing_cross", "m4b_swing_cross_w", "m4b_swing_cross_walk")})


def origin_for(name, default):
    if name in SCHEDULE_ORIGIN:
        return SCHEDULE_ORIGIN[name]
    for prefix, o in SCHEDULE_ORIGIN_PREFIX.items():
        if name.startswith(prefix):
            return o
    return default

RESET_SERVER = string.Template(r'''
entity p = GetPlayerArray()[0]
vector o = <$ox, $oy, $oz>
vector a = <$pitch, $yaw, 0>
p.SetVelocity( <0, 0, 0> )
p.SettleStance()
p.SetOrigin( o )
p.SetAngles( a )
p.SetVelocity( <0, 0, 0> )
p.PlantOnGround()
p.SnapEyeAngles( a )
p.SnapFeetToEyes()
string pre = ""
try
{
	$refill
	$pre
}
catch ( preErr )
{
	pre = " pre_error=" + string( preErr )
}
entity w = p.GetActiveWeapon( eActiveInventorySlot.mainHand )
string wn = w == null ? "none" : w.GetWeaponClassName()
string s = "[HSD-RESET] ver=1 batch=$batch run=$run ent=" + p.GetEntIndex() + " o=" + p.GetOrigin().x + "," + p.GetOrigin().y + "," + p.GetOrigin().z + " vel=" + p.GetVelocity().x + "," + p.GetVelocity().y + "," + p.GetVelocity().z + " yaw=" + p.EyeAngles().y + " ground=" + ( p.IsOnGround() ? 1 : 0 ) + " slide=" + ( p.IsSliding() ? 1 : 0 ) + " weapon=" + wn + " t=" + Time() + pre
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
		if ( verb == "waitair" || verb == "waitland" )
		{
			bool wantGround = verb == "waitland"
			int g = 0
			while ( p.IsOnGround() != wantGround && g < 1200 )
			{
				WaitFrame()
				g++
			}
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=" + verb + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() + " waited=" + g )
			continue
		}
		if ( verb == "set" )
		{
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=set cvar=" + parts[1] + " value=" + parts[2] + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() )
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


def get_schedule(name):
    """Named schedule, or a parametric sweep point generated from the name:
    e7_mb_f<N> / e7_sg_f<N>  second jump press (and for sg a crouch on the next frame) N frames after the climb jump;
    e3_right_k<N>            +moveright pressed N frames after the jump press.
    N is in exact frames at the session's frame rate."""
    if name in SCHEDULES:
        return SCHEDULES[name]
    m = re.fullmatch(r"e7_(mb|sg)_f(\d+)", name)
    if m:
        k = int(m.group(2))
        tail = "tap jump; tap duck" if m.group(1) == "sg" else "tap jump"
        return ("wait 72; down speed; down forward; wait 1.2s; tap jump; waitf %d; %s; wait 1.5s; up forward; up speed; wait 1.0s"
                % (k - 1, tail))
    m = re.fullmatch(r"e3_right_k(\d+)", name)
    if m:
        k = int(m.group(1))
        return ("wait 72; down speed; down forward; wait 1.0s; tap jump; waitf %d; up forward; up speed; down moveright; "
                "wait 0.9s; up moveright; wait 0.5s" % k)
    return None


# Refill tactical, ultimate and glide/jet meters at every reset when --kit is set (_weapon_utility.nut:3810-3865).
REFILL = "DevAbilities_RefillPlayer( p, true )"

KIT_SERVER = r'''
string out = ""
try
{
	entity p = GetPlayerArray()[0]
	ItemFlavor c = LoadoutSlot_GetItemFlavor( ToEHI( p ), Loadout_Character() )
	foreach ( int slot in [ OFFHAND_TACTICAL, OFFHAND_ULTIMATE ] )
	{
		entity old = p.GetOffhandWeapon( slot )
		if ( IsValid( old ) )
			p.TakeOffhandWeapon( slot )
	}
	string tac = CharacterAbility_GetWeaponClassname( CharacterClass_GetTacticalAbility( c ) )
	string ult = CharacterAbility_GetWeaponClassname( CharacterClass_GetUltimateAbility( c ) )
	p.GiveOffhandWeapon( tac, OFFHAND_TACTICAL, [] )
	p.GiveOffhandWeapon( ult, OFFHAND_ULTIMATE, [] )
	int np = 0
	foreach ( ItemFlavor ab in CharacterClass_GetPassiveAbilities( c ) )
	{
		GivePassive( p, CharacterAbility_GetPassiveIndex( ab ) )
		np++
	}
	DevAbilities_RefillPlayer( p, true )
	out = "legend=" + ItemFlavor_GetHumanReadableRef( c ) + " tactical=" + tac + " ultimate=" + ult + " passives=" + np
}
catch ( err )
{
	out = "error=" + string( err )
}
AgentLink_Reply( out )
'''


def parse_schedule(spec, fps=144.0):
    """Normalise a schedule to client frames at `fps`.

    wait N   N frames at 144 fps, scaled to round(N * fps / 144) so durations hold at any frame rate
    wait Xs  X seconds -> round(X * fps) frames
    waitf N  exactly N frames at any frame rate (for frame-window sweeps)
    """
    steps = []
    for s in (x.strip() for x in spec.split(";") if x.strip()):
        verb, _, arg = s.partition(" ")
        if verb in ("wait", "waitf"):
            if verb == "waitf" and arg.isdigit():
                n = int(arg)
            elif verb == "wait" and arg.endswith("s"):
                n = int(round(float(arg[:-1]) * fps))
            elif verb == "wait" and arg.isdigit():
                n = int(round(int(arg) * fps / 144.0))
            else:
                raise ValueError(f"bad wait: {s!r}")
            steps.append(f"wait {n}")
            continue
        steps.append(s)
        if verb in ("waitair", "waitland"):
            continue
        if verb in ("down", "up", "tap"):
            if arg not in KEYS:
                raise ValueError(f"unknown key in {s!r}")
        elif verb == "set":
            cvar, _, val = arg.partition(" ")
            if cvar not in VIEW_CVARS:
                raise ValueError(f"cvar not allowed in {s!r}")
            float(val)
        else:
            raise ValueError(f"unknown step {s!r}")
    return steps


def has_state_waits(steps):
    return any(s in ("waitair", "waitland") for s in steps)


def schedule_frames(steps):
    """Frames of the fixed part of the schedule (state waits add a variable number)."""
    n = 0
    for s in steps:
        verb, _, arg = s.partition(" ")
        n += int(arg) if verb == "wait" else (1 if verb == "tap" else 0) if verb != "waitair" and verb != "waitland" else 0
    return n


def _field(line, key):
    for tok in line.split():
        if tok.startswith(key + "="):
            return tok[len(key) + 1:]
    return None


def check_pacing(lines, frames, fps, tol, variable=False):
    """A frame-indexed schedule only means the planned durations at the planned frame rate.
    Returns (ok, reason, measured fps from PlatformTime between 'start' and 'end')."""
    start = next((l for l in lines if "edge=start" in l), None)
    end = next((l for l in lines if "edge=end" in l), None)
    if not start or not end:
        return False, "no start/end edge (settle timeout?)", None
    n = int(_field(end, "frame")) - int(_field(start, "frame"))
    if (not variable and n != frames) or (variable and n < frames):
        return False, f"schedule ran {n} frames, planned {'>= ' if variable else ''}{frames}", None
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
    ap.add_argument("--geometry", choices=["none", "m3"], default="none",
                    help="m3: (re)spawn the test wall on lane A before the trials (test_geometry.py)")
    ap.add_argument("--kit", action="store_true",
                    help="equip the legend's tactical, ultimate and passives (Agent_SetLegend changes only the setfile; "
                         "m4/ABILITY-TRIGGERS.md) and refill abilities at every reset")
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

    # 'name' runs --trials times, 'name*N' runs N times; a single unknown token is a literal step list.
    tokens = a.schedule.split(",")
    counts = {}
    for tok in tokens:
        n, _, c = tok.partition("*")
        counts[n] = int(c) if c else a.trials
    names = list(counts) if all(get_schedule(n) for n in counts) else [a.schedule]
    if names == [a.schedule]:
        counts = {a.schedule: a.trials}
    scheds = {n: parse_schedule(get_schedule(n) or n, a.fps) for n in names}
    ox, oy, oz = a.origin
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    manifest = {"schema": "hsd-runner/2", "label": a.label, "created": stamp,
                "schedules": {n: {"steps": st, "frames": schedule_frames(st)} for n, st in scheds.items()},
                "origin": list(a.origin), "yaw": a.yaw, "client_fps": a.fps, "census": not a.no_census, "legend": a.legend or None,
                "legend_reply": None, "trials": []}

    with AgentLink("server", a.game) as server, AgentLink("client", a.game) as client:
        # session values of the view-rate cvars, restored after every trial ('set' steps change them)
        view_cvars = {}
        for cv in VIEW_CVARS:
            r = client.eval(f'AgentLink_Reply( GetConVarString( "{cv}" ) )', check=False)
            view_cvars[cv] = r.get("reply", "")
        manifest["view_cvars"] = view_cvars
        if a.fps != 144.0:
            client.cmd(f"fps_max {a.fps:g}")
            time.sleep(3.0)
        if a.geometry == "m3":
            import test_geometry as tg
            server.eval(tg.CLEAR, check=False)
            r = server.eval(tg.SPAWN % dict(model=tg.M3_WALL_MODEL, x=tg.M3_WALL_ORIGIN[0], y=tg.M3_WALL_ORIGIN[1],
                                            z=tg.M3_WALL_ORIGIN[2], yaw=0.0), check=False)
            manifest["geometry"] = {"wall": r.get("reply", "")}
            for side in (server, client):  # [MB-TRIG] per press edge, [MB-APPLY] per boost finish
                side.cmd("bridge_mantle_boost_trig_log 1")
                side.cmd("bridge_mantle_boost_apply_log 1")
            print("geometry:", r.get("reply", ""))
            if "prop=" not in r.get("reply", "") or "invalid" in r.get("reply", ""):
                raise SystemExit("test wall could not be spawned")
            time.sleep(2.0)
        if a.legend:
            r = server.eval('Agent_SetLegend( "me", "%s" )' % a.legend.replace('"', ''))
            manifest["legend_reply"] = r.get("reply", "")
            print("legend:", manifest["legend_reply"])
            if '"ok":true' not in manifest["legend_reply"].replace(" ", ""):
                raise SystemExit("could not set the legend: " + manifest["legend_reply"])
            time.sleep(2.0)
        if a.kit:
            r = server.eval(KIT_SERVER, check=False)
            manifest["kit_reply"] = r.get("reply", "")
            print("kit:", manifest["kit_reply"])
            if "error" in manifest["kit_reply"] or not manifest["kit_reply"]:
                raise SystemExit("could not equip the legend kit")
            time.sleep(1.0)
        if not a.no_census:
            # E0 census: client class vars (bridge_classvar_get) and both sides' settings dump.
            for side, line in ((client, "exec user/hsd_e0_classvars"), (client, "hsd_md_dump_now 1"),
                               (server, "hsd_md_dump_now 1")):
                side.cmd(line)
            time.sleep(2.0)
        plan = [(names[0], 90 + w, 900 + w, True) for w in range(a.warmup)]
        k = 0
        for n in names:
            for _ in range(counts[n]):
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
            ox, oy, oz = origin_for(name, tuple(a.origin))
            pitch = SCHEDULE_PITCH.get(name, 0.0)
            pre = next((code for prefix, code in SCHEDULE_PRE.items() if name.startswith(prefix)), "")  # prefix may be a tuple
            reset = server.eval(RESET_SERVER.substitute(ox=ox, oy=oy, oz=oz, yaw=yaw, pitch=pitch, batch=batch, run=run,
                                                         refill=REFILL if a.kit else "", pre=pre))
            for st in steps:
                if st.startswith("set "):
                    client.cmd(st[4:])
            sched = client.eval(SCHED_CLIENT.substitute(
                steps=", ".join(json.dumps(s) for s in steps), ox=ox, oy=oy, oz=oz,
                settle_frames=a.settle_frames, settle_timeout=a.settle_timeout, trial=trial, run=run))
            lines, gap = wait_for_end(client, since, trial, timeout=(frames + a.settle_timeout) / a.fps * 3 + 30)
            server.cmd("hsd_md_run 0")
            client.cmd("hsd_md_run 0")
            for cv, val in view_cvars.items():
                if val and any(st.startswith("set " + cv + " ") for st in steps):
                    client.cmd(f"{cv} {val}")
            ok, why, fps = check_pacing(lines, frames, a.fps, a.fps_tol, variable=has_state_waits(steps))
            manifest["trials"].append({"trial": trial, "run": run, "batch": batch, "schedule": name, "yaw": yaw, "origin": [ox, oy, oz],
                                       "schedule_frames": frames, "reset": reset.get("reply", ""),
                                       "scheduled": sched.get("reply", ""), "sched_lines": lines,
                                       "log_gap": gap, "measured_fps": fps, "ok": ok, "why": why, "warmup": warm})
            tag = "warm-up " if warm else ""
            print(f"{tag}trial {trial} run r{run} {name}: {'ok' if ok else 'FAILED (' + why + ')'} fps={fps}")
            time.sleep(1.0)

        if a.fps != 144.0:
            client.cmd("fps_max 144")
    out = os.path.join(a.out, f"{stamp}_{a.label}")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "runner.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1)
    print("wrote", os.path.relpath(os.path.join(out, "runner.json"), REPO))
    return 0 if all(t["ok"] for t in manifest["trials"] if not t["warmup"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
