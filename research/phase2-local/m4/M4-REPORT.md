# M4: legend movement abilities as reusable primitives (+ M4b view control and grapple swing)

Plan M4:

- Survey the legends and measure only those with a representative movement mechanism, each against the same legend with
  the ability unused.
  - P1: Pathfinder, Octane, Horizon.
  - P2 (as needed): Revenant, Valkyrie, Vantage.
  - P3 (transitions only): Wraith, Ash, Loba.
- Extract and model at least 3 classes of movement primitive as Unity components.

M4b was added with the user's approval after an external review of M3:

- Per-command view control in the runner.
- A minimal grapple swing / steer / detach / momentum experiment.
- Re-jump after a jump pad.
- Combination chains are moved to the M5 skill-slot rules.

Scope: every finding is for **R5Flowstate S21** (S21 client + S3 dedi + SDK, local offline). It is not official S21.

Branches: `phase2-local/m4-abilities` (research) and `m4/ability-primitives` (HSD-Unity).

Every analysis was written by a subagent and re-run by the lead, with byte-identical outputs. The Unity tests and replays
were also re-run by the lead (§6).

## 1. Acceptance

| # | Criterion | Result |
|---|---|---|
| A1 | P1 legends measured with ability-off controls | **PASS**: Octane (stim, pad), Horizon (lift, passive), Pathfinder (grapple). Controls `m4_ctrl_*`, `e2/e4` and the T0 census. |
| A2 | P2 as needed | **PASS** for Valkyrie (jets) and Revenant (pounce). **Vantage not measured**: on the dedi its jet drive is an SDK reimplementation, not S21 code, and the motion is covered by the thrust and impulse primitives (§3.5). |
| A3 | P3: speed kept across teleports, plus stun | **PASS (transitions only)**: Wraith tactical measured; Loba speed zeroed on teleport (measured); Portal / Phase Breach from source (§3.5). |
| A4 | ≥ 3 primitive classes, parameters extracted and modelled as Unity components | **PASS**: 7 classes, replayed against 38 R5 trials, 99/99 tests (§4, §6). |
| M4b-a | Per-usercmd view control verified on the trajectory | **PASS for yaw**: 178/180 commands at the set rate, server heading = client yaw ± 0.001°. **Pitch: not possible** (`+lookup`/`+lookdown` do nothing in R5) (§5.1). |
| M4b-b | Grapple swing, steering, detach, momentum | **Partial, by the stop-loss rule.** Pull law identified across anchors and entry speeds (RF model, §5.2). Momentum at release identified. **Detach rule not identified** after three rounds. Unity envelopes given. |
| M4b-c | Re-jump after a pad | **PASS** (§5.3) |

## 2. Data

All runs: 120 fps, legend pinned, kit equipped through `--kit` (`GiveOffhandWeapon` / `GivePassive`), at least 5 valid
trials per condition. Frame-rate failures were re-run, never relaxed.

| Session(s) | Content |
|---|---|
| M4_octane, M4_octane_rerun | stim (sprint / walk / air), pad (sprint / walk / crouch), controls |
| M4_horizon, M4_horizon_lift2 | lift (ride / jump-out / strafe), Horizon passive, controls |
| M4_pathfinder, M4_pathfinder2 | grapple: hold, W, near / far, pitch 0 / −20 |
| M4_valkyrie (+rerun), M4_revenant (+rerun) | jets vs control; pounce tap / partial charge |
| M4b_octane, M4b_octane2, M4b_viewprobe | view acceptance; pad re-jump |
| M4b_swing, M4b_swing2, M4b_swing3 | swing round 1 (side anchor, turn, W, jump) and round 2 (speed across the rope) |
| M4_wraith (+2), M4_loba | P3 transitions |

## 3. Measured models (detail docs)

- [octane/OCTANE-PRIMITIVES.md](octane/OCTANE-PRIMITIVES.md)
- [lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md](lift_grapple/LIFT-GRAPPLE-PRIMITIVES.md)
- [valk_rev/VALK-REV-PRIMITIVES.md](valk_rev/VALK-REV-PRIMITIVES.md)
- [p3_transitions/P3-TRANSITIONS.md](p3_transitions/P3-TRANSITIONS.md)
- M4b: [../m4b/VIEW-ACCEPTANCE.md](../m4b/VIEW-ACCEPTANCE.md), [../m4b/swing/SWING.md](../m4b/swing/SWING.md),
  [../m4b/pad_rejump/PAD-REJUMP.md](../m4b/pad_rejump/PAD-REJUMP.md)

### 3.1 Octane

- **Stim:** movescale ×1.298 for 6.0 s, then a 0.5 s cosine fade. While stimmed, a hidden settings mod sets sprintspeed
  282 and sprintAcceleration 120.
