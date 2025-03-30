#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipskins\uiUtil.py
from collections import defaultdict
import evetypes

def GroupAndFilterByShip(skins, filterText):
    skinsByShipID = defaultdict(list)
    for skin in skins:
        for shipTypeID in skin.types:
            if _IsFilterMatch(shipTypeID, skin, filterText):
                skinsByShipID[shipTypeID].append(skin)

    return skinsByShipID


def _IsFilterMatch(shipTypeID, skin, filterText):
    if len(filterText) == 0:
        return True
    shipName = evetypes.GetName(shipTypeID).lower()
    skinName = skin.name.lower()
    return filterText in shipName or filterText in skinName


def PickRepresentingSkin(skins):
    licensedSkins = filter(lambda s: s.licensed, skins)
    if not licensedSkins:
        return skins[0]
    else:
        permanentSkins = filter(lambda s: s.expires is None, licensedSkins)
        if permanentSkins:
            return permanentSkins[0]
        limitedSkins = filter(lambda s: s.expires, licensedSkins)
        limitedSkins = sorted(limitedSkins, key=lambda s: s.expires, reverse=True)
        return limitedSkins[0]


def GetDataForSkinEntry(shipTypeID, skins):
    skin = PickRepresentingSkin(skins)
    data = {'typeID': shipTypeID,
     'itemID': None,
     'label': evetypes.GetName(shipTypeID),
     'getIcon': True,
     'sublevel': 1,
     'skin': skin}
    return data


def GetSkinsAndTexturePathsByByMaterialName(skinsByMaterialID, cosmeticsSvc):
    skinsByName = defaultdict(set)
    texturePathsByName = defaultdict(list)
    for materialID, skins in skinsByMaterialID.iteritems():
        material = cosmeticsSvc.GetStaticMaterialByID(materialID)
        materialName = material.name
        skinsByName[materialName].update(skins)
        texturePathsByName[materialName].append(material.iconTexturePath)

    return (skinsByName, texturePathsByName)
