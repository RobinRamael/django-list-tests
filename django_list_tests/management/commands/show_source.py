import inspect

from django.core.management import BaseCommand
from pygments import formatters, highlight
from pygments.lexers import PythonLexer

from django_list_tests.common import get_code_obj


def print_colored(code):
    print(highlight(code, PythonLexer(), formatters.TerminalFormatter()))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("method_fqn")

    def handle(self, *args, **kwargs):
        fqn = kwargs.get("method_fqn")
        code_obj = get_code_obj(fqn)
        print_colored(inspect.getsource(code_obj))
