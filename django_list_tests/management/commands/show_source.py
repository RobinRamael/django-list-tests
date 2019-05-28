import importlib
import inspect

from django.core.management import BaseCommand
from pygments import formatters, highlight
from pygments.lexers import PythonLexer


def get_source_as_method(fqn):

    module_name = ".".join(fqn.split(".")[:-2])
    klass_name = fqn.split(".")[-2]
    method_name = fqn.split(".")[-1]

    module = importlib.import_module(module_name)

    klass = getattr(module, klass_name)
    method = getattr(klass, method_name)

    code = inspect.getsource(method)

    return code


def get_source_as_class(fqn):
    module_name = ".".join(fqn.split(".")[:-1])
    klass_name = fqn.split(".")[-1]

    module = importlib.import_module(module_name)
    klass = getattr(module, klass_name)

    code = inspect.getsource(klass)

    return code


def get_source_as_module(fqn):
    module = importlib.import_module(fqn)
    code = inspect.getsource(module)
    return code


def print_colored(code):
    print(highlight(code, PythonLexer(), formatters.TerminalFormatter()))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("method_fqn")

    def handle(self, *args, **kwargs):
        fqn = kwargs.get("method_fqn")

        try:
            code = get_source_as_method(fqn)
            print_colored(code)
        except AttributeError:
            try:
                code = get_source_as_class(fqn)
                print_colored(code)
            except AttributeError:
                code = get_source_as_module(fqn)
                print_colored(code)
