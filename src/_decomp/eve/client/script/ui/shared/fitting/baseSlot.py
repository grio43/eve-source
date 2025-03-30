#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\baseSlot.py
import eveui
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_GML, ROLE_WORLDMOD
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui import const as uiconst
from menu import MenuLabel
from carbonui.primitives.transform import Transform
from carbonui.util.various_unsorted import GetAttrs, IsUnder
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors, CanFitFromSourceLocation
from eve.client.script.ui.shared.fitting.utilBtns import UtilBtnData
import inventorycommon.const as invConst
import eve.client.script.ui.shared.fittingScreen as fittingScreenConst
from inventorycommon.util import IsSubsystemFlagVisible
from signals.signalUtil import ChangeSignalConnect
from localization import GetByLabel
import localization
import blue
from carbonui.uicore import uicore
import trinity

class FittingSlotBase(Transform):
    slotActiveTexturePath = 'res:/UI/Texture/classes/Fitting/slotActive.png'
    slotPassiveTexturePath = 'res:/UI/Texture/classes/Fitting/slotPassive.png'
    slotOverheatedTexturePath = 'res:/UI/Texture/classes/Fitting/slotOverheated.png'
    slotsToHintDict = {}

    def ApplyAttributes(self, attributes):
        Transform.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.utilButtons = []
        self._emptyHint, self._emptyTooltip = self.PrimeToEmptySlotHint()
        self.ChangeSignalConnection()
        self.hilitedFromMathing = False
        self.ConstructFlagAndUnderlay()
        self.moduleSlotFill = None
        self.warningFill = None
        self.skillSprite = None
        self.fittingWarning = None

    def ConstructFlagAndUnderlay(self):
        pass

    def ConstructModuleSlotFill(self):
        pass

    def ConstructWarningFill(self):
        pass

    def ConstructSkillSprite(self):
        pass

    def ConstructFittingWarning(self):
        pass

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_online_state_change, self.UpdateOnlineDisplay), (self.controller.on_item_fitted, self.UpdateFitting)]
        ChangeSignalConnect(signalAndCallback, connect)

    def UpdateFitting(self):
        pass

    def DisableSlot(self):
        self.opacity = 0.1
        self.state = uiconst.UI_DISABLED
        self.flagIcon.state = uiconst.UI_HIDDEN
        self.UpdateGhostFittingIcons(None)
        self.Hilite(0)

    def EnableSlot(self):
        self.opacity = 1.0
        self.state = uiconst.UI_NORMAL
        self.flagIcon.state = uiconst.UI_DISABLED
        self.sr.underlay.display = True

    def HideSlot(self):
        self.state = uiconst.UI_HIDDEN

    def HideModuleSlotFill(self):
        self.HideElement(self.moduleSlotFill)

    def ColorUnderlay(self, color = None):
        a = self.sr.underlay.opacity
        r, g, b = color or (1.0, 1.0, 1.0)
        self.sr.underlay.SetRGBA(r, g, b, a)
        self.UpdateOnlineDisplay()

    def GetMenu(self):
        m = self.controller.GetMenu(self)
        if self.controller.GetModuleTypeID() and self.controller.GetModuleID():
            if eve.session.role & (ROLE_GML | ROLE_WORLDMOD):
                m += [(str(self.controller.GetModuleID()), self.CopyItemIDToClipboard, (self.controller.GetModuleID(),)), None]
            m += [(MenuLabel('UI/Commands/ShowInfo'), self.ShowInfo)]
            if self.controller.IsRigSlot():
                if self.controller.CanUnfitRigsWithoutDestroying():
                    m += self.controller.TryGetUnfitOption()
                else:
                    m += [(MenuLabel('UI/Fitting/Destroy'), self.controller.Unfit)]
            else:
                m += self.controller.TryGetUnfitOption()
                if self.controller.IsOnlineable():
                    if self.controller.IsOnline():
                        m.append((MenuLabel('UI/Fitting/PutOffline'), self.ToggleOnline))
                    else:
                        m.append((MenuLabel('UI/Fitting/PutOnline'), self.ToggleOnline))
        return m

    def OnClick(self, *args):
        if self.controller.GetModule():
            PlaySound(uiconst.SOUND_BUTTON_CLICK)
        return self.controller.OnClick(self)

    def ToggleOnline(self):
        self.controller.ToggleOnlineModule()
        self.UpdateOnlineDisplay()

    def CopyItemIDToClipboard(self, itemID):
        blue.pyos.SetClipboardData(str(itemID))

    def ShowInfo(self, *args):
        sm.GetService('info').ShowInfo(self.controller.GetModuleTypeID(), self.controller.GetModuleID())

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.Hilite(1)
        if self.controller.GetModule() is not None:
            self.ShowUtilButtons()
            if self.controller.IsOnlineable() and self.controller.IsOnline():
                self.ShowCpuAndPowergrid()
        else:
            self.hint = self._emptyHint

    def OnMouseExit(self, *args):
        self.Hilite(0)
        self.HideCpuAndPowergrid()

    def Hilite(self, state):
        if state:
            self.sr.underlay.opacity = 0.5
        else:
            self.sr.underlay.opacity = 0.3

    def GetDragData(self, *args):
        return self.controller.GetDragData()

    def HiliteIfMatching(self, flagID, powerType, itemTypeID):
        if flagID is None and powerType is None:
            if self.state != uiconst.UI_DISABLED and self.controller.DoesFitAsCharge(itemTypeID):
                self.SetHiliteFromMatching(1)
                return
        elif self.state != uiconst.UI_DISABLED and self.controller.GetModule() is None:
            if powerType is not None and self.controller.GetPowerType() == powerType:
                self.SetHiliteFromMatching(1)
                return
            if flagID is not None and self.controller.GetFlagID() == flagID:
                self.SetHiliteFromMatching(1)
                return
        self.SetHiliteFromMatching(0)

    def SetHiliteFromMatching(self, value):
        self.Hilite(value)
        self.hilitedFromMathing = value

    def SetFittingWarningColor(self, color):
        if color is None:
            if self.fittingWarning:
                self.fittingWarning.display = False
        else:
            self.ConstructFittingWarning()
            self.fittingWarning.display = True
            self.fittingWarning.SetRGBA(*color)

    def OnDropData(self, dragObj, nodes):
        if not CanFitFromSourceLocation(nodes):
            return
        self.controller.OnDropData(dragObj, nodes)

    def GetDroppedItems(self, nodes):
        items = []
        for node in nodes:
            if node.__guid__ in ('listentry.InvItem', 'xtriui.InvItem'):
                invType = node.rec
                if self.controller.IsFittableType(invType.typeID):
                    items.append(invType)

        return items

    def SetDragState(self):
        if not self.controller.GetModule() and not self.controller.GetCharge():
            self.DisableDrag()
        elif self.controller.SlotExists():
            self.EnableDrag()

    def PrimeToEmptySlotHint(self):
        flagID = self.controller.GetFlagID()
        slotKey = self.GetSlotKey(flagID)
        if slotKey is None or slotKey not in self.slotsToHintDict:
            return (GetByLabel('UI/Fitting/EmptySlot'), '')
        labelPath, tooltipName = self.slotsToHintDict[slotKey]
        return (GetByLabel(labelPath), tooltipName)

    def GetSlotKey(self, flagID):
        if flagID in invConst.hiSlotFlags:
            return 'hiSlot'
        if flagID in invConst.medSlotFlags:
            return 'medSlot'
        if flagID in invConst.loSlotFlags:
            return 'loSlot'
        if IsSubsystemFlagVisible(flagID):
            return 'subSystemSlot'
        if flagID in invConst.rigSlotFlags:
            return 'rigSlot'

    @eveui.skip_if_destroyed
    def UpdateOnlineDisplay(self):
        if self.controller.parentController.GetItemID() == self.controller.dogmaLocation.shipIDBeingDisembarked:
            return
        if self.controller.GetModule() is not None and self.controller.IsOnlineable():
            if self.controller.IsOnline():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
                if GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOnline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOffline')
            else:
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 0.25)
                if GetAttrs(self, 'sr', 'onlineButton') and self.sr.onlineButton.hint == localization.GetByLabel('UI/Fitting/PutOffline'):
                    self.sr.onlineButton.hint = localization.GetByLabel('UI/Fitting/PutOnline')
        elif self.flagIcon:
            if self.controller.GetModule() is None or self.controller.SlotExists():
                self.flagIcon.SetRGBA(1.0, 1.0, 1.0, 1.0)
            else:
                self.flagIcon.SetRGBA(0.7, 0.0, 0.0, 0.5)

    def GetRigsBtns(self):
        if self.controller.CanUnfitRigsWithoutDestroying():
            removeLabel = localization.GetByLabel('UI/Fitting/Unfit')
        else:
            removeLabel = localization.GetByLabel('UI/Fitting/Destroy')
        btns = [UtilBtnData(removeLabel, 'ui_38_16_200', self.controller.Unfit, 1, 0), UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0)]
        return btns

    def GetModuleBtns(self, isOnlinable):
        if bool(self.controller.IsOnline):
            toggleLabel = localization.GetByLabel('UI/Fitting/PutOffline')
        else:
            toggleLabel = localization.GetByLabel('UI/Fitting/PutOnline')
        btns = [UtilBtnData(localization.GetByLabel('UI/Fitting/UnfitModule'), 'ui_38_16_200', self.controller.UnfitModule, 1, 0), UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0), UtilBtnData(toggleLabel, 'ui_38_16_207', self.ToggleOnline, isOnlinable, 1)]
        return btns

    @eveui.skip_if_destroyed
    def ShowUtilButtons(self, *args):
        flagID = self.controller.GetFlagID()
        self.controller.parentController.SetSlotWithMenu(flagID)
        for button in self.utilButtons:
            button.SetBtnColorBasedOnIsActive()

        self.utilButtonsTimer = AutoTimer(500, self.HideUtilButtons)

    @eveui.skip_if_destroyed
    def HideUtilButtons(self, force = 0):
        mo = uicore.uilib.mouseOver
        if not force and (mo in self.utilButtons or mo == self or IsUnder(mo, self)):
            return
        for button in self.utilButtons:
            button.Hide()

        self.utilButtonsTimer = None
        self.HideCpuAndPowergrid()

    def ShowCpuAndPowergrid(self):
        if self.controller:
            self.controller.GetCpuAndPowergridUsage()

    def HideCpuAndPowergrid(self):
        if self.controller:
            self.controller.HideCpuAndPowergridUsage()

    def SetTexurePathForActivatable(self):
        self.SetModuleSlotPathAndState(self.slotActiveTexturePath)

    def SetTexturePathForPassive(self):
        self.SetModuleSlotPathAndState(self.slotPassiveTexturePath)

    def SetTexturePathForOverheated(self):
        self.SetModuleSlotPathAndState(self.slotOverheatedTexturePath)

    def HideElement(self, element):
        if element:
            element.display = False

    def UpdateGhostFittingIcons(self, invItem):
        self.controller.UpdateGhostFittingIcons(self, invItem)

    def UpdateStatusDisplay(self):
        self.controller.UpdateStatusDisplay(self)

    def SetModuleSlotPathAndState(self, texturePath):
        self.ConstructModuleSlotFill()
        self.moduleSlotFill.SetTexturePath(texturePath)
        self.moduleSlotFill.display = True

    def SetStatusDisplayOffline(self):
        self.flagIcon.SetAlpha(0.25)
        self.moduleSlotFill.SetRGBA(*fittingScreenConst.OFFLINE_COLOR)
        self.sr.underlay.display = False

    def SetStatusDisplayOnline(self):
        newAlpha = getattr(self.flagIcon, 'fullAlphaValue', None) or 1.0
        self.flagIcon.SetAlpha(newAlpha)
        self.moduleSlotFill.SetRGBA(*fittingScreenConst.ONLINE_COLOR)
        self.sr.underlay.display = False

    def SetStatusDisplayActive(self):
        newAlpha = getattr(self.flagIcon, 'fullAlphaValue', None) or 1.0
        self.flagIcon.SetAlpha(newAlpha)
        self.ConstructModuleSlotFill()
        self.moduleSlotFill.SetRGBA(*fittingScreenConst.ACTIVE_COLOR)
        self.sr.underlay.display = False

    def SetStatusDisplayOverheated(self):
        newAlpha = getattr(self.flagIcon, 'fullAlphaValue', None) or 1.0
        self.flagIcon.SetAlpha(newAlpha)
        self.ConstructModuleSlotFill()
        self.moduleSlotFill.SetRGBA(*fittingScreenConst.OVERHEATED_COLOR)
        self.sr.underlay.display = False

    def ChangeWarningDisplay(self, isOn = False):
        if isOn:
            self.ConstructWarningFill()
            self.warningFill.display = True
        elif self.warningFill:
            self.HideElement(self.warningFill)

    def SetIconAsPreview(self):
        flagIcon = self.flagIcon
        flagIcon.spriteEffect = trinity.TR2_SFX_SOFTLIGHT
        flagIcon.saturation = 0.1
        flagIcon.SetRGBA(80 / 255.0, 150 / 255.0, 255 / 255.0, flagIcon.GetAlpha())

    def SetIconNotAsPreview(self):
        flagIcon = self.flagIcon
        flagIcon.spriteEffect = trinity.TR2_SFX_COPY
        flagIcon.saturation = 1.0
        if self.controller.GetModule() is None or self.controller.SlotExists():
            flagIcon.SetRGBA(1, 1, 1, flagIcon.GetAlpha())
            flagIcon.fullAlphaValue = 1.0
        else:
            flagIcon.SetRGBA(0.7, 0.0, 0.0, 0.75)
            flagIcon.fullAlphaValue = 0.75

    def HideGhostFittingElement(self):
        self.HideElement(self.moduleSlotFill)
        self.sr.underlay.display = True

    def Close(self):
        with EatSignalChangingErrors(errorMsg='FittingSlotBase'):
            self.ChangeSignalConnection(connect=False)
        Transform.Close(self)
        self.controller = None
