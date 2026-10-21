# R5 replay — Unity motor R5MotorV2/m3 vs R5 trials

Generated 2026-10-21 08:10 UTC by Unity 6000.6.5f1. Models: `R5MotorV2/m3` (after) and `ReferenceMotor/m1-first-guess` (before, M1 first guess, reports in `m1_first_guess/`). Errors are sim − ref in Source units (u, u/s), per step aligned by usercmd. Open-loop replay from initial_state with the recorded inputs; nothing is tuned per trial.

## 1. Per trial (R5MotorV2)

Event cells: largest step delta sim − ref over all paired events (count ref/sim). Apex / takeoff vz: largest |error| over all jumps. Terminal: ground speed over the 1 s before the last release (– when that window is not all ground).

| condition | trial | steps | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ (u/s) | takeoff | land | slide start | slide end | apex err (u) | takeoff vz err (u/s) | M1 pos RMS 3D (before) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e2_noinput | [M4_e2_noinput_r1621](M4_e2_noinput_r1621/report.md) | 544 | 0.286 | 0.432 | 0.285 | 0.421 | 0.087 | 0.318 | – | 0 (1) | 0 (1) | – | – | +0.013 | +0.016 | – |
| e2_noinput | [M4_e2_noinput_r1622](M4_e2_noinput_r1622/report.md) | 544 | 0.330 | 0.494 | 0.329 | 0.484 | 0.109 | 0.367 | – | 0 (1) | 0 (1) | – | – | +0.014 | +0.015 | – |
| e4_stand | [M4_e4_stand_r1616](M4_e4_stand_r1616/report.md) | 301 | 0.017 | 0.078 | 0.000 | 0.000 | 0.072 | 0.211 | – | 0 (1) | 0 (1) | – | – | 0.000 | -0.009 | – |
| e4_stand | [M4_e4_stand_r1617](M4_e4_stand_r1617/report.md) | 301 | 0.023 | 0.116 | 0.000 | 0.000 | 0.090 | 0.303 | – | 0 (1) | 0 (1) | – | – | 0.000 | +0.001 | – |
| m4_ctrl_air | [M4_m4_ctrl_air_r1553](M4_m4_ctrl_air_r1553/report.md) | 640 | 10.318 | 16.930 | 10.304 | 16.918 | 19.371 | 185.313 | – | 0 (1) | 0 (1) | – | – | +0.048 | +0.010 | – |
| m4_ctrl_air | [M4_m4_ctrl_air_r1554](M4_m4_ctrl_air_r1554/report.md) | 640 | 10.749 | 17.643 | 10.736 | 17.631 | 19.364 | 185.304 | – | 0 (1) | 0 (1) | – | – | +0.049 | +0.012 | – |
| m4_ctrl_sprint | [M4_m4_ctrl_sprint_r1501](M4_m4_ctrl_sprint_r1501/report.md) | 1019 | 0.582 | 0.663 | 0.036 | 0.043 | 0.005 | 0.018 | 0.000 | – | – | – | – | – | – | – |
| m4_ctrl_sprint | [M4_m4_ctrl_sprint_r1502](M4_m4_ctrl_sprint_r1502/report.md) | 1020 | 0.587 | 0.671 | 0.083 | 0.112 | 0.005 | 0.027 | 0.000 | – | – | – | – | – | – | – |
| m4_grapple_hold | [M4_m4_grapple_hold_r1701](M4_m4_grapple_hold_r1701/report.md) | 721 | 472.265 | 646.911 | 472.240 | 646.911 | 249.420 | 759.351 | – | 0 (1) | +83 (1) | – | – | -5.709 | +0.001 | – |
| m4_grapple_hold | [M4_m4_grapple_hold_r1702](M4_m4_grapple_hold_r1702/report.md) | 721 | 459.604 | 627.858 | 459.568 | 627.858 | 247.248 | 750.089 | – | 0 (2/1) | +81 (2/1) | – | – | -7.831 | +0.004 | – |
| m4_grapple_near | [M4_m4_grapple_near_r2101](M4_m4_grapple_near_r2101/report.md) | 721 | 324.189 | 416.579 | 324.160 | 416.579 | 176.312 | 617.861 | – | 0 (2/1) | +82 (2/1) | – | – | +12.028 | +0.002 | – |
| m4_grapple_near | [M4_m4_grapple_near_r2102](M4_m4_grapple_near_r2102/report.md) | 721 | 323.550 | 415.547 | 323.514 | 415.547 | 176.015 | 615.436 | – | 0 (1) | +81 (1) | – | – | +12.622 | +0.004 | – |
| m4_lift_jumpout | [M4_m4_lift_jumpout_r2006](M4_m4_lift_jumpout_r2006/report.md) | 1393 | 8.125 | 22.869 | 3.032 | 6.558 | 59.166 | 1347.304 | – | -1 (1) | -2 (1) | – | – | -0.109 | 0.000 | – |
| m4_lift_jumpout | [M4_m4_lift_jumpout_r2007](M4_m4_lift_jumpout_r2007/report.md) | 1393 | 13.794 | 45.471 | 6.167 | 13.423 | 82.520 | 1347.909 | – | 0 (1) | -4 (1) | – | – | -0.330 | 0.000 | – |
| m4_lift_ride | [M4_m4_lift_ride_r2001](M4_m4_lift_ride_r2001/report.md) | 1332 | 5.223 | 11.209 | 1.544 | 3.256 | 42.961 | 1347.125 | – | 0 (1) | -1 (1) | – | – | +0.008 | 0.000 | – |
| m4_lift_ride | [M4_m4_lift_ride_r2002](M4_m4_lift_ride_r2002/report.md) | 1332 | 7.510 | 23.140 | 3.207 | 6.773 | 60.020 | 1347.111 | – | -1 (1) | -2 (1) | – | – | -0.125 | 0.000 | – |
| m4_lift_strafe | [M4_m4_lift_strafe_r2011](M4_m4_lift_strafe_r2011/report.md) | 1452 | 349.212 | 453.882 | 116.977 | 153.453 | 224.253 | 1363.504 | – | 0 (1) | -50 (1) | – | – | -7.481 | 0.000 | – |
| m4_lift_strafe | [M4_m4_lift_strafe_r2012](M4_m4_lift_strafe_r2012/report.md) | 1452 | 349.446 | 454.521 | 118.067 | 154.909 | 225.363 | 1358.435 | – | 0 (1) | -51 (1) | – | – | -7.697 | 0.000 | – |
| m4_pad_crouch | [M4_m4_pad_crouch_r1536](M4_m4_pad_crouch_r1536/report.md) | 960 | 8.060 | 21.537 | 3.936 | 9.915 | 62.846 | 1085.022 | – | +1 (1) | +4 (1) | – | – | +1.035 | +0.013 | – |
| m4_pad_crouch | [M4_m4_pad_crouch_r1537](M4_m4_pad_crouch_r1537/report.md) | 960 | 6.022 | 14.531 | 1.428 | 3.705 | 36.959 | 812.449 | – | 0 (1) | +2 (1) | – | – | +3.878 | +0.010 | – |
| m4_pad_sprint | [M4_m4_pad_sprint_r1531](M4_m4_pad_sprint_r1531/report.md) | 720 | 1.306 | 3.516 | 1.121 | 2.721 | 41.022 | 1100.485 | – | 0 (1) | +1 (1) | – | – | +0.446 | +0.008 | – |
| m4_pad_sprint | [M4_m4_pad_sprint_r1532](M4_m4_pad_sprint_r1532/report.md) | 720 | 1.564 | 2.959 | 1.431 | 2.760 | 0.728 | 1.920 | – | 0 (1) | 0 (1) | – | – | +0.449 | +0.008 | – |
| m4_pad_walk | [M4_m4_pad_walk_r1558](M4_m4_pad_walk_r1558/report.md) | 780 | 1.701 | 4.347 | 1.389 | 3.517 | 39.428 | 1100.595 | – | 0 (1) | +1 (1) | – | – | +0.982 | +0.008 | – |
| m4_pad_walk | [M4_m4_pad_walk_r1559](M4_m4_pad_walk_r1559/report.md) | 780 | 1.713 | 4.346 | 1.404 | 3.525 | 39.428 | 1100.580 | – | 0 (1) | +1 (1) | – | – | +0.986 | +0.006 | – |
| m4_pounce_c0 | [M4_m4_pounce_c0_r1901](M4_m4_pounce_c0_r1901/report.md) | 541 | 6.927 | 11.681 | 6.571 | 9.593 | 53.241 | 698.200 | – | -2 (1) | -3 (1) | – | – | -0.882 | -1.671 | – |
| m4_pounce_c0 | [M4_m4_pounce_c0_r1902](M4_m4_pounce_c0_r1902/report.md) | 540 | 6.882 | 11.639 | 6.529 | 9.559 | 53.283 | 698.211 | – | -2 (1) | -3 (1) | – | – | -0.856 | -1.584 | – |
| m4_pounce_c13 | [M4_m4_pounce_c13_r2305](M4_m4_pounce_c13_r2305/report.md) | 696 | 0.588 | 3.485 | 0.279 | 0.401 | 3.511 | 37.803 | – | 0 (1) | 0 (1) | – | – | -0.087 | -0.138 | – |
| m4_pounce_c13 | [M4_m4_pounce_c13_r2306](M4_m4_pounce_c13_r2306/report.md) | 696 | 0.935 | 3.508 | 0.773 | 1.109 | 3.544 | 38.015 | – | 0 (1) | 0 (1) | – | – | -0.244 | -0.375 | – |
| m4_stim_air | [M4_m4_stim_air_r1516](M4_m4_stim_air_r1516/report.md) | 641 | 20.500 | 33.934 | 20.493 | 33.928 | 32.453 | 266.697 | – | 0 (1) | 0 (1) | – | – | +0.043 | +0.014 | – |
| m4_stim_air | [M4_m4_stim_air_r1517](M4_m4_stim_air_r1517/report.md) | 641 | 10.332 | 16.965 | 10.318 | 16.953 | 19.350 | 185.299 | – | 0 (1) | 0 (1) | – | – | +0.049 | +0.015 | – |
| m4_stim_sprint | [M4_m4_stim_sprint_r1506](M4_m4_stim_sprint_r1506/report.md) | 1020 | 0.584 | 0.669 | 0.058 | 0.102 | 0.046 | 0.250 | 0.000 | – | – | – | – | – | – | – |
| m4_stim_sprint | [M4_m4_stim_sprint_r1507](M4_m4_stim_sprint_r1507/report.md) | 1020 | 0.587 | 0.672 | 0.078 | 0.119 | 0.067 | 0.248 | 0.000 | – | – | – | – | – | – | – |
| m4_stim_walk | [M4_m4_stim_walk_r1511](M4_m4_stim_walk_r1511/report.md) | 817 | 0.606 | 0.746 | 0.260 | 0.344 | 0.016 | 0.102 | 0.000 | – | – | – | – | – | – | – |
| m4_stim_walk | [M4_m4_stim_walk_r1512](M4_m4_stim_walk_r1512/report.md) | 817 | 0.571 | 0.691 | 0.160 | 0.200 | 0.013 | 0.103 | 0.000 | – | – | – | – | – | – | – |
| m4_valk_ctrl | [M4_m4_valk_ctrl_r1801](M4_m4_valk_ctrl_r1801/report.md) | 685 | 0.000 | 0.002 | 0.000 | 0.000 | 0.001 | 0.009 | – | 0 (1) | 0 (1) | – | – | 0.000 | +0.002 | – |
| m4_valk_ctrl | [M4_m4_valk_ctrl_r1802](M4_m4_valk_ctrl_r1802/report.md) | 685 | 0.003 | 0.022 | 0.000 | 0.000 | 0.014 | 0.065 | – | 0 (1) | 0 (1) | – | – | 0.000 | +0.003 | – |
| m4_valk_jets | [M4_m4_valk_jets_r1806](M4_m4_valk_jets_r1806/report.md) | 685 | 0.126 | 1.462 | 0.000 | 0.000 | 6.080 | 158.704 | – | 0 (1) | 0 (1) | – | – | -0.058 | +0.004 | – |
| m4_valk_jets | [M4_m4_valk_jets_r1807](M4_m4_valk_jets_r1807/report.md) | 685 | 1.015 | 2.732 | 0.000 | 0.000 | 6.117 | 158.789 | – | 0 (1) | 0 (1) | – | – | -1.339 | -0.007 | – |

