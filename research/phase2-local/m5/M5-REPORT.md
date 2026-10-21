# M5: skill-slot system, two movement configs, playable Windows build

Plan M5:

- Two Unity configs.
  - A reference calibration config: short-range position RMS ≤ 4 u and velocity RMS ≤ 10 u/s.
  - An original fun config: wall-run, flight, gravity switch.
- A skill-slot system: 3–4 active or passive skills, with explicit interruption, cooldown, priority and speed-stacking
  rules.
- 3 preset loadouts with automated state and collision regression tests.
- A Windows test build with a short playtest route guide.

Branches:

- Research: `phase2-local/m5-play`.
- HSD-Unity: `m5/skill-slots`.
  - Part A: b23916c (skill slots, rules, RF grapple, presets).
  - Part B: 8480b2d (configs, short-range evaluation, game, build).

Both parts were implemented by subagents. The lead then re-ran everything:

- all tests (174/174 EditMode, 1/1 PlayMode);
- the replay regression;
- the 38 M4 replays (identical to the part-A publication);
- the reference-config evaluation (byte-identical CSVs and tables);
- the build smoke test.

Scope: R5Flowstate S21 (local offline), not official S21.

## 1. Acceptance

| # | Criterion | Result |
|---|---|---|
| A1 | Reference config: short-range position RMS ≤ 4 u, velocity RMS ≤ 10 u/s | **PASS for base movement, 2 ability families fail** (§3). 604/633 one-second windows pass (95.4 %). Every base-movement family passes (M1/M2 100 %, M3 lurch 92.7 %, M3 hops / slide chain 96.3 %), as do pad, stim and pounce. **Gravity lift (78.4 %) and jets (83.3 %) fail**; causes are in §3. |
| A2 | Original fun config | **PASS**: wall-run, flight, gravity switch under the same speed caps (§4). |
| A3 | Skill slots (3–4) with interruption / cooldown / priority / stacking rules | **PASS**: 4 generic slots plus a base layer. All rules are data in `SkillRules`, applied by one `SkillArbiter` ([SKILL-RULES.md](SKILL-RULES.md)). |
| A4 | 3 presets with automated state and collision regression | **PASS**: 3 loadout assets. 11 combo tests and 17 random-input runs check every command (speed caps, at most one driver, timeouts, never inside a wall, idle after 12 s), plus 30 part-B tests. 174/174 EditMode, 1/1 PlayMode. |
| A5 | Windows build + route guide | **PASS**. `HSD-Build\HSD-Practice.exe` (outside the repos). Headless smoke run: `ok: 1441 commands (12.01 s at 120 Hz)`, config and loadout switches, reset. [PLAYTEST-GUIDE.md](PLAYTEST-GUIDE.md) (Chinese). |
| R | Default replay motor unchanged | **PASS**: M2/M1 111/111, M3 90/90, M1 first guess 111/111 (same sha256 since M4). The only differences in the M4 replays are the 4 grapple trials (RF grapple). |

## 2. Skill slots and rules (part A)

- **Slots:** up to 4 generic slots, each with a button, charges and a cooldown per charge.
- **Base layer** (always on): landing slowdown and wall jump.
- **Ability states:** each ability is Idle, Pending, Driving or Effect.
- **Order of a command:** begin (recharge, mask refused presses) → abilities → combine boosts → choose a launch → grapple
  late hook → motor → abilities → end (spend charges, exclusivity, one driver, timeouts, speed ceiling).
- **Anti-exploit rules** (design values, no Apex reference):
  - Speed ceilings: 900 u/s horizontal, 1100 u/s up.
  - Boosts don't stack: the largest counts, capped at ×1.40; slows multiply.
  - One launch per command. A launch ends any driver and opens the lurch window (pad → lurch).
  - At most one Driving state; each has a timeout above its longest measured duration.
  - A charge is spent only on an accepted activation.
