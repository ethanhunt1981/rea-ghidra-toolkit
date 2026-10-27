"""Build a tiny synthetic PE32 image entirely in memory."""

import struct

IMAGE_BASE = 0x00400000
SECTION_RVA = 0x1000
RAW_OFFSET = 0x200
RAW_SIZE = 0x400


def make_pe32() -> bytearray:
    data = bytearray(RAW_OFFSET + RAW_SIZE)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"

    coff = 0x84
    struct.pack_into("<H", data, coff, 0x14C)
    struct.pack_into("<H", data, coff + 2, 1)
    struct.pack_into("<H", data, coff + 16, 0xE0)

    optional = coff + 20
    struct.pack_into("<H", data, optional, 0x10B)
    struct.pack_into("<I", data, optional + 16, 0)  # entry point RVA
    struct.pack_into("<I", data, optional + 28, IMAGE_BASE)
    struct.pack_into("<I", data, optional + 32, 0x1000)
    struct.pack_into("<I", data, optional + 36, 0x200)
    struct.pack_into("<I", data, optional + 56, 0x2000)
    struct.pack_into("<I", data, optional + 60, RAW_OFFSET)
    struct.pack_into("<H", data, optional + 68, 3)
    struct.pack_into("<I", data, optional + 92, 16)

    section = optional + 0xE0
    data[section : section + 8] = b".synth\0\0"
    struct.pack_into("<IIII", data, section + 8, RAW_SIZE, SECTION_RVA, RAW_SIZE, RAW_OFFSET)
    # Synthetic code/data section: executable, readable, writable.
    struct.pack_into("<I", data, section + 36, 0xE0000060)
    return data


def rva_to_offset(rva: int) -> int:
    return RAW_OFFSET + rva - SECTION_RVA


def add_vmt(
    data: bytearray,
    *,
    vmt_rva: int = 0x1100,
    name_rva: int = 0x1200,
    method_rva: int = 0x1300,
    name: bytes = b"TExample",
    instance_size: int = 24,
) -> None:
    vmt_offset = rva_to_offset(vmt_rva)
    struct.pack_into("<I", data, vmt_offset - 44, IMAGE_BASE + name_rva)
    struct.pack_into("<I", data, vmt_offset - 40, instance_size)
    struct.pack_into("<I", data, vmt_offset, IMAGE_BASE + method_rva)
    name_offset = rva_to_offset(name_rva)
    struct.pack_into("<B", data, name_offset, len(name))
    data[name_offset + 1 : name_offset + 1 + len(name)] = name
