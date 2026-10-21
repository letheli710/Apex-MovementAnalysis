# M3 — advanced movement tech (tap strafe, climb / wall bounce, mantle / superglide, landing chains)

Plan M3:

- Break each piece of advanced tech into input timing, trigger condition and velocity change.
- Measure trigger windows at several frame rates; give bounds where sampling limits precision.
- Put tap strafe and one wall or landing link into Unity and verify them.
- Give design advice: what to copy, simplify or remove, and how to make it frame-rate independent.

Branch `phase2-local/m3-tech` (research) and `m3/advanced-tech` (HSD-Unity).

Detail reports:

- [lurch/LURCH-MODEL.md](lurch/LURCH-MODEL.md)
- [wall_mantle/WALL-MANTLE-MODEL.md](wall_mantle/WALL-MANTLE-MODEL.md)

Both analyses were re-run by the lead, with byte-identical results.

## 1. Acceptance

| # | Criterion | Result |
|---|---|---|
| A1 | Trigger logic and window data for tap strafe, climb/wall jump, landing links | **PASS** (§3) |
| A2 | Windows at several frame rates; bounds where sampling limits precision | **PASS**: 60/120/144 fps. Lurch and mantle-boost windows are both **time-based** (§3.1, §3.3). 144 fps mantle boost: lower bound only (§4) |
| A3 | Tap strafe + one wall/landing link implemented in Unity and verified | **PASS**: lurch press-command error ≤ 0.04° on the plateau; slide-chain link 88.4 → 2.2 u RMS; 67/67 tests (§5) |
| A4 | Design advice: copy / simplify / remove; frame-rate independence | **PASS** (§6) |

## 2. Data

All trials were automated: Gibraltar pinned, empty-handed (movescale 1.15), z 294.92 test field.

- **Test wall.** The field has no vertical walls, so a wall-run rock is spawned on it the way the map editor does (`tools/test_geometry.py`). Face at x ≈ −13706, about 232 u tall.
- **Frame rate.** An external ~138 fps cap appeared during M2 (not caused by game settings), so M3 runs mostly at **120 fps** (stable 119.9). 60 fps and earlier 144 fps sessions are used for frame-rate dependence.
- **Rejected trials.** Every trial outside ±3 % of the target fps, or with a frame-count mismatch, was rejected and re-run. None is used in a fitted value.

| Session | fps | Content |
|---|---|---|
| `M3_lurch_chain` | 144 | lurch sweep K = 1…90 frames ×2, back / W re-tap, walk / slide speed |
| `M3_wall_chain` | 144 | climb, wall bounces, mantle sweep (early), chains |
| `M3_fps120` + rerun | 120 | mantle per-frame sweep, chains, lurch sweep |
| `M3_fps60` | 60 | lurch sweep, mantle sweep |
| `M3_late_hops120`, `M3_late60` | 120 / 60 | late mantle presses (boost window), hops above 299 at D = 0…10 frames after landing |

## 3. Mechanics

### 3.1 Tap strafe (lurch)

**Trigger.** The press edge of a new horizontal direction input while airborne. The effect is applied only on that command, after AirAccelerate.

**Velocity change.**

- λ = 0.7 · clamp((0.5 − t)/0.3, 0, 1), where t is the time from the start of the jump command.
- d = normalize((1 − λ)·v̂ + λ·wishdir).
- Δv = |v|·d − v, with |Δv| clamped to **209.3 u/s**.

λ = 0.70000 (sd 3e-6). The formula reproduces all 102 trials to 0.002 u/s.

**Window.** It is **time-based**: full strength up to 0.200 s, then a linear fade to 0 at 0.500 s. This was verified at 60/120/144 fps, with edges known to about ±1 ms.

**Speed dependence** comes only from the 209.3 clamp:

- walk speed: −65°;
- sprint 299: −44.5°;
- slide jump at 350: −37°.

**Back press.** The target flips, so the lurch becomes a straight 209.3 u/s brake. **W re-press** does nothing.

**Dedi parity.** The S3 dedi reproduces it natively (101/102 bit-exact, 1 at 0.022 u/s). This resolves the Phase 1 contradiction X1.

### 3.2 Climb and wall bounce

**Climb.** On contact the horizontal speed is killed (299 → 2.8).

