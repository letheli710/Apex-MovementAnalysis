# HSD.MoveDiag v0.2

Observe-only movement telemetry mod for R5Flowstate (S21 client + S3 dedi bridge). It changes no movement values.

**Status: not run in the game.** It has passed static checks only:

- `research/phase1/tools/hsd_modlint.py`: loader rules.
- `research/phase2-prep/tools/hsd_vmcheck.py --strict`: every global, constant and method has a base-script use in the VM that calls it.

See `research/phase2-prep/VALIDATION-REPORT.md` for details.

## Install (Windows, local game)

1. Copy this folder to `<game root>/mods/hsd_movediag/` **on the client install and on the dedi install**. If both use the same root, one copy is enough.
   - The loader scans `mods/<folder>/mod.vdf` (`s21-r5sdk/src/pluginsystem/modsystem.cpp:249-265`).
   - The client splices this mod's `scripts.rson` into its compile list (`vscript/vscript_s21_override.cpp:511-546`).
2. A mod that is not listed in `mods/mods.vdf` is enabled by default (`modsystem.cpp:544-556`).
3. The default `sv_modPolicy 1` enforces only the server's `required_mods.vdf`, so an extra client mod does not block joining (`engine/host_state.cpp:622`, `engine/server/mod_policy_gate.cpp`).

Full procedure: `research/phase2-prep/LOCAL-SETUP.md`.

## Console levers (mod ConVars, both engines)

| ConVar | Default | Effect |
|---|---|---|
| `hsd_md_enable` | 1 | master switch |
| `hsd_md_cl_trace` | 0 | client: one `kind=frame` line per frame; it ends with camera tokens `cpos` / `cang` (camera, with punch and roll), `epos` / `eang` (eye and aim), `vv` (aim vector), `fov` (`cpos=nan` if not readable) |
| `hsd_md_sv_trace` | 0 | dedi: one `kind=frame` line per server frame per player |
| `hsd_md_run <n>` | 0 | trial label copied into every line (`run=`); set it on both consoles |
| `hsd_md_dump_now 1` | 0 | prints the player-settings values once on that engine (`kind=setting`), then resets to 0 |

Client commands handled on the dedi:

- `hsd_md_dump` writes the settings lines plus `scriptdump_hsd_movediag_settings.csv` through `DevTextBufferDumpToFile`.
- `hsd_md_mark <label>`.

Reaching the dedi from the client console has not been verified. `hsd_md_dump_now` on the dedi console does the same job without client-to-server routing.

## Output

Every line looks like this:

```
[HSD-MD] ver=2 side=<cl|sv> kind=<...> run=<n> seq=<n> key=value ...
```

The keys are specified in `research/phase2-prep/TELEMETRY-SCHEMA.md`. Script prints land in `platform/logs/<client|server>/<GUID>/script.log` when the game is started with `-devsdk` or `-logfiles`.

## Turn it into CSV and reports

```
python research/phase2-prep/tools/hsd_tel.py report <game>/platform/logs -o out
```

## Changes from v0.1

- Lines carry `ver=2`, `run=`, `seq=` and the entity index (`ent=`) instead of the player name, which may contain spaces. Velocity is now `vel=`.
- The client frame line adds `ft=` (FrameTime), `ang=` (EyeAngles), `sprint=`, `crouch=`, held jump/duck/forward, and the input axes.
- Every server callback and thread body is inside `try/catch`, because an uncaught server-VM error schedules `HS_GAME_SHUTDOWN` (`s21-r5sdk/AGENTS.md:202`). Contained errors print `kind=error`.
- Settings are read with Float, then Int (server only), then String getters, and the getter that worked is recorded (`vtype=`). `GetPlayerSettingBool` is not used: the base scripts never call it.
- The client sampler starts from ModInit, the same pattern as `sh_surf_movement.gnut:77`, instead of waiting for a spawn callback. Lobby levels are skipped.
- Added the `hsd_md_run` and `hsd_md_dump_now` ConVars.
