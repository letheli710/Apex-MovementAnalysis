#!/usr/bin/env python3
"""Fills the {{name}} tables of the report volumes from the measurement tables and the S21 weapon files, so the numbers are never retyped.
  py -3 -I gen_report_tables.py <gun-measure dir> <s21 scripts/weapons dir>
Reads report/src/*.md, writes report/*.md."""
import collections, csv, glob, os, re, statistics as st, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guns import GUNS

NAMES = {"r301": "R-301", "r99": "R-99", "car": "C.A.R.", "flatline": "Flatline", "spitfire": "Spitfire", "alternator": "Alternator", "re45": "RE-45", "volt": "Volt", "p2020": "P2020", "hemlok": "Hemlok", "prowler": "Prowler",
         "nemesis": "Nemesis", "ehemlok": "Hemlok Elite", "eva8": "EVA-8", "mastiff": "Mastiff", "peacekeeper": "Peacekeeper", "mozambique": "Mozambique", "tripletake": "Triple Take", "kraber": "Kraber", "longbow": "Longbow",
         "sentinel": "Sentinel", "g7": "G7", "wingman": "Wingman", "chargerifle": "Charge Rifle", "havoc": "Havoc", "devotion": "Devotion", "rampage": "Rampage", "lstar": "L-STAR", "r3030": "30-30", "bocek": "Bocek", "sheila": "Sheila"}
ORDER = list(GUNS)
ID_TO = {v: k for k, v in GUNS.items()}
ID_TO["mobile_hmg"] = "sheila"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows: out.append("| " + " | ".join("" if x is None else str(x) for x in r) + " |")
    return "\n".join(out)


def num(x, d=2):
    try: v = float(x)
    except (TypeError, ValueError): return ""
    if v != v: return ""
    s = f"{v:.{d}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def tsv(path):
    return list(csv.DictReader((l for l in open(path, encoding="utf-8") if not l.startswith("#")), delimiter="\t"))


def top_fields(path):
    """Fields at the top level of a weapon file: one tab in. Mods sit deeper."""
    out = {}
    for l in open(path, encoding="utf-8", errors="replace"):
        g = re.match(r'^\t"([^"]+)"\s+"([^"]*)"', l)
        if g and g[1] not in out: out[g[1]] = g[2]
    return out