## 2. Per condition (R5MotorV2; RMS = mean of the trials, max = worst trial)

| condition | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ | worst event Δ (steps) | apex err | takeoff vz err | M1 pos RMS 3D | M1 vel RMS 3D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e2_noinput | 2 | 0.308 | 0.494 | 0.307 | 0.484 | 0.098 | 0.367 | – | 0 | +0.014 | +0.016 | – | – |
| e4_stand | 2 | 0.020 | 0.116 | 0.000 | 0.000 | 0.081 | 0.303 | – | 0 | 0.000 | -0.009 | – | – |
| m4_ctrl_air | 2 | 10.533 | 17.643 | 10.520 | 17.631 | 19.367 | 185.313 | – | 0 | +0.049 | +0.012 | – | – |
| m4_ctrl_sprint | 2 | 0.585 | 0.671 | 0.060 | 0.112 | 0.005 | 0.027 | 0.000 | – | – | – | – | – |
| m4_grapple_hold | 2 | 465.935 | 646.911 | 465.904 | 646.911 | 248.334 | 759.351 | – | +83 (count mismatch) | -7.831 | +0.004 | – | – |
| m4_grapple_near | 2 | 323.870 | 416.579 | 323.837 | 416.579 | 176.164 | 617.861 | – | +82 (count mismatch) | +12.622 | +0.004 | – | – |
| m4_lift_jumpout | 2 | 10.959 | 45.471 | 4.599 | 13.423 | 70.843 | 1347.909 | – | -4 | -0.330 | 0.000 | – | – |
| m4_lift_ride | 2 | 6.366 | 23.140 | 2.375 | 6.773 | 51.491 | 1347.125 | – | -2 | -0.125 | 0.000 | – | – |
| m4_lift_strafe | 2 | 349.329 | 454.521 | 117.522 | 154.909 | 224.808 | 1363.504 | – | -51 | -7.697 | 0.000 | – | – |
| m4_pad_crouch | 2 | 7.041 | 21.537 | 2.682 | 9.915 | 49.902 | 1085.022 | – | +4 | +3.878 | +0.013 | – | – |
| m4_pad_sprint | 2 | 1.435 | 3.516 | 1.276 | 2.760 | 20.875 | 1100.485 | – | +1 | +0.449 | +0.008 | – | – |
| m4_pad_walk | 2 | 1.707 | 4.347 | 1.397 | 3.525 | 39.428 | 1100.595 | – | +1 | +0.986 | +0.008 | – | – |
| m4_pounce_c0 | 2 | 6.904 | 11.681 | 6.550 | 9.593 | 53.262 | 698.211 | – | -3 | -0.882 | -1.671 | – | – |
| m4_pounce_c13 | 2 | 0.762 | 3.508 | 0.526 | 1.109 | 3.528 | 38.015 | – | 0 | -0.244 | -0.375 | – | – |
| m4_stim_air | 2 | 15.416 | 33.934 | 15.405 | 33.928 | 25.902 | 266.697 | – | 0 | +0.049 | +0.015 | – | – |
| m4_stim_sprint | 2 | 0.585 | 0.672 | 0.068 | 0.119 | 0.056 | 0.250 | 0.000 | – | – | – | – | – |
| m4_stim_walk | 2 | 0.588 | 0.746 | 0.210 | 0.344 | 0.014 | 0.103 | 0.000 | – | – | – | – | – |
| m4_valk_ctrl | 2 | 0.002 | 0.022 | 0.000 | 0.000 | 0.007 | 0.065 | – | 0 | 0.000 | +0.003 | – | – |
| m4_valk_jets | 2 | 0.570 | 2.732 | 0.000 | 0.000 | 6.098 | 158.789 | – | 0 | -1.339 | -0.007 | – | – |

