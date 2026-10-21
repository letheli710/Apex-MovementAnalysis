# M5 part A: skill slots, interaction rules, RF grapple, presets

Scope: R5Flowstate S21 measurements (M2–M4b) turned into a playable rule set. Every Apex number below comes from the
measurement docs; every number marked **design** is a practice-game choice with no Apex reference.

Code: HSD-Unity branch `m5/skill-slots`, `Assets/HSD/R5Replay/Runtime/Skills/` (rules, arbiter, loadouts, test world, body) and
`Runtime/Abilities/` (the M4 primitives, the RF grapple, the teleport and wall-jump primitives). Replay and regression results:
[unity/regression.md](unity/regression.md).

## 1. Slot system

| Part | What it is |
|---|---|
| Loadout (`SkillLoadout`, asset `SkillLoadoutAsset`) | Up to **4 generic slots**. Each slot holds one ability id, a button (`Slot1..Slot4`, `Jump` for the jets, `None` for a passive), charges and a cooldown per charge. Validated: 1–4 slots, known ids, no ability or button twice, passives take no button, the jets take jump, one air profile. |
| Base layer (always on, not a slot) | Landing slowdown (OCTANE §4; duration 0 with the Horizon air profile) and the wall jump. |
| Rules (`SkillRules`) | All numbers of §2–§4 as serialisable data, stored in the loadout. |
| Arbiter (`SkillArbiter`) | The **only** code that applies the rules. It hooks into the M4 `MovementAbilitySet` (`IAbilityArbiter`). Without an arbiter the set behaves exactly as in M4. |
| Body (`SkillBody`, `SkillInput`) | Motor + loadout + optional test world. It turns held buttons into the usercmd form (press edges, direction-key edges for the lurch, slot bits) and runs one `Step` per fixed command. The later runtime player controller fills `SkillInput` and calls `Step`. |
| Test world (`BoxWorld`) | Flat floor plus axis-aligned boxes; hull 32 × 32 × 72 u, step-up 18 u. It gives the floor under the body (walking off a ledge starts a fall), pushes the hull out of walls and removes the velocity into the face (R5 wall impact, SWING §5), reports the wall contact, answers the grapple raycast and clips teleports. Ceilings are not handled. |

Every ability reports a **state**: Idle, Pending (accepted, not yet acting), Driving (moves the body every command) or
Effect (timed modifier only). It also reports an activation count and has `Interrupt`, which ends any state and keeps the
velocity.

