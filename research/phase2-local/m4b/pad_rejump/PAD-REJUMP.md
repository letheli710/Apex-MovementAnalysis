# M4b: re-jump 3 frames after a jump-pad landing (Octane)

Status: offline analysis of the `m4b_pad_rejump*` trials in two sessions. Nothing was launched. No game data and no file outside this folder was changed.

```
py -3 pad_rejump_analysis.py ../../data/20261021_022102_M4b_octane ../../data/20261021_023310_M4b_octane2 \
    --json results.json --params params.json > analysis_output.txt
```

- `pad_rejump_analysis.py` computes every number below. It is stdlib only and has no local paths.
  - It imports the M4 `lg_load.py` wrapper unchanged, and with it the M2 loader and join.
  - It uses only `m4b_pad_rejump` and `m4b_pad_rejump_w` trials with ok = true and warmup = false.
- It tests the OCTANE-PRIMITIVES landing model (§4), the M2 ground decel and multi-jump rule, and the M3 ground-jump cap. **Nothing is refitted.**

## TL;DR

| Question | Answer |
|---|---|
| Is the landing slowdown applied before the re-jump? | **Yes, fully.** On the landing command v_h ×= f0, with f0 = 0.2420 (OCTANE model 0.2421, error ≤ 0.0016). msc then follows the OCTANE recovery (max error 0.0009). The 3 ground commands lose 1250 u/s² each (not scaled by msc). With W held, nothing is added, because v_h is far above the slowed walk cap. |
| Does the ground-jump cap 299 apply? | **The cap applies, but it is scaled: 260·msc.** The jump command sets v_h = min(v_h, sprintspeed · msc(t)) = 72.6 u/s, with error −0.0001 ± 0.0004 u/s (no W). This holds without sprint and without input. 299 and walk·msc are rejected (errors −21 and +24 u/s). |
| How much pad speed carries over? | **14.1 %.** 514.3 at launch, 124.6 after the landing, 93.4 at the jump command, **72.6 after the jump** (no W). With W: 72.1, a 14.0 % carry-over. Without the slowdown the result would have been 299 (counterfactual). |
| Re-jump height | frac = 0.3000 (V = 158.74). This is the M2 anti-multi-jump floor (jump 0.033 s after landing). |
| What W changes | Nothing until the hop lands. In the air, W adds +0.90 u/s² (the known M2/OCTANE W drift). After the hop landing, msc is back at 1.15, sprint re-engages and v_h reaches 299 in 1.00 ± 0.02 s. |
| New finding | **The soft hop landing ends the pad slowdown.** msc jumps from 0.44 to 1.150 on the next command (10/12 trials), instead of recovering until 1.0 s. In 2/12 (W) it lands at 1.1347 or 1.146. That residual is unexplained. |

## 1. Data

| Session | Scored pad trials | Excluded |
|---|---|---|
| M4b_octane | rejump 1 (r2417), rejump_w 3 (r2423–2425) | r2416, r2418–2420 (82–101 fps), r2421–2422 (100–106 fps): runner frame-rate rule |
| M4b_octane2 | rejump 5 (r2441–2445), rejump_w 3 (r2446–2448) | r90 warm-up |

- **Setup.** Lane C, yaw 0, Octane kit. The pad was spawned at reset origin + (300, 0, 0).
- **Schedule.** Sprint + W for 1.5 s; the pad launch comes before the keys are released. Then `waitair`, `waitland`, 3 frames, `tap jump`.
- **Timing.** In every trial the jump command is the 4th command after the landing command (0.033 s). The 3 commands in between are on the ground.
- **Client and dedi.** They are **identical** from 5 commands before the pad landing to 0.5 s after the hop landing: max state difference 0.0000, max msc difference 0.0000, no missing rows.
- **Frame rate.** The rejump_w trials in session 1 ran at 118–120 fps, with some 0.0087 s commands. The model uses each command's own dt.

## 2. Per-command sequence (no W, r2441 as the example; all trials in `analysis_output.txt` §1)

