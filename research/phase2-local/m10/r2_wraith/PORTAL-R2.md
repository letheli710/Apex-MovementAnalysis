# M10 track R2: Wraith Dimensional Rift (portal) follow-up

Status: 2 game sessions on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps,
Wraith with kit, **real inputs** for placement and travel. Nothing is committed. Labels **[meas] [src] [inf]**.
Local script: `mp_weapon_phase_tunnel.nut` (Flowstate copy, tuning marked "post s15"; S16 long-portal changes present).
Sessions: `data/20261023_000555_M10R2_s1` (all R2 sub-runs; portal sub-runs `M10R2_wraith`, `M10R2_wraith2`) and
`data/20261023_002614_M10R2_s2` (`M10R2_s2wraith`: Void + portal).

## TL;DR (for the Unity portal build)

| Item | Answer | Evidence |
|---|---|---|
| Long portal | No ≥ 6000 u straight route exists (field ≤ 2300 u). Used a **5238 u drop**: a flat rock top floated at z 5532.8 (floor 294.9), sprint off, fall, land, sprint 2 s, end portal. Placement 6.5–6.6 s, recorded path **6075–6114 u**, portal gap 5285 u. | [meas 3] |
| Distance speed steps | Severity **0.2 → 0.298 → 0.4 → 0.498** while falling, at **43–48 %, 65–71 %, 87 %** of 6000 u straight (3D) distance from the start node. Script: +0.1 when the % exceeds the last step's % + 20 (start 0.1, so the 20 % step to 0.2 is hidden under the ability's own 0.2; steps re-base on the crossing value, so 10 Hz sampling at fall speed pushes them later). Floor sprint at 0.498: **518.98** (msc 1.9961 = 1.0·(1 + 2·0.498)). | [meas 3] [src] |
| % mapping (wiki S21 22/39/57/74 % at 0/60/90/120 m) | **Exactly the speed relative to the normal 299 sprint**: W 1.0 while placing (weapons locked), so 0.2 → 364 (+21.7 %), 0.298 → 415 (+38.8 %), 0.4 → 468 (+56.5 %), 0.498 → 519 (+73.6 %). Thresholds 40/60/80 % of 6000 u = 61/91/122 m. See `../r2_speedboost/SPEEDBOOST-R2.md`. | [meas] [wiki] |
| Placement start | The start portal node is recorded **1.11–1.17 s after the ult press** (raise; the press interrupts a sprint: 299 → 65 u/s, then auto-sprint re-accelerates). | [meas 21] |
| Travel | The player rides a script mover through the recorded nodes: **time = clamp(path / 1024, 0.3, 2.0)** (2.0 → 3.5 s for paths 3000–6000 u) at 0.1 s per step, +0.2 s. Measured: 350–480 u paths → **0.5–0.6 s** dedi (client phase 0.48–0.59 s), i.e. **~1160–1250 u/s average**; the 6100–6190 u drop path → **3.7 s** dedi / 3.68–3.69 s client (3.5 s cap), ~1700 u/s, including the vertical part (the replay goes back up the fall). Track R's "replay at the recorded speed (364)" was the velocity *field*, not the motion. | [meas 24] [src] |
| Exit velocity | **Always 0** (dedi and client, n 24 exits incl. both directions, run-in placements whose end node moved at 364, and the long portal). During travel `SetVelocity( node velocity )` writes the recorded node velocities (so the field reads 364 … 177 … 0), but the travel ends with `ClearParent` + `SetAbsOrigin` and the player is free at v = 0. Entry speed (173–593) has no effect. | [meas 24] [src] |
| Exit facing | The view turns along the path during travel (lerp 0.4 s per step) and is not settled at short exits (yaw 44–137° seen after a 180° travel); long travel ends near the travel direction (172° for 180°). | [meas] |
| Min gap | Straight start-node → end-tap distance **125.7 u: no portal** (placement cancelled, start pre-portal removed, **ult not spent**); **141.7–158 u: portal pair** (n 2 + 5). Script 128 u. | [meas 13] [src] |
| Lifetime | Pair → blockers gone **45.1 s** (n 2, 10 Hz). | [meas] [src 45] |
| Standing on the exit | No ping-pong: standing still on the arrival portal for 6 s → one travel only (n 3). | [meas] |
| Repeated use | Step out 0.5 s and walk back in → travels again, both directions, 3 traversals in one trial (n 2). Debounce 0.5 s / use cooldown 0.25 s not resolved finer. | [meas] [src] |
| Into the Void | Walking through the end portal **while phased: no travel** (0/3; min distance to the portal 11–13 u); same walk without Void: travel 3/3. Ult press while phased: nothing (no placement, ult not spent) (n 2). | [meas] [src] |

