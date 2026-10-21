# M6-A1 / A2 / A3 in HSD-Unity: lurch, climb / mantle / superglide, ziplines

Branch `m6/advanced-movement` of HSD-Unity: commits `27898da` (simulation core, R5Replay) and `3bd822e` (game layer). These sit on top
of A4 `d5da139`. Unity 6000.6.5f1, SOURCE units.

Labels:
- **[meas] / [fit]**: the lead-verified models `m6/a1_lurch`, `m6/a2_climb` (including the round-2b addendum, §9) and `m6/a3_zip`
  (including GRAPPLE-ZIP).
- **[src]**: source audit.
- **[design]**: an HSD choice, either inside a measured bracket or with no measurement.

## 1. Architecture

- **Motor seam.** `CommandModifiers.kinematic`: on that command the ability sets the post-state (position, velocity, grounded) and the
  motor runs no move of its own. The world still sweeps the move.
  - A kinematic move never ends below the floor. If it would, it lands there.
  - With identity modifiers the motor is unchanged, bit for bit (regression in §6).
- **Traversal abilities.** `ClimbAbility` and `ZiplineAbility` (`R5Replay/Runtime/Traversal/`).
  - Both are base-layer `ISkillAbility`s. They run before every slot ability and before the fun abilities, so they see the jump press first.
  - Their parameters live in `AdvancedMovementParams` (`MovementConfig.advanced`).
  - `MovementConfig.CreateBody` builds the game body; `PracticeSession` uses it.
- **Arbiter (SKILL-RULES).**
  - Both traversal states are `Driving`, interruptible and not exclusive. Climb has priority 75 and a 4 s guard, zipline 65 and a 40 s guard.
  - The newest driver wins. So a mount or a climb ends the grapple pull, jets and flight, and a later grapple pull or flight ends the
    traversal (tested).
  - A launch ends them. The speed ceiling (900 / 1100) still applies after every command.
  - New trait `handlesJump`: `jumpBlockedWhileDriving` does not mask the jump of a state that uses it itself (bounce, superglide, jump-off).
  - New interface `ISecondPressAbility`: the grapple's release press is not refused for an empty charge.
- **Guaranteed exits.**
  - Climb / slide: detach at tc 1.000 s.
  - Mantle: the traversal end, and an abort if the world moves the body more than 4 u off its path.
  - Zipline: the rope end, and a detach if the body is pushed more than 8 u off the rope.
  - Behind all of these, the arbiter timeouts.
  - Random play (40 s × 3 seeds × 2 configs × 3 loadouts, in a world with ledges, a wall and three ropes): no traversal timeout, the hull is
    never in a solid or below the floor, the ceiling holds.
- **Configs.**
  - Reference: advanced on, native superglide, air mount off, lurch cutoff 1100.
  - Fun: the same, with air mount on.
  - The default replay motor and the M4 replay grapple have every new option off.

## 2. A1 lurch (motor)

The M3 per-press rule was already general in the motor: every new bit in 0x618 lurches while airborne, the wish is a unit vector from
the command's yaw, AirAccelerate runs first, and `SkillBody` clamps each press at 0.7 × the current sprint cap. A1 confirmed this
unchanged, so the work was making the anchor and the masks explicit.

| Item | Unity | Label |
|---|---|---|
| Press gate | every press edge, no budget, no cooldown, W included (tap strafe) | meas |
| λ(t) | 0.7·clamp01((0.5 − t)/0.3), t from the latest jump command | meas |
| Anchor | ground / slide jump, the wall jump (M5) and the climb bounce, the native mantle jump / superglide, the zipline super jump | meas (bounce), design (mantle jump, super jump: native jumps) |
| Zipline jump-off as anchor | yes | **design** (`jumpOffIsLurchAnchor`) |
| Clamp | per press, 0.7 × sprint cap | meas |
| Suppression | `lurchSuppressed`: set only by the FSM superglide's boost, cleared on landing or at the next traversal | src + meas |
| Cutoff | `lurchCutoffSpeed` 1100 (reference / fun; default 0): inert under the 900 ceiling | src |
| Input layer | `TapKey`: every key tap and every wheel notch is its own one-command press with a released command after it, so n notches give n edges two commands apart; a held key drops queued notches | A1 §10.2 |
| Wheel bind | the mouse wheel (both directions) gives W taps; X = use | design |

