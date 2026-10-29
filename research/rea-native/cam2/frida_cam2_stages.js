// CAM2 camera-stage probe (Frida, read-only: hooks only log, nothing is changed).
// Splits the first-person view (CalcView 0x1407f2bb0) into its stages, per call:
//   base   = angles entering 0x1407f3f90 (eye angles, after the view-entity blend)
//   trav   = change made by C_PredictedFirstPersonProxy::GetTraversalViewPosition (0x1406668a0; traversal animation camera)
//   rodeo  = change made by the rodeo smoothing stage (0x1407f0de0)
//   punch  = vector returned by 0x140af1ed0 (punch spring 1 +0x2430, punch spring 2 +0x2448 x ADS factor, weapon drift)
//   rollIn / rollOut = roll entering / leaving View_CalcRoll (0x140afc480); smoothed grapple/zipline roll (player +0x36d4)
//   zipRoll = Zipline_CameraRoll (0x1407fb580) target
//   final  = CalcView output angles and eye position; origin = player GetAbsOrigin (vtable +0x40)
//   viewOff = player +0xe8..+0xf0 (view offset), zipOff = player +0x2f78..+0x2f80 (smoothed zipline view offset), vel +0x170
// One CSV line per call to OUT_PATH. Addresses are Ghidra (image base 0x140000000) of r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || isNaN(x)) ? '' : (Math.round(x * 10000) / 10000);
const OUT_PATH = 'OUT_PATH_HERE';
const out = new File(OUT_PATH, 'w');
const COLS = ['t', 'fP', 'fY', 'fR', 'bP', 'bY', 'bR', 'tvP', 'tvY', 'tvR', 'tvZ', 'roP', 'roY', 'roR', 'puP', 'puY', 'puR',
  'p1P', 'p1Y', 'p1R', 'p2P', 'p2Y', 'p2R', 'rollIn', 'rollOut', 'smRoll', 'zipRoll', 'ex', 'ey', 'ez', 'ox', 'oy', 'oz',
  'voX', 'voY', 'voZ', 'zoX', 'zoY', 'zoZ', 'vx', 'vy', 'vz'];
out.write(COLS.join(',') + '\n');
let nrows = 0, fr = null, zipRoll = NaN;

Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.pos = args[1]; this.ang = args[2]; fr = { tv: [0, 0, 0, 0], ro: [0, 0, 0] }; },
  onLeave() {
    if (fr === null) return;
    const p = this.p, a = r3(this.ang), e = r3(this.pos);
    let o = [NaN, NaN, NaN];
    try { const fn = new NativeFunction(p.readPointer().add(0x40).readPointer(), 'pointer', ['pointer']); o = r3(fn(p)); } catch (err) { }
    const p1 = r3(p.add(0x2430)), p2 = r3(p.add(0x2448)), vo = r3(p.add(0xe8)), zo = r3(p.add(0x2f78)), v = r3(p.add(0x170));
    const b = fr.base || [NaN, NaN, NaN], pu = fr.punch || [NaN, NaN, NaN];
    const row = [(Date.now() - t0) / 1000, a[0], a[1], a[2], b[0], b[1], b[2], fr.tv[0], fr.tv[1], fr.tv[2], fr.tv[3],
      fr.ro[0], fr.ro[1], fr.ro[2], pu[0], pu[1], pu[2], p1[0], p1[1], p1[2], p2[0], p2[1], p2[2], fr.rollIn, fr.rollOut,
      p.add(0x36d4).readFloat(), zipRoll, e[0], e[1], e[2], o[0], o[1], o[2], vo[0], vo[1], vo[2], zo[0], zo[1], zo[2], v[0], v[1], v[2]];
    out.write(row.map(f).join(',') + '\n');
    fr = null; zipRoll = NaN;
    if (++nrows % 1200 === 0) { out.flush(); send({ rows: nrows }); }
  }
});
Interceptor.attach(at('0x1407f3f90'), { onEnter(args) { if (fr !== null) fr.base = r3(args[2]); } });
Interceptor.attach(at('0x1406668a0'), {
  onEnter(args) { this.pos = args[1]; this.ang = args[2]; this.a0 = r3(this.ang); this.z0 = this.pos.add(8).readFloat(); },
  onLeave() {
    if (fr === null) return;
    const a1 = r3(this.ang);
    fr.tv = [a1[0] - this.a0[0], a1[1] - this.a0[1], a1[2] - this.a0[2], this.pos.add(8).readFloat() - this.z0];
  }
});
Interceptor.attach(at('0x1407f0de0'), {
  onEnter(args) { this.ang = args[2]; this.a0 = r3(this.ang); },
  onLeave() { if (fr !== null) { const a1 = r3(this.ang); fr.ro = [a1[0] - this.a0[0], a1[1] - this.a0[1], a1[2] - this.a0[2]]; } }
});
Interceptor.attach(at('0x140af1ed0'), {
  onEnter(args) { this.o = args[1]; },
  onLeave() { if (fr !== null) fr.punch = r3(this.o); }
});
Interceptor.attach(at('0x140afc480'), {
  onEnter(args) { this.ang = args[2]; if (fr !== null) fr.rollIn = this.ang.add(8).readFloat(); },
  onLeave() { if (fr !== null) fr.rollOut = this.ang.add(8).readFloat(); }
});
Interceptor.attach(at('0x1407fb580'), {
  onEnter(args) { this.o = args[3]; },
  onLeave() { zipRoll = this.o.readFloat(); }
});
send({ ready: true, wall: Date.now() });
