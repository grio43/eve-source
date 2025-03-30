#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveaudio\utils.py
from enum import Enum
import audio2

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ControllerVariableEnum(Enum):

    @classmethod
    def EnumValues(cls):
        return ''.join([ '{}={}, '.format(e.name, e.value) for e in cls ])[:-2]


def singleton(cls, *args, **kwargs):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


def create_emitter(name):
    emitter = audio2.AudEmitter(name)
    return emitter
