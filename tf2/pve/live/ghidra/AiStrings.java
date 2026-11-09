// List defined strings that contain one of the given substrings, with every reference to
// each string: the containing function, or for a reference from data (a name -> function
// table) the pointers stored next to it, resolved to functions. Read-only.
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript AiStrings.java <out.txt> <needle> [<needle> ...]
//   a needle starting with "=" must match the whole string
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;

import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;

public class AiStrings extends GhidraScript {

	private String describe(Memory mem, Address a) {
		try {
			long v = mem.getLong(a);
			Address p = toAddr(v);
			Function f = getFunctionAt(p);
			if (f != null)
				return String.format("0x%x=fn %s", v, f.getName());
			Data d = getDataAt(p);
			if (d != null && d.getValue() instanceof String)
				return String.format("0x%x=\"%s\"", v, d.getValue());
			return String.format("0x%x", v);
		} catch (Exception e) {
			return "?";
		}
	}

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		Memory mem = currentProgram.getMemory();
		try (PrintWriter out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			out.println("program: " + currentProgram.getName() + " sha256: " + currentProgram.getExecutableSHA256()
				+ " ghidra: " + Application.getApplicationVersion());
			DataIterator di = currentProgram.getListing().getDefinedData(true);
			while (di.hasNext()) {
				Data d = di.next();
				Object v = d.getValue();
				if (!(v instanceof String))
					continue;
				String s = (String) v;
				boolean hit = false;
				for (int i = 1; i < args.length; i++) {
					String n = args[i];
					if (n.startsWith("=") ? s.equals(n.substring(1)) : s.contains(n)) {
						hit = true;
						break;
					}
				}
				if (!hit)
					continue;
				out.println("STR " + d.getAddress() + " \"" + s + "\"");
				for (Reference r : getReferencesTo(d.getAddress())) {
					Address from = r.getFromAddress();
					Function f = getFunctionContaining(from);
					if (f != null) {
						out.println("  ref " + from + " in " + f.getName() + " @" + f.getEntryPoint());
					} else {
						StringBuilder sb = new StringBuilder("  dataref " + from + " :");
						for (int k = -2; k <= 3; k++)
							sb.append(" [" + k + "] " + describe(mem, from.add(8L * k)));
						out.println(sb);
					}
				}
			}
		}
	}
}
