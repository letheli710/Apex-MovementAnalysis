// Decompile every function that references a symbol whose name contains one of the given
// substrings (e.g. an RTTI vftable "CTraceFilterGrenadeArc") or a defined string equal to
// one of them, plus the direct callers of those functions. Read-only.
//
//   analyzeHeadless <projdir> tf2 -process client.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript DumpRefsDecomp.java <out.txt> <needle> [<needle> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

public class DumpRefsDecomp extends GhidraScript {

	private final Map<Function, String> funcs = new LinkedHashMap<>();

	private void addRefs(Address target, String why) {
		for (Reference r : getReferencesTo(target)) {
			Function f = getFunctionContaining(r.getFromAddress());
			if (f != null && !funcs.containsKey(f))
				funcs.put(f, why + " @" + r.getFromAddress());
		}
	}

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		for (int i = 1; i < args.length; i++) {
			String needle = args[i];
			if (needle.startsWith("0x")) { // a function by address, without callers
				Function f = getFunctionAt(toAddr(Long.parseUnsignedLong(needle.substring(2), 16)));
				if (f != null)
					funcs.put(f, "addr " + needle);
				continue;
			}
			SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
			while (it.hasNext()) {
				Symbol s = it.next();
				if (s.getName(true).contains(needle))
					addRefs(s.getAddress(), "sym " + s.getName(true));
			}
			DataIterator di = currentProgram.getListing().getDefinedData(true);
			while (di.hasNext()) {
				Data d = di.next();
				Object v = d.getValue();
				if (v instanceof String && v.equals(needle))
					addRefs(d.getAddress(), "str " + needle);
			}
		}
		Map<Function, String> callers = new LinkedHashMap<>();
		for (Function f : funcs.keySet())
			if (!funcs.get(f).startsWith("addr "))
				for (Function c : f.getCallingFunctions(monitor))
				if (!funcs.containsKey(c) && !callers.containsKey(c))
					callers.put(c, "caller of " + f.getName());
		funcs.putAll(callers);
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		try (PrintWriter out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			out.println("program: " + currentProgram.getName() + " sha256: " + currentProgram.getExecutableSHA256()
				+ " ghidra: " + Application.getApplicationVersion());
			for (Map.Entry<Function, String> e : funcs.entrySet()) {
				out.println("\n===== " + e.getKey().getName() + " @" + e.getKey().getEntryPoint() + " (" + e.getValue() + ")");
				DecompileResults res = d.decompileFunction(e.getKey(), 120, monitor);
				out.println(res.decompileCompleted() ? res.getDecompiledFunction().getC() : "// decompile failed");
			}
		}
		d.dispose();
	}
}
