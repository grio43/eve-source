#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\mapViewPanel.py
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.shared.mapView.dockPanelConst import DOCKPANELID_MAP
from eve.client.script.ui.shared.mapView.mapViewConst import MAPVIEW_PRIMARY_ID
from eve.client.script.ui.shared.mapView.mapViewSearch import MapViewSearchControl
from eve.client.script.ui.shared.mapView.controls.mapViewSettingButtons import MapViewSettingButtons
from eve.client.script.ui.shared.mapView.dockPanel import DockablePanel
import carbonui.const as uiconst
import logging
from eve.client.script.ui.shared.mapView.mapViewWorld import MapViewWorld
from eve.client.script.ui.view.viewStateConst import ViewState
log = logging.getLogger(__name__)
OVERLAY_LEFT_PADDING_FULLSCREEN = 360
OVERLAY_RIGHT_PADDING_FULLSCREEN = 280
OVERLAY_SIDE_PADDING_NONFULLSCREEN = 6

class MapViewPanel(DockablePanel):
    __notifyevents__ = DockablePanel.__notifyevents__ + ['OnSetCameraOffset', 'OnHideUI', 'OnShowUI']
    default_captionLabelPath = 'UI/Neocom/MapBtn'
    default_windowID = DOCKPANELID_MAP
    default_iconNum = 'res:/UI/Texture/windowIcons/map.png'
    default_analyticID = 'Map'
    panelID = default_windowID
    mapViewID = MAPVIEW_PRIMARY_ID
    mapView = None
    overlayTools = None
    viewState = ViewState.StarMapNew
    hasImmersiveAudioOverlay = True

    def OnSetCameraOffset(self, cameraOffset):
        if self.mapView and not self.mapView.destroyed:
            if self.IsFullscreen():
                x = -(cameraOffset * 0.5 - 0.5)
                self.mapView.camera.cameraCenter = (x, 0.5)
            else:
                self.mapView.camera.cameraCenter = (0.5, 0.5)

    def ApplyAttributes(self, attributes):
        DockablePanel.ApplyAttributes(self, attributes)
        if not sm.GetService('ui').IsUiVisible():
            self.toolbarContainer.display = False
        zoomToItem = attributes.get('zoomToItem', True)
        self.mapView = MapViewWorld(parent=self.content, isFullScreen=self.IsFullscreen(), mapViewID=self.mapViewID, interestID=attributes.interestID, starColorMode=attributes.starColorMode, zoomToItem=zoomToItem)
        if self.IsFullscreen():
            self.mapView.overlayTools.padding = (OVERLAY_LEFT_PADDING_FULLSCREEN,
             self.toolbarContainer.height + 6,
             OVERLAY_RIGHT_PADDING_FULLSCREEN,
             6)
        else:
            self.mapView.overlayTools.padding = (OVERLAY_SIDE_PADDING_NONFULLSCREEN,
             self.toolbarContainer.height + 6,
             OVERLAY_SIDE_PADDING_NONFULLSCREEN,
             6)
        MapViewSettingButtons(parent=self.toolbarContainer, align=uiconst.CENTERLEFT, onSettingsChangedCallback=self.mapView.OnMapViewSettingChanged, mapViewID=self.mapViewID, left=4, idx=0)
        MapViewSearchControl(parent=self.mapView.overlayTools, mapView=self.mapView, align=uiconst.TOPRIGHT, idx=0)
        Fill(bgParent=self.content, color=eveThemeColor.THEME_TINT, opacity=0.8)

    def Close(self, *args, **kwds):
        DockablePanel.Close(self, *args, **kwds)
        self.mapView = None

    def OnShowUI(self):
        self.mapView.overlayTools.display = True
        self.toolbarContainer.display = True

    def OnHideUI(self):
        if self.IsFullscreen():
            self.mapView.overlayTools.display = False
            self.toolbarContainer.display = False

    def SetActiveItemID(self, *args, **kwds):
        if self.mapView:
            return self.mapView.SetActiveItemID(*args, **kwds)

    def SetMapFilter(self, *args, **kwds):
        if self.mapView:
            return self.mapView.SetMapFilter(*args, **kwds)

    def OnDockModeChanged(self, *args, **kwds):
        if self.mapView:
            if self.mapView.overlayTools and not self.mapView.overlayTools.destroyed:
                if self.IsFullscreen():
                    self.mapView.overlayTools.padLeft = OVERLAY_LEFT_PADDING_FULLSCREEN
                    self.mapView.overlayTools.padRight = OVERLAY_RIGHT_PADDING_FULLSCREEN
                else:
                    self.mapView.overlayTools.padLeft = OVERLAY_SIDE_PADDING_NONFULLSCREEN
                    self.mapView.overlayTools.padRight = OVERLAY_SIDE_PADDING_NONFULLSCREEN
            self.mapView.OnDockModeChanged(self.IsFullscreen())

    def _OnResize(self, *args):
        DockablePanel._OnResize(self, *args)
        if self.mapView:
            self.mapView.OnWindowResize(self.width, self.height)

    def SetActive(self, *args, **kwds):
        DockablePanel.SetActive(self, *args, **kwds)
        if self.mapView:
            self.mapView.SetFocusState(True)

    def OnSetInactive(self, *args, **kwds):
        DockablePanel.OnSetInactive(self, *args, **kwds)
        if self.mapView:
            self.mapView.SetFocusState(False)

    def CmdZoomInOut(self, zoomDelta):
        if self.mapView:
            self.mapView.camera.Zoom(0.0005 * zoomDelta)

    def OnStartMinimize_(self, *args):
        try:
            self.mapView.Hide()
        except AttributeError:
            pass

    def OnStartMaximize_(self, *args):
        try:
            self.mapView.Show()
        except AttributeError:
            pass
