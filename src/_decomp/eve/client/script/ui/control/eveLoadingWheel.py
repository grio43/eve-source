#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveLoadingWheel.py
from carbonui import uiconst
from carbonui.primitives.sprite import StreamingVideoSprite
from carbonui.uiconst import SpriteEffect, BlendMode

class LoadingWheel(StreamingVideoSprite):
    default_name = 'loadingWheel'
    default_width = 64
    default_height = 64
    default_colorType = uiconst.COLORTYPE_UIHILIGHT
    default_state = uiconst.UI_DISABLED
    default_spriteEffect = SpriteEffect.COPY
    default_blendMode = BlendMode.ADD

    def ApplyAttributes(self, attributes):
        super(LoadingWheel, self).ApplyAttributes(attributes)
        if self.width <= 16:
            path = 'res:/Video/loading/loading_16.webm'
        elif self.width <= 32:
            path = 'res:/Video/loading/loading_32.webm'
        else:
            path = 'res:/Video/loading/loading_64.webm'
        self.SetVideoPath(path, videoLoop=True)
