#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeDockablePanel.py
import uthread2
from carbonui import const as uiconst, Align
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.services.setting import CharSettingBool
from carbonui.uicore import uicore
from eve.client.script.ui.control.panContainer import PanContainer
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
from eve.client.script.ui.shared.shipTree.shipTreeConst import ZOOMED_OUT, ZOOMED_IN, PAD_SIDE, PAD_TOP, MAIN_FACTIONS, COLOR_BG
from eve.client.script.ui.shared.shipTree.shipTreeContainer import ShipTreeContainer
from eve.client.script.ui.shared.shipTree.shipTreeUnlockContainer import ShipTreeUnlockContainer
from eve.client.script.ui.view.viewStateConst import ViewState
from localization import GetByLabel

class ShipTreeDockablePanel(DockablePanel):
    default_captionLabelPath = 'UI/ShipTree/ShipTree'
    default_windowID = 'ShipTree'
    default_iconNum = 'res:/ui/texture/windowIcons/isis.png'
    default_minSize = (1055, 720)
    panelID = default_windowID
    default_clipChildren = True
    default_performFitsCheck = False
    viewState = ViewState.ShipTree
    hasImmersiveAudioOverlay = True
    __notifyevents__ = DockablePanel.__notifyevents__ + ['OnEndChangeDevice', 'OnGraphicSettingsChanged']

    def ApplyAttributes(self, attributes):
        super(ShipTreeDockablePanel, self).ApplyAttributes(attributes)
        self.menuButton.display = True
        self.factionID = attributes.get('factionID', None)
        self.isZooming = False
        self.zoomLevel = ZOOMED_IN
        self.shipTreeCont = None
        self.isFadingFrame = False
        self.shipProgressionSetting = CharSettingBool('ShipProgression_Ignore', False)
        self.bg = Fill(name='bg', bgParent=self.GetMainArea(), color=COLOR_BG)
        self.unlockCont = ShipTreeUnlockContainer(parent=self.GetMainArea(), align=Align.BOTTOMLEFT, width=444, height=320, padding=(20, 0, 0, 20))
        self.panCont = PanContainer(parent=self.GetMainArea(), state=uiconst.UI_NORMAL, callback=self.OnPanContainer)
        self.UpdatePanContainerBorder()
        sm.GetService('shipTreeUI').OnShipTreeOpened()

    def GetMenuMoreOptions(self):
        menuData = super(ShipTreeDockablePanel, self).GetMenuMoreOptions()
        menuData.AddCheckbox('Suppress ship unlocks', setting=self.shipProgressionSetting)
        return menuData

    def ConstructSidePanel(self):
        super(ShipTreeDockablePanel, self).ConstructSidePanel()
        self.infoPanelContainer.topCont.display = False

    def DockFullscreen(self):
        super(ShipTreeDockablePanel, self).DockFullscreen()

    def UnDock(self, setPosition = True, registerSettings = True, *args):
        super(ShipTreeDockablePanel, self).UnDock(setPosition, registerSettings, *args)

    def Close(self, setClosed = False, *args, **kwds):
        super(ShipTreeDockablePanel, self).Close(setClosed, *args, **kwds)
        sm.GetService('shipTreeUI').OnShipTreeClosed()

    def Minimize(self, animate = True):
        sm.GetService('shipTreeUI').OnShipTreeMinimized()
        super(ShipTreeDockablePanel, self).Minimize(animate)

    def UpdatePanContainerBorder(self):
        camOffset = settings.user.ui.Get('cameraOffset', 0) / 100.0
        offset = uicore.desktop.width / 2 * camOffset
        padLeft = max(PAD_SIDE, PAD_SIDE - offset)
        padRight = max(PAD_SIDE, PAD_SIDE + offset)
        self.panCont.border = (padLeft,
         PAD_TOP,
         padRight,
         PAD_TOP)

    def OnEndChangeDevice(self, *args):
        self.UpdatePanContainerBorder()

    def OnGraphicSettingsChanged(self, *args):
        self.UpdatePanContainerBorder()

    def SelectFaction(self, factionID, oldFactionID = None):
        if self.shipTreeCont:
            uicore.animations.FadeOut(self.shipTreeCont, callback=self.shipTreeCont.Close, duration=0.15, sleep=True)
        self.shipTreeCont = ShipTreeContainer(parent=self.panCont.mainCont, align=uiconst.TOPLEFT, factionID=factionID, callback=self.OnMainContResize, alignMode=uiconst.TOPLEFT, opacity=0.0)
        self.shipTreeCont.SetSizeAutomatically()
        uicore.animations.FadeIn(self.shipTreeCont, duration=0.3)
        self.panCont.mainCont.SetSizeAutomatically()
        uicore.animations.FadeTo(self.bg, self.bg.opacity, 1.0, duration=1.0)
        self.panTarget = None
        if not oldFactionID:
            panTo = settings.user.ui.Get('ShipTreePanPosition', None)
            if panTo:
                self.panCont.PanTo(panTo[0], panTo[1], animate=False)
            else:
                self.PanToFirstNode()
        elif not (factionID in MAIN_FACTIONS and oldFactionID in MAIN_FACTIONS):
            self.PanToFirstNode()

    def OnMainContResize(self):
        width = self.panCont.mainCont.width
        if self.shipTreeCont:
            self.shipTreeCont.bgCont.width = width + 128
            self.shipTreeCont.bgCont.height = self.panCont.mainCont.height + 128

    def OnPanContainer(self):
        if not self.shipTreeCont:
            return
        if uicore.uilib.leftbtn:
            sm.GetService('shipTreeUI').OnDrag()
        k = 0.05
        left = self.panCont.panLeft
        moveAmount = k * (self.shipTreeCont.width - 2 * PAD_SIDE)
        self.shipTreeCont.bgCont.left = int(moveAmount * (0.5 - left))
        top = self.panCont.panTop
        moveAmount = k * (self.shipTreeCont.height - 2 * PAD_TOP)
        self.shipTreeCont.bgCont.top = int(moveAmount * (0.5 - top))
        if self.zoomLevel != ZOOMED_IN:
            self.shipTreeCont.bgCont.left -= self.shipTreeCont.bgCont.left % 2
            self.shipTreeCont.bgCont.top -= self.shipTreeCont.bgCont.top % 2
        self.shipTreeCont.factionBG.left = self.shipTreeCont.bgCont.left * 0.5
        self.shipTreeCont.factionBG.top = self.shipTreeCont.bgCont.top * 0.5
        if self.panCont.panTop in (0.0, 1.0):
            if self.isFadingFrame:
                return
            self.isFadingFrame = True
            if self.panCont.panTop == 0.0:
                uicore.animations.FadeTo(self.shipTreeCont.topFrame, 3.0, 1.0, duration=0.3, loops=1)
            else:
                uicore.animations.FadeTo(self.shipTreeCont.bottomFrame, 3.0, 1.0, duration=0.3, loops=1)
        else:
            self.isFadingFrame = False

    def OnCloseView(self):
        sm.UnregisterNotify(self)
        if self.bg:
            self.bg.Close()
        if self.shipTreeCont:
            self.shipTreeCont.Close()
        settings.user.ui.Set('ShipTreePanPosition', (self.panCont.panLeft, self.panCont.panTop))
        sm.GetService('shipTree').EmptyRecentlyChangedSkillsCache()

    def PanToNode(self, node, animate = True, duration = None):
        x, y = node.GetPositionProportional()
        s = 0.1
        x = (1.0 + 2 * s) * x - s
        x = max(0.0, min(x, 1.0))
        y = (1.0 + 2 * s) * y - s
        y = max(0.0, min(y, 1.0))
        self.panCont.PanTo(x, y, animate, duration=duration)

    def PanToFirstNode(self):
        node = self.shipTreeCont.rootNode.children[0]
        self.PanToNode(node, animate=False)

    def PanToShipGroup(self, shipGroupID, animate = True, duration = None):
        node = self.shipTreeCont.rootNode.GetChildByID(shipGroupID)
        self.PanToNode(node, animate, duration)

    def OnMouseWheel(self, *args):
        modifier = uicore.mouseInputHandler.GetCameraZoomModifier()
        self.OnZoom(modifier * uicore.uilib.dz)

    def OnZoom(self, dz):
        if self.isZooming:
            return
        if dz < 0:
            self.ZoomTo(ZOOMED_IN)
        else:
            self.ZoomTo(ZOOMED_OUT)

    def ZoomTo(self, zoomLevel):
        if self.isZooming or zoomLevel == self.zoomLevel:
            return
        try:
            duration = 0.6
            self.isZooming = True
            self.zoomLevel = zoomLevel
            uicore.animations.MorphScalar(self.panCont, 'scale', self.panCont.scale, self.zoomLevel, duration=duration, callback=self.OnZoomingDone)
            sm.ScatterEvent('OnShipTreeZoomChanged', self.zoomLevel)
            sm.GetService('shipTreeUI').CloseInfoBubble()
        except:
            self.isZooming = False
            raise

    def OnZoomingDone(self):
        self.isZooming = False
        uicore.CheckCursor()

    def OnBack(self):
        sm.GetService('shipTreeUI').GoBack()

    def OnForward(self):
        sm.GetService('shipTreeUI').GoForward()

    def GetShipGroup(self, shipGroupID):
        return self.shipTreeCont.GetGroupByID(shipGroupID)
