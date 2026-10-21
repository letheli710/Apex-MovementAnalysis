# TELEMETRY-SCHEMA — HSD movement telemetry (schema `hsdtel1`)

This file defines what is recorded, where it lands, how each line is formatted and what each CSV column means. The parser is `tools/hsdtel/`, driven through `tools/hsd_tel.py`.

The machine-readable copy is `TELEMETRY-SCHEMA.json`, regenerated with `python tools/hsd_tel.py schema -o TELEMETRY-SCHEMA.json`. The column table at the end is generated from `tools/hsdtel/schema.py`, and `tests/test_docs.py` fails when the two drift apart.

## 1. Provenance classes (every column has exactly one)

| class | prefix | meaning |
|---|---|---|
| **meta** | – | Written by the parser about where a row came from (file, line). |
| **obs** | none | **Observed.** Printed by the SDK/engine, or read by the mod from an engine API with no arithmetic: positions, velocities, flags, `Time()`, `FrameTime()`, input states, the log-sink wall clock. |
| **ing** | `ing_` | **In-game derived.** Computed by the HSD.MoveDiag mod while running (airtime, takeoff/peak/landing speed). |
| **drv** | `drv_` | **Offline derived.** Computed afterwards by hsdtel: speeds, accelerations, dt estimates, events, run assignment, quality flags. |

Rule: an analysis result must name the columns it used. Any conclusion that rests on `drv_` or `ing_` values inherits the assumptions written in those columns' descriptions.

## 2. Sources and where they land

| source | producer | file (with `-devsdk` or `-logfiles`) | rate | key evidence |
|---|---|---|---|---|
| `MT` | SDK `bridge_move_trace 1` | `platform/logs/<client\|server>/<GUID>/message.log` (rotates at 10 MiB, 16 files: `message.N.log`, larger N = older) | one line per usercmd per player (client: first-time-predicted commands; `rp=1` replays with `bridge_move_trace_replays 1`) | `s21-r5sdk/src/game/{server,client}/move_sim_trace.cpp`; `core/logdef.cpp:50-67`; `core/logdef.h:13,19` |
| `HSD` | HSD.MoveDiag v0.2 (`printt`) | `.../script.log` | client: one per render frame (`hsd_md_cl_trace 1`) plus edges; dedi: events plus optional 20 Hz frames | `research/phase1/mod/hsd_movediag/` |
| `CV` | SDK `bridge_classvar_get <key>` | client `.../message.log` | on demand | `s21-r5sdk/src/game/client/classvar_natives.cpp:251-293` |
| `LOG` | engine level-load lines: dedi `CHostState::State_NewGame: Loading level: '<map>'`, client `[BRIDGE] CONNACCEPT map='<map>'` | `.../message.log` | once per level load / connection | `engine/host_state.cpp:475`; `engine/client/net_bridge_install.cpp:8537` |

**Sessions.** Every row carries `session`, the `<GUID>` folder its file sits in. One folder is one game process, so two recordings (or a client and a dedi of different runs) never share a stream, even when their command numbers overlap. Loose files outside a GUID folder take the name of their folder: keep each session's copies in a folder of its own.

The file sink prefixes every line with `[YYYY-MM-DD HH:MM:SS.mmm] ` and a context tag: `Native(C):`, `Native(S):`, `Script(C):`, `Script(S):` (`public/tier0/dbg.h`, `core/logger.cpp:380-410`). The parser takes `side` from that tag. A console copy instead carries ANSI colour codes and no timestamp; the parser strips the colours, and `--side` covers lines with no tag.

**Time bases.**
- `t` (HSD) is the script game clock, `Time()`.
- `wall` is when the log line was written. It is only good for coarse alignment across files, and the dedi writes in 50 ms command batches.
- `MOVE-TRACE` has **no time field and no frametime**. Per-command dt is estimated as `drv_dt_est`.

## 3. Line formats

### 3.1 `[MOVE-TRACE]` (SDK, unchanged)

