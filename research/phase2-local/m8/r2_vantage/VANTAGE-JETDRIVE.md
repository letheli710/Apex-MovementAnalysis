# M8 track R2: Vantage Echo relocation / jet drive (feasibility probe)

Status: time-boxed probe for the item-10 expansion assessment (`../EXPANSION-ASSESSMENT.md` §2). R5Flowstate S21, local offline, 120 fps, lane C, legend Vantage with kit. One scored session; nothing is committed. Labels: **[meas]** client first-time MOVE-TRACE usercmds (the dedi rows of the same usercmds agree, see below), **[src]**, **[inf]**, **[unknown]**.

## TL;DR

| Question | Answer | Evidence, n |
|---|---|---|
| Is Vantage in the build, and can the runner trigger the move? | **Yes, both ways.** (1) The **real tactical** works from the runner: a tap sends Echo along the aim (pitch 0: Echo settled 1969 u ahead, 246 u above the floor), and a 1 s hold launches the jet drive to Echo (`CheckForHoldInput_Thread`). (2) The **EVAL shortcut** `BeginJetDrive(787, 1575, mover, mover, <0,0,-69>, timeout)` + `EnableJetDriveDoubleJump(<512,0,394>, 0.5)` works on a spawned script mover, with no AI involved | [meas] Echo 5/5; shortcut 40/40 |
| Wind-up | `BeginJetDrive` → leave the ground **0.204 s** later on the dedi (SDK cvar `jetdrive_delay_time` 0.2) | [meas] 40 |
| Launch | **\|v\| 943.1** (= 787 × `jetdrive_initial_speed_mult` 1.2, held for ~0.2 s), elevation 27.7° / 24.7° / 23.7° for 400 / 800 / 1200 u targets (Echo 1976 u: 26–28°) | [meas] |
| Speed profile | 943 for 0.2 s, then easing toward the 787 path speed (1200 u: 897 / 859 / 830 / 808 / 795 at 0.4…1.2 s), then braking near the target: the brake starts about 180 u out, which matches the SDK cvar `jetdrive_decel_dist` 180 | [meas] 5 per distance |
| Arrival | The path **passes through the target point**: closest approach 4.2 u (800 u), 7.7 u (1200 u), 14.3 u (Echo, 1976 u), at 1.025 / 1.51 / 2.45 s. That is a mean of **782 / 787 / 801 u/s**, about the 787 path speed. A short drive misses: at 400 u the arc passes **84 u above** the target (0.53 s). The drive does not stop at the target: the player brakes, falls and lands 49–129 u past it (66 u at 800) | [meas] 5 each |
| Arc | Apex 136 / 151 / 189 u above the floor (target 51 u above the floor) for 400 / 800 / 1200 u; 338 u for Echo at 246 u. This is lower than the SDK `jetdrive_initial_vert_offset` 0.4 × distance would suggest [unknown] | [meas] |
| Double jump at the end | **Applied 12/12** for presses 15–178 u from the target (0.76–1.01 s into an 800 u drive). The press **replaces** the velocity: vz = **394.0** (post vz + g·dt/2, exact) and horizontal **492.8–506.6** along the travel (source 512; it drops slightly with later presses [unknown]). In the explore round, a press at 0.5 s (~385 u out, outside the 180 u window) gave nothing [exploratory, n = 1] | [meas] 12 |
| Crouch | A crouch 0.41 s into the drive scales the velocity by **0.800** (SDK `jetdrive_duck_cancel_vel_frac`) and ends the drive. Afterwards v_h stays constant at 686.3 and vz falls at g = 750 (6.25 u/s per usercmd). During the drive vz fell ~9.9 u/s per usercmd instead | [meas] 3 |
| Moving target | **Tracks it.** Mover moving 300 u sideways in 1.0 s: the path bends, passes **1.7 u** from the moving target point at 1.11 s and lands 3.8 u off the start→target line. Mover receding 600 u in 1.5 s (400 u/s): it catches up and passes 10.4 u from it at 1.75 s (mean 501 u/s along the start→target line) | [meas] 5 + 5 |
| Dedi vs client | The same usercmds agree within 0–1.6 u on fixed targets, 2–8 u on moving targets and 13–14 u on the Echo drive. Client-side MOVE-TRACE is continuous during the drive (no gap as in a traversal) | [meas] 45 |

## What this means for HSD

- Echo relocation is **measurable and buildable** without the Echo AI. The motion is a kinematic drive toward a point or a moving entity: launch at 1.2 × path speed, path speed 787, a braking zone of ~180 u, then ballistic flight past the target. There is a double-jump window inside the braking zone (vz 394, horizontal ~500 along the travel, replacing the velocity), and a crouch cancel (× 0.8).
- The "dynamic anchor" part of the assessment is confirmed: `BeginJetDrive` tracks a moving entity. The same code could serve moving grapple anchors later.
- Distinct from Loba (`SHELVED-ABILITIES.md`): this is not a teleport. It is a 0.5–2.5 s visible flight that keeps ~500–800 u/s on arrival and ends in a double jump.

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_071639_M8R2_vantage` | jd_d400 / d800 / d1200 5 each; d800_dj90 / dj100 / dj110 / dj120 3 each; d800_duck 3; d800_mvy 5; d800_mvx 5; echo_send_launch 5 (45 scored, 119.4–120.0 fps) | none |
| `20261022_065256_M8R2_explore` | exploratory r9511–r9523 (first shortcut runs, two-tap and hold-release Echo inputs, early double-jump press) | **not analysed**, only used to design the schedules (see the double-jump note above) |

- Server lines (`[R2-JD] begin`, `[R2-ECHO]`) use the dedi clock, which differs from the client clock. The analysis matches them to trials by order: 41 begin lines for the 41 jd trials including the warm-up, and 5 Echo groups for the 5 Echo trials. It aligns time through the dedi LEAVE_GROUND event.
- Not done (time box): drives into obstacles (stuck kick), timeout expiry, jump-back (0.5 fraction) and sideways double-jump directions (view and travel were both +X here), Echo placement rules (range, perch, the 60° view / line-of-sight gate), launches from the air or at speed.

## Effort for a full measurement and build

- Measurement: about 1 session. Steering law (fit the path toward fixed targets at 3–5 distances and heights), double-jump direction (view vs travel, jump-back), window edges, timeout, obstacle behaviour, and a few real-Echo placements.
- Unity: M (1–2 days). A kinematic `JetDriveAbility` toward a placed point or entity with the measured launch / cruise / brake, a double-jump claimant for the M8-A `JumpArbitration`, crouch cancel, and drive exclusivity with grapple and jets. Echo itself can be a placed marker (aim ray, max range), with no AI. Steering-law details stay [design] until fitted.

## Rerun

```
cd research/phase2-local/m8/r2_vantage
py -3 vantage_analysis.py ../../data/20261022_071639_M8R2_vantage --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --trials 5 --run-base 9701 --batch-base 9701 -- --fps 120 --legend vantage --kit --state-log --schedule m8r2_jd_d400*5,m8r2_jd_d800*5,m8r2_jd_d1200*5,m8r2_jd_d800_dj90*3,m8r2_jd_d800_dj100*3,m8r2_jd_d800_dj110*3,m8r2_jd_d800_dj120*3,m8r2_jd_d800_duck*3,m8r2_jd_d800_mvy*5,m8r2_jd_d800_mvx*5,m8r2_echo_send_launch*5`. The mover spawn, the delayed `BeginJetDrive` thread and the Echo position logger are `SCHEDULE_PRE` entries (`_r2_jd_pre`, `_R2_ECHO_LOG`) in `tools/hsd_trial.py`.
