#!/usr/bin/env python3
"""The one-row-per-gun table IS-GUNS.tsv, and IS-SILHOUETTE.tsv (each gun's outline along its length).

  py -3 make_table.py <run dir> <data dir>

Sources, as in every table here:
  [picture]  measured from the difference of engine pictures of the gun's own model (capture.py, measure.py): positions and sizes, about +-0.05 u, 1 to 2 % scale
  [held]     read from the held view model while aimed (attachments)
  [field]    weapon script value
  [eye]      my reading of the aimed picture and close-ups: type, parts, what is a user-interface overlay
"""
import csv
import json
import os
import sys

import numpy as np

from measure import FPX, load, mask

# front part index, rear part index (None = no such part), type [eye]. From the close-ups and the aimed picture of each gun.
T = {
    "r301": (0, 2, "两件式，翻折。前：两片弯耳（开口朝上）夹一个矮凸点。后：楔形底座上两面高耳，中间是通的 U 形槽，耳下侧面有圆孔"),
    "r99": (0, 1, "两件式，翻折。前：立柱上的开口圆环（顶部缺口，发蓝光）。后：方块上两只外撇的角"),
    "car": (0, 1, "两件式，翻折。前：立柱上的 U 形叉。后：方块上两面厚墙，中间通"),
    "flatline": (None, 2, "单件式后瞄，翻折：宽护罩中间一个缺口，两侧各一个红点。没有立起来的前瞄：视线前方只有导轨（F -6..-2 顶 2.39，低于视线 0.96）"),
    "spitfire": (0, 2, "两件式，翻折。前：细颈 U 形叉。后：立柱上的闭合圆环"),
    "alternator": (0, 1, "固定一体，无 bodygroup。后：枪身顶部两条发光斜片（开镜时有一道细亮横线）。前：低矮块，低于视线 0.37，开镜看不到。枪口偏右 0.31"),
    "re45": (0, 1, "后瞄翻折，前瞄固定。后：方块上两只竖耳，开镜中心有淡色圆环（界面贴图）。前：枪管顶部矮块，低于视线 0.70"),
    "volt": (0, 1, "两件式，翻折。前：立柱上的 Y 形叉。后：宽矮的块，两侧小耳。开镜时红色圆环是界面贴图"),
    "p2020": (0, 1, "固定一体，滑套顶面就是瞄线，几乎不立起：前后都只比视线低 0.02–0.15。滑套后面有发光计数条"),
    "hemlok": (0, 1, "两件式，翻折。前：两齿高叉。后：A 形架上的闭合圆环"),
    "ehemlok": (0, 1, "同 Hemlok（同一个模型文件）"),
    "prowler": (0, 1, "两件式，翻折。前：矮叉。后：带两耳的块，两边有挡板"),
    "nemesis": (0, 1, "两件式，翻折。前：窄细立片。后：宽口大叉（两片内弯的爪），中间通"),
    "eva8": (0, 2, "两件式，翻折（bodygroup 叫 sight）。前：两片弧形护耳夹细柱。后：方块上两耳，两侧发绿光"),
    "mastiff": (0, 1, "前瞄翻折，后瞄固定。前：枪口上方的宽 U 叉，开镜时有白色方括号（界面贴图）。后：方块上两耳"),
    "peacekeeper": (0, 1, "两件式，翻折（bodygroup 叫 sight_rear，管前后两件）。前：导轨上一个矮立柱。后：宽楔形座上两面高耳，中间通"),
    "mozambique": (0, 2, "固定一体。后：枪身后部两只小耳。前：枪管上两个极小的点，低于视线"),
    "tripletake": (0, 1, "两件式，翻折。前：导轨上的小座，开镜时红色菱形是界面贴图。后：很宽的 U，两臂有绿色发光条"),
    "kraber": (None, None, "没有机瞄。默认带固定瞄准镜（bodygroup scope_dcom），开镜全屏瞄准镜画面，看不到枪"),
    "longbow": (0, 1, "两件式，翻折。前：窄细高叉，带小侧旋钮。后：宽护罩中间缺口"),
    "sentinel": (0, 1, "两件式，翻折。前：窄立片。后：两耳加两侧旋钮"),
    "g7": (0, 2, "后瞄翻折，前瞄固定。前：两片短耳，开镜时青色弧线是界面贴图。后：方块上两耳，两侧旋钮"),
    "wingman": (0, 1, "固定一体，无 bodygroup。后：后方块顶部的方形缺口（两只方耳），计数屏在缺口正下方。前：枪管顶部的平顶小罩，低于视线 0.27"),
    "chargerifle": (0, None, "单件式，翻折：高 U 形叉（铜色），开镜时红色弧线是界面贴图。这一件前面没有前瞄"),
    "havoc": (None, 1, "单件式后瞄，翻折（宽口两耳）。前方枪口附近没有模型瞄具：开镜时的小红圈是界面贴图，挂在枪口处的 ADS_CENTER 上"),
    "devotion": (0, 2, "两件式，翻折。前：开口圆环叉。后：两耳，耳尖有青光，下方是计数屏"),
    "rampage": (0, 1, "两件式，翻折（bodygroup 叫 sight_rear_on）。前：高 V 叉。后：两只外撇的大爪，开镜时粉色括号是界面贴图"),
    "lstar": (0, 1, "两件式，翻折（bodygroup 叫 sight_on）。前：枪口上方矮叉。后：方块上两耳"),
    "r3030": (0, 1, "两件式，翻折。前：枪管上的细叉。后：U 形缺口，右侧有环。枪口偏右 0.31"),
    "bocek": (0, None, "弓：弓身侧面的小环（Bocek 自己的瞄准环），开镜时是界面贴图圆环；视线偏离弓身中线 0.62"),
    "sheila": (0, 1, "架设枪，脚本不能给到手上，没有开镜实测。前：很高的矩形线框（F -22.5，U 7.3–10.3）。后：枪身后上方的方盒。视线高度只能看 ADS_CENTER 挂点（U 8.96）"),
    "mounted_turret": (0, 1, "和 Sheila 相同的外形（不同文件）；同样没有开镜实测"),
    "vantage": (None, None, "没有机瞄。固定瞄准镜（F -32.3..-24.0，U 2.65–4.56），技能武器，没有试着拿到手上，没有开镜实测"),
}
OPTIC_NOTE = {
    "g7": "光学镜不改 sight_rear（字段）：后瞄不折，靠镜子盖过去",
    "kraber": "只换镜子，没有机瞄可折",
    "vantage": "没有配件",
    "alternator": "模型里没有 bodygroup，机瞄不变",
    "wingman": "模型里没有 bodygroup，机瞄不变",
    "mozambique": "模型里没有 bodygroup，机瞄不变",
    "sheila": "模型里没有 bodygroup，字段写了也不起作用",
    "mounted_turret": "同上",
}


