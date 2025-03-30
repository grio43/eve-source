#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\sweep_effect.py
import math
import threadutils
import uthread2
from carbonui.uicore import uicore
import eveui
from raffles.client import texture

class SweepEffect(eveui.Sprite):
    default_name = 'SweepEffect'
    default_texturePath = texture.sweep_effect
    default_opacity = 0
    default_idx = 0

    def __init__(self, opacity = 0.2, duration = 1.5, rotation = math.pi * 0.95, on_start = None, on_end = None, **kwargs):
        super(SweepEffect, self).__init__(**kwargs)
        self._opacity = opacity
        self._rotation = rotation
        self._duration = duration
        self.on_start = on_start
        self.on_end = on_end
        self._thread = None

    def stop(self):
        if self._thread:
            self._thread.kill()
            self._thread = None
        eveui.stop_all_animations(self)
        self.opacity = 0

    def sweep(self, loop = False):
        eveui.fade_in(self, end_value=self._opacity, duration=0.05)
        if loop:
            self._thread = uthread2.start_tasklet(self._loop)
        else:
            self._anim()

    def _loop(self):
        while not self.destroyed:
            self._anim()
            uthread2.sleep(3.5)

    def _anim(self):
        if self.on_start:
            self.on_start()
        uicore.animations.SpSwoopBlink(self, startVal=(-1.5, 0.0), endVal=(1.5, 0.0), rotation=self._rotation, duration=self._duration, callback=self.on_end)
