#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\create\label_value.py
import eveui
from carbonui import TextColor

class LabelValue(eveui.ContainerAutoSize):
    default_minHeight = 16
    default_alignMode = eveui.Align.to_top
    default_padTop = 3

    def __init__(self, label = '', value = '', **kwargs):
        if kwargs.get('align') == eveui.Align.to_top:
            kwargs.setdefault('padTop', 0)
            kwargs.setdefault('padBottom', self.default_padTop)
        super(LabelValue, self).__init__(**kwargs)
        value_cont = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_right, padLeft=6)
        self.value = eveui.EveLabelMedium(parent=value_cont, align=eveui.Align.top_right, text=value, color=TextColor.HIGHLIGHT)
        self.label = eveui.EveLabelMedium(parent=self, align=eveui.Align.to_top, text=label, color=TextColor.SECONDARY)

    def set_label(self, label):
        self.label.text = label

    def set_value(self, value):
        self.value.text = value
