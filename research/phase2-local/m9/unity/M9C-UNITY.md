# M9-C in HSD-Unity: Vantage Echo relocation (C1–C3), the D1 remainder and the measured follow-ups

- Branch `m9c/vantage` of HSD-Unity (commit `307c6ed`), from main `76d4ee8` (M9-A merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M9-PLAN.md](../M9-PLAN.md) items C1–C3 and D1. Evidence (all R5, lead-verified): [../r_vantage/VANTAGE.md](../r_vantage/VANTAGE.md) + `params.json`, [../../m8/r2_vantage/VANTAGE-JETDRIVE.md](../../m8/r2_vantage/VANTAGE-JETDRIVE.md) + `params.json` (and the raw M8 R2 trajectories of `data/20261022_071639_M8R2_vantage`, read with the R2 loader to fit the drive), [../r_d1/D1.md](../r_d1/D1.md), [../r_rev/REVENANT.md](../r_rev/REVENANT.md), S21 script `mp_ability_companion_launch.nut` / `sh_vantage_companion.nut`, track D [../d_library/TECHNIQUE-LIBRARY.md](../d_library/TECHNIQUE-LIBRARY.md) §3.19. Playtest guide (Chinese): [../PLAYTEST-GUIDE-M9C.md](../PLAYTEST-GUIDE-M9C.md).
- **S21 only.** The S22 LOS removal ("slithering"), Echo dash, Echo tap strafe and the Echolevator are post-S21 and are not modelled (the LOS gate is a parameter, `checkLos`, so the S22 rule can be switched on later; nothing else of them exists).

> **Acceptance status (three separate labels)**
> - **「数值/规则测试通过」** (numbers and rules): Echo placement, the tap / hold rule, the 1.82 s pre-launch, the 60° and LOS gates, the jet drive against the R5 trajectories (400 / 800 / 1200 u, the Echo drive, moving targets, crouch, wall), the end double jump (window, velocity, arbitration), the superglide slide-boost state, the uphill slide, the Revenant follow-ups and the R5 lurch numbers are unit-tested; every R5 replay is identical; the M5 route, every older demo verdict and the course lap (80.82 s) are unchanged (§7–8).
> - **「真实按键演示通过」** (real-input demos): 7 M9-C demos, each with a failure variant, pass through the normal command loop (smoke `M9-C 14/14`, §8).
> - **「真人手感未验收」** (human feel): nobody has played it. The pre-launch length, the drive feel, the end-jump timing, the Echo prompt and every [design] value are open.

Labels: **[meas]** R5 measured, **[fit]** a formula fitted to R5 rows / trajectories, **[src]** S21 script constant, **[inf]** interpretation, **[design]** an HSD choice.

## 1. Vantage: measured / source vs implemented (Reference)

Module: `R5Replay/Runtime/Abilities/VantageEchoAbility.cs` (`VantageParams`, `VantageEchoAbility`, its `EndJumpClaimant`, `EchoTrack`, `IMantleBlocker`). Preset `SkillLoadouts.Vantage()` (6th, legend `vantage`, tactical on Q, 1 charge × 4 s [design]); `MovementConfig.vantage` in both configs.

### 1.1 Echo (C1) — a placed marker, no AI

