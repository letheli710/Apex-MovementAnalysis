# R5 replay — M2 Unity motor (R5MotorV2) vs R5 trials

Generated 2026-10-21 01:32 UTC by Unity 6000.6.5f1. Models: `R5MotorV2/m2` (after) and `ReferenceMotor/m1-first-guess` (before, M1 first guess, reports in `m1_first_guess/`). Errors are sim − ref in Source units (u, u/s), per step aligned by usercmd. Open-loop replay from initial_state with the recorded inputs; nothing is tuned per trial.

## 1. Per trial (R5MotorV2)

Event cells: largest step delta sim − ref over all paired events (count ref/sim). Apex / takeoff vz: largest |error| over all jumps. Terminal: ground speed over the 1 s before the last release (– when that window is not all ground).

| condition | trial | steps | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ (u/s) | takeoff | land | slide start | slide end | apex err (u) | takeoff vz err (u/s) | M1 pos RMS 3D (before) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e1_walk | [M2_e1_walk_r301](M2_e1_walk_r301/report.md) | 792 | 0.031 | 0.043 | 0.030 | 0.041 | 0.002 | 0.014 | 0.000 | – | – | – | – | – | – | [32.121](m1_first_guess/M2_e1_walk_r301/report.md) |
| e1_walk | [M2_e1_walk_r302](M2_e1_walk_r302/report.md) | 792 | 0.019 | 0.029 | 0.017 | 0.024 | 0.003 | 0.025 | 0.000 | – | – | – | – | – | – | [32.005](m1_first_guess/M2_e1_walk_r302/report.md) |
| e1_sprint | [M2_e1_sprint_r306](M2_e1_sprint_r306/report.md) | 792 | 0.090 | 0.120 | 0.090 | 0.120 | 0.012 | 0.037 | 0.000 | – | – | – | – | – | – | [210.986](m1_first_guess/M2_e1_sprint_r306/report.md) |
| e1_sprint | [M2_e1_sprint_r307](M2_e1_sprint_r307/report.md) | 792 | 0.026 | 0.046 | 0.025 | 0.044 | 0.018 | 0.063 | 0.000 | – | – | – | – | – | – | [210.893](m1_first_guess/M2_e1_sprint_r307/report.md) |
| e1_crouch | [M2_e1_crouch_r311](M2_e1_crouch_r311/report.md) | 1007 | 0.027 | 0.040 | 0.026 | 0.037 | 0.002 | 0.026 | 0.000 | – | – | – | – | – | – | [201.148](m1_first_guess/M2_e1_crouch_r311/report.md) |
| e1_crouch | [M2_e1_crouch_r312](M2_e1_crouch_r312/report.md) | 1008 | 0.023 | 0.036 | 0.022 | 0.032 | 0.004 | 0.057 | 0.000 | – | – | – | – | – | – | [201.200](m1_first_guess/M2_e1_crouch_r312/report.md) |
| e1_back | [M2_e1_back_r316](M2_e1_back_r316/report.md) | 792 | 0.176 | 0.232 | 0.176 | 0.232 | 0.015 | 0.092 | 0.000 | – | – | – | – | – | – | [32.163](m1_first_guess/M2_e1_back_r316/report.md) |
| e1_back | [M2_e1_back_r317](M2_e1_back_r317/report.md) | 792 | 0.119 | 0.157 | 0.119 | 0.156 | 0.015 | 0.109 | 0.000 | – | – | – | – | – | – | [32.144](m1_first_guess/M2_e1_back_r317/report.md) |
| e1_side | [M2_e1_side_r321](M2_e1_side_r321/report.md) | 791 | 0.181 | 0.248 | 0.181 | 0.248 | 0.011 | 0.083 | 0.000 | – | – | – | – | – | – | [32.303](m1_first_guess/M2_e1_side_r321/report.md) |
| e1_side | [M2_e1_side_r322](M2_e1_side_r322/report.md) | 792 | 0.121 | 0.162 | 0.121 | 0.162 | 0.012 | 0.077 | 0.000 | – | – | – | – | – | – | [32.234](m1_first_guess/M2_e1_side_r322/report.md) |
| e1_diag | [M2_e1_diag_r326](M2_e1_diag_r326/report.md) | 792 | 0.142 | 0.193 | 0.142 | 0.192 | 0.014 | 0.091 | 0.000 | – | – | – | – | – | – | [32.248](m1_first_guess/M2_e1_diag_r326/report.md) |
| e1_diag | [M2_e1_diag_r327](M2_e1_diag_r327/report.md) | 792 | 0.132 | 0.186 | 0.132 | 0.186 | 0.017 | 0.112 | 0.000 | – | – | – | – | – | – | [32.263](m1_first_guess/M2_e1_diag_r327/report.md) |
| e1_turn | [M2_e1_turn_r331](M2_e1_turn_r331/report.md) | 936 | 0.739 | 0.967 | 0.739 | 0.966 | 0.136 | 0.405 | 0.000 | – | – | – | – | – | – | [155.700](m1_first_guess/M2_e1_turn_r331/report.md) |
| e1_turn | [M2_e1_turn_r332](M2_e1_turn_r332/report.md) | 936 | 0.576 | 0.787 | 0.576 | 0.787 | 0.074 | 0.462 | 0.000 | – | – | – | – | – | – | [154.602](m1_first_guess/M2_e1_turn_r332/report.md) |
| e2_strafe | [M2_e2_strafe_r336](M2_e2_strafe_r336/report.md) | 753 | 80.756 | 125.475 | 80.756 | 125.475 | 60.249 | 209.277 | – | 0 (1) | 0 (1) | – | – | +0.028 | -0.010 | [154.438](m1_first_guess/M2_e2_strafe_r336/report.md) |
| e2_strafe | [M2_e2_strafe_r337](M2_e2_strafe_r337/report.md) | 753 | 80.721 | 125.453 | 80.721 | 125.453 | 60.368 | 209.288 | – | 0 (1) | 0 (1) | – | – | +0.031 | +0.011 | [153.609](m1_first_guess/M2_e2_strafe_r337/report.md) |
| e2_noinput | [M2_e2_noinput_r341](M2_e2_noinput_r341/report.md) | 653 | 0.445 | 0.657 | 0.445 | 0.645 | 0.103 | 0.404 | – | 0 (1) | 0 (1) | – | – | +0.013 | +0.007 | [179.824](m1_first_guess/M2_e2_noinput_r341/report.md) |
| e2_noinput | [M2_e2_noinput_r342](M2_e2_noinput_r342/report.md) | 653 | 0.569 | 0.810 | 0.569 | 0.809 | 0.170 | 0.518 | – | 0 (1) | 0 (1) | – | – | +0.010 | -0.012 | [182.197](m1_first_guess/M2_e2_noinput_r342/report.md) |
| e2_keepfwd | [M2_e2_keepfwd_r346](M2_e2_keepfwd_r346/report.md) | 793 | 0.540 | 0.834 | 0.539 | 0.833 | 0.152 | 0.644 | 0.000 | 0 (1) | 0 (1) | – | – | +0.062 | +0.007 | [248.875](m1_first_guess/M2_e2_keepfwd_r346/report.md) |
| e2_keepfwd | [M2_e2_keepfwd_r347](M2_e2_keepfwd_r347/report.md) | 793 | 0.751 | 1.137 | 0.751 | 1.137 | 0.128 | 0.540 | 0.000 | 0 (1) | 0 (1) | – | – | +0.061 | +0.002 | [245.717](m1_first_guess/M2_e2_keepfwd_r347/report.md) |
| e4_stand | [M2_e4_stand_r351](M2_e4_stand_r351/report.md) | 361 | 0.590 | 1.739 | 0.000 | 0.000 | 14.728 | 278.931 | – | 0 (1) | +1 (1) | – | – | +0.979 | -0.015 | [1.241](m1_first_guess/M2_e4_stand_r351/report.md) |
| e4_stand | [M2_e4_stand_r352](M2_e4_stand_r352/report.md) | 361 | 1.098 | 3.299 | 0.000 | 0.000 | 20.811 | 280.502 | – | 0 (1) | +2 (1) | – | – | +1.795 | -0.016 | [1.733](m1_first_guess/M2_e4_stand_r352/report.md) |
| e4_hop0 | [M2_e4_hop0_r356](M2_e4_hop0_r356/report.md) | 982 | 1.248 | 1.734 | 1.248 | 1.734 | 0.186 | 0.561 | – | 0 (5) | 0 (5) | – | – | +0.064 | +0.125 | [310.301](m1_first_guess/M2_e4_hop0_r356/report.md) |
| e4_hop0 | [M2_e4_hop0_r357](M2_e4_hop0_r357/report.md) | 983 | 0.972 | 1.325 | 0.972 | 1.325 | 0.180 | 0.531 | – | 0 (5) | 0 (5) | – | – | +0.062 | +0.111 | [310.935](m1_first_guess/M2_e4_hop0_r357/report.md) |
| e4_hop3 | [M2_e4_hop3_r261](M2_e4_hop3_r261/report.md) | 995 | 0.893 | 1.309 | 0.893 | 1.309 | 0.121 | 0.680 | – | 0 (5) | 0 (5) | – | – | +0.073 | +0.153 | [314.047](m1_first_guess/M2_e4_hop3_r261/report.md) |
| e4_hop3 | [M2_e4_hop3_r262](M2_e4_hop3_r262/report.md) | 995 | 0.797 | 1.182 | 0.797 | 1.182 | 0.107 | 0.507 | – | 0 (5) | 0 (5) | – | – | +0.075 | +0.156 | [313.883](m1_first_guess/M2_e4_hop3_r262/report.md) |
| e4_hop43 | [M2_e4_hop43_r266](M2_e4_hop43_r266/report.md) | 1155 | 1.915 | 2.734 | 1.915 | 2.734 | 0.281 | 1.054 | – | 0 (5) | 0 (5) | – | – | +0.111 | +0.175 | [382.528](m1_first_guess/M2_e4_hop43_r266/report.md) |
| e4_hop43 | [M2_e4_hop43_r267](M2_e4_hop43_r267/report.md) | 1155 | 1.529 | 2.202 | 1.529 | 2.202 | 0.210 | 0.806 | – | 0 (5) | 0 (5) | – | – | +0.100 | +0.236 | [382.711](m1_first_guess/M2_e4_hop43_r267/report.md) |
| e5_slide | [M2_e5_slide_r271](M2_e5_slide_r271/report.md) | 936 | 1.010 | 1.324 | 1.010 | 1.324 | 0.161 | 0.553 | 0.000 | – | – | 0 (1) | 0 (1) | – | – | [201.198](m1_first_guess/M2_e5_slide_r271/report.md) |
| e5_slide | [M2_e5_slide_r272](M2_e5_slide_r272/report.md) | 935 | 0.933 | 1.265 | 0.933 | 1.265 | 0.160 | 0.598 | 0.000 | – | – | 0 (1) | 0 (1) | – | – | [198.615](m1_first_guess/M2_e5_slide_r272/report.md) |
| e5_slidejump02 | [M2_e5_slidejump02_r276](M2_e5_slidejump02_r276/report.md) | 821 | 0.914 | 1.492 | 0.902 | 1.289 | 0.756 | 9.981 | – | 0 (1) | 0 (1) | 0 (2) | -1 (2) | -0.310 | -0.996 | [177.807](m1_first_guess/M2_e5_slidejump02_r276/report.md) |
| e5_slidejump02 | [M2_e5_slidejump02_r277](M2_e5_slidejump02_r277/report.md) | 821 | 0.950 | 1.567 | 0.937 | 1.306 | 0.765 | 9.968 | – | 0 (1) | 0 (1) | 0 (2) | -1 (2) | -0.305 | -0.985 | [174.379](m1_first_guess/M2_e5_slidejump02_r277/report.md) |
| e5_slidejump06 | [M2_e5_slidejump06_r281](M2_e5_slidejump06_r281/report.md) | 879 | 1.305 | 1.786 | 1.304 | 1.786 | 0.237 | 0.635 | – | 0 (1) | 0 (1) | 0 (2) | 0 (2) | +0.145 | +0.264 | [300.612](m1_first_guess/M2_e5_slidejump06_r281/report.md) |
| e5_slidejump06 | [M2_e5_slidejump06_r282](M2_e5_slidejump06_r282/report.md) | 879 | 1.265 | 1.813 | 1.264 | 1.813 | 0.224 | 0.772 | – | 0 (1) | 0 (1) | 0 (2) | 0 (2) | +0.143 | +0.243 | [300.500](m1_first_guess/M2_e5_slidejump06_r282/report.md) |
| M1 | [M1_r41](M1_r41/report.md) | 1225 | 1.382 | 3.375 | 0.904 | 1.079 | 0.004 | 0.025 | 0.000 | 0 (1) | 0 (1) | – | – | -0.001 | -0.001 | [32.174](m1_first_guess/M1_r41/report.md) |
| M1 | [M1_r42](M1_r42/report.md) | 1225 | 1.381 | 3.374 | 0.902 | 1.078 | 0.014 | 0.083 | 0.000 | 0 (1) | 0 (1) | – | – | -0.001 | -0.005 | [32.285](m1_first_guess/M1_r42/report.md) |
| M1 | [M1_r46](M1_r46/report.md) | 1225 | 1.379 | 3.374 | 0.901 | 1.076 | 0.003 | 0.025 | 0.000 | 0 (1) | 0 (1) | – | – | 0.000 | +0.004 | [32.188](m1_first_guess/M1_r46/report.md) |

