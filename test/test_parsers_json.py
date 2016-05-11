import unittest

from pycgtool.parsers.json import CFG


class TestParsersJson(unittest.TestCase):
    def test_json_water(self):
        cfg = CFG("test/data/water.json", "molecules")

        self.assertTrue("SOL" in cfg)
        self.assertEqual(1, len(cfg["SOL"].beads))
        bead = cfg["SOL"].beads[0]
        self.assertEqual("W", bead.name)
        self.assertEqual("P4", bead.type)
        self.assertEqual(["OW", "HW1", "HW2"], bead.atoms)
        self.assertEqual(0, len(cfg["SOL"].bonds))

    def test_json_sugar(self):
        cfg = CFG("test/data/sugar.json", "molecules")

        ref_beads = [["C1", "P3", "C1", "O1"],
                     ["C2", "P3", "C2", "O2"],
                     ["C3", "P3", "C3", "O3"],
                     ["C4", "P3", "C4", "O4"],
                     ["C5", "P2", "C5", "C6", "O6"],
                     ["O5", "P4", "O5"]]

        ref_bonds = [["C1", "C2"],
                     ["C2", "C3"],
                     ["C3", "C4"],
                     ["C4", "C5"],
                     ["C5", "O5"],
                     ["O5", "C1"]]

        self.assertTrue("ALLA" in cfg)

        self.assertEqual(6, len(cfg["ALLA"].beads))
        for ref_bead, bead in zip(ref_beads, cfg["ALLA"].beads):
            self.assertEqual(ref_bead[0], bead.name)
            self.assertEqual(ref_bead[1], bead.type)
            self.assertEqual(ref_bead[2:], bead.atoms)

        self.assertEqual(6, len(cfg["ALLA"].bonds))
        for ref_bond, bond in zip(ref_bonds, cfg["ALLA"].bonds):
            self.assertEqual(ref_bond, bond)

    def test_include_file(self):
        cfg = CFG("test/data/martini.json", "molecules")
        self.assertTrue("DOPC" in cfg)
        self.assertTrue("GLY" in cfg)


if __name__ == '__main__':
    unittest.main()
