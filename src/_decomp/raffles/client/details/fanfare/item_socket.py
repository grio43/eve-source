#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\details\fanfare\item_socket.py
import math
import trinity
import threadutils
import uthread2
import eveui
from raffles.client import texture
from raffles.client.widget.item_icon import ItemIcon

class ItemSocket(eveui.Container):
    default_width = 110
    default_height = 110
    default_opacity = 0

    def __init__(self, type_id, item_id, is_copy, **kwargs):
        super(ItemSocket, self).__init__(**kwargs)
        self._type_id = type_id
        self._item_id = item_id
        self._is_blueprint_copy = is_copy
        self._layout()

    def reveal(self):
        eveui.fade_in(self, duration=1, time_offset=1)
        eveui.fade_in(self.item_icon, duration=0.75, time_offset=1.5)

    @threadutils.threaded
    def highlight(self):
        uthread2.sleep(0.4)
        self.lines.highlight()

    def decrypt(self):
        self.lines.decrypt()

    def close(self):
        eveui.fade_out(self, duration=0.3)

    def _layout(self):
        eveui.Sprite(parent=self, align=eveui.Align.center, width=89, height=32, texturePath=texture.hex_icon_highlight_bot, blendMode=trinity.TR2_SBM_ADD, top=30)
        eveui.Sprite(parent=self, align=eveui.Align.center, width=89, height=32, texturePath=texture.hex_icon_highlight_top, blendMode=trinity.TR2_SBM_ADD, top=-30)
        eveui.Sprite(parent=self, align=eveui.Align.center, width=75, height=86, texturePath=texture.hex_icon_frame)
        self.lines = Lines(parent=self, align=eveui.Align.to_all)
        eveui.Sprite(parent=self, align=eveui.Align.center, width=142, height=167, texturePath=texture.hex_base)
        self.item_icon = ItemIcon(parent=self, align=eveui.Align.center, type_id=self._type_id, item_id=self._item_id, is_copy=self._is_blueprint_copy, width=90, height=90, opacity=0)
        eveui.Sprite(parent=self, align=eveui.Align.center, width=75, height=86, texturePath=texture.hex_icon_base)


class Lines(eveui.Container):

    def __init__(self, **kwargs):
        super(Lines, self).__init__(**kwargs)
        self.lines = []
        self._layout()

    def highlight(self):
        for line in self.lines:
            eveui.fade(line, start_value=1, end_value=0, duration=1)
            uthread2.sleep(0.1)

    def decrypt(self):
        for line in self.lines:
            eveui.fade(line, start_value=1, end_value=0, duration=1)

    def _layout(self):
        le = LineEffect(parent=self, top=33, left=-53, rotation=math.pi * -0.33)
        self.lines.append(le)
        le = LineEffect(parent=self, top=-34, left=-55, rotation=math.pi * 0.33)
        self.lines.append(le)
        le = LineEffect(parent=self, top=-63)
        self.lines.append(le)
        le = LineEffect(parent=self, top=-34, left=55, rotation=math.pi * -0.33)
        self.lines.append(le)
        le = LineEffect(parent=self, top=34, left=55, rotation=math.pi * 0.33)
        self.lines.append(le)
        le = LineEffect(parent=self, top=63)
        self.lines.append(le)


class LineEffect(eveui.Transform):
    default_align = eveui.Align.center
    default_width = 11
    default_height = 46
    default_opacity = 0

    def __init__(self, **kwargs):
        super(LineEffect, self).__init__(**kwargs)
        eveui.Sprite(parent=self, align=eveui.Align.to_all, texturePath=texture.hex_effect_2, blendMode=trinity.TR2_SBM_ADD)
