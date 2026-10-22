# hsd_tel report

Inputs: 17 file(s); rows: 105126 (MT 68498, HSD 36626)

Validation: 0 error(s), 19 warning(s), 4 info

- warning `W_TELEPORT` message.log:3804 teleport in stream ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` message.log:4498 teleport in stream ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` message.log:5161 teleport in stream ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` message.log:5824 teleport in stream ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` message.log:6487 teleport in stream ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_MORE` message.log:0 38 more teleport rows in ('MT', 'cl', 'cmd', 1, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` script.1.log:3483 teleport in stream ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` script.1.log:4774 teleport in stream ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` script.1.log:6039 teleport in stream ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` script.1.log:7303 teleport in stream ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` script.1.log:8561 teleport in stream ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_MORE` script.1.log:0 38 more teleport rows in ('HSD', 'cl', 'frame', None, '9ba30967-d8a3-45a0-935a-e76be06587a0')
- warning `W_TELEPORT` message.log:3600 teleport in stream ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_TELEPORT` message.log:4289 teleport in stream ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_TELEPORT` message.log:4949 teleport in stream ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_TELEPORT` message.log:5608 teleport in stream ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_TELEPORT` message.log:6265 teleport in stream ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_MORE` message.log:0 38 more teleport rows in ('MT', 'sv', 'cmd', 1, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')
- warning `W_TIME_BACKWARDS` script.log:713 t 24.0 -> 23.70909 in ('HSD', 'sv', 'evt', 1.0, 'e31a5dc1-bb56-4895-8b56-82bb2ff29e2a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3229 | 0 | - | - |
| MT | cl | r90 | 494 | 299.168 | first_order (no) | friction (no) |
| MT | cl | b1 | 194 | 0 | - | - |
| MT | cl | r8901 | 493 | 299.16 | first_order (no) | friction (no) |
| MT | cl | b2 | 167 | 0 | - | - |
| MT | cl | r8902 | 491 | 299.152 | first_order (no) | friction (no) |
| MT | cl | b3 | 168 | 0 | - | - |
| MT | cl | r8903 | 486 | 299.144 | first_order (no) | friction (no) |
| MT | cl | b4 | 171 | 0 | - | - |
| MT | cl | r8904 | 539 | 299.269 | first_order (no) | linear (yes) |
| MT | cl | b5 | 195 | 0 | - | - |
| MT | cl | r8905 | 527 | 299.268 | first_order (no) | friction (no) |
| MT | cl | b6 | 193 | 0 | - | - |
| MT | cl | r8906 | 526 | 299.279 | first_order (no) | friction (no) |
| MT | cl | b7 | 194 | 0 | - | - |
| MT | cl | r8907 | 540 | 299.279 | first_order (no) | linear (yes) |
| MT | cl | b8 | 193 | 0 | - | - |
| MT | cl | r8908 | 541 | 299.279 | first_order (no) | linear (yes) |
| MT | cl | b9 | 192 | 0 | - | - |
| MT | cl | r8909 | 540 | 299.278 | first_order (no) | linear (yes) |
| MT | cl | b10 | 192 | 0 | - | - |
| MT | cl | r8910 | 540 | 299.279 | first_order (no) | linear (yes) |
| MT | cl | b11 | 191 | 0 | - | - |
| MT | cl | r8911 | 541 | 416.118 | first_order (no) | linear (no) |
| MT | cl | b12 | 189 | 0 | - | - |
| MT | cl | r8912 | 541 | 299.269 | first_order (no) | linear (yes) |
| MT | cl | b13 | 190 | 0 | - | - |
| MT | cl | r8913 | 539 | 299.259 | first_order (no) | linear (yes) |
| MT | cl | b14 | 189 | 0 | - | - |
| MT | cl | r8914 | 542 | 460.357 | first_order (no) | linear (no) |
| MT | cl | b15 | 186 | 0 | - | - |
| MT | cl | r8915 | 539 | 299.269 | first_order (no) | linear (yes) |
| MT | cl | b16 | 190 | 0 | - | - |
| MT | cl | r8916 | 540 | 460.356 | first_order (no) | linear (no) |
| MT | cl | b17 | 186 | 0 | - | - |
| MT | cl | r8917 | 540 | 460.358 | first_order (no) | linear (no) |
| MT | cl | b18 | 183 | 0 | - | - |
| MT | cl | r8918 | 539 | 460.359 | first_order (no) | linear (no) |
| MT | cl | b19 | 182 | 0 | - | - |
| MT | cl | r8919 | 540 | 460.356 | first_order (no) | linear (no) |
| MT | cl | b20 | 187 | 0 | - | - |
| MT | cl | r8920 | 539 | 460.356 | first_order (no) | linear (no) |
| MT | cl | b21 | 187 | 0 | - | - |
| MT | cl | r8921 | 541 | 460.358 | first_order (no) | linear (no) |
| MT | cl | b22 | 183 | 0 | - | - |
| MT | cl | r8922 | 541 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b23 | 184 | 0 | - | - |
| MT | cl | r8923 | 539 | 460.36 | first_order (no) | linear (no) |
| MT | cl | b24 | 185 | 0 | - | - |
| MT | cl | r8924 | 539 | 460.356 | first_order (no) | linear (no) |
| MT | cl | b25 | 186 | 0 | - | - |
| MT | cl | r8925 | 541 | 460.357 | first_order (no) | linear (no) |
| MT | cl | b26 | 184 | 0 | - | - |
| MT | cl | r8926 | 539 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b27 | 183 | 0 | - | - |
| MT | cl | r8927 | 542 | 460.366 | first_order (no) | linear (no) |
| MT | cl | b28 | 181 | 0 | - | - |
| MT | cl | r8928 | 541 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b29 | 181 | 0 | - | - |
| MT | cl | r8929 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b30 | 183 | 0 | - | - |
| MT | cl | r8930 | 539 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b31 | 183 | 0 | - | - |
| MT | cl | r8931 | 542 | 460.366 | first_order (no) | linear (no) |
| MT | cl | b32 | 179 | 0 | - | - |
| MT | cl | r8932 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b33 | 181 | 0 | - | - |
| MT | cl | r8933 | 539 | 460.366 | first_order (no) | linear (no) |
| MT | cl | b34 | 181 | 0 | - | - |
| MT | cl | r8934 | 543 | 329.533 | first_order (no) | friction (no) |
| MT | cl | b35 | 177 | 0 | - | - |
| MT | cl | r8935 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | cl | b36 | 179 | 0 | - | - |
| MT | cl | r8936 | 539 | 460.368 | first_order (no) | linear (no) |
| MT | cl | b37 | 179 | 0 | - | - |
| MT | cl | r8937 | 540 | 299.619 | first_order (no) | linear (yes) |
| MT | cl | b38 | 178 | 0 | - | - |
| MT | cl | r8938 | 542 | 299.618 | first_order (no) | linear (yes) |
| MT | cl | b39 | 176 | 0 | - | - |
| MT | cl | r8939 | 542 | 299.618 | first_order (no) | linear (yes) |
| MT | cl | b40 | 176 | 0 | - | - |
| MT | cl | r8940 | 538 | 299.607 | first_order (no) | linear (yes) |
| MT | cl | b41 | 187 | 0 | - | - |
| MT | cl | r8941 | 540 | 329.521 | first_order (no) | linear (no) |
| MT | cl | b42 | 185 | 0 | - | - |
| MT | cl | r8942 | 539 | 329.527 | first_order (no) | linear (no) |
| MT | cl | b43 | 150 | 0 | - | - |
| HSD | cl | r0 | 11091 | 0 | - | - |
| HSD | cl | r90 | 541 | 299.168 | first_order (no) | - |
| HSD | cl | r8901 | 541 | 299.16 | first_order (no) | - |
| HSD | cl | r8902 | 540 | 299.152 | first_order (no) | - |
| HSD | cl | r8903 | 536 | 299.144 | first_order (no) | - |
| HSD | cl | r8904 | 572 | 299.269 | first_order (no) | - |
| HSD | cl | r8905 | 575 | 299.268 | first_order (no) | - |
| HSD | cl | r8906 | 574 | 299.279 | first_order (no) | - |
| HSD | cl | r8907 | 575 | 299.279 | first_order (no) | - |
| HSD | cl | r8908 | 576 | 299.279 | first_order (no) | - |
| HSD | cl | r8909 | 575 | 299.278 | first_order (no) | - |
| HSD | cl | r8910 | 577 | 299.279 | first_order (no) | - |
| HSD | cl | r8911 | 578 | 416.118 | - | linear (no) |
| HSD | cl | r8912 | 578 | 299.269 | first_order (no) | - |
| HSD | cl | r8913 | 578 | 299.259 | first_order (no) | - |
| HSD | cl | r8914 | 581 | 460.357 | - | linear (no) |
| HSD | cl | r8915 | 578 | 299.269 | first_order (no) | - |
| HSD | cl | r8916 | 581 | 460.356 | - | linear (no) |
| HSD | cl | r8917 | 581 | 460.358 | - | linear (no) |
| HSD | cl | r8918 | 580 | 460.359 | - | linear (no) |
| HSD | cl | r8919 | 581 | 460.356 | - | linear (no) |
| HSD | cl | r8920 | 580 | 460.356 | - | linear (no) |
| HSD | cl | r8921 | 584 | 460.358 | - | linear (no) |
| HSD | cl | r8922 | 584 | 460.365 | - | linear (no) |
| HSD | cl | r8923 | 582 | 460.36 | - | linear (no) |
| HSD | cl | r8924 | 582 | 460.356 | - | linear (no) |
| HSD | cl | r8925 | 584 | 460.357 | - | linear (no) |
| HSD | cl | r8926 | 584 | 460.365 | - | linear (no) |
| HSD | cl | r8927 | 587 | 460.366 | - | linear (no) |
| HSD | cl | r8928 | 586 | 460.365 | - | linear (no) |
| HSD | cl | r8929 | 585 | 460.365 | - | linear (no) |
| HSD | cl | r8930 | 584 | 460.365 | - | linear (no) |
| HSD | cl | r8931 | 589 | 460.366 | - | linear (no) |
| HSD | cl | r8932 | 587 | 460.365 | - | linear (no) |
| HSD | cl | r8933 | 586 | 460.366 | - | linear (no) |
| HSD | cl | r8934 | 591 | 329.533 | - | linear (no) |
| HSD | cl | r8935 | 589 | 460.365 | - | linear (no) |
| HSD | cl | r8936 | 588 | 460.368 | - | linear (no) |
| HSD | cl | r8937 | 590 | 299.619 | first_order (no) | - |
| HSD | cl | r8938 | 591 | 299.618 | first_order (no) | - |
| HSD | cl | r8939 | 591 | 299.618 | first_order (no) | - |
| HSD | cl | r8940 | 581 | 299.607 | first_order (no) | - |
| HSD | cl | r8941 | 583 | 329.521 | - | linear (no) |
| HSD | cl | r8942 | 582 | 329.527 | - | linear (no) |
| MT | sv | b0 | 3239 | 0 | - | - |
| MT | sv | r90 | 494 | 299.168 | first_order (no) | friction (no) |
| MT | sv | b1 | 194 | 0 | - | - |
| MT | sv | r8901 | 493 | 299.16 | first_order (no) | friction (no) |
| MT | sv | b2 | 167 | 0 | - | - |
| MT | sv | r8902 | 491 | 299.152 | first_order (no) | friction (no) |
| MT | sv | b3 | 168 | 0 | - | - |
| MT | sv | r8903 | 486 | 299.144 | first_order (no) | friction (no) |
| MT | sv | b4 | 171 | 0 | - | - |
| MT | sv | r8904 | 539 | 299.269 | first_order (no) | linear (yes) |
| MT | sv | b5 | 195 | 0 | - | - |
| MT | sv | r8905 | 527 | 299.268 | first_order (no) | friction (no) |
| MT | sv | b6 | 193 | 0 | - | - |
| MT | sv | r8906 | 526 | 299.279 | first_order (no) | friction (no) |
| MT | sv | b7 | 194 | 0 | - | - |
| MT | sv | r8907 | 540 | 299.279 | first_order (no) | linear (yes) |
| MT | sv | b8 | 193 | 0 | - | - |
| MT | sv | r8908 | 541 | 299.279 | first_order (no) | linear (yes) |
| MT | sv | b9 | 192 | 0 | - | - |
| MT | sv | r8909 | 540 | 299.278 | first_order (no) | linear (yes) |
| MT | sv | b10 | 192 | 0 | - | - |
| MT | sv | r8910 | 540 | 299.279 | first_order (no) | linear (yes) |
| MT | sv | b11 | 191 | 0 | - | - |
| MT | sv | r8911 | 541 | 415.998 | first_order (no) | linear (no) |
| MT | sv | b12 | 189 | 0 | - | - |
| MT | sv | r8912 | 541 | 299.269 | first_order (no) | linear (yes) |
| MT | sv | b13 | 190 | 0 | - | - |
| MT | sv | r8913 | 539 | 299.259 | first_order (no) | linear (yes) |
| MT | sv | b14 | 189 | 0 | - | - |
| MT | sv | r8914 | 542 | 460.357 | first_order (no) | linear (no) |
| MT | sv | b15 | 186 | 0 | - | - |
| MT | sv | r8915 | 539 | 299.269 | first_order (no) | linear (yes) |
| MT | sv | b16 | 190 | 0 | - | - |
| MT | sv | r8916 | 540 | 460.356 | first_order (no) | linear (no) |
| MT | sv | b17 | 186 | 0 | - | - |
| MT | sv | r8917 | 540 | 460.358 | first_order (no) | linear (no) |
| MT | sv | b18 | 183 | 0 | - | - |
| MT | sv | r8918 | 539 | 460.359 | first_order (no) | linear (no) |
| MT | sv | b19 | 182 | 0 | - | - |
| MT | sv | r8919 | 540 | 460.356 | first_order (no) | linear (no) |
| MT | sv | b20 | 187 | 0 | - | - |
| MT | sv | r8920 | 539 | 460.356 | first_order (no) | linear (no) |
| MT | sv | b21 | 187 | 0 | - | - |
| MT | sv | r8921 | 541 | 460.358 | first_order (no) | linear (no) |
| MT | sv | b22 | 183 | 0 | - | - |
| MT | sv | r8922 | 541 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b23 | 184 | 0 | - | - |
| MT | sv | r8923 | 539 | 460.36 | first_order (no) | linear (no) |
| MT | sv | b24 | 185 | 0 | - | - |
| MT | sv | r8924 | 539 | 460.356 | first_order (no) | linear (no) |
| MT | sv | b25 | 186 | 0 | - | - |
| MT | sv | r8925 | 541 | 460.357 | first_order (no) | linear (no) |
| MT | sv | b26 | 184 | 0 | - | - |
| MT | sv | r8926 | 539 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b27 | 183 | 0 | - | - |
| MT | sv | r8927 | 542 | 460.366 | first_order (no) | linear (no) |
| MT | sv | b28 | 181 | 0 | - | - |
| MT | sv | r8928 | 541 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b29 | 181 | 0 | - | - |
| MT | sv | r8929 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b30 | 183 | 0 | - | - |
| MT | sv | r8930 | 539 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b31 | 183 | 0 | - | - |
| MT | sv | r8931 | 542 | 460.366 | first_order (no) | linear (no) |
| MT | sv | b32 | 179 | 0 | - | - |
| MT | sv | r8932 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b33 | 181 | 0 | - | - |
| MT | sv | r8933 | 539 | 460.366 | first_order (no) | linear (no) |
| MT | sv | b34 | 181 | 0 | - | - |
| MT | sv | r8934 | 543 | 329.533 | first_order (no) | friction (no) |
| MT | sv | b35 | 177 | 0 | - | - |
| MT | sv | r8935 | 540 | 460.365 | first_order (no) | linear (no) |
| MT | sv | b36 | 179 | 0 | - | - |
| MT | sv | r8936 | 539 | 460.368 | first_order (no) | linear (no) |
| MT | sv | b37 | 179 | 0 | - | - |
| MT | sv | r8937 | 540 | 299.619 | first_order (no) | linear (yes) |
| MT | sv | b38 | 178 | 0 | - | - |
| MT | sv | r8938 | 542 | 299.618 | first_order (no) | linear (yes) |
| MT | sv | b39 | 176 | 0 | - | - |
| MT | sv | r8939 | 542 | 299.618 | first_order (no) | linear (yes) |
| MT | sv | b40 | 176 | 0 | - | - |
| MT | sv | r8940 | 538 | 299.607 | first_order (no) | linear (yes) |
| MT | sv | b41 | 187 | 0 | - | - |
| MT | sv | r8941 | 540 | 329.521 | first_order (no) | linear (no) |
| MT | sv | b42 | 185 | 0 | - | - |
| MT | sv | r8942 | 539 | 329.527 | first_order (no) | linear (no) |
| MT | sv | b43 | 141 | 0 | - | - |

Events: 963. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
