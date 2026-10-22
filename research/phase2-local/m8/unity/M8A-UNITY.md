# M8-A in HSD-Unity: jump / skill input arbitration, slope slide, zipline interactions

- Branch `m8a/foundation` of HSD-Unity (commit `524610d`), from main `3fba896` (M7-A merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M8-PLAN.md](../M8-PLAN.md) items 1–3. Playtest guide (Chinese): [../PLAYTEST-GUIDE-M8A.md](../PLAYTEST-GUIDE-M8A.md).

> **Acceptance status (two separate labels)**
> - **「数值通过」**: every rule, guard and cap below is checked by automated tests, random fuzz and the headless smoke. Every R5 replay is byte-identical; every older demo verdict and the course lap (80.82 s) are unchanged (§6–§7).
> - **「真人手感未验收」**: nobody has played it yet. The slope-slide feel (gain, grade spread, cap), the dropped press on a refused claim, the wall-run start rule and the zipline end / air-mount changes are design values until the user has played them.

Labels: **[meas] / [fit] / [src]** as in M6; **[design]** an HSD choice (a tunable parameter, not Apex data).

## 1. Audit (before the build)

| Area | What existed (M6-A / M7-A) | Gap | Decision |
|---|---|---|---|
| Jump press | Every user acted on the press at once, in ability order: climb (bounce, hang exits, superglide press), zipline (jump-off, super-jump window), wall-run jump, wall bounce, double jump, jets; the arbiter masked an airborne press while a non-traversal driver ran. | A resource user (air jump, jets) spent its resource **before** the command's launches were known: a pad / pounce launch on the same command replaced the velocity of an air jump that was already spent (M7-A open gap); the jets paid the activation cost and were then ended by the launch. A driver starting later in the order (grapple pull) could start beside an air jump. On a wall-run start command, a press became a wall bounce while the run started (and refilled the air jump). | A per-command **claim → commit** layer (`JumpArbitration`, §2). |
| Slope | M6-A4 `slopeMovement` (flat ground velocity, position along the plane, StayOnGround); a slide adds g·n.z·n_h (scale 1). On in the game Reference (no effect on flat ground). M6-C: "the slope slide gains almost nothing". | No grade-dependent design, no guard against banking speed, no test area. | **HSD slope slide** (`SlopeSlideParams`, §3) on top of the M6-A4 option: off in Reference, on in Fun, key 6. |
| Zipline | M6-A3 mount / ride / exits / super jump / grapple handoff / budget; Reference refuses air mounts. | Never tested systematically against quick re-mounts, ends, odd angles, the M7-A mechanics. | Audit by tests (§4); two real defects fixed. |

Replay safety: the arbitration exists only on game bodies (`SkillSlotSystem.Build`); the replay's ability set has `jump == null` and runs the M4 code paths unchanged. The slope slide is a `[NonSerialized]` motor field, null in every replay preset and absent from every report.

## 2. Jump / skill input arbitration (`Skills/JumpArbitration.cs`)

### 2.1 Protocol (per command)

1. `Begin`: the press edge is recorded.
2. **Mask**: while a non-traversal driver runs (grapple pull, jets thrust, gravity lift, flight, phase travel) an airborne press is masked (`JUMP_BLOCKED_DRIVING`, M5 rule).
3. **State-owner tier** (in ability order, immediate): a traversal that owns the body takes the press and acts at once (`ConsumeJump(this)`, recorded as `takenBy`). A taken press is gone for everyone after it.
4. **Ground**: a grounded press is the motor's ground jump. A launch on the same command replaces it (the ground jump spends nothing).
5. **Deferred tier** (airborne resource users): they only **claim** (`Claim(ctx, this, rank)`); nothing is applied or spent. `Resolve` runs after every BeforeMove and the launch choice, before the move:
   - refused (all claims) when: a launch replaced the velocity (`LAUNCH`), a traversal moved the body kinematically (`KINEMATIC`), the controls are locked (`LOCKED`), the body is grounded (`GROUNDED`), a state owner is active (`OWNER`, `IJumpOwner`), or any driver runs (`DRIVING`);
   - otherwise the highest rank commits (`CommitJump`: the effect applies, the resource is spent) and the others are refused as `LOST`.
   - Event `JUMP_REFUSED_<claimant>_<reason>` (not for `LOST`). Nothing was spent, so no refusal needs a refund.
