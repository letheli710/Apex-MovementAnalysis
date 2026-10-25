# M8-B in HSD-Unity: bunny hop, lurch chains, superglide and wall chains

- Branch `m8b/advanced` of HSD-Unity (commit `2e8a39e`), from main `11e887f` (M8-A merged). Unity 6000.6.5f1, SOURCE units.
- Plan: [../M8-PLAN.md](../M8-PLAN.md) items 4–7. Inputs: track D [../d_techniques/TECHNIQUES.md](../d_techniques/TECHNIQUES.md), track R [../r_sg/SG.md](../r_sg/SG.md), [../r_lurch/LURCH.md](../r_lurch/LURCH.md), [../r_slope/SLOPE.md](../r_slope/SLOPE.md). Playtest guide (Chinese): [../PLAYTEST-GUIDE-M8B.md](../PLAYTEST-GUIDE-M8B.md).

> **Acceptance status (two separate labels)**
> - **「数值通过」**: every technique below has a real-input demo with a success condition and a failure variant, unit tests and fuzz checks; every R5 replay is byte-identical; every older demo verdict and the course lap (80.82 s) are unchanged (§7–§8).
> - **「真人手感未验收」**: nobody has played it. The hop rhythm, the superglide timing, the tap rates of the lurch demos, the chain difficulty and every [design] value are open until the user has played them.

Labels: **[meas]** our R5 measurement (M2–M6, M8 track R), **[fit]**, **[src]**, **[model]** a prediction of a measured model that R5 did not record, **[design]** an HSD choice. Evidence classes for techniques (track D): **verified** / **community** / **unverified**.

## 1. Audit (before the build)

| Item | What existed | Gap found | Decision |
|---|---|---|---|
| 4 Bunny hop | M2: jump-command friction skipped, anti-multi-jump 0.3 within 0.15 s; M3: ground jump keeps min(v, 299), resumed-slide jump keeps the speed | Never tested as chains; no demo | Works from the existing rules (§2). Tests, 3 demos, guide only. No code change |
| 5 Lurch | M3 / M6-A1 lurch on every move-key edge, window anchored on jump commands; tap strafe verified at 180 / 360°/s | Chains (reversal, snake, spin), 720°/s, anchors after other moves, held-key cases untested | Natural from the existing lurch (§3); track R measured the follow-ups during this build and Unity matches them. Tests, 4 demos |
| 6 Superglide | M6-A2 native SG 460 at H232 only; exit along the mantle direction; pose speed 299 from any approach; a jump window of 0.1025 s | Other heights / approaches / directions; a 172.5 u/s superglide from rest; the view-only face cone | Parameterised and corrected to the track R grid (§4) |
| 6 Wall chains | M7-A wall-run, hang, bounce, double jump; M8-A arbitration | Long chains never built; a flush wall of two blocks let a run restart after its 1.6 s limit | Coplanar fix (§5); chain yard X and 3 long-chain demos |
| 7 Field / validation | M6-C course, demo framework, course fuzz, M8-A checks | No M8-B areas, demos or checks | Chain yard X (§6), 14 demos, new fuzz episodes and checks (§7) |

Replay safety: every change is on game bodies. The replay motor has no climb / wall-run, `slideSlopeNeedsDuck` is `[NonSerialized]` and set only by `MovementConfigs.Reference()`, so no report changes.

## 2. Item 4: bunny hop (no code change)

| Case | Result (Reference = Fun unless noted) | Basis |
|---|---|---|
| Hop on the first grounded command, W + sprint, start 150 / 200 / 299 / 350 / 450 / 600 | every takeoff = min(v0, 299.0); never above 299 | jump command skips friction [meas M2]; ground jump keeps min(v, 299) [meas M3] |
| Late by k commands, W + sprint held at 299 | 299 kept (the sprint cap is the hop speed) | ground model [meas] |
| Late by k commands, no input | −1250·dt·k per hop exactly | deceleration 1250, not ·msc [meas] |
| Press on the command that lands (airborne) | Reference: dropped, the chain breaks (no jump buffer). Fun: it is the air jump | arbitration [design]; **gap / human judgement** |
| Hop height | frac 0.3 on the first grounded command (16.8 u, ~0.42 s per hop); full height again 0.75 s after a landing | [meas M2] |
| Slide hop (crouch held), 350 / 450 / 600 | every slide jump keeps the speed (resumed slide: no floor, no refund); late jumps pay the slide friction | [meas M3] |
| Air strafe between slide hops (wish kept ⟂ v) | |v|² grows at most (500·dt)² per command: 350 → 378.6 in 10 s, < 400 | AirAccelerate [meas M2]; 900 cap on top |
| Slide jump → standing landing → hop → ducked landing → slide jump | 350 → 299 (capped) → slide resumed → 299 kept | rules above |

