# M6 summary: Advanced Movement & Unique Mobility Expansion

Plan: [M6-PLAN.md](M6-PLAN.md). Sub-reports:

- [M6-A-REPORT.md](M6-A-REPORT.md)
- [b_legends/M6-B-REPORT.md](b_legends/M6-B-REPORT.md)
- [unity/M6C-UNITY.md](unity/M6C-UNITY.md)
- [M6-C-DESIGN-NOTES.md](M6-C-DESIGN-NOTES.md) (Chinese)

Playtest guides: [PLAYTEST-GUIDE-M6.md](PLAYTEST-GUIDE-M6.md), [PLAYTEST-GUIDE-M6C.md](PLAYTEST-GUIDE-M6C.md), [PLAYTEST-GUIDE-M6B.md](PLAYTEST-GUIDE-M6B.md).
Build: `HSD-Build\M6B\HSD-Practice.exe` (contains everything from M5.5, M6-A, M6-C and the M6-B build).

Scope: R5Flowstate S21 (local offline: S21 client + S3 dedi + SDK), not official S21. Every analysis was written by a subagent and re-run by the lead with identical outputs. Every Unity hand-back was re-verified by the lead: tests, replay regression, smoke.

## Acceptance

| Part | Criterion | Result |
|---|---|---|
| M6-A | 3 core families playable; independent tests + regression; M5.5 intact; ≥ 3 real-input chains; Windows build + route | **PASS**. Lurch / tap strafe, climb / mantle / superglide, zipline (+ Super Jump, grapple handoff). 4 chains, each with a failure variant. Merged in research #8 and HSD-Unity #8. |
| M6-B | 4 legends with independent conclusions; evidence classes separated; uniqueness / cost / reuse / combo comparison; no full build without user OK | **PASS (research + chosen build)**. Valkyrie fuel closed; Ash and Loba measured; Alter not triggerable in this setup (SDK placement), so source-only. The user chose to build the Valkyrie jets and Ash Phase Breach; Loba and Alter are shelved ([../../../SHELVED-ABILITIES.md](../../../SHELVED-ABILITIES.md)). Build: [unity/M6B-UNITY.md](unity/M6B-UNITY.md); numbers pass, hands-on feel not yet checked. Merged in research #9 and HSD-Unity #10. |
| M6-C | chosen mechanics combine naturally; no stuck states, wrong speed stacking or serious collision; free play; feedback entry; next-phase advice | **PASS**. Combination course J–P, each section with at least 2 ways through; 7 more chains, 3 of them cross-family. Fuzz: 360 episodes, 1.51 M commands, caps held, never inside solids, no climb/zip timeouts. F9/F10 feedback snapshots. Chinese design notes. |

## Lead-verified final numbers (HSD-Unity `m6c/combination-playground` de4495c on main 9e858a2)

- **Tests:** EditMode 511/511, PlayMode 1/1.
- **Default replay motor:** byte-identical (M2/M1 111/111, M3 90/90, M1 first guess 111/111); 38 M4 replays identical (114/114).
- **Smoke:**
  - M5.5 route line unchanged;
  - demos 34/34 verdicts as expected (M5.5 12/12, M6 8/8, M6-C 14/14);
  - course lap 80.82 s (7/7 checkpoints);
  - feedback snapshot written.

## What M6 measured (headline)

- **Lurch:** every airborne press edge lurches (W too), with no budget, and the latest jump re-anchors the window. Tap strafe emerges from this.
- **Climb:** outcome by ledge height. No ledge hang exists. Releasing W on the wall gives an attached slide, then a detach 1 s after contact.
- **Superglide:** native 460 u/s; the SDK FSM gives 388.7.
- **Zipline:** jump-off = rope·min(v, 400) + 289.8 up. Super Jump exists. The grapple hands off to a rope automatically, and a second tactical press releases the grapple.
- **Legends:**
  - Valkyrie: 1/s drain, cost 1, empty after 7 s, recharge 0.75/s.
  - Ash: exit speed 0, lock grows with the path.
  - Loba: velocity zeroed.

## Problems and how they were handled

- The plan's `research/S21-2026-10-21/` was not found anywhere, so it was not used.
- Lead errors, caught by the analyses and fixed:
  - the A2 round-2 origin bug: re-run, and the runner now guards against it;
  - M6-B first-run inputs: Ash needs offhand4 then attack; Loba's throw delay is 1.21 s.
- The state logger needed a functionref lambda: an EVAL cannot declare a top-level function.
- The `find` cvar census is not possible (the dedi has no `find`).
- Alter: SDK placement failed even with the SDK levers on. Stop-loss.

## Most important design values to playtest

- Super Jump window 0.2 s.
- Superglide window at heights other than 232.
- Climb facing cone 35°.
- Mantle cancel at 0.5 T.
- Vertical-rope top push (~580 u of flight).
- Slope slide, which barely gains speed.
- Fun-config air mount.
- Camera cues.

## M6-B build (after the user's decision)

The user chose the Valkyrie jets and Ash Phase Breach as a route tool, and shelved Loba and Alter. The lead re-ran HSD-Unity `764a618` (main `199dde8`):

- **Tests:** EditMode 607/607, PlayMode 1/1.
- **Default motor:** identical.
- **M4 replays:** 114/114 identical.
- **Smoke:** demos 48/48 (M6-B 14/14); M5.5 route and course lap unchanged.

The **Reference/Fun** split is tested; every Fun value is a design value. Status is **数值通过** (numbers pass) and **真人手感未验收** (hands-on feel not yet checked by a person). Details: [unity/M6B-UNITY.md](unity/M6B-UNITY.md).
