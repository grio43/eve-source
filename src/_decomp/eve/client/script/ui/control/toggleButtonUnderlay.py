#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\toggleButtonUnderlay.py
from carbonui import Density, uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.uianimations import animations
from chroma import Color
from eve.client.script.ui import eveColor, eveThemeColor

class FrameType(object):
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3


FRAME_TEXTURE_BY_DENSITY_AND_TYPE = {Density.NORMAL: {FrameType.LEFT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_left_32px.png',
                  FrameType.MIDDLE: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_32px.png',
                  FrameType.RIGHT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_right_32px.png'},
 Density.COMPACT: {FrameType.LEFT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_left_24px.png',
                   FrameType.MIDDLE: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_24px.png',
                   FrameType.RIGHT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_right_24px.png'},
 Density.EXPANDED: {FrameType.LEFT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_left_40px.png',
                    FrameType.MIDDLE: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_40px.png',
                    FrameType.RIGHT: 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_right_40px.png'}}

class ToggleButtonUnderlay(Container):
    default_name = 'ToggleButtonUnderlay'
    _background = None
    _hovered = False
    _pressed = False

    def __init__(self, density = Density.NORMAL, enabled = True, frame_type = FrameType.MIDDLE, selected = False, selected_color_override = None, **kwargs):
        self._density = density
        self._enabled = enabled
        self._frame_type = frame_type
        self._selected = selected
        self._selected_color_override = selected_color_override
        super(ToggleButtonUnderlay, self).__init__(**kwargs)
        self._layout()

    def _layout(self):
        self._background = StretchSpriteHorizontal(bgParent=self, leftEdgeSize=self.get_edge_size(), rightEdgeSize=self.get_edge_size(), texturePath=self._get_texture_path(), color=self._get_color(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self._get_glow_brightness())

    def get_edge_size(self):
        return 9

    @property
    def density(self):
        return self._density

    @density.setter
    def density(self, value):
        if self._density != value:
            self._density = value
            self._update_texture_path()

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        if self._enabled != value:
            self._enabled = value
            self._update_color(duration=uiconst.TIME_EXIT)

    @property
    def frame_type(self):
        return self._frame_type

    @frame_type.setter
    def frame_type(self, value):
        if self._frame_type != value:
            self._frame_type = value
            self._update_texture_path()

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        if self._hovered != value:
            self._hovered = value
            duration = uiconst.TIME_ENTRY if value else uiconst.TIME_EXIT
            self._update_color(duration)
            self._update_glow_brightness(duration)

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        if self._pressed != value:
            self._pressed = value
            duration = uiconst.TIME_MOUSEDOWN if value else uiconst.TIME_MOUSEUP
            self._update_color(duration)
            self._update_glow_brightness(duration)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self.set_selected(value)

    def set_selected(self, value, animate = True):
        if self._selected != value:
            self._selected = value
            if animate:
                duration = uiconst.TIME_SELECT
            else:
                duration = 0.0
            self._update_color(duration)
            self._update_glow_brightness(duration)

    def _get_color(self):
        if not self.enabled:
            return (1.0, 1.0, 1.0, 0.05)
        if self.selected:
            if self._selected_color_override is not None:
                return self._selected_color_override
            else:
                return Color.from_any(eveThemeColor.THEME_FOCUSDARK).with_alpha(0.6)
        else:
            if self.pressed:
                return eveColor.TUNGSTEN_GREY
            if self.hovered:
                if self._selected_color_override is not None:
                    color = Color.from_any(self._selected_color_override)
                    return color.with_alpha(color.alpha * 0.6)
                else:
                    return (1.0, 1.0, 1.0, 0.3)
            else:
                if self._selected_color_override is not None:
                    color = Color.from_any(self._selected_color_override)
                    return color.with_alpha(color.alpha * 0.3)
                return (1.0, 1.0, 1.0, 0.1)

    def _update_color(self, duration = 0.0):
        if self._background:
            if duration > 0.0:
                animations.SpColorMorphTo(self._background, endColor=self._get_color(), duration=duration)
            else:
                animations.StopAnimation(self._background, 'color')
                self._background.SetRGBA(*self._get_color())

    def _get_glow_brightness(self):
        if self.enabled and (self.pressed or self.hovered) and not self.selected:
            return 0.3
        else:
            return 0.0

    def _update_glow_brightness(self, duration = 0.0):
        if self._background:
            if duration > 0.0:
                animations.MorphScalar(self._background, 'glowBrightness', startVal=self._background.glowBrightness, endVal=self._get_glow_brightness(), duration=duration)
            else:
                animations.StopAnimation(self._background, 'glowBrightness')
                self._background.glowBrightness = self._get_glow_brightness()

    def _get_texture_path(self):
        return FRAME_TEXTURE_BY_DENSITY_AND_TYPE[self._density][self._frame_type]

    def _update_texture_path(self):
        if self._background:
            self._background.texturePath = self._get_texture_path()

    def OnColorThemeChanged(self):
        self._update_color()
