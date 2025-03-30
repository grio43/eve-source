#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventorycommon\__init__.py
from inventorycommon.const import ixSingleton, flagHiddenModifers

def IsBecomingSingleton(change):
    if ixSingleton in change:
        old_singleton, new_singleton = change[ixSingleton]
        if not old_singleton and new_singleton:
            return True
    return False


def ItemIsVisible(item):
    return item.flagID != flagHiddenModifers


class WrongInventoryLocation(RuntimeError):
    pass


class FakeItemNotHere(RuntimeError):
    pass
