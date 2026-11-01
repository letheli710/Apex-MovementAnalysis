#!/usr/bin/env node
// 生成 weapons/<族>/PARAMS.md：每把枪的玩法字段 + 行号、crate / og 差异、配件和 hop-up 的玩法覆盖。
// 用法：node gen-params.mjs <scripts/weapons 目录> <weapons 输出目录>
import fs from 'node:fs';
import path from 'node:path';
import { parseKV } from './extract-weapons.mjs';
import { FAMILIES } from './families.mjs';

const [srcDir, outDir] = process.argv.slice(2);
const cache = {};
function load(n) {
  if (n in cache) return cache[n];
  const p = path.join(srcDir, n + '.txt');
  if (!fs.existsSync(p)) return (cache[n] = null);
  const { root } = parseKV(fs.readFileSync(p, 'utf8'));
  const top = Object.values(root.blocks)[0];
  const mods = {};
  for (const [m, b] of Object.entries(top.blocks.Mods?.blocks ?? {})) mods[m] = b;
  return (cache[n] = { fields: top.fields, mods });
}

const GROUPS = [
  ['射击', /^(fire_mode|is_semi_auto|fire_rate|fire_rate_max|fire_rate_max_time_speedup|fire_rate_max_time_cooldown|burst_fire_count|burst_fire_delay|burst_fire_allow_ads|rechamber_time|primary_attack_ignores_spread|projectiles_per_shot|blast_pattern|blast_pattern_zero_distance|blast_pattern_default_scale|projectile_blast_pattern_zero_distance|projectile_spread_choke_frac_\d|OnWeaponPrimaryAttack)$/],
  ['弹药', /^(ammo_clip_size|ammo_pool_type|ammo_per_shot|ammo_min_to_fire|ammo_stockpile_max|ammo_default_total|ammo_no_remove_from_clip|ammo_no_remove_from_stockpile|uses_ammo_pool|ammo_drains_to_empty_on_fire|regen_ammo_refill_rate|regen_ammo_refill_start_delay|regen_ammo_forced_delay|reload_enabled|empty_reload_only|reload_is_segmented|reloadsegment_time_loop|reloadsegment_time_end|reloadsegmentempty_time_end|ammo_size_segmented_reload|kinetic_ammo_to_load)$/],
  ['时间', /^(reload_time|reloadempty_time|reload_time_late1|reloadempty_time_late1|deploy_time|deployfirst_time|holster_time|raise_time|lower_time|zoom_time_in|zoom_time_out|zoom_fov)$/],
  ['伤害', /^(damage_near_value|damage_far_value|damage_very_far_value|damage_near_distance|damage_far_distance|damage_very_far_distance|damage_headshot_scale|damage_leg_scale|damage_shield_scale|damage_unshielded_scale|critical_hit|critical_hit_damage_scale|allow_headshots|headshot_distance|damage_type|damage_flags|impulse_force|explosion_damage|explosion_inner_radius|explosionradius|pass_through_depth|pass_through_damage_preserved_scale|melee_\w+|npc_damage_near_value|npc_damage_far_value|npc_damage_near_distance|npc_damage_far_distance|npc_max_range|npc_min_range|npc_max_engage_range|npc_min_engage_range|npc_rest_time_\w+|npc_min_burst|npc_max_burst|npc_pre_fire_delay|npc_pre_fire_delay_interval|npc_full_auto_vs_heavy_armor)$/],
  ['弹道', /^(ballistic_type|projectile_launch_speed|projectile_launch_speed_full_charge|bolt_gravity_enabled|projectile_gravity_scale|bolt_zero_distance|bolt_hitsize\w*|projectile_lifetime|projectile_drag_coefficient|projectile_ricochet_max_count|projectile_speed_reduction_factor|projectile_bounce_damage_reduction_scale)$/],
  ['扩散', /^spread_/],
  ['后坐', /^(viewkick_pattern|viewkick_spring|viewkick_pitch_base|viewkick_pitch_random|viewkick_pitch_softScale|viewkick_pitch_hardScale|viewkick_yaw_base|viewkick_yaw_random|viewkick_yaw_softScale|viewkick_yaw_hardScale|viewkick_air_scale_ads|viewkick_move_scale|viewkick_duck_scale|viewkick_perm_\w+)$/],
  ['充能 / 热', /^(charge_time|charge_levels|charge_level_base|charge_cooldown_time|charge_cooldown_delay|charge_cooldown_time_post_fire|charge_end_forces_fire|charge_require_input|charge_remain_full_when_fired|charge_allow_hold_when_full|charge_maintained_until_fired|charge_is_triggered_by_ADS|charge_curve_coefficients|charge_additional_damage_multiplier|charge_attack_min_charge_required|charge_overheat\w*|charge_overheats_when_full|heat_\w+|has_heat_decay|player_overheat_per_bullet|does_player_overheat|sustained_discharge_\w+|sustained_laser_(enabled|radius|range)|energized_duration|energized_consumable_needed_amount|energized_time_consumed_per_shot|has_energized|preburn_duration|marksmans_tempo_\w+)$/],
  ['移动', /^(move_speed_modifier|ads_move_speed_scale|primary_fire_does_not_block_sprint)$/],
];
const MOD_GAMEPLAY = new RegExp([
  'ammo_', 'fire_rate', 'fire_mode', 'is_semi_auto', 'burst_', 'damage_', 'critical_', 'headshot', 'reload', 'deploy_time', 'holster_time', 'raise_time', 'lower_time',
  'zoom_time', 'zoom_fov$', 'spread_', 'viewkick_(pattern|pitch|yaw|spring|scale)', 'viewdrift', 'projectile_launch_speed', 'projectile_gravity', 'projectiles_per_shot', 'blast_pattern', 'bolt_hitsize', 'bolt_gravity', 'charge_', 'rechamber', 'regen_ammo',
  'move_speed', 'ads_move', 'explosion', 'kinetic_', 'smart_reload', 'heat_', 'has_energized', 'energized_', 'pass_through', 'impulse', 'hammer_point', 'shock_', 'marksmans_', 'primary_attack_ignores',
].join('|'));
const cell = (s) => String(s).replace(/\|/g, '\\|');

