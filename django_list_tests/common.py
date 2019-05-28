import importlib
from collections import Counter
import json
import os


def get_code_obj(fqn):
    try:
        return get_method(fqn)
    except AttributeError:
        try:
            return get_class(fqn)
        except AttributeError:
            return get_module(fqn)


def get_method(fqn):

    module_name = ".".join(fqn.split(".")[:-2])
    klass_name = fqn.split(".")[-2]
    method_name = fqn.split(".")[-1]

    module = importlib.import_module(module_name)

    klass = getattr(module, klass_name)
    return getattr(klass, method_name)


def get_class(fqn):
    module_name = ".".join(fqn.split(".")[:-1])
    klass_name = fqn.split(".")[-1]

    module = importlib.import_module(module_name)
    return getattr(module, klass_name)


def get_module(fqn):
    return importlib.import_module(fqn)


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
