#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\vectorarc.py
import math
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import TexturedBase

class VectorArc(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dArc
    default_name = 'vectorarc'
    default_align = uiconst.TOPLEFT
    default_lineWidth = 2
    default_lineColor = (1, 1, 1, 1)
    default_radius = 10
    default_fill = True
    default_startAngle = 0
    default_endAngle = math.pi * 2
    default_spriteEffect = trinity.TR2_SFX_FILL_AA

    def ApplyAttributes(self, attributes):
        TexturedBase.ApplyAttributes(self, attributes)
        self.lineWidth = attributes.get('lineWidth', self.default_lineWidth)
        self.lineColor = attributes.get('lineColor', self.default_lineColor)
        self.radius = attributes.get('radius', self.default_radius)
        self.fill = attributes.get('fill', self.default_fill)
        self.startAngle = attributes.get('startAngle', self.default_startAngle)
        self.endAngle = attributes.get('endAngle', self.default_endAngle)

    @property
    def lineWidth(self):
        return self.renderObject.lineWidth

    @lineWidth.setter
    def lineWidth(self, value):
        self.renderObject.lineWidth = value

    @property
    def lineColor(self):
        return self.renderObject.lineColor

    @lineColor.setter
    def lineColor(self, value):
        self.renderObject.lineColor = value

    @property
    def radius(self):
        return self.renderObject.radius

    @radius.setter
    def radius(self, value):
        self.renderObject.radius = value

    @property
    def startAngle(self):
        return self.renderObject.startAngle

    @startAngle.setter
    def startAngle(self, value):
        self.renderObject.startAngle = value

    @property
    def endAngle(self):
        return self.renderObject.endAngle

    @endAngle.setter
    def endAngle(self, value):
        self.renderObject.endAngle = value

    @property
    def fill(self):
        return self.renderObject.fill

    @fill.setter
    def fill(self, value):
        self.renderObject.fill = value
