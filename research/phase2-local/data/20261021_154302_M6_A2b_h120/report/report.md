# hsd_tel report

Inputs: 17 file(s); rows: 88549 (MT 56838, HSD 31709)

Validation: 0 error(s), 22 warning(s), 6 info

- warning `W_TELEPORT` message.log:3803 teleport in stream ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` message.log:4719 teleport in stream ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` message.log:5637 teleport in stream ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` message.log:6555 teleport in stream ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` message.log:7472 teleport in stream ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` script.1.log:3436 teleport in stream ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` script.1.log:5231 teleport in stream ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` script.1.log:7028 teleport in stream ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` script.1.log:8825 teleport in stream ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` script.1.log:10623 teleport in stream ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_MORE` script.1.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, '2bc9fa65-9b1d-4f93-a962-5a87b976b238')
- warning `W_TELEPORT` message.log:3577 teleport in stream ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` message.log:4487 teleport in stream ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` message.log:5399 teleport in stream ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` message.log:6311 teleport in stream ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` message.log:7222 teleport in stream ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` script.log:1578 teleport in stream ('HSD', 'sv', 'evt', 1.0, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` script.log:1600 teleport in stream ('HSD', 'sv', 'evt', 1.0, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TELEPORT` script.log:1656 teleport in stream ('HSD', 'sv', 'evt', 1.0, '1f66105d-6daf-45ad-8a61-4e77608e93a3')
- warning `W_TIME_BACKWARDS` script.log:717 t 25.25 -> 24.9718 in ('HSD', 'sv', 'evt', 1.0, '1f66105d-6daf-45ad-8a61-4e77608e93a3')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3205 | 0 | - | - |
| MT | cl | r90 | 737 | 299.374 | first_order (no) | linear (yes) |
| MT | cl | b1 | 170 | 0 | - | - |
| MT | cl | r3261 | 737 | 299.363 | first_order (no) | friction (no) |
| MT | cl | b2 | 173 | 0 | - | - |
| MT | cl | r3262 | 737 | 299.364 | first_order (no) | linear (yes) |
| MT | cl | b3 | 172 | 0 | - | - |
| MT | cl | r3263 | 736 | 299.363 | first_order (no) | linear (yes) |
| MT | cl | b4 | 173 | 0 | - | - |
| MT | cl | r3264 | 737 | 299.375 | first_order (no) | friction (no) |
| MT | cl | b5 | 172 | 0 | - | - |
| MT | cl | r3265 | 737 | 299.375 | first_order (no) | friction (no) |
| MT | cl | b6 | 1035 | 0 | - | - |
| MT | cl | r3266 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3267 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3268 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3269 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3270 | 600 | 199.525 | first_order (yes) | - |
| MT | cl | r3271 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b7 | 185 | 0 | - | - |
| MT | cl | r3272 | 484 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b8 | 185 | 0 | - | - |
| MT | cl | r3273 | 485 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b9 | 184 | 0 | - | - |
| MT | cl | r3274 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b10 | 185 | 0 | - | - |
| MT | cl | r3275 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b11 | 184 | 0 | - | - |
| MT | cl | r3276 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b12 | 185 | 0 | - | - |
| MT | cl | r3277 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b13 | 185 | 0 | - | - |
| MT | cl | r3278 | 606 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b14 | 184 | 0 | - | - |
| MT | cl | r3279 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b15 | 185 | 0 | - | - |
| MT | cl | r3280 | 605 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b16 | 185 | 0 | - | - |
| MT | cl | r3281 | 666 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b17 | 184 | 0 | - | - |
| MT | cl | r3282 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b18 | 183 | 0 | - | - |
| MT | cl | r3283 | 666 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b19 | 180 | 0 | - | - |
| MT | cl | r3284 | 666 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b20 | 183 | 0 | - | - |
| MT | cl | r3285 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b21 | 184 | 0 | - | - |
| MT | cl | r3286 | 665 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b22 | 183 | 0 | - | - |
| MT | cl | r3287 | 665 | 299.151 | first_order (no) | linear (yes) |
| MT | cl | b23 | 184 | 0 | - | - |
| MT | cl | r3288 | 666 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b24 | 184 | 0 | - | - |
| MT | cl | r3289 | 666 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b25 | 183 | 0 | - | - |
| MT | cl | r3290 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | cl | b26 | 144 | 0 | - | - |
| HSD | cl | r0 | 8719 | 0 | - | - |
| HSD | cl | r90 | 805 | 299.374 | first_order (no) | - |
| HSD | cl | r3261 | 805 | 299.363 | first_order (no) | - |
| HSD | cl | r3262 | 805 | 299.364 | first_order (no) | - |
| HSD | cl | r3263 | 805 | 299.363 | first_order (no) | - |
| HSD | cl | r3264 | 805 | 299.375 | first_order (no) | - |
| HSD | cl | r3265 | 805 | 299.375 | first_order (no) | - |
| HSD | cl | r3266 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3267 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3268 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3269 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3270 | 600 | 199.525 | first_order (yes) | - |
| HSD | cl | r3271 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3272 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3273 | 553 | 299.151 | first_order (no) | - |
| HSD | cl | r3274 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3275 | 553 | 299.152 | first_order (no) | - |
| HSD | cl | r3276 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3277 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3278 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3279 | 673 | 299.151 | first_order (no) | - |
| HSD | cl | r3280 | 673 | 299.152 | first_order (no) | - |
| HSD | cl | r3281 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3282 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3283 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3284 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3285 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3286 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3287 | 734 | 299.151 | first_order (no) | - |
| HSD | cl | r3288 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3289 | 734 | 299.152 | first_order (no) | - |
| HSD | cl | r3290 | 734 | 299.152 | first_order (no) | - |
| MT | sv | b0 | 3219 | 0 | - | - |
| MT | sv | r90 | 737 | 299.374 | first_order (no) | linear (yes) |
| MT | sv | b1 | 170 | 0 | - | - |
| MT | sv | r3261 | 737 | 299.363 | first_order (no) | friction (no) |
| MT | sv | b2 | 173 | 0 | - | - |
| MT | sv | r3262 | 737 | 299.364 | first_order (no) | linear (yes) |
| MT | sv | b3 | 172 | 0 | - | - |
| MT | sv | r3263 | 736 | 299.363 | first_order (no) | linear (yes) |
| MT | sv | b4 | 173 | 0 | - | - |
| MT | sv | r3264 | 737 | 299.375 | first_order (no) | friction (no) |
| MT | sv | b5 | 172 | 0 | - | - |
| MT | sv | r3265 | 737 | 299.375 | first_order (no) | friction (no) |
| MT | sv | b6 | 1035 | 0 | - | - |
| MT | sv | r3266 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3267 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3268 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3269 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3270 | 600 | 199.525 | first_order (yes) | - |
| MT | sv | r3271 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b7 | 185 | 0 | - | - |
| MT | sv | r3272 | 484 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b8 | 185 | 0 | - | - |
| MT | sv | r3273 | 485 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b9 | 184 | 0 | - | - |
| MT | sv | r3274 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b10 | 185 | 0 | - | - |
| MT | sv | r3275 | 485 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b11 | 184 | 0 | - | - |
| MT | sv | r3276 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b12 | 185 | 0 | - | - |
| MT | sv | r3277 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b13 | 185 | 0 | - | - |
| MT | sv | r3278 | 606 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b14 | 184 | 0 | - | - |
| MT | sv | r3279 | 604 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b15 | 185 | 0 | - | - |
| MT | sv | r3280 | 605 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b16 | 185 | 0 | - | - |
| MT | sv | r3281 | 666 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b17 | 184 | 0 | - | - |
| MT | sv | r3282 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b18 | 183 | 0 | - | - |
| MT | sv | r3283 | 666 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b19 | 180 | 0 | - | - |
| MT | sv | r3284 | 666 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b20 | 183 | 0 | - | - |
| MT | sv | r3285 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b21 | 184 | 0 | - | - |
| MT | sv | r3286 | 665 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b22 | 183 | 0 | - | - |
| MT | sv | r3287 | 665 | 299.151 | first_order (no) | linear (yes) |
| MT | sv | b23 | 184 | 0 | - | - |
| MT | sv | r3288 | 666 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b24 | 184 | 0 | - | - |
| MT | sv | r3289 | 666 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b25 | 183 | 0 | - | - |
| MT | sv | r3290 | 665 | 299.152 | first_order (no) | linear (yes) |
| MT | sv | b26 | 136 | 0 | - | - |

Events: 3114. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
