# M6-G grapple: release, momentum, grapple → zipline handoff

Status: offline analysis of one session, `20261021_162814_M6_G_grapple`.

| setting | value |
|---|---|
| frame rate | 120 fps |
| legend | Pathfinder with kit; the range-doubling mod is removed at every reset |
| geometry | m3 wall + m6zip |
| trials | 26, all ok; 1 warm-up skipped, so 25 used (5 per schedule) |

The same script as A3 produces every number here (section GRAPPLE of `analysis_output.txt`; `results.json` → `grapple`).
The grapple part needs only `--grapple`, but the full command is:

```
cd research/phase2-local/m6/a3_zip
py -3 a3_zip_analysis.py ../../data/20261021_150043_M6_A3_zip \
    --round2 ../../data/20261021_162442_M6_A3_zip2 --grapple ../../data/20261021_162814_M6_G_grapple > analysis_output.txt
```

- **State.** The client `[HSD-STATE]` `gr=` / `zip=` flags match 10960/10960 frames.
- **Indexing.** k = commands after the grapple press (offhand1 down edge).
- **Labels:** [meas] measured, [fit] fitted (residual given), [unknown].

## 1. Release (g1_rel_tac, g1_rel_attack, g1_hold)

The grapple is aimed at the m3 wall from lane A, at pitch −10.

| | g1_hold (5) | g1_rel_attack (5) | g1_rel_tac (5) |
|---|---|---|---|
| liftoff | k24 | k24 | k24 |
| `gr` flag | k0–183/185 (185 frames) | k0–183/185 | k0–86 (**87 frames**) |
| pull end | wall contact at k186–188: x −13720.6, \|v\| 574 → 6.5 in one command | same as hold | **released at k73, the press command itself (latency 0)** |
| max \|v\| during the pull | 611–612 | 611–612 | – |

- **Attack does not release.** Its speed trace stays within 8.3 u/s of the hold mean for 180 commands, and the pull
  ends at the wall like hold [meas].
- **A second tactical press releases.**
  - **Momentum is kept exactly**: v_release = (145.5–147.8, −0.13, 22.8–23.3). That is within ±1.2 u/s of the hold
    trials' speed on the previous command (146.6).
  - From the release command on: Δ|v_xy| = 0.000 until landing (no drag), and g = 750.1–750.3 (ordinary gravity)
    [meas].
  - Landing comes at k111–112 with v = (145.5–147.8, −0.13, −210 … −214).
  - The `gr` flag stays true for 13 commands after the release (retract) with no effect on motion.
- **Unity rule** [meas]: on a release press, stop applying the grapple pull on that same command and keep the velocity.

## 2. Grapple → zipline handoff (g3_hook, g3_hook_use)

**Setup.**
- Start: (−14000, 6650, 294.92), yaw 36.87, pitch −9.09 = atan(40/250).
- The view ray from eye height 60 meets Z1 at **x = −13800**, 250 u away. That is out of +use range (round 1: 80 u
  lateral already fails).
- g3_hook_use adds a use press at k61.

**What happens in all 10 trials, with or without the use press:**

1. **Grapple phase.** `gr` lasts k0 → k113…115 (114–116 frames). The player lifts off at about k24 and is pulled up
   toward the rope.
2. **The handoff is automatic and identical with or without use.**
   - The mount comes at **k114–116** (mean 114.8). It is the command right after `gr` ends.
   - The use press at k61 changes nothing (mount k115–116 vs k114–115).
   - Client and dedi `[ZIPRAIL-USE]` show `grapple=1 result=1` on the same command, which is the first missing MT
     command (10/10).
   - The first trial's client log (rate-limited after it) shows 16 earlier `grapple=1 result=0 why=native wdf=7`
     attempts from k≈14 (dedi: 4 fails, wdf=3). The native code tries the grapple mount every command from about the
     moment the hook lands, and refuses until k114.
3. **Attach point** [meas]. Q (dedi Find point) x = −13803.36 ± 0.29, i.e. **3.4 u before the hook's aim point**
   (−13800).
   - The round-1 Find rule (minimum angle within 130 u of P) would give a point 7.4 u further along (angle 12.9° vs
     13.1°), so Q is not exactly that point.
   - |Q − P| at the mount is 116.5–119.0.
