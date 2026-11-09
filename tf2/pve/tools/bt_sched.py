"""Parse TF2 behaviour trees (aibehavior/behavior_*.txt) and common_schedules.txt.

Usage: py -3 -I bt_sched.py <aibehavior_dir> <aisettings_resolved.tsv> <out_dir>

Writes into <out_dir>:
  data/behavior-trees.tsv   tree, selector, order, entry, native_class, condition, disabled, line
  data/schedules.tsv        schedule, sched_line, part (task|interrupt), order, name, arg, comment, line
  data/bt-users.tsv         tree, mp_users, sp_users (which aisettings point at it)
  BEHAVIOR-TREES.md         every tree as a mermaid chart + table (generated appendix)
  SCHEDULES.md              every schedule: tasks and interrupts (generated appendix)
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bt_gloss import G  # noqa: E402

ENTRY = re.compile(r"^(//\s*)?((?:(\w+)::)?(SelectSchedule_\w+))\s*(.*)$")


def parse_trees(d):
    trees = collections.OrderedDict()
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("behavior_") or not fn.endswith(".txt"):
            continue
        tree = fn[:-4]
        sels = collections.OrderedDict()
        cur = None
        with open(os.path.join(d, fn), encoding="utf-8", errors="replace") as f:
            for ln, raw in enumerate(f, 1):
                s = raw.strip()
                if not s:
                    continue
                if s.startswith("Selector_End"):
                    cur = None
                    continue
                m = re.match(r"^(//\s*)?Selector\s+(\w+)", s)
                if m and not s.startswith("Selector_End"):
                    if m.group(1):
                        continue  # commented-out selector header
                    cur = m.group(2)
                    sels[cur] = []
                    continue
                if cur is None:
                    continue
                m = ENTRY.match(s)
                if not m:
                    continue
                cond = m.group(5).split("//")[0].strip()
                sels[cur].append({
                    "entry": m.group(4), "native_class": m.group(3) or "",
                    "condition": cond, "disabled": bool(m.group(1)), "line": ln,
                })
        trees[tree] = sels
    return trees


def parse_schedules(path):
    scheds = collections.OrderedDict()
    cur, part, sched_line = None, None, None
    expect_name = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for ln, raw in enumerate(f, 1):
            code, _, comment = raw.partition("//")
            s = code.strip()
            comment = comment.strip()
            if not s:
                continue
            if s == "Schedule":
                expect_name = True
                cur = None
                continue
            if expect_name and s.startswith("SCHED_"):
                cur = s.split()[0]
                sched_line = ln
                scheds[cur] = {"line": ln, "tasks": [], "interrupts": []}
                expect_name = False
                part = None
                continue
            if s in ("Tasks", "Interrupts"):
                part = s.lower()
                continue
            if s.startswith("End_Schedule"):
                cur, part = None, None
                continue
            if cur and part:
                toks = s.split(None, 1)
                name = toks[0]
                arg = toks[1].strip() if len(toks) > 1 else ""
                if part == "tasks" and not name.startswith("TASK_"):
                    continue
                if part == "interrupts" and not name.startswith("COND_"):
                    continue
                scheds[cur][part].append({"name": name, "arg": arg, "comment": comment, "line": ln})
    return scheds


def bt_users(tsv):
    users = collections.defaultdict(lambda: ([], []))
    with open(tsv, encoding="utf-8") as f:
        next(f)
        for line in f:
            npc, key, mp, sp, *_ = line.rstrip("\n").split("\t")
            if key.lower() == "behaviorselector":
                if mp:
                    users[mp][0].append(npc)
                if sp:
                    users[sp][1].append(npc)
    return users


def label(i, e):
    n = e["entry"].replace("SelectSchedule_", "")
    zh = G.get(n, (n,))[0]
    t = f"{i}. {zh} {n}"
    if e["native_class"]:
        t += " *"
    if e["condition"]:
        t += f" [{e['condition']}]"
    return t


def tree_mermaid(tree, sels):
    out = ["```mermaid", "flowchart TD"]
    out.append('  start(["每次重新选计划（推断：先试 Common，再试当前状态那一块）"])')
    prev = "start"
    order = [s for s in ("Common",) if s in sels] + [s for s in sels if s != "Common"]
    states = [s for s in sels if s != "Common"]
    if "Common" in sels:
        out.append('  subgraph Common["Common：任何状态都先试"]')
        ids = []
        for i, e in enumerate([e for e in sels["Common"] if not e["disabled"]], 1):
            nid = f"c{i}"
            label_ = label(i, e)
            out.append(f'    {nid}["{label_}"]')
            ids.append(nid)
        for a, b in zip(ids, ids[1:]):
            out.append(f"    {a} --> {b}")
        out.append("  end")
        if ids:
            out.append(f"  start --> {ids[0]}")
            prev = ids[-1]
    out.append('  st{"NPC 当前状态"}')
    out.append(f"  {prev} -- 都没选中 --> st")
    for s in states:
        en = [e for e in sels[s] if not e["disabled"]]
        out.append(f'  subgraph {s}["{s}"]')
        ids = []
        for i, e in enumerate(en, 1):
            nid = f"{s[:2].lower()}{i}"
            label_ = label(i, e)
            out.append(f'    {nid}["{label_}"]')
            ids.append(nid)
        for a, b in zip(ids, ids[1:]):
            out.append(f"    {a} --> {b}")
        out.append("  end")
        if ids:
            out.append(f"  st -- {s} --> {ids[0]}")
    out.append("```")
    return "\n".join(out)


def used_schedules(sels):
    seen = []
    for s_, en in sels.items():
        for e in en:
            if e["disabled"]:
                continue
            n = e["entry"].replace("SelectSchedule_", "")
            for x in G.get(n, ("", "", ""))[2].split(","):
                x = x.strip()
                if x.startswith("SCHED_") or (x and x[0].isupper() and "（" not in x):
                    x = x if x.startswith("SCHED_") else "SCHED_" + x
                    if x not in seen:
                        seen.append(x)
    return seen


CHART_RE = re.compile(r"(<!-- chart:(\w+) -->\n).*?(<!-- /chart -->)", re.S)


def fill_charts(md_path, trees):
    s = open(md_path, encoding="utf-8").read()

    def rep(m):
        t = m.group(2)
        body = (tree_mermaid(t, trees[t]) + "\n\n用到的计划（按选择器名推断）："
                + "、".join("`" + x + "`" for x in used_schedules(trees[t])) + "\n")
        return m.group(1) + body + m.group(3)
    s2, n = CHART_RE.subn(rep, s)
    open(md_path, "w", encoding="utf-8", newline="\n").write(s2)
    print("filled", n, "charts in", md_path)


def main():
    bdir, resolved, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(os.path.join(outdir, "data"), exist_ok=True)
    trees = parse_trees(bdir)
    scheds = parse_schedules(os.path.join(bdir, "common_schedules.txt"))
    users = bt_users(resolved)

    with open(os.path.join(outdir, "data", "behavior-trees.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("tree\tselector\torder\tentry\tnative_class\tcondition\tdisabled\tline\n")
        for t, sels in trees.items():
            for s, en in sels.items():
                k = 0
                for e in en:
                    if not e["disabled"]:
                        k += 1
                    f.write(f"{t}\t{s}\t{k if not e['disabled'] else ''}\t{e['entry']}\t{e['native_class']}\t{e['condition']}\t{int(e['disabled'])}\t{e['line']}\n")
    with open(os.path.join(outdir, "data", "schedules.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("schedule\tsched_line\tpart\torder\tname\targ\tcomment\tline\n")
        for n, sc in scheds.items():
            for part in ("tasks", "interrupts"):
                for i, x in enumerate(sc[part], 1):
                    f.write(f"{n}\t{sc['line']}\t{part[:-1]}\t{i}\t{x['name']}\t{x['arg']}\t{x['comment']}\t{x['line']}\n")
    with open(os.path.join(outdir, "data", "bt-users.tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("tree\tmp_users\tsp_users\n")
        for t in trees:
            mp, sp = users.get(t, ([], []))
            f.write(f"{t}\t{' '.join(mp)}\t{' '.join(sp)}\n")

    # ---- BEHAVIOR-TREES.md
    all_entries = collections.Counter()
    for t, sels in trees.items():
        for s, en in sels.items():
            for e in en:
                if not e["disabled"]:
                    all_entries[e["entry"]] += 1
    L = ["# 附录：TF2 全部行为树（脚本生成）", "",
         "由 `tools/bt_sched.py` 从 `aibehavior/behavior_*.txt` 生成，不要手改。正文和含义见 [AI-SPEC.md](AI-SPEC.md) 第 3 节。", "",
         "- 来源：`TF2-Research/local/vpk/client_sp_training/scripts/aibehavior/`（零售战役包，Respawn 原版）。Northstar 1.31.14 `mod/scripts/aibehavior/` 和它逐字节相同（去掉换行符差别），见 AI-SPEC 第 3.1 节。",
         "- 每块（Selector）从上往下试，第一个返回计划的胜出（推断：选择函数在 `server.dll` 里，原生）。`[health > 0.4]` 这类条件写在树里，含义是\"血量比例大于 0.4 才试这一项\"（推断）。",
         "- 被 `//` 注释掉的项不画进图，表里标\"注释掉\"。",
         f"- 共 {len(trees)} 棵树，{len(all_entries)} 种不同的 `SelectSchedule_*`。", ""]
    for t, sels in trees.items():
        mp, sp = users.get(t, ([], []))
        L.append(f"## {t}")
        L.append("")
        L.append(f"- 多人用它的设置文件：{', '.join('`'+x+'`' for x in mp) if mp else '（无）'}")
        L.append(f"- 战役用它的设置文件：{', '.join('`'+x+'`' for x in sp) if sp else '（无）'}")
        L.append("")
        L.append(tree_mermaid(t, sels))
        L.append("")
        L.append("用到的计划（按选择器名推断）：" + "、".join("`" + x + "`" for x in used_schedules(sels)))
        L.append("")
        L.append("| 块 | # | 选择器 | 类 | 条件 | 行 |")
        L.append("|---|---|---|---|---|---|")
        for s, en in sels.items():
            k = 0
            for e in en:
                if e["disabled"]:
                    num = "注释掉"
                else:
                    k += 1
                    num = str(k)
                L.append(f"| {s} | {num} | `{e['entry']}` | {e['native_class']} | {e['condition']} | {t}.txt:{e['line']} |")
        L.append("")
    L.append("## 选择器词表（全部按名字推断）")
    L.append("")
    L.append("| 选择器 | 中文 | 做什么 | 可能返回的计划 | 用在几棵树里 |")
    L.append("|---|---|---|---|---|")
    for n in sorted(G):
        zh, what, sc = G[n]
        L.append(f"| `SelectSchedule_{n}` | {zh} | {what} | {sc} | {all_entries.get('SelectSchedule_' + n, 0)} |")
    L.append("")
    with open(os.path.join(outdir, "BEHAVIOR-TREES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")

    # ---- SCHEDULES.md
    tasks = collections.Counter()
    conds = collections.Counter()
    for sc in scheds.values():
        for x in sc["tasks"]:
            tasks[x["name"]] += 1
        for x in sc["interrupts"]:
            conds[x["name"]] += 1
    L = ["# 附录：TF2 全部计划（`common_schedules.txt`，脚本生成）", "",
         "由 `tools/bt_sched.py` 生成，不要手改。含义见 [AI-SPEC.md](AI-SPEC.md) 第 4 节。", "",
         f"- 来源：`aibehavior/common_schedules.txt`（零售战役包和 Northstar 相同）。共 {len(scheds)} 个计划，用到 {len(tasks)} 种任务、{len(conds)} 种打断条件。",
         "- 一个计划 = 一串任务（按顺序做）+ 一组打断条件（任一条件成立就放弃这个计划，重新选）。任务和条件的实现都在 `server.dll` 里（原生）。",
         "- 任务后面的数是参数，`//` 后是文件里的原注释。", ""]
    L.append("| 计划 | 行 | 任务（按顺序） | 打断条件 |")
    L.append("|---|---|---|---|")
    for n, sc in scheds.items():
        tl = "<br>".join(f"{i}. `{x['name']}` {x['arg']}" + (f" *{x['comment']}*" if x['comment'] else "") for i, x in enumerate(sc["tasks"], 1))
        il = "<br>".join(f"`{x['name']}`" for x in sc["interrupts"]) or "（无）"
        L.append(f"| `{n}` | {sc['line']} | {tl} | {il} |")
    L.append("")
    L.append("## 任务出现次数")
    L.append("")
    L.append("| 任务 | 用在几个计划里 |")
    L.append("|---|---|")
    for k, v in sorted(tasks.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| `{k}` | {v} |")
    L.append("")
    L.append("## 打断条件出现次数")
    L.append("")
    L.append("| 条件 | 用在几个计划里 |")
    L.append("|---|---|")
    for k, v in sorted(conds.items(), key=lambda kv: (-kv[1], kv[0])):
        L.append(f"| `{k}` | {v} |")
    with open(os.path.join(outdir, "SCHEDULES.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    if len(sys.argv) > 4:
        for mdp in sys.argv[4:]:
            fill_charts(mdp, trees)
    print(len(trees), "trees;", len(all_entries), "selectors;", len(scheds), "schedules;", len(tasks), "tasks;", len(conds), "conds")


if __name__ == "__main__":
    main()
