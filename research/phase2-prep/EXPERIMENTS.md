# EXPERIMENTS — executable local procedures (T0, E0, E1, E2, E4/E5)

Prerequisite: `LOCAL-SETUP.md` §1–4 are done, so the mod is installed, both engines run with Developer, and the configs are under `platform/cfg/user/`.

Order: **T0 → E0 → E1 → E2 → E4 → E5**. Each experiment validates the pipeline for the next one, so stop and fix problems as soon as a **P** criterion fails.

A dry run of every analysis command works today on the SYNTHETIC fixtures: replace the log path with `research/phase2-prep/fixtures/synthetic/platform/logs`. Those numbers are not Apex data.

## Conventions

- **Run labels.** On the client console type `rN` before a trial and `r0` after it. The aliases come from `cfg/hsd_runs.cfg` and set `hsd_md_run`. Dedi `[MOVE-TRACE]` lines inherit the label through the command number, so labelling the client is enough.
- **One trial = one run number.** Never reuse a number within a session. If a trial goes wrong, type `r0`, note the number as bad, and use the next one.
- **Hands.** Keep the mouse still unless the procedure says otherwise. "Hold W 3 s" means counting about 3 s; exact timing is not needed because the time comes from the logs.
- **Settings to write down once per session:** map and playlist, legend, `fps_max`, and the sprint setting (autosprint, hold or toggle; see the `player_setting_*sprint*` ConVars in `ui/panel_hud_options.nut:298-300`).
- **Collect after each experiment:**
  ```
  py research\phase2-prep\tools\hsd_collect.py --game "<game>" --label <E#>
  ```
  This writes `research\data\<stamp>_<E#>\` containing `platform\logs\...` and `report\`. Below, `<L>` stands for `research\data\<stamp>_<E#>\platform\logs`.
- **Acceptance levels.**
  - **P** (pipeline) means the data is usable. If P fails, repeat the experiment.
  - **M** (measurement) means the numbers are stable enough to use. If M fails, record the result as "unstable" with the spread and move on.

| Report file | Contents |
|---|---|
| `report.md` | overview, validation issues, per-run fit shapes |
| `rows.csv` | unified table (TELEMETRY-SCHEMA.md) |
| `events.csv` / `hops.csv` / `slides.csv` | detected edges, land→takeoff pairs, slide segments |
| `summary.csv` | per run: max/mean speed, takeoffs, ground accel/decel fits |
| `fits.json` | ground fits for all streams, air fit, vertical fit |
| `census.csv` | E0 table |
| `*.svg` | speed and vz against time, one line per run |

---

## T0 — pipeline smoke test (5 min)

**Procedure.** `LOCAL-SETUP.md` §4, using run `r1`.

**Check.**
```
py research\phase2-prep\tools\hsd_tel.py smoke <L>
```

**P.** 11/11 PASS. That covers:
- MT rows on both sides
- the HSD init line on both sides
- HSD client frames
- dedi events
- 0 validation errors
- at least 90 % of client commands also on the dedi
- MT `dt_est` within 15 % of `FrameTime`
- no `-1` ground/slide values
- a non-zero run label

---

## E0 — movement parameter inventory (10 min)

**Goal.** Get the live value of the 58 keys on both engines, as seen by up to three readers:
- the client class-var block (`bridge_classvar_get`)
- the client settings getter (mod dump)
- the dedi settings getter (mod dump)

**Procedure** (stand still on flat ground with the default legend):

| run | where | command |
|---|---|---|
| r2 | client | `r2` then `exec user/hsd_e0_classvars` then `hsd_md_dump_now 1` |
| r2 | dedi | `hsd_md_run 2` then `hsd_md_dump_now 1` |
| r3 | client | hold **crouch**, then `r3` then `exec user/hsd_e0_classvars` then `hsd_md_dump_now 1` (stance table, `classvar_natives.h:32`) |
| r4 | both | optional: switch legend, `r4` / `hsd_md_run 4`, repeat both dumps |
| – | client | optional: `ui_devmenu_enable 1`, open the **Movement Lab** tab and screenshot the full field list (`gameui/IDevMenu.cpp:15,97`) |
| – | dedi | optional, read-only: `hsd_md_dump` from the client console. It also writes `scriptdump_hsd_movediag_settings.csv` (client→dedi routing unverified) |

**Analyse.**
```
py research\phase2-prep\tools\hsd_tel.py census <L> -o census_E0.csv
```
Columns: `key, cl_classvar, cl_setting, sv_setting, *_type, readers, differs`.

**P.**
- All 58 keys appear in `census.csv` with an outcome: a value, `unknown`, or `ERR`.
- At least one reader returns values for keys that the base scripts already read (`airSpeed`, `airAcceleration`).

**M.**
- Every `differs=1` row is explained (stance, legend, or a genuine client/dedi mismatch).
- A mismatch is a prediction-error candidate: list it in `VALIDATION-REPORT.md` → "E0 findings".

