#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\scanButton.py
import localization
import signals
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.control import primaryButton
from eve.client.script.ui.inflight.scannerFiles.scannerUtil import IsDirectionalScanPanelEmbedded

class ScanButton(primaryButton.PrimaryButton):

    def ApplyAttributes(self, attributes):
        super(ScanButton, self).ApplyAttributes(attributes)
        self.cmd = attributes.cmd
        self.controller.on_scan_complete.connect(self.blink)

    def blink(self):
        if self.destroyed:
            return
        animations.FadeTo(self._arrows, startVal=self._arrows.opacity, endVal=0.0, loops=3, duration=0.3, curveType=uiconst.ANIM_BOUNCE)

    def LoadTooltipPanel(self, panel, *args):
        panel.LoadGeneric2ColumnTemplate()
        panel.AddCommandTooltip(self.cmd)
        panel.AddSpacer(height=2)
        shortcut_text = self.cmd.GetShortcutAsString()
        panel.AddLabelShortcut(localization.GetByLabel('UI/Inflight/Scanner/ScanTowards'), localization.GetByLabel('UI/Inflight/Scanner/AimTowardsShortcut', shortcut=shortcut_text))
        if IsDirectionalScanPanelEmbedded():
            panel.AddSpacer(height=2)
            panel.AddLabelShortcut(localization.GetByLabel('UI/Inflight/Scanner/RotateScanCone'), localization.GetByLabel('UI/Inflight/Scanner/RotateScanConeShortcut', shortcut=shortcut_text))


class ScanButtonController(primaryButton.PrimaryButtonController):

    def __init__(self, directional_scan_service, service_manager):
        self.directional_scan_service = directional_scan_service
        self.service_manager = service_manager
        super(ScanButtonController, self).__init__()
        self.on_scan_complete = signals.Signal(signalName='on_scan_complete')
        self.service_manager.RegisterForNotifyEvent(self, 'OnDirectionalScanCooldown')
        self.service_manager.RegisterForNotifyEvent(self, 'OnDirectionalScanStarted')

    @property
    def default_is_arrow_animated(self):
        return self.directional_scan_service.IsScanning()

    @property
    def default_is_enabled(self):
        return not self.directional_scan_service.IsScanning()

    @property
    def default_label(self):
        return localization.GetByLabel('UI/Inflight/Scanner/Scan')

    def on_clicked(self):
        self.directional_scan_service.DirectionalScan()

    def OnDirectionalScanCooldown(self):
        self.is_arrow_animated = False
        self.is_enabled = True
        self.on_scan_complete()

    def OnDirectionalScanStarted(self):
        self.is_arrow_animated = True
        self.is_enabled = False
