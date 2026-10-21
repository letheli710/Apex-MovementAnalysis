# hsd_tel report

Inputs: 16 file(s); rows: 47800 (MT 31871, HSD 15869)

Validation: 0 error(s), 20 warning(s), 25 info

- warning `W_TELEPORT` message.log:3731 teleport in stream ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` message.log:4034 teleport in stream ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` message.log:4628 teleport in stream ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` message.log:5367 teleport in stream ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` message.log:6132 teleport in stream ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_MORE` message.log:0 12 more teleport rows in ('MT', 'cl', 'cmd', 1, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` script.log:3404 teleport in stream ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` script.log:3672 teleport in stream ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` script.log:4137 teleport in stream ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` script.log:4855 teleport in stream ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` script.log:5603 teleport in stream ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_MORE` script.log:0 12 more teleport rows in ('HSD', 'cl', 'frame', None, 'e9160c99-be19-4a25-b45e-9489de41610a')
- warning `W_TELEPORT` message.log:3469 teleport in stream ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TELEPORT` message.log:4228 teleport in stream ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TELEPORT` message.log:4939 teleport in stream ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TELEPORT` message.log:5680 teleport in stream ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TELEPORT` message.log:6420 teleport in stream ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_MORE` message.log:0 11 more teleport rows in ('MT', 'sv', 'cmd', 1, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TELEPORT` script.log:830 teleport in stream ('HSD', 'sv', 'evt', 1.0, '875521c7-9088-4caf-982f-e3349ef134c3')
- warning `W_TIME_BACKWARDS` script.log:717 t 23.25 -> 23.0914 in ('HSD', 'sv', 'evt', 1.0, '875521c7-9088-4caf-982f-e3349ef134c3')

## Runs

A fit is marked good when its R^2 >= 0.98 over the whole phase.

| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |
|---|---|---|---|---|---|---|
| MT | cl | b0 | 5835 | 0 | - | - |
| MT | cl | r90 | 608 | 573.654 | - | linear (yes) |
| MT | cl | r1901 | 541 | 575.762 | - | linear (yes) |
| MT | cl | r1902 | 541 | 575.665 | - | linear (yes) |
| MT | cl | r1903 | 541 | 574.06 | - | linear (yes) |
| MT | cl | r1904 | 541 | 573.491 | - | linear (yes) |
| MT | cl | r1905 | 541 | 573.698 | - | linear (yes) |
| MT | cl | r1906 | 612 | 574.501 | - | linear (yes) |
| MT | cl | r1907 | 612 | 575.775 | - | - |
| MT | cl | r1908 | 612 | 573.848 | - | friction (no) |
| MT | cl | r1909 | 612 | 576.111 | - | friction (no) |
| MT | cl | r1910 | 612 | 574.598 | - | linear (yes) |
| MT | cl | r1911 | 696 | 735.388 | - | linear (yes) |
| MT | cl | r1912 | 696 | 734.462 | - | linear (yes) |
| MT | cl | r1913 | 696 | 748.948 | - | linear (yes) |
| MT | cl | r1914 | 696 | 769.301 | - | linear (yes) |
| MT | cl | r1915 | 696 | 734.255 | - | linear (yes) |
| HSD | cl | r0 | 5831 | 0 | - | - |
| HSD | cl | r90 | 541 | 573.654 | - | linear (yes) |
| HSD | cl | r1901 | 541 | 575.762 | - | linear (yes) |
| HSD | cl | r1902 | 541 | 575.665 | - | linear (yes) |
| HSD | cl | r1903 | 541 | 574.06 | - | linear (yes) |
| HSD | cl | r1904 | 541 | 573.491 | - | linear (yes) |
| HSD | cl | r1905 | 541 | 573.698 | - | linear (yes) |
| HSD | cl | r1906 | 612 | 574.501 | - | linear (yes) |
| HSD | cl | r1907 | 612 | 575.775 | - | linear (yes) |
| HSD | cl | r1908 | 612 | 573.848 | - | linear (yes) |
| HSD | cl | r1909 | 612 | 576.111 | - | linear (yes) |
| HSD | cl | r1910 | 612 | 574.598 | - | linear (yes) |
| HSD | cl | r1911 | 696 | 735.388 | - | linear (yes) |
| HSD | cl | r1912 | 696 | 734.462 | - | linear (yes) |
| HSD | cl | r1913 | 696 | 748.948 | - | linear (yes) |
| HSD | cl | r1914 | 696 | 769.301 | - | linear (yes) |
| HSD | cl | r1915 | 696 | 734.255 | - | linear (yes) |
| MT | sv | b0 | 5839 | 0 | - | - |
| MT | sv | r90 | 569 | 573.654 | - | linear (yes) |
| MT | sv | r1901 | 541 | 575.762 | - | linear (yes) |
| MT | sv | r1902 | 541 | 575.665 | - | linear (yes) |
| MT | sv | r1903 | 541 | 573.478 | - | linear (yes) |
| MT | sv | r1904 | 541 | 573.489 | - | linear (yes) |
| MT | sv | r1905 | 541 | 573.698 | - | linear (yes) |
| MT | sv | r1906 | 612 | 574.14 | - | linear (yes) |
| MT | sv | r1907 | 612 | 575.775 | - | linear (yes) |
| MT | sv | r1908 | 612 | 573.848 | - | friction (no) |
| MT | sv | r1909 | 612 | 576.111 | - | friction (no) |
| MT | sv | r1910 | 612 | 574.598 | - | linear (yes) |
| MT | sv | r1911 | 696 | 735.388 | - | linear (yes) |
| MT | sv | r1912 | 696 | 734.462 | - | linear (yes) |
| MT | sv | r1913 | 696 | 748.948 | - | linear (yes) |
| MT | sv | r1914 | 696 | 769.301 | - | linear (yes) |
| MT | sv | r1915 | 696 | 734.255 | - | linear (yes) |

Events: 134. Plots: spd2d_HSD_cl.svg, vz_HSD_cl.svg, spd2d_MT_cl.svg, vz_MT_cl.svg, spd2d_MT_sv.svg, vz_MT_sv.svg. Fits: fits.json.
