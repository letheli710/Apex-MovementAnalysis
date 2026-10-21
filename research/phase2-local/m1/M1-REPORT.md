# M1 — minimal automated loop

Goal (plan M1):

- Fix the six known defects.
- Run "reset → forward → stop → jump → land" automatically 5 times, restart the game, and run it once more.
- Read the trajectory into Unity and produce the first error report. Error targets are not required yet.

Branch `phase2-local/m1-loop`. Data lives under `research/phase2-local/data/`. Only the derived `report/` folders and `runner.json` are in git; the raw logs stay local.

## 1. Acceptance

| # | Criterion | Result | Evidence |
|---|---|---|---|
| A1 | Real in-game T0 smoke 11/11 with client↔dedi join ≥ 90 % | **PASS**: 11/11 on both acceptance sessions; join 100 % | `hsd_tel.py smoke` on `20261020_200349_M1_loop_s7` and `20261020_200510_M1_loop_s8` |
| A2 | 5 repeats + 1 after a restart: same take-off/landing sequence, no dropped samples | **PASS** | §3; `acceptance/verdict.json`, `acceptance/trials.csv` |
| A3 | Unity reads the trial, replays it, writes a first error report | **PASS** (pipeline). Error: 32 u position RMS, not gated in M1 | §5, `unity/` |
| A4 | Defects 1–6 fixed | **PASS** | §2 |

## 2. The six defects

| # | Defect | Fix | Where |
|---|---|---|---|
| 1 | No real automated input; no state reset | Runs go through the SDK **AgentLink** loopback socket (`-devsdk`; `s21-r5sdk/src/engine/agent_link.cpp:1-19`). **Reset:** a dedi `EVAL` runs the fs_1v1 teleport recipe (`gamemodes/fs_1v1/_1v1_match.nut:2087-2103`). **Input:** a client `EVAL` starts a thread that first waits until the client-predicted state has settled at the target (30 frames). It then sends `+/-forward`, `+/-jump` with `player.ClientCommand` on counted script frames, which takes the real kbutton → CreateMove path. Every edge is logged as `[HSD-SCHED]`. A per-trial frame-rate check rejects any trial outside 144 fps ± 3 %. The window never needs focus | `tools/agentlink.py`, `tools/hsd_trial.py`, `tools/hsd_session.py` |
| 2 | Script frames ≠ physics steps | Measured, details in `sampling/SAMPLING-PHASE.md`: each HSD frame is the **post-state of the latest usercmd**, with lag 0. `FrameTime()` is the frame that just finished. In the M1 sessions the client ran 1 usercmd per frame (1225 frames = 1225 usercmds per trial). MOVE-TRACE is the physics source; HSD supplies only inputs, angles and flags. The usercmd number is not readable from client script (no native) | `m1/sampling/` |
| 3 | Server and client parameters mixed | Parameters carry their side and reader. Export uses the trajectory's side; mismatches between sides are listed, never silently resolved | `hsdtel/contract.py`, `analysis.py` (subagent, verified) |
| 4 | Contract lacks replay fields | `hsdmove-trial/2` adds: per-step usercmd number; `n_cmds`; sprint input; `buttons`, `cmd_fwd`, `cmd_side`; pressed/released edges; `initial_state`; `terrain`; `session` | `contract.py`, `UNITY-DATA-CONTRACT.md` |
| 5 | `check_trial`/`compare_trials` too loose | `t` and `cmd` must increase strictly; inputs must be complete; edges are checked. Comparison aligns by usercmd and fails on any length or sequence mismatch instead of truncating | `contract.py`, `tests/test_contract.py` |
| 6 | Join by global `cmd` collides across sessions | The join key is now (session, entity, reset batch, cmd), with documented rules for when a new batch starts | `parse.py`, `derive.py`, `validate.py` |

After the merge, verified by the lead: `run_checks.py` 10/10, 81 unit tests OK, T0 smoke 11/11 with 99.9 % join and 0 ambiguous.

## 3. Repeatability (A2)

Sessions `M1_loop_s7` (5 scored trials after one unscored warm-up) and `M1_loop_s8` (game restarted; 1 scored trial after a warm-up). Firing range, Gibraltar, empty-handed (`msc` 1.15, `maxspeed` 199.525 in every command).

| run | usercmds | gaps | join | fps | fwd_down→fwd_up | fwd_up→stop | stop→jump | jump→takeoff | takeoff→land | peak u/s | distance u | apex u | takeoff vz |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| r41 | 1225 | 0 | 1.0 | 143.77 | 432 | 22 | 410 | 1 | 109 | 199.525 | 604.78 | 55.03 | 277.19 |
| r42 | 1225 | 0 | 1.0 | 143.40 | 432 | 22 | 410 | 1 | 109 | 199.525 | 604.56 | 55.00 | 276.81 |
| r43 | 1225 | 0 | 1.0 | 143.88 | 432 | 22 | 410 | 1 | 109 | 199.525 | 603.77 | 55.00 | 276.81 |
| r44 | 1225 | 0 | 1.0 | 143.85 | 432 | 22 | 410 | 1 | 109 | 199.525 | 604.12 | 54.99 | 276.72 |
| r45 | 1225 | 0 | 1.0 | 143.88 | 432 | 22 | 410 | 1 | 109 | 199.525 | 603.99 | 54.99 | 276.72 |
| r46 (after restart) | 1225 | 0 | 1.0 | 143.90 | 432 | 22 | 410 | 1 | 109 | 199.525 | 603.80 | 54.99 | 276.72 |

