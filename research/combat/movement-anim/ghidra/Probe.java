// Probe.java: read-only multi-query Ghidra script (2026-11-13, r5gap-code).
// Commands, one per line: dec <addr> | callers <addr> | callees <addr> | refs <addr>
//   | str <substring> | mem <ascii> | dis <addr> <n> | imm <hex> [<hex> ...]
// Output contains decompiled game code: write it outside the public repo (private HSD-RawData).
// Run with run.sh (SCRIPT_DIR, GHIDRA_PROJECTS set; analyzeHeadless on PATH).
//@category HSD
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import ghidra.app.decompiler.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import ghidra.program.model.mem.*;

public class Probe extends GhidraScript {
  DecompInterface di;
  PrintWriter w;
  public void run() throws Exception {
    String[] args = getScriptArgs();
    di = new DecompInterface(); di.openProgram(currentProgram);
    w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8);
    for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
      String s = line.trim(); if (s.isEmpty() || s.startsWith("#")) continue;
      String[] t = s.split("\s+", 2);
      try {
        if (t[0].equals("dec")) dec(t[1]);
        else if (t[0].equals("str")) str(t[1]);
        else if (t[0].equals("callers")) callers(t[1]);
        else if (t[0].equals("callees")) callees(t[1]);
        else if (t[0].equals("mem")) mem(t[1]);
        else if (t[0].equals("dis")) dis(t[1]);
        else if (t[0].equals("imm")) imm(t[1]);
        else if (t[0].equals("refs")) refs(t[1]);
      } catch (Exception e) { w.println("// error " + s + ": " + e); }
      w.flush();
    }
    w.close(); di.dispose();
  }
  Address A(String h){ return toAddr(Long.parseUnsignedLong(h.replace("0x",""),16)); }
  void dec(String h) {
    Function f = getFunctionContaining(A(h));
    w.println("//==== dec " + h + (f==null?" no function":" "+f.getEntryPoint()+" "+f.getName()));
    if (f==null) return;
    DecompileResults r = di.decompileFunction(f, 240, monitor);
    w.println(r.decompileCompleted()? r.getDecompiledFunction().getC() : "// failed " + r.getErrorMessage());
  }
  void callers(String h) {
    Function f = getFunctionContaining(A(h));
    w.println("//==== callers " + h);
    for (Reference r : getReferencesTo(f.getEntryPoint())) {
      Function c = getFunctionContaining(r.getFromAddress());
      w.println(r.getFromAddress()+"\t"+r.getReferenceType()+"\t"+(c==null?"-":c.getEntryPoint()+" "+c.getName()));
    }
  }
  void callees(String h) {
    Function f = getFunctionContaining(A(h));
    w.println("//==== callees " + h);
    for (Function c : f.getCalledFunctions(monitor)) w.println(c.getEntryPoint()+" "+c.getName());
  }
  void str(String sub) {
    w.println("//==== str " + sub);
    DataIterator it = currentProgram.getListing().getDefinedData(true);
    int n=0;
    while (it.hasNext()) {
      Data d = it.next();
      if (!d.hasStringValue()) continue;
      Object v = d.getValue(); if (v==null) continue;
      String sv = v.toString();
      if (!sv.contains(sub)) continue;
      n++; if (n>200) { w.println("...more"); break; }
      w.println("S "+d.getAddress()+" \""+sv.replace("\n","\n")+"\"");
      for (Reference r : getReferencesTo(d.getAddress())) {
        Function c = getFunctionContaining(r.getFromAddress());
        w.println("   ref "+r.getFromAddress()+" "+(c==null?"-":c.getEntryPoint()+" "+c.getName()));
      }
    }
  }

  void refs(String h) {
    w.println("//==== refs " + h);
    for (Reference r : getReferencesTo(A(h))) {
      Function c = getFunctionContaining(r.getFromAddress());
      w.println("   ref "+r.getFromAddress()+" "+r.getReferenceType()+" "+(c==null?"-":c.getEntryPoint()+" "+c.getName()));
    }
  }
  void mem(String sub) throws Exception {
    w.println("//==== mem " + sub);
    byte[] pat = sub.getBytes(StandardCharsets.US_ASCII);
    Memory m = currentProgram.getMemory();
    Address start = m.getMinAddress();
    int n=0;
    while (true) {
      Address a = m.findBytes(start, pat, null, true, monitor);
      if (a==null) break;
      // back up to string start
      Address s0 = a;
      while (true) { try { byte b = m.getByte(s0.subtract(1)); if (b==0 || b<32 || b>126) break; s0 = s0.subtract(1);} catch(Exception e){break;} }
      StringBuilder sb = new StringBuilder();
      Address e = s0;
      for (int i=0;i<120;i++){ byte b=m.getByte(e); if (b==0) break; sb.append((char)b); e=e.add(1);} 
      w.println("M "+s0+" \""+sb+"\"");
      for (Reference r : getReferencesTo(s0)) {
        Function c = getFunctionContaining(r.getFromAddress());
        w.println("   ref "+r.getFromAddress()+" "+(c==null?"-":c.getEntryPoint()+" "+c.getName()));
      }
      n++; if (n>300) { w.println("...more"); break; }
      start = e.add(1);
    }
  }

  void dis(String arg) {
    String[] a = arg.split("\s+");
    Address x = A(a[0]); int n = Integer.parseInt(a[1]);
    w.println("//==== dis " + arg);
    Instruction ins = getInstructionContaining(x);
    for (int i=0;i<n && ins!=null;i++) {
      StringBuilder sb = new StringBuilder();
      for (Reference r : ins.getReferencesFrom()) {
        Data dd = getDataAt(r.getToAddress());
        if (dd!=null && dd.hasStringValue()) sb.append(" ; \""+dd.getValue()+"\"");
      }
      w.println(ins.getAddress()+"  "+ins+sb);
      ins = ins.getNext();
    }
  }

  void imm(String arg) {
    String[] a = arg.split("\s+");
    java.util.Set<Long> vals = new java.util.HashSet<>();
    for (String x : a) vals.add(Long.parseLong(x.replace("0x",""),16));
    w.println("//==== imm " + arg);
    InstructionIterator it = currentProgram.getListing().getInstructions(true);
    int n=0;
    while (it.hasNext()) {
      Instruction ins = it.next();
      String mn = ins.getMnemonicString();
      if (!(mn.equals("CMP")||mn.equals("MOV")||mn.equals("SUB")||mn.equals("LEA")||mn.equals("ADD"))) continue;
      for (int i=0;i<ins.getNumOperands();i++) {
        for (Object o : ins.getOpObjects(i)) {
          if (o instanceof ghidra.program.model.scalar.Scalar) {
            long v = ((ghidra.program.model.scalar.Scalar)o).getUnsignedValue();
            if (vals.contains(v)) {
              Function f = getFunctionContaining(ins.getAddress());
              w.println(ins.getAddress()+"	"+(f==null?"-":f.getEntryPoint()+" "+f.getName())+"	"+ins);
              n++;
            }
          }
        }
      }
      if (n>3000) break;
    }
  }
}
