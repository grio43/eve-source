#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\blue2Py.py
import blue
import types
types.BlueType = type(blue.os)

class DecoMetaClass(type):

    def __init__(cls, name, bases, dict):
        type.__init__(name, bases, dict)
        cls.__persistvars__ = cls.CombineLists('__persistvars__')
        cls.__nonpersistvars__ = cls.CombineLists('__nonpersistvars__')

    def __call__(cls, inst = None, initDict = None):
        if not inst:
            inst = blue.classes.CreateInstance(cls.__cid__)
        inst.__klass__ = cls
        if initDict:
            for k, v in initDict.iteritems():
                setattr(inst, k, v)

        if hasattr(cls, '__init__'):
            inst.__init__()
        return inst

    def CombineLists(cls, name):
        result = []
        for b in cls.__mro__:
            if hasattr(b, name):
                result += list(getattr(b, name))

        return result


def BlueClassCid(cid):
    name = 'DecoMetaClass.' + str(cid)
    return type(name, (DecoMetaClass,), {'__module__': 'Blue2Py',
     '__cid__': cid})


blueClasses = {}

def WrapBlueClass(cid):
    if cid in blueClasses:
        return blueClasses[cid]
    blueClasses[cid] = BlueClassCid(cid)('dummy', (), {'__module__': 'Blue2Py'})
    return blueClasses[cid]


exports = {'util.Blue2Py': WrapBlueClass}