No infinite gain: a ground hop is capped at 299; a slide hop only keeps its speed; the only growth is the measured air acceleration (slow, below the 900 ceiling). No unintended loss: a hop on the first grounded command loses nothing.

## 3. Item 5: lurch, LS / RAS, air direction change (no code change)

Mechanism [meas, A1 / M3]: every new move-key bit in the air lurches toward the keys' wish: λ = 0.7·clamp01((0.5 − t)/0.3), t from the latest jump command, |Δv| ≤ 0.7 × sprint cap (209.3). Every chain below is that rule; no per-trick code.

| Check | Unity | R5 (track R r_lurch unless noted) |
|---|---|---|
| Reverse chain W → W+D → D → S+D → S, 0.05 / 0.083 / 0.1 s spacing, sprint jump | 157 / 128–133 / 108–115° (by the first press offset), speed ×0.95–1.0 | 156.4 / 125.9 / 104.6°, ×0.98–1.0 [meas]; **no speed-keeping 180° reversal in R5** |
| Tap strafe 720°/s (15 W edges, 0.25 s) | 166.8° (view 180°), speed ×1.000 | −161.2° (view ~176°) [meas] |
| Tap strafe 1440°/s | heading 26° behind the view after one turn | ~30° behind [meas] |
| Turn only, no taps | < 1° | 0.0° [meas] |
| A held, then W pressed | diagonal lurch toward W+A | diagonal, equal-weight 45° wish [meas]; R5's 11.6 u/s residual on that command is not modelled (gap) |
| A held, then D pressed | no lurch (the keys cancel) | no lurch [meas] |
| Walk off a 232 ledge, D 0.017–0.4 s later | no lurch | no lurch [meas] |
| Clamp at a 350 slide-jump entry | 209.30 | 209.30 [meas] |
| Walk jump, D → D+S → S at 0.05 s, camera fixed | 162°, 98 % speed | [model]; community "OG Ras only out of a walk": the model shows why (from 299 the same chain keeps 72 %) |
| Key-only snake A / D every 0.1 s | swings of 25–60° each way, speed falls to ~50 % (the clamp) | [model] |
| Key-only spin D, S, A, W every 0.05 s | 450–515° of turn, speed falls to 25–40 % | [model] |
| A lurch never adds speed (random) | holds (200 random flights × 3 seeds; fuzz) | rule |

Turning after other moves (the window anchors on jump commands): wall bounce (M3 [meas], demo `m6_bounce_tapstrafe`, test `RunThenCrouchThenJumpIs…`), wall-run jump (M7-A [design], `m7_wallrun_tapstrafe`), zipline jump-off (M6-A [meas], `m8b_chain_zip`), pad launch (`SkillRules.launchOpensLurchWindow`, `pad_lurch`), superglide jump (native [meas], `m8b_sg_tapstrafe`; the SDK FSM variant masks it [src]), double jump (Fun [design], `m7_djump_lurch`). **A grapple release opens no window** (not a jump): in Reference a turn after a release is plain air strafe; in Fun an air jump after it reopens the window (`m8b_grapple_lurch`).

## 4. Item 6a: superglide (code changes in `ClimbAbility`)

Track R measured the native SG at H90 / 120 / 150 / 180 / 232 (102 superglides) during this build; the lead forwarded the results and Unity now follows them.