| Rule | Evidence | Unity | Class |
|---|---|---|---|
| Tap → Echo to the first hit along the eye ray or the ray end | R5 pitch 0: 1968.5 u horizontal; 20° up: 1988 3-D / 1849 horizontal, 732.5 up (= 1967 along the ray from the eye); 10° down: where the aim meets the floor (326 u) | `OrderPoint`: eye + dir·min(hit, `echoRange` 1968.5); a hit is pulled back 20 u | range [meas]; backoff [design] |
| Range constant | script base 40 m (1574.8 u), max 55 m; buffed 50 / 65 m; the build uses the **buffed** base [inf] | `echoRange` parameter, Reference = measured 1968.5 (test: 1574.8 works as a parameter) | [meas] / [src] |
| Hover height | ~246 u above the floor (6 m min order height + bounds) | ≥ 246 above the support under the point (also above a platform top) | [meas] |
| Flight | R5 log: 1197 u/s, slows near the end (script: 1200 u/s, 8 m slow-down range) | 1200·min(1, d/315) u/s; Unity 1968.5 u in ~3 s | [src] + [fit] |
| Re-order | script: a tap orders Echo from where it is | from the current position | [src] |
| Recall | script `+scriptCommand5`; the runner's recall put Echo on the shoulder within one 0.3 s log tick | **E** (slot 2 button, cleared if a slot uses it) → perched at once | key [design], instant [meas] |
| After a drive | R2 log: Echo comes back to the player | perched at the drive end (no flight back) | [meas] / [design] |
| Idle drift, "follows at > 55 m", pathfinding | not measured within the 14 s logger | not modelled | gap |
| Echo cost | tap never spends ammo [src] | a tap works on cooldown (the slot never refuses the press) | [src] |

### 1.2 Hold → launch (C1 / C2)

| Rule | Evidence | Unity | Class |
|---|---|---|---|
| Hold vs tap | 0.3 s hold launched 3 / 5; 0.6 / 1.0 / 2.0 s 5 / 5 | held at press + 0.3 s → pre-launch; a release at or before 0.3 s is a tap | **[design on the edge]** |
| Fixed pre-launch | lift-off 1.808–1.826 s after the press whatever the hold (2.0 s hold: lift-off 0.19 s before the release) | lift-off at press + 1.82 (tests: 0.31 / 0.6 / 1.0 / 2.0 s holds → 1.817–1.825 at 120 Hz) | [meas] |
| Drive call before the lift-off | M8 R2: BeginJetDrive → leave ground 0.204 s (SDK `jetdrive_delay_time` 0.2) | gates checked and the target captured at lift-off − 0.204 | [meas] |
| Perched Echo + hold | R5: Echo ordered out (~1185 u at the call), lift-off 1.662 s after the press | Echo leaves 0.47 s after the press [fit], lift-off 1.662; Echo 1186 u out at the call; the drive then tracks the still-flying Echo | [meas] / [fit] |
| On-screen gate | script DOT_60DEGREE; R5 50° launched 4 / 4, 70° 0 / 5 | view · (Echo − eye) ≥ cos 60° (tests 50 / 59 launch, 61 / 70 refused) | [src] + [meas] |
| LOS gate | script trace eye → Echo + two retries (eye ± 0.5 m right + 0.5 m up); R5 a rock in the line 0 / 5 | same traces on the world; a thin post covering only the centre ray does not block (test) | [src] + [meas] |
| Distance gate | none: Echo 2405 u away launched 5 / 5 | `maxLaunchDistance` = ∞ | [meas] |
| Refusal cost | ammo only taken on a successful launch [src] | refusals (OFFSCREEN / LOS / NO_ECHO / NO_CHARGE) spend nothing; event `JETDRIVE_REFUSED_<why>` | [src] |
| Pre-launch side effects | script `DisableMantle` + `ClearTraverse` in the pre-launch and the drive | `IMantleBlocker`: no climb / mantle start in the pre-launch or the drive (test with a 90 u ledge and a control) | [src] |
| From a zipline | script `Zipline_Stop` at the drive start | the drive (the newer driver) pre-empts the ride (test) | [src] |
| From the air | — | works (test: lift-off while airborne) | [design] |

### 1.3 Jet drive (C2) — fitted on the raw M8 R2 trajectories

A kinematic drive (the world sweeps every move). Phases: **Boost** 0.2 s at 943.1 u/s; **Guide** — heading straight at the (moving) target, vertical speed by a ballistic aim a = 2(vz·t_go − Δz)/t_go² with t_go = horizontal distance / horizontal speed, 3-D speed eased 943.1 → 787 as (1 − t/T)², T = 0.001 s/u × start distance; **Brake** — from the first command within 180 u: speed from at most 787 down at 1047.6 u/s², gravity bending the path (v + g·dt renormalised), heading kept on the target while it is ahead (a fixed target is already straight ahead), passing through the target and on until the speed reaches 78.7 u/s, a landing, a wall, the timeout, a crouch or the end jump.

