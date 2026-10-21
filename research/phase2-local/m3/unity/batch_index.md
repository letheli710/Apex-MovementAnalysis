# R5 replay — Unity motor R5MotorV2/m3 vs R5 trials

Generated 2026-10-21 03:53 UTC by Unity 6000.6.5f1. Models: `R5MotorV2/m3` (after) and `ReferenceMotor/m1-first-guess` (before, M1 first guess, reports in `m1_first_guess/`). Errors are sim − ref in Source units (u, u/s), per step aligned by usercmd. Open-loop replay from initial_state with the recorded inputs; nothing is tuned per trial.

## 1. Per trial (R5MotorV2)

Event cells: largest step delta sim − ref over all paired events (count ref/sim). Apex / takeoff vz: largest |error| over all jumps. Terminal: ground speed over the 1 s before the last release (– when that window is not all ground).

| condition | trial | steps | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ (u/s) | takeoff | land | slide start | slide end | apex err (u) | takeoff vz err (u/s) | M1 pos RMS 3D (before) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e3_back_k12_144fps | [M3_e3_back_k12_144fps_r639](M3_e3_back_k12_144fps_r639/report.md) | 431 | 0.159 | 0.287 | 0.156 | 0.285 | 0.190 | 0.568 | – | 0 (1) | 0 (1) | – | – | +0.031 | +0.016 | – |
| e3_back_k12_144fps | [M3_e3_back_k12_144fps_r640](M3_e3_back_k12_144fps_r640/report.md) | 431 | 0.126 | 0.240 | 0.125 | 0.238 | 0.164 | 0.516 | – | 0 (1) | 0 (1) | – | – | +0.032 | +0.020 | – |
| e3_right_k15_60fps | [M3_e3_right_k15_60fps_r1107](M3_e3_right_k15_60fps_r1107/report.md) | 190 | 8.780 | 16.950 | 8.780 | 16.950 | 27.462 | 201.553 | – | 0 (1) | 0 (1) | – | – | +0.062 | +0.014 | – |
| e3_right_k1_144fps | [M3_e3_right_k1_144fps_r601](M3_e3_right_k1_144fps_r601/report.md) | 420 | 5.916 | 13.170 | 5.916 | 13.170 | 24.125 | 185.283 | – | 0 (1) | 0 (1) | – | – | +0.045 | +0.001 | – |
| e3_right_k1_144fps | [M3_e3_right_k1_144fps_r602](M3_e3_right_k1_144fps_r602/report.md) | 420 | 5.882 | 13.088 | 5.882 | 13.088 | 23.895 | 184.154 | – | 0 (1) | 0 (1) | – | – | +0.046 | +0.008 | – |
| e3_right_k1_60fps | [M3_e3_right_k1_60fps_r1101](M3_e3_right_k1_60fps_r1101/report.md) | 176 | 5.789 | 12.535 | 5.788 | 12.535 | 22.984 | 171.687 | – | 0 (1) | 0 (1) | – | – | +0.047 | +0.013 | – |
| e3_right_k21_120fps | [M3_e3_right_k21_120fps_r964](M3_e3_right_k21_120fps_r964/report.md) | 369 | 6.542 | 13.151 | 6.542 | 13.151 | 23.159 | 182.147 | – | 0 (1) | 0 (1) | – | – | +0.063 | +0.035 | – |
| e3_right_k25_60fps | [M3_e3_right_k25_60fps_r1112](M3_e3_right_k25_60fps_r1112/report.md) | 200 | 23.773 | 44.048 | 23.773 | 44.048 | 55.317 | 345.040 | – | 0 (1) | 0 (1) | – | – | +0.065 | +0.023 | – |
| e3_right_k35_144fps | [M3_e3_right_k35_144fps_r617](M3_e3_right_k35_144fps_r617/report.md) | 454 | 8.426 | 16.539 | 8.426 | 16.539 | 27.028 | 206.628 | – | 0 (1) | 0 (1) | – | – | +0.062 | +0.013 | – |
| e3_right_k35_144fps | [M3_e3_right_k35_144fps_r618](M3_e3_right_k35_144fps_r618/report.md) | 454 | 8.536 | 16.771 | 8.536 | 16.771 | 27.445 | 207.539 | – | 0 (1) | 0 (1) | – | – | +0.061 | +0.001 | – |
| e3_right_k42_120fps | [M3_e3_right_k42_120fps_r1029](M3_e3_right_k42_120fps_r1029/report.md) | 391 | 17.503 | 33.453 | 17.503 | 33.453 | 45.393 | 299.296 | – | 0 (1) | 0 (1) | – | – | +0.065 | +0.018 | – |
| e3_right_k50_144fps | [M3_e3_right_k50_144fps_r623](M3_e3_right_k50_144fps_r623/report.md) | 469 | 16.884 | 32.331 | 16.884 | 32.331 | 44.178 | 294.008 | – | 0 (1) | 0 (1) | – | – | +0.064 | +0.018 | – |
| e3_right_k50_144fps | [M3_e3_right_k50_144fps_r624](M3_e3_right_k50_144fps_r624/report.md) | 469 | 17.261 | 33.040 | 17.261 | 33.040 | 44.307 | 295.540 | – | 0 (1) | 0 (1) | – | – | +0.062 | +0.003 | – |
| e3_right_k58_120fps | [M3_e3_right_k58_120fps_r1033](M3_e3_right_k58_120fps_r1033/report.md) | 406 | 25.229 | 46.153 | 25.229 | 46.153 | 57.722 | 365.861 | – | 0 (1) | 0 (1) | – | – | +0.065 | +0.020 | – |
| e3_right_k60_144fps | [M3_e3_right_k60_144fps_r627](M3_e3_right_k60_144fps_r627/report.md) | 479 | 24.228 | 45.541 | 24.228 | 45.541 | 56.295 | 357.056 | – | 0 (1) | 0 (1) | – | – | +0.064 | +0.022 | – |
| e3_right_k60_144fps | [M3_e3_right_k60_144fps_r628](M3_e3_right_k60_144fps_r628/report.md) | 478 | 24.055 | 45.162 | 24.055 | 45.162 | 55.946 | 354.495 | – | 0 (1) | 0 (1) | – | – | +0.062 | +0.001 | – |
| e3_right_slide350_k5_144fps | [M3_e3_right_slide350_k5_144fps_r650](M3_e3_right_slide350_k5_144fps_r650/report.md) | 654 | 7.260 | 16.955 | 4.035 | 8.627 | 35.709 | 277.190 | – | 0 (1) | +10 (1) | 0 (1) | 0 (1) | +16.629 | +0.252 | – |
| e3_right_slide350_k5_144fps | [M3_e3_right_slide350_k5_144fps_r651](M3_e3_right_slide350_k5_144fps_r651/report.md) | 654 | 7.049 | 16.661 | 3.697 | 9.540 | 35.728 | 277.151 | – | 0 (1) | +10 (1) | 0 (1) | 0 (1) | +16.633 | +0.277 | – |
| e3_right_walk_k5_144fps | [M3_e3_right_walk_k5_144fps_r647](M3_e3_right_walk_k5_144fps_r647/report.md) | 424 | 0.996 | 2.082 | 0.996 | 2.082 | 6.788 | 76.198 | – | 0 (1) | 0 (1) | – | – | +0.059 | -0.008 | – |
| e3_right_walk_k5_144fps | [M3_e3_right_walk_k5_144fps_r648](M3_e3_right_walk_k5_144fps_r648/report.md) | 424 | 1.018 | 2.141 | 1.018 | 2.141 | 6.791 | 76.199 | – | 0 (1) | 0 (1) | – | – | +0.060 | -0.006 | – |
| e3_wtap_k12_144fps | [M3_e3_wtap_k12_144fps_r641](M3_e3_wtap_k12_144fps_r641/report.md) | 432 | 0.313 | 0.495 | 0.312 | 0.495 | 0.149 | 0.286 | – | 0 (1) | 0 (1) | – | – | +0.008 | +0.013 | – |
| e3_wtap_k12_144fps | [M3_e3_wtap_k12_144fps_r642](M3_e3_wtap_k12_144fps_r642/report.md) | 431 | 0.203 | 0.339 | 0.202 | 0.339 | 0.124 | 0.301 | – | 0 (1) | 0 (1) | – | – | +0.007 | +0.007 | – |
| e8_fast_hops_120fps | [M3_e8_fast_hops_120fps_r943](M3_e8_fast_hops_120fps_r943/report.md) | 861 | 4.862 | 16.371 | 1.481 | 2.385 | 23.465 | 265.485 | – | 0 (4) | +8 (4) | 0 (1) | 0 (1) | +16.667 | +0.348 | – |
| e8_fast_hops_120fps | [M3_e8_fast_hops_120fps_r944](M3_e8_fast_hops_120fps_r944/report.md) | 861 | 4.928 | 16.278 | 1.694 | 2.700 | 23.473 | 265.595 | – | 0 (4) | +8 (4) | 0 (1) | 0 (1) | +16.669 | +0.332 | – |
| e8_hop350_d0_120fps | [M3_e8_hop350_d0_120fps_r1236](M3_e8_hop350_d0_120fps_r1236/report.md) | 694 | 8.168 | 21.259 | 2.654 | 4.560 | 62.209 | 374.390 | – | +50 (4/2) | +67 (4/2) | 0 (1) | 0 (1) | +16.666 | +54.069 | – |
| e8_hop350_d0_120fps | [M3_e8_hop350_d0_120fps_r1237](M3_e8_hop350_d0_120fps_r1237/report.md) | 695 | 8.067 | 20.382 | 2.501 | 4.526 | 61.704 | 375.731 | – | +49 (4/2) | +66 (4/2) | 0 (1) | 0 (1) | +16.664 | +52.966 | – |
| e8_hop350_d3_120fps | [M3_e8_hop350_d3_120fps_r1245](M3_e8_hop350_d3_120fps_r1245/report.md) | 702 | 8.292 | 25.972 | 1.578 | 3.031 | 61.858 | 394.371 | – | +52 (4/2) | +73 (4/2) | 0 (1) | 0 (1) | +16.667 | +64.212 | – |
| e8_hop350_d3_120fps | [M3_e8_hop350_d3_120fps_r1246](M3_e8_hop350_d3_120fps_r1246/report.md) | 702 | 8.268 | 25.951 | 1.456 | 2.824 | 61.859 | 394.452 | – | +52 (4/2) | +73 (4/2) | 0 (1) | 0 (1) | +16.666 | +64.202 | – |
| e8_slide_chain_120fps | [M3_e8_slide_chain_120fps_r1015](M3_e8_slide_chain_120fps_r1015/report.md) | 796 | 2.521 | 6.598 | 2.461 | 6.566 | 7.490 | 66.298 | – | 0 (2) | 0 (2) | 0 (3) | +6 (3) | +0.166 | +0.335 | – |
| e8_slide_chain_120fps | [M3_e8_slide_chain_120fps_r1016](M3_e8_slide_chain_120fps_r1016/report.md) | 796 | 2.462 | 6.457 | 2.400 | 6.425 | 7.488 | 66.305 | – | 0 (2) | 0 (2) | 0 (3) | +6 (3) | +0.166 | +0.338 | – |

