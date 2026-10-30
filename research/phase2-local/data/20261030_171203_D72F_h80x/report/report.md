# hsd_tel report

Inputs: 17 file(s); rows: 102918 (MT 67716, HSD 35200)

Validation: 0 error(s), 19 warning(s), 4 info

- warning `W_TELEPORT` message.log:18377 teleport in stream ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` message.log:19091 teleport in stream ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` message.log:19778 teleport in stream ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` message.log:20485 teleport in stream ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` message.log:21174 teleport in stream ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'cl', 'cmd', 1, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` script.1.log:18028 teleport in stream ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` script.1.log:19252 teleport in stream ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` script.1.log:20453 teleport in stream ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` script.1.log:21676 teleport in stream ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` script.1.log:22878 teleport in stream ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_MORE` script.1.log:0 20 more teleport rows in ('HSD', 'cl', 'frame', None, '09488df4-35e2-4b6a-83b9-224855a093b4')
- warning `W_TELEPORT` message.log:18142 teleport in stream ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_TELEPORT` message.log:18800 teleport in stream ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_TELEPORT` message.log:19435 teleport in stream ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_TELEPORT` message.log:20089 teleport in stream ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_TELEPORT` message.log:20723 teleport in stream ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'sv', 'cmd', 1, '2dccee11-064e-4634-9343-79d9652b7474')
- warning `W_TIME_BACKWARDS` script.log:713 t 22.45 -> 22.30758 in ('HSD', 'sv', 'evt', 1.0, '2dccee11-064e-4634-9343-79d9652b7474')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 17772 | 0 | - | - |
| MT | cl | r90 | 489 | 299.231 | first_order (no) | friction (no) |
| MT | cl | b1 | 166 | 0 | - | - |
| MT | cl | r48000 | 489 | 299.242 | first_order (no) | friction (no) |
| MT | cl | b2 | 144 | 0 | - | - |
| MT | cl | r48001 | 488 | 299.243 | first_order (no) | linear (yes) |
| MT | cl | b3 | 165 | 0 | - | - |
| MT | cl | r48002 | 489 | 299.231 | first_order (no) | friction (no) |
| MT | cl | b4 | 144 | 0 | - | - |
| MT | cl | r48003 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b5 | 144 | 0 | - | - |
| MT | cl | r48004 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b6 | 144 | 0 | - | - |
| MT | cl | r48005 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b7 | 144 | 0 | - | - |
| MT | cl | r48006 | 471 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b8 | 163 | 0 | - | - |
| MT | cl | r48007 | 469 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b9 | 164 | 0 | - | - |
| MT | cl | r48008 | 469 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b10 | 164 | 0 | - | - |
| MT | cl | r48009 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b11 | 159 | 0 | - | - |
| MT | cl | r48010 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b12 | 159 | 0 | - | - |
| MT | cl | r48011 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b13 | 159 | 0 | - | - |
| MT | cl | r48012 | 476 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b14 | 154 | 0 | - | - |
| MT | cl | r48013 | 485 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b15 | 162 | 0 | - | - |
| MT | cl | r48014 | 483 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b16 | 154 | 0 | - | - |
| MT | cl | r48015 | 494 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b17 | 148 | 0 | - | - |
| MT | cl | r48016 | 494 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b18 | 149 | 0 | - | - |
| MT | cl | r48017 | 493 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b19 | 149 | 0 | - | - |
| MT | cl | r48018 | 506 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b20 | 144 | 0 | - | - |
| MT | cl | r48019 | 504 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b21 | 143 | 0 | - | - |
| MT | cl | r48020 | 506 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b22 | 144 | 0 | - | - |
| MT | cl | r48021 | 514 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b23 | 164 | 0 | - | - |
| MT | cl | r48022 | 503 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b24 | 164 | 0 | - | - |
| MT | cl | r48023 | 505 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b25 | 132 | 0 | - | - |
| HSD | cl | r0 | 21590 | 0 | - | - |
| HSD | cl | r90 | 521 | 299.231 | first_order (no) | - |
| HSD | cl | r48000 | 521 | 299.242 | first_order (no) | - |
| HSD | cl | r48001 | 521 | 299.243 | first_order (no) | - |
| HSD | cl | r48002 | 521 | 299.231 | first_order (no) | - |
| HSD | cl | r48003 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r48004 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r48005 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r48006 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r48007 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r48008 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r48009 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r48010 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r48011 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r48012 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r48013 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r48014 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r48015 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r48016 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r48017 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r48018 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r48019 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r48020 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r48021 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r48022 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r48023 | 551 | 299.151 | first_order (no) | - |
| MT | sv | b0 | 17779 | 0 | - | - |
| MT | sv | r90 | 489 | 299.231 | first_order (no) | friction (no) |
| MT | sv | b1 | 166 | 0 | - | - |
| MT | sv | r48000 | 489 | 299.242 | first_order (no) | friction (no) |
| MT | sv | b2 | 144 | 0 | - | - |
| MT | sv | r48001 | 488 | 299.243 | first_order (no) | linear (yes) |
| MT | sv | b3 | 165 | 0 | - | - |
| MT | sv | r48002 | 489 | 299.231 | first_order (no) | friction (no) |
| MT | sv | b4 | 144 | 0 | - | - |
| MT | sv | r48003 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b5 | 144 | 0 | - | - |
| MT | sv | r48004 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b6 | 144 | 0 | - | - |
| MT | sv | r48005 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b7 | 144 | 0 | - | - |
| MT | sv | r48006 | 471 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b8 | 163 | 0 | - | - |
| MT | sv | r48007 | 469 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b9 | 164 | 0 | - | - |
| MT | sv | r48008 | 469 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b10 | 164 | 0 | - | - |
| MT | sv | r48009 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b11 | 159 | 0 | - | - |
| MT | sv | r48010 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b12 | 159 | 0 | - | - |
| MT | sv | r48011 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b13 | 159 | 0 | - | - |
| MT | sv | r48012 | 476 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b14 | 154 | 0 | - | - |
| MT | sv | r48013 | 485 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b15 | 162 | 0 | - | - |
| MT | sv | r48014 | 483 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b16 | 154 | 0 | - | - |
| MT | sv | r48015 | 494 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b17 | 148 | 0 | - | - |
| MT | sv | r48016 | 494 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b18 | 149 | 0 | - | - |
| MT | sv | r48017 | 493 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b19 | 149 | 0 | - | - |
| MT | sv | r48018 | 506 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b20 | 144 | 0 | - | - |
| MT | sv | r48019 | 504 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b21 | 143 | 0 | - | - |
| MT | sv | r48020 | 506 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b22 | 144 | 0 | - | - |
| MT | sv | r48021 | 514 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b23 | 164 | 0 | - | - |
| MT | sv | r48022 | 503 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b24 | 164 | 0 | - | - |
| MT | sv | r48023 | 505 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b25 | 128 | 0 | - | - |

Events: 334. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
