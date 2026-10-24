# hsd_tel report

Inputs: 16 file(s); rows: 13422 (MT 8529, HSD 4222)

Validation: 0 error(s), 5 warning(s), 2 info

- warning `W_TELEPORT` message.log:4335 teleport in stream ('MT', 'cl', 'cmd', 1, '2ee854a0-4a6b-4913-8684-eea1a72d5ee6')
- warning `W_TELEPORT` script.log:3313 teleport in stream ('HSD', 'cl', 'frame', None, '2ee854a0-4a6b-4913-8684-eea1a72d5ee6')
- warning `W_TELEPORT` message.log:3480 teleport in stream ('MT', 'sv', 'cmd', 1, 'b302efd5-9f6c-4316-a352-afdd0ebba139')
- warning `W_TELEPORT` script.log:780 teleport in stream ('HSD', 'sv', 'evt', 1.0, 'b302efd5-9f6c-4316-a352-afdd0ebba139')
- warning `W_TIME_BACKWARDS` script.log:718 t 23.55 -> 23.31246 in ('HSD', 'sv', 'evt', 1.0, 'b302efd5-9f6c-4316-a352-afdd0ebba139')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3218 | 0 | - | - |
| MT | cl | r20107 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| HSD | cl | r0 | 3188 | 0 | - | - |
| HSD | cl | r20107 | 1021 | 199.525 | first_order (yes) | linear (yes) |
| MT | sv | b0 | 3246 | 0 | - | - |
| MT | sv | r20107 | 1021 | 199.525 | first_order (yes) | linear (yes) |

Events: 13. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
