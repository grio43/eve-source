#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\environment\invControllers.py
import sys
import utillib
from brennivin.itertoolsext import Bundle
from collections import defaultdict
from corporation.client.goals.goalsController import CorpGoalsController
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.common.lib import appConst as const
from eve.common.script.mgt.fighterConst import TUBE_STATE_READY
from eve.common.script.sys import eveCfg, idCheckers
from eve.common.script.sys.eveCfg import InSpace
from eve.common.script.util import inventoryFlagsCommon
from eve.common.script.util.inventoryFlagsCommon import inventoryFlagData
from inventorycommon.util import GetItemVolume, IsFittingFlag, IsFittingModule, IsStructureServiceFlag
from inventoryrestrictions import is_tradable, can_be_added_to_container
from inventoryrestrictions import ItemCannotBeTraded, ItemCannotBeAddedToContainer
from eve.client.script.ui.util import uix
import carbonui.const as uiconst
import log
import localization
import telemetry
import evetypes
import inventorycommon.typeHelpers
import inventorycommon.const as invConst
from inventoryrestrictions import can_be_unfitted, ItemCannotBeUnfitted
from eve.client.script.ui.plex.textures import PLEX_128_GRADIENT_YELLOW
from eve.client.script.ui.util import utilWindows
from localization import GetByLabel
from resourcewars.client.audioevents import on_not_enough_cargo_space
from spacecomponents.common.componentConst import CARGO_BAY, UNDER_CONSTRUCTION
from spacecomponents.common.data import get_space_component_for_type
from spacecomponents.common.helper import HasCargoBayComponent, HasUnderConstructionComponent
from vgs.common.listeners import PlexDepositListener
from carbon.common.script.sys.row import Row
from carbonui.uicore import uicore
from eveexceptions import UserError
from eveservices.menu import GetMenuService
LOOT_GROUPS = (const.groupWreck,
 const.groupCargoContainer,
 const.groupFreightContainer,
 const.groupSpawnContainer,
 const.groupSpewContainer,
 const.groupDeadspaceOverseersBelongings,
 const.groupMissionContainer,
 const.groupAutoLooter,
 const.groupMobileHomes)
LOOT_GROUPS_NOCLOSE = (const.groupAutoLooter, const.groupMobileHomes)
ZERO_CAPACITY = Row(['capacity', 'used'], [0, 0.0])

def GetNameForFlag(flagID):
    return localization.GetByLabel(inventoryFlagData[flagID]['name'])


