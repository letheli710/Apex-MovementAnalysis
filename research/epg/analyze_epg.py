"""EPG rocket-jump analysis: hsd_session EPG_* sessions (hsd_trial.py epg_* schedules) -> per-trial and per-condition tables.

Per trial the server lines [EPG-FIRE] (zoom press = emulated shot), [EPG-DET] (detonation) and [EPG-V] (health / shield after)
are matched with the server [MOVE-TRACE] usercmd stream (velocity after each command) by the process uptime stamp that every
log line carries. The knockback is the largest single-command velocity change in the 0.3 s after the detonation.

Usage: analyze_epg.py <out_dir> <session_dir> [<session_dir> ...]
Writes trials.csv (one row per scored trial), summary.csv (per condition), trace.csv (server velocity per usercmd from 0.05 s
before to 1.0 s after each detonation, valid trials) and epg_lines.csv (the [EPG-*] lines). Raw game logs stay local.
"""
import csv
import glob
import json
import math
import os
import re
import statistics
import sys

STAMP = re.compile(r"^\[[^\]]+\] \[([\d.]+)\]")
MT = re.compile(r"\[MOVE-TRACE\] cmd=(\d+) ent=(\d+) .*?spr=(\d) duck=(\d) slide=(\d) ge=(\d) .*? o=([-\d.]+) ([-\d.]+) ([-\d.]+) "
                r"v=([-\d.]+) ([-\d.]+) ([-\d.]+)")
EPG = re.compile(r"\[(EPG-FIRE|EPG-DET|EPG-V|EPG-ERR)\] (.*)")
KV = re.compile(r"(\w+)=(\S+)")
FLOOR_Z = 294.92   # test field floor (hsd_trial.FLOOR_Z)
COND = re.compile(r"epg_(f\d+|frag)_s(\d+)_([a-z]+\d*)_p(\d+)")


def vec(s):
    return tuple(float(x) for x in s.split(","))


def load(sdir):
    man = json.load(open(os.path.join(sdir, "runner.json"), encoding="utf-8"))
    trials = {t["run"]: t for t in man["trials"]}
    mt, ev = [], []
    for f in glob.glob(os.path.join(sdir, "platform", "logs", "server", "*", "*.log")):
        for ln in open(f, encoding="utf-8", errors="replace"):
            st = STAMP.match(ln)
            if not st:
                continue
            up = float(st.group(1))
            m = MT.search(ln)
            if m:
                g = m.groups()
                mt.append(dict(up=up, cmd=int(g[0]), spr=int(g[2]), slide=int(g[4]), ground=int(g[5]),
                               o=(float(g[6]), float(g[7]), float(g[8])), v=(float(g[9]), float(g[10]), float(g[11]))))
                continue
            m = EPG.search(ln)
            if m:
                ev.append(dict(up=up, tag=m.group(1), kv=dict(KV.findall(m.group(2))), text=m.group(0), file=os.path.basename(f)))
    mt.sort(key=lambda r: (r["up"], r["cmd"]))
    ev.sort(key=lambda r: r["up"])
    return man, trials, mt, ev


