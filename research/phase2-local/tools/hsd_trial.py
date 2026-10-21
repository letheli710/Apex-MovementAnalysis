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

KEYS = {"forward", "backward", "moveleft", "moveright", "jump", "duck", "speed", "left", "right"}

# Facing so that the schedule's ground motion runs along +X (Source yaw: 0 = +X, 90 = +Y; right = (sin, -cos)).
SCHEDULE_YAW = {"e1_side": 90.0, "e1_back": 180.0, "e1_diag": 45.0}

# Start positions per schedule prefix (M3). Lane A faces the test wall (test_geometry.py: rock face at
# x ~ -13706, y 6380..6620, top ~ +232 u); lane B is the open part of the field at y 5900.
LANE_A = (-14100.0, 6500.0, 294.92)
LANE_B = (-14200.0, 5900.0, 294.92)
# Lane C: y 6800 is flat from x -14825 to -12475 (m3/map/field_fine.json) and 81 u clear of the wall's bounds.
LANE_C = (-14800.0, 6800.0, 294.92)
SPAWN_PAD = (-11699.0, 512.0, 1577.046)  # visible firing-range floor (M0/M1)
SCHEDULE_ORIGIN_PREFIX = {"x_pad_": SPAWN_PAD, "e8_hop350": LANE_C, "e3_": LANE_B, "e8_fast": LANE_C, "e8_slide": LANE_C, "e6_": LANE_A, "e7_": LANE_A,
                          "e8_drop": LANE_A}


def origin_for(name, default):
    for prefix, o in SCHEDULE_ORIGIN_PREFIX.items():
        if name.startswith(prefix):
            return o
    return default

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
            reset = server.eval(RESET_SERVER.substitute(ox=ox, oy=oy, oz=oz, yaw=yaw, batch=batch, run=run))
            sched = client.eval(SCHED_CLIENT.substitute(
                steps=", ".join(json.dumps(s) for s in steps), ox=ox, oy=oy, oz=oz,
                settle_frames=a.settle_frames, settle_timeout=a.settle_timeout, trial=trial, run=run))
            lines, gap = wait_for_end(client, since, trial, timeout=(frames + a.settle_timeout) / a.fps * 3 + 30)
            server.cmd("hsd_md_run 0")
            client.cmd("hsd_md_run 0")
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