6. Audit record `JumpPressRecord` per command (press, masked, takenBy, committed, refused); `Effects ≤ 1` and `doubleTakes = 0` are asserted every command by the tests and the course fuzz.

### 2.2 Priority table

| Order | User | Tier | Takes the press when |
|---|---|---|---|
| 0 | Arbiter mask | mask | airborne, a non-traversal driver runs (grapple pull, jets, lift, flight, breach) |
| 1 | Climb / attached slide / mantle / **hang** | owner | its phase is active: bounce, superglide press, hang climb-up / jump-off |
| 2 | Zipline | owner | riding (jump-off), or within 0.2 s of a ground mount after a jump-off (super jump) |
| 3 | Wall-run | owner | running (wall-run jump). **New:** a run never starts on a command whose press is still unused (§2.4) |
| 4 | Wall bounce (M3) | owner | airborne, wall contact within 0.1 s |
| 5 | Ground jump (motor) | ground | grounded |
| 6 | [M8-C] Octane pad double jump | deferred, rank 300 | extension point only (§2.3) |
| 7 | Jets, rule **JetsFirst** | deferred, rank 250 | `CanEngage` |
| 8 | **Generic air jump** (M7-A) | deferred, rank 200 | air jump left, ≥ 0.1 s after the takeoff, not a hold hand-over |
| 9 | Jets, rule **AirJumpFirst** / no double jump | deferred, rank 100 | `CanEngage` and no higher claim |
| – | AirJumpFirst hold → jets | synthetic press | the air jump's press held 0.25 s: `Synthesize`, then the jets claim (counted `AIR_JUMP_HOLD_JETS` only if they really engage) |

Launches (pad, pounce, lift eject, portal exit, super jump) are not press effects; a launch refuses every deferred claim of its command. Flight (fun) ascends on a **held** jump while Driving, so presses are masked.

### 2.3 Extension point for M8-C (Octane pad double jump)

- A second air-jump source is a separate `IJumpClaimant` with its own eligibility, count and reset; it claims at `JumpRank.PadDoubleJump` (300, above the generic air jump). One press spends only the winner; the generic air jump is `LOST` and keeps its count. Its measured model is **not** built (track R is measuring it).
- Proven by `ASecondAirJumpSourceIsResolvedByRankAndSpendsOnlyTheWinner` (a test stub): winner spends, loser keeps; a launch refuses both.

### 2.4 Behaviour changes (all on game bodies only)

