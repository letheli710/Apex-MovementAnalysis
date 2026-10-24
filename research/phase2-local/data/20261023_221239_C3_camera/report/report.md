# hsd_tel report

Inputs: 16 file(s); rows: 42534 (MT 28210, HSD 14264)

Validation: 0 error(s), 31 warning(s), 24 info

- warning `W_TELEPORT` message.log:3787 teleport in stream ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` message.log:4196 teleport in stream ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` message.log:4606 teleport in stream ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` message.log:5017 teleport in stream ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` message.log:5426 teleport in stream ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_MORE` message.log:0 13 more teleport rows in ('MT', 'cl', 'cmd', 1, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:3427 teleport in stream ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:3839 teleport in stream ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:4252 teleport in stream ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:4667 teleport in stream ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:5080 teleport in stream ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_MORE` script.log:0 13 more teleport rows in ('HSD', 'cl', 'frame', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:3479 teleport in stream ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:3893 teleport in stream ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:4306 teleport in stream ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:4721 teleport in stream ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` script.log:5151 teleport in stream ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_MORE` script.log:0 8 more teleport rows in ('HSD', 'cl', 'edge', None, '11c51955-6573-4120-a26a-4d8752cc37a9')
- warning `W_TELEPORT` message.log:3531 teleport in stream ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` message.log:3939 teleport in stream ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` message.log:4346 teleport in stream ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` message.log:4754 teleport in stream ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` message.log:5161 teleport in stream ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_MORE` message.log:0 13 more teleport rows in ('MT', 'sv', 'cmd', 1, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` script.log:828 teleport in stream ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` script.log:833 teleport in stream ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` script.log:838 teleport in stream ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` script.log:843 teleport in stream ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TELEPORT` script.log:848 teleport in stream ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_MORE` script.log:0 8 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')
- warning `W_TIME_BACKWARDS` script.log:716 t 26.65 -> 26.35997 in ('HSD', 'sv', 'evt', 1.0, '989f1e5e-7ce5-4719-b4ec-bb7403dfb7d6')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 7517 | 0 | - | - |
| MT | cl | r90 | 180 | 0 | - | - |
| MT | cl | r20201 | 180 | 0 | - | - |
| MT | cl | r20202 | 180 | 0 | - | - |
| MT | cl | r20203 | 180 | 0 | - | - |
| MT | cl | r20204 | 180 | 0 | - | - |
| MT | cl | r20205 | 180 | 0 | - | - |
| MT | cl | r20206 | 180 | 0 | - | - |
| MT | cl | r20207 | 180 | 0 | - | - |
| MT | cl | r20208 | 180 | 0 | - | - |
| MT | cl | r20209 | 180 | 0 | - | - |
| MT | cl | r20210 | 240 | 0 | - | - |
| MT | cl | r20211 | 240 | 0 | - | - |
| MT | cl | r20212 | 240 | 0 | - | - |
| MT | cl | r20213 | 668 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r20214 | 668 | 456.705 | first_order (no) | linear (no) |
| MT | cl | r20215 | 668 | 457.802 | first_order (no) | linear (no) |
| MT | cl | r20216 | 668 | 457.771 | first_order (no) | linear (no) |
| MT | cl | r20217 | 668 | 457.803 | first_order (no) | linear (no) |
| MT | cl | r20218 | 668 | 457.808 | first_order (no) | linear (no) |
| HSD | cl | r0 | 7486 | 0 | - | - |
| HSD | cl | r90 | 180 | 0 | - | - |
| HSD | cl | r20201 | 180 | 0 | - | - |
| HSD | cl | r20202 | 180 | 0 | - | - |
| HSD | cl | r20203 | 180 | 0 | - | - |
| HSD | cl | r20204 | 180 | 0 | - | - |
| HSD | cl | r20205 | 180 | 0 | - | - |
| HSD | cl | r20206 | 180 | 0 | - | - |
| HSD | cl | r20207 | 180 | 0 | - | - |
| HSD | cl | r20208 | 180 | 0 | - | - |
| HSD | cl | r20209 | 180 | 0 | - | - |
| HSD | cl | r20210 | 240 | 0 | - | - |
| HSD | cl | r20211 | 240 | 0 | - | - |
| HSD | cl | r20212 | 240 | 0 | - | - |
| HSD | cl | r20213 | 668 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r20214 | 668 | 456.705 | first_order (no) | linear (no) |
| HSD | cl | r20215 | 668 | 457.802 | first_order (no) | linear (no) |
| HSD | cl | r20216 | 668 | 457.771 | first_order (no) | linear (no) |
| HSD | cl | r20217 | 668 | 457.803 | first_order (no) | linear (no) |
| HSD | cl | r20218 | 668 | 457.808 | first_order (no) | linear (no) |
| MT | sv | b0 | 7539 | 0 | - | - |
| MT | sv | r90 | 180 | 0 | - | - |
| MT | sv | r20201 | 180 | 0 | - | - |
| MT | sv | r20202 | 180 | 0 | - | - |
| MT | sv | r20203 | 180 | 0 | - | - |
| MT | sv | r20204 | 180 | 0 | - | - |
| MT | sv | r20205 | 180 | 0 | - | - |
| MT | sv | r20206 | 180 | 0 | - | - |
| MT | sv | r20207 | 180 | 0 | - | - |
| MT | sv | r20208 | 180 | 0 | - | - |
| MT | sv | r20209 | 180 | 0 | - | - |
| MT | sv | r20210 | 240 | 0 | - | - |
| MT | sv | r20211 | 240 | 0 | - | - |
| MT | sv | r20212 | 240 | 0 | - | - |
| MT | sv | r20213 | 668 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r20214 | 668 | 456.705 | first_order (no) | linear (no) |
| MT | sv | r20215 | 668 | 457.802 | first_order (no) | linear (no) |
| MT | sv | r20216 | 668 | 457.771 | first_order (no) | linear (no) |
| MT | sv | r20217 | 668 | 457.803 | first_order (no) | linear (no) |
| MT | sv | r20218 | 668 | 457.808 | first_order (no) | linear (no) |

Events: 142. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
