#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\resize_handle.py
import math
import signals
import trinity
from carbonui import Axis, AxisAlignment, uiconst
from carbonui.decorative.divider_line import DividerLine
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.dpi import reverse_scale_dpi
from eve.client.script.ui import eveThemeColor

class ResizeHandle(Container):
    HANDLE_THICKNESS = 1
    MASK_SIZE = 128
    _dragging = False
    _handle = None
    _last_mouse_position = (0, 0)
    _line = None
    _on_drag_end = None
    _on_drag_move = None
    _on_drag_start = None

    def __init__(self, orientation, on_drag_start = None, on_drag_move = None, on_drag_end = None, show_line = False, cross_axis_alignment = AxisAlignment.CENTER, size = 8, state = uiconst.UI_NORMAL, **kwargs):
        self._cross_axis_alignment = cross_axis_alignment
        self._orientation = orientation
        self._size = size
        self._show_line = show_line
        width, height = self._get_dimensions()
        super(ResizeHandle, self).__init__(width=width, height=height, cursor=self._get_cursor(), state=state, **kwargs)
        self._create_handle()
        if self._show_line:
            self._create_line()
        if on_drag_start:
            self.on_drag_start.connect(on_drag_start)
        if on_drag_move:
            self.on_drag_move.connect(on_drag_move)
        if on_drag_end:
            self.on_drag_end.connect(on_drag_end)

    @property
    def cross_axis_alignment(self):
        return self._cross_axis_alignment

    @cross_axis_alignment.setter
    def cross_axis_alignment(self, value):
        if self._cross_axis_alignment != value:
            self._cross_axis_alignment = value
            self.FlagAlignmentDirty()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        if self._orientation != value:
            self._orientation = value
            self._update_orientation()

    @property
    def show_line(self):
        return self._show_line

    @show_line.setter
    def show_line(self, value):
        if self._show_line != value:
            self._show_line = value
            self._update_show_line()

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if self._size != value:
            self._size = value
            self.FlagAlignmentDirty()

    @property
    def on_drag_start(self):
        if self._on_drag_start is None:
            self._on_drag_start = signals.Signal('{}.on_drag_start'.format(self.__class__.__name__))
        return self._on_drag_start

    @property
    def on_drag_move(self):
        if self._on_drag_move is None:
            self._on_drag_move = signals.Signal('{}.on_drag_move'.format(self.__class__.__name__))
        return self._on_drag_move

    @property
    def on_drag_end(self):
        if self._on_drag_end is None:
            self._on_drag_end = signals.Signal('{}.on_drag_end'.format(self.__class__.__name__))
        return self._on_drag_end

    def _get_cursor(self):
        if self._orientation == Axis.HORIZONTAL:
            return uiconst.UICORSOR_VERTICAL_RESIZE
        if self._orientation == Axis.VERTICAL:
            return uiconst.UICORSOR_HORIZONTAL_RESIZE

    def _update_cursor(self):
        self.cursor = self._get_cursor()

    def _update_axis(self):
        self._update_cursor()
        if self._handle:
            self._handle.align = self._get_handle_align()
        if self._line:
            self._line.align = self._get_handle_align()

    def _update_orientation(self):
        self._update_cursor()
        if self._handle:
            self._handle.align = self._get_handle_align()
        if self._line:
            self._line.align = self._get_handle_align()

    def _create_handle(self):
        self._handle = Sprite(parent=self, align=self._get_handle_align(), state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/ResizeHandle/fill.png', textureSecondaryPath='res:/UI/Texture/classes/ResizeHandle/mask.png', color=self._get_color(), spriteEffect=trinity.TR2_SFX_MODULATE, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5, opacity=0.0)
        self._update_mask()

    def _update_mask(self):
        x, y = self._handle.GetCurrentAbsolutePosition()
        w, h = self._handle.GetCurrentAbsoluteSize()
        px = x + w / 2.0 - uicore.uilib.x
        py = y + h / 2.0 - uicore.uilib.y
        self._handle.scaleSecondary = (w / float(self.MASK_SIZE), h / float(self.MASK_SIZE))
        self._handle.translationSecondary = (px / float(self.MASK_SIZE), py / float(self.MASK_SIZE))

    def _get_handle_align(self):
        if self._orientation == Axis.HORIZONTAL:
            return uiconst.TOTOP_NOPUSH
        if self._orientation == Axis.VERTICAL:
            return uiconst.TOLEFT_NOPUSH

    @staticmethod
    def _get_color():
        return eveThemeColor.THEME_ACCENT[:3]

    def _create_line(self, opacity_override = None):
        if opacity_override is not None:
            opacity = opacity_override
        else:
            opacity = self._get_line_opacity()
        self._line = DividerLine(parent=self, align=self._get_handle_align(), opacity=opacity)

    def _get_line_opacity(self):
        if self._show_line:
            return 1.0
        else:
            return 0.0

    def _update_line_opacity(self):
        if self._line:
            animations.FadeTo(self._line, startVal=self._line.opacity, endVal=self._get_line_opacity(), duration=0.3)

    def _update_show_line(self):
        if self._show_line and self._line is None:
            self._create_line(opacity_override=0.0)
        self._update_line_opacity()

    def OnColorThemeChanged(self):
        if self._handle:
            self._handle.color = self._get_color()

    def _get_dimensions(self):
        if self.align == uiconst.TOALL:
            return (0, 0)
        if self._orientation == Axis.HORIZONTAL:
            height = self._size
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_VERTICAL_PADDING:
                height += self.padTop + self.padBottom
            return (self.width, height)
        if self._orientation == Axis.VERTICAL:
            width = self._size
            if self.align in uiconst.ALIGNMENTS_WITH_INCLUDED_HORIZONTAL_PADDING:
                width += self.padLeft + self.padRight
            return (width, self.height)

    def _update_dimensions(self):
        self.width, self.height = self._get_dimensions()

    def _get_handle_dimensions(self):
        if self._orientation == Axis.HORIZONTAL:
            return (0, self.HANDLE_THICKNESS)
        if self._orientation == Axis.VERTICAL:
            return (self.HANDLE_THICKNESS, 0)

    def _update_handle_dimensions(self):
        width, height = self._get_handle_dimensions()
        if self._handle:
            self._handle.width = width
            self._handle.height = height
        if self._line:
            self._line.width = width
            self._line.height = height

    def _update_handle_position(self, budget_width, budget_height):
        left = 0
        top = 0
        if self._orientation == Axis.HORIZONTAL:
            if self._cross_axis_alignment == AxisAlignment.START:
                top = 0
            elif self._cross_axis_alignment == AxisAlignment.CENTER:
                top = int(math.floor((budget_height - self.HANDLE_THICKNESS) / 2.0))
            elif self._cross_axis_alignment == AxisAlignment.END:
                top = budget_height - self.HANDLE_THICKNESS
        elif self._cross_axis_alignment == AxisAlignment.START:
            left = 0
        elif self._cross_axis_alignment == AxisAlignment.CENTER:
            left = int(math.floor((budget_width - self.HANDLE_THICKNESS) / 2.0))
        elif self._cross_axis_alignment == AxisAlignment.END:
            left = budget_width - self.HANDLE_THICKNESS
        if self._handle:
            self._handle.left = left
            self._handle.top = top
        if self._line:
            self._line.left = left
            self._line.top = top

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        self._update_dimensions()
        self._update_handle_dimensions()
        self._update_handle_position(budget_width=reverse_scale_dpi(budgetWidth), budget_height=reverse_scale_dpi(budgetHeight))
        return super(ResizeHandle, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)

    def OnMouseDown(self, button):
        if not self._dragging and button == uiconst.MOUSELEFT:
            self._dragging = True
            self._last_mouse_position = (uicore.uilib.x, uicore.uilib.y)
            if self._on_drag_start is not None:
                self._on_drag_start()

    def OnMouseUp(self, button):
        if self._dragging and button == uiconst.MOUSELEFT:
            self._dragging = False
            if self._on_drag_end is not None:
                self._on_drag_end()

    def OnMouseMove(self, *args):
        self._update_mask()
        if self._dragging:
            if self._on_drag_move is not None:
                if self._orientation == Axis.VERTICAL:
                    self._on_drag_move(uicore.uilib.x - self._last_mouse_position[0])
                elif self._orientation == Axis.HORIZONTAL:
                    self._on_drag_move(uicore.uilib.y - self._last_mouse_position[1])
            self._last_mouse_position = (uicore.uilib.x, uicore.uilib.y)

    def OnMouseEnter(self, *args):
        self._update_mask()
        animations.FadeIn(self._handle, duration=0.15)

    def OnMouseExit(self, *args):
        animations.FadeOut(self._handle, duration=0.3)
