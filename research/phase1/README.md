# High Speed Doom — Apex Movement Research, Phase 1

This is a static source analysis. No game client was downloaded, no SDK was compiled, and nothing was run against a live or online service.

## Sources analysed (shallow clones, read-only)

| Repository | Branch | Commit | Commit date |
|---|---|---|---|
| `R5Flowstate/s21-r5sdk` | `s21-unify` | `10077bbf020292fa0bab69d9a9a05fef125d6ba5` | 2026-10-08 |
| `R5Flowstate/s21-platform` | default | `9b21dc94a2e1be6f866beb0750f0644c599eafbf` | 2026-10-08 |
| `R5Flowstate/launcher` | default | `00fd92394b4248319d52030df670249245b163a2` | 2026-10-08 |

Path conventions in these documents:

- `s21-r5sdk/src/...:N` and `s21-platform/...:N` are file and line references within the commits above.
- The online documentation at `r5flowstate.org/tools/*` could not be fetched: the cloud VM's network policy refused the tunnel (HTTP 403). Every Modding rule here is therefore taken from the loader source code (`s21-r5sdk/src/pluginsystem/modsystem.cpp`), not from the web documentation.

## Evidence levels (used in every document)

| Tag | Meaning |
|---|---|
| **[A 源码证实]** | The behaviour is implemented in this open-source code (SDK C++ or Squirrel scripts); you can read the implementation. |
| **[B 逆向注释]** | Comments, constants, offsets or signature names in the SDK describe the **closed-source game binaries** (`r5apex.exe` S21 / `r5apex_ds.exe` S3). This is the R5Flowstate authors' reverse-engineering result, not Respawn source code. It can only be checked against the binaries. |
| **[C 合理推断]** | An inference from A/B evidence plus the Source engine lineage. |
| **[D 未验证假设]** | Needs an experiment or binary analysis to confirm. |

The central premise: the **real Apex movement algorithms** (CGameMovement's acceleration, friction, air control, lurch and so on) live inside closed-source binaries and **do not appear in any of these repositories**. The open-source part consists of hooks and fixes, parameter interfaces, diagnostic tools, and S3/S21 compatibility code.

## Deliverables

| File | Contents |
|---|---|
| [Architecture.md](Architecture.md) | Repository and process structure, the movement call chain, data structures, client/server responsibilities |
| [Movement-Analysis.md](Movement-Analysis.md) | Each mechanic: functions, parameters, state transitions, real vs. compatibility-layer classification, source paths |
| [Modding-Capabilities.md](Modding-Capabilities.md) | What can be read, what can be changed, entry points and permission gates |
| [Experiment-Plan.md](Experiment-Plan.md) | Local Windows experiment methods, recorded data, acceptance criteria |
| [Findings-and-Gaps.md](Findings-and-Gaps.md) | Confirmed findings, contradictions, gaps, Phase 2 recommendations, the three most valuable experiments |
| [mod/hsd_movediag/](mod/hsd_movediag/) | Movement Diagnostic Mod prototype (observe-only Squirrel mod; **not run**) |
| [tools/hsd_movelog.py](tools/hsd_movelog.py) | Log → CSV parser (`[MOVE-TRACE]` and `[HSD-MD]`); `selftest` passes |
| [tools/hsd_modlint.py](tools/hsd_modlint.py) | Static checker that reproduces the loader rules; the prototype mod reports 0 errors, and a deliberately broken copy reports 6 errors |

## Reproduction

```bash
git clone --depth 1 -b s21-unify https://github.com/R5Flowstate/s21-r5sdk.git
git clone --depth 1 https://github.com/R5Flowstate/s21-platform.git
python3 research/phase1/tools/hsd_movelog.py selftest
python3 research/phase1/tools/hsd_modlint.py research/phase1/mod/hsd_movediag --base s21-platform/scripts/vscripts
```
