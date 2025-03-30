#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomContainer.py
import logging
import blue
import telemetry
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eveexceptions
import threadutils
import trinity
import uthread
from carbon.common.script.sys.serviceConst import ROLEMASK_ELEVATEDPLAYER
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.line import Line
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.sys import eveinit
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from eve.client.script.ui.control.resourceLoadingIndicator import ResourceLoadingIndicator
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonCharacterIcon import ButtonCharacterIcon
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonEveMenu import ButtonEveMenu
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonGroup import ButtonGroup
from eve.client.script.ui.shared.neocom.neocom.buttons.buttonSkills import ButtonSkills
from eve.client.script.ui.shared.neocom.neocom.buttons.clockButton import ClockButton
from eve.client.script.ui.shared.neocom.neocom.buttons.overflowButton import OverflowButton
from eve.client.script.ui.shared.neocom.neocom.neocomButtonClasses import GetBtnClassByBtnType
from eve.client.script.ui.shared.neocom.neocom.neocomConst import NEOCOM_DEFAULT_WIDTH, NEOCOM_MINSIZE, NEOCOM_MAXSIZE, FIXED_PARENT_BTNTYPES
from eve.client.script.ui.shared.neocom.neocom.neocomSettings import neocom_light_background_setting, neocom_width_setting, neocom_align_setting
from eve.client.script.ui.shared.neocom.neocom.neocomWalletUpdater import WalletUpdater
from eve.common.lib import appConst
from neocom2.walletPopupManager import WalletPopupManager
from uihider import UiHiderMixin
log = logging.getLogger(__name__)

