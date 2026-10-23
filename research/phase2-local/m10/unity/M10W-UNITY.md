# M10-W (track U): Wraith — Dimensional Rift (portal) and the Into the Void audit in HSD-Unity

HSD-Unity branch `m10w/wraith`, commit `91e8b27` (from main `30d4271`), Unity 6000.6.5f1. Inputs: `m10/M10-PLAN.md` ("用户随计划给出的决定" §3: the portal
is approved), track R2 `m10/r2_wraith/PORTAL-R2.md` + `params.json`, `m10/r2_speedboost/SPEEDBOOST-R2.md`, track R `m10/r_wraith/WRAITH-M10.md` +
`params.json` (R5Flowstate local hybrid build, S21 client + S3 dedi + SDK, 120 fps; lead-verified, byte-identical reruns), track D
`m10/d_library/TECHNIQUE-LIBRARY-M10.md` §3.39–3.40 (S21 rules only; the 25 Mar 2025 Void / Rift changes are post-S21), M4 `m4/p3_transitions/P3-TRANSITIONS.md`,
M6-B `m6/unity/M6B-UNITY.md` (Phase Breach traversal), M10-C `m10/unity/M10C-UNITY.md`.

Result classes (M10 rule):
- **Numbers / rules tests: pass.** EditMode 1968 / 1968, PlayMode 1 / 1 (§8).
- **Real-input demos: pass.** 8 new `m10w_*` demos, each with a failure variant; smoke 238/238 (M10-W 16/16).
- **Human feel: not accepted** (needs the user's playtest; guide `m10/PLAYTEST-GUIDE-M10W.md`).

Labels: **[meas]** R5 measurement, **[src]** local script (`mp_weapon_phase_tunnel.nut`, `mp_ability_phase_walk.nut`), **[fit]** chosen to match the R5 rows,
**[inf]** interpretation, **[design]** HSD choice. Nothing post-S21 (Void 0.8 s / 20 s / exit any time, compressed Rift ramp of 25 Mar 2025, Void Jumper 2026).

## 1. The speed-boost rule (shared helper)

`SpeedBoost` (`R5Replay/Runtime/Abilities/SpeedBoost.cs`): **msc = W · (1 + 2·q(S))**, q(S) = floor(255·S)/255, W = 1.15 (melee in hand, every HSD baseline)
or 1.0 (weapons holstered / locked), larger severity wins (`Combine` = max), timed boosts hold for (duration − fade) and fade linearly inside the duration
(`TimedSeverity`). Tests reproduce the R2 table to 5e-5 (0.05 → 1.2582 … 1.0 → 3.45) and the locked-hands sprints 364 / 414.98 / 468 / 518.98.

The rift and the S21 Void use it with W 1.0: the ability sets `ctx.weaponMoveScale = 1.0` and adds the factor (1 + 2q); the arbiter's "largest boost wins"
stacking gives the "no sum" rule. The new **Wraith S21** preset raises its own boost cap to 2.0 (the M5 cap 1.40 would cut ×1.596 / ×1.996); every other
preset keeps 1.40.

Existing numbers checked, **none changed**:
- Octane stim: severity 38/255 = q(0.15) exactly, ×1.298038 — agrees.
- M4 Wraith phase preset (`StimParams.WraithPhase`, Revenant-Wraith ground, M4 replay): ×1.388 on W 1.15 = 1.5962 vs the rule 1.596078 — sprint 415.01 vs
  R5 414.98 (0.03 u/s). Kept for the byte-identical M4 replay and the user's "leave the old Revenant-Wraith preset as is"; see §2 for its other differences.

## 2. Into the Void audit and the S21 Void

Re-reading the client usercmd move scale of the 5 M10 + 7 M4 Void trials (identical shapes; the M10 r_wraith summary "0.8 for 1.175 s then 1.5961 for 2.8 s"
is the min / plateau of this trace):

| t after the press | R5 (client msc, v_h) | M4 preset (`wraith_phase`, unchanged) | S21 Void (`into_the_void`, new) |
|---|---|---|---|
| 0 … 0.367 s | 1.15 (44 commands), sprint continues | ×0.80 → 0.92 from 0 s | 1.15 (nothing yet) |
| 0.367 … 1.167 s | 0.8 rising to 1.0 on a cosine (0.9001 at mid-ramp); **sprint interrupted**: v_h follows the walk cap 173.5·msc (140.6 at 0.81) | 0.92 flat to 1.17 s, sprint kept | W 1.0 · (0.8 → 1.0 cosine), sprint blocked |
| 1.175 … 3.975 s | 1.5961, v_h 414.98 (auto-sprint) | 1.5962 (1.15·1.388) from 1.17 s for 2.77 s | 1.596078 = 1.0·(1 + 2·q(0.3)) for 2.8 s, auto-sprint [src] |
| 3.975 … 5.167 s | smooth fall to **1.0** (cosine-like, 1.3477 at 4.5 s; a small shoulder at 1.094) | cosine 0.79 s back to 1.15 | cosine 1.1917 s to 1.0 (max error ~0.04 at the shoulder) |
| after | stays 1.0 (hands empty until a weapon is drawn) | 1.15 | 1.15 [design: HSD has no weapon slot] |
| phased | phase flag 3.9 s (10 Hz rows), from the plateau | — | 1.175 → 5.175 s (S21 4 s [wiki]) |

Differences of the M4 preset against R5 (reported, not changed — it belongs to the M4 replay and the user wants the old preset left alone): the deploy is
0.92 not 0.8 and starts 0.37 s early, the sprint is not interrupted, the fade ends at 1.15 after 0.79 s instead of 1.0 after 1.19 s, the plateau starts
0.005 s early and is 0.03 s short. The new `IntoTheVoidAbility` (`VoidS21Params`) follows the trace; it is used only by the Wraith S21 preset. Library
values: 1.25 s activation / 4 s / +30 % / 25 s: measured 1.175 s / 4.0 s phase / +38.8 % sprint (414.98 vs 299) / 25 s preset cooldown [wiki].

## 3. Dimensional Rift (`DimensionalRiftAbility`, `RiftParams`)

| Rule | Value | Evidence |
|---|---|---|
| Press → raise: hand scale for 0.375 s, then msc 0.2 easing to 1.0 (cosine, 0.6 s), W 1.0, **sprint interrupted** (walk cap: 299 → 64.3) | HSD: v_h min 64.3 ± 3 (test) | [meas r18001 + 4] |
| Start node + placement boost | **1.04 s** after the press | [meas] client msc 1.4 at 1.009–1.060 s (n 5); the dedi 10 Hz rows first show placing at 1.11–1.17 s, i.e. the start lies in (1.01…1.07, 1.11…1.17). The brief's "~1.14 s" is the logged row (an upper bound); the movement-relevant onset is 1.04 |
| Placement: node every 0.1 s (feet, grounded), auto-sprint, severity max(0.2, tracker) capped at 0.5, W 1.0 | sprint 364 / 415 / 468 / 519 | [meas] [src] |
| Tracker: starts 0.1, +0.1 when the straight 3D % of 6000 u exceeds the last step's % + 20, re-based on the crossing (10 Hz check) | HSD drop from 6000 u: steps at **44.0 / 65.7 / 87.2 %** | R5 drop (5238 u): 43–48 / 65–71 / 87 % [meas 3] |
| Exit: press again, 6000 u of horizontal path, or 10 s | auto-end reasons `distance` / `time` | [src 6000; W-Portal: energy by horizontal distance]; 10 s [R2] |
| Min gap 128 u (straight start node → exit) | cancel, start removed, **charge kept** | [src 128; meas 125.7 none / 141.7+ pair] |
| After the exit press | boost 0.1 s, then W 1.0 for 1.0 s, then 1.15 | [meas 0.07–0.14 / 0.97–1.04 s, n 2] |
| Lifetime | 45 s | [src + meas 45.1] |
| Travel | kinematic + phased along the recorded nodes, input locked; 0.1 s to the first node, the path at constant speed over floor(clamp(L/1024, 0.3, 2.0 → 3.5)/0.1) frames, 0.1 s on the arrival node | [src] + [fit] |
| Travel time | 349 u → 0.5 s, 466 u → 0.6 s, 6190 u → 3.7 s (all R5 rows reproduced) | [meas 24] |
| Exit velocity | **exactly 0**, both directions, any entry speed (walk / sprint / slide 385) | [meas 24] |
| Re-entry | the arrival portal is "occupied" until the body leaves its trigger; walk out and back in → travels again; 0.5 s debounce | [meas] [src 0.5] |
| Phased (S21 Void) | crossing a portal does not travel (it must be left and re-entered); ult press does nothing, not spent | [meas 0/3; n 2] |
| Trigger | body origin within 32 u horizontally, −36…+72 u of the node | [design; R5 crouch portals r 16 [src]; standing size unmeasured] |

- **Arbiter row** (`SkillLoadouts.RiftTraits`, only in the Wraith preset): raise + placement Pending (guard 12 s), travel an exclusive uninterruptible driver
  (guard 4 s, `exclusiveOnDrive` like the Phase Breach): entering a portal ends the zipline ride / grapple pull / climb that carried the body in; the use key is
  blocked during the travel; other slot presses are refused while travelling.
- **Charge**: spent when the pair is created (a cancel or a raise cancel keeps it). Preset cooldown 20 s [design; S21 3 min].
- [design] choices: a new pair replaces the old one when it is created; no travel while raising / placing (a portal touched then must be left first); the
  view is not turned by the travel (R5 lerps the view along the path, unsettled after short travels); the velocity during the travel is 0 (R5 writes the
  node velocities into the field but ends at 0; no effect on the motion); a second press during the raise cancels it (no spend).
- Two motor hooks added to `MovementAbilitySet` (never set by an older ability, so the replay and every older body are unchanged): `ForceSprint` (R5
  auto-sprint) and `BlockSprint` (sprint interrupted).
- Visual layer (`AbilityVisuals.UpdateRift`, read only): the recorded path as a line (live while placing, brighter after each speed step), a translucent
  column on each portal (dimmer as the 45 s run out, grey while occupied) with the seconds left above it; HUD lines (`PracticeGame.RiftNote` /
  `VoidNote`): raising countdown, straight distance / % / boost / sprint / time and distance left, "too close" warning, pair time left and its travel time,
  travel direction; the Void deploy / PHASED countdown.

## 4. Preset, keys, yard

- **Wraith S21** preset (loadout 9, key `'`; both configs, same rules): Into the Void on Q (25 s), Dimensional Rift on Z (20 s), rules boost cap 2.0, traits
  `RiftTraits` + `VoidTraits`. Asset `Presets/Loadouts/WraithS21.asset`. The M5 Revenant-Wraith preset is unchanged (test).
- **Wraith yard WY** (`PracticeMapM10W.cs`, appended after every older block / decal / lift; every older demo, the scripted routes and the course laps were
  re-hashed per command: identical):
  - **WL placement lane**: decal line along y −550 from the start tile x 400 to x 6600, marks at 20 / 40 / 60 / 80 / 100 % of 6000 u (x 1600 … 6400) with signs.
    Decals only (no block lies on y −600…−500 between x 100 and 11900). On flat ground the 10 s placement reaches the 40 % step (415) from a standstill; 60 %
    needs a faster start.
  - **WT drop tower** in the empty block x 8200–9800, y 1800–2200: step (top 1000) and tower (top 2000), a floor lift west of the step and a step lift west of
    the tower (walk in looking east: ejected onto the next level — test in both configs); the drop run east along y 2050 to x 11300 (the wall at x 11580 ends
    it). Heights for pairs: floor / 1000 / 2000. The full 6000 u route does not fit the map (13600 × 5200 u, mostly built); the drop gives the long-path case.

## 5. Demos (Reference, Wraith S21; F6 / smoke)

| Demo | Success | Failure variant |
|---|---|---|
| `m10w_rift_travel` | lane pair (462 u), walk back into the exit → 0.60 s travel → start portal at 0 u/s | second Z during the raise: cancelled, no portal |
| `m10w_rift_gap` | exit at 157 u → pair, charge spent | 0.15 s earlier: 112 u < 128 → cancelled, charge kept |
| `m10w_exit_slide` | arrive at rest, sprint 0.9 s (287), crouch → slide 457 | crouch 0.05 s after the exit (104 u/s): no slide |
| `m10w_rift_repeat` | exit → start, step out and back in → start → exit (both at rest) | stand on the arrival portal: no second travel |
| `m10w_void_portal` | Q, phased walk through both portals: no travel | Q 1.5 s later: reaches the exit before the phase → travels |
| `m10w_place_ramp` | 40.2 % step at 8.0 s: sprint 364 → 415 | exit at 34 %: no step |
| `m10w_drop_long` | tower top → fall → run → 3262 u path: 2.30 s travel back up, at rest on the top | exit after the landing: 2296 u → 2.20 s (the 2.0 s cap) |
| `m10w_pad_portal` (combo) | OY4 pad flight lands in the start portal (vz −999) → exit at rest | turn east too late: walks past the pad, no flight |

Combos: pad → portal (demo); zipline ride and grapple pull into a portal (tests: the travel ends the ride / pull, exit at rest); exit at rest → slide (demo),
→ jump + tap strafe (test); Void + portal (demo + test). A demo for the grapple combo is not possible with a preset (no preset has both).

## 6. Tests

New: `R5Replay/Tests/Editor/R5MotorM10WTests.cs` — `SpeedBoostM10WTests` (R2 table ×8, locked-hands sprints, max / timed fade, older stim / phase agreement),
`VoidM10WTests` (R5 timeline in both configs, phase window / auto-sprint / refused re-press, preset and the unchanged Revenant-Wraith), `RiftM10WTests` (R5 travel
rows ×10, raise + start node + 364, the boost tail, 128 u cancel / spend ×2, drop steps 44 / 66 / 87 %, 10 s / distance ends, exit at rest ×6, standing / re-entry,
phased, 45 s, input ignored + through a solid, zipline and grapple into a portal, jump + lurch from the exit, no travel while placing / replacement);
`Game/Tests/Editor/M10WGameTests.cs` (preset in both configs and the old preset, yard appended and free, the lift chain ×2, the 8 demos + failure variants
and their order, HUD notes). `MovementDemoTests.EveryDemoFailsWithItsFailureShift`: cases for the 8 new demos.

Changed existing tests (why): `M10CGameTests` (9 loadouts; the M10-C blocks are followed by the M10-W yard; the M10-C demos come last before the M10-W ones),
`M10BGameTests` / `M9AGameTests` / `M9BGameTests` / `M9CGameTests` / `M8CGameTests` (demo order: the M10-W demos are appended; M9-B also the loadout count),
`SkillLoadoutTests.PresetsHaveThreeToFourValidSlots` (Wraith S21 has 2 slots), `SkillFuzzTests.Fuzz` (usage count: for the Wraith preset the cancelled raises and refused presses count — 25 s / 20 s cooldowns in a 30 s fuzz), `PhaseBreachTests.AshRouteLoadoutIsValid` (loadout count 9). No older assertion value changed. (`FeedbackRecorder` deliberately does not list the M10-W signs: the lane mark signs would become the nearest station in `M9BGameTests.TheFeedbackNamesTheRevenantYard`.)

Results: EditMode **1968 / 1968**; PlayMode **1 / 1**.

## 7. Regression, build, smoke

- Replays (m5/unity/regression.md): M2+M1 v2 vs main **111** identical; vs pre-M3 **35 / 76**; M1 first guess **111**; M3 **90**; M4 with `-scenarios <abs>/m4/unity/scenarios.json` **114 identical**.
- Build `HSD-Build/M10W/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10W\HSD-Practice.exe`), exit 0. The re-serialised
  `Scenes/Practice.unity` / `ProjectSettings/ProjectSettings.asset` (and EOL-only rewrites of the config / older loadout assets) were reverted; the new
  `WraithS21.asset` is committed. ignore-cr stat equals the plain stat (33 files, +2099 / −21); no CR in the committed .cs.
