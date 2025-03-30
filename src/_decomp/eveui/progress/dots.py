#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\progress\dots.py
from __future__ import division
from eveui import Fill, FlowContainer
from eveui.constants import Align
from eveui.animation.curve import CurveType
from eveui.animation.fade import fade

class DottedProgress(FlowContainer):

    def __init__(self, parent, align = Align.top_left, dot_size = 8, dot_count = 5, **kwargs):
        super(DottedProgress, self).__init__(parent=parent, align=align, contentSpacing=(dot_size, 0), centerContent=True, width=(dot_size * (dot_count * 2 - 1)), height=dot_size, **kwargs)
        for i in range(dot_count):
            dot = Fill(parent=self, align=Align.no_align, height=dot_size, width=dot_size, opacity=0.0)
            duration = 1.0
            time_offset = i / dot_count
            fade(dot, start_value=0.0, end_value=1.0, duration=duration, time_offset=time_offset * duration, curve_type=CurveType.bounce, loops=-1)
