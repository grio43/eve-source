#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\utility\__init__.py
import __builtin__
import inspect
from types import ModuleType
from behaviors.tasks import Task

def get_full_class_name(task):
    return task.__module__ + '.' + task.__name__


def get_tasks_in_module(module):
    return [ cls for name, cls in inspect.getmembers(module) if inspect.isclass(cls) and issubclass(cls, Task) ]


def get_modules_in_module(module):
    return [ member for name, member in inspect.getmembers(module) if inspect.ismodule(member) ]


class DummyModule(ModuleType):
    __all__ = []

    def __getattr__(self, _):
        return None


class ImportFaker(object):

    def __init__(self):
        self.real_import = None

    def try_import(self, name, globals = {}, locals = {}, fromlist = [], level = -1):
        try:
            return self.real_import(name, globals, locals, fromlist, level)
        except (ImportError, TypeError, AttributeError):
            return DummyModule(name)

    def __enter__(self):
        self.real_import = __builtin__.__import__
        __builtin__.__import__ = self.try_import

    def __exit__(self, exc_type, exc_val, exc_tb):
        __builtin__.__import__ = self.real_import
