#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\repackaging\__init__.py
import evetypes
import dogma.const as dogmaconst
import inventorycommon.const as invconst
from eveexceptions import UserError
from inventorycommon.util import IsShipFittingFlag, IsRigFlag, IsJunkLocation, IsNPC, ShipCanUnfitRigs
REPACKABLE_CATEGORIES = (invconst.categoryStarbase,
 invconst.categoryShip,
 invconst.categoryDrone,
 invconst.categoryModule,
 invconst.categorySubSystem,
 invconst.categorySovereigntyStructure,
 invconst.categoryDeployable,
 invconst.categoryStructure,
 invconst.categoryStructureModule,
 invconst.categoryFighter,
 invconst.categoryAncientRelic,
 invconst.categoryInfrastructureUpgrade)
REPACKABLE_CATEGORIES_GROUP_EXCEPTIONS = {invconst.groupCapsule}
REPACKABLE_GROUPS = (invconst.groupCargoContainer,
 invconst.groupSecureCargoContainer,
 invconst.groupAuditLogSecureContainer,
 invconst.groupFreightContainer,
 invconst.groupTool,
 invconst.groupMobileWarpDisruptor,
 invconst.groupPolymerReactionFormulas,
 invconst.groupCompositeReactionFormulas,
 invconst.groupBiochemicalReactionFormulas,
 invconst.groupMolecularForgedReactionFormulas)
REPACKABLE_LOCATION_TYPES = set(evetypes.GetTypeIDsByGroups((invconst.groupCorporateHangarArray, invconst.groupPersonalHangar, invconst.groupStation))) | evetypes.GetTypeIDsByCategories((invconst.categoryStructure,)) | {invconst.typeOffice}

def CheckCanRepackage(item, locationItem, dogma = None):
    if not item.singleton:
        raise UserError('RepackageItemNotSingleton')
    if IsNPC(item.ownerID):
        raise UserError('NotAvailableForNpcCorp')
    if not CanRepackageType(item.typeID):
        raise UserError('CanNotUnassembleInThisItemLoc')
    if not CanRepackageInLocation(item, locationItem):
        raise UserError('CanNotUnassembleInThisItemLoc')
    if dogma and dogma.TypeHasAttribute(item.typeID, dogmaconst.attributeArmorHP):
        if dogma.GetAttributeValue(item.itemID, dogmaconst.attributeArmorDamage):
            raise UserError('CantRepackageDamagedItem')
    if dogma and dogma.TypeHasAttribute(item.typeID, dogmaconst.attributeHp):
        if dogma.GetAttributeValue(item.itemID, dogmaconst.attributeDamage):
            raise UserError('CantRepackageDamagedItem')


def CanRepackageInLocation(item, locationItem):
    if IsShipFittingFlag(item.flagID):
        return False
    if IsJunkLocation(item.locationID):
        return False
    if locationItem.typeID not in REPACKABLE_LOCATION_TYPES:
        return False
    return True


def CanRepackageType(typeID):
    if evetypes.IsDynamicType(typeID):
        return False
    if evetypes.GetCategoryID(typeID) in REPACKABLE_CATEGORIES:
        if evetypes.GetGroupID(typeID) not in REPACKABLE_CATEGORIES_GROUP_EXCEPTIONS:
            return True
    if evetypes.GetGroupID(typeID) in REPACKABLE_GROUPS:
        return True
    return False


def GetContentForRepackaging(contents, containerTypeID):
    moved = []
    destroyed = []
    for item in contents:
        _CheckItem(item)
        if _ItemDestroyed(item, containerTypeID):
            destroyed.append(item)
        elif _ItemPrioritized(item):
            moved.insert(0, item)
        else:
            moved.append(item)

    return (destroyed, moved)


def _CheckItem(item):
    if item.flagID == invconst.flagPilot:
        raise UserError('PeopleAboardShip')


def _ItemDestroyed(item, containerTypeID):
    if item.flagID == invconst.flagHiddenModifers:
        return True
    if IsRigFlag(item.flagID):
        return not ShipCanUnfitRigs(containerTypeID)
    return False


def _ItemPrioritized(item):
    return item.categoryID == invconst.categoryCharge and IsShipFittingFlag(item.flagID)
