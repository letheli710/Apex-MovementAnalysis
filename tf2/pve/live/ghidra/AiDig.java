// Small read-only digging commands for server.dll, written to one output file.
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript AiDig.java <out.txt> <cmd> [<cmd> ...]
//
// commands (addresses in hex without 0x):
//   dis:<addr>:<n>        n instructions before and after addr
//   dec:<addr>            decompile the function containing addr
//   up:<addr>:<depth>     decompile the function containing addr and its callers, depth levels
//   down:<addr>           decompile the function containing addr and every function it calls
//   ptr:<addr>            find 8-byte pointers to addr anywhere in initialized memory; print the
//                         16 qwords around each, resolved to strings / functions
//   q:<addr>:<n>          n qwords from addr, resolved; also as dwords and floats
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

public class AiDig extends GhidraScript {

	private PrintWriter out;
	private DecompInterface dec;
	private final Set<Function> done = new LinkedHashSet<>();

	private Address a(String hex) {
		return toAddr(Long.parseUnsignedLong(hex, 16));
	}

	private String res(long v) {
		try {
			Address p = toAddr(v);
			Function f = getFunctionAt(p);
			if (f != null)
				return String.format("0x%x=fn %s", v, f.getName());
			Data d = getDataAt(p);
			if (d != null && d.getValue() instanceof String)
				return String.format("0x%x=\"%s\"", v, d.getValue());
		} catch (Exception e) {
		}
		return String.format("0x%x", v);
	}

	private void decompile(Function f, String why) {
		if (f == null || done.contains(f))
			return;
		done.add(f);
		out.println("\n===== " + f.getName() + " @" + f.getEntryPoint() + " (" + why + ")");
		DecompileResults r = dec.decompileFunction(f, 180, monitor);
		out.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed");
	}

