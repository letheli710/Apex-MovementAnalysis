// Decompile every function whose entry lies in [start, end) into <outdir>/<entry>.c.
// Read-only. Used for TF2 because .set values are read by struct offset (schema
// "offset" column), so readers are found by grepping the decompiled text.
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript DecompileRange.java <start_hex> <end_hex> <outdir>
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

public class DecompileRange extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Address start = toAddr(Long.parseUnsignedLong(args[0], 16));
		Address end = toAddr(Long.parseUnsignedLong(args[1], 16));
		File outDir = new File(args[2]);
		outDir.mkdirs();
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		int n = 0;
		try {
			FunctionIterator it = currentProgram.getFunctionManager().getFunctions(start, true);
			while (it.hasNext()) {
				monitor.checkCancelled();
				Function fn = it.next();
				if (fn.getEntryPoint().compareTo(end) >= 0) {
					break;
				}
				DecompileResults res = d.decompileFunction(fn, 180, monitor);
				try (PrintWriter w = new PrintWriter(new File(outDir, fn.getEntryPoint() + ".c"), StandardCharsets.UTF_8)) {
					w.println("// " + currentProgram.getName() + " " + fn.getEntryPoint() + " size " + fn.getBody().getNumAddresses());
					w.println(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "// decompile failed: " + res.getErrorMessage());
				}
				n++;
			}
		}
		finally {
			d.dispose();
		}
		println("decompiled " + n + " functions");
	}
}
