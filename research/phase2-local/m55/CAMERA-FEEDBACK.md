# M5.5 part A: first-person camera feedback and HUD modes

HSD-Unity branch `m55/feedback` (from main `a85a0ea`). Code:

- `Assets/HSD/Game/Runtime/CameraFeedback.cs`: smoother, settings, design values, the camera layer, and the M5 camera kept as
  `LegacyCamera`.
- `Assets/HSD/Game/Runtime/CameraRig.cs`: aim pivot / visual rotation, the aim point and the crosshair projection.
- `PracticeGame.cs`: camera rig, HUD modes, settings menu, PlayerPrefs.
- `PracticeSession.cs`: a read-only per-command observer, timed events, and the input bits of recent commands.
- Tests: `Assets/HSD/Game/Tests/Editor/CameraFeedbackTests.cs` (30 tests) and the PlayMode smoke (extended).

Everything here is a visual layer. It is not an R5 measurement. The only R5 numbers it uses are thresholds it reads: the slide stop
and peak speeds, and the landing-slowdown onset.

## 1. Architecture and the decoupling argument

```
mouse ──► PracticeGame.Yaw/Pitch ──► SkillInput ──► SkillBody / R5MotorV2 / abilities   (120 Hz commands, unchanged)
                                         │                        │
                                         │         PracticeSession.OnCommand(session, input)   (after the step, read-only)
                                         ▼                        ▼
                        AimPivot.rotation = AimRotation(Yaw, Pitch)   CameraFeedback.Observe ──► queue of targets/kicks
                                         │                                          │
                         Camera (child): localRotation = (pitchKick, 0, roll)  ◄── CameraFeedback.Update(renderTime)
                                         position = eye + kicks + lag, FOV            (per rendered frame)
```

- **One-way data flow.** The command loop does not know about the camera.
  - `OnCommand` is called after `Body.Step`, the event log and the checkpoints are complete.
  - `Observe` only reads the motor, the abilities, the arbiter slots and the events.
  - `Update` only writes the camera's own smoothers.
  - `PracticeGame` writes the result only to the aim pivot, the camera transform, `Camera.fieldOfView` and the crosshair position.
    `Yaw`/`Pitch` are written by the mouse only, as in M5.
- **Command timing is unchanged.** `Advance`/`Step` are unchanged apart from the observer call after the step.
- **Aim and visuals are separate.**
  - The aim pivot carries only the raw aim (`Quaternion.Euler(pitch, −yaw, 0)`).
  - The visual pitch kick and roll sit on the camera, which is a child of the pivot.
  - The visual offsets never reach `SkillInput`. The grapple aim ray, pounce, lift-eject heading and lurch use the input yaw/pitch,
    exactly as before.
- **Crosshair.**
  - A roll about the view axis does not move the screen centre.
  - The pitch kick (at most ~2° default, 4° at max) and the small position offsets would. So the crosshair is not drawn at the
    screen centre. It is drawn where the *nominal* aim ray lands in the visual camera.
  - The nominal aim ray starts at the nominal eye (origin + eye-height channel, no kicks or lag) and runs along the aim direction to
    its first world hit, or 4000 u.
  - With feedback off it is centred, as in M5.
  - The grapple's own ray origin is still origin + 60 u (M4b assumption). This is unchanged and is not a camera matter.

### How the tests prove it (`CameraFeedbackTests`)

