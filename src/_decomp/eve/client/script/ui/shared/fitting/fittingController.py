#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingController.py
import sys
from collections import defaultdict
import carbonui.const as uiconst
import dogma.const as dogmaConst
import evetypes
import inventorycommon.const as invConst
import log
import shipmode
import signals
from cosmetics.client.ships.ship_skin_signals import on_skin_state_set
from eve.client.script.ui.inflight.shipstance import ShipStanceButtonController
from eve.client.script.ui.shared.skins.controller import GetSkinnedShipModel, GetMultiHullTypeIDList
from eve.client.script.ui.shared.fitting.fittingSlotController import FittingSlotController
from eve.client.script.ui.shared.fitting.fittingUtil import IsCharge, NUM_SUBSYSTEM_SLOTS, GHOST_FITTABLE_CATEGORIES, GetShipAttributeWithDogmaLocation, GetTypeIDForController, CanFitFromSourceLocation
from eve.client.script.ui.shared.fittingScreen.controllerGhostFittingExtension import FittingControllerGhostFittingExtension
from eve.client.script.ui.shared.fittingScreen.fittingSlotController import ShipFittingSlotController
from eve.client.script.ui.shared.fittingScreen.structureFittingController import StructureFittingServiceSlotController
from eve.client.script.ui.shared.fittingScreen.fittingStanceButtons import GhostShipStanceButtonController
from eve.client.script.ui.shared.fittingScreen.ghostControllerMixin import GhostControllerMixin
from eve.common.script.sys.eveCfg import IsControllingStructure
from inventorycommon.util import IsShipFittingFlag
from carbonui.uicore import uicore

