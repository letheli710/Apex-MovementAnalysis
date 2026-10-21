# M6-B: legend mobility research (Alter, Loba, Ash, Valkyrie) + grapple extras

Status: offline analysis of eight sessions recorded on 2026-10-21. No game, Unity or runner file was changed and
nothing was launched for this report. This is research for a decision: **nothing here is being built**, and the
recommendation in §7 is for the user to accept or reject.

**Setup.** R5Flowstate S21. The client is the offline S21 client and the server is the S3 dedi plus the community
SDK. This is not the official S21 game. Where the SDK reimplements a system, the dedi numbers are SDK numbers. That
applies to Alter placement (`vscript_server_placement.cpp`), the Loba drop latch (`translocation.cpp`) and the
Valkyrie jets (`jetpack.cpp`, `bridge_jetpack 1`). Everything ran at 120 fps.

## Files and rerun

| File | Content |
|---|---|
| `m6b_analysis.py` | Re-runnable analysis. Stdlib only, takes session folders as arguments, reads only the raw logs and `runner.json`. |
| `analysis_output.txt` | Console output (per-trial tables and summaries). |
| `results.json` | Per-trial rows and per-schedule summaries. |
| `params.json` | Every parameter with value, unit, source, n and spread. |

Rerun from this folder (about 3 s):

```
py -3 m6b_analysis.py ../../data/20261021_175730_M6B_alter ../../data/20261021_181108_M6B_pilot_alter ../../data/20261021_180124_M6B_loba ../../data/20261021_180406_M6B_ash ../../data/20261021_181301_M6B_pilot_ash ../../data/20261021_181926_M6B_ash2 ../../data/20261021_182355_M6B_ash3 ../../data/20261021_180800_M6B_valk --json results.json --params params.json > analysis_output.txt
```

**Data sources.**
- **Dedi MOVE-TRACE.** Authoritative per-usercmd pre/post state. A teleport shows up as an origin jump. During the Ash
  breach the dedi prints nothing, so the breach shows up as a gap in the command numbers.
- **Dedi diag/script lines:** `[OPL-SRV]`, `[TRANSLOC]`, `LockWeaponsAndMelee from TranslocationLifetimeThread` (one per
  Loba throw), `PhaseTunnel_*`, `[HSD-RESET]` (trial windows).
- **Client:** MOVE-TRACE button bits, `[HSD-STATE]` `ph=` / `glide=` per frame, and the `[CLASSVAR]` census.
- **Not used:** `report/rows.csv`. It keeps only 6 significant digits, so the script parses the raw logs instead.

**Labels.**
- **[meas]**: measured here, with n.
- **[src]**: source-supported (file:line). `P:` = `s21-platform/scripts/vscripts/`, `PW:` = `.../scripts/weapons/`,
  `SDK:` = `s21-r5sdk/src/` (see `../SOURCE-AUDIT.md`).
- **[comm]**: community or historical claim (`R5Flowstate_S21_Movement_Report_2026-10-20.md`). Not verified, and the
  version caveats apply.
- **[open]**: unresolved.

---

## 1. Alter, Void Passage (`mp_ability_phase_door`, tactical)

**Conclusion.** Alter could **not be triggered** in this setup. Every number below is **from source only**.
- **Uniqueness:** Void Passage is the only S21 mobility skill that goes *through* solid geometry. It is also the only
  teleport that carries speed across: exit speed = clamp(v·n, 50, 300) along the exit normal.
- **Cost of finding out more:** debugging the SDK's native placement reimplementation. Under the M6 stop-loss rule,
  that work stops here.

### Measured [meas]

Data: 21 scored trials.
- `M6B_alter`: b_alter_sprint, b_alter_walk and b_alter_stand, 5 each.
- `M6B_pilot_alter`: bp_alter_hold12, hold_att and tap_att, 2 each.

| Item | Result |
|---|---|
| Portal / teleport | **0 / 21.** Client `ph` is false on every frame, there is no `ALTER: Teleporting` print and no dedi origin jump. |
| Player motion | Runs into the rock and stops at x −13724.82 in all 21 trials. That is 18.8 u in front of the face at −13706 (hull contact). Sprint speed is 299 and walk 199.5. |
| SDK placement diag, per trial | 232–717 × `entrance edge-correction failed` (`overhang excess −24.0 over 23.0 on dir 0`). 2–5 × `placement accepted`, and every one of them is also logged as `shallow exit accepted depth=1.1 thickness=216.5`. |
| Exit probe | It measures the rock as **216.5 u** thick (21/21), which is within the 30 m maximum. It still puts the exit **1.1 u behind the entrance**, i.e. on the near face, not on the far side. |
| Lead's live probe (not saved as a session) | Holding `+offhand1` at 150 / 300 u and at 60° down at the floor, `ObjectPlacementHasValidSpot()` returned false and the placement origin/exit was `<0,0,0>` at 0.3 / 0.8 / 1.5 s. The weapon did switch to `mp_ability_phase_door`. Nothing happened on release. |

