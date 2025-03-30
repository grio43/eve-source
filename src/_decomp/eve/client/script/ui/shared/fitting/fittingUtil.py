#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingUtil.py
import dogma.data as dogma_data
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.mathCommon import FloatCloseEnough
from contextlib2 import contextmanager
from eve.client.script.environment import invControllers as invCtrl
from eve.common.script.sys.eveCfg import GetActiveShip
import evetypes
from inventorycommon.util import IsShipFittingFlag, IsFittingModule, IsSubsystemFlagVisible, IsModularShip
from localization import GetByLabel
from shipfitting.fittingDogmaLocationUtil import GetAlignTimeFromAgilityAndMass
from utillib import KeyVal
import inventorycommon.const as invConst
import dogma.const as dogmaConst
import carbonui.const as uiconst
import blue
import collections
from carbonui.uicore import uicore
FONTCOLOR_DEFAULT2 = 3238002687L
PASSIVESHIELDRECHARGE = 0
SHIELDBOOSTRATEACTIVE = 1
ARMORREPAIRRATEACTIVE = 2
HULLREPAIRRATEACTIVE = 3
PANEL_WIDTH_MIN = 280
PANEL_WIDTH_DEFAULT = 400
PANEL_WIDTH_MAX = 600
PANEL_WIDTH_RIGHT = PANEL_WIDTH_MIN
FTTING_PANEL_SETTING_LEFT_WIDTH = 'fitting_leftpanelwidth'
FITKEYS = ('Hi', 'Med', 'Lo')
NUM_SUBSYSTEM_SLOTS = 5
GHOST_FITTABLE_CATEGORIES = (const.categoryModule,
 const.categorySubSystem,
 const.categoryStructureModule,
 const.categoryDrone,
 const.categoryFighter,
 const.categoryCharge)
CLOSE_ENOUGH_TOLERANCE = 1e-07

def GetTypeAttributesByID(typeID):
    if not typeID:
        return {}
    return {attribute.attributeID:attribute.value for attribute in dogma_data.get_type_attributes(typeID)}


def GetAlignTimeForShip(dogmaLocation):
    shipID = dogmaLocation.GetCurrentShipID()
    agility = GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, const.attributeAgility)
    mass = GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, const.attributeMass)
    return GetAlignTimeFromAgilityAndMass(agility, mass)


def GetShipAttributeWithDogmaLocation(dogmaLocation, shipID, attributeID):
    if session.shipid == shipID:
        ship = sm.GetService('godma').GetItem(shipID)
        attributeName = dogma_data.get_attribute_name(attributeID)
        return getattr(ship, attributeName)
    else:
        return dogmaLocation.GetAttributeValue(shipID, attributeID)


def GetSensorStrengthAttribute(dogmaLocation, shipID):
    if session.shipid == shipID:
        return sm.GetService('godma').GetStateManager().GetSensorStrengthAttribute(shipID)
    else:
        maxAttributeID = None
        maxValue = None
        for attributeID in dogmaConst.sensorStrength:
            val = dogmaLocation.GetAttributeValue(shipID, attributeID)
            if val > maxValue:
                maxValue, maxAttributeID = val, attributeID

        return (maxAttributeID, maxValue)


def GetFightersInTubes(dogmaLocation):
    fightersInTubes = []
    for eachTubeFlagID in const.fighterTubeFlags:
        fighters = dogmaLocation.GetFightersForTube(eachTubeFlagID)
        if fighters:
            fightersInTubes.append(fighters)

    return fightersInTubes


def GetFighterNumByTypeIDsInTubes(dogmaLocation):
    fighterTypesInTubes = collections.defaultdict(int)
    for eachFighter in GetFightersInTubes(dogmaLocation):
        fighterTypesInTubes[eachFighter.typeID] += 1

    return fighterTypesInTubes


def GetFittingDragData():
    fittingSvc = sm.StartService('fittingSvc')
    fitting = KeyVal()
    fitting.shipTypeID, fitting.fitData, _ = fittingSvc.GetFittingDictForCurrentFittingWindowShip()
    fitting.fittingID = None
    fitting.description = ''
    fitting.name = cfg.evelocations.Get(GetActiveShip()).locationName
    fitting.ownerID = 0
    if fittingSvc.IsShipSimulated():
        fitting.name = sm.GetService('ghostFittingSvc').GetShipName()
    else:
        fitting.name = cfg.evelocations.Get(GetActiveShip()).locationName
    entry = KeyVal()
    entry.fitting = fitting
    entry.label = fitting.name
    entry.displayText = fitting.name
    entry.__guid__ = 'listentry.FittingEntry'
    return [entry]


