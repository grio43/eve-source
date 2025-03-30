#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\stretchspritevertical.py
import trinity
from carbonui import uiconst
from carbonui.uicore import uicore
from carbonui.primitives.sprite import TexturedBase

class StretchSpriteVertical(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dStretchVertical
    default_name = 'stretchspritevertical'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_color = (1.0, 1.0, 1.0, 1.0)
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_DISABLED
    default_topEdgeSize = 6
    default_bottomEdgeSize = 6
    default_fillCenter = True
    default_offset = 0
    _topEdgeSize = 0
    _bottomEdgeSize = 0
    _offset = 0
    _fillCenter = 0

    def ApplyAttributes(self, attributes):
        self.topEdgeSize = attributes.get('topEdgeSize', self.default_topEdgeSize)
        self.bottomEdgeSize = attributes.get('bottomEdgeSize', self.default_bottomEdgeSize)
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
    def topEdgeSize(self):
        return self._topEdgeSize

    @topEdgeSize.setter
    def topEdgeSize(self, value):
        self._topEdgeSize = value
        ro = self.renderObject
        if ro:
            ro.topEdgeSize = value

    @property
    def bottomEdgeSize(self):
        return self._bottomEdgeSize

    @bottomEdgeSize.setter
    def bottomEdgeSize(self, value):
        self._bottomEdgeSize = value
        ro = self.renderObject
        if ro:
            ro.bottomEdgeSize = value

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
        super(StretchSpriteVertical, self).UpdateUIScaling(value, oldValue)
        self.renderObject.edgeScale = uicore.dpiScaling
