"""Small, read-only PE32 parser used by the toolkit's command-line tools.

It deliberately implements only the structures needed for inventory, address
translation, strings, and imports. It does not load or execute the input file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct


class PEFormatError(ValueError):
    """The input is not a supported, structurally valid PE32 image."""


@dataclass(frozen=True)
class Section:
    name: str
    virtual_address: int
    virtual_size: int
    raw_offset: int
    raw_size: int
    characteristics: int

    @property
    def readable(self) -> bool:
        return bool(self.characteristics & 0x40000000)

    @property
    def writable(self) -> bool:
        return bool(self.characteristics & 0x80000000)

    @property
    def executable(self) -> bool:
        return bool(self.characteristics & 0x20000000)

    def contains_rva(self, rva: int) -> bool:
        mapped_size = max(self.virtual_size, self.raw_size)
        return self.virtual_address <= rva < self.virtual_address + mapped_size


class PE32:
    """Parsed PE32 image backed by an immutable byte string."""

    def __init__(self, data: bytes):
        self.data = bytes(data)
        if len(self.data) < 0x40 or self.data[:2] != b"MZ":
            raise PEFormatError("missing DOS MZ header")

        pe_offset = self._u32_at(0x3C)
        if pe_offset + 24 > len(self.data) or self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise PEFormatError("missing PE signature")

        coff = pe_offset + 4
        self.machine = self._u16_at(coff)
        section_count = self._u16_at(coff + 2)
        optional_size = self._u16_at(coff + 16)
        self.optional_offset = coff + 20
        optional_end = self.optional_offset + optional_size
        if optional_end > len(self.data):
            raise PEFormatError("truncated optional header")
        if self._u16_at(self.optional_offset) != 0x10B:
            raise PEFormatError("only PE32 (magic 0x10b) is supported")
        if optional_size < 96:
            raise PEFormatError("PE32 optional header is too small")

        self.entry_point = self._u32_at(self.optional_offset + 16)
        self.image_base = self._u32_at(self.optional_offset + 28)
        self.section_alignment = self._u32_at(self.optional_offset + 32)
        self.file_alignment = self._u32_at(self.optional_offset + 36)
        self.size_of_image = self._u32_at(self.optional_offset + 56)
        self.size_of_headers = self._u32_at(self.optional_offset + 60)
        self.subsystem = self._u16_at(self.optional_offset + 68)
        self.directory_count = self._u32_at(self.optional_offset + 92)
        directory_limit = (optional_size - 96) // 8
        if self.directory_count > directory_limit:
            raise PEFormatError("data directory count exceeds the optional header")

        section_table = optional_end
        if section_count > 96 or section_table + section_count * 40 > len(self.data):
            raise PEFormatError("invalid or truncated section table")

        sections = []
        for index in range(section_count):
            offset = section_table + index * 40
            raw_name = self.data[offset : offset + 8].split(b"\0", 1)[0]
            name = raw_name.decode("ascii", errors="replace")
            virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            characteristics = self._u32_at(offset + 36)
            if raw_offset + raw_size > len(self.data):
                raise PEFormatError(f"section {name!r} extends beyond the file")
            sections.append(
                Section(
                    name=name,
                    virtual_address=virtual_address,
                    virtual_size=virtual_size,
                    raw_offset=raw_offset,
                    raw_size=raw_size,
                    characteristics=characteristics,
                )
            )
        self.sections = tuple(sections)

    @classmethod
    def from_path(cls, path: str | Path) -> "PE32":
        return cls(Path(path).read_bytes())

    def _check_range(self, offset: int, size: int) -> None:
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise PEFormatError("read outside the input file")

    def _u16_at(self, offset: int) -> int:
        self._check_range(offset, 2)
        return struct.unpack_from("<H", self.data, offset)[0]

    def _u32_at(self, offset: int) -> int:
        self._check_range(offset, 4)
        return struct.unpack_from("<I", self.data, offset)[0]

    def rva_to_offset(self, rva: int, size: int = 1) -> int:
        """Translate a file-backed RVA to a file offset.

        RVAs in zero-filled virtual section tails are rejected because they do
        not have bytes in the input file.
        """
        if rva < 0 or size < 1:
            raise PEFormatError("invalid RVA or read size")
        if rva < self.size_of_headers and rva + size <= min(self.size_of_headers, len(self.data)):
            return rva
        for section in self.sections:
            if not section.contains_rva(rva):
                continue
            delta = rva - section.virtual_address
            if delta + size > section.raw_size:
                raise PEFormatError(f"RVA 0x{rva:x} is not backed by file bytes")
            return section.raw_offset + delta
        raise PEFormatError(f"RVA 0x{rva:x} is not mapped by this image")

    def read_rva(self, rva: int, size: int) -> bytes:
        offset = self.rva_to_offset(rva, size)
        return self.data[offset : offset + size]

    def read_va(self, va: int, size: int) -> bytes:
        if va < self.image_base:
            raise PEFormatError(f"VA 0x{va:x} lies below the image base")
        return self.read_rva(va - self.image_base, size)

    def u32_rva(self, rva: int) -> int:
        return struct.unpack("<I", self.read_rva(rva, 4))[0]

    def u32_va(self, va: int) -> int:
        return struct.unpack("<I", self.read_va(va, 4))[0]

    def c_string_rva(self, rva: int, max_length: int = 260) -> str:
        offset = self.rva_to_offset(rva)
        end = self.data.find(b"\0", offset, min(offset + max_length, len(self.data)))
        if end < 0:
            raise PEFormatError(f"unterminated string at RVA 0x{rva:x}")
        return self.data[offset:end].decode("ascii", errors="replace")

    def data_directory(self, index: int) -> tuple[int, int]:
        if index < 0 or index >= self.directory_count:
            return (0, 0)
        offset = self.optional_offset + 96 + index * 8
        self._check_range(offset, 8)
        return struct.unpack_from("<II", self.data, offset)

    def imports(self, max_libraries: int = 4096, max_functions: int = 65536) -> list[dict]:
        """Return imported DLLs and functions without resolving them."""
        directory_rva, _ = self.data_directory(1)
        if directory_rva == 0:
            return []

        libraries = []
        for index in range(max_libraries):
            descriptor = self.read_rva(directory_rva + index * 20, 20)
            original_first_thunk, _, _, name_rva, first_thunk = struct.unpack("<IIIII", descriptor)
            if not any(descriptor):
                return libraries
            if name_rva == 0:
                raise PEFormatError("import descriptor has no DLL name")

            functions = []
            thunk_rva = original_first_thunk or first_thunk
            if thunk_rva:
                for thunk_index in range(max_functions):
                    thunk = self.u32_rva(thunk_rva + thunk_index * 4)
                    if thunk == 0:
                        break
                    if thunk & 0x80000000:
                        functions.append({"ordinal": thunk & 0xFFFF})
                    else:
                        functions.append({"name": self.c_string_rva((thunk & 0x7FFFFFFF) + 2)})
                else:
                    raise PEFormatError("unterminated import thunk table")

            libraries.append({"dll": self.c_string_rva(name_rva), "functions": functions})
        raise PEFormatError("unterminated import descriptor table")

    def section_for_rva(self, rva: int) -> Section | None:
        return next((section for section in self.sections if section.contains_rva(rva)), None)
