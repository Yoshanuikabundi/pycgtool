import unittest
import filecmp
import os
import logging

import numpy as np

from pycgtool.frame import Atom, Residue, Frame
from pycgtool.framereader import FrameReaderMDTraj
from pycgtool.framereader import FrameReader, get_frame_reader
from pycgtool.framereader import UnsupportedFormatException, NonMatchingSystemError
from pycgtool.util import cmp_file_whitespace_float


class AtomTest(unittest.TestCase):
    def test_atom_create(self):
        atom = Atom(name="Name", num=0, type="Type")
        self.assertEqual("Name", atom.name)
        self.assertEqual(0, atom.num)
        self.assertEqual("Type", atom.type)

    def test_atom_add_missing_data(self):
        atom1 = Atom("Name1", 0, type="Type")
        atom2 = Atom("Name2", 0, mass=1)

        with self.assertRaises(AssertionError):
            atom1.add_missing_data(atom2)

        atom2 = Atom("Name1", 0, mass=1)
        atom1.add_missing_data(atom2)
        self.assertEqual(1, atom1.mass)


class ResidueTest(unittest.TestCase):
    def test_residue_create(self):
        residue = Residue(name="Resname")
        self.assertEqual("Resname", residue.name)

    def test_residue_add_atoms(self):
        atom = Atom(name="Name", num=0, type="Type")
        residue = Residue()
        residue.add_atom(atom)
        self.assertEqual(atom, residue.atoms[0])
        self.assertTrue(atom is residue.atoms[0])


class FrameTest(unittest.TestCase):
    def helper_read_xtc(self, frame, first_only=False, skip_names=False):
        self.assertEqual(663, frame.natoms)
        self.assertEqual(221, len(frame.residues))
        self.assertEqual(3, len(frame.residues[0].atoms))
        if not skip_names:  # MDTraj renames water
            self.assertEqual("SOL", frame.residues[0].name)
            self.assertEqual("OW", frame.residues[0].atoms[0].name)

        atom0_coords = np.array([
            [0.696, 1.330, 1.211],
            [1.176, 1.152, 1.586],
            [1.122, 1.130, 1.534]
        ])

        box_vectors = np.array([
            [1.89868,    1.89868,    1.89868],
            [1.9052,     1.9052,     1.9052],
            [1.90325272, 1.90325272, 1.90325272]
        ])

        for i in range(1 if first_only else len(atom0_coords)):
            np.testing.assert_allclose(atom0_coords[i], frame.residues[0].atoms[0].coords)
            np.testing.assert_allclose(box_vectors[i], frame.box, rtol=1e-4)  # PDB files are f9.3
            frame.next_frame()

    def test_frame_create(self):
        Frame()

    def test_frame_add_residue(self):
        residue = Residue()
        frame = Frame()
        frame.add_residue(residue)
        self.assertEqual(residue, frame.residues[0])
        self.assertTrue(residue is frame.residues[0])


    def test_frame_mdtraj_read_gro(self):
        logging.disable(logging.WARNING)
        frame = Frame("test/data/water.gro", xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)

        self.helper_read_xtc(frame, first_only=True, skip_names=True)


    def test_frame_mdtraj_read_pdb(self):
        reader = FrameReaderMDTraj("test/data/water.pdb")
        frame = Frame.instance_from_reader(reader)

        self.helper_read_xtc(frame, first_only=True, skip_names=True)

    def test_frame_any_read_pdb(self):
        reader = get_frame_reader("test/data/water.pdb")
        frame = Frame.instance_from_reader(reader)

        self.helper_read_xtc(frame, first_only=True, skip_names=True)

    def test_frame_any_read_unsupported(self):
        with self.assertRaises(UnsupportedFormatException):
            reader = get_frame_reader("test/data/dppc.map")

    def test_frame_output_gro(self):
        frame = Frame("test/data/water.gro")
        frame.output("water-out.gro", format="gro")
        self.assertTrue(cmp_file_whitespace_float("test/data/water.gro", "water-out.gro", verbose=True))
        os.remove("water-out.gro")

    def test_frame_read_xtc_mdtraj_numframes(self):
        logging.disable(logging.WARNING)
        frame = Frame(coords="test/data/water.gro", traj="test/data/water.xtc",
                      xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)
        self.assertEqual(11, frame.numframes)

    def test_frame_mdtraj_read_xtc(self):
        logging.disable(logging.WARNING)
        frame = Frame(coords="test/data/water.gro", traj="test/data/water.xtc",
                      xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)

        self.helper_read_xtc(frame, skip_names=True)



    def test_frame_write_xtc_mdtraj(self):
        try:
            os.remove("water_test2.xtc")
        except IOError:
            pass

        logging.disable(logging.WARNING)
        frame = Frame(coords="test/data/water.gro", traj="test/data/water.xtc",
                      xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)

        while frame.next_frame():
            frame.write_traj("water_test2", format="xtc")


    def test_frame_instance_from_reader_dummy(self):
        class DummyReader(FrameReader):
            def _initialise_frame(self, frame):
                frame.dummy_reader = True

            def _read_frame_number(self, number):
                return number * 10, [], None

        reader = DummyReader(None)
        frame = Frame.instance_from_reader(reader)
        self.assertTrue(frame.dummy_reader)

        frame.next_frame()
        self.assertEqual(frame.number, 0)
        self.assertEqual(frame.time, 0)
        np.testing.assert_array_equal(np.zeros(3), frame.box)  # Reader replaces None with (0, 0, 0)

        frame.next_frame()
        self.assertEqual(frame.number, 1)
        self.assertEqual(frame.time, 10)

    def test_raise_nonmatching_system_all(self):
        with self.assertRaises(NonMatchingSystemError):
            reader = get_frame_reader("test/data/water.gro", "test/data/sugar.xtc")


    def test_raise_nonmatching_system_mdtraj(self):
        with self.assertRaises(NonMatchingSystemError):
            reader = FrameReaderMDTraj("test/data/water.gro", "test/data/sugar.xtc")

    def test_to_mdtraj(self):
        logging.disable(logging.WARNING)
        frame = Frame("test/data/water.gro", xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)

        topology = frame.to_mdtraj()
        self.assertEqual(663, topology.n_atoms)
        self.assertEqual(221, topology.n_residues)
        self.assertEqual(topology.residue(0).name, "SOL")

    def test_conv_dcd(self):
        logging.disable(logging.WARNING)
        frame = Frame("test/data/water.gro", "test/data/water.xtc", xtc_reader="mdtraj")
        logging.disable(logging.NOTSET)
        while frame.next_frame():
            frame.write_traj("water", format="dcd")

        frame.write_traj("water", format="dcd")
        frame_dcd = Frame("test/data/water.gro", "water.dcd", xtc_reader="mdtraj")

        os.remove("water.dcd")






if __name__ == '__main__':
    unittest.main()
