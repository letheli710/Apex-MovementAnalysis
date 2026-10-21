# M6-A: general advanced movement (continuous lurch / tap strafe, climb-mantle-superglide, ziplines, world foundation)

Plan: [M6-PLAN.md](M6-PLAN.md) §M6-A. Audit: [M6-AUDIT.md](M6-AUDIT.md). Source research: [SOURCE-AUDIT.md](SOURCE-AUDIT.md).
Branches: research `phase2-local/m6-movement`; HSD-Unity `m6/advanced-movement` (`d5da139` A4, `27898da` core, `3bd822e` game).
Scope: R5Flowstate S21 (local offline: S21 client, S3 dedi, SDK), not official S21.

Evidence labels:

- **[meas] / [fit]**: our runs, analysed by a subagent and re-run by the lead with identical outputs.
- **[src]**: pinned source.
- **[community]**: the 2026-10-20 report.
- **[design]**: an HSD choice.

## 1. Acceptance

| Criterion | Result |
|---|---|
| Three core families playable in Unity | **PASS**: A1 lurch / tap strafe, A2 climb / mantle / cancel / wall slide / superglide, A3 zipline incl. Super Jump and grapple handoff. All run in the practice game from real input. |
| Independent verification + automatic regression | **PASS**: 110 new EditMode tests, each mechanism reproducing the measured numbers (§3). EditMode 424/424, PlayMode 1/1 (lead re-run). |
| No major regression of M5.5 movement / camera / input / HUD | **PASS**: the default replay motor is byte-identical (M2/M1 111/111, M3 90/90, M1 first guess 111/111); the 38 M4 replays are identical (114/114). The M5.5 smoke route line and all 12 M5.5 demo verdicts are unchanged; the M5.5 equivalence tests pass. |
| ≥ 3 representative chains completed by real input | **PASS: 4 chains**, each with a failure variant (§4). Scripted input goes through the normal `Advance → Step` path; bit-identical to feeding `SkillBody.Step` directly; frame-rate independent; unchanged with visuals on. |
| Windows build + practice route | **PASS**: `HSD-Build\M6\HSD-Practice.exe` (outside the repos). Headless smoke: `demos 20/20 verdicts as expected (M5.5 12/12, M6 8/8)`. Guide: [PLAYTEST-GUIDE-M6.md](PLAYTEST-GUIDE-M6.md). |

## 2. What was measured (R5Flowstate)

| Family | Data | Key findings |
|---|---|---|
| A1 lurch | 87 trials, 395 press edges ([a1_lurch](a1_lurch/A1-LURCH.md)) | The M3 model holds unchanged [fit, ≤ 0.008 u/s outside the fade]. **Every airborne press edge lurches**: W included, no budget or cooldown, clamp 209.3 per press. The **latest jump re-anchors** the window (wall bounce included). Tap strafe = W edges while turning: 360 °/s → −81° in 0.25 s at constant speed. The wish direction is the unit vector of the current command's yaw. |
| A2 climb / mantle | 238 + 80 + 51 trials, 8 ledge heights ([a2_climb](a2_climb/A2-CLIMB.md)) | Outcome by height: 60 lands on top; 90–120 instant mantle; 150–180 short climb then mantle; 232 full climb, jump-up, mantle; ≥ 300 climb then fall. The climb end is fixed relative to the floor/takeoff (+147.06), not the ledge. **No ledge hang** in this build. Releasing W on the wall gives an attached slide (time-ramp acceleration), then a detach 1.000 s after contact. A jump from the slide is the M3 wall bounce. Mantle cancel when the forward axis drops below 1 early in the traversal. **Native superglide (SDK FSM off): jump + crouch exits at 460 u/s**; the community FSM gives 388.7 / 367.4 and suppresses lurch afterwards. |
| A3 zipline | 125 + 75 trials ([a3_zip](a3_zip/A3-ZIPLINE.md)) | Mount with +use, Find point within 130 u and inside a 27–40.7° cone; no auto-attach. Ride 600 → 400 u/s², cap 600. Auto-detach and jump-off laws with residual 0 (jump-off = rope·min(v, 400) + 289.8 up). **Super Jump exists** (20/20: mount from the ground, release jump, jump again quickly). Jump-off follows the rope, not the view. Air mount diverges client/dedi. |
| Grapple | 25 trials ([GRAPPLE-ZIP](a3_zip/GRAPPLE-ZIP.md)) | **Grapple → zipline handoff is automatic** (10/10; keeps the momentum along the rope). A **second tactical press releases** the grapple on the press command (velocity kept); attack does not. |
| A4 support | source + Unity | Ground velocity stays flat on slopes [src]; slope slide is native and unmeasured → [design]. |

