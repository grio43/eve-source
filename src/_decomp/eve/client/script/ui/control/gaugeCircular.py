#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\gaugeCircular.py
import math
import carbonui.const as uiconst
from carbon.common.script.util.mathCommon import FloatCloseEnough
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from math import pi, cos, sin, atan2
from carbonui.uianimations import animations
from carbonui.util.color import Color
import geo2
import uthread
import blue
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.donutSegment import DonutSegment

class GaugeCircular(Container):
    default_name = 'GaugeCircular'
    default_radius = 20
    default_lineWidth = 3.0
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_colorStart = (1.0, 1.0, 1.0, 1.0)
    default_colorEnd = (0.8, 0.8, 0.8, 1.0)
    default_colorBg = None
    default_colorMarker = None
    default_startAngle = -pi / 2
    default_value = 0.0
    default_callback = None
    default_hoverMarkerEnabled = False
    default_clockwise = True
    default_bgPortion = 1.0
    default_showMarker = True
    default_autoUpdate = True
    default_moveMarker = False
    default_animateInRealTime = True
    default_angle = 2 * pi
    default_glow = False
    default_useMiddleGauge = False

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.radius = attributes.Get('radius', self.default_radius)
        self.lineWidth = attributes.Get('lineWidth', self.default_lineWidth)
        self.startAngle = attributes.Get('startAngle', self.default_startAngle)
        self.value = attributes.Get('value', self.default_value)
        self.colorStart = attributes.Get('colorStart', self.default_colorStart)
        self.colorEnd = attributes.Get('colorEnd', self.default_colorEnd)
        self.colorBg = attributes.Get('colorBg', self.default_colorBg)
        colorMarker = attributes.Get('colorMarker', self.default_colorMarker)
        self.callback = attributes.Get('callback', self.default_callback)
        self.isHoverMarkerEnabled = attributes.Get('hoverMarkerEnabled', self.default_hoverMarkerEnabled)
        self.isClockwise = attributes.Get('clockwise', self.default_clockwise)
        self.bgPortion = attributes.Get('bgPortion', self.default_bgPortion)
        self.showMarker = attributes.get('showMarker', self.default_showMarker)
        self.autoUpdate = attributes.get('autoUpdate', self.default_autoUpdate)
        self.moveMarker = attributes.get('moveMarker', self.default_moveMarker)
        self.useRealTime = attributes.get('useRealTime', self.default_animateInRealTime)
        self.angle = attributes.get('angle', self.default_angle)
        self.glow = attributes.get('glow', self.default_glow)
        self.glowBrightness = attributes.get('glowBrightness', 0)
        self.useMiddleGauge = attributes.get('useMiddleGauge', self.default_useMiddleGauge)
        if colorMarker is None:
            colorMarker = self.colorStart
        self.width = self.height = self.radius * 2
        self.pickRadius = self.radius + self.lineWidth
        self._angle = 0.0
        hoverMarkerSize = self.lineWidth * 1.7
        self.hoverMarker = Sprite(name='hoverMarker', parent=self, color=colorMarker, width=hoverMarkerSize, height=hoverMarkerSize, state=uiconst.UI_DISABLED, opacity=0.0, texturePath='res:/UI/Texture/Classes/Gauge/circle.png')
        if self.isClockwise:
            rotation = -self.startAngle - pi / 2
        else:
            rotation = self.startAngle + pi / 2
        state = uiconst.UI_DISABLED if self.showMarker else uiconst.UI_HIDDEN
        self.markerTransform = Transform(name='markerTransform', parent=self, align=uiconst.TOALL, rotationCenter=(0.5, 0.5), rotation=rotation, state=state)
        height = self.lineWidth + 5
        self.marker = Fill(name='marker', parent=self.markerTransform, color=colorMarker, align=uiconst.CENTERTOP, pos=(0,
         -(height - self.lineWidth),
         2,
         height))
        self.gauge = None
        self.middleGauge = None
        self.bgGauge = None
        self.Reconstruct()
        if self.autoUpdate:
            uthread.new(self.UpdateThread)

    def UpdateThread(self):
        while not self.destroyed:
            diff = self.gauge.end - self.value
            diff = 3.0 * diff / blue.os.fps
            self.gauge.end -= diff
            blue.synchro.Yield()

    def Reconstruct(self):
        self._ConstructGauge()
        if self.useMiddleGauge:
            self._ConstructMiddleGauge()
        self._ConstructBGGauge()

    def _ConstructBGGauge(self):
        if self.colorBg is None:
            self.colorBg = Color(*self.colorStart).SetBrightness(0.2).GetRGBA()
        if self.bgGauge:
            self.bgGauge.Close()
        self.bgGauge = self.ConstructLine(self.colorBg, self.colorBg)
        self.bgGauge.end = self.bgPortion
        self.bgGauge.name = 'backgroundLine'

    def _ConstructMiddleGauge(self):
        if self.middleGauge:
            self.middleGauge.Close()
        self.middleGauge = self.ConstructLine(eveColor.LEAFY_GREEN, eveColor.LEAFY_GREEN)
        self.middleGauge.end = self.value
        self.middleGauge.name = 'middleLine'

    def _ConstructGauge(self):
        if self.gauge:
            self.gauge.Close()
        self.gauge = self.ConstructLine(self.colorStart, self.colorEnd)
        self.gauge.end = self.value
        self.gauge.name = 'gaugeLine'
        if self.glow:
            self.gauge.outputMode = uiconst.OUTPUT_COLOR_AND_GLOW
            self.gauge.glowBrightness = self.glowBrightness

    def ConstructLine(self, colorStart, colorEnd):
        return DonutSegment(parent=self, colorEnd=colorEnd, colorStart=colorStart, lineWidth=self.lineWidth, startAngle=self.startAngle, radius=self.radius, isClockwise=self.isClockwise, angle=self.angle)

    def SetValue(self, value, animate = True):
        if FloatCloseEnough(value, self.value):
            return
        if not animate:
            self.gauge.end = value
        self.value = value
        if animate:
            glow = self.glowBrightness
            animations.MorphScalar(self.gauge, 'glowBrightness', glow, 4 * glow, curveType=uiconst.ANIM_WAVE, duration=1.0)

    def SetMarkerValue(self, value):
        self.markerTransform.rotation = self.GetOffsetMarkerValue(value)

    def SetValueAndMarker(self, value, animated = True):
        self.SetValue(value, animated)
        self.SetMarkerValue(value)

    def SetValueAndMarkerTimed(self, value, duration):
        self.SetMarkerValueTimed(value, duration)
        self.SetValueTimed(value, duration)

    def SetValueTimed(self, value, duration, timeOffset = 0.0):
        uicore.animations.MorphScalar(self.gauge, 'end', self.gauge.end, value, duration=duration, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet(), timeOffset=timeOffset)
        self.value = value

    def SetValueWithMiddleGauge(self, value, lingerDurationSeconds, animationSpeedSeconds = 0.75, callback = None):
        uicore.animations.MorphScalar(self.middleGauge, 'end', self.gauge.end, value, duration=animationSpeedSeconds, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet())
        uicore.animations.MorphScalar(self.gauge, 'end', self.gauge.end, value, duration=animationSpeedSeconds, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet(), timeOffset=lingerDurationSeconds, callback=callback)
        self.value = value

    def _GetCorrectCurveSet(self):
        simTimeCurveSet = uicore.animations.CreateCurveSet(useRealTime=self.useRealTime)
        simTimeCurveSet.name = 'gaugeCircularCurveSet'
        return simTimeCurveSet

    def SetMarkerValueTimed(self, value, duration):
        newRotation = self.GetOffsetMarkerValue(value)
        uicore.animations.MorphScalar(self.markerTransform, 'rotation', self.markerTransform.rotation, newRotation, duration=duration, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet())

    def StopGaugeAnimations(self):
        self.gauge.StopAnimations()
        self.markerTransform.StopAnimations()

    def GetOffsetMarkerValue(self, value):
        offSet = math.pi * 2 * (1.0 - value)
        newRotation = math.pi * 1.5 - self.startAngle + offSet
        return newRotation

    def SetColor(self, colorStart, colorEnd = None):
        self.colorStart = colorStart
        self.colorEnd = colorEnd
        self.gauge.SetColor(colorStart, colorEnd)

    def SetColorMarker(self, colorMarker):
        self.marker.SetRGBA(*colorMarker)

    def SetColorBg(self, colorBg):
        self.colorBg = colorBg
        self._ConstructBGGauge()

    def GetMousePositionAngle(self):
        x, y = self.GetAbsolutePosition()
        x = uicore.uilib.x - x - self.radius
        y = uicore.uilib.y - y - self.radius
        v1 = (x, y)
        if geo2.Vec2Length(v1) < 5:
            return self._angle
        v2 = (0.0, 1.0)
        dot = geo2.Vec2Dot(v1, v2)
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        angle = atan2(dot, cross)
        angle -= self.startAngle
        if angle < 0:
            angle += 2 * pi
        self._angle = angle
        return angle

    def TriggerCallback(self):
        if not self.callback:
            return
        angle = self.GetMousePositionAngle()
        value = angle / (2.0 * pi)
        self.callback(value)

    def OnMouseDown(self, *args):
        if not uicore.uilib.leftbtn:
            return
        self.TriggerCallback()

    def OnMouseEnter(self, *args):
        if not self.callback:
            return
        for obj in (self.gauge, self.bgGauge, self.marker):
            uicore.animations.FadeTo(obj, obj.opacity, 1.5, duration=0.3)

        if self.isHoverMarkerEnabled:
            uicore.animations.FadeIn(self.hoverMarker, 1.0, duration=0.3)

    def OnMouseExit(self, *args):
        if not self.callback:
            return
        for obj in (self.gauge, self.bgGauge, self.marker):
            uicore.animations.FadeTo(obj, obj.opacity, 1.0, duration=0.6)

        if self.isHoverMarkerEnabled:
            uicore.animations.FadeOut(self.hoverMarker, duration=0.3)
            currAngle = self.hoverMarkerAngle
            endAngle = 2 * pi if currAngle > pi else 0.0
            uicore.animations.MorphScalar(self, 'hoverMarkerAngle', currAngle, endAngle, duration=0.3)

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.TriggerCallback()
        if not self.isHoverMarkerEnabled:
            return
        self.hoverMarkerAngle = self.GetMousePositionAngle()

    def GetHoverMarkerAngle(self):
        if not self.isHoverMarkerEnabled:
            return 0.0
        return self.GetMousePositionAngle()

    def SetHoverMarkerAngle(self, angle):
        angle += self.startAngle
        w = self.hoverMarker.height / 2.0
        r = self.radius + self.lineWidth
        x = (r + w) * cos(angle)
        y = (r + w) * sin(angle)
        offset = r - w - self.lineWidth / 2.0
        self.hoverMarker.left = x + offset
        self.hoverMarker.top = y + offset

    hoverMarkerAngle = property(GetHoverMarkerAngle, SetHoverMarkerAngle)

    def EnableHoverMarker(self):
        self.isHoverMarkerEnabled = True

    def DisableHoverMarker(self):
        self.isHoverMarkerEnabled = False

    def SetRadius(self, radius):
        self.radius = radius
        self.width = self.height = radius * 2
        self.Reconstruct()
