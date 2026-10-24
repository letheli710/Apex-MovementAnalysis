// List every instruction whose memory operand uses a given displacement, e.g.
// 0x1c7 for "byte at object + 0x1c7". Prints one TSV row per hit: address,
// containing function (entry and name), read/write, operand size, instruction.
// Addresses and mnemonics only, no decompiled code. Read-only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript FindOffsetRefs.java <hex disp> <out.tsv>
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.OperandType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class FindOffsetRefs extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		long disp = Long.parseUnsignedLong(args[0].replace("0x", ""), 16);
		int hits = 0;
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("addr\tfunc\tfunc_name\trw\tinsn");
			InstructionIterator it = currentProgram.getListing().getInstructions(true);
			while (it.hasNext() && !monitor.isCancelled()) {
				Instruction in = it.next();
				for (int op = 0; op < in.getNumOperands(); op++) {
					int t = in.getOperandType(op);
					if ((t & OperandType.DYNAMIC) == 0) {
						continue;
					}
					boolean match = false;
					for (Object o : in.getOpObjects(op)) {
						if (o instanceof Scalar && ((Scalar) o).getUnsignedValue() == disp) {
							match = true;
						}
					}
					if (!match) {
						continue;
					}
					Function f = getFunctionContaining(in.getAddress());
					String rw = (op == 0 && in.getNumOperands() > 1) ? "W" : "R";
					w.println(in.getAddress() + "\t" + (f == null ? "" : f.getEntryPoint()) + "\t"
							+ (f == null ? "" : f.getName()) + "\t" + rw + "\t" + in);
					hits++;
				}
			}
		}
		println("hits " + hits);
	}
}
