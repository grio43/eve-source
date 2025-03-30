#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\vectorlinetrace.py
import math
from math import cos, sin
import trinity
import geo2
from carbonui import uiconst
from carbonui.primitives.sprite import TexturedBase
from carbonui.uicore import uicore
from carbonui.util import colorblind
CORNERTYPE_MITER = 0
CORNERTYPE_ROUND = 1
CORNERTYPE_NONE = 2

class VectorLineTrace(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dLineTrace
    default_align = uiconst.TOPLEFT
    default_lineWidth = 1.0
    default_spriteEffect = trinity.TR2_SFX_FILL_AA
    default_textureWidth = 1.0
    default_cornerType = CORNERTYPE_MITER
    default_start = 0.0
    default_end = 1.0
    default_isLoop = False

    def ApplyAttributes(self, attributes):
        TexturedBase.ApplyAttributes(self, attributes)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.textureWidth = attributes.get('textureWidth', self.default_textureWidth)
        self.cornerType = attributes.get('cornerType', self.default_cornerType)
        self.start = attributes.get('start', self.default_start)
        self.end = attributes.get('end', self.default_end)
        self.isLoop = attributes.get('isLoop', self.default_isLoop)
        points = attributes.points
        if points:
            for point in points:
                self.AddPoint(*point)

    def Close(self):
        self.Flush()
        super(VectorLineTrace, self).Close()

    @property
    def lineWidth(self):
        return self._lineWidth

    @lineWidth.setter
    def lineWidth(self, value):
        self._lineWidth = value
        if self.renderObject:
            self.renderObject.lineWidth = uicore.ScaleDpiF(value)

    @property
    def isLoop(self):
        return self.renderObject.isLoop

    @isLoop.setter
    def isLoop(self, value):
        self.renderObject.isLoop = value

    @property
    def cornerType(self):
        return self.renderObject.cornerType

    @cornerType.setter
    def cornerType(self, value):
        self.renderObject.cornerType = value

    @property
    def start(self):
        if self.renderObject:
            return self.renderObject.start
        else:
            return 0.0

    @start.setter
    def start(self, value):
        if self.renderObject:
            self.renderObject.start = value

    @property
    def end(self):
        if self.renderObject:
            return self.renderObject.end
        else:
            return 1.0

    @end.setter
    def end(self, value):
        if self.renderObject:
            self.renderObject.end = value

    @property
    def textureWidth(self):
        if not self.renderObject:
            return
        return self.renderObject.textureWidth

    @textureWidth.setter
    def textureWidth(self, value):
        if not self.renderObject:
            return
        self.renderObject.textureWidth = value

    @property
    def textureOffset(self):
        if not self.renderObject:
            return
        return self.renderObject.textureOffset

    @textureOffset.setter
    def textureOffset(self, value):
        if not self.renderObject:
            return
        self.renderObject.textureOffset = value

    def AddPoint(self, pos, color = (1.0, 1.0, 1.0, 1.0), name = '', idx = -1):
        color = colorblind.CheckReplaceColor(color)
        v = trinity.Tr2Sprite2dLineTraceVertex()
        x, y = pos
        x = uicore.ScaleDpiF(x)
        y = uicore.ScaleDpiF(y)
        v.position = (x, y)
        v.color = color
        v.name = name
        if self.renderObject:
            self.renderObject.vertices.insert(idx, v)

    def AddPoints(self, posList, color = (1.0, 1.0, 1.0, 1.0)):
        for pos in posList:
            self.AddPoint(pos, color)

    def UpdatePoint(self, index, x, y):
        positions = []
        transform = None
        colors = []
        for order, vertex in enumerate(self.renderObject.vertices):
            if index == order:
                positions.append((uicore.ScaleDpiF(x), uicore.ScaleDpiF(y)))
            else:
                positions.append(vertex.position)
            colors.append(vertex.color)

        self.Flush()
        self.renderObject.AppendVertices(positions, transform, colors)

    def RemovePoint(self, index):
        positions = []
        transform = None
        colors = []
        for order, vertex in enumerate(self.renderObject.vertices):
            if index != order:
                positions.append(vertex.position)
                colors.append(vertex.color)

        self.Flush()
        self.renderObject.AppendVertices(positions, transform, colors)

    def SetTexturePath(self, texturePath):
        TexturedBase.SetTexturePath(self, texturePath)
        if self.texturePath:
            self.renderObject.texturePrimary.atlasTexture.isStandAlone = True

    texturePath = property(TexturedBase.GetTexturePath, SetTexturePath)

    def Flush(self):
        if self.renderObject:
            del self.renderObject.vertices[:]

    def _ApplyColorblindCorrection(self, colors):
        if colors:
            if isinstance(colors[0], (float, int)):
                colors = colorblind.CheckReplaceColor(colors)
            else:
                colors = [ colorblind.CheckReplaceColor(color) for color in colors ]
        return colors

    def AppendVertices(self, positions, transform, colors):
        colors = self._ApplyColorblindCorrection(colors)
        self.renderObject.AppendVertices(positions, transform, colors)

    def UpdateUIScaling(self, value, oldValue):
        positions = []
        colors = []
        multiplier = value / oldValue
        for vertex in self.renderObject.vertices:
            x, y = vertex.position
            positions.append((multiplier * x, multiplier * y))
            colors.append(vertex.color)

        self.Flush()
        self.renderObject.AppendVertices(positions, None, colors)
        self.lineWidth = self._lineWidth


class DashedCircle(VectorLineTrace):
    demoCount = 0
    default_smoothScale = 4

    def ApplyAttributes(self, attributes):
        VectorLineTrace.ApplyAttributes(self, attributes)
        self.dashCount = attributes.dashCount or 5
        self._dashSizeFactor = attributes.dashSizeFactor or 2.0
        self.startAngle = attributes.startAngle or math.radians(180.0)
        self.range = attributes.range or math.radians(180.0)
        self._radius = attributes.radius or 60
        self.lineWidth = attributes.lineWidth or 7
        self.startColor = attributes.startColor or (1, 1, 1, 1)
        self.endColor = attributes.endColor or (1, 1, 1, 1)
        self.gapEnds = attributes.gapEnds or True
        self.smoothScale = attributes.smoothScale or self.default_smoothScale
        self.PlotLineTrace()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, newRadius):
        self._radius = newRadius
        self.Flush()
        self.PlotLineTrace()

    @property
    def dashSizeFactor(self):
        return self._dashSizeFactor

    @dashSizeFactor.setter
    def dashSizeFactor(self, newDashSize):
        self._dashSizeFactor = newDashSize
        self.Flush()
        self.PlotLineTrace()

    def SetValue(self, value):
        self.end = value

    def SetValueTimed(self, value, duration):
        uicore.animations.MorphScalar(self, 'end', self.end, value, duration=duration, curveType=uiconst.ANIM_LINEAR)

    def ValueDown(self):
        self.demoCount += 1
        if self.demoCount < 2:
            uicore.animations.MorphScalar(self, 'end', 1.0, 0.0, duration=2.0, callback=self.ValueUp)

    def ValueUp(self):
        uicore.animations.MorphScalar(self, 'end', 0.0, 1.0, duration=2.0, callback=self.ValueDown)

    def PlotLineTrace(self):
        circum = self.radius * self.range
        if self.gapEnds:
            gapStepRad = self.range / (self.dashCount * (self.dashSizeFactor + 1))
        else:
            gapStepRad = self.range / (self.dashCount * (self.dashSizeFactor + 1) - 1)
        dashStepRad = gapStepRad * self.dashSizeFactor
        pixelRad = self.range / circum
        centerOffset = self.radius + self.lineWidth * 0.5
        jointOffset = min(gapStepRad / 3, pixelRad / 2)
        rot = self.startAngle
        if self.gapEnds:
            rot += gapStepRad / 2
        for i in xrange(self.dashCount):
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            dashColor = geo2.Vec4Lerp(self.startColor, self.endColor, (rot - jointOffset - self.startAngle) / self.range)
            r, g, b, a = dashColor
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            dashColor = geo2.Vec4Lerp(self.startColor, self.endColor, (rot + jointOffset - self.startAngle) / self.range)
            self.AddPoint(point, dashColor)
            smoothRad = pixelRad * self.smoothScale + jointOffset
            while smoothRad < dashStepRad - jointOffset:
                point = (centerOffset + self.radius * cos(rot + smoothRad), centerOffset + self.radius * sin(rot + smoothRad))
                dashColor = geo2.Vec4Lerp(self.startColor, self.endColor, (rot + smoothRad - self.startAngle) / self.range)
                self.AddPoint(point, dashColor)
                smoothRad += pixelRad * self.smoothScale

            rot += dashStepRad
            point = (centerOffset + self.radius * cos(rot - jointOffset), centerOffset + self.radius * sin(rot - jointOffset))
            dashColor = geo2.Vec4Lerp(self.startColor, self.endColor, (rot - jointOffset - self.startAngle) / self.range)
            self.AddPoint(point, dashColor)
            point = (centerOffset + self.radius * cos(rot + jointOffset), centerOffset + self.radius * sin(rot + jointOffset))
            dashColor = geo2.Vec4Lerp(self.startColor, self.endColor, (rot + jointOffset - self.startAngle) / self.range)
            r, g, b, a = dashColor
            self.AddPoint(point, (r,
             g,
             b,
             0.0))
            rot += gapStepRad

        self.width = self.height = centerOffset * 2
