#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\effects.py
import eveui
import threadutils
from raffles.client import texture

class Ding(eveui.Sprite):
    default_texturePath = texture.effect_ding

    def __init__(self, scale_start = 20.0, scale_end = 1.0, **kwargs):
        self.scale_start = scale_start
        self.scale_end = scale_end
        super(Ding, self).__init__(**kwargs)

    @property
    def expand(self):
        return abs((self.scale[0] - self.scale_start) / (self.scale_start - self.scale_end))

    @expand.setter
    def expand(self, expand):
        s = (self.scale_end - self.scale_start) * ease_out_cubic(expand) + self.scale_start
        self.scale = (s, s)


@threadutils.threaded
def do_ding(parent, align, pos, offset = 0.0, index = 0, color = None):
    ding = Ding(parent=parent, align=align, pos=pos, opacity=0.0, idx=index, color=color)
    eveui.animate(ding, 'expand', start_value=0.0, end_value=1.0, duration=0.8, time_offset=offset, curve_type=eveui.CurveType.linear)
    eveui.fade_in(ding, end_value=0.2, duration=0.05, time_offset=offset, sleep=True)
    eveui.fade_out(ding, duration=0.4, time_offset=0.25, on_complete=ding.Close)


def ease_in_cubic(t):
    return t * t * t


def ease_out_cubic(t):
    t = t - 1.0
    return t * t * t + 1.0
