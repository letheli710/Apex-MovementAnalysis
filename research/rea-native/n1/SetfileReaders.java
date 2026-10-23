// Setfile reads: for each descriptor from scan_setfile_desc.py, list the code
// sites that read its runtime index field (+0x0). Read-only; writes addresses
// and function entries only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript SetfileReaders.java <descriptors.tsv> <out.tsv>
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;

public class SetfileReaders extends GhidraScript {

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("key\ttype\tdescriptor\tsite\tfunction");
			boolean header = true;
			for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
				if (header) {
					header = false;
					continue;
				}
				String[] t = line.split("\t");
				Address desc = toAddr(Long.parseUnsignedLong(t[0], 16));
				int n = 0;
				for (Reference r : getReferencesTo(desc)) {
					if (!r.getReferenceType().isRead()) {
						continue;
					}
					Function f = getFunctionContaining(r.getFromAddress());
					if (f == null) {
						continue;
					}
					w.println(t[2] + "\t" + t[1] + "\t" + desc + "\t" + r.getFromAddress() + "\t" + f.getEntryPoint());
					n++;
				}
				if (n == 0) {
					w.println(t[2] + "\t" + t[1] + "\t" + desc + "\tNO_READS\t");
				}
			}
		}
	}
}