**Output that feeds Unity.** `census.csv` is the first `parameters` block of a trial manifest (`UNITY-DATA-CONTRACT.md` §5).

---

## E1 — ground acceleration and deceleration (15 min)

**Goal.** Find the shape and the constants of ground acceleration from rest and of coast-down with no input.

Before starting, run on the client: `hsd_md_cl_trace 1` (already set by `hsd_client.cfg`) and `fps_max 144`.

| runs | input sequence (mouse still, open flat ground, start each trial standing still ≥ 1 s) |
|---|---|
| r11–r15 | `rN` · wait 1 s · **hold W 3 s** · release · wait 3 s (fully stopped) · `r0` |
| r16–r20 | `rN` · wait 1 s · **hold W + sprint 3 s** · release · wait 3 s · `r0` |
| r21–r23 | `rN` · hold crouch · wait 1 s · **hold W 3 s** · release W · wait 3 s · release crouch · `r0` |
| r24–r26 | `rN` · wait 1 s · **hold A 3 s** · release · wait 3 s · `r0` |

**Analyse.**
```
py research\phase2-prep\tools\hsd_tel.py summary <L> -o E1_summary.csv
py research\phase2-prep\tools\hsd_tel.py fit-ground <L> --run r11            (HSD client frames, observed Time())
py research\phase2-prep\tools\hsd_tel.py fit-ground <L> --run r11 --source MT (per-command, dt_est time axis)
py research\phase2-prep\tools\hsd_tel.py fit-ground <L> --run r11 --source MT --fit-side sv
py research\phase2-prep\tools\hsd_tel.py plot <L> -o E1_speed.svg
```

**Model shapes tried** (`tools/hsdtel/analysis.py`):
- accel: linear `v0 + a·t` capped at `vmax`, against first-order `vmax − (vmax−v0)·e^(−k·t)`
- decel: linear `v0 − d·t`, against Source-style friction `dv/dt = −k·max(v, stopspeed)`

**P.** For every run, `summary.csv` shows `accel_best` and `decel_best` not empty on HSD/cl. If one is empty, the trial did not start from rest or did not coast to a stop: repeat it.

**M.**
- Per condition, the best shape is the same in ≥ 4/5 trials and its R² ≥ 0.98 (`accel_good` / `decel_good` = True).
- `accel_vmax` CV ≤ 2 %; accel constant (`a` or `k`) CV ≤ 5 %; decel constant CV ≤ 5 %.
- HSD/cl against MT/cl `accel_vmax` within 1 %; MT/cl against MT/sv within 1 %. A larger gap is a client/server prediction difference, which is a finding in itself.

**Compare to E0.**
- walk `vmax` vs `speed`
- sprint `vmax` vs `sprintspeed`
- `a` vs `acceleration` / `sprintAcceleration`
- `d` or `k` vs `deceleration`

Matches or mismatches go into `VALIDATION-REPORT.md` with the run ids.

---

## E2 — air acceleration and steering (15 min)

**Goal.** Measure gravity, jump take-off speed and air-acceleration constants, and test the Phase 1 inference that `accelspeed = airAcceleration·dt` with the wish speed capped at `airSpeed` (`research/phase1/Movement-Analysis.md` §3).

| runs | input sequence |
|---|---|
| r31–r40 | `rN` · sprint forward 2 s · **jump** · as soon as airborne release W and **hold D while turning the mouse right steadily** (about a quarter turn over the airtime) · land · stop · `r0` |
| r41–r43 | `rN` · sprint 2 s · jump · **release every key, mouse still** until landing · `r0` (air drag / friction check) |
| r44–r46 | `rN` · sprint 2 s · jump · **keep W held**, mouse still · land · `r0` |

**Analyse.**
```
py research\phase2-prep\tools\hsd_tel.py fit-vertical <L>
py research\phase2-prep\tools\hsd_tel.py fit-air <L> --run r31      (repeat per run; or omit --run for all)
py research\phase2-prep\tools\hsd_tel.py events <L> -o E2_events.csv
py research\phase2-prep\tools\hsd_tel.py plot <L> --y vz -o E2_vz.svg
```

`fit-air` uses HSD client frame pairs. It needs `ang=` and `ax_*` to be present: **check that `rows.csv` has `yaw` and `ax_fwd` filled, and no `-9`/`nan`.** If they are missing, the input APIs failed at run time; log that in `VALIDATION-REPORT.md` and keep the vertical results only.

**P.** `fit-vertical` reports ≥ 10 airborne segments; `fit-air` returns `ok: true` with n ≥ 100.