| Ability | Pending | Driving | Effect |
|---|---|---|---|
| grapple | hook flight + 0.2 s wind-up | pull | – |
| gravity_lift | – | ride (inside the lift) | – |
| jets | – | thrust (jump held) | post effect (0.45 g + drag until 50 u above ground) |
| teleport / portal | press → teleport delay | portal: control lock | – |
| pounce | pull-out + charge | – | flight (move scale 1.0 until landing) |
| jump_pad | – | – | slow-mo flight until landing |
| stim / wraith_phase | onset delay | – | boost (with Wraith's deploy slow) |
| wall_jump | – | – | – (instant) |

Per command, in this order:

1. **BeginCommand** (before any ability).
   - Charges recharge.
   - A slot press is masked, so the ability never sees it, when the slot has no charge (`SLOT_REFUSED_<id>_COOLDOWN`) or an
     exclusive lock runs (`…_LOCKED`).
   - An airborne jump press is masked while something is Driving (`JUMP_BLOCKED_DRIVING`).
2. **Abilities' BeforeMove.**
3. **CombineBoosts.**
4. **AfterAbilities.** Launch choice and clamp; the launch ends drivers and opens the lurch window.
5. **Late hook (grapple).** The pull uses the final move scale and input.
6. **Motor move.**
7. **Abilities' AfterMove.**
8. **EndCommand.**
   - Charges are spent.
   - An exclusive ability that acted ends every other state.
   - At most one Driving state remains.
   - Timeouts fire.
   - The speed ceiling is applied.

## 2. Per-ability rule table (`SkillRules.DefaultTraits`, preset charges / cooldowns)

Timeouts are guaranteed exits: once the state has lasted that long the arbiter interrupts it (event `…_INTERRUPT_TIMEOUT`).
Each one sits above the longest measured or modelled duration, so the timeouts never change a measured behaviour.

| Ability | Priority | Interruptible | Exclusive | Max Pending / Driving / Effect (s) | Longest modelled duration | Charges × cooldown (presets, **design**) |
|---|---|---|---|---|---|---|
| teleport, portal | 100 | no | **yes** | 2.0 / 1.0 / – | delay 0.25, lock 0.3 | 1 × 6 s (portal) |
| jump_pad | 80 | – | no | – / – / 6.0 | slow-mo flight ≈ 3.4 s | 1 × 15 s |
| wall_jump | 70 | – | no | – | instant; one per 0.4 s (**design**) | – |
| grapple | 60 | yes | no | 1.0 / 3.0 / – | hook ≤ 0.42 + 0.20 s; pulls ≤ 1.55 s measured; own 3 s guard | 2 × 8 s, 1 × 8 s (aerial) |
| gravity_lift | 50 | yes | no | – / 6.0 / – | 1080 u rise at 300 u/s + 0.5 s hover ≈ 4.1 s | 1 × 12 s |
| jets | 40 | yes | no | – / 9.0 / 10.0 | fuel 8 s (drain 1/s **assumed**, M4) | none (fuel) |
| pounce | 30 | – | no | 2.5 / – / 6.0 | pull-out 0.9 + charge 1.3; auto-fire at 2.2 s (**design**) | 1 × 6 s |
| stim | 10 | – | no | 0.5 / – / 7.0 | 0.16 onset, 6.0 + 0.5 s | 1 × 4 s (the stim's own reuse lockout still applies while it runs) |
| wraith_phase | 10 | – | no | 0.5 / – / 5.0 | 1.17 + 2.77 + 0.79 = 4.73 s | 1 × 10 s |

- **Cooldown semantics.** A charge is spent when the ability's activation count grows, not on the press: a grapple miss, a
  refused stim tap or a press during the ability's own lockout costs nothing. A spent charge comes back one cooldown after the
  use that emptied a full slot; the next charge comes one cooldown later.
- **Priority** decides only (a) which launch wins when several land on the same command, and (b) which driver stays when two
  start on the same command.

## 3. Interaction rules (the combo table)

| # | Situation | Rule | Source | Test |
|---|---|---|---|---|
| R1 | Two drivers (grapple pull, lift ride, jets, portal lock) | At most one. The **newest** keeps driving, the older is interrupted with its velocity kept (`PREEMPTED`). An exclusive driver always wins. Starting the second one overlaps the first for one command. | design | `NewerDriverWinsLiftThenGrapple`, fuzz invariant |
| R2 | **Jets + grapple** | The grapple pull preempts the jets: no vz ×0.4 and no post effect, momentum kept. During the pull an air jump press engages nothing (`JUMP_BLOCKED_DRIVING`): jump does not release the grapple (SWING §5) and does not start a second driver. | R5 (jump) + design | `GrapplePreemptsJetsAndJumpDoesNotEngageJetsDuringThePull` |
| R3 | **Grapple release → slide** | The release keeps the momentum exactly (SWING §5). A landing with duck held resumes the slide with **no** boost. The slide jump from that slide keeps v_h: no 350 floor and no refund (M3 slide chain), and it adds nothing. The landing slowdown applies above \|vz\| 772. | R5 | `GrappleReleaseIntoSlideAndSlideJumpStayBounded` (ledge-edge grapple, lands on the ledge top) |
| R4 | **Pad → lurch** | A velocity-replacing launch (pad, pounce, lift eject, portal exit) starts the lurch window like a jump command. The lurch then redirects the velocity, never above \|v\|, with \|Δv\| ≤ 0.7 × the current sprint cap. Switch: `launchOpensLurchWindow`; off = the M4 motor, where a launch is not a jump. | **design** (R5 pad-lurch not measured) + R5 lurch | `PadThenLurch` |
| R5 | **Stim + pad** | The pad launch is a fixed 1150 u/s vector (OCTANE §3.1), so the stim does not scale it. The stim scales only msc terms: air wish cap, sprint cap, lurch clamp. | R5 | `StimDoesNotScaleThePadLaunch` |
| R6 | Speed multipliers (stim, Wraith phase) | Slows (< 1: Wraith deploy, landing recovery) multiply. Boosts (> 1) do not stack: only the largest counts (`boostStacking = Max`), capped at ×1.40. `Multiply` is available, still capped. | design | `BoostsDoNotStack` |
| R7 | Launch vs launch on one command | One launch per command; the higher priority wins and the losers are interrupted. The winner is clamped to the ceiling. | design | fuzz |
| R8 | Launch during a driver (pad under a lift ride or a grapple pull) | The launch ends every interruptible driver and that command runs at full gravity. | design | `PadLaunchEndsALiftRide` |
| R9 | **Wall jump → impulse** | An airborne jump press within 0.1 s of a wall contact adds n̂·182.78 + d̂·75.08 (M3 WALL-MANTLE §3.2) and counts as a jump (lurch window). It uses up the press (no jets on it), one per 0.4 s. A later launch replaces the velocity; it never adds to it. | R5 formula + **design** gating | `WallJumpThenPounceIsBoundedAndOpensTheLurchWindow` |
| R10 | Teleport (Loba) / portal | The body moves to the destination (clipped by the world). Loba: v = 0, no lock (P3). Portal: fixed exit velocity, 0.3 s control lock with every other slot refused (P3 from source). Either way every other Pending or Driving state ends: a pending hook would pull back to the old anchor. Nothing carries speed across, as in Apex. | R5 (P3) + **design** numbers | `PortalExitLocksControlsRefusesOtherSlotsAndCancelsPendingStates` |
| R11 | Grapple into geometry | The pull ends 34.1 u in front of the hooked surface (envelope; the R5 rule is unidentified), on any wall contact, on landing, or at 3 s. A hooked top face approached from below releases once the origin rises above it. | R5 envelope + design guards | `DetachEnvelopeTimeoutAndMiss`, `ContactEndsThePull` |
| R12 | Lift + grapple | R1: the grapple pull (newer) ends the ride with no eject impulse. Lift re-entry stays blocked 2 s. | design | `NewerDriverWinsLiftThenGrapple` |
| R13 | Every state | Timeouts (§2) plus the natural exits: landing ends the pad slow-mo, the pounce flight, the jets and the grapple pull. After 12 s without input every preset is Idle and on the ground (fuzz). | design | `SkillFuzzTests` |

## 4. Global caps

| Cap | Value | Why |
|---|---|---|
| Horizontal speed ceiling | **900 u/s**, applied after every command and on every launch (`SPEED_CEILING`, `LAUNCH_CLAMPED`) | Above every measured R5 value: grapple release 804 (far), pad 514, slide boost cap under stim 400 × 1.15 × 1.298 = 597 (644 at the ×1.40 boost cap). In R5 the grapple has no terminal speed, so this is the only cap on a long pull. |
| Upward speed ceiling | **1100 u/s** | Pad 1028.6 |
| Boost cap | ×1.40 | Wraith ×1.388 and Octane ×1.298 fit under it |
| Impulse stacking | Launches **replace** the velocity (R5 pad, pounce, lift eject). The additive impulses are each bounded and gated: lurch \|Δv\| ≤ 0.7 × sprint cap and \|v\| never grows; wall jump +258 max, one per 0.4 s; slide boost capped at 400·msc with the 0.4 s refund. | M3/M4 + design |
| Sustained states | Mutually exclusive (R1), every one with a timeout (§2) | design |

## 5. Preset loadouts (`SkillLoadouts`, assets in `Assets/HSD/R5Replay/Presets/Loadouts/`)

| Preset | Slots | Combos it exercises |
|---|---|---|
| Pathfinder-Octane mobility | grapple (Slot1, 2 × 8 s), stim (Slot2, 1 × 4 s), jump_pad (Slot4, 1 × 15 s) | grapple release → slide, stim + pad, pad → lurch |
| Valk-Horizon aerial | jets (Jump), horizon_air (passive: air 80 / 800, no landing slowdown), gravity_lift (Slot1, 1 × 12 s), grapple (Slot4, 1 × 8 s) | jets + grapple, lift → grapple, lift eject → lurch |
| Revenant-Wraith ground | pounce (Slot1, 1 × 6 s, auto-fire at full charge), wraith_phase (Slot2, 1 × 10 s), portal (Slot4, 1 × 6 s) | wall jump → pounce, phase + slide, portal lock |

All presets use the measured ability parameters. The fun configs come in a later part.

## 6. New or changed primitives

- **Grapple → RF** (SWING §6 and r2.joint.RF). Model choices:
  - Aim ray from origin + 60 (the eye height the fit assumed). The target is the hit at fire + 31.9 u, world-fixed.
  - Attach at fire + 0.0043 + L/2035. vz is **set** to 200 on the attach command, also in the air. Then a 0.2005 s wind-up.
  - Pull per command: along-rope +541 u/s², cross-rope constant brake 423 u/s², gravity 0.68 g on the cross-rope part only.
    It is integrated as a constant acceleration (trapezoid, as in the fit).
  - Move input: the velocity along the flat wish direction is accelerated at 500·msc and hard-clamped at 420·msc. This was
    measured with W only.
  - Momentum is kept at release. Jump does not release.
  - The M4 F1 pull and its 4-command burst were removed. Adding the burst in front of RF was tried and made the replay worse
    (regression.md).
- **Wraith phase** = `StimParams.WraithPhase()` on the existing `StimAbility`: deploy ×0.80 for 1.17 s, then ×1.388 for
  2.77 s, then a 0.79 s fade, with no sprint mod (P3). The fade shape is not resolved; cosine is assumed.
- **Teleport** (`TeleportAbility`).
  - Loba preset: v = 0, no lock.
  - Portal preset: 300 u/s exit along the view, 0.3 s lock.
  - Distance 400 and delay 0.25 are **design** values.
- **Wall jump** (`WallJumpAbility`): the M3 wall bounce formula with the gating of R9.

## 7. Open items and assumptions

- The **grapple detach rule** is still unidentified. Unity uses the 34.1 u envelope plus contact. In the M4 replay the
  envelope releases 2–4 commands after the recorded detach (regression.md).
- The **RF pull** gives a worse pull-window position RMS than F1 on the 4 M4 trials: F1 was fitted on those geometries, RF is
  the joint fit over 62 trials. Velocity and release direction are much better with RF (regression.md).
- **Unmeasured combinations**, chosen by design (R4 and R9 are labelled): pad → lurch (does R5 open the lurch window on a pad
  launch?), jump-pad double jump, wall jump from a non-climb state, and the pounce auto-fire.
- The **ceilings, boost cap, timeouts, charges and cooldowns** are design values.
- **Jets fuel drain** of 1/s is still an assumption (M4).
- `BoxWorld` is a test stand-in. The game needs a physics adapter for the same three calls: floor height, push-out with
  contact, raycast. It has no ceilings, slopes, climb or mantle (Unity wall/mantle: formula and unit tests only, M3).
- **Frame-rate dependence.** Spatial triggers (pad and lift volumes, landings, contacts) are tested at command starts, so at
  60 Hz they move by up to one command. Chains that pass through an aimed ability amplify this: a 60 Hz run reached a
  34.7 u/s velocity difference after 5 s (regression.md).
