#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\banner_background.py
import math
import random
from carbonui.uianimations import animations
import eveui
import threadutils
import trinity
import uthread2
from raffles.client import texture

class BannerBackground(eveui.ContainerAutoSize):

    def __init__(self, parent):
        super(BannerBackground, self).__init__(parent=parent, align=eveui.Align.to_top)
        self._layout()
        self._animate_lines()

    def _layout(self):
        self._lines_1 = eveui.Sprite(parent=self, align=eveui.Align.center_top, texturePath=texture.background_triangles_banner_lines, blendMode=trinity.TR2_SBM_ADDX2, width=1024, height=418, color=(0.2, 0.6, 1.0), opacity=0.1)
        self._lines_2 = eveui.Sprite(parent=self, align=eveui.Align.center_top, texturePath=texture.background_triangles_banner_lines, blendMode=trinity.TR2_SBM_ADDX2, width=1024, height=418, color=(0.2, 0.6, 1.0), opacity=0.3)
        eveui.Sprite(parent=self, align=eveui.Align.center_top, texturePath=texture.background_triangles_banner, width=1024, height=418, opacity=0.4)

    @threadutils.threaded
    def _animate_lines(self):
        while not self.destroyed:
            rotation = math.pi * random.random()
            animations.SpSwoopBlink(self._lines_1, rotation=rotation, duration=8.0)
            animations.SpSwoopBlink(self._lines_2, rotation=rotation, duration=5.0, timeOffset=2.0)
            uthread2.sleep(6.0)
