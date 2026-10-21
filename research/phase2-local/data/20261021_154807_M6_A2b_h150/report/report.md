# hsd_tel report

Inputs: 17 file(s); rows: 89236 (MT 58262, HSD 30972)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3691 teleport in stream ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` message.log:4603 teleport in stream ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` message.log:5518 teleport in stream ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` message.log:6431 teleport in stream ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` message.log:7350 teleport in stream ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` script.1.log:3331 teleport in stream ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` script.1.log:5126 teleport in stream ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` script.1.log:6923 teleport in stream ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` script.1.log:8721 teleport in stream ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` script.1.log:10518 teleport in stream ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_MORE` script.1.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, '3e19f836-7734-46ec-b016-b4567752a497')
- warning `W_TELEPORT` message.log:3477 teleport in stream ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_TELEPORT` message.log:4385 teleport in stream ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_TELEPORT` message.log:5295 teleport in stream ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_TELEPORT` message.log:6203 teleport in stream ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_TELEPORT` message.log:7111 teleport in stream ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')
- warning `W_TIME_BACKWARDS` script.log:717 t 25.45 -> 25.12722 in ('HSD', 'sv', 'evt', 1.0, '70a9d3d7-f32a-46e1-b102-c6a878d14e06')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3106 | 0 | - | - |
| MT | cl | r90 | 734 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b1 | 170 | 0 | - | - |
| MT | cl | r3301 | 735 | 299.467 | first_order (no) | friction (no) |
| MT | cl | b2 | 173 | 0 | - | - |
| MT | cl | r3302 | 732 | 299.455 | first_order (no) | friction (no) |
| MT | cl | b3 | 173 | 0 | - | - |
| MT | cl | r3303 | 733 | 299.455 | first_order (no) | friction (no) |
| MT | cl | b4 | 172 | 0 | - | - |
| MT | cl | r3304 | 735 | 299.455 | first_order (no) | friction (no) |
| MT | cl | b5 | 173 | 0 | - | - |
| MT | cl | r3305 | 733 | 299.466 | first_order (no) | friction (no) |
| MT | cl | b6 | 1011 | 0 | - | - |
| MT | cl | r3306 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3307 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3308 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3309 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3310 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3311 | 482 | 299.151 | first_order (no) | - |
| MT | cl | b7 | 185 | 0 | - | - |
| MT | cl | r3312 | 483 | 299.151 | first_order (no) | - |
| MT | cl | b8 | 184 | 0 | - | - |
| MT | cl | r3313 | 480 | 299.151 | first_order (no) | - |
| MT | cl | b9 | 185 | 0 | - | - |
| MT | cl | r3314 | 481 | 299.151 | first_order (no) | - |
| MT | cl | b10 | 182 | 0 | - | - |
| MT | cl | r3315 | 480 | 299.151 | first_order (no) | - |
| MT | cl | b11 | 185 | 0 | - | - |
| MT | cl | r3316 | 601 | 299.151 | first_order (no) | - |
| MT | cl | b12 | 185 | 0 | - | - |
| MT | cl | r3317 | 601 | 299.151 | first_order (no) | - |
| MT | cl | b13 | 185 | 0 | - | - |
| MT | cl | r3318 | 602 | 299.152 | first_order (no) | - |
| MT | cl | b14 | 185 | 0 | - | - |
| MT | cl | r3319 | 603 | 299.151 | first_order (no) | - |
| MT | cl | b15 | 184 | 0 | - | - |
| MT | cl | r3320 | 601 | 299.151 | first_order (no) | - |
| MT | cl | b16 | 185 | 0 | - | - |
| MT | cl | r3321 | 666 | 299.15 | first_order (no) | - |
| MT | cl | b17 | 183 | 0 | - | - |
| MT | cl | r3322 | 664 | 299.151 | first_order (no) | - |
| MT | cl | b18 | 184 | 0 | - | - |
| MT | cl | r3323 | 664 | 299.151 | first_order (no) | - |
| MT | cl | b19 | 184 | 0 | - | - |
| MT | cl | r3324 | 663 | 299.15 | first_order (no) | - |
| MT | cl | b20 | 183 | 0 | - | - |
| MT | cl | r3325 | 661 | 299.152 | first_order (no) | - |
| MT | cl | b21 | 184 | 0 | - | - |
| MT | cl | r3326 | 662 | 299.151 | first_order (no) | - |
| MT | cl | b22 | 184 | 0 | - | - |
| MT | cl | r3327 | 665 | 299.15 | first_order (no) | - |
| MT | cl | b23 | 183 | 0 | - | - |
| MT | cl | r3328 | 663 | 299.151 | first_order (no) | - |
| MT | cl | b24 | 184 | 0 | - | - |
| MT | cl | r3329 | 663 | 299.151 | first_order (no) | - |
| MT | cl | b25 | 184 | 0 | - | - |
| MT | cl | r3330 | 665 | 299.151 | first_order (no) | - |
| MT | cl | b26 | 146 | 0 | - | - |
| HSD | cl | r0 | 8596 | 0 | - | - |
| HSD | cl | r90 | 805 | 299.467 | first_order (no) | - |
| HSD | cl | r3301 | 805 | 299.467 | first_order (no) | - |
| HSD | cl | r3302 | 805 | 299.455 | first_order (no) | - |
| HSD | cl | r3303 | 805 | 299.455 | first_order (no) | - |
| HSD | cl | r3304 | 805 | 299.455 | first_order (no) | - |
| HSD | cl | r3305 | 805 | 299.466 | first_order (no) | - |
| HSD | cl | r3306 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3307 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3308 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3309 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3310 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3311 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3312 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3313 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3314 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3315 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3316 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3317 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3318 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3319 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3320 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3321 | 734 | 299.15 | first_order (no) | - |
| HSD | cl | r3322 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3323 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3324 | 734 | 299.15 | first_order (no) | - |
| HSD | cl | r3325 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3326 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3327 | 734 | 299.15 | first_order (no) | - |
| HSD | cl | r3328 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3329 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3330 | 734 | 299.151 | first_order (no) | - |
| MT | sv | b0 | 3118 | 0 | - | - |
| MT | sv | r90 | 734 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b1 | 170 | 0 | - | - |
| MT | sv | r3301 | 735 | 299.467 | first_order (no) | friction (no) |
| MT | sv | b2 | 173 | 0 | - | - |
| MT | sv | r3302 | 732 | 299.455 | first_order (no) | friction (no) |
| MT | sv | b3 | 173 | 0 | - | - |
| MT | sv | r3303 | 733 | 299.455 | first_order (no) | friction (no) |
| MT | sv | b4 | 172 | 0 | - | - |
| MT | sv | r3304 | 735 | 299.455 | first_order (no) | friction (no) |
| MT | sv | b5 | 173 | 0 | - | - |
| MT | sv | r3305 | 733 | 299.466 | first_order (no) | friction (no) |
| MT | sv | b6 | 1011 | 0 | - | - |
| MT | sv | r3306 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3307 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3308 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3309 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3310 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3311 | 482 | 299.151 | first_order (no) | - |
| MT | sv | b7 | 185 | 0 | - | - |
| MT | sv | r3312 | 483 | 299.151 | first_order (no) | - |
| MT | sv | b8 | 184 | 0 | - | - |
| MT | sv | r3313 | 480 | 299.151 | first_order (no) | - |
| MT | sv | b9 | 185 | 0 | - | - |
| MT | sv | r3314 | 481 | 299.151 | first_order (no) | - |
| MT | sv | b10 | 182 | 0 | - | - |
| MT | sv | r3315 | 480 | 299.151 | first_order (no) | - |
| MT | sv | b11 | 185 | 0 | - | - |
| MT | sv | r3316 | 601 | 299.151 | first_order (no) | - |
| MT | sv | b12 | 185 | 0 | - | - |
| MT | sv | r3317 | 601 | 299.151 | first_order (no) | - |
| MT | sv | b13 | 185 | 0 | - | - |
| MT | sv | r3318 | 602 | 299.152 | first_order (no) | - |
| MT | sv | b14 | 185 | 0 | - | - |
| MT | sv | r3319 | 603 | 299.151 | first_order (no) | - |
| MT | sv | b15 | 184 | 0 | - | - |
| MT | sv | r3320 | 601 | 299.151 | first_order (no) | - |
| MT | sv | b16 | 185 | 0 | - | - |
| MT | sv | r3321 | 665 | 299.15 | first_order (no) | - |
| MT | sv | b17 | 183 | 0 | - | - |
| MT | sv | r3322 | 664 | 299.151 | first_order (no) | - |
| MT | sv | b18 | 184 | 0 | - | - |
| MT | sv | r3323 | 664 | 299.151 | first_order (no) | - |
| MT | sv | b19 | 184 | 0 | - | - |
| MT | sv | r3324 | 663 | 299.15 | first_order (no) | - |
| MT | sv | b20 | 183 | 0 | - | - |
| MT | sv | r3325 | 661 | 299.152 | first_order (no) | - |
| MT | sv | b21 | 184 | 0 | - | - |
| MT | sv | r3326 | 662 | 299.151 | first_order (no) | - |
| MT | sv | b22 | 184 | 0 | - | - |
| MT | sv | r3327 | 665 | 299.15 | first_order (no) | - |
| MT | sv | b23 | 183 | 0 | - | - |
| MT | sv | r3328 | 663 | 299.151 | first_order (no) | - |
| MT | sv | b24 | 184 | 0 | - | - |
| MT | sv | r3329 | 663 | 299.151 | first_order (no) | - |
| MT | sv | b25 | 184 | 0 | - | - |
| MT | sv | r3330 | 665 | 299.151 | first_order (no) | - |
| MT | sv | b26 | 141 | 0 | - | - |

Events: 1856. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
