#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\scrollbar.py
import datetime
import gametime
import mathext
import signals
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import Axis, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.text.color import TextColor
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.dpi import reverse_scale_dpi
from carbonui.util.various_unsorted import GetWindowAbove
from chroma import Color
from eve.client.script.ui import eveColor, eveThemeColor

class Scrollbar(Container):
    TRACK_COLOR = (0.0, 0.0, 0.0)
    TRACK_SIZE = 8
    TRACK_OPACITY_INACTIVE = 0.0
    TRACK_OPACITY_ACTIVE = 0.3
    HANDLE_THICKNESS_IDLE = 2
    HANDLE_THICKNESS_HOVER = 4
    HANDLE_SIZE_MIN = 16
    HANDLE_HIGHLIGHT_DURATION = datetime.timedelta(milliseconds=300)
    PAGE_SCROLLING_INITIAL_DELAY = 0.3
    PAGE_SCROLLING_INTERVAL = 0.05
    _active = False
    _handle = None
    _handle_color_override = None
    _handle_highlight_tasklet = None
    _handle_highlight_timestamp = None
    _hovered = False
    _on_scroll_fraction_changed = None
    _page_scrolling_tasklet = None
    _track = None

    def __init__(self, axis, scroll_fraction = 0.0, handle_size_fraction = 0.0, on_scroll_fraction_changed = None, state = uiconst.UI_NORMAL, **kwargs):
        self._axis = axis
        self._scroll_fraction = scroll_fraction
        self._handle_size_fraction = handle_size_fraction
        super(Scrollbar, self).__init__(state=state, **kwargs)
        window_above = GetWindowAbove(self)
        if window_above:
            self._active = window_above.active
        self._layout()
        if on_scroll_fraction_changed:
            self.on_scroll_fraction_changed.connect(on_scroll_fraction_changed)

    @property
    def axis(self):
        return self._axis

    @property
    def scrolling(self):
        is_page_scrolling = self._page_scrolling_tasklet is not None
        if self._handle:
            return self._handle.scrolling or is_page_scrolling
        else:
            return is_page_scrolling

    @property
    def handle_size_fraction(self):
        return self._handle_size_fraction

    @handle_size_fraction.setter
    def handle_size_fraction(self, value):
        value = mathext.clamp(value, 0.0, 1.0)
        if self._handle_size_fraction != value:
            self._handle_size_fraction = value
            self._update_handle_size_and_position()

    @property
    def scroll_fraction(self):
        return self._scroll_fraction

    @scroll_fraction.setter
    def scroll_fraction(self, value):
        value = mathext.clamp(value, 0.0, 1.0)
        if self._scroll_fraction != value:
            self._scroll_fraction = value
            self._update_handle_size_and_position()
            if self._on_scroll_fraction_changed is not None:
                self._on_scroll_fraction_changed(self)

    @property
    def on_scroll_fraction_changed(self):
        if self._on_scroll_fraction_changed is None:
            self._on_scroll_fraction_changed = signals.Signal('{}.on_scroll_fraction_changed'.format(self.__class__.__name__))
        return self._on_scroll_fraction_changed

    def scroll_by_page(self, page_count = 1):
        scrollable_portion = 1.0 - self._handle_size_fraction
        scroll_amount = page_count * self._handle_size_fraction
        scroll_fraction = self.scroll_fraction + scroll_amount / scrollable_portion
        self._set_scroll_fraction_with_highlight(scroll_fraction)

    def scroll_to_fraction(self, scroll_fraction):
        self._set_scroll_fraction_with_highlight(scroll_fraction)

    def _set_scroll_fraction_with_highlight(self, scroll_fraction):
        old_scroll_fraction = self.scroll_fraction
        self.scroll_fraction = scroll_fraction
        if not mathext.is_close(old_scroll_fraction, scroll_fraction):
            self._highlight_scroll_handle()

    def _layout(self):
        handle_width_min, handle_height_min = self._get_handle_size_min()
        self._handle = ScrollHandle(parent=self, align=self._get_handle_align(), axis=self._axis, expanded=self._get_handle_expanded(), color=self._get_handle_color(), on_scroll_move=self._on_handle_scroll_move, on_hovered_changed=self._on_handle_hovered_changed, minWidth=handle_width_min, minHeight=handle_height_min)
        self._track = Fill(bgParent=self, align=uiconst.TOALL, color=self.TRACK_COLOR, opacity=self._get_track_opacity())

    def _get_dimensions(self):
        if self.align == uiconst.TOALL:
            return (0, 0)
        if self._axis == Axis.HORIZONTAL:
            height = self.TRACK_SIZE
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
                height += self.padTop + self.padBottom
            return (self.width, height)
        if self._axis == Axis.VERTICAL:
            width = self.TRACK_SIZE
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
                width += self.padLeft + self.padRight
            return (width, self.height)

    def _update_dimensions(self):
        self.width, self.height = self._get_dimensions()

    def _get_handle_align(self):
        if self._axis == Axis.HORIZONTAL:
            return uiconst.TOLEFT_PROP
        if self._axis == Axis.VERTICAL:
            return uiconst.TOTOP_PROP

    def _get_handle_color(self):
        if self._handle_color_override is not None:
            return self._handle_color_override
        elif self._handle and self._handle.hovered:
            return self._get_handle_highlight_color()
        elif self._hovered:
            return Color.from_rgba(*eveThemeColor.THEME_FOCUSDARK).with_alpha(0.6)
        else:
            return TextColor.DISABLED

    @staticmethod
    def _get_handle_highlight_color():
        return eveThemeColor.THEME_FOCUS

    def _update_handle_color(self, duration = 0.3):
        if self._handle:
            animations.SpColorMorphTo(self._handle, startColor=self._handle.color, endColor=self._get_handle_color(), duration=duration)

    def _highlight_scroll_handle(self):
        self._handle_highlight_timestamp = gametime.now()
        if self._handle_highlight_tasklet is None:
            self._handle_highlight_tasklet = uthread2.start_tasklet(self._do_highlight_handle)

    def _do_highlight_handle(self):
        try:
            self._handle_color_override = self._get_handle_highlight_color()
            self._update_handle_color(duration=0.1)
            while True:
                remaining = (self._handle_highlight_timestamp + self.HANDLE_HIGHLIGHT_DURATION - gametime.now()).total_seconds()
                if remaining > 0.0:
                    uthread2.sleep(remaining)
                else:
                    self._handle_color_override = None
                    self._update_handle_color(duration=0.5)
                    break

        finally:
            self._handle_highlight_tasklet = None

    def _get_handle_size_min(self):
        if self._axis == Axis.HORIZONTAL:
            return (self.HANDLE_SIZE_MIN, None)
        if self._axis == Axis.VERTICAL:
            return (None, self.HANDLE_SIZE_MIN)

    def _update_handle_size_min(self):
        if self._handle:
            self._handle.minWidth, self._handle.minHeight = self._get_handle_size_min()

    def _get_current_handle_length(self):
        if self._axis == Axis.HORIZONTAL:
            return reverse_scale_dpi(self._handle.displayWidth)
        if self._axis == Axis.VERTICAL:
            return reverse_scale_dpi(self._handle.displayHeight)

    def _get_current_track_length(self):
        if self._axis == Axis.HORIZONTAL:
            return reverse_scale_dpi(self.displayWidth)
        if self._axis == Axis.VERTICAL:
            return reverse_scale_dpi(self.displayHeight)

    def _get_handle_size_and_position(self):
        if self._handle:
            track_length = self._get_current_track_length()
            handle_length = self._get_current_handle_length()
            if mathext.is_almost_zero(track_length):
                handle_size_fraction = 1.0
            else:
                handle_size_fraction = handle_length / float(track_length)
            position = mathext.clamp(self._scroll_fraction * (1.0 - handle_size_fraction), low=0.0, high=1.0)
            if self._axis == Axis.HORIZONTAL:
                return (self._handle_size_fraction, 0, position)
            if self._axis == Axis.VERTICAL:
                return (0, self._handle_size_fraction, position)
        else:
            return (0, 0, 0)

    def _update_handle_size_and_position(self):
        if self._handle:
            self._handle.width, self._handle.height, position = self._get_handle_size_and_position()
            if self._axis == Axis.HORIZONTAL:
                self._handle.left = position
            elif self._axis == Axis.VERTICAL:
                self._handle.top = position

    def _get_handle_expanded(self):
        return self._hovered

    def _update_handle_expanded(self):
        if self._handle:
            self._handle.expanded = self._get_handle_expanded()

    def _on_handle_scroll_move(self, delta):
        scrollable_length = self._get_scrollable_track_length()
        if mathext.is_almost_zero(scrollable_length):
            scroll_fraction = 0.0
        else:
            scroll_fraction = delta / float(scrollable_length)
        self.scroll_fraction += scroll_fraction

    def _get_scrollable_track_length(self):
        if self._handle:
            return self._get_current_track_length() - self._get_current_handle_length()
        else:
            return 0

    def _on_handle_hovered_changed(self, handle):
        self._update_handle_color(duration=0.1)

    def _get_track_opacity(self):
        if self._active or self._hovered:
            return self.TRACK_OPACITY_ACTIVE
        else:
            return self.TRACK_OPACITY_INACTIVE

    def _update_track_opacity(self):
        if self._track:
            animations.FadeTo(self._track, startVal=self._track.opacity, endVal=self._get_track_opacity(), duration=0.3)

    def _get_track_fraction_at_position(self, x, y):
        track_length = self._get_current_track_length()
        if self._axis == Axis.VERTICAL:
            mouse_position = y
            _, track_start = self.GetCurrentAbsolutePosition()
        else:
            mouse_position = x
            track_start, _ = self.GetCurrentAbsolutePosition()
        return mathext.clamp((mouse_position - track_start) / float(track_length), low=0.0, high=1.0)

    def _get_scroll_fraction_at_position(self, x, y):
        track_length = self._get_current_track_length()
        if self._axis == Axis.VERTICAL:
            mouse_position = y
            _, track_start = self.GetCurrentAbsolutePosition()
        else:
            mouse_position = x
            track_start, _ = self.GetCurrentAbsolutePosition()
        handle_length = self._get_current_handle_length()
        return mathext.clamp((mouse_position - track_start) / float(track_length - handle_length), low=0.0, high=1.0)

    def _start_page_scrolling(self, target_fraction):
        if target_fraction >= self.scroll_fraction:
            page_count = 1
        else:
            page_count = -1
        self.scroll_by_page(page_count)
        self._start_page_scrolling_tasklet(page_count)

    def _start_page_scrolling_tasklet(self, page_count):
        self._cancel_page_scrolling_maybe()
        self._page_scrolling_tasklet = uthread2.start_tasklet(self._page_scrolling_loop, page_count)

    def _cancel_page_scrolling_maybe(self):
        if self._page_scrolling_tasklet is not None:
            self._page_scrolling_tasklet.kill()
            self._page_scrolling_tasklet = None

    def _page_scrolling_loop(self, page_count):
        try:
            uthread2.sleep(self.PAGE_SCROLLING_INITIAL_DELAY)
            while True:
                if not uicore.uilib.leftbtn:
                    break
                if self._axis == Axis.VERTICAL:
                    handle_start = self._handle.top
                else:
                    handle_start = self._handle.left
                handle_end = handle_start + self._handle_size_fraction
                target_fraction = self._get_track_fraction_at_position(x=uicore.uilib.x, y=uicore.uilib.y)
                if page_count > 0 and target_fraction >= handle_end or page_count < 0 and target_fraction <= handle_start:
                    self.scroll_by_page(page_count)
                uthread2.sleep(self.PAGE_SCROLLING_INTERVAL)

        finally:
            self._page_scrolling_tasklet = None

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        self._update_dimensions()
        result = super(Scrollbar, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        self._update_handle_size_and_position()
        if self._handle._alignmentDirty:
            super(Scrollbar, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
        return result

    def OnWindowAboveSetActive(self):
        self._active = True
        self._update_track_opacity()
        self._update_handle_color()

    def OnWindowAboveSetInactive(self):
        self._active = False
        self._update_track_opacity()
        self._update_handle_color()

    def OnMouseEnter(self, *args):
        self._hovered = True
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self._update_handle_color(duration=0.1)
        self._update_handle_expanded()
        self._update_track_opacity()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update_handle_color()
        self._update_handle_expanded()
        self._update_track_opacity()

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._start_page_scrolling(target_fraction=self._get_scroll_fraction_at_position(x=uicore.uilib.x, y=uicore.uilib.y))

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._cancel_page_scrolling_maybe()


class ScrollHandle(Container):
    _fill = None
    _fill_expanded = None
    _hovered = False
    _on_hovered_changed = None
    _scrolling = False
    _last_mouse_position = None
    _on_scroll_move = None

    def __init__(self, axis, color = None, expanded = False, on_hovered_changed = None, on_scroll_move = None, state = uiconst.UI_NORMAL, **kwargs):
        if color is None:
            color = eveColor.WHITE
        color = Color.from_any(color)
        self._axis = axis
        self._expanded = expanded
        self._color = color
        super(ScrollHandle, self).__init__(state=state, **kwargs)
        self.opacity = color.opacity
        self._layout()
        if on_hovered_changed is not None:
            self.on_hovered_changed.connect(on_hovered_changed)
        if on_scroll_move is not None:
            self.on_scroll_move.connect(on_scroll_move)

    @property
    def color(self):
        return self._color.with_alpha(self.opacity)

    @color.setter
    def color(self, value):
        self._color = Color.from_any(value)
        self.opacity = self._color.opacity
        if self._fill:
            self._fill.color = self._color.rgb
        if self._fill_expanded:
            self._fill_expanded.color = self._color.rgb

    @property
    def expanded(self):
        return self._expanded

    @expanded.setter
    def expanded(self, value):
        if self._expanded != value:
            self._expanded = value
            self._update_expanded()

    @property
    def hovered(self):
        return self._hovered

    @property
    def on_hovered_changed(self):
        if self._on_hovered_changed is None:
            self._on_hovered_changed = signals.Signal('{}.on_hovered_changed'.format(self.__class__.__name__))
        return self._on_hovered_changed

    @property
    def scrolling(self):
        return self._scrolling

    @property
    def on_scroll_move(self):
        if self._on_scroll_move is None:
            self._on_scroll_move = signals.Signal('{}.on_scroll_move'.format(self.__class__.__name__))
        return self._on_scroll_move

    def _layout(self):
        self._fill = Fill(parent=self, align=uiconst.TOALL, padding=self._get_fill_padding(expanded=False), color=self._color.rgb)
        self._fill_expanded = Fill(parent=self, align=uiconst.TOALL, padding=self._get_fill_padding(expanded=True), color=self._color.rgb, opacity=1.0 if self._expanded else 0.0, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)

    @staticmethod
    def _get_fill_padding(expanded):
        if expanded:
            handle_thickness = Scrollbar.HANDLE_THICKNESS_HOVER
        else:
            handle_thickness = Scrollbar.HANDLE_THICKNESS_IDLE
        pad = int(round((Scrollbar.TRACK_SIZE - handle_thickness) / 2.0))
        return (pad,
         pad,
         pad,
         pad)

    def _update_expanded(self):
        if self._fill_expanded:
            if self._expanded:
                animations.FadeIn(self._fill_expanded, duration=0.2)
            else:
                animations.FadeOut(self._fill_expanded, duration=0.2)

    def _start_scrolling(self):
        if not self._scrolling:
            self._scrolling = True
            if self._axis == Axis.HORIZONTAL:
                self._last_mouse_position = uicore.uilib.x
            elif self._axis == Axis.VERTICAL:
                self._last_mouse_position = uicore.uilib.y

    def _update_scrolling(self):
        current_position = 0
        if self._axis == Axis.HORIZONTAL:
            current_position = uicore.uilib.x
        elif self._axis == Axis.VERTICAL:
            current_position = uicore.uilib.y
        delta = current_position - self._last_mouse_position
        if delta != 0 and self._on_scroll_move is not None:
            self._on_scroll_move(delta)
        self._last_mouse_position = current_position

    def _stop_scrolling(self):
        if self._scrolling:
            self._scrolling = False

    def OnMouseEnter(self, *args):
        self._hovered = True
        if self._on_hovered_changed:
            self._on_hovered_changed(self)

    def OnMouseExit(self, *args):
        self._hovered = False
        if self._on_hovered_changed:
            self._on_hovered_changed(self)

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._start_scrolling()

    def OnMouseMove(self, *args):
        if self._scrolling:
            self._update_scrolling()

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._stop_scrolling()
