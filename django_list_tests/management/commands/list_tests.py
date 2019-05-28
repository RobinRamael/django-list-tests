import unittest

from django.core.management import BaseCommand


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

    def handle(self, *args, **kwargs):
        app_name = kwargs.get("app_name", ".")
        methods_only = kwargs.get("methods_only", False)
        suite = unittest.defaultTestLoader.discover(app_name)

        test_names = get_test_names(suite, app_name, methods_only)

        for name in test_names:
            self.stdout.write(name)