- Pad / pounce launch + air jump on one command: refused, **not spent** (was: spent and overwritten).
- Pad launch + jets press on one command: refused, **no activation cost** (was: cost paid, jets ended by the launch).
- A hold hand-over to the jets on a launch command: refused, no cost.
- A driver that starts later in the ability order on the press command (grapple pull): the air jump is refused (`DRIVING`); M7-A allowed it (the course-fuzz exemption is removed, except when the pull also ended on that command).
- A press on the exact command a wall-run would start: the run waits a command, so the press is the measured wall bounce (fresh contact) or the air jump — never run start + bounce, never an air-jump refill from a run that did not happen.
- Not changed: one command **early** (the air jump applies on its own command and is spent; the launch then replaces it — the effect did apply) and one command late (an ordinary air jump in the flight, the pad's rise kept by vz = max(vz, 260)).

## 3. HSD slope slide (`SlopeSlideParams`, `R5MotorV2.SlopeSlideStep`)

Read only with the M6-A4 slope option on (velocity flat, position along the plane). On a walkable slope (n normalised, |n_h| = sin θ, n_h downhill), per slide command:

1. Gravity along the plane, horizontal part: v_h += g·gravityScale·n.z·n_h·dt.
2. **Energy ledger**: a speed gain is limited to the ledger, which is credited 2·g·(height descended since the last slide command, world corrections included), capped at 2·g·energyBuffer, and **cleared whenever the body is not sliding on the ground** (air, jump, launch, traversal). So |v_h|² gained ≤ 2·g·Δh, and toggling the ground state never banks speed. The slope term also never raises |v_h| above max(|v_h|, maxSpeed).
3. Slide friction (decel 100 + decay 0.7^t, SLIDE-MODEL) on the result, × (1 − (1 − downhillFriction)·k), k = clamp01((n_h·d̂)/sin(fullFrictionGrade)): reduced heading downhill, full across the slope and uphill.

Walking / sprinting on slopes is unchanged (flat velocity, the flat caps; tested at 10°, 30°, 44° up and down). Uphill slides use physical gravity + full friction (identical to the M6-A4 term). Flat↔slope, grade changes, landings: speed continuous (the acceleration changes, the speed does not jump).

| Parameter [design] | Value |
|---|---|
| enabled | Reference off, Fun on, key 6 |
| gravityScale | 1.0 (physical) |
| downhillFriction | 0.25 at full downhill grade |
| fullFrictionGrade | 15° |
| maxSpeed | 760 u/s (900 ceiling on top) |
| energyBuffer | 24 u of height |

Resulting speeds on the V hills (height 160; slide from 299 + boost, crest speed 436):

| Grade | Reference (M6-A4 term) foot speed | Fun foot speed | Energy bound | Uphill (both): slide ends |
|---|---|---|---|---|
| 10° | 196 | 432 | 656 | 198 u up the ramp |
| 20° | 418 | 572 | 656 | 129 u |
| 30° | 466 | 561 (shorter ramp) | 656 | 88 u |

Map **V / W** (`PracticeMapM8.cs`, ramps only, appended after the five course ramps; no block or rope added; placed off the path of the scripted smoke / equivalence routes):
- V grade hills, x 500–2600: 10° (y 620–860), 20° (y 920–1160), 30° (y 1220–1460); each up ramp → 200 u top at 160 → down ramp.
- W grade-change chain, x 1800–3265, y 1120–1360: 20° walk-up to a top at 240, then 8° → 25° → 15° (drops 40 / 80 / 40), ending at a slope edge 80 u above the floor.

## 4. Zipline audit

| Case | Result |
|---|---|
| Air mount | Reference refuses (`ZIP_REFUSED_AIR`); Fun mounts with the momentum along the rope as the entry speed. |
| Active jump-off | ĥ·min(v, 400) + 289.8 ẑ, lurch window opened; a direction tap lurches at once (control recovery). |
| Quick re-mount | Next command after the jump-off works (Fun); 3 mounts per airborne phase, +1 per 3 s off the rope, reset on landing (tested). |
| Consecutive jumps | jump-off → super jump (within 0.2 s) → air jump → nothing: one effect each. |
| Rapid use presses | ignored while riding; the ride reaches 600. |
| Grapple → ride → detach | handoff, ride, jump-off min(v, 400), no super jump after a grapple-mounted ride, tap strafe right after. |
| High-speed mount | 850 u/s air mount → the rope cap 600 from the first ride command. |
| From behind | rides with the momentum (−x while looking +x). Open gap: the blend pulls toward the grip point ahead first (§8). |
| Steep (60°) rope | rides to the end zone; jump-off horizontal ≤ 400. |
| Transitions | slide → mount ends the slide; crouch-off with crouch held lands in a slide; jump-off → air jump → lurch; wall-run → mount (ends the run); jump-off + tap → wall-run on another wall (the same wall stays blocked until landing, M7-A rule). |

**Defects fixed** (both [design]):
1. **Mount inside the end zone** (grip point within `stopShort` 90 u of the end it would ride to, sloped / flat rope): the auto-detach fired on the next command with 600 u/s from any speed, even from rest — a free launch, also in Reference from the ground. Now refused (`ZIP_REFUSED_END`), also for the grapple handoff; `refuseMountAtEnd` (true) switches it back. Vertical ropes are unaffected.
2. **Air-mount lift**: the measured +22 u lift (ground mounts) also applied to Fun air mounts, so jump-off / re-mount cycles stacked ~20 u per mount. `airMountLift` = 0: an air mount does not move the body (like the grapple handoff). Ground mounts keep 22 [meas].

## 5. Demos (real input through Advance → Step; Fun config)

| Id | Success | Failure (shift) |
|---|---|---|
| `m8_pad_airjump` | hop onto the world pad, Space on the launch command: refused (LAUNCH), kept; Space 0.45 s later = air jump (vz 756 kept) | −2 commands: the air jump applied and was spent, then replaced; none left for the flight |
| `m8_slope_downhill` | 20° hill: 368 → 526 u/s over 155 u of descent (bound 607) | no crouch: walking down gains nothing |
| `m8_slope_uphill` | uphill loss 1.92 u/s per u (2.7× the flat 0.72), the slide ends 58 u up the ramp | crouch −1.2 s: the slide ends on the flat |
| `m8_slope_chain` | 8° → 25° → 15°: 434 → 506 u/s, ≤ 2.1 u/s per command; off the edge into a landing slide at 506 | crouch released over the landing: no slide |
| `m8_zip_remount` | ride → jump-off 400 → air re-mount 0.15 s later → riding at 400 | use −0.2 s: pressed during the ride (ignored) |
| `m8_wallrun_zipline` | course perch face: wall-run → use 0.13 s into it → yard-rope ride 346 u/s | use −1.2 s: on the ground, rope out of reach |

Zipline → double jump: `m7_djump_zipline` (unchanged). Every M8 demo runs through the existing integrity suites (recorded inputs, frame rates, visuals, seeds, failure shift).

## 6. Tests

| Suite | Result |
|---|---|
| EditMode | **848 / 848** (main 742) |
| PlayMode | 1 / 1 (smoke in the game loop, now also requiring `M8-A 12/12`) |

New: `R5MotorM8Tests` (`JumpArbitrationTests` 15, `SlopeSlideTests` 15, `ZiplineM8Tests` 11, `M8FuzzTests` 13), `M8GameTests` 5, the 6 demos in every demo suite.
- Conflict pairs, each with the press on the conflict command, one early, one late, held through, and rapid presses, audited every command (`M8.Check`: ≤ 1 effect per press, no taken press reused, no air jump / jets activation on a launch command, counters only move with their events, jets meter only drains, M5 invariants incl. caps): pad × air jump, pad × jets (AirJumpFirst, JetsFirst, Reference jets-only), pounce × air jump, jets × air jump (both rules, incl. hold), hold hand-over × launch, super jump × air jump, wall bounce × air jump, wall-run jump × air jump, hang × air jump, grapple pull × jump; plus the M8-C stub.
- Slope: Reference / replay unchanged; downhill gain by grade vs Reference vs flat; uphill loss; energy bound at 10–40°; hopping down a long 25° slope banks nothing; a ±15° sawtooth of net zero height never ends faster; continuity over 8° → 25° → 15°; fast landings up / downhill keep the speed and resume the slide; slide jump on a slope; walking / sprinting sane; slope edge → landing slide; cap and 60 / 144 / 240 Hz.
- Course fuzz: Fun gets 2 more episodes per seed (own generator) at the slope field or with a jittered M8 demo; the older pools leave the M8 demos out, so the older streams are unchanged. New checks every command: the arbitration audit, the slope ledger (excess 0), the air-jump check without the M7-A launch exemption.

Course fuzz (25 s episodes + 10 idle s, 12 seeds; every row: 0 exit failures, 0 traversal timeouts, 0 tunnelling candidates, 0 frozen traversals, 0 unresolved collisions, ledger excess 0):

| Config / loadout | episodes (M7 + M8 extra) | air jumps | slope-slide commands (max v_h) | jump claims refused | rope-end refusals | max v_h |
|---|---|---|---|---|---|---|
| Reference / Pathfinder-Octane | 60 | 0 | 63 (439, M6-A4 term) | – | 2 | 813 |
| Reference / Valk-Horizon | 60 | 0 | 0 | DRIVING 1 | 0 | 629 |
| Reference / Revenant-Wraith | 60 | 0 | 32 (201) | – | 1 | 676 |
| Reference / Ash route | 60 | 0 | 0 | DRIVING 1 | 5 | 641 |
| Fun / Pathfinder-Octane | 108 (24 + 24) | 1477 | 403 (610) | DRIVING 14, KINEMATIC 17, LAUNCH 1 | 7 | 833 |
| Fun / Valk-Horizon | 108 (24 + 24) | 900 | 536 (532) | DRIVING 17, KINEMATIC 9 | 5 | 810 |
| Fun / Revenant-Wraith | 108 (24 + 24) | 1461 | 840 (545) | DRIVING 11, KINEMATIC 6, LAUNCH 21 | 4 | 813 |
| Fun / Ash route | 108 (24 + 24) | 997 | 1049 (532) | DRIVING 30, KINEMATIC 6, LAUNCH 2 | 2 | 641 |
| Reference + M7 toggles / Pathfinder-Octane | 72 (36 M7) | 1382 | 0 | DRIVING 1, KINEMATIC 1 | 1 | 813 |
| Reference + M7 toggles / Valk-Horizon | 72 (36 M7) | 1118 | 0 | – | 0 | 626 |

The LAUNCH refusals in Revenant-Wraith are pounce launches on a press command: before M8-A each of them spent an air jump that did nothing.

Skill fuzz (`M8FuzzTests`, 4 presets × 3 seeds, 40 s, a test world with ramps around the start and two ropes): 0 audit failures; the slope term acted (gain² > 0, always ≤ the ledger credit).

Existing tests changed (each keeps its intent):
- `M6CourseTests.CourseLiesInTheSouthStrip…`: the ramp check covers the course ramps (before `m8RampStart`).
- `M6CourseTests` fuzz: M8 episodes and checks (above); the earlier demo pool excludes `m8_` (stream unchanged).
- `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: 6 cases; the simulation-write scan includes `MovementDemosM8.cs`.
- `PracticeGameTests.ConfigAssetsEqualTheFactory`: also compares `hsd.slopeSlide` and the zipline params (assets regenerated); `ReferenceTurnsOn…`: the slope slide is off in Reference.
- PlayMode smoke test: also requires `M8-A 12/12`; frame limit 30000 → 60000.

## 7. Regression, build, smoke

Replays (default motor; outputs in a scratch folder outside the repositories):

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | 114 identical, 0 different, 0 missing |

Build: `HSD-Build/M8A/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M8A\HSD-Practice.exe`), Build Finished: Success. The re-serialised `ProjectSettings/ProjectSettings.asset` was reverted (`git checkout --`).

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 82/82 verdicts as expected (41 SUCCESS at shift 0, 41 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12); course lap 80.82 s (7/7 checkpoints, Reference
(R5 calibration)); feedback snapshot ok (26 fields, 2113 bytes); 45342 commands in total
```

- The route part is unchanged (1441 commands, (341.586, 146.165, 10), 92.0, 18 events); every older demo verdict and reason is identical to main (all 70 lines diffed by a headless run of main and of the branch); the course lap is 80.817 s in every config × loadout (Fun with the slope slide included: the autopilot lap does not slide on ramps).
- The feedback byte count varies with the timestamp and now carries the slope-slide state in the Fun `m7a` field (field count unchanged).
- PlayMode smoke test: its frame limit was raised from 30000 to 60000 (the 82 demos plus the lap did not fit in 30000 headless frames).

## 8. Open gaps

- Every HSD value is [design]; nobody has played it (「真人手感未验收」).
- Arbitration: a press refused on its command is dropped (no input buffer), e.g. on the exact wall-run start command when there is no fresh contact for a bounce, or on a launch command. One command early, an air jump still applies and is spent before a launch replaces it (no refund by design).
- The Octane pad double jump itself is not built (M8-C; rank and protocol ready).
- Slope: no slope effect on walking speed (Apex-like flat velocity); no slope launch (`sv_slope_launch`); ramps with diagonal slope directions are not on the map; the ledger credits up to 2 u of landing settle.
- Zipline: an air mount whose momentum opposes the view blends toward the grip point ahead for ~0.2 s while the velocity already points back (visual oddity); a high-speed air mount drops to the 600 rope cap at once (rope rule); a mount and a pad launch on one command would spend a mount and refill the air jump (read from the code, not tested).
- The Reference course-fuzz rows were not re-run on main for a side-by-side diff. They can differ from main: the slope field is reachable by long aim rays and random play, and the arbitration refuses a few same-command claims (DRIVING 1 per row above). Every invariant holds.

## 9. Design-value list

| Mechanic | Parameter | Value |
|---|---|---|
| Arbitration | ranks | pad double jump 300 [reserved], jets (JetsFirst) 250, air jump 200, jets (AirJumpFirst) 100 |
| | refusal reasons | LAUNCH, KINEMATIC, LOCKED, GROUNDED, OWNER, DRIVING, LOST |
| | wall-run start | not on a command with an unused jump press |
| Slope slide | gravityScale / downhillFriction / fullFrictionGrade | 1.0 / 0.25 / 15° |
| | maxSpeed / energyBuffer | 760 u/s / 24 u |
| | configs | Reference off, Fun on, key 6 |
| Zipline | refuseMountAtEnd / airMountLift | true / 0 (ground mount lift 22 [meas]) |
| Map | V hills / W chain | height 160, top 200, 10° / 20° / 30°; top 240, 8° / 25° / 15°, edge 80 |
