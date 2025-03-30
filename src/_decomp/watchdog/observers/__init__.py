#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\observers\__init__.py
import warnings
from watchdog.utils import platform
from watchdog.utils import UnsupportedLibc
if platform.is_linux():
    try:
        from .inotify import InotifyObserver as Observer
    except UnsupportedLibc:
        from .polling import PollingObserver as Observer

elif platform.is_darwin():
    try:
        from .fsevents import FSEventsObserver as Observer
    except Exception:
        try:
            from .kqueue import KqueueObserver as Observer
            warnings.warn('Failed to import fsevents. Fall back to kqueue')
        except Exception:
            from .polling import PollingObserver as Observer
            warnings.warn('Failed to import fsevents and kqueue. Fall back to polling.')

elif platform.is_bsd():
    from .kqueue import KqueueObserver as Observer
elif platform.is_windows():
    try:
        from .read_directory_changes import WindowsApiObserver as Observer
    except Exception:
        from .polling import PollingObserver as Observer
        warnings.warn('Failed to import read_directory_changes. Fall back to polling.')

else:
    from .polling import PollingObserver as Observer
__all__ = ['Observer']
