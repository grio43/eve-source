#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\bracket.py
import trinity
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.dpi import reverse_scale_dpi, scale_dpi

class Bracket(Container):
    __guid__ = 'uiprimitives.Bracket'
    default_name = 'bracket'
    default_align = uiconst.NOALIGN
    default_integerCoordinates = True
    default_dock = False
    projectBracket = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.renderObject.displayHeight = scale_dpi(attributes.Get('width', self.default_width))
        self.renderObject.displayWidth = scale_dpi(attributes.Get('height', self.default_height))
        self.projectBracket = trinity.EveProjectBracket()
        self.projectBracket.bracket = self.renderObject
        self.integerCoordinates = attributes.Get('integerCoordinates', self.default_integerCoordinates)
        curveSet = attributes.get('curveSet', uicore.uilib.bracketCurveSet)
        curveSet.curves.append(self.projectBracket)
        self.dock = attributes.Get('dock', self.default_dock)

    def Close(self):
        super(Bracket, self).Close()
        uicore.uilib.bracketCurveSet.curves.fremove(self.projectBracket)
        self.projectBracket = None

    @property
    def name(self):
        return Container.name.fget(self)

    @name.setter
    def name(self, value):
        Container.name.fset(self, value)
        if self.projectBracket:
            self.projectBracket.name = unicode(value)

    @property
    def trackTransform(self):
        if self.projectBracket:
            return self.projectBracket.trackTransform

    @trackTransform.setter
    def trackTransform(self, value):
        self.projectBracket.trackTransform = value

    @property
    def trackBall(self):
        if self.projectBracket:
            return self.projectBracket.trackBall

    @trackBall.setter
    def trackBall(self, value):
        self.projectBracket.trackBall = value

    @property
    def ballTrackingScaling(self):
        return self.projectBracket.ballTrackingScaling

    @ballTrackingScaling.setter
    def ballTrackingScaling(self, value):
        self.projectBracket.ballTrackingScaling = value

    @property
    def dock(self):
        return self.projectBracket.dock

    @dock.setter
    def dock(self, value):
        if not self.destroyed:
            self.projectBracket.dock = value

    @property
    def left(self):
        return reverse_scale_dpi(self.renderObject.displayX)

    @left.setter
    def left(self, value):
        if value != self._left:
            self._left = value
            self.renderObject.displayX = value

    @property
    def top(self):
        return reverse_scale_dpi(self.renderObject.displayY)

    @top.setter
    def top(self, value):
        if value != self._top:
            self._top = value
            self.renderObject.displayY = value

    @property
    def minDispRange(self):
        return self.projectBracket.minDispRange

    @minDispRange.setter
    def minDispRange(self, value):
        if self.destroyed:
            return
        self.projectBracket.minDispRange = value

    @property
    def maxDispRange(self):
        return self.projectBracket.maxDispRange

    @maxDispRange.setter
    def maxDispRange(self, value):
        self.projectBracket.maxDispRange = value

    @property
    def integerCoordinates(self):
        return self.projectBracket.integerCoordinates

    @integerCoordinates.setter
    def integerCoordinates(self, value):
        self.projectBracket.integerCoordinates = value
