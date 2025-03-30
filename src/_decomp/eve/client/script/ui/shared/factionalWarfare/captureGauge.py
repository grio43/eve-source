#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\captureGauge.py
from carbonui import uiconst
from carbonui.uianimations import animations
from eve.client.script.ui.control.gauge import Gauge
from eve.common.lib import appConst
from eve.common.script.util import facwarCommon
import localization
from factionwarfare.client.text import GetSystemCaptureStatusText, GetSystemCaptureStatusHint
COLOR_RED = (0.5, 0.0, 0.0, 1.0)
COLOR_WHITE = (0.5, 0.5, 0.5, 1.0)

class CaptureGauge(Gauge):
    __notifyevents__ = ['OnSystemStatusChanged']

    def ApplyAttributes(self, attributes):
        super(CaptureGauge, self).ApplyAttributes(attributes)
        self.isGaugeInitialized = False
        self.solarSystemID = attributes.get('solarSystemID', session.solarsystemid2)
        self.fwVictoryPointSvc = sm.GetService('fwVictoryPointSvc')
        sm.RegisterNotify(self)

    def UpdateGauge(self, animate = True):
        animate = animate and self.isGaugeInitialized
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        if victoryPointState:
            value = victoryPointState.contestedFraction
        else:
            value = 0.0
        animations.StopAnimation(self, 'opacity')
        self.opacity = 1.0
        self.SetValue(value, animate=animate)
        if value >= 1.0:
            self.SetColor(COLOR_RED)
        else:
            self.SetColor(COLOR_WHITE)
        self.isGaugeInitialized = True

    def OnSystemStatusChanged(self):
        self.UpdateGauge()

    def GetHint(self):
        victoryPointState = self.fwVictoryPointSvc.GetVictoryPointState(self.solarSystemID)
        hint = GetSystemCaptureStatusText(victoryPointState)
        captureStatusHint = GetSystemCaptureStatusHint(victoryPointState)
        if captureStatusHint:
            hint += '<br><color=gray>' + captureStatusHint
        return hint
