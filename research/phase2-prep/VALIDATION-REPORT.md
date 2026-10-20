# VALIDATION-REPORT — verified, unverified and blocked (Phase 1.5)

**Scope.** Everything done in the cloud for tomorrow's local session.

- No game binary was run.
- No game files were downloaded.
- Nothing touched an online service.
- All measurement-like numbers in this report come from SYNTHETIC fixtures (model SYNTH-1). They show that the tools recover *known inputs*; they say nothing about Apex.

Source commits used for static checks:

- `s21-r5sdk` `10077bb` (s21-unify)
- `s21-platform` `9b21dc9`
- `launcher` `00fd923`

## 1. Test commands and actual results

Run on: Python 3.13.16, Linux cloud container. The full log is in `results/CHECKS.md`; per-test output is in `results/unittest.txt`.

<!-- BEGIN RESULTS -->
`python3 research/phase2-prep/run_checks.py` gave **10/10 PASS** (exit 0). The commands, as listed in `results/CHECKS.md`:

| # | Command | Outcome |
|---|---|---|
| 1 | `python -m unittest discover -s research/phase2-prep/tests -v` | **52 tests, OK** (about 34 s) |
| 2 | `python research/phase1/tools/hsd_movelog.py selftest` | `selftest ok` (now includes a `-nan(ind)` case) |
| 3 | `python research/phase1/tools/hsd_modlint.py research/phase1/mod/hsd_movediag` | `0 error(s)` |
| 4 | `python research/phase2-prep/tools/hsd_vmcheck.py research/phase1/mod/hsd_movediag --base <s21-platform>/scripts/vscripts --strict` | `0 error(s)`. 1302 base files indexed; 63 name×VM uses checked, every one `DEF` or `USE`, none `WEAK`/`NONE` (`results/vmcheck.txt`) |
| 5 | `python research/phase2-prep/tools/hsd_tel.py validate .../fixtures/synthetic/platform/logs --quiet` | `files=4 rows=6302 errors=0 warnings=0 infos=3`, exit 0 |
| 6 | `python research/phase2-prep/tools/hsd_tel.py validate .../fixtures/synthetic/faulty` | `errors=3 warnings=5`, exit 2 (expected). All 7 injected defect classes reported |
| 7 | `python research/phase2-prep/tools/hsd_tel.py report .../fixtures/synthetic/platform/logs -o results/synthetic_report` | `rows=6302 events=74 runs=9 errors=0 warnings=0` |
| 8 | `python research/phase2-prep/tools/hsd_tel.py schema -o research/phase2-prep/TELEMETRY-SCHEMA.json` | written |
| 9 | `python research/phase2-prep/tools/hsd_tel.py smoke .../fixtures/synthetic/platform/logs` | `11/11 smoke checks passed [SYNTHETIC - not Apex data]` |
| 10 | `python research/phase2-prep/tools/check_refs.py --src-root <clones>` | `refs: ok=437, ambiguous=59, bare_name=3`; 0 missing, 0 out of range |

About the reference check:

- `ambiguous` means a bare basename matches several files (for example client and server `mantle_boost.cpp`) and at least one of them has the cited lines. That check is weaker.
- `bare_name` means an output file name mentioned in prose.
- The check proves the files and line numbers exist, not that the text at those lines says what the document claims. The key claims were read directly during the audit.
<!-- END RESULTS -->

## 2. Diagnostic mod audit (HSD.MoveDiag v0.1 → v0.2)

### 2.1 Verified statically against the loader / SDK / base scripts

