# STATUS — Phase 2 local (plan M0 → M5)

| Milestone | State | Acceptance | Report |
|---|---|---|---|
| M0 environment and baseline | **done** | game + mod + telemetry run on real data (T0 11/11); Unity project opens (§Unity in SESSION-BASELINE); baseline frozen | [SESSION-BASELINE.md](SESSION-BASELINE.md), [m0/M0-REPORT.md](m0/M0-REPORT.md) |
| M1 minimal automated loop | **done** | defects 1–6 fixed; 5 runs + 1 after restart with identical event spacings, 0 gaps, 100 % join; T0 11/11; Unity replay pipeline runs (26/26 tests), first error report: 32 u RMS (not gated) | [m1/M1-REPORT.md](m1/M1-REPORT.md) |
| M2 base parameters | **done** | 17 conditions × ≥ 5 valid trials; parameter table; R5 spreads 0 % / ≤ 1.06 %; Unity R5MotorV2 terminal speed 0.000 %, accel/decel ≤ 0.19 %, 48/48 tests | [m2/M2-REPORT.md](m2/M2-REPORT.md), [m2/PARAMETER-TABLE.md](m2/PARAMETER-TABLE.md) |
| M3 advanced tech | **done** | lurch λ 0.7, time window 0.2→0.5 s, clamp 209.3 (102 trials, 60/120/144 fps); wall bounce; mantle boost = last 133 ms (time-based); Unity lurch + slide-chain link verified, 67/67 tests; design advice | [m3/M3-REPORT.md](m3/M3-REPORT.md) |
| M4 legend movement primitives | in progress | ≥ 3 primitive classes extracted and modelled | — |
| M4b view control + grapple swing (user-approved add-on) | planned | per-usercmd yaw/pitch verified in MOVE-TRACE; swing/steer/detach/release momentum measured, or Unity swing smooth and controllable across anchors and speeds (stop-loss); pad re-jump | — |
| M5 Unity skill slots + playable build | pending | 2 configs, 3 presets of 3–4 skills, regression tests, Windows build + route notes | — |

Rules in force: offline R5Flowstate and the Unity project only; no game files in git (raw logs stay local, `.gitignore`); no forged PASS; one process drives the game or the Unity editor at a time.

Unity: new project `..\HSD-Unity` (private repo `letheli710/HSD-Unity`); the old `High Speed Doom LAB` project is deprecated and untouched.

Directory layout: `research/phase2-local/{m0,m1,…}/` reports, `data/` derived data, `tools/` local runners. Repo-root `EXECUTION-LOG.md` is the running log.