class BaseInvContainer(object):
    __guid__ = 'invCtrl.BaseInvContainer'
    name = ''
    iconName = 'res:/UI/Texture/Icons/3_64_13.png'
    locationFlag = None
    hasCapacity = False
    oneWay = False
    viewOnly = False
    scope = None
    isLockable = True
    isMovable = True
    filtersEnabled = True
    typeID = None
    acceptsDrops = True
    isCompact = False

    def __init__(self, itemID = None, typeID = None):
        self.itemID = itemID
        self.typeID = typeID
        self.invID = (self.__class__.__name__, itemID)

    def GetInvID(self):
        return self.invID

    def GetInventoryLocationID(self):
        inventoryLocationID, _ = self.invID
        return inventoryLocationID

    def GetName(self):
        return self.name

    def GetNameWithLocation(self):
        return localization.GetByLabel('UI/Inventory/BayAndLocationName', bayName=self.GetName(), locationName=cfg.evelocations.Get(self.itemID).name)

    def GetIconName(self):
        return self.iconName

    @telemetry.ZONE_METHOD
    def GetItems(self):
        try:
            return filter(self.IsItemHere, self._GetItems())
        except RuntimeError as e:
            if e[0] == 'CharacterNotAtStation':
                return []
            raise

    @telemetry.ZONE_METHOD
    def _GetItems(self):
        if self.locationFlag:
            return self._GetInvCacheContainer().List(flag=self.locationFlag)
        else:
            return self._GetInvCacheContainer().List()

    def GetItemsByType(self, typeID):
        return [ item for item in self.GetItems() if item.typeID == typeID ]

    def GetItem(self, itemID):
        for item in self.GetItems():
            if item.itemID == itemID:
                return item

    def GetScope(self):
        return self.scope

    def GetMenu(self):
        return GetMenuService().InvItemMenu(self.GetInventoryItem())

    def _GetInvCacheContainer(self):
        invCache = sm.GetService('invCache')
        return invCache.GetInventoryFromId(self.itemID)

    def GetInventoryItem(self):
        item = sm.GetService('invCache').GetParentItemFromItemID(self.itemID)
        if not item:
            item = self._GetInvCacheContainer().GetItem()
        return item

    def GetTypeID(self):
        if self.typeID is None:
            self.typeID = self.GetInventoryItem().typeID
        return self.typeID

    def IsItemHere(self, item):
        raise NotImplementedError('IsItemHere must be implemented')

    def IsMovable(self):
        return self.isMovable

    def IsItemHereVolume(self, item):
        return self.IsItemHere(item)

    def IsInRange(self):
        return True

    def CheckCanQuery(self):
        return True

    def CheckCanTake(self):
        return True

    def IsPrimed(self):
        return sm.GetService('invCache').IsInventoryPrimedAndListed(self.itemID)

    def HasEnoughSpaceForItems(self, items):
        volume = 0.0
        for item in items:
            volume += GetItemVolume(item)

        cap = self.GetCapacity()
        remainingVolume = cap.capacity - cap.used
        return volume <= remainingVolume

    def DoesAcceptItem(self, item):
        if self.locationFlag and inventoryFlagsCommon.ShouldAllowAdd(self.locationFlag, item.categoryID, item.groupID, item.typeID) is not None:
            return False
        return True

    def OnItemsViewed(self):
        pass

    def AddFightersFromTube(self, fighters):
        fighterSvc = sm.GetService('fighters')
        for fighter in fighters:
            if fighter.squadronState == TUBE_STATE_READY:
                fighterSvc.UnloadTubeToFighterBay(fighter.tubeFlagID)

    def __AddItem(self, item, sourceLocationID, quantity):
        itemID = item.itemID
        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        stateMgr = sm.StartService('godma').GetStateManager()
        dividing = quantity != item.stacksize
        if self.IsItemHere(item):
            if not dividing:
                return
        else:
            if not self.CheckAndConfirmOneWayMove():
                return
            if not self.CheckCanAdd(item.typeID, quantity):
                return
        if self.locationFlag:
            item = stateMgr.GetItem(itemID)
            if item and self.locationFlag in inventoryFlagData and IsFittingFlag(item.flagID):
                if item.categoryID == const.categoryCharge:
                    return dogmaLocation.UnloadAmmoToContainer(item.locationID, item, (self.itemID, self.GetOwnerID(), self.locationFlag), quantity)
                if IsFittingModule(item.categoryID):
                    return stateMgr.UnloadModuleToContainer(item.locationID, item.itemID, self._GetContainerArgs(), self.locationFlag)
            else:
                return self._GetInvCacheContainer().Add(itemID, sourceLocationID, qty=quantity, flag=self.locationFlag)
        else:
            typeID = self.GetTypeID()
            if typeID and evetypes.GetGroupID(typeID) == const.groupAuditLogSecureContainer:
                thisContainer = sm.GetService('invCache').GetInventoryFromId(self.itemID)
                thisContainerItem = thisContainer.GetItem()
                rolesAreNeeded = thisContainerItem is None or not idCheckers.IsStation(thisContainerItem.locationID) and thisContainerItem.locationID != session.shipid
                if rolesAreNeeded:
                    config = thisContainer.ALSCConfigGet()
                    lockFlag = const.flagLocked if bool(config & const.ALSCLockAddedItems) else const.flagUnlocked
                    if lockFlag == const.flagLocked and session.corprole & const.corpRoleEquipmentConfig == 0:
                        if eve.Message('ConfirmAddLockedItemToAuditContainer', {}, uiconst.OKCANCEL) != uiconst.ID_OK:
                            return
            return self._GetInvCacheContainer().Add(itemID, sourceLocationID, qty=quantity, flag=self.locationFlag)

    def _AddItem(self, item, forceQuantity = False, sourceLocation = None):
        locationID = session.locationid
        maxQty = None
        for i in xrange(2):
            try:
                if locationID != session.locationid:
                    return
                itemQuantity = item.stacksize
                if itemQuantity == 1:
                    quantity = 1
                elif uicore.uilib.Key(uiconst.VK_SHIFT) or forceQuantity:
                    quantity = self.PromptUserForQuantity(item, itemQuantity, sourceLocation, maxQty)
                else:
                    quantity = itemQuantity
                if not item.itemID or not quantity:
                    return
                if locationID != session.locationid:
                    return
                if sourceLocation is None:
                    sourceLocation = item.locationID
                return self.__AddItem(item, sourceLocation, quantity)
            except UserError as what:
                msgKey = what.args[0]
                if msgKey in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload', 'NotEnoughDroneBaySpace', 'NotEnoughDroneBaySpaceOverload', 'NoSpaceForThat', 'NoSpaceForThatOverload', 'NotEnoughChargeSpace', 'NotEnoughSpecialBaySpace', 'NotEnoughSpecialBaySpaceOverload', 'NotEnoughSpace', 'NotEnoughFighterBaySpace'):
                    try:
                        cap = self.GetCapacity()
                    except UserError:
                        raise what

                    free = cap.capacity - cap.used
                    if free < 0:
                        raise
                    if item.typeID == const.typePlasticWrap:
                        volume = sm.GetService('invCache').GetInventoryFromId(item.itemID).GetCapacity().used
                    else:
                        volume = GetItemVolume(item, 1)
                    maxQty = self._CalculateMaxQuantity(free, item, volume)
                    if maxQty <= 0:
                        if volume < 0.01:
                            req = 0.01
                        else:
                            req = volume
                        eve.Message('NotEnoughCargoSpaceFor1Unit', {'type': item.typeID,
                         'free': free,
                         'required': req})
                        on_not_enough_cargo_space(self.typeID, item)
                        return
                    if self._DBLessLimitationsCheck(msgKey, item):
                        return
                    forceQuantity = 1
                elif msgKey == 'CannotAddToQtyLimit':
                    maxQty = what.dict.get('maxToAdd', None)
                    if maxQty <= 0:
                        raise
                    forceQuantity = 1
                else:
                    raise
                sys.exc_clear()

    def _CalculateMaxQuantity(self, free, item, volume):
        numberOfItemsWeHaveRoomFor = int(round(free / (volume or 1), 7))
        maxQty = min(item.stacksize, numberOfItemsWeHaveRoomFor)
        return maxQty

    def PromptUserForQuantity(self, item, itemQuantity, sourceLocation = None, maxQtyAllowed = None):
        if self.locationFlag is not None and item.flagID != self.locationFlag or item.locationID != getattr(self._GetInvCacheContainer(), 'itemID', None):
            maxQtyFromAvailableSpace = None
            if self.hasCapacity:
                cap = self.GetCapacity()
                capacity = cap.capacity - cap.used
                itemvolume = GetItemVolume(item, 1) or 1
                maxQtyFromAvailableSpace = int(capacity / itemvolume + 1e-07)
            maxQty = min(filter(None, [itemQuantity, maxQtyAllowed, maxQtyFromAvailableSpace]))
            if maxQty == itemQuantity:
                errmsg = localization.GetByLabel('UI/Common/NoMoreUnits')
            else:
                errmsg = localization.GetByLabel('UI/Common/NoRoomForMore')
            ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
        else:
            ret = uix.QtyPopup(itemQuantity, 1, 1, None, localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack'))
        if item.locationID != session.stationid:
            if not sm.GetService('invCache').IsInventoryPrimedAndListed(item.locationID):
                log.LogError('Item disappeared before we could add it', item)
                return
        if ret is not None:
            return ret['qty']

    def MultiMerge(self, data, mergeSourceID):
        mergeItem = data[0][3]
        if mergeItem.locationID != self.itemID or mergeItem.flagID != self.locationFlag:
            if not self.CheckAndConfirmOneWayMove():
                return
            if not self.CheckCanAdd(typeID=mergeItem.typeID, quantity=data[0][2]):
                return
        try:
            self._GetInvCacheContainer().MultiMerge([ (d[0], d[1], d[2]) for d in data ], mergeSourceID)
            return True
        except UserError as what:
            if len(data) == 1 and what.args[0] in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload', 'NotEnoughDroneBaySpace', 'NotEnoughDroneBaySpaceOverload', 'NoSpaceForThat', 'NoSpaceForThatOverload', 'NotEnoughChargeSpace', 'NotEnoughSpecialBaySpace', 'NotEnoughFighterBaySpace'):
                cap = self.GetCapacity()
                free = cap.capacity - cap.used
                if free < 0:
                    raise
                item = data[0][3]
                if item.typeID == const.typePlasticWrap:
                    volume = sm.GetService('invCache').GetInventoryFromId(item.itemID).GetCapacity().used
                else:
                    volume = GetItemVolume(item, 1)
                maxQty = self._CalculateMaxQuantity(free, item, volume)
                if maxQty <= 0:
                    if volume < 0.01:
                        req = 0.01
                    else:
                        req = volume
                    eve.Message('NotEnoughCargoSpaceFor1Unit', {'type': item.typeID,
                     'free': free,
                     'required': req})
                    return
                if self._DBLessLimitationsCheck(what.args[0], item):
                    return
                if maxQty == item.stacksize:
                    errmsg = localization.GetByLabel('UI/Common/NoMoreUnits')
                else:
                    errmsg = localization.GetByLabel('UI/Common/NoRoomForMore')
                ret = uix.QtyPopup(int(maxQty), 0, int(maxQty), errmsg)
                if ret is None:
                    quantity = None
                else:
                    quantity = ret['qty']
                if quantity:
                    self._GetInvCacheContainer().MultiMerge([(data[0][0], data[0][1], quantity)], mergeSourceID)
                    return True
            else:
                raise
            sys.exc_clear()

    def StackAll(self, securityCode = None):
        if not self.CheckAndConfirmOneWayMove():
            return
        if self.locationFlag:
            retval = self._GetInvCacheContainer().StackAll(self.locationFlag)
            return retval
        try:
            if securityCode is None:
                retval = self._GetInvCacheContainer().StackAll()
            else:
                retval = self._GetInvCacheContainer().StackAll(securityCode=securityCode)
            return retval
        except UserError as what:
            if what.args[0] == 'PermissionDenied':
                if securityCode:
                    caption = localization.GetByLabel('UI/Menusvc/IncorrectPassword')
                    label = localization.GetByLabel('UI/Menusvc/PleaseTryEnteringPasswordAgain')
                else:
                    caption = localization.GetByLabel('UI/Menusvc/PasswordRequired')
                    label = localization.GetByLabel('UI/Menusvc/PleaseEnterPassword')
                passw = utilWindows.NamePopup(caption=caption, label=label, setvalue='', icon=-1, modal=1, btns=None, maxLength=50, passwordChar='*')
                if passw == '':
                    raise UserError('IgnoreToTop')
                else:
                    retval = self.StackAll(securityCode=passw['name'])
                    return retval
            else:
                raise
            sys.exc_clear()

    def _DBLessLimitationsCheck(self, errorName, item):
        return False

    def GetCapacity(self):
        try:
            return self._GetInvCacheContainer().GetCapacity(self.locationFlag)
        except RuntimeError as e:
            if e[0] in ('CharacterNotAtStation', 'FakeItemNotFound'):
                return ZERO_CAPACITY
            raise

    def GetOwnerID(self):
        return self.GetInventoryItem().ownerID

    def _GetContainerArgs(self):
        return (self.itemID,)

    def _ValidateMove(self, items):
        forbiddenTypeIDs = set()
        for item in items:
            typeID = getattr(item, 'typeID', None)
            flagID = getattr(item, 'flagID', None)
            if all([typeID, flagID]) and flagID in invConst.fittingFlags and not can_be_unfitted(typeID):
                forbiddenTypeIDs.add(typeID)

        if forbiddenTypeIDs:
            raise ItemCannotBeUnfitted(type_ids=forbiddenTypeIDs)

    def OnDropData(self, nodes):
        if not self.acceptsDrops:
            return
        items = []
        fighters = []
        lockedNodes = [ node for node in nodes if getattr(node, 'locked', False) ]
        if lockedNodes:
            for node in lockedNodes:
                nodes.remove(node)

            uicore.Message('SomeLockedItemsNotMoved')
        for node in nodes:
            if self.CheckAndHandlePlexVaultItem(node):
                continue
            if getattr(node, '__guid__', None) in ('xtriui.ShipUIModule', 'xtriui.InvItem', 'listentry.InvItem', 'xtriui.FittingSlot'):
                items.append(node.item)
            from eve.client.script.ui.shared.inventory.treeData import TreeDataInv
            if isinstance(node, TreeDataInv) and node.invController.IsMovable():
                items.append(node.invController.GetInventoryItem())
            if getattr(node, '__guid__', None) == 'uicls.FightersHealthGauge':
                fighters.append(node)

        self._ValidateMove(items)
        if fighters:
            return self.AddFightersFromTube(fighters)
        return self.AddItems(items)

    def CheckAndHandlePlexVaultItem(self, node):
        isPlexVaultItem = hasattr(node, 'WithdrawPlex') and callable(node.WithdrawPlex)
        if not isPlexVaultItem:
            return False
        if not self.DoesAcceptItem(node.item):
            return False
        node.WithdrawPlex(self)
        return True

    def AddItems(self, items):
        if not self.CheckCanAddMultiple(items):
            return
        else:
            sourceLocation = items[0].locationID
            if self.itemID != sourceLocation and not sm.GetService('crimewatchSvc').CheckCanTakeItems(sourceLocation):
                sm.GetService('crimewatchSvc').SafetyActivated(const.shipSafetyLevelPartial)
                container = sm.GetService('invCache').GetInventoryFromId(sourceLocation)
                raise UserError('LootTheftDeniedSafetyPreventsSuspect', {'containerName': (const.UE_TYPEID, container.typeID)})
            if session.shipid and self.itemID == session.shipid:
                if self.itemID != sourceLocation and not sm.GetService('consider').ConfirmTakeIllicitGoods(items):
                    return
            if not sm.GetService('invCache').AcceptPossibleRemovalTax(items):
                return
            if len(items) == 1:
                item = items[0]
                if hasattr(item, 'flagID') and IsFittingFlag(item.flagID):
                    if item.locationID == eveCfg.GetActiveShip():
                        if not self.CheckAndConfirmOneWayMove():
                            return
                        itemKey = item.itemID
                        locationID = item.locationID
                        dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
                        containerArgs = self._GetContainerArgs()
                        if IsFittingModule(item.categoryID):
                            return dogmaLocation.UnloadModuleToContainer(locationID, itemKey, containerArgs, self.locationFlag)
                        if item.categoryID == const.categoryCharge:
                            ownerID = session.charid if self.locationFlag == const.flagHangar else self.GetOwnerID()
                            return dogmaLocation.UnloadAmmoToContainer(locationID, item, (containerArgs[0], ownerID, self.locationFlag))
                        if IsStructureServiceFlag(item.flagID):
                            sm.GetService('structureControl').CheckCanDisableServiceModule(item)
                            from eve.client.script.util.eveMisc import GetRemoveServiceConfirmationQuestion
                            questionPath, params = GetRemoveServiceConfirmationQuestion(item.typeID)
                            ret = eve.Message(questionPath, params=params, buttons=uiconst.YESNO)
                            if ret != uiconst.ID_YES:
                                return
                ret = self._AddItem(item, sourceLocation=sourceLocation)
                if ret:
                    sm.ScatterEvent('OnClientEvent_MoveFromCargoToHangar', sourceLocation, self.itemID, self.locationFlag)
                return ret
            if not self.CheckAndConfirmOneWayMove():
                return
            items.sort(key=lambda item: evetypes.GetVolume(item.typeID) * item.stacksize)
            itemIDs = [ node.itemID for node in items ]
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            masters = dogmaLocation.GetAllSlaveModulesByMasterModule(sourceLocation)
            if masters:
                inBank = 0
                for itemID in itemIDs:
                    if dogmaLocation.IsInWeaponBank(sourceLocation, itemID):
                        inBank = 1
                        break

                if inBank:
                    ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/Common/Confirm'),
                     'question': localization.GetByLabel('UI/Inventory/WeaponLinkUnfitMany')}, uiconst.YESNO)
                    if ret != uiconst.ID_YES:
                        return
            for item in items:
                if item.categoryID == const.categoryCharge and IsFittingFlag(item.flagID):
                    log.LogInfo('A module with a db item charge dropped from ship fitting into some container. Cannot use multimove, must remove charge first.')
                    ret = [self._AddItem(item)]
                    items.remove(item)
                    for item in items:
                        ret.append(self._AddItem(item))

                    return ret

            invCacheCont = self._GetInvCacheContainer()
            if self.locationFlag:
                ret = invCacheCont.MultiAdd(itemIDs, sourceLocation, flag=self.locationFlag)
            else:
                ret = invCacheCont.MultiAdd(itemIDs, sourceLocation, flag=const.flagNone)
            if ret:
                sm.ScatterEvent('OnClientEvent_MoveFromCargoToHangar', sourceLocation, self.itemID, self.locationFlag)
            return ret

    def SetCompactMode(self, isCompact):
        self.isCompact = isCompact

    def CheckAndConfirmOneWayMove(self):
        if self.oneWay:
            return self.PromptOneWayMove()
        return True

    def CheckCanAdd(self, typeID, quantity):
        return True

    def CheckCanAddMultiple(self, items):
        if len(items) > 1:
            items = filter(self.DoesAcceptItem, items)
            quantityByType = defaultdict(int)
            for item in items:
                quantityByType[item.typeID] += item.stacksize

            for typeID, quantity in quantityByType.items():
                if quantity > 0:
                    if not self.CheckCanAdd(typeID, quantity):
                        return False

        if not items:
            return False
        return True

    def PromptOneWayMove(self):
        return uicore.Message('ConfirmOneWayItemMove', {}, uiconst.OKCANCEL) == uiconst.ID_OK

    def GetSpecialActions(self):
        return []


