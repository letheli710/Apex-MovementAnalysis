# M9-A1 (track R ①): mid-rope, end, air and re-mounts on ziplines

Status: measured in 8 local sessions (R5Flowstate, **local hybrid build: S21 client + S3 dedicated server + SDK**, offline,
120 fps, Gibraltar, empty-handed). Nothing is committed. One stdlib script produces every number here (rerun below).

Evidence labels: **[meas]** measured here; **[fit]** a bracket or rule checked against every trial; **[src]** SDK source;
**[inf]** interpretation; **[unknown]**. Every row says whether a behaviour is native (S21 client / S3 dedi) or an SDK
reimplementation.

## TL;DR

| Question (user report / plan) | Answer in R5 | Evidence |
|---|---|---|
| Can you mount mid-rope from standing nearby? | **Yes, anywhere along the rope** (start+50, 25 %, 50 %, 75 %, end−50, and 50/100 u beyond the start anchor). The grip is always the M6-A3 point: the rope point with the smallest angle to the view among points within 130 u of origin+72 (residual ≤ 1.6 u on 125 standing mounts; ≤ 8.1 u on all 408 mounts) | [meas] 263 standing presses |
| View cone | Mounted up to a rule angle of **33.18°**, refused from **35.94°** (no overlap) → **33.2° < θmax < 35.9°** (M6-A3: 27–40.7°) | [fit] 198 mounted / 65 refused |
| Reach | The rope must be within **~120 u of origin+72** (115.6 mounted, 128.0 refused; matches the SDK note "collector radius 120"); the grip point still lies within 130 u. Rope heights above the floor: **100, 130 (= HSD-Unity map ropes), 170** mount from standing (170 only looking up/along-up); **200 and 240 never** (out of reach); **80 never** (0/10, the hang point would be at floor level — cause [unknown]) | [meas] |
| "Looking at the rope" from beside it | Lateral 40 / 80 u: mounts when the view points **at** the rope (pitch up), not with a level view across it (55°/36° off) or away. Lateral 120: never (out of reach). Directly under with a level view across the rope: refused (90°) | [meas] 5 per cell |
| Which way does a mid-rope mount ride? | **Toward the view:** eye·rope_dir > 0 → toward the rope end; ≤ 0 (incl. exactly perpendicular) → toward the start (dedi `rev=1`). 5° either side of perpendicular already flips it. Sloped rope: same rule (down-slope view rides down) | [meas] all mounts |
| Can the direction change during the ride? | **No.** A 180° view turn after the 0.5 s mount state leaves the ride going the same way (horizontal); looking down after an upward vertical mount keeps going up | [meas] 5 + 5 |
| Ends | **No end refusal in R5.** A grip within ~90 u of the end the view points to rides **away** from it (grip 50 / 70 u from the start, view to the start: rides toward the end). A grip just outside (110 u) rides toward that end, reaches the 90 u stop-short in 0.19 s and auto-detaches at **600 u/s** (a launch from rest). Beyond the anchor (−50/−100 u) the grip is near the anchor and the ride goes away from it | [meas] 5 each |
| Re-mount mid-rope after dismounting | Works from the ground at once (crouch-off or jump-off, land, use: 10/10). **In the air it is refused for ~0.33–0.40 s after any detach** (jump-off: refused ≤ 0.33 s, mounted from 0.33–0.37 s; crouch-off: refused at 0.36 s, mounted at 0.40 s), independent of height. The refusal happens **before** `Zipline_Use` on the client (no diag line on either side) → a native S21-client gate; wiki `useZiplineCooldown 0.4` | [meas] 95 re-presses |
| Air mount / Mid Air Interact | **Works** (65/65 on client and dedi): standing jump under the rope and 20 / 40 / 80 u beside it, view 0 / 45 / 80° off the rope, use at the apex, rising, or held. No height gate (origin+72 from 14.6 u below to 26.8 u above the rope). The M6-A3 refusal (120 u, 2022 note) was out of reach plus, for its hold case, the client/dedi split below | [meas] |
| Re-grab budget | Ground mount → 2 air re-grabs (client cooldown printed 0.1 → 0.2 → 1.0 s) → the 3rd air re-grab (0.42 s after detach) is refused; landing resets (cd 0.1, SDK `left=3`). Both the S21 client ladder (1.0 s after the 3rd grant) and the SDK "latest Apex" hop-regrab count (3) refuse here, so this build cannot tell which one S21 used. The 3 s refill was not tested | [meas] 10; [src] |
| Super Jump mid-rope | Exists mid-rope (K = 2: +218 u apex, as M6). Window for the 2nd press after a jump-off on the command after the mount: **K 12 5/5, K 18 5/5, K 24 3/5, K 30 0/5** (≈ 0.2 s coyote from leaving the ground) | [meas] 25 |
| Lurch after a jump-off | **No lurch window:** a D press 3 commands after the jump-off gives \|Δv\| 4.18 = AirAccelerate | [meas] 5 + 5 ctrl |
| Carry (R-12) | Running across the rope (≈ 285 u/s along +Y), use, jump on the **next** command: exit (0, **285**, 289.8) — the run velocity, not rope-aligned. Jump 2 commands later: rope-aligned (ride speed 8.3) | [meas] 5 + 5 |
| Entry speed | Sprint along the rope → ride starts at 299.7; slide → 395 (kept flat until the rest curve passes, then +400 u/s² to 600). Same floor rule as M6-G | [meas] 5 + 5 |
| Crouch / slide mounts | With a level view **0/5** (crouched standing and sliding); looking 45° up **5/5** both. The crouched reach is shorter with a level view [cause unknown] | [meas] 20 |
| Vertical rope, mid height | From a ledge level or looking up: rides **up** (grip = min-angle point). Looking down (pitch +30): the **client** predicts a mount, the **S3 dedi never dispatches the use** → corrected back after 0.04–0.09 s (no ride). From the floor looking down 60°: no attempt. Air mounts (floor jump, jump off the ledge) ride up. Jump-off from a vertical rope: 400 along the view yaw + 289.8 up | [meas] 5 each; hybrid split |

