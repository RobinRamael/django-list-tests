import time
import unittest

from django.core.management import BaseCommand
from livereload import Server
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from django_list_tests.common import TestRuns


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


def get_sorted_test_names(app_name, use_mru=True, methods_only=False):
    suite = unittest.defaultTestLoader.discover(app_name)

    test_names = get_test_names(suite, app_name, methods_only)

    if use_mru:
        prev_test_runs = TestRuns.load()
        unused_tests = test_names - set(prev_test_runs.test_counter.keys())
        ordered_names = [test for test, _ in prev_test_runs.test_counter.most_common()] + sorted(unused_tests)
    else:
        ordered_names = sorted(test_names)

    return ordered_names


def write_names(names, fp):
    fp.writelines("{}\n".format(name) for name in names)


def list_tests(app_name, use_mru=True, methods_only=False, outfile=None, stdout=None):
    test_names = get_sorted_test_names(app_name, use_mru, methods_only)

    if outfile:
        with open(outfile, "w") as fp:
            write_names(test_names, fp)
    else:
        write_names(test_names, stdout)


class ListTestsHandler(FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def on_modified(self, event):
        print("change detected, regenerating test names")
        list_tests(*self.args, **self.kwargs)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("app_name", default=".", nargs="?")
        parser.add_argument("--methods-only", dest="methods_only", action="store_true")
        parser.add_argument("--no-mru", dest="use_mru", action="store_false")
        parser.add_argument("--out", dest="outfile", default=None)
        parser.add_argument("--watch", action="store_true", dest="watch", default=None)

    def handle(self, *args, **kwargs):
        app_name = kwargs.get("app_name", ".")
        methods_only = kwargs.get("methods_only", False)
        outfile = kwargs.get("outfile", None)
        use_mru = kwargs.get("use_mru", True)
        watch = kwargs.get("watch", False)

        if not watch:
            return list_tests(app_name, use_mru, methods_only, outfile, self.stdout)

        observer = Observer()

        handler = ListTestsHandler(app_name, use_mru, methods_only, outfile, self.stdout)
        observer.schedule(handler, "src/", recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
