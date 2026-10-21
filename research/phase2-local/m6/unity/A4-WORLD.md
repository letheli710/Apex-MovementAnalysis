# M6-A4: movement world foundation (HSD-Unity)

Branch `m6/advanced-movement` of HSD-Unity, commit `d5da139` (on main `dc649e9`). Unity 6000.6.5f1. SOURCE units throughout.
Evidence tags as in [../M6-AUDIT.md](../M6-AUDIT.md): **[src]** pinned s21-r5sdk source, **[design]** HSD choice with no R5
measurement. Nothing in A4 was measured in R5.

## 1. Interface

`IMovementWorld` (`Assets/HSD/R5Replay/Runtime/World/IMovementWorld.cs`) replaces the M5 `BoxWorld` behind `SkillBody`. It extends
`IGrappleSurface` (grapple raycast).

| Member | Use |
|---|---|
| `BeforeStep(motor)` / `AfterStep(motor, t)` / `ResetBody(motor)` | body hooks of `SkillBody.Step` / `Reset` |
| `SupportHeight(feet)`, `Blocked(feet)`, `FloorZ` | the M5 queries, unchanged meaning |
| `ProbeGround(feet)` → `GroundHit` | support height, up normal, surface id, distance below the feet, walkable |
| `ProbeWall(feet, dir, maxDist)` → `WallHit` | hull swept horizontally: distance, contact origin, outward normal, surface |
| `CeilingClearance(feet, hullHeight, maxUp)` | free height above the head (+∞ if open) |
| `ProbeLedge(feet, towardWall, LedgeProbeParams)` → `LedgeHit` | wall distance and normal, ledge top / height above the feet / depth, mantle target, stand / crouch fit, headroom, or a reason (NO_WALL, TOO_LOW, TOO_HIGH, TARGET_BLOCKED, BLOCKED_ABOVE) |
| `ClosestRail(point, maxDist)` → `RailHit` | closest point on a rail polyline, distance, tangent, path length, attachable |
| `ResolveTeleport(from, to)` | teleport clipping (unchanged rule) |

`MovementWorld` implements it. `SurfaceContact` gained a `surface` id. The motor gained three plain state fields:
`groundNormal`, `groundSurface` (set by the world each command) and `teleported` (set by the teleport so the world does not sweep a
placement).

## 2. Primitives and collision

- **Solids** (`ConvexSolid`): intersections of half-spaces, with the axis-aligned bounds always among the planes.
  - axis-aligned boxes (`Add(min, max)`, the M5 case);
  - ramps / wedges: bounds cut by a top plane with any upward normal (`AddRamp(..., RampRise)` for axis ramps, `ConvexSolid.Ramp` for any normal);
  - yaw-rotated boxes (`AddOrientedBox`).
- **Rails** (`Rail`): a polyline with an attach radius. Geometry only; riding is A3.
- **Hull**: 32 × 32 × 72 standing, 48 crouched **[design]**, step-up 18 (unchanged). The collision hull is crouched when the motor's
  hull is (reference config: `hullCrouched`; plain motor: `ducked`). It stays crouched while standing up would hit a ceiling.
- **Hull space**: every plane is expanded by the hull (Minkowski sum). Walkable tops are lowered by the step-up for blocking, so a top
  at most 18 u above the feet is a step. For boxes this is exactly the M5 rule.
  - Exact for boxes, axis ramps and rotated boxes.
  - A ramp sloping diagonally is slightly too big near its two slanted edges (no bevel planes there; conservative).
- **Walkable**: normal z ≥ 0.7 **[src]** (`slope_launch_math.h` SLOPE_LAUNCH_MIN_NORMAL_Z). Steeper surfaces never support the body;
  they act as walls. Flat: normal z ≥ 0.999 **[src]** (SLOPE_LAUNCH_FLAT_NORMAL_Z).
- **BeforeStep**: floor = highest walkable top under the footprint at most 18 u above the feet. A hull on a slope rests on its higher
  footprint corner, as a Source box hull does.
