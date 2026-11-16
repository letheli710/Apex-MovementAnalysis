#!/usr/bin/env python3
"""从手册各章的"验收"段摘出合格线，生成 handbook/tables/pass-lines.tsv（hb-ch10，2026-11-15）。

为什么要有它：pass-lines.tsv 的 PL-056 以后是从 02 – 09、12 章每一项"#### 验收"段里写着"合格线"的那一句逐条摘的。
章节以后改了合格线，表就过时了。重跑这个脚本，表就跟着章节更新，不用手抄。

表分两部分：
  1. 手写行：pass-lines.tsv 里"章"列是 10 或 11 的行（总口径、脚本容差、技能和 AI、单位、泰坦模型、TF2、流水线、
     重建检验）。它们不在各章的"验收"段里，所以脚本**原样保留**，从现有的 pass-lines.tsv 读回来。要改它们就直接改 TSV。
  2. 摘出来的行：02、03、04、05、06、07、08、09、12 章。每一个 "### x.y" / "## x.y" 项的 "#### 验收" 段里，凡是含
     "合格线" 的一行算一条：
       - "合格线：…"、"合格线（…）：…" → 取冒号后面的话（括号里的说明留在前面）；
       - "合格线建议…" → 前面加"（建议）"；
       - 别的写法（"…以后才有合格线"、"没有合格线"）→ 整行原样保留，提醒这里是空的。
     "检查"列是同一个验收段里出现的 `类名.方法名` 和 `xxx.py`（按出现顺序，最多 6 个）。
  编号 PL-001 起，手写行在前，摘出来的行按章号、按章内顺序在后。

怎么跑（在研究仓库的任意 checkout 根目录，Python 3，只用标准库）：
    py -3 handbook/tables/extract_pass_lines.py                 # 读工作区里的 handbook/*.md（各章合进同一分支以后用这个）
    py -3 handbook/tables/extract_pass_lines.py --from-branches # 各章还在自己的分支上：读 origin/handbook/chNN（先 git fetch）
    py -3 handbook/tables/extract_pass_lines.py --pinned        # 读 11-14 生成时用的那几个提交（复现当时的 185 行）
    py -3 handbook/tables/extract_pass_lines.py --ref origin/handbook/base   # 所有章从同一个分支 / 提交读
    加 --check：不写文件，只比较生成结果和现有 TSV，不一样就打印差别并退出码 1。
    加 --out <文件>：写到别处（默认覆盖 handbook/tables/pass-lines.tsv）。

什么时候重跑：
  - 任何一章的"验收"段改了（加了项、改了合格线、改了测试名），或者各章合进 handbook/base 以后；
  - 重跑后用 git diff 看 pass-lines.tsv 变了哪些行；PL 编号可能整体后移（编号只是行号，引用时请同时写章节 §）；
  - 改完同步更新 11 §11.6 的摘要表里写到的 PL 号范围和行数。
"""
import argparse, csv, io, os, re, subprocess, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
HB = os.path.dirname(HERE)                 # handbook/
REPO = os.path.dirname(HB)
TSV = os.path.join(HERE, 'pass-lines.tsv')

# (文件名, 章号, 领域, 默认分支, 11-14 生成时的提交)
CHAPTERS = [
    ('02-foundation.md', '02', '底层', 'handbook/ch02', 'a5b1362'),
    ('03-ground-air-jump.md', '03', '地面空中跳跃', 'handbook/ch03', '4ab0007'),
    ('04-slide-mantle.md', '04', '滑铲翻越', 'handbook/ch04', '32790bc'),
    ('05-wall-external.md', '05', '墙和外力技能', 'handbook/ch05', '3be1917'),
    ('06-momentum-arbitration-input.md', '06', '动量仲裁输入', 'handbook/ch06', '63dad4f'),
    ('07-camera.md', '07', '镜头', 'handbook/ch07', '10ae546'),
    ('08-body-animation.md', '08', '身体动画', 'handbook/ch08', '16190c0'),
    ('09-combat-feel.md', '09', '战斗手感', 'handbook/ch09', 'd4c4944'),
    ('12-titan-motor.md', '12', '泰坦电机', 'handbook/ch08', '16190c0'),
]
HEADER = ['id', '领域', '章', '节', '量', '合格线', '检查', '出处', '在哪', '来源']
MANUAL_CHAPTERS = {'10', '11'}