**M.**
- **Gravity.** `gravity_median` within 2 % of `sv_gravity × gravityScale`, with `sv_gravity` taken as 750 (Phase 1 B-level, `game/server/slide_super_jump.cpp:52-58`) and `gravityScale` from E0.
- **Take-off.** `takeoff_vz_median` within 2 % of `√(2·750·jumpHeight)`, using `jumpHeight` from E0. This tests the Phase 1 B-level jump-impulse formula (`game/server/mantle_boost.cpp:108-110`). Note: the mod samples the first airborne frame, so one frame of gravity (about 5 u/s at 144 fps) may already be applied.
- **No input (r41–43).** Horizontal speed change ≤ 1 % per second, or report the measured decay (that is `airFriction` / `airDrag`).
- **Air fit.**
  - `forms.flat.rms` ≤ 20 % of `rms_no_accel`.
  - Fitted `cap` and `accel` have CV ≤ 10 % across r31–r40; compare them with E0 `airSpeed` and `airAcceleration`.
  - With keyboard input `best` will read `indistinguishable`. That is expected: separating the forms needs analog input, so use a controller in a later session.

---

## E4 — jump momentum preservation (15 min)

**Goal.** Measure horizontal speed kept per landing as a function of ground time, and the effect of the skip-window penalty.

Optional but recommended: a wheel jump bind for frame-tight re-jumps, `bind MWHEELDOWN +jump` (stock Source syntax; **unverified binding name on R5**).

| runs | input sequence |
|---|---|
| r51–r56 | `rN` · sprint forward 2 s · jump · **re-jump as soon as you land**, 5 hops, W held, mouse still · `r0` |
| r57–r59 | `rN` · sprint 2 s · jump · after each landing **wait about 0.3 s** then jump, 5 hops · `r0` |
| r60–r62 | dedi: `skip_speed_reduce 0` (stock 100, `sh_surf_movement.gnut:88-89`; local offline server only) · repeat the r51 pattern · dedi: `skip_speed_reduce 100` |

**Analyse.**
```
py research\phase2-prep\tools\hsd_tel.py hops <L> -o E4_hops.csv
py research\phase2-prep\tools\hsd_tel.py compare <L> --baseline r51 -o E4_compare.csv
```

`hops.csv` has one row per land→take-off pair: `ground_time`, `spd_air_before_land`, `spd_at_takeoff`, `loss_on_ground`.

**P.** ≥ 20 hop rows across r51–r59, with `ground_time` filled.

**M.**
- Loss against `ground_time` shows a reproducible step or trend, with the per-bin CV ≤ 10 %.
- r60–62 against r51–56 shows whether `skip_speed_reduce` changes the loss on quick re-jumps. Report the delta. If the convar has no effect, that is also a result, because `skip_time` may be shorter than the achieved ground time.

---

## E5 — slide behaviour (15 min)

| runs | input sequence |
|---|---|
| r71–r75 | `rN` · sprint forward 2 s on flat ground · **press and hold crouch** until the slide ends · release · `r0` |
| r76–r78 | `rN` · sprint 2 s · crouch (slide) · **jump about 0.2 s into the slide** · land · `r0` |
| r79–r81 | `rN` · sprint 2 s · crouch (slide) · **jump about 0.6 s into the slide** · land · `r0` |
| r82–r84 | optional: the same as r71 down the test slope |

**Analyse.**
```
py research\phase2-prep\tools\hsd_tel.py slides <L> -o E5_slides.csv
py research\phase2-prep\tools\hsd_tel.py events <L> -o E5_events.csv
py research\phase2-prep\tools\hsd_tel.py plot <L> -o E5_speed.svg
```

`slides.csv`: `speed_before`, `speed_peak`, `boost = peak − before`, `duration_s`, `mean_decel`, `linear_r2` per slide, for each of MT/cl, HSD/cl and MT/sv.

**P.** One slide row per trial on HSD/cl and on MT/sv (`slide` flag available, no `-1`); `SV_BEGIN_SLIDE` / `SV_END_SLIDE` events present.

**M.**
- `boost` and `mean_decel` CV ≤ 10 % over r71–r75; compare with E0 `slideSpeedBoost` and `slideDecel`.
- **Slide jump.** Compare take-off speed of r76–78 against r79–81. Phase 1 B-level expects the boost to be subtracted for a slide jump within 0.4 s (`game/server/player.h:1085-1090`), so early jumps should keep ≈ `boost` less speed. Report the difference with its spread.

---

## After the session

1. Run `py research\phase2-prep\run_checks.py --base "<game>\platform\scripts\vscripts"` (repo still green).
2. For each experiment, add to `VALIDATION-REPORT.md` → "Local session results": P/M outcome, numbers with spread, run ids and anomalies.
3. Export one clean trial per experiment for Unity:
   ```
   py research\phase2-prep\tools\hsd_tel.py export-contract <L> --run r11 --experiment E1 -o research\data\trials\E1_r11
   ```
4. Commit `research\data\<stamp>_*\report\` and the trials.
