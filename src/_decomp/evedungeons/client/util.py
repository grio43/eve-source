#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evedungeons\client\util.py
import evetypes
from inventorycommon.const import categoryShip
from evedungeons.common.constants import ACCELERATION_GATE_BLACKLISTED_GROUPS
from utillib import KeyVal
from .data import GetDungeon

def CanEnterDungeonInCurrentShip(dungeonID, gateID = None):
    shipRestrictions = GetDungeonShipRestrictions(dungeonID, gateID)
    if not shipRestrictions:
        return True
    shipTypeID = None
    if session.shipid:
        item = sm.GetService('invCache').GetInventoryFromId(session.shipid).GetItem()
        if item:
            shipTypeID = item.typeID
    if not shipTypeID:
        return False
    return shipTypeID in shipRestrictions.allowedShipTypes


def GetDungeonShipRestrictions(dungeonID, gateID = None):
    if not dungeonID:
        return None
    dungeon = GetDungeon(dungeonID)
    if not dungeon or not dungeon.connections:
        return None
    allShipTypes = evetypes.GetTypeIDsByCategory(categoryShip)
    whitelist = set(allShipTypes)
    nonDefaultShipRestrictions = False

    def IsTypeValid(typeID, allowedShipRaces, allowedShipsList):
        if allowedShipsList:
            if typeID not in evetypes.GetTypeIDsByListID(allowedShipsList):
                return False
        if allowedShipRaces:
            raceID = evetypes.GetRaceID(typeID)
            if raceID and raceID not in allowedShipRaces:
                return False
        return True

    for connection in dungeon.connections:
        if gateID and gateID != connection.fromObjectID:
            continue
        allowedShipRaces = connection.allowedShipRaces or []
        if allowedShipRaces or connection.allowedShipsList:
            allowedTypes = [ typeID for typeID in allShipTypes if IsTypeValid(typeID, allowedShipRaces, connection.allowedShipsList) ]
            whitelist = whitelist.intersection(allowedTypes)
            nonDefaultShipRestrictions = True

    if not nonDefaultShipRestrictions:
        whitelist = whitelist.difference(evetypes.GetTypeIDsByGroups(ACCELERATION_GATE_BLACKLISTED_GROUPS))
    restrictedTypes = allShipTypes.difference(whitelist)
    return KeyVal(allowedShipTypes=list(whitelist), restrictedShipTypes=list(restrictedTypes), nonDefaultShipRestrictions=nonDefaultShipRestrictions)


def GetDungeonShipRestrictionsTypeListID(dungeonID, gateID = None):
    if not dungeonID:
        return None
    dungeon = GetDungeon(dungeonID)
    if not dungeon or not dungeon.connections:
        return None
    for connection in dungeon.connections:
        if gateID and gateID != connection.fromObjectID:
            continue
        if connection.allowedShipsList:
            return connection.allowedShipsList


def GetDungeonContentTags(dungeon_id):
    from evearchetypes import GetArchetype
    import inventorycommon.const as invConst
    from metadata.common.content_tags import ContentTags
    result = []
    data = GetDungeon(dungeon_id)
    archetypeData = GetArchetype(data.archetypeID)
    if data.contentTags:
        result.extend(data.contentTags)
    if archetypeData.contentTags:
        result.extend(archetypeData.contentTags)
    if data.entryTypeID == invConst.typeDeadspaceSignature:
        result.append(ContentTags.feature_cosmic_signatures)
    result.append(ContentTags.feature_dungeons)
    return result
