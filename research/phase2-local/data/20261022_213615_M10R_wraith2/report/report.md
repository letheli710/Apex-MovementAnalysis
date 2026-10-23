# hsd_tel report

Inputs: 16 file(s); rows: 52679 (MT 34987, HSD 17690)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3596 teleport in stream ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` message.log:4904 teleport in stream ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` message.log:6211 teleport in stream ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` message.log:8849 teleport in stream ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` message.log:9791 teleport in stream ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_MORE` message.log:0 8 more teleport rows in ('MT', 'cl', 'cmd', 1, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` script.log:3248 teleport in stream ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` script.log:7022 teleport in stream ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` script.log:10797 teleport in stream ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` script.log:18350 teleport in stream ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` script.log:20769 teleport in stream ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_MORE` script.log:0 8 more teleport rows in ('HSD', 'cl', 'frame', None, '62fbf8a5-b989-4c49-8c9c-8f75ab379309')
- warning `W_TELEPORT` message.log:3389 teleport in stream ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_TELEPORT` message.log:4706 teleport in stream ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_TELEPORT` message.log:6013 teleport in stream ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_TELEPORT` message.log:8630 teleport in stream ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_TELEPORT` message.log:9547 teleport in stream ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_MORE` message.log:0 8 more teleport rows in ('MT', 'sv', 'cmd', 1, '769c490b-fd04-4ab2-a74a-a8f068619465')
- warning `W_TIME_BACKWARDS` script.log:717 t 24.15 -> 23.9915 in ('HSD', 'sv', 'evt', 1.0, '769c490b-fd04-4ab2-a74a-a8f068619465')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3022 | 0 | - | - |
| MT | cl | r90 | 1116 | 364 | linear (no) | linear (yes) |
| MT | cl | b1 | 181 | 0 | - | - |
| MT | cl | r91 | 1115 | 364 | linear (no) | linear (yes) |
| MT | cl | b2 | 182 | 0 | - | - |
| MT | cl | r17001 | 1116 | 364 | linear (no) | linear (yes) |
| MT | cl | b3 | 183 | 0 | - | - |
| MT | cl | r17002 | 1117 | 364 | linear (no) | linear (yes) |
| MT | cl | b4 | 1881 | 0 | - | - |
| MT | cl | r17003 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r17004 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r17005 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r17006 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r17007 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r17008 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r17009 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r17010 | 743 | 299 | first_order (no) | linear (yes) |
| MT | cl | r17011 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r17012 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 5425 | 0 | - | - |
| HSD | cl | r90 | 1190 | 1392.95 | first_order (no) | linear (no) |
| HSD | cl | r91 | 1190 | 1259.6 | first_order (no) | linear (no) |
| HSD | cl | r17001 | 1190 | 1415.76 | first_order (no) | friction (no) |
| HSD | cl | r17002 | 1190 | 1400.45 | first_order (no) | linear (no) |
| HSD | cl | r17003 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r17004 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r17005 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r17006 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r17007 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r17008 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r17009 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r17010 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r17011 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r17012 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | b0 | 3030 | 0 | - | - |
| MT | sv | r90 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b1 | 181 | 0 | - | - |
| MT | sv | r91 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b2 | 182 | 0 | - | - |
| MT | sv | r17001 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b3 | 183 | 0 | - | - |
| MT | sv | r17002 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b4 | 1872 | 0 | - | - |
| MT | sv | r17003 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r17004 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r17005 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r17006 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r17007 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r17008 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r17009 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r17010 | 743 | 299 | first_order (no) | linear (yes) |
| MT | sv | r17011 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r17012 | 744 | 299 | first_order (no) | linear (yes) |

Events: 2. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
