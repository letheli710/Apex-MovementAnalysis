// List every code reference to the given data addresses (one TSV row per
// reference: target, from address, containing function, ref type, instruction).
// Addresses and mnemonics only, no decompiled code. Read-only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript RefsToAddrs.java <out.tsv> <hex addr> [<hex addr> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;

public class RefsToAddrs extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		try (PrintWriter w = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			w.println("target\tfrom\tfunc\tfunc_name\ttype\tinsn");
			for (int i = 1; i < args.length; i++) {
				Address a = toAddr(Long.parseUnsignedLong(args[i].replace("0x", ""), 16));
				for (Reference r : getReferencesTo(a)) {
					Address from = r.getFromAddress();
					Function f = getFunctionContaining(from);
					Instruction in = getInstructionAt(from);
					w.println(a + "\t" + from + "\t" + (f == null ? "" : f.getEntryPoint()) + "\t"
							+ (f == null ? "" : f.getName()) + "\t" + r.getReferenceType() + "\t"
							+ (in == null ? "" : in.toString()));
				}
			}
		}
	}
}
