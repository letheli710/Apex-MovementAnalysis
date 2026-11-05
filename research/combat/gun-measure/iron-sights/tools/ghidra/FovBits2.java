// Which weapon field sits at var offset 0xb4c (weapon + 0x251c), and who writes the player-setfile offset 141abeee8. Read-only.
//@category HSD
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;

public class FovBits2 extends GhidraScript {
	@Override
	public void run() throws Exception {
		try (PrintWriter w = new PrintWriter(new File(getScriptArgs()[0]), StandardCharsets.UTF_8)) {
			Function f = getFunctionAt(toAddr(0x1400eaef0L));
			String lastName = "";
			for (Instruction ins : currentProgram.getListing().getInstructions(f.getBody(), true)) {
				String s = ins.toString();
				if (s.startsWith("LEA RAX,[0x14")) {
					Address a = toAddr(Long.parseUnsignedLong(s.substring(s.indexOf("0x") + 2, s.indexOf("]")), 16));
					Object d = null;
					try {
						byte[] b = new byte[64];
						currentProgram.getMemory().getBytes(a, b);
						int n = 0;
						while (n < 64 && b[n] >= 32 && b[n] < 127) n++;
						if (n > 2) lastName = new String(b, 0, n, StandardCharsets.US_ASCII);
					} catch (Exception e) {
					}
				}
				if (s.startsWith("MOV EAX,0xb4") || s.startsWith("MOV EAX,0xb5")) {
					w.println(ins.getAddress() + " " + s + " name=" + lastName);
				}
			}
			for (long t : new long[] {0x141abeee8L, 0x141abd858L}) {
				for (Reference r : getReferencesTo(toAddr(t))) {
					if (r.getReferenceType().isWrite()) {
						Instruction ins = getInstructionAt(r.getFromAddress());
						w.println("write " + Long.toHexString(t) + " at " + r.getFromAddress());
						Instruction p = ins;
						for (int k = 0; k < 8 && p != null; k++) p = p.getPrevious();
						for (int k = 0; k < 10 && p != null; k++) {
							StringBuilder sb = new StringBuilder();
							for (Reference rr : p.getReferencesFrom()) {
								byte[] b = new byte[40];
								try {
									currentProgram.getMemory().getBytes(rr.getToAddress(), b);
									int n = 0;
									while (n < 40 && b[n] >= 32 && b[n] < 127) n++;
									if (n > 3) sb.append(" '").append(new String(b, 0, n, StandardCharsets.US_ASCII)).append("'");
								} catch (Exception e) {
								}
							}
							w.println("    " + p.getAddress() + " " + p + sb);
							p = p.getNext();
						}
					}
				}
			}
		}
	}
}