**Tests** (`R5MotorM6Tests.M6LurchTests`, `M6GameTests`):

| Test | Result | A1 measured |
|---|---|---|
| rr_n6 | 209.300 clamped, then 140.26 unclamped with the speed kept | 140.258 |
| rrr_n6 | third press 40.77 | 40.770 |
| lr_n12 | 253.20 → 143.13, two clamps | same |
| shift R-B-L | 253.45 / 141.60 / 78.27, three clamps | same |
| diag_fr | \|D\| 163.149, heading −31.91° | same |
| diag_br | 170.10, −44.89° | same |
| Tap strafe 360 °/s | **−80.99°** at constant speed | −81.02° |
| Tap strafe 180 °/s | **−40.49°** | −40.52° |
| W held while turning | < 6° | — |
| Window | λ 0.7 at 0.1 s, the ramp at 0.3 s, none at 0.5 s | — |
| Cutoff / suppression | press masked; cleared on landing | — |
| Climb bounce | re-anchors: a press 3 commands later has t = 0.025, λ 0.7 | λ 0.70 |
| Wheel tap strafe | one notch per 60 Hz frame while turning: every edge in the window lurched and the flight follows the view | — |

## 3. A2 climb / mantle / superglide (`ClimbAbility`)

The state model is A2-CLIMB §6 including round 2b. The trigger needs all of these:
- airborne;
- W held (forward axis > 0);
- a fresh wall contact, from the last command;
- the view within **35° [design]** of the wall's inward normal (the R5 cone was never measured);
- no climb since the last landing.

Walking into a face never climbs.