def main():
    gm, wdir = sys.argv[1:3]
    data = os.path.join(gm, "report", "data")
    T = {}
    files = {k: os.path.join(wdir, f"mp_weapon_{v}.txt") for k, v in GUNS.items()}
    files["sheila"] = os.path.join(wdir, "mp_weapon_mobile_hmg.txt")
    F = {k: top_fields(p) for k, p in files.items() if os.path.exists(p)}
    guns = [g for g in ORDER if g in F and g != "vantage"]
    N = lambda g: NAMES.get(g, g)
    vars_ = {r["gun"]: r for r in tsv(os.path.join(gm, "GUN-VARS.tsv"))}

    # ---------------------------------------------------------------- reload
    summ = tsv(os.path.join(gm, "C-RELOAD-SUMMARY.tsv"))
    rows = []
    by = collections.defaultdict(dict)
    for r in summ: by[r["gun"]][r["kind"]] = r
    for g in ORDER:
        if g in ("mastiff", "r3030"): continue      # shell guns: the volume's own table
        for k, label in (("tac", "战术"), ("emp", "空仓")):
            r = by.get(g, {}).get(k)
            if not r or not r["flag"]: continue
            state, rise, flag = float(r["state"]), float(r["rise"]), float(r["flag"])
            rows.append([N(g), label, num(r["field"]), num(state), num(rise), f"{rise / state * 100:.0f} %", num(flag), f"{flag / state * 100:.0f} %", num(state - flag), r["ok"]])
    T["reload_all"] = table(["枪", "类型", "字段（s）", "动画（s）", "加弹（s）", "加弹占比", "解锁（s）", "解锁占比", "解锁后还剩（s）", "有效次数"], rows)
    rows = []
    for key in by:
        if "+" not in key: continue
        g, mod = key.split("+")
        if g in ("mastiff", "r3030"): continue      # their base rows mix reloads of different lengths
        for k, label in (("tac", "战术"), ("emp", "空仓")):
            r, b = by[key].get(k), by.get(g, {}).get(k)
            if not r or not r["flag"] or not b or not b["flag"]: continue
            rows.append([N(g), f"`{mod}`", label, num(b["state"]), num(r["state"]), f"×{float(r['state']) / float(b['state']):.3f}", num(r["rise"]), num(r["flag"]), r["clip_end"]])
    T["reload_mods"] = table(["枪", "配件", "类型", "无配件动画", "有配件动画", "比例", "加弹", "解锁", "换完弹匣"], rows)
    rows = []
    for r in tsv(os.path.join(data, "R-RELOAD-SPEED.tsv")):
        if "+" in r["gun"]: continue
        rows.append([N(r["gun"]), "战术" if r["kind"] == "tac" else "空仓", num(r["unlock"]), num(r["reach"], 1), num(r["reach_at"]), num(r["peak_speed"], 0), num(r["mean_speed"], 0)])
    T["reload_speed"] = table(["枪", "类型", "到解锁（s）", "枪口最远（u）", "最远的时刻（s）", "最快（u/s）", "平均（u/s）"], rows)
    curve = [r for r in tsv(os.path.join(gm, "C-RELOAD-CURVE.tsv"))]
    def path(g, k):
        return table(["到解锁的进度", "前（u）", "右（u）", "上（u）"], [[f"{float(r['frac']) * 100:.0f} %", num(r["dF"]), num(r["dR"]), num(r["dU"])] for r in curve if r["gun"] == g and r["kind"] == k and abs(float(r["frac"]) * 10 - round(float(r["frac"]) * 10)) < 1e-6])
    T["path_r301_tac"], T["path_r301_emp"] = path("r301", "tac"), path("r301", "emp")

    # ---------------------------------------------------------------- times
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g), f.get("holster_time"), f.get("deploy_time"), f.get("deployfirst_time"), f.get("raise_time"), f.get("lower_time"), f.get("reload_time"), f.get("reloadempty_time")])
    T["times_all"] = table(["枪", "收枪", "掏枪", "第一次掏枪", "抬枪", "放下", "战术换弹", "空仓换弹"], [[r[0]] + [num(x, 3) for x in r[1:]] for r in rows])
    sw = tsv(os.path.join(data, "R-SWAP-SUMMARY.tsv"))
    agg = collections.defaultdict(list)
    for r in sw:
        agg["holster", r["gun_from"]].append(r)
        agg["draw", r["gun_to"]].append(r)
    rows = []
    for (ph, g), rs in sorted(agg.items(), key=lambda x: (x[0][1], x[0][0] != "holster")):
        if ph == "holster":
            rows.append([N(ID_TO.get(g, g)), "收枪", num(rs[0]["holster"], 3), num(st.mean(float(r["holster_reach"]) for r in rs), 1), num(st.mean(float(r["holster_peak_speed"]) for r in rs), 0), f"{st.mean(float(r['holster_peak_at']) for r in rs) * 100:.0f} %", len(rs)])
        else:
            rows.append([N(ID_TO.get(g, g)), "掏枪", num(rs[0]["deploy"], 3), num(st.mean(float(r["draw_reach"]) for r in rs), 1), num(st.mean(float(r["draw_peak_speed"]) for r in rs), 0), f"{st.mean(float(r['draw_peak_at']) for r in rs) * 100:.0f} %", len(rs)])
    T["swap_speed"] = table(["枪", "动作", "时长（s）", "枪口走多远（u）", "最快（u/s）", "最快在第几成", "次数"], rows)
    sc = tsv(os.path.join(data, "R-SWAP-CURVE.tsv"))
    def swap_shape(g, ph):
        seen = collections.defaultdict(list)
        for r in sc:
            if r["gun"] == g and r["phase"] == ph: seen[float(r["frac"])].append(float(r["dist"]))
        return seen
    rows = []
    for g in ("rspn101", "wingman", "semipistol", "lmg", "sniper", "r97", "shotgun"):
        for ph, label in (("holster", "收枪"), ("draw", "掏枪")):
            s = swap_shape(g, ph)
            if s: rows.append([N(ID_TO.get(g, g)), label] + [num(st.mean(s[k / 10]), 1) if k / 10 in s else "" for k in range(0, 11)])
    T["swap_shape"] = table(["枪", "动作"] + [f"{k * 10}%" for k in range(0, 11)], rows)
    r2 = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in tsv(os.path.join(gm, "C-RAISE2.tsv")):
        g = re.match(r"ra_(\w+?)_(\w+)_\d", r["tag"])
        if g and r["latency"]: r2[g[1]][g[2]].append(r)
    rows = []
    for g, kinds in r2.items():
        c = []
        for k in ("sprint", "slide"):
            rs = kinds.get(k, [])
            c.append(num(st.mean(float(x["latency"]) for x in rs), 3) if rs else "")
            c.append(num(st.mean(float(x["speed_at_key"]) for x in rs), 0) if rs else "")
            c.append(num(st.mean(float(x["speed_first_kick"]) for x in rs), 0) if rs else "")
        rows.append([N(g)] + c + [num(F[g].get("raise_time"), 3) if g in F else ""])
    T["raise"] = table(["枪", "冲刺到第一发（s）", "按键时速度", "第一发时速度", "滑铲到第一发（s）", "按键时速度", "第一发时速度", "字段 `raise_time`"], rows)

    # ---------------------------------------------------------------- ADS
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g), num(f.get("zoom_time_in"), 3), num(f.get("zoom_time_out"), 3), num(f.get("zoom_fov"), 2), num(float(f["zoom_fov"]) * 1.27217, 2) if f.get("zoom_fov") else "", num(f.get("ads_move_speed_scale"), 2), f.get("ads_fov_zoomfrac_start", ""), f.get("ads_fov_zoomfrac_end", "")])
    T["ads_all"] = table(["枪", "开镜（s）", "关镜（s）", "`zoom_fov`", "实际 FOV（算）", "开镜移速倍率", "FOV 窗口起", "FOV 窗口止"], rows)
    rows = []
    label = {"r301": "R-301", "spit": "Spitfire", "wing": "Wingman"}
    for r in tsv(os.path.join(data, "R-ADS-SPEED.tsv")):
        rows.append([label.get(r["gun"], r["gun"]), "开镜" if r["phase"] == "in" else "关镜", num(r["zoom_time"], 3), num(1 / float(r["zoom_time"]), 2), num(r["peak_speed"], 0), num(r["peak_at_zf"], 2), num(r["peak_accel"], 0)])
    T["ads_speed"] = table(["枪", "方向", "总时长（s）", "`zf` 速度（/s，恒定）", "枪最快（u/s）", "最快时的 `zf`", "枪最大加速度（u/s²，约）"], rows)
    rows = []
    for name, fov0, fov1, g in (("R-301", 89, 69.97, "rspn101"), ("Wingman", 89, 76.33, "wingman"), ("Spitfire", 89, 69.97, "lmg")):
        t = float(F[ID_TO[g]]["zoom_time_in"])
        d = fov1 - fov0
        rows.append([name, t, num(fov1, 2), num(abs(d) / t, 1), num(1.5 * abs(d) / t, 1), num(6 * abs(d) / t / t, 0)])
    T["fov_speed"] = table(["枪", "开镜（s）", "到位 FOV", "FOV 平均速度（°/s）", "FOV 最快（°/s，`zf` = 0.5）", "FOV 最大加速度（°/s²，两端）"], rows)

    # ---------------------------------------------------------------- recoil
    fit = collections.defaultdict(dict)
    for r in tsv(os.path.join(gm, "..", "recoil-view", "FIT-TABLE.tsv")): fit[r["weapon"]][r["mode"]] = r
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g), f.get("viewkick_pattern", "无"), num(f.get("viewkick_pitch_hardScale"), 3), num(f.get("viewkick_pitch_softScale"), 3), num(f.get("viewkick_yaw_hardScale"), 3), num(f.get("viewkick_yaw_softScale"), 3), num(f.get("viewkick_pitch_base", 1), 2), num(f.get("viewkick_pitch_random", 1), 2), num(f.get("viewkick_yaw_random", 1), 2), num(f.get("viewkick_hipfire_weaponFraction"), 2), num(f.get("viewkick_ads_weaponFraction"), 2), num(f.get("viewkick_air_scale_ads", 1), 2), num(f.get("viewkick_duck_scale", 1), 2), num(f.get("viewkick_move_scale", 1), 2)])
    T["recoil_fields"] = table(["枪", "图案", "俯仰 hard", "俯仰 soft", "偏航 hard", "偏航 soft", "俯仰 base", "俯仰 random", "偏航 random", "腰射 fraction", "开镜 fraction", "空中开镜 ×", "蹲 ×", "移动 ×"], rows)
    rows = []
    for g in guns:
        w = GUNS.get(g, "")
        if w not in fit: continue
        hip, ads = fit[w].get("hip"), fit[w].get("ads")
        if not hip or not ads: continue
        rows.append([N(g), f"{hip['kC']} / {hip['dC']}", f"{hip['kH']} / {hip['dH']}", f"{ads['kC']} / {ads['dC']}", f"{ads['kH']} / {ads['dH']}", num(hip["hold"], 3), num(hip["fade"], 3), num(hip["t50"]), num(ads["t50"]), num(hip["scaleDelay"], 3), num(hip["scaleRate"], 0)])
    T["springs"] = table(["枪", "腰射冷 k / d", "腰射热 k / d", "开镜冷 k / d", "开镜热 k / d", "热度保持（s）", "热度消退（s）", "腰射回落 50 %（s，算）", "开镜回落 50 %（s，算）", "图案等待（s）", "图案倒数（/s）"], rows)
    pat = {}
    cur = None
    for l in open(os.path.join(wdir, "viewkick_patterns.txt"), encoding="utf-8", errors="replace"):
        g = re.match(r'^\s*"([^"]+)"\s*$', l)
        if g: cur = g[1]; pat[cur] = dict(rows=[], loop=None); continue
        g = re.match(r'^\s*"bullet_\d+"\s+"([^"]+)"', l)
        if g and cur: pat[cur]["rows"].append([float(x) for x in g[1].split()])
        g = re.match(r'^\s*"loop_offset"\s+"(-?\d+)"', l)
        if g and cur: pat[cur]["loop"] = int(g[1])
    rows = []
    p, c_y, c_p = pat.get("rspn101_2", {"rows": []}), 0, 0
    for i, r in enumerate(p["rows"][:28]):
        c_y += r[0]; c_p += r[1]
        rows.append([i + 1, num(r[0]), num(r[1]), num(r[2]), num(r[3]), num(c_y), num(c_p)])
    T["pattern_r301"] = table(["行", "偏航（负 = 右）", "俯仰（负 = 上）", "偏航随机", "俯仰随机", "累计偏航", "累计俯仰"], rows)
    rows = []
    for g in guns:
        name = F[g].get("viewkick_pattern")
        if not name or name not in pat or not pat[name]["rows"]: continue
        rs = pat[name]["rows"]
        rows.append([N(g), name, len(rs), pat[name]["loop"], num(sum(r[1] for r in rs[:10])), num(sum(r[0] for r in rs[:10])), num(sum(r[1] for r in rs)), num(sum(r[0] for r in rs))])
    T["patterns"] = table(["枪", "图案", "行数", "`loop_offset`", "前 10 行累计俯仰", "前 10 行累计偏航", "整表累计俯仰", "整表累计偏航"], rows)
    jolt = collections.defaultdict(dict)
    for r in tsv(os.path.join(gm, "D-JOLT.tsv")): jolt[r["gun"]][r["mode"]] = r
    rows = []
    for g, m in jolt.items():
        a, h = m.get("ads"), m.get("hip")
        if not a: continue
        rolls = [float(x) for x in a["rolls"].split(",") if x] if a.get("rolls") else []
        rows.append([N(g), num(h["vmF"], 3) if h else "", num(a["vmF"], 3), num(a["vmR"], 3), num(a["vmU"], 3), num(a["vmaP"], 3), num(a["vmaR"], 3), num(a["roll_first"], 2), f"{min(rolls):.2f} 到 {max(rolls):.2f}" if rolls else ""])
    T["jolt"] = table(["枪", "腰射 前后（u）", "开镜 前后（u）", "开镜 左右（u）", "开镜 上下（u）", "开镜 俯仰（°）", "开镜 横滚（°）", "第一发 punch 横滚（°）", "每发 punch 横滚范围（°）"], rows)
    # ---------------------------------------------------------------- spread
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g)] + [num(f.get(k), 2) for k in ("spread_stand_hip", "spread_stand_hip_run", "spread_stand_hip_sprint", "spread_crouch_hip", "spread_air_hip", "spread_kick_on_fire_stand_hip", "spread_max_kick_stand_hip", "spread_max_kick_crouch_hip", "spread_max_kick_air_hip", "spread_decay_delay", "spread_decay_rate", "spread_moving_increase_rate", "spread_moving_decay_rate")])
    T["spread_hip"] = table(["枪", "站", "走", "冲刺", "蹲", "空中", "每发加", "站上限", "蹲上限", "空中上限", "等待（s）", "kick 回落（°/s）", "基础上升（°/s）", "基础下降（°/s）"], rows)
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g)] + [num(f.get(k), 2) for k in ("spread_stand_ads", "spread_crouch_ads", "spread_air_ads", "spread_kick_on_fire_stand_ads", "spread_max_kick_stand_ads")])
    T["spread_ads"] = table(["枪", "站", "蹲", "空中", "每发加", "上限"], rows)
    STATE = {"stand": "站", "walk": "走", "sprint": "冲刺", "crouch": "蹲", "crouchwalk": "蹲走", "jump": "跳", "slide": "滑铲"}
    rows = []
    for r in tsv(os.path.join(data, "R-SPREAD-MOVE.tsv")):
        if r["state"] in ("walk", "sprint", "jump"):
            f = F[r["gun"]]
            rows.append([N(r["gun"]), STATE[r["state"]], num(r["high"]), num(r["up_rate"]), num(f.get("spread_moving_increase_rate")), num(r["down_rate"]), num(f.get("spread_moving_decay_rate"))])
    T["spread_move"] = table(["枪", "状态", "这次最高（°）", "上升实测（°/s）", "上升字段", "下降实测（°/s）", "下降字段"], rows)
    rows = []
    for r in tsv(os.path.join(data, "R-SPREAD-FIRE.tsv")):
        if r["gun"] in ("r301", "flatline", "spitfire", "wingman", "p2020") and r["state"] in ("stand", "walk", "crouch", "sprint", "slide", "jump"):
            rows.append([N(r["gun"]), STATE[r["state"]], r["shots"], num(r["base"]), num(r["step"]), num(r["top"]), num(r["fall_starts"]), num(r["back_at"])])
    T["spread_fire"] = table(["枪", "状态", "发数", "第一发前（°）", "每发加（°）", "最高（°）", "停火后开始下降（s）", "回到第一发前的值（s）"], rows)
    blast, cur = {}, None
    for l in open(os.path.join(wdir, "blast_patterns.txt"), encoding="utf-8", errors="replace"):
        g = re.match(r'^\s*"([^"]+)"\s*$', l)
        if g: cur = g[1]; blast[cur] = []; continue
        g = re.match(r'^\s*"bullet_\d+"\s+"([-\d.]+) ([-\d.]+)', l)
        if g and cur: blast[cur].append((float(g[1]), float(g[2])))
    rows = []
    for g in guns:
        f = F[g]
        name = f.get("blast_pattern")
        if name:
            pts = blast.get(name, [])
            rows.append([N(g), f"`{name}`", len(pts), num(max((x * x + y * y) ** 0.5 for x, y in pts), 1) if pts else "", num(f.get("blast_pattern_default_scale"), 2), num(f.get("blast_pattern_ads_scale"), 2), num(f.get("blast_pattern_zero_distance"), 0)])
    T["blast"] = table(["枪", "图案", "弹片数", "表里最外一片的半径", "默认比例", "开镜比例", "归零距离字段"], rows)

    # ---------------------------------------------------------------- mods
    diffs = tsv(os.path.join(gm, "A-MOD-DIFFS.tsv"))
    KEY = ["ammo_clip_size", "reload_time", "reloadempty_time", "holster_time", "deploy_time", "raise_time", "lower_time", "zoom_time_in", "zoom_time_out", "viewkick_pitch_base", "viewkick_pitch_random", "viewkick_yaw_base", "viewkick_yaw_random", "spread_stand_hip", "spread_stand_hip_run", "spread_air_hip", "spread_crouch_hip", "fire_rate", "damage_near_value", "damage_headshot_scale", "ammo_per_shot", "is_semi_auto", "burst_fire_count", "zoom_fov", "ads_fov_zoomfrac_start", "ads_fov_zoomfrac_end", "ads_move_speed_scale", "projectile_launch_speed", "rechamber_time", "reloadsegment_time_loop", "viewdrift_ads_stand_scale_pitch", "viewdrift_ads_stand_scale_yaw", "viewkick_air_scale_ads", "spread_kick_on_fire_stand_hip", "spread_decay_rate"]
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    guns_of = collections.defaultdict(set)
    for r in diffs:
        guns_of[r["mod"]].add(r["gun"])
        for ch in r["changes (visuals and sounds left out)"].split(";"):
            g = re.match(r"\s*(\w+):(\S+)->(\S+)", ch)
            if g and g[1] in KEY:
                per[r["mod"]][g[1]].append((g[2], g[3]))
    def describe(values):
        ratios, abss = [], []
        for a, b in values:
            try:
                x, y = float(a), float(b)
                if x != 0: ratios.append(y / x)
                abss.append((x, y))
            except ValueError: pass
        if not abss: return ""
        if len(values) == 1: return f"{num(abss[0][0], 3)} → {num(abss[0][1], 3)}"
        if ratios and max(ratios) - min(ratios) < 0.005: return f"×{ratios[0]:.3g}"
        if ratios: return f"×{min(ratios):.3g} 到 ×{max(ratios):.3g}"
        return f"{num(abss[0][0], 3)} → {num(abss[0][1], 3)}"
    def mod_table(mods):
        rows = []
        for m in mods:
            if m not in per: continue
            parts = [f"`{k}` {describe(per[m][k])}" for k in KEY if k in per[m]]
            rows.append([f"`{m}`", len(guns_of[m]), "；".join(parts)])
        return table(["配件", "枪数", "变化（一把枪写从多少到多少，多把枪写比例）"], rows)
    T["mods_barrel"] = mod_table([f"barrel_stabilizer_l{i}" for i in (1, 2, 3)] + ["barrel_stabilizer_l4_flash_hider", "corrupted_barrel"])
    T["mods_mag"] = mod_table([f"{s}_l{i}" for s in ("bullets_mag", "highcal_mag", "energy_mag", "sniper_mag") for i in (1, 2, 3, 4)] + ["corrupted_mag"])
    T["mods_stock"] = mod_table([f"stock_tactical_l{i}" for i in (1, 2, 3)] + ["corrupted_tactical_stock"] + [f"stock_sniper_l{i}" for i in (1, 2, 3, 4)] + ["corrupted_stock_sniper"])
    T["mods_laser"] = mod_table([f"laser_sight_l{i}" for i in (1, 2, 3, 4)] + ["corrupted_laser"])
    T["mods_bolt"] = mod_table([f"shotgun_bolt_l{i}" for i in (1, 2, 3, 4)])
    T["mods_other"] = mod_table(["hopup_headshot_dmg", "elevator_shooter", "amped_damage", "fast_reload_mod", "auto_loader"])

    # ---------------------------------------------------------------- fire
    rows = []
    for r in tsv(os.path.join(gm, "D-RATE.tsv")):
        g = r["gun"]
        rows.append([N(g), num(r["field"]), num(r["burst"], 0) if float(r["burst"] or 0) else "", num(r["hold_rate"]), num(r["hold_iv"], 3), num(r["hold_first"], 3), num(r["hold_last"], 3), num(r["taps_rate"]), r["clip"]])
    T["rate"] = table(["枪", "字段（发/s）", "连发数", "按住实测（发/s）", "间隔中位数（s）", "第一个间隔", "最后一个间隔", "连点（发/s）", "弹匣"], rows)
    rows = []
    for g in guns:
        f = F[g]
        rows.append([N(g), num(f.get("damage_near_value"), 1), num(f.get("damage_far_value"), 1), num(f.get("damage_headshot_scale"), 2), num(f.get("damage_leg_scale"), 2), num(f.get("projectile_launch_speed"), 0), num(f.get("projectile_gravity_scale"), 2), num(f.get("projectile_drag_coefficient"), 4), num(f.get("bolt_zero_distance"), 1), f.get("pass_through_depth", "")])
    T["ballistic_fields"] = table(["枪", "近伤害", "远伤害", "爆头 ×", "打腿 ×", "子弹速度", "重力 ×", "阻力", "归零距离字段", "穿透深度"], rows)
    vm = collections.defaultdict(dict)
    for r in tsv(os.path.join(gm, "D-VIEWMODEL.tsv")): vm[r["gun"]][r["mode"]] = r
    rows = []
    for g, m in vm.items():
        h, a = m.get("hip"), m.get("ads")
        if not h or not a: continue
        rows.append([N(g), num(h["muzzleF"], 1), num(h["muzzleR"], 1), num(h["muzzleU"], 1), num(a["muzzleF"], 1), num(a["muzzleR"], 1), num(a["muzzleU"], 1), num(a["fov"], 1)])
    T["viewmodel"] = table(["枪", "腰射 前", "腰射 右", "腰射 上", "开镜 前", "开镜 右", "开镜 上", "开镜 FOV"], rows)

    SN = {"stand": "站", "walk": "走", "sprint": "冲刺", "crouch": "蹲", "crouchwalk": "蹲走", "slide": "滑铲"}
    T["hold_pose"] = table(["枪", "状态", "姿态 前", "姿态 右", "姿态 上", "摆幅 前", "摆幅 右", "摆幅 上", "上下周期（s）", "窗口（s）"], [[N(r["gun"]), SN[r["state"]], r["poseF"], r["poseR"], r["poseU"], r["swingF"], r["swingR"], r["swingU"], r["periodU"], r["seconds"]] for r in tsv(os.path.join(data, "R-HOLD-POSE.tsv")) if r["state"] != "stand"])
    src = os.path.join(gm, "report", "src")
    for p in sorted(glob.glob(os.path.join(src, "*.md"))):
        text = open(p, encoding="utf-8").read()
        def fill(m):
            if m[1] not in T: raise SystemExit("no table " + m[1])
            return T[m[1]]
        out = re.sub(r"\{\{(\w+)\}\}", fill, text)
        with open(os.path.join(gm, "report", os.path.basename(p)), "w", encoding="utf-8", newline="\n") as f: f.write(out)
        print(os.path.basename(p), len(out))


if __name__ == "__main__":
    main()
