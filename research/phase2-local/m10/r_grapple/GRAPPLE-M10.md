# M10 track R ①: Pathfinder grapple techniques, pull model check, detach rules

Status: 3 local sessions on the R5Flowstate **local hybrid build (S21 client + S3 dedicated server + SDK)**, offline, 120 fps,
Pathfinder with kit. Nothing is committed. Labels: **[meas]** measured here, **[src]** class vars / convars / scripts of the
local build, **[inf]** interpretation, **[hyb]** an S21-client vs S3-dedi difference (the dedi is authoritative locally).
Spec column = track D `m10/d_library/TECHNIQUE-LIBRARY-M10.md` §6 (agree / contradict / not testable).

## TL;DR

| Question | Answer | Evidence |
|---|---|---|
| Is there a pendulum / swing mode? | **No.** The Pathfinder setfile (`pilot_survival_grapple`) has **`grapple_swing = false`**. Under an overhead anchor (rock underside, sprint jump below it, no input) the player overshoots 93 u past the anchor's vertical and is pulled back; the horizontal speed is braked, not swung. | [src] + [meas 3] |
| The RF pull model | Confirmed and now **parameterised from the class vars**: speed ramp `grapple_speedRampMin 50 -> speedRampMax 800 over speedRampTime 1.5 s` = 500 u/s² (measured d\|v\|/dt 500.0–502.7, n 17); tangential brake = `grapple_decel 425` (M4b C = 423); W clamp = `grapple_airSpeedMax 420`·msc = 483 (v·ŵ = 483.000 exactly again, n 3), W accel `grapple_airAccel 650` (M4b 645); attach hop 200 (dedi setfile reads 0, client 200: [hyb], the motion shows vz 193.7 = 200 − g·dt both sides); wind-up = convar `grapple_pullDelay_human 0.2`. | [src] + [meas] |
| Speed beyond the RF base? | **Yes, from input, without a swing state.** A or D held during a 45–50° pull (view fixed): max \|v\| **938–945** vs 796 without input; sideways speed across the rope up to ~600; heading change 130–220°. D on a level wall pull: max 784 vs 612. Track D's Slingshot script (80° turn, W+A, swap to W+D): **854** (600 u anchor) / **911** (800 u anchor) vs 796 / 799.5 hold. Side keys behave like air strafe: `grapple_airAccel 650` beats the 425 tangential brake. The wiki's ~1200 was not reached here. | [meas 2–3 per row] |
| Jump Grapple | Ground hook 700 u ahead; a jump within **18 commands (0.15 s) after the attach hop adds the normal jump (+280.5 vz)**; at 24+ commands it does nothing (coyote 0.2 s). Exit v_h **1000–1030** vs 797 without the jump; 400 u: 755 vs 599; sprint start fires on the ground and loses the run-up. Speed above 800 comes from gravity along a rope that points down (convar `grapple_letGravityHelpCosAngle 0.8`, `grapple_dontFightGravity 1`) [inf]. | [meas 30] |
| Grapple hop | Hook straight down (pitch 89): the anchor is already inside the detach distance, so there is no pull, only the 200 hop. A jump on the attach command or up to 4 later stacks: apex **146–155 u** vs 55 for a plain jump (vz 200 + 280). | [meas 16] |
| Detach rule | Four rules, all one-command and momentum-preserving except the press clamp: **(a) proximity**: released while approaching when the anchor is 35–53 u from the player's vertical segment [origin, origin+72] (mean 44.3 on the last pulled command, n 96; no single constant threshold, consistent with `grapple_detachLengthMin 33 / Max 50`); **(b) passing the anchor**: released 1 command after the motion turns away from the anchor (radial −28..−214 u/s), view angle ~85–110° (n 41); **(c) crouch press** and **(d) second tactical press** release on that command; the tactical press **clamps the speed to 460** when faster (580 → 458.7, 675 → 458.5; `grapple_detachSpeedLoss 300 / Min 460`), below 460 it keeps momentum (n 21). **(e) look-away (anchor > ~100° off the view)** is predicted by the S21 client but the S3 dedi keeps pulling for another 0.6–1.2 s [hyb]: the S21 rule exists in the client, the local authority ignores it. | [meas] |
| Rodeo / orbit | The wall-corner Rodeo (2 designs) released after a 17–32° heading change. Under the overhang with D held and the view turning 120°/s ("tether"), the path **turned 393° (more than one full orbit)** in a 2.27 s pull, max 700 u/s. So a one-lap orbit exists with side strafe + view tracking. A thin pole could not be tested (spawning unknown props hung the dedi once). | [meas 2] |
| Firing on the ground | The fire kills the horizontal speed before the attach: sprint 297 → 0, slide 421 → 362; in the air it is kept (297). | [meas 3 each] |
| Not reproduced | Super Grapple (hook never connected, 2 designs: stop-loss); Slide Grapple (hook missed the rock edge, 1 design: design miss, not retried); Grapple Double-Bounce (the second grapple simply attached and pulled into the wall, no climb-space reset seen). | [meas] |