- **AfterStep**: the move from the pre-step origin to the motor's origin is swept against the expanded solids.
  - Method: Cyrus–Beck per solid, earliest entry first, up to 8 bumps.
  - The end point is projected onto the entered plane, and the velocity loses its into-plane part (R5 wall impact, SWING §5).
  - What the entered plane means:
    - side, or a slope too steep to stand on → wall contact (the abilities' contact);
    - downward face → ceiling (`lastCeiling`; v_z → ≤ 0; never a wall contact, because `WallBounce` needs a horizontal normal);
    - walkable top entered from above → feet put on the top.
  - A body that starts inside a solid is pushed out along the least-penetration plane, sides first (the M5 rule).
  - **No tunnelling at any speed**, because the move is swept. Teleports are placements, not sweeps.

## 3. Slope option in the motor

- `R5MotorV2Params.slopeMovement` (default **off**, so the replay motor is unchanged).
- `slideSlopeGravityScale` = 1 **[design]**.
- Both are listed in the parameter report only when the option is on.
- The reference and fun configs turn it on. It changes nothing on flat ground.

On a walkable slope:
- **Velocity**: the ground velocity stays flat. The source comment says so ("Apex keeps grounded velocity flat and only slides the
  position along the slope") **[src]**.
- **Uphill**: the command's horizontal move d = v_h·dt is clipped against the plane (Source TryPlayerMove), so there is less
  horizontal progress uphill **[design detail]**.
- **Downhill**: d is not clipped, and the position follows the plane.
- **Staying on the ground**: a grounded body stays on a slope when the support drops by up to 18 u (StayOnGround) **[design]**. This
  applies only when the old or the new support is a slope. Flat drops (curbs, ledges) still fall as in M5.
- **Slide**: a slide adds g·scale·n.z·n_h·dt to v_h before the slide decel/decay. This is the along-plane gravity, horizontal part
  **[design]**; the R5 slope slide was never measured.
- **Not modelled**: `sv_slope_launch` (community option, off by default).

## 4. Tests

- Before: 262 EditMode + 1 PlayMode (M5.5).
- Now: **314 / 314 EditMode** and **1 / 1 PlayMode** pass in Unity (batch runs).
- The new tests are 52: 32 in `MovementWorldTests` and 20 in `WorldEquivalenceTests`.

**`MovementWorldTests`** (`R5Replay/Tests/Editor/MovementWorldTests.cs`):
- **Ground probe**: on a box, a ramp (corner support, normal) and a steep ramp (no support); the step limit.
- **Rotated boxes**: rotated-box footprint and `TopAt`.
- **Walking on slopes** (option on): walks up and down a 20° ramp, grounded on every command, with flat velocity. On the ramp the body
  stays on the plane within 1e-6 u. The uphill move is clipped; the downhill move is v·dt exactly.
- **Option off on a slope**: on a 40° ramp the option-off motor leaves the ground on more than 20 commands; with the option on, never.
- **Option on, flat world**: on the M5 test world (3 seeds × 20 s of random input), option on = option off bit for bit.
- **Slope slide**: faster than on the flat downhill (30°), slower uphill.
- **Steep slope**: a 60° slope is a wall. The body does not climb it, and an airborne body meets it with the slope normal.
- **Ceiling**: a ceiling stops a jump with the head exactly at it (feet z 28.000) at 60 / 120 / 144 / 240 Hz.
- **Crouched hull**: fits under a 60 u gap and stays crouched there; `CeilingClearance`.
- **No tunnelling**: through a 2 u wall or a 2 u ceiling, at 900 / 1100 u/s and at 20 000 u/s, at 60 / 120 / 144 Hz. The body stops
  exactly at the face.
- **Corners and seams**:
  - an inside corner stops both axes exactly;
  - the body slides along a wall made of two boxes past the seam, gaining y on every command (M5's least-penetration rule could snag there);
  - rotated-box face contact normal and raycast; ramp raycast normal.
- **Probes**:
  - `ProbeWall`: distance, normal, out of reach, a step is not a wall;
  - `ProbeLedge`: target, height, depth (capped / full), thin ledge, TOO_LOW, TOO_HIGH, crouch-only headroom, TARGET_BLOCKED, BLOCKED_ABOVE.
- **Rails**: closest point, segment, path length, attach radius.
- **Random play**: 40 s of random play in a world with every primitive (4 seeds, reference config, Pathfinder-Octane slots). The hull
  is free after every command, never below the floor, never stuck.
- **Determinism**: slope walking is deterministic and within 6 u (x) / 3 u (z) at 60 / 144 / 240 Hz vs 120 Hz.
- **Default report**: the default motor report has no slope keys.

**`WorldEquivalenceTests`** (`Game/Tests/Editor/WorldEquivalenceTests.cs`) compare against a frozen copy of the M5.5 BoxWorld. The
collision code is unchanged; only surface ids were added for reporting.
- **Support and blocked queries**: `SupportHeight` / `Blocked` are equal on 200 000 points around the map blocks, including exact face
  and top coordinates.
- **Smoke route**: the build's `-smoke 12` route (60 / 144 / 90 Hz frames, config / loadout switches, checkpoint reset) is bit-identical
  on every frame, using the full simulation state dump of the M5.5 decoupling tests. It ends at
  "1441 commands final pos (341.586, 146.165, 10) |v_h| 92.0", the M5.5 acceptance numbers.
- **Scripted runs**: 30 s for every config × loadout (6), bit-identical on every command.
- **Movement Demos**: every demo at shift 0 and at its failure shift (12) is bit-identical, with the same verdicts.

## 5. Regression (default replay motor byte-identical)

Outputs are kept outside the repositories. Every run used the same commit.

| Set | Baseline | Identical | Different | Missing |
|---|---|---|---|---|
| M2 + M1 trials, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 | 0 | 0 |
| M2 + M1 trials, M1 first guess | `m2/unity/m1_first_guess` | 111 | 0 | 0 |
| M3 trials, R5MotorV2 | `m3/unity` | 90 | 0 | 0 |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 | 76 | 0 (known M3 change set, unchanged) |
| 38 M4 trials with `-scenarios m4/unity/scenarios.json` | `m5/unity/m4_replay` (`m4_replay_check.py --base m4_replay`) | 114 | 0 | 0 |


## 6. Practice map

- **Unchanged.** It is built on `MovementWorld`, from boxes only.
- **Why no slope / ceiling / ledge area yet**:
  - The map renderer draws only `MapBlock` cubes, so ramps would need visual support.
  - A2 / A3 will lay out their own stations around the mechanics.
- Until then, the world features are covered by the tests above.

## 7. Build / smoke

- **Build**: `HSD.Build.BuildWindows -buildPath <workspace>/HSD-Build/M6/HSD-Practice.exe` succeeded with 0 errors and 0 warnings
  (91 MB). The output is outside the repositories. The scene / ProjectSettings files the build re-serialized were reverted (no
  content change).
- **Headless smoke** (`-batchmode -nographics -smoke 12`): exit code 0, identical to M5.5 (ACCEPTANCE-M55 §3):
  `[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; ... final pos (341.586, 146.165, 10) |v_h| 92.0 u/s;
  demos 12/12 verdicts as expected (6 SUCCESS at shift 0, 6 failure cases FAIL)`. Every demo line carries the same measured values
  as M5.5: 24.0°, 350.0 u/s, 48.3°, 534 u/s, 127 u/s / −32.7°, 0.358 s.

## 8. Open gaps for A2 / A3

- **A2 climb / mantle / wall-slide behaviour**:
  - `ProbeLedge` gives the target, height, depth and fit, but its parameters are design values (max height 160, reach 24, inset 1).
    They must be calibrated from the M3 climb heights.
  - No climb / hang / mantle state exists yet.
  - Forced crouch under low ceilings is collision-only. The motor still uses the standing speed cap when the duck key is released
    under a slab.
  - Walking diagonally into a wall: the M2 instant redirect (v = s·ŵ every command) is clipped every command, so the body only creeps
    along the wall. This was the same with BoxWorld. With `groundVectorRedirect` (reference config) it is different. A2's wall
    behaviour should decide this.
- **A3 zipline**: rails are data and a closest-point query only. Needed:
  - riding (speed along the tangent, gravity along the slope, ends);
  - jump-off and re-attach rules;
  - a hull-vs-rail clearance check (rails are not solids);
  - rail visuals.
- **Ceilings and abilities**: a ceiling contact is not reported to the abilities' `SurfaceContact`, so the grapple's
  release-on-contact does not fire on a ceiling. Decide in A2 / A3.
- **Slope physics**: unmeasured in R5 (uphill clip, StayOnGround limit, slide gravity scale, crouched hull 48). Slope launch is not
  modelled.
- **Ramp collision**: ramps with a diagonal slope direction have no edge bevels (slightly conservative collision near their slanted
  edges).
