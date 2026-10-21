# M5 part A: replay and regression with the skill-slot build

Build: HSD-Unity branch `m5/skill-slots` (Unity 6000.6.5f1). Every run below used the final build of the branch. Pass absolute
paths to Unity; relative ones resolve against the Unity project folder.

## 1. Default motor and M2/M1, M3 regression: byte-identical

```
Unity.exe -batchmode -quit -projectPath <HSD-Unity> -executeMethod HSD.R5Replay.Editor.BatchReplay.Run \
    -trial <abs>/m2/trials/<each> -trial <abs>/m1/trials/<each> -out <scratch>/m2m1 -motor both -logFile <log>
Unity.exe ... -trial <abs>/m3/trials/<each> -out <scratch>/m3 -motor v2 -logFile <log>
python ../../m4/unity/regression_check.py <scratch>/m2m1 <scratch>/m3
```

The outputs are kept outside the repo, as in M4.

| set | baseline | identical files | different | missing |
|---|---|---|---|---|
| M2 + M1 trials, R5MotorV2 reports | `../../m3/unity/regression_m2_m1` (main) | 111 | 0 | 0 |
| M2 + M1 trials, M1 first guess | `../../m2/unity/m1_first_guess` | 111 | 0 | 0 |
| M3 trials, R5MotorV2 reports | `../../m3/unity` | 90 | 0 | 0 |
| M2 + M1 trials vs the pre-M3 motor | `../../m2/unity` (R5MotorV2/m2) | 35 | 76 | 0 |

- The last row is the known M3 change set, unchanged from the M4 note: `../../m4/unity/regression.md`.
- sha256 of the outputs (CRLF → LF for .md/.json, index.md excluded) equals the M4 regression hashes:
  - M2 + M1 `9abd1885c214c4a7bb431927aa595cd0e1c369ad3a76a21f45c986378fb6c0f4`
  - M3 `e7743c7840a2139f6b182bfb38decae34b1a6425c7a3dab5c081603f59ee9c95`
- **Why the default motor is unchanged.** The M5 code runs only through the ability set:
  - The arbiter is null outside a loadout.
  - Boosts and launches go through the set, which with no arbiter applies them exactly as M4 did: product of the factors, last
    launch wins.
  - The new parameter fields (stim deploy phase, pounce auto-fire) are neutral by default and left out of the reports while off.
  - The EditMode test `EmptyKitIsBitForBitThePlainMotor` still passes.

## 2. The 38 M4 replays (`m4_replay/`)

```
Unity.exe ... -trial <abs>/m4/trials/<each, not *_REJECTED> -out <abs>/m5/unity/m4_replay -motor v2 \
    -scenarios <abs>/m4/unity/scenarios.json
python m4_replay_check.py
```

**Result: 102 files identical and 12 different.** The 12 are steps.csv, summary.json and report.md of the 4 grapple trials
(`hold_r1701/r1702`, `near_r2101/r2102`); that change is expected.

- Every stim, pad, lift, jets, pounce and control trial is byte-identical to the M4 publication.
- The grapple summaries differ in the trajectory metrics, `parameters`, `parameter_provenance` and `model_choices` (the RF
  model). The sim events also changed: `GRAPPLE_RELEASE` became `GRAPPLE_RELEASE_SCHEDULED`.
- As in M4, the replay releases the pull on the recorded detach command (`scenarios.json`), so the pull law is compared on the
  same window. For this run the envelope rule is switched off in the scenario.

### Grapple pull window, before (M4 F1) vs after (M5 RF): `python grapple_compare.py` → [grapple_compare.md](grapple_compare.md)

The window runs from the reference pull start to the recorded release. Errors are sim − ref. The "before" run is the published
M4 output (`../../m4/unity/<trial>/steps.csv`).

| trial | pull-window pos RMS 3D: plain / F1 / **RF** (u) | pos RMS horizontal F1 → RF | vel RMS F1 → RF (u/s) | vel error at release F1 → RF | velocity direction error at release F1 → RF |
|---|---|---|---|---|---|
| hold r1701 | 179.9 / 7.39 / **7.54** | 2.57 → 7.27 | 35.9 → 17.9 | 99.5 → 31.3 | 9.2° → 2.5° |
| hold r1702 | 180.2 / 6.53 / **10.32** | 2.30 → 10.23 | 34.0 → 18.9 | 97.1 → 29.5 | 9.0° → 2.5° |
| near r2101 | 113.6 / 3.76 / **10.17** | 1.49 → 9.08 | 26.7 → 21.8 | 73.9 → 8.4 | 8.9° → 0.4° |
| near r2102 | 113.8 / 3.91 / **10.46** | 1.61 → 9.30 | 26.3 → 22.4 | 73.3 → 7.9 | 8.8° → 0.5° |

**What got better.** The velocity, and above all the direction at release:
- F1 left 73–100 u/s of velocity error at the release, the known late upward curvature (M4 index notes).
- RF leaves 8–31 u/s, and the heading is within 0.4–2.5°.
- This is the momentum the player keeps after the release.

**What got worse.** The position RMS over the pull: 3.8–7.4 → 7.5–10.5 u. Causes, read from the per-step trace:
1. **The first pull commands.**
   - R5 has a 1662 u/s² burst for 4 commands (M4 lift_grapple §2.1). RF starts at its own ramp, so the sim falls behind by
     about 2.6 u in the first 15 commands.
   - The RF fit begins 2 commands after the pull start (SWING `c_segment`), so the burst was never part of it.
   - Adding the M4 burst in front of RF was tried. It made things worse: the hold release went from 4 u to 26 u ahead and
     +40 u/s fast, because RF's along-rope A = 541 already absorbs it. It was removed; nothing else was tuned.