The R5 trajectories showed: the horizontal speed stays nearly constant while the vertical component falls linearly at exactly the ballistic aim (672 u/s² at 1200 u, 1182 at 800, both recomputed from the post-boost state = R5 within 1 %); the "easing to 787" is the 3-D speed; the brake is 1047.6 u/s² (|v| drops 52.4 per 0.05 s) and its normal acceleration is gravity's normal component.

| Quantity | R5 (M8 R2, n 5 each) | Unity | Class |
|---|---|---|---|
| Lift-off speed / hold | 943.1, held ~0.2 s | 943.1, 0.2 s | [meas] |
| Lift-off elevation 400 / 800 / 1200 / Echo | 27.71 / 24.74 / 23.72 / 26.67° | 28.27 / 24.65 / 23.43 / 26.1° (target elevation + 21°) | [fit] |
| Speed at 0.4 / 0.6 / 0.8 / 1.0 / 1.2 s (1200 u) | 897.0 / 859.2 / 829.9 / 808.4 / 794.8 | 895.4 / 856.4 / 826.1 / 804.4 / 791.4 | [fit] |
| Brake start / decel | ~180 u (SDK `jetdrive_decel_dist`), 1047.6 u/s² | 180 u, 1047.6 | [meas] |
| Closest approach 400 / 800 / 1200 / Echo 1976 | 84.5 (above) / 4.2 / 7.7 / 14.3 u | 56.8 (above) / 5.6 / 14.0 / 18.4 u | [fit] |
| Crossing the target 800 / 1200 | 1.025 / 1.525 s | ~1.03 / ~1.53 s | [fit] |
| Apex 400 / 800 / 1200 / Echo | 136 / 151 / 189 / 338 u | 115 / 142 / 180 / ~330 u | [fit] |
| Landing past the target 400 / 800 / 1200 / Echo | 129 / 66 / 49 / 80 u | 115 / 52 / 39 / 74 u | [fit] |
| Short drive (400) | misses 84 u above, ends at ~81 u/s and falls | misses 57 u above, ends at 78.7 u/s (`MIN_SPEED`) and falls | [meas] / [src] min speed |
| Moving target 300 u sideways in 1 s / receding 600 u in 1.5 s | passes 1.7 / 10.4 u from it | passes < 30 u from it (test); the yard's 200 u/s shuttle: 21 u | [meas] / [design] heading in the brake |
| Crouch | ×0.800, drive ends, then v_h constant 686.3, vz at g | ×0.8, ends, ballistic; 690.1 (test ±12) | [meas] |
| Into a wall | stops at the face (lowest |v| 123 at the face) | the drive ends at the face (`STUCK`, world-clipped velocity, ~16 u in front) | [meas] / end rule [design] |
| Timeout | script 2·d/787 rounded to 0.1 s | same | [src] |
| Steering law details (curvature, apex) | — | the apex is 10–20 u lower than R5 (the R5 arc rises a bit longer) | gap ("够像就行") |

### 1.4 End double jump (C2)

| Rule | Evidence | Unity | Class |
|---|---|---|---|
| Velocity | script <512, 0, 394> replacing the velocity; R5 vz 394.0 (post 390.87), horizontal 506.6 / 503.2 / 498.8 / 492.9 at 178 / 117 / 62 / 15 u, 483 / 469 past the target | vz 394 (post 390.875); horizontal **512·cos(θ/2)** along the travel, θ = the drive's elevation at the press: 506.9 / 503.7 / 499.1 / 493.0 | [src] + [fit] (12 + 9 presses) |
| Back jump | script back fraction 0.5 | input pointing back along the travel (wish · travel < −0.5): along the input × 0.5; no side part | [src], unmeasured |
| Window opening | M8 R2: presses 15–178 u from the target applied 12 / 12; M9: 250 / 310 u nothing | opens with the brake: the first drive command within `endJumpOpenDistance` 180 u | **[inf]** |
| M9 "0.84 s / 115 u" reading | M9: 0 / 7 at 0.833 s (121 u) vs 3 / 3 at 0.842 s (109–118 u) | not used as the edge: R2 applied at 178 u, and M9 itself refused presses deeper inside (1.083 s, 24 u past: 0 / 4 next to 1.099 s 1 / 1; 1.2152 s refused next to 1.2168 s 4 / 4), so those refusals look like a press-registration artefact of one-frame taps. The distance is a parameter (`endJumpOpenDistance`, test with 115) | [inf], lead decision |
| Late edge | R5 applied 59 u past the target (0.19 s after the crossing); 1.33 s (landed) nothing | open until the drive ends (landing / minimum speed / wall / timeout) | **[design]** |
| Lurch after it | n = 1: D press 3 commands later |Δv| 4.18 (air acceleration) | Reference: no lurch window; Fun: re-anchors it | [meas, weak] / Fun [design] |
| Ends the drive | the trajectory is ballistic after it | yes | [meas] |

