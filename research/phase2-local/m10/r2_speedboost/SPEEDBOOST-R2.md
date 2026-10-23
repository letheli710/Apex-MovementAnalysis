# M10 track R2: speed_boost severity -> move scale

Status: R2 session 1 (`data/20261023_000555_M10R2_s1`, sub-runs `M10R2_wraith`, `M10R2_wraith2`) on the R5Flowstate **local
hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps, Wraith with kit, lane C. The effect is applied by a
dedi EVAL at the reset (`StatusEffect_AddTimed( p, eStatusEffect.speed_boost, S, 5 s, fade 0 )`, a harness shortcut), then a
real-input sprint. Nothing is committed. Labels **[meas] [src] [inf]**.

## TL;DR

**msc = W · (1 + 2·q(S))**, with **q(S) = floor(255·S)/255** (the severity is stored as a byte) and **W** the hold term:
**1.15** with the default melee in hand (every HSD baseline), **1.0** while an ability holsters or locks the weapons (portal
placement, Into the Void). Max speed = 260·msc sprinting, 173.5·msc walking. Two effects at once: **the larger severity wins**
(no sum). A timed effect's fade is **inside** its duration (hold = duration − fade, then a linear fade). [meas, exact to 1e-4]

| Script S | logged q | msc (W 1.15) | sprint v_h | ×(vs 299) | n |
|---|---|---|---|---|---|
| none | 0 | 1.15 | 299.0 | 1.000 | 2 |
| 0.05 | 0.0471 | 1.2582 | 327.14 | 1.094 | 2 |
| 0.10 | 0.0980 | 1.3755 | 357.63 | 1.196 | 2 |
| 0.15 | 0.1490 | 1.4927 | 388.11 | 1.298 | 2 |
| 0.20 | 0.2000 | 1.6100 | 418.60 | 1.400 | 2 |
| 0.30 | 0.2980 | 1.8355 | 477.23 | 1.596 | 3 |
| 0.40 | 0.4000 | 2.0700 | 538.20 | 1.800 | 2 |
| 0.50 | 0.4980 | 2.2955 | 596.83 | 1.996 | 2 |
| 1.00 | 1.0000 | 3.4500 | 897.00 | 3.000 | 2 |
| 0.2 + 0.1 | 0.2000 | 1.6100 | 418.60 | 1.400 | 3 |

Every case: measured msc − model = 0.0000; client and dedi severities agree (dedi `StatusEffect_GetSeverity`).

## What this resolves

- **"0.2 → ×1.22 (Wraith placement)" is not a different mapping.** During portal placement W = 1.0 (weapons locked): msc
  1.4 = 1.0·(1 + 0.4), sprint 364.0 = 260·1.4, walk 242.9 = 173.5·1.4 [meas, 6 + 3 trials]. Relative to the normal 299
  sprint (W 1.15) that is ×1.217. The same rule gives the long-portal steps: q 0.298 → 1.596 (+38.8 %), 0.4 → 1.8 (+56.5 %),
  0.498 → 1.996 → **518.98** (+73.6 %), i.e. the wiki's **22 / 39 / 57 / 74 %** and the script comment "364 → 518" (see
  `../r2_wraith/PORTAL-R2.md`).
- **Stim 0.149** = byte q of 0.15 → 1.15·1.298 = 1.4927 (M4's formula `1 + 2·0.149·g(t)` is this rule).
- **Into the Void 1.5961** = 1.0·(1 + 2·0.298) (track R: W 1.0 while phased, q of 0.3).
- **Mad Maggie pad 0.15** = ×1.298: in the pad msc 1.4927, sprint 388.11, walk 258.99 [meas, `../r2_maggie`]. D2's "×1.30"
  is right; the "×1.22 for 0.2" doubt came from the W term.
- Fade (`AddTimed( 0.15, 1.5, 0.25 )`): q 0.149 for ~1.25 s, then a linear fade to 0 over ~0.25 s (0.134 → 0.05 → 0) [meas 2].

## For HSD (Reference)

- One shared speed-boost rule: `multiplier = W · (1 + 2·q)`, q byte-quantised; boosts do not stack (max severity); timed
  boost = hold (duration − fade) + linear fade. Presets: Maggie pad 0.15, Bloodhound/Mirage/Bangalore 0.15 [src], Wraith portal
  0.2 → 0.5, Void 0.3 (W 1.0), Stim 0.15 (it is a separate status but the same 0.149 multiplier).
- W (weapon/hold term): HSD has no weapon slot; keep W = 1.15 as the normal state and W = 1.0 for abilities that holster the
  weapons in S21 scripts (portal placement, Void). [meas locally; S21 server not testable]

## Evidence classes and splits

- Local hybrid [meas]; client = dedi for all cases (the client predicts the same msc from the networked severity).
- The rule (1 + 2·sev) is also written in the SDK's notes on the S21 client move scale [src: s21-r5sdk mantle_boost.cpp
  comment, melee_lunge_probe.cpp]. S3-dedi vs S21-client difference: none seen.

## Exclusions

r18112 s030, r18113–18114 s040, r18119 stack (fps 100–110); re-run in sub-run `M10R2_wraith2` (r18201–18206).

## Rerun

```
cd research/phase2-local/m10/r2_speedboost
py -3 speedboost_analysis.py ../../data/20261023_000555_M10R2_s1 --json results.json --params params.json > analysis_output.txt
```

Trials: `tools/hsd_trial.py --legend wraith --kit --no-census --state-log --fps 120 --schedule m10r2_sev_<case>*2,...`
(cases ctrl, s005, s010, s015, s020, s030, s040, s050, s100, stack, fade), run inside the R2 game session (see
`../r2_wraith/PORTAL-R2.md` for the session layout).