## 2. Per condition (R5MotorV2; RMS = mean of the trials, max = worst trial)

| condition | n | pos RMS 3D | pos max 3D | pos RMS h | pos max h | vel RMS 3D | vel max 3D | terminal Δ | worst event Δ (steps) | apex err | takeoff vz err | M1 pos RMS 3D | M1 vel RMS 3D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e1_walk | 2 | 0.025 | 0.043 | 0.024 | 0.041 | 0.002 | 0.025 | 0.000 | – | – | – | 32.063 | 24.863 |
| e1_sprint | 2 | 0.058 | 0.120 | 0.058 | 0.120 | 0.015 | 0.063 | 0.000 | – | – | – | 210.940 | 71.669 |
| e1_crouch | 2 | 0.025 | 0.040 | 0.024 | 0.037 | 0.003 | 0.057 | 0.000 | – | – | – | 201.174 | 67.841 |
| e1_back | 2 | 0.148 | 0.232 | 0.147 | 0.232 | 0.015 | 0.109 | 0.000 | – | – | – | 32.154 | 24.816 |
| e1_side | 2 | 0.151 | 0.248 | 0.151 | 0.248 | 0.011 | 0.083 | 0.000 | – | – | – | 32.268 | 24.882 |
| e1_diag | 2 | 0.137 | 0.193 | 0.137 | 0.192 | 0.016 | 0.112 | 0.000 | – | – | – | 32.256 | 24.959 |
| e1_turn | 2 | 0.658 | 0.967 | 0.658 | 0.966 | 0.105 | 0.462 | 0.000 | – | – | – | 155.151 | 77.879 |
| e2_strafe | 2 | 80.739 | 125.475 | 80.739 | 125.475 | 60.308 | 209.288 | – | 0 | +0.031 | +0.011 | 154.023 | 74.504 |
| e2_noinput | 2 | 0.507 | 0.810 | 0.507 | 0.809 | 0.137 | 0.518 | – | 0 | +0.013 | -0.012 | 181.010 | 77.097 |
| e2_keepfwd | 2 | 0.645 | 1.137 | 0.645 | 1.137 | 0.140 | 0.644 | 0.000 | 0 | +0.062 | +0.007 | 247.296 | 84.575 |
| e4_stand | 2 | 0.844 | 3.299 | 0.000 | 0.000 | 17.770 | 280.502 | – | +2 | +1.795 | -0.016 | 1.487 | 27.774 |
| e4_hop0 | 2 | 1.110 | 1.734 | 1.110 | 1.734 | 0.183 | 0.561 | – | 0 | +0.064 | +0.125 | 310.618 | 110.530 |
| e4_hop3 | 2 | 0.845 | 1.309 | 0.845 | 1.309 | 0.114 | 0.680 | – | 0 | +0.075 | +0.156 | 313.965 | 125.922 |
| e4_hop43 | 2 | 1.722 | 2.734 | 1.722 | 2.734 | 0.245 | 1.054 | – | 0 | +0.111 | +0.236 | 382.619 | 112.484 |
| e5_slide | 2 | 0.972 | 1.324 | 0.972 | 1.324 | 0.160 | 0.598 | 0.000 | 0 | – | – | 199.907 | 94.802 |
| e5_slidejump02 | 2 | 0.932 | 1.567 | 0.919 | 1.306 | 0.761 | 9.981 | – | -1 | -0.310 | -0.996 | 176.093 | 86.104 |
| e5_slidejump06 | 2 | 1.285 | 1.813 | 1.284 | 1.813 | 0.230 | 0.772 | – | 0 | +0.145 | +0.264 | 300.556 | 104.516 |
| M1 | 3 | 1.381 | 3.375 | 0.902 | 1.079 | 0.007 | 0.083 | 0.000 | 0 | -0.001 | -0.005 | 32.216 | 23.149 |

