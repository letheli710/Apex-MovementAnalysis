# M4b view-control acceptance

Question: can the runner turn the view during a trial, and is the turn applied to the usercmds the server simulates? It is
not enough to check what the camera shows.

## Method

- **Runner.** New keys `left`/`right`/`lookup`/`lookdown` and a new step `set cl_yawspeed|cl_pitchspeed N`.
  - The runner sends `set` steps to the client console before the schedule starts.
  - It restores the session values after the trial.
- **Rate check.** `view_check.py <session>` compares each command's angle change against the set rate.
  - MOVE-TRACE carries no view angles. The view is read from the client `[HSD-MD]` frame rows instead: one row per usercmd at
    120 fps, ft = that command's dt.
- **Trajectory check.** For `m4b_view_run`, the dedi's MOVE-TRACE velocity heading is compared with the client yaw.
- Rerun:
  - `py -3 view_check.py ../data/20261021_022102_M4b_octane > view_output_s1.txt`
  - `py -3 view_check.py ../data/20261021_023310_M4b_octane2 > view_output_s2.txt`
  - Add `--json` to write `view_results_s*.json`.

## Results

| Check | Session / runs | Result |
|---|---|---|
| Yaw rate, `set cl_yawspeed 90`, +right 1 s then +left 0.5 s | octane2 r2449–2453 (5/5 valid) | 178 / 180 turning commands at 90 ± 1 % (median 89.93–90.04 °/s). The 2 others are the press-edge commands at half rate (45 °/s, the usual key-edge half step). Net turn −45.00 … −45.05° vs −45° expected. |
| Yaw rate while +speed (sprint) is held | octane2 r2454–2458 | 60.3 °/s = 0.67 × 90. Holding the speed key scales key turning by 0.67, like Source `cl_anglespeedkey`. |
| Server trajectory follows the turned view | octane r2411–2413, r2415 (sprint + turn; 140.7 °/s, the session default 210 × 0.67) | Final dedi velocity heading − client yaw = −0.001 … +0.001°. The trajectory turns with the view, not just the camera. |
| Pitch via +lookup / +lookdown | octane r2406–2410, octane2 | **No pitch change at all** (0 turning commands). In R5 these keys do not turn the view. Pitch stays per-trial (`SCHEDULE_PITCH` at reset). |

Accepted: per-command yaw control at a constant rate. Per-command pitch control is not available; it is not needed for the
swing experiment, which turns in yaw.

## Issues found and fixed

- **[fixed]** The first version sent `set` through `player.ClientCommand`. The engine forwards that to the server as a
  client command (`cl_yawspeed isn't a registered client command`), so session 1 turned at the session default
  210 °/s instead of 90. The runner now sets the cvar on the client console.
- **[fixed]** In octane2 the `m4b_view_run` trials ran into a jump pad left over from the pad trials on the same lane
  (speed 299 → 514). Their rates are valid, but their trajectory heading (−16.5° vs yaw −60°) is not. The trajectory check
  uses session 1. View schedules now remove leftover test props in the reset.
