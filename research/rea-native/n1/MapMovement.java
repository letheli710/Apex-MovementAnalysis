// N1 skeleton map: export the movement functions of an analyzed client, with
// call edges, referenced strings, float constants and ConVar reads.
// Read-only: the script never changes the program, and it writes no
// decompiled code (only addresses, names, strings and constants).
//
// Run (headless, on an analyzed project):
//   analyzeHeadless <projdir> <proj> -process <file> -noanalysis -readOnly
//     -scriptPath <dir> -postScript MapMovement.java <seeds.tsv> <windows.tsv> <outdir>
//
// seeds.tsv:   name <TAB> entry (hex), one per line ('#' comments). Named
//              functions (SDK patterns) that start the walk.
// windows.tsv: label <TAB> start (hex) <TAB> end (hex). Address ranges whose
//              every function belongs to the map (the movement translation units).
//
// Output (TSV): functions.tsv, edges.tsv, strings.tsv, floats.tsv, convars.tsv
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
import ghidra.program.model.symbol.*;

public class MapMovement extends GhidraScript {

	// Callee depth followed outside the windows (helpers such as math or traces).
	private static final int CALLEE_DEPTH = 2;
	// Caller depth followed up from the window functions (the command entry chain).
	private static final int CALLER_DEPTH = 4;
	// Offsets inside a ConVar object that code reads. Movement code reads +0x40
	// (ConVarReaders.java: 88 of 88 reads); the others are the object itself
	// (passed by pointer) and the cached float / int values of the registration.
	private static final long[] CVAR_OFFSETS = { 0x40, 0x0, 0x58, 0x5c, 0x60, 0x64, 0x68 };
	private static final long CVAR_NAME_OFFSET = 0x18;
	private static final long CVAR_HELP_OFFSET = 0x20;
	private static final long CVAR_FLAGS_OFFSET = 0x50;

	private final Map<Address, String> seedNames = new HashMap<>();
	private final List<long[]> windows = new ArrayList<>();
	private final List<String> windowLabels = new ArrayList<>();
	private final Map<Address, String> cvarNameCache = new HashMap<>();

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		if (args.length != 3) {
			printerr("usage: MapMovement.java <seeds.tsv> <windows.tsv> <outdir>");
			return;
		}
		readSeeds(new File(args[0]));
		readWindows(new File(args[1]));
		File out = new File(args[2]);
		out.mkdirs();

		FunctionManager fm = currentProgram.getFunctionManager();

		// 1. Collect the map: window functions, seeds, callers and callees.
		Map<Function, String> why = new LinkedHashMap<>();
		for (Function f : fm.getFunctions(true)) {
			String w = windowOf(f.getEntryPoint());
			if (w != null) {
				why.put(f, "window:" + w);
			}
		}
		for (Address a : seedNames.keySet()) {
			Function f = fm.getFunctionAt(a);
			if (f != null) {
				why.putIfAbsent(f, "seed");
			}
		}
		Set<Function> core = new HashSet<>(why.keySet());
		walk(core, why, true, CALLEE_DEPTH, "callee");
		walk(core, why, false, CALLER_DEPTH, "caller");

		List<Function> funcs = new ArrayList<>(why.keySet());
		funcs.sort(Comparator.comparing(Function::getEntryPoint));
		println("map functions: " + funcs.size());