## 3. Ground mapping: terminal speed and accel/decel, Unity motor vs R5

Same estimator on both series (ReplayMetrics.Ground: GROUND-MODEL §1 — band by nearest nominal rate, rate = ΣΔs/Σdt, decel excludes the zeroing step). Unity spread = (max − min)/mean over the condition's trials (plan acceptance: terminal ≤ 2 %, accel/decel ≤ 5 %); Unity vs R5 = (sim mean − ref mean)/ref mean.

| condition | quantity | R5 per trial | Unity per trial | R5 mean | Unity mean | Unity vs R5 | R5 spread | Unity spread | acceptance (Unity spread) |
|---|---|---|---|---|---|---|---|---|---|
| e1_walk | terminal speed (u/s) | 199.525 / 199.525 | 199.525 / 199.525 | 199.525 | 199.525 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_walk | accel_low (u/s²) | 2874.774 / 2874.648 | 2875.000 / 2875.000 | 2874.711 | 2875.000 | +0.010 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_walk | accel_mid (u/s²) | 517.580 / 517.446 | 517.500 / 517.500 | 517.513 | 517.500 | -0.003 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e1_walk | decel_stand (u/s²) | 1249.977 / 1249.931 | 1250.000 / 1250.000 | 1249.954 | 1250.000 | +0.004 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_sprint | terminal speed (u/s) | 299.000 / 299.000 | 299.000 / 299.000 | 299.000 | 299.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_sprint | accel_low (u/s²) | 2875.364 / 2874.060 | 2875.000 / 2875.000 | 2874.712 | 2875.000 | +0.010 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| e1_sprint | accel_mid (u/s²) | 517.519 / 517.513 | 517.500 / 517.500 | 517.516 | 517.500 | -0.003 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_sprint | accel_sprint (u/s²) | 117.318 / 117.317 | 117.300 / 117.300 | 117.318 | 117.300 | -0.015 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_sprint | decel_stand (u/s²) | 1250.111 / 1250.153 | 1250.000 / 1250.000 | 1250.132 | 1250.000 | -0.011 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_crouch | terminal speed (u/s) | 92.000 / 92.000 | 92.000 / 92.000 | 92.000 | 92.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_crouch | accel_low (u/s²) | 2874.137 / 2874.919 | 2875.000 / 2875.000 | 2874.528 | 2875.000 | +0.016 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e1_crouch | decel_duck (u/s²) | 1499.532 / 1498.980 | 1500.000 / 1500.000 | 1499.256 | 1500.000 | +0.050 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e1_back | terminal speed (u/s) | 199.525 / 199.525 | 199.525 / 199.525 | 199.525 | 199.525 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_back | accel_low (u/s²) | 2876.444 / 2876.689 | 2875.000 / 2875.000 | 2876.566 | 2875.000 | -0.054 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_back | accel_mid (u/s²) | 517.706 / 517.744 | 517.500 / 517.500 | 517.725 | 517.500 | -0.043 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_back | decel_stand (u/s²) | 1250.586 / 1250.062 | 1250.000 / 1250.000 | 1250.324 | 1250.000 | -0.026 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e1_side | terminal speed (u/s) | 199.525 / 199.525 | 199.525 / 199.525 | 199.525 | 199.525 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_side | accel_low (u/s²) | 2876.193 / 2876.008 | 2875.000 / 2875.000 | 2876.101 | 2875.000 | -0.038 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_side | accel_mid (u/s²) | 517.722 / 517.747 | 517.500 / 517.500 | 517.734 | 517.500 | -0.045 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e1_side | decel_stand (u/s²) | 1250.306 / 1250.396 | 1250.000 / 1250.000 | 1250.351 | 1250.000 | -0.028 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_diag | terminal speed (u/s) | 199.525 / 199.525 | 199.525 / 199.525 | 199.525 | 199.525 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_diag | accel_low (u/s²) | 2876.214 / 2876.607 | 2875.000 / 2875.000 | 2876.411 | 2875.000 | -0.049 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_diag | accel_mid (u/s²) | 517.721 / 517.804 | 517.500 / 517.500 | 517.763 | 517.500 | -0.051 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e1_diag | decel_stand (u/s²) | 1250.585 / 1250.506 | 1250.000 / 1250.000 | 1250.545 | 1250.000 | -0.044 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e1_turn | terminal speed (u/s) | 299.000 / 299.000 | 299.000 / 299.000 | 299.000 | 299.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e1_turn | accel_low (u/s²) | 2870.572 / 2873.475 | 2875.000 / 2875.000 | 2872.023 | 2875.000 | +0.104 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e1_turn | accel_mid (u/s²) | 516.563 / 517.342 | 517.500 / 517.500 | 516.953 | 517.500 | +0.106 % | 0.15 % | 0.00 % | pass (≤ 5 %) |
| e1_turn | accel_sprint (u/s²) | 117.204 / 117.186 | 117.300 / 117.300 | 117.195 | 117.300 | +0.090 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e1_turn | decel_stand (u/s²) | 1249.414 / 1248.049 | 1250.000 / 1250.000 | 1248.732 | 1250.000 | +0.102 % | 0.11 % | 0.00 % | pass (≤ 5 %) |
| e2_strafe | accel_low (u/s²) | 2874.918 / 2876.810 | 2875.000 / 2875.000 | 2875.864 | 2875.000 | -0.030 % | 0.07 % | 0.00 % | pass (≤ 5 %) |
| e2_strafe | accel_mid (u/s²) | 517.172 / 517.252 | 517.500 / 517.500 | 517.212 | 517.500 | +0.056 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e2_strafe | accel_sprint (u/s²) | 117.175 / 117.188 | 117.300 / 117.300 | 117.181 | 117.300 | +0.101 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e2_strafe | decel_stand (u/s²) | 1248.506 / 1249.580 | 1250.000 / 1250.000 | 1249.043 | 1250.000 | +0.077 % | 0.09 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | accel_low (u/s²) | 2876.604 / 2873.098 | 2875.000 / 2875.000 | 2874.851 | 2875.000 | +0.005 % | 0.12 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | accel_mid (u/s²) | 517.269 / 516.750 | 517.500 / 517.500 | 517.010 | 517.500 | +0.095 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | accel_sprint (u/s²) | 117.144 / 117.204 | 117.300 / 117.300 | 117.174 | 117.300 | +0.107 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| e2_noinput | decel_stand (u/s²) | 1248.641 / 1248.745 | 1250.000 / 1250.000 | 1248.693 | 1250.000 | +0.105 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e2_keepfwd | terminal speed (u/s) | 299.000 / 299.000 | 299.000 / 299.000 | 299.000 | 299.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e2_keepfwd | accel_low (u/s²) | 2870.329 / 2871.985 | 2875.000 / 2875.000 | 2871.157 | 2875.000 | +0.134 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e2_keepfwd | accel_mid (u/s²) | 517.628 / 517.446 | 517.500 / 517.500 | 517.537 | 517.500 | -0.007 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e2_keepfwd | accel_sprint (u/s²) | 117.216 / 117.184 | 117.300 / 117.300 | 117.200 | 117.300 | +0.085 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e2_keepfwd | decel_stand (u/s²) | 1248.820 / 1249.282 | 1250.000 / 1250.000 | 1249.051 | 1250.000 | +0.076 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e4_hop0 | accel_low (u/s²) | 2870.616 / 2869.862 | 2875.000 / 2875.000 | 2870.239 | 2875.000 | +0.166 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e4_hop0 | accel_mid (u/s²) | 516.785 / 516.934 | 517.500 / 517.500 | 516.860 | 517.500 | +0.124 % | 0.03 % | 0.00 % | pass (≤ 5 %) |
| e4_hop0 | accel_sprint (u/s²) | 117.202 / 117.202 | 117.300 / 117.300 | 117.202 | 117.300 | +0.083 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e4_hop0 | decel_stand (u/s²) | 1248.927 / 1248.865 | 1250.000 / 1250.000 | 1248.896 | 1250.000 | +0.088 % | 0.00 % | 0.00 % | pass (≤ 5 %) |
| e4_hop3 | accel_low (u/s²) | 2876.947 / 2875.866 | 2875.000 / 2875.000 | 2876.407 | 2875.000 | -0.049 % | 0.04 % | 0.00 % | pass (≤ 5 %) |
| e4_hop3 | accel_mid (u/s²) | 516.776 / 517.253 | 517.500 / 517.500 | 517.014 | 517.500 | +0.094 % | 0.09 % | 0.00 % | pass (≤ 5 %) |
| e4_hop3 | accel_sprint (u/s²) | 114.868 / 114.859 | 115.000 / 115.000 | 114.863 | 115.000 | +0.119 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e4_hop3 | decel_stand (u/s²) | 1248.516 / 1249.322 | 1250.000 / 1250.000 | 1248.919 | 1250.000 | +0.087 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e4_hop43 | accel_low (u/s²) | 2869.299 / 2870.739 | 2875.000 / 2875.000 | 2870.019 | 2875.000 | +0.174 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| e4_hop43 | accel_mid (u/s²) | 516.922 / 516.623 | 517.500 / 517.500 | 516.773 | 517.500 | +0.141 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e4_hop43 | accel_sprint (u/s²) | 114.871 / 114.931 | 115.000 / 115.000 | 114.901 | 115.000 | +0.086 % | 0.05 % | 0.00 % | pass (≤ 5 %) |
| e4_hop43 | decel_stand (u/s²) | 1250.318 / 1249.563 | 1250.000 / 1250.000 | 1249.941 | 1250.000 | +0.005 % | 0.06 % | 0.00 % | pass (≤ 5 %) |
| e5_slide | terminal speed (u/s) | 92.000 / 92.000 | 92.000 / 92.000 | 92.000 | 92.000 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| e5_slide | accel_low (u/s²) | 2874.003 / 2870.616 | 2875.000 / 2875.000 | 2872.310 | 2875.000 | +0.094 % | 0.12 % | 0.00 % | pass (≤ 5 %) |
| e5_slide | accel_mid (u/s²) | 516.575 / 517.437 | 517.500 / 517.500 | 517.006 | 517.500 | +0.096 % | 0.17 % | 0.00 % | pass (≤ 5 %) |
| e5_slide | accel_sprint (u/s²) | 114.839 / 114.922 | 115.000 / 115.000 | 114.880 | 115.000 | +0.104 % | 0.07 % | 0.00 % | pass (≤ 5 %) |
| e5_slide | decel_stand (u/s²) | 1249.365 / 1248.164 | 1250.000 / 1250.000 | 1248.764 | 1250.000 | +0.099 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e5_slide | decel_duck (u/s²) | 1499.405 / 1496.983 | 1500.000 / 1500.000 | 1498.194 | 1500.000 | +0.121 % | 0.16 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump02 | accel_low (u/s²) | 2868.269 / 2871.006 | 2875.000 / 2875.000 | 2869.637 | 2875.000 | +0.187 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump02 | accel_mid (u/s²) | 516.599 / 516.561 | 517.500 / 517.500 | 516.580 | 517.500 | +0.178 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump02 | accel_sprint (u/s²) | 114.924 / 114.812 | 115.000 / 115.000 | 114.868 | 115.000 | +0.115 % | 0.10 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump02 | decel_stand (u/s²) | 1249.269 / 1251.078 | 1250.000 / 1250.000 | 1250.174 | 1250.000 | -0.014 % | 0.14 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump02 | decel_duck (u/s²) | 1495.584 / 1506.589 | 1500.000 / 1500.000 | 1501.086 | 1500.000 | -0.072 % | 0.73 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump06 | accel_low (u/s²) | 2870.246 / 2869.596 | 2875.000 / 2875.000 | 2869.921 | 2875.000 | +0.177 % | 0.02 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump06 | accel_mid (u/s²) | 516.300 / 518.096 | 517.500 / 517.500 | 517.198 | 517.500 | +0.058 % | 0.35 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump06 | accel_sprint (u/s²) | 114.854 / 114.849 | 115.000 / 115.000 | 114.852 | 115.000 | +0.129 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump06 | decel_stand (u/s²) | 1246.329 / 1254.788 | 1250.000 / 1250.000 | 1250.559 | 1250.000 | -0.045 % | 0.68 % | 0.00 % | pass (≤ 5 %) |
| e5_slidejump06 | decel_duck (u/s²) | 1496.695 / 1505.891 | 1500.000 / 1500.000 | 1501.293 | 1500.000 | -0.086 % | 0.61 % | 0.00 % | pass (≤ 5 %) |
| M1 | terminal speed (u/s) | 199.525 / 199.525 / 199.525 | 199.525 / 199.525 / 199.525 | 199.525 | 199.525 | 0.000 % | 0.00 % | 0.00 % | pass (≤ 2 %) |
| M1 | accel_low (u/s²) | 2875.087 / 2875.393 / 2875.236 | 2875.000 / 2875.000 / 2875.000 | 2875.239 | 2875.000 | -0.008 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| M1 | accel_mid (u/s²) | 517.469 / 517.454 / 517.530 | 517.500 / 517.500 / 517.500 | 517.484 | 517.500 | +0.003 % | 0.01 % | 0.00 % | pass (≤ 5 %) |
| M1 | decel_stand (u/s²) | 1249.922 / 1249.948 / 1249.990 | 1250.000 / 1250.000 / 1250.000 | 1249.953 | 1250.000 | +0.004 % | 0.01 % | 0.00 % | pass (≤ 5 %) |