TEST = re.compile(r'`([A-Z][A-Za-z0-9]+\.[A-Z][A-Za-z0-9]+)`')
SCRIPT = re.compile(r'`([A-Za-z0-9_]+\.py)')
HEAD = re.compile(r'^(#{2,3}) +(\d+\.\d+|[A-Z]\.\d+) +(.*)$')
PASS = re.compile(r'合格线(\s*[（(][^）)]*[)）])?\s*[：:]')


def read_chapter(fn, ref):
    if ref is None:
        with open(os.path.join(HB, fn), encoding='utf-8') as f:
            return f.read()
    out = subprocess.run(['git', '-C', REPO, 'show', f'{ref}:handbook/{fn}'], capture_output=True)
    if out.returncode != 0:
        sys.exit(f'读不到 {ref}:handbook/{fn}：{out.stderr.decode("utf-8", "replace").strip()}')
    return out.stdout.decode('utf-8')


def pass_line(l):
    m = PASS.search(l)
    if m:
        pl = l[m.end():].strip()
        if m.group(1):
            pl = m.group(1).strip() + ' ' + pl
    elif '合格线建议' in l:
        pl = '（建议）' + l[l.find('合格线建议') + 5:].lstrip('：: ')
    else:
        pl = l.strip().lstrip('-').strip()
    pl = pl.replace('\t', ' ').replace('\\|', '|').strip()
    return re.sub(r'\*\*', '', pl)


def extract(text, no, area, where):
    rows, sec, title, inacc, block = [], None, None, False, []

    def flush():
        if not sec or not block:
            return
        checks = []
        for l in block:
            for t in TEST.findall(l) + SCRIPT.findall(l):
                if t not in checks:
                    checks.append(t)
        for l in block:
            if '合格线' in l:
                rows.append([area, no, sec, title, pass_line(l), '；'.join(checks[:6]) or '—',
                             f'{no} §{sec}', where, '章节'])

    for l in text.split('\n'):
        m = HEAD.match(l)
        if m:
            flush()
            block, inacc = [], False
            sec, title = m.group(2), re.sub(r'[`*]', '', m.group(3)).strip()
            continue
        if l.startswith('#### '):
            inacc = l.strip() == '#### 验收'
            continue
        if inacc:
            block.append(l)
    flush()
    return rows


def read_tsv(path):
    with open(path, encoding='utf-8', newline='') as f:
        return [r for r in csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)]


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--from-branches', action='store_true', help='读 origin/handbook/chNN')
    g.add_argument('--pinned', action='store_true', help='读 11-14 生成时的提交')
    g.add_argument('--ref', help='所有章从这一个分支 / 提交读')
    ap.add_argument('--check', action='store_true', help='只比较，不写')
    ap.add_argument('--out', default=TSV)
    a = ap.parse_args()

    old = read_tsv(TSV)
    if old[0] != HEADER:
        sys.exit(f'现有 TSV 的表头不对：{old[0]}')
    manual = [r[1:] for r in old[1:] if r[2] in MANUAL_CHAPTERS]

    extracted = []
    for fn, no, area, branch, pin in CHAPTERS:
        ref = f'origin/{branch}' if a.from_branches else pin if a.pinned else a.ref
        where = f'{branch}，还没合并' if (a.from_branches or a.pinned) else f'{a.ref or "工作区"}（见 handbook/README.md 目录）'
        text = read_chapter(fn, ref)
        if '#### 验收' not in text:
            sys.exit(f'{fn}（{ref or "工作区"}）里没有"#### 验收"段，像是占位文件；换 --from-branches / --ref，不写任何东西')
        extracted += extract(text, no, area, where)

    out = [HEADER] + [[f'PL-{i:03d}'] + r for i, r in enumerate(manual + extracted, 1)]
    for r in out:
        assert len(r) == len(HEADER), r
    text = ''.join('\t'.join(r) + '\n' for r in out)
    print(f'{len(out) - 1} 行：手写 {len(manual)}，摘出 {len(extracted)}', dict(Counter(r[1] for r in extracted)))

    if a.check:
        with open(TSV, encoding='utf-8', newline='') as f:
            cur = f.read()
        if cur == text:
            print('和现有 pass-lines.tsv 逐字节相同')
            return 0
        a_lines, b_lines = cur.splitlines(), text.splitlines()
        for i in range(max(len(a_lines), len(b_lines))):
            x = a_lines[i] if i < len(a_lines) else '<没有>'
            y = b_lines[i] if i < len(b_lines) else '<没有>'
            if x != y:
                print(f'第 {i + 1} 行\n  现有：{x[:160]}\n  生成：{y[:160]}')
        return 1
    with open(a.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print('写入', a.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
