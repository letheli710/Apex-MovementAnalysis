# Cloud check run

- date (UTC): 2026-10-20T14:42:05+00:00
- python: 3.13.16 on Linux
- base scripts: /home/user/research-src/s21-platform/scripts/vscripts

All data used below is SYNTHETIC (hsdtel.synth) or static source; no game was run.


## PASS unit tests

```
$ python -m unittest discover -s research/phase2-prep/tests -v
(exit 0, expected 0)
```

```
test_dt_est_matches_synthetic_frametime (test_derive_validate.TestDerive.test_dt_est_matches_synthetic_frametime) ... ok
test_pressed_edges_and_runs (test_derive_validate.TestDerive.test_pressed_edges_and_runs) ... ok
test_spd_and_heading (test_derive_validate.TestDerive.test_spd_and_heading) ... ok
test_wish_yaw (test_derive_validate.TestDerive.test_wish_yaw) ... ok
test_clean_fixture_has_no_errors_or_warnings (test_derive_validate.TestValidate.test_clean_fixture_has_no_errors_or_warnings) ... ok
test_empty_input (test_derive_validate.TestValidate.test_empty_input) ... ok
test_faulty_fixture_flags_every_injected_defect (test_derive_validate.TestValidate.test_faulty_fixture_flags_every_injected_defect) ... ok
test_fixture_counts (test_parse.TestFiles.test_fixture_counts) ... ok
test_rotated_order (test_parse.TestFiles.test_rotated_order) ... ok
test_side_from_path_when_no_prefix (test_parse.TestFiles.test_side_from_path_when_no_prefix) ... ok
test_side_unknown_is_reported (test_parse.TestFiles.test_side_unknown_is_reported) ... ok
test_ansi_console (test_parse.TestLines.test_ansi_console) ... ok
test_hsd_bad_vector (test_parse.TestLines.test_hsd_bad_vector) ... ok
test_hsd_msg_takes_rest_of_line (test_parse.TestLines.test_hsd_msg_takes_rest_of_line) ... ok
test_hsd_v1_land_maps_ing_columns (test_parse.TestLines.test_hsd_v1_land_maps_ing_columns) ... ok
test_hsd_v2_frame (test_parse.TestLines.test_hsd_v2_frame) ... ok
test_mt_basic (test_parse.TestLines.test_mt_basic) ... ok
test_mt_replay_and_prefixes (test_parse.TestLines.test_mt_replay_and_prefixes) ... ok
test_nonfinite_spellings (test_parse.TestLines.test_nonfinite_spellings) ... ok
test_truncated_mt_is_rejected (test_parse.TestLines.test_truncated_mt_is_rejected) ... ok

----------------------------------------------------------------------
Ran 43 tests in 31.413s

OK
```

## PASS phase1 hsd_movelog selftest

```
$ python research/phase1/tools/hsd_movelog.py selftest
(exit 0, expected 0)
```

```
selftest ok
```

## PASS hsd_modlint (loader rules)

```
$ python research/phase1/tools/hsd_modlint.py research/phase1/mod/hsd_movediag
(exit 0, expected 0)
```

```
ok  id=HSD.MoveDiag namespace=hsd_movediag entry-point suffix=_HSD_MoveDiag_ModInit
  ok  entry point ClientCodeCallback_HSD_MoveDiag_ModInit present
  ok  entry point CodeCallback_HSD_MoveDiag_ModInit present
0 error(s)
```

## PASS hsd_vmcheck --strict (per-VM API evidence)

```
$ python research/phase2-prep/tools/hsd_vmcheck.py research/phase1/mod/hsd_movediag --base ../research-src/s21-platform/scripts/vscripts --strict
(exit 0, expected 0)
```

