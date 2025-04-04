#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\radialMenu\radialMenu.py
import math
from carbon.common.script.util import timerstuff
from carbon.common.script.util.format import FmtDist
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.shared.radialMenu.radialMenuActions import RadialMenuActioSecondLevel, RadialMenuRangeAction
from eve.client.script.ui.shared.radialMenu.radialMenuLayer import RadialMenuLayer, RadialMenuShadow
from eve.client.script.ui.shared.radialMenu.radialMenuUtils import RadialMenuOptionsInfo, RangeRadialMenuAction, SimpleRadialMenuAction, RadialMenuSizeInfo
from eve.client.script.ui.shared.radialMenu import spaceRadialMenuFunctions, inventoryRadialMenuFunctions, NORMAL_RADIAL_MENU, BROADCAST_RADIAL_MENU
from eve.client.script.ui.shared.radialMenu.rangeCircle import RangeCircle
import evetypes
import uthread
import carbonui.const as uiconst
import geo2
import blue
import telemetry
import localization
from eve.client.script.ui.util import uix
from carbonui.control.contextMenu.contextMenu import ShowMenu
from carbonui.uicore import uicore
from eve.client.script.ui.shared.radialMenu.spaceRadialMenuFunctions import GetSingleMouseBtnBroadcastRadialMenu
from eve.client.script.util.bubble import SlimItemFromCharID
RMO_SizeInfo = RadialMenuSizeInfo(width=220, height=220, shadowSize=256, rangeSize=128, sliceCount=8, buttonWidth=100, buttonHeight=70, buttonPaddingTop=12, buttonPaddingBottom=6, actionDistance=110)