class NeocomContainer(UiHiderMixin, Container):
    __notifyevents__ = ['OnEveMenuOpened',
     'OnEveMenuClosed',
     'OnCameraDragStart',
     'OnCameraDragEnd',
     'OnPersonalAccountChangedClient',
     'OnCharacterLpUpdatedInWallet']
    default_name = 'Neocom'
    uniqueUiName = pConst.UNIQUE_NAME_NEOCOM
    default_state = uiconst.UI_NORMAL
    default_width = NEOCOM_DEFAULT_WIDTH
    COLOR_CORNERFILL = (0, 0, 0, 0.5)
    COLOR_FIXED_BUTTON_BORDER = (1.0, 1.0, 1.0, 0.2)
    blurredUnderlay = None

    @property
    def analyticID(self):
        return self.default_name

    def OnPersonalAccountChangedClient(self, newBalance, transaction):
        self.walletPopupManager.OnPersonalAccountChangedClient(newBalance, transaction)
        if not self.isProcessing:
            self.isProcessing = True
            uthread.new(self._ProcessThread)

    def OnCharacterLpUpdatedInWallet(self, issuerCorpID, lpBefore, lpAfter):
        self.walletPopupManager.OnLpUpdated(issuerCorpID, lpBefore, lpAfter)
        if not self.isProcessing:
            self.isProcessing = True
            uthread.new(self._ProcessThread)

    def _ProcessThread(self):
        try:
            blue.synchro.Sleep(500)
            if self.walletPopupManager:
                self.walletPopupManager.ProcessWaitingTransactions()
        finally:
            self.isProcessing = False

    def ApplyAttributes(self, attributes):
        super(NeocomContainer, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.mainBtnDataRoot = attributes.mainBtnDataRoot
        self.skillsBtnDataRoot = attributes.skillsBtnDataRoot
        self.charSheetBtnDataRoot = attributes.charSheetBtnDataRoot
        self.eveMenuBtnDataRoot = attributes.eveMenuBtnDataRoot
        self.fixedButtonDataRoot = attributes.fixedButtonDataRoot
        self.autoHideActive = settings.char.ui.Get('neocomAutoHideActive', False)
        self.isHidden = False
        self.overflowButtons = []
        self.isResizingNeocom = False
        self.buttonDragOffset = None
        self.dragOverBtn = None
        self.walletPopupManager = WalletPopupManager(settings.char.ui, neocom=self, uiClass=WalletUpdater)
        self.isProcessing = False
        self.width = neocom_width_setting.get()
        self.resizeLineCont = Container(parent=self, name='resizeLineCont', align=uiconst.TOALL)
        self.mainCont = Container(parent=self, name='mainCont', align=uiconst.TOALL)
        self._ConstructBackground()
        self._ConstructBaseLayout()
        self._ConstructCharCont()
        self.UpdateButtons()
        if self.autoHideActive:
            self.HideNeocom()
        isElevated = eveinit.Eve().session.role & ROLEMASK_ELEVATEDPLAYER
        if isElevated and settings.public.ui.Get('Insider', True):
            try:
                insider = sm.GetService('insider')
                uthread.new(insider.Show, True, True)
            except eveexceptions.ServiceNotFound:
                pass

        neocom_light_background_setting.on_change.connect(self._on_light_background_changed)

    def _ConstructBackground(self):
        self.blurredUnderlay = BlurredSceneUnderlay(bgParent=self, isLightBackground=neocom_light_background_setting.get(), isInFocus=False, fixedColor=(1.0, 1.0, 1.0))
        if self.align == uiconst.TOLEFT:
            align = uiconst.TORIGHT
        else:
            align = uiconst.TOLEFT
        self.resizeLine = Line(parent=self.resizeLineCont, color=(0, 0, 0, 0), align=align, weight=3, state=uiconst.UI_NORMAL)
        self.resizeLine.OnMouseDown = self.OnReisizeLineMouseDown
        self.resizeLine.OnMouseEnter = self.OnResizeLineMouseEnter
        self.SetResizeLineCursor()

    def _on_light_background_changed(self, value):
        if self.blurredUnderlay:
            if value:
                self.blurredUnderlay.EnableLightBackground()
            else:
                self.blurredUnderlay.DisableLightBackground()

    def OnCameraDragStart(self):
        self.blurredUnderlay.isCameraDragging = True
        self.blurredUnderlay.UpdateState()

    def OnCameraDragEnd(self):
        self.blurredUnderlay.isCameraDragging = False
        self.blurredUnderlay.UpdateState()

    def SetResizeLineCursor(self):
        if self.IsSizeLocked():
            self.resizeLine.cursor = None
        else:
            self.resizeLine.cursor = uiconst.UICURSOR_LEFT_RIGHT_DRAG

    def OnReisizeLineMouseDown(self, *args):
        if not self.IsSizeLocked():
            uthread.new(self.OnResizerDrag)

    def OnResizeLineMouseEnter(self, *args):
        if self.isHidden:
            self.UnhideNeocom()

    def OnResizerDrag(self, *args):
        while uicore.uilib.leftbtn and not self.destroyed:
            self.isResizingNeocom = True
            width = 0
            if self.align == uiconst.TOLEFT:
                width = uicore.uilib.x
            elif self.align == uiconst.TORIGHT:
                width = uicore.desktop.width - uicore.uilib.x
            if width != self.width:
                self.width = max(NEOCOM_MINSIZE, min(width, NEOCOM_MAXSIZE))
                self._ConstructCharCont()
                neocom_width_setting.set(self.width)
                sm.ScatterEvent('OnNeocomResized')
            sm.GetService('window').UpdateIntersectionBackground()
            blue.synchro.SleepWallclock(100)

        self.isResizingNeocom = False

    def _ConstructBaseLayout(self):
        self.charCont = ContainerAutoSize(parent=self.mainCont, name='charCont', align=uiconst.TOTOP)
        ClockButton(parent=self.mainCont, name='clockCont', uniqueUiName=pConst.UNIQUE_NAME_CLOCK_CALENDAR, align=uiconst.TOBOTTOM, height=20)
        self.resourceLoadingIndicator = ResourceLoadingIndicator(parent=self.mainCont, name='resourceLoadingContainer', align=uiconst.TOBOTTOM, height=30)
        Fill(bgParent=self.resourceLoadingIndicator, color=(0, 0, 0, 0.2))
        self.fixedButtonCont = ContainerAutoSize(parent=self.mainCont, name='fixedButtonCont', align=uiconst.TOBOTTOM)
        Fill(bgParent=self.fixedButtonCont, color=self.COLOR_CORNERFILL, blendMode=trinity.TR2_SBM_ADD)
        self.overflowBtn = OverflowButton(parent=self.mainCont, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN, height=20, padBottom=1)
        self.buttonCont = Container(parent=self.mainCont, name='buttonCont', align=uiconst.TOALL)
        self.buttonCont._OnSizeChange_NoBlock = self.OnButtonContainerSizeChanged
        self.dropIndicatorLine = Line(parent=self.mainCont, name='dropIndicatorLine', align=uiconst.TOPLEFT, color=Color.GetGrayRGBA(0.7, 0.3), pos=(0, 0, 0, 1))

    def _ConstructCharCont(self):
        self.charCont.Flush()
        self.eveMenuBtn = ButtonEveMenu(parent=self.charCont, name='eveMenuBtn', uniqueUiName=pConst.UNIQUE_NAME_EVE_MENU_BTN, align=uiconst.TOTOP, height=self.width, btnData=self.eveMenuBtnDataRoot)
        self.charSheetBtn = ButtonCharacterIcon(parent=self.charCont, name='charSheetBtn', align=uiconst.TOTOP, height=self.width, btnData=self.charSheetBtnDataRoot.children[0])
        self.skillPlannerBtn = ButtonSkills(parent=self.charCont, name='skillsBtn', align=uiconst.TOTOP, height=self.width, btnData=self.skillsBtnDataRoot.children[0])

    @threadutils.throttled(0.1)
    def UpdateButtons_throttled(self):
        uthread.new(self.UpdateButtons)

    @telemetry.ZONE_METHOD
    def UpdateButtons(self):
        self.UpdateFixedButtons()
        self.mainBtnDataRoot.on_child_added.connect(self.OnRootNodeChildAdded)
        self.mainBtnDataRoot.on_child_removed.connect(self.OnRootNodeChildRemoved)
        self.buttonCont.Flush()
        isDraggable = not self.IsSizeLocked()
        for btnData in self.mainBtnDataRoot.GetChildrenInScope():
            btnClass = GetBtnClassByBtnType(btnData)
            btnUI = btnClass(parent=self.buttonCont, name=btnData.id, btnData=btnData, isDraggable=isDraggable, width=self.width, height=self.width)
            btnData.btnUI = btnUI
            btnUI.onButtonDragEnter.connect(self.OnButtonDragEnter)
            btnUI.onButtonDragEnd.connect(self.OnButtonDragEnd)
            btnUI.onButtonDragged.connect(self.OnButtonDragged)

        self.CheckOverflow()
        self.dragOverBtn = None
        sm.GetService('neocom').OnNeocomButtonsRecreated()

    def OnRootNodeChildRemoved(self, btnData):
        self.UpdateButtons()
        self.HideDropIndicatorLine()

    def OnRootNodeChildAdded(self, btnData):
        self.UpdateButtons()
        self.HideDropIndicatorLine()

    def SetFixedButtonDataRoot(self, fixedButtonDataRoot):
        self.fixedButtonDataRoot = fixedButtonDataRoot
        self.UpdateFixedButtons()

    def UpdateFixedButtons(self):
        self.fixedButtonCont.DisableAutoSize()
        self.fixedButtonCont.Flush()
        if not self.fixedButtonDataRoot.children:
            self.fixedButtonCont.Hide()
            return
        Line(parent=self.fixedButtonCont, name='fixedButtonTopLine', color=self.COLOR_FIXED_BUTTON_BORDER, align=uiconst.TOTOP, padBottom=1)
        for btnData in self.fixedButtonDataRoot.children:
            btnClass = GetBtnClassByBtnType(btnData)
            btnUI = btnClass(parent=self.fixedButtonCont, name=btnData.id, btnData=btnData, adjustPositionManually=False, isDraggable=False, controller=self, height=self.width, align=uiconst.TOTOP)
            btnData.btnUI = btnUI

        Line(parent=self.fixedButtonCont, name='fixedButtonBottomLine', color=self.COLOR_FIXED_BUTTON_BORDER, align=uiconst.TOTOP, padTop=1)
        self.fixedButtonCont.EnableAutoSize()
        self.fixedButtonCont.Show()

    def CheckOverflow(self):
        self.overflowButtons = []
        w, h = self.buttonCont.GetAbsoluteSize()
        for btnUI in self.buttonCont.children:
            if btnUI.top + btnUI.height > h:
                btnUI.Hide()
                self.overflowButtons.append(btnUI.btnData)
            else:
                btnUI.Show()

        if self.overflowButtons:
            newState = uiconst.UI_NORMAL
        else:
            newState = uiconst.UI_HIDDEN
        if self.overflowBtn.state != newState:
            self.overflowBtn.state = newState
            self.CheckOverflow()

    def GetMenu(self):
        return sm.GetService('neocom').GetMenu()

    def SetSizeLocked(self, isLocked):
        settings.char.ui.Set('neocomSizeLocked', isLocked)
        self.SetResizeLineCursor()
        for btn in self.buttonCont.children:
            btn.SetDraggable(not isLocked)

    def IsSizeLocked(self):
        return settings.char.ui.Get('neocomSizeLocked', False)

    def IsAutoHideActive(self):
        return settings.char.ui.Get('neocomAutoHideActive', False)

    def SetAutoHideOn(self):
        settings.char.ui.Set('neocomAutoHideActive', True)
        self.autoHideActive = True
        uthread.new(self.AutoHideThread)

    def SetAutoHideOff(self):
        settings.char.ui.Set('neocomAutoHideActive', False)
        self.autoHideActive = False
        self.UnhideNeocom()

    def SetAlignRight(self):
        neocom_align_setting.set(uiconst.TORIGHT)
        self.align = uiconst.TORIGHT
        self.resizeLine.align = uiconst.TOLEFT
        self.overflowBtn.UpdateIconRotation()
        self.SetOrder(0)

    def SetAlignLeft(self):
        neocom_align_setting.set(uiconst.TOLEFT)
        self.align = uiconst.TOLEFT
        self.resizeLine.align = uiconst.TORIGHT
        self.overflowBtn.UpdateIconRotation()
        self.SetOrder(0)

    def OnDropData(self, source, dropData):
        if not sm.GetService('neocom').IsValidDropData(dropData):
            return
        sm.GetService('neocom').OnBtnDataDropped(dropData[0])

    def OnDragEnter(self, panelEntry, dropData):
        sm.GetService('neocom').OnNeocomTaskbarMouseEnter(dropData[0])

    def OnDragExit(self, *args):
        self.HideDropIndicatorLine()

    def OnButtonDragEnter(self, btnData, dropData):
        sm.GetService('neocom').OnButtonDragEnter(btnData, dropData)

    def OnButtonDragEnd(self, btnUI):
        folderBtnUI = self._GetButtonByXCoord(btnUI.top)
        if folderBtnUI and folderBtnUI != btnUI and isinstance(folderBtnUI, ButtonGroup):
            self.AddToFolder(btnUI, folderBtnUI)
        self.buttonDragOffset = None
        btnUI.SetCorrectPosition()
        btnUI.isDragging = False

    def AddToFolder(self, btnUI, folderBtnUI, *args):
        btnUI.btnData.MoveTo(folderBtnUI.btnData)

    def _CheckSwitch(self, dragBtn):
        switchBtn = self._GetButtonByXCoord(dragBtn.top)
        if self.dragOverBtn and switchBtn != self.dragOverBtn:
            self.dragOverBtn.OnDragExit()
        if switchBtn and switchBtn != dragBtn:
            if isinstance(switchBtn, ButtonGroup) and dragBtn.btnData.btnType not in FIXED_PARENT_BTNTYPES:
                self.dragOverBtn = switchBtn
                self.dragOverBtn.OnDragEnter(None, [dragBtn.btnData])
            else:
                dragBtn.btnData.SwitchWith(switchBtn.btnData)
                switchBtn.OnSwitched()
                self.UpdateButtonPositions()
        else:
            self.dragOverBtn = None

    def UpdateButtonPositions(self):
        for btn in self.buttonCont.children:
            if btn.isDragging:
                continue
            btn.SetCorrectPosition()

    def _GetButtonByXCoord(self, x, offset = True):
        btnDataList = self.mainBtnDataRoot.GetChildrenInScope()
        if not btnDataList:
            return None
        maxval = len(btnDataList)
        if offset:
            x += self.width / 2
        index = max(0, x / self.width)
        if index < maxval:
            btnData = btnDataList[index]
            button = btnData.btnUI
            if button.display and not button.isDragging:
                return button
        else:
            return None

    def OnButtonDragged(self, btn):
        sm.GetService('neocom').CloseAllPanels()
        l, t, w, h = self.buttonCont.GetAbsolute()
        relY = uicore.uilib.y - t
        if self.buttonDragOffset is None:
            self.buttonDragOffset = relY - btn.top
        minval = 0
        maxval = h - btn.height
        btn.top = max(minval, min(relY - self.buttonDragOffset, maxval))
        btn.isDragging = True
        self._CheckSwitch(btn)

    def OnButtonContainerSizeChanged(self, *args):
        self.UpdateButtons_throttled()

    def HideNeocom(self):
        endVal = 3 - self.width
        uicore.animations.MorphScalar(self, 'left', self.left, endVal, duration=0.7)
        self.isHidden = True

    def UnhideNeocom(self, sleep = False):
        if not self.isHidden:
            return
        uicore.animations.MorphScalar(self, 'left', self.left, 0, duration=0.2, sleep=sleep)
        self.isHidden = False
        if self.autoHideActive:
            uthread.new(self.AutoHideThread)

    def AutoHideThread(self):
        mouseNotOverTime = blue.os.GetTime()
        while not self.destroyed:
            blue.pyos.synchro.Sleep(50)
            if not self or self.destroyed:
                return
            if not self.IsAutoHideActive():
                return
            mo = uicore.uilib.mouseOver
            if mo == self or mo.IsUnder(self):
                mouseNotOverTime = blue.os.GetTime()
                continue
            if sm.GetService('neocom').IsSomePanelOpen() or self.isResizingNeocom:
                mouseNotOverTime = blue.os.GetTime()
                continue
            if uicore.layer.menu.children:
                mouseNotOverTime = blue.os.GetTime()
                continue
            if self.IsDraggingButtons():
                mouseNotOverTime = blue.os.GetTime()
                continue
            if blue.os.GetTime() - mouseNotOverTime > appConst.SEC:
                self.HideNeocom()
                return

    def IsDraggingButtons(self):
        return self.buttonDragOffset is not None

    def ShowDropIndicatorLine(self, index):
        l, t = self.buttonCont.GetAbsolutePosition()
        self.dropIndicatorLine.state = uiconst.UI_DISABLED
        self.dropIndicatorLine.top = t + index * self.width
        self.dropIndicatorLine.width = self.width

    def HideDropIndicatorLine(self):
        self.dropIndicatorLine.state = uiconst.UI_HIDDEN

    def OnEveMenuOpened(self):
        self.menuOpened = True
        for btn in self.buttonCont.children:
            if not self.menuOpened:
                return
            uicore.animations.FadeTo(self.mainCont, self.buttonCont.opacity, 0.5, duration=0.5)

    def OnEveMenuClosed(self):
        self.menuOpened = False
        uicore.animations.FadeTo(self.mainCont, self.buttonCont.opacity, 1.0, duration=uiconst.TIME_EXIT)

    def GetEveMenuButtonSize(self):
        if self.eveMenuBtn and not self.eveMenuBtn.destroyed:
            return (self.width, self.eveMenuBtn.height)
        return (0, 0)