| Mechanism | Unity | Label |
|---|---|---|
| Contact command | v_h → 0, vz += 9.6 − g·dt/2 | meas |
| Climb | vz = min(vz + 490·dt, 1.735·(z_ref + 180.4 − z)); a contact above vz 100 first falls at g | fit; n = 1 unknown |
| Anchor | z_ref = takeoff z (floor and takeoff were the same in A2) | design inside the data |
| End | first command with pre z ≥ z_ref + 147.06 → jump-up: vz += 208 − 584·dt; outward 68.1 − 500·dt with W, 68.5 without; lateral speed kept | meas |
| Side key | lateral accel 113·(1 − v/102.6) u/s² (reproduces −113 at the start, 51 u/s and 18 u by the end) | fit to the round-2b summary |
| W released → slide | dvz/dt = −320 − 727·tc rising, +72 − 806·tc falling; step at vz = 0; the jump-up still fires at the end height | fit |
| Detach | any attached state at tc 1.000 s, +69.97 outward; back on the slide → 0.060 s after the press (−310 u/s² extra meanwhile) | meas |
| Jump on climb / slide | M3 wall bounce n̂·182.78 + d̂·75.08 (no stick → n̂; back + jump the same); U = 4 from the climb, 2.6 from the slide; a jump command | meas |
| Mantle trigger | ProbeLedge toward the wall: top − z ≤ 80, checked every command (the R5 0–3 command lag is not modelled) | fit |
| ProbeLedge calibration | maxHeight 80; inset −9.6 (exit 6.4 u past the face); reach 24 | meas / meas / design: the air drift after the jump-up |
| Traversal | T = 0.1728 + 0.0055·rise | fit |
| Mantle path | rise done by 0.75 T; forward from 0.6 T (inside the 18 u step zone, so the hull clears the edge) | design (A2 measured one rock's path) |
| Mantle exit | 299 (sprintspeed × msc) along the input direction with W held, else at rest; grounded on the top; not a landing for the anti-multi-jump clock (a jump on top is full height, A2) | meas |
| Cancel | the forward axis drops below 1 (W released, or back with W held) at ≤ **0.5 T**; back out for −0.007 + 1.053·elapsed, then snap to the start and drop with v = 0 | design inside (0.395, 0.685]; fit |
| Native superglide (reference) | a jump press ends the traversal on the next command; with ≤ 0.1025 s left it jumps with V 289.82 (post vz = V − 1.5·g·dt) at 299, or at **460** (SlideBoostPeak) with crouch held on the exit command; an earlier press cuts to the ledge height, airborne at 299, no jump; no lurch mask | meas (window derived from H232, generalised as remaining time: design) |
| SDK FSM variant (`superglide = SdkFsm`) | press latched, first traversal frame dropped; exit at the end: boost 388.7 / 367.4 (last 0.1333 s) and the lurch masked until landing, else 299 / 289.8 | src + meas (camera gate not modelled) |
| Hang | none | meas |

**Choice.** Native is the reference behaviour, as the plan asked: it is what the S21 code does with the FSM off, time-window based and frame-rate
independent. The FSM costs one enum and reuses the M3 `MantleBoost` primitive.

**Tests** (`R5MotorM6Tests.A2Climb`): the A2 schedule (sprint, jump 100 u before the face, W held). Test tops are the R5 rock tops
H + 5.92 u.

| H | Unity outcome | Climb (s) | Traversal (s) | R5 (A2) |
|---|---|---|---|---|
| 60 | lands on top | — | — | lands on top |
| 90 | instant mantle | — | 0.425 | mantle, 0.414 |
| 120 | instant mantle | — | 0.592 | mantle, 0.578 |
| 150 | climb + mantle | 0.200 | 0.617 | 0.206 / 0.604 |
| 180 | climb + mantle | 0.392 | 0.617 | 0.399 / 0.612 |
| 232 | climb + jump-up + air mantle | 0.850 (jump-up dvz 202.8 ± 1, out −64.3 ± 0.6; mantle 0.05 s after the jump-up, rise 76 ± 3.5) | 0.608 | 0.849 / 0.590 |
| 300 / 400 | climb + jump-up + fall, no second climb | 0.850 | — | the same |

- **Further checks.** Mantle exit at 299, 6.4 u past the face. Climb at 60 / 144 Hz: 0.85 ± 0.04 s.
- **W release (tc 0.233).** Every slide command matches the ramp to 1e-6. Detach at tc 1.000 ± dt/2, −69.97.
- **Slide actions.** Slide jump → dv_out 257.865, U 2.6. Back → detach 0.060 s later. Release 2 commands before the end → the jump-up still
  fires, out −68.5.
- **Side drift.** 50.7 u/s and 17.6 u (A2: 51 / 18). The jump-up keeps it.
- **Cancel (H180, release 0.233 s in).** Back-out matches the fit within one command. Snap to the start, v = 0, falls to the floor.
- **Back with W held** cancels. **A release at 0.71 T** completes at rest.
- **W + D exit** = (211.43, −211.43).
- **Native.** Mantle jump 299 / 280.45 (post), superglide 460.000, early press → MANTLE_CUT.
- **FSM.** 388.7 / 367.42 (src √(2·750·90); measured 367.414), a strafe press 0.2 s later does not lurch; failed → 299 / 289.8.
- **Climb bounce.** −257.865 with no stick. With W: O − I = 107.70, minus the command's air accel.
- **Every height class ends grounded**, with no arbiter timeout.

**Camera** (fps-camera-design method; every value is [design]):
- climb: grab dip 1.2 u, eye 4 u lower while attached;
- jump-up: lift 1.5;
- mantle start: pitch kick 1.2° down, toward the ledge;
- mantle end: settle dip 1.5;
- cancel: pitch −0.8;
- superglide: FOV kick 5 and lift 1.5 (its own cue, not the pad launch's);
- mantle jump: lift 1.5;
- zip mount: dip 2 and FOV 1;
- zip jump-off: lift 1.5;
- super jump: lift 3 and FOV 3;
- zip exit: FOV 2.

All of them use the existing groups. Tested: the cues fire; at intensity 0 there are no kicks; the simulation is identical with the camera on or off; the M6
demos are unchanged by the visuals at max.

## 4. A3 ziplines (`ZiplineAbility`)

| Mechanism | Unity | Label |
|---|---|---|
| Mount | IN_USE (0x20) press edge on the ground; P = origin + 72; Q = the rope point of minimum angle to the view within 130 u (analytic per segment); cone **34°** | fit; design inside 27.0–40.7 |
| Vertical rope Find | point at origin.z + 80.1 | meas (one geometry) |
| Auto-attach | none | meas |
| Air mount | off (reference), on (fun) | design (R5 dedi refused it) |
| Mount command | +22, no horizontal move, v 0 (grapple handoff: no move) | meas |
| Hang / blend | 80 u below the rope (dedi value); the measured b(k) table read by time, linear to 1 from k 45 to 60 | meas |
| Ride | 8.333 on the first ride command, +600 u/s² through the 0.5 s mount state (k ≤ 60), then +400 to 600; no slope term; s += v·dt with the same command's speed | meas / fit |
| Ride direction | flat / sloped: the end the view faces; with momentum (air, grapple): along v; vertical: up | design |
| View | pulled to the rope during the mount state (90 % in 22 commands); mouse ignored; free from command 61; vertical rope free at once. It moves the aim, so it is applied by the game as a control rule, not by the camera layer | meas |
| Auto-detach | after the ride step, if (L − s) − v·dt < 90: exit at the current position with d̂_end·clamp(v, 600, 600) | meas + src, residual 0 |
| Vertical top | origin = top − 80.16; v = rope·min(v, 1500) + 400 along the view yaw | meas |
| Jump-off | ĥ_rope·min(v, 400) + ẑ·289.828; keys and view ignored that command; no move on it | fit, residual 0 (125 exits) |
| Vertical-rope jump-off | the view yaw is the horizontal | design |
| Crouch-off | ĥ·min(v, 400), vz 0 | fit |
| Super Jump | after a ground mount and a jump-off, a new jump press within **0.2 s** of the mount: vz += √(2·750·56) − 1.5·g·dt, v_xy kept, a jump command (lurch anchor); once | meas; design inside (0.067, 0.525) s |
| Budget | 3 mounts, +1 per 3 s off the rope, reset on landing / mantle | src |
| Grapple → zipline | ropes catch the hook ray (cylinder radius 10, design). While pulling on a rope, the body mounts once the origin is within 136 u of the hook point [meas, one geometry; native trigger unknown]; the grapple ends on that command; v_entry = max(0, v·d̂) + 400·dt; v = max(v_entry, rest curve) during the mount state. With no budget the pull still ends there [design] (otherwise the body orbits a rope that is no surface) | meas / fit |
| Grapple manual release | a second grapple press ends the pull on the press command, velocity kept exactly; during the hook flight / wind-up it cancels. On in the game; off in the replay grapple | meas |

**Tests** (`R5MotorM6ZiplineTests.A3Zipline`):
- **Find.** The sphere-edge point and the exact ray point; out of range.
- **Mount.** +22 and the blend to the hang line. No auto-attach. Air refused (reference). Cone and range refusals.
- **Ride profile.** 8.333, 303.33 at k 60, +400 from k 61, the cap at 1.25 s.
- **Auto-detach.** At 90–95 u from the end with (600, 0, 0), then plain air.
- **Uphill.** The same profile; exit 600·d̂.
- **Jump-off.** At k 1 / 24 / 60 / 120 / 190: min(v, 400) and 289.828 exact, no move, lurch anchor.
- **Crouch-off.** min(v, 400), vz 0.
- **Super jump.** In the window it adds exactly √(2·750·56) − 1.5·g·dt, only once; 0.3 s later it does nothing.
- **Vertical top.** z = 900 − 80.16, vz = v, 400 along a view yaw of 60°.
- **View lock.** Through ride command 60, free from 61.
- **Budget.** 3, then refused, reset on landing.
- **Air mount (fun).** Keeps the momentum.
- **Grapple → zipline.** Handoff with v_entry exact and max(entry, rest) after 30 commands.
- **Manual release.** Velocity exact and no new use. It is not refused at 0 charges. It is off in the replay grapple.
- **Interplay.** A use mount ends a grapple pull. Flight ends on a mount.
- **Random play.** Covered in §1.

## 5. Practice map (M6 area) and chain demos

**Map.** Everything is north of y 1450, so no M5 station, checkpoint or demo moved.

| Station | What it holds |
|---|---|
| F lurch / tap-strafe field | x 0–1800, five posts |
| G wall-bounce corridor | x 2400–3600, 400 wide |
| H ledge wall | five blocks with tops 60 / 120 / 180 / 232 / 300; faces at y 1800, approached going +y |
| I ziplines | flat (5900→7900, z 130); uphill (8100→9900, z 130→530) onto a deck (top 440); vertical at (10600, 1700) up to 700, beside a tower (top 640); a grapple-only rope at z 420 |

The ropes are drawn with posts and 250 u marks. Map tests:
- every station-H ledge gives its height class from real input (60 land / 120 mantle / 180 climb + mantle / 232 climb + jump-up + mantle /
  300 climb + jump-up);
- every rope mounts from its start, rides to its end and lands (uphill onto the deck, vertical onto the tower);
- the high rope is out of use range.

**Chain demos (Movement Demo panel, F6).** These are scripted keys and view through `PracticeSession.Advance` → `SkillBody.Step`. The
existing M5.5 integrity tests run on them too:
- bit-identical to the recorded inputs through raw `SkillBody.Step`, at uneven frame rates;
- succeed for seeds 1–3;
- fail at the failure shift for the expected reason;
- frame-rate independent;
- unchanged by the visuals and camera.

| Demo | Success (shift 0) | Failure variant |
|---|---|---|
| `m6_bounce_tapstrafe` | slide jump 350 → bounce at 1.90 s → 9 W-tap lurches (window anchored at the bounce); the flight follows the view (−2.6° behind, 93° turned) | bounce jump +0.3 s: contact too old, no bounce |
| `m6_climb_superglide` | climb 0.35 s → mantle → superglide 460 u/s (jump 0.054 s before the end, crouch next) | jump −0.3 s: mantle cut, no superglide |
| `m6_zip_superjump` | mount → jump-off at 0.15 s → super jump at 0.183 s (vz 552, apex +214 u) → A tap lurch 67° | second jump +0.3 s: outside the 0.2 s window |
| `m6_grapple_release` | manual release at 248 u/s (v_h unchanged on the command) → A air steer +16° → landing slide at 257 u/s | release +1.5 s: the pull already ended by GAP |

## 6. Verification

- **Tests.** EditMode **424 / 424**: the 314 from before plus 110 new. PlayMode **1 / 1**: the smoke inside the editor, all 20 demo verdicts.
  - One old test changed on purpose: `ApplyKeepsTheLoadoutAndAddsTheFunTraits` now expects the 2 traversal rows.
  - The A4 equivalence tests (frozen M5.5 BoxWorld) still pass on the M5.5 route, the 30 s runs and the M5.5 demos: the M6 features do not
    change any M5.5 run.
- **Default replay motor, byte for byte.**

| Set | Baseline | Result |
|---|---|---|
| M2 + M1 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1, M1 first guess | baseline | 111 identical |
| M3 | `m3/unity` | 90 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set, unchanged |
| 38 M4 trials | `m4_replay_check.py --base m4_replay` with `-scenarios` | 114 identical |

  The new grapple key is left out of the parameter report while it is off.
- **Build.** `HSD-Build/M6/HSD-Practice.exe`: 91 MB, 0 errors, 0 warnings. Only the two config assets changed content. The re-serialised
  scene and ProjectSettings were reverted.
- **Smoke.** `-batchmode -nographics -smoke 12` exit 0:
  `final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 20/20 verdicts as expected (10 SUCCESS at shift 0, 10 failure cases FAIL;
  M5.5 12/12, M6 8/8)`.
  - The route line is identical to M5.5.
  - Every M5.5 demo line carries the M5.5 values: 24.0°, 350.0, 48.3°, 534, 127 / −32.7°, 0.358 s.

## 7. Open gaps

- **Unmeasured cones and rules.**
  - The climb / mantle face cone (35°) is unmeasured.
  - The mantle-reach lag is not modelled.
  - The "contact above vz 100 falls first" rule rests on n = 1.
  - z_ref (floor vs takeoff) was not separable in A2.
- **Mantle path and superglide.**
  - The mantle path shape is design; the R5 "snap back 15–20 u" at a native jump is not reproduced (the exit is at the current path point).
  - The native superglide window is derived from H232 only; other heights use the same remaining time.
  - The FSM's 1.5° camera gate is not modelled.
- **Ziplines.**
  - Downhill ropes are untested in R5; the same profile is used.
  - Ride direction is a design choice.
  - The vertical jump-off direction is unmeasured.
  - The Super Jump window was chosen inside (8, 63) commands.
  - The grapple handoff trigger is a single-geometry distance.
  - Ropes can be grappled anywhere (cylinder radius 10).
  - The air mount in fun is design.
- **Not modelled.** The A2 9.46 u/s first-exit dip at H90 / H120; the client-only hang offset; mantle-from-ground.
- **Camera.** Every cue is a design value until playtested. The zipline view pull is a measured control rule applied by the game: it moves the aim
  by design.
