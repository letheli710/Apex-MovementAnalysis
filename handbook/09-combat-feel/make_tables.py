"""Build the handbook chapter 09 attachment tables from the research branches.

Run from the research repository root (any worktree that has the origin/* refs):

    py -3 -I handbook/09-combat-feel/make_tables.py

It only reads with `git show origin/<branch>:<path>` and writes the TSVs next to this script.
The sources are open PRs (not merged on 2026-11-14); the branch of each is written in the
`source` column and in README.md.
"""
import csv
import io
import os
import re
import statistics
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

SRC = {
    "fit": ("combat/recoil-view-measure", "research/combat/recoil-view/FIT-TABLE.tsv", "PR #93"),
    "vars": ("combat/gun-measure", "research/combat/gun-measure/GUN-VARS.tsv", "PR #95"),
    "rm": ("combat/gun-measure", "research/combat/gun-measure/reload-motion/RM-SUMMARY.tsv", "PR #95"),
    "raise": ("combat/gun-measure", "research/combat/gun-measure/C-RAISE2.tsv", "PR #95"),
    "spread": ("combat/gun-measure", "research/combat/gun-measure/report/06-hipfire-spread.md", "PR #95"),
    "ads": ("combat/recoil-view-measure", "research/combat/recoil-view/ADS-CURVES.tsv", "PR #93"),
}

# S21 weapon file name -> the short id used by GUN-VARS / RM-SUMMARY, and the English name.
R5_ID = {
    "rspn101": ("r301", "R-301"), "r97": ("r99", "R-99"), "car": ("car", "C.A.R."),
    "vinson": ("flatline", "VK-47 Flatline"), "lmg": ("spitfire", "M600 Spitfire"),
    "alternator_smg": ("alternator", "Alternator"), "autopistol": ("re45", "RE-45"),
    "volt_smg": ("volt", "Volt"), "semipistol": ("p2020", "P2020"), "hemlok": ("hemlok", "Hemlok"),
    "auto_hemlok": ("ehemlok", "Hemlok (auto)"), "pdw": ("prowler", "Prowler"),
    "nemesis": ("nemesis", "Nemesis"), "shotgun": ("eva8", "EVA-8"), "mastiff": ("mastiff", "Mastiff"),
    "energy_shotgun": ("peacekeeper", "Peacekeeper"), "shotgun_pistol": ("mozambique", "Mozambique"),
    "doubletake": ("tripletake", "Triple Take"), "sniper": ("kraber", "Kraber"), "dmr": ("longbow", "Longbow"),
    "sentinel": ("sentinel", "Sentinel"), "g2": ("g7", "G7 Scout"), "wingman": ("wingman", "Wingman"),
    "defender": ("chargerifle", "Charge Rifle"), "energy_ar": ("havoc", "Havoc"), "esaw": ("devotion", "Devotion"),
    "dragon_lmg": ("rampage", "Rampage"), "lstar": ("lstar", "L-STAR"), "3030": ("r3030", "30-30"),
    "bow": ("bocek", "Bocek"), "mobile_hmg": ("sheila", "Sheila (mobile)"),
}
NAME_BY_ID = {v[0]: v[1] for v in R5_ID.values()}
NAME_TO_ID = {v[1]: v[0] for v in R5_ID.values()}
NAME_TO_ID.update({"Flatline": "flatline", "Spitfire": "spitfire", "Hemlok Elite": "ehemlok",
                   "G7": "g7", "Sheila": "sheila"})


def show(key):
    branch, path, _ = SRC[key]
    return subprocess.run(["git", "show", f"origin/{branch}:{path}"], check=True,
                          capture_output=True, text=True, encoding="utf-8").stdout


def rows(key):
    return list(csv.DictReader(io.StringIO(show(key)), delimiter="\t"))


def src(key):
    branch, path, pr = SRC[key]
    return f"{path} ({pr}, {branch}, 还没合并)"


def write(name, header, data, note):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        f.write("# " + note + "\n")
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(header)
        w.writerows(data)
    print(f"{name}: {len(data)} rows")


def recoil_springs():
    out = []
    for r in rows("fit"):
        if r["weapon"] not in R5_ID:
            continue
        gid, name = R5_ID[r["weapon"]]
        out.append([gid, name, r["weapon"], r["mode"], r["kC"], r["dC"], r["kH"], r["dH"], r["hold"], r["fade"],
                    r["soft"], r["hard"], r["frac"], r["D"], r["T"], r["t50"], r["t10"],
                    r["scaleDelay"], r["scaleRate"]])
    out.sort(key=lambda x: (x[0], x[3] != "hip"))
    write("recoil-springs.tsv",
          ["gun", "name", "r5_file", "mode", "k_cold_pitch[1/s2]", "d_cold_pitch[1/s]", "k_hot_pitch[1/s2]",
           "d_hot_pitch[1/s]", "heat_hold[s]", "heat_fade[s]", "softScale_pitch[x]", "hardScale_pitch[x]",
           "weaponFraction[x]", "fit_delay_D[s]", "fit_tau_T[s]", "fit_t50[s]", "fit_t10[s]",
           "valueDecayDelay[s]", "valueDecayRate[1/s]"],
          out, "后坐弹簧和回落（每把枪的默认值，不含配件）。字段来自 springs.txt + 武器文件，D/T/t50/t10 是按弹簧公式算的回落拟合 [算]，"
               "R-301/Spitfire/Wingman/P2020 有实测 [实测]（RECOIL-VIEW §2.2）。出处 " + src("fit"))


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def raise_medians():
    med = {}
    by = {}
    for r in rows("raise"):
        m = re.match(r"ra_(\w+?)_(sprint|slide|stand)_\d+$", r["tag"])
        if m:
            by.setdefault((m.group(1), m.group(2)), []).append(float(r["latency"]))
    for k, v in by.items():
        med[k] = f"{statistics.median(v):.3f}"
    return med


