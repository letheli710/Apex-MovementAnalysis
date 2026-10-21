# STATUS — Phase 2 local (plan M0 → M5)

| Milestone | State | Acceptance | Report |
|---|---|---|---|
| M0 environment and baseline | **done** | game + mod + telemetry run on real data (T0 11/11); Unity project opens (§Unity in SESSION-BASELINE); baseline frozen | [SESSION-BASELINE.md](SESSION-BASELINE.md), [m0/M0-REPORT.md](m0/M0-REPORT.md) |
| M1 minimal automated loop | **done** | defects 1–6 fixed; 5 runs + 1 after restart with identical event spacings, 0 gaps, 100 % join; T0 11/11; Unity replay pipeline runs (26/26 tests), first error report: 32 u RMS (not gated) | [m1/M1-REPORT.md](m1/M1-REPORT.md) |
| M2 base parameters | next | parameter table (value, unit, source); ground terminal speed spread ≤ 2 %, accel/decel spread ≤ 5 %; Unity mapping | — |
| M3 advanced tech | pending | tap strafe + one wall/landing link in Unity, trigger windows, design advice | — |
| M4 legend movement primitives | pending | ≥ 3 primitive classes extracted and modelled | — |
| M5 Unity skill slots + playable build | pending | 2 configs, 3 presets of 3–4 skills, regression tests, Windows build + route notes | — |

Rules in force: offline R5Flowstate and the Unity project only; no game files in git (raw logs stay local, `.gitignore`); no forged PASS; one process drives the game or the Unity editor at a time.

Unity: new project `..\HSD-Unity` (private repo `letheli710/HSD-Unity`); the old `High Speed Doom LAB` project is deprecated and untouched.

Directory layout: `research/phase2-local/{m0,m1,…}/` reports, `data/` derived data, `tools/` local runners. Repo-root `EXECUTION-LOG.md` is the running log.
