#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\watchdog\utils\compat.py
__all__ = ['queue', 'Event', 'scandir']
try:
    import queue
except ImportError:
    import Queue as queue

try:
    from os import scandir
except ImportError:
    from os import listdir as scandir

from threading import Event