4. **Trigger** [unknown].
   - By the round-1 Find model a mount was geometrically possible from k76–78 (rope within 130 u of P from k72–74, cone
     < 40.7° from k76–78). The mount came **38 commands later** in every trial.
   - So the trigger is not "Find succeeds". It looks like the end of the grapple: the grapple ends early (114 vs 185
     frames in hold) exactly when the zipline takes over.
   - At the mount, the distance from origin to the aim point is 135.4–137.9 u. Because the pull is deterministic,
     distance and time are confounded.
5. **Pull toward the rope.** Just before the mount the velocity is (293.4, 220.3, 25.8), |v| = 367.8, pointing 24.7°
   off the direction to Q. The grapple pull itself is the M4 model and was not re-fitted here.
6. **Mount command.** No movement on the mount command (0.000 u), as in round 1.
   - Then a blend onto the hang line: the distance to the client hang line (y 6799.77, z 314.75) is 73.2 → 56.6 (k5)
     → 27.6 (k10) → 8.1 (k15) → 1.35 (k20) → 0 (k30).
   - The view is driven from (36.87, −9.09) to (0, 0) along the rope, 90% at k22, the same as round 1.
7. **Entry speed carries the grapple momentum along the rope** [fit, 10/10]:

   ```
   v_entry = v_pre · d̂_rope + 400·dt
   ```

   - Measured v_entry − v_pre·d̂ = 3.346 ± 0.035, i.e. 400.0 u/s² × dt.
   - v_entry = 293.8–297.1, along the rope (dir·d̂ = 1.000000). The cross-rope and vertical components are dropped.
8. **Ride during the 0.5 s mount state: v = max(v_entry, rest-mount curve)** [fit].
   - The speed stays flat at v_entry until the rest curve (8.33 + 600 u/s²) overtakes it at k59.
   - Then 303.3 at k60, and +400 u/s² from there, exactly the rest-mount profile.
   - |residual| ≤ 0.30 u/s in 8 trials. In 2 trials (r3818, r3822) it reaches 3.3 u/s, a one-command phase slip at the
     state switch.
   - **Net effect:** grapple momentum gives ~297 u/s from the first ride command instead of 8 → 303 over 0.5 s. After
     0.5 s the ride is identical to a rest mount.
9. **Ride and detach** exactly as in A3:
   - hang 80.17 below the rope, lateral −0.23 (client);
   - cap 600;
   - auto-detach v_out = (600, 0, 0) on client and dedi, 90.9–94.3 u from the end;
   - 193–195 zip frames.

## 3. Unity rules (per usercmd)

```
GRAPPLE RELEASE: second tactical press -> stop the pull on that cmd, keep velocity (no damping), gravity 750   [meas]
                 attack does not release                                                                      [meas]
GRAPPLE->ZIP:    while the grapple hook is on a zipline, try a grapple mount every cmd; it succeeds when the grapple
                 ends (here 114-116 cmds after the press; trigger unknown, the Find geometry allowed it 38 cmds earlier)
                 attach point Q ~ the hook point on the rope (here 3.4 u before it)                         [meas]
                 mount cmd: no move; blend onto the hang line (~0.25 s); view -> rope direction (90 % in 22 cmds)
                 v_entry = v_pre . rope_dir + 400*dt (along the rope)                                        [fit, resid 0.04]
                 k <= 60: v = max(v_entry, rest-mount curve); k > 60: +400 u/s^2 to the 600 cap            [fit, resid <= 0.3 (3.3 in 2/10)]
                 then the normal A3 ride / detach rules; no use press needed
```

## 4. Open questions

1. **The handoff trigger.** Is it a distance to the hook point, the grapple's own end condition, or a native timer?
   Vary the start distance (150 / 250 / 350 u) and the aim height.
2. **Hook-point rule.** Aim at different points along the rope to check that Q follows the hook point.
3. **Entry along a component that opposes the rope direction:** grapple toward the rope from the far end. Is v_entry
   negative or clamped, and does the mount choose the rope direction?
4. **The 400·dt term** in v_entry: is it the state-3 acceleration applied once, or an additive constant? Test with a
   very slow grapple approach.
5. **Grapple release while ziplining**, and a jump during the handoff blend.