## Data and exclusions

| Session (data/) | Content | Excluded |
|---|---|---|
| `20261022_202105_M10R_g1` | lane A (M3 rock, face x −13706): distances, pitches, entry states, keys, release presses, look-away, crouch, rodeo, super grapple, double bounce; lane B (open floor): jump grapple g200/g400/g700 × k, hop; class-var census (`--client-exec user/hsd_m10_classvars`) | r16121, r16123 `hop_j1` (fps 107 / 113) |
| `20261022_202939_M10R_g2` | `m10fly` rock floating at (−13300, 5900, floor+700): slingshot (600 / 800 u anchors), A/D/S, turns, release, overhead jumps, slide grapple | r16301 `sl_hold`, r16329 `over55_jump_w` (frame count +2/+8), r16344 `sl8_jump`, r16347 `sl_a` (fps 115.6 / 114.7) |
| `20261022_204553_M10R_zip` (grapple part) | release presses at 1.6 / 1.8 s from the far start, tether under `m10fly` | r16471 `tether` (frame count +3) |

Loggers added for M10 (tools/hsd_trial.py): dedi `[M10-GRS]` (grapple flags, hook origin, 10 Hz) and client `[M10-GRC]` (flags,
hook origin per frame). The client pull flag flickers only in look180 / rodeo (the [hyb] case above); everywhere else the dedi
flag ends 0.11–0.21 s after the client's, a constant logging offset (n 137).

## Model for HSD (Reference)

- Keep RF, now with source values: ramp 50 → 800 in 1.5 s along the rope, tangential brake 425, gravity fraction 0.25–0.7, no swing state.
- Add **wish acceleration during the pull for every key**, not only W: `airAccel 650` up to `airSpeedMax 420·msc` along the wish (the measured W clamp on v·ŵ). That alone produces the Slingshot gain (+60 to +150 u/s) and the one-lap tether orbit; no pendulum term. S held raised the pull (740 vs 612 at release) — keep it as measured, unexplained.
- Gravity helps when the rope points down (jump grapple exit ~1000–1030 from a 700 u ground hook).
- Detach: proximity 35–53 u to the player segment (use 45), passing the anchor, crouch, tactical press (clamp to 460 if faster). Do **not** use a view-angle detach in Reference (local authority has none; mark the S21 client rule as an open version question).
- Grounded fire: zero the horizontal speed during the hook flight; airborne fire keeps it.

## Open questions

1. The exact proximity threshold (33..50 interpolated by what?) — the hold_w / dbounce cases release closest (36–37 u).
2. Why S held speeds the pull up (629 vs 473 u/s² along the view).
3. The look-away detach: S21 client predicts it at ~100°, the S3 dedi does not; the true S21 server behaviour is unknown.
4. A thin-pole Rodeo (multi-lap), Super Grapple, Slide Grapple, double bounce: not reproduced; Drag Grapple = the g200/g400 runs (pull along the floor, release on passing).

## Rerun

```
cd research/phase2-local/m10/r_grapple
py -3 grapple_analysis.py ../../data/20261022_202105_M10R_g1 ../../data/20261022_202939_M10R_g2 ../../data/20261022_204553_M10R_zip \
  --json results.json --params params.json > analysis_output.txt
```

Sessions: `tools/hsd_session.py --label M10R_g1 --trials 3 --run-base 16001 --batch-base 16001 -- --fps 120 --legend pathfinder --kit
--state-log --m10-log --geometry m3 --client-exec user/hsd_m10_classvars --schedule <49 m10_g_* names>`; `--label M10R_g2 --run-base 16301 --
... --no-census --geometry m10fly --schedule <21 names>`; the zip session (see `../r_zipgun/ZIPGUN-M10.md`). The census cfg is
`research/phase2-prep/cfg/hsd_m10_classvars.cfg` (copy to `<game>/platform/cfg/user/`). Output reproduces byte for byte (checked).