| Requirement | Test | What it checks |
|---|---|---|
| (a) bit-identical simulation | `FeedbackAtMaxIntensityLeavesTheSimulationBitIdentical` (2 configs × 3 loadouts) | Two sessions get the same jittered 144 fps frame pattern. One has the camera attached at **max** settings and updated every frame; the other has no camera. Script: 30 s practice route, then a corridor wall approach (wall-run in the fun config), a slide on the lane plus every slot fired while the aim sweeps, and a hard drop. After **every command** the test compares a dump of every scalar field (doubles as raw bits). This covers the motor (public and private), every ability, every arbiter slot, the wall contact, the events, the input and the checkpoints. The same test asserts that the camera was really active: FOV > base + 8°, dip < −5 u, slide roll > 3°, and in the fun config wall-run tilt > 10°. |
| (a) settings | `CameraSettingsDoNotReachTheSimulation` | Default, off and max settings give the same per-command log as no camera. |
| (b) physics aim | `PhysicsAimIsTheRawAimDuringRollTiltAndDips` (both configs) | Same two sessions at 60 fps. The per-command input yaw/pitch are bit-identical, as are the grapple hit point / target and every other aim-dependent state; the grapple was fired. Every frame's pose returns the raw aim bit for bit. There are > 10 frames with slide roll > 1°, > 5 with a dip, > 5 with a pitch kick > 0.2°, and in the fun config > 10 with wall-run tilt > 5°. The aim pivot's forward is the physics aim direction (< 0.01°). The crosshair, unprojected through the visual camera, passes through the aim point (< 1 mm per m). |
| crosshair math | `PoseReturnsTheRawAimAndRollAloneKeepsTheCrosshairCentred`, `ViewportMatchesTheUnityCamera` | Roll only gives the screen centre; a pitch kick moves the crosshair. The projection equals `Camera.WorldToViewportPoint` (1e-4). |
| PlayMode | `SmokeRunCompletesWithoutErrors` | In play mode the camera is a child of `AimPivot`, and every frame the pivot rotation equals the pose's raw aim (< 0.01°). The camera runs at max settings during the smoke. |
| (c) replay motor | regression (§6) | Byte-identical. |
| (d) old tests | all | 174 + 1 unchanged, all pass. |

## 2. The smoother

`CriticalSmoother` is a critically damped second-order filter, written as two cascaded first-order lags with the same rate ω:

    stage' = ω (target − stage),   value' = ω (stage − value)

- **Exact step for a constant target:**
  - `a = e^(−ω dt)`
  - `value ← T + ((value − T) + ω dt (stage − T)) a`
  - `stage ← T + (stage − T) a`
- **No overshoot, by construction.** The new value is a convex combination of T, stage and value. The weights are
  `1 − (1 + ω dt) a`, `ω dt a` and `a`, all ≥ 0. So the output never leaves the range of the targets it has seen, for any target
  sequence or any change of ω. There is no bounce and no ringing. A step from rest reaches 90 % at `t = 3.8897 / ω`; this sets the
  per-channel response time ("settle90").
- **Kicks.** A kick adds K to the first stage only. From rest the output is `K ω t e^(−ωt)`: a single bump that peaks at K/e at
  t = 1/ω and returns to the target without crossing it. Kicks of the same sign keep the bump one-sided (`stage − value` keeps its
  sign). Kicks are used on separate zero-target channels, each with one sign (lift +, dip −).
- **Frame-rate independence.**
  - `Observe` stamps each command's targets and kicks with the command time `k·dt`.
  - `Update(renderTime)` advances the smoothers through the queued commands in time order and then to the render time
    `(Commands − 1 + alpha)·dt`. That is the time of the interpolated render position.
  - The targets are therefore piecewise constant on the 120 Hz grid and each segment is integrated exactly, so any frame rate
    gives the same channel values (up to rounding).
  - The body-inertia lag target is also fixed per command. A first version recomputed it inside each frame segment and depended
    on the frame rate (test failed at 144/240 Hz by 0.01 u). It was moved to the command grid.

Smoother tests:

