# M8 R4 (time-boxed): slope slide on the firing-range map (R5Flowstate S21, local offline)

Status: one probe (read-only world traces) and one session (Gibraltar, 120 fps, 15 trials). Downhill only; uphill was not measured (time box). Nothing is committed. Labels: **[meas]**, **[fit]**, **[inf]**.

## Where

A read-only trace grid (M8 probe, same method as `tools/map_scan.py`) found a hillside next to the spawn platform of `mp_rr_canyonlands_staging_mu1`. Along y = 550: flat platform z 1580.03 up to x −10575; then a planar ramp at **29.4°** (normal z 0.8711) to x −10375; then a hillside at **30–41°** (normal z 0.75–0.87, all walkable ≥ 0.7) down to at least x −9500 (z 897). Trials start on the flat at (−10900, 550, 1580.03) facing +X.

## TL;DR

| Question | Answer | Evidence, n |
|---|---|---|
| Speed on the ground | On the slope the engine keeps **vz = 0** and changes only the horizontal speed |v_h| (no free-fall component) | [meas] all slope usercmds |
| Slide downhill (sprint 1 s, crouch on the flat, duck held 3 s) | Slide starts on the flat at 460 (M2 boost cap), decays to **≈ 405 at the slope edge**, then **rises to ≈ 553 u/s** over 2.7 s of slope (29–41°); max 553.3–554.3 | [meas] 5 |
| Slope term | With duck held, the speed change beyond the M2 flat slide law (s' = (s − 100·dt)·0.7^dt) is **extra = 147 + 342·sin(slope) u/s²** (rms 10, slopes 29–41°): ≈ +318 at 30°, +371 at 41° | [fit] 1641 usercmds, 5 trials |
| Duck released, slide flag still on | The slide decays by the flat law again on the 29.9° part (mean extra 24 u/s²): ≈ −255 u/s² at 550 | [meas] 520 usercmds |
| Flat → slope transition | No step: the speed is continuous across the edge (404.8 → 398.1 → 406.5 over the first 0.2 s, the dip is the flat-law decay before the slope term grows) | [meas] 5 |
| Sprint downhill (no crouch) | Exactly **299.0** the whole way (no gravity gain while running); W released → stop by the 1250 decel | [meas] 5 |
| Crouch with W and sprint released on the same usercmd (`m8_slope_slide_now`) | **No slide started** (crouch-walk, then stop) — the design did not test a no-input slide; excluded from the slope fit | [meas] 5 |
| Airborne on the hillside | None (0 airborne usercmds after the slope edge in all trials) | [meas] |

## Caveats

- One hillside, one run-in speed (~405 at the edge), downhill only. The fit's intercept (147 u/s² at sin = 0) is an artefact of the narrow slope range (29–41°); do not extrapolate to shallow slopes.
- The local slope is estimated from each usercmd's own position step (atan(−dz/dxy)).
- Uphill slides, slope edges, slide jumps on the slope and repeated ground/air toggling (anti-exploit) were **not** measured; per the plan the Unity side uses design values there.

## Model note for Unity (design starting point, not a full Apex law)

```
grounded slide, duck held:  s' = (s - 100*dt)*0.7^dt + (147 + 342*sin(slope))*dt      # [fit] 29-41 deg downhill only
duck released:              flat law only (slope term off)                              # [meas]
running (not sliding):      sprint cap unchanged on the slope (299)                     # [meas]
```

## Data

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_054315_M8_slope` | m8_slope_slide 5, m8_slope_slide_now 5, m8_slope_run 5 | none (slide_now is reported but not a slide) |

## Rerun

```
cd research/phase2-local/m8/r_slope
py -3 slope_analysis.py ../../data/20261022_054315_M8_slope --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --label M8_slope --trials 5 -- --fps 120 --legend gibraltar --no-census --state-log --schedule m8_slope_slide,m8_slope_slide_now,m8_slope_run`.