### 1.5 Echo / drive state machine

```
Echo:   Perched ──tap / perched hold──▶ Flying (1200 u/s, slow inside 315) ──▶ Hovering ─┐
          ▲   ▲                              │ order on a track ──▶ Track (shuttle)      │
          │   └──── E recall (Idle only) ◀───┴───────────────────────────────────────────┘
          └──── drive ends (Echo returns)

Tactical: Idle ─press─▶ Pressed ─release ≤ 0.3 s─▶ Idle (+ ECHO_SEND)
                           └─held at 0.3 s─▶ [no charge → JETDRIVE_REFUSED_NO_CHARGE] PreLaunch (Pending)
          PreLaunch ─press+1.616 (gates)─▶ refused (OFFSCREEN | LOS | NO_ECHO | NO_CHARGE) → Idle, nothing spent
                                        └▶ WindUp ─press+1.82─▶ Boost (Driving, charge spent, pad grant cleared)
          Boost (0.2 s) ▶ Guide ─within 180 u─▶ Brake (end-jump window open)
          any drive phase ─▶ Idle on: END_JUMP | DUCK_CANCEL (×0.8) | LAND | STUCK | MIN_SPEED | TIMEOUT | INTERRUPT_<arbiter>
```

Arbiter row (`SkillLoadouts.VantageTraits`, only in the Vantage preset's rules, so every older trait table is unchanged): priority 55, interruptible, not exclusive, `handlesJump` (the arbiter does not mask the press during the drive), guards pending 2.5 s / driving 10 s. Vantage bodies get a 945 horizontal ceiling (`VantageParams.HorizontalCeiling`, above the 943.1 lift-off).

### 1.6 Arbitration rank and resources

- `JumpRank.JetDriveEndJump = 280`: below the pad double jump (300) and above jets-first (250) / the generic air jump (200) / jets (100). The drive clears an unused pad grant at the lift-off [src: `JumpPad_GiveDoubleJump` signal], so 280 vs 300 never meet; during the drive every other claimant is refused anyway (DRIVING / KINEMATIC), so the rank only orders a hypothetical tie.
- New `IDriverJumpClaimant` (its `Driver` is the Vantage ability): `JumpArbitration.RefusalReason(ctx, claimant)` ignores "a driver is running" only for the driver's own claimant. Resolve now evaluates the reason per claim; for every older claimant it is the M8-A reason unchanged (all M8-A / M8-C arbitration tests pass unchanged).
- Resources are separate: the end jump has its own claimant name (`jetdrive_end_jump`), no count; the generic air jump's count is untouched by it (test: Fun body, the generic air jump is refused during the drive and still there after the end jump); the pad double jump keeps its own grant (cleared by the drive start). E1 (both double jumps on one body) is not decided or changed.

### 1.7 Combos

| Combo | Unity | Class |
|---|---|---|
| End jump → lurch / tap strafe | Reference: no window (n = 1 R5); Fun: window | [meas weak] / [design] |
| Crouch cancel → landing slide | crouch held → the landing slides (> 200 u/s) (test) | [inf] |
| Drive → wall bounce / climb / mantle | no climb or mantle start during the pre-launch and the drive [src DisableMantle]; a wall ends the drive | [src] / [design] |
| Fun wall-run | never starts during the drive (driver rule; test) | [design] |
| Zipline | the lift-off ends a ride (test) [src]; a mount during a drive is the newer driver and ends the drive (arbiter) | [src] / [design] |
| Grapple / pad / launches | a launch interrupts the drive (interruptible); a grapple fired mid-drive takes over as the newer driver | [design] |

## 2. D1 remainder

| Item | R5 | Unity before | Unity now | Class |
|---|---|---|---|---|
| Superglide after a slide | sprint approach 299: slide 0.75 s before the jump 0 / 5 (mantle jump 299–329), 1.25 / 2.25 s 5 / 5 at 460.005; slide-jump approach 0 / 5 (M8 0 / 15) → the slide-boost state | any superglide crouch boosted (slide-jump approach superglided) | `ClimbParams.slideBoostRearm` 1.8 s (both configs; 0 in the plain climb): no 460 within 1.8 s of the last slide boost (motor `boostTime`) or superglide; the crouch then only gives the mantle jump (`SUPERGLIDE_NO_BOOST`). At the press the R5 boost was ~1.59 s (refused) vs ~2.09 s (granted) old with the H120 approach (jump → press ≈ 0.84 s): 1.8 is inside | rule [meas], value [design inside the bracket] |
| Pad DJ lurch clamp | 212.53 includes the command's air acceleration; without it 209.05 (control 209.30) | 209.3 | unchanged (pinned by a test) | [meas] |
| Uphill slide (~30°) | 460 → ~92 in 0.64 s; −322 u/s² beyond the flat law; −550 overall | M6-A4 term (duck held) | unchanged: 455 → 92.5 in 0.658 s, −323.8 u/s² extra, −551 overall (test). Fun slope (E2) untouched | [meas], one angle |
| Lurch [model] values (M9-A tests) | R-6 walk −162.4 / −157.3°, sprint −157.6 / −156.2°, slide jump −144.7 / −144.2° (×1.00 / 0.95–0.98 / 0.82–0.85); R-5 (ii) −162.0° ×0.980, (i) −124.7° ×0.634; R-1b −44.7°; no lurch right after a pad launch | [model] | R-6, R-5 (with the R5 one-command taps), R-1b now assert the R5 numbers; Unity agrees within 3° / 0.03 everywhere — **no model change**. R-1a / R-2 keep pinning the input-layer gap; R-4 (R5 run invalid) and R-10 stay [model] | [meas] |
| Pad launch → lurch | R5: **no** lurch window after a pad launch | Reference opens one (M5 launch rule) | **not changed — reported** (the M5.5 `pad_lurch` acceptance demo depends on it; pinned by `PadLaunchLurchWindowPinsTheReportedDisagreement`) | lead decision |

Notes found on the way (not changed): R5's slide jump 0.25 s into a slide left at 397 u/s (no refund), Unity's 0.4 s refund window gives 236 there (`slideBoostRefundWindow` 0.4, bracket 0.201–0.597 in M2): the R5 D1 data suggest a window < 0.25 s; it touches the replays, so it is only reported. Unity's slide does not end when crouch is released (R5's did: the gap schedules were back at 299 sprint), so the R5 gap schedules cannot be replayed literally; the gate is tested on the boost clock and with a real slide-jump approach. R-5: R5 landed in a slide at 195.5 u/s (5 / 5), Unity needs ≥ 200.

