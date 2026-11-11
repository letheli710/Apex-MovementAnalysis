// RJA (D-77): used for ROCKET-JUMP-A-SPEC §7. Read-only; prints addresses and instruction text only (no decompiled code).
// Run: analyzeHeadless <projdir> r5apex -process r5apex.exe -noanalysis -readOnly -scriptPath <dir> -postScript StrRefCtx.java <out.txt> <args...>
//@category HSD
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;
import ghidra.program.model.symbol.*;
import java.io.*;
public class StrRefCtx extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    PrintWriter w = new PrintWriter(new File(a[0]), "UTF-8");
    Memory mem = currentProgram.getMemory();
    for (int i = 1; i < a.length; i++) {
      byte[] pat = (a[i] + "\0").getBytes("US-ASCII");
      Address s = mem.getMinAddress();
      while (true) {
        Address hit = mem.findBytes(s, pat, null, true, monitor);
        if (hit == null) break;
        w.println("STR " + a[i] + " @ " + hit);
        for (Reference r : getReferencesTo(hit)) {
          Address f = r.getFromAddress();
          Function fn = getFunctionContaining(f);
          w.println("  REF " + f + " type=" + r.getReferenceType() + " fn=" + (fn==null?"-":fn.getEntryPoint()+" "+fn.getName()));
          if (fn == null) {
            byte[] b = new byte[64]; mem.getBytes(f.subtract(16), b);
            StringBuilder sb = new StringBuilder("    bytes(-16):");
            for (byte x : b) sb.append(String.format(" %02x", x & 0xff));
            w.println(sb);
          } else {
            Instruction in = getInstructionAt(f);
            for (int k = 0; k < 12 && in != null; k++) { w.println("    " + in.getAddress() + "  " + in); in = in.getNext(); }
          }
        }
        s = hit.add(1);
      }
    }
    w.close();
  }
}
