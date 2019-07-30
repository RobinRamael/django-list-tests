import importlib
import json
import os
from collections import Counter


def grow(xs):
    for i in range(len(xs)):
        yield (xs[: i + 1], xs[i + 1:])


def get_code_obj(fqn):

    fqn_parts = fqn.split(".")

    for mod_path, tail in grow(fqn_parts):
        try:
            mod_name = ".".join(mod_path)
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            tail = [mod_path[-1]] + tail
            break

    if not tail:
        return mod

    klass_name = tail.pop(0)
    klass = getattr(mod, klass_name)

    if not tail:
        return klass

    method_name = tail.pop(0)
    return getattr(klass, method_name)


def is_code_obj(fqn):
    try:
        get_code_obj(fqn)
        return True
    except AttributeError:
        return False


def get_mru_filename():
    return os.getenv("MRU_TESTS", "./.mru_tests")


class TestRuns:
    def __init__(self, test_counts=None, last=None):
        self.test_counter = Counter(test_counts or {})
        self.last_run = last

    @classmethod
    def load(cls, file_name=None):
        file_name = file_name or get_mru_filename()
        if os.path.exists(file_name):
            with open(file_name, "r") as fp:
                try:
                    counts = json.load(fp)
                    return cls(counts)
                except json.decoder.JSONDecodeError:
                    return cls()
        else:
            return cls()

    def write(self, file_name=None):
        file_name = file_name or get_mru_filename()

        with open(file_name, "w") as fp:
            json.dump(self.test_counter, fp)

