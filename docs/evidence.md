# Evidence, logs, and handover

Reverse-engineering results are only reusable if the difference between what was observed and what was inferred stays visible.

## Keep claim levels separate

| Claim type | Meaning | Example |
|---|---|---|
| Observation | directly supported by file bytes, tool output, or a documented runtime action | “the pseudocode of function X shows a call to imported symbol Y” |
| Inference | supported by observations, but not uniquely proven | “the access width and arithmetic match a 32-bit counter” |
| Unknown | outside the current scope, or not yet decided | “the search covered sections A and B; section C has no result yet” |

Avoid broad phrasing such as “the app does X” when the statement comes only from static analysis. More precise is something like “the decompiled path processes X”.

## Private analysis log entries

Use the same structure for each finding:

| Field | Meaning |
|---|---|
| `ID` | stable identifier, for example `F001` |
| `Target` | file name, SHA-256, version |
| `Address` | entry address and, if useful, RVA / image base |
| `Question` | the original open question |
| `Observation` | directly verifiable tool or byte observation |
| `Conclusion` | inference, not proof |
| `Name / hypothesis` | possible function name, type, offset, or VMT role |
| `Status` | `confirmed`, `plausible`, or `unresolved` |
| `Evidence` | evidence ID or private export path |
| `Recheck` | what independent verification remains, or what was performed |
| `Search range` | which areas were intentionally not examined |

## Treat negative results as data

A “no hit” is useful only when the search range is visible:

- examined sections, files, or functions
- search patterns and case sensitivity
- checked references or entry points
- limits caused by packing, file type, or encrypted regions

Without that range, do not claim that something does not exist in general. Claim only that it was not observed within the documented scope.

## Keep identifiers meaningful

A verified function name is valuable because later references become readable immediately. If a hypothesis is disproved, update it with date and reason, so the old assumption does not silently continue.

## Hand over the session

At the end of a session, the private `handover.md` should contain something like:

```text
## Status
- F002 confirmed: VMT hypothesis, cross-references support it.
- F003 unresolved: field at offset 0x10 is still unknown.

## Next steps
- Continue tracking the object usage of class X.
- Check write accesses to the field at offset 0x10.
```

Ready-to-use templates are in [`templates/analysis-log.md`](../templates/analysis-log.md) and [`templates/handover.md`](../templates/handover.md).
