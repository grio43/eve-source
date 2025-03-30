#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\decometaclass\decometaclass.py
import blue
import types
types.BlueType = type(blue.os)

class DecoMetaclass(type):

    def __new__(mcs, name, bases, dict):
        cls = type.__new__(mcs, name, bases, dict)
        cls.__persistvars__ = cls.CombineLists('__persistvars__')
        cls.__nonpersistvars__ = cls.CombineLists('__nonpersistvars__')
        return cls

    def __call__(cls, inst = None, initDict = None, *args, **kwargs):
        if not inst:
            inst = blue.classes.CreateInstance(cls.__cid__)
        inst.__klass__ = cls
        if initDict:
            for k, v in initDict.iteritems():
                setattr(inst, k, v)

        if hasattr(inst, '__init__'):
            inst.__init__()
        return inst

    def CombineLists(cls, name):
        result = []
        for b in cls.__mro__:
            if hasattr(b, name):
                result += list(getattr(b, name))

        return result

    subclasses = {}


def GetDecoMetaclassInst(cid):

    class parentclass(object):
        __metaclass__ = DecoMetaclass
        __cid__ = cid

    return parentclass


BlueWrappedMetaclass = DecoMetaclass
WrapBlueClass = GetDecoMetaclassInst
