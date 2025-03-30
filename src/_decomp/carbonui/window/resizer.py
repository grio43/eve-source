#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\window\resizer.py
import math
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.stretchspritevertical import StretchSpriteVertical
from carbonui.uianimations import animations
from eve.client.script.ui import eveThemeColor

class Side(object):
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    _ALL = (LEFT,
     TOP,
     RIGHT,
     BOTTOM)

    @classmethod
    def iter(cls):
        return iter(cls._ALL)


class Resizer(Container):
    DEFAULT_INNER_PADDING = (0, 0, 0, 0)

    def __init__(self, inner_padding = None, locked_sides = None, on_end_scale = None, on_start_scale = None, **kwargs):
        self._inner_padding = sanitize_padding(inner_padding, default=self.DEFAULT_INNER_PADDING)
        self._handles = []
        self._locked_sides = set(locked_sides or ())
        self._on_end_scale = on_end_scale
        self._on_start_scale = on_start_scale
        super(Resizer, self).__init__(**kwargs)
        self._create_handles()

    @property
    def inner_padding(self):
        return self._inner_padding

    @inner_padding.setter
    def inner_padding(self, value):
        value = sanitize_padding(value, default=self.DEFAULT_INNER_PADDING)
        if self._inner_padding != value:
            self._inner_padding = value
            self._update_inner_padding()

    @property
    def locked_sides(self):
        return frozenset(self._locked_sides)

    @locked_sides.setter
    def locked_sides(self, value):
        new_locked_sides = set(value)
        if self._locked_sides != new_locked_sides:
            self._locked_sides = new_locked_sides
            self._update_handle_locked_state()

    def _create_handles(self):
        for orientation in Orientation.iter():
            handle = ResizeHandle(parent=self, orientation=orientation, on_start_scale=lambda _handle: self._on_start_scale(Orientation.get_sides(_handle.orientation)), on_end_scale=lambda _handle: self._on_end_scale(Orientation.get_sides(_handle.orientation)), enabled=not self._is_orientation_locked(orientation), idx=0 if Orientation.is_corner(orientation) else -1)
            self._handles.append(handle)

    def _update_inner_padding(self):
        for handle in self._handles:
            handle.inner_padding = self._inner_padding

    def _update_handle_locked_state(self):
        for handle in self._handles:
            handle.enabled = not self._is_orientation_locked(handle.orientation)

    def _is_orientation_locked(self, orientation):
        return any((side in self._locked_sides for side in Orientation.get_sides(orientation)))


def sanitize_padding(value, default):
    if not value:
        value = default
    if isinstance(value, int):
        value = (value,) * 4
    return value


class Orientation(object):
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    TOP_LEFT = 5
    TOP_RIGHT = 6
    BOTTOM_RIGHT = 7
    BOTTOM_LEFT = 8
    _ALL = (LEFT,
     TOP,
     RIGHT,
     BOTTOM,
     TOP_LEFT,
     TOP_RIGHT,
     BOTTOM_RIGHT,
     BOTTOM_LEFT)
    _HORIZONTAL_ORIENTATIONS = {LEFT,
     RIGHT,
     TOP_LEFT,
     TOP_RIGHT,
     BOTTOM_LEFT,
     BOTTOM_RIGHT}
    _VERTICAL_ORIENTATIONS = {TOP,
     BOTTOM,
     TOP_LEFT,
     TOP_RIGHT,
     BOTTOM_LEFT,
     BOTTOM_RIGHT}
    _CORNER_ORIENTATIONS = {TOP_LEFT,
     TOP_RIGHT,
     BOTTOM_LEFT,
     BOTTOM_RIGHT}
    _SIDES_BY_ORIENTATION = {LEFT: (Side.LEFT,),
     TOP: (Side.TOP,),
     RIGHT: (Side.RIGHT,),
     BOTTOM: (Side.BOTTOM,),
     TOP_LEFT: (Side.TOP, Side.LEFT),
     TOP_RIGHT: (Side.TOP, Side.RIGHT),
     BOTTOM_RIGHT: (Side.BOTTOM, Side.RIGHT),
     BOTTOM_LEFT: (Side.BOTTOM, Side.LEFT)}

    @classmethod
    def iter(cls):
        return iter(cls._ALL)

    @classmethod
    def get_sides(cls, orientation):
        return cls._SIDES_BY_ORIENTATION[orientation]

    @classmethod
    def is_corner(cls, orientation):
        return orientation in cls._CORNER_ORIENTATIONS

    @classmethod
    def is_horizontal(cls, orientation):
        return orientation in cls._HORIZONTAL_ORIENTATIONS

    @classmethod
    def is_vertical(cls, orientation):
        return orientation in cls._VERTICAL_ORIENTATIONS