- Smoke `-batchmode -nographics -smoke 12`: `[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset; events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 238/238 verdicts as expected (119 SUCCESS at shift 0, 119 failure cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16, M9-C 14/14, M10-A 14/14, M10-B 18/18, M10-C 20/20, M10-W 16/16); course lap 80.55 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2127 bytes); 130834 commands in total`
- **Older demos and routes** (per-command hash of position, velocity, buttons, lurch, events; every older demo at shift 0 and its failure shift (222 runs),
  the 12 s smoke route in both configs, the 30 s scripted route and the course lap for every config × older loadout, against main `30d4271`): **all identical**.
  The yard (blocks, decals, lifts appended last) and the new abilities change nothing outside the Wraith preset.

## 8. Gaps and open questions

1. **Standing portal trigger size** unmeasured (32 u / −36…+72 [design]); crouched nodes are not forced (R5 forces crouch and uses a smaller trigger).
2. **Exit facing**: R5 turns the view along the path (unsettled after short travels) — HSD leaves the view alone [design].
3. **Start node 1.04 s** (client onset) vs the brief's ~1.14 s (dedi logged row); both bracket the same event.
4. **Void fade end**: R5 settles at 1.0 (hands empty); HSD returns to 1.15 at the fade end [design]; the R5 fade's small shoulder (1.094 for ~0.07 s) is not
   modelled. The old M4 phase preset differs from R5 (§2) and is unchanged by request.
5. **Placement auto-end**: 10 s [R2] and 6000 u horizontal [src]; the "hold" placement (R5 kept placing to ~8.6 s while held) and the portal-glide refund
   (≤ 3 m keeps the boost) are not modelled.
6. Other players / projectiles through portals, the Wraith cooldown upgrade: not modelled.
7. **Pre-existing motor issue found (not changed)**: with the Reference ground redirect (M5 `groundVectorRedirect`, both configs) a wish exactly opposite the
   velocity at or below the cap never turns it: run forward, then hold S with the mouse still → the body keeps moving forward at 199.5 u/s; turning W 180°
   in one command while moving does the same. Any yaw change ≥ ~1° breaks it. `GroundVectorRedirect` decays only the cross component and adds at most cap − s
   along the wish. A fix would change older trajectories → lead decision.

## 9. Design values

Trigger size, the in / out split of the +0.2 s, the 20 s preset cooldown, the Void return to 1.15, the yard geometry (lane position, tower / step sizes and
heights, lift positions, run lane), demo thresholds (travel > 2.2 s, slide after the exit, 410 u/s for the 415 step).
