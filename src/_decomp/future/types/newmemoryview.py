#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\types\newmemoryview.py
from numbers import Integral
import string
from future.utils import istext, isbytes, PY2, with_metaclass
from future.types import no, issubset
if PY2:
    from collections import Iterable
else:
    from collections.abc import Iterable

class newmemoryview(object):

    def __init__(self, obj):
        return obj


__all__ = ['newmemoryview']
