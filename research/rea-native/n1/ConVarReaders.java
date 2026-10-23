// For each ConVar name: find its registration, its object address, and every
// instruction outside the registration that references the object.
// Read-only; writes addresses and function names only.
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript ConVarReaders.java <names.txt> <out.tsv>
//
// names.txt: one ConVar name per line; '#' starts a comment.
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;

public class ConVarReaders extends GhidraScript {

	// Registration stores the name pointer at object+0x18 (N0).
	private static final long NAME_OFFSET = 0x18;
	// Object fields scanned for readers: header through the cached values.
	private static final long SCAN_SPAN = 0x70;

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		List<String> names = new ArrayList<>();
		for (String line : Files.readAllLines(new File(args[0]).toPath(), StandardCharsets.UTF_8)) {
			String s = line.trim();
			if (!s.isEmpty() && !s.startsWith("#")) {
				names.add(s);
			}
		}
		try (PrintWriter w = new PrintWriter(new File(args[1]), StandardCharsets.UTF_8)) {
			w.println("convar\tobject\tregistration\tsite\toffset\tref_type\tfunction\tfunction_name");
			for (String n : names) {
				monitor.checkCancelled();
				Address str = findCString(n);
				if (str == null) {
					w.println(n + "\tNO_STRING\t\t\t\t\t\t");
					continue;
				}
				boolean any = false;
				for (Reference r : getReferencesTo(str)) {
					Address base = objectFromNameStore(r.getFromAddress());
					if (base == null) {
						continue;
					}
					any = true;
					Function reg = getFunctionContaining(r.getFromAddress());
					for (long off = 0; off < SCAN_SPAN; off += 4) {
						for (Reference x : getReferencesTo(base.add(off))) {
							Function f = getFunctionContaining(x.getFromAddress());
							if (f != null && f.equals(reg)) {
								continue;
							}
							w.println(n + "\t" + base + "\t" + (reg == null ? "" : reg.getEntryPoint()) + "\t"
								+ x.getFromAddress() + "\t0x" + Long.toHexString(off) + "\t" + x.getReferenceType()
								+ "\t" + (f == null ? "" : f.getEntryPoint()) + "\t" + (f == null ? "" : f.getName()));
						}
					}
				}
				if (!any) {
					w.println(n + "\tNO_OBJECT\t\t\t\t\t\t");
				}
			}
		}
	}

	// The store right after the string load: MOV [object+0x18], reg.
	private Address objectFromNameStore(Address site) {
		Instruction ins = getInstructionAt(site);
		for (int i = 0; ins != null && i < 4; i++) {
			for (Reference r : ins.getReferencesFrom()) {
				MemoryBlock b = getMemoryBlock(r.getToAddress());
				if (r.getReferenceType().isWrite() && b != null && b.isWrite()) {
					return r.getToAddress().subtract(NAME_OFFSET);
				}
			}
			ins = ins.getNext();
		}
		return null;
	}

	private Address findCString(String s) throws Exception {
		byte[] pat = (s + "\0").getBytes(StandardCharsets.US_ASCII);
		Address a = currentProgram.getMemory().findBytes(currentProgram.getMinAddress(), pat, null, true, monitor);
		// Skip matches that are the tail of a longer string.
		while (a != null) {
			try {
				byte prev = getByte(a.subtract(1));
				if (prev == 0) {
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