def main():
    run, data = sys.argv[1:3]
    prof = json.load(open(os.path.join(data, "IS-PROFILES.json"), encoding="utf-8"))
    static = {r["gun"]: r for r in csv.DictReader(open(os.path.join(data, "IS-STATIC.tsv"), encoding="utf-8"), delimiter="\t")}
    names = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "names.json"), encoding="utf-8"))
    keys = ["gun", "name", "type", "bodygroups", "optics",
            "aim_F", "aim_R", "aim_U", "aim_pitch", "ads_center_F", "ads_center_U",
            "front_F", "front_top_U", "front_base_U", "front_top_minus_los", "front_eye_dist", "front_width", "front_gap_at_los",
            "rear_F", "rear_top_U", "rear_base_U", "rear_top_minus_los", "rear_eye_dist", "rear_width", "rear_gap_at_los",
            "source"]
    rows = []
    for g, (fi, ri, ty) in T.items():
        p = prof.get(g)
        if not p:
            continue
        L = p.get("los") or {}
        ac = p.get("ads_center") or ["", "", ""]
        s = static.get(g, {})
        r = dict(gun=g, name=names.get(g, g), type=ty, bodygroups=s.get("iron_default", ""), optics=OPTIC_NOTE.get(g, s.get("optics_set", "")))
        r.update(aim_F=L.get("mF", ""), aim_R=L.get("mR", ""), aim_U=L.get("mU", ""), aim_pitch=L.get("pitch", ""), ads_center_F=ac[0], ads_center_U=ac[2])
        for tag, i in (("front", fi), ("rear", ri)):
            if i is None or i >= len(p["parts"]) or "F" not in p["parts"][i]:
                continue
            q = p["parts"][i]
            r[f"{tag}_F"] = f'{q["F"][0]}..{q["F"][1]}'
            r[f"{tag}_top_U"] = q["U"][1]
            r[f"{tag}_base_U"] = q.get("base_U", "")
            r[f"{tag}_top_minus_los"] = q.get("top_over_los", "")
            ce = q.get("cam_F")
            r[f"{tag}_eye_dist"] = f"{ce[0]}..{ce[1]}" if ce else ""
            tw = q.get("top_width")
            r[f"{tag}_width"] = f"{tw[0]}..{tw[1]}" if tw else ""
            ga = q.get("gap_at_los")
            # 0..0 means something nearer to the camera crossed that row: not measured
            r[f"{tag}_gap_at_los"] = f"{ga[0]}..{ga[1]}" if ga and ga[0] is not None and ga[1] is not None and ga[1] - ga[0] > 0.1 else ""
        r["source"] = "F,U,宽,缺口 [picture]；aim [held]；类型 [eye]；光学镜 [field]" if L else "F,U,宽 [picture]；类型 [eye]；没有开镜实测"
        rows.append(r)
    with open(os.path.join(data, "IS-GUNS.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(keys) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(k, "")) for k in keys) + "\n")
    # outline per unit of length
    out = ["gun\tF\ttop_U\tbottom_U\tleft_R\tright_R"]
    for g in T:
        d = os.path.join(run, g)
        mp = os.path.join(d, "meta.json")
        if not os.path.exists(mp):
            continue
        meta = json.load(open(mp, encoding="utf-8"))
        sh, st = meta["shots"].get("side_full_base"), meta["shots"].get("top_full_base")
        if not sh or not st:
            continue
        b, n = load(d, "side_full_base"), load(d, "side_full_none")
        t, tn = load(d, "top_full_base"), load(d, "top_full_none")
        ms, mt = mask(b, n), mask(t, tn)
        s, s2 = FPX / sh["d"], FPX / st["d"]
        fF, fU = sh["focus"][0], sh["focus"][2]
        ft = st["focus"][0]
        lo, hi = meta["F_extent"]
        F = float(int(hi))
        while F >= lo:
            x = int(round(800 - (F - fF) * s))
            x2 = int(round(800 - (F - ft) * s2))
            row = [g, f"{F:.0f}"]
            if 0 <= x < 1600 and ms[:, x].any():
                r = np.where(ms[:, x])[0]
                row += [f"{fU + (450 - r.min()) / s:.2f}", f"{fU + (450 - r.max() - 1) / s:.2f}"]
            else:
                row += ["", ""]
            if 0 <= x2 < 1600 and mt[:, x2].any():
                r = np.where(mt[:, x2])[0]
                row += [f"{(450 - r.max() - 1) / s2:.2f}", f"{(450 - r.min()) / s2:.2f}"]
            else:
                row += ["", ""]
            out.append("\t".join(row))
            F -= 1
    with open(os.path.join(data, "IS-SILHOUETTE.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print(len(rows), "rows;", len(out) - 1, "outline rows")


if __name__ == "__main__":
    main()