**Reading.**
- The per-frame SDK search mostly fails the entrance edge correction.
- The rare accepted candidates have a degenerate exit at the near face.
- The script's valid-spot check (`P:weapons/mp_ability_phase_door.nut:627-641`) then misses
  (`SDK:game/server/vscript_server_placement.cpp:5173-5182` reads the stored placement state).
- The SDK has A/B levers for this, all **off by default**: `sv_alter_portal_min_depth` 0,
  `sv_alter_portal_entrance_plane_guard` 0, `sv_alter_portal_exit_normal_hemisphere` 0 (`vscript_server_placement.cpp:2936-2946`).
  Shallow exits are logged at `:3261`.
- **Which component finally rejects the spot is [open].**
- **Second attempt, lead, `*_M6B_alter_sdkfix`** (13 trials: b_alter_stand ×5, b_alter_sprint ×5, bp_alter_hold12 ×3; all three levers on via
  `--both-cvar`: min_depth 32, entrance_plane_guard 1, exit_normal_hemisphere 1).
  - Still **0 portals**: 0 `ph=true` frames, no `ALTER: Teleporting` line.
  - Dedi `[OPL-SRV]` counts:
    - 5276 "entrance edge-correction failed" (overhang excess −24.0);
    - 46 "min-depth reject depth=1.1": the lever now rejects the near-face exit;
    - 46 "refined exit normal discarded (flipped hemisphere)";
    - 31 "placement accepted", with the exit probe at loop 1 finding thickness 2538.0 u.
  - That exit is far beyond the 30 m wall limit, so it is presumably still rejected downstream.
  - Stopped here (stop-loss): the remaining cause is SDK placement geometry against this rock prop, not a movement question.
  - This session is not analysed by `m6b_analysis.py` (diagnostic only).

### Source-supported [src]

| Item | Source |
|---|---|
| Hold `+offhand1` = preview, release = place. `object_placement_distance_max` 1750 (SDK default when unset). Clip 50, 25 per use, regen 1/s. | `PW:mp_ability_phase_door.txt:44-86`; `SDK:…placement.cpp:1119-1146` |
| Max wall thickness 30 m. The script comment says it must match the native exit search; the SDK patches the client from 20 m to 30 m. | `P:weapons/mp_ability_phase_door.nut:118`; `SDK:game/client/phase_door_depth.cpp:1-10` |
| Portal life 15 s, plant delay 0.7 s, re-enter debounce 1.35 s | `nut:120-123` |
| **Exit velocity = outDir × clamp(v·outDir, 50, 300).** A floor or ceiling exit forces the direction to ±Z. | `nut:1408-1413, 1476-1479` (min/max at `:125-126`, playlist-overridable at `:316-317`) |
| Exit position = portal centre + outDir × 10 (82 for a ceiling/floor-down portal), minus 32 z for a wall portal | `nut:1403-1406` |
| Teleport: `TeleportPlayerNoInterp` + `PutPlayerInSafeSpot`. Server only, not predicted. | `nut:1435-1436` |
| Post-portal phase shift 1.0 s, weapons taken | `nut:128-129` |
| Vertical "portal extension" keeps only vz, travel 400 u/s | `nut:1438-1444` |

### Community / historical [comm]

- S21 Alter can pass through walls, floors and ceilings. The reported uses are a vertical entry through a ceiling and
  exiting into general movement.
- Version caveats from the report:
  - do **not** use the current 25 m wall limit or later Nexus auto-trigger rules;
  - the S21 limits must be checked against the old script.
- The Void Nexus ultimate is outside the M6-B scope.

### Unresolved [open]

- Exit speed, exit state and wall/floor/ceiling behaviour are all unmeasured.
- Why the SDK exit probe collapses to the near face. Candidates: rock collision, the edge-correction overhang, or a
  missing far-side trace.
