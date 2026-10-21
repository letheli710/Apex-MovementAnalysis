# M4 regression: M2/M1 and M3 trial sets replayed with the M4 build

Build: HSD-Unity branch `m4/ability-primitives` (Unity 6000.6.5f1), the same build that produced the M4 replay in this folder.
Runs (outputs kept outside the repo; only this note is committed):

```
Unity.exe -batchmode -quit -projectPath <HSD-Unity> -executeMethod HSD.R5Replay.Editor.BatchReplay.Run \
    -trial ../../m2/trials/<each> -trial ../../m1/trials/<each> -out <scratch>/m2m1 -motor both -logFile <log>
Unity.exe -batchmode -quit -projectPath <HSD-Unity> -executeMethod HSD.R5Replay.Editor.BatchReplay.Run \
    -trial ../../m3/trials/<each> -out <scratch>/m3 -motor v2 -logFile <log>
python regression_check.py <scratch>/m2m1 <scratch>/m3
```

No `-scenarios` argument, so every R5MotorV2 run is the plain motor (no ability set). `regression_check.py` compares every
steps.csv / summary.json / report.md byte for byte (index.md skipped: it carries the generation time). The research repo stores
.md/.json with LF (`.gitattributes` eol=lf) and Unity writes them with CRLF on Windows, so CRLF is folded to LF for those two types
only; steps.csv is compared raw.

| set | baseline | identical files | different | missing | trials with a difference |
|---|---|---|---|---|---|
| M2 + M1 trials, R5MotorV2 reports | `../../m3/unity/regression_m2_m1` (R5MotorV2/m3 = HSD-Unity main) | 111 | 0 | 0 | – |
| M3 trials, R5MotorV2 reports | `../../m3/unity` (R5MotorV2/m3) | 90 | 0 | 0 | – |
| M2 + M1 trials, M1 first guess | `../../m2/unity/m1_first_guess` | 111 | 0 | 0 | – |
| M2 + M1 trials, R5MotorV2 reports | `../../m2/unity` (R5MotorV2/m2, before M3) | 35 | 76 | 0 | all 37 (see below) |

sha256 of the outputs (CRLF→LF for .md/.json, index.md excluded): M2+M1 `9abd1885c214c4a7bb431927aa595cd0e1c369ad3a76a21f45c986378fb6c0f4`,
M3 `e7743c7840a2139f6b182bfb38decae34b1a6425c7a3dab5c081603f59ee9c95`.

**Result: byte-identical to main.** Every output of the plain motor equals the published M3-motor outputs (M3 trials and the M3
regression of the M2/M1 trials), and the M1 first guess equals the M2 publication.

**The 76 differences against `../../m2/unity` are the M3 changes, not M4.** That folder was produced by the M2 motor
(`R5MotorV2/m2`). In every M2/M1 trial the summary.json and report.md differ only in `model` (`R5MotorV2/m3`), `model_choices`,
`parameters` and `parameter_provenance` (the M3 lurch / jump-chain parameters). steps.csv differs only for M2_e2_strafe_r336/r337,
the two trials with an airborne strafe press, i.e. the M3 lurch; their summary also changes in `overall`, `per_phase`,
`events_sim`, `event_deltas_sim_minus_ref` and `ground_sim`. This is the same set of differences M3 reported (`../../m3/unity/index_notes.md`,
"Regression"), and the M3 regression folder above already contains these outputs bit for bit.

How the plain motor stays identical: the ability seam in `R5MotorV2.Step` runs only when an ability set is attached; the per-command
modifiers default to identity (time scale ×1.0, gravity ×1.0, no launch, no external acceleration, no drag or cap), which leaves every
floating-point operation unchanged; the M4 parameter `lurchClampSprintFraction` defaults to 0 (M3 constant clamp 209.3) and is left out
of the parameter dictionary while 0, so reports keep the M3 parameter list; `MotorInput.buttons` / `pitchDeg` are read only by abilities;
the `sim_events` column gets ability events only from an ability set.
