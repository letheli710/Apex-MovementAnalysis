// Addresses, floats and field-table entries around the view model FOV code. Read-only.
//@category HSD
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.listing.Function;

public class FovBits extends GhidraScript {
	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Memory m = currentProgram.getMemory();
		try (PrintWriter w = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			long[] floats = {0x1417f8a74L, 0x1417f87a8L, 0x1417f7fb4L, 0x1417f8474L, 0x1417f829cL, 0x1417f80d0L, 0x1417f8ab8L, 0x1417f8e98L, 0x1417f8034L, 0x1417f8098L, 0x1417f8a24L};
			for (long a : floats) {
				w.println(String.format("float %x = %f", a, Float.intBitsToFloat(m.getInt(toAddr(a)))));
			}
			w.println("int 141abeee8 = " + m.getInt(toAddr(0x141abeee8L)));
			w.println("int 14989e844 = " + m.getInt(toAddr(0x14989e844L)));
			// field tables: zoom_fov and zoom_fov_viewmodel entries, and every string named on the command line
			long[][] ranges = {{0x140100d70L, 0x140100ef0L}};
			for (long[] r : ranges) {
				Instruction ins = getInstructionAt(toAddr(r[0]));
				while (ins != null && ins.getAddress().getOffset() < r[1]) {
					w.println(ins.getAddress() + " " + ins);
					ins = ins.getNext();
				}
			}
			for (int i = 1; i < args.length; i++) {
				byte[] pat = (args[i] + "\0").getBytes(StandardCharsets.US_ASCII);
				Address a = m.getMinAddress();
				while (true) {
					a = m.findBytes(a, pat, null, true, monitor);
					if (a == null) break;
					byte prev = 0;
					try { prev = m.getByte(a.subtract(1)); } catch (Exception e) { prev = 0; }
					if (prev == 0) {
						for (Reference r : getReferencesTo(a)) {
							Address from = r.getFromAddress();
							Function f = getFunctionContaining(from);
							w.println("== " + args[i] + " @ " + a + " ref " + from + " in " + (f == null ? "?" : f.getEntryPoint().toString()));
							Instruction ins = getInstructionAt(from);
							for (int k = 0; k < 12 && ins != null; k++) {
								w.println("    " + ins.getAddress() + " " + ins);
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
