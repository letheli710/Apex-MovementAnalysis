# Execution log — High Speed Doom × Apex movement (local Phase 2)

Plan: "High Speed Doom：Apex 移动机制提取与 Unity 转化执行计划" (M0 → M5). Current state: [research/phase2-local/STATUS.md](research/phase2-local/STATUS.md).
Newest entries at the bottom. Problems are tagged **[ISSUE]** and also listed in the table at the end.

## 2026-10-20

- Received the plan. Lead agent works locally; game and Unity are driven by one process at a time.
- **M0 (environment and baseline)**
  - Cloned the research repo. Tool checks failed 8/10 on Windows. Causes: CRLF checkout of LF fixtures, no source clones, and `py` following the `/usr/bin/env python3` shebang to the Store stub.
  - Fixed all three: `.gitattributes`; a portable source-root default plus a `check_refs` fallback fix; `py -3` in the docs. Result: 10/10, 52 tests OK, 0 skipped.
  - Pinned source clones in `..\research-src` at the Phase 1 commits. The installed game scripts, cfg and playlists are byte-identical to `s21-platform@9b21dc9`.
  - `server_ready=false` is expected: the channel has no server track and the client track ships the dedi (checked by a read-only subagent; key points spot-checked).
  - Wrote `hsd_launch.ps1` (scripted Play Local: Developer + Cheats + offline) and `hsd_input.ps1` (SendInput keys and console commands to the client window).
  - First real-game T0: smoke 11/11, validate 0 errors, 99.9 % client→dedi join.
  - Baseline frozen in `research/phase2-local/SESSION-BASELINE.md`: firing range, Gibraltar, empty-handed (`msc=1.15` on both sides).
  - **[ISSUE]** computer-use cannot be granted the game window; replaced by `hsd_input.ps1`.
  - **[ISSUE]** `+hsd_md_run N` on the command line is ignored; labels are set from the console after the level loads.
  - **[ISSUE]** Empty-handed runs carry a 1.15 move scale. Every experiment must hold the weapon state fixed and log `msc`.
  - Unity 6000.6.5f1 batch run: the project opens and compiles; PlayMode 104/104 passed in 150 s.
  - **[ISSUE]** The batch run re-serialized `ProjectSettings.asset`. Only a hash was taken beforehand, so the exact delta is unknown. From now on, copy `ProjectSettings/` before every Unity run.
  - **M0 accepted.** PR #1 opened and merged into `claude/laughing-einstein-nlvqcs` (`5646224`).
- **M1 started** on branch `phase2-local/m1-loop`. Three subagents run in parallel, and none of them drives the game or Unity:
  - A: source research on deterministic input and reset (defect 1);
  - B: hsdtel defects 3–6, in worktree `../wt-m1-telemetry` (branch `phase2-local/m1-telemetry`);
  - C: offline sampling-phase analysis of the T0 data (defect 2).
