# hsd_tel report

Inputs: 20 file(s); rows: 177506 (MT 116775, HSD 60729)

Validation: 0 error(s), 19 warning(s), 6 info

- warning `W_TELEPORT` message.1.log:3677 teleport in stream ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` message.1.log:4715 teleport in stream ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` message.1.log:5741 teleport in stream ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` message.1.log:6814 teleport in stream ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` message.1.log:7906 teleport in stream ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_MORE` message.1.log:0 51 more teleport rows in ('MT', 'cl', 'cmd', 1, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` script.2.log:3328 teleport in stream ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` script.2.log:4787 teleport in stream ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` script.2.log:6247 teleport in stream ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` script.2.log:7713 teleport in stream ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` script.2.log:9181 teleport in stream ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_MORE` script.2.log:0 51 more teleport rows in ('HSD', 'cl', 'frame', None, '5b161ed0-d68e-452b-bfb4-c5dc494b5586')
- warning `W_TELEPORT` message.1.log:3467 teleport in stream ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_TELEPORT` message.1.log:4287 teleport in stream ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_TELEPORT` message.1.log:5107 teleport in stream ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_TELEPORT` message.1.log:5926 teleport in stream ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_TELEPORT` message.1.log:6746 teleport in stream ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_MORE` message.1.log:0 51 more teleport rows in ('MT', 'sv', 'cmd', 1, '79dc89f8-c3b6-4b57-a072-191d726305a3')
- warning `W_TIME_BACKWARDS` script.log:713 t 23.35 -> 23.14184 in ('HSD', 'sv', 'evt', 1.0, '79dc89f8-c3b6-4b57-a072-191d726305a3')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5105 | 0 | - | - |
| MT | cl | r90 | 625 | 299.151 | first_order (no) | - |
| MT | cl | r36000 | 625 | 299.147 | first_order (no) | - |
| MT | cl | r36001 | 629 | 299.15 | first_order (no) | - |
| MT | cl | r36002 | 633 | 299.146 | first_order (no) | - |
| MT | cl | r36003 | 637 | 299.15 | first_order (no) | - |
| MT | cl | r36004 | 641 | 299.151 | first_order (no) | - |
| MT | cl | r36005 | 645 | 299.15 | first_order (no) | - |
| MT | cl | r36006 | 649 | 299.147 | first_order (no) | - |
| MT | cl | r36007 | 653 | 299.15 | first_order (no) | - |
| MT | cl | r36008 | 657 | 299.146 | first_order (no) | - |
| MT | cl | r36009 | 661 | 299.15 | first_order (no) | - |
| MT | cl | r36010 | 555 | 299.151 | first_order (no) | friction (no) |
| MT | cl | b1 | 1983 | 0 | - | - |
| MT | cl | r36011 | 625 | 299.147 | first_order (no) | - |
| MT | cl | r36012 | 629 | 299.147 | first_order (no) | - |
| MT | cl | r36013 | 633 | 299.148 | first_order (no) | - |
| MT | cl | r36014 | 637 | 299.147 | first_order (no) | - |
| MT | cl | r36015 | 641 | 299.15 | first_order (no) | - |
| MT | cl | r36016 | 645 | 299.15 | first_order (no) | - |
| MT | cl | r36017 | 649 | 299.15 | first_order (no) | - |
| MT | cl | r36018 | 653 | 299.15 | first_order (no) | - |
| MT | cl | r36019 | 657 | 299.149 | first_order (no) | - |
| MT | cl | r36020 | 661 | 299.15 | first_order (no) | - |
| MT | cl | r36021 | 554 | 299.149 | first_order (no) | friction (no) |
| MT | cl | b2 | 1984 | 0 | - | - |
| MT | cl | r36022 | 625 | 299.149 | first_order (no) | - |
| MT | cl | r36023 | 629 | 299.151 | first_order (no) | - |
| MT | cl | r36024 | 633 | 299.148 | first_order (no) | - |
| MT | cl | r36025 | 637 | 299.15 | first_order (no) | - |
| MT | cl | r36026 | 641 | 299.149 | first_order (no) | - |
| MT | cl | r36027 | 645 | 299.15 | first_order (no) | - |
| MT | cl | r36028 | 649 | 299.146 | first_order (no) | - |
| MT | cl | r36029 | 653 | 299.15 | first_order (no) | - |
| MT | cl | r36030 | 657 | 299.151 | first_order (no) | - |
| MT | cl | r36031 | 661 | 299.15 | first_order (no) | - |
| MT | cl | r36032 | 553 | 299.15 | first_order (no) | friction (no) |
| MT | cl | b3 | 1983 | 0 | - | - |
| MT | cl | r36033 | 625 | 299.147 | first_order (no) | - |
| MT | cl | r36034 | 629 | 299.151 | first_order (no) | - |
| MT | cl | r36035 | 633 | 299.149 | first_order (no) | - |
| MT | cl | r36036 | 637 | 299.148 | first_order (no) | - |
| MT | cl | r36037 | 641 | 299.149 | first_order (no) | - |
| MT | cl | r36038 | 645 | 299.149 | first_order (no) | - |
| MT | cl | r36039 | 649 | 299.147 | first_order (no) | - |
| MT | cl | r36040 | 653 | 299.15 | first_order (no) | - |
| MT | cl | r36041 | 657 | 299.148 | first_order (no) | - |
| MT | cl | r36042 | 661 | 299.149 | first_order (no) | - |
| MT | cl | r36043 | 555 | 299.145 | first_order (no) | friction (no) |
| MT | cl | b4 | 1984 | 0 | - | - |
| MT | cl | r36044 | 625 | 299.148 | first_order (no) | - |
| MT | cl | r36045 | 629 | 299.149 | first_order (no) | - |
| MT | cl | r36046 | 633 | 299.15 | first_order (no) | - |
| MT | cl | r36047 | 637 | 299.151 | first_order (no) | - |
| MT | cl | r36048 | 641 | 299.149 | first_order (no) | - |
| MT | cl | r36049 | 645 | 299.151 | first_order (no) | - |
| MT | cl | r36050 | 649 | 299.147 | first_order (no) | - |
| MT | cl | r36051 | 653 | 299.151 | first_order (no) | - |
| MT | cl | r36052 | 657 | 299.149 | first_order (no) | - |
| MT | cl | r36053 | 661 | 299.149 | first_order (no) | - |
| MT | cl | r36054 | 556 | 299.145 | first_order (no) | friction (no) |
| MT | cl | b5 | 132 | 0 | - | - |
| HSD | cl | r0 | 13154 | 0 | - | - |
| HSD | cl | r90 | 625 | 299.151 | first_order (no) | - |
| HSD | cl | r36000 | 625 | 299.147 | first_order (no) | - |
| HSD | cl | r36001 | 629 | 299.15 | first_order (no) | - |
| HSD | cl | r36002 | 633 | 299.146 | first_order (no) | - |
| HSD | cl | r36003 | 637 | 299.15 | first_order (no) | - |
| HSD | cl | r36004 | 641 | 299.151 | first_order (no) | - |
| HSD | cl | r36005 | 645 | 299.15 | first_order (no) | - |
| HSD | cl | r36006 | 649 | 299.147 | first_order (no) | - |
| HSD | cl | r36007 | 653 | 299.15 | first_order (no) | - |
| HSD | cl | r36008 | 657 | 299.146 | first_order (no) | - |
| HSD | cl | r36009 | 661 | 299.15 | first_order (no) | - |
| HSD | cl | r36010 | 625 | 299.151 | first_order (no) | - |
| HSD | cl | r36011 | 625 | 299.147 | first_order (no) | - |
| HSD | cl | r36012 | 629 | 299.147 | first_order (no) | - |
| HSD | cl | r36013 | 633 | 299.148 | first_order (no) | - |
| HSD | cl | r36014 | 637 | 299.147 | first_order (no) | - |
| HSD | cl | r36015 | 641 | 299.15 | first_order (no) | - |
| HSD | cl | r36016 | 645 | 299.15 | first_order (no) | - |
| HSD | cl | r36017 | 649 | 299.15 | first_order (no) | - |
| HSD | cl | r36018 | 653 | 299.15 | first_order (no) | - |
| HSD | cl | r36019 | 657 | 299.149 | first_order (no) | - |
| HSD | cl | r36020 | 661 | 299.15 | first_order (no) | - |
| HSD | cl | r36021 | 625 | 299.149 | first_order (no) | - |
| HSD | cl | r36022 | 625 | 299.149 | first_order (no) | - |
| HSD | cl | r36023 | 629 | 299.151 | first_order (no) | - |
| HSD | cl | r36024 | 633 | 299.148 | first_order (no) | - |
| HSD | cl | r36025 | 637 | 299.15 | first_order (no) | - |
| HSD | cl | r36026 | 641 | 299.149 | first_order (no) | - |
| HSD | cl | r36027 | 645 | 299.15 | first_order (no) | - |
| HSD | cl | r36028 | 649 | 299.146 | first_order (no) | - |
| HSD | cl | r36029 | 653 | 299.15 | first_order (no) | - |
| HSD | cl | r36030 | 657 | 299.151 | first_order (no) | - |
| HSD | cl | r36031 | 661 | 299.15 | first_order (no) | - |
| HSD | cl | r36032 | 625 | 299.15 | first_order (no) | - |
| HSD | cl | r36033 | 625 | 299.147 | first_order (no) | - |
| HSD | cl | r36034 | 629 | 299.151 | first_order (no) | - |
| HSD | cl | r36035 | 633 | 299.149 | first_order (no) | - |
| HSD | cl | r36036 | 637 | 299.148 | first_order (no) | - |
| HSD | cl | r36037 | 641 | 299.149 | first_order (no) | - |
| HSD | cl | r36038 | 645 | 299.149 | first_order (no) | - |
| HSD | cl | r36039 | 649 | 299.147 | first_order (no) | - |
| HSD | cl | r36040 | 653 | 299.15 | first_order (no) | - |
| HSD | cl | r36041 | 657 | 299.148 | first_order (no) | - |
| HSD | cl | r36042 | 661 | 299.149 | first_order (no) | - |
| HSD | cl | r36043 | 625 | 299.145 | first_order (no) | - |
| HSD | cl | r36044 | 625 | 299.148 | first_order (no) | - |
| HSD | cl | r36045 | 629 | 299.149 | first_order (no) | - |
| HSD | cl | r36046 | 633 | 299.15 | first_order (no) | - |
| HSD | cl | r36047 | 637 | 299.151 | first_order (no) | - |
| HSD | cl | r36048 | 641 | 299.149 | first_order (no) | - |
| HSD | cl | r36049 | 645 | 299.151 | first_order (no) | - |
| HSD | cl | r36050 | 649 | 299.147 | first_order (no) | - |
| HSD | cl | r36051 | 653 | 299.151 | first_order (no) | - |
| HSD | cl | r36052 | 657 | 299.149 | first_order (no) | - |
| HSD | cl | r36053 | 661 | 299.149 | first_order (no) | - |
| HSD | cl | r36054 | 625 | 299.145 | first_order (no) | - |
| MT | sv | b0 | 5115 | 0 | - | - |
| MT | sv | r90 | 625 | 299.151 | first_order (no) | - |
| MT | sv | r36000 | 625 | 299.147 | first_order (no) | - |
| MT | sv | r36001 | 629 | 299.15 | first_order (no) | - |
| MT | sv | r36002 | 633 | 299.146 | first_order (no) | - |
| MT | sv | r36003 | 637 | 299.15 | first_order (no) | - |
| MT | sv | r36004 | 641 | 299.151 | first_order (no) | - |
| MT | sv | r36005 | 645 | 299.15 | first_order (no) | - |
| MT | sv | r36006 | 649 | 299.147 | first_order (no) | - |
| MT | sv | r36007 | 653 | 299.15 | first_order (no) | - |
| MT | sv | r36008 | 657 | 299.146 | first_order (no) | - |
| MT | sv | r36009 | 661 | 299.15 | first_order (no) | - |
| MT | sv | r36010 | 555 | 299.151 | first_order (no) | friction (no) |
| MT | sv | b1 | 1983 | 0 | - | - |
| MT | sv | r36011 | 625 | 299.147 | first_order (no) | - |
| MT | sv | r36012 | 629 | 299.147 | first_order (no) | - |
| MT | sv | r36013 | 633 | 299.148 | first_order (no) | - |
| MT | sv | r36014 | 637 | 299.147 | first_order (no) | - |
| MT | sv | r36015 | 641 | 299.15 | first_order (no) | - |
| MT | sv | r36016 | 645 | 299.15 | first_order (no) | - |
| MT | sv | r36017 | 649 | 299.15 | first_order (no) | - |
| MT | sv | r36018 | 653 | 299.15 | first_order (no) | - |
| MT | sv | r36019 | 657 | 299.149 | first_order (no) | - |
| MT | sv | r36020 | 661 | 299.15 | first_order (no) | - |
| MT | sv | r36021 | 554 | 299.149 | first_order (no) | friction (no) |
| MT | sv | b2 | 1984 | 0 | - | - |
| MT | sv | r36022 | 625 | 299.149 | first_order (no) | - |
| MT | sv | r36023 | 629 | 299.151 | first_order (no) | - |
| MT | sv | r36024 | 633 | 299.148 | first_order (no) | - |
| MT | sv | r36025 | 637 | 299.15 | first_order (no) | - |
| MT | sv | r36026 | 641 | 299.149 | first_order (no) | - |
| MT | sv | r36027 | 645 | 299.15 | first_order (no) | - |
| MT | sv | r36028 | 649 | 299.146 | first_order (no) | - |
| MT | sv | r36029 | 653 | 299.15 | first_order (no) | - |
| MT | sv | r36030 | 657 | 299.151 | first_order (no) | - |
| MT | sv | r36031 | 661 | 299.15 | first_order (no) | - |
| MT | sv | r36032 | 553 | 299.15 | first_order (no) | friction (no) |
| MT | sv | b3 | 1983 | 0 | - | - |
| MT | sv | r36033 | 625 | 299.147 | first_order (no) | - |
| MT | sv | r36034 | 629 | 299.151 | first_order (no) | - |
| MT | sv | r36035 | 633 | 299.149 | first_order (no) | - |
| MT | sv | r36036 | 637 | 299.148 | first_order (no) | - |
| MT | sv | r36037 | 641 | 299.149 | first_order (no) | - |
| MT | sv | r36038 | 645 | 299.149 | first_order (no) | - |
| MT | sv | r36039 | 649 | 299.147 | first_order (no) | - |
| MT | sv | r36040 | 653 | 299.15 | first_order (no) | - |
| MT | sv | r36041 | 657 | 299.148 | first_order (no) | - |
| MT | sv | r36042 | 661 | 299.149 | first_order (no) | - |
| MT | sv | r36043 | 555 | 299.145 | first_order (no) | friction (no) |
| MT | sv | b4 | 1984 | 0 | - | - |
| MT | sv | r36044 | 625 | 299.148 | first_order (no) | - |
| MT | sv | r36045 | 629 | 299.149 | first_order (no) | - |
| MT | sv | r36046 | 633 | 299.15 | first_order (no) | - |
| MT | sv | r36047 | 637 | 299.151 | first_order (no) | - |
| MT | sv | r36048 | 641 | 299.149 | first_order (no) | - |
| MT | sv | r36049 | 645 | 299.151 | first_order (no) | - |
| MT | sv | r36050 | 649 | 299.147 | first_order (no) | - |
| MT | sv | r36051 | 653 | 299.151 | first_order (no) | - |
| MT | sv | r36052 | 657 | 299.149 | first_order (no) | - |
| MT | sv | r36053 | 661 | 299.149 | first_order (no) | - |
| MT | sv | r36054 | 556 | 299.145 | first_order (no) | friction (no) |
| MT | sv | b5 | 129 | 0 | - | - |

Events: 22837. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
