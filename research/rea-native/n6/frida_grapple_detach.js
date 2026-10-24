// N6 grapple detach probe (Frida, read-only: hooks only log, nothing is changed).
// For every call of the native grapple pull step it records which helper functions
// the step called before returning, so a "detach" return (1) can be traced to its
// branch. It also polls the player's grapple-active byte (+0x2d60) and the C3 grapple
// state so a detach decided outside the pull step shows up on its own.
//
//   14066fb60  pull step      returns 1 = detach this command (arg 4 = player)
//   14066f600  detach rules   (contact, away speed > 500, low-speed timeouts)
//   140672580  hook direction / distance helper (proximity and rope-length checks)
//   140672640  hooked entity getter (entity checks)
//   1405ac0e0  impact check (proximity branch)
//   14066f570  move with trace (window check)
//   14066e510  hooked-entity side check
// Addresses are Ghidra (image base 0x140000000) of r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const BASE = mod.base;
const GH = ptr('0x140000000');
const at = (a) => BASE.add(ptr(a).sub(GH));
const rel = (p) => '0x' + p.sub(BASE).add(GH).toString(16);
const t0 = Date.now();
const now = () => (Date.now() - t0) / 1000;
let player = null;
let depth = 0;
let trail = [];
let calls = 0;

const HELPERS = {
  '0x14066f600': 'rules', '0x140672580': 'dir', '0x140672640': 'ent', '0x1405ac0e0': 'impact',
  '0x14066f570': 'move', '0x14066e510': 'side'
};
for (const a in HELPERS) {
  const name = HELPERS[a];
  Interceptor.attach(at(a), {
    onEnter() { if (depth > 0) trail.push(name); },
    onLeave(ret) { if (depth > 0 && name === 'rules') trail.push('rules=' + (ret.toInt32() & 0xff)); }
  });
}

Interceptor.attach(at('0x14066fb60'), {
  onEnter(args) { this.pl = args[4]; depth++; trail = []; calls++; },
  onLeave(ret) {
    depth--;
    if (!this.pl.isNull()) player = this.pl;
    if ((ret.toInt32() & 0xff) !== 0) send({ ev: 'fb60_detach', t: now(), trail: trail.join(' '), ra: rel(this.returnAddress) });
  }
});

let last = -1;
setInterval(() => {
  if (player === null) return;
  let v;
  try { v = player.add(0x2d60).readU8(); } catch (e) { return; }
  if (v !== last) {
    send({ ev: 'flag', t: now(), active: v, fb60_calls: calls });
    last = v;
  }
}, 1);
send({ ev: 'ready', base: BASE.toString() });
