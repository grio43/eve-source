#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\slot.py
import logging
import math
import carbonui.const as uiconst
import dogma.data as dogma_data
import evetypes
import inventorycommon.typeHelpers
import localization
import telemetry
import utillib
from carbonui.primitives.sprite import Sprite
from dogma.const import effectRigSlot
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.inflight.shipModuleButton.moduleButtonTooltip import TooltipModuleWrapper
from eve.client.script.ui.shared.fitting.baseSlot import FittingSlotBase
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor
from eve.client.script.ui.shared.fitting.utilBtns import FittingUtilBtn, UtilBtnData
from eve.client.script.ui.shared.fittingScreen.failedModuleTooltip import LoadGetFailedModuleTooltip
from eve.client.script.ui.station.fitting.fittingTooltipUtils import SetFittingTooltipInfo
from eve.common.lib import appConst as const
from carbonui.uicore import uicore
import inventorycommon.const as invConst
MAXMODULEHINTWIDTH = 300
logger = logging.getLogger(__name__)

class FittingSlot(FittingSlotBase):
    __guid__ = 'xtriui.FittingSlot'
    __notifyevents__ = ['OnRefreshModuleBanks']
    default_name = 'fittingSlot'
    default_width = 44
    default_height = 54
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    slotsToHintDict = {'hiSlot': ('UI/Fitting/EmptyHighPowerSlot', 'EmptyHighSlot'),
     'medSlot': ('UI/Fitting/EmptyMediumPowerSlot', 'EmptyMidSlot'),
     'loSlot': ('UI/Fitting/EmptyLowPowerSlot', 'EmptyLowSlot'),
     'subSystemSlot': ('UI/Fitting/EmptySubsystemSlot', ''),
     'rigSlot': ('UI/Fitting/EmptyRigSlot', '')}

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        FittingSlotBase.ApplyAttributes(self, attributes)
        self.groupMark = None
        self.chargeIndicator = None
        sm.RegisterNotify(self)
        self.radCosSin = attributes.radCosSin
        self.invReady = 1
        self.UpdateFitting()
        self.ChangeSignalConnection(connect=True)

    def ConstructFlagAndUnderlay(self):
        self.flagIcon = eveIcon.Icon(parent=self, name='flagIcon', align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=self.width, height=self.height)
        self.sr.underlay = Sprite(bgParent=self, name='underlay', state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/moduleFrame.png')

    def ConstructModuleSlotFill(self):
        if self.moduleSlotFill:
            return
        self.moduleSlotFill = Sprite(parent=self, name='moduleSlotFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath=self.slotActiveTexturePath, color=(1, 1, 1, 0.5))
        self.moduleSlotFill.display = False

    def ConstructWarningFill(self):
        if self.warningFill and not self.warningFill.destroyed:
            return
        self.warningFill = Sprite(parent=self, name='warningFill', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath=self.slotPassiveTexturePath, color=(1.0, 0.35, 0.0))
        self.warningFill.display = False

    def ConstructSkillSprite(self):
        if self.skillSprite:
            return
        self.skillSprite = Sprite(parent=self, name='skillSprite', align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=(-8, -4, -8, -4), texturePath='res:/UI/Texture/classes/Fitting/slotActive.png', color=(1, 1, 1, 0.5))
        self.skillSprite.display = False

    def ConstructGroupMark(self):
        if self.groupMark:
            return
        self.groupMark = Sprite(parent=self, name='groupMark', pos=(-10, 14, 16, 16), align=uiconst.CENTER, state=uiconst.UI_NORMAL, idx=0)
        self.groupMark.GetMenu = self.controller.GetGroupMenu

    def ConstructChargeIndicator(self):
        if self.chargeIndicator:
            return
        self.chargeIndicator = Sprite(parent=self, name='chargeIndicator', padTop=-2, height=7, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_HIDDEN, texturePath='res:/UI/Texture/Icons/81_64_2.png', ignoreSize=True)
        self.chargeIndicator.rectWidth = 44
        self.chargeIndicator.rectHeight = 7

    def ConstructFittingWarning(self):
        if self.fittingWarning and not self.fittingWarning.destroyed:
            return
        self.fittingWarning = Sprite(parent=self, name='fittingWarning', state=uiconst.UI_DISABLED, align=uiconst.BOTTOMLEFT, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/classes/Fitting/slotWarningIcon.png', idx=0)
        self.fittingWarning.rotation = -self.GetRotation()

    def OnRefreshModuleBanks(self):
        self.SetGroup()

    def SetGroup(self):
        try:
            if self.controller.GetModule() is not None and not self.controller.SlotExists():
                self.controller.DestroyWeaponBank()
        except ReferenceError:
            pass

        parentID = self.controller.GetParentID()
        allGroupsDict = settings.user.ui.Get('linkedWeapons_groupsDict', {})
        groupDict = allGroupsDict.get(parentID, {})
        ret = self.GetBankGroup(groupDict)
        if ret is None:
            if self.groupMark:
                self.groupMark.Hide()
            return
        groupNumber = ret.groupNumber
        self.ConstructGroupMark()
        self.groupMark.state = uiconst.UI_NORMAL
        self.groupMark.rotation = -self.GetRotation()
        if groupNumber < 0:
            availGroups = [1,
             2,
             3,
             4,
             5,
             6,
             7,
             8]
            for masterID, groupNum in groupDict.iteritems():
                if groupNum in availGroups:
                    availGroups.remove(groupNum)

            groupNumber = availGroups[0] if availGroups else ''
        self.groupMark.texturePath = 'res:/UI/Texture/Icons/73_16_%s.png' % (176 + groupNumber)
        self.groupMark.hint = localization.GetByLabel('UI/Fitting/GroupNumber', groupNumber=groupNumber)
        groupDict[ret.masterID] = groupNumber
        allGroupsDict[parentID] = groupDict
        settings.user.ui.Set('linkedWeapons_groupsDict', allGroupsDict)

    def GetBankGroup(self, groupDict):
        module = self.controller.GetModule()
        try:
            if not module:
                return None
        except ReferenceError:
            return None

        masterID = self.controller.IsInWeaponBank()
        if not masterID:
            return None
        if masterID in groupDict:
            groupNumber = groupDict.get(masterID)
        else:
            groupNumber = -1
        ret = utillib.KeyVal()
        ret.masterID = masterID
        ret.groupNumber = groupNumber
        return ret

    def PrepareUtilButtons(self):
        self.RemoveUtilButtons()
        self.utilButtons = []
        if not self.controller.GetModule():
            return
        myrad, cos, sin, cX, cY = self.radCosSin
        btns = self.GetUtilBtns()
        rad = myrad - 34
        i = 0
        for btnData in btns:
            left = int((rad - i * 16) * cos) + cX - 16 / 2
            top = int((rad - i * 16) * sin) + cY - 16 / 2
            utilBtn = FittingUtilBtn(parent=self.parent, icon=btnData.iconPath, left=left, top=top, btnData=btnData, mouseOverFunc=self.ShowUtilButtons, controller=self.controller, name='UtilIcon_%d' % i)
            if btnData.onlineBtn == 1:
                self.sr.onlineButton = utilBtn
            self.utilButtons.append(utilBtn)
            i += 1

    def RemoveUtilButtons(self):
        for btn in self.utilButtons:
            btn.Close()

    def GetUtilBtns(self):
        btns = []
        if self.controller.GetCharge():
            btns += self.GetChargesBtns()
        isRig = False
        for effect in dogma_data.get_type_effects(self.controller.GetModuleTypeID()):
            if effect.effectID == effectRigSlot:
                isRig = True
                break

        isSubSystem = evetypes.GetCategoryID(self.controller.GetModuleTypeID()) == invConst.categorySubSystem
        isOnlinable = self.controller.IsOnlineable()
        if isRig:
            btns += self.GetRigsBtns()
        elif isSubSystem:
            btns += self.GetSubSystemBtns()
        else:
            btns += self.GetModuleBtns(isOnlinable)
        return btns

    def GetChargesBtns(self):
        moduleTypeID = self.controller.GetModuleTypeID()
        btns = [UtilBtnData(localization.GetByLabel('UI/Fitting/RemoveCharge'), 'ui_38_16_200', self.controller.Unfit, 1, 0), UtilBtnData(localization.GetByLabel('UI/Fitting/ShowChargeInfo'), 'ui_38_16_208', self.ShowChargeInfo, 1, 0), UtilBtnData(evetypes.GetName(moduleTypeID), inventorycommon.typeHelpers.GetIconFile(moduleTypeID), None, 1, 0)]
        return btns

    def GetSubSystemBtns(self):
        btns = [UtilBtnData(localization.GetByLabel('UI/Commands/ShowInfo'), 'ui_38_16_208', self.ShowInfo, 1, 0)]
        return btns

    @telemetry.ZONE_METHOD
    def UpdateFitting(self):
        if self.destroyed or not self.controller.CurrentShipIsLoaded():
            return
        if not self.controller.SlotExists() and not self.controller.GetModule():
            if self.controller.IsSubsystemSlot() and self.controller.parentController.HasStance():
                self.HideSlot()
            else:
                self.DisableSlot()
            self.HideChargeIndicator()
            self.RemoveUtilButtons()
            return
        self.EnableSlot()
        self.SetDragState()
        if self.controller.GetCharge():
            chargeQty = self.controller.GetChargeQuantity()
            if self.controller.GetModule() is None:
                portion = 1.0
            else:
                cap = self.controller.GetChargeCapacity()
                if cap.capacity == 0:
                    portion = 1.0
                else:
                    portion = cap.used / cap.capacity
            step = max(0, min(4, int(portion * 5.0)))
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 10 * step
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = '%s %d%%' % (evetypes.GetName(self.controller.GetCharge().typeID), portion * 100)
        elif not self.controller.GetModule():
            self.HideUtilButtons(1)
            self.HideChargeIndicator()
        elif self.controller.IsChargeable():
            self.ConstructChargeIndicator()
            self.chargeIndicator.rectTop = 0
            self.chargeIndicator.state = uiconst.UI_NORMAL
            self.chargeIndicator.hint = localization.GetByLabel('UI/Fitting/NoCharge')
        else:
            self.HideChargeIndicator()
            if self.chargeIndicator:
                self.chargeIndicator.Hide()
        if self.controller.GetModule():
            self.tooltipPanelClassInfo = TooltipModuleWrapper()
            modulehint = evetypes.GetName(self.controller.GetModuleTypeID())
            if self.controller.GetCharge():
                modulehint += '<br>%s' % localization.GetByLabel('UI/Fitting/ChargeQuantity', charge=self.controller.GetCharge().typeID, chargeQuantity=chargeQty)
            if not self.controller.SlotExists():
                modulehint = localization.GetByLabel('UI/Fitting/SlotDoesNotExist')
            self.hint = modulehint
        elif self.controller.GetFailedTypeID():
            self.tooltipPanelClassInfo = None
        else:
            self.tooltipPanelClassInfo = None
            self.hint = self._emptyHint
            tooltipName = self._emptyTooltip
            if tooltipName:
                SetFittingTooltipInfo(targetObject=self, tooltipName=tooltipName, includeDesc=False)
        self.PrepareUtilButtons()
        iconSize = int(48 * GetScaleFactor())
        self.flagIcon.SetSize(iconSize, iconSize)
        if self.controller.GetCharge() or self.controller.GetModule() or self.controller.IsModulePreviewModule():
            self.flagIcon.LoadIconByTypeID((self.controller.GetCharge() or self.controller.GetModuleOrPreview()).typeID, ignoreSize=True)
            self.flagIcon.rotation = -self.GetRotation()
        else:
            rev = 0
            slotIcon = {invConst.flagSubSystemSlot0: 'res:/UI/Texture/Icons/81_64_11.png',
             invConst.flagSubSystemSlot1: 'res:/UI/Texture/Icons/81_64_10.png',
             invConst.flagSubSystemSlot2: 'res:/UI/Texture/Icons/81_64_12.png',
             invConst.flagSubSystemSlot3: 'res:/UI/Texture/Icons/81_64_13.png'}.get(self.controller.GetFlagID(), None)
            if slotIcon is None:
                slotIcon = {const.effectLoPower: 'res:/UI/Texture/Icons/81_64_5.png',
                 const.effectMedPower: 'res:/UI/Texture/Icons/81_64_6.png',
                 const.effectHiPower: 'res:/UI/Texture/Icons/81_64_7.png',
                 const.effectRigSlot: 'res:/UI/Texture/Icons/81_64_8.png'}.get(self.controller.GetPowerType(), None)
            else:
                rev = 1
            if slotIcon is not None:
                self.flagIcon.LoadIcon(slotIcon, ignoreSize=True)
            if rev:
                self.flagIcon.rotation = math.radians(180.0)
            else:
                self.flagIcon.rotation = 0.0
        self.SetGroup()
        self.UpdateOnlineDisplay()
        self.UpdateStatusDisplay()
        self.UpdateGhostFittingIcons(self.controller.GetModule())
        if not self.hilitedFromMathing:
            self.Hilite(0)

    def HideChargeIndicator(self):
        if self.chargeIndicator:
            self.chargeIndicator.Hide()

    def IsCharge(self, typeID):
        return evetypes.GetCategoryID(typeID) == invConst.categoryCharge

    def ShowChargeInfo(self, *args):
        self.controller.ShowChargeInfo()

    def _OnEndDrag(self, *args):
        self.left = self.top = -2

    def OnEndDrag(self, *args):
        if self.controller and self.controller.GetModule() is not None:
            sm.ScatterEvent('OnResetSlotLinkingMode', self.controller.GetModule().typeID)

    def GetTooltipPosition(self):
        rect, point = self.PositionHint()
        return rect

    def GetTooltipPointer(self):
        rect, point = self.PositionHint()
        return point

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if self.controller.GetFailedTypeID():
            LoadGetFailedModuleTooltip(tooltipPanel, self.controller.GetFailedTypeID())

    def UpdateInfo_TimedCall(self, *args):
        if self.destroyed or self.moduleButtonHint.destroyed:
            self.moduleButtonHint = None
            self.updateTimer = None
            return
        if self.controller.GetModuleTypeID():
            if self.controller.GetCharge():
                chargeItemID = self.controller.GetCharge().itemID
            else:
                chargeItemID = None
            self.moduleButtonHint.UpdateAllInfo(self.controller.GetModuleID(), chargeItemID, fromWhere='fitting')

    def PositionHint(self, *args):
        myRotation = self.rotation + 2 * math.pi
        myRotation = -myRotation
        sl, st, sw, sh = self.parent.GetAbsolute()
        cX = sl + sw / 2.0
        cY = st + sh / 2.0
        rad, cos, sin, oldcX, oldcY = self.radCosSin
        hintLeft = int(round(rad * cos))
        hintTop = int(round(rad * sin))
        cap = rad * 0.7
        if hintLeft < -cap:
            point = uiconst.POINT_RIGHT_2
        elif hintLeft > cap:
            point = uiconst.POINT_LEFT_2
        elif hintTop < -cap:
            if hintLeft < 0:
                point = uiconst.POINT_BOTTOM_3
            else:
                point = uiconst.POINT_BOTTOM_1
        elif hintLeft < 0:
            point = uiconst.POINT_TOP_3
        else:
            point = uiconst.POINT_TOP_1
        return ((hintLeft + cX - 15,
          hintTop + cY - 15,
          30,
          30), point)

    def _OnClose(self, *args):
        self.updateTimer = None
        moduleButtonHint = getattr(uicore.layer.hint, 'moduleButtonHint', None)
        if moduleButtonHint and not moduleButtonHint.destroyed:
            if moduleButtonHint.fromWhere == 'fitting':
                uicore.layer.hint.moduleButtonHint.FadeOpacity(0.0)
