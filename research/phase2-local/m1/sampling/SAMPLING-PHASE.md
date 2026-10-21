# M1 / plan defect 2: HSD script-frame sampling vs. usercmd physics steps

Status: offline analysis of one smoke session (`20261020_190759_T0_smoke`, run `r1`). Nothing was launched
and no existing file was changed. Script: `sampling_phase.py`, in this folder.

```
python sampling_phase.py <session>/platform/logs [--run 1] [--json out.json]
```

The script uses only the stdlib and the `hsdtel.parse` line parsers. It finds `client/<guid>/` and
`server/<guid>/` itself and contains no local paths. All numbers below come from its output.

Labels: **[obs]** means read directly from the logs or the source. **[inf]** means an inference that
the logs are consistent with but do not prove.

## 1. Method

**Clock.** Every SDK log line is stamped `[wall] [plat]`. Here `plat` is `Plat_FloatTime()` at the
moment the line was written, printed `%.3f` (`s21-r5sdk/src/tier0/platform.cpp:107`). Within one
process this one clock covers both `message.log` ([MOVE-TRACE], abbreviated MT below) and `script.log`
([HSD-MD]). That lets the analysis order client MT lines against client HSD lines to 1 ms. In r1, no
HSD frame line shares its millisecond with an MT line (`frames_with_same_ms_cmd = 0`), so the ordering
never had a tie. The client and the dedicated server (dedi below) are separate processes, and their
`plat` values are not comparable.

**Streams.**
- Client MT: one line per first-time-predicted `FullWalkMove`, logged after the move. It holds the
  pre-state (`o`, `v`) and the post-state (`po`, `pv`), from `game/client/move_sim_trace.cpp:135-198`.
  Lines tagged `rp=1` are re-predicted replays. They are excluded from the counts and checked on their own.
- Client HSD `kind=frame`: one line per `WaitFrame()` resume of the mod's client thread
  (`hsd_movediag__movediag.gnut:523-549`). It holds `t=Time()`, `ft=FrameTime()`,
  `o=GetOrigin()` and `vel=GetVelocity()`, all printed `%.3f`.
- Run window: from the client `kind=run run=1` line (plat 324.813) to `run=0` (plat 369.800).
  Within r1, W was held for commands 1625–2037 (plat 361.109–364.090). The jump was command 2458 and the
  landing command 2560.

**Phase matching.** Each HSD frame is compared with the commands near it, using exact equality
(distance below 0.0015 u, which is the print precision) against MT pre (`o`,`v`) and post (`po`,`pv`).
A frame counts as "moving" if |v_xy| > 1 or |v_z| > 1. Only moving frames can pick out a single command.
Static frames are consistent with any nearby command.

**Timing.** For each matched frame, `ft` is compared with three things:
- the deltas of consecutive `t` values;
- `dt_est = |po_xy − o_xy| / |pv_xy|` (TELEMETRY-SCHEMA `drv_dt_est`) for commands N−1, N and N+1;
- the sum of `dt_est` over the commands between two frames.

## 2. Results

### 2.1 Frames vs. commands [obs]

| quantity | r1 |
|---|---|
| HSD client frames | 2788 (62.8 /s over 44.38 s) |
| client MT first-time commands | 2811 (63.3 /s), commands 6–2816, no number gaps |
| ratio of frames to commands | **0.9918** |
| client `rp=1` replay lines | 14 (commands 12–16, 25–26, 2463–2469), all bit-identical to the first-time line (max diff 0.0) |
| whole session (all runs) | 7781 frames vs 7803 commands |

Number of first-time commands whose `plat` lies in (previous frame, this frame]:

| commands per frame interval | intervals |
|---|---|
| 0 | 6 |
| 1 | **2780 (99.75 %)** |
| 2+ | 1 (holding 23 commands) |

The two exception types:

