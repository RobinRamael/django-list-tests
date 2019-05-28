import importlib
import inspect

from django.core.management import BaseCommand
from pygments import formatters, highlight
from pygments.lexers import PythonLexer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("method_fqn")

    def handle(self, *args, **kwargs):
        fqn = kwargs.get("method_fqn")

        module_name = ".".join(fqn.split(".")[:-2])
        klass_name = fqn.split(".")[-2]
        method_name = fqn.split(".")[-1]

        module = importlib.import_module(module_name)

        klass = getattr(module, klass_name)
        method = getattr(klass, method_name)

        code = inspect.getsource(method)

        print(highlight(code, PythonLexer(), formatters.TerminalFormatter()))
