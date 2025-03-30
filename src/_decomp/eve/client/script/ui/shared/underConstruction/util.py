#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\underConstruction\util.py
import mathext
from inventorycommon.typeHelpers import GetAveragePrice
import evetypes
import eve.common.lib.appConst as appConst
import logging
logger = logging.getLogger(__name__)
DEFAULT_FACTION_BG = 'res:/UI/Texture/classes/underConstruction/backgrounds/bg_faction_default.png'
FACTION_BG_HEIGHT = 1080
FACTION_BG_WIDTH = 1680
bgTextureByFactionID = {appConst.factionAmarrEmpire: 'res:/UI/Texture/classes/underConstruction/backgrounds/bg_faction_500003.png',
 appConst.factionCaldariState: 'res:/UI/Texture/classes/underConstruction/backgrounds/bg_faction_500001.png',
 appConst.factionGallenteFederation: 'res:/UI/Texture/classes/underConstruction/backgrounds/bg_faction_500004.png',
 appConst.factionMinmatarRepublic: 'res:/UI/Texture/classes/underConstruction/backgrounds/bg_faction_500002.png'}
textureInfoByGroupID = {}
textureInfoByTypeID = {appConst.typeShipcasterBeaconAmarr: ('res:/UI/Texture/classes/underConstruction/outputImages/type75928.png', 1680, 1080),
 appConst.typeShipcasterBeaconCaldari: ('res:/UI/Texture/classes/underConstruction/outputImages/type75929.png', 1680, 1080),
 appConst.typeShipcasterBeaconGallente: ('res:/UI/Texture/classes/underConstruction/outputImages/type75930.png', 1680, 1080),
 appConst.typeShipcasterBeaconMinmatar: ('res:/UI/Texture/classes/underConstruction/outputImages/type75931.png', 1680, 1080)}

def GetBgTextureInfo(typeID):
    textureInfo = textureInfoByTypeID.get(typeID, None)
    if textureInfo:
        return textureInfo
    textureInfo = textureInfoByGroupID.get(evetypes.GetGroupID(typeID), None)
    return textureInfo


def GetFactionBgTexturePath(typeID):
    factionID = evetypes.GetFactionID(typeID)
    return bgTextureByFactionID.get(factionID, DEFAULT_FACTION_BG)


def GetProgressFromQty(qtyByTypeID, qtyRequiredByTypeID):
    priceProgress = _CalculatePriceProgress(qtyByTypeID, qtyRequiredByTypeID)
    if priceProgress is not None:
        return priceProgress
    return _CalculateComponentProgress(qtyByTypeID, qtyRequiredByTypeID)


def _CalculatePriceProgress(qtyByTypeID, qtyRequiredByTypeID):
    valueOfComponents = 0
    totalValueOfNeeded = 0
    try:
        for typeID, reqQty in qtyRequiredByTypeID.iteritems():
            typePrice = GetAveragePrice(typeID)
            if not typePrice:
                return
            totalValueOfNeeded += typePrice * reqQty
            currentQty = qtyByTypeID.get(typeID, 0)
            valueOfComponents += currentQty * typePrice

        if totalValueOfNeeded:
            return float(valueOfComponents) / totalValueOfNeeded
    except StandardError as e:
        logger.exception('Failed _CalculatePriceProgress for wnd')


def _CalculateComponentProgress(qtyByTypeID, qtyRequiredByTypeID):
    progressValues = []
    for typeID, reqQty in qtyRequiredByTypeID.iteritems():
        currentQty = qtyByTypeID.get(typeID, 0)
        progressValues.append(float(currentQty) / reqQty)

    componentProgress = sum(progressValues) / len(progressValues)
    return mathext.clamp(componentProgress, 0.0, 1.0)
