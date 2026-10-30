# hsd_tel report

Inputs: 16 file(s); rows: 50064 (MT 33284, HSD 16778)

Validation: 0 error(s), 20 warning(s), 2 info

- warning `W_TELEPORT` message.log:3938 teleport in stream ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` message.log:5955 teleport in stream ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` message.log:7978 teleport in stream ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` message.log:10016 teleport in stream ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` message.log:12085 teleport in stream ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` script.log:3593 teleport in stream ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` script.log:7195 teleport in stream ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` script.log:10798 teleport in stream ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` script.log:14408 teleport in stream ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` script.log:18057 teleport in stream ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '29ddd202-f600-4059-83f3-53f482b2978b')
- warning `W_TELEPORT` message.log:3728 teleport in stream ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TELEPORT` message.log:5603 teleport in stream ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TELEPORT` message.log:7475 teleport in stream ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TELEPORT` message.log:9357 teleport in stream ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TELEPORT` message.log:11262 teleport in stream ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TELEPORT` script.log:871 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')
- warning `W_TIME_BACKWARDS` script.log:717 t 27.45 -> 27.18113 in ('HSD', 'sv', 'evt', 1.0, 'e3e3a887-7657-46fa-bfd1-43ab01d22dfc')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4583 | 0 | - | - |
| MT | cl | r90 | 1705 | 300.287 | first_order (no) | friction (no) |
| MT | cl | r9200 | 1705 | 300.274 | first_order (no) | friction (no) |
| MT | cl | r9201 | 1705 | 300.261 | first_order (no) | friction (no) |
| MT | cl | r9202 | 1715 | 458.473 | first_order (no) | linear (no) |
| MT | cl | r9203 | 1717 | 458.54 | first_order (no) | linear (no) |
| MT | cl | r9204 | 1705 | 300.275 | first_order (no) | friction (no) |
| MT | cl | r9205 | 1759 | 200.741 | first_order (yes) | friction (no) |
| HSD | cl | r0 | 4566 | 0 | - | - |
| HSD | cl | r90 | 1705 | 300.287 | first_order (no) | friction (no) |
| HSD | cl | r9200 | 1705 | 300.274 | first_order (no) | friction (no) |
| HSD | cl | r9201 | 1705 | 300.261 | first_order (no) | friction (no) |
| HSD | cl | r9202 | 1717 | 458.473 | first_order (no) | linear (no) |
| HSD | cl | r9203 | 1717 | 458.54 | first_order (no) | linear (no) |
| HSD | cl | r9204 | 1705 | 300.275 | first_order (no) | friction (no) |
| HSD | cl | r9205 | 1759 | 200.741 | first_order (yes) | friction (no) |
| MT | sv | b0 | 4586 | 0 | - | - |
| MT | sv | r90 | 1705 | 300.287 | first_order (no) | friction (no) |
| MT | sv | r9200 | 1705 | 300.274 | first_order (no) | friction (no) |
| MT | sv | r9201 | 1705 | 300.261 | first_order (no) | friction (no) |
| MT | sv | r9202 | 1715 | 458.473 | first_order (no) | linear (no) |
| MT | sv | r9203 | 1717 | 458.54 | first_order (no) | linear (no) |
| MT | sv | r9204 | 1705 | 300.275 | first_order (no) | friction (no) |
| MT | sv | r9205 | 1759 | 200.741 | first_order (yes) | friction (no) |

Events: 359. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
