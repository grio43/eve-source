#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\dockPanel.py
import logging
import blue
import eveicon
from carbonui.button.menu import MenuButtonIcon
from carbonui.control.buttonIcon import ButtonIcon
from mathext import clamp
import localization
import uthread
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.primitives.base import Base
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.uicore import uicore
from carbonui.window.resizer import Side
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from carbonui.loggers.message_bus.windowMessenger import WindowMessenger, DOCKING_MODES_CONVERSION
from eve.client.script.ui.control.themeColored import FillThemeColored, StretchSpriteHorizontalThemeColored
from eve.client.script.ui.shared.infoPanels.const import infoPanelUIConst
from eve.client.script.ui.shared.infoPanels.infoPanelContainer import InfoPanelContainer
from eve.client.script.ui.shared.mapView.dockPanelUtil import GetDockPanelManager, GetPanelSettings, RegisterPanelSettings
from eveexceptions import EatsExceptions
logger = logging.getLogger(__name__)
TOOLBARWIDTH_FULLSCREEN = 400
TOOLBARHEIGHT = 26
BUTTON_FULLSCREEN = 1
BUTTON_DOCKLEFT = 2
BUTTON_DOCKRIGHT = 3
BUTTON_FLOAT = 4
BUTTON_DATA_BY_ID = {BUTTON_FULLSCREEN: ('res:/UI/Texture/classes/DockPanel/fullscreenButton.png', 'UI/Control/DockPanel/Fullscreen'),
 BUTTON_DOCKLEFT: ('res:/UI/Texture/classes/DockPanel/dockLeftButton.png', 'UI/Control/DockPanel/DockLeft'),
 BUTTON_DOCKRIGHT: ('res:/UI/Texture/classes/DockPanel/dockRightButton.png', 'UI/Control/DockPanel/DockRight'),
 BUTTON_FLOAT: ('res:/UI/Texture/classes/DockPanel/floatButton.png', 'UI/Control/DockPanel/Floating')}
SNAP_RELEASE_THRESHOLD = 5
SNAP_INDICATOR_SIZE = 2

class DockablePanelHeaderButton(ButtonIcon):
    default_width = 16
    default_height = 16
    default_minSize = (300, 300)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipDelay(self):
        return 5

    def GetTooltipPositionFallbacks(self, *args, **kwds):
        return [uiconst.POINT_TOP_2,
         uiconst.POINT_TOP_1,
         uiconst.POINT_TOP_3,
         uiconst.POINT_BOTTOM_2,
         uiconst.POINT_BOTTOM_1,
         uiconst.POINT_BOTTOM_3]


class DockablePanelHeaderButtonMenu(DockablePanelHeaderButton):
    callback = None
    tooltipPanelMenu = None

    def __init__(self, dock_options, **kw):
        super(DockablePanelHeaderButtonMenu, self).__init__(**kw)
        self.dock_options = dock_options

    def ApplyAttributes(self, attributes):
        DockablePanelHeaderButton.ApplyAttributes(self, attributes)
        self.panelID = attributes.panelID
        self.callback = attributes.dockViewModeCallback
        self.UpdateButtonState()

    def Close(self, *args, **kwds):
        DockablePanelHeaderButton.Close(self)
        self.callback = None
        self.tooltipPanelMenu = None

    def UpdateButtonState(self):
        currentSetting = GetPanelSettings(self.panelID)
        align = currentSetting['align']
        if align == uiconst.TOALL:
            buttonID = BUTTON_FULLSCREEN
        elif align == uiconst.TOLEFT:
            buttonID = BUTTON_DOCKLEFT
        elif align == uiconst.TORIGHT:
            buttonID = BUTTON_DOCKRIGHT
        else:
            buttonID = BUTTON_FLOAT
        texturePath, labelPath = BUTTON_DATA_BY_ID[buttonID]
        self.SetTexturePath(texturePath)

    def GetTooltipPointer(self):
        return uiconst.POINT_TOP_1

    def GetTooltipDelay(self):
        return 5

    def GetTooltipPositionFallbacks(self, *args, **kwds):
        return [uiconst.POINT_TOP_2,
         uiconst.POINT_TOP_1,
         uiconst.POINT_TOP_3,
         uiconst.POINT_BOTTOM_2,
         uiconst.POINT_BOTTOM_1,
         uiconst.POINT_BOTTOM_3]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.columns = 2
        tooltipPanel.margin = 4
        for buttonID in self.dock_options:
            texturePath, labelPath = BUTTON_DATA_BY_ID[buttonID]
            tooltipPanel.AddRow(rowClass=ButtonTooltipRow, buttonID=buttonID, texturePath=texturePath, label=localization.GetByLabel(labelPath), callback=self._LocalCallback)

        tooltipPanel.state = uiconst.UI_NORMAL
        self.tooltipPanelMenu = tooltipPanel

    def _LocalCallback(self, buttonID):
        if self.tooltipPanelMenu and not self.tooltipPanelMenu.destroyed:
            self.tooltipPanelMenu.state = uiconst.UI_HIDDEN
        if self.callback:
            self.callback(buttonID)
        self.UpdateButtonState()


class ButtonTooltipRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    callback = None
    buttonID = None

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.callback = attributes.callback
        self.buttonID = attributes.buttonID
        self.icon = ButtonIcon(pos=(0, 0, 16, 16), texturePath=attributes.texturePath, state=uiconst.UI_DISABLED)
        self.AddCell(cellObject=self.icon, cellPadding=(3, 2, 3, 2))
        label = EveLabelMedium(text=attributes.label, align=uiconst.CENTERLEFT)
        self.AddCell(cellObject=label, cellPadding=(0, 1, 6, 1))
        self.highLight = Fill(bgParent=self, color=(1, 1, 1, 0.1), state=uiconst.UI_HIDDEN)

    def Close(self, *args):
        LayoutGridRow.Close(self, *args)
        self.callback = None

    def OnMouseEnter(self, *args):
        self.icon.OnMouseEnter()
        self.highLight.display = True

    def OnMouseExit(self, *args):
        self.icon.OnMouseExit()
        self.highLight.display = False

    def OnClick(self, *args):
        if self.callback:
            self.callback(self.buttonID)


class DockablePanel(Window):
    default_captionLabelPath = None
    default_isStackable = False
    default_performFitsCheck = True
    default_isLightBackgroundConfigurable = False
    dock_options = (BUTTON_FULLSCREEN,
     BUTTON_DOCKLEFT,
     BUTTON_DOCKRIGHT,
     BUTTON_FLOAT)
    panelSize = (500, 500)
    panelID = None
    toolbarContainer = None
    snapToDockMode = None
    snapIndicator = None
    viewState = None
    hasImmersiveAudioOverlay = False
    __notifyevents__ = ['OnViewStateChanged']

    def ApplyAttributes(self, attributes):
        self._immersiveAudioOverlay = None
        self._caption_label = None
        attributes.windowID = attributes.panelID or self.panelID
        attributes.parent = attributes.parent or uicore.layer.main
        self.performFitsCheck = attributes.get('performFitsCheck', self.default_performFitsCheck)
        Window.ApplyAttributes(self, attributes)
        GetDockPanelManager()
        mainArea = self.GetMainArea()
        mainArea.padding = 2
        mainArea.state = uiconst.UI_NORMAL
        self.CreateToolbar()
        self.panelID = attributes.panelID or self.panelID
        uicore.dockablePanelManager.RegisterPanel(self)
        self.ConstructSidePanel()
        if self.hasImmersiveAudioOverlay:
            self._CreateImmersiveAudioOverlay()

    def ConstructSidePanel(self):
        self.sidePanel = Container(parent=self.GetMainArea(), name='sidePanel', align=uiconst.TOLEFT_NOPUSH, width=infoPanelUIConst.PANELWIDTH, padding=(0, 30, 0, 0), idx=0)
        self.infoPanelContainer = InfoPanelContainer(parent=self.sidePanel, align=uiconst.TOTOP, settingsID='%s_dockablePanel' % self.windowID, performFitsCheck=self.performFitsCheck)

    def OnViewStateChanged(self, from_view, to_view):
        if not self.IsFullscreen():
            return
        fullScreenView = self.GetFullscreenViewStateName()
        viewStateSvc = sm.GetService('viewState')
        if fullScreenView and from_view == fullScreenView and viewStateSvc.GetViewInfo(to_view).IsSecondary():
            self.Minimize()

    def GetFullscreenViewStateName(self):
        return self.viewState

    def SetOrder(self, idx):
        if not self.IsFloating():
            return
        return Window.SetOrder(self, idx)

    def InitializeStatesAndPosition(self, *args, **kw):
        self.InitDockPanelPosition()
        self._SetOpen(True)
        if self.IsMinimized():
            self._SetMaximized()

    def GetRegisteredPushedByIndex(self):
        currentSettings = self.GetPanelSettings()
        pushedBy = currentSettings['pushedBy']
        if pushedBy:
            for objectName in reversed(pushedBy):
                for obj in uicore.layer.sidePanels.children:
                    if obj.name == objectName:
                        index = uicore.layer.sidePanels.children.index(obj) + 1
                        return index

        return 0

    def GetFullScreenViewsOrdered(self):
        return [ panel for panel in uicore.layer.sidePanels.children if isinstance(panel, DockablePanel) and panel.IsFullscreen() ]

    def InitDockPanelPosition(self):
        currentSettings = self.GetPanelSettings()
        if currentSettings['align'] == uiconst.TOPLEFT:
            self.UnDock()
        elif currentSettings['align'] == uiconst.TOLEFT:
            self.DockOnLeft()
        elif currentSettings['align'] == uiconst.TORIGHT:
            self.DockOnRight()
        elif currentSettings['align'] == uiconst.TOALL:
            self.DockFullscreen()
        self.state = uiconst.UI_NORMAL

    def GetAbsolutePosition(self):
        stack = self.GetStack()
        if stack:
            return stack.contentCont.GetAbsolutePosition()
        return Base.GetAbsolutePosition(self)

    def InitializeSize(self, *args, **kwds):
        pass

    def RegisterPositionAndSize(self, *args, **kwds):
        pass

    def ToggleCollapse(self, *args, **kwds):
        pass

    def ToggleMinimize(self):
        if not self.IsFullscreen():
            return Window.ToggleMinimize(self)
        if self.IsMinimizable():
            if self.IsMinimized():
                self.Maximize()
            else:
                self.Minimize()

    def Minimize(self, animate = True):
        if self.GetFullscreenViewStateName() and self.IsFullscreen():
            uthread.new(sm.GetService('viewState').CloseSecondaryView, self.GetFullscreenViewStateName())
        if self._immersiveAudioOverlay:
            self._immersiveAudioOverlay.set_minimized()
        super(DockablePanel, self).Minimize(animate)

    def Collapse(self, *args, **kwds):
        pass

    def Prepare_Header_(self):
        if self.sr.headerParent:
            self.sr.headerParent.Close()
        self.sr.headerParent = Container(parent=self.sr.maincontainer, name='__headerParent', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOTOP_NOPUSH, clipChildren=True, pos=(0,
         0,
         0,
         TOOLBARHEIGHT + 2), padding=2, idx=0)
        self.headerParent = self.sr.headerParent

    def _is_side_resizable(self, side):
        if self.IsFullscreen():
            return False
        elif self.IsDockedLeft() and side != Side.RIGHT:
            return False
        elif self.IsDockedRight() and side != Side.LEFT:
            return False
        else:
            return super(DockablePanel, self)._is_side_resizable(side)

    @classmethod
    def GetIfOpen(cls, *args, **kwds):
        dockablePanelManager = GetDockPanelManager()
        return dockablePanelManager.GetIfOpen(cls.panelID)

    @classmethod
    def CloseIfOpen(cls, *args, **kwds):
        dockablePanelManager = GetDockPanelManager()
        panel = dockablePanelManager.GetIfOpen(cls.panelID)
        if panel:
            panel.CloseByUser()
            return True
        return False

    @classmethod
    def Open(cls, *args, **kwds):
        dockablePanelManager = GetDockPanelManager()
        panel = dockablePanelManager.GetIfOpen(cls.panelID)
        if panel:
            return panel
        return cls(*args, **kwds)

    def CreateToolbar(self):
        self.toolbarContainer = Container(parent=self.headerParent, name='toolbarContainer', align=uiconst.CENTERTOP, width=TOOLBARWIDTH_FULLSCREEN, height=TOOLBARHEIGHT, state=uiconst.UI_NORMAL)
        self.toolbarContainer.DelegateEvents(self)
        self._caption_label = EveLabelMediumBold(parent=self.toolbarContainer, align=uiconst.CENTER, text=self.caption)
        FillThemeColored(bgParent=self.toolbarContainer, opacity=0.9, padding=(1, 1, 1, 0))
        grid = LayoutGrid(parent=self.toolbarContainer, columns=5, cellPadding=2, align=uiconst.CENTERRIGHT, left=6)
        self.menuButton = MenuButtonIcon(name='DockPanel_MenuButton', parent=grid, texturePath=eveicon.more_vertical, get_menu_func=self.GetMenuMoreOptions, height=16, width=16)
        self.menuButton.display = False
        self.dockViewModeButton = DockablePanelHeaderButtonMenu(name='DockPanel_HeaderButton_ChangeViewMode', parent=grid, dockViewModeCallback=self.ChangeViewMode, panelID=self.panelID, dock_options=self.dock_options)
        DockablePanelHeaderButton(name='DockPanel_HeaderButton_Minimize', parent=grid, hint=localization.GetByLabel('/Carbon/UI/Controls/Window/Minimize'), texturePath='res:/UI/Texture/classes/DockPanel/minimizeButton.png', func=self.Minimize)
        DockablePanelHeaderButton(name='DockPanel_HeaderButton_Close', parent=grid, hint=localization.GetByLabel('UI/Generic/Close'), texturePath='res:/UI/Texture/classes/DockPanel/closeButton.png', func=self.CloseByUser)
        StretchSpriteHorizontalThemeColored(texturePath='res:/UI/Texture/classes/MapView/toolbarLine.png', colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=uiconst.OPACITY_FRAME, leftEdgeSize=64, rightEdgeSize=64, parent=self.toolbarContainer, align=uiconst.TOBOTTOM_NOPUSH, padding=(-48, 0, -48, -15), height=64)
        StretchSpriteHorizontalThemeColored(texturePath='res:/UI/Texture/classes/MapView/toolbarFill.png', colorType=uiconst.COLORTYPE_UIBASE, leftEdgeSize=64, rightEdgeSize=64, parent=self.toolbarContainer, align=uiconst.TOBOTTOM_NOPUSH, padding=(-48, 0, -48, -15), height=64)

    def Close(self, setClosed = False, *args, **kwds):
        if self.destroyed:
            return
        Window.Close(self, setClosed=setClosed, *args)
        if self.snapIndicator and not self.snapIndicator.destroyed:
            self.snapIndicator.Close()
            self.snapIndicator = None
        uicore.dockablePanelManager.UnregisterPanel(self)
        if self.GetFullscreenViewStateName() and self.IsFullscreen():
            sm.GetService('viewState').CloseSecondaryView(self.GetFullscreenViewStateName())
        if self._immersiveAudioOverlay:
            self._immersiveAudioOverlay.close()
            self._immersiveAudioOverlay = None

    def ChangeViewMode(self, buttonID, *args, **kwds):
        if buttonID == BUTTON_FULLSCREEN:
            if not self.IsFullscreen():
                self.DockFullscreen()
        elif buttonID == BUTTON_DOCKLEFT:
            self.DockOnLeft()
        elif buttonID == BUTTON_DOCKRIGHT:
            self.DockOnRight()
        else:
            self.UnDock()

    def _OnCaptionChanged(self):
        if self._caption_label:
            self._caption_label.text = self.caption

    def IsFullscreen(self):
        return self.align == uiconst.TOALL

    def IsDockedLeft(self):
        return self.align == uiconst.TOLEFT

    def IsDockedRight(self):
        return self.align == uiconst.TORIGHT

    def IsFloating(self):
        return self.align == uiconst.TOPLEFT

    @apply
    def displayRect():
        fget = Container.displayRect.fget

        def fset(self, value):
            Container.displayRect.fset(self, value)
            uicore.dockablePanelManager.UpdateCameraCenter()

        return property(**locals())

    def GetPanelSettings(self):
        return GetPanelSettings(self.panelID)

    def RegisterPanelSettings(self):
        if not self.panelID:
            return
        current = self.GetPanelSettings()
        current['align'] = self.align
        if not self.IsFullscreen():
            current['dblToggleFullScreenAlign'] = self.align
        if self.IsFloating():
            current['positionX'] = (self.left + self.width / 2) / float(uicore.desktop.width)
            current['positionY'] = (self.top + self.height / 2) / float(uicore.desktop.height)
            current['heightProportion'] = self.height / float(uicore.desktop.height)
            current['widthProportion'] = self.width / float(uicore.desktop.width)
        elif self.align in (uiconst.TOLEFT, uiconst.TORIGHT):
            current['widthProportion_docked'] = min(0.5, self.width / float(uicore.desktop.width))
            current['heightProportion_docked'] = 1.0
        RegisterPanelSettings(self.panelID, current)
        if self.align in (uiconst.TOLEFT, uiconst.TORIGHT):
            uicore.dockablePanelManager.UpdatePanelsPushedBySettings()
        self.dockViewModeButton.UpdateButtonState()

    def CloseByUser(self, *args):
        if not self.destroyed and self.IsClosable():
            self._LogWindowClosed()
            PlaySound(uiconst.SOUND_CLOSE)
            uthread.new(self.Close, True)

    def _StartScale(self, sides):
        if self.align == uiconst.TOALL:
            return
        self.scaleData = (self.left,
         self.top,
         self.width,
         self.height)
        if 'left' in sides and self.align != uiconst.TOLEFT:
            modX = -1
        elif 'right' in sides and self.align != uiconst.TORIGHT:
            modX = 1
        else:
            modX = 0
        if 'top' in sides:
            modY = -1
        elif 'bottom' in sides:
            modY = 1
        else:
            modY = 0
        if not (modX or modY):
            return
        self.scaleModifiers = (modX, modY)
        self._scaling = True
        uthread.new(self.OnScale, uicore.uilib.x, uicore.uilib.y)

    def OnDblClick(self, *args, **kwds):
        if self.IsFullscreen():
            currentSettings = self.GetPanelSettings()
            currentSettings['align'] = currentSettings['dblToggleFullScreenAlign']
            RegisterPanelSettings(self.panelID, currentSettings)
            self.InitDockPanelPosition()
        else:
            self.DockFullscreen()

    def OnScale(self, initMouseX, initMouseY):
        while self._scaling and uicore.uilib.leftbtn and not self.destroyed:
            mouseX, mouseY = uicore.uilib.x, uicore.uilib.y
            dX = mouseX - initMouseX
            dY = mouseY - initMouseY
            l, t, w, h = self.scaleData
            widthMod, heightMod = self.scaleModifiers
            if widthMod:
                newWidth = max(self.GetMinWidth(), w - dX * -widthMod)
                if self.align in (uiconst.TOLEFT, uiconst.TORIGHT):
                    newWidth = min(uicore.desktop.width / 2, newWidth)
                self.width = newWidth
                if widthMod < 0 and self.IsFloating():
                    self.left = l + w - newWidth
            if heightMod and self.IsFloating():
                newHeight = max(self.GetMinHeight(), h - dY * -heightMod)
                self.height = newHeight
                if heightMod < 0:
                    self.top = t + h - newHeight
            self.RegisterPanelSettings()
            blue.pyos.synchro.SleepWallclock(1)

        self.ValidateWindows()
        self.RegisterPanelSettings()

    def OnScaleMove(self, dX, dY, scaleModifiers):
        if self.align == uiconst.TOALL:
            return
        l, t, w, h = self.scaleData
        widthMod, heightMod = self.scaleModifiers
        if widthMod:
            newWidth = max(self.GetMinWidth(), w - dX * -widthMod)
            self.width = newWidth
            if widthMod < 0 and self.IsFloating():
                self.left = l + w - newWidth
        if heightMod and self.IsFloating():
            newHeight = max(self.GetMinHeight(), h - dY * -heightMod)
            self.height = newHeight
            if heightMod < 0:
                self.top = t + h - newHeight
        self.RegisterPanelSettings()

    def DockFullscreen(self, *args):
        if self.destroyed:
            return
        fullScreenViews = self.GetFullScreenViewsOrdered()
        self.SetParent(uicore.layer.sidePanels)
        self.toolbarContainer.align = uiconst.CENTERTOP
        self.align = uiconst.TOALL
        self.width = 0
        self.height = 0
        self.left = 0
        self.top = 0
        self.FinalizeModeChange()
        for each in fullScreenViews:
            each.SetParent(uicore.layer.sidePanels, -1)

        self._CheckActivateFullScreenViewState()

    def _CheckActivateFullScreenViewState(self):
        currViewName = sm.GetService('viewState').GetActiveViewName()
        fullScreenViewName = self.GetFullscreenViewStateName()
        if fullScreenViewName and currViewName != fullScreenViewName:
            self.ActivateViewStateView()

    def DockOnRight(self, index = None, *args):
        if index is None:
            index = self.GetRegisteredPushedByIndex()
        self._DockOnSide(align=uiconst.TORIGHT, index=index)

    def DockOnLeft(self, index = None, *args):
        if index is None:
            index = self.GetRegisteredPushedByIndex()
        self._DockOnSide(align=uiconst.TOLEFT, index=index)

    def _DockOnSide(self, align, index = 0):
        current = self.GetPanelSettings()
        self.SetParent(uicore.layer.sidePanels, idx=index)
        self.toolbarContainer.align = uiconst.TOTOP_NOPUSH
        self.align = align
        minWidth = min(self.GetMinWidth(), uicore.desktop.width / 2.0)
        width = int(current['widthProportion_docked'] * uicore.desktop.width)
        self.width = max(minWidth, min(width, uicore.desktop.width / 2.0))
        self.height = 0
        self.left = 0
        self.top = 0
        self.FinalizeModeChange()
        if self.GetFullscreenViewStateName():
            self.CloseViewStateView()

    def UnDock(self, setPosition = True, registerSettings = True, *args):
        if self.destroyed:
            return
        current = self.GetPanelSettings()
        if self.parent != uicore.layer.main:
            self.SetParent(uicore.layer.main, idx=0)
        self.toolbarContainer.align = uiconst.TOTOP_NOPUSH
        self.toolbarContainer.SetParent(self.headerParent, idx=0)
        self.align = uiconst.TOPLEFT
        self.width = max(self.GetMinWidth(), int(current['widthProportion'] * uicore.desktop.width))
        self.height = max(self.GetMinHeight(), int(current['heightProportion'] * uicore.desktop.height))
        if setPosition:
            left = int(uicore.desktop.width * current['positionX']) - self.width / 2
            self.left = clamp(left, 0, uicore.desktop.width - self.WINDOW_NEVER_OFFSCREEN_BUFFER)
            top = int(uicore.desktop.height * current['positionY']) - self.height / 2
            self.top = clamp(top, 0, uicore.desktop.height - self.WINDOW_NEVER_OFFSCREEN_BUFFER)
        self.FinalizeModeChange(registerSettings)
        if self.GetFullscreenViewStateName():
            self.CloseViewStateView()

    def ActivateViewStateView(self):
        self.infoPanelContainer.Hide()
        uthread.new(sm.GetService('viewState').ActivateView, self.GetFullscreenViewStateName())

    def CloseViewStateView(self):
        self.infoPanelContainer.Show()
        sm.GetService('viewState').CloseSecondaryView(self.GetFullscreenViewStateName())

    def FinalizeModeChange(self, registerSettings = True):
        if registerSettings:
            self.RegisterPanelSettings()
        uthread.new(uicore.dockablePanelManager.CheckViewState)
        if self._immersiveAudioOverlay:
            if self.IsFullscreen():
                self._immersiveAudioOverlay.set_full_screen()
            elif self.IsMinimized():
                self._immersiveAudioOverlay.set_windowed()
            else:
                self._immersiveAudioOverlay.set_windowed()
        self.Prepare_ScaleAreas_()
        self.OnDockModeChanged(self)

    def OnDockModeChanged(self, *args, **kwds):
        pass

    def DeactivateUnderlay(self):
        if self.IsFullscreen():
            return
        super(DockablePanel, self).DeactivateUnderlay()

    def OnDragTick(self, *args, **kwds):

        def FindSnapPosition(mousePosition, snapPositions):
            for snapPosition, index in snapPositions:
                if snapPosition - 2 < mousePosition < snapPosition + 2:
                    return (snapPosition, index)

        snapToDockMode = self.snapToDockMode
        xLeftPositions, xRightPositions = self.snapPositions
        snapLeft = FindSnapPosition(uicore.uilib.x, xLeftPositions)
        snapRight = FindSnapPosition(uicore.uilib.x, xRightPositions)
        if snapLeft and BUTTON_DOCKLEFT in self.dock_options:
            self.snapToDockMode = (BUTTON_DOCKLEFT, snapLeft)
        elif snapRight and BUTTON_DOCKRIGHT in self.dock_options:
            self.snapToDockMode = (BUTTON_DOCKRIGHT, snapRight)
        elif uicore.uilib.y == 0:
            self.snapToDockMode = (BUTTON_FULLSCREEN, (0, -1))
        elif self.snapToDockMode:
            dockMode, (snapPosition, index) = self.snapToDockMode
            if dockMode == BUTTON_FULLSCREEN and uicore.uilib.y > SNAP_RELEASE_THRESHOLD:
                self.snapToDockMode = None
            elif dockMode in (BUTTON_DOCKLEFT, BUTTON_DOCKRIGHT):
                if not snapPosition - SNAP_RELEASE_THRESHOLD < uicore.uilib.x < snapPosition + SNAP_RELEASE_THRESHOLD:
                    self.snapToDockMode = None
        if snapToDockMode != self.snapToDockMode:
            self.UpdateSnapIndicator(xLeftPositions, xRightPositions)

    def UpdateSnapIndicator(self, xLeftPositions, xRightPositions):
        if self.snapToDockMode:
            dockMode, (position, index) = self.snapToDockMode
            if not self.snapIndicator:
                self.snapIndicator = DockPanelSnapIndicator(parent=uicore.desktop, idx=0)
            if dockMode == BUTTON_FULLSCREEN:
                self.snapIndicator.align = uiconst.TOPLEFT
                self.snapIndicator.left = max([ snapPosition for snapPosition, index in xLeftPositions ])
                self.snapIndicator.top = 0
                self.snapIndicator.width = min([ snapPosition for snapPosition, index in xRightPositions ]) - self.snapIndicator.left
                self.snapIndicator.height = SNAP_INDICATOR_SIZE
                self.snapIndicator.Pulse()
                return
            if dockMode == BUTTON_DOCKLEFT:
                onBoundary = xLeftPositions.index((position, index)) == 0
                self.snapIndicator.align = uiconst.TOLEFT_NOPUSH
                if onBoundary:
                    self.snapIndicator.left = position
                else:
                    self.snapIndicator.left = position - SNAP_INDICATOR_SIZE
                self.snapIndicator.top = 0
                self.snapIndicator.width = SNAP_INDICATOR_SIZE
                self.snapIndicator.height = 0
                self.snapIndicator.Pulse()
                return
            if dockMode == BUTTON_DOCKRIGHT:
                onBoundary = xRightPositions.index((position, index)) == 0
                self.snapIndicator.align = uiconst.TOLEFT_NOPUSH
                if onBoundary:
                    self.snapIndicator.left = position - SNAP_INDICATOR_SIZE
                else:
                    self.snapIndicator.left = position - SNAP_INDICATOR_SIZE
                self.snapIndicator.top = 0
                self.snapIndicator.width = SNAP_INDICATOR_SIZE
                self.snapIndicator.height = 0
                self.snapIndicator.Pulse()
                return
        if self.snapIndicator:
            self.snapIndicator.Rest(close=True)
            self.snapIndicator = None

    def _BeginDrag(self, *args, **kwds):
        if not self.IsFloating():
            initMouseX, initMouseY = self.dragMousePosition
            left, top, width, height = self.toolbarContainer.GetAbsolute()
            if self.align == uiconst.TOALL:
                propLeft = initMouseX / float(uicore.desktop.width)
            else:
                propLeft = (initMouseX - left) / float(width)
            self.UnDock(setPosition=False, registerSettings=False)
            self.left = uicore.uilib.x - int(self.width * propLeft)
            self.top = 0
        self.snapPositions = self.GetSnapPositions()
        Window._BeginDrag(self)
        self.state = uiconst.UI_NORMAL

    def AdjustWindowPositionToFitScreen(self):
        if not self.IsFloating():
            return
        super(DockablePanel, self).AdjustWindowPositionToFitScreen()

    def OnMouseUp(self, *args):
        Window.OnMouseUp(self, *args)
        if self.snapToDockMode:
            dockMode, (position, index) = self.snapToDockMode
            if dockMode == BUTTON_FULLSCREEN:
                self.DockFullscreen()
            elif dockMode == BUTTON_DOCKLEFT:
                self.DockOnLeft(index=index)
            elif dockMode == BUTTON_DOCKRIGHT:
                self.DockOnRight(index=index)
        self.snapToDockMode = None
        if self.snapIndicator:
            self.snapIndicator.Close()
            self.snapIndicator = None
        self.RegisterPanelSettings()

    def GetSnapPositions(self):
        xPositionLeft = []
        xPositionRight = []
        l, t, w, h = uicore.layer.sidePanels.GetAbsolute()
        xPositionLeft.append((l, 0))
        xPositionRight.append((l + w - 1, 0))
        for index, each in enumerate(uicore.layer.sidePanels.children):
            if each.align == uiconst.TOLEFT:
                l, t, w, h = each.GetAbsolute()
                xPositionLeft.append((l, index))
                xPositionLeft.append((l + w, index + 1))
            elif each.align == uiconst.TORIGHT:
                l, t, w, h = each.GetAbsolute()
                xPositionRight.append((l, index + 1))
                xPositionRight.append((l + w, index))

        return (xPositionLeft, xPositionRight)

    def IsClosable(self):
        return True

    def _CreateImmersiveAudioOverlay(self):
        if not self.hasImmersiveAudioOverlay:
            return
        self._immersiveAudioOverlay = sm.GetService('audio').CreateImmersiveOverlay(self.windowID)

    @EatsExceptions('protoClientLogs')
    def _LogWindowEventOpened(self):
        if self.analyticID:
            message_bus = WindowMessenger(sm.GetService('publicGatewaySvc'))
            currentSettings = self.GetPanelSettings()
            message_bus.window_opened(self.analyticID, DOCKING_MODES_CONVERSION[currentSettings.get('align', uiconst.TOPLEFT)])

    def UpdateUIScaling(self, *args):
        super(DockablePanel, self).UpdateUIScaling(*args)
        if not self.minimized and not self.IsFullscreen():
            self.InitDockPanelPosition()


class DockPanelSnapIndicator(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fill = FillThemeColored(parent=self, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)

    def Pulse(self):
        uicore.animations.MorphScalar(self.fill, 'opacity', startVal=0.0, endVal=1.0, curveType=uiconst.ANIM_OVERSHOT, duration=0.1, callback=self.Rest)

    def Rest(self, close = False):
        if close:
            uicore.animations.MorphScalar(self.fill, 'opacity', startVal=self.fill.opacity, endVal=0.0, duration=0.3, callback=self.Close)
        else:
            uicore.animations.MorphScalar(self.fill, 'opacity', startVal=self.fill.opacity, endVal=0.3, duration=0.5)