- **Jump pad:** launch = 1150 · normalize(h + 2·up), or 1.0 instead of 2 when ducked. Horizontal velocity is
  **replaced**, and the flight runs in 0.8× slow-mo.
- **Landing slowdown** (all legends with landSlowdownDuration > 0):
  - On landing, speed is multiplied by clamp(1.996 − 1.6714e-6·vz², 0, 1); this does nothing below |vz| ≈ 772.
  - Movescale then recovers over 1.0 s.
- **Lurch clamp** = 0.7 × the current sprint cap.

### 3.2 Horizon

- **Gravity lift:**
  - vz is set to 300; steering 2000 u/s² up to 170 u/s.
  - Hover at 90 % of 1200 u for 0.502 ± 0.003 s.
  - Eject 400 along the view + 450 up.
- **Passive:** airSpeed 80, airAcceleration 800, landSlowdownDuration 0.

### 3.3 Pathfinder grapple (M4, then refined in M4b §5.2)

- Hook flight ~2035 u/s; then a 200 u/s hop that sets vz (also in the air); then a 0.2 s wind-up.
- No terminal speed: release speed is 474 / 612 / 804 u/s at 244 / 394 / 694 u.
- Release is exactly continuous (no boost or cut), then ballistic.
- **Jump does not release the grapple.**

### 3.4 Valkyrie and Revenant

- **Jets** (fit rms 0.004 u/s per command):
  - Thrust 1.9 (1.7 with a move key), plus a start-up boost 1.8× fading over 0.5 s.
  - vz pulled toward the target with a 0.27 s half-life; horizontal 0.14 s half-life, strafe 1035, tapering out between
    300 and 600 u/s.
  - On release, vz ×0.4, then 0.45 g plus quadratic drag until about 50 u above the ground.
  - Fuel drain was **not** observed.
- **Pounce:**
  - 0.9 s pull-out, then up to 1.3 s of charge.
  - Velocity is replaced by (700 + 450·charge) along pitch + 35°; the flight is ballistic.

### 3.5 P3 and skipped legends

- **Wraith tactical:** msc 0.80 for 1.17 s (deploy), then ×1.388 for 2.77 s, then a 0.79 s fade. A pure movescale
  modifier, so it fits the speed-multiplier class.
- **Loba:** velocity is zeroed at the teleport (6/6 teleports, 0–5.5 u/s after). No control lock.
- **Portal / Phase Breach** (source): server path replay; exit velocity = node velocity; controls frozen.
- **Conclusion:** no Apex teleport carries speed across.
- **Not measured:**
  - Ash dash: unknown setfile mod, and the plan lists only teleports for Ash.
  - Vantage: see A2.

## 4. Primitive classes (Unity, HSD-Unity `m4/ability-primitives` 4410b36)

| Class | Unity component(s) | Apex sources |
|---|---|---|
| Speed multiplier (movescale × factor, timed, with fade) | `StimAbility` | Octane stim; Wraith tactical (same class, other numbers) |
| Instant impulse / velocity replace | `JumpPadAbility`, `PounceAbility` (`InstantImpulse`) | pad, pounce, lift eject; Portal / Breach exit |
| Sustained vertical field / gravity replacement | `GravityLiftAbility` | Horizon lift |
| Sustained thrust + post effect + fuel | `JetpackAbility` | Valkyrie jets |
| Rope pull toward an anchor | `GrappleAbility` (`IGrappleSurface`) | Pathfinder |
| Landing slowdown | `LandingSlowdown` | all legends (setfile) |
| Per-legend air profile | `PassiveAirProfile` / `LegendAirProfile` | Horizon passive |

- **Seam:** `IMovementAbility` (slot Movement / Passive / Tactical / Ultimate) plus per-command `CommandModifiers`. The
  modifiers are time scale, gravity scale, velocity-replacing launch, external acceleration, horizontal drag and
  horizontal cap.
- **Parameters:** in `[Serializable]` params and `MovementAbilityParamsAsset`, ready for the M5 skill slots.
- **Default motor:** with no ability set it is bit-for-bit the M3 motor.
- **Grapple:** the Unity grapple still uses the M4 constant-pull model (F1). M5 switches it to the RF model and the
  envelopes from §5.2.

## 5. M4b

### 5.1 View control

- **Runner changes:** new step `set cl_yawspeed N`, applied on the client console (sending it through
  `player.ClientCommand` forwards it to the server and it is ignored), plus `+left`/`+right`.
- **Yaw rate:** 178/180 turning commands at 90 ± 1 °/s; the two edge commands turn at half rate. Net error ≤ 0.05°.
- **Turning while sprinting:** the turn rate is ×0.67 when +speed is held.
- **Trajectory:** the dedi velocity heading equals the client yaw to ±0.001°.
- **Pitch:** cannot be changed per command (`+lookup`/`+lookdown` are inert in R5), so it is set per trial.

