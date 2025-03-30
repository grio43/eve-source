#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\iconIDs.py
import iconIDsLoader
from fsdBuiltData.common.base import BuiltDataLoader

class IconIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/iconIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/iconIDs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/iconIDs.fsdbinary'
    __loader__ = iconIDsLoader


def GetIconIDDictionary():
    return IconIDs.GetData()


def GetIcon(iconID):
    return IconIDs.GetData().get(iconID, None)


def GetIconAttribute(iconID, attributeName, default = None):
    if isinstance(iconID, (int, long)):
        return getattr(GetIcon(iconID), attributeName, None) or default
    return getattr(iconID, attributeName, None) or default


def GetIconFile(iconID, default = None):
    return GetIconAttribute(iconID, 'iconFile', default)


def GetIconType(iconID, default = None):
    return GetIconAttribute(iconID, 'iconType', default)
