#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sentry_sdk\_compat.py
import sys
if False:
    from typing import Optional
    from typing import Tuple
    from typing import Any
    from typing import Type
PY2 = sys.version_info[0] == 2
if PY2:
    import urlparse
    text_type = unicode
    import Queue as queue
    string_types = (str, text_type)
    number_types = (int, long, float)
    int_types = (int, long)
    iteritems = lambda x: x.iteritems()

    def implements_str(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: unicode(x).encode('utf-8')
        return cls


    exec 'def reraise(tp, value, tb=None):\n raise tp, value, tb'
else:
    import urllib.parse as urlparse
    import queue
    text_type = str
    string_types = (text_type,)
    number_types = (int, float)
    int_types = (int,)
    iteritems = lambda x: x.items()

    def _identity(x):
        return x


    def implements_str(x):
        return x


    def reraise(tp, value, tb = None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value


def with_metaclass(meta, *bases):

    class metaclass(type):

        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)

    return type.__new__(metaclass, 'temporary_class', (), {})


def check_thread_support():
    try:
        from uwsgi import opt
    except ImportError:
        return

    if 'threads' in opt:
        return
    if str(opt.get('enable-threads', '0')).lower() in ('false', 'off', 'no', '0'):
        from warnings import warn
        warn(Warning('We detected the use of uwsgi with disabled threads.  This will cause issues with the transport you are trying to use.  Please enable threading for uwsgi.  (Enable the "enable-threads" flag).'))
