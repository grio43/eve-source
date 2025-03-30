#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\decorative\selectionIndicatorLine.py
import trinity
from carbonui import uiconst
from carbonui.primitives.line import Line
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.util.color import Color
from carbonui.util.various_unsorted import GetWindowAbove, IsUnderActiveWindow
from eve.client.script.ui import eveThemeColor
GLOW_BRIGHTNESS_ACTIVE = 0.75
GLOW_BRIGHTNESS_INACTIVE = 0.1
COLOR_INACTIVE = Color.HextoRGBA('#B0B0B0')
OPACITY_INACTIVE = 0.0

class SelectionIndicatorLine(Line):
    default_color = eveThemeColor.THEME_ACCENT
    default_opacity = 0.0
    default_weight = 1
    default_glowBrightness = GLOW_BRIGHTNESS_INACTIVE
    default_fixedColor = None
    default_outputMode = trinity.Tr2SpriteTarget.COLOR_AND_GLOW
    _active = False

    def __init__(self, selected = False, opacity_active = 1.0, **kwargs):
        self._active_color = kwargs.pop('color', None) or self.default_color
        self._selected = selected
        self._opacity_active = opacity_active
        super(SelectionIndicatorLine, self).__init__(opacity=self._get_opacity(), **kwargs)
        self._active = IsUnderActiveWindow(self)
        self._update_glow_brightness(animate=False)
        self._update_color(animate=False)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if self._selected != value:
            self._selected = value
            self._update_opacity()

    def Select(self):
        self.selected = True

    def Deselect(self):
        self.selected = False

    def _get_opacity(self):
        if self.selected:
            return self._opacity_active
        else:
            return OPACITY_INACTIVE

    def _update_opacity(self, animate = True):
        if animate:
            duration = uiconst.TIME_ENTRY if self.selected else uiconst.TIME_EXIT
            animations.FadeTo(self, startVal=self.opacity, endVal=self._get_opacity(), duration=duration)
        else:
            self.opacity = self._get_opacity()

    def SetActiveColor(self, color):
        self._active_color = color
        self._update_color(animate=False)

    def OnColorThemeChanged(self):
        super(SelectionIndicatorLine, self).OnColorThemeChanged()
        self._update_color()

    def OnWindowAboveSetActive(self):
        super(SelectionIndicatorLine, self).OnWindowAboveSetActive()
        self._active = True
        self._update_glow_brightness()
        self._update_color()

    def OnWindowAboveSetInactive(self):
        super(SelectionIndicatorLine, self).OnWindowAboveSetInactive()
        self._active = False
        self._update_glow_brightness()
        self._update_color()

    def _get_glow_brightness(self):
        if self._active:
            return GLOW_BRIGHTNESS_ACTIVE
        else:
            return GLOW_BRIGHTNESS_INACTIVE

    def _update_glow_brightness(self, animate = True):
        if animate:
            animations.MorphScalar(self, 'glowBrightness', startVal=self.glowBrightness, endVal=self._get_glow_brightness(), duration=uiconst.TIME_ENTRY if self._active else uiconst.TIME_EXIT)
        else:
            self.glowBrightness = self._get_glow_brightness()

    def _get_color(self):
        if self._active:
            return self._active_color[:3]
        else:
            return COLOR_INACTIVE[:3]

    def _update_color(self, animate = True):
        if animate:
            animations.SpColorMorphTo(self, endColor=self._get_color(), duration=uiconst.TIME_ENTRY if self._active else uiconst.TIME_EXIT)
        else:
            self.color = self._get_color()
