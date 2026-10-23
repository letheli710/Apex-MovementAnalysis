# M10-C + M10-D1 (track U): Octane (stim, jump pad, ceiling surf) and the slide fixes in HSD-Unity

HSD-Unity branch `m10c/octane-slide`, commit `60ae630 (37 files)` (from main `06a5c55`), Unity 6000.6.5f1. Inputs: `m10/M10-PLAN.md` (M10-C, D1, D4),
track R `m10/r_octane/OCTANE-M10.md` + `params.json` and `m10/r_slide/SLIDE-D1-M10.md` + `params.json` (R5Flowstate local hybrid build, S21 client +
S3 dedi, 120 fps; lead-verified), track D `m10/d_library/TECHNIQUE-LIBRARY-M10.md` §3.35–3.38, M4 `m4/octane/OCTANE-PRIMITIVES.md`, M2
`m2/slide/SLIDE-MODEL.md` / `m2/PARAMETER-TABLE.md`, M8-C pad double jump, M9-C superglide re-arm, M10-D pad lurch rule.

Result classes (M10 rule):
- **Numbers / rules tests: pass.** EditMode 1853 / 1853, PlayMode 1 / 1 (§7).
- **Real-input demos: pass.** 10 new `m10c_*` demos, each with a failure variant; smoke 222/222 (M10-C 20/20).
- **Human feel: not accepted** (needs the user's playtest; guide `m10/PLAYTEST-GUIDE-M10C.md`).

Labels: **[meas]** R5 track R measurement, **[S21-client]** the hybrid build's S21 client prediction (the local S3 dedi differs), **[src]** script
source, **[fit]** chosen to match the R5 numbers, **[inf]** interpretation, **[model]** what the measured model gives where R5 has no data,
**[design]** HSD choice. Nothing from 6 Jan 2026 or later (post-S21: Triple Jump, Squad Rush, base 2 pads, base direction change, Stim 52 % / 0.7 s
delay, Stim Surge) is in the Reference.

## 1. Where the rules live (and why the replays cannot change)

Every new motor / world rule is a `[NonSerialized]` field of `R5MotorV2Params` (never in a report, never in an asset), off in the replay motor
(`R5MotorV2Params.R5Reference()` / `FromTrial`) and switched on by `MovementConfigs.Reference()` (Fun inherits it). The replay reports keep their
parameter lists and their `Choices` text; the only serialised change is the Reference / Fun config's existing fitted field
`slideBoostRefundWindow` 0.4 → 0.225 (config assets regenerated; the replay motor keeps 0.4).

| Rule | Field (Reference value) | Code |
|---|---|---|
| D1 crouch release ends the slide | `slideReleaseEnds` (true), `slideWantToStopDecel` 400, `slideMaxStopSpeed` 350 | `R5MotorV2.Move` |
| D1 350 floor only on young slides | `slideMaxJumpSpeedWindow` (0.8 s; +∞ = M2) | `R5MotorV2.SlideJumpSpeed` |
| D1 refund window | `slideBoostRefundWindow` (0.225; replay 0.4) | same |
| D1 slide boost re-arm | `slideBoostRearm` (1.8 s; 0 = always boosted) | `R5MotorV2.Move` (slide start) |
| C3 ceiling surf | `ceilingSurf` (true) | `MovementWorld.AfterStep` |
| C2 pad heading without motion | `JumpPadParams.straightUpWithoutMotion` (set from `OctaneParams.padStraightUpWithoutMotion`) | `JumpPadAbility.BeforeMove` |
| C2 ×1.2 push (upgrade) | `JumpPadParams.pushScale` (1; from `OctaneParams.padPushScale`) | `InstantImpulse.PadLaunch` |
| C2 Mad Hops | `OctaneParams.madHops` (Reference false, Fun true) | `MovementConfig.Apply` (pad slot charges 2) |

**Do the original R5 recordings encode the new slide rules?** All 67 M2 / M1 / M3 trials were replayed in the scratch harness with the four D1 rules
switched on in the replay motor (not committed): 65 are bit-identical, the two that differ are both M3 `e8_slide_chain` trials (r1015 / r1016), and
both get much closer to R5 — position RMS 2.225 → 0.815 u and 2.196 → 0.900 u, |v_h| RMS 7.48 → 0.15 u/s. Toggling the rules one by one: the
**crouch-release rule alone** gives the whole improvement (the trials release crouch in the slide). So an independent older recording confirms the
release law. The replay motor was **not** switched (the rule: the replays stay byte-identical); switching it would change exactly those 2 M3 report
sets for the better — a lead decision.

## 2. D1 slide (Reference; Fun the same)

### 2.1 Crouch release [meas, fit]
Sliding on the ground with duck released: pre |v_h| ≤ 350 → the slide ends before the move (that command is a crouched ground command: over-speed
decel 1500·dt); above 350 the slide keeps going with s' = (s − 400·dt)·0.7^dt (slideWantToStopDecel replacing slideDecel 100; census values M2 called
"not exercised"). On a slope the slope term stays on next to the stronger decel.

