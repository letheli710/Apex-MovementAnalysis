// Prints the Ghidra function containing each SDK pattern hit. Args: <hits file> <out file>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.*;
import java.nio.file.*;
public class CheckBounds extends GhidraScript {
  @Override public void run() throws Exception {
    String[] a = getScriptArgs();
    try (PrintWriter w = new PrintWriter(new FileWriter(a[1]))) {
      w.println("name\thit\tpdata_start\tghidra_entry\tghidra_size\thit_is_entry\tpdata_matches_entry");
      for (String line : Files.readAllLines(Paths.get(a[0]))) {
        String[] t = line.trim().split(" ");
        if (t.length < 3) continue;
        Address hit = toAddr(Long.parseUnsignedLong(t[1], 16));
        Address pd = toAddr(Long.parseUnsignedLong(t[2], 16));
        Function f = getFunctionContaining(hit);
        if (f == null) { w.println(t[0] + "\t" + t[1] + "\t" + t[2] + "\tNONE\t\t\t"); continue; }
        w.println(t[0] + "\t" + t[1] + "\t" + t[2] + "\t" + f.getEntryPoint() + "\t" + f.getBody().getNumAddresses()
          + "\t" + f.getEntryPoint().equals(hit) + "\t" + f.getEntryPoint().equals(pd));
      }
    }
  }
}
