#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\inventorycommon\util.py
import random
from eve.common.script.sys import idCheckers
import evetypes
from inventorycommon.const import typePlasticWrap, packagedVolumeOverridesPerGroup, packagedVolumeOverridesPerType
from itertoolsext import Bundle
import inventorycommon.const as invconst
import dogma.const as dogmaconst

def IsNPC(ownerID):
    return idCheckers.IsNPC(ownerID)


def IsWormholeSystem(itemID):
    return idCheckers.IsWormholeSystem(itemID)


def IsWormholeConstellation(constellationID):
    return idCheckers.IsWormholeConstellation(constellationID)


def IsWormholeRegion(regionID):
    return idCheckers.IsWormholeRegion(regionID)


def GetPackagedVolume(typeID):
    try:
        volume = packagedVolumeOverridesPerType[typeID]
    except KeyError:
        groupID = evetypes.GetGroupID(typeID)
        try:
            volume = packagedVolumeOverridesPerGroup[groupID]
        except KeyError:
            volume = evetypes.GetVolume(typeID)

    return volume


def GetItemVolume(item, qty = None):
    if item.singleton:
        if item.typeID == typePlasticWrap:
            volume = -item.quantity / 100.0
            if volume <= 0:
                raise RuntimeError('Volume of a plastic wrap should never be zero or less')
        else:
            volume = evetypes.GetVolume(item.typeID)
    else:
        volume = GetPackagedVolume(item.typeID)
    if volume != -1:
        if qty is None:
            qty = item.stacksize
        if qty < 0:
            qty = 1
        volume *= qty
    return float(volume)


def GetTypeVolume(typeID, qty = -1):
    if typeID == typePlasticWrap:
        raise RuntimeError('GetTypeVolume: cannot determine volume of plastic from type alone')
    item = Bundle(typeID=typeID, groupID=evetypes.GetGroupID(typeID), categoryID=evetypes.GetCategoryID(typeID), quantity=qty, singleton=-qty if qty < 0 else 0, stacksize=qty if qty >= 0 else 1)
    return GetItemVolume(item)


def GetVolumeForPlasticItem(itemID):
    return sm.GetService('invCache').GetInventoryFromId(itemID).GetCapacity().used


def GetRandomSubsystemTypeIDs(typeID):
    if not IsModularShip(typeID):
        return None
    subsystems = {}
    subSystemsForType = {}
    godma = sm.GetService('godma')
    for groupID in evetypes.GetGroupIDsByCategory(invconst.categorySubSystem):
        if groupID not in subSystemsForType:
            subSystemsForType[groupID] = []
        for tid in evetypes.GetTypeIDsByGroup(groupID):
            if evetypes.IsPublished(tid) and godma.GetTypeAttribute(tid, dogmaconst.attributeFitsToShipType) == typeID:
                subSystemsForType[groupID].append(tid)

    for k, v in subSystemsForType.iteritems():
        if len(v) is not 0:
            subsystems[k] = random.choice(v)

    return subsystems.values()


def GetSubSystemTypeIDs(itemID, typeID):
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    return GetSubSystemTypeIDsForDogmaLocation(itemID, typeID, dogmaLocation)


def GetSubSystemTypeIDsForDogmaLocation(itemID, typeID, dogmaLocation):
    if not IsModularShip(typeID):
        return
    dogmaItem = dogmaLocation.dogmaItems.get(itemID, None)
    if dogmaItem is None:
        return
    fittedSubsystems = [ fittedItem for fittedItem in dogmaItem.GetFittedItems().itervalues() if fittedItem.categoryID == invconst.categorySubSystem ]
    return [ item.typeID for item in fittedSubsystems ]


def IsSubsystemFlag(flagID):
    return invconst.flagSubSystemSlot0 <= flagID <= invconst.flagSubSystemSlot7


def IsSubsystemFlagVisible(flagID):
    return flagID in invconst.subsystemSlotFlags


def IsRigFlag(flagID):
    return invconst.flagRigSlot0 <= flagID <= invconst.flagRigSlot7


def IsStructureServiceFlag(flagID):
    return flagID in invconst.serviceSlotFlags


def IsModularShip(typeID):
    return evetypes.GetGroupID(typeID) == invconst.groupStrategicCruiser


def IsShipFittingFlag(flagID):
    return flagID in invconst.fittingFlags or flagID == invconst.flagHiddenModifers


def IsStructureFittingFlag(flagID):
    return flagID in invconst.structureFittingFlags or flagID == invconst.flagHiddenModifers


def IsFighterTubeFlag(flagID):
    return flagID in invconst.fighterTubeFlags


def IsFittingFlag(flagID):
    return flagID in invconst.fittingFlags or flagID in invconst.structureFittingFlags or flagID == invconst.flagHiddenModifers


def IsPlayerItem(itemID):
    return idCheckers.IsPlayerItem(itemID)


def IsFittingModule(categoryID):
    return categoryID in (invconst.categoryModule, invconst.categoryStructureModule)


def IsShipFittingModule(categoryID):
    return categoryID == invconst.categoryModule


def IsFittable(categoryID):
    return categoryID in (invconst.categoryModule,
     invconst.categorySubSystem,
     invconst.categoryStructureModule,
     invconst.categoryInfrastructureUpgrade)


def IsShipFittable(categoryID):
    return categoryID in (invconst.categoryModule, invconst.categorySubSystem, invconst.categoryStructureModule)


def IsStructureFittable(categoryID):
    return categoryID in (invconst.categoryStructureModule,)


def IsJunkLocation(locationID):
    return idCheckers.IsJunkLocation(locationID)


def ShipCanUnfitRigs(shipTypeID):
    return evetypes.GetGroupID(shipTypeID) == invconst.groupStrategicCruiser


def IsTypeContainer(typeID):
    if evetypes.GetCategoryID(typeID) in invconst.CONTAINER_CATEGORIES:
        return True
    if evetypes.GetGroupID(typeID) in invconst.CONTAINER_GROUPS:
        return True
    return False
