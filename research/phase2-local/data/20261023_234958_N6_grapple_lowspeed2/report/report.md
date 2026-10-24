# hsd_tel report

Inputs: 16 file(s); rows: 28018 (MT 18830, HSD 9186)

Validation: 0 error(s), 15 warning(s), 2 info

- warning `W_TELEPORT` message.log:3881 teleport in stream ('MT', 'cl', 'cmd', 1, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` message.log:8935 teleport in stream ('MT', 'cl', 'cmd', 1, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` message.log:9618 teleport in stream ('MT', 'cl', 'cmd', 1, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` script.log:3501 teleport in stream ('HSD', 'cl', 'frame', None, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` script.log:11656 teleport in stream ('HSD', 'cl', 'frame', None, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` script.log:12674 teleport in stream ('HSD', 'cl', 'frame', None, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` script.log:11657 teleport in stream ('HSD', 'cl', 'edge', None, '8cc47b1b-9e48-4a91-818c-c386c1dc4f8d')
- warning `W_TELEPORT` message.log:3644 teleport in stream ('MT', 'sv', 'cmd', 1, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` message.log:8377 teleport in stream ('MT', 'sv', 'cmd', 1, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` message.log:8964 teleport in stream ('MT', 'sv', 'cmd', 1, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` script.log:1259 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` script.log:1289 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` script.log:1308 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TELEPORT` script.log:1433 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'd32abe96-3191-499e-86ac-c579f2d0b64c')
- warning `W_TIME_BACKWARDS` script.log:714 t 24.5 -> 24.2394 in ('HSD', 'sv', 'evt', 1.0, 'd32abe96-3191-499e-86ac-c579f2d0b64c')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4928 | 250.708 | - | - |
| MT | cl | r90 | 421 | 0 | - | - |
| MT | cl | r20331 | 421 | 0 | - | - |
| MT | cl | r20332 | 421 | 0 | - | - |
| MT | cl | r20333 | 421 | 0 | - | - |
| MT | cl | r20334 | 421 | 0 | - | - |
| MT | cl | r20335 | 421 | 0 | - | - |
| MT | cl | r20336 | 421 | 0 | - | - |
| MT | cl | r20337 | 421 | 800.671 | - | - |
| MT | cl | r20338 | 421 | 800.596 | - | linear (yes) |
| MT | cl | r20339 | 421 | 800.669 | - | - |
| HSD | cl | r0 | 4906 | 250.708 | - | - |
| HSD | cl | r90 | 421 | 0 | - | - |
| HSD | cl | r20331 | 421 | 0 | - | - |
| HSD | cl | r20332 | 421 | 0 | - | - |
| HSD | cl | r20333 | 421 | 0 | - | - |
| HSD | cl | r20334 | 421 | 0 | - | - |
| HSD | cl | r20335 | 421 | 0 | - | - |
| HSD | cl | r20336 | 421 | 0 | - | - |
| HSD | cl | r20337 | 421 | 800.671 | - | - |
| HSD | cl | r20338 | 421 | 800.596 | - | linear (yes) |
| HSD | cl | r20339 | 421 | 800.669 | - | - |
| MT | sv | b0 | 4931 | 219.636 | - | - |
| MT | sv | r90 | 421 | 0 | - | - |
| MT | sv | r20331 | 421 | 0 | - | - |
| MT | sv | r20332 | 421 | 0 | - | - |
| MT | sv | r20333 | 421 | 0 | - | - |
| MT | sv | r20334 | 421 | 0 | - | - |
| MT | sv | r20335 | 421 | 0 | - | - |
| MT | sv | r20336 | 421 | 0 | - | - |
| MT | sv | r20337 | 421 | 800.671 | - | - |
| MT | sv | r20338 | 421 | 800.596 | - | linear (yes) |
| MT | sv | r20339 | 421 | 800.669 | - | - |

Events: 54. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
