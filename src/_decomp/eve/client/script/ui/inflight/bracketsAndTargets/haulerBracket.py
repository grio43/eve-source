#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\bracketsAndTargets\haulerBracket.py
import carbonui.const as uiconst
from carbon.common.script.util.format import FmtAmt
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from eve.client.script.ui.inflight.bracketsAndTargets.inSpaceBracket import InSpaceBracket
import localization
from resourcewars.client.const import RW_PANEL_HAULER_PROGRESS_LABEL
from resourcewars.client.rwinfopanelhaulertaskentry import HAULER_PROGRESS_COLOR

class HaulerBracket(InSpaceBracket):
    BACKGROUND_GAUGE_COLOR = (0.3, 0.3, 0.3, 0.6)
    GAUGE_WIDTH = 2.5
    RADIUS = 16

    def ApplyAttributes(self, attributes):
        InSpaceBracket.ApplyAttributes(self, attributes)
        self.rwService = sm.GetService('rwService')
        self.shouldShowHint = False
        self.initialized = False
        container = Container(parent=self, align=uiconst.CENTER, height=32, width=32)
        self.gauge = GaugeCircular(parent=container, name='haulerBracketGauge', radius=self.RADIUS, align=uiconst.CENTER, colorStart=HAULER_PROGRESS_COLOR, colorEnd=HAULER_PROGRESS_COLOR, colorBg=self.BACKGROUND_GAUGE_COLOR, lineWidth=self.GAUGE_WIDTH, clockwise=False, showMarker=False, state=uiconst.UI_DISABLED)
        self.percentage = 0.0

    def Startup(self, slimItem, ball = None, transform = None):
        InSpaceBracket.Startup(self, slimItem, ball=ball, transform=transform)
        haulerProgress = self.GetProgress()
        self.SetCapacityBarPercentage(haulerProgress)
        self.gauge.SetValue(self.percentage)

    def SetHint(self, hint):
        if self.label:
            self.label.Close()
        if getattr(self, 'hintLabel', False):
            self.hintLabel.Close()
        self.hintLabel = Label(parent=self, align=uiconst.TOLEFT_NOPUSH, text=hint, padLeft=self.RADIUS * 2)

    def UpdateHint(self):
        if self.shouldShowHint:
            hint = localization.GetByLabel(RW_PANEL_HAULER_PROGRESS_LABEL, current=FmtAmt(self.contents), total=FmtAmt(self.capacity))
        else:
            hint = ''
        self.SetHint(hint)

    def SetCapacityBarPercentage(self, haulerData):
        if haulerData is None:
            return
        self.contents = haulerData.contents
        self.capacity = haulerData.capacity
        self.initialized = True
        try:
            self.percentage = float(self.contents) / self.capacity
        except ZeroDivisionError:
            self.percentage = 0.0

        self.UpdateHint()

    def GetProgress(self):
        return self.rwService.get_progress_for_hauler(self.itemID)

    def Select(self, status):
        InSpaceBracket.Select(self, status)
        if status:
            self.SetCapacityBarPercentage(self.GetProgress())
        else:
            self.SetHint('')

    def UpdateQuantity(self, newQuantity):
        ratio = float(newQuantity) / self.capacity
        self.contents = newQuantity
        self.gauge.SetValueTimed(ratio, 1.0)

    def OnMouseEnter(self, *args):
        if self.initialized:
            self.shouldShowHint = True
        self.UpdateHint()

    def OnMouseExit(self, *args):
        self.shouldShowHint = False
        self.UpdateHint()