### 5.2 Grapple swing (3 rounds, 79 trials)

- **Pull law, model "RF":**
  - Along the rope, a linear speed ramp of ~495–541 u/s² with no cap.
  - Across the rope, a constant brake of ~420 u/s². This produces a ~10 % speed dip with lateral entry speed.
  - The target is the aim-ray hit at fire time (world-fixed), +32 u up.
- **Fit:** one parameter set for all 62 no-input trials, rms 11.8 u (6.8 u horizontal). Pure acceleration toward the
  anchor (F1) gives 39 u; the rope / pendulum model gives 80 u on the cross trials.
- **No pendulum:** Apex's grapple does not swing; the sideways speed is braked.
- **W held:** velocity along the flat view forward is hard-clamped at 483 = 420·msc. Horizontal speed can reach 560 when
  the view is off the motion.
- **Steering without W is negligible:** a 54° view turn moves the release heading by +1°.
- **Detach:** typically a 30–47 u gap, 2–6 commands before impact; sometimes not until contact. No single-feature rule
  fits all 79 trials, so it is **unidentified**. Unity uses the envelope.
- **Momentum:** fully kept at release, then ballistic. Air control after release was not exercised.

### 5.3 Pad re-jump

- The landing slowdown applies fully before the re-jump: f0 0.2420 against the model's 0.2421.
- The ground jump caps v_h at **260·msc**, so 72.6 u/s here. The M3 cap of 299 is the same rule at msc 1.15.
- Only 14 % of the pad's 514 u/s carries into the re-jump; re-jump height is the 0.3 floor.
- New finding: the soft landing of the hop ends the pad slowdown (msc back to 1.15).

## 6. Unity verification (lead re-run)

- **Tests:** EditMode 99/99 (67 existing + 32 new).
- **Replays:** the 38 M4 trials re-run gave 114/114 byte-identical output files (with `-scenarios scenarios.json`).
  - Scenario facts not in the input stream (pad and lift positions, wall face, recorded grapple release) live in
    `unity/scenarios.json`. Nothing is fitted per trial.
- **Regression:** the plain motor is byte-identical to main on M2/M1 (111/111) and M3 (90/90); M1 first guess 111/111.

Whole-trial position RMS, before (plain motor) → after (mean of 2 trials):

| Condition | Before → after | Note |
|---|---|---|
| jets | 356 → 0.57 u | |
| pounce c13 | 765 → 0.76 u | |
| pad walk / sprint | 778–826 → 1.4–1.7 u | launch velocity error 0.01 u/s |
| stim sprint | 67.5 → 0.59 u | |
| lift ride / jump-out | ~900 → 6–11 u | eject velocity error ≤ 0.01 u/s |
| pounce c0 | 530 → 6.9 u | 2-command pull-out latency |
| pad crouch | 993 → 7.0 u | duck hull change not modelled |
| stim air | 24.5 → 15.4 u | rest is the known M2 post-landing redirect |
| grapple, pull window | 114–180 → 3.8–7.4 u | whole trial worse, because the replay has no wall and the sim flies through it after release |

## 7. Unresolved

| Item | Status |
|---|---|
| Grapple detach rule | Unidentified after 3 rounds (stop-loss). Next probe: a free-standing pole or a wall-edge anchor. |
| Grapple in Unity | Switch to RF + envelopes in M5. |
| Combined W-held pull law (sideways / vertical) | Partly identified. |
| Jets fuel drain / recharge | Not observed; Unity drain rate 1/s is an **assumption**. |
| Pad double jump, pad launch heading, stim reuse lockout | Not modelled. |
| Duck hull transition (pad crouch, M3 hops) | Not modelled. |
| Per-command pitch control | Not possible in R5. |
| Ash dash, Vantage, Portal / Breach measurement | Not measured (§3.5). |

## 8. M3 wording corrections (agreed with the user)

- **Tap strafe:** only the **single-press** lurch is modelled. Several presses per jump, diagonal presses and the 1100
  cutoff are untested.
- **Superglide:** Jump + Crouch on the same frame and crouch-then-jump were **not tested**. M3 measured only the mantle-boost
  window.
- **Wall bounce / mantle in Unity:** formula and unit tests only. There is **no** replay against the same geometry.
- **Scope:** all findings are for R5Flowstate S21, not official S21.

## 9. Next (M5)

- Skill-slot system (3–4 slots) on the `IMovementAbility` seam, with interruption, cooldown, priority and speed-stacking
  rules.
  - Combination checks to include: grapple release → slide, pad → lurch, wall jump → impulse.
- Grapple RF model.
- Two configs: a reference config (short-range position RMS ≤ 4 u, velocity ≤ 10 u/s) and an original fun config.
- 3 presets with regression tests.
- Windows build plus a route guide.
