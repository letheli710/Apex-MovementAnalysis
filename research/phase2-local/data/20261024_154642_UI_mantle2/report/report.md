# hsd_tel report

Inputs: 17 file(s); rows: 70177 (MT 45157, HSD 25018)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.log:3610 teleport in stream ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` message.log:4238 teleport in stream ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` message.log:4845 teleport in stream ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` message.log:5475 teleport in stream ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` message.log:6119 teleport in stream ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'cl', 'cmd', 1, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` script.1.log:3255 teleport in stream ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` script.1.log:3967 teleport in stream ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` script.1.log:4634 teleport in stream ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` script.1.log:5309 teleport in stream ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` script.1.log:6041 teleport in stream ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_MORE` script.1.log:0 26 more teleport rows in ('HSD', 'cl', 'frame', None, 'a5dc2561-607f-46b7-af92-0dae6f898a57')
- warning `W_TELEPORT` message.log:3419 teleport in stream ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_TELEPORT` message.log:4052 teleport in stream ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_TELEPORT` message.log:4652 teleport in stream ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_TELEPORT` message.log:5280 teleport in stream ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_TELEPORT` message.log:5921 teleport in stream ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_MORE` message.log:0 26 more teleport rows in ('MT', 'sv', 'cmd', 1, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')
- warning `W_TIME_BACKWARDS` script.log:716 t 24.95 -> 24.70235 in ('HSD', 'sv', 'evt', 1.0, '6b6adbf1-4fb9-487d-b7db-af8c44735d26')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3032 | 0 | - | - |
| MT | cl | r90 | 462 | 299.378 | first_order (no) | friction (no) |
| MT | cl | b1 | 164 | 0 | - | - |
| MT | cl | r8901 | 493 | 299.369 | first_order (no) | friction (no) |
| MT | cl | b2 | 111 | 0 | - | - |
| MT | cl | r8902 | 497 | 299.353 | first_order (no) | friction (no) |
| MT | cl | b3 | 130 | 0 | - | - |
| MT | cl | r8903 | 457 | 299.024 | first_order (no) | - |
| MT | cl | b4 | 184 | 0 | - | - |
| MT | cl | r8904 | 463 | 299.369 | first_order (no) | - |
| MT | cl | b5 | 173 | 0 | - | - |
| MT | cl | r8905 | 493 | 299.375 | first_order (no) | friction (no) |
| MT | cl | b6 | 138 | 0 | - | - |
| MT | cl | r8906 | 482 | 299.249 | first_order (no) | friction (no) |
| MT | cl | b7 | 137 | 0 | - | - |
| MT | cl | r8907 | 460 | 299.024 | first_order (no) | - |
| MT | cl | b8 | 186 | 0 | - | - |
| MT | cl | r8908 | 450 | 299.325 | first_order (no) | - |
| MT | cl | b9 | 161 | 0 | - | - |
| MT | cl | r8909 | 489 | 299.374 | first_order (no) | linear (yes) |
| MT | cl | b10 | 111 | 0 | - | - |
| MT | cl | r8910 | 502 | 299.364 | first_order (no) | friction (no) |
| MT | cl | b11 | 125 | 0 | - | - |
| MT | cl | r8911 | 454 | 299.046 | first_order (no) | friction (no) |
| MT | cl | b12 | 174 | 0 | - | - |
| MT | cl | r8912 | 462 | 299.109 | first_order (no) | - |
| MT | cl | b13 | 184 | 0 | - | - |
| MT | cl | r8913 | 478 | 299.382 | first_order (no) | friction (no) |
| MT | cl | b14 | 131 | 0 | - | - |
| MT | cl | r8914 | 505 | 299.365 | first_order (no) | friction (no) |
| MT | cl | b15 | 111 | 0 | - | - |
| MT | cl | r8915 | 474 | 299.168 | first_order (no) | friction (no) |
| MT | cl | b16 | 164 | 0 | - | - |
| MT | cl | r8916 | 461 | 299.024 | first_order (no) | - |
| MT | cl | b17 | 183 | 0 | - | - |
| MT | cl | r8917 | 469 | 299.379 | first_order (no) | friction (no) |
| MT | cl | b18 | 144 | 0 | - | - |
| MT | cl | r8918 | 509 | 299.364 | first_order (no) | friction (no) |
| MT | cl | b19 | 126 | 0 | - | - |
| MT | cl | r8919 | 459 | 299.083 | first_order (no) | friction (no) |
| MT | cl | b20 | 171 | 0 | - | - |
| MT | cl | r8920 | 459 | 299.074 | first_order (no) | - |
| MT | cl | b21 | 183 | 0 | - | - |
| MT | cl | r8921 | 473 | 299.375 | first_order (no) | linear (yes) |
| MT | cl | b22 | 147 | 0 | - | - |
| MT | cl | r8922 | 471 | 299.16 | first_order (no) | - |
| MT | cl | b23 | 169 | 0 | - | - |
| MT | cl | r8923 | 463 | 299.053 | first_order (no) | - |
| MT | cl | b24 | 186 | 0 | - | - |
| MT | cl | r8924 | 472 | 299.375 | first_order (no) | friction (no) |
| MT | cl | b25 | 130 | 0 | - | - |
| MT | cl | r8925 | 509 | 299.379 | first_order (no) | friction (no) |
| MT | cl | b26 | 135 | 0 | - | - |
| MT | cl | r8926 | 456 | 299.028 | first_order (no) | - |
| MT | cl | b27 | 187 | 0 | - | - |
| MT | cl | r8927 | 463 | 299.383 | first_order (no) | - |
| MT | cl | b28 | 179 | 0 | - | - |
| MT | cl | r8928 | 467 | 299.232 | first_order (no) | - |
| MT | cl | b29 | 156 | 0 | - | - |
| MT | cl | r8929 | 468 | 299.278 | first_order (no) | friction (no) |
| MT | cl | b30 | 126 | 0 | - | - |
| MT | cl | r8930 | 488 | 299.377 | first_order (no) | friction (no) |
| MT | cl | b31 | 148 | 0 | - | - |
| HSD | cl | r0 | 7757 | 0 | - | - |
| HSD | cl | r90 | 533 | 299.378 | first_order (no) | - |
| HSD | cl | r8901 | 540 | 299.369 | first_order (no) | - |
| HSD | cl | r8902 | 529 | 299.353 | first_order (no) | - |
| HSD | cl | r8903 | 528 | 299.024 | first_order (no) | - |
| HSD | cl | r8904 | 534 | 299.369 | first_order (no) | - |
| HSD | cl | r8905 | 541 | 299.375 | first_order (no) | - |
| HSD | cl | r8906 | 520 | 299.249 | first_order (no) | - |
| HSD | cl | r8907 | 531 | 299.024 | first_order (no) | - |
| HSD | cl | r8908 | 532 | 299.325 | first_order (no) | - |
| HSD | cl | r8909 | 539 | 299.374 | first_order (no) | - |
| HSD | cl | r8910 | 533 | 299.364 | first_order (no) | - |
| HSD | cl | r8911 | 519 | 299.046 | first_order (no) | - |
| HSD | cl | r8912 | 533 | 299.109 | first_order (no) | - |
| HSD | cl | r8913 | 540 | 299.382 | first_order (no) | - |
| HSD | cl | r8914 | 538 | 299.365 | first_order (no) | - |
| HSD | cl | r8915 | 522 | 299.168 | first_order (no) | - |
| HSD | cl | r8916 | 533 | 299.024 | first_order (no) | - |
| HSD | cl | r8917 | 538 | 299.379 | first_order (no) | - |
| HSD | cl | r8918 | 542 | 299.364 | first_order (no) | - |
| HSD | cl | r8919 | 518 | 299.083 | first_order (no) | - |
| HSD | cl | r8920 | 532 | 299.074 | first_order (no) | - |
| HSD | cl | r8921 | 538 | 299.375 | first_order (no) | - |
| HSD | cl | r8922 | 522 | 299.16 | first_order (no) | - |
| HSD | cl | r8923 | 534 | 299.053 | first_order (no) | - |
| HSD | cl | r8924 | 539 | 299.375 | first_order (no) | - |
| HSD | cl | r8925 | 542 | 299.379 | first_order (no) | - |
| HSD | cl | r8926 | 526 | 299.028 | first_order (no) | - |
| HSD | cl | r8927 | 534 | 299.383 | first_order (no) | - |
| HSD | cl | r8928 | 528 | 299.232 | first_order (no) | - |
| HSD | cl | r8929 | 530 | 299.278 | first_order (no) | - |
| HSD | cl | r8930 | 529 | 299.377 | first_order (no) | - |
| MT | sv | b0 | 3058 | 0 | - | - |
| MT | sv | r90 | 462 | 299.378 | first_order (no) | friction (no) |
| MT | sv | b1 | 164 | 0 | - | - |
| MT | sv | r8901 | 493 | 299.369 | first_order (no) | friction (no) |
| MT | sv | b2 | 111 | 0 | - | - |
| MT | sv | r8902 | 497 | 299.353 | first_order (no) | friction (no) |
| MT | sv | b3 | 130 | 0 | - | - |
| MT | sv | r8903 | 457 | 299.024 | first_order (no) | - |
| MT | sv | b4 | 184 | 0 | - | - |
| MT | sv | r8904 | 463 | 299.369 | first_order (no) | - |
| MT | sv | b5 | 173 | 0 | - | - |
| MT | sv | r8905 | 493 | 299.375 | first_order (no) | friction (no) |
| MT | sv | b6 | 138 | 0 | - | - |
| MT | sv | r8906 | 482 | 299.249 | first_order (no) | friction (no) |
| MT | sv | b7 | 137 | 0 | - | - |
| MT | sv | r8907 | 460 | 299.024 | first_order (no) | - |
| MT | sv | b8 | 186 | 0 | - | - |
| MT | sv | r8908 | 450 | 299.325 | first_order (no) | - |
| MT | sv | b9 | 161 | 0 | - | - |
| MT | sv | r8909 | 489 | 299.374 | first_order (no) | linear (yes) |
| MT | sv | b10 | 111 | 0 | - | - |
| MT | sv | r8910 | 502 | 299.364 | first_order (no) | friction (no) |
| MT | sv | b11 | 125 | 0 | - | - |
| MT | sv | r8911 | 454 | 299.046 | first_order (no) | friction (no) |
| MT | sv | b12 | 174 | 0 | - | - |
| MT | sv | r8912 | 462 | 299.109 | first_order (no) | - |
| MT | sv | b13 | 184 | 0 | - | - |
| MT | sv | r8913 | 478 | 299.382 | first_order (no) | friction (no) |
| MT | sv | b14 | 131 | 0 | - | - |
| MT | sv | r8914 | 505 | 299.365 | first_order (no) | friction (no) |
| MT | sv | b15 | 111 | 0 | - | - |
| MT | sv | r8915 | 474 | 299.168 | first_order (no) | friction (no) |
| MT | sv | b16 | 164 | 0 | - | - |
| MT | sv | r8916 | 461 | 299.024 | first_order (no) | - |
| MT | sv | b17 | 183 | 0 | - | - |
| MT | sv | r8917 | 469 | 299.379 | first_order (no) | friction (no) |
| MT | sv | b18 | 144 | 0 | - | - |
| MT | sv | r8918 | 509 | 299.364 | first_order (no) | friction (no) |
| MT | sv | b19 | 126 | 0 | - | - |
| MT | sv | r8919 | 459 | 299.083 | first_order (no) | friction (no) |
| MT | sv | b20 | 171 | 0 | - | - |
| MT | sv | r8920 | 459 | 299.074 | first_order (no) | - |
| MT | sv | b21 | 183 | 0 | - | - |
| MT | sv | r8921 | 473 | 299.375 | first_order (no) | linear (yes) |
| MT | sv | b22 | 147 | 0 | - | - |
| MT | sv | r8922 | 471 | 299.16 | first_order (no) | - |
| MT | sv | b23 | 169 | 0 | - | - |
| MT | sv | r8923 | 463 | 299.053 | first_order (no) | - |
| MT | sv | b24 | 186 | 0 | - | - |
| MT | sv | r8924 | 472 | 299.375 | first_order (no) | friction (no) |
| MT | sv | b25 | 130 | 0 | - | - |
| MT | sv | r8925 | 509 | 299.379 | first_order (no) | friction (no) |
| MT | sv | b26 | 135 | 0 | - | - |
| MT | sv | r8926 | 456 | 299.028 | first_order (no) | - |
| MT | sv | b27 | 187 | 0 | - | - |
| MT | sv | r8927 | 463 | 299.383 | first_order (no) | - |
| MT | sv | b28 | 179 | 0 | - | - |
| MT | sv | r8928 | 467 | 299.232 | first_order (no) | - |
| MT | sv | b29 | 156 | 0 | - | - |
| MT | sv | r8929 | 468 | 299.278 | first_order (no) | friction (no) |
| MT | sv | b30 | 126 | 0 | - | - |
| MT | sv | r8930 | 488 | 299.377 | first_order (no) | friction (no) |
| MT | sv | b31 | 139 | 0 | - | - |

Events: 1248. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