| frame seq | plat | commands | `ft` | Δt | Δplat | note |
|---|---|---|---|---|---|---|
| 12 | 329.698→330.529 | 0 | 0.100 | 0.100 | 0.831 | loading hitch; `Time()` advance capped at 0.1 |
| 14 | 330.627→330.633 | 0 | 0.096 | 0.096 | 0.006 | loading; `[TIME-DOMAIN] clock domain broke` at 330.643 |
| 1342 | 359.010→359.254 | **23** (1349–1371) | 0.00723 | **0.00564** | 0.244 | 22 commands never sampled; `[TIME-DOMAIN] window … last_d` 0.002→0.191 at 359.016 |
| 2550–2553 | 368.025→368.056 | 0 each | 0.0001–0.0002 | ≈0.0001 | 0.006–0.010 | 4 script frames with almost no `Time()` advance and no usercmd |

Both cases therefore occur. There are frames without a command (6) and commands without a frame of
their own (22, all in one stall). Apart from those, the relation is exactly one command per script frame.

**[inf]** The client frame rate had two regimes. The median `ft` was 0.00723 s (≈138 fps, against
`fps_max 144`) while active. It was ≈0.053 s (≈19 fps) for about 18 s of standing (plat ≈336–355), with
one command per frame in both regimes. The cause of the slow regime (unfocused window or host load) was
not logged.

### 2.2 Phase: which command's state an HSD frame shows [obs]

| class | frames | share |
|---|---|---|
| moving, matches **post of cmd N** exactly (unique) | 536 | 100 % of moving |
| moving, matches pre of cmd N | 0 | 0 % |
| moving, origin only, or no match / interpolated | 0 | 0 % |
| static (consistent with any nearby command) | 2252 | — |
| **all frames: state == post of the latest command printed before the frame** | **2788 / 2788** | 100 % |

- Lag: N is always the **most recent** first-time command (lag 0 commands, 536/536). No moving frame
  matches N−1, and none shows an interpolated or smoothed render origin.
- Within a frame, the HSD line is written p50 2 ms after the MT line of command N (p05 1 ms, p95 4 ms,
  min 1 ms). The next command follows p50 5 ms later. **[inf]** The client builds and predicts its usercmd
  earlier in the same host frame, before script threads resume.
- Between consecutive matched frames, the command index advances by exactly 1 (533/533).
- Edges: the HSD takeoff frame shows post(2458), with vz 281.675 and ground=0. The landing frame shows
  post(2560), with ground=1. The `ground` flag is therefore post-state too. Because 1 command = 1 frame
  here, the HSD edge timing equals the MT edge timing.

### 2.3 Timing: `FrameTime()` semantics (Phase 1.5 U14) [obs]

| `ft` compared with | n | mean abs diff | within 0.02 ms | within 0.5 ms |
|---|---|---|---|---|
| `t_k − t_{k−1}` (matched frames) | 536 | 7.7 µs | 92.9 % | 100 % |
| `t_{k+1} − t_k` | 536 | 116 µs | 71.5 % | 96.5 % |
| `dt_est` of **cmd N** (the command shown) | 433 | **15 µs** | **95.2 %** | 99.3 % |
| `dt_est` of cmd N+1 | 432 | 79 µs | 70.1 % | 95.6 % |
| `dt_est` of cmd N−1 | 433 | 78 µs | 71.6 % | 95.6 % |
| Δplat of the log lines | 536 | 724 µs | 0.6 % | 50 % |

- All frames: `ft == t_k − t_{k−1}` within 0.05 ms for **99.78 %** of 2787 intervals, against 64.5 % for
  `t_{k+1} − t_k`.
- Decisive subset (|pv_xy| ≥ 150, and cmd N's `dt_est` differs from both neighbours by more than
  0.2 ms): the closest match is cmd **N in 12 of 13** frames and N+1 in 1, where none of the three is close.
- Σ`dt_est` of the commands between two frames, minus `ft`: mean −10 µs (n = 432).
- Moving commands have `dt_est` from 6.08 to 8.73 ms (p50 7.27 ms), and the dedi `dt_est` is identical.

**Answer to U14:** `FrameTime()` is the frame that has just finished. It is the interval that ends at
this sample, equal to `Time() − previous Time()`. It also equals the simulated frametime of the command
whose post-state the frame shows. The 6 frames where `ft ≠ Δt` (seq 10, 11, 13, 15, 711 and 1342) all
sit at client clock re-bases, either during loading or next to `[TIME-DOMAIN] … clock domain broke` /
`window … last_d` lines in the client `warning.log` (339.566 → seq 711, 359.016 → seq 1342). In those
frames `t` jumps by between −0.002 and +1.84 s relative to `ft`. **[inf]** Client `Time()` is re-based
by clock correction, and **`t` deltas are not a physics dt**. `ft` reached 0.10609 once (seq 710, a
static frame), so `FrameTime()` is not limited to the 0.1 command clamp.

