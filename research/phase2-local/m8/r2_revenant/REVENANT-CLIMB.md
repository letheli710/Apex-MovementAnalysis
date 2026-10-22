# M8 track R2: Revenant long climb, pounce wall-climb lock, Sparrow wall launch (feasibility probe)

Status: time-boxed probe for the item-10 expansion assessment (`../EXPANSION-ASSESSMENT.md` §1, §3). R5Flowstate S21, local offline, 120 fps, lane-A rock. Nothing is committed. Labels: **[meas]** client first-time MOVE-TRACE usercmds joined to client frames (dedi rows agree), **[fit]**, **[src]**, **[inf]**, **[unknown]**.

Tall walls: the M6-A2 rock is ~498 u tall, so a single rock (`--geometry h<H>`) reaches H ≈ 480 at most. Taller faces use the new `--geometry s<H>`: copies of the same rock stacked 470 u apart, with the top one at H. The joints between rocks leave a ~25 u bevel notch in the face (traced). At a joint the climb often loses ~70 u/s in one usercmd or detaches. These "impacts" come from the test geometry, not from the movement model, and the analysis flags them.

## TL;DR

| Question | Answer | Evidence, n |
|---|---|---|
| Does Revenant climb further than a normal legend? | **Yes, much further.** On the same wall with the same sprint jump, Gibraltar does the M6-A2 climb: 0.840 s, +96.9 u, final jump-up at floor + 149.6, then falls. Revenant keeps climbing. It **mantles 300, 500 and 800 u ledges** (climb 0.90 / 1.91 / 3.63 s). With W held 12 s it climbed **1181 u (to floor + 1231)** before a final jump-up | [meas] Revenant 5 + 5 + 3 mantles, 5 long climbs; Gibraltar 5 |
| Climb speed profile (Revenant) | Peak vz **226.0** (sd 0.17) about 95 u above the floor, then a speed line in height: **vz = k·(Z0 − z)**, k **0.0921 /s**, Z0 **floor + 2548** (rms 0.02 u/s on the clean face, z 100–400). vz is 225 at 100, 207 at 300, 188 at 500, ~162 at 700 and ~134 at 1000 (the last two include joint losses). The Gibraltar control on the same face: k 1.7454, Z0 floor + 180.4, as in M6-A2 | [fit] 25 climbs |
| Is the speed line tied to the contact height? | Probably yes. Z0 − z_contact ≈ 2493 (sprint jump, contact z 50), 2498 (pounce d150, contact z 202 at the climb start) and ≈ 2480 (pounce d500). So the climb starts at about 228–230 u/s whatever the contact height. Gibraltar: Z0 − z_contact ≈ 130, so the same ~227 u/s start | [fit] [inf] |
| How does a long climb end? | **Not settled.** 3/5 long climbs ended with a final jump-up (dvz +145…+160): two at floor + 1246.6 after 7.38 / 7.44 s, one at floor + 1112 after 7.21 s (a second climb from the floor after a joint detach). In 2/5, a joint impact at z ≈ 898 cut vz from ~147 to ~67. vz then fell to a constant **10.8 u/s creep**, with **no end for 6.8 s** until W was released at 11.75 s. There is no hang (W release → climb end within 0–0.18 s, mean 0.125, then a fall). With W held, neither a 2 s `wallrun_timeLimit` (census) nor any limit under 5.8 s applies | [meas] 5 long + 24 W-release ends; [unknown] end rule |
| Wall-climb lock after a pounce (source 0.75 s) | **Confirmed.** Pounce at pitch −15 from 150 u: the face is reached 0.333 s after the release, but the climb starts **0.855–0.89 s after the release** (0.51–0.56 s after contact). In between, the pounce carries the player up and along the face. From 500 u (contact 1.108 s after the release, past the lock), the climb starts 0.083 s after contact. Jump-in control: at contact (0.000 s) | [meas] d150 7 (2 walls), d500 5, control 5; [src] 0.75 s + ≤ 1 server tick |
| Sparrow climb high jump (optional probe 3) | **Exists.** With Sparrow (kit), a jump press 0.45 s into the climb with W held (input into the face) launches vz **670.82** (= √(2·750·300): the SDK `WALL_LAUNCH_MAX_HEIGHT` 300; props are not world brushes, so the ledge probe finds no ledge) and **442.8 outward**. Rise 302.8 u, apex 0.89 s later. With W still held, edge air control brings vx back to **+357 toward the face** after 1 s. Gibraltar control: an ordinary wall jump, 103 out, vz 118, rise 9.8. Sparrow's normal climb is the 100-class climb (+99.96 u) | [meas] 5 + 5 (+3 climbs) |

## What this means for HSD

