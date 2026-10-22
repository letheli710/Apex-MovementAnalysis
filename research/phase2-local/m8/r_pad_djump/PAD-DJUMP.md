# M8 R1: Octane jump-pad double jump (R5Flowstate S21, local offline)

Status: measured in 4 local sessions (Octane, kit, 120 fps, lane C, pad spawned 300 u ahead by the reset as in M4). Nothing is committed. Evidence labels: **[meas]** read from client first-time MOVE-TRACE usercmds and the dedi MOVE-TRACE rows of the same usercmd, **[fit]** a formula checked against those rows, **[src]** script source, **[inf]** interpretation.

Engine units are used throughout. The pad flight runs in slow-mo (M4: every integral on 0.8·dt), so a world-space velocity is 0.8 × the engine value.

## TL;DR

| Question | Answer | Evidence, n |
|---|---|---|
| Is a double jump (DJ) granted after a pad launch? | **Yes**, one, for any jump press edge after the grant until landing | [meas] 123 DJ on client and dedi |
| Earliest time | **≈ 0.108 s after the launch usercmd.** Dedi: refused at ≤ 0.0834 s (20/20) and at 0.1081–0.1083 (2/5); accepted at 0.1084 (3/5) and ≥ 0.133 s (all). Source: `wait 0.1` thread in `sh_jump_pads.gnut`, grant via settings mod `enable_doublejump` | [meas] 40 first presses before 0.21 s; [src] |
| Client prediction near the grant | The client refused 4/5 presses at 0.133 s that the dedi accepted (client then corrected) | [meas] |
| Vertical | Two branches, **discontinuous**: pre vz ≥ 360.04 → **vz += 201.81**; pre vz ≤ 357.35 → **vz = 409.25** (both before the slow-mo gravity step). Not max(vz + 201.81, 409.25): pre vz 246 gives 409.25, not 447.8 | [meas] add n 106 (sd 0.05), floor n 38 (sd 0.005) |
| Horizontal, no move key | **Unchanged** (|Δv_h| 0.0000, n 100), whatever the view yaw (view turned 90° right: still unchanged) | [meas] |
| Horizontal, move key already held | **v_h' = v_h − 240·v̂_h + 240·ŵ**, then the usual AirAccelerate. W along v: no change; S: −480 along v; D: 240 sideways and 240 less forward; W+D: the diagonal. Same at launch speed 514 and 813 | [fit] 25 DJ, max error 0.015 u/s |
| Horizontal, key pressed on the DJ usercmd itself | Different and **not modelled**: D press gives −264.1 along v̂ and +272.1 along ŵ; S press gives a net 449.3 along ŵ (held S: 480) | [meas] 19 DJ |
| Input vs view | The direction comes from the move keys relative to the view (W after a 90° turn behaves exactly like D before it); the view alone does nothing | [meas] 5 + 5 |
| Once only? | **Yes.** A second press after a DJ: no effect (0/5) | [meas] |
| Does a refused early press consume it? | **No.** Press at 0.058 s (refused), press at 0.508 s: DJ 5/5 | [meas] |
| Jump held through the launch (jump-in, held 1.27 s) | Holding never triggers it (0/5); the next new press after release does (5/5, floor branch) | [meas] |
| Normal jump + air press (control) | **No DJ** (0/5) | [meas] |
| Landing reset | After a pad landing (unused grant) and a ground jump, an air press gives **no DJ on the dedi** (0/5); the client predicted one in 5/5 and was corrected | [meas] |
| Lurch after the DJ | **The DJ re-anchors the lurch window.** A D press 0.025 s after the DJ gives |Δv| 212.55 (control at the same time without DJ: 3.87 = AirAccelerate only) | [meas] 5 + 5 |
| Stand vs crouch entry, walk vs sprint, jump-in | Launch as M4 (514.3/1026.1 standing; 813.2/810.7 crouched); the DJ is the same +201.81 in all; a jump-in launch (airborne pre-state) is identical and grants the DJ | [meas] 5 each |
| Landing after a DJ | The M4 landing law holds (max |f0 − model| 0.00055); a DJ raises the impact to |vz| up to 1336, so f0 is usually **0** (full stop), against 0.24 without DJ | [meas] 135 landings |

