#!/usr/bin/env node
// 把 research-src/s21-platform/scripts/weapons/*.txt（KeyValues 格式）解析成 JSON + 字段行号。
// 用法：node extract-weapons.mjs <scripts/weapons 目录> <输出 json>
// 只解析，不改源文件。行内和整行 // 注释会单独收进 comments（用来找 S3 / dedi 补丁说明）。
import fs from 'node:fs';
import path from 'node:path';

export function parseKV(text) {
  const lines = text.split(/\r?\n/);
  const root = { fields: {}, blocks: {} };
  const stack = [root];
  const comments = [];
  let pendingKey = null;
  lines.forEach((raw, i) => {
    const ln = i + 1;
    let s = raw;
    const c = s.match(/^(?:[^"]|"[^"]*")*?\/\/(.*)$/);
    if (c) { comments.push({ line: ln, text: c[1].trim() }); s = s.slice(0, s.length - c[1].length - (raw.length - raw.trimEnd().length) - 2 + (raw.length - raw.trimEnd().length)); }
    const toks = s.match(/"[^"]*"|\{|\}|[^\s{}"]+/g) || [];
    let j = 0;
    while (j < toks.length) {
      const t = toks[j];
      const top = stack[stack.length - 1];
      if (t === '{') {
        const name = pendingKey ?? '_anon';
        const b = { fields: {}, blocks: {}, line: ln };
        top.blocks[name] = b; stack.push(b); pendingKey = null; j++;
      } else if (t === '}') {
        if (stack.length > 1) stack.pop(); pendingKey = null; j++;
      } else {
        const k = t.replace(/^"|"$/g, '');
        const n = toks[j + 1];
        if (n === undefined || n === '{') { pendingKey = k; j++; }
        else if (n === '}') { pendingKey = k; j++; }
        else { top.fields[k] = { v: n.replace(/^"|"$/g, ''), line: ln }; pendingKey = null; j += 2; }
      }
    }
  });
  return { root, comments };
}

if (process.argv[1] && process.argv[1].endsWith('extract-weapons.mjs')) {
  const [dir, out] = process.argv.slice(2);
  const res = {};
  for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith('.txt')) continue;
    const { root, comments } = parseKV(fs.readFileSync(path.join(dir, f), 'utf8'));
    const top = Object.values(root.blocks)[0];
    if (!top) continue;
    const mods = {};
    for (const [m, b] of Object.entries(top.blocks.Mods?.blocks ?? {})) mods[m] = { line: b.line, fields: b.fields };
    res[f.replace(/\.txt$/, '')] = { fields: top.fields, mods, comments };
  }
  fs.writeFileSync(out, JSON.stringify(res));
  console.log(Object.keys(res).length, 'files');
}
