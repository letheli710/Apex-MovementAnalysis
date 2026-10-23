# M10-B (track U): Pathfinder Zipline Gun in HSD-Unity

HSD-Unity branch `m10b/zipgun`, commit `151a432 (33 files)` (from main `fd04cba`), Unity 6000.6.5f1. Inputs: `m10/M10-PLAN.md` (M10-B: the new ropes
must use the existing ride system), track R `m10/r_zipgun/ZIPGUN-M10.md` + `params.json` (R5 S21 client + S3 dedi local build, 120 fps; lead-verified),
track D `m10/d_library/TECHNIQUE-LIBRARY-M10.md` (Zipline Gun section), S21 `mp_weapon_zipline.nut` / `mp_weapon_zipline.txt` (read-only), M9-A rope
rules (`m9/unity/M9A-UNITY.md`), M10-A grapple (`m10/unity/M10A-UNITY.md`).

Result classes (M10 rule):
- **Numbers / rules tests: pass.** EditMode 1735 / 1735, PlayMode 1 / 1 (§6).
- **Real-input demos: pass.** 9 new `m10b_*` demos, each with a failure variant; smoke 202/202 (M10-B 18/18).
- **Human feel: not accepted** (needs the user's playtest; guide `m10/PLAYTEST-GUIDE-M10B.md`).

Labels: **[meas]** R5 track R measurement, **[src]** S21 script / weapon file, **[fit]** chosen to match the R5 numbers, **[inf]** interpretation,
**[model]** what the HSD rope system produces where R5 did not measure, **[design]** HSD choice.

## 1. Design: how gun ropes plug into the ride system

There is **one** rope system. The gun only *places* ropes; riding them is the existing `ZiplineAbility` (M6-A3 / M8-A / M9-A).

- **Runtime rails in the world's rope list.** On arrival the gun calls `MovementWorld.AddRail` with an ordinary `Rail` (two points). From that command
  on every rope query sees it: the zipline's mount rule (`ZiplineAbility.Evaluate`: collector 120 u, Find, 34° cone, end zone, lockout, budget), the
  mount hint (AbilityVisuals reads the same `Evaluate`), the grapple ray (`MovementWorld.Raycast` with ropes) and the grapple → zipline handoff
  (`ClosestRail`). Nothing in the zipline was duplicated.
- **Per-rope ride law on the rail.** `Rail.ride` (new class `RailRide`, `[NonSerialized]` on the rail) is null for every map rope; the zipline then
  uses its own `ZiplineParams` exactly as before (same arithmetic, same values: map ropes are byte-identical). A gun rope carries
  `RailRide.GunRope()`: ramp 8.33 → +1000 u/s² for the 0.5 s mount state → +280 u/s² → cap 1000; end exit 600 along the rope (`EndExit`); `steep`
  (|d̂.z| > 0.7 [src]) → the end exit keeps only the vertical part and the jump-off goes along the view yaw; `jumpOffAlongRope` (sloped gun ropes jump
  off along the 3-D rope). `ZiplineAbility.Ride` reads the four ramp values and the end exit from the rail when it has a `ride`; `ExitHorizontal`
  (jump-off / crouch-off) takes the steep / along-rope branch only for gun ropes.
- **Removal keeps indices stable.** `Rail.active` (default true, `[NonSerialized]`). The gun's 10-rope limit sets the oldest inactive; `ClosestRail`,
  the grapple ray and `Evaluate` skip inactive rails; a body riding a removed rope lets go with its ride velocity (`ZIP_ROPE_GONE`). The rail stays in
  the list, so the zipline's `rail` index never shifts. `PracticeSession` builds a new world for every body (reset, demo setup, config / loadout
  switch), so a reset removes every gun rope — the R5 behaviour (every reset destroyed the earlier gun ropes [meas]).
