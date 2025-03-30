#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\vectorline.py
import trinity
from carbonui import uiconst
from carbonui.primitives.sprite import TexturedBase
from carbonui.uicore import uicore
from carbonui.util.color import Color

class VectorLine(TexturedBase):
    __renderObject__ = trinity.Tr2Sprite2dLine
    default_name = 'vectorline'
    default_align = uiconst.TOPLEFT
    default_spriteEffect = trinity.TR2_SFX_FILL_AA
    default_translationFrom = (0.0, 0.0)
    default_translationTo = (100.0, 100.0)
    default_widthFrom = 1.0
    default_widthTo = 1.0
    default_colorFrom = Color.WHITE
    default_colorTo = Color.WHITE
    default_textureWidth = 1.0
    _colorFrom = None
    _colorTo = None
    _translationFrom = None
    _translationTo = None
    _widthFrom = None
    _widthTo = None

    def ApplyAttributes(self, attributes):
        TexturedBase.ApplyAttributes(self, attributes)
        self.translationFrom = attributes.get('translationFrom', self.default_translationFrom)
        self.widthFrom = attributes.get('widthFrom', self.default_widthFrom)
        self.translationTo = attributes.get('translationTo', self.default_translationTo)
        self.widthTo = attributes.get('widthTo', self.default_widthTo)
        self.colorFrom = attributes.get('colorFrom', self.default_colorFrom)
        self.colorTo = attributes.get('colorTo', self.default_colorTo)
        self.textureWidth = attributes.get('textureWidth', self.default_textureWidth)
        if attributes.texturePath is not None:
            self.renderObject.texturePrimary.atlasTexture.isStandAlone = True

    @property
    def translationFrom(self):
        return self._translationFrom

    @translationFrom.setter
    def translationFrom(self, value):
        self._translationFrom = value
        if self.renderObject:
            x = uicore.ScaleDpiF(value[0])
            y = uicore.ScaleDpiF(value[1])
            self.renderObject.translationFrom = (x, y)

    @property
    def translationTo(self):
        return self._translationTo

    @translationTo.setter
    def translationTo(self, value):
        self._translationTo = value
        if self.renderObject:
            x = uicore.ScaleDpiF(value[0])
            y = uicore.ScaleDpiF(value[1])
            self.renderObject.translationTo = (x, y)

    @property
    def widthFrom(self):
        return self._widthFrom

    @widthFrom.setter
    def widthFrom(self, value):
        self._widthFrom = float(value)
        if self.renderObject:
            self.renderObject.widthFrom = uicore.ScaleDpiF(value)

    @property
    def widthTo(self):
        return self._widthTo

    @widthTo.setter
    def widthTo(self, value):
        self._widthTo = float(value)
        if self.renderObject:
            self.renderObject.widthTo = uicore.ScaleDpiF(value)

    @property
    def colorFrom(self):
        return self._colorFrom

    @colorFrom.setter
    def colorFrom(self, value):
        self._colorFrom = value
        if self.renderObject:
            self.renderObject.colorFrom = value

    @property
    def colorTo(self):
        return self._colorTo

    @colorTo.setter
    def colorTo(self, value):
        self._colorTo = value
        if self.renderObject:
            self.renderObject.colorTo = value

    @property
    def textureWidth(self):
        return self.renderObject.textureWidth

    @textureWidth.setter
    def textureWidth(self, value):
        self.renderObject.textureWidth = value

    @property
    def textureOffset(self):
        return self.renderObject.textureOffset

    @textureOffset.setter
    def textureOffset(self, value):
        self.renderObject.textureOffset = value

    def UpdateUIScaling(self, value, oldValue):
        super(VectorLine, self).UpdateUIScaling(value, oldValue)
        self.translationFrom = self._translationFrom
        self.translationTo = self._translationTo
        self.widthFrom = self._widthFrom
        self.widthTo = self._widthTo