def analyse(sdir):
    man, trials, mt, ev = load(sdir)
    sess = os.path.basename(sdir.rstrip("/\\"))
    rows, trace, lines = [], [], []
    for e in ev:
        lines.append(dict(session=sess, uptime=e["up"], line=e["text"]))
    for run, t in sorted(trials.items()):
        if t.get("warmup"):
            continue
        fire = next((e for e in ev if e["tag"] == "EPG-FIRE" and e["kv"].get("run") == str(run)), None)
        det = next((e for e in ev if e["tag"] == "EPG-DET" and e["kv"].get("run") == str(run)), None)
        vs = [e for e in ev if e["tag"] == "EPG-V" and e["kv"].get("run") == str(run)]
        row = dict(session=sess, run=run, schedule=t["schedule"], ok=t["ok"], fps=t["measured_fps"], why=t.get("why", ""))
        m = COND.fullmatch(t["schedule"])
        row.update(force=m.group(1), shield=int(m.group(2)), timing=m.group(3), pitch=int(m.group(4)))
        if not fire or not det:
            row["note"] = "no shot"
            rows.append(row)
            continue
        dk, fk = det["kv"], fire["kv"]
        u0 = det["up"]
        win = [r for r in mt if u0 - 0.1 <= r["up"] <= u0 + 1.5]
        for r in win:
            if t["ok"] and r["up"] >= u0 - 0.05 and r["up"] <= u0 + 1.0:
                trace.append(dict(session=sess, run=run, schedule=t["schedule"], dt=round(r["up"] - u0, 3), cmd=r["cmd"],
                                  ground=r["ground"], slide=r["slide"], oz=round(r["o"][2] - FLOOR_Z, 1),
                                  vx=round(r["v"][0], 1), vy=round(r["v"][1], 1), vz=round(r["v"][2], 1)))
        best, bi = 0.0, None
        for i in range(1, len(win)):
            if win[i]["up"] < u0 or win[i]["up"] > u0 + 0.3:
                continue
            d = [a - b for a, b in zip(win[i]["v"], win[i - 1]["v"])]
            n = math.sqrt(sum(x * x for x in d))
            if n > best:
                best, bi = n, i
        pre = win[bi - 1] if bi else min(win, key=lambda r: abs(r["up"] - u0))
        post = win[bi] if bi else pre
        dv = [a - b for a, b in zip(post["v"], pre["v"])]
        z0 = pre["o"][2]
        zmax = max(r["o"][2] for r in win if r["up"] >= u0)
        hp0 = 200 if row["force"] == "frag" else 100
        hp_after = min(int(e["kv"]["hp"]) for e in vs) if vs else None
        sh_after = min(int(e["kv"]["sh"]) for e in vs) if vs else None
        sp_pre = math.hypot(pre["v"][0], pre["v"][1])
        sp_post = math.hypot(post["v"][0], post["v"][1])
        row.update(
            fire_ground=int(fk["ground"]), fire_slide=int(fk["slide"]), flight_s=round(float(fk["dist"]) / 2000.0, 4),
            shot_dist=float(fk["dist"]), det_ground=int(dk["ground"]), dfeet=float(dk["dfeet"]), dcenter=float(dk["dcenter"]),
            dxy=float(dk["dxy"]), det_cmd_lag_s=round(post["up"] - u0, 4),
            vpre_x=pre["v"][0], vpre_y=pre["v"][1], vpre_z=pre["v"][2], vpost_x=post["v"][0], vpost_y=post["v"][1], vpost_z=post["v"][2],
            dv_x=round(dv[0], 2), dv_y=round(dv[1], 2), dv_z=round(dv[2], 2), dv=round(best, 2),
            dv_xy=round(math.hypot(dv[0], dv[1]), 2), speed_xy_pre=round(sp_pre, 2), speed_xy_post=round(sp_post, 2),
            speed_post=round(math.sqrt(sum(x * x for x in post["v"])), 2), rise=round(zmax - z0, 2),
            apex=round(zmax - FLOOR_Z, 2), z_det=round(z0 - FLOOR_Z, 2),
            dmg_health=(int(dk["hp"]) - hp_after) if hp_after is not None else None,
            dmg_shield=(int(dk["sh"]) - sh_after) if sh_after is not None else None, health_before=int(dk["hp"]), hp_full=hp0)
        rows.append(row)
    return rows, trace, lines


def write(path, rows):
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, keys)
        w.writeheader()
        w.writerows(rows)


def summarise(rows):
    out = []
    order = []
    for r in rows:
        if r["schedule"] not in order:
            order.append(r["schedule"])
    for name in order:
        g = [r for r in rows if r["schedule"] == name and r["ok"] and "dv" in r]
        s = dict(schedule=name, n_ok=len(g), n_all=len([r for r in rows if r["schedule"] == name]))
        for k in ("dv", "dv_x", "dv_z", "dv_xy", "speed_xy_pre", "speed_xy_post", "speed_post", "rise", "apex", "z_det", "dfeet", "dcenter",
                  "flight_s", "dmg_health", "dmg_shield"):
            vals = [r[k] for r in g if r.get(k) is not None]
            if vals:
                s[k + "_mean"] = round(statistics.mean(vals), 2)
                s[k + "_sd"] = round(statistics.pstdev(vals), 2)
        s["pushed"] = sum(1 for r in g if r["dv"] > 100)
        out.append(s)
    return out


def main(argv):
    out = argv[0]
    os.makedirs(out, exist_ok=True)
    rows, trace, lines = [], [], []
    for sdir in argv[1:]:
        a, b, c = analyse(sdir)
        rows += a
        trace += b
        lines += c
    write(os.path.join(out, "trials.csv"), rows)
    write(os.path.join(out, "trace.csv"), trace)
    write(os.path.join(out, "epg_lines.csv"), lines)
    summ = summarise(rows)
    write(os.path.join(out, "summary.csv"), summ)
    for s in summ:
        print("%-26s n=%d/%d pushed=%d dv=%s(%s) z=%s xy=%s apex=%s zdet=%s dfeet=%s dctr=%s dmg h/s=%s/%s vxy %s->%s" % (
            s["schedule"], s["n_ok"], s["n_all"], s["pushed"], s.get("dv_mean"), s.get("dv_sd"), s.get("dv_z_mean"), s.get("dv_xy_mean"),
            s.get("apex_mean"), s.get("z_det_mean"), s.get("dfeet_mean"), s.get("dcenter_mean"), s.get("dmg_health_mean"),
            s.get("dmg_shield_mean"), s.get("speed_xy_pre_mean"), s.get("speed_xy_post_mean")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