| Release at slide age | R5: commands to the end, |v_h| at the end | HSD |
|---|---|---|
| 0.10 s (434.06) | 19, 336.26 | 19, 336.25 |
| 0.25 s (396.85) | 11, 335.06 (333.6–335.6) | 11, 335.59 |
| 0.50 s (339.12) | 0, 326.62 | 0, 326.64 |
| 1.00 s (~237) | 0 | 0 |

Slope check (M8 r_slope, duck released on 29.9° at ~550: "flat law again, mean extra +24 u/s²" [meas]): HSD now gives +25 (400 + decay − slope
term); the M8-B model (slope term off on release) gave 0. The M8-B Reference test was updated to the new law (§7).

### 2.2 Slide jump vs slide age [meas, fit] — "够像就行"
Fresh boosted slide (start 457.8): t < 0.225 s → s − lastBoost (refund); 0.225 ≤ t < 0.8 s → max(s, 350); t ≥ 0.8 s → s kept. A slide without a boost
(re-arm, or resumed by a ducked landing) keeps its speed (M3 rule, unchanged).

| Jump at | R5 pre → exit | HSD exit | Window evidence |
|---|---|---|---|
| 0.10 s | 434 → 273.05 | 273.1 | refund (M2 e5 0.201 s also refunded) |
| 0.25 s | 396.8 → 396.83 kept | 396.9 | refund window edge in (0.201, 0.25] → 0.225 [fit, midpoint] |
| 0.40 s | 361.5 kept | 361.6 | v > 350 kept (answers M2 open Q2: keep, not cap) |
| 0.60 s | 317 → 350.01 | 350.0 | 350 floor (M2 e5 0.597 s also 350) |
| 1.00 s | 236 kept | 238.0 | floor window end in (0.597, 1.0) → 0.8 [fit, midpoint; 0.8 s itself unsampled] |

M9-C's "Unity 236 at 0.25 s" was the 0.4 s refund window; it is now 396.9. The M5.5 `slide_jump` demo (jump at 0.5 s → 350) is unchanged.

### 2.3 Boost re-arm [meas + inf]
A duck-press slide within 1.8 s of the last slide boost starts with no boost and is "not boosted" (no refund, no floor). R5: a second slide 1.0 s after
the first boost starts at 297.33 (HSD 297.3) and its jumps keep 249.8 / 187.6 (HSD keeps the pre speed exactly). The 1.8 s is the M9-C superglide
re-arm [meas M9 r_d1, 1.6–2.1 s]: one boost cooldown [inf]; R5 bracket for the slide itself: (1.0 s, ?). The superglide check is unchanged (it reads
the same boost clock); whether a slide right after a superglide loses its boost stays unmodelled (M9-C gap).

## 3. C1 Stim

Checked against R5 (no change to the ability): onset 0.158 s (R5 0.1592), msc 1.15·1.298038 = 1.4927 (R5 1.4927), back to 1.15 at 6.49 s after the
onset (R5 6.4884: the 0.5 s cosine fade crosses 0.1 % there), stim slide start 594.5 (R5 594.69), stim sprint cap 420.95 (R5 420.95), the lurch clamp
0.7 × the stim sprint cap (M4).

- **Re-use lock** [meas + src]: R5 refuses a second stim for the 6.0 s charge + 0.7 s cooldown (+1.0 … +6.6 s nothing, +7.5 / +9.0 s a new stim).
  The new **Octane S21** preset gives the stim slot a 6.7 s recharge from the press (the ability itself also refuses while the stim runs, 6.66 s);
  older presets keep their practice cooldown (M5 4 s → effectively 6.66 s through the running-stim refusal). Open conflict (track D O-2): the wiki's
  pre-2026 "1.8 s delay" implies re-stimming during an active stim; R5 and its script block it — HSD follows R5.
