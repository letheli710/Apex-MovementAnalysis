// GN (G-5) hook parent probe (Frida, read-only: hooks only log, nothing is changed).
// The native "away > grapple_detachAwaySpeed" detach (0x14066f600) and the impact vertical boost (0x14066fb60,
// proximity branch) both run only when the entity handle at +0x148 of the pull step's 4th argument is empty.
// This logs that handle (and the +0x1560 fallback) on every hook, resolves it through the entity list, and
// records the largest radial speed away from the rope seen during the pull (v . d / |d| < 0 in 0x14066f600).
//
//   14066fb60  pull step     args: rcx GrappleData, rdx settings, r8 player, r9 hook entity, [5th] player or 0
//   14066f600  detach rules  7th arg = rope direction d (float[3]); velocity = movedata 0x1423736c4..cc
//   entity list  0x1424139b8 + (handle & 0xffff) * 32 = entity pointer, +8 = serial (handle >> 16)
// Addresses are Ghidra (image base 0x140000000) of r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const BASE = mod.base;
const GH = ptr('0x140000000');
const at = (a) => BASE.add(ptr(a).sub(GH));
const rel = (p) => (p.isNull() ? '0' : (p.compare(BASE) >= 0 && p.compare(BASE.add(mod.size)) < 0 ? '0x' + p.sub(BASE).add(GH).toString(16) : p.toString()));
const t0 = Date.now();
const now = () => (Date.now() - t0) / 1000;
const ENTS = at('0x1424139b8');
const VEL = at('0x1423736c4');

function resolve(h) {
  if (h === 0xffffffff) return { h: 'none', idx: -1, ent: '0', vt: '0' };
  const idx = h & 0xffff;
  const slot = ENTS.add(idx * 32);
  const serialOk = slot.add(8).readU32() === (h >>> 16);
  const e = serialOk ? slot.readPointer() : ptr(0);
  return { h: '0x' + (h >>> 0).toString(16), idx: idx, serialOk: serialOk, ent: e.toString(), vt: e.isNull() ? '0' : rel(e.readPointer()) };
}

let lastKey = '';
let lastH = null;
let calls = 0;
let maxAway = 0, maxToward = 0;
Interceptor.attach(at('0x14066fb60'), {
  onEnter(args) {
    calls++;
    const hook = args[3];
    let key = '', p148 = null, p1560 = null;
    try {
      p148 = resolve(hook.add(0x148).readU32());
      p1560 = resolve(hook.add(0x1560).readU32());
      key = hook.toString() + p148.h + p1560.h;
    } catch (e) { key = 'err ' + e; }
    // h of the rope direction (player +0x1de8, read by 0x140674a90): d = P0 + (0, 0, grapple_lift) - (origin + (0, 0, h + 1))
    let h = NaN;
    try { h = args[2].add(0x1de8).readFloat(); } catch (e) { }
    if (h !== lastH) { send({ ev: 'h1de8', t: now(), h: h }); lastH = h; }
    if (key !== lastKey) {
      send({ ev: 'hook', t: now(), hook: hook.toString(), hook_vt: p148 ? rel(hook.readPointer()) : '', p148: p148, p1560: p1560,
             world0: ENTS.readPointer().toString(), calls: calls, maxAway: maxAway, maxToward: maxToward });
      lastKey = key; maxAway = 0; maxToward = 0;
    }
  },
  onLeave(ret) {
    if ((ret.toInt32() & 0xff) !== 0) send({ ev: 'detach', t: now(), maxAway: maxAway, maxToward: maxToward, vz: VEL.add(8).readFloat() });
  }
});

Interceptor.attach(at('0x14066f600'), {
  onEnter(args) {
    try {
      const d = args[6];
      const dx = d.readFloat(), dy = d.add(4).readFloat(), dz = d.add(8).readFloat();
      const l = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (l < 1e-6) return;
      const vr = (dx * VEL.readFloat() + dy * VEL.add(4).readFloat() + dz * VEL.add(8).readFloat()) / l;
      if (-vr > maxAway) maxAway = -vr;
      if (vr > maxToward) maxToward = vr;
    } catch (e) { }
  },
  onLeave(ret) {
    if ((ret.toInt32() & 0xff) !== 0) send({ ev: 'rules_detach', t: now(), maxAway: maxAway });
  }
});
send({ ev: 'ready', base: BASE.toString(), world0: ENTS.readPointer().toString() });
