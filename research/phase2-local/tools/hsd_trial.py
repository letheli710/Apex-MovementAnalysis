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
import math
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
    # N4-B (rea-native ledger G-07): ground key turns. Native Friction spares only the wish-aligned speed, so a key turn
    # should bend the velocity over ~0.1-0.3 s; the HSD replay motor sets v = s*wishdir (instant).
    "n4b_wd": "wait 72; down speed; down forward; wait 288; up forward; up speed; down moveright; wait 288; up moveright; wait 216",
    "n4b_ws": "wait 72; down speed; down forward; wait 288; up forward; up speed; down backward; wait 288; up backward; wait 216",
    "n4b_ad": "wait 72; down moveleft; wait 288; up moveleft; down moveright; wait 288; up moveright; wait 216",
    "n4b_wwd": "wait 72; down speed; down forward; wait 288; down moveright; wait 288; up moveright; up forward; up speed; wait 216",
    # N4-C (rea-native ledger J-04 / S-02 / G-12)
    # J-04: slide jump just after the 0.2 s duck transition (no refund, ~410 u/s), duck up in the air, then hop on landing.
    #       Native: h = max(299, h - 100) within skip_time; the replay motor clips to 299.
    "n4c_hop_d0": "wait 72; down speed; down forward; wait 288; down duck; wait 31; tap jump; up duck; waitair; waitland; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.3s",
    "n4c_hop_d1": "wait 72; down speed; down forward; wait 288; down duck; wait 31; tap jump; up duck; waitair; waitland; waitf 1; tap jump; waitair; waitland; wait 0.3s; up forward; up speed; wait 0.3s",
    # S-02: slides A (t 0), B (t 1.0 s), C (t 2.5 s) while sprinting. Native cooldown counts from the last slide start (B),
    #       so C gets no boost; the HSD Reference counts 1.8 s from the last boost (A), so C would be boosted.
    "n4c_slidechain": "wait 72; down speed; down forward; wait 288; down duck; wait 58; up duck; wait 86; down duck; wait 58; up duck; wait 158; down duck; wait 144; up duck; up forward; up speed; wait 144",
    "n4c_slidechain_ctrl": "wait 72; down speed; down forward; wait 288; down duck; wait 58; up duck; wait 302; down duck; wait 144; up duck; up forward; up speed; wait 144",
    # G-12: slide, then drop W and hold D only. Native: the perpendicular wish accelerates at slideAccel*msc (~57.5 u/s^2).
    "n4c_slidesteer": "wait 72; down speed; down forward; wait 288; down duck; wait 4; up forward; up speed; down moveright; wait 144; up moveright; wait 72; up duck; wait 144",
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
    # M4 P3 (transitions only): Wraith Into the Void (4 s speed boost) with its control, Loba translocation (thrown
    # bracelet, teleport where it lands; velocity before/after and any control lock)
    "m4_wraith_void": "wait 72; down speed; down forward; wait 0.5s; tap offhand1; wait 4.2s; up forward; up speed; wait 1.0s",
    "m4_wraith_ctrl": "wait 72; down speed; down forward; wait 0.5s; wait 4.2s; up forward; up speed; wait 1.0s",
    "m4_loba_tele": "wait 72; down speed; down forward; wait 1.0s; tap offhand1; wait 3.0s; up forward; up speed; wait 1.0s",
    "m4_loba_tele_still": "wait 72; tap offhand1; wait 3.0s; wait 1.0s",
    # M5.5 grapple range check: pitch 0 straight at the test wall face (x -13706) from 800 / 840 / 860 / 900 u
    "m55_range_d800": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d840": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d860": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d900": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d950": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d1000": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d1050": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d1100": "wait 72; tap offhand1; wait 2.5s",
    "m55_range_d1200": "wait 72; tap offhand1; wait 2.5s",
    # the same without the infinite_abilities_grapple mod (DevAbilities_RefillWeapon adds it: range x2, M5.5 finding)
    "m55_nomod_d800": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d840": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d860": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d900": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d810": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d820": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_d830": "wait 72; tap offhand1; wait 2.5s",
    "m55_nomod_hold": "wait 72; tap offhand1; wait 3.0s; wait 2.5s",
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

# M6-A1 lurch stacking and tap strafe. All start with a sprint jump; W and sprint are released on the command after the
# jump so every later key press is a fresh edge (M3 lurch model: one lurch per press edge, window 0.2 s full -> 0.5 s).
_A1_JUMP = "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; "


def _a1_taps(key, n, gap):
    """n press edges of `key`, one every `gap` frames (a tap holds the key for one frame)."""
    return "; ".join(["tap %s; waitf %d" % (key, gap - 1)] * n)


SCHEDULES.update({
    # several press edges in one window: same direction at 6 / 12 / 24 frames apart, three in a row, opposite, sequence
    "a1_rr_n6": _A1_JUMP + "waitf 2; tap moveright; waitf 5; tap moveright; wait 1.4s",
    "a1_rr_n12": _A1_JUMP + "waitf 2; tap moveright; waitf 11; tap moveright; wait 1.4s",
    "a1_rr_n24": _A1_JUMP + "waitf 2; tap moveright; waitf 23; tap moveright; wait 1.4s",
    "a1_rrr_n6": _A1_JUMP + "waitf 2; " + _a1_taps("moveright", 3, 6) + "; wait 1.4s",
    "a1_lr_n12": _A1_JUMP + "waitf 2; tap moveleft; waitf 11; tap moveright; wait 1.4s",
    "a1_shift": _A1_JUMP + "waitf 2; tap moveright; waitf 7; tap backward; waitf 7; tap moveleft; wait 1.4s",
    # diagonal presses (two keys on the same command)
    "a1_diag_fr": _A1_JUMP + "waitf 2; down forward; down moveright; waitf 1; up forward; up moveright; wait 1.4s",
    "a1_diag_br": _A1_JUMP + "waitf 2; down backward; down moveright; waitf 1; up backward; up moveright; wait 1.4s",
    # tap strafe: forward press edges every 2 frames (a 60 Hz scroll) while the view turns right at a constant rate;
    # controls: taps without turning, turning without taps, turning with W held (plain air strafe, no new edges)
    "a1_ts_360": "set cl_yawspeed 360; " + _A1_JUMP + "waitf 2; down right; " + _a1_taps("forward", 15, 2) + "; up right; wait 1.2s",
    "a1_ts_180": "set cl_yawspeed 180; " + _A1_JUMP + "waitf 2; down right; " + _a1_taps("forward", 15, 2) + "; up right; wait 1.2s",
    "a1_ts_noturn": _A1_JUMP + "waitf 2; " + _a1_taps("forward", 15, 2) + "; wait 1.2s",
    "a1_turn_only": "set cl_yawspeed 360; " + _A1_JUMP + "waitf 2; down right; waitf 30; up right; wait 1.2s",
    "a1_turn_hold_w": "set cl_yawspeed 360; wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up speed; waitf 2; "
                      "down right; waitf 30; up right; up forward; wait 1.2s",
    # slide jump into a tap strafe (higher entry speed)
    "a1_sj_ts_360": "set cl_yawspeed 360; wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; waitf 1; "
                    "up duck; up forward; up speed; waitf 2; down right; " + _a1_taps("forward", 15, 2) + "; up right; wait 1.2s",
    # lurch after a wall bounce (M3 e6 bounce at 0.43 s): does the bounce jump reopen the window?
    "a1_wb_lurch3": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; tap jump; waitf 2; "
                    "tap moveright; wait 2.5s",
    "a1_wb_lurch30": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; tap jump; waitf 29; "
                     "tap moveright; wait 2.5s",
})

# M6-A2 climb / ledge / mantle on the lane-A rock at a chosen ledge height (geometry h<H>; m6/SOURCE-AUDIT.md E-C).
# a2_climb = the M3 e6_climb (sprint jump ~100 u before the face); a2_walk = run into it without a jump; a2_hang = W
# released 0.9 s after the jump (before the ledge) so the climb can settle into the hang; then cancel (back), hop
# (jump) and back-hop from the hang.
_A2_RUN = "wait 72; down speed; down forward; wait 1.2s; tap jump; "
SCHEDULES.update({
    "a2_climb": _A2_RUN + "wait 2.5s; up forward; up speed; wait 2.5s",
    "a2_walk": "wait 72; down forward; wait 3.0s; up forward; wait 1.5s",
    "a2_hang": _A2_RUN + "wait 0.9s; up forward; up speed; wait 2.0s",
    "a2_cancel": _A2_RUN + "wait 0.9s; up forward; up speed; wait 1.5s; down backward; wait 0.5s; up backward; wait 1.0s",
    "a2_hop": _A2_RUN + "wait 0.9s; up forward; up speed; wait 1.5s; tap jump; wait 2.0s",
    "a2_hop_back": _A2_RUN + "wait 0.9s; up forward; up speed; wait 1.5s; down backward; tap jump; wait 1.0s; up backward; wait 1.0s",
})

# A2 round 2 (after m6/a2_climb: no hang exists; W release on the wall = attached slide-down, release early in a
# mantle = cancel). h232: actions while sliding attached, the detach clock, a sideways key while climbing.
# h180: back during a mantle (W held) and W released at 0.70 / 0.74 / 0.78 s after the jump (cancel threshold).
_A2_REL = _A2_RUN + "wait 0.9s; up forward; up speed; wait 0.2s; "
SCHEDULES.update({
    "a2r_rel_jump": _A2_REL + "tap jump; wait 2.0s",
    "a2r_rel_back": _A2_REL + "down backward; wait 0.5s; up backward; wait 1.5s",
    "a2r_rel_backjump": _A2_REL + "down backward; tap jump; wait 0.5s; up backward; wait 1.5s",
    "a2r_rel_t05": _A2_RUN + "wait 0.5s; up forward; up speed; wait 2.5s",
    "a2r_rel_t11": _A2_RUN + "wait 1.1s; up forward; up speed; wait 2.5s",
    "a2r_side": _A2_RUN + "wait 0.5s; down moveright; wait 1.5s; up moveright; up forward; up speed; wait 1.5s",
    "a2r_mant_back": _A2_RUN + "wait 0.75s; down backward; wait 0.5s; up backward; up forward; up speed; wait 1.5s",
    "a2r_mrel_t070": _A2_RUN + "wait 0.70s; up forward; up speed; wait 2.0s",
    "a2r_mrel_t074": _A2_RUN + "wait 0.74s; up forward; up speed; wait 2.0s",
    "a2r_mrel_t078": _A2_RUN + "wait 0.78s; up forward; up speed; wait 2.0s",
})

# M6-B legend abilities (m6/SOURCE-AUDIT.md M6-B). Alter Void Passage through the lane-A rock (hold tactical to place,
# release; start 600 u / 150 u from the face); Loba translocation with an early drop (second tactical press) on the long
# P3 lane; Ash Phase Breach (ultimate) aimed at the ground 600 / 1200 / 2000 u ahead; Valkyrie jets: a 10 s hold to burn
# the meter and a pulse run (start cost per activation).
SCHEDULES.update({
    "b_alter_sprint": "wait 72; down speed; down forward; down offhand1; wait 0.4s; up offhand1; wait 3.0s; up forward; up speed; wait 2.0s",
    "b_alter_walk": "wait 72; down forward; down offhand1; wait 0.4s; up offhand1; wait 4.0s; up forward; wait 2.0s",
    "b_alter_stand": "wait 72; down offhand1; wait 0.4s; up offhand1; wait 1.0s; down forward; wait 2.5s; up forward; wait 2.0s",
    "b_loba_drop_t07": "wait 72; tap offhand1; wait 0.7s; tap offhand1; wait 3.0s",
    "b_loba_drop_t09": "wait 72; tap offhand1; wait 0.9s; tap offhand1; wait 3.0s",
    "b_loba_drop_t12": "wait 72; tap offhand1; wait 1.2s; tap offhand1; wait 3.0s",
    "b_loba_drop_t15": "wait 72; tap offhand1; wait 1.5s; tap offhand1; wait 3.0s",
    "b_loba_sprint_t09": "wait 72; down speed; down forward; wait 0.8s; tap offhand1; wait 0.9s; tap offhand1; up forward; up speed; wait 3.0s",
    "b_ash_600": "wait 72; tap offhand4; wait 1.0s; tap attack; wait 3.5s; wait 12.0s",
    "b_ash_1200": "wait 72; tap offhand4; wait 1.0s; tap attack; wait 3.5s; wait 12.0s",
    "b_ash_2000": "wait 72; tap offhand4; wait 1.0s; tap attack; wait 3.5s; wait 12.0s",
    # input pilots (the first M6-B run fired neither: Ash's ult is offhandHybrid -> main hand, deploy 0.8 s, then attack;
    # Alter's placement is offhandHold with offhand_switch_on_attack)
    "bp_alter_hold12": "wait 72; down offhand1; wait 1.2s; up offhand1; wait 1.0s; down forward; wait 2.5s; up forward; wait 1.5s",
    "bp_alter_hold_att": "wait 72; down offhand1; wait 0.8s; tap attack; wait 0.3s; up offhand1; wait 1.0s; down forward; wait 2.5s; up forward; wait 1.5s",
    "bp_alter_tap_att": "wait 72; tap offhand1; wait 1.0s; tap attack; wait 1.0s; down forward; wait 2.5s; up forward; wait 1.5s",
    "bp_ash_att": "wait 72; tap offhand4; wait 1.0s; tap attack; wait 3.5s",
    "bp_ash_hold_att": "wait 72; down offhand4; wait 1.0s; tap attack; up offhand4; wait 3.5s",
    "b_valk_hold10": "wait 72; tap jump; waitair; wait 0.2s; down jump; wait 10.0s; up jump; waitland; wait 6.0s",
    "b_valk_pulse": "wait 72; tap jump; waitair; wait 0.2s; " + "; ".join(["down jump; wait 0.3s; up jump; wait 0.35s"] * 4) + "; waitland; wait 3.0s",
})

# M6-A3 ziplines (geometry m6zip; m6/SOURCE-AUDIT.md E-Z). The player starts under the flat rope Z1 (100 u above the
# floor) facing along it, mounts with +use, then rides / jumps off / crouches off. z5 = Super Jump: a second jump K
# frames after the jump-off.
_Z_MOUNT = "wait 72; tap use; "
SCHEDULES.update({
    "z0_off0": _Z_MOUNT + "wait 2.0s", "z0_off40": _Z_MOUNT + "wait 2.0s", "z0_off80": _Z_MOUNT + "wait 2.0s",
    "z0_off120": _Z_MOUNT + "wait 2.0s", "z0_off160": _Z_MOUNT + "wait 2.0s",
    "z0_nouse": "wait 72; wait 2.0s",
    "z1_ride": _Z_MOUNT + "wait 5.0s",
    "z2_jump_none": _Z_MOUNT + "wait 0.8s; tap jump; wait 2.0s",
    "z2_jump_fwd": _Z_MOUNT + "wait 0.8s; down forward; tap jump; wait 2.0s; up forward",
    "z2_jump_back": _Z_MOUNT + "wait 0.8s; down backward; tap jump; wait 2.0s; up backward",
    "z2_jump_right": _Z_MOUNT + "wait 0.8s; down moveright; tap jump; wait 2.0s; up moveright",
    "z2_jump_pu30": _Z_MOUNT + "wait 0.8s; tap jump; wait 2.0s",
    "z2_jump_pd30": _Z_MOUNT + "wait 0.8s; tap jump; wait 2.0s",
    "z3_crouch": _Z_MOUNT + "wait 0.8s; tap duck; wait 2.0s",
    "z6_up": _Z_MOUNT + "wait 6.0s",
    "z6_vert": _Z_MOUNT + "wait 5.0s",
    "z7_air": "wait 72; down forward; tap jump; wait 0.25s; tap use; up forward; wait 2.0s",
})
# A3 round 2 (after m6/a3_zip): Super Jump the community way (use on the ground, jump M frames later, second jump K
# frames after that); jump-off at other ride speeds; turning the view during the ride (direction: rope or view);
# air grab from closer (ground range is 130 u) and with use held; duck held through the detach; vertical rope turn.
SCHEDULES.update({"z5b_m%d_k%d" % (m, k): "wait 72; tap use; waitf %d; tap jump; waitf %d; tap jump; wait 2.0s" % (m - 1, k - 1)
                  for m, k in ((1, 1), (1, 2), (1, 4), (3, 2), (6, 2))})
SCHEDULES.update({"z8_jump_t%s" % str(t).replace(".", ""): _Z_MOUNT + "wait %.1fs; tap jump; wait 2.0s" % t
                  for t in (0.2, 0.4, 1.0, 1.6)})
SCHEDULES.update({
    "z9_yaw45": "set cl_yawspeed 90; " + _Z_MOUNT + "wait 0.3s; down right; wait 0.5s; up right; wait 0.4s; tap jump; wait 2.0s",
    "z9_yaw90": "set cl_yawspeed 90; " + _Z_MOUNT + "wait 0.2s; down right; wait 1.0s; up right; tap jump; wait 2.0s",
    "z7b_air": "wait 72; tap jump; wait 0.15s; tap use; wait 2.0s",
    "z7c_air_hold": "wait 72; tap jump; wait 0.1s; down use; wait 0.6s; up use; wait 1.5s",
    "z3_duckhold": _Z_MOUNT + "wait 0.8s; down duck; wait 1.0s; up duck; wait 1.0s",
    "z6_vert_turn": "set cl_yawspeed 180; " + _Z_MOUNT + "wait 0.3s; down right; wait 0.5s; up right; wait 4.0s",
})
# Pathfinder (kit, geometry m3,m6zip): g1 = grapple release by a second tactical press / by attack at the M4 hold pose;
# g3 = grapple aimed at the middle of rope Z1 from 250 u (out of +use range), with and without a use press during the pull
SCHEDULES.update({
    "g1_rel_tac": "wait 72; tap offhand1; wait 0.6s; tap offhand1; wait 2.5s",
    "g1_rel_attack": "wait 72; tap offhand1; wait 0.6s; tap attack; wait 2.5s",
    "g1_hold": "wait 72; tap offhand1; wait 3.0s",
    "g3_hook": "wait 72; tap offhand1; wait 3.0s",
    "g3_hook_use": "wait 72; tap offhand1; wait 0.5s; tap use; wait 3.0s",
})

SCHEDULES.update({"z5_sj_k%d" % k: _Z_MOUNT + "wait 0.5s; tap jump; waitf %d; tap jump; wait 2.0s" % k
                  for k in (1, 2, 3, 4, 6, 8, 12, 40)})

# ---- M8 track R (m8/M8-PLAN.md). Octane pad double jump: the pad is spawned 300 u ahead on lane C (as M4); sprint in,
# release W and sprint on the launch frame (waitair), then a jump press K frames after the launch.
_M8P = "wait 72; down speed; down forward; waitair; up forward; up speed; "
SCHEDULES.update({"m8_pad_dj_f%d" % k: _M8P + ("waitf %d; " % k if k else "") + "tap jump; wait 4.0s"
                  for k in (0, 6, 12, 24, 60, 200, 300)})
SCHEDULES.update({
    "m8_pad_none": _M8P + "wait 4.5s",
    "m8_pad_dj2": _M8P + "waitf 60; tap jump; wait 1.0s; tap jump; wait 3.5s",
    # control without a pad (geometry cleared): a normal sprint jump, then a second press in the air
    # round 2: grant threshold, early press then late press, jump-in (with the press held through the launch), input /
    # view direction, lurch after the double jump (and its control), unused grant after landing, crouch and walk entry
    "m8_pad_dj_f9": _M8P + "waitf 9; tap jump; wait 4.0s",
    "m8_pad_dj_f15": _M8P + "waitf 15; tap jump; wait 4.0s",
    "m8_pad_early_late": _M8P + "waitf 6; tap jump; waitf 53; tap jump; wait 4.0s",
    "m8_pad_jumpin": "wait 72; down speed; down forward; waitf 117; tap jump; waitf 20; up forward; up speed; wait 0.5s; tap jump; wait 4.0s",
    "m8_pad_jumpin_hold": "wait 72; down speed; down forward; waitf 117; down jump; waitf 20; up forward; up speed; wait 1.2s; up jump; "
                          "wait 0.3s; tap jump; wait 3.5s",
    "m8_pad_dj_right": _M8P + "waitf 60; down moveright; tap jump; wait 0.5s; up moveright; wait 3.5s",
    "m8_pad_dj_back": _M8P + "waitf 60; down backward; tap jump; wait 0.5s; up backward; wait 3.5s",
    "m8_pad_dj_view": "set cl_yawspeed 90; " + _M8P + "down right; wait 1.0s; up right; waitf 2; tap jump; wait 3.5s",
    "m8_pad_dj_viewfwd": "set cl_yawspeed 90; " + _M8P + "down right; wait 1.0s; up right; waitf 2; down forward; tap jump; wait 0.3s; "
                         "up forward; wait 3.2s",
    "m8_pad_dj_lurch": _M8P + "waitf 60; tap jump; waitf 2; tap moveright; wait 3.5s",
    "m8_pad_lurch": _M8P + "waitf 62; tap moveright; wait 3.5s",
    "m8_pad_land_jump": _M8P + "waitland; waitf 12; tap jump; wait 0.3s; tap jump; wait 2.0s",
    "m8_padc_dj": "wait 72; down duck; wait 0.5s; down forward; waitair; up forward; up duck; waitf 60; tap jump; wait 4.0s",
    "m8_padw_dj": "wait 72; down forward; waitair; up forward; waitf 60; tap jump; wait 4.0s",
    # round 3: the vertical rule between the add and floor branches (presses at 1.0 / 1.3 / 1.45 s), and the horizontal
    # rule with a key already held (pressed at 0.55 s, outside the launch lurch window; the DJ cmd has no new key edge)
    "m8_pad_dj_f120": _M8P + "waitf 120; tap jump; wait 3.5s",
    "m8_pad_dj_f156": _M8P + "waitf 156; tap jump; wait 3.5s",
    "m8_pad_dj_f174": _M8P + "waitf 174; tap jump; wait 3.5s",
    "m8_pad_djh_right": _M8P + "waitf 66; down moveright; waitf 24; tap jump; wait 0.5s; up moveright; wait 3.0s",
    "m8_pad_djh_back": _M8P + "waitf 66; down backward; waitf 24; tap jump; wait 0.5s; up backward; wait 3.0s",
    "m8_pad_djh_fwd": _M8P + "waitf 66; down forward; waitf 24; tap jump; wait 0.5s; up forward; wait 3.0s",
    "m8_pad_djh_diag": _M8P + "waitf 66; down forward; down moveright; waitf 24; tap jump; wait 0.5s; up forward; up moveright; wait 3.0s",
    "m8_padc_djh_right": "wait 72; down duck; wait 0.5s; down forward; waitair; up forward; up duck; waitf 66; down moveright; waitf 24; "
                         "tap jump; wait 0.5s; up moveright; wait 3.0s",
    # round 4: vertical branch boundary (pre vz between ~350 and ~410), presses 128..140 frames after the launch
    **{"m8_pad_dj_f%d" % k: _M8P + "waitf %d; tap jump; wait 3.5s" % k for k in range(128, 141, 2)},
    "m8_djctrl": "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; wait 0.3s; tap jump; wait 2.0s",
})

# M8 item 5 (lead add-on): lurch follow-ups on lane B, from the M6-A1 sprint jump (W and sprint released on the command after
# the jump). a) reverse chain: press edges every g frames rotating the wish W -> W+D -> D -> S+D -> S (mirror with A);
# b) a key held from before the jump plus a new press; c) tap strafe at 720 / 1440 deg/s; e) slide-jump (350) entry.
def _m8_chain(side, g):
    combo = lambda a, b: "down %s; down %s; waitf 1; up %s; up %s" % (a, b, a, b)  # noqa: E731
    steps = ["tap forward", combo("forward", side), "tap " + side, combo("backward", side), "tap backward"]
    return "; ".join(s + "; waitf %d" % (g - 1) for s in steps)


