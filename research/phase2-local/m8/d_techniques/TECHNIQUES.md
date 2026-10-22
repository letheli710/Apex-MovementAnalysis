# M8 track D: LS / RAS and air-direction-change techniques (desk research)

Desk research only. No game, no Unity. Date 2026-10-22. Written for M8-B item 5 (Lurch, LS/RAS, air direction change) and item 6 (Superglide, wall chains).

Evidence classes:
- **verified**: matches an HSD measurement (file and number cited).
- **community**: documented by community sources, not measured by us. Pages are living wikis and do not automatically apply to S21 (the local report says the same).
- **unverified / contradicted**: unclear, or conflicts with our data.

Local files cited (all under `research/phase2-local/`): `m6/a1_lurch/A1-LURCH.md` (A1), `m3/lurch/LURCH-MODEL.md` (M3), `m6/a2_climb/A2-CLIMB.md` (A2), `m6/M6-A-REPORT.md`, `m7/unity/M7A-UNITY.md` (M7A), and the 69-technique community report `C:\Workspace\Playground\ReApex-MovetionRefer\R5Flowstate_S21_Movement_Report_2026-10-20.md` (REPORT, entries G0xx).

Source reliability note: the wiki pages were fetched and summarised by a small model; the ProGuides, afkgaming and GameLeap pages could not be fetched (403 / redirect), so statements from them are **search-snippet level** and are marked so.

## 1. What LS and RAS mean

**LS = Lurch Strafe (most likely).** The Apex Movement Wiki has a "Lurch strafe" article titled "Lurch Strafing". It lists "Lurch strafe chain" videos and says the advanced presentation is being revamped; it never writes the abbreviation "LS" and gives no input table. https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20strafe%3ELurch%20Strafing%20article . In community use, "lurch strafe" is the umbrella for chains of lurches driven by direction keys (often without turning the camera), as opposed to **tap strafe** (forward-key scroll taps plus camera turning). No other candidate expansion found. Confidence: high.

**RAS: no source I could open defines the acronym.** What exists:
1. **"Ras strafe" is a named lurch-strafe sequence**, used as a proper name. ProGuides (snippet only) lists it first among lurch-strafe variants: A + jump, then W, D and S in very fast succession, with tap strafing, and says solid tap strafing is a prerequisite. It also lists "Yuki strafe" (W+A, jump, then S+A taps). https://www.proguides.com/guides/apex-legends/learn-these-epic-movement-mechanics-in-apex-legends/
2. The wiki's Basic Lurch article ties it to **Momentumshift**: "Sprint, Slide, let go of forward, Jump, then press Left, Backwards, Right" with the view turned 90 degrees toward the first key. The advanced version, which turns you straight backwards into a jump slide without turning the camera, is the **"OG Ras strafe"**; it "only works out of a walk", and higher speeds need advanced lurch strafes. https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3EBasic%20Lurch%20Tech%3EBasic%20Lurch%20Tech%20article
3. A paid course lists "The Ultimate RAS Strafing Guide" (player Jonei), no written steps. https://www.gameleap.com/course/apex-legends/aim-and-predator-mechanics~crs_fPKN4o7H8/the-ultimate-ras-strafing-guide~vguide_97iVQE3Hq
4. A 2021 viral clip "raf strafe" (@rafyxxx_a: mid-air left/right strafing while moving forward and hopping) was debated as config-file trickery. https://afkgaming.com/esports/news/what-is-raf-strafe-movement-in-apex-legends (snippet only). **No source links "raf" to "RAS".**
5. The local REPORT (G021, G023) already says: "Momentum Shift / early RAS", and that RAS / Pito / Yuki / Neo have no stable, unified input definition.

**Conclusion.** Treat RAS as a *name*, probably a player-derived label, not an expandable acronym. Guesses such as "Rapid / Reverse / Rotational Air Strafe" are unsourced; do not use them. Practical meaning: **a chain of different-direction key presses after a jump, each one a lurch, that rotates or reverses the velocity heading (momentum shift) with little or no camera turning.** The OG form is a 180-degree reversal out of a walk. For HSD: LS/RAS = sequences of lurches with *different* wish directions; TS = repeated *forward* lurches while the camera turns. Both are the same mechanism in our model (A1 §9). The user should say which clip/sequence they mean before a demo is built (open question 1).

## 2. The HSD mechanism these all reduce to (verified)

