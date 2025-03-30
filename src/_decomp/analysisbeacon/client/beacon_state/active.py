#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\analysisbeacon\client\beacon_state\active.py
import gametime
from analysisbeacon.client.const import IN_SPACE_GAUGE_THICKNESS
from analysisbeacon.client.state import State
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.gaugeCircular import GaugeCircular

class Active(State):

    def __init__(self, panel, camera_facing_panel, remaining_duration, total_duration):
        self.camera_facing_panel = camera_facing_panel
        self.total_duration = total_duration
        self.remaining_duration = remaining_duration
        gametime.GetSimTime()
        self.panel = panel
        self.timer_gauge = None

    def enter(self):
        value = self.remaining_duration / self.total_duration
        self.timer_gauge = GaugeCircular(parent=self.panel.mainCont, radius=self.panel.width / 2 - 2, lineWidth=IN_SPACE_GAUGE_THICKNESS, showMarker=False, value=value, align=uiconst.CENTER, opacity=0.0, colorStart=(1.0, 0.27, 0.29, 1.0), colorEnd=(1.0, 0.27, 0.29, 1.0), colorBG=Color().SetRGB(0.0, 0.0, 0.0, 0.0), useRealTime=False)
        self.timer_gauge.SetColorBg((0.0, 0.0, 0.0, 0.0))
        uicore.animations.BlinkIn(self.timer_gauge, duration=0.25)
        end_translation = self.panel.transform.translation[:]
        starting_translation = (self.panel.transform.translation[0], self.panel.transform.translation[1] - 1000, self.panel.transform.translation[2])
        uicore.animations.MorphVector3(self.panel.transform, 'translation', startVal=starting_translation, endVal=end_translation)
        self.timer_gauge.SetValueTimed(0.0, self.remaining_duration)
        self._construct_camera_facing_version()

    def _construct_camera_facing_version(self):
        value = self.remaining_duration / self.total_duration
        self._camera_facing_gauge = GaugeCircular(parent=self.camera_facing_panel, radius=self.camera_facing_panel.width / 3, lineWidth=4.0, showMarker=False, value=value, align=uiconst.CENTER, colorStart=(1.0, 0.27, 0.29, 1.0), colorEnd=(1.0, 0.27, 0.29, 1.0))
        self._camera_facing_gauge.SetValueTimed(0.0, self.remaining_duration)

    def exit(self):
        uicore.animations.BlinkOut(self.timer_gauge, duration=0.25, sleep=True)
        self.camera_facing_panel.Flush()
        self.panel.mainCont.Flush()
