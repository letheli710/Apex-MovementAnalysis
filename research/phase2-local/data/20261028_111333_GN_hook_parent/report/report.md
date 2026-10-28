# hsd_tel report

Inputs: 17 file(s); rows: 67896 (MT 45586, HSD 22308)

Validation: 0 error(s), 25 warning(s), 2 info

- warning `W_TELEPORT` message.log:17936 teleport in stream ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` message.log:18694 teleport in stream ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` message.log:19513 teleport in stream ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` message.log:20338 teleport in stream ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` message.log:21168 teleport in stream ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:17542 teleport in stream ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:18692 teleport in stream ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:19861 teleport in stream ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:21019 teleport in stream ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:22304 teleport in stream ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_MORE` script.1.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:18271 teleport in stream ('HSD', 'cl', 'edge', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.1.log:20580 teleport in stream ('HSD', 'cl', 'edge', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` script.log:896 teleport in stream ('HSD', 'cl', 'edge', None, '3997d768-5b59-4189-ab62-80fc09b0c057')
- warning `W_TELEPORT` message.log:17670 teleport in stream ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` message.log:18343 teleport in stream ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` message.log:19020 teleport in stream ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` message.log:19686 teleport in stream ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` message.log:20419 teleport in stream ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` script.log:782 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` script.log:855 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TELEPORT` script.log:933 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')
- warning `W_TIME_BACKWARDS` script.log:715 t 29.95 -> 29.6437 in ('HSD', 'sv', 'evt', 1.0, 'f7a473b7-cd53-4e50-887d-603b92a0ddd1')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 18582 | 0 | - | - |
| MT | cl | r90 | 481 | 572.853 | linear (yes) | - |
| MT | cl | r22001 | 481 | 574.562 | linear (yes) | - |
| MT | cl | r22002 | 481 | 573.557 | linear (yes) | - |
| MT | cl | r22003 | 541 | 511.808 | linear (no) | linear (yes) |
| MT | cl | r22004 | 541 | 521.456 | linear (no) | linear (yes) |
| MT | cl | r22005 | 661 | 418.759 | first_order (no) | linear (yes) |
| MT | cl | r22006 | 487 | 854.466 | - | - |
| HSD | cl | r0 | 18553 | 0 | - | - |
| HSD | cl | r90 | 481 | 572.853 | linear (yes) | - |
| HSD | cl | r22001 | 481 | 574.562 | linear (yes) | - |
| HSD | cl | r22002 | 481 | 573.557 | linear (yes) | - |
| HSD | cl | r22003 | 541 | 511.808 | linear (no) | linear (yes) |
| HSD | cl | r22004 | 541 | 521.456 | linear (no) | linear (yes) |
| HSD | cl | r22005 | 661 | 418.759 | first_order (no) | linear (yes) |
| HSD | cl | r22006 | 487 | 854.466 | - | - |
| MT | sv | b0 | 18586 | 0 | - | - |
| MT | sv | r90 | 481 | 572.851 | linear (yes) | - |
| MT | sv | r22001 | 481 | 574.558 | linear (yes) | - |
| MT | sv | r22002 | 481 | 573.546 | linear (yes) | - |
| MT | sv | r22003 | 541 | 511.808 | linear (no) | linear (yes) |
| MT | sv | r22004 | 541 | 521.456 | linear (no) | linear (yes) |
| MT | sv | r22005 | 661 | 418.759 | first_order (no) | linear (yes) |
| MT | sv | r22006 | 487 | 854.462 | - | - |

Events: 86. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
