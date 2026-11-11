// RJA (D-77): used for ROCKET-JUMP-A-SPEC §7. Read-only; prints addresses and instruction text only (no decompiled code).
// Run: analyzeHeadless <projdir> r5apex -process r5apex.exe -noanalysis -readOnly -scriptPath <dir> -postScript AddrRefs.java <out.txt> <args...>
//@category HSD
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*;
public class AddrRefs extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    PrintWriter w = new PrintWriter(new File(a[0]), "UTF-8");
    for (int i = 1; i < a.length; i++) {
      Address base = toAddr(a[i]);
      for (int off = -16; off <= 0x80; off += 8) {
        Address t = base.add(off);
        for (Reference r : getReferencesTo(t)) {
          Address f = r.getFromAddress();
          Function fn = getFunctionContaining(f);
          w.println("TARGET " + t + " REF " + f + " " + r.getReferenceType() + " fn=" + (fn==null?"-":fn.getEntryPoint()));
          Instruction in = getInstructionAt(f);
          if (in == null) continue;
          Instruction p = in; for (int k=0;k<8 && p.getPrevious()!=null;k++) p = p.getPrevious();
          for (int k=0;k<14 && p!=null;k++) {
            String extra = "";
            for (Reference rr : p.getReferencesFrom()) {
              Data d = getDataAt(rr.getToAddress());
              if (d != null && d.hasStringValue()) extra += " \"" + d.getValue() + "\"";
              else { try { byte[] b = new byte[48]; currentProgram.getMemory().getBytes(rr.getToAddress(), b); String s = new String(b, "ISO-8859-1"); int z = s.indexOf(0); if (z > 3) { s = s.substring(0, z); if (s.matches("[ -~]+")) extra += " ~\"" + s + "\""; } } catch (Exception e) {} }
            }
            w.println("    " + p.getAddress() + "  " + p + extra); p = p.getNext();
          }
        }
        if (off == 0) {}
      }
    }
    w.close();
  }
}
