// ADS probe (Frida, read-only: hooks only log and call read-only getters). Addresses are Ghidra (base 0x140000000) of r5apex_dx12.exe.
// view.csv, one line per first-person CalcView (0x1407f2bb0): zf = 0x140b04140; fov = *arg4 on return; aim and frame time.
// vm.csv, one line per C_BaseViewModel::CalcViewModelView (0x14085c3e0): view model origin and angles on return, in the camera's axes passed in arg3
//   (arg3[0..2] forward, [3..5] right, [6..8] up, [9..11] camera position, [12..14] camera angles); cycle = vm +0xf4, seq = vm +0xe44.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
const r3 = (p) => [p.readFloat(), p.add(4).readFloat(), p.add(8).readFloat()];
const f = (x) => (x === undefined || isNaN(x)) ? '' : (Math.round(x * 100000) / 100000);
const view = new File('OUT_DIR_HERE/view.csv', 'w');
const vmf = new File('OUT_DIR_HERE/vm.csv', 'w');
view.write('t,ct,ft,zf,fov,fP,fY\n');
vmf.write('t,ct,zf,dF,dR,dU,aP,aY,aR,caP,caY,caR,cycle,seq\n');
const zoomFrac = new NativeFunction(at('0x140b04140'), 'float', ['pointer']);
const GV = at('0x1419832d8').readPointer();
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
let n = 0;
Interceptor.attach(at('0x1407f2bb0'), {
  onEnter(args) { this.p = args[0]; this.ang = args[2]; this.fov = args[3]; },
  onLeave() {
    const a = r3(this.ang);
    view.write([(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), GV.add(0x30).readFloat(), zoomFrac(this.p), this.fov.readFloat(), a[0], a[1]].map(f).join(',') + '\n');
    if (++n % 100 === 0) { view.flush(); vmf.flush(); }
  }
});
Interceptor.attach(at('0x14085c3e0'), {
  onEnter(args) { this.vm = args[0]; this.pl = args[1]; this.m = args[2]; },
  onLeave() {
    const m = this.m, vm = this.vm;
    const fw = r3(m), rt = r3(m.add(12)), up = r3(m.add(24)), cp = r3(m.add(36)), ca = r3(m.add(48));
    const o = r3(vm.add(0x188)), an = r3(vm.add(0x194));
    const d = [o[0] - cp[0], o[1] - cp[1], o[2] - cp[2]];
    vmf.write([(Date.now() - t0) / 1000, GV.add(0x28).readFloat(), zoomFrac(this.pl), dot(d, fw), dot(d, rt), dot(d, up), an[0], an[1], an[2], ca[0], ca[1], ca[2], vm.add(0xf4).readFloat(), vm.add(0xe44).readS16()].map(f).join(',') + '\n');
  }
});
// Once: constants, field names, ConVar values.
const strs = {};
for (const a of ['0x1416ba790', '0x1416ba870', '0x1416ba850', '0x1416ba828', '0x1416ba800', '0x1416c04d8', '0x1416c04c0']) strs[a] = at(a).readCString();
const cf = {};
for (const a of ['0x1417f87a8', '0x1417f87c8', '0x1417f8590', '0x1417f8160', '0x1417f8ab8', '0x1417f8a74', '0x1417f8a10']) cf[a] = at(a).readFloat();
const cv = {};
for (const a of ['0x142403130', '0x142794e60', '0x142794fa0', '0x142794410', '0x1427a6c70', '0x1427a6bd0', '0x1427b2490', '0x1423a4f50']) {
  try {
    const c = at(a).readPointer();
    let nm = '?';
    for (const o of [0x10, 0x18, 0x8]) { try { const s = c.add(o).readPointer().readCString(); if (s && /^[a-zA-Z_]\w+$/.test(s)) { nm = s; break; } } catch (e) {} }
    cv[a] = { name: nm, f: c.add(0x60).readFloat(), i: c.add(100).readS32() };
  } catch (e) { cv[a] = String(e); }
}
send({ ready: true, wall: Date.now(), strs, cf, cv });
