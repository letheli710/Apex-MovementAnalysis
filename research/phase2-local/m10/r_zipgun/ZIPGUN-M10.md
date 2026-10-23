# M10 track R ②: Pathfinder Zipline Gun (ultimate) on the local build

Status: 2 sessions (`20261022_204553_M10R_zip`, `20261022_213835_M10R_zip2`) on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**,
offline, 120 fps, Pathfinder with kit, plus 2 exploration trials (not used for numbers). Nothing is committed. Labels **[meas]
[src] [inf]**; spec = track D `m10/d_library/TECHNIQUE-LIBRARY-M10.md` §6 Z-1..Z-4.

## TL;DR

| Item | Answer | Evidence | Spec |
|---|---|---|---|
| Deployable locally? | **Yes, the real ultimate**: tap ultimate (raise), 1.0 s later tap attack. The local `mp_weapon_zipline.nut` carries an S3-dedi patch at `Zipline_SetBeginStation` (script comment), so the local script is not pristine S21. Weapon mods at every reset: `survival_finite_ordnance` only (no `upgrade_ult_one`), so the default block applies: `zipline_distance_min 700`, `zipline_distance_max 8000`. | [meas 66 fires] [src] | — |
| Minimum distance | Floor target 600 u: dry fire (no rope, ammo kept); 800 u: rope. Wall 610 u: dry; 790 u: rope. | [meas 12] | Z-1 agree |
| Ground only | Fire in the air (jump, 0.25 s): no rope, ammo kept (script: only on ground / wallrun / wall hang). | [meas 3] | Z-1 agree |
| Long / odd targets | Pitch 0: rope to far terrain, 3639 u. Pitch −40: rope to the overhead structure, 2631 u at 39.8°. 8000 u could not be reached on the field (not tested). | [meas 6] | not testable (max) |
| Rope geometry | Begin station at the player (rope start 16 u from the origin, **112.1–112.7 u above the floor**); end station at the hit point, rope end 112.7 u above the hit surface; the rope is complete 0.3–0.8 s after the fire (projectile 2600 u/s [src]). Steep flag at \|dir.z\| > 0.7 (44.4°) [src]: 42.3° rope normal, 52.1° rope steep. | [meas] [src] | — |
| Several ropes | 4 gun ropes coexisted after 4 fires (script cap 10 per player [src]). | [meas 3] | — |
| Ride speed | Mount from the begin station with use: **502 at 0.5 s, 641 at 1.0 s, 782 at 1.5 s** (+280 u/s² after 0.5 s), 940 at the end of a 1475 u flat rope; on a 3676 u rope (9.3° up) it reaches **1000 at ~2.3 s and stays at 1000**. Map ropes (M6-A3, `CreateZipline`) cap at `ziplineSpeed 600` after 1.25 s. So gun ropes cap at 1000, not 600. | [meas 2 flat + 1 long + 9 sloped] | Z-2 agree on the 1000 cap (not constant: it ramps) |
| End of ride | Auto-detach 90–130 u before the end (script `ZiplineAutoDetachDistance 100`). Exit capped at **600 along the rope**: flat (600, 0), 11° (589, 0, +113 at the detach), 42° (444, 0, 335 after 0.1 s). **52° (steep): exit vertical** (v_h ~14, vz ~485 after 0.1 s). | [meas 11] | Z-3 contradict ("exit ~800") |
| Jump-off | Flat rope at 584 u/s: **(400, 0, 289.8)** = the map-rope law v_out = rope·min(v, 400) + 289.8 (M6). Steep 52° rope with the view turned 90°: **v = (0, −400, 289.8)**, the jump follows the view (2 of 3; the third turned too late). 42° rope: along the rope (296, 0, 559). | [meas 8] | Z-3 agree (free direction on steep), Z-4 agree |
| Super jump | Use, then jump on the next frames from the begin station: vz ~580, v_h 19. | [meas 3] | Z-4 agree |
| Cooldown | Ult clip refills **0.80–0.99 / s** after a fire (clip 180 → ~3 min; script `regen_ammo_refill_rate 1`); a destroyed rope within 3 s refunds [src]. | [meas 52] | — |
| Grapple onto the own rope | First design missed (aim at 60 u; the rope is 112 u up; 3/3). Retry (rope fired 9.2° up, grapple at 260 u lateral): **1 of 2 hooked the rope and was handed to the zipline** (as map ropes, M6); the ride then restarted the normal ramp (incoming 397 → 252 → 502 at 0.5 s) instead of keeping the grapple speed. The other trial missed. | [meas 1 + 1 miss] | — |

## Data and exclusions

Session `20261022_204553_M10R_zip`: 69 scored. Excluded: r16436 `ride_d1500`, r16456 `ride_s40_jump90` (schedule frame count +1 / +3),
r16471 `m10_g_tether` (grapple part, see `../r_grapple`). Geometry: M3 rock stacked twice at lane A (`s950`, face x −13706) for the
wall / steep targets, `m10fly` for the grapple tether. Logger: dedi `[M10-ZIP]` 10 Hz (every `zipline_start` with its linked
`zipline_end`, zipline flag, clip); the ride itself is a MOVE-TRACE gap, so ride speeds come from client per-frame HSD-MD frames
and the `[HSD-STATE] zip` flag. Every reset takes the player off a rope and destroys the earlier gun ropes (except `keep`).

## Model for HSD

- Placement: ground only; target distance 700..8000 (3D); rope ends 112 u above each station's surface; one rope per charge,
  ~180 s recharge, up to 10 ropes.
- Riding a gun rope uses the existing rope system, but with **no 600 cap during the ride** (accelerates to ≥ 940 in 2 s);
  end-exit capped at 600 along the rope; steep ropes (> 44.4°) exit vertically and allow a jump-off along the view; jump-off law
  unchanged. [inf: the gun rope is the `zipline` entity with ZiplineVertical / ZiplinePreserveVelocity on steep ropes; the
  ride-speed difference to map ropes is measured, its source key was not identified.]

## Open questions

1. Which setting gives gun ropes the 1000 cap (map ropes 600).
2. Grapple handoff speed: the ride restarts its ramp; one hooked trial only.
3. Maximum distance 8000 and wall-run / wall-hang placement (not reachable on the field).

## Rerun

```
cd research/phase2-local/m10/r_zipgun
py -3 zipgun_analysis.py ../../data/20261022_204553_M10R_zip ../../data/20261022_213835_M10R_zip2 --json results.json --params params.json > analysis_output.txt
```

Session: `tools/hsd_session.py --label M10R_zip --trials 3 --run-base 16401 --batch-base 16401 -- --fps 120 --legend pathfinder --kit
--no-census --state-log --m10-log --geometry s950,m10fly --schedule <the 21 m10_z_* names + m10_g_rel_t16,m10_g_rel_t18,m10_g_tether>`;
`--label M10R_zip2 --run-base 17101 --batch-base 17101 -- ... --no-census --state-log --m10-log --schedule m10_z_grapple_rope2` (r17101 excluded: +5 frames).
