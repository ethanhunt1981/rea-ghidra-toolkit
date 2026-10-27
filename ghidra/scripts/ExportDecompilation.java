// Export all non-external functions to one UTF-8 text file for offline review.
// Usage: ExportDecompilation.java <output-file> [timeout-seconds]

import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;

public class ExportDecompilation extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args.length > 2) {
            throw new IllegalArgumentException(
                "Usage: ExportDecompilation.java <output-file> [timeout-seconds]"
            );
        }

        int timeoutSeconds = args.length == 2 ? Integer.parseInt(args[1]) : 60;
        if (timeoutSeconds < 1) {
            throw new IllegalArgumentException("timeout-seconds must be positive");
        }

        Path output = Path.of(args[0]).toAbsolutePath();
        Files.createDirectories(output.getParent());
        DecompInterface decompiler = new DecompInterface();
        int exported = 0;
        int failed = 0;

        try {
            if (!decompiler.openProgram(currentProgram)) {
                throw new IllegalStateException("Could not initialize the decompiler");
            }

            try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
                writer.write("/* Program: " + oneLine(currentProgram.getName()) + " */\n");
                writer.write("/* Image base: " + currentProgram.getImageBase() + " */\n");

                for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
                    if (monitor.isCancelled()) {
                        break;
                    }
                    if (function.isExternal()) {
                        continue;
                    }

                    writer.write("\n/* Function: " + oneLine(function.getName()) + " */\n");
                    writer.write("/* Entry: " + function.getEntryPoint() + " */\n");
                    writer.write("/* Signature: " + oneLine(function.getSignature().getPrototypeString()) + " */\n");

                    DecompileResults results = decompiler.decompileFunction(function, timeoutSeconds, monitor);
                    if (results.decompileCompleted() && results.getDecompiledFunction() != null) {
                        writer.write(results.getDecompiledFunction().getC());
                        writer.write("\n");
                        exported++;
                    }
                    else {
                        writer.write("/* Decompilation failed: " + oneLine(results.getErrorMessage()) + " */\n");
                        failed++;
                    }
                }
            }
        }
        finally {
            decompiler.dispose();
        }

        println("Exported " + exported + " functions to " + output + "; failures: " + failed);
    }

    private static String oneLine(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("*/", "* /").replace('\r', ' ').replace('\n', ' ');
    }
}
