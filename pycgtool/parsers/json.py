import json
import os


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