## 3. Ground mapping: terminal speed and accel/decel, Unity motor vs R5

Same estimator on both series (ReplayMetrics.Ground: GROUND-MODEL §1 — band by nearest nominal rate, rate = ΣΔs/Σdt, decel excludes the zeroing step). Unity spread = (max − min)/mean over the condition's trials (plan acceptance: terminal ≤ 2 %, accel/decel ≤ 5 %); Unity vs R5 = (sim mean − ref mean)/ref mean.

| condition | quantity | R5 per trial | Unity per trial | R5 mean | Unity mean | Unity vs R5 | R5 spread | Unity spread | acceptance (Unity spread) |
|---|---|---|---|---|---|---|---|---|---|
| e2_noinput | accel_low (u/s²) | 2875.250 / 2876.871 | 2875.000 / 2875.000 | 2876.060 | 2875.000 | -0.037 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | accel_mid (u/s²) | 517.886 / 517.694 | 517.500 / 517.500 | 517.790 | 517.500 | -0.056 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | accel_sprint (u/s²) | 115.050 / 115.019 | 115.000 / 115.000 | 115.035 | 115.000 | -0.030 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | decel_stand (u/s²) | 1250.393 / 1249.758 | 1250.000 / 1250.000 | 1250.075 | 1250.000 | -0.006 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| m4_ctrl_air | accel_low (u/s²) | 3732.420 / 2875.855 | 3731.863 / 2875.000 | 3304.138 | 3303.431 | -0.021 % | 25.92 % | 25.94 % | FAIL (> 5 %) |
| m4_ctrl_air | accel_mid (u/s²) | 671.829 / 517.631 | 671.735 / 517.500 | 594.730 | 594.618 | -0.019 % | 25.93 % | 25.94 % | FAIL (> 5 %) |
| m4_ctrl_air | accel_sprint (u/s²) | 153.581 / 115.022 | 148.665 / 115.000 | 134.301 | 131.833 | -1.838 % | 28.71 % | 25.54 % | FAIL (> 5 %) |
| m4_ctrl_air | decel_stand (u/s²) | 1250.152 / 1250.115 | 1250.000 / 1250.000 | 1250.133 | 1250.000 | -0.011 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_ctrl_sprint | terminal speed (u/s) | 299.000 / 299.000 | 299.000 / 299.000 | 299.000 | 299.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| m4_ctrl_sprint | accel_low (u/s²) | 2874.705 / 2874.630 | 2875.000 / 2875.000 | 2874.668 | 2875.000 | +0.012 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_ctrl_sprint | accel_mid (u/s²) | 517.494 / 517.528 | 517.500 / 517.500 | 517.511 | 517.500 | -0.002 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_ctrl_sprint | accel_sprint (u/s²) | 115.001 / 115.009 | 115.000 / 115.000 | 115.005 | 115.000 | -0.004 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_ctrl_sprint | decel_stand (u/s²) | 1249.962 / 1250.058 | 1250.000 / 1250.000 | 1250.010 | 1250.000 | -0.001 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_grapple_hold | decel_stand (u/s²) | 77.946 / 77.181 | 1250.000 / 1250.000 | 77.563 | 1250.000 | +1511.588 % | 0.99 % | 0.00 % | pass (≤ 5 %) |
| m4_grapple_near | decel_stand (u/s²) | 32.707 / 78.810 | 1250.000 / 1250.000 | 55.758 | 1250.000 | +2141.814 % | 82.68 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_jumpout | accel_low (u/s²) | 2874.443 / 2874.775 | 2875.000 / 2875.000 | 2874.609 | 2875.000 | +0.014 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_jumpout | accel_mid (u/s²) | 517.561 / 517.614 | 517.500 / 517.500 | 517.587 | 517.500 | -0.017 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_jumpout | decel_stand (u/s²) | 1250.503 / 1250.332 | 1250.000 / 1250.000 | 1250.418 | 1250.000 | -0.033 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_ride | accel_low (u/s²) | 2874.965 / 2876.095 | 2875.000 / 2875.000 | 2875.530 | 2875.000 | -0.018 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_ride | accel_mid (u/s²) | 517.519 / 517.516 | 517.500 / 517.500 | 517.518 | 517.500 | -0.003 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_ride | decel_stand (u/s²) | 1250.295 / 1250.206 | 1250.000 / 1250.000 | 1250.251 | 1250.000 | -0.020 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_strafe | accel_low (u/s²) | 2876.491 / 2875.155 | 2875.000 / 2875.000 | 2875.823 | 2875.000 | -0.029 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_strafe | accel_mid (u/s²) | 517.674 / 517.745 | 517.500 / 517.500 | 517.709 | 517.500 | -0.040 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_lift_strafe | decel_stand (u/s²) | 1250.653 / 1250.784 | 1250.000 / 1250.000 | 1250.719 | 1250.000 | -0.057 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_crouch | accel_low (u/s²) | 2875.520 / 2875.642 | 2875.000 / 2875.000 | 2875.581 | 2875.000 | -0.020 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_crouch | decel_stand (u/s²) | 1251.616 / 1250.494 | 1250.000 / 1250.000 | 1251.055 | 1250.000 | -0.084 % | 0.09 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_sprint | accel_low (u/s²) | 2878.049 / 2871.719 | 2875.000 / 2875.000 | 2874.884 | 2875.000 | +0.004 % | 0.22 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_sprint | accel_mid (u/s²) | 517.921 / 518.069 | 517.500 / 517.500 | 517.995 | 517.500 | -0.095 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_sprint | accel_sprint (u/s²) | 115.056 / 115.086 | 115.000 / 115.000 | 115.071 | 115.000 | -0.062 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_sprint | decel_stand (u/s²) | 1251.920 / 1250.786 | 1250.000 / 1250.000 | 1251.353 | 1250.000 | -0.108 % | 0.09 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_walk | accel_low (u/s²) | 2875.915 / 2874.995 | 2875.000 / 2875.000 | 2875.455 | 2875.000 | -0.016 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_walk | accel_mid (u/s²) | 517.516 / 517.580 | 517.500 / 517.500 | 517.548 | 517.500 | -0.009 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_pad_walk | decel_stand (u/s²) | 1250.150 / 1250.300 | 1250.000 / 1250.000 | 1250.225 | 1250.000 | -0.018 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_pounce_c0 | decel_stand (u/s²) | 1249.999 / 1250.047 | 1250.000 / 1250.000 | 1250.023 | 1250.000 | -0.002 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_pounce_c13 | decel_stand (u/s²) | 1250.051 / 1250.025 | 1250.000 / 1250.000 | 1250.038 | 1250.000 | -0.003 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_air | accel_low (u/s²) | 2875.691 / 3730.935 | 2875.000 / 3731.863 | 3303.313 | 3303.431 | +0.004 % | 25.89 % | 25.94 % | FAIL (> 5 %) |
| m4_stim_air | accel_mid (u/s²) | 517.701 / 671.805 | 517.500 / 671.735 | 594.753 | 594.618 | -0.023 % | 25.91 % | 25.94 % | FAIL (> 5 %) |
| m4_stim_air | accel_sprint (u/s²) | 143.150 / 148.547 | 143.137 / 146.720 | 145.848 | 144.929 | -0.631 % | 3.70 % | 2.47 % | pass (≤ 5 %) |
| m4_stim_air | decel_stand (u/s²) | 1250.442 / 1250.539 | 1250.000 / 1250.000 | 1250.490 | 1250.000 | -0.039 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_sprint | terminal speed (u/s) | 420.954 / 420.954 | 420.954 / 420.954 | 420.954 | 420.954 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| m4_stim_sprint | accel_low (u/s²) | 2874.121 / 2874.925 | 2875.000 / 2875.000 | 2874.523 | 2875.000 | +0.017 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_sprint | accel_mid (u/s²) | 517.537 / 517.574 | 517.500 / 517.500 | 517.556 | 517.500 | -0.011 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_sprint | accel_sprint (u/s²) | 142.557 / 143.124 | 142.552 / 143.117 | 142.841 | 142.835 | -0.004 % | 0.40 % | 0.40 % | pass (≤ 5 %) |
| m4_stim_sprint | decel_stand (u/s²) | 1249.957 / 1250.064 | 1250.000 / 1250.000 | 1250.010 | 1250.000 | -0.001 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_walk | terminal speed (u/s) | 258.991 / 258.991 | 258.991 / 258.991 | 258.991 | 258.991 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| m4_stim_walk | accel_low (u/s²) | 3733.000 / 3733.413 | 3731.863 / 3731.863 | 3733.207 | 3731.863 | -0.036 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_walk | accel_mid (u/s²) | 672.184 / 671.993 | 671.735 / 671.735 | 672.089 | 671.735 | -0.053 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| m4_stim_walk | decel_stand (u/s²) | 1250.387 / 1249.818 | 1250.000 / 1250.000 | 1250.103 | 1250.000 | -0.008 % | 0.05 % | 0.00 % | pass (≤ 5 %) |