2. **The joint A = 541 is above these trials' ramp.**
   - Measured: 502 u/s² on hold, 494.5 along the rope (SWING §6: A trades off against H and s).
   - So the sim ends 6.5–16.5 u/s faster at the release.
3. **F1 was fitted on these five M4 geometries.** RF is the single joint set for all 62 no-input trials, cross trials included.
   - SWING reports RF open-loop on these conditions from the recorded state 2 commands into the pull: hold 5.1 u, near 8.0 u.
   - The full replay here also carries the attach, wind-up and pull-start timing: the sim pull starts 1 command early in
     r1701.

Attach and pull-start steps are as in M4: attach 0/0/0/0 commands off, pull start −1/0/0/0.

### Detach envelope instead of the recorded release (`grapple_envelope/`, `scenarios_envelope.json` from `make_envelope_scenarios.py`)

Release: the first pull command that starts within 34.1 u of the hooked face (SWING §4 envelope).

| trial | recorded release | envelope release | Δ | R5 gap at the start of the release command |
|---|---|---|---|---|
| hold r1701 | 244 | 246 | +2 | 36.1 u |
| hold r1702 | 243 | 246 | +3 | 35.3 u |
| near r2101 | 201 | 205 | +4 | 33.5 u |
| near r2102 | 201 | 205 | +4 | 32.5 u |

The envelope releases 2–4 commands late. R5 released 32.5–36.1 u from the face. At that moment the sim is behind R5 (position error 4–16 u at the recorded release), and
it releases at 34.1 u. The R5 detach rule stays unidentified.

## 3. EditMode tests: 144/144 pass

The 99 existing tests had 5 F1 grapple tests. Those are replaced by 9 RF grapple tests. There are 41 new skill tests.

| Class | n | What it checks |
|---|---|---|
| GrappleTests | 9 | Eye-height aim and timing; hop in the air; RF step terms (along-rope A, cross brake C, cross-rope gravity, wish 575 u/s² and the 483.000 clamp); cross speed braked, not swung (dip, then growth); no terminal speed; v·ŵ = 483 while v_h > 533; envelope release, 0.5 s timeout, a miss spends nothing; jump does not release |
| SkillLoadoutTests | 4 | Presets valid with 3–4 slots; invalid loadouts rejected; preset assets equal the factory; slot buttons rebound on parameter copies (reference parameters untouched); pounce auto-fire; Horizon has no landing slowdown |
| SkillCooldownTests | 3 | Stim cooldown plus its own reuse lockout; pad 15 s recharge on the exact command; grapple 2 charges recharging one at a time; a miss spends no charge |
| SkillWorldTests | 3 | Wall stops the hull at the face with contact; walk off the 128 u ledge, fall and land; the ledge side is a wall from below |
| SkillComboTests | 11 | grapple release → slide → slide jump; pad → lurch (and off when the rule is off); stim + pad; boosts don't stack; jets + grapple; lift + grapple; pad ends a lift ride; wall jump → pounce; portal lock and refusals, Loba zero velocity, teleport cancels a pending hook and is clipped by the wall; ceiling clip; contact ends the pull |
| SkillFuzzTests | 17 | 3 presets × 5 seeds at 120 Hz, plus all presets at 60 and 144 Hz. 30 s of random input with invariants every command: finite state, \|v_h\| ≤ 900, vz ≤ 1100, ≤ 1 driver, no state past its timeout, hull outside walls, not below the floor. After 12 s idle everything is Idle and grounded. Per run each ability was used 0–17 times (more than 3 uses per run in total) and refused 0–23 times; no timeout and no ceiling clip was needed. |
| SkillFrameRateTests | 3 | One combo script per preset at 60 / 120 / 144 Hz, state at each second. Tolerance: 3 events × one 60 Hz command (15 u at 900 u/s; 20.8 u/s at 1250 u/s²) + 2 % of the path. |

Frame-rate results, largest difference over the 5 checkpoints (vs 120 Hz):

| preset | 60 Hz position / velocity | 144 Hz position / velocity |
|---|---|---|
| Pathfinder-Octane (pad, stim, lurch, grapple, slide) | 37.0 u / 34.7 u/s | 4.1 u / 4.5 u/s |
| Valk-Horizon (lift, jets) | 30.2 u / 11.6 u/s | 9.0 u / 4.2 u/s |
| Revenant-Wraith (phase, slide, pounce, portal) | 3.2 u / 3.1 u/s | 1.3 u / 3.6 u/s |

**Honest note on the tolerance.** The first version of this test assumed every event moves by at most half a command (true for
scheduled times, `AbilityTiming.Due`). It failed at 60 Hz with 34.7 u/s > 31.3 u/s:
- The pad trigger is a spatial test at command starts, so it moves by up to a whole command. Here it fired 9 ms earlier at 60 Hz.
- That changed the lurch weight (time since the launch), and through it the grapple's aim point 1 s later.

The derivation was corrected to a full command for spatial triggers (pad, lift, landing, contact), which is the real bound.
The 60 Hz numbers above are reported as they are. For the game, run the motor at a fixed command rate (M3 advice); then the
render frame rate does not enter.

## 4. Not reproduced or not exercised

- **Grapple.**
  - The detach rule (envelope 2–4 commands late on these trials).
  - The 4-command burst.
  - The wall impact / hang / climb after the release: the replay has no wall.
  - W, wall contact and the cross brake are covered by unit tests only: the W trials were rejected in M4, and the M4b swing
    trials are not in the Unity trial set.
- **Combos.** Pad → lurch, wall jump → pounce, lift → grapple and the other combos have no R5 recording. They are rules (design)
  and tests, not replays.