| Rule | Before (M6-A) | Now (Reference) | Basis |
|---|---|---|---|
| Exit speed | 460 at H232 | 460 at every height H90–H232 (tested) | [meas] |
| Jump window (time left) | 0.1025 s | unchanged; `nativeJumpWindowPerRise` / `RiseRef` plug-in (0 = constant) | R5: SG ≤ 0.085 s always, 0.086–0.12 s mixed, > 0.12 s cut [meas]; 0.1025 is inside the mixed band |
| Exit direction | along the mantle (wall normal) | `SuperglideExit.InputWithW`: along the move input (view-relative); the early cut too | 30° approach → 30° (15/15); view 45° + W+D → normal (14/15) [meas] |
| Exit speed source | pose 299 from any approach | `nativeExitSpeedFromApproach`: min(299, highest |v_h| since the last ground contact) | walk approach → 199.5, no SG (12/15) [meas] |
| Slide boost on the exit | from any speed (W released + crouch → 172.5 from rest) | only from ≥ 200 (`superglideNeedsSlideSpeed`, the motor's slide start) | slide start rule [meas M2]; **defect fixed** |
| Face cone | view within 35° | view **or** move input within 35° (`faceConeAlsoWish`) | R5 mantled with the view 45° off and W+D held [meas] |
| Fun | as Reference | `SuperglideExit.Input` [design]: a side key alone keeps 460 (lateral SG) | R5 lateral SG with only a side key: not measured |

Unity at the measured heights (sprint, press 0.05 s before the end, crouch next): 460.000 at H90 / 120 / 150 / 180 / 232. Traversal times: Unity's mantle starts when the ledge enters the 80 u reach, so the rise is ~79 u above H90; R5 T0 is 0.581–0.602 at H120–H232 but **0.418 s at H90**; Unity 0.531 s at H90 (rise 65) and 0.604–0.610 s at H120–H232 (gap: the R5 mantle at a low ledge starts with a smaller rise; the window and the exit still match).

Not modelled (gaps): the walk-approach 402.009 exits (3/15, unexplained in R5); the slide-jump approach gives no SG in R5 (0/15, slide boost re-arm [inf]) but does in Unity; the 328.98 (1.1 × 299) jump-only exit after a face contact. (Both explained later by the native +30 u/s jump term: `rea-native/n11/N11-OPEN-ITEMS.md`; Unity proposal J-1.)

## 5. Item 6b: wall chains and transitions

**Defect fixed (`WallRunAbility.sameWallCoplanar`, [design]):** the same-wall block compared the surface id only. A run along a flush wall made of two blocks (the corridor S west wall: the 360 part to y 2100, the 200 part after) crossed onto the second block and, at its 1.6 s limit, **started again there** (and the start refilled the air jump). Now a wall on the same plane (same normal, |n·p − plane| ≤ 2 u) counts as the same wall. Found by the zipline chain; covered by `AFlushWallOfSeveralBlocksIsOneWallForTheSameWallBlock` (the old rule as an option reproduces the restart) and a per-command fuzz check (0 restarts).

Transitions checked: run → crouch → the measured bounce (fresh contact) → lurch at λ 0.7 (test); run → jump-off → air jump (demo); run → view into a wall → climb → mantle (demo; too early: climb on the 360 part, no ledge, falls off); hang / climb / mantle exits under random play (fuzz: 0 exit failures, 0 frozen traversals). **Not reachable:** zipline → super jump → wall-run (the super jump leaves at < 100 u/s, the wall-run needs 200 along the wall [design]; test `TheZiplineSuperJumpIsTooSlowToStartAWallRun`); the chain uses the ordinary jump-off (400).

High speed: no tunnelling through an 8 u wall or a 4 u slab at 900 / 1100 u/s with 1/120, 1/60 and 1/30 s commands (test); the course fuzz counts tunnelling candidates every command (0). Speed inheritance through the chains: slope slide 404 → 540, slide jump keeps (370–429), lurch keeps |v| (clamped lurches cost speed: 460 → 387 with a 90° wish), wall-run 305–447 along, wall-run jump ≤ 480 (444), bounce 345 → 458 (M3 bounce adds n̂·182.78), superglide 460 → landing slide 460, rope 600 → jump-off 400. Camera: the existing cue layer reacts to these events (the demo suites' visual-decoupling tests ran unchanged over the M8-B demos).

## 6. Item 7: chain yard X (`PracticeMapM8B.cs`)

Between the M5 finish deck (station E, top 200) and the M7-A wall-run corridor S, appended after every older block, ramp and rope (indices and surface ids unchanged); the floor lane of the M7-A corridor demos (x ≈ 11720, y 1150 → 1500) stays clear; the scripted smoke / equivalence routes never reach x > 8200.

| Item | Geometry [design] |
|---|---|
| X1 slope | ramp off the deck's north edge, x 11640–11800, y 400–1000, 200 → 0 (18.4°, walkable both ways) |
| X2 anchor | hanging block x 11660–11760, y 1080–1160, z 260–320 (grapple range from the deck) |
| X3 rope | `m8b-yard`, x 11450, y 450 → 1900, z 130: past the corridor's west wall (outer face x 11580), 50 u east of the M6 vertical-rope tower |

## 7. Demos (real input through Advance → Step; verdicts read the recorded simulation)

| Id | Config | Success (shift 0) | Failure (shift) | Evidence |
|---|---|---|---|---|
| `m8b_bhop` | Ref | 5 hops on the first grounded command, 299.0 every hop, never above | −1 command: 3 presses on the landing command dropped (no buffer), chain broken | verified |
| `m8b_slidehop` | Ref | slide jump 350 → 4 slide hops at 350.3 | +0.25 s: friction, 350 → 233 | verified |
| `m8b_hop_chain` | Ref | slide jump 350 → hop 299 (capped) → landing slide → slide jump 299 | crouch +0.25 s: landed standing | verified |
| `m8b_ts_720` | Ref | 15 lurches, 166° at 299 | +0.5 s: window closed, 5° | verified (R5 −161°) |
| `m8b_ras_reverse` | Ref | walk jump, D / D+S / S: 162° keeping 98 % | +0.5 s: no lurch | model (R5 max 156° for its chain) |
| `m8b_snake` | Ref | 2 reversals, +49° / −45°, 299 kept | +0.5 s: straight | model |
| `m8b_grapple_lurch` | Fun | release → air jump → A tap: lurch +67° | air jump +0.3 s (after the tap): no window, no lurch | rule verified, air jump design |
| `m8b_sg_tapstrafe` | Ref | SG 460 → A tap 0.1 s later, λ 0.7, +27° | +0.5 s: window closed | verified (SG), lurch rule verified |
| `m8b_sg_slide` | Ref | SG 460 → landing slide 460 | second crouch +0.35 s: standing landing | verified mechanism |
| `m8b_sg_angle` | Ref | 30° approach: SG 460 along the view | −0.2 s: mantle cut | verified (track R 15/15) |
| `m8b_sg_lateral` | Fun | W → A in the second half, SG 460 along A | crouch +1 command: 299 mantle jump along A | design |
| `m8b_chain_slope` | Fun | slope slide 404 → 540 → slide jump → lurch → wall-run → jump-off 444 → air jump | A tap +0.42 s: window closed, no wall contact, no run | design |
| `m8b_chain_grapple` | Fun | grapple → landing slide → slide jump → lurch → wall-run → crouch off → bounce 458 → 10 tap-strafe lurches | bounce +0.3 s: contact too old | design (bounce measured) |
| `m8b_chain_zip` | Fun | rope → jump-off 400 → D lurch → wall-run → turn at y 2152 → climb → mantle onto the 200 wall | turn −0.6 s: the 360 part, climb without a ledge, falls off | design |

Every demo runs through the existing integrity suites (success for seeds 1–3 with every criterion met, failure at its shift for the stated reason, bit-identical to its recorded inputs through `SkillBody.Step` at uneven frame rates, frame-rate independent, unchanged by visuals).

## 8. Tests, fuzz, regression, build

| Suite | Result |
|---|---|
| EditMode | **1038 / 1038** (main 848; +190) |
| PlayMode | 1 / 1 (the smoke in the game loop, now also requiring `M8-B 28/28`; frame limit 60000 → 120000) |

New EditMode cases:
- `R5MotorM8BTests` (R5Replay): `BunnyHopTests` (start speeds 150–600 × both configs, late hops, the landing-command press, hop height, slide hops 350–600, the air-strafe bound, the slide jump ↔ hop ↔ landing-slide chain), `LurchM8BTests` (reverse chains vs track R, 720 / 1440°/s, held + new key and opposing keys, walk-off, the 350-entry clamp, grapple release / air jump anchors, a lurch never adds speed), `SuperglideM8BTests` (460 at H90–H232, the time-left classes, the angled exits, the walk approach, no boost from rest, Fun lateral, the window plug-in, SG → landing slide + native lurch), `WallChainM8BTests` (the coplanar fix with the old rule reproducing the restart, run → crouch → bounce → window, super jump too slow for a run), `HighSpeedM8BTests` (no tunnelling at 900 / 1100 u/s with 1/120–1/30 s commands), `SlopeM8BTests` (Reference vs the R5 fit, duck released → flat law), `M8BFuzzTests` (2 configs × 3 presets × 2 seeds, 40 s).
- `M8BGameTests` (game): the yard appended last in free ground, the M7-A approach lane clear, the rope placement, every M8-B demo start free; the per-config superglide / slope / wall-run rules; the demo coverage of items 4–6.
- 14 demos × the existing demo suites and their failure cases in `EveryDemoFailsWithItsFailureShift`.

Course fuzz (25 s episodes + 10 idle s, 12 seeds): 2 extra M8-B episodes per seed in **both** configs from their own generator (spawns in the chain yard, the hop / lurch fields, the ledge wall, or a jittered M8-B demo); the older pools leave the M8-B demos out, so the older episodes' inputs are unchanged. New checks every command: a ground hop or a lurch never adds more than the air acceleration (quiet commands: no launch, driver, kinematic move or other event), no wall-run starts on a wall plane already run since the landing. Every row: 0 exit failures, 0 tunnelling candidates, 0 frozen traversals, 0 unresolved collisions, ledger excess 0, 0 wall-run restarts.

| Config / loadout | episodes (M8-B extra) | ground hops checked (max v_h) | lurches checked | superglides | max v_h |
|---|---|---|---|---|---|
| Reference / Pathfinder-Octane | 84 (24) | 1991 (421, stim) | 5500 | 6 | 813 |
| Reference / Valk-Horizon | 84 (24) | 1700 (313) | 4452 | 2 | 629 |
| Reference / Revenant-Wraith | 84 (24) | 2013 (412) | 5582 | 4 | 676 |
| Reference / Ash route | 84 (24) | 2016 (299) | 5096 | 7 | 600 |
| Fun / Pathfinder-Octane | 132 (24) | 1387 (421) | 5395 | 5 | 833 |
| Fun / Valk-Horizon | 132 (24) | 853 (299) | 3285 | 3 | 810 |
| Fun / Revenant-Wraith | 132 (24) | 1362 (414) | 5705 | 1 | 813 |
| Fun / Ash route | 132 (24) | 973 (304) | 3380 | 2 | 641 |
| Reference + M7 toggles / Pathfinder-Octane, Valk-Horizon | 72 each (0) | 1013 / 856 | 4199 / 3499 | 2 / 0 | 813 / 626 |

Skill fuzz (`M8BFuzzTests`, a test world with 90 / 150 / 232 ledges, a flush double wall, a corridor, a rope and a ramp): 12 runs, 34–83 ground hops and 256–385 lurches checked per run, 0 failures.

Existing tests changed (each keeps its intent):
- `M7GameTests.TestAreasAreAddedAfterEveryOtherBlockInFreeGround`: the M7-A blocks are the ones before `m8bBlockStart` (no longer the last).
- `M8GameTests.SlopeFieldIsRampsOnlyAfterEveryOlderRampInFreeGround`: the M8-A ramps are the ones before `m8bRampStart`; the rope count excludes `m8b-`.
- `M6CourseTests.CourseLiesInTheSouthStrip…` and `M6GameTests.EveryMapRopeMountsFromItsStart`: the station-rope count excludes the `m8b-` yard rope (it starts 50 u north of the finish deck, where the test's 60 u run-up would stand inside the deck; it is ridden by `m8b_chain_zip`).
- `M6CourseTests` fuzz: M8-B episodes and checks (above); the older demo pool excludes `m8b_`.
- `MovementDemoTests`: 14 failure cases; the simulation-write scan includes `MovementDemosM8B.cs`.
- `PracticeGameTests.ConfigAssetsEqualTheFactory`: also compares the climb's superglide fields (assets regenerated with `PresetAssets.CreateM5ConfigsBatch`).
- PlayMode smoke test: also requires `M8-B 28/28`; frame limit 120000.

Regression (default replay motor; outputs in a scratch folder outside the repositories):

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`) | `m5/unity/m4_replay` | 114 identical, 0 different, 0 missing |

Game-side checks against main: every one of the 82 older demo verdict lines (success and failure case) is identical (headless harness diff of main vs the branch, after every runtime change including the superglide, face-cone, slope-duck and wall-run fixes); the course lap is 80.817 s in every config × loadout.

Build: `HSD-Build/M8B/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M8B\HSD-Practice.exe`), Build Finished: Success. The re-serialised `ProjectSettings/ProjectSettings.asset` was reverted (`git checkout --`).

Headless `-batchmode -nographics -smoke 12`, exit 0:

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 110/110 verdicts as expected (55 SUCCESS at shift 0, 55 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28); course lap 80.82 s (7/7 checkpoints,
Reference (R5 calibration)); feedback snapshot ok (26 fields, 2108 bytes); 56668 commands in total
```

The route part is unchanged (1441 commands, (341.586, 146.165, 10), 92.0, 18 events). The feedback byte count varies with the timestamp and the nearest-station name (the M8-B station joins the list).

## 9. Technique table (evidence classes)

| Technique | HSD mechanism | Status in Unity | Evidence |
|---|---|---|---|
| Bunny hop | jump friction 0, ground jump min(v, 299) | works, demo | verified |
| Slide hop | resumed slide keeps speed | works, demo | verified |
| Tap strafe 90 / 180 / 360°/s | W edges + view turn | works (M5.5 / M6 demos) | verified (A1) |
| Tap strafe 720 / 1440°/s | same | works, demo 720 | verified (track R) |
| Momentum shift / reverse chain | key edges | works; ≤ ~157° from sprint | verified (track R) |
| OG Ras (walk, key-only reversal) | key edges | 162° at 98 % from a walk | community name; model prediction |
| Yuki / Pito / Neo strafes | – | not built (no usable definition) | unverified |
| Snake / spin (keys only) | key edges | work, cost speed (clamp) | model |
| Lurchless air strafe | AirAccelerate only | works (held key before the jump: no lurch) | verified (A1) |
| Held key + new press | diagonal wish | works; opposing keys: none | verified (track R) |
| Wall bounce → lurch / TS | bounce anchors the window | works (demos) | verified (A1) |
| Superglide basic | native mantle jump + slide boost | 460 at H90–H232 | verified (track R) |
| Angled SG (30°, W+D at 45°) | exit along the input | works, demo | verified (track R) |
| Lateral SG (side key only) | Fun `SuperglideExit.Input` | Fun only | design (R5 unmeasured) |
| Backward SG | Fun: S held → 460 backward | Fun only | community; design |
| SG → TS / lurch | SG jump anchors the window | works, demo | verified mechanism |
| SG → landing slide | crouch held at the landing | works, demo | verified mechanism |
| Walk / slide-jump approach SG | approach speed rule | walk: no SG (matches); slide jump: SG (R5 none) | verified / gap |
| Glide bounce, mantle jump chain, no-ma bounce | – | not built | community |
| Zipline super jump | M6-A | works (M6 demos); too slow for a wall-run | verified |
| Wall-run chains, hang, double jump | M7-A | 3 long-chain demos | design |

## 10. Open gaps and parameters for human judgement

- No jump buffer: a hop press one command early is dropped (Reference) or becomes the air jump (Fun). A landing buffer would be a new input rule: user's call.
- The 11.6 u/s residual of a held key + new press (R5) is not modelled; R5's walk-approach 402 exits and the 1.1 × 299 jump-only exit were later explained by the native +30 u/s jump term (N11); the slide-jump approach SG is not blocked in Unity (R5 0/15, cause inferred).
- Unity's mantle at a 90 u ledge takes 0.531 s; R5 0.418 s (the R5 mantle starts with a smaller rise). Window and exit match.
- Uphill slope slides, slope edges and slope slide jumps are unmeasured in R5 (design values).
- Fun slope slide is ~1.6× the R5 fit at 30–40° (538–586 vs 318–367 u/s² extra): the HSD friction cut (`downhillFriction` 0.25) on top of the same gravity term. Reference matches R5 within 2–3 %. Setting `downhillFriction` to 1.0 would match R5; left as the M8-A design pending the playtest.
- Zipline super jump → wall-run is not reachable (wall-run start 200 along the wall [design]).
- Tap rates in the lurch demos (60 Hz edges) need a scroll wheel; a tap aid would be an input-fairness decision (track D open question 3).
- Every [design] value: wall-run, hang, double jump (M7-A), slope slide (M8-A), the lateral superglide, the coplanar tolerance 2 u, the chain-yard geometry.

## 11. Design-value list (new in M8-B)

| Mechanic | Parameter | Value |
|---|---|---|
| Superglide | `superglideExit` | Reference `InputWithW` [meas], Fun `Input` [design] |
| | `nativeExitSpeedFromApproach` / `superglideNeedsSlideSpeed` / `faceConeAlsoWish` | true / true / true [meas-based] |
| | `nativeJumpWindowPerRise` / `nativeJumpWindowRiseRef` | 0 / 76 u (plug-in; constant window 0.1025 s) |
| Wall-run | `sameWallCoplanar` / `coplanarTolerance` | true / 2 u [design] |
| Slope (Reference) | `slideSlopeNeedsDuck` | true [meas]; not serialised, not in reports |
| Map | chain yard X | §6 |
