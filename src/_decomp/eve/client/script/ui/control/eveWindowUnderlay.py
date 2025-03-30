#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveWindowUnderlay.py
import carbonui.const as uiconst
import trinity
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.themeColored import FrameThemeColored, FillThemeColored

class RaisedUnderlay(Container):
    default_fixedColor = None
    default_colorType = uiconst.COLORTYPE_UIHILIGHT
    default_clipChildren = True
    default_hideFrame = False
    OPACITY_DISABLED = 0.2
    OPACITY_IDLE = 0.4
    OPACITY_HOVER = 0.7
    OPACITY_SELECTED = 1.0
    OPACITY_MOUSEDOWN = 1.1

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fixedColor = attributes.Get('color', self.default_fixedColor)
        self._colorType = attributes.Get('colorType', self.default_colorType)
        self.isSelected = False
        self.isDisabled = False
        self.ConstructLayout()

    @property
    def colorType(self):
        return self._colorType

    @colorType.setter
    def colorType(self, colorType):
        if colorType == self.colorType:
            return
        self._colorType = colorType
        self._UpdateColorType()

    def ConstructLayout(self):
        self.frame = FrameThemeColored(name='frame', bgParent=self, colorType=self.colorType, color=self.fixedColor, blendMode=trinity.TR2_SBM_ADD, texturePath='res:/UI/Texture/Classes/Button/frame.png', opacity=0.2)
        self.innerGlow = FrameThemeColored(name='innerGlow', bgParent=self, cornerSize=10, texturePath='res:/UI/Texture/Classes/Button/innerGlow.png', colorType=self.colorType, color=self.fixedColor, opacity=0.2)
        self.hoverFill = FillThemeColored(name='hoverFill', bgParent=self, colorType=self.colorType, opacity=self.OPACITY_IDLE, color=self.fixedColor)
        FillThemeColored(name='backgroundColorFill', bgParent=self, opacity=0.45)

    def HideFrame(self):
        self.frame.Hide()

    def SetFixedColor(self, fixedColor):
        self.fixedColor = fixedColor
        self.frame.SetFixedColor(fixedColor)
        self.innerGlow.SetFixedColor(fixedColor)
        self.hoverFill.SetFixedColor(fixedColor)

    def OnMouseEnter(self, *args):
        self.ShowHilite()

    def OnMouseExit(self, *args):
        self.HideHilite()

    def GetColor(self):
        return self.fixedColor or sm.GetService('uiColor').GetUIColor(self.colorType)

    def ShowHilite(self, animate = True):
        if self.isSelected or self.isDisabled:
            return
        color = self.GetColor()[:3]
        if animate:
            uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, self.OPACITY_HOVER, duration=uiconst.TIME_ENTRY)
            uicore.animations.SpColorMorphTo(self.frame, endColor=color, duration=uiconst.TIME_ENTRY)
        else:
            self.hoverFill.opacity = self.OPACITY_HOVER
            color = color + (self.frame.opacity,)
            self.frame.SetRGBA(*color)

    def HideHilite(self, animate = True):
        if self.isSelected or self.isDisabled:
            return
        color = self.GetColor()[:3]
        if animate:
            uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, self.OPACITY_IDLE, duration=uiconst.TIME_EXIT)
            uicore.animations.SpColorMorphTo(self.frame, endColor=color, duration=uiconst.TIME_ENTRY)
        else:
            self.hoverFill.opacity = self.OPACITY_IDLE
            color = color + (self.frame.opacity,)
            self.frame.SetRGBA(*color)

    def OnMouseDown(self, *args):
        if self.isSelected or self.isDisabled:
            return
        uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, self.OPACITY_MOUSEDOWN, duration=0.1)

    def OnMouseUp(self, *args):
        if self.isSelected or self.isDisabled:
            return
        uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, self.OPACITY_HOVER, duration=0.3)

    def Blink(self, loops = 1):
        opacity = self.OPACITY_DISABLED if self.isDisabled else self.OPACITY_IDLE
        uicore.animations.FadeTo(self.hoverFill, self.OPACITY_MOUSEDOWN, opacity, curveType=uiconst.ANIM_WAVE, duration=0.6, loops=loops)

    def StopBlink(self):
        opacity = self.OPACITY_DISABLED if self.isDisabled else self.OPACITY_IDLE
        uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, opacity, duration=0.3)

    def Select(self, animate = True):
        if self.isSelected:
            return
        self.innerGlow.StopAnimations()
        if self.fixedColor:
            self.innerGlow.SetFixedColor(self.fixedColor)
        else:
            self.innerGlow.SetColorType(uiconst.COLORTYPE_UIHILIGHT)
        if animate:
            uicore.animations.FadeTo(self.hoverFill, self.hoverFill.opacity, self.OPACITY_SELECTED, duration=0.15)
        else:
            self.hoverFill.opacity = self.OPACITY_SELECTED
        self.isSelected = True

    def Deselect(self, animate = True):
        if not self.isSelected:
            return
        self.isSelected = False
        self.HideHilite(animate=animate)

    def SetDisabled(self):
        self.isDisabled = True
        self.hoverFill.StopAnimations()
        self.hoverFill.opacity = self.OPACITY_DISABLED

    def SetEnabled(self):
        self.isDisabled = False
        self.hoverFill.StopAnimations()
        self.hoverFill.opacity = self.OPACITY_IDLE

    def _UpdateColorType(self):
        self.frame.SetColorType(self._colorType)
        self.innerGlow.SetColorType(self._colorType)
        self.hoverFill.SetColorType(self._colorType)

    def Expand(self, *args):
        pass

    def Collapse(self):
        pass


