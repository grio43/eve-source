#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fsdBuiltData\common\graphicMaterialSets.py
import graphicMaterialSetsLoader
from fsdBuiltData.common.base import BuiltDataLoader
import logging
log = logging.getLogger(__file__)

class GraphicMaterialSets(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/graphicMaterialSets.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/graphicMaterialSets.fsdbinary'
    __serverAutobuildBuiltFile__ = 'eve/autobuild/staticdata/server/graphicMaterialSets.fsdbinary'
    __loader__ = graphicMaterialSetsLoader


def GetGraphicMaterialSets():
    return GraphicMaterialSets.GetData()


def GetGraphicMaterialSet(materialSetID):
    return GetGraphicMaterialSets().get(materialSetID, None)


def GetGraphicMaterialSetAttribute(materialSetID, attributeName, default = None):
    if isinstance(materialSetID, (int, long)):
        return getattr(GetGraphicMaterialSet(materialSetID), attributeName, None) or default
    return getattr(materialSetID, attributeName, None) or default


def GetSofFactionName(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'sofFactionName', default)


def GetSofPatternName(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'sofPatternName', default)


def GetSofRaceHint(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'sofRaceHint', default)


def GetMaterial1(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'material1', default)


def GetMaterial2(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'material2', default)


def GetMaterial3(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'material3', default)


def GetMaterial4(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'material4', default)


def GetCustomMaterial1(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'custommaterial1', default)


def GetCustomMaterial2(materialSetID, default = 'none'):
    return GetGraphicMaterialSetAttribute(materialSetID, 'custommaterial2', default)


def GetResPathInsert(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'resPathInsert', default)


def GetColorWindows(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'colorWindow', default)


def GetColorHull(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'colorHull', default)


def GetColorPrimary(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'colorPrimary', default)


def GetColorSecondary(materialSetID, default = None):
    return GetGraphicMaterialSetAttribute(materialSetID, 'colorSecondary', default)
