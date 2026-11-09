// Decompile the functions at the given addresses and the functions they call directly (one level).
// An argument f:<hex addr> prints the float stored there instead. Read-only. Session tf2-weapons, 2026-11-08.
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript DecompAt.java <out.txt> <hex addr> [<hex addr> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class DecompAt extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Set<Function> funcs = new LinkedHashSet<>();
		StringBuilder vals = new StringBuilder();
		for (int i = 1; i < args.length; i++) {
			if (args[i].startsWith("d:")) {
				Address da = toAddr(args[i].substring(2));
				vals.append("// double @" + da + " = " + getDouble(da) + System.lineSeparator());
				continue;
			}
			if (args[i].startsWith("f:")) {
				Address fa = toAddr(args[i].substring(2));
				vals.append("// float @" + fa + " = " + getFloat(fa) + System.lineSeparator());
				continue;
			}
			Address a = toAddr(args[i]);
			Function f = getFunctionAt(a);
			if (f == null)
				f = getFunctionContaining(a);
			if (f == null)
				continue;
			funcs.add(f);
			for (Function c : f.getCalledFunctions(monitor))
				funcs.add(c);
		}
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		try (PrintWriter out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			out.print(vals);
			for (Function f : funcs) {
				out.println("===== " + f.getName() + " @" + f.getEntryPoint());
				DecompileResults r = d.decompileFunction(f, 60, monitor);
				out.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed");
			}
		}
	}
}