## 4. Flags (R5MotorV2 vs reference columns; steps that differ)

| trial | grounded | sliding | sprinting | maxspeed (n compared) |
|---|---|---|---|---|
| M4_e2_noinput_r1621 | 0 | 0 | 0 | 0 (544) |
| M4_e2_noinput_r1622 | 0 | 0 | 0 | 0 (544) |
| M4_e4_stand_r1616 | 0 | 0 | 0 | 0 (301) |
| M4_e4_stand_r1617 | 0 | 0 | 0 | 0 (301) |
| M4_m4_ctrl_air_r1553 | 0 | 0 | 0 | 60 (640) |
| M4_m4_ctrl_air_r1554 | 0 | 0 | 0 | 0 (640) |
| M4_m4_ctrl_sprint_r1501 | 0 | 0 | 0 | 0 (1019) |
| M4_m4_ctrl_sprint_r1502 | 0 | 0 | 0 | 0 (1020) |
| M4_m4_grapple_hold_r1701 | 83 | 0 | 0 | 0 (721) |
| M4_m4_grapple_hold_r1702 | 82 | 0 | 0 | 0 (721) |
| M4_m4_grapple_near_r2101 | 81 | 0 | 0 | 0 (721) |
| M4_m4_grapple_near_r2102 | 81 | 0 | 0 | 0 (721) |
| M4_m4_lift_jumpout_r2006 | 3 | 0 | 0 | 0 (1393) |
| M4_m4_lift_jumpout_r2007 | 4 | 0 | 0 | 0 (1393) |
| M4_m4_lift_ride_r2001 | 1 | 0 | 0 | 0 (1332) |
| M4_m4_lift_ride_r2002 | 3 | 0 | 0 | 0 (1332) |
| M4_m4_lift_strafe_r2011 | 50 | 0 | 0 | 0 (1452) |
| M4_m4_lift_strafe_r2012 | 51 | 0 | 0 | 0 (1452) |
| M4_m4_pad_crouch_r1536 | 5 | 0 | 0 | 172 (960) |
| M4_m4_pad_crouch_r1537 | 2 | 0 | 0 | 170 (960) |
| M4_m4_pad_sprint_r1531 | 1 | 0 | 1 | 121 (720) |
| M4_m4_pad_sprint_r1532 | 0 | 0 | 1 | 121 (720) |
| M4_m4_pad_walk_r1558 | 1 | 0 | 0 | 120 (780) |
| M4_m4_pad_walk_r1559 | 1 | 0 | 0 | 120 (780) |
| M4_m4_pounce_c0_r1901 | 5 | 0 | 0 | 9 (541) |
| M4_m4_pounce_c0_r1902 | 5 | 0 | 0 | 9 (540) |
| M4_m4_pounce_c13_r2305 | 0 | 0 | 0 | 6 (696) |
| M4_m4_pounce_c13_r2306 | 0 | 0 | 0 | 6 (696) |
| M4_m4_stim_air_r1516 | 0 | 0 | 0 | 1 (641) |
| M4_m4_stim_air_r1517 | 0 | 0 | 0 | 62 (641) |
| M4_m4_stim_sprint_r1506 | 0 | 0 | 0 | 62 (1020) |
| M4_m4_stim_sprint_r1507 | 0 | 0 | 0 | 62 (1020) |
| M4_m4_stim_walk_r1511 | 0 | 0 | 0 | 18 (817) |
| M4_m4_stim_walk_r1512 | 0 | 0 | 0 | 38 (817) |
| M4_m4_valk_ctrl_r1801 | 0 | 0 | 0 | 0 (685) |
| M4_m4_valk_ctrl_r1802 | 0 | 0 | 0 | 0 (685) |
| M4_m4_valk_jets_r1806 | 0 | 0 | 0 | 0 (685) |
| M4_m4_valk_jets_r1807 | 0 | 0 | 0 | 0 (685) |

