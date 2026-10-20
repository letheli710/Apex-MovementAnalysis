# M0 — local environment repair and verification

Scope: make the Phase 1 / 1.5 tooling run on the local Windows machine, confirm the installed game matches what was analysed, and prove the telemetry pipeline end to end (T0) before any M1 movement experiment.

- Date: 2026-10-20 (local)
- Machine: Windows 11 Pro 10.0.26200
- Repository: `letheli710/Apex-MovementAnalysis`, branch `claude/laughing-einstein-nlvqcs`, base commit `ad89e2b`
- Game: `%USERPROFILE%\Games\R5Flowstate`, `build.txt` = `R5pc_r5-211_J12_CL6933961_2026-09-27_001_R5F`, `gameversion.txt` = `v3.0.72.12`, SDK string `R5FlowstateSDK005`

## 1. Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| A1 | `run_checks.py` 10/10 PASS on Windows, unit tests OK with 0 skipped | PASS (§3) |
| A2 | Installed game scripts / cfg / playlists equal the analysed `s21-platform@9b21dc9`; SDK DLLs carry every ConVar the configs use | PASS (§4) |
| A3 | HSD.MoveDiag installed; `hsd_modlint` and `hsd_vmcheck --strict` give 0 errors against the installed scripts | PASS (§5) |
| A4 | Local dedicated server availability understood (`server_ready=false`) | PASS (§6.1) |
| A5 | Scripted, repeatable launch of client + dedi with Developer and Cheats | PASS (§6.2, §6.3) |
| A6 | T0 smoke on real game logs: `hsd_tel.py smoke` 11/11 | PASS (§7) |

M1 starts only when A1–A6 all pass. **All six pass: M0 is accepted.**

## 2. Fixes

| # | Problem found | Root cause | Fix | Files |
|---|---|---|---|---|
| F1 | `TestDeterminism` failed: regenerated fixtures differed from the checked-out ones | `core.autocrlf=true` checked out LF fixtures as CRLF; the repo had no `.gitattributes` | `.gitattributes`: `* text=auto eol=lf`; `*.csv -text` (csv.writer emits CRLF and those bytes are stored as-is). Working copy of the 65 affected files re-checked-out as LF | `.gitattributes` |
| F2 | `check_refs` / `test_references_resolve` failed on a fresh machine | (a) defaults pointed only at the cloud path `/home/user/research-src`; (b) without clones, the bare `scripts.rson:630-637` matched the mod's 14-line `scripts.rson` by basename and reported `line_out_of_range` instead of `unchecked` | (a) default source root falls back to `<repo>/../research-src`; (b) a bare external basename that only matches an unrelated in-repo file is `unchecked` when no clones exist; (c) the citation is now path-qualified | `research/phase2-prep/tools/check_refs.py`, `run_checks.py`, `tests/_common.py`, `VALIDATION-REPORT.md` |
| F3 | Source clones absent locally | not part of the repo | pinned clones in `C:\Workspace\Playground\ReApex-DataAnalysis\research-src\` at the exact Phase 1 commits: `s21-r5sdk@10077bb`, `s21-platform@9b21dc9`, `launcher@00fd923` | outside the repo |
| F4 | `py research\...` exited 9009 with no output | the scripts' `#!/usr/bin/env python3` makes `py` search PATH for `python3`, which resolves to the Microsoft Store stub (`WindowsApps\python3.exe`) | all local commands in the docs now use `py -3 ...`; LOCAL-SETUP explains why | `EXPERIMENTS.md`, `LOCAL-SETUP.md`, `VALIDATION-REPORT.md` |

## 3. Offline checks (A1)

`py -3 research\phase2-prep\run_checks.py` (defaults now find `..\research-src`):

```
PASS unit tests: exit 0                      (52 tests, OK, 0 skipped)
PASS phase1 hsd_movelog selftest
PASS hsd_modlint (loader rules)
PASS hsd_vmcheck --strict (per-VM API evidence)
PASS validate clean SYNTHETIC fixture
PASS validate faulty SYNTHETIC fixture (exit 2 expected)
PASS report on SYNTHETIC fixture
PASS schema export
PASS smoke checks on SYNTHETIC fixture
PASS documentation references (check_refs)
10/10 passed
```