From A1 §9 / M3: on each airborne usercmd with a **new key bit** in {W, S, A, D}: `wish = unit(keys at this command's yaw)`, `t = time since latest jump command`, `lambda = 0.7*clamp01((0.5-t)/0.3)`, `v' = normalize((1-lambda)*vhat + lambda*wish)*|v|`, `|dv| <= 209.3` per press; no budget, no cooldown; speed kept unless clamped. Window: full to 0.2 s, fades to 0 at 0.5 s, re-anchored by every jump (ground, slide, wall-bounce [A1 §6]; in Unity also double jump, wall-run jump, zipline jump-off per M7A §3.3). AirAccelerate is separate (69 u/s wish cap at movescale 1.15), so holding a key and turning barely steers (3.1 degrees in 0.25 s [A1 §4]).

Consequence for every technique below: **one lurch changes velocity by at most 209.3 u/s (about 41 degrees of heading at 297 u/s); turning further needs several presses, all inside the window (about 0.5 s after the latest jump, strong for the first 0.2 s).**

## 3. Technique catalogue

Each entry: input / mechanism / platform / S21 status / evidence.

### 3.1 Lurch (single) and Lurch stack  [REPORT G018, G019]
- **Input:** moving, jump, then one new direction key press in the air. Wiki: 400 ms lurch window from the jump, full for 200 ms then linear decay; holding a key before the jump does not lurch; releasing does not. https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20Fundamentals%3ELurch%20Fundamentals%20Techpage
- **Stack:** repeated same-direction presses; wiki says changing the set of active keys ends the "stack" (naming only).
- **Platform:** keyboard only (digital keys); not on controller. **S21:** present (our data are R5Flowstate S21).
- **Evidence:** **verified** for the edge rule, stacking and no budget (A1 §3: three clamped presses in one jump, 627.9 u/s total; lambda 0.7000 even 16.7 ms apart). **Contradicted in detail:** community window is 400 ms; measured fade runs to **0.5 s** (M3 +-1 ms; A1 §7). The community "a stack ends when the keys change" has no counterpart: in HSD a changed key set just gives another independent lurch (A1 shift: R, B, L all lurched).

