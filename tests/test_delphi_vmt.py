import struct
import unittest

from tools.delphi_vmt import VMTError, inspect_vmt, scan_vmts
from tools.pe32 import PE32
from tests.pe_fixture import IMAGE_BASE, add_vmt, make_pe32, rva_to_offset


class DelphiVMTTests(unittest.TestCase):
    def test_reads_vmt_metadata_from_synthetic_image(self):
        data = make_pe32()
        add_vmt(data)
        pe = PE32(data)

        result = inspect_vmt(pe, IMAGE_BASE + 0x1100)

        self.assertEqual(result["class_name"], "TExample")
        self.assertEqual(result["instance_size"], 24)
        self.assertTrue(result["executable_method_target"])
        self.assertFalse(result["verified"])

    def test_scan_finds_only_plausible_candidate(self):
        data = make_pe32()
        add_vmt(data)
        pe = PE32(data)

        results = scan_vmts(pe)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["vmt_address"], "0x00401100")

    def test_rejects_non_printable_class_name(self):
        data = make_pe32()
        add_vmt(data, name=b"Bad\x00Name")
        pe = PE32(data)

        with self.assertRaises(VMTError):
            inspect_vmt(pe, IMAGE_BASE + 0x1100)
        self.assertEqual(scan_vmts(pe), [])

    def test_rejects_implausible_instance_size(self):
        data = make_pe32()
        add_vmt(data)
        struct.pack_into("<I", data, rva_to_offset(0x1100) - 40, 0)
        pe = PE32(data)

        with self.assertRaises(VMTError):
            inspect_vmt(pe, IMAGE_BASE + 0x1100)


if __name__ == "__main__":
    unittest.main()
