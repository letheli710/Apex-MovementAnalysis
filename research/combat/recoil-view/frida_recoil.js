// Recoil probe (Frida, read-only: hooks only log and call read-only getters, nothing is changed). Addresses are Ghidra (base 0x140000000) of r5apex_dx12.exe.
// frames.csv, one line per first-person CalcView (0x1407f2bb0):
//   f* = output angles (the screen); b* = eye angles entering 0x1407f3f90 (the aim); pu* = punch added to the view (0x140af1ed0)
//   s2* / v2* = player +0x2448 / +0x2454, m_vecPunchWeapon angle and velocity; s1P = +0x2430, m_vecPunchBase pitch
//   zf = zoom fraction (0x140b04140), val = decayed kick value (0x140712c80), hot = spring heat (0x140713060), idx = shot index (weapon +0x1700)
//   kP dP kY dY = spring constants used by the last step (0x140712920 output), ft = frame time, ct = game time
// shots.csv, one line per kick (0x140711ce0): weapon, value and pattern row at entry, the punch before and after, and on the first kick of a weapon the raw fields.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
const frames = new File('OUT_DIR_HERE/frames.csv', 'w');
const shots = new File('OUT_DIR_HERE/shots.csv', 'w');
frames.write('t,ct,ft,fP,fY,fR,bP,bY,puP,puY,puR,s1P,s2P,s2Y,s2R,v2P,v2Y,v2R,zf,val,hot,idx,kP,dP,kY,dY\n');
shots.write('t,ct,w,scaleP,scaleR,val,idx,row,c0,c1,c2,c3,zf,s2P0,s2Y0,v2P0,v2Y0,s2P1,s2Y1,v2P1,v2Y1\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const kickVal = new NativeFunction(at('0x140712c80'), 'float', ['pointer']);
const heat = new NativeFunction(at('0x140713060'), 'float', ['pointer']);
const ENT = at('0x1424139b8'), SER = at('0x1424139c0'), GV = at('0x1419832d8').readPointer(), PAT = at('0x142819e70');
const weaponOf = (p) => {
  const h = p.add(0x1930).readU32();
  if (h === 0xffffffff) return null;
  const i = h & 0xffff;
  if (SER.add(i * 32).readU32() !== (h >>> 16)) return null;
  const w = ENT.add(i * 32).readPointer();
  return w.isNull() ? null : w;
};
let n = 0, fr = null, spr = [NaN, NaN, NaN, NaN];
const seen = {};
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.ang = args[2]; fr = {}; },
  onLeave() {
    if (fr === null) return;
    const p = this.p, a = r3(this.ang), b = fr.base || [NaN, NaN, NaN], pu = fr.punch || [NaN, NaN, NaN];
    const s2 = r3(p.add(0x2448)), v2 = r3(p.add(0x2454));
    let zf = NaN, val = NaN, hot = NaN, idx = NaN;
    const w = weaponOf(p);
    if (w !== null) { zf = zoomFrac(p); val = kickVal(w); hot = heat(w); idx = w.add(0x1700).readS32(); }
    const row = [(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), GV.add(0x30).readFloat(), a[0], a[1], a[2], b[0], b[1], pu[0], pu[1], pu[2], p.add(0x2430).readFloat(),
      s2[0], s2[1], s2[2], v2[0], v2[1], v2[2], zf, val, hot, idx, spr[0], spr[3], spr[1], spr[4]];
    frames.write(row.map(f).join(',') + '\n');
    fr = null;
    if (++n % 100 === 0) { frames.flush(); shots.flush(); }
  }
});
Interceptor.attach(at('0x1407f3f90'), { onEnter(args) { if (fr !== null) fr.base = r3(args[2]); } });
Interceptor.attach(at('0x140af1ed0'), { onEnter(args) { this.o = args[1]; }, onLeave() { if (fr !== null) fr.punch = r3(this.o); } });
Interceptor.attach(at('0x140712920'), {
  onEnter(args) { this.o = args[1]; },
  onLeave(ret) { if (ret.toInt32() & 1) { const o = this.o; spr = [o.readFloat(), o.add(4).readFloat(), o.add(8).readFloat(), o.add(12).readFloat(), o.add(16).readFloat(), o.add(20).readFloat()]; } else spr = [NaN, NaN, NaN, NaN, NaN, NaN]; }
});
// args: rcx weapon, xmm1 scale, xmm2 roll scale. Frida has no direct xmm in args, so read this.context.
Interceptor.attach(at('0x140711ce0'), {
  onEnter(args) {
    const w = args[0]; this.w = w;
    const h = w.add(0x1560).readU32(), i = h & 0xffff, own = ENT.add(i * 32).readPointer();
    this.own = new NativeFunction(own.readPointer().add(0x588).readPointer(), 'pointer', ['pointer'])(own);
    const p = this.own;
    this.v0 = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat()];
    const val = kickVal(w), per = w.add(0x2190).readFloat(), pidx = w.add(0x2124).readS32();
    const idx = w.add(0x1700).readS32();
    let row = -1, c = [NaN, NaN, NaN, NaN];
    if (pidx >= 0) {
      const pat = PAT.add(pidx * 0x42c), cnt = pat.add(0x20).readS32();
      row = Math.min(per > 0 ? Math.floor(val / per) : idx, cnt - 1);
      const r = pat.add(row * 0x10 + 0x2c);
      c = [r.readFloat(), r.add(4).readFloat(), r.add(8).readFloat(), r.add(12).readFloat()];
    }
    this.line = [(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), w.toString(), 0, 0, f(val), idx, row].concat(c.map(f));
    this.zf = zoomFrac(p);
    const key = w.toString();
    if (!seen[key]) {
      seen[key] = true;
      const raw = {};
      for (let o = 0x20e8; o <= 0x21e0; o += 4) raw['0x' + o.toString(16)] = f(w.add(o).readFloat());
      send({ weapon: key, name: (() => { try { return w.add(0x15b0).readCString(); } catch (e) { return '?'; } })(), pidx, raw, cnt: pidx >= 0 ? PAT.add(pidx * 0x42c).add(0x20).readS32() : -1 });
    }
  },
  onLeave() {
    const p = this.own, a = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat()];
    shots.write(this.line.concat([f(this.zf)], this.v0.map(f), a.map(f)).join(',') + '\n');
  }
});
send({ ready: true, wall: Date.now() });
