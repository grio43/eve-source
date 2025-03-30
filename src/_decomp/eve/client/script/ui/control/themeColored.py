#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\themeColored.py
from math import pi
from carbonui import const as uiconst
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
import telemetry
from carbonui.primitives.stretchspritehorizontal import StretchSpriteHorizontal
from carbonui.primitives.stretchspritevertical import StretchSpriteVertical
from carbonui.util import colorblind
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.services import uiColorThemeMixer

class ColorThemeMixin:
    default_colorType = None
    default_fixedColor = None
    default_ignoreColorBlindMode = True

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        self.fixedColor = attributes.Get('color', self.default_fixedColor)
        self.colorType = attributes.Get('colorType', self.default_colorType)
        self.ignoreColorBlindMode = attributes.get('ignoreColorBlindMode', self.default_ignoreColorBlindMode)
        self.UpdateColor()

    def OnColorThemeChanged(self):
        self.UpdateColor()

    @telemetry.ZONE_METHOD
    def UpdateColor(self):
        if self.fixedColor is not None:
            color = uiColorThemeMixer.GetUIColor(self.fixedColor, self.colorType)
            color = colorblind.CheckReplaceColor(color)
        else:
            color = sm.GetService('uiColor').GetUIColor(self.colorType)
        r, g, b = Color(*color).GetRGB()
        self.SetRGBA(r, g, b, self.opacity)

    def SetFixedColor(self, fixedColor):
        self.fixedColor = fixedColor
        self.UpdateColor()

    def SetColorType(self, colorType):
        self.colorType = colorType
        self.UpdateColor()


class SpriteThemeColored(ColorThemeMixin, Sprite):
    default_name = 'SpriteThemeColored'
    default_colorType = uiconst.COLORTYPE_UIHILIGHT

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class FrameThemeColored(ColorThemeMixin, Frame):
    default_name = 'FrameThemeColored'
    default_colorType = uiconst.COLORTYPE_UIBASE
    default_color = (1.0, 1.0, 1.0, 0.5)

    def ApplyAttributes(self, attributes):
        Frame.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class FillThemeColored(ColorThemeMixin, Fill):
    default_name = 'FillThemeColored'
    default_colorType = uiconst.COLORTYPE_UIBASE

    def ApplyAttributes(self, attributes):
        Fill.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class LineThemeColored(ColorThemeMixin, Line):
    default_name = 'LineThemeColored'
    default_colorType = uiconst.COLORTYPE_UIHILIGHT
    default_opacity = 0.5

    def ApplyAttributes(self, attributes):
        Line.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class GradientThemeColored(ColorThemeMixin, GradientSprite):
    default_rgbData = [(0, (1.0, 1.0, 1.0))]
    default_alphaData = [(0, 0.7), (0.9, 0.0)]
    default_rotation = -pi / 2
    default_colorType = uiconst.COLORTYPE_UIBASECONTRAST

    def ApplyAttributes(self, attributes):
        GradientSprite.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class LabelThemeColored(ColorThemeMixin, Label):
    default_colorType = uiconst.COLORTYPE_UIHILIGHTGLOW

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        Label.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class StretchSpriteHorizontalThemeColored(ColorThemeMixin, StretchSpriteHorizontal):
    default_colorType = uiconst.COLORTYPE_UIHILIGHT

    def ApplyAttributes(self, attributes):
        StretchSpriteHorizontal.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)


class StretchSpriteVerticalThemeColored(ColorThemeMixin, StretchSpriteVertical):
    default_colorType = uiconst.COLORTYPE_UIHILIGHT

    def ApplyAttributes(self, attributes):
        StretchSpriteVertical.ApplyAttributes(self, attributes)
        ColorThemeMixin.ApplyAttributes(self, attributes)
