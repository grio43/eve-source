#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinutils\trinfileutils.py
import os
import trinity

def SaveTrinityObject(path, trinObj, checkOutFunc = None):
    if os.path.isfile(path) and checkOutFunc is not None:
        retVal, _ = checkOutFunc(path)
        if not retVal:
            return False
    return trinity.Save(trinObj, path)