def GetScaleFactor():
    dw = uicore.desktop.width
    minWidth = 1400
    return min(1.0, max(0.75, dw / float(minWidth)))


def GetBaseShapeSize():
    return int(640 * GetScaleFactor())


def GetBaseShapeYOffset():
    return -6


def IsCharge(typeID):
    return evetypes.GetCategoryID(typeID) in (const.categoryCharge, const.groupFrequencyCrystal)


def GetPowerType(flagID):
    if flagID in invConst.loSlotFlags:
        return dogmaConst.effectLoPower
    if flagID in invConst.medSlotFlags:
        return dogmaConst.effectMedPower
    if flagID in invConst.hiSlotFlags:
        return dogmaConst.effectHiPower
    if IsSubsystemFlagVisible(flagID):
        return dogmaConst.effectSubSystem
    if flagID in invConst.rigSlotFlags:
        return dogmaConst.effectRigSlot
    if flagID in invConst.serviceSlotFlags:
        return dogmaConst.effectServiceSlot


def TryFit(invItems, shipID = None):
    if not shipID:
        shipID = GetActiveShip()
        if not shipID:
            return
    godma = sm.services['godma']
    invCache = sm.GetService('invCache')
    shipInv = invCache.GetInventoryFromId(shipID, locationID=session.stationid)
    shipTypeID = shipInv.typeID
    godmaSM = godma.GetStateManager()
    useRigs = None
    charges = set()
    drones = []
    subSystemGroupIDs = set()
    for invItem in invItems[:]:
        if IsFittingModule(invItem.categoryID):
            moduleEffects = dogma_data.get_type_effects(invItem.typeID)
            for mEff in moduleEffects:
                if mEff.effectID == const.effectRigSlot:
                    if useRigs is None:
                        useRigs = True if RigFittingCheck(invItem, shipTypeID) else False
                    if not useRigs:
                        invItems.remove(invItem)
                        invCache.UnlockItem(invItem.itemID)
                        break

        if invItem.categoryID == const.categorySubSystem:
            if invItem.groupID in subSystemGroupIDs:
                invItems.remove(invItem)
            else:
                subSystemGroupIDs.add(invItem.groupID)
        elif invItem.categoryID == const.categoryCharge:
            charges.add(invItem)
            invItems.remove(invItem)
        elif invItem.categoryID == const.categoryDrone:
            drones.append(invItem)
            invItems.remove(invItem)

    if len(invItems) > 0:
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        shipInv.moniker.MultiAdd([ invItem.itemID for invItem in invItems ], invItems[0].locationID, flag=const.flagAutoFit)
    if charges:
        shipStuff = shipInv.List()
        shipStuff.sort(key=lambda r: (r.flagID, isinstance(r.itemID, tuple)))
        loadedSlots = set()
    if drones:
        invCtrl.ShipDroneBay(shipID or GetActiveShip()).AddItems(drones)
    dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
    shipDogmaItem = dogmaLocation.dogmaItems.get(shipID, None)
    loadedSomething = False
    for DBRowInvItem in charges:
        invItem = KeyVal(DBRowInvItem)
        chargeDgmType = godmaSM.GetType(invItem.typeID)
        isCrystalOrScript = invItem.groupID in cfg.GetCrystalGroups()
        for row in shipStuff:
            if row in loadedSlots:
                continue
            if not IsShipFittingFlag(row.flagID):
                continue
            if dogmaLocation.IsInWeaponBank(row.locationID, row.itemID) and dogmaLocation.IsModuleSlave(row.itemID, row.locationID):
                continue
            if row.categoryID == const.categoryCharge:
                continue
            moduleDgmType = godmaSM.GetType(row.typeID)
            desiredSize = getattr(moduleDgmType, 'chargeSize', None)
            for x in xrange(1, 5):
                chargeGroup = getattr(moduleDgmType, 'chargeGroup%d' % x, False)
                if not chargeGroup:
                    continue
                if chargeDgmType.groupID != chargeGroup:
                    continue
                if desiredSize and getattr(chargeDgmType, 'chargeSize', -1) != desiredSize:
                    continue
                for i, squatter in enumerate([ i for i in shipStuff if i.flagID == row.flagID ]):
                    if isCrystalOrScript and i > 0:
                        break
                    if shipDogmaItem is None:
                        continue
                    subLocation = dogmaLocation.GetSubLocation(shipID, squatter.flagID)
                    if subLocation is None:
                        continue
                    chargeVolume = chargeDgmType.volume * dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                    if godmaSM.GetType(row.typeID).capacity <= chargeVolume:
                        break
                else:
                    moduleCapacity = godmaSM.GetType(row.typeID).capacity
                    numCharges = moduleCapacity / chargeDgmType.volume
                    subLocation = dogmaLocation.GetSubLocation(shipID, row.flagID)
                    if subLocation:
                        numCharges -= dogmaLocation.GetAttributeValue(subLocation, const.attributeQuantity)
                    dogmaLocation.LoadAmmo(shipID, row.itemID, invItem.itemID, invItem.locationID)
                    loadedSomething = True
                    invItem.stacksize -= numCharges
                    loadedSlots.add(row)
                    blue.pyos.synchro.SleepWallclock(100)
                    break

            else:
                continue

            if invItem.stacksize <= 0:
                break
        else:
            if not loadedSomething:
                uicore.Message('NoSuitableModules')