## What this means for HSD (no Unity change made here)

- Mid-rope standing mounts, mid-air interacts and ground re-mounts are **normal Apex behaviour in R5**; the interaction is
  bounded by: rope within ~120 u of origin+72, view within ~34° of the rope point, and a ~0.33–0.40 s air re-grab lockout
  after any detach (ground re-mount is immediate).
- HSD-Unity map ropes are 130 u above the floor (flat, chain, uphill start), the height used in most tests here. From
  standing directly under such a rope with a level view along it the R5 rule angle is 26.5° (accepted); a level view
  *across* it is refused in R5 too — the player must look at it.
- Read from the Unity source only (no Unity opened): `Rail.attachRadius = 48` exists in `WorldGeometry.cs`; and M8-A's
  `refuseMountAtEnd` refuses a grip within the 90 u end zone where R5 instead **reverses** the ride (and launches at 600
  just outside it). These are candidate causes for the playtest report, not verified.
- The air re-grab lockout explains "re-mount after a mid-rope dismount fails" if the press comes in the air within
  ~0.35 s; it is a timing rule, not a position rule.

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_123054_M9R_zipA` | 29 standing schedules × 5 (positions × views on r100/r130, cone sweep yaw 25–37°, beyond-anchor, 85°/95° views) | none |
| `20261022_130307_M9R_zipA2` | 32 × 5 (lateral 0–120 × 4 views at mid / start, slope, r170/r200/r240/r80) | r12343 (364 frames vs 361), r12387 (112.2 fps) |
| `20261022_131501_M9R_zipB1` | 24 × 5 (air mounts, jump-off re-mounts K 2–104, use spam, crouch-off air re-mounts, budget chain v1) | none |
| `20261022_132605_M9R_zipB2` | 24 × 5 (jump-height sweep, turn 180, ground re-mounts, super jump K, lurch, sprint/slide, carry v1, end-zone grips) | none |
| `20261022_133018_M9R_zipD` | lockout bracket (crouch-off 0.25–0.40 s), budget chain v2 | none |
| `20261022_133412_M9R_zipE` | carry v2, crouch / slide-release mounts | r13023 (478 frames vs 475) |
| `20261022_134042_M9R_zipC` | vertical rope 11 × 5 (geometry m3 + m9zipv) | r13108 (115.2 fps) |
| `20261022_134516_M9R_zipF` | budget chain v3, carry v3, crouch / slide mounts looking up | none |
| `20261022_121651_M9R_zip_pilot` | pilot (2 trials × 6), used only to check the pipeline | not analysed |

Design misses (documented, not hidden): budget v1 re-pressed inside the lockout and v2 ran into the rope end (v3 is the
result); carry v1 aimed too flat and carry v2 used the wrong yaw (v3 is the result); slide v1 / crouch v1 are reported as the
level-view result. All fps 118.5–120.0 (±3 % rule unchanged). The client `[ZIPRAIL-USE]` / dedi `[ZIPRAIL-USE]` /
`[ZIPRAIL-FIND]` lines come from `bridge_zip_disc_diag 1` (both) and `bridge_zip_mount_diag 1` (dedi, new
`--server-cvar` runner option).

## Geometry

`--geometry m9zip` (`tools/hsd_trial.py`, `M9_ROPES`): flat ropes 1600 u long at 100 (y 6800), 130 (y 6500), 170 (y 5900,
1500 u), 80 (y 5600, 1000 u) above the floor, a sloped rope 60 → 260 u (y 6200), and after session A r200 (y 7100) and
r240 (y 7300), all `CreateZipline(start, end, false, 100)`. `m9zipv`: a vertical rope floor+20 → floor+900 at x −13790, 84 u in
front of the 232 u lane-A rock (geometry m3). Rope heights used for the user question: **130 u above the floor** (= the
HSD-Unity `PracticeMap` flat / chain ropes; the yard / uphill ropes start at 130; the tower rope runs 0 → 500).

## Model for Unity (per usercmd; hybrid-build values)

```
MOUNT (IN_USE press edge, ground or air):
  P = origin + (0,0,72); e = eye direction
  candidate: a rope whose nearest point is within ~120 u of P                                    [fit 115.6 / 128.0]
  Q = argmin angle(e, Q - P) over rope points with |Q - P| <= 130                                [fit, M6-A3]
  accept if angle(e, Q - P) <= ~34.5 deg (33.2 < theta < 35.9)                                    [fit]
  refuse while airborne within ~0.33-0.40 s of the last detach                                    [meas, native client gate]
  air re-grabs after a ground mount: 2, the 3rd refused (client cd 0.1/0.2/1.0; SDK count 3); landing resets [meas]
  direction: dot(e, rope_dir) > 0 -> toward the end, else toward the start; fixed for the ride   [meas]
  end zone: if the grip is within ~90 u of the end it would ride to, ride the other way            [meas, 70 < limit < 110]
  entry speed: speed along the rope kept as the mount-state floor (sprint 299, slide 395)        [meas]
  crouched / sliding with a level view: refused (look up and it mounts)                           [meas, cause unknown]