## 3. Revenant follow-ups (M9 r_rev vs M9-B)

| Item | R5 | M9-B | M9-C | Class |
|---|---|---|---|---|
| Side key while climbing (W held) | ≈ 161 u/s (148 u over the climb, vz ≈ 215 kept) | generic Gibraltar drift (eases to 102.6) | profile `climbSideMax` 161, `climbSideAccel` 3000 [design ramp]: 161 mean (test); other legends keep 102.6 | [meas] |
| S (W released) | the climb ends at once, ~70 u/s backward | generic back detach 0.060 s, 69.97 out | profile `backDetachDelay` 0: at once, 69.97 out | [meas] |
| Jump with W held | no launch, no bounce: vz follows gravity, re-attaches 0.89 s later | Reference: M3 bounce [inf] | `ClimbJumpKind.Release`: ends the climb, no impulse, a new climb allowed 0.89 s later (also falling faster than the 400 u/s design guard: R5 re-attached at ~446 u/s down); Fun keeps the Sparrow wall launch [design] | [meas] |
| Lurch after a pounce | none (|Δv| 4.17) | Reference: none | matches (test) | [meas] |
| Landing recovery | ordinary friction (564.4 → 245.5 after 0.25 s, ≈ 1276 u/s²) | soft landing + 1250 friction + 0.083 s move-scale hold | matches within 20 u/s (Unity 261 at 0.25 s) | [meas] |
| Pounce cancel | not found (zoom / attack / jump do nothing) | arbiter interrupt only | unchanged (no player cancel) | [meas] / [design] |
| Jump inside the climb lock | R5: no bounce (the no-pounce control was invalid) | M5 base-layer wall jump [design] | unchanged, reported (weak evidence) | gap |

