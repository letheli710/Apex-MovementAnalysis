# hsd_tel report

Inputs: 16 file(s); rows: 30322 (MT 20390, HSD 9930)

Validation: 0 error(s), 20 warning(s), 2 info

- warning `W_TELEPORT` message.log:3670 teleport in stream ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` message.log:7254 teleport in stream ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` message.log:7959 teleport in stream ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` message.log:8654 teleport in stream ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` message.log:9362 teleport in stream ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'cl', 'cmd', 1, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` script.log:3300 teleport in stream ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` script.log:9170 teleport in stream ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` script.log:10217 teleport in stream ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` script.log:11236 teleport in stream ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` script.log:12282 teleport in stream ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_MORE` script.log:0 1 more teleport rows in ('HSD', 'cl', 'frame', None, '3f3f92af-cd26-4637-a205-2bb2d2fd3f90')
- warning `W_TELEPORT` message.log:3437 teleport in stream ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TELEPORT` message.log:6827 teleport in stream ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TELEPORT` message.log:7445 teleport in stream ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TELEPORT` message.log:8032 teleport in stream ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TELEPORT` message.log:8650 teleport in stream ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_MORE` message.log:0 1 more teleport rows in ('MT', 'sv', 'cmd', 1, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TELEPORT` script.log:1121 teleport in stream ('HSD', 'sv', 'evt', 1.0, '3937cfa0-0d98-475a-ac2e-416239ddc388')
- warning `W_TIME_BACKWARDS` script.log:713 t 24.4 -> 24.1108 in ('HSD', 'sv', 'evt', 1.0, '3937cfa0-0d98-475a-ac2e-416239ddc388')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 4880 | 0 | - | - |
| MT | cl | r90 | 487 | 0 | - | - |
| MT | cl | r20301 | 487 | 0 | - | - |
| MT | cl | r20302 | 487 | 0 | - | - |
| MT | cl | r20303 | 486 | 0 | - | - |
| MT | cl | r20304 | 486 | 0 | - | - |
| MT | cl | r20305 | 421 | 604.58 | - | linear (yes) |
| MT | cl | r20306 | 421 | 605.218 | - | linear (yes) |
| MT | cl | r20307 | 421 | 603.183 | - | linear (yes) |
| MT | cl | r20308 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | cl | r20309 | 661 | 299 | first_order (no) | linear (no) |
| HSD | cl | r0 | 4854 | 0 | - | - |
| HSD | cl | r90 | 487 | 0 | - | - |
| HSD | cl | r20301 | 487 | 0 | - | - |
| HSD | cl | r20302 | 487 | 0 | - | - |
| HSD | cl | r20303 | 487 | 0 | - | - |
| HSD | cl | r20304 | 487 | 0 | - | - |
| HSD | cl | r20305 | 421 | 604.58 | - | linear (yes) |
| HSD | cl | r20306 | 421 | 605.218 | - | linear (yes) |
| HSD | cl | r20307 | 421 | 603.183 | - | linear (yes) |
| HSD | cl | r20308 | 661 | 299.001 | first_order (no) | linear (no) |
| HSD | cl | r20309 | 661 | 299 | first_order (no) | linear (no) |
| MT | sv | b0 | 4884 | 0 | - | - |
| MT | sv | r90 | 487 | 0 | - | - |
| MT | sv | r20301 | 487 | 0 | - | - |
| MT | sv | r20302 | 487 | 0 | - | - |
| MT | sv | r20303 | 486 | 0 | - | - |
| MT | sv | r20304 | 486 | 0 | - | - |
| MT | sv | r20305 | 421 | 604.58 | - | linear (yes) |
| MT | sv | r20306 | 421 | 605.218 | - | linear (yes) |
| MT | sv | r20307 | 421 | 603.183 | - | linear (yes) |
| MT | sv | r20308 | 661 | 299.001 | first_order (no) | linear (no) |
| MT | sv | r20309 | 661 | 299 | first_order (no) | linear (no) |

Events: 26. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