		try (PrintWriter fw = writer(out, "functions.tsv");
				PrintWriter ew = writer(out, "edges.tsv");
				PrintWriter sw = writer(out, "strings.tsv");
				PrintWriter flw = writer(out, "floats.tsv");
				PrintWriter cw = writer(out, "convars.tsv")) {
			fw.println("entry\tname\treason\twindow\tsize\tcallers\tcallees\tstrings\tfloats\tconvars");
			ew.println("caller\tcallee");
			sw.println("function\tsite\tstring");
			flw.println("function\tsite\tconst_addr\tvalue");
			cw.println("function\tsite\tconvar\tobject\toffset\taccess");

			for (Function f : funcs) {
				monitor.checkCancelled();
				Set<Function> callees = f.getCalledFunctions(monitor);
				Set<Function> callers = f.getCallingFunctions(monitor);
				for (Function c : callees) {
					ew.println(hex(f) + "\t" + hex(c));
				}
				int nStr = 0, nFlt = 0, nCv = 0;
				InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
				while (it.hasNext()) {
					Instruction ins = it.next();
					for (Reference r : ins.getReferencesFrom()) {
						if (!r.isMemoryReference()) {
							continue;
						}
						Address to = r.getToAddress();
						String s = stringAt(to);
						if (s != null) {
							sw.println(hex(f) + "\t" + ins.getAddress() + "\t" + clean(s));
							nStr++;
							continue;
						}
						String cv = convarAt(to);
						if (cv != null) {
							cw.println(hex(f) + "\t" + ins.getAddress() + "\t" + cv);
							nCv++;
							continue;
						}
						Float v = floatConstAt(to, r);
						if (v != null) {
							flw.println(hex(f) + "\t" + ins.getAddress() + "\t" + to + "\t" + v);
							nFlt++;
						}
					}
				}
				fw.println(hex(f) + "\t" + name(f) + "\t" + why.get(f) + "\t"
					+ nz(windowOf(f.getEntryPoint())) + "\t" + f.getBody().getNumAddresses() + "\t"
					+ callers.size() + "\t" + callees.size() + "\t" + nStr + "\t" + nFlt + "\t" + nCv);
			}
		}
		println("done: " + out);
	}

	// Breadth-first walk from the core set over callees (down) or callers (up).
	private void walk(Set<Function> core, Map<Function, String> why, boolean down, int depth, String tag)
			throws Exception {
		Set<Function> frontier = new HashSet<>(core);
		for (int d = 1; d <= depth; d++) {
			Set<Function> next = new HashSet<>();
			for (Function f : frontier) {
				Set<Function> nb = down ? f.getCalledFunctions(monitor) : f.getCallingFunctions(monitor);
				for (Function g : nb) {
					if (g.isThunk() || g.isExternal()) {
						continue;
					}
					if (!why.containsKey(g)) {
						why.put(g, tag + ":" + d);
						next.add(g);
					}
				}
			}
			frontier = next;
		}
	}

	// A defined or plain NUL-terminated ASCII string in a read-only block.
	private String stringAt(Address a) {
		Data d = getDataAt(a);
		if (d != null && d.hasStringValue()) {
			Object v = d.getValue();
			return v == null ? null : v.toString();
		}
		MemoryBlock b = getMemoryBlock(a);
		if (b == null || b.isWrite() || b.isExecute()) {
			return null;
		}
		StringBuilder sb = new StringBuilder();
		try {
			for (int i = 0; i < 200; i++) {
				byte c = getByte(a.add(i));
				if (c == 0) {
					break;
				}
				if (c < 0x20 || c > 0x7e) {
					return null;
				}
				sb.append((char) c);
			}
		}
		catch (Exception e) {
			return null;
		}
		return sb.length() >= 4 ? sb.toString() : null;
	}

	// A 4-byte float constant read from a read-only block. Plausible values only.
	private Float floatConstAt(Address a, Reference r) {
		if (!r.getReferenceType().isRead()) {
			return null;
		}
		MemoryBlock b = getMemoryBlock(a);
		if (b == null || b.isWrite() || b.isExecute()) {
			return null;
		}
		try {
			float v = Float.intBitsToFloat(getInt(a));
			if (Float.isNaN(v) || Float.isInfinite(v) || v == 0f) {
				return null;
			}
			float m = Math.abs(v);
			if (m < 1e-6f || m > 1e7f) {
				return null;
			}
			return v;
		}
		catch (Exception e) {
			return null;
		}
	}

	// "name<TAB>object<TAB>offset<TAB>access" when the address is a field of a ConVar object.
	private String convarAt(Address a) {
		MemoryBlock b = getMemoryBlock(a);
		if (b == null || !b.isWrite()) {
			return null;
		}
		for (long off : CVAR_OFFSETS) {
			Address base;
			try {
				base = a.subtract(off);
			}
			catch (Exception e) {
				continue;
			}
			String n = convarName(base);
			if (n != null) {
				return n + "\t" + base + "\t0x" + Long.toHexString(off) + "\t" + "ref";
			}
		}
		return null;
	}

	// The ConVar registered at this object, found from the static initializer
	// that stores the name pointer at +0x18 right after loading the string.
	private String convarName(Address base) {
		if (cvarNameCache.containsKey(base)) {
			return cvarNameCache.get(base);
		}
		String found = null;
		Address nameSlot = base.add(CVAR_NAME_OFFSET);
		for (Reference r : getReferencesTo(nameSlot)) {
			if (!r.getReferenceType().isWrite()) {
				continue;
			}
			Instruction ins = getInstructionAt(r.getFromAddress());
			for (int back = 0; ins != null && back < 4 && found == null; back++) {
				for (Reference rr : ins.getReferencesFrom()) {
					String s = stringAt(rr.getToAddress());
					if (s != null && s.matches("[A-Za-z_][A-Za-z0-9_]*")) {
						found = s;
						break;
					}
				}
				ins = ins.getPrevious();
			}
			if (found != null && !isConVarInit(getFunctionContaining(r.getFromAddress()), base)) {
				found = null;
			}
			if (found != null) {
				break;
			}
		}
		cvarNameCache.put(base, found);
		return found;
	}

	// The same static initializer must also store the help string (+0x20) and
	// the flags (+0x50), as every ConVar registration seen in N0 does.
	private boolean isConVarInit(Function init, Address base) {
		if (init == null) {
			return false;
		}
		return writesFrom(init, base.add(CVAR_HELP_OFFSET)) && writesFrom(init, base.add(CVAR_FLAGS_OFFSET));
	}

	private boolean writesFrom(Function f, Address slot) {
		for (Reference r : getReferencesTo(slot)) {
			if (r.getReferenceType().isWrite() && f.getBody().contains(r.getFromAddress())) {
				return true;
			}
		}
		return false;
	}

	private void readSeeds(File f) throws Exception {
		for (String line : Files.readAllLines(f.toPath(), StandardCharsets.UTF_8)) {
			String[] t = line.split("\t");
			if (line.startsWith("#") || t.length < 2 || t[1].equals("NONE")) {
				continue;
			}
			seedNames.putIfAbsent(toAddr(Long.parseUnsignedLong(t[1], 16)), t[0]);
		}
	}

	private void readWindows(File f) throws Exception {
		for (String line : Files.readAllLines(f.toPath(), StandardCharsets.UTF_8)) {
			String[] t = line.split("\t");
			if (line.startsWith("#") || t.length < 3) {
				continue;
			}
			windowLabels.add(t[0]);
			windows.add(new long[] { Long.parseUnsignedLong(t[1], 16), Long.parseUnsignedLong(t[2], 16) });
		}
	}

	private String windowOf(Address a) {
		long v = a.getOffset();
		for (int i = 0; i < windows.size(); i++) {
			if (v >= windows.get(i)[0] && v < windows.get(i)[1]) {
				return windowLabels.get(i);
			}
		}
		return null;
	}

	private String name(Function f) {
		String s = seedNames.get(f.getEntryPoint());
		return s != null ? s : f.getName();
	}

	private static String hex(Function f) {
		return f.getEntryPoint().toString();
	}

	private static String nz(String s) {
		return s == null ? "" : s;
	}

	private static String clean(String s) {
		return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
	}

	private static PrintWriter writer(File dir, String name) throws Exception {
		return new PrintWriter(new File(dir, name), StandardCharsets.UTF_8);
	}
}
