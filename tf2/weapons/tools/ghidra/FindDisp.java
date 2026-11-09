// List functions whose instructions use a memory operand with one of the given displacements
// (e.g. 0x1ccc = a field offset), and decompile up to 25 of them. Read-only.
// Session tf2-weapons, 2026-11-08.
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript FindDisp.java <out.txt> <hex disp> [<hex disp> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindDisp extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		long[] want = new long[args.length - 1];
		for (int i = 1; i < args.length; i++)
			want[i - 1] = Long.decode(args[i]);
		Map<Function, String> hits = new LinkedHashMap<>();
		InstructionIterator it = currentProgram.getListing().getInstructions(true);
		while (it.hasNext() && !monitor.isCancelled()) {
			Instruction ins = it.next();
			for (int op = 0; op < ins.getNumOperands(); op++) {
				String rep = ins.getDefaultOperandRepresentation(op);
				if (!rep.contains("["))
					continue;
				for (Object o : ins.getOpObjects(op)) {
					if (o instanceof Scalar) {
						long v = ((Scalar) o).getUnsignedValue();
						for (long w : want) {
							if (v == w) {
								Function f = getFunctionContaining(ins.getAddress());
								if (f != null) {
									String prev = hits.getOrDefault(f, "");
									hits.put(f, prev + " " + ins.getAddress() + ":" + ins);
								}
							}
						}
					}
				}
			}
		}
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		try (PrintWriter out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			out.println("// functions: " + hits.size());
			for (Map.Entry<Function, String> e : hits.entrySet())
				out.println("// " + e.getKey().getName() + " @" + e.getKey().getEntryPoint() + " :" + e.getValue());
			int n = 0;
			for (Function f : hits.keySet()) {
				if (n++ >= 25)
					break;
				out.println("===== " + f.getName() + " @" + f.getEntryPoint());
				DecompileResults r = d.decompileFunction(f, 60, monitor);
				out.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed");
			}
		}
	}
}
