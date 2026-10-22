# M8-C in HSD-Unity: Octane pad double jump, Horizon gravity lift and Spacewalk

- Branch `m8c/pad-dj-lift` of HSD-Unity (commit `1982b46`), from main `8e959bc` (M8-B merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M8-PLAN.md](../M8-PLAN.md) items 8–9. Inputs (track R, lead-verified): [../r_pad_djump/PAD-DJUMP.md](../r_pad_djump/PAD-DJUMP.md), [../r_lift/LIFT.md](../r_lift/LIFT.md). Playtest guide (Chinese): [../PLAYTEST-GUIDE-M8C.md](../PLAYTEST-GUIDE-M8C.md).

> **Acceptance status (two separate labels)**
> - **「数值通过」**: every rule below is checked by unit tests, a real-input demo with a failure variant, the course fuzz and a skill fuzz; every R5 replay is byte-identical; every older demo verdict (110 lines, diffed against the M8-B build), the M5 route and the course lap (80.82 s) are unchanged (§7).
> - **「真人手感未验收」**: nobody has played it. The 0.108 s grant (an early press does nothing), the two double jumps together, the side-exit and soft-landing feel and every [design] value are open until the user has played them.

Labels: **[meas]** R5 measured (M8 track R unless noted), **[fit]** a formula checked against the rows, **[src]** script source, **[design]** an HSD choice.

## 1. Audit (before the build)

| Area | What existed | Gap | Decision |
|---|---|---|---|
| Pad double jump | M8-A rank `JumpRank.PadDoubleJump` (300) and a test stub; `JumpPadParams` noted "double_jump_delay 0.1 s not modelled" | the ability did not exist | new `PadDoubleJumpAbility` (§2), its own claimant |
| Lift hover / eject | M4 model: hover band 0.9·1200, eject after 0.5 s hover, 400 view / radial past 40 u + 450 up | matches R5 (0.5002 s, 400 / 450) | unchanged |
| Jump in / after the lift | arbiter masks an airborne press while the lift drives; **no lift jump boost exists in the code** | none to remove | unchanged; tested (Reference: nothing; Fun: the HSD generic air jump after the eject [design]) |
| Side exit | radial past 40 u from the axis | matches R5 (0.00° in 15/15, full 400 / 450) | unchanged; tested at three heights |
| Short dwell | M4 src rule min(dwell/0.5, 1) | R5 [fit] (dwell − 0.0206)/0.5 | game bodies use the fit; the replay keeps M4 (§3) |
| Air control after the eject | Horizon profile 800 / cap 80·msc = 92 (M4 census) | the eject (a launch) opened the M5 lurch window: a back key 0.25 s after the eject lurched (209.3 brake) and reversed the eject in 0.36 s; R5 shows plain 800 u/s² from the first command (reversal ≈ 0.6 s) | **Reference: the lift eject opens no lurch window [meas]**; Fun keeps the M5 [design] "lift eject → lurch" (§3) |
| Lateral movement in the lift | steer 170 / 2000, centring 25–50 | W at the top: R5 leaves by the timeout 65.7–78.5 u out; Unity 74.9 u | unchanged |
| Re-entry | 2.0 s block [src] | R5 re-entered at 2.02–2.19 s; < 2 s unmeasured | unchanged ([src], earlier = [design]) |
| Spacewalk soft landing | `SkillSlotSystem.Build` already sets `LandingSlowdown.duration = 0` when the loadout has `horizon_air` (M5) | only "visual" in the M4 note; now measured as movement (f0 1.000 vs 0.000) | unchanged, tested in both configs; Valk-Horizon is the only preset with it |
| Spacewalk air control | `horizon_air` (800 / 80) | measured [meas] | unchanged (the creep from 92 to 93.7 before landing is not modelled) |

## 2. Octane pad double jump (`Abilities/PadDoubleJumpAbility.cs`)

### 2.1 Measured vs implemented

