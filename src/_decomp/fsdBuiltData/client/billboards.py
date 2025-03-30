#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\billboards.py
import billboardsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class Billboards(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/billboards.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/billboards.fsdbinary'
    __loader__ = billboardsLoader


def GetBillboardData():
    return Billboards.GetData()


def GetFolders(resourceDetails, locale = None, **kwargs):
    requestedOverrides = [ name for name, value in kwargs.iteritems() if value is True ]
    gameplayFolderOverrides = getattr(resourceDetails, 'gameplayFolderOverrides', {})
    gameplayOverrides = [ folderInfo for override, folderInfo in gameplayFolderOverrides.iteritems() if override in requestedOverrides ]
    folderInfo = gameplayOverrides[0] if len(gameplayOverrides) > 0 else resourceDetails.folders
    languageOverrides = getattr(folderInfo, 'languageOverrides', {}).get(locale, None)
    folderList = languageOverrides if languageOverrides is not None else folderInfo.default
    return folderList


def GetVideoSpecificationsIterator(viewName, locale = None, **kwargs):
    data = GetBillboardData().get(viewName)
    if data is not None:
        for resourceName, resourceDetails in data.iteritems():
            folders = GetFolders(resourceDetails, locale, **kwargs)
            yield (resourceName,
             folders,
             resourceDetails.size,
             resourceDetails.fallbackImage,
             resourceDetails.sound)


def AreVideosSupportedForView(viewName):
    return viewName in GetBillboardData()


def GetResourcesForView(viewName):
    return [ resourceName for resourceName in GetBillboardData().get(viewName, {}).iterkeys() ]
