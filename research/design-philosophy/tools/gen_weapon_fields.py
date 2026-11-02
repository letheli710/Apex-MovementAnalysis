"""Generate WEAPON-FIELDS.md from the S21 weapon .txt files and springs.txt.

Usage: py -3 gen_weapon_fields.py <research-src/s21-platform/scripts/weapons> <out.md>
Only reads base fields (everything before "Mods"). Prints the counts quoted in DESIGN-PHILOSOPHY.md.
"""
import math
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf8")

# (file stem, display name, class). Class is our grouping, not a game field.
GUNS = [
    ("autopistol", "RE-45", "手枪"), ("semipistol", "P2020", "手枪"), ("wingman", "Wingman", "手枪"),
    ("r97", "R-99", "SMG"), ("alternator_smg", "Alternator", "SMG"), ("car", "C.A.R.", "SMG"),
    ("volt_smg", "Volt", "SMG"), ("pdw", "Prowler", "SMG"),
    ("rspn101", "R-301", "步枪"), ("vinson", "Flatline", "步枪"), ("energy_ar", "Havoc", "步枪"),
    ("hemlok", "Hemlok", "步枪"), ("nemesis", "Nemesis", "步枪"),
    ("lmg", "Spitfire", "机枪"), ("esaw", "Devotion", "机枪"), ("lstar", "L-STAR", "机枪"), ("dragon_lmg", "Rampage", "机枪"),
    ("g2", "G7", "精确"), ("doubletake", "Triple Take", "精确"), ("3030", "30-30", "精确"), ("bow", "Bocek", "精确"),
    ("dmr", "Longbow", "狙击"), ("sentinel", "Sentinel", "狙击"), ("defender", "Charge Rifle", "狙击"), ("sniper", "Kraber", "狙击"),
    ("shotgun", "EVA-8", "霰弹"), ("mastiff", "Mastiff", "霰弹"), ("energy_shotgun", "Peacekeeper", "霰弹"), ("shotgun_pistol", "Mozambique", "霰弹"),
]


def fields(text):
    return dict(re.findall(r'"(\w+)"\s+"([^"]*)"', text.split('"Mods"')[0]))


def springs(path):
    text = open(path, encoding="utf8", errors="ignore").read()
    out = {}
    for name, body in re.findall(r'"(\w+)"\s*\{([^{}]*)\}', text):
        out[name] = {k: float(v) for k, v in re.findall(r'"(\w+)"\s+"(-?[\d.]+)"', body)}
    return out


def fl(f, k, default=None):
    try:
        return float(f[k])
    except (KeyError, ValueError):
        return default


def fmt(v, n=2):
    if v is None:
        return "—"
    s = f"{v:.{n}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def zeta(k, d):
    return d / (2 * math.sqrt(k)) if k and k > 0 and d is not None else None


def rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for m in range(i, j + 1):
            r[order[m]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return num / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


def write_table(rows, out):
    L = [
        "# 全枪字段表（自动生成）", "",
        "由 `tools/gen_weapon_fields.py` 从 `research-src/s21-platform/scripts/weapons/` 的 `mp_weapon_*.txt` 顶层字段和 `springs.txt` 生成，**都是 S21 数据文件的值，不含配件 mod**。ζ = d / (2√k) 是算的。分类是我们分的，不是游戏字段。这些值是 [数据]：写在文件里；运行时含义只在 RECOIL-VIEW、ADS-CURVES 测过的那几把枪上是 [实测]。",
        "", "## 1. 重量：开镜、切枪、开镜移动", "",
        "| 枪 | 类 | zoom in | zoom out | deploy | holster | raise | ADS 移速 | zoom_fov | 换弹 | 射速 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for n, c, f, _, _ in rows:
        vals = ["zoom_time_in", "zoom_time_out", "deploy_time", "holster_time", "raise_time", "ads_move_speed_scale", "zoom_fov", "reload_time", "fire_rate"]
        L.append(f"| {n} | {c} | " + " | ".join(fmt(fl(f, k)) for k in vals) + " |")
    L += [
        "", "## 2. 后坐：kick 和弹簧（俯仰）", "",
        "`放大` = hard + soft × 20 / d热，是 k热 = 0 时每发最终抬高对 kick 的倍数（RECOIL-VIEW §1.2 的公式）；k热 ≠ 0 时不适用，写 —。", "",
        "| 枪 | 类 | 图案 | base | soft | hard | soft/hard | 腰射 k/d（ζ） | 腰射热 k/d | 开镜 k/d（ζ） | 开镜热 k/d | hold+fade | 腰射 fraction | 开镜 fraction | 放大（开镜） |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for n, c, f, cold, hot in rows:
        s, h = fl(f, "viewkick_pitch_softScale", 0), fl(f, "viewkick_pitch_hardScale", 0)
        hk, hd = cold.get("hipfire_pitch_springConstant"), cold.get("hipfire_pitch_damping")
        ak, ad = cold.get("ADS_pitch_springConstant"), cold.get("ADS_pitch_damping")
        hhk, hhd = hot.get("hipfire_pitch_springConstant"), hot.get("hipfire_pitch_damping")
        ahk, ahd = hot.get("ADS_pitch_springConstant"), hot.get("ADS_pitch_damping")
        amp = "—"
        if ahk == 0 and ahd:
            amp = fmt(h + s * 20 / ahd)
        L.append(
            f"| {n} | {c} | {f.get('viewkick_pattern') or '—'} | {fmt(fl(f, 'viewkick_pitch_base'))} | {fmt(s)} | {fmt(h)} | {fmt(s / h if h else None, 1)} | "
            f"{fmt(hk, 0)}/{fmt(hd, 0)}（{fmt(zeta(hk, hd))}） | {fmt(hhk, 0)}/{fmt(hhd, 0)} | {fmt(ak, 0)}/{fmt(ad, 0)}（{fmt(zeta(ak, ad))}） | {fmt(ahk, 0)}/{fmt(ahd, 0)} | "
            f"{fmt(fl(f, 'viewkick_spring_cooldown_holdtime'))}+{fmt(fl(f, 'viewkick_spring_cooldown_fadetime'))} | {fmt(fl(f, 'viewkick_hipfire_weaponFraction'))} | {fmt(fl(f, 'viewkick_ads_weaponFraction'))} | {amp} |"
        )
    L += [
        "", "## 3. 扩散：姿态（度）", "",
        "| 枪 | 类 | 站腰 | 蹲腰 | 走腰 | 冲刺腰 | 空中腰 | 站开镜 | 蹲开镜 | 空中开镜 | 每发 kick（站腰） | kick 上限 | 回落等待 | 回落速率 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for n, c, f, _, _ in rows:
        vals = ["spread_stand_hip", "spread_crouch_hip", "spread_stand_hip_run", "spread_stand_hip_sprint", "spread_air_hip", "spread_stand_ads", "spread_crouch_ads", "spread_air_ads", "spread_kick_on_fire_stand_hip", "spread_max_kick_stand_hip", "spread_decay_delay", "spread_decay_rate"]
        L.append(f"| {n} | {c} | " + " | ".join(fmt(fl(f, k)) for k in vals) + " |")
    L += [
        "", "## 4. 图案重开和状态缩放", "",
        "| 枪 | 类 | value 等待 | value 速率 | 打 5 发后回到第一行（s） | air_scale_ads | duck_scale | move_scale | firstshot_ads | scale_min 腰射 | scale_max 腰射 |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for n, c, f, _, _ in rows:
        de, ra = fl(f, "viewkick_scale_valueDecayDelay"), fl(f, "viewkick_scale_valueDecayRate")
        vals = ["viewkick_air_scale_ads", "viewkick_duck_scale", "viewkick_move_scale", "viewkick_scale_firstshot_ads", "viewkick_scale_min_hipfire", "viewkick_scale_max_hipfire"]
        L.append(f"| {n} | {c} | {fmt(de, 3)} | {fmt(ra)} | {fmt(de + 5 / ra if de is not None and ra else None)} | " + " | ".join(fmt(fl(f, k)) for k in vals) + " |")
    open(out, "w", encoding="utf8", newline="\n").write("\n".join(L) + "\n")


def report(rows):
    auto = [r for r in rows if r[2].get("viewkick_pattern")]
    single = [r for r in rows if not r[2].get("viewkick_pattern")]
    ratio = lambda r: fl(r[2], "viewkick_pitch_softScale", 0) / (fl(r[2], "viewkick_pitch_hardScale", 1) or 1)
    print("guns", len(rows), "with pattern", len(auto), "without", [r[0] for r in single])
    print("soft/hard pattern", sorted((round(ratio(r), 1), r[0]) for r in auto))
    print("soft/hard no pattern", sorted((round(ratio(r), 2), r[0]) for r in single))
    fa = [(fl(r[2], "viewkick_ads_weaponFraction"), r[0]) for r in rows]
    print("ADS fraction 0:", sum(1 for v, _ in fa if v == 0), "nonzero", sorted(x for x in fa if x[0]))
    fh = [fl(r[2], "viewkick_hipfire_weaponFraction") for r in rows]
    print("hip fraction range", min(fh), max(fh), "hip<=ads:", [r[0] for r in rows if fl(r[2], "viewkick_hipfire_weaponFraction") <= fl(r[2], "viewkick_ads_weaponFraction")])
    print("hot ADS k=0:", [r[0] for r in rows if r[4].get("ADS_pitch_springConstant") == 0])
    print("hot ADS k!=0:", [(r[0], r[4].get("ADS_pitch_springConstant")) for r in rows if r[4].get("ADS_pitch_springConstant") != 0])
    print("hot hip k=0:", [r[0] for r in rows if r[4].get("hipfire_pitch_springConstant") == 0])
    za = lambda r: zeta(r[3].get("ADS_pitch_springConstant"), r[3].get("ADS_pitch_damping"))
    zh = lambda r: zeta(r[3].get("hipfire_pitch_springConstant"), r[3].get("hipfire_pitch_damping"))
    print("cold ADS zeta<1:", [(r[0], round(za(r), 2)) for r in rows if za(r) and za(r) < 1])
    print("cold ADS zeta>=1:", [(r[0], round(za(r), 2)) for r in rows if za(r) and za(r) >= 1])
    print("cold hip zeta<1:", [(r[0], round(zh(r), 2)) for r in rows if zh(r) and zh(r) < 1])
    print("cold hip zeta>=1:", [(r[0], round(zh(r), 2)) for r in rows if zh(r) and zh(r) >= 1])
    print("missing spring:", [r[0] for r in rows if not r[3]])
    print("ADS k<=hip k:", [r[0] for r in rows if r[3].get("ADS_pitch_springConstant", 0) <= r[3].get("hipfire_pitch_springConstant", 0)])
    z = lambda k: [fl(r[2], k) for r in rows]
    print("spearman zoom-deploy", round(spearman(z("zoom_time_in"), z("deploy_time")), 2), "zoom-ads", round(spearman(z("zoom_time_in"), z("ads_move_speed_scale")), 2),
          "deploy-holster", round(spearman(z("deploy_time"), z("holster_time")), 2), "deploy-raise", round(spearman(z("deploy_time"), z("raise_time")), 2))
    print("zoom out>in:", [r[0] for r in rows if fl(r[2], "zoom_time_out") > fl(r[2], "zoom_time_in")], "out==in:", [r[0] for r in rows if fl(r[2], "zoom_time_out") == fl(r[2], "zoom_time_in")])
    ok, bad = 0, []
    for r in rows:
        s = [fl(r[2], k) for k in ["spread_crouch_hip", "spread_stand_hip", "spread_stand_hip_run", "spread_stand_hip_sprint", "spread_air_hip"]]
        if all(a <= b for a, b in zip(s, s[1:])):
            ok += 1
        else:
            bad.append((r[0], s))
    print("spread order ok", ok, "bad", bad)
    print("same in all stances:", [r[0] for r in rows if len({fl(r[2], k) for k in ["spread_crouch_hip", "spread_stand_hip", "spread_stand_hip_sprint", "spread_air_hip", "spread_stand_ads"]}) == 1])
    print("perm nonzero:", [(r[0], k) for r in rows for k in r[2] if k.startswith("viewkick_perm") and (fl(r[2], k) or 0) != 0], "guns with perm fields:", sum(1 for r in rows if "viewkick_perm_pitch_base" in r[2]))
    print("spread_air_ads", sorted((fl(r[2], "spread_air_ads"), r[0]) for r in rows))
    print("spread_stand_ads", sorted((fl(r[2], "spread_stand_ads"), r[0]) for r in rows if fl(r[2], "spread_stand_ads")))
    print("crouch/stand", sorted(round(fl(r[2], "spread_crouch_hip") / fl(r[2], "spread_stand_hip"), 2) for r in rows if fl(r[2], "spread_stand_hip")))
    print("air/stand", sorted(round(fl(r[2], "spread_air_hip") / fl(r[2], "spread_stand_hip"), 2) for r in rows if fl(r[2], "spread_stand_hip")))
    by = {}
    for r in rows:
        by.setdefault(r[1], []).append(r)
    for c, rs in by.items():
        rng = lambda k: (min(fl(x[2], k) for x in rs), max(fl(x[2], k) for x in rs))
        print(c, {k: rng(k) for k in ["zoom_time_in", "zoom_time_out", "deploy_time", "ads_move_speed_scale", "reload_time", "fire_rate"]})


def main(root, out):
    sp = springs(os.path.join(root, "springs.txt"))
    rows = []
    for stem, name, cls in GUNS:
        f = fields(open(os.path.join(root, f"mp_weapon_{stem}.txt"), encoding="utf8", errors="ignore").read())
        cold = sp.get(f.get("viewkick_spring", ""), {})
        hot = sp.get(f.get("viewkick_spring_hot", ""), cold)
        rows.append((name, cls, f, cold, hot))
    write_table(rows, out)
    report(rows)


main(sys.argv[1], sys.argv[2])
