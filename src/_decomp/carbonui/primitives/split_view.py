#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\split_view.py
import signals
from carbonui import uiconst
from carbonui.primitives.childrenlist import PyChildrenList
from carbonui.primitives.container import Container
from carbonui.uianimations import animations

class PanelMode(object):
    INLINE = 1
    COMPACT_INLINE = 2
    OVERLAY = 3
    COMPACT_OVERLAY = 4

    @classmethod
    def is_compact(cls, panel_mode):
        return panel_mode == cls.COMPACT_INLINE or panel_mode == cls.COMPACT_OVERLAY

    @classmethod
    def is_inline(cls, panel_mode):
        return panel_mode == cls.INLINE or panel_mode == cls.COMPACT_INLINE

    @classmethod
    def is_overlay(cls, panel_mode):
        return panel_mode == cls.OVERLAY or panel_mode == cls.COMPACT_OVERLAY


class PanelPlacement(object):
    LEFT = 1
    RIGHT = 2


EXPAND_DURATION = 0.2
COLLAPSE_DURATION = 0.2

class SplitView(Container):
    default_clipChildren = True

    def __init__(self, compact_panel_width = 48, expanded = False, expanded_panel_width = 300, panel_mode = PanelMode.INLINE, panel_placement = PanelPlacement.LEFT, static_panel_inner_width = True, **kwargs):
        self._compact_panel_width = compact_panel_width
        self._expanded = expanded
        self._expanded_panel_width = expanded_panel_width
        self._is_animating = False
        self._panel_mode = panel_mode
        self._panel_placement = panel_placement
        self._static_panel_inner_width = static_panel_inner_width
        self._on_expanded_changed = None
        self._on_panel_mode_changed = None
        self._on_panel_placement_changed = None
        super(SplitView, self).__init__(**kwargs)
        self._panel_wrap = Container(name='panel_wrap', parent=self, align=self._get_panel_wrap_align(), width=self._get_panel_width(), clipChildren=True)
        self._panel = Container(name='panel', parent=self._panel_wrap, align=self._get_panel_align(), width=self._get_panel_inner_width())
        self._content = Container(name='content', parent=self, align=uiconst.TOALL)
        self.children = LockedChildrenList(self.children, message="Don't add children directly to a SplitView. Use the `content` and `panel` properties instead.")

    @property
    def collapsed(self):
        return not self._expanded

    @collapsed.setter
    def collapsed(self, value):
        self._set_expanded(not value, animate=True)

    @property
    def on_collapsed_changed(self):
        return self.on_expanded_changed

    @property
    def compact_panel_width(self):
        return self._compact_panel_width

    @compact_panel_width.setter
    def compact_panel_width(self, value):
        if self._compact_panel_width != value:
            self._compact_panel_width = value
            self._update_compact_panel_width()

    @property
    def content(self):
        return self._content

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, value):
        self._set_expanded(value, animate=True)

    def is_expanded(self):
        return self.expanded

    @property
    def on_expanded_changed(self):
        if self._on_expanded_changed is None:
            self._on_expanded_changed = signals.Signal('{}.on_expanded_changed'.format(self.__class__.__name__))
        return self._on_expanded_changed

    @property
    def expanded_panel_width(self):
        return self._expanded_panel_width

    @expanded_panel_width.setter
    def expanded_panel_width(self, value):
        if self._expanded_panel_width != value:
            self._expanded_panel_width = value
            self._update_expanded_panel_width()

    @property
    def panel(self):
        return self._panel

    @property
    def panel_mode(self):
        return self._panel_mode

    @panel_mode.setter
    def panel_mode(self, value):
        if self._panel_mode != value:
            self._panel_mode = value
            self._update_panel_mode()
            self._emit_panel_mode_changed()

    @property
    def on_panel_mode_changed(self):
        if self._on_panel_mode_changed is None:
            self._on_panel_mode_changed = signals.Signal('{}.on_panel_mode_changed'.format(self.__class__.__name__))
        return self._on_panel_mode_changed

    @property
    def panel_placement(self):
        return self._panel_placement

    @panel_placement.setter
    def panel_placement(self, value):
        if self._panel_placement != value:
            self._panel_placement = value
            self._update_panel_placement()
            self._emit_panel_placement_changed()

    @property
    def on_panel_placement_changed(self):
        if self._on_panel_placement_changed is None:
            self._on_panel_placement_changed = signals.Signal('{}.on_panel_placement_changed'.format(self.__class__.__name__))
        return self._on_panel_placement_changed

    @property
    def static_panel_inner_width(self):
        return self._static_panel_inner_width

    @static_panel_inner_width.setter
    def static_panel_inner_width(self, value):
        if self._static_panel_inner_width != value:
            self._static_panel_inner_width = value
            self._update_static_panel_inner_width()

    @property
    def is_animating(self):
        return self._is_animating

    def collapse(self, animate = True):
        self._set_expanded(False, animate)

    def expand(self, animate = True):
        self._set_expanded(True, animate)

    def _emit_expanded_changed(self):
        if self._on_expanded_changed is not None:
            self._on_expanded_changed(self.expanded)

    def _emit_panel_mode_changed(self):
        if self._on_panel_mode_changed is not None:
            self._on_panel_mode_changed(self)

    def _emit_panel_placement_changed(self):
        if self._on_panel_placement_changed is not None:
            self._on_panel_placement_changed(self)

    def _get_panel_align(self):
        if self._static_panel_inner_width:
            return uiconst.TOLEFT
        else:
            return uiconst.TOALL

    def _get_panel_inner_width(self):
        if self._static_panel_inner_width:
            return self._expanded_panel_width
        else:
            return 0

    def _get_panel_wrap_align(self):
        if self._panel_placement == PanelPlacement.LEFT:
            if PanelMode.is_inline(self._panel_mode):
                return uiconst.TOLEFT
            else:
                return uiconst.TOLEFT_NOPUSH
        elif self._panel_placement == PanelPlacement.RIGHT:
            if PanelMode.is_inline(self._panel_mode):
                return uiconst.TORIGHT
            else:
                return uiconst.TORIGHT_NOPUSH

    def _get_panel_width(self):
        if self._expanded:
            return self._expanded_panel_width
        else:
            return self._get_panel_collapsed_width()

    def _get_panel_collapsed_width(self):
        if PanelMode.is_compact(self._panel_mode):
            return self._compact_panel_width
        else:
            return 0

    def _update_compact_panel_width(self):
        if not self._expanded and PanelMode.is_compact(self._panel_mode):
            animations.StopAnimation(self._panel_wrap, 'width')
            self._panel_wrap.width = self._get_panel_collapsed_width()

    def _update_expanded_panel_width(self):
        self._panel.width = self._get_panel_inner_width()
        if self._expanded:
            animations.StopAnimation(self._panel_wrap, 'width')
            self._panel_wrap.width = self._get_panel_width()

    def _update_panel_mode(self):
        self._panel_wrap.align = self._get_panel_wrap_align()
        animations.StopAnimation(self._panel_wrap, 'width')
        self._panel_wrap.width = self._get_panel_width()

    def _update_panel_placement(self):
        self._panel_wrap.align = self._get_panel_wrap_align()

    def _update_static_panel_inner_width(self):
        self._panel.align = self._get_panel_align()
        self._update_expanded_panel_width()

    def _set_expanded(self, value, animate):
        if self._expanded != value:
            self._expanded = value
            self._is_animating = animate
            if self._expanded:
                self._expand(animate)
            else:
                self._collapse(animate)
            self._emit_expanded_changed()

    def _expand(self, animate):
        if animate:
            animations.MorphScalar(self._panel_wrap, 'width', startVal=self._panel_wrap.width, endVal=self._expanded_panel_width, duration=EXPAND_DURATION, callback=self._on_animation_stopped)
        else:
            self._panel_wrap.width = self._expanded_panel_width

    def _collapse(self, animate):
        if animate:
            animations.MorphScalar(self._panel_wrap, 'width', startVal=self._panel_wrap.width, endVal=self._get_panel_collapsed_width(), duration=COLLAPSE_DURATION, callback=self._on_animation_stopped)
        else:
            self._panel_wrap.width = self._get_panel_collapsed_width()

    def _on_animation_stopped(self):
        self._is_animating = False


class LockedChildrenList(PyChildrenList):

    def __init__(self, other, message):
        self._message = message
        super(LockedChildrenList, self).__init__(owner=other.GetOwner(), children=list(other))

    def append(self, obj):
        raise RuntimeError(self._message)

    def insert(self, idx, obj):
        raise RuntimeError(self._message)
