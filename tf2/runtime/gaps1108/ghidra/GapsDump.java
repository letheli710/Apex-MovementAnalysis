// GAPS-1108 read-only lookups in the TF2 Ghidra project. Arguments after the output file:
//   f:ADDR       decompile the function containing ADDR
//   c:ADDR       decompile the function containing ADDR and every direct caller
//   x:ADDR       list the references to ADDR (from address, function)
//   flt:ADDR     the 4-byte float (and int) at ADDR
//   scalar:VAL   every instruction with the scalar VAL as an operand (function, instruction)
//   str:TEXT     decompile every function referencing a defined string equal to TEXT
//
//   analyzeHeadless <projdir> tf2 -process server.dll -noanalysis -readOnly
//     -scriptPath <dir> -postScript GapsDump.java <out.txt> <arg> [<arg> ...]
//@category HSD

import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashSet;
import java.util.Set;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

public class GapsDump extends GhidraScript {

	private DecompInterface dec;
	private PrintWriter out;
	private final Set<Function> done = new LinkedHashSet<>();

	private void decomp(Function f, String why) {
		if (f == null || done.contains(f))
			return;
		done.add(f);
		DecompileResults r = dec.decompileFunction(f, 120, monitor);
		out.println("// ===== " + f.getEntryPoint() + " " + f.getName() + " size " + f.getBody().getNumAddresses() + " (" + why + ")");
		if (r != null && r.getDecompiledFunction() != null)
			out.println(r.getDecompiledFunction().getC());
		else
			out.println("// decompile failed");
	}

	@Override
	public void run() throws Exception {
		String[] args = getScriptArgs();
		out = new PrintWriter(new File(args[0]), StandardCharsets.UTF_8);
		dec = new DecompInterface();
		dec.openProgram(currentProgram);
		out.println("// program " + currentProgram.getName() + " sha256 " + currentProgram.getExecutableSHA256());
		for (int i = 1; i < args.length; i++) {
			String a = args[i];
			int k = a.indexOf(':');
			String kind = a.substring(0, k), val = a.substring(k + 1);
			out.println("// ##### " + a);
			if (kind.equals("f") || kind.equals("c")) {
				Function f = getFunctionContaining(toAddr(val));
				decomp(f, a);
				if (kind.equals("c") && f != null)
					for (Reference r : getReferencesTo(f.getEntryPoint())) {
						Function g = getFunctionContaining(r.getFromAddress());
						out.println("// caller " + r.getFromAddress() + " in " + (g == null ? "?" : g.getEntryPoint()));
						decomp(g, "caller of " + f.getEntryPoint() + " @" + r.getFromAddress());
					}
			} else if (kind.equals("x")) {
				for (Reference r : getReferencesTo(toAddr(val))) {
					Function g = getFunctionContaining(r.getFromAddress());
					out.println("// ref " + r.getFromAddress() + " " + r.getReferenceType() + " in " + (g == null ? "?" : g.getEntryPoint() + " " + g.getName()));
				}
			} else if (kind.equals("flt")) {
				Address ad = toAddr(val);
				int bits = getInt(ad);
				out.println("// " + val + " float " + Float.intBitsToFloat(bits) + " int " + bits);
			} else if (kind.equals("scalar")) {
				long want = Long.decode(val);
				InstructionIterator it = currentProgram.getListing().getInstructions(true);
				while (it.hasNext() && !monitor.isCancelled()) {
					Instruction ins = it.next();
					for (int op = 0; op < ins.getNumOperands(); op++)
						for (Object o : ins.getOpObjects(op))
							if (o instanceof Scalar && ((Scalar) o).getUnsignedValue() == want) {
								Function g = getFunctionContaining(ins.getAddress());
								out.println("// scalar " + ins.getAddress() + " " + (g == null ? "?" : g.getEntryPoint()) + " op" + op + " " + ins);
							}
				}
			} else if (kind.equals("str")) {
				DataIterator it = currentProgram.getListing().getDefinedData(true);
				while (it.hasNext() && !monitor.isCancelled()) {
					Data d = it.next();
					Object v = d.getValue();
					if (v instanceof String && v.equals(val))
						for (Reference r : getReferencesTo(d.getAddress())) {
							Function g = getFunctionContaining(r.getFromAddress());
							out.println("// string ref " + r.getFromAddress() + " in " + (g == null ? "?" : g.getEntryPoint()));
							decomp(g, "refs \"" + val + "\" @" + r.getFromAddress());
						}
				}
			}
			out.flush();
		}
		out.close();
		dec.dispose();
	}
}
