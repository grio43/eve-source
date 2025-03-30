#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\gauge.py
import math
from math import pi
import carbonui.const as uiconst
import uthread
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.const import TOLEFT_PROP, TOPRIGHT, TOPLEFT
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from carbonui.uiconst import OutputMode
from carbonui.uicore import uicore
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.control.themeColored import GradientThemeColored, FillThemeColored
CLOSE_ENOUGH_TOLERANCE = 1e-07

class _GaugeBase(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    default_alignMode = uiconst.TOTOP
    default_width = 100
    default_height = 30
    default_gaugeHeight = 6
    default_label = ''
    default_subText = ''
    default_gradientBrightnessFactor = 2.0
    default_gaugeAlign = TOLEFT_PROP
    default_animateInRealTime = True
    default_labelClass = EveLabelSmall
    default_textPadding = (0, 0, 0, 1)
    default_glowBrightness = 0.5

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        labelTxt = attributes.Get('label', self.default_label)
        subTxt = attributes.Get('subText', self.default_subText)
        gaugeHeight = attributes.Get('gaugeHeight', self.default_gaugeHeight)
        self.gradientBrightnessFactor = attributes.Get('gradientBrightnessFactor', self.default_gradientBrightnessFactor)
        self.gaugeAlign = attributes.Get('gaugeAlign', self.default_gaugeAlign)
        self.useRealTime = attributes.get('useRealTime', self.default_animateInRealTime)
        self.labelClass = attributes.get('labelClass', self.default_labelClass)
        self.textPadding = attributes.get('textPadding', self.default_textPadding)
        self.glowBrightness = attributes.get('glowBrightness', self.default_glowBrightness)
        self.markers = {}
        self.arrows = {}
        self.gaugeCont = Container(parent=self, name='gaugeCont', height=gaugeHeight, align=uiconst.TOTOP, clipChildren=True, state=uiconst.UI_DISABLED)
        self.label = None
        if labelTxt:
            self.SetText(labelTxt)
        self.subText = None
        if subTxt:
            self.SetSubText(subTxt)

    def _SetValue(self, gauge, value, frequency, animate, duration = 0.6, timeOffset = 0.0):
        if animate:
            if self.IsHorizontalGauge():
                attrName = 'width'
                currValue = gauge.width
            else:
                attrName = 'height'
                currValue = gauge.height
            uicore.animations.MorphScalar(gauge, attrName, currValue, value, duration=duration, curveSet=self._GetCorrectCurveSet(), timeOffset=timeOffset)
        elif self.IsHorizontalGauge():
            gauge.width = value
        else:
            gauge.height = value
        self.value = value

    def _GetCorrectCurveSet(self):
        simTimeCurveSet = uicore.animations.CreateCurveSet(useRealTime=self.useRealTime)
        simTimeCurveSet.name = 'gaugeCurveSet'
        return simTimeCurveSet

    def ShowMarker(self, value, width = 1, color = Color.WHITE, **kwargs):
        self.HideMarker(value)
        marker = self._CreateMarker(color, value, width, **kwargs)
        self.markers[value] = marker

    def _CreateMarker(self, color, value, width, **kwargs):
        marker = Fill(parent=self.gaugeCont, name='marker', color=color, align=uiconst.TOPLEFT_PROP, pos=(value,
         0,
         width,
         self.gaugeCont.height), state=uiconst.UI_DISABLED, idx=0)
        return marker

    def ShowArrow(self, value):
        self.HideArrow(value)
        arrow = Sprite(parent=self, name='arrow', align=uiconst.TOPLEFT_PROP, pos=(value,
         self.gaugeCont.height + 16,
         6,
         6), state=uiconst.UI_DISABLED, idx=0, texturePath='res:/UI/Texture/Shared/arrows/arrowRight.png', rotation=math.pi / 2)
        self.arrows[value] = arrow

    def ShowMarkers(self, values, width = 1, color = Color.WHITE):
        for value in values:
            self.ShowMarker(value, width, color)

    def HideMarker(self, value):
        if value in self.markers:
            self.markers[value].Close()
            self.markers.pop(value)

    def HideArrow(self, value):
        if value in self.arrows:
            self.arrows[value].Close()
            self.arrows.pop(value)

    def HideAllArrows(self):
        for arrow in self.arrows.values():
            arrow.Close()

        self.arrows.clear()

    def HideAllMarkers(self):
        for marker in self.markers.values():
            marker.Close()

        self.markers.clear()

    def SetSubText(self, text):
        if not self.subText:
            self.subText = EveLabelSmall(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1, padTop=1)
        self.subText.text = text

    def SetText(self, text):
        if not self.label:
            self.label = self.labelClass(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, maxLines=1, padding=self.textPadding, idx=0)
        self.label.text = text

    def _CreateGradient(self, parent, color):
        if len(color) == 3:
            color = color + (1.0,)
        return GradientSprite(align=uiconst.TOALL, parent=parent, rotation=-pi / 2, rgbData=[(0.0, color[:3])], alphaData=[(0, color[-1])], outputMode=OutputMode.COLOR_AND_GLOW, glowBrightness=self.glowBrightness)

    def IsHorizontalGauge(self):
        return self.gaugeAlign in (uiconst.TOLEFT_PROP, uiconst.TORIGHT_PROP)


class Gauge(_GaugeBase):
    __guid__ = 'uicls.Gauge'
    default_name = 'Gauge'
    default_value = 0.0
    default_backgroundColor = None
    default_cyclic = False
    default_color = Color.WHITE

    def ApplyAttributes(self, attributes):
        _GaugeBase.ApplyAttributes(self, attributes)
        self.color = attributes.Get('color', self.default_color)
        backgroundColor = attributes.Get('backgroundColor', self.default_backgroundColor)
        self.value = attributes.Get('value', self.default_value)
        self.cyclic = attributes.Get('cyclic', self.default_cyclic)
        self.gauge = Container(parent=self.gaugeCont, name='gauge', align=self.gaugeAlign, clipChildren=True, width=0.0, state=uiconst.UI_DISABLED)
        self.gaugeGradient = self._CreateGradient(parent=self.gauge, color=self.color)
        self.flashGradient = None
        if backgroundColor is None:
            backgroundColor = Color(*self.color).SetAlpha(0.2).SetSaturation(0.2).GetRGBA()
        self._CreateBackgroundFill(backgroundColor)
        self.SetValueInstantly(self.value)

    def _CreateBackgroundFill(self, backgroundColor):
        self.sr.backgroundFill = Fill(bgParent=self.gaugeCont, name='background', color=backgroundColor)

    def SetGaugeAlign(self, align):
        self.gauge.align = align

    def HasValue(self, value):
        return FloatCloseEnough(self.value, value, CLOSE_ENOUGH_TOLERANCE)

    def SetValue(self, value, frequency = 10.0, animate = True, timeOffset = 0.0, duration = 0.6, flash = True):
        if self.HasValue(value):
            return
        if self.cyclic and self.value > value:
            self.SetValueInstantly(value)
        else:
            if animate and flash:
                self.AnimFlash(value - self.value, timeOffset=timeOffset)
            self._SetValue(self.gauge, value, frequency, animate, duration, timeOffset)

    def SetValueTimed(self, value, duration, callback = None):
        if self.IsHorizontalGauge():
            attrName = 'width'
            self.value = self.gauge.width
        else:
            attrName = 'height'
            self.value = self.gauge.height
        uicore.animations.MorphScalar(self.gauge, attrName, self.value, value, duration=duration, curveType=uiconst.ANIM_LINEAR, callback=callback, curveSet=self._GetCorrectCurveSet())

    def SetValueText(self, text):
        if getattr(self, 'valueText', None) is None:
            self.valueText = EveLabelSmall(parent=self.gaugeCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, idx=0)
        if self.valueText.text != text:
            self.valueText.text = text

    def SetColor(self, color, animDuration = None):
        if color == self.color:
            return
        self.color = color
        if self.gaugeGradient:
            if animDuration:
                uicore.animations.FadeOut(self.gaugeGradient, duration=animDuration, callback=self.gaugeGradient.Close)
            else:
                self.gaugeGradient.Close()
        self.gaugeGradient = self._CreateGradient(self.gauge, color)
        if animDuration:
            uicore.animations.FadeTo(self.gaugeGradient, 0.0, self.gaugeGradient.opacity, duration=animDuration)

    def SetBackgroundColor(self, color):
        adjustedColor = Color(*color).SetAlpha(0.2).GetRGBA()
        self.sr.backgroundFill.color = adjustedColor

    def SetLabelColor(self, color):
        if self.label is not None:
            self.label.color = color

    def SetValueInstantly(self, value):
        self.value = value
        if self.IsHorizontalGauge():
            self.gauge.width = value
        else:
            self.gauge.height = value
        self.gauge.StopAnimations()

    def AnimFlash(self, diff, duration = 1.6, timeOffset = 0.0):
        uthread.new(self._AnimFlash, diff, duration, timeOffset)

    def _AnimFlash(self, diff, duration, timeOffset):
        w, h = self.gaugeCont.GetAbsoluteSize()
        align = TOPLEFT if self.gauge.align == TOLEFT_PROP else TOPRIGHT
        if not self.flashGradient:
            self._CreateFlashGradient(align, h, w)
        self.flashGradient.opacity = 1.0
        if self.IsHorizontalGauge():
            if diff > 0:
                self.flashGradient.rotation = 0
                uicore.animations.MorphScalar(self.flashGradient, 'left', -w, w, duration - 0.4, timeOffset=timeOffset)
            else:
                self.flashGradient.rotation = pi
                uicore.animations.MorphScalar(self.flashGradient, 'left', w, -w, duration - 0.4, timeOffset=timeOffset)
        elif diff > 0:
            self.flashGradient.rotation = -pi / 2
            uicore.animations.MorphScalar(self.flashGradient, 'top', -h, h, duration - 0.4, timeOffset=timeOffset)
        else:
            self.flashGradient.rotation = pi / 2.0
            uicore.animations.MorphScalar(self.flashGradient, 'top', h, -h, duration - 0.4, timeOffset=timeOffset)
        uicore.animations.FadeOut(self.flashGradient, duration=duration, timeOffset=timeOffset)

    def _CreateFlashGradient(self, align, h, w):
        self.flashGradient = GradientSprite(parent=self.gauge, idx=0, name='flashGradient', align=align, width=w, height=h, rgbData=[(0, (1.0, 1.0, 1.0))], alphaData=[(0, 0.0), (0.9, 0.5), (1.0, 0.0)])

    def HideBackground(self):
        self.sr.backgroundFill.Hide()


class GaugeThemeColored(Gauge):

    def _CreateGradient(self, parent, color):
        GradientThemeColored(align=uiconst.TOALL, colorType=uiconst.COLORTYPE_UIHILIGHT, parent=parent, rotation=-pi / 2, alphaData=[(0.0, 1.0)], rgbData=[(0, (1.0, 1.0, 1.0))])

    def _CreateBackgroundFill(self, *args):
        self.sr.backgroundFill = FillThemeColored(bgParent=self.gaugeCont, colorType=uiconst.COLORTYPE_UIHILIGHT)

    def _CreateFlashGradient(self, align, h, w):
        self.flashGradient = GradientThemeColored(parent=self.gauge, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, idx=0, name='flashGradient', align=align, width=w, height=h, rgbData=[(0, (1.0, 1.0, 1.0))], alphaData=[(0, 0.0), (0.9, 0.5), (1.0, 0.0)])


class GaugeMultiValue(_GaugeBase):
    default_name = 'GaugeMultiValue'
    default_backgroundColor = (1.0, 1.0, 1.0, 0.2)
    default_colors = []

    def ApplyAttributes(self, attributes):
        _GaugeBase.ApplyAttributes(self, attributes)
        colors = attributes.Get('colors', self.default_colors)
        values = attributes.Get('values', [])
        backgroundColor = attributes.Get('backgroundColor', self.default_backgroundColor)
        self.gauges = []
        self.gradients = []
        self.ConstructColorGradients(colors)
        Fill(bgParent=self.gaugeCont, name='background', color=backgroundColor)
        self.UpdateValues(values)

    def UpdateValues(self, values):
        for gaugeNum, value in enumerate(values):
            self.SetValueInstantly(gaugeNum, value)

    def ConstructColorGradients(self, colors):
        numGauges = len(colors)
        for gaugeNum in xrange(numGauges):
            layer = Container(parent=self.gaugeCont, name='layer')
            gauge = Container(parent=layer, name='gaugeCont%s' % gaugeNum, align=uiconst.TOLEFT_PROP)
            self.gradients.append(self._CreateGradient(gauge, color=colors[gaugeNum]))
            self.gauges.append(gauge)

    def SetValue(self, gaugeNum, value, frequency = 10.0, animate = True):
        self._SetValue(self.gauges[gaugeNum], value, frequency, animate)

    def SetValueInstantly(self, gaugeNum, value):
        self.gauges[gaugeNum].width = value