| Test | Result |
|---|---|
| `StepResponseHasNoOvershootAndSettlesMonotonically` (settle 0.05 / 0.1 / 0.35 s) | Overshoot 0 (≤ 1e-12), monotonic, 90 % at the settle time (±0.2 ms). From a start moving the wrong way, overshoot ≤ 1 %. |
| `RandomTargetsAndRatesNeverLeaveTheirRange` | 20 000 random targets, rates and dt: always inside [min, max]. |
| `KicksAreOneSidedBumps` | Peak −4.000 at 0.060 s, never above 0 with repeated kicks, settles to 0. |
| `SmootherIsFrameRateIndependent` (30 / 60 / 144 / 240) | Equal to the 120 Hz grid within 1e-9 at every 1/6 s. |
| `CameraIsFrameRateIndependent` (30 / 60 / 144 / 240) | The whole camera on the 10 s practice route at max settings: all 11 channels (eye, roll, FOV extra, lift, dip, pitch kick, 3 lag axes, streak, FOV) agree within 1e-7. |
| `SteadyMovementHasNoBobOrShake` | Steady sprint: FOV varies < 0.05°, eye < 1e-6 u, no roll, kicks or dips. There is no procedural bob. |

## 3. Channels and design values

All values are in `CameraFeedbackDesign`. Units: SOURCE u, degrees, seconds. "Settle" is the 90 % step time; "peak" is the time
from a kick to its peak. Every response time is multiplied by the **response** setting.

### Eye height above the body origin

| State | Value | Source |
|---|---|---|
| Stand | 60 u | M5 camera; equals the grapple aim-ray height (M4b assumption, not measured) |
| Crouch | 38 u | M5 camera (design) |
| Slide | 38 − 6·height intensity = 32 u | design |

- Driven by the motor's own state: `sliding`, then `ducked` (duck held on the previous command, the motor's flag) or
  `hullCrouched` (reference-config duck hull).
- Going down settles in 0.10 s; going up in 0.24 s.

### Roll (+ = lean left)

| Source | Value |
|---|---|
| Wall-run | ±10°·roll intensity, away from the wall (M5 value and rule) |
| Slide | +3°·roll intensity |
| Strafe lean | −side·1.5°·roll intensity·min(1, v_h/300), not while sliding or wall-running |

- Roll in settles in 0.16 s, roll out in 0.30 s.
- Wall jump / wall-run jump: a 2.5° roll kick away from the wall (peak 0.08 s).

### Position and pitch kicks

| Event | Lift / dip | Pitch |
|---|---|---|
| Takeoff | +1.0 u | −0.4° (up) |
| Slide jump | +2.5 u + FOV kick 2° | −0.4° |
| Wall jump | +1.5 u + FOV kick 2° | — |
| Launch (pad, pounce, lift eject; `mods.hasLaunch`) | +2 u + FOV kick 7° | — |
| Jets on | +1 u | — |
| Gravity switch | ±1.5 u (lighter up, heavier down) | — |
| Landing | −4 u·k | +0.8°·k (down) |
| Hard landing (triggers `LAND_SLOW`) | −8 u | +2.0° |

- Landing: k = clamp((|vz| − 150) / (772 − 150), 0, 1), where |vz| is the impact speed from the previous command.
- 772 u/s is where the measured landing slowdown starts (f0 = 1.996467 − 1.6714e-6·vz² < 1, octane §4).
- Peaks: lift 0.07 s, dip and pitch 0.06 s.
- All kicks scale with the height/dips intensity.

### FOV (vertical, Unity `fieldOfView`)

`base + fov intensity · (speed + slide + sustained) + kicks`. The total extra is clamped to 22°·FOV intensity.

- **Base:** 70°, the M5 value. Setting range 55–100.
- **Speed:** +8°·clamp((v_h − 200) / (700 − 200)).
- **Slide:** +3°·clamp((s − 125) / (460 − 125)). 125 and 460 are the measured slide stop and peak speeds, so the FOV decays with
  the measured slide speed.
- **Sustained:** grapple pull +4°, stim / Wraith phase effect +3°, jets +2°, flight +3°, lift ride +2°.
- **Kicks:**
  - slide start +4° (resumed slide on landing +2°)
  - slide jump +2°
  - launch +7°
  - wall jump +2°
  - wall-run start +1.5°
  - grapple pull start +2°