### 3.2 Tap strafe (TS), 90/180/360 variants  [G020, G024]
- **Input:** sprint, slide, release W, hold a side key, jump, then scroll-wheel-bound forward taps while turning the view the same way as the side key; "slow", synced with the turn, not a flick (wiki). https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3EBasic%20Lurch%20Tech%3EBasic%20Lurch%20Tech%20article
- **Mechanism:** each W edge is a lurch toward the current view. **Platform:** keyboard; the scroll-wheel bind is a config trick (see §5).
- **S21 history:** Respawn announced removal of tap strafing in Sept 2021, then delayed it for "unexpected side effects" (https://www.dexerto.com/apex-legends/respawn-delays-apex-legends-tap-strafing-patch-side-effects-1652385/); a later revert after backlash is only in search snippets. Sept 2024: tap strafing broke at certain angles with Pounce; the wiki suspects a lowered lurch speed cap (Lurch Fundamentals page); the local REPORT warns not to back-apply that to S21. All **community, partly second-hand**. Our R5 build behaves as in §2.
- **Evidence:** **verified.** A1 §4: 15 W edges 2 commands apart; 360 deg/s turn gives velocity turn -81.02 deg (view -88.56 deg) at constant speed (Unity reproduces -80.99 deg, M6-A-REPORT §3); 180 deg/s gives -40.52 deg. **Untested:** turn rates >= 720 deg/s (predicted 162 deg in 0.267 s; the clamp binds near 2900 deg/s).

### 3.3 Momentum Shift  [G021 "early RAS"]
- **Input:** sprint, slide, release W, jump, then Left, Back, Right (or mirrored) while turning the view 90 deg toward the first key. Wiki: redirects momentum 90 deg backwards (same page as 3.2).
- **Platform:** keyboard.
- **Evidence:** **verified as a mechanism**, not as a named sequence. A1 "shift" (R, B, L presses 0.067 s apart): speed 297 -> 78 u/s, |dv| 209.3 on each, residual 0.003 u/s. Opposite presses are hard brakes (clamp), so a speed-keeping shift needs presses spread so each heading change is below the clamp (<= about 41 deg per press at 297 u/s). That is **model-predicted, not recorded**.

### 3.4 Lurch Strafe (LS) chains, OG Ras, Ras, Yuki, Pito, Neo  [G023]
- **Input (community):**
  - OG Ras: out of a *walk*, jump, key sequence ending with the velocity pointing backwards, no camera turn, slide on landing (wiki Momentumshift note).
  - Ras (ProGuides, snippet): A + jump, then W, D, S in fast succession with tap strafing.
  - Yuki: W+A, jump, then S+A taps.
  - Pito, Neo: **no usable definition found.** "Neo strafe" appears only in passing in a Steam thread (commenters call an Octane "neo strafing"; others claim config edits; unverified). https://steamcommunity.com/app/1172470/discussions/0/4203615689067431024
- **Mechanism:** chain of lurches with changing wish directions; the "no camera turn" versions rely on side / diagonal / back wish directions alone.
- **Evidence:** names and exact orders = **community, unstable** (REPORT line 130). The heading changes = **verified as a mechanism** (A1 diag W+D 45 deg unit wish; back = pure brake). Whether a human-feasible sequence reaches a 180 deg reversal *keeping* speed is **unverified**: with lambda 0.7 and the clamp it takes about 4-5 presses of <= about 41 deg each, all within 0.5 s, i.e. roughly one press per 50-100 ms.

### 3.5 Lurchless air strafe  [G022]
- **Input:** hold the direction key *before* the jump, never re-press in the air; steer with the mouse.
- **Evidence:** half **verified**: no edge, no lurch (A1 turn_hold_w: 3.1 deg in 0.25 s, plain AirAccelerate with the 69 u/s cap). Its use as "pure air strafe" is community.

### 3.6 Plain air strafe  [G017]
- Side key plus slow camera turn. AirAccelerate with wish cap 60*movescale. **Verified** (M2/A1, <= 0.008 u/s per command). Weak in R5 and so in HSD.

### 3.7 Held + press diagonals, "null lurch"
- Wiki: pressing a direction while another is held gives the combined (diagonal) direction; opposing keys held then press one "can produce a null lurch". **Partly verified:** A1 diag_fr / diag_br press both keys on the same command (unit wish, error 0.006 / 0.002 u/s). *Held A then new W* is not a separate test; the model uses all keys down on the command and predicts the diagonal. *Opposing keys held:* wish = 0, no lurch (A1 gate `|wish|>0`). Agrees with the wiki, but **unverified** for these two cases.

### 3.8 Wall bounce, bounce + lurch/TS  [G026-G031]
- **Input:** slide jump into a wall, release forward, jump during the climb contact; fatigue / low variants change contact height; Wall Skip keeps forward.
- **Platform:** both; undead-legend exception in REPORT.
- **Evidence:** **verified.** The bounce jump comes 0.434-0.450 s after the ground jump and **restarts the lurch window**: t from the bounce errs 0.000-0.002 u/s, t from the ground jump errs 191-196 u/s (A1 §6). Unity: bounce within 0.1 s of a contact; demo `m7_bounce_djump` (M7A §5). "No-Ma bounce", "Mini bounce", "Crouch Kick": **community only**.

### 3.9 Superglide (SG), lateral/backward SG, SG + TS, Glide Bounce  [G042-G046]
- **Input:** sprint, mantle; in the last 150 ms of the mantle press Jump, then Crouch about one frame later. Lateral: release forward during the pull (it still completes) and hold a side key. Backward: release forward, look up > 25 deg, hold back (or press back exactly one frame earlier). Needs sprint (walk: window about 10 ms). Polling / FPS sensitive. https://apexmovement.tech/wiki/tech/General%20Tech%3EMantle%20Tech%3ESuperglide%3ESuperglide%20article
- **Evidence:** basic SG **verified**: native exit speed **460.000** (n = 13, sd 0) with crouch on the exit command, equal to the slide-start cap min(v+150*msc, 460); control: crouch + jump two commands later leaves at 299; SDK FSM version gives 388.7 / vz 367.4 (A2 §4). Measured only at wall height 232 sprint. The walk claim is unchecked (A2 open item: walking mantle predicts 372). **Lateral / backward SG, SG -> TS, Glide Bounce: community only.** A2 round 2b shows a mantle exit along the input direction and 51 u/s lateral drift at the climb end, but speed after a lateral SG is unmeasured. The "last 150 ms" window is **unverified** against our mantle-cancel bracket (completed at >= 0.685 of the traversal, aborted at <= 0.395; A2 §3), which is a different quantity.

### 3.10 Bunny hop / slide hop  [G011, G012]
- **Input:** jump as soon as grounded, repeat; slide hop holds crouch. Community: shortens friction time, not an automatic gain. Local: M2 measured jump-frame friction = 0 ("bunnyhop keeps speed"), anti-multihop rule (landing within 0.033 s of a jump: frac 0.3) (M8-PLAN leader audit, item 4). **Verified** in mechanism; no new research.

### 3.11 Zip Super Jump / Mantle Jump  [G051, G047]
- Community: mount, release, jump, jump again quickly; Mantle Jump cancels a mantle to regain the condition. **Verified (zipline super jump):** M6-A-REPORT §2, 20/20 (mount from the ground, release jump, jump again). A2 §4 reports a jump on frame N after the climb jump (no crouch) as a *mantle jump*: v_h 299, V 289.8 (N = 204, 208: 5/5). That is the climb-cancel jump, not the community zip + mantle chain; G051's chain is **community only**.

### 3.12 Ghost strafe, Faide, Skip jump (ground)  [G014-G016]
- Ground-fake techniques; out of scope for air direction change. **Community.** No HSD action.

## 4. Mapping: technique to HSD mechanism, demo, success / failure

"Natural" means produced by existing rules with no new code. The lurch window anchors on the latest jump command (ground jump, slide jump, wall bounce, double jump, wall-run jump, zipline jump-off; A1, M7A).

| Technique | HSD mechanism | Real-input demo needs | Success condition | Failure variant |
|---|---|---|---|---|
| Single lurch / stack | Lurch per air press edge (A1 §9) | Jump, then 1-3 side taps 50 ms apart | Heading change per press equals the model; first press at 297 u/s, theta 89 deg clamped at 209.3 | Tap after 0.5 s: none; key held before jump: none |
| Tap strafe 90/180/360 | W edges 2 commands apart + view turn | Slide jump, hold side key, 15 W taps in 0.25 s at 360 deg/s, from a tap scheduler (no scroll wheel) | Velocity turn about -81 deg (+-2), speed 297 +-0.1 | Turn only: 0 deg; W held without edges: about 3 deg |
| Momentum shift | R, B, L presses (distinct wish) | Jump, three taps 50-70 ms apart, 90 deg turn | Heading >= 90 deg from entry; speed threshold taken from a model run first | Taps after 0.5 s: no change |
| LS / OG-Ras 180 deg reversal | Chain of lurches, changing keys; no new code | Walk jump (200 u/s), 4-5 presses within about 0.4 s, camera fixed | Heading >= 150 deg from entry with >= 60 % of entry speed (a prediction, not a measured target) | Same from sprint speed: clamp binds, speed falls; or too late: window closed |
| Lurchless air strafe | AirAccelerate only | Hold side key before jump, slow mouse turn | No lurch, small turn | Press a side key in the air: lurch fires |
| Wall bounce then lurch / TS | Bounce restarts window (verified) | Slide jump to wall, release W, jump in contact, tap 0.1-0.3 s after the bounce | Full-strength lurch even > 0.5 s after the first jump | Tap 0.5 s after the bounce: nothing |
| Superglide (basic) | Native mantle exit + crouch (460) or FSM (388.7) | Sprint, jump to ledge, jump then crouch next command at traversal end | Exit speed about 460 (native) | Crouch two commands later: 299 (control) |
| Lateral / backward SG | Side input during mantle (exit along input, A2) | SG demo with a side key held through the exit | Exit direction along input; speed logged | Not claimed; log only |
| SG then TS / lurch | The SG jump is a jump command, so it anchors the window | Basic SG, taps 0.1 s after | Lurch at full strength | Taps > 0.5 s later: none |
| Wall-run -> jump -> wall-run / TS | M7A wall-run (HSD design) | `m7_wallrun_tapstrafe` (exists) | per M7A §5 | per M7A §5 |
| Double jump then TS | `DoubleJumpAbility` counts as a jump (switch) | `m7_djump_lurch` (exists) | 48.3 deg at +0.10 s | +0.6 s |
| Bunny / slide hop | Jump-frame friction 0, anti-multihop 0.033 s | 10-hop loop at 297 and 350 u/s | Speed kept about >= 0.99 per hop | Hop within 0.033 s of landing: friction fraction 0.3 |
| Zipline super jump | M6-A zipline (measured) | existing M6-A demos | 20/20 pattern | none |

Mantle Jump (zip chain), Glide Bounce, Glide Boost, No-Ma bounce, insta-glide: reachable only if the events they chain (climb cancel, mantle-exit jump, bounce on the exit contact) occur. `ClimbAbility` already has the cancel window and bounce. They need an exploratory demo, not new code.

**New mechanisms?** None justified now.
- **Scroll-wheel / fast tap input:** an *input-layer* concern, not movement. Edges must reach the sim as separate commands (A1 §10 item 2). A keyboard player cannot tap W at 60 Hz, so demos use a scheduler. A built-in "tap aid" for humans would be an input convenience with fairness implications (HSD has fair inputs only). Recommend deferring and asking the user (open question 3).
- **Lurch speed cutoff** (community about 1150-1300 hu/s; SDK 1100 [src], A1 §8): untested in R5; matters only at extreme speed. Not needed now.
- **Window length:** keep the measured 0.5 s; do not shorten to the community 0.4 s.

## 5. Platform and config notes

- **Controller:** lurch is hard-coded to digital keys; TS and momentum shift "do not natively work on controller" (wiki). HSD has one fair input class; none of the techniques here depends on aim assist. REPORT marks TS / Lurch as PC keyboard + mouse, Superglide as FPS / hardware sensitive.
- **Bind tricks:** scroll-wheel forward / jump and scripts are discussed in community threads as artificial or restricted in competitive play (Steam thread above; afkgaming snippet). HSD: none.
- **Frame rate:** lurch is time-based (60 / 120 / 144 fps equal, M3). Superglide is ordering-based (jump, then crouch on a later command); A2 §4 only covers 120 fps.

## 6. Open questions

1. Which exact LS / RAS sequence (clip name) does the user mean? No source I could open defines the acronym.
2. Can a human-feasible sequence reverse a sprinting player's heading by 180 deg without losing most speed? The model's limits are the 209.3 clamp and the 0.5 s window; no R5 recording exists.
3. Should HSD give a "tap-rate" aid (scroll-wheel substitute)? Input design / fairness, not movement.
4. Superglide vs wall height, entry speed, walk vs sprint, lateral exit: only h232 sprint is measured.
5. Does the clamp scale with entry speed above the sprint cap (slide jump 350)? Never clamped at 350 in A1.
6. Does the lurch fire without a jump (walk-off a ledge, coyote)? M3 Q7, untested.
7. Lurch speed cutoff (1100 SDK vs 1150-1300 community) and mantle-boost suppression: not exercised.

## 7. Cheap R5 measurements that would settle these

1. **Held + press, opposing keys:** hold A, jump, press W; hold A+D, press D (120 fps, about 6 trials each). Confirms diagonal and "null lurch".
2. **Reverse chain:** walk (199.5) and sprint (297) jumps, then B-L-F-style press chains at 33 / 50 / 67 ms spacing, camera fixed; read final heading and speed. Settles LS / OG-Ras reversal (about 6 conditions).
3. **Fast-turn tap strafe:** W taps at 720 and 1440 deg/s: checks A1 §4's predicted rows and clamp onset.
4. **Lurch after a walk-off (no jump):** one condition; answers M3 Q7 and the anchor question.
5. **Superglide grid:** heights {120, 180, 232} (where SG is possible) x entry {walk, sprint} x crouch offset {0, 1, 2 commands}, plus a lateral exit (hold D through the pull). Read exit speed and direction.
6. **Slide-jump (350) clamped lurch:** a 90 deg press right after the jump; clamp 209.3 (0.7 x 299) or scaled (0.7 x 350).
7. **Lurch speed cutoff:** a pad / grapple launch above 1100 u/s with one press (SDK says suppressed).

## 8. Sources

- Apex Movement Wiki: Lurch Fundamentals https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20Fundamentals%3ELurch%20Fundamentals%20Techpage ; Basic Lurch (Tap Strafe, Momentumshift, OG Ras) https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3EBasic%20Lurch%20Tech%3EBasic%20Lurch%20Tech%20article ; Lurch Strafing https://apexmovement.tech/wiki/tech/General%20Tech%3ELurch%20Tech%3ELurch%20strafe%3ELurch%20Strafing%20article ; Superglide https://apexmovement.tech/wiki/tech/General%20Tech%3EMantle%20Tech%3ESuperglide%3ESuperglide%20article
- ProGuides (snippet only) https://www.proguides.com/guides/apex-legends/learn-these-epic-movement-mechanics-in-apex-legends/
- Dexerto, tap strafe patch delay https://www.dexerto.com/apex-legends/respawn-delays-apex-legends-tap-strafing-patch-side-effects-1652385/
- afkgaming, raf strafe (snippet only) https://afkgaming.com/esports/news/what-is-raf-strafe-movement-in-apex-legends
- GameLeap RAS guide (title only; 403) https://www.gameleap.com/course/apex-legends/aim-and-predator-mechanics~crs_fPKN4o7H8/the-ultimate-ras-strafing-guide~vguide_97iVQE3Hq
- Steam discussion (neo strafing, scripts) https://steamcommunity.com/app/1172470/discussions/0/4203615689067431024
- Local: A1-LURCH.md, LURCH-MODEL.md, A2-CLIMB.md, M6-A-REPORT.md, M7A-UNITY.md, R5Flowstate_S21_Movement_Report_2026-10-20.md (G014-G024, G026-G031, G042-G047, G051).
