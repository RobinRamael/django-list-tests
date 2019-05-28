import json
import os

from django.core.management.commands import test

from django_list_tests.common import is_code_obj, load_mru_file, write_mru_file


def mark_used(test_name):
    mru_tests = load_mru_file()
    mru_tests[test_name] += 1
    write_mru_file(mru_tests)


class Command(test.Command):
    def handle(self, *args, **kwargs):
        super().handle(*args, **kwargs)

        if is_code_obj(args[0]):
            mark_used(args[0])
