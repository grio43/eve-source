#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\client\groupGraphics.py
import groupGraphicsLoader
from fsdBuiltData.common.base import BuiltDataLoader
import evetypes

class GroupGraphics(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/groupGraphics.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/groupGraphics.fsdbinary'
    __loader__ = groupGraphicsLoader
    typeToGraphicCache = {}


def GetGroup(groupID):
    return GroupGraphics.GetData().get(groupID, None)


def GetGroupAttribute(groupID, attributeName, default = None):
    if isinstance(groupID, (int, long)):
        return getattr(GetGroup(groupID), attributeName, None) or default
    return getattr(groupID, attributeName, None) or default


def GetGroupGraphicDictionary():
    return GroupGraphics.GetData()


def _GetTypeOrGroupAttribute(typeID, name, default = None):
    groupID = evetypes.GetGroupID(typeID)
    typeIDs = GetGroupAttribute(groupID, 'typeIDs')
    if typeIDs is not None and typeID in typeIDs and hasattr(typeIDs[typeID], name):
        return getattr(typeIDs[typeID], name)
    return GetGroupAttribute(groupID, name, default)


def GetColorFromTypeID(typeID, default = None):
    color = _GetTypeOrGroupAttribute(typeID, 'color')
    if color is not None:
        return tuple(color)
    return default


def GetColorFromGroupID(groupID, default = None):
    color = GetGroupAttribute(groupID, 'color')
    if color is not None:
        return tuple(color)
    return default


def __ReadGraphicIdsFromTypeAndCache(typeID, default = None):
    graphicsID = _GetTypeOrGroupAttribute(typeID, 'graphicIDs', default)
    GroupGraphics.typeToGraphicCache[typeID] = graphicsID
    return graphicsID


def GetGraphicIdsFromTypeID(typeID, default = None):
    graphicsID = GroupGraphics.typeToGraphicCache.get(typeID, None)
    if graphicsID is None:
        graphicsID = __ReadGraphicIdsFromTypeAndCache(typeID, default)
    return graphicsID


def GetGraphicIdsFromGroupID(groupID, default = None):
    return GetGroupAttribute(groupID, 'graphicIDs', default)
