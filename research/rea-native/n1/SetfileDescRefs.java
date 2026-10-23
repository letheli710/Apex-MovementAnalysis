// Setfile key descriptors: .data records whose qword at +0x8 points at the key
// name (record layout seen in N1: +0x0 type/index, +0x8 name, offsets filled at
// runtime). For each key, find the descriptor and every code reference into it.
// Read-only; writes addresses, offsets and function entries only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript SetfileDescRefs.java <keys.txt> <out.tsv>
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;

public class SetfileDescRefs extends GhidraScript {

	private static final long NAME_FIELD = 0x8;
	private static final long SPAN_BEFORE = 0x10;
	private static final long SPAN_AFTER = 0x80;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		MemoryBlock data = currentProgram.getMemory().getBlock(".data");
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("key\tdescriptor\tsite\toffset\tref_type\tfunction");
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
				byte[] ptr = new byte[8];
				long v = s.getOffset();
				for (int i = 0; i < 8; i++) {
					ptr[i] = (byte) (v >>> (8 * i));
				}
				Address hit = currentProgram.getMemory().findBytes(data.getStart(), data.getEnd(), ptr, null, true, monitor);
				int nDesc = 0;
				while (hit != null && nDesc < 4) {
					Address desc = hit.subtract(NAME_FIELD);
					nDesc++;
					boolean any = false;
					for (long off = -SPAN_BEFORE; off < SPAN_AFTER; off += 4) {
						for (Reference r : getReferencesTo(desc.add(off))) {
							Function f = getFunctionContaining(r.getFromAddress());
							w.println(k + "\t" + desc + "\t" + r.getFromAddress() + "\t" + off + "\t"
								+ r.getReferenceType() + "\t" + (f == null ? "" : f.getEntryPoint()));
							any = true;
						}
					}
					if (!any) {
						w.println(k + "\t" + desc + "\tNO_REFS\t\t\t");
					}
					hit = currentProgram.getMemory().findBytes(hit.add(8), data.getEnd(), ptr, null, true, monitor);
				}
				if (nDesc == 0) {
					w.println(k + "\t" + s + "\tNO_DESCRIPTOR\t\t\t");
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
