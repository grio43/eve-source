#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\statusIcon.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
import carbonui.const as uiconst
from eve.client.script.ui.eveColor import WARNING_ORANGE
BG_BLUE_COLOR = Color.HextoRGBA('#34566f')[:3] + (0.6,)
FRAME_BLUE_COLOR = Color.HextoRGBA('#3e7aa4')[:3] + (0.5,)

class StatusIcon(Container):
    default_align = uiconst.CENTER
    default_width = 32
    default_height = 32
    default_textureSize = 32
    default_name = 'StatusIcon'
    STATUS_OK = 1
    STATUS_CAUTION = 2
    STATUS_WARNING = 3

    def ApplyAttributes(self, attributes):
        super(StatusIcon, self).ApplyAttributes(attributes)
        texturePath = attributes.texturePath
        status = attributes.status
        textureSize = attributes.get('default_textureSize', self.default_textureSize)
        if status == self.STATUS_WARNING:
            red = (0.8, 0, 0)
            frameColor = red + (0.2,)
            fillColor = red + (0.2,)
        elif status == self.STATUS_CAUTION:
            frameColor = WARNING_ORANGE[:3] + (0.2,)
            fillColor = WARNING_ORANGE[:3] + (0.2,)
        else:
            frameColor = FRAME_BLUE_COLOR
            fillColor = BG_BLUE_COLOR
        Fill(bgParent=self, color=fillColor)
        Frame(bgParent=self, color=frameColor)
        sprite = Sprite(parent=self, align=uiconst.CENTER, pos=(0,
         0,
         textureSize,
         textureSize), texturePath=texturePath, state=uiconst.UI_DISABLED)