## 4. Flags (R5MotorV2 vs reference columns; steps that differ)

| trial | grounded | sliding | sprinting | maxspeed (n compared) |
|---|---|---|---|---|
| M2_e1_walk_r301 | 0 | 0 | 0 | 0 (792) |
| M2_e1_walk_r302 | 0 | 0 | 0 | 0 (792) |
| M2_e1_sprint_r306 | 0 | 0 | 0 | 0 (792) |
| M2_e1_sprint_r307 | 0 | 0 | 0 | 0 (792) |
| M2_e1_crouch_r311 | 0 | 0 | 0 | 66 (1007) |
| M2_e1_crouch_r312 | 0 | 0 | 0 | 64 (1008) |
| M2_e1_back_r316 | 0 | 0 | 0 | 0 (792) |
| M2_e1_back_r317 | 0 | 0 | 0 | 0 (792) |
| M2_e1_side_r321 | 0 | 0 | 0 | 0 (791) |
| M2_e1_side_r322 | 0 | 0 | 0 | 0 (792) |
| M2_e1_diag_r326 | 0 | 0 | 0 | 0 (792) |
| M2_e1_diag_r327 | 0 | 0 | 0 | 0 (792) |
| M2_e1_turn_r331 | 0 | 0 | 0 | 0 (936) |
| M2_e1_turn_r332 | 0 | 0 | 0 | 0 (936) |
| M2_e2_strafe_r336 | 0 | 0 | 0 | 0 (753) |
| M2_e2_strafe_r337 | 0 | 0 | 0 | 0 (753) |
| M2_e2_noinput_r341 | 0 | 0 | 0 | 0 (653) |
| M2_e2_noinput_r342 | 0 | 0 | 0 | 0 (653) |
| M2_e2_keepfwd_r346 | 0 | 0 | 0 | 0 (793) |
| M2_e2_keepfwd_r347 | 0 | 0 | 0 | 0 (793) |
| M2_e4_stand_r351 | 1 | 0 | 0 | 0 (361) |
| M2_e4_stand_r352 | 2 | 0 | 0 | 0 (361) |
| M2_e4_hop0_r356 | 0 | 0 | 0 | 0 (982) |
| M2_e4_hop0_r357 | 0 | 0 | 0 | 0 (983) |
| M2_e4_hop3_r261 | 0 | 0 | 0 | 0 (995) |
| M2_e4_hop3_r262 | 0 | 0 | 0 | 0 (995) |
| M2_e4_hop43_r266 | 0 | 0 | 0 | 0 (1155) |
| M2_e4_hop43_r267 | 0 | 0 | 0 | 0 (1155) |
| M2_e5_slide_r271 | 0 | 0 | 0 | 1 (936) |
| M2_e5_slide_r272 | 0 | 0 | 0 | 1 (935) |
| M2_e5_slidejump02_r276 | 0 | 1 | 0 | 1 (821) |
| M2_e5_slidejump02_r277 | 0 | 1 | 0 | 1 (821) |
| M2_e5_slidejump06_r281 | 0 | 0 | 0 | 1 (879) |
| M2_e5_slidejump06_r282 | 0 | 0 | 0 | 1 (879) |
| M1_r41 | 0 | 0 | 0 | – |
| M1_r42 | 0 | 0 | 0 | – |
| M1_r46 | 0 | 0 | 0 | – |

