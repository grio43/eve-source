#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ccpProfile\__init__.py
try:
    from . import blueTaskletImplementation as implementation
except (ImportError, AttributeError):
    from . import noopImplementation as implementation

Timer = implementation.Timer
TimerPush = implementation.TimerPush
TimedFunction = implementation.TimedFunction
PushTimer = implementation.PushTimer
PopTimer = implementation.PopTimer
CurrentTimer = implementation.CurrentTimer
EnterTasklet = implementation.EnterTasklet
ReturnFromTasklet = implementation.ReturnFromTasklet
