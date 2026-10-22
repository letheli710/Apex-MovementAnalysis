# M7-A in HSD-Unity: wall-run, ledge grab / hang, configurable double jump

- Branch `m7a/wallrun-hang-djump` of HSD-Unity, from main `199dde8` (M6-A/B/C merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M7-A-PLAN.md](../M7-A-PLAN.md). Playtest guide (Chinese): [../PLAYTEST-GUIDE-M7A.md](../PLAYTEST-GUIDE-M7A.md).
- **None of the three mechanics exists in Apex S21.** They are HSD designs, and every value below is **[design]**:
  - M6-A measured that R5 S21 has **no ledge hang** (A2-CLIMB.md; `ClimbAbility`: "No ledge hang exists [meas]").
  - Apex has the climb and the wall bounce (`JumpOutOfWallRun`), **no Titanfall-style wall-run**.
  - Apex has only **Octane's jump-pad double jump** (`pad.double_jump_delay` 0.1 s, not modelled). The double jump here is a general air jump, not a replica of it.

> **Acceptance status (two separate labels)**
> - **「数值通过」**: every rule, chain, guard and cap below is checked by automated tests, random fuzz and the headless smoke. The Reference config and every replay are byte-identical (§7–§8).
> - **「真人手感未验收」**: nobody has played it yet. That covers the wall-run speed and arc, the hang trigger window, the double-jump height, the jets / jump-button rule, the camera cues and every other value here. They stay design values until the user has played them.

Labels: **[meas] / [fit] / [src]** as in M6; **[design]** an HSD choice (a tunable parameter, not Apex data).

## 1. Audit (before the build)

| Area | What existed | Gap for M7-A | Decision |
|---|---|---|---|
| Wall-run | `WallRunAbility` in `FunAbilities.cs` (M5, Fun only, part of the all-or-nothing fun switch): airborne + forward + contact + 200 u/s along → low gravity, along-wall drive, jump off n̂·260 + vz 260, same wall 0.6 s. | No view rule against the climb (it only lost because the climb runs first), no steering off, no forward-release exit, the same-wall block expired in the air (one wall could be re-run), no cap on the jump-off, could not be switched on its own. | **Promoted** to `Traversal/WallRunAbility.cs` (same class name, fields `running` / `normal` kept for the camera and HUD) and reworked; moved out of the fun features into its own toggle group. |
| Climb / mantle / attached slide / wall bounce | `ClimbAbility` (M6-A, measured): climb on a faced wall (35° cone), mantle within 80 u, attached slide, bounce, superglide; `WallBounce` / `WallJumpAbility` (M3 bounce within 0.1 s of a contact); `IMovementWorld.ProbeLedge`. | No hang (R5 has none). Between the mantle reach (80) and the step zone (~98 u above the feet) the climb does not start at all (`TOO_LOW`), so a body at the apex beside a 140 ledge just slides down: the natural place for a hang. | **Hang = a new phase of `ClimbAbility`** (`ClimbPhase.Hang`), reusing its ledge probe, its Driving state, its arbiter row and its once-per-airborne rule; climbing up hands over to the **existing measured mantle**. Off (null) in Reference: the M6-A machine is untouched. |
| Input / jump consumption | Order: climb, zipline (each consumes its own jump press), fun abilities, landing slowdown, wall jump, slots (jets on jump), map fixtures. `ConsumeJump` hides the press from later abilities; the arbiter masks an airborne press while something drives (`jumpBlockedWhileDriving`) except for `handlesJump` traversals. | The double jump must see only a press nobody else used, and must come before the jets so the two can share the button by a rule. | Wall-run in the "first" list after the zipline; the **double jump is inserted after the wall bounce and before the first slot ability**; the jets read nothing new. |
| Arbiter | `SkillArbiter` + `SkillRules`: one driver, launch choice and clamp, timeouts, 900 / 1100 ceilings, boost cap. | Rows for the new abilities; the climb guard (4 s) is shorter than a hang. | Rows added only when a mechanic is on: `wall_run` (Effect, 3 s guard), `double_jump` (instant); the climb's Driving guard becomes 4 + 5 s when the hang is on (4 s otherwise). |
| M6-C course / fuzz / demos / feedback | Course, course fuzz (seeded streams), demo framework (Advance → Step, integrity tests), F9 / F10 feedback, camera layer, ability visuals. | No test area for walls to run, ledges in the hand window or a double-jump gap. | Reused as they are; three small test areas added after every older block; demos, fuzz episodes and feedback fields added without touching the M6 ones (§5–§6). |