- **Long climb is feasible to model.** On a smooth face it is the existing `ClimbAbility` with other numbers: the same ~227 u/s start, but a ~19× longer speed line (Revenant k 0.092 vs 1.745 /s), ending in a final jump-up or a mantle when a ledge comes within reach. The mantles at 300 / 500 / 800 u look normal (traversal 0.565–0.584 s).
- **Undecided for Unity: the end rule** (7.2–7.4 s, or ~floor + 1250 = `climbHeight`?, never after an impact). Use a design value (for example an end at 1200 u gain or 7.4 s) and label it [design].
- The pounce lock is a plain 0.75 s `disable_wall_run` timer from the release (plus up to one 10 Hz server tick). Unity needs only a timer on the pounce.
- The Sparrow wall launch is a one-per-ground-touch climb jump: vz for a 300 u rise and 150–450 outward. It fits on top of `ClimbAbility` and the M7-A wall jump. The ledge-aware height (ledge + 100) could not be tested on props.

## Data and exclusions

| Session (data/) | Legend | Geometry | Scored | Excluded / notes |
|---|---|---|---|---|
| `20261022_065841_M8R2_rev_s1400` | Revenant (kit) | s1400 (3 rocks, joints at floor + 466 / 936) | climb 5, pounce_d150 4, pounce_d500 5, jumpin_ctrl 5, climb_rel 3 | **r9606** (pounce_d150): the schedule ran 1116 frames instead of 955 (hitch on the first pounce of the session) |
| `20261022_070129_M8R2_rev_h300` | Revenant | h300 | climb 5 | none |
| `20261022_070354_M8R2_rev_s500` | Revenant | s500 | climb 5 | none |
| `20261022_070655_M8R2_rev_s800` | Revenant (kit) | s800 (joint at floor + 336) | pounce_d150 3, climb 5 | The warm-up (a pounce) hitched (1006 frames) and is not scored. 2/5 climbs and 2/3 pounces lost the climb at the joint (impact at z ≈ 319) |
| `20261022_072247_M8R2_rev_s1850` | Revenant | s1850 (4 rocks, joints at 446 / 916 / 1386) | climb_long 5 | none (impacts flagged per trial) |
| `20261022_070922_M8R2_gib_s800` | Gibraltar | s800 | climb 5 | none |
| `20261022_073207_M8R2_sparrow_h480` | Sparrow (kit) | h480 | spw_jump 5, climb 3 | The warm-up ran at 114.9 fps (warm-up, not scored) |
| `20261022_073445_M8R2_gib_spw_h480` | Gibraltar | h480 | spw_jump 5 | none |
| `20261022_065256_M8R2_explore` | Revenant, Vantage | s950 | exploratory runs r9501–r9523 (`hsd_trial.py` against a manually launched game; three runner manifests in one folder) | **not analysed**. They were used only to choose the schedules (the first long climb showed the mantle on a 950 u stack) |

- Every scored trial ran at 119.1–120.0 fps. Joins were complete except for ≤ 5 usercmds per trial.
- `s1400` climbs (W held 6 s) and pounce trials all ended **by the W release** (0.10–0.18 s later; one s1400 climb detached at the 936 joint instead), still rising at 133–147 u/s. They give lower bounds for the climb length, not the end. The long-hold session `s1850` was added for the end.
- Not done (time box): the pounce from a wall (`fromWall`), full-charge and non-zero-pitch pounces (assessment §1.2), the climb on a single smooth face taller than 480 u, and the Sparrow ledge-aware height.

## Effort for a full measurement and build

- Measurement: about 1 session to settle the end rule on a smooth tall face. A tall world wall needs a map trace scan; a smooth prop would also work if a suitable model exists. Pounce extras: about 1 session (`m4_pounce_*` and these schedules).
- Unity: S. `ClimbAbility` per-legend profile (start 228 u/s, contact-relative speed line, end rule as a design value), a pounce → 0.75 s climb lock, and a Sparrow wall-launch claimant (300 rise, 150–450 out, edge air control). New tall-wall course. Reference replays need the end rule decided.

## Rerun

```
cd research/phase2-local/m8/r2_revenant
py -3 revenant_analysis.py ../../data/20261022_065841_M8R2_rev_s1400 ../../data/20261022_070129_M8R2_rev_h300 \
  ../../data/20261022_070354_M8R2_rev_s500 ../../data/20261022_070655_M8R2_rev_s800 ../../data/20261022_072247_M8R2_rev_s1850 \
  ../../data/20261022_070922_M8R2_gib_s800 ../../data/20261022_073207_M8R2_sparrow_h480 ../../data/20261022_073445_M8R2_gib_spw_h480 \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --trials 5 -- --fps 120 --legend <revenant|gibraltar|sparrow> [--kit] [--no-census] --state-log --geometry <h300|s500|s800|s1400|s1850|h480> --schedule <m8r2_climb*5,...>` (the exact lists are in each `runner.json`). Schedules `m8r2_climb`, `m8r2_climb_long`, `m8r2_climb_rel`, `m8r2_pounce_d150/_d500` (pitch −15, exact-name origins), `m8r2_jumpin_ctrl` and `m8r2_spw_jump` are in `tools/hsd_trial.py`.
