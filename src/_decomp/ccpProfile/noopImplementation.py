#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ccpProfile\noopImplementation.py
import contextlib
from . import decorator

@contextlib.contextmanager
def Timer(context):
    yield


@contextlib.contextmanager
def TimerPush(context):
    yield


def TimedFunction(context = None):

    def Wrapper(function, *args, **kwargs):
        return function(*args, **kwargs)

    return decorator.decorator(Wrapper)


def PushTimer(context):
    return None


def PopTimer(context):
    return None


def CurrentTimer():
    return None


def EnterTasklet(*_):
    pass


def ReturnFromTasklet(*_):
    pass