Nothing of the motor core (`R5MotorV2`) changed. The two simulation files touched besides the new ones: `ClimbAbility` (the hang phase, all behind `hang != null && hang.enabled`) and `JetpackAbility` (a read-only `CanEngage` query).

## 2. Configs and toggles

- `MovementConfig.hsd` (`HsdMovementParams`) holds `wallRun`, `ledgeHang`, `doubleJump`, each with its own `enabled` flag.
  - **Reference**: all three off (`HsdMovementParams.Off()`). It stays the measured R5 behaviour.
  - **Fun**: all three on (`HsdMovementParams.Fun()`), for every loadout.
- In the game, **keys 7 / 8 / 9** switch the wall-run / hang / double jump for this session, also under Reference; **key 0** switches the jets rule (§3.3).
  - The body is rebuilt with position and velocity kept. The config object itself is never changed (`MovementConfig.WithMechanics` builds a copy).
  - A toggled session has its own best-time key (`… [WR on · hang off · 2J on]`). Without toggles the keys are unchanged.
  - A demo setup clears the toggles (`PracticeSession.ClearMechanicOverrides`), so every demo runs with its config's own mechanics.
- Config assets regenerated (`PresetAssets.CreateM5ConfigsBatch`): `fun.wallRun` moved to `hsd.wallRun`; new `hsd.ledgeHang`, `hsd.doubleJump`.

## 3. The three mechanics

### 3.1 Wall-run (`WallRunAbility`, HSD design, Titanfall-style)

| Phase | Rule |
|---|---|
| Start | Airborne, W held, a wall contact within 0.1 s, ≥ 200 u/s along the wall, not falling faster than 450 u/s, no other driver, not the blocked wall. **View rule**: outside the wall's 35° climb cone (inside it the climb owns the wall) and within 75° of the run direction. vz is clamped into [60, 150] (a small lift at the catch). |
| Run | Effect (not a driver). Gravity ×0.15; the along-wall speed is pulled toward 300·msc (345 u/s) at 400·msc u/s² with W held; an entry above that bleeds at 60 u/s² (the run never adds speed above max(entry, 345)); a 40 u/s push into the wall keeps the contact. |
| Jump off | Space: v_h = along + n̂·280, **capped at 480 u/s**; vz = 300; a jump (lurch window); the press is used up. |
| Exits | landing, the wall ended (no contact for 0.1 s), 1.6 s, < 120 u/s along, crouch press, **steering off** (view > 30° away from the wall beyond parallel, or a strafe key off the wall; +80 u/s off the wall), W released for 0.15 s, another driver (climb when the view turns into the wall, zipline mount, grapple pull, jets). The arbiter's 3 s Effect guard is the last exit. |
| Chains | Same wall (surface + normal) blocked **until the next landing**; any other wall at once (wall-run → jump → opposite wall). |

**Wall-run vs climb.** The view decides. Looking at the wall within the climb's 35° cone, a W-held air contact is the measured climb (or the mantle when the ledge is within 80 u). At a shallow angle it is the wall-run. Turning the view into the wall during a run hands over to the climb (`WALLRUN_END_DRIVER`, then `CLIMB_START` or `MANTLE_START`), once per airborne phase as in R5.

**Wall-run jump vs the measured wall bounce.** During a run, Space is the wall-run jump (the wall-run runs before the wall bounce and uses the press). Outside a run, a press within 0.1 s of a contact is the M3 bounce, exactly as before. Right after a run ends (crouch, steering off) the contact is still fresh, so the press is the bounce (tested).

**Speed stacking.** The run adds no speed above its run speed. The jump-off is capped at 480 u/s. The lurch after it only redirects (|v| kept, |Δv| ≤ 0.7 × the sprint cap). The 900 / 1100 ceilings apply on top. Fuzz maximum: 480.

### 3.2 Ledge grab / hang (`ClimbPhase.Hang`, HSD design; R5 has none)

