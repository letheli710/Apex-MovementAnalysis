// Read-only: list instructions whose scalar operands match given values, in an address range.
// args: <out.txt> <lo hex> <hi hex> <v1,v2,... hex>
//@category HSD
import java.io.*;
import java.util.*;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
public class ImmScan extends GhidraScript {
	@Override public void run() throws Exception {
		String[] a = getScriptArgs();
		Address lo = toAddr(Long.parseUnsignedLong(a[1], 16)), hi = toAddr(Long.parseUnsignedLong(a[2], 16));
		Set<Long> vals = new HashSet<>();
		for (String s : a[3].split(",")) vals.add(Long.parseLong(s, 16));
		try (PrintWriter w = new PrintWriter(new File(a[0]), "UTF-8")) {
			InstructionIterator it = currentProgram.getListing().getInstructions(new AddressSet(lo, hi), true);
			while (it.hasNext()) {
				Instruction ins = it.next();
				for (int i = 0; i < ins.getNumOperands(); i++)
					for (Object o : ins.getOpObjects(i))
						if (o instanceof Scalar && vals.contains(((Scalar) o).getUnsignedValue())) {
							Function f = getFunctionContaining(ins.getAddress());
							w.println(ins.getAddress() + "\t" + ins + "\t" + (f == null ? "-" : f.getEntryPoint().toString()));
						}
			}
		}
	}
}
