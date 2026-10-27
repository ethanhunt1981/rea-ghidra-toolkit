"""Print a deterministic PE32 inventory as text or JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .pe32 import PE32, PEFormatError


def inventory(path: Path, include_imports: bool = False) -> dict:
    data = path.read_bytes()
    pe = PE32(data)
    result = {
        "file": path.name,
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "format": "PE32",
        "machine": f"0x{pe.machine:04x}",
        "image_base": f"0x{pe.image_base:08x}",
        "entry_point_rva": f"0x{pe.entry_point:08x}",
        "subsystem": pe.subsystem,
        "sections": [
            {
                "name": section.name,
                "rva": f"0x{section.virtual_address:08x}",
                "virtual_size": section.virtual_size,
                "raw_offset": f"0x{section.raw_offset:08x}",
                "raw_size": section.raw_size,
                "readable": section.readable,
                "writable": section.writable,
                "executable": section.executable,
            }
            for section in pe.sections
        ],
    }
    if include_imports:
        result["imports"] = pe.imports()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="PE32 file to inspect without executing it")
    parser.add_argument("--imports", action="store_true", help="include imported DLLs and functions")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args()

    try:
        result = inventory(args.file, args.imports)
    except (OSError, PEFormatError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"File:       {result['file']}")
    print(f"Size:       {result['size']} bytes")
    print(f"SHA-256:    {result['sha256']}")
    print(f"Machine:    {result['machine']}")
    print(f"Image base: {result['image_base']}")
    print(f"Entry RVA:  {result['entry_point_rva']}")
    print("Sections:")
    for section in result["sections"]:
        flags = "".join(
            (
                "r" if section["readable"] else "-",
                "w" if section["writable"] else "-",
                "x" if section["executable"] else "-",
            )
        )
        print(
            f"  {section['name']:<8} RVA {section['rva']} "
            f"raw {section['raw_offset']}+{section['raw_size']:<8} {flags}"
        )
    if args.imports:
        print("Imports:")
        for library in result["imports"]:
            names = [str(item.get("name", f"ordinal:{item.get('ordinal')}")) for item in library["functions"]]
            print(f"  {library['dll']}: {', '.join(names)}")


if __name__ == "__main__":
    main()