class ShipCargo(BaseInvContainer):
    __guid__ = 'invCtrl.ShipCargo'
    hasCapacity = True
    locationFlag = const.flagCargo

    def __init__(self, itemID = None, typeID = None):
        self.itemID = itemID or eveCfg.GetActiveShip()
        self.invID = (self.__class__.__name__, self.itemID)
        self.name = localization.GetByLabel('UI/Common/CargoHold')

    def GetMenu(self):
        if self.itemID == session.shipid and InSpace():
            return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.GetTypeID())
        else:
            return BaseInvContainer.GetMenu(self)

    def GetIconName(self, highliteIfActive = False):
        if highliteIfActive and self.itemID == eveCfg.GetActiveShip():
            return 'res:/UI/Texture/Icons/1337_64_11.png'
        else:
            return 'res:/ui/Texture/WindowIcons/ships.png'

    def GetScope(self):
        if self.itemID == eveCfg.GetActiveShip():
            return uiconst.SCOPE_INGAME
        return uiconst.SCOPE_DOCKED

    def GetName(self):
        return cfg.evelocations.Get(self.itemID).name

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID, locationID=session.stationid)

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.flagID == self.locationFlag


class BaseShipBay(BaseInvContainer):
    __guid__ = 'invCtrl.BaseShipBay'
    hasCapacity = True
    isMovable = False

    def __init__(self, itemID = None, typeID = None):
        super(BaseShipBay, self).__init__(itemID, typeID)
        self.itemID = itemID or eveCfg.GetActiveShip()

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.flagID == self.locationFlag

    def GetName(self):
        return GetNameForFlag(self.locationFlag)

    def GetScope(self):
        if self.itemID == eveCfg.GetActiveShip():
            return uiconst.SCOPE_INGAME
        else:
            return uiconst.SCOPE_DOCKED


class ShipDroneBay(BaseShipBay):
    __guid__ = 'invCtrl.ShipDroneBay'
    iconName = 'res:/UI/Texture/WindowIcons/dronebay.png'
    locationFlag = const.flagDroneBay
    hasCapacity = True
    scope = uiconst.SCOPE_DOCKED