## Splits

Local hybrid only (S3 dedi authoritative, travel is server-side script; the client follows with prediction off). Client and
dedi agree on exit v = 0 and travel time. S21 server script = local script except where Flowstate edited it [inf]. The
distance-step data are local [meas]; the 60/90/120 m thresholds are the S21-era wiki numbers and fit the measured % rule.

## For HSD

- Portal = recorder + replay: record a node per 0.1 s while placing (position, crouch, velocity); placement boost W 1.0 ·
  (1 + 2·sev), sev 0.2 → +0.1 per 20 % of 6000 u straight distance (cap 0.5 at 80 %); placement starts 1.1 s after the press,
  max 10 s; end needs ≥ 128 u straight from the start (else cancel, refund).
- Travel: replay the node list in reverse (or forward) in clamp(L/1024, 0.3, 2.0..3.5) s, constant node rate; ignore input;
  **exit at v = 0**; arriving players are not re-sent while standing; re-entry allowed after leaving; phased players do not
  travel; lifetime 45 s.
- Replace the M5 preset (exit 300 + 0.3 s lock) and track D's "exit = recorded node velocity" (W-3 contradicted).

## Not measured / limits

- A flat ≥ 6000 u run (no such route); the drop is the S16 "start high" variant (3D distance), so horizontal-only steps are
  inferred from the same rule.
- Other players using the portal (single-player build), projectile teleport, portal glide refund (3 m) rule.
- Session-1 `w_void_in` design failed (the tactical press 0.6 s after the end tap did not fire; one crossing without travel,
  r18136, unexplained); replaced by session-2 `w_vin2` / `w_vctrl`.

## Data and exclusions

Excluded: r18152 / r18154 / r18155 gap trials (+1..+2 frames). Smoke runs (`M10R2_smoke*`) flagged explore, not analysed.
The tower trials use geometry `m10r2tower` (hsd_trial.py). Start-portal entries (`runin_start`, `stand_start`) use a teleport
helper that puts the player 80 u in front of the start portal 1.5 s after the pair exists (harness shortcut; entry by W).

## Rerun

```
cd research/phase2-local/m10/r2_wraith
py -3 portal_analysis.py ../../data/20261023_000555_M10R2_s1 ../../data/20261023_002614_M10R2_s2 \
  --json results.json --params params.json > analysis_output.txt
```

Trials (inside one manually launched game, logs collected once, sub-run runner files merged; see `runners/` in each session):
`tools/hsd_trial.py --legend wraith --kit --no-census --state-log --fps 120 --geometry m10r2tower --schedule
m10r2_w_runin_end*3,m10r2_w_runin_start*3,m10r2_w_stand_start*2,m10r2_w_stay*3,m10r2_w_repeat*2,m10r2_w_void_in*2,
m10r2_w_void_place*2,m10r2_w_drop*3,m10r2_w_tower_ctrl*2,m10r2_w_life*2,m10r2_w_gap_t000..t075*2`; session 2:
`--schedule m10r2_w_vctrl*3,m10r2_w_vin2*3`.