| Phase | Rule |
|---|---|
| Grab | Only where a **climb would start** (airborne, W held, a fresh contact with the faced wall, not climbed since the landing), and only when the mantle (≤ 80 u) does not apply. Guards (anti-snap): vz ≤ 60 u/s (near the apex or falling; **a rising contact is the measured climb**); not falling faster than 400 u/s; the **impact speed** of this contact (the pre-clip \|v_h\| of its first command) ≤ 420 u/s; sliding along the wall ≤ 200 u/s; the ledge top 80–110 u above the feet (hand window), with room on top; not within 0.6 s of a let-go / jump-off. |
| Hang | Kinematic and Driving. The body settles in 0.12 s to 92 u below the ledge top, at rest. A / D shimmy along the face at 70 u/s, only while the ledge and the room on top continue. |
| Exits (always available) | **Space** facing the wall (within 90°, no S) → climb up through the **measured mantle** (T = 0.173 + 0.0055·rise; this mantle is not cancelled by a missing W). **S + Space**, or Space looking away → jump off: n̂·230 + the along-wall input × 75, vz 250 (a jump: lurch window). **Crouch** → let go (+30 u/s off the wall). **5 s guard** → let go. The ledge lost or the path blocked → let go. A launch, a newer driver (grapple, zipline mount) or the arbiter ends it like any climb state. After any exit: no grab or climb before the next landing. |

**Coexistence with the measured climb.** With the hang off (Reference), the climb machine is the M6-A one bit for bit. With it on, the hang only replaces a climb **start** under the guards above. A jump at a wall that meets it rising still climbs and mantles as measured: the failure case of demo H1 shows exactly that.

### 3.3 Configurable double jump (`DoubleJumpAbility`, HSD design)

| Item | Rule |
|---|---|
| Trigger | An airborne jump press that nothing used (traversals, wall-run, wall bounce run first), ≥ 0.1 s after the takeoff, an air jump left, nothing Driving (the arbiter masks the press then, and a driver that starts on the same command also blocks it). |
| Count | `maxAirJumps` 1 (configurable). |
| Height | vz = max(vz, √(2·g·45)) = 259.8 u/s: an upward speed is never lowered (pad compatibility), a fall is replaced. |
| Horizontal | Re-aimed halfway toward the input; **\|v_h\| never grows**. |
| Lurch window | **Counts as a jump** (opens the window, so a tap strafe can follow), like the wall bounce and the zipline jump-off. Switch: `opensLurchWindow`. |
| Resets | Landing (always); a wall-run start; a ledge grab; a zipline mount. **Not** the grapple (it is strong already) and **not** the climb (the measured R5 move). All switchable. |
| Pad | Allowed during the pad flight; the fast rise is kept (vz = max). Not Octane's pad double jump. |
| Zipline | The super jump keeps its 0.2 s window after the mount (the zipline uses the press first); later presses are the air jump. |

**The jump button with the Valkyrie jets** (`JetsJumpRule`, shown in the HUD; key 0 switches it):
- **AirJumpFirst** (default): an airborne press with an air jump left is the **air jump**. Holding jump on for **0.25 s** engages the jets from that same hold. With no air jump left, a press goes to the jets as before.
- **JetsFirst**: a press goes to the jets whenever they can engage (not active, fuel above the activation cost, the reactivation delay and the press gap run: `JetpackAbility.CanEngage`). The air jump is used only when they cannot.
- During the jets' thrust (Driving) an airborne press is masked by the arbiter, so the two never stack.

## 4. Test areas (map, design values)

Added after every M6-B block (`PracticeMap.m7BlockStart`), so every older block keeps its index and surface id. No ramp, rope, checkpoint or gate was added. Free ground was checked (`TestAreasAreAddedAfterEveryOtherBlockInFreeGround`).

| Area | Where | Geometry |
|---|---|---|
| S wall-run corridor | x 11580–11920, y 1500–2500 | Two parallel walls, inner faces x 11620 / 11880 (260 u apart), height 360. The west wall's north part (y 2100–2500) is 200 high: turn into it during a run to climb / mantle onto it. |
| T ledge set | x 8700–9500, faces at y 1250 (facing −y) | Tops 140 (a running jump meets it at the apex: hang), 165 (late hang / double jump), 240 (measured climb, or double jump + hang). |
| U double-jump gap | x 9700–10800, y 1000–1400 | Deck A (top 100) → 300 u gap → deck B (top 140). Computed: a sprint jump lands ~180 u out and a slide jump ~220 u (+16 u hull), short of 300. Demo D2: an air jump 0.40 s after the jump lands 342 u out on deck B. |

