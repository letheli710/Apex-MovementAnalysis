# LOCAL-SETUP — install and launch for the first local telemetry session

Target: the Windows 11 machine with R5Flowstate already installed. Allow about 30 minutes for the first pass.

Each step says what to look for and what to do when it is missing. Facts taken from the sources carry a path; anything not yet seen working is marked **(unverified)**.

## 0. Prerequisites

| Item | How to check |
|---|---|
| Python ≥ 3.8 (stdlib only; developed on 3.13) | `py --version` |
| This repository, branch `claude/laughing-einstein-nlvqcs` | `git pull` |
| The game root: the folder with `r5apex.exe` and `platform/`. Below it is called `<game>` | the launcher's install path |
| Optional: matplotlib, for PNG copies of the SVG plots | `py -m pip install matplotlib` |

## 1. Pre-flight on the PC (no game running)

```powershell
cd <repo>
py research\phase2-prep\run_checks.py --base "<game>\platform\scripts\vscripts"
```

All steps should read `PASS`.

`--base` re-runs the per-VM API check (`hsd_vmcheck.py --strict`) against **your installed** scripts instead of the cloud clone. If it FAILs, the installed script version differs from the analysed commit. Read `research\phase2-prep\results\vmcheck.txt` before loading the mod.

## 2. Install the mod and the console configs

```powershell
# mod: <game>\mods\hsd_movediag\  (the client reads <folder of r5apex.exe>\mods, pluginsystem/modsystem.cpp:30-44;
#      the launcher owns <install>\mods and never sweeps it, launcher ModsStore.cs:33-38, ContentReconciler.cs:658-662)
robocopy research\phase1\mod\hsd_movediag "<game>\mods\hsd_movediag" /E

# console configs: <game>\platform\cfg\user\  (player-owned; the launcher never deletes it)
mkdir "<game>\platform\cfg\user" 2>$null
copy research\phase2-prep\cfg\*.cfg "<game>\platform\cfg\user\"
```

Check that `<game>\mods\hsd_movediag\mod.vdf` exists. There must be no extra files in that folder: a file outside the namespace makes the loader refuse the whole mod (`modsystem.cpp:1357-1555`).

If the dedi runs from a **different** folder (for example via `r5f-host`), copy both items there as well.

In the launcher, tick **Keep my file changes**. The tooltip says it stops replaced files from triggering a full check. It is a precaution; whether it matters for *added* files is unverified.

## 3. Launch (launcher → Play Local, Advanced layout)

Labels come from `launcher/src/R5Flowstate.Shell/Loc/english.json`.

1. **ADVANCED** layout. In the **CLIENT** section tick **Developer**: it launches with `-dev -devsdk`, which unlocks developer ConVars and turns on file logs. In the **DEDICATED SERVER** section also tick **Developer**. Tick **Cheats** (`sv_cheats` on the local server).
   - Without `-devsdk`, `bridge_move_trace` cannot be set: it is `FCVAR_DEVELOPMENTONLY` (`s21-r5sdk/AGENTS.md:175-180`).
   - Without `-devsdk` or `-logfiles` there are no log files (`AGENTS.md:301-310`).
2. Pick a map with flat open ground, a ~4 m wall and a gentle slope. For example, the **Movement Recorder** mode runs on `mp_rr_canyonlands_hu` (`s21-platform/playlists_r5_patch.txt:5767-5794`). Write down the map and playlist you used.
3. **PLAY**. Commands go into the launcher's **Console** tab, which has separate fields for server and client commands (tooltips `tip_console_server` / `tip_console_client`), or into each game's own console.
   - Fallback for dedi commands: `rcon "<command>"` from the client after setting `cl_rcon_address` and `rcon_password` (`engine/client/cl_rcon.cpp:26,42`) **(unverified for Play Local)**.

## 4. In-game smoke test (T0, about 5 minutes)

| # | Console | Command / action | Expect |
|---|---|---|---|
| 1 | client | `exec user/hsd_client` | echo `[HSD] client telemetry on ...` |
| 2 | dedi | `exec user/hsd_dedi` | echo `[HSD] dedi telemetry on ...` |
| 3 | client | `exec user/hsd_runs` | defines aliases `r0` … `r99` |
| 4 | both | look for the mod's init line (console, or `script.log` later) | `[HSD-MD] ver=2 side=cl kind=init ... mod=0.2.0` and `side=sv` |
| 5 | client | `r1`, then stand still 3 s, hold **W** 3 s, release and wait 3 s, jump once, wait 2 s, `r0` | console shows `[MOVE-TRACE]` and `[HSD-MD] ... kind=frame` lines; the dedi shows `kind=evt evt=JUMP` |
| 6 | dedi | `hsd_md_dump_now 1` | 58 `kind=setting` lines plus one `kind=dump ok=.. total=58` |
| 7 | client | `hsd_md_dump_now 1` | the same on the client (`side=cl`) |
| 8 | client | `exec user/hsd_e0_classvars` | 58 `[CLASSVAR] <key> = ...` or `unknown key` lines |