_M8J_HOLD = "wait 72; down speed; down forward; wait 1.0s; "
SCHEDULES.update({"m8_lurch_chain_%s_g%d" % (s[4], g): _A1_JUMP + "waitf 2; " + _m8_chain(s, g) + "; wait 1.0s"
                  for s in ("moveright", "moveleft") for g in (6, 10, 12)})
SCHEDULES.update({
    "m8_lurch_holdA_W": _M8J_HOLD + "down moveleft; waitf 2; tap jump; waitf 1; up forward; up speed; waitf 10; tap forward; "
                        "wait 1.0s; up moveleft; wait 0.3s",
    "m8_lurch_W_only": _A1_JUMP + "waitf 11; tap forward; wait 1.3s",
    "m8_lurch_holdA_D": _M8J_HOLD + "down moveleft; waitf 2; tap jump; waitf 1; up forward; up speed; waitf 10; tap moveright; "
                        "wait 1.0s; up moveleft; wait 0.3s",
    "m8_lurch_D_only": _A1_JUMP + "waitf 11; tap moveright; wait 1.3s",
    "m8_lurch_ts_720": "set cl_yawspeed 720; " + _A1_JUMP + "waitf 2; down right; " + _a1_taps("forward", 15, 2) + "; up right; wait 1.2s",
    "m8_lurch_ts_1440": "set cl_yawspeed 1440; " + _A1_JUMP + "waitf 2; down right; " + _a1_taps("forward", 15, 2) + "; up right; wait 1.2s",
    "m8_lurch_turn_720": "set cl_yawspeed 720; " + _A1_JUMP + "waitf 2; down right; waitf 30; up right; wait 1.2s",
    "m8_lurch_turn_1440": "set cl_yawspeed 1440; " + _A1_JUMP + "waitf 2; down right; waitf 30; up right; wait 1.2s",
    "m8_lurch_sj_d_k2": "wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; waitf 1; up duck; up forward; "
                        "up speed; waitf 1; tap moveright; wait 1.2s",
    "m8_lurch_spr_d_k2": _A1_JUMP + "waitf 1; tap moveright; wait 1.2s",
})
# d) walk off the 232 u rock (geometry m3; flat top z 532.80 from x -13700 to -13500, probed) with no jump: W released when
# airborne, then a D press K frames later
SCHEDULES.update({"m8_lurch_ledge_k%d" % k: "wait 72; down forward; waitair; up forward; waitf %d; tap moveright; wait 1.5s" % k
                  for k in (2, 12, 24, 48)})
SCHEDULES["m8_lurch_ledge_none"] = "wait 72; down forward; waitair; up forward; wait 1.5s"

# M8 R4 slope slide (time-boxed): the spawn-side hillside found by the M8 probe (y 550: flat 1580.03 to x -10575, then a
# planar 29.4 deg ramp to x -10375 and a 30-41 deg hillside down to x -9500, z 897). Start on the flat top facing +X.
SCHEDULES.update({
    "m8_slope_slide": "wait 72; down speed; down forward; wait 1.0s; down duck; wait 3.0s; up duck; up forward; up speed; wait 1.0s",
    "m8_slope_slide_now": "wait 72; down speed; down forward; wait 1.0s; down duck; up forward; up speed; wait 3.0s; up duck; wait 1.0s",
    "m8_slope_run": "wait 72; down speed; down forward; wait 4.0s; up forward; up speed; wait 1.0s",
})

# M8 Horizon gravity lift (deployed 120 u ahead on lane C, as M4). Times count from the lift entry (waitair). Every trial
# lasts >= 11 s so the previous lift (10 s lifetime) is gone before the next reset (M4 overlap artefact).
_M8L = "wait 72; down forward; waitair; up forward; "
SCHEDULES.update({
    "m8_lift_ride": _M8L + "wait 11.0s",
    "m8_lift_through": "wait 72; down forward; wait 3.0s; up forward; wait 8.5s",
    "m8_lift_top_w": _M8L + "wait 3.7s; down forward; wait 1.5s; up forward; wait 6.0s",
    "m8_lift_top_jump": _M8L + "wait 3.8s; tap jump; wait 7.2s",
    "m8_lift_ej_jump": _M8L + "wait 4.4s; tap jump; wait 6.6s",
    "m8_lift_ej_strafe": _M8L + "wait 4.4s; down moveright; wait 1.0s; up moveright; wait 5.6s",
    "m8_lift_ej_back": _M8L + "wait 4.4s; down backward; wait 1.5s; up backward; wait 5.1s",
    "m8_lift_land_w": _M8L + "wait 1.0s; waitland; down forward; wait 2.0s; up forward; wait 3.0s",
    "m8_liftoff80_w": "wait 72; down forward; wait 3.0s; up forward; wait 8.5s",
    "m8_liftoff83_w": "wait 72; down forward; wait 3.0s; up forward; wait 8.5s",
})
SCHEDULES.update({"m8_lift_side_t%02d" % int(t * 10): _M8L + "wait %.1fs; down moveright; wait 1.0s; up moveright; wait %.1fs"
                  % (t, 10.0 - t) for t in (0.5, 1.5, 3.0)})

# M8 superglide coverage (geometry h<H>, lane A rock, native code: --both-cvar mantle_boost_enabled=0). waittrav = the client
# sees the traversal start; the press comes K frames later. m8_sg_<approach>_<var>_k<K>: approach spr (sprint jump as A2),
# walk (walk jump), slide (slide jump), ang (sprint at 30 deg to the face normal), wd (view 45 deg, W+D, motion normal to the
# face); var sg = jump then crouch on the next frame, mb = jump only, none = no press.
_M8SG_APP = {
    "spr": "wait 72; down speed; down forward; wait 1.2s; tap jump; waittrav; ",
    "walk": "wait 72; down forward; wait 1.65s; tap jump; waittrav; ",
    "slide": "wait 72; down speed; down forward; wait 1.05s; down duck; wait 0.25s; tap jump; up duck; waittrav; ",
    "ang": "wait 72; down speed; down forward; wait 1.4s; tap jump; waittrav; ",
    "wd": "wait 72; down speed; down forward; down moveright; wait 1.2s; tap jump; waittrav; ",
}
_M8SG_VAR = {"sg": "tap jump; tap duck; ", "mb": "tap jump; ", "none": ""}


def _m8_sg(name):
    m = re.fullmatch(r"m8_sg_(spr|walk|slide|ang|wd)_(sg|mb|none)_k(\d+)", name)
    if not m:
        return None
    k = int(m.group(3))
    tail = "wait 1.5s; up forward; up speed; " + ("up moveright; " if m.group(1) == "wd" else "") + "wait 1.0s"
    return _M8SG_APP[m.group(1)] + ("waitf %d; " % k if k else "") + _M8SG_VAR[m.group(2)] + tail

# ---- M8 track R2 (time-boxed feasibility probes, m8/EXPANSION-ASSESSMENT.md). Revenant long climb on the lane-A rock
# (geometry h<H> up to ~480, or s<H> = two stacked rocks up to ~950): sprint jump into the face as a2_climb, W held 6 s.
# Pounce into the face: start d u before the face (x -13728 - d at the player origin), view pitch -15 (no speed loss,
# launch 50 deg up), tap tactical, W pressed after the release (0.9 s pull-out), so the face is reached 0.33 s (d150)
# or 1.1 s (d500) after the release, inside / outside the 0.75 s wall-climb disable.
SCHEDULES.update({
    "m8r2_climb": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 6.0s; up forward; up speed; wait 2.0s",
    # round 2: every s1400 climb ended 0.175 s after the W release, still rising at ~135 u/s; hold W 12 s on the s1850 stack
    "m8r2_climb_long": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 12.0s; up forward; up speed; wait 3.0s",
    # optional probe 3 (Sparrow wall launch, SDK wall_launch.cpp): a jump press while climbing with W held (input into the wall)
    "m8r2_spw_jump": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.7s; tap jump; wait 2.5s; up forward; up speed; wait 1.5s",
    "m8r2_climb_rel": "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 2.0s; up forward; up speed; wait 4.0s",
    "m8r2_pounce_d150": "wait 72; tap offhand1; wait 0.95s; down forward; wait 5.0s; up forward; wait 1.5s",
    "m8r2_pounce_d500": "wait 72; tap offhand1; wait 0.95s; down forward; wait 5.0s; up forward; wait 1.5s",
    "m8r2_jumpin_ctrl": "wait 72; down forward; wait 0.3s; tap jump; wait 5.0s; up forward; wait 1.5s",
})
# Vantage jet drive, shortcut without the Echo AI: the reset spawns a script mover D u ahead on lane C (120 u above the
# floor; drive target = mover - 69 u as the source offset), and a server thread calls BeginJetDrive(787, 1575, mover, mover,
# <0,0,-69>, round(2*dist/787, 1)) + EnableJetDriveDoubleJump(<512,0,394>, 0.5) 1.5 s after the reset
# (mp_ability_companion_launch.nut:79-88,794-811). The schedule waits for the lift-off (waitair). _dj<K>: jump press K
# frames after the lift-off; _duck: crouch 0.4 s after it; _mvy / _mvx: the mover moves 300 u to +Y in 1.0 s / 600 u to +X
# in 1.5 s from the drive start. m8r2_echo_tac: the real tactical (legend vantage --kit), two presses.
_R2JD = "wait 72; waitair; "
SCHEDULES.update({"m8r2_jd_d%d" % d: _R2JD + "wait 4.0s" for d in (400, 800, 1200)})
SCHEDULES.update({"m8r2_jd_d800_dj%d" % k: _R2JD + "waitf %d; tap jump; wait 4.0s" % k for k in (30, 60, 90, 120)})
SCHEDULES.update({
    "m8r2_jd_d800_duck": _R2JD + "wait 0.4s; tap duck; wait 4.0s",
    "m8r2_jd_d800_mvy": _R2JD + "wait 4.0s",
    "m8r2_jd_d800_mvx": _R2JD + "wait 4.0s",
    "m8r2_echo_tac": "wait 72; tap offhand1; wait 3.0s; tap offhand1; wait 5.0s",
    "m8r2_echo_hold": "wait 72; down offhand1; wait 1.0s; up offhand1; wait 3.0s; tap offhand1; wait 5.0s",
    # explore round showed: tap = send Echo along the aim, hold = launch to it (CheckForHoldInput_Thread). Send, then hold.
    "m8r2_echo_send_launch": "wait 72; tap offhand1; wait 2.5s; down offhand1; wait 1.0s; up offhand1; wait 5.0s",
})
SCHEDULES.update({"m8r2_jd_d800_dj%d" % k: _R2JD + "waitf %d; tap jump; wait 4.0s" % k for k in (100, 110)})


def _r2_jd_pre(d, move=""):
    return ('foreach ( entity e in GetEntArrayByScriptName( "hsd_r2_tgt" ) ) e.Destroy()\n'
            'entity tg = CreateScriptMover( "hsd_r2_tgt", o + <%d, 0, 120>, <0, 0, 0> )\n'
            'void functionref() jdf = void function() : ( p, tg ) {\n'
            '\ttry {\n'
            '\t\twait 1.5\n'
            '\t\tif ( !IsValid( tg ) || !IsValid( p ) ) return\n'
            '\t\tfloat dist = Length( tg.GetOrigin() - p.GetOrigin() )\n'
            '\t\tfloat to = floor( 20.0 * dist / 787.0 + 0.5 ) / 10.0\n'
            '\t\tprintt( "[R2-JD] begin t=" + Time() + " o=" + p.GetOrigin() + " tgt=" + tg.GetOrigin() + " timeout=" + to )\n'
            '\t\tp.BeginJetDrive( 787.0, 1575.0, tg.GetOrigin(), tg, <0, 0, -69>, to )\n'
            '\t\tp.EnableJetDriveDoubleJump( <512, 0, 394>, 0.5, "", "" )\n'
            '\t\t%s\n'
            '\t} catch ( jdErr ) { printt( "[R2-JD] error " + string( jdErr ) ) }\n'
            '}\n'
            'thread jdf()\n'
            'pre = " jd_tgt=" + IsValid( tg )\n') % (d, move)



KEYS = {"forward", "backward", "moveleft", "moveright", "jump", "duck", "speed", "left", "right", "lookup", "lookdown",
        "offhand1", "offhand4", "use", "attack", "zoom"}
# Client cvars a schedule may change with 'set' (constant-rate view turns, M4b).
VIEW_CVARS = ("cl_yawspeed", "cl_pitchspeed")

# View pitch per schedule (Source: + = down). Grapple trials aim slightly up at the test wall.
SCHEDULE_PITCH = {"m8r2_pounce_d150": -15.0, "m8r2_pounce_d500": -15.0, "bp_ash_att": 2.86, "bp_ash_hold_att": 2.86, "b_ash_600": 5.71, "b_ash_1200": 2.86, "b_ash_2000": 1.72, "b_loba_drop_t07": -15.0,
                  "b_loba_drop_t09": -15.0, "b_loba_drop_t12": -15.0, "b_loba_drop_t15": -15.0, "b_loba_sprint_t09": -15.0, "g1_rel_tac": -10.0, "g1_rel_attack": -10.0, "g1_hold": -10.0, "g3_hook": -9.09, "g3_hook_use": -9.09,
                  "z7b_air": -15.0, "z7c_air_hold": -15.0, "z2_jump_pu30": -30.0, "z2_jump_pd30": 30.0, "m55_nomod_hold": -10.0, "m4_grapple_hold": -10.0, "m4_grapple_jump": -10.0, "m4_grapple_fwd": -10.0,
                  "m4_grapple_near": -10.0, "m4_grapple_far": -10.0, "m4_grapple_p0": 0.0, "m4_grapple_p20": -20.0,
                  "m4b_swing_side": -10.0, "m4b_swing_turn": -10.0, "m4b_swing_turn_w": -10.0, "m4b_swing_jump": -10.0,
                  "m4b_swing_turn_jump": -10.0, "m4b_swing_cross": -10.0, "m4b_swing_cross_w": -10.0,
                  "m4b_swing_cross_walk": -10.0, "m4_loba_tele": -15.0, "m4_loba_tele_still": -15.0}

# Server snippets run inside the reset (after the teleport, inside try/catch) for prop-based abilities.
# Every spawned prop gets the script name hsd_test_geo; the previous one is removed first.
_CLEAR_GEO = 'foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo_m4" ) ) e.Destroy()\n'
SCHEDULE_PRE = {
    ("m4_pad_", "m4b_pad_"): _CLEAR_GEO + 'entity pad = JumpPad_CreateAtLocation( o + <300, 0, 0>, <0, 0, 0>, p, true )\n'
               'if ( IsValid( pad ) ) pad.SetScriptName( "hsd_test_geo_m4" )\npre = " pad=" + IsValid( pad )\n',
    # view trials run on lane C after pad trials: remove a pad left from an earlier trial (M4b: one was run into)
    "m4b_view": _CLEAR_GEO + 'pre = " geo=cleared"\n',
    # runs after the refill: remove the range-doubling dev mod from the grapple
    "m55_nomod": 'entity gw = p.GetOffhandWeapon( OFFHAND_TACTICAL )\n'
                 'if ( IsValid( gw ) && gw.HasMod( "infinite_abilities_grapple" ) ) gw.RemoveMod( "infinite_abilities_grapple" )\n'
                 'pre = " grapple_mod=" + ( IsValid( gw ) && gw.HasMod( "infinite_abilities_grapple" ) )\n',
    "m4_lift_": 'thread SpaceElevator_PropDeploy( p, o + <120, 0, 0>, <0, 0, 0>, null )\npre = " lift=deployed"\n',
    # M8: pad double jump (pad 300 u ahead, as M4) and its no-pad control
    "m8_pad": _CLEAR_GEO + 'entity pad = JumpPad_CreateAtLocation( o + <300, 0, 0>, <0, 0, 0>, p, true )\n'
              'if ( IsValid( pad ) ) pad.SetScriptName( "hsd_test_geo_m4" )\npre = " pad=" + IsValid( pad )\n',
    "m8_djctrl": _CLEAR_GEO + 'pre = " geo=cleared"\n',
    # lift offset sideways by 80 / 83 u so a W-held walk crosses only a chord of the trigger (dwell < 0.5 s)
    "m8_liftoff80": 'thread SpaceElevator_PropDeploy( p, o + <120, 80, 0>, <0, 0, 0>, null )\npre = " lift=deployed_y80"\n',
    "m8_liftoff83": 'thread SpaceElevator_PropDeploy( p, o + <120, 83, 0>, <0, 0, 0>, null )\npre = " lift=deployed_y83"\n',
    "m8_lift": 'thread SpaceElevator_PropDeploy( p, o + <120, 0, 0>, <0, 0, 0>, null )\npre = " lift=deployed"\n',
}

# M8 R2 jet-drive targets (_r2_jd_pre above)
for _d in (400, 800, 1200):
    SCHEDULE_PRE["m8r2_jd_d%d" % _d] = _r2_jd_pre(_d)
# N4-D (rea-native ledger L-10): lurch high-speed cutoff. Once the player leaves the ground after the jump, the dedi sets
# the horizontal speed along +x (the view) to S; a D press 0.125 s after the jump should lurch only if S <= 1100
# (jump_grace_cutoff_speed, S21 client). The thread logs the set speed.
def _n4d_cut_pre(s):
    return ("void functionref() cutf = void function() : ( p ) {\n"
            "\ttry {\n"
            "\t\tfloat t0 = Time()\n"
            "\t\twhile ( p.IsOnGround() && Time() - t0 < 3.0 ) WaitFrame()\n"
            "\t\tvector v = p.GetVelocity()\n"
            "\t\tp.SetVelocity( <%.1f, 0, v.z> )\n"
            "\t\tprintt( \"[N4D-CUT] set t=\" + Time() + \" s=%.1f vz=\" + v.z )\n"
            "\t} catch ( cErr ) { printt( \"[N4D-CUT] error \" + string( cErr ) ) }\n"
            "}\n"
            "thread cutf()\n"
            "pre = \" cut=%.0f\"\n") % (s, s, s)


for _s in (1000, 1090, 1110, 1200):
    SCHEDULE_PRE["n4d_cut%d" % _s] = _n4d_cut_pre(_s)
    SCHEDULES["n4d_cut%d" % _s] = "wait 72; tap jump; wait 18; tap moveright; wait 216"
# C3 (rea-native camera feel): frame-by-frame camera capture with the HSD.MoveDiag camera tokens.
# Drops: the player is lifted by H after the reset and falls (landing view kick vs fall speed; ducked x0.2).
for _h in (96, 160, 400):
    SCHEDULE_PRE["c3_drop%d" % _h] = "p.SetOrigin( p.GetOrigin() + <0, 0, %d> )\npre = \" drop=%d\"\n" % (_h, _h)
    SCHEDULES["c3_drop%d" % _h] = "wait 216"
# 900 u drops land ~1.55 s after the reset, after the schedule has started, so the duck is held at the landing.
for _n, _steps in (("c3_drop900", "wait 288"), ("c3_drop900_duck", "down duck; wait 288; up duck; wait 72")):
    SCHEDULE_PRE[_n] = "p.SetOrigin( p.GetOrigin() + <0, 0, 900> )\npre = \" drop=900\"\n"
    SCHEDULES[_n] = _steps
# The runner's settle waits for the ground, so a teleport drop always lands before the schedule starts. The ducked
# landing is measured on a standing jump instead: duck pressed in the air, held through the landing.
SCHEDULES["c3_jumpland"] = "wait 72; tap jump; wait 216"
SCHEDULES["c3_jumpland_duck"] = "wait 72; tap jump; waitair; wait 12; down duck; wait 216; up duck; wait 72"
# N6 camera: sprint tilt (sprint + view turn at 90 / 180 deg/s) and strafe roll (sv_rollangle 0: expect none)
SCHEDULES["n6_sprint_turn90"] = "set cl_yawspeed 90; wait 72; down speed; down forward; wait 1.0s; down right; wait 1.0s; up right; wait 0.6s; up forward; up speed; wait 0.5s"
SCHEDULES["n6_sprint_turn180"] = "set cl_yawspeed 180; wait 72; down speed; down forward; wait 1.0s; down right; wait 1.0s; up right; wait 0.6s; up forward; up speed; wait 0.5s"
SCHEDULES["n6_walk_turn90"] = "set cl_yawspeed 90; wait 72; down forward; wait 1.0s; down right; wait 1.0s; up right; wait 0.6s; up forward; wait 0.5s"
SCHEDULES["n6_strafe"] = "wait 72; down moveright; wait 1.0s; up moveright; wait 0.3s; down moveleft; wait 1.0s; up moveleft; wait 0.5s"
SCHEDULE_PRE["c3_drop400_duck"] = "p.SetOrigin( p.GetOrigin() + <0, 0, 400> )\npre = \" drop=400 duck\"\n"
SCHEDULES["c3_drop400_duck"] = "down duck; wait 216; up duck; wait 72"
# Slides: straight (eye sink, no tilt) and with the view turned ~30 deg right during the slide (tilt).
SCHEDULES["c3_slide_straight"] = "wait 72; down speed; down forward; wait 288; down duck; wait 10; up forward; up speed; wait 288; up duck; wait 144"
SCHEDULES["c3_slide_turn"] = ("set cl_yawspeed 90; wait 72; down speed; down forward; wait 288; down duck; wait 10; up forward; up speed; "
                              "down right; wait 48; up right; wait 240; up duck; wait 144")
SCHEDULE_PRE["m8r2_jd_d800_mvy"] = _r2_jd_pre(800, "tg.NonPhysicsMoveTo( tg.GetOrigin() + <0, 300, 0>, 1.0, 0.0, 0.0 )")
SCHEDULE_PRE["m8r2_jd_d800_mvx"] = _r2_jd_pre(800, "tg.NonPhysicsMoveTo( tg.GetOrigin() + <600, 0, 0>, 1.5, 0.0, 0.0 )")
# Echo position log (server, 10 Hz, 9 s) for the real-tactical trials
_R2_ECHO_LOG = r"""
void functionref() ef = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 9.0 ) {
			entity c = VantageCompanion_GetEnt( p )
			printt( "[R2-ECHO] t=" + Time() + " valid=" + IsValid( c ) + " o=" + ( IsValid( c ) ? c.GetOrigin() : <0, 0, 0> ) + " p=" + p.GetOrigin() + " jd=" + p.IsJetDriveActive() )
			WaitFrame()
		}
	} catch ( eErr ) { printt( "[R2-ECHO] error " + string( eErr ) ) }
}
thread ef()
pre = " echo_log=1"
"""
SCHEDULE_PRE["m8r2_echo"] = _R2_ECHO_LOG
# SCHEDULE_PRE is matched by prefix in insertion order: the exact moving-target keys must win over "m8r2_jd_d800"
for _k in ("m8r2_jd_d800_mvy", "m8r2_jd_d800_mvx"):
    SCHEDULE_PRE = {_k: SCHEDULE_PRE.pop(_k), **SCHEDULE_PRE}

