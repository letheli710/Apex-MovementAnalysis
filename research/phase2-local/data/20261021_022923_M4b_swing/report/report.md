# hsd_tel report

Inputs: 16 file(s); rows: 75122 (MT 49980, HSD 25082)

Validation: 0 error(s), 28 warning(s), 28 info

- warning `W_TELEPORT` message.log:3804 teleport in stream ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` message.log:4716 teleport in stream ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` message.log:5688 teleport in stream ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` message.log:6552 teleport in stream ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` message.log:7457 teleport in stream ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'cl', 'cmd', 1, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:3442 teleport in stream ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:4315 teleport in stream ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:5237 teleport in stream ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:6133 teleport in stream ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:7031 teleport in stream ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_MORE` script.log:0 21 more teleport rows in ('HSD', 'cl', 'frame', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:5561 teleport in stream ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:6451 teleport in stream ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:7356 teleport in stream ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:8252 teleport in stream ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` script.log:9084 teleport in stream ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_MORE` script.log:0 14 more teleport rows in ('HSD', 'cl', 'edge', None, '82bff98d-58a3-4ea6-ac09-ab1a39998114')
- warning `W_TELEPORT` message.log:3533 teleport in stream ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` message.log:4404 teleport in stream ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` message.log:5317 teleport in stream ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` message.log:6132 teleport in stream ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` message.log:6948 teleport in stream ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'sv', 'cmd', 1, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` script.log:829 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` script.log:838 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TELEPORT` script.log:847 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')
- warning `W_TIME_BACKWARDS` script.log:716 t 28.25 -> 28.00205 in ('HSD', 'sv', 'evt', 1.0, 'dbdd217c-ac66-439c-8f5d-8a54b1e7245c')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3495 | 0 | - | - |
| MT | cl | r90 | 721 | 621.153 | - | friction (yes) |
| MT | cl | r2501 | 721 | 610.603 | - | friction (yes) |
| MT | cl | r2502 | 658 | 595.145 | - | - |
| MT | cl | b1 | 166 | 0 | - | - |
| MT | cl | r2503 | 660 | 594.297 | - | - |
| MT | cl | b2 | 167 | 0 | - | - |
| MT | cl | r2504 | 660 | 595.351 | - | - |
| MT | cl | b3 | 166 | 0 | - | - |
| MT | cl | r2505 | 661 | 595.846 | - | - |
| MT | cl | b4 | 98 | 0 | - | - |
| MT | cl | r2506 | 672 | 597.738 | - | - |
| MT | cl | b5 | 174 | 0 | - | - |
| MT | cl | r2507 | 672 | 598.224 | - | - |
| MT | cl | b6 | 189 | 0 | - | - |
| MT | cl | r2508 | 653 | 596.994 | - | - |
| MT | cl | b7 | 190 | 0 | - | - |
| MT | cl | r2509 | 654 | 598.414 | - | - |
| MT | cl | b8 | 190 | 0 | - | - |
| MT | cl | r2510 | 670 | 596.498 | - | - |
| MT | cl | b9 | 174 | 0 | - | - |
| MT | cl | r2511 | 667 | 607.453 | linear (no) | friction (no) |
| MT | cl | b10 | 148 | 0 | - | - |
| MT | cl | r2512 | 665 | 606.676 | first_order (no) | friction (no) |
| MT | cl | b11 | 184 | 0 | - | - |
| MT | cl | r2513 | 655 | 610.211 | first_order (yes) | linear (no) |
| MT | cl | b12 | 178 | 0 | - | - |
| MT | cl | r2514 | 657 | 611.819 | first_order (yes) | linear (no) |
| MT | cl | b13 | 191 | 0 | - | - |
| MT | cl | r2515 | 656 | 609.133 | first_order (yes) | friction (no) |
| MT | cl | b14 | 190 | 0 | - | - |
| MT | cl | r2516 | 445 | 595.274 | - | - |
| MT | cl | b15 | 189 | 0 | - | - |
| MT | cl | r2517 | 445 | 594.697 | - | - |
| MT | cl | b16 | 189 | 0 | - | - |
| MT | cl | r2518 | 445 | 595.394 | - | - |
| MT | cl | b17 | 190 | 0 | - | - |
| MT | cl | r2519 | 445 | 596.415 | - | - |
| MT | cl | b18 | 190 | 0 | - | - |
| MT | cl | r2520 | 445 | 594.63 | - | - |
| MT | cl | b19 | 189 | 0 | - | - |
| MT | cl | r2521 | 477 | 597.726 | - | - |
| MT | cl | b20 | 190 | 0 | - | - |
| MT | cl | r2522 | 476 | 598.583 | - | - |
| MT | cl | b21 | 189 | 0 | - | - |
| MT | cl | r2523 | 475 | 598.032 | - | - |
| MT | cl | b22 | 190 | 0 | - | - |
| MT | cl | r2524 | 476 | 596.072 | - | - |
| MT | cl | b23 | 185 | 0 | - | - |
| MT | cl | r2525 | 476 | 599.108 | - | - |
| MT | cl | b24 | 151 | 0 | - | - |
| HSD | cl | r0 | 7724 | 0 | - | - |
| HSD | cl | r90 | 721 | 621.153 | - | friction (yes) |
| HSD | cl | r2501 | 721 | 610.603 | - | friction (yes) |
| HSD | cl | r2502 | 721 | 595.145 | - | - |
| HSD | cl | r2503 | 721 | 594.297 | - | - |
| HSD | cl | r2504 | 721 | 595.351 | - | - |
| HSD | cl | r2505 | 721 | 595.846 | - | - |
| HSD | cl | r2506 | 727 | 597.738 | - | - |
| HSD | cl | r2507 | 727 | 598.224 | - | - |
| HSD | cl | r2508 | 727 | 596.994 | - | - |
| HSD | cl | r2509 | 727 | 598.414 | - | - |
| HSD | cl | r2510 | 727 | 596.498 | - | - |
| HSD | cl | r2511 | 727 | 607.453 | linear (no) | linear (no) |
| HSD | cl | r2512 | 727 | 606.676 | first_order (no) | linear (no) |
| HSD | cl | r2513 | 727 | 610.211 | first_order (yes) | linear (no) |
| HSD | cl | r2514 | 727 | 611.819 | first_order (yes) | linear (no) |
| HSD | cl | r2515 | 727 | 609.133 | first_order (yes) | linear (no) |
| HSD | cl | r2516 | 518 | 595.274 | - | - |
| HSD | cl | r2517 | 518 | 594.697 | - | - |
| HSD | cl | r2518 | 518 | 595.394 | - | - |
| HSD | cl | r2519 | 518 | 596.415 | - | - |
| HSD | cl | r2520 | 518 | 594.63 | - | - |
| HSD | cl | r2521 | 548 | 597.726 | - | - |
| HSD | cl | r2522 | 548 | 598.583 | - | - |
| HSD | cl | r2523 | 548 | 598.032 | - | - |
| HSD | cl | r2524 | 548 | 596.072 | - | - |
| HSD | cl | r2525 | 548 | 599.108 | - | - |
| MT | sv | b0 | 3507 | 0 | - | - |
| MT | sv | r90 | 721 | 621.145 | - | friction (yes) |
| MT | sv | r2501 | 721 | 610.623 | - | friction (yes) |
| MT | sv | r2502 | 648 | 595.144 | - | - |
| MT | sv | b1 | 166 | 0 | - | - |
| MT | sv | r2503 | 648 | 594.289 | - | - |
| MT | sv | b2 | 167 | 0 | - | - |
| MT | sv | r2504 | 649 | 595.346 | - | - |
| MT | sv | b3 | 166 | 0 | - | - |
| MT | sv | r2505 | 649 | 595.838 | - | - |
| MT | sv | b4 | 98 | 0 | - | - |
| MT | sv | r2506 | 655 | 597.697 | - | - |
| MT | sv | b5 | 174 | 0 | - | - |
| MT | sv | r2507 | 654 | 598.21 | - | - |
| MT | sv | b6 | 189 | 0 | - | - |
| MT | sv | r2508 | 653 | 596.94 | - | - |
| MT | sv | b7 | 190 | 0 | - | - |
| MT | sv | r2509 | 654 | 598.379 | - | - |
| MT | sv | b8 | 190 | 0 | - | - |
| MT | sv | r2510 | 654 | 596.494 | - | - |
| MT | sv | b9 | 174 | 0 | - | - |
| MT | sv | r2511 | 667 | 607.45 | linear (no) | friction (no) |
| MT | sv | b10 | 148 | 0 | - | - |
| MT | sv | r2512 | 665 | 606.676 | first_order (no) | friction (no) |
| MT | sv | b11 | 184 | 0 | - | - |
| MT | sv | r2513 | 655 | 610.192 | first_order (yes) | linear (no) |
| MT | sv | b12 | 178 | 0 | - | - |
| MT | sv | r2514 | 657 | 611.803 | first_order (yes) | linear (no) |
| MT | sv | b13 | 191 | 0 | - | - |
| MT | sv | r2515 | 656 | 609.135 | first_order (yes) | friction (no) |
| MT | sv | b14 | 190 | 0 | - | - |
| MT | sv | r2516 | 445 | 595.269 | - | - |
| MT | sv | b15 | 189 | 0 | - | - |
| MT | sv | r2517 | 445 | 594.672 | - | - |
| MT | sv | b16 | 189 | 0 | - | - |
| MT | sv | r2518 | 445 | 595.379 | - | - |
| MT | sv | b17 | 190 | 0 | - | - |
| MT | sv | r2519 | 445 | 596.379 | - | - |
| MT | sv | b18 | 190 | 0 | - | - |
| MT | sv | r2520 | 444 | 594.613 | - | - |
| MT | sv | b19 | 189 | 0 | - | - |
| MT | sv | r2521 | 477 | 597.719 | - | - |
| MT | sv | b20 | 190 | 0 | - | - |
| MT | sv | r2522 | 476 | 598.538 | - | - |
| MT | sv | b21 | 189 | 0 | - | - |
| MT | sv | r2523 | 475 | 597.997 | - | - |
| MT | sv | b22 | 190 | 0 | - | - |
| MT | sv | r2524 | 476 | 596.05 | - | - |
| MT | sv | b23 | 185 | 0 | - | - |
| MT | sv | r2525 | 476 | 599.085 | - | - |
| MT | sv | b24 | 147 | 0 | - | - |

Events: 340. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