class ShipFighterBay(BaseShipBay):
    __guid__ = 'invCtrl.ShipFighterBay'
    iconName = 'res:/UI/Texture/WindowIcons/dronebay.png'
    locationFlag = const.flagFighterBay
    hasCapacity = True
    scope = uiconst.SCOPE_DOCKED


class ShipFrigateEscapeBay(BaseShipBay):
    __guid__ = 'invCtrl.ShipFrigateEscapeBay'
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'
    locationFlag = const.flagFrigateEscapeBay
    scope = uiconst.SCOPE_DOCKED


class ShipFuelBay(BaseShipBay):
    __guid__ = 'invCtrl.ShipFuelBay'
    locationFlag = const.flagSpecializedFuelBay
    iconName = 'res:/UI/Texture/WindowIcons/fuelbay.png'


class ShipGeneralMiningHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipGeneralMiningHold'
    locationFlag = const.flagGeneralMiningHold
    iconName = 'res:/UI/Texture/WindowIcons/orehold.png'


class ShipAsteroidHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipAsteroidHold'
    locationFlag = const.flagSpecialAsteroidHold
    iconName = 'res:/UI/Texture/WindowIcons/orehold.png'


class ShipIceHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipIceHold'
    locationFlag = const.flagSpecializedIceHold
    iconName = 'res:/UI/Texture/WindowIcons/icehold.png'


class ShipGasHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipGasHold'
    locationFlag = const.flagSpecializedGasHold
    iconName = 'res:/UI/Texture/WindowIcons/gashold.png'


class ShipMineralHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipMineralHold'
    locationFlag = const.flagSpecializedMineralHold
    iconName = 'res:/UI/Texture/WindowIcons/mineralhold.png'


class ShipSalvageHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipSalvageHold'
    locationFlag = const.flagSpecializedSalvageHold
    iconName = 'res:/UI/Texture/WindowIcons/salvagehold.png'


class ShipShipHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipShipHold'
    locationFlag = const.flagSpecializedShipHold
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'


class ShipSmallShipHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipSmallShipHold'
    locationFlag = const.flagSpecializedSmallShipHold
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'


class ShipMediumShipHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipMediumShipHold'
    locationFlag = const.flagSpecializedMediumShipHold
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'


class ShipLargeShipHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipLargeShipHold'
    locationFlag = const.flagSpecializedLargeShipHold
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'


class ShipIndustrialShipHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipIndustrialShipHold'
    locationFlag = const.flagSpecializedIndustrialShipHold
    iconName = 'res:/UI/Texture/WindowIcons/shiphangar.png'


class ShipAmmoHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipAmmoHold'
    locationFlag = const.flagSpecializedAmmoHold
    iconName = 'res:/UI/Texture/WindowIcons/itemHangar.png'


class ShipCommandCenterHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipCommandCenterHold'
    locationFlag = const.flagSpecializedCommandCenterHold
    iconName = 'res:/UI/Texture/WindowIcons/commandcenterhold.png'


class ShipPlanetaryCommoditiesHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipPlanetaryCommoditiesHold'
    locationFlag = const.flagSpecializedPlanetaryCommoditiesHold
    iconName = 'res:/UI/Texture/WindowIcons/planetarycommodities.png'


class ShipQuafeHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipQuafeHold'
    locationFlag = const.flagQuafeBay


class ShipCorpseHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipCorpseHold'
    locationFlag = const.flagCorpseBay


class ShipBoosterHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipBoosterHold'
    locationFlag = const.flagBoosterBay


class ShipSubsystemHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipSubsystemHold'
    locationFlag = const.flagSubsystemBay


class ShipMobileDepotHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipMobileDepotHold'
    locationFlag = const.flagMobileDepotHold


class ShipColonyResourcesHold(BaseShipBay):
    __guid__ = 'invCtrl.ShipColonyResourcesHold'
    locationFlag = const.flagColonyResourcesHold


class BaseCorpContainer(BaseInvContainer):
    __guid__ = 'invCtrl.BaseCorpContainer'
    scope = uiconst.SCOPE_DOCKED
    oneWay = True
    isMovable = False

    def __init__(self, itemID = None, divisionID = 0):
        self.itemID = itemID
        self.divisionID = self.roles = self.locationFlag = None
        self.SetDivisionID(divisionID)
        if self.roles is not None:
            self.SetAccess()
        self.invID = (self.__class__.__name__, self.itemID, divisionID)
        self.goals = CorpGoalsController.get_instance()

    def GetIconName(self):
        if self.locationFlag == const.flagCorpGoalDeliveries:
            return 'res:/UI/Texture/WindowIcons/goalDeliveries.png'
        return 'res:/UI/Texture/WindowIcons/corporation.png'

    def GetName(self):
        if self.locationFlag == const.flagCorpGoalDeliveries:
            return localization.GetByLabel('UI/Inventory/GoalDeliveriesHangar')
        if self.divisionID is None:
            return localization.GetByLabel('UI/Inventory/CorporationHangars')
        divisions = sm.GetService('corp').GetDivisionNames()
        return divisions[self.divisionID + 1]

    def SetDivisionID(self, divisionID):
        self.divisionID = divisionID
        self.locationFlag = const.corpFlagByDivision.get(divisionID)
        if self.locationFlag:
            self.roles = (const.corpHangarQueryRolesByFlag[self.locationFlag], const.corpHangarTakeRolesByFlag[self.locationFlag])

    def _GetInvCacheContainer(self):
        try:
            officeID = sm.GetService('officeManager').GetCorpOfficeAtLocation().officeID
            if officeID == self.itemID:
                return sm.GetService('invCache').GetInventoryFromId(self.itemID)
        except AttributeError:
            pass

        raise RuntimeError('Invalid inventory window.')

    def IsItemHere(self, item):
        ballpark = sm.GetService('michelle').GetBallpark()
        return item.locationID == self.itemID and (item.ownerID == session.corpid or ballpark and item.ownerID == ballpark.slimItems[self.itemID].ownerID) and (self.locationFlag is None or item.flagID == self.locationFlag) and self.CheckCanQuery()

    def CheckCanQuery(self):
        if self.roles is None:
            return True
        role = self.roles[0]
        if session.corprole & role == role:
            return True
        return False

    def CheckCanTake(self):
        if self.roles is None:
            return True
        role = self.roles[1]
        if session.corprole & role == role:
            return True
        return False

    def SetAccess(self):
        role = self.roles[1]
        if session.corprole & role == role:
            self.viewOnly = False
        else:
            self.viewOnly = True

    @telemetry.ZONE_METHOD
    def GetItems(self):
        if self.CheckCanQuery():
            return BaseInvContainer.GetItems(self)
        else:
            return []

    def CheckCanAdd(self, typeID, quantity):
        return self._IsItemExpected(typeID, quantity)

    def _IsItemExpected(self, typeID, quantity):
        if self.locationFlag != const.flagCorpGoalDeliveries:
            return True
        try:
            expectedItems = self.goals.get_items_pending_delivery(self.itemID)
        except:
            ShowQuickMessage(GetByLabel('UI/Corporations/Goals/FailedToConnect'))
            raise

        if typeID not in expectedItems:
            raise UserError('CannotMoveTypeToGoalDeliveries', {'containerName': self.GetName(),
             'corpName': cfg.eveowners.Get(session.corpid).name,
             'item': typeID})
        expectedQuantity = expectedItems[typeID]
        if quantity > expectedQuantity:
            raise UserError('CannotMoveQuantityToGoalDeliveries', {'containerName': self.GetName(),
             'corpName': cfg.eveowners.Get(session.corpid).name,
             'item': typeID,
             'quantity': quantity,
             'expectedQuantity': expectedQuantity})
        return True

    def CheckAndHandlePlexVaultItem(self, node):
        isPlexVaultItem = hasattr(node, 'WithdrawPlex') and callable(node.WithdrawPlex)
        if not isPlexVaultItem:
            return False
        if not self.DoesAcceptItem(node.item):
            return False
        if not self.CheckCanAdd(node.typeID, quantity=1):
            return False
        if not self.CheckAndConfirmOneWayMove():
            return False
        node.WithdrawPlex(self)
        return True