- Decision (user, relayed by another session): Unity work for M1+ happens in a **new Unity project inside the workspace** `C:\Workspace\Playground\ReApex-DataAnalysis\`. The original project `High Speed Doom LAB\High Speed Test 01` is no longer touched; it is read-only reference from here on. This supersedes the "new branch in the original project" rule in SESSION-BASELINE §5.
- User update (relayed): the old Unity project is **deprecated**. I7 is closed as won't fix.
- Subagent results, each checked by the lead before use:
  - A: AgentLink is the native control channel. No SDK path drives the human player's usercmds directly; bots and R5Dem replay are dedi-only.
  - C: an HSD frame is the post-state of the latest usercmd (lag 0). Re-ran its script; its result holds.
  - B: defects 3–6. Merged; 81 tests and 10/10 re-run by the lead.
- Built the AgentLink runner (`agentlink.py`, `hsd_trial.py`, `hsd_session.py`): dedi reset over EVAL, then a client thread sends frame-indexed `ClientCommand` input. Probe: each edge lands in the next usercmd; the first forward command has `fwd` 0.5.
- **[ISSUE→fixed]** Session s1: the unfocused client ran at 18.7 fps, so the 3 s forward segment lasted 23 s. Fixed with `not_focus_sleep 0` and a per-trial fps check (±3 %). s1 is kept as `_REJECTED`.
- **[ISSUE→fixed]** s3/s4: the first trial after a level load hitched (126/133 fps), and the check rejected it. Fixed with a 15 s settle plus a warm-up trial.
- **[ISSUE→fixed]** The client run label covered the teleport, which corrupted `initial_state`. The schedule thread now sets the label after the player has settled.
- s7 (5 trials) and s8 (after a restart, 1 trial): identical event spacings (432/22/410/1/109 usercmds), 0 gaps, 100 % join, smoke 11/11 on both. **M1 A1, A2, A4 pass.**
- Exported `hsdmove-trial/2` trials r41, r42, r46 (check-contract: 0 problems). Started the Unity replay subagent: new project `..\HSD-Unity`, the only Unity instance; the game stays off meanwhile.
- **[ISSUE]** `compare-contracts` aligns by absolute usercmd number, so it cannot compare two different trials (O1 in the M1 report).
- **[ISSUE]** Take-off vz is 276.8 u/s, against 289.8 u/s predicted from `jumpHeight` (O2; M2/E4).
- Unity subagent: created `..\HSD-Unity` with the R5Replay pipeline. The lead re-ran it: 26/26 EditMode tests, batch replay exit 0.
  - First error report: position RMS 32 u. Ground acceleration dominates: R5 shows a low-speed branch at about 2875 u/s² and move-scale-scaled acceleration. Jump apex is 56.0 in sim against 55.0 in R5.
- Created the private repo `letheli710/HSD-Unity`: `main` holds the empty project, `m1/r5-replay` holds the pipeline.
- **M1 accepted** (A1–A4). Next: M2 (E0 census per session, E1 ground, E2 air, E4 jump, E5 slide).
- **M2 started** on branch `phase2-local/m2-params`.
  - Contract: optional per-step `movescale`/`maxspeed` columns.
  - Runner: multi-condition sessions with an E0 census at the start; 17 schedules covering E1/E2/E4/E5; per-schedule yaw.
  - Pilot 1, on the spawn pad, exposed three problems: **[ISSUE→fixed]** `+back` does nothing (the command is `+backward`); **[ISSUE→fixed]** walls on the right of the pad; **[ISSUE→fixed]** hop chains fall off the pad after about 1100 u.
  - `map_scan.py` traced the map from the dedi and found a flat, hull-clear field at z 294.92 (about 2000 × 1600 u). Pilot 2 on it is clean: all 17 conditions, no falls, every straight motion along +X.
  - **[ISSUE→fixed]** The first scan JSON contained a local user path, caught before push. The tool now drops it, the commit was amended locally, and a local pre-commit hook blocks `<drive>:\Users\<name>` paths.
- M2 main session (17 conditions × 5 trials): **[ISSUE]** only 32 of 85 trials passed the fps check.
  - From the start the client ran steadily at about **138 fps**, and later dipped to 77–127.
  - Desktop activity overlapped: Twinkle Tray started at 20:42 and VS Code/Chrome at 20:44, while the session started at 20:47.
  - 138 on a 144 Hz display looks like an external frame cap (G-Sync/Reflex style). The cause is unverified.
  - fps returned to 144 by r251; E4/E5 trials from there on are valid.
  - The ±3 % threshold was **not** relaxed. The 12 short conditions were re-run instead (`M2_rerun`): 60/60 passed at about 143.9 fps.
- Every M2 condition now has ≥ 5 valid trials. Started three offline analysis subagents (ground E1, air/jump E2+E4, slide E5). Exported 34 `hsdmove-trial/2` trials (2 per condition) for the Unity mapping; check-contract reports 0 problems.
- M2 analysis by three subagents, each rerun by the lead with byte-identical outputs:
  - **ground**: piecewise accel 2875 → 517.5 → sprint band, constant decel 1250 (not ×msc), crouch 92/1500; spreads ≤ 0.10 %.
  - **air/jump**: half-step gravity 750; V = √(2g·56·frac) with 1.5·g·dt removed on the jump command (this explains 276.8); AirAccelerate = 500·dt, cap 60·msc; multi-jump frac 0.3 → 1 over 0.15 + 0.60 s; no air drag.
  - **slide**: boost to min(v + 150·msc, 400·msc); decay (v − 100·dt)·0.7^dt; end below 125; slide jump refund / 350 floor.
- **[ISSUE→understood]** `sprintAcceleration` differs between sessions (100 vs 102). Cause: the firing range assigns a **random legend per session** (M0/M1 Gibraltar, M2_main Pathfinder, M2_rerun Wraith). Wraith's class vars differ in sprintAcceleration and dodge only, and the measured sprint accel followed each session's census exactly (115.01 / 117.30).
  - The models stay valid because they read live class vars.
  - The runner now pins the legend (`--legend`, default gibraltar, via `Agent_SetLegend`); not yet verified live.
  - SESSION-BASELINE corrected.
- Wrote `m2/PARAMETER-TABLE.md`: value, unit, source and spread for every parameter. M2 R5-side acceptance passes (terminal speed spread 0 %, worst accel/decel spread 1.06 %). Started the Unity motor v2 subagent (the only Unity process).

## Open issues

| # | Since | Issue | Owner / next step |
|---|---|---|---|
| I1 | M0 | Input is wall-clock SendInput, not frame-exact; it needs the window in front | **fixed in M1**: AgentLink runner, frame-indexed and focus-free. cmd-exact edges remain open (M1 report O3) |
| I2 | M0 | `+hsd_md_run` cmdline ignored | **closed**: labels are set by the runner and the schedule thread |
| I3 | M0 | `DevTextBufferDumpToFile` returns false | low priority; values are in `script.log` |
| I4 | M0 | REA has no native provider | only if offline disassembly is approved and time-boxed |
| I5 | M0 | Weapon move scale (1.15 empty-handed) | fix the weapon state per run; measure a weapon-held condition in M2 |
| I6 | M0 | Unity project: most of the existing work is uncommitted on `main` | **closed**: the old project is deprecated; M1+ uses a new project in the workspace |
| I9 | M2 | Firing range assigns a random legend per session; class vars differ between legends | runner pins the legend (`--legend`); verify live at the next session |
| I8 | M2 | Client frame rate can sit at ~138 fps or dip while the desktop is in use (cause unverified) | the per-trial fps check rejects such trials; re-run them; avoid heavy desktop use during sessions |
| I7 | M0 | The Unity batch run rewrote `ProjectSettings.asset`; delta unknown | **closed, won't fix**: the user says the old project is deprecated |
