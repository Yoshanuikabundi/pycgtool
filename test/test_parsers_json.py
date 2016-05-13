import unittest

from pycgtool.parsers.json import CFG, jsonify


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

    def test_missing_section(self):
        with self.assertRaises(KeyError):
            cfg = CFG("test/data/water.json", "potato")

    def test_convert(self):
        jsonify("test/data/sugar.map", "test/data/sugar.bnd", "test.json")
        test_json = CFG("test.json", from_section="molecules")
        ref_json = CFG("test/data/sugar.json", from_section="molecules")
        for tbead, rbead in zip(test_json["ALLA"].beads, ref_json["ALLA"].beads):
            self.assertEqual(tbead, rbead)

        for tbond, rbond in zip(test_json["ALLA"].bonds, ref_json["ALLA"].bonds):
            self.assertEqual(tbond, rbond)

        for tbead, rbead in zip(test_json["SOL"].beads, ref_json["SOL"].beads):
            self.assertEqual(tbead, rbead)

        for tbond, rbond in zip(test_json["SOL"].bonds, ref_json["SOL"].bonds):
            self.assertEqual(tbond, rbond)


if __name__ == '__main__':
    unittest.main()
