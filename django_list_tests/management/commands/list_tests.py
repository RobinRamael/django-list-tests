import os
import unittest

from django.core.management import BaseCommand

from django_list_tests.common import load_mru_file


def get_test_names(suite, base_app_name, methods_only=False):

    test_names = set()

    if hasattr(suite, "__iter__"):
        for x in suite:
            test_names |= get_test_names(x, base_app_name, methods_only)
    else:
        method = "{mod}.{klass}.{method}".format(
            mod=suite.__module__, klass=suite.__class__.__name__, method=suite._testMethodName
        )
        klass = "{mod}.{klass}".format(mod=suite.__module__, klass=suite.__class__.__name__)

        test_names.add(method)
        if not methods_only:
            test_names.add(klass)
            test_names.add(suite.__module__)

    return test_names


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("app_name", default=".", nargs="?")
        parser.add_argument("--methods-only", dest="methods_only", action="store_true")
        parser.add_argument("--no-mru", dest="use_mru", action="store_false")
        parser.add_argument("--out", dest="outfile", default=None)

    def handle(self, *args, **kwargs):
        app_name = kwargs.get("app_name", ".")
        methods_only = kwargs.get("methods_only", False)
        outfile = kwargs.get("outfile", None)
        use_mru = kwargs.get("use_mru", True)

        suite = unittest.defaultTestLoader.discover(app_name)

        test_names = get_test_names(suite, app_name, methods_only)

        if use_mru:
            mru_tests = load_mru_file()
            unused_tests = test_names - set(mru_tests.keys())
            ordered_names = [test for test, _ in mru_tests.most_common()] + sorted(unused_tests)
        else:
            ordered_names = sorted(test_names)

        if outfile:
            with open(outfile, "w") as fp:
                fp.writelines("{}\n".format(name) for name in ordered_names)
        else:
            for name in ordered_names:
                self.stdout.write(name)
