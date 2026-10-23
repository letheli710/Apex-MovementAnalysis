# M10-D2 / D3 (track U ①): per-key direction input, pad-launch lurch window follows R5 in the Reference

HSD-Unity branch `m10d/input-padlurch` (from main `37fcc88`), commit `aca5a22`. Build `HSD-Build/M10D/HSD-Practice.exe`. Plan: [../M10-PLAN.md](../M10-PLAN.md) (D2, D3 and the user's D3 decision).

> **Result classes (kept apart)**
> - **「数值/规则测试通过」** (numbers and rules): the per-key input (all 16 key sets, legacy equivalence, a bit-identical fuzz in both configs), the opposing-key / release / three-key lurch outcomes, R-1a now against the R5 number, R-2, the pad-launch window per config and its interactions (pad double jump, map pads, jets, the Fun air jump, Octane in both configs) are unit-tested. Every R5 replay is byte-identical, every older demo verdict, the M5.5 route and the course lap are unchanged (§5–6).
> - **「真实按键演示通过」** (real-input demos): no new demo. The M5.5 `pad_lurch` demo now runs in Fun with its verdict text unchanged; the smoke still shows 170/170 (§6).
> - **「真人手感通过或尚未验收」**: not playtested. The practice game now reads W/A/S/D per key; holding opposing keys feels different from M9 only in the lurch edges (§1.4).

Labels: **[meas]** R5 measurement, **[model]** what the unchanged measured lurch model gives where R5 has no data, **[wiki]** technique-library claim, **[design]** HSD choice.

## 1. D2: per-key direction input

### 1.1 What was wrong

The replay already fed R5's recorded per-key bits (`IN_FORWARD / IN_BACK / IN_MOVELEFT / IN_MOVERIGHT`, `Replayer` builds the lurch edge from new bits of `buttons & 0x618`). The game side did not: `SkillInput` carried only two axes (`forward`, `side`), and `SkillBody.Buttons` rebuilt one key per axis sign. So A+D (or W+S) held collapsed to "no side key": the press of the second key was lost, and releasing one of the pair showed up as a press of the other (M9-A §6: R-1a, R-2 pinned as input-layer gaps). The practice game (`PracticeGame.ReadInput`) and the demo scripts (`MovementDemoScript.InputAt`) collapsed the keys the same way.

### 1.2 Design

- `DirKeys` (flags W = Forward, S = Back, A = Left, D = Right) and `SkillInput.keys`. `SkillInput.WithKeys(k)` sets the keys and the axes they give: forward = W − S, side = D − A (opposing keys cancel in the wish, two axes have equal weight: R5 [meas M8 r_lurch b1, b2]).
- `SkillInput.HeldKeys`: the keys, or for the **legacy axis form** (`keys == None`) one key per axis sign, exactly the pre-M10 bits. Every pre-M10 script and test (`new SkillInput { forward = 1, side = -1 }`) is therefore the same command; only inputs that hold an opposing pair can differ, and the axis form cannot express those.
- `SkillBody.Buttons` sets one usercmd bit per held key (A+D sets both IN_MOVELEFT and IN_MOVERIGHT, as R5 records them). `SkillInput.Resolved()` derives the axes from the keys when keys are set (a caller cannot make them disagree); `SkillBody.Step` and `PracticeSession.Step` run on the resolved input, so the recorded command, the buttons and the motor axes always agree.
- Nothing in the motor changed. The lurch edge stays "a direction-key bit held now and not on the previous command" (`moveKeyPressed`), and the motor lurches on it only with a non-zero wish and in the window (M3 / M6-A1 / M8 rule, unchanged). The airborne check, the window anchors, the clamp and the 1100 cutoff are untouched.
- Practice game: `ReadInput` builds `DirKeys` from the four `TapKey`s (each key keeps its own press latch and wheel-notch queue, M6-A1), so a wheel-bound D tap while A is held is now a real D edge.
- Demo format: `DemoKeys` is unchanged (it always had one bit per key); `InputAt` now passes the keys through `WithKeys`. No pre-M10 demo holds an opposing pair at any command (asserted for every command of every demo at shift 0 and at the failure shift), so every old demo gives the same commands.

### 1.3 What counts as an edge

- A press is an edge; a release never is. With digital keys every new key changes the key-space sum on its axis (−1 → 0 or 0 → ±1), so "a press that does not change the net wish" does not occur; what can happen is a press whose resulting wish is **zero** (A held + D, or W+A+D held + S) or one along the current velocity (a no-op by geometry). The model's rule (lurch toward the resulting wish, none when it is zero) is the measured one: R5 b2 (A held + D: no lurch, |Δv| 3.5–4.2 = air acceleration) and R-1a / R-1b below.
- No lurch capability was added: same window, clamp, cutoff, and the edge set is exactly R5's bit rule (the replay already used it).

### 1.4 Key combinations: measured vs model vs wiki

Sprint jump at 299, edge at 0.10 s (12 commands), Reference. Unity numbers from `InputM10DTests` / `TechniqueM9ATests`.

| Case | R5 | Unity M10-D2 | Wiki | Class |
|---|---|---|---|---|
| A held + D pressed | no lurch, \|Δv\| 3.5–4.2 [meas M8 b2] | no lurch, \|Δv\| ≤ 4.17 | null lurch | measured, agrees |
| A held, W pressed | 45° key diagonal [meas M8 b1] | toward the 45° diagonal | ↗ | measured, agrees (as before) |
| **R-1a** W+A held (running along W+A), D pressed | **−31.9°, \|Δv\| 163.0, ×1.000** [meas M9 r_d1 m9d_r1a] | **−31.9°, \|Δv\| 164.1 (entry 298.5), ×1.000** | "held Left + Forward, pressed Right = ↑" | **measured, agrees** (was "no lurch" before M10-D2) |
| R-1b W+S held, D pressed | −44.7°, ×0.853 [meas] | −44.3 … −44.7° | "held Forward + Back, pressed Right = →" | measured, agrees (unchanged) |
| **R-2** A+D (and W+A+D) held at the jump, D released +2 cmds, mouse turn | R5 ran it (m9d_r2) but the analysis only scores press edges and found none: **no velocity reading** | **no lurch** (only the mouse air strafe) | lurchless air strafe: no lurch | [model]; wiki claim **unverified** in R5 (was a +59.7° lurch before M10-D2) |
| A+D held, W pressed | — | lurch toward W (no turn when already along the view) | — | [model] |
| A+D held, S pressed | — | straight brake 209.3 (+ air accel.) | — | [model] |
| W+A+D held, S pressed / W+S+A held, D pressed | — | zero wish: no lurch | — | [model] |
| Opposing pair held, one released (A+D → A, W+A+D → W+D, W+S → W) | — | no lurch | "releasing a key does not lurch" | [model] (release rule from the wiki / A1) |

Note: the technique library (M9) listed the two wiki three-key examples as untested; the later R5 run m9/r_d1 measured exactly those (m9d_r1a, m9d_r1b). With per-key input the unchanged model reproduces both, so nothing was tuned to the wiki.

## 2. D3: the pad launch and the lurch window

User decision (M10-PLAN): follow R5 where it does not break accepted results. R5 [meas M9 r_d1, 10 trials]: a reverse chain right after a pad launch gives |Δv| 3.3 on every edge (air acceleration on the pad's 0.8 dt) — the launch opens no lurch window; the pad double jump does (M8).

- `JumpPadParams.launchOpensLurchWindow` ([NonSerialized], default true) and `MovementConfig.padLaunchOpensLurchWindow` (Reference **false** [meas], Fun **true** [design]); `MovementConfig.CreateBody` sets it on every pad of the body (the loadout's pad and the map pads); `SkillArbiter.AfterAbilities` skips the window for a pad whose flag is off — the same mechanism as the M8-C lift eject and the M9-B Revenant pounce. The M5 loadout rule `launchOpensLurchWindow` is unchanged (other launches, and bodies built outside a config).
- Config assets: `padLaunchOpensLurchWindow: 0` (Reference) / `1` (Fun); `ConfigAssetsEqualTheFactory` checks it.
- Interactions (tests `PadLurchM10DTests`, real bodies):

| Case | Reference | Fun |
|---|---|---|
| D 0.133 s after the launch (pad_lurch timing) | no lurch, \|Δv\| ≤ 3.3 [meas] | lurch, 209.3 clamp [design] |
| Reverse chain W, W+D, D, S+D, S every 4 cmds right after the launch | no lurch on any edge (R5 m8_pad_chain_g4) | — |
| Octane pad double jump 0.6 s after the launch, A 0.1 s later | lurch (DJ restarts the window, [meas M8]) | lurch |
| Map pad, any loadout (Valk tested) | flag off, no lurch | flag on, lurch |
| Valk on a map pad, Space 0.6 s after the launch, D 0.1 s later | jets take Space, no window → no lurch | the M7-A generic air jump takes Space and opens its own window [design] → lurch |
| `pad_lurch` script on all 6 loadouts | FAIL "no lurch on the press 0.133 s after the launch" | SUCCESS, 24.0° (24.3° Valk) |

- The replay kit and the M4 pad replays are not affected: outside an arbiter no launch opens a window (the motor's launch is not a jump), and the replay has no config.

### 2.1 Moved / affected demos and tests (each listed)

| Item | Change | Reason |
|---|---|---|
| Demo `pad_lurch` (M5.5) | **config 0 → 1 (Fun)**; title gets "（Fun：R5 跳板发射不开 Lurch 窗口，M10-D3）"; script, goal and evaluator unchanged | it is the accepted M5.5 pad → lurch; in the Reference the pad launch no longer opens a window. The verdict text is identical at shift 0 and at the failure shift ("lurch pressed 0.13 s after the launch, inside the 0.5 s window, heading changed 24.0° (≥ 10°)" / "lurch window closed (0.63 s > 0.50 s): no lurch"); the whole trajectory is bit-identical (per-command hash) |
| Demos `m8c_pad_dj`, `m8c_pad_dj_hold`, `m8c_pad_dj_lurch` (Reference, Octane) | none; verdicts identical, trajectories bit-identical | the only difference is the probe's `LURCH_WINDOW_OPEN / CLOSED` display events after the launch (no longer emitted). `m8c_pad_dj_lurch`'s goal text still says "the launch window is closed (0.7 s)": true either way (the tap is past 0.5 s) |
| Station D sign text | "world jump pad → lurch onto the deck (Fun; Reference: lurch after the Octane pad double jump, M10-D3)" | the Reference pad → lurch is gone |
| `TechniqueM9ATests.PadLaunchLurchWindowPinsTheReportedDisagreement` | → `PadLaunchLurchWindowFollowsR5InTheReference` (Reference false, Fun true, M5 rule unchanged) | the pinned disagreement is resolved |
| `TechniqueM9ATests.R1LurchCombos` | R-1a: 0 lurches (gap pin) → 1 lurch −31.9°, \|Δv\| 163 ±2, ×1.000 [meas]; the test body now runs along W+A like R5 | the input gap is closed |
| `TechniqueM9ATests.R2LurchlessAirStrafePinsTheInputGap` | → `R2LurchlessAirStrafe`: 1 lurch +59.7° → 0 lurches (A+D and W+A+D) [model] | same |
| `TechniqueM9ATests.K` helper | builds per-key input | identical for every other key set in that file |
| `PracticeGameTests.ConfigAssetsEqualTheFactory` | + the new config field | config asset |
| `R5MotorM5SkillTests.PadThenLurch` | unchanged, passes | built from the raw loadout (M5 rule, no config) |

No other demo or test changed. The smoke's per-demo lines are identical to the M9-C build (§6).

## 3. Code

- `R5Replay/Runtime/Skills/SkillBody.cs`: `DirKeys`, `SkillInput.keys / Keys / Axes / WithKeys / HeldKeys / Resolved`, `SkillBody.Buttons` per key, `Step` on the resolved input.
- `R5Replay/Runtime/Abilities/ImpulseAbilities.cs`: `JumpPadParams.launchOpensLurchWindow`.
- `R5Replay/Runtime/Skills/SkillArbiter.cs`: the pad exception in the launch window rule.
- `R5Replay/Runtime/MovementConfig.cs`: `padLaunchOpensLurchWindow` (+ factory, `CreateBody`); `Presets/Configs/{Reference,Fun}Config.asset`.
- `Game/Runtime/PracticeGame.cs` (`ReadInput`), `MovementDemo.cs` (`InputAt`, `PadLurch` → Fun), `PracticeSession.cs` (`Step` resolves), `PracticeMap.cs` (station D text).

## 4. Tests

| Suite | Result |
|---|---|
| EditMode | **1529 / 1529** (main 1512) |
| PlayMode | 1 / 1 (the smoke in the game loop) |

New: `R5MotorM10DTests.cs` — `InputM10DTests` (16 key sets: bits, axes, legacy equivalence, `Resolved`; a 30 s random-stream fuzz × 3 seeds × 2 configs: key form vs axis form bit-identical; opposing keys and releases; three-key combinations incl. R-1a / R-1b; the b1 diagonal), `PadLurchM10DTests` (Reference / Fun window, the R5 chain, the pad double jump in both configs, map pads and Valk jets / the Fun air jump). `M10DGameTests` (every demo command equals the axis form and no old demo holds opposing keys; a scripted A+D hold keeps both bits and edges; `pad_lurch` in Fun with the pre-M10 verdict texts and the Reference copy failing).

## 5. Regression (default replay motor; outputs in a scratch folder outside the repositories)

| Set | Baseline | Result |
|---|---|---|
| M2 + M1, R5MotorV2 (`-motor both`) | `m3/unity/regression_m2_m1` | 111 identical |
| M2 + M1 vs the pre-M3 motor | `m2/unity` | 35 / 76, the known M3 set |
| M2 + M1, M1 first guess | `m2/unity/m1_first_guess` | 111 identical |
| M3 (`-motor v2`) | `m3/unity` | 90 identical |
| 38 M4 trials (`-scenarios <abs>/m4/unity/scenarios.json`, `m4_replay_check.py --base m4_replay`) | `m5/unity/m4_replay` | **114 identical**, 0 different, 0 missing (the `m4_pad_*` trials included) |

Why the replays cannot change: `Replayer` builds its usercmds from the recorded buttons and never goes through `SkillInput` / `SkillBody`; the replay kit has no config, so every pad keeps the default flag (true = the pre-M10 behaviour), including the `m4_pad_*` replays.

## 6. Build and smoke

Build: `HSD-Build/M10D/HSD-Practice.exe` (`-executeMethod HSD.Build.BuildWindows -buildPath <abs>\HSD-Build\M10D\HSD-Practice.exe`), exit 0. The re-serialised `ProjectSettings/ProjectSettings.asset` and `Scenes/Practice.unity` were reverted; `git diff --stat --ignore-cr-at-eol main` equals the plain stat (16 files, +460 / −34); no CR in the committed .cs blobs.

```
[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset;
events seen 18; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s; demos 170/170 verdicts as expected (85 SUCCESS at shift 0, 85 failure
cases FAIL; M5.5 12/12, M6 8/8, M6-C 14/14, M6-B 14/14, M7-A 22/22, M8-A 12/12, M8-B 28/28, M8-C 16/16, M9-B 14/14, M9-A 16/16,
M9-C 14/14); course lap 80.82 s (7/7 checkpoints, Reference (R5 calibration)); feedback snapshot ok (26 fields, 2109 bytes); 92294 commands in total
```

Headless `-batchmode -nographics -smoke 12`, exit 0. The M5.5 route ends where it did (the route uses no pad lurch in the Reference: its per-command trajectory hash is unchanged in both configs). Every demo line (340) is identical to the M9-C build's smoke output, `pad_lurch` included (now Fun, same text). No verdict changed.

## 7. Open gaps

- R-2 has no R5 velocity reading (the r_d1 analysis scores press edges only); the "no lurch on release" result is [model] + wiki.
- The other three-key and opposing-pair cases in §1.4 are [model] (R5 untested); the b1 one-step residual (11.6 u/s, M8) stays unexplained.
- The usercmd's first-command 0.5 axis ramp that R5 shows on a new key is not modelled (the wish uses the keys; M8 b1 showed the keys, not the ramp, set the lurch direction).
- Analog / gamepad movement is not represented per key (the legacy axis form still accepts analog axes; no lurch edge comes from a stick).
- Pad launch: only the "no window" rule is taken from R5; Octane's other pad interactions (ceiling surf, upgrades) are M10-C.
- Every [design] value (Fun pad → lurch, Fun air jump window) is 「真人手感未验收」.
