| trial | pull window (steps) | pull-window pos RMS 3D: plain / F1 (M4) / RF (M5) | RMS horizontal F1 → RF | max 3D F1 → RF | vel RMS F1 → RF | at release: pos err F1 → RF | speed err F1 → RF | vel err F1 → RF | velocity direction err F1 → RF (deg) |
|---|---|---|---|---|---|---|---|---|---|
| M4_m4_grapple_hold_r1701 | 109..243 (135) | 179.91 / 7.39 / **7.54** | 2.57 → 7.27 | 11.37 → 10.19 | 35.94 → 17.94 | 11.37 → 4.10 | +11.73 → +16.53 | 99.53 → 31.28 | 9.19 → 2.46 |
| M4_m4_grapple_hold_r1702 | 108..242 (135) | 180.24 / 6.53 / **10.32** | 2.30 → 10.23 | 9.96 → 13.35 | 34.03 → 18.87 | 8.87 → 10.03 | +6.04 → +11.18 | 97.10 → 29.46 | 9.03 → 2.53 |
| M4_m4_grapple_near_r2101 | 99..200 (102) | 113.59 / 3.76 / **10.17** | 1.49 → 9.08 | 5.76 → 15.12 | 26.65 → 21.83 | 5.38 → 15.11 | +4.79 → +7.70 | 73.89 → 8.44 | 8.90 → 0.41 |
| M4_m4_grapple_near_r2102 | 99..200 (102) | 113.83 / 3.91 / **10.46** | 1.61 → 9.30 | 6.00 → 15.80 | 26.27 → 22.42 | 4.88 → 15.80 | +3.59 → +6.53 | 73.28 → 7.86 | 8.81 → 0.52 |

Event steps (reference / sim) and the detach envelope run (`grapple_envelope/`, release by the model):

| trial | attach ref/sim | pull start ref/sim | release: recorded / envelope (Δ steps) | envelope event | ref gap to the face at the start of the recorded release command (u) | pos RMS 3D up to the earlier release, envelope run |
|---|---|---|---|---|---|---|
| M4_m4_grapple_hold_r1701 | 84/84 | 109/108 | 244 / 246 (+2) | GRAPPLE_RELEASE_GAP | 36.11 | 7.54 |
| M4_m4_grapple_hold_r1702 | 84/84 | 108/108 | 243 / 246 (+3) | GRAPPLE_RELEASE_GAP | 35.30 | 10.32 |
| M4_m4_grapple_near_r2101 | 75/75 | 99/99 | 201 / 205 (+4) | GRAPPLE_RELEASE_GAP | 33.53 | 10.17 |
| M4_m4_grapple_near_r2102 | 75/75 | 99/99 | 201 / 205 (+4) | GRAPPLE_RELEASE_GAP | 32.47 | 10.46 |
