#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\structures\types.py
import structures.const as const
from evetypes import GetCategoryID
from inventorycommon.const import categoryStructure
from inventorycommon.const import groupFuelBlock, typeLiquidOzone, typeColonyReagentLava
import evetypes
from eve.common.script.sys import idCheckers

def IsFlexStructure(typeID):
    if GetCategoryID(typeID) != categoryStructure:
        return False
    return GetStructureSize(typeID) == const.STRUCTURE_SIZE_FLEX


def GetStructureSize(typeID):
    return const.STRUCTURE_SIZE_BY_TYPE.get(typeID, const.STRUCTURE_SIZE_UNDEFINED)


def GetAllowedFuelTypeIDs(typeID):
    fuelBlocks = evetypes.GetTypeIDsByGroup(groupFuelBlock)
    if idCheckers.IsAutoMoonMiner(typeID):
        fuelBlocks.add(typeColonyReagentLava)
    else:
        fuelBlocks.add(typeLiquidOzone)
    return fuelBlocks
