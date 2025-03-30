#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sofDnaLibrary\data.py
import os
import site
import evetypes
site.addsitedir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from shipskins.static import SkinStorage, SkinMaterialStorage
from fsdBuiltData.common import graphicIDs, graphicMaterialSets
_skins = None
_materials = None
_materialSets = None
_graphicIDs = None

def GetSkins():
    global _skins
    if _skins is None:
        _skins = SkinStorage()
    return _skins


def GetMaterialSets():
    global _materialSets
    if _materialSets is None:
        _materialSets = graphicMaterialSets.GetGraphicMaterialSets()
    return _materialSets


def GetMaterials():
    global _materials
    if _materials is None:
        materials = SkinMaterialStorage()
        materialSets = GetMaterialSets()
        _materials = {}
        for materialID, material in materials.iteritems():
            _materials[int(material.skinMaterialID)] = materialSets[int(material.materialSetID)]

    return _materials


def GetTypes():
    return evetypes.GetTypes()


def GetGraphicIDs():
    global _graphicIDs
    if _graphicIDs is None:
        _graphicIDs = graphicIDs.GetGraphicIDDictionary()
    return _graphicIDs
