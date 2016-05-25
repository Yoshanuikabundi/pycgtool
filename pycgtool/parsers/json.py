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


class Parser:
    """
    Class to read data from JSON files.  Supports including other files and filtering a single section.
    """
    def __init__(self, filename, section=None):
        """
        Create a new CFG JSON parser.

        :param filename: JSON file to read
        :param section: Optional section to select from file
        """

        with open(filename) as f:
            self._json = json.load(f, object_hook=AttrDict)

        included = set()

        # Recurse through include lists and add to self._json
        try:
            while self._json.include:
                include_file = os.path.join(os.path.dirname(filename), self._json.include.pop())
                if include_file in included:
                    continue
                included.add(include_file)

                with open(include_file) as include_file:
                    include_json = json.load(include_file, object_hook=AttrDict)

                for sec_name, sec_data in include_json.items():
                    try:
                        # Assume is list
                        self._json[sec_name] += sec_data
                    except TypeError:
                        # Is actually a dictionary
                        self._json[sec_name].update(sec_data)
                    except KeyError:
                        # Doesn't exist in self._json, add it
                        self._json[sec_name] = sec_data
            del self._json.include
        except AttributeError:
            # File doesn't have an include section
            pass

        self._records = self._json
        if section is not None:
            try:
                self._records = self._json[section]
            except KeyError as e:
                e.args = ("Section '{0}' not in file '{1}'".format(section, filename),)
                raise

    def __getitem__(self, item):
        return self._records[item]

    def __getattr__(self, item):
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
