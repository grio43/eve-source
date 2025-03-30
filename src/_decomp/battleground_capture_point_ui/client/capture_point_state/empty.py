#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\capture_point_state\empty.py
from battleground_capture_point_ui.client.const import emptyBadge
from battleground_capture_point_ui.client.state import TimerGaugeState
from carbonui import uiconst
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.vectorline import VectorLine
from eve.client.script.ui import eveColor

class Empty(TimerGaugeState):

    def __init__(self, panel, distance_thresholded_camera_facing_panel, camera_facing_ui):
        super(Empty, self).__init__()
        self.camera_facing_ui = camera_facing_ui
        self.distance_thresholded_camera_facing_panel = distance_thresholded_camera_facing_panel
        self.panel = panel
        self.color = eveColor.WHITE

    def enter(self):
        self._construct_camera_facing_components()

    def SetTimerValue(self, value, animate = True):
        pass

    def _construct_camera_facing_components(self):
        self.camera_facing_ui.opacity = 1.0
        Sprite(texturePath=emptyBadge, parent=self.camera_facing_ui, width=32, height=32, top=-50, align=uiconst.CENTER)
        VectorLine(parent=self.camera_facing_ui, translationFrom=(0, 0), translationTo=(0, -34), align=uiconst.CENTER, colorFrom=eveColor.WHITE, colorTo=eveColor.WHITE, widthFrom=1, widthTo=1)

    def exit(self):
        self.distance_thresholded_camera_facing_panel.Flush()
        self.camera_facing_ui.Flush()
        self.panel.mainCont.Flush()
