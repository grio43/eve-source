#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsd\schemas\telemetryMarkup.py
from contextlib import contextmanager
try:
    import blue
    blueAvailable = True
except ImportError:
    blueAvailable = False

if blueAvailable:

    @contextmanager
    def TelemetryContext(name):
        blue.statistics.EnterZone(name)
        try:
            yield
        finally:
            blue.statistics.LeaveZone()


else:

    @contextmanager
    def TelemetryContext(name):
        yield