| Command | Pre v_h | Post v_h | msc | What happens |
|---|---|---|---|---|
| landing (vz −1024.3) | 514.946 | **124.990** | 1.15 → | v_h ×= f0 = 0.24272 (model 0.24277) |
| ground 1 | 124.990 | 114.570 | 0.2792 | friction 1250 u/s² (W on or off) |
| ground 2 | 114.570 | 104.153 | 0.2794 | friction |
| ground 3 | 104.153 | 93.734 | 0.2797 | friction |
| jump | 93.734 | **72.827** | 0.2801 | cap = 260·0.28010 = 72.827; V = 158.74 (frac 0.3); no friction |
| air (0.400 s) | 72.827 | 72.827 | 0.28 → 0.44 | no input: constant |
| hop landing (vz −144) | 72.827 | 72.827 | 0.4435 → **1.1500** | the slowdown ends; no-input friction stops the player in 0.058 s |

## 3. Results by group

| | rejump (n = 6) | rejump_w (n = 6) |
|---|---|---|
| Pad launch v_h | 514.309 | 514.309 |
| Landing vz | −1024.53 ± 0.14 | −1025.13 ± 1.35 |
| f0 observed / model | 0.24203 / 0.24207 | 0.24015 / 0.23999 |
| v_h after landing | 124.63 ± 0.23 | 124.24 ± 2.54 |
| Ground decel (3 commands) | 1250.0 ± 0.6 | 1249.9 ± 0.5 (W held: no add) |
| v_h before / after the jump command | 93.39 / **72.62** | 93.63 / **72.06** |
| msc on the jump command | 0.27931 | 0.27711 |
| Jump cap error, post − min(pre, 260·msc) | −0.0001 ± 0.0004 | +0.0135 ± 0.0007 (= W drift on that command) |
| same with 173.5·msc / with 299 | +24.16 / −20.77 | +23.98 / −21.57 |
| Jump frac (V²/2g·56) | 0.29999 | 0.29997 |
| Carry-over v_h after the jump / launch v_h | **0.1412 ± 0.0003** | **0.1401 ± 0.0028** |
| Air d\|h\|/dt after the jump | 0.000 | +0.90 ± 0.02 u/s² (AirAccelerate adds nothing: cap 60·msc ≈ 17 < 72) |
| Hop air time | 0.400 s | 0.399 s |
| msc after the hop landing | 1.1500 (6/6) | 1.1500 (4/6), 1.1347 (r2423), 1.1460 (r2425) |
| After the hop landing | stops in 0.058 s | sprint resumes; 299 after 1.00 ± 0.02 s |

## 4. Model for Unity (all existing primitives; one rule added)

```
on landing cmd:   f0 = clamp(1.996467 - 1.6714e-6 * vz^2, 0, 1); v_xy *= f0; slowdown = {f0, tLand}    # OCTANE 4.5
each cmd:         msc = 1.15 * (f0 + (1 - f0) * (t / 1.0)^2)   while t < 1.0                          # OCTANE 4.3
ground, v > cap:  v_xy -= 1250 * dt (not x msc)                                                        # M2
jump cmd:         v_xy = min(|v_xy|, sprintSpeed(260) * msc) ; no friction                              # M3 cap, msc-scaled  [new: holds without sprint]
                  vz = sqrt(2 g 56 frac), frac = clamp(0.3 + 0.7 (t_since_land - 0.15)/0.60, 0.3, 1)    # M2
next landing:     recompute f0 from that impact; if f0 == 1 the slowdown ENDS (msc back to 1.15)       # new [obs 10/12]
```

- **Design consequence.** A pad landing followed by an instant re-jump keeps only about 14 % of the pad's horizontal speed (≈ 73 u/s).
- **The soft hop landing then clears the slowdown.** A "hop out of a hard landing" is a fast way to recover full speed: 1.15 msc at about 0.43 s after the landing, instead of a quadratic recovery over 1 s.

## 5. Open questions

1. **The residual slowdown after the hop landing** in r2423 (msc 1.1347, the hop-landing v_h ×0.9869) and r2425 (1.1460, ×0.9967). Both are W trials with the smallest hop-landing impact (vz −140.6 and −142.5). The vz² model gives f0 = 1 there. These are 2 of 12 trials; the cause is unknown.
2. **The jump cap without sprint.** 260·msc (sprintspeed) applies with no sprint flag and no input. M3 measured it only while sprinting. Crouch and slide jumps after a hard landing are untested.
3. **Only one impact cluster** (|vz| ≈ 1025) was tested. The re-jump at other f0 values, and re-jump delays other than 3 frames, are untested.