```
[MOVE-TRACE] cmd=%d ent=%d ms=%.3f spr=%d duck=%d slide=%d ge=%d fwd=%.3f sd=%.3f b=%08X msc=%.4f o=%.3f %.3f %.3f v=%.3f %.3f %.3f po=%.3f %.3f %.3f pv=%.3f %.3f %.3f[ rp=1]
```

- `o`, `v`, `ge`, `slide`, `spr` and `duck` are read **before** `FullWalkMove`; `po` and `pv` are read **after** it.
- `b` is the held-button mask (`in_buttons.h`).
- On the client, `ent` is always 1.
- NaN/Inf may be printed as `-nan(ind)`, `nan`, `inf` or `1.#INF`. The parser accepts all of these and flags the row `nonfinite`.

### 3.2 `[HSD-MD] ver=2` (mod)

Common head: `[HSD-MD] ver=2 side=<cl|sv> kind=<kind> run=<hsd_md_run> seq=<per-VM counter>`.

Values contain no spaces. Vectors are comma-separated (`o=x,y,z`, `vel=x,y,z`, `ang=pitch,yaw`). `msg=` is always last and takes the rest of the line.

Shared state tokens: `o= vel= spd2d= vz= ground= slide= sprint= crouch=`. A flag of `-1` means the API call threw, so the value is unknown, not 0. `spd2d` and `vz` are printed for humans only; the parser recomputes speed from `vel`.

| kind | side | extra keys |
|---|---|---|
| `init` | cl, sv | `mod=0.2.0` |
| `run` | cl, sv | `prev= t=` (printed when `hsd_md_run` changes) |
| `frame` | cl | `t= ft=` + state + `ang= in_jump= in_duck= in_fwd= ax_fwd= ax_right=` (`ax_*=-9` means unavailable) |
| `frame` | sv | `t= ft= ent= bot=` + state (`hsd_md_sv_trace 1`, 20 Hz) |
| `evt` | sv | `evt=<JUMP\|DOUBLE_JUMP\|DODGE\|LEAVE_GROUND\|TOUCH_GROUND\|MANTLE\|BEGIN/END_WALLRUN\|BEGIN/END_WALLHANG\|BEGIN/END_SLIDE\|RESPAWN> t= ent= bot=` + state |
| `takeoff` | cl | `t= groundtime= hop=` + state (`ing_` values) |
| `land` | cl | `t= airtime= takeoff= peak= land= gain= hop=` + state (`ing_` values) |
| `mark` | sv | `t= ent= label=` + state |
| `setting` | cl, sv | `ent= key= vtype=<float\|int\|string\|ERR> value=` (`-` when empty) |
| `dump` | cl, sv | `ent= ok= total=` |
| `dumpfile` | sv | `file=<0\|1>` (`DevTextBufferDumpToFile` result) |
| `error` | cl, sv | `where= count= msg=<rest of line>` (a contained script error, at most 50 per VM) |

Version 1 lines (Phase 1 prototype, no `ver=`, velocity as `v=`) are still parsed.

### 3.3 `[CLASSVAR]` (SDK)

- `[CLASSVAR] <key> = <value> (type=<n> off=<n>)` becomes `kind=classvar`, `vtype=cvtype<n>`. Types are 0 bool, 1 int, 2 float, 3 float2, 4 float3, 5–7 string (`game/server/classvar_natives.cpp:190-224`).
- `[CLASSVAR] unknown key '<key>'` becomes `vtype=unknown`.
- Other `[CLASSVAR]` chatter is ignored.

## 4. Quality checks (`hsd_tel.py validate`)

