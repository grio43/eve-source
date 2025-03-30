#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\graphicIDs.py
try:
    import graphicIDsLoader
except ImportError:
    graphicIDsLoader = None

from fsdBuiltData.common.base import BuiltDataLoader

class GraphicIDs(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/graphicIDs.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/graphicIDs.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/graphicIDs.fsdbinary'
    __loader__ = graphicIDsLoader


def GetGraphicIDDictionary():
    return GraphicIDs.GetData()


def GetGraphic(graphicID):
    return GraphicIDs.GetData().get(graphicID, None)


def GetGraphicAttribute(graphicID, attributeName, default = None):
    if isinstance(graphicID, (int, long)):
        return getattr(GetGraphic(graphicID), attributeName, None) or default
    return getattr(graphicID, attributeName, None) or default


def GetGraphicFile(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'graphicFile', default)


def GetExplosionBucketID(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'explosionBucketID', default)


def GetSofRaceName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofRaceName', default)


def GetSofHullName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofHullName', default)


def GetSofFactionName(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofFactionName', default)


def GetSofLayoutNames(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofLayout', default)


def GetSofMaterialSetID(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'sofMaterialSetID', default)


def GetCollisionFile(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'collisionFile', default)


def GetIconFolder(graphicID, default = None):
    iconInfo = GetIconInfo(graphicID)
    if iconInfo and hasattr(iconInfo, 'folder'):
        return iconInfo.folder
    return default


def GetIconInfo(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'iconInfo', default)


def GetAnimationStateObjects(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'animationStateObjects', default)


def GetAmmoColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'ammoColor', default)


def GetAlbedoColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'albedoColor', default)


def GetEmissiveColor(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'emissiveColor', default)


def GetGraphicLocationID(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'graphicLocationID', default)


def GetControllerVariableOverrides(graphicID, default = None):
    return GetGraphicAttribute(graphicID, 'controllerVariableOverrides', default)
