#!/usr/bin/env node
// 把 field-check.mjs 的 TSV（列序：ds exe、server.dll、client exe）转成 _shared/W-S3-FIELD-CHECK.md。
// 用法：node gen-field-check-md.mjs <tsv> <输出 md>
import fs from 'node:fs';

const [tsv, out] = process.argv.slice(2);
const rows = fs.readFileSync(tsv, 'utf8').trim().split(/\r?\n/).slice(1).map((l) => {
  const [field, n, ds, sdk, client, script, ex] = l.split('\t');
  return { field, n: +n, ds, sdk, client, script, ex };
});
const noise = /^(On[A-Z]|fx_|sound|sfx|ui\d|rui|bodygroup|activitymodifier|ap_|dof_|hud|menu)|sound|effect|_icon|color|anim|hud|_fx|state_text|comms|hint|ping|consumable_name|full_text|bodygroup|chasecam|haptics|attachment|holster_|sway_|longdesc|flyout|body_type|printname|desc/;
const play = rows.filter((r) => !noise.test(r.field));
const table = (list) => '| 字段 | 用到的武器文件数 | S21 客户端 | 脚本读它 | 例子 |\n|---|---|---|---|---|\n' + list.map((r) => `| \`${r.field}\` | ${r.n} | ${r.client === 'y' ? '有' : '无'} | ${r.script === 'y' ? '是' : '否'} | ${r.ex.split(',').slice(0, 2).map((e) => `\`${e}\``).join('、')} |`).join('\n') + '\n';
const native = play.filter((r) => r.ds === 'y');
const sdkOnly = play.filter((r) => r.ds !== 'y' && r.sdk !== 'n');
const noServerScript = play.filter((r) => r.ds !== 'y' && r.sdk === 'n' && r.script === 'y');
const noServerNoScript = play.filter((r) => r.ds !== 'y' && r.sdk === 'n' && r.script !== 'y');
const s = `# 公共部件 W：S21 武器字段在服务端归谁处理（静态核对）

自动生成：\`_tools/field-check.mjs\` + \`_tools/gen-field-check-md.mjs\`。2026-11-01，只读文件，没启动游戏。

**更正**：这份记录第一版只搜了 \`r5apex_ds.exe\`，得出"energize、heat 在 dedi 上推断不工作"。**这个结论错了**：SDK 的 \`server.dll\` 把它们补回来了。现在的版本三个二进制都搜。

**方法**：把所有 \`mp_weapon_* / npc_weapon_* / melee_* / mp_ability_*\` 的 \`.txt\` 字段名，在本地 \`r5apex_ds.exe\`（S3 dedi）、\`server.dll\`（SDK）、\`r5apex.exe\`（S21 客户端）里搜索，再看 \`vscripts\` 里有没有这个词。源码核对用 \`research-src/s21-r5sdk/src/game/\`（提交 10077bb）；**没有核对这份源码和已安装的 \`server.dll\` 是不是同一版**。

**怎么读**：
- "SDK 补的"这一组只代表字符串在 server.dll 里，可能只是读入或别名。上面关键结论里写了的才核对过源码。
- 这是字符串证据，不是行为证据。"SDK 补的"只说明有人写了代码，和 S21 正版一样不一样要进游戏测。见 \`../W1-SUMMARY.md\`。
- 已滤掉音效、特效、UI、\`ap_*\` 等非玩法字段。
- 数据只有一份：本地安装的 \`platform/scripts/weapons/*.txt\` 和 \`research-src\` 的玩法字段完全相同（\`_tools/diff-builds.mjs\`，330 个文件相同），差别只有 \`research-src\` 多 21 个 \`*_og.txt\`（本地安装没有）。\`viewkick_patterns.txt\`、\`blast_patterns.txt\`、\`vscripts/weapons/\` 忽略行尾后也完全相同。所以 S21 和 S3 的差异不在数据文件，在**服务端谁来执行这些字段**。

统计（玩法字段）：S3 引擎原生认 ${native.length}；S3 不认、SDK 补 ${sdkOnly.length}；服务端都不认但脚本读 ${noServerScript.length}；服务端都不认、脚本也不读 ${noServerNoScript.length}。

## 关键结论

| 机制 | 证据 | 含义 |
|---|---|---|
| Energize（Rampage、Sentinel） | \`energize.cpp\`（\`sdk_energize_bridge\` 默认 1）；\`ForceEnergizeState\` 在 \`server.dll\` 里 | SDK 重写，待实测 |
| Heat（Nemesis） | \`shared/weapon_heat.cpp:384-392\` 读 \`has_heat_decay\`、\`heat_per_bullet\`、\`heat_mod_var0\`；\`sdk_weapon_heat_modvar_write\` 默认 1（\`:38\`） | SDK 重写，待实测。\`mp_weapon_nemesis.txt:44\` 的回调注释仍然成立 |
| 点射 | \`bridge_burst_fire_seed\` 注释说 S3 服务端自己不给 \`m_burstFireCount\` 赋值（\`weapon_heat.cpp:44-47\`） | **S3 原生的点射是缺的，SDK 补上**。默认开 |
| 满蓄力保持 | \`bridge_charge_hold_when_full\`（\`weapon_heat.cpp:51\`）：引擎没这个设置 | SDK 补 |
| 蓄力下限 | \`bridge_charge_min_required\`（\`weapon_heat.cpp:56\`） | SDK 补（Havoc 门槛靠它） |
| 过热冷却 | \`bridge_charge_overheat_cooldown\`（\`weapon_heat.cpp:61\`） | SDK 补，默认 1 |
| 扩散下限 | \`server/weapon_kv_s21_ext.cpp:175\` 读 \`spread_min_kick\`；\`server/bridge_zoom_gate.cpp:757-766\` 对 \`spread_min_kick ≥ 0\` 的武器打警告 "dedi cannot reproduce this S21 term" | SDK **只读入，没发现使用方**，唯一用到它的是这条警告。Sheila 的值是 −2.5，不触发警告，要实测 |
| 分段重力、空气阻力 | \`weapon_kv_s21_ext.cpp\` 读 \`projectile_gravity_scale_2 / _final\`、\`projectile_air_friction*\`（头文件写"S21-only weapon KV keys the dedi schema cannot hold"） | SDK 读进来，但这个文件之外**没发现使用方**（flGravityScale2、flAirFriction2、flGravityScaleFinal）。推断不影响 dedi 弹道，要实测 |
| 蓄力倍伤 | \`charge_additional_damage_multiplier\` 在 SDK 里只是别名（\`shared/weapon_script_vars.cpp:3243-3246\`） | **最可能的真差异**：30-30 ×1.4 推断没生效 |
| 图案数量 | S3 上限 8，SDK 提到 128（\`server/r1/blast_pattern.h:15-16\`）；\`blast_patterns.txt\` 有 14 个 | 排在第 8 之后的图案依赖这个补丁 |
| 转速爬升、三段衰减 | \`fire_rate_max*\`、\`damage_very_far_value\` 在 S3 原生认 | 原生 |
| 脚本实现的 hop-up | \`kinetic_*\`、\`smart_reload_*\`、\`marksmans_tempo_*\`、\`projectile_spread_choke_frac_*\`、\`blast_pattern_ads_scale\` 引擎都不认，脚本读 | 不依赖引擎版本 |

## S3 不认、SDK \`server.dll\` 补的

${table(sdkOnly)}
## 服务端都不认，脚本读

${table(noServerScript)}
## 服务端都不认，脚本也不读（数据里写了，服务端推断无效；客户端可能用）

${table(noServerNoScript)}`;
fs.writeFileSync(out, s);