class FittingController(object):
    __notifyevents__ = ['OnDogmaAttributeChanged',
     'OnStanceActive',
     'OnDogmaItemChange',
     'OnGodmaFlushLocation',
     'OnAttributes',
     'OnAttribute',
     'ProcessActiveShipChanged',
     'OnPostCfgDataChanged',
     'OnDogmaDronesChanged',
     'OnSkillsChanged',
     'OnFighterTubeTaskStatus',
     'OnDroneControlLost']
    SLOTGROUPS = ()
    SLOTGROUP_LAYOUT_ARCS = {0: (-35.0, 82.0),
     1: (54.0, 82.0),
     2: (143.0, 82.0),
     3: (233.0, 51.0),
     4: (287.0, 31.0)}
    SLOT_CLASS = FittingSlotController

    def __init__(self, itemID, typeID = None):
        self._itemID = itemID
        self._typeID = typeID or GetTypeIDForController(itemID)
        self.isShipSimulated = sm.GetService('fittingSvc').IsShipSimulated()
        self.ghostFittingExtension = FittingControllerGhostFittingExtension()
        self.SetDogmaLocation()
        sm.RegisterNotify(self)
        on_skin_state_set.connect(self._OnSkinStateSet)
        self.previewFittedItem = None
        self._skin = None
        self.on_new_itemID = signals.Signal(signalName='on_new_itemID')
        self.on_stats_changed = signals.Signal(signalName='on_stats_changed')
        self.on_hardpoints_fitted = signals.Signal(signalName='on_hardpoints_fitted')
        self.on_slots_updated = signals.Signal(signalName='on_slots_updated')
        self.on_subsystem_fitted = signals.Signal(signalName='on_subsystem_fitted')
        self.on_subsystem_really_changed = signals.Signal(signalName='on_subsystem_really_changed')
        self.on_module_online_state = signals.Signal(signalName='on_module_online_state')
        self.on_item_ghost_fitted = signals.Signal(signalName='on_item_ghost_fitted')
        self.on_name_changed = signals.Signal(signalName='on_name_changed')
        self.on_skin_material_changed = signals.Signal(signalName='on_skin_material_changed')
        self.on_stance_activated = signals.Signal(signalName='on_stance_activated')
        self.on_should_close = signals.Signal(signalName='on_should_close')
        self.on_slots_with_menu_changed = signals.Signal(signalName='on_slots_with_menu_changed')
        self.on_controller_changing = signals.Signal(signalName='on_controller_changing')
        self.on_drones_changed = signals.Signal(signalName='on_drones_changed')
        self.on_warning_display_changed = signals.Signal(signalName='on_warning_display_changed')
        self.slotsByFlagID = {}
        self.slotFlagWithMenu = None
        self.ConstructSlotControllers()
        self._UpdateSkin()

    def GetSlotClass(self, flagID):
        return self.SLOT_CLASS

    def SetDogmaLocation(self):
        if self.IsSimulated():
            dogmaLocation = self.ghostFittingExtension.GetDogmaLocation()
        else:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        self.dogmaLocation = dogmaLocation

    def ConstructSlotControllers(self):
        for slot in self.slotsByFlagID.values():
            slot.Close()

        self.slotsByFlagID = {}
        self.slotsByGroups = {}
        for groupIdx, flagIDs in self.SLOTGROUPS:
            group = []
            for i, flagID in enumerate(flagIDs):
                invItem = self.GetFittedModulesByFlagID().get(flagID, None)
                slotClass = self.GetSlotClass(flagID)
                slotController = slotClass(flagID=flagID, parentController=self)
                self.slotsByFlagID[flagID] = slotController
                group.append(slotController)

            self.slotsByGroups[groupIdx] = group

        self._UpdateSlots()

    def GetSlotsByGroups(self):
        return self.slotsByGroups

    def GetTotalNumSlots(self):
        return sum([ len(group) for group in self.slotsByGroups.itervalues() ])

    def _UpdateSlots(self):
        for flagID, slot in self.slotsByFlagID.iteritems():
            self.SetSlotModuleAndChargeIDs(slot, flagID)

        for slot in self.slotsByFlagID.itervalues():
            slot.on_item_fitted()

        self.on_slots_updated()

    def OnSlotAttributeChanged(self, flagID, shipID, itemID, attributeID, value):
        slot = self.slotsByFlagID[flagID]
        self.SetSlotModuleAndChargeIDs(slot, flagID)
        slot.OnSlotAttributeChanged(shipID, itemID, attributeID, value)

    def SetSlotModuleAndChargeIDs(self, slot, flagID):
        module, charge = self._GetModuleAndCharge(flagID=flagID)
        chargeItemID = charge.itemID if charge else None
        moduleItemID = module.itemID if module else None
        slot.SetModuleAndChargeIDs(moduleItemID, chargeItemID)
        if moduleItemID:
            slot.SetFailedTypeID(None)

    def SetFailedModuleTypeIDs(self, failedTypeIDsByFlags):
        for flagID, slot in self.slotsByFlagID.iteritems():
            typeID = failedTypeIDsByFlags.get(flagID, None)
            slot.SetFailedTypeID(typeID)

    def UpdateItem(self, itemID, typeID = None):
        oldItemID = self._itemID
        oldTypeID = self._typeID
        self._itemID = itemID
        if typeID is None:
            typeID = GetTypeIDForController(itemID)
        self._typeID = typeID
        if self.IsControllerChanging(itemID, typeID, oldItemID, oldTypeID):
            self.on_controller_changing(itemID)
        self._UpdateSkin()
        self.on_new_itemID(itemID, oldItemID, typeID, oldTypeID)
        self._UpdateSlots()

    def _UpdateSkin(self):
        self._skin = sm.GetService('cosmeticsSvc').GetAppliedSkinStateForCurrentSession(self._itemID)

    def GetDogmaItem(self):
        return self.dogmaLocation.SafeGetDogmaItem(self._itemID)

    @property
    def dogmaItem(self):
        return self.GetDogmaItem()

    def CurrentShipIsLoaded(self):
        return bool(self.GetDogmaItem())

    def GetDogmaLocation(self):
        return self.dogmaLocation

    def GetItemID(self):
        return self._itemID

    @property
    def itemID(self):
        return self.GetItemID()

    def GetTypeID(self):
        if self._typeID:
            return self._typeID
        return self.GetDogmaItem().typeID

    @property
    def typeID(self):
        return self.GetTypeID()

    def IsShip(self):
        return evetypes.GetCategoryID(self.GetTypeID()) == const.categoryShip

    def GetAttribute(self, attributeID):
        return GetShipAttributeWithDogmaLocation(self.dogmaLocation, self.GetItemID(), attributeID)

    def GetFittedModules(self):
        shipDogmaItem = self.GetDogmaItem()
        if shipDogmaItem:
            return shipDogmaItem.GetFittedItems().values()
        return []

    def SetPreviewFittedItem(self, previewItem = None, force = False):
        if previewItem and evetypes.GetCategoryID(previewItem.typeID) not in GHOST_FITTABLE_CATEGORIES:
            return
        if self.IsSwitchingShips():
            return
        self.previewFittedItem = previewItem
        self.on_item_ghost_fitted()
        self.on_stats_changed()

    def GetPreviewFittedItem(self):
        return self.previewFittedItem

    def GetNumTurretsAndLaunchersFitted(self):
        turretsFitted = 0
        launchersFitted = 0
        modulesByGroupInShip = {}
        for module in self.GetFittedModules():
            if module.groupID not in modulesByGroupInShip:
                modulesByGroupInShip[module.groupID] = []
            modulesByGroupInShip[module.groupID].append(module)
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, dogmaConst.effectLauncherFitted):
                launchersFitted += 1
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, dogmaConst.effectTurretFitted):
                turretsFitted += 1

        return (launchersFitted, turretsFitted)

    def GetFittedModulesByFlagID(self):
        modulesByFlag = {}
        for module in self.GetFittedModules():
            modulesByFlag[module.flagID, IsCharge(module.typeID)] = module

        return modulesByFlag

    def GetFittedModulesByGroupID(self):
        modulesByGroupInShip = defaultdict(list)
        for module in self.GetFittedModules():
            modulesByGroupInShip[module.groupID].append(module)

        return modulesByGroupInShip

    def _GetModuleAndCharge(self, flagID):
        module = charge = None
        for item in self.GetFittedModules():
            if item.flagID == flagID:
                if IsCharge(item.typeID):
                    charge = item
                else:
                    module = item

        return (module, charge)

    def GetSlotAdditionInfo(self, typeAttributesByID):
        hiSlotAddition = 0
        medSlotAddition = 0
        lowSlotAddition = 0
        if self.GetItemID() and self.IsShip():
            subSystemSlot = typeAttributesByID.get(dogmaConst.attributeSubSystemSlot, None)
            if subSystemSlot is not None:
                slotOccupant = self.dogmaLocation.GetSubSystemInFlag(self.GetItemID(), int(subSystemSlot))
                if slotOccupant is not None:
                    attributesByName = self.dogmaLocation.dogmaStaticMgr.attributesByName
                    GTA = lambda attributeID: self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(slotOccupant.typeID, attributeID)
                    hiSlotAddition = -GTA(attributesByName['hiSlotModifier'].attributeID)
                    medSlotAddition = -GTA(attributesByName['medSlotModifier'].attributeID)
                    lowSlotAddition = -GTA(attributesByName['lowSlotModifier'].attributeID)
        return (lowSlotAddition, medSlotAddition, hiSlotAddition)

    def GetHardpointAdditionInfo(self, typeAttributesByID):
        turretAddition = 0
        launcherAddition = 0
        if self.GetItemID() and self.IsShip():
            subSystemSlot = typeAttributesByID.get(dogmaConst.attributeSubSystemSlot, None)
            if subSystemSlot is not None:
                slotOccupant = self.dogmaLocation.GetSubSystemInFlag(self.GetItemID(), int(subSystemSlot))
                if slotOccupant is not None:
                    attributesByName = self.dogmaLocation.dogmaStaticMgr.attributesByName
                    GTA = lambda attributeID: self.dogmaLocation.dogmaStaticMgr.GetTypeAttribute2(slotOccupant.typeID, attributeID)
                    turretAddition = -GTA(attributesByName['turretHardPointModifier'].attributeID)
                    launcherAddition = -GTA(attributesByName['launcherHardPointModifier'].attributeID)
        turretAddition += typeAttributesByID.get(dogmaConst.attributeTurretHardpointModifier, 0.0)
        launcherAddition += typeAttributesByID.get(dogmaConst.attributeLauncherHardPointModifier, 0.0)
        return (turretAddition, launcherAddition)

    def OnDogmaAttributeChanged(self, shipID, itemID, attributeID, value):
        if shipID == self.GetItemID():
            if attributeID == const.attributeIsOnline:
                self.on_stats_changed()
                if itemID in self.dogmaLocation.dogmaItems:
                    dogmaItem = self.dogmaLocation.dogmaItems[itemID]
                    self.on_module_online_state(dogmaItem)
            if attributeID == const.attributeUpgradeSlotsLeft:
                self.on_stats_changed()
        if attributeID in (const.attributeIsOnline, const.attributeQuantity):
            try:
                dogmaItem = self.dogmaLocation.GetDogmaItem(itemID)
                flagID = dogmaItem.flagID
            except KeyError:
                if isinstance(itemID, tuple) and itemID[0] == self.GetItemID():
                    flagID = itemID[1]
                else:
                    return

            try:
                self.OnSlotAttributeChanged(flagID, shipID, itemID, attributeID, value)
            except KeyError:
                pass

    def OnPostCfgDataChanged(self, cfgname, entry, *args):
        if cfgname == 'evelocations' and entry[0] == self.GetItemID():
            self.on_name_changed()

    def OnDogmaDronesChanged(self):
        self.on_drones_changed()

    def OnGodmaFlushLocation(self, locationID):
        pass

    def OnFighterTubeTaskStatus(self, *args):
        self.on_stats_changed()

    def OnDroneControlLost(self, droneID):
        self.on_stats_changed()

    def OnDogmaItemChange(self, item, change):
        locationOrFlagIsInChange = const.ixFlag in change or const.ixLocationID in change
        didStacksizeFlagOrLocationChange = const.ixStackSize in change or locationOrFlagIsInChange
        if not didStacksizeFlagOrLocationChange:
            return
        oldLocationID = change.get(const.ixLocationID, None)
        if self.GetItemID() not in (oldLocationID, item.locationID):
            return
        if item.groupID in const.turretModuleGroups:
            self.on_hardpoints_fitted()
        updateSlotsAndStats = False
        if IsSubsystemBeingLoaded(change, item, self.itemID):
            self.on_subsystem_fitted(throttle=True)
            updateSlotsAndStats = True
        elif locationOrFlagIsInChange:
            updateSlotsAndStats = True
        if updateSlotsAndStats:
            self._UpdateSlots()
            self.on_stats_changed()

    def OnAttribute(self, attributeName, item, value, updateStats = 1):
        self.WaitForShip()
        try:
            self.GetService('godma').GetItem(item.itemID)
        except AttributeError:
            sys.exc_clear()
            return

        if updateStats:
            self.on_stats_changed()

    def OnAttributes(self, changeList):
        self.WaitForShip()
        slotsChanged = False
        for attributeName, item, value in changeList:
            if attributeName in ('hiSlots', 'medSlots', 'lowSlots'):
                slotsChanged = True

        self.on_stats_changed()
        if slotsChanged:
            self._UpdateSlots()

    def OnSkillsChanged(self, *args):
        self.on_stats_changed()

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if not self.IsSimulated():
            self.UpdateItem(shipID)

    def _OnSkinStateSet(self, itemID, skinState):
        if itemID != self.itemID:
            return
        self._skin = skinState
        self.on_skin_material_changed()

    def Close(self):
        self.on_stats_changed.clear()
        self.on_subsystem_fitted.clear()
        self.on_hardpoints_fitted.clear()
        self.on_new_itemID.clear()
        self.on_module_online_state.clear()
        self.on_item_ghost_fitted.clear()
        self.on_name_changed.clear()
        self.on_skin_material_changed.clear()
        self.on_stance_activated.clear()
        self.on_should_close.clear()
        self.on_slots_with_menu_changed.clear()
        self.on_controller_changing.clear()
        self.on_drones_changed.clear()
        for eachController in self.slotsByFlagID.values():
            eachController.Close()

        on_skin_state_set.disconnect(self._OnSkinStateSet)
        sm.UnregisterNotify(self)

    def OnDropData(self, dragObj, nodes):
        pass

    def OnStanceActive(self, shipID, stanceID):
        if self._itemID == shipID:
            self.on_stance_activated(stanceID)

    def WaitForShip(self):
        self.dogmaLocation.WaitForShip()

    def IsSwitchingShips(self):
        return self.dogmaLocation.IsSwitchingShips()

    def GetNumTurretsFitted(self):
        return self._GetNumHardpointsFitted(const.effectTurretFitted)

    def GetNumLaunchersFitted(self):
        return self._GetNumHardpointsFitted(const.effectLauncherFitted)

    def _GetNumHardpointsFitted(self, effect):
        hardpointsFitted = 0
        for module in self.GetFittedModules():
            if self.dogmaLocation.dogmaStaticMgr.TypeHasEffect(module.typeID, effect):
                hardpointsFitted += 1

        return hardpointsFitted

    def GetNumTurretHardpointsLeft(self):
        return self.GetAttribute(const.attributeTurretSlotsLeft)

    def GetNumLauncherHardpointsLeft(self):
        return self.GetAttribute(const.attributeLauncherSlotsLeft)

    def GetNumHiSlots(self):
        return self.GetAttribute(const.attributeHiSlots)

    def GetNumMedSlots(self):
        return self.GetAttribute(const.attributeMedSlots)

    def GetNumLowSlots(self):
        return self.GetAttribute(const.attributeLowSlots)

    def GetNumSubsystemSlots(self):
        if self.HasSubsystems():
            return NUM_SUBSYSTEM_SLOTS
        else:
            return 0

    def HasSubsystems(self):
        return bool(evetypes.GetTechLevel(self.GetTypeID()) > 2)

    def HasStance(self):
        return shipmode.ship_has_stances(self.GetTypeID())

    def StripFitting(self, prompt = True):
        if prompt and uicore.Message('AskStripShip', None, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
            return
        if self.IsSimulated():
            sm.GetService('ghostFittingSvc').UnfitAllModules()
        elif not IsControllingStructure():
            sm.GetService('invCache').StripFitting(self.GetItemID())

    def GetCharges(self):
        return self.dogmaLocation.GetSublocations(self.GetItemID())

    def GetModel(self):
        multiHullTypeIDList = GetMultiHullTypeIDList(self.typeID, self.itemID, self.dogmaLocation)
        return GetSkinnedShipModel(self._skin, self.typeID, multiHullTypeIDList)

    @property
    def model(self):
        return self.GetModel()

    @property
    def scenePath(self):
        if self.IsSimulated():
            return 'res:/dx9/scene/fitting/previewAmmo.red'
        else:
            return 'res:/dx9/scene/fitting/fitting.red'

    def GetPreviewFittedTypeID(self):
        if self.previewFittedItem:
            return self.previewFittedItem.typeID
        else:
            return None

    def GetPowerLoad(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def GetPowerOutput(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def GetCPULoad(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def GetCPUOutput(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def GetCalibrationLoad(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def GetCalibrationOutput(self):
        self.LogUseOfUnsupportedFunction('GetPowerLoad')

    def LogUseOfUnsupportedFunction(self, what):
        log.LogException("FittingController: This function (%s)is no longer supported and shouldn't be used" % what)

    def GetSlotController(self, flagID):
        return self.slotsByFlagID[flagID]

    def UpdateStats(self):
        self.on_stats_changed()

    def IsSimulated(self):
        return False

    def GetCurrentAttributeValues(self):
        return {}

    def IsFittableType(self, typeID):
        return False

    def SetSlotWithMenu(self, newFlagID):
        oldFlagID = self.slotFlagWithMenu
        self.slotFlagWithMenu = newFlagID
        self.on_slots_with_menu_changed(oldFlagID, newFlagID)

    def HasFighterBay(self):
        try:
            return self.dogmaLocation.GetAccurateAttributeValue(self.GetItemID(), const.attributeFighterCapacity)
        except KeyError as e:
            log.LogWarn('Failed to find an item when checking fighterbay, itemID = ', e)
            return False

    def IsControllerChanging(self, newItemID, newTypeID, oldItemID, oldTypeID):
        oldTypeID = oldTypeID or GetTypeIDForController(oldItemID)
        newTypeID = newTypeID or GetTypeIDForController(newItemID)
        if evetypes.GetCategoryID(oldTypeID) != evetypes.GetCategoryID(newTypeID):
            return True
        return False

    def UpdateSlotsByFlagID(self, newDict):
        self.slotsByFlagID.update(newDict)

    def ControllerForCategory(self):
        pass

    def HasNavigationPanel(self):
        return True

    def HasFuelPanel(self):
        return False

    def HasDronePanel(self):
        return True

    def IsValidItemAndSimulationState(self):
        if self.isShipSimulated and not isinstance(self._itemID, basestring):
            return False
        if not self.isShipSimulated and isinstance(self._itemID, basestring):
            return False
        return True

    def ChangeFittingWarningDisplay(self, warningSlotDict):
        pass


class ShipFittingController(GhostControllerMixin, FittingController):
    SLOT_CLASS = ShipFittingSlotController
    __notifyevents__ = GhostControllerMixin.__notifyevents__ + FittingController.__notifyevents__
    SLOTGROUPS = ((0, invConst.hiSlotFlags),
     (1, invConst.medSlotFlags),
     (2, invConst.loSlotFlags),
     (3, invConst.subsystemSlotFlags),
     (4, invConst.rigSlotFlags))

    def __init__(self, itemID, typeID = None):
        FittingController.__init__(self, itemID, typeID)
        GhostControllerMixin.__init__(self, itemID, typeID)

    def IsFittableType(self, typeID):
        return evetypes.GetCategoryID(typeID) in (const.categoryCharge, const.categorySubSystem, const.categoryModule)

    def ControllerForCategory(self):
        return const.categoryShip

    def GetStanceBtnControllerClass(self):
        if not self.IsValidItemAndSimulationState():
            return
        if self.IsSimulated():
            return GhostShipStanceButtonController
        return ShipStanceButtonController

    def SetPreviewFittedItem(self, ghostItem = None, force = False):
        if not self.IsSimulated():
            FittingController.SetPreviewFittedItem(self, ghostItem)
        else:
            GhostControllerMixin.SetPreviewFittedItem(self, ghostItem, force)

    def ChangeFittingWarningDisplay(self, warningSlotDict):
        self.on_warning_display_changed(warningSlotDict)


class StructureFittingController(GhostControllerMixin, FittingController):
    SLOT_CLASS = ShipFittingSlotController
    SLOT_CLASS_SERVICES = StructureFittingServiceSlotController
    __notifyevents__ = GhostControllerMixin.__notifyevents__ + FittingController.__notifyevents__
    SLOTGROUPS = ((0, invConst.hiSlotFlags),
     (1, invConst.medSlotFlags),
     (2, invConst.loSlotFlags),
     (4, invConst.rigSlotFlags),
     (-1, invConst.serviceSlotFlags))

    def __init__(self, itemID, typeID = None):
        FittingController.__init__(self, itemID, typeID)
        GhostControllerMixin.__init__(self, itemID, typeID)

    def IsFittableType(self, typeID):
        return evetypes.GetCategoryID(typeID) in (const.categoryStructureModule, const.categoryCharge)

    def GetSlotClass(self, flagID):
        if flagID in invConst.serviceSlotFlags:
            return self.SLOT_CLASS_SERVICES
        return self.SLOT_CLASS

    def ControllerForCategory(self):
        return const.categoryStructure

    def GetStanceBtnControllerClass(self):
        if not self.IsValidItemAndSimulationState():
            return
        if self.IsSimulated():
            return GhostShipStanceButtonController
        return ShipStanceButtonController

    def HasNavigationPanel(self):
        return False

    def HasFuelPanel(self):
        return True

    def HasDronePanel(self):
        return False

    def SetPreviewFittedItem(self, ghostItem = None, force = False):
        if not self.IsSimulated():
            FittingController.SetPreviewFittedItem(self, ghostItem)
        else:
            GhostControllerMixin.SetPreviewFittedItem(self, ghostItem, force)


def IsSubsystemBeingLoaded(change, item, itemID):
    locationOrFlagIsInChange = const.ixLocationID in change or const.ixFlag in change
    if not locationOrFlagIsInChange:
        return False
    if item.locationID != itemID:
        return False
    if not IsShipFittingFlag(item.flagID):
        return False
    if item.categoryID != const.categorySubSystem:
        return False
    return True