### 2.4 Squirrel access to the usercmd number (CLIENT VM) [obs]

None was found. In detail:

- **Script corpus** (`s21-platform/scripts/vscripts`). No function or callback named after
  UserCmd, CommandNumber, CmdNum, RunCommand, CurrentCommand, LastCommand or CommandTick exists.
  `lastCommand` in `sh_mod_heirlooms.gnut:79` is an unrelated rate-limit table.
- `InPrediction()` / `IsFirstTimePredicted()` exist and are used in shared code, for example
  `abilities/loba_tactical_translocation.nut:137`, which is loaded in CLIENT per `scripts.rson:2511,2525`.
  Both return only a bool, and only inside predicted code. They are not meaningful in a `WaitFrame` thread.
- `CodeCallback_OnPlayerInputCommandChanged(player, cmdsHeld, cmdsPressed, cmdsReleased)`
  (`_codecallbacks_player_input.gnut:24,27`) is the only per-input callback. It is **SERVER-only**
  (`scripts.rson:630-638`), fires on button changes and carries no command number.
- `AddPlayerMovementEventCallback` (`_codecallbacks_common.gnut:958`) is also SERVER-only
  (`scripts.rson:637`). Every client-side user is behind `#if SERVER`, for example
  `pilot/sh_pilot_passive_sparrow.gnut:133-135`.
- Nearest CLIENT-VM substitutes: `FrameCount()` and `PlatformTime()`, both used at
  `client/cl_damage_indicator.gnut:99` (CLIENT, `scripts.rson:2577,2592`). `PlatformTime()` is also
  used at `client/cl_demo_overlay.gnut:725` (CLIENT, `scripts.rson:2028,2032`).
- **SDK natives.** The client registrations (`game/client/vscript_client.cpp`,
  `vscript_player.cpp:807-1031`, `scriptnetdata_client.cpp:648-699` and the rest) expose no command or
  tick getter. The client reads `command_number` only in native hooks: `MoveTrace_ReadCmdNumber`
  (`game/client/move_sim_trace.cpp:75`) and `bridge_cmd_seed.cpp:122`. Neither is a script function.

### 2.5 Dedicated server: MT batches vs. HSD events [obs]

- Dedi MT: 7802 lines. Every r1 client command (2811 of 2811) is present on the dedi with
  **bit-identical post-state** (max diff 0.0).
- Batches, where lines less than 20 ms apart form one batch:

| quantity | value |
|---|---|
| batches | 1473 |
| batch start interval | p50 50.0 ms, p05 49, p95 52 (20 Hz) |
| batch duration | p50 4 ms, p95 11 ms |
| batch size | 7 ×875, 6 ×143 (≈138 fps client), 1 ×394 (≈19 fps regime), 8–9 ×33, 14–19 ×4 (hitches) |

- The dedi HSD emitted only events (`hsd_md_sv_trace` was 0, so there are no server frames):

| event | server `t` | emitted inside cmd | position in batch | state printed | sv `t` − client `t` at start of that cmd |
|---|---|---|---|---|---|
| JUMP | 366.41956 | 2458 | 3 of 7 | pre(2458): vel 0, ground 1 | +0.12134 s |
| LEAVE_GROUND | 366.41956 | 2458 | 3 of 7 | pre(2458) origin/vel, **ground 0** | +0.12134 s |
| TOUCH_GROUND | 367.16895 | 2560 | 3 of 3 | pre(2560): vz −274.757, **ground 1** | +0.12137 s |
| RESPAWN / first TOUCH_GROUND | 324.450 / 324.183 | spawn, before batch 1–5 | — | static | — |

- The event `plat` equals the `plat` of the MT line of the command that emitted it, which is logged when
  the dedi runs the batch. That is up to about one 50 ms tick, plus transit, after the client predicted it.
