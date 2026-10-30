# hsd_tel report

Inputs: 17 file(s); rows: 80606 (MT 51966, HSD 28638)

Validation: 0 error(s), 24 warning(s), 6 info

- warning `W_TELEPORT` message.log:3947 teleport in stream ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` message.log:4633 teleport in stream ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` message.log:5319 teleport in stream ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` message.log:6035 teleport in stream ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` message.log:6784 teleport in stream ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_MORE` message.log:0 28 more teleport rows in ('MT', 'cl', 'cmd', 1, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` script.1.log:3593 teleport in stream ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` script.1.log:4852 teleport in stream ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` script.1.log:6114 teleport in stream ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` script.1.log:7406 teleport in stream ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` script.1.log:8778 teleport in stream ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_MORE` script.1.log:0 28 more teleport rows in ('HSD', 'cl', 'frame', None, 'e224b635-e088-4997-87c6-79592f37733c')
- warning `W_TELEPORT` message.log:3739 teleport in stream ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` message.log:4379 teleport in stream ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` message.log:5019 teleport in stream ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` message.log:5691 teleport in stream ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` message.log:6390 teleport in stream ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_MORE` message.log:0 28 more teleport rows in ('MT', 'sv', 'cmd', 1, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` script.log:914 teleport in stream ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` script.log:926 teleport in stream ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` script.log:936 teleport in stream ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` script.log:978 teleport in stream ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TELEPORT` script.log:990 teleport in stream ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')
- warning `W_TIME_BACKWARDS` script.log:719 t 24.05 -> 23.89482 in ('HSD', 'sv', 'evt', 1.0, '474a638c-a720-4ba3-9380-dc9ca923ea02')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3369 | 0 | - | - |
| MT | cl | r90 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 165 | 0 | - | - |
| MT | cl | r9100 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b2 | 169 | 0 | - | - |
| MT | cl | r9101 | 474 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b3 | 194 | 0 | - | - |
| MT | cl | r9102 | 525 | 199.77 | first_order (yes) | linear (yes) |
| MT | cl | b4 | 172 | 0 | - | - |
| MT | cl | r9103 | 521 | 199.764 | first_order (yes) | linear (yes) |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r9104 | 494 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b6 | 174 | 0 | - | - |
| MT | cl | r9105 | 496 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b7 | 174 | 0 | - | - |
| MT | cl | r9106 | 471 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b8 | 168 | 0 | - | - |
| MT | cl | r9107 | 477 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b9 | 194 | 0 | - | - |
| MT | cl | r9108 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b10 | 167 | 0 | - | - |
| MT | cl | r9109 | 441 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b11 | 166 | 0 | - | - |
| MT | cl | r9110 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b12 | 196 | 0 | - | - |
| MT | cl | r9111 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b13 | 168 | 0 | - | - |
| MT | cl | r9112 | 468 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b14 | 148 | 0 | - | - |
| MT | cl | r9113 | 461 | 299.119 | first_order (no) | friction (no) |
| MT | cl | b15 | 169 | 0 | - | - |
| MT | cl | r9114 | 514 | 299.707 | first_order (no) | linear (yes) |
| MT | cl | b16 | 185 | 0 | - | - |
| MT | cl | r9115 | 517 | 299.714 | first_order (no) | linear (yes) |
| MT | cl | b17 | 156 | 0 | - | - |
| MT | cl | r9116 | 523 | 389.404 | first_order (no) | linear (no) |
| MT | cl | b18 | 155 | 0 | - | - |
| MT | cl | r9117 | 522 | 299.71 | first_order (no) | linear (yes) |
| MT | cl | b19 | 177 | 0 | - | - |
| MT | cl | r9118 | 523 | 389.402 | first_order (no) | linear (yes) |
| MT | cl | b20 | 175 | 0 | - | - |
| MT | cl | r9119 | 526 | 389.407 | first_order (no) | friction (no) |
| MT | cl | b21 | 172 | 0 | - | - |
| MT | cl | r9120 | 533 | 389.408 | first_order (no) | friction (no) |
| MT | cl | b22 | 166 | 0 | - | - |
| MT | cl | r9121 | 534 | 389.406 | first_order (no) | friction (no) |
| MT | cl | b23 | 195 | 0 | - | - |
| MT | cl | r9122 | 539 | 299.706 | first_order (no) | linear (yes) |
| MT | cl | b24 | 183 | 0 | - | - |
| MT | cl | r9123 | 539 | 299.705 | first_order (no) | linear (yes) |
| MT | cl | b25 | 184 | 0 | - | - |
| MT | cl | r9124 | 537 | 299.085 | first_order (no) | friction (no) |
| MT | cl | b26 | 189 | 0 | - | - |
| MT | cl | r9125 | 540 | 299.703 | first_order (no) | linear (yes) |
| MT | cl | b27 | 172 | 0 | - | - |
| MT | cl | r9126 | 547 | 299.702 | first_order (no) | linear (yes) |
| MT | cl | b28 | 181 | 0 | - | - |
| MT | cl | r9127 | 532 | 389.407 | first_order (no) | friction (no) |
| MT | cl | b29 | 167 | 0 | - | - |
| MT | cl | r9128 | 534 | 389.406 | first_order (no) | friction (no) |
| MT | cl | b30 | 195 | 0 | - | - |
| MT | cl | r9129 | 537 | 389.406 | first_order (no) | friction (no) |
| MT | cl | b31 | 192 | 0 | - | - |
| MT | cl | r9130 | 541 | 299.71 | first_order (no) | linear (yes) |
| MT | cl | b32 | 188 | 0 | - | - |
| MT | cl | r9131 | 538 | 299.71 | first_order (no) | linear (yes) |
| MT | cl | b33 | 151 | 0 | - | - |
| HSD | cl | r0 | 9118 | 0 | - | - |
| HSD | cl | r90 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9100 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9101 | 541 | 299.152 | first_order (no) | - |
| HSD | cl | r9102 | 594 | 199.77 | first_order (yes) | - |
| HSD | cl | r9103 | 591 | 199.764 | first_order (yes) | - |
| HSD | cl | r9104 | 563 | 299.151 | first_order (no) | - |
| HSD | cl | r9105 | 564 | 299.152 | first_order (no) | - |
| HSD | cl | r9106 | 540 | 299.152 | first_order (no) | - |
| HSD | cl | r9107 | 543 | 299.152 | first_order (no) | - |
| HSD | cl | r9108 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r9109 | 540 | 299.152 | first_order (no) | - |
| HSD | cl | r9110 | 541 | 299.151 | first_order (no) | - |
| HSD | cl | r9111 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9112 | 539 | 299.151 | first_order (no) | - |
| HSD | cl | r9113 | 533 | 299.119 | first_order (no) | - |
| HSD | cl | r9114 | 582 | 299.707 | first_order (no) | - |
| HSD | cl | r9115 | 585 | 299.714 | first_order (no) | - |
| HSD | cl | r9116 | 575 | 389.404 | - | linear (no) |
| HSD | cl | r9117 | 590 | 299.71 | first_order (no) | - |
| HSD | cl | r9118 | 592 | 389.402 | - | linear (yes) |
| HSD | cl | r9119 | 595 | 389.407 | - | friction (no) |
| HSD | cl | r9120 | 601 | 389.408 | - | friction (no) |
| HSD | cl | r9121 | 603 | 389.406 | - | friction (no) |
| HSD | cl | r9122 | 603 | 299.706 | first_order (no) | - |
| HSD | cl | r9123 | 607 | 299.705 | first_order (no) | - |
| HSD | cl | r9124 | 603 | 299.085 | first_order (no) | - |
| HSD | cl | r9125 | 611 | 299.703 | first_order (no) | - |
| HSD | cl | r9126 | 616 | 299.702 | first_order (no) | - |
| HSD | cl | r9127 | 600 | 389.407 | - | friction (no) |
| HSD | cl | r9128 | 603 | 389.406 | - | friction (no) |
| HSD | cl | r9129 | 606 | 389.406 | - | friction (no) |
| HSD | cl | r9130 | 609 | 299.71 | first_order (no) | - |
| HSD | cl | r9131 | 606 | 299.71 | first_order (no) | - |
| MT | sv | b0 | 3381 | 0 | - | - |
| MT | sv | r90 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 165 | 0 | - | - |
| MT | sv | r9100 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b2 | 169 | 0 | - | - |
| MT | sv | r9101 | 474 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b3 | 194 | 0 | - | - |
| MT | sv | r9102 | 525 | 199.77 | first_order (yes) | linear (yes) |
| MT | sv | b4 | 172 | 0 | - | - |
| MT | sv | r9103 | 521 | 199.764 | first_order (yes) | linear (yes) |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r9104 | 494 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b6 | 174 | 0 | - | - |
| MT | sv | r9105 | 496 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b7 | 174 | 0 | - | - |
| MT | sv | r9106 | 471 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b8 | 168 | 0 | - | - |
| MT | sv | r9107 | 477 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b9 | 194 | 0 | - | - |
| MT | sv | r9108 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b10 | 167 | 0 | - | - |
| MT | sv | r9109 | 441 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b11 | 166 | 0 | - | - |
| MT | sv | r9110 | 473 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b12 | 196 | 0 | - | - |
| MT | sv | r9111 | 470 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b13 | 168 | 0 | - | - |
| MT | sv | r9112 | 468 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b14 | 148 | 0 | - | - |
| MT | sv | r9113 | 461 | 299.119 | first_order (no) | friction (no) |
| MT | sv | b15 | 169 | 0 | - | - |
| MT | sv | r9114 | 514 | 299.707 | first_order (no) | linear (yes) |
| MT | sv | b16 | 185 | 0 | - | - |
| MT | sv | r9115 | 517 | 299.714 | first_order (no) | linear (yes) |
| MT | sv | b17 | 156 | 0 | - | - |
| MT | sv | r9116 | 523 | 389.404 | first_order (no) | linear (no) |
| MT | sv | b18 | 155 | 0 | - | - |
| MT | sv | r9117 | 522 | 299.71 | first_order (no) | linear (yes) |
| MT | sv | b19 | 177 | 0 | - | - |
| MT | sv | r9118 | 523 | 389.402 | first_order (no) | linear (yes) |
| MT | sv | b20 | 175 | 0 | - | - |
| MT | sv | r9119 | 526 | 389.407 | first_order (no) | friction (no) |
| MT | sv | b21 | 172 | 0 | - | - |
| MT | sv | r9120 | 533 | 389.408 | first_order (no) | friction (no) |
| MT | sv | b22 | 166 | 0 | - | - |
| MT | sv | r9121 | 534 | 389.406 | first_order (no) | friction (no) |
| MT | sv | b23 | 195 | 0 | - | - |
| MT | sv | r9122 | 539 | 299.706 | first_order (no) | linear (yes) |
| MT | sv | b24 | 183 | 0 | - | - |
| MT | sv | r9123 | 539 | 299.705 | first_order (no) | linear (yes) |
| MT | sv | b25 | 184 | 0 | - | - |
| MT | sv | r9124 | 537 | 299.085 | first_order (no) | friction (no) |
| MT | sv | b26 | 189 | 0 | - | - |
| MT | sv | r9125 | 540 | 299.703 | first_order (no) | linear (yes) |
| MT | sv | b27 | 172 | 0 | - | - |
| MT | sv | r9126 | 547 | 299.702 | first_order (no) | linear (yes) |
| MT | sv | b28 | 181 | 0 | - | - |
| MT | sv | r9127 | 532 | 389.407 | first_order (no) | friction (no) |
| MT | sv | b29 | 167 | 0 | - | - |
| MT | sv | r9128 | 534 | 389.406 | first_order (no) | friction (no) |
| MT | sv | b30 | 195 | 0 | - | - |
| MT | sv | r9129 | 537 | 389.406 | first_order (no) | friction (no) |
| MT | sv | b31 | 192 | 0 | - | - |
| MT | sv | r9130 | 541 | 299.71 | first_order (no) | linear (yes) |
| MT | sv | b32 | 188 | 0 | - | - |
| MT | sv | r9131 | 538 | 299.71 | first_order (no) | linear (yes) |
| MT | sv | b33 | 142 | 0 | - | - |

Events: 688. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
