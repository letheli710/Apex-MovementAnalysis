# hsd_tel report

Inputs: 16 file(s); rows: 67555 (MT 45457, HSD 22096)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3936 teleport in stream ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` message.log:4999 teleport in stream ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` message.log:6048 teleport in stream ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` message.log:7028 teleport in stream ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` message.log:8171 teleport in stream ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_MORE` message.log:0 14 more teleport rows in ('MT', 'cl', 'cmd', 1, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` script.log:3579 teleport in stream ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` script.log:4581 teleport in stream ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` script.log:5580 teleport in stream ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` script.log:6574 teleport in stream ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` script.log:7573 teleport in stream ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_MORE` script.log:0 14 more teleport rows in ('HSD', 'cl', 'frame', None, 'eafc8644-a7f3-421e-afc6-f5fbf3ae272f')
- warning `W_TELEPORT` message.log:3745 teleport in stream ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_TELEPORT` message.log:4731 teleport in stream ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_TELEPORT` message.log:5710 teleport in stream ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_TELEPORT` message.log:6617 teleport in stream ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_TELEPORT` message.log:7594 teleport in stream ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_MORE` message.log:0 14 more teleport rows in ('MT', 'sv', 'cmd', 1, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')
- warning `W_TIME_BACKWARDS` script.log:716 t 26.2 -> 25.91022 in ('HSD', 'sv', 'evt', 1.0, 'b41bdb6e-3da5-40c5-99ca-49399a62eb4e')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3732 | 0 | - | - |
| MT | cl | r90 | 794 | 684.89 | first_order (no) | friction (no) |
| MT | cl | r2541 | 794 | 690.494 | first_order (no) | friction (no) |
| MT | cl | r2542 | 723 | 687.55 | first_order (no) | - |
| MT | cl | b1 | 367 | 0 | - | - |
| MT | cl | r2543 | 794 | 685.252 | first_order (no) | friction (no) |
| MT | cl | r2544 | 724 | 683.989 | first_order (no) | - |
| MT | cl | b2 | 551 | 0 | - | - |
| MT | cl | r2545 | 794 | 688.641 | first_order (no) | friction (no) |
| MT | cl | r2546 | 794 | 680.82 | first_order (no) | friction (no) |
| MT | cl | r2547 | 722 | 559.551 | first_order (no) | friction (no) |
| MT | cl | b3 | 183 | 0 | - | - |
| MT | cl | r2548 | 722 | 552.902 | first_order (no) | friction (no) |
| MT | cl | b4 | 183 | 0 | - | - |
| MT | cl | r2549 | 721 | 557.216 | first_order (no) | friction (no) |
| MT | cl | b5 | 184 | 0 | - | - |
| MT | cl | r2550 | 723 | 552.684 | first_order (no) | friction (no) |
| MT | cl | b6 | 167 | 0 | - | - |
| MT | cl | r2551 | 725 | 557.291 | first_order (no) | friction (no) |
| MT | cl | b7 | 178 | 0 | - | - |
| MT | cl | r2552 | 723 | 550.613 | first_order (no) | friction (no) |
| MT | cl | b8 | 183 | 0 | - | - |
| MT | cl | r2553 | 741 | 579.322 | first_order (yes) | - |
| MT | cl | b9 | 352 | 0 | - | - |
| MT | cl | r2554 | 793 | 573.374 | first_order (yes) | linear (no) |
| MT | cl | r2555 | 741 | 571.646 | first_order (yes) | friction (no) |
| MT | cl | b10 | 672 | 0 | - | - |
| MT | cl | r2556 | 794 | 584.645 | first_order (yes) | linear (no) |
| MT | cl | r2557 | 794 | 585.336 | first_order (yes) | linear (no) |
| MT | cl | r2558 | 794 | 584.682 | first_order (yes) | linear (no) |
| HSD | cl | r0 | 6711 | 0 | - | - |
| HSD | cl | r90 | 794 | 684.89 | first_order (no) | friction (no) |
| HSD | cl | r2541 | 794 | 690.494 | first_order (no) | friction (no) |
| HSD | cl | r2542 | 794 | 687.55 | first_order (no) | - |
| HSD | cl | r2543 | 794 | 685.252 | first_order (no) | friction (no) |
| HSD | cl | r2544 | 794 | 683.989 | first_order (no) | - |
| HSD | cl | r2545 | 794 | 688.641 | first_order (no) | friction (no) |
| HSD | cl | r2546 | 794 | 680.82 | first_order (no) | friction (no) |
| HSD | cl | r2547 | 794 | 559.551 | first_order (no) | linear (no) |
| HSD | cl | r2548 | 794 | 552.902 | first_order (no) | linear (no) |
| HSD | cl | r2549 | 794 | 557.216 | first_order (no) | linear (no) |
| HSD | cl | r2550 | 794 | 552.684 | first_order (no) | linear (no) |
| HSD | cl | r2551 | 794 | 557.291 | first_order (no) | linear (no) |
| HSD | cl | r2552 | 794 | 550.613 | first_order (no) | linear (no) |
| HSD | cl | r2553 | 794 | 579.322 | first_order (yes) | - |
| HSD | cl | r2554 | 794 | 573.374 | first_order (yes) | friction (no) |
| HSD | cl | r2555 | 794 | 571.646 | first_order (yes) | friction (no) |
| HSD | cl | r2556 | 794 | 584.645 | first_order (yes) | linear (no) |
| HSD | cl | r2557 | 794 | 585.336 | first_order (yes) | linear (no) |
| HSD | cl | r2558 | 794 | 584.682 | first_order (yes) | linear (no) |
| MT | sv | b0 | 3754 | 0 | - | - |
| MT | sv | r90 | 794 | 684.876 | first_order (no) | friction (no) |
| MT | sv | r2541 | 794 | 690.48 | first_order (no) | friction (no) |
| MT | sv | r2542 | 723 | 687.541 | first_order (no) | - |
| MT | sv | b1 | 367 | 0 | - | - |
| MT | sv | r2543 | 794 | 685.229 | first_order (no) | friction (no) |
| MT | sv | r2544 | 724 | 683.975 | first_order (no) | - |
| MT | sv | b2 | 551 | 0 | - | - |
| MT | sv | r2545 | 794 | 688.631 | first_order (no) | friction (no) |
| MT | sv | r2546 | 794 | 680.782 | first_order (no) | friction (no) |
| MT | sv | r2547 | 722 | 559.554 | first_order (no) | friction (no) |
| MT | sv | b3 | 183 | 0 | - | - |
| MT | sv | r2548 | 722 | 552.908 | first_order (no) | friction (no) |
| MT | sv | b4 | 183 | 0 | - | - |
| MT | sv | r2549 | 721 | 557.2 | first_order (no) | friction (no) |
| MT | sv | b5 | 184 | 0 | - | - |
| MT | sv | r2550 | 723 | 552.682 | first_order (no) | friction (no) |
| MT | sv | b6 | 167 | 0 | - | - |
| MT | sv | r2551 | 725 | 557.288 | first_order (no) | friction (no) |
| MT | sv | b7 | 178 | 0 | - | - |
| MT | sv | r2552 | 723 | 550.608 | first_order (no) | friction (no) |
| MT | sv | b8 | 183 | 0 | - | - |
| MT | sv | r2553 | 722 | 579.325 | first_order (yes) | - |
| MT | sv | b9 | 352 | 0 | - | - |
| MT | sv | r2554 | 793 | 573.374 | first_order (yes) | linear (no) |
| MT | sv | r2555 | 725 | 571.63 | first_order (yes) | linear (no) |
| MT | sv | b10 | 668 | 0 | - | - |
| MT | sv | r2556 | 794 | 584.645 | first_order (yes) | linear (no) |
| MT | sv | r2557 | 794 | 585.359 | first_order (yes) | linear (no) |
| MT | sv | r2558 | 794 | 584.688 | first_order (yes) | linear (no) |

Events: 375. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
