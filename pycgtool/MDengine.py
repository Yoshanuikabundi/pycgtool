import abc
import shutil
import subprocess



class MDEngine(metaclass=abc.ABCMeta):
    def __init__(self, coordfile, moleculetype, mdp=None, forcefield=None):
        self._coordfile = coordfile
        self._mdp = mdp
        self._itp = moleculetype
        self._forcefield = forcefield
        self.command = None
        self.command_tree = {"setup": None, "run":None}

    def find_md(self):
        pass

    def setup(self):
        pass

class Protocol:
    def __init__(self):
        pass


class Gromacs(MDEngine):
    def __init__(self, coordfile, moleculetype, mdp=None, forcefield=None):
        MDEngine.__init__(self, coordfile, moleculetype, mdp=mdp, forcefield=forcefield)
        self.commands = ["gmx", "gmx_d"]
        self.command = "gmx"
        self.command_tree["setup"] = "grompp"
        self.command_tree["run"] = "mdrun"

        for command in self.commands:
            self.command = shutil.which(command)
            if self.command is not None:
                break






if __name__ == '__main__':
    pwd = "/home/jon/pycgtool/doc/tutorial_files/"
    md = Gromacs(pwd+"out.gro", pwd+"out.itp")
    print(md.command)