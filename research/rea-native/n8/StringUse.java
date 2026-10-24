// For each name string, list the instructions that reference it and the
// function / data addresses loaded nearby (script bindings register a name
// next to the native function pointer). Output: addresses and names only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript StringUse.java <out.txt> <name> [<name> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;

public class StringUse extends GhidraScript {

	private static final int AFTER = 14;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Memory mem = currentProgram.getMemory();
		try (PrintWriter w = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			for (int i = 1; i < args.length; i++) {
				byte[] pat = (args[i] + "\0").getBytes(StandardCharsets.US_ASCII);
				Address a = mem.getMinAddress();
				while (true) {
					a = mem.findBytes(a, pat, null, true, monitor);
					if (a == null) {
						break;
					}
					// whole string only: the byte before must be 0
					byte prev = 1;
					try {
						prev = mem.getByte(a.subtract(1));
					} catch (Exception e) {
						prev = 0;
					}
					if (prev == 0) {
						w.println("== " + args[i] + " @ " + a);
						for (Reference r : getReferencesTo(a)) {
							Address from = r.getFromAddress();
							Function f = getFunctionContaining(from);
							w.println("  ref " + from + " in " + (f == null ? "?" : f.getName() + "@" + f.getEntryPoint()));
							Instruction ins = getInstructionAt(from);
							for (int k = 0; k < AFTER && ins != null; k++) {
								StringBuilder sb = new StringBuilder();
								for (Reference rr : ins.getReferencesFrom()) {
									Address t = rr.getToAddress();
									Function tf = getFunctionAt(t);
									sb.append(" ").append(t).append(tf != null ? "(fn " + tf.getName() + ")" : "");
								}
								w.println("    " + ins.getAddress() + " " + ins.getMnemonicString() + sb);
								ins = ins.getNext();
							}
						}
					}
					a = a.add(1);
				}
			}
		}
	}
}
