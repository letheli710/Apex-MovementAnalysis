# hsd_tel report

Inputs: 16 file(s); rows: 35065 (MT 23574, HSD 11489)

Validation: 0 error(s), 20 warning(s), 3 info

- warning `W_TELEPORT` message.log:3613 teleport in stream ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` message.log:3909 teleport in stream ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` message.log:4834 teleport in stream ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` message.log:5658 teleport in stream ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` message.log:6488 teleport in stream ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_MORE` message.log:0 6 more teleport rows in ('MT', 'cl', 'cmd', 1, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` script.log:3263 teleport in stream ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` script.log:3531 teleport in stream ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` script.log:4074 teleport in stream ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` script.log:4882 teleport in stream ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` script.log:5690 teleport in stream ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'cl', 'frame', None, '430d33c0-b8ea-4ce0-89a0-ae7da55dcf7d')
- warning `W_TELEPORT` message.log:3399 teleport in stream ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TELEPORT` message.log:4235 teleport in stream ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TELEPORT` message.log:5036 teleport in stream ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TELEPORT` message.log:5837 teleport in stream ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TELEPORT` message.log:6637 teleport in stream ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_MORE` message.log:0 5 more teleport rows in ('MT', 'sv', 'cmd', 1, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TELEPORT` script.log:767 teleport in stream ('HSD', 'sv', 'evt', 1.0, '6c36ba7d-067e-4361-9d6e-afabb1656200')
- warning `W_TIME_BACKWARDS` script.log:713 t 22.25 -> 22.09472 in ('HSD', 'sv', 'evt', 1.0, '6c36ba7d-067e-4361-9d6e-afabb1656200')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4882 | 0 | - | - |
| MT | cl | r90 | 663 | 573.793 | - | linear (yes) |
| MT | cl | r2301 | 612 | 575.747 | - | linear (yes) |
| MT | cl | r2302 | 612 | 575.693 | - | linear (yes) |
| MT | cl | r2303 | 612 | 573.932 | - | linear (yes) |
| MT | cl | r2304 | 612 | 575.706 | - | linear (yes) |
| MT | cl | r2305 | 696 | 686.787 | - | linear (yes) |
| MT | cl | r2306 | 696 | 687.369 | - | linear (yes) |
| MT | cl | r2307 | 696 | 687.533 | - | linear (yes) |
| MT | cl | r2308 | 696 | 687.743 | - | linear (yes) |
| MT | cl | r2309 | 696 | 687.397 | - | linear (yes) |
| HSD | cl | r0 | 4865 | 0 | - | - |
| HSD | cl | r90 | 612 | 573.793 | - | linear (yes) |
| HSD | cl | r2301 | 612 | 575.747 | - | linear (yes) |
| HSD | cl | r2302 | 612 | 575.693 | - | linear (yes) |
| HSD | cl | r2303 | 612 | 573.932 | - | linear (yes) |
| HSD | cl | r2304 | 612 | 575.706 | - | linear (yes) |
| HSD | cl | r2305 | 696 | 686.787 | - | linear (yes) |
| HSD | cl | r2306 | 696 | 687.369 | - | linear (yes) |
| HSD | cl | r2307 | 696 | 687.533 | - | linear (yes) |
| HSD | cl | r2308 | 696 | 687.743 | - | linear (yes) |
| HSD | cl | r2309 | 696 | 687.397 | - | linear (yes) |
| MT | sv | b0 | 4883 | 0 | - | - |
| MT | sv | r90 | 639 | 573.793 | - | linear (yes) |
| MT | sv | r2301 | 612 | 575.747 | - | linear (yes) |
| MT | sv | r2302 | 612 | 575.693 | - | linear (yes) |
| MT | sv | r2303 | 612 | 573.932 | - | linear (yes) |
| MT | sv | r2304 | 612 | 575.706 | - | linear (yes) |
| MT | sv | r2305 | 696 | 686.785 | - | linear (yes) |
| MT | sv | r2306 | 696 | 687.369 | - | linear (yes) |
| MT | sv | r2307 | 696 | 687.533 | - | linear (yes) |
| MT | sv | r2308 | 696 | 687.743 | - | linear (yes) |
| MT | sv | r2309 | 696 | 687.397 | - | linear (yes) |

Events: 82. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