## Data and exclusions

| Session (data/) | Schedules (ok trials) | Excluded |
|---|---|---|
| `20261022_035342_M8_pad1` | m8_pad_none 5, m8_pad_dj_f0/f6/f12/f24/f60/f200/f300 5 each, m8_pad_dj2 5, m8_djctrl 5 | warm-up only |
| `20261022_040528_M8_pad2` | dj_f9, dj_f15, early_late, jumpin, jumpin_hold, dj_right, dj_view, dj_viewfwd, dj_lurch, pad_lurch, land_jump, padc_dj, padw_dj 5 each; dj_back 4 | r8132 dj_back (115.6 fps, runner frame-rate rule) |
| `20261022_042841_M8_pad3` | dj_f120/f156/f174, djh_right/back/fwd/diag, padc_djh_right, dj_back 5 each | none |
| `20261022_050022_M8_pad4` | dj_f128…f140 (step 2) 3 each | none |

`m8_pad_dj_fK`: sprint into the pad, release W and sprint on the launch frame (`waitair`), press jump K client frames later. All analysis times are measured from the launch usercmd, not from K. Dedi and client agree to 0.0 u/s on every DJ usercmd except the mispredictions listed above.

## Model for Unity (pad-specific DJ, separate from the generic DJ)

```
on pad launch:   grant = pending; tGrant = tLaunch + 0.108 s            [meas; src 0.1 s]
grant pending -> available at tGrant; cleared on landing or zipline    [meas landing; src zipline]
jump press edge (new press only; holding does nothing) while available:
    vz = vz + 201.81            if vz >= ~359   (engine units)        [meas]
    vz = 409.25                 otherwise
    if move keys held (wish w != 0):  v_h = v_h - 240*normalize(v_h) + 240*w     [fit, key held before the press]
    available = false (once per launch)
    re-anchor the lurch window (t = 0 at the DJ)                        [meas]
then the slow-mo flight continues; the landing uses the M4 landing law (f0 from vz^2)
```

Values are engine units inside the 0.8 slow-mo flight. In world space the add is 161.4 u/s, the floor 327.4 u/s and the horizontal step 192 u/s, if Unity models the flight in world units (M4 recommends keeping engine units and scaling dt).

## Open questions

1. The vertical branch boundary is only bracketed: (357.35, 360.04] u/s pre vz. Its meaning (a threshold on vz, or a comparison of the two candidate values) is unknown.
2. A move key pressed on the same usercmd as the DJ gives a different horizontal result (D: −264.1 / +272.1; S: net 449.3). The held-key rule plus the M3 lurch in either order does not reproduce it.
3. The lurch clamp after a DJ measured 212.55, not the 209.3 of a ground jump (0.7 × sprint cap at msc 1.15). Not explained.
4. Only the normal (non-upgraded) pad was used; `enable_doublejump_aircontrol` (upgraded pad skin) was not tested.
5. DJ grant timing is quantised by the server thread (`WaitFrame(); wait 0.1`); only 120 fps was tested.

## Rerun

```
cd research/phase2-local/m8/r_pad_djump
py -3 pad_djump_analysis.py ../../data/20261022_035342_M8_pad1 ../../data/20261022_040528_M8_pad2 \
  ../../data/20261022_042841_M8_pad3 ../../data/20261022_050022_M8_pad4 \
  --json results.json --params params.json > analysis_output.txt
```

Sessions were run with `tools/hsd_session.py --trials 5 (pad4: 3) -- --fps 120 --legend octane --kit --no-census --state-log --schedule <list>`.
