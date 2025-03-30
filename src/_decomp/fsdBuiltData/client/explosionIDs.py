#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\explosionIDs.py
import explosionIDsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class ExplosionIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/explosionIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/explosionIDs.fsdbinary'
    __loader__ = explosionIDsLoader


def GetExplosionIDs():
    return ExplosionIDs.GetData()


def GetExplosion(explosionID):
    return ExplosionIDs.GetData().get(explosionID, None)


def GetExplosionAttribute(explosionID, attributeName, default = None):
    if isinstance(explosionID, (str, unicode)):
        return getattr(GetExplosion(explosionID), attributeName, default)
    return getattr(explosionID, attributeName, default)


def GetExplosionFilePath(explosionID):
    return GetExplosionAttribute(explosionID, 'filePath')