class StationCorpHangar(BaseCorpContainer):
    __guid__ = 'invCtrl.StationCorpHangar'
    hasCapacity = False

    def __init__(self, itemID = None, divisionID = 0):
        if itemID is None:
            itemID = sm.GetService('officeManager').GetCorpOfficeAtLocation().officeID
        BaseCorpContainer.__init__(self, itemID, divisionID)

    def GetItems(self):
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        if office is None or office.officeID != self.itemID:
            return []
        else:
            return BaseCorpContainer.GetItems(self)

    def GetCapacity(self):
        if sm.GetService('officeManager').GetCorpOfficeAtLocation() is None:
            return ZERO_CAPACITY
        else:
            return BaseCorpContainer.GetCapacity(self)

    def GetMenu(self):
        return []

    def IsInRange(self):
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        return office and office.officeID == self.itemID


class POSCorpHangar(BaseCorpContainer):
    __guid__ = 'invCtrl.POSCorpHangar'
    scope = uiconst.SCOPE_INFLIGHT
    hasCapacity = True

    def GetCapacity(self):
        return self._GetInvCacheContainer().GetCapacity()

    def OnItemsViewed(self):
        settings.user.ui.Set('InvPOSCorpHangar_%s' % self.itemID, self.divisionID)

    def IsInRange(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return True
        ball = bp.GetBall(self.itemID)
        if not ball:
            return False
        item = sm.GetService('michelle').GetItem(self.itemID)
        if item is None:
            return False
        operationalDistance = sm.GetService('godma').GetTypeAttribute(item.typeID, const.attributeMaxOperationalDistance)
        if operationalDistance is None:
            operationalDistance = const.maxCargoContainerTransferDistance
        if ball.surfaceDist > operationalDistance:
            if bp.IsShipInRangeOfStructureControlTower(session.shipid, self.itemID):
                return True
            return False
        return True

    def IsItemHereVolume(self, item):
        return item.locationID == self.itemID and (item.ownerID == session.corpid or session.solarsystemid and item.ownerID == sm.GetService('michelle').GetBallpark().slimItems[self.itemID].ownerID) and self.CheckCanQuery()

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)


class StationCorpMember(BaseInvContainer):
    __guid__ = 'invCtrl.StationCorpMember'
    scope = uiconst.SCOPE_STATION
    oneWay = True
    viewOnly = True
    locationFlag = const.flagHangar
    iconName = 'res:/ui/Texture/WindowIcons/member.png'

    def __init__(self, itemID = None, ownerID = None):
        self.itemID = itemID
        self.ownerID = ownerID
        self.invID = (self.__class__.__name__, itemID, ownerID)

    def GetName(self):
        return localization.GetByLabel('UI/Station/Hangar/HangarNameWithOwner', charID=self.ownerID)

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventory(const.containerHangar, self.itemID)

    def _GetContainerArgs(self):
        return (const.containerHangar, self.itemID)

    def IsItemHere(self, item):
        return item.flagID == const.flagHangar and item.locationID == session.stationid and item.ownerID == self.ownerID


class StationCorpDeliveries(BaseInvContainer):
    __guid__ = 'invCtrl.StationCorpDeliveries'
    scope = uiconst.SCOPE_DOCKED
    oneWay = True
    locationFlag = const.flagCorpDeliveries
    iconName = 'res:/UI/Texture/WindowIcons/corpdeliveries.png'
    isMovable = False
    acceptsDrops = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/CorpDeliveries')

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventory(const.containerCorpMarket, session.corpid)

    def _GetContainerArgs(self):
        return (const.containerCorpMarket, session.corpid)

    def GetOwnerID(self):
        return session.corpid

    def IsItemHere(self, item):
        return item.flagID == const.flagCorpDeliveries and item.locationID in (session.stationid, session.structureid) and item.ownerID == session.corpid

    def DoesAcceptItem(self, item):
        return False


class AssetSafetyDeliveries(BaseInvContainer):
    __guid__ = 'invCtrl.AssetSafetyDeliveries'
    scope = uiconst.SCOPE_DOCKED
    acceptsDrops = False
    locationFlag = const.flagAssetSafety
    iconName = 'res:/UI/Texture/WindowIcons/personalDeliveries.png'
    isMovable = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventory(const.containerHangar)

    def _GetContainerArgs(self):
        return (const.containerHangar,)

    def IsItemHere(self, item):
        return item.flagID == const.flagAssetSafety and item.locationID in (session.stationid, session.structureid) and (item.ownerID == session.charid or item.ownerID == session.corpid and session.corprole & const.corpRoleDirector)

    def GetMenu(self):
        return []


class StationItems(BaseInvContainer):
    __guid__ = 'invCtrl.StationItems'
    locationFlag = const.flagHangar
    scope = uiconst.SCOPE_DOCKED
    iconName = 'res:/ui/Texture/WindowIcons/itemHangar.png'
    isMovable = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/ItemHangar')

    @telemetry.ZONE_METHOD
    def IsItemHere(self, item):
        return item.locationID == session.stationid and item.ownerID == session.charid and item.flagID == const.flagHangar and item.categoryID != const.categoryShip

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventory(const.containerHangar)

    def _GetContainerArgs(self):
        return (const.containerHangar,)

    def IsPrimed(self):
        return self.IsInRange()

    def IsInRange(self):
        return session.stationid and self.itemID == session.stationid


class RedeemItems(BaseInvContainer):
    __guid__ = 'invCtrl.RedeemItems'
    locationFlag = const.flagHangar
    scope = uiconst.SCOPE_DOCKED
    isMovable = False
    viewOnly = True

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)

    def __AddItem(self, item, sourceLocationID, quantity):
        sourceFlagID = item.flagID
        dropLocationID = self._GetInvCacheContainer().GetItem().itemID
        isDropInSameLocation = dropLocationID == sourceLocationID and sourceFlagID == self.locationFlag
        isDividing = quantity != item.stacksize
        if isDropInSameLocation and not isDividing:
            return
        super(RedeemItems, self).__AddItem(item, sourceLocationID, quantity)

    def _GetItems(self):
        self.redeemSvc = sm.GetService('redeem')
        self.tokens = self.redeemSvc.GetRedeemTokens()
        self.items = []
        for token in self.tokens:
            tokenID = int(token.tokenID) if token.tokenID else None
            typeID = int(token.typeID)
            massTokenID = int(token.massTokenID) if token.massTokenID else None
            categoryID = evetypes.GetCategoryID(typeID)
            isAutoInject = self.redeemSvc.redeemData.is_auto_injected(token)
            blueprintInfo = None
            if categoryID == invConst.categoryBlueprint:
                blueprintInfo = Bundle(isCopy=True, runs=token.blueprintRuns or 1, materialEfficiency=token.blueprintMaterialLevel, timeEfficiency=token.blueprintProductivityLevel)
            qty = token.quantity * evetypes.GetPortionSize(typeID)
            item = Bundle(itemID=tokenID, typeID=typeID, ownerID=session.charid, locationID=session.stationid or session.structureid or session.solarsystemid, flagID=int(self.locationFlag), quantity=qty, categoryID=categoryID, groupID=evetypes.GetGroupID(typeID), customInfo=None, stacksize=qty, singleton=None, tokenID=tokenID, massTokenID=massTokenID, stationID=token.stationID, expireDateTime=token.expireDateTime, description=self.redeemSvc.GetTokenDescription(token) or self.redeemSvc.GetTokenLabel(token), dateTime=token.dateTime, blueprintInfo=blueprintInfo, isAutoInject=isAutoInject)
            self.items.append(item)

        return self.items

    def IsItemHere(self, item):
        if not item:
            return False
        if session.charid:
            return item.ownerID == session.charid
        return True

    def GetInventoryItem(self):
        return None


class StationShips(BaseInvContainer):
    __guid__ = 'invCtrl.StationShips'
    iconName = 'res:/ui/Texture/WindowIcons/shiphangar.png'
    scope = uiconst.SCOPE_DOCKED
    locationFlag = const.flagHangar
    isMovable = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/ShipHangar')

    @telemetry.ZONE_METHOD
    def IsItemHere(self, item):
        return item.locationID == session.stationid and item.ownerID == session.charid and item.flagID == const.flagHangar and item.categoryID == const.categoryShip

    def GetActiveShip(self):
        activeShipID = eveCfg.GetActiveShip()
        for item in self._GetItems():
            if item.itemID == activeShipID:
                return item

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventory(const.containerHangar)

    def _GetContainerArgs(self):
        return (const.containerHangar,)

    def IsPrimed(self):
        return self.IsInRange()

    def IsInRange(self):
        return session.stationid and self.itemID == session.stationid


