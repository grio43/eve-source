#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\storage.py
import fsdlite

class BehaviorTree(object):

    @staticmethod
    def __new__(cls, *more):
        obj = super(BehaviorTree, cls).__new__(cls, *more)
        obj.name = None
        obj.description = None
        obj.root = None
        return obj

    def __setstate__(self, data):
        for key, value in data.iteritems():
            if hasattr(self, key):
                setattr(self, key, value)


MAPPING = ()

def BehaviortreeStorage():
    try:
        return BehaviortreeStorage._storage
    except AttributeError:
        BehaviortreeStorage._storage = CreateBehaviortreeStorage()
        return BehaviortreeStorage._storage


def CreateBehaviortreeStorage(cache = 'behaviortrees.static'):
    return fsdlite.EveStorage(data='behaviortrees', cache=cache, mapping=MAPPING, indexes=[], coerce=int)


def BehaviortreeStorageWithNoCache():
    try:
        return BehaviortreeStorageWithNoCache._storage
    except AttributeError:
        BehaviortreeStorageWithNoCache._storage = CreateBehaviortreeStorage(cache=None)
        return BehaviortreeStorageWithNoCache._storage