function weaponSection(name, label) {
  const w = load(name);
  if (!w) return `## ${label}（\`${name}\`）\n\n本地没有 \`${name}.txt\`。\n\n`;
  let s = `## ${label}（\`weapons/${name}.txt\`）\n\n`;
  for (const [g, re] of GROUPS) {
    const rows = Object.entries(w.fields).filter(([k]) => re.test(k)).sort((a, b) => a[1].line - b[1].line);
    if (!rows.length) continue;
    s += `**${g}**：` + rows.map(([k, v]) => `\`${k}\` ${cell(v.v)} (L${v.line})`).join('；') + '\n\n';
  }
  for (const [suf, nm] of [['_crate', '补给箱版'], ['_og', 'OG 版']]) {
    const o = load(name + suf);
    if (!o) continue;
    const diff = [];
    for (const [k, v] of Object.entries(o.fields)) {
      if (!GROUPS.some(([, re]) => re.test(k))) continue;
      if (w.fields[k]?.v !== v.v) diff.push(`\`${k}\` ${cell(w.fields[k]?.v ?? '—')} → ${cell(v.v)} (L${v.line})`);
    }
    if (diff.length) s += `**${nm}差异**（\`${name}${suf}.txt\`）：` + diff.join('；') + '\n\n';
  }
  const mods = Object.entries(w.mods)
    .map(([m, b]) => [m, b.line, Object.entries(b.fields).filter(([k]) => MOD_GAMEPLAY.test(k))])
    .filter(([, , f]) => f.length);
  if (mods.length) {
    s += `**Mods 的玩法覆盖**（\`*x\` 乘、\`++x\` 加，其余直接替换）：\n\n| mod | 行 | 覆盖 |\n|---|---|---|\n`;
    for (const [m, l, f] of mods) s += `| \`${m}\` | ${l} | ${f.map(([k, v]) => `\`${k}\` ${cell(v.v)}`).join('；')} |\n`;
    s += '\n';
  }
  const empty = Object.entries(w.mods).filter(([, b]) => !Object.entries(b.fields).some(([k]) => MOD_GAMEPLAY.test(k))).map(([m]) => m);
  if (empty.length) s += `没有玩法字段的 mod（只改外观或靠脚本 \`HasMod\`）：${empty.map((m) => `\`${m}\``).join('、')}\n\n`;
  return s;
}

for (const [fam, def] of Object.entries(FAMILIES)) {
  const dir = path.join(outDir, fam);
  fs.mkdirSync(dir, { recursive: true });
  let s = `# ${def.title}：参数全表（自动生成）\n\n由 \`weapons/_tools/gen-params.mjs\` 从 \`research-src/s21-platform/scripts/weapons/*.txt\` 生成，不要手改。\`L\` 是行号，字段名就是来源字段。全部是 S21 数据文件里的值；S3 dedi 的差异看同目录 \`SYSTEM.md\`。\n\n`;
  for (const [n, l] of Object.entries(def.weapons)) s += weaponSection(n, l);
  fs.writeFileSync(path.join(dir, 'PARAMS.md'), s);
}

// 跨武器比较表
let cmp = `# 全武器参数比较（自动生成）\n\n由 \`_tools/gen-params.mjs\` 生成。值来自各 \`.txt\` 的同名字段。名义 DPS = \`fire_rate × damage_near_value\`，不算点射间隔、充能、拉栓、弹丸数和距离衰减，只用来排序。\n\n| 族 | 武器 | 射速 | 近伤 | 远伤 | 极远伤 | 近距 u | 远距 u | 爆头 | 腿 | 弹匣 | 弹种 | 换弹 s | 空换 s | 弹速 u/s | 重力 | 点射 | 弹丸 | 名义 DPS |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n`;
const short = (x) => (/^-?\d+\.\d+$/.test(x) ? String(parseFloat(x)) : x);
for (const [fam, def] of Object.entries(FAMILIES)) {
  if (['melee', 'npc-weapons'].includes(fam)) continue;
  for (const [n, l] of Object.entries(def.weapons)) {
    const w = load(n);
    if (!w) continue;
    const g = (k) => short(w.fields[k]?.v ?? '—');
    const r = parseFloat(g('fire_rate')), d = parseFloat(g('damage_near_value'));
    const dps = isFinite(r) && isFinite(d) ? (r * d).toFixed(0) : '—';
    cmp += `| ${fam} | ${l} | ${g('fire_rate')} | ${g('damage_near_value')} | ${g('damage_far_value')} | ${g('damage_very_far_value')} | ${g('damage_near_distance')} | ${g('damage_far_distance')} | ${g('damage_headshot_scale')} | ${g('damage_leg_scale')} | ${g('ammo_clip_size')} | ${g('ammo_pool_type')} | ${g('reload_time')} | ${g('reloadempty_time')} | ${g('projectile_launch_speed')} | ${g('projectile_gravity_scale')} | ${g('burst_fire_count')} | ${g('projectiles_per_shot')} | ${dps} |\n`;
  }
}
fs.mkdirSync(path.join(outDir, '_shared'), { recursive: true });
fs.writeFileSync(path.join(outDir, '_shared', 'W-PARAM-COMPARE.md'), cmp);
