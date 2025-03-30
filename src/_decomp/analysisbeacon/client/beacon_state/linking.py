#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\analysisbeacon\client\beacon_state\linking.py
from analysisbeacon.client.state import State
from carbonui import uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.control.gaugeCircular import GaugeCircular

class Linking(State):

    def __init__(self, panel):
        self.panel = panel
        self.timer_gauge = None

    def enter(self):
        self.timer_gauge = GaugeCircular(parent=self.panel, radius=self.panel / 2, lineWidth=50.0, showMarker=False, value=0.5, align=uiconst.CENTER, opacity=0.0, colorStart=(1.0, 1.0, 1.0, 1.0), colorEnd=(0.8, 0.8, 0.8, 1.0))
        uicore.animations.BlinkIn(self.timer_gauge, duration=0.25)
        uicore.animations.MoveInFromBottom(self.timer_gauge, amount=500, duration=0.25)
