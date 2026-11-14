// C1-C5 animation probe (Frida, read-only: hooks only log and call read-only getters). Ghidra addresses (base 0x140000000) of r5apex_dx12.exe.
// Built from gun-measure/tools/probe.js + MOVEMENT-ANIMATION section 12.
// frames.csv, one line per first-person CalcView (0x1407f2bb0):
//   w = Date.now ms (same clock as Python time.time), ct10 / ct28 = globals +0x10 / +0x28
//   zf, vx vy vz = player +0x170, clip = weapon +0x1590, ws = weapon state +0x15a4
//   vmF vmR vmU = view model origin in camera axes, vmaP vmaY vmaR = its angles minus camera angles (0x14085c3e0 args)
//   cyc = view model +0xf4, seq = +0xe44
//   pp_<name> = pose parameter, normalized 0..1, view model +0xe54 + 4*index; index tables at +0x1cfc.. and +0x18e0.. (0x1408596d0)
//   ovA = 9 overlay "active" bytes at view model +0x1694, ovS = 9 overlay sequence shorts at +0x1730 (0x1409e0a70)
// trans.csv: every call of 0x140aba4d0 (sequence transitioner) for the view model where the sequence changes or the layer count changes:
//   old = transitioner +0x38 before, new = arg2, fade = +0x48 after, n0 / n1 = layer count +0x1a0 before / after, lastFade = newest layer +0x80
// ranges.jsonl: per model, each pose parameter's real range (0x140209ce0 called with -1e6 / +1e6 into a scratch float).
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || x === null || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
const DIR = 'OUT_DIR_HERE';
const PP = [['ads_blend', 0x1cfc], ['crouchFraction', 0x1cfe], ['oneHandFraction', 0x1d00], ['aimPitch', 0x1d02], ['aimYaw', 0x1d04], ['script0', 0x1d06],
  ['reactiveIdle', 0x1d08], ['sprintfrac', 0x18e0], ['velocity', 0x18e2], ['chargeFraction', 0x18e4], ['chargeFractionEventScaled', 0x18e6],
  ['zoomToggleFrac', 0x1d0a], ['move_yaw', 0x1d0c], ['move_yaw_backward', 0x1d0e]];
