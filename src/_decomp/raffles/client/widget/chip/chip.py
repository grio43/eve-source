#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\chip.py
import eveui
from raffles.client import texture

class Chip(eveui.ContainerAutoSize):
    default_name = 'Chip'
    default_state = eveui.State.hidden
    default_align = eveui.Align.to_left
    default_alignMode = eveui.Align.center_left
    default_padRight = 4
    default_clipChildren = True
    isDragObject = True
    default_fixedHeight = 28
    max_width = 150

    def __init__(self, on_clear, text = '', **kwargs):
        super(Chip, self).__init__(**kwargs)
        self._on_clear = on_clear
        self._text = ''
        self._layout()
        if text:
            self.text = text

    def clear(self):
        self.text = ''

    def OnMouseEnter(self, *args):
        eveui.fade_in(self.stroke_frame, end_value=0.25, duration=0.1)
        eveui.fade_in(self.background_frame, end_value=0.75, duration=0.1)
        eveui.fade_in(self.clear_button, end_value=1, duration=0.1)

    def OnMouseExit(self, *args):
        eveui.fade(self.stroke_frame, end_value=0.1, duration=0.3)
        eveui.fade_out(self.background_frame, duration=0.3)
        eveui.fade_out(self.clear_button, duration=0.3)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if self._text == text:
            return
        self._text = text
        self.text_label.text = text
        if text:
            if self.text_label.MeasureTextSize(text)[0] > self.max_width:
                self.SetHint(text)
            else:
                self.SetHint(None)
            self.Show()
        else:
            self.Hide()

    def _layout(self):
        self.stroke_frame = eveui.Frame(bgParent=self, texturePath=texture.frame_1_corner, cornerSize=9, opacity=0.1)
        self.background_frame = eveui.Frame(bgParent=self, texturePath=texture.panel_1_corner, cornerSize=9, opacity=0, color=(0.125, 0.125, 0.125))
        self.text_label = eveui.EveLabelMedium(parent=self, align=eveui.Align.center_left, color=(0.75, 0.75, 0.75, 1), maxLines=1, padLeft=24, padRight=24, maxWidth=self.max_width)
        self.clear_button = eveui.ButtonIcon(parent=self, align=eveui.Align.center_right, left=6, texture_path=texture.window_close_icon, size=12, on_click=self._on_clear, opacity=0.0)
