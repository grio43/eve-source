#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\slotControllerGhostFittingExtension.py
import carbonui.const as uiconst
from carbonui.uicore import uicore

def FitCharges(flagID, chargeItems):
    chargeTypeID = chargeItems[0].typeID
    ghostFittingSvc = sm.GetService('ghostFittingSvc')
    chargeItem = ghostFittingSvc.FitAmmoToLocation(flagID, chargeTypeID)
    if chargeItem:
        _TryUnfitChargeFromOldLocation(chargeItems)
    ghostFittingSvc.SendFittingSlotsChangedEvent()


def _TryUnfitChargeFromOldLocation(chargeItems):
    if len(chargeItems) != 1:
        return
    item = chargeItems[0]
    itemID = getattr(item, 'itemID', None)
    wasFitted = getattr(item, 'isFitted', False)
    if wasFitted and itemID and not uicore.uilib.Key(uiconst.VK_SHIFT):
        sm.GetService('ghostFittingSvc').UnfitModule(itemID)


def UnfitFromSlot(charge, module):
    itemID = None
    if charge:
        itemID = charge.itemID
    elif module:
        itemID = module.itemID
    if itemID:
        _UnfitModuleOrAmmo(itemID)


def _UnfitModuleOrAmmo(itemID):
    ghostFittingSvc = sm.GetService('ghostFittingSvc')
    ghostFittingSvc.UnfitModule(itemID)