- Server `t` inside a command is the **start time of that command**. It is not the 20 Hz frame time.
  Between JUMP and TOUCH_GROUND the dedi Δt is 0.74939 s and the client Δt is 0.74936 s. The offset is
  constant, +0.1213 s in this session.
- **[inf]** Server `Time()` in frame context is tick-aligned (RESPAWN 324.45001, `run` 324.55002). In
  command context it is per-command time. That explains the `W_TIME_BACKWARDS` warning (324.450 →
  324.183) in this session's report.
- **[inf]** Event callbacks fire inside `FullWalkMove`, after the ground flag changes but before
  origin/velocity integrate. The MT line is written after the move returns
  (`game/server/move_sim_trace.cpp:182-232`).

## 3. Conclusions

1. **[obs]** In r1 an HSD client frame is a sample of the **post-state of the latest first-time-predicted
   usercmd** (lag 0). This holds for 2788 of 2788 frames, and uniquely for all 536 moving frames. It is
   never a pre-state or an interpolated render state. Its `ft` is that command's frametime.
2. **[obs]** The relation is one command per frame for 99.75 % of intervals, but it is not guaranteed.
   There are frames with no command (`ft` from 0.0001 s to 0.1 s) and a stall in which 22 consecutive
   commands were never sampled. With an uncapped frame rate above the command rate, or with script
   stalls, HSD under-samples physics.
3. **[obs]** HSD `t` deltas break at client clock re-bases. `ft` is the dt that matches the command
   frametime.
4. **[obs]** No CLIENT Squirrel API gives a usercmd number or a per-command callback.
5. **[obs]** Dedi MT equals client MT bit-for-bit for every r1 command. Dedi HSD events are emitted
   inside a specific command, print that command's pre-state with the updated ground flag, and carry
   that command's start time.

## 4. Recommendation

- **Physics truth is MT.** Use client first-time MT lines for every per-command quantity (dt, accel,
  friction, air control). Use dedi MT to confirm the result, since it was identical in r1. Do not
  differentiate HSD samples for physics.
- **Tag HSD frames, don't trust them blindly.** In analysis, give every client HSD frame
  `drv_cmd_post` = the latest non-replay client MT `cmd` with `plat ≤` the frame's `plat`, plus
  `drv_ncmd` = the number of commands since the previous frame. Where the frame is moving, verify the tag
  by exact state equality and set `drv_flags=phase_unverified` otherwise. Use HSD only for what MT lacks:
  input bits and axes, angles, script ground/slide/sprint flags, and run labels. Join those to MT by
  `drv_cmd_post`. Use `ft` as the dt of a frame only when `drv_ncmd == 1`. Never use `t` deltas across a
  frame where `|ft − Δt| > 0.05 ms`.
- **Tag dedi HSD events** with the command that emitted them: the transition command inside the batch
  containing the event `plat`. Treat their state as pre(N) with the ground flag of post(N). For timing,
  use the command (joined to client MT), not the event's `plat` or server frame time.
- **Mod change (v0.3, proposed, not applied).** Add `fc=FrameCount()` and `pt=PlatformTime()` to the
  client `kind=frame` line. Both have CLIENT base uses (`cl_damage_indicator.gnut:99`), so they satisfy
  the hsd_vmcheck rule. A jump in `fc` shows directly when commands went unsampled, and `pt` removes the
  dependence on 1 ms sink stamps on the HSD side. **[inf]** `PlatformTime()` is a 32-bit script float,
  about 30 µs resolution at 400 s, and the meaning of `FrameCount()` (host frame vs. client frame) needs
  a live check.
- **A command number in HSD needs an SDK change, not a mod change.** One option is a CLIENT script native
  that returns the MT high-water command number (`s_nMoveTraceHighWater`,
  `game/client/move_sim_trace.cpp:166-201`). Another is to add a host frame counter to the MT line. Until
  either exists, the `plat`-order join above is the tag. It was exact in r1 (0 same-ms ties) but
  degrades if a frame and a command share a millisecond.
- **Coverage caveat.** This is one session. Only 19 % of frames were moving and only 13 frames were
  decisive for N vs N±1, so rerun `sampling_phase.py` on the E1/E2 sessions before relying on lag 0 at
  other frame rates.
