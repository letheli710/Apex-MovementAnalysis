// CAM-13 probe (Frida, read-only: hooks only log, nothing is changed).
// Zipline_CameraRoll (0x1407fb580, arg 0 = player) adds a curvature roll on top of the roll toward the rope:
// ziprailMaxCurvatureRollAngle (18) x the player float at +0x223c. This logs that float and the player speed
// (+0x170 velocity) on every call, batched 60 calls per message: [t, curv, speed] rows.
// Addresses are Ghidra (image base 0x140000000) of r5apex_dx12.exe.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const t0 = Date.now();
let rows = [];
Interceptor.attach(at('0x1407fb580'), {
  onEnter(args) {
    const p = args[0];
    const vx = p.add(0x170).readFloat(), vy = p.add(0x174).readFloat(), vz = p.add(0x178).readFloat();
    rows.push([((Date.now() - t0) / 1000).toFixed(3), p.add(0x223c).readFloat().toFixed(4),
               Math.sqrt(vx * vx + vy * vy + vz * vz).toFixed(1)]);
    if (rows.length >= 60) { send({ r: rows }); rows = []; }
  }
});
send({ ready: true, wall: Date.now() });