class ListEntryUnderlay(Fill):
    COLOR = eveThemeColor.THEME_FOCUSDARK
    OPACITY_IDLE = 0.0
    OPACITY_HOVER = 0.2
    OPACITY_SELECTED = 0.4
    GLOW_BRIGHTNESS_IDLE = 0.0
    GLOW_BRIGHTNESS_HOVERED = 0.3
    default_name = 'ListEntryUnderlay'
    default_padBottom = 1

    def __init__(self, color_override = None, hovered = False, selected = False, **kwargs):
        if 'color' in kwargs:
            color_override = kwargs.pop('color')
        self._color_override = color_override
        self._hovered = hovered
        self._selected = selected
        super(ListEntryUnderlay, self).__init__(color=self._get_color(), opacity=self._get_opacity(), outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=self._get_glow_brightness(), **kwargs)

    @property
    def color_override(self):
        return self._color_override

    @color_override.setter
    def color_override(self, value):
        self.set_color_override(value)

    @property
    def hovered(self):
        return self._hovered

    @hovered.setter
    def hovered(self, value):
        self.set_hovered(value)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        self.set_selected(value)

    def set_color_override(self, value, animate = True):
        if self._color_override != value:
            self._color_override = value
            self._update_color(animate)
            self._update_opacity(animate)

    def set_hovered(self, value, animate = True):
        if self._hovered != value:
            self._hovered = value
            self._update_opacity(animate)
            self._update_glow_brightness(animate)

    def set_selected(self, value, animate = True):
        if self._selected != value:
            self._selected = value
            self._update_color(animate)
            self._update_opacity(animate)

    def select(self, animate = True):
        self.set_selected(True, animate)

    def deselect(self, animate = True):
        self.set_selected(False, animate)

    def _get_color(self):
        if self._selected:
            return self.COLOR
        elif self._color_override is not None:
            return self._color_override
        else:
            return self.COLOR

    def _update_color(self, animate = True):
        if animate:
            animations.SpColorMorphTo(self, startColor=self.color.GetRGB(), endColor=self._get_color()[:3], duration=0.3)
        else:
            self.color = self._get_color()[:3]

    def _get_opacity(self):
        if self._selected:
            return self.OPACITY_SELECTED
        elif self._color_override is not None:
            return self.OPACITY_SELECTED
        elif self._hovered:
            return self.OPACITY_HOVER
        else:
            return self.OPACITY_IDLE

    def _update_opacity(self, animate = True):
        if animate:
            animations.FadeTo(self, startVal=self.opacity, endVal=self._get_opacity(), duration=0.3)
        else:
            self.opacity = self._get_opacity()

    def _get_glow_brightness(self):
        if self._hovered:
            return self.GLOW_BRIGHTNESS_HOVERED
        else:
            return self.GLOW_BRIGHTNESS_IDLE

    def _update_glow_brightness(self, animate = True):
        if animate:
            if self._hovered:
                duration = 0.1
            else:
                duration = 0.3
            animations.MorphScalar(self, 'glowBrightness', endVal=self._get_glow_brightness(), duration=duration)
        else:
            self.glowBrightness = self._get_glow_brightness()

    def OnColorThemeChanged(self):
        self._update_color(animate=False)

    def OnMouseEnter(self, *args):
        self.hovered = True

    def OnMouseExit(self, *args):
        self.hovered = False

    def ShowHilite(self, animate = True):
        self.set_hovered(True, animate)

    def HideHilite(self, animate = True):
        self.set_hovered(False, animate)

    def Select(self, animate = True):
        self.select(animate)

    def Deselect(self, animate = True):
        self.deselect(animate)
