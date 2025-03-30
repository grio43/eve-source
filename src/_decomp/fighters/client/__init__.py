#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fighters\client\__init__.py
from eve.common.script.mgt.fighterConst import TEXTURE_BY_ROLE
from eve.common.script.sys.eveCfg import GetActiveShip
from eveexceptions import UserError
from fighters import SQUADRON_SIZE_SLIMITEM_NAME, fighterClassByDogmaAttribute, SquadronIsLight, SquadronIsSupport, SquadronIsHeavy, GetSquadronRole

def LoadShipIfNecessary(dogmaLocation, shipID):
    if not dogmaLocation.IsItemLoaded(shipID):
        dogmaLocation.LoadItem(shipID)


def GetFighterTubesForShip():
    myShip = GetActiveShip()
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    return GetFighterTubesForShipAndDogmaLocation(myShip, dogmaLocation)


def GetFighterTubesForShipAndDogmaLocation(myShip, dogmaLocation):
    if myShip is None:
        return 0
    LoadShipIfNecessary(dogmaLocation, myShip)
    numOfTubes = int(dogmaLocation.GetAttributeValue(myShip, const.attributeFighterTubes))
    return numOfTubes


def GetLightSupportHeavySlotsForShip():
    myShip = GetActiveShip()
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    return GetLightSupportHeavySlotsForShipAndDogmaLocation(dogmaLocation, myShip)


def GetLightSupportHeavySlotsForShipAndDogmaLocation(dogmaLocation, myShipID):
    LoadShipIfNecessary(dogmaLocation, myShipID)
    lightSlots = GetShipLightSlots(dogmaLocation, myShipID)
    supportSlots = GetShipSupportSlots(dogmaLocation, myShipID)
    heavySlots = GetShipHeavySlots(dogmaLocation, myShipID)
    return (lightSlots, supportSlots, heavySlots)


def GetShipLightSlots(dogmaLocation, shipID):
    lightSlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterLightSlots)) + int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterStandupLightSlots))
    return lightSlots


def GetShipSupportSlots(dogmaLocation, shipID):
    supportSlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterSupportSlots)) + int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterStandupSupportSlots))
    return supportSlots


def GetShipHeavySlots(dogmaLocation, shipID):
    heavySlots = int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterHeavySlots)) + int(dogmaLocation.GetAttributeValue(shipID, const.attributeFighterStandupHeavySlots))
    return heavySlots


def GetSquadronSizeFromSlimItem(slimItem):
    return getattr(slimItem, SQUADRON_SIZE_SLIMITEM_NAME)


def GetFighterClass(dogmaLocation, fighterTypeID):
    for attributeID, fighterClass in fighterClassByDogmaAttribute.iteritems():
        if dogmaLocation.dogmaStaticMgr.GetTypeAttribute(fighterTypeID, attributeID):
            return fighterClass


def GetSquadronClassResPath(typeID):
    if SquadronIsHeavy(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterHeavy.png'
    if SquadronIsSupport(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterMedium.png'
    if SquadronIsLight(typeID):
        return 'res:/UI/Texture/classes/CarrierBay/iconFighterLight.png'


def GetSquadronClassTooltip(typeID):
    if SquadronIsHeavy(typeID):
        return 'UI/Fighters/Class/Heavy'
    if SquadronIsSupport(typeID):
        return 'UI/Fighters/Class/Support'
    if SquadronIsLight(typeID):
        return 'UI/Fighters/Class/Light'


def GetSquadronRoleResPath(typeID):
    squadronRoleID = GetSquadronRole(typeID)
    return TEXTURE_BY_ROLE[squadronRoleID]


def ConvertAbilityFailureReason(fighterID, abilitySlotID, failureReasonUserError):
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsSuspect':
        return UserError('CannotActivateAbilitySafetyPreventsSuspect', failureReasonUserError.dict)
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsCriminal':
        return UserError('CannotActivateAbilitySafetyPreventsCriminal', failureReasonUserError.dict)
    if failureReasonUserError.msg == 'ModuleActivationDeniedSafetyPreventsLimitedEngagement':
        return UserError('CannotActivateAbilitySafetyPreventsLimitedEngagement', failureReasonUserError.dict)
    return failureReasonUserError


def GetSquadronTypes(fighterNumByTypeIDs):
    heavy = 0
    support = 0
    light = 0
    for typeID, num in fighterNumByTypeIDs.iteritems():
        if SquadronIsHeavy(typeID):
            heavy += num
        elif SquadronIsSupport(typeID):
            support += num
        elif SquadronIsLight(typeID):
            light += num

    return (heavy, support, light)