## 3. What Unity reproduces (lead-verified tests)

| Check | Unity | Measured |
|---|---|---|
| Tap strafe 360 / 180 °/s | −80.99° / −40.49° | −81.02° / −40.52° |
| Stacked / opposite / sequence / diagonal presses | match | ≤ 0.1 u/s |
| Ledge 90 / 120: mantle time | 0.425 / 0.592 s | 0.414 / 0.578 s |
| Ledge 150 / 180: climb, then mantle | 0.200 / 0.392 s, then 0.617 s | 0.206 / 0.399 s, then 0.604 / 0.612 s |
| Ledge 232: climb, jump-up | 0.850 s, dvz 202.8, out −64.3 | 0.849 s, same |
| Superglide / mantle jump | 460 / 299, post vz 280.45 | 460 / 299 |
| Side drift while climbing | 50.7 u/s, 17.6 u | 51 u/s, 18 u |
| Zipline exits, Super Jump | exact | residual 0 |

Main **[design]** values:

- climb facing cone 35°;
- mantle cancel at 0.5 T (inside the measured 0.395–0.685);
- zipline mount cone 34° (inside 27–40.7°);
- Super Jump window 0.2 s (measured: works at 3–8 commands, fails at ≥ 63);
- re-mount budget 3 (+1 every 3 s; SDK modern-Apex rule);
- air mount off in Reference, on in Fun;
- superglide window derived from the 232 u data and reused at other heights;
- slope numbers;
- camera cues.

## 4. Chains (real input, through the normal step path)

| Chain | Success | Failure variant |
|---|---|---|
| Slide jump → wall bounce → tap strafe | 9 lurches anchored to the bounce; the flight ends 2.6° behind the view | bounce jump 0.3 s late: contact too old |
| Climb → mantle → superglide | exit 460 u/s | jump 0.3 s early: mantle cut, no superglide |
| Zipline → Super Jump → air lurch | vz 552, apex +214 u, then a 67° lurch | second jump outside the window |
| Grapple release → air steer → landing slide | release 248 u/s kept, +16° steer, slide at 257 u/s | release 1.5 s late: the pull already ended |

## 5. Problems met

- **Lead error.** The A2 round-2 schedules (`a2r_`) missed the `a2_` origin prefix, started at the default origin and never reached the wall (50 trials). The analysis caught it. The runner now refuses any non-legacy schedule without an explicit start; the round was re-run.
- **Logger.** The state logger failed to compile twice: an EVAL cannot declare a top-level `void function`. Bisected live; it now uses a functionref lambda.
- **Zipline trace.** MOVE-TRACE has a gap during zipline rides (the native hook is not reached); the ride was analysed from HSD frames and SDK diag lines.
- **Census.** The `find` cvar census does not work: the client forwards `find` to the dedi, which has no such command. `jump_graceperiod` stays unread.
- **Missing material.** `research/S21-2026-10-21/` was not found anywhere. M6 did not use or cite it.

## 6. Open items (affect M6-B / M6-C)

- Not measured, so [design] in Unity:
  - downhill ziplines;
  - the zipline re-mount budget in S21;
  - the air-mount rule;
  - the exact Super Jump window (9–62 commands);
  - the mantle-cancel threshold inside 0.395–0.685;
  - superglide windows at heights other than 232;
  - slope slide.
- Not modelled:
  - the mantle trigger lag (0–3 commands);
  - the FSM 1.5° camera gate;
  - the 9.46 u/s dip on the first exit command at 90/120 u.
- Camera cues are design values until playtested.
- Next: **M6-B** (Alter, Loba, Ash, Valkyrie; schedules already prepared), then **M6-C** (combination playground). The M6-A chains are the base of the M6-C checks.
