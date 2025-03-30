#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\probescanning\analyzeButton.py
import localization
import probescanning.formations
import signals
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.control import primaryButton
from probescanning.tooltips.scanProbeTooltip import GetNoProbesTooltipText

class AnalyzeButton(primaryButton.PrimaryButton):
    default_soundClick = 'msg_newscan_probe_analyze_button_play'

    def ApplyAttributes(self, attributes):
        super(AnalyzeButton, self).ApplyAttributes(attributes)
        self.cmd = attributes.cmd
        self.controller.on_analyze_complete.connect(self.blink)

    def blink(self):
        animations.FadeTo(self._arrows, startVal=self._arrows.opacity, endVal=0.0, loops=3, duration=0.3, curveType=uiconst.ANIM_BOUNCE)

    def LoadTooltipPanel(self, panel, _):
        panel.LoadGeneric2ColumnTemplate()
        if self.controller.is_scanning:
            panel.AddLabelMedium(text=localization.GetByLabel('UI/Inflight/Scanner/Analyzing'), wrapWidth=200)
        elif not self.controller.is_enabled:
            panel.state = uiconst.UI_NORMAL
            panel.AddLabelMedium(text=GetNoProbesTooltipText(), state=uiconst.UI_NORMAL, wrapWidth=200)
        elif not self.controller.has_launched_probes:
            panel.AddLabelShortcut(localization.GetByLabel('UI/Commands/CmdLaunchProbes'), self.cmd.GetShortcutAsString())
        else:
            panel.AddCommandTooltip(self.cmd)


class AnalyzeButtonController(primaryButton.PrimaryButtonController):
    UPDATE_INTERVAL_MS = 500

    def __init__(self, scan_service):
        super(AnalyzeButtonController, self).__init__()
        self.scan_service = scan_service
        self.on_analyze_complete = signals.Signal(signalName='on_analyze_complete')
        self._update()
        self._refresh_timer = timerstuff.AutoTimer(interval=self.UPDATE_INTERVAL_MS, method=self._update)
        sm.RegisterForNotifyEvent(self, 'OnProbePositionsUpdated')
        sm.RegisterForNotifyEvent(self, 'OnReconnectToProbesAvailable')
        sm.RegisterForNotifyEvent(self, 'OnScannerDisconnected')
        sm.RegisterForNotifyEvent(self, 'OnSystemScanDone')

    @property
    def is_scanning(self):
        return self.scan_service.IsScanning()

    @property
    def has_available_probes(self):
        return self.scan_service.HasAvailableProbes()

    @property
    def has_launched_probes(self):
        return bool(self.scan_service.GetProbeData())

    @property
    def has_probe_charges_loaded(self):
        return bool(self.scan_service.GetChargesInProbeLauncher())

    def analyze(self):
        self.scan_service.RequestScans_Check()

    def close(self):
        super(AnalyzeButtonController, self).close()
        self._refresh_timer.KillTimer()
        self._refresh_timer = None
        sm.UnregisterForNotifyEvent(self, 'OnProbePositionsUpdated')
        sm.UnregisterForNotifyEvent(self, 'OnReconnectToProbesAvailable')
        sm.UnregisterForNotifyEvent(self, 'OnScannerDisconnected')
        sm.UnregisterForNotifyEvent(self, 'OnSystemScanDone')

    def launch(self):
        self.scan_service.MoveProbesToFormation(probescanning.formations.PINPOINT_FORMATION)

    def on_clicked(self):
        if self.has_launched_probes:
            self.analyze()
        else:
            self.launch()

    def _update(self):
        self._update_arrow_animated()
        self._update_enabled()
        self._update_label()

    def _update_arrow_animated(self):
        self.is_arrow_animated = self.is_scanning

    def _update_enabled(self):
        if self.is_scanning:
            is_enabled = False
        elif self.has_available_probes:
            is_enabled = True
        elif self.has_probe_charges_loaded:
            is_enabled = True
        else:
            is_enabled = False
        self.is_enabled = is_enabled

    def _update_label(self):
        if self.has_launched_probes:
            label = 'UI/Inflight/Scanner/Analyze'
        else:
            label = 'UI/Inflight/Scanner/Launch'
        self.label = localization.GetByLabel(label)

    def OnProbePositionsUpdated(self):
        self._update()

    def OnReconnectToProbesAvailable(self):
        self._update()

    def OnScannerDisconnected(self):
        self._update()

    def OnSystemScanDone(self):
        self.on_analyze_complete()
