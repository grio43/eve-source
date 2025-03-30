#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\reprocessing\util.py
import logging
from inventorycommon.typeHelpers import GetAdjustedAveragePrice
from itertoolsext import Bundle
import inventorycommon.const as invconst
import dogma.const as dgmconst
from eveexceptions import UserError
from math import floor
import evetypes
import typematerials.data
logger = logging.getLogger(__name__)

def GetReprocessInfoForItem(reprocessingSvc, charID, item, itemsToBeReprocessed, stationsTake):
    portionSize = evetypes.GetPortionSize(item.typeID)
    stacksize = item.stacksize
    portions = stacksize / portionSize
    leftOvers = stacksize % portionSize
    quantityToProcess = stacksize - leftOvers
    efficiency = _GetEfficiency(reprocessingSvc, charID, item.typeID)
    recoverables = _GetRecoverables(item, stationsTake, portions, efficiency)
    return (item.itemID,
     item.typeID,
     int(round(quantityToProcess)),
     int(round(leftOvers)),
     recoverables)


def GetRefiningYieldPercentageForType(charID, dogmaIM, dogmaLM, skillHandler, typeID):
    if evetypes.GetCategoryID(typeID) == invconst.categoryAsteroid:
        refiningYieldPercentage = dogmaLM.GetCharacterAttribute(charID, dgmconst.attributeRefiningYieldPercentage)
        skillTypeID = dogmaIM.GetTypeAttribute(typeID, dgmconst.attributeReprocessingSkillType)
    else:
        refiningYieldPercentage = 1.0
        skillTypeID = invconst.typeScrapmetalProcessing
    skillLevel = skillHandler.GetSkillLevel(skillTypeID)
    percentagePerLevel = dogmaIM.GetTypeAttribute2(skillTypeID, dgmconst.attributeRefiningYieldMutator)
    refiningYieldPercentage *= (100 + skillLevel * float(percentagePerLevel)) / 100
    return refiningYieldPercentage


def _GetEfficiency(reprocessingSvc, charID, typeID):
    stationEfficiency = reprocessingSvc.GetStationEfficiencyForTypeID(typeID)
    efficiency = min(stationEfficiency * reprocessingSvc.GetCharRefiningYieldPercentageForType(charID, typeID), 1.0)
    return efficiency


def _GetRecoverables(item, stationsTake, portions, efficiency):
    recoverables = []
    if invconst.typeCredits != item.typeID and portions:
        materials = typematerials.get_type_materials_by_id(item.typeID)
        for material in materials:
            try:
                quantity = material.quantity * portions
                recoverable = int(floor(quantity * efficiency))
                client = recoverable
                station = recoverable * stationsTake
                price = GetAdjustedAveragePrice(material.materialTypeID)
                if price is None:
                    price = 0
                iskCost = round(price * station, 2)
            except OverflowError:
                raise UserError('ReprocessingPleaseSplit')

            unrecoverable = int(round(quantity - client))
            recoverables.append(Bundle(typeID=material.materialTypeID, client=client, unrecoverable=unrecoverable, iskCost=iskCost))

    return recoverables