| # | Item | Result | Evidence |
|---|---|---|---|
| M1 | Folder layout, `mod.vdf` keys, id `HSD.MoveDiag` (4–32 chars, `[A-Za-z0-9._]`), namespace `hsd_movediag`, every file owned | pass (`hsd_modlint.py` 0 errors; the broken-copy test fails as expected) | `pluginsystem/modsystem.cpp:895-1038,1357-1555` |
| M2 | `scripts.rson`: brace-less, plain entries, `When: "SERVER \|\| CLIENT"` (the same form as the base surf block) | pass | dedi path `vscript/vscript.cpp:401-507`; **client splices the mod rson text into the base compile list** `vscript/vscript_s21_override.cpp:467-560`; base example `s21-platform/scripts/vscripts/scripts.rson:2977-2982` |
| M3 | Entry points `CodeCallback_HSD_MoveDiag_ModInit` / `ClientCodeCallback_HSD_MoveDiag_ModInit` (id with `.`→`_`, case kept) | pass | `game/shared/pluginsystem/modsystem.cpp:81-85`; `vscript/languages/squirrel_re/vsquirrel.h:100-108`; `pluginsystem/modsystem.cpp:442-446` |
| M4 | ModInit timing: once per level per VM, from `SV_CL_Init` (maps) or `Shared_Lobby_Init` (lobby). It runs **before** `Server_Init`/`Client_Init` and after `CodeCallbacksShared_Init` | verified; v0.1's comment ("two init chains in one VM") was wrong and is fixed | `s21-platform/scripts/vscripts/_sh_init.gnut:30-43,85-91,965-990` |
| M5 | Mod ConVars are registered on **each** engine in `Activate()` (not `CLIENT_DLL`-guarded). Flag string `RELEASE` is the exact map key (case-sensitive) | verified | `pluginsystem/modsystem.cpp:771-773,1043-1137`; `tier1/cvar.cpp:12,40,76-99` |
| M6 | Every global function and constant used in a VM has a base-script use compiled in that VM; every method has a base use in that VM | pass (`hsd_vmcheck.py --strict` 0 errors, 0 WEAK; table in `results/vmcheck.txt`) | `tools/hsd_vmcheck.py` |
| M7 | Client code avoids `IN_BACK`, `IN_MOVELEFT`, `IN_MOVERIGHT`, `IN_SPEED`, `IN_DODGE` (SERVER-only evidence) and uses `GetInputAxisForward/Right` (both VMs) | fixed in v0.2 | `vmcheck --why` output: e.g. `IN_MOVELEFT` only `gamemodes/fs_1v1/_input_detector.nut:55` (SERVER) |
| M8 | Movement events: `AddPlayerMovementEventCallback` and the 12 `CodeCallback_OnPlayer*` dispatchers exist (SERVER VM only); a second add asserts, so registration is once per entity | verified | `_codecallbacks_common.gnut:958-970,1006-1139`; `scripts.rson:630-637` |
| M9 | Error containment: an uncaught server-VM error schedules `HS_GAME_SHUTDOWN`. v0.2 wraps every server callback/thread body in `try/catch` and converts errors with `string( e )` | fixed in v0.2 (v0.1 had no containment) | `s21-r5sdk/AGENTS.md:202-207`; pattern `ai/_ai_utility.gnut:781-783`; `return`/`continue` inside `try` appear 55×/11× in the base scripts |
| M10 | `AddClientCommandCallback` callbacks return `void` | verified | `_codecallbacks_common.gnut:751` |
| M11 | Settings getters: `GetPlayerSettingFloat` (both VMs), `GetPlayerSettingInt` (SERVER evidence only, so `#if SERVER`), `GetPlayerSettingString` (both). `GetPlayerSettingBool` has **no** base use and is not called | verified | `vmcheck` sites: `_script_movers.gnut:2180`, `weapons/mp_ability_holopilot.nut:571`, `_utility_shared.nut:4378` |
| M12 | `DevTextBufferDumpToFile` has an **unguarded** SERVER use (not DEVELOPER-only); the SDK keeps the base name and prefixes `scriptdump_` | verified | `survival_loot.gnut:8538`; `vscript/script_convar_guard.cpp:300-341,579-600` |
| M13 | `SetConVarInt("hsd_md_dump_now", 0)` is not write-locked for scripts | verified | `vscript/script_convar_guard.cpp:36-90` (locked names/prefixes) |
| M14 | `printt` reaches `script.log` with a `Script(C|S):` prefix; SDK `Msg` reaches `message.log` with `Native(C|S):`; every file line has a `[YYYY-MM-DD HH:MM:SS.mmm]` stamp | verified in source (not observed) | `core/logdef.cpp:50-67,248-267`; `core/logger.cpp:150-200,380-410`; `public/tier0/dbg.h` |
| M15 | An extra client mod does not block joining a local dedi under the default `sv_modPolicy 1` (only required mods are enforced) | verified in source | `engine/host_state.cpp:622`; `engine/server/mod_policy_gate.cpp` |
| M16 | Install locations: mods at `<folder of r5apex.exe>/mods` (client) and launcher `<install>/mods`, which the launcher never sweeps; configs in `platform/cfg/user/` (player-owned, `exec user/<stem>` precedent) | verified in source | `pluginsystem/modsystem.cpp:30-44`; `launcher/src/R5Flowstate.Content/ModsStore.cs:33-38`; `ContentReconciler.cs:658-662`; `R5Flowstate.Host.Core/InstanceCfg.cs:4-22` |

