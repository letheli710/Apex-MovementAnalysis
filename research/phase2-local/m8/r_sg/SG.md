# M8 R3: superglide coverage (R5Flowstate S21, local offline)

Status: measured in 6 local sessions (Gibraltar, 120 fps, lane A rock sunk to ledge height H as in M6-A2). Five sessions run the **native** code path (`--both-cvar mantle_boost_enabled=0`, as the M6-A2 `sg_off` session); one control runs the default **SDK FSM** (mantle boost on). Nothing is committed. Labels: **[meas]**, **[fit]**, **[src]**, **[inf]**.

The press is timed from the traversal start: the runner's new `waittrav` step waits until the client sees `IsTraversing()`, then the schedule presses jump + crouch (next frame) K frames later. The analysis measures the press on the client HSD frames relative to the last usercmd before the MOVE-TRACE gap (the traversal runs outside FullWalkMove, M6-A2). "Time left" = T0 − press time, where T0 is the duration of an unpressed traversal at the same height and approach.

## TL;DR

| Question | Answer | Evidence |
|---|---|---|
| Does native SG work at other mantle heights? | **Yes, at H90, H120, H150, H180 and H232**, always exit |v_h| **460.000** (slide-boost cap, M6-A2) and vz ≈ 286.2–286.7 (post) | [meas] 102 SG at 5 heights |
| Timing window (native) | A press ends the traversal on the next usercmd. **Too early → cut without a jump** (exit 299, vz 0); **inside the last ≈ 0.085 s of the traversal → SG**; after the natural end → ordinary jump on top (299). The cut/SG boundary sits between **0.086 and 0.12 s of time left** at every height (cuts and SGs overlap there) | [meas] table below |
| Traversal duration T0 (unpressed, sprint approach) | H90 0.418 s, H120 0.581, H150 0.602, H180 0.600, H232 0.587 | [meas] 2–3 each |
| Success rate in the window | 100 % for presses with time left between 0.005 and 0.085 s at every height (sprint approach); mixed between 0.086 and 0.12 s | [meas] |
| Approach at 30° to the face normal (view 30°, W) | SG 15/15, exit 460 **along the view/input direction (30°)** | [meas] H120 |
| View 45°, W+D (motion normal to the face) | SG 14/15, exit 460 along the input direction (0°, normal to the face); 1 early press cut | [meas] H120 |
| Walk-jump approach (199.5 u/s) | **Mostly no SG**: 12/15 plain mantle jump at 199.5 (crouch gives no slide; below slideRequiredStartSpeed 200, M2 [inf]); 3/15 exit at **402.009** (unexplained) | [meas] H120 |
| Slide-jump approach (397 u/s into the jump) | **No SG (0/15)**: mantle jump at 299 or cut. Consistent with the slide boost not re-arming within ~1.2 s of the first slide (M2 open question 4: no boost on re-entry at 0.92 / 1.32 s) [inf] | [meas] H120 |
| SDK FSM (mantle boost on, server default) | Boost state 4: **388.700 / 367.42**, 15/15 sprint (including a press 0.12 s before the end that is cut natively) and **5/5 after a slide-jump approach** | [meas] H120 control |
| Jump only (no crouch) | Mantle jump at 299 (vz 286.7); 3/12 at **328.98 ≈ 1.1 × 299** when the approach touched the face before the mantle (class `mantle_jump_fast`) | [meas] |

### Window per height (native, sprint approach, press time after the traversal start)

| H | T0 (s) | cut (no jump) | SG 460 | jump on top | SG / pressed |
|---|---|---|---|---|---|
| 90 | 0.418 | 0.274–0.325 (left 0.093–0.143) | 0.309–0.412 (left 0.005–0.108) | 0.408–0.432 | 22/36 |
| 120 | 0.581 | 0.458–0.475 (left 0.106–0.123) | 0.463–0.575 (left 0.006–0.118) | 0.575–0.609 | 24/36 |
| 150 | 0.602 | 0.467–0.516 (left 0.086–0.136) | 0.483–0.584 (left 0.019–0.119) | 0.600–0.617 | 22/36 |
| 180 | 0.600 | 0.492 (left 0.108) | 0.508–0.592 (left 0.008–0.092) | 0.592–0.633 | 22/35 |
| 232 | 0.587 | 0.458–0.492 (left 0.095–0.128) | 0.492–0.560 (left 0.027–0.095) | — | 12/20 |

The pressed counts are the whole sweep (presses deliberately placed before, inside and after the window), not a success rate for a human. At H180, 3 presses at 0.474 s gave a completed mantle without a jump (`mantle_only`, unexplained).

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_050608_M8_sg_h90` | spr none 3, spr sg K 31…49 (3–5 each), spr mb 3 | none |
| `20261022_045433_M8_sg_h120` | as h90 (K 51…69) + walk / slide / ang / wd: none 2 + sg 5 × 3 each | none |
| `20261022_051237_M8_sg_h150` | as h90 (K 54…72) | none |
| `20261022_051917_M8_sg_h180` | as h90 (K 55…73) | r9122 (115.0 fps) |
| `20261022_052359_M8_sg_h232` | spr none 3, spr sg K 53/57/61/65 × 5 | r9201 (107.1 fps) |
| `20261022_052803_M8_sg_h120_fsm` | FSM on: spr none 3, spr sg K 53/59/65 × 5, slide sg K61 × 5 | none |

## Model notes for Unity

```
native SG (Reference, M6-A2): a jump press during the mantle ends it on the next usercmd
    time_left = T_trav - t_press
    time_left > ~0.12 s        -> cut to the ledge, exit (299 * moveDir, vz 0), no jump        [meas; 0.086-0.12 s mixed]
    0 < time_left <= ~0.085 s  -> jump (V 289.8); with crouch held on the exit usercmd: v_h = slide boost min(v+172.5, 460)
                                   along the input direction (view-relative wish)                [meas]
    after the end              -> ordinary ground jump on top (299)
    slide boost not available (recent slide, or speed < 200) -> no SG speed                        [inf]
FSM variant (SDK default): state 4 = 388.7 / 367.42 whenever the press is latched in the last 133 ms (M6-A2) [meas]
```

## Open questions

1. The exact cut/SG boundary (0.086–0.12 s left, mixed): whether it is a time, an animation fraction or a height gate.
2. The 402.009 walk-approach SG exit (3/15) and the 328.98 jump-only exit after a face contact. **Resolved (2026-10-24/25):** native `Jump` adds 30 u/s toward the surface hit on the last move tick (299 + 30; 199.5 + 30 > 200 lets the slide boost apply, + 172.5 = 402.0). See `rea-native/ledger-open/LEDGER-OPEN-5.md` and `rea-native/n11/N11-OPEN-ITEMS.md`.
3. The slide-boost re-arm time that blocks SG after a slide-jump approach (M2 open question 4).
4. Lateral SG with a sideways key pressed during the mantle (strafe held before the press but released at the exit) was not run separately; only the W+D-held case.

## Rerun

```
cd research/phase2-local/m8/r_sg
py -3 sg_analysis.py ../../data/20261022_050608_M8_sg_h90 ../../data/20261022_045433_M8_sg_h120 \
  ../../data/20261022_051237_M8_sg_h150 ../../data/20261022_051917_M8_sg_h180 ../../data/20261022_052359_M8_sg_h232 \
  ../../data/20261022_052803_M8_sg_h120_fsm --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --trials 3 (h232/fsm: 5) -- --fps 120 --legend gibraltar --no-census --state-log --geometry h<H> --both-cvar mantle_boost_enabled=0 --schedule <m8_sg_* list>` (the FSM control without `--both-cvar`).
