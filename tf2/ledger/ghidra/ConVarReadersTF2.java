// TF2 version of R5's n1/ConVarReaders.java. For each ConVar object address,
// list every code reference into the object (offsets -0x10..+0x80) with the
// containing function, then decompile each reader function once into
// <outdir>/<entry>.c. Read-only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript ConVarReadersTF2.java <objects.tsv> <readers.tsv> <outdir>
//
// objects.tsv: "convar<TAB>object_hex" per line, '#' for comments.
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

public class ConVarReadersTF2 extends GhidraScript {

	private static final long SPAN_BEFORE = 0x10;
	private static final long SPAN_AFTER = 0x80;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		File outDir = new File(args[2]);
		outDir.mkdirs();
		Map<Address, Function> readers = new LinkedHashMap<>();
		Map<Address, StringBuilder> readsOf = new TreeMap<>();
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("convar\tobject\tsite\toffset\tref_type\tfunction");
			for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
				String s = line.trim();
				if (s.isEmpty() || s.startsWith("#")) {
					continue;
				}
				String[] f = s.split("\t");
				Address obj = toAddr(Long.parseUnsignedLong(f[1], 16));
				for (long off = -SPAN_BEFORE; off < SPAN_AFTER; off += 4) {
					for (Reference r : getReferencesTo(obj.add(off))) {
						Function fn = getFunctionContaining(r.getFromAddress());
						if (fn == null || isRegistration(fn)) {
							continue;
						}
						w.println(f[0] + "\t" + obj + "\t" + r.getFromAddress() + "\t" + off + "\t"
							+ r.getReferenceType() + "\t" + fn.getEntryPoint());
						readers.putIfAbsent(fn.getEntryPoint(), fn);
						readsOf.computeIfAbsent(fn.getEntryPoint(), k -> new StringBuilder()).append(f[0]).append(' ');
					}
				}
			}
		}
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		try {
			for (Function fn : readers.values()) {
				monitor.checkCancelled();
				DecompileResults res = d.decompileFunction(fn, 180, monitor);
				try (PrintWriter w = new PrintWriter(new File(outDir, fn.getEntryPoint() + ".c"), StandardCharsets.UTF_8)) {
					w.println("// " + currentProgram.getName() + " " + fn.getEntryPoint() + " size " + fn.getBody().getNumAddresses());
					w.println("// reads: " + readsOf.get(fn.getEntryPoint()));
					w.println(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "// decompile failed: " + res.getErrorMessage());
				}
			}
		}
		finally {
			d.dispose();
		}
	}

	// The static registration stub and its atexit destructor also reference the
	// object; they are tiny and contain no movement logic.
	private boolean isRegistration(Function fn) {
		return fn.getBody().getNumAddresses() < 0x40;
	}
}
