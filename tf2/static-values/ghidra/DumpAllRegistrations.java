// Dump every call to the given ConVar registration functions as one line of
// decompiled C, so all ConVars (not just a name list) get a default and object.
// Read-only. Output feeds parse_convar_dump.py (same "## name" block format).
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript DumpAllRegistrations.java <out.txt> <reg_fn_hex> [<reg_fn_hex> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

public class DumpAllRegistrations extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		DecompInterface d = new DecompInterface();
		d.openProgram(currentProgram);
		Pattern name = Pattern.compile("\\(&?(?:DAT|PTR)_[0-9a-f]+,\\s*\"([^\"]+)\"");
		try (PrintWriter out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8)) {
			out.println("# ConVar registration dump (all callers)");
			out.println("program: " + currentProgram.getName());
			out.println("sha256: " + currentProgram.getExecutableSHA256());
			out.println("ghidra: " + Application.getApplicationVersion());
			out.println();
			for (int i = 1; i < args.length; i++) {
				Function reg = getFunctionAt(toAddr(Long.parseUnsignedLong(args[i], 16)));
				Set<Function> callers = new LinkedHashSet<>();
				for (Reference r : getReferencesTo(reg.getEntryPoint())) {
					Function f = getFunctionContaining(r.getFromAddress());
					if (f != null) {
						callers.add(f);
					}
				}
				for (Function f : callers) {
					monitor.checkCancelled();
					DecompileResults res = d.decompileFunction(f, 60, monitor);
					if (!res.decompileCompleted()) {
						continue;
					}
					String c = res.getDecompiledFunction().getC();
					// one block per registration call in the caller
					String flat = c.replaceAll("\\s*\\n\\s*", " ");
					Matcher m = Pattern.compile(reg.getName() + "\\([^;]*\\);").matcher(flat);
					while (m.find()) {
						Matcher n = name.matcher(m.group());
						if (!n.find()) {
							continue;
						}
						out.println("## " + n.group(1));
						out.println("ref: " + f.getEntryPoint() + " (CALL) in " + f.getName() + " @ " + f.getEntryPoint());
						out.println(m.group());
						out.println();
					}
				}
			}
		}
		finally {
			d.dispose();
		}
	}
}