Without any clones, `check_refs.py` now exits 0 with `bare_name=11, ok=106, unchecked=385`.

Before the fixes the same run gave 8/10 (determinism and references).

Known, harmless churn: regenerating `results/synthetic_report/fits.json` on Windows changes the last digit of some floats (platform libm). Generated result files were restored to the committed versions after each run.

## 4. Installed game vs. analysed sources (A2)

| Compared | Result |
|---|---|
| `platform/scripts/vscripts` (1393 files) vs `s21-platform@9b21dc9` | identical after line-ending normalisation (0 changed, 0 missing, 0 extra) |
| `platform/cfg` (27 files) | identical |
| `platform/playlists_r5_patch.txt` | identical |
| SDK DLLs | `client.dll` and `server.dll` both contain `R5FlowstateSDK005`; ConVars `bridge_move_trace`, `bridge_move_trace_replays`, `bridge_classvar_get`, `bridge_classvar_log_cl` (client), `bridge_classvar_log`, `bridge_lurch_cutoff_speed`, `mantle_boost_enabled` (server) are present |

So every Phase 1 script-level citation applies to this install. The SDK DLLs cannot be tied to `s21-r5sdk@10077bb` byte-for-byte (no commit string is embedded); the ConVar set matches what the telemetry configs need.

## 5. Mod and configs installed (A3)