## 2. Per condition (R5MotorV2; RMS = mean of the trials, max = worst trial)

| condition | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ | worst event Δ (steps) | apex err | takeoff vz err | M1 pos RMS 3D | M1 vel RMS 3D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e3_back_k12_144fps | 2 | 0.142 | 0.287 | 0.141 | 0.285 | 0.177 | 0.568 | – | 0 | +0.032 | +0.020 | – | – |
| e3_right_k15_60fps | 1 | 8.780 | 16.950 | 8.780 | 16.950 | 27.462 | 201.553 | – | 0 | +0.062 | +0.014 | – | – |
| e3_right_k1_144fps | 2 | 5.899 | 13.170 | 5.899 | 13.170 | 24.010 | 185.283 | – | 0 | +0.046 | +0.008 | – | – |
| e3_right_k1_60fps | 1 | 5.789 | 12.535 | 5.788 | 12.535 | 22.984 | 171.687 | – | 0 | +0.047 | +0.013 | – | – |
| e3_right_k21_120fps | 1 | 6.542 | 13.151 | 6.542 | 13.151 | 23.159 | 182.147 | – | 0 | +0.063 | +0.035 | – | – |
| e3_right_k25_60fps | 1 | 23.773 | 44.048 | 23.773 | 44.048 | 55.317 | 345.040 | – | 0 | +0.065 | +0.023 | – | – |
| e3_right_k35_144fps | 2 | 8.481 | 16.771 | 8.481 | 16.771 | 27.237 | 207.539 | – | 0 | +0.062 | +0.013 | – | – |
| e3_right_k42_120fps | 1 | 17.503 | 33.453 | 17.503 | 33.453 | 45.393 | 299.296 | – | 0 | +0.065 | +0.018 | – | – |
| e3_right_k50_144fps | 2 | 17.072 | 33.040 | 17.072 | 33.040 | 44.242 | 295.540 | – | 0 | +0.064 | +0.018 | – | – |
| e3_right_k58_120fps | 1 | 25.229 | 46.153 | 25.229 | 46.153 | 57.722 | 365.861 | – | 0 | +0.065 | +0.020 | – | – |
| e3_right_k60_144fps | 2 | 24.142 | 45.541 | 24.142 | 45.541 | 56.120 | 357.056 | – | 0 | +0.064 | +0.022 | – | – |
| e3_right_slide350_k5_144fps | 2 | 7.155 | 16.955 | 3.866 | 9.540 | 35.719 | 277.190 | – | +10 | +16.633 | +0.277 | – | – |
| e3_right_walk_k5_144fps | 2 | 1.007 | 2.141 | 1.007 | 2.141 | 6.790 | 76.199 | – | 0 | +0.060 | -0.008 | – | – |
| e3_wtap_k12_144fps | 2 | 0.258 | 0.495 | 0.257 | 0.495 | 0.136 | 0.301 | – | 0 | +0.008 | +0.013 | – | – |
| e8_fast_hops_120fps | 2 | 4.895 | 16.371 | 1.587 | 2.700 | 23.469 | 265.595 | – | +8 | +16.669 | +0.348 | – | – |
| e8_hop350_d0_120fps | 2 | 8.118 | 21.259 | 2.578 | 4.560 | 61.957 | 375.731 | – | +67 (count mismatch) | +16.666 | +54.069 | – | – |
| e8_hop350_d3_120fps | 2 | 8.280 | 25.972 | 1.517 | 3.031 | 61.859 | 394.452 | – | +73 (count mismatch) | +16.667 | +64.212 | – | – |
| e8_slide_chain_120fps | 2 | 2.491 | 6.598 | 2.430 | 6.566 | 7.489 | 66.305 | – | +6 | +0.166 | +0.338 | – | – |

