#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\fittingSlotController.py
import dogma.data as dogma_data
import eveicon
import evetypes
import uthread
from carbonui.control.contextMenu.menuEntryData import MenuEntryData
from menu import MenuLabel
from eve.client.script.ui.shared.fitting.fittingSlotController import FittingSlotController
from eve.client.script.ui.shared.fitting.fittingUtil import RigFittingCheck, IsCharge
from eve.client.script.ui.shared.fittingScreen import OFFLINE, ONLINE, ACTIVE, OVERHEATED
from eve.client.script.ui.shared.fittingScreen.fittingUtil import GetOriginalItemID
from eve.common.script.sys.eveCfg import IsDocked
from localization import GetByLabel
from shipfitting.errorConst import WRONG_SLOT
from shipfitting.fittingStuff import IsRightSlotForType, IsFittable
from signals import Signal
import carbonui.const as uiconst
from utillib import KeyVal
from carbonui.uicore import uicore

class ShipFittingSlotController(FittingSlotController):

    def __init__(self, flagID, parentController):
        FittingSlotController.__init__(self, flagID, parentController)

    def GetModule(self):
        if self.IsModulePreviewModule():
            return None
        return self.dogmaModuleItem

    def GetModuleOrPreview(self):
        return self.dogmaModuleItem

    def IsModulePreviewModule(self):
        if not self.dogmaModuleItem:
            return False
        if getattr(self.dogmaModuleItem, 'isPreviewItem', False):
            return True
        return False

    def Add(self, item, sourceLocation = None):
        if self.IsSimulated():
            return self.AddSimulatedItem(item)
        else:
            guid = getattr(item, '__guid__', None)
            if guid is None and item.itemID or guid in ('listentry.InvItem', 'xtriui.InvItem'):
                return self.AddRealItem(item)
            sm.GetService('ghostFittingSvc').LoadCurrentShip()
            return self.AddSimulatedItem(item)

    def AddSimulatedItem(self, item):
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        if not IsRightSlotForType(self.dogmaLocation.dogmaStaticMgr, item.typeID, self.flagID):
            ghostFittingSvc.SendOnFeedbackTextChanged(KeyVal(errorKey=WRONG_SLOT, extraInfo=None), timeout=True)
            return
        shipID = self.GetParentID()
        wasUnfitted = self._TryUnfitModule(ghostFittingSvc, item)
        originalItemID = GetOriginalItemID(item.itemID)
        dogmaItem, errorInfo = ghostFittingSvc.FitModuleToShipAndChangeState(shipID, self.GetFlagID(), item.typeID, originalItemID=originalItemID)
        if dogmaItem:
            ghostFittingSvc.SendFittingSlotsChangedEvent()
        else:
            flagID = getattr(item, 'flagID', None)
            if wasUnfitted and flagID:
                ghostFittingSvc.FitModuleToShipAndChangeState(shipID, flagID, item.typeID, originalItemID=originalItemID)
            ghostFittingSvc.SendOnFeedbackTextChanged(errorInfo, timeout=True)

    def _TryUnfitModule(self, ghostFittingSvc, item):
        itemID = getattr(item, 'itemID', None)
        wasFitted = getattr(item, 'isFitted', False)
        if wasFitted and itemID and not uicore.uilib.Key(uiconst.VK_SHIFT):
            return sm.GetService('ghostFittingSvc').UnfitModule(itemID)

    def AddRealItem(self, item):
        if not getattr(item, 'typeID', None):
            return
        if not RigFittingCheck(item, self.parentController.GetTypeID()):
            return
        validFitting = False
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        for effect in dogma_data.get_type_effects(item.typeID):
            if not IsFittable(effect.effectID):
                continue
            validFitting = True
            if effect.effectID == self.GetPowerType():
                isFitted = item.locationID == self.GetParentID() and item.flagID != const.flagCargo
                if isFitted and shift and self.GetModule():
                    if self.GetModule().typeID == item.typeID:
                        self.LinkWithWeapon(item)
                        return
                    else:
                        uicore.Message('CustomNotify', {'notify': GetByLabel('UI/Fitting/GroupingIncompatible')})
                        return
                self.FitModule(item)
                return
            msgDict = {'item': evetypes.GetName(item.typeID),
             'slotpower': dogma_data.get_effect_display_name(self.GetPowerType()),
             'itempower': dogma_data.get_effect_display_name(effect.effectID)}
            uicore.Message('ItemDoesntFitPower', msgDict)

        if not validFitting:
            raise UserError('ItemNotHardware', {'itemname': item.typeID})

    def OnDropData(self, dragObj, nodes):
        if self.GetModule() is not None and not self.SlotExists():
            return
        items, fakeItems = self.GetDroppedItems(nodes)
        allItems = items + fakeItems
        chargeTypeID = None
        chargeItems = []
        for item in allItems:
            if not getattr(item, 'typeID', None):
                return
            if IsCharge(item.typeID):
                if self.IsChargeable():
                    if chargeTypeID is None:
                        chargeTypeID = item.typeID
                    if chargeTypeID == item.typeID:
                        chargeItems.append(item)
            else:
                uthread.new(self.Add, item)

        if len(chargeItems):
            if fakeItems and not self.IsSimulated():
                sm.GetService('ghostFittingSvc').LoadCurrentShip()
            self.FitCharges(chargeItems)

    def GetDroppedItems(self, nodes):
        items = []
        fakeItems = []
        for node in nodes:
            guid = getattr(node, '__guid__', None)
            if guid in ('listentry.InvItem', 'xtriui.InvItem'):
                invType = node.rec
                if self.IsFittableType(invType.typeID):
                    items.append(invType)
            elif guid in ('listentry.GenericMarketItem', 'listentry.Item', 'listentry.FittingModuleEntry'):
                if self.IsFittableType(node.typeID):
                    fakeItems.append(KeyVal(typeID=node.typeID, itemID=getattr(node, 'itemID', None), isFitted=getattr(node, 'isFitted', False), flagID=getattr(node, 'flagID', None)))

        return (items, fakeItems)

    def GetMenu(self, slot):
        m = []
        flagID = self.GetFlagID()
        if flagID in const.moduleSlotFlags + const.rigSlotFlags:
            m += [(MenuLabel('UI/Fitting/FittingWindow/SetFiltersForSlot'), sm.ScatterEvent, ('OnFittingFlagFilterSet', flagID))]
        typeID = self.GetModuleTypeID()
        if typeID and self.GetModuleID():
            m += [(MenuLabel('UI/Fitting/FittingWindow/FindTypeInBrowser'), sm.ScatterEvent, ('OnFindTypeInList', typeID))]
            sm.GetService('marketutils').AddMarketDetailsMenuOption(m, typeID)
            m += self.GetGroupMenu()
        elif self.GetFailedTypeID():
            m += [(MenuLabel('UI/Fitting/FittingWindow/ClearSlot'), self.ClearFailedSlot, (slot,))]
        return m

    def ClearFailedSlot(self, slot):
        self.SetFailedTypeID(None)
        self.UpdateStatusDisplay(slot)

    def _GetUnfitOption(self):
        return [MenuEntryData(MenuLabel('UI/Fitting/Unfit'), self.Unfit, texturePath=eveicon.close)]

    def GetGroupMenu(self, *args):
        masterID = self.IsInWeaponBank()
        if masterID:
            return [(MenuLabel('UI/Fitting/ClearGroup'), self.DestroyWeaponBank, ())]
        return []

    def OnClick(self, slot):
        if self.GetModule() is None:
            flagID = self.GetFlagID()
            if flagID in const.moduleSlotFlags + const.rigSlotFlags:
                sm.ScatterEvent('OnFittingFlagFilterSet', flagID)
                return
        if self.IsSimulated():
            return self.OnClickSimulated(slot)
        if not self._ShouldContinueAfterOfflineWarning():
            return
        self.ToggleOnlineModule()

    def _ShouldContinueAfterOfflineWarning(self):
        if not self.IsOnlineable():
            return False
        if IsDocked():
            return True
        if not self.IsOnline():
            return True
        if eve.Message('PutOffline', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            return True
        return False

    def OnClickSimulated(self, slot):
        if self.GetModule() is None:
            return
        typeID = self.GetModuleTypeID()
        itemKey = self.GetModuleID()
        flagID = self.GetFlagID()
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        if flagID not in const.rigSlotFlags and not self.IsOnlineable():
            if self.IsOnline():
                ghostFittingSvc.OfflineSlotList([flagID])
        else:
            ghostFittingSvc.SwitchBetweenModes(itemKey, typeID, flagID)
        self.UpdateStatusDisplay(slot)

    def UpdateStatusDisplay(self, slot):
        slot.SetIconNotAsPreview()
        if not self.IsSimulated():
            slot.HideModuleSlotFill()
            slot.ChangeWarningDisplay(False)
            return
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        itemKey = self.GetModuleID()
        typeID = self.GetModuleTypeID()
        flagID = self.GetFlagID()
        slot.ChangeWarningDisplay(bool(self.GetFailedTypeID()))
        if itemKey is None or typeID is None:
            slot.HideModuleSlotFill()
            return
        if self.IsModulePreviewModule():
            slot.SetIconAsPreview()
        typeEffectInfo = ghostFittingSvc.GetDefaultAndOverheatEffect(typeID)
        currentStatus = ghostFittingSvc.GetModuleStatus(itemKey, typeID, flagID)
        if currentStatus is None:
            return
        if typeEffectInfo.defaultEffect and typeEffectInfo.isActivatable:
            if currentStatus == OVERHEATED:
                slot.SetTexturePathForOverheated()
            else:
                slot.SetTexurePathForActivatable()
        else:
            slot.SetTexturePathForPassive()
        if currentStatus == OFFLINE:
            slot.SetStatusDisplayOffline()
        elif currentStatus == ONLINE:
            slot.SetStatusDisplayOnline()
        elif currentStatus == ACTIVE:
            slot.SetStatusDisplayActive()
        elif currentStatus == OVERHEATED:
            slot.SetStatusDisplayOverheated()

    def ShowChargeInfo(self, *args):
        if self.GetCharge():
            sm.GetService('info').ShowInfo(self.GetCharge().typeID, self.GetCharge().itemID)

    def UpdateGhostFittingIcons(self, slot, invItem):
        if not self.IsSimulated() or not invItem:
            slot.HideGhostFittingElement()

    def GetCpuAndPowergridUsage(self):
        if not self.GetModuleID() or self.parentController is None:
            return
        cpu = self.dogmaLocation.GetAttributeValue(self.GetModuleID(), const.attributeCpu)
        powergrid = self.dogmaLocation.GetAttributeValue(self.GetModuleID(), const.attributePower)
        calibration = self.dogmaLocation.GetAttributeValue(self.GetModuleID(), const.attributeUpgradeCost)
        self.parentController.OnPreviewCPU(cpu, powergrid, calibration)

    def HideCpuAndPowergridUsage(self):
        if self.parentController:
            self.parentController.OnPreviewCPU(0, 0, 0)

    def ToggleOnlineModule(self):
        if not self.IsSimulated():
            return FittingSlotController.ToggleOnlineModule(self)
        if self.IsOnline():
            newState = OFFLINE
        else:
            newState = ONLINE
        ghostFittingSvc = sm.GetService('ghostFittingSvc')
        ghostFittingSvc.PerformActionAndSetNewState(newState, self.GetModuleID(), self.GetModuleTypeID(), self.GetFlagID())
        ghostFittingSvc.SendFittingSlotsChangedEvent()
