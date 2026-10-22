# M8 R2: Horizon Gravity Lift gaps and the Horizon landing (R5Flowstate S21, local offline)

Status: measured in 3 local sessions (Horizon with kit; Gibraltar control without kit; 120 fps, lane C; the lift is deployed by the reset 120 u ahead, as in M4). Nothing is committed. Labels: **[meas]** client first-time MOVE-TRACE usercmds, **[fit]**, **[src]**, **[inf]**. This complements `../../m4/lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md` §1 and only covers its open points.

## TL;DR

| Question | Answer | Evidence, n |
|---|---|---|
| Top hover | Hover band starts at 0.9 × 1200; **eject 0.5002 s (sd 0.0003) after the hover starts**, 400 along the flat view yaw + 450 up (post vz + g·dt/2 = 450.000). Unchanged from M4 | [meas] 10 rides |
| Jump during the hover | **No effect** (5/5), as M4 found for the rise. There is no jump-exit boost in S21 | [meas] 5 |
| Jump just after the eject | No effect (Horizon has no air jump) | [meas] 5 |
| W held at the top | The player steers at 170 u/s inside the column, but still leaves only by the hover timeout (eject at 0.501 s after hover start, 69–82 u from the centre), direction = view (= radial here) | [meas] 5 |
| Side exit (D held) at 0.5 / 1.5 / 3.0 s after entry (z ≈ 278 / 603 / 1054 above the floor) | Full eject (400.01 horizontal, 450 up) **radially outward from the lift centre** (direction − radial = 0.00° in 15/15; view yaw differs by 124° / 102° / 92°) | [meas] 15 |
| Walk straight through (W held) | Leaves the far side at 1.04 s, z ≈ 301, full eject 400/450 along +X | [meas] 5 |
| Short dwell (< 0.5 s) | **Eject scaled**: both components × s with s = (t_eject − 0.016…0.030 s)/0.5 (t from the entry usercmd); measured s 0.54–0.80 for exits at 0.30–0.42 s. Confirms the M4 source rule min(dwell/0.5, 1) with a ~2-usercmd offset | [meas]/[fit] 10 (lift centred 80 / 83 u to the side of the walk line) |
| Air control after the eject (Horizon) | AirAccelerate at **800 u/s²** along the wish (per usercmd 799.5–800.5). Sideways: the wish component reaches the **92 cap** (80·msc) within about 0.1 s, then creeps to 93.7 at landing. Backward: 400 → −93.7 u/s, i.e. Horizon can cancel and reverse the eject in ≈ 0.6 s | [meas] 5 + 9 |
| Re-entry | After a backward air-brake the player fell back into the column and was lifted again **2.02–2.19 s after the eject** (entry sets v_h to 50 toward the centre and vz 5 → 300). Consistent with the 2.0 s re-entry block [src]; a re-entry earlier than 2 s was not attempted | [meas] 9 |
| **Horizon landing vs a normal landing** (same lift eject, impact |vz| 1347) | **Horizon: no slowdown at all** (f0 1.000, msc stays 1.15; v_h 400 then the normal 1250 u/s² friction; with W: 199.5 after 0.25 s). **Gibraltar: full stop** (f0 0.000, v_h 400 → 0 on the landing usercmd; msc ×(t/1.0)² for 1 s; with W 7.6 u/s at 0.25 s, 36.8 at 0.5 s, 190 at 1.0 s) | [meas] Horizon 15, Gibraltar 10 |

So the Spacewalk soft landing **is a movement difference**, not only visual: Horizon's `landSlowdownDuration` 0 (M4 census) removes the M4 landing slowdown entirely. The control also confirms the M4 landing law (f0 from vz²) on a normal-gravity fall (M4 open question 4): |vz| 1347 > 1093 gives f0 = 0 as predicted.

## Data and exclusions

| Session (data/) | Legend | Scored | Notes |
|---|---|---|---|
| `20261022_041952_M8_lift1` | Horizon (kit) | ride, through, side_t05/t15/t30, top_w, top_jump, ej_jump, ej_strafe 5 each; ej_back 4 | **Trial 8250 (ej_back) timed out** (the client schedule thread printed no end line within 100 s); `hsd_trial.py` crashed before writing `runner.json`. The manifest was **rebuilt** from the runner stdout and the client `[HSD-SCHED]` lines (`runner.json` has `reconstructed: true`; 49 scored trials with their measured fps). `hsd_trial.py` now records a timeout as a failed trial and still writes the manifest. land_w was not reached |
| `20261022_043620_M8_lift2` | Horizon (kit) | land_w, liftoff80_w, liftoff83_w, ej_back, ride 5 each | none |
| `20261022_044044_M8_lift_ctrl` | Gibraltar (no kit; the lift is deployed by script) | ride 5, land_w 5 | none |

Side-exit trials land on lower terrain (about 440–470 u below the field floor, off the lane); their landings are not used for the landing comparison. `ej_back` trials re-enter the lift (see above) and have no clean landing.

## Model updates for Unity (`SustainedThrustVolume`)

```
eject scale  s = clamp((t_in_lift - ~0.02 s) / 0.5, 0, 1)    # [fit] n 10; M4 src min(dwell/0.5, 1)
eject dir    radial from the centre when leaving sideways; view yaw at the top timeout (M4)
jump input   ignored during the rise and the hover (no exit boost)            [meas]
after eject  normal air with the legend air values (Horizon 800 / cap 80*msc)  [meas]
landing      Horizon: no landing slowdown (landSlowdownDuration 0); others: M4 law (f0 from vz^2)   [meas]
```

## Open questions

1. The exact short-dwell offset (0.016 s at 0.40 s, 0.022–0.030 s at 0.30 s; scale_v is 0.005 below scale_h at 0.30 s).
2. Whether a re-entry inside 2.0 s is blocked (the observed re-entries all came after 2.02 s).
3. The lift expiry (10 s lifetime) while riding a second time ejected with a small scale (v_h 40–54, vz 42–57) in 4 trials; not studied.
4. The trial 8250 client hang (an ej_back trial that re-entered the lift); cause unknown, not reproduced in lift2.

## Rerun

```
cd research/phase2-local/m8/r_lift
py -3 lift_analysis.py ../../data/20261022_041952_M8_lift1 ../../data/20261022_043620_M8_lift2 \
  ../../data/20261022_044044_M8_lift_ctrl --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --trials 5 -- --fps 120 --legend horizon --kit --no-census --state-log --schedule <m8_lift_* list>`; control `--legend gibraltar` without `--kit`.