def CanFitFromSourceLocation(dragNodes):
    from eve.client.script.ui.shared.inventory.invContainers import AssetSafetyContainer, AssetSafetyCorpContainer
    if not isinstance(dragNodes, collections.Iterable):
        dragNodes = [dragNodes]
    for node in dragNodes:
        container = getattr(node, 'container', None)
        if isinstance(container, (AssetSafetyContainer, AssetSafetyCorpContainer)):
            return False

    return True


def RigFittingCheck(invItem, shipTypeID):
    if IsModularShip(shipTypeID):
        return True
    moduleEffects = dogma_data.get_type_effects(invItem.typeID)
    for mEff in moduleEffects:
        if mEff.effectID == const.effectRigSlot:
            if uicore.Message('RigFittingInfo', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                return False

    return True


def IsSurveyProbeLauncherFitted():
    dogmaLoc = sm.GetService('clientDogmaIM').GetDogmaLocation()
    fittedModules = dogmaLoc.SafeGetDogmaItem(session.shipid).GetFittedItems()
    for module in fittedModules.values():
        if module.groupID == invConst.groupSurveyProbeLauncher:
            return True

    return False


class ModifiedAttribute(object):

    def __init__(self, value, multiplier = 1.0, addition = 0.0, higherIsBetter = True, oldValue = None, attributeID = None):
        self.baseValue = value
        self.multiplier = multiplier
        self.addition = addition
        self.higherIsBetter = higherIsBetter
        self.oldValue = oldValue
        self.attributeID = attributeID

    @property
    def value(self):
        return (self.baseValue + self.addition) * self.multiplier

    @value.setter
    def value(self, value):
        self.baseValue = value

    @property
    def diff(self):
        return self.value - self.baseValue

    @property
    def diffNormalized(self):
        if not self.higherIsBetter:
            return -self.diff
        else:
            return self.diff

    @property
    def isBetterThanBefore(self):
        if self.oldValue is None or FloatCloseEnough(self.value, self.oldValue, CLOSE_ENOUGH_TOLERANCE) or self.higherIsBetter is None:
            return
        else:
            currentIsHigher = self.value > self.oldValue
            if self.higherIsBetter:
                return currentIsHigher
            return not currentIsHigher

    @property
    def isSame(self):
        return FloatCloseEnough(self.value, self.baseValue)


def GetDefensiveLayersInfo(controller):
    shieldResistanceInfo = {'em': controller.GetShieldEmDamageResonance(),
     'explosive': controller.GetShieldExplosiveDamageResonance(),
     'kinetic': controller.GetShieldKineticDamageResonance(),
     'thermal': controller.GetShieldThermalDamageResonance()}
    armorResistanceInfo = {'em': controller.GetArmorEmDamageResonance(),
     'explosive': controller.GetArmorExplosiveDamageResonance(),
     'kinetic': controller.GetArmorKineticDamageResonance(),
     'thermal': controller.GetArmorThermalDamageResonance()}
    structureResistanceInfo = {'em': controller.GetStructureEmDamageResonance(),
     'explosive': controller.GetStructureExplosiveDamageResonance(),
     'kinetic': controller.GetStructureKineticDamageResonance(),
     'thermal': controller.GetStructureThermalDamageResonance()}
    allLayersInfo = {'shield': KeyVal(resistances=shieldResistanceInfo, hpInfo=controller.GetShieldHp(), isRechargable=True),
     'armor': KeyVal(resistances=armorResistanceInfo, hpInfo=controller.GetArmorHp(), isRechargable=False),
     'structure': KeyVal(resistances=structureResistanceInfo, hpInfo=controller.GetStructureHp(), isRechargable=False)}
    return allLayersInfo


def GetEffectiveHp(controller):
    effectiveHp = 0.0
    allDefensiveLayersInfo = GetDefensiveLayersInfo(controller)
    for whatLayer, layerInfo in allDefensiveLayersInfo.iteritems():
        layerResistancesInfo = layerInfo.resistances
        total = sum((valueInfo.value for valueInfo in layerResistancesInfo.itervalues()))
        avgResistance = total / len(layerResistancesInfo)
        layerHp = layerInfo.hpInfo.value
        if avgResistance:
            effectiveHpForLayer = layerHp / avgResistance
            effectiveHp += effectiveHpForLayer

    return effectiveHp


def GetTypeIDForController(itemID):
    if isinstance(itemID, basestring):
        typeID = int(itemID.split('_')[1])
        return typeID
    item = sm.GetService('godma').GetItem(itemID)
    if item:
        return item.typeID


def CanDeleteFit(ownerID):
    if ownerID == session.charid:
        return True
    if not session.corprole & const.corpRoleFittingManager:
        return False
    if ownerID == session.corpid:
        return True
    if session.allianceid and ownerID == session.allianceid:
        if sm.GetService('alliance').GetAlliance().executorCorpID == session.corpid:
            return True
    return False


def GetDeletableNodes(nodes):
    canDelete = []
    for eachNode in nodes:
        if CanDeleteFit(eachNode.ownerID):
            canDelete.append(eachNode)

    return canDelete


def DeleteFittings(selectedNodes):
    fittingSvc = sm.GetService('fittingSvc')
    if len(selectedNodes) > 1:
        fittingsByOwnerID = collections.defaultdict(list)
        for node in selectedNodes:
            fittingsByOwnerID[node.ownerID].append(node.fittingID)

        if len(fittingsByOwnerID) == 1:
            ownerText = cfg.eveowners.Get(fittingsByOwnerID.keys()[0]).name
            msgName = 'DeleteFittingsManyOneOwner'
        else:
            ownerText = _GetDeleteWarningText(fittingsByOwnerID)
            msgName = 'DeleteFittingsMany'
        if eve.Message(msgName, {'ownerText': ownerText,
         'numFittings': len(selectedNodes)}, uiconst.YESNO) != uiconst.ID_YES:
            return False
        fittingSvc.DeleteManyFittings(fittingsByOwnerID)
    else:
        node = selectedNodes[0]
        if eve.Message('DeleteFitting', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return False
        fittingID = node.fittingID
        ownerID = node.ownerID
        fittingSvc.DeleteFitting(ownerID, fittingID)
    return True


def _GetDeleteWarningText(fittingsByOwnerID):
    textList = []
    myOwners = [session.charid, session.corpid, session.allianceid]
    for ownerID in myOwners:
        if not ownerID:
            continue
        fittingIDs = fittingsByOwnerID.get(ownerID, [])
        if fittingIDs:
            ownerName = cfg.eveowners.Get(ownerID).name
            t = GetByLabel('UI/Fitting/FittingWindow/OwnerAndFittingNum', ownerName=ownerName, numFittings=len(fittingIDs))
            t = u'  \u2022 ' + t
            textList.append(t)

    text = '<br>'.join(textList)
    return text


@contextmanager
def EatSignalChangingErrors(errorMsg):
    try:
        yield
    except Exception as e:
        import log
        log.LogError('Failed at changing signal connections, %s e = %s ' % (errorMsg, e))
