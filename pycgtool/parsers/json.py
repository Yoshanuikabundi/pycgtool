import json


class DuplicateSectionError(Exception):
    """
    Exception used to indicate that a section has appeared twice in a file.
    """
    def __repr__(self):
        return "Section {0} appears twice in file {1}.".format(*self.args)


class Record(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]


class CFG:
    def __init__(self, filename):
        with open(filename) as f:
            try:
                self._json = json.load(f, object_hook=Record)
            except ValueError:
                raise DuplicateSectionError()

    def __getitem__(self, item):
        return Record(self._json[item])

    def __contains__(self, item):
        return item in self._json

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