def gun_weight():
    med = raise_medians()
    cols = ["holster_time", "deploy_time", "deployfirst_time", "raise_time", "lower_time", "reload_time",
            "reloadempty_time", "zoom_fov", "zoom_time_in", "zoom_time_out", "ads_move_speed_scale",
            "ads_fov_zoomfrac_start", "ads_fov_zoomfrac_end", "viewmodel_offset_zoom_frac_start",
            "viewmodel_offset_zoom_frac_end", "viewkick_air_scale_ads", "viewkick_duck_scale",
            "fire_rate", "rechamber_time", "ammo_clip_size"]
    alias = {}
    out = []
    for r in rows("vars"):
        g = r["gun"]
        if g == "gun":
            continue
        key = alias.get(g, g)
        out.append([g, NAME_BY_ID.get(g, g)] + [r.get(c, "") for c in cols] +
                   [med.get((key, "sprint"), ""), med.get((key, "slide"), ""), med.get((key, "stand"), "")])
    hdr = ["gun", "name", "holster[s]", "deploy[s]", "deployfirst[s]", "raise[s]", "lower[s]", "reload_tac[s]",
           "reload_empty[s]", "zoom_fov[deg]", "zoom_time_in[s]", "zoom_time_out[s]", "ads_move_speed_scale[x]",
           "ads_fov_zoomfrac_start[x]", "ads_fov_zoomfrac_end[x]", "vm_offset_zoom_frac_start[x]",
           "vm_offset_zoom_frac_end[x]", "viewkick_air_scale_ads[x]", "viewkick_duck_scale[x]", "fire_rate[1/s]",
           "rechamber[s]", "clip[rounds]", "sprint_to_fire[s]", "slide_to_fire[s]", "stand_to_fire[s]"]
    write("gun-weight.tsv", hdr, out,
          "枪的重量轴（P5）：运行时读回的字段 [数据]，最后三列是按开火到第一发的实测中位数 [实测，3 次]。"
          "字段 " + src("vars") + "；举枪 " + src("raise"))


def reload_moments():
    out = []
    for r in rows("rm"):
        g = r["gun"]
        if g == "gun":
            continue
        dur, ammo, unlock = num(r["dur"]), num(r["ammo"]), num(r["unlock"])
        out.append([g, NAME_BY_ID.get(g, g), r["kind"], r["runs"], r["dur"], r["ammo"], r["unlock"],
                    f"{ammo / dur:.3f}" if dur and ammo is not None else "",
                    f"{unlock / dur:.3f}" if dur and unlock is not None else ""])
    write("reload-moments.tsv",
          ["gun", "name", "kind(tac/emp)", "runs", "length[s]", "ammo_moment[s]", "unlock_moment[s]",
           "ammo_frac[x]", "unlock_frac[x]"],
          out, "换弹三个时刻（D-118 的数据来源：RM-SUMMARY）。从换弹开始算 [实测]。Sentinel 的 length 只到解锁，"
               "动画全长用 C-MOTIONS 的 2.99 / 4.05 s（D-118 例外）；Mastiff、30-30 是逐发装填，见正文 §7.3。出处 " + src("rm"))


def md_table(text, heading):
    part = text.split(heading, 1)[1]
    lines = []
    for ln in part.splitlines()[1:]:
        if ln.startswith("## "):
            break
        if ln.startswith("|"):
            lines.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return lines[0], [l for l in lines[2:]]


def spread():
    text = show("spread")
    h1, hip = md_table(text, "## 3. 每把枪的腰射字段")
    h2, ads = md_table(text, "## 6. 开镜字段")
    adsby = {r[0]: r for r in ads}
    out = []
    for r in hip:
        a = adsby.get(r[0], [""] * 6)
        out.append([NAME_TO_ID.get(r[0], r[0]), r[0]] + r[1:] + a[1:6])
    hdr = ["gun", "name", "hip_stand[deg]", "hip_walk[deg]", "hip_sprint[deg]", "hip_crouch[deg]", "hip_air[deg]",
           "kick_per_shot[deg]", "kick_max_stand[deg]", "kick_max_crouch[deg]", "kick_max_air[deg]",
           "kick_decay_delay[s]", "kick_decay_rate[deg/s]", "base_rise_rate[deg/s]", "base_fall_rate[deg/s]",
           "ads_stand[deg]", "ads_crouch[deg]", "ads_air[deg]", "ads_kick_per_shot[deg]", "ads_kick_max[deg]"]
    write("spread.tsv", hdr, out,
          "腰射 / 开镜扩散字段（S21 文件顶层值 [数据]；R-301、Flatline、Spitfire、Wingman、P2020 开火实测和字段相符 [实测]）。"
          "空格 = 文件没写。出处 " + src("spread") + " §3、§6")


def ads_curves():
    text = show("ads")
    with open(os.path.join(HERE, "ads-curves.tsv"), "w", encoding="utf-8", newline="") as f:
        f.write("# 开镜 / 关镜时枪的路径（视线中心相对腰射，按 zf 每 0.05 一行）[实测]，只有 R-301、Spitfire、Wingman。"
                "原样复制，列含义见 ADS-CURVES.md §2.3。出处 " + src("ads") + "\n")
        f.write(text.replace("\r", ""))
    print("ads-curves.tsv: copied", text.count("\n"), "lines")


if __name__ == "__main__":
    recoil_springs()
    gun_weight()
    reload_moments()
    spread()
    ads_curves()