| code | severity | meaning |
|---|---|---|
| `E_MALFORMED_MT` / `E_MALFORMED_HSD` | error | a tagged line that does not parse (truncated, edited, bad vector) |
| `E_MISSING_FIELD` | error | a v2 line lacks a key that its kind requires |
| `E_NONFINITE` | error | NaN/Inf in a kinematic field |
| `W_SEQ_GAP` | warning | `[HSD-MD]` lines were lost (seq jumped) |
| `W_TELEPORT` | warning | position jump between consecutive samples larger than speed×dt×3 + 64 u (respawn, `SetOrigin`, or lost lines) |
| `W_API_MISSING` | warning | rows with `ground` or `slide` = -1 |
| `W_SCRIPT_ERROR` | warning | the mod caught and reported a script error |
| `W_DUP_CMD` | warning | the same command number was logged twice without `rp=1` within one reset batch (`drv_batch`) |
| `W_TIME_BACKWARDS` | warning | `t` decreased within one stream |
| `W_JOIN_LOW` | warning | fewer than 90 % of client commands are joined to a dedi line for the same usercmd (join key below, §5) |
| `W_JOIN_AMBIGUOUS` | warning | client commands with more than one dedi candidate (overlapping sessions or several dedi entities that the origin cannot tell apart); they stay unjoined |
| `W_SIDE_UNKNOWN`, `W_SIDE_MISMATCH`, `W_HSD_VERSION`, `W_HSD_KIND` | warning | provenance problems |
| `I_*` | info | expected conditions: bursts, reset batches (`I_RESET_BATCH`), replays, seq reset after a map change, settings key unreadable, no MT or no HSD rows, the join summary (`I_JOIN`) |

Exit code: `validate` and `report` return 2 when any error is present.

## 5. Derivations and their assumptions

- `drv_dt_est` = `|po_xy − o_xy| / |pv_xy|`, only when `|pv_xy| > 20 u/s`.
  - It assumes origin += post-velocity × frametime with no collision.
  - Positions are printed with 3 decimals, so the relative error is about 0.0005 u divided by the displacement.
  - On real data, check it against `ft` from the HSD client frames before trusting it.
- `drv_burst`: a command-number jump greater than `--burst-gap` (default 8) starts a new burst. Toggling `bridge_move_trace` off and on between trials makes bursts line up with trials.
- `drv_batch` (reset batch, per MT stream = side, session, entity). A new batch starts at a non-replay row when
  1. its `cmd` is lower than the previous non-replay `cmd` (the counter restarted: reconnect, map restart), or
  2. `cmd` jumped forward by more than `--burst-gap` **and** a reset marker lies between the two rows: a level load (`LOG` map) or a script VM start (`kind=init`) of the same side and session, a dedi `evt=RESPAWN` (both by wall clock), or a position jump larger than 64 u from the previous post-move origin.

  Contiguous commands never start a batch. A respawn or teleport that keeps the numbering cannot collide, and splitting there would only break the join.
- **Client/dedi join** (`drv_join` = `ok`/`none`/`ambiguous`, `derive.join_sides`). Each side's key is `(session, ent, drv_batch, cmd)`. The two sides write different session folders, and the client always prints `ent=1` (`game/client/move_sim_trace.cpp:189-198`), so the client key is mapped onto the dedi keys:
  1. The candidates are dedi rows with the same `cmd` whose `(session, ent, batch)` segment is live at the client row's wall time (segment span ± 5 s). Without wall clocks (console copies), segments pair in order.
  2. When there are several candidates, the one whose pre-move origin is within 8 u wins while all others are farther. Failing that, the one nearest in wall time wins when the next is more than 1 s farther.
  3. Otherwise the row is `ambiguous`. A dedi row claimed by two client rows makes both ambiguous.

  `validate` (`I_JOIN`/`W_JOIN_LOW`) and `smoke` report `joined / first-time client commands`.
- **Client high-water caveat.** The client tags a command as a replay when its number is not above the highest number traced so far in the process, and resets that mark only when numbers drop by more than 100000 (`game/client/move_sim_trace.cpp:163-166`, `game/client/move_sim_trace.cpp:200-201`). After a reconnect inside one client process, the new low-numbered commands are therefore logged as `rp=1` (or not at all) until they pass the old maximum. The client stream then shows no restart, while the dedi does. The join still pairs them by wall time, but replay-only stretches stay unjoined.
- `drv_run`, in order of precedence:
  1. HSD rows use `r<run>`.
  2. Client MT rows use the client `hsd_md_run` active at their wall time in the same session.
  3. Dedi MT rows inherit the label of the client MT row they are joined to, whenever that client session has `hsd_md_run` marks. This includes `b<burst>` when the client was outside a run, so a dedi whose `hsd_md_run` was never reset cannot extend a trial.
  4. Otherwise the dedi `hsd_md_run` of the same session at their wall time, else `b<burst>`.
