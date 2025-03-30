#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdlite\__init__.py
try:
    from _fsdlite import dump, load, encode, decode, strip
except:
    from .encoder import dump, load, encode, decode, strip

from .util import repr, WeakMethod, extend_class, Extendable
from .monitor import start_file_monitor, stop_file_monitor
from .indexer import index
from .cache import Cache
from .storage import Storage, WeakStorage, EveStorage, DontUseSource, UseSource
