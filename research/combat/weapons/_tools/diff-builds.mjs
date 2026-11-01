#!/usr/bin/env node
// 比较两份 scripts/weapons 目录的同名 .txt（字段和 Mods）。用来核对 research-src 和本地安装是不是同一份数据。
// 用法：node diff-builds.mjs <目录 A> <目录 B> [只看字段的正则]
import fs from 'node:fs';
import path from 'node:path';
import { parseKV } from './extract-weapons.mjs';

const [a, b, re] = process.argv.slice(2);
const filter = re ? new RegExp(re) : /./;
const names = new Set([...fs.readdirSync(a), ...fs.readdirSync(b)].filter((f) => f.endsWith('.txt')));
const load = (d, f) => {
  const p = path.join(d, f);
  if (!fs.existsSync(p)) return null;
  const top = Object.values(parseKV(fs.readFileSync(p, 'utf8')).root.blocks)[0];
  return top ?? { fields: {}, blocks: {} };
};
let same = 0;
for (const f of [...names].sort()) {
  const x = load(a, f), y = load(b, f);
  if (!x || !y) { console.log(`${f}\t只在 ${x ? 'A' : 'B'}`); continue; }
  const out = [];
  for (const k of new Set([...Object.keys(x.fields), ...Object.keys(y.fields)])) {
    if (!filter.test(k)) continue;
    if (x.fields[k]?.v !== y.fields[k]?.v) out.push(`${k}: ${x.fields[k]?.v ?? '—'} -> ${y.fields[k]?.v ?? '—'}`);
  }
  const mx = x.blocks.Mods?.blocks ?? {}, my = y.blocks.Mods?.blocks ?? {};
  for (const m of new Set([...Object.keys(mx), ...Object.keys(my)])) {
    if (!mx[m] || !my[m]) { out.push(`mod ${m}: 只在 ${mx[m] ? 'A' : 'B'}`); continue; }
    for (const k of new Set([...Object.keys(mx[m].fields), ...Object.keys(my[m].fields)])) {
      if (!filter.test(k)) continue;
      if (mx[m].fields[k]?.v !== my[m].fields[k]?.v) out.push(`mod ${m}.${k}: ${mx[m].fields[k]?.v ?? '—'} -> ${my[m].fields[k]?.v ?? '—'}`);
    }
  }
  if (out.length) console.log(`${f}\t${out.length}\t${out.slice(0, 12).join(' ; ')}`);
  else same++;
}
console.log(`完全相同（按过滤）：${same}`);
