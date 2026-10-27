# Repository rules

## Scope

This repository contains only generic, reusable REA / Ghidra methodology, tools, and synthetic tests. It is not a dumping ground for a specific reverse-engineering target.

Never commit:

- original binaries, installers, libraries, or assets from an analyzed target
- decompiled code, strings, or larger extracts from a concrete target
- target-specific format specifications or reimplementations
- credentials, private URLs, usernames in local paths, or confidential project names
- code or text without confirmed rights and licensing

Use only generated data for tests. Keep examples neutral and avoid implying a specific real target.

## Changes

- Prefer small, read-only Python tools using only the standard library.
- Link new documentation from `README.md` and `llms.txt`; keep `llms.txt` short, because it is the main GitMCP entry point.
- Do not claim a universal REA / Ghidra / JDK version compatibility. Record version-specific guidance with a date and source, or describe a dynamic check instead.
- Clearly separate observations, heuristics, and verified claims.
- Do not commit generated Ghidra projects or decompilation output.

## Checks

From the repository root, run:

```sh
python -m unittest discover -v
python -m compileall -q tools tests
```

Compile or run Ghidra scripts with the installed Ghidra version when possible. If that is not possible in the current environment, state that limitation explicitly.