## 4. Training area VE, preset, demos

- **Preset**: `SkillLoadouts.Vantage()` (6th, key **=** outside the demo panel, whose = is the shift), asset `Presets/Loadouts/Vantage.asset`; config assets regenerated (`PresetAssets.CreateM5LoadoutsBatch` / `CreateM5ConfigsBatch`; the older loadout assets came out byte-identical apart from line endings and were reverted).
- **Echo yard VE** (`PracticeMapM9C.cs`, appended after every older item: blocks 81–84, decals after the M9-A ones, no rope): south of station D's tower (x 7300…10000, y −950…−360). Checked free: no older block inside; running every older demo (both shifts) and the 30 s scripted route in every config × loadout, nothing passes through it (a first placement at x 3000–5000 was hit by `m8b_hop_chain` / `m8b_bhop` and the scripted route, so it moved).
  - VE1 lane (start 7400, −550): stripes every 250 u, tiles 500 / 1000 / 1500 / 1968.5 (a level tap), dots for the 60° cone at the start tile.
  - VE2 pillars 120 / 300 / 500 tall at 600 / 1200 / 1800 u (y −410): Echo above a top or 20 u in front of a face (wall-stop drill between pillars 2 and 3).
  - VE3 moving target: a floor strip at x 9900 (y −950…−600) → Echo rides an `EchoTrack` (200 u/s back and forth, 246 u up) [design training aid]; practice spot 1000 u west (8900, −775).
  - VE4 LOS wall (x 7800–7860, y −930…−750, 400 tall): tile A (clear line to the spot 8600, −850), tile B behind the wall.