- vz accelerates at about 490 u/s² up to about 180 u/s, then falls linearly with height.
- The climb ends at an absolute height of about 441.9 (96 u above contact, after 0.85 s), with a jump-up and a 68 u/s kick-out.
- Then comes a 0.588 s scripted mantle, which exits at exactly 299 u/s forward.
- Client and dedi drift by up to 0.13 u during the climb. This is the first mechanic that is not bit-exact.

**Wall bounce.** Δv = wallNormal·182.78 + inputDir·75.08. The input is normalized; no input counts as the wall normal. Vertical speed is kept.

- Census values: outward 188, input 75, up 240. The 240 up speed is not applied.
- The press time within the climb (0.15 s vs 0.40 s) does not matter.

### 3.3 Mantle boost / superglide

**Trigger.** A jump press inside the last **133 ms** of the mantle.

- That is 16 frames at 120 fps and 8 at 60 fps, the same time at both rates.
- In traversal fraction it is ≥ about 0.78, while the camera-pitch delta is below 1.5°.

**Exit.** Boosted: 388.7 u/s horizontal (1.3 × 299) and vz 367.4 (= √(2·750·90)), matching the SDK FSM exactly.

**Failure cases.**

- Pressing earlier in the mantle gives a failed boost, which is an ordinary 56 u jump.
- Pressing during the climb gives a wall bounce.

**Classic jump + crouch** behaves exactly like jump only, so in this build superglide is the SDK's time-window FSM, not a frame-order exploit.

**Misprediction.** 1 in 30 boosts was mispredicted by the client (press on the last mantle frame) and corrected by the dedi three commands later.

### 3.4 Landing links

- **Jumping from the ground** caps horizontal speed at the ground cap (299 sprint).
  - Hops from a 350 slide jump lose 51.2 / 40.7 / 30.3 / 19.9 u/s at D = 0/1/2/3 frames after landing, because the speed bleeds at 1250 u/s² while on the ground before the jump.
  - The multi-jump height penalty applies (V = 158.7 = 289.8·√0.3).
  - `skip_speed_reduce` (−100) was not observed. min(v, 299) and max(v − 100, 299) cannot be told apart below 399 u/s.
- **Landing with crouch held** resumes the slide with no loss. A slide jump from the resumed slide keeps its speed (the 350 floor does not apply).
- **A 232 u drop** (impact −585 u/s) showed no landing slowdown.

## 4. Open items

| # | Item | Why open |
|---|---|---|
| O1 | Lurch: cutoff speed 1100, other move scales, diagonal and full-stick presses, repeated presses in one window, walk-off without a jump, suppression after a mantle boost | not covered by the schedules |
| O2 | Mantle boost window at 144 fps | client capped at ~138 fps (external); only a lower bound measured |
| O3 | Climb end rule (absolute height vs ledge vs climbHeight) | one wall height only |
| O4 | Side-press wall bounce (140.9 / 177.5 split) | not explained by the 2-term formula; measured vector kept |
| O5 | `skip_speed_reduce`, `landSlowdownDuration` | not triggered by any input tried |
| O6 | Ground redirect after landing with a strafe key held: R5 turns velocity at about 1250 u/s² (the M2 model redirects instantly) | M2 turn data had W held while turning the view; needs a ground-turn-with-strafe experiment |
| O7 | Crouch-height transition (about 16 u origin drop when releasing duck mid-air) | motor has no stance-height model |

## 5. Unity

`HSD-Unity`, branch `m3/advanced-tech`, model id `R5MotorV2/m3`:

- **Lurch** sits in the air step after AirAccelerate. Its parameters are in the preset: 0.7 / 0.2 s / 0.5 s / 209.3.
  - The press edge is a 0x618 move bit that was not held on the previous command.
- **Ground re-jump cap**: min(v_h, cap).
- **Slide-chain rules**: landing while ducked resumes the slide; a slide jump from a resumed slide keeps its speed.
- **Reusable primitives** for the game controller: `WallBounce` (normal·182.78 + input·75.08) and `MantleBoost` (last 133 ms of the mantle → ×1.3 exit + 90 u jump; otherwise an ordinary jump).
- **EditMode tests: 67/67** (48 old + 19 new: lurch plateau/fade/clamp/back-brake/W no-op, the time-based window at 60/120/144 dt, ground-jump cap, slide rules, WallBounce, MantleBoost edges). Re-run by the lead.
- **Replay of the 30 M3 trials** ([unity/index.md](unity/index.md)). The lead re-ran it:
  - 22 trials were byte-identical to the subagent's output.
  - 8 were re-exported with the census they lacked (those sessions ran without one), then replayed again.

