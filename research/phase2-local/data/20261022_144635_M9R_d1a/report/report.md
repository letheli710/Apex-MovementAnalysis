# hsd_tel report

Inputs: 23 file(s); rows: 266171 (MT 175501, HSD 90668)

Validation: 0 error(s), 25 warning(s), 6 info

- warning `W_TELEPORT` message.2.log:3803 teleport in stream ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` message.2.log:4542 teleport in stream ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` message.2.log:5278 teleport in stream ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` message.2.log:6017 teleport in stream ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` message.2.log:6755 teleport in stream ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_MORE` message.2.log:0 126 more teleport rows in ('MT', 'cl', 'cmd', 1, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` script.3.log:3443 teleport in stream ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` script.3.log:4885 teleport in stream ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` script.3.log:6330 teleport in stream ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` script.3.log:7777 teleport in stream ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` script.3.log:9221 teleport in stream ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_MORE` script.3.log:0 126 more teleport rows in ('HSD', 'cl', 'frame', None, '64536050-0254-4d06-8553-40033650dfd4')
- warning `W_TELEPORT` message.2.log:3594 teleport in stream ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` message.2.log:4329 teleport in stream ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` message.2.log:5064 teleport in stream ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` message.2.log:5798 teleport in stream ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` message.2.log:6534 teleport in stream ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_MORE` message.2.log:0 126 more teleport rows in ('MT', 'sv', 'cmd', 1, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` script.log:777 teleport in stream ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` script.log:813 teleport in stream ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` script.log:825 teleport in stream ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` script.log:837 teleport in stream ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TELEPORT` script.log:851 teleport in stream ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_MORE` script.log:0 13 more teleport rows in ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.8 -> 23.62009 in ('HSD', 'sv', 'evt', 1.0, '9b309c68-c0b5-4fbe-99e0-ad346742053a')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 3218 | 0 | - | - |
| MT | cl | r90 | 562 | 423.486 | first_order (no) | linear (no) |
| MT | cl | b1 | 171 | 0 | - | - |
| MT | cl | r15001 | 561 | 422.2 | first_order (no) | linear (no) |
| MT | cl | b2 | 173 | 0 | - | - |
| MT | cl | r15002 | 562 | 421.348 | first_order (no) | linear (no) |
| MT | cl | b3 | 173 | 0 | - | - |
| MT | cl | r15003 | 562 | 420.973 | first_order (no) | linear (no) |
| MT | cl | b4 | 172 | 0 | - | - |
| MT | cl | r15004 | 563 | 422.218 | first_order (no) | linear (no) |
| MT | cl | b5 | 171 | 0 | - | - |
| MT | cl | r15005 | 564 | 421.117 | first_order (no) | friction (no) |
| MT | cl | b6 | 171 | 0 | - | - |
| MT | cl | r15006 | 623 | 460.428 | first_order (no) | linear (no) |
| MT | cl | b7 | 171 | 0 | - | - |
| MT | cl | r15007 | 624 | 460.428 | first_order (no) | linear (no) |
| MT | cl | b8 | 171 | 0 | - | - |
| MT | cl | r15008 | 623 | 460.428 | first_order (no) | linear (no) |
| MT | cl | b9 | 172 | 0 | - | - |
| MT | cl | r15009 | 616 | 460.427 | first_order (no) | linear (no) |
| MT | cl | b10 | 178 | 0 | - | - |
| MT | cl | r15010 | 623 | 460.427 | first_order (no) | linear (no) |
| MT | cl | b11 | 172 | 0 | - | - |
| MT | cl | r15011 | 742 | 460.429 | first_order (no) | linear (no) |
| MT | cl | b12 | 171 | 0 | - | - |
| MT | cl | r15012 | 742 | 460.423 | first_order (no) | linear (no) |
| MT | cl | b13 | 173 | 0 | - | - |
| MT | cl | r15013 | 741 | 460.427 | first_order (no) | linear (no) |
| MT | cl | b14 | 173 | 0 | - | - |
| MT | cl | r15014 | 744 | 460.427 | first_order (no) | friction (no) |
| MT | cl | b15 | 171 | 0 | - | - |
| MT | cl | r15015 | 742 | 460.418 | first_order (no) | linear (no) |
| MT | cl | b16 | 171 | 0 | - | - |
| MT | cl | r15016 | 575 | 457.803 | first_order (no) | - |
| MT | cl | b17 | 190 | 0 | - | - |
| MT | cl | r15017 | 576 | 457.803 | first_order (no) | - |
| MT | cl | b18 | 188 | 0 | - | - |
| MT | cl | r15018 | 575 | 457.805 | first_order (no) | - |
| MT | cl | b19 | 190 | 0 | - | - |
| MT | cl | r15019 | 577 | 457.803 | first_order (no) | - |
| MT | cl | b20 | 187 | 0 | - | - |
| MT | cl | r15020 | 576 | 457.803 | first_order (no) | - |
| MT | cl | b21 | 189 | 0 | - | - |
| MT | cl | r15021 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b22 | 166 | 0 | - | - |
| MT | cl | r15022 | 541 | 460.429 | first_order (no) | linear (no) |
| MT | cl | b23 | 193 | 0 | - | - |
| MT | cl | r15023 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b24 | 193 | 0 | - | - |
| MT | cl | r15024 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b25 | 193 | 0 | - | - |
| MT | cl | r15025 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | cl | b26 | 192 | 0 | - | - |
| MT | cl | r15026 | 556 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b27 | 166 | 0 | - | - |
| MT | cl | r15027 | 562 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b28 | 194 | 0 | - | - |
| MT | cl | r15028 | 555 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b29 | 166 | 0 | - | - |
| MT | cl | r15029 | 562 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b30 | 193 | 0 | - | - |
| MT | cl | r15030 | 556 | 299.15 | first_order (no) | linear (no) |
| MT | cl | b31 | 168 | 0 | - | - |
| MT | cl | r15031 | 578 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b32 | 165 | 0 | - | - |
| MT | cl | r15032 | 578 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b33 | 166 | 0 | - | - |
| MT | cl | r15033 | 580 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b34 | 194 | 0 | - | - |
| MT | cl | r15034 | 580 | 299.152 | first_order (no) | linear (no) |
| MT | cl | b35 | 193 | 0 | - | - |
| MT | cl | r15035 | 581 | 299.151 | first_order (no) | linear (no) |
| MT | cl | b36 | 17319 | 278.239 | - | linear (yes) |
| MT | cl | r15036 | 540 | 455.095 | first_order (no) | linear (no) |
| MT | cl | r15037 | 540 | 455.094 | first_order (no) | linear (no) |
| MT | cl | r15038 | 540 | 455.101 | first_order (no) | linear (no) |
| MT | cl | r15039 | 540 | 455.096 | first_order (no) | linear (no) |
| MT | cl | r15040 | 540 | 455.095 | first_order (no) | linear (no) |
| MT | cl | r15041 | 540 | 299 | first_order (no) | linear (yes) |
| MT | cl | r15042 | 540 | 299 | first_order (no) | linear (yes) |
| MT | cl | r15043 | 540 | 299 | first_order (no) | linear (yes) |
| MT | cl | r15044 | 540 | 299 | first_order (no) | linear (yes) |
| MT | cl | r15045 | 540 | 299 | first_order (no) | linear (yes) |
| MT | cl | r15046 | 540 | 408.108 | first_order (no) | linear (no) |
| MT | cl | r15047 | 540 | 407.061 | first_order (no) | linear (no) |
| MT | cl | r15048 | 540 | 407.373 | first_order (no) | linear (no) |
| MT | cl | r15049 | 540 | 406.886 | first_order (no) | linear (no) |
| MT | cl | r15050 | 540 | 406.921 | first_order (no) | linear (no) |
| MT | cl | r15051 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | cl | r15052 | 324 | 199.574 | first_order (yes) | friction (no) |
| MT | cl | r15053 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | cl | r15054 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | cl | r15055 | 324 | 199.575 | first_order (yes) | linear (no) |
| MT | cl | r15056 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | cl | r15057 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | cl | r15058 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | cl | r15059 | 334 | 199.573 | first_order (yes) | friction (no) |
| MT | cl | r15060 | 334 | 199.572 | first_order (yes) | linear (no) |
| MT | cl | r15061 | 324 | 296.78 | first_order (no) | friction (no) |
| MT | cl | r15062 | 324 | 297.93 | first_order (no) | friction (no) |
| MT | cl | r15063 | 324 | 296.627 | first_order (no) | friction (no) |
| MT | cl | r15064 | 324 | 296.927 | first_order (no) | friction (no) |
| MT | cl | r15065 | 324 | 296.727 | first_order (no) | friction (no) |
| MT | cl | r15066 | 332 | 299.02 | first_order (no) | friction (no) |
| MT | cl | r15067 | 333 | 299.029 | first_order (no) | friction (no) |
| MT | cl | r15068 | 334 | 299.027 | first_order (no) | friction (no) |
| MT | cl | r15069 | 334 | 299.027 | first_order (no) | friction (no) |
| MT | cl | r15070 | 334 | 296.741 | first_order (no) | friction (no) |
| MT | cl | r15071 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | cl | r15072 | 516 | 457.802 | first_order (no) | friction (no) |
| MT | cl | r15073 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | cl | r15074 | 516 | 457.799 | first_order (no) | friction (no) |
| MT | cl | r15075 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | cl | r15076 | 526 | 457.771 | first_order (no) | friction (no) |
| MT | cl | r15077 | 526 | 457.807 | first_order (no) | friction (no) |
| MT | cl | r15078 | 526 | 457.825 | first_order (no) | friction (no) |
| MT | cl | r15079 | 526 | 457.811 | first_order (no) | friction (no) |
| MT | cl | r15080 | 526 | 457.803 | first_order (no) | friction (no) |
| MT | cl | r15081 | 376 | 299.062 | first_order (yes) | linear (no) |
| MT | cl | r15082 | 376 | 299.054 | first_order (yes) | linear (no) |
| MT | cl | r15083 | 376 | 299.065 | first_order (yes) | linear (no) |
| MT | cl | r15084 | 376 | 299.057 | first_order (yes) | linear (no) |
| MT | cl | r15085 | 376 | 299.061 | first_order (yes) | linear (no) |
| MT | cl | r15086 | 376 | 368.118 | first_order (no) | linear (yes) |
| MT | cl | r15087 | 376 | 368.118 | first_order (no) | linear (yes) |
| MT | cl | r15088 | 376 | 368.122 | first_order (no) | linear (yes) |
| MT | cl | r15089 | 376 | 368.122 | first_order (no) | linear (yes) |
| MT | cl | r15090 | 376 | 368.116 | first_order (no) | linear (yes) |
| MT | cl | r15091 | 382 | 298.734 | first_order (yes) | linear (no) |
| MT | cl | r15092 | 382 | 299.06 | first_order (yes) | linear (no) |
| MT | cl | r15093 | 382 | 299.054 | first_order (yes) | linear (no) |
| MT | cl | r15094 | 382 | 299.061 | first_order (yes) | linear (no) |
| MT | cl | r15095 | 382 | 299.063 | first_order (yes) | linear (no) |
| MT | cl | r15096 | 382 | 368.122 | first_order (no) | linear (yes) |
| MT | cl | r15097 | 382 | 368.115 | first_order (no) | linear (yes) |
| MT | cl | r15098 | 382 | 368.116 | first_order (no) | linear (yes) |
| MT | cl | r15099 | 382 | 368.117 | first_order (no) | linear (yes) |
| MT | cl | r15100 | 382 | 368.121 | first_order (yes) | linear (yes) |
| MT | cl | r15101 | 394 | 298.726 | first_order (yes) | linear (no) |
| MT | cl | r15102 | 394 | 298.733 | first_order (yes) | linear (no) |
| MT | cl | r15103 | 394 | 299.055 | first_order (yes) | linear (no) |
| MT | cl | r15104 | 394 | 299.05 | first_order (yes) | linear (no) |
| MT | cl | r15105 | 394 | 299.064 | first_order (yes) | linear (no) |
| MT | cl | r15106 | 394 | 368.114 | first_order (yes) | linear (yes) |
| MT | cl | r15107 | 394 | 368.121 | first_order (yes) | linear (yes) |
| MT | cl | r15108 | 394 | 368.121 | first_order (yes) | linear (yes) |
| MT | cl | r15109 | 394 | 368.12 | first_order (yes) | linear (yes) |
| MT | cl | r15110 | 394 | 368.116 | first_order (yes) | linear (yes) |
| MT | cl | r15111 | 533 | 457.812 | first_order (no) | linear (no) |
| MT | cl | r15112 | 533 | 457.811 | first_order (no) | linear (no) |
| MT | cl | r15113 | 533 | 457.812 | first_order (no) | linear (no) |
| MT | cl | r15114 | 533 | 457.811 | first_order (no) | linear (no) |
| MT | cl | r15115 | 533 | 457.806 | first_order (no) | linear (no) |
| MT | cl | r15116 | 337 | 299 | first_order (no) | - |
| MT | cl | r15117 | 337 | 299 | first_order (no) | - |
| MT | cl | r15118 | 337 | 299 | first_order (no) | - |
| MT | cl | r15119 | 337 | 299.27 | first_order (no) | - |
| MT | cl | r15120 | 337 | 299 | first_order (no) | - |
| MT | cl | r15121 | 337 | 296.455 | first_order (no) | friction (no) |
| MT | cl | r15122 | 337 | 295.978 | first_order (no) | friction (no) |
| MT | cl | r15123 | 337 | 296.456 | first_order (no) | friction (no) |
| MT | cl | r15124 | 337 | 296.19 | first_order (no) | friction (no) |
| MT | cl | r15125 | 337 | 296.447 | first_order (no) | friction (no) |
| MT | cl | r15126 | 326 | 299.142 | first_order (no) | - |
| MT | cl | r15127 | 326 | 296.35 | first_order (no) | - |
| MT | cl | r15128 | 326 | 296.502 | first_order (no) | - |
| MT | cl | r15129 | 326 | 296.227 | first_order (no) | - |
| MT | cl | r15130 | 326 | 296.591 | first_order (no) | - |
| HSD | cl | r0 | 26750 | 288.621 | - | linear (yes) |
| HSD | cl | r90 | 625 | 423.486 | first_order (no) | friction (no) |
| HSD | cl | r15001 | 624 | 422.2 | first_order (no) | friction (no) |
| HSD | cl | r15002 | 625 | 421.348 | first_order (no) | friction (no) |
| HSD | cl | r15003 | 625 | 420.973 | first_order (no) | friction (no) |
| HSD | cl | r15004 | 626 | 422.218 | first_order (no) | friction (no) |
| HSD | cl | r15005 | 627 | 421.117 | first_order (no) | friction (no) |
| HSD | cl | r15006 | 686 | 460.428 | first_order (no) | friction (no) |
| HSD | cl | r15007 | 687 | 460.428 | first_order (no) | friction (no) |
| HSD | cl | r15008 | 686 | 460.428 | first_order (no) | friction (no) |
| HSD | cl | r15009 | 679 | 460.427 | first_order (no) | friction (no) |
| HSD | cl | r15010 | 686 | 460.427 | first_order (no) | friction (no) |
| HSD | cl | r15011 | 805 | 460.429 | first_order (no) | friction (no) |
| HSD | cl | r15012 | 805 | 460.423 | first_order (no) | friction (no) |
| HSD | cl | r15013 | 804 | 460.427 | first_order (no) | friction (no) |
| HSD | cl | r15014 | 807 | 460.427 | first_order (no) | friction (no) |
| HSD | cl | r15015 | 805 | 460.418 | first_order (no) | friction (no) |
| HSD | cl | r15016 | 638 | 457.803 | first_order (no) | - |
| HSD | cl | r15017 | 639 | 457.803 | first_order (no) | - |
| HSD | cl | r15018 | 638 | 457.805 | first_order (no) | - |
| HSD | cl | r15019 | 640 | 457.803 | first_order (no) | - |
| HSD | cl | r15020 | 639 | 457.803 | first_order (no) | - |
| HSD | cl | r15021 | 602 | 460.428 | - | friction (no) |
| HSD | cl | r15022 | 604 | 460.429 | - | linear (no) |
| HSD | cl | r15023 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r15024 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r15025 | 605 | 460.428 | - | friction (no) |
| HSD | cl | r15026 | 602 | 299.151 | first_order (no) | - |
| HSD | cl | r15027 | 604 | 299.152 | first_order (no) | - |
| HSD | cl | r15028 | 601 | 299.15 | first_order (no) | - |
| HSD | cl | r15029 | 604 | 299.152 | first_order (no) | - |
| HSD | cl | r15030 | 601 | 299.15 | first_order (no) | - |
| HSD | cl | r15031 | 602 | 299.151 | first_order (no) | - |
| HSD | cl | r15032 | 602 | 299.151 | first_order (no) | - |
| HSD | cl | r15033 | 604 | 299.152 | first_order (no) | - |
| HSD | cl | r15034 | 604 | 299.152 | first_order (no) | - |
| HSD | cl | r15035 | 605 | 299.151 | first_order (no) | - |
| HSD | cl | r15036 | 540 | 455.095 | first_order (no) | linear (no) |
| HSD | cl | r15037 | 540 | 455.094 | first_order (no) | linear (no) |
| HSD | cl | r15038 | 540 | 455.101 | first_order (no) | linear (no) |
| HSD | cl | r15039 | 540 | 455.096 | first_order (no) | linear (no) |
| HSD | cl | r15040 | 540 | 455.095 | first_order (no) | linear (no) |
| HSD | cl | r15041 | 540 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r15042 | 540 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r15043 | 540 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r15044 | 540 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r15045 | 540 | 299 | first_order (no) | linear (yes) |
| HSD | cl | r15046 | 540 | 408.108 | first_order (no) | linear (no) |
| HSD | cl | r15047 | 540 | 407.061 | first_order (no) | linear (no) |
| HSD | cl | r15048 | 540 | 407.373 | first_order (no) | linear (no) |
| HSD | cl | r15049 | 540 | 406.886 | first_order (no) | linear (no) |
| HSD | cl | r15050 | 540 | 406.921 | first_order (no) | linear (no) |
| HSD | cl | r15051 | 324 | 199.575 | first_order (yes) | linear (yes) |
| HSD | cl | r15052 | 324 | 199.574 | first_order (yes) | linear (yes) |
| HSD | cl | r15053 | 324 | 199.575 | first_order (yes) | linear (yes) |
| HSD | cl | r15054 | 324 | 199.575 | first_order (yes) | linear (yes) |
| HSD | cl | r15055 | 324 | 199.575 | first_order (yes) | linear (yes) |
| HSD | cl | r15056 | 334 | 199.572 | first_order (yes) | linear (yes) |
| HSD | cl | r15057 | 334 | 199.572 | first_order (yes) | linear (yes) |
| HSD | cl | r15058 | 334 | 199.572 | first_order (yes) | linear (yes) |
| HSD | cl | r15059 | 334 | 199.573 | first_order (yes) | linear (yes) |
| HSD | cl | r15060 | 334 | 199.572 | first_order (yes) | linear (yes) |
| HSD | cl | r15061 | 324 | 296.78 | first_order (no) | friction (no) |
| HSD | cl | r15062 | 324 | 297.93 | first_order (no) | friction (no) |
| HSD | cl | r15063 | 324 | 296.627 | first_order (no) | friction (no) |
| HSD | cl | r15064 | 324 | 296.927 | first_order (no) | friction (no) |
| HSD | cl | r15065 | 324 | 296.727 | first_order (no) | friction (no) |
| HSD | cl | r15066 | 334 | 299.02 | first_order (no) | friction (no) |
| HSD | cl | r15067 | 334 | 299.029 | first_order (no) | friction (no) |
| HSD | cl | r15068 | 334 | 299.027 | first_order (no) | friction (no) |
| HSD | cl | r15069 | 334 | 299.027 | first_order (no) | friction (no) |
| HSD | cl | r15070 | 334 | 296.741 | first_order (no) | linear (yes) |
| HSD | cl | r15071 | 516 | 457.803 | first_order (no) | friction (no) |
| HSD | cl | r15072 | 516 | 457.802 | first_order (no) | friction (no) |
| HSD | cl | r15073 | 516 | 457.803 | first_order (no) | friction (no) |
| HSD | cl | r15074 | 516 | 457.799 | first_order (no) | friction (no) |
| HSD | cl | r15075 | 516 | 457.803 | first_order (no) | friction (no) |
| HSD | cl | r15076 | 526 | 457.771 | first_order (no) | linear (yes) |
| HSD | cl | r15077 | 526 | 457.807 | first_order (no) | linear (yes) |
| HSD | cl | r15078 | 526 | 457.825 | first_order (no) | linear (yes) |
| HSD | cl | r15079 | 526 | 457.811 | first_order (no) | linear (yes) |
| HSD | cl | r15080 | 526 | 457.803 | first_order (no) | linear (yes) |
| HSD | cl | r15081 | 376 | 299.062 | first_order (yes) | linear (no) |
| HSD | cl | r15082 | 376 | 299.054 | first_order (yes) | linear (no) |
| HSD | cl | r15083 | 376 | 299.065 | first_order (yes) | linear (no) |
| HSD | cl | r15084 | 376 | 299.057 | first_order (yes) | linear (no) |
| HSD | cl | r15085 | 376 | 299.061 | first_order (yes) | linear (no) |
| HSD | cl | r15086 | 376 | 368.118 | first_order (no) | linear (yes) |
| HSD | cl | r15087 | 376 | 368.118 | first_order (no) | linear (yes) |
| HSD | cl | r15088 | 376 | 368.122 | first_order (no) | linear (yes) |
| HSD | cl | r15089 | 376 | 368.122 | first_order (no) | linear (yes) |
| HSD | cl | r15090 | 376 | 368.116 | first_order (no) | linear (yes) |
| HSD | cl | r15091 | 382 | 298.734 | first_order (yes) | linear (no) |
| HSD | cl | r15092 | 382 | 299.06 | first_order (yes) | linear (no) |
| HSD | cl | r15093 | 382 | 299.054 | first_order (yes) | linear (no) |
| HSD | cl | r15094 | 382 | 299.061 | first_order (yes) | linear (no) |
| HSD | cl | r15095 | 382 | 299.063 | first_order (yes) | linear (no) |
| HSD | cl | r15096 | 382 | 368.122 | first_order (no) | linear (yes) |
| HSD | cl | r15097 | 382 | 368.115 | first_order (no) | linear (yes) |
| HSD | cl | r15098 | 382 | 368.116 | first_order (no) | linear (yes) |
| HSD | cl | r15099 | 382 | 368.117 | first_order (no) | linear (yes) |
| HSD | cl | r15100 | 382 | 368.121 | first_order (yes) | linear (yes) |
| HSD | cl | r15101 | 394 | 298.726 | first_order (yes) | linear (no) |
| HSD | cl | r15102 | 394 | 298.733 | first_order (yes) | linear (no) |
| HSD | cl | r15103 | 394 | 299.055 | first_order (yes) | linear (no) |
| HSD | cl | r15104 | 394 | 299.05 | first_order (yes) | linear (no) |
| HSD | cl | r15105 | 394 | 299.064 | first_order (yes) | linear (no) |
| HSD | cl | r15106 | 394 | 368.114 | first_order (yes) | linear (yes) |
| HSD | cl | r15107 | 394 | 368.121 | first_order (yes) | linear (yes) |
| HSD | cl | r15108 | 394 | 368.121 | first_order (yes) | linear (yes) |
| HSD | cl | r15109 | 394 | 368.12 | first_order (yes) | linear (yes) |
| HSD | cl | r15110 | 394 | 368.116 | first_order (yes) | linear (yes) |
| HSD | cl | r15111 | 533 | 457.812 | first_order (no) | linear (no) |
| HSD | cl | r15112 | 533 | 457.811 | first_order (no) | linear (no) |
| HSD | cl | r15113 | 533 | 457.812 | first_order (no) | linear (no) |
| HSD | cl | r15114 | 533 | 457.811 | first_order (no) | linear (no) |
| HSD | cl | r15115 | 533 | 457.806 | first_order (no) | linear (no) |
| HSD | cl | r15116 | 337 | 299 | first_order (no) | - |
| HSD | cl | r15117 | 337 | 299 | first_order (no) | - |
| HSD | cl | r15118 | 337 | 299 | first_order (no) | - |
| HSD | cl | r15119 | 337 | 299.27 | first_order (no) | - |
| HSD | cl | r15120 | 337 | 299 | first_order (no) | - |
| HSD | cl | r15121 | 337 | 296.455 | first_order (no) | friction (no) |
| HSD | cl | r15122 | 337 | 295.978 | first_order (no) | friction (no) |
| HSD | cl | r15123 | 337 | 296.456 | first_order (no) | friction (no) |
| HSD | cl | r15124 | 337 | 296.19 | first_order (no) | friction (no) |
| HSD | cl | r15125 | 337 | 296.447 | first_order (no) | friction (no) |
| HSD | cl | r15126 | 326 | 299.142 | first_order (no) | - |
| HSD | cl | r15127 | 326 | 296.35 | first_order (no) | - |
| HSD | cl | r15128 | 326 | 296.502 | first_order (no) | - |
| HSD | cl | r15129 | 326 | 296.227 | first_order (no) | - |
| HSD | cl | r15130 | 326 | 296.591 | first_order (no) | - |
| MT | sv | b0 | 3232 | 0 | - | - |
| MT | sv | r90 | 562 | 423.486 | first_order (no) | linear (no) |
| MT | sv | b1 | 171 | 0 | - | - |
| MT | sv | r15001 | 561 | 422.2 | first_order (no) | linear (no) |
| MT | sv | b2 | 173 | 0 | - | - |
| MT | sv | r15002 | 562 | 421.348 | first_order (no) | linear (no) |
| MT | sv | b3 | 173 | 0 | - | - |
| MT | sv | r15003 | 562 | 420.973 | first_order (no) | linear (no) |
| MT | sv | b4 | 172 | 0 | - | - |
| MT | sv | r15004 | 563 | 422.218 | first_order (no) | linear (no) |
| MT | sv | b5 | 171 | 0 | - | - |
| MT | sv | r15005 | 564 | 421.117 | first_order (no) | friction (no) |
| MT | sv | b6 | 171 | 0 | - | - |
| MT | sv | r15006 | 623 | 460.428 | first_order (no) | linear (no) |
| MT | sv | b7 | 171 | 0 | - | - |
| MT | sv | r15007 | 624 | 460.428 | first_order (no) | linear (no) |
| MT | sv | b8 | 171 | 0 | - | - |
| MT | sv | r15008 | 623 | 460.428 | first_order (no) | linear (no) |
| MT | sv | b9 | 172 | 0 | - | - |
| MT | sv | r15009 | 616 | 460.427 | first_order (no) | linear (no) |
| MT | sv | b10 | 178 | 0 | - | - |
| MT | sv | r15010 | 623 | 460.427 | first_order (no) | linear (no) |
| MT | sv | b11 | 172 | 0 | - | - |
| MT | sv | r15011 | 742 | 460.429 | first_order (no) | linear (no) |
| MT | sv | b12 | 171 | 0 | - | - |
| MT | sv | r15012 | 742 | 460.423 | first_order (no) | linear (no) |
| MT | sv | b13 | 173 | 0 | - | - |
| MT | sv | r15013 | 741 | 460.427 | first_order (no) | linear (no) |
| MT | sv | b14 | 173 | 0 | - | - |
| MT | sv | r15014 | 744 | 460.427 | first_order (no) | friction (no) |
| MT | sv | b15 | 171 | 0 | - | - |
| MT | sv | r15015 | 742 | 460.418 | first_order (no) | linear (no) |
| MT | sv | b16 | 171 | 0 | - | - |
| MT | sv | r15016 | 575 | 457.803 | first_order (no) | - |
| MT | sv | b17 | 190 | 0 | - | - |
| MT | sv | r15017 | 576 | 457.803 | first_order (no) | - |
| MT | sv | b18 | 188 | 0 | - | - |
| MT | sv | r15018 | 575 | 457.805 | first_order (no) | - |
| MT | sv | b19 | 190 | 0 | - | - |
| MT | sv | r15019 | 577 | 457.803 | first_order (no) | - |
| MT | sv | b20 | 187 | 0 | - | - |
| MT | sv | r15020 | 576 | 457.803 | first_order (no) | - |
| MT | sv | b21 | 189 | 0 | - | - |
| MT | sv | r15021 | 539 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b22 | 166 | 0 | - | - |
| MT | sv | r15022 | 541 | 460.429 | first_order (no) | linear (no) |
| MT | sv | b23 | 193 | 0 | - | - |
| MT | sv | r15023 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b24 | 193 | 0 | - | - |
| MT | sv | r15024 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b25 | 193 | 0 | - | - |
| MT | sv | r15025 | 542 | 460.428 | first_order (no) | friction (no) |
| MT | sv | b26 | 192 | 0 | - | - |
| MT | sv | r15026 | 556 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b27 | 166 | 0 | - | - |
| MT | sv | r15027 | 562 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b28 | 194 | 0 | - | - |
| MT | sv | r15028 | 555 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b29 | 166 | 0 | - | - |
| MT | sv | r15029 | 562 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b30 | 193 | 0 | - | - |
| MT | sv | r15030 | 556 | 299.15 | first_order (no) | linear (no) |
| MT | sv | b31 | 168 | 0 | - | - |
| MT | sv | r15031 | 578 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b32 | 165 | 0 | - | - |
| MT | sv | r15032 | 578 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b33 | 166 | 0 | - | - |
| MT | sv | r15033 | 580 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b34 | 194 | 0 | - | - |
| MT | sv | r15034 | 580 | 299.152 | first_order (no) | linear (no) |
| MT | sv | b35 | 193 | 0 | - | - |
| MT | sv | r15035 | 581 | 299.151 | first_order (no) | linear (no) |
| MT | sv | b36 | 17315 | 278.239 | - | linear (yes) |
| MT | sv | r15036 | 540 | 455.095 | first_order (no) | linear (no) |
| MT | sv | r15037 | 540 | 455.094 | first_order (no) | linear (no) |
| MT | sv | r15038 | 540 | 455.101 | first_order (no) | linear (no) |
| MT | sv | r15039 | 540 | 455.096 | first_order (no) | linear (no) |
| MT | sv | r15040 | 540 | 455.095 | first_order (no) | linear (no) |
| MT | sv | r15041 | 540 | 299 | first_order (no) | linear (yes) |
| MT | sv | r15042 | 540 | 299 | first_order (no) | linear (yes) |
| MT | sv | r15043 | 540 | 299 | first_order (no) | linear (yes) |
| MT | sv | r15044 | 540 | 299 | first_order (no) | linear (yes) |
| MT | sv | r15045 | 540 | 299 | first_order (no) | linear (yes) |
| MT | sv | r15046 | 540 | 408.108 | first_order (no) | linear (no) |
| MT | sv | r15047 | 540 | 407.061 | first_order (no) | linear (no) |
| MT | sv | r15048 | 540 | 407.373 | first_order (no) | linear (no) |
| MT | sv | r15049 | 540 | 406.886 | first_order (no) | linear (no) |
| MT | sv | r15050 | 540 | 406.921 | first_order (no) | linear (no) |
| MT | sv | r15051 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | sv | r15052 | 324 | 199.574 | first_order (yes) | friction (no) |
| MT | sv | r15053 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | sv | r15054 | 324 | 199.575 | first_order (yes) | friction (no) |
| MT | sv | r15055 | 324 | 199.575 | first_order (yes) | linear (no) |
| MT | sv | r15056 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | sv | r15057 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | sv | r15058 | 334 | 199.572 | first_order (yes) | friction (no) |
| MT | sv | r15059 | 334 | 199.573 | first_order (yes) | friction (no) |
| MT | sv | r15060 | 334 | 199.572 | first_order (yes) | linear (no) |
| MT | sv | r15061 | 324 | 296.78 | first_order (no) | friction (no) |
| MT | sv | r15062 | 324 | 297.93 | first_order (no) | friction (no) |
| MT | sv | r15063 | 324 | 296.627 | first_order (no) | friction (no) |
| MT | sv | r15064 | 324 | 296.927 | first_order (no) | friction (no) |
| MT | sv | r15065 | 324 | 296.727 | first_order (no) | friction (no) |
| MT | sv | r15066 | 332 | 299.02 | first_order (no) | friction (no) |
| MT | sv | r15067 | 333 | 299.029 | first_order (no) | friction (no) |
| MT | sv | r15068 | 334 | 299.027 | first_order (no) | friction (no) |
| MT | sv | r15069 | 334 | 299.027 | first_order (no) | friction (no) |
| MT | sv | r15070 | 334 | 296.741 | first_order (no) | friction (no) |
| MT | sv | r15071 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | sv | r15072 | 516 | 457.802 | first_order (no) | friction (no) |
| MT | sv | r15073 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | sv | r15074 | 516 | 457.799 | first_order (no) | friction (no) |
| MT | sv | r15075 | 516 | 457.803 | first_order (no) | friction (no) |
| MT | sv | r15076 | 526 | 457.771 | first_order (no) | friction (no) |
| MT | sv | r15077 | 526 | 457.807 | first_order (no) | friction (no) |
| MT | sv | r15078 | 526 | 457.825 | first_order (no) | friction (no) |
| MT | sv | r15079 | 526 | 457.811 | first_order (no) | friction (no) |
| MT | sv | r15080 | 526 | 457.803 | first_order (no) | friction (no) |
| MT | sv | r15081 | 376 | 299.062 | first_order (yes) | linear (no) |
| MT | sv | r15082 | 376 | 299.054 | first_order (yes) | linear (no) |
| MT | sv | r15083 | 376 | 299.065 | first_order (yes) | linear (no) |
| MT | sv | r15084 | 376 | 299.057 | first_order (yes) | linear (no) |
| MT | sv | r15085 | 376 | 299.061 | first_order (yes) | linear (no) |
| MT | sv | r15086 | 376 | 368.118 | first_order (no) | linear (yes) |
| MT | sv | r15087 | 376 | 368.118 | first_order (no) | linear (yes) |
| MT | sv | r15088 | 376 | 368.122 | first_order (no) | linear (yes) |
| MT | sv | r15089 | 376 | 368.122 | first_order (no) | linear (yes) |
| MT | sv | r15090 | 376 | 368.116 | first_order (no) | linear (yes) |
| MT | sv | r15091 | 382 | 298.734 | first_order (yes) | linear (no) |
| MT | sv | r15092 | 382 | 299.06 | first_order (yes) | linear (no) |
| MT | sv | r15093 | 382 | 299.054 | first_order (yes) | linear (no) |
| MT | sv | r15094 | 382 | 299.061 | first_order (yes) | linear (no) |
| MT | sv | r15095 | 382 | 299.063 | first_order (yes) | linear (no) |
| MT | sv | r15096 | 382 | 368.122 | first_order (no) | linear (yes) |
| MT | sv | r15097 | 382 | 368.115 | first_order (no) | linear (yes) |
| MT | sv | r15098 | 382 | 368.116 | first_order (no) | linear (yes) |
| MT | sv | r15099 | 382 | 368.118 | first_order (no) | linear (yes) |
| MT | sv | r15100 | 382 | 368.121 | first_order (yes) | linear (yes) |
| MT | sv | r15101 | 394 | 298.726 | first_order (yes) | linear (no) |
| MT | sv | r15102 | 394 | 298.733 | first_order (yes) | linear (no) |
| MT | sv | r15103 | 394 | 299.055 | first_order (yes) | linear (no) |
| MT | sv | r15104 | 394 | 299.05 | first_order (yes) | linear (no) |
| MT | sv | r15105 | 394 | 299.064 | first_order (yes) | linear (no) |
| MT | sv | r15106 | 394 | 368.114 | first_order (yes) | linear (yes) |
| MT | sv | r15107 | 394 | 368.121 | first_order (yes) | linear (yes) |
| MT | sv | r15108 | 394 | 368.121 | first_order (yes) | linear (yes) |
| MT | sv | r15109 | 394 | 368.12 | first_order (yes) | linear (yes) |
| MT | sv | r15110 | 394 | 368.116 | first_order (yes) | linear (yes) |
| MT | sv | r15111 | 533 | 457.812 | first_order (no) | linear (no) |
| MT | sv | r15112 | 533 | 457.811 | first_order (no) | linear (no) |
| MT | sv | r15113 | 533 | 457.812 | first_order (no) | linear (no) |
| MT | sv | r15114 | 533 | 457.811 | first_order (no) | linear (no) |
| MT | sv | r15115 | 533 | 457.806 | first_order (no) | linear (no) |
| MT | sv | r15116 | 337 | 299 | first_order (no) | - |
| MT | sv | r15117 | 337 | 299 | first_order (no) | - |
| MT | sv | r15118 | 337 | 299 | first_order (no) | - |
| MT | sv | r15119 | 337 | 299.27 | first_order (no) | - |
| MT | sv | r15120 | 337 | 299 | first_order (no) | - |
| MT | sv | r15121 | 337 | 296.455 | first_order (no) | friction (no) |
| MT | sv | r15122 | 337 | 295.978 | first_order (no) | friction (no) |
| MT | sv | r15123 | 337 | 296.456 | first_order (no) | friction (no) |
| MT | sv | r15124 | 337 | 296.19 | first_order (no) | friction (no) |
| MT | sv | r15125 | 337 | 296.447 | first_order (no) | friction (no) |
| MT | sv | r15126 | 326 | 299.142 | first_order (no) | - |
| MT | sv | r15127 | 326 | 296.35 | first_order (no) | - |
| MT | sv | r15128 | 326 | 296.502 | first_order (no) | - |
| MT | sv | r15129 | 326 | 296.227 | first_order (no) | - |
| MT | sv | r15130 | 326 | 296.591 | first_order (no) | - |

Events: 2275. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
