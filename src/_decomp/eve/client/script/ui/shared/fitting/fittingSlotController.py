#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingSlotController.py
import sys
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from menu import MenuLabel
import eve.client.script.ui.shared.fittingScreen.slotControllerGhostFittingExtension as ghostHelpers
from eve.common.script.sys.eveCfg import IsControllingStructure, IsDocked
from inventorycommon.util import IsSubsystemFlagVisible, ShipCanUnfitRigs
import signals
from carbon.common.script.util.logUtil import LogException
from carbonui import const as uiconst
from eve.client.script.ui.shared.fitting.fittingUtil import GetPowerType
from inventorycommon import const as invConst
from inventoryrestrictions import can_be_unfitted, ItemCannotBeUnfitted
from carbonui.uicore import uicore

class FittingSlotController(object):

    def __init__(self, flagID, parentController):
        self.flagID = flagID
        self.moduleItemID = None
        self.chargeItemID = None
        self.parentController = parentController
        self.failedModuleTypeID = None
        self.on_online_state_change = signals.Signal(signalName='on_online_state_change')
        self.on_item_fitted = signals.Signal(signalName='on_item_fitted')

    @property
    def dogmaModuleItem(self):
        if self.moduleItemID:
            return self.dogmaLocation.SafeGetDogmaItem(self.moduleItemID)
        else:
            return None

    @dogmaModuleItem.setter
    def dogmaModuleItem(self, _value):
        LogException('Setting dogmaModuleItem, no one should be doing that!')

    @property
    def dogmaChargeItem(self):
        if self.chargeItemID:
            return self.dogmaLocation.SafeGetDogmaItem(self.chargeItemID)
        else:
            return None

    @dogmaChargeItem.setter
    def dogmaChargeItem(self, _value):
        LogException('Setting dogmaChargeItem, no one should be doing that!')

    @property
    def dogmaLocation(self):
        return self.parentController.GetDogmaLocation()

    @dogmaLocation.setter
    def dogmaLocation(self, _value):
        LogException('Setting dogmaLocation, no one should be doing that!')

    def SetModuleAndChargeIDs(self, moduleItemID, chargeItemID):
        self.moduleItemID = moduleItemID
        self.chargeItemID = chargeItemID

    def GetFailedTypeID(self):
        return self.failedModuleTypeID

    def SetFailedTypeID(self, typeID):
        self.failedModuleTypeID = typeID

    def GetParentID(self):
        return self.parentController.GetItemID()

    def CurrentShipIsLoaded(self):
        if not self.parentController:
            return False
        return self.parentController.CurrentShipIsLoaded()

    def GetPowerType(self):
        return GetPowerType(self.flagID)

    def GetFlagID(self):
        return self.flagID

    def Close(self):
        self.on_online_state_change.clear()
        self.on_item_fitted.clear()
        self.parentController = None

    def GetModule(self):
        return self.dogmaModuleItem

    def GetModuleID(self):
        return self.moduleItemID

    def GetModuleTypeID(self):
        if self.dogmaModuleItem:
            return self.dogmaModuleItem.typeID

    def GetCharge(self):
        return self.dogmaChargeItem

    def GetChargeQuantity(self):
        if self.moduleItemID:
            self.dogmaLocation.GetQuantity(self.moduleItemID)
        return 0

    def IsChargeable(self):
        return bool(self.dogmaModuleItem and self.dogmaModuleItem.groupID in cfg.__chargecompatiblegroups__)

    def DoesFitAsCharge(self, chargeTypeID):
        if not chargeTypeID or not self.GetModule() or evetypes.GetCategoryID(chargeTypeID) != invConst.categoryCharge:
            return False
        usedWith = sm.GetService('info').GetUsedWithTypeIDs(chargeTypeID)
        if usedWith and self.GetModuleTypeID() in usedWith:
            return True
        return False

    def GetChargeCapacity(self):
        return self.dogmaLocation.GetCapacity(self.GetModule().locationID, const.attributeCapacity, self.GetFlagID())

    def FitCharges(self, items):
        if self.IsSimulated():
            ghostHelpers.FitCharges(self.flagID, items)
            self.on_item_fitted()
            return
        for chargeItem in items:
            if isinstance(chargeItem.itemID, tuple):
                itemID = self.dogmaLocation.UnloadAmmoToContainer(session.shipid, chargeItem, (session.shipid, session.charid, const.flagCargo))
                if itemID:
                    chargeItem.itemID, chargeItem.locationID, chargeItem.flagID = itemID[0], session.shipid, const.flagCargo

        chargeTypeID = items[0].typeID
        self.dogmaLocation.DropLoadChargeToModule(self.GetModuleID(), chargeTypeID, items)

    def IsSimulated(self):
        return self.parentController.IsSimulated()

    def RaiseErrorIfCannotUnfit(self):
        typeID = self.GetModuleTypeID()
        if not can_be_unfitted(typeID):
            raise ItemCannotBeUnfitted(type_ids=[typeID])

    def UnfitCharge(self):
        self.RaiseErrorIfCannotUnfit()
        if self.IsSimulated():
            return ghostHelpers.UnfitFromSlot(self.GetCharge(), None)
        moduleID = self.GetModuleID()
        if moduleID is None:
            return
        if self.IsInWeaponBank():
            moduleID = self.dogmaLocation.GetMasterModuleForFlag(session.shipid, self.GetFlagID())
        if IsDocked():
            destination = (session.structureid or session.stationid, session.charid, const.flagHangar)
        elif IsControllingStructure():
            destination = (session.shipid, sm.GetService('structureDirectory').GetStructureInfo(session.shipid).ownerID, const.flagCargo)
        else:
            destination = (session.shipid, session.charid, const.flagCargo)
        self.dogmaLocation.UnloadAmmoFromModules(session.shipid, moduleID, destination)

    def FitModule(self, item):
        self.dogmaLocation.TryFit(item, self.flagID)
        PlaySound(uiconst.SOUND_ADD_OR_USE)

    def ShouldShowUnfitOption(self):
        if not can_be_unfitted(type_id=self.GetModuleTypeID()):
            return False
        if self.IsSimulated():
            return True
        if any([session.stationid, session.structureid]):
            return True
        return False

    def TryGetUnfitOption(self):
        if self.ShouldShowUnfitOption():
            return self._GetUnfitOption()
        return []

    def _GetUnfitOption(self):
        m = []
        if self.GetCharge():
            m += [(MenuLabel('UI/Fitting/RemoveCharge'), self.UnfitCharge)]
        m += [(MenuLabel('UI/Fitting/Unfit'),
          self.UnfitModule,
          (),
          None,
          None,
          'Unfit')]
        return m

    def UnfitModule(self, *args):
        self.RaiseErrorIfCannotUnfit()
        if self.IsSimulated():
            return ghostHelpers.UnfitFromSlot(None, self.GetModule())
        if self.GetModule() is None:
            return
        parentID = self.GetParentID()
        if parentID is None:
            return
        masterID = self.IsInWeaponBank()
        invCache = sm.GetService('invCache')
        if masterID:
            ret = eve.Message('ClearGroupModule', {}, uiconst.YESNO, suppress=uiconst.ID_YES)
            if ret != uiconst.ID_YES:
                return
            if self.GetModule():
                self.GetModule().dogmaLocation.UngroupModule(parentID, masterID)
        if self.GetCharge() is not None:
            self.UnfitCharge()
        if session.stationid or session.structureid:
            invCache.GetInventory(const.containerHangar).Add(self.GetModuleID(), parentID, flag=const.flagHangar)
        else:
            shipInv = invCache.GetInventoryFromId(parentID, locationID=session.stationid)
            shipInv.Add(self.GetModuleID(), parentID, qty=None, flag=const.flagCargo)
        PlaySound(uiconst.SOUND_REMOVE)

    def Unfit(self, *args):
        self.RaiseErrorIfCannotUnfit()
        if self.IsSimulated():
            return ghostHelpers.UnfitFromSlot(self.GetCharge(), self.GetModule())
        parentID = self.GetParentID()
        if parentID is None:
            return
        invCache = sm.GetService('invCache')
        parentInv = invCache.GetInventoryFromId(parentID, locationID=session.stationid)
        if self.GetPowerType() == const.effectRigSlot:
            if self.CanUnfitRigsWithoutDestroying():
                self.UnfitModule()
            else:
                ret = eve.Message('RigUnFittingInfo', {}, uiconst.OKCANCEL)
                if ret != uiconst.ID_OK:
                    return
                parentInv.DestroyFitting(self.GetModuleID())
        elif self.GetCharge():
            self.UnfitCharge()
        else:
            self.UnfitModule()

    def CanUnfitRigsWithoutDestroying(self):
        if self.parentController.ControllerForCategory() == invConst.categoryShip:
            if ShipCanUnfitRigs(self.parentController.GetTypeID()):
                return True
        return False

    def IsGroupable(self):
        return self.GetModule().groupID in const.dgmGroupableGroupIDs

    def GetDragData(self):
        l = []
        if self.dogmaChargeItem:
            l.extend(self.GetChargeDragNodes())
        if l:
            return l
        if self.GetModule() is None:
            return l
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if shift:
            if self.IsGroupable():
                sm.ScatterEvent('OnStartSlotLinkingMode', self.GetModule().typeID)
            elif not self.IsSimulated():
                return []
        return self.GetModuleDragData()

    def GetModuleDragData(self):
        return self.dogmaLocation.GetDragData(self.GetModuleID())

    def GetChargeDragNodes(self, *args):
        return self.dogmaLocation.GetDragData(self.chargeItemID)

    def SlotExists(self):
        if not self.CurrentShipIsLoaded():
            return
        if self.IsSubsystemSlot():
            if self.parentController.HasStance() or not self.parentController.HasSubsystems():
                return False
        return self.dogmaLocation.SlotExists(self.GetParentID(), self.flagID)

    def IsSubsystemSlot(self):
        return IsSubsystemFlagVisible(self.flagID)

    def IsOnlineable(self):
        if not self.GetModule() or not self.SlotExists():
            return False
        try:
            return const.effectOnline in self.dogmaLocation.dogmaStaticMgr.effectsByType[self.GetModuleTypeID()]
        except ReferenceError:
            pass

    def IsOnline(self):
        return self.GetModule().IsOnline()

    def OnlineModule(self):
        self.dogmaLocation.OnlineModule(self.GetModuleID())

    def OfflineModule(self):
        self.dogmaLocation.OfflineModule(self.GetModuleID())

    def IsInWeaponBank(self, item = None):
        if not item:
            return self.dogmaLocation.IsInWeaponBank(self.GetModule().locationID, self.GetModuleID())
        else:
            return self.dogmaLocation.IsInWeaponBank(item.locationID, item.itemID)

    def GetWeaponBankChargeIDs(self):
        return self.dogmaLocation.GetSubLocationsInBank(self.GetParentID(), self.GetCharge().itemID)

    def GetWeaponBankCrystalIDs(self):
        return self.dogmaLocation.GetCrystalsInBank(self.GetParentID(), self.GetCharge().itemID)

    def LinkWithWeapon(self, item):
        self.dogmaLocation.LinkWeapons(self.GetModule().locationID, self.GetModuleID(), item.itemID)

    def DestroyWeaponBank(self):
        masterID = self.IsInWeaponBank()
        if masterID:
            self.dogmaLocation.DestroyWeaponBank(self.GetModule().locationID, masterID)

    def ToggleOnlineModule(self):
        if self.IsOnline():
            if self.IsInWeaponBank():
                ret = eve.Message('QueryGroupOffline', {}, uiconst.YESNO, suppress=uiconst.ID_YES)
                if ret != uiconst.ID_YES:
                    return
            self.OfflineModule()
        else:
            self.OnlineModule()

    def IsRigSlot(self):
        return self.flagID in invConst.rigSlotFlags

    def OnSlotAttributeChanged(self, parentID, itemID, attributeID, value):
        try:
            if self.GetModule() is not None and self.GetModuleID() == itemID and attributeID == const.attributeIsOnline:
                self.on_online_state_change()
            elif attributeID == const.attributeQuantity:
                if not isinstance(itemID, tuple):
                    return
                parentID, flagID, typeID = itemID
                if parentID != self.GetParentID() or flagID != self.GetFlagID():
                    return
                if not value:
                    self.chargeItemID = None
                self.on_item_fitted()
        except ReferenceError:
            self.chargeItemID = None
            sys.exc_clear()

    def IsModulePreviewModule(self):
        return False

    def IsFittableType(self, typeID):
        return self.parentController.IsFittableType(typeID)

    def GetMenu(self):
        return []
