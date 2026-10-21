# hsd_tel report

Inputs: 16 file(s); rows: 44100 (MT 28483, HSD 15615)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3294 teleport in stream ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` message.log:3715 teleport in stream ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` message.log:4133 teleport in stream ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` message.log:4552 teleport in stream ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` message.log:4973 teleport in stream ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_MORE` message.log:0 22 more teleport rows in ('MT', 'cl', 'cmd', 1, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` script.log:2924 teleport in stream ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` script.log:3386 teleport in stream ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` script.log:3848 teleport in stream ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` script.log:4310 teleport in stream ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` script.log:4773 teleport in stream ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_MORE` script.log:0 22 more teleport rows in ('HSD', 'cl', 'frame', None, '9730302c-f27c-4fa8-be1c-d453ba9a5475')
- warning `W_TELEPORT` message.log:3072 teleport in stream ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_TELEPORT` message.log:3491 teleport in stream ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_TELEPORT` message.log:3907 teleport in stream ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_TELEPORT` message.log:4325 teleport in stream ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_TELEPORT` message.log:4744 teleport in stream ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_MORE` message.log:0 22 more teleport rows in ('MT', 'sv', 'cmd', 1, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')
- warning `W_TIME_BACKWARDS` script.log:714 t 25.25 -> 25.00313 in ('HSD', 'sv', 'evt', 1.0, '91cc9aeb-0da4-4c76-b9bd-4deae3a50acf')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 2698 | 0 | - | - |
| MT | cl | r90 | 310 | 299.977 | first_order (no) | - |
| MT | cl | b1 | 100 | 0 | - | - |
| MT | cl | r1301 | 307 | 299.95 | first_order (no) | - |
| MT | cl | b2 | 101 | 0 | - | - |
| MT | cl | r1302 | 311 | 300.032 | first_order (no) | - |
| MT | cl | b3 | 99 | 0 | - | - |
| MT | cl | r1303 | 312 | 300.032 | first_order (no) | - |
| MT | cl | b4 | 99 | 0 | - | - |
| MT | cl | r1304 | 319 | 300.004 | first_order (no) | - |
| MT | cl | b5 | 113 | 0 | - | - |
| MT | cl | r1305 | 314 | 300.032 | first_order (no) | - |
| MT | cl | b6 | 112 | 0 | - | - |
| MT | cl | r1306 | 315 | 300.032 | first_order (no) | - |
| MT | cl | b7 | 111 | 0 | - | - |
| MT | cl | r1307 | 314 | 300.033 | first_order (no) | - |
| MT | cl | b8 | 110 | 0 | - | - |
| MT | cl | r1308 | 315 | 300.032 | first_order (no) | - |
| MT | cl | b9 | 109 | 0 | - | - |
| MT | cl | r1309 | 315 | 300.032 | first_order (no) | - |
| MT | cl | b10 | 108 | 0 | - | - |
| MT | cl | r1310 | 316 | 389.597 | linear (no) | linear (yes) |
| MT | cl | b11 | 107 | 0 | - | - |
| MT | cl | r1311 | 317 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b12 | 106 | 0 | - | - |
| MT | cl | r1312 | 321 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b13 | 105 | 0 | - | - |
| MT | cl | r1313 | 322 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b14 | 104 | 0 | - | - |
| MT | cl | r1314 | 321 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b15 | 103 | 0 | - | - |
| MT | cl | r1315 | 322 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b16 | 102 | 0 | - | - |
| MT | cl | r1316 | 322 | 389.647 | linear (no) | linear (yes) |
| MT | cl | b17 | 101 | 0 | - | - |
| MT | cl | r1317 | 323 | 389.647 | linear (no) | linear (yes) |
| MT | cl | b18 | 100 | 0 | - | - |
| MT | cl | r1318 | 333 | 460 | first_order (no) | - |
| MT | cl | b19 | 99 | 0 | - | - |
| MT | cl | r1319 | 328 | 300.011 | first_order (no) | - |
| MT | cl | b20 | 113 | 0 | - | - |
| MT | cl | r1320 | 336 | 300.018 | first_order (no) | - |
| MT | cl | b21 | 111 | 0 | - | - |
| MT | cl | r1321 | 327 | 300.011 | first_order (no) | - |
| MT | cl | b22 | 111 | 0 | - | - |
| MT | cl | r1322 | 331 | 300.011 | first_order (no) | - |
| MT | cl | b23 | 110 | 0 | - | - |
| MT | cl | r1323 | 330 | 300.011 | first_order (no) | - |
| MT | cl | b24 | 109 | 0 | - | - |
| MT | cl | r1324 | 325 | 300.033 | first_order (no) | - |
| MT | cl | b25 | 107 | 0 | - | - |
| MT | cl | r1325 | 322 | 389.647 | linear (no) | linear (yes) |
| MT | cl | b26 | 104 | 0 | - | - |
| MT | cl | r1326 | 325 | 389.648 | linear (no) | linear (yes) |
| MT | cl | b27 | 68 | 0 | - | - |
| HSD | cl | r0 | 5494 | 0 | - | - |
| HSD | cl | r90 | 343 | 299.977 | first_order (no) | - |
| HSD | cl | r1301 | 343 | 299.95 | first_order (no) | - |
| HSD | cl | r1302 | 344 | 300.032 | first_order (no) | - |
| HSD | cl | r1303 | 345 | 300.032 | first_order (no) | - |
| HSD | cl | r1304 | 346 | 300.004 | first_order (no) | - |
| HSD | cl | r1305 | 347 | 300.032 | first_order (no) | - |
| HSD | cl | r1306 | 348 | 300.032 | first_order (no) | - |
| HSD | cl | r1307 | 349 | 300.033 | first_order (no) | - |
| HSD | cl | r1308 | 350 | 300.032 | first_order (no) | - |
| HSD | cl | r1309 | 351 | 300.032 | first_order (no) | - |
| HSD | cl | r1310 | 352 | 389.597 | - | linear (yes) |
| HSD | cl | r1311 | 353 | 389.648 | - | linear (yes) |
| HSD | cl | r1312 | 354 | 389.648 | - | linear (yes) |
| HSD | cl | r1313 | 355 | 389.648 | - | linear (yes) |
| HSD | cl | r1314 | 356 | 389.648 | - | linear (yes) |
| HSD | cl | r1315 | 357 | 389.648 | - | linear (yes) |
| HSD | cl | r1316 | 358 | 389.647 | - | linear (yes) |
| HSD | cl | r1317 | 359 | 389.647 | - | linear (yes) |
| HSD | cl | r1318 | 360 | 460 | first_order (no) | - |
| HSD | cl | r1319 | 361 | 300.011 | first_order (no) | - |
| HSD | cl | r1320 | 362 | 300.018 | first_order (no) | - |
| HSD | cl | r1321 | 363 | 300.011 | first_order (no) | - |
| HSD | cl | r1322 | 364 | 300.011 | first_order (no) | - |
| HSD | cl | r1323 | 365 | 300.011 | first_order (no) | - |
| HSD | cl | r1324 | 352 | 300.033 | first_order (no) | - |
| HSD | cl | r1325 | 355 | 389.647 | - | linear (yes) |
| HSD | cl | r1326 | 358 | 389.648 | - | linear (yes) |
| MT | sv | b0 | 2709 | 0 | - | - |
| MT | sv | r90 | 310 | 299.977 | first_order (no) | - |
| MT | sv | b1 | 100 | 0 | - | - |
| MT | sv | r1301 | 307 | 299.95 | first_order (no) | - |
| MT | sv | b2 | 101 | 0 | - | - |
| MT | sv | r1302 | 311 | 300.032 | first_order (no) | - |
| MT | sv | b3 | 99 | 0 | - | - |
| MT | sv | r1303 | 312 | 300.032 | first_order (no) | - |
| MT | sv | b4 | 99 | 0 | - | - |
| MT | sv | r1304 | 319 | 300.004 | first_order (no) | - |
| MT | sv | b5 | 113 | 0 | - | - |
| MT | sv | r1305 | 314 | 300.032 | first_order (no) | - |
| MT | sv | b6 | 112 | 0 | - | - |
| MT | sv | r1306 | 315 | 300.032 | first_order (no) | - |
| MT | sv | b7 | 111 | 0 | - | - |
| MT | sv | r1307 | 314 | 300.033 | first_order (no) | - |
| MT | sv | b8 | 110 | 0 | - | - |
| MT | sv | r1308 | 315 | 300.032 | first_order (no) | - |
| MT | sv | b9 | 109 | 0 | - | - |
| MT | sv | r1309 | 315 | 300.032 | first_order (no) | - |
| MT | sv | b10 | 108 | 0 | - | - |
| MT | sv | r1310 | 316 | 389.597 | linear (no) | linear (yes) |
| MT | sv | b11 | 107 | 0 | - | - |
| MT | sv | r1311 | 317 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b12 | 106 | 0 | - | - |
| MT | sv | r1312 | 321 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b13 | 105 | 0 | - | - |
| MT | sv | r1313 | 322 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b14 | 104 | 0 | - | - |
| MT | sv | r1314 | 321 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b15 | 103 | 0 | - | - |
| MT | sv | r1315 | 322 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b16 | 102 | 0 | - | - |
| MT | sv | r1316 | 322 | 389.647 | linear (no) | linear (yes) |
| MT | sv | b17 | 101 | 0 | - | - |
| MT | sv | r1317 | 323 | 389.647 | linear (no) | linear (yes) |
| MT | sv | b18 | 100 | 0 | - | - |
| MT | sv | r1318 | 333 | 389.647 | linear (no) | linear (yes) |
| MT | sv | b19 | 99 | 0 | - | - |
| MT | sv | r1319 | 328 | 300.011 | first_order (no) | - |
| MT | sv | b20 | 113 | 0 | - | - |
| MT | sv | r1320 | 336 | 300.018 | first_order (no) | - |
| MT | sv | b21 | 111 | 0 | - | - |
| MT | sv | r1321 | 327 | 300.011 | first_order (no) | - |
| MT | sv | b22 | 111 | 0 | - | - |
| MT | sv | r1322 | 331 | 300.011 | first_order (no) | - |
| MT | sv | b23 | 110 | 0 | - | - |
| MT | sv | r1323 | 330 | 300.011 | first_order (no) | - |
| MT | sv | b24 | 109 | 0 | - | - |
| MT | sv | r1324 | 325 | 300.033 | first_order (no) | - |
| MT | sv | b25 | 107 | 0 | - | - |
| MT | sv | r1325 | 322 | 389.647 | linear (no) | linear (yes) |
| MT | sv | b26 | 104 | 0 | - | - |
| MT | sv | r1326 | 325 | 389.648 | linear (no) | linear (yes) |
| MT | sv | b27 | 64 | 0 | - | - |

Events: 827. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
