#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\directionalScannerWindow.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.window.widget import WidgetWindow
from carbonui.window.control.action import WindowActionImportance, WindowToggleAction
from carbonui.window.header.small import SmallWindowHeader
from eve.client.script.ui.inflight.scannerFiles.directionalScannerPalette import DirectionalScannerPalette
from carbonui.control.window import Window
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsDirectionalScanPanelEmbedded
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import SetDirectionalScanPanelEmbedded
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import SetDirectionalScanPanelWindowed
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsShortuctExecutionAllowed
from eveuniverse.solar_systems import is_directional_scanner_suppressed
from localization import GetByLabel
from carbonui.uicore import uicore
import carbonui.const as uiconst
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
MIN_WINDOW_WIDTH = 300
MIN_WINDOW_HEIGHT = 124

class DirectionalScannerCompactHeader(SmallWindowHeader):
    default_height = 32


class DirectionalScanner(WidgetWindow):
    __notifyevents__ = ['OnOverviewPresetSaved', 'OnBallparkSetState', 'OnSessionChanged']
    default_windowID = 'directionalScannerWindow'
    default_width = 400
    default_height = 350
    default_minSize = (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    default_captionLabelPath = 'UI/Inflight/Scanner/DirectionalScanner'
    default_scope = uiconst.SCOPE_INFLIGHT

    def ApplyAttributes(self, attributes):
        super(DirectionalScanner, self).ApplyAttributes(attributes)
        self.scannerPalette = DirectionalScannerPalette(parent=self.GetMainArea(), uniqueUiName=pConst.UNIQUE_NAME_DIRECTIONAL_SCANNER, window=self)
        sm.ScatterEvent('OnDirectionalScannerOpened')
        self.on_compact_mode_changed.connect(self.OnWindowStateChanged)
        self.on_stacked_changed.connect(self.OnWindowStateChanged)
        self.on_collapsed_changed.connect(self.OnWindowStateChanged)

    def OnWindowStateChanged(self, *args):
        self.Prepare_Header_()
        self.scannerPalette.Reconstruct()

    def Confirm(self, *args):
        self.scannerPalette.Confirm()

    @classmethod
    def ToggleOpenCloseDirectionalScanner(cls):
        if IsDirectionalScanPanelEmbedded():
            uicore.cmd.GetCommandAndExecute('CmdToggleSolarSystemMap', openDirectionalScanPanel=True)
        else:
            cls.ToggleOpenClose()

    @classmethod
    def OpenDirectionalScanner(cls):
        if IsDirectionalScanPanelEmbedded():
            from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
            solarSystem = SolarSystemViewPanel.GetIfOpen()
            if solarSystem:
                solarSystem.mapView.OpenDirectionalScanPanelEmbedded()
        else:
            DirectionalScanner.Open()

    def CloseByUser(self, *args):
        Window.CloseByUser(self, *args)
        sm.ScatterEvent('OnDirectionalScannerClosed')

    def GetCustomHeaderButtons(self):
        return [DockWindowAction(self)]

    def DockInMap(self, *args):
        SetDirectionalScanPanelEmbedded()
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        SolarSystemViewPanel.Open()
        self.Close(setClosed=True)
        sm.ScatterEvent('OnDirectionalScannerDocked')

    def UndockFromMap(self, *args):
        SetDirectionalScanPanelWindowed()
        sm.ScatterEvent('OnDirectionalScannerUndocked')

    def OnSetActive_(self, *args):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if SolarSystemViewPanel.IsOpen():
            PlaySound('scanner_atmo_window_loop_play')

    def OnSetInactive(self, *args):
        Window.OnSetInactive(self, *args)
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if SolarSystemViewPanel.IsOpen():
            PlaySound('scanner_atmo_loop_play')

    def OnShortcutKeyDown(self, modkey, vkey, flag):
        if IsShortuctExecutionAllowed(self):
            return self.scannerPalette.ToggleFitlerShortcut(vkey)
        return False

    def Prepare_Header_(self):
        if self.compact:
            self._SetHeader(DirectionalScannerCompactHeader(show_caption=False))
        else:
            super(DirectionalScanner, self).Prepare_Header_()

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            if is_directional_scanner_suppressed(session.solarsystemid2):
                self.Close()


class DockWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(DockWindowAction, self).__init__(window=window, callback=self._toggle_docked, toggled_on_icon='res:/UI/Texture/classes/DockPanel/floatButton.png', toggled_off_icon='res:/UI/Texture/classes/DockPanel/fullscreenButton.png', toggled_on_label=GetByLabel('UI/Inflight/Scanner/OpenInWindow'), toggled_off_label=GetByLabel('UI/Inflight/Scanner/DockInSolarSystemMap'), toggled_check=lambda _window: IsDirectionalScanPanelEmbedded(), importance_check=self._get_importance)

    @staticmethod
    def _toggle_docked(window):
        if IsDirectionalScanPanelEmbedded():
            window.UndockFromMap()
        else:
            window.DockInMap()

    @staticmethod
    def _get_importance(window):
        if window.compact:
            return WindowActionImportance.extra
        else:
            return WindowActionImportance.core