- **RF grapple** (from M4b):
  - At release, velocity error drops from 73–99 to 8–31 u/s and direction error from about 9° to 0.4–2.5°.
  - Pull-window position RMS gets worse (3.8–7.4 → 7.5–10.5 u). Reasons: the burst at the start of the pull is not
    modelled, and one fit serves all 62 trials (A 541 against these trials' ~502). This is reported, not tuned. A burst
    variant made the result worse and was rejected.
- **Presets:**
  - Pathfinder-Octane mobility: grapple, stim, jump pad.
  - Valk-Horizon aerial: jets, air profile, lift, grapple.
  - Revenant-Wraith ground: pounce, Wraith phase, portal teleport.
- **Frame-rate test note:** the 60 Hz determinism tolerance was corrected from half a command to a full command. Spatial
  triggers such as the pad fire at command starts, so they can move by one command. This fixes a wrong assumption in the
  test; it is not a relaxed pass. See `unity/regression.md`.

## 3. Reference config: short-range accuracy

**Definition** ([reference_config/README.md](reference_config/README.md)):

- Consecutive 1.0 s windows cover every row of all 101 trials once: M1, M2, M3, and M4 without grapple and without
  rejected trials. No window is dropped.
- Each window after the first restarts from the recorded state.
- A window passes if position RMS ≤ 4 u **and** velocity RMS ≤ 10 u/s. A family passes if its p90 meets both limits.

**Model changes in the reference config** (options; off in the default replay motor):

- **Ground vector redirect:** after a lurched landing the cross-wish velocity decays at 1250 u/s² instead of being set
  instantly. Measured |f| is 1246.8–1255.7. This closes the main M3 gap.
- **Air un-duck drop:** releasing duck in the air lowers the origin by 16.5 u, no earlier than 0.08 s after takeoff.

| Family | Windows | Pass before → after | Position p90 (u) | Velocity p90 (u/s) | Verdict |
|---|---|---|---|---|---|
| M1/M2 ground, air strafe, jumps, slide | 242 | 100 → 100 % | ≤ 3.04 | ≤ 0.32 | PASS |
| M3 lurch (tap strafe) | 82 | 78.0 → 92.7 % | 13.6 → 2.2 | 76 → 7.9 | PASS |
| M3 hops / slide chain | 54 | 85.2 → 96.3 % | 12.9 → 0.36 | 63 → 0.54 | PASS |
| M4 controls / stim | 102 | 96 → 100 % | 0.33 | ≤ 0.32 | PASS |
| M4 jump pad | 45 | 93.3 → 97.8 % | 0.69 | 0.50 | PASS |
| M4 pounce | 22 | 90.9 % | 0.64 | 8.47 | PASS |
| M4 gravity lift | 74 | 78.4 % | 5.58 | 53.3 | **FAIL** |
| M4 jets | 12 | 83.3 % | 0.28 | 14.4 | **FAIL** |

**The 29 failing windows:**

- **Lift:** the entry threshold is not exact (known since M4) and the eject is one command off. In 4 windows the body
  leaves the test plateau and lands 414 u lower, while the replay floor is flat.
- **Jets:** the stop is one command off, giving a single 158 u/s spike.
- **Other one-command offsets:** a landing, and the pounce pull-out latency.
- **M3 lurch:** a post-landing redirect-direction residual remains (three windows at 4.4–4.7 u / 13 u/s).
- **M3 slide chain:** the slide end is 6 commands off.

Nothing was tuned per trial and no threshold was changed.

## 4. Fun config (original HSD)

Same reference motor and caps, plus:

- **Wall-run:**
  - Starts in the air with W held and a wall contact.
  - Gravity ×0.15; along-wall speed is pulled toward 300·msc; at most 1.6 s.
  - Jump pushes off at 260 out + 260 up and opens the lurch window.
- **Flight (F):** no gravity, 450 u/s, 5 s of fuel. It counts as a driver, so a grapple or lift ends it.
- **Gravity switch (G):** ×1 / ×0.45 / ×1.6, with the same jump takeoff speed.

## 5. Playable build

- **Runtime:** fixed 120 Hz commands with render interpolation (bit-identical state at 30–240 fps, tested).
- **Controls:**
  - Mouse look, WASD, Shift sprint, Ctrl/C crouch-slide, Space jump / wall jump / jets.
  - Q/E/Z skill slots, Tab/F1 config, 1/2/3 loadouts, R checkpoint, T restart, Esc menu.
- **HUD:** speed in u/s and km/h, state, config and loadout, cooldowns, fuel, gravity, timer.
- **Greybox map with five stations** that form a 7-checkpoint time trial:
  - A: sprint / slide lane
  - B: hop / tap-strafe field
  - C: wall corridor and ledges
  - D: jump pad, lift and tower
  - E: grapple anchors and a raised finish deck
- **Build:** `C:\Workspace\Playground\ReApex-DataAnalysis\HSD-Build\HSD-Practice.exe`, Mono x64, 91 MB, kept out of git.

## 6. Open items

- Gravity lift and jets do not reach the reference accuracy (§3).
- The post-landing redirect direction law is unidentified.
- The grapple detach rule is unknown in R5; the game uses the 34 u envelope and has no manual release.
- Not in the game: mantle, climb, slopes, ceilings, superglide.
- Design rules, not measurements: pad → lurch, pounce auto-fire at full charge, all caps, cooldowns and teleport numbers.
- Jets fuel drain (1/s) is an assumption.
- At 60 Hz, combo chains drift up to ~35 u/s. The game therefore uses a fixed 120 Hz command rate.
