# Combining REA and Ghidra

REA provides agent-side access, evidence handling, and focused tool calls. Ghidra supplies disassembly and decompilation for native PE targets. Always follow the schemas and tools that the connected REA version actually exposes.

## REA: focused native analysis

### 1. Open the correct target

Use `open_binary` on the exact target path supplied by the user. Do not choose a different file because its name looks similar, and do not open a duplicate session for a target you are already analyzing.

```text
open_binary(path = "<absolute private target path>")
binary_overview()
```

The overview answers:

- is it a known supported binary/container?
- which architecture are we looking at?
- what analysis methods are actually available?

Do not re-open a large target just because a new detail question appeared.

### 2. Work from an entry point

Depending on the available tools, combine strings, functions, references, and calls. Common useful operations are:

- `procedure_pseudo_code`
- `procedure_callers`
- `procedure_references`
- string or function search tools

Read the actual registered schema before a call. Do not invent parameter names or tool names. If a call fails, correct the cause first; repeating the same call is usually not useful.

### 3. Keep evidence

For each important claim, keep the:

- target hash
- address and address kind
- returned evidence ID or private export path
- tool version and command

If a large render or response is available in summary form, prefer that over repeating the full call. Export only what you need.

### 4. Close the session

```text
close_binary()
```

Save the evidence first. Do not modify a provider-managed Ghidra database in parallel with external scripts.

## Ghidra headless as a fallback or batch step

Prerequisites:

- `GHIDRA_INSTALL_DIR` points at the Ghidra root directory.
- the installed Java version satisfies `application.java.min`.
- the script directory contains [`ExportDecompilation.java`](../ghidra/scripts/ExportDecompilation.java).

Check the installation and Java version:

```powershell
Get-Content "$env:GHIDRA_INSTALL_DIR\Ghidra\application.properties" |
  Select-String 'application.version|application.java.min'
java -version
```

Do not trust the folder name of a Ghidra installation. The `application.properties` is decisive.

### First import and export

```powershell
& "$env:GHIDRA_INSTALL_DIR\support\analyzeHeadless.bat" `
  "C:\re-work\ghidra" "AnalysisProject" `
  -import "C:\re-work\input\program.exe" `
  -scriptPath "C:\re-work\toolkit\ghidra\scripts" `
  -postScript ExportDecompilation.java "C:\re-work\out\decompilation.txt" 60
```

The optional `60` is the decompiler timeout in seconds per function.

### Re-open an already analyzed project

```powershell
& "$env:GHIDRA_INSTALL_DIR\support\analyzeHeadless.bat" `
  "C:\re-work\ghidra" "AnalysisProject" `
  -process "program.exe" -noanalysis `
  -scriptPath "C:\re-work\toolkit\ghidra\scripts" `
  -postScript ExportDecompilation.java "C:\re-work\out\decompilation.txt" 60
```

`-noanalysis` is useful here because the project has already been analyzed. For a newly imported target do not assume the same mode.

### Use the output responsibly

The script writes one UTF-8 text file containing, per non-external function:

- function name
- entry address
- current signature
- decompiled C, or a clear error message

Output can be large and contains target-specific pseudocode. Keep it in the private project; do not copy it into GitMCP queries or into this toolkit.

## Practical choice

Use REA for a single sharp question and direct evidence interpretation. Use Ghidra headless for repeatable batch exports or when REA is unavailable. In most investigations you will need both at different times.