# M6-A3 ropes on the clear lanes (m6/SOURCE-AUDIT.md E-Z): Z1 flat 1600 u on lane C 100 u above the floor, Z2 uphill
# 1600 u (+300 u) at y 6350, Z3 vertical 800 u at (-14700, 6500). CreateZipline picks vertical above |dir.z| 0.7.
ZIP_SERVER = r'''
string out = ""
try
{
	foreach ( entity e in GetEntArrayByScriptName( "hsd_zip" ) ) e.Destroy()
	array<entity> all
	all.extend( CreateZipline( <-14600, 6800, 394.92>, <-13000, 6800, 394.92>, false, 100 ) )
	all.extend( CreateZipline( <-14500, 6350, 394.92>, <-12900, 6350, 694.92>, false, 100 ) )
	all.extend( CreateZipline( <-14700, 6500, 314.92>, <-14700, 6500, 1114.92> ) )
	foreach ( entity e in all ) e.SetScriptName( "hsd_zip" )
	out = "zip_ents=" + all.len()
}
catch ( err ) { out = "error=" + string( err ) }
AgentLink_Reply( out )
'''
# every zipline schedule starts off the rope (never destroy a rope that is being ridden)
_ZIP_RESET = 'if ( p.IsZiplining() ) p.Zipline_Stop()\npre = " zip=" + p.IsZiplining()\n'
SCHEDULE_PRE["z_"] = _ZIP_RESET
SCHEDULE_PRE["g3_"] = _ZIP_RESET

# Facing so that the schedule's ground motion runs along +X (Source yaw: 0 = +X, 90 = +Y; right = (sin, -cos)).
SCHEDULE_YAW = {"n4b_wd": 45.0, "n4b_wwd": 45.0, "n4b_ad": 90.0, "g3_hook": 36.87, "g3_hook_use": 36.87, "z7b_air": 90.0, "z7c_air_hold": 90.0, "z7_air": 90.0, "e1_side": 90.0, "e1_back": 180.0, "e1_diag": 45.0,
                "m4b_swing_side": 20.0, "m4b_swing_turn": 20.0, "m4b_swing_turn_w": 20.0, "m4b_swing_jump": 20.0,
                "m4b_swing_turn_jump": 20.0, "m4b_swing_cross": 90.0, "m4b_swing_cross_w": 90.0, "m4b_swing_cross_walk": 90.0}

# M8 superglide approaches with a turned view (prefix of 9 characters)
M8_YAW_PREFIX = {"m8_sg_ang": 30.0, "m8_sg_wd_": 45.0}

# Start positions per schedule prefix (M3). Lane A faces the test wall (test_geometry.py: rock face at
# x ~ -13706, y 6380..6620, top ~ +232 u); lane B is the open part of the field at y 5900.
LANE_A = (-14100.0, 6500.0, 294.92)
LANE_B = (-14200.0, 5900.0, 294.92)
# Lane C: y 6800 is flat from x -14825 to -12475 (m3/map/field_fine.json) and 81 u clear of the wall's bounds.
LANE_C = (-14800.0, 6800.0, 294.92)
SPAWN_PAD = (-11699.0, 512.0, 1577.046)  # visible firing-range floor (M0/M1)
SCHEDULE_ORIGIN_PREFIX = {"m8r2_climb": LANE_A, "m8r2_spw": LANE_A, "m8r2_jumpin": (-13878.0, 6500.0, 294.92), "m8r2_jd_": LANE_C, "m8r2_echo": LANE_C, "m8_slope": (-10900.0, 550.0, 1580.03), "m8_lurch_ledge": (-13640.0, 6500.0, 532.80), "m8_lurch_sj": LANE_C, "m8_lurch": LANE_B, "m8_sg_ang": (-14100.0, 6272.0, 294.92), "m8_sg_slide": (-14200.0, 6500.0, 294.92), "m8_sg_": LANE_A, "m8_pad": LANE_C, "m8_djctrl": LANE_C, "m8_lift": LANE_C, "b_alter_stand": (-13856.0, 6500.0, 294.92), "bp_alter": (-13856.0, 6500.0, 294.92), "bp_ash": (-14900.0, 6650.0, 294.92), "b_alter_": (-14306.0, 6500.0, 294.92),
                          "b_loba_": (-14900.0, 6650.0, 294.92), "b_ash_": (-14900.0, 6650.0, 294.92), "b_valk_": LANE_C, "a2r_": LANE_A, "g1_": LANE_A, "a2_": LANE_A, "z": (-14550.0, 6800.0, 294.92), "a1_wb": LANE_A, "a1_": LANE_B, "m4b_view": LANE_C, "m4b_pad": LANE_C, "m4_valk": LANE_C, "m4_pounce": LANE_C, "m4_stim": LANE_C, "m4_ctrl": LANE_C, "m4_pad": LANE_C, "m4_lift": LANE_C,
                          "m4_grapple": LANE_A, "x_pad_": SPAWN_PAD, "e8_hop350": LANE_C, "e3_": LANE_B, "e8_fast": LANE_C, "e8_slide": LANE_C, "e6_": LANE_A, "e7_": LANE_A,
                          "e8_drop": LANE_A}


# M6-A3: under rope Z1 (y 6800) with lateral offsets toward -Y; uphill rope Z2 at y 6350; beside the vertical rope Z3
_Z1 = (-14550.0, 6800.0, 294.92)
SCHEDULE_ZIP_ORIGIN = {"z0_off40": (-14550.0, 6760.0, 294.92), "z0_off80": (-14550.0, 6720.0, 294.92),
                       "z0_off120": (-14550.0, 6680.0, 294.92), "z0_off160": (-14550.0, 6640.0, 294.92),
                       "z6_up": (-14450.0, 6350.0, 294.92), "z6_vert": (-14740.0, 6500.0, 294.92),
                       "z7_air": (-14550.0, 6600.0, 294.92),
                       "z7b_air": (-14550.0, 6680.0, 294.92), "z7c_air_hold": (-14550.0, 6680.0, 294.92),
                       "z6_vert_turn": (-14740.0, 6500.0, 294.92),
                       "g3_hook": (-14000.0, 6650.0, 294.92), "g3_hook_use": (-14000.0, 6650.0, 294.92)}

# Exact-name origins take precedence over prefixes (grapple distance variants on lane A).
SCHEDULE_ORIGIN = {"m8r2_pounce_d150": (-13878.0, 6500.0, 294.92), "m8r2_pounce_d500": (-14228.0, 6500.0, 294.92), "m4_grapple_near": (-13950.0, 6500.0, 294.92), "m4_grapple_far": (-14400.0, 6500.0, 294.92)}
# M4b swing: lane A shifted 150 u to -Y (the wall spans y 6279..6719, so a 20 deg aim hits it near y 6493)
SCHEDULE_ORIGIN.update({n: (-14100.0, 6350.0, 294.92) for n in ("m4b_swing_side", "m4b_swing_turn", "m4b_swing_turn_w",
                                                                  "m4b_swing_jump", "m4b_swing_turn_jump")})
# P3: the longest clear lane of the field scan (y 6650, x -14925..-12550, m3/map/field_fine.json)
SCHEDULE_ORIGIN.update({n: (-14900.0, 6650.0, 294.92) for n in ("m4_wraith_void", "m4_wraith_ctrl", "m4_loba_tele",
                                                                  "m4_loba_tele_still")})
# M5.5 range check: horizontal distance from the start to the wall face (pitch 0, so it is also the aim-ray distance)
SCHEDULE_ORIGIN.update({"m55_range_d%d" % d: (-13706.0 - d, 6500.0, 294.92) for d in (800, 840, 860, 900, 950, 1000, 1050, 1100, 1200)})
SCHEDULE_ORIGIN.update({"m55_nomod_d%d" % d: (-13706.0 - d, 6500.0, 294.92) for d in (800, 810, 820, 830, 840, 860, 900)})
SCHEDULE_ORIGIN["m55_nomod_hold"] = (-14100.0, 6500.0, 294.92)  # = LANE_A, the M4 m4_grapple_hold start
# round 2 starts 450 u to -Y of the wall centre, running along +Y
SCHEDULE_ORIGIN.update({n: (-14100.0, 6050.0, 294.92) for n in ("m4b_swing_cross", "m4b_swing_cross_w", "m4b_swing_cross_walk")})


# ---- M9 track R (m9/M9-PLAN.md) ① zipline A1: mid-rope / end mounts, direction, air mounts, re-mounts.
# Geometry m9zip: four flat ropes (rope height above the field floor 100 / 130 / 170 / 80; 130 = the HSD-Unity map ropes) and
# one sloped rope (60 -> 260 u, start = low end), 300 u apart so only one rope is within the 130 u Find radius. m9zipv: one
# vertical rope 84 u in front of the lane-A rock face (geometry m3, top 232 u), floor+20 .. floor+900.
FLOOR_Z = 294.92
M9_ROPES = {  # name: (y, x0, h0 above the floor, x1, h1)
    "r100": (6800.0, -14600.0, 100.0, -13000.0, 100.0),
    "r130": (6500.0, -14600.0, 130.0, -13000.0, 130.0),
    "sl": (6200.0, -14600.0, 60.0, -13000.0, 260.0),
    "r170": (5900.0, -14400.0, 170.0, -12900.0, 170.0),
    "r80": (5600.0, -14000.0, 80.0, -13000.0, 80.0),
    # added after session zipA (track D spec R-16: rope 200 / 240 u above the origin); session zipA ran without them
    "r200": (7100.0, -13450.0, 200.0, -12450.0, 200.0),
    "r240": (7300.0, -13150.0, 240.0, -12150.0, 240.0),
}
M9_VROPE = (-13790.0, 6500.0, 20.0, 900.0)  # x, y, bottom / top above the floor
M9_ZIP_SERVER = r'''
string out = ""
try
{
	foreach ( entity e in GetEntArrayByScriptName( "hsd_zip" ) ) e.Destroy()
	array<entity> all
%s
	foreach ( entity e in all ) e.SetScriptName( "hsd_zip" )
	out = "zip_ents=" + all.len()
}
catch ( err ) { out = "error=" + string( err ) }
AgentLink_Reply( out )
'''
M9_ZIP_LINES = "\n".join("\tall.extend( CreateZipline( <%.2f, %.2f, %.2f>, <%.2f, %.2f, %.2f>, false, 100 ) )"
                         % (x0, y, FLOOR_Z + h0, x1, y, FLOOR_Z + h1) for (y, x0, h0, x1, h1) in M9_ROPES.values())
M9_ZIPV_LINES = "\tall.extend( CreateZipline( <%.2f, %.2f, %.2f>, <%.2f, %.2f, %.2f> ) )" % (
    M9_VROPE[0], M9_VROPE[1], FLOOR_Z + M9_VROPE[2], M9_VROPE[0], M9_VROPE[1], FLOOR_Z + M9_VROPE[3])
M9_EYE = 60.0  # standing eye height used to aim at the rope ('to' views)


def _m9_pos_x(rope, pos):
    y, x0, h0, x1, h1 = M9_ROPES[rope]
    L = x1 - x0
    if pos.startswith("s"):
        return x0 + float(pos[1:])
    if pos.startswith("e"):
        return x1 - float(pos[1:])
    if pos.startswith("b"):
        return x0 - float(pos[1:])
    if pos.startswith("p"):
        return x0 + L * float(pos[1:]) / 100.0
    raise ValueError(pos)


def _m9_rope_h(rope, x):
    y, x0, h0, x1, h1 = M9_ROPES[rope]
    f = min(1.0, max(0.0, (x - x0) / (x1 - x0)))
    return h0 + f * (h1 - h0)


def _m9_view(rope, x, lat, view):
    """(yaw, pitch) for a standing-mount view name. Offsets are toward -Y, so 'toward the rope' is yaw 90."""
    h = _m9_rope_h(rope, x)
    if view == "fx":
        return 0.0, 0.0
    if view == "bx":
        return 180.0, 0.0
    if view == "aw":
        return 270.0, 0.0
    if view == "tp":
        return 90.0, 0.0
    if view == "up":
        return 0.0, -89.0
    m = re.fullmatch(r"y(\d+)", view)
    if m:
        return float(m.group(1)), 0.0
    m = re.fullmatch(r"y(\d+)u(\d+)", view)     # yaw Y, looking up by U deg
    if m:
        return float(m.group(1)), -float(m.group(2))
    m = re.fullmatch(r"fp(\d+)", view)          # along +X, looking up by N deg
    if m:
        return 0.0, -float(m.group(1))
    m = re.fullmatch(r"to(\d*)", view)            # yaw N (default 90), pitch so the eye ray meets the rope line
    if m:
        yaw = float(m.group(1) or 90)
        dist = lat / max(1e-6, math.sin(math.radians(yaw)))
        return yaw, -math.degrees(math.atan2(h - M9_EYE, dist))
    raise ValueError(view)


_M9_STAND = "wait 72; tap use; wait 2.5s"
M9_STAND_RE = re.compile(r"m9z_(r100|r130|sl|r170|r80|r200|r240)_([sepb]\d+)_l(\d+)_(\w+)")


def _m9_stand_setup(name):
    m = M9_STAND_RE.fullmatch(name)
    if not m:
        return None
    rope, pos, lat, view = m.group(1), m.group(2), float(m.group(3)), m.group(4)
    x = _m9_pos_x(rope, pos)
    y = M9_ROPES[rope][0] - lat
    yaw, pitch = _m9_view(rope, x, lat, view)
    return (x, y, FLOOR_Z), yaw, round(pitch, 3)