## 5. M1 first guess (before) vs R5MotorV2 (after)

| trial | pos RMS 3D before → after | pos max 3D before → after | vel RMS 3D before → after | vel max 3D before → after | terminal Δ before → after | takeoff vz err before → after | apex err before → after | land Δ before → after |
|---|---|---|---|---|---|---|---|---|
| M1_r41 | 32.174 → 1.382 | 34.477 → 3.375 | 23.126 → 0.004 | 288.865 → 0.025 | 0.000 → 0.000 | +2.527 → -0.001 | +0.969 → -0.001 | +2 (1) → 0 (1) |
| M1_r42 | 32.285 → 1.381 | 34.589 → 3.374 | 23.161 → 0.014 | 288.430 → 0.083 | 0.000 → 0.000 | +2.601 → -0.005 | +1.000 → -0.001 | +2 (1) → 0 (1) |
| M1_r46 | 32.188 → 1.379 | 34.493 → 3.374 | 23.160 → 0.003 | 288.092 → 0.025 | 0.000 → 0.000 | +2.625 → +0.004 | +1.008 → 0.000 | +2 (1) → 0 (1) |
| M2_e1_walk_r301 | 32.121 → 0.031 | 34.504 → 0.043 | 24.917 → 0.002 | 125.635 → 0.014 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_walk_r302 | 32.005 → 0.019 | 34.369 → 0.029 | 24.810 → 0.003 | 124.681 → 0.025 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_sprint_r306 | 210.986 → 0.090 | 295.555 → 0.120 | 71.703 → 0.012 | 126.102 → 0.037 | -99.475 → 0.000 | – → – | – → – | – → – |
| M2_e1_sprint_r307 | 210.893 → 0.026 | 295.423 → 0.046 | 71.634 → 0.018 | 125.911 → 0.063 | -99.475 → 0.000 | – → – | – → – | – → – |
| M2_e1_crouch_r311 | 201.148 → 0.027 | 293.145 → 0.040 | 67.860 → 0.002 | 121.399 → 0.026 | +107.525 → 0.000 | – → – | – → – | – → – |
| M2_e1_crouch_r312 | 201.200 → 0.023 | 293.393 → 0.036 | 67.822 → 0.004 | 121.441 → 0.057 | +107.525 → 0.000 | – → – | – → – | – → – |
| M2_e1_back_r316 | 32.163 → 0.176 | 34.578 → 0.232 | 24.802 → 0.015 | 124.749 → 0.092 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_back_r317 | 32.144 → 0.119 | 34.537 → 0.157 | 24.831 → 0.015 | 124.695 → 0.109 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_side_r321 | 32.303 → 0.181 | 34.723 → 0.248 | 24.919 → 0.011 | 125.445 → 0.083 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_side_r322 | 32.234 → 0.121 | 34.636 → 0.162 | 24.845 → 0.012 | 125.470 → 0.077 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_diag_r326 | 32.248 → 0.142 | 34.668 → 0.193 | 24.985 → 0.014 | 125.343 → 0.091 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_diag_r327 | 32.263 → 0.132 | 34.686 → 0.186 | 24.933 → 0.017 | 125.681 → 0.112 | 0.000 → 0.000 | – → – | – → – | – → – |
| M2_e1_turn_r331 | 155.700 → 0.739 | 216.962 → 0.967 | 78.044 → 0.136 | 136.753 → 0.405 | -99.637 → 0.000 | – → – | – → – | – → – |
| M2_e1_turn_r332 | 154.602 → 0.576 | 215.423 → 0.787 | 77.713 → 0.074 | 126.681 → 0.462 | -99.637 → 0.000 | – → – | – → – | – → – |
| M2_e2_strafe_r336 | 154.438 → 80.756 | 200.897 → 125.475 | 74.547 → 60.249 | 306.927 → 209.277 | – → – | +2.600 → -0.010 | +1.028 → +0.028 | +2 (1) → 0 (1) |
| M2_e2_strafe_r337 | 153.609 → 80.721 | 199.936 → 125.453 | 74.460 → 60.368 | 306.031 → 209.288 | – → – | +2.632 → +0.011 | +1.038 → +0.031 | +2 (1) → 0 (1) |
| M2_e2_noinput_r341 | 179.824 → 0.445 | 269.837 → 0.657 | 76.551 → 0.103 | 302.230 → 0.404 | – → – | +2.628 → +0.007 | +1.020 → +0.013 | +2 (1) → 0 (1) |
| M2_e2_noinput_r342 | 182.197 → 0.569 | 272.604 → 0.810 | 77.643 → 0.170 | 302.088 → 0.518 | – → – | +2.564 → -0.012 | +1.000 → +0.010 | +2 (1) → 0 (1) |
| M2_e2_keepfwd_r346 | 248.875 → 0.540 | 398.690 → 0.834 | 84.592 → 0.152 | 305.173 → 0.644 | -99.475 → 0.000 | +2.613 → +0.007 | +1.062 → +0.062 | +2 (1) → 0 (1) |
| M2_e2_keepfwd_r347 | 245.717 → 0.751 | 394.660 → 1.137 | 84.558 → 0.128 | 304.960 → 0.540 | -99.475 → 0.000 | +2.608 → +0.002 | +1.066 → +0.061 | +2 (1) → 0 (1) |
| M2_e4_stand_r351 | 1.241 → 0.590 | 3.751 → 1.739 | 25.788 → 14.728 | 286.517 → 278.931 | – → – | +2.651 → -0.015 | +2.009 → +0.979 | +3 (1) → +1 (1) |
| M2_e4_stand_r352 | 1.733 → 1.098 | 5.256 → 3.299 | 29.760 → 20.811 | 288.325 → 280.502 | – → – | +2.594 → -0.016 | +2.798 → +1.795 | +4 (1) → +2 (1) |
| M2_e4_hop0_r356 | 310.301 → 1.248 | 474.147 → 1.734 | 111.045 → 0.186 | 470.107 → 0.561 | – → – | +133.684 → +0.125 | +39.757 → +0.064 | +252 (5/3) → 0 (5) |
| M2_e4_hop0_r357 | 310.935 → 0.972 | 475.309 → 1.325 | 110.014 → 0.180 | 450.305 → 0.531 | – → – | +133.648 → +0.111 | +39.751 → +0.062 | +252 (5/3) → 0 (5) |
| M2_e4_hop3_r261 | 314.047 → 0.893 | 480.617 → 1.309 | 126.011 → 0.121 | 306.385 → 0.680 | – → – | +133.683 → +0.153 | +39.759 → +0.073 | +53 (5) → 0 (5) |
| M2_e4_hop3_r262 | 313.883 → 0.797 | 480.435 → 1.182 | 125.834 → 0.107 | 305.130 → 0.507 | – → – | +133.688 → +0.156 | +39.760 → +0.075 | +53 (5) → 0 (5) |
| M2_e4_hop43_r266 | 382.528 → 1.915 | 595.268 → 2.734 | 111.901 → 0.281 | 305.917 → 1.054 | – → – | +91.116 → +0.175 | +29.693 → +0.111 | +34 (5) → 0 (5) |
| M2_e4_hop43_r267 | 382.711 → 1.529 | 594.631 → 2.202 | 113.067 → 0.210 | 305.478 → 0.806 | – → – | +86.488 → +0.236 | +28.462 → +0.100 | +34 (5) → 0 (5) |
| M2_e5_slide_r271 | 201.198 → 1.010 | 324.657 → 1.324 | 95.119 → 0.161 | 258.671 → 0.553 | +107.525 → 0.000 | – → – | – → – | – → – |
| M2_e5_slide_r272 | 198.615 → 0.933 | 321.527 → 1.265 | 94.484 → 0.160 | 258.644 → 0.598 | +107.525 → 0.000 | – → – | – → – | – → – |
| M2_e5_slidejump02_r276 | 177.807 → 0.914 | 266.608 → 1.492 | 86.498 → 0.756 | 291.170 → 9.981 | – → – | +17.581 → -0.996 | +6.638 → -0.310 | +8 (1) → 0 (1) |
| M2_e5_slidejump02_r277 | 174.379 → 0.950 | 262.667 → 1.567 | 85.711 → 0.765 | 291.020 → 9.968 | – → – | +17.547 → -0.985 | +6.626 → -0.305 | +8 (1) → 0 (1) |
| M2_e5_slidejump06_r281 | 300.612 → 1.305 | 448.247 → 1.786 | 104.507 → 0.237 | 320.662 → 0.635 | – → – | +18.836 → +0.264 | +7.090 → +0.145 | +8 (1) → 0 (1) |
| M2_e5_slidejump06_r282 | 300.500 → 1.265 | 448.160 → 1.813 | 104.524 → 0.224 | 320.686 → 0.772 | – → – | +18.842 → +0.243 | +7.098 → +0.143 | +8 (1) → 0 (1) |

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
- Not modelled: lurch (first strafe press in air), slideAccel / slideWantToStopDecel / slideMaxStopSpeed, landSlowdown, skip_speed_reduce, the 1.4e-5·vz² residual air gain, the duck transition (hull/eye offset), sprint timing keys, server corrections, slopes/steps/collisions.