## 5. Demos (real input through Advance → Step; Fun config; verdicts read the recorded simulation)

| Id | Chain | Success (shift 0) | Failure variant (shift) |
|---|---|---|---|
| `m7_wallrun_chain` | wall-run → jump-off → wall-run on the opposite wall | west run → jump-off 444 u/s (cap 480) → east run 0.82 s later | jump −0.55 s: before the run, so the press is the air jump; no wall-run jump |
| `m7_wallrun_tapstrafe` | **slide** → slide jump → wall-run → jump-off → **tap strafe** | slide jump 350 → run → jump-off → D tap 0.10 s later: lurch, 27.3° | tap +0.6 s: lurch window closed |
| `m7_wallrun_mantle` | wall-run → turn into the low wall → **climb + mantle** | handover at y 2216 → climb + mantle onto the 200 top | turn −0.6 s: climb on the 360 high wall, top not reached |
| `m7_hang_climbup` | ledge grab → climb up (**mantle**) | grab at vz 18 (85 u below the top) → Space → on the 140 top | jump +0.25 s: met rising (vz 205): the measured climb, no hang |
| `m7_hang_jumpoff` | ledge grab → S+Space jump-off → air jump | jump-off 230 u/s off the wall, vz 250 → air jump (the grab gave it back) | S +0.3 s: Space facing the wall climbs up instead |
| `m7_djump_lurch` | double jump → **tap strafe** | A tap 0.10 s after the air jump: 48.3° | tap +0.6 s: window closed |
| `m7_djump_gap` | double jump across the 300 u gap | air jump 0.40 s after the jump → onto deck B | air jump +0.6 s: no air jump, into the gap |
| `m7_djump_grapple` | **grapple** → manual release → air jump | release → air jump 0.20 s later (the grapple neither spent nor refilled it) | press −0.45 s: during the pull, masked (`JUMP_BLOCKED_DRIVING`) |
| `m7_djump_zipline` | **zipline** jump-off → air jump | air jump 0.30 s after the jump-off, outside the super-jump window | press −0.25 s: inside the 0.2 s window: super jump |
| `m7_djump_jets` | Valkyrie: the jump button shared with the jets | one press: air jump, held 0.25 s → jets from the same hold | rest of the hold +0.5 s: released at 0.13 s, the jets needed the next press |
| `m7_bounce_djump` | measured **wall bounce** → air jump | bounce (W released before the contact: no run, no climb) → air jump 0.30 s later | bounce press +0.3 s: contact too old, the press was the air jump |

