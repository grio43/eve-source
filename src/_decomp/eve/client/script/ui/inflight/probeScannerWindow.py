#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\probeScannerWindow.py
import carbonui.const as uiconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui.window.widget import WidgetWindow
from carbonui.uicore import uicore
from carbonui.window.control.action import WindowActionImportance, WindowToggleAction
from carbonui.window.header.small import SmallWindowHeader
from eve.client.script.ui.inflight.scannerFiles.probeScannerPalette import ProbeScannerPalette
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsProbeScanPanelEmbedded
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import SetProbeScanPanelEmbedded
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import SetProbeScanPanelWindowed
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsShortuctExecutionAllowed
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenSolarSystemMap
from eveuniverse.solar_systems import is_scanning_suppressed
from localization import GetByLabel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
MIN_WINDOW_WIDTH = 300
MIN_WINDOW_HEIGHT = 150

class ProbeScannerCompactHeader(SmallWindowHeader):
    default_height = 32


class ProbeScannerWindow(WidgetWindow):
    __notifyevents__ = ['OnCosmicAnomalyAdded', 'OnCosmicSignatureAdded', 'OnSessionChanged']
    default_windowID = 'probeScannerWindow'
    default_width = 400
    default_height = 400
    default_minSize = (MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
    default_captionLabelPath = 'UI/Inflight/Scanner/ProbeScanner'

    def ApplyAttributes(self, attributes):
        super(ProbeScannerWindow, self).ApplyAttributes(attributes)
        self.scope = uiconst.SCOPE_INFLIGHT
        self.probeScannerPalette = ProbeScannerPalette(parent=self.GetMainArea(), align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, idx=0, uniqueUiName=pConst.UNIQUE_NAME_PROBE_SCANNER, window=self)
        sm.ScatterEvent('OnProbeScannerOpened')
        sm.RegisterNotify(self)
        self.on_compact_mode_changed.connect(self.OnWindowStateChanged)
        self.on_stacked_changed.connect(self.OnWindowStateChanged)
        self.on_collapsed_changed.connect(self.OnWindowStateChanged)

    def OnWindowStateChanged(self, *args):
        self.Prepare_Header_()
        self.probeScannerPalette.Reconstruct()

    def Prepare_Header_(self):
        if self.compact:
            self._SetHeader(ProbeScannerCompactHeader(show_caption=False))
        else:
            super(ProbeScannerWindow, self).Prepare_Header_()

    def Confirm(self, *args):
        self.probeScannerPalette.Confirm()

    @classmethod
    def OpenProbeScanner(cls, *args, **kwargs):
        if IsProbeScanPanelEmbedded():
            OpenSolarSystemMap(openProbeScanPanel=True)
        else:
            super(ProbeScannerWindow, cls).Open(cls, *args, **kwargs)

    @classmethod
    def ToggleOpenCloseProbeScanner(cls):
        if IsProbeScanPanelEmbedded():
            uicore.cmd.GetCommandAndExecute('CmdToggleSolarSystemMap', openProbeScanPanel=True)
        else:
            cls.ToggleOpenClose()

    def CloseByUser(self, *args):
        super(ProbeScannerWindow, self).CloseByUser(*args)
        sm.ScatterEvent('OnProbeScannerClosed')

    def GetCustomHeaderButtons(self):
        return [DockWindowAction(self)]

    def DockInMap(self, *args):
        SetProbeScanPanelEmbedded()
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        SolarSystemViewPanel.Open()
        sm.ScatterEvent('OnProbeScannerDocked')
        self.Close(setClosed=True)

    def UndockFromMap(self, *args):
        SetProbeScanPanelWindowed()
        sm.ScatterEvent('OnProbeScannerUndocked')

    def OnSetActive_(self, *args):
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if SolarSystemViewPanel.IsOpen():
            PlaySound('scanner_atmo_window_loop_play')

    def OnSetInactive(self, *args):
        super(ProbeScannerWindow, self).OnSetInactive(*args)
        from eve.client.script.ui.shared.mapView.solarSystemViewPanel import SolarSystemViewPanel
        if SolarSystemViewPanel.IsOpen():
            PlaySound('scanner_atmo_loop_play')

    def OnShortcutKeyDown(self, modkey, vkey, flag):
        if IsShortuctExecutionAllowed(self):
            return self.probeScannerPalette.ToggleFilterShortcut(vkey)
        return False

    def OnCosmicAnomalyAdded(self, *args):
        self._HighlightResult()

    def OnCosmicSignatureAdded(self, *args):
        self._HighlightResult()

    def _HighlightResult(self):
        if self.InStack() and not self.IsVisible():
            self.Blink()

    def OnSessionChanged(self, isremote, session, change):
        if 'solarsystemid2' in change:
            if is_scanning_suppressed(session.solarsystemid2):
                self.Close()


class DockWindowAction(WindowToggleAction):

    def __init__(self, window):
        super(DockWindowAction, self).__init__(window=window, callback=self._toggle_docked, toggled_check=lambda _window: IsProbeScanPanelEmbedded(), toggled_on_icon='res:/UI/Texture/classes/DockPanel/floatButton.png', toggled_off_icon='res:/UI/Texture/classes/DockPanel/fullscreenButton.png', toggled_on_label=GetByLabel('UI/Inflight/Scanner/OpenInWindow'), toggled_off_label=GetByLabel('UI/Inflight/Scanner/DockInSolarSystemMap'), importance_check=self._get_importance)

    @staticmethod
    def _toggle_docked(window):
        if IsProbeScanPanelEmbedded():
            window.UndockFromMap()
        else:
            window.DockInMap()

    @staticmethod
    def _get_importance(window):
        if window.compact:
            return WindowActionImportance.extra
        else:
            return WindowActionImportance.core