- **Timing:** settle 0.35 s, kick peak 0.09 s.

### Body inertia

- A smoothed velocity v_s (settle 0.12 s) follows the body velocity.
- At each command the lag target is `(v_s − v)·0.006 s·inertia intensity`, clamped to 1.5 u·intensity (3.8 cm at 1).
- The lag itself is smoothed again (settle 0.06 s), so there are no steps at command edges.
- Effect: the eye trails a sharp acceleration or braking by a few cm. The vertical part adds to the landing dip.

### Speed streaks

- A non-HUD cue: thin radial streaks at the screen edge.
- Alpha = 0.5·clamp((|v| − 330) / (650 − 330)), using the 3D speed, smoothed with settle 0.25 s.
- A procedural texture, toggleable.

### Coverage by state

| State | Cue |
|---|---|
| Sprint | Speed FOV |
| Slide start / sustain / end | Eye drop, FOV kick, roll in / low eye, slide roll, FOV tied to the measured speed / eased rise (0.24 s), roll out (0.30 s) |
| Jump / takeoff | Lift, small pitch up |
| Landing soft / hard | Scaled dip + pitch / strong dip + pitch |
| Wall-run (fun) | Tilt away from the wall, FOV kick |
| Wall bounce | Roll kick, lift, FOV kick |
| Grapple pull | FOV kick + sustained |
| Pad / lift launch | Launch kick; lift ride sustained |
| Jets | Lift + sustained FOV |
| Flight (fun) | Sustained FOV |
| Gravity switch | Lift or dip |

### Slide feedback (`SlideStartSustainAndEndAreFelt`, `SlideJumpIsADistinctTakeoff`)

Sprint, then a slide with duck held, default settings:

- **Start:** the eye is below the crouch eye within 0.15 s; the FOV kick peaks > 3.6°; the roll is at 3° by 0.6 s.
- **Sustain:** the FOV falls at every 0.1 s step from 0.6 s until the slide ends, as the measured speed decays.
- **End:** the eye rises monotonically to 60 u with no overshoot, and the roll returns to 0 without crossing.
- **Slide jump:** the lift peak is more than twice a plain jump's, plus a ≥ 1.5° FOV kick.

`LandingDipScalesWithTheImpactAndHardLandingsDipMore`: a standing hop dips 0.2–2 u. An 800 u/s drop triggers `LAND_SLOW` and dips
≥ 7.6 u with a ≥ 1.5° pitch. The dip never goes positive.

## 4. Settings (Esc menu, PlayerPrefs `hsd.m55.*`)

- **Controls:**
  - Feedback ON / OFF.
  - Intensity sliders 0–2 for the FOV, roll / tilt, height / dips and inertia groups.
  - Base FOV 55–100.
  - Response time × (0.5–2).
  - Speed streaks.
  - Presets: **Default** and **Off (M5 camera)**.
- **Persistence:** saved on change. Mouse sensitivity is now saved too. Reads and writes are wrapped in try/catch; a failure falls
  back to the defaults and only logs a warning.
- **Off preset:**
  - Feedback off, FOV 70, streaks off.
  - Runs `LegacyCamera`, the M5 `LateUpdate` code moved unchanged: eye 60/38 lerp at 12/s, wall-run roll ±10° at 8/s.
  - Sets the camera's world position and rotation exactly as M5 did, and centres the crosshair.
  - `OffPresetIsTheM5Camera` checks LegacyCamera against a verbatim copy of the M5 code on a 12 s fun-config run (exact equality).
  - Because the camera is now parented, its world transform passes through the pivot. That adds float rounding of ~1e-7 m.
- `IntensityZeroAndFovSettingsBound`: intensity 0 removes the group's feedback exactly; Clamp bounds every setting.
- The smoke run (`-smoke`) always uses the max settings.

## 5. HUD modes (F3 toggles; default = normal)

