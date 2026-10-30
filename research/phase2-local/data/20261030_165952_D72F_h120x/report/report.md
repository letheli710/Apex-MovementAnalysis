# hsd_tel report

Inputs: 18 file(s); rows: 116883 (MT 76036, HSD 40845)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:18000 teleport in stream ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` message.log:18666 teleport in stream ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` message.log:19328 teleport in stream ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` message.log:19992 teleport in stream ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` message.log:20657 teleport in stream ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_MORE` message.log:0 29 more teleport rows in ('MT', 'cl', 'cmd', 1, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` script.2.log:17637 teleport in stream ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` script.2.log:18837 teleport in stream ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` script.2.log:20038 teleport in stream ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` script.2.log:21240 teleport in stream ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` script.2.log:22442 teleport in stream ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_MORE` script.2.log:0 29 more teleport rows in ('HSD', 'cl', 'frame', None, 'f3d6769f-54e3-49cf-973b-7de14be4795d')
- warning `W_TELEPORT` message.log:17757 teleport in stream ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_TELEPORT` message.log:18368 teleport in stream ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_TELEPORT` message.log:18977 teleport in stream ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_TELEPORT` message.log:19586 teleport in stream ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_TELEPORT` message.log:20195 teleport in stream ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_MORE` message.log:0 29 more teleport rows in ('MT', 'sv', 'cmd', 1, 'f37e2889-2693-4d5a-80ad-d1902328381b')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.25 -> 23.17678 in ('HSD', 'sv', 'evt', 1.0, 'f37e2889-2693-4d5a-80ad-d1902328381b')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 17390 | 0 | - | - |
| MT | cl | r90 | 465 | 299.354 | first_order (no) | friction (no) |
| MT | cl | b1 | 142 | 0 | - | - |
| MT | cl | r46000 | 464 | 299.354 | first_order (no) | linear (yes) |
| MT | cl | b2 | 144 | 0 | - | - |
| MT | cl | r46001 | 464 | 299.367 | first_order (no) | linear (yes) |
| MT | cl | b3 | 144 | 0 | - | - |
| MT | cl | r46002 | 464 | 299.354 | first_order (no) | linear (yes) |
| MT | cl | b4 | 144 | 0 | - | - |
| MT | cl | r46003 | 434 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b5 | 144 | 0 | - | - |
| MT | cl | r46004 | 454 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b6 | 144 | 0 | - | - |
| MT | cl | r46005 | 434 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b7 | 144 | 0 | - | - |
| MT | cl | r46006 | 442 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b8 | 106 | 0 | - | - |
| MT | cl | r46007 | 442 | 299.148 | first_order (no) | linear (no) |
| MT | cl | b9 | 165 | 0 | - | - |
| MT | cl | r46008 | 459 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b10 | 164 | 0 | - | - |
| MT | cl | r46009 | 447 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b11 | 159 | 0 | - | - |
| MT | cl | r46010 | 449 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b12 | 159 | 0 | - | - |
| MT | cl | r46011 | 449 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b13 | 159 | 0 | - | - |
| MT | cl | r46012 | 457 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b14 | 154 | 0 | - | - |
| MT | cl | r46013 | 456 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b15 | 112 | 0 | - | - |
| MT | cl | r46014 | 467 | 299 | first_order (no) | - |
| MT | cl | b16 | 164 | 0 | - | - |
| MT | cl | r46015 | 465 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b17 | 148 | 0 | - | - |
| MT | cl | r46016 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b18 | 149 | 0 | - | - |
| MT | cl | r46017 | 465 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b19 | 149 | 0 | - | - |
| MT | cl | r46018 | 471 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b20 | 144 | 0 | - | - |
| MT | cl | r46019 | 472 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b21 | 144 | 0 | - | - |
| MT | cl | r46020 | 472 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b22 | 144 | 0 | - | - |
| MT | cl | r46021 | 474 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b23 | 164 | 0 | - | - |
| MT | cl | r46022 | 474 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b24 | 164 | 0 | - | - |
| MT | cl | r46023 | 474 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b25 | 164 | 0 | - | - |
| MT | cl | r46024 | 426 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b26 | 154 | 0 | - | - |
| MT | cl | r46025 | 426 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b27 | 153 | 0 | - | - |
| MT | cl | r46026 | 424 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b28 | 154 | 0 | - | - |
| MT | cl | r46027 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b29 | 144 | 0 | - | - |
| MT | cl | r46028 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b30 | 144 | 0 | - | - |
| MT | cl | r46029 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b31 | 144 | 0 | - | - |
| MT | cl | r46030 | 451 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b32 | 159 | 0 | - | - |
| MT | cl | r46031 | 451 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b33 | 159 | 0 | - | - |
| MT | cl | r46032 | 452 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b34 | 127 | 0 | - | - |
| HSD | cl | r0 | 22430 | 0 | - | - |
| HSD | cl | r90 | 521 | 299.354 | first_order (no) | - |
| HSD | cl | r46000 | 521 | 299.354 | first_order (no) | - |
| HSD | cl | r46001 | 521 | 299.367 | first_order (no) | - |
| HSD | cl | r46002 | 521 | 299.354 | first_order (no) | - |
| HSD | cl | r46003 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r46004 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r46005 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r46006 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r46007 | 526 | 299.148 | first_order (no) | - |
| HSD | cl | r46008 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r46009 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r46010 | 531 | 299.15 | first_order (no) | - |
| HSD | cl | r46011 | 531 | 299.15 | first_order (no) | - |
| HSD | cl | r46012 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r46013 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r46014 | 536 | 299 | first_order (no) | - |
| HSD | cl | r46015 | 541 | 299.15 | first_order (no) | - |
| HSD | cl | r46016 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r46017 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r46018 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r46019 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r46020 | 546 | 299.15 | first_order (no) | - |
| HSD | cl | r46021 | 551 | 299.15 | first_order (no) | - |
| HSD | cl | r46022 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r46023 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r46024 | 511 | 299.154 | first_order (no) | - |
| HSD | cl | r46025 | 511 | 299.154 | first_order (no) | - |
| HSD | cl | r46026 | 511 | 299.154 | first_order (no) | - |
| HSD | cl | r46027 | 521 | 299.154 | first_order (no) | - |
| HSD | cl | r46028 | 521 | 299.154 | first_order (no) | - |
| HSD | cl | r46029 | 521 | 299.154 | first_order (no) | - |
| HSD | cl | r46030 | 531 | 299.154 | first_order (no) | - |
| HSD | cl | r46031 | 531 | 299.154 | first_order (no) | - |
| HSD | cl | r46032 | 531 | 299.154 | first_order (no) | - |
| MT | sv | b0 | 17394 | 0 | - | - |
| MT | sv | r90 | 465 | 299.354 | first_order (no) | friction (no) |
| MT | sv | b1 | 142 | 0 | - | - |
| MT | sv | r46000 | 464 | 299.354 | first_order (no) | linear (yes) |
| MT | sv | b2 | 144 | 0 | - | - |
| MT | sv | r46001 | 464 | 299.367 | first_order (no) | linear (yes) |
| MT | sv | b3 | 144 | 0 | - | - |
| MT | sv | r46002 | 464 | 299.354 | first_order (no) | linear (yes) |
| MT | sv | b4 | 144 | 0 | - | - |
| MT | sv | r46003 | 434 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b5 | 144 | 0 | - | - |
| MT | sv | r46004 | 454 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b6 | 144 | 0 | - | - |
| MT | sv | r46005 | 434 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b7 | 144 | 0 | - | - |
| MT | sv | r46006 | 442 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b8 | 106 | 0 | - | - |
| MT | sv | r46007 | 442 | 299.148 | first_order (no) | linear (no) |
| MT | sv | b9 | 165 | 0 | - | - |
| MT | sv | r46008 | 459 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b10 | 164 | 0 | - | - |
| MT | sv | r46009 | 447 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b11 | 159 | 0 | - | - |
| MT | sv | r46010 | 449 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b12 | 159 | 0 | - | - |
| MT | sv | r46011 | 449 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b13 | 159 | 0 | - | - |
| MT | sv | r46012 | 457 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b14 | 154 | 0 | - | - |
| MT | sv | r46013 | 456 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b15 | 112 | 0 | - | - |
| MT | sv | r46014 | 467 | 299 | first_order (no) | - |
| MT | sv | b16 | 164 | 0 | - | - |
| MT | sv | r46015 | 465 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b17 | 148 | 0 | - | - |
| MT | sv | r46016 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b18 | 149 | 0 | - | - |
| MT | sv | r46017 | 465 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b19 | 149 | 0 | - | - |
| MT | sv | r46018 | 471 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b20 | 144 | 0 | - | - |
| MT | sv | r46019 | 472 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b21 | 144 | 0 | - | - |
| MT | sv | r46020 | 472 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b22 | 144 | 0 | - | - |
| MT | sv | r46021 | 474 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b23 | 164 | 0 | - | - |
| MT | sv | r46022 | 474 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b24 | 164 | 0 | - | - |
| MT | sv | r46023 | 474 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b25 | 164 | 0 | - | - |
| MT | sv | r46024 | 426 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b26 | 154 | 0 | - | - |
| MT | sv | r46025 | 425 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b27 | 153 | 0 | - | - |
| MT | sv | r46026 | 424 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b28 | 154 | 0 | - | - |
| MT | sv | r46027 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b29 | 144 | 0 | - | - |
| MT | sv | r46028 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b30 | 144 | 0 | - | - |
| MT | sv | r46029 | 437 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b31 | 144 | 0 | - | - |
| MT | sv | r46030 | 451 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b32 | 159 | 0 | - | - |
| MT | sv | r46031 | 451 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b33 | 159 | 0 | - | - |
| MT | sv | r46032 | 452 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b34 | 123 | 0 | - | - |

Events: 478. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
