#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\header\small.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.window.header.base import WindowHeaderBase
from carbonui.window.header.caption import WindowCaption

class SmallWindowHeader(Container, WindowHeaderBase):
    HAS_SUFFICIENT_BOTTOM_PADDING = True

    def __init__(self, show_caption = True, fixed_height = None):
        self._show_caption = show_caption
        self._caption_label = None
        self._fixed_height = fixed_height
        super(SmallWindowHeader, self).__init__()

    @staticmethod
    def caption_font_size(window):
        return 12

    @staticmethod
    def caption_color(window):
        if window.active:
            return TextColor.HIGHLIGHT
        elif window.IsLightBackgroundEnabled():
            return TextColor.NORMAL
        else:
            return TextColor.SECONDARY

    @property
    def extra_content(self):
        return self._extra_content

    @property
    def fixed_height(self):
        return self._fixed_height

    @fixed_height.setter
    def fixed_height(self, value):
        if value != self._fixed_height:
            self._fixed_height = value
            window = self.window
            if window is not None:
                self._update_height(window)

    @property
    def show_caption(self):
        return self._show_caption

    @show_caption.setter
    def show_caption(self, value):
        if self._show_caption != value:
            self._show_caption = value
            window = self.window
            if window is not None:
                self._update_caption(window)

    def mount(self, window):
        super(SmallWindowHeader, self).mount(window)
        self._layout(window)
        self._update_height(window)
        self._update_caption(window)
        window.on_active_changed.connect(self._on_active_changed)
        window.on_caption_changed.connect(self._on_caption_changed)
        window.on_collapsed_changed.connect(self._on_collapsed_changed)
        window.on_header_inset_changed.connect(self._on_header_inset_changed)
        window.on_stacked_changed.connect(self._on_stacked_changed)

    def unmount(self, window):
        super(SmallWindowHeader, self).unmount(window)
        window.on_active_changed.disconnect(self._on_active_changed)
        window.on_caption_changed.disconnect(self._on_caption_changed)
        window.on_collapsed_changed.disconnect(self._on_collapsed_changed)
        window.on_header_inset_changed.disconnect(self._on_header_inset_changed)
        window.on_stacked_changed.disconnect(self._on_stacked_changed)

    def _on_active_changed(self, window):
        self._update_caption(window, animate=True)

    def _on_caption_changed(self, window):
        self._update_caption(window)

    def _on_collapsed_changed(self, window):
        self._update_caption(window, animate=True)

    def _on_header_inset_changed(self, window):
        self._main_cont.padding = self._desired_padding(window)

    def _on_stacked_changed(self, window):
        self._update_height(window)

    def _desired_height(self, window):
        if window.stacked:
            return 0
        elif self._fixed_height is not None:
            return self._fixed_height
        else:
            return 32

    @staticmethod
    def _desired_padding(window):
        left, right = window.header_inset
        return (left,
         0,
         right,
         0)

    def _update_height(self, window):
        self.height = self._desired_height(window)

    def _update_caption(self, window, animate = False):
        if self._show_caption or window.collapsed:
            if self._caption_label is None:
                self._create_caption_label(window)
            else:
                self._caption_label.font_size = self.caption_font_size(window)
                caption_color = self.caption_color(window)
                if animate:
                    animations.SpColorMorphTo(self._caption_label, startColor=self._caption_label.color, endColor=caption_color, duration=uiconst.TIME_ENTRY)
                else:
                    self._caption_label.color = caption_color
                self._caption_label.text = window.caption
                self._caption_label.padLeft = 0
        elif not self._show_caption:
            if self._caption_label is not None:
                self._caption_label.Close()
                self._caption_label = None

    def _create_caption_label(self, window):
        self._caption_label = WindowCaption(parent=self._main_cont, text=window.caption, font_size=self.caption_font_size(window), color=self.caption_color(window), padding=(0, 0, 8, 0))

    def _layout(self, window):
        left_inset, right_inset = window.header_inset
        self._main_cont = Container(name='_main_cont', parent=self, align=uiconst.TOALL, padding=(left_inset,
         0,
         right_inset,
         0))
        self._create_caption_label(window)
        self._extra_content = Container(name='extra_content', parent=self._main_cont, align=uiconst.TOALL, clipChildren=True)
