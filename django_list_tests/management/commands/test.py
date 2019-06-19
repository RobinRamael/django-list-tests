from django.core.management.commands import test

from django_list_tests.common import is_code_obj, TestRuns


def mark_used(test_name):
    runs = TestRuns.load()
    runs.mark_run(test_name)
    runs.write()


class Command(test.Command):
    def handle(self, *args, **kwargs):
        super().handle(*args, **kwargs)

        if is_code_obj(args[0]):
            mark_used(args[0])