	private void up(Function f, int depth, String why) {
		if (f == null)
			return;
		decompile(f, why);
		if (depth <= 0)
			return;
		for (Function c : f.getCallingFunctions(monitor))
			up(c, depth - 1, "caller of " + f.getName());
	}

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Memory mem = currentProgram.getMemory();
		dec = new DecompInterface();
		dec.openProgram(currentProgram);
		out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8);
		out.println("program: " + currentProgram.getName() + " sha256: " + currentProgram.getExecutableSHA256()
			+ " ghidra: " + Application.getApplicationVersion());
		for (int i = 1; i < args.length; i++) {
			String[] c = args[i].split(":");
			out.println("\n######## " + args[i]);
			switch (c[0]) {
			case "dis": {
				int n = Integer.parseInt(c[2]);
				Instruction ins = getInstructionContaining(a(c[1]));
				for (int k = 0; k < n && ins != null && ins.getPrevious() != null; k++)
					ins = ins.getPrevious();
				for (int k = 0; k < 2 * n + 1 && ins != null; k++, ins = ins.getNext()) {
					StringBuilder sb = new StringBuilder(ins.getAddress() + "  " + ins);
					for (ghidra.program.model.symbol.Reference r : ins.getReferencesFrom())
						sb.append("   ; -> " + res(r.getToAddress().getOffset()));
					out.println(sb);
				}
				break;
			}
			case "dec":
				decompile(getFunctionContaining(a(c[1])), "dec");
				break;
			case "xref": {
				for (ghidra.program.model.symbol.Reference r : getReferencesTo(a(c[1]))) {
					Function f = getFunctionContaining(r.getFromAddress());
					Instruction ins = getInstructionAt(r.getFromAddress());
					out.println("  " + r.getFromAddress() + " " + r.getReferenceType() + " in "
						+ (f != null ? f.getName() + " @" + f.getEntryPoint() : "-") + "  " + (ins != null ? ins.toString() : ""));
				}
				break;
			}
			case "sel": { // name -> function table entries: strings starting with c[1]
				ghidra.program.model.listing.DataIterator di = currentProgram.getListing().getDefinedData(true);
				while (di.hasNext()) {
					Data d = di.next();
					if (!(d.getValue() instanceof String) || !((String) d.getValue()).startsWith(c[1]))
						continue;
					StringBuilder sb = new StringBuilder(d.getValue() + " :");
					for (ghidra.program.model.symbol.Reference r : getReferencesTo(d.getAddress())) {
						Instruction ins = getInstructionAt(r.getFromAddress());
						for (int k = 0; k < 14 && ins != null; k++, ins = ins.getPrevious()) {
							String t = ins.toString();
							if (t.startsWith("MOV qword ptr [RCX],R") || t.startsWith("MOV qword ptr [RCX],qword")) {
								for (ghidra.program.model.symbol.Reference rf : ins.getReferencesFrom())
									sb.append(" " + res(rf.getToAddress().getOffset()));
								break;
							}
							if (k > 0 && t.contains("SelectSchedule_"))
								break;
						}
						sb.append(" [ref " + r.getFromAddress() + "]");
						break; // first reference is the table store
					}
					out.println(sb);
				}
				break;
			}
			case "schema": { // schema:<key name>:<stride>  dump the name table around a pointer to that key
				int stride = Integer.parseInt(c[2]);
				Address str = null;
				ghidra.program.model.listing.DataIterator di = currentProgram.getListing().getDefinedData(true);
				while (di.hasNext() && str == null) {
					Data d = di.next();
					if (d.getValue() instanceof String && d.getValue().equals(c[1]))
						str = d.getAddress();
				}
				if (str == null) {
					out.println("no string");
					break;
				}
				long target = str.getOffset();
				byte[] pat = new byte[8];
				for (int k = 0; k < 8; k++)
					pat[k] = (byte) (target >>> (8 * k));
				Address hit = null;
				for (MemoryBlock b : mem.getBlocks())
					if (b.isInitialized() && hit == null)
						hit = mem.findBytes(b.getStart(), b.getEnd(), pat, null, true, monitor);
				if (hit == null) {
					out.println("no pointer");
					break;
				}
				Address s = hit;
				while (true) {
					Address p = s.subtract(stride);
					Data d = getDataAt(toAddr(mem.getLong(p)));
					if (d == null || !(d.getValue() instanceof String))
						break;
					s = p;
				}
				for (Address e = s;; e = e.add(stride)) {
					Data d = getDataAt(toAddr(mem.getLong(e)));
					if (d == null || !(d.getValue() instanceof String))
						break;
					StringBuilder sb = new StringBuilder(e + " " + d.getValue());
					for (int k = 8; k < stride; k += 8)
						sb.append(String.format(" %016x", mem.getLong(e.add(k))));
					out.println(sb);
				}
				break;
			}
			case "strs": { // strs:<prefix>  strings starting with prefix, each with its references
				ghidra.program.model.listing.DataIterator di = currentProgram.getListing().getDefinedData(true);
				while (di.hasNext()) {
					Data d = di.next();
					if (!(d.getValue() instanceof String) || !((String) d.getValue()).startsWith(c[1]))
						continue;
					StringBuilder sb = new StringBuilder(d.getAddress() + " " + d.getValue() + " :");
					for (ghidra.program.model.symbol.Reference r : getReferencesTo(d.getAddress())) {
						Function f = getFunctionContaining(r.getFromAddress());
						sb.append(" " + r.getFromAddress() + (f != null ? "(" + f.getName() + ")" : "(data)"));
					}
					out.println(sb);
				}
				break;
			}
			case "disp": { // disp:<hex>[,<hex>...]  functions with instructions using "+ 0x<hex>]" displacements
				String[] ds = c[1].split("/");
				java.util.Map<String, java.util.Map<String, Integer>> hits = new java.util.TreeMap<>();
				ghidra.program.model.listing.InstructionIterator it = currentProgram.getListing().getInstructions(true);
				while (it.hasNext()) {
					Instruction ins = it.next();
					String t = ins.toString();
					for (String dsp : ds) {
						if (t.contains("+ 0x" + dsp + "]")) {
							Function f = getFunctionContaining(ins.getAddress());
							String fn = f != null ? f.getName() + "@" + f.getEntryPoint() : "-";
							hits.computeIfAbsent(fn, k -> new java.util.TreeMap<>()).merge(dsp, 1, Integer::sum);
						}
					}
				}
				for (java.util.Map.Entry<String, java.util.Map<String, Integer>> e : hits.entrySet())
					if (e.getValue().size() >= Math.min(2, ds.length))
						out.println("  " + e.getKey() + " " + e.getValue());
				break;
			}
			case "f": { // c[1] = address of a float, c[2] = count
				Address s = a(c[1]);
				int n = Integer.parseInt(c[2]);
				for (int k = 0; k < n; k++) {
					Address q = s.add(4L * k);
					int v = mem.getInt(q);
					out.println(String.format("   %s float %g int %d", q, Float.intBitsToFloat(v), v));
				}
				break;
			}
			case "d": { // double
				Address s = a(c[1]);
				out.println(String.format("   %s double %g", s, Double.longBitsToDouble(mem.getLong(s))));
				break;
			}
			case "up":
				up(getFunctionContaining(a(c[1])), Integer.parseInt(c[2]), "up");
				break;
			case "down": {
				Function f = getFunctionContaining(a(c[1]));
				decompile(f, "down");
				for (Function g : f.getCalledFunctions(monitor))
					decompile(g, "called by " + f.getName());
				break;
			}
			case "ptr": {
				long target = Long.parseUnsignedLong(c[1], 16);
				byte[] pat = new byte[8];
				for (int k = 0; k < 8; k++)
					pat[k] = (byte) (target >>> (8 * k));
				for (MemoryBlock b : mem.getBlocks()) {
					if (!b.isInitialized())
						continue;
					Address s = b.getStart();
					while (s != null && s.compareTo(b.getEnd()) <= 0) {
						Address hit = mem.findBytes(s, b.getEnd(), pat, null, true, monitor);
						if (hit == null)
							break;
						out.println("ptr at " + hit + " (" + b.getName() + ")");
						for (int k = -8; k < 8; k++) {
							Address q = hit.add(8L * k);
							out.println(String.format("   %+d %s %s", k, q, res(mem.getLong(q))));
						}
						s = hit.add(1);
					}
				}
				break;
			}
			case "q": {
				Address s = a(c[1]);
				int n = Integer.parseInt(c[2]);
				for (int k = 0; k < n; k++) {
					Address q = s.add(8L * k);
					long v = mem.getLong(q);
					int lo = (int) v, hi = (int) (v >>> 32);
					out.println(String.format("   %s %s  | %d %d | %g %g", q, res(v), lo, hi,
						Float.intBitsToFloat(lo), Float.intBitsToFloat(hi)));
				}
				break;
			}
			default:
				out.println("unknown command");
			}
			out.flush();
		}
		out.close();
		dec.dispose();
	}
}