class RadialMenu(Transform):
    __notifyevents__ = ['OnSettingsOpened']
    default_left = 0
    default_top = 0
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_width = RMO_SizeInfo.width
    default_height = RMO_SizeInfo.height
    sizeInfo = RMO_SizeInfo
    default_showActionText = True
    default_usePreciseRanges = True
    shadowTexture = 'res:/UI/Texture/classes/RadialMenu/menuShadow2.png'
    buttonBackgroundOpacity = 0.7
    menuType = NORMAL_RADIAL_MENU

    def ApplyAttributes(self, attributes):
        self.creationTime = blue.os.GetWallclockTime()
        self.clickedObject = attributes.get('clickedObject', None)
        self.radialMenuSvc = sm.GetService('radialmenu')
        self.cursor = uiconst.UICURSOR_SELECT
        uicore.UpdateCursor(self, force=True)
        self.lastMoveTime = 0
        Transform.ApplyAttributes(self, attributes)
        self.InitializeVariables(attributes)
        self.itemID = None
        self.SetSpecificValues(attributes)
        self.actionDistance = int(self.height / 2.0)
        self.selectedBtn = None
        self.AddMenuLayers()
        self.blocker = Container(name='blocker', parent=uicore.layer.menu, state=uiconst.UI_NORMAL, align=uiconst.TOALL, pos=(0, 0, 0, 0))
        self.blocker.OnMouseUp = self.OnMouseUpBlocker
        self.AddRangeCircle()
        doShowActionText = attributes.get('showActionText', self.default_showActionText)
        if doShowActionText:
            self.AddOptionText()
        shadowSize = self.sizeInfo.shadowSize
        self.shadow = RadialMenuShadow(parent=self, pos=(0,
         0,
         shadowSize,
         shadowSize), shadowSize=shadowSize, texturePath=self.shadowTexture, idx=-1)
        self.LoadMyActions(animate=True)
        self.InitializeCenterPoint(attributes)
        if self.displayName or self.updateDisplayName:
            self.AddDisplayLabel()
        self.SetPosition()
        self.mouseMoveCookie = uicore.event.RegisterForTriuiEvents(uiconst.UI_MOUSEMOVE, self.OnGlobalMove)
        self.updateOptionsTimer = timerstuff.AutoTimer(250, self.UpdateOptions)
        self.UpdateIndicator()
        sm.GetService('audio').SendUIEvent('ui_radial_open_play')
        sm.RegisterNotify(self)

    def AddMenuLayers(self):
        self.secondLayerCont = RadialMenuLayer(parent=self, name='secondLayerCont', pos=(0,
         0,
         self.width,
         self.height), display=False, sizeInfo=self.sizeInfo, buttonBackgroundOpacity=self.buttonBackgroundOpacity, usePreciseRanges=self.usePreciseRanges, menuType=self.menuType)
        self.firstLayerCont = RadialMenuLayer(parent=self, name='firstLayerCont', pos=(0,
         0,
         self.width,
         self.height), sizeInfo=self.sizeInfo, buttonBackgroundOpacity=self.buttonBackgroundOpacity, usePreciseRanges=self.usePreciseRanges, menuType=self.menuType)

    def InitializeVariables(self, attributes):
        self.sliceCount = self.sizeInfo.sliceCount
        self.stepSize = 360 / self.sliceCount
        self.buttonHeight = self.sizeInfo.buttonHeight
        self.buttonPaddingBottom = self.sizeInfo.buttonPaddingBottom
        self.usePreciseRanges = attributes.get('usePreciseRanges', self.default_usePreciseRanges)
        self.displayName = attributes.get('displayName', '')
        self.updateDisplayName = attributes.get('updateDisplayName', False)

    def InitializeCenterPoint(self, attributes):
        self.originalX = attributes.get('x', uicore.uilib.x)
        self.originalY = attributes.get('y', uicore.uilib.y)
        self.currentCenterX = self.originalX
        self.currentCenterY = self.originalY
        self.halfScreenX = uicore.desktop.width / 2
        self.halfScreenY = uicore.desktop.height / 2
        uicore.uilib.ClipCursor(0, 0, uicore.desktop.width, uicore.desktop.height)
        self.cursorClipped = True
        self.offsetX = 0
        self.offsetY = 0

    def SetSpecificValues(self, attributes):
        pass

    def AddDisplayLabel(self):
        displayTop = -18
        self.displayLabelCont = ThreePartContainer(parent=self, name='labelShadow', pos=(0,
         displayTop,
         200,
         30), align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, idx=0, leftTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowLeft.png', rightTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowRight.png', centerTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowCenter.png', sideSize=24)
        self.displayLabel = eveLabel.EveLabelLarge(text=self.displayName, parent=self.displayLabelCont, state=uiconst.UI_DISABLED, align=uiconst.CENTERTOP, top=0, idx=0)
        height = self.displayLabel.textheight + 2
        centerWidth = self.displayLabel.textwidth
        self.displayLabelCont.SetCenterSizeAndTop(centerWidth, height)
        if self.updateDisplayName:
            self.UpdateDisplayName()
            self.displayNameTimer = timerstuff.AutoTimer(250, self.UpdateDisplayName)

    def AddRangeCircle(self):
        rangeSize = self.sizeInfo.rangeSize
        self.rangeCont = RangeCircle(parent=self, rangeSize=rangeSize, idx=0)

    def AddOptionText(self):
        self.labelShadow = ThreePartContainer(parent=self, name='labelShadow', pos=(0, -10, 200, 30), align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0, leftTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowLeft.png', rightTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowRight.png', centerTexturePath='res:/UI/Texture/classes/RadialMenu/textShadowCenter.png', sideSize=24)
        self.labelShadow.display = False
        self.optionLabel = eveLabel.EveLabelLarge(text='', parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, top=-10, idx=0, bold=True)
        self.optionLabel.display = False
        self.optionRangeLabel = eveLabel.EveLabelLarge(text='', parent=self, state=uiconst.UI_DISABLED, align=uiconst.CENTER, top=6, idx=0)
        self.optionRangeLabel.display = False
        self.AdjustTextShadow()

    def SetOptionText(self, text):
        if not getattr(self, 'optionLabel', None):
            return
        self.optionLabel.display = True
        if text != self.optionLabel.text:
            self.optionLabel.text = text
            self.AdjustTextShadow()

    def ClearOptionText(self, *args):
        if not getattr(self, 'optionLabel', None):
            return
        self.optionLabel.display = False
        if self.optionLabel.text:
            self.optionLabel.text = ''
        if getattr(self, 'labelShadow', None):
            self.labelShadow.display = False

    def SetOptionRangeText(self, text = None, display = True):
        if not getattr(self, 'optionRangeLabel', None):
            return
        if text:
            self.optionRangeLabel.text = text
        self.optionRangeLabel.display = display
        self.AdjustTextShadow()

    def ClearOptionRangeText(self, *args):
        if not getattr(self, 'optionRangeLabel', None):
            return
        self.optionRangeLabel.display = False
        if self.optionRangeLabel.text:
            self.optionRangeLabel.text = ''
            self.AdjustTextShadow()

    def UpdateOptions(self):
        self.LoadMyActions(doReset=False)
        if self.secondLayerCont.isExpanded and self.secondLayerCont.expandedButton:
            self.UpdateSecondLevel(self.secondLayerCont.expandedButton, animate=False)

    def LoadMyActions(self, doReset = False, animate = False):
        pass

    def AnimateMenuFromCenter(self, sizeRatio = 0.5, opacityRatio = 0.5, duration = 0.25, grow = True, sleep = False, skipBnts = ()):
        curveSet = None
        curveSet = self.firstLayerCont.AnimateFromCenter(curveSet, duration, sizeRatio, opacityRatio, grow, skipBnts)
        curveSet = self.secondLayerCont.AnimateFromCenter(curveSet, duration, sizeRatio, opacityRatio, grow, skipBnts)
        curveSet = self.shadow.AnimateFromCenter(duration, sizeRatio, opacityRatio, grow)
        curveSet = self.rangeCont.AnimateFromCenter(curveSet, duration, opacityRatio, grow, sleep)

    def ClickButton(self, btn):
        self.CleanUp()
        self.state = uiconst.UI_DISABLED
        btnClickThread = uthread.new(btn.actionButton.OnButtonClick)
        btnClickThread.context = 'RadialMenu::ClickButton:OnButtonClick'
        duration = 0.5
        sm.GetService('audio').SendUIEvent('ui_radial_select_play')
        btnClickThread = uthread.new(self.RunClosingAnimation_thread, btn, duration)
        btnClickThread.context = 'RadialMenu::ClickButton:RunClosingAnimation_thread'

    def RunClosingAnimation_thread(self, btn, duration = 0.5):
        self.isClosing = True
        self.CleanUp()
        self.AnimateMenuFromCenter(opacityRatio=0.0, duration=duration * 0.5, grow=False, sleep=False, skipBnts=(btn,))
        btn.actionButton.SelectButtonSlice(duration=duration)
        self.Close()

    @telemetry.ZONE_METHOD
    def GetLengthFromCenter(self):
        aX, bY = self.GetDistancesFromMenuCenter()
        length = geo2.Vec2Length((aX, bY))
        return length

    @telemetry.ZONE_METHOD
    def GetCurrentDegree(self):
        aX, bY = self.GetDistancesFromMenuCenter()
        currentDegree = math.degrees(math.atan2(-aX, bY))
        if currentDegree < 0:
            currentDegree += 360
        return currentDegree

    def GetDistancesFromMenuCenter(self, *args):
        xDistance = self.currentCenterX - self.offsetX - uicore.uilib.x
        yDistance = self.currentCenterY - self.offsetY - uicore.uilib.y
        return (xDistance, yDistance)

    @telemetry.ZONE_METHOD
    def FindMyButton(self, degree, buttonLayer, stepSize):
        return buttonLayer.FindMyButton(degree, stepSize)

    @telemetry.ZONE_METHOD
    def OnGlobalMove(self, *args):
        try:
            self._OnGlobalMove()
        finally:
            return 1

    def _OnGlobalMove(self):
        self.TryRepositionMouse()
        now = blue.os.GetWallclockTime()
        if now - self.lastMoveTime < 250000:
            return
        self.lastMoveTime = now
        if getattr(self, 'isClosing', False):
            return
        length = self.GetLengthFromCenter()
        if length < self.actionDistance - self.buttonHeight + self.buttonPaddingBottom:
            self.ResetFromCenter()
            return
        if not self.IsRadialMenuButtonActive() and length > self.actionDistance - self.sizeInfo.buttonPaddingTop:
            self.ResetFromCenter()
            return
        currentDegree = self.GetCurrentDegree()
        if self.secondLayerCont.isExpanded:
            buttonLayer = self.secondLayerCont
        else:
            buttonLayer = self.firstLayerCont
        if self.selectedBtn and isinstance(self.selectedBtn.actionButton, RadialMenuRangeAction) and length > self.selectedBtn.actionButton.minRangeDistance:
            buttonFound = self.selectedBtn
        else:
            self.rangeCont.display = False
            buttonFound = self.FindMyButton(currentDegree, buttonLayer, self.stepSize)
        self.HiliteOneButton(buttonFound, buttonLayer)
        self.SelectButton(btn=None)
        if buttonFound:
            if isinstance(buttonFound.actionButton, RadialMenuRangeAction):
                moveMouseResults = self.MoveMouseRangeAction(buttonFound, buttonFound.actionButton, length, currentDegree)
            elif isinstance(buttonFound.actionButton, RadialMenuActioSecondLevel):
                uthread.new(self.MoveMouseSecondLevel, buttonFound, buttonFound.actionButton, length, currentDegree)
                self.MoveMouseRangeCallback(usingRangeOption=False)
            else:
                self.SelectButton(buttonFound)
                self.ClearOptionRangeText()
                self.MoveMouseRangeCallback(usingRangeOption=False)
        else:
            self.ClearOptionRangeText()

    def MoveMouseRangeAction(self, buttonCont, actionButton, length, currentDegree):
        moveMouseResults = actionButton.MoveMouse(length, currentDegree)
        if moveMouseResults:
            currentRange, percOfAllRange = moveMouseResults
            self.MoveMouseRangeCallback(usingRangeOption=True, currentRange=currentRange, percOfAllRange=percOfAllRange)
            self.SetOptionRangeText(FmtDist(currentRange))
            self.SetRangeCircle(buttonCont.degree, percOfAllRange)
            self.SelectButton(buttonCont)
        return moveMouseResults

    def MoveMouseRangeCallback(self, usingRangeOption, currentRange = None, percOfAllRange = None):
        pass

    def MoveMouseSecondLevel(self, buttonParent, actionButton, length, currentDegree):
        self.ClearOptionRangeText()
        shouldExpand = actionButton.MoveMouse(length, currentDegree)
        if shouldExpand and not self.secondLayerCont.isExpanded:
            wasLoaded = self.UpdateSecondLevel(buttonParent, animate=True)
            if wasLoaded:
                sm.GetService('audio').SendUIEvent('ui_radial_expand_play')

    def AdjustTextShadow(self):
        if not getattr(self, 'optionLabel', None) or not self.optionLabel.display:
            if getattr(self, 'labelShadow', None):
                self.labelShadow.display = False
            return
        if self.optionRangeLabel.display:
            centerWidth = max(self.optionLabel.textwidth, self.optionRangeLabel.textwidth)
            height = self.optionLabel.textheight + self.optionRangeLabel.textheight + 4
            top = 0
        else:
            centerWidth = self.optionLabel.textwidth
            height = self.optionLabel.textheight + 4
            top = -10
        self.labelShadow.display = True
        self.labelShadow.SetCenterSizeAndTop(centerWidth, height, top=top)

    def UpdateSecondLevel(self, buttonParent, animate = False):
        optionsInfo = self.GetSecondLevelOptions(buttonParent)
        if not optionsInfo or len(optionsInfo.allWantedMenuOptions) < 1:
            return
        self.firstLayerCont.SetOpacity(0.3)
        wasLoaded = self.LoadSecondLevelActions(buttonParent, optionsInfo=optionsInfo, animate=animate)
        if wasLoaded:
            self.secondLayerCont.isExpanded = True
            self.secondLayerCont.expandedButton = buttonParent
            return True
        return False

    def GetSecondLevelOptions(self, buttonParent):
        return None

    def LoadSecondLevelActions(self, buttonParent, optionsInfo = None, animate = False):
        return False

    def OnMouseUp(self, button, *args):
        uicore.uilib.UnclipCursor()
        self.cursorClipped = False
        radialMenuBtn = self.GetRadialMenuButton()
        if radialMenuBtn == button and self.selectedBtn:
            self.ClickButton(self.selectedBtn)
        else:
            self.KillRadialMenu(button)

    def KillRadialMenu(self, button):
        self.CloseWithoutActionCallback(button)
        self.Close()

    def OnMouseUpBlocker(self, button):
        self.OnMouseUp(button)

    def CloseWithoutActionCallback(self, button):
        pass

    @telemetry.ZONE_METHOD
    def HiliteOneButton(self, btnCont, buttonLayer):
        newLabel = buttonLayer.HiliteOneButtonAndGetLabel(btnCont)
        if newLabel:
            self.SetOptionText(newLabel)
        if btnCont is None:
            self.ClearOptionText()
            self.ClearOptionRangeText()

    def SelectButton(self, btn = None):
        self.selectedBtn = btn

    def HideCursor(self):
        self.cursor = uiconst.UICURSOR_NONE
        uicore.UpdateCursor(self, force=True)

    def TryRepositionMouse(self, *args):
        if not self.cursorClipped:
            return
        repositionToCenter = False
        resetToRealPointer = False
        currentMouseX = uicore.uilib.x
        currentMouseY = uicore.uilib.y
        newX = currentMouseX
        newY = currentMouseY
        newOffsetX = self.offsetX
        newOffsetY = self.offsetY
        if (currentMouseX <= 1 or currentMouseX >= uicore.desktop.width - 1) and self.offsetX == 0:
            repositionToCenter = True
            newX = self.halfScreenX
            newOffsetX = uicore.uilib.x - newX
        if (currentMouseY <= 1 or currentMouseY >= uicore.desktop.height - 1) and self.offsetY == 0:
            repositionToCenter = True
            newY = self.halfScreenY
            newOffsetY = uicore.uilib.y - newY
        if not repositionToCenter and self.offsetX == 0 and self.offsetY == 0:
            return
        if self.offsetX < 0 and currentMouseX > abs(self.offsetX) or self.offsetX > 0 and currentMouseX < self.offsetX:
            newX = max(2, min(uicore.uilib.x + self.offsetX, uicore.desktop.width - 2))
            newOffsetX = 0
            resetToRealPointer = True
        if self.offsetY < 0 and currentMouseY > abs(self.offsetY) or self.offsetY > 0 and currentMouseY < self.offsetY:
            newY = max(2, min(uicore.uilib.y + self.offsetY, uicore.desktop.height - 2))
            newOffsetY = 0
            resetToRealPointer = True
        if repositionToCenter or resetToRealPointer:
            self.offsetX = newOffsetX
            self.offsetY = newOffsetY
            if resetToRealPointer and self.offsetX == 0 and self.offsetY == 0:
                self.cursor = uiconst.UICURSOR_SELECT
            else:
                self.cursor = uiconst.UICURSOR_NONE
            uicore.uilib.SetCursorPos(newX, newY)
            uicore.UpdateCursor(self, force=True)

    def ResetFromCenter(self):
        self.rangeCont.display = False
        self.HiliteOneButton(None, self.firstLayerCont)
        self.SelectButton(btn=None)
        self.ResetSecondLevel()
        self.firstLayerCont.SetOpacity(1.0)
        if getattr(self, 'moduleOpacityChanged', False):
            uicore.layer.shipui.ResetModuleButtonOpacity()
            self.moduleOpacityChanged = False

    def SetPosition(self):
        normalX = self.currentCenterX - self.width / 2
        rightMost = uicore.desktop.width - self.width
        if normalX > rightMost:
            left = rightMost
            self.currentCenterX = rightMost + self.width / 2
        else:
            left = normalX
        left = max(0, left)
        normalY = self.currentCenterY - self.height / 2
        bottomMost = uicore.desktop.height - self.height
        if normalY > bottomMost:
            top = bottomMost
            self.currentCenterY = bottomMost + self.height / 2
        else:
            top = normalY
        if getattr(self, 'displayLabelCont', None):
            minTop = self.displayLabelCont.height + 4
        else:
            minTop = 4
        top = max(minTop, top)
        self.currentCenterX = max(left + self.width / 2, self.currentCenterX)
        self.currentCenterY = max(top + self.height / 2, self.currentCenterY)
        uicore.uilib.SetCursorPos(self.currentCenterX, self.currentCenterY)
        self.offsetX = 0
        self.offsetY = 0
        self.left = left
        self.top = top

    def CleanUp(self):
        self.cleanupStarted = True
        self.state = uiconst.UI_DISABLED
        self.ResetCursor()
        if getattr(self, 'blocker', None):
            self.blocker.Close()
        self.updateOptionsTimer = None
        self.displayNameTimer = None
        self.cleanUpDone = True
        if getattr(self, 'mouseMoveCookie', None):
            uicore.event.UnregisterForTriuiEvents(self.mouseMoveCookie)

    def ResetCursor(self):
        try:
            self.ResetCursorPosition()
            uicore.UpdateCursor(uicore.uilib.mouseOver)
            uicore.uilib.UpdateMouseOver()
        except Exception as e:
            self.radialMenuSvc.LogError('Error when resetting the cursor, error = ', e)
            uicore.uilib.SetCursorPos(uicore.desktop.width / 2, uicore.desktop.height / 2)

    def ResetCursorPosition(self, *args):
        try:
            leftPos = max(0, min(uicore.uilib.x + self.offsetX, uicore.desktop.width))
            topPos = max(0, min(uicore.uilib.y + self.offsetY, uicore.desktop.height))
            uicore.uilib.SetCursorPos(leftPos, topPos)
        except:
            uicore.uilib.SetCursorPos(uicore.desktop.width / 2, uicore.desktop.height / 2)

    def _OnClose(self, *args):
        if not getattr(self, 'cleanUpDone', False):
            self.CleanUp()
        sm.GetService('audio').SendUIEvent('ui_radial_close')
        super(RadialMenu, self)._OnClose(*args)
        self.clickedObject = None

    def SetRangeCircle(self, degree, percOfAllRange):
        self.rangeCont.SetRangeCircle(degree, percOfAllRange)
        if percOfAllRange is None:
            self.AdjustTextShadow()

    def ResetSecondLevel(self):
        self.secondLayerCont.display = False
        self.secondLayerCont.isExpanded = False
        self.secondLayerCont.expandedButton = None

    def LoadButtons(self, parentLayer, optionsInfo, alternate = False, startingDegree = 0, animate = False, doReset = False):
        if getattr(self, 'busyReloading', False):
            return
        self.busyReloading = True
        parentLayer.LoadButtons(self.itemID, self.stepSize, alternate, animate, doReset, optionsInfo, startingDegree, self.GetIconTexturePath)
        self.OnGlobalMove()
        self.busyReloading = False

    def GetIconTexturePath(self, activeOption, menuOptions = None):
        return None

    def GetMyActions(self):
        return None

    def UpdateDisplayName(self):
        pass

    def UpdateIndicator(self):
        pass

    def OnSettingsOpened(self):
        self.KillRadialMenu(None)


class ThreePartContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        leftTexturePath = attributes.leftTexturePath
        rightTexturePath = attributes.rightTexturePath
        centerTexturePath = attributes.centerTexturePath
        orientation = attributes.get('orientation', 'horizontal')
        self.sideSize = attributes.sideSize
        color = attributes.get('color', (0, 0, 0, 0.5))
        if orientation == 'vertical':
            leftSide = Container(parent=self, name='leftSide', height=self.sideSize, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
            rightSide = Container(parent=self, name='rightSide', height=self.sideSize, align=uiconst.TOBOTTOM, state=uiconst.UI_DISABLED)
        else:
            leftSide = Container(parent=self, name='leftSide', width=self.sideSize, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED)
            rightSide = Container(parent=self, name='rightSide', width=self.sideSize, align=uiconst.TORIGHT, state=uiconst.UI_DISABLED)
        leftTexture = Sprite(parent=leftSide, name='leftTexture', pos=(0, 0, 0, 0), texturePath=leftTexturePath, align=uiconst.TOALL, color=color, idx=0)
        rightTexture = Sprite(parent=rightSide, name='rightTexture', pos=(0, 0, 0, 0), texturePath=rightTexturePath, align=uiconst.TOALL, color=color, idx=0)
        centerTexture = Sprite(parent=self, name='centerTexture', pos=(0, 0, 0, 0), texturePath=centerTexturePath, align=uiconst.TOALL, color=color)

    def SetCenterSizeAndTop(self, centerWidth, height, top = None):
        self.width = centerWidth + 2 * self.sideSize
        self.height = height
        if top is not None:
            self.top = top


class RadialMenuSpace(RadialMenu):
    default_usePreciseRanges = False
    CLICKCOUNTRESETTIME = 250

    def SetSpecificValues(self, attributes):
        slimItem = attributes.slimItem
        self.slimItem = slimItem
        self.itemID = attributes.itemID
        self.manyItemsData = attributes.get('manyItemsData', None)
        self.bookmarkInfo = attributes.get('bookmarkInfo', None)
        self.typeID = attributes.get('typeID', None)
        self.siteData = attributes.get('siteData', None)
        self.SetFallbackDisplayName()

    def SetFallbackDisplayName(self, *args):
        try:
            if self.manyItemsData:
                self.fallBackDisplayName = self.manyItemsData.displayName
            elif self.siteData:
                self.fallBackDisplayName = self.siteData.GetName()
            else:
                self.fallBackDisplayName = cfg.evelocations.Get(self.itemID).name
        except:
            self.fallBackDisplayName = ''

    def LoadMyActions(self, doReset = False, animate = False):
        self.SetSlimItemAndItemIDIfNeeded()
        optionsInfo = spaceRadialMenuFunctions.FindRadialMenuOptions(slimItem=self.slimItem, itemID=self.itemID, typeID=self.typeID, bookmarkInfo=self.bookmarkInfo, manyItemsData=self.manyItemsData, siteData=self.siteData, menuType=self.menuType)
        if optionsInfo is None:
            return
        if self.itemID is None and self.slimItem is not None:
            self.itemID = self.slimItem.itemID
        self.LoadButtons(self.firstLayerCont, optionsInfo, doReset=doReset)
        if animate:
            self.AnimateMenuFromCenter(duration=0.1)

    def LoadSecondLevelActions(self, buttonParent, optionsInfo = None, animate = False):
        self.SetSlimItemAndItemIDIfNeeded()
        if not optionsInfo:
            optionsInfo = self.GetSecondLevelOptions(buttonParent)
        if optionsInfo is None:
            return False
        if self.itemID is None and self.slimItem is not None:
            self.itemID = self.slimItem.itemID
        self.secondLayerCont.display = True
        self.LoadButtons(self.secondLayerCont, optionsInfo, alternate=True, startingDegree=buttonParent.degree, doReset=animate, animate=animate)
        return True

    def GetSecondLevelOptions(self, buttonParent):
        if self.itemID is None and self.slimItem is not None:
            self.itemID = self.slimItem.itemID
        return spaceRadialMenuFunctions.FindRadialMenuOptions(slimItem=self.slimItem, itemID=self.itemID, typeID=self.typeID, primaryActions=False, bookmarkInfo=self.bookmarkInfo, manyItemsData=self.manyItemsData, siteData=self.siteData, menuType=self.menuType)

    def GetIconTexturePath(self, activeOption, menuOptions = None):
        texturePath = spaceRadialMenuFunctions.GetIconPath(activeOption)
        return texturePath

    def MoveMouseRangeCallback(self, usingRangeOption, currentRange = None, percOfAllRange = None):
        if usingRangeOption:
            uicore.layer.shipui.ChangeOpacityForRange(currentRange=currentRange)
            self.moduleOpacityChanged = True
        elif getattr(self, 'moduleOpacityChanged', False):
            uicore.layer.shipui.ResetModuleButtonOpacity()
            self.moduleOpacityChanged = False

    def IsRadialMenuButtonActive(self, *args):
        return spaceRadialMenuFunctions.IsRadialMenuButtonActive()

    def GetRadialMenuButton(self, *args):
        actionmenuBtn = settings.user.ui.Get('actionmenuBtn', uiconst.MOUSELEFT)
        if self.menuType == BROADCAST_RADIAL_MENU:
            btn = GetSingleMouseBtnBroadcastRadialMenu()
            if btn:
                return btn
        return actionmenuBtn

    def _OnClose(self, *args):
        if self.clickedObject and hasattr(self.clickedObject, 'HideRadialMenuIndicator'):
            self.clickedObject.HideRadialMenuIndicator(self.slimItem)
        RadialMenu._OnClose(self, *args)
        uicore.layer.shipui.ResetModuleButtonOpacity()
        uicore.layer.menu.radialMenu = None

    def UpdateDisplayName(self):
        displayName = ''
        if self.itemID == session.shipid and self.slimItem:
            shipCategory = evetypes.GetGroupNameByGroup(self.slimItem.groupID)
            displayName = localization.GetByLabel('UI/Inflight/ActionButtonsYourShipWithCategory', categoryOfYourShip=shipCategory)
        elif self.manyItemsData and self.fallBackDisplayName:
            displayName = self.fallBackDisplayName
        elif self.slimItem:
            displayName = uix.GetSlimItemName(self.slimItem)
            bp = sm.StartService('michelle').GetBallpark()
            if bp:
                ball = bp.GetBall(self.itemID)
                if ball:
                    displayName += ' ' + FmtDist(ball.surfaceDist)
        elif self.bookmarkInfo:
            displayName = self.bookmarkInfo.memo
            displayName = displayName.strip('\t')
        elif self.fallBackDisplayName:
            displayName = self.fallBackDisplayName
        displayName = '<b>%s</b>' % displayName
        self.SetDisplayName(displayName)

    def SetDisplayName(self, displayName, *args):
        if displayName != self.displayName:
            self.displayLabel.text = displayName
            height = self.displayLabel.textheight + 2
            centerWidth = self.displayLabel.textwidth
            self.displayLabelCont.SetCenterSizeAndTop(centerWidth, height)
            self.displayLabelCont.display = True
            self.displayName = displayName
        elif not displayName:
            self.displayLabelCont.display = False

    def SetSlimItemAndItemIDIfNeeded(self, *args):
        pass

    def UpdateIndicator(self, *args):
        if self.clickedObject and hasattr(self.clickedObject, 'ShowRadialMenuIndicator'):
            self.clickedObject.ShowRadialMenuIndicator(self.slimItem)

    def CloseWithoutActionCallback(self, button):
        if self.clickedObject is None:
            return
        now = blue.os.GetWallclockTime()
        diff = now - self.creationTime
        if diff > self.CLICKCOUNTRESETTIME * const.MSEC:
            return
        xDistance = self.currentCenterX - self.offsetX - uicore.uilib.x
        yDistance = self.currentCenterY - self.offsetY - uicore.uilib.y
        menuButton = self.GetRadialMenuButton()
        if xDistance != 0 or yDistance != 0:
            return
        if menuButton not in (uiconst.MOUSELEFT, uiconst.MOUSERIGHT):
            return
        self.blocker.display = False
        if menuButton == uiconst.MOUSELEFT:
            uthread.new(self.clickedObject.OnMouseUp, button)
            uthread.new(self.clickedObject.OnClick)
        elif menuButton == uiconst.MOUSERIGHT:
            if uicore.uilib.leftbtn:
                return
            if getattr(self.clickedObject, 'GetMenu', None):
                uthread.new(ShowMenu, self.clickedObject, uicore.uilib.GetAuxMouseOver())


class RadialMenuSpaceCharacter(RadialMenuSpace):
    __guid__ = 'uicls.RadialMenuSpaceCharacter'

    def SetSpecificValues(self, attributes):
        RadialMenuSpace.SetSpecificValues(self, attributes)
        self.charID = attributes.charID

    def SetSlimItemAndItemIDIfNeeded(self, *args):
        if self.slimItem is None and self.charID is not None:
            self.slimItem = SlimItemFromCharID(self.charID)
            if self.slimItem is not None:
                self.itemID = self.slimItem.itemID

    def UpdateDisplayName(self):
        if self.itemID == session.shipid or self.slimItem:
            return RadialMenuSpace.UpdateDisplayName(self)
        if self.charID:
            displayName = '<b>%s' % cfg.eveowners.Get(self.charID).name
            self.SetDisplayName(displayName)


class RadialMenuInventory(RadialMenuSpace):

    def SetSpecificValues(self, attributes):
        RadialMenuSpace.SetSpecificValues(self, attributes)
        self.rec = attributes.rec

    def LoadMyActions(self, doReset = False, animate = False):
        optionsInfo = inventoryRadialMenuFunctions.FindRadialMenuOptions(itemID=self.itemID, typeID=self.typeID, manyItemsData=self.manyItemsData, rec=self.rec)
        if optionsInfo is None:
            return
        self.LoadButtons(self.firstLayerCont, optionsInfo, doReset=doReset)
        if animate:
            self.AnimateMenuFromCenter(duration=0.1)

    def LoadSecondLevelActions(self, buttonParent, optionsInfo = None, animate = False):
        if not optionsInfo:
            optionsInfo = self.GetSecondLevelOptions(buttonParent)
        if optionsInfo is None:
            return False
        self.secondLayerCont.display = True
        self.LoadButtons(self.secondLayerCont, optionsInfo, alternate=True, startingDegree=buttonParent.degree, doReset=animate, animate=animate)
        return True

    def GetSecondLevelOptions(self, buttonParent):
        levelType = buttonParent.levelType
        return inventoryRadialMenuFunctions.FindRadialMenuOptions(itemID=self.itemID, typeID=self.typeID, primaryActions=False, manyItemsData=self.manyItemsData, rec=self.rec, levelType=levelType)

    def GetIconTexturePath(self, activeOption, menuOptions = None):
        texturePath = inventoryRadialMenuFunctions.GetIconPath(activeOption)
        return texturePath


RMTEST_SizeInfo = RadialMenuSizeInfo(width=118, height=118, shadowSize=130, rangeSize=50, sliceCount=4, buttonWidth=84, buttonHeight=49, buttonPaddingTop=5, buttonPaddingBottom=5, actionDistance=59)

class RadialMenuTest(RadialMenu):
    default_left = 0
    default_top = 0
    default_align = uiconst.TOPLEFT
    default_width = RMTEST_SizeInfo.width
    default_height = RMTEST_SizeInfo.height
    sizeInfo = RMTEST_SizeInfo
    default_showActionText = False

    def LoadMyActions(self, doReset = False, animate = False):
        optionsInfo = self.GetMyActions()
        if optionsInfo is None:
            return
        self.LoadButtons(self.firstLayerCont, optionsInfo, doReset=doReset)
        if animate:
            self.AnimateMenuFromCenter(duration=0.1)

    def GetMyActions(self, *args):
        inactiveRangeOptions = set()
        allWantedMenuOptions = [RangeRadialMenuAction(optionPath='UI/Inflight/OrbitObject', rangeList=[1, 2, 3], defaultRange=2, callback=self.Orbit, iconPath='res:/UI/Texture/Icons/44_32_27.png'),
         SimpleRadialMenuAction(option1='a', func=self.TestA, iconPath='res:/UI/Texture/Icons/44_32_24.png'),
         SimpleRadialMenuAction(option1='b', func=self.TestB, iconPath='res:/UI/Texture/Icons/44_32_25.png'),
         SimpleRadialMenuAction(option1='c', func=self.TestC, iconPath='res:/UI/Texture/Icons/44_32_26.png')]
        activeSingleOptions = {'b': allWantedMenuOptions[1],
         'c': allWantedMenuOptions[2]}
        activeRangeOptions = {'UI/Inflight/OrbitObject': allWantedMenuOptions[0]}
        inactiveSingleOptions = set(('a', 'd'))
        optionsInfo = RadialMenuOptionsInfo(allWantedMenuOptions=allWantedMenuOptions, activeSingleOptions=activeSingleOptions, inactiveSingleOptions=inactiveSingleOptions, activeRangeOptions=activeRangeOptions, inactiveRangeOptions=inactiveRangeOptions)
        return optionsInfo

    def TestA(self, *args):
        print 'TestAx'

    def TestB(self, *args):
        print '~~~~ TestB'

    def TestC(self, *args):
        print 'TestC'

    def TestD(self, *args):
        print 'TestD'

    def GetIconTexturePath(self, activeOption, menuOptions = None, *args):
        return menuOptions.iconPath

    def Orbit(self, itemID, value, *args):
        print 'value = ', value
