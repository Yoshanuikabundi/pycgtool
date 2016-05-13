import json
import os

from .cfg import CFG as OldParser


class AttrDict(dict):
    """
    Class allowing dictionary entries to be accessed as attributes as well as keys.
    """
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class CFG:
    """
    Class to read data from JSON files.  Supports including other files and filtering a single section.
    """
    def __init__(self, filename, from_section=None):
        """
        Create a new CFG JSON parser.

        :param filename: JSON file to read
        :param from_section: Optional section to select from file
        """
        with open(filename) as f:
            self._json = json.load(f, object_hook=AttrDict)

        # Recurse through include lists and add to self._json
        while self._json.include:
            include_file = os.path.join(os.path.dirname(filename), self._json.include.pop())
            with open(include_file) as include_file:
                include_json = json.load(include_file, object_hook=AttrDict)

            for curr, incl in zip(self._json.values(), include_json.values()):
                try:
                    curr += incl
                except TypeError:
                    curr.update(incl)

        self._records = self._json
        if from_section is not None:
            try:
                self._records = self._json[from_section]
            except KeyError as e:
                e.args = ("Section '{0}' not in file '{1}'".format(from_section, filename),)
                raise

    def __getitem__(self, item):
        return self._records[item]

    def __contains__(self, item):
        return item in self._records


def jsonify(mappingfile, bondfile, outfile):
    json_dict = AttrDict({"include": [],
                          "molecules": {}})
    with OldParser(mappingfile) as mappings:
        for mapping in mappings:
            if mapping.name not in json_dict.molecules:
                json_dict.molecules[mapping.name] = {}
            mol = json_dict.molecules[mapping.name]
            mol["beads"] = []
            for line in mapping:
                mol["beads"].append({"name": line[0],
                                     "type": line[1],
                                     "atoms": line[2:]})

    with OldParser(bondfile) as bondlists:
        for bondlist in bondlists:
            try:
                mol = json_dict.molecules[bondlist.name]
            except KeyError:
                continue
            mol["bonds"] = []
            for line in bondlist:
                mol["bonds"].append(line)

    with open(outfile, "w") as out:
        json.dump(json_dict, out, indent=4, sort_keys=True)
