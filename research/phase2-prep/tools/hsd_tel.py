#!/usr/bin/env python3
"""hsd_tel -- HSD movement telemetry command line.

Inputs are log files or folders (e.g. <game>/platform/logs/client/<GUID>/ and
.../server/<GUID>/). Rotated message.N.log files are read oldest first.

  report    <inputs...> -o OUTDIR   everything below in one go (start here)
  parse     <inputs...> -o rows.csv unified hsdtel1 table
  validate  <inputs...> [--json f]  data-quality issues; exit 2 on errors
  events    <inputs...> -o f.csv    takeoff/land/slide/jump events
  hops      <inputs...> -o f.csv    land -> takeoff pairs (HSD client frames)
  census    <inputs...> -o f.csv    E0: settings key x reader table (classvar get / mod dumps)
  summary   <inputs...> -o f.csv    per-run metrics incl. ground accel/decel fits
  compare   <inputs...> --baseline r1 [-o f.csv]
  fit-ground / fit-air / fit-vertical <inputs...>   JSON to stdout
  plot      <inputs...> -o f.svg [--y spd2d|vz] [--source HSD|MT] [--side cl|sv]
  synth     -o DIR                  write SYNTHETIC example logs (not Apex data)
  schema    [-o f.json]             column contract as JSON

Standard library only; --png also writes PNGs when matplotlib is installed.
"""
import argparse
import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hsdtel import analysis, derive as derive_mod, parse as parse_mod, plot as plot_mod, schema, synth, validate as val  # noqa: E402


def _write(path, text, lines=False):
    with open(path, "w", newline="\n") as fh:
        if lines:
            fh.writelines(text)
        else:
            fh.write(text)


def load(inputs, side=None, burst_gap=8):
    files, rows, issues = parse_mod.parse_inputs(inputs, side)
    derive_mod.derive(rows, burst_gap=burst_gap)
    return files, rows, issues


def _fmt(v):
    if isinstance(v, float):
        if not math.isfinite(v):
            return "nan" if math.isnan(v) else ("inf" if v > 0 else "-inf")
        return f"{v:.6g}"
    return "" if v is None else v


def write_csv(path, dict_rows, columns=None):
    if columns is None:
        columns = []
        for r in dict_rows:
            for k in r:
                if not k.startswith("_") and k not in columns:
                    columns.append(k)
    fh = sys.stdout if path in (None, "-") else open(path, "w", newline="")
    w = csv.writer(fh)
    w.writerow(columns)
    for r in dict_rows:
        w.writerow([_fmt(r.get(c)) for c in columns])
    if fh is not sys.stdout:
        fh.close()


def write_rows(path, rows):
    write_csv(path, rows, list(schema.COLUMNS.keys()))


def series_for_plot(rows, y="spd2d", source="HSD", side="cl"):
    out = []
    for key, srows in derive_mod.streams(rows).items():
        if key[0] != source or key[1] != side or key[2] not in ("frame", "cmd"):
            continue
        by_run = {}
        for r in srows:
            if not r.get("replay"):
                by_run.setdefault(r.get("drv_run"), []).append(r)
        for rid, rr in by_run.items():
            ts = analysis.time_series(rr, source)
            if not ts:
                continue
            t0 = ts[0][0]
            if y == "spd2d":
                pts = [(t - t0, analysis.speed_of(r)) for t, r in ts]
            else:
                pts = [(t - t0, r.get("pvz", r.get("vz"))) for t, r in ts if r.get("vz") is not None]
            label = f"{rid}" + (f" ent{key[3]}" if key[3] not in (None, 1) else "")
            out.append((label, pts))
    return out


SYNTH_TAG = " [SYNTHETIC - not Apex data]"


def synth_suffix(files):
    return SYNTH_TAG if any(parse_mod.is_synthetic(f) for f in files) else ""


