# SESSION-BASELINE — frozen local environment for Phase 2 (M0)

Frozen: 2026-10-20. Every M1+ measurement must state any deviation from this baseline.
Details of the repairs and the first real run are in [m0/M0-REPORT.md](m0/M0-REPORT.md).

## 1. Versions

| Item | Value |
|---|---|
| OS | Windows 11 Pro 10.0.26200; Windows PowerShell 5.1 only (no PowerShell 7) |
| Python | 3.11.1. Call it as `py -3`; bare `py`/`python` hit the Microsoft Store stub |
| Research repo | `letheli710/Apex-MovementAnalysis` (public). Base `claude/laughing-einstein-nlvqcs` @ `ad89e2b`; work branch `phase2-local/m0-baseline` |
| Source clones (analysis only, outside the repo) | `..\research-src\`: `s21-r5sdk@10077bb`, `s21-platform@9b21dc9`, `launcher@00fd923` |
| Game | `%USERPROFILE%\Games\R5Flowstate`, `R5pc_r5-211_J12_CL6933961_2026-09-27_001_R5F`, `v3.0.72.12`, SDK `R5FlowstateSDK005`, launcher 0.1.62 |
| Engines | S21 client (`r5apex_dx12.exe`) predicts; S3 dedi (`r5apex_ds.exe`) is authoritative; SDK DLLs patch both (Phase 1 F1). The dedi log confirms S3 at run time ("SetStickerSlot not available in S3") |
| Installed scripts | byte-identical (line endings aside) to `s21-platform@9b21dc9`: 1393 vscripts, 27 cfg, playlists |
| Mods | `HSD.MoveDiag` 0.2.0 (ours, observe-only), `Cafe.HelloMod` 1.0.0 (pre-installed 21-line smoke test; no movement code) |
| REA | 6.4.0 MCP; no native provider (Ghidra/IDA not configured) |
| Unity | 6000.6.5f1. Project `High Speed Doom LAB\High Speed Test 01` (git `letheli710/High-Speed-Test-01`, branch `main`, one commit; most of the current work is uncommitted, see §5) |

## 2. Test baseline (clean offline mode)

| Choice | Value | Why |
|---|---|---|
| Playlist / map | `survival_firingrange` / `mp_rr_canyonlands_staging_mu1` | Flat open ground and walls; no match timer or ring; dedi ready in about 27 s |
| Mode-level speed effects | none | The playlist block (`playlists_r5_patch.txt:951-1135`) has no speed, gravity, jump or class vars. The only platform-script modifier active in this mode is CafeMod `items_weapon`, which only affects toy projectiles from DevMenu "Give Weapon" (`cafemods/sv_mod_items_weapon.nut`) |
| Legend | Gibraltar (`character_gibraltar`, setfile `settings/player/mp/pilot_survival_gunner.rpak`), **pinned by the runner** (`hsd_trial.py --legend`) | **Correction (M2):** the firing range assigns a *random* legend per session; Gibraltar in M0/M1 was chance (M2 sessions got Pathfinder and Wraith). Wraith's class vars differ (sprintAcceleration 102, dodge). Every session's census is recorded, and models read class vars per session |
| Weapon state | **empty-handed** | Observed `msc=1.1500` on both sides for every grounded command (7797 dedi / 7806 client rows), so `ms = 173.5 × 1.15 = 199.525`. The weapon term enters through `SetupMove` (Phase 1 §2). **Every run must hold the weapon state fixed and log `msc`**; M2 adds a weapon-held condition |
| Launch | `research/phase2-local/tools/hsd_launch.ps1`: Developer (`-devsdk -dev`), `sv_cheats 1`, `-offline` on both sides, windowed 1600×900, `+mat_vsync_mode 0 +mat_antialias_mode 0` (cosmetic; since M3). Frame rate: `fps_max 144` in M0–M2, **120 from M3** (an external ~138 fps cap appeared during M2; 120 is stable). Set per session with `hsd_trial.py --fps` | Scripted; no launcher GUI |
| Telemetry | `bridge_move_trace 1` on both sides, `hsd_md_cl_trace 1` on the client | `hsd_client.cfg` / `hsd_dedi.cfg` |

## 3. What works

| Capability | Evidence |
|---|---|
| Offline tool checks | `run_checks.py` 10/10, 52 unit tests OK, 0 skipped (Windows) |
| Game start, mod load on both VMs, telemetry on both sides | T0: `hsd_tel.py smoke` 11/11, 99.9 % client→dedi command join, `dt_est/FrameTime` 1.005 |
| Scripted input (keys, console) | `research/phase2-local/tools/hsd_input.ps1` drove the whole T0 |
| Runtime parameter readout | 58-key census from the class-var reader and from `GetPlayerSetting*` on both sides; equal where both can read |

## 4. Where it is stuck or limited

| Item | Status |
|---|---|
| Deterministic, frame-exact input | **Not yet.** SendInput is wall-clock timed and needs the window in front. This is defect 1 of the plan: M1 builds the reset + input layer |
| Run labels at start-up | `+hsd_md_run N` on the command line is ignored; set labels after the level loads |
| `DevTextBufferDumpToFile` | returns false; the same values are in `script.log` |
| computer-use on the game | cannot be granted (the game exe is not a registered app); the input script replaces it |
| First level load | about 5 min (shader cache build) |

## 5. Unity project state

| Item | Value |
|---|---|
| Path | `C:\Workspace\Playground\High Speed Doom LAB\High Speed Test 01` |
| Editor | 6000.6.5f1 (Unity Hub); URP 17.6, Input System 1.20, Test Framework 1.8 |
| Git | remote `letheli710/High-Speed-Test-01`, branch `main`, one commit (`2402262 Initial check-in`). **The existing High Speed Doom work is uncommitted**: `Assets/HighSpeedDoom/`, `Docs/`, `Art/`, `README.md` are untracked, and 15 tracked settings files are modified |
| Existing prototype | `CapsuleMotor` / `FpsMovementController`, fixed step 0.01 s, 7 abilities (Dash, WallRun, Grapple, Blink, GravityShift, Flight, MomentumBrake), 4 loadouts with up to 4 slots, 10 course scenes, `MovementTelemetry`, `FrameInputReplayTests` |
| Opens and compiles | yes. `Unity.exe -batchmode -runTests -testPlatform PlayMode` exited 0 after 150 s |
| PlayMode tests | **104/104 passed**, 0 failed, 0 skipped (same count as the project README) |
| Files touched by the batch run | The five `*.csproj` were regenerated; they are ignored by `.gitignore:54`. `ProjectSettings/ProjectSettings.asset` was re-serialized (hash changed). Only hashes were taken beforehand, so the exact batch delta cannot be told apart from the user's own uncommitted edits. Its diff against HEAD contains only project settings (product name, run in background, cloud ids…). From now on, copy `ProjectSettings/` before every Unity run |

Rule for Unity work from M1 on (user decision, 2026-10-20):

- Unity work happens in a **new Unity project inside the workspace** `C:\Workspace\Playground\ReApex-DataAnalysis\`, with its own git repository.
- The original project above is **read-only reference**: no editor or batch runs and no file changes. Code may be read or copied out of it.
- Only one Unity instance at a time, and never while the game is being driven.
