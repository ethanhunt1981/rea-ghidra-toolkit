import struct
import tempfile
import unittest
from pathlib import Path

from tools.pe32 import PE32, PEFormatError
from tools.pe_inventory import inventory
from tests.pe_fixture import IMAGE_BASE, RAW_OFFSET, make_pe32, rva_to_offset


def add_import_table(data: bytearray, *, directory_size: int = 40) -> None:
    optional = 0x98
    directory_rva = 0x1100
    struct.pack_into("<II", data, optional + 96 + 8, directory_rva, directory_size)

    descriptor = rva_to_offset(directory_rva)
    struct.pack_into("<IIIII", data, descriptor, 0x1240, 0, 0, 0x1200, 0x1270)
    data[rva_to_offset(0x1200) : rva_to_offset(0x1200) + 13] = b"KERNEL32.dll\0"

    thunk_table = rva_to_offset(0x1240)
    struct.pack_into("<III", data, thunk_table, 0x1260, 0x80000007, 0)
    name_entry = rva_to_offset(0x1260)
    struct.pack_into("<H", data, name_entry, 0)
    data[name_entry + 2 : name_entry + 14] = b"CreateFileA\0"


class PE32Tests(unittest.TestCase):
    def test_parses_synthetic_headers_and_maps_addresses(self):
        data = make_pe32()
        data[rva_to_offset(0x1010) : rva_to_offset(0x1010) + 4] = b"test"
        pe = PE32(data)

        self.assertEqual(pe.image_base, IMAGE_BASE)
        self.assertEqual(pe.machine, 0x14C)
        self.assertEqual(len(pe.sections), 1)
        self.assertEqual(pe.rva_to_offset(0x1000), RAW_OFFSET)
        self.assertEqual(pe.read_va(IMAGE_BASE + 0x1010, 4), b"test")
        self.assertEqual(pe.imports(), [])

    def test_rejects_non_pe_input(self):
        with self.assertRaises(PEFormatError):
            PE32(b"not a PE file")

    def test_inventory_hashes_without_executing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.exe"
            path.write_bytes(make_pe32())
            result = inventory(path)

        self.assertEqual(result["format"], "PE32")
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["sections"][0]["name"], ".synth")

    def test_parses_named_and_ordinal_imports(self):
        data = make_pe32()
        add_import_table(data)

        imports = PE32(data).imports()

        self.assertEqual(imports, [{
            "dll": "KERNEL32.dll",
            "functions": [{"name": "CreateFileA"}, {"ordinal": 7}],
        }])

    def test_string_must_terminate_within_file_backed_section(self):
        data = make_pe32()
        data[-1] = ord("A")
        data.extend(b"\0")
        pe = PE32(data)

        with self.assertRaises(PEFormatError):
            pe.c_string_rva(0x13FF)

    def test_import_descriptors_cannot_exceed_declared_directory(self):
        data = make_pe32()
        add_import_table(data, directory_size=20)
        pe = PE32(data)

        with self.assertRaises(PEFormatError):
            pe.imports()

    def test_import_function_limits_allow_exactly_terminated_table(self):
        data = make_pe32()
        add_import_table(data)
        pe = PE32(data)

        functions = pe.imports(max_functions=2, max_total_functions=2)[0]["functions"]
        self.assertEqual(len(functions), 2)

    def test_import_function_limit_applies_across_libraries(self):
        data = make_pe32()
        add_import_table(data)
        struct.pack_into("<I", data, rva_to_offset(0x1240) + 4, 0)

        second_descriptor = rva_to_offset(0x1114)
        struct.pack_into("<IIIII", data, second_descriptor, 0x1280, 0, 0, 0x1220, 0x1290)
        data[rva_to_offset(0x1220) : rva_to_offset(0x1220) + 11] = b"USER32.dll\0"
        struct.pack_into("<II", data, rva_to_offset(0x1280), 0x12A0, 0)
        struct.pack_into("<H", data, rva_to_offset(0x12A0), 0)
        data[rva_to_offset(0x12A2) : rva_to_offset(0x12A2) + 12] = b"MessageBoxA\0"
        struct.pack_into("<II", data, 0x98 + 96 + 8, 0x1100, 60)
        pe = PE32(data)

        with self.assertRaises(PEFormatError):
            pe.imports(max_total_functions=1)

    def test_import_limits_must_be_positive(self):
        with self.assertRaises(PEFormatError):
            PE32(make_pe32()).imports(max_total_functions=0)


if __name__ == "__main__":
    unittest.main()
