## 0. Findings (M4 Unity ability primitives, HSD-Unity `m4/ability-primitives`)

**What was added.** A small seam in `R5MotorV2`: an optional `MovementAbilitySet` runs `BeforeMove` / `AfterMove` of every ability
around each command, and the move reads per-command `CommandModifiers` (time scale, gravity scale, velocity-replacing launch after
StartGravity, external acceleration in two half steps, horizontal drag, horizontal cap). Abilities implement `IMovementAbility`
(name, `AbilitySlot` Movement / Passive / Tactical / Ultimate, Reset, BeforeMove, AfterMove, parameters) and keep their numbers in
[Serializable] params classes (defaults = the measured values; all of them also in `MovementAbilityParamsAsset`). Classes:
`StimAbility` (speed multiplier + settings mod), `JumpPadAbility` and `PounceAbility` (instant impulses, `InstantImpulse` formulas),
`GravityLiftAbility` (vertical field / gravity replacement), `JetpackAbility` (sustained thrust + post effect + fuel),
`GrappleAbility` (rope pull, `IGrappleSurface`), `LandingSlowdown` (always on), `PassiveAirProfile` / `LegendAirProfile`
(per-legend air values). The move scale is the product weapon base × ability factors; the lurch clamp is 0.7 × the current sprint
cap (`lurchClampSprintFraction`, off by default). Without an ability set the motor is the M3 motor bit for bit (`regression.md`).

