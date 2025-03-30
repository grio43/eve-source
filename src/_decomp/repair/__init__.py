#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\repair\__init__.py
import inventorycommon.const as invConst
import dogma.const as dogmaConst
REPAIRABLE_GROUPS = {invConst.groupCargoContainer,
 invConst.groupSecureCargoContainer,
 invConst.groupAuditLogSecureContainer,
 invConst.groupFreightContainer,
 invConst.groupTool}
REPAIRABLE_CATEGORIES = {invConst.categoryDeployable,
 invConst.categoryShip,
 invConst.categoryDrone,
 invConst.categoryStarbase,
 invConst.categoryModule,
 invConst.categoryStructureModule}
STATION_REPAIR_COST_MULTIPLIER = 0.1
QUOTE_ROWSET_HEADER = ['itemID',
 'typeID',
 'groupID',
 'damage',
 'maxHealth',
 'repairable',
 'costToRepairOneUnitOfDamage']
REPAIR_ROWSET_HEADER = ['itemID',
 'amountOfStructureToRepair',
 'amountOfArmorToRepair',
 'categoryID',
 'typeID',
 'actualCost']

def IsRepairable(item):
    if not item.singleton:
        return False
    if item.groupID in REPAIRABLE_GROUPS:
        return True
    if item.categoryID in REPAIRABLE_CATEGORIES:
        return True
    return False


def IsModuleDamaged(itemID, dogmaLM):
    if dogmaLM.ItemHasAttribute(itemID, dogmaConst.attributeDamage):
        structuralDamage = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeDamage)
        if structuralDamage > 0:
            return True
    return False


def IsModuleBurntOut(itemID, dogmaLM):
    if dogmaLM.ItemHasAttribute(itemID, dogmaConst.attributeDamage) and dogmaLM.ItemHasAttribute(itemID, dogmaConst.attributeHp):
        moduleHp = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeHp)
        moduleDamage = dogmaLM.GetAttributeValue(itemID, dogmaConst.attributeDamage)
        if moduleHp and moduleHp <= moduleDamage:
            return True
    return False
