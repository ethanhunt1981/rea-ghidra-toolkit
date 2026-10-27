# Troubleshooting: REA, Ghidra, and PE analysis

Prefer diagnosis over repetition. If a call fails, correct the cause first. Usually this means fixing the parameter, target, tool schema, or version rather than trying the same command again.

## Ghidra installation and version

### Check the version correctly

Do not trust the directory name. Check the installed binary itself:

```powershell
Get-Content "$env:GHIDRA_INSTALL_DIR\Ghidra\application.properties" |
  Select-String 'application.version|application.java.min'
```

- If the file does not exist, `GHIDRA_INSTALL_DIR` usually points to the wrong directory.
- If the Java version does not satisfy `application.java.min`, provide the required Java version first.
- A Ghidra update can change the minimum Java version. Read the properties for the exact installation you are using.

### Wrong installation directory

`GHIDRA_INSTALL_DIR` must point to the Ghidra root, the directory that contains `Ghidra` and `support`. Then restart the provider session or re-run the connection check.

### Do not assume a universal version matrix

Which Ghidra version a REA installation accepts depends on the installed REA distribution. Check the policy or documentation of the version actually used. If you document version-specific facts in this repository, record the date and source as well.

## REA issues

### Provider session ends unexpectedly

Do:

1. Read the reported root cause first.
2. Stop only the relevant old analysis process, not all Java processes.
3. Re-open the same target with `open_binary`.
4. Export important evidence before making larger changes; session-local annotations can disappear.
5. Close cleanly with `close_binary` when you are done.

### Unknown or wrong tool name

- Read the actual registered tools and schemas first.
- Use exactly the supplied names and parameters.
- Some harnesses include a `tools.` prefix, others do not. Do not memorize one pattern and generalize it.

### Timeout or oversized response

Do not simply repeat a large call:

- use available summary or detail parameters
- use a returned evidence ID for a smaller view
- narrow the question to one function, module, or region
- export once if a full result is needed

Confirm whether the failure happened locally in the client or on the server side. Only retry when it is clear the analysis did not actually complete.

## Ghidra headless

### Program not found

`-process` refers to a program inside the specified Ghidra project. For a new target use `-import`; afterwards the analyzed project can be reused with `-process`.

### Script not found

`-scriptPath` must contain `ExportDecompilation.java`. In `-postScript`, the script name is followed by its arguments. After the script name, provide the output path and optionally the timeout.

### Java errors

First check `application.java.min` and the actual `java -version`. After installing or replacing Java, re-check the environment and/or run the call with a clean environment.

## PE analysis problems

### Input is not accepted as PE32

- Verify file size and hash; downloads can be truncated.
- Confirm that the optional header uses the PE32 magic `0x10b`. 64-bit PE files are intentionally rejected by this parser.
- An `MZ` marker alone does not make the file a valid PE.

### Imports are missing or appear partial

- Bound imports, ordinal-only imports, forwarding entries, or packed sections can make the import table look different.
- This tool reads only the standard directory and thunk forms. It does not replace a complete import-table reader.
- If the target is an installer package, inspect its members first rather than only the outer package.

### VMT scan produces no result

Possible reasons:

- the compiler uses a different VMT / RTTI layout
- packing or encrypted sections prevent simple file-backed checks
- there really are no such candidates in the examined range

That output remains a scoped observation, not a disproof.
