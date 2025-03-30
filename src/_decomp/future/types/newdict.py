#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\types\newdict.py
import sys
from future.utils import with_metaclass
from future.types.newobject import newobject
_builtin_dict = dict
ver = sys.version_info

class BaseNewDict(type):

    def __instancecheck__(cls, instance):
        if cls == newdict:
            return isinstance(instance, _builtin_dict)
        else:
            return issubclass(instance.__class__, cls)


class newdict(with_metaclass(BaseNewDict, _builtin_dict)):
    if ver >= (3,):
        pass
    elif ver >= (2, 7):
        items = dict.viewitems
        keys = dict.viewkeys
        values = dict.viewvalues
    else:
        items = dict.iteritems
        keys = dict.iterkeys
        values = dict.itervalues

    def __new__(cls, *args, **kwargs):
        return super(newdict, cls).__new__(cls, *args)

    def __native__(self):
        return dict(self)


__all__ = ['newdict']
