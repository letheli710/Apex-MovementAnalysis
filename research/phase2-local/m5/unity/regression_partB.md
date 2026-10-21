# M5 part B: regression, tests, build

Build: HSD-Unity branch `m5/skill-slots`, commit `8480b2d` (on top of part A `b23916c`), Unity 6000.6.5f1. Every run below used
that commit. Absolute paths are passed to Unity; outputs of the regression runs stay outside the repositories.

## 1. Default replay motor: byte-identical

Same commands as part A ([regression.md](regression.md) §1–2).

| set | baseline | identical | different | missing |
|---|---|---|---|---|
| M2 + M1 trials, R5MotorV2 reports | `../../m3/unity/regression_m2_m1` | 111 | 0 | 0 |
| M2 + M1 trials, M1 first guess | `../../m2/unity/m1_first_guess` | 111 | 0 | 0 |
| M3 trials, R5MotorV2 reports | `../../m3/unity` | 90 | 0 | 0 |
| 38 M4 trials with `-scenarios` | `m4_replay/` (part A publication; `python m4_replay_check.py <new> --base m4_replay`) | 114 | 0 | 0 |

- sha256 (`../../m4/unity/regression_check.py --write`): M2 + M1 `9abd1885c214c4a7bb431927aa595cd0e1c369ad3a76a21f45c986378fb6c0f4`,
  M3 `e7743c7840a2139f6b182bfb38decae34b1a6425c7a3dab5c081603f59ee9c95` — equal to part A and M4.
- Against the M4 publication (`../../m4/unity`) the result is unchanged from part A: 102 identical, 12 different (the 4 grapple
  trials, RF model).
- **Why it is unchanged.** The new motor options (`groundVectorRedirect`, `airUnduckDrop` and its two timing fields) default to
  off and are left out of the parameter report while off, like `lurchClampSprintFraction` in M4. `Replayer.Replay(trial, motor)`
  calls the new hooked overload with a null hook. `AbilityScenario.Build/MotorFor` take an optional preset that defaults to the
  old behaviour. An EditMode test checks that the default parameter report has none of the new keys.

## 2. Tests

| Platform | Result | New in part B |
|---|---|---|
| EditMode | **174 / 174 pass** (part A's 144 unchanged + 30 new) | see below |
| PlayMode | **1 / 1 pass** | `SmokeRunCompletesWithoutErrors`: the MonoBehaviour in play mode builds the map visuals and camera and runs the 11 s scripted smoke (config and loadout switches, a checkpoint reset) |

New EditMode classes (`Assets/HSD/Game/Tests/Editor/PracticeGameTests.cs`):

| Class | n | What it checks |
|---|---|---|
| MovementConfigTests | 3 | Config assets equal the factory; the reference turns on the measured options and the default motor stays off (no new report keys); `Apply` leaves the preset untouched, adds the fun traits, keeps the 900 u/s ceiling |
| ReferenceModelTests | 4 | Vector redirect equals the M2 rule bit for bit when aligned; a sideways landing turns at 1250 / 517.5 u/s²; over-speed decays at 1250 and the cross component dies; the un-duck drop happens once, 9 commands (≥ 0.08 s) after the takeoff, 16.5 u, and not at all by default |
| ShortRangeEvalTests | 1 | Windows tile the whole trial (every row once, durations sum to the trial), window 0 equals the plain replay |
| FunAbilityTests | 4 | Wall-run holds the body up (gravity ×0.15) and jumps off along the normal, absent in the reference config; flight toggles, climbs, drains fuel, lands; gravity switch keeps the takeoff speed and scales the apex (56 → 124 → 35 u, back to ×1 exactly); the fun session has the features and the reference session does not |
| PracticeSessionTests | 18 | Map sanity (spawn in the start ring, respawn points on their floor and free, fixtures free); **the same commands at 30/60/75/144/240 fps with ±20 % frame jitter give bit-identical state** (fixed 120 Hz command rate); accumulator, interpolation and the 12-command hitch cap; config and loadout switches keep position and velocity; checkpoints in order, out-of-order ignored, reset to checkpoint (position, zero velocity, clock running), finish time and best time, restart; 30 s scripted run on the map for both configs × three loadouts with invariants every command (finite, ceilings, not below the floor, not inside a wall, on the map); the world jump pad carries a walking player onto the mid deck and the world lift ejects onto the tower-top checkpoint ring, for every loadout |

## 3. Windows build and headless smoke

```
Unity.exe -batchmode -nographics -projectPath <HSD-Unity> -executeMethod HSD.Build.BuildWindows -logFile <log>
    → <workspace>/HSD-Build/HSD-Practice.exe   (default: <HSD-Unity>/../HSD-Build; a path inside the project is refused)
HSD-Practice.exe -batchmode -nographics -smoke 12 -smokeOut <file> -logFile <log>
```

- Build: succeeded, 0 errors, 0 warnings, 91 MB (Mono, x64). Output folder `HSD-Build` next to the two repositories (not in git).
- Smoke (headless): exit code 0, no player process left afterwards:

  `[HSD-SMOKE] ok: 1441 commands (12.01 s at 120 Hz) in 1039 frames; configs/loadouts switched config0,config1,loadout1,loadout2,reset; events seen 17; final pos (341.586, 146.165, 10) |v_h| 92.0 u/s`

  The smoke advances uneven frames (60 / 144 / 90 Hz pattern) through the accumulator, drives the scripted route
  (`ScriptedInput.PracticeRoute`: sprint, slide, slide jump, lurch, hops, all slot buttons, flight, gravity), switches to the fun
  config at 3 s, loadouts at 5 s and 7 s, resets to the checkpoint at 9 s and back to the reference at 10 s, and checks finite
  state, the speed ceiling, the floor and the map bounds every frame. Two runs gave the same final state.
- A windowed smoke run with `-smokeShot` wrote screenshots at 1.5 s and 6.4 s: the map, HUD and labels render with the built-in
  Standard material (no missing shaders).