Quit the match (or keep playing) and collect:

```powershell
py research\phase2-prep\tools\hsd_collect.py --game "<game>" --label T0_smoke
py research\phase2-prep\tools\hsd_tel.py smoke research\data\<stamp>_T0_smoke\platform\logs
```

`hsd_collect.py` copies the newest `platform\logs\client\<GUID>` and `server\<GUID>` sessions, Movement Lab profiles and any `scriptdump_*` into `research\data\<stamp>_<label>\`. It is read-only on the game folder, and then it writes `report\`.

**T0 passes when `smoke` prints 11/11 PASS.** Commit `research\data\<stamp>_T0_smoke\report\` (and, if they are small enough, the logs).

## 5. Where things land

| What | Path |
|---|---|
| client logs | `<game>\platform\logs\client\<GUID>\message.log` (`[MOVE-TRACE]`, `[CLASSVAR]`), `script.log` (`[HSD-MD]`), rotated as `message.1.log` … |
| dedi logs | `<dedi root>\platform\logs\server\<GUID>\...` |
| settings CSV from `hsd_md_dump` | `scriptdump_hsd_movediag_settings.csv` somewhere on the GAME search path **(unverified; `hsd_collect.py` searches the root 3 levels deep)** |
| Movement Lab profiles | `<game>\platform\cfg\movementlab\*.csv` (`gameui/IClassVarLab.cpp:18`) |

## 6. Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| No `kind=init` line on a side | mod not loaded on that engine | Search the console or logs for `[MOD-LOAD]`, `[MOD-OWN] ... Refusing the mod`, `Mod settings ... skipping` and `[MOD-SCRIPT]`. Check that `mods\hsd_movediag\mod.vdf` exists and `mods\mods.vdf` does not disable `HSD_MoveDiag`. |
| Level fails to load / script compile error that mentions `hsd_movediag__movediag.gnut` | an API name missing in that VM | Remove `<game>\mods\hsd_movediag`, keep the logs (`script.log`, `script_warning.log`), and report the line. The static check covers only names the base scripts use. |
| `Shutdown host game` / kicked right after spawn | uncaught server script error (`AGENTS.md:202`) | Every server body is in `try/catch`, so this should not happen. Collect the dedi `script.log` and remove the mod. |
| `kind=error ... msg=the index 'X' does not exist` | method X missing at run time; contained | Note it in `VALIDATION-REPORT.md`. The field reads `-1` / `-9` / `nan`. |
| `Unknown command: bridge_move_trace` or it will not change | not started with Developer (`-devsdk`) | Tick Developer for that side and relaunch. |
| `hsd_md_*` unknown | mod ConVar not registered | The mod falls back to defaults (enable 1, traces 0). Set `hsd_md_cl_trace` by other means, or use only MOVE-TRACE. |
| No `platform\logs\...\<GUID>` folder | no `-devsdk` / `-logfiles` | Relaunch with Developer. |
| Kicked with `#SDK_MODS_POLICY` | dedi `sv_modPolicy 2` or a required mod missing (`engine/server/mod_policy_gate.cpp`) | Set `sv_modPolicy 1` (default, `engine/host_state.cpp:622`) on the dedi. |
| `smoke` FAIL "client cmds with a dedi line" | dedi trace off, or the dedi log was not collected | `exec user/hsd_dedi`; pass `--server-game` to `hsd_collect.py` if the dedi folder differs. |
| `smoke` FAIL "dt_est vs FrameTime" | collisions while moving, or MOVE-TRACE and HSD from different moments | Repeat T0 in open terrain. |
| `W_TELEPORT` warnings | respawn / ring / teleport during a run | Ignore when it lines up with a respawn; otherwise check `W_SEQ_GAP`. |

## 7. Turning things off

`exec user/hsd_off` on both consoles. To remove the mod, delete `<game>\mods\hsd_movediag`. Nothing else was changed.