- **Visual layer only**: an Echo ball, the eye → Echo line in the pre-launch (green: the gates pass for this aim, orange: refused), a ring on the drive target, the track line (`AbilityVisuals.UpdateEcho`); a prompt under the crosshair (`PracticeGame.EchoPrompt`: tap / hold / recall, "not within 60°" / "line blocked", the pre-launch countdown, "二段跳窗口：空格").
- **Demos** (Reference; failure variant = the panel's timing shift):

| Id | Success (shift 0) | Failure (shift) |
|---|---|---|
| `m9c_echo_launch` | tap → Echo at 1968.5; hold 0.6 s → lift-off 1.817 s after the press at 943.1, passes 18.4 u from Echo, lands 74 u past | −0.36: the hold ends at 0.24 s → a tap, Echo re-sent, no launch |
| `m9c_offscreen` | view turning 25°/s: Echo 40.7° off at the call → launches | +0.9: 63.0° at the call → `REFUSED_OFFSCREEN`, no charge |
| `m9c_line_of_sight` | from tile A (clear line) → launches | −2.7: strafed to tile B before the call → `REFUSED_LOS` |
| `m9c_moving_target` | the tap on the strip → Echo on the track; the drive passes 21.2 u from the moving Echo | −0.45: the tap lands short of the strip, Echo hovers in place |
| `m9c_end_jump` | Space 1.12 s after the lift-off (in the window, 109 u from Echo): v_h 506.8, vz 394, drive ends | −0.35: before the window (the brake) → nothing |
| `m9c_crouch_cancel` | crouch 0.41 s into the drive: ×0.800, drops out 867 u short | +3.0: after the drive ended → no cancel |
| `m9c_wall_stop` | Echo 20 u in front of the 500 pillar's face; the drive ends at the face (16 u, the hull) | +1.1: the tap while turned 25° right misses the pillar; the drive goes past it |

## 5. Design values (new in M9-C)

| Mechanic | Parameter | Reference | Fun |
|---|---|---|---|
| Tap / hold edge | `holdThreshold` | 0.3 s (≤ 0.3 = tap) | same |
| Perched-hold order delay | `perchedOrderDelay` | 0.47 s [fit n 5] | same |
| Wall backoff of an order | `echoWallBackoff` | 20 u | same |
| Eye height (aim and traces) | `eyeHeight` | 60 | same |
| Recall key | `recallMask` | E (slot 2) | same |
| End-jump window open / late edge | `endJumpOpenDistance` / — | 180 u [inf] / until the drive ends | same |
| End jump → lurch window | `endJumpOpensLurchWindow` | false [meas n 1] | true |
| Back-jump rule (direction) | — | input back along the travel → along the input × 0.5 | same |
| Lift-off elevation | `elevationBase` | +21° [fit] | same |
| Easing time | `easeTimePerUnit` | 0.001 s/u [fit] | same |
| Brake heading on a moving target | — | kept on the target while it is ahead | same |
| Wall stop rule | — | a fresh wall contact against the drive ends it | same |
| Echo after a drive | — | perched at once | same |
| Charges | slot | 1 × 4 s | same |
| Horizontal ceiling (Vantage bodies) | `HorizontalCeiling` | 945 | 945 |
| Arbiter row | `VantageTraits` | prio 55, guards 2.5 / 10 s | same |
| Superglide re-arm | `slideBoostRearm` | 1.8 s (inside 1.59–2.09) | same |
| Revenant side ramp | `climbSideAccel` | 3000 u/s² (max 161 [meas]) | same |
| Yard VE | lane, pillars, track 200 u/s, LOS wall | | |

## 6. Tests

| Suite | Result |
|---|---|
| EditMode | **1512 / 1512** (main 1398) |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M9-C 14/14`; frame limit 260000 → 320000) |

New:
- `R5MotorM9CTests.cs` (R5Replay): `VantageEchoM9CTests` (placement at three pitches, walls / platforms / the range parameter, flight / re-order / recall, the 1.82 s lift-off for four holds, taps, the perched hold, distance and on-screen gates incl. 59 / 61°, LOS with the retries and the S22 parameter, charges), `JetDriveM9CTests` (shape vs R5 at 400 / 800 / 1200 incl. the 1200 speed profile and the brake, the long Echo drive, two moving targets, crouch, wall stop, the end-jump window and velocity at six press times, the window-distance parameter, arbitration / lurch / back fraction, distinct from the generic and the pad double jump, combos (slide, mantle block, air lift-off, Fun wall-run), zipline, timeout and guards), `D1M9CTests` (slide-jump approach both configs + the old rule, the boost clock at five ages, config wiring, the pad DJ clamp, the uphill slide), `RevenantFollowUpM9CTests` (side drift, back key, release jump + re-attach, pounce lurch / landing).
- `M9CGameTests` (Game): preset and values in both configs, the yard appended and free, the lane / LOS drill geometry, demo coverage (M9-C last), the feedback station name.
- 7 demos in every demo suite and 7 failure cases in `EveryDemoFailsWithItsFailureShift`.

Existing tests changed (each kept to its intent; the reason in brackets):
- `R5MotorM9ATechniqueTests`: R-1b / R-5 / R-6 assert the R5 numbers (R-5 now uses the R5 one-command taps); a new pinned test for the pad-launch lurch disagreement [R5 m9/r_d1 arrived].
- `R5MotorM9BTests`: `BackOnTheSlideDetachesSooner` (Revenant: at once, was 0.060), `JumpOnTheClimbBouncesInReferenceAndLaunchesInFun` (Reference: the release jump), `ProfileKeys` (+4 profile fields) [R5 m9/r_rev].
- `M9BGameTests`: 6 presets; the Reference Revenant climb jump is `Release`; the M9-B demos come before the M9-A and M9-C demos.
- `R5MotorM5SkillTests`: the single-legend presets have 1 slot; the fuzz counts Vantage taps / refused holds as uses [a random fuzz rarely satisfies the 60° + LOS gates at the call].
- `PhaseBreachTests.AshRouteLoadoutIsValid`: 6 presets.
- `M8CGameTests`, `M9AGameTests`: the M9-C demos / blocks / decals come last (M9-A's "last block / decal" now asserts the M9-C start).
- `PracticeGameTests.ConfigAssetsEqualTheFactory`: also the Vantage set and the new climb fields.
- `MovementDemoTests`: 7 failure cases; the simulation-write scan includes `MovementDemosM9C.cs`.
- `M6CourseTests` fuzz: the older demo pool excludes `m9c_` (the fuzz episodes are unchanged).
- PlayMode smoke test: `M9-C 14/14`, frame limit 320000.

## 7. Regression (default replay motor; outputs in a scratch folder outside the repositories)

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 (`-motor both`) | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 (`-motor v2`; includes the wall / mantle trials) | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | **114 identical**, 0 different, 0 missing |

The superglide change lives in the game climb (`slideBoostRearm` 0 in `ClimbParams.R5Reference`, 1.8 only in the configs); the replay kit has no climb / Vantage, and no replay preset changed. No M2 / M3 replay changed.

## 8. Build and smoke

Build: `HSD-Build/M9C/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M9C\HSD-Practice.exe`), exit 0. The re-serialised `ProjectSettings/ProjectSettings.asset` and `Scenes/Practice.unity` were reverted; `git diff --stat --ignore-cr-at-eol main` equals the plain stat (39 files, +2570 / −69); no CR in the committed .cs blobs.

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 170/170 verdicts as expected (85 SUCCESS at shift 0, 85 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16,
M9-C 14/14); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2109 bytes); 92294 commands in total
```

Every older demo line is identical to the M9-A build's smoke output (diffed, 156 lines). No older demo changed.

## 9. Open gaps

- **End-jump window edges**: the opening is read as the brake start (180 u) against M9's 0 / 7 at 121 u (artefact reading [inf]); the late edge is [design]. A finer R5 sweep with held (not one-frame) presses would settle it; the distance is a parameter.
- **Drive shape**: Unity's arc is 10–20 u lower at the apex and lands 10–15 u nearer than R5; the 400 u miss is 57 u vs 84 u above. The SDK path algorithm (path points, `jetdrive_initial_vert_offset` 0.4) is not reproduced, only fitted.
- **Moving targets inside the braking zone**: R5's movers had stopped before the brake; Unity keeps the heading on the target while it is ahead [design].
- **Echo**: no AI, no idle drift, no "follow at > 55 m", no flight back after a drive, no ledge / corner placement logic (the script's ledge checks), no Echo collision; the order delay after a tap is 0 [design].
- **Hold edge**: R5 0.3 s launched 3 / 5; Unity's 0.3 s is a tap.
- **Back jump** and the jump direction with side / back input: [src] only, unmeasured (R5 view = travel).
- **Pad launch lurch window** (Reference opens one, R5 none): reported, not changed.
- **Slide-jump refund window** (R5 397 u/s at 0.25 s vs Unity 236) and **slide end on crouch release**: reported, not changed (replay-relevant).
- **Superglide re-arm**: one rule (time since the last slide boost / superglide, checked at the superglide); whether a ground slide right after a superglide also loses its boost is not modelled (the motor's slide boost is unchanged).
- **Revenant**: the climb-lock wall bounce (R5 none, control invalid) stays the M5 wall jump; the long-climb end rule stays [design] (M9-B).
- Every [design] value is 「真人手感未验收」.
