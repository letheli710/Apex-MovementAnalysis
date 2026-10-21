# hsd_tel report

Inputs: 17 file(s); rows: 89424 (MT 58400, HSD 31022)

Validation: 0 error(s), 24 warning(s), 4 info

- warning `W_TELEPORT` message.log:3811 teleport in stream ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` message.log:4744 teleport in stream ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` message.log:5676 teleport in stream ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` message.log:6612 teleport in stream ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` message.log:7549 teleport in stream ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` script.1.log:3452 teleport in stream ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` script.1.log:5248 teleport in stream ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` script.1.log:7044 teleport in stream ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` script.1.log:8842 teleport in stream ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` script.1.log:10640 teleport in stream ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_MORE` script.1.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, '3f24404c-aeef-4063-bbf2-abf90d026da2')
- warning `W_TELEPORT` message.log:3608 teleport in stream ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` message.log:4538 teleport in stream ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` message.log:5470 teleport in stream ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` message.log:6399 teleport in stream ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` message.log:7330 teleport in stream ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` script.log:948 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` script.log:978 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` script.log:990 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` script.log:1002 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TELEPORT` script.log:1012 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')
- warning `W_TIME_BACKWARDS` script.log:713 t 24.75 -> 24.46237 in ('HSD', 'sv', 'evt', 1.0, 'ef096cb1-511e-4ffc-a381-535303d9ef28')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3231 | 0 | - | - |
| MT | cl | r90 | 756 | 299.269 | first_order (no) | linear (yes) |
| MT | cl | b1 | 171 | 0 | - | - |
| MT | cl | r3221 | 757 | 299.27 | first_order (no) | friction (no) |
| MT | cl | b2 | 172 | 0 | - | - |
| MT | cl | r3222 | 756 | 299.279 | first_order (no) | linear (yes) |
| MT | cl | b3 | 173 | 0 | - | - |
| MT | cl | r3223 | 757 | 299.269 | first_order (no) | friction (no) |
| MT | cl | b4 | 173 | 0 | - | - |
| MT | cl | r3224 | 756 | 299.269 | first_order (no) | linear (yes) |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r3225 | 756 | 299.268 | first_order (no) | linear (yes) |
| MT | cl | b6 | 1011 | 0 | - | - |
| MT | cl | r3226 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3227 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3228 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3229 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3230 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3231 | 504 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b7 | 184 | 0 | - | - |
| MT | cl | r3232 | 503 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b8 | 185 | 0 | - | - |
| MT | cl | r3233 | 503 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b9 | 184 | 0 | - | - |
| MT | cl | r3234 | 504 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b10 | 185 | 0 | - | - |
| MT | cl | r3235 | 505 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b11 | 185 | 0 | - | - |
| MT | cl | r3236 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b12 | 185 | 0 | - | - |
| MT | cl | r3237 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b13 | 184 | 0 | - | - |
| MT | cl | r3238 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b14 | 185 | 0 | - | - |
| MT | cl | r3239 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b15 | 184 | 0 | - | - |
| MT | cl | r3240 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b16 | 185 | 0 | - | - |
| MT | cl | r3241 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b17 | 183 | 0 | - | - |
| MT | cl | r3242 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b18 | 184 | 0 | - | - |
| MT | cl | r3243 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b19 | 182 | 0 | - | - |
| MT | cl | r3244 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b20 | 184 | 0 | - | - |
| MT | cl | r3245 | 685 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b21 | 184 | 0 | - | - |
| MT | cl | r3246 | 684 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b22 | 183 | 0 | - | - |
| MT | cl | r3247 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b23 | 183 | 0 | - | - |
| MT | cl | r3248 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b24 | 184 | 0 | - | - |
| MT | cl | r3249 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b25 | 183 | 0 | - | - |
| MT | cl | r3250 | 685 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b26 | 144 | 0 | - | - |
| HSD | cl | r0 | 8712 | 0 | - | - |
| HSD | cl | r90 | 805 | 299.269 | first_order (no) | - |
| HSD | cl | r3221 | 805 | 299.27 | first_order (no) | - |
| HSD | cl | r3222 | 805 | 299.279 | first_order (no) | - |
| HSD | cl | r3223 | 805 | 299.269 | first_order (no) | - |
| HSD | cl | r3224 | 805 | 299.269 | first_order (no) | - |
| HSD | cl | r3225 | 805 | 299.268 | first_order (no) | - |
| HSD | cl | r3226 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3227 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3228 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3229 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3230 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3231 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3232 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3233 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3234 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3235 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3236 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3237 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3238 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3239 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3240 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3241 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3242 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3243 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3244 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3245 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3246 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3247 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3248 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3249 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3250 | 734 | 299.152 | first_order (no) | - |
| MT | sv | b0 | 3247 | 0 | - | - |
| MT | sv | r90 | 756 | 299.269 | first_order (no) | linear (yes) |
| MT | sv | b1 | 171 | 0 | - | - |
| MT | sv | r3221 | 757 | 299.27 | first_order (no) | friction (no) |
| MT | sv | b2 | 172 | 0 | - | - |
| MT | sv | r3222 | 756 | 299.279 | first_order (no) | linear (yes) |
| MT | sv | b3 | 173 | 0 | - | - |
| MT | sv | r3223 | 757 | 299.269 | first_order (no) | friction (no) |
| MT | sv | b4 | 173 | 0 | - | - |
| MT | sv | r3224 | 756 | 299.269 | first_order (no) | linear (yes) |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r3225 | 756 | 299.268 | first_order (no) | linear (yes) |
| MT | sv | b6 | 1011 | 0 | - | - |
| MT | sv | r3226 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3227 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3228 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3229 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3230 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3231 | 504 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b7 | 184 | 0 | - | - |
| MT | sv | r3232 | 503 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b8 | 185 | 0 | - | - |
| MT | sv | r3233 | 503 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b9 | 184 | 0 | - | - |
| MT | sv | r3234 | 504 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b10 | 185 | 0 | - | - |
| MT | sv | r3235 | 505 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b11 | 185 | 0 | - | - |
| MT | sv | r3236 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b12 | 185 | 0 | - | - |
| MT | sv | r3237 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b13 | 184 | 0 | - | - |
| MT | sv | r3238 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b14 | 185 | 0 | - | - |
| MT | sv | r3239 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b15 | 184 | 0 | - | - |
| MT | sv | r3240 | 625 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b16 | 185 | 0 | - | - |
| MT | sv | r3241 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b17 | 183 | 0 | - | - |
| MT | sv | r3242 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b18 | 184 | 0 | - | - |
| MT | sv | r3243 | 686 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b19 | 182 | 0 | - | - |
| MT | sv | r3244 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b20 | 184 | 0 | - | - |
| MT | sv | r3245 | 685 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b21 | 184 | 0 | - | - |
| MT | sv | r3246 | 684 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b22 | 183 | 0 | - | - |
| MT | sv | r3247 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b23 | 183 | 0 | - | - |
| MT | sv | r3248 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b24 | 184 | 0 | - | - |
| MT | sv | r3249 | 686 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b25 | 183 | 0 | - | - |
| MT | sv | r3250 | 685 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b26 | 140 | 0 | - | - |

Events: 1776. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
