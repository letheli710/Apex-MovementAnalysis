// F-GAPS probe (Frida, read-only: hooks only log and call read-only getters). Addresses are Ghidra (base 0x140000000) of r5apex_dx12.exe.
// Built from recoil-view/frida_recoil.js + tools/probe.js. frames.csv, one line per first-person CalcView (0x1407f2bb0):
//   w = Date.now ms (same clock as Python time.time), ct = game time, ft = frame time
//   fP fY fR = output angles (screen); bP bY = eye angles into 0x1407f3f90 (aim); puP puY puR = punch added to the view (0x140af1ed0)
//   p1* / pv1* = player +0x2430 / +0x243c (first punch group angle / velocity, m_vecPunchBase); s2* / v2* = +0x2448 / +0x2454 (m_vecPunchWeapon)
//   kP dP kY dY = weapon spring constants of the last 0x140712920 call that returned true (NaN when it returned false)
//   zf, fov (*arg4 on return), idx = weapon +0x1700, clip = weapon +0x1590, vz = player +0x170 z, oz = origin z (vtable +0x40)
//   eX eY eZ = *arg1 on return (view origin, for position shake)
// shots.csv, one line per kick (0x140711ce0): punch before/after, as in tools/probe.js.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || x === null || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
const DIR = 'OUT_DIR_HERE';
const frames = new File(DIR + '/frames.csv', 'w');
const shots = new File(DIR + '/shots.csv', 'w');
frames.write('w,ct,ft,fP,fY,fR,bP,bY,puP,puY,puR,p1P,p1Y,p1R,pv1P,pv1Y,pv1R,s2P,s2Y,s2R,v2P,v2Y,v2R,kP,dP,kY,dY,zf,fov,idx,clip,vz,oz,eX,eY,eZ\n');
shots.write('w,ct,val,idx,row,c0,c1,c2,c3,zf,s2P0,s2Y0,v2P0,v2Y0,s2P1,s2Y1,v2P1,v2Y1,p1P,p1Y\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const kickVal = new NativeFunction(at('0x140712c80'), 'float', ['pointer']);
const ENT = at('0x1424139b8'), SER = at('0x1424139c0'), GV = at('0x1419832d8').readPointer(), PAT = at('0x142819e70');
const fromHandle = (h) => {
  if (h === 0xffffffff) return null;
  const i = h & 0xffff;
  if (SER.add(i * 32).readU32() !== (h >>> 16)) return null;
  const w = ENT.add(i * 32).readPointer();
  return w.isNull() ? null : w;
};
let n = 0, fr = null, spr = [NaN, NaN, NaN, NaN, NaN, NaN];
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.org = args[1]; this.ang = args[2]; this.fov = args[3]; fr = {}; },
  onLeave() {
    if (fr === null) return;
    const p = this.p, a = r3(this.ang), b = fr.base || [NaN, NaN, NaN], pu = fr.punch || [NaN, NaN, NaN];
    const p1 = r3(p.add(0x2430)), pv1 = r3(p.add(0x243c)), s2 = r3(p.add(0x2448)), v2 = r3(p.add(0x2454)), vv = r3(p.add(0x170));
    let zf = NaN, idx = NaN, clip = NaN;
    const w = fromHandle(p.add(0x1930).readU32());
    try { zf = zoomFrac(p); } catch (e) { }
    if (w !== null) { idx = w.add(0x1700).readS32(); clip = w.add(0x1590).readS32(); }
    let fov = NaN, e = [NaN, NaN, NaN], oz = NaN;
    try { fov = this.fov.readFloat(); } catch (x) { }
    try { e = r3(this.org); } catch (x) { }
    try { oz = new NativeFunction(p.readPointer().add(0x40).readPointer(), 'pointer', ['pointer'])(p).add(8).readFloat(); } catch (x) { }
    const row = [Date.now(), GV.add(0x28).readFloat(), GV.add(0x30).readFloat(), a[0], a[1], a[2], b[0], b[1], pu[0], pu[1], pu[2],
      p1[0], p1[1], p1[2], pv1[0], pv1[1], pv1[2], s2[0], s2[1], s2[2], v2[0], v2[1], v2[2], spr[0], spr[3], spr[1], spr[4], zf, fov, idx, clip, vv[2], oz, e[0], e[1], e[2]];
    frames.write(row.map(f).join(',') + '\n');
    fr = null;
    if (++n % 50 === 0) { frames.flush(); shots.flush(); }
  }
});
Interceptor.attach(at('0x1407f3f90'), { onEnter(args) { if (fr !== null) fr.base = r3(args[2]); } });
Interceptor.attach(at('0x140af1ed0'), { onEnter(args) { this.o = args[1]; }, onLeave() { if (fr !== null) fr.punch = r3(this.o); } });
Interceptor.attach(at('0x140712920'), {
  onEnter(args) { this.o = args[1]; },
  onLeave(ret) { if (ret.toInt32() & 1) { const o = this.o; spr = [o.readFloat(), o.add(4).readFloat(), o.add(8).readFloat(), o.add(12).readFloat(), o.add(16).readFloat(), o.add(20).readFloat()]; } else spr = [NaN, NaN, NaN, NaN, NaN, NaN]; }
});
Interceptor.attach(at('0x140711ce0'), {
  onEnter(args) {
    const w = args[0];
    const own = fromHandle(w.add(0x1560).readU32());
    if (own === null) { this.own = null; return; }
    this.own = new NativeFunction(own.readPointer().add(0x588).readPointer(), 'pointer', ['pointer'])(own);
    const p = this.own;
    if (p.isNull()) { this.own = null; return; }
    this.v0 = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat()];
    const val = kickVal(w), per = w.add(0x2190).readFloat(), pidx = w.add(0x2124).readS32(), idx = w.add(0x1700).readS32();
    let row = -1, c = [NaN, NaN, NaN, NaN];
    if (pidx >= 0) {
      const pat = PAT.add(pidx * 0x42c), cnt = pat.add(0x20).readS32();
      row = Math.min(per > 0 ? Math.floor(val / per) : idx, cnt - 1);
      const r = pat.add(row * 0x10 + 0x2c);
      c = [r.readFloat(), r.add(4).readFloat(), r.add(8).readFloat(), r.add(12).readFloat()];
    }
    let zf = NaN; try { zf = zoomFrac(p); } catch (x) { }
    this.line = [Date.now(), GV.add(0x28).readFloat(), val, idx, row].concat(c, [zf]);
  },
  onLeave() {
    if (this.own === null) return;
    const p = this.own;
    const a = [p.add(0x2448).readFloat(), p.add(0x244c).readFloat(), p.add(0x2454).readFloat(), p.add(0x2458).readFloat(), p.add(0x2430).readFloat(), p.add(0x2434).readFloat()];
    shots.write(this.line.concat(this.v0, a).map(f).join(',') + '\n');
  }
});
send({ ready: true, wall: Date.now() });