- `drv_wish_yaw` = `yaw + atan2(−ax_right, ax_fwd)`. This is the same construction the base scripts use for a move intention (`sh_doors.nut:1577-1580`). It is empty when there is no input.
- Events:
  - TAKEOFF, LAND, SLIDE_START and SLIDE_END are edges of the per-stream `ground` and `slide` flags. In MT these are pre-move flags, so an edge marks the first command that *starts* in the new state.
  - JUMP_PRESS is the `IN_JUMP` press edge in MT.
  - `SV_<evt>` are the mod's server events, passed through.

## 6. Unified table columns (generated)

<!-- BEGIN GENERATED COLUMNS -->
| column | provenance | unit | description |
|---|---|---|---|
| `file` | meta |  | source log file (basename) |
| `line_no` | meta |  | 1-based line number in that file |
| `source` | meta |  | MT = SDK [MOVE-TRACE]; HSD = HSD.MoveDiag mod; CV = SDK [CLASSVAR] bridge_classvar_get output; LOG = engine level-load line |
| `side` | obs |  | cl = S21 client prediction, sv = S3 dedi; from the log prefix Native(C)/Script(S)/... or --side (LOG rows: from the folder) |
| `session` | meta |  | log session: the GUID folder of the file (platform/logs/<side>/<GUID>/), else the name of its folder; one game process |
| `kind` | obs |  | cmd (MT) / classvar (CV) / map (LOG) / frame / evt / takeoff / land / mark / run / setting / dump / dumpfile / init / error |
| `wall` | obs | s | log-sink wall clock from the [YYYY-MM-DD HH:MM:SS.mmm] file prefix, as seconds since 1970 reading the logged local time as if UTC; ms resolution; time the line was written, not simulation time; empty on console copies |
| `run` | obs |  | HSD: value of hsd_md_run when the line was printed |
| `seq` | obs |  | HSD: per-VM line counter (gaps = lost lines) |
| `t` | obs | s | HSD: script Time() (game clock) |
| `ft` | obs | s | HSD: script FrameTime() |
| `cmd` | obs |  | MT: usercmd command_number |
| `ent` | obs |  | MT ent= / HSD ent= entity index |
| `bot` | obs |  | HSD server: 1 = fake client |
| `replay` | obs |  | MT client: 1 = re-predicted command (rp=1) |
| `ox` | obs | u | origin x (MT: before the move) |
| `oy` | obs | u | origin y |
| `oz` | obs | u | origin z |
| `vx` | obs | u/s | velocity x (MT: before the move) |
| `vy` | obs | u/s | velocity y |
| `vz` | obs | u/s | velocity z |
| `pox` | obs | u | MT: origin x after the move |
| `poy` | obs | u | MT: origin y after the move |
| `poz` | obs | u | MT: origin z after the move |
| `pvx` | obs | u/s | MT: velocity x after the move |
| `pvy` | obs | u/s | MT: velocity y after the move |
| `pvz` | obs | u/s | MT: velocity z after the move |
| `pitch` | obs | deg | HSD client: EyeAngles().x |
| `yaw` | obs | deg | HSD client: EyeAngles().y |
| `ground` | obs |  | 1/0; MT ge= (ground entity before the move); HSD IsOnGround(); -1 = API unavailable |
| `slide` | obs |  | 1/0; MT slide= (before the move); HSD IsSliding(); -1 = unavailable |
| `sprint` | obs |  | 1/0; MT spr=; HSD IsSprinting(); -1 = unavailable |
| `crouch` | obs |  | HSD IsCrouched(); -1 = unavailable |
| `duck` | obs |  | MT duck= m_duckState (0 stand, 2 ducked) |
| `buttons` | obs |  | MT b= m_nButtons (held) as integer; bits per in_buttons.h |
| `fwd` | obs |  | MT fwd= forwardmove |
| `sidemove` | obs |  | MT sd= sidemove |
| `maxspeed` | obs | u/s | MT ms= CMoveData maxspeed |
| `movescale` | obs |  | MT msc= m_cachedMoveScale |
| `in_jump` | obs |  | HSD client IsInputCommandHeld(IN_JUMP); -1 = unavailable |
| `in_duck` | obs |  | HSD client IsInputCommandHeld(IN_DUCK) |
| `in_fwd` | obs |  | HSD client IsInputCommandHeld(IN_FORWARD) |
| `ax_fwd` | obs |  | HSD client GetInputAxisForward(); -9 = unavailable |
| `ax_right` | obs |  | HSD client GetInputAxisRight(); -9 = unavailable |
| `evt` | obs |  | HSD server movement event name |
| `label` | obs |  | HSD mark label |
| `key` | obs |  | HSD setting key |
| `vtype` | obs |  | HSD setting getter that succeeded: float/int/string/ERR |
| `value` | obs |  | HSD setting value as printed; LOG map: the map name |
| `msg` | obs |  | HSD error text |
| `where` | obs |  | HSD error: which mod function contained the error |
| `prev` | obs |  | HSD run: previous run label |
| `ok` | obs |  | HSD dump: keys read successfully |
| `total` | obs |  | HSD dump: keys attempted |
| `dumpfile_ok` | obs |  | HSD dumpfile: DevTextBufferDumpToFile return value |
| `mod` | obs |  | HSD init: mod version |
| `ing_airtime` | ing | s | mod: Time() between sampled takeoff and landing |
| `ing_groundtime` | ing | s | mod: Time() on the ground before a takeoff |
| `ing_takeoff` | ing | u/s | mod: horizontal speed at the takeoff sample |
| `ing_peak` | ing | u/s | mod: max horizontal speed sampled in the air |
| `ing_land` | ing | u/s | mod: horizontal speed at the landing sample |
| `ing_gain` | ing | u/s | mod: land - takeoff |
| `ing_hop` | ing |  | mod: consecutive takeoffs with < 0.1 s ground time |
| `drv_run` | drv |  | trial id: HSD run if present, else MT burst index |
| `drv_burst` | drv |  | MT: index of a contiguous command range (gap > --burst-gap cmds starts a new one) |
| `drv_batch` | drv |  | MT: reset batch within the stream; +1 when cmd goes backwards, or jumps > --burst-gap across a level load / VM start / dedi RESPAWN / position jump (TELEMETRY-SCHEMA.md 5) |
| `drv_join` | drv |  | MT: ok = paired with the other side's line for the same usercmd on (session, ent, drv_batch, cmd); none; ambiguous (more than one candidate) |
| `drv_spd2d` | drv | u/s | hypot(vx, vy) |
| `drv_spd2d_post` | drv | u/s | MT: hypot(pvx, pvy) |
| `drv_dspd2d` | drv | u/s | MT: post - pre horizontal speed within one command |
| `drv_dheading` | drv | deg | MT: change of horizontal velocity direction within one command |
| `drv_dt` | drv | s | HSD: t - previous t of the same side/kind; MT: drv_dt_est |
| `drv_dt_est` | drv | s | MT: /po_xy - o_xy/ / /pv_xy/ when /pv_xy/ > 20 u/s (assumes origin += post velocity * frametime and no collision; positions are printed with 3 decimals, so the relative error is about 0.0005 u / displacement) |
| `drv_accel2d` | drv | u/s^2 | HSD: (spd2d - prev spd2d) / drv_dt; MT: drv_dspd2d / drv_dt_est |
| `drv_pressed` | drv |  | MT: buttons pressed this command vs the previous line of the stream |
| `drv_wish_yaw` | drv | deg | HSD client: yaw + atan2(-ax_right, ax_fwd); empty without input |
| `drv_flags` | drv |  | quality flags: nonfinite/teleport/api_missing |
<!-- END GENERATED COLUMNS -->