def cmd_report(a):
    files, rows, issues = load(a.inputs, a.side, a.burst_gap)
    suffix = synth_suffix(files)
    issues = val.validate(rows, issues)
    os.makedirs(a.out, exist_ok=True)
    P = lambda n: os.path.join(a.out, n)  # noqa: E731
    write_rows(P("rows.csv"), rows)
    ev = analysis.events(rows)
    write_csv(P("events.csv"), ev)
    write_csv(P("hops.csv"), analysis.hops(rows))
    cen = analysis.census(rows)
    if cen:
        write_csv(P("census.csv"), cen)
    summ = analysis.run_summary(rows)
    write_csv(P("summary.csv"), summ)
    fits = {
        "ground": [g for side in ("cl", "sv") for src in ("HSD", "MT") for g in analysis.fit_ground(rows, src, side)],
        "air": {side: analysis.fit_air(analysis.air_samples(rows, side)) for side in ("cl",)},
        "vertical": analysis.fit_vertical(rows, "cl"),
    }
    _write(P("fits.json"), json.dumps(fits, indent=2, default=str))
    vs = val.summarize(issues)
    _write(P("validation.json"), json.dumps({"files": files, "summary": vs, "issues": [i.as_dict() for i in issues]},
                                            indent=2))
    plots = []
    for src in ("HSD", "MT"):
        for side in ("cl", "sv"):
            for y in ("spd2d", "vz"):
                s = series_for_plot(rows, y, src, side)
                if s:
                    name = f"{y}_{src}_{side}.svg"
                    _write(P(name), plot_mod.svg_plot(
                        s, f"{y} vs time since run start ({src}, {side}){suffix}", "s", "u/s"))
                    if a.png:
                        plot_mod.save_png(s, P(name[:-4] + ".png"), name + suffix, "s", "u/s")
                    plots.append(name)
    with open(P("report.md"), "w") as fh:
        fh.write("# hsd_tel report\n\n")
        if suffix:
            fh.write("> Input contains SYNTHETIC test data (hsdtel.synth, '# SYNTHETIC' header). Not Apex measurements.\n\n")
        fh.write(f"Inputs: {len(files)} file(s); rows: {len(rows)} "
                 f"(MT {sum(r['source'] == 'MT' for r in rows)}, HSD {sum(r['source'] == 'HSD' for r in rows)})\n\n")
        fh.write(f"Validation: {vs['errors']} error(s), {vs['warnings']} warning(s), {vs['infos']} info\n\n")
        for i in issues:
            if i.severity != "info":
                fh.write(f"- {i.severity} `{i.code}` {i.file}:{i.line_no} {i.message}\n")
        fh.write("\n## Runs\n\nA fit is marked good when its R^2 >= 0.98 over the whole phase.\n\n"
                 "| source | side | run | samples | max spd2d | accel shape (good?) | decel shape (good?) |\n"
                 "|---|---|---|---|---|---|---|\n")
        for r in summ:
            acc = f"{r['accel_best']} ({'yes' if r['accel_good'] else 'no'})" if r["accel_best"] else "-"
            dec = f"{r['decel_best']} ({'yes' if r['decel_good'] else 'no'})" if r["decel_best"] else "-"
            fh.write(f"| {r['source']} | {r['side']} | {r['drv_run']} | {r['samples']} | {_fmt(r['max_spd2d'])} | "
                     f"{acc} | {dec} |\n")
        fh.write(f"\nEvents: {len(ev)}. Plots: {', '.join(plots) or 'none'}. Fits: fits.json.\n")
    print(f"wrote {a.out}: rows={len(rows)} events={len(ev)} runs={len(summ)} "
          f"errors={vs['errors']} warnings={vs['warnings']}")
    return 2 if vs["errors"] else 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, out=True, out_required=False):
        p.add_argument("inputs", nargs="+")
        p.add_argument("--side", choices=["cl", "sv"], help="side for MT lines without a Native(C)/(S) prefix")
        p.add_argument("--burst-gap", type=int, default=8, help="command-number gap that starts a new MT burst")
        if out:
            p.add_argument("-o", "--out", required=out_required, default="-")

    for name in ("parse", "events", "hops", "summary", "census"):
        common(sub.add_parser(name))
    p = sub.add_parser("report")
    common(p, out=False)
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--png", action="store_true")
    p = sub.add_parser("validate")
    common(p, out=False)
    p.add_argument("--json")
    p.add_argument("--quiet", action="store_true")
    p = sub.add_parser("compare")
    common(p)
    p.add_argument("--baseline", required=True, help="drv_run id, e.g. r1 or b0")
    for name in ("fit-ground", "fit-air", "fit-vertical"):
        p = sub.add_parser(name)
        common(p, out=False)
        p.add_argument("--run")
        p.add_argument("--source", default="HSD", choices=["HSD", "MT"])
        p.add_argument("--fit-side", default="cl", choices=["cl", "sv"])
    p = sub.add_parser("plot")
    common(p, out_required=True)
    p.add_argument("--y", default="spd2d", choices=["spd2d", "vz"])
    p.add_argument("--source", default="HSD", choices=["HSD", "MT"])
    p.add_argument("--plot-side", default="cl", choices=["cl", "sv"])
    p = sub.add_parser("synth")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--seed", type=int, default=1)
    p = sub.add_parser("schema")
    p.add_argument("-o", "--out", default="-")
    a = ap.parse_args(argv)

    if a.cmd == "synth":
        paths, _ = synth.write_logs(a.out, a.seed)
        faulty, expected = synth.write_faulty(paths, os.path.join(a.out, "faulty"))
        console = synth.write_console_copy(paths, os.path.join(a.out, "console_copy_client.txt"))
        for p in list(paths.values()) + faulty + [console]:
            print("SYNTHETIC", p)
        print("expected issue codes in faulty/:", ",".join(sorted(expected)))
        return 0
    if a.cmd == "schema":
        text = json.dumps(schema.as_json(), indent=2)
        if a.out == "-":
            print(text)
        else:
            _write(a.out, text + "\n")
        return 0
    if a.cmd == "report":
        return cmd_report(a)

    files, rows, issues = load(a.inputs, a.side, a.burst_gap)
    if a.cmd == "parse":
        write_rows(a.out, rows)
    elif a.cmd == "validate":
        issues = val.validate(rows, issues)
        s = val.summarize(issues)
        if not a.quiet:
            for i in issues:
                print(i)
        print(f"files={len(files)} rows={len(rows)} errors={s['errors']} warnings={s['warnings']} infos={s['infos']}")
        if a.json:
            _write(a.json, json.dumps({"files": files, "summary": s, "issues": [i.as_dict() for i in issues]}, indent=2))
        return 2 if s["errors"] else 0
    elif a.cmd == "events":
        write_csv(a.out, analysis.events(rows))
    elif a.cmd == "hops":
        write_csv(a.out, analysis.hops(rows))
    elif a.cmd == "census":
        write_csv(a.out, analysis.census(rows))
    elif a.cmd == "summary":
        write_csv(a.out, analysis.run_summary(rows))
    elif a.cmd == "compare":
        write_csv(a.out, analysis.compare(analysis.run_summary(rows), a.baseline))
    elif a.cmd == "fit-ground":
        print(json.dumps(analysis.fit_ground(rows, a.source, a.fit_side, a.run), indent=2, default=str))
    elif a.cmd == "fit-air":
        print(json.dumps(analysis.fit_air(analysis.air_samples(rows, a.fit_side, a.run)), indent=2))
    elif a.cmd == "fit-vertical":
        print(json.dumps(analysis.fit_vertical(rows, a.fit_side), indent=2))
    elif a.cmd == "plot":
        s = series_for_plot(rows, a.y, a.source, a.plot_side)
        _write(a.out, plot_mod.svg_plot(s, f"{a.y} ({a.source}, {a.plot_side})", "s", "u/s"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
