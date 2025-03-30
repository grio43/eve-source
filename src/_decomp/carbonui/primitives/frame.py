#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\frame.py
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import TexturedBase
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor

class Frame(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dFrame
    default_name = 'framesprite'
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_color = eveColor.WHITE
    default_align = uiconst.TOALL
    default_frameConst = uiconst.FRAME_BORDER1_CORNER0
    default_state = uiconst.UI_DISABLED
    default_offset = 0
    default_cornerSize = 6
    default_fillCenter = True
    default_filter = False
    default_uiScaleVertices = False
    _offset = 0
    _cornerSize = 0

    def ApplyAttributes(self, attributes):
        self.offset = self.default_offset
        self.cornerSize = self.default_cornerSize
        self.fillCenter = attributes.get('fillCenter', self.default_fillCenter)
        self.uiScaleVertices = attributes.get('uiScaleVertices', self.default_uiScaleVertices)
        TexturedBase.ApplyAttributes(self, attributes)
        texturePath = attributes.get('texturePath', self.default_texturePath)
        if texturePath:
            self.cornerSize = attributes.get('cornerSize', self.default_cornerSize)
            self.offset = attributes.get('offset', self.default_offset)
        else:
            self.LoadFrame(attributes.get('frameConst', self.default_frameConst))
        if self.uiScaleVertices:
            self.renderObject.cornerScale = uicore.desktop.dpiScaling

    @property
    def cornerSize(self):
        return self._cornerSize

    @cornerSize.setter
    def cornerSize(self, value):
        self._cornerSize = value
        ro = self.renderObject
        if ro:
            ro.cornerSize = value

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
        self.FlagAlignmentDirty()

    def LoadFrame(self, frameConst = None):
        frameConst = frameConst or uiconst.FRAME_BORDER1_CORNER0
        if len(frameConst) == 4:
            iconNo, cornerSize, offset, fillCenter = frameConst
            self.fillCenter = fillCenter
        else:
            iconNo, cornerSize, offset = frameConst
            self.fillCenter = True
        if 'ui_' in iconNo:
            resPath = iconNo.replace('ui_', 'res:/ui/texture/icons/') + '.png'
        else:
            resPath = iconNo
        self.SetTexturePath(resPath)
        self.cornerSize = cornerSize
        self.offset = offset

    def SetOffset(self, offset):
        self.offset = offset

    def GetOffset(self):
        return self.offset

    def SetCornerSize(self, cornerSize = 0):
        self.cornerSize = cornerSize

    def GetCornerSize(self):
        return self.cornerSize

    def UpdateUIScaling(self, value, oldValue):
        if self.uiScaleVertices:
            self.renderObject.cornerScale = value
