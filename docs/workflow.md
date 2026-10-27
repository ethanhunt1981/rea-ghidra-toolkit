# Evidence-oriented analysis workflow

This workflow is for authorized static analysis. The concrete target and all target-derived data stay in the private analysis project.

## 1. Set the question and the scope

Start with testable questions, for example:

- Which function reads a specific file format?
- Which class is responsible for an observed behavior?
- Which data structure is used by a specific function?
- Is a hypothesis supported by static evidence, or only plausible?

Decide whether static analysis is the only permitted mode. Opening a file, extracting strings, or decompiling it does **not** mean executing it. Runtime work is a separate scope.

## 2. Keep the private working directory and artifact identity

A simple private structure is enough:

```text
analysis/
  notes/
  evidence/
  exports/
tools/
handover.md
```

Record at least:

- the full path and source of the artifact inside the private project
- file size and SHA-256
- file type, architecture, and any useful compiler/runtime information
- date, tool versions, and the exact scope

For PE32 files:

```powershell
python -m tools.pe_inventory "C:\analysis\program.exe" --imports --json
```

The output belongs in the private project, not in this toolkit.

## 3. Create the smallest useful overview

Do not decompile every function immediately. Start with:

1. PE / archive inventory and available metadata
2. sections, imports, resources, and entry points
3. existing REA session or Ghidra project instead of starting a duplicate
4. strings and references as leads, not as behavioral proof

If the target is an installer or archive, identify the relevant member first. An installer is not necessarily the program you want to decompile.

## 4. Move from question to function

For each question, look for a concrete entry point:

- an interesting import or API
- a string and the code that references it
- a resource or file access path
- a function address from a previous observation
- a VMT / RTTI candidate in Delphi

From there, focus on pseudocode, calls, callers, and references. Expand the analysis only when the open question justifies it.

## 5. Reconstruct functions and structures incrementally

For each examined function, record in the private log:

- SHA-256 of the target and the entry address
- original and later assigned function name
- signature and the confidence in that signature
- observed calls and meaningful references
- constants, offsets, and string/data references
- evidence ID or private export path
- open questions

Do not name a function solely because a string is nearby. A name like `load_data` remains a hypothesis until call context and data flow support it.

For data structures, record only confirmed fields first. Field size and type come from access width, signedness, pointer arithmetic, and independent accesses rather than from a single intuition.

## 6. Validate VMT and RTTI information

For classic 32-bit Delphi, [`tools/delphi_vmt.py`](../tools/delphi_vmt.py) can provide candidates. Treat every hit as unverified until the disassembler supports it. Check at least:

- is the address really the start of a method table?
- does the name pointer resolve to a plausible `ShortString`?
- does the instance size fit observed object usage?
- do method entries point to actual code?
- are there repeated, consistent references to the same table?

Details are in [`delphi-pe32.md`](delphi-pe32.md).

## 7. Prefer verification over plausibility

Keep three separate claim types:

- **Observation:** directly supported by the artifact or a tool result.
- **Inference:** supported by observations, but not uniquely proven.
- **Unknown:** outside the current scope or not yet decided.

Static analysis does not prove that execution actually happened. Conversely, one runtime run does not prove all paths. Phrase negative results with range: “no hit within the examined functions”, not “it does not exist”.

## 8. Test it reproducibly

Useful checks include:

- repeating a decompilation and comparing the result
- using an independent reference or a second call context
- re-running address and offset calculations with a local script
- testing parser hypotheses with synthetic fixtures
- exercising expected failure and boundary conditions

Do not verify a parser only with the same assumptions that produced it. Look for at least one independent confirmation in the real target.

## 9. Close the session cleanly

- mark analysis questions as answered, partly answered, or open
- export useful evidence and update the private `handover.md`
- close the REA binary session with `close_binary`
- do not modify a provider-managed Ghidra database externally
- only move general, cleaned, and legally safe knowledge into this public toolkit

Use [`templates/handover.md`](../templates/handover.md) for the next session.
