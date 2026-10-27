"""Inspect or heuristically locate classic 32-bit Delphi VMT metadata.

The negative VMT offsets used here are a hypothesis to validate against the
specific compiler version. Every scan result must be corroborated in Ghidra or
another disassembler before it is used for a reconstruction.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pe32 import PE32, PEFormatError

VMT_CLASS_NAME_OFFSET = -44
VMT_INSTANCE_SIZE_OFFSET = -40
MAX_CLASS_NAME_LENGTH = 120
MAX_INSTANCE_SIZE = 64 * 1024 * 1024


class VMTError(ValueError):
    """A candidate does not contain plausible classic Delphi VMT metadata."""


def _class_name(pe: PE32, pointer: int) -> tuple[str, int]:
    length = pe.read_va(pointer, 1)[0]
    if not 1 <= length <= MAX_CLASS_NAME_LENGTH:
        raise VMTError("implausible ShortString length")
    raw = pe.read_va(pointer + 1, length)
    if any(byte < 0x20 or byte > 0x7E for byte in raw):
        raise VMTError("class name is not printable ASCII")
    name = raw.decode("ascii")
    if not (name[0].isalpha() or name[0] in "_@"):
        raise VMTError("class name has an implausible first character")
    return name, pointer


def inspect_vmt(pe: PE32, vmt_va: int) -> dict:
    """Read one candidate at its virtual address, without auto-validating it."""
    name_pointer = pe.u32_va(vmt_va + VMT_CLASS_NAME_OFFSET)
    instance_size = pe.u32_va(vmt_va + VMT_INSTANCE_SIZE_OFFSET)
    if not 0 < instance_size <= MAX_INSTANCE_SIZE:
        raise VMTError(f"implausible instance size: {instance_size}")
    name, name_address = _class_name(pe, name_pointer)
    first_method = pe.u32_va(vmt_va)

    executable_target = False
    if first_method >= pe.image_base:
        section = pe.section_for_rva(first_method - pe.image_base)
        executable_target = bool(section and section.executable)

    return {
        "vmt_address": f"0x{vmt_va:08x}",
        "class_name_address": f"0x{name_address:08x}",
        "class_name": name,
        "instance_size": instance_size,
        "first_method": f"0x{first_method:08x}",
        "executable_method_target": executable_target,
        "verified": False,
    }


def scan_vmts(pe: PE32, include_unverified: bool = False) -> list[dict]:
    """Return heuristic candidates backed by file bytes, ordered by address."""
    candidates = {}
    for section in pe.sections:
        for delta in range(0, max(0, section.raw_size - 3), 4):
            vmt_rva = section.virtual_address + delta
            vmt_va = pe.image_base + vmt_rva
            try:
                candidate = inspect_vmt(pe, vmt_va)
            except (PEFormatError, VMTError):
                continue
            if candidate["executable_method_target"] or include_unverified:
                candidates[vmt_va] = candidate
    return [candidates[address] for address in sorted(candidates)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="PE32 file to inspect without executing it")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--vmt", type=lambda value: int(value, 0), help="candidate VMT VA, e.g. 0x00412340")
    target.add_argument("--scan", action="store_true", help="scan sections for heuristic candidates")
    parser.add_argument(
        "--include-unverified",
        action="store_true",
        help="with --scan, also include candidates whose first method is not in an executable section",
    )
    args = parser.parse_args()

    try:
        pe = PE32.from_path(args.file)
        if args.scan:
            result = scan_vmts(pe, args.include_unverified)
        else:
            result = inspect_vmt(pe, args.vmt)
    except (OSError, PEFormatError, VMTError) as exc:
        raise SystemExit(f"error: {exc}") from exc

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
