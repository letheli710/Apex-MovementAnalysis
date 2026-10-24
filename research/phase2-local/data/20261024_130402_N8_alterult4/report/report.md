# hsd_tel report

Inputs: 16 file(s); rows: 50148 (MT 33441, HSD 16705)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.log:3687 teleport in stream ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` message.log:5696 teleport in stream ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` message.log:7689 teleport in stream ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` message.log:9683 teleport in stream ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` message.log:11738 teleport in stream ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'cl', 'cmd', 1, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` script.log:3338 teleport in stream ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` script.log:7120 teleport in stream ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` script.log:10903 teleport in stream ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` script.log:14685 teleport in stream ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` script.log:18574 teleport in stream ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_MORE` script.log:0 2 more teleport rows in ('HSD', 'cl', 'frame', None, '937e1a2f-8da7-4153-9c0c-f47d2c48b624')
- warning `W_TELEPORT` message.log:3481 teleport in stream ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_TELEPORT` message.log:8149 teleport in stream ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_TELEPORT` message.log:12431 teleport in stream ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_TELEPORT` message.log:15995 teleport in stream ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_TELEPORT` message.log:19504 teleport in stream ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_MORE` message.log:0 2 more teleport rows in ('MT', 'sv', 'cmd', 1, '5107eb36-1b62-4602-99b7-0fa845c50ebf')
- warning `W_TIME_BACKWARDS` script.log:715 t 22.95 -> 22.78314 in ('HSD', 'sv', 'evt', 1.0, '5107eb36-1b62-4602-99b7-0fa845c50ebf')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4360 | 0 | - | - |
| MT | cl | r90 | 1790 | 199.901 | first_order (yes) | linear (yes) |
| MT | cl | r8871 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| MT | cl | r8872 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| MT | cl | r8873 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| MT | cl | r8874 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| MT | cl | r8875 | 1610 | 199.832 | first_order (yes) | friction (no) |
| MT | cl | r8876 | 1610 | 199.872 | first_order (yes) | friction (no) |
| HSD | cl | r0 | 4343 | 0 | - | - |
| HSD | cl | r90 | 1790 | 199.901 | first_order (yes) | linear (yes) |
| HSD | cl | r8871 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| HSD | cl | r8872 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| HSD | cl | r8873 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| HSD | cl | r8874 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| HSD | cl | r8875 | 1610 | 199.832 | first_order (yes) | linear (yes) |
| HSD | cl | r8876 | 1610 | 199.872 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 4371 | 0 | - | - |
| MT | sv | r90 | 1790 | 199.901 | first_order (yes) | linear (yes) |
| MT | sv | r8871 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| MT | sv | r8872 | 1790 | 199.896 | first_order (yes) | linear (yes) |
| MT | sv | r8873 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| MT | sv | r8874 | 1838 | 199.901 | first_order (yes) | linear (yes) |
| MT | sv | r8875 | 1610 | 199.832 | first_order (yes) | friction (no) |
| MT | sv | r8876 | 1610 | 199.872 | first_order (yes) | friction (no) |

Events: 130. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
