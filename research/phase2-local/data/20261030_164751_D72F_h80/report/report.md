# hsd_tel report

Inputs: 18 file(s); rows: 115449 (MT 75482, HSD 39965)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:18353 teleport in stream ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` message.log:19049 teleport in stream ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` message.log:19737 teleport in stream ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` message.log:20425 teleport in stream ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` message.log:21103 teleport in stream ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` script.2.log:17999 teleport in stream ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` script.2.log:19248 teleport in stream ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` script.2.log:20498 teleport in stream ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` script.2.log:21749 teleport in stream ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` script.2.log:22999 teleport in stream ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_MORE` script.2.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, '30f1660a-d497-4c95-9dcd-7c15d1b4ef40')
- warning `W_TELEPORT` message.log:18118 teleport in stream ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_TELEPORT` message.log:18754 teleport in stream ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_TELEPORT` message.log:19388 teleport in stream ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_TELEPORT` message.log:20021 teleport in stream ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_TELEPORT` message.log:20641 teleport in stream ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')
- warning `W_TIME_BACKWARDS` script.log:714 t 22.1 -> 22.06985 in ('HSD', 'sv', 'evt', 1.0, '3ef59a01-1c0a-4c1a-bd23-a912bc4e1bae')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 17753 | 0 | - | - |
| MT | cl | r90 | 490 | 299.242 | first_order (no) | linear (no) |
| MT | cl | b1 | 143 | 0 | - | - |
| MT | cl | r44000 | 487 | 299.254 | first_order (no) | linear (yes) |
| MT | cl | b2 | 145 | 0 | - | - |
| MT | cl | r44001 | 487 | 299.254 | first_order (no) | linear (yes) |
| MT | cl | b3 | 145 | 0 | - | - |
| MT | cl | r44002 | 474 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b4 | 145 | 0 | - | - |
| MT | cl | r44003 | 472 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b5 | 145 | 0 | - | - |
| MT | cl | r44004 | 473 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b6 | 145 | 0 | - | - |
| MT | cl | r44005 | 477 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b7 | 165 | 0 | - | - |
| MT | cl | r44006 | 478 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b8 | 166 | 0 | - | - |
| MT | cl | r44007 | 471 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b9 | 166 | 0 | - | - |
| MT | cl | r44008 | 482 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b10 | 162 | 0 | - | - |
| MT | cl | r44009 | 480 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b11 | 162 | 0 | - | - |
| MT | cl | r44010 | 478 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b12 | 162 | 0 | - | - |
| MT | cl | r44011 | 483 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b13 | 158 | 0 | - | - |
| MT | cl | r44012 | 486 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b14 | 158 | 0 | - | - |
| MT | cl | r44013 | 485 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b15 | 158 | 0 | - | - |
| MT | cl | r44014 | 491 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b16 | 154 | 0 | - | - |
| MT | cl | r44015 | 495 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b17 | 154 | 0 | - | - |
| MT | cl | r44016 | 493 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b18 | 154 | 0 | - | - |
| MT | cl | r44017 | 498 | 299.044 | first_order (no) | linear (no) |
| MT | cl | b19 | 150 | 0 | - | - |
| MT | cl | r44018 | 497 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b20 | 149 | 0 | - | - |
| MT | cl | r44019 | 496 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b21 | 150 | 0 | - | - |
| MT | cl | r44020 | 508 | 299.044 | first_order (no) | friction (no) |
| MT | cl | b22 | 145 | 0 | - | - |
| MT | cl | r44021 | 506 | 299.044 | first_order (no) | friction (no) |
| MT | cl | b23 | 145 | 0 | - | - |
| MT | cl | r44022 | 504 | 299.036 | first_order (no) | linear (no) |
| MT | cl | b24 | 145 | 0 | - | - |
| MT | cl | r44023 | 517 | 299.044 | first_order (no) | friction (no) |
| MT | cl | b25 | 165 | 0 | - | - |
| MT | cl | r44024 | 514 | 299.044 | first_order (no) | friction (no) |
| MT | cl | b26 | 165 | 0 | - | - |
| MT | cl | r44025 | 512 | 299.036 | first_order (no) | friction (no) |
| MT | cl | b27 | 165 | 0 | - | - |
| MT | cl | r44026 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b28 | 144 | 0 | - | - |
| MT | cl | r44027 | 463 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b29 | 144 | 0 | - | - |
| MT | cl | r44028 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b30 | 159 | 0 | - | - |
| MT | cl | r44029 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b31 | 126 | 0 | - | - |
| HSD | cl | r0 | 22475 | 0 | - | - |
| HSD | cl | r90 | 545 | 299.242 | first_order (no) | - |
| HSD | cl | r44000 | 545 | 299.254 | first_order (no) | - |
| HSD | cl | r44001 | 545 | 299.254 | first_order (no) | - |
| HSD | cl | r44002 | 545 | 299.044 | first_order (no) | - |
| HSD | cl | r44003 | 545 | 299.044 | first_order (no) | - |
| HSD | cl | r44004 | 545 | 299.044 | first_order (no) | - |
| HSD | cl | r44005 | 549 | 299.044 | first_order (no) | - |
| HSD | cl | r44006 | 549 | 299.036 | first_order (no) | - |
| HSD | cl | r44007 | 549 | 299.036 | first_order (no) | - |
| HSD | cl | r44008 | 553 | 299.044 | first_order (no) | - |
| HSD | cl | r44009 | 553 | 299.044 | first_order (no) | - |
| HSD | cl | r44010 | 553 | 299.044 | first_order (no) | - |
| HSD | cl | r44011 | 557 | 299.036 | first_order (no) | - |
| HSD | cl | r44012 | 557 | 299.044 | first_order (no) | - |
| HSD | cl | r44013 | 557 | 299.044 | first_order (no) | - |
| HSD | cl | r44014 | 561 | 299.036 | first_order (no) | - |
| HSD | cl | r44015 | 561 | 299.044 | first_order (no) | - |
| HSD | cl | r44016 | 561 | 299.044 | first_order (no) | - |
| HSD | cl | r44017 | 565 | 299.044 | first_order (no) | - |
| HSD | cl | r44018 | 565 | 299.036 | first_order (no) | - |
| HSD | cl | r44019 | 565 | 299.036 | first_order (no) | - |
| HSD | cl | r44020 | 570 | 299.044 | first_order (no) | - |
| HSD | cl | r44021 | 570 | 299.044 | first_order (no) | - |
| HSD | cl | r44022 | 570 | 299.036 | first_order (no) | - |
| HSD | cl | r44023 | 575 | 299.044 | first_order (no) | - |
| HSD | cl | r44024 | 575 | 299.044 | first_order (no) | - |
| HSD | cl | r44025 | 575 | 299.036 | first_order (no) | - |
| HSD | cl | r44026 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r44027 | 521 | 299.151 | first_order (no) | - |
| HSD | cl | r44028 | 531 | 299.151 | first_order (no) | - |
| HSD | cl | r44029 | 531 | 299.151 | first_order (no) | - |
| MT | sv | b0 | 17755 | 0 | - | - |
| MT | sv | r90 | 490 | 299.242 | first_order (no) | linear (no) |
| MT | sv | b1 | 143 | 0 | - | - |
| MT | sv | r44000 | 487 | 299.254 | first_order (no) | linear (yes) |
| MT | sv | b2 | 145 | 0 | - | - |
| MT | sv | r44001 | 487 | 299.254 | first_order (no) | linear (yes) |
| MT | sv | b3 | 145 | 0 | - | - |
| MT | sv | r44002 | 474 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b4 | 145 | 0 | - | - |
| MT | sv | r44003 | 472 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b5 | 145 | 0 | - | - |
| MT | sv | r44004 | 473 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b6 | 145 | 0 | - | - |
| MT | sv | r44005 | 477 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b7 | 165 | 0 | - | - |
| MT | sv | r44006 | 478 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b8 | 166 | 0 | - | - |
| MT | sv | r44007 | 471 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b9 | 166 | 0 | - | - |
| MT | sv | r44008 | 482 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b10 | 162 | 0 | - | - |
| MT | sv | r44009 | 480 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b11 | 162 | 0 | - | - |
| MT | sv | r44010 | 478 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b12 | 162 | 0 | - | - |
| MT | sv | r44011 | 483 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b13 | 158 | 0 | - | - |
| MT | sv | r44012 | 486 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b14 | 158 | 0 | - | - |
| MT | sv | r44013 | 485 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b15 | 158 | 0 | - | - |
| MT | sv | r44014 | 491 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b16 | 154 | 0 | - | - |
| MT | sv | r44015 | 495 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b17 | 154 | 0 | - | - |
| MT | sv | r44016 | 493 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b18 | 154 | 0 | - | - |
| MT | sv | r44017 | 498 | 299.044 | first_order (no) | linear (no) |
| MT | sv | b19 | 150 | 0 | - | - |
| MT | sv | r44018 | 497 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b20 | 149 | 0 | - | - |
| MT | sv | r44019 | 496 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b21 | 150 | 0 | - | - |
| MT | sv | r44020 | 508 | 299.044 | first_order (no) | friction (no) |
| MT | sv | b22 | 145 | 0 | - | - |
| MT | sv | r44021 | 506 | 299.044 | first_order (no) | friction (no) |
| MT | sv | b23 | 145 | 0 | - | - |
| MT | sv | r44022 | 504 | 299.036 | first_order (no) | linear (no) |
| MT | sv | b24 | 145 | 0 | - | - |
| MT | sv | r44023 | 517 | 299.044 | first_order (no) | friction (no) |
| MT | sv | b25 | 165 | 0 | - | - |
| MT | sv | r44024 | 514 | 299.044 | first_order (no) | friction (no) |
| MT | sv | b26 | 165 | 0 | - | - |
| MT | sv | r44025 | 512 | 299.036 | first_order (no) | friction (no) |
| MT | sv | b27 | 165 | 0 | - | - |
| MT | sv | r44026 | 462 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b28 | 144 | 0 | - | - |
| MT | sv | r44027 | 463 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b29 | 144 | 0 | - | - |
| MT | sv | r44028 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b30 | 159 | 0 | - | - |
| MT | sv | r44029 | 478 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b31 | 118 | 0 | - | - |

Events: 398. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