- **The gun** (`ZiplineGunAbility`, ultimate slot, new file `R5Replay/Runtime/Abilities/ZiplineGunAbility.cs`): Z raises (aiming = Pending), LMB fires
  after 0.5 s, Z again holsters, 20 s aim timeout; a fire is evaluated every aiming command (`Evaluate`: stance, eye ray against the solids, distance,
  stations, rope-line test) and shown as the preview. A valid fire spends the charge (`Activations`), the projectile "flies" for |impact − eye| / 2600 s
  and the rope is added on the command it lands. The charge time is a script cooldown (`IChargeTimer`, the M10-A mechanism): fire + 180 s
  (Reference) / 10 s (Fun); a refund sets it to "now". Config: `MovementConfig.ziplineGun` (Reference `ZiplineGunParams.Measured()`, Fun
  `ZiplineGunParams.Fun()`), applied in `CreateBody` like the grapple / Vantage sets; slot binding in `SkillSlotSystem` (`world` = the body's world).
- **Preset.** `SkillLoadouts.Pathfinder()` ("Pathfinder S21", key `\`) gets the slot `zipline_gun` on Slot4 (Z), 1 charge, `scriptCooldown`, plus the
  arbiter row `ZiplineGunTraits()` (priority 20, aim guard 25 s). The same preset in the Fun config is the "Fun Pathfinder" (10 s charge). No other
  preset changes. Bodies with the gun get the 1100 horizontal ceiling (the Pathfinder preset already had it through the S21 grapple).

## 2. Rules and numbers (R5 vs HSD)

| Item | R5 / source | HSD | Label |
|---|---|---|---|
| Stance | fire on the ground / wall-run / wall hang; air fire 0/3, clip kept | ground; HSD wall-run and ledge hang (M7-A, Fun) also allowed; in the air = dry fire, charge kept | [src+meas] |
| Distance | 700–8000 (origin → impact); floor 600 dry 0/3, 800 rope 3/3; wall 610 dry, 790 rope | 3-D origin → impact ≥ 700 and ≤ 8000; eye ray length 8060 | [src+meas] |
| Dry fire | no projectile / clip kept; failed deploy refunds | no rope, no charge spent, the gun stays raised (`ZIPGUN_DRY_<reason>`) | [meas] |
| Obstacles | projectile hits the first solid | the first solid on the eye ray is the target (ropes do not stop it) | [design] |
| Rope through solids | native spot finder (not measured); script `CanTetherEntities` traces station → station | the rope line start → end (2 u in from each end) must miss every solid and stay above the floor, else dry fire `ROPE_BLOCKED` | [design + src hint] |
| Rope start | begin station at the player: 16.2 u from the origin, 112.1 u above the floor | origin + 16 u toward the flat aim, + 112.1 u | [meas] |
| Rope end | impact + station; rope end 112.7 u above the hit surface | standable impact (n.z ≥ 0.7): + 112.7 u up; wall / ceiling: 16 u out along the normal at the impact height | [meas] / [design] |
| Projectile | 2600 u/s [src]; rope seen 0.3 / 0.5–0.6 / 0.8 / 1.4 s at 800 / 1500 / 2300 / 3640 | rope added at fire + |impact − eye| / 2600 (0.31 / 0.58 / 0.89 / 1.40 s) | [src+meas] |
| Ride ramp | 502.2 @0.5 s, 641.5 @1.0, 781.9 @1.5, 1000 from ~2.3 s; 940 at the end of a 1475 u rope; ride 2.07 s | 502.3 / 642.3 / 782.3, 1000 at 2.3 s; 1484 u rope: peak 943, ride 2.09 s | [fit] |
| Cap | gun ropes 1000, map ropes 600 | per rope (`RailRide.speed` 1000; map ropes `ZiplineParams.speed` 600) | [meas] |
| End exit | 90–130 u before the end; 600 along the rope (flat 600; 11° 589 / +113; 42° 444 / +335 after 0.1 s) | stop-short 90 (autoDetach 100); 600·d̂ | [meas] |
| Steep exit | 52° rope: v_h ~14, vz 405–417 0.1 s after | vertical only: 600·sin θ (52.09° → 473.3, inside the R5 bracket 473–486 at the detach) | [fit] |
| Jump-off flat | (400, 0, 289.8) at 584 u/s | map law (400, 0, 289.8) | [meas] |
| Jump-off steep | view turned 90°: (0, −400, 289.8) (2/3) | view yaw · min(v, 400) + 289.8 | [meas] |
| Jump-off 42° | (296, 0, 559) = 400·d̂ + 289.8 ẑ | sloped gun ropes: d̂(3-D)·min(v, 400) + 289.8 ẑ (crouch-off without the vz [inf]) | [meas 2] |
| Super jump | vz ~575 (the 0.1 s sample is ~502–507) | map law: 564 on the command (502 after 0.08 s of gravity) | [meas] |
| Several ropes | 4 coexisted; cap 10 per player [src] | ≤ 10; the 11th removes the oldest (a rider lets go) | [src+meas] |
| Refund | destroyed within 3 s → clip back [src] | a rope removed within 3 s of its creation refunds (reachable only through the limit; HSD has no rope damage) | [src] |
| Lifetime | permanent [src] | permanent (`ropeLifetime` 0) | [src] |
| Charge | clip 180 at 1/s (meas 0.80–0.99/s) | 180 s Reference; 10 s Fun | [src] / [design] |
| Raise | R5 schedules fired 1.0 s after the raise | fire accepted 0.5 s after Z | [design] |
| Grapple onto own rope | 1/2 hooked and handed over; the ride restarted the ramp (397 → 252 → 502 @0.5 s) | existing M6 handoff (136 u, entry speed kept, max with the ramp) on the gun ramp | [meas] / [model] |
| Mount rules on gun ropes | (map rope rules, M9-A) | identical: mid-rope / air mounts, 0.35 s air lockout (Reference), ground + 2 air re-grabs, super jump, end zone, mount hint | [model, same system] |

## 3. Items (B2 / B3)

| Item | Status | Where |
|---|---|---|
| Aim + validity (stance, 700 / 8000, surface, obstacles, rope line) | done | `ZiplineGunAbility.Evaluate`; tests `TheMinimumDistance…`, `WallTargets…`, `AnAirFire…`, `NothingWithinRange…`, `AnObstacleInTheAimPath…`, `ARopeLineThroughASolid…` |
| Visible aim preview | done | AbilityVisuals: rope line start → end + impact ring (green valid & raised / grey raising / red dry), red ball where the rope line meets a solid, projectile ball; HUD crosshair text + `zip gun` status (ropes n/10) |
| Projectile 2600 u/s, rope on arrival | done | `TheRopeGeometryAndTheProjectileTime` (4 distances) |
| Runtime rail in the existing rope set, per-rope params | done | §1; `AGunRopeRampsTo1000…`, `ALongGunRopeCapsAt1000AndAMapRopeAt600`, `MapRopesCarryNoRideLaw` |
| Mid-rope / air mounts, lockout, re-grab budget on gun ropes | done (same code) | `GunRopesKeepTheMapRopeMountRules` |
| Super jump, end detach, steep vertical exit, view jump-off, sloped jump-off | done | `TheSuperJump…`, `SteepRopes…`, `ASlopedGunRope…`, `AFlatGunRopeJumpOff…` |
| Max 10 ropes, removal while ridden, refund 3 s, reset, cooldown | done | `TenRopesAtMost…`, `ARopeRemovedWhileRidden…`, `ARopeDestroyedWithinThreeSeconds…` (1.0 s yes / 3.5 s no), `AResetRemovesTheGunRopes`, `TheChargeReturnsAfterTheConfigCooldown` |
| Grapple → gun rope, gun rope → grapple | done | `TheGrappleHandsOverToTheOwnGunRope`, `AGrappleFromAGunRopeEndsTheRide`; demo `m10b_grapple_own_rope` |
| Zipline → super jump → air turn | done | demo `m10b_super_jump_turn` (vz 552 on the record, lurch \|Δv\| 144) |
| Chaining several ropes | done (Fun: 10 s charge) | demo `m10b_chain_two` |
| Self-built routes: yard ZG | done | `PracticeMapM10B.cs`: fire lane + marks 600/700/800/1500/2300/3000, deck 250 + ramp (downhill ropes), wall-run wall (Fun), steep wall 1000 + tile 600 u in front |
| Real-input demos + failure variants | done | §4 |
| Chinese practice guide | done | `m10/PLAYTEST-GUIDE-M10B.md` |

## 4. Demos (Pathfinder S21 preset, key `\`)

| Demo | Shows | Result (shift 0) | Failure variant |
|---|---|---|---|
| `m10b_fire_ride` | fire at the 3000 mark, rope after 1.15 s, X, ride to 1000, end exit 600 | peak 1000, END 600 after 3.60 s | X 1.4 s earlier: no rope yet |
| `m10b_map_rope_cap` | the same preset on the M6 flat map rope | peak 600, 2.13 s at the cap | turn to the rope after X: no mount |
| `m10b_dry_fire` | 600 u dry fire (charge kept), 900 u rope | dry + rope (884 u) | aim raised too late: both dry |
| `m10b_air_fire` | air fire refused (charge kept), ground fire rope | DRY_AIR + rope | 2nd LMB 0.6 s earlier (in the air): both dry |
| `m10b_steep_exit` | ~50.5° rope from the steep-wall tile, END straight up | v_h 0, vz 463 | jump 0.8 s earlier: JUMP exit |
| `m10b_steep_jump_view` | turn 90° on the steep rope and jump | (400, 0, 290) along the view | turn 0.3 s late: along the rope |
| `m10b_chain_two` (Fun) | rope 1 → land → charge back (10 s) → rope 2 from the landing point → ride | 2nd mount 1720 u up the lane | 2nd Z 1.6 s early: refused (cooldown) |
| `m10b_grapple_own_rope` | gun rope, Q at the rope 300 u ahead → handoff → gun ramp | handoff at 2.43 s, peak 892 | Q before the rope exists: nothing hooked |
| `m10b_super_jump_turn` | X at the station, jump-off, 2nd jump ≤ 0.2 s, D tap | vz 552, lurch \|Δv\| 144 | 2nd jump 0.2 s late: no super jump |

## 5. Rope through geometry, endpoints, deletion (decisions)

- **Rope line vs solids** [design]: a fire whose rope line (begin station top → end station top) would cross a solid is a dry fire (`ROPE_BLOCKED`, a red
  ball in the preview). R5's native placement was not measured; the S21 script's `CanTetherEntities` (station-to-station line trace against the static
  world) is the only source hint. The world is static, so a placed rope can never end up inside geometry; the ride itself is the zipline's (a body pushed
  more than 8 u off the hang path detaches, `ZIP_BLOCKED`, as on map ropes).
- **Endpoints**: start 16 u ahead / 112.1 u up [meas]; floor / ledge-top impacts end 112.7 u above [meas]; walls / ceilings 16 u out of the face [design].
  A rope ending on a wall face cannot carry the body onto that wall's top (the body hangs 80 u below the rope, detaches 90 u early; the steep vertical
  exit rises ~150 u) — consistent with R5 (the 52° exit fell back).
- **Steep ropes and the mount cone** [model]: a ≥ 45° rope is outside the 34° mount cone when looking level from its begin station; look ~40° up to mount
  (the M9-A Find rule; R5 did not report the view of its steep mounts).
- **Deletion / expiry**: permanent ropes [src]; the 11th removes the oldest [src]; a body reset removes all [meas]; a removed rope frees its rider.

## 6. Tests

New: `R5Replay/Tests/Editor/R5MotorM10BTests.cs` (`ZiplineGunM10BTests`, 34 cases) and `Game/Tests/Editor/M10BGameTests.cs` (6 tests: the gun on the
Pathfinder preset in both configs and nowhere else, the yard appended after every older item and free of older blocks / ropes / checkpoints, the yard
geometry against the R5 distances and the steep wall, the 9 demos + failure variants and their order, a body reset removes gun ropes, visuals / HUD
read-only).

Changed existing tests (why):
- `SkillLoadoutTests.PresetsHaveThreeToFourValidSlots`: Pathfinder S21 now has 2 slots (grapple + gun).
- `M10AGameTests.TheGrappleYardIsAppendedAfterEveryOlderItemAndFree`: the M10-A blocks are now the last before the M10-B yard (`m10bBlockStart`).
- `M8BGameTests.ChainYardIsAppendedAfterEveryOlderItemInFreeGround`: the M8-B ramp is now the last before the M10-B deck ramp.
- `M8CGameTests` / `M9AGameTests` / `M9BGameTests` / `M9CGameTests` (demo order): the M10-B demos come last.
- `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: cases for the 9 new demos.

Results: EditMode **1735 / 1735**; PlayMode **1 / 1**.

## 7. Regression, build, smoke

- Replays (m5/unity/regression.md): M2+M1 v2 vs main **111** identical; vs pre-M3 **35 / 76**; M1 first guess **111**; M3 **90**; M4 with
  `-scenarios <abs>/m4/unity/scenarios.json` **114 identical**.
- Build `HSD-Build/M10B/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10B\HSD-Practice.exe`), exit 0.
  The re-serialised `Scenes/Practice.unity` and `ProjectSettings/ProjectSettings.asset` were reverted; the config assets (new `ziplineGun` block)
  and `PathfinderS21.asset` (new slot + arbiter row) are committed. ignore-cr stat equals the plain stat (33 files, +1965 / −29); no CR in the
  committed .cs.
- Smoke `-batchmode -nographics -smoke 12`: exit 0. `1441 commands (12.01 s at 120 Hz) in 1039 frames; ... final pos (341.586, 146.165, 10) |v_h| 92.0
  u/s; demos 202/202 verdicts as expected (101 SUCCESS at shift 0, 101 failure cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22,
  M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16, M9-C 14/14, M10-A 14/14, M10-B 18/18); course lap 80.82 s (7/7 checkpoints, Reference
  (R5 calibration)); feedback snapshot ok (26 fields, 2116 bytes); 107572 commands in total`
- **Older trajectories identical**: a per-command hash (position, velocity, buttons, lurch, events) of every older demo at shift 0 and its failure
  shift (184 runs) and of the scripted M5 route in both configs equals main `fd04cba` (scratch harness, net8 build of the Unity csprojs). No older
  test or demo changed its verdict or trajectory; no map rope changed.

## 8. Gaps and open questions

1. **Raise time** 0.5 s [design]; R5 fired 1.0 s after the raise and never tested shorter.
2. **Wall / ceiling end point** 16 u out of the face [design]; R5 measured only floor / top impacts (and a wall rope's slope, not its end point).
3. **8000 u maximum** not reachable on the R5 field ([src] only).
4. **Grapple handoff speed**: R5 (1 hooked trial) restarted the ramp (397 → 252 → 502 @0.5 s); HSD keeps the existing map-rope handoff (entry speed,
   then max with the ramp), so the first ~0.4 s of the ride is faster than R5. Kept because the task asked for the existing handoff; one parameter
   would switch it.
5. **Steep end exit** 600·sin θ is a fit on one angle (52°); between 44.4° and 52° and for downhill steep rides it is [inf].
6. **Sloped jump-off along the 3-D rope** measured on one 42° rope going up; a downhill gun rope then jumps off with vz = 289.8 − 400·sin θ [inf].
   Map ropes keep their measured horizontal law (M6-A3 measured flat ropes only, so whether map ropes also jump along a slope is open).
7. **Wall-run / hang firing** uses the HSD M7-A states (Fun only); the S21 wall-run / wall-hang placement was not testable in R5.
8. **Refund** is reachable only through the 10-rope limit (HSD has no rope damage); the projectile is not simulated in flight (the target is fixed at the
   fire; the world is static).
9. The gun-rope cap source key is unknown (R5: measured 1000; not in the script).

## 9. Design values

Raise 0.5 s, aim timeout 20 s, eye 60, wall standoff 16, rope-line test (2 u end clearance), Fun charge 10 s, arbiter row (priority 20, aim guard 25 s),
the ZG yard geometry except the R5 distances (lane marks), HUD / preview colours.
