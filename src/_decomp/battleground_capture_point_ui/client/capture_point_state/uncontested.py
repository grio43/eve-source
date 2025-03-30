#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\capture_point_state\uncontested.py
from battleground_capture_point_ui.client.const import FACTION_ID_TO_CAPTURE_BADGE
from battleground_capture_point_ui.client.state import TimerGaugeState
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.gaugeCircular import GaugeCircular
from fwwarzone.client.dashboard.const import FACTION_ID_TO_COLOR

class UnContested(TimerGaugeState):

    def __init__(self, panel, distance_thresholded_camera_facing_panel, camera_facing_ui, remaining_duration, total_duration, currentKing):
        super(UnContested, self).__init__()
        self.camera_facing_ui = camera_facing_ui
        self.currentKing = currentKing
        self.distance_thresholded_camera_facing_panel = distance_thresholded_camera_facing_panel
        self.total_duration = float(total_duration)
        self.remaining_duration = float(remaining_duration)
        self.panel = panel
        self.color = eveColor.WHITE

    def enter(self):
        self._construct_camera_facing_components()

    def _construct_camera_facing_components(self):
        self.camera_facing_ui.opacity = 1.0
        bgColor = (self.color[0],
         self.color[1],
         self.color[2],
         0.5)
        value = self.remaining_duration / self.total_duration
        topOffset = -50
        internalGaugePadding = 5
        self.timer_gauge = GaugeCircular(parent=self.camera_facing_ui, radius=self.camera_facing_ui.width / 3 + internalGaugePadding, lineWidth=2.0, showMarker=False, value=value, align=uiconst.CENTER, colorStart=FACTION_ID_TO_COLOR[self.currentKing], colorEnd=FACTION_ID_TO_COLOR[self.currentKing], colorBg=bgColor, top=topOffset)
        Sprite(texturePath=FACTION_ID_TO_CAPTURE_BADGE[self.currentKing], parent=self.camera_facing_ui, width=32, height=32, top=-50, align=uiconst.CENTER)
        VectorLine(parent=self.camera_facing_ui, translationFrom=(0, 0), translationTo=(0, -40), align=uiconst.CENTER, colorFrom=eveColor.WHITE, colorTo=eveColor.WHITE, widthFrom=1, widthTo=1)

    def exit(self):
        self.distance_thresholded_camera_facing_panel.Flush()
        self.camera_facing_ui.Flush()
        self.panel.mainCont.Flush()