- Whether a thinner wall, a different prop or the `sv_alter_portal_*` levers would make it work. Testing that is the
  high-cost path the stop-loss excludes.

---

## 2. Loba, Burglar's Best Friend (`mp_ability_translocation`, tactical)

**Conclusion.**
- A delayed point teleport with **velocity zeroed** (15/15 measured, |v| = 0.000).
- The early drop works only when it is pressed **≥ ~0.3 s after the bracelet leaves the hand**. A press before that is
  ignored.
- It is not a flight. The player never travels along the arc.
- Fit for HSD: low. It kills momentum and is slow: press → throw is 1.2 s from a weapon-out start, then flight, then
  0.6 s from the drop to the teleport.

### Measured [meas]

Session `M6B_loba`: 25 scored trials plus 1 warm-up. 16 throws, 15 teleports.

| Item | Result |
|---|---|
| **Press → throw**, melee weapon active | **1.208 s** (1.152–1.252, n = 16). The runner assumed the 0.6 s pull-out, but the melee holster plus deploy/raise comes first. |
| Second press **before or at** the throw | b_loba_drop_t07 / t09 / t12 pressed at −0.53 / −0.30 / **+0.048 s** relative to the throw. **0 / 15 drops.** The +0.048 s press is below the 0.24 s minimum [src]. |
| Second press **0.30–0.35 s after** the throw (b_loba_drop_t15) | **5 / 5 drops.** Teleport **0.95–1.05 s after the throw**, **832–932 u** from the throw position, dz 0 (on the field), v = 0. |
| Drop → teleport (where `tossloop end` is logged) | **0.600 s** (n = 4). Of that, 0.4 s is the scripted pre-teleport delay [src]; the rest is the dropped bracelet falling and planting [inf]. |
| Bracelets not dropped in their own trial (t07–t12, sprint) | Their teleport happened in the **next** trial, after the runner reset. 8 / 10 came **1.00–1.15 s after that trial's first `+offhand1` press**, which acted as a late drop 4.4–4.85 s into the flight. Those landed **3855–3885 u** away and **482–492 u lower**, off the field. 2 / 10 (sprint throws) planted on their own 4.55 s after the throw, 2502 u away, dz −456. |
| Teleport rate | Teleport inside the same trial: t07 0/5, t09 0/5, t12 0/5, **t15 5/5**, sprint 0/5. Every attributable throw teleported eventually (15/15). The 16th throw was the session's last trial. **No failed teleport, so no refund was observed.** |
| Velocity after | **0.000 u/s** on the teleport command and the next one (15/15). Confirms M4. |

**Why some trials did not teleport.**
- It was not destination validity. It was **timing**: the runner pressed the drop before the projectile existed.
- The undropped bracelets then flew 4–5 s and landed off-field. That spilled the teleport into the next trial.

### Source-supported [src]

| Item | Source |
|---|---|
| Deploy 0.1 s, toss pull-out 0.6 s. Launch 1815 u/s (1390 above 50° pitch). Staged gravity scale 0.5975 → 0.48 → 0.68. Inherits owner velocity. Fuse 5.7 s. | `PW:mp_ability_translocation.txt:9-68` |
| Drop: `+attack` or `+offhand1` polled by the server toss thread. Allowed only ≥ `loba_tactical_drop_minimum_time` 0.24 s after projectile creation, only once, only before planting. Re-thrown straight down at 1650. | `P:abilities/loba_tactical_translocation.nut:466-487, 716-724`; `.txt:58`; SDK latch `SDK:game/server/translocation.cpp:61-66, 604-612, 1405-1441` |
| Destination: plant point + 2 backups. `IsLandingPositionValid`: ground within 1000 u below, no slip/OOB/kill trigger. Then `CanPutPlayerInSafeSpot`. | `nut:754-836, 966-971, 1061-1075` |
| Pre-teleport delay 0.4 s (`fxPreTime` 0.2). Aborts if the player enters a bad state. | `nut:1009-1025` |
| Teleport: stops the zipline, angles face the travel direction, **velocity = 0**, `TeleportPlayerNoInterp`. On failure, angles and velocity are restored. | `nut:1095-1115` |
| Failed teleport → one charge (25/50) refunded, next attack time reset | `nut:595-607` |

### Community / historical [comm]

- S21 Loba is a "position transfer, not flying along the bracelet path".
- Reported techniques: high/low throws, the early-drop command to adjust the destination, and teleporting through
  windows or over obstacles.