VERTICAL: rides up from level / upward views; a downward mid-height mount is client-only (dedi refuses)  [meas, hybrid split]
JUMP-OFF: unchanged (M6-A3); no lurch window; super jump 2nd press up to ~0.2 s after leaving the ground [meas]
CARRY: a jump on the command right after the mount keeps the pre-mount velocity (285 across the rope) [meas]
```

## Track D spec check

| Spec | Result |
|---|---|
| R-12 carry | **agree** (285 kept, not rope-aligned; jump 2 cmds later rope-aligned) |
| R-13 super jump edge | **agree** (applied ≤ 18, 3/5 at 24, 0/5 at 30 commands ≈ 0.2 s) |
| R-14 Mid Air Interact 20/40/80 u, 0/45/80° | **agree** (45/45 accepted on the dedi); the M6-A3 refusal is explained by reach |
| R-15 re-grab limit | **partly**: 2 air re-grabs then refused; a 4th could not be reached; 3 s refill not testable here |
| R-16 mid-rope, heights 120/160/200/240 above origin | **agree** for 130/170 (direction = look); 200/240 out of reach (collector ~120 from origin+72) |
| R-17 vertical mid mount | look up / level → up (**agree** "prefers up"); look down → client mounts, S3 dedi refuses (**not testable** for S21) |

## Open questions

1. Why r80 (rope 80 above the floor) never mounts from standing, and why a crouched level view fails — two gates
   upstream of `Zipline_Use` that this data does not separate.
2. The exact lockout source (one timer of ~0.35 s with frame phase, or different for jump-off and crouch-off).
3. A downward vertical ride (client accepts, S3 dedi refuses): which is S21 retail? Needs an S21 server or footage.
4. Which re-grab limiter S21 had (client ladder vs the SDK's "latest" count); the 3 s refill.

## Rerun

```
cd research/phase2-local/m9/r_zip
py -3 zip_analysis.py ../../data/20261022_123054_M9R_zipA ../../data/20261022_130307_M9R_zipA2 \
  ../../data/20261022_131501_M9R_zipB1 ../../data/20261022_132605_M9R_zipB2 ../../data/20261022_134042_M9R_zipC \
  ../../data/20261022_133018_M9R_zipD ../../data/20261022_133412_M9R_zipE ../../data/20261022_134516_M9R_zipF \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --label M9R_zip<X> --trials 5 --run-base <N> --batch-base <N> -- --fps 120 --legend gibraltar
--no-census --state-log --geometry m9zip (C: m3,m9zipv) --server-cvar bridge_zip_mount_diag=1 --both-cvar bridge_zip_disc_diag=1
--schedule <list>`; the exact lists are in each `runner.json`. Schedules `m9z_*` (standing, parametric name
`m9z_<rope>_<pos>_l<lateral>_<view>`), `m9zd_*`, `m9zv_*` are in `tools/hsd_trial.py`. Loader: `zip_load.py` (uses
`../../m6/a2_climb/a2_load.py`).
