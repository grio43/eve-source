#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\header\default.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.window.header.base import WindowHeaderBase
from carbonui.window.header.caption import WindowCaption
from carbonui.window.settings import WindowMarginMode

class DefaultWindowHeader(WindowHeaderBase, Container):
    ICON_SIZE_COMPACT = 24
    ICON_SIZE_NORMAL = 32
    ICON_OFFSET_COMPACT = -2
    ICON_OFFSET_NORMAL = -4
    HAS_SUFFICIENT_BOTTOM_PADDING = True

    def __init__(self, show_caption = True):
        self._show_caption = show_caption
        self._caption_label = None
        super(DefaultWindowHeader, self).__init__()

    @staticmethod
    def caption_font_size(window):
        if window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            return 12
        else:
            return 18

    @staticmethod
    def caption_color(window):
        if window.active:
            return TextColor.HIGHLIGHT
        elif window.IsLightBackgroundEnabled():
            return TextColor.NORMAL
        else:
            return TextColor.SECONDARY

    @staticmethod
    def desired_height(window):
        if window.stacked:
            return 0
        elif window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            return WindowHeaderBase.COLLAPSED_HEIGHT
        else:
            return 48

    @staticmethod
    def desired_padding(window):
        left, right = window.header_inset
        return (left,
         0,
         right,
         0)

    @staticmethod
    def should_show_icon(window):
        return not window.compact and not window.collapsed and getattr(window, 'hasWindowIcon', True)

    @property
    def extra_content(self):
        return self._extra_content

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
        super(DefaultWindowHeader, self).mount(window)
        self._layout(window)
        self.height = self.desired_height(window)
        self._update_caption(window)
        self._update_caption_icon_display(window)
        window.on_caption_changed.connect(self._on_caption_changed)
        window.on_collapsed_changed.connect(self._on_collapsed_changed)
        window.on_compact_mode_changed.connect(self._on_compact_mode_changed)
        window.on_header_inset_changed.connect(self._on_header_inset_changed)
        window.on_icon_changed.connect(self._on_icon_changed)
        window.on_margin_mode_changed.connect(self._on_margin_mode_changed)
        window.on_stacked_changed.connect(self._on_stacked_changed)

    def unmount(self, window):
        window.on_caption_changed.disconnect(self._on_caption_changed)
        window.on_collapsed_changed.disconnect(self._on_collapsed_changed)
        window.on_compact_mode_changed.disconnect(self._on_compact_mode_changed)
        window.on_header_inset_changed.disconnect(self._on_header_inset_changed)
        window.on_icon_changed.disconnect(self._on_icon_changed)
        window.on_margin_mode_changed.disconnect(self._on_margin_mode_changed)
        window.on_stacked_changed.disconnect(self._on_stacked_changed)

    @classmethod
    def _get_icon_offset(cls, window):
        if window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            return cls.ICON_OFFSET_COMPACT
        else:
            return cls.ICON_OFFSET_NORMAL

    @classmethod
    def _get_icon_size(cls, window):
        if window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            return cls.ICON_SIZE_COMPACT
        else:
            return cls.ICON_SIZE_NORMAL

    def _on_caption_changed(self, window):
        self._update_caption(window)

    def _on_collapsed_changed(self, window):
        self._update_caption(window, animate=True)
        self._update_caption_icon_display(window)
        self._update_height(window)
        self._update_icon_size(window)

    def _on_compact_mode_changed(self, window):
        self._update_caption(window, animate=True)
        self._update_caption_icon_display(window)
        self._update_height(window)
        self._update_icon_size(window)

    def _on_header_inset_changed(self, window):
        self._main_cont.padding = self.desired_padding(window)

    def _on_margin_mode_changed(self, window):
        self._update_caption(window)
        self._update_height(window)
        self._update_icon_size(window)
        self._update_icon_size(window)

    def _on_stacked_changed(self, window):
        self._update_height(window)

    def _on_icon_changed(self, window):
        self._caption_icon.display = window.icon is not None
        self._caption_icon.texturePath = window.icon

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
                self._caption_label.padLeft = 8 if self.should_show_icon(window) else 0
        elif not self._show_caption:
            if self._caption_label is not None:
                self._caption_label.Close()
                self._caption_label = None

    def _update_caption_icon_display(self, window):
        self._caption_icon.parent.display = self.should_show_icon(window)

    def _update_height(self, window):
        self.height = self.desired_height(window)

    def _update_icon_size(self, window):
        size = self._get_icon_size(window)
        self._caption_icon.width = size
        self._caption_icon.height = size
        self._caption_icon.parent.left = self._get_icon_offset(window)
        self.minWidth = size
        self.minHeight = size

    def _create_caption_label(self, window):
        left_pad = 8 if self.should_show_icon(window) else 0
        self._caption_label = WindowCaption(parent=self._main_cont, text=window.caption, font_size=self.caption_font_size(window), color=self.caption_color(window), padding=(left_pad,
         0,
         8,
         0))

    def _layout(self, window):
        left_inset, right_inset = window.header_inset
        self._main_cont = Container(name='main', parent=self, align=uiconst.TOALL, padding=(left_inset,
         0,
         right_inset,
         0))
        self._create_icon(window)
        self._update_caption_icon_display(window)
        self._create_caption_label(window)
        self._extra_content = Container(name='extra', parent=self._main_cont, align=uiconst.TOALL, clipChildren=True)
        icon_size = self._get_icon_size(window)
        self.minWidth = icon_size
        self.minHeight = icon_size

    def _create_icon(self, window):
        size = self._get_icon_size(window)
        self._caption_icon = Sprite(parent=ContainerAutoSize(name='icon', parent=self._main_cont, align=uiconst.TOLEFT, left=self._get_icon_offset(window)), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=size, height=size, texturePath=window.icon)
