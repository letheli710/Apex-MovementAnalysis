// Print the instructions in address ranges (disassembly text). Output goes
// under local/ only.
//
// Run: ... -postScript DumpIns.java <out.txt> <start-hex>-<end-hex> [...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class DumpIns extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		try (PrintWriter w = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			for (int i = 1; i < args.length; i++) {
				String[] r = args[i].split("-");
				Address end = toAddr(Long.parseUnsignedLong(r[1], 16));
				w.println("== " + args[i]);
				Instruction ins = getInstructionAt(toAddr(Long.parseUnsignedLong(r[0], 16)));
				while (ins != null && ins.getAddress().compareTo(end) < 0) {
					w.println("  " + ins.getAddress() + "  " + ins);
					ins = ins.getNext();
				}
			}
		}
	}
}