- **Normal:**
  - Config and loadout in one line.
  - Bottom left: the speed number with km/h and a 0–900 u/s bar, with marks at walk 199.5, sprint 299 and slide peak 460.
  - Stance (SLIDE / sprint / crouch / air).
  - One box per slot: key, ability, a cooldown fill that drains, charges, and a state stripe (Pending yellow, Driving cyan,
    Effect green).
  - Jets and flight fuel bars; gravity level and wall-run when active.
  - Time trial and help line as before.
- **Diagnostic:**
  - The full M5 HUD, unchanged.
  - A right-hand panel:
    - session time / command
    - pos / vel
    - motor flags: ground, slide, duck, sprint, hull-crouch, wall-run
    - cap and slide boost
    - lurch window: open / closed, lam, time left, last lurch t / lam / |D|
    - every arbiter slot (base layer included) with Idle / Pending / Driving / Effect and charges / cooldown
    - input bits of the last 8 commands (letters + hex)
    - the last 10 events with session timestamps
    - camera channels: eye, roll, pitch kick, FOV and its extra / kick, lift, dip, lag, streak, last cue with its time
- **Help line:** now lists F3.
- **For the playtest guide:** add `F3 = HUD 普通 / 诊断` and the Esc camera settings.

## 6. Regression and build check

| Check | Result |
|---|---|
| EditMode | **204 / 204** (174 existing + 30 new) |
| PlayMode | **1 / 1** |
| M2 + M1, R5MotorV2 vs `m3/unity/regression_m2_m1` | **111 / 111** identical |
| M1 first guess | 111 / 111 |
| M3 vs `m3/unity` | **90 / 90** |
| sha256 | M2+M1 `9abd1885…6c0f4`, M3 `e7743c78…c9ee9c95` (equal to M4 / M5) |
| 38 M4 replays vs `m5/unity/m4_replay` (`m4_replay_check.py --base m4_replay`) | **114 identical, 0 different, 0 missing** |
| Build `HSD.Build.BuildWindows -buildPath <workspace>/HSD-Build/M55a-check/HSD-Practice.exe` | Succeeded, 0 errors, 0 warnings, 91 MB (outside both repos) |
| Headless smoke of that build (camera at max) | `[HSD-SMOKE] ok: 1441 commands … final pos (341.586, 146.165, 10) \|v_h\| 92.0 u/s`, exit 0. **Identical to the M5 smoke line.** |

- The pre-M3 row (`m2/unity`: 35 identical, 76 different) is the known M3 change set, unchanged.
- The build's default output folder is `<HSD-Unity>/../HSD-Build`. `-buildPath` overrides it, and a path inside the project is
  refused.
- The build regenerates `Practice.unity` and rewrites the config assets and ProjectSettings. Those were line-ending or ID-only
  changes and were reverted; they are not committed.

## 7. Known limits

- All feedback values are design choices, tuned by reasoning rather than by a playtest. They need the user's playtest.
- The pitch kick moves the screen centre off the aim. The crosshair compensates, so it can move by a few pixels on a hard landing.
  This is intended and the crosshair stays truthful, but some players prefer a fixed crosshair. Setting height intensity to 0
  removes the pitch kick.
- The FOV is vertical (Unity). An Apex "FOV 90" setting is horizontal.
- Visual only:
  - no weapon or hand model, no head bob, no audio
  - no camera collision: the eye can clip into a wall by the lag (≤ 1.5 u) or a kick
  - no motion-sickness options beyond the intensity sliders and the off preset
- Wall-run, wall-jump and gravity cues exist only where those mechanics exist (fun config, wall contact). Mantle and climb are
  still not in the game.
- Landing |vz| is the previous command's post velocity. A landing on the first command after a body rebuild (config or loadout
  switch) gets no dip.
- In the M5-style off mode the camera is now parented to the pivot, so its world transform matches M5 to float rounding, not
  bit for bit.