## 3. Ground mapping: terminal speed and accel/decel, Unity motor vs R5

Same estimator on both series (ReplayMetrics.Ground: GROUND-MODEL §1 — band by nearest nominal rate, rate = ΣΔs/Σdt, decel excludes the zeroing step). Unity spread = (max − min)/mean over the condition's trials (plan acceptance: terminal ≤ 2 %, accel/decel ≤ 5 %); Unity vs R5 = (sim mean − ref mean)/ref mean.

| condition | quantity | R5 per trial | Unity per trial | R5 mean | Unity mean | Unity vs R5 | R5 spread | Unity spread | acceptance (Unity spread) |
|---|---|---|---|---|---|---|---|---|---|
| e3_back_k12_144fps | accel_low (u/s²) | 2875.862 / 2875.371 | 2875.000 / 2875.000 | 2875.616 | 2875.000 | -0.021 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e3_back_k12_144fps | accel_mid (u/s²) | 517.725 / 517.667 | 517.500 / 517.500 | 517.696 | 517.500 | -0.038 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_back_k12_144fps | accel_sprint (u/s²) | 115.053 / 115.037 | 115.000 / 115.000 | 115.045 | 115.000 | -0.039 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_back_k12_144fps | decel_stand (u/s²) | 1249.483 / 1250.036 | 1250.000 / 1250.000 | 1249.759 | 1250.000 | +0.019 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k15_60fps | accel_low (u/s²) | 2874.930 | 2875.000 | 2874.930 | 2875.000 | +0.002 % | – | – | n/a (1 trial) |
| e3_right_k15_60fps | accel_mid (u/s²) | 506.371 | 517.500 | 506.371 | 517.500 | +2.198 % | – | – | n/a (1 trial) |
| e3_right_k15_60fps | accel_sprint (u/s²) | 118.354 | 115.000 | 118.354 | 115.000 | -2.834 % | – | – | n/a (1 trial) |
| e3_right_k15_60fps | decel_stand (u/s²) | 1249.987 | 1250.000 | 1249.987 | 1250.000 | +0.001 % | – | – | n/a (1 trial) |
| e3_right_k1_144fps | accel_low (u/s²) | 2874.939 / 2875.319 | 2875.000 / 2875.000 | 2875.129 | 2875.000 | -0.004 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k1_144fps | accel_mid (u/s²) | 504.153 / 496.874 | 517.500 / 517.500 | 500.514 | 517.500 | +3.394 % | 1.45 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k1_144fps | accel_sprint (u/s²) | 117.330 / 116.236 | 115.000 / 115.000 | 116.783 | 115.000 | -1.527 % | 0.94 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k1_144fps | decel_stand (u/s²) | 1249.899 / 1249.898 | 1250.000 / 1250.000 | 1249.899 | 1250.000 | +0.008 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k1_60fps | accel_low (u/s²) | 2875.315 | 2875.000 | 2875.315 | 2875.000 | -0.011 % | – | – | n/a (1 trial) |
| e3_right_k1_60fps | accel_mid (u/s²) | 491.766 | 517.500 | 491.766 | 517.500 | +5.233 % | – | – | n/a (1 trial) |
| e3_right_k1_60fps | accel_sprint (u/s²) | 116.105 | 115.000 | 116.105 | 115.000 | -0.952 % | – | – | n/a (1 trial) |
| e3_right_k1_60fps | decel_stand (u/s²) | 1250.003 | 1250.000 | 1250.003 | 1250.000 | 0.000 % | – | – | n/a (1 trial) |
| e3_right_k21_120fps | accel_low (u/s²) | 2879.558 | 2875.000 | 2879.558 | 2875.000 | -0.158 % | – | – | n/a (1 trial) |
| e3_right_k21_120fps | accel_mid (u/s²) | 503.602 | 517.500 | 503.602 | 517.500 | +2.760 % | – | – | n/a (1 trial) |
| e3_right_k21_120fps | accel_sprint (u/s²) | 117.571 | 115.000 | 117.571 | 115.000 | -2.187 % | – | – | n/a (1 trial) |
| e3_right_k21_120fps | decel_stand (u/s²) | 1249.377 | 1250.000 | 1249.377 | 1250.000 | +0.050 % | – | – | n/a (1 trial) |
| e3_right_k25_60fps | accel_low (u/s²) | 2875.045 | 2875.000 | 2875.045 | 2875.000 | -0.002 % | – | – | n/a (1 trial) |
| e3_right_k25_60fps | accel_mid (u/s²) | 548.482 | 517.500 | 548.482 | 517.500 | -5.649 % | – | – | n/a (1 trial) |
| e3_right_k25_60fps | accel_sprint (u/s²) | 114.567 | 115.000 | 114.567 | 115.000 | +0.378 % | – | – | n/a (1 trial) |
| e3_right_k25_60fps | decel_stand (u/s²) | 1249.947 | 1250.000 | 1249.947 | 1250.000 | +0.004 % | – | – | n/a (1 trial) |
| e3_right_k35_144fps | accel_low (u/s²) | 2875.364 / 2875.164 | 2875.000 / 2875.000 | 2875.264 | 2875.000 | -0.009 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k35_144fps | accel_mid (u/s²) | 503.732 / 499.376 | 517.500 / 517.500 | 501.554 | 517.500 | +3.179 % | 0.87 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k35_144fps | accel_sprint (u/s²) | 117.621 / 116.859 | 115.000 / 115.000 | 117.240 | 115.000 | -1.911 % | 0.65 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k35_144fps | decel_stand (u/s²) | 1250.298 / 1249.817 | 1250.000 / 1250.000 | 1250.057 | 1250.000 | -0.005 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k42_120fps | accel_low (u/s²) | 2878.816 | 2875.000 | 2878.816 | 2875.000 | -0.133 % | – | – | n/a (1 trial) |
| e3_right_k42_120fps | accel_mid (u/s²) | 504.195 | 517.500 | 504.195 | 517.500 | +2.639 % | – | – | n/a (1 trial) |
| e3_right_k42_120fps | accel_sprint (u/s²) | 115.372 | 117.300 | 115.372 | 117.300 | +1.671 % | – | – | n/a (1 trial) |
| e3_right_k42_120fps | decel_stand (u/s²) | 1251.226 | 1250.000 | 1251.226 | 1250.000 | -0.098 % | – | – | n/a (1 trial) |
| e3_right_k50_144fps | accel_low (u/s²) | 2874.075 / 2875.026 | 2875.000 / 2875.000 | 2874.550 | 2875.000 | +0.016 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k50_144fps | accel_mid (u/s²) | 509.828 / 509.319 | 517.500 / 517.500 | 509.573 | 517.500 | +1.556 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k50_144fps | accel_sprint (u/s²) | 117.237 / 117.061 | 115.000 / 115.000 | 117.149 | 115.000 | -1.835 % | 0.15 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k50_144fps | decel_stand (u/s²) | 1250.197 / 1250.479 | 1250.000 / 1250.000 | 1250.338 | 1250.000 | -0.027 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k58_120fps | accel_low (u/s²) | 2876.915 | 2875.000 | 2876.915 | 2875.000 | -0.067 % | – | – | n/a (1 trial) |
| e3_right_k58_120fps | accel_mid (u/s²) | 542.680 | 517.500 | 542.680 | 517.500 | -4.640 % | – | – | n/a (1 trial) |
| e3_right_k58_120fps | accel_sprint (u/s²) | 115.311 | 117.300 | 115.311 | 117.300 | +1.725 % | – | – | n/a (1 trial) |
| e3_right_k58_120fps | decel_stand (u/s²) | 1251.466 | 1250.000 | 1251.466 | 1250.000 | -0.117 % | – | – | n/a (1 trial) |
| e3_right_k60_144fps | accel_low (u/s²) | 2875.380 / 2876.296 | 2875.000 / 2875.000 | 2875.838 | 2875.000 | -0.029 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k60_144fps | accel_mid (u/s²) | 533.123 / 535.256 | 517.500 / 517.500 | 534.190 | 517.500 | -3.124 % | 0.40 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k60_144fps | accel_sprint (u/s²) | 116.099 / 116.537 | 115.000 / 115.000 | 116.318 | 115.000 | -1.133 % | 0.38 % | 0.00 % | pass (≤ 5 %) |
| e3_right_k60_144fps | decel_stand (u/s²) | 1250.732 / 1250.936 | 1250.000 / 1250.000 | 1250.834 | 1250.000 | -0.067 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e3_right_slide350_k5_144fps | accel_low (u/s²) | 2877.268 / 2877.357 | 2875.000 / 2875.000 | 2877.312 | 2875.000 | -0.080 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e3_right_slide350_k5_144fps | accel_mid (u/s²) | 497.873 / 501.206 | 517.500 / 517.500 | 499.539 | 517.500 | +3.595 % | 0.67 % | 0.00 % | pass (≤ 5 %) |
| e3_right_slide350_k5_144fps | accel_sprint (u/s²) | 116.029 / 116.675 | 115.000 / 115.000 | 116.352 | 115.000 | -1.162 % | 0.55 % | 0.00 % | pass (≤ 5 %) |
| e3_right_slide350_k5_144fps | decel_stand (u/s²) | 1247.976 / 1250.174 | 1250.000 / 1250.000 | 1249.075 | 1250.000 | +0.074 % | 0.18 % | 0.00 % | pass (≤ 5 %) |
| e3_right_walk_k5_144fps | accel_low (u/s²) | 2873.134 / 2869.760 | 2875.000 / 2875.000 | 2871.447 | 2875.000 | +0.124 % | 0.12 % | 0.00 % | pass (≤ 5 %) |
| e3_right_walk_k5_144fps | accel_mid (u/s²) | 516.660 / 516.801 | 517.500 / 517.500 | 516.731 | 517.500 | +0.149 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e3_right_walk_k5_144fps | accel_sprint (u/s²) | 158.042 / 158.021 | – / – | 158.031 | – | – | 0.01 % | – | n/a (1 trial) |
| e3_right_walk_k5_144fps | decel_stand (u/s²) | 1249.466 / 1248.975 | 1250.000 / 1250.000 | 1249.220 | 1250.000 | +0.062 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e3_wtap_k12_144fps | accel_low (u/s²) | 2876.695 / 2876.379 | 2875.000 / 2875.000 | 2876.537 | 2875.000 | -0.053 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_wtap_k12_144fps | accel_mid (u/s²) | 517.648 / 517.690 | 517.500 / 517.500 | 517.669 | 517.500 | -0.033 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e3_wtap_k12_144fps | accel_sprint (u/s²) | 115.061 / 115.009 | 115.000 / 115.000 | 115.035 | 115.000 | -0.030 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| e3_wtap_k12_144fps | decel_stand (u/s²) | 1249.771 / 1249.605 | 1250.000 / 1250.000 | 1249.688 | 1250.000 | +0.025 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e8_fast_hops_120fps | accel_low (u/s²) | 2876.515 / 2873.159 | 2875.000 / 2875.000 | 2874.837 | 2875.000 | +0.006 % | 0.12 % | 0.00 % | pass (≤ 5 %) |
| e8_fast_hops_120fps | accel_mid (u/s²) | 517.775 / 518.140 | 517.500 / 517.500 | 517.957 | 517.500 | -0.088 % | 0.07 % | 0.00 % | pass (≤ 5 %) |
| e8_fast_hops_120fps | accel_sprint (u/s²) | 114.988 / 115.080 | 115.000 / 115.000 | 115.034 | 115.000 | -0.029 % | 0.08 % | 0.00 % | pass (≤ 5 %) |
| e8_fast_hops_120fps | decel_stand (u/s²) | 1249.389 / 1249.113 | 1250.000 / 1250.000 | 1249.251 | 1250.000 | +0.060 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d0_120fps | accel_low (u/s²) | 2877.275 / 2877.135 | 2875.000 / 2875.000 | 2877.205 | 2875.000 | -0.077 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d0_120fps | accel_mid (u/s²) | 517.967 / 517.821 | 517.500 / 517.500 | 517.894 | 517.500 | -0.076 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d0_120fps | accel_sprint (u/s²) | 115.051 / 115.079 | 117.300 / 117.300 | 115.065 | 117.300 | +1.943 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d0_120fps | decel_stand (u/s²) | 1250.282 / 1251.118 | 1250.000 / 1250.000 | 1250.700 | 1250.000 | -0.056 % | 0.07 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d3_120fps | accel_low (u/s²) | 2879.656 / 2877.415 | 2875.000 / 2875.000 | 2878.536 | 2875.000 | -0.123 % | 0.08 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d3_120fps | accel_mid (u/s²) | 518.122 / 517.985 | 517.500 / 517.500 | 518.054 | 517.500 | -0.107 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d3_120fps | accel_sprint (u/s²) | 115.055 / 115.128 | 117.300 / 117.300 | 115.091 | 117.300 | +1.919 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e8_hop350_d3_120fps | decel_stand (u/s²) | 1250.743 / 1251.138 | 1250.000 / 1250.000 | 1250.941 | 1250.000 | -0.075 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e8_slide_chain_120fps | accel_low (u/s²) | 2876.035 / 2876.860 | 2875.000 / 2875.000 | 2876.448 | 2875.000 | -0.050 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e8_slide_chain_120fps | accel_mid (u/s²) | 517.554 / 517.740 | 517.500 / 517.500 | 517.647 | 517.500 | -0.028 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e8_slide_chain_120fps | accel_sprint (u/s²) | 115.050 / 115.009 | 117.300 / 117.300 | 115.029 | 117.300 | +1.974 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e8_slide_chain_120fps | decel_stand (u/s²) | 1250.687 / 1250.917 | 1250.000 / 1250.000 | 1250.802 | 1250.000 | -0.064 % | 0.02 % | 0.00 % | pass (≤ 5 %) |

