# Delphi PE32: working with VMTs and RTTI

These notes describe typical 32-bit Delphi patterns. Compiler version, linker, packing, and language variants can change the layout. Confirm every layout assumption against the concrete binary.

## File offsets, RVAs, and VAs

Static PE tools need three distinct address kinds:

- **File offset** — position inside the file.
- **RVA** — relative virtual address inside the loaded image.
- **VA** — virtual address, typically `Image Base + RVA` for PE32.

A section defines how file bytes map to RVAs. Not every virtual range corresponds to file bytes; zero-filled areas cannot be read from the file.

The included parser hides that translation for you:

```python
from tools.pe32 import PE32

pe = PE32.from_path("program.exe")
rva = 0x1234

offset = pe.rva_to_offset(rva)
value = pe.u32_va(pe.image_base + rva)
```

Keep RVAs and image base in the analysis record. Use VAs mostly as convenient local labels rather than as persistent identifiers.

## Common classic VMT layout

Many 32-bit Delphi versions place metadata before the positive method table. Frequently observed fields are:

| Offset relative to VMT start | Typical meaning |
|---|---|
| `-44` | pointer to the class name, stored as a `ShortString` |
| `-40` | instance size as a 32-bit value |
| `0` | start of the positive method / virtual-method area |

A `ShortString` typically begins with a length byte, followed by characters. It does not always end with a terminating NUL byte.

These offsets are **not** a universal specification. They are a testable hypothesis that must be supported by references, method pointers, and object usage.

## Check a known candidate

```powershell
python -m tools.delphi_vmt "C:\analysis\program.exe" --vmt 0x00412340
```

The tool checks, among other things:

- can the name pointer be mapped to file-backed bytes?
- is the `ShortString` length plausible?
- is the class name printable ASCII?
- is the instance size inside a defensive range?
- does the first method pointer point into an executable section?

Even a successful output contains `"verified": false`. That is intentional. Structural plausibility is not yet a disassembler validation.

## Heuristic search

```powershell
python -m tools.delphi_vmt "C:\analysis\program.exe" --scan
```

By default, only candidates whose first method pointer points into an executable section are returned. To include weaker candidates:

```powershell
python -m tools.delphi_vmt "C:\analysis\program.exe" --scan --include-unverified
```

The search favors speed and cheap validation, not completeness. It can produce false positives and can miss unusual layouts.

## Validate a candidate in the disassembler

1. Examine the negative metadata and the positive method area together.
2. Verify that several method pointers address actual function starts.
3. Look for repeated references to the same table.
4. Compare object allocation size and observed memory accesses with the reported instance size.
5. Only then name the class, hierarchy, or methods.

In many Delphi objects, the first field is a VMT pointer. That does not mean any arbitrary 32-bit value at the start of a structure is a VMT.

## Common misinterpretations

- **A printable string is not enough.** Random bytes can pass a simple heuristic.
- **Code-like bytes are not automatically functions.** Check entry points and references.
- **A field offset is not a field type.** Derive the type from usage.
- **Imports and strings are leads, not proofs.**
- **Packing changes the assumptions.** A lack of file-backed structures is not a disproof.
- **ASLR changes runtime addresses.** Document RVAs plus the target hash, not just a runtime VA.

## Useful next evidence

- independent references to the same VMT
- consistent method calls through the same table offsets
- allocation size and field accesses that match the reported instance size
- multiple classes with a coherent layout
- RTTI references that have themselves been validated

Only this combination turns a candidate into a defensible reconstruction.

## Where to go next

- [`docs/workflow.md`](workflow.md) for the overall procedure
- [`tools/delphi_vmt.py`](../tools/delphi_vmt.py) for a concrete parser
- [`docs/evidence.md`](evidence.md) for recording the conclusion cleanly