```
SERVER  global  GetPlayerArray                           USE      hsd_movediag__movediag.gnut:384
SERVER  global  IsAlive                                  USE      hsd_movediag__movediag.gnut:358
SERVER  global  IsLobby                                  USE      hsd_movediag__movediag.gnut:260
SERVER  global  IsValid                                  USE      hsd_movediag__movediag.gnut:278
SERVER  global  Length2D                                 USE      hsd_movediag__movediag.gnut:179
SERVER  global  SetConVarInt                             USE      hsd_movediag__movediag.gnut:383
SERVER  global  Time                                     USE      hsd_movediag__movediag.gnut:191
SERVER  global  WaitFrame                                USE      hsd_movediag__movediag.gnut:353
SERVER  global  format                                   USE      hsd_movediag__movediag.gnut:98
SERVER  global  printt                                   DEF      hsd_movediag__movediag.gnut:109
SERVER  method  EndSignal                                USE      hsd_movediag__movediag.gnut:349
SERVER  method  GetEntIndex                              USE      hsd_movediag__movediag.gnut:165
SERVER  method  GetOrigin                                USE      hsd_movediag__movediag.gnut:177
SERVER  method  GetPlayerSettingFloat                    USE      hsd_movediag__movediag.gnut:206
SERVER  method  GetPlayerSettingInt                      USE      hsd_movediag__movediag.gnut:218
SERVER  method  GetPlayerSettingString                   USE      hsd_movediag__movediag.gnut:230
SERVER  method  GetVelocity                              USE      hsd_movediag__movediag.gnut:176
SERVER  method  IsBot                                    USE      hsd_movediag__movediag.gnut:323
SERVER  method  IsCrouched                               USE      hsd_movediag__movediag.gnut:153
SERVER  method  IsOnGround                               USE      hsd_movediag__movediag.gnut:117
SERVER  method  IsPlayer                                 USE      hsd_movediag__movediag.gnut:278
SERVER  method  IsSliding                                USE      hsd_movediag__movediag.gnut:129
SERVER  method  IsSprinting                              USE      hsd_movediag__movediag.gnut:141
SERVER  method  len                                      USE      hsd_movediag__movediag.gnut:243
0 error(s)
```

## PASS validate clean SYNTHETIC fixture

```
$ python research/phase2-prep/tools/hsd_tel.py validate research/phase2-prep/fixtures/synthetic/platform/logs --quiet
(exit 0, expected 0)
```

```
files=4 rows=6302 errors=0 warnings=0 infos=3
```

## PASS validate faulty SYNTHETIC fixture (exit 2 expected)

```
$ python research/phase2-prep/tools/hsd_tel.py validate research/phase2-prep/fixtures/synthetic/faulty
(exit 2, expected 2)
```

```
error E_MALFORMED_MT faulty_client_message.log:16 Native(C): [MOVE-TRACE] cmd=5011 ent=1 ms=300.000 spr=0 duck=0 slide=0 ge=1 fwd=0.000 sd=0.000 b=00000000 msc=1.0000 o=0.000 0.000 0.000 v=0.000 0.000 0.000
error E_MISSING_FIELD faulty_client_script.log:66 kind=frame missing ground
warning W_SCRIPT_ERROR faulty_client_script.log:96 mod contained an error where=sample: the index 'IsSliding' does not exist
warning W_SEQ_GAP faulty_client_script.log:46 1 [HSD-MD] line(s) missing on side cl (seq 44 -> 46)
warning W_SEQ_GAP faulty_client_script.log:96 999903 [HSD-MD] line(s) missing on side cl (seq 95 -> 999999)
info I_SEQ_RESET faulty_client_script.log:97 seq 999999 -> 96 (VM restart/map change)
error E_NONFINITE faulty_client_message.log:26 nonfinite in stream ('MT', 'cl', 'cmd', 1)
warning W_TELEPORT faulty_client_message.log:36 teleport in stream ('MT', 'cl', 'cmd', 1)
info I_REPLAYS faulty_client_message.log:0 41 re-predicted (rp=1) rows in ('MT', 'cl', 'cmd', 1)
warning W_API_MISSING faulty_client_script.log:6 1 row(s) with ground/slide=-1 (method unavailable) in ('HSD', 'cl', 'frame', None)
files=2 rows=4202 errors=3 warnings=5 infos=2
```

## PASS report on SYNTHETIC fixture

```
$ python research/phase2-prep/tools/hsd_tel.py report research/phase2-prep/fixtures/synthetic/platform/logs -o research/phase2-prep/results/synthetic_report
(exit 0, expected 0)
```

```
wrote /home/user/Apex-MovementAnalysis/research/phase2-prep/results/synthetic_report: rows=6302 events=74 runs=9 errors=0 warnings=0
```

## PASS schema export

```
$ python research/phase2-prep/tools/hsd_tel.py schema -o research/phase2-prep/TELEMETRY-SCHEMA.json
(exit 0, expected 0)
```

```

```


**8/8 steps passed.**
