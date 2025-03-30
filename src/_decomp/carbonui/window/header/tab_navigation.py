#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\header\tab_navigation.py
import signals
from carbonui import uiconst
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.window.header.base import WindowHeaderBase
from carbonui.window.settings import WindowMarginMode
from carbonui.control.tabGroup import TabGroup

class TabNavigationWindowHeader(Container, WindowHeaderBase):
    NORMAL_HEIGHT = 48
    ICON_SIZE_COMPACT = 24
    ICON_SIZE_NORMAL = 32
    ICON_OFFSET_COMPACT = -2
    ICON_OFFSET_NORMAL = -4
    _caption_icon = None
    _line = None
    _main_cont = None
    _tab_group = None

    def __init__(self, on_tab_selected = None):
        self.on_tab_selected = signals.Signal('TabNavigationWindowHeader.on_tab_selected')
        super(TabNavigationWindowHeader, self).__init__(height=self.NORMAL_HEIGHT)
        if on_tab_selected is not None:
            self.on_tab_selected.connect(on_tab_selected)

    @classmethod
    def desired_height(cls, window):
        if window.compact or window.collapsed or window.margin_mode == WindowMarginMode.COMPACT:
            return cls.COLLAPSED_HEIGHT
        else:
            return cls.NORMAL_HEIGHT

    @staticmethod
    def desired_tab_spacing(window):
        if window.compact or window.collapsed or window.margin_mode == WindowMarginMode.COMPACT:
            return 16
        else:
            return 32

    @property
    def extra_content(self):
        return self._extra_content

    @property
    def tab_group(self):
        return self._tab_group

    def select_tab(self, tab_id):
        self.tab_group.SelectByID(tab_id)

    def auto_select_tab(self):
        self.tab_group.AutoSelect()

    def mount(self, window):
        super(TabNavigationWindowHeader, self).mount(window)
        self._layout(window)
        window.on_collapsed_changed.connect(self._on_collapsed_changed)
        window.on_compact_mode_changed.connect(self._on_compact_changed)
        window.on_content_padding_changed.connect(self._on_content_padding_changed)
        window.on_header_inset_changed.connect(self._on_header_inset_changed)
        window.on_margin_mode_changed.connect(self._on_window_margin_mode_changed)

    def unmount(self, window):
        super(TabNavigationWindowHeader, self).unmount(window)
        self._clear()
        window.on_collapsed_changed.disconnect(self._on_collapsed_changed)
        window.on_compact_mode_changed.disconnect(self._on_compact_changed)
        window.on_content_padding_changed.disconnect(self._on_content_padding_changed)
        window.on_header_inset_changed.disconnect(self._on_header_inset_changed)
        window.on_margin_mode_changed.disconnect(self._on_window_margin_mode_changed)

    @classmethod
    def _get_icon_padding(cls, window):
        if window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            pad_left = cls.ICON_OFFSET_COMPACT
        elif window.margin_mode == WindowMarginMode.NORMAL:
            pad_left = cls.ICON_OFFSET_NORMAL
        else:
            raise ValueError('Unknown margin mode {!r}'.format(window.margin_mode))
        content_pad_left, _, _, _ = window.content_padding
        return (pad_left,
         0,
         content_pad_left,
         0)

    @classmethod
    def _get_icon_size(cls, window):
        if window.collapsed or window.compact or window.margin_mode == WindowMarginMode.COMPACT:
            return cls.ICON_SIZE_COMPACT
        else:
            return cls.ICON_SIZE_NORMAL

    @staticmethod
    def _get_icon_visible(window):
        return not (window.collapsed or window.compact)

    def _on_header_inset_changed(self, window):
        if self._main_cont:
            left, right = window.header_inset
            self._main_cont.padding = (left,
             0,
             right,
             0)

    def _on_collapsed_changed(self, window):
        self._update_caption_icon_display(window)
        self._update_height(window)
        self._update_icon_padding(window)
        self._update_icon_size(window)
        self._update_line_visible(window)
        self._update_tab_spacing(window)

    def _on_compact_changed(self, window):
        self._update_caption_icon_display(window)
        self._update_height(window)
        self._update_icon_padding(window)
        self._update_icon_size(window)

    def _on_content_padding_changed(self, window):
        self._update_icon_padding(window)

    def _on_window_margin_mode_changed(self, window):
        self._update_height(window)
        self._update_icon_padding(window)
        self._update_icon_size(window)
        self._update_tab_spacing(window)

    def _layout(self, window):
        self._line = DividerLine(parent=self, align=uiconst.TOBOTTOM_NOPUSH)
        self._line.display = self._get_line_visible(window)
        left_inset, right_inset = window.header_inset
        self._main_cont = Container(name='_main_cont', parent=self, align=uiconst.TOALL, padding=(left_inset,
         0,
         right_inset,
         0))
        content_pad_left, _, _, _ = window.content_padding
        icon_size = self._get_icon_size(window)
        self._caption_icon = Sprite(parent=ContainerAutoSize(parent=self._main_cont, align=uiconst.TOLEFT, padding=self._get_icon_padding(window)), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=icon_size, height=icon_size, texturePath=window.icon)
        self._update_caption_icon_display(window)
        self._tab_group = TabGroup(name='mainTabGroup', parent=self._main_cont, align=uiconst.TOLEFT, height=self.height, callback=self.on_tab_selected, autoselecttab=False, padding=0, tabSpacing=self.desired_tab_spacing(window), groupID=self.name + window.windowID, show_line=False, auto_size=True)
        self._extra_content = Container(name='extra', parent=self._main_cont, align=uiconst.TOALL, clipChildren=True)

    def _update_caption_icon_display(self, window):
        if self._caption_icon and self._caption_icon.parent:
            self._caption_icon.parent.display = self._get_icon_visible(window)

    def _update_height(self, window):
        self.height = self.desired_height(window)
        if self._tab_group:
            self._tab_group.height = self.height

    def _update_icon_size(self, window):
        if self._caption_icon:
            size = self._get_icon_size(window)
            self._caption_icon.width = size
            self._caption_icon.height = size

    def _update_icon_padding(self, window):
        if self._caption_icon and self._caption_icon.parent:
            self._caption_icon.parent.padding = self._get_icon_padding(window)

    def _update_tab_spacing(self, window):
        if self._tab_group:
            self._tab_group.tab_spacing = self.desired_tab_spacing(window)

    @staticmethod
    def _get_line_visible(window):
        return not window.collapsed

    def _update_line_visible(self, window):
        if self._line:
            self._line.display = self._get_line_visible(window)

    def _clear(self):
        self.Flush()
        self._caption_icon = None
        self._line = None
        self._main_cont = None
        self._tab_group = None
        self.on_tab_selected.clear()
