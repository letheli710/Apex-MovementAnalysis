# hsd_tel report

Inputs: 16 file(s); rows: 53580 (MT 33260, HSD 20318)

Validation: 0 error(s), 25 warning(s), 6 info

- warning `W_TELEPORT` message.log:3615 teleport in stream ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` message.log:4149 teleport in stream ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` message.log:4678 teleport in stream ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` message.log:5206 teleport in stream ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` message.log:5735 teleport in stream ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'cl', 'cmd', 1, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:3250 teleport in stream ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:4253 teleport in stream ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:5259 teleport in stream ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:6264 teleport in stream ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:7270 teleport in stream ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_MORE` script.log:0 21 more teleport rows in ('HSD', 'cl', 'frame', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:20630 teleport in stream ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:21684 teleport in stream ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:22738 teleport in stream ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:23791 teleport in stream ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` script.log:24845 teleport in stream ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_MORE` script.log:0 4 more teleport rows in ('HSD', 'cl', 'edge', None, '21ea6f79-8127-4415-8f6a-379d46fceddc')
- warning `W_TELEPORT` message.log:3384 teleport in stream ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_TELEPORT` message.log:3937 teleport in stream ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_TELEPORT` message.log:4466 teleport in stream ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_TELEPORT` message.log:4995 teleport in stream ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_TELEPORT` message.log:5524 teleport in stream ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_MORE` message.log:0 21 more teleport rows in ('MT', 'sv', 'cmd', 1, '91c5b16f-e67f-4086-830a-e6d206f04849')
- warning `W_TIME_BACKWARDS` script.log:715 t 23.1 -> 22.94325 in ('HSD', 'sv', 'evt', 1.0, '91c5b16f-e67f-4086-830a-e6d206f04849')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3016 | 0 | - | - |
| MT | cl | r90 | 331 | 343.245 | - | linear (yes) |
| MT | cl | b1 | 181 | 0 | - | - |
| MT | cl | r12901 | 331 | 340 | - | linear (yes) |
| MT | cl | b2 | 183 | 0 | - | - |
| MT | cl | r12902 | 331 | 343.334 | - | linear (yes) |
| MT | cl | b3 | 183 | 0 | - | - |
| MT | cl | r12903 | 331 | 339.999 | - | linear (yes) |
| MT | cl | b4 | 183 | 0 | - | - |
| MT | cl | r12904 | 331 | 343.34 | - | linear (yes) |
| MT | cl | b5 | 183 | 0 | - | - |
| MT | cl | r12905 | 331 | 343.151 | - | linear (yes) |
| MT | cl | b6 | 182 | 0 | - | - |
| MT | cl | r12906 | 337 | 343.34 | - | linear (yes) |
| MT | cl | b7 | 177 | 0 | - | - |
| MT | cl | r12907 | 337 | 343.336 | - | linear (yes) |
| MT | cl | b8 | 177 | 0 | - | - |
| MT | cl | r12908 | 337 | 343.336 | - | linear (yes) |
| MT | cl | b9 | 177 | 0 | - | - |
| MT | cl | r12909 | 337 | 343.34 | - | linear (yes) |
| MT | cl | b10 | 177 | 0 | - | - |
| MT | cl | r12910 | 337 | 343.338 | - | linear (yes) |
| MT | cl | b11 | 177 | 0 | - | - |
| MT | cl | r12911 | 343 | 343.182 | - | linear (yes) |
| MT | cl | b12 | 171 | 0 | - | - |
| MT | cl | r12912 | 343 | 343.341 | - | linear (yes) |
| MT | cl | b13 | 170 | 0 | - | - |
| MT | cl | r12913 | 343 | 343.417 | - | linear (yes) |
| MT | cl | b14 | 171 | 0 | - | - |
| MT | cl | r12914 | 343 | 343.341 | - | linear (yes) |
| MT | cl | b15 | 171 | 0 | - | - |
| MT | cl | r12915 | 343 | 343.341 | - | linear (yes) |
| MT | cl | b16 | 171 | 0 | - | - |
| MT | cl | r12916 | 173 | 600 | - | - |
| MT | cl | b18 | 194 | 600 | - | - |
| MT | cl | r12917 | 173 | 600 | - | - |
| MT | cl | b20 | 195 | 600 | - | - |
| MT | cl | r12918 | 173 | 600 | - | - |
| MT | cl | b22 | 195 | 600 | - | - |
| MT | cl | r12919 | 173 | 600 | - | - |
| MT | cl | b24 | 195 | 600 | - | - |
| MT | cl | r12920 | 173 | 600 | - | - |
| MT | cl | b26 | 195 | 600 | - | - |
| MT | cl | r12921 | 515 | 400 | - | linear (no) |
| MT | cl | b29 | 180 | 0 | - | - |
| MT | cl | r12922 | 515 | 400 | - | linear (no) |
| MT | cl | b32 | 181 | 0 | - | - |
| MT | cl | r12923 | 515 | 400 | - | linear (no) |
| MT | cl | b35 | 181 | 0 | - | - |
| MT | cl | r12924 | 515 | 400 | - | linear (no) |
| MT | cl | b38 | 180 | 0 | - | - |
| MT | cl | r12925 | 515 | 400 | - | linear (no) |
| MT | cl | b41 | 152 | 0 | - | - |
| HSD | cl | r0 | 7681 | 600 | - | linear (yes) |
| HSD | cl | r90 | 405 | 343.245 | - | linear (yes) |
| HSD | cl | r12901 | 405 | 340 | - | linear (yes) |
| HSD | cl | r12902 | 405 | 343.334 | - | linear (yes) |
| HSD | cl | r12903 | 405 | 339.999 | - | linear (yes) |
| HSD | cl | r12904 | 405 | 343.34 | - | linear (yes) |
| HSD | cl | r12905 | 405 | 343.151 | - | linear (yes) |
| HSD | cl | r12906 | 411 | 343.34 | - | linear (yes) |
| HSD | cl | r12907 | 411 | 343.336 | - | linear (yes) |
| HSD | cl | r12908 | 411 | 343.336 | - | linear (yes) |
| HSD | cl | r12909 | 411 | 343.34 | - | linear (yes) |
| HSD | cl | r12910 | 411 | 343.338 | - | linear (yes) |
| HSD | cl | r12911 | 417 | 343.182 | - | linear (yes) |
| HSD | cl | r12912 | 417 | 343.341 | - | linear (yes) |
| HSD | cl | r12913 | 417 | 343.417 | - | linear (yes) |
| HSD | cl | r12914 | 417 | 343.341 | - | linear (yes) |
| HSD | cl | r12915 | 417 | 343.341 | - | linear (yes) |
| HSD | cl | r12916 | 423 | 600 | - | - |
| HSD | cl | r12917 | 423 | 600 | - | - |
| HSD | cl | r12918 | 423 | 600 | - | - |
| HSD | cl | r12919 | 423 | 600 | - | - |
| HSD | cl | r12920 | 423 | 600 | - | - |
| HSD | cl | r12921 | 737 | 430.075 | - | linear (no) |
| HSD | cl | r12922 | 737 | 426.696 | - | linear (no) |
| HSD | cl | r12923 | 737 | 429.997 | - | linear (no) |
| HSD | cl | r12924 | 737 | 430.068 | - | linear (no) |
| HSD | cl | r12925 | 737 | 426.713 | - | linear (no) |
| MT | sv | b0 | 3027 | 0 | - | - |
| MT | sv | r90 | 331 | 343.245 | - | linear (yes) |
| MT | sv | b1 | 181 | 0 | - | - |
| MT | sv | r12901 | 331 | 340 | - | linear (yes) |
| MT | sv | b2 | 183 | 0 | - | - |
| MT | sv | r12902 | 331 | 343.334 | - | linear (yes) |
| MT | sv | b3 | 183 | 0 | - | - |
| MT | sv | r12903 | 331 | 339.999 | - | linear (yes) |
| MT | sv | b4 | 183 | 0 | - | - |
| MT | sv | r12904 | 331 | 343.34 | - | linear (yes) |
| MT | sv | b5 | 183 | 0 | - | - |
| MT | sv | r12905 | 331 | 343.151 | - | linear (yes) |
| MT | sv | b6 | 182 | 0 | - | - |
| MT | sv | r12906 | 337 | 343.34 | - | linear (yes) |
| MT | sv | b7 | 177 | 0 | - | - |
| MT | sv | r12907 | 337 | 343.336 | - | linear (yes) |
| MT | sv | b8 | 177 | 0 | - | - |
| MT | sv | r12908 | 337 | 343.336 | - | linear (yes) |
| MT | sv | b9 | 177 | 0 | - | - |
| MT | sv | r12909 | 337 | 343.34 | - | linear (yes) |
| MT | sv | b10 | 177 | 0 | - | - |
| MT | sv | r12910 | 337 | 343.338 | - | linear (yes) |
| MT | sv | b11 | 177 | 0 | - | - |
| MT | sv | r12911 | 343 | 343.182 | - | linear (yes) |
| MT | sv | b12 | 171 | 0 | - | - |
| MT | sv | r12912 | 343 | 343.341 | - | linear (yes) |
| MT | sv | b13 | 170 | 0 | - | - |
| MT | sv | r12913 | 343 | 343.417 | - | linear (yes) |
| MT | sv | b14 | 171 | 0 | - | - |
| MT | sv | r12914 | 343 | 343.341 | - | linear (yes) |
| MT | sv | b15 | 171 | 0 | - | - |
| MT | sv | r12915 | 343 | 343.341 | - | linear (yes) |
| MT | sv | b16 | 171 | 0 | - | - |
| MT | sv | r12916 | 173 | 600 | - | - |
| MT | sv | b18 | 194 | 600 | - | - |
| MT | sv | r12917 | 173 | 600 | - | - |
| MT | sv | b20 | 195 | 600 | - | - |
| MT | sv | r12918 | 173 | 600 | - | - |
| MT | sv | b22 | 195 | 600 | - | - |
| MT | sv | r12919 | 173 | 600 | - | - |
| MT | sv | b24 | 195 | 600 | - | - |
| MT | sv | r12920 | 173 | 600 | - | - |
| MT | sv | b26 | 195 | 600 | - | - |
| MT | sv | r12921 | 515 | 400 | - | linear (no) |
| MT | sv | b29 | 180 | 0 | - | - |
| MT | sv | r12922 | 515 | 400 | - | linear (no) |
| MT | sv | b32 | 181 | 0 | - | - |
| MT | sv | r12923 | 515 | 400 | - | linear (no) |
| MT | sv | b35 | 181 | 0 | - | - |
| MT | sv | r12924 | 515 | 400 | - | linear (no) |
| MT | sv | b38 | 180 | 0 | - | - |
| MT | sv | r12925 | 515 | 400 | - | linear (no) |
| MT | sv | b41 | 144 | 0 | - | - |

Events: 295. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
