# hsd_tel report

Inputs: 17 file(s); rows: 104152 (MT 68319, HSD 35831)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3327 teleport in stream ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` message.log:4245 teleport in stream ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` message.log:5164 teleport in stream ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` message.log:6082 teleport in stream ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` message.log:6998 teleport in stream ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_MORE` message.log:0 16 more teleport rows in ('MT', 'cl', 'cmd', 1, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` script.1.log:2973 teleport in stream ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` script.1.log:5378 teleport in stream ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` script.1.log:7790 teleport in stream ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` script.1.log:10199 teleport in stream ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` script.1.log:12608 teleport in stream ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_MORE` script.1.log:0 16 more teleport rows in ('HSD', 'cl', 'frame', None, '2a3f7444-4922-4733-b187-5c3e884f67ee')
- warning `W_TELEPORT` message.log:3143 teleport in stream ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_TELEPORT` message.log:4054 teleport in stream ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_TELEPORT` message.log:4964 teleport in stream ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_TELEPORT` message.log:5871 teleport in stream ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_TELEPORT` message.log:6778 teleport in stream ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_MORE` message.log:0 16 more teleport rows in ('MT', 'sv', 'cmd', 1, '2903c894-229c-4c21-8763-14d1489789c7')
- warning `W_TIME_BACKWARDS` script.log:717 t 27.2 -> 26.90748 in ('HSD', 'sv', 'evt', 1.0, '2903c894-229c-4c21-8763-14d1489789c7')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3938 | 0 | - | - |
| MT | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r16801 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r16802 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r16803 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | cl | r16804 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r16805 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r16806 | 744 | 299 | first_order (no) | linear (yes) |
| MT | cl | r16807 | 1123 | 364 | linear (no) | linear (yes) |
| MT | cl | b1 | 178 | 0 | - | - |
| MT | cl | r16808 | 1118 | 364 | linear (no) | linear (yes) |
| MT | cl | b2 | 183 | 0 | - | - |
| MT | cl | r16809 | 1119 | 364 | linear (no) | linear (yes) |
| MT | cl | b3 | 178 | 0 | - | - |
| MT | cl | r16810 | 1474 | 364 | linear (no) | linear (yes) |
| MT | cl | b4 | 183 | 0 | - | - |
| MT | cl | r16811 | 1474 | 364 | linear (no) | linear (yes) |
| MT | cl | b5 | 183 | 0 | - | - |
| MT | cl | r16812 | 1467 | 364 | linear (no) | linear (yes) |
| MT | cl | b6 | 184 | 0 | - | - |
| MT | cl | r16813 | 1197 | 364 | linear (no) | linear (yes) |
| MT | cl | b7 | 183 | 0 | - | - |
| MT | cl | r16814 | 1192 | 364 | linear (no) | linear (yes) |
| MT | cl | b8 | 183 | 0 | - | - |
| MT | cl | r16815 | 1191 | 364 | linear (no) | linear (yes) |
| MT | cl | b9 | 182 | 0 | - | - |
| MT | cl | r16816 | 1143 | 557.755 | linear (no) | friction (no) |
| MT | cl | b10 | 190 | 0 | - | - |
| MT | cl | r16817 | 1150 | 557.756 | linear (no) | friction (no) |
| MT | cl | b11 | 194 | 0 | - | - |
| MT | cl | r16818 | 1136 | 557.748 | linear (no) | friction (no) |
| MT | cl | b12 | 178 | 0 | - | - |
| MT | cl | r16819 | 1138 | 364 | linear (no) | linear (yes) |
| MT | cl | b13 | 171 | 0 | - | - |
| MT | cl | r16820 | 1131 | 364 | linear (no) | linear (yes) |
| MT | cl | b14 | 171 | 0 | - | - |
| MT | cl | r16821 | 1138 | 364 | linear (no) | linear (yes) |
| MT | cl | b15 | 350 | 0 | - | - |
| MT | cl | r16822 | 1188 | 364 | linear (no) | linear (yes) |
| MT | cl | r16823 | 886 | 224.298 | first_order (no) | - |
| MT | cl | b17 | 325 | 0 | - | - |
| MT | cl | r16824 | 1188 | 364 | linear (no) | linear (yes) |
| HSD | cl | r0 | 7121 | 0 | - | - |
| HSD | cl | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r16801 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r16802 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r16803 | 745 | 414.98 | first_order (no) | friction (no) |
| HSD | cl | r16804 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r16805 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r16806 | 744 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r16807 | 1190 | 1399.67 | first_order (no) | linear (no) |
| HSD | cl | r16808 | 1190 | 1389.71 | first_order (no) | linear (no) |
| HSD | cl | r16809 | 1190 | 1179.59 | first_order (no) | linear (no) |
| HSD | cl | r16810 | 1670 | 1092.61 | - | friction (no) |
| HSD | cl | r16811 | 1670 | 1122.71 | first_order (no) | linear (no) |
| HSD | cl | r16812 | 1670 | 1092.49 | first_order (no) | friction (no) |
| HSD | cl | r16813 | 1310 | 1101.54 | linear (no) | friction (no) |
| HSD | cl | r16814 | 1310 | 1456.28 | first_order (no) | friction (no) |
| HSD | cl | r16815 | 1310 | 1092.75 | - | friction (no) |
| HSD | cl | r16816 | 1238 | 1426.65 | first_order (no) | - |
| HSD | cl | r16817 | 1238 | 1455.69 | first_order (no) | friction (no) |
| HSD | cl | r16818 | 1238 | 1195.13 | first_order (no) | - |
| HSD | cl | r16819 | 1202 | 1409.4 | first_order (no) | friction (no) |
| HSD | cl | r16820 | 1202 | 1193.79 | first_order (no) | friction (no) |
| HSD | cl | r16821 | 1202 | 1398.66 | first_order (no) | friction (no) |
| HSD | cl | r16822 | 1188 | 364 | linear (no) | linear (yes) |
| HSD | cl | r16823 | 1188 | 1764.85 | linear (no) | - |
| HSD | cl | r16824 | 1188 | 364 | linear (no) | linear (yes) |
| MT | sv | b0 | 3965 | 0 | - | - |
| MT | sv | r90 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r16801 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r16802 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r16803 | 745 | 414.98 | first_order (no) | friction (no) |
| MT | sv | r16804 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r16805 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r16806 | 744 | 299 | first_order (no) | linear (yes) |
| MT | sv | r16807 | 1131 | 364 | linear (no) | linear (yes) |
| MT | sv | b1 | 178 | 0 | - | - |
| MT | sv | r16808 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b2 | 183 | 0 | - | - |
| MT | sv | r16809 | 1124 | 364 | linear (no) | linear (yes) |
| MT | sv | b3 | 178 | 0 | - | - |
| MT | sv | r16810 | 1478 | 364 | linear (no) | linear (yes) |
| MT | sv | b4 | 183 | 0 | - | - |
| MT | sv | r16811 | 1478 | 364 | linear (no) | linear (yes) |
| MT | sv | b5 | 183 | 0 | - | - |
| MT | sv | r16812 | 1472 | 364 | linear (no) | linear (yes) |
| MT | sv | b6 | 184 | 0 | - | - |
| MT | sv | r16813 | 1202 | 364 | linear (no) | linear (yes) |
| MT | sv | b7 | 183 | 0 | - | - |
| MT | sv | r16814 | 1196 | 364 | linear (no) | linear (yes) |
| MT | sv | b8 | 183 | 0 | - | - |
| MT | sv | r16815 | 1196 | 364 | linear (no) | linear (yes) |
| MT | sv | b9 | 182 | 0 | - | - |
| MT | sv | r16816 | 1148 | 557.755 | linear (no) | friction (no) |
| MT | sv | b10 | 190 | 0 | - | - |
| MT | sv | r16817 | 1154 | 557.756 | linear (no) | friction (no) |
| MT | sv | b11 | 194 | 0 | - | - |
| MT | sv | r16818 | 1141 | 557.748 | linear (no) | friction (no) |
| MT | sv | b12 | 178 | 0 | - | - |
| MT | sv | r16819 | 1142 | 364 | linear (no) | linear (yes) |
| MT | sv | b13 | 171 | 0 | - | - |
| MT | sv | r16820 | 1136 | 364 | linear (no) | linear (yes) |
| MT | sv | b14 | 171 | 0 | - | - |
| MT | sv | r16821 | 1142 | 364 | linear (no) | linear (yes) |
| MT | sv | b15 | 350 | 0 | - | - |
| MT | sv | r16822 | 1188 | 364 | linear (no) | linear (yes) |
| MT | sv | r16823 | 894 | 222.242 | first_order (no) | linear (yes) |
| MT | sv | b17 | 321 | 0 | - | - |
| MT | sv | r16824 | 1188 | 364 | linear (no) | linear (yes) |

Events: 20. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
