// Decompile a list of functions to one text file, for reading in N2.
// The output contains decompiled game code: write it under local/ only (the
// folder is git-ignored; the research repository is public). Read-only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript DecompileList.java <list.txt> <out.c>
//
// list.txt: one entry address (hex) per line, optional label after a TAB;
// '#' starts a comment.
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class DecompileList extends GhidraScript {

	private static final int TIMEOUT_S = 180;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		DecompInterface di = new DecompInterface();
		di.openProgram(currentProgram);
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
				String s = line.trim();
				if (s.isEmpty() || s.startsWith("#")) {
					continue;
				}
				String[] t = s.split("\t");
				Function f = getFunctionAt(toAddr(Long.parseUnsignedLong(t[0], 16)));
				w.println("//==== " + t[0] + (t.length > 1 ? " " + t[1] : ""));
				if (f == null) {
					w.println("// no function");
					continue;
				}
				DecompileResults r = di.decompileFunction(f, TIMEOUT_S, monitor);
				w.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// failed: " + r.getErrorMessage());
			}
		}
		di.dispose();
	}
}
