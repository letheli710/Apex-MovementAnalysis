// Sequence table per view model (Frida, read-only). For each new model (keyed by CStudioHdr + label of sequence 1) on the view model (+0x1000 = CStudioHdr):
// virtual model = CStudioHdr +0x10, count = vmodel +2 (u16), entry i = *(vmodel +0x10) + 8 + 0x10*i -> sequence descriptor (as 0x140aba4d0 reads it).
// Per sequence: fade-in +0x40, fade-out +0x44 (the two values 0x140aba4d0 takes the min of), bytes +4..+7, and the strings at desc + u16 +0 / +2
// (label = full .rseq path, activity name; found by scanning for known names). Output seqtable.jsonl, one line per model.
'use strict';
const mod = Process.getModuleByName('r5apex_dx12.exe');
const at = (a) => mod.base.add(ptr(a).sub(ptr('0x140000000')));
const DIR = 'OUT_DIR_HERE';
const out = new File(DIR + '/seqtable.jsonl', 'a');
const seen = {};
const str = (p) => { try { const s = p.readCString(); return s.length < 200 && /^[\x20-\x7e]*$/.test(s) ? s : '?'; } catch (e) { return '?'; } };
Interceptor.attach(at('0x14085c3e0'), {
  onEnter(args) {
    try {
      const vm = args[0], chdr = vm.add(0x1000).readPointer();
      if (chdr.isNull()) return;
      const hdr = chdr.add(8).readPointer(), vmod = chdr.add(0x10).readPointer();
      if (vmod.isNull()) return;
      // the CStudioHdr address is reused when the gun changes, so key on the first sequence's label (it holds the weapon folder)
      const t0 = vmod.add(0x10).readPointer(), P1 = t0.add(8 + 0x10).readPointer(), key = chdr.toString() + str(P1.add(P1.readU16()));
      if (seen[key]) return;
      seen[key] = 1;
      const o = { w: Date.now(), mdl: chdr.toUInt32() & 0xffffff, name: str(hdr.add(8)), seqs: [] };
      if (vmod.isNull()) { o.err = 'no vmodel'; out.write(JSON.stringify(o) + '\n'); out.flush(); return; }
      const n = vmod.add(2).readU16(), tab = vmod.add(0x10).readPointer();
      for (let i = 0; i < n && i < 400; i++) {
        try {
          const P = tab.add(8 + i * 0x10).readPointer();
          o.seqs.push([i, str(P.add(P.readU16())), str(P.add(P.add(2).readU16())), Math.round(P.add(0x40).readFloat() * 1e4) / 1e4, Math.round(P.add(0x44).readFloat() * 1e4) / 1e4, P.add(4).readU32().toString(16)]);
        } catch (e) { o.seqs.push([i, 'err']); }
      }
      out.write(JSON.stringify(o) + '\n'); out.flush();
    } catch (e) { }
  }
});
send({ ready: 'seqtable' });
