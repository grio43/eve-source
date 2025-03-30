#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\validation\__init__.py
import importlib

def RegisterAll():
    RegisterCFSD()
    RegisterFSD()


def RegisterCFSD():
    pass


def RegisterFSD():
    pass


def Register(module):
    importlib.import_module(module)
