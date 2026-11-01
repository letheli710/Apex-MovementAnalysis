#!/usr/bin/env node
// 查武器 .txt 用到的字段名在各 exe 里有没有（以 \0 分隔的完整字符串）。只读文件，不启动游戏。
// 没有 = 引擎不认识这个字段；脚本可能用 GetWeaponInfoFileKeyField 自己读，所以还要看 vscripts 里有没有读它。
// 用法：node field-check.mjs <scripts 目录> <exe 1> [exe 2 ...] > out.tsv
import fs from 'node:fs';
import path from 'node:path';
import { parseKV } from './extract-weapons.mjs';

const [scripts, ...exes] = process.argv.slice(2);
const wdir = path.join(scripts, 'weapons');
const usage = new Map();
const add = (f, n) => { if (!usage.has(f)) usage.set(f, new Set()); usage.get(f).add(n); };
for (const f of fs.readdirSync(wdir)) {
  if (!/^(mp_weapon|npc_weapon|melee_|mp_ability)/.test(f) || !f.endsWith('.txt')) continue;
  const n = f.replace('.txt', '');
  const top = Object.values(parseKV(fs.readFileSync(path.join(wdir, f), 'utf8')).root.blocks)[0];
  if (!top) continue;
  for (const k of Object.keys(top.fields)) add(k, n);
  for (const b of Object.values(top.blocks.Mods?.blocks ?? {})) for (const k of Object.keys(b.fields)) add(k, n);
}
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : /\.(nut|gnut)$/.test(e.name) ? [path.join(d, e.name)] : []));
const scriptText = walk(path.join(scripts, 'vscripts')).map((p) => fs.readFileSync(p, 'latin1')).join('\n');
const bins = exes.map((e) => fs.readFileSync(e).toString('latin1'));
console.log(['field', 'weapons', ...exes.map((e) => path.basename(e)), 'in_vscripts', 'examples'].join('\t'));
for (const [f, set] of [...usage].sort((a, b) => a[0].localeCompare(b[0]))) {
  const hits = bins.map((b) => (b.includes('\0' + f + '\0') ? 'y' : 'n'));
  const inScript = new RegExp(`\\b${f.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`).test(scriptText) ? 'y' : 'n';
  console.log([f, set.size, ...hits, inScript, [...set].slice(0, 4).join(',')].join('\t'));
}
