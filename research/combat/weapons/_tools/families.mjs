// 武器 → 机制族 的归类（W0-WEAPON-FILTER 第 2 节的机器可读版）。
export const FAMILIES = {
  'auto-ballistic': { title: '全自动 / 半自动弹道枪', weapons: {
    mp_weapon_rspn101: 'R-301', mp_weapon_r97: 'R-99', mp_weapon_car: 'C.A.R.', mp_weapon_vinson: 'Flatline',
    mp_weapon_lmg: 'Spitfire', mp_weapon_alternator_smg: 'Alternator', mp_weapon_autopistol: 'RE-45',
    mp_weapon_autopistol_fusion: 'RE-45 Fusion（活动）', mp_weapon_volt_smg: 'Volt', mp_weapon_semipistol: 'P2020' } },
  'burst-fire': { title: '点射枪', weapons: {
    mp_weapon_hemlok: 'Hemlok', mp_weapon_auto_hemlok: 'Hemlok Elite（auto_hemlok）', mp_weapon_pdw: 'Prowler',
    mp_weapon_nemesis: 'Nemesis' } },
  'shotgun-blast': { title: '霰弹 / 固定图案弹丸', weapons: {
    mp_weapon_shotgun: 'EVA-8', mp_weapon_mastiff: 'Mastiff', mp_weapon_energy_shotgun: 'Peacekeeper',
    mp_weapon_shotgun_pistol: 'Mozambique', mp_weapon_doubletake: 'Triple Take' } },
  'sniper-marksman': { title: '狙击 / 精确射手', weapons: {
    mp_weapon_sniper: 'Kraber', mp_weapon_dmr: 'Longbow', mp_weapon_sentinel: 'Sentinel', mp_weapon_g2: 'G7 Scout',
    mp_weapon_wingman: 'Wingman', mp_weapon_defender: 'Charge Rifle' } },
  'charge-spinup': { title: '充能门槛 / 转速爬升 / 过热', weapons: {
    mp_weapon_energy_ar: 'Havoc', mp_weapon_esaw: 'Devotion', mp_weapon_dragon_lmg: 'Rampage',
    mp_weapon_lstar: 'L-STAR', mp_weapon_3030: '30-30 Repeater', mp_weapon_bow: 'Bocek' } },
  'special-energy': { title: '特殊能量武器（模式 / 活动）', weapons: {
    mp_weapon_buster_rifle: 'Buster Rifle', mp_weapon_raygun: 'Ray Gun', mp_weapon_instagib: 'Instagib',
    mp_weapon_epg: 'EPG', mp_weapon_epg_tethered: 'EPG Tethered', mp_weapon_charge_gauntlet: 'Charge Gauntlet',
    mp_weapon_arc_bolt: 'Arc Bolt', mp_weapon_arc_wave: 'Arc Wave', mp_weapon_defender_sustained: 'Defender Sustained' } },
  'melee': { title: '近战', weapons: {
    mp_weapon_melee_survival: '拳头（持握）', melee_pilot_emptyhanded: '拳头（出招）', mp_weapon_titan_sword: 'Titan Sword',
    mp_weapon_power_sword: 'Power Sword', mp_weapon_wraith_kunai_primary: 'Wraith 传家宝（持握，代表）', melee_wraith_kunai: 'Wraith 传家宝（出招，代表）' } },
  'rampart-sheila-weapon': { title: 'Rampart Sheila 枪械调参', weapons: {
    mp_weapon_mobile_hmg: 'Sheila 手持', mp_weapon_mounted_turret_weapon: 'Sheila 炮台' } },
  'vantage-sniper-weapon': { title: 'Vantage 大招狙击枪', weapons: { mp_ability_sniper_ult: 'Sniper Mark' } },
  'npc-weapons': { title: 'NPC 武器', weapons: {
    npc_weapon_hemlok: 'NPC Hemlok', npc_weapon_lstar: 'NPC L-STAR', npc_weapon_shotgun: 'NPC 霰弹',
    npc_weapon_energy_shotgun: 'NPC 能量霰弹', npc_weapon_super_spectre: 'Super Spectre 榴弹',
    npc_weapon_spider_jungle: 'Spider 喷吐', npc_weapon_boss_beam: 'Boss 光束', npc_weapon_boss_turret_rockets: 'Boss 炮台火箭',
    npc_weapon_plasma_cannon_overcharged: '等离子炮', npc_weapon_goliath_throw: 'Goliath 投掷', npc_weapon_nessie: 'Nessie', npc_weapon_thermite_grenade: 'NPC 铝热' } },
};