class ResizeHandle(Container):
    ALIGN_BY_ORIENTATION = {Orientation.LEFT: uiconst.TOLEFT_NOPUSH,
     Orientation.TOP: uiconst.TOTOP_NOPUSH,
     Orientation.RIGHT: uiconst.TORIGHT_NOPUSH,
     Orientation.BOTTOM: uiconst.TOBOTTOM_NOPUSH,
     Orientation.TOP_LEFT: uiconst.TOPLEFT,
     Orientation.TOP_RIGHT: uiconst.TOPRIGHT,
     Orientation.BOTTOM_RIGHT: uiconst.BOTTOMRIGHT,
     Orientation.BOTTOM_LEFT: uiconst.BOTTOMLEFT}
    CURSOR_BY_ORIENTATION = {Orientation.LEFT: uiconst.UICURSOR_LEFT_RIGHT_DRAG,
     Orientation.TOP: uiconst.UICURSOR_TOP_BOTTOM_DRAG,
     Orientation.RIGHT: uiconst.UICURSOR_LEFT_RIGHT_DRAG,
     Orientation.BOTTOM: uiconst.UICURSOR_TOP_BOTTOM_DRAG,
     Orientation.TOP_LEFT: uiconst.UICURSOR_TOP_LEFT_BOTTOM_RIGHT_DRAG,
     Orientation.TOP_RIGHT: uiconst.UICURSOR_TOP_RIGHT_BOTTOM_LEFT_DRAG,
     Orientation.BOTTOM_RIGHT: uiconst.UICURSOR_TOP_LEFT_BOTTOM_RIGHT_DRAG,
     Orientation.BOTTOM_LEFT: uiconst.UICURSOR_TOP_RIGHT_BOTTOM_LEFT_DRAG}
    SIZE_BY_ORIENTATION = {Orientation.LEFT: (8, 0),
     Orientation.TOP: (0, 8),
     Orientation.RIGHT: (8, 0),
     Orientation.BOTTOM: (0, 8),
     Orientation.TOP_LEFT: (8, 8),
     Orientation.TOP_RIGHT: (8, 8),
     Orientation.BOTTOM_RIGHT: (8, 8),
     Orientation.BOTTOM_LEFT: (8, 8)}
    HANDLE_ALIGN_BY_ORIENTATION = {Orientation.LEFT: uiconst.CENTERLEFT,
     Orientation.TOP: uiconst.CENTERTOP,
     Orientation.RIGHT: uiconst.CENTERRIGHT,
     Orientation.BOTTOM: uiconst.CENTERBOTTOM,
     Orientation.TOP_LEFT: uiconst.TOPLEFT,
     Orientation.TOP_RIGHT: uiconst.TOPRIGHT,
     Orientation.BOTTOM_RIGHT: uiconst.BOTTOMRIGHT,
     Orientation.BOTTOM_LEFT: uiconst.BOTTOMLEFT}
    TEXTURE_ROTATION_BY_ORIENTATION = {Orientation.LEFT: 0.0,
     Orientation.TOP: 0.0,
     Orientation.RIGHT: math.pi,
     Orientation.BOTTOM: math.pi,
     Orientation.TOP_LEFT: 0.0,
     Orientation.TOP_RIGHT: -math.pi / 2.0,
     Orientation.BOTTOM_RIGHT: -math.pi,
     Orientation.BOTTOM_LEFT: math.pi / 2.0}
    OPACITY_IDLE = 0.0
    OPACITY_HOVER = 0.5
    OPACITY_SCALING = 1.0
    DEFAULT_INNER_PADDING = (0, 0, 0, 0)
    _handle = None
    _handle_wrap = None
    _hovered = False
    _scaling = False

    def __init__(self, orientation, on_start_scale = None, on_end_scale = None, enabled = True, inner_padding = None, **kwargs):
        self._orientation = orientation
        self._on_start_scale = on_start_scale
        self._on_end_scale = on_end_scale
        self._enabled = enabled
        self._inner_padding = sanitize_padding(inner_padding, default=self.DEFAULT_INNER_PADDING)
        width, height = self._get_size(orientation=self._orientation, inner_padding=self._inner_padding)
        super(ResizeHandle, self).__init__(align=self.ALIGN_BY_ORIENTATION[orientation], cursor=self.CURSOR_BY_ORIENTATION[orientation], state=self._get_state(), width=width, height=height, opacity=self._get_opacity(), **kwargs)
        align = self.HANDLE_ALIGN_BY_ORIENTATION[orientation]
        rotation = self.TEXTURE_ROTATION_BY_ORIENTATION[orientation]
        self._handle_wrap = Container(parent=self, align=uiconst.TOALL, clipChildren=True, padding=self._get_handle_wrap_padding())
        if orientation in {Orientation.LEFT, Orientation.RIGHT}:
            self._handle = StretchSpriteVertical(parent=self._handle_wrap, align=align, width=2, height=64, topEdgeSize=2, bottomEdgeSize=2, texturePath='res:/UI/Texture/classes/Window/resize_handle_edge_vertical.png', rotation=rotation, color=self._get_color(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)
        elif orientation in {Orientation.TOP, Orientation.BOTTOM}:
            self._handle = StretchSpriteHorizontal(parent=self._handle_wrap, align=align, width=64, height=2, leftEdgeSize=2, rightEdgeSize=2, texturePath='res:/UI/Texture/classes/Window/resize_handle_edge_horizontal.png', rotation=rotation, color=self._get_color(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)
        else:
            self._handle = Sprite(parent=self._handle_wrap, align=align, width=8, height=8, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Window/resize_handle_corner.png', rotation=rotation, color=self._get_color(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.5)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            self._update_state()

    @property
    def inner_padding(self):
        return self._inner_padding

    @inner_padding.setter
    def inner_padding(self, value):
        value = sanitize_padding(value, default=self.DEFAULT_INNER_PADDING)
        if self._inner_padding != value:
            self._inner_padding = value
            self._update_size()
            self._update_handle_wrap_padding()

    @property
    def orientation(self):
        return self._orientation

    def _get_state(self):
        if self._enabled:
            return uiconst.UI_NORMAL
        return uiconst.UI_DISABLED

    def _update_state(self):
        self.state = self._get_state()
        if not self._enabled:
            self._end_scaling()

    @classmethod
    def _get_size(cls, orientation, inner_padding):
        width, height = cls.SIZE_BY_ORIENTATION[orientation]
        pad_left, pad_top, pad_right, pad_bottom = inner_padding
        width += pad_left + pad_right
        height += pad_top + pad_bottom
        return (width, height)

    def _update_size(self):
        self.width, self.height = self._get_size(orientation=self._orientation, inner_padding=self._inner_padding)

    def _get_handle_wrap_padding(self):
        return self._inner_padding

    def _update_handle_wrap_padding(self):
        if self._handle_wrap:
            self._handle_wrap.padding = self._get_handle_wrap_padding()

    def _get_opacity(self):
        if not self._enabled:
            return self.OPACITY_IDLE
        elif self._scaling:
            return self.OPACITY_SCALING
        elif self._hovered:
            return self.OPACITY_HOVER
        else:
            return self.OPACITY_IDLE

    def _update_opacity(self):
        duration = 0.15 if self._hovered else 0.3
        animations.FadeTo(self, startVal=self.opacity, endVal=self._get_opacity(), duration=duration)

    def _start_scaling(self):
        if not self._scaling and self._enabled:
            self._scaling = True
            self._update_opacity()
            if self._on_start_scale:
                self._on_start_scale(self)

    def _end_scaling(self):
        if self._scaling:
            self._scaling = False
            self._update_opacity()
            if self._on_end_scale:
                self._on_end_scale(self)

    @staticmethod
    def _get_color():
        return eveThemeColor.THEME_ACCENT

    def OnColorThemeChanged(self):
        if self._handle is not None:
            self._handle.color = self._get_color()

    def OnMouseEnter(self, *args):
        self._hovered = True
        self._update_opacity()

    def OnMouseExit(self, *args):
        self._hovered = False
        self._update_opacity()

    def OnMouseDown(self, button, *args):
        if button == uiconst.MOUSELEFT and self._enabled:
            self._start_scaling()

    def OnMouseUp(self, button, *args):
        if button == uiconst.MOUSELEFT:
            self._end_scaling()
