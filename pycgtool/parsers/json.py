import json
import os


class Record(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]


class CFG:
    def __init__(self, filename, from_section=None):
        with open(filename) as f:
            self._json = json.load(f, object_hook=Record)

        while self._json.include:
            include_file = os.path.join(os.path.dirname(filename), self._json.include.pop())
            with open(include_file) as include_file:
                include_json = json.load(include_file, object_hook=Record)

            for curr, incl in zip(self._json.values(), include_json.values()):
                try:
                    curr += incl
                except TypeError:
                    curr.update(incl)

        if from_section is not None:
            self._records = self._json[from_section]
        else:
            self._records = self._json

    def __getitem__(self, item):
        return self._records[item]

    def __contains__(self, item):
        return item in self._records
