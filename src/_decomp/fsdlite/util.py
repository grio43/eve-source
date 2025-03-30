#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdlite\util.py
import weakref
import inspect
import types
import copy

def repr(obj, module = None, exclude = []):
    module = '' if module else module + '.'
    if hasattr(obj, '__slots__'):
        return '<{}{} {}>'.format(module, obj.__class__.__name__, ' '.join([ '{}={}'.format(key, getattr(obj, key, None)) for key in obj.__slots__ if key not in exclude ]))
    elif hasattr(obj, '__dict__'):
        return '<{}{} {}>'.format(module, obj.__class__.__name__, ' '.join([ '{}={}'.format(key, value) for key, value in obj.__dict__.iteritems() if key not in exclude ]))
    else:
        return str(obj)


class WeakMethod(object):

    def __init__(self, f):
        self.f = f.im_func
        self.c = weakref.ref(f.im_self)

    def __call__(self, *args):
        if self.c() is not None:
            apply(self.f, (self.c(),) + args)


def extend_class(cls, mixin):
    for name, member in inspect.getmembers(mixin):
        if inspect.ismethod(member):
            setattr(cls, name, types.MethodType(member.im_func, None, cls))


class Extendable(object):

    @classmethod
    def extend(cls, mixin):
        extend_class(cls, mixin)
