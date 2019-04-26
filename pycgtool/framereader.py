"""
This module contains classes for reading trajectories into a Frame instance.

Multiple readers are defined, allowing different underlying trajectory libraries to be used.
This module is tightly coupled with the frame.py module, so shares a set of unit tests.
"""

import os
import abc
import itertools
import logging
import collections
import warnings
from mdtraj import formats as fmt
import types

import numpy as np

from .frame import Atom, Residue
from .util import FixedFormatUnpacker

logger = logging.getLogger(__name__)

def load_blank(self):
    '''
    This is a filthy hack that stops mdtraj changing the names
    of residues/atoms to pdb standard names
    :param self: reference to instance
    :return:
    '''
    self._residueNameReplacements = {}
    self._atomNameReplacements = {}
    return None


funcType = types.MethodType
fmt.pdb.PDBTrajectoryFile._loadNameReplacementTables = funcType(load_blank, fmt.pdb.PDBTrajectoryFile)

class UnsupportedFormatException(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Topology/Trajectory format not supported by this reader"
        super(UnsupportedFormatException, self).__init__(msg)


class NonMatchingSystemError(ValueError):
    def __init__(self, msg=None):
        if msg is None:
            msg = "Number of atoms does not match between topology and trajectory files"
        super(NonMatchingSystemError, self).__init__(msg)


def get_frame_reader(top, traj=None, frame_start=0, name=None):
    readers = collections.OrderedDict([
        ("mdtraj", FrameReaderMDTraj)
    ])

    nonmatching_atoms = False

    if name is not None:
        try:
            return readers[name](top, traj, frame_start)
        except KeyError as e:
            e.args = ("Frame reader '{0}' is not a valid option.".format(name),)
            raise
    else:
        for name, reader in readers.items():  # Return first reader that accepts given files
            try:
                r = reader(top, traj, frame_start)
                print()
                print("Using '" + name + "' trajectory reader")
                r.warn()
                print()
                return r
            except (UnsupportedFormatException, ImportError) as e2:
                print("Failed to read using '" + name + "' trajectory reader")
                continue
            except NonMatchingSystemError:
                print("Failed to read using '" + name + "' trajectory reader")
                nonmatching_atoms = True
                continue

    if nonmatching_atoms:
        raise NonMatchingSystemError
    raise UnsupportedFormatException("None of the available readers support the trajector format provided, {0} {1}".format(top, traj))


class FrameReader(metaclass=abc.ABCMeta):
    def __init__(self, topname, trajname=None, frame_start=0):
        self._topname = topname
        self._trajname = trajname
        self._frame_number = frame_start

        self.num_atoms = 0
        self.num_frames = 0

        self.warnings = None

    def initialise_frame(self, frame):
        self._initialise_frame(frame)

    def read_next(self, frame):
        result = self.read_frame_number(self._frame_number, frame)
        if result:
            self._frame_number += 1
        return result

    def read_frame_number(self, number, frame):
        try:
            time, coords, box = self._read_frame_number(number)
            print(box, frame.number)
            if box is None:
                box = np.zeros(3)
            frame.time = time
            frame.box = box

            for atom, coord_line in zip(itertools.chain.from_iterable(frame.residues), coords):
                atom.coords = coord_line

        except (IndexError, AttributeError):
            # IndexError - run out of xtc frames
            # AttributeError - we didn't provide an xtc
            return False
        return True

    def warn(self):
        if self.warnings is not None:
            for warning in self.warnings:
                logger.warning("WARNING: " + warning)

    @abc.abstractmethod
    def _initialise_frame(self, frame):
        pass

    @abc.abstractmethod
    def _read_frame_number(self, number):
        pass


    def _initialise_frame(self, frame):
        """
        Parse a GROMACS GRO file and create Residues/Atoms
        Required before reading coordinates from XTC file
        :param frame: Frame instance to initialise from GRO file
        """
        with open(self._topname) as gro:
            frame.name = gro.readline().strip()
            try:
                self.num_atoms = int(gro.readline())
            except ValueError as e:
                raise UnsupportedFormatException from e

            frame.natoms = self.num_atoms
            resnum_last = None
            atnum = 0

            unpacker = FixedFormatUnpacker("I5,2A5,5X,3F8",
                                           FixedFormatUnpacker.FormatStyle.Fortran)

            for _ in range(self.num_atoms):
                resnum, resname, atomname, *coords = unpacker.unpack(gro.readline())
                coords = np.array(coords, dtype=np.float32)

                if resnum != resnum_last:
                    frame.residues.append(Residue(name=resname,
                                                  num=resnum))
                    resnum_last = resnum
                    atnum = 0

                atom = Atom(name=atomname, num=atnum, coords=coords)
                frame.residues[-1].add_atom(atom)
                atnum += 1

            frame.box = np.array([float(x) for x in gro.readline().split()[0:3]], dtype=np.float32)

    def _read_frame_number(self, number):
        """
        Read next frame from XTC using simpletraj library.
        """
        self._traj.get_frame(number)
        # SimpleTraj uses Angstrom, we want nanometers
        xyz = self._traj.x / 10
        box = np.diag(self._traj.box)[0:3] / 10

        return self._traj.time, xyz, box

class FrameReaderMDTraj(FrameReader):
    def __init__(self, topname, trajname=None, frame_start=0):
        """
        Open input XTC file from which to read coordinates using mdtraj library.

        :param topname: GROMACS GRO file from which to read topology
        :param trajname: GROMACS XTC file to read subsequent frames
        """
        FrameReader.__init__(self, topname, trajname, frame_start)
        self.warnings = ["MDTraj renames solvent molecules"]

        try:
            import mdtraj
        except ImportError as e:
            if "scipy" in repr(e):
                e.msg = "The MDTraj FrameReader also requires Scipy"
            else:
                e.msg = "The MDTraj FrameReader requires the module MDTraj (and probably Scipy)"
            raise

        try:
            if trajname is None:
                self._traj = mdtraj.load(topname)
            else:
                self._traj = mdtraj.load(trajname, top=topname)
        except OSError as e:
            if not os.path.isfile(topname):
                raise FileNotFoundError(topname) from e
            if trajname is not None and not os.path.isfile(trajname):
                raise FileNotFoundError(trajname) from e
            if "no loader for filename" in repr(e):
                raise UnsupportedFormatException from e
            e.args = ("Error opening file '{0}' or '{1}'".format(topname, trajname),)
            raise
        except ValueError as e:
            if "xyz must be shape" in repr(e):
                raise NonMatchingSystemError from e

        self.num_atoms = self._traj.n_atoms
        self.num_frames = self._traj.n_frames

    def _initialise_frame(self, frame):
        """
        Parse a GROMACS GRO file and create Residues/Atoms
        Required before reading coordinates from XTC file

        :param frame: Frame instance to initialise from GRO file
        """
        import mdtraj
        top = mdtraj.load(self._topname)

        frame.name = ""
        self.num_atoms = top.n_atoms
        frame.natoms = top.n_atoms

        frame.residues = [Residue(name=res.name, num=res.resSeq) for res in top.topology.residues]

        for atom in top.topology.atoms:
            new_atom = Atom(name=atom.name, num=atom.serial,
                            coords=top.xyz[0][atom.index])
            frame.residues[atom.residue.index].add_atom(new_atom)

        if top.unitcell_lengths is None:
            top.unitcell_lengths = [np.array([0., 0., 0.])]
        frame.box = top.unitcell_lengths[0]

    def _read_frame_number(self, number):
        """
        Read next frame from XTC using mdtraj library.
        """
        try:
            return self._traj.time[number], self._traj.xyz[number], self._traj.unitcell_lengths[number]
        except TypeError:
            return self._traj.time[number], self._traj.xyz[number], None