## Model choices (R5MotorV2)

- Units: SOURCE (u, u/s); one step per usercmd with the recorded dt (dt / n_cmds sub-steps); double precision; flat floor at initial_state z.
- Parameters: census class vars from the trial's own trial.json parameters; fitted constants (crouch speed 80, crouch decel 1500, stop snap 1, ground probe 2, multi-jump t0 0.15 / T 0.60, refund window 0.4) from the M2 params.json; movescale per step from samples.csv when present.
- Ground (GROUND-MODEL §2): piecewise accel low/mid/sprint by PRE-move speed, sprint edge rule 's + sprintAccel·msc·dt < speed·msc', caps speed/sprintspeed/crouch 80 ×msc, constant decel 1250 standing / 1500 ducked (not ×msc), snap < 1 u/s to 0, v = s·wishdir (instant redirect, diagonal normalized, input magnitude ignored on the ground).
- Sprint flag (GROUND-MODEL §3.3 'spr set one command after the press'; AIR-JUMP §3.1/§4.1): grounded pre-state, sprint held on this AND the previous command, forward > 0, not ducked, not sliding. Sprint button = IN_SPEED (1<<17) or bit 15 (the M2 trials record sprint as bit 15; in_sprint is always 0).
- Ducked state (choice): ducked = IN_DUCK held on the previous command (pre-state flag, mirrors the sprint flag lag); the release command still decelerates at 1500 in e5 data.
- Ground over-speed with input held (choice, not in GROUND-MODEL): s = max(cap, s - D·dt) with D = 1500 ducked (SLIDE-MODEL §4) or deceleration standing.
- speedScaleBack / speedScaleSide (choice, both 1 in every trial): multiply the cap when fwd < 0 / when fwd = 0 and side != 0.
- Jump (AIR-JUMP §2.2, §4.2, §6): press edge while grounded; frac = clamp(f + (1-f)(t-0.15)/0.60, f, 1), f = antiMultiJumpHeightFrac, t = start of the jump command - start of the last landing command (first jump of a trial: no landing yet -> frac 1, the trial reset is not a landing); V = sqrt(2 g H frac); vz = -g dt/2 + V, -g dt/2, move, -g dt/2 (post vz = V - 1.5 g dt); no ground friction; the jump command uses AirAccelerate (choice: 'ground clamp still applies' read as the clamp on ground commands only).
- Air (AIR-JUMP §2.1, §3.2): half-step gravity g = sv_gravity·gravityScale; AirAccelerate accelspeed = airAcceleration·dt, wishcap = airSpeed·msc, wishspeed = min(|wishvel|,1)·maxspeed_air (speed·msc, crouch·msc if duck held), current yaw; no air friction/drag.
- Land (AIR-JUMP §2.3): vz < 0 and floor within 2 u below after the move -> grounded, vz = 0, z kept; the next ground command snaps z to the floor.
- Slide (SLIDE-MODEL §6): duck press edge, grounded, |v| >= slideRequiredStartSpeed (unscaled) -> vPeak = min(|v| + 150·msc, 400·msc) before the move, lastBoost = vPeak - |v|; per command s = (s - 100·dt)·0.7^dt along the current velocity direction (no steering, no slideAccel); ends after the first command with post s < 125; ducked afterwards: over-speed decel 1500 down to 92.
- Slide jump (SLIDE-MODEL §5, H1): now - tBoost < 0.4 s -> s -= lastBoost, else s = max(s, 350); H = slideJumpHeight 50; the multi-jump frac is applied to slide jumps too (choice; frac = 1 in every trial used). Landing with duck held and s >= 200 resumes the slide with no boost and no speed loss.
- Lurch (M3 LURCH-MODEL §8): on an airborne command whose buttons gain a bit of IN_FORWARD|IN_BACK|IN_MOVELEFT|IN_MOVERIGHT (0x618) vs the previous command, with move input, AFTER AirAccelerate: t = start of the press command - start of the last jump command (time-based window); lam = 0.7·clamp((0.5 - t)/0.3, 0, 1); d = normalize((1-lam)·v̂ + lam·wishdir) (skipped when zero); D = |v|·d - v, |D| <= 209.3; v_xy += D. Every new press edge can lurch (several presses per jump untested). Back = straight 209.3 brake, W re-press = no-op by geometry. No jump since Reset -> no lurch. Not modelled: cutoff speed 1100, mantle-boost suppression, movescale dependence of 209.3.
- Ground jump speed (M3 E8 hop350): a non-slide ground jump sets v_xy = min(|v_xy|, sprintspeed·msc) (299 at msc 1.15) before AirAccelerate, whatever the stance/sprint flag (walk-speed hops untested; min(v, cap) and max(v - 100, cap) only differ above 399).
- Slide chain (M3 E8 slide_chain): a slide resumed by a ducked landing (s >= slideRequiredStartSpeed) is flagged 'not boosted'; its slide jump keeps the horizontal speed (no 350 floor, no refund). A slide started by the duck press (boost) keeps the M2 rule. A trial that starts sliding counts as boosted (M2 behaviour).
- Not modelled: slideAccel / slideWantToStopDecel / slideMaxStopSpeed, landSlowdown, the 1.4e-5·vz² residual air gain, the duck transition (hull/eye offset), sprint timing keys, server corrections, slopes/steps/collisions, walls/climb/mantle in the replay (WallBounce / MantleBoost are separate primitives).

