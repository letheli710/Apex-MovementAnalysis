# M10-A (track U): Pathfinder advanced grapple in HSD-Unity

HSD-Unity branch `m10a/grapple`, commit `a394815` (from main `2f5f5c1`; 37 files, +1719 / −32, ignore-cr stat equal, no CR in the committed .cs), Unity 6000.6.5f1. Inputs: `m10/M10-PLAN.md` (M10-A), track R
`m10/r_grapple/GRAPPLE-M10.md` + `params.json` (R5 S21 client + S3 dedi, 120 fps), track D `m10/d_library/TECHNIQUE-LIBRARY-M10.md` §3.21–3.33,
lead decision of 2026-10-22 on client/dedi splits.

Result classes (M10 rule):
- **Numbers / rules tests: pass.** EditMode 1623 / 1623, PlayMode 1 / 1 (§6); the open-loop comparison against all 72 R5 grapple schedules is in §3.
- **Real-input demos: pass.** 7 new `m10a_*` demos, each with a failure variant; smoke 184/184 (M10-A 14/14).
- **Human feel: not accepted** (needs the user's playtest; guide `m10/PLAYTEST-GUIDE-M10A.md`).

Labels: **[meas]** R5 track R measurement, **[src]** Pathfinder class var / S21 script of the local build, **[fit]** chosen by the open-loop
comparison in §3, **[inf]** interpretation, **[model]** what the HSD model produces where R5 did not measure, **[design]** HSD choice,
**[S21-client; local dedi differs]** lead rule (Reference follows the S21 client where it and the S3 dedi disagree and community evidence supports it).

## 1. What changed (summary)

| Item | Before (M4b RF, still the M4 replay) | Now (game configs, `GrappleParams.Measured()` + `GrappleS21Params`) | Label |
|---|---|---|---|
| Along-rope speed | +541 u/s² forever | follows the ramp S = min(800, 50 + 500 t) (speedRampMin/Max/Time); catch-up at 1500 u/s² (grapple_accel) while below S; kept when above S | [src+meas] |
| Rope target | hit + 31.9 u, from origin | the hook point itself, from origin (sl_hold: velocity points at the hook within 4 u) | [meas] |
| Cross-rope brake | 423 u/s² always | 425 (grapple_decel), only while the along-rope speed is at the ramp or a key is held | [src] + [fit] |
| Gravity | off; 0.68 g on the cross part | ×0.25 (gravityFracMin; 187.5 u/s² seen to 0.1 u/s²), ×1 with the rope within acos 0.8 = 36.9° of straight down | [src+meas] |
| Downward pull | yes | never (grapple_dontFightGravity): on a rope that points down the pull is horizontal only | [src+meas] |
| Keys during the pull | v·ŵ += 500·msc·dt to 483 (W only measured) | every key: +650 u/s² (grapple_airAccel, not ·msc) along ŵ up to 420·msc = 483, clamped above; the motor's own air accel is off while pulled | [src+meas] |
| Detach | 34.1 u from the hooked plane; contact; landing | (a) hook ≤ 45 u from the body segment [origin, origin+72], from the attach on; (b) passing: moving away from the hook and hook > 85° off the view; (e) look-away: hook > 100° off the view [S21-client; local dedi differs]; (c) crouch press; (d) 2nd tactical: |v| kept ≤ 460, above → max(460, |v| − 300); low speed < 250 for 1.5 s (wall 1.2, floor 0.7); no contact release; no landing release (the body glides along the floor, R5 ground flag 0) | [meas]/[src] |
| Attach jump | none | a jump press after a ground attach and before the pull starts (0.2005 s wind-up) adds sqrt(2·g·56) − ½·g·dt (post vz +280.5 [meas]); owns the press (no air jump / jets on it); re-anchors the lurch window [inf] | [meas] |
| Max rope | 850 | 850 (unchanged) | [src] |
| Cooldown | slot 8 s × 2 (practice) | new preset **Pathfinder S21** (key `\`): 1 charge, script cooldown = min(300, 100 + int(300·clamp((d − 300)/4200)))/10 s, d = 2-D path from the attach while active or \|v\| > 500, ≤ 5 s, zipline mount stops it (10–30 s). Older presets keep their fixed cooldowns. | [src] |
| Speed ceiling | 900 | 1100 on bodies with the S21 grapple (jump grapple exits 1000–1035 [meas]) | [design] |

Ground-fire "speed kill": **no rule added.** The per-command data shows the sprint run-up (297 → 0 before the attach) decaying at exactly the
1250 u/s² no-input ground deceleration: the R5 schedule releases W + sprint on the fire command (`tap offhand1; up forward; up speed`). The slide
case (421 → 362) is the slide friction. Unity already does both. Demo `m10a_ground_fire` shows it; holding W through the hook flight keeps the
run-up in HSD [model; R5 not measured].

## 2. How the pull law was read from the data

Per-command R5 trajectories of the 72 `m10_g_*` schedules (track R sessions, read-only via `m10_load.py`) were dumped and decomposed into
along-rope / cross-rope accelerations (scratch scripts `dump.py`, `acc.py`). Findings that fixed the law:
- **Ramp.** No-input pulls (d250/d400/d700, g200/g400/g700, sl_hold, sl8_hold) keep v_r = S(t) within one command (S − 4.8 on the pre-state =
  one 120 Hz command of ramp). The release presses rel_t09/t12 (226 / 376 u/s at 0.35 / 0.65 s of pull) are the ramp values.
- **Catch-up 1500.** First pull commands: 1446–1559 u/s² along the rope (d700, g400, g700_jK).
- **Air entry kept.** The air trial enters at 297 u/s; |v| stays ~297 (−25 u/s², the 0.25 g along a rope tilted 14° up) until the ramp passes it
  at 0.5 s, then follows the ramp.
- **No downward pull, 0.25 g.** g400_j2 / g700_j6 (jump grapple): during the rise the acceleration is (1350–1450, 0, −187.5): horizontal only,
  vertical = −0.25·750 exactly. When the rope passes 36.9° from straight down the vertical becomes −750 (letGravityHelpCosAngle 0.8).
- **Brake gating [fit].** Four variants of the 425 brake were run open loop over every schedule (always / at the ramp only / at the ramp or with a
  key / sideways only). "Always" undershoots the jump grapple by 11 %; "at the ramp only" overshoots the side keys by 7 %; "sideways only" sags
  the 49° pulls by 12 %; **"at the ramp or with a key" keeps every no-input pull within 1 %, the side keys at −1 %, the jump grapple at +2 %**.
  It is a fit of an unknown native branch, not a class var.

## 3. Open-loop comparison with R5 (same start state, same per-command inputs, the measured hook point)

Means over the scored repeats; `max / v_h at release / pull s`. The rock face is a stop for the wall trials (the sim clamps x at the largest x
R5 reached). Rows that compare different things are marked.

| Schedule | HSD | R5 | HSD release | R5 end | Δ max |
|---|---|---|---|---|---|
| d250 | 479 / 453 / 0.87 | 474 / 439 / 0.85 | NEAR | auto | +1.1 % |
| d400 | 613 / 590 / 1.14 | 612 / 575 / 1.12 | NEAR | auto | +0.3 % |
| d700 | 800 / 777 / 1.56 | 804 / 763 / 1.55 | NEAR | auto | −0.6 % |
| p20 | 636 / 574 / 1.18 | 635 / 566 / 1.18 | NEAR | auto | +0.2 % |
| p0 | 608 / 605 / 1.12 | 729 / 728 / 1.07 | NEAR | auto | **−16.6 %** (open, §8) |
| sprint (entry) | 713 / 690 / 1.33 | 709 / 670 / 1.32 | NEAR | auto | +0.5 % |
| air (entry 297) | 516 / 481 / 0.94 | 513 / 467 / 0.93 | NEAR | auto | +0.5 % |
| hold_w | 519 / **483.0** / 0.76 | 520 / **483.0** / 0.75 | NEAR | auto | −0.1 % |
| hold_s | 720 / 703 / 1.36 | 739 / 692 / 1.38 | NEAR | auto | −2.6 % |
| hold_d (wall contact in R5) | 695 / 490 / 1.39 | 784 / 392 / 1.45 | NEAR | auto | −11.3 % |
| rel_t09 / t12 / t16 / t18 (2nd press) | 223 / 373 / 574 / 671 | 225 / 376 / 580 / 675 | MANUAL | key | −1 % |
| crouch | 200 / 195 / 0.31 | 203 / 201 / 0.31 | CROUCH | key | −1.4 % |
| look180 | 331 / 323 / **0.57** | 331 / 323 / **0.58** | LOOK_AWAY | auto (client) | +0.2 % |
| g200 / g400 / g700 (drag) | 408 / 603 / 798 | 400 / 599 / 797 | NEAR | auto | +0.2 … +2 % |
| g700_j1 / j6 / j12 / j18 | 1032 / 1049 / 1025 / 1046 (v_h at release 1030 / 1047 / 1024 / 1044) | 1012 / 1029 / 1006 / 1026 | PASSED | auto (passed) | **+1.9 %** |
| g700_j24 / j30 / j48 | 800 / 800 / 801 | 799 / 800 / 798 | NEAR | auto | 0 % |
| g400_j2 / j12 | 800 / 801 | 771 / 774 | PASSED | auto | +3.6 % |
| g400_spr_j2 | 713 | 685 | PASSED | auto | +4.1 % |
| g200_j2 / j12 | 538 / 566 | 485 / 516 | PASSED | auto | +10 % |
| hop, hop_j0 / j1 / j2 / j4 (apex) | 26.7, 155.5 / 153.1 / 150.8 / 146.3 | 26.7, 155.5 / 153.1 / 150.8 / 146.3 | no pull | no pull | **exact** |
| sl_hold / sl8_hold | 796 / 799 | 796 / 800 | NEAR | auto | 0 % |
| sl_a / sl_d (side key) | 927 / 930 | 938 / 942 | LOOK_AWAY | auto | **−1.2 %** |
| sl_s | 795 | 795 | NEAR | auto | 0 % |
| sl_g1 (Slingshot, 600) | 889 | 854 | NEAR | auto | **+4.2 %** |
| sl8_g1 (Slingshot, 800) | 975 | 911 | PASSED | auto | **+7.1 %** |
| sl8_w | 876 | 870 | NEAR | auto | +0.7 % |
| sl8_jump | 799 / v_h 628 | 799 / 625 | NEAR | auto | 0 % |
| sl_turn_d / sl_turn_w | 791 / 910 | 796 / 880 | LOOK_AWAY | auto | −0.6 / +3.5 % |
| sl_rel / sl_turn_rel | 228 / 382 | 233 / 386 | MANUAL | key | −2 % |
| sl_spr | 799 / 608 | 800 / 607 | NEAR | auto | 0 % |
| over75_jump / over55_jump (overhead, no keys) | 552 / 575 | 545 / 568 | NEAR | auto | +1.3 % |
| over75_jump_w / over55_jump_w | 655 / 774 | 683 / 808 | LOOK_AWAY | auto (view) | −4 % |
| rodeo_d | 484 | 528 | PASSED | auto | −8 % |
| dbounce | 442 | 496 | NEAR | auto | −11 % |
| tether (R5 hits the rock underside) | 724, 1.05 s | 700, 2.26 s, 393° | LOOK_AWAY | auto (view) | see §5 |

Not comparable (sim artefacts): `slide` / `g400_sl` (the sim start state is not sliding, so the run-up brakes on the ground), `slidegr*` /
`super_*` (R5 never connected; the sim fakes a hit).

Task targets: Slingshot **889 / 975 vs 854 / 911** (+4 / +7 %; the gain over the no-input pull is +93 / +176 vs R5 +58 / +112); side keys
**927–934 vs 938–945** (−1 %); Jump Grapple **1025–1049 vs 1006–1029** (+2 %), none at K ≥ 24 (exactly as R5); hop apex exact; detach timings
NEAR within 0.02 s, LOOK_AWAY 0.575 vs 0.576 s, CROUCH / MANUAL on the press with the 460 clamp.

## 4. Technique table

| Technique | Status | Notes |
|---|---|---|
| Basic pull / Drag Grapple (ground hook) | **works** | ramp to 800, release near the hook; on the floor the body glides (no landing) |
| Slingshot (G-1: turn 80° + W+A → W+D) | **works** | 889 / 975 (R5 854 / 911); gain comes from the side keys (650 > 425), no swing state |
| Side-key pull | **works** | 927–934 (R5 938–945) |
| Jump Grapple | **works**, window **input condition** | jump within the 0.2 s wind-up after a *ground* attach; later = nothing (pull masks it). Air attach: no window [inf, R5 only tested ground] |
| Grapple hop | **works** | apex exact vs R5 |
| Momentum carry / release → slide | **works** | crouch / 2nd press release keeps momentum (2nd press clamps above 460); crouch held lands into a slide |
| Release → lurch | **works (no lurch)** | a release is not a jump (`m8b_grapple_lurch`, test `ReleaseIsNoJumpAndLandsIntoASlide`); the attach jump does open a window [inf] |
| Grapple → wall bounce | **works** | release 45 u before the hook, momentum reaches the wall, jump = wall action (test `GrappleIntoAWallThenBounce`) |
| Grapple → zipline handoff | **works** (unchanged M6-G) | `m6c_grapple_highline` |
| Zipline → grapple | **works** | the grapple ends the ride (newer driver) and pulls (test `ZiplineToGrapple`) |
| Look-away detach | **works** [S21-client; local dedi differs] | 100°; R5 client 101–103° |
| Tether / Rodeo orbit | **model partial** | side key + turning view swings round the hook: 212–227°, max 701 (R5 700) before the head meets the slab and the passing / look-away rule lets go; R5 kept scraping round the rock to 393° (the local dedi ignored the client look-away). Thin pole: geometry for free play only, no R5 data |
| Super Grapple / Slide Grapple / Double-Bounce | **model missing / not reproduced** | R5 did not reproduce them (stop-loss); the SDK has retract / swing / rope-wrap states the S21 setfile does not use (grapple_swing false); nothing faked |
| Wiki 1200 u/s Slingshot | **not reached** (as in R5) | |

## 5. Tether / Rodeo [model]

Demo `m10a_tether` (tile D under the slab): sprint 1.8 s, jump, fire 75° up 0.2 s later, D held and the view turning right at 120°/s (the R5
`m10_g_tether` inputs). HSD: the body swings 212° round the hook in 0.98 s, max 701 u/s (R5 700), then the head meets the slab underside and the
look-away rule (100°) lets go; with the client rule off (the local dedi's behaviour) the passing rule lets go at 227°. R5: 393° in 2.27 s, still
scraping along the rock underside. The orbit emerges from the side key + view (no hard-coded orbit); the remaining gap is the contact behaviour
under an overhang and the detach while scraping. Without the view turn: 35° (the failure variant).

## 6. Tests

New: `R5Replay/Tests/Editor/R5MotorM10ATests.cs` (`GrappleM10ATests`, 33 cases: M4 replay grapple untouched, ramp, 49° hold, air entry kept,
rope-down gravity, W clamp, side keys ×2, Slingshot ×2 (R5 geometry, ±8 %), jump grapple ×5 (K 1/6/18/24/none), attach jump +286.8 over a plain
command, hop ×5 (exact apexes), crouch, 2nd press ×3, look-away on/off, overhead overshoot, floor glide, rope 850, script cooldown formula,
Pathfinder slot cooldown, attach jump = one effect on a Valkyrie body, grapple → wall bounce); `Game/Tests/Editor/M10AGameTests.cs` (preset and
S21 grapple on every grapple body, yard layout + anchor geometry, the 7 demos and failure variants, release → no lurch / slide, zipline →
grapple).

Changed existing tests (why):
- `PracticeGameTests.ApplyKeepsTheLoadoutAndAddsTheFunTraits`: grapple bodies get the 1100 ceiling (was 900); a no-grapple preset still 900.
- `JumpArbitrationTests.EveryJumpPressUserHasItsPlaceInThePriorityTable`: the grapple is a jump owner (attach-jump window).
- `M8FuzzTests.TheFuzzSlidOnTheSlopes`: the S21 grapple changed seed 201's random paths (no slope slide left); now any of the three fuzz seeds.
- `SkillFuzzTests` (uses count): the S21 preset's refused presses (1 charge, 10–30 s) count as use.
- `SkillLoadoutTests.PresetsHaveThreeToFourValidSlots`, `PhaseBreachTests.AshRouteLoadoutIsValid`, `M9BGameTests` (loadout counts): 7 presets.
- `M8CGameTests` / `M9AGameTests` / `M9BGameTests` / `M9CGameTests` (demo order, block counts): the M10-A demos and yard come last.
- `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: cases for the 7 new demos.

Results: EditMode **1623 / 1623**; PlayMode **1 / 1** (the smoke in the game loop).

## 7. Regression, build, smoke

- Replays (m5/unity/regression.md): M2+M1 v2 vs main **111** identical; vs pre-M3 **35 / 76**; M1 first guess **111**; M3 **90**; M4 with
  `-scenarios <abs>/m4/unity/scenarios.json` **114 identical** (incl. hold_r1701/r1702, near_r2101/r2102). The M4 replay builds its grapple
  with `GrappleParams.R5Reference()` (s21 null; the s21 keys are left out of the report).
- Build `HSD-Build/M10A/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10A\HSD-Practice.exe`), exit 0.
  The re-serialised `Scenes/Practice.unity` and `ProjectSettings/ProjectSettings.asset` were reverted; the config assets (new `grapple` block) and
  loadout assets (new `scriptCooldown`, new `PathfinderS21.asset`) are committed.
- Smoke `-batchmode -nographics -smoke 12`: exit 0. `1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset; events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 184/184 verdicts as expected (92 SUCCESS at shift 0, 92 failure cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16, M9-C 14/14, M10-A 14/14); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2107 bytes); 97580 commands in total`
- Older demos whose trajectory changed (hash of every command), all verdicts unchanged: `grapple_slide` (release now NEAR at 515 u/s, was GAP
  534; slide kept 100 %), `grapple_range`, `m6_grapple_release` (manual release 249 u/s, was 248), `m6c_anchor_release`, `m6c_grapple_highline`
  (ride 0.71 s, was 0.73), `m6b_valk_grapple`, `m7_djump_grapple`, `m8b_grapple_lurch`, `m8b_chain_grapple`. Their gameplay is R5-faithful under
  the S21 law, so nothing moved to Fun. Every other demo and both scripted routes are bit-identical; course lap 80.82 s.

## 8. Gaps and open questions

1. **p0** (hook at eye height, rope ~5° up): R5 728 vs HSD 608 — R5 exceeds the ramp by 145 u/s with an unbraked vertical cross component; no
   single brake rule fits it together with the 49° pulls. Open.
2. Brake gating is a fit (§2); `hold_d` / `dbounce` / `rodeo_d` (wall contact or a lateral pass at short range) are 8–11 % low.
3. Side-key and Slingshot peaks are reached in the last 0.2 s before R5 meets the rock; HSD's +4–7 % on the Slingshot partly reflects that.
4. Look-away 100° in Reference by the lead rule; the true S21 server behaviour is unknown (local S3 dedi ignores it). One parameter
   (`s21.lookAwayAngle`, NaN = off).
5. Attach jump only after a ground attach [inf]; whether an air attach also opens a window is unmeasured.
6. Script cooldown: the JumpPad_GiveDoubleJump end signal is not modelled (pad double jump during tracking); a use that never attaches costs the
   base 10 s [design].
7. Tether / Rodeo: §5. Super Grapple, Slide Grapple, Double-Bounce: not reproduced in R5, not modelled.
8. Fun uses the same S21 grapple (no separate Fun values).

## 9. Design values

1100 horizontal ceiling on S21-grapple bodies; the brake gating (§2); yard geometry other than the R5 anchor distances / heights (GY: anchors at
438 u / 576 u and 589 u / 661 u, jump lane marks 400 / 700, slab underside 470, pole 40 × 40 × 700); HUD text (attach-jump window "JUMP",
pull speed vs ramp) is visual only; no-attach use costs 10 s.