### 2.2 v0.2 changes, each traceable to a finding above

- `ver=2`, `run=`, `seq=` on every line.
- `ent=` replaces player names, which may contain spaces and broke tokenization.
- Velocity key is now `vel=`.
- Client frame lines add `ft=` (FrameTime), `ang=` (EyeAngles; move-intention construction per `sh_doors.nut:1577-1580`), `sprint=`, `crouch=`, held jump/duck/forward and the input axes.
- Time is printed with 5 decimals (it was 4, which gave about 1.4 % dt jitter at 144 fps).
- `hsd_md_run` and `hsd_md_dump_now` ConVars: dedi-console levers that need no client→server command routing.
- The client sampler starts from ModInit (precedent `sh_surf_movement.gnut:77`). Lobby levels are skipped.

## 3. Telemetry and analysis pipeline — verified on SYNTHETIC data

| Capability | Evidence (synthetic) |
|---|---|
| Parse SDK file logs: timestamps, `Native/Script(C|S)` side tags, ANSI console copies, rotated `message.N.log` order, MSVC NaN/Inf spellings | `tests/test_parse.py` (13 tests) |
| Derived columns: `dt_est` matches the true 1/144 s within 2e-5 s above 100 u/s; dedi run labels inherited by `cmd` (100 % match) | `tests/test_derive_validate.py` |
| Malformed or missing data: all 7 injected defect classes flagged; the clean fixture has 0 errors and 0 warnings | `TestValidate` |
| Recover the SYNTH-1 constants (they are made-up values, not Apex): see the table below | `tests/test_analysis.py` |
| Events: 6 takeoffs, 6 landings, 1 slide start/end per client stream; 6 server JUMP events; 4 hop pairs | `TestFits.test_events_and_hops` |
| Run comparison, census (3 readers, mismatch flag), smoke checks, plots (well-formed SVG with a SYNTHETIC banner) | `TestFits`, `TestCensus`, `TestSlidesAndSmoke`, `TestPlot` |
| Unity contract export/check/compare: identical trial passes; +10 u shift and a dropped LAND fail exactly the position and event checks; axis mapping | `TestContract` |
| Determinism: regenerating the fixtures is byte-identical | `TestDeterminism` |
| Static tools: loader-rule lint, per-VM checker (positive and negative), log collector | `tests/test_cli_and_tools.py` |
| Docs: generated schema table is current; every `path:line` reference resolves | `tests/test_docs.py` |

Fitted constants on the synthetic fixtures:

| Fitted on SYNTHETIC fixtures | True SYNTH-1 value | Recovered |
|---|---|---|
| ground accel (linear) | 1800 u/s² | 1799.9 (HSD), 1800.0 (MT cl), 1799.6 (MT sv) |
| friction k / stopspeed | 5.0 / 100 | 5.09 / 96 (1 % grid) |
| air cap / accel (flat form) | 40 / 2400 | 39.97 / 2400.3 |
| gravity / take-off vz | 750 / 289.83 | 750.0 / 289.83 |
| slide decel | 150 u/s² | 150.0 |

## 4. Unverified — needs the game (in priority order)

