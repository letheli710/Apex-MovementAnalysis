# hsd_tel report

Inputs: 16 file(s); rows: 22502 (MT 14878, HSD 7564)

Validation: 0 error(s), 31 warning(s), 24 info

- warning `W_TELEPORT` message.log:3795 teleport in stream ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` message.log:4383 teleport in stream ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` message.log:4975 teleport in stream ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` message.log:5569 teleport in stream ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` message.log:6163 teleport in stream ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:3441 teleport in stream ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4033 teleport in stream ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4628 teleport in stream ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:5222 teleport in stream ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:5817 teleport in stream ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:3619 teleport in stream ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4034 teleport in stream ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4212 teleport in stream ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4629 teleport in stream ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` script.log:4807 teleport in stream ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_MORE` script.log:0 6 more teleport rows in ('HSD', 'cl', 'edge', None, 'bc202043-4566-489a-80c2-8d903a01eaac')
- warning `W_TELEPORT` message.log:3530 teleport in stream ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` message.log:4117 teleport in stream ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` message.log:4705 teleport in stream ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` message.log:5293 teleport in stream ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` message.log:5878 teleport in stream ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` script.log:830 teleport in stream ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` script.log:835 teleport in stream ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` script.log:840 teleport in stream ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` script.log:844 teleport in stream ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TELEPORT` script.log:849 teleport in stream ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.25 -> 23.11613 in ('HSD', 'sv', 'evt', 1.0, '160db020-a9b4-493f-bf50-fabd81b9cbfb')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5551 | 0 | - | - |
| MT | cl | r90 | 240 | 0 | - | - |
| MT | cl | r20221 | 240 | 0 | - | - |
| MT | cl | r20222 | 240 | 0 | - | - |
| MT | cl | r20223 | 240 | 0 | - | - |
| MT | cl | r20224 | 300 | 0 | - | - |
| MT | cl | r20225 | 300 | 0 | - | - |
| MT | cl | r20226 | 300 | 0 | - | - |
| HSD | cl | r0 | 5526 | 0 | - | - |
| HSD | cl | r90 | 240 | 0 | - | - |
| HSD | cl | r20221 | 240 | 0 | - | - |
| HSD | cl | r20222 | 240 | 0 | - | - |
| HSD | cl | r20223 | 240 | 0 | - | - |
| HSD | cl | r20224 | 300 | 0 | - | - |
| HSD | cl | r20225 | 300 | 0 | - | - |
| HSD | cl | r20226 | 300 | 0 | - | - |
| MT | sv | b0 | 5558 | 0 | - | - |
| MT | sv | r90 | 240 | 0 | - | - |
| MT | sv | r20221 | 240 | 0 | - | - |
| MT | sv | r20222 | 240 | 0 | - | - |
| MT | sv | r20223 | 240 | 0 | - | - |
| MT | sv | r20224 | 300 | 0 | - | - |
| MT | sv | r20225 | 300 | 0 | - | - |
| MT | sv | r20226 | 300 | 0 | - | - |

Events: 58. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