| Rule | R5 (PAD-DJUMP.md) | Unity | Class |
|---|---|---|---|
| Granted after a pad launch | yes, 123 DJ | `PAD_DJ_GRANT` on the command whose pad launch the arbiter applied (slot pad and map pads) | [meas] |
| Earliest press | refused ≤ 0.0834 s (20/20), 0.1081–0.1083 mixed (3/5 accepted at 0.1084), always from 0.133 s; src `wait 0.1` | available when now − t_launch ≥ **0.108 s** (120 Hz: the 13th command, 0.1083 s; 60 Hz: 0.1167 s; 144 Hz: 0.1111 s). The mixed band is resolved as granted | [meas] / [design] grant point |
| Once per launch | second press: nothing (0/5) | `pending` cleared on use; a new launch re-grants | [meas] |
| Early refused press | does not consume (5/5 later DJ) | `PAD_DJ_EARLY`, grant kept | [meas] |
| Jump held through the launch | never fires (0/5); a new press after the release does (5/5) | press edges only (SkillBody) | [meas] |
| Normal jump + air press | no DJ (0/5) | grant only from a pad launch | [meas] |
| Landing / zipline | cleared on landing (dedi 0/5); zipline [src] | `PAD_DJ_CLEAR_LAND` / `_ZIPLINE` | [meas] / [src] |
| Vertical | pre vz ≥ 360.04 → +201.81; ≤ 357.35 → = 409.25 (discontinuous) | +201.81 / = 409.25, boundary **358.7**, applied before the move (post = … − g·0.8·dt) | [meas], boundary [design] |
| Horizontal, no key | unchanged (any view) | unchanged (exact) | [meas] |
| Horizontal, key held | v_h − 240·v̂ + 240·ŵ, then AirAccelerate (max err 0.015) | same, exact | [fit] |
| Key pressed on the DJ command | D: −264.1 / +272.1; S: net 449.3 (unmodelled) | **treated as held** (step with that command's wish), and **no lurch on that command** (`CommandModifiers.suppressLurch`); option `sameCommandKeyAsHeld` | [design] (error ≈ 25–32 u/s vs R5; the held rule + lurch would be ≈ 180 off) |
| Lurch after the DJ | window re-anchored: D 0.025 s after → \|Δv\| 212.55 (3.87 without DJ) | `jumpTime = now`; the D press gives lam 0.7, \|Δv\| **209.3** (the usual 0.7 × sprint cap) | [meas]; the 212.55 clamp is a gap |
| Stand / crouch / walk / sprint / jump-in | the same +201.81 | tested, same | [meas] |
| Landing after a DJ | M4 law (max err 0.00055), impacts to 1336 → f0 usually 0 | the M4 law unchanged (tested: f0 0 after an early DJ) | [meas] |
| Upward ceiling | pad 1028.6 + DJ 201.8 = 1230.4 | bodies with the pad DJ get `maxUpSpeed` 1250 (was 1100 for all; 1100 would cut the measured DJ); others keep 1100 | [design] |

### 2.2 Pad DJ vs the HSD generic double jump

| | Octane pad double jump | HSD generic double jump (M7-A) |
|---|---|---|
| Source | R5 S21 measured | HSD design |
| Class / claimant | `PadDoubleJumpAbility`, rank 300 | `DoubleJumpAbility`, rank 200 |
| Eligibility | a pad launch, ≥ 0.108 s after it | airborne, ≥ 0.1 s after the takeoff, air jumps left |
| Count / consumption | one per launch | `maxAirJumps` (1) per airborne phase |
| Reset | a new pad launch; cleared by landing / zipline | landing, wall-run, hang, zipline |
| Effect | +201.81 / = 409.25; held key 240 step | vz = max(vz, 259.8); v_h re-aimed half-way, \|v_h\| kept |
| Configs / loadouts | both configs, Octane preset (any body whose loadout has the jump pad); key 5 switch | Fun (and the Reference toggle 9) |

Both on (Fun + Octane): a press while the pad DJ is available is the pad DJ; the generic claim is `LOST` and keeps its count; the next press is the generic air jump (`m8c_pad_dj_generic`, `BothDoubleJumpsOnThePadOneWinsTheGenericKeepsItsCount`). A press before the grant goes to the generic one if it is eligible (≥ 0.1 s after the takeoff), and the pad DJ stays for a later press. So one flight can hold three jumps' worth of lift; whether both may be equipped in the final game is **not decided**.

Scope decision [design]: map pads grant the DJ only to bodies that carry the ability (the Octane preset). In R5 anyone launched by a pad gets it [src]; giving it to every loadout would change the M8-A pad / air-jump demo and the generic-DJ tests. The M8-A demo `m8_pad_airjump` turns it off for its run (`MovementDemoScript.padDoubleJump = false`): it is about the generic air jump.

Replay safety: the ability exists only on game bodies built by `MovementConfig.CreateBody`; the replay kit has no arbitration and no pad DJ; `JumpPadParams` is unchanged (its report fields are asserted); the lift fields are `[NonSerialized]` and neutral by default.

## 3. Gravity lift and Spacewalk changes

| Change | Before | Now | Class |
|---|---|---|---|
| Short-dwell eject scale (game bodies) | min(dwell/0.5, 1) | clamp((dwell − 0.0206)/0.5, 0, 1); R5 exits at 0.30–0.42 s gave s 0.54–0.80 → Unity 0.559–0.799 | [fit]; the replay keeps M4 (`ejectScaleOffset` 0, not serialised) |
| Lift eject and the lurch window | every launch opened it (M5 `launchOpensLurchWindow`) | `MovementConfig.liftEjectOpensLurchWindow`: Reference false (the back key reverses 400 → −92 in 0.61 s, 800 u/s² from the first command, as R5), Fun true | [meas] / Fun [design] |
| Spacewalk | duration 0 for `horizon_air` loadouts (M5) | unchanged; tests: Horizon f0 1 with W → 199.5 u/s at 0.25 s (R5 199.5); normal legend f0 0, W → 9.9 / 35.7 u/s at 0.25 / 0.5 s (R5 7.6 / 36.8) | [meas] |

Loadouts: the Octane preset (Pathfinder-Octane, key 1) has the pad DJ in both configs; Valk-Horizon (key 2) has Spacewalk (air 800 / 80 and no landing slowdown) in both configs; every game lift (slot and map) uses the measured offset.

## 4. Demos (real input through Advance → Step)

| Id | Config / loadout | Success (shift 0) | Failure (shift) |
|---|---|---|---|
| `m8c_pad_dj` | Ref / Octane | world pad, Space 0.208 s after the launch: +201.81, once | −0.15 s: Space at 0.058 s, refused, nothing spent, no DJ |
| `m8c_pad_dj_hold` | Ref / Octane | jump-in with Space held through the launch: nothing; new press 0.65 s in: DJ | +2.5 s (release moved, `DemoSegment.endOnly`): held through the flight, never fires |
| `m8c_pad_dj_generic` | Fun / Octane | 1st press = pad DJ (generic kept), 2nd = generic air jump | −0.2 s: 1st press too early for both, the 2nd gets the pad DJ instead |
| `m8c_pad_dj_lurch` | Ref / Octane | D held, DJ 0.6 s after the launch (step exact), A 0.1 s later lurches +31° (launch window closed) | +0.5 s: window closed, no lurch |
| `m8c_lift_side` | Ref / Valk-Horizon | A 2.4 s after entry: exit at z 878, 400 / 450 radial, 89° from the view | −2.37 s: dwell 0.27 s, eject scaled to 197 / 221 |
| `m8c_lift_hover_jump` | Ref / Valk-Horizon | Space in the hover: masked; eject 0.517 s after the hover start, 400 / 450 along the view | +0.75 s: the press is after the eject and engages the Valkyrie jets (the loadout's jump ability, not a lift boost) |
| `m8c_horizon_soft_land` | Ref / Valk-Horizon | side exit → W air turn −12° → impact 1228 kept 410 → landing slide | +1.6 s: crouch after the landing, friction took the speed |
| `m8c_normal_hard_land` | Ref / Octane | same exit: impact 1228 → f0 0, 400 → 0, no slide | −2.37 s: low exit, impact 412, f0 1 |

Every demo runs through the existing integrity suites (3 seeds, failure case, bit-identical to its recorded inputs through `SkillBody.Step` at uneven frame rates, frame-rate independent, unchanged by visuals). DJ → slide on landing / wall-run / wall bounce / climb, lift → wall-run / mantle and lift eject → double jump are unit tests (§5), not demos.

## 5. Tests

| Suite | Result |
|---|---|
| EditMode | **1152 / 1152** (main 1038; +114) |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M8-C 16/16`; frame limit 120000 → 160000) |

New:
- `R5MotorM8CTests` (R5Replay): `PadDoubleJumpTests` 23 cases (with parameters) — loadouts / replay safety; grant at 60 / 120 / 144 Hz; early press not consumed, once per launch; held jump; normal jump and landing clear; vertical branches (direct and through the motor); horizontal rule (no key at 3 views, W / S / D / W+D, both launch speeds); same-command key (both options); lurch window restart (209.3) vs no DJ; five entries; M4 landing law; both double jumps (LOST, count kept, before-grant press); press-timing variants (same / early / late / hold / rapid at the launch, the grant and later, both configs); DJ → tap strafe; DJ → crouch-held landing slide (ducked pad, floor branch); DJ → wall-run (Fun); DJ → wall bounce and a bounce that leaves the grant; DJ → climb / mantle; zipline mount clears the grant. `LiftM8CTests` 17 cases — top hover 0.5 s, jump masked (both configs; Fun: the generic air jump after the eject); side exits at three heights radial and full; short-dwell fit; W at the top; air control reversal 0.55–0.7 s and the 92 sideways cap; no lurch window in Reference / M5 window in Fun; re-entry ≥ 2 s; Spacewalk vs normal landing (both configs); lift → air turn → landing slide (both configs); lift → wall-run (Fun); lift → mantle. `M8CFuzzTests` 6 runs (2 configs × 3 seeds, 40 s, pads re-deployed every 3 s, random keys).
- `M8CGameTests` 4: loadout coverage and the lift offset in every game body, the key-5 switch / best-time key / HUD / demo setup, the world pad grant (Octane yes, Revenant-Wraith no), demo coverage.
- 8 demos in every demo suite (64 cases) and 8 failure cases in `EveryDemoFailsWithItsFailureShift`.

Per-command checks (`M8C.Check`, course fuzz): a pad DJ only with its event, from a pending grant past 0.108 s, never on a launch command, committed by the arbitration as the press's only effect, ≤ one per grant, grants only on a pad launch, no grant survives a landing; lift eject ≤ 400 / 450; a Horizon body never gets `LAND_SLOW`; plus every M8-A / M8-B check (one effect per press, no double take, caps, stuck / tunnelling / frozen traversal, exit failures).

Course fuzz: 2 extra M8-C episodes per seed in both configs from their own generator (station D pad / lift spawns or a jittered M8-C demo); the older pools leave the M8-C demos out. Every row: 0 exit failures, 0 stuck, 0 frozen traversals, 0 tunnelling candidates.

| Config / loadout | pad grants / DJs (early, landing clears) | lift ejects (short-dwell) | Horizon hard landings kept | max v_h |
|---|---|---|---|---|
| Ref / Pathfinder-Octane | 32 / 31 (12, 1) | 13 (3) | – | 814 |
| Ref / Valk-Horizon | – | 207 (118) | 20 | 624 |
| Ref / Revenant-Wraith | – | 15 (6) | – | 676 |
| Ref / Ash route | – | 8 (1) | – | 600 |
| Fun / Pathfinder-Octane | 28 / 24 (5, 0) | 17 (7) | – | 833 |
| Fun / Valk-Horizon | – | 271 (166) | 37 | 810 |
| Fun / Revenant-Wraith | – | 8 (3) | – | 813 |
| Fun / Ash route | – | 9 (4) | – | 641 |
| Ref + M7 toggles / Octane, Valk-Horizon | 15 / 15 (5, 0); – | 0; 125 (78) | –; 6 | 813 / 619 |

Skill fuzz: 9–11 grants and 9–11 pad DJs per run, 7–8 early presses, 0 audit failures.

Existing tests changed (each keeps its intent):
- `DoubleJumpTests.APadLaunchIsNeverLoweredByAnAirJump` (M7) and `JumpArbitrationTests.PadBody` (M8-A): built with the pad DJ off — they test the generic air jump and the jets on a pad flight (rank 300 would take the press).
- `WorldEquivalenceTests.ScriptedRunsOfEveryConfigAndLoadoutAreBitIdentical`: the 30 s route runs with the pad DJ off. With it on, the route's presses after the pad launch double-jump the Octane body onto a course ramp, which the M5.5 box world never had (the comparison is about the box worlds).
- `MovementDemoTests`: 8 failure cases; the simulation-write scan includes `MovementDemosM8C.cs`; the reference run of `DemoTrajectoryEquals…` applies the demo's `padDoubleJump` setting.
- `M6CourseTests` fuzz: M8-C episodes and checks; the older demo pool excludes `m8c_`.
- `PracticeGameTests.ConfigAssetsEqualTheFactory`: also compares the pad DJ fields and the lift-eject lurch rule (assets regenerated with `PresetAssets.CreateM5ConfigsBatch`).
- PlayMode smoke test: `M8-C 16/16`, frame limit 160000.

## 6. Regression (default replay motor; outputs in a scratch folder outside the repositories)

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | **114 identical**, 0 different, 0 missing (incl. every `m4_pad_*` and `m4_lift_*`) |

No replay preset had to change: the pad DJ is not in the replay kit and the lift offset / lurch flag are neutral non-serialised fields.

## 7. Build and smoke

Build: `HSD-Build/M8C/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M8C\HSD-Practice.exe`), Build Succeeded. The re-serialised `ProjectSettings/ProjectSettings.asset` and `Scenes/Practice.unity` were reverted (`git checkout --`).

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 126/126 verdicts as expected (63 SUCCESS at shift 0, 63 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16); course lap 80.82 s (7/7
checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2115 bytes); 64784 commands in total
```

The 110 older demo lines are identical to the M8-B build's smoke output (diffed). The feedback byte count varies with the timestamp.

## 8. Open gaps

- Key pressed on the DJ command: R5's own result (D −264.1 / +272.1, S net 449.3) is unmodelled; Unity uses the held rule without the same-command lurch [design].
- Lurch clamp after a DJ: R5 212.55, Unity 209.3 (0.7 × sprint cap).
- Upgraded pad (`enable_doublejump_aircontrol`) and other frame rates of the grant thread are unmeasured.
- Map pads grant the DJ only to the Octane preset (R5: anyone) — a scope decision.
- Both double jumps on one body: allowed and tested, not decided for the final game.
- Lift: re-entry inside 2 s, the lift expiry eject (10 s lifetime) and the exact short-dwell offset per dwell are unmeasured; the Horizon wish component creeping from 92 to 93.7 before landing is not modelled.
- Reference Valk-Horizon trajectories after a lift eject differ from main by design (no lurch window); the 30 s scripted route (box-world equivalence) was not diffed against main for that loadout (its new-vs-legacy equivalence holds, the smoke route numbers are unchanged).
- Every [design] value is 「真人手感未验收」.

## 9. Design-value list (new in M8-C)

| Mechanic | Parameter | Value |
|---|---|---|
| Pad DJ | `grantDelay` | 0.108 s ([meas] band resolved as granted) |
| | `vzBranch` | 358.7 u/s (inside the measured bracket) |
| | `sameCommandKeyAsHeld` | true |
| | `UpCeiling` (bodies with the pad DJ) | 1250 u/s |
| | loadouts / switch | Octane preset, both configs; key 5 |
| | map pads | grant only to bodies with the ability |
| Lift | `liftEjectOpensLurchWindow` | Reference false [meas], Fun true [design] |
| | `ejectScaleOffset` | 0.0206 s [fit] (game), 0 (replay) |
| Generic DJ with the pad DJ | rank order | pad 300 > generic 200; the loser keeps its count |
