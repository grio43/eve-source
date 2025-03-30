#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\stretchspritehorizontal.py
import trinity
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.sprite import TexturedBase

class StretchSpriteHorizontal(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dStretch
    default_name = 'stretchspritehorizontal'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_DISABLED
    default_leftEdgeSize = 6
    default_rightEdgeSize = 6
    default_fillCenter = True
    default_offset = 0
    _leftEdgeSize = 0
    _rightEdgeSize = 0
    _offset = 0

    def ApplyAttributes(self, attributes):
        self.offset = attributes.get('offset', self.default_offset)
        self.leftEdgeSize = attributes.get('leftEdgeSize', self.default_leftEdgeSize)
        self.rightEdgeSize = attributes.get('rightEdgeSize', self.default_rightEdgeSize)
        self.fillCenter = attributes.get('fillCenter', self.default_fillCenter)
        TexturedBase.ApplyAttributes(self, attributes)
        self.renderObject.edgeScale = uicore.dpiScaling

    def SetAlign(self, align):
        TexturedBase.SetAlign(self, align)
        ro = self.renderObject
        if not ro:
            return

    align = property(TexturedBase.GetAlign, SetAlign)

    @property
    def leftEdgeSize(self):
        return self._leftEdgeSize

    @leftEdgeSize.setter
    def leftEdgeSize(self, value):
        self._leftEdgeSize = value
        ro = self.renderObject
        if ro:
            ro.leftEdgeSize = value

    @property
    def rightEdgeSize(self):
        return self._rightEdgeSize

    @rightEdgeSize.setter
    def rightEdgeSize(self, value):
        self._rightEdgeSize = value
        ro = self.renderObject
        if ro:
            ro.rightEdgeSize = value

    @property
    def fillCenter(self):
        return self._fillCenter

    @fillCenter.setter
    def fillCenter(self, value):
        self._fillCenter = value
        ro = self.renderObject
        if ro:
            ro.fillCenter = value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        ro = self.renderObject
        if ro:
            ro.offset = value

    def UpdateUIScaling(self, value, oldValue):
        super(StretchSpriteHorizontal, self).UpdateUIScaling(value, oldValue)
        self.renderObject.edgeScale = uicore.dpiScaling
