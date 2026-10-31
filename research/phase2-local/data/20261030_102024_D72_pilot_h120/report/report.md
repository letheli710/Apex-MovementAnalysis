# hsd_tel report

Inputs: 16 file(s); rows: 40827 (MT 26371, HSD 14454)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3567 teleport in stream ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` message.log:4380 teleport in stream ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` message.log:5189 teleport in stream ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` message.log:5963 teleport in stream ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` message.log:6762 teleport in stream ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'cl', 'cmd', 1, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` script.log:3181 teleport in stream ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` script.log:4640 teleport in stream ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` script.log:6098 teleport in stream ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` script.log:7528 teleport in stream ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` script.log:8995 teleport in stream ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_MORE` script.log:0 9 more teleport rows in ('HSD', 'cl', 'frame', None, '6a1cbbc3-8f96-4834-a5b9-59ac5296b9f1')
- warning `W_TELEPORT` message.log:3330 teleport in stream ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_TELEPORT` message.log:4084 teleport in stream ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_TELEPORT` message.log:4837 teleport in stream ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_TELEPORT` message.log:5552 teleport in stream ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_TELEPORT` message.log:6295 teleport in stream ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_MORE` message.log:0 9 more teleport rows in ('MT', 'sv', 'cmd', 1, '7b40ec37-c300-4be5-81f7-004085270536')
- warning `W_TIME_BACKWARDS` script.log:713 t 29.25 -> 29.03861 in ('HSD', 'sv', 'evt', 1.0, '7b40ec37-c300-4be5-81f7-004085270536')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2958 | 0 | - | - |
| MT | cl | r90 | 557 | 299.354 | first_order (no) | linear (yes) |
| MT | cl | b1 | 193 | 0 | - | - |
| MT | cl | r30000 | 557 | 299.376 | first_order (no) | friction (no) |
| MT | cl | b2 | 193 | 0 | - | - |
| MT | cl | r30001 | 547 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b3 | 165 | 0 | - | - |
| MT | cl | r30002 | 553 | 299.149 | first_order (no) | linear (no) |
| MT | cl | b4 | 186 | 0 | - | - |
| MT | cl | r30003 | 545 | 299.149 | first_order (no) | linear (no) |
| MT | cl | b5 | 178 | 0 | - | - |
| MT | cl | r30004 | 556 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b6 | 172 | 0 | - | - |
| MT | cl | r30005 | 566 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b7 | 166 | 0 | - | - |
| MT | cl | r30006 | 568 | 299.148 | first_order (no) | linear (no) |
| MT | cl | b8 | 190 | 0 | - | - |
| MT | cl | r30007 | 547 | 299.155 | first_order (no) | linear (no) |
| MT | cl | b9 | 167 | 0 | - | - |
| MT | cl | r30008 | 504 | 298.45 | first_order (no) | linear (no) |
| MT | cl | b10 | 178 | 0 | - | - |
| MT | cl | r30009 | 557 | 299.155 | first_order (no) | linear (no) |
| MT | cl | b11 | 186 | 0 | - | - |
| MT | cl | r30010 | 518 | 298.256 | first_order (no) | linear (no) |
| MT | cl | b12 | 168 | 0 | - | - |
| MT | cl | r30011 | 560 | 299.154 | first_order (no) | linear (no) |
| MT | cl | b13 | 172 | 0 | - | - |
| MT | cl | r30012 | 554 | 297.246 | first_order (no) | linear (no) |
| MT | cl | b14 | 152 | 0 | - | - |
| HSD | cl | r0 | 5396 | 0 | - | - |
| HSD | cl | r90 | 625 | 299.354 | first_order (no) | - |
| HSD | cl | r30000 | 625 | 299.376 | first_order (no) | - |
| HSD | cl | r30001 | 625 | 299.151 | first_order (no) | - |
| HSD | cl | r30002 | 633 | 299.149 | first_order (no) | - |
| HSD | cl | r30003 | 641 | 299.149 | first_order (no) | - |
| HSD | cl | r30004 | 647 | 299.151 | first_order (no) | - |
| HSD | cl | r30005 | 653 | 299.151 | first_order (no) | - |
| HSD | cl | r30006 | 659 | 299.148 | first_order (no) | - |
| HSD | cl | r30007 | 623 | 299.155 | first_order (no) | - |
| HSD | cl | r30008 | 611 | 298.45 | first_order (no) | - |
| HSD | cl | r30009 | 633 | 299.155 | first_order (no) | - |
| HSD | cl | r30010 | 621 | 298.256 | first_order (no) | - |
| HSD | cl | r30011 | 647 | 299.154 | first_order (no) | - |
| HSD | cl | r30012 | 635 | 297.246 | first_order (no) | - |
| MT | sv | b0 | 2973 | 0 | - | - |
| MT | sv | r90 | 557 | 299.354 | first_order (no) | linear (yes) |
| MT | sv | b1 | 193 | 0 | - | - |
| MT | sv | r30000 | 557 | 299.376 | first_order (no) | friction (no) |
| MT | sv | b2 | 193 | 0 | - | - |
| MT | sv | r30001 | 547 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b3 | 165 | 0 | - | - |
| MT | sv | r30002 | 553 | 299.149 | first_order (no) | linear (no) |
| MT | sv | b4 | 186 | 0 | - | - |
| MT | sv | r30003 | 545 | 299.149 | first_order (no) | linear (no) |
| MT | sv | b5 | 178 | 0 | - | - |
| MT | sv | r30004 | 556 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b6 | 172 | 0 | - | - |
| MT | sv | r30005 | 566 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b7 | 166 | 0 | - | - |
| MT | sv | r30006 | 568 | 299.148 | first_order (no) | linear (no) |
| MT | sv | b8 | 190 | 0 | - | - |
| MT | sv | r30007 | 547 | 299.155 | first_order (no) | linear (no) |
| MT | sv | b9 | 167 | 0 | - | - |
| MT | sv | r30008 | 504 | 298.45 | first_order (no) | linear (no) |
| MT | sv | b10 | 178 | 0 | - | - |
| MT | sv | r30009 | 557 | 299.155 | first_order (no) | linear (no) |
| MT | sv | b11 | 186 | 0 | - | - |
| MT | sv | r30010 | 518 | 298.256 | first_order (no) | linear (no) |
| MT | sv | b12 | 168 | 0 | - | - |
| MT | sv | r30011 | 560 | 299.154 | first_order (no) | linear (no) |
| MT | sv | b13 | 172 | 0 | - | - |
| MT | sv | r30012 | 554 | 297.246 | first_order (no) | linear (no) |
| MT | sv | b14 | 149 | 0 | - | - |

Events: 214. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
