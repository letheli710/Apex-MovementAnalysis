# hsd_tel report

Inputs: 19 file(s); rows: 135680 (MT 90635, HSD 45043)

Validation: 0 error(s), 19 warning(s), 2 info

- warning `W_TELEPORT` message.1.log:3691 teleport in stream ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` message.1.log:5344 teleport in stream ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` message.1.log:6998 teleport in stream ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` message.1.log:8665 teleport in stream ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` message.1.log:10332 teleport in stream ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_MORE` message.1.log:0 21 more teleport rows in ('MT', 'cl', 'cmd', 1, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` script.1.log:3336 teleport in stream ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` script.1.log:6461 teleport in stream ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` script.1.log:9581 teleport in stream ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` script.1.log:12709 teleport in stream ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` script.1.log:15832 teleport in stream ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_MORE` script.1.log:0 21 more teleport rows in ('HSD', 'cl', 'frame', None, '2f3f822d-ba7d-4bb0-8464-94010a1a53b9')
- warning `W_TELEPORT` message.1.log:3489 teleport in stream ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_TELEPORT` message.1.log:5133 teleport in stream ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_TELEPORT` message.1.log:6768 teleport in stream ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_TELEPORT` message.1.log:8410 teleport in stream ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_TELEPORT` message.1.log:10047 teleport in stream ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_MORE` message.1.log:0 21 more teleport rows in ('MT', 'sv', 'cmd', 1, 'caf01847-e267-4b49-a504-73f07d5fe590')
- warning `W_TIME_BACKWARDS` script.log:717 t 22.9 -> 22.74135 in ('HSD', 'sv', 'evt', 1.0, 'caf01847-e267-4b49-a504-73f07d5fe590')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 7558 | 400 | - | linear (yes) |
| MT | cl | r90 | 1469 | 400 | first_order (no) | linear (no) |
| MT | cl | r8401 | 1469 | 400 | first_order (no) | linear (no) |
| MT | cl | r8402 | 1469 | 400 | first_order (no) | linear (no) |
| MT | cl | r8403 | 1472 | 400 | first_order (no) | linear (no) |
| MT | cl | r8404 | 1473 | 400 | first_order (no) | linear (no) |
| MT | cl | r8405 | 1479 | 400 | first_order (no) | linear (no) |
| MT | cl | r8406 | 1440 | 354.785 | linear (no) | linear (no) |
| MT | cl | r8407 | 1440 | 314.591 | linear (no) | linear (no) |
| MT | cl | r8408 | 1440 | 320.73 | linear (no) | linear (no) |
| MT | cl | r8409 | 1440 | 354.798 | linear (no) | linear (no) |
| MT | cl | r8410 | 1440 | 354.81 | linear (no) | linear (no) |
| MT | cl | r8411 | 1440 | 271.748 | linear (no) | linear (no) |
| MT | cl | r8412 | 1440 | 274.439 | linear (no) | linear (no) |
| MT | cl | r8413 | 1440 | 240.82 | linear (no) | linear (no) |
| MT | cl | r8414 | 1440 | 274.463 | linear (no) | linear (no) |
| MT | cl | r8415 | 1440 | 274.451 | linear (no) | linear (no) |
| MT | cl | r8416 | 1407 | 400 | first_order (yes) | - |
| MT | cl | r8417 | 1407 | 400 | first_order (yes) | - |
| MT | cl | r8418 | 1407 | 400 | first_order (yes) | - |
| MT | cl | r8419 | 1408 | 400 | first_order (yes) | - |
| MT | cl | r8420 | 1407 | 400 | first_order (yes) | - |
| MT | cl | r8421 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | cl | r8422 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | cl | r8423 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | cl | r8424 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | cl | r8425 | 1407 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r0 | 7529 | 400 | - | linear (yes) |
| HSD | cl | r90 | 1469 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8401 | 1469 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8402 | 1469 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8403 | 1472 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8404 | 1473 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8405 | 1479 | 400 | first_order (no) | linear (no) |
| HSD | cl | r8406 | 1440 | 354.785 | first_order (no) | friction (no) |
| HSD | cl | r8407 | 1440 | 314.591 | first_order (no) | linear (no) |
| HSD | cl | r8408 | 1440 | 320.73 | first_order (no) | linear (no) |
| HSD | cl | r8409 | 1440 | 354.798 | first_order (no) | friction (no) |
| HSD | cl | r8410 | 1440 | 354.81 | first_order (no) | friction (no) |
| HSD | cl | r8411 | 1440 | 271.748 | first_order (no) | linear (no) |
| HSD | cl | r8412 | 1440 | 274.439 | first_order (no) | linear (no) |
| HSD | cl | r8413 | 1440 | 240.82 | first_order (no) | linear (no) |
| HSD | cl | r8414 | 1440 | 274.463 | first_order (no) | linear (no) |
| HSD | cl | r8415 | 1440 | 274.451 | first_order (no) | linear (no) |
| HSD | cl | r8416 | 1407 | 400 | first_order (yes) | - |
| HSD | cl | r8417 | 1407 | 400 | first_order (yes) | - |
| HSD | cl | r8418 | 1407 | 400 | first_order (yes) | - |
| HSD | cl | r8419 | 1408 | 400 | first_order (yes) | - |
| HSD | cl | r8420 | 1407 | 400 | first_order (yes) | - |
| HSD | cl | r8421 | 1407 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r8422 | 1407 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r8423 | 1407 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r8424 | 1407 | 400 | first_order (no) | linear (yes) |
| HSD | cl | r8425 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | sv | b0 | 7564 | 400 | - | linear (yes) |
| MT | sv | r90 | 1469 | 400 | first_order (no) | linear (no) |
| MT | sv | r8401 | 1469 | 400 | first_order (no) | linear (no) |
| MT | sv | r8402 | 1469 | 400 | first_order (no) | linear (no) |
| MT | sv | r8403 | 1472 | 400 | linear (no) | linear (no) |
| MT | sv | r8404 | 1473 | 400 | linear (no) | linear (no) |
| MT | sv | r8405 | 1479 | 400 | first_order (no) | linear (no) |
| MT | sv | r8406 | 1440 | 354.785 | linear (no) | linear (no) |
| MT | sv | r8407 | 1440 | 314.591 | linear (no) | linear (no) |
| MT | sv | r8408 | 1440 | 314.335 | linear (no) | linear (no) |
| MT | sv | r8409 | 1440 | 354.798 | linear (no) | linear (no) |
| MT | sv | r8410 | 1440 | 354.81 | linear (no) | linear (no) |
| MT | sv | r8411 | 1440 | 271.748 | linear (no) | linear (no) |
| MT | sv | r8412 | 1440 | 274.439 | linear (no) | linear (no) |
| MT | sv | r8413 | 1440 | 240.82 | linear (no) | linear (no) |
| MT | sv | r8414 | 1440 | 274.463 | linear (no) | linear (no) |
| MT | sv | r8415 | 1440 | 274.451 | linear (no) | linear (no) |
| MT | sv | r8416 | 1407 | 400 | first_order (yes) | - |
| MT | sv | r8417 | 1407 | 400 | first_order (yes) | - |
| MT | sv | r8418 | 1407 | 400 | first_order (yes) | - |
| MT | sv | r8419 | 1408 | 400 | first_order (yes) | - |
| MT | sv | r8420 | 1407 | 400 | first_order (yes) | - |
| MT | sv | r8421 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | sv | r8422 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | sv | r8423 | 1407 | 400 | linear (no) | linear (yes) |
| MT | sv | r8424 | 1407 | 400 | first_order (no) | linear (yes) |
| MT | sv | r8425 | 1407 | 400 | first_order (no) | linear (yes) |

Events: 210. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
