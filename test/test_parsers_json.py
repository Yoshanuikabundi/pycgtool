import unittest

from pycgtool.parsers.json import CFG, DuplicateSectionError


class TestParsersJson(unittest.TestCase):
    def test_cfg_with(self):
        with CFG("test/data/water.json"):
            pass

    def test_cfg_get_section(self):
        with CFG("test/data/water.json") as cfg:
            self.assertTrue("SOL" in cfg)
            self.assertEqual(1, len(cfg["SOL"].beads))
            bead = cfg["SOL"].beads[0]
            self.assertEqual("W", bead.name)
            self.assertEqual("P4", bead.type)
            self.assertEqual(["OW", "HW1", "HW2"], bead.atoms)
            self.assertEqual(0, len(cfg["SOL"].bonds))

    def test_cfg_duplicate_error(self):
        with self.assertRaises(DuplicateSectionError):
            CFG("test/data/twice.json")

    @unittest.expectedFailure
    def test_include_file(self):
        with CFG("test/data/martini.json") as cfg:
            self.assertTrue("DOPC" in cfg)
            self.assertTrue("GLY" in cfg)


if __name__ == '__main__':
    unittest.main()