| # | Item | Why it matters | How tomorrow checks it |
|---|---|---|---|
| U1 | The mod **compiles** in both VMs (Respawn Squirrel; no compiler for this dialect exists in the cloud) | a compile failure can stop the level loading | LOCAL-SETUP §4 step 4: both init lines present |
| U2 | Methods resolve at run time on the client: `IsOnGround`, `IsSliding`, `IsSprinting`, `IsCrouched`, `EyeAngles`, `IsInputCommandHeld`, `GetInputAxis*` | otherwise the fields read `-1`/`nan` | `smoke` "no -1"; `kind=error` lines |
| U3 | `try/catch` contains errors raised by natives | containment depends on it | any `kind=error` line instead of a crash |
| U4 | Mod ConVars exist and `GetConVarInt`/`SetConVarInt` work on them | levers and run labels | `hsd_md_run` changes show as `kind=run` lines |
| U5 | The S3 dedi fires `ePlayerMovementEvents` callbacks | server events | `smoke` "HSD dedi movement events" |
| U6 | Log destinations and prefixes as read from source (`script.log`/`message.log`, `Script(C):`) | parser side detection | `smoke`; `W_SIDE_UNKNOWN` absent |
| U7 | `bridge_classvar_get` output matches `classvar_natives.cpp:282-289` | E0 census | `census.csv` populated |
| U8 | `GetPlayerSettingFloat` returns live (class-var) or setfile values | E0 interpretation | E0: compare with `bridge_classvar_get` |
| U9 | `drv_dt_est` assumption (origin += post-velocity × frametime) | MT time axis | `smoke` dt_est/FrameTime ratio |
| U10 | Step semantics: held inputs sampled after the predicted move belong to that move | Unity replay alignment | E2 air fit residuals; T0 inspection |
| U11 | Client-console → dedi routing for `hsd_md_dump` / `hsd_md_mark`; `exec user/...`, `alias`, `echo`, `bind MWHEELDOWN` | convenience only | try once; alternatives are documented |
| U12 | The launcher **Developer** checkbox adds `-dev -devsdk` (read from the launcher source, `R5Flowstate.Spawn/LaunchArgs.cs:155-162,294-301`) | DEVELOPMENTONLY ConVars, file logs | `bridge_move_trace 1` accepted |
| U13 | Where `scriptdump_hsd_movediag_settings.csv` lands | optional CSV | `hsd_collect.py` search |
| U14 | `FrameTime()` semantics (last frame vs current) | `dt` provenance | compare `ft` against consecutive `t` deltas in `rows.csv` |

## 5. Blocked in the cloud

- Running any Windows game binary, or loading the mod. This is out of scope by design.
- Reading `r5flowstate.org` docs: the proxy refuses the tunnel (HTTP 403). The rules come from the loader source instead.
- A Squirrel compile check for the Respawn dialect: the stock Squirrel 3 compiler does not accept `global function`, typed declarations or `#if`. `hsd_vmcheck.py` covers name existence only.

## 6. Corrections to Phase 1 (verifiable errors only)

| Where | Was | Now | How found |
|---|---|---|---|
| `research/phase1/Movement-Analysis.md` (auto bhop bullet) <!-- refcheck:skip --> | `game/client/autobunnyhop.cpp:3-6,58-70` | `:3-6,23-35` (the file has 36 lines; the old numbers came from a concatenated listing) | `check_refs.py` line_out_of_range |
| `research/phase1/Architecture.md` §3.3 | `autobunnyhop.cpp` "C:56" | `game/client/autobunnyhop.cpp:21` | same cause, manual follow-up |
| `research/phase1/tools/hsd_movelog.py` | `-nan(ind)` lines silently dropped | parsed as NaN (selftest extended) | review |
| mod v0.1 comment | "reached from more than one init chain" | once per level per VM (map or lobby path) | M4 |

Additions that refine Phase 1 (not errors):

- The client loads mod scripts by splicing the rson (M2).
- `sv_modPolicy` defaults to 1 (M15).
- Mods and configs live in launcher-safe folders (M16).
- Logs are split per channel with a timestamp prefix (M14).

## 7. Tomorrow — ordered checklist

1. `git pull`; `py research\phase2-prep\run_checks.py --base "<game>\platform\scripts\vscripts"` → all PASS (this re-checks the mod against **your** installed scripts).
2. Copy `research\phase1\mod\hsd_movediag` → `<game>\mods\hsd_movediag`, and `research\phase2-prep\cfg\*.cfg` → `<game>\platform\cfg\user\`.
3. Launcher → ADVANCED → tick **Developer** (client and dedi) and **Cheats** → PLAY on a flat open map.
4. Client: `exec user/hsd_client`, `exec user/hsd_runs`. Dedi: `exec user/hsd_dedi`. Confirm both `kind=init` lines.
5. **T0**: `r1`, then stand / walk / stop / jump, then `r0`; quit; `hsd_collect.py --label T0_smoke`; `hsd_tel.py smoke` → 11/11. If not, use LOCAL-SETUP §6 and stop here.
6. **E0** census (r2, r3) → `census.csv`.
7. **E1** ground (r11–r26) → `summary.csv`, `fit-ground`.
8. **E2** air (r31–r46) → `fit-vertical`, `fit-air` (check that `yaw` and `ax_*` are present).
9. **E4** hops (r51–r62), **E5** slides (r71–r81).
10. Record P/M outcomes and the U-items resolved in §8, export one trial per experiment, commit `research\data\...\report\`.

## 8. Local session results

_Empty until the local session. For each item: date, build, run ids, P/M outcome, numbers ± spread, anomalies._
