// For each setfile key name: list every reference to its string, with the
// containing function (code refs) or the raw qwords around the site (data refs,
// e.g. a key table). Read-only; writes addresses and numbers only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript SetfileKeyRefs.java <keys.txt> <out.tsv>
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

public class SetfileKeyRefs extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("key\tstring\tsite\tref_type\tfunction\tqwords_at_site");
			for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
				String k = line.trim();
				if (k.isEmpty() || k.startsWith("#")) {
					continue;
				}
				Address s = findCString(k);
				if (s == null) {
					w.println(k + "\tNO_STRING\t\t\t\t");
					continue;
				}
				int n = 0;
				for (Reference r : getReferencesTo(s)) {
					Address from = r.getFromAddress();
					Function f = getFunctionContaining(from);
					StringBuilder q = new StringBuilder();
					if (f == null) {
						for (int i = -2; i < 4; i++) {
							try {
								q.append(String.format("%016x ", getLong(from.add(i * 8L))));
							}
							catch (Exception e) {
								q.append("? ");
							}
						}
					}
					w.println(k + "\t" + s + "\t" + from + "\t" + r.getReferenceType() + "\t"
						+ (f == null ? "" : f.getEntryPoint() + " " + f.getName()) + "\t" + q.toString().trim());
					if (++n >= 12) {
						break;
					}
				}
				if (n == 0) {
					w.println(k + "\t" + s + "\tNO_REFS\t\t\t");
				}
			}
		}
	}

	private Address findCString(String s) throws Exception {
		byte[] pat = (s + "\0").getBytes(StandardCharsets.US_ASCII);
		Address a = currentProgram.getMemory().findBytes(currentProgram.getMinAddress(), pat, null, true, monitor);
		while (a != null) {
			try {
				if (getByte(a.subtract(1)) == 0) {
					return a;
				}
			}
			catch (Exception e) {
				return a;
			}
			a = currentProgram.getMemory().findBytes(a.add(1), pat, null, true, monitor);
		}
		return null;
	}
}
