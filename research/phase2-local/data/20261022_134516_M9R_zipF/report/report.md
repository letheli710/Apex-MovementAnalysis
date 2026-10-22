# hsd_tel report

Inputs: 16 file(s); rows: 60222 (MT 36685, HSD 23535)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3712 teleport in stream ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` message.log:4381 teleport in stream ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` message.log:5041 teleport in stream ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` message.log:5701 teleport in stream ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` message.log:6362 teleport in stream ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` script.log:3367 teleport in stream ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` script.log:4934 teleport in stream ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` script.log:6503 teleport in stream ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` script.log:8073 teleport in stream ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` script.log:9643 teleport in stream ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_MORE` script.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, '570b3f67-b734-4835-b056-166d15b293c5')
- warning `W_TELEPORT` message.log:3505 teleport in stream ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_TELEPORT` message.log:4210 teleport in stream ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_TELEPORT` message.log:4889 teleport in stream ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_TELEPORT` message.log:5564 teleport in stream ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_TELEPORT` message.log:6238 teleport in stream ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '8f3397ca-1748-437d-af19-a20e382529fc')
- warning `W_TIME_BACKWARDS` script.log:715 t 22.35 -> 22.16447 in ('HSD', 'sv', 'evt', 1.0, '8f3397ca-1748-437d-af19-a20e382529fc')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3133 | 0 | - | - |
| MT | cl | r90 | 447 | 600 | - | - |
| MT | cl | b5 | 175 | 0 | - | - |
| MT | cl | r13201 | 448 | 600 | - | linear (yes) |
| MT | cl | b10 | 176 | 0 | - | - |
| MT | cl | r13202 | 447 | 600 | - | - |
| MT | cl | b15 | 177 | 0 | - | - |
| MT | cl | r13203 | 447 | 600 | - | - |
| MT | cl | b20 | 177 | 0 | - | - |
| MT | cl | r13204 | 447 | 600 | - | - |
| MT | cl | b25 | 177 | 0 | - | - |
| MT | cl | r13205 | 448 | 600 | - | linear (yes) |
| MT | cl | b30 | 1950 | 0 | - | - |
| MT | cl | r13206 | 408 | 285.358 | first_order (no) | friction (no) |
| MT | cl | r13207 | 408 | 285.143 | first_order (no) | friction (no) |
| MT | cl | r13208 | 408 | 285.153 | first_order (no) | friction (no) |
| MT | cl | r13209 | 408 | 285.105 | first_order (no) | friction (no) |
| MT | cl | r13210 | 408 | 285.153 | first_order (no) | friction (no) |
| MT | cl | r13211 | 408 | 285.144 | first_order (no) | - |
| MT | cl | r13212 | 408 | 285.152 | first_order (no) | - |
| MT | cl | r13213 | 408 | 284.993 | first_order (no) | - |
| MT | cl | r13214 | 408 | 285.188 | first_order (no) | - |
| MT | cl | r13215 | 408 | 285.037 | first_order (no) | - |
| MT | cl | r13216 | 201 | 600 | first_order (no) | - |
| MT | cl | b31 | 178 | 600 | - | - |
| MT | cl | r13217 | 200 | 600 | first_order (no) | - |
| MT | cl | b32 | 179 | 600 | - | - |
| MT | cl | r13218 | 200 | 600 | first_order (no) | - |
| MT | cl | b33 | 179 | 600 | - | - |
| MT | cl | r13219 | 199 | 600 | first_order (no) | - |
| MT | cl | b34 | 180 | 600 | - | - |
| MT | cl | r13220 | 200 | 600 | first_order (no) | - |
| MT | cl | b35 | 179 | 600 | - | - |
| MT | cl | r13221 | 120 | 600 | - | - |
| MT | cl | b36 | 190 | 600 | - | - |
| MT | cl | r13222 | 120 | 600 | - | - |
| MT | cl | b37 | 191 | 600 | - | - |
| MT | cl | r13223 | 120 | 600 | - | - |
| MT | cl | b38 | 191 | 600 | - | - |
| MT | cl | r13224 | 120 | 600 | - | - |
| MT | cl | b39 | 191 | 600 | - | - |
| MT | cl | r13225 | 120 | 600 | - | - |
| MT | cl | b40 | 190 | 600 | - | - |
| MT | cl | r13226 | 243 | 600 | first_order (no) | - |
| MT | cl | b41 | 173 | 600 | - | - |
| MT | cl | r13227 | 244 | 600 | first_order (no) | - |
| MT | cl | b42 | 173 | 600 | - | - |
| MT | cl | r13228 | 244 | 600 | first_order (no) | - |
| MT | cl | b43 | 169 | 600 | - | - |
| MT | cl | r13229 | 243 | 600 | first_order (no) | - |
| MT | cl | b44 | 173 | 600 | - | - |
| MT | cl | r13230 | 244 | 600 | first_order (no) | - |
| MT | cl | b45 | 144 | 600 | - | - |
| HSD | cl | r0 | 8627 | 600 | - | linear (yes) |
| HSD | cl | r90 | 681 | 600 | - | - |
| HSD | cl | r13201 | 681 | 600 | - | - |
| HSD | cl | r13202 | 681 | 600 | - | - |
| HSD | cl | r13203 | 681 | 600 | - | - |
| HSD | cl | r13204 | 681 | 600 | - | - |
| HSD | cl | r13205 | 681 | 600 | - | - |
| HSD | cl | r13206 | 410 | 285.358 | first_order (no) | linear (yes) |
| HSD | cl | r13207 | 410 | 285.143 | first_order (no) | linear (yes) |
| HSD | cl | r13208 | 410 | 285.153 | first_order (no) | linear (yes) |
| HSD | cl | r13209 | 410 | 285.105 | first_order (no) | linear (yes) |
| HSD | cl | r13210 | 410 | 285.153 | first_order (no) | linear (yes) |
| HSD | cl | r13211 | 411 | 285.144 | first_order (no) | - |
| HSD | cl | r13212 | 411 | 285.152 | first_order (no) | - |
| HSD | cl | r13213 | 411 | 284.993 | first_order (no) | - |
| HSD | cl | r13214 | 411 | 285.188 | first_order (no) | - |
| HSD | cl | r13215 | 411 | 285.037 | first_order (no) | - |
| HSD | cl | r13216 | 409 | 600 | first_order (no) | - |
| HSD | cl | r13217 | 409 | 600 | first_order (no) | - |
| HSD | cl | r13218 | 409 | 600 | first_order (no) | - |
| HSD | cl | r13219 | 409 | 600 | first_order (no) | - |
| HSD | cl | r13220 | 409 | 600 | first_order (no) | - |
| HSD | cl | r13221 | 397 | 600 | - | - |
| HSD | cl | r13222 | 397 | 600 | - | - |
| HSD | cl | r13223 | 397 | 600 | - | - |
| HSD | cl | r13224 | 397 | 600 | - | - |
| HSD | cl | r13225 | 397 | 600 | - | - |
| HSD | cl | r13226 | 475 | 600 | first_order (no) | - |
| HSD | cl | r13227 | 475 | 600 | first_order (no) | - |
| HSD | cl | r13228 | 475 | 600 | first_order (no) | - |
| HSD | cl | r13229 | 475 | 600 | first_order (no) | - |
| HSD | cl | r13230 | 475 | 600 | first_order (no) | - |
| MT | sv | b0 | 3146 | 0 | - | - |
| MT | sv | r90 | 447 | 600 | - | - |
| MT | sv | b5 | 175 | 0 | - | - |
| MT | sv | r13201 | 448 | 600 | - | linear (yes) |
| MT | sv | b10 | 176 | 0 | - | - |
| MT | sv | r13202 | 447 | 600 | - | - |
| MT | sv | b15 | 177 | 0 | - | - |
| MT | sv | r13203 | 447 | 600 | - | - |
| MT | sv | b20 | 177 | 0 | - | - |
| MT | sv | r13204 | 447 | 600 | - | - |
| MT | sv | b25 | 177 | 0 | - | - |
| MT | sv | r13205 | 448 | 600 | - | linear (yes) |
| MT | sv | b30 | 1950 | 0 | - | - |
| MT | sv | r13206 | 408 | 285.358 | first_order (no) | friction (no) |
| MT | sv | r13207 | 408 | 285.143 | first_order (no) | friction (no) |
| MT | sv | r13208 | 408 | 285.153 | first_order (no) | friction (no) |
| MT | sv | r13209 | 408 | 285.105 | first_order (no) | friction (no) |
| MT | sv | r13210 | 408 | 285.153 | first_order (no) | friction (no) |
| MT | sv | r13211 | 408 | 285.144 | first_order (no) | - |
| MT | sv | r13212 | 408 | 285.152 | first_order (no) | - |
| MT | sv | r13213 | 408 | 284.993 | first_order (no) | - |
| MT | sv | r13214 | 408 | 285.188 | first_order (no) | - |
| MT | sv | r13215 | 408 | 285.037 | first_order (no) | - |
| MT | sv | r13216 | 201 | 600 | first_order (no) | - |
| MT | sv | b31 | 178 | 600 | - | - |
| MT | sv | r13217 | 200 | 600 | first_order (no) | - |
| MT | sv | b32 | 179 | 600 | - | - |
| MT | sv | r13218 | 200 | 600 | first_order (no) | - |
| MT | sv | b33 | 179 | 600 | - | - |
| MT | sv | r13219 | 199 | 600 | first_order (no) | - |
| MT | sv | b34 | 180 | 600 | - | - |
| MT | sv | r13220 | 200 | 600 | first_order (no) | - |
| MT | sv | b35 | 179 | 600 | - | - |
| MT | sv | r13221 | 120 | 600 | - | - |
| MT | sv | b36 | 190 | 600 | - | - |
| MT | sv | r13222 | 120 | 600 | - | - |
| MT | sv | b37 | 191 | 600 | - | - |
| MT | sv | r13223 | 120 | 600 | - | - |
| MT | sv | b38 | 191 | 600 | - | - |
| MT | sv | r13224 | 120 | 600 | - | - |
| MT | sv | b39 | 191 | 600 | - | - |
| MT | sv | r13225 | 120 | 600 | - | - |
| MT | sv | b40 | 190 | 600 | - | - |
| MT | sv | r13226 | 243 | 600 | first_order (no) | - |
| MT | sv | b41 | 173 | 600 | - | - |
| MT | sv | r13227 | 244 | 600 | first_order (no) | - |
| MT | sv | b42 | 173 | 600 | - | - |
| MT | sv | r13228 | 244 | 600 | first_order (no) | - |
| MT | sv | b43 | 169 | 600 | - | - |
| MT | sv | r13229 | 243 | 600 | first_order (no) | - |
| MT | sv | b44 | 173 | 600 | - | - |
| MT | sv | r13230 | 244 | 600 | first_order (no) | - |
| MT | sv | b45 | 136 | 600 | - | - |

Events: 376. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
