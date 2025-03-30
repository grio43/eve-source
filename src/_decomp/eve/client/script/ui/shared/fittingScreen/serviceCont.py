#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\serviceCont.py
import dogma.data as dogma_data
import evetypes
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from dogma.const import effectRigSlot
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.shared.fitting.baseSlot import FittingSlotBase
from eve.client.script.ui.shared.fitting.fittingUtil import EatSignalChangingErrors, GetScaleFactor
import carbonui.const as uiconst
from eve.client.script.ui.shared.fitting.utilBtns import FittingUtilBtn
from localization import GetByLabel
from carbonui.uicore import uicore
import inventorycommon.const as invConst
from signals.signalUtil import ChangeSignalConnect

class FittingServiceSlot(FittingSlotBase):
    __guid__ = 'FittingServiceSlot'
    SLOT_SIZE = 48
    default_align = uiconst.BOTTOMLEFT
    default_height = SLOT_SIZE
    default_width = SLOT_SIZE
    isDragObject = True
    underlayTexturePath = 'res:/UI/Texture/classes/Fitting/stationServiceSlotFrame.png'
    slotPassiveTexturePath = 'res:/UI/Texture/classes/Fitting/slotPassive_Structure.png'
    slotActiveTexturePath = 'res:/UI/Texture/classes/Fitting/serviceSlotGlowOuter2.png'

    def ApplyAttributes(self, attributes):
        FittingSlotBase.ApplyAttributes(self, attributes)
        self.UpdateFitting()

    def ConstructFlagAndUnderlay(self):
        self.sr.underlay = Sprite(bgParent=self, name='underlay', state=uiconst.UI_DISABLED, padding=(0, 0, 0, 0), texturePath=self.underlayTexturePath)
        self.flagIcon = Icon(parent=self, name='flagIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.width, height=self.height)

    def ConstructModuleSlotFill(self):
        if self.moduleSlotFill:
            return
        self.moduleSlotFill = Sprite(parent=self, name='moduleSlotFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(0, 0, 0, 0), texturePath=self.slotActiveTexturePath, color=(1, 1, 1, 0.5))
        self.moduleSlotFill.display = False

    def ConstructWarningFill(self):
        if self.warningFill and not self.warningFill.destroyed:
            return
        self.warningFill = Sprite(parent=self, name='moduleSlotFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-4, -4, -4, -4), texturePath=self.slotPassiveTexturePath, color=(1.0, 0.35, 0.0))
        self.warningFill.display = False

    def ConstructSkillSprite(self):
        if self.skillSprite:
            return
        self.skillSprite = Sprite(parent=self, name='skillSprite', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/slotGlowInner.png', color=(1, 1, 1, 0.5))
        self.skillSprite.display = False

    def UpdateFitting(self):
        if not self.controller.SlotExists() and not self.controller.GetModuleOrPreview():
            self.DisableSlot()
            return
        self.EnableSlot()
        self.SetDragState()
        self.PrepareUtilButtons()
        iconSize = int(self.SLOT_SIZE * GetScaleFactor())
        self.flagIcon.SetSize(iconSize, iconSize)
        if self.controller.GetModule() or self.controller.IsModulePreviewModule():
            moduleItem = self.controller.GetModuleOrPreview()
            self.flagIcon.LoadIconByTypeID(moduleItem.typeID, ignoreSize=True)
        else:
            slotIcon = 'res:/UI/Texture/classes/Fitting/stationServiceSlot.png'
            self.flagIcon.LoadIcon(slotIcon, ignoreSize=True)
        if self.controller.GetModule():
            self.tooltipPanelClassInfo = TooltipModuleWrapper()
            modulehint = evetypes.GetName(self.controller.GetModuleTypeID())
            if not self.controller.SlotExists():
                modulehint = GetByLabel('UI/Fitting/SlotDoesNotExist')
            self.hint = modulehint
        else:
            self.tooltipPanelClassInfo = None
            self.hint = self._emptyHint
        if not self.hilitedFromMathing:
            self.Hilite(0)
        self.UpdateOnlineDisplay()
        self.UpdateStatusDisplay()
        self.UpdateGhostFittingIcons(self.controller.GetModule())

    def OnDropData(self, dragObj, nodes):
        self.controller.OnDropData(dragObj, nodes)

    def AddItem(self, item, sourceLocation = None):
        pass

    def OnClick(self, *args):
        return self.controller.OnClick(self)

    def OnMouseEnter(self, *args):
        if self.controller.GetModule() is not None:
            self.ShowUtilButtons()
            self.ShowCpuAndPowergrid()
        else:
            self.hint = self._emptyHint
            self.Hilite(1)
            uicore.Message('ListEntryEnter')

    def OnMouseExit(self, *args):
        if not self.controller.GetModule():
            self.Hilite(0)
        self.HideCpuAndPowergrid()

    def PrepareUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

        self.utilButtons = []
        if not self.controller.GetModule():
            return
        btns = self.GetUtilBtns()
        i = 0
        for btnData in btns:
            left = int(self.left + self.width / 2.0 - 8)
            top = self.height + 20 + i * 16
            utilBtn = FittingUtilBtn(parent=self.parent, icon=btnData.iconPath, left=left, top=top, btnData=btnData, mouseOverFunc=self.ShowUtilButtons, align=uiconst.BOTTOMLEFT, controller=self.controller)
            if btnData.onlineBtn == 1:
                self.sr.onlineButton = utilBtn
            self.utilButtons.append(utilBtn)
            i += 1

    def GetUtilBtns(self):
        btns = []
        isRig = False
        for effect in dogma_data.get_type_effects(self.controller.GetModuleTypeID()):
            if effect.effectID == effectRigSlot:
                isRig = True
                break

        isOnlinable = self.controller.IsOnlineable()
        if isRig:
            btns += self.GetRigsBtns()
        else:
            btns = self.GetModuleBtns(isOnlinable)
        return btns

    def ShowCpuAndPowergrid(self):
        self.controller.GetCpuAndPowergridUsage()

    def HideCpuAndPowergrid(self):
        self.controller.HideCpuAndPowergridUsage()


class FittingServiceCont(Container):
    SLOT_CLASS = FittingServiceSlot
    default_name = 'FittingServiceCont'
    default_height = 70
    default_width = 300
    default_align = uiconst.CENTERBOTTOM
    default_top = 4

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.slotsByFlagID = {}
        scaleFactor = GetScaleFactor()
        slotWidth = int(round(44.0 * scaleFactor))
        slotHeight = int(round(44.0 * scaleFactor))
        label = EveLabelMedium(parent=self, text=GetByLabel('UI/Fitting/StructureServices'), align=uiconst.TOBOTTOM)
        top = label.textheight + 2
        width = 0
        for i, flagID in enumerate(invConst.serviceSlotFlags):
            left = i * (slotWidth + 4)
            slot = self.SLOT_CLASS(name='%s' % flagID, parent=self, pos=(left,
             top,
             slotWidth,
             slotHeight), controller=self.controller.GetSlotController(flagID))
            self.slotsByFlagID[flagID] = slot
            width += slotWidth + 4

        self.width = width
        self.height = slotHeight + label.textheight + 100
        self.ChangeSignalConnection(connect=True)

    def ChangeSignalConnection(self, connect = True):
        signalAndCallback = [(self.controller.on_slots_with_menu_changed, self.OnSlotsWithMenuChanged)]
        ChangeSignalConnect(signalAndCallback, connect)

    def OnSlotsWithMenuChanged(self, oldFlagID, newFlagID):
        slot = self.slotsByFlagID.get(oldFlagID, None)
        if slot is not None:
            slot.HideUtilButtons()

    def GetSlotsByFlagID(self):
        return self.slotsByFlagID

    def Close(self):
        with EatSignalChangingErrors(errorMsg='FittingServiceCont'):
            self.ChangeSignalConnection(connect=False)
        self.controller = None
        Container.Close(self)
