// Dump the decompiled registration code for a list of ConVar names.
// For every name string in the program, follow its references, decompile the
// containing function, and print the lines around the reference. Read-only:
// the script never changes the program.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript DumpConVarRegistrations.java <names.txt> <out.txt>
//
// names.txt: one ConVar name per line; '#' starts a comment.
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;

public class DumpConVarRegistrations extends GhidraScript {

	// Static ConVar initializers set the default value before they store the
	// name, so keep the whole (short) function above the name.
	private static final int CONTEXT_BEFORE = 80;
	private static final int CONTEXT_AFTER = 24;
	private static final int DECOMPILE_TIMEOUT_S = 120;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length != 2) {
			printerr("usage: DumpConVarRegistrations.java <names.txt> <out.txt>");
			return;
		}
		List<String> names = readNames(new File(args[0]));

		DecompInterface decomp = new DecompInterface();
		decomp.openProgram(currentProgram);

		try (PrintWriter out = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			out.println("# ConVar registration dump");
			out.println("program: " + currentProgram.getName());
			out.println("sha256: " + currentProgram.getExecutableSHA256());
			out.println("image_base: " + currentProgram.getImageBase());
			out.println("ghidra: " + Application.getApplicationVersion());
			out.println("script: DumpConVarRegistrations.java");
			out.println();

			Memory mem = currentProgram.getMemory();
			for (String name : names) {
				monitor.checkCancelled();
				out.println("## " + name);
				byte[] pattern = ("\0" + name + "\0").getBytes(StandardCharsets.US_ASCII);
				Address hit = mem.findBytes(mem.getMinAddress(), pattern, null, true, monitor);
				if (hit == null) {
					out.println("string: not found");
					out.println();
					continue;
				}
				Address str = hit.add(1);
				out.println("string: " + str);

				Set<Function> seen = new LinkedHashSet<>();
				Reference[] refs = getReferencesTo(str);
				if (refs.length == 0) {
					out.println("refs: none");
				}
				for (Reference ref : refs) {
					Address from = ref.getFromAddress();
					Function fn = getFunctionContaining(from);
					out.println("ref: " + from + " (" + ref.getReferenceType() + ") in "
						+ (fn == null ? "<no function>" : fn.getName() + " @ " + fn.getEntryPoint()));
					if (fn == null || !seen.add(fn)) {
						continue;
					}
					DecompileResults res = decomp.decompileFunction(fn, DECOMPILE_TIMEOUT_S, monitor);
					if (!res.decompileCompleted()) {
						out.println("decompile: failed (" + res.getErrorMessage() + ")");
						continue;
					}
					String c = res.getDecompiledFunction().getC();
					printDefault(out, c, name);
					printContext(out, c, name);
				}
				out.println();
			}
		}
		finally {
			decomp.dispose();
		}
	}

	private List<String> readNames(File f) throws Exception {
		List<String> names = new ArrayList<>();
		for (String line : Files.readAllLines(f.toPath(), StandardCharsets.UTF_8)) {
			String s = line.replaceAll("#.*", "").trim();
			if (!s.isEmpty()) {
				names.add(s);
			}
		}
		return names;
	}

	// A static ConVar initializer copies its default value from a string literal:
	//   DAT_obj_c8 = &DAT_<literal>;  DAT_obj_d8 = <length incl. NUL>;
	// Print the first such literal above the name assignment, read from program
	// memory, with its address and the copy length.
	private void printDefault(PrintWriter out, String c, String name) {
		int nameAt = c.indexOf("\"" + name + "\"");
		String head = nameAt < 0 ? c : c.substring(0, nameAt);
		java.util.regex.Matcher lit = java.util.regex.Pattern
			.compile("= (?:&(?:DAT|s_[A-Za-z0-9_]+?)_([0-9a-f]{9,16})|\"([^\"]*)\");").matcher(head);
		if (!lit.find()) {
			out.println("default: <no literal found>");
			return;
		}
		// The copy length is the first small non-zero constant after the literal.
		java.util.regex.Matcher len = java.util.regex.Pattern
			.compile("= ([1-9][0-9]?);").matcher(head.substring(lit.end()));
		String lenText = len.find() ? len.group(1) : "?";
		if (lit.group(2) != null) {
			out.println("default: \"" + lit.group(2) + "\" (inline literal, copy length " + lenText + ")");
			return;
		}
		Address a = toAddr(Long.parseUnsignedLong(lit.group(1), 16));
		StringBuilder sb = new StringBuilder();
		try {
			for (int i = 0; i < 256; i++) {
				byte b = getByte(a.add(i));
				if (b == 0) {
					break;
				}
				sb.append((char) (b & 0xff));
			}
		}
		catch (Exception e) {
			out.println("default: <unreadable at " + a + ">");
			return;
		}
		out.println("default: \"" + sb + "\" @ " + a + " (copy length " + lenText + ")");
	}

	// Print the lines around each line that mentions the name (as a literal or a
	// Ghidra string label such as s_sv_gravity_14...).
	private void printContext(PrintWriter out, String c, String name) {
		String[] lines = c.split("\n");
		String label = "s_" + name + "_";
		boolean any = false;
		for (int i = 0; i < lines.length; i++) {
			if (!lines[i].contains("\"" + name + "\"") && !lines[i].contains(label)) {
				continue;
			}
			any = true;
			out.println("```c");
			int lo = Math.max(0, i - CONTEXT_BEFORE);
			int hi = Math.min(lines.length, i + CONTEXT_AFTER + 1);
			for (int j = lo; j < hi; j++) {
				out.println(lines[j]);
			}
			out.println("```");
		}
		if (!any) {
			out.println("decompile: name not visible in output; full function follows");
			out.println("```c");
			out.println(c);
			out.println("```");
		}
	}
}
