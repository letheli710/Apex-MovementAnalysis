# M6 difference audit (before M6-A)

Date: 2026-10-21. Baseline: research `main` = 798734a (M5.5 merged); HSD-Unity `main` = dc649e9 (M5.5 + fps-camera-design skill).
Evidence classes used throughout M6:

- **[meas-R5F]**: measured in our local R5Flowstate S21 runs.
- **[src]**: read from pinned source (`s21-r5sdk@10077bb`, `s21-platform@9b21dc9`); [src-sdk] = SDK reimplementation, [src-script] = Squirrel, [src-native] = engine boundary only.
- **[community]**: community/wiki/video claims (the 2026-10-20 report).
- **[official-hist]**: official S21 history.
- **[design]**: HSD choice with no Apex reference.

## 1. Material check

| Material | Status |
|---|---|
| Research repo M0–M5.5 | present (`research/phase2-local/m0…m55`) |
| HSD-Unity M5.5 | present: motor `R5MotorV2`, 7 primitive classes + RF grapple + teleport, `SkillArbiter` slots, practice game, M5.5 camera / HUD / Movement Demo, 262 EditMode + 1 PlayMode tests |
| `ReApex-MovetionRefer/R5Flowstate_S21_Movement_Report_2026-10-20.md` | present (69 general items, 26 legends, 24 parameter candidates; adoption rates all null) |
| `research/S21-2026-10-21/` (candidate matrix, support-movement survey, grapple target experiment) | **not found** on this machine, in any branch of the research repo, or in HSD-Unity. Asked the M5.5 fork session; until it turns up, M6 re-derives what it needs and does not cite that material. The plan's note "a horizontal zipline's middle can be grappled" is kept as an unverified claim. |
| Fps-camera-design skill (`HSD-Unity/.claude/skills/fps-camera-design/`) | present; to be used for any camera language of new moves (method, not numbers) |

## 2. What exists vs what M6 needs

| M6 item | Already measured (R5F) | Already in Unity | Gap |
|---|---|---|---|
| A1 single lurch | λ 0.7, window 0.2 s full → 0.5 s, clamp 209.3 = 0.7 × sprint cap; back = brake; time-based (M3, 102 trials) | yes (M3 motor; reference config) | — |
| A1 several presses / lurch stack | — (M3 open Q6) | each press edge lurches in code, untested | measure stacking; Unity tests |
| A1 tap strafe (W edges while turning) | — (M3 open Q4: W press when v is not along the view) | W edge treated like any edge | measure; yaw control now available (M4b `set cl_yawspeed`) |
| A1 diagonal, cutoff 1100, walk-off anchor | — (M3 Q1, Q3, Q7) | — | diagonal now; cutoff 1100 is above the HSD 900 cap (low value); walk-off later |
| A1 lurch after wall jump / mantle boost | — (M3 §7 Q1, lurch Q8) | — | measure |
| A2 climb on one wall | climb sequence, speed line, end height, final jump-up, wall bounce vector, mantle traversal 0.59 s, exit 299 (M3, 157 climbs) | `WallBounce`, `MantleBoost` formulas + unit tests only; **no climb or mantle state in the game**; `BoxWorld` has no ledge detection | heights (M3 Q3), hang / cancel / mantle hop, low obstacles (insta-mantle), superglide vs SDK mantle boost; Unity climb / ledge / mantle state machine |
| A2 mantle boost / superglide | SDK bridge "mantle boost" window = last 133 ms (M3) — this is the **community SDK implementation**, not proven to be the official superglide | formula only | classify official vs SDK; same-frame crouch variants untested |
| A3 zipline | nothing | nothing | full: spawn, attach, ride, jump/crouch off, re-attach, super jump, grapple handoff |
| A4 slopes, ceilings, edges, normals | slide on flat only | `BoxWorld`: flat floor + axis-aligned boxes, no ceilings, no slopes | world generalization (ramps, ceilings, ledge probe, rails) behind an interface |
| B Valkyrie jets | thrust model fitted to 0.004 u/s; fuel drain never observed (M4) | `JetpackAbility`, fuel 1/s assumed | fuel, short bursts, steering, stop inertia |
| B Loba | velocity zeroed on teleport, no lock (M4 P3, 6 teleports, throw left the field) | `TeleportAbility` (Loba mode, design distance) | throw arc, early drop, destination validation, failure |
| B Ash Phase Breach | source only (server path replay, 1200 u/s, controls frozen) | `TeleportAbility` portal mode (design numbers) | presence in build, targeting, timings |
| B Alter Void Passage | nothing | nothing | presence in build, thickness, exits |
| Grapple extras | RF pull law (79 trials); detach rule unknown; range 830–840 u; refill adds a range-doubling mod (M5.5) | RF grapple, 34 u envelope release, no manual release | players / entities / deployables / ziplines / manual release |

## 3. Constraints that shape the work

- **One controller per instance**: one game session and one Unity process at a time; heavy analysis or Unity batch runs are kept off game sessions (fps rejects, learned in M4).
- **Lurch on the dedi is an SDK reimplementation** (`src/game/server/tapstrafe.cpp`), as is the jet drive and the mantle boost; client prediction is native S21. M3 found client/dedi parity for lurch (101/102 identical); M6 keeps checking parity per mechanic.
- **Protect M5.5**: new mechanics go through the existing seams (`IMovementAbility`, `CommandModifiers`, `SkillArbiter`, world interface); the default replay motor and all 263 tests must stay green; camera work follows the fps-camera-design skill.
- **No fake chains**: the M5.5 Movement Demo pattern (scripted input through the normal `Advance → Step` path, verified bit-identical to raw `SkillBody.Step`) is the template for M6-C chain checks.

## 4. Execution order

1. Source research (subagent, read-only) → `m6/SOURCE-AUDIT.md` with experiment designs for A1–A3, B and grapple extras.
2. A1 game session (no new geometry needed) → analysis.
3. A2 / A3 sessions once the source audit gives the spawn recipes (walls at several heights, ziplines).
4. Unity A4 world generalization, then A1/A2/A3 implementation, tests, build, route (one Unity subagent at a time, not overlapping game sessions).
5. M6-A report → M6-B experiments and comparison (user decides the build scope) → M6-C.
