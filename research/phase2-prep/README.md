# High Speed Doom — Movement Research Phase 1.5 (cloud preparation)

This folder is the infrastructure for the first local R5Flowstate telemetry session. Everything here was built and tested in the cloud **without the game**.

- All data under `fixtures/` and `results/synthetic_report/` is **SYNTHETIC**. It comes from a made-up model, not from Apex.
- The Phase 1 research it builds on is in `research/phase1/` (commit `252a3bd`).

## Start here (tomorrow)

1. [LOCAL-SETUP.md](LOCAL-SETUP.md): install the mod and configs, launch with Developer, T0 smoke test, troubleshooting.
2. [EXPERIMENTS.md](EXPERIMENTS.md): T0 → E0 → E1 → E2 → E4 → E5 with run numbers, input sequences, commands and P/M acceptance criteria.
3. [VALIDATION-REPORT.md](VALIDATION-REPORT.md): what is verified, unverified or blocked, the exact test commands and results, and the ordered checklist.

## Reference

| File | Contents |
|---|---|
| [TELEMETRY-SCHEMA.md](TELEMETRY-SCHEMA.md) / `TELEMETRY-SCHEMA.json` | sources, line formats, quality codes, CSV columns with provenance (observed / in-game / offline-derived) |
| [UNITY-DATA-CONTRACT.md](UNITY-DATA-CONTRACT.md) | `hsdmove-trial/2` trial format (usercmds, input edges, initial state, terrain, side-explicit parameters), axes/units, strict checks, replay and compare procedure, tolerances |
| [fixtures/synthetic/README.md](fixtures/synthetic/README.md) | what the synthetic fixtures contain and how they were generated |

## Tools (Python ≥ 3.8, standard library only)

| Tool | Purpose |
|---|---|
| `tools/hsd_tel.py` | one CLI: `report`, `smoke`, `parse`, `validate`, `events`, `hops`, `slides`, `summary`, `census`, `compare`, `fit-ground`, `fit-air`, `fit-vertical`, `plot`, `export-contract`, `check-contract`, `compare-contracts`, `synth`, `schema` |
| `tools/hsdtel/` | the library: `parse`, `derive`, `validate`, `analysis`, `contract`, `plot` (SVG; optional matplotlib PNG), `synth`, `schema` |
| `tools/hsd_collect.py` | copy the newest log sessions out of the game folder (read-only) and build the report |
| `tools/hsd_vmcheck.py` | per-VM API evidence check of the mod against a base `scripts/vscripts` tree |
| `tools/check_refs.py` | resolve every `path:line` reference and link in the research docs |
| `run_checks.py` | runs everything above that needs no game; writes `results/CHECKS.md` |
| `cfg/*.cfg` | console configs to copy into `<game>/platform/cfg/user/` |

Also updated in place (Phase 1 paths):

- `research/phase1/mod/hsd_movediag/`: the HSD.MoveDiag mod, now **v0.2**.
- `research/phase1/tools/hsd_movelog.py`: accepts MSVC NaN spellings.

## Run all cloud checks

```
python3 research/phase2-prep/run_checks.py
python3 -m unittest discover -s research/phase2-prep/tests -v
```
