# hsd_tel report

Inputs: 17 file(s); rows: 103938 (MT 68113, HSD 35823)

Validation: 0 error(s), 19 warning(s), 4 info

- warning `W_TELEPORT` message.log:19014 teleport in stream ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` message.log:19689 teleport in stream ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` message.log:20360 teleport in stream ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` message.log:21029 teleport in stream ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` message.log:21701 teleport in stream ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'cl', 'cmd', 1, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` script.1.log:18660 teleport in stream ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` script.1.log:19861 teleport in stream ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` script.1.log:21062 teleport in stream ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` script.1.log:22263 teleport in stream ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` script.1.log:23465 teleport in stream ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_MORE` script.1.log:0 20 more teleport rows in ('HSD', 'cl', 'frame', None, '5c726e5f-2227-481a-810f-661ddfe601ee')
- warning `W_TELEPORT` message.log:18776 teleport in stream ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_TELEPORT` message.log:19396 teleport in stream ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_TELEPORT` message.log:20015 teleport in stream ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_TELEPORT` message.log:20634 teleport in stream ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_TELEPORT` message.log:21254 teleport in stream ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_MORE` message.log:0 20 more teleport rows in ('MT', 'sv', 'cmd', 1, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.45 -> 23.22786 in ('HSD', 'sv', 'evt', 1.0, 'a27419fe-8f4d-4156-bc34-33072b9e86bc')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 18407 | 0 | - | - |
| MT | cl | r90 | 474 | 299.315 | first_order (no) | friction (no) |
| MT | cl | b1 | 143 | 0 | - | - |
| MT | cl | r47000 | 473 | 299.29 | first_order (no) | linear (yes) |
| MT | cl | b2 | 144 | 0 | - | - |
| MT | cl | r47001 | 473 | 299.302 | first_order (no) | linear (yes) |
| MT | cl | b3 | 143 | 0 | - | - |
| MT | cl | r47002 | 474 | 299.302 | first_order (no) | linear (yes) |
| MT | cl | b4 | 144 | 0 | - | - |
| MT | cl | r47003 | 453 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b5 | 144 | 0 | - | - |
| MT | cl | r47004 | 453 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b6 | 144 | 0 | - | - |
| MT | cl | r47005 | 455 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b7 | 166 | 0 | - | - |
| MT | cl | r47006 | 459 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b8 | 164 | 0 | - | - |
| MT | cl | r47007 | 459 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b9 | 164 | 0 | - | - |
| MT | cl | r47008 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b10 | 164 | 0 | - | - |
| MT | cl | r47009 | 468 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b11 | 159 | 0 | - | - |
| MT | cl | r47010 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b12 | 159 | 0 | - | - |
| MT | cl | r47011 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b13 | 159 | 0 | - | - |
| MT | cl | r47012 | 464 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b14 | 153 | 0 | - | - |
| MT | cl | r47013 | 463 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b15 | 154 | 0 | - | - |
| MT | cl | r47014 | 465 | 299.148 | first_order (no) | linear (no) |
| MT | cl | b16 | 154 | 0 | - | - |
| MT | cl | r47015 | 476 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b17 | 149 | 0 | - | - |
| MT | cl | r47016 | 475 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b18 | 149 | 0 | - | - |
| MT | cl | r47017 | 475 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b19 | 149 | 0 | - | - |
| MT | cl | r47018 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b20 | 144 | 0 | - | - |
| MT | cl | r47019 | 482 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b21 | 144 | 0 | - | - |
| MT | cl | r47020 | 482 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b22 | 144 | 0 | - | - |
| MT | cl | r47021 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b23 | 163 | 0 | - | - |
| MT | cl | r47022 | 483 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b24 | 164 | 0 | - | - |
| MT | cl | r47023 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b25 | 132 | 0 | - | - |
| HSD | cl | r0 | 22193 | 0 | - | - |
| HSD | cl | r90 | 521 | 299.315 | first_order (no) | - |
| HSD | cl | r47000 | 521 | 299.29 | first_order (no) | - |
| HSD | cl | r47001 | 521 | 299.302 | first_order (no) | - |
| HSD | cl | r47002 | 521 | 299.302 | first_order (no) | - |
| HSD | cl | r47003 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r47004 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r47005 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r47006 | 526 | 299.15 | first_order (no) | - |
| HSD | cl | r47007 | 526 | 299.15 | first_order (no) | - |
| HSD | cl | r47008 | 526 | 299.151 | first_order (no) | - |
| HSD | cl | r47009 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r47010 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r47011 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r47012 | 536 | 299.15 | first_order (no) | - |
| HSD | cl | r47013 | 536 | 299.151 | first_order (no) | - |
| HSD | cl | r47014 | 536 | 299.148 | first_order (no) | - |
| HSD | cl | r47015 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r47016 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r47017 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r47018 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r47019 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r47020 | 546 | 299.151 | first_order (no) | - |
| HSD | cl | r47021 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r47022 | 551 | 299.151 | first_order (no) | - |
| HSD | cl | r47023 | 551 | 299.151 | first_order (no) | - |
| MT | sv | b0 | 18413 | 0 | - | - |
| MT | sv | r90 | 474 | 299.315 | first_order (no) | friction (no) |
| MT | sv | b1 | 143 | 0 | - | - |
| MT | sv | r47000 | 473 | 299.29 | first_order (no) | linear (yes) |
| MT | sv | b2 | 144 | 0 | - | - |
| MT | sv | r47001 | 473 | 299.302 | first_order (no) | linear (yes) |
| MT | sv | b3 | 143 | 0 | - | - |
| MT | sv | r47002 | 474 | 299.302 | first_order (no) | linear (yes) |
| MT | sv | b4 | 144 | 0 | - | - |
| MT | sv | r47003 | 453 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b5 | 144 | 0 | - | - |
| MT | sv | r47004 | 453 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b6 | 144 | 0 | - | - |
| MT | sv | r47005 | 455 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b7 | 166 | 0 | - | - |
| MT | sv | r47006 | 459 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b8 | 164 | 0 | - | - |
| MT | sv | r47007 | 459 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b9 | 164 | 0 | - | - |
| MT | sv | r47008 | 461 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b10 | 164 | 0 | - | - |
| MT | sv | r47009 | 468 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b11 | 159 | 0 | - | - |
| MT | sv | r47010 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b12 | 159 | 0 | - | - |
| MT | sv | r47011 | 466 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b13 | 159 | 0 | - | - |
| MT | sv | r47012 | 464 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b14 | 153 | 0 | - | - |
| MT | sv | r47013 | 463 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b15 | 154 | 0 | - | - |
| MT | sv | r47014 | 465 | 299.148 | first_order (no) | linear (no) |
| MT | sv | b16 | 154 | 0 | - | - |
| MT | sv | r47015 | 476 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b17 | 149 | 0 | - | - |
| MT | sv | r47016 | 475 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b18 | 149 | 0 | - | - |
| MT | sv | r47017 | 475 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b19 | 149 | 0 | - | - |
| MT | sv | r47018 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b20 | 144 | 0 | - | - |
| MT | sv | r47019 | 482 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b21 | 144 | 0 | - | - |
| MT | sv | r47020 | 482 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b22 | 144 | 0 | - | - |
| MT | sv | r47021 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b23 | 163 | 0 | - | - |
| MT | sv | r47022 | 483 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b24 | 164 | 0 | - | - |
| MT | sv | r47023 | 484 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b25 | 128 | 0 | - | - |

Events: 354. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