# dynamic zipline schedules: name -> (rope, pos, lat, view, steps)
_M9ZD = {
    # turn 180 deg during the ride (after the 0.5 s mount state): does the ride direction follow the view?
    "m9zd_turn180": ("r130", "p25", 0, "fx", "set cl_yawspeed 360; wait 72; tap use; wait 0.7s; down right; wait 0.5s; up right; wait 2.0s"),
    # dismount mid-rope (crouch / jump), land, then use again from the ground under the rope
    "m9zd_drop_remount": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap duck; waitland; waitf 6; tap use; wait 2.0s"),
    "m9zd_jump_remount": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitland; waitf 6; tap use; wait 2.0s"),
    # air mounts under / beside the rope (standing jump, use at the apex or rising; use held; jump toward the rope from 80 u)
    "m9zd_air_apex": ("r130", "p50", 0, "fx", "wait 72; tap jump; wait 0.38s; tap use; wait 2.0s"),
    "m9zd_air_rise": ("r130", "p50", 0, "fx", "wait 72; tap jump; wait 0.12s; tap use; wait 2.0s"),
    "m9zd_air_apex100": ("r100", "p50", 0, "fx", "wait 72; tap jump; wait 0.38s; tap use; wait 2.0s"),
    "m9zd_air_hold": ("r130", "p50", 0, "fx", "wait 72; tap jump; waitf 6; down use; wait 0.8s; up use; wait 1.5s"),
    "m9zd_air_l80": ("r130", "p50", 80, "to", "wait 72; down forward; tap jump; wait 0.3s; tap use; wait 0.3s; up forward; wait 1.5s"),
    # jump-off then an air re-mount K frames later; use spam after the jump-off
    "m9zd_jo_remount_k12": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 12; tap use; wait 2.0s"),
    "m9zd_jo_remount_k30": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 30; tap use; wait 2.0s"),
    "m9zd_jo_remount_k46": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 46; tap use; wait 2.0s"),
    "m9zd_jo_spam": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 3; "
                     + "; ".join(["tap use; waitf 3"] * 36) + "; wait 1.5s"),
    # jump-off then use while falling back below the rope height (P = origin + 72 below the rope 0.744..0.917 s after the
    # jump-off from the r130 hang), and 2 frames after it (P still below the rope)
    "m9zd_jo_remount_k2": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 2; tap use; wait 2.0s"),
    "m9zd_jo_remount_k96": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 96; tap use; wait 2.0s"),
    "m9zd_jo_remount_k104": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 104; tap use; wait 2.0s"),
    # crouch-off (drop) then an air re-mount K frames later (P stays below the rope while falling)
    "m9zd_drop_air_k4": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap duck; waitf 4; tap use; wait 2.0s"),
    "m9zd_drop_air_k12": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap duck; waitf 12; tap use; wait 2.0s"),
    "m9zd_drop_air_k24": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap duck; waitf 24; tap use; wait 2.0s"),
    # standing jump under r100 (rope 28 u above P on the ground, 28 u below P at the apex), use at t after the jump press
    **{"m9zd_r100_jair_t%02d" % int(round(t * 100)): ("r100", "p50", 0, "fx", "wait 72; tap jump; wait %.2fs; tap use; wait 2.0s" % t)
       for t in (0.05, 0.12, 0.2, 0.38, 0.6, 0.7)},
    # re-mount budget: ground mount, then crouch-off + air re-mount 4 frames later, four times (r170: hang 90 u above the floor)
    "m9zd_budget_chain": ("r170", "p25", 0, "up", "wait 72; tap use; " + "; ".join(["wait 0.6s; tap duck; waitf 4; tap use"] * 4)
                          + "; wait 1.5s"),
    # super jump from a mid-rope mount (M6 z5b_m3_k2 timing)
    "m9zd_superjump": ("r100", "p50", 0, "fx", "wait 72; tap use; waitf 2; tap jump; waitf 1; tap jump; wait 2.0s"),
    # lurch after a jump-off (D press 3 frames after the jump-off) and its control
    "m9zd_jo_lurch": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; waitf 3; tap moveright; wait 1.5s"),
    "m9zd_jo_ctrl": ("r130", "p25", 0, "fx", "wait 72; tap use; wait 0.8s; tap jump; wait 1.5s"),
    # entry speed: sprint / slide along the rope, then use
    "m9zd_sprint_mount": ("r130", "s50", 0, "fx", "wait 72; down speed; down forward; wait 1.45s; tap use; up forward; up speed; wait 2.0s"),
    "m9zd_slide_mount": ("r130", "s50", 0, "fx", "wait 72; down speed; down forward; wait 1.2s; down duck; wait 0.25s; tap use; up duck; "
                         "up forward; up speed; wait 2.0s"),
}
# track D specs: R-12 carry (sprint across the rope along +Y, use, jump on the next usercmd / 2 later / no jump), R-13 super
# jump second press K = 12..30 after a jump-off at M = 1, R-14 air interact from a standing jump at lateral 20 / 40 / 80 u with
# the view 0 / 45 / 80 deg off the direction to the rope (use at the apex, where origin + 72 is 2 u below the r130 rope)
_M9ZD.update({
    "m9zd_carry_j1": ("r130", "p50", 220, "to", "wait 72; down speed; down forward; wait 0.9s; tap use; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry_j3": ("r130", "p50", 220, "to", "wait 72; down speed; down forward; wait 0.9s; tap use; waitf 1; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry_ride": ("r130", "p50", 220, "to", "wait 72; down speed; down forward; wait 0.9s; tap use; up forward; up speed; wait 2.0s"),
})
_M9ZD.update({"m9zd_sj_k%d" % k: ("r100", "p50", 0, "fx", "wait 72; tap use; waitf 0; tap jump; waitf %d; tap jump; wait 2.0s" % (k - 1))
              for k in (12, 18, 24, 30)})
_M9ZD.update({"m9zd_air_l%d_a%d" % (l, ang): ("r130", "p50", l, "y%d" % (90 - ang), "wait 72; tap jump; wait 0.38s; tap use; wait 2.0s")
              for l in (20, 40, 80) for ang in (0, 45, 80)})
# after session zipB1 (re-mount refused for ~0.33 s after any detach, regardless of height): lockout bracket from a crouch-off
# off r170 (hang 90 u above the floor, airborne ~0.49 s), and the re-grab budget with jump-offs and re-grabs 0.42 s later
_M9ZD.update({"m9zd_lock_t%02d" % int(round(t * 100)): ("r170", "p25", 0, "up", "wait 72; tap use; wait 0.6s; tap duck; wait %.2fs; tap use; wait 2.0s" % t)
              for t in (0.25, 0.30, 0.35, 0.40)})
# budget_jo ran into the rope end on its 4th re-grab; jo2: shorter rides (0.3 s), five re-grabs from p10
_M9ZD["m9zd_budget_jo2"] = ("r130", "p10", 0, "fx", "wait 72; tap use; " + "; ".join(["wait 0.3s; tap jump; wait 0.42s; tap use"] * 5) + "; wait 1.5s")
_M9ZD["m9zd_budget_jo"] = ("r130", "p10", 0, "fx", "wait 72; tap use; " + "; ".join(["wait 0.6s; tap jump; wait 0.42s; tap use"] * 4) + "; wait 1.5s")
# after session zipB2: the carry run never mounted (view too flat at the press) -> view pitch -65 (the rope 58 u above P,
# ~16 u lateral at the press); slide 0/5 -> crouch-standing control and a slide with crouch released one frame before use
_M9ZD.update({
    "m9zd_carry2_j1": ("r130", "p50", 220, "fp65", "wait 72; down speed; down forward; wait 0.9s; tap use; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry2_j3": ("r130", "p50", 220, "fp65", "wait 72; down speed; down forward; wait 0.9s; tap use; waitf 1; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry2_ride": ("r130", "p50", 220, "fp65", "wait 72; down speed; down forward; wait 0.9s; tap use; up forward; up speed; wait 2.0s"),
    "m9zd_crouch_mount": ("r130", "p25", 0, "fx", "wait 72; down duck; wait 0.5s; tap use; wait 0.3s; up duck; wait 2.0s"),
    "m9zd_slide_rel_mount": ("r130", "s50", 0, "fx", "wait 72; down speed; down forward; wait 1.2s; down duck; wait 0.25s; up duck; tap use; "
                             "up forward; up speed; wait 2.0s"),
})
# carry2 used the wrong view (fp65 = along +X); carry3: yaw 90 (running across the rope), 65 deg up. Crouched mounts with the
# view 45 deg up (separates a crouch block from the lower search point of the crouched hull)
_M9ZD.update({
    "m9zd_carry3_j1": ("r130", "p50", 220, "y90u65", "wait 72; down speed; down forward; wait 0.9s; tap use; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry3_j3": ("r130", "p50", 220, "y90u65", "wait 72; down speed; down forward; wait 0.9s; tap use; waitf 1; tap jump; up forward; up speed; wait 2.0s"),
    "m9zd_carry3_ride": ("r130", "p50", 220, "y90u65", "wait 72; down speed; down forward; wait 0.9s; tap use; up forward; up speed; wait 2.0s"),
    "m9zd_crouch_mount_up": ("r130", "p25", 0, "y0u45", "wait 72; down duck; wait 0.5s; tap use; wait 0.3s; up duck; wait 2.0s"),
    "m9zd_slide_mount_up": ("r130", "s50", 0, "y0u45", "wait 72; down speed; down forward; wait 1.2s; down duck; wait 0.25s; tap use; up duck; "
                            "up forward; up speed; wait 2.0s"),
})
# N6 camera: zipline roll. After the 0.5 s mount state the view turns off the rope by 30 / 60 deg (cl_yawspeed 60 / 120 for 0.5 s)
_M9ZD["m9zd_n6roll30"] = ("r130", "p25", 0, "fx", "set cl_yawspeed 60; wait 72; tap use; wait 0.7s; down right; wait 0.5s; up right; wait 1.5s")
_M9ZD["m9zd_n6roll60"] = ("r130", "p25", 0, "fx", "set cl_yawspeed 120; wait 72; tap use; wait 0.7s; down right; wait 0.5s; up right; wait 1.5s")
for _n, (_rope, _pos, _lat, _view, _steps) in _M9ZD.items():
    SCHEDULES[_n] = _steps
    _x = _m9_pos_x(_rope, _pos)
    SCHEDULE_ORIGIN[_n] = (_x, M9_ROPES[_rope][0] - _lat, FLOOR_Z)
    _yw, _pt = _m9_view(_rope, _x, _lat, _view)
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = round(_pt, 3)

# vertical rope (geometry m3,m9zipv): floor start 70 u in front of the rope facing it (+X); ledge start on the rock top
# 110 u behind the rope facing it (yaw 180)
M9_V_FLOOR = (-13860.0, 6500.0, FLOOR_Z)
M9_V_LEDGE = (-13680.0, 6500.0, 532.80)
_M9ZV = {  # name: (start, yaw, pitch, steps)
    "m9zv_floor_p0": (M9_V_FLOOR, 0.0, 0.0, "wait 72; tap use; wait 3.0s"),
    "m9zv_floor_dn": (M9_V_FLOOR, 0.0, 60.0, "wait 72; tap use; wait 3.0s"),
    "m9zv_ledge_p0": (M9_V_LEDGE, 180.0, 0.0, "wait 72; tap use; wait 3.0s"),
    "m9zv_ledge_up": (M9_V_LEDGE, 180.0, -30.0, "wait 72; tap use; wait 3.0s"),
    "m9zv_ledge_dn": (M9_V_LEDGE, 180.0, 30.0, "wait 72; tap use; wait 3.0s"),
    "m9zv_ledge_turn": (M9_V_LEDGE, 180.0, -30.0, "set cl_pitchspeed 180; wait 72; tap use; wait 0.4s; down lookdown; wait 0.5s; "
                        "up lookdown; wait 2.5s"),
    "m9zv_ledge_turn_up": (M9_V_LEDGE, 180.0, 30.0, "set cl_pitchspeed 180; wait 72; tap use; wait 0.4s; down lookup; wait 0.5s; "
                           "up lookup; wait 2.5s"),
    "m9zv_floor_air": (M9_V_FLOOR, 0.0, 0.0, "wait 72; tap jump; wait 0.38s; tap use; wait 3.0s"),
    "m9zv_ledge_air": (M9_V_LEDGE, 180.0, 0.0, "wait 72; down forward; tap jump; wait 0.3s; tap use; up forward; wait 3.0s"),
    "m9zv_jumpoff": (M9_V_FLOOR, 0.0, 0.0, "wait 72; tap use; wait 0.8s; tap jump; wait 2.0s"),
    "m9zv_jo_remount": (M9_V_FLOOR, 0.0, 0.0, "wait 72; tap use; wait 0.8s; tap jump; waitf 12; tap use; wait 2.0s"),
}
for _n, (_o, _yw, _pt, _steps) in _M9ZV.items():
    SCHEDULES[_n] = _steps
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
SCHEDULE_PRE["m9z"] = _ZIP_RESET   # m9z_, m9zd_, m9zv_

# ---- M9 track R ② Revenant (legend revenant --kit). Pounce grid on lane C (pitch: Source convention, + = down; m30 = 30 up):
# m9r_p<pitch>_c<tap|mid|full>_<st|sp|sl>: tap = 1-frame press (launch at the 0.9 s pull-out end), mid = 1.55 s hold
# (c = 0.5), full = 2.3 s hold (c = 1); st = standing, sp = sprinting (W + sprint held through the launch), sl = sliding
# (sprint 1 s, crouch, then the press while sliding, crouch held).
_M9R_CHARGE = {"tap": "tap offhand1", "mid": "down offhand1; wait 1.55s; up offhand1", "full": "down offhand1; wait 2.3s; up offhand1"}
_M9R_START = {
    "st": "wait 72; %s; wait 3.0s",
    "sp": "wait 72; down speed; down forward; wait 1.0s; %s; wait 1.0s; up forward; up speed; wait 2.0s",
    "sl": "wait 72; down speed; down forward; wait 1.0s; down duck; wait 0.1s; up forward; up speed; %s; wait 1.0s; up duck; wait 2.0s",
}
_M9R_PITCH = {"m30": -30.0, "0": 0.0, "20": 20.0, "45": 45.0, "70": 70.0}
for _p, _pv in _M9R_PITCH.items():
    for _c, _cs in _M9R_CHARGE.items():
        for _st, _ss in _M9R_START.items():
            _n = "m9r_p%s_c%s_%s" % (_p, _c, _st)
            SCHEDULES[_n] = _ss % _cs
            SCHEDULE_ORIGIN[_n] = LANE_C
            SCHEDULE_PITCH[_n] = _pv
# track D R-19 extra pitches (full charge, standing) and R-18 pounce tap strafe: hold tactical 1.0 / 2.5 s, jump edge while
# holding, release on the next frame, D held, then W edges every 2 frames x 10 while turning right at 360 deg/s (and controls)
for _p, _pv in (("m15", -15.0), ("10", 10.0), ("25", 25.0)):
    _n = "m9r_p%s_cfull_st" % _p
    SCHEDULES[_n] = _M9R_START["st"] % _M9R_CHARGE["full"]
    SCHEDULE_ORIGIN[_n] = LANE_C
    SCHEDULE_PITCH[_n] = _pv
_M9R_TS = "set cl_yawspeed 360; wait 72; down offhand1; wait %.1fs; tap jump; up offhand1; down moveright; waitf 2; down right; %s; up right; up moveright; wait 2.0s"
for _h in (1.0, 2.5):
    for _v, _taps in (("ts", "; ".join(["tap forward; waitf 1"] * 10)), ("turn", "waitf 20")):
        _n = "m9r_%s_h%02d" % (_v, int(_h * 10))
        SCHEDULES[_n] = _M9R_TS % (_h, _taps)
        SCHEDULE_ORIGIN[_n] = LANE_C
# pull-out / cancel / air press / lurch after the launch (lane C, pitch 0)
_M9R_LANEC = {
    "m9r_rel05": "wait 72; down offhand1; wait 0.5s; up offhand1; wait 3.0s",
    "m9r_cancel_zoom": "wait 72; down offhand1; wait 1.2s; tap zoom; wait 0.3s; up offhand1; wait 3.0s",
    "m9r_cancel_attack": "wait 72; down offhand1; wait 1.2s; tap attack; wait 0.3s; up offhand1; wait 3.0s",
    "m9r_cancel_jump": "wait 72; down offhand1; wait 1.2s; tap jump; wait 0.3s; up offhand1; wait 3.0s",
    "m9r_air": "wait 72; tap jump; waitf 10; tap offhand1; wait 3.0s",
    "m9r_lurch_k3": "wait 72; tap offhand1; waitair; waitf 3; tap moveright; wait 2.5s",
    "m9r_lurch_k36": "wait 72; tap offhand1; waitair; waitf 36; tap moveright; wait 2.5s",
    "m9r_lurch_ctrl": "wait 72; tap offhand1; waitair; wait 2.5s",
}
for _n, _s in _M9R_LANEC.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = LANE_C
# pounce into the lane-A face (geometry m3 / h<H>): tap from 150 u (pitch 0), full charge from 300 u; a jump press at the
# face inside the 0.75 s climb lock (wall bounce?) and its no-pounce control (jump into the face, then jump)
_M9R_FACE = {
    "m9r_wall_tap_d150": ((-13878.0, 6500.0, FLOOR_Z), 0.0, "wait 72; tap offhand1; wait 3.0s"),
    "m9r_wall_full_d300": ((-14028.0, 6500.0, FLOOR_Z), 0.0, "wait 72; down offhand1; wait 2.3s; up offhand1; wait 3.0s"),
    "m9r_wall_w_d150": ((-13878.0, 6500.0, FLOOR_Z), 0.0, "wait 72; tap offhand1; wait 0.95s; down forward; wait 4.0s; up forward; wait 1.0s"),
    "m9r_wall_bounce_lock": ((-13878.0, 6500.0, FLOOR_Z), 0.0, "wait 72; tap offhand1; waitair; wait 0.38s; tap jump; wait 2.5s"),
    "m9r_wall_bounce_ctrl": ((-13878.0, 6500.0, FLOOR_Z), 0.0, "wait 72; down forward; wait 0.3s; tap jump; wait 0.35s; up forward; "
                             "tap jump; wait 2.5s"),
    # ledge pounce looking down past the rock edge (ground-check trace misses): rock top, facing -X
    "m9r_ledge_p45": ((-13690.0, 6500.0, 780.80), 45.0, "wait 72; tap offhand1; wait 3.0s"),
    "m9r_ledge_p70": ((-13690.0, 6500.0, 780.80), 70.0, "wait 72; tap offhand1; wait 3.0s"),
    # climb on the h480 rock: sideways key while climbing, back key, jump while climbing (W held)
    "m9r_climb_d": (LANE_A, 0.0, "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.5s; down moveright; wait 1.0s; up moveright; "
                    "wait 1.0s; up forward; up speed; wait 1.5s"),
    "m9r_climb_back": (LANE_A, 0.0, "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.8s; up forward; up speed; down backward; "
                       "wait 0.5s; up backward; wait 1.5s"),
    "m9r_climb_jump": (LANE_A, 0.0, "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.8s; tap jump; wait 2.0s; up forward; "
                       "up speed; wait 1.0s"),
    # the tall world face found by the M9 read-only scan (face x -8437 facing -X, ground 2462.6; smooth >= 2360 u by traces):
    # walk-jump into it as m8r2_jumpin_ctrl and hold W 12 s
    "m9r_bigwall_climb": ((-8609.0, 8375.0, 2462.6), 0.0, "wait 72; down forward; wait 0.3s; tap jump; wait 12.0s; up forward; wait 2.0s"),
}
for _n, (_o, _pt, _s) in _M9R_FACE.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_PITCH[_n] = _pt
    if _n.startswith("m9r_ledge"):
        SCHEDULE_YAW[_n] = 180.0  # geometry h480 (rock top z 780.80)


# ---- M9 track R ③ D1 re-checks.
# Uphill slide on the M8 hillside (y ~550 profile from the M8 slope session: z 692.8 at x -9141, rising to 1580 at x -10595);
# start low, facing up the slope (-X)
M9D_HILL = (-9141.0, 501.0, 692.80)
for _n, _s in {"m9d_up_slide": "wait 72; down speed; down forward; wait 1.0s; down duck; wait 2.0s; up duck; up forward; up speed; wait 1.0s",
               "m9d_up_run": "wait 72; down speed; down forward; wait 3.0s; up forward; up speed; wait 1.0s",
               "m9d_up_slide_now": "wait 72; down speed; down forward; wait 0.5s; down duck; wait 2.5s; up duck; up forward; up speed; wait 1.0s"}.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = M9D_HILL
    SCHEDULE_YAW[_n] = 180.0
# SG approach (geometry h120, lane A face x -13706): a slide G s before an ordinary sprint jump (approach speed 299, boost state
# varies), the M8 slide-jump approach again, and track-D R-7a/b sideways (W released, D held during the pull) / backward
# (S held, view 30 deg up during the pull) superglides. The press is K = 61 frames after the traversal start (H120 window).
_M9SG_TAIL = "waittrav; waitf 61; tap jump; tap duck; wait 1.5s; up forward; up speed; wait 1.0s"
for _g, _x in ((0.5, -14190.0), (1.0, -14340.0), (2.0, -14640.0)):
    _n = "m9d_sg_gap%02d" % int(_g * 10)
    SCHEDULES[_n] = ("wait 72; down speed; down forward; wait 0.6s; down duck; wait 0.25s; up duck; wait %.1fs; tap jump; " % _g) + _M9SG_TAIL
    SCHEDULE_ORIGIN[_n] = (_x, 6500.0, FLOOR_Z)
SCHEDULES["m9d_sg_slidejump"] = "wait 72; down speed; down forward; wait 1.05s; down duck; wait 0.25s; tap jump; up duck; " + _M9SG_TAIL
SCHEDULE_ORIGIN["m9d_sg_slidejump"] = (-14200.0, 6500.0, FLOOR_Z)
SCHEDULES["m9d_sg_spr"] = "wait 72; down speed; down forward; wait 1.2s; tap jump; " + _M9SG_TAIL
SCHEDULE_ORIGIN["m9d_sg_spr"] = LANE_A
SCHEDULES["m9d_sg_side"] = ("wait 72; down speed; down forward; wait 1.2s; tap jump; waittrav; waitf 20; up forward; down moveright; waitf 41; "
                            "tap jump; tap duck; wait 1.5s; up moveright; up speed; wait 1.0s")
SCHEDULE_ORIGIN["m9d_sg_side"] = LANE_A
SCHEDULES["m9d_sg_back"] = ("set cl_pitchspeed 300; wait 72; down speed; down forward; wait 1.2s; tap jump; waittrav; waitf 10; down lookup; waitf 12; "
                            "up lookup; up forward; down backward; waitf 39; tap jump; tap duck; wait 1.5s; up backward; up speed; wait 1.0s")
SCHEDULE_ORIGIN["m9d_sg_back"] = LANE_A
# reverse chain (W -> W+D -> D -> S+D -> S, one edge every g frames) at walk / sprint / slide-jump entries (lane B / C)
_M9_ENTRY = {
    "walk": ("wait 72; down forward; wait 1.0s; tap jump; waitf 1; up forward; waitf 2; ", LANE_B),
    "spr": (_A1_JUMP + "waitf 2; ", LANE_B),
    "sj": ("wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; waitf 1; up duck; up forward; up speed; waitf 2; ", LANE_C),
}
for _e, (_pre, _o) in _M9_ENTRY.items():
    for _g in (4, 6):
        _n = "m9d_chain_%s_g%d" % (_e, _g)
        SCHEDULES[_n] = _pre + _m8_chain("moveright", _g) + "; wait 1.0s"
        SCHEDULE_ORIGIN[_n] = _o
# R-5 OG Ras from a walk jump, camera fixed: (i) A, S, D edges; (ii) D, D+S, S edges; spacing 4 / 6 / 10; crouch held from the
# last edge (jump slide on landing)
for _g in (4, 6, 10):
    _i = "tap moveleft; waitf %d; tap backward; waitf %d; tap moveright; waitf %d" % (_g - 1, _g - 1, _g - 1)
    _ii = ("tap moveright; waitf %d; down moveright; down backward; waitf 1; up moveright; up backward; waitf %d; tap backward; waitf %d"
           % (_g - 1, _g - 1, _g - 1))
    for _v, _seq in (("i", _i), ("ii", _ii)):
        _n = "m9d_ras_%s_g%d" % (_v, _g)
        SCHEDULES[_n] = "wait 72; down forward; wait 1.0s; tap jump; waitf 1; up forward; waitf 2; " + _seq + "; down duck; wait 1.2s; up duck; wait 0.3s"
        SCHEDULE_ORIGIN[_n] = LANE_B
# R-4 momentum shift: slide jump, A, S, D edges at +6 / +12 / +18 frames while the view turns left ~90 deg over ~18 frames
SCHEDULES["m9d_mshift"] = ("set cl_yawspeed 300; wait 72; down speed; down forward; wait 2.0s; down duck; wait 86; tap jump; waitf 1; up duck; up forward; "
                           "up speed; down left; waitf 4; tap moveleft; waitf 5; tap backward; waitf 5; tap moveright; waitf 22; up left; wait 1.0s")
SCHEDULE_ORIGIN["m9d_mshift"] = LANE_C
# R-1 lurch combos (a: A+W held from before the jump, D edge at 0.10 s; b: W+S held, D edge at 0.10 s) and R-2 (A+D held, D
# released 2 frames after the jump, A kept, turn left 90 deg/s 0.5 s)
SCHEDULES["m9d_r1a"] = "wait 72; down speed; down forward; down moveleft; wait 1.0s; tap jump; waitf 11; tap moveright; wait 1.2s; up moveleft; up forward; up speed"
SCHEDULES["m9d_r1b"] = "wait 72; down speed; down forward; wait 1.0s; down backward; tap jump; waitf 11; tap moveright; wait 1.2s; up backward; up forward; up speed"
SCHEDULES["m9d_r2"] = ("set cl_yawspeed 90; wait 72; down speed; down forward; wait 1.0s; down moveleft; down moveright; tap jump; waitf 1; up moveright; "
                       "down left; wait 0.5s; up left; wait 0.7s; up moveleft; up forward; up speed")
for _n in ("m9d_r1a", "m9d_r1b", "m9d_r2"):
    SCHEDULE_ORIGIN[_n] = LANE_B
# Octane pad: chain right after the pad launch (pad 300 u ahead on lane C, as M8)
for _g in (4, 6):
    SCHEDULES["m8_pad_chain_g%d" % _g] = _M8P + "waitf 2; " + _m8_chain("moveright", _g) + "; wait 3.0s"


# ---- M9 track R ④ Vantage (legend vantage --kit). Real tactical on lane C: every trial first recalls Echo at the reset
# (ClientCallback_VantageCompanion_Recall, server-global) and waits 3 s for it to perch; the M8 Echo position logger runs at
# 10 Hz. Tap = send Echo along the aim; hold = launch (mp_ability_companion_launch.nut CheckForHoldInput_Thread).
_M9V_PRE = 'ClientCallback_VantageCompanion_Recall( p )\n' + _R2_ECHO_LOG.replace("Time() - t0 < 9.0", "Time() - t0 < 14.0")
_M9V_W = "wait 72; wait 3.0s; "
_M9V = {
    "m9v_send_p0": (LANE_C, 0.0, 0.0, _M9V_W + "tap offhand1; wait 4.0s"),
    "m9v_send_pd10": (LANE_C, 0.0, 10.0, _M9V_W + "tap offhand1; wait 4.0s"),
    "m9v_send_pu20": (LANE_C, 0.0, -20.0, _M9V_W + "tap offhand1; wait 4.0s"),
    "m9v_hold_perched": (LANE_C, 0.0, 0.0, _M9V_W + "down offhand1; wait 1.0s; up offhand1; wait 4.0s"),
    "m9v_launch_h03": (LANE_C, 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.5s; down offhand1; wait 0.3s; up offhand1; wait 5.0s"),
    "m9v_launch_h06": (LANE_C, 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.5s; down offhand1; wait 0.6s; up offhand1; wait 5.0s"),
    "m9v_launch_h10": (LANE_C, 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.5s; down offhand1; wait 1.0s; up offhand1; wait 5.0s"),
    "m9v_launch_h20": (LANE_C, 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.5s; down offhand1; wait 2.0s; up offhand1; wait 5.0s"),
    # track D R-20: view turned 50 / 70 deg away from Echo before the hold (60 deg on-screen gate in the S21 script)
    "m9v_off50": (LANE_C, 0.0, 0.0, "set cl_yawspeed 100; " + _M9V_W + "tap offhand1; wait 2.0s; down left; wait 0.5s; up left; wait 0.3s; "
                  "down offhand1; wait 1.0s; up offhand1; wait 4.0s"),
    "m9v_off70": (LANE_C, 0.0, 0.0, "set cl_yawspeed 100; " + _M9V_W + "tap offhand1; wait 2.0s; down left; wait 0.7s; up left; wait 0.3s; "
                  "down offhand1; wait 1.0s; up offhand1; wait 4.0s"),
    # LOS: send Echo along y 6820 (north of the lane-A rock, geometry m3), then step right (-Y) behind the rock so the eye -> Echo
    # line crosses it; control: stay
    "m9v_los_block": ((-13900.0, 6820.0, FLOOR_Z), 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.0s; down moveright; wait 1.0s; up moveright; wait 0.5s; "
                      "down offhand1; wait 1.0s; up offhand1; wait 4.0s"),
    "m9v_los_clear": ((-13900.0, 6820.0, FLOOR_Z), 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.0s; wait 1.5s; down offhand1; wait 1.0s; up offhand1; wait 4.0s"),
    # distance: send, walk back 3 s (Echo beyond the 40 m base range), hold; control without the walk
    "m9v_far": ((-14300.0, 6800.0, FLOOR_Z), 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.0s; down backward; wait 3.0s; up backward; "
                "down offhand1; wait 1.0s; up offhand1; wait 5.0s"),
    "m9v_far_ctrl": ((-14300.0, 6800.0, FLOOR_Z), 0.0, 0.0, _M9V_W + "tap offhand1; wait 2.0s; wait 3.0s; down offhand1; wait 1.0s; up offhand1; wait 5.0s"),
}
for _n, (_o, _yw, _pt, _s) in _M9V.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
# jet-drive shortcut (M8 _r2_jd_pre, mover 800 u ahead on lane C): end double-jump window edges, lurch after the end jump,
# and a drive into the lane-A rock (mover 900 u ahead behind the face, geometry m3)
_M9VJ = {"m9v_jd_dj%d" % k: (800, LANE_C, _R2JD + "waitf %d; tap jump; wait 4.0s" % k) for k in (70, 80, 100, 130, 145, 160)}
_M9VJ["m9v_jd_dj100_lurch"] = (800, LANE_C, _R2JD + "waitf 100; tap jump; waitf 3; tap moveright; wait 4.0s")
_M9VJ["m9v_jd_wall"] = (900, LANE_A, _R2JD + "wait 4.0s")
_jd_pre = {}
for _n, (_d, _o, _s) in _M9VJ.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    _jd_pre[_n] = _r2_jd_pre(_d)
SCHEDULE_PRE = {**_jd_pre, **SCHEDULE_PRE}
SCHEDULE_PRE["m9v_"] = _M9V_PRE


# ---- M10 track R (m10/M10-PLAN.md). ① Pathfinder grapple (legend pathfinder --kit, --m10-log). Every m10_g* reset starts a
# server logger (_M10_GR_LOG: per server frame the grapple flags, the hook origin and the player state for 6 s); --m10-log
# adds the client per-frame logger (M10_CLIENT). Geometry: m3 (lane-A rock, face x -13706) and m10fly (the same rock floating
# at (-13300, 5900, floor + 700): front face x ~ -13424, underside ~ floor + 450..505, y 5679..6119; probed in the M10 explore
# game). Pitch: Source convention (+ = down).
_M10_GR_LOG = r"""
void functionref() m10gr = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 6.5 && IsValid( p ) ) {
			entity h = p.GetGrappleHook()
			vector ho = IsValid( h ) ? h.GetOrigin() : <0, 0, 0>
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			printt( "[M10-GRS] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%.4f", Time() ) + " act=" + p.IsGrappleActive() + " att=" + p.IsGrappleAttached() + " pull=" + p.IsGrapplePulling() + format( " hook=%.3f,%.3f,%.3f o=%.3f,%.3f,%.3f v=%.3f,%.3f,%.3f eye=%.3f", ho.x, ho.y, ho.z, po.x, po.y, po.z, pv.x, pv.y, pv.z, p.EyePosition().z - po.z ) + " gnd=" + p.IsOnGround() )
			WaitFrame()
		}
	} catch ( grErr ) { printt( "[M10-GRS] error " + string( grErr ) ) }
}
thread m10gr()
pre += " m10_grlog=1"
"""
M10_ROCK = "mdl/rocks/rock_white_chalk_modular_wallrun_02.rmdl"
M10_FLY = (-13300.0, 5900.0, FLOOR_Z + 700.0)   # m10fly rock origin (pitch 0)
_M10G = {}
# detach / RF base on lane A (as M4 near / hold / far; p0 / p20 at the hold distance)
for _n, _x, _pt in (("d250", -13950.0, -10.0), ("d400", -14100.0, -10.0), ("d700", -14400.0, -10.0), ("p0", -14100.0, 0.0),
                    ("p20", -14100.0, -20.0)):
    _M10G["m10_g_" + _n] = ((_x, 6500.0, FLOOR_Z), 0.0, _pt, "wait 72; tap offhand1; wait 3.5s")
_M10GA = ((-14100.0, 6500.0, FLOOR_Z), 0.0, -10.0)    # the M4 hold start
_M10G.update({
    # entry speed: sprint / slide / air (grapple pressed while moving toward the face)
    "m10_g_sprint": ((-14500.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; down speed; down forward; wait 1.0s; tap offhand1; up forward; up speed; wait 3.5s"),
    "m10_g_slide": ((-14500.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; down speed; down forward; wait 1.0s; down duck; wait 0.15s; up forward; up speed; tap offhand1; wait 1.5s; up duck; wait 2.0s"),
    "m10_g_air": ((-14500.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; down speed; down forward; wait 1.0s; tap jump; up forward; up speed; wait 0.3s; tap offhand1; wait 3.5s"),
    # keys held from the fire
    "m10_g_hold_w": _M10GA + ("wait 72; tap offhand1; down forward; wait 3.0s; up forward; wait 0.5s",),
    "m10_g_hold_s": _M10GA + ("wait 72; tap offhand1; down backward; wait 3.0s; up backward; wait 0.5s",),
    "m10_g_hold_d": _M10GA + ("wait 72; tap offhand1; down moveright; wait 3.0s; up moveright; wait 0.5s",),
    "m10_g_hold_wd": _M10GA + ("wait 72; tap offhand1; down forward; down moveright; wait 3.0s; up forward; up moveright; wait 0.5s",),
    # second tactical press (release) at 0.6 / 0.9 / 1.2 s after the fire from the far start (speed > 460 at 0.9 / 1.2 s)
    "m10_g_rel_t06": ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 0.6s; tap offhand1; wait 3.0s"),
    "m10_g_rel_t09": ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 0.9s; tap offhand1; wait 3.0s"),
    "m10_g_rel_t12": ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 1.2s; tap offhand1; wait 3.0s"),
    # rodeo attempt: sprint along +X past the rock's -Y side face (y ~6280), turn left onto it, fire, hold A and keep turning
    "m10_g_rodeo": ((-14150.0, 6120.0, FLOOR_Z), 0.0, -10.0, "set cl_yawspeed 180; wait 72; down speed; down forward; wait 1.2s; down left; "
                   "wait 0.3s; up left; tap offhand1; up forward; up speed; down moveleft; down left; wait 1.5s; up left; up moveleft; wait 2.0s"),
})
# Jump / drag grapple on lane B (open floor): the hook on the ground 200 / 400 u ahead (pitch 19.3 / 9.9 down from eye 70);
# jump K frames after the attach hop (waitair = the hop makes the player airborne); sprint and slide versions
for _p, _pv in (("g200", 19.29), ("g400", 9.93)):
    _M10G["m10_g_%s" % _p] = (LANE_B, 0.0, _pv, "wait 72; tap offhand1; wait 3.0s")
    for _k in (2, 12, 30):
        _M10G["m10_g_%s_j%d" % (_p, _k)] = (LANE_B, 0.0, _pv, "wait 72; tap offhand1; waitair; waitf %d; tap jump; wait 3.0s" % _k)
_M10G.update({
    "m10_g_g400_spr": (LANE_B, 0.0, 9.93, "wait 72; down speed; down forward; wait 1.0s; tap offhand1; up forward; up speed; wait 3.0s"),
    "m10_g_g400_spr_j2": (LANE_B, 0.0, 9.93, "wait 72; down speed; down forward; wait 1.0s; tap offhand1; up forward; up speed; waitair; waitf 2; tap jump; wait 3.0s"),
    "m10_g_g400_sl": (LANE_B, 0.0, 9.93, "wait 72; down speed; down forward; wait 1.0s; down duck; wait 0.15s; up forward; up speed; tap offhand1; wait 1.5s; up duck; wait 1.5s"),
    "m10_g_g400_sl_j2": (LANE_B, 0.0, 9.93, "wait 72; down speed; down forward; wait 1.0s; down duck; wait 0.15s; up forward; up speed; tap offhand1; waitair; waitf 2; tap jump; wait 1.5s; up duck; wait 1.5s"),
    # control: the same sprint and jump without the grapple
    "m10_g_ctrl_spr_jump": (LANE_B, 0.0, 9.93, "wait 72; down speed; down forward; wait 1.0s; up forward; up speed; wait 0.25s; tap jump; wait 3.0s"),
})
# m10fly: slingshot (hook on the front face ~49 deg up from (-13850, 5900)), overhead pendulum test (sprint under the rock with
# the view pitched up, fire when the ray meets the underside), and the slingshot inputs (turn + strafe at the pull midpoint,
# W + turn, a release press at the midpoint, a sprint entry)
_M10SL = ((-13850.0, 5900.0, FLOOR_Z), 0.0, -49.0)
_M10G.update({
    "m10_g_sl_hold": _M10SL + ("wait 72; tap offhand1; wait 3.5s",),
    "m10_g_sl_turn_d": _M10SL + ("set cl_yawspeed 180; wait 72; tap offhand1; wait 0.9s; down right; down moveright; wait 0.5s; up right; wait 0.5s; up moveright; wait 2.0s",),
    "m10_g_sl_turn_w": _M10SL + ("set cl_yawspeed 180; wait 72; tap offhand1; down forward; wait 0.9s; down right; wait 0.5s; up right; wait 0.5s; up forward; wait 2.0s",),
    "m10_g_sl_rel": _M10SL + ("wait 72; tap offhand1; wait 0.9s; tap offhand1; wait 2.5s",),
    "m10_g_sl_turn_rel": _M10SL + ("set cl_yawspeed 180; wait 72; tap offhand1; wait 0.9s; down right; down moveright; wait 0.3s; tap offhand1; wait 0.2s; up right; wait 0.5s; up moveright; wait 2.0s",),
    "m10_g_sl_spr": ((-14250.0, 5900.0, FLOOR_Z), 0.0, -36.0, "wait 72; down speed; down forward; wait 1.0s; tap offhand1; up forward; up speed; wait 3.5s"),
})
# (explore: a grapple fired on the ground stops a sprint within ~0.25 s, so the overhead test fires in the air: sprint 1.8 s,
# jump, fire 0.2 s later; start so the hook lands on the underside ~100 u (pitch 75) / ~260 u (pitch 55) ahead)
for _p, _x0 in ((75, -13930.0), (55, -14070.0)):
    _M10G["m10_g_over%d_jump" % _p] = ((_x0, 5900.0, FLOOR_Z), 0.0, -float(_p),
                                       "wait 72; down speed; down forward; wait 1.8s; tap jump; up forward; up speed; wait 0.2s; tap offhand1; wait 3.5s")
    _M10G["m10_g_over%d_jump_w" % _p] = ((_x0, 5900.0, FLOOR_Z), 0.0, -float(_p),
                                         "wait 72; down speed; down forward; wait 1.8s; tap jump; up speed; wait 0.2s; tap offhand1; wait 3.5s; up forward")
# track D specs (m10/d_library/TECHNIQUE-LIBRARY-M10.md §6). G-1 Slingshot: from the pull start (~0.5 s after the fire) turn
# the view 80 deg left at 300 deg/s holding W+A, at about half the pull turn back right 90 deg and swap to W+D; 600 u anchor
# (start -13850, pitch -49) and 800 u anchor (start -13989, pitch -45, hook ~floor+635 on the m10fly face); W-only and a
# jump 2 cmds after the attach. G-1b: A / D / S held from the pull start with the view on the anchor.
_G1 = ("set cl_yawspeed 300; wait 72; tap offhand1; wait 0.5s; down left; down forward; down moveleft; wait 0.27s; up left; wait 0.43s; "
       "down right; up moveleft; down moveright; wait 0.3s; up right; wait 1.0s; up forward; up moveright; wait 1.5s")
_M10SL8 = ((-13989.0, 5900.0, FLOOR_Z), 0.0, -45.0)
_M10G.update({
    "m10_g_sl_g1": _M10SL + (_G1,),
    "m10_g_sl8_g1": _M10SL8 + (_G1,),
    "m10_g_sl8_hold": _M10SL8 + ("wait 72; tap offhand1; wait 3.5s",),
    "m10_g_sl8_w": _M10SL8 + ("wait 72; tap offhand1; wait 0.5s; down forward; wait 2.5s; up forward; wait 0.5s",),
    "m10_g_sl8_jump": _M10SL8 + ("wait 72; tap offhand1; waitair; waitf 2; tap jump; wait 3.5s",),
    "m10_g_sl_a": _M10SL + ("wait 72; tap offhand1; wait 0.5s; down moveleft; wait 2.5s; up moveleft; wait 0.5s",),
    "m10_g_sl_d": _M10SL + ("wait 72; tap offhand1; wait 0.5s; down moveright; wait 2.5s; up moveright; wait 0.5s",),
    "m10_g_sl_s": _M10SL + ("wait 72; tap offhand1; wait 0.5s; down backward; wait 2.5s; up backward; wait 0.5s",),
    # G-5 slide grapple (hook on the m10fly front-bottom edge, ~57 deg up from (-13700, 5900)): walk backwards 1 s, jump, hold
    # crouch, fire 2 cmds after the landing (slide) and hold W 0.6 s later; control: fire 0.15 s after the jump (air connect)
    "m10_g_slidegr": ((-13700.0, 5900.0, FLOOR_Z), 0.0, -57.0, "wait 72; down backward; wait 1.0s; tap jump; down duck; waitair; waitland; "
                      "waitf 2; tap offhand1; up backward; wait 0.6s; down forward; wait 1.5s; up forward; up duck; wait 1.0s"),
    "m10_g_slidegr_air": ((-13700.0, 5900.0, FLOOR_Z), 0.0, -57.0, "wait 72; down backward; wait 1.0s; tap jump; down duck; wait 0.15s; "
                          "tap offhand1; up backward; wait 0.6s; down forward; wait 1.5s; up forward; up duck; wait 1.0s"),
})
# G-2 jump grapple: ground hook 700 u ahead (pitch 5.71), jump k cmds after the attach hop; G-2b grapple hop: pitch 89
_M10G["m10_g_g700"] = (LANE_B, 0.0, 5.71, "wait 72; tap offhand1; wait 3.5s")
for _k in (1, 6, 12, 18, 24, 30, 48):
    _M10G["m10_g_g700_j%d" % _k] = (LANE_B, 0.0, 5.71, "wait 72; tap offhand1; waitair; waitf %d; tap jump; wait 3.5s" % _k)
_M10G["m10_g_hop"] = (LANE_B, 0.0, 89.0, "wait 72; tap offhand1; wait 2.5s")
for _k in (0, 1, 2, 4):
    _M10G["m10_g_hop_j%d" % _k] = (LANE_B, 0.0, 89.0, "wait 72; tap offhand1; waitair; " + ("waitf %d; " % _k if _k else "") + "tap jump; wait 2.5s")
_M10G["m10_g_jump_ctrl"] = (LANE_B, 0.0, 0.0, "wait 72; tap jump; wait 2.0s")
# G-3 detach candidates on lane A from the far start: view turned away at 180 deg/s from the pull start; crouch edge at
# pull + 0.3 s; (passing the anchor = g700; tactical = rel_t*)
_M10G["m10_g_look180"] = ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "set cl_yawspeed 180; wait 72; tap offhand1; wait 0.55s; down left; wait 1.0s; up left; wait 2.0s")
_M10G["m10_g_crouch"] = ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 0.85s; tap duck; wait 3.0s")
# G-6 super grapple: aim 30 u over the lane-A rock top from 300 u (miss), jump 0.2 s after the fire / no jump (control)
_M10G["m10_g_super_jump"] = ((-14006.0, 6500.0, FLOOR_Z), 0.0, -32.6, "wait 72; tap offhand1; wait 0.2s; tap jump; wait 3.0s")
_M10G["m10_g_super_none"] = ((-14006.0, 6500.0, FLOOR_Z), 0.0, -32.6, "wait 72; tap offhand1; wait 3.0s")
# G-7 rodeo, D held with the view kept on the fire direction (no turn); G-8 double bounce attempt: wallbounce as M3
# e6_bounce_none_15, tactical 0.25 s after the bounce jump (view on the wall), W pressed 0.5 s later
_M10G["m10_g_rodeo_d"] = ((-14150.0, 6120.0, FLOOR_Z), 0.0, -10.0, "set cl_yawspeed 180; wait 72; down speed; down forward; wait 1.2s; down left; "
                          "wait 0.3s; up left; tap offhand1; up forward; up speed; down moveright; wait 2.0s; up moveright; wait 1.5s")
_M10G["m10_g_dbounce"] = (LANE_A, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 0.43s; up forward; up speed; tap jump; "
                          "wait 0.25s; tap offhand1; wait 0.5s; down forward; wait 2.0s; up forward; wait 1.0s")
# round 2 (after session M10R_g1): the second-press release above the class-var grapple_detachSpeedLossMin 460 (far start,
# 1.6 / 1.8 s after the fire), and one tether / rodeo attempt under the m10fly overhang: the over75 jump with D held and the view
# turning right at 120 deg/s from the fire (an orbit around the vertical through the anchor)
_M10G["m10_g_rel_t16"] = ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 1.6s; tap offhand1; wait 3.0s")
_M10G["m10_g_rel_t18"] = ((-14400.0, 6500.0, FLOOR_Z), 0.0, -10.0, "wait 72; tap offhand1; wait 1.8s; tap offhand1; wait 3.0s")
_M10G["m10_g_tether"] = ((-13930.0, 5900.0, FLOOR_Z), 0.0, -75.0, "set cl_yawspeed 120; wait 72; down speed; down forward; wait 1.8s; tap jump; up forward; "
                         "up speed; wait 0.2s; tap offhand1; down moveright; down right; wait 3.0s; up right; up moveright; wait 0.5s")
# N6 (rea-native P-07): low-speed timeout. Run with --geometry h20 (the rock sunk to a ~33 u ledge, face x -13706). Standing
# against the ledge face, the hook goes over the ledge to the floor ~750-850 u beyond it (pitch 4.0-4.6 deg down), so the rope
# pulls the body into the ledge: speed stays below grapple_detachLowSpeedThreshold 250 and the ground timeout (0.7 s) releases it.
for _p in (4.0, 4.3, 4.6):
    _M10G["m10_g_n6low%02d" % round(_p * 10)] = ((-13723.0, 6500.0, FLOOR_Z), 0.0, _p, "wait 72; tap offhand1; wait 3.0s")
for _n, (_o, _yw, _pt, _s) in _M10G.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
SCHEDULE_PRE["m10_g"] = _M10_GR_LOG
# N6 P-07 round 3: the grapple on Gibraltar (grapple_attachVerticalBoost 0, Pathfinder 200), so no attach hop lifts the body
# over the ~33 u ledge of --geometry h20. Run with --legend gibraltar and without --kit: every reset puts mp_ability_grapple in
# the tactical slot (refilled, range mod removed) before the M10 grapple logger. Pitch 5.0-6.0 deg down: floor 570-690 u ahead,
# beyond the ledge (the ray clears its 229 u deep top), within the 850 range.
_N6_GIB_GRAPPLE = (
    'entity n6gw = p.GetOffhandWeapon( OFFHAND_TACTICAL )\n'
    'if ( !IsValid( n6gw ) || n6gw.GetWeaponClassName() != "mp_ability_grapple" )\n'
    '{\n'
    '\tif ( IsValid( n6gw ) ) p.TakeOffhandWeapon( OFFHAND_TACTICAL )\n'
    '\tp.GiveOffhandWeapon( "mp_ability_grapple", OFFHAND_TACTICAL, [] )\n'
    '}\n'
    'DevAbilities_RefillPlayer( p, true )\n'
    'entity n6rg = p.GetOffhandWeapon( OFFHAND_TACTICAL )\n'
    'if ( IsValid( n6rg ) && n6rg.HasMod( "infinite_abilities_grapple" ) ) n6rg.RemoveMod( "infinite_abilities_grapple" )\n'
    'pre = " n6tac=" + p.GetOffhandWeapon( OFFHAND_TACTICAL ).GetWeaponClassName()\n')
_N6GIB = {}
for _p in (5.0, 5.5, 6.0):
    _k = "m10_g_n6gib%02d" % round(_p * 10)
    _N6GIB[_k] = None
    SCHEDULES[_k] = "wait 72; tap offhand1; wait 3.0s"
    SCHEDULE_ORIGIN[_k] = (-13723.0, 6500.0, FLOOR_Z)
    SCHEDULE_YAW[_k] = 0.0
    SCHEDULE_PITCH[_k] = _p
    SCHEDULE_PRE[_k] = _N6_GIB_GRAPPLE + _M10_GR_LOG
# Round 4: the ground pull lifts the body (grapple_initialImpulseOffGround) over the ledge, so a ceiling (the M10 Octane rock
# pitched 90 deg, underside 80 u above the floor, ~450 u along x centred at x -13800) over the start keeps the body below the
# ledge top; the eye-height ray (60 u) still passes between the ceiling and the ledge to the floor beyond.
_N6_CEIL = ('foreach ( entity e in GetEntArrayByScriptName( "hsd_n6_ceil" ) ) e.Destroy()\n'
            'asset n6rk = $"%s"\n'
            'if ( !ModelIsPrecached( n6rk ) ) MapEdit_PrecacheModel( n6rk )\n'
            '{ entity n6ce = CreatePropDynamic( n6rk, <-13800.0, 6500, %.2f>, <90, 0, 0>, SOLID_VPHYSICS, -1.0 ); n6ce.SetScriptName( "hsd_n6_ceil" ) }\n'
            'pre += " n6ceil=80"\n')
for _p in (5.0, 5.5):
    _k = "m10_g_n6ceil%02d" % round(_p * 10)
    _N6GIB[_k] = None
    SCHEDULES[_k] = "wait 72; tap offhand1; wait 3.0s"
    SCHEDULE_ORIGIN[_k] = (-13723.0, 6500.0, FLOOR_Z)
    SCHEDULE_YAW[_k] = 0.0
    SCHEDULE_PITCH[_k] = _p
    SCHEDULE_PRE[_k] = _N6_GIB_GRAPPLE + (_N6_CEIL % (M10_ROCK, FLOOR_Z + 80.0 + 110.0)) + _M10_GR_LOG
# exact names must win over the "m10_g" prefix (matched in insertion order)
SCHEDULE_PRE = {**{k: SCHEDULE_PRE[k] for k in _N6GIB}, **{k: v for k, v in SCHEDULE_PRE.items() if k not in _N6GIB}}

# ---- M10 ③ Octane (legend octane --kit, --m10-log). Every m10_o* reset: full health, the pad upgrades (passives) taken away
# and given per schedule, then a server logger (health, speed_boost severity, stim visual effect; 10 Hz, 10 s). Pads are created
# with JumpPad_CreateAtLocation (as M4) AFTER the passives so the x1.2 launch (PAS_ULT_UPGRADE_ONE) and the upgraded skin
# (PAS_ULT_UPGRADE_THREE, enable_doublejump_aircontrol) are applied. Ceilings: three copies of the M3 rock pitched 90 deg
# (flat underside ~110 u below the origin, ~450 u along x and ~420 u along y each; probed in the M10 explore game) at x -14450 /
# -14000 / -13550 over lane C, underside H u above the floor; the logger traces the underside 0.3 s after the spawn.
_M10O_LOG = r"""
void functionref() m10o = void function() : ( p ) {
	try {
		wait 0.3
		string ce = ""
		foreach ( float cx in [ -14500.0, -14300.0, -14000.0, -13600.0, -13300.0 ] ) {
			TraceResults tr = TraceLine( <cx, 6800, 304.92>, <cx, 6800, 1500>, [ p ], TRACE_MASK_PLAYERSOLID, TRACE_COLLISION_GROUP_PLAYER )
			ce += format( " %.0f:%.1f", cx, tr.fraction < 1 ? tr.endPos.z - 294.92 : -1.0 )
		}
		printt( "[M10-OCT] run=" + GetConVarInt( "hsd_md_run" ) + " ceiling" + ce )
		float t0 = Time()
		while ( Time() - t0 < 10.0 && IsValid( p ) ) {
			printt( "[M10-OCT] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%.4f hp=%d boost=%.4f stimfx=%.4f", Time(), p.GetHealth(), StatusEffect_GetSeverity( p, eStatusEffect.speed_boost ), StatusEffect_GetSeverity( p, eStatusEffect.stim_visual_effect ) ) )
			WaitFrame()
		}
	} catch ( oErr ) { printt( "[M10-OCT] error " + string( oErr ) ) }
}
thread m10o()
"""


def _m10o_pre(pad_dx=None, passives=(), ceil_h=None, smooth=False):
    s = ['p.SetHealth( p.GetMaxHealth() )',
         'foreach ( int pas in [ ePassives.PAS_ULT_UPGRADE_ONE, ePassives.PAS_ULT_UPGRADE_TWO, ePassives.PAS_ULT_UPGRADE_THREE ] ) '
         '{ if ( p.HasPassive( pas ) ) TakePassive( p, pas ) }',
         'foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo_m4" ) ) e.Destroy()',
         'foreach ( entity e in GetEntArrayByScriptName( "hsd_m10_ceil" ) ) e.Destroy()']
    for ps in passives:
        s.append('GivePassive( p, ePassives.%s )' % ps)
    if ceil_h is not None and smooth:
        # round 2: ONE rock pitched -90 / yaw 180 (its smooth climbable face down): underside rises ~1.9 deg along +X from
        # ~H at x -14475 to ~H + 13 at x -14075 (probed in the M10 explore game), lip at x -14500 over the pad
        s.append('asset rk = $"%s"' % M10_ROCK)
        s.append('if ( !ModelIsPrecached( rk ) ) MapEdit_PrecacheModel( rk )')
        s.append('{ entity ce = CreatePropDynamic( rk, <-14290.0, 6800, %.2f>, <-90, 180, 0>, SOLID_VPHYSICS, -1.0 ); ce.SetScriptName( "hsd_m10_ceil" ) }'
                 % (FLOOR_Z + ceil_h + 115.0))
    elif ceil_h is not None:
        s.append('asset rk = $"%s"' % M10_ROCK)
        s.append('if ( !ModelIsPrecached( rk ) ) MapEdit_PrecacheModel( rk )')
        for cx in (-14450.0, -14000.0, -13550.0):
            s.append('{ entity ce = CreatePropDynamic( rk, <%.1f, 6800, %.2f>, <90, 0, 0>, SOLID_VPHYSICS, -1.0 ); ce.SetScriptName( "hsd_m10_ceil" ) }'
                     % (cx, FLOOR_Z + ceil_h + 110.0))
    if pad_dx is not None:
        s.append('entity pad = JumpPad_CreateAtLocation( o + <%.1f, 0, 0>, <0, 0, 0>, p, true )' % pad_dx)
        s.append('if ( IsValid( pad ) ) pad.SetScriptName( "hsd_test_geo_m4" )')
        s.append('pre += " pad=" + IsValid( pad )')
    s.append('pre += " passives=%s ceil=%s%s"' % ("+".join(passives) or "none", ceil_h, "_smooth" if smooth else ""))
    return "\n".join(s) + "\n" + _M10O_LOG


_M10O = {}   # name: (origin, yaw, pitch, steps, pre)
_LC = LANE_C
_M10O.update({
    # O-1 regression and interactions (lane C, no pad)
    "m10_o_stim_sprint": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.0s; tap offhand1; wait 2.5s; up forward; up speed; wait 6.0s", _m10o_pre()),
    "m10_o_stim_slide": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 0.6s; tap offhand1; wait 1.0s; down duck; wait 1.2s; up duck; up forward; up speed; wait 6.0s", _m10o_pre()),
    "m10_o_ctrl_slide": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.6s; down duck; wait 1.2s; up duck; up forward; up speed; wait 1.0s", _m10o_pre()),
    "m10_o_stim_hop": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 0.4s; tap offhand1; wait 1.0s; tap jump; waitair; waitland; tap jump; waitair; waitland; tap jump; "
                       "waitair; waitland; wait 0.3s; up forward; up speed; wait 5.0s", _m10o_pre()),
    "m10_o_ctrl_hop": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.4s; tap jump; waitair; waitland; tap jump; waitair; waitland; tap jump; "
                       "waitair; waitland; wait 0.3s; up forward; up speed; wait 1.0s", _m10o_pre()),
    # O-2 re-use: stand, stim, second press X s later; single stim control
    "m10_o_stim_once": (_LC, 0.0, 0.0, "wait 72; tap offhand1; wait 9.0s", _m10o_pre()),
    # O-3 / O-4 pad direction and arcs (pad 300 u ahead; drift = pad 60 u ahead, a 12-frame W tap, no key at contact)
    "m10_o_pad_walk": (_LC, 0.0, 0.0, "wait 72; down forward; wait 2.5s; up forward; wait 3.5s", _m10o_pre(300.0)),
    "m10_o_pad_crouch": (_LC, 0.0, 0.0, "wait 72; down duck; wait 0.5s; down forward; wait 4.0s; up forward; up duck; wait 2.0s", _m10o_pre(300.0)),
    "m10_o_pad_sprint": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.5s; up forward; up speed; wait 4.0s", _m10o_pre(300.0)),
    "m10_o_pad_drift": (_LC, 0.0, 0.0, "wait 72; down forward; waitf 12; up forward; wait 4.5s", _m10o_pre(60.0)),
    "m10_o_pad_side": (_LC, 90.0, 0.0, "wait 72; down moveright; wait 3.0s; up moveright; wait 3.0s", _m10o_pre(300.0)),
    "m10_o_pad_back": (_LC, 180.0, 0.0, "wait 72; down backward; wait 3.0s; up backward; wait 3.0s", _m10o_pre(300.0)),
    # upgrades (local scripts; S21 status per track D): x1.2 push, upgraded pad double jump with D held 0.5 s after the launch
    "m10_o_padup1_walk": (_LC, 0.0, 0.0, "wait 72; down forward; wait 2.5s; up forward; wait 4.0s", _m10o_pre(300.0, ("PAS_ULT_UPGRADE_ONE",))),
    "m10_o_padup1_crouch": (_LC, 0.0, 0.0, "wait 72; down duck; wait 0.5s; down forward; wait 4.0s; up forward; up duck; wait 2.5s", _m10o_pre(300.0, ("PAS_ULT_UPGRADE_ONE",))),
    "m10_o_pad_dj_d": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; waitair; up forward; up speed; waitf 60; down moveright; tap jump; wait 0.6s; up moveright; wait 3.0s", _m10o_pre(300.0)),
    "m10_o_padup3_dj_d": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; waitair; up forward; up speed; waitf 60; down moveright; tap jump; wait 0.6s; up moveright; wait 3.0s",
                          _m10o_pre(300.0, ("PAS_ULT_UPGRADE_THREE",))),
    "m10_o_padup3_dj_none": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; waitair; up forward; up speed; waitf 60; tap jump; wait 3.6s", _m10o_pre(300.0, ("PAS_ULT_UPGRADE_THREE",))),
    "m10_o_padup3_dj_dhold": (_LC, 0.0, 0.0, "wait 72; down speed; down forward; waitair; up forward; up speed; waitf 40; down moveright; waitf 20; tap jump; wait 0.6s; up moveright; wait 3.0s",
                              _m10o_pre(300.0, ("PAS_ULT_UPGRADE_THREE",))),
})
for _x in (1.0, 2.0, 3.0, 5.9, 6.1, 6.6):
    _M10O["m10_o_restim_t%02d" % int(round(_x * 10))] = (_LC, 0.0, 0.0, "wait 72; tap offhand1; wait %.1fs; tap offhand1; wait %.1fs" % (_x, 9.0 - _x), _m10o_pre())
# O-6 / O-7 ceiling surf: walk (W held) / crouch-walk onto the pad under a ceiling H u above the floor; W held 2 s after the
# launch (waitair = the launch); drift (no key at contact) at 250; steer (D 0.3 s after the launch) at 150; controls without
# a pad under the H100 ceiling (standing jump, sprint jump)
for _h in (100, 150, 250, 400, 600):
    _M10O["m10_o_ceil_h%d_st" % _h] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; wait 2.0s; up forward; wait 2.5s", _m10o_pre(300.0, (), _h))
    _M10O["m10_o_ceil_h%d_cr" % _h] = (_LC, 0.0, 0.0, "wait 72; down duck; wait 0.5s; down forward; waitair; wait 2.0s; up forward; up duck; wait 2.5s", _m10o_pre(300.0, (), _h))
_M10O["m10_o_ceil_h250_drift"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitf 12; up forward; wait 4.5s", _m10o_pre(60.0, (), 250))
_M10O["m10_o_ceil_h150_steer"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; wait 0.3s; up forward; down moveright; wait 1.0s; up moveright; wait 3.0s", _m10o_pre(300.0, (), 150))
_M10O["m10_o_ceil_h100_jump"] = ((-14300.0, 6800.0, FLOOR_Z), 0.0, 0.0, "wait 72; tap jump; wait 2.0s", _m10o_pre(None, (), 100))
_M10O["m10_o_ceil_h100_sprjump"] = (_LC, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.0s; tap jump; wait 1.5s; up forward; up speed; wait 1.0s", _m10o_pre(None, (), 100))
# round 2 (after session M10R_octane: the surf exists but the three rough rocks broke it after 0.05-0.13 s): one smooth rock;
# stim re-press after the charge cooldown (charge_time 6 + charge_cooldown_time 0.7 in mp_ability_octane_stim.txt)
for _h in (150, 250, 400):
    _M10O["m10_o_ceil2_h%d_st" % _h] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; wait 2.0s; up forward; wait 2.5s", _m10o_pre(300.0, (), _h, True))
    _M10O["m10_o_ceil2_h%d_cr" % _h] = (_LC, 0.0, 0.0, "wait 72; down duck; wait 0.5s; down forward; waitair; wait 2.0s; up forward; up duck; wait 2.5s", _m10o_pre(300.0, (), _h, True))
_M10O["m10_o_ceil2_h250_drift"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitf 12; up forward; wait 4.5s", _m10o_pre(60.0, (), 250, True))
_M10O["m10_o_ceil2_h250_steer"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; wait 0.25s; up forward; down moveright; wait 1.0s; up moveright; wait 3.0s", _m10o_pre(300.0, (), 250, True))
_M10O["m10_o_ceil2_h250_noW"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; up forward; wait 4.5s", _m10o_pre(300.0, (), 250, True))
_M10O["m10_o_ceil2_h100_jump"] = ((-14350.0, 6800.0, FLOOR_Z), 0.0, 0.0, "wait 72; tap jump; wait 2.0s", _m10o_pre(None, (), 100, True))
for _x in (7.5, 9.0):
    _M10O["m10_o_restim_t%02d" % int(round(_x * 10))] = (_LC, 0.0, 0.0, "wait 72; tap offhand1; wait %.1fs; tap offhand1; wait %.1fs" % (_x, 10.5 - _x), _m10o_pre())
_M10O["m10_o_noceil_st"] = (_LC, 0.0, 0.0, "wait 72; down forward; waitair; wait 2.0s; up forward; wait 2.5s", _m10o_pre(300.0))
_M10O["m10_o_noceil_cr"] = (_LC, 0.0, 0.0, "wait 72; down duck; wait 0.5s; down forward; waitair; wait 2.0s; up forward; up duck; wait 2.5s", _m10o_pre(300.0))
for _n, (_o, _yw, _pt, _s, _pre) in _M10O.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
    SCHEDULE_PRE[_n] = _pre
# exact names must win over the shorter prefixes already in SCHEDULE_PRE (matched in insertion order)
SCHEDULE_PRE = {**{k: SCHEDULE_PRE[k] for k in _M10O}, **{k: v for k, v in SCHEDULE_PRE.items() if k not in _M10O}}


# ---- M10 ② Zipline Gun (legend pathfinder --kit, --m10-log). Real ultimate: tap offhand4 (raise), 1.0 s later tap attack.
# Every m10_z* reset: the player is taken off any rope, the gun ropes already in the world are counted and (except m10_z_keep*)
# destroyed, the ult weapon's mods / clip / distance keys are printed, then a server logger (10 Hz, 10 s): every gun rope
# (script name zipline_start: origin, linked zipline_end origin), the player's zipline flag, origin, velocity, ult clip.
_M10Z_LOG = r"""
void functionref() m10z = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 10.0 && IsValid( p ) ) {
			string rs = ""
			foreach ( entity zs in GetEntArrayByScriptName( "zipline_start" ) ) {
				entity ze = zs.GetLinkEnt()
				vector a = zs.GetOrigin()
				vector b = IsValid( ze ) ? ze.GetOrigin() : <0, 0, 0>
				rs += format( " rope=%.2f,%.2f,%.2f>%.2f,%.2f,%.2f", a.x, a.y, a.z, b.x, b.y, b.z )
			}
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			printt( "[M10-ZIP] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%.4f zip=%d o=%.3f,%.3f,%.3f v=%.3f,%.3f,%.3f clip=%d gnd=%d", Time(), p.IsZiplining() ? 1 : 0, po.x, po.y, po.z, pv.x, pv.y, pv.z, IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1, p.IsOnGround() ? 1 : 0 ) + rs )
			WaitFrame()
		}
	} catch ( zErr ) { printt( "[M10-ZIP] error " + string( zErr ) ) }
}
thread m10z()
"""


def _m10z_pre(keep=False):
    s = ['if ( p.IsZiplining() ) p.Zipline_Stop()',
         'int nz = GetEntArrayByScriptName( "zipline_start" ).len()',
         'pre += " ropes_before=" + nz']
    if not keep:
        s.append('foreach ( entity zs in GetEntArrayByScriptName( "zipline_start" ) ) zs.Destroy()')
    s.append('entity zw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )')
    s.append('if ( IsValid( zw ) ) pre += " ult=" + zw.GetWeaponClassName() + " mods=" + zw.GetMods().len() + " clip=" + zw.GetWeaponPrimaryClipCount() + "/" + zw.GetWeaponPrimaryClipCountMax()')
    s.append('if ( IsValid( zw ) ) { foreach ( string md in zw.GetMods() ) pre += " mod:" + md }')
    return "\n".join(s) + "\n" + _M10Z_LOG


_ZF = "wait 72; tap offhand4; wait 1.0s; tap attack; "
_M10Z = {   # name: (origin, yaw, pitch, steps, keep)
    "m10_z_fire_d600": (_LC, 0.0, 6.65, _ZF + "wait 3.0s", False),
    "m10_z_fire_d800": (_LC, 0.0, 5.0, _ZF + "wait 3.0s", False),
    "m10_z_fire_d1500": (_LC, 0.0, 2.67, _ZF + "wait 3.0s", False),
    "m10_z_fire_d2300": (_LC, 0.0, 1.74, _ZF + "wait 3.0s", False),
    "m10_z_fire_flat": (_LC, 0.0, 0.0, _ZF + "wait 4.0s", False),
    "m10_z_fire_sky": (_LC, 0.0, -40.0, _ZF + "wait 3.0s", False),
    "m10_z_fire_air": (_LC, 0.0, 2.67, "wait 72; tap offhand4; wait 1.0s; tap jump; wait 0.25s; tap attack; wait 3.0s", False),
    "m10_z_wall_d800": ((-14506.0, 6500.0, FLOOR_Z), 0.0, -10.0, _ZF + "wait 3.0s", False),
    "m10_z_wall_d600": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -10.0, _ZF + "wait 3.0s", False),
    "m10_z_steep40": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -40.0, _ZF + "wait 3.0s", False),
    "m10_z_steep50": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -50.0, _ZF + "wait 3.0s", False),
    # rides: mount from the begin station 2 s after the fire
    "m10_z_ride_d1500": (_LC, 0.0, 2.67, _ZF + "wait 2.0s; tap use; wait 6.0s", False),
    "m10_z_ride_wall": ((-14506.0, 6500.0, FLOOR_Z), 0.0, -10.0, _ZF + "wait 2.0s; tap use; wait 4.0s", False),
    "m10_z_ride_s40": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -40.0, _ZF + "wait 2.0s; tap use; wait 4.0s", False),
    "m10_z_ride_s50": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -50.0, _ZF + "wait 2.0s; tap use; wait 4.0s", False),
    "m10_z_ride_jump": (_LC, 0.0, 2.67, _ZF + "wait 2.0s; tap use; wait 0.8s; tap jump; wait 3.0s", False),
    "m10_z_ride_super": (_LC, 0.0, 2.67, _ZF + "wait 2.0s; tap use; waitf 2; tap jump; waitf 1; tap jump; wait 3.0s", False),
    "m10_z_ride_s50_jump90": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -50.0, "set cl_yawspeed 180; " + _ZF + "wait 2.0s; tap use; wait 0.3s; down right; wait 0.5s; up right; tap jump; wait 3.0s", False),
    "m10_z_ride_s40_jump90": ((-14306.0, 6500.0, FLOOR_Z), 0.0, -40.0, "set cl_yawspeed 180; " + _ZF + "wait 2.0s; tap use; wait 0.3s; down right; wait 0.5s; up right; tap jump; wait 3.0s", False),
    # grapple onto the own rope: fire along lane C, walk 1.3 s to +Y, turn right 90 deg, grapple (pitch 2.67 = the rope height
    # ~58 u at 260 u lateral, if the stations hold the rope ~60 u up)
    "m10_z_grapple_rope": (_LC, 0.0, 2.67, "set cl_yawspeed 180; " + _ZF + "wait 1.5s; down moveleft; wait 1.3s; up moveleft; down right; wait 0.5s; up right; "
                           "wait 0.2s; tap offhand1; wait 4.0s", False),
    # retry (session M10R_zip: the gun rope hangs 112 u up, the 2.67 deg aim passed under it): the rope is fired with the view
    # 9.2 deg up (it lands on the far terrain), the player walks 1.0 s forward and 1.3 s to +Y, turns right 90 deg, grapples
    "m10_z_grapple_rope2": (_LC, 0.0, -9.2, "set cl_yawspeed 180; " + _ZF + "wait 1.5s; down forward; wait 1.0s; up forward; down moveleft; wait 1.3s; "
                            "up moveleft; down right; wait 0.5s; up right; wait 0.2s; tap offhand1; wait 4.0s", False),
    # several ropes: not destroyed between these trials (3 ropes side by side from y 6800 / 6650 / 6500 is not possible on one
    # origin, so the same origin is reused: count the ropes and see what a second gun rope does to the first)
    "m10_z_keep_d1500": (_LC, 0.0, 2.67, _ZF + "wait 3.0s", True),
}
for _n, (_o, _yw, _pt, _s, _keep) in _M10Z.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
    SCHEDULE_PRE[_n] = _m10z_pre(_keep)
SCHEDULE_PRE = {**{k: SCHEDULE_PRE[k] for k in _M10Z}, **{k: v for k, v in SCHEDULE_PRE.items() if k not in _M10Z}}


# ---- M10 ④ D1 slide re-check (lane C, legend gibraltar, no kit). rel: crouch released at slide age X with W + sprint still
# held (and one with every key released); sj: slide jump at slide age A from a 1.5 s sprint (fresh slide boost); sj2: the same
# on a second slide that starts 0.6 s after a first 0.4 s slide ended (boost not re-armed, M9-D1: ~1 s re-arm)
_M10S = {}
for _x in (0.10, 0.25, 0.50, 1.00):
    _M10S["m10_s_rel_t%03d" % int(round(_x * 100))] = "wait 72; down speed; down forward; wait 1.5s; down duck; wait %.2fs; up duck; wait 1.5s; up forward; up speed; wait 0.5s" % _x
_M10S["m10_s_rel_t025_nokeys"] = "wait 72; down speed; down forward; wait 1.5s; down duck; wait 0.25s; up duck; up forward; up speed; wait 2.0s"
_M10S["m10_s_hold"] = "wait 72; down speed; down forward; wait 1.5s; down duck; wait 2.0s; up duck; up forward; up speed; wait 0.5s"
for _a in (0.10, 0.25, 0.40, 0.60, 1.00):
    _M10S["m10_s_sj_a%03d" % int(round(_a * 100))] = "wait 72; down speed; down forward; wait 1.5s; down duck; wait %.2fs; tap jump; wait 1.0s; up duck; up forward; up speed; wait 0.5s" % _a
for _a in (0.25, 0.60):
    _M10S["m10_s_sj2_a%03d" % int(round(_a * 100))] = ("wait 72; down speed; down forward; wait 1.5s; down duck; wait 0.4s; up duck; wait 0.6s; down duck; wait %.2fs; tap jump; "
                                                       "wait 1.0s; up duck; up forward; up speed; wait 0.5s" % _a)
_M10S["m10_s_sprint_jump"] = "wait 72; down speed; down forward; wait 1.5s; tap jump; wait 1.0s; up forward; up speed; wait 0.5s"
for _n, _s in _M10S.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = LANE_C


# ---- M10 ⑤ Wraith feasibility (legend wraith --kit, --state-log). Server logger (10 Hz, 12 s): speed_boost severity, phase
# flag, placing_phase_tunnel severity, ult clip, origin / velocity, phase-tunnel blockers (the portals' trace blockers).
# Tactical regression = M4 m4_wraith_void. Portal (mp_weapon_phase_tunnel, charge_time -1, placement up to 10 s / 6000 u, a
# +0.1 speed_boost step per 20 % of the max distance): tap ultimate, sprint D s, tap ultimate again (end portal), then walk
# back into the exit portal: back 0.6 s, forward 1.5 s (the travel replays the path); sl = slide the last 0.4 s before the
# end press; walk = no sprint.
_M10W_LOG = r"""
void functionref() m10w = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 14.0 && IsValid( p ) ) {
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			int nb = GetEntArrayByScriptName( "phase_tunnel_blocker" ).len()
			int npb = GetEntArrayByScriptName( "pre_phase_tunnel_blocker" ).len()
			printt( "[M10-WR] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%.4f boost=%.4f placing=%.3f ph=%d clip=%d o=%.3f,%.3f,%.3f v=%.3f,%.3f,%.3f blockers=%d pre=%d", Time(),
				StatusEffect_GetSeverity( p, eStatusEffect.speed_boost ), StatusEffect_GetSeverity( p, eStatusEffect.placing_phase_tunnel ), p.IsPhaseShifted() ? 1 : 0,
				IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1, po.x, po.y, po.z, pv.x, pv.y, pv.z, nb, npb ) )
			WaitFrame()
		}
	} catch ( wErr ) { printt( "[M10-WR] error " + string( wErr ) ) }
}
thread m10w()
"""
_WR_PRE = 'try { DEV_PhaseTunnel_DestroyAll() } catch ( dErr ) { pre += " destroyall_err" }\n' + _M10W_LOG
_M10W = {
    "m10_w_void": "wait 72; down speed; down forward; wait 0.5s; tap offhand1; wait 4.2s; up forward; up speed; wait 1.0s",
    "m10_w_ctrl": "wait 72; down speed; down forward; wait 4.7s; up forward; up speed; wait 1.0s",
    "m10_w_portal_d2": "wait 72; tap offhand4; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; tap offhand4; wait 1.0s; "
                       "down backward; wait 0.6s; up backward; down forward; wait 1.5s; up forward; wait 4.0s",
    "m10_w_portal_d5": "wait 72; tap offhand4; wait 0.3s; down speed; down forward; wait 5.0s; up forward; up speed; tap offhand4; wait 1.0s; "
                       "down backward; wait 0.6s; up backward; down forward; wait 1.5s; up forward; wait 5.0s",
    "m10_w_portal_walk": "wait 72; tap offhand4; wait 0.3s; down forward; wait 3.0s; up forward; tap offhand4; wait 1.0s; "
                         "down backward; wait 0.6s; up backward; down forward; wait 1.5s; up forward; wait 4.0s",
    "m10_w_portal_sl": "wait 72; tap offhand4; wait 0.3s; down speed; down forward; wait 2.0s; down duck; wait 0.4s; up duck; up forward; up speed; "
                       "tap offhand4; wait 1.0s; down backward; wait 0.6s; up backward; down forward; wait 1.5s; up forward; wait 4.0s",
    "m10_w_portal_sprint_in": "wait 72; tap offhand4; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; tap offhand4; wait 0.5s; "
                              "down backward; wait 1.2s; up backward; down speed; down forward; wait 1.5s; up forward; up speed; wait 4.0s",
    "m10_w_portal_hold": "wait 72; down offhand4; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; up offhand4; wait 1.0s; "
                         "down backward; wait 0.6s; up backward; down forward; wait 1.5s; up forward; wait 4.0s",
}
for _n, _s in _M10W.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = (-14700.0, 6650.0, FLOOR_Z)   # explore: from x -14900 the portal exit dropped the player off the field edge
    SCHEDULE_PRE[_n] = _WR_PRE
SCHEDULE_PRE = {**{k: SCHEDULE_PRE[k] for k in _M10W}, **{k: v for k, v in SCHEDULE_PRE.items() if k not in _M10W}}


# ---- M10 track R2 (m10/E2-NEXT-BATCH.md section 5; follow-up of track R). Prefix m10r2_*. Every m10r2 reset stops all
# speed_boost status effects first. Server logger [M10R2-WR] (per dedi script frame, 10 Hz): speed_boost severity, placing
# severity, phase flag, isInPhaseTunnel, ult / tactical clip, origin, velocity, eye yaw, portal blocker count and (when the
# count changes) their origins. Duration per schedule (lifetime trials 52 s).
def _m10r2_log(dur):
    return r"""
void functionref() m10r2w = void function() : ( p ) {
	try {
		float t0 = Time()
		int lastnb = -1
		int lastnpb = -1
		int run0 = GetConVarInt( "hsd_md_run" )
		while ( Time() - t0 < %.1f && IsValid( p ) ) {
			int rn = GetConVarInt( "hsd_md_run" )
			if ( rn != run0 && rn != 0 )
				break
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			entity tw = p.GetOffhandWeapon( OFFHAND_TACTICAL )
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			array<entity> bl = GetEntArrayByScriptName( "phase_tunnel_blocker" )
			array<entity> pbl = GetEntArrayByScriptName( "pre_phase_tunnel_blocker" )
			int npb = pbl.len()
			string bs = ""
			if ( npb != lastnpb ) {
				bs += " pbls="
				foreach ( entity b in pbl ) { vector bo = b.GetOrigin(); bs += format( "%%.1f,%%.1f,%%.1f;", bo.x, bo.y, bo.z ) }
				lastnpb = npb
			}
			if ( bl.len() != lastnb ) {
				bs += " bls="
				foreach ( entity b in bl ) { vector bo = b.GetOrigin(); bs += format( "%%.1f,%%.1f,%%.1f;", bo.x, bo.y, bo.z ) }
				lastnb = bl.len()
			}
			printt( "[M10R2-WR] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f boost=%%.4f placing=%%.3f ph=%%d tun=%%d uclip=%%d tclip=%%d o=%%.3f,%%.3f,%%.3f v=%%.3f,%%.3f,%%.3f yaw=%%.2f gnd=%%d blockers=%%d pre=%%d", Time(),
				StatusEffect_GetSeverity( p, eStatusEffect.speed_boost ), StatusEffect_GetSeverity( p, eStatusEffect.placing_phase_tunnel ), p.IsPhaseShifted() ? 1 : 0,
				p.e.isInPhaseTunnel ? 1 : 0, IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1, IsValid( tw ) ? tw.GetWeaponPrimaryClipCount() : -1,
				po.x, po.y, po.z, pv.x, pv.y, pv.z, p.EyeAngles().y, p.IsOnGround() ? 1 : 0, bl.len(), npb ) + bs )
			WaitFrame()
		}
	} catch ( wErr ) { printt( "[M10R2-WR] error " + string( wErr ) ) }
}
thread m10r2w()
""" % dur


_M10R2_CLEAN = ('StatusEffect_StopAllOfType( p, eStatusEffect.speed_boost )\n'
                'try { DEV_PhaseTunnel_DestroyAll() } catch ( dErr ) { pre += " destroyall_err" }\n')

# Teleport helper for the start-portal entry: once the portal pair exists (2 blockers) wait D s, then put the player DX u
# along +X from the start portal (the blocker nearest the reset origin), velocity 0, view kept; the schedule then walks in.
_M10R2_TP = r"""
void functionref() m10r2tp = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 25.0 && StatusEffect_GetSeverity( p, eStatusEffect.placing_phase_tunnel ) <= 0.0 ) WaitFrame()
		while ( Time() - t0 < 25.0 && GetEntArrayByScriptName( "phase_tunnel_blocker" ).len() < 2 ) WaitFrame()
		wait %(delay).2f
		vector o0 = <%(ox).1f, %(oy).1f, %(oz).2f>
		array<entity> bl = GetEntArrayByScriptName( "phase_tunnel_blocker" )
		entity s = bl[0]
		foreach ( entity b in bl ) {
			vector d1 = b.GetOrigin() - o0
			vector d2 = s.GetOrigin() - o0
			if ( d1.x * d1.x + d1.y * d1.y < d2.x * d2.x + d2.y * d2.y ) s = b
		}
		vector so = s.GetOrigin()
		p.SetVelocity( <0, 0, 0> )
		p.SetOrigin( <so.x + %(dx).1f, so.y, %(oz).2f> )
		p.SetVelocity( <0, 0, 0> )
		printt( "[M10R2-TP] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f start=%%.1f,%%.1f,%%.1f", Time(), so.x, so.y, so.z ) )
	} catch ( tErr ) { printt( "[M10R2-TP] error " + string( tErr ) ) }
}
thread m10r2tp()
"""

_M10R2_WO = (-14700.0, 6650.0, FLOOR_Z)   # track R portal start (field edge safe)
# placement with a run-in: sprint 1 s, tap ult while sprinting, sprint 2 s more, tap ult (end) and release W on the next frame
_RUNIN = "wait 72; down speed; down forward; wait 1.0s; tap offhand4; wait 2.0s; tap offhand4; up forward; up speed; "
# track R placement (standing start, W released before the end tap)
_STAND = "wait 72; tap offhand4; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; tap offhand4; "
_M10R2W = {   # name: (steps, pre extra, logger seconds)
    # exit velocity rule: through the end portal (arrive at the start node) and through the start portal (arrive at the end node)
    "m10r2_w_runin_end": (_RUNIN + "wait 1.0s; down backward; waitph; up backward; wait 4.0s", "", 16.0),
    "m10r2_w_runin_start": (_RUNIN + "wait 2.8s; down forward; waitph; up forward; wait 4.0s", "TP", 18.0),
    "m10r2_w_stand_start": (_STAND + "wait 2.8s; down forward; waitph; up forward; wait 4.0s", "TP", 18.0),
    # minimum portal gap: walk W for X s after the raise, stop, end tap
    "m10r2_w_gap_t000": ("wait 72; tap offhand4; wait 1.2s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t015": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.15s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t030": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.30s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t045": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.45s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t060": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.60s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t065": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.65s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t070": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.70s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    "m10r2_w_gap_t075": ("wait 72; tap offhand4; wait 0.7s; down forward; wait 0.75s; up forward; wait 0.5s; tap offhand4; wait 3.0s", "", 8.0),
    # lifetime: standing-start portal, then wait
    "m10r2_w_life": (_STAND + "wait 48.0s", "", 52.0),
    # stay on the exit portal (no keys) after arriving; repeated traversal (step out, back in, twice)
    "m10r2_w_stay": (_STAND + "wait 1.0s; down backward; waitph; up backward; wait 6.0s", "", 16.0),
    "m10r2_w_repeat": (_STAND + "wait 1.0s; down backward; waitph; up backward; wait 1.5s; down forward; wait 0.5s; up forward; wait 0.5s; "
                       "down backward; waitph; up backward; wait 1.5s; down backward; wait 0.5s; up backward; wait 0.5s; down forward; waitph; up forward; wait 3.0s", "", 24.0),
    # Into the Void + portal: walk into the end portal while phased; tap ult while phased
    "m10r2_w_void_in": (_STAND + "wait 0.6s; tap offhand1; wait 1.25s; down backward; wait 1.5s; up backward; wait 3.0s", "", 16.0),
    "m10r2_w_void_place": ("wait 72; tap offhand1; wait 1.4s; tap offhand4; wait 0.3s; down forward; wait 1.0s; up forward; tap offhand4; wait 3.0s", "", 10.0),
    # session 2 (the tactical did not fire 0.6 s after the end tap): Void 2.5 s after the end tap, walk back through the end
    # portal during the phase (from 1.3 s after the press); vctrl = the same walk without the Void press
    "m10r2_w_vin2": (_STAND + "wait 2.5s; tap offhand1; wait 1.3s; down backward; wait 1.2s; up backward; wait 3.0s", "", 16.0),
    "m10r2_w_vctrl": (_STAND + "wait 2.5s; wait 1.3s; down backward; wait 1.2s; up backward; wait 3.0s", "", 16.0),
}
for _n, (_s, _x, _d) in _M10R2W.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _M10R2_WO
    _p = _M10R2_CLEAN + _m10r2_log(_d)
    if _x == "TP":
        _p += _M10R2_TP % dict(delay=1.5, ox=_M10R2_WO[0], oy=_M10R2_WO[1], oz=_M10R2_WO[2], dx=-80.0)
    SCHEDULE_PRE[_n] = _p

# speed_boost severity -> move scale: StatusEffect_AddTimed( speed_boost, S, 5 s, fade 0 ) at the reset, sprint 3 s on lane C;
# stack = 0.2 + 0.1 (two effects); fade = 0.15 for 1.5 s with a 0.25 s fade (the Maggie trailing call)
_M10R2_SEV = {"s005": [(0.05, 5.0, 0.0)], "s010": [(0.10, 5.0, 0.0)], "s015": [(0.15, 5.0, 0.0)], "s020": [(0.20, 5.0, 0.0)],
              "s030": [(0.30, 5.0, 0.0)], "s040": [(0.40, 5.0, 0.0)], "s050": [(0.50, 5.0, 0.0)], "s100": [(1.00, 5.0, 0.0)],
              "stack": [(0.20, 5.0, 0.0), (0.10, 5.0, 0.0)], "fade": [(0.15, 1.5, 0.25)], "ctrl": []}
for _k, _effs in _M10R2_SEV.items():
    _n = "m10r2_sev_" + _k
    SCHEDULES[_n] = "wait 72; down speed; down forward; wait %s; up forward; up speed; wait 3.0s" % ("1.6s" if _k == "s100" else "2.5s")
    SCHEDULE_ORIGIN[_n] = LANE_C
    SCHEDULE_PRE[_n] = (_M10R2_CLEAN + "".join("StatusEffect_AddTimed( p, eStatusEffect.speed_boost, %.3f, %.2f, %.2f )\n" % e for e in _effs)
                        + 'pre += " sev=%s"\n' % _k + _m10r2_log(9.0))
# long portal: the M10 rock floated with its flat top (x -14700..-14500, y 6325..6650) at z 5532.8 (probed: top = origin +
# 237.88; the map's ceiling is z ~8475 here); start on it, sprint off the +X edge, brake in the air with S, land on the
# field ~5238 u lower, sprint 1.5 s (severity steps), end tap, walk back into the end portal (replay up the drop)
_M10R2_GEO = {"m10r2tower": [(M10_ROCK, -14600.0, 6500.0, FLOOR_Z + 5000.0, 0.0, 0.0, 0.0)]}
_M10R2_TOWER = (-14680.0, 6500.0, 5532.8)
for _n, _s in {
        "m10r2_w_drop": "wait 72; tap offhand4; wait 0.3s; down speed; down forward; waitair; up forward; up speed; down backward; wait 0.8s; up backward; "
                        "waitland; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; tap offhand4; wait 1.0s; down backward; waitph; up backward; wait 6.0s",
        "m10r2_w_tower_ctrl": "wait 72; down speed; down forward; waitair; up forward; up speed; down backward; wait 0.8s; up backward; "
                              "waitland; wait 0.3s; down speed; down forward; wait 2.0s; up forward; up speed; wait 2.0s"}.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _M10R2_TOWER
    SCHEDULE_PRE[_n] = _M10R2_CLEAN + _m10r2_log(22.0)
# ---- M10 R2 Mad Maggie Wrecking Ball (legend madmaggie --kit). Server logger [M10R2-MG] per dedi frame: speed_boost severity,
# ground friction scale, sliding, origin, velocity, count of wreckingball_speedtrigger entities (and their origins when the
# count changes), balls. Reset: speed triggers cleared (DEV_ClearWreckingBallSpeedTriggers), friction 1, boosts stopped.
def _m10r2_mlog(dur):
    return r"""
void functionref() m10r2m = void function() : ( p ) {
	try {
		float t0 = Time()
		int lastn = -1
		int run0 = GetConVarInt( "hsd_md_run" )
		while ( Time() - t0 < %.1f && IsValid( p ) ) {
			int rn = GetConVarInt( "hsd_md_run" )
			if ( rn != run0 && rn != 0 )
				break
			array<entity> tr = GetEntArrayByScriptName( "wreckingball_speedtrigger" )
			int nb = GetEntArrayByScriptName( "wreckingball_ball" ).len()
			string ts = ""
			if ( tr.len() != lastn ) {
				ts = " trs="
				foreach ( entity e in tr ) { vector eo = e.GetOrigin(); ts += format( "%%.1f,%%.1f,%%.1f;", eo.x, eo.y, eo.z ) }
				lastn = tr.len()
			}
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			printt( "[M10R2-MG] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f boost=%%.4f fric=%%.3f slide=%%d gnd=%%d o=%%.3f,%%.3f,%%.3f v=%%.3f,%%.3f,%%.3f ntr=%%d balls=%%d uclip=%%d stim=%%.3f", Time(),
				StatusEffect_GetSeverity( p, eStatusEffect.speed_boost ), p.GetGroundFrictionScale(), p.IsSliding() ? 1 : 0, p.IsOnGround() ? 1 : 0,
				po.x, po.y, po.z, pv.x, pv.y, pv.z, tr.len(), nb, IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1,
				StatusEffect_GetSeverity( p, eStatusEffect.stim_visual_effect ) ) + ts )
			WaitFrame()
		}
	} catch ( mErr ) { printt( "[M10R2-MG] error " + string( mErr ) ) }
}
thread m10r2m()
""" % dur


_M10R2_MCLEAN = ('StatusEffect_StopAllOfType( p, eStatusEffect.speed_boost )\n'
                 'try { foreach ( entity wb in GetEntArrayByScriptName( "wreckingball_ball" ) ) wb.Destroy() } catch ( bErr ) { pre += " ball_err" }\n'
                 'try { DEV_ClearWreckingBallSpeedTriggers() } catch ( cErr ) { pre += " clear_err" }\n'
                 'p.SetGroundFrictionScale( 1.0 )\n')
_M10R2M = {
    "m10r2_m_probe_tap": ("wait 72; tap offhand4; wait 6.0s", 10.0),
    "m10r2_m_probe_hold": ("wait 72; down offhand4; wait 1.5s; up offhand4; wait 6.0s", 10.0),
    # ball thrown +X from lane C (first piece lands ~490-520 u ahead, then one piece per ~1 s every ~500-700 u)
    "m10r2_m_pass": ("wait 72; tap offhand4; wait 2.8s; down speed; down forward; wait 2.6s; up forward; up speed; wait 3.5s", 12.0),
    "m10r2_m_pass2": ("wait 72; tap offhand4; wait 2.8s; down speed; down forward; wait 4.6s; up forward; up speed; wait 3.0s", 13.0),
    "m10r2_m_walk": ("wait 72; tap offhand4; wait 2.8s; down forward; wait 3.6s; up forward; wait 3.0s", 12.0),
    "m10r2_m_slide": ("wait 72; tap offhand4; wait 2.8s; down speed; down forward; wait 1.4s; down duck; wait 1.6s; up duck; up forward; up speed; wait 3.0s", 12.0),
    "m10r2_m_stand": ("wait 72; tap offhand4; wait 2.8s; down forward; wait 2.45s; up forward; wait 3.0s; down forward; wait 1.0s; up forward; wait 3.0s", 15.0),
    "m10r2_m_ctrl_slide": ("wait 72; wait 2.8s; down speed; down forward; wait 1.4s; down duck; wait 1.6s; up duck; up forward; up speed; wait 3.0s", 12.0),
}
for _n, (_s, _d) in _M10R2M.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = LANE_C
    SCHEDULE_PRE[_n] = _M10R2_MCLEAN + _m10r2_mlog(_d)
# ---- M10 R2 Newcastle Castle Wall / Armored Leap (legend newcastle --kit, --server-cvar bridge_armored_leap_trace=1). Ult is
# offhandHybrid: tap offhand4 (raise 1.5 s), then attack fires the leap at the view trace point. Server logger [M10R2-NC] per
# dedi frame: origin, velocity, ground, ult clip, castle wall entity count. Distances by pitch from the standing eye (60 u).
def _m10r2_nlog(dur):
    return r"""
void functionref() m10r2n = void function() : ( p ) {
	try {
		float t0 = Time()
		int run0 = GetConVarInt( "hsd_md_run" )
		while ( Time() - t0 < %.1f && IsValid( p ) ) {
			int rn = GetConVarInt( "hsd_md_run" )
			if ( rn != run0 && rn != 0 )
				break
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			int nw = GetEntArrayByScriptName( "al_shield_barrier" ).len() + GetEntArrayByScriptName( "al_shield_anchor" ).len()
			printt( "[M10R2-NC] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f o=%%.3f,%%.3f,%%.3f v=%%.3f,%%.3f,%%.3f gnd=%%d uclip=%%d walls=%%d", Time(),
				po.x, po.y, po.z, pv.x, pv.y, pv.z, p.IsOnGround() ? 1 : 0, IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1, nw ) )
			WaitFrame()
		}
	} catch ( nErr ) { printt( "[M10R2-NC] error " + string( nErr ) ) }
}
thread m10r2n()
""" % dur


_M10R2_NCLEAN = ('StatusEffect_StopAllOfType( p, eStatusEffect.speed_boost )\n'
                 'try { foreach ( string sn in [ "al_shield_barrier", "al_shield_anchor", "axiom_castle_wall_snakehead" ] ) '
                 'foreach ( entity we in GetEntArrayByScriptName( sn ) ) we.Destroy() } catch ( wErr ) { pre += " wall_err" }\n'
                 'foreach ( entity ie in GetEntArrayByScriptName( "hsd_m10r2_int" ) ) ie.Destroy()\n')
_NC_FIRE = "wait 72; tap offhand4; wait 1.6s; tap attack; wait 5.0s"
# interruption helper (harness shortcut): once the leap launch speed is reached (v_x > 1500) a rock is spawned in the path
# (origin 330 u ahead, 100 u below the player; its -X face ~206 u ahead); removed at the next reset
_M10R2_NINT = r"""
void functionref() m10r2ni = void function() : ( p ) {
	try {
		float t0 = Time()
		while ( Time() - t0 < 8.0 && p.GetVelocity().x < 1500.0 ) WaitFrame()
		vector po = p.GetOrigin()
		entity ce = CreatePropDynamic( $"%s", <po.x + 330.0, po.y, po.z - 100.0>, <0, 0, 0>, SOLID_VPHYSICS, -1.0 )
		ce.SetScriptName( "hsd_m10r2_int" )
		printt( "[M10R2-NI] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f at=%%.1f,%%.1f,%%.1f vx=%%.1f", Time(), po.x, po.y, po.z, p.GetVelocity().x ) )
	} catch ( iErr ) { printt( "[M10R2-NI] error " + string( iErr ) ) }
}
thread m10r2ni()
""" % M10_ROCK
_M10R2N = {   # name: (origin, yaw, pitch, steps)
    "m10r2_n_d500": (LANE_C, 0.0, 6.84, _NC_FIRE),
    "m10r2_n_d900": (LANE_C, 0.0, 3.81, _NC_FIRE),
    "m10r2_n_d1400": (LANE_C, 0.0, 2.45, _NC_FIRE),
    "m10r2_n_d2000": (LANE_C, 0.0, 1.72, _NC_FIRE),
    # interruption: the leap arc to ~1300 u passes under the floating m10fly rock (underside ~ floor + 450..505)
    "m10r2_n_fly1300": ((-14300.0, 5900.0, FLOOR_Z), 0.0, 2.64, _NC_FIRE),
}
# round 2 (probe: the target lands ~1.13x farther than a 60 u eye predicts -> eye ~69 u during the raise; cap 1575 u = 40 m)
for _d in (300, 600, 700, 1200, 1800):
    _M10R2N["m10r2_n_e%d" % _d] = (LANE_C, 0.0, round(math.degrees(math.atan2(69.0, _d)), 2), _NC_FIRE)
_M10R2N["m10r2_n_int"] = (LANE_C, 0.0, round(math.degrees(math.atan2(69.0, 1200.0)), 2), _NC_FIRE)
_M10R2N["m10r2_n_ceil"] = (LANE_C, 0.0, round(math.degrees(math.atan2(69.0, 1200.0)), 2), _NC_FIRE)   # ceiling variant
for _n, (_o, _yw, _pt, _s) in _M10R2N.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
    SCHEDULE_PRE[_n] = _M10R2_NCLEAN + _m10r2_nlog(9.0) + {"m10r2_n_int": _M10R2_NINT,
                                                          "m10r2_n_ceil": _M10R2_NINT.replace("po.x + 330.0, po.y, po.z - 100.0", "po.x + 250.0, po.y, po.z + 362.0")}.get(_n, "")
# ---- M10 R2 Pathfinder (legend pathfinder --kit): Zipline Gun fired while climbing (s950 wall), grapple onto the own gun
# rope with a deterministic aim (harness teleport + eye snap), and Octane pad tap strafe (O-5, pads by JumpPad_CreateAtLocation).
# Server logger [M10R2-ZP] per dedi frame: zipline / wall-run / grapple flags, origin, velocity, ult clip, gun ropes.
def _m10r2_zlog(dur):
    return r"""
void functionref() m10r2z = void function() : ( p ) {
	try {
		float t0 = Time()
		int run0 = GetConVarInt( "hsd_md_run" )
		int lastn = -1
		while ( Time() - t0 < %.1f && IsValid( p ) ) {
			int rn = GetConVarInt( "hsd_md_run" )
			if ( rn != run0 && rn != 0 )
				break
			array<entity> zl = GetEntArrayByScriptName( "zipline_start" )
			string rs = ""
			if ( zl.len() != lastn ) {
				foreach ( entity zs in zl ) {
					entity ze = zs.GetLinkEnt()
					vector a = zs.GetOrigin()
					vector b = IsValid( ze ) ? ze.GetOrigin() : <0, 0, 0>
					rs += format( " rope=%%.2f,%%.2f,%%.2f>%%.2f,%%.2f,%%.2f", a.x, a.y, a.z, b.x, b.y, b.z )
				}
				lastn = zl.len()
			}
			entity uw = p.GetOffhandWeapon( OFFHAND_ULTIMATE )
			vector po = p.GetOrigin()
			vector pv = p.GetVelocity()
			printt( "[M10R2-ZP] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f zip=%%d wr=%%d hang=%%d gract=%%d gratt=%%d o=%%.3f,%%.3f,%%.3f v=%%.3f,%%.3f,%%.3f uclip=%%d gnd=%%d nrope=%%d", Time(),
				p.IsZiplining() ? 1 : 0, p.IsWallRunning() ? 1 : 0, p.IsWallHanging() ? 1 : 0, p.IsGrappleActive() ? 1 : 0, p.IsGrappleAttached() ? 1 : 0,
				po.x, po.y, po.z, pv.x, pv.y, pv.z, IsValid( uw ) ? uw.GetWeaponPrimaryClipCount() : -1, p.IsOnGround() ? 1 : 0, zl.len() ) + rs )
			WaitFrame()
		}
	} catch ( zErr ) { printt( "[M10R2-ZP] error " + string( zErr ) ) }
}
thread m10r2z()
""" % dur


_M10R2_ZCLEAN = ('StatusEffect_StopAllOfType( p, eStatusEffect.speed_boost )\n'
                 'if ( p.IsZiplining() ) p.Zipline_Stop()\n'
                 'foreach ( entity zs in GetEntArrayByScriptName( "zipline_start" ) ) zs.Destroy()\n'
                 'foreach ( entity e in GetEntArrayByScriptName( "hsd_test_geo_m4" ) ) e.Destroy()\n'
                 'foreach ( entity e in GetEntArrayByScriptName( "hsd_m10r2_int" ) ) e.Destroy()\n')
# grapple-to-rope aim helper (harness shortcut): when the gun rope exists, wait 1 s, put the player LAT u to the right of the
# rope, ALONG u from its start, on the floor, and snap the eye to the rope point (eye = origin + 60) plus a pitch offset
_M10R2_GROPE = r"""
void functionref() m10r2gr = void function() : ( p ) {
	try {
		float t0 = Time()
		array<entity> zl
		while ( Time() - t0 < 10.0 ) {
			zl = GetEntArrayByScriptName( "zipline_start" )
			if ( zl.len() > 0 && IsValid( zl[0].GetLinkEnt() ) )
				break
			WaitFrame()
		}
		wait 1.0
		vector a = zl[0].GetOrigin()
		vector b = zl[0].GetLinkEnt().GetOrigin()
		vector u = Normalize( b - a )
		vector tp = a + u * %(along).1f
		vector side = Normalize( CrossProduct( u, <0, 0, 1> ) )
		vector po = tp + side * %(lat).1f
		po.z = %(fz).2f
		vector ang = VectorToAngles( tp - ( po + <0, 0, 60> ) )
		ang.x += %(poff).2f
		p.SetVelocity( <0, 0, 0> )
		p.SetOrigin( po )
		p.SetVelocity( <0, 0, 0> )
		p.SnapEyeAngles( ang )
		p.SnapFeetToEyes()
		printt( "[M10R2-GR] run=" + GetConVarInt( "hsd_md_run" ) + format( " t=%%.4f tp=%%.1f,%%.1f,%%.1f po=%%.1f,%%.1f,%%.1f pitch=%%.2f yaw=%%.2f", Time(), tp.x, tp.y, tp.z, po.x, po.y, po.z, ang.x, ang.y ) )
	} catch ( gErr ) { printt( "[M10R2-GR] error " + string( gErr ) ) }
}
thread m10r2gr()
"""
_ZFIRE = "wait 72; tap offhand4; wait 1.0s; tap attack; "
_M10R2Z = {   # name: (origin, yaw, pitch, steps, extra pre)
    # Zipline Gun while climbing the s950 wall (lane A, face x -13706): raise, sprint, jump into the wall, then turn the view
    # 90 / 135 deg right in 0.1 / 0.15 s and fire along the wall (a far target); ground control: same aim from the floor
    "m10r2_z_climb_t90": (LANE_A, 0.0, 0.0, "set cl_yawspeed 900; wait 72; tap offhand4; wait 1.0s; down speed; down forward; wait 1.2s; tap jump; "
                          "wait 0.6s; down right; wait 0.1s; up right; tap attack; wait 0.5s; up forward; up speed; wait 3.0s", ""),
    "m10r2_z_climb_t135": (LANE_A, 0.0, 0.0, "set cl_yawspeed 900; wait 72; tap offhand4; wait 1.0s; down speed; down forward; wait 1.2s; tap jump; "
                           "wait 0.6s; down right; wait 0.15s; up right; tap attack; wait 0.5s; up forward; up speed; wait 3.0s", ""),
    "m10r2_z_climb_t0": (LANE_A, 0.0, -30.0, "wait 72; tap offhand4; wait 1.0s; down speed; down forward; wait 1.2s; tap jump; "
                         "wait 0.6s; tap attack; wait 0.5s; up forward; up speed; wait 3.0s", ""),
    "m10r2_z_ground_m90": (LANE_A, -90.0, 0.0, _ZFIRE + "wait 3.0s", ""),
    # design 2 (the 0.1 s turn ended the climb before the fire): turn in 4 frames, fire on the next frame; side = 90 deg right
    # (pitch 0, target along -Y), back = 180 deg with the view 20 deg down (floor ~800 u behind); ctrl = climb without the gun
    "m10r2_z_climb_side": (LANE_A, 0.0, 0.0, "set cl_yawspeed 2700; wait 72; tap offhand4; wait 1.0s; down speed; down forward; wait 1.2s; tap jump; "
                           "wait 0.6s; down right; waitf 4; up right; tap attack; wait 0.5s; up forward; up speed; wait 3.0s", ""),
    "m10r2_z_climb_back": (LANE_A, 0.0, 20.0, "set cl_yawspeed 5400; wait 72; tap offhand4; wait 1.0s; down speed; down forward; wait 1.2s; tap jump; "
                           "wait 0.6s; down right; waitf 4; up right; tap attack; wait 0.5s; up forward; up speed; wait 3.0s", ""),
    "m10r2_z_climb_ctrl": (LANE_A, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.2s; tap jump; wait 2.5s; up forward; up speed; wait 1.5s", ""),
    # grapple onto the own gun rope (rope fired flat along +X from lane C to the far terrain, track R m10_z_fire_flat)
    "m10r2_z_grope": (LANE_C, 0.0, 0.0, _ZFIRE + "wait 3.0s; tap offhand1; wait 4.5s", "GR0"),
    "m10r2_z_gup": (LANE_C, 0.0, 0.0, _ZFIRE + "wait 3.0s; tap offhand1; wait 4.5s", "GR+"),
    "m10r2_z_gdn": (LANE_C, 0.0, 0.0, _ZFIRE + "wait 3.0s; tap offhand1; wait 4.5s", "GR-"),
}
_O5_TS = "down moveright; down right; " + "; ".join(["tap forward; waitf 1"] * 30) + "; up right; up moveright; wait 3.0s"
for _dx in (260, 290, 320):
    _M10R2Z["m10r2_o5_j%d" % _dx] = (LANE_C, 0.0, 0.0, "set cl_yawspeed 720; wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; " + _O5_TS, "PAD%d" % _dx)
_M10R2Z["m10r2_o5_ctrl"] = (LANE_C, 0.0, 0.0, "set cl_yawspeed 720; wait 72; down speed; down forward; waitair; up forward; up speed; " + _O5_TS, "PAD300")
# session 2 (session 1's O-5 trials hit leftover Newcastle castle walls on lane C): fresh game, pads 270 / 280 / 300 / 310 u
for _dx in (270, 280, 300, 310):
    _M10R2Z["m10r2_o5b_j%d" % _dx] = (LANE_C, 0.0, 0.0, "set cl_yawspeed 720; wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; " + _O5_TS, "PAD%d" % _dx)
_M10R2Z["m10r2_o5b_ctrl"] = _M10R2Z["m10r2_o5_ctrl"]
_M10R2Z["m10r2_o5b_jnots"] = (LANE_C, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; wait 3.5s", "PAD280")
_M10R2Z["m10r2_o5_jnots"] = (LANE_C, 0.0, 0.0, "wait 72; down speed; down forward; wait 1.0s; tap jump; waitf 1; up forward; up speed; wait 3.5s", "PAD290")
for _n, (_o, _yw, _pt, _s, _x) in _M10R2Z.items():
    SCHEDULES[_n] = _s
    SCHEDULE_ORIGIN[_n] = _o
    SCHEDULE_YAW[_n] = _yw
    SCHEDULE_PITCH[_n] = _pt
    _p = _M10R2_ZCLEAN + _m10r2_zlog(11.0)
    if _x.startswith("GR"):
        _p += _M10R2_GROPE % dict(along=400.0, lat=250.0, fz=FLOOR_Z, poff={"GR0": 0.0, "GR+": -1.5, "GR-": 1.5}[_x])
    elif _x.startswith("PAD"):
        _p += ('entity pad = JumpPad_CreateAtLocation( o + <%s, 0, 0>, <0, 0, 0>, p, true )\n'
               'if ( IsValid( pad ) ) pad.SetScriptName( "hsd_test_geo_m4" )\npre += " pad=" + IsValid( pad )\n' % _x[3:])
    SCHEDULE_PRE[_n] = _p
_R2K = [k for k in SCHEDULE_PRE if isinstance(k, str) and k.startswith("m10r2_")]
SCHEDULE_PRE = {**{k: SCHEDULE_PRE[k] for k in _R2K}, **{k: v for k, v in SCHEDULE_PRE.items() if k not in _R2K}}


# M10 client per-frame logger (--m10-log): grapple flags, hook origin, eye height; zipline flag
M10_CLIENT = string.Template(r'''
void functionref() hsd_m10_f = void function() {
	entity p = GetLocalClientPlayer()
	int w = 0
	while ( GetConVarInt( "hsd_md_run" ) != $run && w < 2400 )
	{
		WaitFrame()
		w++
	}
	while ( IsValid( p ) && GetConVarInt( "hsd_md_run" ) == $run )
	{
		entity h = p.GetGrappleHook()
		vector ho = IsValid( h ) ? h.GetOrigin() : <0, 0, 0>
		printt( "[M10-GRC] run=$run fc=" + FrameCount() + format( " t=%.5f", Time() ) + " act=" + p.IsGrappleActive() + " att=" + p.IsGrappleAttached() + " pull=" + p.IsGrapplePulling() + format( " hook=%.3f,%.3f,%.3f eye=%.3f", ho.x, ho.y, ho.z, p.EyePosition().z - p.GetOrigin().z ) + " zip=" + p.IsZiplining() )
		WaitFrame()
	}
}
thread hsd_m10_f()
AgentLink_Reply( "m10 logger run=$run" )
''')

# m10fly and later M10 props: (model, x, y, z, pitch, yaw, roll); spawned with the script name hsd_test_geo after the wall
M10_GEO = {"m10fly": [(M10_ROCK,) + M10_FLY + (0.0, 0.0, 0.0)]}
M10_GEO.update(_M10R2_GEO)
M10_SPAWN = r'''
string out = ""
try
{
	asset m = $"%(model)s"
	bool pre = ModelIsPrecached( m ) || MapEdit_PrecacheModel( m )
	out = "precached=" + pre
	if ( pre )
	{
		entity prop = CreatePropDynamic( m, <%(x)f, %(y)f, %(z)f>, <%(p)f, %(yw)f, %(r)f>, SOLID_VPHYSICS, -1.0 )
		if ( IsValid( prop ) )
		{
			prop.SetScriptName( "hsd_test_geo" )
			prop.AllowMantle()
			out += " prop=" + prop.GetEntIndex()
		}
		else
			out += " prop=invalid"
	}
}
catch ( err ) { out += " error=" + string( err ) }
AgentLink_Reply( out )
'''


DEFAULT_ORIGIN_SCHEDULES = {"basic","e1_walk", "e1_sprint", "e1_crouch", "e1_back", "e1_side", "e1_diag", "e1_turn",
                            "e2_strafe", "e2_noinput", "e2_keepfwd", "e4_stand", "e4_hop0", "e4_hop3", "e4_hop43", "e5_slide",
                            "e5_slidejump02", "e5_slidejump06", "n4b_wd", "n4b_ws", "n4b_ad", "n4b_wwd", "n4c_hop_d0", "n4c_hop_d1", "n4c_slidechain", "n4c_slidechain_ctrl", "n4c_slidesteer", "n4d_cut1000", "n4d_cut1090", "n4d_cut1110", "n4d_cut1200", "c3_drop96", "c3_drop160", "c3_drop400", "c3_drop400_duck", "c3_slide_straight", "c3_slide_turn", "c3_drop900", "c3_drop900_duck", "c3_jumpland", "c3_jumpland_duck", "n6_sprint_turn90", "n6_sprint_turn180", "n6_walk_turn90", "n6_strafe"}


def origin_for(name, default):
    st = _m9_stand_setup(name)
    if st:
        return st[0]
    if name in SCHEDULE_ORIGIN:
        return SCHEDULE_ORIGIN[name]
    if name in SCHEDULE_ZIP_ORIGIN:
        return SCHEDULE_ZIP_ORIGIN[name]
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
		if ( verb == "waitph" )
		{
			// M10 R2: wait until the client sees the phase shift (Wraith portal travel)
			int g = 0
			while ( !p.IsPhaseShifted() && g < 1200 )
			{
				WaitFrame()
				g++
			}
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=waitph frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() + " waited=" + g )
			continue
		}
		if ( verb == "waittrav" )
		{
			// M8: wait until the client-predicted traversal (mantle) has started
			int g = 0
			while ( !p.IsTraversing() && g < 1200 )
			{
				WaitFrame()
				g++
			}
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=waittrav frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() + " waited=" + g )
			continue
		}
		if ( verb == "set" )
		{
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=set cvar=" + parts[1] + " value=" + parts[2] + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() )
			continue
		}
		string key = parts[1]
		if ( verb == "wheel" )
		{
			// a mouse-wheel bind: press and release on the same frame (M6-A1 scroll tap strafe)
			p.ClientCommand( "+" + key )
			p.ClientCommand( "-" + key )
			printt( "[HSD-SCHED] ver=1 trial=$trial run=$run edge=wheel key=" + key + " frame=" + ( FrameCount() - f0 ) + " fc=" + FrameCount() + " pt=" + PlatformTime() + " t=" + Time() )
			continue
		}
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
    if M9_STAND_RE.fullmatch(name):
        return _M9_STAND
    # M6-A2 variants: sc = crouch on the same frame as the jump, cf = crouch one frame before the jump (jump still at N),
    # mbl = jump at N then a moveright press 30 frames later (lurch after a mantle boost)
    m = re.fullmatch(r"e7_(mb|sg|sc|cf|mbl)_f(\d+)", name)
    if m:
        k = int(m.group(2))
        if m.group(1) == "cf":
            return ("wait 72; down speed; down forward; wait 1.2s; tap jump; waitf %d; tap duck; tap jump; wait 1.5s; up forward; "
                    "up speed; wait 1.0s" % (k - 2))
        tail = {"sg": "tap jump; tap duck", "mb": "tap jump", "sc": "down duck; tap jump; up duck",
                "mbl": "tap jump; waitf 29; tap moveright"}[m.group(1)]
        return ("wait 72; down speed; down forward; wait 1.2s; tap jump; waitf %d; %s; wait 1.5s; up forward; up speed; wait 1.0s"
                % (k - 1, tail))
    if name.startswith("m8_sg_"):
        return _m8_sg(name)
    m = re.fullmatch(r"e3_right_k(\d+)", name)
    if m:
        k = int(m.group(1))
        return ("wait 72; down speed; down forward; wait 1.0s; tap jump; waitf %d; up forward; up speed; down moveright; "
                "wait 0.9s; up moveright; wait 0.5s" % k)
    return None


# M6 client state logger: traversal / hang / zipline / grapple / phase / glide meter per frame while the trial label is set.
# All eight getters exist on the client VM (probed live, M6); bools print true/false (list from m6/SOURCE-AUDIT.md A2).
STATE_CLIENT = string.Template(r'''
void functionref() hsd_state_f = void function() {
	entity p = GetLocalClientPlayer()
	int w = 0
	while ( GetConVarInt( "hsd_md_run" ) != $run && w < 2400 )
	{
		WaitFrame()
		w++
	}
	while ( IsValid( p ) && GetConVarInt( "hsd_md_run" ) == $run )
	{
		string sl = "[HSD-STATE] run=$run fc=" + FrameCount() + " t=" + Time() + " trav=" + p.IsTraversing() + " mant=" + p.IsMantling()
		sl = sl + " hang=" + p.IsWallHanging() + " wr=" + p.IsWallRunning() + " zip=" + p.IsZiplining() + " gr=" + p.IsGrappleActive()
		sl = sl + " ph=" + p.IsPhaseShifted() + " glide=" + p.GetGlideMeter()
		printt( sl )
		WaitFrame()
	}
}
thread hsd_state_f()
AgentLink_Reply( "state logger run=$run" )
''')

# Refill tactical, ultimate and glide/jet meters at every reset when --kit is set (_weapon_utility.nut:3810-3865).
# The refill also puts the range-doubling dev mod on the grapple (DevAbilities_RefillWeapon, M5.5 finding); from M6 on every
# --kit reset removes it again, so grapple range is the normal 850 setting (M4/M4b data ran with the mod; no effect found)
REFILL = ("DevAbilities_RefillPlayer( p, true )\n"
          "entity rgw = p.GetOffhandWeapon( OFFHAND_TACTICAL )\n"
          "if ( IsValid( rgw ) && rgw.HasMod( \"infinite_abilities_grapple\" ) ) rgw.RemoveMod( \"infinite_abilities_grapple\" )")

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
        if verb in ("waitair", "waitland", "waittrav", "waitph"):
            continue
        if verb in ("down", "up", "tap"):
            if arg not in KEYS:
                raise ValueError(f"unknown key in {s!r}")
        elif verb == "wheel":
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
    return any(s in ("waitair", "waitland", "waittrav", "waitph") for s in steps)


def schedule_frames(steps):
    """Frames of the fixed part of the schedule (state waits add a variable number)."""
    n = 0
    for s in steps:
        verb, _, arg = s.partition(" ")
        n += int(arg) if verb == "wait" else (1 if verb == "tap" else 0) if verb not in ("waitair", "waitland", "waittrav", "waitph") else 0
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
    ap.add_argument("--geometry", default="none",
                    help="comma list: m3 = the test wall on lane A (test_geometry.py); h<H> = the same rock sunk so its top "
                         "is H u above the floor (M6-A2 ledge heights); m6zip = the M6 ziplines (ZIP_SERVER)")
    ap.add_argument("--state-log", action="store_true", help="M6: client [HSD-STATE] logger thread per trial")
    ap.add_argument("--both-cvar", action="append", default=[],
                    help="NAME=VALUE set on the dedi and client consoles for the session, restored afterwards")
    ap.add_argument("--server-cvar", action="append", default=[],
                    help="NAME=VALUE set on the dedi console only for the session (M9: bridge_zip_mount_diag=1), restored afterwards")
    ap.add_argument("--client-exec", action="append", default=[],
                    help="M10: client console 'exec <cfg>' after the legend / kit (e.g. user/hsd_m10_classvars)")
    ap.add_argument("--m10-log", action="store_true", help="M10: client [M10-GRC] logger thread per trial")
    ap.add_argument("--m6-census", action="store_true",
                    help="also exec user/hsd_m6_classvars (client) and the M6 cvar finds on both consoles")
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
    # Only these M1/M2 schedules run at --origin on purpose; any other schedule must map to an explicit start (an M6
    # round-2 set once fell through to the default origin and never reached the test wall).
    unmapped = [n for n in names if origin_for(n, None) is None and n not in DEFAULT_ORIGIN_SCHEDULES and " " not in n]
    if unmapped:
        raise SystemExit("no start position for: " + ", ".join(unmapped) + " (add SCHEDULE_ORIGIN / _PREFIX)")
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
        geos = [g for g in a.geometry.split(",") if g and g != "none"]
        wall = next((g for g in geos if g == "m3" or (g[:1] in "hs" and g[1:].isdigit())), None)
        if wall and wall.startswith("s"):
            # M8 R2: copies of the rock stacked 470 u apart (the rock is ~498 u tall; overlap ~18 u), the top one with its
            # top H u above the floor (h<H> convention), down to the first copy whose bottom (origin - 250) reaches the floor.
            import test_geometry as tg
            H = float(wall[1:])
            zs = [tg.M3_WALL_ORIGIN[2] - (232.0 - H)]
            while zs[-1] - 250.0 > tg.M3_WALL_ORIGIN[2]:
                zs.append(zs[-1] - 470.0)
            if len(zs) > 4:
                raise SystemExit("stack height out of range: %s" % wall)
            server.eval(tg.CLEAR, check=False)
            replies = [server.eval(tg.SPAWN % dict(model=tg.M3_WALL_MODEL, x=tg.M3_WALL_ORIGIN[0], y=tg.M3_WALL_ORIGIN[1],
                                                   z=z, yaw=0.0), check=False).get("reply", "") for z in zs]
            manifest["geometry_wall_z"] = zs
            manifest["geometry"] = {"wall": " | ".join(replies)}
            print("geometry:", manifest["geometry"]["wall"])
            if any("prop=" not in r or "invalid" in r for r in replies):
                raise SystemExit("stacked test wall could not be spawned")
            time.sleep(2.0)
        elif wall:
            import test_geometry as tg
            # the rock's top is 232 u above its origin floor (M3); sink it to get a ledge H u above the floor
            wz = tg.M3_WALL_ORIGIN[2] - (232.0 - float(wall[1:])) if wall != "m3" else tg.M3_WALL_ORIGIN[2]
            server.eval(tg.CLEAR, check=False)
            r = server.eval(tg.SPAWN % dict(model=tg.M3_WALL_MODEL, x=tg.M3_WALL_ORIGIN[0], y=tg.M3_WALL_ORIGIN[1],
                                            z=wz, yaw=0.0), check=False)
            manifest["geometry_wall_z"] = wz
            manifest["geometry"] = {"wall": r.get("reply", "")}
            for side in (server, client):  # [MB-TRIG] per press edge, [MB-APPLY] per boost finish
                side.cmd("bridge_mantle_boost_trig_log 1")
                side.cmd("bridge_mantle_boost_apply_log 1")
            print("geometry:", r.get("reply", ""))
            if "prop=" not in r.get("reply", "") or "invalid" in r.get("reply", ""):
                raise SystemExit("test wall could not be spawned")
            time.sleep(2.0)
        for gname, lines in (("m9zip", M9_ZIP_LINES), ("m9zipv", M9_ZIPV_LINES)):
            if gname in geos:
                if "m6zip" in geos or ("m9zip" in geos and "m9zipv" in geos):
                    raise SystemExit("one rope geometry per session (each clears hsd_zip)")
                r = server.eval(M9_ZIP_SERVER % lines, check=False)
                manifest["geometry_zip"] = gname + " " + r.get("reply", "")
                manifest["geometry_ropes"] = M9_ROPES if gname == "m9zip" else {"vertical": M9_VROPE}
                print("ziplines:", manifest["geometry_zip"])
                if "zip_ents=" not in manifest["geometry_zip"]:
                    raise SystemExit("ziplines could not be spawned")
                time.sleep(1.0)
        m10g = [g for g in geos if g in M10_GEO]
        if m10g:
            if not wall:   # the wall branch clears hsd_test_geo; without a wall clear it here
                import test_geometry as tg
                server.eval(tg.CLEAR, check=False)
            manifest["geometry_m10"] = {}
            for g in m10g:
                reps = []
                for (mdl, x, y, z, pp, yw, rr) in M10_GEO[g]:
                    reps.append(server.eval(M10_SPAWN % dict(model=mdl, x=x, y=y, z=z, p=pp, yw=yw, r=rr), check=False).get("reply", ""))
                manifest["geometry_m10"][g] = {"props": M10_GEO[g], "replies": reps}
                print("geometry:", g, " | ".join(reps))
                if any("prop=" not in r or "invalid" in r for r in reps):
                    raise SystemExit("M10 geometry could not be spawned: " + g)
            time.sleep(2.0)
        if "m6zip" in geos:
            r = server.eval(ZIP_SERVER, check=False)
            manifest["geometry_zip"] = r.get("reply", "")
            print("ziplines:", manifest["geometry_zip"])
            if "zip_ents=" not in manifest["geometry_zip"]:
                raise SystemExit("ziplines could not be spawned")
            time.sleep(1.0)
        restore = []
        for nv in a.both_cvar:
            name, _, val = nv.partition("=")
            for side in (server, client):
                old = side.eval(f'AgentLink_Reply( GetConVarString( "{name}" ) )', check=False).get("reply", "")
                restore.append((side, name, old))
                side.cmd(f"{name} {val}")
        manifest["both_cvars"] = {nv.partition("=")[0]: nv.partition("=")[2] for nv in a.both_cvar}
        for nv in a.server_cvar:
            name, _, val = nv.partition("=")
            old = server.eval(f'AgentLink_Reply( GetConVarString( "{name}" ) )', check=False).get("reply", "")
            restore.append((server, name, old))
            server.cmd(f"{name} {val}")
        manifest["server_cvars"] = {nv.partition("=")[0]: nv.partition("=")[2] for nv in a.server_cvar}
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
        for cfg in a.client_exec:
            client.cmd("exec " + cfg)
            time.sleep(2.0)
        manifest["client_exec"] = a.client_exec
        if a.m6_census:
            client.cmd("exec user/hsd_m6_classvars")
            for side in (server, client):
                for f in ("jump_grace", "zipline", "mantle_boost", "lurch"):
                    side.cmd(f"find {f}")
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
            yaw = SCHEDULE_YAW.get(name, M8_YAW_PREFIX.get(name[:9], a.yaw))
            ox, oy, oz = origin_for(name, tuple(a.origin))
            pitch = SCHEDULE_PITCH.get(name, 0.0)
            m9st = _m9_stand_setup(name)
            if m9st:
                yaw, pitch = m9st[1], m9st[2]
            pre = next((code for prefix, code in SCHEDULE_PRE.items() if name.startswith(prefix)), "")  # prefix may be a tuple
            reset = server.eval(RESET_SERVER.substitute(ox=ox, oy=oy, oz=oz, yaw=yaw, pitch=pitch, batch=batch, run=run,
                                                         refill=REFILL if a.kit else "", pre=pre))
            for st in steps:
                if st.startswith("set "):
                    client.cmd(st[4:])
            if a.state_log:
                client.eval(STATE_CLIENT.substitute(run=run), check=False)
            if a.m10_log:
                client.eval(M10_CLIENT.substitute(run=run), check=False)
            sched = client.eval(SCHED_CLIENT.substitute(
                steps=", ".join(json.dumps(s) for s in steps), ox=ox, oy=oy, oz=oz,
                settle_frames=a.settle_frames, settle_timeout=a.settle_timeout, trial=trial, run=run))
            try:
                lines, gap = wait_for_end(client, since, trial, timeout=(frames + a.settle_timeout) / a.fps * 3 + 30)
            except TimeoutError as err:   # M8: keep the manifest of the trials already run, then stop the session
                print(f"trial {trial} run r{run} {name}: FAILED ({err}); stopping the session")
                manifest["trials"].append({"trial": trial, "run": run, "batch": batch, "schedule": name, "yaw": yaw,
                                           "origin": [ox, oy, oz], "schedule_frames": frames, "reset": reset.get("reply", ""),
                                           "scheduled": sched.get("reply", ""), "sched_lines": [], "log_gap": None,
                                           "measured_fps": None, "ok": False, "why": "timeout: " + str(err), "warmup": warm})
                break
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

        for side, name, old in restore:
            if old:
                side.cmd(f"{name} {old}")
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