const frames = new File(DIR + '/frames.csv', 'w');
const trans = new File(DIR + '/trans.csv', 'w');
const ranges = new File(DIR + '/ranges.jsonl', 'w');
frames.write(['w', 'ct10', 'ct28', 'zf', 'vx', 'vy', 'vz', 'clip', 'ws', 'vmF', 'vmR', 'vmU', 'vmaP', 'vmaY', 'vmaR', 'cyc', 'seq', 'mdl'].concat(PP.map(x => 'pp_' + x[0]), ['ovA', 'ovS']).join(',') + '\n');
trans.write('w,ct10,ent,old,new,fadeBefore,fade,n0,n1,lastFade,lastStart\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const ppReal = new NativeFunction(at('0x140209ce0'), 'float', ['pointer', 'int16', 'float', 'pointer']);
const ENT = at('0x1424139b8'), SER = at('0x1424139c0'), GV = at('0x1419832d8').readPointer();
const fromHandle = (h) => {
  if (h === 0xffffffff) return null;
  const i = h & 0xffff;
  if (SER.add(i * 32).readU32() !== (h >>> 16)) return null;
  const w = ENT.add(i * 32).readPointer();
  return w.isNull() ? null : w;
};
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const scratch = Memory.alloc(16);
const seenMdl = {};
let n = 0, vmPtr = null, vmr = null;
function vmInfo(vm) {
  const mdl = vm.add(0x1000).readPointer();
  const idx = PP.map(x => vm.add(x[1]).readS16());
  const pp = idx.map(i => (i < 0 || i > 64) ? NaN : vm.add(0xe54 + 4 * i).readFloat());
  if (!mdl.isNull() && !seenMdl[mdl.toString()]) {
    seenMdl[mdl.toString()] = 1;
    const o = { w: Date.now(), mdl: mdl.toString(), idx: {} };
    PP.forEach((x, k) => {
      const i = idx[k];
      if (i < 0) return;
      try { const lo = ppReal(mdl, i, -1e6, scratch); const hi = ppReal(mdl, i, 1e6, scratch); const mid = ppReal(mdl, i, 0.5 * (lo + hi), scratch); o.idx[x[0]] = [i, lo, hi, mid]; } catch (e) { o.idx[x[0]] = [i, 'err']; }
    });
    ranges.write(JSON.stringify(o) + '\n'); ranges.flush();
  }
  const ovA = [], ovS = [];
  for (let k = 0; k < 9; k++) { ovA.push(vm.add(0x1694 + k).readU8()); ovS.push(vm.add(0x1730 + 2 * k).readS16()); }
  return { mdl: mdl.toUInt32() & 0xffffff, pp, ovA: ovA.join(' '), ovS: ovS.join(' '), cyc: vm.add(0xf4).readFloat(), seq: vm.add(0xe44).readS16() };
}
Interceptor.attach(at('0x14085c3e0'), {
  onEnter(args) { this.vm = args[0]; this.m = args[2]; },
  onLeave() {
    try {
      const m = this.m, vm = this.vm;
      vmPtr = vm;
      const fw = r3(m), rt = r3(m.add(12)), up = r3(m.add(24)), cp = r3(m.add(36)), ca = r3(m.add(48));
      const o = r3(vm.add(0x188)), an = r3(vm.add(0x194));
      const d = [o[0] - cp[0], o[1] - cp[1], o[2] - cp[2]];
      const inf = vmInfo(vm);
      inf.pos = [dot(d, fw), dot(d, rt), dot(d, up), an[0] - ca[0], an[1] - ca[1], an[2] - ca[2]];
      vmr = inf;
    } catch (e) { }
  }
});
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; },
  onLeave() {
    const p = this.p;
    let zf = NaN, clip = NaN, ws = NaN;
    try { zf = zoomFrac(p); } catch (e) { }
    const w = fromHandle(p.add(0x1930).readU32());
    if (w !== null) { clip = w.add(0x1590).readS32(); ws = w.add(0x15a4).readS32(); }
    const vv = r3(p.add(0x170));
    const v = vmr || { pos: [NaN, NaN, NaN, NaN, NaN, NaN], cyc: NaN, seq: NaN, mdl: 0, pp: PP.map(() => NaN), ovA: '', ovS: '' };
    const row = [Date.now(), GV.add(0x10).readFloat(), GV.add(0x28).readFloat(), zf, vv[0], vv[1], vv[2], clip, ws].concat(v.pos, [v.cyc, v.seq, v.mdl], v.pp).map(f);
    frames.write(row.join(',') + ',' + v.ovA + ',' + v.ovS + '\n');
    if (++n % 60 === 0) { frames.flush(); trans.flush(); }
  }
});
Interceptor.attach(at('0x140aba4d0'), {
  onEnter(args) {
    this.t = args[0];
    this.e = null;
    try {
      const ent = this.t.add(8).readPointer();
      if (vmPtr === null || !ent.equals(vmPtr)) return;
      this.e = ent;
      this.nw = args[1].toInt32() & 0xffff;
      this.old = this.t.add(0x38).readU16();
      this.f0 = this.t.add(0x48).readFloat();
      this.n0 = this.t.add(0x1a0).readU32();
    } catch (e) { this.e = null; }
  },
  onLeave() {
    if (this.e === null) return;
    const t = this.t, n1 = t.add(0x1a0).readU32(), fd = t.add(0x48).readFloat();
    if (this.nw === this.old && n1 === this.n0) return;
    let lf = NaN, ls = NaN;
    if (n1 > 0 && n1 <= 6) { lf = t.add((n1 - 1) * 0x38 + 0x80).readFloat(); ls = t.add((n1 - 1) * 0x38 + 0x7c).readFloat(); }
    trans.write([Date.now(), f(GV.add(0x10).readFloat()), this.e.toUInt32() & 0xffffff, this.old, this.nw, f(this.f0), f(fd), this.n0, n1, f(lf), f(ls)].join(',') + '\n');
  }
});
send({ ready: true, wall: Date.now() });
