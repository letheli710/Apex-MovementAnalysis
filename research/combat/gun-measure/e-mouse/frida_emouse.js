// E-MOUSE probe (Frida, read-only: hooks only log and call read-only getters). Addresses are Ghidra (base 0x140000000) of r5apex_dx12.exe.
// Built from recoil-view/frida_recoil.js + frida_ads.js. frames.csv, one line per first-person CalcView (0x1407f2bb0):
//   w = wall clock ms (Date.now, same clock as the Python mouse/key log), ct = game time, ft = frame time
//   fP fY = output angles (the screen); bP bY = eye angles entering 0x1407f3f90 (the aim); puP puY = punch added to the view (0x140af1ed0)
//   s2* / v2* = player +0x2448 / +0x2454 (m_vecPunchWeapon angle / velocity); zf = zoom fraction (0x140b04140); fov = *arg4 on return; idx = weapon +0x1700
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
const frames = new File('OUT_DIR_HERE/frames.csv', 'w');
frames.write('w,ct,ft,fP,fY,bP,bY,puP,puY,s2P,s2Y,v2P,v2Y,zf,fov,idx\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const ENT = at('0x1424139b8'), SER = at('0x1424139c0'), GV = at('0x1419832d8').readPointer();
const weaponOf = (p) => {
  const h = p.add(0x1930).readU32();
  if (h === 0xffffffff) return null;
  const i = h & 0xffff;
  if (SER.add(i * 32).readU32() !== (h >>> 16)) return null;
  const w = ENT.add(i * 32).readPointer();
  return w.isNull() ? null : w;
};
let n = 0, fr = null;
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.ang = args[2]; this.fov = args[3]; fr = {}; },
  onLeave() {
    if (fr === null) return;
    const p = this.p, a = r3(this.ang), b = fr.base || [NaN, NaN, NaN], pu = fr.punch || [NaN, NaN, NaN];
    const s2 = r3(p.add(0x2448)), v2 = r3(p.add(0x2454));
    let zf = NaN, idx = NaN;
    const w = weaponOf(p);
    if (w !== null) { zf = zoomFrac(p); idx = w.add(0x1700).readS32(); }
    let fov = NaN; try { fov = this.fov.readFloat(); } catch (e) {}
    const row = [Date.now(), GV.add(0x28).readFloat(), GV.add(0x30).readFloat(), a[0], a[1], b[0], b[1], pu[0], pu[1], s2[0], s2[1], v2[0], v2[1], zf, fov, idx];
    frames.write(row.map(f).join(',') + '\n');
    fr = null;
    if (++n % 50 === 0) frames.flush();
  }
});
Interceptor.attach(at('0x1407f3f90'), { onEnter(args) { if (fr !== null) fr.base = r3(args[2]); } });
Interceptor.attach(at('0x140af1ed0'), { onEnter(args) { this.o = args[1]; }, onLeave() { if (fr !== null) fr.punch = r3(this.o); } });
send({ ready: true, wall: Date.now() });