**Scenario facts** (`scenarios.json`, written by `make_scenarios.py`): legend → kit; jump pad at o + (300, 0, 0) and lift base at
o + (120, 0, 0) from `hsd_trial.py` SCHEDULE_PRE; grapple surface = the M3 test wall face x −13706; per trial: the recorded grapple
detach command (the detach rule is unknown, so the replay releases the pull where R5 did; the release steps were cross-checked against
`../lift_grapple/results.json`) and the stim carried over from the previous trial in r1517 / r1553 (onset placed 6.0 s before the first
faded command of the recorded movescale; r1517's own tap gave nothing in R5, so its tactical is marked not ready). Nothing is fitted
per trial.

**Before vs after (whole-trial pos RMS 3D, mean of 2 trials).** Pad 778–993 → 1.4–7.0 u; lift ride / jump-out 899–903 → 6.4–11.0 u;
jets 356 → 0.57 u; pounce c0 530 → 6.9 u, c13 765 → 0.76 u; stim sprint 67.5 → 0.59 u; stim air 24.5 → 15.4 u. The before run is
fed the recorded movescale column (which already carries the stim, landing and weapon move scales), so for stim walk (0.60 → 0.59 u)
the after run only shows that the modelled move scale is as good as the recorded one. Controls are unchanged (ctrl sprint 0.585, valk
ctrl 0.002, Horizon e2/e4 0.31 / 0.02 u): the idle kit does not disturb the motor.

**Best reproduced.**
- **Jets** (valk_jets): jet phase pos RMS 0.03 / 0.88 u, activation on the press command, vz error on the last held command 0.00 /
  −0.09 u/s, post-effect end −1 command, landing step 0. The −2.8 u/s at release + 1 is the client trace stopping one command late
  (the model uses the dedi stop on the release command, VALK-REV §2.4). r1807's 0.88 u: the open-loop vz drifts 0.12 u/s, which moves
  the above-limit branch switch (threshold margin 0.01 u/s) one command and leaves a 3.4 u/s step that decays.
- **Pounce c13**: launch step 0, launch v_h / vz error −0.2..−0.5 u/s, landing step 0, range −0.3 / −0.8 u.
- **Pad launch**: launch on the recorded command in 5/6 trials, launch v_h −0.013 / vz +0.008 u/s (the +0.013 is the unmodelled W
  drift of octane §3.3), flight pos RMS 1.5–2.3 u standing.
- **Lift**: entry within one command, eject velocity error ≤ 0.01 u/s (400 view / radial + 450 up), lift-phase pos RMS 7–12 u.
- **Stim**: onset on the recorded command in all 4 tap trials, fade start +1 / +2 commands (the client predicts the fade 0–2 commands
  before the dedi, whose timing the model uses), sprint cap 420.954; the strafe press under stim: |Δv| 298.14, error 0.003 u/s
  (before, with the 209.3 clamp: 85.4 u/s).

**Worst / not reproduced, with the cause.**
- **Grapple hold / near, whole trial 297–431 u (worse than the 199–319 u of the motionless before run).** After the recorded release the
  body hits the wall, hangs and climbs; the replay has no wall, so the sim flies on through it. The pull itself: pull window pos RMS
  6.5–7.4 u (hold) and 3.8–3.9 u (near) vs 114–180 u before; attach (hop) step 0, pull start −1 / 0; position error at the release
  4.9–11.4 u, speed error +3.6..+11.7 u/s, but the **velocity direction** is off by 73–100 u/s at the release: the global F1 model
  (518.3 u/s² toward hit + 51 u, gravity ×0.047) under-produces the late upward curvature near the face (LIFT-GRAPPLE §2.2/§2.5, the
  known F1 limitation; neither F1 nor R1 is the mechanism). The burst (1662 u/s² × 4 commands) is modelled, the ~800 u/s² phase after
  it is not.
- **Lift strafe, 349 u**: the ejected body leaves lane C sideways and falls off the field edge (ref lands at z −120, 50 steps after
  the sim lands on the replay's flat floor). Geometry, not the lift: lift phase 9.8 / 12.1 u, eject −1 / −2 commands.
- **Lift hover start −3..−5 commands**: the reference trace has a dedi correction 4 commands after entry (−5 u in z, client enters
  the lift ≈ 4 commands before the dedi, LIFT-GRAPPLE §1.2); the sim keeps the client's head start and reaches 90 % height earlier.
  The eject follows the 0.5 s hover rule (−1..−4 commands).
- **Pounce c0, launch −2 commands, v_h −2.3 u/s, range −7.2 u**: the model launches at press + 0.9 s (toss_pullout_time); R5 launches
  109–110 commands after the press (0.908–0.917 s) with a charge of 0–1 command (701–703 u/s instead of 700). Not tuned.
- **Pad crouch, landing +2 / +4, flight pos RMS 10–13 u**: in R5 the duck is released in mid-flight and the un-crouch moves the origin
  ≈ 14 u (no duck hull transition in the motor, the M3 gap); r1536 also launches one command late (the crouch walk ends 0.27 u short of
  the 48 u trigger distance).
- **Pad landing f0 0.227 vs 0.240 (r1531, walk)**: the replay floor is the start height 294.274, the landing area is at 294.92, so the
  sim falls 0.65 u further, lands one command later and 5 u/s faster, which the vz² rule turns into a 0.013 lower f0.
- **Stim / ctrl air, 10–15 u**: entirely after the landing, the M2 instant ground redirect (M3 notes); the air phase and the press are
  exact. stim_air r1516 improves 38.0 → 20.5 u (stim cap 420.95 and the 294.67 lurch clamp).
- **max |Δ maxspeed| 32.84 u/s in the stim trials**: the client drops the stim settings mod for one command a few commands after the
  onset (octane §2.1, a client artefact).

**Not exercised by the replay (unit tests only).** Grapple W cap 483 and auto-detach gap, the jets fuel cut (drain rate assumed
1 meter/s, NOT measured), jets reactivation gates and W thrust, lift re-entry block and the short-dwell eject scaling, pad debounce and
heading choice, pounce high/low pitch rules, landing slowdown recovery with W held, Horizon air cap 92 with input (in the e2/e4 controls AirAccelerate never adds: no input, or forward at 199.5 u/s,
above the wish cap; the census already carries 80/800, so the passive changes nothing in these trials).

**Open gaps.** Grapple detach rule (scenario-driven), grapple pull direction late in the pull, grapple wall impact/hang/climb; pad
double jump (no double jump in the motor) and launch heading (velocity vs view vs pad yaw undetermined); stim reuse lockout; jets fuel
drain/recharge and jetpackPostEffectTime; pounce auto-fire at full charge and the 1–2 command pull-out latency; duck hull transition;
flat-floor replay (floor 294.274 vs 294.92 at the far end of lane C; the field edge in lift_strafe).