class CustomsOffice(BaseInvContainer):
    __guid__ = 'invCtrl.CustomsOffice'
    isMovable = False


LOOT_ALL_BUTTON_NAME = 'invLootAllBtn'

class BaseCelestialContainer(BaseInvContainer):
    __guid__ = 'invCtrl.BaseCelestialContainer'
    hasCapacity = True
    isMovable = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self._isLootable = None

    def IsItemHere(self, item):
        if self.locationFlag is not None:
            return item.locationID == self.itemID and item.flagID == self.locationFlag
        else:
            return item.locationID == self.itemID

    def IsInRange(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None or not InSpace():
            return True
        ball = bp.GetBall(self.itemID)
        if not ball:
            return False
        item = sm.GetService('michelle').GetItem(self.itemID)
        if item is None:
            return False
        if ball.surfaceDist > self.GetOperationalDistance(item.typeID):
            if bp.IsShipInRangeOfStructureControlTower(session.shipid, self.itemID):
                return True
            return False
        return True

    def GetOperationalDistance(self, typeID):
        distance = sm.GetService('godma').GetTypeAttribute(typeID, const.attributeMaxOperationalDistance)
        if distance is None:
            distance = const.maxCargoContainerTransferDistance
        return distance

    def GetIconName(self):
        try:
            typeID = self.GetTypeID()
        except UserError:
            return self.iconName

        if typeID:
            icon = inventorycommon.typeHelpers.GetIcon(typeID)
            if icon and icon.iconFile:
                return icon.iconFile
        return self.iconName

    def GetTypeID(self):
        if self.typeID is not None:
            return self.typeID
        bp = sm.GetService('michelle').GetBallpark()
        if bp and self.itemID in bp.slimItems:
            slimItem = bp.slimItems[self.itemID]
            self.typeID = slimItem.typeID
        else:
            self.typeID = BaseInvContainer.GetTypeID(self)
        return self.typeID

    def GetName(self):
        if self.name:
            return self.name
        bp = sm.GetService('michelle').GetBallpark()
        if bp:
            slimItem = bp.slimItems.get(self.itemID, None)
            if slimItem:
                return uix.GetSlimItemName(slimItem)
        return ''

    def _DBLessLimitationsCheck(self, errorName, item):
        if errorName in ('NotEnoughCargoSpace', 'NotEnoughCargoSpaceOverload'):
            eve.Message('ItemMoveGoesThroughFullCargoHold', {'itemType': item.typeID})
            return True
        return False

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.GetTypeID())

    def GetSpecialActions(self):
        if self.IsLootable():
            return [(localization.GetByLabel('UI/Inventory/LootAll'),
              self.LootAll,
              LOOT_ALL_BUTTON_NAME,
              True)]
        return []

    def LootAll(self, *args):
        items = self.GetItems()
        shipCargo = ShipCargo()
        if len(items) > 0:
            if sm.GetService('crimewatchSvc').CheckCanTakeItems(self.itemID):
                if sm.GetService('consider').ConfirmTakeIllicitGoods(items):
                    shipCargo.AddItems(items)
                    sm.GetService('audio').SendUIEvent('ui_notify_mission_rewards_play')
            else:
                sm.GetService('crimewatchSvc').SafetyActivated(const.shipSafetyLevelPartial)
                raise UserError('LootTheftDeniedSafetyPreventsSuspect', {'containerName': (const.UE_TYPEID, self.GetTypeID())})
        if shipCargo.HasEnoughSpaceForItems(items):
            sm.ScatterEvent('OnWreckLootAll', self.GetInvID(), items)

    def IsLootable(self):
        if self._isLootable is None:
            bp = sm.GetService('michelle').GetBallpark()
            item = bp.GetInvItem(self.itemID) if bp else None
            if item and item.groupID in LOOT_GROUPS:
                self._isLootable = True
            else:
                self._isLootable = False
        return self._isLootable