- **Hops** [model, gap]: R5 stim hops leave at 410.6 (plain 299.0). HSD's ground-jump clamp is min(v, sprintspeed·msc) = 420.9 under stim (+2.5 %).
  410.6 = 420.95 − 10.3 looks like one 1250·dt over-speed decel at the non-stim sprint cap, but the R5 rule is not identified; not changed.
- Health cost (−20, Thick Skin −5 per pick): not modelled (note only).

## 4. C2 Jump pad

- **Launch direction = the horizontal direction of motion at contact** [meas]. Unity already used the velocity (`headingFromVelocity`, M4); R5 now
  confirms it (view 90 + D moving +X → +X; view 180 + S moving +X → +X; a W tap and no key at contact, drifting 170 → +X at 63.4°). New: with no motion
  at all the launch is **straight up** (1150 up) [inf: normalize(0 + 2ẑ); the wiki's "no Forward → straight up"; R5 untested at exactly zero] —
  every pad of a config body; the replay kit keeps the M4 view-yaw fallback.
- **Stand / crouch** [meas, M4 agrees]: 1150·normalize(ĥ + 2ẑ) = 514.3 / 1028.6 at 63.43° (R5 1147.76 at 63.38° after the slow-mo half step),
  crouched V = 1: 813.2 / 813.2 at 45° (R5 1148.23 at 44.91°). Approach speed discarded (R5 walk / sprint / drift identical).
- **Upgrades (S21 Level 2 / 3)** — `OctaneParams` on the config, applied to the new Octane S21 preset (legend "octane"):
  - **Mad Hops** (L2, S21 official + `upgrade_ult_one` clip 2×90 [src]): 2 pad charges. Reference **off** (the S21 base Octane, no upgrade picked);
    Fun **on** [design: the S21 "2nd pad" combos].
  - **×1.2 push** (`JumpPad_GetPushVelocity` with `PAS_ULT_UPGRADE_ONE` [src], R5 1377.8 / 1378.2 [meas]): `padPushScale`, 1 in both configs
    (track D: no dated source names a +20 % launch upgrade; version unknown). When set it scales only the preset's own pads, never the map pads.
  - **Airborne Agility** (L3, `PAS_ULT_UPGRADE_THREE` → `enable_doublejump_aircontrol` [src]): R5 shows **no measurable difference** on the pad
    double jump (Δv (−264, −272, +197) and v 0.5 s later identical) → a flag with no effect; the M8-C pad double jump is unchanged.
  - Thick Skin: health only, not modelled.
- **Combos** (tests / demos):
  - pad → TS: the Reference launch opens no lurch window (M10-D3, R5 r_d1); a jump just before the pad keeps **its** window through the launch, so an
    A tap ≤ 0.5 s after the jump lurches (209.3 clamp) — **[model]**, R5 O-5 untested (demo `m10c_pad_ts_prejump`).
  - pad → slide: a crouched launch with crouch held lands into a slide; the M4 hard-landing slowdown takes 813 → 733 (test).
  - pad → wall: a flight into a wall faced with W held is taken by the M6 climb (jump = the climb's jump-up); a wall bounce needs the M6 wall-jump
    conditions as before (test).
  - pad → zipline: the existing M6-C demo `m6c_pad_airmount` (unchanged).
  - stim + pad: the launch replaces the velocity, so the stim does not change the arc (M4, W-Pad) — unchanged.

## 5. C3 Ceiling surf (Reference per the S21 client; Fun the same)

R5 (M10 r_octane, 68 trials): the **S21 client predicts the surf** — on contact z stays pinned while vz stays > 0 and decays at 600 u/s² (g × the pad
slow-mo 0.8), v_h kept; the **local S3 dedi clips vz to ~0** and corrects the client after 6–16 commands. The same split for a sprint jump into a
100 u ceiling (client pins it with vz 180, decaying at g). The technique is documented before S21 (Mokeysniper 12 Jan 2021; wiki). Lead rule:
follow the S21 client → Reference surfs, label **[S21-client; local dedi differs]**.

**Rule** (`MovementWorld.AfterStep`): when the swept move enters a ceiling plane (n.z ≤ −0.7) while moving into it, the position is stopped at the
ceiling as before, but the velocity is **kept** (no v·n removal) — only in free flight: not on a kinematic traversal command (climb, mantle,
zipline, Vantage drive), not under an external acceleration (grapple pull), not with gravity off (lift ride, Fun flight) or reversed. Everything else
follows from the existing motor: vz keeps decaying under the command's gravity (600 u/s² in the pad's dt·0.8 flight, 750 otherwise), v_h and the air
strafe carry on (500 u/s², wish cap 69 — so a strafe on the ceiling needs W released, as the wiki says), and past the ceiling's edge the leftover vz
throws the body up. No new state, no new parameter beyond the switch.

| Pad under a flat ceiling (stand) | R5 client contact vz | HSD contact vz | HSD surf |
|---|---|---|---|
| 150 u | 966.1 | 971.1 | vz/600 = 1.6 s if long enough |
| 250 u | 885.9 | 891.1 | 1.48 s, ~760 u at 514 |
| 400 u | 750.9 | 751.1 | 1.25 s |
| 250 u crouched | 590.3 (smooth) / 595.4 (rough) | 600.7 | 1.0 s at 813 |
| sprint jump, 100 u | 180.1 | 199 | 0.27 s at g |

The HSD contact vz is 5 u/s higher at 150 / 250 (the hull top vs R5's head; 48 / 72 u hulls are design values); R5's pinned time (0.05–0.09 s) is
the client before its correction, so the full surf length is [S21-client + model]. Exit speed: the leftover vz plus the unchanged v_h (514 / 813).

- **Not broken**: climb / mantle / zipline / Vantage drive (kinematic) and the grapple pull (external acceleration) clip as before; lifts and the Fun
  flight (gravity off) clip as before. Every older demo and test keeps its verdict; `m10a_tether` is the only older trajectory where a surf now
  happens (a grapple release under the GY slab: after the release the body is in free flight and surfs; verdict unchanged).
- Rough / interrupted ceilings: each slab face is a plane; a surf ends at any edge (the wiki's "needs a smooth ceiling").
- Stored through a zipline (wiki): not modelled (a mount is kinematic; the stored vz is lost) — gap.

## 6. Practice area, preset, demos

- **Octane S21 preset** (loadout 8, key `;`): stim on Q (6.7 s recharge), jump pad on Z (1 charge, practice cooldown 15 s; S21 script 90 s), the
  config's Octane upgrades and the M8-C pad double jump. The M5 "Pathfinder-Octane mobility" preset is unchanged.
- **Octane yard OY** (`PracticeMapM10C.cs`), in two bands west of the A lane that no older block, rope, pad, demo path, 30 s scripted route (every
  config × loadout) or course lap touches (checked with an occupancy map of all of them, then by the trajectory hashes): OY1 / OY2 / OY3 pads under
  150 / 250 / 400 ceilings (y −300 / −500 / −700, pads at x −970, slabs 400 / 400 / 800 long), OY2's deck (top 250) past its ceiling for the throw,
  OY4 open pad-direction lane (y 400, pad at x −700) with a landing patch 1300–1500 u east, OY5 sprint-jump slab (bottom 100). OS: the A lane as the
  stim course (sign only). 4 map pads appended after the 2 older ones (every older index unchanged).
- **Demos** (Reference, Octane S21; F6 / smoke):

| Demo | Success | Failure variant |
|---|---|---|
| `m10c_stim_relock` | Q, Q at +3 s refused, Q at +7.0 s → a second stim | Q at +5.0 s refused (locked 6.7 s) |
| `m10c_stim_slide` | stim, sprint to 421, crouch → slide 594.5 | Q after the crouch → plain 457.8 |
| `m10c_pad_motion` | view north, D east, release D, drift onto the pad → launch east | D released too early: stops 66 u short |
| `m10c_pad_crouch` | crouch before the pad → 45° (813 / 813) | crouch after the contact → 63.4° |
| `m10c_ceiling_surf` | OY2 30° approach, view east before the pad → surf 0.69 s, thrown up with vz 476, lands on the deck | turn too late → 30° launch leaves the ceiling's side after 0.36 s, misses the deck |
| `m10c_sprint_jump_ceiling` | sprint jump under the 100 slab → pinned 32 commands, contact vz 199 | jump past the slab → no contact |
| `m10c_pad_ts_prejump` | jump just before the pad, A 0.28 s after the jump → lurch 24° [model] | A 0.68 s after the jump → window closed |
| `m10c_slide_release` | release crouch 0.10 s into the slide → ends 19 commands later at 336.3 | crouch held → the slide runs its 1.68 s |
| `m10c_slide_jump_age` | slide jump at 0.25 s → 396.9 kept | at 0.10 s → 434 → 273 (refund) |
| `m10c_slide_rearm` | second slide 1.9 s after the first boost → 457.8 | at 1.0 s → no boost, 297.3 |

- Probe events: `CEILING_SURF` / `CEILING_SURF_END`; `SLIDE_START (no boost: not re-armed)`; `SLIDE_END (crouch released)`; record fields
  `ceilingSurf`, `slideUnboosted`, `slideReleased`.

## 7. Tests

New: `R5Replay/Tests/Editor/R5MotorM10CTests.cs` — `SlideM10DTests` (release table ×4, slide-jump age table, second slide no boost / re-arm ×2, replay
motor unchanged and nothing in a report, slope release +24) and `OctaneM10CTests` (stim regression, re-use lock ×6, stim hop [model], pad heading =
motion ×3, straight up / crouched, upgrades, pad → slide / wall, pre-jump window through the launch, surf at 150 / 250 / 400, edge throw + air strafe,
sprint jump at g, surf gating free / off / kinematic / pull / no gravity); `Game/Tests/Editor/M10CGameTests.cs` (preset and lock in both configs, yard
appended and free, every lane surfs in both configs ×6, the 10 demos + failure variants and their order, probe events).

Changed existing tests (why):
- `PadDoubleJumpTests.StandCrouchWalkAndJumpInEntriesGiveTheSameAdd`: the "stand" entry (zero speed on the pad) now launches straight up (C2); the
  double jump add (+201.81) is unchanged.
- `SlopeM8BTests.ReferenceSlopeSlideMatchesTheR5FitWhereItWasMeasured(30/35/40)`: duck released is now slope term − 300 (D1 + the M8 slope term,
  +25 at 30°, R5 +24 [meas]) instead of exactly the flat law; the duck-held assertion is unchanged.
- `ZiplineM8Tests.TransitionsWithSlideLurchDoubleJumpAndWallRun`: it tapped crouch for 2 commands and mounted "while sliding" 0.4 s later; the
  release now ends that slide, so crouch is held through the mount command.
- `WorldEquivalenceTests` (`LegacyBoxWorld`): the M6 traversal queries (`ProbeLedge`, `ProbeWall`, `CeilingClearance`, `ClosestRail`) now answer
  from a `MovementWorld` of the same boxes (as `Raycast` already did) instead of throwing. Reason: with the release rule the 30 s scripted run of
  Fun × Revenant-Wraith reaches the D platform face in the Fun flight, where the climb probes the face; the frozen M5.5 collision code is unchanged
  and all 20 equivalence cases are bit-identical.
- `SkillLoadoutTests.PresetsHaveThreeToFourValidSlots`, `PhaseBreachTests.AshRouteLoadoutIsValid`, `M9BGameTests` (loadout count): 8 presets, Octane
  S21 has 2 slots.
- `M10BGameTests` (the M10-B blocks / demos are now the last before the M10-C ones), `M8CGameTests` / `M9AGameTests` / `M9BGameTests` /
  `M9CGameTests` (demo order), `MovementDemoTests.EveryDemoFailsWithItsFailureShift` (cases for the 10 new demos), `MovementConfigTests` (the
  config assets carry the new `octane` block).

Results: EditMode **1853 / 1853**; PlayMode **1 / 1**.

## 8. Regression, build, smoke

- Replays (m5/unity/regression.md): M2+M1 v2 vs main **111** identical; vs pre-M3 **35 / 76**; M1 first guess **111**; M3 **90**; M4 with `-scenarios <abs>/m4/unity/scenarios.json` (incl. every m4_stim_* / m4_pad_*) **114 identical**.
- Build `HSD-Build/M10C/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10C\HSD-Practice.exe`), exit 0. The
  re-serialised `Scenes/Practice.unity` / `ProjectSettings/ProjectSettings.asset` were reverted; the config assets (refund window, `octane` block)
  and the new `OctaneS21.asset` are committed. ignore-cr stat equals the plain stat (37 files, +1468 / −50); no CR in the committed .cs.
- Smoke `-batchmode -nographics -smoke 12`: `[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset; events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 222/222 verdicts as expected (111 SUCCESS at shift 0, 111 failure cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16, M9-C 14/14, M10-A 14/14, M10-B 18/18, M10-C 20/20); course lap 80.55 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2109 bytes); 115899 commands in total`
- **Older demos and routes** (per-command hash of position, velocity, buttons, lurch, events; every older demo at shift 0 and its failure shift,
  202 runs, and the scripted M5 route in both configs, against main `06a5c55`): 196 identical, 6 changed, all verdicts unchanged:

| Run | Cause | Evidence |
|---|---|---|
| `m6_climb_superglide` −0.30, `m6c_barrier_superglide` −0.30, `m8b_sg_angle` −0.20 (failure variants) | crouch released while sliding at ~230–237 u/s → the slide ends (release rule) | the early-press superglide failure is the same (mantle cut) |
| `m8_slope_chain` +0.80 (Fun failure variant) | crouch released on the slope: stronger decel | lands without a slide at 501 instead of 506 u/s |
| `m6b_breach_gap_slide` 0.00 | crouch released at the end of the demo (315 u/s) → the slide ends 0.6 s before the demo ends | after every criterion (exit, landing, slide 457) |
| `m10a_tether` 0.00 | the look-away release at z 398 under the GY slab: free flight → ceiling surf (vz 542 kept instead of 0) | after the verdict (212° swing, max 701) |

  The smoke route (12 s, final pos (341.586, 146.165, 10)) is unchanged. The 30 s scripted runs change after 9–27 s through the release rule (the M5.5
  route releases crouch while sliding); they never enter the yard (checked).
- **Course lap 80.82 → 80.55 s** (7/7, all configs / loadouts): the autopilot crouch-slides under the K barrier and releases crouch behind it; that
  slide now ends at ≤ 350 and the body sprints on instead of decaying in a slide (toggling the rules: only the release rule moves the lap).

## 9. D4 leftovers

Checked the M9 / M10 gap lists (M9-A / M9-B / M9-C / M10-A / M10-B / M10-D UNITY docs, M9 report): no item clearly breaks a function; all are
unmeasured / [design] choices or lead decisions. Listed, not changed: Revenant long-climb end rule [design], Vantage drive shape / Echo AI, zipline
80 u rope / lockout source / vertical rope looking down, grapple p0 −16.6 % and Slingshot +4–7 %, gun-rope handoff speed, superglide → slide boost
(now: the slide re-arm reads the slide boost clock only).

## 10. Gaps and open questions

1. **Stim hops** 420.9 vs R5 410.6 (rule unidentified, §3).
2. **Slide floor window end** 0.8 s is a midpoint of (0.597, 1.0); **refund window** 0.225 of (0.201, 0.25]; **re-arm** 1.8 s borrowed from the
   superglide (R5: > 1.0 s).
3. **Ceiling surf length**: R5's client is corrected after 6–16 commands, so the full surf is the client law extrapolated [S21-client + model]; the
   hull heights (72 / 48) set the contact height; vz stored through a zipline (wiki) is not modelled.
4. **Pad straight up at zero speed** [inf]; "very high approach speed launches straight up" (wiki) is not modelled.
5. **Pad → TS** from a pre-pad jump window [model] (O-5 untested); pad wall-run (O-8) untested and not modelled (Fun wall-run applies as usual).
6. **×1.2 push** version unknown (off); Airborne Agility no effect in R5 (flag only); Mad Hops on in Fun only [design].
7. **Stim re-use** follows R5 (6.7 s lock) against the wiki's pre-2026 1.8 s delay (open conflict O-2).
8. The replay motor could take the release rule (2 M3 slide-chain replays improve, §1) — lead decision.

## 11. Design values

Yard geometry except the ceiling heights (slab lengths, widths 160, thickness 40, deck 300 × 200 at 250, lane spacing, pad positions, landing
patch), Octane S21 pad cooldown 15 s, Fun Mad Hops, the 0.225 / 0.8 / 1.8 s choices inside the measured brackets, demo thresholds (surf ≥ 0.5 s,
thrown vz > 150, hop/slide margins).