## 4. Flags (R5MotorV2 vs reference columns; steps that differ)

| trial | grounded | sliding | sprinting | maxspeed (n compared) |
|---|---|---|---|---|
| M3_e3_back_k12_144fps_r639 | 0 | 0 | 0 | 0 (431) |
| M3_e3_back_k12_144fps_r640 | 0 | 0 | 0 | 0 (431) |
| M3_e3_right_k15_60fps_r1107 | 0 | 0 | 0 | 0 (190) |
| M3_e3_right_k1_144fps_r601 | 0 | 0 | 0 | 0 (420) |
| M3_e3_right_k1_144fps_r602 | 0 | 0 | 0 | 0 (420) |
| M3_e3_right_k1_60fps_r1101 | 0 | 0 | 0 | 0 (176) |
| M3_e3_right_k21_120fps_r964 | 0 | 0 | 0 | 0 (369) |
| M3_e3_right_k25_60fps_r1112 | 0 | 0 | 0 | 0 (200) |
| M3_e3_right_k35_144fps_r617 | 0 | 0 | 0 | 0 (454) |
| M3_e3_right_k35_144fps_r618 | 0 | 0 | 0 | 0 (454) |
| M3_e3_right_k42_120fps_r1029 | 0 | 0 | 0 | 0 (391) |
| M3_e3_right_k50_144fps_r623 | 0 | 0 | 0 | 0 (469) |
| M3_e3_right_k50_144fps_r624 | 0 | 0 | 0 | 0 (469) |
| M3_e3_right_k58_120fps_r1033 | 0 | 0 | 0 | 0 (406) |
| M3_e3_right_k60_144fps_r627 | 0 | 0 | 0 | 0 (479) |
| M3_e3_right_k60_144fps_r628 | 0 | 0 | 0 | 0 (478) |
| M3_e3_right_slide350_k5_144fps_r650 | 10 | 0 | 0 | 5 (654) |
| M3_e3_right_slide350_k5_144fps_r651 | 10 | 0 | 0 | 6 (654) |
| M3_e3_right_walk_k5_144fps_r647 | 0 | 0 | 0 | 0 (424) |
| M3_e3_right_walk_k5_144fps_r648 | 0 | 0 | 0 | 0 (424) |
| M3_e3_wtap_k12_144fps_r641 | 0 | 0 | 0 | 0 (432) |
| M3_e3_wtap_k12_144fps_r642 | 0 | 0 | 0 | 0 (431) |
| M3_e8_fast_hops_120fps_r943 | 8 | 0 | 8 | 17 (861) |
| M3_e8_fast_hops_120fps_r944 | 8 | 0 | 8 | 17 (861) |
| M3_e8_hop350_d0_120fps_r1236 | 76 | 0 | 76 | 85 (694) |
| M3_e8_hop350_d0_120fps_r1237 | 77 | 0 | 77 | 86 (695) |
| M3_e8_hop350_d3_120fps_r1245 | 83 | 0 | 83 | 92 (702) |
| M3_e8_hop350_d3_120fps_r1246 | 83 | 0 | 83 | 92 (702) |
| M3_e8_slide_chain_120fps_r1015 | 0 | 6 | 0 | 0 (796) |
| M3_e8_slide_chain_120fps_r1016 | 0 | 6 | 0 | 0 (796) |

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