class POSRefinery(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSRefinery'
    locationFlag = const.flagCargo
    iconName = 'res:/UI/Texture/Icons/24_64_1.png'


class POSCompression(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSCompression'
    locationFlag = const.flagCargo
    iconName = 'res:/UI/Texture/Icons/24_64_1.png'


class POSStructureCharges(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSStructureCharges'
    locationFlag = const.flagHiSlot0

    def GetIconName(self):
        typeID = self.GetTypeID()
        groupID = evetypes.GetGroupID(typeID)
        if groupID == const.groupMobileHybridSentry:
            return 'res:/UI/Texture/Icons/13_64_5.png'
        elif groupID == const.groupMobileMissileSentry:
            return 'res:/UI/Texture/Icons/12_64_16.png'
        elif groupID == const.groupMobileProjectileSentry:
            return 'res:/UI/Texture/Icons/12_64_9.png'
        else:
            return BaseCelestialContainer.GetIconName(self)


class POSStructureChargeCrystal(POSStructureCharges):
    __guid__ = 'invCtrl.POSStructureChargeCrystal'
    iconName = 'res:/UI/Texture/Icons/8_64_2.png'

    def __init__(self, *args, **kwargs):
        POSStructureCharges.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/ActiveCrystal')


class POSStructureChargesStorage(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSStructureChargesStorage'
    locationFlag = const.flagNone
    iconName = 'res:/UI/Texture/Icons/8_64_1.png'

    def __init__(self, *args, **kwargs):
        BaseCelestialContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/CrystalStorage')


class POSStrontiumBay(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSStrontiumBay'
    locationFlag = const.flagSecondaryStorage
    iconName = 'res:/UI/Texture/Icons/51_64_10.png'

    def __init__(self, *args, **kwargs):
        BaseCelestialContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/StrontiumBay')


class POSFuelBay(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSFuelBay'
    locationFlag = const.flagNone
    iconName = 'res:/UI/Texture/Icons/98_64_9.png'

    def __init__(self, *args, **kwargs):
        BaseCelestialContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Ship/FuelBay')

    def PromptUserForQuantity(self, item, itemQuantity, sourceLocation, maxQtyAllowed = None):
        if sourceLocation == self.itemID:
            return None
        return BaseCelestialContainer.PromptUserForQuantity(self, item, itemQuantity)


class POSShipMaintenanceArray(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSShipMaintenanceArray'
    locationFlag = const.flagNone
    iconName = 'res:/ui/Texture/WindowIcons/settings.png'


class POSPersonalHangar(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSPersonalHangar'
    locationFlag = const.flagHangar
    iconName = 'res:/ui/Texture/WindowIcons/itemHangar.png'

    def IsItemHere(self, item):
        return BaseCelestialContainer.IsItemHere(self, item) and session.charid == item.ownerID

    def GetCapacity(self):
        cap = BaseCelestialContainer.GetCapacity(self)
        totalVolume = 0
        for item in self.GetItems():
            totalVolume += GetItemVolume(item)

        return utillib.KeyVal(capacity=cap.capacity, used=totalVolume)


class POSMobileReactor(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSMobileReactor'
    locationFlag = const.flagNone
    iconName = 'res:/UI/Texture/Icons/27_64_11.png'

    def PromptUserForQuantity(self, item, itemQuantity, sourceLocation, maxQtyAllowed = None):
        if sourceLocation == self.itemID:
            return None
        return BaseCelestialContainer.PromptUserForQuantity(self, item, itemQuantity)


class POSSilo(BaseCelestialContainer):
    __guid__ = 'invCtrl.POSSilo'
    locationFlag = const.flagNone
    iconName = 'res:/UI/Texture/Icons/26_64_12.png'

    def PromptUserForQuantity(self, item, itemQuantity, sourceLocation, maxQtyAllowed = None):
        if sourceLocation == self.itemID:
            return None
        return BaseCelestialContainer.PromptUserForQuantity(self, item, itemQuantity)


class ItemFloatingCargo(BaseCelestialContainer):
    __guid__ = 'invCtrl.ItemFloatingCargo'
    iconName = 'res:/UI/Texture/Shared/Brackets/containerCargo_20x20.png'

    def GetIconName(self):
        return self.iconName

    def GetItems(self):
        sm.GetService('wreck').MarkViewed(self.itemID, True)
        return BaseCelestialContainer.GetItems(self)


class ShipMaintenanceBay(BaseCelestialContainer):
    __guid__ = 'invCtrl.ShipMaintenanceBay'
    locationFlag = const.flagShipHangar
    iconName = 'res:/ui/Texture/WindowIcons/settings.png'

    def GetName(self):
        bayName = GetNameForFlag(self.locationFlag)
        if session.solarsystemid and self.itemID != eveCfg.GetActiveShip():
            return localization.GetByLabel('UI/Inventory/BayAndLocationName', bayName=evetypes.GetName(self.GetTypeID()), locationName=bayName)
        return bayName

    def GetOperationalDistance(self, *args):
        return const.maxCargoContainerTransferDistance


class ShipFleetHangar(BaseCelestialContainer):
    __guid__ = 'invCtrl.ShipFleetHangar'
    locationFlag = const.flagFleetHangar
    iconName = 'res:/ui/Texture/WindowIcons/fleet.png'

    def GetName(self):
        bayName = GetNameForFlag(self.locationFlag)
        if session.solarsystemid and self.itemID != eveCfg.GetActiveShip():
            return localization.GetByLabel('UI/Inventory/BayAndLocationName', bayName=evetypes.GetName(self.GetTypeID()), locationName=bayName)
        return bayName

    def GetOperationalDistance(self, *args):
        return const.maxCargoContainerTransferDistance


class StationContainer(BaseCelestialContainer):
    __guid__ = 'invCtrl.StationContainer'
    hasCapacity = True
    isMovable = True

    def __init__(self, *args, **kwargs):
        BaseCelestialContainer.__init__(self, *args, **kwargs)
        self._oneWay = None
        self.invItem = None

    @property
    def oneWay(self):
        if self._oneWay is not None:
            return self._oneWay
        if self.invItem is None:
            try:
                self.invItem = self.GetInventoryItem()
            except StandardError:
                self._oneWay = super(StationContainer, self).oneWay
                return self._oneWay

        if self.invItem.ownerID == session.corpid and self.invItem.flagID in invConst.flagCorpSAGs:
            self._oneWay = True
        return self._oneWay

    def GetMenu(self):
        return GetMenuService().InvItemMenu(self.GetInventoryItem())

    def GetName(self):
        name = cfg.evelocations.Get(self.itemID).name
        if not name:
            name = evetypes.GetName(self.GetTypeID())
        return name

    def IsInRange(self):
        return True

    def CheckAndConfirmOneWayMove(self):
        if self.oneWay:
            return self.PromptOneWayMove()
        if session.solarsystemid:
            invItem = self.GetInventoryItem()
            bp = sm.GetService('michelle').GetBallpark()
            if bp:
                ball = bp.GetBallById(invItem.locationID)
                if ball and evetypes.GetGroupID(ball.typeID) in (const.groupCorporateHangarArray, const.groupAssemblyArray, const.groupMobileLaboratory):
                    return self.PromptOneWayMove()
                if invItem.flagID == const.flagFleetHangar and invItem.ownerID != session.charid:
                    return self.PromptOneWayMove()
        return True

    def AddItems(self, items):
        allowedItems = []
        forbiddenTypes = set()
        for item in items:
            typeID = item.typeID
            if can_be_added_to_container(typeID, self.typeID):
                allowedItems.append(item)
            else:
                forbiddenTypes.add(typeID)

        if forbiddenTypes:
            raise ItemCannotBeAddedToContainer(type_ids=forbiddenTypes)
        super(StationContainer, self).AddItems(allowedItems)


class AssetSafetyContainer(StationContainer):
    __guid__ = 'invCtrl.AssetSafetyContainer'
    scope = uiconst.SCOPE_DOCKED
    isMovable = False

    def __init__(self, itemID = None, typeID = None, name = None):
        StationContainer.__init__(self, itemID, typeID)
        self.name = name

    def GetName(self):
        return self.name or ''

    def IsItemHere(self, item):
        return item.locationID == self.itemID


class ItemWreck(BaseCelestialContainer):
    __guid__ = 'invCtrl.ItemWreck'
    hasCapacity = False

    def GetIconName(self):
        slimItem = sm.GetService('michelle').GetBallpark().slimItems[self.itemID]
        return sm.GetService('bracket').GetBracketIcon(slimItem.typeID, slimItem.isEmpty)

    @telemetry.ZONE_METHOD
    def GetItems(self):
        sm.GetService('wreck').MarkViewed(self.itemID, True, True)
        return BaseCelestialContainer.GetItems(self)


class PlayerTrade(BaseInvContainer):
    __guid__ = 'invCtrl.PlayerTrade'
    scope = uiconst.SCOPE_DOCKED
    viewOnly = True
    hasCapacity = False
    isLockable = False
    filtersEnabled = False
    isMovable = False

    def __init__(self, itemID = None, ownerID = None, tradeSession = None):
        self.itemID = itemID
        self.ownerID = ownerID
        self.tradeSession = tradeSession
        self.invID = (self.__class__.__name__, itemID, ownerID)

    def _GetItems(self):
        return [ item for item in self.tradeSession.List().items ]

    def IsItemHere(self, item):
        return item.ownerID == self.ownerID and self.itemID == item.locationID

    def GetOwnerID(self):
        return self.ownerID

    def AddItems(self, items):
        activeShipID = eveCfg.GetActiveShip()
        nonTradableTypes = set()
        for item in items:
            if item.itemID == activeShipID:
                raise UserError('PeopleAboardShip')
            if item.typeID == const.typeAssetSafetyWrap:
                raise UserError('CannotTradeAssetSafety')
            if not is_tradable(item.typeID):
                nonTradableTypes.add(item.typeID)

        if nonTradableTypes:
            raise ItemCannotBeTraded(type_ids=nonTradableTypes)
        BaseInvContainer.AddItems(self, items)

    def _GetInvCacheContainer(self):
        self.tradeSession.GetItem = self.tradeSession.GetSelfInvItem
        return self.tradeSession


class SpaceComponentInventory(BaseCelestialContainer):
    __guid__ = 'invCtrl.SpaceComponentInventory'
    iconName = 'res:/ui/Texture/WindowIcons/itemHangar.png'
    locationFlag = const.flagCargo

    def GetMenu(self):
        return GetMenuService().CelestialMenu(self.itemID)

    def _GetAcceptedCargoBayTypeIDs(self):
        myTypeID = self.GetTypeID()
        if HasCargoBayComponent(myTypeID):
            cargo_bay = get_space_component_for_type(myTypeID, CARGO_BAY)
            return cargo_bay.acceptedTypeIDs

    def DoesAcceptItem(self, item):
        if not BaseCelestialContainer.DoesAcceptItem(self, item):
            return False
        acceptedTypeIDs = self._GetAcceptedCargoBayTypeIDs()
        if acceptedTypeIDs is not None and item.typeID not in acceptedTypeIDs:
            return False
        return True

    def HasUnderConstructionComponent(self):
        return HasUnderConstructionComponent(self.GetTypeID())

    def GetInputItems(self):
        if self.HasUnderConstructionComponent():
            underConstructionComp = get_space_component_for_type(self.GetTypeID(), UNDER_CONSTRUCTION)
            return underConstructionComp.inputItems
        return {}


class StructureContainer(BaseInvContainer):
    isMovable = False

    def IsInRange(self):
        return session.structureid and self.itemID == session.structureid

    def GetMenu(self):
        return []


class StructureBay(StructureContainer):

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.flagID == self.locationFlag and item.ownerID == self.GetOwnerID()


class Structure(StructureContainer):
    __guid__ = 'invCtrl.Structure'
    iconName = 'res:/ui/Texture/WindowIcons/structurebrowser.png'

    def GetName(self):
        name = cfg.evelocations.Get(self.itemID).name
        if not name:
            name = evetypes.GetName(self.GetTypeID())
        return name

    def IsItemHere(self, item):
        return False


class StructureAmmoBay(StructureBay):
    __guid__ = 'invCtrl.StructureAmmoBay'
    iconName = 'res:/ui/Texture/WindowIcons/itemHangar.png'
    locationFlag = const.flagCargo

    def GetName(self):
        return localization.GetByLabel('UI/Ship/AmmoHold')

    def DoesAcceptItem(self, item):
        return item.categoryID == const.categoryCharge


class StructureFuelBay(StructureBay):
    __guid__ = 'invCtrl.StructureFuelBay'
    iconName = 'res:/UI/Texture/WindowIcons/fuelbay.png'
    locationFlag = const.flagStructureFuel

    def GetName(self):
        return localization.GetByLabel('UI/Ship/FuelBay')

    def DoesAcceptItem(self, item):
        return item.groupID == const.groupFuelBlock


class StructureFighterBay(StructureBay):
    __guid__ = 'invCtrl.StructureFighterBay'
    iconName = 'res:/UI/Texture/WindowIcons/dronebay.png'
    locationFlag = const.flagFighterBay
    hasCapacity = True

    def GetName(self):
        return localization.GetByLabel('UI/Ship/FighterBay')

    def DoesAcceptItem(self, item):
        return item.categoryID == const.categoryFighter


class StructureItemHangar(StructureContainer):
    __guid__ = 'invCtrl.StructureItemHangar'
    iconName = 'res:/ui/Texture/WindowIcons/itemHangar.png'
    locationFlag = const.flagHangar

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/ItemHangar')

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.ownerID == session.charid and item.flagID == const.flagHangar and item.categoryID != const.categoryShip


class StructureShipHangar(StructureContainer):
    __guid__ = 'invCtrl.StructureShipHangar'
    iconName = 'res:/ui/Texture/WindowIcons/shiphangar.png'
    locationFlag = const.flagHangar

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/ShipHangar')

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.ownerID == session.charid and item.flagID == const.flagHangar and item.categoryID == const.categoryShip


class StructureDeliveriesHangar(StructureContainer):
    __guid__ = 'invCtrl.StructureDeliveriesHangar'
    iconName = 'res:/ui/Texture/WindowIcons/personalDeliveries.png'
    locationFlag = const.flagDeliveries
    isMovable = False

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/DeliveriesHangar')

    def IsItemHere(self, item):
        return item.locationID == self.itemID and item.ownerID == session.charid and item.flagID == const.flagDeliveries

    def DoesAcceptItem(self, item):
        if item.typeID == invConst.typePlex and item.itemID is None:
            return False
        return super(StructureDeliveriesHangar, self).DoesAcceptItem(item)


class StructureCorpHangar(BaseCorpContainer):
    __guid__ = 'invCtrl.StructureCorpHangar'

    def IsInRange(self):
        office = sm.GetService('officeManager').GetCorpOfficeAtLocation()
        return office and office.officeID == self.itemID

    def GetMenu(self):
        return []

    def GetItems(self):
        try:
            return BaseCorpContainer.GetItems(self)
        except UserError:
            return []

    def SetDivisionID(self, divisionID):
        BaseCorpContainer.SetDivisionID(self, divisionID)
        self.locationFlag = const.corpFlagByDivision.get(divisionID)


class AssetSafetyCorpContainer(StructureCorpHangar):
    __guid__ = 'invCtrl.AssetSafetyCorpContainer'
    scope = uiconst.SCOPE_DOCKED
    isMovable = False

    def GetName(self):
        if self.divisionID == invConst.flagCorpDeliveries:
            return localization.GetByLabel('UI/Inventory/CorpDeliveries')
        return StructureCorpHangar.GetName(self)

    def SetDivisionID(self, divisionID):
        StructureCorpHangar.SetDivisionID(self, divisionID)
        self.locationFlag = invConst.corpAssetSafetyFlagsFromDivision.get(divisionID)

    def GetIconName(self):
        if self.locationFlag == const.flagCorpDeliveries:
            return 'res:/UI/Texture/WindowIcons/corpdeliveries.png'
        return StructureCorpHangar.GetIconName(self)

    def DoesAcceptItem(self, item):
        if item.typeID == invConst.typePlex and item.itemID is None:
            return False
        return super(AssetSafetyCorpContainer, self).DoesAcceptItem(item)

    def _GetInvCacheContainer(self):
        return sm.GetService('invCache').GetInventoryFromId(self.itemID)

    def IsInRange(self):
        return True


class StructureDeedBay(StructureBay):
    __guid__ = 'invCtrl.StructureDeedBay'
    iconName = 'res:/UI/Texture/WindowIcons/fuelbay.png'
    locationFlag = invConst.flagStructureDeed

    def GetName(self):
        return localization.GetByLabel('UI/Ship/StructureDeedBay')

    def DoesAcceptItem(self, item):
        return item.groupID == invConst.groupStructureDeed


class StructureMoonMaterialBay(BaseCelestialContainer):
    __guid__ = 'invCtrl.StructureMoonMaterialBay'
    iconName = 'res:/ui/Texture/WindowIcons/moon_material_bay.png'
    locationFlag = const.flagMoonMaterialBay

    def __init__(self, *args, **kwargs):
        BaseInvContainer.__init__(self, *args, **kwargs)
        self.name = localization.GetByLabel('UI/Inventory/MoonMaterialBay')
        self._isLootable = True

    def DoesAcceptItem(self, item):
        return False

    def GetOperationalDistance(self, *args):
        return const.maxCargoContainerTransferDistance

    def CheckCanAdd(self, typeID, quantity):
        return False

    def IsInRange(self):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return False
        ball = bp.GetBall(self.itemID)
        if not ball:
            return False
        operationalDistance = const.maxCargoContainerTransferDistance
        if ball.surfaceDist > operationalDistance:
            return False
        return True

    def GetIconName(self):
        return self.iconName


def GetInvCtrlFromInvID(invID):
    from eve.client.script.environment import invControllers
    if invID is None:
        return
    cls = getattr(invControllers, invID[0], None)
    if cls is not None:
        return cls(*invID[1:])


class ItemSiphonPseudoSilo(BaseCelestialContainer):
    __guid__ = 'invCtrl.ItemSiphonPseudoSilo'
    iconName = 'res:/UI/Texture/Icons/38_20_12.png'

    def GetIconName(self):
        return self.iconName

    def GetItems(self):
        return BaseCelestialContainer.GetItems(self)


class PlexVault(BaseInvContainer):
    __guid__ = 'invCtrl.PlexVault'
    iconName = PLEX_128_GRADIENT_YELLOW
    locationFlag = None
    hasCapacity = False
    oneWay = False
    viewOnly = False
    scope = None
    isLockable = False
    isMovable = False
    filtersEnabled = False
    typeID = None
    acceptsDrops = True

    def IsItemHere(self, item):
        return False

    def IsPrimed(self):
        return True

    def DoesAcceptItem(self, item):
        return item.groupID == invConst.groupCurrency

    def GetInventoryItem(self):
        return None

    def GetMenu(self):
        return []

    def GetItems(self):
        return []

    def AddItems(self, items):
        locationID = session.stationid or session.structureid
        inventoryMgr = sm.GetService('invCache').GetInventoryMgr()
        for item in items:
            if item.groupID != invConst.groupCurrency:
                continue
            quantity = item.stacksize
            if len(items) == 1 and uicore.uilib.Key(uiconst.VK_SHIFT):
                quantity = self.PromptUserForQuantity(item, quantity)
            if not quantity:
                continue
            reference = inventoryMgr.DepositPlexToVault(locationID, item.itemID, quantity)
            PlexDepositListener(session.userid, quantity, reference)

    def OnDropData(self, nodes):
        items = super(PlexVault, self).OnDropData(nodes)
        for node in nodes:
            if getattr(node, '__guid__', None) == 'listentry.InvAssetItem':
                items.append(node.item)

        return items

    def CheckAndHandlePlexVaultItem(self, node):
        return False

    def PromptUserForQuantity(self, item, itemQuantity, sourceLocation = None, maxQtyAllowed = None):
        message = localization.GetByLabel('UI/Inventory/ItemActions/DivideItemStack')
        quantity = item.stacksize
        ret = uix.QtyPopup(maxvalue=quantity, minvalue=0, setvalue=quantity, hint=message)
        if ret:
            return ret['qty']
