#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\primitives\blurredbackgroundsprite.py
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from trinity import device, TR2_SFX_BLURBACKGROUND
from carbonui.uicore import uicore

class BlurredBackgroundSprite(Sprite):
    __notifyevents__ = ['OnBlurredBufferCreated']
    default_name = 'BlurredBackgroundSprite'
    default_state = uiconst.UI_DISABLED
    default_spriteEffect = TR2_SFX_BLURBACKGROUND

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        if uicore.uilib.blurredBackBufferAtlas:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
        device.RegisterResource(self)

    def OnCreate(self, *args):
        pass

    def OnBlurredBufferCreated(self, *args):
        if not self.destroyed:
            self.texture.atlasTexture = uicore.uilib.blurredBackBufferAtlas