- Chains with each required move: slide (W2), wall bounce (D6), mantle (W3, H1), tap strafe (W2, D1), grapple (D3), zipline (D4).
- The double jump with the lurch (D1), the grapple (D3), the zipline exit (D4) and the jets conflict (D5).
- Every demo runs through the existing integrity tests: bit-identical to its recorded inputs through `SkillBody.Step` at uneven frame rates; success for seeds 1–3 with every criterion met; frame-rate independent; unchanged by visuals; its failure at its shift for the stated reason, checked independently in `EveryDemoFailsWithItsFailureShift`.
- One framework addition: `DemoAimKey.shifted` lets the timing shift move a view key (W3's turn). No existing demo uses it, so their inputs are unchanged.

## 6. Tests

| Suite | Result |
|---|---|
| EditMode | **742 / 742** on the commit (main had 607; +135) |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M7-A 22/22`) |

New EditMode cases:
- `R5MotorM7Tests` (R5Replay):
  - `WallRunTests`: Reference has none and the toggles add them, in the right order; a shallow approach runs and a faced wall climbs; the run never adds speed above max(entry, run speed); every exit (TIME, NO_WALL, DUCK, STEER_OFF, RELEASE, a strafe key off the wall, LAND); the jump-off cap, the lurch window, the opposite wall and the same-wall block; the block lifts on landing; after a run a contact press is the measured bounce.
  - `LedgeHangTests`: a near-apex grab, the settle, the climb up through the mantle; the guards (rising → climb, fast impact, fast fall, outside the hand window, no W, hang off); every exit (crouch, S+Space, looking away, the 5 s guard) and no regrab before landing; the shimmy stops where the ledge ends.
  - `DoubleJumpTests`: one air jump, the vz model, no horizontal gain, the landing reset; the count and the lurch switch; the wall-run refill vs the grapple; a pad rise never lowered; both jets rules; no air jump while something drives.
  - `M7FuzzTests`: every preset × 3 new seeds with the three on in the M5 test world, the M5 invariants every command (finite, ceilings, one driver, timeouts, hull outside walls), plus wall-run ⟂ climb, the air-jump count, the jump-off cap; everything idle and grounded 12 s after the input stops.
- `M7GameTests` (game): the toggles (also under Reference; the config never changes; a demo clears them; the jets rule switch); Reference bodies carry none of it; the test areas (after every older block, in free ground, every demo start free); the HUD lines; the feedback field only when on; the camera cues and intensity 0.
- 11 demos × the existing demo suites (success ×3 seeds, failure, recorded inputs ×2, frame rate, visuals) and their failure cases in `EveryDemoFailsWithItsFailureShift`.
- Course fuzz: in Fun each of the 4 loadouts gets 2 extra episodes per seed (12 seeds) from their **own** random generator, starting at the M7-A areas or with a jittered M7-A demo; the earlier episodes keep their inputs (the demo pool of those episodes leaves the M7-A demos out). New `RandomPlayWithTheM7TogglesInReferenceHasNoAbnormalStates` (Pathfinder-Octane and Valk-Horizon, 12 seeds × (3 + 3) episodes). New checks every command: the wall-run never beside a climb / hang or a zipline ride; the wall-run jump ≤ 480; an air jump adds no horizontal speed beyond the command's air acceleration (a launch or a grapple pull starting on the same command is exempt); the air-jump count; a hang never past its 5 s guard; the wall-run ended after the idle seconds.

Course fuzz results (25 s episodes + 10 idle s; every row: 0 exit failures, 0 traversal timeouts, 0 tunnelling candidates, 0 frozen traversals, 0 unresolved collisions):

| Config / loadout | M7-A episodes | wall-runs (jumps, max v_h) | hangs (climb-ups / jump-offs / let-gos, longest) | air jumps (jets holds) | other guard timeouts |
|---|---|---|---|---|---|
| Fun / Pathfinder-Octane | 24 | 17 (8, 444) | 3 (1 / 1 / 1, 1.38 s) | 1156 | pad 9, grapple 2 |
| Fun / Valk-Horizon | 24 | 14 (7, 444) | 4 (1 / 0 / 3, 0.67 s) | 677 (4) | pad 5, grapple 1 |
| Fun / Revenant-Wraith | 24 | 24 (13, 480) | 8 (5 / 2 / 1, 0.69 s) | 1149 | pounce 14, pad 1 |
| Fun / Ash route | 24 | 16 (10, 444) | 6 (3 / 1 / 2, 1.47 s) | 821 (3) | pad 3, grapple 1 |
| Reference + toggles / Pathfinder-Octane | 36 | 23 (14, 476) | 6 (4 / 1 / 1, 0.33 s) | 1383 | 0 |
| Reference + toggles / Valk-Horizon | 36 | 9 (3, 444) | 4 (4 / 0 / 0, 0.65 s) | 1116 (3) | 0 |
| Reference (4 loadouts) | – | 0 | 0 | 0 | as in M6-B |

The other guard timeouts are the M5 abilities' own guards, as reported in M6-C (§4.1 there). The Reference rows are identical to main for 3 of the 4 loadouts; for Ash see §10.

Problems the tests found and fixed during the build:
- An air jump on the command where the flight toggle starts a driver (the arbiter's mask runs before it). The double jump now also refuses when any driver is active.
- A fast wall impact could grab one command later, because the clipped velocity is slow. The guard now uses the impact speed of the whole contact.
- Between the mantle reach and the step zone the climb returns early (`TOO_LOW`), so the hang must be tried before that return. The climb path is unchanged.

Existing tests changed, each keeping its intent:
- `MovementConfigTests.ConfigAssetsEqualTheFactory`: compares `hsd.wallRun / ledgeHang / doubleJump` instead of `fun.wallRun` (moved).
- `MovementConfigTests.ReferenceTurnsOnTheMeasuredModelOptions…`: also asserts the three are off in Reference and on in Fun.
- `MovementConfigTests.ApplyKeepsTheLoadoutAndAddsTheFunTraits`: the Fun row count is now 2 fun + 2 M7-A + 2 traversal (the wall-run row moved, `double_jump` is new); asserts the climb guard 9 s in Fun and 4 s in Reference.
- `FunAbilityTests` body helper: adds the wall-run from its new group (the test itself is unchanged and passes with the reworked rules).
- `M6BGameTests.M6BStationsAreAddedAfterEveryOtherBlock`: the M6-B blocks are the 5 before `m7BlockStart` (no longer the last 5).
- `M6BGameTests.JetsMeetTheZiplinePerConfig(1, true)`: in Fun the first airborne press is now the air jump (rule AirJumpFirst), so the test switches the double jump off for its session. It is about the jets meeting the rope.
- `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: cases for the 11 demos. `DemoProbeAndVisualCodeHaveNoSimulationWrites`: also scans `MovementDemosM7.cs` and `HsdHud.cs`.
- `M6CourseTests`: the fuzz as above. A hang is excluded from the "frozen traversal" check: it holds still by design, with its own guard checked.
- PlayMode smoke test: also requires `M7-A 22/22`.

## 7. Regression (default replay motor)

`R5Replay/` replay code is untouched; the default motor never builds any M7-A ability.

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set, unchanged |
| 38 M4 trials (`m4_replay_check.py <new> --base m4_replay`, `-scenarios <abs>/m4/unity/scenarios.json`) | `m5/unity/m4_replay` | 114 identical, 0 different, 0 missing |

Outputs in a scratch folder outside the repositories.

Game-side Reference checks against main (`199dde8`, same harness):
- every one of the 48 older demo verdicts and reasons is identical (smoke lines diffed);
- the course lap is 80.82 s in every config × loadout, Fun included (the autopilot lap presses no air jump);
- the Reference course fuzz is identical for 3 of 4 loadouts (Ash: §10).

## 8. Build and smoke

- `HSD-Build/M7A/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>/HSD-Build/M7A/HSD-Practice.exe`): 91 MB, 0 errors, 0 warnings.
- The scene and ProjectSettings that the build re-serialised were reverted (`git checkout --`).
- Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 70/70 verdicts as expected (35 SUCCESS at shift 0, 35 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration));
feedback snapshot ok (26 fields, 2110 bytes); 41166 commands in total
```

- **The route part is unchanged**: 1441 commands, final position (341.586, 146.165, 10), |v_h| 92.0.
  - "events seen" is 18 instead of 17: the route runs in Fun from 3 s to 10 s, and its scripted hops at 3.47 s and 7.21 s are now air jumps (`AIR_JUMP` is the new name).
  - The checkpoint reset at 9 s rebuilds the body, so the end state is untouched.
- **Every older demo line is identical** to M6-B (all 48 lines diffed).
- **The course lap is unchanged** at 80.82 s.
- The feedback byte count varies with the timestamp; it was 2111 / 2112 in M6-C / M6-B. A Reference snapshot gets no M7-A field.

## 9. Camera and visuals (fps-camera-design method; visual layer only)

- **Brief.**
  - Wall-run: the body leans off the wall, speed along a surface. Kept: the M5 roll (10°) and the start kick (1.5). New: a sustained FOV +2 while running. The jump-off uses the wall-jump cues (roll kick away, lift, FOV).
  - Hang: the hands catch the edge (a dip of 1.5), the head hangs below the edge (eye −6 while hanging). Climbing up uses the mantle cues; the jump-off lifts (1.5).
  - Air jump: a lighter takeoff, lift 1.5 + FOV kick 1.5, no pitch. Distinct from the ground jump.
- **Rules.** Every new term sits in the existing intensity groups (height / FOV / roll) and scales to 0 at intensity 0 (`M7CameraCuesFireAndScaleToZero`). The camera reads only.
- **Visuals.** An expanding pale-blue puff ring under the feet at an air jump (0.4 s). A yellow bar on the gripped edge while hanging.
- **HUD.** The toggles line (`[7] wall-run ON · [8] hang ON · [9] double jump ON`, `*` = switched this session). `air jump 1/1` with the jets rule when the loadout has jets. `HANG  Space climb up · S+Space jump off · Ctrl let go · A/D shimmy (x.x s)`. The stance label shows WALL-RUN / HANG. The F3 diagnostic shows the M7-A counts. The feedback snapshot gets an `m7a` entry when a mechanic is on.
- **Proof.** The existing visual / camera decoupling tests ran unchanged, now including the 11 M7-A demos (`VisualsDoNotChangeADemo`) and the Fun wall-run frames (`FeedbackAtMaxIntensityLeavesTheSimulationBitIdentical`).

## 10. Open gaps

- **Every value is a design value**, and no person has played any of it (「真人手感未验收」). The list is in §11.
- Wall-run:
  - no wall-run on curved or sloped walls: only walls with |n.z| < 0.5 count, and the course ramps are not walls;
  - no camera roll toward the run direction (only off the wall);
  - the run direction follows the velocity, not the view: turning the view along the wall does not reverse a run.
- Hang:
  - only where a climb would start (W held toward the wall). No grab from a fall with W released, and no grab after a climb's jump-up (the climb's own air phase keeps probing only the mantle);
  - no hang on a ledge without room on top (the climb up would have nowhere to go);
  - the shimmy does not turn corners;
  - the impact-speed guard holds for the whole contact, so a fast impact never grabs until the contact ends.
- Double jump:
  - an air jump on the same command as a pad / pounce launch is spent while the launch replaces its velocity (fuzz edge case, harmless);
  - it is on for every loadout in Fun. A per-legend assignment ("not on all characters") is not built: today it is a config / session switch;
  - inside the jets' post effect (0.45 g for up to 3 s) an air jump floats more.
- The new geometry is reachable by long aim rays. The Ash breach aim (2953 u range) from the course's north lane can hit the M7-A ledge set, so the Reference Ash course-fuzz counts moved slightly (bounces 142 → 141, lurches 5766 → 5753, grapple pulls 115 → 114). Removing the M7-A blocks gives the main numbers exactly again (checked). Every other Reference fuzz row is identical to main.
- The smoke route's "events seen" went from 17 to 18: the route runs in Fun from 3 s to 10 s, and two of its scripted hops are now air jumps (`AIR_JUMP`). The command count, final position and speed are unchanged, because the route resets to the checkpoint at 9 s.

## 11. Design-value list (all [design], tunable in `HsdMovementParams` / the config assets)

| Mechanic | Parameter | Value |
|---|---|---|
| Wall-run | minStartSpeed / minRunSpeed | 200 / 120 u/s along the wall |
| | runSpeed / runAccel / overSpeedDecel | 300·msc (345) / 400·msc u/s² / 60 u/s² |
| | gravityScale / entry vz window / maxEntryFall | ×0.15 / [60, 150] / 450 u/s |
| | maxDuration / contactGrace / stick | 1.6 s / 0.1 s / 40 u/s |
| | climbCone / maxViewToRun / steerOffAngle / steerOffPush / releaseGrace | 35° / 75° / 30° / 80 u/s / 0.15 s |
| | jumpNormal / jumpUp / jumpAlongKeep / jumpMaxSpeed | 280 / 300 / 1.0 / 480 u/s |
| | same wall | blocked until landing (else 0.6 s) |
| | arbiter | prio 45, Effect guard 3 s |
| Hang | minRise / maxRise / hangRise / settleTime | 80 / 110 / 92 u / 0.12 s |
| | maxEntryVz / maxFallSpeed / maxApproachSpeed (impact) / maxAlongSpeed | 60 / 400 / 420 / 200 u/s |
| | regrabCooldown / maxHangTime / shimmySpeed | 0.6 s / 5 s / 70 u/s |
| | climbUpCone / jumpOffOut / jumpOffUp / jumpOffSide / dropPush | 90° / 230 / 250 / 75 / 30 u/s |
| | climb arbiter guard with the hang on | 4 + 5 = 9 s |
| Double jump | maxAirJumps / height / redirect / minSinceTakeoff | 1 / 45 u (259.8 u/s) / 0.5 / 0.1 s |
| | opensLurchWindow | yes |
| | resets | landing, wall-run, hang, zipline (not grapple, not climb) |
| | jetsRule / holdForJets | AirJumpFirst / 0.25 s |
| | arbiter | prio 25, instant |
| Camera | wallRunFov / hangGrabDip / hangEyeDrop / hangJumpOffLift / airJumpLift / airJumpKick | 2° / 1.5 / 6 / 1.5 / 1.5 u / 1.5° |
| Map | corridor width / wall heights / ledge tops / gap | 260 u / 360 & 200 / 140, 165, 240 / 300 u (decks 100 → 140) |
