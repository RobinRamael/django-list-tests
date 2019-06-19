import importlib
import json
import os
from collections import Counter


def grow(xs):
    yield from ((xs[: i + 1], xs[i + 1 :]) for i in range(len(xs)))


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


def load_mru_file(file_name=None):
    file_name = file_name or get_mru_filename()
    if os.path.exists(file_name):
        with open(file_name, "r") as fp:
            try:
                return Counter(json.load(fp))
            except json.decoder.JSONDecodeError:
                return {}
    else:
        return {}


def write_mru_file(mru_tests, file_name=None):
    file_name = file_name or get_mru_filename()

    with open(file_name, "w") as fp:
        json.dump(mru_tests, fp)
