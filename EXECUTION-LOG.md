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
  - **M0 accepted.** Started M1 source research on deterministic input and reset (read-only subagent).

## Open issues

| # | Since | Issue | Owner / next step |
|---|---|---|---|
| I1 | M0 | Input is wall-clock SendInput, not frame-exact; it needs the window in front | M1 defect 1: deterministic input + reset layer |
| I2 | M0 | `+hsd_md_run` cmdline ignored | set labels after load (done); revisit in the M1 runner |
| I3 | M0 | `DevTextBufferDumpToFile` returns false | low priority; values are in `script.log` |
| I4 | M0 | REA has no native provider | only if offline disassembly is approved and time-boxed |
| I5 | M0 | Weapon move scale (1.15 empty-handed) | fix the weapon state per run; measure a weapon-held condition in M2 |
| I6 | M0 | Unity project: most of the existing work is uncommitted on `main` | protect it; M1 Unity work goes on a new branch in its own folder |
| I7 | M0 | The Unity batch run rewrote `ProjectSettings.asset`; delta unknown | copy `ProjectSettings/` before each Unity run |