- **Event sequence and spacings:** identical in all six trials (spread 0 usercmds).
- **Distance and vertical values:** distance spreads 0.17 %, apex 0.07 %, take-off vz 0.17 %. The residual comes from per-frame `dt` jitter at a nominal 144 fps.
- **Samples:** HSD frames = usercmds = 1225 per trial; no usercmd number gaps.
- **First forward command:** `fwd = 0.5`, then 1.0 (the Source kbutton half-press). A Unity replay must reproduce this.
- **Input latency:** a `ClientCommand` issued in frame N is carried by the very next usercmd (≈ 5 ms; seen in the probe trial).

## 4. Problems found and fixed on the way (all real-data findings)

| Problem | Evidence | Fix |
|---|---|---|
| The unfocused client paced itself to **18.7 fps**: a frame-indexed "forward 432 frames" lasted 23 s, and the player fell off the platform | session `…_M1_loop_s1_REJECTED` (kept, see its `REJECTED.md`) | `not_focus_sleep 0` in `hsd_client.cfg` (the SDK demo player does the same, `demo_play.cpp:831-836`), plus the runner's frame-rate check |
| The first trial after a level load hitched (126 fps over the trial; 72 frames took 1.69 s) | sessions s3/s4 (rejected by the check) | 15 s settle after the spawn plus one unscored warm-up trial |
| The client run label covered the reset teleport, so `initial_state` was the pre-teleport position | first M1_r31 export (discarded) | the schedule thread sets `hsd_md_run` itself once the reset has settled |
| Log rotation (10 MiB per file) split sessions across `message.N.log` | s1 had 3 files | the hsdtel parser already reads every rotated file (up to 16). The one-off `sampling_phase.py` reads only `message.log`; noted |

## 5. Unity replay (A3) — **PASS (pipeline); error targets not met yet, as the plan allows**

New project `C:\Workspace\Playground\ReApex-DataAnalysis\HSD-Unity` (Unity 6000.6.5f1, private repo `letheli710/HSD-Unity`, branch `m1/r5-replay`). The deprecated project was not touched. The code lives under `Assets/HSD/R5Replay/`:

- `TrialLoader` validates the `hsdmove-trial/2` contract strictly.
- `SourceSpace` converts Unity = (−y, z, x)·0.0254.
- `ReferenceMotor` is a first-guess Source-style model in Source units, one step per usercmd with the recorded dt.
- `Replayer` aligns by usercmd and fails on any mismatch.
- `BatchReplay.Run` is the `-executeMethod` entry point.

Verified by the lead: EditMode tests **26/26 passed** on a rerun, and the batch replay of `M1_r41` exited 0.

First error report (`unity/index.md`; per trial `steps.csv`, `summary.json`, `report.md`). Δ = sim − R5:

| trial | pos RMS / max (u) | vel RMS / max (u/s) | take-off Δ | land Δ | stop Δ | apex R5 → sim | peak speed |
|---|---|---|---|---|---|---|---|
| M1_r41 | 32.17 / 34.48 | 23.13 / 288.86 | 0 | +2 | 0 | 54.91 → 56.00 | 199.53 both |
| M1_r42 | 32.28 / 34.59 | 23.16 / 288.43 | 0 | +2 | 0 | 54.88 → 56.00 | 199.53 both |
| M1_r46 | 32.19 / 34.49 | 23.16 / 288.09 | 0 | +2 | 0 | 54.87 → 56.00 | 199.53 both |

What the error says (input for M2, not yet applied):

- **Ground acceleration dominates.** Peak speed comes 40 steps late, which leaves a constant offset of about 33 u (distance 571 vs 605 u).
  - R5 accelerates at about 2875 u/s² up to about 138 u/s, then at about 518 u/s².
  - That fits `lowAcceleration` 2500 below `lowSpeed` 120 and `acceleration` 450 above it, each × the 1.15 move scale. So the move scale probably scales acceleration too, and there is a low-speed branch.
- **Stopping already matches** (22 usercmds in both).
- **Jump:** sim apex 56.0 against R5 55.0, and air time 111 against 109 steps. The jump command loses about 2.5 u/s of vz in R5, as noted in O2.
- The 288 u/s velocity maximum is the two landing steps where R5 is already grounded and the sim is not.

Limitations:

- flat floor;
- no sprint, crouch or slide;
- no side or back scaling;
- no landing slowdown;
- the move scale is read from the course note rather than from a contract column (to add: `movescale`/`maxspeed` per step, O6).

## 6. Open issues carried forward

| # | Issue | Next |
|---|---|---|
| O1 | `compare-contracts` aligns by absolute usercmd, so two different trials cannot be compared, only a replay of the same trial | add a relative-cmd mode for repeatability comparisons (M2) |
| O2 | Take-off vz is 276.8 u/s, below √(2·750·56) = 289.8 u/s, and apex is 55.0 u against `jumpHeight` 56 | M2/E4: model the first airborne step (gravity applied in the jump command) |
| O3 | Frame-indexed input is quantised to frames; dt jitter ≈ ±0.3 %. It does not give cmd-exact edges for tap-strafe or superglide | M3: bot `BotCmd_*` / synthetic R5Dem replay (dedi only), or an SDK CreateMove detour; time-boxed |
| O4 | No producer logs the ground normal (`terrain.ground_normal` null) | only needed for slopes (M2 E1 variants) |
| O5 | The census was not re-run in the acceptance sessions; the parameters come from T0 (same build and legend) | run E0 inside each M2 session |
| O6 | The contract has no per-step `movescale` or `maxspeed`, so Unity reads the move scale from the course note | add both columns to `hsdmove-trial/2` (M2) |
| O7 | The first-guess motor is off by about 32 u RMS position | M2/E1: low-speed acceleration branch and move-scale scaling; E4: jump command |