| Condition | Press-command heading error | Press Δv error | Before (M2 motor) |
|---|---|---|---|
| lurch plateau (t < 0.2 s), back-brake, W re-press | ≤ 0.04° | ≤ 0.011 u/s | up to 64° / 209.3 u/s |
| lurch fade (t 0.25–0.49 s) | ≤ 0.25° | 0.02–1.98 u/s (≈ 1 ms window clock) | |

**Other trial results:**

- Air phase (take-off → landing): about 0.1–0.4 u position RMS on most e3 trials, against 15–72 u before.
- **Landing link e8_slide_chain: 88.4 → 2.2 u position RMS.**
- M2 e2_strafe (one lurch each): 80.8 → 0.47 u position RMS, heading 43.6° → 0.006°.

**M2 regression:** 35/37 M2/M1 trials are byte-identical; the 2 that changed are exactly the e2_strafe trials above.

**Where error remains** (none of it from the new formulas):

- **Ground phase after a lurch landing** (e3 overall 12–43 u). R5 turns the landed velocity toward the held key at about 1250 u/s². The M2 ground model redirects instantly; M2 measured instant redirect only while turning the view with W held. → open item O6.
- **Crouch release in the air** (slide350, fast hops). R5 lowers the origin by about 16 u when the duck is released mid-air, so landing comes 8–10 steps late. The motor has no crouch-height transition, so the 350 → 299 re-jump cap is covered by a unit test, not by the replay. → O7.
- **Not replayed:** wall, climb and mantle (no wall geometry in the replay). They exist as tested primitives.

**Acceptance A3: PASS.** Tap strafe and one landing link (slide chain) are implemented in Unity and verified against real trials. Wall bounce and mantle boost are implemented as verified-formula primitives.

## 6. Design advice for High Speed Doom

| Mechanic | Apex behaviour (measured) | Advice |
|---|---|---|
| Ground accel / decel, sprint, crouch | piecewise accel, constant decel, instant redirect | **Copy.** These carry the "feel"; all values are in the parameter table |
| Air control | AirAccelerate 500·dt, cap 69 (60·msc), no drag | **Copy.** Already frame-rate independent |
| Jump + multi-jump penalty | V = √(2gh·frac), frac 0.3 → 1 over 0.15 + 0.60 s after landing | **Copy, but expose** hold/ramp as tunables. The penalty is what stops bhop spam |
| Slide | boost to min(v + 150·msc, 460), decay (v − 100·dt)·0.7^dt, refund within 0.4 s, 350 slide-jump floor | **Copy.** The refund rule is the anti-exploit that keeps slide-jumps honest |
| Tap strafe (lurch) | time-based window 0.2 s full, fade to 0.5 s, λ 0.7, \|Δv\| ≤ 209.3 | **Copy as a designed window.** It is already time-based, so it is frame-rate independent in Apex. The 209.3 clamp is the natural tuning knob. Consider a UI/telemetry cue during the window for training |
| Back-press brake | same formula: a straight 209 u/s brake | **Keep.** It is a legitimate air-brake skill |
| Climb | speed killed on contact, climb to a fixed height band, 0.59 s mantle | **Simplify:** expose climb height and duration; skip the drift; use a deterministic mantle curve |
| Wall bounce | wall-normal 182.8 + input 75.1, vertical kept | **Copy.** For the side press, use the measured vector or a simple input blend |
| Mantle boost / superglide | last 133 ms of the mantle, exit ×1.3 + 90 u jump; failed press = normal jump | **Copy as a time window**, not frame-order. Optionally widen it for practice (a training slider), and show a success indicator |
| Landing → re-jump at speed | re-jump caps at the ground cap; speed bleeds at 1250 u/s² while grounded | **Copy.** The tiny grace window is the skill ceiling; a practice mode can show the lost u/s per hop |
| Frame-rate dependence | lurch and mantle boost are time-based. Jump apex differs by about V·dt/2 (frame rate). Frame-indexed inputs change the effective timing | **Remove frame binding:** run the Unity motor at a fixed step (or the measured per-command dt in replay) and define every window in seconds |
| Client/dedi corrections | 1/30 mantle-boost presses mispredicted; climb drift | **Drop:** a single-player game has one authority |