| What | Where |
|---|---|
| HSD.MoveDiag v0.2 (`mod.vdf`, `readme.md`, `scripts/vscripts/scripts.rson`, `hsd_movediag__movediag.gnut`) | `<game>\mods\hsd_movediag\` |
| `hsd_client.cfg`, `hsd_dedi.cfg`, `hsd_e0_classvars.cfg`, `hsd_off.cfg`, `hsd_runs.cfg` | `<game>\platform\cfg\user\` |

- `hsd_modlint` on the installed copy: 0 errors. `hsd_vmcheck --strict --base <game>\platform\scripts\vscripts`: 0 errors.
- `mods\mods.vdf` lists only `Cafe.HelloMod`; mods not listed there are enabled by default (`s21-r5sdk/src/pluginsystem/modsystem.cpp:532-556`).
- Undo: delete `<game>\mods\hsd_movediag` and the five `hsd_*.cfg` files. Nothing else in the game folder was changed.

## 6. Dedicated server and launch (A4, A5)

### 6.1 `server_ready=false` is expected

Investigated by a read-only subagent against `launcher@00fd923` (the installed launcher is the same 0.1.62 build); key points spot-checked.

- The "server" track is an optional channel tip. This channel's `CHANNEL_MANIFEST.json` has only `client`, `platform` and `hd` keys (checked), so the launcher never plans a server track.
- The client track already carries the dedi: `r5apex_ds.exe`, `server.dll`, `paks/Win64_server/*`, `startup_dedi_*.cfg`.
- Play Local drops the server requirement when the channel has no server tip: "Mixed client SHARE carries dedi. No separate server tip = not a missing track." (`launcher/src/R5Flowstate.Content/InstallHealthAssessor.cs:31-33`, checked).
- On-disk check (exists + size): client 10573/10573, platform 2522/2522, hd 1321/1321 files match their manifests.
- Confirmed in practice: the dedi started from the client install, loaded the map and accepted the client (§7).

### 6.2 Scripted launch: `research/phase2-local/tools/hsd_launch.ps1`

Reproduces launcher "Play Local" with Developer + Cheats (launcher `R5Flowstate.Spawn/LaunchArgs.cs`, `Shell/MainWindow.xaml.cs` `RunPlayAsync`):

- **dedi:** `r5apex_ds.exe -dedicated -port 37015 … -devsdk -dev … -offline +sv_onlineAuthEnable 0 +spire_host_visibility 0 +sv_cheats 1 +exec user/hsd_dedi +launchplaylist <pl> +map <map> +sv_modPolicy 0`.
- **Gate:** the script waits for the dedi's `R5F_HOST_READY` named event (the launcher's own gate) before starting the client.
- **client:** `r5apex_dx12.exe -nodiscord -allowmultiple -devsdk -dev … -offline +cl_onlineAuthEnable 0 … +exec user/hsd_client +exec user/hsd_runs -windowed -width 1600 -height 900 +connect 127.0.0.1:37015`.
- **Stop:** `-Stop` ends only processes whose image is under the game root. The launcher, by contrast, kills every `r5apex_ds.exe` on the machine.
- **Side effects:** it writes no game files and no registry keys. It skips the launcher's rcon and hosted-console pipes, which the SDK treats as optional.
- **Compatibility:** Windows PowerShell 5.1 (no PowerShell 7 on this machine).

Observed on the first run (firing range, `survival_firingrange` / `mp_rr_canyonlands_staging_mu1`):

- the dedi was ready after 27 s;
- the client was in the level about 5 min after start. The first launch builds the shader cache (`psoCache.pso` was missing); later launches should be faster (unverified).

### 6.3 Scripted input: `research/phase2-local/tools/hsd_input.ps1`

The computer-use tool cannot target the game: `r5apex_dx12` is not a registered app, and only the launcher could be granted. Input therefore comes from a local script:

- It sends hardware scan codes with `SendInput` to the client's `Respawn001` render window. The process also owns a console window titled "R5F Client"; the script targets the render window, not that one.
- It types console commands (grave key, text, Enter).
- It saves PNGs of the window.

Steps are a small text program, e.g. `console hsd_md_run 1; wait 3; hold w 3; wait 3; tap space; wait 2; console hsd_md_run 0`. While it runs it takes keyboard focus; nobody should type meanwhile.

## 7. T0 smoke on the real game (A6)

Data: `research/phase2-local/data/20261020_190759_T0_smoke/`, collected with `hsd_collect.py --label T0_smoke`. Only `report/` (without `rows.csv`) is in git; the raw log sessions (`platform/`, 12 MB) stay on the local machine because they contain local paths (`research/phase2-local/.gitignore`).

```
PASS  MT client rows  [7817]
PASS  MT dedi rows  [7802]
PASS  HSD client init line  [1]
PASS  HSD dedi init line  [1]
PASS  HSD client frames (hsd_md_cl_trace 1)  [7781]
PASS  HSD dedi movement events  [5]
PASS  validation errors == 0  [0]
PASS  client cmds with a dedi line >= 90%  [99.9%]
PASS  MT dt_est median / HSD FrameTime median within 15%  [1.005]
PASS  HSD ground/slide APIs available (no -1)  [0]
PASS  at least one non-zero hsd_md_run label  [['r0', 'r1']]
11/11 smoke checks passed
```

`validate` reported `files=16 rows=23589 errors=0 warnings=2 infos=24`.

- Both warnings come from the spawn: a `W_TELEPORT` at RESPAWN, and a RESPAWN event stamped 0.27 s after the TOUCH_GROUND that follows it.
- The infos are: 7 setting keys that could not be read, 14 re-predicted rows, and the join summary.
- Client `error.log` holds only audio-codec and material warnings. Dedi `script_warning.log` holds S3 stubs (e.g. "SetStickerSlot not available in S3"). Neither log mentions HSD.

Phase 1.5 unverified items, as resolved by this run:

| Item | Result |
|---|---|
| U1 mod compiles in both VMs | yes (`kind=init` on `sv` and `cl`, no script errors) |
| U2 client methods resolve | yes (no `-1` ground/slide, no `kind=error`) |
| U3 try/catch containment | not exercised (nothing raised) |
| U4 mod ConVars | work when set from the console. They do **not** take effect as `+hsd_md_run N` on the command line (R1) |
| U5 S3 dedi fires movement events | yes (RESPAWN, TOUCH_GROUND, JUMP, LEAVE_GROUND) |
| U6 log paths and prefixes | as read from source |
| U7 `bridge_classvar_get` census | all 58 keys printed |
| U8 `GetPlayerSettingFloat` vs class vars | equal on every key both can read (`differs=0` for all 58) |
| U9 `dt_est` assumption | ratio 1.005 |
| U11 console `exec`, `alias`, client → dedi `hsd_md_dump` | work (the dedi printed its 58 settings after the client command) |
| U12 Developer args | work (`[DEVGATE] FCVAR_DEVELOPMENTONLY console gate neutered`; `bridge_move_trace 1` took effect) |
| U13 where the settings CSV lands | not written: `kind=dumpfile file=0` (R4) |
| U10, U14 | not checked in M0; they belong to the E1/E2 analysis |

The run also captured a first parameter census (`report/census.csv`: 58 keys, for one legend in the firing range). It is a by-product of T0. Interpreting it belongs to M1/E0, and nothing in M0 depends on it.

## 8. Remaining issues

| # | Issue | Impact | Proposed handling |
|---|---|---|---|
| R1 | `+hsd_md_run N` on either command line is ignored (init lines show `run=0`); probably applied before the mod ConVars exist | run labels must be set after the level loads | M1 automation sets labels through `hsd_input.ps1 console …` (as T0 did) or a dedi-side lever |
| R2 | Injected input needs the client window in front and an idle keyboard. It is wall-clock timed, not frame-exact | fine for T0; too coarse for frame-window mechanics (tap strafe, superglide) | M1: measure with native deterministic input (`BotCmd_*`, `CmdRec_*` / `BotCmd_PlayRecording`, Phase 1 F15); keep SendInput for setup and smoke tests |
| R3 | computer-use cannot be granted the game client | no screenshots or clicks through that tool | covered by `hsd_input.ps1` (`shot`, keys, console) |
| R4 | `DevTextBufferDumpToFile` returned false (`file=0`); no `scriptdump_*.csv` | none: the same values are in `script.log` | low priority |
| R5 | 7 of 58 keys cannot be read through `GetPlayerSetting*` (`lowSpeed`, `lowAcceleration`, `sprintAcceleration`, `sprintDeceleration`, `doubleJump`, `climbEnabled`, `wallrun`) | the class-var reader still has them | none for M0 |
| R6 | The SDK DLLs carry `R5FlowstateSDK005` but no commit id; parity with `s21-r5sdk@10077bb` is inferred from the ConVar set only | Phase 1 SDK citations may drift when the SDK updates | recheck the ConVar set after each launcher update |
| R7 | REA has no native provider (Ghidra/IDA not configured) | no disassembly of the closed movement code | only if the user approves offline static analysis (Phase 1 recommendation 3) |
| R8 | The first level load took about 5 min (shader cache) | slow first iteration only | none |
| R9 | `-offline` on both sides deviates from the launcher's current setting (Offline unticked). The run worked offline; whether that avoids every network call is unverified | none observed | keep the default `-Offline $true`; pass `-Offline $false` if a mode needs auth |
| R10 | Regenerated synthetic results differ in the last float digit on Windows | git noise only | do not commit synthetic results regenerated on Windows |

## 9. How to reproduce M0

```powershell
cd C:\Workspace\Playground\ReApex-DataAnalysis\Apex-MovementAnalysis
py -3 research\phase2-prep\run_checks.py                                   # 10/10; then: git checkout -- research/phase2-prep/results
powershell -ExecutionPolicy Bypass -File research\phase2-local\tools\hsd_launch.ps1   # dedi + client, firing range, telemetry on
# once the level is loaded:
powershell -ExecutionPolicy Bypass -File research\phase2-local\tools\hsd_input.ps1 -Steps "console hsd_md_run 1; wait 3; hold w 3; wait 3; tap space; wait 2; console hsd_md_run 0; console quit"
powershell -ExecutionPolicy Bypass -File research\phase2-local\tools\hsd_launch.ps1 -Stop
py -3 research\phase2-prep\tools\hsd_collect.py --game "%USERPROFILE%\Games\R5Flowstate" --out research\phase2-local\data --label T0_smoke
py -3 research\phase2-prep\tools\hsd_tel.py smoke research\phase2-local\data\<stamp>_T0_smoke\platform\logs
```
