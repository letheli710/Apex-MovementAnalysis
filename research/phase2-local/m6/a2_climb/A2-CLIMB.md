# M6-A2 climb, ledge, mantle and superglide: model

Status: offline analysis of 11 existing session folders. Nothing was launched, and no file outside this folder was changed. Nothing is committed.

- Scripts (stdlib only, no local paths): `a2_climb_analysis.py` (analysis) and `a2_load.py` (raw-log loader and join).
- Outputs: `analysis_output.txt` (the script's stdout), `results.json` (every trial plus the summaries) and `params.json` (the parameter list in §6, with labels).
- Rerun:

```
cd research/phase2-local/m6/a2_climb
py -3 a2_climb_analysis.py ../../data/20261021_153251_M6_A2b_h60 ../../data/20261021_153757_M6_A2b_h90 \
  ../../data/20261021_154302_M6_A2b_h120 ../../data/20261021_154807_M6_A2b_h150 ../../data/20261021_155312_M6_A2b_h180 \
  ../../data/20261021_152746_M6_A2b_h232 ../../data/20261021_155815_M6_A2b_h300 ../../data/20261021_160320_M6_A2b_h400 \
  ../../data/20261021_151815_M6_A2_h232 ../../data/20261021_161058_M6_A2_sg_off ../../data/20261021_161628_M6_A2_sg_on \
  --json results.json --params params.json > analysis_output.txt
```

The run takes about 10 s in one Python process.

The round-2 sessions (§8) are optional extra arguments. Without them, the command above reproduces the round-1 outputs byte for byte; this was checked against the lead-verified files. The current `analysis_output.txt`, `results.json` and `params.json` come from the full command:

```
py -3 a2_climb_analysis.py <the 11 round-1 sessions above> \
  ../../data/20261021_164822_M6_A2r_h232 ../../data/20261021_165145_M6_A2r_h180 \
  --json results.json --params params.json > analysis_output.txt
```

The round-2 additions are output section 4c, the `round2` block in `results.json`, and one extra entry at the end of `params.json` (`round2_a2r_validity`).

Labels: **[meas]** read directly from client usercmds; **[fit]** a formula fitted to usercmds; **[src]** source or census; **[unknown]** seen but not explained; **[design-needed]** the data cannot decide it, so it is a Unity design choice.

## 1. Data and method

| Session | Scored | Not scored |
|---|---|---|
| A2b h60, h120 | 29 each | warm-up r90; one `a2_walk` each (r3190, r3266): the schedule ran 605 frames instead of 600 |
| A2b h90, h150, h180, h232, h300, h400 | 30 each | warm-up r90 |
| A2 h232 (older, no state log) | 29 | warm-up; r3111 `a2_hang` ran 557 frames instead of 553. Used only as a repeatability check |
| A2 sg_off (`mantle_boost_enabled 0`, runner `both_cvars`) | 50 | warm-up |
| A2 sg_on | 30 | warm-up |

- All sessions ran at 120 fps (measured 119.6–120.0). Every scored trial joined with ≤ 5 unjoined usercmds and no bad-state joins.
- **Raw logs, not `report/rows.csv`.** `rows.csv` keeps only 6 significant digits, which gives 0.1 u in x and 1 ms in t. `a2_load.py` parses the raw `MOVE-TRACE`, `[HSD-MD]` frame and evt lines, `[HSD-STATE]` and `[MB-*]` lines. It joins usercmds to client frames by the Plat_FloatTime stamp, using the `m2/air_jump/aj_load.py` rule.
- **State flags.** `[HSD-STATE]` lines are joined to frames by run and t. The climb shows as `wr=true`, the mantle as `trav=true mant=true`. **`hang=true` never occurs** in any A2b trial (238 trials).
- **FSM-off check.** The client `net_trace.log` shows `mantle_boost_enabled 0` sent before the session and `1` after it. No dedi log echoes the cvar. sg_off has **no** `[MB-TRIG]`/`[MB-APPLY]` lines on either side, although the trig and apply logs were switched on. That is consistent with the FSM being off on both sides.
- **Geometry.** The mantle exit z at each height is floor + H + 5.92: 390.84, 420.84, 450.84, 480.84 and 532.84. At H60 the jump lands on the top at z 360.82 (floor + 65.9). The exit x is −13698.1 at every height. The face origin x at climb contact is about −13720.5, so the face line is about −13704.5. Walking stops the origin at x −13719.2 (H60) to −13727.0 (H300), because a different part of the irregular rock sits at floor level for each H.

## 2. Q1: outcome per height, climb, anchor, traversal

### 2.1 Outcomes (5 trials per cell)

| H | a2_climb (sprint jump ~100 u before the face, W held) | a2_walk (W only, 199.5 u/s) |
|---|---|---|
| 60 | **lands on top** (z 360.82); no climb, no mantle | blocked at the face |
| 90 | **instant mantle** from the air at contact | blocked |
| 120 | **instant mantle** (wr set for ≤ 2 frames in 2 of 5) | blocked |
| 150 | **climb 0.206 s, then mantle** | blocked; 2/5 show client-only micro-climbs (§5) |
| 180 | **climb 0.399 s, then mantle** | blocked |
| 232 | **full climb 0.849 s, final jump-up, then mantle from the air** | blocked |
| 300 | **full climb 0.849 s, final jump-up, then fall** (re-touches the face and slides without climbing; climbs again after landing at the wall) | blocked; 2/5 client-only micro-climbs |
| 400 | same as 300 (climb 0.859 s) | blocked |

- [meas] Walking into the face never starts a climb or a mantle at any height (60 to 400). The climb needs an airborne contact.

### 2.2 Climb profile and duration

| H | climb duration (s) | height gained from contact (u) | end | z at end (abs) |
|---|---|---|---|---|
| 150 | 0.206 (0.199–0.217) | 25.3 | mantle trigger | 372.3 |
| 180 | 0.399 (0.392–0.409) | 55.6 | mantle trigger | 401.4 |
| 232 | 0.849 (sd 0.001) | 96.2 | final jump-up | 442.17 |
| 300 | 0.849 (sd 0.001) | 96.4 | final jump-up | 442.21 |
| 400 | 0.859 (sd 0.001) | 97.1 | final jump-up | 442.17 |
| 232, old session | 0.850 | — | final jump-up | 442.17 |

- [meas] The climb follows the same vz(t) at every height until the ledge interrupts it: peak about 180 at about 26 u, then the speed line.
- [meas] The final jump-up at 120 fps is dvz +202.8 (sd 0.6) with post vx −64.3 outward. M3 gave the dt→0 value 208 and the outward kick 68.1 − 500·dt.
- [meas] H400 contacts about 1 u lower (z 345.1 vs 346.0). It climbs 0.01 s longer and still ends at the same absolute z.

### 2.3 Anchor test (M3 open question 3): settled, not ledge-relative

| H | ledge (exit z) | climb end z | ledge − end | Z0 of the speed line |
|---|---|---|---|---|
| 232 | 532.84 | 442.167 | 90.7 | 475.33 |
| 300 | no mantle | 442.213 | — | 475.33 |
| 400 | no mantle | 442.167 | — | 475.27 |

- [meas] **The climb end and the speed line do not depend on the ledge.** With the ledge 68 u and 168 u higher, the climb ends at the same absolute z, about floor + 147.06. The bracket over 15 full climbs is pre-z in (441.865, 442.086], which is consistent with M3's (441.913, 441.934]. Z0 is also unchanged: floor + 180.3–180.4.
- **ClimbHeight 100 is not reached** either: the gain is 96.2–97.1 u. The end is not "contact + 100" either, because the contact z varies by 1 u while the end z does not.
- **What remains open.** Floor, takeoff z and contact are all the same in these sessions, so "floor-relative" and "takeoff-relative" cannot be separated. [design-needed] Unity uses `z_ref` = z of the last ground contact (the takeoff).
- **The ledge is only a mantle trigger** (§2.4). It ends the climb early when the ledge is in reach (H150, H180) or catches the player after the jump-up (H232).

### 2.4 Mantle trigger and traversal

| H | trigger | ledge − origin z at traversal start | traversal duration (s) | rise (u) |
|---|---|---|---|---|
| 90 | at contact (air) | 43.9 | 0.414 | 43.9 |
| 120 | at contact (air) | 73.6 | 0.578 | 73.6 |
| 150 | during the climb | 78.5 (74.6–79.9) | 0.604 | 78.5 |
| 180 | during the climb | 79.5 (78.8–79.9) | 0.612 | 79.5 |
| 232 | in the air after the jump-up | 76.0 (72.8–78.3) | 0.590 | 76.0 |

- [fit] **The traversal time scales with the remaining height:** T = 0.1728 + 0.00550·rise s, with rms 0.0026 s over 25 W-held traversals (rise 43–80 u). M3's 0.59 s is the rise-76 case.
- [fit] **Reach.** A mantle starts once ledge_top − z ≤ about 80 u. It is not a sharp threshold:
  - triggers were seen at gaps up to 79.9 u;
  - but other climbs passed gaps down to 76.0 u, one usercmd earlier, without triggering;
  - the climb durations at the trigger are quantised (0.200 / 0.208 / 0.217 / 0.225 s at H150), which suggests the check does not run on every usercmd [unknown].
- [meas] **Exit.** The origin ends at x −13698.1, about 6.4 u inside the face line, at the ledge z.
  - With W held, the first post-traversal usercmd has pre-velocity (299, 0, 0): the sprint pose speed along the move direction.
  - With W released earlier, the exit is at rest: (0, 0, 0) in 20/20.
  - In 24/65 W-held exits (H90/H120 only) that usercmd then loses 9.46 u/s and is back to 299 a few usercmds later: on both sides in 20 trials, client only in 4 [unknown].

## 3. Q2: hang, cancel, hop

The hang schedule releases W 0.9 s after the jump, which is 0.63–0.65 s after contact. What that does depends on the height:

| H | state at the release | result |
|---|---|---|
| 60 | standing on top | — |
| 90, 120 | mantle already finished | — |
| 150 | inside the traversal, at 0.42 s = frac 0.71 of the expected T | **mantle completes at rest** (exit v 0), 20/20 |
| 180 | inside the traversal, at 0.23 s = frac 0.38 | **mantle cancel**, 20/20 (below) |
| 232, 300, 400 | climbing, before the climb end | **slide down and detach**, 60/60 (below) |

- [meas] **No hang anywhere.** `hang=false` on every frame. Releasing W never leaves the player still on the wall near the ledge.
- [meas] **Mantle cancel (H180).**
  - After the release the scripted path runs backwards for 0.228 s (sd 0.010). x moves back 18.0 u from the peak at z ≈ 428.7.
  - Then the origin snaps in one frame to the traversal start position: x −13719.7, z 403.3 (start z 402.4).
  - The player falls with v = 0, and the dedi agrees.
  - Bracket of the cancel window, as a fraction of the expected traversal time: **aborted at ≤ 0.395, completed at ≥ 0.685** (0.242 s vs 0.404 s after the start).
- [fit] **Slide down after W is released on the wall (H232–400, n = 60).**
  - On the first usercmd after the release, dvz/dt = −789 (sd 4).
  - While vz > 5, the decel is −820 u/s²; vz reaches 0 after 0.100 s, at z ≈ 431.
  - The player then slides down still attached (wr=true) at −642 u/s² (dedi −639 to −649).
  - The detach comes **1.003 s (sd 0.004) after contact**, which is 0.36 s after the release. The schedule always released at the same time, so the data cannot say which of the two clocks sets it.
  - On the detach usercmd, +69.96 u/s outward is added (sd 0.001). After that the player falls normally.
- [meas] **Cancel, hop and back-hop presses all came after the player was standing**: on the floor at H180–400, and on the ledge top at H60–150. They are therefore ordinary ground actions:
  - back: first usercmd −23.96 u/s, −174 after 0.1 s (walk acceleration);
  - hop: standing jump, post vz 280.45 = 289.82 − 1.5·g·dt;
  - back+jump: the same jump with −4.17 on the jump usercmd and −54 after 0.1 s (air acceleration).
- **What this means.** Hang, cancel-from-hang and hop-from-hang are **not measured**. The only native "let go" mechanics observed are the mid-mantle cancel and the slide-down.

## 4. Q3 and Q4: superglide

### 4.1 FSM off (native code, `mantle_boost_enabled 0`), H232 rock, 5 trials per cell

| N (frames after the climb jump) | mb (jump) | sg (jump, crouch next frame) |
|---|---|---|
| 196 | 5× **cut to the top**: v (299, 0, 0), no jump | 5× cut, no jump |
| 200 | 2× cut, 3× **mantle jump**: v_h 299, V 289.8 | 2× cut, 3× **superglide**: v_h **460.0**, V 289.8 |
| 204 | 5× mantle jump | 5× superglide 460.0 |
| 208 | 5× mantle jump | 5× superglide 460.0 |
| 212 (after the traversal end) | 5× ordinary jump on top (299, V 289.8) | 5× ordinary jump on top (299); the crouch after it does nothing |

- [meas] **Without the FSM, a jump press inside the traversal ends the traversal on the next frame.** On that frame the origin snaps 15–20 u back toward the face (x −13721 … −13703).
- [meas] **Early press (f196 all, f200 4/10).** The origin goes to the ledge height. It exits airborne with (299, 0, 0) and no jump, then lands on the rock top 0.04 s later.
- [meas] **Later press (f200 6/10, f204, f208).** A native jump: post vz = 289.82 − 1.5·g·dt (V 289.82, sd 0.004, the ground-jump law) from a z below the ledge (522–533).
- **The f200 band is mixed.** The same pre-press position (z 520.9, x −13699.7) gave both outcomes, so the deciding variable is [unknown].
- [meas] **Native superglide.** With crouch on the exit usercmd, the exit horizontal speed is **460.000** on client and dedi (n = 13, sd 0). That equals the slide-start boost cap from M3's slide model, min(v + 150·msc, 460) = min(299 + 172.5, 460). [fit] The traversal-ending jump therefore keeps the slide boost, which the ground-jump clip to 299 would normally remove.
- **The control confirms it.** A crouch + jump on the ground two usercmds after the exit (sg_on r3607) has pre-velocity 460 and leaves at 299.
- **Comparison.**

| Exit | v_h | vz V |
|---|---|---|
| plain mantle (M3) | 299 | 0 |
| FSM state 3 (M3) | 299 | 289.8 (applied at the full traversal end) |
| FSM boost state 4 (M3 and §4.2) | 388.7 | 367.4 |
| **native jump-off (FSM off)** | 299 | 289.8, but the traversal is cut 1 frame after the press, 10–20 u back from the end |
| **native superglide (FSM off)** | **460** | 289.8 |

- **Client and dedi.** Exit-window parity is ≤ 0.08 u/s in 79/80 trials (r3518: 0.44, later in the air). No class differs between client and dedi.

### 4.2 FSM on (SDK mantle boost)

| Variant | n | Result |
|---|---|---|
| sc f200 (crouch on the jump frame) | 5 | 5× state 4: 388.700 / 367.42 |
| sc f208 | 5 | 4× state 4; r3607 pressed 2 frames after the exit → ordinary jump on top |
| cf f200 (crouch one frame before) | 5 | 5× state 4 |
| cf f208 | 5 | 5× state 4 |
| mb f204 (control) | 5 | 5× state 4 |
| mbl f204 (boost, then moveright 30 frames later) | 5 | 5× state 4 |

- [meas] **Crouch timing does not matter.** On the same frame, one frame before, or not at all, the exit is identical to the mb control.
  - Client and dedi `[MB-TRIG]` agree in all trials: gate `ok`, anim 0.83–0.96, delta 0.02–0.83.
  - Every boost exit is ducked (`duck=1`), with or without crouch.
- [meas] **Lurch after a boost is suppressed.**
  - The moveright press comes 0.19–0.22 s after the exit jump.
  - The measured change is |dv| = 0.008 u/s, on client and dedi.
  - The M3 lurch law at that t predicts |dv| 207.8 (clamped 209.3).
  - This matches the source: state 4 masks tap strafe until landing or the next traversal [src].

## 5. Residuals and client/dedi divergence

- **Climb re-simulation.** From the contact usercmd, with vz = min(vz + 490·dt, k·(Z0 − z)) and the end at pre-z ≥ 441.976 (30 climbs):

| Constants | Max \|vz err\| per climb, mean over climbs (incl. outlier) | Worst per H (excl. H180 outlier) | Final jump-up usercmd |
|---|---|---|---|
| M3 (k 1.735, Z0 475.33) | 2.39 | 0.79 (H150) to 1.79 (H400) | 0 or −1 |
| line fit of this data (k 1.748, Z0 475.25) | 3.28 | up to 2.83 | 0 or −1 |

  - [fit] Keep the M3 constants. The per-step decay rate here is 1.723 (pooled), against M3's 1.735.
- **Outlier r3343 (H180).** The jump came 14 u closer to the face, so contact happened at z 342.6 with vz 109. On the next 2 usercmds vz *fell* at −733 u/s². The +499 acceleration started only once vz ≈ 97. The model misses this, with a max error of 27.6 u/s.
  - That points to the climb acceleration applying only while vz < about 100 (n = 1, [unknown]).
  - M3's two-level acceleration (499, then 486) is visible again here.
- **Traversal time fit:** rms 0.0026 s.
- **Slide-down accelerations:** sd 3–5 u/s² within a height. H400 is about 4 u/s² steeper than H232.
- **Client vs dedi, whole trials.**
  - Landing usercmd ±3.1 u/s or a one-usercmd landing offset: harmless.
  - The climb and slide-down are not bit-exact: 2–5 u/s, as in M3.
  - Ground micro-climbs (H150/H300 walks) and the post-fall re-climb at H300: the client predicts a climb start (vz 37–49) while the dedi stays grounded. Up to 50 u/s and 2.4 u, corrected by the dedi. The micro-climbs are a client misprediction, not physics.
  - H400 r3431: the detach happened one usercmd earlier on the dedi.

## 6. Unity state model (per usercmd, dt = frame time)

```
GROUND / AIR: as M2/M3. Track z_ref = z at the last ground contact [design-needed: floor or takeoff], climbUsed = false on landing.

AIR -> CLIMB      when airborne, moving into a climbable face with W held, and !climbUsed [meas]
                  (walking into a face never climbs [meas])
  on contact:     v_h = 0; vz += 9.6 - g*dt/2 (M3) [meas]
                  (vz_contact > ~100: vz falls at g until <= ~100 before the climb accel [unknown, n=1])
  each cmd:       vz = min(vz + 490*dt, 1.735*(Z0 - z)), Z0 = z_ref + 180.4 [fit]; z += vz*dt
                  (vx follows the 1.86 deg face lean, M3)
  CLIMB -> MANTLE       if ledge_top - z <= ~80 u (check may lag 0-3 cmds) [fit]
  CLIMB -> JUMPUP       if z >= z_ref + 147.06 [meas]: vz += 208 - 584*dt; v_out = 68.1 - 500*dt (M3); climbUsed = true -> AIR
                        (AIR keeps checking the mantle reach; after the jump-up the trigger came at gap 72.8-78.3 u [meas])
  CLIMB -> SLIDE        on W release [meas]: first cmd vz += -789*dt, then -820 u/s^2 while vz > 5, then -642 u/s^2,
                        still attached; detach at contact + 1.00 s [meas; the clock is unknown: contact vs release + 0.36 s]
                        with v += 70 outward -> AIR (climbUsed = true)
  CLIMB -> WALL BOUNCE  on jump (M3 section 3, not re-tested here)
  AIR touching the face with climbUsed: no climb, plain slide/fall [meas]

AIR -> MANTLE     directly at contact when ledge_top - z <= reach (H90/H120) [meas]
MANTLE (scripted traversal, no physics):
  T = 0.173 + 0.0055*(ledge_top - z_start) s [fit]; path: in ~22 u toward the face while rising slowly
  (first ~0.2 s), then mostly vertical to the ledge height, then forward to face + 6.4 u [meas, one rock]
  exit: v = 299*moveDir if W held at the exit, else 0; vz = 0 [meas]
  W released before frac ~0.4-0.69 of T -> CANCEL [meas bracket; Unity 0.5 = design-needed]:
        play the path backwards 0.23 s, snap to the start position, v = 0 -> AIR
  jump pressed:
    SDK FSM variant (what the server runs by default) [src+meas]: latch; at the exit
        state 4 if pressed in the last 133 ms (camera gate): v_h = 1.3*299 = 388.7, vz = 367.4, ducked
        else state 3: v_h = 299, vz = 289.8; crouch timing irrelevant; after state 4: no lurch / tap strafe
        until landing or the next traversal
    native variant (FSM off) [meas]: end the traversal on the next frame, snap ~15-20 u back toward the face;
        press before ~0.47-0.50 s into T: go to the ledge height, v = (299,0,0), no jump;
        later: jump V = 289.82 (native law); v_h = 460 if crouch is held on that cmd (slide boost kept), else 299
    -> superglide flavour for Unity: [design-needed] (native 460, FSM 388.7/367.4, or a designed window)
HANG: not observed in S21 data -> [design-needed] (none in the native model)
```

**Parameters** (full list with n and spread in `params.json`):

| Parameter | Value | Label |
|---|---|---|
| climb accel | 490 u/s² (499 for the first ~10 usercmds, then 486) | fit |
| speed line k / Z0 | 1.735 /s / z_ref + 180.4 | fit (M3 constants re-validated, max err ≤ 1.8 u/s) |
| climb end | z_ref + 147.06 (bracket 146.95–147.17) | meas |
| full climb | 0.853 s, +96.6 u | meas |
| final jump-up (120 fps) | dvz +202.8, out −64.3 | meas |
| mantle reach | ~80 u (not sharp) | fit |
| traversal time | 0.1728 + 0.0055·rise | fit |
| exit speed | 299 (W held) / 0 (released) | meas |
| mantle cancel window | frac (0.395, 0.685] | meas bracket; threshold unknown |
| cancel reverse time | 0.228 s, then snap and drop | meas |
| W-release slide | −789 (first usercmd), −820 rising, −642 falling u/s² | fit |
| detach | 1.003 s after contact, +69.96 out | meas (clock ambiguous) |
| native superglide | v_h 460, V 289.82 | meas; 460 = slide cap (M3) fit |
| FSM boost | 388.7 / 367.41 | meas = src |
| post-boost lurch | 0.008 (predicted 207.8) | meas |
| hang | none | meas → design-needed |

## 7. Open questions and next run

1. **Floor vs takeoff anchor** for the climb end and Z0. Jump from a raised step or a box in front of the rock, or start on a slope, so that the takeoff z differs from the floor under the face.
2. **Detach clock.** Release W at 2–3 different times after contact (0.3 / 0.5 / 0.7 s).
3. **Hang, cancel and hop were not exercised.**
   - Every cancel, hop and back-hop press came after the player had landed (2.4 s after the jump).
   - Next run: press back / jump / back+jump 0.05–0.3 s after the W release, while still sliding on the wall (H300), and during the traversal (H180 and H232).
   - Also test pressing back during the mantle (cancel by input rather than by releasing W).
4. **Mantle cancel threshold** inside frac (0.395, 0.685]. Release W at 0.30 / 0.35 / 0.40 / 0.45 s into an H180/H232 traversal.
5. **FSM-off f200 band.** Find the hidden variable (sweep N 197–203 with 5 repeats each), and say what "cut to the top" is natively. Also run 60 and 144 fps.
6. **Superglide 460 = slide cap?** Test a walking mantle (exit 199.5, which predicts min(199.5 + 172.5, 460) = 372) and a crouch held through the press.
7. **High-vz contact** (r3343): gravity before the climb acceleration. Sweep the jump distance (60–110 u before the face).
8. **Mantle reach lag** (quantised durations): a finer height sweep (H 130–175 in 5 u steps).
9. The 9.46 u/s loss on the first exit usercmd at H90/H120 (both sides). Also the wall bounce on these heights (not re-tested), and a jump pressed in the slide-down phase.

## 8. Round 2 (a2r_* sessions): invalid, nothing could be measured

Sessions: `20261021_164822_M6_A2r_h232` (30 scored) and `20261021_165145_M6_A2r_h180` (20 scored). Both ran at 120 fps with the state log on, and the runner accepted every trial. The script checks them in output section 4c.

- [meas] **No round-2 trial reached the rock: 0/50.** There is no wall contact, no `wr` frame, no `trav` frame, and no BEGIN_WALLRUN or MANTLE dedi event.
- **Cause.** Every a2r_* trial started at the runner default origin, x −14750. Round 1 started at lane A, x −14100.
  - In `tools/hsd_trial.py`, `SCHEDULE_ORIGIN_PREFIX` maps only `"a2_"` to lane A. `"a2r_"` does not match that prefix, so the schedules fell back to `DEFAULT_ORIGIN`.
  - The sprint jump therefore happened about 753 u before the face instead of about 100 u. The player landed on the floor 0.758 s after the jump.
  - Every W release (0.5 / 0.70 / 0.74 / 0.78 / 0.9 / 1.1 s) and every back, jump or back+jump press happened on flat floor 370–475 u short of the face.
  - a2r_side, with W held for 2.0 s, got closest: a 240 u gap.
- **What the data do show is only flat-floor behaviour**, already known from M2:
  - releasing W at 299: −10.4 u/s per usercmd of ground deceleration;
  - back press: −199.5 walk;
  - jump pressed 0.35 s after the landing: post vz 204.2, below the 280.45 of a rested ground jump (M2 anti-multi-jump hold); horizontal 49 u/s.
- **None of the round-2 questions is answered.** That covers the jump / back / back+jump from the attached slide (wall bounce or not), the detach clock (contact vs release), a sideways climb, back cancelling a mantle, and the mantle-cancel threshold.
- **Effect on the model:** none. §6 and every parameter in `params.json` keep their round-1 values. The only new parameter entry is `round2_a2r_validity` = 0/50.
- **Fix before rerunning.** Add `"a2r_": LANE_A` to `SCHEDULE_ORIGIN_PREFIX`, or rename the schedules to `a2_*`. Check that the runner trial `origin` is (−14100, 6500, 294.92), then rerun both sessions. The round-2 code path in the script will analyse them once contact occurs: it currently reports validity only, and the per-question measurements (§7 items 2–4) still need to be added for a valid rerun.
