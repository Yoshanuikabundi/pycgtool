import unittest

from pycgtool.parsers.json import Parser, jsonify


class TestParsersJson(unittest.TestCase):
    def test_json_read(self):
        parser = Parser("test/data/sugar.json")

        self.assertTrue("molecules" in parser)
        self.assertTrue("ALLA" in parser.molecules)

        self.assertTrue("beads" in parser.molecules["ALLA"])
        self.assertEqual("C1", parser.molecules["ALLA"].beads[0].name)

        self.assertTrue("bonds" in parser.molecules["ALLA"])
        self.assertEqual(["C1", "C2"], parser.molecules["ALLA"].bonds[0])

    def test_json_section(self):
        molecules = Parser("test/data/sugar.json", section="molecules")

        self.assertTrue("ALLA" in molecules)

        self.assertTrue("beads" in molecules["ALLA"])
        self.assertEqual("C1", molecules["ALLA"].beads[0].name)

        self.assertTrue("bonds" in molecules["ALLA"])
        self.assertEqual(["C1", "C2"], molecules["ALLA"].bonds[0])

    def test_include_file(self):
        martini = Parser("test/data/martini.json")
        self.assertTrue("molecules" in martini)
        self.assertTrue("DOPC" in martini.molecules)
        self.assertTrue("GLY" in martini.molecules)

    def test_json_water(self):
        parser = Parser("test/data/water.json", "molecules")

        self.assertTrue("SOL" in parser)
        self.assertEqual(1, len(parser["SOL"].beads))
        bead = parser["SOL"].beads[0]
        self.assertEqual("W", bead.name)
        self.assertEqual("P4", bead.type)
        self.assertEqual(["OW", "HW1", "HW2"], bead.atoms)
        self.assertEqual(0, len(cfg["SOL"].bonds))

    def test_json_sugar(self):
        parser = Parser("test/data/sugar.json", "molecules")

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

        self.assertTrue("ALLA" in parser)

        self.assertEqual(6, len(parser["ALLA"].beads))
        for ref_bead, bead in zip(ref_beads, parser["ALLA"].beads):
            self.assertEqual(ref_bead[0], bead.name)
            self.assertEqual(ref_bead[1], bead.type)
            self.assertEqual(ref_bead[2:], bead.atoms)

        self.assertEqual(6, len(parser["ALLA"].bonds))
        for ref_bond, bond in zip(ref_bonds, parser["ALLA"].bonds):
            self.assertEqual(ref_bond, bond)

    def test_missing_section(self):
        with self.assertRaises(KeyError):
            parser = Parser("test/data/water.json", "potato")

    def test_convert(self):
        jsonify("test/data/sugar.map", "test/data/sugar.bnd", "test.json")
        test_json = Parser("test.json", section="molecules")
        ref_json = Parser("test/data/sugar.json", section="molecules")
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