- Version caveat: later abilities (Wolf's Claw etc.) are excluded.

### Unresolved [open]

- The drop gate in absolute terms. The press-vs-creation threshold lies between +0.05 and +0.30 s after the throw
  line. The source says 0.24 s; a finer sweep would place it.
- Landing distance as a function of drop time. Only one effective drop time (≈ 0.33 s) was tested.
- The refund path (a throw into the void) and the control lock after the teleport (no input was given after the
  teleport in M6-B; M4 found none).

---

## 3. Ash, Phase Breach (`mp_weapon_phase_breach`, **ultimate**, `+offhand4`)

**Conclusion.** A targeted, one-way point-to-point **kinematic path**:
- Exit velocity is **exactly 0** (31/31 breaches).
- The player is frozen for **0.15 + 0.1 s per path frame**: 0.65 s at 551 u, 1.08 s at 1103 u, 1.67 s at 1833 u.
- The exit is at **~91.8 % of the aimed ground distance, 5 u above the ground**.
- The entry portal stays live and **re-usable** (15 s [src]). A second touch sends the player to the same exit.

### Measured [meas]

Primary breaches in ok, non-warm-up trials: **n = 20**.
- `ash2`: 9.
- `ash3`: 9.
- `pilot_ash`: 2.

Plus 11 re-entries (§ below).

| Aim (ground at d, pitch) | n | Start → exit 2D | Exit / aim | Freeze (dedi cmd gap) | Source path time → path frames | Client `ph` |
|---|---|---|---|---|---|---|
| 600 u (5.71°) | 6 | **551.2 u** | 0.919 | **0.653 s** (0.617–0.700) | 0.459 s → 5 | 0.687 s |
| 1200 u (2.86°) | 6 (+2 pilot) | **1102.8 u** | 0.918 | **1.076 s** (1.050–1.100) | 0.919 s → 9 | 1.096 s |
| 2000 u (1.72°) | 6 | **1832.5 u** | 0.917 | **1.672 s** (1.642–1.692) | 1.527 s → 15 | 1.698 s |

- **Freeze model [fit]:** gap = **0.152 + 0.1017 × frames** s (rms 0.025 s, n = 20), with
  frames = round(clamp(d/1200, 0.3, 1.8) / 0.1).
  - The slope is the script's 0.1 s path frame [src].
  - The ±0.05 s scatter is the 20 Hz server tick.
  - Against distance alone: 0.206 s + d / 1255 u/s.
- **Attack → breach start: 0.401 s** (n = 19; 0.450 s in the one hold variant).
  - The sequence is: tap `+offhand4` (raises targeting), then tap `+attack` (fires), then 0.4 s, then travel.
- **Exit:**
  - |v| = **0.000** on the first post-breach command (20/20 and 11/11 re-entries);
  - z = start ground + **5.00 u**;
  - an ordinary fall, landing 11 commands later at vz −62.5;
  - move scale 1.18 on exit (weapons holstered);
  - MT resumes on the exit command. No input was given at the exit, so the response to input after the exit is not
    tested.
- **Exit point.** dz 5.0 and the constant 0.918 ratio fit a target where the eye ray (eye 60 u) is 5 u above the
  ground: (60 − 5) / 60 = 0.917 [inf].
- **Re-entry (ash2, pilot).**
  - The runner reset placed the player on the still-live entry portal 4.15–4.40 s after the breach.
  - Dedi: `PhaseTunnel_ShouldPhaseEnt PASSED`, then a second breach to the **same exit** (11/11, v = 0).
  - That is why every other ash2 trial failed the settle ("no start/end edge").
  - ash3 padded the trial past the portal lifetime: 9/9 valid.
- **First run (`M6B_ash`): 0 breaches in 15 ok trials.** The schedule tapped only `+offhand4`.
  - The reset weapon alternated `phase_breach` / `melee` from trial to trial. Each tap raised or holstered the
    targeting weapon; nothing ever fired.
  - Phase Breach (`offhandHybrid`) needs `+attack` while raised. This is an input-schedule error, not a game failure.

### Source-supported [src]

| Item | Source |
|---|---|
| `fire_mode offhandHybrid`, clip 150 per use, regen 1/s after 1 s | `PW:mp_weapon_phase_breach.txt:9, 45-53` |
| Speed 1200, time min 0.3 / max 1.8 s (1.4 upgraded). Range 75 m = 2953 u (100 m upgraded). Full range only within 45° of view. Min 200 u. Movers < 12 u/s allowed. No OOB end. | `P:weapons/mp_weapon_phase_breach.nut:36-64` |
| Path nodes get origin + angles only, **no velocity** → exit velocity 0 (now measured) | `nut:341-352`; mover sets `SetVelocity(node.velocity)` at `P:weapons/mp_weapon_phase_tunnel.nut:1520-1521` |
| Path time → `numPathFrames = round(pathTime / FRAME_TIME)`, FRAME_TIME 0.1. One mover step per frame, then a final WaitFrame and `SetAbsOrigin`. | `mp_weapon_phase_tunnel.nut:64, 2183-2187, 1514-1549` |
| Prediction off and `FreezeControlsOnServer` at entry. Revert: prediction on, controls unfrozen immediately (`controlRestoreDelay` 0), weapons back after 0.4 s. | `tunnel:1576-1577, 1642-1653`; `breach.nut:409` |
| Portal lifetime 15 s | `breach.nut:42` |

### Community / historical [comm]

- S21 Ash has Phase Breach, a one-way teleport, and **no Dash**. The air dash is S24; `mp_ability_ash_dash.nut` in the
  community tree does not prove S21 had it.
- Reported uses: crossing height differences and gaps, and the exit feeding into general movement.

### Unresolved [open]

- Input response right after the exit (control return was inferred from MT resuming, not from an input).
- Weapon return timing (0.4 s, source only).
- Targeting rules beyond flat ground: the 45° cone, movers, walls, the vertical limit and the out-of-range fallback.

---

## 4. Valkyrie, VTOL jets (passive; not the ultimate)

**Conclusion.** M6-B supplements M4 and closes the fuel gap.
- **Meter:** 8.0, drain **1.000 /s**, **1.000 per activation**.
- Recharge **0.75 /s**, starting **4.43 s after landing** (5.01 s after the jump release) [meas].
- Running empty stops the jets exactly like a release: vz × 0.4, then the post effect.
- The post effect lasts **3.0 s** (`jetpackPostEffectTime`, now observed).
- **New:** a release *above* the thrust terminal (265.75 u/s, as in short bursts) applies **neither** the 0.4 cut nor
  the post effect.
- The M4 flight model holds unchanged over 7 s holds and 0.3 s pulses.

### Measured [meas]

Session `M6B_valk`: b_valk_hold10 n = 5 (10 s hold), b_valk_pulse n = 5 (4 × 0.3 s holds, 0.35 s gaps). 25 activations.

| Item | Result |
|---|---|
| Census `[CLASSVAR]` | jetpackMeterRate **1**, jetpackMeterOnActivation **1**, jetpackTacticalMeterRate 1, jetpackPostEffectTime **3**, PostEffectGravity 0.45, PostEffectDrag 0.000125, TightnessUp 0.27, **TightnessDown 0.1**, **TightnessSideways 0.11**, ForwardBack 0.14, ThrustScaleOnActivation 1.8 / 0.5 s, glideDuration 8, glideRechargeOnlyInGroundedState false, glideRechargeOnlyWhenFeetOnGround false. The M4 fits are confirmed as setfile values. |
| Meter at start | 8.0 in every trial. The runner reset refills it. |
| Drain while held | **1.0002 /s** (1.0001–1.0005, n = 5; fit rms ≤ 0.0003) |
| Activation cost | **1.000**: 0.9998 (hold10, n = 5) and 1.0001 (pulses, n = 20). The step appears on the activation command. The client state shows it 1 frame later. |
| Continuous hold | The meter is empty **7.000 s** after the press, = (8 − 1) / 1, in 5/5. The dedi fuel stop comes at 6.94–7.00 s with jump still held. |
| Fuel stop | vz **× 0.40000** (post 253.88 → 101.55, 5/5). Then **low gravity (0.45 g) for 2.96–2.99 s** and full g from 3.000 s after the stop, at ~659 u height (5/5). The post effect ends **by time**, so jetpackPostEffectTime = 3 is now observed. No reactivation while empty, even with jump still held. |
| 0.3 s pulses | 4/4 activations per trial (the 0.35 s gap is above the 0.25 s reactivation delay [src]). Each pulse costs 1.3 (1 + 0.3). The meter goes 8 → 6.70 → 5.40 → 4.10 → 2.80. Peak pre-vz per pulse 328–356. |
| Release above terminal | Release vz 324–352 > 265.75. Next-pre / post = **1.00000** (no cut), and **0 low-g commands** after it (20/20): full gravity at once. This matches `SDK:game/server/jetpack.cpp:385-390`, where both the cut and the post gravity sit inside `if (flTerm >= vz)`. |
| Height | Apex **1889 u** (10 s hold, 7 s of jets) vs **633 u** (4 pulses, 1.2 s of jets for 5.2 meter). That is about 270 u per meter continuous vs about 122 u per meter in bursts. |
| Landing vz | −1343 (hold10), −970 (pulse). No fall damage was examined. |
| M4 model check (dedi, vz only, no input) | Terminal pre-vz **260.126** (M4 260.13; the post-move value is 253.88). One-step residual rms 0.04 u/s per activation; \|e\| > 0.1 u/s in 192 of 4913 commands, mostly one trial (r4334) with timing jitter. **No refit needed.** |
| Recharge | Rate **0.7494 /s** (0.7485–0.7501, n = 5). Starts **4.430 s after landing** (4.417–4.441), which is **5.010 s after the jump release** and 8.02 s after the meter emptied. Pulse trials ended 3.0 s after landing with no recharge. That is consistent, but it cannot tell landing from release as the trigger. |
| Meter in the air after the jets stop | Flat for 0.53–1.74 s (10/10). That is shorter than the recharge delay, so **air recharge is not tested**. The flags say it is allowed. |

### Source-supported [src]

- **Meter.**
  - The meter update is native (`v_Jetpack_UpdateMeter`). The SDK only swaps the tactical drain rate and the
    recharge-grounded flag (`SDK:game/server/jetpack.cpp:725-768`).
  - There is a native recharge-delay accumulator `m_glideRechargeDelayAccumulator` (`SDK:game/shared/s21_dt_schema.h:3394`).
    The delay and rate keys are not in the census.
- **Stops and post effect.**
  - Fuel stop when the meter is ≤ 0 (`jetpack.cpp:447-448`).
  - Stop rule (`jetpack.cpp:372-398`).
  - Post effect: time or 50 u ground probe (`:604-622`).
  - Reactivation delay 0.25 s (`P:weapons/mp_ability_valk_jets.nut:27, 562`).
  - The meter is set to glideDuration when the passive is gained (`:689-712`).
  - Jets stop when a grapple attaches (`jetpack.cpp:419-420`).

### Community / historical [comm]

- Reported uses: short-burst dodges; climbing, hovering and horizontal flight; a short burst before touchdown for a
  soft landing; and jets combined with a jump-pad double jump.
- The fuel, startup cost, thrust control, stop rule and holster limit are all called out as needed for a faithful
  reproduction.
- Version traps:
  - the **S27 fuel/thrust rework** and the 2026 crouch-flight discovery are *not* S21;
  - "Valk Moonboots" has an unknown removal date and keeps no S21 pass mark (report §五).
- Our 1.0 activation cost and 1.0 /s drain are this build's setfile. Do not mix them with current-season numbers.

### Unresolved [open]

- What starts the recharge: landing + 4.43 s or release + 5.0 s. To separate them, land at a different time after
  the release.
- Air recharge.
- The recharge delay and rate keys (not in the census).
- Horizontal and sideways jets with input at the M6 tightness values (Sideways 0.11 vs the 0.14 assumed in Unity).
- Fall damage after a 1889 u descent.

---

## 5. Pathfinder grapple extras (summary of what is already measured)

| Item | Result | Where |
|---|---|---|
| Release by a second `+offhand1` | Releases **on the press command** (latency 0). Momentum is kept to ±1.2 u/s, then plain ballistics (no drag, g 750). The `gr` flag lingers 13 commands with no effect. **Attack does not release.** | `../a3_zip/GRAPPLE-ZIP.md` §1 (n = 5 each) |
| Grapple → zipline | **Automatic handoff** (10/10, with or without `+use`). The mount comes the command after the grapple ends. v_entry = v_pre·rope + 400·dt along the rope, then the normal ride. The trigger is [open]. | `../a3_zip/GRAPPLE-ZIP.md` §2 |
| Range | Configured 850. Effective **830–840 u** at pitch 0 without the dev mod (M4/M4b ran with the ×2 range mod, but no hook exceeded 705 u). Out of range: nothing happens. | `../../m55/GRAPPLE-RANGE.md` |
| Pull law | RF model: along-rope ramp 541 u/s², constant cross-rope brake 423 u/s², s 0.68, target = aim hit + 32 u. W clamps v·ŵ at 483. Momentum kept on release. Jump does not release. The detach rule is unidentified. | `../../m4b/swing/SWING.md` |
| Interactions [src] | Jets and glide stop when the grapple attaches. A grapple detach ends mantle-boost state 4. A jump pad launches grappled players (SDK lifts the S3 ground gate). | `../SOURCE-AUDIT.md` (Grapple extras) |

**Still untested:**
- grappling **players** (enemy, friendly) and auto-aim bend (`GrappleAutoAim_FindTarget`, native) / grapple-to-melee;
- **moving entities** (movers, prowler detach above 400 u/s [src]);
- **deployables** (`AddEntityCallback_OnGrappled` is only used by levers);
- jump pad + grapple (G4) and the server forced release (G2);
- the vertical range limit.

All need a second entity or a scripted mover. They matter only if HSD gets multiplayer or moving platforms.

---

## 6. Comparison

M6-A moves:
- lurch / tap strafe (A1);
- climb / mantle / superglide (A2);
- zipline / Super Jump / grapple handoff (A3);
- slide.

Unity primitives (`HSD-Unity/Assets/HSD/R5Replay/Runtime`):
- `IMovementAbility`;
- `CommandModifiers` (gravityScale, launch, kinematic, drag);
- `InstantImpulse`;
- `TeleportAbility` (ZeroVelocity / FixedExit + `destinationResolver`);
- `JetpackAbility`;
- `GrappleAbility`;
- `ClimbAbility` / `ZiplineAbility`;
- `IMovementWorld` (`ResolveTeleport`, `ProbeGround`, raycast).

| | **Valkyrie jets** | **Ash Phase Breach** | **Loba translocation** | **Alter Void Passage** |
|---|---|---|---|---|
| Evidence | Measured (n = 10, 25 activations) + census + SDK | Measured (n = 20 + 11 re-entries) + source | Measured (n = 25, 15 teleports) + source | **Source only** (not triggerable here) |
| Mechanism uniqueness | **High.** The only sustained, controllable flight. A fuel economy that rewards continuous holds over bursts. | **Medium.** Targeted long-range relocation plus a persistent, re-usable one-way portal (a route/level tool). Exit speed 0. | **Low–medium.** A delayed relocation with speed zeroed. The arc and the drop give it some skill expression. | **High.** The only through-geometry traversal, and the only teleport that keeps speed (clamped 50–300 along the exit normal). Floor/ceiling portals give vertical exits. |
| Dev cost | **S.** The primitive already exists. Add the activation cost, the recharge (rate + delay), the 3 s post-effect timer, no post effect above terminal, and sideways tightness 0.11. | **S–M.** Kinematic path via `CommandModifiers.kinematic` (like the zipline). Targeting ray. Freeze = 0.15 + 0.1·frames. Exit 0 at 5 u above the hit. A **new** persistent portal object (15 s, re-entry). | **M.** Ballistic projectile with staged gravity and inherited velocity, drop redirect (≥ 0.24 s), plant + 0.4 s delay, landing validity (ground ≤ 1000 u below, safe spot), refund. | **M–L.** New world query (through-solid thickness, far-side exit and its normal, 30 m cap), a placement preview and validity UX, persistent paired portals (15 s, 0.7 s plant, 1.35 s debounce), velocity redirect, 1 s phase state. Its numbers cannot be verified in R5 here. |
| Primitives reused | `JetpackAbility` (all), `CommandModifiers.gravityScale` / `horizontalDragQuad` | `TeleportAbility` (FixedExit → exit 0, lock = travel) or `CommandModifiers.kinematic`; `IMovementWorld` raycast / `ResolveTeleport` | `TeleportAbility` ZeroVelocity, `IMovementWorld.ProbeGround` / `ResolveTeleport` | `TeleportAbility` (placement), `IMovementWorld.ResolveTeleport`, `InstantImpulse` / launch for the exit |
| New primitives | None (parameter and rule changes only) | Persistent world trigger (portal entity); aim-target resolver | Simulated projectile entity + redirect; landing validator | Thickness / exit-search query; paired portal entity; velocity-redirect exit mode; phase state |
| Combo potential with M6-A | **High.** Zipline Super Jump → jets; pad → jets; jets → mantle a high ledge; release above terminal keeps full speed (no cut) for a burst → lurch / tap strafe in the air; grapple cancels the jets [src]. | **Low for flow** (frozen 0.65–1.7 s, exit 0). **Medium as a route tool**: a portal into a slide or zipline start; a practice "return" portal. | **Low.** Zeroes speed; long latency (1.2 s throw + flight + 0.6 s). It can only set up a position or height for other moves. | **High in principle.** Slide into a wall at ≥ 300 u/s → exit at 300 along the normal; ceiling → floor drop into a slide; a portal into a zipline. The 300 cap limits high-speed chains. |
| Risks | Recharge trigger ambiguous (landing vs release). Unity currently applies the post effect after every stop and has no activation cost or recharge (it would change the M5.5 jets feel). | Breaks movement flow. Portal persistence needs ownership and team rules. Targeting edge cases are untested. | Low payoff for a speed game. Destination validity is terrain-heavy. | No measurement possible in this build (SDK placement). Level geometry must have thickness metadata. Exploit and softlock risk (exits inside geometry). |

---

## 7. Recommendation (for the user to decide; nothing is scheduled)

1. **Valkyrie jets: complete the existing Unity primitive** (S, high value, fully measured). These are parameter and
   rule changes inside `JetpackAbility`:
   - activation cost 1.0;
   - drain 1.0 /s (now measured, no longer assumed);
   - recharge 0.75 /s after a ~4.4 s grounded delay (flag the landing-vs-release ambiguity);
   - post effect only when the stop vz ≤ terminal, and it ends at 3.0 s or the 50 u probe;
   - tightness sideways 0.11 / down 0.1.
2. **Ash-style breach: only if HSD wants a long-range reposition or a route-building tool** (S–M).
   - The measured behaviour (freeze, exit 0) is anti-flow.
   - A cheap variant is `TeleportAbility` FixedExit with exitSpeed 0 and lock = 0.15 + 0.1·round(clamp(d/1200, 0.3, 1.8)/0.1).
   - The re-usable 15 s portal is the genuinely new part.
3. **Alter-style pass-through: the most distinctive mechanic for a movement game, but a design-from-source build**
   (M–L).
   - Worth a prototype only if the user wants a signature "through the wall" move. The source rule clamp(v·n, 50, 300)
     is a usable starting point.
   - It needs level thickness data or a through-solid query.
   - Optional: a further R5 attempt via the `sv_alter_portal_*` levers or a thin test wall, outside the stop-loss.
4. **Loba: deprioritise** (M, low fit).
   - The existing `TeleportAbility` ZeroVelocity already covers its movement effect.
   - If kept, update the timing defaults: press → throw ≈ 1.2 s from a weapon-out start, drop ≥ 0.24–0.3 s after the
     throw, drop → teleport ≈ 0.6 s. The current Unity delay of 0.25 s is a design value.
5. **Grapple extras:** release and zipline handoff are already measured and implemented (M6-A). Player, mover and
   deployable interactions stay low priority unless multiplayer or moving platforms are planned.

## 8. Open questions

1. Alter: which SDK component rejects the spot (near-face exit at 1.1 u vs the 216.5 u wall), and would a thinner
   wall or the `sv_alter_portal_*` levers make it work? This is the high-cost path.
2. Valkyrie: does the recharge delay start at landing (4.43 s) or at the jets/button release (5.0 s)? Is there air
   recharge? What are the native delay and rate keys?
3. Loba: the exact drop gate (between +0.05 and +0.30 s after the throw line; source 0.24 s), distance vs drop time,
   the refund path, and control after the teleport.
4. Ash: input response at the exit, the targeting cone/vertical/mover rules, and weapon return.
5. Grapple: players, auto-aim, movers, deployables, pad + grapple, and the zipline handoff trigger.

## 9. Failures and caveats (kept, not hidden)

- **Alter:** 21/21 trials without a portal. The conclusions are source-only.
- **Loba:** the drop-time sweep was mistimed. The runner assumed a 0.6 s pull-out, but the throw comes 1.2 s after
  the press. t07–t12 therefore pressed before the projectile existed, and those throws teleported in the following
  trial. They are reported as "carried over", not discarded.
- **Ash:**
  - the first run tapped only `+offhand4` and never fired (0/15);
  - in ash2 every other trial failed the runner settle, because the reset re-entered the live portal;
  - the client trace is not physics truth during the breach (prediction off), so only dedi MT and the dedi gap are
    used.
- **Valkyrie:** the glide meter is the client's predicted meter (`[HSD-STATE]`). The dedi fuel stop at 6.94–7.00 s is
  consistent with it. Only hold10 trials reached the recharge.
