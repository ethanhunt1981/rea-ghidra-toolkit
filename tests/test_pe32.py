import tempfile
import unittest
from pathlib import Path

from tools.pe32 import PE32, PEFormatError
from tools.pe_inventory import inventory
from tests.pe_fixture import IMAGE_BASE, RAW_OFFSET, make_pe32, rva_to_offset


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


if __name__ == "__main__":
    unittest.main()
