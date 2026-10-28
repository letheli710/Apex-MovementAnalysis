// F6 landing-kick seed probe (Frida, read-only: hooks only log, nothing is changed).
// Land_ViewKick (0x140a35750) draws its three random numbers by re-seeding the shared uniform stream with SeedMix(base, salt)
// (0x140ad55b0, salts 0x76704c58 / 59 / 5a) and drawing one value in [-0.5, 0.5]. This logs every SeedMix call with those salts:
// the base seed (the global at 0x1419832d0), the salt and the mixed seed, plus the base seed every time Land_ViewKick is entered, so the
// base can be matched to the landing command numbers of the HSD.MoveDiag log (k-th kick <-> k-th landing).
// Rows go to OUT_PATH (set when the script is loaded): [t, kind, base, salt, mixed]. Addresses are Ghidra (image base 0x140000000) of
// r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const OUT_PATH = 'OUT_PATH_HERE';
const out = new File(OUT_PATH, 'w');
out.write('t,kind,base,salt,mixed\n');
const SALTS = [0x76704c58, 0x76704c59, 0x76704c5a];
const seedGlobal = at('0x1419832d0');
let n = 0;

Interceptor.attach(at('0x140a35750'), {
  onEnter() {
    out.write([((Date.now() - t0) / 1000).toFixed(4), 'kick', seedGlobal.readU32(), '', ''].join(',') + '\n');
    out.flush();
    send({ kick: ++n });
  }
});
Interceptor.attach(at('0x140ad55b0'), {
  onEnter(args) {
    this.salt = args[1].toUInt32() >>> 0;
    this.base = args[0].toUInt32() >>> 0;
  },
  onLeave(ret) {
    if (SALTS.indexOf(this.salt) < 0) return;
    out.write([((Date.now() - t0) / 1000).toFixed(4), 'mix', this.base, this.salt, ret.toInt32()].join(',') + '\n');
  }
});
send({ ready: true });
