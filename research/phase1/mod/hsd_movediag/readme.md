# HSD.MoveDiag (Phase 1 prototype)

Observe-only movement diagnostic mod for R5Flowstate (S21 client + S3 dedi bridge).
It changes no movement values.

**Status: not run.** It has been written and statically checked (`research/phase1/tools/hsd_modlint.py`) without a game install.

## Install (Windows, local game)

1. Copy this folder to `<game root>/mods/hsd_movediag/`. The loader scans `mods/<folder>/mod.vdf` (`s21-r5sdk/src/pluginsystem/modsystem.cpp:249-265`).
2. A mod that is not listed in `mods/mods.vdf` is enabled by default (`modsystem.cpp:544-556`).
3. Start an offline/local match and open the console.

## What it prints

Every line starts with `[HSD-MD]` and is made of `key=value` tokens.

| side | kind | when |
|---|---|---|
| sv | `evt` | each engine movement event: JUMP, DOUBLE_JUMP, DODGE, LEAVE_GROUND, TOUCH_GROUND, MANTLE, wallrun/wallhang begin/end, BEGIN/END_SLIDE |
| sv | `frame` | every server frame while `hsd_md_sv_trace 1` (about 20 Hz) |
| sv | `setting` / `dump` | after the client command `hsd_md_dump` |
| sv | `mark` | after the client command `hsd_md_mark <label>` |
| cl | `takeoff` / `land` | each ground-to-air and air-to-ground edge of the predicted local player |
| cl | `frame` | every client frame while `hsd_md_cl_trace 1` |

`hsd_md_dump` also writes `scriptdump_hsd_movediag_settings.csv` through `DevTextBufferDumpToFile`. The output folder is whatever the GAME search path resolves; this has not been verified.

## Sending the commands

`hsd_md_dump` and `hsd_md_mark` are server-side client commands (`AddClientCommandCallback`).

- From script, they can be sent with `player.ClientCommand( "hsd_md_dump" )`, the same pattern `cl_movement_recorder.gnut:126` uses.
- From the console, Source normally forwards unknown commands, or `cmd <command>`, to the server. This has not been verified on R5.

## Turn it into CSV

```
python research/phase1/tools/hsd_movelog.py hsd  console.log  -o hsd.csv
```
